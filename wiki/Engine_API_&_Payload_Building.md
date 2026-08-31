# Engine API & Payload Building

> 16 nodes · cohesion 0.13

## Key Concepts

- **Changeset cache MISS, falling back to DB-based computation** (4 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **New payload job created** (4 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **unsafe head stall** (3 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **engine_forkchoiceUpdatedV3** (3 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **ExecEngine interface** (3 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **FinalizedBlockHash evict threshold** (2 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **ForkchoiceState HeadBlockHash** (2 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **onBuildStart** (2 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **op-node stall as burst amplifier** (2 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **startPayload** (2 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **state_by_block_hash** (2 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **op-conductor health monitor failover** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **engine_getPayloadV3** (1 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **engine_newPayloadV3** (1 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **Loki correlation query** (1 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **promoteFinalized** (1 connections) — `runbooks/op-reth-changeset-cache-miss.md`

## Relationships

- [L1 Receipts & Derivation Stalls](L1_Receipts_%26_Derivation_Stalls.md) (1 shared connections)
- [Sequencer L1 Origin Stalls](Sequencer_L1_Origin_Stalls.md) (1 shared connections)

## Source Files

- `runbooks/op-node-find-l1-origin-stall.md`
- `runbooks/op-reth-changeset-cache-miss.md`

## Audit Trail

- EXTRACTED: 32 (94%)
- INFERRED: 2 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*