# P2P Peering & Chain Isolation

> 28 nodes · cohesion 0.13

## Key Concepts

- **op-node P2P Peering & Chain Isolation** (17 connections) — `concepts/op-node-p2p-peering.md`
- **op-reth --max-outbound-peers & devp2p 피어 슬롯 제어** (17 connections) — `concepts/op-reth-max-outbound-peers.md`
- **--max-outbound-peers** (6 connections) — `concepts/op-reth-max-outbound-peers.md`
- **libp2p(gossipsub) 블록 전파 네트워크** (5 connections) — `concepts/op-node-p2p-peering.md`
- **has_out_capacity() AND 게이트** (5 connections) — `concepts/op-reth-max-outbound-peers.md`
- **--trusted-peers / --trusted-only** (5 connections) — `concepts/op-reth-max-outbound-peers.md`
- **체인별 gossip 토픽 /optimism/<L2ChainID>/N/blocks** (4 connections) — `concepts/op-node-p2p-peering.md`
- **discv5 discovery (ListenV5)** (4 connections) — `concepts/op-node-p2p-peering.md`
- **devp2p(RLPx) EL 피어 네트워크** (4 connections) — `concepts/op-reth-max-outbound-peers.md`
- **BlockingConnectionGater** (3 connections) — `concepts/op-node-p2p-peering.md`
- **FilterEnodes()** (3 connections) — `concepts/op-node-p2p-peering.md`
- **InterceptAccept / InterceptSecured 게이팅 한계** (3 connections) — `concepts/op-node-p2p-peering.md`
- **--p2p.no-discovery + --p2p.static (정적 신뢰 피어)** (3 connections) — `concepts/op-node-p2p-peering.md`
- **피어 스코어링 & 밴 (--p2p.ban.peers)** (3 connections) — `concepts/op-node-p2p-peering.md`
- **best_unconnected() 우선순위** (3 connections) — `concepts/op-reth-max-outbound-peers.md`
- **ConnectionsConfig::default()** (3 connections) — `concepts/op-reth-max-outbound-peers.md`
- **fill_outbound_slots()** (3 connections) — `concepts/op-reth-max-outbound-peers.md`
- **max_concurrent_outbound_dials (CLI 플래그 없음)** (3 connections) — `concepts/op-reth-max-outbound-peers.md`
- **--max-peers (2:1 in:out 분배)** (3 connections) — `concepts/op-reth-max-outbound-peers.md`
- **try_rotate_peer() / UselessPeer 로테이션** (3 connections) — `concepts/op-reth-max-outbound-peers.md`
- **P2P 두 개 — libp2p(블록) vs devp2p(트랜잭션)** (3 connections) — `concepts/op-stack-tx-ingress-propagation.md`
- **방화벽 P2P 포트(9222) inbound 차단** (2 connections) — `concepts/op-node-p2p-peering.md`
- **opp2p_blockPeer / blockAddr / blockSubnet RPC** (2 connections) — `concepts/op-node-p2p-peering.md`
- **ENR opstack 키 + chainID 필터** (2 connections) — `concepts/op-node-p2p-peering.md`
- **--p2p.netrestrict** (2 connections) — `concepts/op-node-p2p-peering.md`
- *... and 3 more nodes in this community*

## Relationships

- [Transaction Submission & Local Exemption](Transaction_Submission_%26_Local_Exemption.md) (8 shared connections)
- [Sqrt Broadcast & Tx Gossip](Sqrt_Broadcast_%26_Tx_Gossip.md) (7 shared connections)
- [Sync Modes & ReqResp Deprecation](Sync_Modes_%26_ReqResp_Deprecation.md) (1 shared connections)
- [Sequencer Block Production Cycle](Sequencer_Block_Production_Cycle.md) (1 shared connections)

## Source Files

- `concepts/op-node-p2p-peering.md`
- `concepts/op-reth-max-outbound-peers.md`
- `concepts/op-stack-block-production.md`
- `concepts/op-stack-tx-ingress-propagation.md`

## Audit Trail

- EXTRACTED: 105 (90%)
- INFERRED: 12 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*