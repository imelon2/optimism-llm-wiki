---
type: Concept
title: OP Stack 시퀀서 블록 생성 과정 (2초 사이클)
description: op-node 시퀀서가 2초마다 L2 블록 하나를 만드는 9단계 사이클(알람 → L1 origin 선택 → deposit 수집 → Engine API forkchoiceUpdated/getPayload/newPayload → gossip)과 이를 구속하는 3가지 제약(고정 블록타임, L1 origin 시간 역전 금지, max sequencer drift 1800초), L1 origin 선캐싱으로 정상 경로에서 L1 RPC 호출이 0회가 되는 메커니즘
resource: resource/optimism/op-node/rollup/sequencing/sequencer.go
tags: [op-stack, sequencer, derivation, l2, l1]
timestamp: 2026-08-24T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# OP Stack 시퀀서 블록 생성 과정 (2초 사이클)

## 개요

OP Stack 시퀀서는 **2초에 한 번**(체인별 설정, → [L2 블록타임](op-stack-l2-block-time.md)) L2 블록 하나를 생산한다. 역할은 둘로 나뉜다.

- **op-node** — 무엇을 만들지 결정한다. 어느 L1 블록에 매달지, 어떤 deposit을 넣을지를 정해 지시서(payload attributes)를 쓴다. 블록을 직접 만들지는 않는다.
- **op-geth / op-reth (EL)** — 지시서를 받아 실제로 트랜잭션을 실행하고 블록을 만든다. 무엇을 만들지는 스스로 정하지 않는다.

둘은 **Engine API**로만 통신한다. 이 사이클이 만들어내는 것은 **unsafe 블록까지**이며, safe/finalized 승격은 op-batcher와 L1의 몫이다.

전체 사이클은 **드라이버의 단일 이벤트 루프 goroutine 위에서 순차 실행**된다 (→ [op-node 단일 이벤트 루프 설계](op-node-event-loop-design.md)). 이 사실이 아래 모든 단계의 장애 특성을 지배한다.

## 핵심 동작/책임

### 9단계 사이클

| # | 단계 | 외부 호출 | 코드 정본 |
|---|------|-----------|-----------|
| 1 | 타이머 만료 → `SequencerActionEvent` 발행 | — | `driver.go:326` |
| 2 | **L1 origin 선택** (`FindL1Origin`) | **L1 RPC** | `sequencer.go:556` → `origin_selector.go:75` |
| 3 | payload attributes 준비 (L1 info + deposit) | **L1 RPC** | `sequencer.go:581` |
| 4 | 블록 빌드 시작 `forkchoiceUpdatedV3(+attrs)` → `payloadID` | Engine | `engine/build_start.go:21` |
| 5 | 블록시각 −50ms까지 대기 (EL이 mempool에서 tx 수집) | — | `sequencer.go:270-274` |
| 6 | 블록 봉인 `getPayloadV3` | Engine | `engine/build_seal.go:58` |
| 7 | conductor 커밋(HA 구성 시) → P2P gossip | conductor/P2P | `sequencer.go:308-321` |
| 8 | 자체 체인에 반영 `newPayloadV3` + `forkchoiceUpdated` → **unsafe head** | Engine | `engine/payload_process.go` |
| 9 | 헤드 갱신 이벤트로 다음 알람 예약 → 1로 복귀 | — | `sequencer.go:472-527` |

`sealingDuration` 기본값은 50ms이며(`sequencer.go:26`), 5단계의 대기 종료 시각은 `payloadTime - sealingDuration`으로 예약된다. 남은 시간이 이보다 적으면 즉시 봉인한다(`sequencer.go:270`).

### 3가지 제약

**① 블록 간격은 고정이다.** 늦게 만들어도 타임스탬프는 `직전 + BlockTime`이다. 타임스탬프가 블록 번호에서 산술적으로 유도되기 때문이다.

```go
// resource/optimism/op-node/rollup/types.go:213
return cfg.Genesis.L2Time + ((blockNumber - cfg.Genesis.L2.Number) * cfg.BlockTime)
```

따라서 생산이 지연되면 체인이 실시간(wall clock)에서 그만큼 뒤처지고, 복구 후에는 밀린 블록을 **최대 속도로 몰아서** 생산해 따라잡는다(`sequencer.go:490-497`에서 `payloadTime`이 과거이면 `nextAction = now`).

**② L2 블록 시각은 L1 origin 시각보다 앞설 수 없다.** 미래의 L1 블록을 가리킬 수 없다는 뜻이다. `findL1OriginOfNextL2Block`이 `driftNext >= 0`일 때만 다음 origin을 채택한다(`origin_selector.go:262-266`).

**③ max sequencer drift = 1800초.** L1 origin을 이보다 오래 끌고 가면 사용자 트랜잭션을 넣지 못하고 **deposit만 든 빈 블록**이 나온다.

```go
// resource/optimism/op-node/rollup/sequencing/sequencer.go:610
attrs.NoTxPool = uint64(attrs.Timestamp) > l1Origin.Time+d.spec.MaxSequencerDrift(l1Origin.Time)
```

Fjord 이후 1800초는 rollup config 설정값이 아니라 **프로토콜 상수**다(`resource/optimism/op-node/rollup/chain_spec.go:31,110`). 하드포크 활성화 블록(Ecotone/Fjord/Isthmus/Jovian/Karst/Lagoon)에서도 같은 이유로 `NoTxPool = true`가 강제된다(`sequencer.go:614-660`).

### L1 origin 선캐싱 — 정상 경로에서 2단계는 L1을 부르지 않는다

2단계가 매번 L1 RPC를 호출하면 블록 생산이 L1 지연에 직결된다. 이를 피하려고 **헤드가 갱신될 때마다 500ms 예산으로 다음 origin을 미리 받아 캐시에 넣는다.**

```go
// resource/optimism/op-node/rollup/sequencing/origin_selector.go:157
ctx, cancel := context.WithTimeout(los.ctx, 500*time.Millisecond)
```

이 선캐싱은 **best-effort**다. 실패하면 조용히 로그만 남기고 포기하며 블록 생산을 붙잡지 않는다(`origin_selector.go:165-181`). 캐시가 적중하면 2단계의 L1 호출 횟수는 **0회**이고, 그래서 정상 운영에서는 이 경로가 블로킹하지 않는다.

캐시가 빗나가는 경우는 노드 재시작 직후, L1 리오그 직후, origin이 막 넘어가는 경계, conf depth에 걸려 다음 origin이 계속 `NotFound`로 보이는 구간이다. 이때 2단계가 그 자리에서 직접 L1을 조회하며, 여기에 **시퀀서 레벨 마감시한이 없다**는 점이 정지 장애로 이어진다 (→ [FindL1Origin 무기한 대기 정지](../runbooks/op-node-find-l1-origin-stall.md)).

### unsafe → safe → finalized

| 상태 | 의미 | 누가 만드나 |
|------|------|-------------|
| **unsafe** | 시퀀서가 방금 만든 블록. 되돌려질 수 있음 | 본 사이클 |
| **safe** | 배처가 L1에 올린 데이터로 다시 유도해낸 블록 | op-batcher + derivation |
| **finalized** | L1이 확정한 블록 | L1 |

## 주요 인터페이스/필드

### 단계별 타임아웃 지도

| 단계 | 마감시한 | 실패 시 |
|------|----------|---------|
| ② L1 origin 선택 | **없음** (RPC `callTimeout` 10초에만 의존) | 1초 뒤 재시도 (`sequencer.go:569`) |
| ③ attributes 준비 | 20초 (`sequencer.go:578`) | 1초 뒤 재시도 |
| ④ 빌드 시작 | 10초 (`engine/params.go` `buildStartTimeout`) | 1초 뒤 재시도 |
| ⑥ 봉인 | 10초 (`buildSealTimeout`) | 블록 폐기, 블록타임 후 재시작 (`handleInvalid`) |
| ⑦ conductor 커밋 | 30초 (`sequencer.go:309`) | 1초 뒤 재시도 |
| 선캐싱(정상 경로) | 500ms | 조용히 포기 |

②만 마감시한이 비어 있다. 같은 함수 안에서 22줄 아래 ③에는 20초가 붙어 있다는 점이 이 누락을 두드러지게 한다.

### Engine API 호출 순서 (Ecotone 이후)

1. `engine_forkchoiceUpdatedV3(fcState, payloadAttributes)` → `payloadID` 반환, 빌드 시작
2. `engine_getPayloadV3(payloadID)` → 완성 페이로드
3. `engine_newPayloadV3(payload)` → 실행·임포트
4. `engine_forkchoiceUpdatedV3(fcState)` → 헤드 갱신

(스펙: [specs.optimism.io/protocol/derivation.html](https://specs.optimism.io/protocol/derivation.html))

### 실패 유형별 재스케줄

```go
// resource/optimism/op-node/rollup/sequencing/sequencer.go:277-285
func (d *Sequencer) handleInvalid() {
	d.metrics.RecordSequencingError()
	d.latest = BuildingState{}
	d.asyncGossip.Clear()
	// upon error, retry after one block worth of time
	blockTime := time.Duration(d.rollupCfg.BlockTime) * time.Second
	d.nextAction = d.timeNow().Add(blockTime)
	d.nextActionOK = d.active.Load()
}
```

- 일시적 엔진 오류 → 1초 뒤 (syncing이면 30초, `sequencer.go:430-434`)
- 페이로드 무효/봉인 실패 → `handleInvalid`, 블록타임 뒤
- origin 불일치·orphan → `ResetEvent` 발행, 시퀀서 타이머 정지(`sequencer.go:458`)

## 관련 페이지

- [op-node 단일 이벤트 루프 설계](op-node-event-loop-design.md) — 본 사이클 9단계가 goroutine 하나 위에서 직렬 실행되는 구조와 그 설계 근거. 아래 두 런북의 공통 뿌리다.
- [op-node FindL1Origin 무기한 대기로 인한 블록 생산 정지](../runbooks/op-node-find-l1-origin-stall.md) — 본 사이클 **2단계**가 마감시한 없이 L1을 기다리며 전체를 잠그는 장애.
- [op-node "failed to fetch receipts ... for L1 sysCfg update" 진단](../runbooks/op-node-fetch-receipts-context-deadline.md) — derivation 파이프라인 쪽 L1 origin 전진에서 발생하는 유사 정지. 본 페이지 2단계(sequencing)와는 **다른 코드 경로**다.
- [op-node --verifier.l1-confs vs --sequencer.l1-confs](op-node-l1-confs-conf-depth.md) — 2단계의 origin 후보를 confDepth로 게이팅하는 설정. `--sequencer.l1-confs` 과다 시 drift 초과로 deposit-only 블록이 나온다.
- [OP Stack L2 블록타임 설정 및 확인](op-stack-l2-block-time.md) — 본 사이클의 주기를 정하는 `BlockTime` 파라미터.
- [OP Stack 트랜잭션 수수료 & EIP-1559](op-stack-eip1559-fees.md) — 3단계가 넣는 L1 info deposit이 실어 나르는 수수료 파라미터의 소비처.
- [OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)](op-stack-tx-ingress-propagation.md) — 5단계에서 EL이 mempool에서 수집하는 사용자 트랜잭션이 **어떻게 시퀀서 풀까지 도달하는가**. 시퀀서는 빌드 중 원격 풀을 조회할 수 없으므로(`miner/worker.go:774`), 블록 빌드 시작 전에 풀에 들어와 있어야 한다.
- [트랜잭션 `√n` 브로드캐스트 규칙](tx-propagation-sqrt-broadcast.md) — 전파 지연이 본 사이클의 **2초 블록타임 대비 얼마나 치명적인지**를 판단하는 기준. op-geth의 500ms 대기는 블록타임의 1/4에 해당한다.
