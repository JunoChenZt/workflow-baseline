import io

import pytest

import lint_pr_body as lpb

GOOD = lpb.GOOD


def test_good_body_has_no_problems():
    assert lpb.check(GOOD) == []


@pytest.mark.parametrize("mutate, expect", [
    (lambda t: t.replace("- 档位: M（入口）→ M（DoD 对账）｜判据: …\n", ""), "档位"),
    (lambda t: t.replace("### 验证了什么、怎么验的", "### 验证"), "三栏不齐"),
    (lambda t: t.replace("- 冒烟 ⚪：原因 (a) 无 key → 请用户跑\n", ""), "空白"),
    (lambda t: t.replace("- 冒烟 ⚪：原因 (a) 无 key → 请用户跑", "- 冒烟 ⚪：原因 (a)\n\n全部通过。"), "总评"),
    (lambda t: t.replace("- 冒烟 ⚪：原因 (a) 无 key → 请用户跑", "- 冒烟 ⚪：原因 (a)\n\nAll Pass."), "总评"),
    (lambda t: t.replace("⚪ 1", "⚪ 0"), "≠ 第三栏"),
    (lambda t: t.replace("修 3 / 记账 1 / 明确不做 1", "修 3 / 记账 1 / 明确不做 0"), "finding"),
    (lambda t: t.replace("- 冒烟 ⚪：原因 (a) 无 key → 请用户跑", "- 冒烟没跑"), "没标 ⚪"),
])
def test_each_bad_form_is_reported(mutate, expect):
    problems = lpb.check(mutate(GOOD))
    assert any(expect in p for p in problems), problems


def test_third_column_none_forms_are_accepted():
    for none in ("无", "- 无", "（没有就写：无）"):
        body = GOOD.replace("- 冒烟 ⚪：原因 (a) 无 key → 请用户跑", none).replace("⚪ 1", "⚪ 0")
        assert lpb.check(body) == [], (none, lpb.check(body))


def test_none_third_column_allows_total_verdict_wording():
    body = GOOD.replace("- 冒烟 ⚪：原因 (a) 无 key → 请用户跑", "无").replace("⚪ 1", "⚪ 0") + "\n全部通过。\n"
    assert lpb.check(body) == []


def test_sections_out_of_order_is_reported():
    body = GOOD.replace("### 改了什么\n- a.py：x\n", "").replace("### 未验证什么、为什么", "### 未验证什么、为什么\n\n### 改了什么\n- a.py：x")
    assert any("顺序" in p for p in lpb.check(body))


def test_finding_regex_accepts_both_spellings():
    assert lpb.FINDING.search("坐实 5 条 = 本 PR 修 3 / 记账 1 / 明确不做 1").groups() == ("5", "3", "1", "1")
    assert lpb.FINDING.search("坐实 4 = 修 2 / 记账 1 / 不做 1").groups() == ("4", "2", "1", "1")


def test_main_reads_file_and_stdin(tmp_path, monkeypatch, capsys):
    p = tmp_path / "body.md"
    p.write_text(GOOD, encoding="utf-8")
    assert lpb.main(["--file", str(p)]) == 0
    monkeypatch.setattr("sys.stdin", io.StringIO(GOOD.replace("⚪ 1", "⚪ 0")))
    assert lpb.main([]) == 1
    assert "DELIVERY" in capsys.readouterr().out


def test_self_test_passes():
    lpb.self_test()


def test_example_walkthrough_delivery_form_passes(repo_root):
    text = (repo_root / "core/examples/walkthrough-cli-json-flag.md").read_text(encoding="utf-8")
    start = text.index("## 交付单 (goal TMP-json.1)")
    end = text.index("```", start)
    body = "- 档位: M\n- 计数: ✅ 3 / ❌ 0 / ⚪ 1\n" + text[start:end]
    assert lpb.check(body) == []
