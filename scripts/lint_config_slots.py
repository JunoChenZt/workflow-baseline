"""骨架 / 配置对账：core/ 里用到的每个 {{key}} 必须在 project-config.md 有定义；core/ 里不得出现项目名词；
项目指令文件里的「过程规则」编号条目必须与 core/01 §0 接入片段逐字一致（两份真值不许分叉）。

用法：
  python scripts/lint_config_slots.py            # 任一违反 → exit 1
  python scripts/lint_config_slots.py --self-test

登记：checks.md「lint_config_slots」
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import ROOT, load  # noqa: E402

SLOT = re.compile(r"\{\{([\w.]+)\}\}")
DEFINED = re.compile(r"^\| `([\w.]+)` \|", re.M)
IGNORE_SLOTS = {"key"}  # README 里解释记法用的字面量
RULE_ITEM = re.compile(r"^\d+\. .*$", re.M)


def snippet_drift(core01: Path, instructions: Path) -> list[str]:
    """项目指令里的编号规则条目 vs core/01 §0 片段：条数可少不可多，出现的每条必须逐字相同。"""
    if not core01.exists() or not instructions.exists():
        return []
    src = RULE_ITEM.findall(core01.read_text(encoding="utf-8").split("## 1.")[0])
    dst = RULE_ITEM.findall(instructions.read_text(encoding="utf-8"))
    out = []
    if len(dst) > len(src):
        out.append(f"{instructions.name}: 规则条目 {len(dst)} 条 > core/01 §0 的 {len(src)} 条")
    for i, (a, b) in enumerate(zip(src, dst), 1):
        if a != b:
            out.append(f"{instructions.name}: 第 {i} 条与 core/01 §0 不一致 —— 指令:「{b[:40]}…」 骨架:「{a[:40]}…」")
    return out


def check(core_dir: Path, config_md: Path, leak_terms: list[str]) -> list[str]:
    problems: list[str] = []
    defined = set(DEFINED.findall(config_md.read_text(encoding="utf-8")))
    leak = re.compile("|".join(re.escape(t) for t in leak_terms)) if leak_terms else None
    for f in sorted(core_dir.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        for key in sorted(set(SLOT.findall(text)) - IGNORE_SLOTS):
            if key not in defined:
                problems.append(f"{f.name}: 槽位 {{{{{key}}}}} 在 project-config.md 无定义")
        if leak:
            body = text.split("## 6. CHANGELOG")[0]  # 变更记录写出处，不算泄漏
            for i, line in enumerate(body.splitlines(), 1):
                m = leak.search(line)
                if m:
                    problems.append(f"{f.name}:{i}: 项目名词泄漏「{m.group(0)}」")
    return problems


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        r = Path(td)
        core = r / "core"
        core.mkdir()
        cfg = r / "project-config.md"
        cfg.write_text("| `a.b` | 1 | 说明 |\n", encoding="utf-8")
        (core / "x.md").write_text("用 {{a.b}} 和 {{missing}}。\n提到 SecretProj 一次。\n## 6. CHANGELOG\n- SecretProj 出处\n", encoding="utf-8")
        p = check(core, cfg, ["SecretProj"])
        assert any("missing" in x for x in p), p
        assert sum("泄漏" in x for x in p) == 1, p
        (core / "x.md").write_text("只用 {{a.b}}。\n", encoding="utf-8")
        assert check(core, cfg, ["SecretProj"]) == []
        c01 = core / "01.md"
        c01.write_text("## 0. 片段\n```\n1. 甲\n2. 乙\n```\n## 1. 正文\n3. 不算\n", encoding="utf-8")
        ins = r / "CLAUDE.md"
        ins.write_text("1. 甲\n2. 乙\n", encoding="utf-8")
        assert snippet_drift(c01, ins) == []
        ins.write_text("1. 甲\n2. 乙改了\n", encoding="utf-8")
        assert any("第 2 条" in x for x in snippet_drift(c01, ins))
        ins.write_text("1. 甲\n2. 乙\n3. 多出来\n", encoding="utf-8")
        assert any("3 条 >" in x for x in snippet_drift(c01, ins))
    print("self-test: 未定义槽位会响、泄漏会响（CHANGELOG 除外）、片段分叉会响、干净不响 ✓")


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        self_test()
        return 0
    cfg = load()
    problems = check(ROOT / "core", ROOT / "project-config.md", cfg.get("core_leak_terms", []))
    problems += snippet_drift(ROOT / "core" / "01-entry-and-routing.md", ROOT / cfg.get("instructions_file", "CLAUDE.md"))
    for p in problems:
        print("SLOT", p)
    print(f"config-slots: problems={len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows GBK 控制台
    except Exception:
        pass
    sys.exit(main(sys.argv[1:]))
