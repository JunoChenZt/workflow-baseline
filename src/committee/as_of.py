"""as_of 一等公民 helper（PR-12d-1 / S2 #11）。

设计意图：
- as_of 字段在多个 schema 出现（EvidenceItem / MarginalCost / 未来扩展）；
  本模块统一格式（ISO 8601 日期）+ 解析 + staleness 计算。
- 向后兼容：空字符串 ""（legacy default）或 None 视为"未提供"，不抛错。
- 严格格式：``YYYY-MM-DD``（不接受 datetime / 时区 / RFC 3339）——
  分析报告通常以"日"为粒度的 as_of，更细粒度（如 intraday quote 的精确
  timestamp）属另一类型字段（``observed_at`` 等），不复用 as_of。
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Annotated

from pydantic import BeforeValidator, StringConstraints


# ISO 8601 日期正则（YYYY-MM-DD）。允许空字符串（向后兼容）。
_AS_OF_DATE_PATTERN = r"^(\d{4}-\d{2}-\d{2})?$"
_AS_OF_DATE_RE = re.compile(_AS_OF_DATE_PATTERN)

# Coarse-precision shapes that we normalize up to YYYY-MM-DD before the
# StringConstraints pattern runs. LLM evidence citations often provide
# month / quarter / year precision; schema stores normalized ISO date
# strings for downstream consistency.
_YEAR_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
_YEAR_ONLY_RE = re.compile(r"^\d{4}$")
_YEAR_QUARTER_RE = re.compile(r"^(\d{4})-Q([1-4])$")
_YEAR_HALF_RE = re.compile(r"^(\d{4})-H([1-2])$")

# No-data sentinels（whitelist；case-insensitive）。
# 严格白名单：仅这些字符串（或这些字符串后跟分隔符 + 解释）归一化为空串。
# 其他任何输入（包括 DATA_INSUFFICIENT、TBD、自然语言日期 "around 2024" /
# "Q4 2024" / "as of latest filing"）继续 fail-fast，让异常显性暴露。
_NO_DATA_SENTINELS = (
    "not available", "no data", "no date", "not disclosed",  # 多词放前
    "unknown", "none", "null", "n/a", "na",
)
_NO_DATA_SEPARATORS = (" ", "\t", ":", "-", "—")

_QUARTER_TO_MONTH = {"1": "01", "2": "04", "3": "07", "4": "10"}
_HALF_TO_MONTH = {"1": "01", "2": "07"}


def _is_no_data_sentinel(v_lower: str) -> bool:
    """精确命中 sentinel 或 sentinel + 分隔符 + 解释 → 视为无数据。"""
    for s in _NO_DATA_SENTINELS:
        if v_lower == s:
            return True
        if v_lower.startswith(s):
            rest = v_lower[len(s):]
            if rest and rest[0] in _NO_DATA_SEPARATORS:
                return True
    return False


def _normalize_as_of(v):
    """Normalize coarse precision / no-data sentinels into ISO 8601 before pattern check.

    - YYYY-MM-DD              → unchanged
    - YYYY-MM                 → YYYY-MM-01
    - YYYY                    → YYYY-01-01
    - YYYY-Q[1-4]             → YYYY-{first month of quarter}-01
    - YYYY-H[1-2]             → YYYY-{01 or 07}-01
    - "" / None               → unchanged (optional / legacy default)
    - sentinel (whitelist) + 可选分隔符 + 解释 → "" (no-data)
    - other                   → unchanged (downstream pattern check rejects)

    ⚠️ **英文日期写法一概不认** —— ``Dec 19, 2025`` / ``25 Feb 2026`` / ``Feb 2026``
    全部落到最后一档 "other → unchanged"，随后被 ``_AS_OF_DATE_PATTERN`` 拒掉；
    走 :func:`sanitize_as_of` 的调用方因此拿到空串（2026-07-31 拿 Serper 真实返回值实测，
    三种写法全灭 —— **连绝对日期都不认**，不是精度问题）。

    **今天没出事，是因为有人在上游替我们转了**：外部搜索走 Cloudflare Worker，日期在
    **进本仓之前**就已归一成 ISO（2026-07-31 Serper 切换时选的方案 A）。归一能力因此
    落在**某一个上游的转发层**，不在主链路。

    ⇒ **接第二个会吐英文日期的上游时，补在这里**，别在每个上游各转一遍。

    〔原 backlog 条目 **BD**，2026-09-08 close-by-decision —— 关之前先把这段知识挪进代码，
    否则关掉等于扔掉。**本注即真值源**，不必再去 backlog 找活条目。〕
    """
    if v is None or v == "":
        return v
    if not isinstance(v, str):
        return v
    if _is_no_data_sentinel(v.strip().lower()):
        return ""
    if _YEAR_MONTH_RE.fullmatch(v):
        return f"{v}-01"
    if _YEAR_ONLY_RE.fullmatch(v):
        return f"{v}-01-01"
    m = _YEAR_QUARTER_RE.fullmatch(v)
    if m:
        year, q = m.group(1), m.group(2)
        return f"{year}-{_QUARTER_TO_MONTH[q]}-01"
    m = _YEAR_HALF_RE.fullmatch(v)
    if m:
        year, h = m.group(1), m.group(2)
        return f"{year}-{_HALF_TO_MONTH[h]}-01"
    return v


# Pydantic 字段 type alias：限制 as_of 格式。空字符串合法（legacy）。
# 用法：``as_of: AsOfDate = ""``
AsOfDate = Annotated[
    str,
    BeforeValidator(_normalize_as_of),
    StringConstraints(pattern=_AS_OF_DATE_PATTERN),
]


def sanitize_as_of(v) -> str:
    """Salvage path: coerce an as_of value to a strict-valid string, or "".

    与严格 ``AsOfDate`` 类型互补：``AsOfDate`` 对无法解析的输入**故意 fail-fast**
    （设计意图，见模块 docstring + ``_NO_DATA_SENTINELS`` 注释）。本 helper 是
    **抢救路径**——跑同一套 ``_normalize_as_of`` 归一化，若结果仍不是合法
    ``YYYY-MM-DD``（或空串）则返回 ``""``（无日期）而非抛错。

    用途（AO）：``AnalysisReport`` sanitizer 用它兜底 ``evidence_log[].as_of`` /
    ``marginal_cost.as_of``——某条证据的 as_of 写坏（如 ``"DATA_INSUFFICIENT"`` /
    ``"Q4 2024"`` / ``"2026/06/05"``）时只丢这个日期，而不让整份报告降级 fallback。

    None / 非字符串 → ``""``。**不改变严格 ``AsOfDate`` 路径**。
    """
    if v is None:
        return ""
    normalized = _normalize_as_of(v)
    if isinstance(normalized, str) and _AS_OF_DATE_RE.fullmatch(normalized):
        return normalized
    return ""


def parse_as_of(s: str | None) -> date | None:
    """Parse as_of string → date | None (None = 未提供 / 无效)。

    严格 YYYY-MM-DD；其他格式（""、None、"unknown"、"2026/04/30" 等）返回 None。
    上层据此决定显示 "as of —" 或具体日期。
    """
    if not s:
        return None
    if not _AS_OF_DATE_RE.fullmatch(s):
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def staleness_days(as_of: str | None, *, today: date | None = None) -> int | None:
    """How many days old is this data as of `today` (default real today)?

    Args:
        as_of: ISO 8601 date string; "" / None / invalid → returns None
        today: 默认 datetime.now().date()；测试可注入

    Returns:
        非负整数（0 = 今天）；as_of 是未来日期返回负数（异常 case 上层处理）；
        as_of 无效返回 None。
    """
    parsed = parse_as_of(as_of)
    if parsed is None:
        return None
    ref = today if today is not None else datetime.now().date()
    return (ref - parsed).days
