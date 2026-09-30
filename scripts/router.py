"""路由器 v2（core/01 §2–§4）：由「事实」推档位，输出路由卡。取代 v1 的 tier_check.py。

事实（机器提取）：
  F1 改动清单按桶：src / tests / docs / config / infra / other；另计删除、重命名
  F2 行数按桶
  F3 路径命中：paths.l（命中即 L）/ paths.m（命中即至少 M）
  F4 坑表命中：坑表条目「路径:」字段与改动路径匹配；🔴 active 命中即至少 M，action 进停止条件
  F5 新增依赖：依赖清单文件有改动（DoD 模式再查 diff 里的新增行）
  F6 验证可得性：每个 src 文件按 test_map 找配对测试；找不到即不满足 S
人声明（三个是非题）：H1 新增能力 / H2 外部副作用 / H3 不可逆操作

档位：L = F3.l | F5 | H2 | H3；M = F3.m | 桶超阈值 | 跨顶层目录 | F4 🔴 | F6 缺测试 | H1 | 删除或重命名；否则 S。

三个运行点（同一脚本）：
  入口   python scripts/router.py --planned a.py b.py --h1 no --h2 no --h3 no
  DoD 前 python scripts/router.py --base origin/main --h1 no --h2 no --h3 no [--declared S]
  CI     python scripts/router.py --base origin/<base> --pr-body-file body.md   （H 与声明档位从 PR 描述读）
  离线   python scripts/router.py --numstat-file stat.txt ...
  --json 输出 JSON；--self-test 证明会响。

登记：checks.md「router」（WARN 试用）
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import ROOT, load  # noqa: E402

RANK = {"S": 0, "M": 1, "L": 2}
TIER_LINE = re.compile(r"档位\s*[:：]\s*([SML])\b(?:[^\n]*?(?:→|->)\s*([SML])\b)?")
H_LINE = re.compile(r"H([123])[^:：\n]*[:：]\s*(是|否|yes|no)", re.I)

# 每档必做 / 本档不要求（镜像 core/01 §4 矩阵）
MATRIX = {
    "S": {"必做": ["路由卡（本卡）", "执行 + 自验（受影响测试 + lint）", "刹车 8 问", "DoD：Code Review / Corner Case（受影响测试）/ 彻底跑通", "交付单三栏"],
          "本档不要求": ["pre-flight 5 问", "goal XML", "冒烟", "5 类 evidence", "节点级 retro", "PR（可不开；开则档位声明 + 交付单）", "cold review"]},
    "M": {"必做": ["路由卡（本卡）", "pre-flight 5 问", "goal XML（单 goal 可用本卡代替 scope / verification）", "执行 + 自验", "刹车 8 问", "DoD 四步全", "5 类 evidence + 交付单", "节点级 retro 简版", "完整 PR 模板"],
          "本档不要求": ["用户确认拆解", "pitfall-scout 派遣（本卡已按路径扫过）", "cold review（可选）", "回填清单（无裁决落地时）"]},
    "L": {"必做": ["路由卡（本卡）", "用户确认拆解方案", "pre-flight 5 问 + pitfall-scout", "goal XML + 拆解文件落盘", "执行 + 自验", "刹车 8 问", "DoD 四步全", "5 类 evidence + 交付单 + 回填清单", "节点级 retro 完整（落文件）", "完整 PR + review", "cold review（推荐）"],
          "本档不要求": []},
}


# ---------- 输入 ----------
GIT = ["git", "-c", "core.quotepath=false"]   # 非 ASCII 路径原样输出，不加引号不转义


def _unquote(path: str) -> str:
    """离线 numstat 文件里可能仍是 git 默认的 C 风格引号 + 八进制转义（"docs/\\344\\270\\255.md"），还原成真路径。"""
    path = path.strip()
    if len(path) >= 2 and path[0] == path[-1] == '"':
        inner = path[1:-1]
        try:
            path = inner.encode("latin-1", "backslashreplace").decode("unicode_escape").encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            path = inner
    return path


def _rename_target(path: str) -> tuple[str, bool]:
    """numstat 对重命名输出 `old => new` 或 `pre/{old => new}/suf`；取新路径。返回 (路径, 是否重命名)。"""
    if " => " not in path:
        return path, False
    if "{" in path and "}" in path:
        i, j = path.index("{"), path.index("}")
        new_inner = path[i + 1:j].split(" => ", 1)[1]
        return path[:i] + new_inner + path[j + 1:], True
    return path.split(" => ", 1)[1], True


def parse_numstat(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add, dele = (0 if parts[0] == "-" else int(parts[0])), (0 if parts[1] == "-" else int(parts[1]))
        path, renamed = _rename_target(_unquote(parts[-1]))
        rows.append({"path": path, "add": add, "del": dele, "status": "R" if renamed else "M"})
    return rows


def _git(*args: str) -> str:
    return subprocess.run(GIT + list(args), cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout


def git_rows(base: str) -> list[dict]:
    rng = f"{base}...HEAD"
    rows = parse_numstat(_git("diff", "--numstat", rng))
    st = {}
    for line in _git("diff", "--name-status", rng).splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            st[_unquote(parts[-1])] = parts[0][0]   # 重命名行是 R<score>\told\tnew，键取新路径
    for r in rows:
        r["status"] = st.get(r["path"], r["status"])
    return rows


def git_added_lines(base: str, skip_suffixes: tuple[str, ...] = (".md", ".txt", ".rst")) -> str:
    """diff 里的新增行，供 H 反查。跳过文档类文件：文档里写「DROP TABLE」「git push --force」是在讲规则，不是在做操作。"""
    out = _git("diff", "-U0", f"{base}...HEAD")
    kept, skipping = [], False
    for l in out.splitlines():
        if l.startswith("+++ "):
            skipping = _unquote(l[4:]).endswith(skip_suffixes)
            continue
        if l.startswith("+") and not skipping:
            kept.append(l[1:])
    return "\n".join(kept)


# ---------- 事实 ----------
def bucket_of(path: str, buckets: list[list[str]]) -> str:
    for name, pat in buckets:
        if re.search(pat, path):
            return name
    return "other"


def top_dir(path: str, pairs: list[list[str]]) -> str:
    for a, b in pairs:
        if path.startswith(b):
            path = a + path[len(b):]
    return path.split("/", 1)[0] if "/" in path else "."


def test_for(path: str, test_map: list[list[str]]) -> str | None:
    for pat, repl in test_map:
        if re.search(pat, path):
            return re.sub(pat, repl, path)
    return None


def load_pitfalls(table: Path, field: str) -> list[dict]:
    """坑表里带「路径:」字段的条目。条目 = 以 - 🔴/🟡/🟢 开头的行 + 后续缩进行。"""
    if not table.exists():
        return []
    entries, cur, section = [], None, ""
    for line in table.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("### ") or line.startswith("## "):
            section = "§" + line.lstrip("#").strip()
        m = re.match(r"^- (🔴|🟡|🟢)\s*\[(\w+)\]\s*(.*)", line)
        if m:
            cur = {"severity": m.group(1), "status": m.group(2), "text": m.group(3)[:80], "section": section, "paths": [], "action": ""}
            entries.append(cur)
            continue
        if cur and (line.startswith("  ") or line.startswith("\t")):
            pm = re.search(re.escape(field) + r"\s*(.+)", line)
            if pm:
                cur["paths"] = [p.strip() for p in re.split(r"[,，;；]", pm.group(1)) if p.strip()]
            am = re.search(r"(?:action|动作|规避)\s*[:：]\s*(.+)", line)
            if am and not cur["action"]:
                cur["action"] = am.group(1).strip()[:120]
        elif cur and line.strip() == "":
            continue
        elif cur and not line.startswith(" "):
            cur = None
    return [e for e in entries if e["paths"]]


def facts(rows: list[dict], cfg: dict, pitfalls: list[dict], root: Path | None = None) -> dict:
    t = cfg["tier"]
    buckets: dict[str, dict] = {}
    for r in rows:
        b = bucket_of(r["path"], t["buckets"])
        d = buckets.setdefault(b, {"files": 0, "lines": 0, "paths": []})
        d["files"] += 1
        d["lines"] += r["add"] + r["del"]
        d["paths"].append(r["path"])
    deleted = [r["path"] for r in rows if r["status"] == "D"]
    renamed = [r["path"] for r in rows if r["status"] == "R"]
    dirs = sorted({top_dir(r["path"], t.get("same_dir_pairs", [])) for r in rows})
    lp = [re.compile(p) for p in cfg["paths"]["l"]]
    mp = [re.compile(p) for p in cfg["paths"]["m"]]
    l_hits = sorted({r["path"] for r in rows if any(p.search(r["path"]) for p in lp)})
    m_hits = sorted({r["path"] for r in rows if any(p.search(r["path"]) for p in mp)})
    dep = [re.compile(p) for p in t.get("dependency_files", [])]
    dep_hits = sorted({r["path"] for r in rows if any(p.search(r["path"]) for p in dep)})
    pit_hits = []
    for e in pitfalls:
        for pp in e["paths"]:
            if any(re.search(pp, r["path"]) for r in rows):
                pit_hits.append(e)
                break
    missing_tests = []
    deleted_set = set(deleted)
    for p in buckets.get("src", {}).get("paths", []):
        if p in deleted_set:
            continue   # 删掉的文件不需要测试
        tf = test_for(p, t.get("test_map", []))
        if tf is None or (root is not None and not (root / tf).exists()):
            missing_tests.append((p, tf))
    return {"buckets": buckets, "deleted": deleted, "renamed": renamed, "dirs": dirs,
            "l_hits": l_hits, "m_hits": m_hits, "dep_hits": dep_hits, "pitfalls": pit_hits, "missing_tests": missing_tests}


# ---------- 档位 ----------
def decide(f: dict, h: dict, cfg: dict) -> tuple[str, list[str]]:
    lim = cfg["tier"]["s_limits"]
    L, M = [], []
    if f["l_hits"]:
        L.append(f"L 档路径命中 {f['l_hits']}")
    if f["dep_hits"]:
        L.append(f"依赖清单改动 {f['dep_hits']}")
    if h.get("h2"):
        L.append("H2 外部副作用 = 是")
    if h.get("h3"):
        L.append("H3 不可逆操作 = 是")
    if f["m_hits"]:
        M.append(f"M 档路径命中 {f['m_hits']}")
    for b, d in f["buckets"].items():
        mf, ml = lim.get(b, lim.get("other", [3, 100]))
        if mf is not None and d["files"] > mf:
            M.append(f"{b} 桶 {d['files']} 文件 > {mf}")
        if ml is not None and d["lines"] > ml:
            M.append(f"{b} 桶 {d['lines']} 行 > {ml}")
    if len(f["dirs"]) > 1:
        M.append(f"跨顶层目录 {f['dirs']}")
    red = [e for e in f["pitfalls"] if e["severity"] == "🔴" and e["status"] == "active"]
    if red:
        M.append("坑表 🔴 active 命中 " + ", ".join(e["section"] for e in red))
    if f["missing_tests"]:
        M.append("源码文件无配对测试 " + ", ".join(p for p, _ in f["missing_tests"]))
    if h.get("h1"):
        M.append("H1 新增能力 = 是")
    if f["deleted"] or f["renamed"]:
        M.append(f"删除 {len(f['deleted'])} / 重命名 {len(f['renamed'])}")
    if L:
        return "L", L + M
    if M:
        return "M", M
    return "S", []


def h_evidence(added: str) -> dict:
    """DoD 反查：声明「否」但 diff 里有迹象 → 提示。只抓明显形态。"""
    return {
        "h1": bool(re.search(r"add_argument\(|@click\.(option|command)|@app\.(get|post|put|delete)|def \w*(api|endpoint)\w*\(", added)),
        "h2": bool(re.search(r"^\s*(import|from)\s+(requests|httpx|urllib|aiohttp|smtplib|boto3|stripe)\b|https?://", added, re.M)),
        "h3": bool(re.search(r"os\.remove|shutil\.rmtree|unlink\(|DROP\s+TABLE|TRUNCATE|DELETE\s+FROM|git\s+push\s+--force", added, re.I)),
    }


# ---------- 输出 ----------
def route(rows, h, cfg, pitfalls, root=None, added: str | None = None) -> dict:
    f = facts(rows, cfg, pitfalls, root)
    tier, reasons = decide(f, h, cfg)
    warn = []
    if added is not None:
        ev = h_evidence(added)
        for k, lab in (("h1", "H1 新增能力"), ("h2", "H2 外部副作用"), ("h3", "H3 不可逆操作")):
            if ev[k] and not h.get(k):
                warn.append(f"{lab} 声明「否」，但 diff 有迹象 → 请复核")
    tests = sorted({tf for p, tf in ((p, test_for(p, cfg["tier"].get("test_map", []))) for p in f["buckets"].get("src", {}).get("paths", [])) if tf})
    stops = [f"{e['section']} {e['text']}" + (f" → {e['action']}" if e["action"] else "") for e in f["pitfalls"]]
    summary = "；".join(f"{b} {d['files']} 文件 / {d['lines']} 行" for b, d in sorted(f["buckets"].items()))
    return {"tier": tier, "reasons": reasons, "facts_summary": summary, "h": h, "warnings": warn,
            "required": MATRIX[tier]["必做"], "not_required": MATRIX[tier]["本档不要求"],
            "verify": tests, "stop_conditions": stops, "needs_user_confirmation": tier == "L",
            "facts": {k: v for k, v in f.items() if k != "pitfalls"}, "pitfall_hits": f["pitfalls"]}


def card(r: dict) -> str:
    yn = lambda k: "是" if r["h"].get(k) else "否"
    lines = [
        f"档位: {r['tier']} ｜ 事实: {r['facts_summary'] or '无改动'}" + (f"；{'；'.join(r['reasons'])}" if r["reasons"] else "；S 判据全满足"),
        f"H1 新增能力: {yn('h1')}  H2 外部副作用: {yn('h2')}  H3 不可逆: {yn('h3')}",
        "必做: " + " / ".join(r["required"]),
        "本档不要求: " + (" / ".join(r["not_required"]) or "无"),
        "验证命令: " + (" ".join(["pytest"] + r["verify"]) if r["verify"] else "（无源码改动或无配对测试；按 verify.lint）"),
        "停止条件（来自坑表）: " + ("；".join(r["stop_conditions"]) or "无命中"),
        f"需用户确认: {'是' if r['needs_user_confirmation'] else '否'}",
    ]
    lines += [f"⚠ {w}" for w in r["warnings"]]
    return "\n".join(lines)


def declared_from_body(text: str) -> str | None:
    m = TIER_LINE.search(text)
    return (m.group(2) or m.group(1)) if m else None


def h_from_body(text: str) -> dict:
    """PR 描述里的 H 行。**第一次出现为准**：后文复盘 / 引用里再提到「H2 …: 是」不算声明。"""
    h = {}
    for m in H_LINE.finditer(text):
        k = f"h{m.group(1)}"
        if k not in h:
            h[k] = m.group(2).lower() in ("是", "yes")
    return h


# ---------- self-test ----------
CFG = {
    "tier": {
        "buckets": [["tests", r"(^|/)tests?/|(^|/)test_[^/]+\.py$"], ["docs", r"\.md$|(^|/)docs/"],
                    ["infra", r"^\.github/|(^|/)migrations/|pyproject\.toml$"], ["config", r"(^|/)config/|\.ya?ml$"], ["src", r"\.py$"]],
        "s_limits": {"src": [3, 100], "tests": [5, 300], "docs": [5, None], "config": [0, 0], "infra": [0, 0], "other": [3, 100]},
        "same_dir_pairs": [["src/", "tests/"]],
        "test_map": [[r"^src/[^/]+/([^/]+)\.py$", r"tests/test_\1.py"]],
        "dependency_files": [r"pyproject\.toml$"],
    },
    "paths": {"l": [r"(^|/)schemas?/", r"^\.github/"], "m": [r"(^|/)rout(er|ing)"]},
}
PIT = [{"severity": "🔴", "status": "active", "text": "改路由前确认 fallback 链", "section": "§3.2-12", "paths": [r"router\.py$"], "action": "grill fallback"}]
NO_H = {"h1": False, "h2": False, "h3": False}


def rows_of(*specs):
    out = []
    for s in specs:
        p, a, d = s[0], s[1], s[2]
        out.append({"path": p, "add": a, "del": d, "status": s[3] if len(s) > 3 else "M"})
    return out


def self_test() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "tests").mkdir()
        (root / "tests" / "test_a.py").write_text("", encoding="utf-8")
        R = lambda rows, h=NO_H, pit=(): route(rows, h, CFG, list(pit), root)
        r = R(rows_of(("src/app/a.py", 20, 5), ("tests/test_a.py", 30, 0)))
        assert r["tier"] == "S", r["reasons"]
        assert r["verify"] == ["tests/test_a.py"], r["verify"]
        r = R(rows_of(("src/app/b.py", 5, 0)))
        assert r["tier"] == "M" and "无配对测试" in r["reasons"][0], r["reasons"]
        r = R(rows_of(("docs/a.md", 400, 0), ("docs/b.md", 1, 0), ("README.md", 1, 0)))
        assert r["tier"] == "M" and "跨顶层" in r["reasons"][0], r["reasons"]          # docs 与 . 两个顶层
        r = R(rows_of(("docs/a.md", 400, 0), ("docs/b.md", 1, 0)))
        assert r["tier"] == "S", r["reasons"]                                            # docs 行数不限
        r = R(rows_of(("src/app/a.py", 90, 20)))
        assert r["tier"] == "M" and "行" in r["reasons"][0], r["reasons"]
        r = R(rows_of(("src/app/schemas/x.py", 1, 0)))
        assert r["tier"] == "L" and "L 档路径" in r["reasons"][0], r["reasons"]
        r = R(rows_of(("pyproject.toml", 1, 0)))
        assert r["tier"] == "L" and any("依赖" in x for x in r["reasons"]), r["reasons"]
        r = R(rows_of(("src/app/a.py", 1, 0)), {"h1": False, "h2": True, "h3": False})
        assert r["tier"] == "L" and "H2" in r["reasons"][0], r["reasons"]
        r = R(rows_of(("src/app/a.py", 1, 0)), {"h1": True, "h2": False, "h3": False})
        assert r["tier"] == "M" and "H1" in r["reasons"][0], r["reasons"]
        r = R(rows_of(("src/app/a.py", 1, 0), ("src/app/old.py", 0, 30, "D")))
        assert r["tier"] == "M" and any("删除 1" in x for x in r["reasons"]), r["reasons"]
        r = R(rows_of(("src/app/router.py", 3, 1)), NO_H, PIT)
        assert r["tier"] == "M" and any("坑表" in x for x in r["reasons"]) and "grill fallback" in r["stop_conditions"][0], r
        r = route(rows_of(("src/app/a.py", 1, 0)), NO_H, CFG, [], root, added="import requests\nos.remove(x)")
        assert len(r["warnings"]) == 2 and "H2" in r["warnings"][0] and "H3" in r["warnings"][1], r["warnings"]
        assert declared_from_body("档位: S → M（DoD 对账）") == "M" and declared_from_body("x") is None
        assert h_from_body("H1 新增能力: 是  H2 外部副作用: 否  H3 不可逆: 否") == {"h1": True, "h2": False, "h3": False}
        assert "档位: S" in card(R(rows_of(("src/app/a.py", 1, 0), ("tests/test_a.py", 1, 0))))
    print("self-test: 12 种事实各推对档位（S 2 / M 6 / L 3 + 反查 2 警告）、声明行与 H 行解析、路由卡可渲染 ✓")


# ---------- main ----------
def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        self_test()
        return 0
    cfg = load()
    info = (lambda m: print(m, file=sys.stderr)) if "--json" in argv else print   # --json 时 stdout 只放 JSON

    def arg(k: str) -> str | None:
        if k not in argv:
            return None
        i = argv.index(k) + 1
        if i >= len(argv) or argv[i].startswith("--"):
            raise SystemExit(f"router: {k} 缺值")
        return argv[i]

    body = Path(arg("--pr-body-file")).read_text(encoding="utf-8") if arg("--pr-body-file") else ""
    h = h_from_body(body)
    YES, NO = ("yes", "是", "y", "true"), ("no", "否", "n", "false")
    for k in ("h1", "h2", "h3"):
        v = arg(f"--{k}")
        if v is None:
            continue
        if v.lower() in YES:
            h[k] = True
        elif v.lower() in NO:
            h[k] = False
        else:
            raise SystemExit(f"router: --{k} 只认 yes|no，收到「{v}」（答不准就写 yes，core/01 §5）")
    added = None
    if "--planned" in argv:
        i = argv.index("--planned") + 1
        planned = []
        while i < len(argv) and not argv[i].startswith("--"):
            planned.append(argv[i]); i += 1
        rows = [{"path": p, "add": 0, "del": 0, "status": "M"} for p in planned]
        mode = "入口（预计清单，行数未知按 0 计；DoD 前会重算）"
    elif arg("--numstat-file"):
        rows = parse_numstat(Path(arg("--numstat-file")).read_text(encoding="utf-8"))
        mode = "离线 numstat"
    else:
        base = arg("--base") or "origin/main"
        rows = git_rows(base)
        added = git_added_lines(base)
        mode = f"DoD / CI（diff {base}...HEAD）"
    missing_h = [k for k in ("h1", "h2", "h3") if k not in h]
    if missing_h:
        info(f"router: 缺人声明 {missing_h}（--h1/--h2/--h3 yes|no，或 PR 描述里「H1 新增能力: 是/否」行）→ 按「是」算（core/01 §5 拿不准往高一档），卡上标注")
        for k in missing_h:
            h[k] = True
    pit_cfg = cfg.get("pitfalls", {})
    pitfalls = load_pitfalls(ROOT / pit_cfg.get("table", ""), pit_cfg.get("path_field", "路径:")) if pit_cfg.get("table") else []
    r = route(rows, h, cfg, pitfalls, ROOT, added)
    if missing_h:
        r["warnings"].append(f"人声明 {missing_h} 缺失，按「是」计 —— 补上声明再跑才能降回来")
    if "--json" in argv:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"router: 模式 = {mode}")
        print(card(r))
    declared = (arg("--declared") or "").upper() or declared_from_body(body)
    if not declared:
        if body:
            info("TIER PR 描述里没有「档位: S/M/L」行 = 没跑路由器就交付（core/01 §5）")
            return 1
        info("router: 未给声明档位（--declared 或 --pr-body-file），只算不判")
        return 0
    if RANK.get(declared, -1) < RANK[r["tier"]]:
        info(f"TIER 声明 {declared} 低于路由器算出的 {r['tier']} → 必须升档（core/01 §5）")
        return 1
    info(f"router: 声明 {declared} ≥ 算出 {r['tier']} ✓")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main(sys.argv[1:]))
