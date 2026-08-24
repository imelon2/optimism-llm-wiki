# devp2p Peer Slot Control

> 18 nodes · cohesion 0.11

## Key Concepts

- **--max-outbound-peers** (8 connections) — `concepts/op-reth-max-outbound-peers.md`
- **has_out_capacity** (4 connections) — `concepts/op-reth-max-outbound-peers.md`
- **best_unconnected** (3 connections) — `concepts/op-reth-max-outbound-peers.md`
- **max_concurrent_outbound_dials** (3 connections) — `concepts/op-reth-max-outbound-peers.md`
- **ConnectionsConfig::default()** (2 connections) — `concepts/op-reth-max-outbound-peers.md`
- **fill_outbound_slots** (2 connections) — `concepts/op-reth-max-outbound-peers.md`
- **--max-inbound-peers** (2 connections) — `concepts/op-reth-max-outbound-peers.md`
- **--max-peers** (2 connections) — `concepts/op-reth-max-outbound-peers.md`
- **try_rotate_peer** (2 connections) — `concepts/op-reth-max-outbound-peers.md`
- **inbound trusted 예외 경로(outbound엔 없음)** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **network_pending_outgoing_connections 메트릭** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **PeersConfig** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **reth.toml [peers.connection_info]** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **reth v2.3.0 pin** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **network_outbound too_many_peers 카운터** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **--trusted-only (trusted_nodes_only)** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **--trusted-peers** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **DisconnectReason::UselessPeer** (1 connections) — `concepts/op-reth-max-outbound-peers.md`

## Relationships

- [CLSync vs ELSync Modes](CLSync_vs_ELSync_Modes.md) (1 shared connections)
- [P2P Peering and Chain Isolation](P2P_Peering_and_Chain_Isolation.md) (1 shared connections)
- [Observability and Profiling](Observability_and_Profiling.md) (1 shared connections)

## Source Files

- `concepts/op-reth-max-outbound-peers.md`

## Audit Trail

- EXTRACTED: 35 (95%)
- INFERRED: 2 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*