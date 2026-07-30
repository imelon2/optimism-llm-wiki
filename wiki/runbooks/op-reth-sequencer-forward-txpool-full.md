---
type: Runbook
title: op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단
description: op-reth replica가 eth_sendRawTransaction을 시퀀서로 포워딩하다 -32003 "txpool is full"로 거절당할 때 남기는 WARN 로그의 발생 경로(로그 주체는 시퀀서가 아닌 replica), 재시도·로컬 보관 없이 즉시 실패하는 동작, 그리고 용량 초과 vs 계정 슬롯 초과를 구분하는 진단 절차
resource: resource/optimism/rust/op-reth/crates/rpc/src/sequencer.rs
tags: [op-stack, reth, txpool, sequencer, l2]
timestamp: 2026-07-28T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단

## 개요

```
HTTP request to sequencer failed err=server returned an error response: error code -32003: txpool is full
```

**이 로그를 남긴 노드는 시퀀서가 아니다.** 트랜잭션을 시퀀서로 대신 전달해주는 **op-reth RPC/replica 노드**이며, 문제는 전달받은 **시퀀서 쪽 mempool**에 있다.

비유하면 — 로그를 남긴 노드는 우편물을 받아 본사(시퀀서)로 넘기는 지점 창구다. 창구는 정상인데 본사 접수함이 꽉 차서 "방금 넣은 그 봉투"를 도로 빼서 돌려보낸 것이다. 창구는 재시도하지 않고 그대로 사용자에게 실패를 반환한다.

| 항목 | 값 |
|------|-----|
| 심각도 | 사용자 tx 제출 실패 (자가복구 아님 — 원인 제거 필요) |
| 로그 주체 | `--rollup.sequencer`가 설정된 op-reth 비-시퀀서 노드 |
| 실제 원인 위치 | **시퀀서** 노드의 txpool |
| 재시도 | **없음** — 즉시 사용자에게 -32003 반환 |
| 로컬 풀 보관 | **없음** — tx가 어디에도 남지 않음 |

## 핵심 동작/책임

### 1. 로그 발생 지점 (op-reth)

`resource/optimism/rust/op-reth/crates/rpc/src/sequencer.rs:138-154`:

```rust
    /// Sends a [`alloy_rpc_client::RpcCall`] request to the sequencer endpoint.
    pub async fn request<Params: RpcSend, Resp: RpcRecv>(
        &self, method: &str, params: Params,
    ) -> Result<Resp, SequencerClientError> {
        let resp =
            self.client().request::<Params, Resp>(method.to_string(), params).await.inspect_err(
                |err| {
                    warn!(
                        target: "rpc::sequencer",
                        %err,
                        "HTTP request to sequencer failed",   // ← 이 로그
                    );
                },
            )?;
        Ok(resp)
    }
```

이 `request()`의 호출자는 op-reth 전체에서 **딱 두 곳**뿐이다:

- `forward_raw_transaction` → `eth_sendRawTransaction` (`sequencer.rs:161`)
- `forward_raw_transaction_conditional` → `eth_sendRawTransactionConditional` (`sequencer.rs:181`)

→ **이 로그가 보이면 원인은 반드시 트랜잭션 포워딩이다.** 정상이라면 바로 뒤에 `target: rpc::eth`의 `"Failed to forward transaction to sequencer"` WARN이 짝으로 찍힌다.

`SequencerClient`는 `--rollup.sequencer` 플래그가 있을 때만 생성된다 (`crates/node/src/args.rs:88`, 별칭 `--rollup.sequencer-http` / `--rollup.sequencer-ws`; `crates/rpc/src/eth/mod.rs:571-579`).

### 2. 실패 시 replica의 동작 — 재시도 없음, 로컬 보관 없음

`crates/rpc/src/eth/transaction.rs:45-81`:

```rust
        // On optimism, transactions are forwarded directly to the sequencer to be included in
        // blocks that it builds.
        if let Some(client) = self.raw_tx_forwarder().as_ref() {
            tracing::debug!(target: "rpc::eth", hash = %pool_transaction.hash(), "forwarding raw transaction to sequencer");
            let hash = client.forward_raw_transaction(&tx).await.inspect_err(|err| {
                    tracing::debug!(target: "rpc::eth", %err, hash=% *pool_transaction.hash(), "failed to forward raw transaction");
                })?;              // ← 여기서 조기 반환

            // Retain tx in local tx pool after forwarding, for local RPC usage.
            let _ = self.inner.eth_api.add_pool_transaction(origin, pool_transaction).await...
```

`?`로 즉시 반환하므로 **로컬 풀 보관(`add_pool_transaction`)까지 도달하지 못한다.** 사용자는 -32003을 그대로 받고 트랜잭션은 어디에도 남지 않는다.

관측 주의: `record_forward_latency` 메트릭은 **성공 시에만** 기록되므로 실패는 latency 지표에 잡히지 않는다. 별도로 로그/에러율을 봐야 한다.

### 3. 시퀀서가 -32003을 반환하는 두 가지 이유

`-32003 "txpool is full"`은 **원인이 다른 두 상황이 하나의 메시지로 붕괴된 것**이다. 메커니즘 상세는 [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한](../concepts/reth-txpool-capacity-slot-limits.md) 참조.

| 원인 | 풀 에러 | 실제 조건 | 풀이 한가해도 발생? |
|------|---------|-----------|---------------------|
| **A. 용량 초과** | `DiscardedOnInsert` | 서브풀 4종 중 하나가 한도(기본 10,000 tx / 20MB) 초과 상태에서, 방금 넣은 tx가 축출 1순위였음 = 사실상 underpriced | ✗ |
| **B. 계정 슬롯 초과** | `SpammerExceededCapacity` | 한 발신자의 풀 내 tx ≥ `max_account_slots`(기본 16) **이면서** 새 tx의 nonce > 온체인 nonce | **✓ 발생함** |

**B가 실무에서 가장 흔한 오진 지점이다.** 시퀀서 풀이 텅 비어 있어도 하나의 hot wallet(브릿지 relayer, 배치 봇, faucet)이 nonce를 앞질러 17개 이상 밀어 넣으면 바로 이 에러가 나온다. RPC 메시지는 "txpool is full"이라 원인이 완전히 가려진다.

### 4. 거절한 쪽이 어떤 클라이언트인지 판별

op-geth도 문자열은 **완전히 동일**하다 (`core/txpool/legacypool/legacypool.go:62`). 구분자는 **에러 코드**다:

- **-32003** + `txpool is full` → reth 계열 (op-reth / op-rbuilder / flashblocks builder)
- **-32000** + `txpool is full` → go-ethereum / op-geth (geth에서 -32003은 `errcodeResponseTooLarge`로 전혀 다른 의미)

즉 이 로그를 보고 있다면 **시퀀서는 reth 계열**이다.

## 주요 인터페이스/필드

### 진단 절차

**Step 0 — 로그 주체 확인 (replica 쪽)**

```bash
# 이 노드가 forwarding 노드인지 확인
op-reth node --help | grep -i "rollup.sequencer"
ps aux | grep -o '\--rollup.sequencer[^ ]* [^ ]*'
```
`--rollup.sequencer`가 있으면 replica가 맞다. **여기서 조정할 것은 없다** — 이 로그는 증상 전달일 뿐이고 재시도 로직도 없다.

**Step 1 — 시퀀서 서브풀 상태 확인 (원인 A/B 분기)**

```bash
# 시퀀서에서
curl -s -X POST -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","method":"txpool_status","params":[],"id":1}' \
  http://<sequencer>:8545
```
- 어느 서브풀이든 한도(기본 10,000)에 근접 → **원인 A**
- 4종 모두 한가한데도 에러 발생 → **원인 B 확정**

서브풀 4종 중 **하나만** 넘어도 전체 `discard_worst`가 돈다는 점에 주의한다 (pending만 보고 "여유 있다"고 판단하면 안 됨).

**Step 2 — 원인 B 확증 (계정별 확인)**

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","method":"txpool_contentFrom","params":["0x<sender>"],"id":1}' \
  http://<sequencer>:8545
```
특정 발신자의 미래 nonce tx가 16개 넘게 쌓여 있는지 본다.

**Step 3 — 시퀀서 로그에서 원본 에러 문자열 확인 (결정적)**

RPC 응답에서는 사라진 원본 메시지가 시퀀서 로그에는 남는다:

| 로그 문자열 | 원인 |
|-------------|------|
| `rejected due to 0x... being identified as a spammer` | **B** (계정 슬롯) |
| `transaction discarded outright due to pool size constraints` | **A** (용량) |

### 대응

**시퀀서 설정 (원인이 여기 있음):**

| 상황 | 조치 |
|------|------|
| 원인 A — 서브풀 용량 부족 | `--txpool.pending-max-count` / `--txpool.pending-max-size` 상향 (기본 10,000 / 20MB). queued·basefee·blobpool도 함께 점검 |
| 원인 B — 계정 슬롯 초과 | `--txpool.max-account-slots` 상향 (기본 16) |
| 신뢰하는 발신자 면제 | `--txpool.locals <address>` — slot 체크를 통째로 우회. 단 eviction 보호는 pending 서브풀에서만 적용됨 |
| 면제가 안 먹을 때 | `--txpool.nolocals`가 켜져 있으면 위 `--txpool.locals`가 **무효화**된다 → [nolocals 페이지](../concepts/op-reth-txpool-nolocals.md) |

**애플리케이션 쪽:**

- 원인 A → gas price / priority fee를 올려 축출 후보에서 벗어난다.
- 원인 B → hot wallet 하나로 미래 nonce를 16개 넘게 쌓지 말고, 앞 tx 확정 후 순차 제출하거나 발신 계정을 분산한다.

**⚠️ 흔한 착각:** "replica RPC로 직접 넣었으니 시퀀서에서 local 특혜를 받겠지" — 성립하지 않는다. reth v2.3.0의 `eth_sendRawTransaction`은 `TransactionOrigin::External`을 쓰므로 포워딩된 tx도 시퀀서에서 External로 취급된다. 면제를 받으려면 반드시 `--txpool.locals`로 **주소를 명시**해야 한다.

### 프록시가 끼어 있는 경우

시퀀서가 `op-conductor`나 `rollup-boost` 뒤에 있어도 에러는 그대로 통과한다. `rollup-boost`의 `parse_response_code`는 JSON-RPC 에러 코드를 **로깅만 하고 변형하지 않는다** (`resource/optimism/rust/rollup-boost/crates/rollup-boost/src/client/http.rs:92-115`). 프록시 자체는 원인이 아니다.

## 관련 페이지

- [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")](../concepts/reth-txpool-capacity-slot-limits.md) — 이 런북이 진단하는 **원인 A/B의 메커니즘 정본**. 서브풀 한도, `max_account_slots` 정확한 의미, 두 에러가 -32003으로 붕괴되는 코드 경로.
- [op-reth --txpool.nolocals & Local Transaction Exemption](../concepts/op-reth-txpool-nolocals.md) — 대응책 중 `--txpool.locals`가 무력화되는 조건.
- [op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로](op-reth-changeset-cache-miss.md) — 동일 op-reth 로그 진단 런북 계열. 단, 그쪽은 무해·자가복구 WARN인 반면 **이 로그는 사용자 tx가 실제로 유실되는 실패 신호**다.
- [OP Stack 트랜잭션 수수료 & EIP-1559 (maxFeePerGas / maxPriorityFeePerGas)](../concepts/op-stack-eip1559-fees.md) — 원인 A 대응(priority fee 상향)의 근거 모델.

## 출처

**코드 정본 (`resource/optimism` @ `aaeb6c0154`, CodeGraph 조회):**
- `rust/op-reth/crates/rpc/src/sequencer.rs:138-193` — 로그 발생 지점, `forward_raw_transaction` / `forward_raw_transaction_conditional`
- `rust/op-reth/crates/rpc/src/eth/transaction.rs:45-81` — 포워딩 실패 시 조기 반환(로컬 풀 미보관), `raw_tx_forwarder`
- `rust/op-reth/crates/rpc/src/eth/mod.rs:571-579` — `SequencerClient` 생성 조건
- `rust/op-reth/crates/rpc/src/error.rs:43-68` — `OpEthApiError::Sequencer` → RPC 에러 변환
- `rust/op-reth/crates/node/src/args.rs:88,148` — `--rollup.sequencer`(별칭 `-http`/`-ws`), `--rollup.sequencer-headers`
- `rust/rollup-boost/crates/rollup-boost/src/client/http.rs:92-115` — `parse_response_code` (코드 로깅만, 변형 없음)
- `rust/Cargo.toml:411` — reth v2.3.0 pin

**코드 정본 — reth v2.3.0 (시퀀서 측 거절 로직):**
- [`crates/rpc/rpc-eth-types/src/error/mod.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/rpc/rpc-eth-types/src/error/mod.rs) — `RpcPoolError::TxPoolOverflow` → -32003
- [`crates/transaction-pool/src/pool/txpool.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/pool/txpool.rs) — `ensure_valid` slot 체크(1864-1881)
- [`crates/transaction-pool/src/pool/mod.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/pool/mod.rs) — `DiscardedOnInsert`(697-728)
- [`crates/rpc/rpc-eth-api/src/helpers/transaction.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/rpc/rpc-eth-api/src/helpers/transaction.rs) — `TransactionOrigin::External`(79-87)

**대조 — go-ethereum (master):**
- [`core/txpool/legacypool/legacypool.go`](https://github.com/ethereum/go-ethereum/blob/master/core/txpool/legacypool/legacypool.go) — `ErrTxPoolOverflow = errors.New("txpool is full")`(62)
- [`rpc/errors.go`](https://github.com/ethereum/go-ethereum/blob/master/rpc/errors.go) — `errcodeDefault = -32000`, `errcodeResponseTooLarge = -32003`(61-63)
