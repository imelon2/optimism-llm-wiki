---
type: Concept
title: op-node --verifier.l1-confs vs --sequencer.l1-confs (L1 Confirmation Depth)
description: 두 플래그가 동일한 confDepth 안전거리 메커니즘(L1 head 기준 최근 N블록을 NotFound로 숨김)을 각각 derivation 파이프라인과 sequencer의 L1 origin 선택에 적용한다는 차이, 기본값(verifier=0/sequencer=4)이 다른 이유, sequencer depth 과다 시 deposit-only 블록 위험
resource: resource/optimism/op-node/rollup/confdepth/conf_depth.go
tags: [op-stack, l1, sequencer, derivation]
timestamp: 2026-07-10T00:00:00Z
chain: l1
version: bedrock
source_commit: aaeb6c0154
---

# op-node --verifier.l1-confs vs --sequencer.l1-confs (L1 Confirmation Depth)

## 개요

`--verifier.l1-confs`와 `--sequencer.l1-confs`는 **둘 다 "L1 head에서 몇 블록 뒤까지만 신뢰하고 사용할지"를 정하는 동일한 confirmation-depth 안전거리** 설정이다. 유일한 차이는 그 안전거리를 **누가** 지키느냐다.

- `--verifier.l1-confs` → **derivation(검증·재구성) 파이프라인**에 적용
- `--sequencer.l1-confs` → **sequencer의 L1 origin 선택**에 적용

비유하면 L1 체인의 끝부분(최근 블록들)은 "아직 안 마른 페인트"라 언제든 뒤집힐(reorg) 수 있다. 두 플래그 모두 "끝에서 N칸은 아직 안 마른 걸로 치고 손대지 마라"는 안전거리다. 대상 컴포넌트만 다르다.

핵심 사실:

1. **같은 메커니즘, 다른 소비자.** 두 값 모두 `confdepth.NewConfDepth`로 L1 fetcher를 감싸지만, 하나는 derivation에, 하나는 origin selector에 주입된다 (`resource/optimism/op-node/rollup/driver/driver.go:61,111`).
2. **기본값이 다르다.** `--verifier.l1-confs`=**0**, `--sequencer.l1-confs`=**4** (`resource/optimism/op-node/flags/flags.go:252-284`).
3. **환경변수/카테고리.** `OP_NODE_VERIFIER_L1_CONFS`(L1RPC 카테고리) / `OP_NODE_SEQUENCER_L1_CONFS`(Sequencer 카테고리) (`flags.go:255,281`).
4. **depth=0이면 안전거리 없음.** L1 head를 그대로 사용한다. verifier가 기본 0인 이유는 derivation이 reorg를 정식 지원하기 때문 (`conf_depth.go:14`, `flags.go:254`).

## 핵심 동작/책임

### 공통 메커니즘 — confDepth 래퍼

두 값 모두 `op-node/rollup/confdepth/conf_depth.go`의 동일한 래퍼를 거친다. 이 래퍼는 L1 fetcher를 감싸 **L1 head에 너무 가까운 블록을 "없는 것(`ethereum.NotFound`)"처럼 숨긴다** (`conf_depth.go:29-39`).

```go
func (c *confDepth) L1BlockRefByNumber(ctx context.Context, num uint64) (eth.L1BlockRef, error) {
	l1Head := c.l1Head()
	if l1Head == (eth.L1BlockRef{}) {      // 시작 직후엔 그대로 통과
		return c.L1Fetcher.L1BlockRefByNumber(ctx, num)
	}
	if num == 0 || c.depth == 0 || num+c.depth <= l1Head.Number {
		return c.L1Fetcher.L1BlockRefByNumber(ctx, num)   // 안전거리 밖 → 정상 반환
	}
	return eth.L1BlockRef{}, ethereum.NotFound             // 안전거리 안 → 숨김
}
```

- 핵심 규칙: `num + depth <= l1Head.Number`일 때만 반환. 즉 **head 기준 최근 `depth`개 블록은 조회 불가**로 처리된다.
- **hash 조회 경로는 그대로 통과** — 임베딩(`derive.L1Fetcher`)으로 위임하며, 이미 신뢰된 데이터라 안전거리를 적용하지 않는다. depth는 `L1BlockRefByNumber`(번호 기반 순방향 traversal / origin 탐색)에만 걸린다 (`conf_depth.go:16-20`).

### 플래그 → 필드 매핑

CLI 값이 driver config로 들어간다 (`resource/optimism/op-node/service.go:197-198`).

```go
VerifierConfDepth:  ctx.Uint64(flags.VerifierL1Confs.Name),
SequencerConfDepth: ctx.Uint64(flags.SequencerL1Confs.Name),
```

그리고 `driver.go`에서 **각각 별도의 confDepth 래퍼를 만들어 서로 다른 컴포넌트에 주입**한다 (`resource/optimism/op-node/rollup/driver/driver.go:61,111`).

```go
// verifier용: derivation 파이프라인에 주입
verifConfDepth := confdepth.NewConfDepth(driverCfg.VerifierConfDepth, statusTracker.L1Head, l1)
derivationPipeline := derive.NewDerivationPipeline(log, cfg, depSet, verifConfDepth, ...)

// sequencer용: origin selector에 주입 (SequencerEnabled일 때만)
sequencerConfDepth := confdepth.NewConfDepth(driverCfg.SequencerConfDepth, statusTracker.L1Head, l1)
findL1Origin := sequencing.NewL1OriginSelector(driverCtx, log, cfg, sequencerConfDepth)
```

### --verifier.l1-confs의 효과 (derivation)

- derivation 파이프라인이 L1을 traversal하며 batch/deposit을 읽어 L2 safe head를 재구성할 때, 이 depth만큼 L1 head에서 떨어진 지점까지만 읽는다.
- 부가적으로 **runtime config 초기 로드** 시에도 `VerifierConfDepth`를 재사용한다 (`resource/optimism/op-node/node/node.go:392`).
- 플래그 Usage: *"Reorgs are supported, but may be slow to perform."* → 그래서 기본 0. depth를 올리면 L1 reorg 노출은 줄지만 safe head 진행이 그만큼 지연된다 (`flags.go:254`).

### --sequencer.l1-confs의 효과 (origin 선택)

- sequencer가 다음 L2 블록의 **L1 origin**을 고를 때 사용한다. `origin_selector.go:194` 주석: *"The L1 source can be shimmed to hide new L1 blocks and enforce a sequencer confirmation distance."*
- 동작: 다음 origin 후보(`currentOrigin.Number + 1`)를 조회했을 때 confDepth가 `NotFound`를 주면, sequencer는 origin을 전진시키지 않고 현재 origin에 머문다 (`resource/optimism/op-node/rollup/sequencing/origin_selector.go:182-186`). 즉 **head에서 4블록 안쪽으로는 origin을 당기지 않는다.**
- **왜 4인가:** 너무 최근 L1 블록을 origin으로 잡으면 그 블록이 reorg될 때 만든 L2 블록이 통째로 무효화된다. 안전거리로 이를 회피한다.

## 주요 인터페이스/필드

| 항목 | `--verifier.l1-confs` | `--sequencer.l1-confs` |
|---|---|---|
| 내부 필드 | `Driver.VerifierConfDepth` | `Driver.SequencerConfDepth` |
| **기본값** | **0** | **4** |
| 환경변수 | `OP_NODE_VERIFIER_L1_CONFS` | `OP_NODE_SEQUENCER_L1_CONFS` |
| 플래그 카테고리 | L1RPC | Sequencer |
| 소비 지점 | derivation 파이프라인 (L2 재구성/검증) + runtime config 로드 | L1 origin selector (신규 L2 블록 생성) |
| 역할 | L1 데이터를 **derive**할 때 L1 head에서 유지할 거리 | 새 블록의 **L1 origin**을 고를 때 L1 head에서 유지할 거리 |

### sequencer depth 과다 설정 시 위험

`driver/config.go:13-17` 주석이 명시하는 트레이드오프: `SequencerConfDepth`가 너무 크면 origin이 지나치게 뒤처져

- `rollup.Config.MaxSequencerDrift`(허용 시간) 안에 L1 origin을 채택하지 못하거나,
- `rollup.Config.SeqWindowSize`(L1 포함 가능 범위) 안에 들어가지 못해

**deposit만 담긴 빈 블록**밖에 만들지 못할 수 있다 (`resource/optimism/op-node/rollup/driver/config.go:13-17`).

## 관련 페이지

- [op-node "failed to fetch receipts ... for L1 sysCfg update" 진단](../runbooks/op-node-fetch-receipts-context-deadline.md) — sequencer가 L1 origin을 **전진**시킬 때(본 페이지의 `--sequencer.l1-confs`가 게이팅하는 바로 그 동작) receipts 조회가 실패하며 백오프하는 런북. origin 전진의 실패 측면을 다룬다.
- [op-node l1.rpckind & L1 Receipts Fetching 최적화](op-node-l1-rpckind-receipts.md) — 같은 op-node의 L1-facing 설정 계열. 이쪽은 L1 영수증 조회 방식, 본 페이지는 L1 head와의 안전거리.
