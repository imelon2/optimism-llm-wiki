---
name: op-wiki
description: Ingest the current session's analysis/discussion into the Optimism / OP Stack wiki (./wiki/) following references/schema.md — create/update pages, merge, update index & log, and isolate ambiguity to the REVIEW queue. Use ONLY when the user explicitly asks to reflect findings into the wiki — triggers like "wiki 반영해줘", "위키에 반영", "위키에 추가해줘", "페이지로 만들어줘", "정리해서 저장", "ingest". This skill does NOT research or analyze (that is op-research); it ingests already-analyzed content that exists in the current session.
tools: Read, Write, Edit, Glob, Grep
---

Take the current session's conversation/analysis as input and create/update (ingest, reflect) `wiki/` pages in accordance with the `references/schema.md` conventions.


## Single source of truth (do NOT duplicate rules)

The page conventions live **only in `references/schema.md`**. This skill holds the procedure only; it points to the conventions via `see references/schema.md §<heading>`.

- Data structure (type / frontmatter / body / wikilink / language) → `references/schema.md`
- The 8 types → `references/schema.md §Type catalog`
- The 7 REVIEW types decision tree → `references/schema.md §REVIEW types`
- Language policy → `references/schema.md §Language policy`

At the start of ingest, Read `references/schema.md` to load the latest conventions.

## User gate (P2)

Enter the ingest procedure ONLY when one of the following expressions appears:

- "wiki 반영해줘" / "위키에 반영" / "위키에 추가해줘" / "페이지로 만들어줘" / "정리해서 저장" / "ingest"

If the gate is not passed, do NOT edit the wiki body *through any workaround*.

## Ingest procedure

Once the gate is passed, execute in order:

1. **Load & comply with references/schema.md** — Required frontmatter (9 fields) + the type-specific fields for that type + Body rules + Wikilinks + Type catalog. For fields with unknown values, add the `(insufficient data)` body marker + `REVIEW: confirmation`.

2. **Determine the target page** — `wiki/<type-folder>/<slug>.md`. First check whether the page already exists with Glob/Grep.

3. **Produce the FILE block** — emit the page in the following strict format, then Write it to the actual file:
   ```
   ---FILE: wiki/<type-folder>/<slug>.md---
   ---
   <YAML frontmatter — all required + type-specific fields from references/schema.md>
   ---
   <markdown body with [[wikilinks]]>
   ---END---
   ```

4. **Isolate ambiguity/contradiction into a REVIEW block** (P4) — do not leak arbitrary decisions into the body:
   ```
   ---REVIEW: <type>---
   type: <one of the 7 in references/schema.md §REVIEW types>
   severity: high | medium | low
   pages: <affected wiki/.../....md paths>
   description: <one-paragraph rationale>
   ---END---
   ```
   Do NOT ingest the REVIEW block into the page body; instead append it as a new row to `.olw/review-queue.md` (id = `RV-YYYYMMDD-NNN`, status=`open`).

5. **Merge existing pages** — combine the two versions, but take the union (dedup) for `sources`/`related`/`affects`/`tags`, use the later date for `updated`, and isolate contradictions with `REVIEW: contradiction`. Duplicate slugs are also consolidated to a canonical name via this §merge procedure (references/schema.md §File naming).

6. **Update the index** — insert an alphabetically ordered `- [[<slug>]] — <title>` row into the relevant index. For `type=troubleshooting` pages the target is the dedicated `wiki/troubleshooting.md` index (references/schema.md §Type catalog troubleshooting-index note); for every other type it is the relevant type section of `wiki/index.md`.

7. **Prepend to log.md** — prepend a session entry to `wiki/log.md`. Format:
   ```
   ## [YYYY-MM-DD] ingest | <one-line summary>
   - pages: <list of created/updated slugs>
   - review: <list of emitted RV-ids, or none>
   - note: <1-2 lines of learning notes>
   ```

8. **Prepend to question.md** — a brief entry in `wiki/question.md`: `# YYYY-MM-DD` + `Q. "<original ≤150 chars>"` + `output:` + the list of produced wikilinks. log.md handles the detailed narrative, so keep this minimal.

## LLM behavioral principles (ingest system prompt)

- **No speculation** (P3) — "probably/presumably" is forbidden. Every claim must be one of `[[slug]]` / a `sources` citation / `(insufficient data)` (references/schema.md §Body rules).
- **No chain-of-thought output** — reason internally, but emit only the result.
- **Language policy** — Korean body + English proper nouns/symbols/code; do not transliterate proper nouns (references/schema.md §Language policy).
- **Mandatory citation of risky identifiers** — do NOT write contract addresses, hard-fork activation dates, EIP numbers, opcodes, constants, or security properties into the body without a sources citation → emit `REVIEW: security-claim`.
- **No automatic merging of contradictions** (P4) — if two sources conflict, do not arbitrarily adopt one; isolate with `REVIEW: contradiction`.
- **Do NOT create pages in any format other than the FILE/REVIEW IR blocks.**

## Verification (ingest exit self-check)

- [ ] Every claim is backed by one of `[[slug]]` / a source URL (fetched) / `(insufficient data)`
- [ ] All required + type-specific frontmatter is filled (unknowns use `(insufficient data)` + `REVIEW: confirmation`)
- [ ] Korean body + English proper-noun policy complied with (English ratio ≤ 30%)
- [ ] No risky identifiers in the body without a sources citation (if any, `REVIEW: security-claim`)
- [ ] Contradictions/ambiguities isolated to `.olw/review-queue.md`
- [ ] Alphabetically ordered row inserted into the relevant index (`wiki/troubleshooting.md` for troubleshooting pages, otherwise the relevant type section of `wiki/index.md`)
- [ ] Ingest entry prepended to `wiki/log.md`
- [ ] Brief entry prepended to `wiki/question.md`
- [ ] Non-existent `[[X]]` links flagged as `REVIEW: missing-page`

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
