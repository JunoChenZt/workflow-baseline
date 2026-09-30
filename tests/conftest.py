"""scripts/ 下的脚本不是包，靠 sys.path 导入；ROOT 指仓库根。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def repo_root() -> Path:
    return REPO


@pytest.fixture
def config_md(tmp_path: Path):
    """写一份最小 project-config.md（只有机器可读块 + 一行定义表），返回路径。"""
    def _make(block: str, defined: str = "| `a.b` | 1 | 说明 |\n") -> Path:
        p = tmp_path / "project-config.md"
        p.write_text(defined + "\n```json project-config\n" + block + "\n```\n", encoding="utf-8")
        return p
    return _make
