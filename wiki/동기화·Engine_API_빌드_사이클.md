# 동기화·Engine API 빌드 사이클

> 11 nodes · cohesion 0.22

## Key Concepts

- **op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로** (10 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **op-node --syncmode (CLSync/ELSync)** (9 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **onBuildStart의 ForkchoiceState 조립 (HeadBlockHash = reth 로그의 parent=X)** (4 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **--p2p.sync.req-resp 서버 (payload_by_number 서빙, rate limit)** (3 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **Engine API 블록 빌드 사이클 (FCU-with-attributes → getPayload → newPayload → FCU)** (3 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **ReqResp P2P sync 클라이언트 제거 배경 (무서명 역순 인증·메모리 제약·complexity ceiling)** (2 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **op-node finalized 신호가 정하는 reth 캐시 축출 임계 (min(finalized, persisted_tip−64))** (2 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **부모 상태 overlay 조회 (state_by_block_hash) → changeset MISS → DB 폴백** (2 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **req-resp 프로토콜 ID /opstack/req/payload_by_number/<chainID>/0** (1 connections) — `concepts/op-node-p2p-peering.md`
- **공식 문서 p2p.sync.req-resp 서술의 stale 충돌 (코드가 정본)** (1 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **op-node 스톨 = 방아쇠가 아닌 MISS 버스트 증폭기** (1 connections) — `runbooks/op-reth-changeset-cache-miss.md`

## Relationships

- [Wiki 인덱스 허브](Wiki_%EC%9D%B8%EB%8D%B1%EC%8A%A4_%ED%97%88%EB%B8%8C.md) (7 shared connections)
- [P2P 피어링·부트노드 진단](P2P_%ED%94%BC%EC%96%B4%EB%A7%81%C2%B7%EB%B6%80%ED%8A%B8%EB%85%B8%EB%93%9C_%EC%A7%84%EB%8B%A8.md) (4 shared connections)
- [txpool full 원인 판별](txpool_full_%EC%9B%90%EC%9D%B8_%ED%8C%90%EB%B3%84.md) (2 shared connections)
- [L1 Receipt 조회 전략](L1_Receipt_%EC%A1%B0%ED%9A%8C_%EC%A0%84%EB%9E%B5.md) (1 shared connections)

## Source Files

- `concepts/op-node-p2p-peering.md`
- `concepts/op-node-syncmode-reqresp-deprecation.md`
- `runbooks/op-reth-changeset-cache-miss.md`

## Audit Trail

- EXTRACTED: 37 (97%)
- INFERRED: 1 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*