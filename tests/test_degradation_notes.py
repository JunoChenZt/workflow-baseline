"""BK.2 收集器（M0）—— 便条篮的机制层守护。

**为什么机制要单独测透**：后面 20 多处接线只各配 2 条测试（注入故障验会响 / 对照组验不误报），
靠的就是机制本身在这里被测穿。前两批每处自带一套字面量守护，25 处照那样做会产出 25 套、
不可维护 —— 这是收集器存在的理由，也是本文件必须够硬的理由。

🔴 **最要紧的一组在最后**：`test_no_scope_is_counted_not_swallowed`
—— "篮子不在就悄悄丢"正是本域要治的那个病本身。
"""
from __future__ import annotations

import asyncio
import pathlib
import subprocess
import threading

import pytest

from committee.degradation import NOTE_CODES, NOTE_RULE, degradation_summary
from committee.degradation_notes import (
    RECORDER_DROPPED_CODE,
    dropped_count,
    note_degradation,
    notes_scope,
    reset_dropped,
    end_run_notes,
    start_run_notes,
)

CODE = "fundamentals_fetch_failed"      # 码表里真实存在的码（别用编的）


@pytest.fixture(autouse=True)
def _clean_dropped():
    """每条测试都跑在「一次跑批」里（M2.3 起丢失单按跑批开·不在跑批里的便条当场作废）。
    「不在任何跑批里」那一支的行为另见 test_degradation_run_scope.py。"""
    token = start_run_notes()
    reset_dropped()
    yield
    reset_dropped()
    end_run_notes(token)


# ---- 1. 传递矩阵（模块 docstring 那张表的可复现版本）--------------------------------


def test_propagation_matrix():
    """★★ 六种跑法逐一实测 —— 表里写的每一格都由本条支撑，不是推断。

    ⚠️ 失败时**别改断言**：那说明 Python 的上下文语义与我们记的不一致，
    要改的是模块 docstring 那张表和依赖它的接线方案。
    """
    got: list[str] = []

    async def leaf_async(tag):
        note_degradation(CODE, tag)

    def leaf_sync(tag):
        note_degradation(CODE, tag)

    def rebind_inside(tag):
        # 反例：子上下文里重新 set 一个篮子 —— 外面看不到（规则 1 禁止这么写）
        from committee.degradation_notes import _NOTES
        _NOTES.set([])
        note_degradation(CODE, tag)

    async def main():
        with notes_scope() as box:
            await leaf_async("同协程")
            await asyncio.gather(leaf_async("gather-1"), leaf_async("gather-2"))
            await asyncio.to_thread(leaf_sync, "to_thread")
            await asyncio.create_task(leaf_async("create_task"))
            await asyncio.to_thread(rebind_inside, "线程内 set")
            # BK.6：标的解析在 build_context 内 to_thread 后再 asyncio.run 一个协程（classifier）——
            # 数字盖章失败的便条会从这一层发，篮子必须传得到
            await asyncio.to_thread(lambda: asyncio.run(leaf_async("run-in-thread")))
            t = threading.Thread(target=leaf_sync, args=("裸线程",))
            t.start()
            t.join()
            return [e["detail"] for e in box]

    got = asyncio.run(main())

    for want in ("同协程", "gather-1", "gather-2", "to_thread", "create_task", "run-in-thread"):
        assert want in got, f"这种跑法本该收得到，实际没收到：{want}（收到 {got}）"
    assert "线程内 set" not in got, "子上下文里 set() 竟然传出来了 —— 规则 1 的前提变了"
    assert "裸线程" not in got, "裸线程竟然拿到了篮子 —— 传递语义与记录不一致"


def test_no_bare_threads_in_src():
    """★ 上一条里"裸线程收不到"之所以无害，前提是**本仓根本不用裸线程**。

    前提变了（有人新写了 `threading.Thread`）就在这里红 —— 否则那种跑法会静默丢便条。
    """
    out = subprocess.run(
        ["git", "grep", "-n", "--untracked", "-e", "threading.Thread(", "--", "src/committee"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert not out.stdout.strip(), (
        "src/committee 里出现了裸线程 —— 那里调 note_degradation 会静默丢；"
        f"要么改用 asyncio.to_thread，要么给该处显式传递上下文：\n{out.stdout}")


# ---- 2. 🔴 没篮子 = 计数，不是静默 ------------------------------------------------


def test_no_scope_is_recorded_not_swallowed():
    """🔴 ★★ 不在作用域里发的便条 → **下一个节点出口把它变成一条 `recorder_dropped` 降级**。

    "篮子不在就悄悄丢"= 把本域正在治的病原样复制一遍（记录器自己失灵、产物看起来正常）。

    ⚠️ **刻意不用「进程级计数 + 归档印个数」**（PR #298 review 两条 finding）：
    段式跑每段独立进程、归档在最后一段写 ⇒ 读进程累计值永远是 0、产物会印「无丢失」；
    且常驻服务里会跨跑串味。改走 enforcement_log 后，它本就进断点、跨段累积。
    """
    note_degradation(CODE, "在作用域之外发的")
    assert dropped_count() == 1, "没篮子时被静默吞掉了 —— 这正是本域要治的形态"

    with notes_scope() as box:
        pass
    assert dropped_count() == 0, "节点出口该把它取走并清零（否则会跨跑串味）"
    assert [e["action"] for e in box] == [RECORDER_DROPPED_CODE]
    assert CODE in box[0]["detail"]
    assert RECORDER_DROPPED_CODE in _codes(box), "记录器失灵本身必须能被汇总看见"


def test_scope_exit_restores_previous():
    """★ 出了作用域就不再收 —— 否则跨节点串味，一个节点的便条记到另一个节点上。"""
    with notes_scope() as box:
        note_degradation(CODE, "在里面")
    assert len(box) == 1
    note_degradation(CODE, "在外面")
    assert len(box) == 1, "作用域退出后还在往旧篮子里塞"
    assert dropped_count() == 1, "退出后发的便条应被记为丢失，等下一个节点出口取走"


def test_late_note_from_a_subtask_is_not_swallowed():
    """🔴 ★ 节点退出后才到的便条（子任务慢了一步）→ 计入丢失，**不掉进已倒空的篮子**。

    子任务是在**创建时**拿到篮子绑定的，节点退出后它仍指着同一个列表对象 ——
    不标记的话，晚到的便条既不进产物、也不计丢失（PR #298 review 逮到的静默洞）。
    """
    late: list = []

    async def main():
        with notes_scope() as box:
            late.append(asyncio.create_task(_slow_note()))
            # 节点在子任务写完之前就退出了
        await asyncio.gather(*late)
        return box

    async def _slow_note():
        await asyncio.sleep(0)
        note_degradation(CODE, "我来晚了")

    box = asyncio.run(main())
    assert not [e for e in box if e["detail"] == "我来晚了"], "晚到的便条掉进了已倒空的篮子"
    assert dropped_count() == 1, "晚到的便条既没进产物也没计丢失 —— 又一个静默洞"


def test_exit_merge_appends_not_overwrites(repo_root):
    """★ 出口写法必须**追加**（M2.2 起全图唯一出口在包装函数里）：决策 / 风控环节内层会产闸门执法记录。"""
    src = (repo_root / "src/committee/degradation_notes.py").read_text(encoding="utf-8")
    assert 'list(patch.get("enforcement_log") or []) + stamped' in src,         "出口用了覆盖式合并 —— 会产执法记录的环节上就会吞掉它们"


# ---- 3. 规则 1 的源码守护 ----------------------------------------------------------


def test_only_the_scope_helper_sets_the_contextvar():
    """★ `src/committee` 里 `_NOTES.set(` 只允许出现在 `notes_scope` 那一处。

    别处 `set()` 会换掉篮子对象 —— 并发子任务 / 线程里换的那个，外面**看不到**
    （见传递矩阵「线程内 set」那格）。这是会静默丢数据的写法，用源码扫描钉死。
    （本文件自己的 `rebind_inside` 是**故意的反例**，在 tests/ 下、不在扫描范围内。）

    ⚠️ **必须带 `--untracked`**：`git grep` 默认只搜已跟踪文件，新加的源文件还没入索引时
    会扫出 0 条、以「全绿」的面目通过 —— M0 首跑就踩到了这一格。
    """
    out = subprocess.run(
        ["git", "grep", "-n", "--untracked", "_NOTES.set(", "--", "src/committee"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    hits = [ln for ln in out.stdout.splitlines() if ln.strip()]
    assert len(hits) == 1 and hits[0].startswith("src/committee/degradation_notes.py"), \
        f"_NOTES.set( 只许出现在 degradation_notes.notes_scope 里，实际：{hits}"


# ---- 4. 通用派生 -------------------------------------------------------------------


def _codes(enforcement):
    state = {"common_context": {}, "enforcement_log": enforcement}
    return {e.code for e in degradation_summary(state)}


def test_note_becomes_a_degradation_event():
    with notes_scope() as box:
        note_degradation(CODE, "600519.SH: boom")
    assert CODE in _codes(box)


def test_same_code_twice_is_one_event_with_count():
    """★ 三处基本面都失败是**一件事**，不是三件 —— 否则用户面会被同一句话刷屏。"""
    with notes_scope() as box:
        note_degradation(CODE, "a")
        note_degradation(CODE, "b")
    events = [e for e in degradation_summary({"common_context": {}, "enforcement_log": box})
              if e.code == CODE]
    assert len(events) == 1
    assert "2 处" in events[0].text


def test_unregistered_code_is_still_reported():
    """★ 码没登记**也要报**（而不是静默丢）—— 漏登记是接线错误，与本域要治的病同形态。"""
    box = [{"rule": NOTE_RULE, "action": "zz_not_in_table", "detail": ""}]
    events = [e for e in degradation_summary({"common_context": {}, "enforcement_log": box})
              if e.code == "zz_not_in_table"]
    assert events and "没在码表里登记" in events[0].text


def test_other_enforcement_entries_are_not_notes():
    """★ 闸门执法记录不是便条 —— 通用派生只认自己那个 rule。"""
    box = [{"rule": "hard_block", "action": "block", "detail": "x"}]
    assert not _codes(box)


def _note_codes_used_in_source() -> set[str]:
    """按 AST 取每个 ``note_degradation(<字面量>, ...)`` 调用的首参（不认写法）。

    🔴 BK.2 M3（2026-09-18）改：原来用单行正则 ``note_degradation\\("…"`` 扫，**多行写法整个看不见**
    （``note_degradation(\\n    "code",`` —— #304 的 coerced 便条起就是这种写法、一直没被盯住）；
    两向变异「码表漏登记」不转红才暴露。同族先例：BJ 派生器「循环读键 / 函数体内 import」盲区 ⇒ 守护按 AST 取。
    """
    import ast

    # ⚠️ **必须带 `--others --exclude-standard`**（#306 review·2026-09-21）：`git ls-files` 默认只列
    # 已跟踪文件，新加的源文件还没 `git add` 时整个看不见 —— 用了没登记的码照样全绿。
    # 同文件另两道扫描守卫为同一个理由带着 `--untracked`（M0 首跑就踩到过），本条改写时漏了。
    out = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard",
         "--", "src/committee/*.py", "src/committee/**/*.py"],
        capture_output=True, check=True,
    )
    used: set[str] = set()
    for rel in out.stdout.decode("utf-8").split("\0"):
        if not rel:
            continue
        tree = ast.parse(pathlib.Path(rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else fn.attr if isinstance(fn, ast.Attribute) else None
            if name != "note_degradation" or not node.args:
                continue
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                used.add(first.value)
    return used


def test_note_codes_cover_all_call_sites():
    """★ 源码里用到的每个码都必须在码表里 —— 「接一个新点 = 代码一行 + 码表一行」的那道闸。"""
    used = _note_codes_used_in_source()
    assert used, "扫到 0 个调用点 —— 识别器在空转，不许以「零 finding」的面目通过"
    # 识别器自证：多行写法的调用点必须被认到（M3.1 那条就是多行写的）
    assert "verification_finding_dropped" in used, "AST 识别器没认到多行写法的调用点"
    missing = sorted(used - set(NOTE_CODES))
    assert not missing, f"这些码在源码里用了但没登记进 NOTE_CODES：{missing}"


def test_note_rule_matches_its_source():
    """★ 字面量两处必须一致（degradation.py 被登记检查单独加载·不能 import 包内模块）。"""
    from committee.degradation_notes import NOTE_RULE as SRC
    assert NOTE_RULE == SRC


# ---- 5. 真实链路穿线（不是桩）-------------------------------------------------------


def test_real_fundamentals_failure_reaches_the_box(monkeypatch):
    """★★ 拿**真实的深层函数**穿一次：A 股基本面拉取失败 → 经**图层统一包装**进执法记录。

    为什么不用桩：机制的价值全在「深层代码不改签名也能留痕」，
    而这只有让真的调用链跑一遍才算证到（本仓反复踩的「手搭上下文 = 病灶」）。
    M2.2 起篮子由包装函数开，本条改为经包装调用 —— 测的才是生产路径。
    """
    from committee.common_context.sources import tushare_source
    from committee.degradation_notes import with_notes

    async def _boom(*a, **k):
        raise RuntimeError("tushare 挂了")
    monkeypatch.setattr(tushare_source, "_post_tushare_row", _boom)

    async def node(state):
        await tushare_source._fetch_fundamentals_cn("tok", "600519.SH", 5.0)
        return {}

    out = asyncio.run(with_notes(node, "build_context")({}))
    log = out.get("enforcement_log") or []
    assert log, "真实链路里基本面拉取失败了，却没留下便条"
    assert {e["action"] for e in log} == {CODE}
    assert {e["node"] for e in log} == {"build_context"}
    assert CODE in _codes(log)


# ---- 6. BK.2 M2.1：并行环节各开本子（一次性探针转正）----------------------------------
#
# 蓝本：docs/observations/bk2-m1-20260915/parallel-scope-probe.py。
# 🔑 两类断言**刻意分开**（拆解 M2.1·2026-09-17 改正）：
#   - 隔离断言：各收各的、零丢失、拼接后条数对 —— **不论实际是否并发都必须成立**；
#   - 并发断言：用栅栏**强制**制造重叠 —— 它失败只说明测试没造出并发，不否定方案。
# 原写法「先断言并发、并发不出来就重审方案」是反的：不并发 = 顺序跑 = 篮子只会更安全。

import operator
import threading as _threading
from typing import Annotated, TypedDict


class _PState(TypedDict):
    log: Annotated[list, operator.add]


def _deep(tag: str) -> None:
    """假装是取数源 / 工具循环里的深层函数 —— 不知道自己在哪个节点里。"""
    note_degradation(CODE, f"from-{tag}")


def _build_parallel_graph(kind: str, *, shared_box: list | None = None, gate=None):
    """三个同类节点从 START 并行扇出。

    shared_box 非空 = **变异**：节点不开自己的篮子、共用一个列表（模拟「两个环节共用一本」）。
    gate = 可选的栅栏（asyncio 用 _AsyncGate / 同步用 threading.Barrier），强制重叠。
    """
    from langgraph.graph import END, START, StateGraph

    def _report(tag, box):
        return {"log": [(tag, [e["detail"] for e in box if e["action"] == CODE])]}

    def make_async(tag):
        async def node(state):
            if shared_box is not None:
                box = shared_box
                await asyncio.gather(*[asyncio.to_thread(_deep, tag) for _ in range(3)])
                return _report(tag, box)
            with notes_scope() as box:
                if gate is not None:
                    await gate.wait_all()
                await asyncio.gather(*[asyncio.to_thread(_deep, tag) for _ in range(3)])
            return _report(tag, box)
        return node

    def make_sync(tag):
        def node(state):
            if shared_box is not None:
                _deep(tag)
                return _report(tag, shared_box)
            with notes_scope() as box:
                if gate is not None:
                    gate.wait()
                _deep(tag)
            return _report(tag, box)
        return node

    g = StateGraph(_PState)
    mk = make_async if kind == "async" else make_sync
    for i in "abc":
        name = f"{kind}_{i}"
        g.add_node(name, mk(name))
        g.add_edge(START, name)
        g.add_edge(name, END)
    return g.compile()


def _contamination(log: list, per_node: int) -> list[str]:
    """隔离判据：每个节点只收到自己的便条、条数恰好 per_node。返回问题清单（空 = 干净）。"""
    problems = []
    for tag, details in log:
        foreign = [d for d in details if d != f"from-{tag}"]
        if foreign:
            problems.append(f"{tag} 收到了别人的便条 {foreign}")
        if len(details) != per_node:
            problems.append(f"{tag} 应收 {per_node} 条、实收 {len(details)}")
    return problems


class _AsyncGate:
    """三个协程都走到这里才一起放行 —— 放行本身就证明它们时间窗重叠。"""

    def __init__(self, n: int):
        self.n, self.entered, self.ev = n, 0, None

    async def wait_all(self):
        if self.ev is None:
            self.ev = asyncio.Event()
        self.entered += 1
        if self.entered >= self.n:
            self.ev.set()
        await asyncio.wait_for(self.ev.wait(), timeout=5)


@pytest.mark.parametrize("kind,per_node", [("async", 3), ("sync", 1)])
def test_parallel_nodes_each_keep_their_own_box(kind, per_node):
    """🔴 ★★ 隔离断言（无条件成立）：三个并行节点各收各的、零丢失、reducer 拼接后条数对。"""
    out = asyncio.run(_build_parallel_graph(kind).ainvoke({"log": []}))
    assert len(out["log"]) == 3, f"reducer 拼接后应有 3 条节点记录，实际 {out['log']}"
    assert sorted(t for t, _ in out["log"]) == [f"{kind}_{i}" for i in "abc"]
    assert not _contamination(out["log"], per_node), _contamination(out["log"], per_node)
    assert dropped_count() == 0, "并行节点里有便条掉进了丢失单"


def test_parallel_async_nodes_really_overlap():
    """★ 并发断言（异步）：栅栏强制三节点同时在篮子里 —— 放行即证重叠，且隔离仍成立。"""
    gate = _AsyncGate(3)
    out = asyncio.run(_build_parallel_graph("async", gate=gate).ainvoke({"log": []}))
    assert gate.entered == 3
    assert not _contamination(out["log"], 3)


def test_parallel_sync_nodes_really_overlap():
    """★ 并发断言（同步）：线程栅栏强制三节点同时在篮子里。

    ⚠️ 栅栏超时 = 框架把同步节点**串行**跑了 —— 那只说明本测试没造出并发，
    **不否定**篮子方案（串行只会更安全）；要改的是测试写法，不是方案。
    """
    barrier = _threading.Barrier(3, timeout=5)
    try:
        out = asyncio.run(_build_parallel_graph("sync", gate=barrier).ainvoke({"log": []}))
    except _threading.BrokenBarrierError:  # pragma: no cover - 调度前提变了才会进
        pytest.fail("同步节点没有并发执行（栅栏超时）—— 核 LangGraph 同步节点调度方式，改测试写法")
    assert not _contamination(out["log"], 1)


@pytest.mark.parametrize("kind", ["async", "sync"])
def test_isolation_check_catches_a_shared_box(kind):
    """★ 变异：让三个环节**共用一本** → 隔离判据必须报出串味（证明判据不是恒真）。"""
    shared: list = []
    with notes_scope() as outer:        # 共用本子也得在作用域里，否则便条进丢失单、测不到串味
        shared = outer
        out = asyncio.run(_build_parallel_graph(kind, shared_box=shared).ainvoke({"log": []}))
    per_node = 3 if kind == "async" else 1
    assert _contamination(out["log"], per_node), "共用一本也判成干净 —— 隔离判据在空转"


def test_note_survives_asyncio_run_inside_a_worker_thread():
    """★ 传递矩阵补一行（标的解析的真实跑法）：节点开篮 → to_thread → 线程内 asyncio.run
    → 其中再 gather + to_thread。2026-09-17 探针实测通过，此处转正防退化。"""
    async def inner():
        await asyncio.gather(asyncio.sleep(0), asyncio.to_thread(note_degradation, CODE, "gather-thread"))
        note_degradation(CODE, "direct")

    def sync_classify():
        asyncio.run(inner())

    async def node():
        with notes_scope() as box:
            await asyncio.to_thread(sync_classify)
        return box

    box = asyncio.run(node())
    assert sorted(e["detail"] for e in box) == ["direct", "gather-thread"]
    assert dropped_count() == 0
