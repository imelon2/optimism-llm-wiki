---
type: Concept
title: op-node 동기화 모드(CLSync/ELSync) & ReqResp P2P Sync Deprecation
description: op-node의 --syncmode(consensus-layer/execution-layer) 차이와, CL 레벨 ReqResp P2P sync 클라이언트가 제거되어 gap 복구가 op-reth의 EL snap sync로 넘어간 변화. deprecated no-op 플래그와 op-reth의 post-finalization EL sync 이점
resource: resource/optimism/op-node/rollup
tags: [op-stack, p2p, sync, reth, l2]
timestamp: 2026-07-16T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# op-node 동기화 모드(CLSync/ELSync) & ReqResp P2P Sync Deprecation

## 개요

op-node가 뒤처진 unsafe 체인을 따라잡는 방식이 바뀌었다. 예전에는 op-node가 **CL(컨센서스 계층) 레벨에서 다른 op-node에게 블록을 직접 요청**하는 ReqResp P2P sync(프로토콜 `/opstack/req/payload_by_number/<chainID>/0`)로 빠진 unsafe 블록을 backfill했다. 이 **클라이언트가 통째로 제거**되었고, 관련 CLI 플래그들은 deprecated no-op이 되었다. 이제 큰 gap 복구는 **op-reth(EL, 실행 계층)의 EL P2P snap sync**로 넘어간다.

핵심 결론:

1. **ReqResp sync 클라이언트 제거됨.** op-node는 더 이상 CL 레벨에서 peer에게 payload_by_number를 요청하지 않는다. `--syncmode.req-resp`·`--p2p.sync.onlyReqToStatic`는 deprecated no-op(always disabled)이다 (`resource/optimism/op-node/flags/flags.go:127-135`, `flags/p2p_flags.go:86-93`).
2. **서버는 아직 남아있다.** `--p2p.sync.req-resp`(기본 `true`)는 여전히 payloads-by-number **서버**를 켜서 요청하는 (구버전) peer에게 서빙한다. 단 "client side has been removed; server will be deprecated in a future release in favor of EL P2P sync" (`flags/p2p_flags.go:406-413`).
3. **gap 복구는 EL sync가 대체한다.** `--syncmode`는 `consensus-layer`(CLSync, 기본)와 `execution-layer`(ELSync) 두 값이며, **둘 다 결국 op-reth의 EL snap sync에 의존**한다. 차이는 "언제 EL sync를 시작하느냐"뿐이다.
4. **op-reth 사용자는 유리하다.** `--l2.enginekind=reth`(기본값)일 때 op-reth는 **finalized 블록이 이미 있어도 EL sync를 시작**할 수 있다(`SupportsPostFinalizationELSync=true`). op-geth는 fresh 상태에서만 EL sync가 된다.

> 비유: ReqResp client는 예전엔 "친구(다른 op-node)에게 전화해 빠진 페이지를 한 장씩 불러받던" 방식이었다. 취약해서 폐기됐고, 이제는 "실행 계층(op-reth)이 전용 DB로 스냅샷을 통째 내려받는" 방식으로 넘어갔다.

## 핵심 동작/책임

### 왜 ReqResp 클라이언트가 제거되었나

ReqResp sync는 unsafe payload(아직 확정 안 된 L2 블록)를 번호로 요청/응답하던 alt-sync였다. 폐기 이유(설계 문서 기준):

- **서명 없는 블록의 역순 인증 부담** — gossip과 달리 이 블록엔 서명이 없어, 역순으로 받아 sync target에 대조 검증해야 했다.
- **메모리 제약** — 전용 DB 없이 in-memory 버퍼라 sync 깊이가 제한됐다.
- **취약성** — 수차례 재작성 시도(2024-07 미병합 rewrite 포함)가 실패하며 "complexity-ceiling"에 도달했다.

대체재는 **EL sync via op-geth/op-reth**(snap sync): 전용 DB, skeleton chain으로 target 연결, reorg·moving target 자동 처리 (design-docs `protocol/deprecate-reqresp-sync.md`, 추적 이슈 optimism#14108).

### `--syncmode` 두 모드의 차이

gossip으로 unsafe payload가 들어오면 `OnUnsafeL2Payload`가 모드에 따라 분기한다 (`resource/optimism/op-node/rollup/driver/sync_deriver.go:96-116`):

```go
switch s.SyncCfg.SyncMode {
case sync.CLSync:
    s.Engine.AddUnsafePayload(ctx, envelope)   // 큐에 넣고 부모→자식 순서대로 실행
case sync.ELSync:
    if ref.Number <= s.Engine.UnsafeL2Head().Number { return }
    s.Engine.InsertUnsafePayload(...)          // 곧장 op-reth에 넘겨 snap sync 유도
}
```

- **`consensus-layer`(CLSync, 기본)** — op-node가 주도. gossip 블록을 payloads queue에 쌓아 **순서대로 한 개씩** `NewPayload`로 실행시킨다. op-node가 "이 블록 실행해"라고 일일이 지시하는 "받아쓰기" 방식.
- **`execution-layer`(ELSync)** — op-reth가 주도. 받은 tip이 내 head보다 앞서면 바로 `InsertUnsafePayload` → op-reth에 `forkchoiceUpdated`로 "최종 목적지는 이 블록"만 알려주고, **실제 블록 수집·실행은 op-reth가 자기 EL P2P에서 snap sync로** 처리하는 "알아서 따라와" 방식.

`sync.CLSync=0`(consensus-layer), `sync.ELSync=1`(execution-layer), 기본값 CLSync (`resource/optimism/op-node/rollup/sync/config.go:18-46`; 엔진 컨트롤러 초기 상태 `engine_controller.go:190-192`).

### 두 모드 모두 결국 EL sync로 수렴

**CLSync에서도 gap이 나면 EL sync로 fallback한다.** CLSync로 진행하다 부모 없는 블록을 만나면 op-reth의 `NewPayload`가 `SYNCING`을 반환하고, op-node는 CLSync에서도 이를 허용해 `forkchoiceUpdated`를 마저 호출 → op-reth가 EL snap sync를 시작한다 (`resource/optimism/op-node/rollup/engine/engine_controller.go:585-590`, 주석: "In CLSync mode we tolerate a SYNCING response ... can trigger the EL sync behavior").

따라서 실질적 차이는:
- **ELSync** = 시작하자마자 op-reth에 snap sync를 몰아준다(초기 catch-up 최적).
- **CLSync** = 평소엔 op-node가 순서대로 몰다가, 막히면 그때 EL sync로 빠진다.

EL sync가 끝나면(`syncStatusFinishedEL`) 두 모드 모두 정상 파생(consolidation)으로 전환된다 (`engine_controller.go:582-583, 801-814`). 즉 ELSync는 영구 모드라기보다 **초기 동기화 전략**에 가깝다. EL sync 진행 중에는 derivation 파이프라인이 backoff로 멈춰 기다린다 (`sync_deriver.go:264-266`).

### op-reth 특혜: post-finalization EL sync

op-node는 엔진 종류별로 EL sync 허용 조건을 다르게 둔다 (`resource/optimism/op-node/rollup/engine/engine_kind.go:37-45`):

```go
func (kind Kind) SupportsPostFinalizationELSync() bool {
	switch kind {
	case Geth:            return false
	case Erigon, Reth:    return true   // op-reth는 true
	}
}
```

`insertUnsafePayload`의 초기 분기 (`engine_controller.go:757-767`): EL sync 시작 시 finalized 블록을 조회해서 —
- **op-geth**: 이미 finalized 블록이 있으면 EL sync를 거부하고 CLSync로 빠진다. 즉 신규(genesis) 상태에서만 snap sync 가능.
- **op-reth / erigon**: `SupportsPostFinalizationELSync=true`라 **finalized 블록이 있어도 EL sync를 시작**할 수 있다.

**실질 의미**: ReqResp client가 사라진 지금, 오래 운영하던 노드가 크게 뒤처졌을 때 — op-geth는 EL snap sync 복구가 막히지만 **op-reth는 finalized head가 있는 상태에서도 EL snap sync로 복구**할 수 있다. `--l2.enginekind` 기본값은 이미 `reth`다 (`resource/optimism/op-node/flags/flags.go:220-228`).

## 주요 인터페이스/필드

### 플래그 상태 (코드 정본)

| 플래그 | 상태 | 근거 |
|---|---|---|
| `--syncmode` | `consensus-layer`(기본) / `execution-layer` | `sync/config.go:18-46`, `flags.go:120-126` |
| `--l2.enginekind` | 기본 `reth`. reth/erigon만 post-finalization EL sync | `flags.go:220-228`, `engine_kind.go:37-45` |
| `--syncmode.req-resp` | **Deprecated, no-op. 항상 disabled**, hidden | `flags.go:127-135` |
| `--p2p.sync.onlyReqToStatic` | **Deprecated, no-op.** 클라이언트 제거됨, hidden | `p2p_flags.go:86-93` |
| `--p2p.sync.req-resp` | 존재(기본 `true`)하나 **서버만** 켬. 향후 제거 예정 | `p2p_flags.go:406-413` |

### 남은 ReqResp 서버 동작

`--p2p.sync.req-resp=true`이면 op-node는 아직 payload_by_number 서버를 띄워 요청 peer에게 블록을 서빙하며 rate limit이 걸린다 (`resource/optimism/op-node/p2p/sync.go:40-58, 124-150`):
- 전역: 초당 20블록(burst 40) / peer당: 초당 4블록(burst 15)
- 초과 시 끊지 않고 throttle(대기), 임계치 넘으면 실패.

### 운영 권장 설정 (op-node + op-reth)

- **정상 운영 중**: 기본값 그대로 두고 deprecated no-op(`--syncmode.req-resp`, `--p2p.sync.onlyReqToStatic`)만 제거. CLSync도 gap은 EL sync fallback으로 복구된다.
- **초기 동기화 / 크게 밀림**: `--syncmode=execution-layer`로 op-reth snap sync를 곧장 몰아준다. 따라잡으면 자동으로 정상 파생으로 전환되므로 이후 굳이 안 바꿔도 된다.
- **전제**: `--l2.enginekind=reth`(기본) + op-reth의 EL P2P가 peer를 정상적으로 물고 있을 것. 이제 gap 복구가 op-reth의 EL discovery/peer에 의존하므로, op-reth가 peer를 못 물면 snap sync가 진행되지 않는다.

> 모순 flag: 공식 문서 `https://docs.optimism.io/node-operators/reference/op-node-config`의 `p2p.sync.req-resp` 설명은 아직 "default true, 서버·클라이언트 양쪽 활성화"로 서술되어 **코드(client 제거)와 충돌하는 stale 상태**다. 동작은 코드를 정본으로 삼는다.

> 근거: 로컬 `resource/optimism` 클론(`source_commit: aaeb6c0154`) 코드 기준. 폐기 배경은 [design-docs `protocol/deprecate-reqresp-sync.md`](https://github.com/ethereum-optimism/design-docs/blob/main/protocol/deprecate-reqresp-sync.md), 추적 이슈 [optimism#14108](https://github.com/ethereum-optimism/optimism/issues/14108).

## 관련 페이지

- [op-node P2P Peering & Chain Isolation](op-node-p2p-peering.md) — 본 페이지의 ReqResp 프로토콜 ID(`/opstack/req/payload_by_number/<chainID>/0`)가 등장하는 곳. 그 페이지는 P2P 피어링·chainID 격리를, 본 페이지는 그 위에서 도는 sync 클라이언트/서버의 제거·대체를 다룬다.
- [op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로](../runbooks/op-reth-changeset-cache-miss.md) — 본 페이지의 EL sync는 op-node가 op-reth에 보내는 engine API `forkchoiceUpdated`로 유도된다. 그 Runbook은 FCU-with-attributes 블록 빌드 경로를 다룬다.
- (아직 없음) 향후 `op-node` Component 페이지, derivation/gossip Concept 페이지가 생기면 교차링크한다.
