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
- [reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")](concepts/reth-txpool-capacity-slot-limits.md) — 서브풀 4종 한도(기본 10,000tx/20MB) 초과의 DiscardedOnInsert와 계정 슬롯(max_account_slots 기본 16) 초과의 SpammerExceededCapacity가 RPC 계층에서 동일한 -32003 "txpool is full"로 붕괴되어 원인 구분이 불가능한 메커니즘, max_account_slots는 하드캡이 아닌 미래 nonce in-flight 깊이 제한(온체인 nonce 일치 tx는 항상 통과), eth_sendRawTransaction은 External origin이라 local 면제 대상이 아님, geth(-32000)와의 코드 차이
- [op-reth --max-outbound-peers & devp2p 피어 슬롯 제어](concepts/op-reth-max-outbound-peers.md) — outbound(기본 100)/inbound(기본 30) 별도 카운터, 실제 다이얼은 `num_pending_out < max_concurrent_outbound_dials(30, CLI 없음)` AND `num_outbound < max_outbound`로 게이트, trusted는 우선권만 있고 outbound 상한 면제 없음(inbound만 예외 경로), --max-peers는 배타적이며 outbound=max_peers/3(2:1 in:out), 상한 도달 시 평균 5분 주기 UselessPeer 로테이션, OP 맥락에서 EL 피어는 snap sync·tx gossip에 민감
- [op-node 동기화 모드(CLSync/ELSync) & ReqResp P2P Sync Deprecation](concepts/op-node-syncmode-reqresp-deprecation.md) — --syncmode consensus-layer/execution-layer 차이(op-node 주도 순차 실행 vs op-reth 주도 snap sync)와 CL 레벨 ReqResp sync 클라이언트 제거(deprecated no-op 플래그), gap 복구가 op-reth EL snap sync로 대체된 변화, op-reth의 post-finalization EL sync 이점(--l2.enginekind=reth), 남은 서버·rate limit
- [OP Stack 시퀀서 블록 생성 과정 (2초 사이클)](concepts/op-stack-block-production.md) — 2초마다 L2 블록 하나를 만드는 9단계 사이클(알람→L1 origin 선택→deposit 수집→forkchoiceUpdated/getPayload/newPayload→gossip)과 3가지 제약(고정 블록타임·L1 origin 시간 역전 금지·max sequencer drift 1800초 초과 시 deposit-only), 헤드 갱신 시 500ms 선캐싱으로 정상 경로의 L1 호출이 0회가 되는 메커니즘, 단계별 타임아웃 지도
- [op-node 단일 이벤트 루프 설계 (GlobalSynchronous executor)](concepts/op-node-event-loop-design.md) — 모든 deriver가 드라이버 goroutine 하나 위에서 직렬 실행되는 6단계 코드 근거 사슬, 락 대신 소유권으로 경합을 없애는 설계 의도의 증거(미머지 events-parallel 브랜치·Executor 추상화·attributes.go:85), 창구를 잠그는 백오프(retry.Do)와 잠그지 않는 백오프(nextAction/time.After)의 구분, libp2p pubsub·eventbus와의 대조
- [OP Stack L2 블록타임 설정 및 확인 (rollup.Config.BlockTime)](concepts/op-stack-l2-block-time.md) — 초 단위 정수로 rollup config에만 존재(제약은 0 불가·L1 블록타임 이하 둘뿐), 온체인 컨트랙트에 기록되지 않아 SystemConfig 조회 불가, 타임스탬프 소급 계산 때문에 배포 후 변경은 하드포크, optimism_rollupConfig·rollup.json·타임스탬프 실측·superchain registry 4가지 확인 경로와 블록타임 단축 시 정지 피해가 비례 증가하는 이유
- [op-geth personal 네임스페이스 제거 (personal_listAccounts / personal_listWallets)](concepts/op-geth-personal-namespace-removal.md) — 두 메서드의 반환 차이(평탄한 주소 배열 vs 백엔드 컨테이너+잠금상태)와 op-geth 버전별 존재 여부(v1.101311은 --rpc.enabledeprecatedpersonal로만 활성, v1.101503 이후 삭제, op-reth는 미구현), 비밀번호 RPC 전송·서버측 해제 키라는 제거 이유, eth_accounts·clef·클라이언트 사이드 서명 대체 경로

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
- [op-node FindL1Origin 무기한 대기로 인한 블록 생산 정지 진단](runbooks/op-node-find-l1-origin-stall.md) — 시퀀서의 L1 origin 선택에 시퀀서 레벨 마감시한이 없어(sequencer.go:540 ctx := d.ctx) RPC 기본 10초 동안 단일 이벤트 루프가 잠기고 고정 1초 뒤 재시도가 반복되어 잠김 비율 약 91%가 되는 메커니즘, 실패 유형별 주기 차이(refused 1초 vs hang 11초 vs 2회 호출 20초), 리셋 중첩 시 블록당 65초, 원래 타임아웃 에러가 ErrNextL1OriginRequired로 대체되는 로그 함정, 진단 로그 4종·pprof 확증·대응 우선순위
- [op-reth discv5 Bootnode Timeout 진단](runbooks/op-reth-discv5-bootnode-timeout.md) — enode 부트노드가 `failed adding boot node ... err=Timeout`으로 실패하는 원인(enode→ENR 라이브 요청)과 해결(ENR 사용·포트·UDP 점검)
- [op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로](runbooks/op-reth-changeset-cache-miss.md) — 무해·자가복구 WARN이 op-node의 FCU-with-attributes 블록 빌드에서 유발되는 경로(parent=X↔unsafe 헤드 매핑, finalized→evict 임계)와 진단 체크리스트
- [op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단](runbooks/op-reth-sequencer-forward-txpool-full.md) — 로그 주체가 시퀀서가 아닌 **replica**(--rollup.sequencer 포워딩 노드)임을 확정하는 코드 경로, 재시도·로컬 풀 보관 없이 즉시 실패하는 동작, 시퀀서 서브풀 용량(A) vs 계정 슬롯 초과(B) 분기 진단 절차와 원본 에러 문자열로 확증하는 법, -32003/-32000으로 거절 클라이언트 판별
- [op-node "failed to fetch receipts ... for L1 sysCfg update" 진단 (RPC 타임아웃 / 연결 리셋)](runbooks/op-node-fetch-receipts-context-deadline.md) — L1 origin 전진 시 receipts 조회가 L1 RPC 실패(timeout / connection reset)로 시퀀서가 백오프하는 로그의 인과 사슬·일시적/자가복구 판정·단일 이벤트 루프 블로킹이 블록 생산을 멈추는 메커니즘(연속 실패 지수 백오프 타임라인)·원인 후보·진단 절차
