"""段式 e2e 跑批的分段规格（单一真值源）。

用途：`committee analyze --stop-after <key>` 让 pipeline 跑到某个**屏障节点**就停，
存 checkpoint + 全量 trace，下次 `--resume` 接着跑下一段。方便一段一段排查问题。

为什么停在这些节点：LangGraph 用 `interrupt_after=[node]` 在指定节点跑完后、
进入下一个 superstep 前挂起，并把当前 state 原样返回（已实证 langgraph 1.1.6）。
选 **fan-in 屏障节点**（research_done / triage_passed / debate_done / ds_debate /
risk_gate_pre_check）做停点 → 停下时 state 干净（并行分支都已收束），
序列化成 JSON 跨进程 `--resume` 时不会落在半完成的 superstep 中间。

与 graph.py 的耦合：本表的 `interrupt_after` / `members` 必须与 graph.py 里
`build_committee_graph` 实际 add_node 的节点名一致。`tests/test_segments.py`
用 `build_committee_graph().get_graph()` 反查校验每个名字都存在、9 段恰好覆盖全部节点。

与 checkpoint.completed_phases() 的关系：那个函数从 state 反推"哪些阶段已完成"
（用于 resume 时打印进度）；本表定义"停在哪"。两者正交，措辞独立。
"""
from __future__ import annotations

from dataclasses import dataclass

from committee.config import RESEARCH_ROLES, VOTING_ROLES


@dataclass(frozen=True)
class Segment:
    """一个可停可续的执行段。"""

    key: str                      # --stop-after 取值，如 "research"
    index: int                    # 1-based 顺序号
    label: str                    # 中文标签（报告/CLI 展示）
    interrupt_after: str | None   # 终止节点；None = 跑到 END（最后一段）
    members: tuple[str, ...]      # 本段预期执行的节点（report 高亮用）
    produces: tuple[str, ...]     # 本段预期新增/更新的 state key（校验 + 报告分组）


# 节点 → 数据流标签（边注解 + 拓扑表的"产出"列）。
# lambda 屏障节点本身不产出 state，标注它转发/收束的聚合物。
PRODUCES: dict[str, str] = {
    "build_context": "common_context",
    "price_unavailable": "final_decision(暂不可分析)",
    **{f"analyst_{r}": f"{r}_report" for r in RESEARCH_ROLES},
    "research_done": "*_report (8)",
    "triage": "triage_verdicts",
    "rework_dispatcher": "rework_counts / *_report(重写)",
    "triage_passed": "reports + verdicts",
    "debate_bull_opening": "debate_log[+bull/opening]",
    "debate_bear_opening": "debate_log[+bear/opening]",
    "debate_bull_rebuttal": "debate_log[+bull/rebuttal]",
    "debate_bear_rebuttal": "debate_log[+bear/rebuttal]",
    "debate_bull_closing": "debate_log[+bull/closing]",
    "debate_bear_closing": "debate_log[+bear/closing]",
    "ds_researcher": "ds_researcher_result",
    "debate_done": "debate_log (6)",
    **{f"vote_{r}": f"votes[+{r}]" for r in VOTING_ROLES},
    "ds_debate": "ds_debate_result",
    "ds_merge": "pass0_result",
    "audit_pass_0_5": "pass0_result(audit_status)",
    "risk_gate_pre_check": "risk_gate_pre_findings",
    "fund_manager": "final_decision",
    "risk_gate_check": "risk_gate_findings",
    "risk_gate_response": "final_decision(.risk_gate_response)",
    "execution_stage_hard_block": "final_decision(终稿)",
}


# 节点 → 主要消费的上游 state key（拓扑表"输入"列；硬编码，链路固定）。
CONSUMES: dict[str, str] = {
    "build_context": "query / context",
    "price_unavailable": "price_unavailable / confirmed_tickers",
    **{f"analyst_{r}": "common_context" for r in RESEARCH_ROLES},
    "research_done": "*_report",
    "triage": "*_report",
    "rework_dispatcher": "triage_verdicts",
    "triage_passed": "triage_verdicts",
    "debate_bull_opening": "*_report",
    "debate_bear_opening": "*_report / debate_log",
    "debate_bull_rebuttal": "debate_log",
    "debate_bear_rebuttal": "debate_log",
    "debate_bull_closing": "debate_log",
    "debate_bear_closing": "debate_log",
    "ds_researcher": "*_report",
    "debate_done": "debate_log",
    **{f"vote_{r}": "debate_log / *_report" for r in VOTING_ROLES},
    "ds_debate": "debate_log / votes",
    "ds_merge": "ds_researcher_result / ds_debate_result",
    "audit_pass_0_5": "pass0_result",
    "risk_gate_pre_check": "pass0_result",
    "fund_manager": "pass0_result / risk_gate_pre_findings",
    "risk_gate_check": "final_decision",
    "risk_gate_response": "risk_gate_findings / final_decision",
    "execution_stage_hard_block": "risk_gate_findings / final_decision",
}


_DEBATE = {
    1: ("debate_bull_opening", "debate_bear_opening"),
    2: ("debate_bull_rebuttal", "debate_bear_rebuttal"),
    3: ("debate_bull_closing", "debate_bear_closing"),
}


# 9 段。停点都对齐 fan-in 屏障，并行分支收束后再切。
SEGMENTS: list[Segment] = [
    Segment(
        key="context", index=1, label="① 公共上下文",
        interrupt_after="build_context",
        # price_unavailable = AT.2 现价拿不到早退终点（build_context 后条件跳转·→END）
        members=("build_context", "price_unavailable"),
        produces=("common_context",),
    ),
    Segment(
        key="research", index=2, label="② 并行研究（8 analyst）",
        interrupt_after="research_done",
        members=tuple(f"analyst_{r}" for r in RESEARCH_ROLES) + ("research_done",),
        produces=tuple(f"{r}_report" for r in RESEARCH_ROLES),
    ),
    Segment(
        key="triage", index=3, label="③ Triage + rework",
        interrupt_after="triage_passed",
        members=("triage", "rework_dispatcher", "triage_passed"),
        produces=("triage_verdicts", "rework_counts"),
    ),
    Segment(
        # ds_researcher 在 triage_passed 后与 debate r1 并行，落在本段
        key="debate1", index=4, label="④ 辩论 R1 opening (+ds_researcher 并行)",
        interrupt_after="debate_bear_opening",
        members=_DEBATE[1] + ("ds_researcher",),
        produces=("debate_log", "ds_researcher_result"),
    ),
    Segment(
        key="debate2", index=5, label="⑤ 辩论 R2 rebuttal",
        interrupt_after="debate_bear_rebuttal",
        members=_DEBATE[2],
        produces=("debate_log",),
    ),
    Segment(
        key="debate3", index=6, label="⑥ 辩论 R3 closing",
        interrupt_after="debate_done",
        members=_DEBATE[3] + ("debate_done",),
        produces=("debate_log",),
    ),
    Segment(
        key="votes", index=7, label="⑦ 投票（10 voter）+ ds_debate",
        interrupt_after="ds_debate",
        members=tuple(f"vote_{r}" for r in VOTING_ROLES) + ("ds_debate",),
        produces=("votes", "ds_debate_result"),
    ),
    Segment(
        key="pass0", index=8, label="⑧ ds_merge + audit + 前置风控",
        interrupt_after="risk_gate_pre_check",
        members=("ds_merge", "audit_pass_0_5", "risk_gate_pre_check"),
        produces=("pass0_result", "risk_gate_pre_findings"),
    ),
    Segment(
        key="decision", index=9, label="⑨ 决策 + 风控闸门 + hard_block",
        interrupt_after=None,  # 跑到 END
        members=(
            "fund_manager", "risk_gate_check",
            "risk_gate_response", "execution_stage_hard_block",
        ),
        produces=("final_decision", "risk_gate_findings"),
    ),
]


_BY_KEY = {s.key: s for s in SEGMENTS}
_BY_INDEX = {s.index: s for s in SEGMENTS}


def all_keys() -> list[str]:
    return [s.key for s in SEGMENTS]


def segment_by_key(key: str) -> Segment | None:
    return _BY_KEY.get(key)


def next_segment(seg: Segment) -> Segment | None:
    """返回下一段；seg 是最后一段则 None。"""
    return _BY_INDEX.get(seg.index + 1)


def resolve_stop_after(value: str) -> Segment:
    """把 --stop-after 取值（段 key 或 1-based 序号）解析成 Segment。

    解析失败抛 ValueError，带可用取值清单——CLI 直接把消息透给用户。
    """
    value = (value or "").strip()
    seg = _BY_KEY.get(value)
    if seg is not None:
        return seg
    if value.isdigit():
        seg = _BY_INDEX.get(int(value))
        if seg is not None:
            return seg
    avail = ", ".join(f"{s.index}={s.key}" for s in SEGMENTS)
    raise ValueError(f"未知的 --stop-after 值 {value!r}；可用：{avail}")


def members_up_to(seg: Segment) -> set[str]:
    """seg（含）及之前所有段的成员节点并集——report 里标"已完成/已跳过"。"""
    out: set[str] = set()
    for s in SEGMENTS:
        out |= set(s.members)
        if s.index == seg.index:
            break
    return out
