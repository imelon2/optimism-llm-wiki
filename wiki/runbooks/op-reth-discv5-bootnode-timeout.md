---
type: Runbook
title: op-reth discv5 Bootnode Timeout 진단
description: op-reth 기동 시 --bootnodes의 enode가 "net::discv5: failed adding boot node ... err=Timeout"으로 실패하는 원인(enode→ENR 라이브 요청)과 해결(ENR 사용, 포트·UDP 점검)
resource: https://reth.rs/docs/src/reth_discv5/lib.rs.html
tags: [op-stack, p2p, reth, l2]
timestamp: 2026-06-29T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# op-reth discv5 Bootnode Timeout 진단

## 개요

**증상**: op-reth(reth) 노드 기동 시 `--bootnodes`에 등록한 enode가 다음 로그로 실패한다.

```
net::discv5: failed adding boot node ... err=Timeout
```

**한 줄 결론**: 이것은 버그가 아니다. **enode 형식으로 부트노드를 넣었기 때문에** reth가 그 노드에 "정보(ENR) 좀 줘"라고 직접 discv5 요청을 보냈는데 **응답이 안 와서(Timeout)** 그 부트노드를 건너뛴 것이다. 비유하면 *전화를 걸었는데 상대가 안 받은 것*이다.

부트스트랩은 best-effort라 한두 개 실패는 노드 기동을 막지 않지만, **등록한 부트노드가 전부 실패하면 피어를 못 찾는다.** 가장 확실한 해결은 **enode 대신 ENR을 등록**하는 것이다.

## 핵심 동작/책임

### enode와 ENR은 처리 경로가 다르다

reth는 `--bootnodes` 항목을 두 가지로 나눠 처리한다 (reth `reth_discv5/lib.rs` `bootstrap`, L542-577).

| 형식 | 생긴 모양 | reth 처리 | 네트워크 |
|------|-----------|-----------|----------|
| **ENR**(Ethereum Node Record, 서명된 노드 기록) | `enr:-IS4QH...` | `discv5.add_enr(node)` — 기록 안에 모든 정보가 있어 바로 라우팅 테이블에 삽입 | 없음 ✅ |
| **enode**(discv4/RLPx 식별자, IP·포트만) | `enode://<pubkey>@<ip>:<port>` | `discv5.request_enr(enode).await` — 정보가 부족해 그 주소로 **실시간 요청**을 보내 ENR을 받아와야 함 | **있음** 📞 |

enode URL에는 서명된 ENR이 없으므로 reth는 enode의 `ip:UDP포트`로 live discv5 요청을 보낸다. 응답이 제한 시간 내 안 오면 `err=Timeout`이 나고 그 부트노드는 `continue`로 건너뛴다. 실패 로그(현재 reth는 `debug!` 레벨):

```rust
// reth_discv5/lib.rs  bootstrap (L542-577)
BootNode::Enr(node)     => { discv5.add_enr(node) }              // 네트워크 없음
BootNode::Enode(enode)  => { discv5.request_enr(enode.to_string()).await } // 실패 시 ↓
// debug!(target: "net::discv5", ?enode, %err, "failed adding boot node");
```

> 교차검증: 로컬 kona(Rust OP CL 노드)도 동일 패턴이다 — `BootNode::Enode(enode) => disc.request_enr(enode).await`, 실패 시 `continue` (`resource/optimism/rust/kona/crates/node/disc/src/driver.rs:111-134`). 즉 enode→ENR 라이브 요청은 reth·kona 공통 동작이다.

### Timeout의 의미

`request_enr` Timeout = **상대 IP:UDP포트로 보낸 discv5 패킷에 유효한 응답이 없었다.** ENR 경로면 네트워크 왕복이 없어 이 에러 자체가 발생하지 않는다.

## 주요 인터페이스/필드

### 원인별 진단·해결 (흔한 순서)

| # | 원인 | 진단 | 해결 |
|---|------|------|------|
| 1 | **UDP 차단** (가장 흔함) | discv5는 전부 UDP. 방화벽/보안그룹이 TCP만 열고 UDP를 막으면 무조건 Timeout | 해당 IP:UDP포트로 UDP inbound/outbound 모두 허용 |
| 2 | **포트 불일치** | `enode://...@ip:30303`의 포트는 보통 TCP. discv5 요청은 **UDP 포트**로 감. 상대 discv5 UDP 포트가 다르면 빈 곳에 요청 | enode 끝에 `?discport=<UDP포트>` 명시 |
| 3 | **EL/CL 부트노드 혼동** | 로그 타깃 `net::discv5`는 **reth(EL)**. 여기에 op-node(CL) 부트노드를 넣으면 EL discv5 요청에 응답하지 않음 | 다른 op-reth/op-geth(EL) 노드의 식별자를 등록 |
| 4 | **discv4 enode를 discv5에 등록** | enode는 본래 discv4 식별자. 상대가 discv5를 안 켰거나 discv4만 말하면 응답 없음 | 상대 노드가 discv5 가동 중인지 확인 |
| 5 | **도달 불가 / stale** | IP가 옛날 값, 노드 다운, NAT 뒤 | 최신 enode/ENR 확보, 노드 가동 확인 |

### 권장 조치 (쉬운 것부터)

1. **enode 대신 ENR(`enr:...`) 등록** — ENR 경로는 `add_enr`라 네트워크 왕복이 없어 Timeout이 원천 차단된다. OP Stack 공식 부트노드는 ENR로 배포된다. **가장 확실한 해결책.**
2. enode를 꼭 써야 하면 **`?discport=`로 상대 discv5 UDP 포트를 정확히 명시**하고, 그 노드가 discv5를 켰는지 확인.
3. **EL용 부트노드**인지 확인 (`net::discv5`는 reth=EL, op-node CL 부트노드와 혼동 금지).
4. **UDP 연결성 검증** — 방화벽/보안그룹에서 해당 IP:UDP포트 개방 확인.
5. **로그 확대** — `RUST_LOG=net::discv5=trace`로 어느 enode가 어느 단계에서 Timeout인지 특정.

### 참고 / 불확실

- 로그 레벨: 확인한 현재 reth 소스에서는 `debug!`다. 과거 버전은 `warn!`였을 수 있으나 동작·원인은 동일하다.
- `request_enr`의 정확한 Timeout 값·에러 enum은 하위 `discv5`(sigp/discv5) 크레이트에 정의된다.
- reth EL discv5 기본 UDP 포트는 `DEFAULT_DISCOVERY_V5_PORT = 9200` (reth `reth_discv5/config.rs`). 단 위 진단의 포트 문제는 *상대 부트노드*의 포트이지 로컬 기본값과는 별개다.
- 부트노드가 전부 잘못되면 reth가 별도 치명 에러 없이 피어를 못 찾고 스톨할 수 있다 (reth #12309).

## 관련 페이지

- [op-node P2P Peering & Chain Isolation](../concepts/op-node-p2p-peering.md) — op-node(CL) 측 discv5 discovery·ENR `opstack` chainID 필터. 본 Runbook은 그 EL(reth) 대응으로, **discv5/enode/ENR 개념을 공유**한다.

## 출처

- reth `reth_discv5/lib.rs` (`bootstrap`, `request_enr`, "failed adding boot node"): https://reth.rs/docs/src/reth_discv5/lib.rs.html
- reth `reth_discv5/config.rs` (BootNode::Enr vs Enode, `DEFAULT_DISCOVERY_V5_PORT`): https://reth.rs/docs/src/reth_discv5/config.rs.html
- 로컬 교차검증: `resource/optimism/rust/kona/crates/node/disc/src/driver.rs:111-134` (`bootstrap_peers`)
- paradigmxyz/reth #12309 (잘못된 enode가 피어 탐색을 막음): https://github.com/paradigmxyz/reth/issues/12309
- Optimism Docs — op-node discv5/ENR 부트노드 설정: https://docs.optimism.io/operators/node-operators/configuration/consensus-config
