"""档位对账（core/01 §5「DoD 前按实际 diff 对账、超出自动升档」的程序版；也是路由器的第一版）。

按 diff 算「最低档位」：
  S 判据 1 文件数 ≤ tier.s_max_files 且同一顶层目录
  S 判据 2 增删合计 ≤ tier.s_max_lines
  S 判据 3 不碰 sensitive_paths
  判据 4（不新增能力）、5（有现成验证）机器判不了 → 只提示，人核
命中敏感路径 → 至少 M，并提示按风险五条判是否 L（机器判不了）。

用法：
  python scripts/tier_check.py --base origin/main              # 只算，打印结果
  python scripts/tier_check.py --base origin/main --declared S # 声明档位低于算出的 → exit 1
  python scripts/tier_check.py --pr-body-file body.md          # 从「档位: X」行取声明
  python scripts/tier_check.py --numstat-file stat.txt         # 用保存的 git diff --numstat 输出（测试 / 离线）
  python scripts/tier_check.py --self-test

登记：checks.md「tier_check」（WARN 试用）
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import ROOT, load  # noqa: E402

RANK = {"S": 0, "M": 1, "L": 2}
TIER_LINE = re.compile(r"档位\s*[:：]\s*([SML])\b(?:[^\n]*?(?:→|->)\s*([SML])\b)?")


def parse_numstat(text: str) -> list[tuple[str, int, int]]:
    rows = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add, dele, path = parts
        add = 0 if add == "-" else int(add)  # 二进制文件
        dele = 0 if dele == "-" else int(dele)
        rows.append((path.strip(), add, dele))
    return rows


def top_dir(path: str, pairs: list[list[str]]) -> str:
    """取顶层目录；配对目录（如 src/ 与 tests/）视为同一处。"""
    for a, b in pairs:
        if path.startswith(b):
            path = a + path[len(b):]
    return path.split("/", 1)[0] if "/" in path else "."


def evaluate(rows: list[tuple[str, int, int]], cfg: dict) -> dict:
    t = cfg["tier"]
    sens = [re.compile(p) for p in cfg.get("sensitive_paths", [])]
    files = len(rows)
    lines = sum(a + d for _, a, d in rows)
    dirs = {top_dir(p, t.get("same_dir_pairs", [])) for p, _, _ in rows}
    hits = sorted({p for p, _, _ in rows if any(s.search(p) for s in sens)})
    reasons = []
    if hits:
        reasons.append(f"碰敏感路径 {hits}")
    if files > t["s_max_files"]:
        reasons.append(f"文件数 {files} > {t['s_max_files']}")
    if len(dirs) > 1:
        reasons.append(f"跨顶层目录 {sorted(dirs)}")
    if lines > t["s_max_lines"]:
        reasons.append(f"增删 {lines} 行 > {t['s_max_lines']}")
    min_tier = "M" if reasons else "S"
    return {
        "files": files, "lines": lines, "dirs": sorted(dirs), "sensitive_hits": hits,
        "min_tier": min_tier, "reasons": reasons,
        "human_checks": (["判据 4 不新增能力 / 依赖 / 配置项", "判据 5 有现成验证命令"] if min_tier == "S" else [])
                        + (["碰了敏感路径：按风险五条判是否 L"] if hits else []),
    }


def git_numstat(base: str) -> str:
    return subprocess.run(["git", "diff", "--numstat", f"{base}...HEAD"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout


def declared_from_body(text: str) -> str | None:
    m = TIER_LINE.search(text)
    if not m:
        return None
    return m.group(2) or m.group(1)  # 有「→ 升档」取升档后的


def self_test() -> None:
    cfg = {"tier": {"s_max_files": 3, "s_max_lines": 100, "same_dir_pairs": [["src/", "tests/"]]},
           "sensitive_paths": [r"(^|/)schemas?/", r"\.env", r"^\.github/"]}
    small = "5\t3\tsrc/app/a.py\n10\t0\ttests/test_a.py\n"
    r = evaluate(parse_numstat(small), cfg)
    assert r["min_tier"] == "S" and r["dirs"] == ["src"], r
    r = evaluate(parse_numstat(small + "1\t0\tsrc/app/schemas/x.py\n"), cfg)
    assert r["min_tier"] == "M" and "敏感" in r["reasons"][0], r
    r = evaluate(parse_numstat("90\t20\tsrc/app/a.py\n"), cfg)
    assert r["min_tier"] == "M" and "行" in r["reasons"][0], r
    r = evaluate(parse_numstat("1\t0\tsrc/a.py\n1\t0\tdocs/b.md\n"), cfg)
    assert r["min_tier"] == "M" and "跨顶层" in r["reasons"][0], r
    r = evaluate(parse_numstat("1\t0\ta\n1\t0\tb\n1\t0\tc\n1\t0\td\n"), cfg)
    assert r["min_tier"] == "M" and "文件数" in r["reasons"][0], r
    assert declared_from_body("档位: S ｜ 判据: …") == "S"
    assert declared_from_body("档位: S → M（DoD 对账）") == "M"
    assert declared_from_body("没有档位行") is None
    print("self-test: 小改动算 S；敏感路径 / 超行 / 跨目录 / 超文件各升 M；声明行解析含升档 ✓")


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        self_test()
        return 0
    cfg = load()
    if "--numstat-file" in argv:
        stat = Path(argv[argv.index("--numstat-file") + 1]).read_text(encoding="utf-8")
    else:
        base = argv[argv.index("--base") + 1] if "--base" in argv else "origin/main"
        stat = git_numstat(base)
    r = evaluate(parse_numstat(stat), cfg)
    declared = None
    if "--declared" in argv:
        declared = argv[argv.index("--declared") + 1].upper()
    elif "--pr-body-file" in argv:
        declared = declared_from_body(Path(argv[argv.index("--pr-body-file") + 1]).read_text(encoding="utf-8"))
    print(f"tier-check: files={r['files']} lines={r['lines']} dirs={r['dirs']} sensitive={r['sensitive_hits']}")
    print(f"tier-check: 最低档位 = {r['min_tier']}" + (f"（{'；'.join(r['reasons'])}）" if r["reasons"] else ""))
    for h in r["human_checks"]:
        print(f"tier-check: 人核 → {h}")
    if declared is None:
        print("tier-check: 未给声明档位（--declared 或 --pr-body-file），只算不判")
        return 0
    print(f"tier-check: 声明档位 = {declared}")
    if RANK.get(declared, -1) < RANK[r["min_tier"]]:
        print(f"TIER 声明 {declared} 低于按 diff 算出的最低档 {r['min_tier']} → 必须升档（core/01 §5）")
        return 1
    print("tier-check: 声明档位 ≥ 最低档位 ✓")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows GBK 控制台
    except Exception:
        pass
    sys.exit(main(sys.argv[1:]))
