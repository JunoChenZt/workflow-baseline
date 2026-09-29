# -*- coding: utf-8 -*-
"""Lint all tracked markdown files for broken relative links.

CJK-safe: uses `git ls-files -z` (NUL-separated, no quotepath escaping),
so files with Chinese names are scanned instead of silently skipped.
(2026-07-30 PR #218 review 教训: quotepath 转义串当路径读 → CJK 文件全跳过 → 假 0。)

Usage:
  python scripts/lint_doc_links.py            # exit 0 = clean, exit 1 = broken links found
  python scripts/lint_doc_links.py --verbose  # also print scan stats

Checks [label](target) style links in *.md:
  - skips http(s)/mailto links
  - URL-decodes targets (%20 etc.)
  - strips :NN / :LNN-LNN line suffixes and #anchors before existence check
  - skips template placeholders (<node-id>, 0X-name, etc.)
  - skips frozen evidence snapshots listed in SKIP_SOURCES / *.trace.md under docs/observations/ (machine-generated verbatim evidence)

Same-page anchor check (WARN 试用期, 2026-08-14 · #240 冷审 defer 落地):
  - pure-anchor links `[x](#slug)` are checked against the file's own headings
    (GitHub slug rules, see ``github_slug``); dead ones are printed as WARN
  - ⚠️ WARN 不影响 exit code —— 按 e2e-acceptance-standard §4 试用期规则,
    升 hard-fail 需用户裁决 (试用期观察误报后再升)
  - 🔒 slug 规则**先自校准再判**: ``_SLUG_CALIBRATION`` 里是本仓已实证
    可跳转的 (标题 → 锚点) 对; 校不过 → exit 2 拒绝出任何结论。
    出处: 2026-08-14 清 61 条死锚点时, 手写 slug 规则被校准连着证伪两次
    (全角括号被误留 / 标题里 markdown 链接的 URL 也被喂进 slug)。
  - 锚点集 = `#` 标题的 slug **加上**手写的 `<a id=…>`/`<a name=…>`
    (本仓拿显式锚点当兼容垫片: 标题追加 `✅ CLOSED` 后缀后旧 slug 失效)
  - 围栏代码块整块剥掉再判: 里面的 `# xxx` 不是标题, `](#x)` 也不是链接
  - 边界(声明·非验证): 跨文件锚点 `file.md#anchor` 的锚点半仍不查
    (存在性检查只看 `#` 前的路径半)

  ⚠️ 上面三条里的前两条是 2026-08-14 冷审补的 —— 初版**手写正则去猜 markdown
  的渲染规则**, 三处与真实行为不符且**全是静默方向**(代码块造出 184 个幽灵锚点
  可遮死链 / 显式锚点被判死 / 带 title 的写法整条漏扫)。与 #239 冷审同一族病:
  自己建模别人的语义, 追不平的每一条都是静默偏差。
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import urllib.parse
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LINK = re.compile(r"\[([^\]\n]*)\]\(([^)\s]+?)(?:\s+\"[^\"]*\")?\)")
LINE_SUFFIX = re.compile(r":L?\d+(-L?\d+)?$")

# ---- same-page anchors (WARN trial) ---------------------------------------

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# 带 title 的写法 `](#slug "提示")` 也要认 —— 与上面 LINK 的 title 子模式保持一致。
# 初版只认紧跟右括号的形式，那种链接**整条漏扫**（死活都不出声）。
PAGE_ANCHOR = re.compile(r"\]\(#([^)\s]+?)(?:\s+\"[^\"]*\")?\)")
# 显式锚点：标题改了名之后用来接住旧链接的兼容垫片，本仓在用
# （docs/governance/backlog.md 有一个）。不收它 → 把真能跳的链接报成死锚点。
HTML_ANCHOR = re.compile(r"<a\s[^>]*\b(?:id|name)\s*=\s*[\"']([^\"']+)[\"']", re.I)
_MD_LINK_IN_HEADING = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_EMPHASIS = re.compile(r"(\*\*|\*|`|~~)")
_FENCE = re.compile(r"^\s*(```+|~~~+)")


def strip_code_fences(text: str) -> str:
    """把围栏代码块的**内容**换成空行（行号逐行对齐，WARN 才报得准）。

    围栏里的东西不是渲染后的 markdown：`# xxx` 那行不是标题，`](#x)` 也不是链接。
    两边都得剥，否则各错一个方向 ——
      - 不剥标题：代码块里的注释行被当成标题写进合法锚点集。实测全仓多出 **184 个**
        幽灵锚点（README 从安装示例块拿到 `#配置-api-key` / `#python--310`，
        pr-template 从模板示例块拿到 `#节点`），而这些名字恰恰最像真实目录项 →
        真死锚点撞上同名幽灵就**静默放行**；
      - 不剥链接：代码块里写的锚点语法字面量被当成真链接报死（噪音）。
    """
    out: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        m = _FENCE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)[:3]
                out.append("")
                continue
            out.append(line)
        else:
            # 收尾围栏：同种符号即可（长度可不等，CommonMark 允许收尾更长）
            out.append("")
            if m and m.group(1).startswith(fence):
                fence = None
    return "\n".join(out)


def rendered_heading_text(heading_md: str) -> str:
    """标题的**渲染后文本** —— GitHub 拿它算锚点, 不是拿 markdown 源码.

    关键: `[#223](https://…)` 渲染成 `#223`, URL 根本不参与 slug
    (校准第二次证伪抓的就是这条: 把 URL 喂进 slug → 多报死锚点).
    """
    s = _MD_LINK_IN_HEADING.sub(r"\1", heading_md)
    return _EMPHASIS.sub("", s).strip()


def github_slug(rendered: str) -> str:
    """渲染后标题 → GitHub 页内锚点.

    规则 (由 ``_SLUG_CALIBRATION`` 实证钉住, 不是猜的):
      小写; 空格→`-`; `-`/`_` 保留; 字母/数字/组合标记 (含 CJK·圈号②·
      变体选择符) 保留; emoji (Symbol-other ≥ U+2100) 保留;
      其余标点/符号 (**含全角括号「」——校准第一次证伪抓的**) 一律丢弃且不留 `-`.
    """
    import unicodedata

    out: list[str] = []
    for ch in rendered.lower():
        cat = unicodedata.category(ch)
        if ch in " \t":
            out.append("-")
        elif ch in "-_":
            out.append(ch)
        elif cat[0] in ("L", "N", "M"):
            out.append(ch)
        elif cat == "So" and ord(ch) >= 0x2100:
            out.append(ch)
    return "".join(out)


# 本仓已实证可跳转的 (标题 markdown 源码 → 锚点) 对 —— slug 规则的判据.
# 覆盖面各有分工: CJK+全角括号 / 标题内 markdown 链接 / emoji+方括号 / 圈号+冒号 / 点号.
_SLUG_CALIBRATION: list[tuple[str, str]] = [
    (
        "BA. 本地证券名录 DB 未持久化到 volume（S2 首次部署起会每次重建清零）（2026-07-29 docs-audit surface）",
        "ba-本地证券名录-db-未持久化到-volumes2-首次部署起会每次重建清零2026-07-29-docs-audit-surface",
    ),
    (
        "BG. 往 .env / .env.example 加数值项会静默架空「测代码默认值」的断言 —— 无人守（2026-08-03 [#223](https://github.com/JunoChenZt/subagent-for-investment/pull/223) review 沉淀切出）",
        "bg-往-env--envexample-加数值项会静默架空测代码默认值的断言--无人守2026-08-03-223-review-沉淀切出",
    ),
    (
        "6.8 🔴 [active] worktree base-check 反模式 + 假设 remote 状态未 fetch (PR-C 事故)",
        "68-🔴-active-worktree-base-check-反模式--假设-remote-状态未-fetch-pr-c-事故",
    ),
    (
        "附录 A：深核② measurement 脚本（只读复现）",
        "附录-a深核②-measurement-脚本只读复现",
    ),
    ("0.2 活跃条目一览表", "02-活跃条目一览表"),
]


def calibrate_slugger() -> list[str]:
    """跑校准; 返回不吻合项 (空 = 校准通过). 校不过的 slug 规则出的任何
    结论都不可信 —— caller 必须 exit 2, 不许带着坏尺子继续量."""
    bad = []
    for heading_md, expected in _SLUG_CALIBRATION:
        got = github_slug(rendered_heading_text(heading_md))
        if got != expected:
            bad.append(f"{heading_md[:40]}... -> got {got!r}, expected {expected!r}")
    return bad


def heading_slugs(text: str) -> set[str]:
    """本页全部**可跳转锚点**的集合 —— 两个来源，缺一个就会误报/漏报。

    1. `#` 标题生成的 slug，含 GitHub 重复标题去重（二次出现 → `slug-1`）；
    2. 手写的 `<a id="…">` / `<a name="…">`。本仓拿它当**兼容垫片**：标题被追加
       `✅ CLOSED …` 后缀之后旧 slug 失效，写个显式锚点把旧链接接住。不收它 →
       把一条**真能跳的链接**报成死锚点。

    ⚠️ 入参应当是 :func:`strip_code_fences` 处理过的文本（调用方负责），
    否则代码块里的注释行会被当成标题混进来。
    """
    seen: Counter[str] = Counter()
    slugs: set[str] = set()
    for line in text.splitlines():
        for explicit in HTML_ANCHOR.findall(line):
            slugs.add(explicit)
        m = HEADING.match(line)
        if not m:
            continue
        s = github_slug(rendered_heading_text(m.group(2)))
        slugs.add(s if seen[s] == 0 else f"{s}-{seen[s]}")
        seen[s] += 1
    return slugs


def scan_page_anchors(rel_path: str, text: str) -> list[tuple[str, int, str]]:
    """本页 `[x](#slug)` 里跳不到本页任何锚点的那些 (WARN 用, 不进 exit code)."""
    body = strip_code_fences(text)
    slugs = heading_slugs(body)
    dead: list[tuple[str, int, str]] = []
    for lineno, line in enumerate(body.splitlines(), 1):
        for m in PAGE_ANCHOR.finditer(line):
            anchor = urllib.parse.unquote(m.group(1))
            if anchor not in slugs:
                dead.append((rel_path, lineno, m.group(1)))
    return dead

# 冻结证据快照：内容是历史复制品，链接断裂属快照事实，不修不报
SKIP_SOURCES = {
    "docs/observations/fm-refactor-spec/D-hot-e2e-2026-06-16/baseline-scratch/guide-originmain.md",
}


def _is_frozen_evidence(path: str) -> bool:
    """机器产的 verbatim 证据文件 → 整文件跳过。

    trace.md 是 trace_report 渲染的 LLM 调用全量记录，正文里嵌着模型原始
    输出——网页摘要 + 盖章标恰好拼成 `29[W#sentiment-4-1#n3](w)` 这类
    markdown 链接形状（2026-08-03 实测：seg2 obs 落账起连红 main CI 三笔）。
    这些"链接"是证据内容不是文档链接，逐个加 SKIP_SOURCES 是打地鼠——
    每次跑批都会再产 trace.md。按形状豁免：observations 下的 *.trace.md
    全是段式 e2e 的机器产物（trace_report.py 唯一写手），没有人写的链接。
    """
    if path in SKIP_SOURCES:
        return True
    return path.startswith("docs/observations/") and path.endswith(".trace.md")


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, cwd=REPO, check=True
    ).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def tracked_index() -> tuple[set[str], set[str]]:
    """(tracked file set, implied dir set) — 精确大小写，与 CI checkout 一致。

    存在性判定用 git index 而非 os.path.exists：
    - 本地未入库文件（gitignored `_checkpoints/`、`.env` 等）不算存在 → 本地结论 == CI 结论
    - Windows 大小写不敏感 fs 不会放过大小写错位（index 存精确大小写）
    """
    files = set(tracked_files())
    dirs = {""}
    for f in files:
        d = os.path.dirname(f)
        while d:
            dirs.add(d)
            d = os.path.dirname(d)
    return files, dirs


def is_placeholder(target: str) -> bool:
    return "<" in target or ">" in target or "0X-name" in target or target == "state"


def resolve_target(href: str, base: str) -> str | None:
    """href → repo-relative path to check, or None if this href is not checkable.

    None means "deliberately not a local-file link" (external scheme, pure
    anchor, template placeholder), **not** "checked and fine" — callers must
    not count these as scanned links.
    """
    if href.startswith(("http://", "https://", "#", "mailto:")):
        return None
    target = href.split("#")[0]
    target = LINE_SUFFIX.sub("", target)
    if not target or is_placeholder(target):
        return None
    target = urllib.parse.unquote(target)
    rel = os.path.normpath(os.path.join(base, target)).replace("\\", "/")
    rel = rel.rstrip("/")
    return "" if rel == "." else rel


def scan_markdown(
    rel_path: str, text: str, tracked: set[str], dirs: set[str]
) -> tuple[list[tuple[str, int, str]], int]:
    """Pure core: (broken links, number of local links actually checked).

    Extracted from ``main`` 2026-08-07 (闸门矩阵 G0.2) so the rules can be
    mutation-tested without a git checkout. ``main`` keeps sole responsibility
    for enumerating files and reading them; behaviour is unchanged.
    """
    broken: list[tuple[str, int, str]] = []
    scanned = 0
    base = os.path.dirname(rel_path)
    for lineno, line in enumerate(text.splitlines(), 1):
        for _label, href in LINK.findall(line):
            rel = resolve_target(href, base)
            if rel is None:
                continue
            scanned += 1
            if rel not in tracked and rel not in dirs:
                broken.append((rel_path, lineno, href))
    return broken, scanned


def main() -> int:
    verbose = "--verbose" in sys.argv

    # 先校准 slug 规则, 校不过 → 拒绝出任何结论 (与 READ FAIL 同级: 尺子坏了
    # 不是 finding, 是不能开工).
    calib_bad = calibrate_slugger()
    if calib_bad:
        print("lint_doc_links: slug calibration FAILED — refusing to run", file=sys.stderr)
        for b in calib_bad:
            print(f"  {b}", file=sys.stderr)
        return 2

    tracked, dirs = tracked_index()
    md = [f for f in sorted(tracked) if f.endswith(".md") and not _is_frozen_evidence(f)]
    broken: list[tuple[str, int, str]] = []
    dead_anchors: list[tuple[str, int, str]] = []
    scanned_links = 0
    for f in md:
        path = os.path.join(REPO, f)
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            print(f"READ FAIL {f}: {e}", file=sys.stderr)
            return 2  # 读失败必须显式炸，不许静默跳过（本 linter 存在的理由）
        f_broken, f_scanned = scan_markdown(f, text, tracked, dirs)
        broken.extend(f_broken)
        scanned_links += f_scanned
        dead_anchors.extend(scan_page_anchors(f, text))

    if verbose:
        print(f"scanned {len(md)} md files, {scanned_links} relative links")
    if dead_anchors:
        # ⚠️ WARN 试用期: 只报不红 (exit code 只由 broken 决定).
        # 升 hard-fail 需用户裁决 —— 别顺手把下面这段接进 return 1。
        print(
            f"lint_doc_links: WARN {len(dead_anchors)} dead in-page anchor(s)"
            " [试用期 · 不影响 exit code]"
        )
        for f, lineno, anchor in dead_anchors:
            print(f"  WARN {f}:{lineno}  (#{anchor})")
    if broken:
        print(f"lint_doc_links: {len(broken)} broken link(s)\n")
        for f, lineno, href in broken:
            print(f"  {f}:{lineno}  ({href})")
        return 1
    print("lint_doc_links: all links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
