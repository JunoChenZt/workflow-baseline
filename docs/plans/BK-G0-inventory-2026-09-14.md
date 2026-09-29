# BK.0 盘点 · 降级点全景（2026-09-14）

> **性质**：[BK 重评方案](BK-silent-degradation-reeval-2026-09-14.md) 的 G0 产出。**只读盘点，零代码改动**。
> **口径**：降级 = **某个能力退了一步、产出仍继续、下游可能不知道**。区别于 ① 重试中间态（后面还有最终态）② 整跑崩（会炸，不是静默）③ 纯信息性警告。
> **🔴 对方案 §2.2「44 处」的订正见 §1.2** —— 那是一次窄词表 grep 的数，**不是全集**。

---

## 大白话导读

这一步只干一件事：**把"系统会在什么时候悄悄退一步"列全，并逐个查它退了之后在产物里留没留下影子。**

结论三句：

1. **数字错了、而且错得不小**。方案里说约 44 处，那是按"降级/兜底/回退/fallback"这几个词搜出来的。换一套更宽的词再搜，**告警类日志共 179 条、其中 105 条像是在说退路**，两套词表差了 69 条。逐条看过之后，**真正算降级的是 58 处**，其余是重试中间态或真崩。⇒ 方案里那句"44 处"作废。
2. **一半以上没有影子**。58 处里，**33 处只写了一行日志**——跑完看产物根本看不出来。〔**🔴 2026-09-15 重算**：这两个数复算不出来（详见 §3.0）。**能对上账的是表本身**：**62 行**里 **44 行无痕**、已做 3 行、**余 42 行待补**（§2.5 已补齐 9 行·其中 **1 条是新查出的 🔴**）。〕
3. **最要紧的是其中三条**：系统里有三道"检查"，当它们自己出故障时，**产物看起来和"检查通过了"一模一样**——安全信号算不出来就当作"没问题"放行、誊写核查跳过时按"通过"处理、决策前的事实核验失败时交出一份空的问题清单（空清单读起来就是"没发现问题"）。这三条不是"少记了一笔账"，是**把"没检查"说成了"检查过、没事"**，正是当初立这条待办要治的最严重形态。

---

## 1. 计数方法与成立条件

### 1.1 方法

| 项 | 做法 |
|---|---|
| 文件枚举 | `git ls-files -z src/committee`（CJK 路径不转义）→ **148 个 .py**；读失败直接抛，不静默跳过 |
| 调用点枚举 | AST 找 `log/logger/_log . warning/error/exception(...)`，取首个字面量或 f-string 参数作消息 → **179 处** |
| 词表 A（方案原用） | `降级 兜底 回退 fallback 缺席` → **命中 36 处** |
| 词表 B（对差集用） | A + `skip 跳过 degrad unavailable 失败 failed 超时 timeout None 空 placeholder 占位 truncat 截断 partial 退回 不可用` → **命中 105 处** |
| 人工分类 | 105 处逐条读上下文，判「真降级 / 重试中间态 / 崩 / 信息性」 |

**成立条件（缺一则本表不是全集）**：① 只扫 `src/committee`（`scripts/` / `tests/` 不算产品行为）；② 只认 `log.warning/error/exception` 三种调用，**`log.info` / `log.debug` 里的降级不在内**（已知至少 2 处：`builder.py` 缓存 get/set 失败走 `debug`）；③ 只认首个字面量参数，消息拼在变量里的认不出；④ 无日志的降级点（只改字段不喊）靠 [S2 §6 fallback 表](../roadmap/S2.md) 逐行补，**不靠日志扫描发现**。

### 1.2 🔴 对方案 §2.2 的订正

| 方案原写 | 实数 | 差在哪 |
|---|---|---|
| 「44 处 warning 文本含降级字样」 | **窄词表 36 · 宽词表 105 · 真降级 58** | 44 那个数当时是 `grep -A1` 的行数（含上下文行），既不是调用点数也不是降级点数。**三个数全不同，原句作废** |

**差集里捞出的真降级点**（词表 A 完全看不见，且多数只写日志）：取数封顶后产出空资料夹 · EXEC-FLOOR 信号算不出按不触发放行 · 誊写核查 fail-open · 决策核验失败退空清单 · 辩论/投票解析失败用占位 · 基本面拉取失败 · 名录不可用 · 归档导出失败 · 大纲解析失败退单段 · 回应解析失败跳过。

⇒ **坑表④「枚举型验证宣称全绿前先证工具看得见全部对象」再 +1 实证**：同一件事换个词表，结论从 44 变 105。

## 2. 降级点全表（62 行 = 53 原有 + §2.5 补齐 9·标题原写「58 处真降级」·该数复算不出·见 §3.0）

图例 —— **留痕层**：`state`=有结构化字段 · `trace`=排查报告里看得见 · `log`=只有一行日志 · `cli`=用户面可见。
**🔴 = 安全型静默放行**（检查自己坏了，产物看起来像检查通过）。

### 2.1 seg1 召回层（22 处）

| # | 降级点 | 位置 | 今天留痕 | 层 |
|---|---|---|---|---|
| 1 | classify LLM 失败 → 名录 | [classifier.py:464](../../src/committee/query_class/classifier.py) | `query_classification.source="registry"` | state·trace |
| 2 | 名录未命中 → regex | 同上 | `source="regex"` | state·trace |
| 3 | 三层全落空 → THEMATIC 兜底 | [classifier.py:517](../../src/committee/query_class/classifier.py) | `source="default"` | state·trace |
| 4 | 名录不可用（索引构建失败） | [service.py:210](../../src/committee/security_registry/service.py) | — | **log** 〔**✅ PR3 2026-09-18 已补痕**·分支 `auto/BK.2-M2b`·索引构建失败 → 返回空 → 对账写「名录不可用」旗子，由读法 `registry_unavailable` 报〕 |
| 5 | 名录为空且 lazy 拉取关闭 → 名录能力本进程不可用 | [service.py:159](../../src/committee/security_registry/service.py) | — | **log** 〔**✅ PR3 2026-09-18 已补痕**·分支 `auto/BK.2-M2b`·补拉关闭 = 配置不是故障，名录空 → 旗子读法 `registry_unavailable` 报〕 |
| 6 | 名录刷新失败（保留旧数据） | [service.py:138](../../src/committee/security_registry/service.py) | — | **log** 〔**✅ PR3 2026-09-18 已补痕**·分支 `auto/BK.2-M2b`·跑批内现拉时由 `registry_market_fetch_failed` 便条报（带市场与原因）；跑批外的刷新命令不发〕 |
| 7 | 名录疑似被上游截断，拒绝写入 | [service.py:141](../../src/committee/security_registry/service.py) | — | **log** 〔**✅ PR3 2026-09-18 已补痕**·分支 `auto/BK.2-M2b`·同上，便条 detail 记 `truncated_rejected`〕 |
| 8 | registry 校验/兜底跳过（3 处） | [classifier.py:368/396/483](../../src/committee/query_class/classifier.py) | — | **log** 〔**✅ PR3 2026-09-18 已补痕**·分支 `auto/BK.2-M2b`·索引不可用那两支 → 旗子读法；对账模块加载失败那支 → 便条 `registry_reconcile_failed`〕 |
| 9 | ticker 解析失败 → 空 | [classifier.py:347](../../src/committee/query_class/classifier.py) | `tickers=[]`（间接） | state 弱 〔**✅ P0 批 2026-09-17 已补痕**·合 main `3da9a61`·码 `ticker_unresolved`·收口点在 classify、三支共用一条〕 |
| 10 | 规划员没出计划 → 兜底路由 | [context_node.py:259](../../src/committee/agents/context_node.py) | `source_routing` 降级键 | state·trace |
| 11 | 计划全没过校验 → 兜底路由 | [context_node.py:267](../../src/committee/agents/context_node.py) | 同上 | state·trace |
| 12 | 出计划过程失败 → 兜底路由 | [context_node.py:282](../../src/committee/agents/context_node.py) | 同上 | state·trace |
| 13 | 出计划超 85s 封顶 → 兜底路由 | [context_node.py:407](../../src/committee/agents/context_node.py) | 同上 | state·trace |
| 14 | 校验层全灭（0 条存活） | [validator.py:865](../../src/committee/retrieval_plan/validator.py) | 间接（走兜底） | **log** |
| 15 | **取数+回核超封顶 → 产出空资料夹** | [context_node.py:476](../../src/committee/agents/context_node.py) | `source_routing[__budget_capped__]` | 归档 ✅ 〔**✅ M1 2026-09-15 只加读法**·汇总侧派生 `fetch_budget_capped`·生产代码零改动〕 |
| 16 | 按计划构造源认不出 → 跳过这条腿 | [builder.py:365](../../src/committee/common_context/builder.py) | — | **log** 〔**✅ PR3 2026-09-18 已补痕**·分支 `auto/BK.2-M2b`·便条 `plan_leg_unbuildable`。🔴 §3.1 原判「假待办·leg_missing 已报」**与 09-04 后的代码不符**（被跳过的腿不进腿清单），已订正；今天生产上走不到（两份源名单启动时对齐）〕 |
| 17 | 单源失败/超时 → 跳过 | builder `gather(return_exceptions=True)` | — | **log** 〔✅ BK.6 2026-09-22 判**已覆盖**：后果（腿没到）由 `leg_missing` 派生逐腿报 + quality_flag；本处非 dict 结果直接跳过、**连 log 都没有**（本格「log」过时）；「原因」缺失记 backlog BK〕 |
| 18 | 补取价腿（安全兜底） | [validator.py:981](../../src/committee/retrieval_plan/validator.py) | — | **log** 〔**✅ PR3 2026-09-18 已补痕**·分支 `auto/BK.2-M2b`·读法 `price_leg_safety_added`（**只进排查报告**·补上了数据就不缺）；补的腿仍不进归档计划的意图清单〕 |
| 19 | 回核判腿降级 → scope=background | [builder.py:152](../../src/committee/common_context/builder.py) | `source_routing` 理由 | state·trace |
| 20 | 确认后缺腿 | [confirm.py `legs_empty`](../../src/committee/retrieval_plan/confirm.py) | `DegradationNotice` | **cli only** 〔✅ BK.6 2026-09-22 判**已覆盖**：同一事实由 `leg_missing` 派生报；本告警写进 `source_routing.__degradation_notices__` 后**全仓无读者**（「cli only」指终端那行）—— 记 backlog BK〕 |
| 21 | A股/美股基本面拉取失败（3 处） | [tushare_source.py:245/252](../../src/committee/common_context/sources/tushare_source.py) · [yfinance_source.py:232](../../src/committee/common_context/sources/yfinance_source.py) | — | **log** |
| 22 | yfinance NaN → 回退旧 bar · AV 兜底失败 · wisburg 工具回退跳摘要 · 单篇摘要失败 · 回核缓存失效失败 | yfinance:149/292 · wisburg:343/376/209 · [verifier.py:573](../../src/committee/retrieval_plan/verifier.py) | — | **log** 〔**✅ PR3 2026-09-18 已补痕**·分支 `auto/BK.2-M2b`·yfinance 坏值回退 → 便条 `price_bar_stale_fallback`；研报工具回退 / 摘要失败 → 读法 `wisburg_partial_fallback`（与回核去重）；AV 兜底失败 → `leg_missing` 已报；回核缓存失效 → 不接（生产走不到）〕 |
### 2.2 seg2–7 分析 / 辩论 / 投票（9 处）

| # | 降级点 | 位置 | 今天留痕 | 层 |
|---|---|---|---|---|
| 23 | analyst LLM 失败 → 兜底报告 | [base.py:1036](../../src/committee/agents/base.py) · [validation.py:254](../../src/committee/schemas/validation.py) | headline 含「兜底模式」+ `conviction=DATA_INSUFFICIENT` | state·trace |
| 24 | 软 schema 降级（sanitized / fallback 三档） | [validation.py:275](../../src/committee/schemas/validation.py) | 档位**只作返回值、未落 state** | **log** 〔**✅ M4.1 2026-09-21 已补痕**·分支 `auto/BK.2-M4`·便条 `report_sanitized`（「洗过才过关」半支；「兜底」半支早由 #23 的 `analyst_fallback_report` 读法报）·量基线 218 份历史报告 6 份洗过、23 跑 3 跑（13%）→ 进用户面〕 |
| 25 | analyst 扩写失败 → 保留原报告 | [base.py:1100](../../src/committee/agents/base.py) | — | **log** 〔✅ BK.6 2026-09-22 便条 `analyst_expand_failed`（在册 0 次扩写调用·无历史基线）〕 |
| 26 | 续写解析失败 → 截断 | [base.py:685/693](../../src/committee/agents/base.py) | `truncated_at_chunk` | state·trace |
| 27 | 分诊 reject → 报告置 None | `rejected_roles` | `rejected_roles` | state·trace |
| 28 | 辩论 turn 解析失败 → 占位（2 处） | [base.py:1239/1301](../../src/committee/agents/base.py) | content 文本「已降级」 | state 弱·trace |
| 29 | 投票解析失败 → 兜底 | [base.py:1378](../../src/committee/agents/base.py) | 兜底票 `reasoning` 写「投票解析失败」 | 归档 ✅ 〔**✅ M1 2026-09-15 只加读法**·汇总侧派生 `vote_parse_failed`·生产代码零改动〕 |
| 30 | 工具调用 JSON 解析失败 | [base.py:321](../../src/committee/agents/base.py) | — | **log** 〔**⚪ M4.5 2026-09-21 核实：由 #23 承接、不接码**——分析师节点对工具循环无外层重试（一次调用即 except → 兜底报告），解析器的 ValueError 原样 raise、不吞不丢，兜底报告由 `analyst_fallback_report` 读法报；登记表 M1.5 已定 `base.py:_extract` = exempt。执行计划 M4-5 原问「是不是重试中间态」：**不是**，它是链头、链尾已报〕 |
| 31 | MCP run 预算耗尽 → 研报腿失败 | [run_budget.py:128](../../src/committee/mcp_client/run_budget.py) | — | **log** |

### 2.3 seg8–9 pass0 / 决策 / 风控（19 处）

| # | 降级点 | 位置 | 今天留痕 | 层 |
|---|---|---|---|---|
| 32 | Pass0 LLM/解析/校验失败 → None（3 处） | [pass0_node.py:100/119/133](../../src/committee/agents/pass0_node.py) | `pass0_result=None` | state 弱 |
| 33 | ds_researcher 失败 → None（3 处） | [pass0_parallel.py:101/121/134](../../src/committee/agents/pass0_parallel.py) | `ds_researcher_result=None` | state 弱 |
| 34 | ds_debate 失败 → None（3 处） | [pass0_parallel.py:181/201/214](../../src/committee/agents/pass0_parallel.py) | `ds_debate_result=None` | state 弱 |
| 35 | ds_merge 两个都失败 | [pass0_parallel.py:278](../../src/committee/agents/pass0_parallel.py) | 同上 | state 弱 |
| 36 | 🔴 **决策前事实核验失败 → 空 findings** | [base.py:1870](../../src/committee/agents/base.py) | — | **log** ⚠️ |
| 37 | 核验跳过非法 finding | [base.py:1885](../../src/committee/agents/base.py) | — | **log** 〔**✅ M3.1 2026-09-18 已补痕**·分支 `auto/BK.2-M3`·便条 `verification_finding_dropped`·实为两支（非 dict / 校验不过）一次核验一条；历史 25 次核验零阳性〕 |
| 38 | 决策大纲解析/校验/形状/长度失败 → 单段（4 处） | [base.py:3141/3147/3152/3160](../../src/committee/agents/base.py) | — | **log** 〔**✅ P0 批 2026-09-17 已补痕**·合 main `3da9a61`·码 `decision_outline_fallback`·实为五支（成功路径上的装配校验也算）·旧存档另有「段数偏少 = 疑似」读法〕 |
| 39 | 段落正文空 → 插占位 | [base.py:3621](../../src/committee/agents/base.py) | `thesis_sections[].body` 写「核心观点待补充」 | 归档 ✅ 〔**✅ M1 2026-09-15 只加读法**·汇总侧派生 `thesis_section_placeholder`·生产代码零改动〕 |
| 40 | 价位 level 全被抹 | [base.py:3767](../../src/committee/agents/base.py) | `prose_gate_status="degraded"`（**无消费方**，见代码注释） | state 弱 |
| 41 | 🔴 **誊写核查跳过（fail-open）** | [base.py:2777](../../src/committee/agents/base.py) | `enforcement_log[rule=ai-transcription-check]` | state·trace ✅ 〔**🔴 2026-09-15 订正**：原记 **log** 有误 —— 该处**一直在写**一条结构化记录，只是没有消费面；BK.2 提前批只加了读法，核查代码零改动。见 §3 结论 2 订正〕 |
| 42 | 复核员缺席 / 调用失败 → 维持硬拦 | [mismatch_review.py:275/289](../../src/committee/facts/mismatch_review.py) | `verdict="skipped"` + `error` | state·trace |
| 43 | 🔴 **EXEC-FLOOR 信号算不出 → 按不触发放行** | [risk_gate.py:534](../../src/committee/agents/risk_gate.py) | — | **log** ⚠️ |
| 44 | 风控回应失败/非法 → 跳过（3 处） | [risk_gate.py:624/633/687](../../src/committee/agents/risk_gate.py) | — | **log** 〔**✅ M3.3 2026-09-18 已补痕**·分支 `auto/BK.2-M3`·便条 `risk_response_missing` 在回应节点当场记（调用失败 / 漏答两支合一码，结构非法 · 条目非法 · 未知 id 三种丢法在 detail 里计数）；原计划「只加读法」不成立——节点失败与没跑到在归档里一样、现场事件不进归档；历史 50 份有需回应 finding 的归档全部答齐〕 |
| 45 | 外源册/引用条目畸形 → 跳过（2 处） | [base.py:3106](../../src/committee/agents/base.py) · [verify.py:175](../../src/committee/facts/verify.py) | — | **log** 〔**✅ P0 批 2026-09-17 已补痕**·合 main `3da9a61`·码 `reference_entry_dropped`·base.py 实为三支；verify.py 那支核实生产零调用、登记改不算降级〕 |
| 46 | 列表超上限 → 截断 | [base.py:3202](../../src/committee/agents/base.py) | — | **log** 〔**✅ P0 批 2026-09-17 已补痕**·合 main `3da9a61`·码 `decision_list_truncated`·留痕带被截条目原文前缀〕 |
| 47 | 价格闸早停 | `price_unavailable` | `price_unavailable` + 早停结论 | state·trace·**cli** |

### 2.4 跨段（8 处）

| # | 降级点 | 位置 | 今天留痕 | 层 |
|---|---|---|---|---|
| 48 | 归档 JSON 导出失败（DB 记录保住） | [archive/service.py:97](../../src/committee/archive/service.py) | — | **log** |
| 49 | 末段 archive-from-final 写失败 | [graph.py:818](../../src/committee/graph.py) | — | **log** 〔**⚪ M4.3 2026-09-21 用户面小修已做·不开新出口**（用户 09-16 裁 5）：图外、state 定稿后无出口；cli 末段 archive 为 None 时印「归档没写成、断点仍在」；登记表翻 exempt 并写重评时点（归档写入挪进图内即重评）〕 |
| 50 | 缓存 get/set 失败 → 当 miss（2 处·`debug` 级） | [builder.py:440/463](../../src/committee/common_context/builder.py) | — | **debug** |
| 51 | 无 adapter → 跳过缓存 | [adapters.py:120](../../src/committee/facts/adapters.py) | — | **log** |
| 52 | 算不出钱 / 价目表过期 | token_usage | `partial_cost` / `unpriced_models` / `stale_price_models` | state·trace·归档·**cli** |
| 53 | 配置漂移 / 未登记键（BJ.3/BJ.5） | config_explain | 快照 + trace 头 ⚠️ 块 | trace·归档 |

### 2.5 补齐（2026-09-15·表与登记表对账查出）

> **怎么查出来的**（可复现）：拿 [`DEGRADATION_SITES` 登记表](../../src/committee/degradation.py) 与本表**对账** ——
> 登记为 `code:` / `pending:`（= 真降级）的键里，**整个函数在本表一行都没点到**的，就是本表漏的。
> 比对在 `a53b196`（本盘点落地那笔）上做，与表内行号同一版本；这 10 个文件自那以后**一字未改**（已 `git diff` 核）。
> ⚠️ 两处易错已踩过：① 表里用**简称**（`yfinance:149` 指 `yfinance_source.py`、`wisburg:` 同理）——
> 别名不归一会多报 4 条；② 表里行号与实际调用点**有偏移**（如 pass0 记 100/119/133、实际 106/124/130）——
> 按行精确匹配会多报 40+ 条，**必须按函数区间匹配**。

| # | 降级点 | 位置 | 今天留痕 | 层 |
|---|---|---|---|---|
| 54 | 名录拉取失败（美股 NASDAQ · A股分页） | [nasdaq.py:99](../../src/committee/security_registry/providers/nasdaq.py) · [tushare.py:92](../../src/committee/security_registry/providers/tushare.py) | — | **log** 〔**✅ PR3 2026-09-18 已补痕**·分支 `auto/BK.2-M2b`·由 `registry_market_fetch_failed` 便条带出市场与原因〕 |
| 55 | 名录预热失败（读现状 / 刷新异常·2 处） | [service.py:279/296](../../src/committee/security_registry/service.py) | — | **log** 〔**⚪ 用户 2026-09-17 裁 ⑤「不接」**（预热只在跑批外跑、便条在跑批作用域外当场作废）·登记表 `service.py:prewarm` 早已 exempt；**本行 M4 收口 2026-09-21 才翻**，此前表未跟上〕 |
| 56 | 绑工具失败 → 退回无工具调用（这次用不上检索） | [agent_loop.py:265](../../src/committee/tools/agent_loop.py) | — | **log** 〔**✅ P0 批 2026-09-17 已补痕**·合 main `3da9a61`·码 `tool_loop_no_tools`〕 |
| 57 | 工具循环异常 / 到上限强制收尾 / 收尾也失败（4 处） | [agent_loop.py:289/396/404/423](../../src/committee/tools/agent_loop.py) | — | **log** 〔**✅ P0 批 2026-09-17 已补痕**·合 main `3da9a61`·首轮失败那支同码 `tool_loop_no_tools`；撞上限强制收尾按用户裁 G **不发**（设计内每跑上限·上限调大后重评）；非首轮失败 / 收尾也失败两支会抛、不静默〕 |
| 58 | 单份报告分诊失败 → 该报告这轮没被审 | [node.py:192](../../src/committee/triage/node.py) | 判定写成 `warning` + 一条 `triage error:` 备注 | state·trace ✅ 〔**🔴 2026-09-15 订正**：原记「只写日志」**有误** —— 它一直把判定写成 warning 并附一条备注、也进归档，**只是没有消费面**（同 #41 形态）。⇒ 生产者零改动，只在汇总侧加读法〕 |
| 59 | 🔴 **C 类规则跑不起来 → 判定与「C 类通过」无法区分** | [rules_c.py:121](../../src/committee/triage/rules_c.py) | `enforcement_log[rule=triage-c-class]` | state·trace ✅ 〔**2026-09-15 已补痕**·放行判定一字未改〕 |
| 60 | E2 规则跑不起来 → 本跑没有 E2 记录 | [rules_e.py:215](../../src/committee/triage/rules_e.py) | 部分（E1 也判不合格时，E3 会带一句「E2 没跑成」） | **log** 〔**🔴 2026-09-15 降档·原标 🔴 是我判早了**：追到底后**不成立** —— E 类整族目前是**观察期、只记日志**（[node.py](../../src/committee/triage/node.py) 里 E 类结果既不改判定也不进 notes），所以 E2 没跑成**不会**把「本该警告」变成「通过」，只是少了一个观察数据点。且 E1 判不合格那条分支里，[E3 会写明「E2 没跑成、无法汇总」](../../src/committee/triage/rules_e.py)。⇒ 归「少记一笔账」的普通批〕 |
| 61 | pass0 结构校验异常 → 跳过校验，坏结构可流向下游 | [pass0_validator.py:22](../../src/committee/triage/pass0_validator.py) | — | **log** |
| 62 | 重跑派发失败 → 维持原报告（不显示它被判过不合格） | [rework.py:98](../../src/committee/triage/rework.py) | — | **log** 〔**✅ M4.2 2026-09-21 已补痕**·便条 `rework_dispatch_failed`（一次派发一条、detail 逐角色）。🔴 §3.1 原判「假待办·`analyst_rejected` 已报」**说过头**：那条读法只报「打回且没能补救」这个**结果**，盖不住「重跑根本没派出去」这个**原因**（与「重跑了仍不合格」产物一样、`rework_counts` 照加）；执行计划 M4-2 与登记表 `pending` 本就按待补写 ⇒ 改判真待办并做（照 #16 先例）〕 |
| 63 | 待查证清单条目没写事项 / 非 dict → 装配前被过滤（到不了 #304 的逐项校验） | [base.py:_build_outline](../../src/committee/agents/base.py) | — | 无（连日志都没有） 〔**2026-09-18 M3.2 新增即做**·分支 `auto/BK.2-M3`·便条 `verify_checklist_item_dropped`（同码另一支 = #304 里事项本身校验不过被扔）；执行计划 09-16 说「登记为新行随 M3 处理」但一直没加进表，本批补上；历史 27 次大纲零阳性〕 |

**🔴 #59 已逐行核实（R5：先读消费方再下判断）**：[node.py:83](../../src/committee/triage/node.py) 写的是
`c_failed = (c_results is not None and any(... fail ...))` —— C 类**跑不起来时返回空**，
于是 `c_failed` 为假、**不产生任何 warning**，判定读起来与「C 类全过」**一模一样**。
⇒ 与本次提前批修掉的三处是**同一个形态**。

**✅ #60 已追到底（2026-09-15·原标 🟡 现判「不是同一个形态」）**：上一版只核到「失败时没有 E2 条目、
而『未触发』会明写两条 `pass`」就停了。追完下游的结论是**它不成立**：
① **E 类整族目前是观察期、只记日志** —— E 类结果既不改 `verdict`、也不进 `notes`，
只在 [node.py](../../src/committee/triage/node.py) 里走一句 `log.info`；
⇒ E2 没跑成**不会**把「本该警告」变成「通过」，它本来就不产生警告。
② E1 判不合格那条分支里，`run_e3` 会返回带理由的结果（「E2 没跑成、无法汇总」），**那一支其实有痕**。
⇒ 降为普通批的「少记一笔账」。**这是把「先证设计再判 bug」走完的结果 —— 上一版的 🔴 是判早了。**

**其余 5 条（#54 #55 #56 #57 #61 #62）的档位仍未逐条核**，只照登记表原话誊录，别当已判定。
（原句把 #58 也列在内 —— 它已于 2026-09-15 核实并订正为「有记录、无人读」，见上表。）

> **不算漏的一条**：`planner.py:plan_retrieval`（出计划的四条失败路径）在登记表里没被本表按文件点到，
> 但 **#10–13 已从调用方 `context_node` 那一侧覆盖**同一批降级 —— 属重复视角，不另立行。

---

## 3. 统计与三个结论

| 分类 | 数 |
|---|---|
| 真降级点 | **58** |
| ├ 有结构化留痕（state 字段可派生） | **25** |
| └ **只有日志 / 无痕** | **33** |
| 其中 🔴 安全型静默放行 | **3** |
| 重试中间态（不算降级） | 29 |
| 整跑崩 / BaseException 上抛（会炸，不静默） | 6 |
| 信息性告警 | 12 |

> ## 🔴 3.0 全表重算（2026-09-15·用户裁「`state 弱` 也算无痕」）
>
> **下面 §3 那张表是 point-in-time、正文不改；前向事实以本节为准。**
>
> **重算口径（写出来，别再靠印象）**：「有痕」= 表里「留痕层」那栏出现 `trace` / `cli` / `归档`
> 之一（= 排查报告 / 用户面 / 归档里**真的看得见**）。**`state 弱` 不算有痕**（用户 2026-09-15 裁）——
> 它只是某个字段退成空值，没人读就等于没有。
>
> | 项 | 数 | 怎么来的 |
> |---|---|---|
> | 表内**行数** | **62** | 53 原有 + §2.5 补齐 9（编号 1–62） |
> | 新口径**无痕行** | **24** | 留痕层不含 trace/cli/归档〔2026-09-15 由 44 降 2：#58 #59 已补痕转有痕；**M1 再降 3：#15 #29 #39 加了读法转有痕**；**P0 批 2026-09-17 再降 6：#9 #38 #45 #46 #56 #57 已补痕**（39 → 33）；**PR3 2026-09-18 再降 9：#4 #5 #6 #7 #8 #16 #18 #22 #54**（33 → 24）〕 |
> | 已做 | **23** | #36 #41 #43（提前批）+ **#58 #59**（分诊批）+ **#15 #29 #39**（M1·只加读法）+ **#9 #38 #45 #46 #56 #57**（P0 批·PR [#303](https://github.com/JunoChenZt/subagent-for-investment/pull/303)）+ **#4 #5 #6 #7 #8 #16 #18 #22 #54**（PR3·[证据](../observations/bk2-m2b-20260918/FINDINGS.md)） |
> | **余待补痕** | **40 行** → **🔴 清账后 25 行**（见 §3.1）→ **M1 后余 37 行·真待补仍 24**（M1 做的是 🟡 档，不在 24 里）→ **P0 批后余 31 行·真待补 18**（P0 的 6 行全在那 24 里）→ **PR3 后余 22 行·真待补 10** → **M3 后余 20 行·真待补 8**（M3 2026-09-18：#37 #44 翻已做；#63 新增即做、不入计数；登记表待补痕 9 → **6** 点）→ **M4 后真待补 3（2026-09-21·首次写出明细）**：⚠️ M3 之前的「8」是链式减法、从未列明细；本批按规则逐行枚举（无痕 ∧ 未做 ∧ 非假待办 / 不算 / 裁不做）得 **#17 #20 #24 #25 #30 #49 #55 #62 = 8**（恰与链式数相等，但其中 #62 是按登记表 `pending` 算入、与 §3.1 旧判矛盾；#55 早已裁不接、表未翻）。M4 处置：#24 #62 补痕 ✅ · #30 承接 ⚪ · #49 用户面小修 ⚪ · #55 翻裁不接 ⚪ ⇒ **余 #17 #20 #25 三行**（登记表待补痕 6 → **4** 点〔🔴 **09-21 落账实跑订正：实为 5 点** —— 下列四点之外，`graph.py:_write_final_archive` 仍是 `pending`：M4.3 计划的翻 `exempt:` 没进合并代码；去处见 backlog BK〕〔✅ M4-fix [#309](https://github.com/JunoChenZt/subagent-for-investment/pull/309) 合 main `15443b8` 后补上 ⇒ **4 点**·合并后实跑 40 / 4 / 21〕：`_build_context_inner` / `apply_cache_invalidation` / `_alpha_vantage_fetch` / `run_tool_agent`，均属一键多支 / 生产不可达 / 裁 G，键粒度归 BK.3）〔✅ BK.3 [#310](https://github.com/JunoChenZt/subagent-for-investment/pull/310) 合 main `dea94eb`（2026-09-22）：登记表改**站级键**、待补痕改按**站点**口径 = **12 站**（旧 4 点各留 1 站 + 拆出后首次独立记账 8 站；合并后实跑 82 / 12 / 50 共 144）—— 与「N 点」（函数级键）单位不同、不互相推导；盘点真待补仍 3 行 #17 #20 #25〕〔✅ BK.6（2026-09-22·拆解 [BK.6-decomposition](BK.6-decomposition.md)）：**盘点真待补 3 → 0**（#25 便条 `analyst_expand_failed` · #17 #20 判已覆盖——后果由 `leg_missing` 派生报）；**登记表待补 7 → 0 站**（4 站便条 · 1 站只加读法 `hallucinated_refs_stripped` · 2 站 exempt 写明重评时点）；合并后账面见 backlog BK〕〔✅ **2026-09-22 BK CLOSED**（close-by-completion·两本账归零·记账项迁观察点表 [O-BK-01](../observations/should_update_observations.md)）〕〔✅ BK.5 [#311](https://github.com/JunoChenZt/subagent-for-investment/pull/311) 合 main `d4d3891`（2026-09-22）：意图被拒收 / 丢弃同族 5 站合一码 `plan_intent_dropped` 翻 code ⇒ 待补 **12 → 7 站**（合并后实跑 87 / 7 / 51 共 145）〕（**怎么数的**：本批 9 行里 8 行在那 18 里、18 − 8 = 10；#16 原被判假待办、不在 18 里，本批改判后直接做掉。**另一份同口径的数**：登记表按代码点数，`lint_degradation_registry` 实跑 = 待补痕 **9** 点，两者单位不同〔行 vs 函数〕、不互相推导） | 行内自注代码点合计 60 |
>
> 🔴 **2026-09-16 M1.5 补一条口径警告**：本表「留痕层」栏写的是**当年记的**，
> 与代码对账后 **32 个登记点里有 9 处不符**（含一条 `code:` 是**死派生** —— 派生读的键
> 全仓无生产者、从落地起恒不触发）。⇒ **本表任何一格都不许单独当证据用**，
> 承重判断必须开代码核。逐处订正见 [M2–M4 计划 §2](BK2-M2-M4-plan-2026-09-16.md) 与
> [M1.5 证据](../observations/bk2-m15-20260916/FINDINGS.md)。
>
> 🔴 **两处对账缺口 —— ① 已补齐，② 仍无解**：
>
> 1. ~~**表格少 5 行**~~ 〔**2026-09-15 已查并补齐·原假设不成立**〕：按小节标题算差 5 行（22/9/19/8=58 vs 实际 22/9/16/6=53），
>    但**照着「§2.3 / §2.4 少了 5 行」去找是找不到的** —— 真正的漏项**不在那两节**。
>    改用**表与 [登记表](../../src/committee/degradation.py) 对账**（登记为真降级、而整个函数在表里一行都没点到）
>    查出 **10 个登记键无覆盖**，其中 9 个立为新行（#54–62，见 §2.5）、1 个属重复视角不另立。
>    ⇒ **小节标题那几个数仍然对不上，且已知不是"少 5 行"那么简单，不再据它推断**。
> 2. **「58 / 33」无法从表里复算**（按行 53 / 按行内自注代码点 71，两个都不是 58）。
>    §3 的 58 / 33 出自 §1.1 那轮人工分类（105 条逐条读），与表格是两份数据、**从未对过账**。**至今无解，保留记录。**
>
> 📌 **元教训（第四次了）**：§1.2 订正过一次数（44→），2026-09-15 订正过「无痕」判据、订正过「余 30 处」、
> 本次又因补齐 9 行把 33 改成 42。四次根因同一个：**承重数字没有写出「怎么数的、从哪份数据数的」**。
> ⇒ 本节起，凡改这些数**必须同时更新上表的「怎么来的」栏**；口径变了就是新数，不许沿用旧数。

> ## 🔴 3.1 余 40 行清账（2026-09-15·用户裁「剩下 40 行也做」后的开工前核对）
>
> **做法**：逐行打开代码看**失败之后留下了什么**，再对现有派生。**不认登记表的一面之词**
> —— 前两批逐条核了 3 处、**3 处全和登记表写的不一样**，本轮再次验证这个命中率。
>
> **结果：40 行里只有 25 行是真待办。**
>
> | 档 | 行数 | 明细 |
> |---|---|---|
> | 🟢 **假待办（汇总早就在报）** | **9** | #14 #16 #32 #33 #34 #35 #40 #61 #62 |
> | 🟡 **有记录、只差读法**（生产代码零改动） | **3** | #15 #29 #39 〔**✅ M1 已做·合 main `3f1bf58`**（PR #299·2026-09-16）·证据 [bk2-m1](../observations/bk2-m1-20260915/FINDINGS.md)〕 |
> | ⚪ **应判不算降级** | **3** | #31 #50 #51 |
> | 🔧 **真待补** | **25 → 24**〔#21 已由 M0 接线穿通〕 | 其余 |
>
> **🟢 9 行为什么是假待办**（逐条核过，不是推断）：
> - **#32 #33 #34 #35 #61** —— 都以 `pass0_result` / `ds_*_result` 变空收场，
>   而 [`_pass0_events`](../../src/committee/degradation.py) 早就在报「这一步没出结果，决策是在缺这份材料的情况下做的」。
>   #61（pass0 结构校验异常）是 #32 的上游，None 一路流到同一个字段。
> - **#40** 价位被抹 → `prose_gate_degraded` 已报。
> - ~~**#16** 认不出源跳过这条腿 → 资料夹里没这个键 → 腿的 `arrived=False` → `leg_missing` 已报。~~ 🔴 **2026-09-18 订正：不成立**——09-04 起腿清单收窄成「真跑得起来的腿」，被跳过的那条不进清单，`leg_missing` 接不住。改判真待办，PR3 已补痕（[证据](../observations/bk2-m2b-20260918/FINDINGS.md) §2）。
> - **#14** 校验层全灭 → 退兜底路由，**同一事件 #11 已从调用方覆盖**（重复视角，同 planner 那条）。
> - ~~**#62** 重跑派发失败 → 报告维持「被打回」→ `rejected_roles` → `analyst_rejected` 已报
>   （那条派生的原话就是「被质量审核打回**且没能补救**」）。~~ 🔴 **2026-09-21 M4 订正：说过头**——那条读法只报结果（打回且没补救），盖不住原因（重跑根本没派出去 vs 重跑了仍不合格，产物一样）。改判真待办，M4.2 已补痕。
>
> **🟡 3 行为什么便宜**：失败时**已经写下了可识别的东西**，只是没人读 —— 同 #41 / #58 / #29 的老形态：
> - **#15** 取数超封顶 → 往路由里写了 `__budget_capped__` 键，而
>   [`ROUTING_DEGRADED_KEYS`](../../src/committee/degradation.py) 里**没有它**（加一条映射即可）。
> - **#29** 投票解析失败 → 兜底票的理由字段写着「投票解析失败」字样，进归档。
> - **#39** 段落正文空 → 正文被写成「（某某：核心观点待补充）」，进归档。
>
> **⚪ 3 行为什么不算降级**：
> - **#31** 是**配置值校验告警**（预算填了 0 或负数 → 改用默认值），不是运行期退路。
> - **#50 #51** 只影响**缓存命中**（当作没命中、跳过缓存）⇒ 影响速度不影响正确性。
>
> ⚠️ **两条附带发现**：
> 1. **#24 只覆盖了一半** —— 报告降级三档里「兜底」那档由 `analyst_fallback_report` 报了，
>    **「清洗过」那档没人报**。故它留在真待办里，但范围应收窄。
> 2. **表里 `base.py` / `risk_gate.py` 的行号已漂** —— 提前批与分诊批改过这两个文件
>    （如 #44 记的 624/633/687，实际已到 645/654/708 一带）。**按行号找会找错地方，按函数名找。**
>
> 📌 **本轮再次印证**：「有没有留痕」必须**打开代码看失败后留下了什么**，
> 登记表与盘点表的措辞都只是线索。命中率至今 **4/4**（#41 · #58 · #60 · 本轮 9+3 行）。

**结论 1 —— 汇总是够本的**：25 处已有结构化留痕，**不改任何判定就能派生出一张清单**，覆盖 43%。这 25 处正是 BK.1 的推导源。

> **🔴 2026-09-15 订正（BK.2 提前批开工前核对）**：下面这段把 #41 归进「33 处无痕」是**错的**。实地看过代码：#41 早就在往 `enforcement_log` 里写一条 `skipped_fail_open`，**只是没有任何消费面**—— 属「有结构化记录、无人读」，不属「只写日志」。⇒ 真·无痕数应为 **32 处**（其中 🔴 两处：#36 #43）；#41 的修法因此是三处里最省的：**核查那段代码一个字未动**，只在汇总侧加派生。
> 教训同 §1.2：**「有没有留痕」不能只看日志行，要看那条记录有没有人读** —— 写了没人读，在产物上与没写完全一样。

**结论 2 —— 补痕要分两批**〔**🔴 2026-09-15 数字已作废·见 §3.0**：新口径下是 **44 行无痕**（含 §2.5 补齐的 9 行）、已做 3 行、**余 42 行**〕：33 处无痕里，30 处是"少记一笔账"（BK.2 普通批）；**3 处是"把没检查说成检查过了"**（#36 决策核验失败退空清单 · #41 誊写核查 fail-open · #43 EXEC-FLOOR 信号算不出按不触发）。这三条建议**单独提前处理**，因为它们的后果不是"信息少了"，而是**产物在撒谎**。⚠️ 但它们都在风控/核查路径上，碰它们要极小心（只加留痕、绝不改判定）——**逐点请用户裁**。

**结论 3 —— 设计与代码有一处分叉**：[S2 §6.2](../roadmap/S2.md) 写「全 8 analyst 都 fallback → degraded run flag」，代码里**没有这个 flag**（只有 [risk_gate.py:302](../../src/committee/agents/risk_gate.py) RW-3 的 quorum 守卫在存活数不足时不断言"committee 收敛"）。⇒ 设计表该行标注为"未实现，由 RW-3 部分承接"（BK.4 回填）。

## 4. 交给 BK.1 的推导源（25 项）

| 推导码 | 读什么 | 何时响 | 已知阳性归档（R6：从 `origin/main` 读） |
|---|---|---|---|
| `classify_degraded` | `query_classification.source != "llm"` | 分类走了名录/regex/默认 | 待补（历史归档多为 `llm`） |
| `plan_fallback_routing` | `common_context.source_routing` 含降级键 | 规划员四种失败任一 | [ctx-legs-pr270-e2e-20260904](../observations/ctx-legs-pr270-e2e-20260904/FINDINGS.md) O1「规划员 2/2 超时」 |
| `leg_verification_degraded` | `legs[].verification_status == "degraded"` | 回核判腿降级 | 待补 |
| `leg_missing` | 计划有腿、资料夹无键 | 取数缺腿 | BV 立账那跑 |
| `analyst_fallback_report` | 报告 headline 含「兜底模式」/ `conviction=DATA_INSUFFICIENT` | 分析师 LLM 失败 | 待补 |
| `analyst_truncated` | `truncated_at_chunk is not None` | 续写解析失败 | 待补 |
| `analyst_rejected` | `rejected_roles` 非空 | 分诊 reject | 历史多跑有 |
| `debate_placeholder` | turn.content 含「解析失败，已降级」 | 辩论解析失败 | 待补 |
| `debate_truncated` | `DebateTurn.truncated_at_chunk` | 辩论截断 | 待补 |
| `pass0_missing` / `ds_researcher_missing` / `ds_debate_missing` | 对应 state 键为 None | 超时/失败 | 待补 |
| `review_skipped` | `ReviewResult.verdict == "skipped"` | 复核员缺席 | [cred-1-g5-e2e-20260910](../observations/cred-1-g5-e2e-20260910/FINDINGS.md)（复核员 0 次调用） |
| `prose_gate_degraded` | `final_decision.prose_gate_status == "degraded"` | 价位全抹 | 待补 |
| `price_unavailable` | `price_unavailable is True` | 价格闸早停 | 历史有 |
| `cost_partial` / `cost_unpriced` / `cost_stale_price` | `token_usage.*` | 算不出钱/价目表过期 | [bj-cfg-snapshot-e2e-20260914](../observations/bj-cfg-snapshot-e2e-20260914/FINDINGS.md)（`stale_price_models`）|
| `config_drift` / `config_unregistered` | BJ.3 快照比对 | 配置漂移/拼错键 | BJ.3 单测 |

⚠️ **「待补」不是"没有"，是"本盘点没去翻 109 份归档逐个找阳性"** —— BK.1 落地时每条至少要有一个真实或合成阳性样本证明它会响（坑扫描①）。

## 5. 本盘点没做的（如实）

- **没扫 `log.info` / `log.debug` 里的降级**（已知至少缓存那 2 处）—— 口径写在 §1.1，BK.3 守护同样只认 warning/error。
- **没逐条翻 109 份 tracked 归档找阳性样本** —— 留给 BK.1。
- **没核"下游消费面会不会因看见而改行为"的全部路径**：只确认了 `source_routing` 属资料夹、是分析师提示词原料（⇒ 补痕不走它，坑扫描②）；其余槽位的消费面在 BK.2 逐点裁时补。
