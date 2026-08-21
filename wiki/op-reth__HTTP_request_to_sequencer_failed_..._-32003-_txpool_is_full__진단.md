# op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단

> God node · 10 connections · `runbooks/op-reth-sequencer-forward-txpool-full.md`

**Community:** [txpool full 원인 판별](txpool_full_%EC%9B%90%EC%9D%B8_%ED%8C%90%EB%B3%84.md)

## Connections by Relation

### rationale_for
- -32003(reth) vs -32000(op-geth)로 거절 클라이언트 판별 `EXTRACTED`

### references
- [Wiki Log (append-only 변경 이력)](Wiki_Log_%28append-only_%EB%B3%80%EA%B2%BD_%EC%9D%B4%EB%A0%A5%29.md) `EXTRACTED`
- [Wiki Index (OP Stack LLM Wiki 전체 카탈로그)](Wiki_Index_%28OP_Stack_LLM_Wiki_%EC%A0%84%EC%B2%B4_%EC%B9%B4%ED%83%88%EB%A1%9C%EA%B7%B8%29.md) `EXTRACTED`
- [op-reth --txpool.nolocals (local exemption 전체 비활성화)](op-reth_--txpool.nolocals_%28local_exemption_%EC%A0%84%EC%B2%B4_%EB%B9%84%ED%99%9C%EC%84%B1%ED%99%94%29.md) `EXTRACTED`
- [op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로](op-reth__Changeset_cache_MISS__%EB%A1%9C%EA%B7%B8_%EC%A7%84%EB%8B%A8_%EB%B0%8F_op-stack_%EC%9C%A0%EB%B0%9C_%EA%B2%BD%EB%A1%9C.md) `EXTRACTED`
- [OP Stack 트랜잭션 수수료 & EIP-1559 모델](OP_Stack_%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98_%EC%88%98%EC%88%98%EB%A3%8C_%26_EIP-1559_%EB%AA%A8%EB%8D%B8.md) `EXTRACTED`
- PoolErrorKind::DiscardedOnInsert (용량 초과 = 사실상 underpriced) `EXTRACTED`
- 원인 A — 서브풀 용량 초과 (DiscardedOnInsert, 기본 10,000tx/20MB) `EXTRACTED`
- 원인 B — 계정 슬롯 초과 (SpammerExceededCapacity, max_account_slots 16 + 미래 nonce) `EXTRACTED`
- SequencerClient::request — "HTTP request to sequencer failed" WARN 발생 지점 `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*