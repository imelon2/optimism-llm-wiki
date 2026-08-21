# op-reth --txpool.nolocals (local exemption 전체 비활성화)

> God node · 10 connections · `concepts/op-reth-txpool-nolocals.md`

**Community:** [Wiki 인덱스 허브](Wiki_%EC%9D%B8%EB%8D%B1%EC%8A%A4_%ED%97%88%EB%B8%8C.md)

## Connections by Relation

### rationale_for
- nolocals의 실효성은 sequencer 노드에 한정 (replica는 forward) `EXTRACTED`

### references
- [Wiki Log (append-only 변경 이력)](Wiki_Log_%28append-only_%EB%B3%80%EA%B2%BD_%EC%9D%B4%EB%A0%A5%29.md) `EXTRACTED`
- [Wiki Index (OP Stack LLM Wiki 전체 카탈로그)](Wiki_Index_%28OP_Stack_LLM_Wiki_%EC%A0%84%EC%B2%B4_%EC%B9%B4%ED%83%88%EB%A1%9C%EA%B7%B8%29.md) `EXTRACTED`
- [OP Stack 노드 ↔ Grafana LGTM 관측성 연동](OP_Stack_%EB%85%B8%EB%93%9C_%E2%86%94_Grafana_LGTM_%EA%B4%80%EC%B8%A1%EC%84%B1_%EC%97%B0%EB%8F%99.md) `EXTRACTED`
- [op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단](op-reth__HTTP_request_to_sequencer_failed_..._-32003-_txpool_is_full__%EC%A7%84%EB%8B%A8.md) `EXTRACTED`
- [OP Stack 트랜잭션 수수료 & EIP-1559 모델](OP_Stack_%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%EC%88%98%EC%88%98%EB%A3%8C_%26_EIP-1559_%EB%AA%A8%EB%8D%B8.md) `EXTRACTED`
- op-reth OTLP 트레이스/로그 네이티브 export (--tracing-otlp / --logs-otlp) `EXTRACTED`
- max_account_slots (기본 16, in-flight 미래 nonce 깊이 제한) `EXTRACTED`
- 흔한 착각 — 포워딩된 tx도 시퀀서에서 TransactionOrigin::External `EXTRACTED`

### shares_data_with
- LocalTransactionConfig (no_exemptions / local_addresses / propagate) `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*