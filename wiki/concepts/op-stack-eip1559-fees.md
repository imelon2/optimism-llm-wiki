---
type: Concept
title: OP Stack 트랜잭션 수수료 & EIP-1559 (maxFeePerGas / maxPriorityFeePerGas)
description: OP Stack에서 maxFeePerGas/maxPriorityFeePerGas가 L2 실행 수수료(effectiveGasPrice = min(maxFeePerGas, baseFee + maxPriorityFeePerGas))만 지배하고 L1 data fee는 별도 부과되는 2(+1)-요소 수수료 모델, base fee가 소각 대신 BaseFeeVault로 적립되는 OP 고유 차이, EIP-1559 파라미터의 Holocene 이후 체인별 설정, min-suggested-priority-fee 추천 하한
resource: https://docs.optimism.io/app-developers/transactions/fees
source_commit: aaeb6c0154
tags: [op-stack, eip-1559, fees, gas, reth, l2]
timestamp: 2026-07-06T00:00:00Z
chain: l2
version: bedrock
---

# OP Stack 트랜잭션 수수료 & EIP-1559 (maxFeePerGas / maxPriorityFeePerGas)

## 개요

OP Stack에서 트랜잭션의 `maxFeePerGas`/`maxPriorityFeePerGas` 두 EIP-1559 필드는 **L2 실행 수수료(execution fee) 부분만** 지배한다. 이더리움과 완전히 동일하게 `effectiveGasPrice = min(maxFeePerGas, baseFee + maxPriorityFeePerGas)`로 해석된다. 반면 OP 고유의 **L1 data fee(트랜잭션 데이터를 L1에 게시하는 비용)는 이 두 필드가 전혀 커버하지 않고**, 사용자 잔액에서 별도로 추가 차감된다.

비유하면, OP에서 요금 영수증에는 항목이 최소 2줄이다. `maxFeePerGas`는 그중 **"L2 연산비" 한 줄에만 상한을 거는 리모컨**이고, 아래 붙는 **"L1 게시비"는 상한을 걸 수 없는 자동 부과 항목**이다. 지갑이 보여주는 `maxFeePerGas`만 보고 "이만큼만 내겠지"라고 생각하면 실제 총액은 그보다 크다.

핵심 사실:

1. **두 필드의 역할 = L2 실행비 한정.** `maxPriorityFeePerGas`(팁)는 시퀀서에게 가고, base fee는 이더리움과 달리 **소각되지 않고 BaseFeeVault로 적립**된다.
2. **L1 data fee는 별개.** `GasPriceOracle` 예치 컨트랙트가 계산해 L1FeeVault로 보내며, `maxFeePerGas`로 **상한을 걸 수 없다**(공식 문서 명시).
3. **base fee 곡선 파라미터(elasticity/denominator)는 Holocene 업그레이드부터 체인별로 `SystemConfig`에서 설정** 가능하다(그 전엔 제네시스 고정 상수).
4. **priority fee 최소값**은 op-reth의 `--min-suggested-priority-fee`(기본 `1_000_000` wei)로 설정하지만, 이는 `eth_maxPriorityFeePerGas` RPC **추천 하한**이지 mempool 강제 하한이 아니다.

> ⚠️ **정본 범위 한계:** `min(...)` 선택과 vault 적립을 실제로 실행하는 것은 실행 클라이언트(op-geth / op-reth의 `op-revm`)다. `resource/optimism` 모노레포에 op-geth는 pinned Go 모듈(`go.mod`)로만 있고 소스가 없으며, op-reth의 fee-splitting은 외부 크레이트 `op-revm`에 있다. 따라서 아래의 실행-계층 서술은 EIP-1559 스펙·공식 문서를 정본으로, 온체인 컨트랙트/설정은 로컬 소스를 정본으로 삼는다.

## 핵심 동작/책임

### 총 수수료 모델 — 영수증은 2~3줄

공식 문서 기준 총액 공식([docs.optimism.io/app-developers/transactions/fees](https://docs.optimism.io/app-developers/transactions/fees)):

```
# Isthmus 이전
totalFee = gasUsed * (baseFee + priorityFee) + l1Fee

# Isthmus 이후 (operator fee 추가)
totalFee = operatorFee + gasUsed * (baseFee + priorityFee) + l1Fee
```

- **L2 실행비** `gasUsed * (baseFee + priorityFee)` — 이더리움과 gas 사용량·요금 계산이 동일. `maxFeePerGas`/`maxPriorityFeePerGas`가 지배하는 부분.
- **L1 data fee** `l1Fee` — L1 게시(DA) 비용. 자동 부과되며 `maxFeePerGas`와 무관.
- **operator fee** (Isthmus+) — 세 번째 독립 항목. `GasPriceOracle.getOperatorFee`가 계산.

### maxFeePerGas / maxPriorityFeePerGas → effective gas price (L2 실행비)

EIP-1559 표준 그대로 해석된다([eips.ethereum.org/EIPS/eip-1559](https://eips.ethereum.org/EIPS/eip-1559)):

```
priorityFee       = min(maxPriorityFeePerGas, maxFeePerGas - baseFee)
effectiveGasPrice = baseFee + priorityFee
                  = min(maxFeePerGas, baseFee + maxPriorityFeePerGas)
```

- `maxFeePerGas` = gas당 총 지불 상한, `maxPriorityFeePerGas` = 그중 시퀀서에게 줄 팁 상한.
- **팁(priority fee) → 시퀀서.** 블록 coinbase가 `SequencerFeeVault`(`0x4200...0011`) 주소로 설정돼 팁이 시퀀서 vault로 적립된다. op-reth chainspec genesis에서 `"coinbase": "0x42..0011"` 확인(`rust/op-reth/crates/chainspec/src/lib.rs:1212,1270`).
- **base fee → BaseFeeVault, 소각 안 함.** 이더리움과의 핵심 차이. 스펙: base fee는 "not burned, but add up to the Base Fee Vault"([specs.optimism.io/protocol/exec-engine.html](https://specs.optimism.io/protocol/exec-engine.html)).

### base fee 곡선 파라미터 — Holocene 이후 체인별 설정

**Holocene 이전 = 제네시스 고정 상수** (`op-chain-ops/genesis/genesis.go:34-45`):

```go
eip1559Denom       := 50   // base fee 최대 변화 분모 (pre-Canyon 기본값)
eip1559DenomCanyon := 250  // Canyon 이후 분모
eip1559Elasticity  := 10   // elasticity 기본값
```

**Holocene 이후 = `SystemConfig`에서 owner가 설정** (`packages/contracts-bedrock/src/L1/SystemConfig.sol:438-455`):

```solidity
function setEIP1559Params(uint32 _denominator, uint32 _elasticity) external onlyOwner {
    require(_denominator >= 1, "SystemConfig: denominator must be >= 1");
    require(_elasticity  >= 1, "SystemConfig: elasticity must be >= 1");
    eip1559Denominator = _denominator;
    eip1559Elasticity  = _elasticity;
    emit ConfigUpdate(VERSION, UpdateType.EIP_1559_PARAMS, data);
}
```

이 값은 `L1Block` 예치가 아니라 **L2 블록 헤더 `extraData`**로 인코딩된다(`rust/op-alloy/crates/consensus/src/eip1559.rs`): 9바이트 = `[version=0]` + `denominator(4B BE)` + `elasticity(4B BE)`, 값이 0이면 체인 기본 `BaseFeeParams`로 폴백. Jovian은 17바이트로 확장해 `min_base_fee(8B)`를 덧붙이고 version byte=1을 쓴다(`SystemConfig.minBaseFee`, `setMinBaseFee`).

> ⚠️ **불확실(코드 우선):** 일부 문서/커뮤니티 자료는 OP Mainnet elasticity를 `6`으로 표기하나, 로컬 코드 정본(`genesis.go`)의 **기본값은 elasticity 10, denom 50→250(Canyon)**이다. OP Mainnet이 실제로 쓰는 구체 값은 각 체인 config(superchain-registry)에서 명시적으로 오버라이드되며 이 모노레포에는 담겨 있지 않다. → 정본은 "제네시스 기본 = 10 / 50·250", 특정 체인 값은 superchain-registry 확인 필요.

### L1 data fee — maxFeePerGas가 못 건드리는 부분

`GasPriceOracle` 예치 컨트랙트(`0x420...000F`)가 포크별로 분기한다(`packages/contracts-bedrock/src/L2/GasPriceOracle.sol:64-71`):

```solidity
function getL1Fee(bytes memory _data) external view returns (uint256) {
    if (isFjord)        { return _getL1FeeFjord(_data); }
    else if (isEcotone) { return _getL1FeeEcotone(_data); }
    return _getL1FeeBedrock(_data);
}
```

| 업그레이드 | 방식 | 코드 |
|---|---|---|
| **Bedrock** | calldata gas × (overhead + scalar), 6 decimals | `_getL1FeeBedrock` `GasPriceOracle.sol:236` |
| **Ecotone** | EIP-4844 blob 도입 → base/blob **2개 scalar** + `blobBaseFee` | `_getL1FeeEcotone` `GasPriceOracle.sol:246` |
| **Fjord** | **FastLZ 압축 크기** 기반 선형회귀 추정(`LibZip.flzCompress`) | `_getL1FeeFjord` `GasPriceOracle.sol:257` |

Fjord(현행) 정본:

```solidity
function _fjordL1Cost(uint256 _fastLzSize) internal view returns (uint256) {
    uint256 estimatedSize = _fjordLinearRegression(_fastLzSize);
    uint256 feeScaled = baseFeeScalar()*16*l1BaseFee() + blobBaseFeeScalar()*blobBaseFee();
    return estimatedSize * feeScaled / (10 ** (DECIMALS * 2));
}
// 회귀 상수: COST_INTERCEPT=-42_585_600, COST_FASTLZ_COEF=836_500, MIN_TRANSACTION_SIZE=100
```

입력값(L1 basefee, `blobBaseFee`, scalar들)은 `L1Block` 예치(`0x420...0015`)가 매 블록 L1-attributes deposit tx로 채운다(`setL1BlockValues`/`setL1BlockValuesEcotone`/`...Isthmus`/`...Jovian`). 이 fee는 **L1FeeVault(`0x4200...001A`)로 적립**되며, 문서가 명시하듯 **"현재 L1 Data Fee의 상한을 tx가 지정하는 것은 불가능"** — `maxFeePerGas`로 못 막는다.

### priority fee 최소값 — `--min-suggested-priority-fee` (추천 하한이지 강제 아님)

op-reth `RollupArgs`가 최소 팁 추천값을 설정한다(`rust/op-reth/crates/node/src/args.rs:159-161`):

```rust
/// Minimum suggested priority fee (tip) in wei, default `1_000_000`
#[arg(long, default_value_t = 1_000_000)]
pub min_suggested_priority_fee: u64,
```

이 값은 `eth_maxPriorityFeePerGas` RPC 응답의 하한으로 gas oracle에 주입된다(`rust/op-reth/crates/rpc/src/eth/mod.rs:343-350`):

```rust
async fn suggested_priority_fee(&self) -> Result<U256, Self::Error> {
    self.inner.eth_api.gas_oracle()
        .op_suggest_tip_cap(self.inner.min_suggested_priority_fee)  // ← 하한 주입
        .await
        .map_err(Into::into)
}
```

gas oracle이 최근 블록 tip을 관찰해 추천값을 계산하되, 결과가 하한보다 낮으면 이 값으로 끌어올린다. **성격 구분이 중요**하다: 이것은 지갑에게 "팁을 최소 이만큼 넣으라"고 **제안**하는 값이지, 이보다 낮은 팁 tx를 mempool에서 **거부하는 강제 스위치가 아니다**. 주차장의 "권장 요금 안내판"이지 차단기가 아니다. 실제로 낮은 팁 tx를 거부/미포함시키는 강제 하한은 txpool 수용 기준(→ [op-reth --txpool.nolocals](op-reth-txpool-nolocals.md)의 price 면제 맥락)과 블록 빌더(op-revm, 외부 크레이트)에 있으며, 로컬 소스로 정본 확인이 제한적이다.

## 주요 인터페이스/필드

### Fee Vault 예치 컨트랙트 3종 (`packages/contracts-bedrock/src/L2/`)

| Vault | 예치 주소 | 담는 것 | 파일 |
|---|---|---|---|
| **BaseFeeVault** | `0x4200...0019` | L2 base fee (소각 대신 적립) | `BaseFeeVault.sol` |
| **SequencerFeeVault** | `0x4200...0011` | priority fee(팁), 블록 coinbase | `SequencerFeeVault.sol` |
| **L1FeeVault** | `0x4200...001A` | L1 data fee 부분 | `L1FeeVault.sol` |

모두 공용 `FeeVault` 베이스를 상속하며 `withdraw()`로 `minWithdrawalAmount` 도달 시 recipient(L2 또는 L1 bridged)로 인출한다.

### priority fee 최소값 설정 요약

| 항목 | 값/위치 |
|---|---|
| 설정 위치 | op-reth `RollupArgs.min_suggested_priority_fee` (`rust/op-reth/crates/node/src/args.rs:159`) |
| CLI 플래그 | `--min-suggested-priority-fee` |
| 기본값 | `1_000_000` wei (0.001 gwei) |
| 성격 | `eth_maxPriorityFeePerGas` RPC **추천 하한** (mempool 강제 아님) |
| 소비처 | `op_suggest_tip_cap(min_suggested_priority_fee)` (`rust/op-reth/crates/rpc/src/eth/mod.rs:347`) |

### EIP-1559 파라미터 저장/설정 (`SystemConfig.sol`)

| 필드/함수 | 위치 | 의미 |
|---|---|---|
| `eip1559Denominator` | `SystemConfig.sol:134` | base fee 최대 변화 분모 (uint32) |
| `eip1559Elasticity` | `SystemConfig.sol:138` | elasticity multiplier (uint32) |
| `setEIP1559Params` | `SystemConfig.sol:438` | owner 전용 설정, `EIP_1559_PARAMS` ConfigUpdate emit |
| `minBaseFee` / `setMinBaseFee` | `SystemConfig.sol:156,460` | Jovian 최소 base fee |

## 관련 페이지

- [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth-txpool-nolocals.md) — 이 페이지의 "priority fee 추천 하한"과 대비되는 txpool의 **강제** price 면제/하한 계층. local tx가 최소 수수료 기준을 우회하는 메커니즘.
- [OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황](observability-grafana-integration.md) — 동일 op-reth 클라이언트의 다른 운영 설정 계열.

## 출처

**코드 정본 (`resource/optimism` @ `aaeb6c0154`, CodeGraph 조회):**
- `packages/contracts-bedrock/src/L2/GasPriceOracle.sol:64,236,246,257` — L1 fee 포크별 공식(Bedrock/Ecotone/Fjord), operator fee
- `packages/contracts-bedrock/src/L1/SystemConfig.sol:134-138,438-455,156,460` — Holocene EIP-1559 params + Jovian minBaseFee 설정
- `packages/contracts-bedrock/src/L2/{BaseFeeVault,SequencerFeeVault,L1FeeVault}.sol` — fee vault 라우팅
- `op-chain-ops/genesis/genesis.go:34-86` — 제네시스 EIP-1559 기본 상수(elasticity 10, denom 50/250)
- `rust/op-alloy/crates/consensus/src/eip1559.rs` — Holocene/Jovian extraData 인코딩
- `rust/op-reth/crates/node/src/args.rs:159-161` — `--min-suggested-priority-fee` (기본 1,000,000 wei)
- `rust/op-reth/crates/rpc/src/eth/mod.rs:343-350` — `op_suggest_tip_cap` 하한 주입
- `rust/op-reth/crates/chainspec/src/lib.rs:1212,1270` — coinbase = SequencerFeeVault
- `go.mod` — op-geth pinned 모듈(실행 클라이언트 소스 부재 근거)

**문서:**
- [docs.optimism.io/app-developers/transactions/fees](https://docs.optimism.io/app-developers/transactions/fees) — 총 수수료 모델, L1 fee 상한 불가, operator fee
- [specs.optimism.io/protocol/exec-engine.html](https://specs.optimism.io/protocol/exec-engine.html) — base fee 미소각·vault, 시퀀서 우선순위
- [specs.optimism.io/protocol/holocene/exec-engine.html](https://specs.optimism.io/protocol/holocene/exec-engine.html) · [system-config.html](https://specs.optimism.io/protocol/system-config.html) — Holocene extraData/SystemConfig
- [eips.ethereum.org/EIPS/eip-1559](https://eips.ethereum.org/EIPS/eip-1559) — effectiveGasPrice 공식
