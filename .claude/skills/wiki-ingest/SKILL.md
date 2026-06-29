---
name: wiki-ingest
description: "input을 OKF 기반 LLM Wiki 페이지로 정리하고 index/log/교차링크를 갱신한다."
triggers: ["ingest", "위키에 추가", "wiki ingest", "위키 ingest", "위키로 정리"]
---

# wiki-ingest

/wiki-ingest는 분석·조사한 input을 Google OKF(Open Knowledge Format) 기반 LLM Wiki(`./wiki`)에 기록하는 스킬이다. input을 위키 구조에 맞는 페이지로 정리하고, 담긴 출처·인용은 그대로 보존한다.

이 스킬은 **2단계 Chain-of-Thought**로 동작한다: 먼저 **Step 1(분석)**에서 무엇을 어디에 쓸지 계획만 세우고, 그다음 **Step 2(생성)**에서 그 계획대로만 파일을 쓴다. 분석 없이 바로 파일을 쓰지 않는다 — 분석과 생성을 한 번에 하면 중복을 뒤늦게 발견하거나 교차링크를 빠뜨리기 쉽다.

---

## Step 1 — 분석

input을 읽고, 아래 항목을 채운 **분석 결과**를 먼저 산출한다. 이 단계에서는 위키 파일을 만들거나 고치지 않는다.

1. **핵심 엔티티/개념** — input에서 페이지가 될 만한 대상을 나열한다. (예: `OptimismPortal`, `depositTransaction`, `fault-proofs`)
2. **type 결정** — 각 대상의 type을 정한다(`Contract`/`Component`/`Concept`/`Spec`/`Runbook`).
3. **기존 위키와의 연결 (중복 확인)** — 새로 쓰기 전에 같은·유사 주제가 이미 있는지 확인한다.
   - `wiki/index.md`를 읽고, `graphify-out/`가 있으면 `graphify query "<주제>"` / `graphify explain "<개념>"`로 유사·중복 페이지를 탐색한다.
   - 대상별로 셋 중 하나로 분류한다:
     - **신규** — 유사 페이지 없음 → 새 페이지 작성 예정.
     - **보강** — 유사 페이지 있고, input에 빠진 사실·세부·새 출처가 있음 → 기존 페이지에 통합 예정.
     - **스킵** — 유사 페이지 있고 이미 다 담겨 있음 → 손대지 않음(마무리 보고에만 기록).
4. **역방향 링크 대상** — 이번 페이지와 관련된 **기존 페이지** 목록. `graphify-out/`가 있으면 `graphify path "<A>" "<B>"`로 관계 경로를 확인해 근거로 삼는다.
5. **모순/충돌 후보** — input이 기존 페이지의 서술과 상충하는 부분이 있으면 여기 명시한다. **모순은 ingest 시점에 flag한다**(query까지 묻어두지 않는다). silent overwrite 금지 — 충돌은 마무리 보고에 남기고, 필요하면 lint의 contradiction 점검으로 넘긴다.
6. **sources[]** — 각 사실 주장에 붙일 정확한 원본 경로/인용(`resource/` 기준 상대경로, 외부만 있으면 URL).

> 산출한 분석은 Step 2의 유일한 입력이다. Step 2는 이 계획에 없는 파일을 건드리지 않는다.

---

## Step 2 — 생성

분석 결과를 입력으로 받아, 영향받는 파일을 **모두 함께** 갱신한다.

### 페이지 작성 (OKF 형식)
- 프론트매터를 스키마대로 채운다(필수 `type` + 가능한 OKF 5필드 + 해당 시 op-stack 확장 키). 컨트랙트/컴포넌트는 `source_commit`을 기록한다(`git -C resource/optimism rev-parse --short HEAD`).
- 본문 구조: `## 개요` → `## 핵심 동작/책임` → `## 주요 인터페이스/필드` → `## 관련 페이지`.
- Step 1의 sources[]를 사실 주장에 붙인다.
- **보강** 대상이면 새로 만들지 않고 기존 페이지에 통합한 뒤, 충돌 서술이 없는지 확인하고 `timestamp`(해당 시 `source_commit`)를 갱신한다.

### index 갱신
- `wiki/index.md`의 해당 type 섹션에 `- [제목](상대경로) — 한줄요약`을 추가/갱신한다.
- `_아직 없음_` 플레이스홀더는 첫 항목 추가 시 제거한다.

### 교차링크
- Step 1이 지목한 **역방향 링크 대상** 기존 페이지들에 이번 페이지로의 링크를 추가한다(한 번에 여러 파일 OK). 관계의 종류는 산문으로 표현한다("…에 의존한다", "…를 배포한다").

### log 갱신
- `wiki/log.md` 최상단(헤더 아래)에 한 줄 추가한다: `## [YYYY-MM-DD] ingest | <대상> → <생성/갱신한 페이지들>`.
- 날짜는 `date +%F`로 확인한다.

---

## 마무리 보고
- 생성/갱신한 페이지 목록, 추가한 교차링크, Step 1에서 flag한 모순 후보, 스킵한 대상, 다음에 ingest하면 좋을 후보를 짧게 보고한다.

## 반드시 해야 할 일
하나의 ingest를 끝낼 때, 영향받는 파일을 모두 함께 갱신해 정합성을 유지한다(새 페이지 + 관련 페이지 역방향 링크 + index + log). 일부만 반영된 상태로 끝내지 않는다. 작업 후 `python3 scripts/lint_wiki.py wiki/`(또는 `make lint`)로 정합성을 점검할 수 있다.

## Tool usage

graphify (`graphify-out/`가 있을 때 사용):
- `graphify query`/`explain` — **Step 1 중복 확인** 시 유사·중복 페이지 탐색.
- `graphify path "<A>" "<B>"` — **Step 1 역방향 링크 대상** 결정 시 두 페이지의 관계 확인.
- `graphify update .` — Step 2에서 페이지 작성·갱신 후 그래프 최신화.
