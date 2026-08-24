# Fee Pricing and Pool Eviction

> 19 nodes · cohesion 0.12

## Key Concepts

- **maxPriorityFeePerGas** (5 connections) — `concepts/op-stack-eip1559-fees.md`
- **discard_worst** (4 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **PoolErrorKind::DiscardedOnInsert** (4 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **effectiveGasPrice** (3 connections) — `concepts/op-stack-eip1559-fees.md`
- **--min-suggested-priority-fee** (3 connections) — `concepts/op-stack-eip1559-fees.md`
- **-32003 "txpool is full"** (3 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **RpcPoolError::TxPoolOverflow** (3 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **PoolErrorKind::SpammerExceededCapacity** (3 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **BaseFeeVault (0x4200...0019)** (2 connections) — `concepts/op-stack-eip1559-fees.md`
- **op_suggest_tip_cap** (2 connections) — `concepts/op-stack-eip1559-fees.md`
- **SubPoolLimit / PoolConfig::is_exceeded** (2 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **base fee 미소각·vault 적립 (OP 고유 차이)** (1 connections) — `concepts/op-stack-eip1559-fees.md`
- **maxFeePerGas** (1 connections) — `concepts/op-stack-eip1559-fees.md`
- **SequencerFeeVault (0x4200...0011)** (1 connections) — `concepts/op-stack-eip1559-fees.md`
- **go-ethereum -32000 errcodeDefault** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **-32003 + txpool is full = reth 계열 지문** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **서브풀 4종(pending/basefee/queued/blob)** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **ParkedPool truncate_pool** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **pending remove_locals truncate** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`

## Relationships

- [Txpool Local Exemption Rules](Txpool_Local_Exemption_Rules.md) (2 shared connections)

## Source Files

- `concepts/op-stack-eip1559-fees.md`
- `concepts/reth-txpool-capacity-slot-limits.md`

## Audit Trail

- EXTRACTED: 36 (86%)
- INFERRED: 6 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*