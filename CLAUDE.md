## Language Rule

본 프로젝트의 주요 사용자는 한국어 사용자입니다.

Claude는 이 프로젝트에서 사용자와 소통할 때 기본적으로 **한국어를 사용합니다**.

- 설명, 요약, 질문, 제안, 작업 결과 보고는 한국어로 작성합니다.
- 코드, 명령어, 파일명, 함수명, 변수명, 에러 메시지, 공식 용어는 원문을 유지할 수 있습니다.
- 사용자가 영어 또는 다른 언어로 답변을 요청한 경우에는 사용자의 요청을 우선합니다.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
