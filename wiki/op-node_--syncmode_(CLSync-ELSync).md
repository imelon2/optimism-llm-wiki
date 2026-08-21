# op-node --syncmode (CLSync/ELSync)

> God node · 9 connections · `concepts/op-node-syncmode-reqresp-deprecation.md`

**Community:** [동기화·Engine API 빌드 사이클](%EB%8F%99%EA%B8%B0%ED%99%94%C2%B7Engine_API_%EB%B9%8C%EB%93%9C_%EC%82%AC%EC%9D%B4%ED%81%B4.md)

## Connections by Relation

### conceptually_related_to
- Engine API 블록 빌드 사이클 (FCU-with-attributes → getPayload → newPayload → FCU) `EXTRACTED`

### rationale_for
- ReqResp P2P sync 클라이언트 제거 배경 (무서명 역순 인증·메모리 제약·complexity ceiling) `EXTRACTED`

### references
- [Wiki Log (append-only 변경 이력)](Wiki_Log_%28append-only_%EB%B3%80%EA%B2%BD_%EC%9D%B4%EB%A0%A5%29.md) `EXTRACTED`
- [Wiki Index (OP Stack LLM Wiki 전체 카탈로그)](Wiki_Index_%28OP_Stack_LLM_Wiki_%EC%A0%84%EC%B2%B4_%EC%B9%B4%ED%83%88%EB%A1%9C%EA%B7%B8%29.md) `EXTRACTED`
- [op-reth --max-outbound-peers (devp2p outbound 슬롯 상한)](op-reth_--max-outbound-peers_%28devp2p_outbound_%EC%8A%AC%EB%A1%AF_%EC%83%81%ED%95%9C%29.md) `EXTRACTED`
- [op-node P2P Peering & Chain Isolation](op-node_P2P_Peering_%26_Chain_Isolation.md) `EXTRACTED`
- [op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로](op-reth__Changeset_cache_MISS__%EB%A1%9C%EA%B7%B8_%EC%A7%84%EB%8B%A8_%EB%B0%8F_op-stack_%EC%9C%A0%EB%B0%9C_%EA%B2%BD%EB%A1%9C.md) `EXTRACTED`
- ELSync (execution-layer, op-reth snap sync 주도) `EXTRACTED`
- CLSync (consensus-layer, op-node 주도 순차 NewPayload) `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*