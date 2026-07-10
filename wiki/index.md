# Wiki Index

> OP Stack LLM Wiki의 전체 카탈로그. 각 Concept 페이지를 `[제목](경로)` — 한줄요약 형식으로 등록한다.
> 탐색은 항상 이 파일을 먼저 읽고 관련 페이지로 드릴다운한다. (예약 파일 — concept 문서로 쓰지 않음)

## Concepts
<!-- wiki/concepts/ — 프로토콜 개념/메커니즘 -->
- [op-node P2P Peering & Chain Isolation](concepts/op-node-p2p-peering.md) — discv5·ENR opstack chainID·gossip 토픽·게이팅으로 Optimism 노드만 격리하는 메커니즘과 inbound 하드 제한 방법
- [op-node l1.rpckind & L1 Receipts Fetching 최적화](concepts/op-node-l1-rpckind-receipts.md) — --l1.rpckind가 L1 RPC 공급자 힌트로 영수증 조회 메서드를 비용 최적 선택·강등·복구하는 메커니즘과 alchemy 설정 효과
- [OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황](concepts/observability-grafana-integration.md) — 메트릭·로그·프로파일은 네이티브 연동(pprof→Pyroscope), 트레이스(Tempo)는 Go 노드·op-geth 미지원이나 op-reth는 --tracing-otlp/--logs-otlp로 OTLP 네이티브 export(예외). 프로파일 타입별 정보와 SRE 활용 가치
- [op-reth --txpool.nolocals & Local Transaction Exemption](concepts/op-reth-txpool-nolocals.md) — local tx의 slot/price/eviction 3종 면제를 꺼 모든 tx를 remote와 동일 취급하게 하는 boolean 플래그, is_local() 로직에서 nolocals가 --txpool.locals보다 우선, OP sequencer 맥락의 실효성
- [OP Stack 트랜잭션 수수료 & EIP-1559 (maxFeePerGas / maxPriorityFeePerGas)](concepts/op-stack-eip1559-fees.md) — 두 필드가 L2 실행비만 지배(effectiveGasPrice=min(maxFeePerGas, baseFee+maxPriorityFeePerGas))하고 L1 data fee는 별도 부과, base fee가 소각 대신 BaseFeeVault 적립, EIP-1559 파라미터의 Holocene 이후 SystemConfig 설정, min-suggested-priority-fee 추천 하한
- [op-node --verifier.l1-confs vs --sequencer.l1-confs (L1 Confirmation Depth)](concepts/op-node-l1-confs-conf-depth.md) — 동일한 confDepth 안전거리(L1 head 기준 최근 N블록을 NotFound로 숨김)를 각각 derivation 파이프라인과 sequencer의 L1 origin 선택에 적용, 기본값 verifier=0/sequencer=4가 다른 이유, sequencer depth 과다 시 deposit-only 블록 위험

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
- [op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로](runbooks/op-reth-changeset-cache-miss.md) — 무해·자가복구 WARN이 op-node의 FCU-with-attributes 블록 빌드에서 유발되는 경로(parent=X↔unsafe 헤드 매핑, finalized→evict 임계)와 진단 체크리스트
- [op-node "failed to fetch receipts ... for L1 sysCfg update" 진단 (RPC 타임아웃 / 연결 리셋)](runbooks/op-node-fetch-receipts-context-deadline.md) — L1 origin 전진 시 receipts 조회가 L1 RPC 실패(timeout / connection reset)로 시퀀서가 백오프하는 로그의 인과 사슬·일시적/자가복구 판정·단일 이벤트 루프 블로킹이 블록 생산을 멈추는 메커니즘(연속 실패 지수 백오프 타임라인)·원인 후보·진단 절차
