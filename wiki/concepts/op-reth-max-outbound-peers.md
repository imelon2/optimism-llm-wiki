---
type: Concept
title: op-reth --max-outbound-peers & devp2p 피어 슬롯 제어
description: op-reth(EL)의 outbound 피어 상한(기본 100)이 inbound(기본 30)와 별도 카운터로 관리되고, 실제 다이얼은 max_concurrent_outbound_dials(기본 30, CLI 없음)와의 AND 조건으로 게이트되며, --max-peers는 2:1(inbound:outbound) 분배로 배타 적용되고, 상한 도달 시 평균 5분 주기 피어 로테이션이 UselessPeer 절단을 유발하는 메커니즘
resource: https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/node/core/src/args/network.rs
source_commit: aaeb6c0154
tags: [op-stack, p2p, reth, l2]
timestamp: 2026-08-03T00:00:00Z
chain: l2
version: bedrock
---

# op-reth --max-outbound-peers & devp2p 피어 슬롯 제어

## 개요

`--max-outbound-peers`는 op-reth가 devp2p(RLPx) 네트워크에서 **자기가 먼저 걸어나가는(outbound) 연결의 최대 개수**다. 기본값 100이며, **받는(inbound) 연결(기본 30)과는 완전히 별도의 카운터**다.

비유하자면 전화 회선이다. op-reth에는 **거는 회선 100개**와 **받는 회선 30개**가 따로 있고, 이 플래그는 앞쪽만 조절한다. 회선이 남으면 5초마다 후보 목록에서 가장 좋은 상대에게 전화를 걸고, 다 차면 더 걸지 않는다.

핵심 결론은 다음과 같다.

1. **op-reth 고유 옵션이 아니다.** op-reth는 upstream `paradigmxyz/reth`의 `reth-node-core`를 git tag로 pin해 쓰며(로컬 스냅샷 기준 `tag = "v2.3.0"` — `resource/optimism/rust/Cargo.toml:345-349`), `NetworkArgs`를 그대로 상속한다. OP 전용 오버라이드는 없다.
2. **값을 올려도 즉시 그만큼 늘지 않는다.** 동시 진행 다이얼은 `max_concurrent_outbound_dials`(기본 30)로 별도 제한되고, 이 값은 **CLI 플래그가 없어 `reth.toml`로만** 조정 가능하다.
3. **trusted 피어도 outbound 상한을 우회하지 못한다.** 우선순위만 받는다 — inbound에는 상한 예외 경로가 있지만 outbound에는 없다.
4. **상한에 도달하면 피어 로테이션이 돈다.** 평균 5분(3~7분 지터) 주기로, 10분 이상 붙어 있던 비-trusted/static 피어 하나를 `UselessPeer`로 끊어 새 피어 자리를 만든다(geth peer dropper 모방). 주기적 `UselessPeer` disconnect 로그는 정상 동작이다.
5. **CL(op-node)의 P2P와 다른 네트워크다.** 이 상한은 EL devp2p 피어에만 적용되며, op-node의 libp2p 피어링과는 무관하다.

## 핵심 동작/책임

### 플래그 정의 (코드 정본)

`crates/node/core/src/args/network.rs:303-322` (v2.3.0 / upstream main 동일):

```rust
/// Maximum number of outbound peers. default: 100
#[arg(long)]
pub max_outbound_peers: Option<usize>,

/// Maximum number of inbound peers. default: 30
#[arg(long)]
pub max_inbound_peers: Option<usize>,

/// Maximum number of total peers (inbound + outbound).
///
/// Splits peers using approximately 2:1 inbound:outbound ratio. Cannot be used together with
/// `--max-outbound-peers` or `--max-inbound-peers`.
#[arg(long, value_name = "COUNT",
      conflicts_with = "max_outbound_peers",
      conflicts_with = "max_inbound_peers")]
pub max_peers: Option<usize>,
```

주의할 점은 **`default_value_t`가 없다**는 것이다. 타입이 `Option<usize>`이고 `None`이면 `reth.toml`의 값을 그대로 둔다 (`crates/net/network-types/src/peers/config.rs:250-255`):

```rust
pub const fn with_max_outbound_opt(mut self, max_outbound: Option<usize>) -> Self {
    if let Some(max_outbound) = max_outbound {
        self.connection_info.max_outbound = max_outbound;
    }
    self
}
```

즉 **"기본 100"은 CLI의 기본값이 아니라 `ConnectionsConfig::default()`의 값**이다(`config.rs:11-19, 108-110`). 우선순위는 `CLI > reth.toml [peers.connection_info] > 코드 기본값`.

### 실제 게이트 — 두 조건의 AND

값은 `NetworkArgs::network_config()`(`network.rs:571-580`) → `PeersConfig.connection_info.max_outbound` → `PeersManager`의 `ConnectionInfo`로 전달된다. 강제 지점은 이 한 줄이다 (`crates/net/network/src/peers.rs:1333-1336`):

```rust
const fn has_out_capacity(&self) -> bool {
    self.num_pending_out < self.config.max_concurrent_outbound_dials &&
        self.num_outbound < self.config.max_outbound
}
```

이 **AND 조건**이 실무에서 가장 자주 오해되는 부분이다. `--max-outbound-peers 300`을 줘도 진행 중인 다이얼은 30개(`DEFAULT_MAX_COUNT_CONCURRENT_OUTBOUND_DIALS`)를 넘지 못하므로, 목표치까지 채워지는 **속도**는 여전히 제한된다.

슬롯 충전은 `fill_outbound_slots()`가 담당하고 `refill_slots_interval`(기본 5초) 주기로 호출된다 (`peers.rs:1153-1179`):

```rust
while self.connection_info.has_out_capacity() {
    let (peer_id, peer) = match self.best_unconnected() { Some(p) => p, _ => break };
    peer.state = PeerConnectionState::PendingOut;
    ...
}
```

### 누구에게 거는가 — `best_unconnected()` 우선순위

`peers.rs:1066-1099`. 밴/백오프 상태가 아닌 미연결 피어 중에서:

1. **trusted 또는 static이면 즉시 선택** (우선권만 있고 상한 면제는 아님)
2. 나머지는 **reputation 최고값**
3. reputation 동률이면 **`fork_id`가 알려진 피어 우선** (호환 포크라는 신호)

`--trusted-only`(`trusted_nodes_only`)를 켜면 trusted 피어만 후보가 된다.

후보 풀 자체는 discovery(discv4/discv5)와 `--bootnodes`, `--trusted-peers`, peers 파일이 채운다. 즉 **상한을 올려도 discovery가 찾아낸 후보 수가 실제 천장**이다 — 부트노드 설정 실패로 후보가 안 쌓이면 outbound는 올라가지 않는다 ([op-reth discv5 Bootnode Timeout 진단](../runbooks/op-reth-discv5-bootnode-timeout.md) 참고).

### inbound와의 비대칭

inbound는 꽉 찼을 때 trusted 피어를 위한 예외 경로가 있다 (`peers.rs:336-358`) — `max_inbound == 0`이어도 아직 연결되지 않은 trusted 피어가 있으면 pending 연결을 받아준다. **outbound에는 이런 예외가 없다.**

따라서 `--max-outbound-peers 0`을 주면 다이얼을 아예 하지 않는 **inbound-only 노드**가 된다(discovery로 발견해도 걸지 않음).

### 상한 도달 시 — 피어 로테이션

`try_rotate_peer()` (`peers.rs:1107-1146`)는 outbound 또는 inbound 풀이 capacity에 닿았을 때, **10분 이상**(`PEER_ROTATION_MIN_UPTIME`) 연결돼 있던 비-trusted·비-static 피어 중 하나를 무작위로 골라 `DisconnectReason::UselessPeer`로 끊는다. 주기는 평균 5분(`DEFAULT_PEER_ROTATION_INTERVAL`)에 지터를 준 3~7분 (`config.rs:118-122, 211`).

> **운영 함의**: `--max-outbound-peers`를 작게 잡으면 노드가 항상 capacity 상태가 되어 몇 분마다 피어가 교체된다. 로그의 주기적 `UselessPeer` disconnect는 장애가 아니라 설계된 동작이다. 끄려면 `reth.toml`의 `peer_rotation_interval`을 비활성화해야 한다(CLI 플래그 없음).

### `--max-peers`와의 관계 (배타적)

`--max-peers`는 `--max-outbound-peers` / `--max-inbound-peers`와 **동시 사용 불가**(clap `conflicts_with`). 분배 로직 (`network.rs:495-520`):

```rust
// outbound
Some((max_peers / 3).max(1))
// inbound
let outbound = (max_peers / 3).max(1);
Some(max_peers.saturating_sub(outbound))
```

| 입력 | outbound | inbound |
|------|----------|---------|
| `--max-peers 30` | 10 | 20 |
| `--max-peers 10` | 3 | 7 |
| `--max-peers 0` | 0 | 0 |

이 플래그는 **2025-12-12 커밋 `13416495` (PR #20139)에서 추가**됐다. 그 이전 reth를 pin한 op-reth 빌드에는 없으므로 `op-reth node --help | grep max-peers`로 확인 후 사용한다.

### OP Stack 맥락 — EL 피어가 무엇에 쓰이나

op-reth의 devp2p 피어는 op-node(CL)의 libp2p 피어와 **완전히 다른 네트워크**다. OP 체인에서 EL 피어의 실질적 용도는 세 가지다.

| 용도 | outbound 피어 수 민감도 |
|------|------|
| **ELSync / snap sync** (초기 동기화, gap 복구) | 매우 민감 — 피어가 적으면 헤더·바디·state 다운로드가 느려짐 |
| **트랜잭션 gossip** | 민감 — 단 `--rollup.disable-tx-pool-gossip`을 켠 노드에서는 무의미 |
| **블록 전파** | 상대적으로 덜 민감 — unsafe 블록의 정본 경로는 op-node(CL) gossip → Engine API |

따라서 replica/RPC 노드에서 리소스를 아끼려고 낮추는 것은 합리적이지만, **초기 동기화 중이거나 snap sync에 의존하는 노드에서는 낮춘 값이 그대로 병목**이 된다. gap 복구가 op-reth의 EL snap sync로 대체된 이후 이 의존성은 더 커졌다 ([op-node 동기화 모드 & ReqResp Deprecation](op-node-syncmode-reqresp-deprecation.md) 참고).

## 주요 인터페이스/필드

### 관련 CLI 플래그 (`crates/node/core/src/args/network.rs`)

| 플래그 | 기본값 | 의미 |
|--------|--------|------|
| `--max-outbound-peers <N>` | 100 | outbound 연결 상한 |
| `--max-inbound-peers <N>` | 30 | inbound 연결 상한 |
| `--max-peers <COUNT>` | (없음) | 총합 지정, 2:1(in:out) 분배. 위 두 플래그와 배타 |
| `--trusted-peers <enode/ENR,...>` | (없음) | 항상 우선 연결하는 피어 |
| `--trusted-only` | false | trusted 피어에게만 연결/수락 |
| `--peers-file <PATH>` | | 재기동 시 복원할 알려진 피어 목록 |
| `--bootnodes <enode/ENR,...>` | 체인 기본값 | discovery 부트스트랩 |

`max_concurrent_outbound_dials`에 대응하는 **CLI 플래그는 존재하지 않는다.**

### `reth.toml` 대응 설정

```toml
[peers.connection_info]
max_outbound = 100
max_inbound = 30
max_concurrent_outbound_dials = 30   # CLI 플래그 없음 — 여기서만 조정 가능
```

`[peers]` 섹션에는 `refill_slots_interval`(기본 5s), `peer_rotation_interval`(기본 5m), `ban_duration`(기본 12h), `trusted_nodes_only` 등이 함께 있다 (`crates/net/network-types/src/peers/config.rs:124-213`).

### 관측 — 설정이 실제로 먹었는지 확인

reth-network 메트릭(scope `network`, `crates/net/network/src/metrics.rs:16-41`):

| 메트릭 | 읽는 법 |
|--------|---------|
| `network_outgoing_connections` | 현재 활성 outbound. 설정한 상한에 붙어 있는지 확인 |
| `network_pending_outgoing_connections` | 진행 중 다이얼. **30에 붙어 있으면 `max_concurrent_outbound_dials`가 병목** |
| `network_incoming_connections` | 현재 활성 inbound |
| `network_connected_peers` / `network_tracked_peers` | 전체 연결 / 알고 있는 피어 수 |
| `network_outbound_*` (disconnect 카운터) | 특히 `too_many_peers`가 높으면 **상대 노드들이 꽉 차서** 내 다이얼을 거절하는 상황 — 내 설정을 올려도 해결되지 않는다 |

RPC로는 `admin_peers`, `net_peerCount`. 메트릭 수집 경로 전반은 [OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황](observability-grafana-integration.md) 참고.

### 튜닝 가이드

| 상황 | 권장 |
|------|------|
| 정상 운영 중인 replica/RPC | 기본값 유지. 리소스 압박이 있으면 `--max-peers`로 총합을 줄이는 편이 비율이 깨지지 않아 안전 |
| 초기 동기화 / snap sync 중 | 낮추지 않는다. 낮춰 둔 값이 있으면 sync 완료까지 기본값으로 복귀 |
| 폐쇄망 / 통제된 토폴로지 | `--trusted-peers` + `--trusted-only`. 단 trusted도 outbound 상한을 넘지 못하므로 상한 ≥ trusted 피어 수여야 한다 |
| outbound가 안 차오름 | 먼저 `network_tracked_peers`(후보 부족 = discovery 문제)와 `network_outbound_*` `too_many_peers`(상대가 꽉 참)를 구분한다 |

> **문서/코드 불일치 flag**: reth CLI help와 rustdoc은 `--max-outbound-peers`를 "default: 100"으로 적지만, clap 정의에는 `default_value_t`가 없다(`Option<usize>`). `reth.toml`에서 값을 바꿔 두면 CLI를 생략했을 때 100이 아니라 파일 값이 적용된다. 또한 `--max-peers`의 비율을 일부 생성 문서는 "1:2 ratio"로 표기하나, 코드상 outbound = `max_peers/3`이므로 **inbound:outbound = 2:1이 맞다**(동작 차이는 없고 표현만 혼용).

> 근거: upstream `paradigmxyz/reth` v2.3.0 및 main 대조 확인. op-reth 측은 로컬 `resource/optimism` 클론(`source_commit: aaeb6c0154`)의 `rust/Cargo.toml` pin(`tag = "v2.3.0"`)과 `Cargo.lock`(`reth-node-core 2.3.0`, `9384bc53`)으로 확인했으며, `rust/op-reth` 내에 `max_outbound_peers` 관련 오버라이드는 없다.

## 관련 페이지

- [op-node P2P Peering & Chain Isolation](op-node-p2p-peering.md) — CL(op-node) 측 libp2p 피어링·chainID 격리. 본 페이지의 EL(devp2p/RLPx) 피어 슬롯과 **완전히 다른 네트워크**이며, 두 레이어의 피어 수는 서로 독립적으로 관리된다.
- [op-reth discv5 Bootnode Timeout 진단](../runbooks/op-reth-discv5-bootnode-timeout.md) — 본 페이지의 outbound 슬롯을 채울 **후보 피어를 공급하는 discovery** 단계. 부트노드가 실패하면 상한을 올려도 outbound가 차오르지 않는다.
- [op-node 동기화 모드(CLSync/ELSync) & ReqResp P2P Sync Deprecation](op-node-syncmode-reqresp-deprecation.md) — gap 복구가 op-reth EL snap sync로 대체되면서 **EL 피어 수가 동기화 성능을 좌우**하게 된 배경.
- [트랜잭션 `√n` 브로드캐스트 규칙 (원본 전송 vs 해시 알림)](tx-propagation-sqrt-broadcast.md) — 본 페이지가 정하는 **피어 수가 그대로 `√n`의 입력값**이 된다. 피어를 늘리면 슬롯은 늘지만 트랜잭션 원본을 받는 피어의 **비율은 떨어져** 전파 지연 확률이 올라간다. 두 페이지는 같은 변수를 반대편에서 본다.
- [OP Stack 트랜잭션 전파 경로 (Ingress → 시퀀서)](op-stack-tx-ingress-propagation.md) — 본 페이지의 EL 피어 네트워크 위로 실제 트랜잭션이 흐르는 경로와 Ingress 아키텍처.
- [OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황](observability-grafana-integration.md) — 본 페이지의 `network_*` 메트릭을 수집·시각화하는 경로.

## 출처

- reth `crates/node/core/src/args/network.rs:303-322, 495-520, 571-580` (플래그 정의, `resolved_max_*`, `PeersConfig` 적용): https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/node/core/src/args/network.rs
- reth `crates/net/network-types/src/peers/config.rs:11-19, 108-122, 192-213, 236-311` (기본값 상수, `ConnectionsConfig`, `PeersConfig`, 로테이션 상수): https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/net/network-types/src/peers/config.rs
- reth `crates/net/network/src/peers.rs:336-358, 1066-1099, 1107-1179, 1309-1398` (inbound trusted 예외, `best_unconnected`, `try_rotate_peer`, `fill_outbound_slots`, `ConnectionInfo`): https://github.com/paradigmxyz/reth/blob/v2.3.0/crates/net/network/src/peers.rs
- reth `crates/net/network/src/metrics.rs:16-41, 475-492` (피어 게이지, outbound disconnect 카운터)
- reth 커밋 `13416495` "feat: add `--max-peers` CLI flag (#20139)", 2025-12-12
- reth CLI 레퍼런스 / `reth.toml` 설정: https://reth.rs/cli/reth/node/ , https://reth.rs/run/configuration/
- 로컬: `resource/optimism/rust/Cargo.toml:345-349`(reth pin `tag = "v2.3.0"`), `resource/optimism/rust/UPDATING-RETH.md`(pin 정책), `resource/optimism/rust/Cargo.lock`(`reth-node-core 2.3.0`)
- op-reth 크레이트 소유권 이관(`ethereum-optimism/optimism` `rust/op-reth`): https://github.com/ethereum-optimism/optimism/tree/develop/rust/op-reth
