---
type: Concept
title: OP Stack L2 블록타임 설정 및 확인 (rollup.Config.BlockTime)
description: L2 블록타임이 초 단위 정수(uint64)로 rollup config에만 존재하며 제약은 0 불가·L1 블록타임 이하 두 가지뿐이라는 점, 온체인 컨트랙트에는 기록되지 않아 SystemConfig로 조회 불가라는 점, 배포 후 변경은 타임스탬프 소급 계산 때문에 하드포크가 된다는 점, optimism_rollupConfig RPC·rollup.json·타임스탬프 실측·superchain registry 4가지 확인 경로
resource: resource/optimism/op-node/rollup/types.go
tags: [op-stack, l2, derivation, sequencer]
timestamp: 2026-08-24T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# OP Stack L2 블록타임 설정 및 확인 (rollup.Config.BlockTime)

## 개요

L2 블록타임은 rollup config의 **초 단위 정수 필드**다. 1초·2초 모두 유효하며, OP Mainnet 계열의 관례값은 2초다.

```go
// resource/optimism/op-node/rollup/types.go:72-73
// Seconds per L2 block
BlockTime uint64 `json:"block_time"`
```

중요한 성질 셋:

- **온체인에 기록되지 않는다** — 컨트랙트를 읽어서 확인할 수 없다.
- **런타임 플래그가 아니다** — op-node CLI로 바꿀 수 없다.
- **배포 후 변경은 하드포크다** — 과거 모든 블록의 타임스탬프가 이 값으로 소급 계산되기 때문이다.

## 핵심 동작/책임

### 제약은 두 가지뿐

```go
// resource/optimism/op-node/rollup/types.go:298
if cfg.BlockTime == 0 { return ErrBlockTimeZero }

// resource/optimism/op-chain-ops/genesis/config.go:1055-1056
if d.L1BlockTime < d.L2BlockTime {
	return fmt.Errorf("L2 block time (%d) is larger than L1 block time (%d)", d.L2BlockTime, d.L1BlockTime)
}
```

이더리움 L1(12초) 위에서는 **1~12초 사이의 정수**가 유효하다. `uint64`이므로 0.5초 같은 소수 블록타임은 이 필드로 표현할 수 없다.

### 설정 위치 — 배포 시점

```go
// resource/optimism/op-chain-ops/genesis/config.go:672-673
// L2BlockTime is the number of seconds between each L2 block.
L2BlockTime uint64 `json:"l2BlockTime"`
```

op-deployer 기본값은 2다.

```go
// resource/optimism/op-deployer/pkg/deployer/state/deploy_config.go:87-90
L2CoreDeployConfig: genesis.L2CoreDeployConfig{
	...
	L2BlockTime:               2,
```

이 값이 genesis 생성 시 `rollup.Config.BlockTime`으로 전달된다(`config.go:1132`).

### 왜 런타임에 못 바꾸나

블록 타임스탬프가 블록 번호에서 산술적으로 유도된다.

```go
// resource/optimism/op-node/rollup/types.go:213
return cfg.Genesis.L2Time + ((blockNumber - cfg.Genesis.L2.Number) * cfg.BlockTime)
```

중간에 값을 바꾸면 **이미 확정된 과거 블록들의 타임스탬프가 재계산되면서 전부 어긋난다.** 그래서 op-node 플래그 목록에 블록타임을 바꾸는 옵션이 없고, 모든 노드의 rollup.json이 동시에 바뀌지 않으면 즉시 체인 스플릿이 된다.

### 온체인에는 없다

컨트랙트 소스 전체에서 `blockTime`·`rollupConfig`는 검출되지 않는다.

```
$ grep -rn -i "blocktime"    --include=*.sol packages/contracts-bedrock/src/   → 결과 없음
$ grep -rn -i "rollupconfig" --include=*.sol packages/contracts-bedrock/src/   → 결과 없음
```

대비되는 것은 실제로 온체인에 있는 값들이다.

**`SystemConfig` (L1)** — 운영 중 트랜잭션으로 바꿀 수 있고 L2가 따라야 하는 값:

```solidity
// resource/optimism/packages/contracts-bedrock/src/L1/SystemConfig.sol:108-156
uint256 public overhead;              uint32 public basefeeScalar;
uint256 public scalar;                uint32 public blobbasefeeScalar;
bytes32 public batcherHash;           uint32 public eip1559Denominator;
uint64  public gasLimit;              uint32 public eip1559Elasticity;
uint32  public operatorFeeScalar;     uint64 public operatorFeeConstant;
uint16  public daFootprintGasScalar;  uint64 public minBaseFee;
uint256 public l2ChainId;
```

**`L1Block` (L2 predeploy)** — 매 블록 L1에서 밀어넣는 값(`src/L2/L1Block.sol:26-67`): `number`, `timestamp`, `basefee`, `hash`, `sequenceNumber` 등.

`l2ChainId`가 SystemConfig에 있다는 점이 경계를 보여준다 — **롤업 설정 중 일부는 온체인에 올렸으나 블록타임은 올리지 않았다.** SystemConfig에 있는 값들의 공통점은 "운영 중 바꿀 수 있고 그 변경이 derivation에 자연스럽게 반영되는 것"인데, 블록타임은 그 조건을 만족하지 못한다.

같은 성격의 오프체인 전용 파라미터: `max_sequencer_drift`, `seq_window_size`, `channel_timeout`.

## 주요 인터페이스/필드

### 확인 방법 4가지

**A. op-node RPC (정본)**

```bash
curl -s -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":1,"method":"optimism_rollupConfig","params":[]}' \
  <op-node-rpc-url> | jq '.result | {block_time, max_sequencer_drift, seq_window_size}'
```

`optimism` 네임스페이스의 `RollupConfig` 메서드다(`op-node/node/node.go:614-616`, `op-node/node/api.go:185`). 노드가 실제로 로드한 설정을 그대로 반환하므로 가장 신뢰할 수 있다.

**B. rollup.json 직접 확인**

`--rollup.config`로 주는 파일의 `block_time` 필드. A와 값이 다르면 그 자체가 사고 원인이다.

**C. 체인에서 실측**

설정값이 아니라 **실제 생산 간격**을 본다.

```bash
N=$(cast block-number --rpc-url <l2-rpc>)
T1=$(cast block $N          -f timestamp --rpc-url <l2-rpc>)
T0=$(cast block $((N - 100)) -f timestamp --rpc-url <l2-rpc>)
echo "avg = $(( (T1 - T0) / 100 ))s"
```

**A와 C의 괴리가 곧 진단 정보다.** 정지 장애가 있으면 실측 간격이 설정값보다 커지고, 밀린 블록을 몰아서 낼 때는 순간적으로 작아진다 (→ [FindL1Origin 정지 런북](../runbooks/op-node-find-l1-origin-stall.md)).

**D. superchain registry (등록된 체인)**

`--network <chain>`으로 뜨는 노드는 레지스트리에서 값을 읽는다.

```go
// resource/optimism/op-node/rollup/superchain.go:74
BlockTime: chConfig.BlockTime,
```

**간접 힌트**: `L1Block.sequenceNumber`는 L1 origin이 바뀔 때마다 0으로 리셋되고 L2 블록마다 증가하므로, 한 에포크 내 최댓값이 대략 `L1블록타임 / L2블록타임`이다. L1 12초 기준 최댓값이 5 언저리면 2초 체인, 11 언저리면 1초 체인이다. 확증용은 아니고 교차검증 정도로 쓴다.

### 블록타임과 장애 피해의 비례

RPC 타임아웃(10초)과 봉인 여유(50ms)는 블록타임과 **무관한 고정 상수**다. 따라서 블록타임을 줄일수록 한 번의 L1 지연이 삼키는 블록 수가 비례해 늘어난다.

| 블록타임 | L1 RPC 10초 잠김 시 놓치는 블록 |
|----------|--------------------------------|
| 2초 | 5개 |
| 1초 | **10개** |

1초 체인을 운영한다면 L1 RPC 지연 예산을 그만큼 더 빡빡하게 잡아야 한다.

### 설정 요약

| 값 | 온체인 | 변경 방법 |
|----|--------|-----------|
| gasLimit, scalar, batcherHash 등 | SystemConfig | 트랜잭션 |
| l2ChainId | SystemConfig | 사실상 불변 |
| **block_time** | **없음** | **하드포크만** |
| max_sequencer_drift, seq_window_size | 없음 | 하드포크만 |

## 관련 페이지

- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](op-stack-block-production.md) — 이 파라미터가 정하는 사이클 주기와, 타임스탬프가 고정이라 지연이 곧 실시간 뒤처짐이 되는 이유.
- [op-node FindL1Origin 무기한 대기로 인한 블록 생산 정지](../runbooks/op-node-find-l1-origin-stall.md) — 설정값 대 실측 간격 비교를 헬스체크로 쓰는 방법.
- [OP Stack 트랜잭션 수수료 & EIP-1559](op-stack-eip1559-fees.md) — 블록타임과 달리 **온체인 SystemConfig에 있는** 파라미터들(EIP-1559 denominator/elasticity 등)의 설정 경로.
- [op-node --verifier.l1-confs vs --sequencer.l1-confs](op-node-l1-confs-conf-depth.md) — 함께 rollup config에만 존재하는 `MaxSequencerDrift`/`SeqWindowSize`와의 상호작용.
