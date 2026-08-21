# P2P 피어링·부트노드 진단

> 16 nodes · cohesion 0.14

## Key Concepts

- **op-reth --max-outbound-peers (devp2p outbound 슬롯 상한)** (11 connections) — `concepts/op-reth-max-outbound-peers.md`
- **op-node P2P Peering & Chain Isolation** (10 connections) — `concepts/op-node-p2p-peering.md`
- **op-reth discv5 Bootnode Timeout 진단** (8 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **ELSync (execution-layer, op-reth snap sync 주도)** (3 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **enode vs ENR 부트스트랩 경로 분기 (add_enr 로컬 vs request_enr 라이브 요청)** (3 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **try_rotate_peer() — capacity 도달 시 UselessPeer 절단 로테이션** (2 connections) — `concepts/op-reth-max-outbound-peers.md`
- **실패 모드 분기: timeout(느림) vs connection reset(끊김)** (2 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **kona bootstrap_peers 교차검증 (BootNode::Enode → request_enr, 실패 시 continue)** (2 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **request_enr Timeout의 의미 (UDP discv5 패킷 무응답, best-effort continue)** (2 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **체인별 gossip 토픽 /optimism/<L2ChainID>/N/blocks** (1 connections) — `concepts/op-node-p2p-peering.md`
- **SupportsPostFinalizationELSync (reth/erigon만 true)** (1 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **"default: 100" 문서/코드 불일치 (default_value_t 부재 → reth.toml 우선)** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **inbound trusted 예외 vs outbound 무예외 비대칭** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **--max-peers (총합 지정, inbound:outbound 2:1 분배, 배타)** (1 connections) — `concepts/op-reth-max-outbound-peers.md`
- **paradigmxyz/reth #12309 — 잘못된 enode가 피어 탐색을 막음** (1 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`
- **원인별 진단 (UDP 차단·discport 불일치·EL/CL 부트노드 혼동·discv4 enode·stale)** (1 connections) — `runbooks/op-reth-discv5-bootnode-timeout.md`

## Relationships

- [Wiki 인덱스 허브](Wiki_%EC%9D%B8%EB%8D%B1%EC%8A%A4_%ED%97%88%EB%B8%8C.md) (9 shared connections)
- [동기화·Engine API 빌드 사이클](%EB%8F%99%EA%B8%B0%ED%99%94%C2%B7Engine_API_%EB%B9%8C%EB%93%9C_%EC%82%AC%EC%9D%B4%ED%81%B4.md) (4 shared connections)
- [피어 발견·아웃바운드 다이얼](%ED%94%BC%EC%96%B4_%EB%B0%9C%EA%B2%AC%C2%B7%EC%95%84%EC%9B%83%EB%B0%94%EC%9A%B4%EB%93%9C_%EB%8B%A4%EC%9D%B4%EC%96%BC.md) (2 shared connections)
- [L1 확인 깊이·inbound 차단](L1_%ED%99%95%EC%9D%B8_%EA%B9%8A%EC%9D%B4%C2%B7inbound_%EC%B0%A8%EB%8B%A8.md) (1 shared connections)

## Source Files

- `concepts/op-node-p2p-peering.md`
- `concepts/op-node-syncmode-reqresp-deprecation.md`
- `concepts/op-reth-max-outbound-peers.md`
- `runbooks/op-node-fetch-receipts-context-deadline.md`
- `runbooks/op-reth-discv5-bootnode-timeout.md`

## Audit Trail

- EXTRACTED: 45 (90%)
- INFERRED: 5 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*