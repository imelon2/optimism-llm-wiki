---
type: Concept
title: op-node 단일 이벤트 루프 설계 (GlobalSynchronous executor)
description: op-node의 모든 deriver(sequencer/engine/pipeline/sync/origin-selector)가 드라이버 goroutine 하나 위에서 직렬 실행되는 구조의 코드 근거 사슬, 락 대신 소유권으로 경합을 없애는 설계 의도(미머지 events-parallel 브랜치·Executor 추상화가 증거), 창구를 잠그는 백오프와 잠그지 않는 백오프의 구분, libp2p pubsub/eventbus와의 대조
resource: resource/optimism/op-service/event/executor_global.go
tags: [op-stack, sequencer, derivation, l2]
timestamp: 2026-08-24T00:00:00Z
version: bedrock
source_commit: aaeb6c0154
---

# op-node 단일 이벤트 루프 설계 (GlobalSynchronous executor)

## 개요

op-node 안에서 여러 부품(시퀀서, 엔진 컨트롤러, derivation 파이프라인)이 **같은 상태**를 고친다 — unsafe/safe/finalized head, 진행 중인 블록 빌드 작업. 동시 접근을 막는 방법은 크게 둘이다.

- **락(mutex)** — 아무나 만지되 열쇠를 받게 한다. 열쇠가 늘면 데드락 위험이 커진다.
- **소유권** — **한 goroutine만** 상태를 만진다. 나머지는 이벤트를 큐에 넣고, 그 goroutine이 하나씩 꺼내 처리한다.

**op-node는 소유권 방식이다.** 상태를 만지는 goroutine은 드라이버의 `eventLoop` 하나이고, 이벤트가 그 창구에 한 줄로 선다.

이 설계의 대가는 명확하다 — **그 goroutine이 오래 붙잡히면 노드 전체가 멈춘다.** 관련 장애 두 건이 모두 이 특성에서 나온다 (→ 관련 페이지).

## 핵심 동작/책임

### 근거 사슬 (6단계)

**① 드라이버 루프는 goroutine 1개**

```go
// resource/optimism/op-node/rollup/driver/driver.go:210-211
s.wg.Add(1)
go s.eventLoop()
```

한 번만 기동되며, 내부는 `for { select { ... } }` 하나다(`driver.go:305-346`).

**② 이벤트 처리 진입점은 그 루프 안의 한 줄**

```go
// resource/optimism/op-node/rollup/driver/driver.go:348-349
case <-s.drain.Await():
    if err := s.drain.Drain(); err != nil {
```

**③ `Drain()` 호출자는 저장소 전체에서 이곳뿐이다**

```
$ grep -rn "\.Drain()\|\.DrainUntil(" --include=*.go op-node/ op-service/ | grep -v _test
op-node/rollup/driver/driver.go:349      s.drain.Drain()
op-service/event/limiter.go:53           return l.emitter.Drain()        ← 인터페이스 패스스루
op-service/event/limiter.go:57           return l.emitter.DrainUntil(fn, excl)
```

`limiter.go`의 둘은 단순 전달이므로 실제 큐를 비우는 goroutine은 하나다.

**④ `Drain()`은 호출자 스택에서 그대로 실행된다**

```go
// resource/optimism/op-service/event/executor_global.go:190-203
func (gs *GlobalSyncExec) Drain() error {
	for {
		ev := gs.events.Pop()
		if ev.Event == nil { return nil }
		gs.processEvent(ev)      // go 키워드 없음
	}
}
```

`processEvent` → `h.onEvent(ev)`(`:161-166`) → `gh.d.RunEvent(ev)`(`:265`).

**⑤ `RunEvent`가 deriver를 직접 호출한다 — 여기에도 goroutine 분기가 없다**

```go
// resource/optimism/op-service/event/system.go:158-177
func (r *systemActor) RunEvent(ev AnnotatedEvent) {
	...
	effect := r.deriv.OnEvent(ev.Ctx, ev.Event)
```

즉 `Drain()` → `processEvent` → `RunEvent` → `Sequencer.OnEvent` → `startBuildingBlock` → `FindL1Origin`이 **하나의 콜스택**이다.

**⑥ 모든 deriver가 executor 하나를 공유한다**

```go
// resource/optimism/op-node/node/node.go:312-313
executor := event.NewGlobalSynchronous(node.resourcesCtx).WithMetrics(node.metrics)
sys := event.NewSystem(node.log, executor)
```

op-node 전체에서 `NewGlobalSynchronous` 호출은 이 한 곳뿐이고, 여기에 `status`·`engine-controller`·`finalizer`·`attributes-handler`·`pipeline`·`step-scheduler`·`sync`·`engine`·`origin-selector`·`sequencer`·`node`가 모두 등록된다(`driver.go:56-132`, `node.go:315`).

### `Emit`은 큐잉만 한다

```go
// resource/optimism/op-service/event/system.go:378
err := s.executor.Enqueue(annotated)
```

`Emit`은 핸들러를 즉석 실행하지 않는다. 그래서 **다른 goroutine(P2P 수신, RPC 핸들러 등)이 이벤트를 발행해도 실행은 언제나 드라이버 루프로 되돌아온다.** 발행 지점은 여럿이지만 실행 지점은 하나다.

큐가 넘치면 배압(backpressure)이 아니라 **폭주 감지**로 처리한다.

```go
// resource/optimism/op-service/event/executor_global.go:13-15
// Don't queue up an endless number of events.
// At some point it's better to drop events and warn something is exploding the number of events.
const sanityEventLimit = 10_000
```

한도 초과 시 `Enqueue`가 에러를 반환하고 `Sys.emit`이 **패닉**한다(`system.go:379-385`: *"we should panic to avoid deferred errors creating behaviors that are hard to reason about"*). 상시 방어는 emitter별 레이트리밋(`eventsLimit = 10_000/s`, `options.go`)이 맡는다.

### 범위 한정 — P2P는 "죽는" 게 아니라 "반영이 멈춘다"

루프가 잠기면 정지하는 것은 **이벤트 처리**이지 네트워크 계층 전체가 아니다.

- **P2P 수신 계층** — 별도 goroutine. 피어 관리와 gossip 수신은 계속 돌고, 페이로드는 `OnUnsafeL2Payload`(`driver.go:468`)로 들어와 큐에 쌓인다.
- **그 페이로드를 엔진에 넣는 처리** — 이벤트라서 드라이버 루프 뒤에 줄을 선다.

진단 시 피어 수·gossip 트래픽은 정상으로 보이므로 혼동하기 쉽다.

### 창구를 잠그는 백오프 vs 잠그지 않는 백오프

"backoff"라는 같은 단어가 정반대 성격으로 쓰인다. 장애 분석 시 이 구분이 핵심이다.

| 유형 | 구현 | 예 | 루프 |
|------|------|-----|------|
| **스케줄링 백오프** | 타이머 시각만 기록하고 즉시 반환 | `sequencer.go:569` `nextAction = now + 1s`<br>`step_scheduling_deriver.go:98` `time.After(delay)` | **열림** — 다른 이벤트 처리됨 |
| **블로킹 백오프** | 호출한 goroutine이 그 자리에서 잠 | `retry/operation.go:73-78` `select { case <-t.C: }` | **잠김** |

```go
// resource/optimism/op-service/retry/operation.go:73-78
t.Reset(strategy.Duration(i))
select {
case <-ctx.Done():
	return ctx.Err()
case <-t.C:        // 호출한 goroutine이 여기서 잔다
}
```

`retry.Do`가 **이벤트 핸들러 안에서** 호출되면 백오프 수면 자체가 창구를 잠근다. 실제로 리셋 경로가 그렇다.

```
engine_controller.go:1085-1086   case ResetEngineRequestEvent: e.onResetEngineRequest(ctx)
engine_controller.go:1382        → sync.FindL2Heads(...)
sync/start.go:208, 217           → retry.Do(ctx, 5, retry.Exponential(), ...)
```

`retry.Exponential()`은 `Min=0, Max=10s, jitter≤250ms`이므로 5회 시도의 백오프 합은 1+2+4+8 = **15초**이고(`retry/strategies.go:30-54`), 여기에 회당 RPC 타임아웃 10초가 더해져 **L2 블록 하나를 되짚는 데 최대 65초**가 잠긴다.

## 주요 인터페이스/필드

### 설계가 의도된 것이라는 증거

op-node에는 이 설계의 철학을 서술한 주석·README·doc.go가 **없다**. 대신 다음 세 가지가 의도성을 뒷받침한다.

**① 병렬 실행기가 구현되었으나 머지되지 않았다**

```
$ git log --oneline --all -- op-service/event/ op-node/rollup/event/
833a55c932 op-node: parallel events executor      ← protolambda, 2024-07-07

$ git merge-base --is-ancestor 833a55c932 HEAD
(조상 아님)

$ git branch -a --contains 833a55c932
  remotes/origin/events-parallel
```

`ParallelExec`(112줄)와 `ParallelEventProcessing bool` 설정 스위치까지 추가된 커밋이 브랜치에만 남아 있다. 병렬 대안을 만들어 본 뒤 채택하지 않은 것이므로, 동기 실행은 "아직 안 만든 것"이 아니라 **유지 중인 선택**이다.

**② 추상화가 병렬을 허용하도록 설계되어 있다**

`Executor`는 인터페이스이고 `GlobalSyncExec`는 그 구현체 중 하나다(`op-service/event/executor.go:16-19`). 여러 주석이 "동기 실행기일 경우"라는 조건절을 단다.

```go
// options.go:7    For synchronous executors this may help decide which deriver receives the event first.
// priority.go:7   when and if there is a synchronous choice.
// system.go:159   While different things may execute in parallel, only one event is executed per entry at a time.
```

마지막 줄이 실제 계약이다 — 보장하는 것은 goroutine 개수가 아니라 **deriver별 직렬성**이다.

**③ 코드가 스스로 "영구 보장이 아님"을 인정한다**

```go
// resource/optimism/op-node/rollup/attributes/attributes.go:85
// Events may be concurrent in the future. Prevent unsafe concurrent modifications to the attributes.
eq.mu.Lock()
```

현재는 필요 없는 뮤텍스를 미리 걸어둔다. 유사 표기: `engine/payloads_queue.go:73`("not safe to use concurrently"), `engine/payload_success.go:44`("must be sequentially invoked").

### libp2p와의 대조

op-node의 P2P 스택인 libp2p는 두 가지 다른 태도를 문서화하고 있어 비교 기준이 된다.

**pubsub — 같은 소유권 모델, 명시적으로 표기함.** `processLoop`가 상태를 독점 소유하고, 상태를 만지는 핸들러마다 마커를 붙인다.

```go
// go-libp2p-pubsub/pubsub.go:763 외 총 9곳
// Only called from processLoop.
```

외부에서 루프에 일을 밀어넣는 통로도 있다 — `eval chan func()` (`pubsub.go:143`, *"eval thunk in event loop"*). `mySubs`·`myTopics`·`peers` 같은 맵이 락 없이 평범한 맵인 이유가 이것이다.

**eventbus — 반대 선택(배압), 인터페이스 주석에 명시함.**

```go
// go-libp2p/core/event/bus.go:29-32
// Emit emits an event onto the eventbus. If any channel subscribed to the topic is blocked,
// calls to Emit will block.
```

느린 소비자가 생산자를 막는다. op-node는 이쪽을 따르지 않았다(`Emit`은 막히지 않음).

**시사점**: op-node는 pubsub과 같은 모델을 쓰면서 `// Only called from processLoop.`에 해당하는 표기를 하지 않았다. "이 루프 위에서 오래 머물면 안 된다"는 규칙이 코드에는 살아 있으나 글로 명문화되어 있지 않고, 이것이 `FindL1Origin`의 마감시한 누락(→ 관련 런북)이 리뷰에서 걸러지지 않은 배경으로 보인다.

### 진단 — pprof로 직접 확인

정지 순간에 goroutine 덤프를 뜨면 사슬 전체가 한 스택에 쌓여 있다.

```bash
curl -s localhost:6060/debug/pprof/goroutine?debug=2 | grep -A 25 "driver.*eventLoop"
```

`eventLoop` → `Drain` → `processEvent` → `RunEvent` → (해당 핸들러) 순으로 나타나며, 이 goroutine이 하나뿐임을 확인할 수 있다. op-node에 `--pprof.enabled`가 필요하다.

## 관련 페이지

- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](op-stack-block-production.md) — 이 루프 위에서 직렬 실행되는 9단계 사이클.
- [op-node FindL1Origin 무기한 대기로 인한 블록 생산 정지](../runbooks/op-node-find-l1-origin-stall.md) — 본 설계의 대가가 실제 장애로 드러나는 sequencing 경로.
- [op-node "failed to fetch receipts ... for L1 sysCfg update" 진단](../runbooks/op-node-fetch-receipts-context-deadline.md) — 같은 대가가 derivation 경로에서 드러나는 사례. 해당 런북의 "영향" 절이 본 페이지의 요약판이다.
- [op-node P2P Peering & Chain Isolation](op-node-p2p-peering.md) — 본 페이지가 대조 기준으로 삼은 libp2p 스택의 op-node 측 활용.
