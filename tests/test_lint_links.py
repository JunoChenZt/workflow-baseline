from pathlib import Path

import pytest

import lint_links


@pytest.mark.parametrize("heading, expected", [
    ("2.7 刹车自检（8 问）", "27-刹车自检8-问"),
    ("### 2.9.5 交付单（固定三栏，2026-09-29 立）", "295-交付单固定三栏2026-09-29-立"),
    ("Reading Order（什么时候读哪一份子文档）", "reading-order什么时候读哪一份子文档"),
    ("6. PR 描述模板（决策溯源）", "6-pr-描述模板决策溯源"),
])
def test_slug_matches_github_rules(heading, expected):
    assert lint_links.slug(heading.lstrip("#")) == expected


def _tree(root: Path):
    (root / "a.md").write_text(
        "# A\n\n## 真标题\n\n"
        "[ok](b.md) [bad](nope.md) [anc](b.md#没有的) [anc-ok](a.md#真标题) "
        "[http](https://x.y/z) [mail](mailto:a@b) [line](b.md:12) [dir](sub/) [tpl](<node>.md)\n",
        encoding="utf-8")
    (root / "b.md").write_text("# B\n", encoding="utf-8")
    (root / "sub").mkdir()
    (root / "sub" / "c.md").write_text("[out](../../elsewhere.md)\n", encoding="utf-8")
    (root / ".git").mkdir()
    (root / ".git" / "ignored.md").write_text("[x](zzz.md)\n", encoding="utf-8")


def test_check_reports_only_real_problems(tmp_path):
    _tree(tmp_path)
    broken, anchors = lint_links.check(tmp_path)
    assert sorted(broken) == ["a.md: nope.md", "sub/c.md: ../../elsewhere.md"]  # .git 里的不扫；:12 / dir/ / http / mailto / <模板> 不算
    assert len(anchors) == 1 and "没有的" in anchors[0]


def test_scope_limits_which_files_are_scanned(tmp_path):
    _tree(tmp_path)
    broken, _ = lint_links.check(tmp_path, ["a.md"])
    assert broken == ["a.md: nope.md"]
    broken, _ = lint_links.check(tmp_path, ["sub/"])
    assert broken == ["sub/c.md: ../../elsewhere.md"]


def test_main_exit_codes(tmp_path, monkeypatch, capsys):
    _tree(tmp_path)
    monkeypatch.setattr(lint_links, "ROOT", tmp_path)
    monkeypatch.setattr(lint_links, "load", lambda: {"checks": {"link_scope": ["a.md"]}})
    assert lint_links.main([]) == 1                       # 有断链
    (tmp_path / "nope.md").write_text("", encoding="utf-8")
    assert lint_links.main([]) == 0                       # 只剩锚点错 → 默认 WARN
    assert lint_links.main(["--anchors"]) == 1            # --anchors 才 hard-fail
    out = capsys.readouterr().out
    assert "ANCHOR a.md" in out and "scope=['a.md']" in out


def test_self_test_passes():
    lint_links.self_test()


def test_real_repo_maintained_layers_have_no_broken_links():
    assert lint_links.main([]) == 0
