---
type: Runbook
title: op-node "failed to fetch receipts ... for L1 sysCfg update" 진단 (RPC 타임아웃 / 연결 리셋)
description: op-node가 L1 origin 전진 시 다음 L1 블록 receipts를 조회해 SystemConfig를 갱신하다 L1 RPC 실패(context deadline exceeded 타임아웃, connection reset by peer 연결 끊김 등)로 시퀀서가 "Engine failed temporarily, backing off sequencer"로 백오프하는 로그의 인과 사슬·무해/자가복구 판정·단일 이벤트 루프 블로킹이 블록 생산을 멈추는 메커니즘·원인 후보·진단 절차
resource: resource/optimism/op-node/rollup/derive/l1_traversal.go
tags: [op-stack, l1, sequencer]
timestamp: 2026-07-06T00:00:00Z
chain: l1
version: bedrock
source_commit: aaeb6c0154
---

# op-node "failed to fetch receipts ... for L1 sysCfg update" 진단 (RPC 타임아웃 / 연결 리셋)

## 개요

**증상**: 리더 시퀀서의 op-node가 다음 ERROR를 남긴다.

```
# 변형 A — op-node 자체 타임아웃(응답이 느림)
ERROR Engine failed temporarily, backing off sequencer
  err="temp: failed to fetch receipts of L1 block 0x...:NNNN (parent: 0x...:NNNN-1)
       for L1 sysCfg update: querying block: context deadline exceeded"

# 변형 B — 상대 L1 서버가 연결을 끊음(서버가 조기 종료)
ERROR Engine failed temporarily, backing off sequencer
  err="temp: failed to fetch receipts of L1 block 0x...:NNNN (parent: 0x...:NNNN-1)
       for L1 sysCfg update: querying block: read tcp <local>-><remote>:443: read: connection reset by peer"
```

로그 끝 `querying block:` **뒤에 붙는 문자열이 실제 실패 사유**이고, 이 부분만 케이스마다 다르다(`context deadline exceeded`, `connection reset by peer`, `EOF`, `broken pipe` 등). 앞의 래핑 문구(`failed to fetch receipts ... for L1 sysCfg update`)는 동일하다.

**판정: 일시적(temporary) 에러·자가복구·합의/안전성 무관·데이터 손상 아님.** op-node가 L2 블록을 만들기 전에 L1 origin을 한 칸 전진시키면서, **그 L1 블록의 receipts(영수증)를 L1 RPC로 조회**하려다 L1 RPC 호출이 실패했다. 실패 사유는 두 부류다 — op-node가 응답을 기다리다 **자체 타임아웃**(`context deadline exceeded`)이 나거나, 상대 L1 서버가 **연결을 끊어**(`connection reset by peer`) 조기 실패한다. 어느 쪽이든 `TemporaryError`로 감싸져 **자동 재시도**되고(재시도 간격은 지수 백오프 — 아래 "영향" 참조), origin은 전진하지 않고 그대로 멈춰 다음 스텝에 다시 시도할 뿐 잘못된 데이터가 반영되지 않는다.

**왜 굳이 receipts를 가져오나 (한 줄 요약)**: L2를 L1 시스템 설정과 동기화하기 위해서다. op-node는 L1 origin을 전진시킬 때마다 그 L1 블록에 **SystemConfig 컨트랙트의 `ConfigUpdate` 이벤트**(배처 주소·gas 설정·gas limit·EIP-1559 파라미터 변경 등)가 있는지 receipts를 스캔해 L2 시스템 설정을 갱신한다. 비유하면 "새 L2 블록을 짓기 전에 L1 관청에 새 공지가 붙었는지 확인하러 가는데, 창구(L1 RPC)가 느려 정해진 시간 안에 답을 못 받고 '다음에 다시 오자'며 돌아온" 상황이다.

> **범위**: 본 페이지는 **단발성 또는 간헐적** 타임아웃(L1 RPC 지연·순간 부하)을 다룬다. `context deadline exceeded`가 **지속 반복**되어 unsafe 블록 생산이 멈추는 상황은 L1 엔드포인트 자체를 교체·증설해야 하는 별개 인시던트로, 아래 "원인 후보"·"진단 절차"로 원인을 좁힌다.

## 핵심 동작/책임

### 인과 사슬 (코드 정본)

```
Sequencer 블록 생성 루프
  └─ DerivationPipeline.Step()                       pipeline.go:216
       └─ L1Traversal.AdvanceL1Block(ctx)            l1_traversal.go:60
            ├─ L1BlockRefByNumber(origin+1)          ← 다음 L1 블록 헤더 (여기는 통과)
            ├─ (parent 해시 불일치면 ResetError = L1 reorg)   l1_traversal.go:69-71
            └─ FetchReceipts(nextL1Origin.Hash)      l1_traversal.go:74  ← 여기서 RPC 실패
                 └─ L1 EthClient → CachingReceiptsProvider → RPCReceiptsFetcher
                      RPC 실패 (callTimeout 초과=timeout, 또는 서버가 연결 끊음=connection reset)
       ↑ NewTemporaryError("failed to fetch receipts of L1 block %s ... for L1 sysCfg update: %w")
                                                      l1_traversal.go:76
  ↑ (파이프라인 → 엔진) EngineTemporaryErrorEvent
Sequencer.onEngineTemporaryError                     sequencer.go:425
  └─ log.Error("Engine failed temporarily, backing off sequencer")   sequencer.go:429
       nextAction = now + 1s   (재시도; syncing이면 +30s)              sequencer.go:430-434
```

로그의 `L1 block ...:11199451 (parent: ...:11199450)`에서 **11199451이 `nextL1Origin`**(현재 origin 다음 L1 블록)이고, 이 블록의 receipts 조회에서 실패했다. 즉 origin이 11199450 → 11199451로 넘어가려다 막힌 것이다.

### receipts를 조회·적용하는 지점

```go
// resource/optimism/op-node/rollup/derive/l1_traversal.go:73-82
// Parse L1 receipts of the given block and update the L1 system configuration
_, receipts, err := l1t.l1Blocks.FetchReceipts(ctx, nextL1Origin.Hash)
if err != nil {
    return NewTemporaryError(fmt.Errorf("failed to fetch receipts of L1 block %s (parent: %s) for L1 sysCfg update: %w", nextL1Origin, origin, err))
}
if err := UpdateSystemConfigWithL1Receipts(&l1t.sysCfg, receipts, l1t.cfg, nextL1Origin.Time); err != nil {
    // 영수증이 malformed/invalid일 때만. 적용 실패는 정보성 로그로 처리하고 계속 진행.
    l1t.log.Warn("failed to fully update L1 sysCfg with receipts from block", "block", nextL1Origin, "error", err)
}
```

주목: `FetchReceipts` **조회 실패**는 TemporaryError(재시도)지만, receipts를 받아온 뒤 `UpdateSystemConfigWithL1Receipts` **적용 실패**는 WARN 로그 후 계속 진행이다 — 본 증상은 전자(조회 타임아웃)에 해당한다.

### `context deadline exceeded`의 정체 — RPC 호출 타임아웃

이 데드라인은 파생 파이프라인의 스텝별 타임아웃이 아니라 **L1 RPC 클라이언트 자체의 호출 타임아웃**이다. 파생 deriver는 장기 컨텍스트(`d.ctx`)로 `pipeline.Step`을 호출하므로(`deriver.go:128`), 실질 데드라인은 RPC 클라이언트 기본값에서 온다:

```go
// resource/optimism/op-service/client/rpc.go:147-152
if cfg.callTimeout == 0 {
    cfg.callTimeout = 10 * time.Second       // 단건 호출(eth_getBlockReceipts 등)
}
if cfg.batchCallTimeout == 0 {
    cfg.batchCallTimeout = 20 * time.Second  // tx별 배치(eth_getTransactionReceipt batch)
}
```

즉 L1 EL RPC가 이 창(10s/20s) 안에 receipts를 못 돌려주면 컨텍스트가 취소되고 위 에러가 난다. 어느 타임아웃이 걸리는지는 그 순간 선택된 receipts 조회 메서드에 달렸다(→ 원인 후보 2).

### 실패 모드: 타임아웃 vs 연결 리셋

`FetchReceipts`가 실패하는 이유는 크게 두 부류이며, 로그 꼬리로 구분된다:

| | 타임아웃 (`context deadline exceeded`) | 연결 리셋 (`connection reset by peer`) |
|---|---|---|
| 누가 실패시켰나 | **op-node 자신** — 자체 타임아웃이 먼저 울림 | **상대 L1 서버/네트워크** — 연결을 강제 종료(TCP RST) |
| 상황 | 서버가 **느려서** 응답이 안 옴 | 연결은 됐는데 서버가 **중간에 끊음** |
| op-node가 매달린 시간 | 타임아웃 창을 **꽉 채움**(≈10초 단건 / 20초 배치) | 끊긴 **즉시** 실패(수백 ms~수 초) |
| 블록 생산 영향 | **큼** (아래 "영향" 참조) | **작음** (프리징이 짧음) |

`connection reset by peer` 외에 `EOF`·`broken pipe`도 같은 "서버/네트워크가 연결을 끊음" 계열이다.

## 영향: 블록 생산에 미치는 효과 (단일 이벤트 루프)

이 에러의 실질 영향은 **"L1 RPC 하나가 느리면(혹은 끊기면) op-node 전체가 잠시 멈춘다"** 는 것이다. op-node가 파생·시퀀싱·L1 추적을 **단일 이벤트 루프(고루틴 1개)** 에서 한 번에 하나씩 동기로 처리하기 때문이다.

### 왜 요청 하나가 노드 전체를 멈추나

- op-node는 이벤트 executor로 `event.NewGlobalSynchronous`를 쓴다(`resource/optimism/op-node/node/node.go:312`). 이 executor의 `Drain()`은 **한 루프가 이벤트를 하나 꺼내 그 처리가 끝나야 다음 걸 꺼낸다**(`resource/optimism/op-service/event/executor_global.go:190-204`). 워커 풀·병렬 분기가 없다.
- 그 루프가 곧 드라이버의 `eventLoop` **하나**다(`resource/optimism/op-node/rollup/driver/driver.go:224`). 블록 생성 타이머(`sequencerCh`)도, 파생 스텝(`NextStep`)도 같은 `select` 한 곳에서 받는다(`driver.go:324-349`).
- receipts 조회는 이 루프 안에서 도는 파생 스텝의 **동기 블로킹 RPC**다(`l1_traversal.go:74`). 이 호출이 반환돼야 `Drain`이 다음 이벤트로 넘어가므로, 응답을 기다리는 동안 **큐에 쌓인 "블록 만들어" 신호를 못 꺼내** 블록 생산이 멈춘다.
- 이 단일 루프 설계는 **의도적**이다 — 엔진 forkchoice·헤드 등 민감한 상태를 경합(race) 없이 **결정론적**으로 처리하려는 것이고, 그 대가로 "느린 요청 하나가 전체를 막는" 특성을 감수한다.

정상적으로 L1 RPC가 빠르고 receipts가 캐시(`CachingReceiptsProvider`)에 있으면 스텝은 수 ms에 끝나 루프가 빠르게 회전한다 — 이 프리징은 **RPC가 느리거나 끊기는 병리적 케이스에서만** 발생한다.

### 연속 실패 시 타임라인 (지수 백오프 + 회복 창)

재시도 간격은 **고정이 아니라 지수 백오프**다. temp 에러마다 파생 스텝이 백오프 없이 재요청되고(`resource/optimism/op-node/rollup/driver/sync_deriver.go:73-77`), 재시도 지연은 `retry.Exponential()` = `min(2^n × 1s, 10s) + jitter(≤250ms)`로 늘어난다(`step_scheduling_deriver.go:60,100`, `resource/optimism/op-service/retry/strategies.go:49-54`). 결정적으로 **이 백오프 대기 동안에는 루프가 풀려 있어**(`step_scheduling_deriver.go:98` 주석 *"without blocking other events"*) 그 틈에 시퀀서가 밀린 블록을 만든다.

타임아웃이 3연속 발생한 예(회당 10초 가정):

```
[freeze 10s] → 백오프 2s(루프 자유) → [freeze 10s] → 백오프 4s(루프 자유) → [freeze 10s] → 백오프 8s ...
   블록 X        블록 생성 가능           블록 X        블록 생성 가능           블록 X
```

- **실제 멈춘 시간(하드 프리징) 합계 ≈ 30초** (10초 × 3, 연속이 아니라 토막).
- **전체 벽시계 ≈ 36초** (프리징 + 사이 회복 창).
- 백오프 구간(2s·4s)은 "멈춤"이 아니라 **회복 창**이다 — 그동안 블록이 생성된다. 따라서 "3번 실패 = 33초 연속 정지"는 부정확하고, **약 30초가 토막으로 정지**하며 사이에 짧게 회복하는 형태다.
- 별도로 시퀀서 자신의 `nextAction +1s` 백오프(`sequencer.go:433`)가 겹치지만 10초 프리징에 묻힌다.
- **연결 리셋 계열**은 프리징이 짧으므로 위 "30초 정지"의 대부분이 사라진다 — 같은 3연속이라도 훨씬 덜 아프다.

## 주요 인터페이스/필드

### 원인 후보 (확률순)

1. **L1 RPC 엔드포인트 지연/과부하/레이트리밋/네트워크 지터 (가장 흔함).** 공급자 순간 부하나 네트워크 문제로 응답이 10~20초를 넘김. 로그가 **단발성**이면 대부분 이 케이스이고 자동 재시도로 자가복구된다.
2. **`--l1.rpckind` 미스매치로 느린 조회 경로.** kind가 실제 공급자와 안 맞으면 블록 단위 저렴한 메서드(`eth_getBlockReceipts`) 대신 tx별 `eth_getTransactionReceipt` **배치**로 강등되어, tx가 많은 L1 블록에서 조회가 무거워지고 타임아웃 위험이 커진다. **같은 시간대에 `"resetting back RPC preferences, please review RPC provider kind setting"` 경고가 함께 보이면 이 원인이 유력하다.** (→ [op-node l1.rpckind & L1 Receipts Fetching 최적화](../concepts/op-node-l1-rpckind-receipts.md))
3. **해당 L1 블록이 tx가 많은 "무거운 블록"** 이라 receipts 페이로드가 커서 조회가 느림. 특정 블록에서만 재현되면 의심.
4. **L1 노드 자체 문제** — 자체 운영 L1이 syncing 중이거나 디스크 I/O 지연·GC 스톨. (`errors.Is(err, ErrEngineSyncing)`이면 백오프가 30초로 늘어난다: `sequencer.go:430-431`)
5. **연결 리셋(`connection reset by peer`) 특유 원인** — 조회가 느린 게 아니라 상대가 연결을 끊는 경우다. ① L1 서버/앞단 프로세스 **재시작·크래시**, ② 레이트리밋을 429 대신 **RST로 처리**하는 공급자, ③ 앞단 **프록시/로드밸런서**의 idle·과부하 커넥션 정리(HTTPS 443 앞의 TLS 종단 프록시 등), ④ op-node가 재사용하려던 **keep-alive 커넥션을 서버가 이미 닫음**(재시도 시 새 연결로 대개 성공), ⑤ 무거운 조회가 **서버 자체 시간제한**을 넘겨 서버가 끊음.

### 진단 절차

1. **에러 꼬리 읽기 + 빈도 확인**: `querying block:` 뒤 문자열이 `context deadline exceeded`면 **느림(timeout)**, `connection reset by peer`/`EOF`/`broken pipe`면 **끊김(reset)**이다 — 이후 조치가 갈린다. 단발인지, 특정 L1 블록·시간대에 반복되는지도 확인 — 단발이면 정상 자가복구로 종결.
2. **동반 로그 확인**: 같은 시간대에
   - `"resetting back RPC preferences, please review RPC provider kind setting"` → 원인 후보 2 (`l1.rpckind` 교정).
   - `"failed to use selected RPC method for receipt fetching, temporarily falling back to alternatives"` → 메서드 강등 발생 중.
   - L1 RPC 관련 다른 timeout/5xx → 원인 후보 1/4.
3. **L1 RPC 상태 점검**: L1 엔드포인트의 응답 지연·에러율·레이트리밋 확인. 공용 RPC라면 전용/더 빠른 엔드포인트로 교체 검토.
4. **`--l1.rpckind` 정합성 점검**: 실제 L1 공급자에 맞게 설정(Alchemy→`alchemy`, QuickNode→`quicknode`, 자체 Geth→`debug_geth` 등). 기본값 `standard`는 `eth_getBlockReceipts`를 쓰므로 대부분 안전하나, 공급자를 알면 명시가 낫다.
5. **완화(증상)**: 순수 지연이라면 L1 RPC 호출 타임아웃을 늘려 완화할 수 있으나 근본 해결은 아니다. 우선순위는 L1 RPC 성능/안정성 개선.

### 판정 요약

| 관측 | 판정 |
|------|------|
| 단발 1~2건, 다음 스텝에 진행 | 무해. L1 RPC 순간 지연. 종결. |
| 간헐적, `resetting back RPC preferences` 동반 | `--l1.rpckind` 미스매치. 설정 교정. |
| `context deadline exceeded` 지속 반복, unsafe 헤드 정체 | L1 엔드포인트 **느림/과부하**. 회당 10~20초 프리징. 엔드포인트 교체·증설. |
| `connection reset by peer`/`EOF` 반복 | L1 서버 **재시작·레이트리밋(RST)·프록시 정리**. 서버/프록시 로그·요청 rate 확인. 프리징은 짧음. |
| `parent` 해시 불일치로 `ResetError` 동반 | 별개 이슈(L1 reorg). 본 페이지 범위 밖. |

> 근거: 로컬 `resource/optimism` 클론(`source_commit: aaeb6c0154`) 코드로 인과 사슬·타임아웃 기본값 확인. 실제 배포 노드가 RPC 타임아웃을 커스텀 오버라이드했는지는 노드 실행 플래그로 별도 확인 필요.

### 불확실성 / 검증 한계

- **실 데드라인 값**: 위 10s/20s는 RPC 클라이언트 **기본값**이다. 배포 환경에서 옵션으로 오버라이드했다면 실제 창은 다르다.
- **원인 확정**: 후보 1~4 중 어느 것인지는 **단독 로그로는 확정 불가**하다. 같은 시간대의 `resetting back RPC preferences` 경고 유무, L1 RPC 에러율/지연, 해당 L1 블록의 tx 수를 함께 봐야 좁혀진다.

## 관련 페이지

- [op-node l1.rpckind & L1 Receipts Fetching 최적화](../concepts/op-node-l1-rpckind-receipts.md) — 본 타임아웃의 원인 후보 2(느린 조회 경로)의 배경. receipts 조회 메서드 선택·강등·복구 메커니즘과 `--l1.rpckind` kind별 권장.
- [op-reth "Changeset cache MISS" 로그 진단 및 op-stack 유발 경로](op-reth-changeset-cache-miss.md) — 시퀀서 블록 빌드 사이클의 EL 측 로그 진단. 본 페이지(L1 origin 전진의 CL 측)와 **시퀀서 로그 진단 런북 계열**을 공유한다.
- [OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황](../concepts/observability-grafana-integration.md) — 이 ERROR는 관측성 4축 중 **로그 축(Loki)**으로 수집·상관분석하는 대상이다.
