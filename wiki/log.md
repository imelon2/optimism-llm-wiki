# Wiki Log

> Append-only 변경 이력. 최신 항목이 위로 오도록 추가한다.
> 형식: `## [YYYY-MM-DD] <op> | <대상>` (op = ingest | query | lint)
> (예약 파일 — concept 문서로 쓰지 않음)

## [2026-07-06] ingest | op-node receipts fetch 실패의 connection reset by peer 변형 + 단일 이벤트 루프(GlobalSynchronous) 블로킹이 블록 생산을 멈추는 메커니즘·연속 실패 지수 백오프 타임라인 보강 → runbooks/op-node-fetch-receipts-context-deadline.md (보강: 실패 모드 표·영향 섹션·원인 후보 5·판정 표, 제목/description 일반화)
## [2026-07-04] ingest | op-node "failed to fetch receipts ... for L1 sysCfg update: context deadline exceeded" 진단(L1 origin 전진 시 receipts 조회 RPC 타임아웃 → 시퀀서 백오프, 일시적/자가복구 판정) → runbooks/op-node-fetch-receipts-context-deadline.md (신규), concepts/op-node-l1-rpckind-receipts.md·runbooks/op-reth-changeset-cache-miss.md·concepts/observability-grafana-integration.md (교차링크)
## [2026-07-03] ingest | op-reth "Changeset cache MISS" 로그 진단 + op-stack Engine API 블록 빌드 유발 경로(2026-05-22 대규모 사례 제외) → runbooks/op-reth-changeset-cache-miss.md (신규), runbooks/op-reth-discv5-bootnode-timeout.md·concepts/observability-grafana-integration.md (교차링크)
## [2026-07-02] ingest | OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 조사(트레이스 미지원 + pprof→Pyroscope + SRE 가치) → concepts/observability-grafana-integration.md (신규), concepts/op-node-l1-rpckind-receipts.md·concepts/op-node-p2p-peering.md (교차링크)
## [2026-06-30] ingest | op-node l1.rpckind 옵션 분석(receipts fetching 최적화 + alchemy 예시) → concepts/op-node-l1-rpckind-receipts.md (신규)
## [2026-06-29] ingest | op-reth discv5 부트노드 Timeout 조사 → runbooks/op-reth-discv5-bootnode-timeout.md (신규), concepts/op-node-p2p-peering.md (교차링크)
## [2026-06-29] ingest | op-node P2P peer 격리 리서치 → concepts/op-node-p2p-peering.md (신규)
## [2026-06-26] init | wiki 골격 생성 (Phase 0: 디렉토리 + index.md + log.md)
