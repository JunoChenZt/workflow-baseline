# S2 收口 G1 · 坑表 S2 结束审视（2026-09-28）

> **✅ 用户 2026-09-28 裁：三项全按建议（见 §3）；坑表已按裁决落地 23 条改动（保持不动的 13 条里 6 条只加过期事实订正），原文与历史原因全部保留。**
>
> 初版为只出建议、坑表未改。 改状态 / 退役按 [坑表维护协议 §3.10](../governance/workflow/09-known-pitfalls.md) 须用户确认、PR 描述写明替代证据。
> 核对基准：main `47c62c6`（工作树 = main）。§3.3–3.9 逐条由三路只读核查并行完成，最重的四条结论（§3.3 缓存没接管道 / §3.5 风控回应只警告 / §3.7 D1 已有牙 / §3.8 质检门无挂标率检查）主会话又逐一开代码复核过。

## 0. 大白话导读

**先纠一个前提**：拆解里写的「逐条审视怀疑过时（stale_candidate）的坑」——坑表里**一条都没有**，唯一命中的是格式说明里的示例。所以本次改为审视**和 S2 各子阶段绑定的 30 条坑**（§3.3–3.9），看它们的状态标记还对不对；§3.2 那 34 条通用教训是跨阶段的工作方法，**整体保留**，只抽查了点名的代码符号仍在。

**结论**：30 条里只有 13 条可以原样留着；其余 17 条要么该升级成「已有守护」、要么该退役、要么文字已经和现实对不上。

| 处置 | 条数 | 要不要您裁 |
|---|---:|---|
| 保持不变（部分要订正过期事实） | 13 | 不用 |
| 改成「已有守护（mitigated）」 | 7 | 不用（维护协议允许的操作），但要在 PR 里写明守护是什么 |
| **建议退役** | 8 | **要** |
| **文字和现实相反，必须改写** | 1 | **要**（改写后的口径） |
| **去留待定** | 1 | **要** |

**最要紧的一条**：「基金经理对风控意见的回应是必填、不可绕过」——**系统并不具备这个保证**。真实设计是「要回应，但漏答或调用失败只记一笔、照常放行」，而且是当年有意这么选的。坑表写着一个不存在的保证，比没写更糟。

**顺带的流程发现**：
- 这两节（§3.6 / §3.7）在 S2.2 交接时**根本没被审过**；S2.3 交接也只一笔带过 ⇒ 这些状态从立下到今天没人动过。
- 反过来，两份交接报告里都写着「维持 active」的两条坑（F3 规则对中文 100% 误报、E2「报告太短」判得过严）**从来没进过坑表**。它们实际是校准债，已在收口计划的「移交 S3 清单」里。

---

## 1. 逐条审视

图例：**保持** = 状态不动 · **→mitigated** = 改成已有守护 · **退役** = 建议 `retired_after_phase_review`（须裁）· **改写** / **待裁** = 须裁。

### §3.3 S2.1 召回层

| 条目 | 现状 | 证据 | 建议 | 过期事实 |
|---|---|---|---|---|
| 🔴[mitigated] 问题分类 AI 必带兜底 | 仍在且更强：AI → 名录 → regex → 主题兜底，永不抛错 | [classifier.py:478](../../src/committee/query_class/classifier.py) · [test_query_class_classifier.py:372](../../tests/test_query_class_classifier.py) | 保持 | macro_event 已改名 THEMATIC；是 4 条路径不是 2 层 |
| 🔴[mitigated] 任一数据源失败不拖累其他 | 仍在，另加 12 秒总时限 | [builder.py:587](../../src/committee/common_context/builder.py) · [test_common_context_dispatch.py:134](../../tests/test_common_context_dispatch.py) | 保持 | 数据源是 **5** 个不是 4 个 |
| 🔴[active] 缓存库 SQLite WAL，改前先讨论 | WAL 设置在，但**缓存从没接进主流程**，只在测试里用 | [context_node.py:506](../../src/committee/agents/context_node.py) 自述「两条路都不走缓存」；backlog P 已按此关闭 | **退役**（重开条件：缓存真接进主流程那天） | — |
| 🟡[active] 来源标记放资料末尾，不放提示词开头 | 仍成立 | [base.py:1164](../../src/committee/agents/base.py) | 保持（**没有测试守位置**，不够格 mitigated） | — |
| 🟢[active] 缓存命中率 > 60% | S2 口径下量不出（数据缓存没接；提示词缓存只做过一次探针、开关默认关） | [探针](ag-cache-meter-probe/EVIDENCE.md) · [S3.md](../roadmap/S3.md) §6.1 COST-FM-PREFIX | **退役**（跟进已移 S3） | 原文没说是哪种缓存（推断·未证实） |

### §3.4 S2.1 软 schema + 分诊员

| 条目 | 现状 | 证据 | 建议 | 过期事实 |
|---|---|---|---|---|
| 🔴[mitigated] 格式降级最后必有兜底报告 | 仍在，必定返回一份报告 | [validation.py:271](../../src/committee/schemas/validation.py) · [test_validation.py:242](../../tests/test_validation.py) | 保持 | 代码是 **3 档**不是 4 层；没有 `full_fallback` 这个名字 |
| 🔴[mitigated] 分诊 AI 失败 → 跳过 C 类与 E2/E3 | 仍在 | [rules_c.py:96](../../src/committee/triage/rules_c.py) · [test_triage.py:382](../../tests/test_triage.py) | 保持 | — |
| 🔴[mitigated] A1.2 动工前讨论清 A/B/C 规则 | 一次性开工手续，早已做完 | 条目自带「A1.2 DONE」 | **退役**（不是会复发的坑） | — |
| 🟢[active] 格式降级率作 S3 决策输入 | 已有计量（09-21 基线 218 份报告里 6 份被清洗） | [degradation.py:1032](../../src/committee/degradation.py) · 消费方 [S3.md:131](../roadmap/S3.md) | 保持 | — |

### §3.5 S2.1 Risk Gate

| 条目 | 现状 | 证据 | 建议 | 过期事实 |
|---|---|---|---|---|
| 🔴[mitigated] 核心风险字段换结构，样例全更新 | 迁移完成，有旧存档回放守护 | [test_pr8c_e2e.py:202](../../tests/test_pr8c_e2e.py) | 保持 | 「1328 个测试」是 05-25 快照 |
| 🔴[mitigated] 硬拦截路径有回归测 | 仍在，覆盖更广 | [test_pr8c_e2e.py:151](../../tests/test_pr8c_e2e.py) · [test_pr8c_risk_gate.py:525](../../tests/test_pr8c_risk_gate.py) | 保持 | — |
| 🔴[active] **风控回应必填、不可绕过（提示词第 6 段钉死）** | **与现实相反**：独立补充步骤，无风控意见就跳过，失败或漏答**只警告、照常放行**；是返工时有意选的宽松读法 | [risk_gate.py:689](../../src/committee/agents/risk_gate.py)「失败 → warn-only，不阻塞」· 设计依据 [risk-gate-design.md:26](../pipeline/decision/risk-gate-design.md) | **改写**为「要回应；漏答必须留痕（走警告事件）」，改写后可 mitigated | 「提示词第 6 段」已不存在 |
| 🔴[active] 碰硬拦截路径必须对照北极星自查 | 流程规则仍有效；代码层有一条测试守「拦下后不留执行能力」 | [test_pr8c_risk_gate.py:641](../../tests/test_pr8c_risk_gate.py) | 保持（流程规则不能由测试替代） | — |

### §3.6 S2.2 分轮可见性

| 条目 | 现状 | 证据 | 建议 | 过期事实 |
|---|---|---|---|---|
| 🔴[active] 空头开场看得到多头发言的 bug 必须修 | 已修（#127），有测试 + F1 规则运行时二道闸 | [base.py:1156](../../src/committee/agents/base.py) · [test_debate_visibility.py:40](../../tests/test_debate_visibility.py) | **→mitigated** | — |
| 🔴[active] 改流程图后旧存档仍能回放（保留非分轮后备） | **前提没发生**：F-vis 没改流程图；「非分轮后备」代码里从没实现过 | `git show dd6a273~1:src/committee/graph.py` 已是 3 轮 6 发言；旧数据可读由 [test_archive_format_s22.py:22](../../tests/test_archive_format_s22.py) 与 §3.2 首条接管 | **退役** | — |
| 🔴[active] 审核状态字段默认 not_audited，旧存档缺字段不崩 | 行为成立，有测试 | [pass0.py:172](../../src/committee/schemas/pass0.py) · [test_mask_e1_audit_enum.py:38](../../tests/test_mask_e1_audit_enum.py) | **→mitigated** | 字段在 `FactInventoryItem` 上，不在 `EvidenceItem` |

### §3.7 S2.2 D / E / F 类规则

| 条目 | 现状 | 证据 | 建议 | 过期事实 |
|---|---|---|---|---|
| 🟡[active] D 类只挂旗不阻塞；命中率 > 10% 升级审视 | **文字已过时**：D1（整份报告零引用）09-01 起直接打回；10% 线早被触发（D1 约 24%）并由 BT 盘点处理完 | [triage/node.py:135](../../src/committee/triage/node.py) · [BT 盘点](bt-triage-teeth-audit-20260901.md) | **→mitigated**，文字改为「D1 打回，其余只挂旗」 | 同左 |
| 🟢[active] E 类抽样 1/5，按观测调参 | 参数还在；观测做过，从没调过；E 类 71 次评估零开火 | [rules_e.py:33](../../src/committee/triage/rules_e.py) · [BT 盘点](bt-triage-teeth-audit-20260901.md) | **退役**（这是参数不是坑） | — |
| 🟡[active] F 类违规返工一次，仍违规标记放行 | 机制仍在 | [base.py:1367](../../src/committee/agents/base.py) · [test_debate_key_claims_fix.py:131](../../tests/test_debate_key_claims_fix.py) | **→mitigated** | 残留违规记在发言的 `f_check_failed` 字段，不进 quality_flag |

### §3.8 S2.3 fund_manager / Audit

| 条目 | 现状 | 证据 | 建议 | 过期事实 |
|---|---|---|---|---|
| 🔴[active] 正文挂标率 > 50%，低于回炉 | 代码和质检门里**都没有**这项检查；GATE-B 以后设计就是「只验挂了的标，不猎没挂的」 | 质检门 16 项清单 [e2e_quality_gate.py:631](../../src/committee/e2e_quality_gate.py) 无此项 | **待裁**：还要不要这条线？要就在质检门加一项 WARN 试用 | 「FM-3p.1」是早期节点名 |
| 🔴[active] 引用不存在的 fact_id < 2%，超即失败 | 没有「2% 判失败」；实际是**假标全部剥掉并记账**（两层） | [base.py:2435](../../src/committee/agents/base.py) · [base.py:4017](../../src/committee/agents/base.py) · [test_mask_c2_stamp_check.py](../../tests/test_mask_c2_stamp_check.py) | **→mitigated**，文字改为「全剥」机制 | 决策模型不一定是 opus；2% 从没实现 |
| ⚫[resolved] 智堡 MCP 配额硬限制 | 审核环节已无 MCP | [audit_node.py:6](../../src/committee/agents/audit_node.py) | **退役**（「resolved」不在状态词表里，统一改成退役） | 「quota=3 从未触发·调用量无上限」已过期：08-21 换成 run 级总闸（[run_budget.py](../../src/committee/mcp_client/run_budget.py)） |
| ⚫[resolved] 审核 30 秒超时 | 审核已是纯规则 | 同上 | **退役** | — |
| ⚫[resolved] 智堡 MCP 不可用降级 | 审核已不依赖 MCP | 同上 | **退役** | — |
| 🟢[active] 审核通过 / 存疑比例作观测指标 | 只有单跑计数，无跨跑汇总 | [audit_node.py:588](../../src/committee/agents/audit_node.py) · [trace_report.py:367](../../src/committee/trace_report.py) | 保持 | 「负态观测取消」已过期：`audit_notpassed` 08-05 起重新有值 |
| 🟡[active] 安全闸每格只查决策者自查不了的外部盲区 | 设计原则，仍成立 | 条目自带 #176 / #192 记录 | 保持 | — |

### §3.9 S2.3 决策日志 + 引用渲染

| 条目 | 现状 | 证据 | 建议 | 过期事实 |
|---|---|---|---|---|
| 🔴[active] Postgres 迁移升级 / 回退双向干净 | 迁移脚本有升级 / 回退函数，但**没有任何自动测试跑它**；默认库是 SQLite；S2 从没部署 | [migrations/versions/](../../migrations/versions/) · [auth/engine.py:25](../../src/committee/auth/engine.py) | 保持（没有守护，不能 mitigated） | Postgres → SQLite / Alembic |
| 🔴[active] 价格双源路由：A 股 Tushare / 美股 yfinance | 路由在，但**按代码形态判**，且在取数腿上不在价格快照上；两个格式校验器互斥 | [validator.py:530](../../src/committee/retrieval_plan/validator.py) · [test_retrieval_plan_validator.py:175](../../tests/test_retrieval_plan_validator.py) | **→mitigated** | 「按 region 字段」「价格快照路由」都不准 |
| 🔴[active] GET 响应永不返回服务商密钥明文 | 列表只返回挑过的字段，详情按名剥敏感键；只有导出层测试 | [archive/models.py:68](../../src/committee/archive/models.py) · [test_archive.py:120](../../tests/test_archive.py) | **→mitigated**（注明 S4 接入密钥时补接口层测试） | — |
| 🟢[active] 历史列表按时间倒序，不按信心排 | 后端接口如此，但**前端没消费这个接口**（前端历史是浏览器本地会话列表） | [server/api.py:125](../../src/committee/server/api.py) | 保持 | — |

---

## 2. 坑表之外顺带查出的文档漂移（不在 G1 范围内改，并入 G3 全仓收口）

| 漂移 | 位置 | 去处 |
|---|---|---|
| 「拓扑切换失败 → 退回非分轮模式」是从没实现过的设计，仍写得像现有后备 | [S2.md](../roadmap/S2.md) §6.4 | G3 R7 扫：加前向注记 |
| 「audit 平均延迟 < 30s」仍标 must；「智堡 MCP 完全不可用」测试用例是遗留 | [S2.md](../roadmap/S2.md) §5.3 / §5.6 | G3 R7 扫 |
| 「audit_notpassed 永无生产者」旧口径与同文后文、代码矛盾 | [audit-positioning.md](../pipeline/decision/audit-positioning.md) 首段表 | G3 R7 扫 → **G3 核：已被该文 08-05 前向标注覆盖，无需再改** |
| F3 误报、E2「太短」判严两条校准债：交接报告说「维持 active」，但**从没进坑表** | [S2.2 交接报告](s2.2-verification-report-2026-05-26.md) 坑表审视节 | 已在收口计划的「移交 S3 清单」（F3 / E2 校准债） |

## 3. 裁决（用户 2026-09-28）

- **8 条退役 → 全部同意**；缓存库那条写明重开条件「缓存真接进主流程那天」。3 条「⚫ resolved」统一改退役，强度按 git 历史恢复原档（🔴 / 🔴 / 🟡）。
- **风控回应 → 改写并标 mitigated**：「要回应；漏答或调用失败必须留痕，但不拦」；原文保留作历史。
- **挂标率 > 50% → 退役**（被 GATE-B「只验挂了的标」取代）。
- 合计退役 9 条、改 mitigated 8 条；落地方式 = 状态标记改 + 行尾追加「2026-09-28 S2 结束审视」注记，不删原文。

### 裁前原列的待裁项

1. **8 条退役**（§1 标「退役」的行）：同意 / 逐条改。
2. **风控回应那条的改写口径**：「要回应；漏答必须留痕（走警告事件）」，改写后标 mitigated。
3. **挂标率 > 50% 去留**：删（GATE-B 已不猎无标）/ 留，并在质检门加 WARN 试用。
4. 裁完后，坑表的实际改动（状态 + 过期事实订正，保留历史原因）在 G3 同一个 PR 里落地。
