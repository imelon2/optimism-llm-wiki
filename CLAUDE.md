# Optimism LLM Wiki

Optimism LLM Wiki is a markdown knowledge base that accumulates and maintains OP Stack engineering knowledge so that LLMs can directly write and read it. Its structure is designed by combining Andrej Karpathy's "LLM Wiki" with the Google "Open Knowledge Format" (OKF) v0.1.

## Additional Documentation

More detailed guidance for AI agents can be found in:

- [docs/ai/wiki-structure.md](docs/ai/wiki-structure.md) — layers/directories/type, frontmatter schema, tags, cross-links, body style
- [docs/ai/op-stack-references.md](docs/ai/op-stack-references.md) — location and usage of OP Stack analysis/research source material (official docs, local sources, CodeGraph)

## Language and Documentation Guidelines

- The default language for communication is `Korean`.
- Write explanations, summaries, documentation, and comment-style text in Korean, but preserve code, commands, logs, and proper nouns in their original form.

## Git Commit Rules

- Commits are **authored by the `git-master` agent** (automatic style detection, atomic commits).
- In environments where the git-master agent is unavailable, **first inspect recent commit messages with `git log`** to understand the format, language, structure, and trailers, then write the commit yourself matching that style.
- Write commit messages in `Korean`.
- Commits that include `./wiki` changes must start the message with `wiki:`.
