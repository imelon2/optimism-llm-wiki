# Graph Report - ./wiki  (2026-08-21)

## Corpus Check
- Corpus is ~16,270 words - fits in a single context window. You may not need a graph.

## Summary
- 112 nodes · 172 edges · 10 communities
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.75)
- Token cost: 237,703 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Wiki 인덱스 허브|Wiki 인덱스 허브]]
- [[_COMMUNITY_txpool local 면제·수수료 정책|txpool local 면제·수수료 정책]]
- [[_COMMUNITY_P2P 피어링·부트노드 진단|P2P 피어링·부트노드 진단]]
- [[_COMMUNITY_동기화·Engine API 빌드 사이클|동기화·Engine API 빌드 사이클]]
- [[_COMMUNITY_L1 확인 깊이·inbound 차단|L1 확인 깊이·inbound 차단]]
- [[_COMMUNITY_L1 Receipt 조회 전략|L1 Receipt 조회 전략]]
- [[_COMMUNITY_RPC 타임아웃·백오프 재시도|RPC 타임아웃·백오프 재시도]]
- [[_COMMUNITY_관측성·프로파일링 스택|관측성·프로파일링 스택]]
- [[_COMMUNITY_피어 발견·아웃바운드 다이얼|피어 발견·아웃바운드 다이얼]]
- [[_COMMUNITY_txpool full 원인 판별|txpool full 원인 판별]]

## God Nodes (most connected - your core abstractions)
1. `Wiki Log (append-only 변경 이력)` - 16 edges
2. `Wiki Index (OP Stack LLM Wiki 전체 카탈로그)` - 15 edges
3. `OP Stack 노드 ↔ Grafana LGTM 관측성 연동` - 11 edges
4. `op-reth --max-outbound-peers (devp2p outbound 슬롯 상한)` - 11 edges
5. `op-node P2P Peering & Chain Isolation` - 10 edges
6. `op-reth --txpool.nolocals (local exemption 전체 비활성화)` - 10 edges
7. `op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로` - 10 edges
8. `op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단` - 10 edges
9. `op-node --syncmode (CLSync/ELSync)` - 9 edges
10. `OP Stack 트랜잭션 수수료 & EIP-1559 모델` - 9 edges

## Surprising Connections (you probably didn't know these)
- `op-node finalized 신호가 정하는 reth 캐시 축출 임계 (min(finalized, persisted_tip−64))` --semantically_similar_to--> `op-node L1 Confirmation Depth (--verifier.l1-confs vs --sequencer.l1-confs)`  [INFERRED] [semantically similar]
  runbooks/op-reth-changeset-cache-miss.md → concepts/op-node-l1-confs-conf-depth.md
- `kona bootstrap_peers 교차검증 (BootNode::Enode → request_enr, 실패 시 continue)` --semantically_similar_to--> `op-node P2P Peering & Chain Isolation`  [INFERRED] [semantically similar]
  runbooks/op-reth-discv5-bootnode-timeout.md → concepts/op-node-p2p-peering.md
- `PoolErrorKind::DiscardedOnInsert (용량 초과 = 사실상 underpriced)` --semantically_similar_to--> `try_rotate_peer() — capacity 도달 시 UselessPeer 절단 로테이션`  [INFERRED] [semantically similar]
  concepts/reth-txpool-capacity-slot-limits.md → concepts/op-reth-max-outbound-peers.md
- `op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로` --references--> `OP Stack 노드 ↔ Grafana LGTM 관측성 연동`  [EXTRACTED]
  runbooks/op-reth-changeset-cache-miss.md → concepts/observability-grafana-integration.md
- `동반 경고 "resetting back RPC preferences" — l1.rpckind 미스매치 신호` --references--> `op-node --l1.rpckind (L1 RPC 공급자 힌트)`  [EXTRACTED]
  runbooks/op-node-fetch-receipts-context-deadline.md → concepts/op-node-l1-rpckind-receipts.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **관측성 4축 (메트릭·로그·프로파일·트레이스) 지원 현황** — concepts_observability_grafana_integration_oppprof_pprof_endpoint, concepts_observability_grafana_integration_pyroscope_scrape, concepts_observability_grafana_integration_op_reth_otlp_export, concepts_observability_grafana_integration_tempo_trace_unsupported, concepts_op_reth_max_outbound_peers_network_peer_metrics [EXTRACTED 1.00]
- **-32003 "txpool is full" 원인 판별 경로** — concepts_reth_txpool_capacity_slot_limits_discarded_on_insert, concepts_reth_txpool_capacity_slot_limits_spammer_exceeded_capacity, concepts_reth_txpool_capacity_slot_limits_max_account_slots, concepts_reth_txpool_capacity_slot_limits_subpool_limits, concepts_reth_txpool_capacity_slot_limits_rpc_pool_error_txpool_overflow, concepts_op_reth_txpool_nolocals_is_local [EXTRACTED 1.00]
- **gap 복구가 CL ReqResp에서 op-reth EL snap sync로 이관된 흐름** — concepts_op_node_syncmode_reqresp_deprecation_reqresp_sync_client_removal, concepts_op_node_syncmode_reqresp_deprecation_el_sync_fallback, concepts_op_node_syncmode_reqresp_deprecation_post_finalization_el_sync, concepts_op_reth_max_outbound_peers_max_outbound_peers, concepts_op_node_p2p_peering_reqresp_protocol_id [EXTRACTED 1.00]
- **L1 origin 전진 → receipts 조회 실패 → 단일 이벤트 루프 프리징 → 백오프 회복 흐름** — runbooks_op_node_fetch_receipts_context_deadline_l1_traversal_advance_l1_block, runbooks_op_node_fetch_receipts_context_deadline_temporary_error_backoff, runbooks_op_node_fetch_receipts_context_deadline_global_synchronous_event_loop, runbooks_op_node_fetch_receipts_context_deadline_exponential_backoff_recovery_window [EXTRACTED 1.00]
- **replica 포워딩 실패 체인 (WARN 지점 → 조기반환 → 원인 A/B → 에러코드 판별)** — runbooks_op_reth_sequencer_forward_txpool_full_sequencer_client_request, runbooks_op_reth_sequencer_forward_txpool_full_no_retry_no_local_retention, runbooks_op_reth_sequencer_forward_txpool_full_cause_a_capacity_overflow, runbooks_op_reth_sequencer_forward_txpool_full_cause_b_account_slot_exceeded, runbooks_op_reth_sequencer_forward_txpool_full_error_code_client_discrimination [EXTRACTED 1.00]
- **op-reth 로그 해석 런북 계열 (changeset MISS / discv5 Timeout / txpool full)** — runbooks_op_reth_changeset_cache_miss_changeset_cache_miss, runbooks_op_reth_discv5_bootnode_timeout_bootnode_timeout, runbooks_op_reth_sequencer_forward_txpool_full_sequencer_forward_txpool_full, runbooks_op_node_fetch_receipts_context_deadline_fetch_receipts_failure [EXTRACTED 1.00]

## Communities (10 total, 0 thin omitted)

### Community 0 - "Wiki 인덱스 허브"
Cohesion: 0.20
Nodes (19): OP Stack 노드 ↔ Grafana LGTM 관측성 연동, op-node L1 Confirmation Depth (--verifier.l1-confs vs --sequencer.l1-confs), op-node --l1.rpckind (L1 RPC 공급자 힌트), 기본값 standard 채택 이유 (eth_getBlockReceipts 표준화), nolocals의 실효성은 sequencer 노드에 한정 (replica는 forward), op-reth --txpool.nolocals (local exemption 전체 비활성화), OP Stack 트랜잭션 수수료 & EIP-1559 모델, 실행 계층 정본 한계 (op-geth pinned 모듈 · op-revm 외부 크레이트) (+11 more)

### Community 1 - "txpool local 면제·수수료 정책"
Cohesion: 0.12
Nodes (18): eviction 면제는 pending 서브풀에서만 — parked는 보호 없음, LocalTransactionConfig::is_local (nolocals가 locals보다 우선), local 트랜잭션 면제 3종 (slot / price / eviction), LocalTransactionConfig (no_exemptions / local_addresses / propagate), eth_sendRawTransaction은 TransactionOrigin::External (local 아님), --txpool.locals (주소 기반 local 지정), OP의 base fee는 소각되지 않고 BaseFeeVault로 적립, effectiveGasPrice = min(maxFeePerGas, baseFee + maxPriorityFeePerGas) (+10 more)

### Community 2 - "P2P 피어링·부트노드 진단"
Cohesion: 0.14
Nodes (16): 체인별 gossip 토픽 /optimism/<L2ChainID>/N/blocks, op-node P2P Peering & Chain Isolation, ELSync (execution-layer, op-reth snap sync 주도), SupportsPostFinalizationELSync (reth/erigon만 true), "default: 100" 문서/코드 불일치 (default_value_t 부재 → reth.toml 우선), inbound trusted 예외 vs outbound 무예외 비대칭, op-reth --max-outbound-peers (devp2p outbound 슬롯 상한), --max-peers (총합 지정, inbound:outbound 2:1 분배, 배타) (+8 more)

### Community 3 - "동기화·Engine API 빌드 사이클"
Cohesion: 0.22
Nodes (11): req-resp 프로토콜 ID /opstack/req/payload_by_number/<chainID>/0, 공식 문서 p2p.sync.req-resp 서술의 stale 충돌 (코드가 정본), ReqResp P2P sync 클라이언트 제거 배경 (무서명 역순 인증·메모리 제약·complexity ceiling), --p2p.sync.req-resp 서버 (payload_by_number 서빙, rate limit), op-node --syncmode (CLSync/ELSync), op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로, Engine API 블록 빌드 사이클 (FCU-with-attributes → getPayload → newPayload → FCU), op-node finalized 신호가 정하는 reth 캐시 축출 임계 (min(finalized, persisted_tip−64)) (+3 more)

### Community 4 - "L1 확인 깊이·inbound 차단"
Cohesion: 0.22
Nodes (9): confDepth 래퍼 (L1 head 근접 블록을 ethereum.NotFound으로 숨김), sequencer depth 과다 시 deposit-only 빈 블록 위험 (MaxSequencerDrift/SeqWindowSize), derivation 파이프라인 (verifConfDepth 소비 지점), --sequencer.l1-confs (SequencerConfDepth, 기본 4), verifier 기본 depth=0인 이유 (derivation이 reorg를 정식 지원), --verifier.l1-confs (VerifierConfDepth, 기본 0), BlockingConnectionGater (peerID/IP/subnet denylist), 방화벽 기반 inbound 하드 차단 (TCP/UDP 9222) (+1 more)

### Community 5 - "L1 Receipt 조회 전략"
Cohesion: 0.22
Nodes (9): L1OriginSelector (sequencer의 L1 origin 전진 결정), alchemy_getTransactionReceipts (블록당 250 CU 정액), AvailableReceiptsFetchingMethods (kind → 메서드 비트필드), receipt 메서드 자동 강등(OnReceiptsMethodErr)과 주기적 복구, PickBestReceiptsFetchingMethod (tx 수 기반 비용 손익분기 선택), RPCReceiptsFetcher (provKind 소비 지점), "resetting back RPC preferences" 경고 = kind 미스매치 신호, CLSync (consensus-layer, op-node 주도 순차 NewPayload) (+1 more)

### Community 6 - "RPC 타임아웃·백오프 재시도"
Cohesion: 0.22
Nodes (9): 지수 백오프 재시도와 회복 창 (min(2^n×1s,10s)+jitter, 대기 중 루프 해제), GlobalSynchronous 단일 이벤트 루프 (동기 블로킹 RPC가 블록 생산을 멈춤), L1Traversal.AdvanceL1Block — L1 origin 전진 시 receipts 조회 지점, L1 RPC 클라이언트 호출 타임아웃 기본값 (callTimeout 10s / batchCallTimeout 20s), TemporaryError 래핑 & 시퀀서 백오프 (origin 미전진·자가복구), UpdateSystemConfigWithL1Receipts — L1 ConfigUpdate 이벤트 스캔·SystemConfig 갱신, forward_raw_transaction / _conditional — request()의 유일한 호출자 2곳, 포워딩 실패 시 `?` 조기반환 — 재시도 없음·로컬 풀 미보관(tx 유실) (+1 more)

### Community 7 - "관측성·프로파일링 스택"
Cohesion: 0.29
Nodes (7): 연속 프로파일링의 SRE 활용 가치 (MTTR·회귀탐지·용량산정), op-reth OTLP 트레이스/로그 네이티브 export (--tracing-otlp / --logs-otlp), op-service/oppprof /debug/pprof 엔드포인트, otlp-logs Cargo feature 게이팅 함정 (--logs-otlp 무효화), pprof 0.0.0.0 기본 바인딩 노출 위험, Grafana Alloy pyroscope.scrape (pull 모드 연속 프로파일링), Go 노드·op-geth 분산 트레이스 미지원 (Tempo 공백)

### Community 8 - "피어 발견·아웃바운드 다이얼"
Cohesion: 0.29
Nodes (7): discv5 discovery (L1 CL과 동일 와이어 프로토콜), ENR opstack 키 + chainID 필터 (FilterEnodes, outbound 격리), --p2p.no-discovery + --p2p.static (정적 신뢰 피어 토폴로지), best_unconnected() 다이얼 우선순위 (trusted/static → reputation → fork_id), has_out_capacity() — pending dial AND outbound 상한 AND 게이트, max_concurrent_outbound_dials (기본 30, CLI 플래그 없음), reth-network 피어 메트릭 (network_outgoing_connections 등)

### Community 9 - "txpool full 원인 판별"
Cohesion: 0.33
Nodes (7): 로그 상관관계: New payload job created parent=X ↔ 최고 번호 MISS 블록 해시 일치, 원인 A — 서브풀 용량 초과 (DiscardedOnInsert, 기본 10,000tx/20MB), 원인 B — 계정 슬롯 초과 (SpammerExceededCapacity, max_account_slots 16 + 미래 nonce), -32003(reth) vs -32000(op-geth)로 거절 클라이언트 판별, rollup-boost/op-conductor 프록시는 에러 코드를 변형하지 않음 (parse_response_code), op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단, 시퀀서 로그 원본 에러 문자열로 A/B 확증 (spammer vs pool size constraints)

## Knowledge Gaps
- **18 isolated node(s):** `derivation 파이프라인 (verifConfDepth 소비 지점)`, `alchemy_getTransactionReceipts (블록당 250 CU 정액)`, `ENR opstack 키 + chainID 필터 (FilterEnodes, outbound 격리)`, `체인별 gossip 토픽 /optimism/<L2ChainID>/N/blocks`, `--p2p.no-discovery + --p2p.static (정적 신뢰 피어 토폴로지)` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Wiki Log (append-only 변경 이력)` connect `Wiki 인덱스 허브` to `txpool full 원인 판별`, `P2P 피어링·부트노드 진단`, `동기화·Engine API 빌드 사이클`?**
  _High betweenness centrality (0.238) - this node is a cross-community bridge._
- **Why does `Wiki Index (OP Stack LLM Wiki 전체 카탈로그)` connect `Wiki 인덱스 허브` to `txpool full 원인 판별`, `P2P 피어링·부트노드 진단`, `동기화·Engine API 빌드 사이클`?**
  _High betweenness centrality (0.220) - this node is a cross-community bridge._
- **Why does `op-reth --txpool.nolocals (local exemption 전체 비활성화)` connect `Wiki 인덱스 허브` to `txpool local 면제·수수료 정책`, `txpool full 원인 판별`, `관측성·프로파일링 스택`?**
  _High betweenness centrality (0.183) - this node is a cross-community bridge._
- **What connects `otlp-logs Cargo feature 게이팅 함정 (--logs-otlp 무효화)`, `Go 노드·op-geth 분산 트레이스 미지원 (Tempo 공백)`, `pprof 0.0.0.0 기본 바인딩 노출 위험` to the rest of the system?**
  _38 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `txpool local 면제·수수료 정책` be split into smaller, more focused modules?**
  _Cohesion score 0.12418300653594772 - nodes in this community are weakly interconnected._
- **Should `P2P 피어링·부트노드 진단` be split into smaller, more focused modules?**
  _Cohesion score 0.14166666666666666 - nodes in this community are weakly interconnected._