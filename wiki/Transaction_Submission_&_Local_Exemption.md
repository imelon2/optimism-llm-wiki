# Transaction Submission & Local Exemption

> 44 nodes · cohesion 0.08

## Key Concepts

- **OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)** (21 connections) — `concepts/op-stack-tx-ingress-propagation.md`
- **reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")** (18 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **op-reth --txpool.nolocals & Local Transaction Exemption** (14 connections) — `concepts/op-reth-txpool-nolocals.md`
- **op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단** (12 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **Wiki Index** (9 connections) — `index.md`
- **Wiki Log** (9 connections) — `log.md`
- **PoolErrorKind::DiscardedOnInsert (원인 A — 용량 초과)** (4 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **max_account_slots (기본 16, in-flight 깊이 제한)** (4 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **RpcPoolError::TxPoolOverflow** (4 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **PoolErrorKind::SpammerExceededCapacity (원인 B — 계정 슬롯 초과)** (4 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **서브풀 4종 용량 한도 (10,000 tx / 20MB)** (4 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **eth_sendRawTransaction → TransactionOrigin::External** (3 connections) — `concepts/op-reth-txpool-nolocals.md`
- **서명 검증(ecrecover) 위임 불가** (3 connections) — `concepts/op-stack-tx-ingress-propagation.md`
- **길 B — Ingress + devp2p gossip** (3 connections) — `concepts/op-stack-tx-ingress-propagation.md`
- **Ingress 구조의 조용한 장애 3종** (3 connections) — `concepts/op-stack-tx-ingress-propagation.md`
- **Tx Ingress Node 아키텍처** (3 connections) — `concepts/op-stack-tx-ingress-propagation.md`
- **ensure_valid() 계정 슬롯 체크** (3 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **-32003 "txpool is full"** (3 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **--tx-propagation-policy (all/trusted/none)** (3 connections) — `concepts/tx-propagation-sqrt-broadcast.md`
- **진단 절차 (txpool_status / txpool_contentFrom / 원본 에러 문자열)** (3 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **forward_raw_transaction / forward_raw_transaction_conditional** (3 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **재시도 없음 · 로컬 풀 미보관 (조기 반환)** (3 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **eth_sendRawTransaction** (2 connections) — `concepts/op-geth-personal-namespace-removal.md`
- **local 트랜잭션 면제 3종 (slot/price/eviction)** (2 connections) — `concepts/op-reth-txpool-nolocals.md`
- **LocalTransactionConfig** (2 connections) — `concepts/op-reth-txpool-nolocals.md`
- *... and 19 more nodes in this community*

## Relationships

- [Sqrt Broadcast & Tx Gossip](Sqrt_Broadcast_%26_Tx_Gossip.md) (15 shared connections)
- [P2P Peering & Chain Isolation](P2P_Peering_%26_Chain_Isolation.md) (8 shared connections)
- [Sequencer Block Production Cycle](Sequencer_Block_Production_Cycle.md) (4 shared connections)

## Source Files

- `concepts/op-geth-personal-namespace-removal.md`
- `concepts/op-reth-txpool-nolocals.md`
- `concepts/op-stack-tx-ingress-propagation.md`
- `concepts/reth-txpool-capacity-slot-limits.md`
- `concepts/tx-propagation-sqrt-broadcast.md`
- `index.md`
- `log.md`
- `runbooks/op-reth-sequencer-forward-txpool-full.md`

## Audit Trail

- EXTRACTED: 167 (94%)
- INFERRED: 10 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*