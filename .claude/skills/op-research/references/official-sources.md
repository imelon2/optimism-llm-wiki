# Optimism / OP Stack official sources

> The `op-research` skill orchestrator and the research agents it spawns — `oh-my-claudecode:explore` (code + wiki/KB) and `oh-my-claudecode:document-specialist` (docs) — read this **before** any code/docs exploration. The orchestrator passes the path to this file in every research-agent prompt.

## Source table

| Type | Location | Purpose |
|---|---|---|
| Official docs (LLM index) | https://docs.optimism.io/llms.txt | Primary entry point for concepts/architecture/operation guides (the LLM agent fetches this first) |
| OP Stack core (local) | `./optimism/` | The actual implementation. Cite source paths as `optimism/<module>/<file>.go:LINE` |
| OP Stack core (remote) | https://github.com/ethereum-optimism/optimism | For branches / PRs / issues not present locally (supplementary) |
| Operations & infra components | https://github.com/ethereum-optimism/infra | Node operation, monitoring, infra tooling. Local `./infra/`, cite as `infra/<path>:LINE` |
| OP Stack contracts (local) | `./optimism/packages/contracts-bedrock` directory | The actual OP Stack contracts implementation. Cite as `optimism/packages/contracts-bedrock/<path>:LINE` |

## Exploration rules

- The local `./optimism/` directory is a clone of the GitHub repo above. Always use **local first** for code exploration; reference the remote only as a fallback.
- If the local clone does not yet exist, check the remote (GitHub) via WebFetch / `gh`, but mark the result as **"remote-based (local not cloned)"**. (The version pin is uncertain, so it must be re-verified at ingest time.)
- Major modules inside `./optimism/` (`op-node`, `op-batcher`, `op-proposer`, `op-challenger`, `op-supervisor`, `op-deployer`, `packages/`, `cannon/`, etc.) are each an independent research topic. Narrowing scope to a single module makes deep analysis easier.
- Tools in the `infra` repo (monitoring, deployment scripts, k8s manifests, etc.) are the subject of node-operation / infra research. Cite code as `infra/<path>:LINE`.

## Analysis docs rules

1. Fetch `https://docs.optimism.io/llms.txt` → identify topic-relevant docs from the index.
2. Fetch the identified doc URLs → expand the search to adjacent docs as needed.
3. If a spec ↔ local-code-implementation mismatch (spec drift) appears, flag it in the report.

## Citation format summary

| Target | Format |
|---|---|
| Local code | `optimism/<module>/<file>.go:LINE` |
| Local contracts | `optimism/packages/contracts-bedrock/<path>:LINE` |
| Local infra | `infra/<path>:LINE` |
| Official docs | URL |
| Remote code | URL (+ commit SHA or PR/issue #number) |
| Existing KB page | `[[page-slug]]` |

