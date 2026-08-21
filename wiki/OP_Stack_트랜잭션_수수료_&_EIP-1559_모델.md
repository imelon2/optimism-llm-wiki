# OP Stack 트랜잭션 수수료 & EIP-1559 모델

> God node · 9 connections · `concepts/op-stack-eip1559-fees.md`

**Community:** [Wiki 인덱스 허브](Wiki_%EC%9D%B8%EB%8D%B1%EC%8A%A4_%ED%97%88%EB%B8%8C.md)

## Connections by Relation

### rationale_for
- 실행 계층 정본 한계 (op-geth pinned 모듈 · op-revm 외부 크레이트) `EXTRACTED`

### references
- [Wiki Log (append-only 변경 이력)](Wiki_Log_%28append-only_%EB%B3%80%EA%B2%BD_%EC%9D%B4%EB%A0%A5%29.md) `EXTRACTED`
- [Wiki Index (OP Stack LLM Wiki 전체 카탈로그)](Wiki_Index_%28OP_Stack_LLM_Wiki_%EC%A0%84%EC%B2%B4_%EC%B9%B4%ED%83%88%EB%A1%9C%EA%B7%B8%29.md) `EXTRACTED`
- [OP Stack 노드 ↔ Grafana LGTM 관측성 연동](OP_Stack_%EB%85%B8%EB%93%9C_%E2%86%94_Grafana_LGTM_%EA%B4%80%EC%B8%A1%EC%84%B1_%EC%97%B0%EB%8F%99.md) `EXTRACTED`
- [op-reth --txpool.nolocals (local exemption 전체 비활성화)](op-reth_--txpool.nolocals_%28local_exemption_%EC%A0%84%EC%B2%B4_%EB%B9%84%ED%99%9C%EC%84%B1%ED%99%94%29.md) `EXTRACTED`
- [op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단](op-reth__HTTP_request_to_sequencer_failed_..._-32003-_txpool_is_full__%EC%A7%84%EB%8B%A8.md) `EXTRACTED`
- PoolErrorKind::DiscardedOnInsert (용량 초과 = 사실상 underpriced) `EXTRACTED`
- effectiveGasPrice = min(maxFeePerGas, baseFee + maxPriorityFeePerGas) `EXTRACTED`
- L1 data fee (maxFeePerGas로 상한 불가한 별도 항목) `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*