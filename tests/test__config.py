import pytest

import _config


def test_load_parses_fenced_block(config_md):
    p = config_md('{"tier": {"s_limits": {"src": [3, 100]}}, "paths": {"l": [], "m": []}}')
    cfg = _config.load(p)
    assert cfg["tier"]["s_limits"]["src"] == [3, 100]


def test_load_without_fence_exits_with_message(tmp_path):
    p = tmp_path / "project-config.md"
    p.write_text("# 没有围栏\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        _config.load(p)
    assert "找不到" in str(e.value)


def test_load_invalid_json_exits_with_message(config_md):
    p = config_md('{"tier": [broken')
    with pytest.raises(SystemExit) as e:
        _config.load(p)
    assert "不是合法 JSON" in str(e.value)


def test_real_config_has_every_key_the_scripts_read():
    cfg = _config.load()
    assert set(cfg["tier"]) >= {"buckets", "s_limits", "same_dir_pairs", "test_map", "dependency_files"}
    assert set(cfg["paths"]) == {"l", "m"}
    assert set(cfg["pitfalls"]) == {"table", "path_field"}
    assert cfg["metrics"]["retire_after_days"] > 0 and cfg["metrics"]["ledger"]
    assert cfg["checks"]["link_scope"] and isinstance(cfg["core_leak_terms"], list)
    for name, _files_lines in cfg["tier"]["s_limits"].items():
        assert len(_files_lines) == 2, name


def test_real_config_regexes_compile():
    import re
    cfg = _config.load()
    for _, pat in cfg["tier"]["buckets"]:
        re.compile(pat)
    for pat in cfg["paths"]["l"] + cfg["paths"]["m"] + cfg["tier"]["dependency_files"]:
        re.compile(pat)
    for pat, _repl in cfg["tier"]["test_map"]:
        re.compile(pat)
