# GlobalSyncExec

> God node · 8 connections · `concepts/op-node-event-loop-design.md`

**Community:** [Single Event Loop Blocking](Single_Event_Loop_Blocking.md)

## Connections by Relation

### calls
- Emit / executor.Enqueue `EXTRACTED`

### cites
- 드라이버 단일 이벤트 루프 위 직렬 실행 `EXTRACTED`

### implements
- Drain() `EXTRACTED`
- Executor 인터페이스 `EXTRACTED`

### rationale_for
- 락 대신 소유권 설계 `EXTRACTED`

### references
- event.NewGlobalSynchronous `EXTRACTED`

### semantically_similar_to
- op-node Tracer 훅 인터페이스 `INFERRED`
- libp2p pubsub processLoop `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*