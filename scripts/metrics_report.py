"""流程划算度报告（评审建议 6 的代理指标版）：读 metrics.md 两张台账，报退役候选与趋势。

不做前后对照（任务不可复现、agent 输出高方差，流程指标会被噪声淹没）。只做两件便宜的事：
  1 规则命中台账：每条规则「上次拦到东西」距今天数；≥ metrics.retire_after_days 或从未命中 → 退役候选
  2 PR 台账：S 档被自动升档的次数、⚪ 数、返工次数，按月看趋势，不做 A/B

用法：
  python scripts/metrics_report.py                # 打印报告（markdown）
  python scripts/metrics_report.py --today 2026-12-31
  python scripts/metrics_report.py --self-test

登记：checks.md「metrics_report」（只报不拦）
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import ROOT, load  # noqa: E402

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def tables(text: str) -> dict[str, list[list[str]]]:
    """按 '## ' 标题切段，每段取第一张 markdown 表（去掉表头与分隔行）。"""
    out: dict[str, list[list[str]]] = {}
    cur = None
    rows: list[list[str]] = []
    seen_header = False
    for line in text.splitlines():
        if line.startswith("## "):
            if cur:
                out[cur] = rows
            cur, rows, seen_header = line[3:].strip(), [], False
            continue
        if cur and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not seen_header:
                seen_header = True
                continue
            if set("".join(cells)) <= set("-: "):
                continue
            rows.append(cells)
    if cur:
        out[cur] = rows
    return out


def report(text: str, today: date, retire_after: int) -> str:
    t = tables(text)
    lines = [f"# 流程划算度报告 · {today.isoformat()}", ""]
    rules = t.get("1. 规则命中台账", [])
    retire, active, watching = [], [], []
    for r in rules:
        if len(r) < 4:
            continue
        name, last, hits = r[0], r[2], r[3]
        m = DATE.search(last)
        if m and "未记录" not in last:
            days = (today - date.fromisoformat(m.group(0))).days
            (retire if days >= retire_after else active).append((name, f"{days} 天前", hits))
            continue
        # 从未命中：按立账日算，立账不满 retire_after 天的只标「观察中」，不进候选
        opened = DATE.search(" ".join(r))
        if opened and (today - date.fromisoformat(opened.group(0))).days < retire_after:
            watching.append((name, f"立账 {opened.group(0)}", hits))
        else:
            retire.append((name, "从未命中" + ("" if opened else "·立账日未知"), hits))
    lines += [f"## 规则命中：{len(active)} 条近期命中 / {len(watching)} 条新立账观察中 / {len(retire)} 条退役候选（≥ {retire_after} 天零命中）", ""]
    for name, when, hits in retire:
        lines.append(f"- 退役候选：{name}（上次 {when}，累计 {hits}）")
    if not retire:
        lines.append("- 无退役候选")
    lines.append("")
    prs = t.get("2. PR 台账", [])
    by_month: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    up = 0
    for r in prs:
        if len(r) < 5:
            continue
        m = DATE.search(r[0])
        month = m.group(0)[:7] if m else "?"
        tier = r[2]
        if re.search(r"S\s*(→|->)\s*[ML]", tier):
            up += 1
            by_month[month]["S升档"] += 1
        by_month[month]["PR"] += 1
        by_month[month]["返工"] += int(re.search(r"\d+", r[3]).group(0)) if re.search(r"\d+", r[3]) else 0
        by_month[month]["⚪"] += int(re.search(r"\d+", r[4]).group(0)) if re.search(r"\d+", r[4]) else 0
    lines += [f"## PR 台账：{len(prs)} 条；S 档被自动升档 {up} 次（调 tier.s_max_* 的依据）", "",
              "| 月 | PR 数 | 返工合计 | ⚪ 合计 | S 升档 |", "|---|---|---|---|---|"]
    for month in sorted(by_month):
        d = by_month[month]
        lines.append(f"| {month} | {d['PR']} | {d['返工']} | {d['⚪']} | {d['S升档']} |")
    lines.append("")
    lines.append("看趋势，不做 A/B。退役候选在里程碑交接（core/07 §2）审视，退役走 core/08 §2 协议，不物理删。")
    return "\n".join(lines)


SAMPLE = """# m
## 1. 规则命中台账
| 规则 | 出处 | 上次命中 | 命中次数 | 守护 |
|---|---|---|---|---|
| 新规则 | core/05 | 2026-09-20 | 1 | 无 |
| 老规则 | core/04 | 2026-01-01 | 3 | 无 |
| 空规则 | core/08 | 未记录 | 0 | 无 |
| 新立账 | core/02 | 未记录（2026-09-01 立账） | 0 | 无 |
## 2. PR 台账
| 日期 | PR | 档位 | 返工 | ⚪ | token | 备注 |
|---|---|---|---|---|---|---|
| 2026-09-29 | c1 | S → M | 0 | 1 | 未记 | |
| 2026-09-29 | c2 | L | 2 | 0 | 未记 | |
"""


def self_test() -> None:
    out = report(SAMPLE, date(2026, 9, 29), 90)
    assert "退役候选：老规则" in out and "退役候选：空规则" in out and "退役候选：新规则" not in out, out
    assert "退役候选：新立账" not in out and "1 条新立账观察中" in out, out
    assert "S 档被自动升档 1 次" in out, out
    assert "| 2026-09 | 2 | 2 | 1 | 1 |" in out, out
    print("self-test: 零命中进退役候选、新立账只观察、近期命中不进、升档与月度合计对得上 ✓")


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        self_test()
        return 0
    cfg = load()
    today = date.fromisoformat(argv[argv.index("--today") + 1]) if "--today" in argv else date.today()
    ledger = ROOT / cfg.get("metrics", {}).get("ledger", "metrics.md")
    print(report(ledger.read_text(encoding="utf-8"), today, int(cfg.get("metrics", {}).get("retire_after_days", 90))))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows GBK 控制台
    except Exception:
        pass
    sys.exit(main(sys.argv[1:]))
