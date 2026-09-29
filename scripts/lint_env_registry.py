#!/usr/bin/env python3
"""配置键名册对账 —— 代码读的 env 键 ↔ 模板写的 env 键，两边对得上吗（backlog BJ · BJ.1）。

**这个脚本治的病**：没有一份「合法 env 键」清单。2026-06-16 拿 ``config.py`` 的 Python
符号名当 env 名去查，查空、误判"没配置"——没有任何东西说「这个名字不存在」。
BJ.0 盘点又查出：代码读 105 个键，两份模板合起来只写了 64 个（核心数据源的钥匙都没写），
模板里还躺着 2 个代码根本不读的死键。

名册**不手写**，由 [src/committee/config_registry.py](../src/committee/config_registry.py)
从源码 AST 派生（8 种读取形态，见其 docstring）；本脚本只做对账 + 报告。

**三类 finding**（WARN 试用期：默认只报不拦；升硬拦须按 e2e 验收标准 §4 走用户裁决）：

- ``[枚举盲区]``   代码里有一处读 env，但键判不出来（调用点传的不是字面量 / f-string 嵌了认不出的
                   表达式）。这不是"没问题"，是**这个键从名册里消失了而检查照样绿** —— 必须修到能判。
- ``[模板死键]``   模板里写了某键，代码从不读它（拼错 / 已删）。模板是所有人 .env 的来源：
                   照着抄一个死键，配置写了却永远不生效、还没人知道。
- ``[缺模板]``     代码读了某键，两份模板都没写。新环境照模板配不出它；只能靠读代码才知道能配。

**结构性失败一律 exit 2、绝不静默放行**：扫到 0 个文件 / 0 处读取、模板读不到 —— 解析不到东西的
检查器外观与「全绿」一模一样（坑表 §3.2「扫到 0 = 守护在空转」）。**每次输出固定打印**
「枚举到 N 个文件 / M 处读取 / K 个键」，让人看得见它到底看了多少。

用法::

    python scripts/lint_env_registry.py             # 对账（WARN 试用：有 finding 也 exit 0）
    python scripts/lint_env_registry.py --strict    # 有 finding 则 exit 1
    python scripts/lint_env_registry.py --dump      # 打印整份名册（键 / 读取处 / 形态 / 默认值 / 是否密钥）
    python scripts/lint_env_registry.py --json      # 机器可读

退出码：0 跑通 · 1 有 finding 且 --strict · 2 结构性失败。
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
REGISTRY_MODULE = SRC_ROOT / "committee" / "config_registry.py"
TEMPLATES = {".env.example": REPO_ROOT / ".env.example", ".env.prod.example": REPO_ROOT / ".env.prod.example"}


def load_registry_module():
    """按文件路径加载名册模块 —— 不 import 本包，CI 上不装依赖也能跑（它是纯标准库）。"""
    spec = importlib.util.spec_from_file_location("committee_config_registry", REGISTRY_MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"加载不了 {REGISTRY_MODULE}")
    mod = importlib.util.module_from_spec(spec)
    # 先登记再执行：模块里的 dataclass 在解析 `from __future__ import annotations` 的类型注解时
    # 会按 __module__ 回查 sys.modules，不登记就是 None → AttributeError。
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def run(cr, src_root: pathlib.Path, templates: dict[str, str]) -> tuple[list[str], list[str], object, object]:
    """纯核心：返回 (结构性失败, findings, registry, reconciliation)。"""
    struct: list[str] = []
    findings: list[str] = []
    registry = cr.enumerate_reads(src_root)
    if registry.files_scanned == 0:
        struct.append(f"STRUCT 在 {src_root} 下扫到 0 个文件 —— 路径错了或包不在")
    if not registry.reads:
        struct.append("STRUCT 枚举到 0 处 env 读取 —— 识别器在空转，不许以「零 finding」的面目通过")
    if not templates:
        struct.append("STRUCT 一份模板都没读到")
    if struct:
        return struct, findings, registry, None
    rec = cr.reconcile(registry, templates)
    for r in rec.unresolved:
        findings.append(f"[枚举盲区] {r.file}:{r.line} 读 env 但键判不出（{r.form}·{r.key}）—— 改成字面量或让派生器认得这种写法")
    for key, sites in sorted(rec.dead.items()):
        where = ", ".join(f"{lbl}:{ln}" for lbl, ln in sites)
        findings.append(f"[模板死键] {key} 写在 {where}，但 src/ 无任何读取 —— 拼错了还是已删？删掉或接上")
    if rec.undocumented:
        findings.append(
            f"[缺模板] 代码读了 {len(rec.undocumented)} 个键、两份模板都没写（含密钥类 "
            f"{sum(1 for k in rec.undocumented if cr.is_secret(k))} 个）: " + ", ".join(rec.undocumented)
        )
    return struct, findings, registry, rec


def dump(cr, registry) -> list[str]:
    lines = [f"{'键':<52} {'密钥':<4} {'形态':<22} {'来源':<9} 默认值 / 位置"]
    for key, reads in sorted(registry.keys.items()):
        for r in reads:
            lines.append(f"{key:<52} {'是' if cr.is_secret(key) else '':<4} {r.form:<22} {r.how:<9} {r.default or '-'}  @ {r.file}:{r.line}")
    for r in registry.unresolved:
        lines.append(f"{'?? ' + r.key:<52} {'':<4} {r.form:<22} {r.how:<9} {r.default or '-'}  @ {r.file}:{r.line}  ← 判不出")
    return lines


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover
        pass
    strict = "--strict" in args
    try:
        cr = load_registry_module()
        templates = {}
        for label, path in TEMPLATES.items():
            if path.exists():
                templates[label] = path.read_text(encoding="utf-8")
        struct, findings, registry, rec = run(cr, SRC_ROOT, templates)
    except RuntimeError as exc:
        print(f"lint_env_registry: STRUCT {exc}")
        return 2

    n_keys = len(registry.keys) if registry else 0
    n_helpers = len(registry.helpers) if registry else 0
    print(
        f"lint_env_registry: 枚举到 {registry.files_scanned} 个文件 / {len(registry.reads)} 处读取 / "
        f"{n_keys} 个键（经 {n_helpers} 个助手函数展开）· 模板 {', '.join(templates) or '无'}"
    )
    if struct:
        for s in struct:
            print("  " + s)
        return 2

    if "--json" in args:
        print(json.dumps({
            "files_scanned": registry.files_scanned,
            "reads": [r.__dict__ for r in registry.reads],
            "keys": sorted(registry.keys),
            "dead": rec.dead, "undocumented": rec.undocumented,
            "unresolved": [r.__dict__ for r in rec.unresolved],
        }, ensure_ascii=False, indent=1))
        return 0
    if "--dump" in args:
        for line in dump(cr, registry):
            print(line)

    for f in findings:
        print("  " + f)
    if findings:
        print(f"lint_env_registry: {len(findings)} 条 finding" + ("" if strict else "（WARN 试用期，不拦路）"))
        return 1 if strict else 0
    print("lint_env_registry: 干净")
    return 0


if __name__ == "__main__":
    sys.exit(main())
