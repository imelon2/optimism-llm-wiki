# Wiki Index

> OP Stack LLM Wiki의 전체 카탈로그. 각 Concept 페이지를 `[제목](경로)` — 한줄요약 형식으로 등록한다.
> 탐색은 항상 이 파일을 먼저 읽고 관련 페이지로 드릴다운한다. (예약 파일 — concept 문서로 쓰지 않음)

## Concepts
<!-- wiki/concepts/ — 프로토콜 개념/메커니즘 -->
- [op-node P2P Peering & Chain Isolation](concepts/op-node-p2p-peering.md) — discv5·ENR opstack chainID·gossip 토픽·게이팅으로 Optimism 노드만 격리하는 메커니즘과 inbound 하드 제한 방법
- [op-node l1.rpckind & L1 Receipts Fetching 최적화](concepts/op-node-l1-rpckind-receipts.md) — --l1.rpckind가 L1 RPC 공급자 힌트로 영수증 조회 메서드를 비용 최적 선택·강등·복구하는 메커니즘과 alchemy 설정 효과
- [OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황](concepts/observability-grafana-integration.md) — 메트릭·로그·프로파일은 네이티브 연동(pprof→Pyroscope), 트레이스(Tempo)만 커스텀 계측 필요. 프로파일 타입별 정보와 SRE 활용 가치

## Contracts
<!-- wiki/contracts/ — 온체인 스마트 컨트랙트 -->
_아직 없음_

## Components
<!-- wiki/components/ — 오프체인 서비스/바이너리 (op-node, op-batcher, ...) -->
_아직 없음_

## Specs
<!-- wiki/specs/ — specs.optimism.io 스펙 요약 -->
_아직 없음_

## Runbooks
<!-- wiki/runbooks/ — 운영 절차/인시던트 대응 -->
- [op-reth discv5 Bootnode Timeout 진단](runbooks/op-reth-discv5-bootnode-timeout.md) — enode 부트노드가 `failed adding boot node ... err=Timeout`으로 실패하는 원인(enode→ENR 라이브 요청)과 해결(ENR 사용·포트·UDP 점검)
