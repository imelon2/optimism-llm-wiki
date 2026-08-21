# Wiki 인덱스 허브

> 19 nodes · cohesion 0.20

## Key Concepts

- **Wiki Log (append-only 변경 이력)** (16 connections) — `log.md`
- **Wiki Index (OP Stack LLM Wiki 전체 카탈로그)** (15 connections) — `index.md`
- **OP Stack 노드 ↔ Grafana LGTM 관측성 연동** (11 connections) — `concepts/observability-grafana-integration.md`
- **op-reth --txpool.nolocals (local exemption 전체 비활성화)** (10 connections) — `concepts/op-reth-txpool-nolocals.md`
- **OP Stack 트랜잭션 수수료 & EIP-1559 모델** (9 connections) — `concepts/op-stack-eip1559-fees.md`
- **op-node "failed to fetch receipts ... for L1 sysCfg update" 진단** (9 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **op-node --l1.rpckind (L1 RPC 공급자 힌트)** (8 connections) — `concepts/op-node-l1-rpckind-receipts.md`
- **PoolErrorKind::DiscardedOnInsert (용량 초과 = 사실상 underpriced)** (7 connections) — `concepts/reth-txpool-capacity-slot-limits.md`
- **op-node L1 Confirmation Depth (--verifier.l1-confs vs --sequencer.l1-confs)** (6 connections) — `concepts/op-node-l1-confs-conf-depth.md`
- **L1 data fee (maxFeePerGas로 상한 불가한 별도 항목)** (2 connections) — `concepts/op-stack-eip1559-fees.md`
- **Index-first 탐색 규약 (index.md → 드릴다운)** (2 connections) — `index.md`
- **모순/문서-코드 불일치 flag 관행 (ingest 시 정정 기록)** (2 connections) — `log.md`
- **기본값 standard 채택 이유 (eth_getBlockReceipts 표준화)** (1 connections) — `concepts/op-node-l1-rpckind-receipts.md`
- **nolocals의 실효성은 sequencer 노드에 한정 (replica는 forward)** (1 connections) — `concepts/op-reth-txpool-nolocals.md`
- **실행 계층 정본 한계 (op-geth pinned 모듈 · op-revm 외부 크레이트)** (1 connections) — `concepts/op-stack-eip1559-fees.md`
- **GasPriceOracle 예치 컨트랙트 (Bedrock/Ecotone/Fjord 분기)** (1 connections) — `concepts/op-stack-eip1559-fees.md`
- **ingest 로그 엔트리 형식 (`## [YYYY-MM-DD] <op> | <대상>`)** (1 connections) — `log.md`
- **동반 경고 "resetting back RPC preferences" — l1.rpckind 미스매치 신호** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **흔한 착각 — 포워딩된 tx도 시퀀서에서 TransactionOrigin::External** (1 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`

## Relationships

- [P2P 피어링·부트노드 진단](P2P_%ED%94%BC%EC%96%B4%EB%A7%81%C2%B7%EB%B6%80%ED%8A%B8%EB%85%B8%EB%93%9C_%EC%A7%84%EB%8B%A8.md) (9 shared connections)
- [동기화·Engine API 빌드 사이클](%EB%8F%99%EA%B8%B0%ED%99%94%C2%B7Engine_API_%EB%B9%8C%EB%93%9C_%EC%82%AC%EC%9D%B4%ED%81%B4.md) (7 shared connections)
- [txpool local 면제·수수료 정책](txpool_local_%EB%A9%B4%EC%A0%9C%C2%B7%EC%88%98%EC%88%98%EB%A3%8C_%EC%A0%95%EC%B1%85.md) (5 shared connections)
- [txpool full 원인 판별](txpool_full_%EC%9B%90%EC%9D%B8_%ED%8C%90%EB%B3%84.md) (5 shared connections)
- [관측성·프로파일링 스택](%EA%B4%80%EC%B8%A1%EC%84%B1%C2%B7%ED%94%84%EB%A1%9C%ED%8C%8C%EC%9D%BC%EB%A7%81_%EC%8A%A4%ED%83%9D.md) (3 shared connections)
- [RPC 타임아웃·백오프 재시도](RPC_%ED%83%80%EC%9E%84%EC%95%84%EC%9B%83%C2%B7%EB%B0%B1%EC%98%A4%ED%94%84_%EC%9E%AC%EC%8B%9C%EB%8F%84.md) (2 shared connections)
- [피어 발견·아웃바운드 다이얼](%ED%94%BC%EC%96%B4_%EB%B0%9C%EA%B2%AC%C2%B7%EC%95%84%EC%9B%83%EB%B0%94%EC%9A%B4%EB%93%9C_%EB%8B%A4%EC%9D%B4%EC%96%BC.md) (1 shared connections)
- [L1 확인 깊이·inbound 차단](L1_%ED%99%95%EC%9D%B8_%EA%B9%8A%EC%9D%B4%C2%B7inbound_%EC%B0%A8%EB%8B%A8.md) (1 shared connections)
- [L1 Receipt 조회 전략](L1_Receipt_%EC%A1%B0%ED%9A%8C_%EC%A0%84%EB%9E%B5.md) (1 shared connections)

## Source Files

- `concepts/observability-grafana-integration.md`
- `concepts/op-node-l1-confs-conf-depth.md`
- `concepts/op-node-l1-rpckind-receipts.md`
- `concepts/op-reth-txpool-nolocals.md`
- `concepts/op-stack-eip1559-fees.md`
- `concepts/reth-txpool-capacity-slot-limits.md`
- `index.md`
- `log.md`
- `runbooks/op-node-fetch-receipts-context-deadline.md`
- `runbooks/op-reth-sequencer-forward-txpool-full.md`

## Audit Trail

- EXTRACTED: 98 (94%)
- INFERRED: 6 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*