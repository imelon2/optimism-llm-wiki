---
type: Runbook
title: op-node FindL1Origin 무기한 대기로 인한 블록 생산 정지 진단
description: 시퀀서의 L1 origin 선택(FindL1Origin)에 시퀀서 레벨 마감시한이 없어 L1 RPC 기본 타임아웃 10초 동안 단일 이벤트 루프가 잠기고, 실패 시 고정 1초 뒤 재시도가 반복되어 잠김 비율 약 91%로 블록이 나오지 않는 장애의 코드 근거·실패 유형별 주기 차이·리셋 중첩 시 블록당 65초·진단 로그 4종·대응 우선순위
resource: resource/optimism/op-node/rollup/sequencing/sequencer.go
tags: [op-stack, sequencer, l1, l2]
timestamp: 2026-08-24T00:00:00Z
chain: l1
version: bedrock
source_commit: aaeb6c0154
---

# op-node FindL1Origin 무기한 대기로 인한 블록 생산 정지 진단

## 개요

**증상**: 시퀀서 op-node가 크래시하지 않고 CPU도 한가한데 **unsafe head가 전진하지 않는다.** 로그는 계속 흐르고, P2P 피어 수와 gossip 트래픽도 정상으로 보인다.

**판정**: L1 RPC 지연이 원인인 경우가 대부분이며 자가복구 가능하나, **L1 지연이 지속되면 사실상 영구 정지**가 된다. 합의·안전성 문제나 데이터 손상은 아니다.

**핵심 메커니즘**: [블록 생성 사이클](../concepts/op-stack-block-production.md)의 **2단계(L1 origin 선택)** 에는 시퀀서 레벨 마감시한이 없다. L1이 응답하지 않으면 RPC 클라이언트 기본 타임아웃 10초가 끝날 때까지 그 자리에 머물고, 그동안 [단일 이벤트 루프](../concepts/op-node-event-loop-design.md)가 잠겨 시퀀서 타이머·derivation·P2P 페이로드 반영이 전부 뒤에서 대기한다.

> **범위 구분**: 본 페이지는 **sequencing 경로**(`op-node/rollup/sequencing/`)의 origin 선택을 다룬다. derivation 파이프라인의 origin 전진에서 receipts 조회가 실패하는 유사 장애는 → [op-node "failed to fetch receipts ..." 진단](op-node-fetch-receipts-context-deadline.md). 두 경로는 코드가 다르며 로그 문자열로 구분된다.

## 핵심 동작/책임

### 인과 사슬

```
드라이버 이벤트 루프 (goroutine 1개)          driver.go:224
  └─ Drain() → processEvent → RunEvent        executor_global.go:190
       └─ Sequencer.OnEvent → onSequencerAction    sequencer.go:378
            └─ startBuildingBlock()                sequencer.go:539
                 ├─ ctx := d.ctx                   sequencer.go:540  ← 마감시한 없음
                 └─ FindL1Origin(ctx, l2Head)      sequencer.go:556
                      └─ origin_selector.go:75
                           ├─ CurrentAndNextOrigin → L1BlockRefByHash   (캐시 미스 시)
                           └─ fetch → L1BlockRefByNumber                (다음 origin 필요 시)
                                RPC callTimeout 10초 소진 ← 여기서 루프 잠김
       ↑ 실패 시 nextAction = now + 1s          sequencer.go:569
```

### 마감시한 누락 — 같은 함수 안 22줄 차이

```go
// resource/optimism/op-node/rollup/sequencing/sequencer.go
540:  ctx := d.ctx                              // 노드 수명 컨텍스트. 데드라인 없음
556:  l1Origin, err := d.l1OriginSelector.FindL1Origin(ctx, l2Head)
      ...
578:  fetchCtx, cancel := context.WithTimeout(ctx, time.Second*20)
581:  attrs, err := d.attrBuilder.PreparePayloadAttributes(fetchCtx, l2Head, l1Origin.ID())
```

3단계(`PreparePayloadAttributes`)에는 20초 마감이 있는데 2단계에는 없다. 유일한 브레이크는 RPC 클라이언트 기본값이다.

```go
// resource/optimism/op-service/client/rpc.go:147-152
if cfg.callTimeout == 0      { cfg.callTimeout = 10 * time.Second }
if cfg.batchCallTimeout == 0 { cfg.batchCallTimeout = 20 * time.Second }
```

### 재시도 주기 — 10초는 상한이지 고정값이 아니다

```go
// resource/optimism/op-node/rollup/sequencing/sequencer.go:566-573
case errors.Is(err, ErrNextL1OriginRequired):
	fallthrough
default:
	d.nextAction = d.timeNow().Add(time.Second)   // timeNow()는 블로킹 종료 후 호출됨
	d.nextActionOK = d.active.Load()
	d.log.Error("Error finding next L1 Origin", "err", err)
	d.emitter.Emit(d.ctx, rollup.L1TemporaryErrorEvent{Err: err})
	return
```

`timeNow()`가 블로킹이 끝난 뒤 호출되므로 다음 시도는 `T0 + 잠김시간 + 1초`다. 잠김 시간은 L1의 실패 방식에 따라 다르다.

| L1 상태 | 잠김 | 재시도 주기 | 심각도 |
|---------|------|-------------|--------|
| connection refused / DNS 실패 | 수 ms | 약 1초 | 낮음 — 창구가 거의 안 잠김 |
| 패킷 유실·무응답(hang) | 10초 | 11초 | **높음** |
| 느리지만 3초에 응답 | 3초 | 에러 없음, 블록은 3초 늦게 생산 | 중간 |

방화벽이 패킷을 조용히 버리는 경우가 10초를 꽉 채운다.

**최대 20초가 될 수 있다.** `FindL1Origin` 안에 L1 호출이 순차로 최대 2번 있다(`origin_selector.go:78`의 `L1BlockRefByHash`, `:92`의 `fetch`). 첫 호출이 느리게 **성공**하고 두 번째가 타임아웃하면 합산된다. 첫 호출이 타임아웃하면 즉시 반환하므로 10초다.

### 잠김 비율

```
한 주기 = 10초 잠김 + 1초 대기 = 11초
잠김 비율 = 10 / 11 ≈ 91%
이 11초에 나왔어야 할 블록 = 11 / 2 ≈ 5.5개 → 실제 0개
```

1초 대기 구간은 **스케줄링 백오프**라 루프가 열려 있다(→ [백오프 두 종류](../concepts/op-node-event-loop-design.md)). 그래서 100%가 아니라 91%다.

### 재시도는 같은 블록을 다시 만든다

`l2Head`가 변하지 않으므로 블록 번호와 타임스탬프(`parent.Time + BlockTime`)가 그대로다. 벽시계로 1분이 흘러도 그 블록의 타임스탬프는 과거 그대로이며, 정지가 길수록 체인이 실시간에서 뒤처진다. 복구되면 `payloadTime`이 계속 과거이므로 `nextAction = now`가 반복되어 **밀린 블록을 최대 속도로 몰아서** 생산한다(`sequencer.go:490-497`).

### 리셋이 겹치면 블록당 최대 65초

L1 리오그나 origin 불일치가 감지되면 `ResetEvent` → `ResetEngineRequestEvent`가 발행되고, 리셋 핸들러가 **이벤트 루프 위에서** L2 블록을 거꾸로 되짚으며 매번 L1에 조회한다.

```
engine_controller.go:1085-1086   case ResetEngineRequestEvent: e.onResetEngineRequest(ctx)
engine_controller.go:1382        → sync.FindL2Heads(...)
sync/start.go:208, 217           → retry.Do(ctx, 5, retry.Exponential(), ...)
```

```
시도 5회 × 10초 타임아웃 = 50초
백오프 1 + 2 + 4 + 8      = 15초   (retry/strategies.go:49-54, Max=10s)
────────────────────────────────
L2 블록 1개당 최대          65초    ← 전부 루프가 잠긴 시간
```

여기서 백오프는 **블로킹 백오프**다(`retry/operation.go:73-78`의 `select { case <-t.C: }`). 시퀀서의 1초 백오프와 달리 창구를 잠근다. 되짚을 블록 수만큼 곱해지므로 10블록이면 10분 이상이다.

게다가 리셋 중에는 `nextActionOK = false`로 **시퀀서 타이머 자체가 꺼진다**(`sequencer.go:458`). 다시 켜지려면 리셋 완료 신호가 필요한데, 그 신호가 위 재시도 루프에 묶여 있다. 재시도가 안전장치가 아니라 정지의 원인이 되는 지점이다.

## 주요 인터페이스/필드

### 원인 후보 — 캐시가 빗나가는 순간

정상 경로에서는 헤드 갱신 시 500ms 예산으로 다음 origin을 선캐싱하므로 2단계의 L1 호출이 0회다(`origin_selector.go:157`). 아래 상황에서 캐시가 빗나가고, 하필 L1 불안정 시점과 겹친다.

1. **노드 재시작 직후** — 캐시가 비어 `L1BlockRefByHash`부터 조회해야 한다.
2. **L1 리오그 직후** — 캐시 무효화 + 리셋 중첩(위 65초 경로).
3. **L1 origin 경계** — 선캐싱 500ms가 실패했다면 그 자리에서 직접 조회한다.
4. **conf depth 구간** — `--sequencer.l1-confs`(기본 4)가 과다하면 다음 origin이 계속 `NotFound`로 보여 매 블록 재조회를 시도한다 (→ [L1 Confirmation Depth](../concepts/op-node-l1-confs-conf-depth.md)).

### 진단 절차

**1. 로그 4종 확인**

```
① "Started sequencing new block" 이후 다음 로그까지 수 초의 공백
   → 그 공백이 FindL1Origin에 잠긴 시간 (sequencer.go:576)

② "Error finding next L1 Origin"  err=...
   → 타임아웃이 실제로 터졌다는 증거 (sequencer.go:571)

③ "Scheduled sequencer action"  delta=-8.4s
   → delta가 음수로 커짐 = 이미 늦음 (driver.go:265)

④ op-conductor: unsafe head 정체 → 헬스체크 실패 → 리더 교체
   → health/monitor.go:141
```

**2. 로그의 함정 — 타임아웃이 안 보일 수 있다**

`fetch` 경로에서 타임아웃하면 원래 에러가 버려지고 다른 에러로 대체된다.

```go
// resource/optimism/op-node/rollup/sequencing/origin_selector.go:102-104
} else {
    return eth.L1BlockRef{}, ErrNextL1OriginRequired   // fetch의 err를 버림
}
```

그래서 ②의 `err=`에 `context deadline exceeded`가 아니라 `origin-selector: nextL1Origin not supplied but required to satisfy constraints`만 보인다. **이 메시지가 반복되면 로직 문제가 아니라 L1 지연을 먼저 의심한다.**

**3. goroutine 덤프로 확증**

```bash
curl -s localhost:6060/debug/pprof/goroutine?debug=2 | grep -A 25 "driver.*eventLoop"
```

`eventLoop` → `Drain` → `processEvent` → `RunEvent` → `startBuildingBlock` → `FindL1Origin`이 한 스택에 쌓여 있으면 확정이다.

**4. 메트릭**

`unsafe head 번호 vs 벽시계 기대값`의 격차가 가장 정직한 신호다. CPU·메모리는 정상으로 보이므로 그쪽만 보면 놓친다. 설정 블록타임(→ [L2 블록타임](../concepts/op-stack-l2-block-time.md))과 실측 블록 간격을 비교하는 것이 사실상 최선의 헬스체크다.

### 대응 (우선순위)

| # | 조치 | 근거 |
|---|------|------|
| 1 | **L1 RPC를 저지연 엔드포인트로 교체.** 같은 네트워크 내 전용 L1 노드 권장, 공용 엔드포인트 직결 지양 | 원인의 대부분 |
| 2 | **호출 타임아웃을 블록타임에 맞춰 축소.** 기본 10초는 2초 체인에 과도. 실패는 1초 뒤 재시도로 회복되지만 **정지는 회복되지 않는다** | `rpc.go:147-152` |
| 3 | `--l1.rpc-max-batch-size` 축소 — 배치 타임아웃은 20초로 두 배 | `rpc.go:150-152` |
| 4 | `--sequencer.l1-confs` 점검 — 과다 시 캐시 상시 미스 | 원인 후보 4 |
| 5 | op-conductor 페일오버 준비 — 근본 해결은 아니나 체인은 계속 굴러감 | `health/monitor.go:141` |

### 판정 요약

| 관측 | 판정 |
|------|------|
| ② 단발 1~2건, 곧 헤드 전진 | 무해. L1 순간 지연. 종결 |
| ② 반복 + ③ delta 음수 확대 + 헤드 정체 | 본 장애. 대응 1·2 적용 |
| ② 반복이나 잠김 시간이 짧음(로그 간격 1초 내외) | connection refused 계열. 엔드포인트 도달성·DNS 점검 |
| `ResetEvent`/리셋 로그 동반, 수 분 정지 | 리셋 중첩(65초/블록 경로). L1 리오그 여부 확인 |
| 로그 문자열이 `failed to fetch receipts ... for L1 sysCfg update` | **다른 경로.** → [receipts 런북](op-node-fetch-receipts-context-deadline.md) |

### 불확실성 / 검증 한계

- 위 10초/20초는 RPC 클라이언트 **기본값**이다. 배포 환경에서 오버라이드했다면 실제 창이 다르다. 노드 실행 플래그로 별도 확인이 필요하다.
- 65초 계산은 `retry.Exponential()` 기본 전략과 회당 타임아웃 소진을 가정한 **상한**이다. 실제로는 일부 시도가 빠르게 실패해 더 짧을 수 있다.
- 마감시한 누락이 의도적 설계인지 실수인지는 코드·커밋 메시지에서 확인되지 않았다. 22줄 아래 3단계에 20초가 붙어 있다는 점이 정황일 뿐이다.

## 관련 페이지

- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](../concepts/op-stack-block-production.md) — 본 장애가 발생하는 2단계의 위치와 전체 사이클.
- [op-node 단일 이벤트 루프 설계](../concepts/op-node-event-loop-design.md) — "왜 호출 하나가 노드 전체를 멈추나"의 구조적 근거, 백오프 두 종류의 구분.
- [op-node "failed to fetch receipts ... for L1 sysCfg update" 진단](op-node-fetch-receipts-context-deadline.md) — derivation 경로의 동일 계열 장애. 증상이 비슷하므로 로그 문자열로 먼저 분기한다.
- [op-node --verifier.l1-confs vs --sequencer.l1-confs](../concepts/op-node-l1-confs-conf-depth.md) — 원인 후보 4(캐시 상시 미스)의 설정 배경.
- [op-node l1.rpckind & L1 Receipts Fetching 최적화](../concepts/op-node-l1-rpckind-receipts.md) — L1 RPC 조회 경로 최적화. 대응 1·3의 배경.
- [OP Stack L2 블록타임 설정 및 확인](../concepts/op-stack-l2-block-time.md) — 블록타임이 짧을수록 같은 10초 잠김이 삼키는 블록 수가 비례해 늘어난다.
