#!/usr/bin/env python
"""检查 `.env` / `.env.example` 有没有**静默架空**「测代码默认值」的断言。

## 这个脚本在防什么（backlog BG）

`config.py` 等模块在 import 时 `load_dotenv()`。所以一旦 `.env` 里某个键的值
**恰好等于代码里的默认值**，那些写着 `assert SYMBOL == <默认值>` 的测试就从
「验代码默认值」悄悄变成「验本机配置」—— **测试照常绿，但已经什么都没验**。

危险的是这个失守**没有声音**：

- `.env` 值 **不等于** 代码默认值 → 断言当场变红。吵，但看得见。
- `.env` 值 **等于** 代码默认值 → 断言恒绿、恒真。**看不见。**

CI 里没有 `.env`（已 gitignore），所以代码默认值在 CI 仍有人守；丢的是**本地
验证的可信度** —— 而「mutation 证承重」按 DoD 是在本地做的。2026-08-03 的
[#223](https://github.com/JunoChenZt/subagent-for-investment/pull/223) review
差点据此把一条好断言判成不承重。

## 两条规则

1. **生效即报错**：某键在 `.env.example` 或本机 `.env` 里**实际生效**、值等于代码
   默认值、且有测试断言该默认值 → 报错。已知且可接受的写进 `ALLOW` 声明理由。
2. **进模板就要留警示**：某键出现在 `.env.example`（**注释态也算**）、且有测试断言
   它的默认值 → **每一处**出现的附近都必须带警示注记 `MARKER`。注释态不报错
   （没生效），但下一个来取消注释的人必须**当场看见**这行是雷。

另有两条防锈：
- `ALLOW` 里的条目若已不再是真实雷（键删了 / 值改了 / 断言没了）→ 报错。
  豁免表一旦变成坟场，检查就成了摆设。
- 同一个符号名在 `src/` 下被定义多次 → 报错。**宁可吵，不可静默**：静默取其一
  会让断言被拿去和错误的配置项比对（见下「为什么规则 1 不自己解析」同款教训）。

## 为什么规则 1 不自己写解析器（2026-08-13 review 修复）

初版手写正则去**猜** `.env` 的加载语义，结果与 python-dotenv 实际行为差了四条，
每条都是**静默漏报**（检查器报干净、雷还在）—— 恰恰是本脚本要治的那个病：

- 同键写两次时，靠后的注释行覆盖了靠前的生效行 → 生效的雷被记成"没生效"；
- 值带引号（`="12288"`）不脱引号 → 比不相等，**加个引号就能绕过检查**；
- 不认 `export KEY=value` → 整行解析不出来，两条规则同时失灵；
- 不展开 `${VAR}` 引用 → 展开后恰好等于默认值的情形看不见。

现在**规则 1 的取值一律经 `dotenv.dotenv_values`**，与运行时同源：重复键、引号、
`export`、变量展开的语义按构造对齐，将来库升级也自动跟上，不用逐条追平。

**规则 2 仍用自家正则**，因为它问的是「这个键在模板里**出现过没有、在第几行**」——
`dotenv_values` 只吐生效值，既不报注释行也不报行号，答不了这个问题。语义要求低一
档，正则够用；但同样要认引号与 `export`，且**同键多次出现要全部记录、不能互相覆盖**。

## 覆盖边界（**声明出来，不靠"没报错"推断**）

- 只认**模块级**赋值里直接读 env 的形态：`X = _clamp_int("COMMITTEE_...", 默认, ...)`
  / `_clamp_float` / `os.getenv` / `os.environ.get`，允许外面再包一层（如
  `int(_clamp_float(...))`）。函数内的局部变量不算（测试断的是模块级常量）。
- 默认值必须是**字面量**才比对得了。写成具名常量（`_clamp_int("COMMITTEE_X",
  _DEFAULT_X, ...)`）时本检查判不出默认值 —— 这时**不静默跳过**：只要有测试在断
  它的字面量值，就报 `[判不了默认值]`（见 :func:`find_blind_spots`）。没人断它 =
  无害，保持安静。
- **不追派生链**：若测试断言的符号是从另一个 env 符号**推导**出来的
  （env → 原始串 → 派生值），本检查连不上，**不覆盖**。
- 断言必须是 `assert <符号> == <字面量>` 且**字面量等于代码默认值**。断言别的值
  （如 `test_external_search_url_override` 里断言 override 生效）不算被架空。
- 值比较：先按字符串比，再尝试按数字比（`2` 与 `2.0` 算相等 —— `REFRESH_HOUR`
  就是这个形态，纯字符串比会漏）。
"""
from __future__ import annotations

import ast
import importlib.util
import sys
import io
import pathlib
import re
import sys

try:
    from dotenv import dotenv_values
except ImportError as exc:  # pragma: no cover - 让它吵，绝不静默降级成自家正则
    raise SystemExit(
        "lint_env_shadowing 需要 python-dotenv（规则 1 的取值必须与运行时同源）。\n"
        "  本地：它本就是项目依赖，用项目环境跑即可。\n"
        "  CI：该 job 需要 `pip install python-dotenv` 一步。\n"
        "  ⚠️ 不提供「退回自家正则」的兜底 —— 那等于让检查器在无人知晓的情况下缩小覆盖面，\n"
        "     正是本脚本要治的病。\n"
        f"  原始错误：{exc}"
    ) from exc

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
TESTS = ROOT / "tests"
ENV_EXAMPLE = ROOT / ".env.example"
ENV_LOCAL = ROOT / ".env"

#: `.env.example` 里给"有测试在断其默认值"的键留的警示注记（规则 2）。
MARKER = "有测试在断这个默认值"

#: 警示注记允许出现的位置：本行，或本行往上数 N 行（迁就模板里的块注释风格）。
MARKER_LOOKBEHIND = 3

#: 「什么算读 env」只认一份：src/committee/config_registry.py（backlog BJ.1）。按文件路径加载、
#: 不 import 本包 —— CI 的 env-shadowing-lint job 只装 python-dotenv，装不起整个包。
def _load_registry():
    path = SRC / "committee" / "config_registry.py"
    spec = importlib.util.spec_from_file_location("committee_config_registry", path)
    if spec is None or spec.loader is None:  # pragma: no cover - 让它吵
        raise RuntimeError(f"加载不了 {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_registry = _load_registry()

#: 拿形参当键读 env 的助手（config.py）。原始读取（getenv / environ.get）由 registry.primitive_read 判。
#: `_env_bool`（BJ.5 (c)·2026-09-14）：不加它，11 个开关会从本检查的覆盖面里静默消失（首轮实测 39 → 31 个符号）。
_HELPERS = {"_clamp_int", "_clamp_float", "_env_bool"}

#: 规则 1 的已知豁免：符号 → 理由。**加条目必须写清为什么可接受。**
ALLOW: dict[str, str] = {
    "MIN_CHARS_DEBATE": (
        "非新洞·已有明文分工：tests/test_checklist_structural_invariants.py 的 docstring "
        "写明「CI 守代码默认值 / 本地被 .env 罩住」两条路，并在断言失败信息里列了三种来源的排查顺序。"
        "该断言钉的是**生效值**（guide ⑥ 段数字线的前提），不是 config.py 的字面默认值。"
    ),
    "MAX_CONTINUATIONS": (
        "与 MIN_CHARS_DEBATE **同一形态、同一理由**（2026-08-14 加）：断言在 "
        "tests/test_checklist_structural_invariants.py，docstring 同样写明「CI 守代码默认值 / "
        "本地被 .env 罩住」两条路 + 失败信息列了三种来源的排查顺序。钉的是**生效值** —— "
        "因为 guide ⑥ 段那条排查线「有没有轮次打满续写上限」的**刻度就是这个数**，"
        "跑 e2e 的机器上生效值是几，'打满'就是几次；钉代码默认值反而验不到真正要用的那个。"
        "⚠️ 该豁免**只覆盖数值断言**：同文件另有一条 test_continuation_loop_bound_matches_constant "
        "是**行为断言**（真数 invoke 次数），不依赖常量取值、不受本豁免影响。"
    ),
}


def _display(path: pathlib.Path) -> str:
    """仓库内的路径显示成相对路径；仓库外（测试的 tmp_path）原样显示，不崩。"""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _norm(v: object) -> str:
    return str(v).strip()


def values_equal(a: object, b: object) -> bool:
    """先按字符串比，再退一步按数字比（`2` == `2.0`）。"""
    if _norm(a) == _norm(b):
        return True
    try:
        return float(_norm(a)) == float(_norm(b))
    except (TypeError, ValueError):
        return False


# ---- 取值：一律走 python-dotenv，与运行时同源 --------------------------------


def effective_values(text: str) -> dict[str, str | None]:
    """这份 env 文件加载后**实际生效**的键值（规则 1 与防锈的唯一取值口径）。

    交给 `dotenv_values` 而不是自己解析 —— 重复键取最后一条生效的、引号剥离、
    `export` 前缀、`${VAR}` 展开，全部按运行时的语义来。
    """
    return dict(dotenv_values(stream=io.StringIO(text)))


# ---- 出现位置：自家正则，只回答「出现过没有、在第几行」----------------------

#: ⚠️ 行首空白必须在 `hash` 组**外面**。写成 `(?P<hash>\s*#\s*)?` 时，只有带 `#`
#: 的分支吃得掉行首缩进，`  KEY=v` 这种**缩进的生效行**整行匹配不上 → 规则 2 一声
#: 不吭（而 dotenv 认它生效）。这是 2026-08-13 那四个 finding 的同一形态第五处。
_ENV_LINE = re.compile(
    r"^\s*(?P<hash>#\s*)?(?:export\s+)?(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$"
)


def _quote_still_open(value: str) -> str | None:
    """这个值是不是一段**没闭合的**引号（即多行值的第一行）？返回待闭合的引号字符。"""
    quote = value[:1]
    if quote not in {'"', "'"}:
        return None
    return quote if value.find(quote, 1) == -1 else None


def scan_occurrences(text: str) -> dict[str, list[tuple[bool, str, int]]]:
    """扫出每个键的**全部**出现位置 → [(是否未注释, 原始值文本, 行号)]。

    ⚠️ 同键多次出现必须**全部记录**：初版按 key 覆盖，导致靠后的注释行把靠前的
    生效行盖掉、规则 1 静默漏报（`.env.example` 里本就有 13 个重复键）。
    这里只管「出现过没有」；「到底哪条生效」由 :func:`effective_values` 回答。

    ⚠️ 多行引号值的**内部**要整段跳过：`OTHER="a` / `COMMITTEE_X=7` / `b"` 里那个
    中间行在 dotenv 眼中只是字符串的一部分，逐行扫会把它当成一处键出现 → 规则 2
    误报。误报会逼人往豁免表里塞条目，长期把检查稀释掉，与漏报殊途同归。
    """
    out: dict[str, list[tuple[bool, str, int]]] = {}
    open_quote: str | None = None
    for lineno, line in enumerate(text.splitlines(), 1):
        if open_quote is not None:
            if open_quote in line:
                open_quote = None
            continue
        m = _ENV_LINE.match(line)
        if not m:
            continue
        value = m.group("value").strip()
        is_live = m.group("hash") is None
        out.setdefault(m.group("key"), []).append((is_live, value, lineno))
        if is_live:
            open_quote = _quote_still_open(value)
    return out


def _live_line_hint(occurrences: list[tuple[bool, str, int]] | None) -> str:
    """给报错信息一个行号提示。dotenv 不吐行号，故只能尽力回填。"""
    if not occurrences:
        return "行号未定位"
    live = [ln for is_live, _, ln in occurrences if is_live]
    if live:
        return f"L{live[-1]}" + ("（该键多处出现，取最后一条生效行）" if len(live) > 1 else "")
    return f"L{occurrences[-1][2]}（该处是注释行，生效值来自别处 —— 可能是变量展开或被别的行覆盖）"


# ---- 源码侧：符号 → env 键 + 代码默认值 --------------------------------------


def _env_read(expr: ast.AST) -> tuple[str, ast.AST] | None:
    """在表达式里找 `COMMITTEE_*` 的 env 读取，返回 (env_key, 默认值表达式节点)。

    ⚠️ **不**在这里筛「默认值是不是字面量」：筛掉 = 这个键连同它的两条规则一起
    从覆盖面里静默消失，而脚本照样打印「干净」。判不判得出默认值由调用方分流，
    判不出且有测试在断它 → :func:`find_blind_spots` 让它吵出来。
    """
    for node in ast.walk(expr):
        hit = _registry.primitive_read(node)
        if hit:
            _form, key, default = hit
        elif isinstance(node, ast.Call) and len(node.args) >= 2:
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else None)
            if name not in _HELPERS:
                continue
            key, default = node.args[0], node.args[1]
        else:
            continue
        if default is None:
            continue
        if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
            continue
        if not key.value.startswith("COMMITTEE_"):
            continue
        return key.value, default
    return None


def _iter_env_assignments(src_root: pathlib.Path):
    """遍历 src/ 下**模块级**的 `符号 = <含 COMMITTEE_ env 读取的表达式>`。

    产出 (符号名, env_key, 默认值表达式节点, 定义位置)。
    """
    for path in sorted(src_root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:  # pragma: no cover - 让它吵
            raise RuntimeError(f"读不了 {path}: {exc}") from exc
        for node in tree.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name):
                continue
            hit = _env_read(node.value)
            if hit:
                yield target.id, hit[0], hit[1], f"{_display(path)}:{node.lineno}"


def collect_env_symbols(src_root: pathlib.Path) -> dict[str, list[tuple[str, object, str]]]:
    """扫 src/，返回 符号 → [(env_key, 代码默认值, 定义位置)]。**只含默认值是字面量的**。

    ⚠️ 值是**列表**不是单值：同名符号在两个模块各定义一次时，初版按 key 覆盖 →
    后者静默吃掉前者，此后断言会被拿去和错误的 env 键比对。现在全部留着，
    由 :func:`lint` 报重名并对**每个**候选都做检查（宁可吵，不可静默）。

    默认值不是字面量的那些不在这里，见 :func:`collect_unresolved_defaults`。
    """
    out: dict[str, list[tuple[str, object, str]]] = {}
    for symbol, env_key, default, where in _iter_env_assignments(src_root):
        if isinstance(default, ast.Constant):
            out.setdefault(symbol, []).append((env_key, default.value, where))
    return out


def collect_unresolved_defaults(src_root: pathlib.Path) -> dict[str, list[tuple[str, str]]]:
    """扫 src/，返回 符号 → [(env_key, 定义位置)]：**默认值不是字面量**的 env 读取。

    比如把默认值提成具名常量（`_clamp_int("COMMITTEE_X", _DEFAULT_X, ...)`）——
    一次纯无害的重构，就能让这个键连同两条规则一起从覆盖面里消失。
    这类**不能静默跳过**，见 :func:`find_blind_spots`。
    """
    out: dict[str, list[tuple[str, str]]] = {}
    for symbol, env_key, default, where in _iter_env_assignments(src_root):
        if not isinstance(default, ast.Constant):
            out.setdefault(symbol, []).append((env_key, where))
    return out


def _iter_equality_assertions(tests_root: pathlib.Path):
    """遍历 tests/ 下所有 `assert <名字> == <字面量>`，产出 (名字, 字面量, 位置)。"""
    for path in sorted(tests_root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:  # pragma: no cover - 让它吵
            raise RuntimeError(f"读不了 {path}: {exc}") from exc
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert):
                continue
            test = node.test
            if not (isinstance(test, ast.Compare) and len(test.ops) == 1):
                continue
            if not isinstance(test.ops[0], ast.Eq):
                continue
            left, right = test.left, test.comparators[0]
            name = left.id if isinstance(left, ast.Name) else (left.attr if isinstance(left, ast.Attribute) else None)
            if name is None or not isinstance(right, ast.Constant):
                continue
            yield name, right.value, f"{_display(path)}:{node.lineno}"


def collect_default_assertions(
    tests_root: pathlib.Path, symbols: dict[str, list[tuple[str, object, str]]]
) -> dict[str, list[str]]:
    """扫 tests/，返回 符号 → [断言位置]。**只收断言值等于代码默认值的**。

    符号有多个候选定义时，断言值只要等于**任一**候选的默认值就算命中 ——
    重名本身另有 finding 提醒，这里宁可多收也不漏。
    """
    out: dict[str, list[str]] = {}
    for name, asserted, loc in _iter_equality_assertions(tests_root):
        if name not in symbols:
            continue
        if any(values_equal(asserted, default) for _, default, _ in symbols[name]):
            out.setdefault(name, []).append(loc)
    return out


def collect_literal_assertions(tests_root: pathlib.Path, names: set[str]) -> dict[str, list[str]]:
    """扫 tests/，返回 名字 → [断言位置]：`assert <名字> == <字面量>`，**不问断言的是什么值**。

    给「判不出代码默认值」的符号用 —— 判不出默认值就没法比对，只能看有没有人在
    断它的字面量值。
    """
    out: dict[str, list[str]] = {}
    for name, _asserted, loc in _iter_equality_assertions(tests_root):
        if name in names:
            out.setdefault(name, []).append(loc)
    return out


def find_blind_spots(
    src_root: pathlib.Path, tests_root: pathlib.Path
) -> dict[str, tuple[list[tuple[str, str]], list[str]]]:
    """本检查的**失明点**：符号 → (env 读取位置列表, 断言位置列表)。

    命中条件 = 默认值判不出来（不是字面量）**且**有测试在断它的某个字面量值。
    这时两条规则对这个键整个失效，而人看到的是「lint 干净」—— 正是本脚本要治的
    那个病在检查器自己身上的形态。判不出默认值但**没人断它** = 无害，保持安静。
    """
    unresolved = collect_unresolved_defaults(src_root)
    if not unresolved:
        return {}
    asserted = collect_literal_assertions(tests_root, set(unresolved))
    return {
        symbol: (defs, asserted[symbol]) for symbol, defs in unresolved.items() if symbol in asserted
    }


def _has_marker(lines: list[str], lineno: int) -> bool:
    start = max(0, lineno - 1 - MARKER_LOOKBEHIND)
    return any(MARKER in ln for ln in lines[start:lineno])


def lint(
    symbols: dict[str, list[tuple[str, object, str]]],
    assertions: dict[str, list[str]],
    example_text: str,
    local_text: str | None = None,
    blind_spots: dict[str, tuple[list[tuple[str, str]], list[str]]] | None = None,
) -> list[str]:
    """返回 findings 列表；空列表 = 干净。`blind_spots` 见 :func:`find_blind_spots`。"""
    findings: list[str] = []
    example_lines = example_text.splitlines()
    example_occ = scan_occurrences(example_text)
    files = [(".env.example", effective_values(example_text), example_occ)]
    if local_text is not None:
        files.append((".env", effective_values(local_text), scan_occurrences(local_text)))

    def shadowed(effective: dict[str, str | None], key: str, default: object) -> bool:
        return key in effective and values_equal(effective[key], default)

    # ---- 防锈 A：同名符号被定义多次（静默取其一会比对到错的 env 键）----------
    for symbol, defs in sorted(symbols.items()):
        if len(defs) > 1:
            where = "；".join(f"{k} @ {w}" for k, _, w in defs)
            findings.append(
                f"[符号重名] `{symbol}` 在 src/ 下被定义了 {len(defs)} 次（{where}）—— "
                f"测试里的 `assert {symbol} == ...` 无法判断指向哪一个，"
                f"检查会拿它去和**可能错误**的 env 键比对。"
                f"处置：给其中一个改名，或确认它们语义相同后合并到一处。"
            )

    for symbol in sorted(assertions):
        sites = ", ".join(assertions[symbol])
        for env_key, default, where in symbols[symbol]:
            # ---- 规则 1：实际生效 + 值等于默认值 = 断言已被静默架空 -----------
            for label, effective, occ in files:
                if not shadowed(effective, env_key, default) or symbol in ALLOW:
                    continue
                raw = effective[env_key]
                hint = _live_line_hint(occ.get(env_key))
                findings.append(
                    f"[规则1·静默架空] {label} {hint} 的 {env_key} **实际生效**且值等于代码默认值 "
                    f"({default!r}，定义在 {where}；dotenv 解析出的生效值 = {raw!r})，"
                    f"而 {sites} 正在断言这个默认值 —— 该断言现在验的是本机配置，不是代码。"
                    f"处置：把这行从 {label} 去掉或改成注释（临时调值用进程 env："
                    f"`{env_key}=x pytest ...`）；若确属可接受，写进 "
                    f"scripts/lint_env_shadowing.py 的 ALLOW 并说明理由。"
                )

            # ---- 规则 2：进了模板就必须留警示（注释态也要·逐处要）------------
            for _is_live, _raw, lineno in example_occ.get(env_key, []):
                if _has_marker(example_lines, lineno):
                    continue
                findings.append(
                    f"[规则2·缺警示] .env.example:{lineno} 的 {env_key} 有测试在断它的默认值"
                    f"（{sites}），但这行附近没有警示注记。"
                    f"处置：在该行（或往上 {MARKER_LOOKBEHIND} 行内）的注释里写上「{MARKER}」，"
                    f"让下一个来取消注释的人当场看见。"
                )

    # ---- 防锈 B：ALLOW 里的条目必须仍是真实的雷 -----------------------------
    #
    # ⚠️ 判「还是不是雷」必须扫**与规则 1 同一套文件**（模板 + 本机 `.env`）。
    # 早先只查模板，于是「雷只在本机 .env」时两条检查互相打架、无解：加豁免 →
    # 这里报「豁免过时，删掉」；删豁免 → 规则 1 报「.env 静默架空」。
    # 本机那条真实仓库测试于是永远红，且两句处置指引互相矛盾。
    checked = "/".join(label for label, _, _ in files)
    for symbol in sorted(ALLOW):
        defs = symbols.get(symbol)
        if not defs:
            findings.append(f"[豁免过时] ALLOW 里的 {symbol} 已不是 env 支撑的符号 —— 删掉这条豁免。")
            continue
        still_a_hazard = symbol in assertions and any(
            shadowed(effective, env_key, default)
            for _label, effective, _occ in files
            for env_key, default, _where in defs
        )
        if not still_a_hazard:
            keys = " / ".join(k for k, _, _ in defs)
            findings.append(
                f"[豁免过时] ALLOW 里的 {symbol}（{keys}）在 {checked} 里已不是生效的雷 —— "
                f"删掉这条豁免，否则它会白白罩住将来真的复发。"
            )

    # ---- 失明点：默认值判不出来，而有测试在断它 -----------------------------
    for symbol, (defs, sites) in sorted((blind_spots or {}).items()):
        where = "；".join(f"{k} @ {w}" for k, w in defs)
        findings.append(
            f"[判不了默认值] `{symbol}` 在读 env（{where}），但那里的默认值不是字面量 —— "
            f"本检查算不出「代码默认值」，两条规则对这个键**整个失效**，"
            f"而 {', '.join(sites)} 正在断言它的一个字面量值。"
            f"处置：把默认值写回字面量（提成具名常量这种无害重构就足以让它从覆盖面里消失），"
            f"或把那条断言改成不依赖默认值。在改之前，"
            f"**别把「本检查报干净」当成这个键安全的证据**。"
        )

    return findings


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    verbose = "--verbose" in args or "-v" in args

    symbols = collect_env_symbols(SRC)
    assertions = collect_default_assertions(TESTS, symbols)
    blind_spots = find_blind_spots(SRC, TESTS)
    local_text = ENV_LOCAL.read_text(encoding="utf-8") if ENV_LOCAL.exists() else None
    if verbose:
        has_local = ENV_LOCAL.exists()
        print(f"扫描：{len(symbols)} 个 env 支撑符号；本机 .env {'存在' if has_local else '不存在（CI 即如此）'}")
        for symbol in sorted(assertions):
            for env_key, default, where in symbols[symbol]:
                print(f"  断言默认值 · {symbol} ({env_key}={default!r}, 定义 {where})")
            for loc in assertions[symbol]:
                print(f"      {loc}")
    findings = lint(
        symbols, assertions, ENV_EXAMPLE.read_text(encoding="utf-8"), local_text, blind_spots
    )
    for f in findings:
        print(f)
    if findings:
        print(f"\nlint_env_shadowing: {len(findings)} 个问题")
        return 1
    print(
        f"lint_env_shadowing: 干净"
        f"（{len(symbols)} 个 env 支撑符号，其中 {len(assertions)} 个被测试断言默认值）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
