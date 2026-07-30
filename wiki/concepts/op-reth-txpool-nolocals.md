---
type: Concept
title: op-reth --txpool.nolocals & Local Transaction Exemption
description: op-reth(reth)의 --txpool.nolocals가 local 트랜잭션에게 주던 slot/price/eviction 3종 면제(exemption)를 꺼서 모든 tx를 remote와 동일하게 취급하게 만드는 메커니즘과, is_local() 로직에서 nolocals가 --txpool.locals보다 우선하는 상호작용
resource: https://github.com/paradigmxyz/reth/blob/main/crates/transaction-pool/src/config.rs
tags: [op-stack, reth, txpool, l2]
timestamp: 2026-07-28T00:00:00Z
source_commit: aaeb6c0154
chain: l2
version: bedrock
---

# op-reth --txpool.nolocals & Local Transaction Exemption

## 개요

`--txpool.nolocals`는 op-reth(및 상위 reth) 노드에서 "내 노드에 직접 들어온 트랜잭션(local tx)"에게 주던 **특혜(면제, exemption)를 전부 끄고, 모든 트랜잭션을 외부(remote) 트랜잭션과 동일하게 취급**하게 만드는 boolean 플래그다. 기본값은 꺼짐(`false`) — 기본 상태에서는 local tx가 특혜를 받는다.

비유하면 트랜잭션 풀을 공항 보안검색대라고 할 때, 원래 local tx는 "직원 전용 패스트트랙"을 탄다(줄 안 서고, 요금 기준 완화, 자리 없어도 안 쫓겨남). `--txpool.nolocals`를 켜면 이 패스트트랙을 폐지하고 직원도 일반 승객 줄에 세운다.

핵심 사실:

1. **op-reth 전용 동작이 아니다.** reth 코드베이스를 그대로 상속한 표준 txpool 플래그이며, OP 전용으로 의미가 바뀌지 않는다.
2. **`nolocals`가 `locals`보다 우선한다.** `is_local()`은 `no_exemptions == true`이면 origin이나 주소와 무관하게 무조건 `false`를 반환한다. 따라서 `--txpool.nolocals`를 켜면 `--txpool.locals`로 지정한 주소도 무력화된다 (`crates/transaction-pool/src/config.rs` `LocalTransactionConfig::is_local`).
3. **exemption(풀 내부 우대)만 끈다.** tx의 P2P 전파(propagation)는 별개 플래그(`--txpool.no-local-transactions-propagation`)로 제어되므로, nolocals를 켜도 브로드캐스트 자체가 막히는 것은 아니다.

## 핵심 동작/책임

### CLI 플래그 → 풀 설정 매핑

`TxPoolArgs`의 세 필드가 `pool_config()`에서 `LocalTransactionConfig`로 변환된다 (`crates/node/core/src/args/txpool.rs`).

```rust
local_transactions_config: LocalTransactionConfig {
    no_exemptions: self.no_locals,                           // ← --txpool.nolocals
    local_addresses: self.locals.iter().copied().collect(), // ← --txpool.locals
    propagate_local_transactions: !self.no_local_transactions_propagation,
}
```

### is_local() 판정 로직 (정본)

```rust
pub fn is_local(&self, origin: TransactionOrigin, sender: &Address) -> bool {
    if self.no_local_exemptions() {   // no_exemptions == true 이면
        return false                  // origin/주소 무관하게 non-local 취급
    }
    origin.is_local() || self.contains_local_address(sender)
}
```

`no_exemptions`가 `false`(기본)일 때만 다음 두 경로로 local 판정을 한다:

- **origin 기반** — `TransactionOrigin::Local`로 삽입된 tx. ⚠️ **`eth_sendRawTransaction`은 여기 해당하지 않는다** (아래 주의 참조).
- **주소 기반** — `--txpool.locals`로 등록한 주소가 sender이면 local.

> ⚠️ **정정 (2026-07-28):** 이전 서술은 "RPC(`eth_sendRawTransaction` 등)로 내 노드에 직접 들어온 tx는 origin이 local"이었으나, 코드 확인 결과 **틀렸다.** reth v2.3.0의 `send_raw_transaction`은 `TransactionOrigin::**External**`을 쓴다 (`crates/rpc/rpc-eth-api/src/helpers/transaction.rs:79-87`). `TransactionOrigin::Local`은 노드가 직접 서명하는 `eth_sendTransaction` 경로에만 쓰인다(같은 파일 502행).
>
> 실무 함의: **"내 노드 RPC로 직접 넣었으니 local 특혜를 받겠지"는 성립하지 않는다.** origin 기반 면제는 사실상 노드 자체 서명 tx 전용이며, RPC로 들어오는 tx에 면제를 주려면 반드시 `--txpool.locals <address>`로 **주소를 명시**해야 한다. geth와 다른 지점이라 오해하기 쉽다.

### local 트랜잭션이 받는 면제(exemption) 3종

`--txpool.nolocals`를 켜면 아래 3가지가 모두 사라지고, local tx도 remote와 동일한 규칙을 적용받는다 (`LocalTransactionConfig` doc comment).

| 항목 | 면제 내용 | 실제 적용 범위 |
|------|-----------|----------------|
| **Slot 면제** | 계정당 슬롯 제한(`max_account_slots`, 기본 16) 우회 | 전면 적용 — `ensure_valid`의 spam 체크를 통째로 건너뜀 (`pool/txpool.rs:1864-1881`) |
| **가격(price) 면제** | 풀의 최소 수수료/priority fee 기준보다 낮아도 수용 | — |
| **Eviction 면제** | 풀이 가득 차 tx를 쫓아낼 때 제거 대상에서 보호 | ⚠️ **서브풀별로 비대칭** (아래) |

#### Eviction 면제는 pending 서브풀에서만 적용된다

| 서브풀 | truncate 시 local 보호 | 근거 |
|--------|------------------------|------|
| pending | **있음** — non-local을 먼저 자르고, 그래도 한도를 못 맞추면 local도 자름 | `pool/pending.rs:375-500` (`remove_locals` 플래그) |
| basefee / queued (`ParkedPool`) | **없음** — `is_local` 참조가 전혀 없고 sender 제출 순서로만 축출 | `pool/parked.rs` `truncate_pool` |

즉 local 지정은 **완전한 축출 방패가 아니다.** base fee 미달이나 nonce gap으로 tx가 parked 서브풀에 머무는 동안에는 보호받지 못한다. 용량 한도 자체의 메커니즘은 [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한](reth-txpool-capacity-slot-limits.md) 참조.

## 주요 인터페이스/필드

관련 CLI 플래그 3종 (모두 `--txpool.*` 네임스페이스):

| 플래그 | 타입 | 의미 |
|--------|------|------|
| `--txpool.nolocals` | bool | local exemption 전체 비활성화 (`no_exemptions`), 기본 `false` |
| `--txpool.locals` | `Vec<Address>` | 특정 주소를 local로 지정 |
| `--txpool.no-local-transactions-propagation` | bool | local tx를 P2P 피어로 전파하지 않음 |

### OP Stack 맥락에서의 실효성

- 이 플래그가 실제로 의미 있는 노드는 **sequencer(블록 생성 주체)**다. sequencer 풀에서 특정 주소/RPC tx에 우대를 줄지 결정한다.
- 일반 op-reth **follower/replica 노드**는 대개 받은 raw tx를 자체 블록에 넣지 않고 sequencer로 forward하므로, 이 노드에서는 nolocals의 실효성이 제한적이다.
- **용도 예시:** 퍼블릭 RPC 엔드포인트 운영 시, RPC로 들어온 tx가 수수료·슬롯 제한을 우회하는 특혜를 받지 못하게 하여 DoS/스팸 저항성과 요금 정책 일관성을 확보하고 싶을 때 켠다.

> 운영 중 정확한 플래그명/기본값은 배포 릴리스에 따라 다를 수 있으니 `op-reth node --help | grep -i local`로 확인한다. 2026-07-28 보강분은 op-reth가 pin한 **reth v2.3.0** 태그 소스 기준으로 재검증했다 (`resource/optimism/rust/Cargo.toml:411`).

## 관련 페이지

- [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")](reth-txpool-capacity-slot-limits.md) — 이 페이지가 **끄는** 대상(slot 체크·eviction 보호)의 원본 메커니즘. `max_account_slots`의 정확한 의미와 서브풀 한도를 다룬다. 두 페이지는 같은 `LocalTransactionConfig`를 반대 방향에서 본다.
- [op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단](../runbooks/op-reth-sequencer-forward-txpool-full.md) — `--txpool.locals`로 면제를 주려다 `--txpool.nolocals` 때문에 무력화되는 실제 운영 사례.
- [OP Stack 트랜잭션 수수료 & EIP-1559 (maxFeePerGas / maxPriorityFeePerGas)](op-stack-eip1559-fees.md) — 여기의 price 면제(**강제** 최소 수수료/priority fee 하한)와 대비되는, `--min-suggested-priority-fee`의 RPC **추천** 하한 및 L2 실행비/ L1 data fee 전체 모델
- [OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황](observability-grafana-integration.md) — op-reth의 다른 CLI 플래그 계열(--tracing-otlp/--logs-otlp) 참고
- [op-reth "Changeset cache MISS" 로그 진단](../runbooks/op-reth-changeset-cache-miss.md) — 동일 op-reth 클라이언트 운영 진단

## 출처

- `paradigmxyz/reth` — [`crates/transaction-pool/src/config.rs`](https://github.com/paradigmxyz/reth/blob/main/crates/transaction-pool/src/config.rs) (`LocalTransactionConfig`, `is_local`, `no_local_exemptions`) — **코드 정본**
- `paradigmxyz/reth` — [`crates/node/core/src/args/txpool.rs`](https://github.com/paradigmxyz/reth/blob/main/crates/node/core/src/args/txpool.rs) (`TxPoolArgs` → `pool_config()`) — **코드 정본**
- [reth CLI 문서 — `reth node`](https://reth.rs/cli/reth/node/)

**2026-07-28 보강분 — reth v2.3.0 (op-reth pin 버전):**
- [`crates/rpc/rpc-eth-api/src/helpers/transaction.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/rpc/rpc-eth-api/src/helpers/transaction.rs) — `send_raw_transaction` → `TransactionOrigin::External`(79-87), `eth_sendTransaction` → `Local`(502) — **origin 서술 정정 근거**
- [`crates/transaction-pool/src/pool/txpool.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/pool/txpool.rs) — `ensure_valid` slot 면제(1864-1881), `allow_local_spamming` 테스트(3301-)
- [`crates/transaction-pool/src/pool/pending.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/pool/pending.rs) — local 보호 truncate(375-500)
- [`crates/transaction-pool/src/pool/parked.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/pool/parked.rs) — `truncate_pool` (local 보호 **없음**) — **eviction 면제 비대칭 근거**
- `resource/optimism/rust/Cargo.toml:411` — reth v2.3.0 pin
