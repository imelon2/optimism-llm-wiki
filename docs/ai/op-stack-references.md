# OP Stack 분석 레퍼런스 맵

AI가 **op-stack/optimism을 분석·조사·리서치·심층 탐구**할 때 근거로 삼는 1차 자료의 위치와 사용처를 정의한다.

## 정본 자료 (Canonical Sources)

| # | 자료 | 위치 | 권한 | 무엇을 위한 것인가 |
|---|------|------|------|--------------------|
| 1 | **Official docs (LLM index)** | https://docs.optimism.io/llms.txt | 외부 fetch | 개념 정의, 운영자/개발자 가이드, 용어 정본 |
| 2 | **OP Stack Core** | `resource/optimism` | 로컬 | 오프체인 클라이언트/서비스 Go 소스 (실제 동작의 정본) |
| 3 | **Contracts (Bedrock)** | `resource/optimism/packages/contracts-bedrock` | 로컬 | 온체인 컨트랙트 Solidity 소스 + 프로토콜 specs |
| 4 | **Operations & Infra** | `resource/infra` | 로컬 | 체인을 운영하기 위한 보조 인프라 서비스 |

- GitHub 원본: [`ethereum-optimism/optimism`](https://github.com/ethereum-optimism/optimism) · [`ethereum-optimism/infra`](https://github.com/ethereum-optimism/infra)

## CodeGraph

- 코드 탐색 시 CodeGraph 인덱스는 **`resource/.codegraph`** 에 있으며 `resource/optimism` 전체를 커버한다.
- MCP `codegraph_explore`에 `projectPath: resource/optimism`을 주거나, shell은 `cd resource && codegraph explore "<symbol/question>"`로 조회한다.
- 인덱스가 있으므로 코드 트랙은 grep/find보다 `codegraph_explore`를 우선한다.

## 탐색 규칙

- `./optimism/` 내부의 주요 모듈들(`op-node`, `op-batcher`, `op-proposer`, `op-challenger`, `op-supervisor`, `op-deployer`, `packages/`, `cannon/` 등)은 각각 독립적인 리서치 주제이다. 범위를 단일 모듈로 좁히면 심층 분석이 쉬워진다.
- `infra` 저장소의 도구들, 예를 들어 모니터링, 배포 스크립트, k8s 매니페스트 등은 노드 운영/인프라 리서치의 대상이다.
