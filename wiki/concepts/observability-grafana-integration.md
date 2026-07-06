---
type: Concept
title: OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황
description: OP Stack Go 노드의 관측성 4축(메트릭·로그·프로파일·트레이스)이 Grafana 스택(Prometheus/Loki/Pyroscope/Tempo)과 각각 어디까지 네이티브로 연동되는지와, 프로파일링의 SRE 활용 가치. 트레이스는 Go 노드·op-geth 미지원이나 op-reth는 --tracing-otlp/--logs-otlp로 OTLP 네이티브 export하는 예외
resource: resource/optimism/op-service/oppprof/service.go
tags: [op-stack, observability, monitoring, sre]
timestamp: 2026-07-06T00:00:00Z
version: bedrock
source_commit: aaeb6c0154
---

# OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황

## 개요

OP Stack Go 서비스(op-node·op-batcher·op-proposer·op-challenger·op-geth 등)를 Grafana LGTM 스택(Loki·Grafana·Tempo·Mimir/Prometheus + Pyroscope)으로 관측할 때, **축마다 지원 수준이 다르다.** 메트릭·로그·프로파일 3축은 노드가 네이티브로 데이터를 노출하므로 스크레이프/수집만 붙이면 되지만, **트레이스(Tempo)만은 Go 노드·op-geth가 데이터를 생산하지 않아 커스텀 계측이 필요하다.** (단, 실행 클라이언트로 **op-reth**를 쓰면 트레이스·로그를 CLI 플래그로 OTLP 네이티브 export하는 예외다 — 아래 §1-a.)

비유: 메트릭·알람이 "엔진 과열 경고등"이라면, 프로파일은 "3번 실린더가 원인"이라고 짚어주는 진단기이고, 트레이스는 "택배 하나가 창고→트럭→집까지 거친 전 구간 경로"다. OP Stack 노드는 경고등과 진단기 데이터는 이미 뿜어내지만, 택배 송장(trace/span)은 찍지 않는다.

### 관측성 4축 요약

| 축 | Grafana 백엔드 | OP Stack 지원 | 연동 방식 |
|---|---|---|---|
| 메트릭 | Prometheus / Mimir | ✅ 네이티브 | `/metrics` 스크레이프 |
| 로그 | Loki | ✅ 구조화 로그 | stdout/파일 수집 |
| **프로파일** | **Pyroscope** | **✅ 네이티브** | `/debug/pprof/*` 스크레이프 (코드 수정 불필요) |
| 트레이스 | Tempo | ⚠️ Go 노드·op-geth 미지원 / **op-reth 네이티브** | Go: OTel Collector 등 커스텀 계측 / op-reth: `--tracing-otlp` 플래그 (§1-a) |

## 핵심 동작/책임

### 1. 트레이스(Tempo): 기본 미지원

Grafana Tempo는 OTLP/Jaeger/Zipkin span을 ingest하는 트레이싱 백엔드이므로, **누군가 span을 생산해 보내주어야** 동작한다. OP Stack **Go** 프로덕션 노드와 **op-geth**에는 그 생산자가 없다(EL을 op-reth로 쓰면 예외 — §1-a).

- **OpenTelemetry는 존재하나 위치가 테스트/데브스택뿐이다.** `go.opentelemetry.io/otel/trace` 임포트는 `op-devstack/devtest/*`, `op-up/main.go`, `op-e2e/`에만 있고 테스트 스코프마다 span을 만든다 (`resource/optimism/op-devstack/devtest/testing.go:292`, `common.go:8`). 게다가 레포에 OTLP exporter(`otlptrace`/`SetTracerProvider`) 구성 코드가 없어, 데브스택조차 기본값으로는 span이 no-op로 버려진다.
- **프로덕션 노드의 "Tracer"는 이름만 Tracer일 뿐 span이 아니다.** op-node의 `Tracer`는 P2P/체인 이벤트 훅 인터페이스(`OnNewL1Head`/`OnUnsafeL2Payload`/`OnPublishL2Payload`)로, 내부적으로 로그·메트릭을 호출할 뿐 OTLP를 내보내지 않는다 (`resource/optimism/op-node/node/tracer/comms.go`). derivation 이벤트 훅(`op-service/event/tracer.go`)도 동일하게 span이 아니다.
- **op-geth의 "tracing"은 EVM 실행 트레이싱(`debug_traceTransaction`)**이지 분산 트레이싱이 아니다.
- **Tempo 연동 경로**: (a) OTel Collector를 노드 외부에 두고 JSON-RPC 계층을 프록시로 감싸 요청 단위 span 생성 → OTLP 전송(노드 무수정, 단 노드 내부 파이프라인은 못 봄), 또는 (b) 노드를 fork해 위 훅 지점에 실제 OTel span 계측 추가(정밀하나 유지보수 부담). 두 경우 모두 커스텀 작업이다.

### 1-a. 예외 — op-reth(러스트 EL)는 OTLP 트레이스/로그를 네이티브 제공

위 "미지원"은 **OP Stack Go 서비스와 op-geth 기준**이다. 실행 클라이언트를 op-geth 대신 **op-reth**(reth 기반, 러스트)로 쓰면, op-reth는 **CLI 플래그만으로 자기 내부 span·로그를 OTLP로 직접 export**한다 — 별도 계측/프록시 불필요. reth 상속 기능이다.

**두 개의 독립 파이프라인**이며, **컴파일 feature 게이팅이 다르다**(가장 큰 운영 함정):

| 파이프라인 | 플래그 | Cargo feature | op-reth 기본 빌드 |
|---|---|---|---|
| **트레이스** | `--tracing-otlp*` | `otlp` | ✅ 포함 (바로 작동) |
| **로그** | `--logs-otlp*` | `otlp-logs` | ❌ 미포함 |

→ `--logs-otlp`를 기본 바이너리에 그냥 주면 **무효**이고 `WARN ... compile with the otlp-logs feature` 경고만 뜬다. 로그 OTLP는 `otlp-logs` feature로 재빌드해야 한다. 트레이스(`--tracing-otlp`)는 기본 빌드에서 바로 된다 (`resource/optimism/rust/op-reth/bin/Cargo.toml:33`, `crates/cli/src/app.rs:143-159`).

플래그별(정본: upstream reth **v2.3.0** `crates/node/core/src/args/trace.rs`):

| 플래그 | 기본값 | 하는 일 |
|---|---|---|
| `--tracing-otlp <URL>` | 없음(비활성) | 트레이스 export 켜기+엔드포인트. HTTP=`:4318/v1/traces`, gRPC=`:4317` |
| `--tracing-otlp-protocol <http\|grpc>` | `http` | 전송 프로토콜(트레이스·로그 공통). gRPC는 tokio 런타임 필요 |
| `--tracing-otlp.filter <directive>` | `debug` | **어떤 span**을 보낼지(`RUST_LOG` 문법). stdout과 분리 가능 |
| `--tracing-otlp.sample-ratio <0.0~1.0>` | 없음 | 샘플링 비율. `None`/`1.0`=전부, `0.0`=없음, `0.1`=10%(TraceIdRatioBased) |
| `--logs-otlp <URL>` | 없음 | 로그 export 켜기+엔드포인트(경로 `/v1/logs`). **`otlp-logs` feature 필요** |
| `--logs-otlp.filter <directive>` | `info` | **어떤 로그**를 보낼지 |

- **기동 확인**: 성공 시 `INFO ... Started OTLP <protocol> tracing export to <endpoint>` 로그가 뜬다 (`app.rs:143-145`).
- **엔드포인트 정규화**: HTTP면 경로 없을 때 `/v1/traces`(또는 `/v1/logs`)를 자동 append, gRPC면 그 경로가 없어야 한다 (`reth-tracing-otlp/src/lib.rs`).
- **활용**: op-reth를 EL로 쓰면 Go 스택에 없던 **트레이스 축**(블록 실행·페이로드 빌드 지연을 요청/블록 단위로 분해)을 옵션 하나로 얻고, `sample-ratio`·`filter`로 볼륨·비용을 조절한다.

### 2. 프로파일(Pyroscope): 네이티브 연동

모든 OP Stack Go 바이너리가 공유하는 `op-service/oppprof` 패키지가 표준 Go pprof HTTP 서버를 이미 노출한다. Grafana Pyroscope(연속 프로파일링 백엔드)가 이를 Prometheus처럼 pull 모드로 스크레이프하면 **노드 코드 수정 없이** 연속 프로파일링이 붙는다.

- `op-service/oppprof/service.go:99`가 `/debug/pprof/`(Index → allocs/heap/goroutine/block/mutex 등), `/debug/pprof/profile`(CPU), `/symbol`, `/trace`를 서빙한다.
- `--pprof.enabled`로 켜며 기본 바인딩은 `0.0.0.0:6060`, 지원 타입은 `cpu, heap, goroutine, threadcreate, block, mutex, allocs` (`resource/optimism/op-service/oppprof/cli.go:16-27,111-119`).
- op-geth도 go-ethereum의 `--pprof --pprof.addr --pprof.port`(기본 6060)로 동일한 `/debug/pprof/*`를 노출한다.
- Grafana Alloy의 `pyroscope.scrape` 컴포넌트가 대상의 `/debug/pprof/{allocs,block,goroutine,mutex}`와 `/debug/pprof/profile?seconds=N`(CPU)를 주기적으로 긁어 Pyroscope로 전송한다 ([Grafana Pyroscope Go pull mode](https://grafana.com/docs/pyroscope/latest/configure-client/grafana-alloy/go_pull/)).

### 3. 메트릭·로그

- **메트릭**: 노드가 Prometheus 포맷으로 `/metrics`를 노출한다(`op-node/metrics/metrics.go`의 `StartServer`, `op-service/metrics/server.go`). Prometheus/Mimir가 스크레이프한다 ([Optimism Node Metrics 문서](https://docs.optimism.io/builders/node-operators/management/metrics)).
- **로그**: 구조화 로그를 stdout/파일로 남기며 Loki(Promtail/Alloy)로 수집한다.

## 주요 인터페이스/필드

### Alloy `pyroscope.scrape` 예시 (pull 모드)

```alloy
pyroscope.scrape "op_stack" {
  targets = [
    { "__address__" = "op-node:6060",    "service_name" = "op-node" },
    { "__address__" = "op-geth:6060",    "service_name" = "op-geth" },
    { "__address__" = "op-batcher:6060", "service_name" = "op-batcher" },
  ]
  forward_to = [pyroscope.write.default.receiver]
}
```

### 프로파일 타입별로 얻는 정보

프로파일의 핵심은 **콜스택(call stack) 단위**로 "자원을 어느 함수/라인이 쓰는지"를 짚어준다는 점이다. 메트릭이 "무엇이 얼마나 나빠졌나"라면 프로파일은 "그 원인이 코드 어디인가"다.

| 프로파일 | 답하는 질문 | 대표 증상 |
|---|---|---|
| `cpu` | CPU 시간을 어느 함수가 태우나 | 노드 CPU 100%, 블록 처리 지연 |
| `heap` | 지금 살아있는 메모리를 누가 붙잡나 | 메모리 지속 증가(누수), OOM |
| `allocs` | 할당을 누가 많이 일으키나(GC 압박) | GC 빈발로 지연 지터(jitter) |
| `goroutine` | 고루틴이 몇 개고 어디서 멈춰 있나 | 고루틴 누수, 데드락, 응답 없음 |
| `block` | 채널/락 대기로 어디서 블로킹되나 | CPU는 낮은데 처리량 정체 |
| `mutex` | 어느 락에서 경합이 심한가 | 코어를 늘려도 성능 정체 |
| `threadcreate` | OS 스레드가 왜 계속 늘어나나 | 스레드 폭증 |

### SRE 활용 가치

특히 **연속 프로파일링**(상시 스크레이프)이 SRE에 유효하다.

1. **MTTR 단축 / 사후 분석**: 일반 pprof는 "지금" 떠야 잡히지만, Pyroscope로 상시 수집해두면 장애 발생 시각의 프로파일을 사후 조회할 수 있다 — 재현 어려운 간헐적 장애에 결정적.
2. **회귀 탐지**: op-node/op-geth 버전 업그레이드 전후 프로파일을 diff해, 새 릴리스가 특정 함수의 CPU/메모리를 늘렸는지 배포 전 포착.
3. **용량 산정·비용 최적화**: 자원 핫스팟을 근거로 인스턴스 스펙·노드 수를 결정하고 클라우드 비용을 줄인다.
4. **탐지→진단 연결**: 메트릭 알람(예: 힙 사용률 > 85%)에서 같은 Grafana의 해당 시점 heap 프로파일로 바로 드릴다운.

전형적 OP Stack 시나리오: 메모리 누수/OOM → `heap` 두 시점 diff로 계속 커지는 자료구조 특정; 처리 정체인데 CPU는 낮음 → `goroutine`+`block`/`mutex`로 락 경합·데드락 지점 확인; p99 지터 → `allocs`로 핫 패스의 불필요 할당 제거.

### 한계 / 주의

- **인과 분석 한계**: 프로파일은 "어디서" 자원을 쓰는지는 잘 보이나 "어떤 요청 때문인지"(요청 단위 인과)는 약하다 — 그건 트레이스(Tempo)의 영역이라 상호 보완적이다. EL로 op-reth를 쓰면 이 요청 단위 인과를 `--tracing-otlp` 네이티브 트레이스로 보완할 수 있다(§1-a).
- **표본 기반**: sampling이라 아주 짧고 드문 이벤트는 놓칠 수 있다.
- **오버헤드**: CPU 프로파일 스크레이프는 수집 구간 동안 런타임 부하가 있다. 스크레이프 주기를 보수적으로.
- **보안**: pprof 기본 바인딩이 `0.0.0.0`이다(코드에도 `TODO: Switch to 127.0.0.1` 주석). `/debug/pprof`는 힙·고루틴 내부를 노출하므로 **공개망에 열지 말고** 내부망/방화벽/Alloy 사이드카로만 접근시킨다 (`resource/optimism/op-service/oppprof/cli.go:80`).
- **최적화(선택)**: Pyroscope 권장 delta 프로파일용 `godeltaprof` 엔드포인트는 노드 코드 변경이 필요하다. 없어도 표준 `/debug/pprof/*` 스크레이프로 동작하므로 필수는 아니다.

> 근거: 로컬 `resource/optimism` 클론(`source_commit: aaeb6c0154`) 코드 기준. Grafana 측 수집 방식은 공식 문서로 교차 검증했다. op-reth OTLP 플래그(§1-a)의 정본은 upstream reth **v2.3.0**(`crates/node/core/src/args/trace.rs`)이며, op-reth 배선·feature 기본값은 로컬 `resource/optimism/rust/op-reth`로 확인했다.

## 관련 페이지

- [op-node l1.rpckind & L1 Receipts Fetching 최적화](op-node-l1-rpckind-receipts.md) — op-node 운영 튜닝의 다른 축(L1 RPC 비용 최적화). 본 페이지는 그 op-node를 **관측·프로파일링하는 관점**을 다룬다.
- [op-node P2P Peering & Chain Isolation](op-node-p2p-peering.md) — op-node P2P 운영. 관측성 축에서 P2P 관련 메트릭(`opp2p_*`)·프로파일로 피어링 이상을 진단할 수 있다.
- [op-reth "Changeset cache MISS" 로그 진단](../runbooks/op-reth-changeset-cache-miss.md) — 로그 축(Loki) 진단 사례. op-reth WARN 로그를 op-node Engine API 블록 빌드와 상관분석한다.
- [op-reth --txpool.nolocals & Local Transaction Exemption](op-reth-txpool-nolocals.md) — 동일 op-reth 클라이언트의 다른 CLI 플래그 계열(txpool 정책). 관측성 축과 별개로 mempool 우대 정책을 제어한다.
- 외부: [Grafana Pyroscope — Go pull mode](https://grafana.com/docs/pyroscope/latest/configure-client/grafana-alloy/go_pull/), [Alloy `pyroscope.scrape`](https://grafana.com/docs/alloy/latest/reference/components/pyroscope/pyroscope.scrape/), [Optimism Node Metrics](https://docs.optimism.io/builders/node-operators/management/metrics), [reth v2.3.0 `args/trace.rs`(OTLP 플래그 정본)](https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/node/core/src/args/trace.rs), [OpenTelemetry Sampling](https://opentelemetry.io/docs/concepts/sampling/)
