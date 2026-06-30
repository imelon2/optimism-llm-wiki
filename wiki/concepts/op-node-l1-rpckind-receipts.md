---
type: Concept
title: op-node l1.rpckind & L1 Receipts Fetching 최적화
description: op-node의 --l1.rpckind 옵션이 L1 RPC 공급자 종류를 힌트로 받아 블록 영수증(receipts) 조회 메서드를 비용 최적으로 선택·강등·복구하는 메커니즘과 alchemy 설정의 효과
resource: resource/optimism/op-service/sources/receipts_rpc.go
tags: [op-stack, l1]
timestamp: 2026-06-30T00:00:00Z
chain: l1
version: bedrock
source_commit: aaeb6c0154
---

# op-node l1.rpckind & L1 Receipts Fetching 최적화

## 개요

`--l1.rpckind`는 op-node에게 "내 L1 RPC 공급자가 어떤 종류인지" 힌트를 주는 옵션이다. op-node는 이 힌트로 그 공급자에 가장 저렴하고 빠른 **블록 영수증(receipts) 조회 메서드**를 골라 RPC 비용을 줄인다. 비유하면 "이 동네는 쿠팡이 빠르고 저 동네는 우체국이 싸다"를 미리 알려줘 가장 효율적인 배송사를 고르게 하는 것과 같다.

핵심 사실:

1. **영향 범위는 L1 영수증 조회 방식 선택뿐이다.** 합의·검증 로직 자체는 바꾸지 않는다. 잘못 설정해도 비용/속도만 손해이고 안전성(영수증 해시 검증)은 동일하다 (`resource/optimism/op-service/sources/receipts_rpc.go:108`).
2. **플래그명** `--l1.rpckind`, **환경변수** `OP_NODE_L1_RPC_KIND`, **기본값** `standard` (`resource/optimism/op-node/flags/flags.go:163-173`).
3. **유효값** 10종: `alchemy`, `quicknode`, `infura`, `parity`, `nethermind`, `debug_geth`, `erigon`, `basic`, `any`, `standard`. 목록에 없는 값은 노드 기동 실패 (`resource/optimism/op-service/sources/receipts_rpc.go:162-211`, `eth_client.go:116`).
4. **자가 교정** 장치가 있어, 설정이 실제 공급자와 안 맞아 메서드가 실패하면 자동으로 다른 방식으로 강등(fallback)하고 주기적으로 복구한다 (`receipts_rpc.go:120-143`).

## 핵심 동작/책임

### 데이터 흐름 (op-node → op-service)

CLI 입력은 그대로 영수증 조회기(`RPCReceiptsFetcher`)까지 전달된다.

```
--l1.rpckind (CLI)
  └─ service.go:154   L1RPCKind = RPCProviderKind(lower(flag))   // 소문자화
       └─ L1ClientConfig.RPCProviderKind        (l1_client.go:39)
            └─ EthClientConfig.RPCProviderKind   (eth_client.go:67)
                 └─ RPCReceiptsFetcher.provKind  (receipts_rpc.go:39)
```

`eth_client.go:116`의 `ValidRPCProviderKind` 검증을 통과하지 못하면 `unknown rpc provider kind` 에러로 기동이 실패한다.

### kind → "사용 가능 메서드 집합" 매핑

`AvailableReceiptsFetchingMethods(kind)` (`receipts_rpc.go:324`)가 kind마다 시도 후보(비트필드)를 다르게 켠다. `eth_getTransactionReceipt`(batch)는 모든 경우의 최후 fallback이다.

| kind | 켜지는 receipt 조회 메서드 |
|------|-----------------------------|
| `alchemy` | `alchemy_getTransactionReceipts`, `eth_getBlockReceipts`, batch |
| `quicknode` | `debug_getRawReceipts`, `eth_getBlockReceipts`, batch |
| `infura` | `eth_getBlockReceipts`, batch |
| `parity` | `parity_getBlockReceipts`, batch |
| `nethermind` | `parity_getBlockReceipts`, batch |
| `debug_geth` | `debug_getRawReceipts`, batch |
| `erigon` | `erigon_getBlockReceiptsByBlockHash`, batch |
| `basic` | batch만 (가장 보수적) |
| `any` | 위의 거의 모든 최적화 메서드 전부 |
| `standard` (기본) | `eth_getBlockReceipts`, batch |
| (그 외/default) | batch만 |

`standard`가 기본인 이유: 표준화된 `eth_getBlockReceipts`(execution-apis PR #438로 표준화, Geth 등 채택)는 대부분 공급자에서 안전히 동작하므로 공급자를 모를 때의 합리적 기본값이다.

### 실제 호출 시 최적 메서드 선택

매 블록 조회 시 `PickBestReceiptsFetchingMethod`(`receipts_rpc.go:357`)가 **kind + 현재 가용 메서드 + 트랜잭션 수**로 한 가지를 고른다. "정액 메서드가 tx별 batch보다 싸지는 손익분기점"을 계산하는 비용 모델이다. batch는 tx당 15 CU(Alchemy 기준)이므로, 정액 N CU 메서드는 `N/15` tx부터 이득이다.

### 런타임 자동 강등(fallback)과 복구

- **강등:** 선택 메서드가 "지원 안 함" 류 에러를 내면 `OnReceiptsMethodErr`(`receipts_rpc.go:133`)가 그 비트를 끄고(`availableReceiptMethods &^= m`) 다음 후보로 폴백하며 경고 로그를 남긴다.
- **주기적 복구:** `PickReceiptsMethod`(`receipts_rpc.go:120`)는 `methodResetDuration`마다 가용 집합을 kind 기준으로 리셋한다. 이때 집합이 달라져 있으면 `"resetting back RPC preferences, please review RPC provider kind setting"` 경고를 띄운다 → **이 로그가 보이면 `l1.rpckind`가 실제 공급자와 안 맞는다는 신호다.**

## 주요 인터페이스/필드

### 예시: `alchemy` 설정의 효과

`alchemy`는 Alchemy 전용 `alchemy_getTransactionReceipts`(블록 전체를 **250 CU 정액**)를 후보로 추가한다. Alchemy 분기 선택 로직 (`receipts_rpc.go:360`):

```go
if kind == RPCKindAlchemy {
    if available&AlchemyGetTransactionReceipts != 0 && txCount > 250/15 {  // tx ≥ 17 → 정액
        return AlchemyGetTransactionReceipts
    }
    if available&EthGetBlockReceipts != 0 && txCount > 500/15 {            // tx ≥ 34 (강등 시에만 도달)
        return EthGetBlockReceipts
    }
    return EthGetTransactionReceiptBatch                                    // 그 외 tx별 batch
}
```

블록 크기별 선택과 비용(정상 상태):

| 블록 tx 수 | 선택 메서드 | 비용 | batch였다면 |
|---|---|---|---|
| 16개 | batch | 240 CU | 240 CU (정액 250보다 쌈) |
| 17개 | `alchemy_getTransactionReceipts` | 250 CU | 255 CU |
| 50개 | `alchemy_getTransactionReceipts` | 250 CU | 750 CU |
| 200개 | `alchemy_getTransactionReceipts` | 250 CU | 3,000 CU (**12배**) |

같은 200-tx 블록을 `standard`(기본)로 두면 `eth_getBlockReceipts`(500 CU)를 써 **2배** 비용이 든다. 즉 Alchemy 노드를 쓰면서 `alchemy`로 맞추면 가장 싼 창구(250 CU)가 열린다.

Alchemy 특이 처리: 응답이 배열이 아니라 `{"receipts":[...]}` 객체로 래핑되므로 op-node가 `receiptsWrapper`로 언래핑한다 (`receipts_rpc.go:79-82`). 다른 메서드엔 없는 처리다.

### kind별 권장

| 상황 | 권장 kind |
|------|-----------|
| Alchemy 사용 | `alchemy` (전용 250 CU 메서드 활용) |
| 표준 노드(Geth/Reth/Besu 등)·공급자 불명 | `standard` (기본 유지) |
| 자체 Geth 풀노드 + 빠른 동기화 | `debug_geth` (무료 `debug_getRawReceipts`) |
| QuickNode | `quicknode` |
| Erigon | `erigon` |

`any`는 호환성은 좋지만 실패-강등 과정에서 불필요한 호출이 생길 수 있어, 공급자를 알면 명시 지정을 권장한다. 운영 중 "resetting back RPC preferences" 경고가 뜨면 설정을 실제 공급자에 맞춘다.

> 근거: 로컬 `resource/optimism` 클론(`source_commit: aaeb6c0154`) 코드 기준. CU 비용 수치는 `receipts_rpc.go:240-303`의 코드 주석 출처이며, 공급자별 최신 과금은 각 공급자 문서와 교차 검증을 권장한다.

## 관련 페이지

- (아직 없음) 향후 `op-node` Component 페이지가 생기면 본 L1 RPC 옵션을 교차링크한다. L1 클라이언트(`op-service/sources/l1_client.go`)·EthClient 설정 관련 Concept 페이지가 추가되면 데이터 흐름을 연결한다.
