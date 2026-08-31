# 트랜잭션 √n 브로드캐스트 규칙 (원본 전송 vs 해시 알림)

> God node · 22 connections · `concepts/tx-propagation-sqrt-broadcast.md`

**Community:** [Sqrt Broadcast & Tx Gossip](Sqrt_Broadcast_%26_Tx_Gossip.md)

## Connections by Relation

### references
- [OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)](OP_Stack_%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%EC%A0%84%ED%8C%8C_%EA%B2%BD%EB%A1%9C_%28Ingress_%E2%86%92_%EC%8B%9C%ED%80%80%EC%84%9C%29.md) `EXTRACTED`
- [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")](reth-op-reth_txpool_%EC%9A%A9%EB%9F%89_%ED%95%9C%EB%8F%84_%26_%EA%B3%84%EC%A0%95_%EC%8A%AC%EB%A1%AF_%EC%A0%9C%ED%95%9C_%28-32003__txpool_is_full_%29.md) `EXTRACTED`
- [op-node P2P Peering & Chain Isolation](op-node_P2P_Peering_%26_Chain_Isolation.md) `EXTRACTED`
- [op-reth --max-outbound-peers & devp2p 피어 슬롯 제어](op-reth_--max-outbound-peers_%26_devp2p_%ED%94%BC%EC%96%B4_%EC%8A%AC%EB%A1%AF_%EC%A0%9C%EC%96%B4.md) `EXTRACTED`
- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](OP_Stack_%EC%8B%9C%ED%80%80%EC%84%9C_%EB%B8%94%EB%A1%9D_%EC%83%9D%EC%84%B1_%EA%B3%BC%EC%A0%95_%282%EC%B4%88_%EC%82%AC%EC%9D%B4%ED%81%B4%29.md) `EXTRACTED`
- [txpool nonce 갭으로 인한 트랜잭션 전파 정지](txpool_nonce_%EA%B0%AD%EC%9C%BC%EB%A1%9C_%EC%9D%B8%ED%95%9C_%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%EC%A0%84%ED%8C%8C_%EC%A0%95%EC%A7%80.md) `EXTRACTED`
- Wiki Index `EXTRACTED`
- Wiki Log `EXTRACTED`
- √n 브로드캐스트 규칙 `EXTRACTED`
- propagate_transactions (op-reth) `EXTRACTED`
- buffer_hashes() — reth의 실제 지연 지점 `EXTRACTED`
- fetched_transactions 메트릭 `EXTRACTED`
- policy trusted + mode sqrt 조합 함정 `EXTRACTED`
- pool.retain_unknown() — 이미 보유한 알림 폐기 `EXTRACTED`
- --tx-propagation-policy (all/trusted/none) `EXTRACTED`
- choosePeers (op-geth, siphash + txSender) `EXTRACTED`
- devp2p caps/eth.md — Transaction Exchange `EXTRACTED`
- EIP-2464 (eth/65 announcements and retrievals) `EXTRACTED`
- hashes_pending_fetch 메트릭 `EXTRACTED`
- off-by-one — peer_idx > max_num_full `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*