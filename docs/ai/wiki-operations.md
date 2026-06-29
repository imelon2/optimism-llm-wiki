# Wiki Operations

위키의 3가지 연산: ingest / query / lint (Karpathy LLM Wiki 모델). 구조·작성 표준은 [wiki-structure.md](./wiki-structure.md).

## ingest

새 소스를 위키에 흡수하는 연산. 절차는 `.claude/skills/wiki-ingest/SKILL.md`에 있다.
트리거: "ingest", "위키에 추가", "wiki ingest".

흐름: type 결정 → `resource/` 원본 읽기 → OKF 페이지 작성 → `index.md` 갱신 → 교차링크 → `log.md` 갱신.

## query

1. `wiki/index.md`를 먼저 읽고 관련 페이지로 드릴다운한다.
2. 페이지를 종합해 출처 인용과 함께 답한다.
3. 재사용 가치가 있는 답은 새 Concept 페이지로 환류한다(= ingest).

## lint

위키 전체의 정합성을 점검하는 연산. 여러 번 ingest 후, `resource/` submodule 업데이트 직후, 정기 주기에 실행한다.

점검 항목: 페이지 간 모순 / stale(`source_commit`·`timestamp`) / orphan(인바운드 링크 없음) / 누락된 교차링크 / 깨진 링크.
