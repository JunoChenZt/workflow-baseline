"""配置键名册 —— 从源码派生的「合法 env 键」单一真值（backlog BJ · BJ.1）。

**这个模块治的病**：2026-06-16 把 ``config.py`` 里的 Python 符号名 ``EXTERNAL_SEARCH_URL``
当成 env 变量真名去查（真名 ``COMMITTEE_EXTERNAL_SEARCH_URL``），查空 → 误判"没配置"。
没有任何东西告诉查的人「你查的这个名字根本不存在」—— 因为**根本没有一份"存在哪些名字"的清单**。

**为什么从源码派生、不手写**：手写清单 = 又一笔靠人记得去登记的账，正是要消灭的东西。
这里用 AST 把 ``src/committee`` 下每一处 env 读取枚举出来，名册 = 枚举结果。
新加一个 ``os.getenv("COMMITTEE_X")`` 自动进名册；名册与代码不可能漂开。

**认得的读取形态**（每种都有靶测，见 tests/test_lint_env_registry.py；漏一种 = 那种写法的键
从名册里静默消失、检查照样报干净 —— BJ.0 盘点时扫描器初版就漏过「元组循环读键」）：

1. ``os.getenv("K", d)`` / ``getenv("K")``           —— 字面量键
2. ``os.environ.get("K")`` / ``os.environ["K"]`` / ``"K" in os.environ`` / ``os.environ.pop("K")``
3. 键是**模块级常量**：``ENV_X = "K"; os.environ.get(ENV_X)``
4. 键是**循环变量**：``for k in ("A", "B"): os.getenv(k)``（模块级或函数内）
5. 键是**函数内局部变量**：``name = f"..."; os.getenv(name)``
6. **助手函数**：函数体里拿形参当键读 env（``_clamp_int(name, ...)`` / ``_get_bool(name, ...)``），
   键在**调用点**：``_clamp_int("COMMITTEE_X", 500, 0, 20000)``
7. **动态拼键助手**：``f"COMMITTEE_MODEL_{role.upper()}"`` —— 记成模式，按调用点的字面量展开
   （``model_for_role("macro", ...)`` ⇒ ``COMMITTEE_MODEL_MACRO``）。**按调用点展开、不按固定角色表**：
   新增调用点自动进名册。
8. 助手被 ``from committee.config import model_for_role`` 到别的模块后的调用点。

**判不出来的一律记成 unresolved、不静默丢**：调用点传的不是字面量、f-string 里嵌了认不出的表达式
—— 这些在 lint 里是 finding，不是"没看见"。

**边界**：
- 只扫 ``src/committee``（``scripts/`` / ``tests/`` 读 env 是为了测，不是产品行为）。
- 纯标准库、**不 import 本包任何东西** —— lint 脚本与测试按文件路径单独加载它，CI 上不装依赖也能跑。
- 只枚举「读」，不评判默认值 / 回退行为（那是 backlog BJ.5 逐族裁的事）。
"""
from __future__ import annotations

import ast
import pathlib
import re
from dataclasses import dataclass, field

#: 密钥类键的识别规则（BJ.0 §5）—— 规则识别，不手维护名单。
#: URL 类（``*_BASE_URL`` / ``*_MCP_URL`` / ``EXTERNAL_SEARCH_URL``）不算密钥，但值里可能带鉴权参数，
#: 落盘时由消费方去掉 query string（BJ.3）。
def is_secret(key: str) -> bool:
    return (
        key == "DATABASE_URL"
        or key.endswith(("_API_KEY", "_TOKEN", "SECRET_KEY"))
        or "PASSWORD" in key
    )


#: 模板里一行「键=值」（注释态也算：注释掉的键仍是"文档承诺"，同 lint_env_shadowing 规则 2）。
_TEMPLATE_LINE = re.compile(r"^(?P<comment>#\s?)?(?P<key>[A-Z_][A-Z0-9_]*)=")


@dataclass(frozen=True)
class Read:
    """一处 env 读取。"""

    key: str            # 具体键名；unresolved 时是源码片段 / 带 {} 的模式
    kind: str           # "literal" | "unresolved"
    file: str           # 相对仓库根的 posix 路径
    line: int
    form: str           # 语法形态：os.getenv / environ.get / environ[] / in environ / environ.pop / helper:<名>
    how: str            # 键怎么定下来的：literal / const / loop / local / call-site
    default: str | None = None   # 默认值的源码片段（没有 = None）
    symbol: str | None = None    # 读取结果赋给了哪个模块级符号（`X = os.getenv(...)` ⇒ X；嵌在 `ROLES = {...}` 里 ⇒ ROLES）


@dataclass
class Helper:
    """一个「拿形参当键读 env」的函数。"""

    name: str
    file: str
    line: int
    params: list[str]
    key_param: str
    template: str | None        # None = 键就是形参本身；否则形如 "COMMITTEE_MODEL_{}"
    transform: str | None       # "upper" / "lower" / None
    default_param: str | None   # 默认值来自哪个形参（调用点取）
    default_src: str | None     # 否则默认值写死在助手里


@dataclass
class Registry:
    files_scanned: int
    reads: list[Read]
    helpers: list[Helper]

    @property
    def keys(self) -> dict[str, list[Read]]:
        out: dict[str, list[Read]] = {}
        for r in self.reads:
            if r.kind == "literal":
                out.setdefault(r.key, []).append(r)
        return out

    @property
    def unresolved(self) -> list[Read]:
        return [r for r in self.reads if r.kind == "unresolved"]

    def has(self, key: str) -> bool:
        return key in self.keys


# ---------------------------------------------------------------------------
# 语法识别
# ---------------------------------------------------------------------------

def _is_environ(node: ast.AST) -> bool:
    """``os.environ`` / ``environ``。"""
    return (isinstance(node, ast.Name) and node.id == "environ") or (
        isinstance(node, ast.Attribute) and node.attr == "environ"
    )


def primitive_read(node: ast.AST) -> tuple[str, ast.AST, ast.AST | None] | None:
    """如果 ``node`` 是一处原始 env 读取，返回 (形态, 键表达式, 默认值表达式或 None)。

    这是全仓唯一一份「什么算读 env」的判定；lint_env_shadowing 也走这里。
    """
    if isinstance(node, ast.Call):
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else None)
        if name == "getenv" and node.args:
            return "os.getenv", node.args[0], _default_of(node)
        if name in ("get", "pop") and isinstance(fn, ast.Attribute) and _is_environ(fn.value) and node.args:
            return f"environ.{name}", node.args[0], _default_of(node)
        return None
    if isinstance(node, ast.Subscript) and _is_environ(node.value):
        return "environ[]", node.slice, None
    if isinstance(node, ast.Compare) and node.comparators and _is_environ(node.comparators[0]):
        if isinstance(node.ops[0], (ast.In, ast.NotIn)):
            return "in environ", node.left, None
    return None


def _default_of(call: ast.Call) -> ast.AST | None:
    if len(call.args) > 1:
        return call.args[1]
    for kw in call.keywords:
        if kw.arg == "default":
            return kw.value
    return None


# ---------------------------------------------------------------------------
# 键表达式求值
# ---------------------------------------------------------------------------

@dataclass
class _Scope:
    consts: dict[str, str]                    # 模块级 NAME = "..."
    loops: dict[str, list[str]]               # for NAME in ("a", "b")
    locals: dict[str, ast.AST | None]         # 函数内 NAME = <expr>；None = 赋值多次、不唯一
    params: set[str]


@dataclass
class _KeyValue:
    """键表达式的求值结果。"""

    literals: list[str] = field(default_factory=list)   # 展开后的具体键
    template: str | None = None                          # 含形参 → 模式（"{}" 占位）
    param: str | None = None                             # 模式里引用的形参
    transform: str | None = None
    how: str = "literal"
    unresolved: str | None = None                        # 认不出时的源码片段


def _eval_key(expr: ast.AST, scope: _Scope, text: str, _depth: int = 0) -> _KeyValue:
    if _depth > 5:
        return _KeyValue(unresolved=_src(expr, text))
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return _KeyValue(literals=[expr.value])
    if isinstance(expr, ast.Name):
        if expr.id in scope.loops:
            return _KeyValue(literals=list(scope.loops[expr.id]), how="loop")
        if expr.id in scope.locals:
            inner = scope.locals[expr.id]
            if inner is None:
                return _KeyValue(unresolved=_src(expr, text))
            v = _eval_key(inner, scope, text, _depth + 1)
            if v.how == "literal":
                v.how = "local"
            return v
        if expr.id in scope.params:
            return _KeyValue(param=expr.id, template="{}")
        if expr.id in scope.consts:
            return _KeyValue(literals=[scope.consts[expr.id]], how="const")
        return _KeyValue(unresolved=_src(expr, text))
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr in ("upper", "lower") and not expr.args:
        v = _eval_key(expr.func.value, scope, text, _depth + 1)
        v.transform = expr.func.attr
        if v.literals:
            v.literals = [getattr(s, expr.func.attr)() for s in v.literals]
        return v
    if isinstance(expr, ast.JoinedStr):
        combos: list[str] = [""]
        param = None
        transform = None
        how = "literal"
        for part in expr.values:
            if isinstance(part, ast.Constant):
                combos = [c + str(part.value) for c in combos]
                continue
            if not isinstance(part, ast.FormattedValue):
                return _KeyValue(unresolved=_src(expr, text))
            v = _eval_key(part.value, scope, text, _depth + 1)
            if v.unresolved:
                return _KeyValue(unresolved=_src(expr, text))
            if v.param:
                param, transform = v.param, v.transform
                continue
            if v.how != "literal":
                how = v.how
            combos = [c + lit for c in combos for lit in v.literals]
        if param:
            return _KeyValue(template=_fill_template(expr, scope, text), param=param, transform=transform)
        return _KeyValue(literals=combos, how=how)
    return _KeyValue(unresolved=_src(expr, text))


def _fill_template(expr: ast.JoinedStr, scope: _Scope, text: str) -> str:
    out = ""
    for part in expr.values:
        if isinstance(part, ast.Constant):
            out += str(part.value)
        else:
            v = _eval_key(part.value, scope, text, 1)
            out += "{}" if v.param else (v.literals[0] if v.literals else "?")
    return out


def _src(node: ast.AST, text: str) -> str:
    try:
        return ast.get_source_segment(text, node) or ast.dump(node)
    except Exception:  # pragma: no cover
        return ast.dump(node)


# ---------------------------------------------------------------------------
# 枚举
# ---------------------------------------------------------------------------

def _module_consts(tree: ast.Module) -> dict[str, str]:
    out: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                out[node.targets[0].id] = node.value.value
    return out


def _loops_in(body_root: ast.AST) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for node in ast.walk(body_root):
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and isinstance(node.iter, (ast.Tuple, ast.List)):
            vals = [e.value for e in node.iter.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            if vals and len(vals) == len(node.iter.elts):
                out[node.target.id] = vals
    return out


def _locals_in(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, ast.AST | None]:
    out: dict[str, ast.AST | None] = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            out[name] = None if name in out else node.value
    return out


def _walk_no_nested_fn(root: ast.AST):
    """遍历 root，但不进入嵌套函数（它们各自成 scope）。"""
    stack = list(ast.iter_child_nodes(root))
    while stack:
        n = stack.pop()
        yield n
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            stack.extend(ast.iter_child_nodes(n))


def _module_name(path: pathlib.Path, src_root: pathlib.Path) -> str:
    rel = path.relative_to(src_root).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _imports(tree: ast.Module) -> dict[str, str]:
    """本模块里 名字 → 它来自哪个模块（``from a.b import c`` ⇒ c: a.b；``import a.b as x`` ⇒ x: a.b）。

    ⚠️ 走 ``ast.walk`` 不走 ``tree.body``：本仓大量 import 写在**函数体内**（延迟导入），
    只看顶层会让那些调用点的助手认不出 —— 2026-09-14 首轮对账就把 ``COMMITTEE_MODEL_FUND_MGR_VERIFY``
    误报成"模板死键"（agents/base.py 在函数里 ``from committee.config import model_for_role``）。
    """
    out: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                out[a.asname or a.name] = node.module
        elif isinstance(node, ast.Import):
            for a in node.names:
                out[a.asname or a.name.split(".")[0]] = a.name
    return out


def enumerate_reads(src_root: pathlib.Path, package: str = "committee") -> Registry:
    """扫 ``src_root/package`` 下所有 .py（跳过 __pycache__），返回名册。

    读失败（语法错 / 编码错）**直接抛**，不静默跳过 —— 静默跳过就是又造一个空过。
    """
    pkg_root = src_root / package
    files = sorted(p for p in pkg_root.rglob("*.py") if "__pycache__" not in p.parts)
    repo_root = src_root.parent
    parsed: dict[pathlib.Path, tuple[ast.Module, str]] = {}
    for p in files:
        try:
            text = p.read_text(encoding="utf-8")
            parsed[p] = (ast.parse(text), text)
        except (SyntaxError, UnicodeDecodeError, OSError) as exc:
            raise RuntimeError(f"config_registry: 读不了 {p}: {exc}") from exc

    def rel(p: pathlib.Path) -> str:
        return p.relative_to(repo_root).as_posix()

    # ---- 第一遍：找助手函数（拿形参当键读 env）---------------------------------
    helpers: dict[tuple[str, str], Helper] = {}   # (模块名, 函数名) → Helper
    for p, (tree, text) in parsed.items():
        mod = _module_name(p, src_root)
        consts = _module_consts(tree)
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            params = [a.arg for a in fn.args.args + fn.args.kwonlyargs]
            scope = _Scope(consts, _loops_in(fn), _locals_in(fn), set(params))
            for node in _walk_no_nested_fn(fn):
                hit = primitive_read(node)
                if not hit:
                    continue
                _form, key_expr, default_expr = hit
                v = _eval_key(key_expr, scope, text)
                if not v.param:
                    continue
                # 默认值来源：getenv 的第二参若是形参 → 该形参；否则若函数有名为 default 的形参
                # （_clamp_int(name, default, lo, hi) 这种「raw 为空退回 default」的写法）→ 取它。
                default_param = default_expr.id if isinstance(default_expr, ast.Name) and default_expr.id in params else None
                if default_param is None and "default" in params:
                    default_param = "default"
                default_src = None if default_param is None and default_expr is None else (
                    None if default_param else _src(default_expr, text)
                )
                helpers[(mod, fn.name)] = Helper(
                    name=fn.name, file=rel(p), line=fn.lineno, params=params, key_param=v.param,
                    template=None if v.template == "{}" else v.template, transform=v.transform,
                    default_param=default_param, default_src=default_src,
                )
                break

    # ---- 第二遍：所有读取处 -------------------------------------------------------
    reads: list[Read] = []
    for p, (tree, text) in parsed.items():
        mod = _module_name(p, src_root)
        consts = _module_consts(tree)
        imports = _imports(tree)
        module_loops = _loops_in(tree)

        def scope_for(fn: ast.FunctionDef | ast.AsyncFunctionDef | None) -> _Scope:
            if fn is None:
                return _Scope(consts, module_loops, {}, set())
            return _Scope(consts, {**module_loops, **_loops_in(fn)}, _locals_in(fn),
                          {a.arg for a in fn.args.args + fn.args.kwonlyargs})

        def helper_for_call(call: ast.Call) -> Helper | None:
            f = call.func
            if isinstance(f, ast.Name):
                if (mod, f.id) in helpers:
                    return helpers[(mod, f.id)]
                origin = imports.get(f.id)
                if origin and (origin, f.id) in helpers:
                    return helpers[(origin, f.id)]
                return None
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                origin = imports.get(f.value.id)
                if origin:
                    if (origin, f.attr) in helpers:
                        return helpers[(origin, f.attr)]
                    # from committee import config ⇒ config.model_for_role
                    if (f"{origin}.{f.value.id}", f.attr) in helpers:
                        return helpers[(f"{origin}.{f.value.id}", f.attr)]
            return None

        # 模块级 `NAME = <expr>` 里出现的读取 → 记下 NAME（BJ.2 拿它去 getattr(committee.config, NAME) 读解析后的生效值）
        sym_of: dict[int, str] = {}
        for stmt in tree.body:
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                for sub in ast.walk(stmt.value):
                    sym_of[id(sub)] = stmt.targets[0].id

        # 需要知道每个节点在哪个函数里：先收集函数区间
        regions: list[tuple[ast.FunctionDef | ast.AsyncFunctionDef, list[ast.AST]]] = []
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                regions.append((fn, list(_walk_no_nested_fn(fn))))
        top_nodes = list(_walk_no_nested_fn(tree))

        def emit(nodes: list[ast.AST], fn: ast.FunctionDef | ast.AsyncFunctionDef | None) -> None:
            scope = scope_for(fn)
            for node in nodes:
                hit = primitive_read(node)
                if hit:
                    form, key_expr, default_expr = hit
                    v = _eval_key(key_expr, scope, text)
                    if v.param:
                        continue  # 助手内部的原始读取：键在调用点，那边记
                    default = _src(default_expr, text) if default_expr is not None else None
                    if v.unresolved:
                        reads.append(Read(v.unresolved, "unresolved", rel(p), node.lineno, form, "?", default, sym_of.get(id(node))))
                    for lit in v.literals:
                        reads.append(Read(lit, "literal", rel(p), node.lineno, form, v.how, default, sym_of.get(id(node))))
                    continue
                if isinstance(node, ast.Call):
                    h = helper_for_call(node)
                    if h is None:
                        continue
                    key_arg = _arg_for(node, h.params, h.key_param)
                    if key_arg is None:
                        reads.append(Read(f"{h.name}(…)", "unresolved", rel(p), node.lineno, f"helper:{h.name}", "call-site", None))
                        continue
                    v = _eval_key(key_arg, scope, text)
                    default = None
                    if h.default_param:
                        d_arg = _arg_for(node, h.params, h.default_param)
                        default = _src(d_arg, text) if d_arg is not None else None
                    else:
                        default = h.default_src
                    if v.unresolved or v.param:
                        shown = h.template.format(_src(key_arg, text)) if h.template else _src(key_arg, text)
                        reads.append(Read(shown, "unresolved", rel(p), node.lineno, f"helper:{h.name}", "call-site", default))
                        continue
                    for lit in v.literals:
                        val = getattr(lit, h.transform)() if h.transform else lit
                        key = h.template.format(val) if h.template else val
                        reads.append(Read(key, "literal", rel(p), node.lineno, f"helper:{h.name}", "call-site", default, sym_of.get(id(node))))

        for fn, nodes in regions:
            emit(nodes, fn)
        emit(top_nodes, None)

    reads.sort(key=lambda r: (r.file, r.line, r.key))
    return Registry(files_scanned=len(files), reads=reads, helpers=list(helpers.values()))


def _arg_for(call: ast.Call, params: list[str], name: str) -> ast.AST | None:
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    try:
        idx = params.index(name)
    except ValueError:
        return None
    return call.args[idx] if idx < len(call.args) else None


# ---------------------------------------------------------------------------
# 模板对账
# ---------------------------------------------------------------------------

def template_keys(text: str) -> dict[str, list[tuple[int, bool]]]:
    """``.env.example`` 一类模板里出现的键 → [(行号, 是否生效行)]；注释态也收。"""
    out: dict[str, list[tuple[int, bool]]] = {}
    for i, line in enumerate(text.splitlines(), 1):
        m = _TEMPLATE_LINE.match(line)
        if m:
            out.setdefault(m.group("key"), []).append((i, not m.group("comment")))
    return out


@dataclass
class Reconciliation:
    dead: dict[str, list[tuple[str, int]]]      # 模板有、名册无 → {键: [(模板名, 行号)]}
    undocumented: list[str]                     # 名册有、所有模板都无
    unresolved: list[Read]                      # 枚举盲区：读了但键判不出


def reconcile(registry: Registry, templates: dict[str, str]) -> Reconciliation:
    known = set(registry.keys)
    documented: set[str] = set()
    dead: dict[str, list[tuple[str, int]]] = {}
    for label, text in templates.items():
        for key, occ in template_keys(text).items():
            documented.add(key)
            if key not in known:
                dead.setdefault(key, []).extend((label, ln) for ln, _ in occ)
    undocumented = sorted(known - documented)
    return Reconciliation(dead=dead, undocumented=undocumented, unresolved=registry.unresolved)


def default_src_root() -> pathlib.Path:
    """本文件所在的 ``src/``。"""
    return pathlib.Path(__file__).resolve().parents[1]
