# Sequencer Stall Timeline

> 23 nodes · cohesion 0.09

## Key Concepts

- **FindL1Origin** (7 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **Single event loop blocking** (4 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **callTimeout** (4 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **Exponential backoff recovery window** (3 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **Lock ratio 91%** (3 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **retry.Do blocking backoff** (3 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **unsafe head stall** (3 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **callTimeout** (2 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **ErrNextL1OriginRequired** (2 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **Missing deadline in FindL1Origin** (2 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **Origin pre-caching 500ms** (2 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **PreparePayloadAttributes** (2 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **startBuildingBlock** (2 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **sync.FindL2Heads** (2 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **event.NewGlobalSynchronous** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **retry.Exponential** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **batchCallTimeout** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **Error finding next L1 Origin** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **goroutine dump diagnosis** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **op-conductor health monitor failover** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **Reset overlap 65s per block** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **ResetEngineRequestEvent** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **sequencer.l1-confs cache miss** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`

## Relationships

- [L1 RPC Failure Diagnostics](L1_RPC_Failure_Diagnostics.md) (2 shared connections)
- [Wiki Catalogue and Runbooks](Wiki_Catalogue_and_Runbooks.md) (1 shared connections)
- [Changeset Cache Miss Path](Changeset_Cache_Miss_Path.md) (1 shared connections)

## Source Files

- `runbooks/op-node-fetch-receipts-context-deadline.md`
- `runbooks/op-node-find-l1-origin-stall.md`

## Audit Trail

- EXTRACTED: 45 (90%)
- INFERRED: 5 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*