---
type: Runbook
title: op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로
description: op-reth가 남기는 "Changeset cache MISS, falling back to DB-based computation" WARN이 무엇이고, op-node의 Engine API 블록 빌드(FCU-with-attributes)가 어떻게 이 조회를 유발하는지, 무해·자가복구 판정과 진단 체크리스트
resource: resource/optimism/op-node/rollup/engine/build_start.go
tags: [op-stack, reth, l2, sequencer]
timestamp: 2026-07-03T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로

## 개요

**증상**: op-reth(reth 코어)가 리더 시퀀서에서 다음 WARN을 버스트(3~8줄, block_number 내림차순)로 남긴다.

```
WARN Changeset cache MISS, falling back to DB-based computation block_hash=0x... block_number=NNNN
```

**판정: 무해·에러 아님·reorg 무관·자가복구.** reth는 블록마다 "그 블록을 되돌리기 위한 trie 변경분(changeset)"을 인메모리 캐시에 두는데, 어떤 블록의 changeset을 캐시에서 못 찾으면(MISS) DB에서 재계산(정확하지만 느림)한 뒤 다시 캐시에 넣는다. 이 WARN은 그 DB 폴백 1건당 1줄이다. 값은 정확하고 비용(CPU/IO)만 추가되며 스스로 복구된다.

**op-stack 관점 한 줄 요약**: 이 조회의 방아쇠는 **op-node가 다음 L2 블록을 만들려고 op-reth에 보내는 `engine_forkchoiceUpdatedV3(forkchoiceState, payloadAttributes)`** 다. 이 FCU의 `HeadBlockHash`(= op-node의 현재 unsafe 헤드)를 받은 op-reth가 "그 부모 위에 블록을 짓기 위한 부모 시점 상태"를 재구성하다가 changeset을 조회 → 조건에 따라 MISS가 난다. 따라서 **reth 로그의 `New payload job created ... parent=X`의 `X`는 op-node가 FCU에 실어보낸 그 블록 해시 그 자체**이고, 이어지는 MISS 버스트의 최고 번호 블록과 일치한다.

> **범위**: 본 페이지는 **정상 블록 생산 cadence에서 만성적으로 뜨는 소량 MISS**를 다룬다. 대규모 catch-up/unwind로 `persisted_tip − 64`보다 훨씬 깊은 블록을 대량 재구성해 MISS가 폭증하는 상황은 원인·영향이 다르며 본 페이지 범위 밖이다.

## 핵심 동작/책임

### op-node가 이 사이클을 굴리는 방식 (Engine API 블록 빌드 흐름)

op-node가 op-reth를 몰아가는 통로는 **Engine API**(`ForkchoiceUpdate`/`GetPayload`/`NewPayload`) 하나다 (`resource/optimism/op-node/rollup/engine/engine_controller.go:54-58`의 `ExecEngine` 인터페이스). 블록 빌드를 시작시키는 건 "attributes가 실린 FCU"이며, op-node 코드 주석이 이를 명시한다:

```go
// resource/optimism/op-service/sources/engine_client.go:73-75
// ForkchoiceUpdate ... If attributes is not nil, the engine client will also
// begin building a block based on attributes ... and return the payload ID.
```

`attributes != nil`인 FCU를 받은 op-reth가 payload job을 스폰하며 남기는 로그가 **`New payload job created ... parent=X`** 다.

한 블록은 op-node 엔진 상태머신(`engine_controller.go:1041-1090` `OnEvent`)에서 이 순서로 만들어진다:

| op-node 이벤트 | Engine API 호출 | op-reth 동작/로그 |
|---|---|---|
| `BuildStartEvent` → `onBuildStart` | `engine_forkchoiceUpdatedV3(fc, **attrs**)` | **New payload job created parent=X** → 빌드 시작 → 부모상태 overlay 조회 → **Changeset cache MISS**(조건부) → DB 폴백 |
| `BuildSealEvent` → `onBuildSeal` | `engine_getPayloadV3(id)` | 완성 블록 반환 |
| `PayloadProcessEvent` → `NewPayload` | `engine_newPayloadV3(payload)` | 블록 실행·검증·임포트 |
| (다음) FCU(attrs 없음) | `engine_forkchoiceUpdatedV3(fc, nil)` | 헤드 canonical 승격 |

→ **MISS는 1단계(빌드 시작 직후)에서만** 난다. 그래서 `New payload job created` 직후 1~6ms에 MISS 버스트가 시작된다.

### `parent=X`의 정체 — op-node의 unsafe 헤드

FCU를 조립하는 지점은 **`op-node/rollup/engine/build_start.go`의 `onBuildStart`** 다:

```go
// resource/optimism/op-node/rollup/engine/build_start.go:32-48
fcEvent := ForkchoiceUpdateEvent{
    UnsafeL2Head:    ev.Attributes.Parent,   // 지을 블록의 부모
    SafeL2Head:      e.SafeL2Head(),
    FinalizedL2Head: e.FinalizedHead(),
}
fc := eth.ForkchoiceState{
    HeadBlockHash:      fcEvent.UnsafeL2Head.Hash,     // ← reth 로그의 parent=X
    SafeBlockHash:      fcEvent.SafeL2Head.Hash,
    FinalizedBlockHash: fcEvent.FinalizedL2Head.Hash,  // ← reth evict 임계의 한 축(아래)
}
id, errTyp, err := e.startPayload(rpcCtx, fc, ev.Attributes.Attributes)  // FCU 전송
```

`startPayload`(`engine_controller.go:1430-1431`)가 `e.engine.ForkchoiceUpdate(ctx, &fc, attrs)`로 RPC를 쏜다. op-reth의 payload 빌더는 그 부모 상태를 해시로 읽는다 — `state_by_block_hash(ctx.parent().hash())` (`resource/optimism/rust/op-reth/crates/payload/src/builder.rs:270`) — 이 "부모 상태 조회"가 reth 코어의 overlay/changeset 경로로 들어가 MISS를 낼 수 있다. 조회는 부모에서 조상 방향(내림차순)으로 이어지므로 로그의 block_number도 내림차순이다.

### op-node의 `finalized` 신호가 reth의 캐시 축출(evict) 임계를 정한다

reth는 changeset 캐시를 `persist` 완료 시에만, "저장 지점 기준 일정 블록보다 오래된" 항목을 버린다(upstream reth 기준 임계 ≈ `min(finalized, persisted_tip − 64)`; 아래 불확실성 참고). 이때 `finalized`는 **op-node가 FCU에 실어보낸 `FinalizedBlockHash`** 다.

- op-node의 finalized 헤드는 **L1 finality에서 파생**된다 — `finality/finalizer.go`가 L1 finalized 블록에 대응하는 L2 블록을 `promoteFinalized` → `SetFinalizedHead`로 올린다 (`resource/optimism/op-node/rollup/engine/engine_controller.go:1175-1188`, `resource/optimism/op-node/rollup/finality/finalizer.go:86-152`).
- L2 finality는 L1보다 약 2 에폭(~13분) 지연되고, 매 L2 블록이 아니라 **L1 origin 전환 때 묶어서** 반영된다 — "PromoteSafe는 forkchoice 상태만 갱신하고 FCU를 안 보내며, L1 블록당 한 번 배치 FCU로 flush"한다 (`engine_controller.go:1058-1064`).
- 따라서 캐시 축출 임계는 op-node의 finality cadence에 맞춰 **계단식**으로 전진한다. L1 finality가 아직 없거나 op-node가 finalized를 못 올린 상태(초기 체인/테스트넷)면 임계는 순수 `persisted_tip − 64`로 동작한다.

### op-node 스톨은 방아쇠가 아니라 "버스트 증폭기"

정상 cadence(블록타임마다 `BuildStartEvent`)에서도 매 블록 1회 overlay 조회가 일어나 소량 MISS가 만성적으로 난다(스톨 없이도 관측됨). op-node가 스톨하면 `BuildStartEvent`/FCU가 지연·묶여, 재개 시 더 넓은 부모-조상 구간의 overlay를 한 번에 재구성 → **MISS 개수만 증가**한다. 즉 op-node 스톨은 필요조건이 아니라 버스트 폭을 키우는 요인일 뿐이다.

## 주요 인터페이스/필드

### 로그 상관관계 (op-node → op-reth)

`New payload job created`의 `parent`와 뒤따르는 MISS 버스트의 최고 번호 블록 해시가 **바이트 일치**한다 — op-node가 FCU로 가리킨 부모가 곧 reth가 overlay를 재구성하려 제일 먼저 조회하는 블록이기 때문이다.

정상 cadence 예 (스톨 없음) — payload job 직후 MISS, `parent` = 최고 번호 MISS 블록:
```
INFO New payload job created id=0x0477c05f5dce4491 parent=0x4ad176927a5039ec0529c4f1f8d6621fa62a6a08116778c876c0a6f78bec1257
WARN Changeset cache MISS ... block_hash=0x4ad176927a5039ec... block_number=2928432
WARN Changeset cache MISS ... block_hash=0x83e39a2f34209a01... block_number=2928431
WARN Changeset cache MISS ... block_hash=0x9f3bab1c21a10a7e... block_number=2928430
```

스톨 후 버스트 예 (내림차순, 개수만 증가):
```
WARN Changeset cache MISS ... block_number=3103856
WARN Changeset cache MISS ... block_number=3103857
WARN Changeset cache MISS ... block_number=3103858
```

### 진단 체크리스트

1. **에러로 오인 말 것**: 이 WARN은 정상 블록 생산의 부산물이다. reorg/unwind/`StateRootMismatch` 동반 여부를 먼저 확인 — 없으면 무해로 종결.
2. **버스트가 리더 시퀀서에 국한**되고, 각 버스트가 `New payload job created` 직후 시작하며 `parent` 해시가 버스트 최고 번호 MISS와 일치하면 → 정상 빌드 경로다.
3. **버스트 폭이 커졌다면** op-node 스톨/지연(sequencing loop, derivation)을 함께 본다. MISS는 결과 신호이지 원인이 아니다.
4. **관측 수단**: 이 로그는 로그 축(Loki)으로 수집·조회한다. Loki 쿼리 예: `{service_name="op-reth"} |= "Changeset cache MISS"`, 상관 확인은 `... |~ "New payload job created|Changeset cache MISS"`.

> 근거: op-stack(op-node) 측은 로컬 `resource/optimism` 클론(`source_commit: aaeb6c0154`) 코드로 확인. reth 코어 내부(changeset 캐시 구현·축출 상수)는 아래 불확실성 참고.

### 불확실성 / 검증 한계

- **reth 코어 내부는 이 레포에서 검증 불가.** `resource/optimism/rust`에는 op-reth 래퍼 크레이트만 벤더링돼 있고, changeset 캐시 구현체(`crates/trie/db`)·payload job 생성기·`"New payload job created"` 문자열·유지 상수(≈64블록)·축출 규칙은 **upstream reth(≈v2.3.0) 의존성**이라 로컬 인덱스에 없다. 해당 file:line·상수는 외부 reth 소스 분석에 의존하며, 배포 op-reth 버전에 따라 세부가 다를 수 있다. **op-node → Engine API 계약(attributes 실린 FCU가 빌드를 유발)은 버전 불변**이다.
- **EL 특이성**: 위 블록 빌드 사이클은 Engine API 표준이라 EL 종류와 무관하지만, `Changeset cache MISS` 로그 자체는 reth 계열 EL 고유다(op-geth에서는 이 WARN이 나지 않는다).

## 관련 페이지

- [op-reth discv5 Bootnode Timeout 진단](op-reth-discv5-bootnode-timeout.md) — 또 다른 op-reth 로그 진단(기동 시 부트노드 Timeout). 본 페이지와 **op-reth 로그 해석 런북 계열**을 공유한다.
- [OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황](../concepts/observability-grafana-integration.md) — 이 WARN은 관측성 4축 중 **로그 축(Loki)**으로 수집·상관분석하는 대상이다.
- [op-node 동기화 모드(CLSync/ELSync) & ReqResp P2P Sync Deprecation](../concepts/op-node-syncmode-reqresp-deprecation.md) — 본 페이지의 FCU-with-attributes 블록 빌드와 같은 engine API `forkchoiceUpdated` 경로가, EL sync에서는 op-node가 op-reth에 target head를 지정해 snap sync를 유도하는 데 쓰인다.
