"""Web search tool-use 集成测试（Cloudflare proxy + run_tool_agent）。

覆盖：
1. _exec_web_search — 成功路径 / HTTP 失败 / 未配置 URL（mock httpx，避真实网络）
2. run_tool_agent — 无 tool_call 直接出 JSON / tool-call loop / bind_tools fallback
3. make_analyst_node（async）— 白名单内走 run_tool_agent / 白名单外走 _invoke_json /
   扩写路径不走 tool agent（成本保护）
4. config — WEB_SEARCH_ROLES 解析 + EXTERNAL_SEARCH_* 默认值

asyncio.run() inline 包裹（不依赖 pytest-asyncio，与 tests/test_common_context_* 一致）。
"""
from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _run(coro):
    """asyncio.run() inline 包裹 — 不依赖 pytest-asyncio。"""
    return asyncio.run(coro)


# ---- 1. _exec_web_search -----------------------------------------------------


def _mock_async_client(get_return=None, get_side_effect=None):
    """构造一个可作 `async with httpx.AsyncClient(...)` 用的 mock。"""
    client = MagicMock()
    if get_side_effect is not None:
        client.get = AsyncMock(side_effect=get_side_effect)
    else:
        client.get = AsyncMock(return_value=get_return)
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=client)
    cm.__aexit__ = AsyncMock(return_value=False)
    return MagicMock(return_value=cm)


def test_exec_web_search_success_trims_results(monkeypatch):
    from committee.tools import definitions

    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_URL", "https://example/search")
    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_MAX_RESULTS", 2)

    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value={
        "query": "AAPL",
        "number_of_results": 3,
        # 标题带 query 词 = 通过相关性守卫（守卫本身另有专测）
        "results": [
            {"title": "AAPL t1", "description": "d1", "url": "u1", "engine": "brave"},
            {"title": "AAPL t2", "description": "d2", "url": "u2", "engine": "ddg"},
            {"title": "AAPL t3", "description": "d3", "url": "u3", "engine": "brave"},
        ],
    })

    with patch("httpx.AsyncClient", _mock_async_client(get_return=resp)):
        out = _run(definitions._exec_web_search("AAPL"))

    data = json.loads(out)
    assert data["query"] == "AAPL"
    assert data["number_of_results"] == 2  # capped at MAX_RESULTS
    assert [r["title"] for r in data["results"]] == ["AAPL t1", "AAPL t2"]
    # engine field dropped from LLM-facing payload
    assert "engine" not in data["results"][0]


def test_exec_web_search_includes_publication_date(monkeypatch):
    """AD.4: web_search 结果带 publication_date（多 key 兼容；缺失为空串）。"""
    from committee.tools import definitions

    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_URL", "https://example/search")
    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_MAX_RESULTS", 5)

    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value={
        "results": [
            {"title": "AAPL t1", "url": "u1", "publishedDate": "2026-05-30"},
            {"title": "AAPL t2", "url": "u2"},  # 无日期
        ],
    })
    with patch("httpx.AsyncClient", _mock_async_client(get_return=resp)):
        out = _run(definitions._exec_web_search("AAPL"))
    data = json.loads(out)
    assert data["results"][0]["publication_date"] == "2026-05-30"
    assert data["results"][1]["publication_date"] == ""


def test_exec_web_search_http_error_returns_error(monkeypatch):
    import httpx

    from committee.tools import definitions

    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_URL", "https://example/search")

    with patch("httpx.AsyncClient", _mock_async_client(get_side_effect=httpx.ConnectError("boom"))):
        out = _run(definitions._exec_web_search("AAPL"))

    data = json.loads(out)
    assert "error" in data
    assert "boom" in data["error"]


# ---- 1a. 空消息异常不得产生空 error（2026-07-31 Serper 切换实测）--------------
#
# httpx 超时类异常 str(e) == ""，旧码 `{"error": str(e)}` + `log.warning("...: %s", e)`
# 会得到空 error 字段 + 日志行 "tool web_search failed: " 后面什么都没有 ——
# 故障原因被自己的日志吃掉。seg2 实跑 4 次撞上，靠人肉复现才定位。


@pytest.mark.parametrize(
    "exc",
    [
        __import__("httpx").ConnectTimeout(""),
        __import__("httpx").ReadTimeout(""),
        __import__("httpx").ReadError(""),
    ],
    ids=["ConnectTimeout", "ReadTimeout", "ReadError"],
)
def test_exec_web_search_empty_message_exception_still_reports_type(monkeypatch, caplog, exc):
    """空消息异常：喂回模型的 error 和日志都必须带异常类型名，不得为空。"""
    from committee.tools import definitions

    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_URL", "https://example/search")

    # 前提自证：这些异常的 str() 确实是空的（否则本测试测了个寂寞）
    assert str(exc) == ""

    with caplog.at_level("WARNING", logger="committee.tools"):
        with patch("httpx.AsyncClient", _mock_async_client(get_side_effect=exc)):
            out = _run(definitions._exec_web_search("AAPL"))

    data = json.loads(out)
    assert data["error"], "error 字段不得为空 —— agent 无从判断该不该重试"
    assert type(exc).__name__ in data["error"]

    logged = " ".join(r.getMessage() for r in caplog.records)
    assert type(exc).__name__ in logged, "日志必须带类型名，否则故障原因不可见"


def _worker_upstream_timeout_s() -> float:
    """从 Worker 源码读出它的上游超时（秒）——不许两边各写一个数字。

    这个不变式的另一端在 JS 里，写死字面量的话，Worker 一改超时、这条测试
    照样绿，而客户端会重新掉到它下面（= 本次修的 bug 原样复活）。
    """
    import re
    from pathlib import Path

    js = Path(__file__).resolve().parent.parent / "docs" / "plans" / "worker-search-serper.js"
    assert js.is_file(), f"读不到 Worker 源码：{js} —— 文件挪走了？"
    m = re.search(r"UPSTREAM_TIMEOUT_MS\s*=\s*(\d+)", js.read_text(encoding="utf-8"))
    assert m, f"{js} 里找不到 UPSTREAM_TIMEOUT_MS —— 常量改名了？（改名 = 这条测试失去意义，必须跟着改）"
    return int(m.group(1)) / 1000.0


def test_exec_web_search_timeout_is_wider_than_worker_upstream():
    """web_search 用自己那条更宽的线，且必须**高于** Worker 的上游超时。

    客户端若比 Worker 短，就永远收不到 Worker 那个带上游状态码的结构化 502，
    只能收到一个空的 httpx 超时 —— 等于把诊断信息挡在门外。

    Worker 侧的值**从源码现读**（docs/plans/worker-search-serper.js 的
    UPSTREAM_TIMEOUT_MS），不写死在这里 —— 否则守不住漂移的那一侧。
    ⚠️ 收窄不等于闭合：真正的权威是**已部署的** Worker，仓库里这份只是副本；
    改了线上没改文件，本测试仍然绿。
    """
    from committee.tools import definitions

    worker_s = _worker_upstream_timeout_s()
    assert definitions._WEB_SEARCH_TIMEOUT > worker_s, (
        f"客户端 {definitions._WEB_SEARCH_TIMEOUT}s 必须 > Worker 上游 {worker_s}s，"
        "否则只能收到空的 httpx 超时、收不到 Worker 带上游状态码的结构化 502"
    )
    # 其余工具不受影响（只加宽 web_search，避免掩盖 wisburg 走代理这类慢）
    assert definitions._TOOL_TIMEOUT == 8.0, (
        "只加宽 web_search，其余工具维持 8s —— 加宽它们会掩盖慢"
        "（wisburg 直连 ~0.5s，走代理劣化到 8-18s 是要暴露的问题，不是要容忍的）。"
        "若确实要重调这条共享超时，改这里的期望值并在 commit 里说明理由。"
    )


def test_exec_web_search_uses_web_search_timeout(monkeypatch):
    """load-bearing：AsyncClient 真的拿到 _WEB_SEARCH_TIMEOUT（防常量改了没接线）。"""
    from committee.tools import definitions

    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_URL", "https://example/search")

    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value={"results": []})
    factory = _mock_async_client(get_return=resp)

    with patch("httpx.AsyncClient", factory):
        _run(definitions._exec_web_search("AAPL"))

    assert factory.call_args.kwargs["timeout"] == definitions._WEB_SEARCH_TIMEOUT


def test_exec_web_search_unconfigured_url_returns_error(monkeypatch):
    from committee.tools import definitions

    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_URL", "")

    out = _run(definitions._exec_web_search("AAPL"))
    data = json.loads(out)
    assert "error" in data
    assert "not configured" in data["error"]


# ---- 1b. 相关性守卫 (DEFECT-WEBSEARCH-RELEVANCE·2026-07-30) -------------------
#
# 上游返 HTTP 200 + 满额条数 + 零 error，但内容与 query 完全无关（SEO 污染）。
# 守卫把这类结果集当失败处理，一条都不喂回 LLM。


def _garbage_resp():
    """真实垃圾样本（2026-07-30 e2e 实录）——查英伟达财报返法国消费杂志/克里米亚词条。"""
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value={
        "results": [
            {"title": "60 Millions de Consommateurs", "description": "magazine", "url": "https://x/1"},
            {"title": "Crimea - Wikipedia", "description": "peninsula", "url": "https://x/2"},
            {"title": "IndiGo - Book Domestic Flights", "description": "airline", "url": "https://x/3"},
        ],
    })
    return resp


def test_exec_web_search_unrelated_results_return_error(monkeypatch):
    from committee.tools import definitions

    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_URL", "https://example/search")
    monkeypatch.setattr("committee.config.WEB_SEARCH_RELEVANCE_CHECK", True)

    with patch("httpx.AsyncClient", _mock_async_client(get_return=_garbage_resp())):
        out = _run(definitions._exec_web_search(
            "Nvidia NVDA Q2 2026 earnings forecast analyst estimates",
        ))

    data = json.loads(out)
    assert "error" in data
    assert "unrelated" in data["error"]
    # 垃圾一条都不进 LLM 的阅读面
    assert "results" not in data
    assert "Crimea" not in out
    # 报错公约四字段（此出口曾是唯一手搓信封的地方，现走共享渲染器 —— 钉住）
    assert data["isError"] is True
    assert data["errorCategory"] == "transient"
    assert data["isRetryable"] is True
    # 指引是整句换过的：不许让模型改写 query（那是 validation 的处置），
    # 也不许残留"源内部已重试"那句对本形态不成立的通用文案
    assert "do not reword" in data["description"]
    assert "already retried" not in data["description"]
    # query 回显仍在（改走共享渲染器不得丢键）
    assert data["query"].startswith("Nvidia")


def test_exec_web_search_relevance_check_off_passes_garbage_through(monkeypatch):
    """kill-switch 关 → 回旧行为（原样喂回）。守卫是 load-bearing 的反证。"""
    from committee.tools import definitions

    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_URL", "https://example/search")
    monkeypatch.setattr("committee.config.WEB_SEARCH_RELEVANCE_CHECK", False)

    with patch("httpx.AsyncClient", _mock_async_client(get_return=_garbage_resp())):
        out = _run(definitions._exec_web_search(
            "Nvidia NVDA Q2 2026 earnings forecast analyst estimates",
        ))

    data = json.loads(out)
    assert "error" not in data
    assert data["number_of_results"] == 3


def test_exec_web_search_one_relevant_result_passes_whole_set(monkeypatch):
    """判据刻意宽松：任一条命中即整批放行（只堵「全错」，不做质量排序）。"""
    from committee.tools import definitions

    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_URL", "https://example/search")
    monkeypatch.setattr("committee.config.WEB_SEARCH_RELEVANCE_CHECK", True)

    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value={
        "results": [
            {"title": "Crimea - Wikipedia", "description": "peninsula", "url": "https://x/1"},
            {"title": "Q2 report", "description": "Nvidia beat estimates", "url": "https://x/2"},
        ],
    })
    with patch("httpx.AsyncClient", _mock_async_client(get_return=resp)):
        out = _run(definitions._exec_web_search("Nvidia Q2 2026 earnings"))

    data = json.loads(out)
    assert "error" not in data
    assert data["number_of_results"] == 2


def test_exec_web_search_empty_results_not_flagged_unrelated(monkeypatch):
    """返空 ≠ 无关：0 条走原路径（number_of_results=0），不冒充相关性失败。"""
    from committee.tools import definitions

    monkeypatch.setattr("committee.config.EXTERNAL_SEARCH_URL", "https://example/search")
    monkeypatch.setattr("committee.config.WEB_SEARCH_RELEVANCE_CHECK", True)

    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value={"results": []})
    with patch("httpx.AsyncClient", _mock_async_client(get_return=resp)):
        out = _run(definitions._exec_web_search("Nvidia Q2 earnings"))

    data = json.loads(out)
    assert "error" not in data
    assert data["number_of_results"] == 0


def test_query_tokens_drops_years_and_stopwords():
    from committee.tools.definitions import _query_tokens

    tokens = _query_tokens("The latest news about Nvidia in 2026")
    assert "nvidia" in tokens
    # 年份 + 功能词/填充词剔除（垃圾页面上太常见 → 留着制造假重叠）
    assert "2026" not in tokens
    for w in ("the", "latest", "news", "about", "in"):
        assert w not in tokens


def test_query_tokens_cjk_bigrams():
    from committee.tools.definitions import _query_tokens

    tokens = _query_tokens("英伟达财报")
    assert "英伟" in tokens
    assert "伟达" in tokens


def test_relevance_ignores_url_field():
    """url 不进比对面——bing 的 ck/a?<base64> 跳转链会随机撞短 token 制造假重叠。"""
    from committee.tools.definitions import _results_are_relevant

    results = [{
        "title": "Crimea - Wikipedia",
        "description": "peninsula",
        "url": "https://www.bing.com/ck/a?!&&p=nvidia123",
    }]
    assert _results_are_relevant("Nvidia earnings", results) is False


def test_relevance_cjk_query_matches_cjk_result():
    from committee.tools.definitions import _results_are_relevant

    results = [{"title": "英伟达发布第二季度财报", "description": ""}]
    assert _results_are_relevant("英伟达 财报", results) is True


# ---- 2. run_tool_agent -------------------------------------------------------


def test_run_tool_agent_no_tool_calls_returns_json():
    """LLM 首轮即给 text-only JSON → 直接解析返回，不进 tool loop。"""
    from committee.tools.agent_loop import run_tool_agent

    resp = MagicMock()
    resp.content = '{"headline": "no search needed", "conviction": 5}'
    resp.tool_calls = []

    bound = MagicMock()
    bound.ainvoke = AsyncMock(return_value=resp)
    llm = MagicMock()
    llm.bind_tools = MagicMock(return_value=bound)

    result = _run(run_tool_agent(llm, "sys", "user", tools=[]))
    assert result["headline"] == "no search needed"
    assert result["conviction"] == 5


def test_run_tool_agent_executes_tool_then_returns_json():
    """LLM 调一次 tool → 执行 → 结果回灌 → 第二轮给 JSON。"""
    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field

    from committee.tools.agent_loop import run_tool_agent

    class _P(BaseModel):
        query: str = Field(description="q")

    calls = []

    async def _exec(query: str) -> str:
        calls.append(query)
        return json.dumps({"results": [{"title": "hit"}]})

    tool = StructuredTool(
        name="web_search", description="search", args_schema=_P,
        func=lambda *a, **k: None, coroutine=_exec,
    )

    resp1 = MagicMock()
    resp1.content = ""
    resp1.tool_calls = [{"name": "web_search", "args": {"query": "AAPL"}, "id": "c1"}]

    resp2 = MagicMock()
    resp2.content = '{"headline": "searched", "conviction": 8}'
    resp2.tool_calls = []

    bound = MagicMock()
    bound.ainvoke = AsyncMock(side_effect=[resp1, resp2])
    llm = MagicMock()
    llm.bind_tools = MagicMock(return_value=bound)

    result = _run(run_tool_agent(llm, "sys", "user", tools=[tool]))
    assert calls == ["AAPL"]
    assert result["headline"] == "searched"


def test_run_tool_agent_logs_websearch_observe_with_role_tag(caplog):
    """Q3 measure-first: web_search 调用产出 websearch_observe 日志，带 role_tag + query。"""
    import logging as _logging

    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field

    from committee.tools.agent_loop import run_tool_agent

    class _P(BaseModel):
        query: str = Field(description="q")

    async def _exec(query: str) -> str:
        return json.dumps({"results": [{"title": "hit", "url": "http://x"}]})

    tool = StructuredTool(
        name="web_search", description="search", args_schema=_P,
        func=lambda *a, **k: None, coroutine=_exec,
    )

    resp1 = MagicMock()
    resp1.content = ""
    resp1.tool_calls = [{"name": "web_search", "args": {"query": "NVDA price"}, "id": "c1"}]
    resp2 = MagicMock()
    resp2.content = '{"decision": "HOLD"}'
    resp2.tool_calls = []

    bound = MagicMock()
    bound.ainvoke = AsyncMock(side_effect=[resp1, resp2])
    llm = MagicMock()
    llm.bind_tools = MagicMock(return_value=bound)

    with caplog.at_level(_logging.INFO, logger="committee.tools.agent_loop"):
        _run(run_tool_agent(llm, "sys", "user", tools=[tool], role_tag="fund_mgr"))

    observe = [r for r in caplog.records if r.getMessage().startswith("websearch_observe")]
    assert observe, "expected a websearch_observe log line for the web_search call"
    msg = observe[0].getMessage()
    assert "role=fund_mgr" in msg
    assert "NVDA price" in msg


def _ws_agent_llm(query="AAPL"):
    """LLM mock：一轮 web_search(query) → 第二轮出最终 JSON。"""
    resp1 = MagicMock()
    resp1.content = ""
    resp1.tool_calls = [{"name": "web_search", "args": {"query": query}, "id": "c1"}]
    resp2 = MagicMock()
    resp2.content = '{"decision": "HOLD"}'
    resp2.tool_calls = []
    bound = MagicMock()
    bound.ainvoke = AsyncMock(side_effect=[resp1, resp2])
    llm = MagicMock()
    llm.bind_tools = MagicMock(return_value=bound)
    return llm


def _ws_tool(coroutine):
    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field

    class _P(BaseModel):
        query: str = Field(description="q")

    return StructuredTool(
        name="web_search", description="s", args_schema=_P,
        func=lambda *a, **k: None, coroutine=coroutine,
    )


def test_run_tool_agent_returns_tool_outputs_when_requested():
    """AD.4: return_tool_outputs=True → (dict, outputs)；默认仍只返回 dict（向后兼容）。"""
    from committee.tools.agent_loop import run_tool_agent

    async def _exec(query: str) -> str:
        return json.dumps({"results": [{"title": "hit", "url": "http://x"}]})

    # 默认：dict
    out = _run(run_tool_agent(_ws_agent_llm(), "s", "u", tools=[_ws_tool(_exec)]))
    assert isinstance(out, dict)

    # opt-in：(dict, outputs)
    data, outputs = _run(run_tool_agent(
        _ws_agent_llm(), "s", "u", tools=[_ws_tool(_exec)], return_tool_outputs=True))
    assert isinstance(data, dict)
    assert len(outputs) == 1
    assert outputs[0]["tool"] == "web_search"
    assert outputs[0]["args"]["query"] == "AAPL"
    assert "hit" in outputs[0]["result"]


def test_run_tool_agent_surfaces_tool_failure_in_outputs():
    """AD.4 超时/失败反向单测：工具抛错 → 错误如实进 tool_outputs（不伪装成功），loop 仍完成。"""
    from committee.tools.agent_loop import run_tool_agent

    async def _boom(query: str) -> str:
        raise asyncio.TimeoutError("simulated timeout")

    data, outputs = _run(run_tool_agent(
        _ws_agent_llm(), "s", "u", tools=[_ws_tool(_boom)], return_tool_outputs=True))
    assert isinstance(data, dict)  # loop 仍走到最终 JSON
    assert len(outputs) == 1
    assert "error" in outputs[0]["result"].lower()


def test_run_tool_agent_web_search_budget_denies_excess():
    """web_search_budget=1：一轮内 2 个 web_search，第 2 个被拒（不执行），返回 steer。"""
    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field

    from committee.tools.agent_loop import run_tool_agent

    class _P(BaseModel):
        query: str = Field(description="q")

    executed = []

    async def _exec(query: str) -> str:
        executed.append(query)
        return json.dumps({"results": [{"title": query}]})

    tool = StructuredTool(
        name="web_search", description="search", args_schema=_P,
        func=lambda *a, **k: None, coroutine=_exec,
    )

    resp1 = MagicMock()
    resp1.content = ""
    resp1.tool_calls = [
        {"name": "web_search", "args": {"query": "q1"}, "id": "c1"},
        {"name": "web_search", "args": {"query": "q2"}, "id": "c2"},
    ]
    resp2 = MagicMock()
    resp2.content = '{"headline": "done", "conviction": 5}'
    resp2.tool_calls = []

    bound = MagicMock()
    bound.ainvoke = AsyncMock(side_effect=[resp1, resp2])
    llm = MagicMock()
    llm.bind_tools = MagicMock(return_value=bound)

    result = _run(run_tool_agent(llm, "sys", "user", tools=[tool], web_search_budget=1))
    # Only the first search executed; second denied.
    assert executed == ["q1"]
    assert result["headline"] == "done"


def test_run_tool_agent_executes_batch_concurrently():
    """一轮内多个 tool_call 经 asyncio.gather 并发执行（顺序无关，全部跑到）。"""
    import asyncio as _aio

    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field

    from committee.tools.agent_loop import run_tool_agent

    class _P(BaseModel):
        query: str = Field(description="q")

    done = []

    async def _exec(query: str) -> str:
        await _aio.sleep(0.01)  # 若串行执行，3 个累加；并发则重叠
        done.append(query)
        return json.dumps({"ok": query})

    tool = StructuredTool(
        name="web_search", description="search", args_schema=_P,
        func=lambda *a, **k: None, coroutine=_exec,
    )

    resp1 = MagicMock()
    resp1.content = ""
    resp1.tool_calls = [
        {"name": "web_search", "args": {"query": f"q{i}"}, "id": f"c{i}"}
        for i in range(3)
    ]
    resp2 = MagicMock()
    resp2.content = '{"headline": "ok", "conviction": 5}'
    resp2.tool_calls = []

    bound = MagicMock()
    bound.ainvoke = AsyncMock(side_effect=[resp1, resp2])
    llm = MagicMock()
    llm.bind_tools = MagicMock(return_value=bound)

    result = _run(run_tool_agent(llm, "sys", "user", tools=[tool], web_search_budget=10))
    assert sorted(done) == ["q0", "q1", "q2"]
    assert result["headline"] == "ok"


def test_run_tool_agent_bind_tools_failure_falls_back():
    """bind_tools 抛错 → 退回无工具 plain invoke。"""
    from committee.tools.agent_loop import run_tool_agent

    resp = MagicMock()
    resp.content = '{"headline": "fallback", "conviction": 4}'

    llm = MagicMock()
    llm.bind_tools = MagicMock(side_effect=RuntimeError("no bind_tools"))
    llm.ainvoke = AsyncMock(return_value=resp)

    result = _run(run_tool_agent(llm, "sys", "user", tools=[]))
    assert result["headline"] == "fallback"


# ---- 3. make_analyst_node path selection (async) -----------------------------


def test_analyst_node_uses_tool_agent_when_role_in_whitelist(monkeypatch):
    """Role in WEB_SEARCH_ROLES → run_tool_agent called, _invoke_json not."""
    monkeypatch.setattr("committee.agents.base.WEB_SEARCH_ROLES", frozenset({"historian"}))
    monkeypatch.setattr("committee.agents.base.MIN_CHARS_ANALYST", 0)

    mock_result = {
        "headline": "History repeats", "conviction": 7,
        "key_points": ["point1"], "bullish_factors": ["b1"],
        "bearish_factors": ["be1"], "risks": ["r1"],
    }

    async def _fake_agent(llm, system, user, tools, *, return_tool_outputs=False, **kwargs):
        # AO: analyst 节点现以 return_tool_outputs=True 调 run_tool_agent → 必返 (dict, outputs)
        return (dict(mock_result), []) if return_tool_outputs else dict(mock_result)

    mock_llm = MagicMock()
    with patch("committee.tools.run_tool_agent", side_effect=_fake_agent) as mock_agent:
        with patch("committee.agents.base._invoke_json") as mock_plain:
            with patch("committee.agents.base._llm", return_value=mock_llm):
                from committee.agents.base import make_analyst_node
                node = make_analyst_node("historian")
                result = _run(node({"query": "test", "context": "ctx"}))

    mock_agent.assert_called_once()
    mock_plain.assert_not_called()
    assert "historian_report" in result


def test_analyst_node_uses_plain_invoke_when_role_not_in_whitelist(monkeypatch):
    """Role NOT in WEB_SEARCH_ROLES → _invoke_json called, no tool agent."""
    monkeypatch.setattr("committee.agents.base.WEB_SEARCH_ROLES", frozenset())
    monkeypatch.setattr("committee.agents.base.MIN_CHARS_ANALYST", 0)

    mock_result = {
        "headline": "Technical", "conviction": 6,
        "key_points": ["p1"], "bullish_factors": ["b1"],
        "bearish_factors": ["be1"], "risks": ["r1"],
    }

    mock_llm = MagicMock()
    with patch("committee.agents.base._invoke_json", return_value=mock_result) as mock_plain:
        with patch("committee.tools.run_tool_agent") as mock_agent:
            with patch("committee.agents.base._llm", return_value=mock_llm):
                from committee.agents.base import make_analyst_node
                node = make_analyst_node("technical")
                result = _run(node({"query": "test", "context": "ctx"}))

    mock_plain.assert_called_once()
    mock_agent.assert_not_called()
    assert "technical_report" in result


def test_analyst_expansion_does_not_use_tool_agent(monkeypatch):
    """扩写（MIN_CHARS 触发）走 plain _invoke_json，不走 tool agent —— 成本保护。"""
    monkeypatch.setattr("committee.agents.base.WEB_SEARCH_ROLES", frozenset({"historian"}))
    monkeypatch.setattr("committee.agents.base.MIN_CHARS_ANALYST", 99999)

    initial = {
        "headline": "Test", "conviction": 7, "key_points": ["short"],
        "bullish_factors": ["b"], "bearish_factors": ["be"], "risks": ["r"], "role": "historian",
    }
    expansion = {
        "headline": "Test", "conviction": 7,
        "key_points": ["short", "extra1"], "bullish_factors": ["b", "xb"],
        "bearish_factors": ["be", "xbe"], "risks": ["r", "xr"],
    }

    call_log = []

    async def _fake_agent(llm, system, user, tools, *, return_tool_outputs=False, **kwargs):
        call_log.append("agent")
        return (dict(initial), []) if return_tool_outputs else dict(initial)

    def _fake_plain(llm, system, user):
        call_log.append("plain")
        return dict(expansion)

    mock_llm = MagicMock()
    with patch("committee.tools.run_tool_agent", side_effect=_fake_agent):
        with patch("committee.agents.base._invoke_json", side_effect=_fake_plain):
            with patch("committee.agents.base._llm", return_value=mock_llm):
                from committee.agents.base import make_analyst_node
                node = make_analyst_node("historian")
                _run(node({"query": "test", "context": "ctx"}))

    assert call_log == ["agent", "plain"], (
        f"Expected [agent, plain] but got {call_log}. Expansion must not use the tool agent."
    )


# ---- 3a. analyst LLM/tool failure → fallback (no crash) regression -----------
#
# 2026-05-29 full e2e crash: analyst_technical's deepseek call raised
# APIConnectionError after retries; make_analyst_node had no guard → the whole
# parallel Phase-1 fan-out crashed. A single analyst's transient failure must
# degrade to a fallback report, not crash the pipeline.


def test_analyst_node_tool_agent_failure_degrades_to_fallback(monkeypatch):
    monkeypatch.setattr("committee.agents.base.WEB_SEARCH_ROLES", frozenset({"technical"}))
    monkeypatch.setattr("committee.agents.base.MIN_CHARS_ANALYST", 0)

    async def _boom(llm, system, user, tools, **kwargs):
        raise ConnectionError("Connection error.")  # mimics openai APIConnectionError

    mock_llm = MagicMock()
    with patch("committee.tools.run_tool_agent", side_effect=_boom):
        with patch("committee.agents.base._llm", return_value=mock_llm):
            from committee.agents.base import make_analyst_node
            node = make_analyst_node("technical")
            result = _run(node({"query": "test", "context": "ctx"}))

    # pipeline survives: a report (fallback) is still produced for the role
    assert "technical_report" in result
    assert result["technical_report"].role == "technical"


def test_analyst_node_plain_invoke_failure_degrades_to_fallback(monkeypatch):
    monkeypatch.setattr("committee.agents.base.WEB_SEARCH_ROLES", frozenset())
    monkeypatch.setattr("committee.agents.base.MIN_CHARS_ANALYST", 0)

    def _boom(llm, system, user):
        raise ConnectionError("Connection error.")

    mock_llm = MagicMock()
    with patch("committee.agents.base._invoke_json", side_effect=_boom):
        with patch("committee.agents.base._llm", return_value=mock_llm):
            from committee.agents.base import make_analyst_node
            node = make_analyst_node("macro")
            result = _run(node({"query": "test", "context": "ctx"}))

    assert "macro_report" in result
    assert result["macro_report"].role == "macro"


def test_analyst_node_cancelled_error_still_propagates(monkeypatch):
    """CancelledError (cooperative cancellation) must NOT be swallowed by the guard."""
    import asyncio as _asyncio
    monkeypatch.setattr("committee.agents.base.WEB_SEARCH_ROLES", frozenset())
    monkeypatch.setattr("committee.agents.base.MIN_CHARS_ANALYST", 0)

    def _cancel(llm, system, user):
        raise _asyncio.CancelledError()

    mock_llm = MagicMock()
    with patch("committee.agents.base._invoke_json", side_effect=_cancel):
        with patch("committee.agents.base._llm", return_value=mock_llm):
            from committee.agents.base import make_analyst_node
            node = make_analyst_node("macro")
            with pytest.raises(_asyncio.CancelledError):
                _run(node({"query": "test", "context": "ctx"}))


# ---- 3b. make_decision_node fund_mgr search path -----------------------------


def test_decision_head_pass_uses_invoke_json_not_tool_agent(monkeypatch):
    """八步重写：head pass（步骤 4）走 _invoke_json（不走 run_tool_agent）。
    验证已分离（step 3 DeepSeek 查证已走 _run_verification async 函数）。

    用 sentinel 异常确认 _invoke_json 路径被取。
    """
    class _InvokeJsonCalled(Exception):
        pass

    call_count = {"n": 0}

    def _fake_invoke(llm, system, user):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return {"thesis_outline": ["A", "B", "C"], "verify_checklist": []}
        raise _InvokeJsonCalled("invoke_json path confirmed for head pass")

    mock_state = {
        "query": "test", "context": "",
        "macro_report": None, "sentiment_report": None, "technical_report": None,
        "fundamentals_report": None, "commodity_report": None, "political_report": None,
        "historian_report": None, "economist_report": None,
        "debate_log": [], "votes": [],
    }

    mock_llm = MagicMock()
    with patch("committee.agents.base._llm", return_value=mock_llm):
        with patch("committee.agents.base._invoke_json", side_effect=_fake_invoke):
            with patch("committee.agents.base.emit_event"):
                async def _noop_verify(*a, **kw): return [], [], []
                async def _noop_scan(*a, **kw): return []
                with patch("committee.agents.base._build_verify_checklist", return_value=[]):
                    with patch("committee.agents.base._run_verification", side_effect=_noop_verify):
                        with patch("committee.agents.base._derive_all_confidence", return_value=([], {})):
                            from committee.agents.base import make_decision_node
                            node = make_decision_node("fund_mgr")
                            with pytest.raises(_InvokeJsonCalled, match="invoke_json path confirmed"):
                                _run(node(mock_state))


# ---- 3c. _run_verification 绑 web_search tool（联网职责守卫）-----------------


def test_run_verification_calls_run_tool_agent_with_web_tools():
    """Q1 守卫：_run_verification 真实路径通过 run_tool_agent + ALL_TOOLS 执行。

    这是"步骤 3 联网"契约的唯一出口——若 provider 路由错或 tool 没绑上，
    整套 pipeline 会静默降级成 opus 不查 DeepSeek 也不查，而 mock 测试照样绿。

    策略：用 AsyncMock 捕获传给 run_tool_agent 的 tools 参数，验证包含 web_search。
    sentinel 不用 Exception 子类（会被 _run_verification 内的 except Exception 吞掉）。
    """
    from committee.agents.base import _run_verification
    from committee.tools import ALL_TOOLS

    # 先验证 ALL_TOOLS 里确实有 web_search（否则即便调用到也守不住联网契约）
    tool_names = {t.name for t in ALL_TOOLS}
    assert "web_search" in tool_names, (
        "ALL_TOOLS 中必须包含 web_search；否则步骤 3 查证无法联网"
    )

    captured_tools: list = []

    async def _capture_agent(llm, system, user, tools, *, return_tool_outputs=False, **kwargs):
        captured_tools.extend(tools)
        # 返回合法的空 findings 结构，让 _run_verification 正常走完
        result = {"findings": []}
        return (result, []) if return_tool_outputs else result

    checklist = [{"item": "京东方最新股价", "criticality": "high", "data_kind": "current_price"}]

    # lazy import 路径：_run_verification 内 `from committee.tools import run_tool_agent`
    # patch 打在 committee.tools 命名空间（re-export 点），这是 lazy import 拿到的那个引用
    with patch("committee.tools.run_tool_agent", side_effect=_capture_agent):
        _run(_run_verification(MagicMock(), checklist, "京东方TCL"))

    assert captured_tools, "_run_verification 没有调用 run_tool_agent（联网路径未触发）"
    passed_tool_names = {t.name for t in captured_tools}
    assert "web_search" in passed_tool_names, (
        f"_run_verification 必须把含 web_search 的 tool 列表传给 run_tool_agent；"
        f"实际收到：{passed_tool_names}"
    )


def test_run_verification_returns_empty_for_no_high_items():
    """空 high-criticality 清单 → 跳过联网，返回 ([], [], [])。

    ★ 第三项（降级记录）必须是**空**：「没有要查的项」是正常结果，
    不是「核验没做成」（BK.2 #36）。两者都返回空 findings，靠这一项分开 ——
    混了就会每跑都报一次「核验没做」，把真信号淹掉。
    """
    from committee.agents.base import _run_verification

    result = _run(
        _run_verification(
            MagicMock(),
            [{"item": "背景数据", "criticality": "low", "data_kind": "other"}],
            "test",
        )
    )
    assert result == ([], [], [])


def test_run_verification_failure_is_visible_in_degradation_summary():
    """🔴 ★★ 注入真故障：核验跑不起来 → 必须留痕，且下游汇总读得出来。

    治的病：失败时交出的空清单**读起来就是「查过了、没发现问题」**。
    为什么注入真故障而不是手搭记录：这条痕只在 except 分支里，正常跑批永不进入，
    "跑一次是绿的"对它零信息量（坑表 BC 形态⑥）。
    """
    from committee.agents.base import _run_verification
    from committee.degradation import degradation_summary

    async def _boom(*a, **kw):
        raise RuntimeError("查证工具挂了")

    checklist = [{"item": "京东方最新股价", "criticality": "high", "data_kind": "current_price"}]
    with patch("committee.tools.run_tool_agent", side_effect=_boom):
        findings, tool_outputs, notices = _run(
            _run_verification(MagicMock(), checklist, "京东方TCL"))

    # ① 判定零改动：仍然交出空 findings、仍然不抛
    assert findings == [] and tool_outputs == []
    # ② 痕确实留下了
    assert notices and notices[0]["rule"] == "fund-mgr-verification"
    assert notices[0]["action"] == "skipped_failed"
    # ③ 下游汇总读得出来
    codes = {e.code for e in degradation_summary(
        {"common_context": {}, "final_decision": {}, "enforcement_log": notices})}
    assert "fact_verification_failed" in codes,         f"核验没做成，降级汇总却看不见 = 空清单继续冒充「没发现问题」· 实际: {sorted(codes)}"


# ---- 4. config WEB_SEARCH_ROLES + EXTERNAL_SEARCH_* --------------------------


@pytest.fixture
def restore_config():
    """本节专用收尾：跑完把 committee.config 重新 load 回本机真实配置。

    下面几个测试靠 `importlib.reload` 观察不同 env 下的解析结果，而 reload 改的是
    **全局模块对象**、不是局部副本 —— 不收尾就会把最后一次的假 env 留在原地，
    同 session 后续任何直接读 `committee.config.X` 的测试都会看到它。
    实测（摘掉本 fixture 后用探针复现）：test_external_search_url_override 会把
    `EXTERNAL_SEARCH_URL = "https://my/search"` 一直留到进程结束。

    收尾放在 fixture teardown 而非测试体内：这几个测试的 env patch 都是**函数体内的
    context manager**，测试返回时早已退出，teardown 这时 reload 读到的就是真实环境。
    """
    import importlib
    yield
    import committee.config as cfg
    importlib.reload(cfg)


def test_web_search_roles_default_all(restore_config):
    import importlib
    with patch.dict("os.environ", {}, clear=False):
        if "COMMITTEE_WEB_SEARCH_ROLES" in __import__("os").environ:
            del __import__("os").environ["COMMITTEE_WEB_SEARCH_ROLES"]
        import committee.config as cfg
        importlib.reload(cfg)
        expected = frozenset({
            "macro", "sentiment", "technical", "fundamentals",
            "commodity", "political", "historian", "economist", "fund_mgr",
        })
        assert cfg.WEB_SEARCH_ROLES == expected


def test_web_search_roles_explicit_empty_disables_all(restore_config):
    import importlib
    with patch.dict("os.environ", {"COMMITTEE_WEB_SEARCH_ROLES": ""}):
        import committee.config as cfg
        importlib.reload(cfg)
        assert cfg.WEB_SEARCH_ROLES == frozenset()


def test_web_search_roles_parses_csv(restore_config):
    import importlib
    with patch.dict("os.environ", {"COMMITTEE_WEB_SEARCH_ROLES": "historian,political,economist"}):
        import committee.config as cfg
        importlib.reload(cfg)
        assert cfg.WEB_SEARCH_ROLES == frozenset({"historian", "political", "economist"})


def test_external_search_defaults(restore_config):
    import importlib
    with patch.dict("os.environ", {}, clear=False):
        for k in ("COMMITTEE_EXTERNAL_SEARCH_URL", "COMMITTEE_EXTERNAL_SEARCH_ENGINES"):
            __import__("os").environ.pop(k, None)
        # ⚠️ 本测试测的是**代码默认值**，必须与本机 .env 无关。
        # config.py:16 在 import 时跑 load_dotenv() → importlib.reload 会把 .env
        # 里的值重新灌回 os.environ，上面几行 pop 白做。此前一直绿只是因为 .env
        # 里恰好没设这两个键；2026-07-31 有人把 COMMITTEE_EXTERNAL_SEARCH_URL
        # 写进 .env（切 Serper）后本测试立刻红 —— 测的其实是本机配置不是默认值。
        # 停掉 dotenv 源头（reload 会重新 `from dotenv import load_dotenv`，
        # 补 module 属性不管用，必须打源）。
        with patch("dotenv.load_dotenv", lambda *a, **kw: None):
            import committee.config as cfg
            importlib.reload(cfg)
        assert cfg.EXTERNAL_SEARCH_URL.endswith("/search")
        # Default engine set must exclude `bing`: it answers HTTP 200 with a full
        # result count and no error log, but 35% of what it returns is SEO garbage
        # unrelated to the query (2026-07-30 A/B: bing's marginal contribution was
        # +1 useful result and +24 garbage). The 07-29 default `bing,duckduckgo`
        # was picked on a non-empty-rate measurement that never checked relevance.
        # Measurements (both dimensions): see config.EXTERNAL_SEARCH_ENGINES.
        assert "duckduckgo" in cfg.EXTERNAL_SEARCH_ENGINES
        assert "bing" not in cfg.EXTERNAL_SEARCH_ENGINES
        assert cfg.EXTERNAL_SEARCH_MAX_RESULTS >= 1
        # Relevance guard on by default (engine-agnostic backstop).
        assert cfg.WEB_SEARCH_RELEVANCE_CHECK is True


def test_external_search_url_override(restore_config):
    import importlib
    with patch.dict("os.environ", {"COMMITTEE_EXTERNAL_SEARCH_URL": "https://my/search"}):
        import committee.config as cfg
        importlib.reload(cfg)
        assert cfg.EXTERNAL_SEARCH_URL == "https://my/search"
