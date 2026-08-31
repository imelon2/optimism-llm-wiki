---
type: Concept
title: 트랜잭션 √n 브로드캐스트 규칙 (원본 전송 vs 해시 알림)
description: 노드가 새 트랜잭션의 원본을 피어 일부에게만 보내고 나머지에겐 해시만 알리는 규칙과 그 지연 비용 — op-reth는 round(√n)+1개에 즉시 요청(~1 RTT), op-geth는 ceil(√n)개에 txArriveTimeout 400ms 대기로 비용이 500배 차이, 선택 기준도 피어 순번(reth) vs sender 주소(geth)로 달라 증상 모양이 반대, 이 규칙은 devp2p 표준이 아님
resource: resource/optimism/rust/op-reth/crates/node/src/args.rs
tags: [op-stack, p2p, txpool, reth, sequencer, l2]
timestamp: 2026-08-28T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# 트랜잭션 √n 브로드캐스트 규칙 (원본 전송 vs 해시 알림)

## 개요

EL 노드는 새 트랜잭션을 **모든 피어에게 보내지 않는다.** 일부에게만 **원본**(`Transactions` 0x02)을 보내고, 나머지에겐 **"나한테 이런 게 있다"는 해시 알림**(`NewPooledTransactionHashes` 0x08)만 보낸다. 알림만 받은 노드는 필요하면 `GetPooledTransactions`(0x09)로 가지러 간다.

원본 대상 수는 대략 `√(피어 수)`다. 이는 피어 50개짜리 **공개 메인넷의 대역폭 최적화**이며, 피어가 서너 개뿐인 사내망에서는 아낄 대역폭도 대신 뿌려줄 이웃도 없어 순수한 손해가 된다.

**핵심 결론 3가지:**

1. **비용이 클라이언트마다 500배 차이 난다.** op-geth는 알림을 받으면 `txArriveTimeout` **400~500ms를 의도적으로 대기**한다. **op-reth에는 그 대기가 없어 즉시 요청**하므로 비용이 왕복 한 번(사내망 ~1~2ms)이다.
2. **선택 기준이 달라 증상 모양이 정반대다.** geth는 **sender 주소** 기반이라 "특정 지갑만 항상 느림", reth는 **피어 순번** 기반이라 "전부 느리거나 전부 빠르거나"가 된다.
3. **알림은 이미 갖고 있으면 그냥 버려진다.** 원본이 먼저 도착하면 알림은 무해하다. 비용은 "아무도 원본을 안 보냈을 때"만 발생한다.

## 핵심 동작/책임

### op-reth — 분할 로직

```rust
// reth v2.3.0 crates/net/network/src/transactions/mod.rs — propagate_transactions
let max_num_full = self.config.propagation_mode.full_peer_count(self.peers.len());
//                                                              ^^^^^^^^^^^^^^^^ 전체 피어

// Note: Assuming ~random~ order due to random state of the peers map hasher
for (peer_idx, (peer_id, peer)) in self.peers.iter_mut().enumerate() {
    if !self.policies.propagation_policy().can_propagate(peer) {
        // skip peers we should not propagate to
        continue                            // ← 걸러내지만 peer_idx는 이미 소모됨
    }
    let mut builder = if peer_idx > max_num_full {
        PropagateTransactionsBuilder::pooled(peer.version)   // 해시 알림
    } else {
        PropagateTransactionsBuilder::full(peer.version)     // 원본
    };
```

```rust
// reth v2.3.0 crates/net/network/src/transactions/config.rs
enum TransactionPropagationMode {
    #[default] Sqrt,   // (peer_count as f64).sqrt().round()
    All,               // 전체 피어에게 원본
    Max(usize),        // peer_count.min(max)
}
```

**off-by-one:** 비교가 `>=`가 아니라 `>`이므로 실제 원본 대상은 `max_num_full + 1`개다.

| 피어 수 | `round(√n)` | **원본 받는 수** | 비율 |
|---|---|---|---|
| 1~3 | 1~2 | **전부** | **100%** |
| 4 | 2 | **3** | 75% |
| 5 | 2 | 3 | 60% |
| 6 | 2 | 3 | 50% |
| 7 | 3 | 4 | 57% |
| 9 | 3 | 4 | 44% |

**피어가 3개 이하면 `sqrt` 모드가 `all` 모드와 사실상 같아진다.**

### op-geth — 분할 로직 (대조군)

```go
// op-geth eth/handler.go:707-745
func (bc *broadcastChoice) choosePeers(peers []*ethPeer, txSender common.Address) map[*ethPeer]struct{} {
	hash := siphash.New(bc.key[:])
	for i, peer := range peers {
		hash.Reset()
		hash.Write(bc.self[:])                   // 브로드캐스트하는 노드 자신의 ID
		hash.Write(peer.Peer.Peer.ID().Bytes())  // 피어 ID
		hash.Write(txSender[:])                  // ★ 트랜잭션 보낸 사람 주소
		bc.tmp[i] = broadcastPeer{peer, hash.Sum64()}
	}
	slices.SortFunc(bc.tmp, ...)
	n := int(math.Ceil(math.Sqrt(float64(len(bc.tmp)))))  // ★ 상위 ceil(√peers)개
	...
}
```

`txSender`가 해시 입력에 들어가므로 **어떤 지갑의 트랜잭션은 항상 원본을 받고, 어떤 지갑은 항상 알림만 받는** 고정 편향이 생긴다. 해시 키는 프로세스 기동 시 난수라(`eth/handler.go:169,692-695`) **재시작하면 느린 주소 집합이 통째로 재배정**된다.

두 클라이언트 모두 **원본 대상 선정이 "이미 아는 피어" 필터보다 먼저** 일어나므로, 이미 트랜잭션을 아는 피어가 원본 슬롯을 차지하면 그 슬롯은 그냥 버려진다.

### ★ 지연 비용의 500배 차이

```go
// op-geth eth/fetcher/tx_fetcher.go:65-71
txArriveTimeout = 500 * time.Millisecond   // 알림 후 실제 요청까지 대기
txGatherSlack   = 100 * time.Millisecond   // 실효 대기 ≈ 400ms
txFetchTimeout  = 5 * time.Second
```

**reth에는 이에 해당하는 상수가 없다.** `crates/net/network/src/transactions/constants.rs`에는 메시지 크기·동시성·캐시 상한만 있고, `fetcher.rs`는 알림을 받으면 필터링 후 곧바로 `GetPooledTransactions`를 보낸다.

```
op-geth 수신 시:  알림 → [400ms 대기] → 요청 → 응답     ≈ 500ms
op-reth 수신 시:  알림 → 요청 → 응답                    ≈ 1 RTT (사내망 ~1~2ms)
```

**대기하는 주체는 받는 쪽이다.** 시퀀서가 op-reth면 이 대기는 일어나지 않는다.

### 알림은 이미 갖고 있으면 버려진다

```
NewPooledTransactionHashes 도착 → on_new_pooled_transaction_hashes
 ├─ 1. 싱크 상태 확인 / 피어 조회
 ├─ 2. peer.seen_transactions 삽입 시도
 │      실패 → occurrences_hash_already_seen_by_peer +1
 ├─ 3. 메시지 검증 (빈 메시지·중복 해시 → bad announcement 신고)
 ├─ 4. pool.retain_unknown()          ★ 이미 풀에 있으면 여기서 제거
 │      → occurrences_hashes_already_in_pool +1
 ├─ 5. filter_unseen_and_pending_hashes()  (요청 중·bad import 이력 제거)
 └─ 6. 피어 idle → pack_request() → request_transactions_from_peer()  ← 즉시 전송
        피어 busy → buffer_hashes()                                   ← 여기가 지연 지점
```

4단계 때문에 **알림을 여러 장 받아도 원본 한 장만 먼저 오면 전부 무해하게 버려진다.** 즉 원본과 알림은 경쟁 관계이며, 손해는 "아무도 원본을 안 보냈을 때"만 발생한다.

그리고 **reth에서 지연이 생기는 유일한 경로는 6단계의 `buffer_hashes()`** 다 — 피어가 이미 요청을 처리 중이라 바쁠 때 해시가 큐에 쌓인다.

### 확률 모델 (op-reth, 5노드 풀메시)

Ingress 2 + 시퀀서 3, 각자 피어 4개, 원본 대상 3개. 트랜잭션이 ingress-1에서 발생하고 리더는 seq-1이라 하면:

```
1라운드: P(ingress-1이 seq-1을 빠뜨림) = 1/4
         (4개 중 3개가 원본이므로 빠지는 건 정확히 하나)
         → 빠졌다면 나머지 셋은 전부 원본을 받음

2라운드: 그 셋이 각자 재브로드캐스트, 각자 P(빠뜨림) = 1/4
         P(셋 다 빠뜨림) = (1/4)³ = 1/64

합계: 1/4 × 1/64 = 1/256 ≈ 0.39%
기대 손실: 0.0039 × 1.5ms ≈ 0.006ms
```

재브로드캐스트가 성립하는 이유는 **노드가 출처와 무관하게 풀에 들어온 트랜잭션을 다시 뿌리기 때문**이다(`op-geth eth/handler.go:433,534-535`의 `SubscribeTransactions`는 로컬/원격을 구분하지 않는다). 그리고 각 노드의 선택은 서로 독립이다 — reth는 노드마다 HashMap 시드가 다르고, geth는 해시 입력에 `bc.self`(자기 노드 ID)가 들어간다.

| 구성 (op-reth) | 노드 | 피어 | 원본 대상 | 브로드캐스터 | P(알림만) |
|---|---|---|---|---|---|
| Ingress 1 + 시퀀서 3 | 4 | 3 | **3 (전부)** | 3 | **0%** |
| Ingress 2 + 시퀀서 3 | 5 | 4 | 3 | 4 | **0.39%** |
| Ingress 3 + 시퀀서 3 | 6 | 5 | 3 | 5 | 1.0% |
| Ingress 4 + 시퀀서 3 | 7 | 6 | 3 | 6 | 1.6% |

⚠️ **중계자가 빠지면 지수가 줄어 급격히 나빠진다.** `policy`에 걸리거나 `synced=false`이거나 gossip이 꺼진 노드는 중계 집합에서 제외된다. 4→3개로 줄면 `1/4 × (1/4)² = 1.6%`로 4배가 된다.

동일 구성을 op-geth로 계산하면 `ceil(√4)=2`(원본 2개)라 약 **6.9%**이며, 건당 비용도 500ms라 실질 손해가 1000배 이상 차이 난다.

### 이 규칙은 devp2p 표준이 아니다

[devp2p `caps/eth.md`](https://github.com/ethereum/devp2p/blob/master/caps/eth.md) Transaction Exchange 절 원문:

> "When new transactions appear in the client's pool, it **should** propagate them to the network using the Transactions and NewPooledTransactionHashes messages."
>
> "The Transactions message relays complete transaction objects and is **typically sent to a small, random fraction of connected peers**."
>
> "A node should never send a transaction back to a peer that it can determine already knows of it."

`should`·`typically`이며 비율은 구현에 맡긴다. **트랜잭션에 대한 `√n` 공식은 명세에 없다.** 같은 문서에서 `√n`이 나오는 유일한 자리는 **블록** 전파(PoW 시절 `NewBlock`, The Merge 이후 사문화)다:

> "It then sends the block to a small fraction of connected peers (**usually the square root of the total number of peers**)."

출처는 [EIP-2464 (eth/65)](https://eips.ethereum.org/EIPS/eip-2464)의 **동기(Motivation)** — "선형 → 제곱근 복잡도"라는 설계 목표로 서술됐을 뿐 프로토콜 규정으로 승격된 적이 없다. geth의 결정론적 sender 기반 선택은 명세의 "random fraction" 문구와도 성격이 다르다.

## 주요 인터페이스/필드

### 이름이 비슷한 op-reth 플래그 두 개

| 플래그 | 결정하는 것 | 값 | 기본 |
|---|---|---|---|
| `--tx-propagation-mode` | **몇 명에게 원본**을 보낼지 | `sqrt` / `all` / `max:N` | `sqrt` |
| `--tx-propagation-policy` | **누구에게** 보낼지 (대상 필터) | `all` / `trusted` / `none` | `all` |

```rust
// reth v2.3.0 crates/net/network/src/transactions/config.rs
pub enum TransactionPropagationKind {
    /// Propagate transactions to all peers.  No restrictions
    #[default] All,
    /// Propagate transactions to only trusted peers.
    Trusted,
    /// Do not propagate transactions
    None,
}

fn can_propagate(&self, peer: &mut PeerMetadata<N>) -> bool {
    match self {
        Self::All     => true,
        Self::Trusted => peer.peer_kind.is_trusted(),
        Self::None    => false,
    }
}
```

`policy`는 op-geth의 `--rollup.txpool.trusted-peers-only`(=`trusted`) / `--rollup.txpool.disable-gossip`(=`none`)에 대응하는 **보안 필터**이며 **지연과 무관**하다.

**`policy`는 아웃바운드 전파만 게이팅한다.** `GetPooledTransactions` **서빙**은 영향받지 않는다.

```rust
// reth v2.3.0 crates/net/network/src/transactions/mod.rs
fn on_get_pooled_transactions(&mut self, peer_id, request, response) {
    // fast exit if gossip is disabled
    if self.network.tx_gossip_disabled() {   // ← --rollup.disable-tx-pool-gossip 만 확인
        let _ = response.send(Ok(PooledTransactions::default()));
        return
    }
    ...
```

`can_propagate` 호출 지점은 `propagate_transactions` 하나뿐이며, 나머지 둘은 세션 등록/해제 훅이다.

> ⚠️ [reth CLI 레퍼런스](https://reth.rs/cli/reth/node/)는 `--tx-propagation-policy`의 accepted values를 `All` 하나만 표시한다. **문서가 불완전한 것**이고 소스의 `FromStr`은 `all`/`trusted`/`none`을 대소문자 무관하게 받는다.

### ⚠️ `policy trusted` + `mode sqrt` 조합은 최악이 될 수 있다

`√n`의 `n`은 trusted 피어 수가 아니라 **전체 연결 피어 수**이고, 필터에 걸린 피어도 **순번을 소모한다**(`continue`가 `peer_idx` 할당 이후).

피어 10개(시퀀서 3대 trusted + 외부 7대)인 경우:

```
max_num_full = round(√10) = 3  → idx 0~3 이 원본 대상

idx 0~3  외부노드 → policy에 걸려 skip   (원본 슬롯 4개 전부 낭비)
idx 4    시퀀서   → 4 > 3 → 해시만  ⚠️
idx 6, 8 시퀀서   → 해시만          ⚠️
```

**시퀀서 3대가 전부 알림만 받는다.** → `policy trusted`를 쓰더라도 `mode all`을 반드시 병행한다.

### 노드 역할별 권장 설정

원본을 직접 받는 쪽(push)이 시퀀서에게 유리하다. 시퀀서는 2초 하드 데드라인을 가진 지연 민감 노드이며, pull의 장점(대역폭 절감·백프레셔·무단 수신 차단)은 전부 공개 메인넷용이기 때문이다.

| 노드 | 권장 | 이유 |
|---|---|---|
| **Ingress** | `--tx-propagation-mode all` | 1홉에서 시퀀서 전원에게 원본 push → `√n` 확률 0% |
| **시퀀서** | `--tx-propagation-mode max:0` | Ingress가 `all`이면 시퀀서 간 중계는 전부 중복. 원본 아웃바운드를 1개로 줄이되 **알림은 계속 나가 안전망 유지** |
| 둘 다 | `--tx-propagation-policy trusted` + `--trusted-peers` | 보안 |

⚠️ `policy trusted`는 `--trusted-peers` 등록이 전제다. 미등록 상태로 켜면 전파가 통째로 멈추며(`none`과 동일 효과) **로그 없이 조용히 실패한다.**

⚠️ `mode max:0`은 off-by-one 때문에 **0개가 아니라 1개**에게 원본을 보낸다. `max:0`이 파싱되는지는 미검증이며(`--help`로 확인), 거부되면 `max:1`(원본 2개)로 대체한다.

`policy none`으로 시퀀서 전파를 완전히 끄면 중복은 사라지지만 **중계 안전망도 사라져** Ingress의 `mode all` 설정에 정상 동작이 결합된다. 설정 드리프트 시 조용히 깨지므로 `max:0`이 낫다.

### 측정 지표 (op-reth)

op-geth에는 "이 트랜잭션이 알림으로 왔다"는 지표가 없지만(`eth/fetcher/tx_fetcher.go`에 메트릭이 하나도 없어 `p2p/ingress/eth/69/0x08/packets` 등으로 우회해야 함), **reth에는 직접 있다.**

| 지표 (scope `network`) | 타입 | 의미 |
|---|---|---|
| **`fetched_transactions`** | Counter | **알림으로 와서 가지러 가 받아온 tx 수** ← 핵심 지표 |
| `propagated_transactions` | Counter | 내가 남에게 알린 tx 수. ⚠️ **원본+알림 합산**이라 분할 비율 산출 불가 |
| `inflight_transaction_requests` | **Gauge** | 지금 나가 있는 `GetPooledTransactions` 수 (누적 아님) |
| **`hashes_pending_fetch`** | Gauge | idle 피어를 못 찾아 **대기 중인 해시 수** ← reth의 실제 지연 원인 |
| `occurrences_hashes_already_in_pool` | Counter | 알림이 왔는데 이미 갖고 있어 버린 횟수 (**정상·건강 신호**) |
| `occurrences_transactions_already_in_pool` | Counter | 원본이 중복으로 온 횟수 (대역폭·RLP 디코딩 낭비량) |
| `unsolicited_transactions` | Counter | 요청 안 한 tx가 응답에 섞여 옴 |
| `pool_import_prepare_duration` | Histogram | "mostly sender recovery" — ecrecover 비용 |
| `skipped_transactions_pending_pool_imports_at_capacity` | Counter | 풀 import 포화로 **버려진 tx** (조용한 유실 알람 대상) |

증가 지점:

```rust
// fetcher.rs — on_resolved_get_pooled_transactions_request_fut
self.metrics.fetched_transactions.increment(fetched.len() as u64);

// fetcher.rs — update_metrics
metrics.inflight_transaction_requests.set(self.inflight_requests.len() as f64);
metrics.hashes_pending_fetch.set(hashes_pending_fetch);
```

⚠️ `fetched_transactions`는 **응답 도착 시점**에 증가한다. 요청이 타임아웃되거나 피어가 끊기면 올라가지 않으므로 알림 수신 횟수를 과소 집계할 수 있다.

### 측정 절차

**설계 원칙:** op-geth는 sender 주소별로 운명이 갈려 "서로 다른 주소 100개"가 필요하지만, **reth는 피어 집합이 고정인 한 모든 트랜잭션이 같은 경로를 탄다.** 한 주소에서 연속 nonce 20~50개면 충분하다. 반대로 이 실험으로 0.39%라는 **비율은 측정할 수 없다**(배치를 재추첨하려면 수십 번 재시작해야 함). 목적을 "지금 배치가 좋은 상태인가, 나쁠 때 비용이 얼마인가"로 잡는다.

```bash
# seq-1
--metrics 0.0.0.0:9001
curl -s http://seq1:9001/metrics | grep -iE 'fetched_transactions|hashes_pending_fetch|inflight_transaction'
```

타이밍은 측정 머신 한 대에서 두 노드를 동시에 구독해 시계 오차를 없앤다.

```javascript
const ing = new ethers.WebSocketProvider("ws://ingress1:8546");
const seq = new ethers.WebSocketProvider("ws://seq1:8546");
ing.on("pending", h => { /* t_ing 기록 */ });
seq.on("pending", h => { /* t_seq 기록 */ });
// propagation delay = t_seq − t_ing
```

⚠️ `newPendingTransactions`는 **pending 승격 시점**에 발화하므로 nonce 갭이 있으면 결과가 오염된다. 갭 없는 연속 nonce를 쓴다.

| 관측 | 해석 |
|---|---|
| `Δfetched ≈ 0`, 지연 ~1~5ms | ✅ 정상. 원본을 직접 받는 배치 |
| `Δfetched ≈ 보낸 수`, `hashes_pending_fetch ≈ 0`, 지연 ~3~10ms | ⚠️ 알림 경로지만 비용 미미 (reth에 대기가 없다는 판단이 실측 확인됨) |
| `Δfetched ≈ 보낸 수`, `hashes_pending_fetch > 0` | ❌ 버퍼링 중 — 진짜 지연. `mode all` 필요 |
| 지연이 **수 초**, 계단식 | ❌ `√n`이 아니라 [nonce 갭](txpool-nonce-gap-propagation-stall.md) |

⚠️ 측정은 **재시작 없이 한 세션 안에서** 끝내야 한다. 재시작하면 배치가 재추첨된다.

## 관련 페이지

- [OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)](op-stack-tx-ingress-propagation.md) — 본 페이지의 규칙이 적용되는 **상위 구조**. 어떤 경로로 트랜잭션이 흐르는지, Ingress가 무엇을 덜어주는지를 다룬다.
- [txpool nonce 갭으로 인한 전파 정지](txpool-nonce-gap-propagation-stall.md) — 본 페이지의 `√n` 지연(ms 단위)보다 **1000배 큰** 지연 원인. 측정 시 두 현상을 구분해야 한다.
- [op-reth --max-outbound-peers & devp2p 피어 슬롯 제어](op-reth-max-outbound-peers.md) — 본 페이지의 `√n`에 들어가는 **피어 수**를 결정하는 설정. 피어가 늘수록 원본 비율이 떨어지므로 두 페이지는 같은 변수를 반대편에서 본다.
- [op-node P2P Peering & Chain Isolation](op-node-p2p-peering.md) — 본 페이지는 **EL(devp2p) 트랜잭션** 전파, 그 페이지는 **CL(libp2p) 블록** 전파. 별개 네트워크다.
- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](op-stack-block-production.md) — 500ms 지연이 왜 치명적인지의 기준(블록타임 2초)을 제공한다.
- [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한](reth-txpool-capacity-slot-limits.md) — 전파에 성공해도 풀 한도에 걸리면 유실된다.

## 출처

**reth `v2.3.0`** (op-reth pin — `resource/optimism/rust/Cargo.toml`)
- `crates/net/network/src/transactions/mod.rs` — `propagate_transactions`(`full_peer_count`, `peer_idx > max_num_full`, policy 체크 위치), `on_new_pooled_transaction_hashes`, `on_get_pooled_transactions`
- `crates/net/network/src/transactions/config.rs` — `TransactionPropagationMode`, `TransactionPropagationKind`, `can_propagate`
- `crates/net/network/src/transactions/fetcher.rs` — 알림 → **즉시 요청**(대기 없음), `fetched_transactions`·`inflight_transaction_requests`·`hashes_pending_fetch` 증가 지점
- `crates/net/network/src/transactions/constants.rs` — 도착 대기 상수 **부재**
- `crates/net/network/src/metrics.rs` — `TransactionsManagerMetrics`, `TransactionFetcherMetrics`
- `crates/node/core/src/args/network.rs` — `--tx-propagation-mode`, `--tx-propagation-policy`

**op-geth `v1.101702.3-rc.4`** (대조군)
- `eth/handler.go:473-527, 692-745` — `BroadcastTransactions`, `choosePeers`
- `eth/handler.go:169, 433, 529-540` — `txBroadcastKey` 난수 생성, 원격 tx 재브로드캐스트
- `eth/fetcher/tx_fetcher.go:65-71` — `txArriveTimeout = 500ms`
- `eth/protocols/eth/protocol.go:53-67` — 메시지 코드 (0x02/0x08/0x09/0x0a)
- `p2p/peer.go:398-402` — 메시지 코드별 ingress 메트릭

**표준 문서**
- [devp2p — Ethereum Wire Protocol (ETH)](https://github.com/ethereum/devp2p/blob/master/caps/eth.md) — Transaction Exchange 절 (권고, 숫자 없음) / Block Propagation 절 (`√n`)
- [EIP-2464: eth/65 transaction announcements and retrievals](https://eips.ethereum.org/EIPS/eip-2464) — 제곱근 복잡도를 **설계 목표**로 서술
- [reth CLI 레퍼런스 — reth node](https://reth.rs/cli/reth/node/) (※ policy 값 목록 불완전)

## 미검증 / 주의

- reth의 **대기 상수 부재**와 **off-by-one**은 소스 조회로 확인했으나 실기기 검증은 하지 않았다. 위 측정 절차가 곧 그 검증이다.
- `--tx-propagation-mode` / `--tx-propagation-policy`가 **op-reth CLI에 실제로 노출되는지** `--help`로 확인이 필요하다(reth `NetworkArgs` 상속이라 노출될 것으로 보이나 미검증).
- reth 메트릭의 **정확한 Prometheus 이름**(접두사·구분자)은 확인하지 못했다.
- reth의 HashMap 순회 순서가 **피어 집합 변경 없이도** 재정렬될 여지(리해싱 등)는 확인하지 못했다. "피어 집합이 고정이면 순서도 고정"은 표준 HashMap 동작에서 유도한 것이다.
- **0.39% 확률은 코드에서 유도한 모델**이며 실측하지 않았다. `full_peer_count`가 균등한 부분집합을 만든다는 가정에 의존한다.
