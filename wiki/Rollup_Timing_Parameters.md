# Rollup Timing Parameters

> 22 nodes · cohesion 0.11

## Key Concepts

- **rollup.Config.BlockTime** (8 connections) — `concepts/op-stack-l2-block-time.md`
- **rollup.Config.MaxSequencerDrift** (3 connections) — `concepts/op-node-l1-confs-conf-depth.md`
- **MaxSequencerDrift (1800초 프로토콜 상수)** (3 connections) — `concepts/op-stack-block-production.md`
- **타임스탬프 산술 유도** (3 connections) — `concepts/op-stack-block-production.md`
- **eip1559Denominator** (3 connections) — `concepts/op-stack-eip1559-fees.md`
- **setEIP1559Params** (3 connections) — `concepts/op-stack-eip1559-fees.md`
- **SystemConfig** (3 connections) — `concepts/op-stack-eip1559-fees.md`
- **L2BlockTime (deploy config)** (3 connections) — `concepts/op-stack-l2-block-time.md`
- **오프체인 전용 파라미터(max_sequencer_drift/seq_window_size/channel_timeout)** (3 connections) — `concepts/op-stack-l2-block-time.md`
- **SystemConfig 온체인 값** (3 connections) — `concepts/op-stack-l2-block-time.md`
- **타임스탬프 산술 유도** (3 connections) — `concepts/op-stack-l2-block-time.md`
- **eip1559Elasticity** (2 connections) — `concepts/op-stack-eip1559-fees.md`
- **Holocene/Jovian extraData 인코딩** (2 connections) — `concepts/op-stack-eip1559-fees.md`
- **attrs.NoTxPool** (1 connections) — `concepts/op-stack-block-production.md`
- **제네시스 EIP-1559 기본 상수(elasticity 10 / denom 50·250)** (1 connections) — `concepts/op-stack-eip1559-fees.md`
- **minBaseFee / setMinBaseFee** (1 connections) — `concepts/op-stack-eip1559-fees.md`
- **ErrBlockTimeZero** (1 connections) — `concepts/op-stack-l2-block-time.md`
- **배포 후 변경은 하드포크** (1 connections) — `concepts/op-stack-l2-block-time.md`
- **L1BlockTime ≥ L2BlockTime 제약** (1 connections) — `concepts/op-stack-l2-block-time.md`
- **op-deployer L2BlockTime 기본값 2** (1 connections) — `concepts/op-stack-l2-block-time.md`
- **optimism_rollupConfig RPC** (1 connections) — `concepts/op-stack-l2-block-time.md`
- **superchain registry BlockTime** (1 connections) — `concepts/op-stack-l2-block-time.md`

## Relationships

- [L1 Confirmation Depth](L1_Confirmation_Depth.md) (1 shared connections)

## Source Files

- `concepts/op-node-l1-confs-conf-depth.md`
- `concepts/op-stack-block-production.md`
- `concepts/op-stack-eip1559-fees.md`
- `concepts/op-stack-l2-block-time.md`

## Audit Trail

- EXTRACTED: 49 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*