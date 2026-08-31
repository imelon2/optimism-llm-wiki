# L1 Receipts & Derivation Stalls

> 22 nodes · cohesion 0.10

## Key Concepts

- **context deadline exceeded** (4 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **FetchReceipts** (4 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **Single event loop blocking** (4 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **callTimeout** (4 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **Exponential backoff recovery window** (3 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **l1.rpckind mismatch slow fetch path** (3 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **L1Traversal.AdvanceL1Block** (3 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **Lock ratio 91%** (3 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **retry.Do blocking backoff** (3 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **CachingReceiptsProvider** (2 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **callTimeout** (2 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **UpdateSystemConfigWithL1Receipts** (2 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **sync.FindL2Heads** (2 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **batchCallTimeout** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **DerivationPipeline.Step** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **event.NewGlobalSynchronous** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **resetting back RPC preferences, please review RPC provider kind setting** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **retry.Exponential** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **SystemConfig ConfigUpdate event** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **batchCallTimeout** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **Reset overlap 65s per block** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`
- **ResetEngineRequestEvent** (1 connections) — `runbooks/op-node-find-l1-origin-stall.md`

## Relationships

- [Sequencer L1 Origin Stalls](Sequencer_L1_Origin_Stalls.md) (2 shared connections)
- [discv5 Bootnode Discovery](discv5_Bootnode_Discovery.md) (1 shared connections)
- [Engine API & Payload Building](Engine_API_%26_Payload_Building.md) (1 shared connections)

## Source Files

- `runbooks/op-node-fetch-receipts-context-deadline.md`
- `runbooks/op-node-find-l1-origin-stall.md`

## Audit Trail

- EXTRACTED: 41 (85%)
- INFERRED: 7 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*