"""Pass 0 DeepSeek 助理输出 schema — 双 subagent 并行架构。

DS-0.1 → DS-0.P (parallel refactor):
  ResearcherBriefing = facts_inventory                      (DS-researcher)
  DebateBriefing     = debate_summary                       (DS-debate)
  VoteDistribution   = deterministic code, 不走 LLM
  Pass0Result        = 合并容器（audit_node + fund_mgr 消费）

设计原则（roadmap-v3.4 §5.2）：
- DeepSeek 助理 = 信息整理员（覆盖率优先），不是分析师
- 严格 schema 输出，严禁方向判断 / 重新分析 / 散文写作
- audit_status 由 Pass 0.5 fund_manager Audit 填写，Pass 0 输出时一律 not_audited
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field

if TYPE_CHECKING:
    from committee.schemas.vote import Vote


# ---- audit_status 枚举（Pass 0.5 lifecycle）——收 4 值（MASK.E1·2026-07-15）-------
#
# DEC-C1（fundmgr-mask-fix-series）：乱 7 值 → 4 个自然判决类别。
# ★ **2026-08-05 起 audit 不再只产「来源存在性」**：ANCHOR-MISBIND 开门方案给它加了
#   核值执法（[PR #226](https://github.com/JunoChenZt/subagent-for-investment/pull/226)·用户拍板 =
#   [endgame](../../../docs/governance/number-provenance-endgame.md) 判据 D2）——
#   下方「AUDIT-3CHECK 已彻底砍 → audit 永久停在半项」的旧口径**已被 supersede**。
#   〔本块 2026-08-06 由 #226 review F2 补正：转正时只改了 audit_node，**漏了本枚举定义处**，
#     三句（永久占位 / 无生产者 / 测试须断言其不产）全与现状相反，还在指挥后来者写反向测试。
#     命中坑表 §3.2「改数据形态须核下游 + 相邻/守护注释」(N=5)。**改枚举语义时连本块一起核。**〕
#   活跃 4 值（新代码派生写入）：
#     audit_passed   —— 核过、水印全对上 common_context references
#     audit_notsure  —— 核一半 / 免检推算 / 无法交叉验证（合并旧 partial_support +
#                       inconclusive + skipped 三态·audit_node 产）
#     audit_notpassed —— 「查了、是错的」= **已启用**（2026-08-05·空置一年多后转正）。
#                       **唯一生产者** = audit_node「数字与所引来源对不上」分支（容差 2%·
#                       可比键白名单见 [audit_node.py](../agents/audit_node.py)
#                       ``_COMPARABLE_DATA_KEYS``）；~~永久占位·无生产者~~ 已作废。
#                       守护测试 = tests/test_mask_e1_audit_enum.py（"零生产者"→"**唯一生产者**"）
#                       + tests/test_pass0_schema.py（正向断言它确实被产出）。
#                       写作待遇：**写但强标注**（非"不写"）——机械上分不清"抄错"与"挂错出处"，
#                       实测 6/6 是后者，删真数字比标注更糟（同 GATE-B 先例）。
#     not_audited    —— 没查（Pass 0 初始态 + 异常防御态·audit_node 从不返回它）
#   遗留只读（archive replay 兼容·新代码不再写入·「只加不删」·参 FindingConfidence 先例）：
#     旧 checkpoint 含 audit_partial_support(×1) / audit_inconclusive(×830) / audit_skipped(×505)
#     → 保留 Literal 成员使旧 archive replay 不 Pydantic 崩；下游按 audit_notsure 同档处理。
#   已删（从没进过任何归档·命中皆 prompt 文本·无 compat 需要）：
#     audit_confirmed_mismatch / audit_failed —— 全史零生产者·直接移除·语义位由 audit_notpassed 顶替。
# 稳定点：confidence.audit_gate 只认 == audit_passed·其余全 unavailable（二值不变·E1 不碰）。

AUDIT_STATUS = Literal[
    # ── 活跃 4 值 ──
    "audit_passed",
    "audit_notsure",
    "audit_notpassed",   # ★ 已启用（2026-08-05 转正）·唯一生产者 = audit_node 核值分支
    "not_audited",
    # ── 遗留只读（archive replay·新代码不写入）──
    "audit_partial_support",
    "audit_inconclusive",
    "audit_skipped",
]

# ---- source_type 枚举 -------------------------------------------------------
#
# 与 EvidenceItem 计划中的 source_type 对齐（S2.3 EvidenceItem 升级时统一）。
#
# 🔴 T7 守护（trace-only·2026-07-10）：source_type 是**纯溯源 trace 标签**，
# **不参与任何承重决策路由**。confidence / risk_gate **均不读它**；系统对"出处
# 可信度"的判定早已改认 ``audit_status``（source_type 的 LLM 值已证不可信——
# AP/AO 两轮坐实 web 数据被误标 ``retrieved_from_common_context``，故刻意不再按它
# 路由）。**唯一 sanctioned 的 code 消费** = audit 用 ``DATA_INSUFFICIENT`` /
# ``inferred`` 做 **claim 类型门控**（决定某条要不要审·与"出处真值"正交·见
# ``audit_node._audit_fact_against_context``）；``pass0_validator`` 对 ``retrieved``
# 无水印的检查是 **advisory warning**、非路由。
# **⚠️ 别新增"按 source_type 路由决策"的逻辑**——要判出处/可信度请用
# ``audit_status`` / ``confidence`` / 外源册，不是本标签。
# ``retrieved_from_web``：M1-T7（2026-07-10）起启用于 pass0 prompt 分类，标记联网
# 搜索（web_search·带 [W#…] 盖章）数据；纯 trace 诚实性用途（读 trace 的人不被误导），
# 不喂任何闸——仍受本守护约束。

SOURCE_TYPE = Literal[
    "retrieved",
    "retrieved_from_common_context",
    "retrieved_from_web",
    "inferred",
    "DATA_INSUFFICIENT",
]


# ---- as_of null 归一（backlog AX·2026-07-30）--------------------------------
#
# 模型对**确实没有日期**的 fact 会诚实地吐 `"as_of": null`（web 搜索结果里绝大多数
# 条目根本不带日期字段）。原 `as_of: str` 只收 str → 整份 `ResearcherBriefing`
# `model_validate` 抛 `string_type` → `ds_researcher_node` 重试一次仍失败 →
# fallback `None` → **facts_inventory 全空**：几十条日期齐全的 fact 被一条 null
# 连坐作废。2026-07-30 全链回归 e2e 实测触发率 14–19%、重试无效。
#
# ⚠️ 性质 = **惩罚诚实**——模型随便编个日期反而能过校验，如实说"不知道"却把整批
# 结果搞没。与项目原则「不确定性诚实 > 数字正确」正面冲突 → 这里把 null 归一成
# ""（= 本字段既有的"无日期"表示，与 default 同值）。
#
# 边界：**只收 null，不做格式归一**。本字段是宽松 `str`（"Q4 2024" 这类今天就收），
# 套 `sanitize_as_of` 会把现在收的值改写/丢弃 → 那是行为变更，不是本 defect 的修法。
# 同族先例（宽松 str → 严格字段须在消费点 sanitize）见 known-pitfalls §3.2。

def _as_of_null_to_empty(v: object) -> object:
    """`None` → `""`（无日期）；其余原样交给 str 校验。"""
    return "" if v is None else v


AsOfLoose = Annotated[str, BeforeValidator(_as_of_null_to_empty)]


# ---- 维度 1: facts_inventory ------------------------------------------------


class FactInventoryItem(BaseModel):
    """事实清单项 — 单条 claim + 溯源链 + 审计状态。

    fact_id 用于 {ref:fX} 引用占位（fund_manager thesis 中 {ref:f1} 指向
    facts_inventory[0]）。watermarks 保留原始引用链——T11 起两族：[REF#X-NNN]
    （表① 系统数据水印）+ [W#role-batch-rIdx#nK]（web_search 数字级编号·盖章
    seam 生成·真值在外源册 number_registry）。推算/汇总数字 = watermarks 留空 +
    source_type "inferred"（免检语义结构化承载在"无水印"上，不另立字段——
    第二个 LLM 填的位不会更可信）。
    """

    fact_id: str = Field(description="唯一 ID，如 f1, f2，用于 {ref:fX} 引用")
    claim: str = Field(description="事实性断言（一句话）")
    watermarks: list[str] = Field(
        default_factory=list,
        description="原始数据引用标记：[REF#xxx]（表①水印）/ [W#…]（web 数字级编号）",
    )
    cited_by_roles: list[str] = Field(
        default_factory=list,
        description="引用该 fact 的 analyst role 列表",
    )
    cited_in_phase: list[str] = Field(
        default_factory=list,
        description="出现阶段: phase_1 / phase_2_round_N / phase_3_vote",
    )
    source_type: SOURCE_TYPE = "inferred"
    as_of: AsOfLoose = Field(
        default="", description="数据时点 ISO 日期或空（LLM 的 null 归一为空·见上方 AX 注释）",
    )
    supporting_data: str | None = Field(
        default=None, description="补充数据（数字、百分比等原始值）",
    )
    numeric_value: float | None = Field(
        default=None,
        description=(
            "AO: 该 fact 的主数字（结构化值），供 confidence 数域名印证 + prose "
            "numeric_match 比对。口径=显示值（对齐 verify._snippet_numbers / "
            "confidence.numeric_match，不解析亿/万/%）。无硬数字 → None"
            "（缺失=不通过，fail-safe）。Optional 默认 None，旧 archive 缺键不崩。"
        ),
    )
    consensus_level: Literal[
        "consensus", "majority", "minority", "single",
    ] = "single"
    quality_flags: list[str] = Field(
        default_factory=list,
        description=(
            "质量标记。当前由下游 exec_floor check① 决策节点盖 "
            "evidence_transcription_mismatch / evidence_citation_mismatch 戳"
            "（DS-0 不再产 LLM 软 flag）"
        ),
    )
    audit_status: AUDIT_STATUS = "not_audited"
    audit_rationale: str | None = None


# ---- 维度 2: debate_summary -------------------------------------------------


class DebateSummary(BaseModel):
    """辩论摘要 — 整理 bull/bear 核心论点与演进，非分析判断。"""

    bull_core_thesis: str = Field(
        default="", description="多头核心论点（一句话）",
    )
    bear_core_thesis: str = Field(
        default="", description="空头核心论点（一句话）",
    )
    key_agreements: list[str] = Field(
        default_factory=list,
        description="双方共识点",
    )
    key_disagreements: list[str] = Field(
        default_factory=list,
        description="核心分歧点",
    )
    progression_notes: str = Field(
        default="",
        description="辩论演进轨迹（如 R2 对手让步了哪些点）",
    )


# ---- 维度 3: vote_distribution ----------------------------------------------


class RoleVote(BaseModel):
    """单角色投票摘要 — 用于与原始投票交叉验证。"""

    role: str
    direction: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    conviction: int = Field(ge=1, le=10)


class VoteDistribution(BaseModel):
    """投票分布 — 可与原始 10 voter 交叉验证。"""

    bullish_count: int = 0
    bearish_count: int = 0
    neutral_count: int = 0
    total_votes: int = 0
    average_conviction: float = Field(default=0.0, ge=0.0, le=10.0)
    per_role: list[RoleVote] = Field(default_factory=list)


# ---- subagent 输出 -----------------------------------------------------------
#
# 注：cross_role_alignment（consensus/divergent/data_gaps）= 已删死输出（AJ·2026-07-24）。
# 全 src 零 consumer（fund_mgr/audit/trace 都不读）；分歧/共识信号已由 debate_summary +
# vote_distribution 更扎实承载。旧 archive 带该 key → Pydantic extra=ignore 静默丢、不崩。


class ResearcherBriefing(BaseModel):
    """DS-researcher 输出 — reports → facts_inventory。"""

    facts_inventory: list[FactInventoryItem] = Field(default_factory=list)
    quality_warnings: list[str] = Field(default_factory=list)


class DebateBriefing(BaseModel):
    """DS-debate 输出 — debate_log → debate_summary。"""

    debate_summary: DebateSummary | None = None
    quality_warnings: list[str] = Field(default_factory=list)


# ---- 容器 -------------------------------------------------------------------


class Pass0Result(BaseModel):
    """DeepSeek 助理 Pass 0 输出 — 合并容器。

    ds_merge 节点将 ResearcherBriefing + DebateBriefing + deterministic
    VoteDistribution 合并到本结构。fund_manager 3-pass 消费此结构；
    Pass 0.5 Audit 在此基础上修改 facts_inventory[].audit_status。

    quality_warnings 由 sanity check 填入（8 项软警告），不阻塞 pipeline。
    """

    facts_inventory: list[FactInventoryItem] = Field(default_factory=list)
    debate_summary: DebateSummary | None = None
    vote_distribution: VoteDistribution | None = None
    quality_warnings: list[str] = Field(default_factory=list)


# ---- deterministic vote computation -----------------------------------------


def compute_vote_distribution(votes: list[Vote]) -> VoteDistribution:
    """Pure-code vote counting — no LLM needed."""
    bullish = bearish = neutral = 0
    total_conviction = 0
    per_role: list[RoleVote] = []

    for v in votes:
        direction = v.vote.value
        if direction == "BULLISH":
            bullish += 1
        elif direction == "BEARISH":
            bearish += 1
        else:
            neutral += 1
        total_conviction += v.conviction
        per_role.append(RoleVote(
            role=v.role,
            direction=direction,
            conviction=v.conviction,
        ))

    total = bullish + bearish + neutral
    avg = round(total_conviction / total, 1) if total > 0 else 0.0

    return VoteDistribution(
        bullish_count=bullish,
        bearish_count=bearish,
        neutral_count=neutral,
        total_votes=total,
        average_conviction=avg,
        per_role=per_role,
    )
