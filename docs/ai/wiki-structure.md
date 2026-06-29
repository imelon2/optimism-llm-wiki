# Wiki Structure & Page Schema

OP Stack LLM Wiki의 구조와 페이지 작성 표준.

## 디렉토리 & type

위키 페이지(OKF "Concept")는 type별 디렉토리에 둔다.

| type | 디렉토리 | 의미 |
|------|----------|------|
| `Concept` | `wiki/concepts/` | 프로토콜 개념/메커니즘 (fault proofs, derivation, deposits...) |
| `Contract` | `wiki/contracts/` | 온체인 스마트 컨트랙트 |
| `Component` | `wiki/components/` | 오프체인 서비스/바이너리 (op-node, op-batcher...) |
| `Spec` | `wiki/specs/` | 스펙 요약 |
| `Runbook` | `wiki/runbooks/` | 운영 절차/인시던트 대응 |
| `RFC` | `wiki/concepts/` | 설계 제안 (tag `rfc`로 구분) |

- **Concept ID** = 경로에서 `.md` 제거. 예: `wiki/contracts/OptimismPortal.md` → `contracts/OptimismPortal`.
- 파일명: 컨트랙트/컴포넌트는 원문 식별자(`OptimismPortal.md`), 개념은 kebab-case(`fault-proofs.md`).
- `index.md`, `log.md`는 예약 파일이다.

## 탐색/관리 파일

- `wiki/index.md` — 전체 카탈로그. type별 섹션에 `- [제목](상대경로) — 한줄요약` 형식.
- `wiki/log.md` — append-only 변경 이력. 최신 항목이 헤더 아래 최상단. 형식 `## [YYYY-MM-DD] <op> | <대상>`.

## 프론트매터 (OKF + op-stack 확장)

페이지는 `---`로 구분된 YAML 프론트매터로 시작한다.

```yaml
---
# ── OKF 표준 ──
type: Contract                 # 위 type vocab 중 하나
title: OptimismPortal          # 표시 이름 (컨트랙트/컴포넌트는 원문 식별자)
description: L1→L2 예치와 L2→L1 출금 증명을 처리하는 핵심 브릿지 컨트랙트  # 한 문장
resource: resource/optimism/packages/contracts-bedrock/src/L1/OptimismPortal2.sol  # 원본 경로/URL
tags: [op-stack, bridge, withdrawals, l1]
timestamp: 2026-06-26T00:00:00Z   # ISO-8601, 마지막 수정 시각
# ── op-stack 확장 (해당될 때만) ──
chain: l1                      # l1 | l2
audit_status: audited          # audited | unaudited | in-review
version: bedrock               # 프로토콜 버전/업그레이드 라인
source_commit: <git-sha>       # 요약 시점의 resource submodule HEAD (stale 추적용)
---
```

- `type`이 유일한 필수 필드. 나머지 OKF 5필드(title/description/resource/tags/timestamp)는 가능한 한 채운다.
- `resource`는 `resource/` 기준 상대경로를 쓰고, 외부만 있으면 URL을 쓴다.
- `source_commit`은 stale 추적의 핵심 키로, 컨트랙트/컴포넌트 페이지에 기록한다
  (`git -C resource/optimism rev-parse --short HEAD`).
- OKF는 임의 키 확장을 허용한다.

## tags

`op-stack`을 기본 포함. 도메인 축:
`bridge`, `fault-proofs`, `derivation`, `batcher`, `proposer`, `sequencer`, `withdrawals`, `deposits`, `governance`, `da`(data availability), `p2p`(networking), `reth`(EL client), `l1`, `l2`, `rfc`.
분류체계는 등장 빈도에 따라 확장된다.

## 교차링크

- 표준 마크다운 상대 링크를 쓴다 (GitHub에서 렌더). 예: `[FaultDisputeGame](../contracts/FaultDisputeGame.md)`.
- 링크는 방향성 관계를 나타내며, 관계의 종류는 산문으로 표현한다("…에 의존한다", "…를 배포한다").
- 본문 끝 `## 관련 페이지`에 핵심 링크를 모은다.

## 본문 스타일

- **언어**: 산문은 한국어, 식별자·코드·고유명사·함수명은 영어.
- **길이**: 핵심 위주. 길어지면(>대략 400줄) 분할하고 링크로 연결.
- **인용**: 사실 주장에 출처 경로 표기 (예: `(resource/optimism/.../OptimismPortal2.sol)`).
- **구조**: `## 개요` → `## 핵심 동작/책임` → `## 주요 인터페이스/필드` → `## 관련 페이지`.
- **근거**: `resource/` 소스(코드·natspec·README)에서 확인된 내용 위주. 불확실하면 명시.

## 동작 특성

- 검색은 `index.md`를 먼저 읽고 관련 페이지로 드릴다운하는 방식이다 (벡터 임베딩 미사용).
- 모든 페이지는 프론트매터 `type`을 가진다.
- ingest나 페이지 수정은 `index.md`와 `log.md` 갱신을 동반한다.
