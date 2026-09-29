from datetime import date

import metrics_report as mr

SAMPLE = mr.SAMPLE
TODAY = date(2026, 9, 29)


def test_tables_split_by_h2_and_drop_header_and_separator():
    t = mr.tables("# m\n## A\n| x | y |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n## B\n无表\n## C\n| p |\n|---|\n| q |\n")
    assert t == {"A": [["1", "2"], ["3", "4"]], "B": [], "C": [["q"]]}


def test_rule_classification():
    out = mr.report(SAMPLE, TODAY, 90)
    assert "退役候选：老规则（上次 271 天前" in out          # 2026-01-01 → 271 天
    assert "退役候选：空规则（上次 从未命中·立账日未知" in out
    assert "退役候选：新规则" not in out                       # 9 天前命中
    assert "退役候选：新立账" not in out and "1 条新立账观察中" in out


def test_threshold_moves_the_line():
    out = mr.report(SAMPLE, TODAY, 5)
    assert "退役候选：新规则" in out                           # 9 天 ≥ 5
    assert "退役候选：新立账" in out                            # 立账 28 天 ≥ 5


def test_pr_table_counts_upgrades_rework_and_unverified_by_month():
    out = mr.report(SAMPLE, TODAY, 90)
    assert "S 档被自动升档 1 次" in out
    assert "| 2026-09 | 2 | 2 | 1 | 1 |" in out


def test_short_rows_are_skipped_not_crashed():
    text = SAMPLE + "| 只有一列 |\n"
    mr.report(text, TODAY, 90)


def test_main_reads_real_ledger(monkeypatch, capsys):
    assert mr.main(["--today", "2026-09-29"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("# 流程划算度报告 · 2026-09-29") and "## PR 台账" in out


def test_main_honours_config_ledger_path(tmp_path, monkeypatch, capsys):
    (tmp_path / "led.md").write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(mr, "ROOT", tmp_path)
    monkeypatch.setattr(mr, "load", lambda: {"metrics": {"ledger": "led.md", "retire_after_days": 5}})
    assert mr.main(["--today", "2026-09-29"]) == 0
    assert "退役候选：新规则" in capsys.readouterr().out


def test_self_test_passes():
    mr.self_test()
