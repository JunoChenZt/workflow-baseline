"""Phase 1 — analyst system prompts assembly.

Combines role-specific prompts (from analyst/role_prompts/) with the shared
output schema (common_output) to produce the final SYSTEM_PROMPTS dict.

全 8 role 已升级到 7-段 prompt（以 analyst/role_prompts/ 子模块为
single source of truth）。
"""

from .role_prompts.macro import SYSTEM_PROMPT as _MACRO_PROMPT
from .role_prompts.sentiment import SYSTEM_PROMPT as _SENTIMENT_PROMPT
from .role_prompts.commodity import SYSTEM_PROMPT as _COMMODITY_PROMPT
from .role_prompts.historian import SYSTEM_PROMPT as _HISTORIAN_PROMPT
from .role_prompts.technical import SYSTEM_PROMPT as _TECHNICAL_PROMPT
from .role_prompts.fundamentals import SYSTEM_PROMPT as _FUNDAMENTALS_PROMPT
from .role_prompts.economist import SYSTEM_PROMPT as _ECONOMIST_PROMPT
from .role_prompts.political import SYSTEM_PROMPT as _POLITICAL_PROMPT

from .common_output import COMMON_OUTPUT as _COMMON_OUTPUT

SYSTEM_PROMPTS: dict[str, str] = {
    "macro": f"{_MACRO_PROMPT}\n{_COMMON_OUTPUT}",
    "sentiment": f"{_SENTIMENT_PROMPT}\n{_COMMON_OUTPUT}",
    "technical": f"{_TECHNICAL_PROMPT}\n{_COMMON_OUTPUT}",
    "fundamentals": f"{_FUNDAMENTALS_PROMPT}\n{_COMMON_OUTPUT}",
    "commodity": f"{_COMMODITY_PROMPT}\n{_COMMON_OUTPUT}",
    "historian": f"{_HISTORIAN_PROMPT}\n{_COMMON_OUTPUT}",
    "political": f"{_POLITICAL_PROMPT}\n{_COMMON_OUTPUT}",
    "economist": f"{_ECONOMIST_PROMPT}\n{_COMMON_OUTPUT}",
}
