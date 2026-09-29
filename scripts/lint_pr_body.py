"""交付单格式检查（core/05 §5 五条硬规则 + core/06 §3 finding 对账）。

输入：PR 描述 / goal 汇报的 markdown 文本。
用法：
  python scripts/lint_pr_body.py --file body.md
  cat body.md | python scripts/lint_pr_body.py
  python scripts/lint_pr_body.py --self-test

检查项：
  1 档位行：存在「档位: S|M|L」
  2 三栏齐：### 改了什么 / ### 验证了什么 / ### 未验证什么 三个标题按序存在
  3 第三栏非空：至少一条项目，或明确写「无」；每条项目必须带 ⚪（core/05 §5 规则 3：只能用四种原因）
  4 第三栏非「无」时，全文不得出现「全部通过 / 全绿 / all pass」
  5 三态计数行「⚪ c」若存在，c 必须等于第三栏条数
  6 finding 去处「坐实 N = 修 a / 记账 b / 不做 c」若存在，N 必须等于 a+b+c

登记：checks.md「lint_pr_body」（WARN 试用）
"""
from __future__ import annotations

import re
import sys

TIER = re.compile(r"档位\s*[:：]\s*[SML]\b")
H1, H2, H3 = "### 改了什么", "### 验证了什么", "### 未验证什么"
FORBIDDEN = re.compile(r"全部通过|全绿|all\s+pass", re.I)
COUNT = re.compile(r"⚪\s*(\d+)")
FINDING = re.compile(r"坐实\s*(\d+)\s*条?\s*=\s*(?:本\s*PR\s*)?修\s*(\d+)\D+?记账\s*(\d+)\D+?(?:明确)?不做\s*(\d+)")


def section(text: str, start: str, ends: list[str]) -> str | None:
    i = text.find(start)
    if i < 0:
        return None
    j = len(text)
    for e in ends:
        k = text.find(e, i + len(start))
        if 0 <= k < j:
            j = k
    return text[i + len(start):j]


def check(text: str) -> list[str]:
    problems: list[str] = []
    if not TIER.search(text):
        problems.append("缺档位行（档位: S/M/L）")
    pos = [text.find(h) for h in (H1, H2, H3)]
    if any(p < 0 for p in pos):
        problems.append("交付单三栏不齐（改了什么 / 验证了什么 / 未验证什么）")
        return problems
    if not (pos[0] < pos[1] < pos[2]):
        problems.append("交付单三栏顺序不对")
    third = section(text, H3, ["\n## ", "\n# "]) or ""
    items = [l for l in third.splitlines() if l.strip().startswith(("-", "*"))]
    is_none = bool(re.search(r"^\s*[（(]?\s*(?:没有就写\s*[:：]\s*)?无\s*[）)]?\s*$", third, re.M)) or any(
        re.fullmatch(r"[-*]\s*无", l.strip()) for l in items)
    if not items and not is_none:
        problems.append("第三栏空白：没有未验证项要显式写「无」")
    real_items = [l for l in items if not re.fullmatch(r"[-*]\s*无", l.strip())]
    unmarked = [l for l in real_items if "⚪" not in l]
    if unmarked:
        problems.append(f"第三栏 {len(unmarked)} 条没标 ⚪（每条 = 一个未验证项 + 原因 a/b/c/d）")
    real_items = [l for l in real_items if "⚪" in l]
    if real_items:
        m = FORBIDDEN.search(text)
        if m:
            problems.append(f"第三栏非「无」但出现总评「{m.group(0)}」")
    cm = COUNT.search(text)
    if cm and int(cm.group(1)) != len(real_items):
        problems.append(f"三态计数 ⚪ {cm.group(1)} ≠ 第三栏条数 {len(real_items)}")
    fm = FINDING.search(text)
    if fm:
        n, a, b, c = map(int, fm.groups())
        if n != a + b + c:
            problems.append(f"finding 去处 {n} ≠ {a}+{b}+{c}")
    return problems


GOOD = """## 节点
- 档位: M（入口）→ M（DoD 对账）｜判据: …
## DoD 三态
- 计数: ✅ 3 / ❌ 0 / ⚪ 1
## 交付单
### 改了什么
- a.py：x
### 验证了什么、怎么验的
- pytest → 12 passed（全集 = 该文件全部用例）
### 未验证什么、为什么
- 冒烟 ⚪：原因 (a) 无 key → 请用户跑
## Review finding 去处
- 坐实 5 条 = 本 PR 修 3 / 记账 1 / 明确不做 1
"""


def self_test() -> None:
    assert check(GOOD) == [], check(GOOD)
    bad = GOOD.replace("- 冒烟 ⚪：原因 (a) 无 key → 请用户跑", "- 冒烟 ⚪：原因 (a) 无 key\n\n全部通过。")
    assert any("总评" in p for p in check(bad)), check(bad)
    bad = GOOD.replace("⚪ 1", "⚪ 0")
    assert any("≠ 第三栏" in p for p in check(bad)), check(bad)
    bad = GOOD.replace("修 3 / 记账 1 / 明确不做 1", "修 3 / 记账 1 / 明确不做 0")
    assert any("finding" in p for p in check(bad)), check(bad)
    bad = GOOD.replace("- 冒烟 ⚪：原因 (a) 无 key → 请用户跑\n", "")
    assert any("空白" in p for p in check(bad)), check(bad)
    bad = GOOD.replace("- 档位: M（入口）→ M（DoD 对账）｜判据: …\n", "")
    assert any("档位" in p for p in check(bad)), check(bad)
    bad = GOOD.replace("- 冒烟 ⚪：原因 (a) 无 key → 请用户跑", "- 冒烟没跑")
    assert any("没标 ⚪" in p for p in check(bad)), check(bad)
    none_ok = GOOD.replace("- 冒烟 ⚪：原因 (a) 无 key → 请用户跑", "无").replace("⚪ 1", "⚪ 0")
    assert check(none_ok) == [], check(none_ok)
    print("self-test: 7 种坏形态各会响、2 种好形态不响 ✓")


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        self_test()
        return 0
    if "--file" in argv:
        text = open(argv[argv.index("--file") + 1], encoding="utf-8").read()
    else:
        text = sys.stdin.read()
    problems = check(text)
    for p in problems:
        print("DELIVERY", p)
    print(f"pr-body: problems={len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows GBK 控制台
    except Exception:
        pass
    sys.exit(main(sys.argv[1:]))
