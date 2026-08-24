# P2P Peering and Chain Isolation

> 19 nodes · cohesion 0.11

## Key Concepts

- **ReqResp P2P sync** (5 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **discv5 discovery** (4 connections) — `concepts/op-node-p2p-peering.md`
- **FilterEnodes** (4 connections) — `concepts/op-node-p2p-peering.md`
- **BlockingConnectionGater** (3 connections) — `concepts/op-node-p2p-peering.md`
- **체인별 gossip 토픽 /optimism/<L2ChainID>/*/blocks** (3 connections) — `concepts/op-node-p2p-peering.md`
- **inbound은 chainID로 게이팅되지 않는다** (3 connections) — `concepts/op-node-p2p-peering.md`
- **InterceptAccept / InterceptSecured** (2 connections) — `concepts/op-node-p2p-peering.md`
- **OpStackENRData (opstack ENR 키)** (2 connections) — `concepts/op-node-p2p-peering.md`
- **--p2p.no-discovery** (2 connections) — `concepts/op-node-p2p-peering.md`
- **/opstack/req/payload_by_number/<chainID>/0** (2 connections) — `concepts/op-node-p2p-peering.md`
- **devp2p(RLPx) EL 피어 네트워크** (2 connections) — `concepts/op-reth-max-outbound-peers.md`
- **방화벽 inbound 차단 (TCP/UDP 9222)** (1 connections) — `concepts/op-node-p2p-peering.md`
- **opp2p_blockPeer / blockAddr / blockSubnet** (1 connections) — `concepts/op-node-p2p-peering.md`
- **--p2p.ban.peers** (1 connections) — `concepts/op-node-p2p-peering.md`
- **--p2p.netrestrict** (1 connections) — `concepts/op-node-p2p-peering.md`
- **--p2p.static** (1 connections) — `concepts/op-node-p2p-peering.md`
- **--p2p.sync.onlyReqToStatic (deprecated no-op)** (1 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **ReqResp 폐기 이유(무서명 역순 인증·메모리 제약·복잡도 상한)** (1 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **--syncmode.req-resp (deprecated no-op)** (1 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`

## Relationships

- [CLSync vs ELSync Modes](CLSync_vs_ELSync_Modes.md) (1 shared connections)
- [devp2p Peer Slot Control](devp2p_Peer_Slot_Control.md) (1 shared connections)

## Source Files

- `concepts/op-node-p2p-peering.md`
- `concepts/op-node-syncmode-reqresp-deprecation.md`
- `concepts/op-reth-max-outbound-peers.md`

## Audit Trail

- EXTRACTED: 38 (95%)
- INFERRED: 2 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*