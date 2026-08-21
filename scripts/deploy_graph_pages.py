#!/usr/bin/env python3
"""deploy_graph_pages.py — graphify 산출물을 GitHub Pages(gh-pages 브랜치)로 배포.

graphify-out/ 은 .gitignore 대상(재생성 가능 산출물)이고, graph.html 은 LLM 추출
결과라 CI 에서 재빌드할 수 없다. 따라서 배포는 항상 "로컬 빌드 결과를 orphan
gh-pages 브랜치에 올리는" 형태다. main 히스토리에는 생성물이 남지 않는다.

배포 구성:
  index.html        graph.html (좌하단에 Wiki/Report 네비게이션 주입)
  report.html       GRAPH_REPORT.md 변환본
  wiki/index.html   graphify wiki 진입점 + 커뮤니티/god node 문서
  wiki/*.md         에이전트 크롤링용 원본 마크다운 동봉
  graph.json        GraphRAG 원본 데이터
  .nojekyll         Jekyll 처리 비활성화(퍼센트 인코딩 한글 파일명 보호)

markdown 패키지가 있으면 사용하고, 없으면 내장 폴백 변환기를 쓴다(외부 의존성 없음).

사용법:
  python3 scripts/deploy_graph_pages.py --out /tmp/site   # 빌드만, git 미접촉
  python3 scripts/deploy_graph_pages.py --no-push         # gh-pages 커밋까지
  python3 scripts/deploy_graph_pages.py                   # 커밋 + push

최초 1회는 저장소 Settings > Pages 에서 Source 를 gh-pages 브랜치 / root 로
지정해야 한다(admin 권한 필요, 스크립트가 대신 켤 수 없음).
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# graph.html 은 사이드바가 오른쪽(border-left)이라 좌하단이 비어 있다.
NAV_HTML = """
<div id="gp-nav" style="position:fixed;bottom:14px;left:14px;z-index:9999;
 font:13px/1.4 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
 background:#1a1a2ee6;color:#e0e0e0;border:1px solid #2a2a4e;border-radius:8px;
 padding:7px 12px;box-shadow:0 2px 12px #0006">
<a href="wiki/index.html" style="color:#8ab4dd;text-decoration:none">Wiki</a>
<span style="color:#3a3a5e;margin:0 8px">|</span>
<a href="report.html" style="color:#8ab4dd;text-decoration:none">Report</a>
<span style="color:#3a3a5e;margin:0 8px">|</span>
<a href="graph.json" style="color:#8ab4dd;text-decoration:none">graph.json</a>
</div>
"""

PAGE_TMPL = """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{ color-scheme: dark; }}
body {{ margin:0; background:#0f0f1a; color:#d8d8e0;
  font:15px/1.75 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',sans-serif; }}
.wrap {{ max-width:860px; margin:0 auto; padding:28px 20px 80px; }}
nav.top {{ position:sticky; top:0; background:#0f0f1aee; border-bottom:1px solid #2a2a4e;
  padding:10px 20px; font-size:13px; backdrop-filter:blur(6px); }}
nav.top a {{ color:#8ab4dd; text-decoration:none; margin-right:14px; }}
nav.top a:hover {{ text-decoration:underline; }}
h1,h2,h3 {{ color:#f0f0f5; line-height:1.35; margin:1.6em 0 .6em; }}
h1 {{ font-size:1.7em; margin-top:.4em; }} h2 {{ font-size:1.3em; }} h3 {{ font-size:1.1em; }}
a {{ color:#8ab4dd; }}
code {{ background:#1a1a2e; border:1px solid #2a2a4e; border-radius:4px;
  padding:1px 5px; font-size:.9em; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
pre {{ background:#1a1a2e; border:1px solid #2a2a4e; border-radius:8px;
  padding:12px 14px; overflow-x:auto; }}
pre code {{ background:none; border:none; padding:0; }}
blockquote {{ margin:1em 0; padding:.4em 1em; border-left:3px solid #4E79A7;
  background:#16162a; color:#aaa; }}
hr {{ border:none; border-top:1px solid #2a2a4e; margin:2em 0; }}
table {{ border-collapse:collapse; width:100%; display:block; overflow-x:auto; }}
th,td {{ border:1px solid #2a2a4e; padding:6px 10px; text-align:left; }}
th {{ background:#1a1a2e; }}
ul,ol {{ padding-left:1.4em; }}
li {{ margin:.25em 0; }}
</style>
</head><body>
<nav class="top"><a href="{root}index.html">← Graph</a><a href="{root}wiki/index.html">Wiki</a><a href="{root}report.html">Report</a></nav>
<div class="wrap">
{body}
</div>
</body></html>
"""

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)\|([^\]]+)\]\]")
WIKILINK_BARE_RE = re.compile(r"\[\[([^\]]+)\]\]")
MD_HREF_RE = re.compile(r'(href=")([^"]+?)\.md((?:#[^"]*)?")')


# ---------------------------------------------------------------- markdown

def _fallback_markdown(text: str) -> str:
    """markdown 패키지가 없을 때 쓰는 최소 변환기.

    graphify wiki/report 가 쓰는 문법(제목·목록·링크·강조·인용·코드펜스·hr)만
    다룬다. 일반 목적 변환기가 아니다.
    """
    out: list[str] = []
    in_code = False
    list_stack: list[str] = []

    def close_lists(to_depth: int = 0) -> None:
        while len(list_stack) > to_depth:
            out.append(f"</{list_stack.pop()}>")

    def inline(s: str) -> str:
        s = html.escape(s, quote=False)
        s = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                   lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
        return s

    for raw in text.splitlines():
        if raw.lstrip().startswith("```"):
            if in_code:
                out.append("</code></pre>")
            else:
                close_lists()
                out.append("<pre><code>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html.escape(raw, quote=False))
            continue

        line = raw.rstrip()
        if not line.strip():
            close_lists()
            continue
        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", line.strip()):
            close_lists()
            out.append("<hr>")
            continue

        m = re.match(r"(#{1,6})\s+(.*)", line)
        if m:
            close_lists()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            continue

        m = re.match(r"(\s*)([-*+]|\d+\.)\s+(.*)", line)
        if m:
            depth = len(m.group(1)) // 2 + 1
            tag = "ul" if m.group(2) in "-*+" else "ol"
            while len(list_stack) > depth:
                out.append(f"</{list_stack.pop()}>")
            while len(list_stack) < depth:
                list_stack.append(tag)
                out.append(f"<{tag}>")
            out.append(f"<li>{inline(m.group(3))}</li>")
            continue

        if line.lstrip().startswith(">"):
            close_lists()
            out.append(f"<blockquote>{inline(line.lstrip()[1:].strip())}</blockquote>")
            continue

        close_lists()
        out.append(f"<p>{inline(line)}</p>")

    if in_code:
        out.append("</code></pre>")
    close_lists()
    return "\n".join(out)


def md_to_html(text: str, use_ext: bool = True) -> str:
    if use_ext:
        try:
            import markdown  # type: ignore
            return markdown.markdown(text, extensions=["extra", "sane_lists", "nl2br"])
        except ImportError:
            pass
    return _fallback_markdown(text)


def render_page(md_text: str, title: str, root: str, use_ext: bool = True) -> str:
    # [[a|b]] / [[a]] 위키링크는 Obsidian 볼트 전용이라 배포본에서는 평문으로 낮춘다.
    md_text = WIKILINK_RE.sub(r"\2", md_text)
    md_text = WIKILINK_BARE_RE.sub(r"\1", md_text)
    body = md_to_html(md_text, use_ext)
    # 상대 .md 링크 → .html (http(s) 절대링크는 건드리지 않음)
    body = MD_HREF_RE.sub(
        lambda m: m.group(0) if m.group(2).startswith(("http://", "https://", "//"))
        else f"{m.group(1)}{m.group(2)}.html{m.group(3)}", body)
    return PAGE_TMPL.format(title=html.escape(title), root=root, body=body)


# ---------------------------------------------------------------- build

def build_site(source: Path, dest: Path, use_ext: bool = True) -> dict:
    graph_html = source / "graph.html"
    if not graph_html.is_file():
        sys.exit(f"error: {graph_html} 가 없습니다. 먼저 /graphify 로 그래프를 빌드하세요.")

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    stats = {"wiki_pages": 0}

    # 1. index.html ← graph.html + 네비게이션 주입
    page = graph_html.read_text(encoding="utf-8")
    if "</body>" in page:
        page = page.replace("</body>", NAV_HTML + "</body>", 1)
    else:
        page += NAV_HTML
    (dest / "index.html").write_text(page, encoding="utf-8")

    # 2. graph.json
    src_json = source / "graph.json"
    if src_json.is_file():
        shutil.copy2(src_json, dest / "graph.json")

    # 3. report.html
    report = source / "GRAPH_REPORT.md"
    if report.is_file():
        (dest / "report.html").write_text(
            render_page(report.read_text(encoding="utf-8"), "Graph Report", "", use_ext),
            encoding="utf-8")
        shutil.copy2(report, dest / "GRAPH_REPORT.md")

    # 4. wiki/ — 변환본(.html) + 에이전트용 원본(.md)
    src_wiki = source / "wiki"
    if src_wiki.is_dir():
        out_wiki = dest / "wiki"
        out_wiki.mkdir()
        for md in sorted(src_wiki.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            title = next((l.lstrip("# ").strip() for l in text.splitlines()
                          if l.startswith("# ")), md.stem)
            (out_wiki / f"{md.stem}.html").write_text(
                render_page(text, title, "../", use_ext), encoding="utf-8")
            shutil.copy2(md, out_wiki / md.name)
            stats["wiki_pages"] += 1

    # 5. Jekyll 비활성화 — 퍼센트 인코딩된 한글 파일명이 재작성되지 않도록
    (dest / ".nojekyll").write_text("", encoding="utf-8")
    return stats


# ---------------------------------------------------------------- git

def git(*args: str, cwd: Path | None = None, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=cwd or REPO,
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"error: git {' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout.strip()


def branch_exists(ref: str) -> bool:
    return subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref],
                          cwd=REPO, capture_output=True).returncode == 0


def deploy(stage: Path, branch: str, remote: str, message: str, push: bool) -> None:
    wt = Path(tempfile.mkdtemp(prefix="gh-pages-"))
    try:
        git("fetch", remote, branch, check=False)
        if branch_exists(branch):
            git("worktree", "add", str(wt), branch)
        elif branch_exists(f"{remote}/{branch}"):
            git("worktree", "add", "-b", branch, str(wt), f"{remote}/{branch}")
        else:
            git("worktree", "add", "--detach", str(wt))
            git("checkout", "--orphan", branch, cwd=wt)
            git("rm", "-rf", ".", cwd=wt, check=False)

        # 삭제분이 반영되도록 매 배포마다 내용 전체 교체
        for item in wt.iterdir():
            if item.name == ".git":
                continue
            shutil.rmtree(item) if item.is_dir() else item.unlink()
        for item in stage.iterdir():
            shutil.copytree(item, wt / item.name) if item.is_dir() \
                else shutil.copy2(item, wt / item.name)

        git("add", "-A", cwd=wt)
        if not git("status", "--porcelain", cwd=wt):
            print("변경 없음 — 커밋을 건너뜁니다.")
        else:
            git("commit", "-m", message, cwd=wt)
            print(f"커밋 완료: {branch} — {message}")
        if push:
            git("push", remote, branch, cwd=wt)
            print(f"push 완료: {remote}/{branch}")
        else:
            print(f"push 생략 (--no-push). 수동 배포: git push {remote} {branch}")
    finally:
        git("worktree", "remove", "--force", str(wt), check=False)
        shutil.rmtree(wt, ignore_errors=True)


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(
        description="graphify 산출물을 GitHub Pages(gh-pages)로 배포",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="최초 1회: 저장소 Settings > Pages 에서 Source = gh-pages / root 지정 필요")
    ap.add_argument("--source", default="graphify-out", help="graphify 출력 디렉터리 (기본 graphify-out)")
    ap.add_argument("--out", help="빌드 결과만 이 경로에 생성하고 git 은 건드리지 않음")
    ap.add_argument("--branch", default="gh-pages", help="배포 브랜치 (기본 gh-pages)")
    ap.add_argument("--remote", default="origin", help="원격 이름 (기본 origin)")
    ap.add_argument("--no-push", action="store_true", help="커밋만 하고 push 는 하지 않음")
    ap.add_argument("--message", help="커밋 메시지 (기본: 노드/엣지 수 자동 기입)")
    ap.add_argument("--no-ext-markdown", action="store_true",
                    help="markdown 패키지 대신 내장 폴백 변환기 사용")
    args = ap.parse_args()

    source = (REPO / args.source).resolve() if not os.path.isabs(args.source) else Path(args.source)
    use_ext = not args.no_ext_markdown

    if args.out:
        dest = Path(args.out).resolve()
        stats = build_site(source, dest, use_ext)
        print(f"빌드 완료: {dest}  (wiki {stats['wiki_pages']} 페이지)")
        return

    stage = Path(tempfile.mkdtemp(prefix="graph-site-"))
    try:
        stats = build_site(source, stage, use_ext)
        message = args.message
        if not message:
            import json
            g = json.loads((source / "graph.json").read_text(encoding="utf-8"))
            # networkx node-link 포맷은 엣지 키가 'links' 다 ('edges' 인 판본도 있음)
            edges = g.get("links", g.get("edges", []))
            message = (f"chore: 지식 그래프 사이트 배포 "
                       f"({len(g['nodes'])} nodes, {len(edges)} edges, "
                       f"wiki {stats['wiki_pages']} pages)")
        deploy(stage, args.branch, args.remote, message, push=not args.no_push)
    finally:
        shutil.rmtree(stage, ignore_errors=True)


if __name__ == "__main__":
    main()
