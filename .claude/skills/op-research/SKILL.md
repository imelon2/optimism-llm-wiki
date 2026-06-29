---
name: op-research
description: "OP Stack / Optimism을 조사·분석·심층 탐구한다. 질문을 명확화한 뒤 문서/코드 2-트랙으로 리서치하고 출처를 인용해 종합 보고한다."
triggers: ["op-research", "옵티미즘 리서치", "op stack 분석", "옵스택 조사", "research optimism", "deep dive op-stack"]
tools: Read, Bash, Grep, Glob, WebSearch, WebFetch, Task, TodoWrite, AskUserQuestion, mcp__codegraph__codegraph_explore
---

# op-research

/op-research skill applies open deep-research methodology to conduct comprehensive research on OP Stack / Optimism topics.

---

## Step 1 — 질문 명확화 (Clarify & Scope)

답을 찾기 전에 **무엇을 리서치할지** 확정한다. 모호하면 추측하지 말고 `AskUserQuestion`으로 1회 묻는다. 확정해야 할 축:

1. **범위(scope)** — `문서` / `코드` / `둘 다`. (아래 라우팅 규칙으로 1차 판단하고, 애매하면 묻는다.)
2. **대상(target)** — 어떤 모듈/컨트랙트/개념인가. (예: `op-node/rollup/derive`, `OptimismPortal2`, fault-proofs)
3. **깊이(depth)** — 개요(overview) / 심층(deep-dive). 심층이면 단일 모듈로 좁힌다.

확정한 범위·대상·깊이를 한 줄로 요약하고, 리서치 항목이 여러 개면 `TodoWrite`로 트랙다운한다.

## Step 2 — 리서치 계획 (Plan)

확정된 질문을 **트랙별 하위 질문**으로 분해한다. 독립적인 하위 질문이 2개 이상이면 `Task`로 병렬 fan-out 할 수 있다.

## Step 3 — 실행 (Execute)

트랙별로 도구를 달리 적용한다. **위키 트랙을 가장 먼저 돈다** — 이미 조사·정리된 내용이 있으면 외부 리서치를 줄이고 그 위에 보강할 수 있다.

### 위키 트랙
- 외부 조사 전에 로컬 위키(`wiki/`)에 관련 페이지가 있는지 `/wiki-query` 스킬로 확인한다.
- 위키에서 찾은 내용은 **출발점이자 검증 대상**이다 — 위키는 과거 시점 스냅샷이라 stale할 수 있으므로, 사실 주장은 아래 문서·코드 트랙으로 재확인하고 충돌 시 코드를 정본으로 삼는다.

### 문서 트랙
- 문서를 리서치해야 하는 경우 `WebSearch`/`WebFetch`로 조사한다(공식 docs·specs·블로그·EIP 우선, 출처 신뢰도 확인).
- 문서는 최신 코드보다 뒤처질 수 있다 — **사실 주장은 코드 트랙으로 교차검증**한다.

### 코드 트랙
- 코드를 분석/리서치해야 하는 경우 CodeGraph를 사용한다. MCP `codegraph_explore`를 우선 쓰고, 없으면 shell `codegraph explore "<symbol/question>"`로 폴백한다.
- 둘 다 없으면 Grep/Find를 사용한다.
- **코드가 동작의 정본**이다. 문서와 충돌하면 코드를 신뢰하고, 충돌을 보고에 명시한다.


## Step 4 — 교차검증 (Verify)

종합 전에 핵심 주장을 적대적으로 검증한다.
- **문서 ↔ 코드 대조**: 문서가 말한 동작이 실제 코드와 일치하는가. 불일치는 버리지 말고 **코드 우선 + 불일치 명시**.
- 근거가 한 소스뿐이고 확신이 낮으면, 그 불확실성을 보고에 표시한다(추측을 사실처럼 쓰지 않는다).

## Step 5 — 종합 보고 (Synthesize)

1. **구조** — `## 요약`(핵심 결론 먼저) → `## 상세`(트랙별 근거) → `## 미해결/불확실`(있으면) → `## 출처`.
2. **포맷** — 코드는 언어 지정 트리플 백틱. 응답 전체를 ```markdown 펜스로 감싸지 않는다.

### 이해 가능성 원칙

- **한 줄 요약 먼저** — `## 요약` 맨 앞에 전문용어 없이 결론을 한 문장으로. 근거·메커니즘은 그다음.
- **비유로 한 번 더** — 핵심 메커니즘은 코드/스펙 용어로 한 번, 일상어·비유로 한 번 더 푼다.
- **용어 풀기** — 약어/고유명사는 첫 등장 시 괄호로 뜻을 단다(고유명사 원문은 보존).

---

## 반드시 해야 할 일
- **명확화 없이 리서치를 시작하지 않는다.** 범위(문서/코드)·대상·깊이가 불명확하면 `AskUserQuestion`으로 먼저 확정한다.
- **출처 없는 사실 주장을 하지 않는다.** 문서와 코드가 충돌하면 코드를 정본으로 삼고 충돌을 명시한다.

## Tool usage
- `/wiki-query` — 위키 트랙. `/wiki-query "<주제/질문>"`로 기존 위키 페이지를 검색해 출처와 함께 답을 받는다(index 드릴다운은 스킬이 처리).
- `WebSearch` / `WebFetch` — 문서 트랙. 문서 리서치가 필요할 때 조사(공식 출처 우선).
- CodeGraph — 코드 트랙. MCP `codegraph_explore` 우선, 없으면 shell `codegraph explore`, 둘 다 없으면 Grep/Find.
- context7 `resolve-library-id` → `query-docs` — 외부 의존 라이브러리/프레임워크 문서.