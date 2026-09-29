"""Config — model routing and role metadata."""
from __future__ import annotations
import logging
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# ⚠️ Runs at import time (before load_dotenv). Claude Code injects empty
# ANTHROPIC_API_KEY="" into child processes; load_dotenv(override=False) sees
# the key as "set" and won't overwrite with the .env value. We pop empties so
# load_dotenv picks up the real keys from .env. Side-effect: any test that
# mocks an API key to "" before importing config will have that mock popped.
for _k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"):
    if os.getenv(_k) == "":
        os.environ.pop(_k)
load_dotenv()

log = logging.getLogger("committee.config")


class ConfigValueError(ValueError):
    """env 里写了一个**认不出的值**（不是没写）—— 起步就停，不悄悄退默认。

    backlog BJ.5 (b)/(c)·用户 2026-09-14 裁：此前「非法值 → warn + 回退默认」（#210 起沿用的契约，
    理由只是「否则整包导不进」）。而"整包导不进"正是要的效果：填错字是拼写错误，静默退默认是本仓最不该有的
    那种失效（配置写了却没生效、还没人知道）。**没写 / 空串仍走默认**；**超范围仍夹回**（保守方向，坑表明说别一刀切）。
    查来源层用 `committee config explain <KEY>`。
    """


_TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})
_FALSE_TOKENS = frozenset({"0", "false", "no", "off"})

ANALYST_MODEL = os.getenv("COMMITTEE_ANALYST_MODEL", "claude-haiku-4-5-20251001")
DEBATE_MODEL = os.getenv("COMMITTEE_DEBATE_MODEL", "claude-sonnet-4-6")
DECISION_MODEL = os.getenv("COMMITTEE_DECISION_MODEL", "claude-sonnet-4-6")


def _clamp_int(name: str, default: int, lo: int, hi: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        v = int(raw)
    except ValueError:
        raise ConfigValueError(
            f"{name}={raw!r} 不是整数（合法范围 {lo}~{hi}，缺省 {default}）—— 起步已停；"
            f"改正 env 或删掉这一项；查它从哪层来：committee config explain {name}"
        ) from None
    return max(lo, min(v, hi))


def _clamp_float(name: str, default: float, lo: float, hi: float) -> float:
    """float 版 ``_clamp_int`` —— 同一套失败语义（填错字 → :class:`ConfigValueError` 起步停；空 → 默认）。

    与 ``_clamp_int`` 的区别只有类型；**上下限同样是「防误填」兜底**，但对 timeout
    类配置，``hi`` 是**真上界**（超过即夹回）——防 env 把预算类天花板悄悄顶穿。
    """
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        v = float(raw)
    except ValueError:
        raise ConfigValueError(
            f"{name}={raw!r} 不是数（合法范围 {lo}~{hi}，缺省 {default}）—— 起步已停；"
            f"改正 env 或删掉这一项；查它从哪层来：committee config explain {name}"
        ) from None
    return max(lo, min(v, hi))


def _env_bool(name: str, default: bool) -> bool:
    """开关型 env 的**唯一**读法（backlog BJ.5 (c)·用户 2026-09-14 裁）。

    封闭集合：``1/true/yes/on`` 开 · ``0/false/no/off`` 关 · 没写/空 → ``default`` ·
    **其余一律** :class:`ConfigValueError`（起步停）。此前各开关各写一套：默认关的用白名单
    （写 ``enabled`` 会悄悄关）、默认开的用黑名单（写 ``disable`` 会悄悄开）—— 两种写法各漏一头，
    G1 冷审 findings 5 只把默认开的那几处换成黑名单。现在不猜：认不出就报错，值该写什么在错误里。
    """
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    if raw in _TRUE_TOKENS:
        return True
    if raw in _FALSE_TOKENS:
        return False
    hint = "开" if default else "关"
    raise ConfigValueError(
        f"{name}={raw!r} 不是开关值（开：1/true/yes/on · 关：0/false/no/off；缺省 {hint}）"
        f"—— 起步已停；查它从哪层来：committee config explain {name}"
    )


# 字符数（Python len(str)）目标，非 token。0 表示关闭本机制。
#
# 上下限是「防误填」兜底，不是 supported operating range。推荐区间在第 4 个参数注明。
# 跑出推荐区间会同时放大调用次数 × prompt 体积（续写每轮回灌已合并内容），
# 单次 analyze 的 LLM 调用数和 token 消耗都会显著膨胀；调参前请确认成本可接受。
MIN_CHARS_ANALYST = _clamp_int("COMMITTEE_MIN_CHARS_ANALYST", 500, 0, 20000)    # 推荐 300-1000
MIN_CHARS_DEBATE = _clamp_int("COMMITTEE_MIN_CHARS_DEBATE", 1500, 0, 20000)     # 推荐 1000-2500
# DEPRECATED in PR 3：主 decision pass 已不再产 thesis，此变量仅为兼容老 .env 保留。
# 未来 PR 5+ 清理；删除会破坏老部署的 env 解析（虽然只 warn 不挂），故缓行。
MIN_CHARS_DECISION = _clamp_int("COMMITTEE_MIN_CHARS_DECISION", 1500, 0, 20000) # DEPRECATED
# 注：MIN_CHARS_SECTION（旧步骤6 长正文展开的字符目标）已随 step6/7 一并移除
# （MASK.B1·2026-07-15）；env COMMITTEE_MIN_CHARS_SECTION 若仍设置将被忽略（无害）。
MAX_CONTINUATIONS = _clamp_int("COMMITTEE_MAX_CONTINUATIONS", 3, 0, 10)         # 推荐 2-4；>5 会显著膨胀成本

# LLM 单次调用输出上限（token 数，所有 provider / role 共用）。
#
# PR-8b 上线 fundamentals 7 段 prompt 后，单次 analyst 调用输出体量显著上升，
# 历史默认 4096 容易首包被掐断 → `_extract_json` 因缺尾 `}` 直接 ValueError，
# 且 `_invoke_with_continuation` 首包失败时续写循环根本不会启动（参 base.py 注释）。
# 此变量允许生产侧调高（推荐 8192），同时给上下限兜底防误填。
#
# 推荐区间 4096-16384。> 16384 多数模型不支持或显著放大单调用成本；
# < 1024 几乎必触发任何 role 截断。下限 256 仅为防 0/负数让所有调用失败。
MAX_TOKENS = _clamp_int("COMMITTEE_MAX_TOKENS", 4096, 256, 32768)               # 推荐 4096-16384
# fund_mgr 决策 pass（opus #2）独立上限：决策头 + N 段核心观点 ≤1000 字，
# 但 JSON 结构化 overhead + 个别超长段需要余量。默认 8192（spec 要求），
# 用 COMMITTEE_MAX_TOKENS_DECIDE env 覆盖。
MAX_TOKENS_DECIDE = _clamp_int("COMMITTEE_MAX_TOKENS_DECIDE", 8192, 2048, 32768)
# Academic/advisory 角色（political / historian / economist·tier=="advisory"）独立上限：
# 这三个角色带「结构化承重字段先于 raw」抗截断硬规则（见各 role_prompt），但截断根
# 治不了只靠字段顺序——deepseek 不遵守 raw-last（backlog AM）、生产 gemini-2.5-pro 的
# thinking token 吃掉 ~68% 预算（2026-06-05 political-arms 实验）。给足预算 = 从根上
# 不截断，字段顺序对不对都无所谓。默认 12288 覆盖 gemini thinking overhead 最坏情况
# （需 ~4000 可见 / 0.32 ≈ 12500）；max_tokens 是上限、按实际用量计费，用不到不花。
# make_analyst_node 用 max(MAX_TOKENS, MAX_TOKENS_ACADEMIC) 做下限语义（全局调更高则跟随）。
MAX_TOKENS_ACADEMIC = _clamp_int("COMMITTEE_MAX_TOKENS_ACADEMIC", 12288, 4096, 32768)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# OpenAI-compatible 聚合（云雾 yunwu.ai、OneAPI 等）：base 一般为 https://host/v1
OPENAI_COMPAT_BASE_URL = os.getenv("OPENAI_COMPAT_BASE_URL") or os.getenv("OPENAI_BASE_URL")
# 非 compat 路的 OpenAI 网关与 DeepSeek 网关（此前 agents/base.py 构造 LLM 时各自再读一遍 env ——
# BJ.5 (e) 归并到这里：同一个键全仓只读一处，`committee config explain` 才答得出它的来源层）。
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").strip()
OPENAI_COMPAT_API_KEY = os.getenv("OPENAI_COMPAT_API_KEY") or os.getenv("OPENAI_API_KEY")

FORCE_OPENAI_COMPAT = _env_bool("COMMITTEE_FORCE_OPENAI_COMPAT", False)

# AG.2 —— 给 Anthropic 的 system prompt 打可缓存标记（prompt 文本零改动）。
#
# **默认关**，理由是成本方向在单次孤立 run 里是负的：
#   Anthropic 的缓存写入按基础输入价 ×1.25 计费、读取 ×0.1。而 fund_mgr 的两次调用
#   各用一份不同的开头指令（DECISION_OUTLINE_PROMPT / DECISION_PROMPT），前缀在第一段
#   就断，彼此吃不到对方的缓存 → 单次孤立 run 只写不读 = 净亏约 $0.02。
#   真正会赚的场景：① JSON 解析失败的同参重试；② 5 分钟有效期内连续跑多次分析
#   （批量回归 / 段式续跑重放决策段）。
#
# 实测收益（2026-08-11 AG.1 探针·docs/observations/ag-cache-meter-probe/EVIDENCE.md）：
#   命中时单次成本 $0.0835 → $0.0093（降 89%）；不打标记则恒不命中。
#
# 打开：环境变量置 1 / true / yes / on。开关只影响 Anthropic 一路，
# deepseek（自动前缀缓存，白捡）与 gemini（无标记可打）完全不受影响。
PROMPT_CACHE_ENABLED = _env_bool("COMMITTEE_PROMPT_CACHE", False)

# 低于最小可缓存长度时 Anthropic **静默忽略**标记（不报错）—— 所以「没报错」不等于
# 「缓存生效」，唯一判据是返回里的 cache_creation / cache_read。
#
# 门槛按**词元**算（claude-opus-4-7 = 2,048 token，官方文档 2026-08-11 核），
# 这里用**字符数**做粗筛 —— 两者的换算比随内容形态浮动，实测差一个数量级
# （count_tokens API，claude-opus-4-7，2026-08-12 实测，非估算）：
#
#   本仓真实 prompt（中英混排 + markdown）  0.65–0.76 词元/字符
#   纯中文散文                              ~1.07
#   生僻字                                  ~2.65
#   纯英文                                  ~0.35
#
# 所以这道粗筛**两个方向都可能判错，但都不影响正确性**：
#   · 放得太松（本仓的常见情形）—— 按 0.76 算，2,048 字符才约 1,560 词元，
#     2,048~2,700 字符这段会被放行、然后被 API 静默忽略标记，行为与不打标记完全相同；
#   · 收得太紧（本仓当前不会发生）—— 纯中文散文约 1.07，1,914 字符就够 2,048 词元，
#     那段会被本闸拦掉、少省一次钱。只影响账单，不影响输出。
#
# 门槛值保持 2048 不动：本仓唯一够格的那份开头指令（fund_mgr 定稿用）是
# 7,236 字符 / 5,513 词元，离门槛很远，换算比再怎么浮动都不会翻到界外。
PROMPT_CACHE_MIN_CHARS = 2048


def model_for_role(role_key: str, tier_fallback: str) -> str:
    """Per-role override: COMMITTEE_MODEL_<ROLE_KEY_UPPER>, e.g. COMMITTEE_MODEL_MACRO."""
    env_name = f"COMMITTEE_MODEL_{role_key.upper()}"
    return os.getenv(env_name, tier_fallback)


# Phase 0a Step 0.0 Query Classifier model routing (A6.1.1).
#
# **不进 ROLES dict** —— B.1#1 锁定 ``tier`` 语义为"投票资格 + UI 分组"，
# query_class 是 Phase 0a 基础设施（非 voter / 非 advisor / 非 debater），
# 不应混入 ``ROLES`` 表。仅用 ``model_for_role`` 走 env 路由：
# ``COMMITTEE_MODEL_QUERY_CLASS`` 可覆盖；缺省回退 ``ANALYST_MODEL``
# （轻量 tier；原「≤ 3s runtime 预算」口径已随 2026-07-24 classify 超时上调放宽，见
# ``query_class/classifier.py`` LLM_TIMEOUT_SECONDS 论证块）。
QUERY_CLASS_MODEL = model_for_role("query_class", "deepseek-v4-pro")

# QC-R1 G3 ticker 解析专职模型路由。
# classify 判定 ticker_specific 但未提取到代码时，额外调一次专职 LLM 做
# name→code 解析（任务窄、prompt 短）。默认 ``deepseek-chat``（用户拍板"deepseek 即可"——
# 解析公司名→代码不需要重模型）。``COMMITTEE_MODEL_TICKER_RESOLVER`` 可覆盖。
TICKER_RESOLVER_MODEL = model_for_role("ticker_resolver", "deepseek-chat")

# seg1 G5 retrieval_planner（取数规划员）模型路由。
# 照 QUERY_CLASS_MODEL 先例：Phase 0a 基础设施（非 voter / 非 advisor /
# 非 debater），不进 ROLES 表，仅走 env 路由。``COMMITTEE_MODEL_RETRIEVAL_PLANNER``
# 可覆盖；缺省与 classify 同档（要读长 prompt + 按五源分格出计划，
# 比 ticker 解析重、与 classify 的推理量同量级）。
RETRIEVAL_PLANNER_MODEL = model_for_role("retrieval_planner", "deepseek-v4-pro")


def _temp_env(stage: str, default: float) -> float:
    """Stage-level temperature with `COMMITTEE_TEMPERATURE_<STAGE>` env override.

    填错字 → :class:`ConfigValueError` 起步停（与 _clamp_int 一致的失败语义·BJ.5 (b)）；空 → 默认。
    """
    name = f"COMMITTEE_TEMPERATURE_{stage.upper()}"
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        raise ConfigValueError(
            f"{name}={raw!r} 不是数（缺省 {default}）—— 起步已停；查它从哪层来：committee config explain {name}"
        ) from None


# Stage-level temperatures（消除 base.py 旧魔法数 0.4/0.6/0.3/0.3）。
# 设计原则：temperature 是 stage 属性而非 role 属性——同 stage 不同 role 共享，
# 不引入 per-role 化（B.3 不动列表，canonical spec 已退役，见 git history）。
TEMP_ANALYST = _temp_env("analyst", 0.4)
TEMP_DEBATE = _temp_env("debate", 0.6)
TEMP_VOTE = _temp_env("vote", 0.3)
TEMP_DECISION = _temp_env("decision", 0.3)


@dataclass(frozen=True)
class RoleMeta:
    """Role 元数据。

    `tier` 字段语义（B.1#1 锁定）：**投票资格 + UI 分组**，**不是行为路由**。
    具体来说：
    - tier 决定 role 是否进 `RESEARCH_ROLES`（Phase 1 调研循环）/ `VOTING_ROLES`
      （Phase 3 投票循环）/ debate 池。
    - tier **不**决定调用工厂（`make_analyst_node` / `make_debate_node` /
      `make_vote_node` / `make_decision_node`）—— 工厂选择由 `graph.py` 显式装配，
      不由 tier 派生。
    - 不引入 `FACTORY_BY_TIER` dispatcher（B.3#15 锁定）。

    合法值：``"research"`` / ``"advisory"`` / ``"debate"`` / ``"decision"``
    （PR-5 加性 schema 后扩 ``"fundamentals"``）。
    """

    key: str
    name_en: str
    name_zh: str
    tier: str
    model: str


ROLES: dict[str, RoleMeta] = {
    "macro":      RoleMeta("macro", "Macro Analyst", "宏观分析师", "research", model_for_role("macro", ANALYST_MODEL)),
    "sentiment":  RoleMeta("sentiment", "Sentiment Analyst", "情绪分析师", "research", model_for_role("sentiment", ANALYST_MODEL)),
    "technical":  RoleMeta("technical", "Technical Analyst", "技术分析师", "research", model_for_role("technical", ANALYST_MODEL)),
    # fundamentals 在 PR-8b 激活——tier="research" 使其自动进 RESEARCH_ROLES / VOTING_ROLES
    # 顺序：technical → fundamentals → commodity（与 REPORT_KEYS / SYSTEM_PROMPTS 统一）
    "fundamentals": RoleMeta("fundamentals", "Fundamental Analyst", "基本面分析师", "research", model_for_role("fundamentals", ANALYST_MODEL)),
    "commodity":  RoleMeta("commodity", "Commodity Trader", "商品交易员", "research", model_for_role("commodity", ANALYST_MODEL)),
    # political 代码默认 = deepseek-v4-pro（2026-06-09 四臂选型实验定，见
    # docs/observations/experiments/political-arms/decision-review.md）：gemini-2.5-pro
    # 的 thinking token 吃掉 ~68% 输出预算致截断；deepseek 同质量、~1/5 成本、不截断。
    # COMMITTEE_MODEL_POLITICAL 仍可覆盖；代码默认即正确事实源，.env 缺失也跑 deepseek。
    "political":  RoleMeta("political", "Political Scientist", "政治学教授", "advisory", model_for_role("political", "deepseek-v4-pro")),
    "historian":  RoleMeta("historian", "Historian", "历史学教授", "advisory", model_for_role("historian", ANALYST_MODEL)),
    "economist":  RoleMeta("economist", "Economist", "经济学教授", "advisory", model_for_role("economist", ANALYST_MODEL)),
    "bull":       RoleMeta("bull", "Bull Researcher", "多头研究员", "debate", model_for_role("bull", DEBATE_MODEL)),
    "bear":       RoleMeta("bear", "Bear Researcher", "空头研究员", "debate", model_for_role("bear", DEBATE_MODEL)),
    "fund_mgr":   RoleMeta("fund_mgr", "Fund Manager", "基金经理", "decision", model_for_role("fund_mgr", DECISION_MODEL)),
}

# tier 白名单：单一真值来源（B.1#2 锁定）。新增 role 自动获得对应资格；新增 tier
# 强制做决策（不写进白名单默认不获权，安全方向）。fundamentals PR-8b 已激活，
# tier="research" 无需改白名单，自动进 RESEARCH_ROLES / VOTING_ROLES。
RESEARCH_ROLES = [k for k, v in ROLES.items() if v.tier in ("research", "advisory")]
VOTING_ROLES = [k for k, v in ROLES.items() if v.tier in ("research", "advisory", "debate")]
DEBATE_ROUNDS = 3

# Per-role tool-agent whitelist. Comma-separated role keys; empty = all off.
# Roles in this set run through the tool-use agent loop (run_tool_agent) and can
# call data-source tools + web_search; roles outside it use single-shot _invoke_json.
# Provider-agnostic: tools work via OpenAI function calling (yunwu.ai oc/*, DeepSeek,
# Anthropic, Google all support bind_tools).
#
# ⚠️ COST WARNING: The tool loop may issue extra LLM round-trips + external search
# calls. Default: all 8 researchers + fund_mgr. Set to empty string to disable all.
_WS_ALL_ROLES = "macro,sentiment,technical,fundamentals,commodity,political,historian,economist,fund_mgr"
_ws_raw = os.getenv("COMMITTEE_WEB_SEARCH_ROLES", _WS_ALL_ROLES).strip()
WEB_SEARCH_ROLES: frozenset[str] = frozenset(
    r.strip() for r in _ws_raw.split(",") if r.strip()
)

# External web search proxy (Cloudflare Workers / SearXNG-compatible).
# GET {EXTERNAL_SEARCH_URL}?q=<query>&engines=<engines> ->
#   {query, number_of_results, results: [{title, description, url, engine}]}
# EXTERNAL_SEARCH_TOKEN (optional) -> sent as Authorization: Bearer <token>.
# httpx respects system proxy env (HTTP_PROXY/HTTPS_PROXY) — *.workers.dev needs a
# proxy from mainland China; set the proxy env, do not hardcode it here.
EXTERNAL_SEARCH_URL = os.getenv(
    "COMMITTEE_EXTERNAL_SEARCH_URL",
    "https://cloudflare-search.junochenzt.workers.dev/search",
).strip()
EXTERNAL_SEARCH_TOKEN = os.getenv("COMMITTEE_EXTERNAL_SEARCH_TOKEN", "").strip()
# Default engine set queried via the Cloudflare search proxy.
#
# ⚠️ TWO DIMENSIONS, both must be measured: **non-empty** (did anything come
# back) and **relevant** (is what came back about the query). Green on the first
# does NOT imply green on the second — that blind spot is what produced the
# 2026-07-30 regression below.
#
# 2026-07-29 measurement — NON-EMPTY rate only (N=10 per engine, 5 queries x 2):
#   bing 10/10 · duckduckgo 3/10 solo · brave 0/10 · brave,ddg 2/10 · bing,ddg 10/10
#   → default was switched to `bing,duckduckgo` on that evidence.
#
# 2026-07-30 re-measurement — RELEVANCE, same day, A/B off one e2e checkpoint:
#   bing,ddg   69 calls → 12 useful / **24 garbage** (35% garbage, 17% useful)
#   brave,ddg  73 calls → 11 useful / **0 garbage**  ( 0% garbage, 15% useful)
#   → bing's marginal contribution = **+1 useful, +24 garbage** → reverted here.
# Garbage = HTTP 200 + 10 results + zero error log + content totally unrelated
# (French consumer magazine / Crimea Wikipedia / Korean gov petition site for
# "Nvidia Q2 earnings"). bing serves SEO-poisoned results to SearXNG-style
# scrapers; SearXNG cannot tell and forwards them verbatim. Failure is query-
# specific and deterministic → **retrying does not help**. Evidence:
# docs/observations/regression-e2e-20260730/SEARCH-ENGINE-REGRESSION.md
#
# ⚠️ `brave` is dead (0/10 non-empty) — this default is therefore effectively
# **duckduckgo solo**; brave is kept in the string so a revival is picked up
# automatically and so the failure stays visible. brave fails by returning
# HTTP 200 with ZERO results — there is **no error to grep for**. Do NOT go
# looking for timeouts: the 2026-07-02 removal cited a different symptom
# (hanging past the local 8s `_TOOL_TIMEOUT` into an empty httpx ReadTimeout);
# **that mode no longer reproduces** — brave now answers in ~1.5s median, empty.
#
# The real fix is a different search backend (Cloudflare side, user action) —
# 15–17% useful means four out of five searches are wasted either way. Until
# then WEB_SEARCH_RELEVANCE_CHECK below is the engine-agnostic backstop.
#
# Override per run via COMMITTEE_EXTERNAL_SEARCH_ENGINES. Engine availability
# drifts (brave's failure mode, duckduckgo's solo rate and bing's result quality
# all changed between 2026-07-02 and 07-30) → **re-measure BOTH dimensions
# before trusting these numbers**.
EXTERNAL_SEARCH_ENGINES = os.getenv("COMMITTEE_EXTERNAL_SEARCH_ENGINES", "brave,duckduckgo").strip()
# Cap results fed back to the LLM (keep token cost bounded).
EXTERNAL_SEARCH_MAX_RESULTS = _clamp_int("COMMITTEE_EXTERNAL_SEARCH_MAX_RESULTS", 5, 1, 20)

# DEFECT-WEBSEARCH-RELEVANCE（2026-07-30）：结果集相关性守卫 kill-switch。
# ON（默认）→ `_exec_web_search` 在把结果喂回 LLM 前做一次零成本词汇重叠判定：
# 整个结果集与 query **零重叠** → 当失败处理、返 {"error": ...}，让分析师走
# DATA_INSUFFICIENT 诚实路径，而不是把 SEO 垃圾当资料读。
# **与选哪个引擎无关**——引擎可用性一直在漂（07-02 / 07-29 / 07-30 三次结论各不同），
# 这道检查是常设兜底：上游怎么变垃圾都进不到分析师手里。
# 设 0/false/no/off → 一键回旧行为（结果原样喂回·零判定）。
WEB_SEARCH_RELEVANCE_CHECK = _env_bool("COMMITTEE_WEB_SEARCH_RELEVANCE_CHECK", True)

# T11（信源册 M1·数字级外源册）：web_search 结果喂回 LLM 前的数字级盖章 kill-switch。
# ON（默认）→ 结果摘要里每个数字旁注入 [W#role-batch-rIdx#nK] 编号 + 生成 number_registry
# 登记（raw result 原文不动·见 tools/number_stamp.py 两路分离铁律）。
# 设 0/false/no/off → 一键回旧行为（原文喂回·零登记）。
WEB_NUMBER_STAMPING = _env_bool("COMMITTEE_WEB_NUMBER_STAMPING", True)

# G5（MASK.GATE-B·2026-07-16 用户拍）：AI 誊写核查 kill-switch。
# ON（默认）→ 确定性验章门**之后**加一道 AI pass：对每个挂 {ref} 标的数字核「它声称的
# 来源真这么说吗」。**只降级**：mismatch→打码 / unclear→只记日志 / match→**零动作**。
# 🔴 红线：AI 判定**绝不用于提档**（标 verified / 去 caveat / 改 confidence）——那是
# DEFECT-R5-01 的失败模式（门零判别力·寄生 LLM 老实度·被伪造来源骗过）。降级安全
# （AI 误报只会多涂=可读性代价·永远无法让坏数字变可信）；升级危险 → code 里不给这条路。
# 设 0/false/no/off → 一键关（退回纯确定性门 = 本 flag 引入前的行为）。
TRANSCRIPTION_CHECK = _env_bool("COMMITTEE_TRANSCRIPTION_CHECK", True)
# 誊写核查模型：要读研报自由文本做数值比对 = 精度活。默认 gemini-2.5-pro（用户 2026-07-16 拍）——
# 弱模型（deepseek-v4-flash）本轮 e2e 出过空壳报告（非确定性），精度活风险高；误报会重新
# 引入过度打码（正是 GATE-B 刚治好的病）。真实误报率由 G4 e2e 量·高则退 log-only。
TRANSCRIPTION_CHECK_MODEL = os.getenv("COMMITTEE_MODEL_TRANSCRIPTION_CHECK", "gemini-2.5-pro")
# ★ 给足输出预算（镜像 MAX_TOKENS_ACADEMIC 先例·backlog AM 同族坑）。
# **G4 e2e 实证（2026-07-16）**：默认 MAX_TOKENS=4096 时 gemini-2.5-pro 的 **thinking token
# 把预算吃光 → 可见输出为空**（实测该次调用吐满 4,093 token、content=''）→ _extract_json
# 抛 "No JSON object in LLM output" → G5 整个 fail-open 跳过（安全但白跑）。
# 12288 覆盖 thinking overhead 最坏情况（需 ~4000 可见 / 0.32 ≈ 12500）；max_tokens 是
# **上限**、按实际用量计费，用不到不花。
TRANSCRIPTION_CHECK_MAX_TOKENS = _clamp_int(
    "COMMITTEE_MAX_TOKENS_TRANSCRIPTION_CHECK", 12288, 4096, 32768,
)

# CRED.1.G4（用户裁 D4-b·2026-09-10）：check① 异模型复核员 kill-switch。
# ON（默认）→ EXEC-FLOOR check① 机械判「证据搬运错」之后，叫一个**不同 provider 家族**的模型
# 看一眼是不是误报；判 false_positive → 撤硬拦（计划保留·打「存疑」标）；unsure / true_error /
# 失败 → 维持硬拦。🔴 这是用户显式裁定的「只降不升」红线例外，成立前提焊在
# `committee.facts.mismatch_review`（独立性 / 输入隔离 / 输出封闭）。设 0/false/no/off → 关
# （= 纯机械 check①·本 flag 引入前的行为）。
EVIDENCE_MISMATCH_REVIEW = _env_bool("COMMITTEE_EVIDENCE_MISMATCH_REVIEW", True)
# 复核模型：必须与**产出该 fact 的那些角色的 per-role 实配**不同 provider 家族
# （`mismatch_review.producer_models_for_fact`：pass0 + cited_by_roles 的实配 + fund_mgr 实配；
# 不知道谁写的就把全部非决策角色算进来）。默认 gemini-2.5-pro（G5 誊写核查同款·精度活先例）。
# ⚠️ 判据**不是**这几个 tier 兜底常量（ANALYST_MODEL / DECISION_MODEL）——本机 .env 里
# `COMMITTEE_MODEL_BEAR=gemini-2.5-pro` 就是未注释实配，拿兜底常量比会漏判同族自审
# （PR #286 review 第 1 条）。不独立时复核员自动缺席（代码守·不靠自觉）。
EVIDENCE_MISMATCH_REVIEW_MODEL = model_for_role("evidence_mismatch_review", "gemini-2.5-pro")
# 输出预算：镜像 TRANSCRIPTION_CHECK_MAX_TOKENS（gemini thinking token 吃预算的坑·同上注）。
EVIDENCE_MISMATCH_REVIEW_MAX_TOKENS = _clamp_int(
    "COMMITTEE_MAX_TOKENS_EVIDENCE_MISMATCH_REVIEW", 12288, 4096, 32768,
)
# 单次尝试超时（秒）。最坏耗时 ≈ TIMEOUT × ATTEMPTS。
EVIDENCE_MISMATCH_REVIEW_TIMEOUT = _clamp_float("COMMITTEE_EVIDENCE_MISMATCH_REVIEW_TIMEOUT", 30.0, 1.0, 600.0)
# 🔴 **`attempts` 是「总尝试次数」不是「重试次数」**（PR #286 review 第 3 条·核到
# langchain-google-genai 源码：`retry_options = HttpRetryOptions(attempts=max_retries)`）。
# 传 1 = 只试一次、网络抖一下就直接维持硬拦（复核形同虚设）；故默认 **2**（= 一次重试），
# 与 TIMEOUT=30 配成最坏 60 秒。坑表第 11 条：要「这一步最多花 N 秒」的硬保证，
# 必须同时钉死超时**和**尝试次数，只设 timeout 拿到的是 timeout × attempts。
EVIDENCE_MISMATCH_REVIEW_ATTEMPTS = _clamp_int(
    "COMMITTEE_EVIDENCE_MISMATCH_REVIEW_ATTEMPTS", 2, 1, 5,
)

# Tool-use agent loop budgets — two cost axes, throttled separately:
#   - max_iterations = LLM round-trips (token cost + latency). **Primary throttle.**
#     Tools within one round run concurrently (asyncio.gather), so a low round cap
#     does NOT prevent thorough search — the model batches multiple queries per round.
#   - web_search max calls = search-API cost. **Backstop only**, kept generous.
# Analysts: tight (2 rounds) — prompt guides "outline first, batch-search round 1,
# then finalize". fund_mgr: looser (4 rounds) — final synthesis may re-verify a thesis.
WEB_SEARCH_MAX_ITERATIONS = _clamp_int("COMMITTEE_WEB_SEARCH_MAX_ITERATIONS", 2, 1, 10)
WEB_SEARCH_MAX_CALLS = _clamp_int("COMMITTEE_WEB_SEARCH_MAX_CALLS", 5, 0, 50)
DECISION_WEB_SEARCH_MAX_ITERATIONS = _clamp_int("COMMITTEE_DECISION_WEB_SEARCH_MAX_ITERATIONS", 4, 1, 10)
DECISION_WEB_SEARCH_MAX_CALLS = _clamp_int("COMMITTEE_DECISION_WEB_SEARCH_MAX_CALLS", 8, 0, 50)

# ticker-confirm G1: web_search-backed ticker resolution（公司名→代码）的预算。
# 收得很紧——解析是窄查证、非深研。**与 classify 主调用的 socket 超时（`LLM_TIMEOUT_SECONDS`·
# 默认 15s·2026-07-24 由 2.5s 上调）是两回事**：搜索走 run_tool_agent（_resolve_tickers），
# 不在 classify 主路径上，不占主调用的超时预算。
# 仅在"判定 ticker_specific 但主调用没认出代码"或交互编辑重搜时触发。
TICKER_RESOLVER_WEB_SEARCH_MAX_ITERATIONS = _clamp_int("COMMITTEE_TICKER_RESOLVER_WEB_SEARCH_MAX_ITERATIONS", 2, 1, 5)
TICKER_RESOLVER_WEB_SEARCH_MAX_CALLS = _clamp_int("COMMITTEE_TICKER_RESOLVER_WEB_SEARCH_MAX_CALLS", 2, 0, 10)


# ---- seg1 G1：取数计划的两个开关 -------------------------------------------
#
# ⚠️ **刻意写成函数、不写成 import 期常量**（坑表第 12 条「断言配置常量前先证本机
# 配置没罩住它」）：模块级常量在 import 那一刻就冻住，测试里 `monkeypatch.setenv`
# 之后**不会重新求值** —— 于是"改了环境变量、断言仍是旧值"的测试会**因为错误的
# 原因变绿**。读取时求值让开关在进程内真的可切，变异验证才做得动。
#
# 两个开关**语义不同，别合并**：
#   RECORD —— 要不要把本次实际取数动作如实记成一份计划（默认开·纯记账）
#   REPLAY —— 手上已有一份计划时，是否原样沿用而不重新记（默认关）


def retrieval_plan_record_enabled() -> bool:
    """要不要记录本次取数动作（seg1 G1 记录器）。**默认开**。

    纯记账：它不改任何源的选择、参数、时序或降级链 —— 关掉它，系统行为与
    2026-08-21 之前**逐字节一致**（有反向测试钉住这条）。

    ⚠️ **默认开的开关用「黑名单」写法**（2026-08-21 冷审 findings 5）：
    只有 ``0/false/no/off`` 才关，其余一律开 —— 对齐本仓另外三处默认开的
    kill-switch（``WEB_SEARCH_RELEVANCE_CHECK`` / ``WEB_NUMBER_STAMPING`` /
    ``TRANSCRIPTION_CHECK``）。读法 = :func:`_env_bool` 封闭集合（BJ.5 (c)·2026-09-14）：此前白名单写法
    会把 ``enabled`` / ``y`` 这类**本意是开**的值悄悄关掉、归档从此不带计划一声不吭；现在这类值
    直接起步报错，不再猜。
    """
    return _env_bool("COMMITTEE_RETRIEVAL_PLAN_RECORD", True)


def retrieval_planner_enabled() -> bool:
    """要不要让取数规划员决定查什么（seg1 G5.4 换大脑）。**默认开**。

    关掉 = 退回今天的按标签路由（`_route`），行为与 2026-08-25 之前一致 ——
    它是这次换大脑的 **kill-switch**：真出问题时不必回滚代码，关掉即可。

    读法 = :func:`_env_bool` 封闭集合（BJ.5 (c)·2026-09-14）—— 取代 G1 冷审 findings 5 的「黑名单写法」：
    那种写法防住了 ``enabled`` 被当成关，却会把 ``disable`` 当成开；现在两头都不猜，认不出就报错。
    """
    return _env_bool("COMMITTEE_RETRIEVAL_PLANNER", True)


def retrieval_plan_replay_enabled() -> bool:
    """回放模式：手上已有计划时原样沿用、不重新记。**默认关**。

    ⚠️ **G1 阶段回放只保住"计划这份记录"，不驱动取数** —— 大脑还没换，
    取数仍按今天的路子走。等 G5 接线后，回放才会真的决定去查什么。
    现在就留这个开关，是为了让"两种模式都要留"这条设计要求在地基阶段就成立
    （只回放会让规划质量退化时没人发现）。
    """
    return _env_bool("COMMITTEE_RETRIEVAL_PLAN_REPLAY", False)
