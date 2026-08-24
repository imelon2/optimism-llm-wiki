# Graph Report - ./wiki  (2026-08-24)

## Corpus Check
- Corpus is ~21,868 words - fits in a single context window. You may not need a graph.

## Summary
- 322 nodes · 362 edges · 22 communities (19 shown, 3 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.83)
- Token cost: 291,893 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Txpool Local Exemption Rules|Txpool Local Exemption Rules]]
- [[_COMMUNITY_L1 RPC Failure Diagnostics|L1 RPC Failure Diagnostics]]
- [[_COMMUNITY_Single Event Loop Blocking|Single Event Loop Blocking]]
- [[_COMMUNITY_Sequencer Stall Timeline|Sequencer Stall Timeline]]
- [[_COMMUNITY_Rollup Timing Parameters|Rollup Timing Parameters]]
- [[_COMMUNITY_Wiki Catalogue and Runbooks|Wiki Catalogue and Runbooks]]
- [[_COMMUNITY_P2P Peering and Chain Isolation|P2P Peering and Chain Isolation]]
- [[_COMMUNITY_Fee Pricing and Pool Eviction|Fee Pricing and Pool Eviction]]
- [[_COMMUNITY_Observability and Profiling|Observability and Profiling]]
- [[_COMMUNITY_L1 Receipts Method Selection|L1 Receipts Method Selection]]
- [[_COMMUNITY_devp2p Peer Slot Control|devp2p Peer Slot Control]]
- [[_COMMUNITY_L1 Confirmation Depth|L1 Confirmation Depth]]
- [[_COMMUNITY_Changeset Cache Miss Path|Changeset Cache Miss Path]]
- [[_COMMUNITY_Personal Namespace Removal|Personal Namespace Removal]]
- [[_COMMUNITY_CLSync vs ELSync Modes|CLSync vs ELSync Modes]]
- [[_COMMUNITY_L1 Data Fee Predeploys|L1 Data Fee Predeploys]]
- [[_COMMUNITY_Engine API Block Cycle|Engine API Block Cycle]]
- [[_COMMUNITY_Txpool Full Error Collapse|Txpool Full Error Collapse]]
- [[_COMMUNITY_Txpool Locals Flags|Txpool Locals Flags]]
- [[_COMMUNITY_OTLP Logs Feature Gate|OTLP Logs Feature Gate]]
- [[_COMMUNITY_ReqResp Server Rate Limits|ReqResp Server Rate Limits]]
- [[_COMMUNITY_Local Transaction Origin|Local Transaction Origin]]

## God Nodes (most connected - your core abstractions)
1. `AvailableReceiptsFetchingMethods` - 10 edges
2. `GlobalSyncExec` - 8 edges
3. `--max-outbound-peers` - 8 edges
4. `rollup.Config.BlockTime` - 8 edges
5. `--txpool.nolocals` - 7 edges
6. `FindL1Origin` - 7 edges
7. `LGTM observability` - 6 edges
8. `personal_listAccounts` - 6 edges
9. `LocalTransactionConfig` - 6 edges
10. `FindL1Origin` - 6 edges

## Surprising Connections (you probably didn't know these)
- `op-node Tracer 훅 인터페이스` --semantically_similar_to--> `GlobalSyncExec`  [INFERRED] [semantically similar]
  concepts/observability-grafana-integration.md → concepts/op-node-event-loop-design.md
- `2026-07-04 receipts fetch ingest` --references--> `Fetch Receipts Context Deadline Runbook`  [EXTRACTED]
  log.md → runbooks/op-node-fetch-receipts-context-deadline.md
- `op-node stall as burst amplifier` --semantically_similar_to--> `unsafe head stall`  [INFERRED] [semantically similar]
  runbooks/op-reth-changeset-cache-miss.md → runbooks/op-node-find-l1-origin-stall.md
- `2026-07-03 changeset cache miss ingest` --references--> `Changeset Cache MISS Runbook`  [EXTRACTED]
  log.md → runbooks/op-reth-changeset-cache-miss.md
- `2026-06-29 discv5 bootnode ingest` --references--> `discv5 Bootnode Timeout Runbook`  [EXTRACTED]
  log.md → runbooks/op-reth-discv5-bootnode-timeout.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **op-node 단일 이벤트 루프 콜스택** — concepts_op_node_event_loop_design_eventloop, concepts_op_node_event_loop_design_drain, concepts_op_node_event_loop_design_processevent, concepts_op_node_event_loop_design_runevent, concepts_op_node_event_loop_design_globalsyncexec [EXTRACTED 1.00]
- **시퀀서 2초 사이클 Engine API 흐름** — concepts_op_stack_block_production_sequenceractionevent, concepts_op_stack_block_production_findl1origin, concepts_op_stack_block_production_engine_forkchoiceupdatedv3, concepts_op_stack_block_production_engine_getpayloadv3, concepts_op_stack_block_production_engine_newpayloadv3 [EXTRACTED 1.00]
- **두 원인이 -32003으로 붕괴되는 경로** — concepts_reth_txpool_capacity_slot_limits_discardedoninsert, concepts_reth_txpool_capacity_slot_limits_spammerexceededcapacity, concepts_reth_txpool_capacity_slot_limits_rpcpoolerror_txpooloverflow, concepts_reth_txpool_capacity_slot_limits_32003_txpool_is_full [EXTRACTED 1.00]
- **L1 RPC latency to single-event-loop lock to block production stall** — runbooks_op_node_find_l1_origin_stall_findl1origin, runbooks_op_node_find_l1_origin_stall_calltimeout, runbooks_op_node_find_l1_origin_stall_lock_ratio_91, runbooks_op_node_find_l1_origin_stall_unsafe_head_stall, runbooks_op_node_fetch_receipts_context_deadline_single_event_loop_blocking, runbooks_op_node_fetch_receipts_context_deadline_fetchreceipts [EXTRACTED 1.00]
- **Engine API block build cycle (FCU-with-attributes to newPayload)** — runbooks_op_reth_changeset_cache_miss_onbuildstart, runbooks_op_reth_changeset_cache_miss_engine_forkchoiceupdatedv3, runbooks_op_reth_changeset_cache_miss_engine_getpayloadv3, runbooks_op_reth_changeset_cache_miss_engine_newpayloadv3, runbooks_op_reth_changeset_cache_miss_new_payload_job_created, runbooks_op_reth_changeset_cache_miss_changeset_cache_miss [EXTRACTED 1.00]
- **Replica forwarding failure path for -32003 txpool is full** — runbooks_op_reth_sequencer_forward_txpool_full_rollup_sequencer, runbooks_op_reth_sequencer_forward_txpool_full_forward_raw_transaction, runbooks_op_reth_sequencer_forward_txpool_full_sequencerclient_request, runbooks_op_reth_sequencer_forward_txpool_full_http_request_to_sequencer_failed, runbooks_op_reth_sequencer_forward_txpool_full_raw_tx_forwarder_early_return, runbooks_op_reth_sequencer_forward_txpool_full_32003_txpool_is_full [EXTRACTED 1.00]

## Communities (22 total, 3 thin omitted)

### Community 0 - "Txpool Local Exemption Rules"
Cohesion: 0.09
Nodes (26): clef 외부 서명자, eth_sendRawTransaction, eth_sendRawTransaction, Eviction 면제, is_local(), LocalTransactionConfig, max_account_slots (기본 16), no_exemptions (+18 more)

### Community 1 - "L1 RPC Failure Diagnostics"
Cohesion: 0.08
Nodes (26): batchCallTimeout, CachingReceiptsProvider, connection reset by peer, context deadline exceeded, DerivationPipeline.Step, Engine failed temporarily, backing off sequencer, failed to fetch receipts for L1 sysCfg update, FetchReceipts (+18 more)

### Community 2 - "Single Event Loop Blocking"
Cohesion: 0.09
Nodes (24): 블로킹 백오프(창구 잠김), Drain(), Emit / executor.Enqueue, driver eventLoop, Executor 인터페이스, GlobalSyncExec, pprof goroutine 덤프 진단, libp2p eventbus Emit 배압 (+16 more)

### Community 3 - "Sequencer Stall Timeline"
Cohesion: 0.09
Nodes (23): callTimeout, event.NewGlobalSynchronous, Exponential backoff recovery window, retry.Exponential, Single event loop blocking, batchCallTimeout, callTimeout, ErrNextL1OriginRequired (+15 more)

### Community 4 - "Rollup Timing Parameters"
Cohesion: 0.11
Nodes (22): rollup.Config.MaxSequencerDrift, attrs.NoTxPool, MaxSequencerDrift (1800초 프로토콜 상수), 타임스탬프 산술 유도, eip1559Denominator, eip1559Elasticity, 제네시스 EIP-1559 기본 상수(elasticity 10 / denom 50·250), Holocene/Jovian extraData 인코딩 (+14 more)

### Community 5 - "Wiki Catalogue and Runbooks"
Cohesion: 0.13
Nodes (22): Wiki Index, 2026-06-29 discv5 bootnode ingest, 2026-07-03 changeset cache miss ingest, 2026-07-04 receipts fetch ingest, 2026-07-28 txpool full ingest, 2026-08-24 block production and L1 RPC stall ingest, Wiki Log, Fetch Receipts Context Deadline Runbook (+14 more)

### Community 6 - "P2P Peering and Chain Isolation"
Cohesion: 0.11
Nodes (19): BlockingConnectionGater, 체인별 gossip 토픽 /optimism/<L2ChainID>/*/blocks, discv5 discovery, FilterEnodes, 방화벽 inbound 차단 (TCP/UDP 9222), inbound은 chainID로 게이팅되지 않는다, InterceptAccept / InterceptSecured, opp2p_blockPeer / blockAddr / blockSubnet (+11 more)

### Community 7 - "Fee Pricing and Pool Eviction"
Cohesion: 0.12
Nodes (19): base fee 미소각·vault 적립 (OP 고유 차이), BaseFeeVault (0x4200...0019), effectiveGasPrice, maxFeePerGas, maxPriorityFeePerGas, --min-suggested-priority-fee, op_suggest_tip_cap, SequencerFeeVault (0x4200...0011) (+11 more)

### Community 8 - "Observability and Profiling"
Cohesion: 0.12
Nodes (18): 연속 프로파일링 SRE 활용, /debug/pprof/*, Grafana Pyroscope, Grafana Tempo, LGTM observability, /metrics 엔드포인트, 관측성 4축(메트릭·로그·프로파일·트레이스), op-node Tracer 훅 인터페이스 (+10 more)

### Community 9 - "L1 Receipts Method Selection"
Cohesion: 0.12
Nodes (18): alchemy_getTransactionReceipts, AvailableReceiptsFetchingMethods, CU 비용 손익분기 모델, debug_getRawReceipts, erigon_getBlockReceiptsByBlockHash, eth_getBlockReceipts, eth_getTransactionReceipt batch (최후 fallback), --l1.rpckind (+10 more)

### Community 10 - "devp2p Peer Slot Control"
Cohesion: 0.11
Nodes (18): best_unconnected, ConnectionsConfig::default(), fill_outbound_slots, has_out_capacity, inbound trusted 예외 경로(outbound엔 없음), max_concurrent_outbound_dials, --max-inbound-peers, --max-outbound-peers (+10 more)

### Community 11 - "L1 Confirmation Depth"
Cohesion: 0.14
Nodes (16): confDepth 래퍼, sequencer depth 과다 → deposit-only 블록, ethereum.NotFound, L1BlockRefByNumber, confdepth.NewConfDepth, derive.NewDerivationPipeline, sequencing.NewL1OriginSelector, OP_NODE_SEQUENCER_L1_CONFS (+8 more)

### Community 12 - "Changeset Cache Miss Path"
Cohesion: 0.15
Nodes (14): Changeset cache MISS, falling back to DB-based computation, engine_forkchoiceUpdatedV3, engine_getPayloadV3, engine_newPayloadV3, ExecEngine interface, FinalizedBlockHash evict threshold, ForkchoiceState HeadBlockHash, Loki correlation query (+6 more)

### Community 13 - "Personal Namespace Removal"
Cohesion: 0.24
Nodes (10): -32601 method does not exist, accounts.Manager 순회, eth_accounts, op-geth v1.101702.3-rc.4 pin, personal_listAccounts, personal_listWallets, 비밀번호 RPC 전송·서버측 해제 키 위험, PersonalAccountAPI (+2 more)

### Community 14 - "CLSync vs ELSync Modes"
Cohesion: 0.24
Nodes (10): Engine.AddUnsafePayload, CLSync (consensus-layer), CLSync의 SYNCING 응답 허용 fallback, op-reth EL P2P snap sync, ELSync (execution-layer), Engine.InsertUnsafePayload, --l2.enginekind, SupportsPostFinalizationELSync (+2 more)

### Community 15 - "L1 Data Fee Predeploys"
Cohesion: 0.20
Nodes (10): GasPriceOracle (0x420...000F), _getL1FeeBedrock, _getL1FeeEcotone, _getL1FeeFjord, L1 data fee, L1Block predeploy (0x420...0015), L1FeeVault (0x4200...001A), operator fee (Isthmus+) (+2 more)

### Community 16 - "Engine API Block Cycle"
Cohesion: 0.32
Nodes (8): conductor 커밋 / asyncGossip, Engine API, engine_forkchoiceUpdatedV3, engine_getPayloadV3, engine_newPayloadV3, handleInvalid, sealingDuration (50ms), unsafe → safe → finalized 승격

### Community 17 - "Txpool Full Error Collapse"
Cohesion: 0.29
Nodes (8): -32000 geth txpool is full, -32003 txpool is full, DiscardedOnInsert, max_account_slots, rollup-boost parse_response_code, SpammerExceededCapacity, txpool_contentFrom, txpool_status

### Community 18 - "Txpool Locals Flags"
Cohesion: 0.67
Nodes (3): TransactionOrigin::External, --txpool.locals, --txpool.nolocals

## Knowledge Gaps
- **122 isolated node(s):** `--pprof.enabled`, `--tracing-otlp.filter`, `--tracing-otlp.sample-ratio`, `--logs-otlp`, `otlp-logs Cargo feature` (+117 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LGTM observability` connect `Observability and Profiling` to `L1 Receipts Method Selection`?**
  _High betweenness centrality (0.225) - this node is a cross-community bridge._
- **Why does `--l1.rpckind` connect `L1 Receipts Method Selection` to `Observability and Profiling`, `L1 Confirmation Depth`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `GlobalSyncExec` (e.g. with `op-node Tracer 훅 인터페이스` and `libp2p pubsub processLoop`) actually correct?**
  _`GlobalSyncExec` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `--pprof.enabled`, `--tracing-otlp.filter`, `--tracing-otlp.sample-ratio` to the rest of the system?**
  _139 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Txpool Local Exemption Rules` be split into smaller, more focused modules?**
  _Cohesion score 0.08831908831908832 - nodes in this community are weakly interconnected._
- **Should `L1 RPC Failure Diagnostics` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._
- **Should `Single Event Loop Blocking` be split into smaller, more focused modules?**
  _Cohesion score 0.09333333333333334 - nodes in this community are weakly interconnected._