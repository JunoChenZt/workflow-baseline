"""Agent node factories — all agents share the same call pattern.

续写协议（plan §0.2 / §3）：
- `_invoke_json` 是底层原语：一次 invoke + JSON 提取。vote / 首段调用 / 测试 mock 直接用。
- `_invoke_with_continuation` 是编排层：在 `_invoke_json` 之上做长度保障与续写循环。
  权威停止条件 = `len(str(data[length_field])) >= min_chars`；`continuation` 仅辅助。
- vote 节点不走续写（输出短、结构刚、长度非瓶颈）。
- analyst 节点走「一次性扩写」（最多再调一次，不进入循环；并行 7 个节点做 chunk UI
  会过于抖动，故不发 chunk 事件）。
"""
from __future__ import annotations
import asyncio
import json
import logging
import re
import time
from typing import TYPE_CHECKING, Any, Callable

import httpx
import pydantic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

from committee.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    FORCE_OPENAI_COMPAT,
    MAX_CONTINUATIONS,
    MAX_TOKENS,
    MAX_TOKENS_ACADEMIC,
    MAX_TOKENS_DECIDE,
    MIN_CHARS_ANALYST,
    MIN_CHARS_DEBATE,
    OPENAI_BASE_URL,
    OPENAI_COMPAT_API_KEY,
    OPENAI_COMPAT_BASE_URL,
    PROMPT_CACHE_ENABLED,
    PROMPT_CACHE_MIN_CHARS,
    ROLES,
    TEMP_ANALYST,
    TEMP_DEBATE,
    TEMP_DECISION,
    TEMP_VOTE,
    DECISION_WEB_SEARCH_MAX_CALLS,
    DECISION_WEB_SEARCH_MAX_ITERATIONS,
    WEB_SEARCH_MAX_CALLS,
    WEB_SEARCH_MAX_ITERATIONS,
    WEB_SEARCH_ROLES,
)
from committee.degradation_notes import note_degradation
from committee.policy import (
    DEBATE_POLICY,
    DECISION_POLICY,
    ClaimAccumulator,
    FieldPolicy,
    mergeable_keys,
)
from committee.prompts import (
    SYSTEM_PROMPTS,
    DEBATE_PROMPTS,
    VOTE_PROMPT,
    DECISION_PROMPT,
    DECISION_OUTLINE_PROMPT,
    SECTION_EXPAND_PROMPT,
    VERIFICATION_PROMPT,
    build_facts_guidance,
)
from committee.prompts.portfolio_context import render_portfolio_context
from committee.schemas import (
    AnalysisReport,
    DebateTurn,
    Vote,
    VoteDirection,
    FinalDecision,
    DecisionOutline,
    SectionSpec,
    ThesisSection,
)
from committee.schemas.decision import (
    ClaimAudit,
    VerificationFinding,
    VerifyItem,
    ReferenceEntry,
    CREDIBILITY_TIER_ZH,
    llm_facing_findings,
)
from committee.schemas.common import FindingConfidence
from committee.schemas.validation import sanitized_fields, validate_with_fallback
from committee.state import CommitteeState, collect_reports
from committee.streaming import emit_chunk, emit_event
from committee.triage.rules_f import run_f_class, _F3_OBSERVATION_ONLY

if TYPE_CHECKING:
    from committee.common_context.schema import CommonContext

log = logging.getLogger("committee.agents")

_REF_PATTERN = re.compile(r"\{ref:(f\d+)\}")
_WEB_REF_PATTERN = re.compile(r"\{ref:(w\d+)\}")  # AD.6 §b: web 信源引用
_MAX_WEB_REF_GUIDANCE_LINES = 20  # RISK-2: section prompt 注入可引用信源上限
_CITATION_WINDOW = 300
_CLAIM_TOKEN_THRESHOLD = 0.3
_CJK_RUN_RE = re.compile(r"[一-鿿]+")
_ASCII_WORD_RE = re.compile(r"[a-z0-9]+")

_THESIS_NUMBER_RE = re.compile(
    r"(?:[\$¥€£]?\s*)"
    r"(\d[\d,]*\.?\d*)"
    r"(?:\s*[%‰万亿千KMBTkmbGg]?)",  # AD.2 §c: 去掉"百"——"5个百分点"被误 scale ×100
)
_THESIS_SCALE_MAP = {
    "万": 1e4, "亿": 1e8, "千": 1e3,  # AD.2 §c: 移除"百"（百分点/百分比误判源）
    "k": 1e3, "K": 1e3, "m": 1e6, "M": 1e6,
    "b": 1e9, "B": 1e9, "g": 1e9, "G": 1e9,
    "t": 1e12, "T": 1e12,
}
_THESIS_NUM_TOLERANCE = 0.05
_THESIS_REF_PROXIMITY = 200
# AD.2 §c: 裸年份 / A股代码不是定量主张，扫描时跳过以消除 uncited-number 噪音。
_THESIS_YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")
_ASHARE_CODE_PREFIXES = (
    "600", "601", "603", "605", "000", "001", "002", "003", "300", "301", "688", "689",
)


def _extract_claim_tokens(claim: str, min_len: int = 2) -> set[str]:
    """Tokenize a claim for citation-proximity matching.

    Latin/digit runs → word tokens (whitespace/punctuation already separate them).
    CJK runs → character bigrams. Chinese has no word delimiters, so the old
    ``[\\w一-鿿]+`` produced whole-phrase tokens that almost never matched the
    fund_mgr's *paraphrased* thesis verbatim → ~87% false-positive misattribution
    on Chinese (2026-05-29 e2e finding). Bigrams are paraphrase-robust: same topic
    discussed nearby shares many 2-grams even when wording differs.
    """
    tokens: set[str] = set()
    for w in _ASCII_WORD_RE.findall(claim.lower()):
        if len(w) >= min_len:
            tokens.add(w)
    for run in _CJK_RUN_RE.findall(claim):
        if len(run) == 1:
            tokens.add(run)
        else:
            for i in range(len(run) - 1):
                tokens.add(run[i:i + 2])
    return tokens


def _verify_citation_context(
    fact_id: str,
    claim: str,
    section_body: str,
    match_start: int,
) -> bool:
    """Check if key tokens from the fact's claim appear near the citation."""
    tokens = _extract_claim_tokens(claim)
    if not tokens:
        return True
    window = section_body[max(0, match_start - _CITATION_WINDOW):match_start + _CITATION_WINDOW].lower()
    hits = sum(1 for t in tokens if t in window)
    return hits / len(tokens) >= _CLAIM_TOKEN_THRESHOLD


def _is_noise_number(m: "re.Match") -> bool:
    """AD.2 §c: True 表示裸年份(19xx/20xx) 或 A股代码(6位 + A股前缀)，无 %/货币/scale 修饰。

    这类不是定量主张，否则在 uncited-number 扫描里产生误报噪音（EVID-2e/CASE-13/14）。
    """
    full = m.group(0).strip()
    digits = m.group(1)
    if full != digits:  # 带货币前缀 / %/scale 后缀 → 是真实数量，不算噪音
        return False
    plain = digits.replace(",", "")
    if not plain.isdigit():  # 含小数点 → 不是年份/代码
        return False
    if _THESIS_YEAR_RE.match(plain):
        return True
    if len(plain) == 6 and plain.startswith(_ASHARE_CODE_PREFIXES):
        return True
    return False


def _extract_thesis_numbers(text: str, *, skip_noise: bool = False) -> list[tuple[float, int]]:
    """Extract (value, position) pairs from thesis text.

    skip_noise=True (AD.2 §c)：丢弃裸年份 / A股代码（见 _is_noise_number）。仅 thesis
    正文扫描用；inventory 数值提取保持 False（不影响匹配基准）。
    """
    results: list[tuple[float, int]] = []
    for m in _THESIS_NUMBER_RE.finditer(text):
        raw = m.group(1).replace(",", "")
        try:
            val = float(raw)
        except ValueError:
            continue
        if skip_noise and _is_noise_number(m):
            continue
        suffix = m.group(0).rstrip()
        if suffix:
            scale = _THESIS_SCALE_MAP.get(suffix[-1], 1.0)
            val *= scale
        results.append((val, m.start()))
    return results


def _number_has_nearby_ref(pos: int, ref_positions: list[int]) -> bool:
    """Check if a number at `pos` has a {ref:fX} citation within proximity."""
    return any(abs(pos - rp) <= _THESIS_REF_PROXIMITY for rp in ref_positions)


def _number_in_inventory(val: float, inventory_numbers: list[float]) -> bool:
    """Check if a number approximately matches any number in the facts inventory."""
    for inv in inventory_numbers:
        if inv == 0:
            if val == 0:
                return True
            continue
        if abs(val - inv) / abs(inv) <= _THESIS_NUM_TOLERANCE:
            return True
    return False


def _scan_uncited_numbers(
    section_body: str,
    facts_inventory: list,
) -> list[tuple[float, int]]:
    """Find numeric claims in thesis text not backed by a nearby citation or inventory match."""
    from committee.facts.stamp_families import web_stamp_spans

    # T11（认章不撕章·麻烦一 a）：外部数据章 [W#…] 现在会出现在论文正文里。
    # 认识它——① 章区间内的 batch/rIdx/k 不是正文数字（跳过，不误当 uncited）；
    # ② 章 = 一枚出处引用，章旁的真数字算"有出处"（章起点加进 ref_positions）。
    web_spans = web_stamp_spans(section_body)
    nums = _extract_thesis_numbers(section_body, skip_noise=True)  # AD.2 §c: 滤年份/A股代码
    if web_spans:
        nums = [(v, p) for (v, p) in nums
                if not any(s <= p < e for s, e in web_spans)]
    if not nums:
        return []
    ref_positions = [m.start() for m in _REF_PATTERN.finditer(section_body)]
    ref_positions += [s for s, _ in web_spans]
    inv_numbers: list[float] = []
    for fact in facts_inventory:
        claim = getattr(fact, "claim", "") or ""
        sd = getattr(fact, "supporting_data", "") or ""
        inv_numbers.extend(v for v, _ in _extract_thesis_numbers(claim))
        inv_numbers.extend(v for v, _ in _extract_thesis_numbers(sd))

    uncited: list[tuple[float, int]] = []
    for val, pos in nums:
        if _number_has_nearby_ref(pos, ref_positions):
            continue
        if _number_in_inventory(val, inv_numbers):
            continue
        uncited.append((val, pos))
    return uncited


def _extract_json(text: str) -> dict:
    """Extract the first JSON object from LLM output.

    Three-layer repair chain (2026-06-03):
    1. ``raw_decode`` from first ``{`` — handles trailing content / "Extra data".
    2. ``_sanitize_llm_text_fields`` — fixes bare newline/quote in whitelisted fields.
    3. ``json_repair.repair_json`` — deterministic structural repair (missing commas,
       unterminated strings, unescaped chars in any field).

    Raises ``ValueError`` (controlled) if no object is parseable — never lets a bare
    ``json.JSONDecodeError`` escape to callers.
    """
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON object in LLM output: {text[:200]!r}")
    decoder = json.JSONDecoder()
    try:
        obj, _end = decoder.raw_decode(text, start)
    except json.JSONDecodeError:
        # Layer 2: fix illegal chars in whitelisted text fields
        sanitized, fixes = _sanitize_llm_text_fields(text)
        s_start = sanitized.find("{")
        if s_start == -1:
            raise ValueError(f"No JSON object after sanitize: {text[:200]!r}")
        try:
            obj, _end = decoder.raw_decode(sanitized, s_start)
        except json.JSONDecodeError:
            # Layer 3: json_repair — structural fix (missing commas, etc.)
            try:
                from json_repair import repair_json
                repaired = repair_json(sanitized[s_start:], return_objects=False)
                obj = json.loads(repaired)
                log.warning(
                    "_extract_json: recovered via json_repair (sanitize fixes=%r)",
                    fixes,
                )
            except Exception as e:
                raise ValueError(
                    f"unparseable JSON after sanitize+repair ({e}); "
                    f"prefix={text[:160]!r} suffix={text[-120:]!r}"
                ) from e
        else:
            if fixes:
                log.warning("_extract_json: recovered via sanitizer fixes=%r", fixes)
    if not isinstance(obj, dict):
        raise ValueError(f"top-level JSON is not an object: {type(obj).__name__}")
    return obj


def _make_tool_json_extractor(role: str, model: str):
    """Build an ``extract_json_fn`` for ``run_tool_agent`` with a controlled JSON guard.

    The agent loop has already produced its final text by the time this runs, so
    "retry" here means parse + sanitize/repair (delegated to ``_extract_json``) — an
    LLM re-invoke isn't available at this layer; ``run_tool_agent``'s ``max_iterations``
    is the upstream retry. On unrecoverable failure: log role/model + a bounded snippet
    (model output only — never headers/keys/secrets) and raise a controlled ``ValueError``,
    not a bare ``JSONDecodeError``.
    """
    def _extract(text: str) -> dict:
        try:
            return _extract_json(text)
        except ValueError as e:
            log.warning(
                "tool_agent_json_parse_failed role=%s model=%s err=%s prefix=%r suffix=%r",
                role, model, e,
                text[:200], (text[-120:] if len(text) > 320 else ""),
            )
            raise ValueError(
                f"tool_agent[{role}/{model}] produced unparseable JSON output: {e}"
            ) from e
    return _extract


_TEXT_FIELD_KEYS = frozenset({"body", "reasoning", "rationale", "summary", "content"})
_TEXT_FIELD_RE = re.compile(
    r'"(?:' + "|".join(re.escape(k) for k in sorted(_TEXT_FIELD_KEYS)) + r')"\s*:\s*"',
)


def _sanitize_llm_text_fields(raw: str) -> tuple[str, list[str]]:
    """修复白名单大文本字段 value 内的非法字符；key、结构字符、非白名单字段不动。

    value 结束判断：裸 " 后（跳过空白）若下一个非空白字符是 , } ] 则是合法结束。
    不包含 : —— value 后面不直接跟 :，只有 key 后跟 :。
    """
    fixes: list[str] = []
    n = len(raw)

    # 第一遍：定位各白名单字段 value 的内容区间 [seg_start, seg_end)
    segments: list[tuple[int, int]] = []
    for m in _TEXT_FIELD_RE.finditer(raw):
        val_open = m.end() - 1   # value 开口 " 的位置
        i = val_open + 1
        while i < n:
            c = raw[i]
            if c == "\\":
                i += 2
            elif c == '"':
                j = i + 1
                while j < n and raw[j] in " \t\r\n":
                    j += 1
                if j >= n or raw[j] in ",}]":
                    segments.append((val_open + 1, i))
                    break
                else:
                    i += 1
            else:
                i += 1

    if not segments:
        return raw, fixes

    # 第二遍：seg 范围内修复，区间外原样拼接
    result: list[str] = []
    prev = 0
    for seg_start, seg_end in segments:
        result.append(raw[prev:seg_start])
        i = seg_start
        while i < seg_end:
            c = raw[i]
            if c == "\\":
                result.append(c)
                if i + 1 < n:
                    result.append(raw[i + 1])
                i += 2
            elif c == '"':
                j = i + 1
                while j < n and raw[j] in " \t\r\n":
                    j += 1
                if j >= n or raw[j] in ",}]":
                    result.append(c)
                    i += 1
                else:
                    result.append('\\"')
                    fixes.append(f"bare-quote@{i}")
                    i += 1
            elif c == "\n":
                result.append("\\n"); fixes.append(f"bare-newline@{i}"); i += 1
            elif c == "\t":
                result.append("\\t"); fixes.append(f"bare-tab@{i}"); i += 1
            elif c == "\r":
                result.append("\\r"); fixes.append(f"bare-cr@{i}"); i += 1
            elif "\x00" <= c <= "\x1f":
                result.append(f"\\u{ord(c):04x}"); fixes.append(f"ctrl-{ord(c):02x}@{i}"); i += 1
            else:
                result.append(c); i += 1
        prev = seg_end
    result.append(raw[prev:])
    return "".join(result), fixes


def _openai_compat_llm(
    model_id: str,
    temperature: float,
    max_tokens: int,
    timeout: float | None = None,
    max_retries: int | None = None,
) -> BaseChatModel:
    """Single OpenAI-compatible endpoint (云雾 / 自建网关等).

    ``timeout``：HTTP socket 层超时（秒），langchain 透传到 httpx/openai client。
    None = 无 timeout（保留 langchain 默认行为）。

    🔴 ``max_retries``：底层 SDK 重试几次（``None`` = 保留 SDK 默认 2 次）。
    **必须有这个参数**：本函数构造的就是 ``ChatOpenAI``，而 ``timeout`` 是
    **每次尝试**的上界 ⇒ 不定死重试次数，"这一步最多 N 秒"的硬保证拿到的是 3N。
    详见 :func:`_llm` 里那段实测记录（规划员 ``timeout=15`` 跑出 44.3 秒）。
    """
    from langchain_openai import ChatOpenAI

    if not OPENAI_COMPAT_BASE_URL:
        raise ValueError(
            "使用 OpenAI 兼容聚合时必须设置 OPENAI_COMPAT_BASE_URL 或 OPENAI_BASE_URL（例如 https://yunwu.ai/v1）"
        )
    extra: dict[str, Any] = {}
    if timeout is not None:
        extra["timeout"] = timeout
    if max_retries is not None:
        extra["max_retries"] = max_retries
    return ChatOpenAI(
        model=model_id,
        base_url=OPENAI_COMPAT_BASE_URL,
        api_key=OPENAI_COMPAT_API_KEY or None,
        temperature=temperature,
        max_tokens=max_tokens,
        **extra,
    )


def _llm(
    model: str,
    temperature: float = 0.4,
    timeout: float | None = None,
    tag: str = "unknown",
    max_tokens: int | None = None,
    max_retries: int | None = None,
) -> BaseChatModel:
    """Route to the right LangChain chat class based on model name prefix.

    max_tokens 由 `COMMITTEE_MAX_TOKENS` env 控制（默认 4096，可在 prod 调到 8192）。
    调用方可通过 max_tokens 参数覆盖（如决策 pass 用 MAX_TOKENS_DECIDE=8192）。
    详见 `committee.config.MAX_TOKENS` 注释。

    ``timeout``：HTTP socket 层超时（秒），用于需要硬超时的轻量场景
    （如 ``committee.query_class`` Phase 0a 分类器）。**真 timeout**（HTTP 层），
    不依赖 Python concurrency 原语。``None`` = 保留 langchain 默认（无 timeout
    或 provider 自身默认）。

    ``tag``：token usage tracking 标签（AH），焊进 TokenUsageCallback。并发节点
    各自构造 LLM，callback 互不干扰。

    🔴 ``max_retries``：**底层 SDK 重试几次**（``None`` = 保留 SDK 默认，
    所有既有调用方行为一字不变）。

    ⚠️ **为什么要暴露它**（2026-08-27 seg1 G7 实测查出）：``timeout`` 是
    **每次尝试**的上界，**不是总上界** —— openai SDK 客户端默认
    ``max_retries=2`` ⇒ 最坏耗时 ≈ ``timeout × 3``。实测规划员那条路
    ``timeout=15`` 却跑出 **44.3 秒**，正好三倍。
    ⇒ **谁需要"这一步最多花 N 秒"这种硬保证，就必须同时把重试次数定死**，
    只设 timeout 得到的是 3N。这正是坑表第 11 条「看似生效实则失效的超时写法」
    的一个新形态（此前记的都是 Python 并发原语那类，这次是**SDK 重试**）。
    ⚠️ 本参数目前只对走 ``ChatOpenAI`` 的分支生效；Anthropic / Gemini 分支
    **未接**（用到时再补，别默认它已经全覆盖）。

    ⚠️ **"走 ChatOpenAI 的分支"要逐条数，别按印象**（2026-09-01 review 查出）：
    ``oc/`` 前缀与 ``COMMITTEE_FORCE_OPENAI_COMPAT`` 这两条**也**构造 ``ChatOpenAI``，
    但它们经 :func:`_openai_compat_llm` 中转、只透传了 ``max_tokens``/``timeout``
    ⇒ 本参数曾在这两条路上被**静默丢弃**（已修：那个函数补了同名参数）。
    当时这段警告只点名 Anthropic / Gemini，把"经中转函数的 ChatOpenAI"漏在了
    两个清单之外 —— **中转一层就脱离了"直接构造"的直觉**，这是坑表第 11 条
    「看似生效实则失效」在参数透传上的形态。改这里时请把**全部**分支数一遍。
    """
    from committee.token_usage import (
        TokenUsageCallback, note_if_price_stale, note_if_unpriced,
    )
    from committee.trace import TraceCallback

    # 花钱之前先喊一声（可见性闸口 ①）：① 名字在不在价目表里；② 在的话价过没过期。
    # 两道都只 warn 不拦 —— 算不出钱 / 算错钱都不该让一次分析跑不起来，
    # 理由见 note_if_unpriced。
    if not note_if_unpriced(model, f"_llm(tag={tag})"):
        note_if_price_stale(model, f"_llm(tag={tag})")

    kwargs: dict[str, Any] = dict(temperature=temperature, max_tokens=max_tokens or MAX_TOKENS)
    if timeout is not None:
        kwargs["timeout"] = timeout
    if max_retries is not None:
        kwargs["max_retries"] = max_retries

    llm: BaseChatModel

    # 单端点走兼容 API：oc/<id> 或全局 COMMITTEE_FORCE_OPENAI_COMPAT=1（模型名以聚合商定价页为准）
    if model.startswith("oc/"):
        llm = _openai_compat_llm(
            model[3:].strip() or model, temperature, kwargs["max_tokens"],
            timeout, max_retries,
        )
    elif FORCE_OPENAI_COMPAT:
        llm = _openai_compat_llm(
            model, temperature, kwargs["max_tokens"], timeout, max_retries,
        )

    elif model.startswith(("claude-", "anthropic/")):
        from langchain_anthropic import ChatAnthropic
        anthropic_kwargs: dict[str, Any] = {"max_tokens": kwargs["max_tokens"]}
        if timeout is not None:
            anthropic_kwargs["timeout"] = timeout
        llm = ChatAnthropic(model=model, **anthropic_kwargs)

    elif model.startswith(("gpt-", "o1-", "o3-", "o4-", "openai/")):
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=model, **kwargs)

    elif model.startswith(("gemini-", "google/")):
        from langchain_google_genai import ChatGoogleGenerativeAI
        # NB: ChatGoogleGenerativeAI's `max_output_tokens` field carries the
        # alias `max_tokens`, so passing max_tokens=N here IS honored (verified
        # 2026-06-09).  The seg2 2026-06-05 political truncation root cause was
        # NOT a dropped param — it was gemini-2.5-pro thinking tokens consuming
        # the 4096 budget (~0.7 visible chars/token vs ~1.95 for deepseek),
        # leaving too little for the report body.  Fix is a budget/model
        # decision, tracked separately — do not "fix" by renaming the param.
        llm = ChatGoogleGenerativeAI(model=model, **kwargs)

    elif model.startswith("deepseek"):
        from langchain_openai import ChatOpenAI
        import os
        kwargs["http_client"] = httpx.Client(trust_env=False)
        kwargs["http_async_client"] = httpx.AsyncClient(trust_env=False)
        llm = ChatOpenAI(
            model=model,
            base_url=DEEPSEEK_BASE_URL,      # BJ.5 (e)：改读 config 那一份，不再各自 os.getenv
            api_key=DEEPSEEK_API_KEY or "",
            **kwargs,
        )

    else:
        from langchain_openai import ChatOpenAI
        import os
        llm = ChatOpenAI(
            model=model,
            base_url=OPENAI_BASE_URL,        # BJ.5 (e)：同上
            **kwargs,
        )

    existing = getattr(llm, "callbacks", None) or []
    try:
        # TokenUsageCallback 常驻（轻量）；TraceCallback 仅在 _TRACE 激活时记录
        # （段式 trace 模式），未激活时其 on_* 自身 no-op，复用同一 tag。
        llm.callbacks = list(existing) + [TokenUsageCallback(tag), TraceCallback(tag)]
    except AttributeError:
        pass
    return llm


def _cacheable_system(llm: BaseChatModel, system: str) -> str | list[dict[str, Any]]:
    """给 Anthropic 的 system prompt 套上可缓存标记；其余 provider 原样返回。

    **文本逐字不变** —— 只是把裸字符串换成带标记的 content block。
    LLM 看到的内容一个字都没变，变的只是账单上重复部分打不打折。

    三道闸，任一不满足就原样返回（**静默降级、绝不抛错**）：

    1. ``COMMITTEE_PROMPT_CACHE`` 开关（默认关，理由见 config 处注释）
    2. 实例类型必须是 ``ChatAnthropic`` —— **按实例判、不按模型名前缀判**。
       本仓存在聚合端点路（``oc/`` 前缀 / ``COMMITTEE_FORCE_OPENAI_COMPAT``），
       那条路上跑 claude 模型名时用的是 ``ChatOpenAI``，按名字判会把标记贴到
       不认识它的端点上。
    3. 长度粗筛（``PROMPT_CACHE_MIN_CHARS``）—— 低于门槛 API 会静默忽略标记，
       省掉套结构。门槛按词元算而这里数字符，两个方向都可能判错但都不影响
       正确性（实测换算比与两种判错的后果见 config 处注释）。

    ⚠️ 不要顺手推广到 deepseek / gemini：deepseek 是自动前缀缓存（白捡，不接受也不需要
    标记），gemini 根本没有「标记」这回事（implicit 自动、explicit 要预建缓存对象，
    是另一套东西）。实测见 docs/observations/ag-cache-meter-probe/EVIDENCE.md。
    """
    if not PROMPT_CACHE_ENABLED:
        return system
    if not isinstance(system, str) or len(system) < PROMPT_CACHE_MIN_CHARS:
        return system
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError:  # pragma: no cover - 依赖缺失时不该影响任何调用
        return system
    if not isinstance(llm, ChatAnthropic):
        return system
    return [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]


def _invoke_json(llm: BaseChatModel, system: str, user: str) -> dict:
    """底层原语：单次 invoke + JSON 提取；parse 失败时**重试一次**（更严指令）。

    重试动机：部分聚合商路由下的 Opus/GPT 偶发返回纯 markdown 正文（忽略 system
    prompt 的 JSON 约束），导致首包 ``_extract_json`` 直接 ValueError、整条 run
    崩溃。重试以"你上次的回复不是合法 JSON"为 prompt，绝大多数模型能纠正格式。

    若二次仍失败则正常抛原 ValueError——避免无限重试变相隐藏模型层 bug。
    不做长度保障、不触发续写（那是上层 ``_invoke_with_continuation`` 的事）。
    """
    messages = [SystemMessage(content=_cacheable_system(llm, system)), HumanMessage(content=user)]
    resp = llm.invoke(messages)
    text = resp.content if isinstance(resp.content, str) else str(resp.content)
    try:
        return _extract_json(text)
    except ValueError as e:
        raw_suffix = text[-200:] if len(text) > 400 else ""
        log.warning(
            "_invoke_json parse failed (retrying once with stricter instruction): %s；"
            "raw_prefix=%r raw_suffix=%r",
            e, text[:200], raw_suffix,
        )
        sanitized, fixes = _sanitize_llm_text_fields(text)
        if fixes:
            log.warning("_invoke_json sanitizer applied fixes=%r; retrying parse", fixes)
            try:
                return _extract_json(sanitized)
            except ValueError:
                pass  # sanitizer 没解决，继续走原有 retry
        retry_user = (
            f"你上一次的回复不是合法 JSON 对象（前 200 字：{text[:200]!r}）。\n"
            f"请**只**输出 JSON 对象，不要 markdown 标题、不要 ```json 围栏、"
            f"不要任何解释或说明文字。\n\n"
            f"原任务：\n{user}"
        )
        resp2 = llm.invoke([
            # 重试与首发用**同一份** system —— 打上标记后这次正是最典型的命中场景
            # （同一开头指令的第二次调用）。
            SystemMessage(content=_cacheable_system(llm, system)),
            HumanMessage(content=retry_user),
        ])
        text2 = resp2.content if isinstance(resp2.content, str) else str(resp2.content)
        return _extract_json(text2)  # 若再失败则 ValueError 上抛（不再重试）


# 续写失败重试的结构化日志 key（PR-B）。
# **不要演化这两个 key** —— 生产靠 `grep continuation_parse_failed_final` 统计
# 截断频率；`_once - _final` 即重试救回的次数。改名会破坏历史观测。
# 需要新事件（如重试成功）请新开 key，不要改写已有的。
_CONTINUATION_RETRY_SLEEP_SECONDS = 1.0


def _invoke_json_with_retry(
    llm: BaseChatModel,
    system: str,
    user: str,
    *,
    role_tag: str,
    chunk_idx: int,
) -> dict | None:
    """续写 chunk 解析的"时间间隔重试"封装（PR-B）。与 ``_invoke_json`` 内置的
    "format-repair 重试"层级不同、语义正交：

    - ``_invoke_json`` 内部：首轮输出非合法 JSON → 立刻用更严 prompt 再试一次；
      解决"模型忽视 JSON 约束"，**不睡眠**、**不换参**。
    - 本 helper（外层）：整个 ``_invoke_json`` 失败（含其内部 repair 已用完）→
      ``time.sleep(1)`` + 重发原 prompt；解决"瞬时 flaky / 模型短暂不稳"，
      不做 prompt 调整。

    失败场景严格限定为 ``ValueError`` / ``json.JSONDecodeError`` —— 不捕网络错误 /
    timeout / HTTP 5xx，那些属于 PR-C/D 的 LLM 调用层重试，责任分层避免耦合。

    返回：成功 → dict；首次 + 重试都失败 → None（调用方据此设 ``truncated_at_chunk``）。
    """
    try:
        return _invoke_json(llm, system, user)
    except (ValueError, json.JSONDecodeError) as e:
        log.warning(
            "continuation_parse_failed_once chunk=%d role=%s error=%s",
            chunk_idx, role_tag, e,
        )
    time.sleep(_CONTINUATION_RETRY_SLEEP_SECONDS)
    try:
        return _invoke_json(llm, system, user)
    except (ValueError, json.JSONDecodeError) as e:
        log.warning(
            "continuation_parse_failed_final chunk=%d role=%s truncated=true error=%s",
            chunk_idx, role_tag, e,
        )
        return None


_ENVELOPE_KEYS = frozenset({"continuation", "chunk_index", "model_self_continuation"})


def _drop_unknown_fields(
    payload: dict,
    field_policy: dict[str, FieldPolicy],
    role_tag: str,
    source: str,
) -> None:
    """Mutates `payload` in place by popping keys not declared in policy and not
    envelope metadata; emits a warning per dropped key."""
    declared = set(field_policy.keys())
    unknown = [k for k in payload.keys() if k not in declared and k not in _ENVELOPE_KEYS]
    for k in unknown:
        log.warning(
            "%s: %s 出现未声明字段 %r（已 drop）。如属业务字段请在 policy 中显式声明。",
            role_tag or "?", source, k,
        )
        payload.pop(k, None)


def _apply_initial(
    data: dict,
    field_policy: dict[str, FieldPolicy],
    role_tag: str,
) -> tuple[dict[str, object], dict[str, ClaimAccumulator]]:
    """Process the first chunk per policy. Mutates `data` in place.

    Pins immutable fields, initializes ClaimAccumulators for append_list fields,
    drops ignore-policy fields (with warning if non-empty), drops unknown fields.
    Returns (immutable_pins, accumulators) for the continuation loop.
    """
    accumulators: dict[str, ClaimAccumulator] = {}
    immutable_pins: dict[str, object] = {}
    for f, p in field_policy.items():
        if p == "immutable":
            immutable_pins[f] = data.get(f)
        elif p == "append_list":
            acc = ClaimAccumulator()
            acc.extend(data.get(f) or [], source_chunk_idx=0)
            accumulators[f] = acc
            data[f] = acc.as_list()
        elif p == "ignore":
            if data.get(f):
                log.warning(
                    "%s: ignore-policy 字段 %r 出现在首段输出（已 drop）。"
                    "该字段应由代码注入，不应由 LLM 产生。",
                    role_tag or "?", f,
                )
            data.pop(f, None)
        elif p == "replace_once":
            raise NotImplementedError("replace_once policy is reserved for V2")
        # append_text 首段保留原值，无需特殊处理
    _drop_unknown_fields(data, field_policy, role_tag, source="initial")
    return immutable_pins, accumulators


def _apply_chunk(
    data: dict,
    chunk: dict,
    field_policy: dict[str, FieldPolicy],
    immutable_pins: dict[str, object],
    accumulators: dict[str, ClaimAccumulator],
    chunk_idx: int,
    role_tag: str,
) -> None:
    """Merge one continuation chunk into `data` per policy. Mutates `data` in place."""
    for f, p in field_policy.items():
        if p == "immutable":
            if f in chunk and chunk[f] != immutable_pins[f]:
                log.warning(
                    "%s: chunk#%d 试图改写 immutable 字段 %r "
                    "(pinned=%r, attempted=%r)；已 drop 保留 pinned 值。",
                    role_tag or "?", chunk_idx, f, immutable_pins[f], chunk[f],
                )
            # data[f] 始终保持 pinned 值（不动）
        elif p == "append_text":
            new_piece = str(chunk.get(f, "") or "")
            if new_piece:
                data[f] = f"{data.get(f, '') or ''}\n\n{new_piece}".strip()
        elif p == "append_list":
            accumulators[f].extend(chunk.get(f) or [], source_chunk_idx=chunk_idx)
            data[f] = accumulators[f].as_list()
        elif p == "ignore":
            if chunk.get(f):
                log.warning(
                    "%s: chunk#%d 中 ignore-policy 字段 %r 仍被产出（已 drop）。",
                    role_tag or "?", chunk_idx, f,
                )
        elif p == "replace_once":
            raise NotImplementedError("replace_once policy is reserved for V2")
    _drop_unknown_fields(chunk, field_policy, role_tag, source=f"chunk#{chunk_idx}")


def _invoke_with_continuation(
    llm: BaseChatModel,
    system: str,
    user: str,
    *,
    field_policy: dict[str, FieldPolicy],
    length_field: str,
    min_chars: int,
    max_continuations: int,
    on_chunk: Callable[[dict, int, bool], None] | None = None,
    role_tag: str = "",
    continuation_hint: str = "",
) -> dict:
    """编排层：在 `_invoke_json` 之上做长度保障与续写循环，按 field policy 分发合并。

    Field policy contract (plan §3.1 PR 1):
      Field policy governs ONLY persisted business fields. Envelope/control
      fields (continuation, chunk_index, model_self_continuation) are handled
      outside the merge policy by this helper itself.
        - immutable    : pinned from first call; later attempts to change
                         trigger warning and are dropped.
        - append_text  : concat with `\\n\\n`.
        - append_list  : routed through ClaimAccumulator (literal dedup +
                         source chunk_index metadata).
        - ignore       : LLM not allowed to set; dropped with warning if non-empty.
        - replace_once : reserved for V2; raises NotImplementedError if used.
      Unknown fields (not in policy, not envelope) are warning-logged and dropped.
      Per-policy dispatch lives in `_apply_initial` / `_apply_chunk`; this function
      owns control flow + envelope (continuation / chunk_index / model_self_continuation)
      + on_chunk emission only.

    返回值契约：
    - 返回 dict 的 `continuation` 字段**始终为 False**——给调用方/持久化层的"最终封箱"
      信号。helper 内部的中间自评在循环中读取做停止判断，但退出前统一清零。
    - 模型最后一次自评原值保留在 `model_self_continuation`（仅诊断；Pydantic schema
      未声明该字段，model_validate 时自动 drop，不污染持久化对象）。

    停止条件 = `len(str(data[length_field])) >= min_chars` AND model_done。
    `continuation=false` 但长度不足 → 继续。
    `continuation=true` 但长度达标 → 跑一次收尾，max_continuations 兜底。

    续写 JSON 解析失败 → log.warning 并终止循环，返回已有内容。

    continuation_hint (PR 2 §B.0)：
      用于在每轮续写 prompt **前部**（紧跟上段 JSON）追加固定提醒（如"按既定结构展开"），
      用极小 token 成本刷新结构存在感。**位置故意前置**：放在 cont_user 末尾会被字数
      要求/merge 规则/immutable 列表稀释注意力，导致后段漂移。**故意不重新注入完整
      outline**——那会让续写 token 倍增，违背本 PR 不引入二级 prompt 增长的边界。
      不传则等价空串，与 PR 1 行为完全一致（debate 节点无需迁移）。
    """
    data = _invoke_json(llm, system, user)
    data.setdefault("chunk_index", 0)

    immutable_pins, accumulators = _apply_initial(data, field_policy, role_tag)

    if on_chunk:
        on_chunk(data, 0, True)  # 首包 = initial（完整首段，非增量）

    # 与 policy.mergeable_keys() 同源；提到循环外避免每轮重算。
    mergeable_field_names = mergeable_keys(field_policy)

    for i in range(1, max_continuations + 1):
        length_ok = len(str(data.get(length_field, ""))) >= min_chars
        model_done = not bool(data.get("continuation", False))
        if length_ok and model_done:
            break

        current_len = len(str(data.get(length_field, "")))
        # hint **前置**到上段 JSON 之后、字数要求之前——位置即权重。
        hint_block = f"\n\n{continuation_hint}\n" if continuation_hint else ""
        cont_user = (
            f"上一段你的部分回答（JSON）：\n{json.dumps(data, ensure_ascii=False)}"
            f"{hint_block}\n"
            f"当前 `{length_field}` 字符数 {current_len}，目标 ≥ {min_chars}。\n"
            f"请续写新内容（严禁重复既有文字），输出同一 JSON schema；\n"
            f"仅在以下字段给出**新增**内容：{mergeable_field_names}；\n"
            f"以下字段已锁定，必须与上段保持一致："
            f"{json.dumps(immutable_pins, ensure_ascii=False)}\n"
            f"若已充分请设 continuation=false。"
        )
        chunk = _invoke_json_with_retry(
            llm, system, cont_user, role_tag=role_tag, chunk_idx=i,
        )
        if chunk is None:
            data["truncated_at_chunk"] = i
            break

        _apply_chunk(data, chunk, field_policy, immutable_pins, accumulators, i, role_tag)

        data["continuation"] = bool(chunk.get("continuation", False))
        data["chunk_index"] = i
        if on_chunk:
            on_chunk(chunk, i, False)

    # 退出前统一清零（见上方 docstring "返回值契约"）：
    # 把模型最后一次自评搬到 model_self_continuation，再把 continuation 强制置 False。
    # 这一步必须无条件执行——包括 max_continuations=0、循环未进入的路径。
    data["model_self_continuation"] = bool(data.get("continuation", False))
    data["continuation"] = False

    # V1 字面去重未捕获的近义重复 → log.info 供 V2 决策（见 ClaimAccumulator.near_duplicate_pairs）。
    for fname, acc in accumulators.items():
        suspects = acc.near_duplicate_pairs()
        if suspects:
            log.info(
                "%s: %s 发现 %d 对疑似近义重复（V1 字面去重未捕获）：%s",
                role_tag or "?", fname, len(suspects),
                [(a, b, round(r, 2)) for a, b, r in suspects[:3]],  # 截前 3 对避免日志爆炸
            )

    return data


# ---------- Phase 1: analyst / advisor ----------

def _tool_usage_guidance(rounds: int) -> str:
    """工具使用引导：提纲先行 + 一轮查全 + 不重复（注入开了工具的角色的 user 消息）。

    引导而非硬约束——真正的成本闸门是 run_tool_agent 的 max_iterations（轮数）+
    web_search_budget（搜索总数兜底）。本段只让模型"用好"有限轮次。
    """
    return (
        f"\n\n【工具使用指引】你有 web_search 等工具，最多 {rounds} 轮搜索机会。"
        "请先看上方【数据来源】(common_context) 已经给了什么、还缺什么，"
        "在心里列出你想知道的信息提纲；第一轮就把不同角度的查询一次性查全"
        "（可一次发起多个搜索，会并发执行），不要重复搜同一主题，"
        "common_context 已有的数字/事实不要再搜。"
    )


def _analyst_text_len(data: dict) -> int:
    """analyst 长度度量：4 个 list 字段字符串内容总字符数。"""
    total = 0
    for k in ("key_points", "bullish_factors", "bearish_factors", "risks"):
        for s in data.get(k) or []:
            total += len(str(s))
    return total


# RISK-1: exception types that are almost always *programming bugs*, not transient
# LLM / network / API faults. The analyst fan-out catches a broad ``Exception`` to keep
# stability (Priority 1 — one role's failure must not crash the run), but a broad catch
# can silently mask these as if they were transient. We don't change control flow (still
# degrade to fallback), but we log them at ERROR with a traceback so they surface instead
# of hiding behind a WARNING. Denylist (not a transient allowlist) so a *new* network /
# API error type defaults to the safe WARNING path, never to a crash.
_LIKELY_BUG_EXCEPTIONS: tuple[type[BaseException], ...] = (
    KeyError, AttributeError, TypeError, IndexError, NameError, ImportError, AssertionError,
)


def make_analyst_node(role_key: str) -> Callable[[CommitteeState], Any]:
    """分析师：tool-use agent loop（白名单内）或单次调用（白名单外）+ 一次性扩写。

    白名单（``WEB_SEARCH_ROLES``）内的角色走 ``run_tool_agent``：LLM 可在循环中调用
    数据源工具 + web_search，再产出最终 JSON 报告。白名单外保持单次 ``_invoke_json``。
    扩写（``MIN_CHARS_ANALYST``）不绑工具——目的是补字数而非取数，避免双倍搜索成本。

    节点为 ``async``：LangGraph ``astream``/``ainvoke`` 原生 await；工具调用是外部
    HTTP（httpx 透传 timeout 到 socket），并行 analyst 节点可真正并发。单次 invoke /
    扩写走 ``asyncio.to_thread`` 包裹同步 ``_invoke_json``，复用其 sanitize/retry 逻辑
    且不阻塞事件循环。

    headline 刻意不在扩写时更新——扩写定位是「补充要点」而非「重写判断」，
    避免 headline 来回变动造成不一致。
    """
    meta = ROLES[role_key]
    system = SYSTEM_PROMPTS[role_key]
    state_key = f"{role_key}_report"

    async def node(state: CommitteeState) -> dict:
        from committee.tools import ALL_TOOLS, run_tool_agent

        # AM (backlog): academic/advisory 角色（political/historian/economist）带 raw-last
        # 抗截断硬规则，但截断根须靠预算而非字段顺序（deepseek 不遵守 raw-last / gemini
        # thinking 吃预算）→ 给足 max_tokens 从根上不截断。下限语义：全局 MAX_TOKENS 调更
        # 高则跟随。非 advisory 角色 max_tokens=None → _llm 回退全局 MAX_TOKENS（行为不变）。
        _max_tokens = max(MAX_TOKENS, MAX_TOKENS_ACADEMIC) if meta.tier == "advisory" else None
        llm = _llm(meta.model, temperature=TEMP_ANALYST, tag=role_key, max_tokens=_max_tokens)
        user = f"研究任务: {state['query']}\n\n额外上下文:\n{state.get('context', '（无）')}"

        # 注入 common_context watermark — analyst 需要看到 [REF#X-NNN] 数据来源
        ctx = state.get("common_context")
        if ctx is not None:
            ctx_block = _format_common_context_for_debate(ctx)
            if ctx_block:
                user += f"\n\n=== 数据来源（Data Provenance）===\n{ctx_block}\n"

        # FM-pipeline.1: fundamentals on non-ticker queries → scope hint
        if role_key in _FUNDAMENTALS_OUT_OF_SCOPE_ROLES and not _is_ticker_query(state):
            user += (
                "\n\n【注意】本次查询非个股标的，无公司级基本面数据。"
                "对于需要个股财务数据的指标（估值、财报、护城河深度等），"
                "请标记 DATA_INSUFFICIENT 并在 evidence_log 中注明缺失原因。"
                "仍可基于宏观数据和行业信息提供可用分析。\n"
            )

        # AA backlog fix: if this analyst was previously rejected by triage, append
        # the failure notes so the LLM knows exactly what to fix (not a blind retry).
        rework_notes = state.get("rework_notes", {})
        if rework_notes and role_key in rework_notes:
            notes_str = "; ".join(rework_notes[role_key])
            user += (
                f"\n\n【重要】你的上一次输出已被质量检查拒绝，原因: {notes_str}。"
                "请针对性修正上述问题后重新输出完整报告。"
            )

        use_tools = role_key in WEB_SEARCH_ROLES
        # AO web-provenance: 捕获 analyst web_search 的 tool_outputs（URL/title/description
        # 在 result JSON 串里），透传到共享 web_provenance 供下游 code 侧域名印证。默认空：
        # 非 web_search 角色 / 调用失败 fallback → 不写 web_provenance（reducer add 空=无害）。
        tool_outputs: list[dict] = []
        try:
            if use_tools:
                data, tool_outputs = await run_tool_agent(
                    llm,
                    system,
                    user + _tool_usage_guidance(WEB_SEARCH_MAX_ITERATIONS),
                    ALL_TOOLS,
                    max_iterations=WEB_SEARCH_MAX_ITERATIONS,
                    web_search_budget=WEB_SEARCH_MAX_CALLS,
                    extract_json_fn=_make_tool_json_extractor(role_key, meta.model),
                    role_tag=role_key,
                    return_tool_outputs=True,
                )
            else:
                data = await asyncio.to_thread(_invoke_json, llm, system, user)
        except Exception as e:
            # Robustness (2026-05-29 e2e): a transient LLM / API / tool failure for ONE
            # analyst must not crash the whole parallel Phase-1 fan-out. Degrade to a
            # fallback report so triage/debate/vote continue with the remaining roles.
            # Catch Exception (not BaseException) so CancelledError — cooperative
            # cancellation — still propagates and isn't swallowed.
            # RISK-1: classify so a programming bug doesn't hide behind a transient-looking
            # WARNING. Control flow is identical (both branches degrade to fallback).
            if isinstance(e, _LIKELY_BUG_EXCEPTIONS):
                log.error(
                    "analyst %s: non-transient %s — likely a bug, not an LLM/API fault "
                    "(still degrading to fallback to protect the parallel fan-out)",
                    role_key, type(e).__name__, exc_info=True,
                )
            else:
                log.warning(
                    "analyst %s: LLM/tool call failed (%s): %s — degrading to fallback report",
                    role_key, type(e).__name__, e,
                )
            report, _ = validate_with_fallback(
                {"role": role_key, "raw": f"analyst {role_key} 调用失败（{type(e).__name__}）：{e}"},
                role_key,
            )
            return {state_key: report}
        except (KeyboardInterrupt, SystemExit):
            # 用户主动中断 / 解释器退出：不是 C1 信号。不记 —— 否则一次 Ctrl-C 会让
            # 8 个并行 analyst 各吐一条带栈 ERROR，把下面那条日志的信号意义冲淡。
            raise
        except BaseException as e:  # noqa: BLE001 — 只记录，立刻原样 re-raise
            # C1 可观测性（2026-08-10 归因后加）。**控制流一字未改**：仍然 re-raise，
            # 上面那条 "let CancelledError propagate" 的设计选择原样保留。
            #
            # 但它依赖的前提已被实测推翻：注释假设"传上去 = 有人接、不会被吞"，
            # 而实测传上去就是**被 langgraph 并行分支静默吞掉** —— 正是它想避免的
            # "swallowed"。2026-08-03 run1 实证过一次（analyst 无声消失、键缺席非为空）。
            #
            # 📚 **各异常类型的实测行为表 = 单一真值源在**
            #    docs/observations/seg2-c1-probe-2026-08-10.md §2
            #    （此处刻意不复制那张表：它随 langgraph 版本变，抄多份必然三处一起 stale
            #      —— 2026-08-10 /review 🟡4）。
            #
            # ⚠️ **本条日志的失效条件（写死，别等人想起来）**：ERROR 级预设了
            #    "取消 = 异常事件"。当前成立（生产无任何路径会主动取消 analyst）。
            #    **一旦取消变成正常路径**——加整跑 wall-clock 时限 / API 侧请求取消
            #    能传到这层 / 给 analyst 扇出加超时——8 个 analyst 会同时喷 ERROR + 栈，
            #    **全是误报**。届时本条须降级为 WARNING 或 INFO，并重估措辞。
            #    做上述任一改动的人：请连本条一起改。
            #
            # 措辞只陈述**已确证的事实**（未被捕获 + 继续上抛），后果写成依类型而定
            # ——原文曾写死"报告将整个缺失"，那只对裸 CancelledError 成立
            #  （同 backlog BF 记过的"措辞与语义不符"形态·/review 🟠2 已订正）。
            # 账：backlog DEFECT-SEG2-FLAKY（C1 行）。
            log.error(
                "analyst %s: BaseException %s 未被兜底捕获（兜底只捕 Exception，见上），继续上抛"
                " —— 后果依类型而异：裸 CancelledError 会被 langgraph 并行分支静默吞掉"
                "（本角色报告整个缺失、非降级为兜底报告）；BaseExceptionGroup 则会中断整跑。"
                "这是本条路径上唯一的证据留存点",
                role_key, type(e).__name__, exc_info=True,
            )
            raise
        data["role"] = role_key

        if MIN_CHARS_ANALYST > 0 and _analyst_text_len(data) < MIN_CHARS_ANALYST:
            current = _analyst_text_len(data)
            ext_user = (
                f"上一段你的分析报告（JSON）：\n{json.dumps(data, ensure_ascii=False)}\n\n"
                f"key_points / bullish_factors / bearish_factors / risks 当前总字符 {current}，"
                f"目标 ≥ {MIN_CHARS_ANALYST}。请补充新的要点（新增项，不要重复既有文字），"
                f"输出同一 JSON schema。**不要修改 headline / conviction / role / raw**，"
                f"只在四个列表中新增条目。"
            )
            try:
                extra = await asyncio.to_thread(_invoke_json, llm, system, ext_user)
                for k in ("key_points", "bullish_factors", "bearish_factors", "risks"):
                    existing = data.setdefault(k, [])
                    for x in extra.get(k) or []:
                        if x not in existing:
                            existing.append(x)
            except Exception as e:  # noqa: BLE001 — 扩写是锦上添花，任何失败都退回原报告
                # #312 review（2026-09-22）：原只捕 (ValueError, JSONDecodeError)，而本段在主调用的
                # try/except 之外 —— 网络超时 / provider 异常这类**更常见**的扩写失败会从节点直接穿出，
                # 既不落兜底报告也不留痕（review 坐实，非推断：1084-1105 行不在任何 try 里）。
                # 初版 except 范围来自 initial import、无设计记录；按本段自己的意图（保留原报告）放宽。
                # BaseException（取消 / 退出）不在此列，仍原样上抛。
                log.warning("analyst %s 一次性扩写失败: %s；保留原报告", role_key, e)
                # BK.6（2026-09-22·盘点 #25）：保留的是那份不够长的原报告，读者看不出「要求过扩写、没成」。
                note_degradation(
                    "analyst_expand_failed",
                    f"role={role_key}; chars={current}<{MIN_CHARS_ANALYST}; err={type(e).__name__}",
                )

        report, quality = validate_with_fallback(data, role_key)
        if quality != "full":
            log.warning("analyst %s: report quality=%s", role_key, quality)
        if quality == "sanitized":
            # BK.2 M4.1（2026-09-21）：「洗过才过关」留痕。**只这一支** —— fallback 那档由
            # 兜底报告的 headline 标记（analyst_fallback_report 读法）报，上面的调用失败分支
            # 只会落 fallback、不会落 sanitized。三档收报行为一字不改；detail 记被洗的顶层字段
            # （≤ 5 个，超出只记个数），永远不进提示词。09-21 量基线：218 份历史报告 6 份洗过、
            # 23 跑 3 跑（13%）→ 进用户面（拆解 §5 裁 C：< 1/3 不落 TRACE_ONLY）。
            _fields = sanitized_fields(data)
            _shown = ", ".join(_fields[:5]) + (f" +{len(_fields) - 5}" if len(_fields) > 5 else "")
            note_degradation("report_sanitized", f"role={role_key}; fields={_shown}")
        out: dict = {state_key: report}
        if tool_outputs:
            # AO: 与 {role}_report 同一 return 写 web_provenance → skip-wrapper 原子覆盖，
            # 已完成 analyst resume 不重复 append。每条带 role 便于溯源/debug。保真全存
            # raw tool_outputs（消费者 count_corroborating_domains 自筛 tool=="web_search"）。
            out["web_provenance"] = [{"role": role_key, **o} for o in tool_outputs]
        return out

    node.__name__ = f"analyst_{role_key}"
    return node


# ---------- Phase 2: debate ----------

def _format_reports(reports: list[AnalysisReport]) -> str:
    chunks = []
    for r in reports:
        chunks.append(
            f"### {r.role} | headline: {r.headline} | conviction: {r.conviction}\n"
            f"key_points: {r.key_points}\n"
            f"bullish: {r.bullish_factors}\n"
            f"bearish: {r.bearish_factors}\n"
            f"risks: {r.risks}\n"
        )
    return "\n".join(chunks)


def _format_debate(
    turns: list[DebateTurn],
    up_to_round: int | None = None,
) -> str:
    filtered = turns if up_to_round is None else [t for t in turns if t.round < up_to_round]
    if not filtered:
        return ""
    return "\n\n".join(
        f"[Round {t.round} {t.side} {t.stage}] {t.content}" for t in filtered
    )


def _format_common_context_for_debate(ctx: CommonContext) -> str:
    """Render CommonContext as a text block consumable by debate nodes (Round 2+)."""
    from committee.common_context.watermark import render_watermark_section

    parts: list[str] = []
    payload = ctx.payload  # PR2：读真值（与改前 ticker_payload or macro_payload 逐字节相同）
    if payload:
        parts.append(json.dumps(payload, ensure_ascii=False, indent=2))
    if ctx.references:
        wm_text = render_watermark_section(ctx.references)
        if wm_text:
            parts.append(wm_text)
    return "\n".join(parts) if parts else ""


_DEBATE_DELTA_KEYS = mergeable_keys(DEBATE_POLICY)

_OPPOSITE_SIDE = {"bull": "bear", "bear": "bull"}


def _get_opponent_claims(debate_log: list[DebateTurn], round_num: int, side: str) -> list[str]:
    """Extract key_claims from the opponent's turn in the same round."""
    opp = _OPPOSITE_SIDE.get(side, "")
    claims: list[str] = []
    for t in debate_log:
        if t.round == round_num and t.side == opp:
            claims.extend(t.key_claims)
    return claims


def _get_prior_round_claims(debate_log: list[DebateTurn], round_num: int) -> list[str]:
    """Extract key_claims from all turns in rounds before round_num."""
    claims: list[str] = []
    for t in debate_log:
        if t.round < round_num:
            claims.extend(t.key_claims)
    return claims


def _coerce_debate_key_claims(raw: Any) -> tuple[list[str] | None, dict, list[str], list[str]]:
    """把辩论发言里坏掉的 ``key_claims`` 整理成字符串列表（BK.2 M4-fix·2026-09-21·照 #304）。

    规则（用户 09-21 裁「逐项校验、对象型条目取 claim 字段、其余保住 + 留痕记原值」）：
    字符串 → 原样保留；带非空字符串 ``claim`` 的对象 → 取出 ``claim``；其余条目 → 略过。
    整个值不是列表 → 返回 ``None``（调用方删掉该字段、交给 schema 默认的空列表）。

    Returns:
        ``(整理后的列表或 None, 计数, 取出论点条目的样本, 被略过条目的样本)`` ——
        取出论点的条目只记**被丢弃的其余字段**，被略过的条目记整条原值。
        两份样本分开，供两个码各记各的（#309 review：一码一义，照 M3.2 裁 B）。
    """
    if not isinstance(raw, list):
        return None, {"non_list": type(raw).__name__}, [], [f"non_list={_clip_dropped_item(raw)}"]
    out: list[str] = []
    counts = {"kept": 0, "coerced": 0, "dropped": 0}
    coerced_samples: list[str] = []
    dropped_samples: list[str] = []
    for i, item in enumerate(raw):
        if isinstance(item, str):
            out.append(item)
            counts["kept"] += 1
        elif isinstance(item, dict) and isinstance(item.get("claim"), str) and item["claim"].strip():
            out.append(item["claim"])
            counts["coerced"] += 1
            # 论点文字已进要点清单；留痕记**被丢掉的那部分**（confidence / evidence 等），
            # 否则一段长论点就占满截断长度、真正丢掉的信息一个字都没留下。
            rest = {k: v for k, v in item.items() if k != "claim"}
            coerced_samples.append(f"#{i + 1}: 丢弃字段={_clip_dropped_item(rest)}")
        else:
            counts["dropped"] += 1
            dropped_samples.append(f"#{i + 1}: {_clip_dropped_item(item)}")
    return out, counts, coerced_samples, dropped_samples


# 一段辩论发言校验后**待发**的便条：``(码, detail)``。由环节出口对**最终采用**的那条发言发出
# （#309 review finding 1）：便条若在校验时当场发，首轮被整理过、随后又被 F 类返工替换掉，
# 归档里就留一条「发言正文完整保留」却指着一条已不存在的发言；两次都整理则一段发言发两次。
DebatePendingNotes = list[tuple[str, str]]


def _validate_debate_turn(
    data: dict, *, side: str, round_num: int, stage: str,
) -> tuple[DebateTurn, DebatePendingNotes]:
    """校验一段辩论发言；**只在校验失败、且问题出在 key_claims 时**整理这一项再校验一次。

    **治的病**（BK.2 M4.0 量基线查出·1/91）：模型把 ``key_claims`` 写成带 claim / confidence /
    evidence 的对象列表，schema 只认字符串列表 → 整段发言校验失败 → 生产把**整段陈词**换成
    「解析失败，已降级」占位（实例：空头总结陈词 1571 字全丢）。一个小字段让整份产物作废，
    与大纲小修 #304 同形态、照同一先例治：坏字段整理掉，发言保住，留痕记原值。

    行为边界（刻意）：
    - 校验一次就过 → 原样返回，一个字不碰、不留痕（待发便条为空）；
    - 失败但不涉及 key_claims → **原样抛出**，调用方照旧换占位（日志一字不改）；
    - 整理后仍不过（别的字段也坏）→ 抛**原来那个**异常，同上。

    留痕**两码两义**（#309 review finding 2·照 BK.2 M3.2 裁 B「一码一义」）：
    - 有条目取出了论点文字 → ``debate_key_claims_coerced``（要点还在，只是附带字段没了）；
    - 有条目取不出、被略过 / 整个值不是列表被清空 → ``debate_key_claims_dropped``（要点清单少了这些）。
    一段发言两种情况都有则两条都发。便条**不在这里发**、只返回给调用方（见 :data:`DebatePendingNotes`）。
    """
    try:
        return DebateTurn.model_validate(data), []
    except pydantic.ValidationError as e:
        bad = {str(err["loc"][0]) for err in e.errors() if err.get("loc")}
        if "key_claims" not in bad:
            raise
        fixed, counts, coerced_samples, dropped_samples = _coerce_debate_key_claims(data.get("key_claims"))
        retry = {k: v for k, v in data.items() if k != "key_claims"}
        if fixed is not None:
            retry["key_claims"] = fixed
        try:
            turn = DebateTurn.model_validate(retry)
        except pydantic.ValidationError:
            raise e from None
        tally = "; ".join(f"{k}={v}" for k, v in counts.items())
        log.warning(
            "debate %s_%s r%d: key_claims 格式不对，已整理后保住整段发言（%s）",
            side, stage, round_num, tally,
        )
        head = f"side={side}; round={round_num}; stage={stage}; {tally}"
        pending: DebatePendingNotes = []
        if counts.get("coerced"):
            pending.append((
                "debate_key_claims_coerced",
                f"{head}; samples={json.dumps(coerced_samples[:_DROPPED_MAX_ITEMS], ensure_ascii=False)}",
            ))
        if dropped_samples:
            pending.append((
                "debate_key_claims_dropped",
                f"{head}; samples={json.dumps(dropped_samples[:_DROPPED_MAX_ITEMS], ensure_ascii=False)}",
            ))
        return turn, pending


def make_debate_node(side: str, stage: str, round_num: int) -> Callable[[CommitteeState], dict]:
    key = f"{side}_{stage}"
    meta = ROLES[side]  # "bull" / "bear"

    def node(state: CommitteeState) -> dict:
        llm = _llm(meta.model, temperature=TEMP_DEBATE, tag=f"debate_{side}_{stage}")
        reports_block = _format_reports(collect_reports(state))
        prior_debate = _format_debate(state.get("debate_log", []), up_to_round=round_num)

        ctx_block = ""
        if round_num >= 2:
            ctx = state.get("common_context")
            if ctx is not None:
                ctx_block = _format_common_context_for_debate(ctx)

        user_parts = [f"主题: {state['query']}\n"]
        user_parts.append(f"=== 分析师报告汇总 ===\n{reports_block}\n")
        if ctx_block:
            user_parts.append(f"=== 原始数据参考 ===\n{ctx_block}\n")
        user_parts.append(f"=== 既往辩论记录 ===\n{prior_debate or '（尚无）'}\n")
        user_parts.append("请进行本轮发言。")
        user = "\n".join(user_parts)

        def _on_chunk(chunk: dict, idx: int, is_initial: bool) -> None:
            emit_chunk(
                "debate_turn_chunk",
                chunk,
                idx,
                is_initial,
                allowed_keys=_DEBATE_DELTA_KEYS,
                round=round_num,
                side=side,
                stage=stage,
            )

        data = _invoke_with_continuation(
            llm,
            DEBATE_PROMPTS[key],
            user,
            field_policy=DEBATE_POLICY,
            length_field="content",
            min_chars=MIN_CHARS_DEBATE,
            max_continuations=MAX_CONTINUATIONS,
            on_chunk=_on_chunk,
            role_tag=f"debate:{key}",
        )
        data.setdefault("round", round_num)
        data.setdefault("side", side)
        data.setdefault("stage", stage)
        # continuation 已由 _invoke_with_continuation 统一清零（见其 docstring "返回值契约"）；
        # 这里不再重复清零，避免"谁负责清零"的认知重复。
        pending_notes: DebatePendingNotes = []
        try:
            turn, pending_notes = _validate_debate_turn(data, side=side, round_num=round_num, stage=stage)
        except Exception as e:
            # AE backlog fix: malformed debate output must not crash the whole pipeline.
            # Fallback to a minimal placeholder turn so Phase 2 continues degraded.
            log.warning(
                "make_debate_node: DebateTurn.model_validate failed (%s): %s "
                "— using placeholder turn (side=%s round=%d)",
                type(e).__name__, e, side, round_num,
            )
            turn = DebateTurn(
                side=side,
                stage=stage,
                round=round_num,
                content=f"（{side} Round {round_num} 解析失败，已降级）",
            )

        # F-class visibility compliance check + single rework
        debate_log = state.get("debate_log", [])
        opp_claims = _get_opponent_claims(debate_log, round_num, side)
        prior_claims = _get_prior_round_claims(debate_log, round_num)
        f_results = run_f_class(turn, round_num, opp_claims, prior_claims)

        f_failed = [r for r in f_results.values() if r.status == "fail"]

        # F3 observation-only: if the only failures are F3 and F3 is in
        # placeholder-threshold observation mode, skip rework (log only).
        f_needs_rework = f_failed
        if _F3_OBSERVATION_ONLY and f_failed:
            non_f3 = [r for r in f_failed if r.rule_id != "F3"]
            if not non_f3:
                # All failures are F3 — observation only, skip rework
                log.info(
                    "F3 observation (no rework): side=%s round=%d rules=%s",
                    side, round_num, [r.rule_id for r in f_failed],
                )
                turn.f_check_reworked = False
                turn.f_check_failed = [r.rule_id for r in f_failed]
                f_needs_rework = []

        if f_needs_rework:
            log.warning(
                "F-class violation (attempt 1): side=%s round=%d rules=%s",
                side, round_num, [r.rule_id for r in f_failed],
            )
            violation_warning = (
                "\n\n【可见性违规警告】你的上一次回答违反了分轮可见性规则："
                + "；".join(r.reason for r in f_failed)
                + "。请重新回答，严格遵守当前轮次的信息边界。"
            )
            data = _invoke_with_continuation(
                llm,
                DEBATE_PROMPTS[key],
                user + violation_warning,
                field_policy=DEBATE_POLICY,
                length_field="content",
                min_chars=MIN_CHARS_DEBATE,
                max_continuations=MAX_CONTINUATIONS,
                on_chunk=_on_chunk,
                role_tag=f"debate:{key}:rework",
            )
            data.setdefault("round", round_num)
            data.setdefault("side", side)
            data.setdefault("stage", stage)
            # 返工版**取代**首轮发言 ⇒ 首轮校验时攒下的待发便条一并作废（#309 review finding 1）：
            # 便条只描述最终采用的那条发言。返工解析失败换占位时同理清空。
            try:
                turn, pending_notes = _validate_debate_turn(data, side=side, round_num=round_num, stage=stage)
            except Exception as e:
                log.warning(
                    "make_debate_node rework: DebateTurn.model_validate failed (%s): %s "
                    "— using placeholder turn (side=%s round=%d)",
                    type(e).__name__, e, side, round_num,
                )
                pending_notes = []
                turn = DebateTurn(
                    side=side,
                    stage=stage,
                    round=round_num,
                    content=f"（{side} Round {round_num} rework 解析失败，已降级）",
                )

            f_results = run_f_class(turn, round_num, opp_claims, prior_claims)
            f_still_failed = [r for r in f_results.values() if r.status == "fail"]
            if f_still_failed:
                log.warning(
                    "F-class violation persists after rework: side=%s round=%d rules=%s",
                    side, round_num, [r.rule_id for r in f_still_failed],
                )
            turn.f_check_reworked = True
            turn.f_check_failed = [r.rule_id for r in f_still_failed]
        elif not f_failed:
            turn.f_check_failed = []

        # 只对最终进 debate_log 的这条发言留痕（首轮被返工替换的那次不发）。
        for code, detail in pending_notes:
            note_degradation(code, detail)
        return {"debate_log": [turn]}

    node.__name__ = f"debate_{side}_{stage}"
    return node


# ---------- Phase 3: vote ----------
# 投票节点不走续写：输出短（单句 reasoning + vote 枚举）、结构刚性强、长度非瓶颈。
# 若后续发现需要扩展，可复用 _invoke_with_continuation。

_FUNDAMENTALS_OUT_OF_SCOPE_ROLES = frozenset({"fundamentals"})


def _is_ticker_query(state: CommitteeState) -> bool:
    """本次有没有一家具体公司当主角 —— 问腿清单，不问格子（DEFECT-CTX-BAG-SHAPE·PR2）。"""
    from committee.common_context.questions import has_equity_leg

    return has_equity_leg(state.get("common_context"))


def make_vote_node(role_key: str) -> Callable[[CommitteeState], dict]:
    meta = ROLES[role_key]

    def node(state: CommitteeState) -> dict:
        # FM-pipeline.1: fundamentals on non-ticker queries → auto DATA_INSUFFICIENT
        if role_key in _FUNDAMENTALS_OUT_OF_SCOPE_ROLES and not _is_ticker_query(state):
            log.info("vote_%s: non-ticker query → auto DATA_INSUFFICIENT (skip LLM)", role_key)
            vote = Vote(
                role=role_key,
                vote=VoteDirection.NEUTRAL,
                conviction=1,
                position_suggestion="观望",
                reasoning="DATA_INSUFFICIENT: 非个股查询，基本面分析师不具备投票依据",
            )
            return {"votes": [vote]}

        llm = _llm(meta.model, temperature=TEMP_VOTE, tag=f"vote_{role_key}")
        reports_block = _format_reports(collect_reports(state))
        debate_block = _format_debate(state.get("debate_log", []))
        user = (
            f"主题: {state['query']}\n\n"
            f"=== 分析师报告 ===\n{reports_block}\n\n"
            f"=== 辩论全文 ===\n{debate_block}\n\n"
            f"请投票。"
        )
        system = VOTE_PROMPT.format(role=role_key, name_zh=meta.name_zh)
        data = _invoke_json(llm, system, user)
        data["role"] = role_key
        try:
            vote = Vote.model_validate(data)
        except Exception as e:
            # AE backlog fix: malformed vote output must not crash Phase-3 fan-out.
            # Fallback to DATA_INSUFFICIENT so tally still aggregates correctly.
            log.warning(
                "make_vote_node: Vote.model_validate failed for %s (%s): %s "
                "— falling back to DATA_INSUFFICIENT vote",
                role_key, type(e).__name__, e,
            )
            vote = Vote(
                role=role_key,
                vote=VoteDirection.NEUTRAL,
                conviction=1,
                position_suggestion="观望",
                reasoning=f"DATA_INSUFFICIENT: 投票解析失败 ({type(e).__name__})",
            )
        return {"votes": [vote]}

    node.__name__ = f"vote_{role_key}"
    return node


# ---------- Phase 4: final decision ----------

# Section 扩写与 outline fallback 用到的常量（PR 3）。
# _OVERLAP_* 是续写块去重的 character-level 阈值；threshold = 30 字是经验值——
# 中文一段话约 30-40 字传达一个完整意思，>30 字重叠基本能确定是 paraphrase 重复。
_OVERLAP_WINDOW = 40
_OVERLAP_TAIL_WINDOW = 200
_OVERLAP_THRESHOLD = 30


def _hit(needle: str, haystack: str) -> bool:
    """关键词命中检查（head-4 + tail-4 双锚，PR 2 修复版，PR 3 提到模块顶层）。

    英文（有空格）→ 取前两词作关键词；
    中文（无空格）→ 首 4 + 末 4 双锚，避免修饰词命中、核心词漏掉。
    注意 ``str.split()`` 对 "宏观利好" 返回 ``["宏观利好"]`` 而非 ``[]``，
    所以必须显式看是否含空格，不能 ``if not kws`` 判空——这是 PR 2 自审时
    发现的 bug。

    PR 3 改动：从 ``make_decision_node`` 内部 closure 提到模块顶层，签名
    显式化为 ``(needle, haystack)``——section 循环里要对每段独立调用。
    """
    if " " in needle:
        kws = [k for k in needle.split() if k][:2]
    else:
        kws = [needle[:4], needle[-4:]] if len(needle) >= 4 else [needle]
    return any(k in haystack for k in kws)


def _piece_is_duplicate(new_piece: str, existing: str) -> tuple[bool, str]:
    """续写块去重最小防护（PR 3）。两层字符串检查：

    1. 字面 substring：``new_piece`` 整段已在 ``existing`` 中 → 重复。
    2. head/tail overlap：``new_piece`` 首 40 字与 ``existing`` 末 200 字
       的后缀/前缀匹配长度 > 30 字 → 判定 paraphrase 重复。

    返回 ``(is_duplicate, reason)``；reason 用于 warning 日志归因。

    设计选择：不做 NLP 相似度（如 ``SequenceMatcher.ratio``）——字符串 overlap
    已足够抓 production 里 80% 的重复（模型最常见的复读模式是把上段最后两句
    paraphrase 一遍），剩余的 paraphrase 留给后续 PR。
    """
    if not new_piece or not existing:
        return False, ""
    if new_piece in existing:
        return True, "literal"
    head = new_piece[:_OVERLAP_WINDOW]
    tail = existing[-_OVERLAP_TAIL_WINDOW:]
    # 在 tail 中找与 head 的最长公共后缀/前缀：从 head 完整长度开始递减，
    # 第一个 tail 以 head[:k] 结尾的 k 即为最大重叠。
    max_overlap = 0
    for k in range(min(len(head), len(tail)), _OVERLAP_THRESHOLD, -1):
        if tail.endswith(head[:k]):
            max_overlap = k
            break
    if max_overlap > _OVERLAP_THRESHOLD:
        return True, f"head/tail overlap {max_overlap}字"
    return False, ""


def _section_summary(section: ThesisSection, max_chars: int = 80) -> str:
    """段摘要 = body 前 ``max_chars`` 字符（合并空白后）。

    PR 3 跨段一致性 guard 用：每段完成后取摘要 push 进 ``completed_summaries``，
    下一段 prompt 注入此摘要让模型知道前段大意而不读全文。

    刻意 heuristic 而非 LLM 摘要：摘要 × N 段会再多 N 次 LLM 调用，违背
    本 PR "降低成本"的初衷；前 80 字作"话头"对连贯性已足够提示。
    独立函数便于测试时 mock 与断言。
    """
    return " ".join(section.body.split())[:max_chars]


def _section_tail_anchor(section: ThesisSection, max_chars: int = 200) -> str:
    """段尾锚点 = body 末尾 ``max_chars`` 字符（合并空白后）。

    与 ``_section_summary`` 职能正交：
      - summary（head 80）= "这段讲了什么"——服务跨段去重
      - tail_anchor（tail 200）= "上段说到哪了"——服务叙事承接

    下一段 prompt 仅注入**最紧邻上一段**的 tail，用于"从这里继续写"的语义锚定。
    刻意 heuristic 而非 LLM 摘要——理由同 ``_section_summary``（成本/复杂度）。
    """
    return " ".join(section.body.split())[-max_chars:]


def _expand_section(
    llm: BaseChatModel,
    user_context: str,
    spec: SectionSpec,
    *,
    index: int,
    total: int,
    min_chars: int,
    max_continuations: int,
    completed_summaries: list[tuple[str, str, str, str]] | None = None,
    on_chunk: Callable[[dict, int, bool], None] | None = None,
) -> ThesisSection:
    """单段独立扩写（PR 3 §B.1）：prompt 只含 user_context + 本段 spec + 已完成段
    摘要（**不是全文**）。section 内部仍可续写，但回灌上限 = 本段已生成 body——
    O(本段长度)，不是 O(累计 thesis)。

    跨段一致性 guard：
      ``completed_summaries`` 是 ``[(section_id, title, summary, tail_anchor)]`` 列表，
      由调用方在前一段完成后 push 进来。
        - summary = ``body[:80]``（头部话头）→ 注入"已完成段落摘要"块，服务**跨段防重**
        - tail_anchor = ``body[-200:]``（末尾收束）→ 仅注入"最紧邻上一段末尾"块，
          服务**叙事承接**（让下一段知道从哪里接着写，不再从无 anchor 状态起笔）

      summary 与 tail_anchor 职能正交、并存。每段 prompt 增量 ≈ 80×(N-1) + 200
      （只注入最近一段 tail），相对 user_base 可忽略，保持 O(N) 成本。

    续写重复防护：
      每轮 chunk 合并前走 ``_piece_is_duplicate`` 两层检查（字面 + head/tail
      overlap）。命中即 drop + warn，**不推进 chunk_index**——避免重复内容
      吃掉 MAX_CONTINUATIONS 配额。``continuation`` 自评仍更新以便下一轮可能 break。

    复用 ``_invoke_with_continuation``？——**否**。后者的 immutable_pins +
    field_policy 分发框架是为"一个 JSON object 多字段合并"设计的；section 的
    "单 body append" 用它反而绕，且它的 cont_user 模板包含字段锁定提示与 section
    语义不匹配。两者共享的只有循环骨架（约 50 LOC），重复可接受；等第三个调用方
    出现再抽 ``_run_continuation_loop``。
    """
    summary_block = ""
    tail_anchor_block = ""
    if completed_summaries:
        summary_block = (
            "\n\n=== 已完成段落摘要（用于保持跨段一致性，不要重复以下内容）===\n"
            + "\n".join(
                f"- {sid}（{stitle}）: {summary}"
                for sid, stitle, summary, _tail in completed_summaries
            )
        )
        # 仅注入"最紧邻上一段"的 tail —— 叙事承接只发生在邻段，注入更多 anchor 收益不增
        last_id, last_title, _last_summary, last_tail = completed_summaries[-1]
        tail_anchor_block = (
            f"\n\n=== 上一段（{last_id} {last_title}）末尾（用于承接，不要重复）===\n"
            f"{last_tail}"
        )
    per_section_system = SECTION_EXPAND_PROMPT.format(
        index=index,
        total=total,
        title=spec.title,
        section_id=spec.id,
        min_chars=min_chars,
    )
    user = user_context + summary_block + tail_anchor_block

    # RW-3 (D15)：reconciliation 段注入段专属内容引导（基线 §B.16.5"必须显式论述"）。
    recon_guidance = _RECONCILIATION_SECTION_GUIDANCE.get(spec.title)
    if recon_guidance:
        user += f"\n\n=== 本段专属要求（Synthesis Reconciliation）===\n{recon_guidance}"

    # 可观测：per-call prompt 字符数 log —— 后续可 grep 量化"prompt 长度 vs 输出质量"
    log.info(
        "section_prompt_chars id=%s phase=init system=%d user=%d total=%d",
        spec.id, len(per_section_system), len(user),
        len(per_section_system) + len(user),
    )

    data = _invoke_json(llm, per_section_system, user)
    data.setdefault("chunk_index", 0)
    data["section_id"] = spec.id  # 强制校准：LLM 若输出错 id 也以后端为准
    data["body"] = str(data.get("body", "") or "")

    # 跨段抄袭观测（PR-Next-4）：若新段开头与上一段 tail 有显著 overlap，
    # 说明 LLM 把 tail_anchor 复制进本段 body。`_piece_is_duplicate` 只守段内，
    # 跨段是盲区；这里补一条观测 log 不拦不改行为，frequency 高时再动检测逻辑。
    if completed_summaries and data["body"]:
        _, _, _, last_tail = completed_summaries[-1]
        is_copy, reason = _piece_is_duplicate(data["body"], last_tail)
        if is_copy:
            log.warning(
                "cross_section_copy_suspected id=%s reason=%s；"
                "LLM 可能把上段末尾复制到本段开头。当前不拦，仅观测——"
                "若频繁出现可升级 _piece_is_duplicate 覆盖跨段",
                spec.id, reason,
            )

    if on_chunk:
        on_chunk(data, 0, True)

    for i in range(1, max_continuations + 1):
        length_ok = len(data["body"]) >= min_chars
        model_done = not bool(data.get("continuation", False))
        if length_ok and model_done:
            break
        cont_user = (
            f"本段已写 body（仅本段）：\n{data['body']}\n\n"
            f"当前 body 字符数 {len(data['body'])}, 目标 ≥ {min_chars}。"
            f"请只续写本段新内容（严禁重复既有文字或换种说法复述）。输出同一 JSON schema。"
        )
        log.info(
            "section_prompt_chars id=%s phase=cont round=%d system=%d user=%d total=%d",
            spec.id, i, len(per_section_system), len(cont_user),
            len(per_section_system) + len(cont_user),
        )
        chunk = _invoke_json_with_retry(
            llm, per_section_system, cont_user,
            role_tag=f"section:{spec.id}", chunk_idx=i,
        )
        if chunk is None:
            data["truncated_at_chunk"] = i
            break

        new_piece = str(chunk.get("body", "") or "").strip()
        is_dup, reason = _piece_is_duplicate(new_piece, data["body"])
        if is_dup:
            log.warning(
                "section %s chunk#%d 重复检测命中（%s）；drop 不推进 chunk_index",
                spec.id, i, reason,
            )
            # 仍读模型自评以便下一轮可能 break；**不推进 chunk_index**
            data["continuation"] = bool(chunk.get("continuation", False))
            continue

        if new_piece:
            data["body"] = f"{data['body']}\n\n{new_piece}".strip()
        data["continuation"] = bool(chunk.get("continuation", False))
        data["chunk_index"] = i
        if on_chunk:
            on_chunk(chunk, i, False)

    # 出口统一清零（持久化合约）：与 _invoke_with_continuation 一致的协议
    data["continuation"] = False
    body = data["body"]
    if not body:
        # 空 body = 上游真实 bug（LLM 在所有 chunk 里都没产出内容）。降级成 " " 让
        # Pydantic 满意但污染 UI 又把信号藏起来——直接 raise 由调用方走 error event。
        log.error(
            "section %s expanded to empty body after %d chunks; raising",
            spec.id, data["chunk_index"],
        )
        raise ValueError(f"section {spec.id} body is empty")
    return ThesisSection(
        id=spec.id,
        title=spec.title,
        body=body,
        chunk_index=data["chunk_index"],
        continuation=False,
        truncated_at_chunk=data.get("truncated_at_chunk"),
    )


# Outline fallback：N=1 等价 monolithic 但**代码路径唯一**——不维护双路径。
# 任何 outline 失败（parse / shape / length / validation）都退化到此单段，
# section 流程仍正常跑（emit start/chunk/done），用户体验不退化。
_FALLBACK_OUTLINE = DecisionOutline(
    thesis_outline=[SectionSpec(id="sec_1", title="整体投资逻辑")]
)


# PR-8c P4.B.6 — Synthesis Reconciliation 触发判定（_build_outline 注入）。
# 复用 SectionSpec 现有机制，零 schema 体积。reconciliation section 是"合成优先"，
# 注入到 outline 最前（synthesis 应先于分项论述），并把总段数 cap 在 DecisionOutline
# 上限（5）内——若 LLM 已给满 5 段，reconciliation 顶掉末尾的常规段。
_RECON_BULLISH = frozenset({"Overweight", "Strong Overweight"})
_RECON_STRONG = frozenset({"Strong Overweight", "Strong Underweight"})
_OUTLINE_MAX = 5  # 与 DecisionOutline.thesis_outline 上限一致

# Synthesis Reconciliation section 标题（单一来源，cold-review #2 DRY 修：原本在
# reconciliation_titles() 与 _RECONCILIATION_SECTION_GUIDANCE 两处各写字面，改一处忘改另一处
# 会让 D15 段内容引导静默失效——故抽常量，两处共用）。
_FXT_TITLE = "F×T Reconciliation"
_FXS_TITLE = "F×S Priced-In Check"

# PR-8c RW-3 (D15)：reconciliation 段的内容引导。基线 §B.16.5 要求 fund_mgr 在该段
# **必须显式论述**特定问题；v1（Goal 3）只注入了标题，段被通用展开 = 半成品。此处按
# 标题给 _expand_section 注入段专属要求（定性，不写执行价位——与 hard_block 后切除一致）。
_RECONCILIATION_SECTION_GUIDANCE: dict[str, str] = {
    _FXT_TITLE: (
        "本段是 F×T Reconciliation：必须显式论述 fundamentals（强）与 technical（背离/未确认）"
        "的冲突如何取舍——等待入场 / 降低仓位 / 是否忽略技术信号，给出可执行的逻辑。"
        "**定性表述，不写具体入场/止损价位**（执行数字只属 execution_plan）。"
    ),
    _FXS_TITLE: (
        "本段是 F×S Priced-In Check：必须显式论述 fundamentals 的看多是否已被价格 + 仓位"
        "（crowding / narrative 见顶）提前消化——即'好消息是否已 priced in'，并给出据此的仓位含义。"
        "**定性表述，不写具体价位**。"
    ),
}


def _conviction_direction(conviction: str | None) -> str:
    """bullish / bearish / none —— 用于 F×T 方向背离判定。"""
    if conviction in ("Overweight", "Strong Overweight"):
        return "bullish"
    if conviction in ("Underweight", "Strong Underweight"):
        return "bearish"
    return "none"


def reconciliation_titles(reports: list[AnalysisReport]) -> list[str]:
    """返回需注入的 Synthesis Reconciliation section 标题（0-2 条）。

    F×S Priced-In Check（字段精确）：fundamentals ∈ {Overweight, Strong Overweight}
      AND sentiment crowding_score ≥ 8 AND narrative_phase == "peaking"。

    F×T Reconciliation（**proxy**，pr-8c §2.2 原写 "technical 失效位接近"——该信号无
      对应 schema 字段，dead-link B.16.5 失效）：退化为 **conviction 方向背离** 近似——
      fundamentals ∈ Strong* AND technical 方向与 fundamentals 不一致（对立或未确认）。
      语义偏移：原意是"技术失效位临近"，proxy 是"基本面强但技术面不确认"。低成本可调，
      待真信号落地后升级（见 backlog W）。
    """
    by_role = {r.role: r for r in reports}
    titles: list[str] = []

    fund = by_role.get("fundamentals")
    tech = by_role.get("technical")
    senti = by_role.get("sentiment")

    # F×T Reconciliation（proxy: conviction 方向背离）
    if fund is not None and tech is not None and fund.conviction in _RECON_STRONG:
        fdir = _conviction_direction(fund.conviction)
        tdir = _conviction_direction(tech.conviction)
        if fdir != tdir:  # 技术面不确认（对立或中性/数据不足）
            titles.append(_FXT_TITLE)

    # F×S Priced-In Check（字段精确）
    if fund is not None and senti is not None and fund.conviction in _RECON_BULLISH:
        crowding = senti.crowding_score
        if crowding is not None and crowding >= 8 and senti.narrative_phase == "peaking":
            titles.append(_FXS_TITLE)

    return titles


# ---------------------------------------------------------------------------
# fund_mgr 重构：八步新函数（步骤 2a–7 + 装配工具）
# 设计真值源：plan wondrous-snacking-liskov.md
# 核心不变量：成员资格(valid_fact_ids) ⊥ 可信度(confidence, code 派生)
# ---------------------------------------------------------------------------

_CONFIDENCE_TO_CREDIBILITY: dict[str, str] = {
    # 活跃档（5 档漏斗）→ CredibilityTier 显示档
    "verified": "verified",
    "sourced": "web-single",          # 有源单域名，未达 verified 门
    "sourced_outdated": "web-single",  # 有源但过期
    "controversial": "unverified",     # 多源打架无定论
    "unavailable": "unverified",       # 无源 / 查不到
    # 遗留档（archive replay 兼容；新代码不再写入）
    "stale": "web-single",
    "model_prior": "unverified",
}

# 过期 confidence 档：单一真值源 = schemas/common.py（另一消费方 = facts.exec_floor check③）。
# 装配期据此给 ReferenceEntry.is_outdated 打标——这些档经 _CONFIDENCE_TO_CREDIBILITY 塌进
# "web-single"（与新鲜 sourced 同档），展示语义中立不变。
# ⚠️ 消费方史：旧 AD.7/C 安全地板曾读 is_outdated（层② 相位2·2026-07-07 已改·gate 不再读表③=
# 表③退纯展示）；is_outdated 现仅供**表③展示打标**，不再喂安全闸。过期硬拦现由 fund_mgr 步骤 5'
# 抹 level 承担（+ EXEC-FLOOR check③ 冗余兜底·见 facts/exec_floor.py）。
from committee.schemas.common import OUTDATED_CONFIDENCES as _OUTDATED_CONFIDENCES

_PROSE_SCAN_FIELDS = [
    "thesis_sections[].body",
    "core_risks[].risk",
    "core_risks[].mitigation",
    "trigger_events[]",
    "dissenting_views[]",
    "position_size",
    "override_justification",
    "execution_plan.entry.note",
    "execution_plan.stop_loss.note",
    "execution_plan.take_profit[].note",
    "execution_plan.reevaluate_triggers[].description",
]

_VER_REF_PATTERN = re.compile(r"\{ref:(v\d+|f\d+)\}")


def _build_verify_checklist(
    pass0_result: Any,
    today: "date",
) -> list[dict]:
    """步骤 2a — 纯 code 构建 high-criticality 查证清单。

    两个杠杆零 LLM 成本：
    - 一致性交叉验证（杠杆2）：consensus_level != consensus/single 的 fact → conflict
    - as_of 超期（杠杆3）：按 data_kind 新鲜度窗口判 stale
    """
    from committee.as_of import staleness_days
    from committee.facts.confidence import FRESHNESS_WINDOW_DAYS

    if not pass0_result or not pass0_result.facts_inventory:
        return []

    checklist: list[dict] = []
    for item in pass0_result.facts_inventory:
        is_conflict = item.consensus_level in ("minority", "majority")
        days = staleness_days(item.as_of, today=today)
        dk = _guess_data_kind(item.claim)
        window = FRESHNESS_WINDOW_DAYS.get(dk, FRESHNESS_WINDOW_DAYS["other"])
        is_stale = days is not None and days > window

        if is_conflict or is_stale:
            checklist.append({
                "item": item.claim,
                "criticality": "high",
                "data_kind": dk,
                "conflict": is_conflict,
            })
    return checklist


def _guess_data_kind(claim: str) -> str:
    """启发式 data_kind 推断（纯 code，降级 other）。"""
    cl = claim.lower()
    if any(k in cl for k in ("股价", "收盘", "current price", "stock price", "报价")):
        return "current_price"
    if any(k in cl for k in ("pe", "pb", "估值", "valuation", "市盈", "市净")):
        return "valuation"
    if any(k in cl for k in ("目标价", "target price", "目标位")):
        return "target_price"
    if any(k in cl for k in ("营收", "净利", "eps", "revenue", "profit", "财报", "利润")):
        return "financial"
    return "other"


def _merge_checklists(code: list[dict], opus: list[dict]) -> list[dict]:
    """合并 code 预构建 + opus 增补的查证清单，按 item 文本去重。"""
    seen: set[str] = set()
    merged: list[dict] = []
    for c in code:
        key = c.get("item", "").strip()
        if key and key not in seen:
            seen.add(key)
            merged.append(c)
    for c in opus:
        key = c.get("item", "").strip()
        if key and key not in seen:
            seen.add(key)
            merged.append(c)
    return merged


async def _run_verification(
    ds_llm: BaseChatModel,
    checklist: list[dict],
    query: str,
) -> tuple[list[VerificationFinding], list[dict], list[dict]]:
    """步骤 3 — DeepSeek 联网查证 high-criticality 项。

    Returns: (findings, tool_outputs, notices)。tool_outputs 保留供步骤 3' code 侧域名印证
    （R-5：不再 `data, _` 丢弃实际检索结果）。失败 → ([], [], [一条降级记录])
    （fallback：价位全走定性 —— **判定不变**）。

    第三项 ``notices`` 是 BK.2 提前批 #36（2026-09-15）加的：查证失败时交出的空清单，
    **读起来就是「查过了、没发现问题」** —— 与「压根没查成」在产物上分不开。
    调用方把它并进 ``enforcement_log``，[降级汇总](../degradation.py) 据此派生。
    ⚠️ 只加留痕：失败仍返回空 findings、仍不阻断（用户 2026-09-15 裁）。
    ⚠️ 「清单里没有 high 项」返回的空是**正常**、不是降级，故不发记录。
    """
    from committee.tools import ALL_TOOLS, run_tool_agent

    high_items = [c for c in checklist if c.get("criticality") == "high"]
    if not high_items:
        return [], [], []      # 没有要查的 → 空是正常结果，不是降级

    checklist_text = "\n".join(
        f"- [{c.get('data_kind', 'other')}] {c['item']}"
        + (" ⚠️冲突项" if c.get("conflict") else "")
        for c in high_items
    )
    user_msg = (
        f"查证主题：{query}\n\n"
        f"查证清单（仅 high-criticality）：\n{checklist_text}\n\n"
        f"请逐项联网核实。"
    )

    try:
        data, tool_outputs = await run_tool_agent(
            ds_llm,
            VERIFICATION_PROMPT,
            user_msg,
            ALL_TOOLS,
            max_iterations=3,
            web_search_budget=len(high_items) * 2,
            role_tag="fund_mgr_verify",
            return_tool_outputs=True,
        )
    except Exception as e:
        log.warning("fund_mgr: verification failed: %s; fallback 空 findings", e)
        return [], [], [{
            "rule": "fund-mgr-verification",
            "action": "skipped_failed",
            "detail": f"决策前事实核验失败·本次交出的是空清单（不是「没发现问题」）: {e}",
        }]

    raw_findings = data.get("findings", [])
    findings: list[VerificationFinding] = []
    # BK.2 M3.1（2026-09-18）：解析不出的 finding 被丢时留痕。两支（非 dict / 校验不过）攒在一起、
    # **一次核验只发一条**；丢弃行为与返回值一字不改。detail 只带 id + 报错字段 + 事项短前缀，
    # 让将来能按数据形态立项（坑表：LLM 宽松字段撞严格校验 → except 静默丢整条，本批不 sanitize）。
    dropped: list[str] = []
    for i, rf in enumerate(raw_findings):
        if not isinstance(rf, dict):
            dropped.append(f"#{i+1}: non_dict={type(rf).__name__}")
            continue
        rf.setdefault("id", f"v{i+1}")
        rf.setdefault("item", "")
        rf.setdefault("finding", "")
        rf.setdefault("confidence", "unavailable")  # 占位，步骤 3' 覆写（Q4：不再写 model_prior）
        try:
            findings.append(VerificationFinding.model_validate(rf))
        except Exception as e:
            log.warning("fund_mgr: skip invalid finding %s: %s", rf.get("id"), e)
            fields = sorted({str(err["loc"][0]) for err in e.errors() if err.get("loc")}) \
                if isinstance(e, pydantic.ValidationError) else [type(e).__name__]
            dropped.append(f"{rf.get('id')}: fields={fields}; item={_clip_dropped_item(rf.get('item'))}")
    if dropped:
        note_degradation(
            "verification_finding_dropped",
            f"dropped={len(dropped)}/{len(raw_findings)}; "
            f"samples={json.dumps(dropped[:_DROPPED_MAX_ITEMS], ensure_ascii=False)}",
        )
    return findings, tool_outputs, []


def _norm_url(u: str | None) -> str:
    """URL 归一（strip + 去尾斜杠）。

    T2（信源册建册·M1·换读）上提为模块级：G1 换读锚比对时**两边都过同一个 _norm_url**
    （载点②）——册存 raw url、finding.source 也 raw，若两边归一不一致，尾斜杠差一字符就会
    锚集变→计数变→判定翻。原为 ``_anchor_tool_outputs_by_source`` 内嵌 ``_norm``，上提后
    单一归一源、防"两处 _norm 各自演化漂移"。None → ""（保持内嵌版 ``(u or "")`` 语义）。
    """
    return (u or "").strip().rstrip("/")


def _anchor_tool_outputs_by_source(
    source: str | None,
    tool_outputs: list[dict] | None,
) -> list[dict]:
    """R5-02 小修（路线 B #6 · Option C）— 把 finding 的印证池从全量 verify ``tool_outputs``
    收紧到"产生该 finding ``source`` 的那次搜索结果集"，堵跨 finding 巧合凑 verified
    （[DEFECT-R5-02](../../../docs/governance/backlog.md) 支柱1：池未 scope）。

    返回 ``tool_outputs`` 中 results 含 ``source`` URL 的 web_search 子集（精确 URL 成员，
    多命中取并集；尾部 ``/`` 与空白归一）。``source`` 为空 / 未命中任何 tool_output → ``[]``
    → 该 finding 印证数 0 → 不达 verified（保守、安全方向，绝不误升）。

    纯字符串/集合运算，零 LLM / 零网络（与 verify.py judge-by-code 红线同源）。
    实测锚定率 100%（run-D seg9 10/10 带 source finding）——agent 的 source 本就从它搜到
    的结果里挑，故 source∈搜索结果近乎结构性恒真；未命中 = 伪造源/改写 URL，落不 verified。
    """
    if not source or not source.strip():
        return []

    src = _norm_url(source)  # T2：内嵌 _norm 上提为模块级 _norm_url（G1 换读复用同一归一）
    anchored: list[dict] = []
    for out in tool_outputs or []:
        if not isinstance(out, dict) or out.get("tool") != "web_search":
            continue
        try:
            data = json.loads(out.get("result", "") or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(data, dict) or "error" in data:
            continue
        if any(_norm_url((r or {}).get("url", "")) == src for r in (data.get("results") or [])):
            anchored.append(out)
    return anchored


def _derive_all_confidence(
    findings: list[VerificationFinding],
    pass0_result: Any,
    today: "date",
    tool_outputs: list[dict] | None = None,
    web_provenance: list[dict] | None = None,
    external_websearch_ledger: list[dict] | None = None,
    references: list | None = None,
) -> tuple[list[VerificationFinding], dict[str, FindingConfidence]]:
    """步骤 3' — confidence 终裁。

    ``references``（CRED.2.G3·BP）：表① ``common_context.references``。给了才看 audit_passed
    事实**所引出处**的日期（过期 → ``sourced_outdated``）；不给（旧单测 / 无表①）= 不看，
    与改动前逐字节相同。生产唯一调用点（fund_mgr 步骤 3'）**必须传**。

    R-5：web finding 的 verified 需 ≥VERIFIED_MIN_DOMAINS 个不同域名摘要含一致数字
    （code 侧印证，由 tool_outputs 计），单一伪造 source URL 不足以标 verified。
    **R5-02 小修（Option C）**：每条 finding 的印证池先经 _anchor_tool_outputs_by_source
    收紧到"产生它 source 的那次搜索结果集"，不在全量 tool_outputs 大杂池数（堵跨 finding 巧合凑）。

    AO：DS-0 fact 走 audit_passed 分流——非 audit_passed 事实用 web_provenance（8 个
    analyst 的 web_search outputs）数域名印证 numeric_value。两源各喂各群：findings 用
    fund_mgr 自查的 tool_outputs；DS-0 fact 用 analyst 的 web_provenance（同一台机器
    count_corroborating_domains）。audit_passed 事实不受影响（confidence_for_ds_fact
    走老路、忽略 web_corroboration）。

    Returns:
        (覆写后的 findings, DS-0 fact confidence_map {fact_id: confidence})
    """
    from committee.facts.confidence import confidence_for_finding, confidence_for_ds_fact
    from committee.facts.verify import (
        build_external_websearch_ledger,
        count_corroborating_domains_from_ledger,
    )

    # T2（信源册建册·M1·换读）：两处 confidence 读路改读 T1 固化的 external_websearch 外源册。
    # 正常 fresh/resume 路 fund_mgr 节点透传步骤 3″ 固化的册；老 archive（T1 前）无此册 /
    # 任何未透传的调用（含既有单测传 tool_outputs/web_provenance 的那批）→ replay-fallback：
    # 现场用**同一 builder** 重建 = 节点会建的那本册（换存取不换判定·读固化册 vs 现建册结果全同）。
    if external_websearch_ledger is None:
        external_websearch_ledger = build_external_websearch_ledger(web_provenance, tool_outputs)

    for f in findings:
        # A1.4 + T2（信源册建册·M1·换读）：finding 印证数改从 T1 固化的 external_websearch 外源册
        # 锚读（旧路 = _anchor_tool_outputs_by_source(f.source) → derive → count；今合并册在手，
        # 须在册里把 fund_mgr 半那截锚回来）。
        # 🔴 三载点·一个不能错（换读命门·实现重点盯防·别信"看着对"）：
        #   ① origin=="fund_mgr" 预滤（load-bearing）：旧 G1 锚只在 fund_mgr verify 上做、看不到
        #      analyst；合并册若不先滤 fund_mgr 半，某 analyst 搜索恰含 f.source URL（或仅 group
        #      索引与 fund_mgr 命中 group 撞号）就漏进 G1 计数 → 翻。硬化后按显式来源章 origin 滤
        #      （旧口径 = role is None·见 build_external_websearch_ledger origin 章）。
        #   ② _norm_url 归一：旧 _anchor 用 _norm(strip+去尾/) 比对、册存 raw url；两边都过同一
        #      _norm_url，否则尾斜杠差一字符 → 锚集变 → 计数变。
        #   ③ group=搜索级锚：_anchor 语义 = 整条搜索命中就纳入该搜索【全部】结果；按命中 group
        #      取该 group 全部条目（非只取命中那一条）。
        # 等价性：A1.1 焊死 count_from_ledger==经典；_anchored=derive(命中的那些搜索)，故
        # count_from_ledger(_anchored)==经典 count(anchor)。★焊的是【计数】相等、非列表逐字节
        # （合并册 fund_mgr 半 group/ref_id 有偏移，count 不看这俩）。忠实复刻单 URL 锚（含已知
        # 锚漏·不修：修锚漏=改判定→非 verdict-neutral·已 defer #4/阶段B）。
        _fm = [e for e in external_websearch_ledger if e.get("origin") == "fund_mgr"]        # 载点①
        _hit_groups = {e["group"] for e in _fm if _norm_url(e["url"]) == _norm_url(f.source)}  # 载点②
        _anchored = [e for e in _fm if e["group"] in _hit_groups]                            # 载点③
        corroboration = count_corroborating_domains_from_ledger(f.numeric_value, _anchored)
        f.confidence = confidence_for_finding(
            source=f.source,
            as_of=f.as_of,
            data_kind=f.data_kind,
            today=today,
            conflict=f.conflict,
            corroboration_count=corroboration,
        )

    confidence_map: dict[str, FindingConfidence] = {}
    # CRED.2.G3（BP）：所引出处的时效 —— 判据在 audit_node（`cited_stale_refs`·单一真值源）。
    from committee.agents.audit_node import cited_stale_refs
    _ref_lookup = {r.ref_id: r for r in (references or [])}
    if pass0_result and pass0_result.facts_inventory:
        # A1.3 + T2（信源册建册·M1·换读）：DS-0 印证池从 raw web_provenance → 改读 T1 固化的
        # external_websearch 外源册。scope = **先按显式来源章 origin 排除 fund_mgr 半（与 G1 载点①
        # 对称·靠设计不靠巧合）**，再按 role∈cited_by_roles 筛 analyst 半。
        # 🔴 冷审硬化（2026-07-01）：旧写法只 `role in cited`、靠"fund_mgr 半碰巧 role=None ∉ cited"
        #   排除 = 捡漏捡来的对；将来谁给 verify 输出补 role 键、且撞上某 fact 的 cited_by_roles，就
        #   悄无声息漏进 → 凑 verified（不安全方向）。改成 `origin=="analyst"` 显式排除 = 谁改都改不坏。
        #   verdict-neutral：当前不变量下 fund_mgr 半 role=None，新旧筛选中集**完全相同** → 逐字节同。
        # 逐字节同：count_...from_ledger 只读 domain/numbers；册里 analyst 半 (domain,numbers,role) 与
        # derive(web_provenance) 内容全同（仅 ref_id 偏移、count 不看）。★confidence_for_ds_fact 调用、
        # 封顶/fresh 逻辑一字未动（封顶在 confidence.py·零碰）。
        for item in pass0_result.facts_inventory:
            dk = _guess_data_kind(item.claim)
            # AO: 非 audit_passed 事实的 numeric_value 在 ≥1 web 域名印证 → web 支；
            # audit_passed 走老路忽略此值（golden 锁）。None numeric_value → 计 0。
            # R5-02 小修(Goal 2)：按 role∈cited_by_roles 收池，只数"引用过该 fact 的 analyst
            # 自己查的来源"，堵 8 分析师全量大杂池跨 fact 巧合凑。空/缺 cited_by_roles → 空池
            # → web_corr=0 → 维持 unavailable（用户拍定 (a) 保守降级：洞堵彻底、安全方向、
            # 绝不退回全池；显式兜底非静默——见 test_r5_02 空 cited 用例）。
            # A1.3：scope 语义不变（role∈cited_by_roles），从册 entry 筛（册 entry.role = 来源
            # tool_output 的 role，等价于旧"按 role 筛 web_provenance"）。冷审补：显式 origin 排除
            # fund_mgr 半在前（与 G1 载点① 对称），role 筛 analyst 半在后。
            _cited = set(item.cited_by_roles or [])
            _scoped_ledger = [
                e for e in external_websearch_ledger
                if e.get("origin") == "analyst" and e.get("role") in _cited
            ]
            web_corr = count_corroborating_domains_from_ledger(item.numeric_value, _scoped_ledger)
            confidence_map[item.fact_id] = confidence_for_ds_fact(
                audit_status=item.audit_status,
                as_of=item.as_of,
                data_kind=dk,
                today=today,
                conflict=item.consensus_level in ("minority", "majority"),
                web_corroboration=web_corr,
                source_outdated=bool(
                    _ref_lookup and item.audit_status == "audit_passed"
                    and cited_stale_refs(item, _ref_lookup, today)
                ),
            )

    for f in findings:
        confidence_map[f.id] = f.confidence

    return findings, confidence_map


def _format_findings_for_prompt(findings: list[VerificationFinding]) -> str:
    """格式化 verification findings 注入 opus prompt。

    ★ DEFECT-PROSE-GATE-NARRATIVE-UNDERREDACT 修复（fix 2，源头传导）：
    `confidence != "verified"` 的 finding（含 not_found→unavailable、model_prior、
    stale/sourced_outdated、controversial 等）前缀 **⚠️未核实**，配合 DECISION_PROMPT
    的「未核实事实标注」规则，要求 opus 把这类**叙事型未核实事实**用进 dissenting_views/
    trigger_events/core_risks/thesis 等行动字段时显式带"（未核实）"标注、不得当确凿事实陈述
    （堵 prose-gate 只拦数字、漏叙事的洞）。
    **镜像安全（验收硬条件）**：`verified` finding **不加**标记——已核实事实不被误标 unavailable。
    """
    if not findings:
        return ""
    lines = []
    for f in findings:
        marker = "⚠️未核实 " if f.confidence != "verified" else ""
        status = f"confidence={f.confidence}"
        src = f"来源: {f.source}" if f.source else "来源: 无"
        lines.append(f"{marker}[{f.id}] {f.item} → {f.finding} ({status}, {src}, as_of={f.as_of})")
    return (
        "\n\n=== 查证结果（助理已联网核实；标 ⚠️未核实 = 查证未坐实，用进决策行动字段须带"
        "（未核实）标注，不得当确凿事实）===\n"
        + "\n".join(lines)
    )


_PRESCRIBED_NUM_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def _decision_prescribed_numbers(decision: "FinalDecision") -> set[float]:
    """决策者在行动字段（position_size / execution_plan 价位·触发·note）自定的数字。

    ★ DEFECT-PROSE-GATE-SELF-ABRADE 修复：这些是 fm 的**处方**（仓位上限、建仓/止损/目标价、
    触发阈值），非外部待核 fact。prose-gate（5' 打码 + expand/review strip）只该约束"外部引用
    的未核实数字"，绝不该拿"外部是否核实"去删决策者自己拍的行动数字（删了=方向+价位+仓位三缺一、
    核心交付物残缺）。本函数收集这些处方数字，供 5' 打码门豁免（不打码决策者自定数字）。

    已知边界（docstring 明示）：按**数值**匹配——若某外部未核实数字恰好等于处方数字会一并放行
    （如外部"20 倍 PE"撞仓位"20%"）；方向 fail-safe（保决策者数字），且行动数字多为独特价位，
    碰撞罕见。更精确的"按字段+位置豁免"留后续（需 scan 侧带 location，本次治标不扩界）。
    """
    nums: set[float] = set()

    def _add_text(text: str | None) -> None:
        for m in _PRESCRIBED_NUM_RE.findall(text or ""):
            try:
                nums.add(float(m.replace(",", "")))
            except ValueError:
                pass

    _add_text(decision.position_size)
    ep = decision.execution_plan
    if ep is not None:
        for pf in (ep.entry, ep.stop_loss, *ep.take_profit):
            if pf is None:
                continue
            for attr in ("low", "high", "level"):
                v = getattr(pf, attr, None)
                if isinstance(v, (int, float)):
                    nums.add(float(v))
            _add_text(getattr(pf, "note", None))
        for rt in ep.reevaluate_triggers:
            v = getattr(rt, "threshold", None)
            if isinstance(v, (int, float)):
                nums.add(float(v))
            _add_text(getattr(rt, "description", None))
    return nums


def _committee_structural_numbers(
    decision: "FinalDecision", risk_gate_findings: list | None = None,
) -> set[float]:
    """委员会**自产的流程/结构数字**——投票分布、决策自己的信心分、闸门质疑条数等。

    ★ MASK.C2（D-3 空跑坐实）：这些数字来自委员会自己的过程（vote_summary / confidence /
    risk_gate finding 计数），**不是外部待核 fact·天生没有 f#/v# 来源可挂**。opus 在散文里
    写"投票 33 vs 14""confidence 封顶 5""24 条交叉质疑"是如实转述过程，不该被验引用门
    当"未引用裸数字"涂（涂了 = "投票 相关数值 vs 相关数值" = 有害误涂）。本函数收集它们，
    与 _decision_prescribed_numbers 合并成豁免集。按**数值**匹配（同处方豁免·fail-safe 边界）。
    """
    nums: set[float] = set()

    def _harvest(obj) -> None:
        if isinstance(obj, bool):
            return
        if isinstance(obj, (int, float)):
            nums.add(float(obj))
        elif isinstance(obj, dict):
            for v in obj.values():
                _harvest(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                _harvest(v)

    # 决策自己的信心分 + 投票分布（含嵌套 weighted）
    if isinstance(getattr(decision, "confidence", None), (int, float)):
        nums.add(float(decision.confidence))
    _harvest(getattr(decision, "vote_summary", None))

    # 闸门 finding 消息里的计数（如 G2 "24 条交叉质疑"）
    for f in (risk_gate_findings or []):
        msg = f.get("message", "") if isinstance(f, dict) else getattr(f, "message", "")
        for m in _PRESCRIBED_NUM_RE.findall(msg or ""):
            try:
                nums.add(float(m.replace(",", "")))
            except ValueError:
                pass
    return nums


# ---------------------------------------------------------------------------
# MASK.C2 — 步骤 5' 验章门（Path B：生成侧带标·门验章不搜章·2026-07-15）
# ---------------------------------------------------------------------------

# 🔴 时真正执行定性替换的字段（= 旧 _replace_in_decision 覆盖面·ESCAPE 修复边界）。
# trigger_events / execution_plan notes 有意不涂（观点/处方场·backlog ESCAPE 条 scope）；
# 全部字段都剥机器标（标是内部杂质·任何字段都不给用户看生标）。
_REPLACEABLE_LOC_PREFIXES = (
    "sec_", "core_risks", "position_size", "dissenting_views", "override_justification",
)

# ---- caveat 去重（MASK.GATE-B G3·2026-07-16）--------------------------------
# 系统里有**两套**未核实括注、互不知情：
#   ① 验章门 🟡 档插的 _GATE_CAVEAT——**每个 yellow 标插一次**，同句多个 yellow 标 → 插多次；
#   ② fund_mgr 按 DECISION_PROMPT「未核实事实标注」规则**自写**的 _FM_CAVEAT
#      （提示来自 _render_verify_findings_block 的 ⚠️未核实 前缀）。
# 二者无 dedup → NVDA e2e 实测出现「（未独立核实）（未独立核实）（未核实）」三连。
# 折叠成一个：**保留门的**（code 权威·语义更精确「有源但未独立核实」）。
# RDR-1.G3（2026-09-28·用户裁「模型贴、程序只补漏、措辞统一为一种」）：真值源挪到零依赖的
# committee.caveats（终局质检 Q13 也从那里读集合）。提示词 R7 / 审计闸门现在都让模型写
# 「（未独立核实）」；「（未核实）」「（未完全核实）」降为**历史变体**，产出侧见到就归一。
from committee.caveats import CAVEAT_GATE as _GATE_CAVEAT, CAVEAT_FM as _FM_CAVEAT, CAVEAT_LEGACY as _CAVEAT_LEGACY  # noqa: E402

# ---- 价位门控 (b) 的 run 级 grounding 地板（GATE-ROUTE G2·2026-07-22 用户拍）----
# 整篇分析引用的来源里 verified 个数 ≥ 本阈值 → 判"有据" → 放行全部价位原样显示；
# < 阈值（数据几乎全失败的降级 run）→ 抹全部 level（防凭空拍价位）。
# 🔴 **刻意不复用 `confidence.VERIFIED_MIN_DOMAINS`（=2）**——两者数值巧合但**语义不同**：
#   · VERIFIED_MIN_DOMAINS = 单条 finding 要几个**独立域名**印证才升 verified（证据强度门槛）
#   · 本常量        = 整个 run 要有几条 **verified 事实**才算"有据"（run 级 grounding 地板）
# 合用会导致将来调其一而**两处行为一起漂**。见 C-价位门控-实施清单.md ①。
_GROUNDING_MIN_VERIFIED = 2
_CAVEAT_ALT = rf"(?:{re.escape(_GATE_CAVEAT)}|{re.escape(_FM_CAVEAT)})"
# 历史变体 → 唯一措辞。两种形态：① 完整括注「（未核实）」「（未完全核实）」；
# ② **缺左括号的残缺形**「…）未核实）」「，未核实）」（09-23 实测：折叠切在了不同措辞的边界上）。
_CAVEAT_LEGACY_RE = re.compile(
    "|".join(re.escape(c) for c in sorted(_CAVEAT_LEGACY, key=len, reverse=True))
    + r"|（[尚暂]未(?:完全|独立)?核实）"      # 「（尚未核实）」「（暂未独立核实）」等整括注变体也归一
)
# 残缺形 = 「未…核实）」**前面紧挨着**右括号 / 标的右花括号 / 百分号 / 数字（中间至多一个逗号顿号）。
# ⚠️ 不能只看「前一个字不是左括号」（冷审 F1）：那会把「（尚未核实）」「（该数据未核实）」这种合法整括注
# 从中间劈开成「（尚（未独立核实）」。
_CAVEAT_ORPHAN_RE = re.compile(r"(?<=[）}%％\d])[，,、]?\s*未(?:完全|独立)?核实）")
# 两个括注之间**只隔着标 / 空白**时仍算相邻：🟡 档的 f# 标是**留标**的
# （`1325{ref:f3}（未独立核实）{ref:f4}（未独立核实）`）→ 标夹在两个括注中间。
# 语义站得住：这些标认领的必是**同一个数字**——num_span_before_stamp 会先剥掉尾随的
# 「标(+括注)」再往前找数字，所以 f4 借的就是 f3 那个 1325。
# （MASK.GATE-B-fix finding 4：旧 `\s*` 间隔只折得动 v# 路径——v# 标被 caveat 替换掉、
#  括注自然相邻；而 f# 是**多数**路径，e2e 要治的叠加恰恰折不动。）
_CAVEAT_PAIR_RE = re.compile(
    rf"({_CAVEAT_ALT})((?:\s*\{{ref:[fv]\d+\}})*[\s，,、]*)({_CAVEAT_ALT})"
)
# 「已经有括注了」——门补括注前先看这里（只补漏·不重复贴）：标后面紧跟（只隔空白）任一括注形态。
_CAVEAT_FOLLOWS_RE = re.compile(r"^\s*（?未(?:完全|独立)?核实）")
_STAMP_RE_INLINE = re.compile(r"\{ref:[fv]\d+\}")   # 折叠时保留标用（整枚·含花括号）


def _fold_caveat_pair(m: "re.Match") -> str:
    """折一对括注 → 中间的标**原样留下**（前端 FactRef chip·不是杂质），只收重复括注。
    两者有一个是门的 → 留门的（code 权威·语义更精确「有源但未独立核实」）。
    中间的空白随被折掉的括注一起丢（否则会把空格搬到括注前·改变正文排版）。"""
    keep = _GATE_CAVEAT if _GATE_CAVEAT in (m.group(1), m.group(3)) else _FM_CAVEAT
    return "".join(_STAMP_RE_INLINE.findall(m.group(2))) + keep


def _normalize_caveats(text: str) -> str:
    """历史变体 / 残缺形 → 唯一措辞「（未独立核实）」（RDR-1.G3）。

    先归一再折叠：「{ref:f18}（未独立核实）（未完全核实）」→ 两个同措辞相邻 → 折成一个；
    「12.5%（未独立核实）未核实）」→ 残缺形补成完整括注 → 折成一个。
    残缺形只认「未…核实）」前面**不是**左括号的那种；前面若有逗号（「，未核实）」）一并吃掉，
    否则折叠后会留下一个悬空的逗号。
    """
    if "核实）" not in text:
        return text
    text = _CAVEAT_LEGACY_RE.sub(_GATE_CAVEAT, text)
    return _CAVEAT_ORPHAN_RE.sub(_GATE_CAVEAT, text)


def _dedup_caveats(text: str) -> str:
    """折叠相邻/重复的未核实括注（G3 · RDR-1.G3 起先归一措辞）。

    迭代到稳定——「A A B」需先折 AA 再折 AB，单轮不收敛。上限 4 轮防病态输入死循环。
    **只折叠相邻**——中间只允许空白 / 来源标 / 一个顿号逗号；句中真正相隔的两个括注
    （中间有正文/别的数字）各自标注不同数字，不该合并。
    """
    text = _normalize_caveats(text)
    for _ in range(4):
        prev = text
        text = _CAVEAT_PAIR_RE.sub(_fold_caveat_pair, text)
        if text == prev:
            break
    return text


#: 论点标题的防御性截断上限（与 schema ``SectionSpec.title`` / ``ThesisSection.title`` 的 50 一致；
#: 提示词要求 ≤ 40 字）。RDR-1.G3 从 30 放宽：09-23 黄金跑批三个标题全撞 30 字、截成「…而非'启」。
TITLE_MAX_CHARS = 50
_TITLE_BREAK_CHARS = "，。；：、！？,;:!? —–"   # 不含 ASCII "-"：数字区间 / 英文连字里的连字符不是断句（冷审 F9）


def clip_title(title: str, limit: int = TITLE_MAX_CHARS) -> str:
    """标题超长时**按标点回退**截断，不截在词中间；找不到标点才硬截。"""
    t = title.strip()
    if len(t) <= limit:
        return t
    head = t[:limit]
    cut = max(head.rfind(ch) for ch in _TITLE_BREAK_CHARS)
    if cut >= limit // 2:
        return head[:cut].rstrip(_TITLE_BREAK_CHARS + " ")
    return head


def _iter_prose_fields(decision: FinalDecision):
    """(location, text, setter) 遍历器——覆盖旧步骤5 scan 的全部散文字段。"""
    for sec in decision.thesis_sections:
        yield f"{sec.id}.body", sec.body, (lambda s, _o=sec: setattr(_o, "body", s))
    for i, cr in enumerate(decision.core_risks):
        yield f"core_risks[{i}].risk", cr.risk, (lambda s, _o=cr: setattr(_o, "risk", s))
        yield (f"core_risks[{i}].mitigation", cr.mitigation,
               (lambda s, _o=cr: setattr(_o, "mitigation", s)))
    for i, te in enumerate(decision.trigger_events):
        yield (f"trigger_events[{i}]", te,
               (lambda s, _i=i, _d=decision: _d.trigger_events.__setitem__(_i, s)))
    for i, dv in enumerate(decision.dissenting_views):
        yield (f"dissenting_views[{i}]", dv,
               (lambda s, _i=i, _d=decision: _d.dissenting_views.__setitem__(_i, s)))
    yield ("position_size", decision.position_size,
           (lambda s, _d=decision: setattr(_d, "position_size", s)))
    if decision.override_justification:
        yield ("override_justification", decision.override_justification,
               (lambda s, _d=decision: setattr(_d, "override_justification", s)))
    ep = decision.execution_plan
    if ep:
        for name, pf in (("entry", ep.entry), ("stop_loss", ep.stop_loss)):
            if pf is not None and getattr(pf, "note", None):
                yield (f"execution_plan.{name}.note", pf.note,
                       (lambda s, _o=pf: setattr(_o, "note", s)))
        for i, tp in enumerate(ep.take_profit):
            if getattr(tp, "note", None):
                yield (f"execution_plan.take_profit[{i}].note", tp.note,
                       (lambda s, _o=tp: setattr(_o, "note", s)))
        for i, rt in enumerate(ep.reevaluate_triggers):
            desc = getattr(rt, "description", None)
            if isinstance(desc, str):
                yield (f"execution_plan.reevaluate_triggers[{i}].description", desc,
                       (lambda s, _o=rt: setattr(_o, "description", s)))


def _apply_stamp_gate(
    decision: FinalDecision,
    findings: list[VerificationFinding],
    confidence_map: dict[str, FindingConfidence],
    pass0_result: Any,
    common_context: Any,
    prescribed_numbers: set[float] | frozenset[float] = frozenset(),
) -> tuple[FinalDecision, list[ClaimAudit], list[dict]]:
    """步骤 5'（Path B 验引用门·MASK.C2）— **只核引用、不核数字值** + 价位门控。

    本 session 任务 = fund_mgr 写数字挂来源、门确认引用（有没有、对不对、哪个册子）。
    数字**值**对不对（源值抄错/写错）是上游数据层独立任务（backlog AS）·不在本门。

    opus 生成侧带标（{ref:fX}/{ref:vX}·C1），本门逐标**认标 + 认册**（judge-by-code·零 LLM）：

    - 🟢 留原值：标解析到真源且来自**结构化直拉源**（表① REF#T/Y/F·audit 核过）或
      **v#-verified**（fund_mgr 重查·≥2 域名印证·code 派生非自封）
    - 🟡 留原值 + 「（未独立核实）」：其余有效引用（v# 单域名 / f# 表① REF#R/W 研报文本 /
      f# 外源册 W# / 水印落空）——有出处但未经结构化核验（认册结果·见 stamp_check.classify_stamp）
    - 🔴 剥标 + 涂定性：**幻觉标（f#/v# 不存在）**——假标不许活到读者（不变量·B 不放行）

    ★ **处方豁免不作用于挂标数字**（GATE-ROUTE G1·2026-07-22 用户拍）：挂标 ⟹ 引用外部事实
    ⟹ 一律走上面三档；`prescribed_numbers` 的**唯一消费点 = 无标扫描段**（自产数字从不挂标·
    零反例）。旧的按值 exempt tier 已删——它会把撞上处方数值的挂标研报数误放（f35）。

    ★ **无标裸数字：不涂·只记审计日志**（Option B「信任标记」·2026-07-16 用户拍·
    [设计 pass](../../../docs/plans/MASK-GATE-REDEF-信任标记-设计pass-2026-07-16.md)）。
    门只验 fm 主动挂标的、不猎他没标的：无标数字 = fm 自己的散文（日期/列表序号/区间/
    推理量），旧门默认涂它们 → 豁免集永远补不完（NVDA e2e 实测 21 涂全误伤·0 真阳）。
    现**无标数字一律**记 enforcement_log 供审计监控挂标率（不做"像不像事实"的过滤——
    任何这类过滤器都有 gap，而降级为「记」之后 gap = 静默放行；见下方执行段注释）——
    **ESCAPE 底线由「涂」降级为「记」**（北极星放松·已授权；诚实信号搬到内部审计、
    不再毁可读性）。

    标处置（渲染安全）：f# 标保留（前端 InlineMd 渲染 FactRef chip·可追溯）；
    v# 标验后即剥（前端不认 v#·机器追溯在 claim_audits.matched_finding）。
    涂的执行面 = _REPLACEABLE_LOC_PREFIXES（仅幻觉标走它）；剥标全字段。
    价位门控 = **run 级 grounding 地板 (b)**（GATE-ROUTE G2）：整篇 verified 数
    ≥ `_GROUNDING_MIN_VERIFIED` → 放行全部价位原样；否则抹全部 level。
    「带 level ⟺ verified」不变量**已废**→ EXEC-FLOOR check③ 转正为过期价位主保护。

    Returns: (门控后 decision, claim_audits, enforcement_log entries)
    """
    from committee.facts.confidence import qualitative_word
    from committee.facts.stamp_check import (
        STAMP_RE, classify_stamp, num_span_before_stamp, parse_literal_nums,
    )
    from committee.facts.stamp_families import web_marker_end_at, web_stamp_spans

    findings_by_id = {f.id: f for f in findings}
    facts_by_id = {
        fi.fact_id: fi
        for fi in (getattr(pass0_result, "facts_inventory", None) or [])
    }
    ref_lookup = {
        r.ref_id: r
        for r in (getattr(common_context, "references", None) or [])
    }

    audits: list[ClaimAudit] = []
    enforcement: list[dict] = []
    CAVEAT = _GATE_CAVEAT  # 模块常量·与 _dedup_caveats(G3) 共用同一真值·防漂移

    for location, text, setter in _iter_prose_fields(decision):
        if not text:
            continue
        replaceable = location.startswith(_REPLACEABLE_LOC_PREFIXES)

        # ---- 判定（认标 + 认册·**只核引用不核值**·MASK.C2）----
        stamp_ms = list(STAMP_RE.finditer(text))
        verdicts: list[dict] = []
        for m in stamp_ms:
            rid = m.group(1)
            # ★ 取 span 而非仅字面值：🔴 按 span 涂（find-first 会涂错同名数字·finding 1）
            hit = num_span_before_stamp(text, m.start())
            literal = hit[0] if hit else None
            lit_span = (hit[1], hit[2]) if hit else None
            nums = parse_literal_nums(literal)
            is_v = rid.startswith("v")
            v = {"m": m, "rid": rid, "nums": nums, "literal": literal,
                 "lit_span": lit_span, "is_v": is_v}
            cls = classify_stamp(
                rid, findings_by_id=findings_by_id, facts_by_id=facts_by_id,
                ref_lookup=ref_lookup,
            )
            if cls == "halluc":
                v["tier"] = "halluc"          # 标指向不存在编号 → 剥+涂
            elif not literal:
                v["tier"] = "qualit"          # 标挂定性句（无数字）：剥标不涂
            else:
                v["tier"] = cls               # green（结构化源/v#-verified）/ yellow（其余有效引用）
            # ★ GATE-ROUTE G1（2026-07-22 用户拍）：**挂标数字不再按值豁免**（原 exempt tier 已删）。
            # 旧逻辑在此处插一句 `any(n in prescribed_numbers for n in nums) → exempt`（留值剥标·不盖章），
            # 按**数值**认人 → 挂标的引用事实只要数值撞上处方数字就被当自己人放走：
            # 实测 f35「产能 1500 万」{ref:f35}（研报数·该盖章）撞止盈价 1500 → 章没盖、标被剥。
            # 这正是 `_decision_prescribed_numbers` docstring 自陈的已知边界（「外部 20 倍 PE 撞仓位
            # 20%」）+ 它当年押后的「按字段+位置豁免」的落地：**改按「挂没挂标」认人**。
            # 不变量：自产数字（仓位/价位/触发/投票/信心/质疑计数）**从不挂 {ref} 标**——它们没有
            # 外部来源可引 ⟹ 挂标 ⟹ 引用外部事实 ⟹ **不存在「该豁免」的合法情形**（零反例）。
            # ∴ 豁免唯一消费点收窄到**无标扫描段**（下方 `val in prescribed_numbers` 一处·保留不动）：
            # 该免的（自产数字本就无标）一个不漏，撞号误伤（含投票 14 / 信心 6 等小整数撞挂标事实数
            # 的一整类）根治。设计见 docs/plans/gate-routing-redesign/（轨A 步3 + 📜决策记录 Q2）。
            # conf 仅供 claim_audits 记录（不参与档位判定·门不看值/不看可信度门槛）
            v["conf"] = (findings_by_id[rid].confidence if (is_v and rid in findings_by_id)
                         else confidence_map.get(rid, "unavailable") if not is_v else "unavailable")
            verdicts.append(v)

        # ---- 无标数字（Option B「信任标记」·2026-07-16 用户拍·**不涂·只记**）----
        # ★ 门重定义（[MASK-GATE-REDEF 设计 pass](../../../docs/plans/MASK-GATE-REDEF-信任标记-设计pass-2026-07-16.md)）：
        # 门只验 fund_mgr **主动挂标**的数字、**不猎他没标的**。无标数字 = fm 自己的散文
        # （日期 / 列表序号 / 区间端点 / 推理量），本就无来源可挂——旧门默认涂它们 →
        # 豁免集永远补不完（开放空间）。NVDA e2e 实测：裸数涂 21 个**全是误伤、0 真阳**。
        # 现改为：**原样保留不涂**，把无标数字**全部**记进 enforcement_log 供审计监控
        # fm 挂标率。**ESCAPE 底线由「涂」降级为「记」**（北极星·用户已授权）。
        # 幻觉标（挂了不存在的 ref）仍由上方验标 loop 剥+涂——B 只放行**无标**、不放行**假标**。
        #
        # ★ 为什么「全记」而不是「只记像事实的」：任何「像不像事实」的过滤器都有 gap
        # （实测 _THESIS_NUMBER_RE 只捕获 $¥€£/%‰万亿千KMBT，**漏 元/倍/x** → 「目标价
        # 1325 元」会既不涂也不记 = **静默放行**，踩设计红线「无标疑似事实必须进日志」）。
        # 而补 gap 就是回到豁免/词表 treadmill。∴ 取最笨最稳：**无标数字全记**（零 gap、
        # 零词表），噪音（年份/列表序号）由 G5 的 AI 语义核查分类——AI 读得懂哪些真是
        # 漏标的事实，比任何正则词表都准。三个排除项是语义上本就不该记的，非「防误涂」补丁。
        # 「已由标处置」= 该数字**确实被某枚标绑定**（验标 loop 的 lit_span·门自己的判定），
        # **不是**「离某枚标够近」。旧的 30 字符邻近启发式会把标**没**认领的数字一起吞掉：
        # 实测 "毛利率 75% 对应营收 1325 亿元{ref:f3}" 里标只绑 1325，而 75% 离标 13 字符
        # → 被跳过 → **既不涂也不记 = 静默放行**，正是设计红线「无标疑似事实必须进日志」
        # 禁的事（MASK.GATE-B-fix finding 3·「全记零 gap」当时并未真的零 gap）。
        # ★ 这是 known-pitfalls §3.2「阻断降级为记录时 gap 性质翻转」的**第二次现身**：
        # 邻近窗是**阻断时代**的过滤器（那时 gap = 少涂一个 = 安全方向），照搬到记录时代
        # 就成了漏报。修法 = 不再用任何"疑似"启发式，改用门自己的确定性绑定结果。
        claimed = [v["lit_span"] for v in verdicts if v["lit_span"]]
        wspans = web_stamp_spans(text) + [m.span() for m in stamp_ms]
        unstamped_suspect: list[tuple[Any, float]] = []
        for nm in _THESIS_NUMBER_RE.finditer(text):
            if any(a <= nm.start() < b for a, b in wspans):
                continue                       # W# 章内流水号 / {ref:} 标内编号·非正文数字
            gs, ge = nm.span(1)                # 数字本体（不含币种前缀/单位后缀）
            if any(ls < ge and gs < le for ls, le in claimed):
                continue                       # 真被某枚标认领（区间 "20-24" 两端同属一个 span）
            try:
                val = float(nm.group(1).replace(",", ""))
            except ValueError:
                continue
            if val in prescribed_numbers:
                continue                       # 决策者行动数字 / 委员会流程数字：本就无需来源标·不算漏标
            unstamped_suspect.append((nm, val))

        # ---- 执行 ----
        # ★ 先收集**互不重叠的 span 编辑**、再按位置降序一次性应用（MASK.GATE-B-fix finding 1）。
        # 不能边遍历边改文本：数字 span 落在**它自己的标之前**，而连写标
        # （"1.8M{ref:f98}{ref:f99}"）里 f98 的标又在该数字**之后** → 处置 f99 时涂掉数字，
        # 会让尚未处理的 f98 标 span 当场失效（实测漏 "}" 到正文）。收集成编辑表后，
        # 降序应用即可保证每次改动只影响**已处理过**的区域。
        # 不重叠性：每枚标的数字必落在前一枚标之后（num_span_before_stamp 从 prev stamp end
        # 起找）→ [数字, 标] 区块彼此不交；连写标共享同一数字 span → 去重后只留一条。
        edits: list[tuple[int, int, str]] = []      # (start, end, replacement)
        red_spans: set[tuple[int, int]] = set()     # 已登记涂的数字 span（连写标共享时去重）
        for v in verdicts:
            m = v["m"]; tier = v["tier"]; is_v = v["is_v"]
            s, e = m.span()
            if tier == "green":
                if is_v:
                    edits.append((s, e, ""))                # v# 剥标（前端不认）
                # f# 留标（前端 FactRef chip）
            elif tier == "yellow":
                if is_v:
                    edits.append((s, e, CAVEAT))            # v# 标→括注
                elif _CAVEAT_FOLLOWS_RE.match(text[e:e + 12]):
                    v["caveat_present"] = True  # 模型已经贴了括注（任一措辞）→ 只补漏、不重复贴（RDR-1.G3）；措辞由 _dedup 归一
                else:
                    edits.append((e, e, CAVEAT))            # f# 标后插括注（标保留）
            elif tier == "qualit" and not is_v:
                pass  # f# 定性引用标（观点/叙事引用·无数字）：保留——可追溯性
                      # 是收益非杂质（fm-spec B1 结论层可回溯）·前端渲染 FactRef chip
            else:
                # qualit(v#) / halluc / red → 剥标（G1 后不再有 exempt tier）
                edits.append((s, e, ""))
                if tier in ("halluc", "red") and v["lit_span"] and replaceable:
                    repl = qualitative_word(
                        findings_by_id[v["rid"]].data_kind
                        if (is_v and v["rid"] in findings_by_id) else "other"
                    )
                    ls, le = v["lit_span"]
                    v["replaced"] = True   # 该数字被涂（本枚标涂 or 连写的另一枚已登记）
                    if (ls, le) not in red_spans:
                        red_spans.add((ls, le))
                        # 紧跟的外部数据章一并移除（数字成定性词后出处不该悬空·T11 麻烦一 b）
                        edits.append((ls, web_marker_end_at(text, le), repl))
                        enforcement.append({
                            "rule": "stamp-gate-5'", "action": "qualitative_replace",
                            "detail": f"{location}: '{v['literal']}' → '{repl}' (验章不过)",
                        })

        new_text = text
        # 降序按 **(start, end)**：同一起点上「插括注」是零宽编辑 (e,e)，而紧邻的下一枚标
        # 若要剥则是 (e, e+8) —— 起点相同。必须**先应用宽的那条**（剥标），否则零宽插入
        # 会把后者的坐标顶歪、剥进括注里，漏出残缺生标 "ref:v4}" 给读者
        # （实测 "1325{ref:f3}{ref:v4}"（🟡f# + 🟢v#）→ "1325{ref:f3}ref:v4}"）。
        for st, en, repl in sorted(edits, key=lambda x: (x[0], x[1]), reverse=True):
            new_text = new_text[:st] + repl + new_text[en:]

        # 无标疑似事实数字：**只记审计日志·绝不改 new_text**（Option B·ESCAPE 降级为「记」）
        for nm, val in unstamped_suspect:
            lit = nm.group(0).strip()
            audits.append(ClaimAudit(
                location=location, claim_text=lit, value=nm.group(1),
                numeric_value=val, data_kind="other", matched_finding=None,
                numeric_match=False, confidence="unavailable",
                replaced=False, replacement_text=None,
            ))
            enforcement.append({
                "rule": "stamp-gate-unstamped-log", "action": "log_only",
                "detail": f"{location}: 无标疑似事实数字 '{lit}'（未挂 ref·原样保留·仅记审计）",
            })

        # ClaimAudit（标记录·裸数字已在上面记）
        for v in verdicts:
            rid = v["rid"]; tier = v["tier"]
            # 由执行段回填（而非在此按 tier/replaceable 重算一遍判据）：单一真值源，
            # 改涂的条件时不会漏改这里。**当前语义与旧的预判式等价**（连写标共享数字时
            # 两枚都记 replaced=True——数字确被涂），非行为修复，是防漂移。
            replaced = bool(v.get("replaced"))
            audits.append(ClaimAudit(
                location=location,
                claim_text=(v["literal"] or "") if v["nums"] else "(定性标)",
                value=v["literal"] or "",
                numeric_value=(v["nums"][0] if v["nums"] else None),
                data_kind=(findings_by_id[rid].data_kind
                           if (v["is_v"] and rid in findings_by_id) else "other"),
                matched_finding=rid if tier not in ("halluc",) else None,
                numeric_match=tier in ("green", "yellow"),
                confidence=v["conf"],
                replaced=replaced,
                replacement_text=None,
            ))
            if tier == "halluc":
                log.warning("fund_mgr: stamp-gate stripped hallucinated ref %s at %s", rid, location)
                enforcement.append({
                    "rule": "stamp-gate-5'", "action": "strip_hallucinated_stamp",
                    "detail": f"{location}: 幻觉标 {{ref:{rid}}} 已剥" + (
                        f"·数字 '{v['literal']}' 已涂" if (replaced) else ""),
                    "refs": [rid],
                })
            elif tier == "yellow" and not v.get("caveat_present"):
                enforcement.append({
                    "rule": "stamp-gate-5'", "action": "caveat_annotate",
                    "detail": f"{location}: '{v['literal']}'{{ref:{rid}}} 照印+括注{CAVEAT} (confidence={v['conf']})",
                })

        # RDR-1.G3：先把历史变体 / 残缺形归一成唯一措辞——单独留痕，不混进「折叠」那条
        # （PR #327 复审：只归一没折叠时也记「折叠重复括注」会让事后按该条统计的重复次数偏高）。
        normalized = _normalize_caveats(new_text)
        if normalized != new_text:
            enforcement.append({
                "rule": "stamp-gate-caveat-normalize", "action": "normalize",
                "detail": f"{location}: 括注措辞归一为{_GATE_CAVEAT}（历史变体 / 残缺形）",
            })
            new_text = normalized
        # G3：折叠相邻/重复的未核实括注（门 CAVEAT 每 yellow 标插一次 + fm 自写的
        # 「（未核实）」双系统叠加 → e2e 实测三连）。定稿前统一去重。
        deduped = _dedup_caveats(new_text)
        if deduped != new_text:
            enforcement.append({
                "rule": "stamp-gate-caveat-dedup", "action": "dedup",
                "detail": f"{location}: 折叠重复/相邻未核实括注",
            })
            new_text = deduped

        if new_text != text:
            setter(new_text)

    # ---- 价位门控（GATE-ROUTE G2·改法 (b)：run 级 grounding 地板）----
    # ★ 旧法（已废）= **逐价位**查自己的 source_ref 够不够 verified，不够就抹 level。
    #   结构性缺陷：买入/止损/止盈是 fm **分析推算的目标价**，天底下没有哪个官方来源会
    #   证实"应该在 950 买" → 它们**永远够不到 verified** → 合理价位被系统性删光
    #   （中际旭创 r1 实测抹 4 个；用户问"什么价位"啥也拿不到）。这最顶北极星
    #   「装备决策者」——工具把决策者最想要的可执行价位拿走了。
    #
    # ★ 新法 (b)：不看单个价位的来源，改看**整篇分析有没有据**——
    #   `confidence_map` 里 verified 个数 ≥ _GROUNDING_MIN_VERIFIED → **放行全部价位·原样显示**；
    #   < 阈值（数据几乎全失败的降级 run）→ 才抹（防凭空拍价位的地板）。
    #   性质很松（正常 run 都 ≥2）= 实际把"留不留"交给**真守门 EXEC-FLOOR**：
    #   check②（价位 vs 真实市场价差数量级·独立锚）+ check③（过期锚点撑价位）。
    #
    # ★ 主动废除不变量「带 level ⟺ confidence==verified」：
    #   该不变量曾让 EXEC-FLOOR check③（过期锚点）恒不成立 = 正常态死码。(b) 后带 level 的
    #   非 verified 价位存活 → **check③ 转正为过期价位主保护**（exec_floor.py:279·代码零改）。
    #
    # ★ 极端边界（连现价都拉不到 → check② 退化到模型自报 current_price、两者皆无才 skip）
    #   改在**上游**治（取价 retry + 拿不到 fail-fast·backlog AT），不在本关加判据。
    # 设计：docs/plans/gate-routing-redesign/（轨C 第一关 + 📜决策记录 Q1）。
    ep = decision.execution_plan
    if ep:
        grounded = sum(
            1 for c in confidence_map.values() if c == "verified"
        ) >= _GROUNDING_MIN_VERIFIED
        price_fields = []
        if ep.entry:
            price_fields.append(("entry", ep.entry))
        if ep.stop_loss:
            price_fields.append(("stop_loss", ep.stop_loss))
        for i, tp in enumerate(ep.take_profit):
            price_fields.append((f"take_profit[{i}]", tp))
        for name, pf in price_fields:
            ref_id = getattr(pf, "source_ref", None)
            conf = confidence_map.get(ref_id) if ref_id else None
            if conf is None:
                conf = "unavailable"
            # 仍写 confidence：check③ 读它判过期 + 前端/显示层可用（(b) 只改"抹不抹"、不改"记不记"）
            pf.confidence = conf
            if not grounded:
                for attr in ("low", "high", "level"):
                    if hasattr(pf, attr) and getattr(pf, attr) is not None:
                        enforcement.append({
                            "rule": "price-gate-5'",
                            "action": "strip_level",
                            "detail": (
                                f"execution_plan.{name}.{attr}={getattr(pf, attr)} → null "
                                f"(ungrounded: <{_GROUNDING_MIN_VERIFIED} verified in run)"
                            ),
                        })
                        setattr(pf, attr, None)

    return decision, audits, enforcement


# ---- G5：AI 誊写核查（MASK.GATE-B·2026-07-16 用户拍）------------------------
# 定位：确定性验章门**之后**的一道 AI pass。门只核「引用存不存在」（judge-by-code）；
# 本 pass 核「**来源真这么说吗**」= 誊写保真（catch 抄错/假归因）。**取代 backlog AS 的
# 机械路**——AI 直读研报自由文本即可比对，不需建 per-number 锚定那套贵基建。
#
# 🔴🔴 红线（结构性焊死·非靠自觉）：**只降级·绝不升级**
#   mismatch → 打码（降级=安全方向：AI 误报只多涂一个〔可读性代价〕·永远无法让坏数字变可信）
#   unclear  → 只记日志·不涂（拿不准不动手·控误报）
#   match    → **零动作**（本函数根本不写 tier / confidence / caveat —— **没有提档的代码路**）
# 为什么「升级」危险：[DEFECT-R5-01] 实证门「零判别力·判别力全寄生 LLM 老实度」——B 档被
# 权威域名 + 贴真值数字的伪造骗过、9 条 claim 标 verified。∴ AI 说「对得上」**永远不能**
# 成为可信度依据；要放开须单独走北极星裁决（同 WEB_VERIFIED_ENABLED 规格）。
_TC_SOURCE_MAXLEN = 4000   # 单条来源原文喂 AI 的截断（wisburg 研报文本可长）
_TC_MAX_ITEMS = 40         # 单次核查条数上限（成本护栏）

_TRANSCRIPTION_CHECK_PROMPT = """你是投资决策报告的**誊写核查员**。任务：核对报告正文里的数字，是否如实照抄了它声称的来源。

## 输入
`items` 数组，每条含：`id`（本条唯一编号·**原样回填**）/ `ref`（来源编号）/ `written`（正文里写的数字）/ `context`（该数字所在句）/ `source`（它声称的来源原文）。

**同一个 `ref` 可能被多条引用**（同一来源支撑多个数字）——它们是**互相独立**的判定，必须**逐条**给结论、各自回填自己的 `id`。

## 逐条判定（三档·严格按定义）
- `match`：来源明确支持这个数字（数值一致·**含合理的单位/量纲换算**，如 "81.6 亿" vs "$8.16B"）
- `mismatch`：来源**明确**写着**另一个数**（如正文写 350、来源写 300）——**只有确凿冲突才用**
- `unclear`：来源里找不到这个数 / 读不准 / 语义模糊 / 需要推断 —— **拿不准一律用这档**

## 铁律
1. **拿不准就 `unclear`，绝不猜 `mismatch`**。误报 mismatch 会让**正确**数字被无谓涂掉、损害报告可读性。
2. 单位 / 量纲 / 口径差异（亿 vs 十亿、% vs 个百分点、财年 vs 自然年、约数 vs 精确值）**不算 mismatch**，除非数值本身确凿冲突。
3. 你的判定**只用于降级**（涂掉可疑数字）。报 `match` **不会**让任何数字被标成「已核实」——**别为了帮它过关而报 match**，那对系统没有任何作用。

## 输出（严格 JSON·不要 markdown 代码块·不要任何解释文字）
**每条输入 item 出一条 check·`id` 必须原样回填**（漏 `id` 的条目会被丢弃 = 该数字不被核查）：
{"checks":[{"id":"i0","ref":"f3","written":"300","verdict":"match","source_says":"目标价300美元","reason":"来源标题明确写目标价300美元"}]}
"""


#: 「来源称:」那半的展示预算（字符）。原文本体上限是 `_TC_SOURCE_MAXLEN`，两者无关。
_EXCERPT_LEN = 60

#: 原文里的"一个数"：允许千分位 / 小数点 / 区间连字符，但**必须以数字收尾**，
#: 免得把 ``300.`` 的句号也算进来。用于把摘录窗口对准数字。
_NUM_IN_SOURCE = re.compile(r"\d[\d,.–—~\-]*\d|\d")


def _clip_with_ellipsis(s: str, limit: int) -> str:
    """超预算就截，并**显式打省略号** —— 让"这里被截过"看得见，而不是读成完整的。"""
    return s if len(s) <= limit else s[:limit] + "…"


def _excerpt_around_number(src: str, limit: int = _EXCERPT_LEN) -> str:
    """摘一段**能看到数字**的原文；**绝不把数字切一半**。

    规则：以原文里**最长的那个数**为中心开窗；数字本身比预算还长时**宁可超预算也给全**
    （半截数字比长一点危险得多）；两端有省略即打 ``…``。
    原文没有数字时退回"从头截 + 省略号"。

    **为什么取最长而不是第一个**：实测一句真实来源开头是"美联储 **9** 月议息会议纪要…"，
    对准第一个数就对准了那个 ``9``，而真正要给人看的 ``4,100-4,700`` 在句尾、落在窗外 ——
    等于没治好。位数多 / 带千分位或区间号的那个，才更像正事。

    ⚠️ **这是启发式**：原文里有多个实质数字时，可能开在不是本次争议的那一个上。
    它保证的是"**一定能看到某个完整的数**"，不是"一定是那个数"。
    要更准需把争议数字传进来做定位 —— 但 mismatch 场景下来源恰恰**不含**正文那个数，
    没有可靠的锚，故不做（做了也是猜）。
    """
    if len(src) <= limit:
        return src
    nums = list(_NUM_IN_SOURCE.finditer(src))
    m = max(nums, key=lambda x: x.end() - x.start()) if nums else None
    if m is None:
        return src[:limit] + "…"
    num_len = m.end() - m.start()
    span = max(limit, num_len)                  # 装不下数字就把窗口撑到装得下
    start = max(0, m.start() - (span - num_len) // 2)
    end = min(len(src), start + span)
    start = max(0, end - span)                  # 贴到右端时把左侧补回来
    return ("…" if start > 0 else "") + src[start:end] + ("…" if end < len(src) else "")


def _source_says_or_excerpt(check: dict, item: dict) -> str:
    """G5 mismatch 记录里「来源称:」那半 —— 模型漏回填时退回**真实来源原文摘录**。

    **为什么需要兜底（2026-08-14·BC 收官中际旭创跑实测）**：模型对 mismatch 条目
    **可以只给 verdict 不给 ``source_says``**，此前直接落成「（来源称: ）」——
    括号是空的。后果不是难看，是**排查断链**：读记录的人看得到"正文写了 4,000、
    与来源不符"，却看不到**来源到底写的是多少**，必须回去翻底稿才知道该不该信这次涂。
    而那份来源原文**我们手上就有**（喂给核查的 ``item["source"]``），没有理由不写。

    ⚠️ **两半必须可区分**：模型给的结论（``source_says``）与我们摘的原文是两回事，
    后者带 ``原文摘录:`` 前缀标明出处，**不冒充模型的判断**。

    🔬 **摘录必须围着数字摘（2026-08-14 冷审修）**：初版从原文**开头**截 60 字，
    而来源原文最长可到 ``_TC_SOURCE_MAXLEN``（4000）、数字通常在后半 ——
    实测一句 82 字的真实来源，摘出来的 60 字**完全不含**那个区间，
    等于"排查断链"没被治好，只是把空括号换成了一段无关前文。
    更坏的是切口落在数字中间时会印出 ``…4,100``：**读起来是个完整数字，其实是一半** ——
    在一份专门用来判断"这次涂得对不对"的记录里，这就是本项目定义的致命
    （错的数字伪装成对的）。故现在 :func:`_excerpt_around_number` 保证
    **数字整体入选、截断处显式打省略号**。
    """
    says = str(check.get("source_says") or "").strip()
    if says:
        # 模型给的结论一般是短句，但同样不许"截半了看着还像完整的"
        return _clip_with_ellipsis(says, _EXCERPT_LEN)
    src = str(item.get("source") or "").strip()
    if src:
        return f"模型未回填·原文摘录: {_excerpt_around_number(src, _EXCERPT_LEN)}"
    return "模型未回填·且该 ref 解析不出来源原文"


def _transcription_source_text(
    rid: str, *, findings_by_id: dict, facts_by_id: dict, ref_lookup: dict,
) -> str:
    """G5：把一个 {ref} 编号解析成「它声称的来源原文」（喂 AI 核查用）。"""
    from committee.facts.stamp_families import split_stamps

    if rid.startswith("v"):
        f = findings_by_id.get(rid)
        if f is None:
            return ""
        parts = [str(getattr(f, "finding", "") or "")]
        if getattr(f, "source", None):
            parts.append(f"[source: {f.source}]")
        return " ".join(p for p in parts if p)[:_TC_SOURCE_MAXLEN]

    fact = facts_by_id.get(rid)
    if fact is None:
        return ""
    parts = [str(getattr(fact, "claim", "") or "")]
    for wm in getattr(fact, "watermarks", None) or []:
        for _fam, canon in split_stamps(wm):
            ref = ref_lookup.get(canon)
            if ref is not None and getattr(ref, "value", None):
                parts.append(f"[{canon}] {ref.value}")
    return "\n".join(p for p in parts if p)[:_TC_SOURCE_MAXLEN]


def _apply_ai_transcription_check(
    decision: FinalDecision,
    audits: list[ClaimAudit],
    findings: list,
    pass0_result,
    common_context,
) -> tuple[FinalDecision, list[dict]]:
    """G5 主体：AI 核「来源真这么说吗」→ **只降级**。见上方红线。

    Returns: (decision, enforcement entries)
    """
    from committee.config import (
        TRANSCRIPTION_CHECK, TRANSCRIPTION_CHECK_MAX_TOKENS, TRANSCRIPTION_CHECK_MODEL,
    )
    from committee.facts.confidence import qualitative_word

    enforcement: list[dict] = []
    if not TRANSCRIPTION_CHECK:
        return decision, enforcement

    findings_by_id = {f.id: f for f in findings}
    facts_by_id = {
        fi.fact_id: fi
        for fi in (getattr(pass0_result, "facts_inventory", None) or [])
    }
    ref_lookup = {
        r.ref_id: r for r in (getattr(common_context, "references", None) or [])
    }

    # 待核项：**带标 + 有数字 + 门没涂过**（门涂过的已是 🔴·无需再核）。
    # 无标数字不进（那是 G1 的域：只记日志·门不碰）。
    items: list[dict] = []
    for a in audits:
        if not a.matched_finding or a.replaced or not a.value:
            continue
        src = _transcription_source_text(
            a.matched_finding, findings_by_id=findings_by_id,
            facts_by_id=facts_by_id, ref_lookup=ref_lookup,
        )
        if not src:
            continue
        # id：**逐条**唯一。不能拿 ref 当 key——同一 ref 常支撑多个数字
        # （f3 既挂 "300" 又挂 "8.16"），按 ref 归并会让一条 mismatch 连坐另一条 match
        # 的数字（涂错），或反过来让真 mismatch 被 match 覆盖掉（漏涂）。
        items.append({"id": f"i{len(items)}", "ref": a.matched_finding, "written": a.value,
                      "context": a.claim_text, "source": src, "_audit": a})
        if len(items) >= _TC_MAX_ITEMS:
            break
    if not items:
        return decision, enforcement

    payload = [{k: it[k] for k in ("id", "ref", "written", "context", "source")} for it in items]
    try:
        # max_tokens 给足：gemini-2.5-pro 的 thinking token 会吃掉默认 4096 预算
        # → 可见输出为空 → fail-open 空跑（G4 e2e 2026-07-16 实证）。见 config 注释。
        llm = _llm(TRANSCRIPTION_CHECK_MODEL, temperature=0.0, tag="transcription_check",
                   max_tokens=TRANSCRIPTION_CHECK_MAX_TOKENS)
        resp = llm.invoke([
            SystemMessage(content=_TRANSCRIPTION_CHECK_PROMPT),
            HumanMessage(content=json.dumps({"items": payload}, ensure_ascii=False)),
        ])
        raw = resp.content if isinstance(resp.content, str) else str(resp.content)
        checks = _extract_json(raw).get("checks") or []
    except Exception as exc:
        # ★ fail-open：核查是**额外**一层；跑不了就退回确定性门的产出（= 引入本 pass
        # 之前的行为·安全）。fail-closed（涂掉全部）= 灾难性过度打码。
        log.warning("G5 transcription check skipped (fail-open): %s", exc)
        enforcement.append({
            "rule": "ai-transcription-check", "action": "skipped_fail_open",
            "detail": f"AI 誊写核查失败·跳过（不涂·退回确定性门产出）: {exc}",
        })
        return decision, enforcement

    by_id: dict[str, dict] = {}
    for c in checks:
        if isinstance(c, dict) and c.get("id"):
            by_id.setdefault(str(c["id"]), c)

    # mismatch → 按**本条自己的 location** 收集要涂的字面数字。
    # 不能拿一个扁平的 to_mask 去涂所有字段：sec_1 里一个对不上源的 "300"，会把
    # core_risks 里另一个合法的 "300" 一并涂掉 = 重新引入 GATE-B 刚治好的过度打码。
    mask_by_loc: dict[str, list[dict]] = {}
    for it in items:
        c = by_id.get(it["id"])
        if not c:
            continue    # 模型漏回填 id → 该条不核（与 fail-open 同向·不涂）
        verdict = str(c.get("verdict") or "").strip().lower()
        if verdict == "mismatch":
            mask_by_loc.setdefault(it["_audit"].location, []).append(it)
            enforcement.append({
                "rule": "ai-transcription-mismatch", "action": "qualitative_replace",
                "detail": (f"{it['_audit'].location}: '{it['written']}'{{ref:{it['ref']}}} 与来源不符"
                           f"（来源称: {_source_says_or_excerpt(c, it)}）→ 涂"),
            })
        elif verdict == "unclear":
            enforcement.append({
                "rule": "ai-transcription-unclear", "action": "log_only",
                "detail": (f"{it['_audit'].location}: '{it['written']}'{{ref:{it['ref']}}} 来源未明确支持"
                           f"（{str(c.get('reason') or '')[:60]}）·原样保留·仅记审计"),
            })
        # verdict == "match" → **零动作**（🔴 不写 tier/confidence/caveat·无提档代码路）

    if not mask_by_loc:
        return decision, enforcement

    repl = qualitative_word("other")
    for location, text, setter in _iter_prose_fields(decision):
        hits = mask_by_loc.get(location)
        if not text or not hits or not location.startswith(_REPLACEABLE_LOC_PREFIXES):
            continue
        new_text = text
        masked_lits: set[str] = set()
        for it in hits:
            new_text, n = _mask_number_occurrences(new_text, it["written"], repl)
            # ★ replaced 记**实际改没改文本**（location 在涂的执行面外 / 数字已不在正文
            # → 一个字没动）。无条件写 True = archive 说谎。
            # `masked_lits`：同字段两条 mismatch 撞同一字面数字时，第一条已把该数字的
            # **所有**出现涂完 → 第二条 n==0，但它的数字确实被涂了 → 仍记 replaced
            # （否则反向说谎：漏记）。
            if n or it["written"] in masked_lits:
                masked_lits.add(it["written"])
                it["_audit"].replaced = True
                it["_audit"].replacement_text = repl
        if new_text != text:
            setter(new_text)

    return decision, enforcement


def _derive_prose_gate_status(decision: FinalDecision, scan_succeeded: bool) -> str:
    """机械派生散文层门控状态 —— 由字段实际可信度推导，不独立赋值、不靠 LLM 自觉。

    spec R-3 / A3「全抹自检」：若状态独立默认 verified，会出现机器层撒谎——
    报 verified 但承重价位（execution_plan）全 null/model_prior。本函数把 status
    钉死在事实上：verified **同时**要求

    - scan_succeeded：门控有效执行。MASK.C3 后验章门（_apply_stamp_gate）为纯代码、
      恒执行 → 调用方恒传 True（旧 DeepSeek scan 的失败降级来源已消失·参数保留
      以钉住"门没跑过就不许报 verified"的契约语义）；
    - 价位未被 (b) 地板抹光：若 execution_plan 存在价位字段，**至少一个还带实际 level**。

    ★ **GATE-ROUTE G2 判据变更**（2026-07-22 用户拍·随价位门控 (b) 同步）：
    旧判据是「至少一个价位 `confidence==verified`」，与旧价位门控的「非 verified 即抹 level」
    互为表里（那时"带 level" ⟺ "verified"，两种写法等价）。(b) 废除该不变量后
    **留下的价位多是非 verified** → 若不同步改，本函数会把**正常 grounded run 全员误报
    degraded**。新判据直接看"价位有没有被抹光"（= (b) 地板是否 fire），语义与 A3
    「全抹自检」的原意一致：**机器层不许在承重价位全没了的时候还报 verified**。

    任一不满足 → degraded（spec A3 明确「硬拦转 degraded」）。价位 level/confidence 由
    `_apply_stamp_gate` 的价位门控段机械赋值，故本函数须在其后调用。

    零下游风险（已全仓核）：`prose_gate_status` **无消费方**——前端不读（types.ts 无该
    字段）、无闸 branch 读它、仅本函数派生 + set + log + schema 定义 + 测试。
    """
    if not scan_succeeded:
        return "degraded"
    ep = decision.execution_plan
    if ep is not None:
        price_fields = [
            pf for pf in (ep.entry, ep.stop_loss, *ep.take_profit) if pf is not None
        ]
        has_any_level = any(
            getattr(pf, attr, None) is not None
            for pf in price_fields
            for attr in ("low", "high", "level")
        )
        if price_fields and not has_any_level:
            return "degraded"
    return "verified"


def _translate_web_markers_to_citations(
    decision: FinalDecision, ledger: list[dict] | None,
) -> list[dict]:
    """步骤 7.5（T11·麻烦一 c）— 最终正文里的外部数据章 [W#…] 翻译成人看的引用 [来源N]。

    章是内部流水号，不该出现在给用户看的决策书里。回查外源册把每枚章解析成来源域名：
    - 能解析（num_id 在册）→ 换成按首次出现顺序编号的 [来源N]，同一 num_id 复用同号；
      并产出脚注 ``{marker, num_id, source, url}``。
    - 解析不到（空头章/损坏）→ 从正文移除（指向空的引用不留，避免误导）。

    只改**展示层文本**（thesis/core_risks/position_size/trigger/dissent），零判定影响；
    gate/audit 永不读产出的 ``web_citations``（#5 隔离·不是 references_appendix）。
    """
    from committee.facts.stamp_families import find_web_markers

    src: dict[str, tuple[str, str]] = {}
    for e in ledger or []:
        for n in (e.get("number_registry") or []):
            nid = (n or {}).get("num_id")
            if isinstance(nid, str):
                src.setdefault(nid, (e.get("domain", "") or "", e.get("url", "") or ""))

    numbering: dict[str, str] = {}
    citations: list[dict] = []

    def _rewrite(text: str) -> str:
        if not text:
            return text
        markers = find_web_markers(text)
        if not markers:
            return text
        out: list[str] = []
        last = 0
        for s, e, canon in markers:
            out.append(text[last:s])
            if canon in src:
                label = numbering.get(canon)
                if label is None:
                    label = f"来源{len(numbering) + 1}"
                    numbering[canon] = label
                    dom, url = src[canon]
                    citations.append({"marker": label, "num_id": canon, "source": dom, "url": url})
                out.append(f"[{label}]")
            # 解析不到 → 移除（append 空）
            last = e
        out.append(text[last:])
        return "".join(out)

    for sec in decision.thesis_sections:
        sec.body = _rewrite(sec.body)
    for cr in decision.core_risks:
        cr.risk = _rewrite(cr.risk)
        cr.mitigation = _rewrite(cr.mitigation)
    decision.position_size = _rewrite(decision.position_size)
    decision.trigger_events = [_rewrite(t) for t in decision.trigger_events]
    decision.dissenting_views = [_rewrite(d) for d in decision.dissenting_views]
    return citations


# 涂数字时一并吞掉的**前置**货币符号（见 `_mask_number_occurrences` docstring）。
# 只列紧贴数字写的单字符符号；``US$`` / ``HK$`` 这类多字符前缀留下的 "US" 属另一形态，
# 未观察到，不预防性处理（多消费字符 = 误伤面变大）。
_CURRENCY_PREFIXES = frozenset("$¥￥€£₩")


def _mask_number_occurrences(text: str, literal: str, replacement: str) -> tuple[str, int]:
    """把 ``text`` 里**所有独立出现**的字面数字 ``literal`` 换成 ``replacement``。

    Returns: ``(新文本, 实际涂了几处)`` —— 调用方据此如实回填 ``ClaimAudit.replaced``。

    取代旧的 ``_replace_value_and_marker``（``str.find`` 版·MASK.GATE-B-fix finding 2），
    两处关键差别：

    1. **数字边界**：前后不得贴数字/小数点 → 涂 "300" 不会命中 "1300" / "300.5" 的**内部**
       （``str.find`` 会——把正文改成 "1相关数值"）。
    2. **涂全部而非首个**：同字段同一字面数字出现多次时，光凭字面分不出哪个是对不上源的
       那个 → **一律涂**。宁可多涂一个（可读性代价·安全方向），也不放走与来源冲突的数字
       （放走 = 错数字伪装成对的 = 本项目定义的致命）。

    紧跟的外部数据章一并移除（数字成定性词后出处不该悬空·T11 麻烦一 b）。

    **紧贴在前的货币符号一并移除**（2026-08-14·BC 收官黄金跑实测）：替换词是**无量纲的
    名词**（"相关数值" / "关键价位区间"…），前面留着 ``$`` 会印出「基准情景：**$相关数值**
    区间震荡」这种半截句 —— 涂得对（错数字确实该拿掉），呈现是坏的。
    ⚠️ **只处理紧贴的前置货币符号**。后置单位（``相关数值元`` / ``相关数值%``）**不处理** ——
    〔**2026-08-14 订正**：本行初稿写「未观察到」，**当天冒烟即观察到**（A 股跑印出
    「止损**相关数值元**{ref:f43}」「持仓者**相关数值元**」）。**结论不变、理由要换**：
    不处理**不是**因为没见过，而是因为**它不坏**——「相关数值元」读着别扭但语义完整、
    不像 ``$相关数值`` 那样看着像模板漏填；而多消费一个尾字符的误伤面更大
    （``元`` / ``%`` 可能属于后面另一句）。**要改须先有"它真的误导了读者"的实证。**〕
    """
    from committee.facts.stamp_families import web_marker_end_at

    if not literal:
        return text, 0
    pat = re.compile(r"(?<![\d.])" + re.escape(literal) + r"(?![\d.]*\d)")
    out: list[str] = []
    idx = n = 0
    for m in pat.finditer(text):
        if m.start() < idx:
            continue                      # 落在上一处替换（含章）范围内
        start = m.start()
        # 前置货币符号回退：仅当它**紧贴**数字（中间无空格）才吞，避免误伤
        # "价格为 $ 300" 这类写法之外的正常文本。
        if start > 0 and text[start - 1] in _CURRENCY_PREFIXES:
            start -= 1
        out.append(text[idx:start])
        out.append(replacement)
        idx = web_marker_end_at(text, m.end())
        n += 1
    if not n:
        return text, 0
    out.append(text[idx:])
    return "".join(out), n


def _note_reference_dropped(ref_id: Any, branch: str, exc: BaseException) -> None:
    """留一条「引用条目坏了被扔掉」（BK.2 P0.4）。只加留痕，丢弃行为一个字不改。

    为什么要紧：引用校验集只认编号、不看这条能不能装进清单 ⇒ 正文里的引用活着，
    读者去文末清单查却查无此条 = **断掉的引用**。前两支原先连日志都没有。
    """
    note_degradation(
        "reference_entry_dropped",
        f"ref_id={ref_id}; branch={branch}; {type(exc).__name__}",
    )


def _fact_relevance(item: Any, ref_by_id: dict) -> str:
    """DS-0 事实在表③ 的身份 = 它所引表① 引用的身份（CRED.2.G4·backlog BS）。**只取保守的一头**：

    - 没引表① / 所引任一条未标注 → ``""``（不替它下结论）；
    - 所引编号在表① 里**查不到**（转抄抄错数字等）→ 同样按未标注算，``""``
      —— 跳过它会让「一条对题 + 一条查无此条」冒充整条对题；
    - 所引里有 ``off_topic`` → ``off_topic``；有 ``context`` → ``context``；
    - **全部** ``on_topic`` 才 ``on_topic``（一条背景引用就不许整条冒充「针对本问题」）。
    """
    from committee.facts.stamp_families import FAMILY_EXTERNAL, split_stamps

    rels = [
        (getattr(ref_by_id[canon], "relevance", "") or "") if canon in ref_by_id else ""
        for wm in (getattr(item, "watermarks", None) or [])
        for fam, canon in split_stamps(wm)
        if fam != FAMILY_EXTERNAL
    ]
    if not rels or "" in rels:
        return ""
    for worst in ("off_topic", "context"):
        if worst in rels:
            return worst
    return "on_topic"


def _build_references_appendix(
    findings: list[VerificationFinding],
    confidence_map: dict[str, FindingConfidence],
    pass0_result: Any,
    external_ledger: list[dict] | None = None,
    *,
    today: "date | None" = None,
    references: list | None = None,
) -> list[ReferenceEntry]:
    """步骤 8 辅助 — 内源（verification findings + DS-0 facts）+ 外源（external_websearch
    外源册 ``wN``）→ references_appendix（表③·**纯展示表**）。

    FindingConfidence → CredibilityTier 映射（内源）；外源 ``tier`` 本就是合法
    CredibilityTier（``web-corroborated`` / ``web-single``）直接落 ``credibility``。

    ★ **T4 受控放开（外源合进表③·2026-07-09）**：本函数曾由 T3（2026-07-01）焊死"外源永不
    进表③"（签名只收三个内源入参），因为当时 **gate 实读本附录**——外源以 ``wN`` 进来会把
    ``all_unverified`` 变 False、压制 risk_gate 安全地板 AD.7/C（D1 症状）。**层② 相位2a
    （#176·`d5c42e1`·2026-07-07）已让 gate 与表③彻底脱钩**（EXEC-FLOOR 闸内现算
    ``execution_support``·check①/②/③ 全不读 references_appendix）→ 表③退成**纯展示**
    → T4 放开外源通道**不再稀释 gate**（gate 结构性够不着表③）。故本函数新增
    ``external_ledger`` 入参、把外源 ``wN`` 条目并进展示。
    ★ **红线（绝不越）**：外源册**绝不并进** ``internal_structured`` / ``ctx.references``——
    audit 的 ``_build_ref_lookup`` 永远只遍历内源册。本函数只把外源**展示**进给人看的表③，
    不改 audit 认证域；``wN`` 命名空间与内源 ``REF#`` 族双向互不误捕（#5 verified 后门仍关死）。
    ★ **外源 ``is_outdated`` 按 as_of 现算**（非默认"不过期"）：外源册条目无 confidence、只有
    ``as_of``（publication_date·可空）；这里按 ``staleness_days`` 现算——缺失 / 非法 / 未来 /
    超通用窗口（``FRESHNESS_WINDOW_DAYS["other"]``）→ ``True``（当过期看·不冒充新鲜）。与内源
    ``sourced_outdated`` 的口径一致。**注**：``is_outdated`` 现为**纯展示打标**（层② 后 gate
    不再读表③·见 ``_OUTDATED_CONFIDENCES`` 处注释）——此处现算是为**对人诚实**（过期外源不装新鲜），
    非为喂安全闸。
    ★ 内源 ``is_outdated``：装配期从 ``confidence ∈ _OUTDATED_CONFIDENCES`` 带出
    （credibility 显示值不动）——DEFECT-D1-ROOT 组合修法（2026-07-02 `66c411d`）遗留列，
    层② 后同样退为纯展示打标。
    ★ **T6 方案A（DS-0 as_of 归一·2026-07-09）**：DS-0 fact 的 ``as_of`` 是 ``FactInventoryItem``
    的**裸 str**（LLM 产·非 ``AsOfDate`` 类型·schema 层不校验），脏日期（如 ``"Q3 2024"`` /
    ``"2026/06/05"``·``_normalize_as_of`` 归一不掉）直接喂 ``ReferenceEntry.as_of`` 严格
    ``AsOfDate`` 会 fail-fast 抛异常 → 撞下方 ``except`` → 该条被**静默丢弃**；而
    ``valid_fact_ids``（引用校验集）只收 ``fact_id`` 不看日期 → 正文 ``{ref:fX}`` 引用存活
    但清单查无此条 = **引用断链**。修法 = 先 ``sanitize_as_of`` 归一（脏日期只丢日期不丢整条），
    与 T4 外源半（下方 ``external_ledger`` 块）**同款抢救路径对称**。**verdict-neutral**：表③纯
    展示（层② 相位2a 后 gate 不读）；confidence/gate 各自独立读 ``item.as_of``（``_derive_all_confidence``），
    本函数不改它们的输入。findings 循环无需归一——``VerificationFinding.as_of`` 已是 ``AsOfDate``
    类型（构造期已校验·恒合法）。
    """
    from committee.as_of import sanitize_as_of

    refs: list[ReferenceEntry] = []

    for f in findings:
        cred = _CONFIDENCE_TO_CREDIBILITY.get(f.confidence, "unverified")
        try:
            refs.append(ReferenceEntry(
                ref_id=f.id,
                source=f.source or "",
                locator=f.source or "",
                credibility=cred,
                as_of=f.as_of or "",
                contested=f.conflict,
                is_outdated=f.confidence in _OUTDATED_CONFIDENCES,
            ))
        except Exception as ex:  # noqa: BLE001 — 丢条目不许挡住装配（判定不变），但不许再无痕
            _note_reference_dropped(f.id, "finding", ex)

    # CRED.2.G4（backlog BS）：DS-0 事实行继承所引表① 引用的身份（见 `_fact_relevance`）
    _ref_by_id = {r.ref_id: r for r in (references or [])}
    if pass0_result and pass0_result.facts_inventory:
        for item in pass0_result.facts_inventory:
            conf = confidence_map.get(item.fact_id, "unavailable")
            cred = _CONFIDENCE_TO_CREDIBILITY.get(conf, "unverified")
            locator = ", ".join(item.watermarks) if item.watermarks else ""
            try:
                refs.append(ReferenceEntry(
                    ref_id=item.fact_id,
                    source=item.claim[:80],
                    locator=locator,
                    credibility=cred,
                    as_of=sanitize_as_of(item.as_of),  # T6 方案A：脏日期只丢日期不丢整条（防引用断链）
                    is_outdated=conf in _OUTDATED_CONFIDENCES,
                    relevance=_fact_relevance(item, _ref_by_id),
                ))
            except Exception as ex:  # noqa: BLE001 — 同上
                _note_reference_dropped(item.fact_id, "fact", ex)

    # ==== T4：外源册 wN 条目受控接入（gate 已不读表③=纯展示·#176 层② 相位2a）====
    # credibility 直接取册内 tier（web-corroborated/web-single 本就是合法 CredibilityTier·
    # 永不 verified=封顶红线在 tier 生成端已保证）；is_outdated 按 as_of 现算（见 docstring）。
    if external_ledger:
        from committee.as_of import staleness_days  # sanitize_as_of 已在函数顶导入
        from committee.facts.confidence import FRESHNESS_WINDOW_DAYS
        _win = FRESHNESS_WINDOW_DAYS["other"]  # 外源无 data_kind → 通用兜底窗口（不自造阈值）
        for e in external_ledger:
            if not isinstance(e, dict):
                continue
            # 先归一 as_of（抢救路径：写坏的日期只丢日期不丢整条源·同 AO evidence_log 兜底），
            # 再据归一值现算过期——保证显示日期与 is_outdated 口径一致。
            as_of = sanitize_as_of(e.get("as_of", ""))
            days = staleness_days(as_of, today=today)
            outdated = days is None or days < 0 or days > _win
            tier = e.get("tier") or "web-single"  # 生成端恒发 web-*·此兜底仅防损坏册（保守取单源）
            try:
                refs.append(ReferenceEntry(
                    ref_id=e.get("ref_id", "") or "",
                    source=e.get("domain", "") or "",
                    locator=e.get("url", "") or "",
                    credibility=tier,
                    as_of=as_of,
                    is_outdated=outdated,
                    origin=e.get("origin", "") or "",  # T4.2：检索方展示（analyst/fund_mgr）
                ))
            except Exception as ex:
                # 损坏册条目（坏 tier/字段）→ 跳过但留痕（不像内源静默 pass·外源丢源应可见）。
                log.warning("T4: skip malformed external ledger entry %s: %s",
                            e.get("ref_id", "?"), ex)
                _note_reference_dropped(e.get("ref_id", "?"), "external", ex)

    return refs


def _build_outline(
    outline_llm: BaseChatModel,
    user: str,
    reports: list[AnalysisReport] | None = None,
) -> DecisionOutline:
    """outline pass + 单段 fallback（PR 3）+ Synthesis Reconciliation 注入（PR-8c P4.B.6）。
    任何失败均不抛——返回单段 outline。

    LLM 输出契约：``{"thesis_outline": list[str]}``，长度 3-5；后端注入 id
    后再 model_validate。schema 层放宽到 1-5 是为了容纳合成的单段降级构造，
    LLM 输出仍受 3-5 约束（不符即 fallback）——"schema 宽容 + 节点严格"
    的刻意分工。

    ``reports`` 提供时，在 outline 最前注入 reconciliation section（F×T / F×S），
    总段数 cap 在 5；reconciliation 也注入到 fallback 单段路径（合成优先于降级正文）。
    """
    recon = reconciliation_titles(reports or [])
    noted: list[str] = []

    def _note(branch: str) -> None:
        """BK.2 P0.3：大纲退成单段留一条痕。只加留痕 —— 3–5 门、合成段注入、单段兜底内容一字不改。

        **一次退路只发一条**：解析失败后走 ``_assemble`` 若又撞装配校验，是同一件事（论述结构塌了），
        不是两件；detail 记**先发生的那一支**。
        """
        if noted:
            return
        noted.append(branch)
        note_degradation(
            "decision_outline_fallback",
            f"branch={branch}; recon_sections={len(recon)}",
        )

    def _assemble(base_titles: list[str], checklist: list[dict] | None = None) -> DecisionOutline:
        """recon 前置 + base 拼接 + cap 5 + 重编 id + validate（失败回单段）。"""
        merged = recon + base_titles
        merged = merged[:_OUTLINE_MAX]
        specs = [{"id": f"sec_{i+1}", "title": clip_title(str(t))} for i, t in enumerate(merged)]
        payload: dict = {"thesis_outline": specs}
        if checklist:
            payload["verify_checklist"] = checklist
        try:
            return DecisionOutline.model_validate(payload)
        except pydantic.ValidationError as e:
            log.warning("decision_outline_validation_error: %s; fallback 单段", e)
            # ⚠️ **成功路径也会走到这里**：模型给了合法的 3–5 段，但装配校验挂了（实测在册归档
            # 4 份单段全是这一支 —— 查证清单里一个档位值不合法，连带整份大纲作废）。
            _note("assemble_validation:" + ",".join(sorted({
                ".".join(str(x) for x in err.get("loc", ())[:1]) for err in e.errors()})))
            return _FALLBACK_OUTLINE

    try:
        raw = _invoke_json(outline_llm, DECISION_OUTLINE_PROMPT, user)
    except (ValueError, json.JSONDecodeError) as e:
        log.warning("decision_outline_parse_error: %s; fallback 单段(+recon)", e)
        _note("parse")
        return _assemble(["整体投资逻辑"]) if recon else _FALLBACK_OUTLINE

    raw_titles = raw.get("thesis_outline", [])
    if not isinstance(raw_titles, list) or not raw_titles:
        log.warning(
            "decision_outline_shape_error: %r; fallback 单段(+recon)",
            type(raw_titles).__name__,
        )
        _note("shape")
        return _assemble(["整体投资逻辑"]) if recon else _FALLBACK_OUTLINE

    # 验收门：LLM 输出必须 3-5；不符 → fallback。schema 层 1-5 才允许 fallback 存在。
    if not (3 <= len(raw_titles) <= 5):
        log.warning(
            "decision_outline_length_gate: LLM 输出 %d 项，非 3-5；fallback 单段(+recon)",
            len(raw_titles),
        )
        _note(f"length:{len(raw_titles)}")
        return _assemble(["整体投资逻辑"]) if recon else _FALLBACK_OUTLINE

    raw_checklist = raw.get("verify_checklist", [])
    checklist_dicts: list[dict] = []
    # BK.2 M3.2（2026-09-18·新行 #63）：没写事项 / 非 dict 的条目在这里被过滤 —— 它们**到不了**下面的
    # 逐项校验（#304 那条只盖「有事项但字段坏」）。过滤行为一字不改，只把被扔的攒起来留一条痕。
    prefilter_dropped: list[str] = []
    if isinstance(raw_checklist, list):
        for i, vc in enumerate(raw_checklist):
            if isinstance(vc, dict) and vc.get("item"):
                checklist_dicts.append(vc)
            else:
                why = "no_item" if isinstance(vc, dict) else f"non_dict={type(vc).__name__}"
                prefilter_dropped.append(f"#{i+1}: {why}; raw={_clip_dropped_item(vc)}")
    if prefilter_dropped:
        _note_checklist_items_dropped("prefilter", prefilter_dropped)
    # BK.2 大纲缺陷小修（2026-09-18·用户裁 A）：清单逐项校验，坏字段回默认值、保住大纲。
    # 此前清单里一个档位值不合法就让 _assemble 整份校验失败 → 五段大纲连同清单一起作废
    # （在册 29 份带决策存档里 4 份，原因全同：criticality 写了 "medium"）。
    checklist_dicts = _sanitize_verify_checklist(checklist_dicts)

    return _assemble([str(t) for t in raw_titles], checklist_dicts)


#: 查证清单单项里允许「坏了就回默认值」的字段（默认值取自 schema 自己：VerifyItem 的字段默认）。
#: ``item`` 不在其中——没有事项文本的条目没法留，只能丢。
_CHECKLIST_COERCIBLE_FIELDS = ("criticality", "data_kind", "conflict")


def _sanitize_verify_checklist(items: list[dict]) -> list[dict]:
    """查证清单逐项校验（BK.2 大纲缺陷小修·2026-09-18·用户裁 A「保留该项、坏字段按默认值记」）。

    **治的病**：模型在清单里写了 schema 不认的值（实测全是 ``criticality="medium"``，schema 只认
    high / low），``DecisionOutline.model_validate`` 整份失败 → 五段大纲作废、论述退成一整段 ——
    清单里一个小字段写错，代价是整篇论述的结构（在册 29 份带决策存档里 4 份 = 14%）。

    **做法**：每项先按 :class:`VerifyItem` 校验；不过 → 把报错点名的字段**删掉让 schema 默认值接手**
    （重要程度默认 low、数据类型默认 other、冲突默认 False）再校验一次；仍不过（``item`` 本身坏）→ 丢该项。
    **对「查哪些数字」零影响**：核验只查 ``criticality == "high"`` 的项，坏值改前改后都不会被查。
    只要动了任何一项就留一条痕（``verify_checklist_item_coerced``），detail 记模型原本写的是什么。

    ⚠️ 只在**清单项**这一层容错；大纲标题 / 段数的 3–5 门一个字不改（那是设计内的验收门）。
    """
    if not items:
        return items
    kept: list[dict] = []
    coerced: list[str] = []
    dropped: list[str] = []
    for vc in items:
        try:
            VerifyItem.model_validate(vc)
            kept.append(vc)
            continue
        except pydantic.ValidationError as e:
            bad = {str(err["loc"][0]) for err in e.errors() if err.get("loc")}
        fixable = bad & set(_CHECKLIST_COERCIBLE_FIELDS)
        fixed = {k: v for k, v in vc.items() if k not in fixable}
        try:
            if not fixable:
                raise ValueError("no coercible field")
            VerifyItem.model_validate(fixed)
        except (pydantic.ValidationError, ValueError):
            dropped.append(f"{str(vc.get('item', ''))[:40]}: {sorted(bad)}")
            continue
        kept.append(fixed)
        got = "; ".join(f"{k}={vc.get(k)!r}" for k in sorted(fixable))
        coerced.append(f"{str(vc.get('item', ''))[:40]}: {got}")
    if coerced or dropped:
        log.warning(
            "verify_checklist: %d 项字段不合法已回默认值、%d 项丢弃（大纲保留）: %s | %s",
            len(coerced), len(dropped), coerced[:5], dropped[:5],
        )
    # BK.2 M3.2（2026-09-18·用户裁 B「一码一义」）：改字段与扔条目**分两个码**。此前一条 coerced 便条
    # 同时带 dropped= 计数，而它的人话说「清单和大纲都保住」—— 对被扔的条目不是真话。
    if coerced:
        note_degradation(
            "verify_checklist_item_coerced",
            f"coerced={len(coerced)}; coerced_samples={json.dumps(coerced[:5], ensure_ascii=False)}",
        )
    if dropped:
        _note_checklist_items_dropped("item_invalid", dropped)
    return kept


def _note_checklist_items_dropped(branch: str, samples: list[str]) -> None:
    """留一条「待查证清单条目被扔」（BK.2 M3.2）。两支：``prefilter``（没写事项 / 非 dict，
    在 :func:`_build_outline` 装配前过滤）与 ``item_invalid``（事项本身校验不过，在
    :func:`_sanitize_verify_checklist` 丢弃）。只加留痕，过滤 / 丢弃行为一字不改。"""
    note_degradation(
        "verify_checklist_item_dropped",
        f"branch={branch}; dropped={len(samples)}; "
        f"samples={json.dumps(samples[:_DROPPED_MAX_ITEMS], ensure_ascii=False)}",
    )


# 主 decision pass 三个 list 字段的合理长度区间。**不在 schema 层校验**——
# 主 pass 不走续写，单次 ValidationError 会让整 run 挂；故由 _enforce_list_bounds
# 做 warn + 截断。三个 tuple 的下界尊重 prompt 中 "3-5 / 2-4 / 可空" 的契约。
_LIST_BOUNDS: dict[str, tuple[int, int]] = {
    "core_risks": (3, 5),
    "trigger_events": (2, 4),
    "dissenting_views": (0, 5),
}


_DROPPED_MAX_ITEMS = 5      # 留痕里最多带几条被截条目
_DROPPED_MAX_CHARS = 80     # 每条最多带多少字


def _clip_dropped_item(item: Any) -> str:
    """被截条目 → 留痕用的短前缀。条目可能是 str 也可能是 dict（风险条目），统一压成一行。"""
    text = item if isinstance(item, str) else json.dumps(item, ensure_ascii=False, default=str)
    return text[:_DROPPED_MAX_CHARS]


def _enforce_list_bounds(data: dict, role_tag: str) -> None:
    """list 字段长度观测：太少 warn 不修；太多 warn + 截断。**不 raise**。

    设计意图：主 decision pass 是单次调用、无续写循环，一次 raise 会让整 run 挂。
    "太少"通常是模型省略了，再调一次也未必修复，故只 warn 保留信号；"太多"会破坏
    UI 渲染（信息过载），截断更稳妥。pop 之后 dict 是 in-place 改，调用方负责
    用同一个 dict 走 model_validate。
    """
    for fname, (lo, hi) in _LIST_BOUNDS.items():
        items = data.get(fname) or []
        if len(items) < lo:
            log.warning(
                "%s: %s 仅 %d 项（期望 ≥ %d）；保留原样",
                role_tag, fname, len(items), lo,
            )
        elif len(items) > hi:
            log.warning(
                "%s: %s 有 %d 项超上限 %d；截断为前 %d 项",
                role_tag, fname, len(items), hi, hi,
            )
            # BK.2 P0.5：截到 5 条与本来就 5 条在产物上一模一样 ⇒ 留痕，并把被截条目的
            # **原文前缀**存进留痕（用户 2026-09-17 裁 B）：只进执法记录、不进正文、不进提示词。
            # 封顶（每条 ≤80 字、最多 5 条）防归档被撑大。上下界与截断行为一个字不改。
            # 「太少」那支不发：什么都没丢，读者看到的就是模型给的（登记表 exempt）。
            dropped = [_clip_dropped_item(x) for x in items[hi:][:_DROPPED_MAX_ITEMS]]
            note_degradation(
                "decision_list_truncated",
                f"field={fname}; had={len(items)}; kept={hi}; dropped={json.dumps(dropped, ensure_ascii=False)}",
            )
            data[fname] = items[:hi]


# 主 decision pass 不再走续写循环（thesis_sections 由 section 扩写填充），
# 所以也不再需要 _DECISION_DELTA_KEYS——chunk 事件改走 thesis_section_chunk。
_SECTION_CHUNK_ALLOWED_KEYS = frozenset({"body"})


def _weighted_majority_direction(tally: dict | None) -> str | None:
    """从 tally 取加权多数方向（weighted 优先，回落 count）；无票→None。"""
    if not isinstance(tally, dict):
        return None
    weighted = tally.get("weighted") or {}
    if weighted:
        return max(weighted, key=lambda d: weighted[d])
    counts = {k: tally.get(k, 0) for k in ("BULLISH", "BEARISH", "NEUTRAL")}
    if any(counts.values()):
        return max(counts, key=lambda d: counts[d])
    return None


def _collect_dissent_checklist(
    debate_log: list,
    reports: list | None = None,
    votes: list | None = None,
    tally: dict | None = None,
    *,
    cap: int = 25,
) -> list[str]:
    """OBEY-2（A-2 注入 + Step3 核对）用：汇集需在决策中 address 的论点/质疑。

    B 覆盖面（spec R-10「覆盖面仅 bear-side」修复）——三来源，token 近似去重：
    - 跨角色质疑 cross_check_concerns（reports[].cross_check_concerns[].concern）
    - 辩论各轮 key_claims（**全 side**，不止 bear；含 R10-01 修复后的 closing）
    - 少数派投票理由（vote 方向 != 加权多数方向的 votes[].reasoning；pass0 路径
      votes 为空时无此来源——RoleVote 无 reasoning 字段）
    顺序=显式质疑→辩论→少数派；≥0.8 token 重叠视为同条丢弃；截断 cap。

    cap=25（R10-02 cap 残留修复，2026-06-24）：旧 cap=15 太小——cross_check_concerns
    在前、数量多时（D seg9 实测达 21）会占满 cap，把 R10-01 修的 closing key_claims
    + 少数派理由全挤出注入清单。25 容下实测 cross_check≥21 + closing + minority。
    残留边界（不在本轮修）：cross_check 若 ≥25 仍会挤出 → 彻底解需 closing/minority
    保底名额，按设计裁定 defer（见 plan group-b §3）。
    """
    items: list[str] = []
    seen: list[set] = []

    def _add(text) -> None:
        text = (text or "").strip()
        if not text:
            return
        toks = {t.lower() for t in re.findall(r"[\w一-鿿]{3,}", text)}
        if not toks:
            # 无 ≥3 字 token（极短串）→ 退回精确去重，不静默丢
            if text not in items:
                items.append(text)
            return
        for s in seen:
            if len(toks & s) / len(toks) >= 0.8:
                return
        seen.append(toks)
        items.append(text)

    for r in reports or []:
        for cc in (getattr(r, "cross_check_concerns", None) or []):
            _add(getattr(cc, "concern", None))
    for turn in debate_log or []:
        for claim in (getattr(turn, "key_claims", None) or []):
            _add(claim)
    majority = _weighted_majority_direction(tally)
    for v in votes or []:
        vdir = getattr(getattr(v, "vote", None), "value", None)
        if majority and vdir and vdir != majority:
            _add(getattr(v, "reasoning", None))

    return items[:cap]


def _uncovered_dissent(checklist: list[str], decision) -> list[str]:
    r"""OBEY-2 决策后核对（Step 3 检测告警）：checklist 中哪些 dissent 在决策**全文零提及**。

    addressed 池 = 决策全文 token：dissenting_views ∪ trigger_events ∪
    core_risks(risk+mitigation) ∪ thesis_sections.body。某条 checklist 与池**零 token
    重叠** → 未覆盖。crude token 启发式（与原 OBEY-2 同族 ``[\w一-鿿]{3,}``）——
    高精度低召回，只标"全文零提及"的强遗漏信号；**仅告警、不阻断、不改决策**。
    改进匹配精度属独立 scope（冷审 §4），此处不做。
    """
    def _toks(text):
        return {t.lower() for t in re.findall(r"[\w一-鿿]{3,}", text or "")}

    addressed: set[str] = set()
    for dv in (getattr(decision, "dissenting_views", None) or []):
        addressed |= _toks(dv)
    for te in (getattr(decision, "trigger_events", None) or []):
        addressed |= _toks(te)
    for cr in (getattr(decision, "core_risks", None) or []):
        addressed |= _toks(getattr(cr, "risk", ""))
        addressed |= _toks(getattr(cr, "mitigation", ""))
    for sec in (getattr(decision, "thesis_sections", None) or []):
        addressed |= _toks(getattr(sec, "body", ""))

    uncovered: list[str] = []
    for item in checklist:
        itoks = _toks(item)
        if itoks and not (itoks & addressed):
            uncovered.append(item)
    return uncovered


def make_decision_node(role_key: str = "fund_mgr") -> Callable[[CommitteeState], Any]:
    """Decision factory — fund_mgr 决策链路（MASK.B1 后：步骤6/7 长正文展开/审阅已移除）。

    opus = 2 次（outline / 决策+核心观点）；DeepSeek = 2 次（verify / scan）。
    核心不变量：成员资格(valid_fact_ids) ⊥ 可信度(confidence, code 派生)。
    """
    from committee.config import model_for_role
    meta = ROLES[role_key]

    async def node(state: CommitteeState) -> dict:
        from datetime import date as _date
        today = _date.today()

        # ---- LLM 实例化（tag 细分 → token_usage by_tag 可观测）----
        llm_outline = _llm(meta.model, temperature=TEMP_DECISION, tag="fund_mgr_outline")
        llm_decide = _llm(meta.model, temperature=TEMP_DECISION, tag="fund_mgr_decide", max_tokens=MAX_TOKENS_DECIDE)

        ds_verify_model = model_for_role("fund_mgr_verify", "deepseek-chat")

        llm_verify = _llm(ds_verify_model, temperature=0.3, tag="fund_mgr_verify")

        reports = collect_reports(state)
        reports_block = _format_reports(reports)
        votes = state.get("votes", [])

        pass0_result = state.get("pass0_result")

        if pass0_result and pass0_result.debate_summary:
            ds = pass0_result.debate_summary
            disagreements = "; ".join(ds.key_disagreements) if ds.key_disagreements else "（无）"
            debate_block = (
                f"多头核心论点: {ds.bull_core_thesis}\n"
                f"空头核心论点: {ds.bear_core_thesis}\n"
                f"辩论演进: {ds.progression_notes or '（无摘要）'}\n"
                f"关键分歧: {disagreements}"
            )
        else:
            debate_block = _format_debate(state.get("debate_log", []))

        if pass0_result and pass0_result.vote_distribution:
            vd = pass0_result.vote_distribution
            votes_block = "\n".join(
                f"- {rv.role}: {rv.direction} (conv={rv.conviction})"
                for rv in vd.per_role
            )
            tally: dict = {
                "BULLISH": vd.bullish_count,
                "BEARISH": vd.bearish_count,
                "NEUTRAL": vd.neutral_count,
                "total": vd.total_votes,
                "avg_conviction": vd.average_conviction,
                "weighted": {},
            }
            for rv in vd.per_role:
                tally["weighted"][rv.direction] = (
                    tally["weighted"].get(rv.direction, 0) + rv.conviction
                )
        else:
            votes_block = "\n".join(
                f"- {v.role}: {v.vote.value} (conv={v.conviction}) → {v.position_suggestion} — {v.reasoning}"
                for v in votes
            )
            tally = {"BULLISH": 0, "BEARISH": 0, "NEUTRAL": 0, "weighted": {}}
            for v in votes:
                tally[v.vote.value] += 1
                tally["weighted"][v.vote.value] = tally["weighted"].get(v.vote.value, 0) + v.conviction

        portfolio_block = render_portfolio_context(state.get("portfolio_context"))
        portfolio_section = (
            f"\n\n=== 用户组合上下文 ===\n{portfolio_block}" if portfolio_block else ""
        )

        facts_guidance = build_facts_guidance(pass0_result)

        # (OBEY signals — 不变)
        cc_total = 0
        cc_roles: list[str] = []
        for r in reports:
            n = len(r.cross_check_concerns)
            if n > 0:
                cc_total += n
                cc_roles.append(f"{r.role}({n})")
        cc_section = ""
        if cc_total > 0:
            cc_section = (
                f"\n\n=== 跨角色交叉质疑汇总 ===\n"
                f"共 {cc_total} 条 cross_check_concerns，涉及: {', '.join(cc_roles)}"
            )

        oos_roles = [r.role for r in reports if r.conviction == "DATA_INSUFFICIENT"]
        oos_section = ""
        if oos_roles:
            oos_section = (
                f"\n\n=== 数据不足角色 ===\n"
                f"以下 {len(oos_roles)} 个角色 conviction=DATA_INSUFFICIENT: "
                + ", ".join(oos_roles)
                # A5-R3（2026-07-22 用户澄清设计意图）：本提示仅对**多标的 / 板块查询**成立。
                # 单标的分析里 entry/stop_loss/take_profit 只有一组、不按角色领域切分，
                # 照字面读会被误解成"那就别给价位了" → 价位全灭 = 顶北极星（(b) 刚修好的病从后门复发）。
                # ∴ 此处与 DECISION_PROMPT R3 同步标注适用范围（两处必须一起改·只改一处会留半截旧措辞）。
                + "\n（这些角色覆盖的领域不应在 execution_plan 给出具体价位；"
                + "**仅适用于多标的 / 板块查询**——单标的分析价位只有一组、"
                + "不按领域切分，不得据此清空该标的的价位）"
            )

        weighted = tally.get("weighted", {})
        vote_leader = ""
        if weighted:
            top_dir = max(weighted, key=lambda d: weighted[d])
            top_val = weighted[top_dir]
            vote_leader = (
                f"\n\n=== 投票第一名 ===\n"
                f"加权票数最高: {top_dir} ({top_val})"
            )

        today_str = today.isoformat()
        time_anchor = f"\n\n=== 时间锚点 ===\n今天日期: {today_str}。所有时间判断以此为基准。"

        # CRED.1.G2 复审修（2026-09-09）：影子对账（G1-shadow）是给**用户**看的观测条目，
        # 不进决策提示词——否则 R6 会逼决策者把它写进 core_risks / 据此降信心，试用期采到的
        # "本该拦"样本就来自一个已被影子改过的决策（观测器污染被观测对象）。
        pre_findings = llm_facing_findings(state.get("risk_gate_pre_findings", []))
        pre_gate_section = ""
        if pre_findings:
            pf_lines = [f"- {f.finding_id} [{f.gate}/{f.severity}]: {f.message}" for f in pre_findings]
            pre_gate_section = (
                f"\n\n=== 风险闸门预检 ===\n"
                f"以下 {len(pre_findings)} 条 finding 在你做决策前已触发，请在决策中充分考量:\n"
                + "\n".join(pf_lines)
            )

        user_base = (
            f"主题: {state['query']}\n\n"
            f"=== 分析师报告 ===\n{reports_block}\n\n"
            f"=== 辩论记录 ===\n{debate_block}\n\n"
            f"=== 投票明细 ===\n{votes_block}\n\n"
            f"=== 票数汇总 ===\n{json.dumps(tally, ensure_ascii=False)}"
            f"{cc_section}"
            f"{oos_section}"
            f"{vote_leader}"
            f"{time_anchor}"
            f"{pre_gate_section}"
            f"{portfolio_section}"
            f"{facts_guidance}"
        )

        # ==== 步骤 2a: code 构建查证清单 ====
        code_checklist = _build_verify_checklist(pass0_result, today)

        # ==== 步骤 2b: outline + opus 增补查证清单（opus #1）====
        outline = await asyncio.to_thread(
            _build_outline, llm_outline, user_base + "\n\n请先列出决策骨架。", reports
        )
        outline_specs: list[SectionSpec] = list(outline.thesis_outline)
        emit_event({
            "type": "decision_outline",
            "outline": [{"id": s.id, "title": s.title} for s in outline_specs],
        })

        opus_checklist = [
            vi.model_dump() for vi in outline.verify_checklist
        ]
        merged_checklist = _merge_checklists(code_checklist, opus_checklist)
        log.info(
            "fund_mgr: verify_checklist code=%d opus=%d merged=%d (high=%d)",
            len(code_checklist), len(opus_checklist), len(merged_checklist),
            sum(1 for c in merged_checklist if c.get("criticality") == "high"),
        )

        # ==== 步骤 3: DeepSeek 联网查证 ====
        findings, verify_tool_outputs, verify_notices = await _run_verification(
            llm_verify, merged_checklist, state["query"]
        )
        log.info("fund_mgr: verification produced %d findings", len(findings))

        # ==== 步骤 3″: 外源册固化（信源册建册·M1·T1）====
        # 两源第一次同时在手的最早时刻（web_provenance + 刚产出的 verify_tool_outputs）→
        # 单点固化成 external_websearch 外源册、存进 state。**只加写路、不换读**：下方步骤 3'
        # 仍临时现派生 → T1 天然 verdict-neutral（写了新字段但此刻没人读）。T2 才把 3' 换成读它。
        # 副产物：fund_mgr verify_tool_outputs 从此不再用完即扔（满足五锚-3）。零 LLM/零网络。
        from committee.facts.verify import build_external_websearch_ledger
        external_websearch_ledger = build_external_websearch_ledger(
            state.get("web_provenance"), verify_tool_outputs
        )

        # ==== 步骤 3': confidence 终裁（纯 code）====
        # AO: 透传 analyst web_provenance（唯一显式接点；中间 11 节点经 state+reducer
        # 自动穿过、不需改）。给非 audit_passed DS-0 事实数 web 域名印证。
        findings, confidence_map = _derive_all_confidence(
            findings, pass0_result, today, verify_tool_outputs,
            web_provenance=state.get("web_provenance"),
            external_websearch_ledger=external_websearch_ledger,  # T2：透传 T1 步骤 3″ 固化的册
            # CRED.2.G3（BP）：表① 出处，用来判 audit_passed 事实所引出处是否过期
            references=getattr(state.get("common_context"), "references", None),
        )

        # ==== 步骤 3'' 层② check① 证据搬运对账（P2b.2 接线）====
        # 对每条 DS-0 fact 跑对账（fact 主数字 ↔ 其引 W# 编号在外源册登记值·数量级比），命中
        # 盖 fact 级 `EVIDENCE_TRANSCRIPTION_FLAG` 戳（清洗+按需盖·幂等·防 LLM 预填/续跑重复）。
        # 手边有册 → 这里读表②、产 fact 戳；**安全闸之后只读 fact 戳、物理不碰表②**（守 #5 封顶版：
        # 表②派生信号只降不升——本戳只会 → 切价位/HOLD）。in-place 改 pass0_result.facts_inventory·
        # 同对象经 state 流到闸门（execution_stage_hard_block 读 pass0_result.facts_inventory）。
        # CRED.1.G4（用户裁 D4-b·2026-09-10）：机械判 transcription 之后叫**异模型复核员**
        # （`mismatch_review.review_evidence_mismatch`·只看 fact + 出处·不看本节点任何推理）；
        # 复核判误报 → 盖 disputed 戳（闸门不切·计划打存疑标），否则仍盖 transcription 戳。
        # 每条判定（含复核结论 + 三元组）记 enforcement_log 供审计；quality_flags / enforcement_log
        # 都不进 LLM 提示词（坑表 2026-09-10：观测产物不得改变被观测对象输入）。
        # ⚠️ **必须 to_thread**（PR #286 review 第 3 条）：复核是同步 LLM 调用，单条最坏
        # TIMEOUT×ATTEMPTS 秒；本节点是 async，直接同步调会卡死事件循环 —— 期间连保活心跳
        # 都发不出去、前端断流。本节点其它 LLM 调用（outline / head）也都走 to_thread。
        # 对账函数本身是纯同步、in-place 改 facts_inventory，整体卸到线程即可。
        check1_audit: list[dict] = []
        if pass0_result and pass0_result.facts_inventory:
            from committee.facts.exec_floor import apply_evidence_transcription_flags
            from committee.facts.mismatch_review import review_evidence_mismatch
            _et_n = await asyncio.to_thread(
                apply_evidence_transcription_flags,
                pass0_result.facts_inventory, external_websearch_ledger,
                reviewer=review_evidence_mismatch, audit=check1_audit,
            )
            if _et_n:
                log.info("层② check① 对账：%d 条 fact 命中证据搬运数量级错、盖戳", _et_n)

        # valid_fact_ids = DS-0 全部 fact_id ∪ verification id
        valid_fact_ids: set[str] = set(
            item.fact_id
            for item in (pass0_result.facts_inventory if pass0_result else [])
        )
        valid_fact_ids.update(f.id for f in findings)
        valid_fact_ids_frozen = frozenset(valid_fact_ids)

        # ==== 步骤 4: opus 决策 + 核心观点 body（opus #2）====
        findings_block = _format_findings_for_prompt(findings)
        outline_block = "\n".join(f"- {s.id}: {s.title}" for s in outline_specs)
        # OBEY-2（A-2+B，R10-02 修复）：把反方论点/质疑在决策【前】显式注入，确保决策
        # pass 看见、逐条 address。原实现在决策【后】才追加进 user_base→仅达扩写层=死代码。
        # B 覆盖面：辩论全 side + 跨角色质疑 + 少数派投票（见 _collect_dissent_checklist）。
        dissent_checklist = _collect_dissent_checklist(
            state.get("debate_log", []), reports, votes, tally,
        )
        dissent_block = ""
        if dissent_checklist:
            dissent_block = (
                "=== 须 address 的反方论点/质疑（OBEY-2）===\n"
                "以下汇集自辩论、跨角色质疑、少数派投票，请对与你决策方向相左的逐条 address"
                "（在 dissenting_views 驳斥／纳入 trigger_events／据此降级 decision）:\n"
                + "\n".join(f"- {c}" for c in dissent_checklist)
                + "\n\n"
            )
        head_user = (
            f"{user_base}"
            f"{findings_block}\n\n"
            f"【已确定的 thesis 骨架】\n{outline_block}\n\n"
            f"{dissent_block}"
            f"请做最终决策：决策头部 + 每段核心观点。"
        )

        try:
            head_data = await asyncio.to_thread(
                _invoke_json, llm_decide, DECISION_PROMPT, head_user
            )
        except (ValueError, json.JSONDecodeError) as e:
            log.error("decision_head_parse_error role=%s: %s", role_key, e)
            raise

        if "thesis" in head_data:
            log.warning("fund_mgr: 主 decision pass 输出 thesis 字段（已 drop）")
            head_data.pop("thesis", None)

        _enforce_list_bounds(head_data, role_tag="fund_mgr")

        # （OBEY-2 dissent 注入已上移到决策【前】= A-2，R10-02 修复；决策后追加进
        #   user_base→仅达扩写的死代码已删。决策后的覆盖核对/告警见后续 Step 3。）

        # 装配 head_data → decision（thesis_sections 带 opus 核心观点 body）
        head_data["vote_summary"] = tally
        head_data.pop("continuation", None)
        head_data.pop("chunk_index", None)

        from committee.schemas.decision import normalize_decision
        _raw_decision = head_data.get("decision")
        _norm_decision = normalize_decision(_raw_decision)
        if not (isinstance(_raw_decision, str) and _raw_decision.strip().upper() == _norm_decision):
            log.warning("fund_mgr: decision %r normalized to %s", _raw_decision, _norm_decision)
            emit_event({
                "type": "decision_normalized",
                "raw": _raw_decision if isinstance(_raw_decision, str) else str(_raw_decision),
                "normalized": _norm_decision,
            })

        # thesis_sections 从 head_data 解析（opus 产核心观点 body）；schema_version=2
        raw_sections = head_data.get("thesis_sections", [])
        sections: list[ThesisSection] = []
        for i, spec in enumerate(outline_specs):
            sec_data = None
            if isinstance(raw_sections, list):
                for rs in raw_sections:
                    if isinstance(rs, dict) and rs.get("id") == spec.id:
                        sec_data = rs
                        break
                if sec_data is None and i < len(raw_sections) and isinstance(raw_sections[i], dict):
                    sec_data = raw_sections[i]

            body = ""
            if sec_data:
                body = str(sec_data.get("body", "") or "")
            if not body:
                body = f"（{spec.title}：核心观点待补充）"
                log.warning("fund_mgr: section %s body empty, placeholder inserted", spec.id)

            sections.append(ThesisSection(
                id=spec.id,
                title=spec.title,
                body=body,
                schema_version=2,
            ))

        head_data["thesis_sections"] = [s.model_dump() for s in sections]
        head_data["references_appendix"] = []
        decision = FinalDecision.model_validate(head_data)

        # OBEY-2 Step3（检测告警，不阻断/不改决策）：决策后核对注入的 dissent 哪些在
        # 决策全文零提及 → 写 enforcement_log + log.warning，供人工注意 + 攒频率（决定
        # 是否上 A-1 自动重决，留 S3/S4）。注入(A-2)在决策【前】，此处仅观测、不重决。
        obey2_entries: list[dict] = []
        _uncovered = _uncovered_dissent(dissent_checklist, decision)
        if _uncovered:
            obey2_entries.append({
                "rule": "OBEY-2-dissent-coverage",
                "action": "flag",
                "detail": (
                    f"{len(_uncovered)} 条注入的反方论点/质疑在决策全文零提及"
                    f"（dissenting_views/trigger_events/core_risks/thesis 均无 token 重叠）；"
                    f"crude 启发式、仅告警、未改决策"
                ),
                "uncovered": _uncovered[:8],
            })
            log.warning(
                "fund_mgr: OBEY-2 %d 条 dissent 决策全文零提及（已告警、未自动重决）: %s",
                len(_uncovered), _uncovered[:8],
            )

        # ==== 步骤 5/5'（Path B·MASK.C2/C3·2026-07-15）: 确定性验章门 + 价位门控 ====
        # 旧步骤5（DeepSeek 全文扫描 _scan_claims·搜章）已删——opus 生成侧带标（C1），
        # 门做一对一验章（judge-by-code·零 LLM·恒执行·无"扫描失败"降级路）。
        # prose_gate_status 仍由步骤 8 _derive_prose_gate_status 机械派生（gate 恒执行
        # → degraded 只剩"价位全抹"来源）。
        # ★ DEFECT-PROSE-GATE-SELF-ABRADE：在门控**前**（position_size/价位仍是决策者原值）
        # 收集决策者自定行动数字，供 5' 验章门豁免（不打码决策者自定的仓位/价位/触发数字）。
        # 豁免集 = 决策者自定行动数字（处方）∪ 委员会自产流程数字（投票/信心分/质疑计数）。
        # 后者 D-3 空跑坐实：不加会误涂"投票 33 vs 14""confidence 5"等如实转述的过程数字。
        # CRED.1.G2 复审修：影子 finding 的 message 里是对账计数 + 表①编号（`REF#W-003` 会被
        # 数字正则切成 -3），既不是委员会流程数字也不该进豁免集 → 过滤掉。
        prescribed_numbers = _decision_prescribed_numbers(decision) | _committee_structural_numbers(
            decision,
            llm_facing_findings(
                (state.get("risk_gate_findings") or []) + (state.get("risk_gate_pre_findings") or [])
            ),
        )
        decision, claim_audits, gate_enforcement = _apply_stamp_gate(
            decision, findings, confidence_map, pass0_result,
            state.get("common_context"), prescribed_numbers,
        )
        scan_succeeded = True  # 验章纯代码恒执行（DeepSeek scan 失败路已随 C3 删）

        # ==== G5（MASK.GATE-B·2026-07-16）: AI 誊写核查 —— **只降级** ====
        # 挂在确定性门**之后**：门核「引用存不存在」，本 pass 核「来源真这么说吗」。
        # 结构上只能收紧门的产出（mismatch→涂 / unclear→只记 / match→零动作）。
        # 🔴 绝不提档（R5-01 红线·详见 _apply_ai_transcription_check docstring 上方）。
        # kill-switch COMMITTEE_TRANSCRIPTION_CHECK=off 一键退回纯确定性门。
        decision, tc_enforcement = _apply_ai_transcription_check(
            decision, claim_audits, findings, pass0_result, state.get("common_context"),
        )
        gate_enforcement = list(gate_enforcement) + tc_enforcement
        evid1_entries: list[dict] = []
        evid1_entries.extend(gate_enforcement)

        # EVID-1（第二层兜底·墙的不变量承接）：C1 后 opus 生成侧带标——幻觉标已在验章门
        # （_apply_stamp_gate tier=halluc）剥掉+涂；本段扫剩余正文标提取 external_knowledge_refs，
        # 并兜"验章门漏剥"的越界 ref（双层防御·fm-spec B3：hallucinated ref 不许活到读者）。
        cited_ids: set[str] = set()
        hallucinated_refs: list[str] = []
        for sec in decision.thesis_sections:
            for m in _VER_REF_PATTERN.finditer(sec.body):
                rid = m.group(1)
                if rid in valid_fact_ids_frozen:
                    cited_ids.add(rid)
                else:
                    hallucinated_refs.append(rid)
            for m in _REF_PATTERN.finditer(sec.body):
                fid = m.group(1)
                if fid in valid_fact_ids_frozen:
                    cited_ids.add(fid)
                else:
                    hallucinated_refs.append(fid)

        if hallucinated_refs:
            for sec in decision.thesis_sections:
                new_body = _VER_REF_PATTERN.sub(
                    lambda m: "" if m.group(1) not in valid_fact_ids_frozen else m.group(0),
                    sec.body,
                )
                new_body = _REF_PATTERN.sub(
                    lambda m: "" if m.group(1) not in valid_fact_ids_frozen else m.group(0),
                    new_body,
                )
                if new_body != sec.body:
                    new_body = re.sub(r"[ \t]{2,}", " ", new_body)
                    sec.body = re.sub(r"\s+([,，。.;；、）)])", r"\1", new_body)
            uniq_hall = sorted(set(hallucinated_refs))
            log.warning("fund_mgr: stripped hallucinated refs %s", uniq_hall)
            evid1_entries.append({
                "rule": "EVID-1",
                "action": "strip",
                "detail": f"hallucinated refs stripped: {uniq_hall}",
                "refs": uniq_hall,
            })

        # 验章过的引用并入（MASK.C2）：v# 标验后即剥（前端不认 v#·正文标已不在），
        # 但引用事实成立——从验章 audits 收 matched_finding：green/yellow（数字验过）
        # + qualit（定性引用·numeric_value=None·标剥句在）；red（值不对·数字已涂）与
        # halluc（matched_finding 已置 None）不算引用。v#/f# 引用不从
        # external_knowledge_refs 消失（quality gate REF 计数 + 可追溯性）。
        # B3 不变量仍守：rid 必在合法域（验章已核存在性 + 此处再滤一遍）。
        cited_ids.update(
            a.matched_finding for a in claim_audits
            if a.matched_finding and a.matched_finding in valid_fact_ids_frozen
            and (a.numeric_match or a.numeric_value is None)
        )

        decision.external_knowledge_refs = sorted(cited_ids)

        # ==== 步骤 6/7 已移除（MASK.B1·2026-07-15）====
        # 旧步骤6（DeepSeek 长正文展开 _expand_section_ds）+ 步骤7（opus strip-only 审阅
        # _review_expansions）已砍：body_expanded 长文实测 0.99–1.06×不增内容、前端从不渲染
        # （只读 body·frontend ThesisSection 无 body_expanded 字段），且是 DEFECT-PROSE-MASK-ESCAPE
        # 的逃逸面来源。thesis section 交付物 = 步骤4 opus 核心观点 body（已过步5' 打码门）。

        # ==== 步骤 7.5: 外部数据章 [W#…] 翻译成人看引用 [来源N]（T11·麻烦一 c）====
        # 正文已定稿（步骤 5' 打码后）、外源册在手 → 把内部流水号翻译成来源脚注。
        decision.web_citations = _translate_web_markers_to_citations(
            decision, external_websearch_ledger,
        )

        # ==== 步骤 8: 装配 FinalDecision ====
        decision.references_appendix = _build_references_appendix(
            findings, confidence_map, pass0_result,
            external_websearch_ledger, today=today,
            # CRED.2.G4（BS）：表① 引用，DS-0 事实行据此继承身份
            references=getattr(state.get("common_context"), "references", None),
        )

        # 机械派生（不独立默认 verified）：scan 跑过 + 价位未被 (b) 地板抹光 → verified，否则 degraded。
        # spec R-3 / A3 全抹自检——价位 level/confidence 已由步骤 5' 门控落定，此处据实推导。
        decision.prose_gate_status = _derive_prose_gate_status(decision, scan_succeeded)
        if decision.prose_gate_status == "degraded" and scan_succeeded:
            log.warning(
                "fund_mgr: 价位 level 全被抹（ungrounded run·<%d verified）→ prose_gate_status=degraded",
                _GROUNDING_MIN_VERIFIED,
            )
        decision.claim_audits = claim_audits

        if decision.references_appendix:
            from committee.facts.verify import render_appendix_zh
            emit_event({
                "type": "references_appendix",
                "entries": [e.model_dump() for e in decision.references_appendix],
                "rendered_zh": render_appendix_zh(decision.references_appendix),
            })

        # OBEY-5/6/7: validators (unchanged)
        from committee.validators.obedience import check_vote_override, check_mitigation_execution, check_time_horizon_stale
        decision, obey5_entries = check_vote_override(decision, tally)
        obey6_entries = check_mitigation_execution(decision)
        obey7_entries = check_time_horizon_stale(decision)

        result: dict = {"final_decision": decision}
        # T1（信源册建册·M1）：外源册随决策一起落进 state（plain 字段·单写者 fund_mgr）。
        result["external_websearch_ledger"] = external_websearch_ledger
        # verify_notices（BK.2 提前批 #36）：决策前事实核验没做成时的那条痕。
        # 不并进就等于「交出空清单 = 没发现问题」继续骗人 —— 汇总据此派生。
        enforcement = (obey5_entries + obey6_entries + obey7_entries + evid1_entries
                       + obey2_entries + check1_audit + verify_notices)
        if enforcement:
            result["enforcement_log"] = enforcement
        return result

    node.__name__ = "fund_manager_decide"
    return node
