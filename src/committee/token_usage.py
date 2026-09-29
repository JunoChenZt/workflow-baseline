"""LLM token usage tracking — per-call records + per-run cost estimation.

Architecture: construction-time callback (方案 C).
- TokenUsageCallback 焊在 _llm() 返回的每个 LLM 实例上，tag 在构造时固定。
- 并发 analyst 节点各自构造 LLM，callback 互不干扰。
- ContextVar 只用于 run 级 TokenTracker（run_committee 入口 set，所有 callback 只读）。

已知偏差（文档标注）:
- 失败 run 已完成轮次会被重复计（rework 重试前一轮 on_llm_end 已触发）→ 偏高
- 失败调用可能少计（异常路径不触发 on_llm_end）→ 偏低
"""
from __future__ import annotations

import logging
import threading
from contextvars import ContextVar
from datetime import date as _date
from dataclasses import dataclass, field, asdict
from typing import Any, NamedTuple

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Run-level tracker (ContextVar)
# ---------------------------------------------------------------------------

_TRACKER: ContextVar[TokenTracker | None] = ContextVar("token_tracker", default=None)


def get_tracker() -> TokenTracker | None:
    return _TRACKER.get(None)


# ---------------------------------------------------------------------------
# Fee table — Anthropic/Google as of 2026-08，DeepSeek as of 2026-09-11
# ---------------------------------------------------------------------------

# Anthropic 缓存三个倍率（官方 prompt-caching 文档，2026-08-12 核对，不凭记忆）：
#   5 分钟档写入 = 基础输入价 ×1.25 ｜ **1 小时档写入 = ×2** ｜ 读取 = ×0.1
# 故 `cache_write` = 5 分钟档、`cache_write_1h` = 1 小时档。**两档差 60%**，
# 合成一个价会在用到长档时静默少算 —— 少算的方向与「缓存写入量恒记 0」那个
# 缺陷完全一致（见 extract_cache_tokens docstring）。
# 非 Anthropic 不填此键：deepseek 是自动前缀缓存、gemini 没有 TTL 档位这回事，
# 它们的返回里也不会出现 ephemeral_* 字段 → estimate_cost 回退用 cache_write。
COST_PER_1M: dict[str, dict[str, float]] = {
    # Anthropic
    "claude-opus-4-7":            {"input": 15.0,  "output": 75.0,  "cache_read": 1.5,   "cache_write": 18.75, "cache_write_1h": 30.0},
    "claude-opus-4-6":            {"input": 15.0,  "output": 75.0,  "cache_read": 1.5,   "cache_write": 18.75, "cache_write_1h": 30.0},
    "claude-sonnet-4-6":          {"input": 3.0,   "output": 15.0,  "cache_read": 0.3,   "cache_write": 3.75,  "cache_write_1h": 6.0},
    "claude-haiku-4-5-20251001":  {"input": 0.8,   "output": 4.0,   "cache_read": 0.08,  "cache_write": 1.0,   "cache_write_1h": 1.6},
    # DeepSeek —— 价格以 https://api-docs.deepseek.com/quick_start/pricing 为准
    # （**2026-09-11 重新核对**；中英两版价目页交叉验过，换算一致）。
    #
    # 🔴 **这里记的是「响应回包里的 model 字段」，不是我们配置里写的名字**。
    # 配置写 ``deepseek-chat``，DeepSeek 回什么名由它定，而且**改过**：
    #   · 2026-06 ~ 2026-08 回 ``deepseek-v4-flash``
    #   · 2026-09 起改成 ``deepseek-flash``（= 官方 DeepSeek-V4.1-Flash）
    # 2026-09-10 那跑 45 次自有调用里 41 次命中 ``deepseek-flash``、**全部记 $0**，
    # 归档只留一个「部分模型无费率」的星号 —— 这就是**改名当天起每跑都少算**的形态。
    # ⇒ 名字换了而表没跟上，不该再靠人翻归档发现：见 :func:`note_if_unpriced`。
    #
    # ⚠️ **2026-09-14 12:00（北京时间）起 ``deepseek-v4-pro`` 的请求全部转 V4.1 Flash
    # 并按 Flash 价计费**（官方定价页原文）。**实证（09-14 16:15 跑批）：回包名没变、仍报
    # ``deepseek-v4-pro``** ⇒ 该键单价已改成与 Flash 同价（见下），登记项已从 _PRICE_RECHECK_BY 删除。
    #
    # 📌 **单价取「高峰档」**：官方分高峰 / 空闲两档，空闲是高峰的 50%
    # （高峰 = 北京时间周一至周五 09:00-12:00、14:00-18:00）。这张表一个模型只放得下
    # 一个数，故取**高峰档 = 上界**：宁可高估不可低估 —— 低估正是本条要修的毛病。
    # 要换算空闲档把下面 deepseek 三个数各乘 0.5。
    # cache_read = cache-hit input；cache_write = cache-miss input（DeepSeek 不单收
    # cache 创建费，建缓存即付普通 input 价）。
    #
    # 🔒 **下面两个 legacy 键的价格刻意不动**：它们已不是任何活跃请求会回的名字，
    # 只有历史 archive 才命中，记的就是当年那个价。改它们等于篡改旧账。
    "deepseek-chat":              {"input": 0.27,  "output": 1.1,   "cache_read": 0.07,     "cache_write": 0.27},   # legacy V3，仅历史 archive
    "deepseek-v4-flash":          {"input": 0.14,  "output": 0.28,  "cache_read": 0.0028,   "cache_write": 0.14},   # 2026-06~08 的回包名，仅历史 archive
    # ↓ 以下两个是**当前活跃**的回包名，价格随官方页走
    "deepseek-flash":             {"input": 0.30,  "output": 1.20,  "cache_read": 0.006,    "cache_write": 0.30},
    # 2026-09-14 12:00 起按 Flash 计费（官方定价页）；**回包仍报 v4-pro 已实证**（同日 16:15 NVDA seg1，
    # by_model 键就是它）⇒ 与 deepseek-flash 同价。改前是 1.32 / 3.96 / 0.044 / 1.32，每笔高估 3~4 倍。
    "deepseek-v4-pro":            {"input": 0.30,  "output": 1.20,  "cache_read": 0.006,    "cache_write": 0.30},
    # Google
    "gemini-2.5-pro":             {"input": 1.25,  "output": 10.0,  "cache_read": 0.315, "cache_write": 1.25},
}


# ---------------------------------------------------------------------------
# 防漂移：价目表里没有的模型名必须**看得见**，不能静默记 0
# ---------------------------------------------------------------------------

#: 模型名 → **这个价必须在这天之前重核**（`date` + 一句为什么）。
#:
#: 🔴 **治的是三道闸的一个结构性盲区**（2026-09-11 PR review 查出）：
#: 那三道闸只认「名字不在表里」，认不出「名字在表里、但价格已经过期」——
#: 后者算得出一个数、不标 partial、归档干干净净，**比记 $0 更难发现**。
#: 通用地治「价格过期」得有价格源可对，这里不做；但**已知有期限**的那几条，
#: 没有理由让它悄悄过期。
#:
#: ⚠️ **到期只告警不拦**（遵 e2e-acceptance-standard §4「新检查一律 WARN 试用」）。
_PRICE_RECHECK_BY: dict[str, tuple[_date, str]] = {
    # 2026-09-11 ~ 09-14 这里登记过 `deepseek-v4-pro`（官方页 9-14 12:00 起转 V4.1 Flash 计费）。
    # 09-14 到期后按登记时写好的处置改完（回包名实证仍是 v4-pro → 四个数改成 Flash 同价），条目删除。
    # 🔒 **表空不等于机制没用**：机制由 tests/test_token_usage.py::TestStalePriceReminder 用合成条目钉着；
    #   下次官方页再写出"某日起改价"，把 (到期日, 一句话该改成什么) 登进来即可。
}


def stale_priced_models(today: _date | None = None) -> list[str]:
    """价格已过重核期限的模型名（排序去重）。到期只告警、不改变计价行为。"""
    now = today or _date.today()
    return sorted(m for m, (due, _why) in _PRICE_RECHECK_BY.items() if now >= due)


def note_if_price_stale(model: str, where: str, *, today: _date | None = None,
                        seen: set[str] | None = None) -> bool:
    """价格过了重核期限就喊一嗓子（每个名字每跑一次）。返回「是否已过期」。

    与 :func:`note_if_unpriced` **是两回事，别合并**：那条说「这笔钱算不出来」，
    本条说「算出来了，但这个数多半已经不对」。前者读表的人看得出可疑，后者看不出。
    """
    entry = _PRICE_RECHECK_BY.get(model)
    if entry is None:
        return False
    due, why = entry
    if (today or _date.today()) < due:
        return False
    bucket = _warned_stale_price_models if seen is None else seen
    if model not in bucket:
        bucket.add(model)
        logger.warning(
            "token_usage: 模型 %r 的单价已过重核期限 %s（%s）—— 现在算出来的钱多半不对（%s）。"
            "请对照官方定价页更新 COST_PER_1M 后把它从 _PRICE_RECHECK_BY 里删掉",
            model, due.isoformat(), where, why,
        )
    return True


#: 已经喊过的名字，不再重复喊（避免一跑里同一个名字刷几十条日志）。
#: ⚠️ 模块级 = 跨测试残留，测试里要隔离请 clear() 它（镜像 ``streaming._warned_*`` 的写法）。
#:
#: 🔴 **模块级去重只适用于「构造 LLM」那道闸**（2026-09-11 PR review 查出）：
#: 进程长期活着时（服务进程、批量回归），一个新名字**这辈子只会被喊一次** ——
#: 第二次跑批的人在日志里什么也看不到。落账那道闸因此**改成按 tracker 去重**
#: （见 :meth:`TokenTracker.record`）：一次 run 一个 tracker ⇒ **每跑都至少喊一次**。
#: 归档那道闸（``unpriced_models``）本来就每跑都写，不受影响。
_warned_unpriced_models: set[str] = set()

#: 同上，给「价格过期」那道用。
_warned_stale_price_models: set[str] = set()


def note_if_unpriced(model: str, where: str, *, seen: set[str] | None = None) -> bool:
    """模型名不在价目表里就喊一嗓子（每个名字只喊一次）。返回「是否不在册」。

    **为什么是 warn 而不是当场炸**（与 ``common_context.schema.check_source_roster``
    那道导入期硬核**刻意不同**）：五源名录漂开会让某条腿被静默跳过、下游身份错位一格，
    那是**决策正确性**问题，必须让进程起不来。这里坏掉的只是**账**——
    钱算不准不该把一次分析跑停掉。⇒ 同一套「对着一份真值源点名 + 漂开立刻可见」的手法，
    承重等级不同，收口力度就不同。

    这道闸的**唯一职责是让它可见**，可见有三处（缺一不可，各堵一个时间点）：
      ① 本函数在**构造 LLM 时**喊 —— 花钱之前就知道这次记不上账；
      ② 本函数在**落账时**（``TokenTracker.record``）喊 —— 回包报了个新名字时；
      ③ ``TokenTracker.to_dict()`` 把名字**写进归档**（``unpriced_models``）——
         日志会滚掉，归档不会；事后翻账能直接看到是哪个名字漏了，
         而不是只看到一个「部分模型无费率」的星号，再去逐条数记录。

    🔴 **已知盲区 —— ``oc/`` 聚合商那条路，这三道闸都拦不住**（2026-09-11 PR review 查出，
    **未修，本函数不解决**）：配置写 ``oc/gemini-2.5-pro`` 时，闸 ① 看到的是带前缀的字符串
    ⇒ 会喊；但送给聚合商的是**去掉前缀的裸名**，回包报的多半也是裸名
    （**推断**：归档里至今没有一次 ``oc/`` 调用可查）⇒ 闸 ② / ③ 一看「在册」就放行，
    于是**按原厂直连价算钱**，归档还理直气壮写 ``partial_cost: false``。
    **这比记 $0 更糟：$0 至少长得可疑，这个是一个自信的错数。**
    要真治得把「这次走的是聚合商」一路带到落账处，不是本函数改得动的。
    ⚠️ 现状缓解项：本仓实际 ``.env`` **一处 ``oc/`` 都没用**，``.env.example`` 里那几行是**注释掉的示例**。

    🔒 **直接问 ``COST_PER_1M``，不另存一份名单**：快照常量会与表漂开，
    那正是本函数要治的病的同款形态。

    Args:
        model: 待核的模型名（配置写的名字，或回包报的名字）。
        where: 出错信息里指认是在哪一步看到的，例如 ``"_llm(tag=triage_c)"``。
        seen: 去重用的集合。不给 = 用模块级那份（进程内只喊一次）；
            给一个 run 级的集合 = **每跑都至少喊一次**（落账那道闸走这条）。
    """
    if model in COST_PER_1M:
        return False
    bucket = _warned_unpriced_models if seen is None else seen
    if model not in bucket:
        bucket.add(model)
        logger.warning(
            "token_usage: 模型 %r 不在价目表里（%s）—— 这批调用会按 $0 落账，"
            "整跑成本偏低。对得上的话请补进 COST_PER_1M；"
            "已登记的名字有 %s",
            model, where, sorted(COST_PER_1M),
        )
    return True


def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read: int | None,
    cache_creation: int | None,
    cache_creation_1h: int = 0,
) -> float | None:
    """Estimate USD cost. Returns None if model not in fee table.

    ``cache_creation`` 是缓存写入量**合计**；``cache_creation_1h`` 是其中走
    1 小时 TTL 的部分（由 `extract_cache_tokens` 拆出）。两档单价差 60%，
    合起来按 5 分钟档计会少算 —— 默认 0 时行为与拆分前完全相同。
    """
    rates = COST_PER_1M.get(model)
    if rates is None:
        return None
    cr = cache_read or 0
    cc = cache_creation or 0
    # 防御：1 小时档不可能多于合计（真实返回不会这样，但坏数据不该把 5 分钟档算成负数）
    cc_1h = min(max(0, cache_creation_1h or 0), cc)
    cc_5m = cc - cc_1h
    fresh_input = max(0, input_tokens - cr - cc)
    return (
        fresh_input * rates["input"]
        + output_tokens * rates["output"]
        + cr * rates["cache_read"]
        + cc_5m * rates["cache_write"]
        + cc_1h * rates.get("cache_write_1h", rates["cache_write"])
    ) / 1_000_000


# ---------------------------------------------------------------------------
# TokenRecord
# ---------------------------------------------------------------------------

class CacheTokens(NamedTuple):
    """`extract_cache_tokens` 的返回值。仍可当元组比较 / 解包（3 元）。"""

    read: int | None
    creation: int | None
    """写入量**合计**（5 分钟档 + 1 小时档）—— TokenRecord 记的就是这个数。"""
    creation_1h: int
    """上面那笔里走 1 小时 TTL 的部分。只为计价拆出来（单价 ×2 而非 ×1.25）。"""


def extract_cache_tokens(usage_metadata: dict | None) -> CacheTokens:
    """从 langchain 归一后的 usage_metadata 取出缓存读取量 / 写入量（含 TTL 分档）。

    **单一真值源**：`TokenTracker.record` 与 `trace.py` 的 TraceCallback 都走这里。
    两处各写一份是「改一处留半截」的经典形态（见已知坑表 §3.2），不要复制粘贴。

    ⚠️ **写入量必须做回退，否则永远记 0**（2026-08-11 AG.1 探针实测坐实）：
    `langchain-anthropic==1.5.0` 归一 Anthropic 返回时，把写入量拆进
    ``ephemeral_5m_input_tokens`` / ``ephemeral_1h_input_tokens``，
    而 ``cache_creation`` 恒填 0。实测同一次响应里：

        原始 response.usage.cache_creation_input_tokens = 5520
        归一后 input_token_details = {"cache_read": 0, "cache_creation": 0,
                                      "ephemeral_5m_input_tokens": 5520, ...}

    只读 ``cache_creation`` 的后果有两层：① 成本低估（写入按基础价 ×1.25 计费，
    记 0 等于这笔没算）；② 「打的标记到底生没生效」这个判据**永不会响** ——
    正是已知坑表 §3.2 形态⑥（判据写得对、前提也成立，坏的是执行检查那段代码它自己）。

    读取量（``cache_read``）三家都填得对，不需要回退。

    **为什么要把 1 小时档单独拆出来**：Anthropic 的写入价按 TTL 分两档
    （5 分钟 = 基础输入价 ×1.25，1 小时 = ×2，差 60%）。合成一个数交给
    `estimate_cost` 就只能按其中一档计 —— 那是同一种少算法的另一半。
    本仓目前不请求 1 小时档（`_cacheable_system` 不带 ttl），所以这条是
    **提前把口子堵上**：真用起来时不必记得回来改计价。
    """
    details = (usage_metadata or {}).get("input_token_details") or {}
    if not details:
        return CacheTokens(None, None, 0)
    cache_read = details.get("cache_read")
    cache_creation = details.get("cache_creation")
    eph_1h = details.get("ephemeral_1h_input_tokens") or 0
    if not cache_creation:
        ephemeral = (details.get("ephemeral_5m_input_tokens") or 0) + eph_1h
        if ephemeral:
            cache_creation = ephemeral
    # 无论合计是从哪条路来的，1 小时档都以 ephemeral_1h 为准（取 min 防坏数据越界）
    return CacheTokens(cache_read, cache_creation, min(eph_1h, cache_creation or 0))


@dataclass
class TokenRecord:
    tag: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cache_read_input_tokens: int | None = None
    cache_creation_input_tokens: int | None = None
    estimated_cost_usd: float | None = None


# ---------------------------------------------------------------------------
# TokenTracker
# ---------------------------------------------------------------------------

class TokenTracker:
    """Thread-safe accumulator for token usage across a pipeline run."""

    def __init__(self) -> None:
        self._records: list[TokenRecord] = []
        self._lock = threading.Lock()
        #: 本跑已经喊过的「表里没有的名字」。**run 级**，不是进程级 ——
        #: 长期活着的进程里，模块级那份会让新名字一辈子只被喊一次。
        self._warned_unpriced: set[str] = set()
        #: 同上，给「价格过期」那道用（也走 run 级）。
        self._warned_stale: set[str] = set()

    def record(self, tag: str, model: str, usage_metadata: dict | None) -> None:
        if usage_metadata is None:
            logger.debug("token_usage: usage_metadata=None for tag=%s model=%s (streaming without stream_usage?)", tag, model)
            return
        input_t = usage_metadata.get("input_tokens", 0) or 0
        output_t = usage_metadata.get("output_tokens", 0) or 0
        total_t = usage_metadata.get("total_tokens", 0) or 0

        cache = extract_cache_tokens(usage_metadata)
        cache_read, cache_creation = cache.read, cache.creation

        cost = estimate_cost(model, input_t, output_t, cache_read, cache_creation, cache.creation_1h)
        if cost is None:
            # 回包报了个表里没有的名字 —— 可见性闸口 ②（见 note_if_unpriced）。
            # 按 tracker 去重 = 每跑至少喊一次，不因进程长活而全程只喊一次。
            note_if_unpriced(model, f"响应回包 tag={tag}", seen=self._warned_unpriced)
        else:
            # 算出来了，但这个价可能已经过期 —— 与上面是两回事，不能合并。
            note_if_price_stale(model, f"响应回包 tag={tag}", seen=self._warned_stale)

        rec = TokenRecord(
            tag=tag,
            model=model,
            input_tokens=input_t,
            output_tokens=output_t,
            total_tokens=total_t,
            cache_read_input_tokens=cache_read,
            cache_creation_input_tokens=cache_creation,
            estimated_cost_usd=cost,
        )
        with self._lock:
            self._records.append(rec)

    def _aggregate(self, key_fn) -> dict[str, dict]:
        agg: dict[str, dict] = {}
        with self._lock:
            records = list(self._records)
        for r in records:
            k = key_fn(r)
            if k not in agg:
                agg[k] = {
                    "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                    "cache_read_input_tokens": None,
                    "cache_creation_input_tokens": None,
                    "estimated_cost_usd": 0.0,
                    "calls": 0,
                    "_has_unknown_cost": False,
                }
            a = agg[k]
            a["input_tokens"] += r.input_tokens
            a["output_tokens"] += r.output_tokens
            a["total_tokens"] += r.total_tokens
            a["calls"] += 1

            for field_name in ("cache_read_input_tokens", "cache_creation_input_tokens"):
                val = getattr(r, field_name)
                if val is not None:
                    a[field_name] = (a[field_name] or 0) + val

            if r.estimated_cost_usd is not None:
                a["estimated_cost_usd"] += r.estimated_cost_usd
            else:
                a["_has_unknown_cost"] = True
        return agg

    def summary_by_model(self) -> dict[str, dict]:
        return self._aggregate(lambda r: r.model)

    def summary_by_tag(self) -> dict[str, dict]:
        return self._aggregate(lambda r: r.tag)

    def total(self) -> dict:
        agg = self._aggregate(lambda _: "_total")
        return agg.get("_total", {
            "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
            "cache_read_input_tokens": None,
            "cache_creation_input_tokens": None,
            "estimated_cost_usd": 0.0,
            "calls": 0,
            "_has_unknown_cost": False,
        })

    def to_dict(self) -> dict:
        by_model = self.summary_by_model()
        by_tag = self.summary_by_tag()
        totals = self.total()
        # `_has_unknown_cost` 仍由 `_aggregate` 算、仍要从对外结构里摘掉；
        # 但 `partial_cost` 的值**不再取自它**（见下方同一快照那段注释）。
        for d in list(by_model.values()) + list(by_tag.values()) + [totals]:
            d.pop("_has_unknown_cost", None)
        with self._lock:
            records = [asdict(r) for r in self._records]
        # 可见性闸口 ③：把「是哪些名字没算上钱」写进归档。
        # 🔒 **从 records 现推，不另记一份**：``merge_from`` 续跑吃进来的旧记录也照样算得上，
        # 而另攒一个集合只有 record() 那条路会填 —— 续跑段就会漏，属「改一处留半截」。
        # cost is None ⇔ 模型不在价目表（estimate_cost 只有这一条返 None 的路）。
        unpriced = sorted({r["model"] for r in records if r["estimated_cost_usd"] is None})
        # 🔴 **这两个字段必须出自同一份快照**（2026-09-11 PR review 查出）：
        # 上面那几个汇总各自加过一次锁，``records`` 又是第四次 —— 并发下两份快照之间
        # 可以插进新记录，于是「标了 partial 却没名字」或反过来。
        # 而我们自己写了条测试断言这两个字段永远一致（那条是单线程的，照不出这道缝）。
        # ⇒ 索性让 partial 也从 records 推：一致性变成**构造上成立**，不靠运气。
        partial = bool(unpriced)
        # 「价格过期」也写进归档 —— 日志会滚掉，归档不会。
        # ⚠️ **不并进 partial_cost**：那个字段的意思是「这笔钱算不出来」，
        # 而过期价是**算出来了但多半不对**，两种病读者的应对完全不同。
        seen_models = {r["model"] for r in records}
        stale = [m for m in stale_priced_models() if m in seen_models]
        return {
            "records": records,
            "by_model": by_model,
            "by_tag": by_tag,
            "total": totals,
            "partial_cost": partial,
            "unpriced_models": unpriced,
            "stale_price_models": stale,
        }

    def merge_from(self, data: dict) -> None:
        """Rehydrate records from a checkpoint's token_usage dict."""
        for rd in data.get("records", []):
            rec = TokenRecord(**{k: v for k, v in rd.items() if k in TokenRecord.__dataclass_fields__})
            with self._lock:
                self._records.append(rec)


# ---------------------------------------------------------------------------
# Construction-time callback — attached to every LLM by _llm()
# ---------------------------------------------------------------------------

def _extract_model_name(response: LLMResult) -> str:
    """Best-effort model name from LLMResult."""
    if response.llm_output:
        name = response.llm_output.get("model_name") or response.llm_output.get("model")
        if name:
            return name
    try:
        gen = response.generations[0][0]
        meta = getattr(gen, "generation_info", {}) or {}
        name = meta.get("model") or meta.get("model_name")
        if name:
            return name
        msg = getattr(gen, "message", None)
        if msg:
            rm = getattr(msg, "response_metadata", {}) or {}
            name = rm.get("model") or rm.get("model_name") or rm.get("model_id")
            if name:
                return name
    except (IndexError, AttributeError):
        pass
    return "unknown"


def _extract_usage(response: LLMResult) -> dict | None:
    """Extract usage_metadata from LLMResult."""
    try:
        gen = response.generations[0][0]
        msg = getattr(gen, "message", None)
        if msg and hasattr(msg, "usage_metadata"):
            return msg.usage_metadata
    except (IndexError, AttributeError):
        pass
    return None


class TokenUsageCallback(BaseCallbackHandler):
    """Attached at LLM construction time with a fixed tag. Thread-safe via TokenTracker._lock."""

    def __init__(self, tag: str = "unknown") -> None:
        super().__init__()
        self.tag = tag

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        tracker = _TRACKER.get(None)
        if tracker is None:
            logger.debug("token_usage: no tracker active for tag=%s (call outside run_committee?)", self.tag)
            return
        model = _extract_model_name(response)
        usage = _extract_usage(response)
        tracker.record(self.tag, model, usage)
