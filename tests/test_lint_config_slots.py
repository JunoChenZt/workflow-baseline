from pathlib import Path

import lint_config_slots as lcs


def _core(tmp_path: Path, text: str) -> tuple[Path, Path]:
    core = tmp_path / "core"
    core.mkdir(exist_ok=True)
    (core / "x.md").write_text(text, encoding="utf-8")
    cfg = tmp_path / "project-config.md"
    cfg.write_text("| `a.b` | 1 | 说明 |\n| `c` | 2 | 说明 |\n", encoding="utf-8")
    return core, cfg


def test_undefined_slot_is_reported(tmp_path):
    core, cfg = _core(tmp_path, "用 {{a.b}} 和 {{missing}} 和 {{c}}。\n")
    problems = lcs.check(core, cfg, [])
    assert problems == ["x.md: 槽位 {{missing}} 在 project-config.md 无定义"]


def test_literal_key_placeholder_is_ignored(tmp_path):
    core, cfg = _core(tmp_path, "记法：{{key}} 表示槽位。\n")
    assert lcs.check(core, cfg, []) == []


def test_leak_reported_with_line_number_but_not_in_changelog(tmp_path):
    core, cfg = _core(tmp_path, "第一行\n提到 SecretProj 一次。\n## 6. CHANGELOG\n- SecretProj 出处\n")
    problems = lcs.check(core, cfg, ["SecretProj"])
    assert problems == ["x.md:2: 项目名词泄漏「SecretProj」"]


def test_main_exit_codes(tmp_path, monkeypatch):
    core, cfg = _core(tmp_path, "干净 {{a.b}}\n")
    monkeypatch.setattr(lcs, "ROOT", tmp_path)
    monkeypatch.setattr(lcs, "load", lambda: {"core_leak_terms": ["SecretProj"]})
    assert lcs.main([]) == 0
    (core / "x.md").write_text("SecretProj\n", encoding="utf-8")
    assert lcs.main([]) == 1


def test_self_test_passes():
    lcs.self_test()


def test_real_skeleton_is_clean():
    assert lcs.main([]) == 0
