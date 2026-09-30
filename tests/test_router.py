import json
import shutil
import subprocess
from pathlib import Path

import pytest

import router

CFG = router.CFG
NO_H = router.NO_H
rows_of = router.rows_of


# ---------- 输入解析 ----------
def test_parse_numstat_handles_binary_and_junk():
    rows = router.parse_numstat("5\t3\tsrc/a.py\n-\t-\timg.png\n不是三列\n")
    assert [(r["path"], r["add"], r["del"]) for r in rows] == [("src/a.py", 5, 3), ("img.png", 0, 0)]


def test_parse_numstat_strips_git_quotes_on_non_ascii_paths():
    # git 对含中文的路径输出 "docs/plans/\344\270..." 带引号；不去引号顶层目录会算成 '"docs'
    rows = router.parse_numstat('1\t0\t"docs/plans/\\344\\270\\255.md"\n')
    assert rows[0]["path"].startswith("docs/plans/") and not rows[0]["path"].startswith('"')
    assert router.top_dir(rows[0]["path"], []) == "docs"


@pytest.mark.parametrize("path, bucket", [
    ("tests/test_a.py", "tests"), ("src/app/test_b.py", "tests"), ("docs/x.md", "docs"), ("README.md", "docs"),
    (".github/workflows/ci.yml", "infra"), ("pyproject.toml", "infra"), ("config/app.yml", "config"),
    ("src/app/a.py", "src"), ("Makefile", "other"),
])
def test_bucket_order_is_priority(path, bucket):
    assert router.bucket_of(path, CFG["tier"]["buckets"]) == bucket


def test_top_dir_pairs_tests_with_src():
    pairs = CFG["tier"]["same_dir_pairs"]
    assert router.top_dir("tests/test_a.py", pairs) == "src"
    assert router.top_dir("src/app/a.py", pairs) == "src"
    assert router.top_dir("README.md", pairs) == "."


def test_test_for_maps_by_convention():
    tm = CFG["tier"]["test_map"]
    assert router.test_for("src/app/a.py", tm) == "tests/test_a.py"
    assert router.test_for("docs/x.md", tm) is None


# ---------- 坑表解析 ----------
def test_load_pitfalls_reads_only_entries_with_path_field(tmp_path):
    t = tmp_path / "pit.md"
    t.write_text(
        "### 3.2 通用\n"
        "- 🔴 [active] 改路由前确认 fallback 链（2026-09-29）\n"
        "  路径: router\\.py$, src/rout\n"
        "  动作: grill fallback\n"
        "  出处：retro X\n"
        "\n"
        "- 🟡 [mitigated] 没有路径字段的老条目\n"
        "  出处：Y\n"
        "### 3.3 别的段\n"
        "- 🟢 [active] 有路径无动作\n"
        "  路径: docs/\n",
        encoding="utf-8")
    entries = router.load_pitfalls(t, "路径:")
    assert [(e["severity"], e["section"], e["paths"], e["action"]) for e in entries] == [
        ("🔴", "§3.2 通用", ["router\\.py$", "src/rout"], "grill fallback"),
        ("🟢", "§3.3 别的段", ["docs/"], ""),
    ]


def test_load_pitfalls_accepts_h2_sections(tmp_path):
    t = tmp_path / "pit.md"
    t.write_text("## 1. 脚本与 CI\n- 🔴 [active] 管道吞退出码\n  路径: ^scripts/\n", encoding="utf-8")
    e = router.load_pitfalls(t, "路径:")
    assert len(e) == 1 and e[0]["section"] == "§1. 脚本与 CI"


def test_load_pitfalls_missing_table_is_empty(tmp_path):
    assert router.load_pitfalls(tmp_path / "nope.md", "路径:") == []


def test_real_pitfall_table_parses(repo_root):
    from _config import load
    cfg = load()
    entries = router.load_pitfalls(repo_root / cfg["pitfalls"]["table"], cfg["pitfalls"]["path_field"])
    assert isinstance(entries, list)
    for e in entries:
        assert e["paths"] and e["severity"] in "🔴🟡🟢"


# ---------- 档位规则 ----------
@pytest.fixture
def root_with_test(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("", encoding="utf-8")
    return tmp_path


def R(rows, h=NO_H, pit=(), root=None):
    return router.route(rows, h, CFG, list(pit), root)


def test_small_change_with_paired_test_is_S(root_with_test):
    r = R(rows_of(("src/app/a.py", 20, 5), ("tests/test_a.py", 30, 0)), root=root_with_test)
    assert r["tier"] == "S" and r["reasons"] == [] and r["verify"] == ["tests/test_a.py"]
    assert r["needs_user_confirmation"] is False and r["not_required"]


def test_missing_paired_test_is_M(root_with_test):
    r = R(rows_of(("src/app/b.py", 5, 0)), root=root_with_test)
    assert r["tier"] == "M" and "无配对测试" in r["reasons"][0]


@pytest.mark.parametrize("rows, h, tier, needle", [
    (rows_of(("docs/a.md", 400, 0), ("docs/b.md", 1, 0)), NO_H, "S", None),                     # docs 行数不限
    (rows_of(("docs/a.md", 1, 0), ("README.md", 1, 0)), NO_H, "M", "跨顶层"),
    (rows_of(("docs/1.md", 1, 0), ("docs/2.md", 1, 0), ("docs/3.md", 1, 0), ("docs/4.md", 1, 0), ("docs/5.md", 1, 0), ("docs/6.md", 1, 0)), NO_H, "M", "docs 桶 6 文件"),
    (rows_of(("src/app/a.py", 90, 20), ("tests/test_a.py", 1, 0)), NO_H, "M", "行"),
    (rows_of(("config/app.yml", 1, 0)), NO_H, "M", "config 桶 1 文件 > 0"),
    (rows_of(("src/app/schemas/x.py", 1, 0)), NO_H, "L", "L 档路径"),
    (rows_of((".github/workflows/ci.yml", 1, 0)), NO_H, "L", "L 档路径"),
    (rows_of(("pyproject.toml", 1, 0)), NO_H, "L", "依赖清单"),
    (rows_of(("src/app/a.py", 1, 0), ("tests/test_a.py", 1, 0)), {"h1": False, "h2": True, "h3": False}, "L", "H2"),
    (rows_of(("src/app/a.py", 1, 0), ("tests/test_a.py", 1, 0)), {"h1": False, "h2": False, "h3": True}, "L", "H3"),
    (rows_of(("src/app/a.py", 1, 0), ("tests/test_a.py", 1, 0)), {"h1": True, "h2": False, "h3": False}, "M", "H1"),
    (rows_of(("src/app/a.py", 1, 0), ("tests/test_a.py", 1, 0), ("src/app/old.py", 0, 30, "D")), NO_H, "M", "删除 1"),
    (rows_of(("src/app/a.py", 1, 0), ("tests/test_a.py", 1, 0), ("src/app/new.py", 0, 0, "R")), NO_H, "M", "重命名 1"),
])
def test_decision_table(root_with_test, rows, h, tier, needle):
    r = R(rows, h, root=root_with_test)
    assert r["tier"] == tier, r["reasons"]
    if needle:
        assert any(needle in x for x in r["reasons"]), r["reasons"]


def test_L_reasons_keep_M_reasons_too(root_with_test):
    r = R(rows_of(("src/app/schemas/x.py", 1, 0), ("docs/a.md", 1, 0)), root=root_with_test)
    assert r["tier"] == "L" and any("L 档路径" in x for x in r["reasons"]) and any("跨顶层" in x for x in r["reasons"])


def test_pitfall_hit_raises_to_M_and_injects_stop_condition(root_with_test):
    r = R(rows_of(("src/app/router.py", 3, 1), ("tests/test_router.py", 1, 0)), pit=router.PIT, root=root_with_test)
    assert r["tier"] == "M" and any("坑表" in x for x in r["reasons"])
    assert r["stop_conditions"] == ["§3.2-12 改路由前确认 fallback 链 → grill fallback"]


def test_yellow_pitfall_only_alerts(root_with_test):
    pit = [dict(router.PIT[0], severity="🟡", paths=[r"a\.py$"])]   # 不用 router.py：它本身命中 M 档路径
    r = R(rows_of(("src/app/a.py", 3, 1), ("tests/test_a.py", 1, 0)), pit=pit, root=root_with_test)
    assert r["tier"] == "S" and r["stop_conditions"] and not any("坑表" in x for x in r["reasons"])


# ---------- H 反查 ----------
def test_h_evidence_patterns():
    ev = router.h_evidence("parser.add_argument('--json')\nimport requests\nos.remove(p)\n")
    assert ev == {"h1": True, "h2": True, "h3": True}
    assert router.h_evidence("x = 1\n") == {"h1": False, "h2": False, "h3": False}


def test_warnings_only_when_declared_no(root_with_test):
    added = "import requests\n"
    r = router.route(rows_of(("src/app/a.py", 1, 0), ("tests/test_a.py", 1, 0)), NO_H, CFG, [], root_with_test, added=added)
    assert len(r["warnings"]) == 1 and "H2" in r["warnings"][0]
    r = router.route(rows_of(("src/app/a.py", 1, 0), ("tests/test_a.py", 1, 0)), {"h1": False, "h2": True, "h3": False}, CFG, [], root_with_test, added=added)
    assert r["warnings"] == []


# ---------- 声明解析与卡 ----------
def test_declared_and_h_from_body():
    assert router.declared_from_body("档位: S ｜ 事实: …") == "S"
    assert router.declared_from_body("档位: S → M（DoD 重算）") == "M"
    assert router.declared_from_body("档位：L") == "L"
    assert router.declared_from_body("无") is None
    assert router.h_from_body("H1 新增能力: 是  H2 外部副作用: 否  H3 不可逆: no") == {"h1": True, "h2": False, "h3": False}


def test_card_renders_all_lines(root_with_test):
    r = R(rows_of(("src/app/a.py", 1, 0), ("tests/test_a.py", 1, 0)), root=root_with_test)
    c = router.card(r)
    for key in ("档位: S", "H1 新增能力: 否", "必做:", "本档不要求:", "验证命令: pytest tests/test_a.py", "停止条件", "需用户确认: 否"):
        assert key in c, c


# ---------- main：三种模式 + 退出码 ----------
@pytest.fixture
def patched_main(monkeypatch, root_with_test):
    monkeypatch.setattr(router, "ROOT", root_with_test)
    monkeypatch.setattr(router, "load", lambda: dict(CFG, pitfalls={}))
    return root_with_test


def test_main_planned_mode_missing_h_defaults_to_no_with_warning(patched_main, capsys):
    assert router.main(["--planned", "src/app/a.py", "tests/test_a.py"]) == 0
    out = capsys.readouterr().out
    assert "缺人声明" in out and "档位: S" in out and "按「否」计" in out


def test_main_declared_below_computed_fails(patched_main, tmp_path, capsys):
    stat = tmp_path / "stat.txt"
    stat.write_text("1\t0\tsrc/app/schemas/x.py\n", encoding="utf-8")
    assert router.main(["--numstat-file", str(stat), "--h1", "no", "--h2", "no", "--h3", "no", "--declared", "M"]) == 1
    assert "TIER 声明 M 低于路由器算出的 L" in capsys.readouterr().out
    assert router.main(["--numstat-file", str(stat), "--h1", "no", "--h2", "no", "--h3", "no", "--declared", "L"]) == 0


def test_main_reads_declaration_and_h_from_pr_body(patched_main, tmp_path):
    stat = tmp_path / "stat.txt"
    stat.write_text("1\t0\tsrc/app/a.py\n1\t0\ttests/test_a.py\n", encoding="utf-8")
    body = tmp_path / "body.md"
    body.write_text("- 档位: S\n- H1 新增能力: 是  H2 外部副作用: 否  H3 不可逆: 否\n", encoding="utf-8")
    assert router.main(["--numstat-file", str(stat), "--pr-body-file", str(body)]) == 1   # H1=是 → M，声明 S 低
    body.write_text("- 档位: M\n- H1 新增能力: 是  H2 外部副作用: 否  H3 不可逆: 否\n", encoding="utf-8")
    assert router.main(["--numstat-file", str(stat), "--pr-body-file", str(body)]) == 0


def test_main_json_output_is_parseable(patched_main, capsys):
    assert router.main(["--planned", "src/app/a.py", "tests/test_a.py", "--h1", "no", "--h2", "no", "--h3", "no", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["tier"] == "S" and data["verify"] == ["tests/test_a.py"] and "facts" in data


@pytest.mark.skipif(shutil.which("git") is None, reason="需要 git")
def test_main_base_mode_uses_real_git_diff(tmp_path, monkeypatch):
    repo = tmp_path / "r"
    repo.mkdir()
    run = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True, text=True)
    run("init", "-q", "-b", "main")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    (repo / "src" / "app").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "src" / "app" / "a.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "tests" / "test_a.py").write_text("", encoding="utf-8")
    run("add", "-A")
    run("commit", "-q", "-m", "base")
    run("branch", "base")
    (repo / "src" / "app" / "a.py").write_text("import requests\nx = 2  # 中文注释：GBK 控制台下 subprocess 按 locale 解码会炸\n", encoding="utf-8")
    (repo / "RULES.md").write_text("红线：禁止 git push --force 与 DROP TABLE\n", encoding="utf-8")
    run("add", "-A")
    run("commit", "-q", "-am", "change")
    monkeypatch.setattr(router, "ROOT", repo)
    monkeypatch.setattr(router, "load", lambda: dict(CFG, pitfalls={}))
    rows = router.git_rows("base")
    assert [(r["path"], r["status"]) for r in rows] == [("RULES.md", "A"), ("src/app/a.py", "M")]
    added = router.git_added_lines("base")
    assert "import requests" in added and "中文注释" in added      # 2026-09-30 真跑撞出：text=True 默认 locale 解码
    assert "DROP TABLE" not in added                                # .md 里的规则文案不进反查
    r = router.route(rows, NO_H, CFG, [], repo, added)
    assert r["tier"] == "M"                                          # RULES.md 与 src 跨顶层目录
    assert [w[:2] for w in r["warnings"]] == ["H2"]                  # 只有网络 import 的警告，没有 .md 文案触发的 H3


def test_self_test_passes():
    router.self_test()
