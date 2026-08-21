# txpool local 면제·수수료 정책

> 18 nodes · cohesion 0.12

## Key Concepts

- **LocalTransactionConfig::is_local (nolocals가 locals보다 우선)** (4 connections) — `concepts/op-reth-txpool-nolocals.md`
- **local 트랜잭션 면제 3종 (slot / price / eviction)** (4 connections) — `concepts/op-reth-txpool-nolocals.md`
- **effectiveGasPrice = min(maxFeePerGas, baseFee + maxPriorityFeePerGas)** (4 connections) — `concepts/op-stack-eip1559-fees.md`
- **max_account_slots (기본 16, in-flight 미래 nonce 깊이 제한)** (4 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **RpcPoolError::TxPoolOverflow 매핑 (두 PoolErrorKind → -32003)** (4 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **PoolErrorKind::SpammerExceededCapacity (계정 슬롯 초과)** (4 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **LocalTransactionConfig (no_exemptions / local_addresses / propagate)** (3 connections) — `concepts/op-reth-txpool-nolocals.md`
- **--min-suggested-priority-fee (RPC 추천 하한, mempool 강제 아님)** (3 connections) — `concepts/op-stack-eip1559-fees.md`
- **eth_sendRawTransaction은 TransactionOrigin::External (local 아님)** (2 connections) — `concepts/op-reth-txpool-nolocals.md`
- **Fee Vault 3종 (BaseFeeVault / SequencerFeeVault / L1FeeVault)** (2 connections) — `concepts/op-stack-eip1559-fees.md`
- **서브풀 4종 용량 한도 (기본 10,000 tx / 20MB, PoolConfig::is_exceeded)** (2 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **eviction 면제는 pending 서브풀에서만 — parked는 보호 없음** (1 connections) — `concepts/op-reth-txpool-nolocals.md`
- **--txpool.locals (주소 기반 local 지정)** (1 connections) — `concepts/op-reth-txpool-nolocals.md`
- **OP의 base fee는 소각되지 않고 BaseFeeVault로 적립** (1 connections) — `concepts/op-stack-eip1559-fees.md`
- **Holocene 이후 체인별 EIP-1559 파라미터 (SystemConfig.setEIP1559Params / extraData)** (1 connections) — `concepts/op-stack-eip1559-fees.md`
- **-32003 vs -32000 클라이언트 지문 (reth 계열 특정)** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **geth AccountSlots(보장치) vs reth(거부 임계값) 의미 역전** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **reth/op-reth -32003 "txpool is full" (두 원인의 붕괴)** (1 connections) — `concepts/reth-txpool-capacity-slot-limits.md`

## Relationships

- [Wiki 인덱스 허브](Wiki_%EC%9D%B8%EB%8D%B1%EC%8A%A4_%ED%97%88%EB%B8%8C.md) (5 shared connections)

## Source Files

- `concepts/op-reth-txpool-nolocals.md`
- `concepts/op-stack-eip1559-fees.md`
- `concepts/reth-txpool-capacity-slot-limits.md`

## Audit Trail

- EXTRACTED: 41 (95%)
- INFERRED: 2 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*