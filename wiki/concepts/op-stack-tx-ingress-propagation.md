---
type: Concept
title: OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)
description: 사용자 트랜잭션이 시퀀서에 도달하는 두 경로(HTTP 포워딩 vs devp2p gossip)와 Optimism 공식 Tx Ingress Node 아키텍처, op-geth/op-reth의 포워딩 시 로컬 풀 보존 차이, Ingress가 실제로 덜어주는 부하(읽기 RPC·무효 트래픽)와 덜어주지 못하는 부하(ecrecover·nonce/잔액 검증)
resource: resource/optimism/rust/op-reth/crates/rpc/src/eth/transaction.rs
tags: [op-stack, p2p, txpool, reth, sequencer, l2]
timestamp: 2026-08-28T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)

## 개요

OP Stack에서 사용자 트랜잭션이 시퀀서에 도달하는 경로는 **두 가지**이며, 어느 쪽을 쓰느냐에 따라 지연 특성·장애 모드·조회 가능 여부가 전부 달라진다.

| | 길 A — HTTP 포워딩 | 길 B — Ingress + devp2p gossip |
|---|---|---|
| 트리거 | `--rollup.sequencer`(op-reth) / `--rollup.sequencerhttp`(op-geth) | 위 플래그를 **설정하지 않음** |
| 경로 | 노드 → 시퀀서 RPC 직접 | 노드 풀 → devp2p gossip → 시퀀서 풀 |
| 홉 | 1 | 1~2 |
| 실패 시 | 사용자에게 RPC 에러 반환 | **무증상** (fire-and-forget) |
| 용도 | 공개 리플리카 | **체인 오퍼레이터 내부망 (공식 권장)** |

길 B가 [OP Stack chain architecture 문서](https://docs.optimism.io/chain-operators/reference/architecture)가 명시적으로 권장하는 구조다.

> "These nodes receive `eth_sendRawTransaction` calls from the public and then gossip the transactions to the internal execution-layer network."
>
> "Sequencers receive transactions from the Tx Ingress Nodes via execution-layer p2p gossip."
>
> "Leave `--rollup.disable-tx-pool-gossip` unset so transactions are gossiped to sequencers."

## 핵심 동작/책임

### 먼저 정리할 혼동 — P2P가 두 개다

이름이 같아 섞이기 쉬우나 완전히 별개의 네트워크다.

| | op-node의 P2P | op-geth/op-reth의 P2P |
|---|---|---|
| 기술 | libp2p (gossipsub) | devp2p (eth wire protocol) |
| 무엇을 나르나 | **블록**(unsafe payload) | **트랜잭션** |
| 방향 | 시퀀서 → 모든 노드 | 노드 ↔ 노드 |
| 관련 플래그 | `--p2p.*` | `--tx-propagation-*`, `--rollup.*`, `--trusted-peers` |

"P2P gossip으로 트랜잭션을 전달한다"는 말은 **아래쪽(devp2p)** 이야기다. op-node의 `--p2p.*` 플래그는 트랜잭션 전파에 아무 영향이 없다 (→ [op-node P2P Peering](op-node-p2p-peering.md)).

### 길 A — HTTP 포워딩과 로컬 풀 보존 (클라이언트 간 차이)

**op-reth는 포워딩 후에도 항상 로컬 풀에 보존한다.**

```rust
// resource/optimism/rust/op-reth/crates/rpc/src/eth/transaction.rs:57-70
if let Some(client) = self.raw_tx_forwarder().as_ref() {
    let hash = client.forward_raw_transaction(&tx).await...?;
    // Retain tx in local tx pool after forwarding, for local RPC usage.
    let _ = self.inner.eth_api.add_pool_transaction(origin, pool_transaction).await...;
    return Ok(hash);
}
```

**op-geth는 기본적으로 보존하지 않는다.**

```go
// op-geth cmd/utils/flags.go:2148
cfg.RollupDisableTxPoolAdmission = cfg.RollupSequencerHTTP != "" && !ctx.Bool(RollupTxPoolEnableAdmissionFlag.Name)
```

```go
// op-geth eth/api_backend.go:332-358
if b.eth.seqRPCService != nil { ... 포워딩 ... }
if b.disableTxPool { return nil }              // ← 기본 true (sequencerhttp 설정 시)
// Retain tx in local tx pool after forwarding, for local RPC usage.
err := b.sendTx(ctx, signedTx)
```

⚠️ **실무 함의:** `--rollup.sequencerhttp`만 켠 op-geth 노드에서는 제출 직후 `eth_getTransactionByHash`가 `null`을 반환한다(블록이 도착할 때까지). 버그가 아니라 기본 동작이며 `--rollup.txpool.enable-admission`으로 되돌린다. **op-reth에는 이 스위치가 없고 항상 보존하므로**, 두 클라이언트를 섞어 쓰면 동일 설정에서 응답이 갈린다.

### 길 B — Ingress 구조에서 Ingress가 실제로 덜어주는 부하

**흔한 오해:** "Ingress를 두면 시퀀서의 트랜잭션 처리 부하가 줄어든다."

**사실:** 유효한 트랜잭션에 대해서는 **바이트도, 검증 CPU도 줄지 않는다.** 시퀀서가 전부 다시 한다.

| 시퀀서가 감당해야 할 부하 | Ingress가 흡수? |
|---|---|
| 공개 인터넷 노출, TLS 핸드셰이크, HTTP 커넥션 수천 개 | ✅ 전부 |
| **읽기 RPC** (`eth_call`, `eth_getLogs`, `debug_trace*` …) | ✅ **전부 — 진짜 핵심** |
| 잘못된 트랜잭션의 검증 비용 (서명 불량·nonce 미달·잔액 부족·저가) | ✅ 전부 (시퀀서에 도달조차 안 함) |
| 중복 제출 (클라이언트 재시도) | ✅ 전부 (Ingress 풀이 해시로 dedup) |
| DoS 홍수의 타격 | ✅ 격리 (Ingress가 죽지 시퀀서는 안 죽음) |
| **유효한 트랜잭션의 서명 검증(ecrecover)** | ❌ **못 덜어줌** |
| **유효한 트랜잭션의 nonce·잔액·intrinsic gas 검증** | ❌ **못 덜어줌** |
| **유효한 트랜잭션의 본문 바이트** | ❌ 못 덜어줌 |

**서명 검증은 프로토콜상 위임이 불가능하다.** 와이어로 들어온 트랜잭션은 RLP에서 갓 디코딩된 새 객체라 sender 캐시가 비어 있고, 받는 노드가 직접 ecrecover를 돌린다. "이 트랜잭션의 sender는 0xAlice야"를 피어 말만 믿으면 서명 검증을 안 하는 것과 같다.

```go
// op-geth core/txpool/validation.go:154 — 풀 진입 시 ecrecover
if _, err := types.Sender(signer, tx); err != nil {

// op-geth core/types/transaction_signing.go:145-161 — 캐시는 객체 내부에만
func Sender(signer Signer, tx *Transaction) (common.Address, error) {
	if sigCache := tx.from.Load(); sigCache != nil {   // tx.from atomic.Pointer
		if sigCache.signer.Equal(signer) { return sigCache.from, nil }
	}
	addr, err := signer.Sender(tx)                     // 없으면 ecrecover 실행
	...
}
```

nonce·잔액은 시퀀서에서 **두 번** 검사한다 — 풀 admission에서 한 번(`validation.go`), 블록 실행에서 또 한 번(`core/state_transition.go:364-375`).

> **한 줄 요약:** Ingress는 "시퀀서가 처리할 트랜잭션의 양"을 줄이는 게 아니라, **"시퀀서가 트랜잭션 말고 해야 할 일"을 없애는 장치**다. 무거운 `eth_call` 하나가 [2초 블록 빌드 윈도](op-stack-block-production.md)와 CPU·상태 접근을 두고 경쟁하는 것을 막는 데 가치가 있다.

### 시퀀서는 필요할 때 가져갈 수 없다

시퀀서는 블록을 만들 때 **자기 로컬 풀만 본다.**

```go
// op-geth miner/worker.go:774
pendingPlainTxs, plainTxCount := miner.txpool.Pending(filter)
```

빌드 도중 원격 풀을 조회하는 경로가 코드에 없고, 무엇이 필요한지는 다 받아서 수수료순으로 정렬해봐야 알기 때문에 애초에 선별할 수도 없다. 즉 **push든 pull이든 유효한 트랜잭션은 전부 시퀀서에 도착하며**, 바뀌는 것은 *언제* 도착하느냐뿐이다.

## 주요 인터페이스/필드

### 클라이언트별 플래그 대응

| 목적 | op-reth | op-geth |
|---|---|---|
| 시퀀서 포워딩 | `--rollup.sequencer <url>`<br>(alias `--rollup.sequencer-http/-ws`) | `--rollup.sequencerhttp <url>` |
| tx gossip 비활성화 | `--rollup.disable-tx-pool-gossip` | `--rollup.txpool.disable-gossip`<br>(alias `--rollup.disabletxpoolgossip`) |
| 포워딩 시 로컬 풀 보존 | **항상 보존** (스위치 없음) | `--rollup.txpool.enable-admission` |
| 전파 대상 필터 | `--tx-propagation-policy <all\|trusted\|none>` | `--rollup.txpool.trusted-peers-only`<br>`--rollup.txpool.netrestrict <CIDR>` |
| 원본/알림 분할 | `--tx-propagation-mode <sqrt\|all\|max:N>` | **없음** |
| pending 블록 계산 | `--rollup.compute-pending-block` (미구현 주석) | `--rollup.computependingblock` |

⚠️ **공식 문서가 두 클라이언트 표기를 섞어 쓴다.** 아키텍처 문서는 `--rollup.disable-tx-pool-gossip`(op-reth 표기)을 쓰지만 op-geth의 정식 이름은 `--rollup.txpool.disable-gossip`이다. 그대로 복사하면 op-geth에서 파싱 에러가 난다.

### Ingress 구조의 조용한 장애 3종

gossip은 fire-and-forget이라 **시퀀서에 도달하지 못해도 사용자는 성공 응답(트랜잭션 해시)을 받는다.**

| 장애 | 원인 | 관측 지표 |
|---|---|---|
| **싱크 중 전파 정지** | 노드가 `synced=false`면 tx gossip 자체가 죽는다 (`op-geth eth/handler_eth.go:46-59` `AcceptTxs`; 이 플래그는 op-node의 `engine_forkchoiceUpdated`가 로컬 헤드를 지정할 때 켜진다 — `eth/catalyst/api.go:338`) | `eth_syncing`, `net_peerCount` |
| **Ingress 풀 포화** | 시퀀서 도달 전 유실 (→ [txpool 용량 한도](reth-txpool-capacity-slot-limits.md)) | `skipped_transactions_pending_pool_imports_at_capacity` |
| **nonce 갭 정지** | 갭에 막힌 tx는 gossip되지 않음 | → [nonce 갭 전파 정지](txpool-nonce-gap-propagation-stall.md) |

세 경우 모두 **에러도 로그도 없다.** 헬스체크에 `eth_syncing` + `net_peerCount`를 넣고 싱크 완료 전에는 로드밸런서에서 빼야 한다.

### 시퀀서 풀 포화가 상류로 전파되지 않는다

시퀀서 풀이 가득 차 트랜잭션을 거부해도 Ingress는 알 수 없다. HTTP 포워딩이었다면 `-32003 txpool is full`이 사용자에게 그대로 반환된다 (→ [sequencer forward txpool full 진단](../runbooks/op-reth-sequencer-forward-txpool-full.md)).

### op-conductor는 tx 제출을 프록시하지 않는다

HA 구성에서 "리더에게만 포워딩"을 구현하려 할 때 흔히 기대하는 것과 다르다. conductor의 `eth_` 프록시 범위는 **`eth_getBlockByNumber` 하나뿐**이며, op-batcher/op-proposer용이다.

```go
// resource/optimism/op-conductor/rpc/api.go:67-71
// ExecutionProxyAPI defines the methods proxied to the execution 'eth_' rpc backend
// This should include all methods that are called by op-batcher or op-proposer
type ExecutionProxyAPI interface {
	GetBlockByNumber(ctx context.Context, number rpc.BlockNumber, fullTx bool) (map[string]interface{}, error)
}
```

리더 라우팅이 필요하면 `conductor_leader` / `conductor_leaderWithID`(`op-conductor/rpc/api.go:41-44`)를 헬스체크로 쓰는 LB를 직접 구성해야 한다.

## 관련 페이지

- [트랜잭션 `√n` 브로드캐스트 규칙](tx-propagation-sqrt-broadcast.md) — 본 페이지의 길 B에서 **어느 피어가 원본을 받고 어느 피어가 해시 알림만 받는지**를 결정하는 규칙. Ingress→시퀀서 지연의 직접 원인이다.
- [txpool nonce 갭으로 인한 전파 정지](txpool-nonce-gap-propagation-stall.md) — Ingress를 **여러 대** 두고 로드밸런서로 분산할 때 발생하는 최대 위험. 본 페이지의 "조용한 장애 3종" 중 하나를 상세히 다룬다.
- [op-node P2P Peering & Chain Isolation](op-node-p2p-peering.md) — 본 페이지가 다루는 **EL(devp2p) 트랜잭션 전파**와 대비되는 **CL(libp2p) 블록 전파**. 두 네트워크가 별개임을 확인하는 페이지.
- [op-reth --max-outbound-peers & devp2p 피어 슬롯 제어](op-reth-max-outbound-peers.md) — 본 페이지의 gossip이 흐르는 그 EL 피어 네트워크의 **연결 개수**를 정하는 설정. 피어 수는 `√n` 분할의 입력값이기도 하다.
- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](op-stack-block-production.md) — 시퀀서가 로컬 풀만 보고 블록을 만드는 사이클. 본 페이지의 "필요할 때 가져갈 수 없다"의 근거.
- [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한](reth-txpool-capacity-slot-limits.md) — Ingress 풀이 포화되면 트랜잭션이 시퀀서 도달 전에 유실된다. 그 한도의 메커니즘.
- [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth-txpool-nolocals.md) — Ingress 풀은 "실제로 사용자 트랜잭션이 사는 곳"이므로 local 면제 설정이 스팸 저항성에 직접 영향을 준다.
- [op-reth "HTTP request to sequencer failed ... -32003" 진단](../runbooks/op-reth-sequencer-forward-txpool-full.md) — 본 페이지 길 A(포워딩)의 대표 장애.

## 출처

- [OP Stack chain architecture — Optimism Docs](https://docs.optimism.io/chain-operators/reference/architecture) — Tx Ingress Nodes 정의 (**이 구조의 1차 근거**)
- [Chain operator best practices — Optimism Docs](https://docs.optimism.io/operators/chain-operators/management/best-practices)
- `resource/optimism/rust/op-reth/crates/rpc/src/eth/transaction.rs:44-95` — 포워딩 후 항상 로컬 보존
- `resource/optimism/rust/op-reth/crates/node/src/args.rs:84-180` — `RollupArgs`
- `resource/optimism/op-conductor/rpc/api.go:41-44, 67-71` — 리더 조회 RPC, 프록시 범위
- op-geth `v1.101702.3-rc.4` — `eth/api_backend.go:332-358`, `cmd/utils/flags.go:1044-1125,2148`, `core/txpool/validation.go:154`, `core/types/transaction_signing.go:145-161`, `core/state_transition.go:364-375`, `miner/worker.go:774`, `eth/handler_eth.go:46-59`, `eth/catalyst/api.go:338`
