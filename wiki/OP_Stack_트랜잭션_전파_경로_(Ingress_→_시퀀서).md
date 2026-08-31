# OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)

> God node · 21 connections · `concepts/op-stack-tx-ingress-propagation.md`

**Community:** [Transaction Submission & Local Exemption](Transaction_Submission_%26_Local_Exemption.md)

## Connections by Relation

### references
- [트랜잭션 √n 브로드캐스트 규칙 (원본 전송 vs 해시 알림)](%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%E2%88%9An_%EB%B8%8C%EB%A1%9C%EB%93%9C%EC%BA%90%EC%8A%A4%ED%8A%B8_%EA%B7%9C%EC%B9%99_%28%EC%9B%90%EB%B3%B8_%EC%A0%84%EC%86%A1_vs_%ED%95%B4%EC%8B%9C_%EC%95%8C%EB%A6%BC%29.md) `EXTRACTED`
- [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")](reth-op-reth_txpool_%EC%9A%A9%EB%9F%89_%ED%95%9C%EB%8F%84_%26_%EA%B3%84%EC%A0%95_%EC%8A%AC%EB%A1%AF_%EC%A0%9C%ED%95%9C_%28-32003__txpool_is_full_%29.md) `EXTRACTED`
- [op-node P2P Peering & Chain Isolation](op-node_P2P_Peering_%26_Chain_Isolation.md) `EXTRACTED`
- [op-reth --max-outbound-peers & devp2p 피어 슬롯 제어](op-reth_--max-outbound-peers_%26_devp2p_%ED%94%BC%EC%96%B4_%EC%8A%AC%EB%A1%AF_%EC%A0%9C%EC%96%B4.md) `EXTRACTED`
- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](OP_Stack_%EC%8B%9C%ED%80%80%EC%84%9C_%EB%B8%94%EB%A1%9D_%EC%83%9D%EC%84%B1_%EA%B3%BC%EC%A0%95_%282%EC%B4%88_%EC%82%AC%EC%9D%B4%ED%81%B4%29.md) `EXTRACTED`
- [txpool nonce 갭으로 인한 트랜잭션 전파 정지](txpool_nonce_%EA%B0%AD%EC%9C%BC%EB%A1%9C_%EC%9D%B8%ED%95%9C_%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%EC%A0%84%ED%8C%8C_%EC%A0%95%EC%A7%80.md) `EXTRACTED`
- [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth_--txpool.nolocals_%26_Local_Transaction_Exemption.md) `EXTRACTED`
- [op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단](op-reth__HTTP_request_to_sequencer_failed_..._-32003-_txpool_is_full__%EC%A7%84%EB%8B%A8.md) `EXTRACTED`
- Wiki Index `EXTRACTED`
- Wiki Log `EXTRACTED`
- 서명 검증(ecrecover) 위임 불가 `EXTRACTED`
- 길 B — Ingress + devp2p gossip `EXTRACTED`
- Ingress 구조의 조용한 장애 3종 `EXTRACTED`
- P2P 두 개 — libp2p(블록) vs devp2p(트랜잭션) `EXTRACTED`
- Tx Ingress Node 아키텍처 `EXTRACTED`
- 포워딩 시 로컬 풀 보존 차이 (op-reth 항상 보존 vs op-geth 미보존) `EXTRACTED`
- op-conductor는 tx 제출을 프록시하지 않는다 `EXTRACTED`
- 길 A — HTTP 포워딩 `EXTRACTED`
- --rollup.disable-tx-pool-gossip / --rollup.txpool.disable-gossip `EXTRACTED`
- --rollup.sequencer / --rollup.sequencerhttp `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*