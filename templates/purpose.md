# Purpose

## Why this wiki

Optimism / OP Stack 프로토콜·컴포넌트·컨트랙트·업그레이드 히스토리를 한 곳에 모아, 새 컨트리뷰터 / 보안 리뷰어 / 노드 운영자 / 통합 개발자가 빠르게 *정확한 근거를 인용하며* 학습할 수 있게 한다. 본 위키의 모든 페이지는 사변이 아닌 출처 인용·코드 참조·기존 페이지 링크로 뒷받침되며, LLM(Claude Code 세션)이 ingest 절차를 통해 컴파일하고, 사람은 REVIEW 큐로 큐레이션한다.

본 위키는 단순한 메모장이 아니라 **OP Stack 기반 Layer2 메인넷을 구축·운영하기 위한 실전형 기술 지도** 이며, 한 번 학습한 내용을 시간이 지나도 다시 꺼내 검증·재해석할 수 있는 **장기 학습 자산** 으로 누적된다.

## 역할 분리 (스킬·문서)

| 주체 | 역할 | 산출물 |
| --- | --- | --- |
| **op-research** 스킬 | 조사·분석·deep-dive | `./.olw/` 보고서 (위키를 만들지 않음) |
| **op-wiki** 스킬 | 반영(ingest) — 대화/분석 결과를 위키 페이지로 컴파일 | `./wiki/**.md` (사용자 명시 트리거 시에만) |
| **.claude/skills/op-wiki/references/schema.md** | 페이지 작성 규약 단일 진실원 | type / frontmatter / body / wikilink / REVIEW / 언어 |
| **사람** | 소싱·질문·큐레이션 | `.olw/review-queue.md` status 갱신 |

위키를 실제로 쓰는 트리거는 **오직 op-wiki 스킬** 이다 (`.claude/skills/op-wiki/SKILL.md`). 조사 자체는 op-wiki 가 하지 않는다.


## Audience

- 프로토콜 엔지니어 (op-node / op-reth / op-batcher / op-proposer / op-challenger / fault proof 구현·운영)
- 보안 리뷰어 (컨트랙트 감사·spec drift 탐지)
- 노드 운영자 (L2 메인넷·테스트넷 운영)
- 신규 컨트리뷰터 (OP Labs 모노레포 입문)
- 본인 (선형 학습이 아닌 *검색·재방문* 자료로서)

## 공식 참고 자료

| 종류 | 위치 | 용도 |
| --- | --- | --- |
| 공식 문서 (LLM 색인) | https://docs.optimism.io/llms.txt | 개념·아키텍처·운영 가이드의 1차 진입점 (LLM agent 가 가장 먼저 fetch) |
| OP Stack 본체 (로컬) | `optimism/` 디렉토리 | 실제 구현체. 소스 경로 인용은 `optimism/<module>/<file>.go:LINE` 형식 |
| OP Stack Contract (로컬) | `optimism/packages/contracts-bedrock` 디렉토리 | 실제 op-stak contracts 구현체. |
| OP Stack 본체 (원격) | https://github.com/ethereum-optimism/optimism | 로컬에 없는 브랜치 / PR / 이슈 확인용 |
| 운영·인프라 컴포넌트 | https://github.com/ethereum-optimism/infra | 노드 운영, 모니터링, 인프라 관련 도구 |

- 로컬 `optimism/` 디렉토리는 위 GitHub 저장소의 클론이다. 코드 탐색은 항상 **로컬을 먼저** 사용하고, 원격은 보조적으로 참조한다.
- `optimism/` 내부 주요 모듈(예: `op-node`, `op-batcher`, `op-proposer`, `op-challenger`, `op-supervisor`, `op-deployer`, `packages/`, `cannon/` 등) 은 그 자체로 독립적 리서치 주제다. 모듈별로 `type: component` 페이지 (`wiki/components/<slug>.md`) 를 분리해 축적해 나간다.
- `infra` 저장소의 도구 (예: monitoring, deployment scripts, k8s manifests) 는 `type: component` 또는 `type: synthesis` 페이지로 별도 정리. 코드 인용은 `infra/<path>:LINE` 형식.