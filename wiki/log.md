# Wiki Log

> Append-only 변경 이력. 최신 항목이 위로 오도록 추가한다.
> 형식: `## [YYYY-MM-DD] <op> | <대상>` (op = ingest | query | lint)
> (예약 파일 — concept 문서로 쓰지 않음)

## [2026-07-16] ingest | op-node --syncmode(CLSync/ELSync) 차이 + ReqResp P2P sync 클라이언트 제거 리서치(client 제거로 --syncmode.req-resp·--p2p.sync.onlyReqToStatic deprecated no-op, --p2p.sync.req-resp는 서버만 잔존·향후 제거 예정, gap 복구가 op-reth EL snap sync로 대체(CLSync도 NewPayload SYNCING→FCU로 EL sync fallback), op-reth는 SupportsPostFinalizationELSync=true로 finalized 이후에도 EL sync 가능·--l2.enginekind 기본 reth, 서버 rate limit 20/s·peer 4/s) → concepts/op-node-syncmode-reqresp-deprecation.md (신규), concepts/op-node-p2p-peering.md (교차링크). 모순 flag: docs op-node-config가 p2p.sync.req-resp를 여전히 "server+client, default true"로 stale 서술
## [2026-07-10] ingest | op-node --verifier.l1-confs vs --sequencer.l1-confs 차이 분석(동일 confDepth 안전거리 메커니즘을 각각 derivation 파이프라인/sequencer L1 origin 선택에 주입, 기본값 verifier=0·sequencer=4, depth=0=안전거리없음, sequencer depth 과다 시 MaxSequencerDrift/SeqWindowSize 초과로 deposit-only 블록 위험) → concepts/op-node-l1-confs-conf-depth.md (신규), runbooks/op-node-fetch-receipts-context-deadline.md (교차링크)
## [2026-07-06] ingest | OP Stack maxFeePerGas/maxPriorityFeePerGas 리서치(두 필드=L2 실행비 한정 effectiveGasPrice=min(maxFeePerGas, baseFee+maxPriorityFeePerGas), base fee 소각 대신 BaseFeeVault 적립, EIP-1559 파라미터 Holocene 이후 SystemConfig 설정, L1 data fee Bedrock/Ecotone/Fjord 진화, --min-suggested-priority-fee 추천 하한 기본 1,000,000 wei) → concepts/op-stack-eip1559-fees.md (신규), concepts/op-reth-txpool-nolocals.md (교차링크)
## [2026-07-06] ingest | op-reth --txpool.nolocals 옵션 분석(local tx slot/price/eviction 3종 면제 비활성화, is_local() 로직에서 no_exemptions가 --txpool.locals보다 우선, exemption과 propagation 분리, OP sequencer 실효성) → concepts/op-reth-txpool-nolocals.md (신규), concepts/observability-grafana-integration.md (교차링크)
## [2026-07-06] ingest | op-reth OTLP 관측성 옵션(--tracing-otlp*/--logs-otlp*) 분석 — 트레이스/로그 OTLP 네이티브 export, otlp/otlp-logs feature 게이팅, 플래그별 정본(reth v2.3.0 trace.rs) → concepts/observability-grafana-integration.md (보강: §1-a op-reth 예외 섹션·4축 표·인과 한계·근거·외부링크)
## [2026-07-06] ingest | op-node receipts fetch 실패의 connection reset by peer 변형 + 단일 이벤트 루프(GlobalSynchronous) 블로킹이 블록 생산을 멈추는 메커니즘·연속 실패 지수 백오프 타임라인 보강 → runbooks/op-node-fetch-receipts-context-deadline.md (보강: 실패 모드 표·영향 섹션·원인 후보 5·판정 표, 제목/description 일반화)
## [2026-07-04] ingest | op-node "failed to fetch receipts ... for L1 sysCfg update: context deadline exceeded" 진단(L1 origin 전진 시 receipts 조회 RPC 타임아웃 → 시퀀서 백오프, 일시적/자가복구 판정) → runbooks/op-node-fetch-receipts-context-deadline.md (신규), concepts/op-node-l1-rpckind-receipts.md·runbooks/op-reth-changeset-cache-miss.md·concepts/observability-grafana-integration.md (교차링크)
## [2026-07-03] ingest | op-reth "Changeset cache MISS" 로그 진단 + op-stack Engine API 블록 빌드 유발 경로(2026-05-22 대규모 사례 제외) → runbooks/op-reth-changeset-cache-miss.md (신규), runbooks/op-reth-discv5-bootnode-timeout.md·concepts/observability-grafana-integration.md (교차링크)
## [2026-07-02] ingest | OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 조사(트레이스 미지원 + pprof→Pyroscope + SRE 가치) → concepts/observability-grafana-integration.md (신규), concepts/op-node-l1-rpckind-receipts.md·concepts/op-node-p2p-peering.md (교차링크)
## [2026-06-30] ingest | op-node l1.rpckind 옵션 분석(receipts fetching 최적화 + alchemy 예시) → concepts/op-node-l1-rpckind-receipts.md (신규)
## [2026-06-29] ingest | op-reth discv5 부트노드 Timeout 조사 → runbooks/op-reth-discv5-bootnode-timeout.md (신규), concepts/op-node-p2p-peering.md (교차링크)
## [2026-06-29] ingest | op-node P2P peer 격리 리서치 → concepts/op-node-p2p-peering.md (신규)
## [2026-06-26] init | wiki 골격 생성 (Phase 0: 디렉토리 + index.md + log.md)
