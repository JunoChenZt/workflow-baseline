"""文档链接检查：仓内所有 .md 的相对链接必须指向存在的文件；锚点按 GitHub 规则核。

用法：
  python scripts/lint_links.py            # 文件级断链 → exit 1；锚点错 → 只警告
  python scripts/lint_links.py --anchors  # 锚点错也 exit 1
  python scripts/lint_links.py --self-test  # 证明「它会响」：造一个断链，必须报错

登记：checks.md「lint_links」
"""
from __future__ import annotations

import os
import posixpath
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import ROOT, load  # noqa: E402

LINK = re.compile(r"\]\(([^)\s]+)\)")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def slug(heading: str) -> str:
    """近似 GitHub 的标题 → 锚点规则：小写、去标点（保留 - 与空格）、空格变 -。"""
    h = heading.strip().lower()
    h = re.sub(r"[^\w\s一-鿿-]", "", h)
    return h.replace(" ", "-")


def headings(path: Path) -> set[str]:
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#"):
            out.add(slug(line.lstrip("#")))
    return out


def md_files(root: Path, scope: list[str] | None = None):
    """scope = 路径前缀列表（相对 root）；None = 全仓。快照层文件的二级链接指向未打包文件，不在检查范围。"""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if not f.endswith(".md"):
                continue
            p = Path(dirpath) / f
            rel = p.relative_to(root).as_posix()
            if scope is None or any(rel == s or rel.startswith(s.rstrip("/") + "/") for s in scope):
                yield p


def check(root: Path, scope: list[str] | None = None) -> tuple[list[str], list[str]]:
    """返回 (文件级断链, 锚点错)。每项是一行可读文字。"""
    broken: list[str] = []
    anchors: list[str] = []
    hcache: dict[Path, set[str]] = {}
    for f in md_files(root, scope):
        rel = f.relative_to(root).as_posix()
        d = posixpath.dirname(rel)
        for m in LINK.finditer(f.read_text(encoding="utf-8", errors="replace")):
            raw = m.group(1)
            if raw.startswith(("http://", "https://", "mailto:")) or "<" in raw:
                continue
            target, _, frag = raw.partition("#")
            target = re.sub(r":\d+$", "", target.rstrip("/"))
            if target:
                tpath = root / posixpath.normpath(posixpath.join(d, target))
            else:
                tpath = f
            if not tpath.exists():
                broken.append(f"{rel}: {raw}")
                continue
            if frag and tpath.suffix == ".md" and tpath.is_file():
                hs = hcache.setdefault(tpath, headings(tpath))
                if frag not in hs:
                    anchors.append(f"{rel}: {raw}（{tpath.relative_to(root).as_posix()} 无此锚点）")
    return broken, anchors


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        r = Path(td)
        (r / "a.md").write_text("# A\n\n## 真标题\n\n[ok](b.md) [bad](nope.md) [anc](b.md#没有的) [anc-ok](a.md#真标题)\n", encoding="utf-8")
        (r / "b.md").write_text("# B\n", encoding="utf-8")
        broken, anchors = check(r)
        assert broken == ["a.md: nope.md"], broken
        assert len(anchors) == 1 and "没有的" in anchors[0], anchors
        (r / "snap").mkdir()
        (r / "snap" / "c.md").write_text("[out](../../elsewhere.md)\n", encoding="utf-8")
        assert check(r, ["a.md"]) == (["a.md: nope.md"], anchors), "scope 应只扫 a.md"
        assert "snap/c.md: ../../elsewhere.md" in check(r)[0], "无 scope 应扫到 snap"
    print("self-test: 断链会响、锚点错会响、好链接不响 ✓")


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        self_test()
        return 0
    scope = load().get("checks", {}).get("link_scope")
    broken, anchors = check(ROOT, scope)
    for b in broken:
        print("BROKEN", b)
    for a in anchors:
        print("ANCHOR", a)
    print(f"links: broken={len(broken)} anchor_miss={len(anchors)} scope={scope or '全仓'}")
    if broken:
        return 1
    if anchors and "--anchors" in argv:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows GBK 控制台
    except Exception:
        pass
    sys.exit(main(sys.argv[1:]))
