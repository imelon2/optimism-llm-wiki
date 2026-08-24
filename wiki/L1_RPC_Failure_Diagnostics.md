# L1 RPC Failure Diagnostics

> 26 nodes · cohesion 0.08

## Key Concepts

- **failed adding boot node err=Timeout** (6 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **context deadline exceeded** (4 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **FetchReceipts** (4 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **failed to fetch receipts for L1 sysCfg update** (3 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **l1.rpckind mismatch slow fetch path** (3 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **L1Traversal.AdvanceL1Block** (3 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **NewTemporaryError** (3 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **bootstrap** (3 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **discv5.request_enr** (3 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **CachingReceiptsProvider** (2 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **Sequencer.onEngineTemporaryError** (2 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **UpdateSystemConfigWithL1Receipts** (2 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **discport port mismatch** (2 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **discv5.add_enr** (2 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **batchCallTimeout** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **connection reset by peer** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **DerivationPipeline.Step** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **Engine failed temporarily, backing off sequencer** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **resetting back RPC preferences, please review RPC provider kind setting** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **SystemConfig ConfigUpdate event** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **DEFAULT_DISCOVERY_V5_PORT** (1 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **EL CL bootnode confusion** (1 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **enode** (1 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **ENR** (1 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **kona bootstrap_peers** (1 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- *... and 1 more nodes in this community*

## Relationships

- [Sequencer Stall Timeline](Sequencer_Stall_Timeline.md) (2 shared connections)
- [Wiki Catalogue and Runbooks](Wiki_Catalogue_and_Runbooks.md) (2 shared connections)

## Source Files

- `runbooks/op-node-fetch-receipts-context-deadline.md`
- `runbooks/op-reth-discv5-bootnode-timeout.md`

## Audit Trail

- EXTRACTED: 50 (93%)
- INFERRED: 4 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*