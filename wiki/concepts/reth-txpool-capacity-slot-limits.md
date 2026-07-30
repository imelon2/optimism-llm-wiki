---
type: Concept
title: reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")
description: 서브풀 4종의 용량 한도(기본 10,000 tx / 20MB)와 계정당 슬롯 제한(max_account_slots 기본 16)이 각각 DiscardedOnInsert / SpammerExceededCapacity 에러를 만들고, 둘이 RPC 계층에서 동일한 -32003 "txpool is full" 메시지로 붕괴되어 원인 구분이 불가능해지는 메커니즘
resource: https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/pool/txpool.rs
source_commit: aaeb6c0154
tags: [op-stack, reth, txpool, sequencer, l2]
timestamp: 2026-07-28T00:00:00Z
chain: l2
version: bedrock
---

# reth/op-reth txpool 용량 한도 & 계정 슬롯 제한 (-32003 "txpool is full")

## 개요

reth 계열 노드가 트랜잭션을 거절하며 반환하는 `-32003: txpool is full`은 **원인이 서로 다른 두 상황이 하나의 메시지로 뭉개진 결과**다. 문자 그대로 "풀이 꽉 찼다"인 경우도 있지만, **풀이 텅 비어 있어도 한 계정이 슬롯 한도를 넘기면 똑같은 메시지가 나온다.** 이 구분을 모르면 시퀀서 용량만 계속 올리면서 원인을 못 잡는다.

비유하면 — 주차장 안내판에 "만차"라는 등 하나만 달려 있는데, 실제로는 (a) 정말 자리가 없을 때와 (b) "한 사람이 차 16대를 이미 대놨으니 더는 안 받는다"일 때 **같은 등이 켜진다.** 안내판만 보면 둘을 구분할 수 없다.

핵심 사실:

1. **두 원인이 같은 코드·같은 문자열로 매핑된다.** `PoolErrorKind::DiscardedOnInsert`(용량 초과)와 `PoolErrorKind::SpammerExceededCapacity`(계정 슬롯 초과)가 모두 `RpcPoolError::TxPoolOverflow` → `-32003 "txpool is full"`이 된다.
2. **`max_account_slots`(기본 16)는 "총 발송량 제한"이 아니라 "동시 대기(in-flight) 깊이 제한"이다.** 그리고 하드캡도 아니다 — 온체인 nonce와 일치하는 tx는 슬롯이 꽉 차도 항상 통과한다.
3. **`-32003`이라는 코드 자체가 클라이언트 지문이다.** go-ethereum/op-geth도 문자열은 똑같이 `txpool is full`이지만 코드는 `-32000`이다.

이 페이지는 reth **v2.3.0** 기준이다. op-reth는 이 버전을 pin한다 (`resource/optimism/rust/Cargo.toml:411` — `reth-transaction-pool = { git = "https://github.com/paradigmxyz/reth", tag = "v2.3.0" }`).

## 핵심 동작/책임

### 에러 매핑 — 두 원인 → 하나의 -32003

`crates/rpc/rpc-eth-types/src/error/mod.rs`:

```rust
impl From<PoolError> for RpcPoolError {
    fn from(err: PoolError) -> Self {
        match err.kind {
            PoolErrorKind::SpammerExceededCapacity(_) |
            PoolErrorKind::DiscardedOnInsert => Self::TxPoolOverflow,
            ...
        }
    }
}

impl From<RpcPoolError> for jsonrpsee_types::error::ErrorObject<'static> {
    fn from(error: RpcPoolError) -> Self {
        match error {
            RpcPoolError::TxPoolOverflow =>
                rpc_error_with_code(EthRpcErrorCode::TransactionRejected.code(), error.to_string()),
            ...
        }
    }
}
```

`RpcPoolError::TxPoolOverflow`의 메시지는 `#[error("txpool is full")]`, `EthRpcErrorCode::TransactionRejected`는 EIP-1474의 **-32003**이다.

문제는 풀 내부의 **원본 메시지는 서로 다른데** RPC 계층에서 버려진다는 점이다 (`crates/transaction-pool/src/error.rs`):

```rust
/// Thrown when the number of unique transactions of a sender exceeded the slot capacity.
#[error("rejected due to {0} being identified as a spammer")]
SpammerExceededCapacity(Address),

/// Thrown when a new transaction is added to the pool, but then immediately discarded to
/// respect the size limits of the pool.
#[error("transaction discarded outright due to pool size constraints")]
DiscardedOnInsert,
```

→ **원인 구분은 RPC 응답이 아니라 시퀀서 노드의 로그/메트릭에서 해야 한다.**

### 원인 A — DiscardedOnInsert (진짜 용량 초과)

tx는 **일단 삽입에 성공한 뒤**, 한도 정리(`discard_worst`)에서 축출 대상에 자기 자신이 포함되었을 때만 이 에러가 된다 (`crates/transaction-pool/src/pool/mod.rs:697-728`):

```rust
            // Enforce the pool size limits if at least one transaction was added successfully
            let discarded = if results.iter().any(Result::is_ok) {
                pool.discard_worst()
            } else { Default::default() };
...
            // A newly added transaction may be immediately discarded, so we need to
            // adjust the result here
            for res in &mut results {
                if let Ok(AddedTransactionOutcome { hash, .. }) = res &&
                    discarded_hashes.contains(hash)
                {
                    *res = Err(PoolError::new(*hash, PoolErrorKind::DiscardedOnInsert))
                }
            }
```

의미가 중요하다. **"풀이 꽉 찼다"가 아니라 "꽉 찬 풀에서 당신 tx가 가장 먼저 버려질 후보였다"** — 사실상 *underpriced*의 다른 얼굴이며, gas price를 올리면 통과할 수 있다.

한도는 서브풀 4종 중 **하나라도** 넘으면 발동한다 (`crates/transaction-pool/src/config.rs`):

```rust
pub const fn is_exceeded(&self, pool_size: PoolSize) -> bool {
    self.blob_limit.is_exceeded(pool_size.blob, pool_size.blob_size) ||
        self.pending_limit.is_exceeded(pool_size.pending, pool_size.pending_size) ||
        self.basefee_limit.is_exceeded(pool_size.basefee, pool_size.basefee_size) ||
        self.queued_limit.is_exceeded(pool_size.queued, pool_size.queued_size)
}
```

기본값은 **서브풀당 10,000 tx / 20 MB** (`TXPOOL_SUBPOOL_MAX_TXS_DEFAULT = 10_000`, `TXPOOL_SUBPOOL_MAX_SIZE_MB_DEFAULT = 20`).

### 원인 B — SpammerExceededCapacity (계정 슬롯 초과)

`crates/transaction-pool/src/pool/txpool.rs:1864-1881` (`ensure_valid`):

```rust
        if !self.local_transactions_config.is_local(transaction.origin, transaction.sender_ref()) {
            let current_txs =
                self.tx_counter.get(&transaction.sender_id()).copied().unwrap_or_default();

            // Reject transactions if sender's capacity is exceeded.
            // If transaction's nonce matches on-chain nonce always let it through
            if current_txs >= self.max_account_slots && transaction.nonce() > on_chain_nonce {
                return Err(InsertErr::ExceededSenderTransactionsCapacity { ... })
            }
        }
```

거부되려면 **세 조건이 모두** 성립해야 한다:

| # | 조건 | 비고 |
|---|------|------|
| 1 | 발신자가 local이 아님 | `--txpool.locals`로 등록하면 우회 |
| 2 | 그 발신자의 풀 내 tx 수 ≥ `max_account_slots` | 기본 **16** (`TXPOOL_MAX_ACCOUNT_SLOTS_PER_SENDER`) |
| 3 | 새 tx의 nonce **>** 온체인 nonce | nonce가 같으면(=즉시 실행 가능) 무조건 통과 |

**풀 전체는 텅 비어 있어도 발생한다.** 하나의 hot wallet(브릿지 relayer, 배치 봇, faucet)이 nonce를 앞질러 17개 이상 쌓으면 바로 이 에러가 나온다.

### max_account_slots의 정확한 의미 — 3가지 단서

**① 세는 대상은 서브풀 합산.** `tx_counter`는 `AllTransactions`("Container for _all_ transaction in the pool")의 필드이고, `tx_inc()`는 `insert_tx` 안에서 단 한 번 호출된다 (`txpool.rs:2166`). pending / basefee / queued / blob **어디에 있든 전부 합산**되며, 서브풀별 분리 카운트가 아니다.

**② 하드캡이 아니다 — 실제로 17개까지 공존 가능.** 조건 3 때문에 온체인 nonce와 같은 tx는 슬롯이 꽉 차도 들어간다. reth 자체 테스트 `reject_spammer`가 이를 명시적으로 검증한다 (`txpool.rs:3275-3299`):

```rust
        let mut tx = MockTransaction::eip1559();
        let unblocked_tx = tx.clone();                    // nonce == 0 == on_chain_nonce
        for _ in 0..pool.max_account_slots {
            tx = tx.next();                               // nonce 1..16 삽입
            pool.insert_tx(f.validated(tx.clone()), on_chain_balance, on_chain_nonce).unwrap();
        }
        // 17번째(nonce 17) → 거부
        let err = pool.insert_tx(f.validated(tx.next()), ...).unwrap_err();
        assert!(matches!(err, InsertErr::ExceededSenderTransactionsCapacity { .. }));
        // 하지만 nonce == on_chain_nonce 인 tx 는 통과
        assert!(pool.insert_tx(f.validated(unblocked_tx), ...).is_ok());
```

따라서 정확한 표현은 **"한 계정이 앞질러 쌓아둘 수 있는 *미래 nonce* tx가 최대 16개"** 다.

**③ 처리량 제한이 아니라 in-flight 깊이 제한.** 삽입 시점의 *거부*이지 기존 tx 축출이 아니며, 앞 nonce가 채굴되면 카운터가 줄어 자리가 다시 생긴다 (`tx_decr`, `txpool.rs:1758·1773·1817`). "이 계정은 총 16개만 보낼 수 있다"가 아니라 **"아직 채굴 안 된 tx를 동시에 16개까지만 대기시킬 수 있다"** 이다.

### local 면제와의 상호작용 (주의: 비대칭적이다)

`--txpool.locals`로 등록한 발신자는 위 spam 체크를 통째로 건너뛴다 (`allow_local_spamming` 테스트, `txpool.rs:3301` 이하). 하지만 **축출(eviction) 보호는 서브풀마다 다르다**:

| 서브풀 | truncate 시 local 보호 | 근거 |
|--------|------------------------|------|
| pending | **있음** — non-local을 먼저 자르고, 그래도 한도를 못 맞추면 local도 자름 | `pool/pending.rs:375-500` (`remove_locals` 플래그) |
| basefee / queued (`ParkedPool`) | **없음** — `is_local` 참조가 전혀 없고 sender 제출 순서로만 축출 | `pool/parked.rs` `truncate_pool` |

`pending.rs`의 doc comment:

> "If the `remove_locals` flag is unset, transactions will be removed per-sender until a local transaction is the highest nonce transaction for that sender. If all senders have a local highest-nonce transaction, the pool will not be truncated further."

`--txpool.nolocals`를 켜면 이 면제가 전부 사라진다. 자세한 내용은 [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth-txpool-nolocals.md).

### ⚠️ RPC로 들어온 tx는 local이 아니다

reth v2.3.0에서 `eth_sendRawTransaction`은 **`TransactionOrigin::External`**을 쓴다 (`crates/rpc/rpc-eth-api/src/helpers/transaction.rs:79-87`):

```rust
    fn send_raw_transaction(&self, tx: Bytes) -> ... {
        async move {
            let recovered = recover_raw_transaction::<PoolPooledTx<Self::Pool>>(&tx)?;
            self.send_transaction(TransactionOrigin::External, WithEncoded::new(tx, recovered))
                .await
        }
    }
```

`TransactionOrigin::Local`은 노드가 직접 서명하는 `eth_sendTransaction` 경로에만 쓰인다(같은 파일 502행). 즉 **"내 노드 RPC로 직접 넣었으니 local 특혜를 받겠지"는 성립하지 않으며**, origin 기반 면제를 받으려면 `--txpool.locals <address>`로 주소를 명시해야 한다. geth와 다른 지점이라 오해하기 쉽다.

## 주요 인터페이스/필드

### 관련 CLI 플래그 (`crates/node/core/src/args/txpool.rs`)

| 플래그 | 기본값 | 의미 |
|--------|--------|------|
| `--txpool.pending-max-count` | 10,000 | pending 서브풀 최대 tx 수 |
| `--txpool.pending-max-size` | 20 (MB) | pending 서브풀 최대 크기 |
| `--txpool.basefee-max-count` / `-max-size` | 10,000 / 20MB | basefee 서브풀 |
| `--txpool.queued-max-count` / `-max-size` | 10,000 / 20MB | queued 서브풀 |
| `--txpool.blobpool-max-count` / `-max-size` | 10,000 / 20MB | blob 서브풀 |
| `--txpool.max-account-slots` | 16 | 계정당 미래 nonce tx 슬롯 |
| `--txpool.locals` | `[]` | 지정 주소를 local로 취급 (slot 체크 우회) |
| `--txpool.nolocals` | false | local 면제 전체 무효화 |
| `--txpool.minimum-priority-fee` | 없음 | 풀 수용 최소 priority fee |
| `--txpool.pricebump` | 10 (%) | 교체 tx 가격 인상 요구율 |

### 용어 함정 — "guaranteed"는 geth 유산

reth의 CLI 도움말과 필드 주석은 `Max number of executable transaction slots **guaranteed** per account`인데, 실제 코드는 보장치가 아니라 **거부 임계값**으로 쓴다. 이 문구는 geth에서 왔고 geth에서는 진짜 보장치다:

```go
// go-ethereum core/txpool/legacypool/legacypool.go:152-171
	AccountSlots uint64 // Number of executable transaction slots guaranteed per account
	GlobalSlots  uint64 // Maximum number of executable transaction slots for all accounts
	AccountQueue uint64 // Maximum number of non-executable transaction slots permitted per account
	GlobalQueue  uint64 // Maximum number of non-executable transaction slots for all accounts
...
	AccountSlots: 16,
	GlobalSlots:  4096 + 1024,
	AccountQueue: 64,
	GlobalQueue:  1024,
```

geth는 계정별 상한이 **queue 64개**(`AccountQueue`)로 따로 있고 `AccountSlots: 16`은 글로벌 한도 초과 시 잘라내며 지키는 하한이다. reth는 그 64에 해당하는 개념 없이 **16을 그대로 상한으로** 쓴다. **같은 이름·같은 기본값인데 동작이 반대에 가깝다.**

> 문서/주석 ↔ 코드 불일치이며, 코드를 정본으로 삼았다. geth 쪽은 config 필드 주석·기본값만 확인했고 `truncatePending` 실제 집행 로직까지 추적하지는 않았다.

### 클라이언트 지문 — -32003 vs -32000

| 클라이언트 | 메시지 | JSON-RPC 코드 |
|---|---|---|
| reth 계열 (op-reth, op-rbuilder) | `txpool is full` | **-32003** (`EthRpcErrorCode::TransactionRejected`) |
| go-ethereum / op-geth | `txpool is full` | **-32000** (`rpc/errors.go:61` `errcodeDefault`) |

go-ethereum의 `ErrTxPoolOverflow`(`core/txpool/legacypool/legacypool.go:62`)는 `ErrorCode()`를 구현하지 않으므로 기본 -32000이 붙는다. geth에서 -32003은 `errcodeResponseTooLarge`로 **전혀 다른 의미**다. 따라서 `-32003` + `txpool is full` 조합은 **거절한 쪽이 reth 계열임을 특정**한다.

## 관련 페이지

- [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth-txpool-nolocals.md) — 이 페이지의 slot 체크 우회·eviction 보호를 **끄는** 플래그. 두 페이지는 같은 `LocalTransactionConfig`를 반대 방향에서 본다.
- [op-reth "HTTP request to sequencer failed ... -32003: txpool is full" 진단](../runbooks/op-reth-sequencer-forward-txpool-full.md) — 이 메커니즘이 replica의 forwarding 실패 로그로 관측될 때의 진단 절차.
- [OP Stack 트랜잭션 수수료 & EIP-1559 (maxFeePerGas / maxPriorityFeePerGas)](op-stack-eip1559-fees.md) — 원인 A(`DiscardedOnInsert`)는 사실상 underpriced 판정이므로, 축출을 피하려면 이 페이지의 priority fee 모델을 이해해야 한다.

## 출처

**코드 정본 — reth v2.3.0 (op-reth가 pin한 버전, `resource/optimism/rust/Cargo.toml:411`):**
- [`crates/transaction-pool/src/pool/txpool.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/pool/txpool.rs) — `ensure_valid` slot 체크(1864-1881), `tx_counter`/`tx_inc`(1406·1460·2166), `AllTransactions` doc(1386-1406), `reject_spammer`/`allow_local_spamming` 테스트(3275-3325)
- [`crates/transaction-pool/src/pool/mod.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/pool/mod.rs) — `DiscardedOnInsert` 생성(697-728)
- [`crates/transaction-pool/src/pool/pending.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/pool/pending.rs) — local 보호 truncate(375-500)
- [`crates/transaction-pool/src/pool/parked.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/pool/parked.rs) — `truncate_pool` (local 보호 없음)
- [`crates/transaction-pool/src/error.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/error.rs) — `PoolErrorKind`, `InvalidPoolTransactionError`
- [`crates/transaction-pool/src/config.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/transaction-pool/src/config.rs) — 기본 한도 상수, `SubPoolLimit`, `PoolConfig::is_exceeded`
- [`crates/rpc/rpc-eth-types/src/error/mod.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/rpc/rpc-eth-types/src/error/mod.rs) — `RpcPoolError::TxPoolOverflow` → -32003, `From<PoolError>` 매핑
- [`crates/rpc/rpc-eth-api/src/helpers/transaction.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/rpc/rpc-eth-api/src/helpers/transaction.rs) — `send_raw_transaction` → `TransactionOrigin::External`(79-87), `eth_sendTransaction` → `Local`(502)
- [`crates/node/core/src/args/txpool.rs`](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/node/core/src/args/txpool.rs) — CLI 플래그·기본값

**대조 — go-ethereum (master):**
- [`core/txpool/legacypool/legacypool.go`](https://github.com/ethereum/go-ethereum/blob/master/core/txpool/legacypool/legacypool.go) — `ErrTxPoolOverflow`(62), `AccountSlots`/`AccountQueue` 정의·기본값(152-171)
- [`rpc/errors.go`](https://github.com/ethereum/go-ethereum/blob/master/rpc/errors.go) — `errcodeDefault = -32000`(61)

**로컬 소스 (`resource/optimism` @ `aaeb6c0154`):**
- `rust/Cargo.toml:411` — reth v2.3.0 pin
