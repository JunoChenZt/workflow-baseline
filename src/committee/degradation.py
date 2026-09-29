"""本跑退了哪几步 —— 降级汇总（backlog BK.1）。

**这个模块治的病**：系统有几十条"退路"（模型超时换正则认代码、计划出不来退老路由、源挂了跳过、
报告写不出用兜底……）。退路本身是对的，**问题是走了没人知道**：结果看起来正常，其实数据没拿到
（[META 观察](../../docs/observations/meta-assume-mechanism-without-verify.md) 实例 #2）。
痕迹其实散落在十几个字段里，但**没有一处能回答"这次跑到底退了几步"**。本模块就是那一处。

**三条硬边界**（每条都有守护）：

1. **纯派生、零副作用**：只读已有 state 字段，**不写 state、不加字段、不改任何降级判定**
   （🚩 北极星边界，与 BK 立项原话一致：只做可见性）。
2. **不进提示词**：汇总只喂 trace / 归档 / CLI 三个展示面。观测产物进了被观测对象的输入
   就是污染决策（坑表 2026-09-10 实证：影子 finding 走正式通道进了 fund_mgr 提示词）。
3. **字段缺失 = 未知，不折成"没降级"**：旧归档（109+ 份，含 07-10 旧格式断点）整块缺字段是常态；
   把"读不到"当成"没事"正是本模块要治的那个病换个地方复发。

**为什么要分"没跑到"与"跑了但降级"**：`pass0_result is None` 两种含义都可能 —— 段式跑只跑到
seg1 时它本来就是 None。而 :func:`completed_phases` 判"pass0 完成"用的**正是同一个字段**，
拿它当判据会把两者混为一谈（坑表：信号被中间层抹掉）。本模块改用**更下游有没有产物**来判：
决策产出了 ⇒ pass0 必然跑过 ⇒ 此时的 None 才是真降级。

推导源逐条见 [BK.0 盘点 §4](../../docs/plans/BK-G0-inventory-2026-09-14.md)。
盘点同时查明：大半的降级点今天**产物里看不见**，本模块覆盖的是有结构化留痕的那些；
其余由 BK.2 逐点补痕 —— **补痕通道已定 = 复用既有 ``enforcement_log``**（不新增 state 键；
它已进断点 / 归档 / 本模块，写一条记录 + 在这里加一条派生即可）。
⚠️ **别引用盘点里「58 / 33」那两个数** —— 已三次订正、且从表里复算不出来；
口径与实数**只存一份**，以 [BK.0 §3.0 / §3.1](../../docs/plans/BK-G0-inventory-2026-09-14.md) 为准 ——
这里不再抄一份具体数字（2026-09-16 冷审：抄过一份，M1.5 改了 5 行登记类别后两边就对不上了）。
⚠️ 引用那张表时注意它自己的前向警告：**留痕层那一栏与代码对账有 9 处不符**，任何一格都不许单独当证据用。
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

#: 流水线阶段序 —— 用于「更下游有产物 ⇒ 上游跑过」的推断。
_STAGES: tuple[str, ...] = (
    "context", "research", "triage", "debate", "votes", "pass0", "decision",
)

#: 走了兜底路由 / 回核判降级 / 回核判丢弃时，落进 ``source_routing`` 的留痕键。
#: 与 [context_node](agents/context_node.py) / [builder](common_context/builder.py) 同名常量对齐；
#: 此处**复制字符串而非 import**是刻意的 —— 本模块要能读**旧归档里的 dict**，
#: 那些 dict 不经过任何构造函数，import 常量只是为了名字好看、并不能保证一致。
#: 守护测试钉住两边相等（漂开即红）。
ROUTING_DEGRADED_KEYS: dict[str, tuple[str, str]] = {
    "__plan_degraded__": ("plan_fallback_routing", "取数计划没出来或全灭，退回按标签路由取数"),
    "__verification_degraded__": ("leg_verification_degraded", "有资料没达到计划要求，被降为通用背景"),
    "__verification_dropped__": ("leg_verification_dropped", "有资料没通过回核，被丢弃"),
    # BK.2 M1 #15（2026-09-15）：取数+回核超预算封顶时 context_node 一直往路由里写这个键，
    # 只是这张映射表里没有它 —— 于是「八位分析师在没有资料的情况下开会」在产物上与正常跑一样。
    # ⚠️ 这里只放**中性版**措辞（不对分析师开没开会下断言）。按下游实际走到哪另给两版，
    # 见 :func:`_budget_capped_text` —— 2026-09-16 #301 review：同一份汇总里
    # 「分析师靠工具现取」与「在价格闸提前停下、没进入完整分析」两句打架。
    "__budget_capped__": ("fetch_budget_capped", "取数+回核超过预算封顶被切断，本段产出的是空资料夹（没有拿到统一的背景材料）"),
}

#: 封顶后**分析师确实开了会** —— 他们手上没有统一材料，只能靠各自的工具现取。
_BUDGET_CAPPED_ANALYSTS_RAN = (
    "取数+回核超过预算封顶被切断，本段产出的是空资料夹 —— "
    "分析师手上没有统一的背景材料，只能靠各自的工具现取"
)
#: 封顶后**在价格闸提前停下** —— 空资料夹里连现价都没有，分析师根本没开会。
_BUDGET_CAPPED_EARLY_STOP = (
    "取数+回核超过预算封顶被切断，本段产出的是空资料夹 —— "
    "连这个标的的现价也没拿到，所以本次在价格闸提前停下，分析师没有开会"
)

#: 兜底报告的识别特征（[validation._build_fallback_report](schemas/validation.py) 写死的 headline 后缀）。
_FALLBACK_HEADLINE_MARK = "（兜底模式）"

#: 辩论 turn 解析失败时塞的占位正文特征（[base.make_debate_node](agents/base.py)）。
_DEBATE_PLACEHOLDER_MARK = "解析失败，已降级"

#: 投票解析失败时兜底票的理由字段特征（[base.make_vote_node](agents/base.py)·BK.2 M1 #29）。
#: 兜底票 = 中立 / 信念 1 / 观望，理由写死「DATA_INSUFFICIENT: 投票解析失败 (…)」——
#: 它进 tally、进归档，但从没人把它和「真投了中立票」分开过。
#:
#: 🔴 **2026-09-16 冷审收紧：判据从「含不含」改成「整段是不是以它开头」**。
#: 原先只要 reasoning 里**任何位置**出现这四个字就算兜底票，而 reasoning 是
#: **投票模型自由书写**的散文 —— 模型自己提一句「上一轮投票解析失败过」，
#: 一张真票就会被报成没解析出来。生产者写的是整段开头，按开头匹配既精确又不漏。
_VOTE_PARSE_FAILED_PREFIX = "DATA_INSUFFICIENT: 投票解析失败 ("

#: 决策论述某一节正文为空时塞的占位文字特征（[base.make_decision_node](agents/base.py)·BK.2 M1 #39）。
#: 生产者写的是「（<节标题>：核心观点待补充）」**当作整段正文**，进 thesis_sections 进归档。
#:
#: 🔴 **2026-09-16 冷审收紧：同上，从「含不含」改成「整段就是这个形状」**。
#: body 也是决策模型自由书写的散文，正文里写一句「此节核心观点待补充更多数据」
#: （而该节其实论证写满了）原先会被报成「这节没写出来」，直接误导读者。
#: ⇒ 判据 = 去掉首尾空白后，整段以全角左括号开头、以「：核心观点待补充）」结尾。
_SECTION_PLACEHOLDER_OPEN = "（"
_SECTION_PLACEHOLDER_TAIL = "：核心观点待补充）"


def _is_section_placeholder(body: str) -> bool:
    """这一节的正文**整段**就是占位文字（而不是正文里提到了这几个字）。"""
    b = body.strip()
    return b.startswith(_SECTION_PLACEHOLDER_OPEN) and b.endswith(_SECTION_PLACEHOLDER_TAIL)


@dataclass(frozen=True)
class DegradationEvent:
    """一条"这次退了一步"。

    - ``stage``：哪一段（:data:`_STAGES` 之一）
    - ``code``：机器可读的稳定码（给 gate / 统计用，别改字面量）
    - ``text``：给人读的一句话（**不带代码符号**，会直接印给用户）
    - ``evidence``：这条是从哪个字段推出来的（排查时照着去看）
    """

    stage: str
    code: str
    text: str
    evidence: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


# ---------------------------------------------------------------------------
# 兼容读取：state 里可能是对象（dataclass / pydantic），旧归档里是 dict
# ---------------------------------------------------------------------------

_MISSING = object()


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    """读一个字段，兼容对象与 dict；**读不到返回 default（默认 None）= 未知**。"""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    got = getattr(obj, name, _MISSING)
    return default if got is _MISSING else got


def _iter(obj: Any) -> list:
    return list(obj) if isinstance(obj, (list, tuple)) else []


# ---------------------------------------------------------------------------
# 阶段可达性
# ---------------------------------------------------------------------------

def _last_stage_with_output(state: dict) -> str | None:
    """最靠后的、确实产出了东西的阶段；None = 一段都没跑。

    ⚠️ 判据刻意**只认正向产物**（有东西 = 跑过），不认"某字段是 None"——
    后者恰恰是降级本身的信号，拿它判可达性就把两件事混在一起了。
    """
    if _attr(state, "final_decision") is not None:
        return "decision"
    if any(_attr(state, k) is not None
           for k in ("pass0_result", "ds_researcher_result", "ds_debate_result")):
        return "pass0"
    if _iter(_attr(state, "votes")):
        return "votes"
    if _iter(_attr(state, "debate_log")):
        return "debate"
    if _iter(_attr(state, "triage_verdicts")):
        return "triage"
    if any(k.endswith("_report") and state.get(k) is not None for k in state):
        return "research"
    if _attr(state, "common_context") is not None:
        return "context"
    return None


def reached_stages(state: dict) -> set[str]:
    """跑到过的阶段集合（含中途降级成 None 的那些）。"""
    last = _last_stage_with_output(state)
    if last is None:
        return set()
    return set(_STAGES[: _STAGES.index(last) + 1])


# ---------------------------------------------------------------------------
# 逐段推导
# ---------------------------------------------------------------------------

def _analysts_ran(state: dict) -> bool:
    """有**正向证据**表明分析师这一段真的跑过。

    ⚠️ 不能用 :func:`reached_stages` —— 价格闸早停也会产出 ``final_decision``，
    那里的「决策阶段已到达 ⇒ 前面各段都跑过」推断**恰好在这条路上不成立**。
    所以只认分析师自己的产物：任一份报告，或被分诊打回的记录。
    """
    if not isinstance(state, dict):
        return False
    if any(k.endswith("_report") and state.get(k) is not None for k in state):
        return True
    return bool(_iter(_attr(state, "rejected_roles")))


def _early_stopped(state: dict) -> bool:
    """价格闸早停**确实发生了**：早停标记为真，**且**分析师没有任何产物。

    🔴 **不能只看标记**（#301 冷审·2026-09-16）：「标记为真 ⇒ 流程在价格闸结束」
    这一环靠的是图里的路由（graph 里 build_context 之后那个条件分支），**不在 state 里**。
    路由哪天改成「缺现价也继续做定性分析」，只看标记的判断就会同时做错两件事：
    把真的「pass0 这一步没出结果」静音，并对用户说「分析师没有开会」。
    ⇒ 叠加正向证据 :func:`_analysts_ran`，让判断只依赖 state 自己。

    ⚠️ 与守护 ``test_price_gate_exit_cannot_reach_pass0_steps`` **互补而非重复**：
    本函数防的是「标记为真但分析师开了会」；那条防的是「早停后流程又去跑了 pass0」
    （那时分析师仍没开会，本函数照样判早停，只有图上的守护看得见）。
    """
    return _attr(state, "price_unavailable") is True and not _analysts_ran(state)


def _budget_capped_text(state: dict, default: str) -> str:
    """取数封顶那条按**下游实际走到哪**选措辞，不许对没发生的事下断言。

    - 价格闸早停确实发生（见 :func:`_early_stopped`）→ 分析师没开会；
    - 有分析师产物 → 他们靠各自的工具现取；
    - 两者都看不出（只跑到第一段 / 旧归档缺字段）→ 中性版，**不猜**。
    """
    if _early_stopped(state):
        return _BUDGET_CAPPED_EARLY_STOP
    if _analysts_ran(state):
        return _BUDGET_CAPPED_ANALYSTS_RAN
    return default


def _context_events(state: dict) -> list[DegradationEvent]:
    out: list[DegradationEvent] = []
    cc = _attr(state, "common_context")
    # 分类降级（BK.2 M1.5 修·2026-09-16）。
    # 🔴 **本条原先是死的**：落地时读的是 `state["query_classification"]`，而那个键
    # **全仓没有任何生产者**（`state.py` 里也没有）—— 于是从第一天起恒不触发，
    # 而登记表标着「已有留痕」= 把没做的说成做了，正是本模块要治的病换个地方复发。
    # 真因：`ClassificationResult` 不进 checkpoint，当年是靠**搬一趟**进 CommonContext
    # 才让名录对账留痕可见的（见 builder._ticker_resolution）；写本条时漏了这一趟。
    # ⇒ 修法照当年先例：builder._classification_source 把它搬进资料夹，这里改读那个字段。
    # ⚠️ 别再改回读 state 顶层 —— 守护 `test_classification_source_has_a_real_producer`
    # 会真的跑一次构建来钉住「这个字段有人写」，光有字面量不算数。
    source = _attr(cc, "classification_source")
    if source is not None and source != "llm":
        how = {"registry": "靠本地证券名录认出来的",
               "regex": "靠字符规则硬抓的（认不出中文公司名）",
               "default": "三层全落空，按主题类兜底"}.get(str(source), f"走的是 {source}")
        out.append(DegradationEvent(
            "context", "classify_degraded",
            f"问题分类没走模型主路径 —— {how}。",
            f"common_context.classification_source={source}"))

    routing = _attr(cc, "source_routing") or {}
    if isinstance(routing, dict):
        for key, (code, text) in ROUTING_DEGRADED_KEYS.items():
            if key in routing:
                reason = str(routing[key]).strip()
                if key == "__budget_capped__":
                    text = _budget_capped_text(state, text)
                out.append(DegradationEvent(
                    "context", code, f"{text}。" + (f"原因：{reason}" if reason else ""),
                    f"common_context.source_routing[{key!r}]"))

    for leg in _iter(_attr(cc, "legs")):
        if _attr(leg, "arrived") is False:
            src, tic = _attr(leg, "source", "?"), _attr(leg, "ticker")
            who = f"{src}{'·' + str(tic) if tic else ''}"
            out.append(DegradationEvent(
                "context", "leg_missing",
                f"有一份资料没取到（{who}）—— 计划里排了，实际没拿回来。",
                f"common_context.legs[key={_attr(leg, 'key', '?')}].arrived=False"))
    out += _registry_events(cc)
    out += _safety_price_leg_events(routing)
    out += _wisburg_events(cc)
    return out


# ---- BK.2 M2.4：只加读法（记录早在存档里、没人读·生产代码零改动）------------------

#: 名录对账「名录不可用」旗子（[reconcile.FLAG_UNAVAILABLE](security_registry/reconcile.py)）。
#: ⚠️ 复制字面量、不 import（本模块须能被登记检查脚本单独加载）；守护钉两边相等。
REGISTRY_UNAVAILABLE_FLAG = "registry_unavailable"


def _registry_events(cc: Any) -> list[DegradationEvent]:
    """名录不可用 —— 问题里的股票代码没经过名录核对（BK.2 M2.4 ①·名录链的**下端**）。

    旗子由对账写进 ``ticker_resolution.flags``、经资料夹进断点 / 归档，一直没人读。
    **名录链一件事两条**（拆解 M2.5）：本条是「这次有没有名录可用」，上端「哪个市场没拉到」由便条报。
    ⚠️ 已知缺口（登记表写明）：分类主路径失败、走兜底时不做对账、不写旗子 —— 那支由分类降级那条承接。
    📐 基线：在册 192 份记录、带对账留痕 71 份，**本旗子 0 次** ⇒ 零阳性样本，会响只由注入测试证。
    """
    flags = _attr(_attr(cc, "ticker_resolution"), "flags")
    if not isinstance(flags, (list, tuple)) or REGISTRY_UNAVAILABLE_FLAG not in flags:
        return []
    return [DegradationEvent(
        "context", "registry_unavailable",
        "本地证券名录这次不可用，问题里的股票代码没经过名录核对 —— 代码写错、认错公司这次都不会被纠正。",
        f"common_context.ticker_resolution.flags ∋ {REGISTRY_UNAVAILABLE_FLAG}")]


#: 补价腿的路由说明尾巴（[validator.ensure_price_leg](retrieval_plan/validator.py) 写进 purpose、
#: 再经 builder.sources_from_plan 进 source_routing）。⚠️ 复制字面量；守护扫生产者源码钉住。
#: 🔴 **按「结尾整段相等」匹配、不按「含不含」**：路由里其余腿的说明是**取数规划员（模型）自由书写**的，
#: 按片段匹配会把模型碰巧写的同样字眼报成兜底（#301 冷审：判据锚在散文会漂）。
SAFETY_PRICE_LEG_SUFFIX = "（个股问题的行情腿：计划里没有，按安全兜底补）"


def _safety_price_leg_events(routing: Any) -> list[DegradationEvent]:
    """个股问题的行情腿是系统按安全兜底补的（BK.2 M2.4 ②）。

    补腿本身成功时**数据不缺**，缺的是「计划里本没有这条腿」这件事的可见性（归档的计划里查无此腿）。
    ⇒ 属规划质量信号、不影响结论 ⇒ **只进排查报告**（:data:`TRACE_ONLY_CODES`）。
    📐 基线：在册 192 份 **0 次** ⇒ 零阳性样本。
    """
    if not isinstance(routing, dict):
        return []
    keys = sorted(k for k, v in routing.items()
                  if isinstance(v, str) and v.endswith(SAFETY_PRICE_LEG_SUFFIX))
    if not keys:
        return []
    return [DegradationEvent(
        "context", "price_leg_safety_added",
        f"取数计划漏了个股的行情腿，系统按安全兜底补上了（{'、'.join(keys)}）—— 数据没缺，"
        "只是这份计划本身不完整。",
        "common_context.source_routing[*] 以兜底补腿说明结尾")]


def _wisburg_events(cc: Any) -> list[DegradationEvent]:
    """研报库三种兜底 + 摘要取失败（BK.2 M2.4 ③④）。**与回核已报的那条去重**。

    回核（[verifier._verify_wisburg](retrieval_plan/verifier.py)）读得到：库名认不出 / 工具回退 /
    「要了摘要却一篇都没取到」—— 这三件在回核跑过时已由「有资料没达到计划要求」那条报出。
    ⇒ 这里只补回核**读不到**的：
      - 深度认不出（回核从不读）；
      - 摘要**部分**没取到（回核只看「一篇都没有」）；
      - 回核**没跑**这条腿时（腿上无结论、且元信息里没有回核写的保留篇数）的全部三件。
    📐 基线：在册 52 份研报记录，四种标记 **全 0 次** ⇒ 零阳性样本。
    """
    payload = _attr(cc, "payload")
    if not isinstance(payload, dict):
        return []
    out: list[DegradationEvent] = []
    for leg in _iter(_attr(cc, "legs")):
        if _attr(leg, "source") != "wisburg":
            continue
        key = _attr(leg, "key")
        meta = _attr(payload.get(key), "_meta") if key in payload else None
        if not isinstance(meta, dict):
            continue
        # 🔴 「回核跑没跑」锚在**回核自己写的字段**上，不锚在腿的回核结论上（2026-09-18 量出）：
        # 在册存档里 41 条研报腿回核明明跑过（元信息里有回核写的 verified_kept），腿上的结论却是空 ——
        # 那些是旧格式存档补推出来的腿、结论一律为空。只看结论会把这 41 条全部重复报一遍。
        verified = _attr(leg, "verification_status") is not None or "verified_kept" in meta
        what: list[str] = []
        if meta.get("depth_fallback") is not None:
            what.append(f"要的检索深度认不出（{meta['depth_fallback']!r}），按只取标题处理")
        if not verified and meta.get("library_fallback") is not None:
            what.append(f"点名的研报库认不出（{meta['library_fallback']!r}），改查了默认库")
        if not verified and meta.get("tool_fallback") is not None:
            what.append("查询工具对不上、换了别的工具，列表其实来自别的库、且没取摘要")
        failed = meta.get("summary_failures")
        got = meta.get("summaries")
        n_fail = len(failed) if isinstance(failed, list) else 0
        n_got = len(got) if isinstance(got, list) else 0
        if n_fail and (n_got or not verified):
            what.append(f"有 {n_fail} 篇研报摘要没取到（取到 {n_got} 篇）")
        if what:
            out.append(DegradationEvent(
                "context", "wisburg_partial_fallback",
                f"研报库这条腿（{key}）有退路：" + "；".join(what) + "。",
                f"common_context.payload[{key!r}]._meta"))
    return out


def _research_events(state: dict) -> list[DegradationEvent]:
    out: list[DegradationEvent] = []
    for key in sorted(k for k in state if k.endswith("_report")):
        rep = state.get(key)
        if rep is None:
            continue
        role = str(_attr(rep, "role", key[: -len("_report")]))
        headline = str(_attr(rep, "headline", "") or "")
        if _FALLBACK_HEADLINE_MARK in headline:
            out.append(DegradationEvent(
                "research", "analyst_fallback_report",
                f"{role} 这一路的报告没写成，用的是兜底版（模型输出没解析出来）。",
                f"{key}.headline"))
        if _attr(rep, "truncated_at_chunk") is not None:
            out.append(DegradationEvent(
                "research", "analyst_truncated",
                f"{role} 这一路的报告是截断的 —— 续写没接上，后半段丢了。",
                f"{key}.truncated_at_chunk"))
    rejected = [str(r) for r in _iter(_attr(state, "rejected_roles"))]
    if rejected:
        out.append(DegradationEvent(
            "triage", "analyst_rejected",
            f"有 {len(rejected)} 路分析被质量审核打回且没能补救（{'、'.join(rejected)}）"
            f"—— 后面的辩论和投票少了这几路的输入。",
            "rejected_roles"))
    # 质量审核自己出故障的两种（BK.2 #59 / #58·2026-09-15）。
    # 区别于上面那条：上面是「审了、判不合格」，这两条是「**根本没审成**」——
    # 而没审成在产物上与「审过、没问题」长得一模一样。
    # 🔴 **按角色去重**（合并前 review 坐实·2026-09-15）：分诊节点随返工循环重跑（最多 3 轮·
    # `graph.py`「Never skip-wrap these two」），而 ``enforcement_log`` 是累加型 state 键
    # ⇒ 同一个角色的 C 类连着失败会留下多条痕。直接数条数会把「1 路连失败 3 轮」说成
    # 「3 路没跑成」—— 在**专门用来讲实话**的降级汇总里虚报影响面。
    roles_c = sorted({str(_attr(e, "role", "?")) for e in _iter(_attr(state, "enforcement_log"))
                      if _attr(e, "rule") == "triage-c-class"
                      and _attr(e, "action") == "skipped_failed"})
    if roles_c:
        out.append(DegradationEvent(
            "triage", "triage_c_class_skipped",
            f"有 {len(roles_c)} 路分析的深度质量检查没跑成（{'、'.join(roles_c)}）"
            "—— 这一步这次没生效，不代表检查通过了。",
            "enforcement_log[rule=triage-c-class]"))
    # #58：这条记录**早就在写**（审核出异常时判定直接写成 warning + 一条 `triage error:` 备注），
    # 只是没有消费面 —— 同 #41 的形态，故生产者零改动、这里只加读法。
    failed_roles = [str(_attr(v, "role", "?")) for v in _iter(_attr(state, "triage_verdicts"))
                    if any(str(n).startswith("triage error:") for n in _iter(_attr(v, "notes")))]
    if failed_roles:
        out.append(DegradationEvent(
            "triage", "triage_report_failed",
            f"有 {len(failed_roles)} 路分析的质量审核整个跑挂了（{'、'.join(failed_roles)}）"
            "—— 这几路这次没被审过。",
            "triage_verdicts[].notes"))
    return out


def _debate_events(state: dict) -> list[DegradationEvent]:
    out: list[DegradationEvent] = []
    for turn in _iter(_attr(state, "debate_log")):
        side, rnd = _attr(turn, "side", "?"), _attr(turn, "round", "?")
        if _DEBATE_PLACEHOLDER_MARK in str(_attr(turn, "content", "") or ""):
            out.append(DegradationEvent(
                "debate", "debate_placeholder",
                f"辩论第 {rnd} 轮 {side} 方这一发言没解析出来，用的是占位文字。",
                f"debate_log[round={rnd},side={side}].content"))
        if _attr(turn, "truncated_at_chunk") is not None:
            out.append(DegradationEvent(
                "debate", "debate_truncated",
                f"辩论第 {rnd} 轮 {side} 方的发言是截断的。",
                f"debate_log[round={rnd},side={side}].truncated_at_chunk"))
    return out


def _vote_events(state: dict) -> list[DegradationEvent]:
    """投票解析失败 → 兜底票（BK.2 M1 #29·2026-09-15）。

    生产者零改动：[base.make_vote_node](agents/base.py) 在 Vote 校验失败时一直会投一张
    中立兜底票、理由写明「投票解析失败」，**只是没人读**。不读的后果：tally 里多一张中立票，
    看起来像「这位分析师真的没倾向」。按角色去重（同 triage 那两条的理由）。
    """
    roles = sorted({str(_attr(v, "role", "?")) for v in _iter(_attr(state, "votes"))
                    if str(_attr(v, "reasoning", "") or "").strip()
                    .startswith(_VOTE_PARSE_FAILED_PREFIX)})
    if not roles:
        return []
    return [DegradationEvent(
        "votes", "vote_parse_failed",
        f"有 {len(roles)} 位分析师的投票没解析出来（{'、'.join(roles)}），按兜底投了中立票"
        "—— 这不是他们真实的倾向，票数统计里这几票请打折看。",
        "votes[].reasoning")]


def _pass0_events(state: dict, reached: set[str]) -> list[DegradationEvent]:
    """⚠️ 只在**决策已产出**时判 —— 否则 None 只是"还没跑到"。"""
    if "decision" not in reached:
        return []
    # 价格闸早停（#301 review 顺带查出·2026-09-16）：那条路是 取数 → 价格闸早停 → 结束，
    # 事实清单整理与两个辅助助理**根本没被排上**。但早停节点照样产出 final_decision，
    # 于是上面「决策到了 ⇒ 前面都跑过」在这里不成立 —— 三条「这一步没出结果、决策是在
    # 缺这份材料的情况下做的」全是假的（既没缺材料，也没做决策）。
    # ⚠️ 只认 `is True`：旧归档没有这个键 = 未知，按正常跑判，不许把真降级一并静音。
    # 🔴 **判「早停确实发生」不能只看标记**（#301 冷审）—— 用 :func:`_early_stopped`，
    # 叠加「分析师没有产物」这条正向证据；图上的守护
    # `test_price_gate_exit_cannot_reach_pass0_steps` 仍保留，两者防的不是同一种变化。
    if _early_stopped(state):
        return []
    out: list[DegradationEvent] = []
    for key, code, who in (
        ("pass0_result", "pass0_missing", "事实清单整理"),
        ("ds_researcher_result", "ds_researcher_missing", "辅助研究助理"),
        ("ds_debate_result", "ds_debate_missing", "辅助辩论助理"),
    ):
        if _attr(state, key) is None:
            out.append(DegradationEvent(
                "pass0", code,
                f"{who}这一步没出结果（超时或失败），决策是在缺这份材料的情况下做的。",
                f"{key} is None"))
    return out


def _evid1_events(state: Any) -> list[DegradationEvent]:
    """决策正文里的幻觉引用被剥掉 —— **只加读法**（BK.6·2026-09-22·生产者零改动）。

    写入点：[base.py 决策节点](agents/base.py) 剥掉不在有效清单里的 v# / f# 引用后，
    往执法记录追加 ``{"rule": "EVID-1", "action": "strip", "detail": …, "refs": […]}``。
    读者此前只有终局质检 Q5（算比例定 PASS / WARN / FAIL）；本汇总一直没读 ⇒ 产物被改了、
    「本次退了哪几步」却不提。这里只报事实，不算比例、不改剥除。
    📐 基线：在册 29 个带执法记录的 run 里 **0 条**（bk6 证据 §0.1）⇒ 会响只由合成靶测证。
    """
    out: list[DegradationEvent] = []
    for entry in _iter(_attr(state, "enforcement_log")):
        if _attr(entry, "rule") != "EVID-1" or _attr(entry, "action") != "strip":
            continue
        refs = ", ".join(str(r) for r in _iter(_attr(entry, "refs")))[:120]
        out.append(DegradationEvent(
            "decision", "hallucinated_refs_stripped",
            "决策正文里引用了不存在的证据编号，已被剥掉 —— 那几处论述失去了出处。"
            + (f"编号：{refs}" if refs else ""),
            "enforcement_log[rule=EVID-1,action=strip]"))
    return out


def _decision_events(state: dict) -> list[DegradationEvent]:
    out: list[DegradationEvent] = []
    d = _attr(state, "final_decision")
    if _attr(d, "prose_gate_status") == "degraded":
        out.append(DegradationEvent(
            "decision", "prose_gate_degraded",
            "正文里的具体价位被抹掉了 —— 支撑这些数字的证据没达到核验要求。",
            "final_decision.prose_gate_status"))
    if _attr(state, "price_unavailable") is True:
        routing = _attr(_attr(state, "common_context"), "source_routing") or {}
        capped = isinstance(routing, dict) and "__budget_capped__" in routing
        # 2026-09-16 #301 review：取数被预算封顶切断时，现价拿不到是**结果不是原因** ——
        # 原措辞「拿不到这个标的的实时行情」会让人去查行情源，而行情源可能好好的。
        # 🔴 **但也不许反过来断言「不是行情源的问题」**（#301 冷审）：封顶后资料夹是空的，
        # 价格闸**必然**跳闸，这条路上行情源到底有没有报价**从来没被看过**。而把 20 秒
        # 预算耗光的，恰恰常是行情源在一只拿不到报价的票上反复重试 —— 否定它等于把人
        # 从真正的原因上引开。⇒ 只断言能担保的那半，另一半明说无从得知。
        out.append(DegradationEvent(
            "decision", "price_unavailable",
            ("本次在价格闸提前停下，没有进入完整分析 —— 直接原因是取数被预算封顶切断"
             "（见取数那一条）：资料夹是空的，价格闸必然跳闸。"
             "行情源本身有没有这只标的的报价，这次无从得知。") if capped else
            ("这个标的所在的市场 / 代码形态当前版本不支持行情，本次在价格闸提前停下，"
             "没有进入完整分析；重新运行不会改变结果。")
            if _attr(state, "price_unavailable_reason") == "unsupported_market" else
            "拿不到这个标的的实时行情，本次在价格闸提前停下，没有进入完整分析。",
            "price_unavailable"))
    for entry in _iter(_attr(state, "enforcement_log")):
        if _attr(entry, "rule") != "evidence-mismatch-review":
            continue
        detail = str(_attr(entry, "detail", "") or "")
        if "未配置复核员" in detail or "复核 skipped" in detail:
            out.append(DegradationEvent(
                "decision", "review_skipped",
                "有证据对不上账，但复核这一步没能进行（没有可用的独立复核模型），按最保守处理、维持拦截。",
                "enforcement_log[rule=evidence-mismatch-review]"))
            break
    # 誊写核查 fail-open（BK.2 提前批 #41·2026-09-15）。
    # ⚠️ 这条记录**早就在写** —— [base._apply_ai_transcription_check](agents/base.py) 的
    # except 分支一直往 enforcement_log 里放一条 skipped_fail_open，**只是从来没有消费面**。
    # 于是「核查跑了、数字都对得上」与「核查根本没跑成」在产物上一模一样 = 把没检查说成检查过了。
    # 本处**只加读法**：核查那段代码一个字未动（用户 2026-09-15 裁：只加留痕、不动判定）。
    # ⇒ BK.0 盘点把本处记为「只写日志」有误，实为「有结构化记录、无人读」，盘点已订正。
    for entry in _iter(_attr(state, "enforcement_log")):
        if (_attr(entry, "rule") == "ai-transcription-check"
                and _attr(entry, "action") == "skipped_fail_open"):
            out.append(DegradationEvent(
                "decision", "transcription_check_skipped",
                "誊写核查这一步没能进行 —— 报告里的数字这次没有逐个回去比对出处，"
                "这不等于比对通过；承重数字请人工核对。",
                "enforcement_log[rule=ai-transcription-check]"))
            break
    # EXEC-FLOOR 信号算不出（BK.2 提前批 #43·2026-09-15）。
    # 治的病：算不出 → 按不触发放行，产物里「没踩线」与「没算出来」长得一模一样。
    # 生产者 = [risk_gate 的 hard_block 节点](agents/risk_gate.py) 的 except 分支；
    # 那里的放行判定一个字未改，只多写了这条记录。
    for entry in _iter(_attr(state, "enforcement_log")):
        if (_attr(entry, "rule") == "exec-floor-signal"
                and _attr(entry, "action") == "skipped_compute_failed"):
            out.append(DegradationEvent(
                "decision", "exec_floor_signal_failed",
                "执行价位的安全信号这次没算出来，本次按「未触发」放行 —— "
                "这不等于查过并且没问题；带价位的建议请人工复核。",
                "enforcement_log[rule=exec-floor-signal]"))
            break
    # 决策前事实核验失败（BK.2 提前批 #36·2026-09-15）。
    # 治的病：核验跑不成 → 交出**空的问题清单**，而空清单读起来就是「查过了、没发现问题」。
    # 生产者 = [base._run_verification](agents/base.py) 的 except 分支（判定不变：仍返回空、仍不阻断）。
    # ⚠️「清单里本来就没有要查的项」也返回空，那是正常结果、不发记录 —— 两者必须分得开。
    for entry in _iter(_attr(state, "enforcement_log")):
        if (_attr(entry, "rule") == "fund-mgr-verification"
                and _attr(entry, "action") == "skipped_failed"):
            out.append(DegradationEvent(
                "decision", "fact_verification_failed",
                "决策前的事实核验这次没能进行 —— 报告里那份「核验问题清单」是空的，"
                "空不代表没问题，只代表这一步没做成。",
                "enforcement_log[rule=fund-mgr-verification]"))
            break
    # 决策论述某节正文空 → 占位（BK.2 M1 #39·2026-09-15）。
    # 生产者零改动：[base.make_decision_node](agents/base.py) 解析不到某节 body 时一直塞
    # 「（<节标题>：核心观点待补充）」进 thesis_sections、进归档，**只是没人读** ——
    # 读者看到的是一节写着"待补充"的论述，没人告诉他这节本来该有内容、是模型没写出来。
    empty = [str(_attr(s, "title", None) or _attr(s, "id", "?"))
             for s in _iter(_attr(d, "thesis_sections"))
             if _is_section_placeholder(str(_attr(s, "body", "") or ""))]
    if empty:
        out.append(DegradationEvent(
            "decision", "thesis_section_placeholder",
            f"决策论述有 {len(empty)} 节没写出来（{'、'.join(empty)}），正文是占位文字"
            "—— 这几节的论证这次是缺的，不是「没什么可说」。",
            "final_decision.thesis_sections[].body"))
    out += _outline_suspected_events(state, d)
    out += _broken_reference_events(d)
    out += _evid1_events(state)
    return out


#: 正常路径的论述段数下界：大纲过 3–5 门、合成段封顶 5 ⇒ 正常 ≥ 3；退路是 1 段，或合成段 1–2 + 单段。
#: ⚠️ 这是**下界判据**：合成段两条 + 单段 = 3 段的退路读不出来（新跑批靠便条，不靠这条）。
_OUTLINE_MIN_NORMAL_SECTIONS = 3


def _outline_suspected_events(state: dict, d: Any) -> list[DegradationEvent]:
    """论述段数偏少 → 「疑似大纲退成单段」（BK.2 P0.3·**给没有便条的旧存档用的读法**）。

    - 有同码便条 ⇒ 以便条为准，这里不报（不双报）；
    - 价格闸早停的决策本就一段 ⇒ 不报（复用 :func:`_early_stopped`）；
    - ``thesis_sections`` 缺失 / 不是列表 / 为空 ⇒ **未知**，不报。

    📐 **定档依据**（2026-09-17 回放 origin/main 在册 192 份·其中带决策 29 份）：命中 **4 份、逐份核为真**
    —— 四份原因完全相同：模型给了合法 5 段，但查证清单里有档位值不合法，装配校验失败、连带整份大纲作废
    （3 份用归档里的大纲原始输出复现；1 份无调用记录，从排查报告里读到同样的原始输出）；**假阳性 0**。
    措辞仍只说「疑似」：段数少是结果，这条读法**看不见原因**。
    """
    secs = _attr(d, "thesis_sections")
    if not isinstance(secs, (list, tuple)) or not secs:
        return []
    if len(secs) >= _OUTLINE_MIN_NORMAL_SECTIONS or _early_stopped(state):
        return []
    if any(_attr(e, "rule") == NOTE_RULE and _attr(e, "action") == "decision_outline_fallback"
           for e in _iter(_attr(state, "enforcement_log"))):
        return []
    return [DegradationEvent(
        "decision", "decision_outline_suspected",
        f"决策论述只有 {len(secs)} 段（正常是 3–5 段）—— 疑似大纲没生成出来、退成了单段。"
        "这份记录生成时还没有这类留痕，具体原因无从确认。",
        "final_decision.thesis_sections（段数）")]


#: 正文里的引用标记。⚠️ **刻意复制字面量、不 import**（本模块须能被登记检查脚本单独加载）。
#: 源头三条：[base._REF_PATTERN / _WEB_REF_PATTERN / _VER_REF_PATTERN](agents/base.py)
#: 与 [stamp_check.STAMP_RE](facts/stamp_check.py) —— 源头**没有任何归一步骤**（不忽略大小写、
#: 不容忍空格、不拆连写），就是「花括号 + ref: + 一个字母族 + 数字」的严格字面；这里取三族并集。
#: 守护 ``test_ref_mark_pattern_matches_its_sources`` 用同一批正反样本钉住两边判定一致（改副本即红）。
_REF_MARK_RE = re.compile(r"\{ref:([fvw]\d+)\}")

#: 扫哪些地方找引用：决策里**除了**清单自己与核查明细之外的全部文字
#: （回放实测引用出现在论述正文 / 少数派意见 / 触发事件 / 风险 / 执行计划备注）。
_REF_SCAN_SKIP_KEYS = frozenset({"references_appendix", "claim_audits"})


def _collect_ref_marks(obj: Any, out: set[str]) -> None:
    if isinstance(obj, str):
        out.update(m.group(1) for m in _REF_MARK_RE.finditer(obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k not in _REF_SCAN_SKIP_KEYS:
                _collect_ref_marks(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _collect_ref_marks(v, out)


def _broken_reference_events(d: Any) -> list[DegradationEvent]:
    """正文引用了、文末清单里查不到 = 断掉的引用（BK.2 P0.4·效果检查·**只记录不判定**）。

    ⚠️ **只许说「门后残存的断链」**：扫的是**最终**决策（验章门剥过、价位门控折叠过之后），
    门前就被剥掉的引用这里看不见，也不该看见。
    ⚠️ **清单缺失 / None / 空 → 未知，不报**（用户 2026-09-17 裁 D）：旧存档整块没有清单是常态，
    「读不到清单」折成「全部断链」会把每一份旧存档都报红。

    📐 **定档依据**（2026-09-17 回放 origin/main 在册 192 份·带决策 29 份·29 份全有清单）：
    命中 **0 份** ⇒ **零阳性样本：它会不会响只由注入测试证明**，回放只证明它不乱响。
    ⇒ 档位 = 只进排查报告、**不进用户面**（:data:`TRACE_ONLY_CODES`）。
    """
    if d is None:
        return []
    if hasattr(d, "model_dump"):
        d = d.model_dump()
    if not isinstance(d, dict):
        return []
    appendix = d.get("references_appendix")
    if not isinstance(appendix, (list, tuple)) or not appendix:
        return []
    listed = {str(_attr(e, "ref_id")) for e in appendix}
    cited: set[str] = set()
    _collect_ref_marks(d, cited)
    broken = sorted(cited - listed, key=lambda r: (r[0], int(r[1:])))
    if not broken:
        return []
    return [DegradationEvent(
        "decision", "broken_reference",
        f"正文里有 {len(broken)} 处引用在文末的证据清单里查不到（{'、'.join(broken)}）"
        "—— 这是各道核查之后仍留在正文里的断链，读者顺着编号找不到出处。",
        "final_decision 正文引用编号 − references_appendix[].ref_id")]


def _note_events(state: dict, reached: set[str]) -> list[DegradationEvent]:
    """收集器便条 → 降级事件（BK.2 M0 的通用派生）。

    与上面那些「一条规则一段代码」的派生**刻意不同**：深层代码只发一个码，
    人话统一取自 :data:`NOTE_CODES`。前两批每处自带字面量守护，25 处照那样做
    会产出 25 套、不可维护 —— 这是本机制存在的理由。

    ⚠️ **码不在表里也要报**（而不是静默丢）：那是「登记漏了」的接线错误，
    与本域要治的病同形态。报出来时显式标明码未登记。
    ⚠️ **同一个码在同一阶段只报一条** —— 三处基本面拉取都失败时是一件事，不是三件。

    🔑 **阶段从「哪个环节记的」推**（BK.2 M2.2·2026-09-17）：同一个码（如工具循环退成不带工具）
    会从分析师、决策、取数三类环节发出，码表里「一码一阶段」撑不住 ⇒ 便条带 ``node`` 时按
    :data:`NODE_STAGES` 定阶段、**合并键 = (码, 阶段)**；不带 ``node`` 的旧便条仍按码表阶段
    （旧归档回放逐字不变）。带 ``node`` 时人话后面列出涉及的环节名 —— 名字**从环节名映射**，
    不解析 detail 文本（#301 冷审：判据锚在散文会漂）。
    """
    groups: dict[tuple[str, str], list[str | None]] = {}
    for entry in _iter(_attr(state, "enforcement_log")):
        if _attr(entry, "rule") != NOTE_RULE:
            continue
        code = str(_attr(entry, "action", "") or "")
        if not code:
            continue
        node = _attr(entry, NOTE_NODE_KEY)
        node = str(node) if node else None
        stage = stage_of_node(node) if node else None
        if stage is None:
            stage = NOTE_CODES.get(code, ("context", ""))[0]
        if stage not in reached:
            stage = "context"
        groups.setdefault((code, stage), []).append(node)
    out: list[DegradationEvent] = []
    for (code, stage), nodes in groups.items():
        text = NOTE_CODES.get(code, ("context", f"有一处退了一步，但这个码（{code}）没在码表里登记。"))[1]
        n = len(nodes)
        named = sorted({nd for nd in nodes if nd})
        evidence = f"enforcement_log[rule={NOTE_RULE}, action={code}]"
        if named:
            labels = "、".join(dict.fromkeys(node_label(nd) for nd in named))
            text += f"（{n} 处：{labels}）" if n > 1 else f"（{labels}）"
            evidence += f", node={','.join(named)}"
        elif n > 1:
            text += f"（{n} 处）"
        out.append(DegradationEvent(stage, code, text, evidence))
    return out


#: 便条里记「是哪个环节记的」的键。⚠️ 与 [degradation_notes.NODE_KEY](degradation_notes.py)
#: **刻意复制字面量、不 import**（本模块要能被登记检查脚本单独加载）；守护钉住两边相等。
NOTE_NODE_KEY = "node"

#: 环节名 → (阶段, 给人看的名字)。**流程图里每个环节都必须能在这里或下面的前缀族里查到**
#: —— 查不到时便条会悄悄退回码表阶段，正是本域要治的「悄悄」。守护从**编译后的图**取全部
#: 环节名逐个核（不从源码字面量取·防改名漏网）。
NODE_STAGES: dict[str, tuple[str, str]] = {
    "build_context": ("context", "取数"),
    "price_unavailable": ("decision", "价格闸"),
    "research_done": ("research", "研究汇合"),
    "triage": ("triage", "质量审核"),
    "rework_dispatcher": ("triage", "返工重跑"),
    "triage_passed": ("triage", "审核放行"),
    "debate_done": ("debate", "辩论汇合"),
    "ds_researcher": ("pass0", "辅助研究助理"),
    "ds_debate": ("pass0", "辅助辩论助理"),
    "ds_merge": ("pass0", "事实清单整理"),
    "audit_pass_0_5": ("pass0", "事实核查"),
    "risk_gate_pre_check": ("decision", "风控预检"),
    "fund_manager": ("decision", "决策经理"),
    "risk_gate_check": ("decision", "风控检查"),
    "risk_gate_response": ("decision", "风控回应"),
    "execution_stage_hard_block": ("decision", "执行期硬拦"),
}

#: 按前缀归段的环节族：(前缀, 阶段, 名字模板)。精确表优先（``debate_done`` 不落进辩论族）。
_NODE_PREFIX_STAGES: tuple[tuple[str, str, str], ...] = (
    ("analyst_", "research", "{role}"),
    ("vote_", "votes", "{role}投票"),
    ("debate_", "debate", "辩论"),
)


def stage_of_node(node: str | None) -> str | None:
    """环节名 → 阶段；查不到返回 None（调用方退回码表阶段·守护保证生产里查得到）。"""
    if not node:
        return None
    if node in NODE_STAGES:
        return NODE_STAGES[node][0]
    for prefix, stage, _tmpl in _NODE_PREFIX_STAGES:
        if node.startswith(prefix):
            return stage
    return None


def node_label(node: str) -> str:
    """环节名 → 给人看的名字。查不到就原样返回环节名（不编造）。"""
    if node in NODE_STAGES:
        return NODE_STAGES[node][1]
    for prefix, _stage, tmpl in _NODE_PREFIX_STAGES:
        if node.startswith(prefix):
            return tmpl.format(role=_role_name_zh(node[len(prefix):]))
    return node


def _role_name_zh(role: str) -> str:
    """角色键 → 中文名。**函数内按需读配置**：本模块须保持能被登记检查脚本单独加载
    （顶层不许 import 包内模块），读不到就原样返回角色键。"""
    try:
        from committee.config import ROLES  # noqa: PLC0415 — 刻意延迟导入，见 docstring
        meta = ROLES.get(role)
        return getattr(meta, "name_zh", None) or role
    except Exception:  # noqa: BLE001 — 取不到名字不许影响汇总
        return role


def _cost_events(token_usage: Any) -> list[DegradationEvent]:
    out: list[DegradationEvent] = []
    if _attr(token_usage, "partial_cost") is True:
        out.append(DegradationEvent(
            "cost", "cost_partial",
            "本次花费算不全 —— 有模型不在价目表里，账面数字偏低。",
            "token_usage.partial_cost"))
    unpriced = [str(m) for m in _iter(_attr(token_usage, "unpriced_models"))]
    if unpriced:
        out.append(DegradationEvent(
            "cost", "cost_unpriced",
            f"有 {len(unpriced)} 个模型没有价格（{'、'.join(unpriced)}），它们的花费按 0 计。",
            "token_usage.unpriced_models"))
    stale = [str(m) for m in _iter(_attr(token_usage, "stale_price_models"))]
    if stale:
        out.append(DegradationEvent(
            "cost", "cost_stale_price",
            f"有 {len(stale)} 个模型的价格已过重核期限（{'、'.join(stale)}），算出来的钱多半不准。",
            "token_usage.stale_price_models"))
    return out


# ---------------------------------------------------------------------------
# 对外
# ---------------------------------------------------------------------------

def degradation_summary(state: dict, token_usage: Any = None) -> list[DegradationEvent]:
    """本跑退了哪几步。**纯读，不改 state 一个字节。**

    Args:
        state: 流水线 state（或从断点 / 归档读回来的 dict —— 字段缺失一律当未知）。
        token_usage: ``tracker.to_dict()`` 的结果；不传则从 ``state["_token_usage"]`` 找。

    Returns:
        按阶段序排好的事件列表。空列表 = **在本模块看得见的范围内**没有降级
        —— 不等于"整跑没退过路"（还有一批只写日志的点本模块看不见，见 BK.0 §3.0）。
    """
    if not isinstance(state, dict):
        return []
    reached = reached_stages(state)
    events: list[DegradationEvent] = []
    if "context" in reached:
        events += _context_events(state)
    if "research" in reached:
        events += _research_events(state)
    if "debate" in reached:
        events += _debate_events(state)
    if "votes" in reached:
        events += _vote_events(state)
    events += _pass0_events(state, reached)
    if "decision" in reached:
        events += _decision_events(state)
    events += _note_events(state, reached)
    events += _cost_events(token_usage if token_usage is not None else state.get("_token_usage"))

    order = {s: i for i, s in enumerate((*_STAGES, "cost"))}
    events.sort(key=lambda e: (order.get(e.stage, 99), e.code))
    return events


def render_markdown(events: list[DegradationEvent]) -> str:
    """给用户看的一节。**无降级时返回空串**（每跑都印一句"本次无降级"会让真有降级那次淹掉）。"""
    events = [e for e in events if e.code not in TRACE_ONLY_CODES]
    if not events:
        return ""
    lines = ["\n## 本次降级提示",
             "",
             f"这次分析过程中有 {len(events)} 处退而求其次的地方，结论请结合这些情况看：",
             ""]
    lines += [f"- {e.text}" for e in events]
    lines.append("")
    lines.append("> 这一节只列**看得见的**降级；系统里还有一些退路目前只写在日志里。")
    return "\n".join(lines)


def render_trace_block(events: list[DegradationEvent]) -> list[str]:
    """trace.md 报告头里的一块（照 BJ.3 配置漂移块的写法：没有就一行都不加）。"""
    if not events:
        return []
    out = ["", f"> ⚠️ **本跑降级 {len(events)} 处**（只列有结构化留痕的；"
                "只读不拦·backlog BK.1）："]
    out += [f"> - `{e.code}`（{e.stage}）{e.text}　↖ {e.evidence}" for e in events]
    return out


# ---------------------------------------------------------------------------
# 降级点登记表（BK.3）—— 沉默 = 失败
# ---------------------------------------------------------------------------
#
# **为什么要这张表**：BK.0 盘点查明大半的降级点产物里看不见（实数见 BK.0 §3.0）。今天补不完（BK.2 逐点裁），
# 但**不能让"今天补不完"变成"将来新加的也没人管"**。这张表把每个降级日志点的处置显式写下来，
# [lint_degradation_registry.py](../../scripts/lint_degradation_registry.py) 扫出没登记的就喊。
#
# ⚠️ **它不是"按关键词认降级"的清单**（那是开放词表、必漏，坑扫描④）：词表只用来**提问**
# 「这个点你登记了吗」，答案由人写在这里。新加一个降级日志 → 没登记 → 闸门点名 → 人来判它属哪档。
#
# 键 = ``相对路径:函数名``（**不用行号** —— 行号一改动就漂，守护会变成噪音）。
# 值三档，前缀区分：
#   ``code:<推导码>``  —— 已有结构化留痕，:func:`degradation_summary` 能派生出来
#   ``pending:<理由>`` —— 确是降级但今天只有日志，**待 BK.2 补痕**（理由要写清退的是什么）
#   ``exempt:<理由>``  —— 不算降级（重试中间态 / 会炸不静默 / 纯信息），理由 ≥15 字
_MIN_REASON_CHARS = 15

#: 收集器便条在 ``enforcement_log`` 里的 rule 值。
#: ⚠️ **刻意复制字面量、不 import** [degradation_notes](degradation_notes.py) ——
#: 本模块被 [登记检查脚本](../../scripts/lint_degradation_registry.py) **单独加载**
#: （CI 那个 job 只有 checkout、不装包），一旦 import 包内模块，CI 立刻起不来。
#: 同 :data:`ROUTING_DEGRADED_KEYS` 的理由。守护 `test_note_rule_matches_its_source` 钉住两边相等。
NOTE_RULE = "degradation"

#: 收集器便条的码表（BK.2 M0）—— `code → (阶段, 给人读的一句话)`。
#:
#: **为什么措辞放这里、不放调用点**：同一个码可能在好几个调用点发出（比如三处基本面拉取），
#: 措辞写在调用点必然漂移；放一张表则「接一个新点 = 代码一行 + 这里一行」。
#: 守护 `test_note_codes_cover_all_call_sites` 扫源码比对：**用了没登记的码 → 红**。
#:
#: ⚠️ 阶段取 :data:`_STAGES` 之一 —— 它决定这条降级印在汇总的哪一段。
NOTE_CODES: dict[str, tuple[str, str]] = {
    # 🔴 记录器自己失灵 —— 接线错误，恒不该出现；出现了必须看得见。
    "recorder_dropped": (
        "context",
        "有降级留痕没被收到（记录器接线错误）—— 本次的「退了哪几步」可能不全。",
    ),
    "fundamentals_fetch_failed": (
        "context",
        "有标的的基本面数据没拉到（财务指标接口失败）—— 相关分析这次缺这块材料。",
    ),
    # ---- BK.2 P0 批（2026-09-17）----
    # ⚠️ 下面几条的阶段只是**旧便条兜底**：便条带环节名时阶段从环节推（同一个码会从
    # 分析师 / 决策 / 取数三类环节发出），人话后面自动列出是哪几位。
    "tool_loop_no_tools": (
        "research",
        "有环节的联网检索工具这次没接上，是在不查资料的情况下直接写的"
        "—— 这和「查了、觉得不用引」不是一回事，相关内容请当作没有外部查证。",
    ),
    "ticker_unresolved": (
        "context",
        "判断出问的是某只个股，但到最后也没认出是哪一只 —— 后面的分析是在不知道具体标的、"
        "拿不到它的行情和财务数据的情况下做的。（命令行里逐步确认时屏幕上已有提示；"
        "自动确认、脚本调用、服务调用这几条路上，这一条是唯一的提示。）",
    ),
    "decision_outline_fallback": (
        "decision",
        "决策论述的大纲这次没生成出来，退成了一整段 —— 论述少了分节结构，读起来会比平时粗。",
    ),
    "reference_entry_dropped": (
        "decision",
        "文末证据清单里有条目因为格式坏了被丢掉 —— 正文里对它的引用可能查不到出处。",
    ),
    "decision_list_truncated": (
        "decision",
        "模型给出的风险 / 触发事件 / 少数派意见超过了展示上限，超出的几条被截掉了"
        "—— 被截掉的原文留在这次的存档记录里，正文里看不到。",
    ),
    # ---- BK.2 PR3（M2.5 / M2.6·2026-09-18）----
    "registry_market_fetch_failed": (
        "context",
        "本地证券名录这次需要现拉，但有市场的名录没拉到 —— 名录能力这次不全，代码核对可能不生效。",
    ),
    "registry_reconcile_failed": (
        "context",
        "名录对账这一步没跑起来（模块加载失败）—— 股票代码这次没经过名录核对。",
    ),
    "plan_leg_unbuildable": (
        "context",
        "取数计划里有一条腿点名的数据源系统认不出，整条腿被跳过了 —— 那份资料这次没去取。",
    ),
    "price_bar_stale_fallback": (
        "context",
        "有标的最新一天的行情是坏值（多半是当天还没结算），用的是前一个有效交易日的价格 —— 现价可能不是最新的。",
    ),
    # ---- BK.5（2026-09-22·取数意图被拒收 / 丢弃·5 站合一码）----
    # 一义 = 「一条意图没进最终计划」；哪道关扔的（规划员 / 校验员）写在 detail 的 stage 里。
    # 便条在节点**最终采用**时刻发（context_node._note_dropped_intents·一条意图一张），全灭不发本码
    # （整份计划没了由 plan_fallback_routing 报）。与 plan_leg_unbuildable（过了校验、构造时认不出）分开。
    # 历史基线：在册 13 个规划员 run 零命中（bk5 证据 §0）——首次在真实跑批响起时回头核档位与措辞。
    "plan_intent_dropped": (
        "context",
        "取数计划里有几条意图被扔掉了（数据源不认识 / 条目格式坏 / 没过校验），按剩下的腿执行 —— 那几份资料这次没去取。",
    ),
    # ---- BK.6（2026-09-22·登记表余 7 站 + 盘点余 2 行清账）----
    # 四码在册全零（bk6 证据 §0.1·trace 不收日志行）——首次在真实跑批响起时回头核档位与措辞。
    "context_empty_query": (
        "context",
        "问题是空的，这一段取数整个跳过了 —— 分析师在没有任何资料的情况下开会。",
    ),
    "analyst_expand_failed": (
        "analyst",
        "分析师报告太短、要求扩写，但扩写没成功，用的是原来那份短报告。",
    ),
    # 三个调用方（分析师工具循环 / 决策前核验 / 标的解析），阶段从发便条的环节推、不从这里推。
    "web_number_stamp_failed": (
        "analyst",
        "联网搜索结果里的数字没能盖上出处编号，原文直接喂回了模型 —— 这批数字后面对不了账。",
    ),
    "review_call_failed": (
        "decision",
        "证据对不上账时请另一个模型复核，复核调用本身失败了，按最保守处理维持拦截。",
    ),
    # ---- BK.2 M3（2026-09-18·决策 / 风控组）----
    # 与 fact_verification_failed（整次核验挂了、交出空清单）分开：这条是核验跑成了、但**其中几条**读不出来。
    "verification_finding_dropped": (
        "decision",
        "决策前的事实核验里有几条结果读不出来、被跳过了 —— 那几个数字这次没核到，不是核过没问题。",
    ),
    # 与 verify_checklist_item_coerced 分工（用户 09-18 裁 B「一码一义」）：coerced = 字段改回默认值、**条目保住**；
    # dropped = 条目**被扔**（没写事项 / 非 dict 在大纲装配前就被过滤，或事项本身校验不过）。两者可同时出现、各说各的。
    "verify_checklist_item_dropped": (
        "decision",
        "待查证清单里有条目没写清要查什么、被略过了 —— 那几项这次没进核验。",
    ),
    # 在回应节点当场记（三支合一条：调用失败 / 回应格式坏 / 漏答哪几条）。**不做**「从归档读漏答」的派生：
    # 节点失败与没跑到在归档里长得一样；且 09-18 量基线 50 份有需回应 finding 的归档全部答齐、零阳性。
    "risk_response_missing": (
        "decision",
        "风控闸门提了几条问题，决策经理这次有几条没有正面回应 —— 这些问题没被回答，不等于已被考虑过。",
    ),
    # ---- BK.2 M4（2026-09-21·末批）----
    # 与 analyst_fallback_report（整份退成兜底报告）分开：这条是报告**收下了**，但模型没按格式写、
    # 系统修正格式后才过关（要点写成整段散文 / 坏日期 / 分数越界 …）。09-21 量基线 23 跑 3 跑（13%）
    # → 进用户面（拆解 §5 裁 C）；detail 记被洗的顶层字段名。
    "report_sanitized": (
        "research",
        "有分析师的报告没按格式写，系统修正格式后才收下 —— 内容没丢，但这位分析师这次没按要求交。",
    ),
    # 与 analyst_rejected（「被质量审核打回且没能补救」·只报结果）分工：这条报**原因** —— 重写那一趟根本没派出去
    # （真环境几乎只有协程被取消一种情形；普通异常在分析师节点内已成兜底报告）。一次派发只发一条，detail 逐角色。
    # 🔴 #308 review：便条是**某一轮派发失败的当时**发的，措辞只许说那一轮 —— 失败照算一次返工机会，但每角色
    # 可返工 2 次（MAX_REWORK_PER_ROLE），下一轮可能照常重写并通过，也可能重写后仍被打回。原措辞「报告仍是被打回
    # 的那版，不是重写后仍不合格」是对**最终结果**下断言，两种情形下都会说错；最终结果由后面的审核与 analyst_rejected 报。
    "rework_dispatch_failed": (
        "triage",
        "质量审核打回后安排的重写有一轮没派出去（被中断）—— 那一轮这几位分析师没有被重写，且照算用掉一次返工机会；"
        "最终用的是哪一版报告，以后面的审核结果为准。",
    ),
    # ---- BK.2 M4-fix（2026-09-21·照 #304）----
    # 与 debate_placeholder（整段发言换成占位）分开：这两条是发言**保住了**，只是要点清单格式不对、被系统整理过。
    # 量基线 1/91（06-11 后零复现）。**两码两义**（#309 review·照 M3.2 裁 B）：取出论点文字 → coerced（要点还在）；
    # 取不出被略过 / 整个值不是列表被清空 → dropped（要点清单少了）。一段发言两种都有则两条都发。
    # 便条由辩论环节出口对**最终采用**的发言发出（首轮被返工替换的不发），detail 记被丢弃的字段 / 被略过条目的原值。
    "debate_key_claims_coerced": (
        "debate",
        "有辩论发言的要点清单里有条目写成了对象，系统只取出其中的论点文字收下"
        "—— 发言正文完整保留，这些要点的论点文字也在，只是附带的置信度 / 证据等字段被略去了。",
    ),
    "debate_key_claims_dropped": (
        "debate",
        "有辩论发言的要点清单里有条目取不出论点文字（或整个清单不是列表），被系统略过了"
        "—— 发言正文完整保留，但要点清单少了这些条目。",
    ),
    # ---- BK.2 大纲缺陷小修（2026-09-18·用户裁 A）----
    "verify_checklist_item_coerced": (
        "decision",
        "待查证清单里有条目的字段写法不合格（如重要程度写了系统不认的档位），已按系统默认值记、清单和大纲都保住"
        "—— 这不影响「哪些数字被拿去核验」（只核标「高」的项），模型原本写的值留在这次的存档记录里。",
    ),
}

#: 只进排查报告、**不进用户面**的码（:func:`render_markdown` 据此过滤；trace 与存档照常带）。
#: 进这张表的理由必须写明，且要写明**什么时候重评**。
TRACE_ONLY_CODES: frozenset[str] = frozenset({
    # 零阳性样本（回放 29 份带决策的存档命中 0）：没见过它真响，先不拿去打扰用户。
    # 重评时点 = 首次在真实跑批里响、且逐份核为真断链之后。
    "broken_reference",
    # 补腿成功时数据不缺，缺的只是「计划本身不完整」的可见性 —— 规划质量信号，不影响结论（BK.2 M2.4）。
    # 重评时点 = 有人想拿它衡量取数规划员的质量时（那时它该进的是规划员的考核面，不是用户面）。
    "price_leg_safety_added",
})


#: 降级点登记表（BK.3 起·2026-09-22·**站级键**）：``文件:函数限定名::告警消息前 40 字`` → ``code:<码>`` /
#: ``pending:<为什么还没留痕>`` / ``exempt:<为什么不算降级>``。守护 [lint_degradation_registry](../../scripts/lint_degradation_registry.py)
#: 扫 ``src/committee`` 下每一处 warning / error 调用点，命中退路词表而没登记的点名。
#: **为什么是站级而不是「文件:函数名」**：一个函数常有好几支退路（最大一个 17 支），一键盖多支 ⇒
#: 往已登记的函数里再加一支闸门不响（实测 findings=0）、一支留痕一支没留只能整体记 pending 或整体洗成 code。
#: 键里**不含行号**（改无关行不飘）；改措辞 = 旧键报「过时」+ 新站报「未登记」，两头都响、没有静默第三态。
#: 同函数前 40 字撞了 → 指纹段用整句；整句也相同 / 消息不是字面量 → 守护分别报「指纹碰撞」「消息非字面量」
#: （#310 review 修）——顺序编号会随重排静默换主，词表问不到的告警等于看不见，两者都不许静默过。
#: ``code:`` 值必须是**裸码**（守护按它对账码表）；依据写在条目上一行的 ``# ↓`` 注释里。
#: 逐站审依据与 65 旧键 → 144 站的映射见 [bk3 证据](../../docs/observations/bk3-20260922/FINDINGS.md)。
DEGRADATION_SITES: dict[str, str] = {
    # ↓ RDR-1.G4（2026-09-28）：命令行渲染层的兜底 —— 结论内容一字不少，只是排版回退到旧打印；
    #   不在跑批作用域内（决策已产出、归档已落），便条篮子早已关，故不算降级、不留痕。
    "src/committee/cli.py:_print_decision::决策渲染失败，回退原始打印：%s": "exempt:渲染层排版兜底——结论与数字一字不少、只是回到旧打印格式；发生在归档之后、跑批作用域外，便条篮子已关，产物看不见也不该看见",
    # ---- seg1 召回层 ----
    # 🔴 2026-09-16 M1.5 订正：本条从落地起就是**死的** —— 派生读的 state 键全仓无
    # 生产者，恒不触发，而这里标着已有留痕 = 把没做的说成做了。现已真正接通
    # （分类来源经 builder._classification_source 搬进资料夹），两向变异 + 端到端守护齐备。
    # ↓ BK.3 拆自 src/committee/query_class/classifier.py:classify（3 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ LLM 挂了走名录 / regex / 默认，分类 source≠llm，派生读 classification.source
    "src/committee/query_class/classifier.py:classify::LLM classify failed (%s: %s) for query=%": "code:classify_degraded",
    # ↓ 便条就在本支·origin=fallback）；分类走了兜底另由 classify_degraded 报，两条两件事
    "src/committee/query_class/classifier.py:classify::registry fallback 不可用 (%s: %s)，继续走 regex": "code:registry_reconcile_failed",
    # ↓ 三层全落空 source=default，同一派生
    "src/committee/query_class/classifier.py:classify::classify 三层全落空 → 按 THEMATIC 兜底 (source=d": "code:classify_degraded",
    "src/committee/query_class/classifier.py:_call_llm_with_retry::classify LLM 瞬态失败 (%s: %s)，%.1fs 后重试 %d/": "exempt:重试中间态——这条之后还有最终态，最终失败由 classify 那条登记",
    # ↓ （BK.2 M2.5（2026-09-18）名录链**中间层**——索引构建失败 → 返回空 → 对账写「名录不可用」旗子，由下游读法报；本层不另发便条（一件事一条））
    "src/committee/query_class/classifier.py:_registry_index::security registry unavailable (%s: %s), ": "code:registry_unavailable",
    # ↓ （BK.2 M2.5——对账模块**加载失败**那支原样返回、连旗子都不写，今已发便条；对账内部异常那支由对账自己写旗子（下游读法报））
    # ↓ BK.3 拆自 src/committee/query_class/classifier.py:_apply_registry（2 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 便条就在本支
    "src/committee/query_class/classifier.py:_apply_registry::registry reconcile 不可用 (%s: %s)，本次跳过校验/兜": "code:registry_reconcile_failed",
    "src/committee/query_class/classifier.py:_apply_registry::registry reconcile: %s": "exempt:对账结果逐条转日志（纠正 / 旗子说明），不是独立退路；名录不可用那类结果已写进 ticker_flags、由 registry_unavailable 派生读",
    # ↓ （BK.2 P0.2·2026-09-17）——「判了个股却到最后也没认出是哪只」已留痕；收口点在 classify（补解析报错 / 没搜到 / 搜到了但名录判无效 三支共用一条），本函数只把异常类型递过去、**返回契约未改**。价格闸不早停是设计（有一手注释），未动
    "src/committee/query_class/classifier.py:_resolve_tickers::ticker resolution failed (%s: %s) for qu": "code:ticker_unresolved",
    # ↓ （BK.2 M2.5 名录链中间层——返回空 = 名录不可用，由下游旗子读法承接）
    "src/committee/security_registry/service.py:get_index::registry: 索引构建失败 (%s: %s) → 本次跳过名录校验/兜底": "code:registry_unavailable",
    # ↓ （BK.2 M2.5 名录链**上端**——跑批内现拉时哪个市场没拉到 / 预算用尽 / 疑似截断被拒写，一次补拉一条便条；「补拉已关闭」那支不是故障，由下游旗子读法承接）
    # ↓ BK.3 拆自 src/committee/security_registry/service.py:_lazy_bootstrap（2 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ lazy 拉取关闭且本地名录为空 → 下端对账写 registry_unavailable 旗子进 ticker_flags，派生读（M2.5「上端不重复报」
    "src/committee/security_registry/service.py:_lazy_bootstrap::registry: 本地名录为空且 lazy 拉取已关闭 → 名录能力本进程不可": "code:registry_unavailable",
    # ↓ 便条就在本支·missed 汇总一条
    "src/committee/security_registry/service.py:_lazy_bootstrap::registry: lazy 预算 %.1fs 用尽，%s 未拉取（跑 `com": "code:registry_market_fetch_failed",
    # ↓ （BK.2 M2.5——跑批内只经 _lazy_bootstrap 走到，由它看结果后发便条；本函数**自己不发**（也被刷新命令 / 预热 / 日更调用，守护钉住函数体无便条））
    # ↓ BK.3 拆自 src/committee/security_registry/service.py:refresh（3 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 本函数刻意不发便条（也被跑批外的刷新命令 / 预热调，守护钉住）；跑批内经 _lazy_bootstrap 调用时 res.ok=False 进 missed、由那里发便条；跑批外只剩日志属设计（M2.5
    "src/committee/security_registry/service.py:refresh::registry: %s provider 意外抛异常 (%s: %s)": "code:registry_market_fetch_failed",
    # ↓ 同上：res.ok=False → _lazy_bootstrap 的 missed → 便条
    "src/committee/security_registry/service.py:refresh::registry: %s 刷新失败 — %s（保留本地已有数据）": "code:registry_market_fetch_failed",
    # ↓ 同上：res.truncated → _lazy_bootstrap 的 missed → 便条
    "src/committee/security_registry/service.py:refresh::registry: %s 拉取疑似被上游截断，拒绝写入（残缺名录会把有效码判成无": "code:registry_market_fetch_failed",
    # ↓ BK.3 拆自 src/committee/security_registry/service.py:prewarm（2 支·原值 exempt:）—— 逐站审后各支各记各的
    "src/committee/security_registry/service.py:prewarm::registry prewarm: 读现状失败 (%s: %s)": "exempt:用户 2026-09-17 裁 ⑤「不接」——预热只在跑批外跑（命令行 / 服务启动），便条在跑批作用域外当场作废；后果只是本次不预热、后续按需补拉（影响延迟不影响正确性）",
    "src/committee/security_registry/service.py:prewarm::registry prewarm: 刷新异常 (%s: %s)": "exempt:同上（裁 ⑤）——预热刷新异常只影响延迟，跑批内按需补拉另有留痕",
    # ↓ BK.3 拆自 src/committee/degradation_notes.py:end_run_notes（2 支·原值 exempt:）—— 逐站审后各支各记各的
    "src/committee/degradation_notes.py:end_run_notes::本次跑批结束后仍有未进产物的降级便条（最后一个环节之后才到）：%s": "exempt:记录器自身的收尾边界（BK.2 M2.3）——最后一个环节之后才到的便条物理上进不了产物，只能如实写 warning；接线错误由 recorder_dropped 在跑批中途报",
    "src/committee/degradation_notes.py:end_run_notes::丢失单关闭时上下文已变（流式入口被别处收尾），跳过还原": "exempt:记录器自身的收尾边界（BK.2 M2.3）——上下文令牌被别处收尾，跳过还原不影响任何产物",
    "src/committee/security_registry/service.py:daily_refresh_loop::registry: 每日自动刷新失败 (%s: %s)，保留本地数据·明日再试": "exempt:长驻进程的定时刷新循环，失败下一轮再来，不影响任何单次跑批的产物",
    "src/committee/security_registry/store.py:RegistryStore.replace_market::registry: %s 收到 0 条记录，拒绝清空既有数据（疑似 provid": "exempt:写库失败会上抛给调用方处置，不是静默降级（调用方 refresh 已登记）",
    # ↓ （BK.2 M2.5 名录链最上游——返回失败结果，由 _lazy_bootstrap 那条便条带出市场与原因）
    "src/committee/security_registry/providers/nasdaq.py:fetch_us::registry: NASDAQ 名录拉取失败 (%s: %s)": "code:registry_market_fetch_failed",
    # ↓ （BK.2 M2.5 名录链最上游——同上（含疑似截断 → 被拒写那支））
    "src/committee/security_registry/providers/tushare.py:_fetch_paged::registry: %s 拉取失败 (%s: %s)": "code:registry_market_fetch_failed",
    # ↓ BK.3 拆自 src/committee/agents/context_node.py:_plan_and_validate（4 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 返回 None → 调用方走降级链、routing 写 DEGRADED_ROUTE_KEY，派生读
    "src/committee/agents/context_node.py:_plan_and_validate::取数规划员没出计划，走兜底路由": "code:plan_fallback_routing",
    # ↓ 全部没过校验返回 None → 同上
    "src/committee/agents/context_node.py:_plan_and_validate::计划 %d 条意图全部没过校验，走兜底路由": "code:plan_fallback_routing",
    # ↓ BK.5：本站是汇总日志；便条在同函数紧随其后的 _note_dropped_intents 里按 verdict 逐条发（stage=validator）
    "src/committee/agents/context_node.py:_plan_and_validate::计划有 %d 条没过校验（已留痕丢弃），按剩下 %d 条执行": "code:plan_intent_dropped",
    "src/committee/agents/context_node.py:_note_dropped_intents::plan_intent_dropped 留痕本身出错，计划照旧采用（便条缺这一段": "exempt:留痕代码自己出错时的自兜分支（#311 review）——计划照旧采用、取数不退路，只是这一段便条缺了；不兜住反而会把已校验通过的计划整跑打回兜底路由",
    # ↓ 出计划 / 校验抛异常返回 None → 同上
    "src/committee/agents/context_node.py:_plan_and_validate::出计划/校验过程失败，走兜底路由": "code:plan_fallback_routing",
    # ↓ BK.3 拆自 src/committee/agents/context_node.py:_build_context_inner（4 支·原值 pending:）—— 逐站审后各支各记各的
    # ↓ BK.6：便条就在本支（HTTP /analyze 不拦空串 ⇒ 生产可达·bk6 证据 §0.2）；纯空白走规划员→兜底路由，由 plan_fallback_routing 报
    "src/committee/agents/context_node.py:make_build_context_node._build_context_inner::build_context: empty query, skipping": "code:context_empty_query",
    # ↓ 出计划超时 planned=None → 降级链写 DEGRADED_ROUTE_KEY（原键值已注明由该派生承接
    "src/committee/agents/context_node.py:make_build_context_node._build_context_inner::出计划超过 %.0fs 封顶，走兜底路由": "code:plan_fallback_routing",
    "src/committee/agents/context_node.py:make_build_context_node._build_context_inner::计划预算提醒：%s": "exempt:预算提醒是规划质量信号（validation.budget_flags），计划照常执行、不退路",
    # ↓ M1 #15·路由键 fetch_budget_capped 由派生读
    "src/committee/agents/context_node.py:make_build_context_node._build_context_inner::取数+回核超过 %.0fs 封顶，本段产出空资料夹": "code:fetch_budget_capped",
    # ↓ BK.3 拆自 src/committee/retrieval_plan/planner.py:plan_retrieval（5 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 空 query 不出计划返回 None → 调用方降级链
    "src/committee/retrieval_plan/planner.py:plan_retrieval::retrieval_planner: 空 query，不出计划": "code:plan_fallback_routing",
    # ↓ 输出缺 intents 返回 None → 同上
    "src/committee/retrieval_plan/planner.py:plan_retrieval::retrieval_planner: 输出缺 intents 数组（keys=%": "code:plan_fallback_routing",
    # ↓ 意图全部不合格返回 None → 同上
    "src/committee/retrieval_plan/planner.py:plan_retrieval::retrieval_planner: %d 条意图全部不合格，放弃本次计划": "code:plan_fallback_routing",
    # ↓ BK.5：本站是汇总日志；扔掉的条目记进 RetrievalPlan.dropped_intents（stage=planner），便条由节点最终采用时发
    "src/committee/retrieval_plan/planner.py:plan_retrieval::retrieval_planner: 丢弃 %d 条不合格意图，保留 %d 条": "code:plan_intent_dropped",
    # ↓ 出计划失败返回 None → 同上
    "src/committee/retrieval_plan/planner.py:plan_retrieval::retrieval_planner: 出计划失败，返回 None 走降级链": "code:plan_fallback_routing",
    # ↓ BK.3 拆自 src/committee/retrieval_plan/planner.py:_normalize_intent（4 支·原值 exempt:）—— 逐站审后各支各记各的
    # ↓ BK.5：逐条日志；判据与记录同出 _drop_reason，记进 dropped_intents（stage=planner），便条由节点最终采用时发
    "src/committee/retrieval_plan/planner.py:_normalize_intent::retrieval_planner: 第 %d 条意图不是对象（%s），丢弃": "code:plan_intent_dropped",
    # ↓ 同上
    "src/committee/retrieval_plan/planner.py:_normalize_intent::retrieval_planner: 第 %d 条意图 source=%r 不在": "code:plan_intent_dropped",
    "src/committee/retrieval_plan/planner.py:_normalize_intent::retrieval_planner: 第 %d 条意图（source=%s）缺 ": "exempt:意图缺 why 只是留痕字段空着，取数行为与产物数据一个字节不变（原键理由·只对本支成立）",
    "src/committee/retrieval_plan/planner.py:_normalize_intent::retrieval_planner: 第 %d 条意图（source=%s）ro": "exempt:role 认不出 scope 落 unknown，丢字段不丢条，取数行为不变",
    # ↓ BK.3 拆自 src/committee/retrieval_plan/validator.py:validate_plan（2 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ BK.5：逐条日志；verdict 进 PlanValidation，便条由节点 _note_dropped_intents 按 verdict 发（自动 / 回放路径）；人工确认路径由 cli 确认环把被拦条目记进 dropped_intents 带进节点
    "src/committee/retrieval_plan/validator.py:validate_plan::校验层拒收第 %d 条（source=%s）：%s": "code:plan_intent_dropped",
    # ↓ 全灭 → all_rejected → 调用方 None → 降级链
    "src/committee/retrieval_plan/validator.py:validate_plan::校验层全灭：%d 条意图无一存活（降级链信号）": "code:plan_fallback_routing",
    # ↓ （BK.2 M2.4——补腿说明经路由进存档，今已有读法（只进排查报告：补腿成功时数据不缺）；「两个行情源都补不出」那支由 price_unavailable 承接。⚠️ 仍在：补的腿不进归档里那份计划的意图清单（计划本身不完整这件事只在路由里看得见））
    # ↓ BK.3 拆自 src/committee/retrieval_plan/validator.py:ensure_price_leg（2 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 两个行情源都收不出股票腿 → 不补；随后价格闸早停由派生 price_unavailable 报（本函数无便条，validator 里没有 note 调用
    "src/committee/retrieval_plan/validator.py:ensure_price_leg::个股问题补不出取价腿：%r 两个行情源都收不出股票腿（格式不认或不是股票形态）": "code:price_unavailable",
    # ↓ 派生读补腿 verdict
    "src/committee/retrieval_plan/validator.py:ensure_price_leg::计划里没有取价的腿，已按个股问题的安全兜底补 %d 条（下游价位核对要用现价当尺": "code:price_leg_safety_added",
    "src/committee/retrieval_plan/verifier.py:apply_cache_invalidation::回核层：缓存条目 %s 失效失败 —— 重跑可能再次命中这条坏缓存": "exempt:BK.6 核实（2026-09-22）——生产零调用：build_context 从未给任何路径传过 cache、全仓 FactCache 只在测试里构造（context_node 注释 + grep），cache is None 立即返回、告警分支不可达。⚠️ 接上调度层缓存即重评：那时它是真无痕（失效失败只有日志、重跑会命中坏缓存）",
    # ↓ （BK.2 M2.6——被跳过的腿不进腿清单（2026-09-04 起名单收窄），「有一份资料没取到」接不住，今已发便条。⚠️ BK.0 盘点 §3.1 曾把本行（#16）判为「假待办·leg_missing 已报」，与 09-04 后的代码不符，已订正）
    "src/committee/common_context/builder.py:sources_from_plan::按计划构造源：认不出 %r，跳过这条腿": "code:plan_leg_unbuildable",
    "src/committee/common_context/sources/tushare_source.py:TushareSource.fetch::tushare attempt %d/%d failed: ts_code=%s": "exempt:重试中间态——每次 attempt 失败都喊，最终成败由调用方的缺腿判定承接",
    # ↓ BK.3 拆自 src/committee/common_context/sources/tushare_source.py:_fetch_fundamentals_cn（3 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 便条就在本支
    "src/committee/common_context/sources/tushare_source.py:_fetch_fundamentals_cn::tushare daily_basic 基本面拉取失败 ts_code=%s e": "code:fundamentals_fetch_failed",
    # ↓ 便条就在本支
    "src/committee/common_context/sources/tushare_source.py:_fetch_fundamentals_cn::tushare fina_indicator 基本面拉取失败 ts_code=%": "code:fundamentals_fetch_failed",
    # ↓ 便条就在本支
    "src/committee/common_context/sources/tushare_source.py:_fetch_fundamentals_cn::tushare 基本面两个接口都返回空行（未抛异常）ts_code=%s": "code:fundamentals_fetch_failed",
    "src/committee/common_context/sources/yfinance_source.py:YfinanceSource.fetch::yfinance attempt %d/%d failed: ticker=%s": "exempt:重试中间态——同 tushare fetch，最终成败由缺腿判定承接",
    # ↓ （BK.2 M2.6——最新一根 Close 为坏值回退前一交易日，已发便条（记本该哪天 / 实际哪天）；分析师行情工具调它时便条进分析师环节。基线：历史 1 例（07-15 NVDA）、09-18 现场 8 只 0 例 ⇒ 不是每跑必响）
    "src/committee/common_context/sources/yfinance_source.py:_sync_fetch::yfinance %s: 最新 bar Close 为 NaN，回退到最近有效 ": "code:price_bar_stale_fallback",
    "src/committee/common_context/sources/yfinance_source.py:_alpha_vantage_fetch::Alpha Vantage fallback failed: ticker=%s": "exempt:BK.6 核实（2026-09-22）——备用行情源默认未配置（ALPHA_VANTAGE_API_KEY 直接读环境、.env.example 注释掉；未配置时静默 None 连告警都不出）；配置后失败的后果 = 该腿缺货 = legs.arrived=False → leg_missing 派生已报（同函数 attempt-failed 站理由）。⚠️ 配置了该键且需要区分「主源失败 / 备源也失败」时重评",
    # ↓ BK.3 拆自 src/committee/common_context/sources/yfinance_source.py:_maybe_attach_fundamentals_us（2 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 便条就在本支
    "src/committee/common_context/sources/yfinance_source.py:_maybe_attach_fundamentals_us::yfinance 基本面为空（未抛异常）ticker=%s": "code:fundamentals_fetch_failed",
    # ↓ 便条就在本支
    "src/committee/common_context/sources/yfinance_source.py:_maybe_attach_fundamentals_us::yfinance 基本面 attach 失败（不影响价格）ticker=%s e": "code:fundamentals_fetch_failed",
    # M1.5 查明（仍成立）：三处兜底（库名 / 深度 / 工具）全写进 payload._meta，
    # 且 library_fallback 与 tool_fallback 会让回核判 STATUS_DEGRADED →
    # __verification_degraded__ ⇒ **走回核那条路**汇总已报、并带原因原文。
    # ⚠️ 但例外两支是真无痕，所以本行**不**翻 code:（见值里的冷审再订正）。
    # ↓ （BK.2 M2.4（2026-09-18）——三种兜底现已全有读者：回核跑过时库名 / 工具两支由 __verification_degraded__ 报；回核没跑时两支 + 深度认不出（回核从不读）由本读法报，两者去重）
    # ↓ BK.3 拆自 src/committee/common_context/sources/wisburg_source.py:fetch（3 支·原值 code:）—— 逐站审后各支各记各的
    "src/committee/common_context/sources/wisburg_source.py:WisburgSource.fetch::wisburg: 认不出的深度 %r，按 %r 处理（可选：%s）": "exempt:深度参数认不出按默认处理，是配置纠正不是运行时退路（同 run_budget 先例）；取数内容照常",
    # ↓ meta.tool_fallback 由派生读（「查询工具对不上、换了别的工具」
    "src/committee/common_context/sources/wisburg_source.py:WisburgSource.fetch::wisburg: 库 %r 要的工具 %r 不在服务端列表里，改用 %r（同时跳": "code:wisburg_partial_fallback",
    # ↓ 同一派生句「…且没取摘要」盖住本支
    "src/committee/common_context/sources/wisburg_source.py:WisburgSource.fetch::wisburg: 因工具回退跳过取摘要（想要 %r、实际用了 %r）—— 编号来": "code:wisburg_partial_fallback",
    # ↓ （BK.2 M2.4——「一篇都没取到」由回核报；**部分**没取到、以及回核没跑时的全部失败由本读法报）
    "src/committee/common_context/sources/wisburg_source.py:_fetch_summaries::wisburg: 第 %s 篇摘要取失败：%s": "code:wisburg_partial_fallback",
    # ↓ BK.3 拆自 src/committee/mcp_client/run_budget.py:resolve_budget_limit（2 支·原值 exempt:）—— 逐站审后各支各记各的
    "src/committee/mcp_client/run_budget.py:resolve_budget_limit::%s=%r 不是整数，改用默认值 %d（**你写的那个值没有生效**）": "exempt:预算配置非法时改用默认值并明确告警，属配置纠正不是运行时降级",
    "src/committee/mcp_client/run_budget.py:resolve_budget_limit::%s=%d 小于 1，改用默认值 %d（0 或负数会让整条研报腿必然失败，多半不": "exempt:预算配置非法时改用默认值并明确告警，属配置纠正不是运行时降级",
    # ---- seg2-7 分析 / 分诊 / 辩论 / 投票 ----
    # ↓ 一键盖分析师节点的两档（BK.2 M4.1·2026-09-21）：调用失败 / 校验全败 → 兜底报告 = analyst_fallback_report（读法）；
    #   模型没按格式写、洗过才过关 → 便条 report_sanitized（quality == "sanitized" 那一支）。
    # ↓ BK.3 拆自 src/committee/agents/base.py:node（17 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 疑似 bug 的异常同样退成兜底报告（headline 后缀由派生读
    "src/committee/agents/base.py:make_analyst_node.node::analyst %s: non-transient %s — likely a ": "code:analyst_fallback_report",
    # ↓ 调用失败退成兜底报告，派生读 headline 后缀
    "src/committee/agents/base.py:make_analyst_node.node::analyst %s: LLM/tool call failed (%s): %": "code:analyst_fallback_report",
    "src/committee/agents/base.py:make_analyst_node.node::analyst %s: BaseException %s 未被兜底捕获（兜底只捕": "exempt:BaseException 不兜底、继续上抛（取消 / 退出），会炸的路径不是静默退路（同 _exec_one_tool_call 先例）",
    # ↓ BK.6（盘点 #25）·便条就在本支；在册 0 次扩写调用（160 份报告最短 569 字 > 阈值 500）
    "src/committee/agents/base.py:make_analyst_node.node::analyst %s 一次性扩写失败: %s；保留原报告": "code:analyst_expand_failed",
    # ↓ M4.1·只对 quality=sanitized 发便条；fallback 档由 analyst_fallback_report 派生报
    "src/committee/agents/base.py:make_analyst_node.node::analyst %s: report quality=%s": "code:report_sanitized",
    # ↓ 派生读占位正文特征
    "src/committee/agents/base.py:make_debate_node.node::make_debate_node: DebateTurn.model_valid": "code:debate_placeholder",
    "src/committee/agents/base.py:make_debate_node.node::F-class violation (attempt 1): side=%s r": "exempt:可见性规则违规 → 返工是设计内纠正流程，结果写进 turn.f_check_reworked 进归档，不是静默退路",
    # ↓ 返工版占位，同一派生
    "src/committee/agents/base.py:make_debate_node.node::make_debate_node rework: DebateTurn.mode": "code:debate_placeholder",
    "src/committee/agents/base.py:make_debate_node.node::F-class violation persists after rework:": "exempt:返工后仍违规写进 turn.f_check_failed 进归档（可见），不是静默退路",
    # ↓ M1 #29·派生读兜底票理由开头
    "src/committee/agents/base.py:make_vote_node.node::make_vote_node: Vote.model_validate fail": "code:vote_parse_failed",
    "src/committee/agents/base.py:make_decision_node.node::decision_head_parse_error role=%s: %s": "exempt:决策头解析失败原样上抛（整跑失败走失败转储路径），不是静默退路",
    "src/committee/agents/base.py:make_decision_node.node::fund_mgr: 主 decision pass 输出 thesis 字段（已": "exempt:多余字段 thesis 丢弃，schema 卫生、不改决策内容",
    "src/committee/agents/base.py:make_decision_node.node::fund_mgr: decision %r normalized to %s": "exempt:决策枚举写法归一（大小写 / 空白），语义不变",
    # ↓ M1 #39·派生读占位正文
    "src/committee/agents/base.py:make_decision_node.node::fund_mgr: section %s body empty, placeho": "code:thesis_section_placeholder",
    "src/committee/agents/base.py:make_decision_node.node::fund_mgr: OBEY-2 %d 条 dissent 决策全文零提及（已告": "exempt:合规观察（OBEY-2 未覆盖的异议）只告警不改决策，执法记录已进 enforcement_log",
    # ↓ BK.6·只加读法：执法记录 rule=EVID-1 action=strip 早在写（终局质检 Q5 在读），派生 _evid1_events 读它；剥除行为不动
    "src/committee/agents/base.py:make_decision_node.node::fund_mgr: stripped hallucinated refs %s": "code:hallucinated_refs_stripped",
    # ↓ 派生读 final_decision.prose_gate_status
    "src/committee/agents/base.py:make_decision_node.node::fund_mgr: 价位 level 全被抹（ungrounded run·<%": "code:prose_gate_degraded",
    # ↓ BK.3 拆自 src/committee/agents/base.py:_invoke_json（2 支·原值 exempt:）—— 逐站审后各支各记各的
    "src/committee/agents/base.py:_invoke_json::_invoke_json parse failed (retrying once": "exempt:重试中间态——这次解析失败还会重试一次，最终失败另有登记",
    "src/committee/agents/base.py:_invoke_json::_invoke_json sanitizer applied fixes=%r;": "exempt:JSON 修复成功后内容照常校验、修复本身不是退路；失败的那支另有登记（重试 / 兜底）",
    # ↓ BK.3 拆自 src/committee/agents/base.py:_invoke_json_with_retry（2 支·原值 code:）—— 逐站审后各支各记各的
    "src/committee/agents/base.py:_invoke_json_with_retry::continuation_parse_failed_once chunk=%d ": "exempt:续写解析失败一次会重试，中间态；最终失败另有登记（下一支）",
    # ↓ truncated_at_chunk 由派生读
    "src/committee/agents/base.py:_invoke_json_with_retry::continuation_parse_failed_final chunk=%d": "code:analyst_truncated",
    "src/committee/agents/base.py:_make_tool_json_extractor._extract::tool_agent_json_parse_failed role=%s mod": "exempt:🔴 2026-09-16 M1.5 订正——原记「结果丢弃、无痕」与代码不符：它是最终答案的 JSON 解析器，解析不出**原样 raise**（不吞、不丢工具结果），被分析师节点接住后走兜底报告 ⇒ 由 code:analyst_fallback_report 100% 覆盖（这条路只有这一个出口）",
    # ↓ BK.3 拆自 src/committee/tools/agent_loop.py:run_tool_agent（5 支·原值 pending:）—— 逐站审后各支各记各的
    # ↓ BK.2 P0.1·便条在 _note_no_tools
    "src/committee/tools/agent_loop.py:run_tool_agent::bind_tools failed (%s); falling back to ": "code:tool_loop_no_tools",
    # ↓ 首轮失败退成不带工具·便条在 _note_no_tools）；非首轮原样上抛，由分析师兜底报告承接（analyst_fallback_report
    "src/committee/tools/agent_loop.py:run_tool_agent::agent_loop LLM invoke failed at iteratio": "code:tool_loop_no_tools",
    # ↓ BK.6·便条就在本支（三个调用方：分析师工具循环 / 决策前核验 / 标的解析 to_thread+asyncio.run，传递矩阵已补该行）；原文喂回一字不变、detail 不含原文
    "src/committee/tools/agent_loop.py:run_tool_agent::number stamping failed (fail-safe: raw r": "code:web_number_stamp_failed",
    "src/committee/tools/agent_loop.py:run_tool_agent::agent_loop: max_iterations=%d reached, f": "exempt:用户 2026-09-17 裁 G：撞迭代上限强制收尾是设计内每跑上限、非降级（rp-g7 调查 7/8 角色撞顶，接上则清单每跑必响）；⚠️ 上限调大、撞顶变少见后重评",
    # ↓ 强制收尾失败原样上抛 → 分析师节点兜底报告承接（同 #30「由下游承接」先例
    "src/committee/tools/agent_loop.py:run_tool_agent::agent_loop: final forced response failed": "code:analyst_fallback_report",
    # ↓ （BK.2 P0.1）——便条发在**进入本函数之前**的两个退路分支，不发在本函数里（它是 module 级函数，别处直调不该响）；本函数自己的告警后面紧跟 raise，会炸不静默
    "src/committee/tools/agent_loop.py:_plain_invoke::_plain_invoke LLM call failed: %s(%s)": "code:tool_loop_no_tools",
    # ↓ BK.3 拆自 src/committee/tools/agent_loop.py:_exec_one_tool_call（2 支·原值 exempt:）—— 逐站审后各支各记各的
    "src/committee/tools/agent_loop.py:_exec_one_tool_call::agent_loop: unknown tool %r called by LL": "exempt:模型点了不存在的工具，把错误回给模型让它改口，属对话内纠错、不改产物",
    "src/committee/tools/agent_loop.py:_exec_one_tool_call::agent_loop: tool %s raised BaseException": "exempt:BaseException 显式不捕获、继续上抛，属会炸的路径不是静默降级",
    "src/committee/tools/tool_errors.py:tool_error::tool %s failed: %s (category=%s retryabl": "exempt:把工具异常转成结构化错误回给模型，模型看得见，不是对人静默",
    # ↓ BK.3 拆自 src/committee/triage/node.py:triage（3 支·原值 code:）—— 逐站审后各支各记各的
    "src/committee/triage/node.py:make_triage_node.triage::triage: no reports to triage": "exempt:只有零份报告时到达——分析师失败会产兜底报告而不是缺席（analyst_fallback_report 派生先报），生产到不了这里",
    # ↓ verdict=warning + notes「triage error」进 triage_verdicts，派生读
    "src/committee/triage/node.py:make_triage_node.triage::triage: report %s triage failed: %s": "code:triage_report_failed",
    "src/committee/triage/node.py:make_triage_node.triage::triage verdict: role=%s verdict=%s notes": "exempt:非 pass 审核结论转日志，结论本身已在 triage_verdicts 进归档",
    # ↓ BK.3 拆自 src/committee/triage/rules_c.py:run_c_class（3 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 返回 None → C 类跳过的痕经 notices 进 enforcement_log（#59
    "src/committee/triage/rules_c.py:run_c_class::C class: unexpected response shape for %": "code:triage_c_class_skipped",
    # ↓ 同上
    "src/committee/triage/rules_c.py:run_c_class::C class: invalid status %r for %s": "code:triage_c_class_skipped",
    # ↓ 同上
    "src/committee/triage/rules_c.py:run_c_class::C class LLM call failed, skipping": "code:triage_c_class_skipped",
    "src/committee/triage/rules_e.py:run_e2::E2 LLM call failed, skipping": "exempt:用户 2026-09-16 裁「不做」——E 类整族在观察期**只记日志**（不写 verdict.notes、不改 verdict），通过时也不产生任何警告 ⇒ 它跑不起来**不会**把「本该警告」变成「通过」，实际产物影响为零。失败事实其实已落归档（e_results.E3.reason 写明 E2 没跑成），只是没人读；补它只增噪音不增信息。⚠️ **E 类一旦转正为会影响判定的检查，本条即刻作废、必须补痕**",
    # ↓ BK.2 M4.2（2026-09-21）：BaseException 分支发便条。Exception 路到不了这里（分析师节点内已成兜底报告 →
    #   analyst_fallback_report 承接）；「打回且没能补救」的结果由 analyst_rejected 读法报，本码只报原因。
    "src/committee/triage/rework.py:make_rework_node.rework_dispatcher::rework_dispatcher: role %s failed (%s): ": "code:rework_dispatch_failed",
    "src/committee/triage/pass0_validator.py:validate_pass0::Pass0Result validation failed: %s": "exempt:🔴 2026-09-16 M1.5 订正——原记「跳过校验、坏结构流向下游」与代码相反：它返回 None 恰恰是**拦住**，下游拿到的是空而非坏结构，后果已由 code:pass0_missing 覆盖；且 make_pass0_node **未注册进图**（现役走 pass0_parallel），这条今天不执行",
    # ---- seg8-9 pass0 / 决策 / 风控 ----
    # ↓ BK.3 拆自 src/committee/agents/pass0_node.py:pass0_node（6 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 调用失败直接 pass0_result=None，派生读
    "src/committee/agents/pass0_node.py:make_pass0_node.pass0_node::Pass 0 LLM call failed: %s(%s) — fallbac": "code:pass0_missing",
    "src/committee/agents/pass0_node.py:make_pass0_node.pass0_node::Pass 0 JSON parse failed (attempt 1): %s": "exempt:解析失败一次会重试，中间态；最终失败另有登记（下一支）",
    # ↓ 重试失败 → None
    "src/committee/agents/pass0_node.py:make_pass0_node.pass0_node::Pass 0 retry failed: %s(%s) — fallback": "code:pass0_missing",
    "src/committee/agents/pass0_node.py:make_pass0_node.pass0_node::Pass 0 validation failed (attempt 1), re": "exempt:校验失败一次会重试，中间态；最终失败另有登记",
    # ↓ 校验重试失败 → None
    "src/committee/agents/pass0_node.py:make_pass0_node.pass0_node::Pass 0 validation retry failed: %s(%s)": "code:pass0_missing",
    # ↓ 重试后仍不过 → None
    "src/committee/agents/pass0_node.py:make_pass0_node.pass0_node::Pass 0 validation failed after retry — f": "code:pass0_missing",
    # ↓ BK.3 拆自 src/committee/agents/pass0_parallel.py:ds_researcher_node（5 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 调用失败 → None，派生读
    "src/committee/agents/pass0_parallel.py:make_ds_researcher_node.ds_researcher_node::DS-researcher LLM call failed: %s(%s) — ": "code:ds_researcher_missing",
    "src/committee/agents/pass0_parallel.py:make_ds_researcher_node.ds_researcher_node::DS-researcher JSON parse failed (attempt": "exempt:解析失败一次会重试，中间态；最终失败另有登记",
    # ↓ 重试失败 → None
    "src/committee/agents/pass0_parallel.py:make_ds_researcher_node.ds_researcher_node::DS-researcher retry failed: %s(%s) — fal": "code:ds_researcher_missing",
    "src/committee/agents/pass0_parallel.py:make_ds_researcher_node.ds_researcher_node::DS-researcher validation failed (attempt": "exempt:校验失败一次会重试，中间态；最终失败另有登记",
    # ↓ 校验重试失败 → None
    "src/committee/agents/pass0_parallel.py:make_ds_researcher_node.ds_researcher_node::DS-researcher validation retry failed: %": "code:ds_researcher_missing",
    # ↓ BK.3 拆自 src/committee/agents/pass0_parallel.py:ds_debate_node（5 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 调用失败 → None，派生读
    "src/committee/agents/pass0_parallel.py:make_ds_debate_node.ds_debate_node::DS-debate LLM call failed: %s(%s) — fall": "code:ds_debate_missing",
    "src/committee/agents/pass0_parallel.py:make_ds_debate_node.ds_debate_node::DS-debate JSON parse failed (attempt 1):": "exempt:解析失败一次会重试，中间态；最终失败另有登记",
    # ↓ 重试失败 → None
    "src/committee/agents/pass0_parallel.py:make_ds_debate_node.ds_debate_node::DS-debate retry failed: %s(%s) — fallbac": "code:ds_debate_missing",
    "src/committee/agents/pass0_parallel.py:make_ds_debate_node.ds_debate_node::DS-debate validation failed (attempt 1):": "exempt:校验失败一次会重试，中间态；最终失败另有登记",
    # ↓ 校验重试失败 → None
    "src/committee/agents/pass0_parallel.py:make_ds_debate_node.ds_debate_node::DS-debate validation retry failed: %s(%s": "code:ds_debate_missing",
    "src/committee/agents/pass0_parallel.py:make_ds_merge_node.ds_merge_node::ds_merge: both subagents failed — pass0_": "code:pass0_missing",
    # ↓ 同一函数两支都有痕（BK.2 M3.1·2026-09-18）：整次核验挂了 → fact_verification_failed（except 分支的执法记录）；
    #   核验跑成但其中几条读不出 → 便条 verification_finding_dropped。此前因「一键盖两支」不翻，现两支齐、翻 code。
    # ↓ BK.3 拆自 src/committee/agents/base.py:_run_verification（2 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 提前批 🔴·执法记录进 enforcement_log，派生读
    "src/committee/agents/base.py:_run_verification::fund_mgr: verification failed: %s; fallb": "code:fact_verification_failed",
    # ↓ M3.1·便条就在本支
    "src/committee/agents/base.py:_run_verification::fund_mgr: skip invalid finding %s: %s": "code:verification_finding_dropped",
    "src/committee/agents/base.py:_apply_ai_transcription_check::G5 transcription check skipped (fail-ope": "code:transcription_check_skipped",
    # ↓ 四个同名嵌套 node 逐个核过（BK.2 M3.3·2026-09-18）：pre_check / check 纯计算无退路；hard_block 那支
    #   EXEC-FLOOR 算不出 → exec_floor_signal_failed；response 那支调用失败 / 漏答 → 便条 risk_response_missing。四支齐、翻 code。
    # ↓ BK.3 拆自 src/committee/agents/risk_gate.py:node（3 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 提前批 🔴·执法记录进 enforcement_log，派生读
    "src/committee/agents/risk_gate.py:make_execution_stage_hard_block_node.node::EXEC-FLOOR 信号计算失败（非阻断·按不 fire 放行）": "code:exec_floor_signal_failed",
    # ↓ M3 #44·调用失败与漏答合一个码，在回应环节当场记
    "src/committee/agents/risk_gate.py:make_risk_gate_response_node.node::risk_gate_response_failed: %s; 跳过回应（warn": "code:risk_response_missing",
    # ↓ M3 #44·漏答当场记
    "src/committee/agents/risk_gate.py:make_risk_gate_response_node.node::risk_gate_response_incomplete: fund_mgr ": "code:risk_response_missing",
    # ↓ 结构非法 / 条目非法 / 未知重复 id 三种丢法都让某条 finding 没被答上，由 response 节点比对后发一条便条（一次回应一条）
    # ↓ BK.3 拆自 src/committee/agents/risk_gate.py:_parse_responses（2 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 非 list 视为空 → 回应节点按漏答记
    "src/committee/agents/risk_gate.py:_parse_responses::risk_gate_response 非 list: %r; 视为空": "code:risk_response_missing",
    # ↓ 非法条目跳过 → 该条按漏答记
    "src/committee/agents/risk_gate.py:_parse_responses::risk_gate_response item 非法跳过: %s": "code:risk_response_missing",
    # ↓ （BK.2 P0.3·2026-09-17）——解析失败 / 形状不对 / 段数不在 3–5 三支已留痕；一次退路只发一条
    # ↓ 同函数第二个码（BK.2 M3.2·2026-09-18）：清单条目没写事项 / 非 dict 被过滤 → verify_checklist_item_dropped
    # ↓ BK.3 拆自 src/committee/agents/base.py:_build_outline（3 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ 便条就在本函数·三支同一码
    "src/committee/agents/base.py:_build_outline::decision_outline_parse_error: %s; fallba": "code:decision_outline_fallback",
    # ↓ 同上
    "src/committee/agents/base.py:_build_outline::decision_outline_shape_error: %r; fallba": "code:decision_outline_fallback",
    # ↓ 同上
    "src/committee/agents/base.py:_build_outline::decision_outline_length_gate: LLM 输出 %d ": "code:decision_outline_fallback",
    # ↓ （BK.2 P0.3）——装配校验失败那支（**成功路径也会走到**；回放在册归档 4 份单段全是这一支）已留痕，detail 带是哪个字段没过校验
    "src/committee/agents/base.py:_build_outline._assemble::decision_outline_validation_error: %s; f": "code:decision_outline_fallback",
    # ↓ （BK.2 大纲缺陷小修·2026-09-18）——清单项坏字段回默认值 / 丢项，大纲保留；上面那 4 份单段的成因从此走这一支、不再作废大纲
    # ↓ 两支两码（BK.2 M3.2 拆·裁 B）：字段回默认值 → verify_checklist_item_coerced；事项本身坏、条目扔 → verify_checklist_item_dropped
    "src/committee/agents/base.py:_sanitize_verify_checklist::verify_checklist: %d 项字段不合法已回默认值、%d 项丢弃（": "code:verify_checklist_item_coerced",
    # ↓ BK.2 M4-fix（2026-09-21·照 #304）——辩论发言只因 key_claims 格式不对校验失败时，整理该项、保住发言
    # ↓ 两支两码（#309 review·照 M3.2 裁 B）：取出论点 → debate_key_claims_coerced；取不出被略过 → debate_key_claims_dropped。
    # ↓ 告警在本函数打、便条由辩论环节出口对最终采用的发言发（首轮被返工替换的不发）
    "src/committee/agents/base.py:_validate_debate_turn::debate %s_%s r%d: key_claims 格式不对，已整理后保住": "code:debate_key_claims_coerced",
    # ↓ （BK.2 P0.4·2026-09-17）——三个吞异常分支（核验发现 / 事实清单 / 外源册）全部留痕；效果侧另有 broken_reference 读法（只进排查报告）
    "src/committee/agents/base.py:_build_references_appendix::T4: skip malformed external ledger entry": "code:reference_entry_dropped",
    # ↓ （BK.2 P0.5·2026-09-17）——「太多→截断」已留痕并带被截条目原文前缀；「太少」那支**不发**：什么都没丢，读者看到的就是模型给的，为凑数发便条只增噪音
    # ↓ BK.3 拆自 src/committee/agents/base.py:_enforce_list_bounds（2 支·原值 code:）—— 逐站审后各支各记各的
    "src/committee/agents/base.py:_enforce_list_bounds::%s: %s 仅 %d 项（期望 ≥ %d）；保留原样": "exempt:太少不修、什么都没丢（P0.5 刻意不发：读者看到的就是模型给的）",
    # ↓ P0.5·便条就在本支
    "src/committee/agents/base.py:_enforce_list_bounds::%s: %s 有 %d 项超上限 %d；截断为前 %d 项": "code:decision_list_truncated",
    "src/committee/facts/verify.py:_safe_reference_entry::verify: skip malformed reference %s: %s": "exempt:BK.2 P0.4 核实（2026-09-17）——生产零调用：唯一调用方 build_web_references 在 src/ 下仅测试引用（其 docstring 自述），这条路今天不执行。⚠️ **接回生产即须重评**：那时它是真无痕（丢条目只有日志）",
    # ↓ BK.3 拆自 src/committee/facts/mismatch_review.py:review_evidence_mismatch（2 支·原值 code:）—— 逐站审后各支各记各的
    # ↓ verdict=skipped → 执法记录 detail「复核 skipped」，派生读 enforcement_log[evidence-mismatch-review]
    "src/committee/facts/mismatch_review.py:review_evidence_mismatch::check① 复核员缺席（维持硬拦）：%s": "code:review_skipped",
    # ↓ BK.6·便条就在本支（fund_manager 内 to_thread）；执法记录写「复核 unsure（…call failed…）」、review_skipped 派生不读它、也不扩派生去锚 error 散文（裁 B）
    "src/committee/facts/mismatch_review.py:review_evidence_mismatch::check① 异模型复核调用失败（维持硬拦）: %s": "code:review_call_failed",
    "src/committee/facts/adapters.py:adapt::No adapter for provider=%s, skipping cac": "exempt:没有对应适配器时跳过缓存，只影响速度不影响取到的数据与结论",
    # ---- 跨段 ----
    "src/committee/archive/service.py:ArchiveService._try_export_json::archive: JSON export failed (DB record p": "exempt:🔴 2026-09-16 M1.5 订正 + 用户当日裁「不做」——原当活路径登记，实测 ArchiveService 在 src/ 下**零生产调用**（只有测试引用）。⚠️ **接回生产即须重评**：那时它是真无痕（只有日志、无 state 无 enforcement_log），形态同 META 实例 #4",
    # ↓ BK.2 M4.3 计划项（拆解 M4.3 step 2）当时没落地、#308 落账实跑查出，本批补上（M4-fix·2026-09-21）。
    "src/committee/graph.py:_write_final_archive::T12: failed to write archive-from-final.": "exempt:图外、state 定稿后无出口（用户 2026-09-16 裁不开新出口）；用户面已在 cli 提示（M4.3）；⚠️ 归档写入若挪进图内即重评",
    # ↓ BK.3 拆自 src/committee/graph.py:_dump_failure_checkpoint（3 支·原值 exempt:）—— 逐站审后各支各记各的
    "src/committee/graph.py:run_committee._dump_failure_checkpoint::pipeline failed — checkpoint saved → %s": "exempt:整跑已经失败时的转储路径，失败本身不静默（调用方已抛）",
    "src/committee/graph.py:run_committee._dump_failure_checkpoint::failed to dump trace on failure: %s": "exempt:整跑已经失败时的转储路径，失败本身不静默（调用方已抛）",
    "src/committee/graph.py:run_committee._dump_failure_checkpoint::failed to save checkpoint: %s": "exempt:整跑已经失败时的转储路径，失败本身不静默（调用方已抛）",
    "src/committee/auth/email_client.py:_resolve_sink_dir::Email sink directory fallback to %s": "exempt:登录系统邮件落盘目录回退，与投研链路产物无关",
}
