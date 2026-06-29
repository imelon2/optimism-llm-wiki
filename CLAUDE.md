# Optimism LLM Wiki

Optimism LLM Wiki는 OP Stack 엔지니어링 지식을 LLM이 직접 쓰고 읽도록 누적·유지하는 마크다운 지식베이스로, Andrej Karpathy의 "LLM Wiki"와 Google "Open Knowledge Format"(OKF) v0.1의 구조를 결합해 설계했다.

## Additional Documentation

More detailed guidance for AI agents can be found in:

- [docs/ai/wiki-structure.md](docs/ai/wiki-structure.md) — 레이어/디렉토리/type, 프론트매터 스키마, tags, 교차링크, 본문 스타일
- [docs/ai/wiki-operations.md](docs/ai/wiki-operations.md) — ingest/query/lint 연산

## 언어 및 문서화 지침

- 의사소통의 기본 언어는 `한국어`로 한다.
- 설명·요약·문서·주석성 텍스트는 한국어로 작성하되, 코드·명령어·로그·고유명사는 원문 그대로 보존한다.

## Git 커밋 규칙

- 커밋은 **`git-master` 에이전트로 작성**합니다(스타일 자동 감지, 원자적 커밋).
- git-master 에이전트를 쓸 수 없는 환경이면, **먼저 `git log`로 최근 커밋 메시지를 조회**해 형식·언어·구조·트레일러를 파악한 뒤 그 스타일에 맞춰 직접 작성합니다.
- 커밋 메시지는 `한국어`로 작성한다.
- `./wiki` 변경이 포함된 커밋은 메시지를 `wiki:` 로 시작한다.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
