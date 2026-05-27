# Schema

This document is the **single source of truth** for the wiki page authoring conventions. The type enum / type-specific fields / body rules / wikilink conventions / the 7 REVIEW types decision tree / language policy live *only in this document*. The op-wiki skill (`.claude/skills/op-wiki/SKILL.md`) does NOT duplicate the page conventions; it only cites by reference via `see references/schema.md §<heading>`. Copy-pasting the rules causes drift, so it is forbidden.

> This wiki is authored only through the op-wiki skill's ingest (reflect) procedure. Investigation/analysis is handled by the op-research skill (`./.olw/` reports), which does NOT author the wiki. This schema governs *only how a page must look*; the procedure for *when/how to reflect* is owned by op-wiki SKILL.md.

## File naming

- The filename is an **English kebab-case slug**. e.g., `optimism-portal-2.md`, `fault-dispute-game.md`, `eip-4844-blob-da.md`.
- Location: `wiki/<type-folder>/<slug>.md`. The `overview` page is the exception — a single file at `wiki/overview.md` (see §Type catalog).
- No duplicate slugs — if a slug pointing to the same concept arises due to abbreviations/plurals/language differences, consolidate to the canonical name via op-wiki SKILL.md §merge procedure. If ambiguous, isolate to the `REVIEW: duplicate` queue.
- One page = one file. Never merge multiple type pages into a single file.

## Required frontmatter

Every page has a YAML frontmatter + markdown body structure.

| Field | Type | Notes |
|---|---|---|
| `type` | enum | One of the 8 in §Type catalog |
| `title` | string | Descriptive Korean; proper nouns in English (e.g., `"OptimismPortal2 컨트랙트"`) |
| `slug` | string | English kebab-case (recommended to match the filename) |
| `tags` | array | Empty array allowed |
| `related` | array | `"[[other-slug]]"` form wikilinks, empty array allowed |
| `sources` | array | URL or absolute local path; if empty, the `(insufficient data)` body marker is required |
| `created` | date | `YYYY-MM-DD` |
| `updated` | date | `YYYY-MM-DD` |
| `status` | enum | `stable \| wip \| needs-review \| deprecated` |

## Optional frontmatter (type-specific)

Each type *must* carry the following fields.

### `contract` type
- `contract-address-l1`: `"0x..."` (checksummed address)
- `contract-address-l2`: `"0x..."` or `null`
- `proxy`: `true | false`
- `implementation-version`: semver/tag such as `"v1.5.0"`
- `solidity-version`: such as `"0.8.25"`

### `component` type
- `language`: `go | rust | solidity | typescript`
- `repo-path`: e.g., `"optimism/op-node"`
- `binary`: e.g., `"op-node"`

### `troubleshooting` type
- `encountered`: `YYYY-MM-DD` (date the incident occurred; if unknown, the page authoring date)
- `environment`: free text (e.g., `"OP Mainnet, op-batcher v1.9.2, L1 mainnet"`). Include node version, network, L1 state, and related contract versions as far as possible.
- `severity`: `critical | high | medium | low`
- `status`: `open | resolved | recurring | mitigated`
- `error-signature`: the key single line of the error message or stack trace (acts as a search key; MUST appear verbatim somewhere in the body)
- `root-cause`: `[[wiki-slug]]` (another page pointing to the root cause) or accompanied by the `(insufficient data)` body marker
- `resolution`: a 1-line resolution summary (or `(not yet resolved)`)

## Body rules

- The first line must NOT be an H1 — the title already lives in frontmatter.
- **Every claim (factual statement)** must be backed by exactly one of the following three:
  (a) grounded in a page linked via `[[related-page]]` in the immediately preceding sentence or the same paragraph
  (b) an explicit citation from one of the items in the `sources:` array (URL fragment or line ref recommended)
  (c) an explicit `(insufficient data)` marker — a single body line in the form `> (insufficient data: <what is missing>)`
- Code/commands use fenced code blocks, **language tag required** (` ```go `, ` ```solidity `, ` ```bash `, etc.).
- Tables use GFM tables only (HTML tables forbidden).
- Korean body + English proper nouns. Code symbols, function names, event names, EIP/ERC numbers, and repo paths stay in English. For the detailed directive, see §Language policy.

## Wikilinks

- `[[slug]]` — display name automatic (slug → converted to title).
- `[[slug|display name]]` — alias display.
- Linking a non-existent page triggers isolation to the queue as `REVIEW: missing-page` (§REVIEW types).
- `related` frontmatter is an *explicit graph edge*; body `[[wikilink]]` is a *contextual edge*. Both kinds are used for graph traversal/revisit (Grep + Read + Glob + wikilink hop).

## REVIEW types

REVIEW blocks are NOT ingested into the body; they are sent only to the `.olw/review-queue.md` queue. Each item must be labeled with **exactly one type**, evaluating the following decision tree *in order* (mutually exclusive: once it matches above, stop evaluating the predicates below).

1. Two *existing wiki pages* hold *conflicting claims* about the same fact → `contradiction`
2. Two *existing wiki pages* hold the same *concept* under different slugs (the facts are identical) → `duplicate`
3. The body invokes `[[X]]` but page `X` does not exist → `missing-page`
4. The body identifies a divergence between the *official spec* and the *monorepo code* → `spec-drift`
5. An *address/opcode/constant/security property* appears in the body without a sources citation → `security-claim`
6. An item where spec/code agreement *needs confirmation* (no contradiction, but unverified) → `confirmation`
7. Otherwise, an *optional improvement* (style/extra citation/context enrichment) → `suggestion` (catch-all)

Each REVIEW item's severity is `high | medium | low`. Severity decision guide:
- `high`: direct impact on user funds/security (e.g., wrong contract address, security-claim)
- `medium`: impact on protocol semantics (e.g., spec-drift)
- `low`: curation/style (e.g., suggestion, duplicate)

Queue status values (`status`) are `open | resolved | dismissed | deep-research-needed`. Only humans update status (op-wiki only appends as `open`).

## Type catalog

A single `type` value determines almost all logic branching — graph node color, search weight, lint rules, and type-specific field enforcement at ingest. **This table is the single source of truth**; other files such as op-wiki SKILL.md only cite by reference.

| type | folder | Definition | Example pages |
|---|---|---|---|
| `protocol` | `wiki/protocols/` | OP Stack protocol flows/mechanisms | `derivation.md`, `fault-proof-game.md`, `batch-submission.md` |
| `component` | `wiki/components/` | Execution module / daemon / binary | `op-node.md`, `op-batcher.md`, `op-challenger.md`, `op-reth.md` |
| `contract` | `wiki/contracts/` | L1/L2 smart contracts | `optimism-portal-2.md`, `l2-output-oracle.md`, `fault-dispute-game.md` |
| `concept` | `wiki/concepts/` | Abstract concepts | `finality.md`, `data-availability.md`, `pre-image.md`, `safe-head.md` |
| `source` | `wiki/sources/` | 1:1 summary page of an original document | `paper-mips-fault-proof.md`, `eip-4844-blob.md` |
| `synthesis` | `wiki/synthesis/` | Multi-page synthesis/integration | `l2-finality-end-to-end.md`, `bridging-trust-model.md` |
| `troubleshooting` | `wiki/troubleshooting/` | A temporal incident — the symptom/environment/hypothesis/verification/root cause/resolution/recurrence-prevention narrative of an error/failure/unexpected behavior that occurred | `op-batcher-blob-revert-granite.md`, `withdrawal-proof-stale-output-root.md` |
| `overview` | `wiki/overview.md` (single file, no folder) | Area intro/landing (currently a single whole-wiki overview) | `overview.md` |

**Note the overview exception**: the `overview` type has no folder and exists only as the single file `wiki/overview.md`. If a request comes in to create a new type=overview page, always overwrite/merge into `wiki/overview.md` (op-wiki SKILL.md §merge procedure); do NOT create a separate folder.

**Note the troubleshooting index exception**: troubleshooting *pages* still live in the `wiki/troubleshooting/` folder like any other type, but they are **NOT** listed in `wiki/index.md`. They are cataloged in a dedicated `wiki/troubleshooting.md` index file — a sibling of `wiki/index.md` / `wiki/log.md` at the wiki root — so that temporal incidents are managed separately from the conceptual page catalog. The `## troubleshooting` section therefore does NOT appear in `wiki/index.md`. The op-wiki ingest procedure routes troubleshooting rows to `wiki/troubleshooting.md` instead of `wiki/index.md` (op-wiki SKILL.md §6); this schema only fixes the location convention.

## Language policy

This is the **single source of truth** for the wiki's language policy (Korean body + English proper nouns/symbols/code). Every ingest LLM call applies the following directive.

```
Write all wiki page bodies and descriptive titles in Korean.
Keep English for: proper nouns (op-node, OptimismPortal2, FaultDisputeGame,
DisputeGameFactory, L2OutputOracle, op-batcher, op-challenger, …),
code symbols, function names, event names, struct names, EIP/ERC numbers
(EIP-4844, EIP-1559, ERC-20, …), repository paths
(optimism/op-node, ethereum-optimism/optimism, …).
Slugs must be English kebab-case (e.g., optimism-portal-2, fault-dispute-game).
Do not transliterate English proper nouns into Hangul (e.g., never write
'옵티미즘 포털' for OptimismPortal2 — keep it in English).
```

An English ratio ≤ 30% (proper nouns excluded from the count) is the body's self-estimation criterion. This §Language policy covers only the Korean policy for wiki page bodies (`wiki/**.md`).

## Sources

When citing a URL, you **MUST** record `fetched: YYYY-MM-DD` alongside each item in the `sources:` array. This ensures that even if the domain disappears or the page moves, *the content as of that point in time* is preserved as a body paraphrase.

```yaml
sources:
  - url: https://specs.optimism.io/protocol/derivation.html
    fetched: YYYY-MM-DD   # MUST
    section: "L2 Block Derivation"
  - path: /home/choi/projects/personal/optimism-llm/optimism/op-node/rollup/derive/engine_queue.go
    fetched: YYYY-MM-DD   # local paths are MUST too
    lines: 120-180
```
