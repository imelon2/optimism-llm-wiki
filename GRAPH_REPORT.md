# Graph Report - ./wiki  (2026-08-31)

## Corpus Check
- 11 files · ~27,853 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 310 nodes · 438 edges · 19 communities (17 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.8)
- Token cost: 138,220 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Transaction Submission & Local Exemption|Transaction Submission & Local Exemption]]
- [[_COMMUNITY_P2P Peering & Chain Isolation|P2P Peering & Chain Isolation]]
- [[_COMMUNITY_Sqrt Broadcast & Tx Gossip|Sqrt Broadcast & Tx Gossip]]
- [[_COMMUNITY_L1 Receipts & Derivation Stalls|L1 Receipts & Derivation Stalls]]
- [[_COMMUNITY_Single Event Loop Design|Single Event Loop Design]]
- [[_COMMUNITY_Sequencer L1 Origin Stalls|Sequencer L1 Origin Stalls]]
- [[_COMMUNITY_L1 RPC Kind & Receipts Methods|L1 RPC Kind & Receipts Methods]]
- [[_COMMUNITY_EIP-1559 Params & Block Time|EIP-1559 Params & Block Time]]
- [[_COMMUNITY_L1 Confirmation Depth|L1 Confirmation Depth]]
- [[_COMMUNITY_Engine API & Payload Building|Engine API & Payload Building]]
- [[_COMMUNITY_Observability & Profiling|Observability & Profiling]]
- [[_COMMUNITY_Sync Modes & ReqResp Deprecation|Sync Modes & ReqResp Deprecation]]
- [[_COMMUNITY_discv5 Bootnode Discovery|discv5 Bootnode Discovery]]
- [[_COMMUNITY_Sequencer Block Production Cycle|Sequencer Block Production Cycle]]
- [[_COMMUNITY_personal Namespace Removal|personal Namespace Removal]]
- [[_COMMUNITY_L1 Data Fee & Gas Oracle|L1 Data Fee & Gas Oracle]]
- [[_COMMUNITY_Base Fee & Fee Vaults|Base Fee & Fee Vaults]]
- [[_COMMUNITY_OTLP Log Export|OTLP Log Export]]
- [[_COMMUNITY_ReqResp Payload Server|ReqResp Payload Server]]

## God Nodes (most connected - your core abstractions)
1. `트랜잭션 √n 브로드캐스트 규칙 (원본 전송 vs 해시 알림)` - 22 edges
2. `OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)` - 21 edges
3. `reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")` - 18 edges
4. `op-node P2P Peering & Chain Isolation` - 17 edges
5. `op-reth --max-outbound-peers & devp2p 피어 슬롯 제어` - 17 edges
6. `OP Stack 시퀀서 블록 생성 과정 (2초 사이클)` - 16 edges
7. `txpool nonce 갭으로 인한 트랜잭션 전파 정지` - 15 edges
8. `op-reth --txpool.nolocals & Local Transaction Exemption` - 14 edges
9. `op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단` - 12 edges
10. `AvailableReceiptsFetchingMethods` - 10 edges

## Surprising Connections (you probably didn't know these)
- `op-node Tracer 훅 인터페이스` --semantically_similar_to--> `GlobalSyncExec`  [INFERRED] [semantically similar]
  concepts/observability-grafana-integration.md → concepts/op-node-event-loop-design.md
- `failed adding boot node err=Timeout` --semantically_similar_to--> `context deadline exceeded`  [INFERRED] [semantically similar]
  runbooks/op-reth-discv5-bootnode-timeout.md → runbooks/op-node-fetch-receipts-context-deadline.md
- `Wiki Index` --references--> `op-node P2P Peering & Chain Isolation`  [EXTRACTED]
  index.md → concepts/op-node-p2p-peering.md
- `Wiki Log` --references--> `op-node P2P Peering & Chain Isolation`  [EXTRACTED]
  log.md → concepts/op-node-p2p-peering.md
- `Wiki Index` --references--> `op-reth --max-outbound-peers & devp2p 피어 슬롯 제어`  [EXTRACTED]
  index.md → concepts/op-reth-max-outbound-peers.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Ingress → 시퀀서 트랜잭션 도달 전체 흐름** — concepts_op_stack_tx_ingress_propagation, concepts_tx_propagation_sqrt_broadcast, concepts_txpool_nonce_gap_propagation_stall, concepts_reth_txpool_capacity_slot_limits, concepts_op_stack_block_production [INFERRED 0.85]
- **-32003 "txpool is full" 진단 사슬 (replica 로그 → 원인 A/B → local 면제)** — runbooks_op_reth_sequencer_forward_txpool_full, concepts_reth_txpool_capacity_slot_limits, concepts_op_reth_txpool_nolocals, concepts_reth_txpool_capacity_slot_limits_discardedoninsert, concepts_reth_txpool_capacity_slot_limits_spammerexceededcapacity, concepts_reth_txpool_capacity_slot_limits_error_32003_txpool_is_full [EXTRACTED 1.00]
- **CL libp2p(블록) vs EL devp2p(트랜잭션) 두 P2P 레이어 분리** — concepts_op_node_p2p_peering, concepts_op_reth_max_outbound_peers, concepts_op_stack_tx_ingress_propagation_two_p2p_networks, concepts_op_node_p2p_peering_libp2p_block_gossip, concepts_op_reth_max_outbound_peers_devp2p_rlpx_network [EXTRACTED 1.00]

## Communities (19 total, 2 thin omitted)

### Community 0 - "Transaction Submission & Local Exemption"
Cohesion: 0.08
Nodes (43): clef 외부 서명자, eth_sendRawTransaction, op-reth --txpool.nolocals & Local Transaction Exemption, local 트랜잭션 면제 3종 (slot/price/eviction), LocalTransactionConfig, --txpool.no-local-transactions-propagation, eth_sendRawTransaction → TransactionOrigin::External, --txpool.locals (+35 more)

### Community 1 - "P2P Peering & Chain Isolation"
Cohesion: 0.13
Nodes (28): op-node P2P Peering & Chain Isolation, BlockingConnectionGater, 체인별 gossip 토픽 /optimism/<L2ChainID>/N/blocks, discv5 discovery (ListenV5), FilterEnodes(), 방화벽 P2P 포트(9222) inbound 차단, InterceptAccept / InterceptSecured 게이팅 한계, libp2p(gossipsub) 블록 전파 네트워크 (+20 more)

### Community 2 - "Sqrt Broadcast & Tx Gossip"
Cohesion: 0.14
Nodes (24): eviction 면제의 서브풀 비대칭 (pending만 보호), 트랜잭션 √n 브로드캐스트 규칙 (원본 전송 vs 해시 알림), buffer_hashes() — reth의 실제 지연 지점, choosePeers (op-geth, siphash + txSender), devp2p caps/eth.md — Transaction Exchange, EIP-2464 (eth/65 announcements and retrievals), fetched_transactions 메트릭, hashes_pending_fetch 메트릭 (+16 more)

### Community 3 - "L1 Receipts & Derivation Stalls"
Cohesion: 0.10
Nodes (22): batchCallTimeout, CachingReceiptsProvider, callTimeout, context deadline exceeded, DerivationPipeline.Step, event.NewGlobalSynchronous, Exponential backoff recovery window, FetchReceipts (+14 more)

### Community 4 - "Single Event Loop Design"
Cohesion: 0.11
Nodes (19): 블로킹 백오프(창구 잠김), Drain(), Emit / executor.Enqueue, driver eventLoop, Executor 인터페이스, GlobalSyncExec, pprof goroutine 덤프 진단, libp2p eventbus Emit 배압 (+11 more)

### Community 5 - "Sequencer L1 Origin Stalls"
Cohesion: 0.11
Nodes (19): connection reset by peer, Engine failed temporarily, backing off sequencer, failed to fetch receipts for L1 sysCfg update, Fetch Receipts Context Deadline Runbook, NewTemporaryError, Sequencer.onEngineTemporaryError, ErrNextL1OriginRequired, Error finding next L1 Origin (+11 more)

### Community 6 - "L1 RPC Kind & Receipts Methods"
Cohesion: 0.12
Nodes (18): alchemy_getTransactionReceipts, AvailableReceiptsFetchingMethods, CU 비용 손익분기 모델, debug_getRawReceipts, erigon_getBlockReceiptsByBlockHash, eth_getBlockReceipts, eth_getTransactionReceipt batch (최후 fallback), --l1.rpckind (+10 more)

### Community 7 - "EIP-1559 Params & Block Time"
Cohesion: 0.12
Nodes (18): eip1559Denominator, eip1559Elasticity, 제네시스 EIP-1559 기본 상수(elasticity 10 / denom 50·250), Holocene/Jovian extraData 인코딩, minBaseFee / setMinBaseFee, setEIP1559Params, SystemConfig, ErrBlockTimeZero (+10 more)

### Community 8 - "L1 Confirmation Depth"
Cohesion: 0.14
Nodes (16): confDepth 래퍼, sequencer depth 과다 → deposit-only 블록, ethereum.NotFound, L1BlockRefByNumber, rollup.Config.MaxSequencerDrift, confdepth.NewConfDepth, derive.NewDerivationPipeline, sequencing.NewL1OriginSelector (+8 more)

### Community 9 - "Engine API & Payload Building"
Cohesion: 0.13
Nodes (16): op-conductor health monitor failover, unsafe head stall, Changeset cache MISS, falling back to DB-based computation, engine_forkchoiceUpdatedV3, engine_getPayloadV3, engine_newPayloadV3, ExecEngine interface, FinalizedBlockHash evict threshold (+8 more)

### Community 10 - "Observability & Profiling"
Cohesion: 0.15
Nodes (15): 연속 프로파일링 SRE 활용, /debug/pprof/*, Grafana Pyroscope, Grafana Tempo, LGTM observability, /metrics 엔드포인트, 관측성 4축(메트릭·로그·프로파일·트레이스), op-node Tracer 훅 인터페이스 (+7 more)

### Community 11 - "Sync Modes & ReqResp Deprecation"
Cohesion: 0.16
Nodes (14): Engine.AddUnsafePayload, CLSync (consensus-layer), CLSync의 SYNCING 응답 허용 fallback, op-reth EL P2P snap sync, ELSync (execution-layer), Engine.InsertUnsafePayload, --l2.enginekind, --p2p.sync.onlyReqToStatic (deprecated no-op) (+6 more)

### Community 12 - "discv5 Bootnode Discovery"
Cohesion: 0.15
Nodes (13): bootstrap, DEFAULT_DISCOVERY_V5_PORT, discport port mismatch, discv5.add_enr, discv5 Bootnode Timeout Runbook, discv5.request_enr, EL CL bootnode confusion, enode (+5 more)

### Community 13 - "Sequencer Block Production Cycle"
Cohesion: 0.33
Nodes (11): OP Stack 시퀀서 블록 생성 과정 (2초 사이클), Engine API 호출 순서 (forkchoiceUpdatedV3 → getPayloadV3 → newPayloadV3), FindL1Origin (L1 origin 선택), 고정 블록 간격 (타임스탬프 산술 유도), handleInvalid() 재스케줄, L1 origin 500ms best-effort 선캐싱, max sequencer drift 1800초, 9단계 2초 블록 생성 사이클 (+3 more)

### Community 14 - "personal Namespace Removal"
Cohesion: 0.24
Nodes (10): -32601 method does not exist, accounts.Manager 순회, eth_accounts, op-geth v1.101702.3-rc.4 pin, personal_listAccounts, personal_listWallets, 비밀번호 RPC 전송·서버측 해제 키 위험, PersonalAccountAPI (+2 more)

### Community 15 - "L1 Data Fee & Gas Oracle"
Cohesion: 0.20
Nodes (10): GasPriceOracle (0x420...000F), _getL1FeeBedrock, _getL1FeeEcotone, _getL1FeeFjord, L1 data fee, L1Block predeploy (0x420...0015), L1FeeVault (0x4200...001A), operator fee (Isthmus+) (+2 more)

### Community 16 - "Base Fee & Fee Vaults"
Cohesion: 0.29
Nodes (8): base fee 미소각·vault 적립 (OP 고유 차이), BaseFeeVault (0x4200...0019), effectiveGasPrice, maxFeePerGas, maxPriorityFeePerGas, --min-suggested-priority-fee, op_suggest_tip_cap, SequencerFeeVault (0x4200...0011)

## Knowledge Gaps
- **83 isolated node(s):** `--pprof.enabled`, `--tracing-otlp.filter`, `--tracing-otlp.sample-ratio`, `--logs-otlp`, `otlp-logs Cargo feature` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `--sequencer.l1-confs` connect `L1 Confirmation Depth` to `Sequencer Block Production Cycle`?**
  _High betweenness centrality (0.268) - this node is a cross-community bridge._
- **Why does `OP Stack 시퀀서 블록 생성 과정 (2초 사이클)` connect `Sequencer Block Production Cycle` to `Transaction Submission & Local Exemption`, `P2P Peering & Chain Isolation`, `Sqrt Broadcast & Tx Gossip`?**
  _High betweenness centrality (0.262) - this node is a cross-community bridge._
- **Why does `L1 origin 500ms best-effort 선캐싱` connect `Sequencer Block Production Cycle` to `L1 Confirmation Depth`?**
  _High betweenness centrality (0.238) - this node is a cross-community bridge._
- **What connects `--pprof.enabled`, `--tracing-otlp.filter`, `--tracing-otlp.sample-ratio` to the rest of the system?**
  _96 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Transaction Submission & Local Exemption` be split into smaller, more focused modules?**
  _Cohesion score 0.07928118393234672 - nodes in this community are weakly interconnected._
- **Should `P2P Peering & Chain Isolation` be split into smaller, more focused modules?**
  _Cohesion score 0.13227513227513227 - nodes in this community are weakly interconnected._
- **Should `Sqrt Broadcast & Tx Gossip` be split into smaller, more focused modules?**
  _Cohesion score 0.14130434782608695 - nodes in this community are weakly interconnected._