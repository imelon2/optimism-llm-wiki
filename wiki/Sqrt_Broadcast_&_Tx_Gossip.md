# Sqrt Broadcast & Tx Gossip

> 24 nodes · cohesion 0.14

## Key Concepts

- **트랜잭션 √n 브로드캐스트 규칙 (원본 전송 vs 해시 알림)** (22 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **txpool nonce 갭으로 인한 트랜잭션 전파 정지** (15 connections) — `concepts/txpool-nonce-gap-propagation-stall.md`
- **nonce 갭 전파 정지 메커니즘** (9 connections) — `concepts/txpool-nonce-gap-propagation-stall.md`
- **√n 브로드캐스트 규칙** (7 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **queued 트랜잭션은 gossip되지 않는다** (5 connections) — `concepts/txpool-nonce-gap-propagation-stall.md`
- **propagate_transactions (op-reth)** (4 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **해결책 ② Ingress 노드 간 EL 피어링** (4 connections) — `concepts/txpool-nonce-gap-propagation-stall.md`
- **buffer_hashes() — reth의 실제 지연 지점** (3 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **fetched_transactions 메트릭** (3 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **policy trusted + mode sqrt 조합 함정** (3 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **pool.retain_unknown() — 이미 보유한 알림 폐기** (3 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **eviction 면제의 서브풀 비대칭 (pending만 보호)** (2 connections) — `concepts/op-reth-txpool-nolocals.md`
- **choosePeers (op-geth, siphash + txSender)** (2 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **devp2p caps/eth.md — Transaction Exchange** (2 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **EIP-2464 (eth/65 announcements and retrievals)** (2 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **hashes_pending_fetch 메트릭** (2 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **off-by-one — peer_idx > max_num_full** (2 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **txArriveTimeout 500ms (op-geth 의도적 대기)** (2 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **bad_imports 메트릭 (갭은 잡히지 않음)** (2 connections) — `concepts/txpool-nonce-gap-propagation-stall.md`
- **FirstNonceGap: nil (풀의 갭 허용)** (2 connections) — `concepts/txpool-nonce-gap-propagation-stall.md`
- **pool.pending_transactions_listener()** (2 connections) — `concepts/txpool-nonce-gap-propagation-stall.md`
- **해결책 ① 로드밸런서 sticky session (source IP)** (2 connections) — `concepts/txpool-nonce-gap-propagation-stall.md`
- **--txpool.lifetime** (2 connections) — `concepts/txpool-nonce-gap-propagation-stall.md`
- **--tx-propagation-mode (sqrt/all/max:N)** (1 connections) — `concepts/tx-propagation-sqrt-broadcast.md`

## Relationships

- [Transaction Submission & Local Exemption](Transaction_Submission_%26_Local_Exemption.md) (15 shared connections)
- [P2P Peering & Chain Isolation](P2P_Peering_%26_Chain_Isolation.md) (7 shared connections)
- [Sequencer Block Production Cycle](Sequencer_Block_Production_Cycle.md) (3 shared connections)

## Source Files

- `concepts/op-reth-txpool-nolocals.md`
- `concepts/tx-propagation-sqrt-broadcast.md`
- `concepts/txpool-nonce-gap-propagation-stall.md`

## Audit Trail

- EXTRACTED: 91 (88%)
- INFERRED: 12 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*