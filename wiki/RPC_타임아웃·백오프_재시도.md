# RPC 타임아웃·백오프 재시도

> 9 nodes · cohesion 0.22

## Key Concepts

- **L1Traversal.AdvanceL1Block — L1 origin 전진 시 receipts 조회 지점** (4 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **TemporaryError 래핑 & 시퀀서 백오프 (origin 미전진·자가복구)** (3 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **지수 백오프 재시도와 회복 창 (min(2^n×1s,10s)+jitter, 대기 중 루프 해제)** (2 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **GlobalSynchronous 단일 이벤트 루프 (동기 블로킹 RPC가 블록 생산을 멈춤)** (2 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **forward_raw_transaction / _conditional — request()의 유일한 호출자 2곳** (2 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **포워딩 실패 시 `?` 조기반환 — 재시도 없음·로컬 풀 미보관(tx 유실)** (2 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **SequencerClient::request — "HTTP request to sequencer failed" WARN 발생 지점** (2 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **L1 RPC 클라이언트 호출 타임아웃 기본값 (callTimeout 10s / batchCallTimeout 20s)** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`
- **UpdateSystemConfigWithL1Receipts — L1 ConfigUpdate 이벤트 스캔·SystemConfig 갱신** (1 connections) — `runbooks/op-node-fetch-receipts-context-deadline.md`

## Relationships

- [Wiki 인덱스 허브](Wiki_%EC%9D%B8%EB%8D%B1%EC%8A%A4_%ED%97%88%EB%B8%8C.md) (2 shared connections)
- [txpool full 원인 판별](txpool_full_%EC%9B%90%EC%9D%B8_%ED%8C%90%EB%B3%84.md) (1 shared connections)

## Source Files

- `runbooks/op-node-fetch-receipts-context-deadline.md`
- `runbooks/op-reth-sequencer-forward-txpool-full.md`

## Audit Trail

- EXTRACTED: 17 (89%)
- INFERRED: 2 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*