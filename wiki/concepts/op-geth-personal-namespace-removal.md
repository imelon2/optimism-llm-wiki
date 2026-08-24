---
type: Concept
title: op-geth personal 네임스페이스 제거 (personal_listAccounts / personal_listWallets)
description: geth personal 네임스페이스의 계정·지갑 조회 메서드 두 개의 반환 형태와 차이(평탄한 주소 배열 vs 백엔드 컨테이너+잠금상태), op-geth 버전별 존재 여부(v1.101311에서는 --rpc.enabledeprecatedpersonal로만 활성, v1.101503 이후 완전 삭제)와 제거 이유(비밀번호 RPC 전송·서버측 해제 키), eth_accounts·clef·클라이언트 사이드 서명이라는 대체 경로
resource: resource/optimism/go.mod
tags: [op-stack, l2, reth]
timestamp: 2026-08-24T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# op-geth personal 네임스페이스 제거 (personal_listAccounts / personal_listWallets)

## 개요

`personal_*`는 go-ethereum의 **노드 로컬 키 관리 API**다. 체인 프로토콜과 무관하며, 그 노드가 들고 있는 서명 키를 다루는 운영용 메서드 모음이다.

**현재 OP Stack에서는 사용할 수 없다.** 이 저장소가 고정한 op-geth에는 `PersonalAccountAPI` 자체가 존재하지 않는다.

## 핵심 동작/책임

### 두 메서드의 차이

**`personal_listAccounts` → `[]address`**

노드의 account manager가 서명할 수 있는 모든 주소를 평탄한 배열로 반환한다.

```go
// internal/ethapi/api.go:302 (op-geth v1.101311.0-rc.1)
func (s *PersonalAccountAPI) ListAccounts() []common.Address {
	return s.am.Accounts()
}
```

```json
["0xd0a2...", "0x1f5b..."]
```

**`personal_listWallets` → `[]rawWallet`**

같은 키를 **지갑(백엔드 컨테이너) 단위**로, 상태까지 붙여 반환한다.

```go
// internal/ethapi/api.go:308-332
type rawWallet struct {
	URL      string             `json:"url"`
	Status   string             `json:"status"`
	Failure  string             `json:"failure,omitempty"`
	Accounts []accounts.Account `json:"accounts,omitempty"`
}
```

여기서 wallet은 키 하나가 아니라 **키를 담고 있는 백엔드 하나**다 — keystore 파일, Ledger/Trezor USB 장치, 스마트카드 등. `url` 스킴으로 출처가 구분되고 `status`로 `Unlocked`/`Locked`/`Awaiting PIN` 여부가 드러난다.

**관계**: `listAccounts`는 `listWallets` 결과에서 `accounts`만 뽑아 펼친 것이다(`accounts/manager.go:213-224`가 동일하게 순회). 주소만 필요하면 전자, 하드웨어 지갑 연결·잠금·백엔드 오류를 알아야 하면 후자다.

### 버전별 존재 여부

| op-geth 버전 | `PersonalAccountAPI` |
|--------------|----------------------|
| `v1.101311.0-rc.1` (geth 1.13.x) | 존재하나 **기본 비활성** |
| `v1.101503.1` 이후 ~ `v1.101702.3-rc.4` | **완전 삭제** |
| op-reth | 구현한 적 없음 |

이 저장소가 고정한 버전:

```
// resource/optimism/go.mod:256
replace github.com/ethereum/go-ethereum => github.com/ethereum-optimism/op-geth v1.101702.3-rc.4
```

마지막으로 남아 있던 1.13 시절에도 기본으로 꺼져 있었고 `--rpc.enabledeprecatedpersonal`로만 켤 수 있었다.

```go
// node/node.go:383-390 (op-geth v1.101311.0-rc.1)
if api.Namespace == "personal" {
	if n.config.EnablePersonal {
		log.Warn("Deprecated personal namespace activated")
	} else {
		continue   // 등록하지 않음
	}
}
```

### 제거 이유

네임스페이스의 나머지 메서드를 보면 분명하다 — `UnlockAccount`, `SendTransaction(args, passwd)`, `ImportRawKey`, `Sign`. **비밀번호를 JSON-RPC로 전송하고, 노드 프로세스가 해제된 키를 보유하는** 구조다. RPC 포트가 노출되면 자금이 그대로 탈취된다.

## 주요 인터페이스/필드

### 대체 경로

| 필요 | 대체 |
|------|------|
| 주소 목록 | **`eth_accounts`** — 현재도 존재 (`internal/ethapi/api.go:295`, `EthereumAccountAPI.Accounts()`) |
| 서명 | **clef** 등 외부 서명자로 분리 |
| 트랜잭션 전송 | **클라이언트 사이드 서명 + `eth_sendRawTransaction`** (프로덕션 표준) |
| 지갑 상태 조회 | **없음** — 하드웨어 지갑 상태 조회는 노드의 책임이 아니라는 판단으로 기능 자체가 삭제 |

### 확인 방법

특정 노드에서 사용 가능한지는 직접 호출해 보면 된다.

```bash
curl -s -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":1,"method":"personal_listAccounts","params":[]}' \
  <el-rpc-url>
# 제거된 버전: {"error":{"code":-32601,"message":"the method personal_listAccounts does not exist/is not available"}}
```

## 관련 페이지

- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](op-stack-block-production.md) — 시퀀서가 서명하는 대상은 사용자 트랜잭션이 아니라 P2P gossip 페이로드이며, 그 키는 `--p2p.sequencer.key` 등 op-node 측 설정으로 관리된다(EL의 personal 네임스페이스와 무관).
- [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth-txpool-nolocals.md) — `eth_sendRawTransaction`이 External origin으로 취급되어 local 면제 대상이 아니라는 점. 대체 경로 3의 실제 동작 맥락.
