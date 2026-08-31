# op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단

> God node · 12 connections · `runbooks/op-reth-sequencer-forward-txpool-full.md`

**Community:** [Transaction Submission & Local Exemption](Transaction_Submission_%26_Local_Exemption.md)

## Connections by Relation

### references
- [OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)](OP_Stack_%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%EC%A0%84%ED%8C%8C_%EA%B2%BD%EB%A1%9C_%28Ingress_%E2%86%92_%EC%8B%9C%ED%80%80%EC%84%9C%29.md) `EXTRACTED`
- [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")](reth-op-reth_txpool_%EC%9A%A9%EB%9F%89_%ED%95%9C%EB%8F%84_%26_%EA%B3%84%EC%A0%95_%EC%8A%AC%EB%A1%AF_%EC%A0%9C%ED%95%9C_%28-32003__txpool_is_full_%29.md) `EXTRACTED`
- [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth_--txpool.nolocals_%26_Local_Transaction_Exemption.md) `EXTRACTED`
- Wiki Index `EXTRACTED`
- Wiki Log `EXTRACTED`
- 진단 절차 (txpool_status / txpool_contentFrom / 원본 에러 문자열) `EXTRACTED`
- forward_raw_transaction / forward_raw_transaction_conditional `EXTRACTED`
- 재시도 없음 · 로컬 풀 미보관 (조기 반환) `EXTRACTED`
- 원인 A — 시퀀서 서브풀 용량 초과 `EXTRACTED`
- 원인 B — 계정 슬롯 초과 `EXTRACTED`
- rollup-boost parse_response_code — 에러 코드 무변형 통과 `EXTRACTED`
- SequencerClient::request() — 로그 발생 지점 `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*