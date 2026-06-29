# Optimism LLM Wiki

Optimism LLM Wiki는 OP Stack 엔지니어링 지식을 LLM이 직접 쓰고 읽도록 누적·유지하는 마크다운 지식베이스로, Andrej Karpathy의 "LLM Wiki"와 Google "Open Knowledge Format"(OKF) v0.1의 구조를 결합해 설계했다.

## Additional Documentation

More detailed guidance for AI agents can be found in:

- [docs/ai/wiki-structure.md](docs/ai/wiki-structure.md) — 레이어/디렉토리/type, 프론트매터 스키마, tags, 교차링크, 본문 스타일
- [docs/ai/op-stack-references.md](docs/ai/op-stack-references.md) — OP Stack 분석·리서치 근거 자료(공식 문서, 로컬 소스, CodeGraph)의 위치와 사용처

## 언어 및 문서화 지침

- 의사소통의 기본 언어는 `한국어`로 한다.
- 설명·요약·문서·주석성 텍스트는 한국어로 작성하되, 코드·명령어·로그·고유명사는 원문 그대로 보존한다.

## Git 커밋 규칙

- 커밋은 **`git-master` 에이전트로 작성**합니다(스타일 자동 감지, 원자적 커밋).
- git-master 에이전트를 쓸 수 없는 환경이면, **먼저 `git log`로 최근 커밋 메시지를 조회**해 형식·언어·구조·트레일러를 파악한 뒤 그 스타일에 맞춰 직접 작성합니다.
- 커밋 메시지는 `한국어`로 작성한다.
- `./wiki` 변경이 포함된 커밋은 메시지를 `wiki:` 로 시작한다.
