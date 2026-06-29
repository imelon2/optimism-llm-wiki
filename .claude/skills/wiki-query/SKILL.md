---
name: wiki-query
description: "LLM Wiki를 검색해 출처 인용과 함께 답하고, 가치 있는 답은 새 페이지로 환류한다."
triggers: ["query", "위키에서 찾아", "위키에서 검색", "위키 기반", "위키에 뭐라고", "wiki query"]
---

# wiki-query

/wiki-query는 LLM Wiki(`./wiki`)를 읽어 사용자 질문에 답하는 스킬이다. ingest로 **이미 컴파일된 위키 페이지**를 근거로 답한다. 가치 있는 답은 다시 위키로 환류(file-back)해 위키를 누적시킨다.

---

## Step 1 — 검색 (index 드릴다운)

1. **항상 `wiki/index.md`를 먼저 읽는다.** type별 섹션에서 질문과 관련된 페이지 후보를 고른다.
2. 후보 페이지를 읽고, 본문의 `## 관련 페이지` 링크와 교차링크를 따라 **1–2 hop 확장**한다(직접 관련 페이지 → 그 페이지가 의존/참조하는 페이지).
3. `graphify-out/`가 있으면 `graphify query "<질문>"` / `graphify path "<A>" "<B>"`로 관련 페이지·관계를 보강 탐색한다.
4. 답에 실제로 쓸 페이지만 추린다. 관련 없는 페이지는 컨텍스트에 넣지 않는다.

## Step 2 — 컨텍스트 조립 (provenance 보존)

추린 페이지를 아래 형식으로 묶어 답변의 근거 컨텍스트로 삼는다. 각 페이지에 **File Path / Content** 메타데이터를 붙여 출처 추적을 가능하게 한다.

```
<CONTEXTS>
  File Path: wiki/contracts/OptimismPortal.md
  Content: <해당 페이지 본문 발췌>
  ---
  File Path: wiki/concepts/deposits.md
  Content: <해당 페이지 본문 발췌>
</CONTEXTS>
```

## Step 3 — 응답 (출력 규칙)

DeepWiki-Open `RAG_SYSTEM_PROMPT`에서 차용한 출력 규칙을 지킨다:

1. **언어 일치** — 사용자 질문의 언어를 감지해 같은 언어로 답한다("Respond in the SAME language").
2. **출처 강제** — 모든 사실 주장에 근거 위키 페이지 경로를 인용한다. 답 끝에 근거 페이지를 `## 출처` 섹션으로 모은다(예: `- wiki/contracts/OptimismPortal.md`).
3. **포맷** — 코드는 언어 지정 트리플 백틱을 쓴다. **응답 전체를 ` ```markdown ` 펜스로 감싸지 말 것**("DO NOT include ```markdown fences"). 콘텐츠로 바로 시작한다("Start directly with the content").
4. **근거 한정** — 위키에 없는 내용은 추측하지 않는다. 위키가 답을 담고 있지 않으면 그 사실을 명시하고, 필요하면 어떤 소스를 ingest하면 되는지 제안한다.

## Step 4 — 환류 (file-back, 선택)

답이 **재사용 가치가 있고** 기존 위키에 아직 페이지로 존재하지 않으면(예: 여러 페이지를 종합한 새 합성), 새 `Concept` 페이지로 환류할지 제안한다.
- 사용자가 동의하면 [wiki-ingest](../wiki-ingest/SKILL.md) 스킬로 넘긴다. 답에 이미 출처가 박혀 있으므로 ingest의 sources[]로 그대로 쓸 수 있다.
- 환류는 query를 다시 ingest로 잇는 고리다 — 이렇게 위키가 compounding된다.

---

## 반드시 해야 할 일
- `index.md`를 읽지 않고 답하지 않는다. 항상 index 드릴다운으로 근거 페이지를 먼저 확보한다.
- 출처 없는 사실 주장을 하지 않는다. 위키에 근거가 없으면 없다고 말한다.

## Tool usage

graphify (`graphify-out/`가 있을 때 사용):
- `graphify query "<질문>"` / `explain "<개념>"` — **Step 1 검색** 시 관련 페이지를 보강 탐색.
- `graphify path "<A>" "<B>"` — **Step 1 확장** 시 두 페이지의 관계 경로 확인(1–2 hop 근거).