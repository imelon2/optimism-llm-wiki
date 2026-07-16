#!/usr/bin/env python3
"""lint_wiki.py — LLM Wiki 정합성 점검 (7-pass health check).

기계적으로 잡을 수 있는 결함만 점검한다. 의미적 모순(contradiction) 탐지는
LLM 패스(별도)의 몫이다 — docs/research-llm-wiki-skills.md §4.3 참고.

Passes:
  1. broken link    본문 상대링크가 실제 파일을 가리키나
  2. orphan page    index.md/다른 페이지에서 인바운드 링크 없는 페이지
  3. index missing  wiki/ 안에 있으나 index.md에 등록 안 된 페이지
  4. frontmatter    필수 type 누락 / OKF 5필드 결측 경고
  5. stale          source_commit이 resource submodule HEAD와 불일치
  6. log shape      log.md 항목 형식 '## [YYYY-MM-DD] <op> | <대상>' 검증
  7. tag vocab      알려진 tags 축에서 벗어난 태그 경고

표준 라이브러리만 사용한다(외부 의존성 없음).
사용법:  python3 scripts/lint_wiki.py [wiki_dir]   (기본값 ./wiki)
종료코드: error 가 하나라도 있으면 1, 아니면 0. (warning 은 0)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field

# wiki-structure.md 의 tags 축 (분류체계는 등장 빈도에 따라 확장됨 → 경고만)
KNOWN_TAGS = {
    "op-stack", "bridge", "fault-proofs", "derivation", "batcher", "proposer",
    "sequencer", "withdrawals", "deposits", "governance", "da", "p2p", "sync", "reth", "l1", "l2", "rfc",
    "observability", "monitoring", "sre", "txpool",
    "eip-1559", "fees", "gas",
}
VALID_TYPES = {"Concept", "Contract", "Component", "Spec", "Runbook", "RFC"}
OKF_FIELDS = ("type", "title", "description", "resource", "tags", "timestamp")
RESERVED = {"index.md", "log.md"}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
LOG_ENTRY_RE = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] (ingest|query|lint|init) \| .+")


@dataclass
class Findings:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def parse_frontmatter(text: str) -> dict[str, str]:
    """`---` 로 감싼 단순 YAML frontmatter 를 key->raw_value 로 파싱.

    pyyaml 의존을 피하려고 한 줄 `key: value` 만 처리한다(중첩 미지원).
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm: dict[str, str] = {}
    for line in text[3:end].splitlines():
        line = line.split("#", 1)[0].rstrip()  # 인라인 주석 제거
        if not line.strip() or ":" not in line:
            continue
        key, _, val = line.partition(":")
        fm[key.strip()] = val.strip()
    return fm


def parse_tags(raw: str) -> list[str]:
    raw = raw.strip().strip("[]")
    return [t.strip().strip("'\"") for t in raw.split(",") if t.strip()]


def md_pages(wiki_dir: str) -> list[str]:
    """예약 파일을 뺀 모든 .md 페이지의 wiki 기준 상대경로."""
    pages = []
    for root, _, files in os.walk(wiki_dir):
        for f in files:
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(root, f), wiki_dir)
            if rel in RESERVED:
                continue
            pages.append(rel)
    return sorted(pages)


def submodule_head(sub: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", sub, "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def lint(wiki_dir: str) -> Findings:
    f = Findings()
    wiki_dir = wiki_dir.rstrip("/")
    repo_root = os.path.dirname(os.path.abspath(wiki_dir))
    pages = md_pages(wiki_dir)

    # 페이지 본문/frontmatter 캐시
    bodies: dict[str, str] = {}
    fronts: dict[str, dict[str, str]] = {}
    for rel in pages:
        with open(os.path.join(wiki_dir, rel), encoding="utf-8") as fh:
            text = fh.read()
        bodies[rel] = text
        fronts[rel] = parse_frontmatter(text)

    # index.md 로드 + 등록된 링크 타깃 수집
    index_path = os.path.join(wiki_dir, "index.md")
    index_text = ""
    index_targets: set[str] = set()
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as fh:
            index_text = fh.read()
        for m in LINK_RE.finditer(index_text):
            index_targets.add(_norm_target(m.group(1), "", wiki_dir))
    else:
        f.error("index.md 가 없습니다.")

    # 인바운드 링크 그래프 (orphan 판정용): 페이지 본문 + index
    inbound: dict[str, int] = {rel: 0 for rel in pages}

    # ---- Pass 1: broken link ----
    for rel in pages:
        src_dir = os.path.dirname(rel)
        for m in LINK_RE.finditer(bodies[rel]):
            target = m.group(1)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            norm = _norm_target(target, src_dir, wiki_dir)
            if norm is None:
                continue  # wiki 밖(상위 디렉토리 등) → 점검 범위 외
            abspath = os.path.join(wiki_dir, norm)
            if not os.path.exists(abspath):
                f.error(f"[broken link] {rel} → {target} (대상 파일 없음)")
            elif norm in inbound:
                inbound[norm] += 1
    # index 가 가리키는 페이지도 인바운드로 카운트
    for tgt in index_targets:
        if tgt in inbound:
            inbound[tgt] += 1

    # ---- Pass 2: orphan page ----
    for rel in pages:
        if inbound.get(rel, 0) == 0:
            f.warn(f"[orphan] {rel} — 인바운드 링크 없음(index/다른 페이지에서 링크되지 않음)")

    # ---- Pass 3: index missing ----
    for rel in pages:
        if rel not in index_targets:
            f.error(f"[index missing] {rel} — index.md 에 등록되지 않음")

    # ---- Pass 4: frontmatter ----
    for rel in pages:
        fm = fronts[rel]
        if not fm:
            f.error(f"[frontmatter] {rel} — frontmatter 가 없거나 파싱 불가")
            continue
        t = fm.get("type")
        if not t:
            f.error(f"[frontmatter] {rel} — 필수 필드 'type' 누락")
        elif t not in VALID_TYPES:
            f.error(f"[frontmatter] {rel} — 알 수 없는 type '{t}' (허용: {sorted(VALID_TYPES)})")
        for key in OKF_FIELDS:
            if key not in fm:
                f.warn(f"[frontmatter] {rel} — OKF 필드 '{key}' 결측")

    # ---- Pass 5: stale ----
    heads = {
        "resource/optimism": submodule_head(os.path.join(repo_root, "resource/optimism")),
        "resource/infra": submodule_head(os.path.join(repo_root, "resource/infra")),
    }
    for rel in pages:
        fm = fronts[rel]
        sc = fm.get("source_commit")
        if not sc:
            continue
        sc = sc.strip().strip("<>")
        res = fm.get("resource", "")
        sub = next((s for s in heads if res.startswith(s)), "resource/optimism")
        head = heads.get(sub)
        if head is None:
            f.warn(f"[stale] {rel} — {sub} HEAD 를 확인할 수 없음(submodule 미초기화?)")
        elif not (sc.startswith(head) or head.startswith(sc)):
            f.warn(f"[stale] {rel} — source_commit {sc} != {sub} HEAD {head} (재확인 필요)")

    # ---- Pass 6: log shape ----
    log_path = os.path.join(wiki_dir, "log.md")
    if not os.path.exists(log_path):
        f.error("log.md 가 없습니다.")
    else:
        with open(log_path, encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                if line.startswith("## ") and not LOG_ENTRY_RE.match(line.rstrip()):
                    f.error(f"[log shape] log.md:{i} — 형식 위반: {line.rstrip()!r} "
                            f"(기대: '## [YYYY-MM-DD] <op> | <대상>')")

    # ---- Pass 7: tag vocab ----
    for rel in pages:
        tags = parse_tags(fronts[rel].get("tags", ""))
        for tag in tags:
            if tag not in KNOWN_TAGS:
                f.warn(f"[tag vocab] {rel} — 미등록 태그 '{tag}' "
                       f"(오타이거나 분류체계 확장 후보)")

    return f


def _norm_target(target: str, src_dir: str, wiki_dir: str) -> str | None:
    """링크 타깃을 wiki 기준 상대경로로 정규화. wiki 밖이면 None."""
    target = target.split("#", 1)[0]  # 앵커 제거
    if not target:
        return None
    joined = os.path.normpath(os.path.join(src_dir, target))
    if joined.startswith(".."):
        return None
    return joined


def main(argv: list[str]) -> int:
    wiki_dir = argv[1] if len(argv) > 1 else "wiki"
    if not os.path.isdir(wiki_dir):
        print(f"error: wiki 디렉토리를 찾을 수 없습니다: {wiki_dir}", file=sys.stderr)
        return 2

    f = lint(wiki_dir)
    n_pages = len(md_pages(wiki_dir))

    for w in f.warnings:
        print(f"WARN  {w}")
    for e in f.errors:
        print(f"ERROR {e}")

    print(f"\nlint_wiki: {n_pages} pages, "
          f"{len(f.errors)} errors, {len(f.warnings)} warnings")
    return 1 if f.errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
