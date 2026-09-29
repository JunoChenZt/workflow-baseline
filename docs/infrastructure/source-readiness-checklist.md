# Data Source Production Readiness Checklist

> A6.1.4 Phase 0a 新增治理项 (本节点新增, 非 backlog 原有任务)。
> 未来涉及数据源变更/新增的节点, 在 pre-flight (§2.3) 时引用本 checklist。

## 适用场景

- 新增数据源
- 变更数据源 endpoint / 协议
- 变更代理配置
- 部署到新环境

## Checklist

### 1. Source 可达性 (必须)

| # | 检查项 | PASS 标准 | 验证方法 |
|---|--------|----------|---------|
| 1.1 | HTTP 200 (或等效成功) | status_code == 200 | `scripts/verify_sources.py` |
| 1.2 | Response body 非空 | len(body) > 0 | 同上 |
| 1.3 | Parse 成功 | dict / DataFrame 可解析 | 同上 |
| 1.4 | 数据非空 | 至少 1 条有效记录 | 同上 |
| 1.5 | Endpoint 匹配 | URL 含预期 domain | 同上 (防静默 fallback) |
| 1.6 | Latency < 30s | response time < 30000ms | 同上 |

### 2. 代理兼容 (环境相关)

| # | 检查项 | 验证方法 |
|---|--------|---------|
| 2.1 | Library 读取哪些 proxy source | 参考 [proxy-allowlist.md](proxy-allowlist.md) 兼容矩阵 |
| 2.2 | NO_PROXY 绕过有效 | httpbin.org IP 对比测试 |
| 2.3 | WinINET 影响评估 (Windows) | trust_env=False 对比测试 |

### 3. 降级路径 (必须)

| # | 检查项 | PASS 标准 |
|---|--------|----------|
| 3.1 | Source 失败不崩溃 | quality_flag="degraded", 非 exception |
| 3.2 | 部分 source 失败保留健康 source | payload 含健康 source 数据 |
| 3.3 | 全部 source 失败返回 None | payload=None, flag="degraded"；**例外（2026-07-23）**：`ticker_specific` 现价全失 → 早停「暂不可分析」不硬跑（[#200](https://github.com/JunoChenZt/subagent-for-investment/pull/200)）；价格源单边失败若另一边有价 → 不降级（冗余组·[#199](https://github.com/JunoChenZt/subagent-for-investment/pull/199)） |

### 4. 缓存集成 (如适用)

| # | 检查项 | PASS 标准 |
|---|--------|----------|
| 4.1 | Cache miss → fetch | fetch_count == 1 |
| 4.2 | Cache hit → skip IO | fetch_count == 0 |
| 4.3 | Cache 异常 → fallback fetch | cache error 不阻塞 |
| 4.4 | Fetch 失败不写 cache | cache.size() == 0 after failure |

### 5. Evidence (必须)

| # | 检查项 |
|---|--------|
| 5.1 | N >= 2 次 verify run |
| 5.2 | Evidence log 已脱敏 (参考 [redact-rules.md](../reference/redact-rules.md)) |
| 5.3 | 不可达 source 按事实分类 (CONFIG_MISSING / BLOCKED_BY_ENV / FAIL) |
| 5.4 | sources/ 实现问题记录为 finding, 不在 verify 节点修 |

## 当前 A6.1.4 Phase 0a 结果

| Source | 状态 | 说明 |
|--------|------|------|
| FRED | CONFIG_MISSING | 无 FRED_API_KEY (非 network failure) |
| yfinance (AAPL) | PASS (间歇 flaky) | Yahoo API 偶发 "possibly delisted" |
| yfinance (BRK-B) | PASS | 含连字符 edge case, 稳定 |
| tushare (600519/000001) | CONFIG_MISSING | 无 TUSHARE_TOKEN (非 network failure) |
| RSS (MarketWatch) | PASS | 替换 Yahoo (404/429), Dow Jones CDN, 10 items |
| RSS (Google) | PASS | 稳定, ~100 headlines |
| Wisburg (智堡, MCP) | 后续接入 (A6.2.2, 不在 Phase 0a 范围) | MCP Streamable HTTP；`WISBURG_MCP_URL` 默认 `https://mcp.wisburg.com/mcp`，`WISBURG_API_KEY` 必填（缺失 → 单源降级）；client `trust_env=False` 强制直连不走 VPN 代理 |

## sources/ 改动需求 (surface, 不在本节点修)

1. **tushare**: 需设置 TUSHARE_TOKEN 环境变量。补 token 后预期 PASS；httpx 实现，proxy 行为与 FRED/RSS 一致，无 WinINET 问题。
2. **RSS Yahoo (已解决)**: `feeds.finance.yahoo.com` 返回 404, `finance.yahoo.com/news/rssindex` 返回 429。PR-A 已切换至 MarketWatch。长期可靠性见 backlog。
3. **yfinance AAPL flaky**: Yahoo API 间歇性错误, 需要重试机制或降级容忍。
