# txpool nonce 갭으로 인한 트랜잭션 전파 정지

> God node · 15 connections · `concepts/txpool-nonce-gap-propagation-stall.md`

**Community:** [Sqrt Broadcast & Tx Gossip](Sqrt_Broadcast_%26_Tx_Gossip.md)

## Connections by Relation

### references
- [트랜잭션 √n 브로드캐스트 규칙 (원본 전송 vs 해시 알림)](%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%E2%88%9An_%EB%B8%8C%EB%A1%9C%EB%93%9C%EC%BA%90%EC%8A%A4%ED%8A%B8_%EA%B7%9C%EC%B9%99_%28%EC%9B%90%EB%B3%B8_%EC%A0%84%EC%86%A1_vs_%ED%95%B4%EC%8B%9C_%EC%95%8C%EB%A6%BC%29.md) `EXTRACTED`
- [OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)](OP_Stack_%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%EC%A0%84%ED%8C%8C_%EA%B2%BD%EB%A1%9C_%28Ingress_%E2%86%92_%EC%8B%9C%ED%80%80%EC%84%9C%29.md) `EXTRACTED`
- [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")](reth-op-reth_txpool_%EC%9A%A9%EB%9F%89_%ED%95%9C%EB%8F%84_%26_%EA%B3%84%EC%A0%95_%EC%8A%AC%EB%A1%AF_%EC%A0%9C%ED%95%9C_%28-32003__txpool_is_full_%29.md) `EXTRACTED`
- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](OP_Stack_%EC%8B%9C%ED%80%80%EC%84%9C_%EB%B8%94%EB%A1%9D_%EC%83%9D%EC%84%B1_%EA%B3%BC%EC%A0%95_%282%EC%B4%88_%EC%82%AC%EC%9D%B4%ED%81%B4%29.md) `EXTRACTED`
- [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth_--txpool.nolocals_%26_Local_Transaction_Exemption.md) `EXTRACTED`
- nonce 갭 전파 정지 메커니즘 `EXTRACTED`
- Wiki Index `EXTRACTED`
- Wiki Log `EXTRACTED`
- queued 트랜잭션은 gossip되지 않는다 `EXTRACTED`
- 해결책 ② Ingress 노드 간 EL 피어링 `EXTRACTED`
- bad_imports 메트릭 (갭은 잡히지 않음) `EXTRACTED`
- FirstNonceGap: nil (풀의 갭 허용) `EXTRACTED`
- pool.pending_transactions_listener() `EXTRACTED`
- 해결책 ① 로드밸런서 sticky session (source IP) `EXTRACTED`
- --txpool.lifetime `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*