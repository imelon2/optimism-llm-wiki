# Single Event Loop Design

> 20 nodes · cohesion 0.11

## Key Concepts

- **GlobalSyncExec** (7 connections) — `concepts/op-node-event-loop-design.md`
- **driver eventLoop** (4 connections) — `concepts/op-node-event-loop-design.md`
- **블로킹 백오프(창구 잠김)** (3 connections) — `concepts/op-node-event-loop-design.md`
- **Drain()** (3 connections) — `concepts/op-node-event-loop-design.md`
- **Emit / executor.Enqueue** (3 connections) — `concepts/op-node-event-loop-design.md`
- **retry.Do** (3 connections) — `concepts/op-node-event-loop-design.md`
- **Executor 인터페이스** (2 connections) — `concepts/op-node-event-loop-design.md`
- **락 대신 소유권 설계** (2 connections) — `concepts/op-node-event-loop-design.md`
- **ParallelExec (events-parallel 미머지)** (2 connections) — `concepts/op-node-event-loop-design.md`
- **processEvent** (2 connections) — `concepts/op-node-event-loop-design.md`
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

- [Observability & Profiling](Observability_%26_Profiling.md) (1 shared connections)

## Source Files

- `concepts/op-node-event-loop-design.md`

## Audit Trail

- EXTRACTED: 36 (88%)
- INFERRED: 5 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*