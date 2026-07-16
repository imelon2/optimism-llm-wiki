---
type: Concept
title: op-node P2P Peering & Chain Isolation
description: op-node가 discv5 discovery·ENR opstack chainID 필터·체인별 gossip 토픽·피어 게이팅으로 Optimism 노드만 격리하는 메커니즘과 inbound 연결을 하드 제한하는 방법
resource: resource/optimism/op-node/p2p
tags: [op-stack, p2p, l2]
timestamp: 2026-06-29T00:00:00Z
chain: l2
version: bedrock
source_commit: aaeb6c0154
---

# op-node P2P Peering & Chain Isolation

## 개요

op-node의 P2P 네트워크에는 Prysm/Lighthouse 등 L1 컨센서스 노드가 연결을 시도하는 현상이 관찰된다. "Optimism 노드만 연결되도록" 제한할 수 있는지에 대한 메커니즘과 운영 옵션을 정리한다.

핵심 결론은 다음과 같다.

1. **op-node가 능동적으로(outbound) dial하는 대상은 이미 Optimism 노드뿐이다.** discv5로 발견한 노드 중 ENR에 `opstack` 키 + 자기 체인의 L2 chainID가 일치하는 노드만 dial한다 (`resource/optimism/op-node/p2p/discovery.go:215-252`).
2. **L1 노드의 inbound "연결 시도"는 네트워크 레벨에서 완전히 차단할 수 없다.** op-node의 discv5(UDP)는 L1 컨센서스 클라이언트와 동일한 와이어 프로토콜을 쓰기 때문에, 그들의 DHT 탐색이 우리 엔드포인트를 발견하고 probe/dial한다 — 공개 포트의 자연스러운 노이즈다 (`resource/optimism/op-node/p2p/discovery.go:108`).
3. **그 시도는 실제 피어링으로 이어지지 않아 무해하다.** chainID 불일치 + gossip 토픽 불일치 + 피어 스코어링/밴으로 거부·정리된다.
4. **하드 제한이 필요하면** 방화벽(P2P 포트 inbound 제한)을 축으로 `--p2p.no-discovery` + `--p2p.static`을 병행한다. op-node 설정만으로 "chainID 다른 inbound를 connected 전에 거부"하는 것은 불가능하다 — 게이터가 chainID를 모르기 때문이다.

## 핵심 동작/책임

### 왜 L1 노드가 연결을 시도하는가

op-node의 노드 발견(discovery)은 **discv5**이며, 이는 geth/L1 컨센서스 레이어(Prysm, Lighthouse, Teku)가 쓰는 것과 **동일한 discv5 프로토콜**이다. `discover.ListenV5(conn, localNode, cfg)`로 표준 go-ethereum discv5 UDP 서비스를 띄운다 (`resource/optimism/op-node/p2p/discovery.go:108`). discv5는 글로벌 DHT 위 랜덤 워크로 노드를 찾고, 전송 레이어 자체는 "이 노드가 어느 체인용인가"를 dial 전에 구분하지 않는다. 따라서 inbound 연결 시도 자체는 설정으로 막는 대상이 아니라 공개 P2P 포트의 정상 노이즈다.

### Optimism 전용 격리 장치 (3중)

op-node는 외부 노드와 실제로 피어링하기 전에 세 단계에서 체인을 격리한다.

1. **ENR `opstack` 키 + chainID 필터 (outbound dial 격리).** op-node는 자기 ENR에 `OpStackENRData{ chainID, version }`를 심고 (`resource/optimism/op-node/p2p/discovery.go:80-84`), `FilterEnodes()`로 발견 노드 중 `opstack` 엔트리가 없거나 chainID/version이 다르면 무시한다 (`resource/optimism/op-node/p2p/discovery.go:215-236`). 필터 통과 노드만 peerstore에 넣고 dial 후보로 삼는다 (`:247-252`). → Prysm/Lighthouse는 `opstack` 엔트리가 없어 **outbound 대상에서 원천 제외**된다.
2. **체인별 gossip 토픽 (메시징 격리).** 블록 전파 토픽 이름에 L2 chainID가 박혀 있다 — `/optimism/<L2ChainID>/{0,1,2,3}/blocks` (V1~V4) (`resource/optimism/op-node/p2p/gossip.go:81-94`). msg-id도 chainID를 포함해 유일하다 (`:144`). 다른 체인/네트워크 노드는 이 토픽을 구독하지 않아 메시지 교환이 성립하지 않는다.
3. **libp2p 보안 협상 + 피어 스코어링/밴 (inbound 정리).** inbound TCP도 Noise 핸드셰이크(`--p2p.security=noise`)와 op-node 전용 프로토콜 협상을 통과해야 한다. 밴이 기본 ON이다 — `--p2p.ban.peers` 기본 `true`, threshold 기본 `-100`, duration 기본 `1h` (`resource/optimism/op-node/flags/p2p_flags.go:115-139`, `resource/optimism/op-node/p2p/config.go:64-65,172-176`). 연결 게이터 `BlockingConnectionGater`(libp2p `conngater` 기반)가 peerID/IP/subnet denylist를 host에 주입한다 (`resource/optimism/op-node/p2p/gating/blocking.go`, `host.go:195-227`). → 토픽도 안 맞고 유효 트래픽도 못 내는 L1 노드는 점수가 떨어져 정리·밴된다.

### inbound 연결은 chainID로 게이팅되지 않는다

`opp2p_peers`의 connected는 TCP + Noise + muxer 핸드셰이크까지 끝난 피어를 뜻하며, op-node는 **chainID/opstack이 다른 노드의 inbound 연결을 거부할 네이티브 수단이 없다.**

- op-node와 L1 CL은 동일한 libp2p 스택(Noise + yamux/mplex)을 공유하므로 connected(TCP+Noise+muxer) 협상은 성공한다 (`resource/optimism/op-node/p2p/host.go:217-248`). 체인 구분은 그 위 계층(gossipsub 토픽, req-resp 프로토콜 `/opstack/req/payload_by_number/<chainID>/0` — `resource/optimism/op-node/p2p/sync.go:79`)에서만 일어난다.
- 게이팅 지점 `InterceptAccept`/`InterceptSecured`는 **peerID와 multiaddr(IP)만** 받고 chainID/opstack ENR을 전달받지 못한다 (`resource/optimism/op-node/p2p/gating/scoring.go:56`, `gating/expiry.go:138-161`). InterceptSecured 시점은 identify(AgentVersion 교환) 이전이라 user-agent(`"optimism"`)로도 거를 수 없다.
- discovery 필터 `FilterEnodes`는 **outbound dial 대상 선정에만** 적용되고 inbound에는 관여하지 않는다. op-node가 host에 다는 게이터는 `AddBanExpiry` + `AddMetering`뿐이며 `AddScoring`(점수 기반 inbound 거부)은 메인 경로에 wire되지 않는다 (`resource/optimism/op-node/p2p/host.go:200-201`). 밴은 명시적으로 `BlockPeer`/`BlockAddr`로 올린 peerID/IP만 거부한다.
- chainID(OPStackID)는 peerstore metadata·RPC 조회·req-resp 프로토콜 ID에만 쓰이고 inbound 게이팅에는 쓰이지 않는다. connected 후 "op 프로토콜 미지원이면 끊기" 같은 자동 disconnect도 없다 (`resource/optimism/op-node/p2p/notifications.go`는 메트릭·로깅용).

## 주요 인터페이스/필드

### "Optimism 노드만" 하드 제한 방법

| 방법 | 설정 | 효과 / 한계 |
|------|------|------------|
| **A. 정적 신뢰 피어 (가장 강력)** | `--p2p.no-discovery=true` + `--p2p.static=<multiaddr,...>` | discv5를 꺼 DHT 노출·무작위 발견 제거. static 피어는 `"static"` 태그로 `Protect()`되어 프루닝 제외 (`resource/optimism/op-node/p2p/host.go:96-100,243-244`). 피어 자동 확장이 안 되므로 통제된 토폴로지(sequencer↔replica, 사내 클러스터)에 적합 |
| **B. IP 대역(CIDR) 제한** | `--p2p.netrestrict=<CIDR,...>` | "P2P will only try to connect on these networks". 단 `NetRestrict`는 **discv5 discovery 설정에만** 연결되고 (`resource/optimism/op-node/p2p/discovery.go:102`, `cli/load_config.go:207-212`, `config.go:103`) libp2p host의 ConnectionGater에는 자동 적용되지 않는다 → inbound TCP 화이트리스트로는 불완전 |
| **C. 방화벽 (가장 확실한 inbound 차단)** | OS/클라우드 방화벽으로 P2P 포트(기본 **TCP/UDP 9222**) inbound를 신뢰 대역만 허용 | TCP 수립 전에 차단 — chainID 부재로 게이터가 못 막는 inbound를 막는 유일하게 확실한 방법. 외부 OP 피어 발견도 막히므로 방법 A와 병행(폐쇄망) |
| **D. RPC 사후 차단** | `opp2p_blockPeer` / `blockAddr` / `blockSubnet` | 런타임에 특정 피어·IP·서브넷 차단. 사후·수작업이며 활성 연결은 자동 종료되지 않고 다음부터 차단 (`resource/optimism/op-node/p2p/gating/blocking.go:17-32`) |

### "connected 차단" 가능 여부

| 방법 | chainID 다른 inbound를 connected 전에 막나? |
|------|---|
| 방화벽(필수) | ✅ TCP 수립 전 차단 — 유일하게 확실 |
| `--p2p.no-discovery` + `--p2p.static` | △ 노출/신규 발견은 줄지만 이미 알려진 ENR로의 inbound는 못 막음 → 방화벽 병행 |
| RPC `opp2p_block*` | △ 사후·수작업. 차단 후 `InterceptAccept/Secured`에서 거부 |
| 코드 fork | ✅ identify 완료 후 AgentVersion≠optimism 또는 op 토픽/프로토콜 미지원 피어를 `ClosePeer`(NotifyBundle Connected 콜백 활용). 단 connected가 잠깐 생긴 뒤 끊는 방식이며 upstream에 없음 |

### 권장 사항

- **일반 메인넷/퍼블릭 운영**: 별도 설정 불필요. L1 노드의 inbound 시도는 chainID·토픽·스코어링으로 이미 걸러지는 정상 노이즈다. 로그가 거슬리면 해당 P2P 로거 레벨만 낮춘다.
- **폐쇄망/통제된 토폴로지**: 방법 A(`--p2p.no-discovery` + `--p2p.static`) + 방법 C(방화벽) 조합이 정석.
- `--p2p.netrestrict`(방법 B)는 discovery 단계 IP 제한 보조로만 쓰고, inbound 하드 차단은 방화벽에 맡긴다.

> 근거: 로컬 `resource/optimism` 클론(`source_commit: aaeb6c0154`) 코드 기준. 플래그 명칭·기본값은 코드로 확인했으며, 공식 문서 `https://docs.optimism.io`의 P2P 운영 가이드와 교차 검증을 권장한다.

## 관련 페이지

- [op-reth discv5 Bootnode Timeout 진단](../runbooks/op-reth-discv5-bootnode-timeout.md) — EL(reth) 측 discv5 부트노드 운영 이슈. 본 페이지의 op-node(CL) discovery와 **discv5/enode/ENR 개념을 공유**하며, enode 부트노드의 `request_enr` Timeout 진단을 다룬다.
- [OP Stack 노드 ↔ Grafana 관측성(LGTM) 연동 현황](observability-grafana-integration.md) — 본 페이지의 P2P 피어링 이상은 op-node 메트릭(`opp2p_*`)·프로파일로 진단할 수 있으며, 관측성 4축 지원 현황을 다룬다.
- [op-node 동기화 모드(CLSync/ELSync) & ReqResp P2P Sync Deprecation](op-node-syncmode-reqresp-deprecation.md) — 본 페이지에서 언급한 req-resp 프로토콜(`/opstack/req/payload_by_number/<chainID>/0`)의 **클라이언트가 제거**되어 gap 복구가 op-reth EL snap sync로 넘어간 변화와 `--syncmode` 차이를 다룬다.
- (아직 없음) 향후 `op-node` Component 페이지, gossip/derivation 관련 Concept 페이지가 생기면 교차링크한다.
