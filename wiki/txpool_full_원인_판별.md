# txpool full 원인 판별

> 7 nodes · cohesion 0.33

## Key Concepts

- **op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단** (10 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **-32003(reth) vs -32000(op-geth)로 거절 클라이언트 판별** (3 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **로그 상관관계: New payload job created parent=X ↔ 최고 번호 MISS 블록 해시 일치** (2 connections) — `runbooks/op-reth-changeset-cache-miss.md`
- **원인 A — 서브풀 용량 초과 (DiscardedOnInsert, 기본 10,000tx/20MB)** (2 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **원인 B — 계정 슬롯 초과 (SpammerExceededCapacity, max_account_slots 16 + 미래 nonce)** (2 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **시퀀서 로그 원본 에러 문자열로 A/B 확증 (spammer vs pool size constraints)** (2 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`
- **rollup-boost/op-conductor 프록시는 에러 코드를 변형하지 않음 (parse_response_code)** (1 connections) — `runbooks/op-reth-sequencer-forward-txpool-full.md`

## Relationships

- [Wiki 인덱스 허브](Wiki_%EC%9D%B8%EB%8D%B1%EC%8A%A4_%ED%97%88%EB%B8%8C.md) (5 shared connections)
- [동기화·Engine API 빌드 사이클](%EB%8F%99%EA%B8%B0%ED%99%94%C2%B7Engine_API_%EB%B9%8C%EB%93%9C_%EC%82%AC%EC%9D%B4%ED%81%B4.md) (2 shared connections)
- [RPC 타임아웃·백오프 재시도](RPC_%ED%83%80%EC%9E%84%EC%95%84%EC%9B%83%C2%B7%EB%B0%B1%EC%98%A4%ED%94%84_%EC%9E%AC%EC%8B%9C%EB%8F%84.md) (1 shared connections)

## Source Files

- `runbooks/op-reth-changeset-cache-miss.md`
- `runbooks/op-reth-sequencer-forward-txpool-full.md`

## Audit Trail

- EXTRACTED: 20 (91%)
- INFERRED: 2 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*