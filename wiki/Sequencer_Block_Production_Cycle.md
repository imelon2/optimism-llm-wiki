# Sequencer Block Production Cycle

> 11 nodes · cohesion 0.33

## Key Concepts

- **OP Stack 시퀀서 블록 생성 과정 (2초 사이클)** (16 connections) — `concepts/op-stack-block-production.md`
- **9단계 2초 블록 생성 사이클** (8 connections) — `concepts/op-stack-block-production.md`
- **FindL1Origin (L1 origin 선택)** (4 connections) — `concepts/op-stack-block-production.md`
- **Engine API 호출 순서 (forkchoiceUpdatedV3 → getPayloadV3 → newPayloadV3)** (3 connections) — `concepts/op-stack-block-production.md`
- **L1 origin 500ms best-effort 선캐싱** (3 connections) — `concepts/op-stack-block-production.md`
- **고정 블록 간격 (타임스탬프 산술 유도)** (2 connections) — `concepts/op-stack-block-production.md`
- **handleInvalid() 재스케줄** (2 connections) — `concepts/op-stack-block-production.md`
- **max sequencer drift 1800초** (2 connections) — `concepts/op-stack-block-production.md`
- **NoTxPool / deposit-only 블록** (2 connections) — `concepts/op-stack-block-production.md`
- **sealingDuration 50ms** (2 connections) — `concepts/op-stack-block-production.md`
- **드라이버 단일 이벤트 루프 직렬 실행** (2 connections) — `concepts/op-stack-block-production.md`

## Relationships

- [Transaction Submission & Local Exemption](Transaction_Submission_%26_Local_Exemption.md) (4 shared connections)
- [Sqrt Broadcast & Tx Gossip](Sqrt_Broadcast_%26_Tx_Gossip.md) (3 shared connections)
- [P2P Peering & Chain Isolation](P2P_Peering_%26_Chain_Isolation.md) (1 shared connections)
- [personal Namespace Removal](personal_Namespace_Removal.md) (1 shared connections)
- [L1 Confirmation Depth](L1_Confirmation_Depth.md) (1 shared connections)

## Source Files

- `concepts/op-stack-block-production.md`

## Audit Trail

- EXTRACTED: 46 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*