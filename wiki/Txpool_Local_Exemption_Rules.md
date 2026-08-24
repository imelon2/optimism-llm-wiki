# Txpool Local Exemption Rules

> 27 nodes · cohesion 0.09

## Key Concepts

- **--txpool.nolocals** (7 connections) — `concepts/op-reth-txpool-nolocals.md`
- **LocalTransactionConfig** (6 connections) — `concepts/op-reth-txpool-nolocals.md`
- **ensure_valid** (6 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **max_account_slots (기본 16)** (6 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **TransactionOrigin::External** (4 connections) — `concepts/op-reth-txpool-nolocals.md`
- **Eviction 면제** (3 connections) — `concepts/op-reth-txpool-nolocals.md`
- **is_local()** (3 connections) — `concepts/op-reth-txpool-nolocals.md`
- **Slot 면제** (3 connections) — `concepts/op-reth-txpool-nolocals.md`
- **eth_sendRawTransaction** (2 connections) — `concepts/op-geth-personal-namespace-removal.md`
- **no_exemptions** (2 connections) — `concepts/op-reth-txpool-nolocals.md`
- **ParkedPool truncate_pool (local 보호 없음)** (2 connections) — `concepts/op-reth-txpool-nolocals.md`
- **pending remove_locals truncate** (2 connections) — `concepts/op-reth-txpool-nolocals.md`
- **가격(price) 면제** (2 connections) — `concepts/op-reth-txpool-nolocals.md`
- **--txpool.locals** (2 connections) — `concepts/op-reth-txpool-nolocals.md`
- **go-ethereum AccountSlots / AccountQueue** (2 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **TransactionOrigin::External** (2 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **clef 외부 서명자** (1 connections) — `concepts/op-geth-personal-namespace-removal.md`
- **eth_sendRawTransaction** (1 connections) — `concepts/op-reth-txpool-nolocals.md`
- **max_account_slots (기본 16)** (1 connections) — `concepts/op-reth-txpool-nolocals.md`
- **sequencer에서만 실효적인 정책** (1 connections) — `concepts/op-reth-txpool-nolocals.md`
- **--txpool.no-local-transactions-propagation** (1 connections) — `concepts/op-reth-txpool-nolocals.md`
- **TxPoolArgs → pool_config()** (1 connections) — `concepts/op-reth-txpool-nolocals.md`
- **allow_local_spamming 테스트** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **max_account_slots는 in-flight 깊이 제한** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **reject_spammer 테스트** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- *... and 2 more nodes in this community*

## Relationships

- [Fee Pricing and Pool Eviction](Fee_Pricing_and_Pool_Eviction.md) (2 shared connections)
- [Observability and Profiling](Observability_and_Profiling.md) (1 shared connections)

## Source Files

- `concepts/op-geth-personal-namespace-removal.md`
- `concepts/op-reth-txpool-nolocals.md`
- `concepts/reth-txpool-capacity-slot-limits.md`

## Audit Trail

- EXTRACTED: 61 (94%)
- INFERRED: 4 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*