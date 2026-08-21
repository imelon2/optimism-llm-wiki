# op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로

> God node · 10 connections · `runbooks/op-reth-changeset-cache-miss.md`

**Community:** [동기화·Engine API 빌드 사이클](%EB%8F%99%EA%B8%B0%ED%99%94%C2%B7Engine_API_%EB%B9%8C%EB%93%9C_%EC%82%AC%EC%9D%B4%ED%81%B4.md)

## Connections by Relation

### rationale_for
- op-node 스톨 = 방아쇠가 아닌 MISS 버스트 증폭기 `EXTRACTED`

### references
- [Wiki Log (append-only 변경 이력)](Wiki_Log_%28append-only_%EB%B3%80%EA%B2%BD_%EC%9D%B4%EB%A0%A5%29.md) `EXTRACTED`
- [Wiki Index (OP Stack LLM Wiki 전체 카탈로그)](Wiki_Index_%28OP_Stack_LLM_Wiki_%EC%A0%84%EC%B2%B4_%EC%B9%B4%ED%83%88%EB%A1%9C%EA%B7%B8%29.md) `EXTRACTED`
- [OP Stack 노드 ↔ Grafana LGTM 관측성 연동](OP_Stack_%EB%85%B8%EB%93%9C_%E2%86%94_Grafana_LGTM_%EA%B4%80%EC%B8%A1%EC%84%B1_%EC%97%B0%EB%8F%99.md) `EXTRACTED`
- [op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단](op-reth__HTTP_request_to_sequencer_failed_..._-32003-_txpool_is_full__%EC%A7%84%EB%8B%A8.md) `EXTRACTED`
- [op-node --syncmode (CLSync/ELSync)](op-node_--syncmode_%28CLSync-ELSync%29.md) `EXTRACTED`
- op-node "failed to fetch receipts ... for L1 sysCfg update" 진단 `EXTRACTED`
- op-reth discv5 Bootnode Timeout 진단 `EXTRACTED`
- Engine API 블록 빌드 사이클 (FCU-with-attributes → getPayload → newPayload → FCU) `EXTRACTED`
- 부모 상태 overlay 조회 (state_by_block_hash) → changeset MISS → DB 폴백 `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*