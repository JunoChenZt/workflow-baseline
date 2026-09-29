"""读取 project-config.md 里的机器可读块（```json project-config 围栏）。

所有检查脚本共用；配置只有一份，改 project-config.md 即可。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_MD = ROOT / "project-config.md"
FENCE = re.compile(r"```json project-config\s*\n(.*?)\n```", re.S)


def load(path: Path = CONFIG_MD) -> dict:
    text = path.read_text(encoding="utf-8")
    m = FENCE.search(text)
    if not m:
        raise SystemExit(f"{path}: 找不到 ```json project-config 围栏块")
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path}: 机器可读块不是合法 JSON：{e}")
