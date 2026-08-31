---
type: Concept
title: txpool nonce 갭으로 인한 트랜잭션 전파 정지
description: 로드밸런서가 한 계정의 연속 nonce를 여러 Ingress 노드에 흩뿌릴 때 갭에 막힌 트랜잭션이 queued 서브풀에 갇혀 gossip 자체가 되지 않고 블록당 한 칸씩만 진행하는 메커니즘 — 풀은 갭을 허용해 에러도 로그도 없으며, 전파 이벤트가 pending 승격 시에만 발행되는 것이 원인, sticky LB와 Ingress 상호 피어링으로 해소
resource: resource/optimism/rust/op-reth/crates/net/network/src/transactions/mod.rs
tags: [op-stack, txpool, p2p, reth, sequencer, l2]
timestamp: 2026-08-28T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# txpool nonce 갭으로 인한 트랜잭션 전파 정지

## 개요

Ingress 노드를 **여러 대** 두고 로드밸런서로 분산하는 구조에서, 같은 계정이 연속 nonce를 빠르게 제출하면 **한 블록에 다 들어갈 수 있었던 트랜잭션이 여러 블록에 걸쳐 한 칸씩만 진행**한다.

원인은 두 가지 사실의 결합이다.

1. **풀은 nonce 갭을 허용한다** — 갭이 있는 트랜잭션도 정상 접수되어 `queued`(대기) 서브풀에 앉는다. 사용자는 성공 응답(트랜잭션 해시)을 받는다.
2. **queued 트랜잭션은 gossip되지 않는다** — 전파 이벤트가 `pending` 승격 시에만 발행되므로, 갭에 막힌 트랜잭션은 **시퀀서에게 존재 자체가 알려지지 않는다.**

**에러도 없고 로그도 없다.** 블록당 한 칸씩 전진하는 패턴으로만 드러나므로, [`√n` 브로드캐스트](tx-propagation-sqrt-broadcast.md)의 밀리초 단위 지연과 달리 **수 초~수십 초** 규모이면서도 모니터링에 잡히지 않는다.

## 핵심 동작/책임

### 재현 시나리오

```
sender A, 현재 state nonce = 1
LB가 라운드로빈으로 분산 →
  ingress-1 ← nonce 1, 3, 4
  ingress-2 ← nonce 2, 5, 6
```

```
t0   ingress-1 풀: 1=pending ✅   3,4=queued (2번 갭)
     ingress-2 풀: 2,5,6=queued   (1번 갭)
     → gossip 나가는 건 nonce 1 하나뿐

블록 N   [1]        state nonce → 2
     ingress-2가 블록 N을 보고 → 2 승격 → gossip
     ingress-1은 2가 없으니 3,4 여전히 queued

블록 N+1 [2]        state nonce → 3
     ingress-1 → 3,4 승격 → gossip

블록 N+2 [3,4]      state nonce → 5
     ingress-2 → 5,6 승격 → gossip

블록 N+3 [5,6]
```

**6개가 4블록(8초)에 걸쳐 나간다.** 각 블록이 갭을 한 칸씩만 메우기 때문이며, 트랜잭션 수가 많고 Ingress에 고르게 흩어질수록 심해진다.

### ① 풀은 갭을 명시적으로 허용한다

```go
// op-geth core/txpool/legacypool/legacypool.go:660
FirstNonceGap: nil, // Pool allows arbitrary arrival order, don't invalidate nonce gaps
```

```go
// op-geth core/txpool/validation.go:299-301 — 낮은 nonce만 거부
next := opts.State.GetNonce(from)
if next > tx.Nonce() {
    return fmt.Errorf("%w: next nonce %v, tx nonce %v", core.ErrNonceTooLow, next, tx.Nonce())
}
// 갭(높은 nonce) 체크는 선택적
if opts.FirstNonceGap != nil { ... }
```

`ErrNonceTooLow`만 있고 "너무 높다"는 기본적으로 없다. blobpool은 `FirstNonceGap`을 설정해 갭을 제한하지만(`blobpool.go:1293-1300`), OP Stack L2는 blob 트랜잭션을 거부하므로 무관하다.

### ② queued는 gossip되지 않는다 (핵심)

전파를 담당하는 네트워크 매니저가 구독하는 것은 **pending 리스너뿐**이다.

```rust
// reth v2.3.0 crates/net/network/src/transactions/mod.rs
let pending = pool.pending_transactions_listener();
```

문서 주석이 조건을 명시한다.

> "A transaction is considered **pending** if it is executable on the current state of the chain. In other words, this only yields transactions that satisfy all consensus requirements, these include: **no nonce gaps**, all dynamic fee requirements are (currently) met, account has enough balance to cover the transaction's gas"

op-geth도 동일하다 — `promoted`(pending 승격) 트랜잭션에만 이벤트가 발행된다.

```go
// op-geth core/txpool/legacypool/legacypool.go:1386-1400
// Notify subsystems for newly added transactions
for _, tx := range promoted {          // ← promoted만
    ...
}
if len(events) > 0 {
    pool.txFeed.Send(core.NewTxsEvent{Txs: txs})   // ← BroadcastTransactions를 깨우는 이벤트
}
```

따라서 **갭에 막힌 트랜잭션은 원본도 해시 알림도 나가지 않는다.** 다른 노드는 그 트랜잭션의 존재를 알 방법이 없다.

### ③ 왜 조용한가

| | HTTP 포워딩 | Ingress + gossip |
|---|---|---|
| 갭 트랜잭션의 응답 | (시퀀서가 판단) | **성공 (해시 반환)** |
| 로그 | — | **없음** |
| 메트릭 | — | `bad_imports`에 **안 잡힘** |

reth의 `bad_imports` 카운터 주석이 이를 명시한다 — *"imports that fail because the transaction is badly formed (i.e. have no chance of passing validation, **unlike imports that fail due to e.g. nonce gaps**)"*. 갭은 실패가 아니라 정상 대기 상태로 취급된다.

## 주요 인터페이스/필드

### 해결책 ① — 로드밸런서 sticky session (근본)

같은 클라이언트의 트랜잭션이 항상 같은 Ingress로 가면 갭이 애초에 생기지 않는다.

- sender 주소로 라우팅하려면 LB가 raw tx를 파싱해 ecrecover까지 해야 하므로 비싸다.
- **source IP 해시로 충분하다.** 봇·마켓메이커·브릿지처럼 연속 nonce를 쏘는 주체는 커넥션·IP가 고정인 것이 일반적이다.
- 거의 모든 LB의 기본 기능이며 비용이 0이다.

### 해결책 ② — Ingress 노드끼리 EL 피어링 (안전망)

피어를 맺으면 갭이 스스로 메워진다.

```
ingress-1: nonce 1 pending → 브로드캐스트 (시퀀서 + ingress-2)
ingress-2: nonce 1 수신 → 갭 해소 → 2 승격 → 브로드캐스트
ingress-1: nonce 2 수신 → 3,4 승격 → 브로드캐스트
ingress-2: nonce 3,4 수신 → 5,6 승격 → 브로드캐스트
```

노드는 출처를 구분하지 않고 풀에 들어온 트랜잭션을 다시 뿌리므로(`op-geth eth/handler.go:433,534-535`) 연쇄가 성립한다. 전부 사내망 왕복이라 **수 ms 안에 완료**되어 같은 블록에 들어간다. **8초 → 2초.**

sticky가 깨지는 경우(Ingress 장애 전환, 클라이언트 IP 변경, NAT 뒤 다중 사용자)를 위한 보험이므로 ①과 함께 쓴다.

> ⚠️ 이 조치는 Ingress의 피어 수를 늘려 [`√n` 원본 비율](tx-propagation-sqrt-broadcast.md)을 떨어뜨린다. 그러나 op-reth 기준 `√n` 손해는 밀리초 단위이고 갭 손해는 초 단위이므로 **갭 해소가 압도적으로 우선**한다. `--tx-propagation-mode all`을 켜면 두 비용이 동시에 사라진다.

### 진단 절차

전용 로그·메트릭이 없으므로 **블록 포함 패턴**으로 확인한다.

```
한 주소에서 연속 nonce 10개를 LB를 통해 제출
→ ingress-1/2로 흩어지게 함
→ 각 트랜잭션이 몇 번째 블록에 들어갔는지 확인

정상:   전부 같은 블록 (또는 2블록 이내)
문제:   블록당 1~2개씩 계단식으로 진행
```

보조 지표:

| 확인 | 방법 |
|---|---|
| 각 Ingress의 queued 적체 | `txpool_status` (`queued` 값이 지속적으로 0이 아님) |
| Ingress 간 피어 연결 여부 | `admin.peers` / `net_peerCount` |
| `√n` 지연과의 구분 | 지연이 **수 초·계단식**이면 갭, **수 ms~수백 ms 이봉 분포**면 `√n` |

⚠️ `eth_subscribe("newPendingTransactions")`로 지연을 잴 때 **갭이 있으면 결과가 오염된다.** 승격 시점에 발화하기 때문이다. `√n`을 측정할 때는 반드시 갭 없는 연속 nonce를 쓴다.

### 관련 설정

| 항목 | 영향 |
|---|---|
| `--txpool.lifetime` (op-geth 문서 권장 Ingress `3600`) | 갭에 막힌 트랜잭션이 오래 남아 슬롯을 먹는 것을 제한. 만료되면 **조용히 사라진다** |
| 계정 슬롯 한도 (`max_account_slots` 기본 16) | queued에 쌓인 미래 nonce가 이 한도를 소진해 후속 제출이 거부될 수 있다 (→ [txpool 용량 한도](reth-txpool-capacity-slot-limits.md)) |
| local 면제 (`--txpool.locals`) | ⚠️ **eviction 면제는 pending 서브풀에서만 적용된다.** 갭으로 parked/queued에 머무는 동안에는 보호받지 못한다 (→ [--txpool.nolocals](op-reth-txpool-nolocals.md)) |

## 관련 페이지

- [OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)](op-stack-tx-ingress-propagation.md) — 본 페이지의 문제가 발생하는 **상위 구조**. Ingress를 여러 대 두는 배치가 전제다.
- [트랜잭션 `√n` 브로드캐스트 규칙](tx-propagation-sqrt-broadcast.md) — 같은 "전파 지연"이지만 규모가 1000배 작다. 측정 시 두 현상을 반드시 구분해야 하며, 해결책 ②가 이 페이지의 확률에 영향을 준다.
- [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한](reth-txpool-capacity-slot-limits.md) — 갭으로 queued에 쌓인 트랜잭션이 계정 슬롯을 소진하면 후속 제출이 `-32003`으로 거부된다.
- [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth-txpool-nolocals.md) — local eviction 면제가 pending에만 적용되어, 갭 상태의 트랜잭션은 보호받지 못한다.
- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](op-stack-block-production.md) — "블록당 한 칸"의 시간 단위(2초)를 정하는 사이클.

## 출처

**reth `v2.3.0`**
- `crates/net/network/src/transactions/mod.rs` — `pool.pending_transactions_listener()` 구독 및 pending 정의 주석("no nonce gaps")
- `crates/net/network/src/metrics.rs` — `bad_imports` 주석("unlike imports that fail due to e.g. nonce gaps")

**op-geth `v1.101702.3-rc.4`**
- `core/txpool/legacypool/legacypool.go:660` — `FirstNonceGap: nil` (갭 허용)
- `core/txpool/legacypool/legacypool.go:1386-1400` — `promoted`만 `txFeed.Send`
- `core/txpool/validation.go:290-312` — `ErrNonceTooLow`만 검사, 갭 체크는 선택적
- `core/txpool/blobpool/blobpool.go:1293-1300` — `FirstNonceGap` 설정 예 (대조군)
- `eth/handler.go:433, 529-540` — 출처 무관 재브로드캐스트 (해결책 ②의 근거)

**문서**
- [OP Stack chain architecture — Optimism Docs](https://docs.optimism.io/chain-operators/reference/architecture) — Tx Ingress Node 다중 배치 권장

## 미검증 / 주의

- **8초 타임라인은 코드에서 유도한 모델**이며 실측하지 않았다. 위 진단 절차로 확인이 필요하다.
- reth 풀의 **갭 수용**(queued 진입) 동작은 op-geth 코드로 확인했고, reth 쪽은 `pending_transactions_listener` 주석으로 간접 확인했다. reth 풀의 갭 수용 코드는 직접 보지 않았다.
- LB의 source IP sticky가 실제 트래픽 패턴(NAT·프록시 뒤 다중 사용자)에서 얼마나 유효한지는 환경마다 다르다.
