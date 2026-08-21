# op-reth --max-outbound-peers (devp2p outbound 슬롯 상한)

> God node · 11 connections · `concepts/op-reth-max-outbound-peers.md`

**Community:** [P2P 피어링·부트노드 진단](P2P_%ED%94%BC%EC%96%B4%EB%A7%81%C2%B7%EB%B6%80%ED%8A%B8%EB%85%B8%EB%93%9C_%EC%A7%84%EB%8B%A8.md)

## Connections by Relation

### conceptually_related_to
- --max-peers (총합 지정, inbound:outbound 2:1 분배, 배타) `EXTRACTED`

### rationale_for
- "default: 100" 문서/코드 불일치 (default_value_t 부재 → reth.toml 우선) `EXTRACTED`
- inbound trusted 예외 vs outbound 무예외 비대칭 `EXTRACTED`

### references
- [Wiki Log (append-only 변경 이력)](Wiki_Log_%28append-only_%EB%B3%80%EA%B2%BD_%EC%9D%B4%EB%A0%A5%29.md) `EXTRACTED`
- [Wiki Index (OP Stack LLM Wiki 전체 카탈로그)](Wiki_Index_%28OP_Stack_LLM_Wiki_%EC%A0%84%EC%B2%B4_%EC%B9%B4%ED%83%88%EB%A1%9C%EA%B7%B8%29.md) `EXTRACTED`
- [op-node P2P Peering & Chain Isolation](op-node_P2P_Peering_%26_Chain_Isolation.md) `EXTRACTED`
- [op-node --syncmode (CLSync/ELSync)](op-node_--syncmode_%28CLSync-ELSync%29.md) `EXTRACTED`
- op-reth discv5 Bootnode Timeout 진단 `EXTRACTED`
- ELSync (execution-layer, op-reth snap sync 주도) `EXTRACTED`
- has_out_capacity() — pending dial AND outbound 상한 AND 게이트 `EXTRACTED`
- try_rotate_peer() — capacity 도달 시 UselessPeer 절단 로테이션 `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*