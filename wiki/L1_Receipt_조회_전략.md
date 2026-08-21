# L1 Receipt 조회 전략

> 9 nodes · cohesion 0.22

## Key Concepts

- **AvailableReceiptsFetchingMethods (kind → 메서드 비트필드)** (3 connections) — `concepts/op-node-l1-rpckind-receipts.md`
- **receipt 메서드 자동 강등(OnReceiptsMethodErr)과 주기적 복구** (3 connections) — `concepts/op-node-l1-rpckind-receipts.md`
- **RPCReceiptsFetcher (provKind 소비 지점)** (3 connections) — `concepts/op-node-l1-rpckind-receipts.md`
- **L1OriginSelector (sequencer의 L1 origin 전진 결정)** (2 connections) — `concepts/op-node-l1-confs-conf-depth.md`
- **PickBestReceiptsFetchingMethod (tx 수 기반 비용 손익분기 선택)** (2 connections) — `concepts/op-node-l1-rpckind-receipts.md`
- **CLSync (consensus-layer, op-node 주도 순차 NewPayload)** (2 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **CLSync의 SYNCING 허용 → EL snap sync fallback** (2 connections) — `concepts/op-node-syncmode-reqresp-deprecation.md`
- **alchemy_getTransactionReceipts (블록당 250 CU 정액)** (1 connections) — `concepts/op-node-l1-rpckind-receipts.md`
- **"resetting back RPC preferences" 경고 = kind 미스매치 신호** (1 connections) — `concepts/op-node-l1-rpckind-receipts.md`

## Relationships

- [L1 확인 깊이·inbound 차단](L1_%ED%99%95%EC%9D%B8_%EA%B9%8A%EC%9D%B4%C2%B7inbound_%EC%B0%A8%EB%8B%A8.md) (1 shared connections)
- [Wiki 인덱스 허브](Wiki_%EC%9D%B8%EB%8D%B1%EC%8A%A4_%ED%97%88%EB%B8%8C.md) (1 shared connections)
- [동기화·Engine API 빌드 사이클](%EB%8F%99%EA%B8%B0%ED%99%94%C2%B7Engine_API_%EB%B9%8C%EB%93%9C_%EC%82%AC%EC%9D%B4%ED%81%B4.md) (1 shared connections)

## Source Files

- `concepts/op-node-l1-confs-conf-depth.md`
- `concepts/op-node-l1-rpckind-receipts.md`
- `concepts/op-node-syncmode-reqresp-deprecation.md`

## Audit Trail

- EXTRACTED: 15 (79%)
- INFERRED: 4 (21%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*