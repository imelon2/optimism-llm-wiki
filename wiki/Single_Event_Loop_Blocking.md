# Single Event Loop Blocking

> 25 nodes · cohesion 0.09

## Key Concepts

- **GlobalSyncExec** (8 connections) — `concepts/op-node-event-loop-design.md`
- **FindL1Origin** (6 connections) — `concepts/op-stack-block-production.md`
- **driver eventLoop** (5 connections) — `concepts/op-node-event-loop-design.md`
- **블로킹 백오프(창구 잠김)** (4 connections) — `concepts/op-node-event-loop-design.md`
- **Drain()** (3 connections) — `concepts/op-node-event-loop-design.md`
- **Emit / executor.Enqueue** (3 connections) — `concepts/op-node-event-loop-design.md`
- **retry.Do** (3 connections) — `concepts/op-node-event-loop-design.md`
- **RPC callTimeout 10초 (2단계 마감시한 부재)** (3 connections) — `concepts/op-stack-block-production.md`
- **L1 origin 선캐싱(500ms best-effort)** (3 connections) — `concepts/op-stack-block-production.md`
- **Executor 인터페이스** (2 connections) — `concepts/op-node-event-loop-design.md`
- **락 대신 소유권 설계** (2 connections) — `concepts/op-node-event-loop-design.md`
- **ParallelExec (events-parallel 미머지)** (2 connections) — `concepts/op-node-event-loop-design.md`
- **processEvent** (2 connections) — `concepts/op-node-event-loop-design.md`
- **드라이버 단일 이벤트 루프 위 직렬 실행** (2 connections) — `concepts/op-stack-block-production.md`
- **SequencerActionEvent** (2 connections) — `concepts/op-stack-block-production.md`
- **pprof goroutine 덤프 진단** (1 connections) — `concepts/op-node-event-loop-design.md`
- **libp2p eventbus Emit 배압** (1 connections) — `concepts/op-node-event-loop-design.md`
- **libp2p pubsub processLoop** (1 connections) — `concepts/op-node-event-loop-design.md`
- **event.NewGlobalSynchronous** (1 connections) — `concepts/op-node-event-loop-design.md`
- **onResetEngineRequest → FindL2Heads** (1 connections) — `concepts/op-node-event-loop-design.md`
- **OnUnsafeL2Payload** (1 connections) — `concepts/op-node-event-loop-design.md`
- **retry.Exponential()** (1 connections) — `concepts/op-node-event-loop-design.md`
- **systemActor.RunEvent** (1 connections) — `concepts/op-node-event-loop-design.md`
- **sanityEventLimit (10,000)** (1 connections) — `concepts/op-node-event-loop-design.md`
- **스케줄링 백오프(창구 열림)** (1 connections) — `concepts/op-node-event-loop-design.md`

## Relationships

- [L1 Confirmation Depth](L1_Confirmation_Depth.md) (2 shared connections)
- [Observability and Profiling](Observability_and_Profiling.md) (1 shared connections)
- [Personal Namespace Removal](Personal_Namespace_Removal.md) (1 shared connections)

## Source Files

- `concepts/op-node-event-loop-design.md`
- `concepts/op-stack-block-production.md`

## Audit Trail

- EXTRACTED: 51 (85%)
- INFERRED: 9 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*