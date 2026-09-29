from typing import Literal

from pydantic import BaseModel, Field, field_validator

from committee.as_of import AsOfDate
from committee.schemas.common import Criticality, FindingConfidence, VerifyDataKind

# LLM 在 directional-only / SELL / HOLD 场景下偶尔对数字价位字段输出字符串占位符
# 或 null。before-validator 统一归一化为 None；父字段改为 Optional[float] 接受 None。
_NUMERIC_SENTINEL_STRINGS: frozenset[str] = frozenset(
    {"n/a", "na", "none", "null", "unknown", "", "-", "—"}
)

# decision 收敛到三值 BUY / SELL / HOLD（2026-05-29 用户拍板）。历史/变体值经
# before-validator 归一化到 canonical 3：ADD→BUY（加仓并入买入）、REDUCE→SELL
# （减仓并入卖出）、AVOID→SELL（回避=负面方向）、无法识别→HOLD（最保守默认）。
# **纯归一化、永不 raise**——守住 ``make_decision_node`` 的 bare
# ``FinalDecision.model_validate`` 永不崩 run 不变量（见 FinalDecision / CoreRisk
# docstring 的 warn-only 设计 + 稳定性 Priority 1）。非 canonical 输入的可观测性
# （warn + emit_event）由节点层 ``make_decision_node`` 承担，schema 层保持纯净
# （与 ``_coerce_take_profit_none_to_empty`` 等既有 before-validator 同风格）。
_DECISION_NORMALIZE: dict[str, str] = {
    "BUY": "BUY", "ADD": "BUY", "买入": "BUY", "加仓": "BUY", "增持": "BUY", "建仓": "BUY",
    "SELL": "SELL", "REDUCE": "SELL", "AVOID": "SELL", "卖出": "SELL", "减仓": "SELL",
    "减持": "SELL", "回避": "SELL", "清仓": "SELL",
    "HOLD": "HOLD", "持有": "HOLD", "观望": "HOLD", "中性": "HOLD", "维持": "HOLD",
}


def normalize_decision(raw: object) -> str:
    """把任意 decision 输入归一化到 canonical {BUY, SELL, HOLD}。

    无法识别（含非 str / 空 / 句子 / 未知词）→ ``HOLD``（最保守默认）。纯函数：
    不 raise、不 log、不 emit（可观测性在节点层做）。中文键经 ``.upper()`` 为恒等，
    故单次大写查找即可命中中英文键。
    """
    if not isinstance(raw, str):
        return "HOLD"
    return _DECISION_NORMALIZE.get(raw.strip().upper(), "HOLD")


class SectionSpec(BaseModel):
    """Outline 中单个段落的契约：固定 id + 标题（PR 3）。

    id 由**后端生成**（不让 LLM 自由起名），格式 ``sec_1`` / ``sec_2`` ...
    保证：稳定（可在日志里用）、可观测（事件和 schema 间强关联）、可校验
    （`pattern` 拒绝伪造形式）。LLM 输出仍是纯 list[str] 标题，注入 id
    是 `make_decision_node` 内 `_build_outline` 的职责。
    """

    id: str = Field(pattern=r"^sec_\d+$")
    title: str = Field(max_length=50)  # RDR-1.G3：30 → 50（提示词要求 ≤ 40·留缓冲）


# ===== fund_mgr 重构（不确定性诚实）：confidence 门控 verification models =====
# 核心不变量：成员资格（在 valid_fact_ids）⊥ 可信度（confidence）。
# confidence 由 code 派生（facts/confidence.py），不由 DeepSeek 自证。
# FindingConfidence/VerifyDataKind/Criticality 抽到 schemas.common（中性、零 import），
# 让 DS-0 fact（pass0）与 verification finding 说同一种可信度语言，收口②③不分叉。


class VerifyItem(BaseModel):
    """查证清单单项（步骤 2）。criticality 决定是否值得花 token 查（杠杆1）；
    data_kind 决定新鲜度窗口 + 收口① 校验；conflict 标记一致性交叉检验发现的分歧（杠杆2）。"""

    item: str = Field(description="要查证的事项，如 '京东方最新股价'")
    criticality: Criticality = "low"
    data_kind: VerifyDataKind = "other"
    conflict: bool = Field(default=False, description="一致性交叉检验标记的角色间分歧项")


class VerificationFinding(BaseModel):
    """DeepSeek 查证产出（步骤 3）+ code confidence 终裁（步骤 3'）。

    DeepSeek 只交事实和来源，不判真假：填 item/finding/source/as_of/data_kind。
    confidence 是 **code 派生的最终值**（facts/confidence.py），覆写后才作数——
    DeepSeek 说 verified 但缺源，强制降级。numeric_value 供收口① 数值校验。

    ★ MASK.D1（2026-07-15·= backlog AQ）：删死字段 `raw_confidence`（DeepSeek 自评 str·
    全库零读点·spec C2「留痕观测」名不副实连 trace 都不渲染）。旧 archive 带该键靠
    Pydantic 默认 `extra="ignore"` 兼容（本类无 model_config·不 forbid）。"""

    id: str = Field(description="finding 标识，如 'v1'（进 decision 节点 local valid_fact_ids）")
    item: str
    finding: str = Field(description="查到的事实/数字")
    source: str | None = Field(default=None, description="来源 URL")
    as_of: AsOfDate = ""
    data_kind: VerifyDataKind = "other"
    conflict: bool = False
    numeric_value: float | None = Field(default=None, description="finding 的数值（收口① 校验）")
    confidence: FindingConfidence = "unavailable"  # code 终裁，门控只读这个（Q4：默认 model_prior→unavailable）


class ClaimAudit(BaseModel):
    """全文散文数字扫描结果（步骤 5）+ 5' 替换记录（旁注字段）。

    DeepSeek 抽数字 + 提议匹配，code 数值+data_kind 双门槛校验复核（收口①）。
    confidence 是 code 终裁，门控（5'）读它。

    5' 对 confidence≠verified 的散文数字做**定性词替换**（不是标⚠——标⚠防系统不防
    人眼）：正文流里精确数字换成 replacement_text；本 ClaimAudit 保留原始 value/
    numeric_value，作为 FinalDecision.claim_audits 的旁注（机器可读，前端可选展开 /
    审计可查）。两层"剥"语义统一 = 伪精度不进人眼。"""

    location: str = Field(description="数字位置，如 'sec_2.body' / 'core_risks[0].risk'")
    claim_text: str = Field(description="数字所在短句")
    value: str = Field(description="数字字面，如 '39.6' / 'PE 15.8x'")
    numeric_value: float | None = Field(default=None, description="解析出的数值（收口① 校验）")
    data_kind: VerifyDataKind = "other"
    matched_finding: str | None = Field(default=None, description="DeepSeek 提议匹配的 finding id（提议，不作数）")
    numeric_match: bool = Field(default=False, description="code 数值+data_kind 校验结果（收口①）")
    confidence: FindingConfidence = "unavailable"  # code 终裁（Q4：默认 model_prior→unavailable）
    # 5' 替换记录：confidence≠verified → 正文换定性词，原数字留这里供旁注/审计
    replaced: bool = Field(default=False, description="5' 是否把正文里的精确数字替换成了定性词")
    replacement_text: str | None = Field(default=None, description="替换成的定性词（如 '估值区间'）")


class DecisionOutline(BaseModel):
    """决策骨架 — fund_mgr 在生成 thesis 之前先产出 3-5 个段落标题（PR 2 落地）。
    PR 3 升级为 list[SectionSpec]，给 thesis 段拿到稳定 id 以便按段扩写、按段渲染。

    设计意图（plan §11 P0 → PR 3）：把 "结构" 从 "正文" 中抽出，让续写时模型有
    结构锚点可依，缓解后段质量衰减。PR 2 仅做"半约束注入主 prompt"；PR 3 用此
    outline 驱动 N 次独立的 section 扩写——每段独立调一次 LLM、prompt 不再回灌
    其他段 body，从 O(n²) 降到 O(n)。

    生命周期：ephemeral execution artifact with UI persistence —— 节点内一次性
    生成、驱动后续 section 扩写循环；前端 RunState 长期持有用于"决策框架"展示。
    **故意 one-shot**：让 outline 也走续写会引入二级 prompt 增长，违背本 PR 初衷。

    数据流非对称：outline 影响 section 扩写（每段拿自己的 spec.title 作 prompt），
    但 section body 不反哺 outline——绝不允许"基于已生成 body 调整 outline"这种
    回路设计，那会破坏 outline 作为"先验骨架"的观测意义。

    **v2 schema 长度放宽到 1..5**（v1 是 3..5）：单段（N=1）是 outline 失败时
    `make_decision_node` 合成的降级构造（fallback "整体投资逻辑"），不应受 LLM
    契约约束；schema 层宽容、节点层（`_build_outline`）严格——LLM 输出 3-5 不符
    即触发 fallback 单段。这是"代码路径唯一"的关键妥协。
    """

    thesis_outline: list[SectionSpec]
    # fund_mgr 重构：opus 在 outline 时增补的查证清单（步骤 2b）。code 预构建的
    # high-criticality 项（角色分歧 + as_of 超期）+ opus 补充。默认空 → 旧 archive replay 兼容。
    verify_checklist: list[VerifyItem] = Field(default_factory=list)

    @field_validator("thesis_outline")
    @classmethod
    def _len_and_ids_valid(cls, v: list[SectionSpec]) -> list[SectionSpec]:
        if not (1 <= len(v) <= 5):
            raise ValueError(
                f"thesis_outline 长度须在 1..5 之间，实际 {len(v)}"
            )
        ids = [s.id for s in v]
        if len(set(ids)) != len(ids):
            raise ValueError(f"thesis_outline id 重复: {ids}")
        return v


class ThesisSection(BaseModel):
    """单段扩写结果（PR 3）。id 与 SectionSpec.id 一一对应；title 冗余存一份避免
    渲染时再 join outline。

    body 允许短（min_length=1）但不能空——空 body 在 production 多半是 LLM 输出
    异常，应该让 Pydantic raise 而不是悄悄留个空段。

    chunk_index / continuation 是**段内**续写元数据，不是全局——`_expand_section`
    退出前必须把 continuation 清零（持久化合约）。
    """

    id: str = Field(pattern=r"^sec_\d+$")
    title: str = Field(max_length=50)  # RDR-1.G3：30 → 50（提示词要求 ≤ 40·留缓冲）
    body: str = Field(min_length=1)
    chunk_index: int = 0
    continuation: bool = False
    # 非空 = 段内第 N 次续写解析失败（首次 + 重试都失败），body 在 chunk N 处截断。
    # 默认 None 保证旧持久化数据向后兼容。
    truncated_at_chunk: int | None = None
    # fund_mgr 重构：body 语义从"完整正文"变"opus 核心观点（≤1000字）"。
    # ⚠️ DEPRECATED（MASK.B1·2026-07-15）：body_expanded / expansion_status 曾由步骤6/7
    # （长正文展开 + 审阅）填充，那两步已移除（长文不增内容、前端从不渲染 body_expanded、
    # 且是 ESCAPE 逃逸面）。**字段保留**仅为旧 archive replay 兼容（老 checkpoint 带值/
    # schema_version=2）；新 run 不再产出——body_expanded 恒 None、expansion_status 恒
    # "not_expanded"、schema_version 恒 1。前端 ThesisSection 不含 body_expanded、只渲染 body。
    body_expanded: str | None = None
    expansion_status: Literal["not_expanded", "completed", "failed"] = "not_expanded"
    schema_version: int = 1


class EntryRange(BaseModel):
    """买入价格区间。`note` 必填——v1 无结构化 price context pipeline，模型给数字时若
    note Optional 会让前端把"无依据的价位"视觉强化成事实。schema 强制 note 是当前唯一
    能落地的防幻觉兜底；代价是 LLM 漏 note 时该次 decision 整体 ValidationError，可接受。

    OBS-FIX-7-neighbor：low / high 改为 Optional[float]；before-validator 将字符串
    占位符（"N/A" / "null" / "" 等）归一化为 None，避免 ValidationError 让整 run 挂。
    """

    low: float | None = None
    high: float | None = None
    note: str = Field(
        min_length=1,
        description="价位依据，例如 '前低 / 200 日均线 / Fib 38.2%'",
    )
    # fund_mgr 重构：价位结构化带 confidence（门控读字段，非 regex note）。
    # 机械门控（GATE-ROUTE G2 起 = **run 级 grounding 地板 (b)**）：整篇 verified 数
    # 不足 → 抹全部 low/high/level；足够则**原样保留**（不再逐价位要求 verified）。
    # confidence 恒写入：EXEC-FLOOR check③ 读它判「过期锚点撑价位」→ 切价位降 HOLD。
    confidence: FindingConfidence | None = Field(default=None, description="价位可信度")
    source_ref: str | None = Field(default=None, description="关联 finding id（v1/v2 / DS-0 fX）")

    @field_validator("low", "high", mode="before")
    @classmethod
    def _normalize_price_sentinel(cls, v: object) -> object:
        if isinstance(v, str) and v.strip().lower() in _NUMERIC_SENTINEL_STRINGS:
            return None
        return v


class StopLoss(BaseModel):
    """止损位。type 区分 hard（固定价位）/ trail（移动止损）；None 表示模型未指定。

    OBS-FIX-7-neighbor：level 改为 Optional[float]；before-validator 归一化字符串
    占位符。level=None 表示"无具体价位"——推荐直接将整个 stop_loss 设为 null，但此
    schema 接受 None level 以避免 ValidationError 让整 run 挂。
    """

    level: float | None = None
    type: Literal["hard", "trail"] | None = None
    note: str = Field(min_length=1, description="止损触发依据")
    confidence: FindingConfidence | None = Field(default=None, description="价位可信度（门控读字段）")
    source_ref: str | None = Field(default=None, description="关联 finding id（v1/v2 / DS-0 fX）")

    @field_validator("level", mode="before")
    @classmethod
    def _normalize_level_sentinel(cls, v: object) -> object:
        if isinstance(v, str) and v.strip().lower() in _NUMERIC_SENTINEL_STRINGS:
            return None
        return v


class TakeProfitItem(BaseModel):
    """单档止盈。`portion` 是自由文本（"30%" / "1/3" 等），不强 enum。

    OBS-FIX-7-neighbor followup：level 改为 Optional[float]；before-validator 归一化
    字符串占位符。当 directional query 无具体标的时 LLM 偶尔输出 level=null。
    """

    level: float | None = None
    portion: str | None = None
    note: str = Field(min_length=1, description="目标位依据")
    confidence: FindingConfidence | None = Field(default=None, description="价位可信度（门控读字段）")
    source_ref: str | None = Field(default=None, description="关联 finding id（v1/v2 / DS-0 fX）")

    @field_validator("level", mode="before")
    @classmethod
    def _normalize_level_sentinel(cls, v: object) -> object:
        if isinstance(v, str) and v.strip().lower() in _NUMERIC_SENTINEL_STRINGS:
            return None
        return v


class ReevaluateTrigger(BaseModel):
    """S4 soft-structure（S4.md §6.3）：结构化重评估触发条件。

    description 必填（LLM 今天已在产出的原 list[str] 元素），其余全 optional
    best-effort——soft-schema 兼容，不 raise 不崩 run。S4 trigger watcher 对
    纯价格触发（direction+threshold 够）自动订阅，复合的靠 description 兜底。
    """

    description: str
    direction: str | None = None
    threshold: float | None = None
    action: str | None = None
    expires_at: str | None = None


# `direction` 是 advisory tag（S4.md §6.3 设计决策 3），取值 price_above / price_below /
# event / metric。仅在 LLM 漏填 description、需要回填一条人可读描述时用于翻译。
_TRIGGER_DIRECTION_LABEL: dict[str, str] = {
    "price_above": "价格上破",
    "price_below": "价格下破",
    "event": "事件触发",
    "metric": "指标触发",
}


def _rebuild_trigger_description(item: dict) -> str | None:
    """LLM 漏填 ``description`` 时，从其余字段重建一条人可读的触发条件。

    重建不出（整条是空壳）返回 ``None`` —— 调用方丢弃该项。**刻意不编造内容**：
    宁可少一条触发条件，也不给决策者看一条我们自己拼出来的"条件"。

    背景：``description`` 是 ``ReevaluateTrigger`` 唯一必填字段，缺失会让 Pydantic
    raise，而决策节点走 bare ``model_validate`` 无 fallback → 崩整 run。
    """
    direction = item.get("direction")
    threshold = item.get("threshold")
    action = item.get("action")

    # bool 是 int 的子类，显式排除，避免 True 被当成阈值 1
    numeric = (
        threshold
        if isinstance(threshold, (int, float)) and not isinstance(threshold, bool)
        else None
    )

    parts: list[str] = []
    if isinstance(direction, str) and direction.strip():
        label = _TRIGGER_DIRECTION_LABEL.get(direction.strip(), direction.strip())
        parts.append(f"{label} {numeric:g}" if numeric is not None else label)
    elif numeric is not None:
        parts.append(f"价格触及 {numeric:g}")

    if isinstance(action, str) and action.strip():
        parts.append(f"→ {action.strip()}")

    return " ".join(parts) if parts else None


class ExecutionPlan(BaseModel):
    """决策的可操作指引：买入区间 / 止盈止损 / 重评估指标。

    设计取舍：
    - **`note` 全员必填**（EntryRange / StopLoss / TakeProfitItem）：见各嵌套模型 docstring。
    - **不加语义 validators**（low<=high / TP 单调 / 价位与 current_price 距离）：模型偶尔
      失误 raise 让 run 挂得不值，留给 prompt 引导 + observation 攒数据决定是否升级。
    - **顶层字段全 Optional**：HOLD/SELL 语义下可空、缺字段前端按存在性渲染。
    - **`entry` 语义锁死为"买入区间"**：SELL/REDUCE 必须置 null，用 `reevaluate_triggers`
      表达出场/减仓条件——前端 PriceLadder 按"买入"色调渲染 entry，反向使用会语义混乱。
    """

    symbol: str | None = None
    current_price: float | None = None
    unit: str | None = None
    entry: EntryRange | None = None
    stop_loss: StopLoss | None = None
    take_profit: list[TakeProfitItem] = Field(default_factory=list)
    reevaluate_triggers: list[ReevaluateTrigger] = Field(default_factory=list)

    @field_validator("take_profit", mode="before")
    @classmethod
    def _coerce_take_profit_none_to_empty(cls, v):
        # OBS-FIX-7：LLM 在 SELL / REDUCE / AVOID 决策下偶尔输出
        # take_profit: null，但 schema 要求 list[TakeProfitItem]。
        # 仅对本字段做输入归一化（None → []），不泛化到其他 list 字段。
        return [] if v is None else v

    @field_validator("reevaluate_triggers", mode="before")
    @classmethod
    def _coerce_triggers(cls, v):
        """归一化 reevaluate_triggers 输入，**永不 raise**。

        三类输入：
        - ``str``：旧 ``list[str]`` 形态（139 archive replay + 老 prompt 产物）→ 包成
          ``{description: ...}``。
        - ``dict``：新 prompt 产的结构化对象。``description`` 是 schema 唯一必填字段，
          缺了会让 Pydantic raise —— 而 ``make_decision_node`` 走 bare
          ``model_validate`` **无 fallback，raise 即崩整 run**（S4.md §6.4 约束 3 的
          soft-schema 红线）。2026-08-06 prompt 改成对象数组后这条路径**首次成为可能**
          （字符串模板下 LLM 不可能漏 description），故在此补齐：缺 description 就从
          其余字段重建一条；重建不出（整条空壳）才丢弃该项。
        - 其他类型：丢弃。宁可少一条触发条件，也不崩掉整次决策。

        与 ``_coerce_take_profit_none_to_empty`` 同风格：schema 层只做输入归一化、
        不 log 不 raise，可观测性归节点层。
        """
        if v is None:
            return []
        if not isinstance(v, list):
            # LLM 偶尔把整个字段写成单个 str / dict / null-ish 值。
            v = [v] if isinstance(v, (str, dict)) else []
        coerced = []
        for item in v:
            if isinstance(item, str):
                coerced.append({"description": item})
            elif isinstance(item, ReevaluateTrigger):
                # 已是合法实例（代码内构造 / 二次校验）→ 原样放行。
                # ⚠️ 这一支不能省：它既不是 str 也不是 dict，落到"其他类型丢弃"
                # 会把好数据静默吃掉（2026-08-06 本次加固初版就踩了，全量套件抓出）。
                coerced.append(item)
            elif isinstance(item, dict):
                item = dict(item)
                desc = item.get("description")
                if not isinstance(desc, str) or not desc.strip():
                    rebuilt = _rebuild_trigger_description(item)
                    if rebuilt is None:
                        continue  # 整条无任何可读内容 → 丢弃，不编造
                    item["description"] = rebuilt
                coerced.append(item)
            # 其他类型静默丢弃（见 docstring）
        return coerced


class CoreRisk(BaseModel):
    """结构化关键风险（PR-8c）——替换旧 ``key_risks: list[str]``。

    每条风险绑定 ``risk``（风险描述）+ ``mitigation``（对应缓解 / 触发监控）两栏，
    把"列风险"升级成"列风险 + 怎么应对"。

    **warn-only 设计（P4.B 拍板，2026-05-21）**：``risk`` / ``mitigation`` **不加**
    ``min_length``。理由：``make_decision_node`` 走 bare ``FinalDecision.model_validate``
    （无 fallback——``validate_with_fallback`` 是 AnalysisReport 专用），schema 一旦
    raise 就崩整 run（违反稳定性 Priority 1）。"≥10 字 + ≥3 条"的 enforcement 委托给
    **G5 gate**（emit finding 不 raise）+ prompt 引导 + ``_enforce_list_bounds``（warn）。
    详见 [docs/observations/pr-8c-readiness.md](§2.1 Implementation deviation)。
    """

    risk: str = Field(description="风险描述（prompt 引导 ≥10 字；schema 不强制）")
    mitigation: str = Field(
        description="对应缓解 / 触发监控（prompt 引导 ≥10 字；schema 不强制）"
    )


#: 观测型「影子」闸名（CRED.1.G2）：只对用户可见的对账结果，不进任何 LLM 消费面。
SHADOW_GATES: frozenset[str] = frozenset({"G1-shadow"})


class RiskGateFinding(BaseModel):
    """``_risk_gate_check`` 节点产出的单条 gate finding（PR-8c）。

    纯 schema 字段机械计数 + 聚合的产物，不调 LLM。作为 ``risk_gate_finding`` event
    透传给 fund_mgr，fund_mgr 在 ``risk_gate_response`` 中逐条回应。**不持久化进
    FinalDecision**（findings 是输入 / event，responses 才进 decision）。

    gate 语义 + severity（[risk-gate-design.md §B.16.2](../../../docs/pipeline/decision/risk-gate-design.md)）：
    - G1: Strong* conviction + evidence < 2 → **high**（S2 后；RW-1 对齐 B.16.2）
    - G2: cross_check_concerns ≥ 3 → **warning**
    - G3: 8 role 全 Neutral/DATA_INSUFFICIENT 但 fund_mgr 输出方向性决策 → **warning**
    - G5: core_risks < 3 OR mitigation 空 → **high**

    severity 三档 ``info/warning/high``（RW-1 对齐 B.16.2 + UI 颜色语义：warning=amber，
    high 可触发 hard_block）。hard_block 触发于任何 high → G1+G5 双档（[risk-gate-design.md
    §B.16.1 D2/D3](../../../docs/pipeline/decision/risk-gate-design.md)）。
    """

    finding_id: str = Field(description="唯一 id，v1 = gate 代码（每 gate 至多一条）")
    # CRED.1.G2（2026-09-09·用户裁 D5）：加 ``G1-shadow`` —— G1「排除错误条目」新口径的
    # **影子对账**结果。与 G1 并存：G1 仍按旧口径（条目一律计数）驱动 high / hard_block；
    # shadow 只在两口径**不一致**时出现、恒 ``warning``、携带分歧明细（见 ``details``）。
    # 升硬拦 = 把 G1 切到新口径（须用户裁·改动清单见 risk_gate.py 注释块），届时本值退役。
    # additive：旧归档不含它。⚠️ 反向不保证：带本值的新断点在没有本枚举的旧代码上 model_validate 会炸。
    gate: Literal["G1", "G2", "G3", "G5", "G1-shadow"]
    severity: Literal["info", "warning", "high"]
    message: str = Field(description="触发条件的人类可读描述")
    # RW-3 (D9b)：建议动作（基线 §B.16.3，如 "downgrade_conviction"）。Optional——
    # 给 fund_mgr 回应 / UI 一个修复方向提示，非强制。additive，default None。
    recommended_action: str | None = None
    # CRED.1.G2：结构化明细（目前只有 ``G1-shadow`` 填）。**影子试用的可审样本**就是它：
    # ``{roles: [{role, n_old, n_new, would_block, excluded: [{ref_id, data_key, value, claim}]}],
    #   would_block, would_newly_block}``
    # —— ``would_block`` 是 role 级（该 role 按新口径短缺）；``would_newly_block`` 是**闸级**
    # （新口径本该拦而旧口径 G1 没响），试用期要人工坐实的样本是后者。用户逐条认定靠的是
    # 这里的登记形态，不是 message 里的散文。additive，default None；老 checkpoint / 归档回读不受影响。
    details: dict | None = None

    # CRED.1.G2 复审修（2026-09-09）：影子 = **观测型**条目，消费者是用户——**不进** fund_mgr
    # 决策提示词、**不进**逐条回应 pass、**不进**打码豁免数字集；否则观测器污染被观测的决策，
    # 试用期采到的样本就不再是"旧口径下会发生什么"。事件流 / checkpoint / 归档 / trace 照常带它。
    # 判据走 gate 名而非 severity：warning 的既有契约是"必须被 fund_mgr 回应"
    # （risk-gate-design §UI），影子恰恰**不要**那个契约。
    @property
    def is_shadow(self) -> bool:
        return self.gate in SHADOW_GATES


def llm_facing_findings(findings: list[RiskGateFinding] | None) -> list[RiskGateFinding]:
    """去掉观测型影子后、可以喂给 LLM 的 findings（CRED.1.G2 复审修）。

    三个消费面**都**走这一个过滤：fund_mgr 决策提示词的预检注入、逐条回应 pass、打码豁免
    数字集。集中在一处 = 以后再加影子闸只改 ``SHADOW_GATES``，不会漏掉某个消费面。
    """
    return [f for f in (findings or []) if not f.is_shadow]


class RiskGateResponse(BaseModel):
    """fund_mgr 对单条 RiskGateFinding 的回应（PR-8c）。

    **warn-only**：``reason`` 不加 ``min_length``（同 CoreRisk 理由）；prompt 引导
    ``reason ≥ 20 字``（overridden 时尤其严格）。漏回应任一 finding → 节点层 emit
    ``risk_gate_response_incomplete`` event（warn），schema 不强制 len 对齐。
    """

    finding_id: str = Field(description="对应 RiskGateFinding.finding_id")
    status: Literal["accepted", "downgraded", "overridden"]
    reason: str = Field(description="回应理由（prompt 引导 ≥20 字；schema 不强制）")


# AD.3（§b 地基）：信源置信度档 — 与 audit_status（核对动作生命周期态）正交的"来源可信度"轴。
# 派生自"信源通道 + 交叉印证"，零人工表。设计见
# [docs/plans/AD-b-websearch-verify-credibility.md](../../../docs/plans/AD-b-websearch-verify-credibility.md)。
CredibilityTier = Literal[
    "verified",          # 结构化源确定性匹配（yfinance/FRED/Tushare + grep）
    "mcp-sourced",       # 经 MCP/智堡机构研报通道
    "web-corroborated",  # 开放 web，≥3 个独立源印证
    "web-single",        # 开放 web，单一源
    "unverified",        # 无支撑 / 被矛盾
    "analyst-judgment",  # fund_mgr 纯综合判断，无外部信源
]

# 信源附录渲染给用户时用中文（2026-06-01 用户要求）。单一真值源，AD.6 渲染层消费。
CREDIBILITY_TIER_ZH: dict[str, str] = {
    "verified": "确凿核实",
    "mcp-sourced": "机构研报",
    "web-corroborated": "多源印证",
    "web-single": "单一来源",
    "unverified": "未经核实",
    "analyst-judgment": "分析师判断",
}


class ReferenceEntry(BaseModel):
    """信源附录单行（§b）——报告末尾"参考文献"表的一行，给人看、人自行判断。

    由 make_decision_node 后处理（AD.6）填充，LLM 不直接输出。warn-only 友好：
    除 ref_id 外均有默认值，避免 bare ``FinalDecision.model_validate`` 崩 run。
    """

    ref_id: str = Field(description="引用编号：'f3'(DS-0 facts) / 'w5'(web)")
    source: str = Field(default="", description="来源名，如 'FRED CPIAUCSL' / '智堡研报《…》' / 域名")
    locator: str = Field(default="", description="定位：'[REF#F-001] 值' / URL / 研报 id")
    credibility: CredibilityTier = "unverified"
    as_of: AsOfDate = ""
    contested: bool = Field(default=False, description="#4：多源对同一值有冲突")
    origin: str = Field(
        default="",
        description=(
            "外源检索方（T4·additive·仅展示）：'analyst'（分析师联网检索）/ 'fund_mgr'"
            "（基金经理复核检索）；**内源恒为空串**。渲染层据此在外源表显示'检索方'列。"
            "gate/audit 永不读本字段（表③已退纯展示·层② 相位2a）；空串默认 = archive replay "
            "旧条目（无此字段）自动落内源侧。"
        ),
    )
    is_outdated: bool = Field(
        default=False,
        description=(
            "本条信源是否过期（confidence ∈ {sourced_outdated, stale}）。装配期从 confidence "
            "带出，credibility 显示值不变。⚠️ 消费方史：旧 AD.7/C 安全地板曾据此把'过期孤证'计入 "
            "unverified（层② 相位2·2026-07-07 已改·gate 不再读表③=表③退纯展示）；本字段现**仅供"
            "表③展示打标**、不再喂安全闸（过期硬拦改由 fund_mgr 步骤 5' 抹 level 承担）。"
            "默认 False = '当新鲜看'——装配期若来源可能过期须显式算出，别依赖默认。"
        ),
    )
    relevance: str = Field(
        default="",
        description=(
            "CRED.2.G4（backlog BS）：这条对本问题的身份——'on_topic' 针对本问题 / 'context' 通用背景 / "
            "'off_topic' 无关 / '' 未标注。DS-0 事实行继承所引表① 引用的身份（全部对题才算对题）；"
            "外源行与旧归档为空串。**仅展示**，gate/audit 不读。"
        ),
    )


class FinalDecision(BaseModel):
    """PR 3 breaking change：移除 ``thesis: str``、``continuation: bool``、
    ``chunk_index: int``，全部迁移到 ``thesis_sections: list[ThesisSection]``。

    单段（N=1）是合法 fallback，故 ``min_length=1``。续写元数据退居 section 内部，
    FinalDecision 本身不再需要 envelope 字段。

    list 字段长度 invariant **不在此处校验**——主 decision pass 不走续写，单次
    Pydantic ValidationError 会让整 run 挂；故 ``core_risks`` / ``trigger_events``
    / ``dissenting_views`` 的长度合理性由 `_enforce_list_bounds`（节点层）做
    warn + 截断，schema 层只接受。

    PR-8c breaking：``key_risks: list[str]`` → ``core_risks: list[CoreRisk]``；
    加 ``risk_gate_response`` / ``hard_block_reason``。``core_risks`` 故意**不加**
    ``min_length=3``——见 CoreRisk docstring 的 warn-only 设计说明；"≥3 条"由 G5 gate
    enforce。
    """

    decision: Literal["BUY", "SELL", "HOLD"] = Field(
        description=(
            "最终方向，三选一：BUY（含加仓 ADD）/ SELL（含减仓 REDUCE / 回避 AVOID）/ "
            "HOLD。其他值由 before-validator 归一化到这三个，无法识别→HOLD"
        )
    )
    position_size: str = Field(description="仓位建议，例如 '组合的 30%（上限 25%）'")
    confidence: int = Field(ge=1, le=10)
    time_horizon: str
    thesis_sections: list[ThesisSection] = Field(min_length=1)
    core_risks: list[CoreRisk] = Field(
        default_factory=list,
        description=(
            "结构化关键风险（risk + mitigation）。prompt 引导 3-5 条；schema 不强制"
            "条数（warn-only），'≥3 条' 由 G5 gate 检测。替换旧 key_risks: list[str]"
        ),
    )
    trigger_events: list[str] = Field(description="会改变决策的关键事件")
    dissenting_views: list[str] = Field(default_factory=list)
    vote_summary: dict = Field(default_factory=dict, description="raw tally")
    execution_plan: ExecutionPlan | None = Field(
        default=None,
        description=(
            "可选执行计划。HOLD 倾向用 reevaluate_triggers 表达双向阈值；"
            "SELL/REDUCE 不复用 entry——entry 字段语义是『买入区间』，"
            "出场/减仓条件应放进 reevaluate_triggers"
        ),
    )
    # PR-8c：fund_mgr 对 _risk_gate_check findings 的逐条回应。warn-only（漏回应由
    # 节点层 emit risk_gate_response_incomplete event，schema 不强制 len 对齐）。
    risk_gate_response: list[RiskGateResponse] = Field(default_factory=list)
    # PR-8c：_execution_stage_hard_block_check 节点写入（fund_mgr 自身不写）。
    # 非空 = D2-β/D3-β 触发：execution_plan 被切除、decision 降级 HOLD，本字段记原因。
    # 北极星：切除"假装的执行能力"，保留分析层（thesis_sections / core_risks 不动）。
    hard_block_reason: str | None = None
    # CRED.1.G4（用户裁 D4-b·2026-09-10）：同为硬闸节点写入（fund_mgr 自身不写）。
    # 非空 = check① 机械判「证据搬运错」、但异模型复核判误报 → 硬拦撤销、execution_plan
    # **保留**、决策方向不动，本字段记「存疑」理由（三元组 + 复核一句话）给人看。
    # 与 hard_block_reason 互斥语义：切了计划就没有存疑标；有存疑标说明计划还在。
    # Optional 默认 None → 旧 archive 缺键不崩；不进 LLM 提示词。
    execution_plan_caveat: str | None = None
    # PR-5 加性字段。fund_mgr 在裁决时如观察到 voter 共识异常一致（如 10/10 同向）
    # 应置 True，警示用户独立分析空间被压缩。具体激活逻辑在 PR-8a/PR-8c 节点层
    # 实施；本 PR 仅落 schema 默认值。
    convergence_warning: bool = False
    # OBEY-5: fund_mgr 背离 vote 第一名时必须填写的 override 理由。
    # 由 LLM 在 R1 规则触发时输出，或由 validator 在背离时强制要求。
    override_justification: str | None = Field(
        default=None,
        description="当 decision 背离投票加权第一名时的逐条驳斥理由",
    )
    # FM-3p.1：DS-0 facts_inventory 中被 fund_mgr thesis 实际引用的 fact_id 列表。
    # 由 make_decision_node 后处理从 {ref:fX} 占位符提取填入，LLM 不直接输出此字段。
    # ⚠️ 命名误导（NAMING-EXTKREFS·backlog）：这里的 "external" **不是** external websearch
    # 联网外源（那是 M1 外源册 external_websearch / build_web_references，完全另一套）；
    # 本字段是**委员会内部**被正文引用的 fact 编号。改名须动 checkpoint/archive 序列化=承重。
    # 🔒 **backlog 条目 NAMING-EXTKREFS 已于 2026-09-08 close-by-decision**：改名零行为收益、
    # 却要动存档兼容，判定不值得单独做。**本注即真值源，别再去 backlog 找活条目**；若将来本来
    # 就要做一次 breaking 的 schema 迁移，可顺手改成 `cited_fact_refs` / `thesis_cited_refs` 一类。
    external_knowledge_refs: list[str] = Field(default_factory=list)
    # AD.3（§b）：信源附录——报告级"参考文献"表，每条带来源/定位/置信度/日期。
    # 由 make_decision_node 后处理（AD.6）填充；默认空 → 旧 archive 无此字段照常 replay。
    references_appendix: list[ReferenceEntry] = Field(default_factory=list)
    # fund_mgr 重构：散文层门控状态。由 _derive_prose_gate_status 机械派生（spec R-3 / A3
    # 全抹自检）——不靠独立默认/LLM 自觉。verified = 全文扫描跑过 **且** 价位未被 (b) 地板
    # 抹光（至少一个价位仍带实际 level，或本就无价位字段）；degraded = 扫描失败退回 v3，**或**
    # 价位 level 全被抹（ungrounded run）——后者避免「报 verified 但承重价位全 null」的机器层撒谎。
    # 〔GATE-ROUTE G2 判据变更·2026-07-22〕旧口径是「至少一个价位 confidence==verified」；
    # 随价位门控改 (b)（不再逐价位要求 verified）同步改为看 level 存活，否则正常 run 全员误报 degraded。
    # schema 默认仍 verified → 旧 archive 无此字段照常 replay（派生只作用于新跑的 make_decision_node）。
    prose_gate_status: Literal["verified", "degraded"] = "verified"
    # fund_mgr 重构：散文层数字门控的完整记录（旁注字段）。每个被扫描的散文数字一条，
    # 含原始 value/numeric_value/confidence + 是否被 5' 替换。正文流里非 verified 数字已
    # 换成定性词，原数字存这里供前端可选展开 / 审计可查。默认空 → 旧 archive replay 兼容。
    claim_audits: list[ClaimAudit] = Field(default_factory=list)
    # T11（冷审·麻烦一 c）：最终正文里的外部数据章 [W#…]（内部流水号）翻译成人看的
    # 引用 [来源N] 后，此处存 [来源N] → 来源域名/URL 的对照表（脚注）。默认空 → 旧 archive
    # 无此字段照常 replay。⚠️ **不是** references_appendix——那是**纯展示表**（gate/audit 永不读·
    # 层② 相位2a 脱钩·表③退纯展示·T4 后外源 wN 亦进该表，见 base.py `_build_references_appendix`）；
    # 本字段是外源正文引用专属脚注、同样 gate/audit 永不读（#5 隔离·与表③各司其职）。每条 =
    # {marker: "来源1", num_id: "W#macro-2-1#n1", source: "域名", url: "..."}。
    web_citations: list[dict] = Field(default_factory=list)

    @field_validator("decision", mode="before")
    @classmethod
    def _normalize_decision_value(cls, v):
        # decision 收敛三值（2026-05-29 用户拍板）。纯归一化，永不 raise——保证
        # make_decision_node bare model_validate + 旧 archive replay 都不会因
        # 历史值（ADD/REDUCE/AVOID）崩 run。归一化口径见 normalize_decision()。
        return normalize_decision(v)
