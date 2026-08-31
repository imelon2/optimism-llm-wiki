# reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")

> God node · 18 connections · `concepts/reth-txpool-capacity-slot-limits.md`

**Community:** [Transaction Submission & Local Exemption](Transaction_Submission_%26_Local_Exemption.md)

## Connections by Relation

### references
- [트랜잭션 √n 브로드캐스트 규칙 (원본 전송 vs 해시 알림)](%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%E2%88%9An_%EB%B8%8C%EB%A1%9C%EB%93%9C%EC%BA%90%EC%8A%A4%ED%8A%B8_%EA%B7%9C%EC%B9%99_%28%EC%9B%90%EB%B3%B8_%EC%A0%84%EC%86%A1_vs_%ED%95%B4%EC%8B%9C_%EC%95%8C%EB%A6%BC%29.md) `EXTRACTED`
- [OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)](OP_Stack_%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%EC%A0%84%ED%8C%8C_%EA%B2%BD%EB%A1%9C_%28Ingress_%E2%86%92_%EC%8B%9C%ED%80%80%EC%84%9C%29.md) `EXTRACTED`
- [txpool nonce 갭으로 인한 트랜잭션 전파 정지](txpool_nonce_%EA%B0%AD%EC%9C%BC%EB%A1%9C_%EC%9D%B8%ED%95%9C_%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%EC%A0%84%ED%8C%8C_%EC%A0%95%EC%A7%80.md) `EXTRACTED`
- [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth_--txpool.nolocals_%26_Local_Transaction_Exemption.md) `EXTRACTED`
- [op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단](op-reth__HTTP_request_to_sequencer_failed_..._-32003-_txpool_is_full__%EC%A7%84%EB%8B%A8.md) `EXTRACTED`
- Wiki Index `EXTRACTED`
- Wiki Log `EXTRACTED`
- PoolErrorKind::DiscardedOnInsert (원인 A — 용량 초과) `EXTRACTED`
- max_account_slots (기본 16, in-flight 깊이 제한) `EXTRACTED`
- RpcPoolError::TxPoolOverflow `EXTRACTED`
- PoolErrorKind::SpammerExceededCapacity (원인 B — 계정 슬롯 초과) `EXTRACTED`
- 서브풀 4종 용량 한도 (10,000 tx / 20MB) `EXTRACTED`
- ensure_valid() 계정 슬롯 체크 `EXTRACTED`
- -32003 "txpool is full" `EXTRACTED`
- geth AccountSlots — 같은 이름·기본값, 반대 동작 `EXTRACTED`
- 클라이언트 지문 — -32003(reth) vs -32000(geth) `EXTRACTED`
- reject_spammer / allow_local_spamming 테스트 `EXTRACTED`
- RPC로 들어온 tx는 local이 아니다 `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*