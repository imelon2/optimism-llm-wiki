# L1 확인 깊이·inbound 차단

> 9 nodes · cohesion 0.22

## Key Concepts

- **confDepth 래퍼 (L1 head 근접 블록을 ethereum.NotFound으로 숨김)** (4 connections) — `concepts/op-node-l1-confs-conf-depth.md`
- **--sequencer.l1-confs (SequencerConfDepth, 기본 4)** (3 connections) — `concepts/op-node-l1-confs-conf-depth.md`
- **--verifier.l1-confs (VerifierConfDepth, 기본 0)** (3 connections) — `concepts/op-node-l1-confs-conf-depth.md`
- **BlockingConnectionGater (peerID/IP/subnet denylist)** (3 connections) — `concepts/op-node-p2p-peering.md`
- **inbound 연결은 chainID로 게이팅되지 않는다 (InterceptAccept/Secured 한계)** (2 connections) — `concepts/op-node-p2p-peering.md`
- **sequencer depth 과다 시 deposit-only 빈 블록 위험 (MaxSequencerDrift/SeqWindowSize)** (1 connections) — `concepts/op-node-l1-confs-conf-depth.md`
- **derivation 파이프라인 (verifConfDepth 소비 지점)** (1 connections) — `concepts/op-node-l1-confs-conf-depth.md`
- **verifier 기본 depth=0인 이유 (derivation이 reorg를 정식 지원)** (1 connections) — `concepts/op-node-l1-confs-conf-depth.md`
- **방화벽 기반 inbound 하드 차단 (TCP/UDP 9222)** (1 connections) — `concepts/op-node-p2p-peering.md`

## Relationships

- [Wiki 인덱스 허브](Wiki_%EC%9D%B8%EB%8D%B1%EC%8A%A4_%ED%97%88%EB%B8%8C.md) (1 shared connections)
- [L1 Receipt 조회 전략](L1_Receipt_%EC%A1%B0%ED%9A%8C_%EC%A0%84%EB%9E%B5.md) (1 shared connections)
- [P2P 피어링·부트노드 진단](P2P_%ED%94%BC%EC%96%B4%EB%A7%81%C2%B7%EB%B6%80%ED%8A%B8%EB%85%B8%EB%93%9C_%EC%A7%84%EB%8B%A8.md) (1 shared connections)

## Source Files

- `concepts/op-node-l1-confs-conf-depth.md`
- `concepts/op-node-p2p-peering.md`

## Audit Trail

- EXTRACTED: 17 (89%)
- INFERRED: 2 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*