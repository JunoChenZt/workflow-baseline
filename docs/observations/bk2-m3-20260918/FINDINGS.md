# BK.2 M3 · 决策 / 风控组补痕 —— 证据与发现（2026-09-18）

> 施工单：[BK.2-M3 拆解](../../plans/BK.2-M3-decomposition.md)（用户 09-18 裁五件全按建议）· 分支 `auto/BK.2-M3`（从 main `4ab0627` 新建）
> 三处：核验 finding 丢弃（#37）/ 待查证清单缺键（新行 #63）/ 风控问了没答上（#44）。**只加留痕、判定一字不动。**
> 合并请求：[#306](https://github.com/JunoChenZt/subagent-for-investment/pull/306)（2026-09-18 开·刹车 8 问未命中·✅ 2026-09-21 合 main `eee2ef4`；落账见 [backlog 09-21 第 2 笔](../../governance/backlog.md)）〔09-21 合并前 review 补 1 条：「码必须登记」守护改写时列文件丢了未跟踪文件 → `959e9ec` 已修〕

## 大白话导读

决策经理定案前有两道工序：先把关键数字拿去联网查证，再由风控闸门对他的决定提问、让他逐条回应。这两道工序各有退路：查证结果里某条读不出就扔掉；待查证清单里没写清"查什么"的条目被过滤；风控的问题他没答上就跳过。退路都对，但退了没人知道。这一批把三处接到"本次退了哪几步"的清单上。

三处在历史存档里**一次都没发生过**（分别数了 25 次查证、27 次列清单、50 份有风控提问的存档）。所以"它会响"全靠人为注入故障证明，"它不乱响"靠正常路径对照 + 全部 202 份历史存档回放前后逐字相同。改动全在出事才走的分支上，按裁决不单独真跑。

顺带抓到一个**守护自己在空转**的问题：本仓有一道闸，专门检查"代码里用了某个降级码、码表里却没登记"。它只认写在同一行上的写法，换行写的它一个都看不见 —— 上一批（#304）那条就是换行写的，从那时起就没被盯住。这次靠"故意把码表改坏、看闸响不响"才发现，已改成按语法树扫、不认写法。

## 1. 开工前核实

见拆解 §1（十二行核实表）。开工第一步按内容 grep 核了地基在 main：`with_notes` 包装（[graph.py](../../../src/committee/graph.py) `_add`）与 `start_run_notes` 两入口都在。

## 2. 开工前量基线（坑表第 9 条：没量基线不定档位）

脚本 [baseline.py](baseline.py) · 结果 [baseline-result.json](baseline-result.json)。清单从 `origin/main` 取（`ls-tree -z`）：**181 份 `calls.jsonl` · 202 份归档 / 断点**。

| 处 | 怎么数 | 样本 | 命中 | 结论 |
|---|---|---|---|---|
| A 核验 finding 丢弃 | `fund_mgr_verify` 每份日志取最后一条能解析出 `findings` 的记录，照生产循环逐条过 `VerificationFinding`（含 setdefault 四步） | **25 次核验** | 非 dict **0** · 校验不过 **0** | **零阳性样本**；会响只靠注入证 |
| B 清单缺键 | `fund_mgr_outline` 最后一条能解析出 `verify_checklist` 的记录，先照 3217 行过滤（非 dict / 无 item），余下按 `VerifyItem` 分 #304 两档 | **27 次大纲** | 过滤支 **0**；（对照：#304 可纠字段 **10 项**、item 坏 **0**） | **零阳性样本**；#304 的量在同一脚本里复现，读法正确 |
| C 风控问了没答上 | 202 份里 `risk_gate_findings` 去影子后非空的，比对 `final_decision.risk_gate_response` 的 `finding_id` | **50 份有需回应的 finding** | 回应为空 **0** · 非空但缺 id **0** · 齐全 **50** | **零阳性样本**；「回应非空但缺 id」读法 **不做**（拆解 M3.3 step 4 条件不满足） |

**三处都不接近「每跑必响」** ⇒ 档位不停问，正常进用户面（不进 `TRACE_ONLY_CODES`）；措辞按「零阳性 ≠ 不会发生」写。

🔴 **一条与旧记录不符**：[摸底计划 §4.1](../../plans/BK2-M2-M4-plan-2026-09-16.md)（2026-09-16）写「四十四份有问题清单的，十七份回应为空」。本次在 `origin/main` 在册集上**两种读法都复现不出**（去影子 + 决策非空：0/50 为空；不加任何过滤、直接看键：`resp_key_missing=0 / resp_empty=0 / resp_ok=50`）。那份 44/17 **没有脚本入库、无法追溯**；可能原因 = 当时读的是工作树（R6）或按 `id` 键取（memory 记过一次 27/27 全假阳性的同型错）。**本文以可复现的 0/50 为准**；这不改变拆解裁 C 的结论（「节点跑没跑」在 state 里仍看不出，便条为主的理由是结构性的，不是靠那 17 份撑的）。已在摸底 §4.1 加订正注。

## 3. 各处实施（三处 + 一道守护）

| goal | 改动点 | 码 | 一次只一条 | 注入样本 | 对照 | 提交 |
|---|---|---|---|---|---|---|
| M3.1 | [base.py `_run_verification`](../../../src/committee/agents/base.py)：非 dict 的 `continue` + `model_validate` 的 except 两支攒起来、循环后发；detail = 丢几条 / 总数 + 每条 id + 报错字段 + 事项 ≤80 字前缀（≤5 条） | `verification_finding_dropped` | ✅（3 条里丢 2 条 → 1 条便条） | 非 dict / 校验不过各单独一例 + 混合一例；整次失败 → 只出 `fact_verification_failed`（互斥） | 全合法 → 零记录、findings 逐字同、notices 空 | `20f693f` |
| M3.2 | [base.py `_build_outline`](../../../src/committee/agents/base.py) 3217 行过滤支攒起来发 `branch=prefilter`；`_sanitize_verify_checklist` 的 `dropped` 支改发同码 `branch=item_invalid`，`coerced` 支只发 coerced（**裁 B 拆码**） | `verify_checklist_item_dropped` | ✅ | 缺 item / item 空 / 非 dict 三形态一例；事项本身坏一例；改字段 + 扔条目同批各发各的 | 全合法 → 零记录；#304 三份真实夹具照旧只出 coerced、不出 dropped | `f7dd9b8` |
| M3.3 | [risk_gate.py `make_risk_gate_response_node`](../../../src/committee/agents/risk_gate.py)：调用失败 except → `reason=call_failed`、missing=全部；比对后有缺 → `reason=incomplete` + 缺哪几个 id + `_parse_responses` 的三种丢法计数（新加可选 `stats` 入参·返回契约未改）；跳过（决策缺 / 全影子）**不发** | `risk_response_missing` | ✅ | 调用失败 / 部分漏答 / 结构非 list / 条目非法 + 未知 id 各一例 | 全答上 → 零记录、回应照存；跳过路径 → `{}` 且不调模型 | `d54f2da` |
| 守护 | [test_degradation_notes.py](../../../tests/test_degradation_notes.py) `test_note_codes_cover_all_call_sites` 从单行正则改 AST 取首参，并加识别器自证（多行调用点必须被认到） | — | — | 变异 REG-b（见 §3.2） | 原 21 条测试照过 | `2962cc7` |

登记表（[degradation.py `DEGRADATION_SITES`](../../../src/committee/degradation.py)）三键翻 `code:`（`_run_verification` / `risk_gate.py:node` / `_parse_responses`），守卫 `test_registered_codes_are_actually_producible` 与 `lint_degradation_registry` 都认：**待补痕 9 → 6 点**。收集器白名单登记 `risk_gate.py`（只 `note_degradation`、不读篮子，守护逐名核）。

### 3.1 验证四件套

| 步 | 结果 | 依据 |
|---|---|---|
| ① 注入真故障 | 三处 12 条靶测全绿（[test_bk2_m3.py](../../../tests/test_bk2_m3.py)），便条都经**真实环节包装**落进 enforcement_log、带 `node`、不是 `recorder_dropped` | 同上 |
| ② 对照组 | 三处好路径零记录、产物逐字同 | 同上 |
| ③ 在册归档回放 | **202 / 202 逐字相同**、零消失、零新增；三个新码在旧记录里 0 命中（符合零阳性基线） | [replay_degradations.py](replay_degradations.py) · [replay-result.json](replay-result.json) |
| ④ 两向变异 | **13 / 13 RED**（每处：删便条 / 挪到好路径 / 漏一支或错分母；登记表指错码 / 码表漏登记） | [mutations.py](mutations.py) · [mutations-result.json](mutations-result.json) |

全套：**4752 passed / 0 failed**（2 skipped · 2 xfailed 为既有；PR3 时 4737，本批净增 15）。

### 3.2 🔴 变异抓到守护空转：「用了没登记的码」那道闸看不见多行写法

首轮变异 REG-b（把码表里 `verification_finding_dropped` 改名）**不转红**。追下去：闸用 `git grep -E 'note_degradation\("…"'` 扫源码，只认 `函数(` 与 `"字面量"` 在**同一行**；M3.1 写成 `note_degradation(\n    "verification_finding_dropped",` 就整个不在它眼里。**#304 的 coerced 便条起就是这种写法**，也就是那道闸从 09-18 上午起就漏着一个真实调用点、全绿。

- **修**：改按 `ast.walk` 找 `Call` 取首参（不认写法）+ 识别器自证断言。改后 REG-b 转红，13/13。
- **同族**：BJ 派生器「循环读键 / 函数体内 import」盲区（守护要按 AST 取）—— 本例是同一病在另一道闸上的第 2 例。
- **去处**：坑表 §3.2 新增一条（本批 retro must_update）；memory「守护别只认字面量」下补一句。

## 4. 收口闸门

### 4.1 刹车自检 8 问

| # | 问 | 判 | 依据 |
|---|---|---|---|
| 1–2 | 生产可用性 / 敏感配置 | 否 | 不部署、不动密钥 |
| 3 | 北极星 / 合规 | 否 | 不碰决策方向、hard_block、warn-only 语义；核验范围（只查 high）不变；便条不进任何提示词（三道白名单守护全绿） |
| 4 | 不可逆数据 | 否 | 无 |
| 5 | 标准降低 | **否（主动披露两件）** | ① **改 case 两处**（[test_outline_checklist_fix.py](../../../tests/test_outline_checklist_fix.py)）：原断言 `"dropped=0" in coerced 便条 detail` / `"dropped=1" ... in coerced 便条 detail`；改因 = 用户裁 B「一码一义」把扔条目挪到新码；新断言改为「coerced 便条不含 dropped；dropped 便条 `branch=item_invalid`」并**加断言另一码不响**（更严不更松）；影响范围 = 只这两条；回填 = [test_bk2_m3.py](../../../tests/test_bk2_m3.py) `test_coerced_and_dropped_are_two_codes`。② 守护改写（§3.2）是**收紧**不是放松。未删 case、未加 skip；冒烟豁免 = 用户裁 E |
| 6 | 历史改写 | 否 | 只动决策**一个阶段**里两个环节的退路分支；不改 schema / 提示词 / 已 DONE 节点契约；摸底 §4.1 那句**加订正注、原文不动**（规划文档、非冻结档） |
| 7 | 用户成本 / 外部依赖 | 否 | 零模型花费 |
| 8 | 路线选择 | 否 | 五件路线用户已裁；「读法做不做」按拆解写定的判据（基线零命中 → 不做）走，不是新路线 |

**不命中 ⇒ 按 §2.7.4 不停，开合并请求。**

### 4.2 完成标准 4 步

| 步 | 结论 |
|---|---|
| Code Review（自查） | 契约未触：`_run_verification` 返回三元组不变；`_build_outline` / `_sanitize_verify_checklist` 签名与返回不变；`_parse_responses` 只加可选 `stats` 入参（默认 None·返回不变）；回应节点 warn-only / `return {}` / `emit_event` 照旧；hard_block 三个函数一字未碰（相关 251 条测试逐字过） |
| Corner Case | 全套 **4752 / 0 失败**；新增 1 个测试文件（12 条）+ 守护改写 1 条；改 case 两处已按 §2.8.2 四要素披露（§4.1 Q5） |
| 冒烟 | 豁免（用户裁 E）：改动全在 except / 过滤 / 漏答分支 + 202 份回放齐 + 三处注入齐 |
| 彻底跑通 | 无 known issue skip；`lint_degradation_registry` / `lint_doc_links` / `lint_env_registry` 干净 |

### 4.3 goal 级复盘

- **触发**：第 6 条（高风险节点）· 第 3 条（暴露守护空转 §3.2）。
- **must_update（已落盘）**：坑表 §3.2 新增「扫源码的守护要按 AST、别按单行正则」（[09-known-pitfalls.md](../../governance/workflow/09-known-pitfalls.md)）。
- **should_update**：0。
- **observe**：① 09-16 摸底里的「44/17」这种**没脚本入库的数**进了两份计划、撑了一条设计理由，今天才发现复现不出 —— 与「计划表数字是待核假设」同族，本批按规则回核了、没吃亏；不新增条目。② `emit_event` 是「现场事件」、不进归档 —— 凡拿它当留痕的登记都要重看（本域今后新点照便条走即可，不另立）。
- **本批未触发的旧 observe**：同族「一个字段写坏整份作废」三处候选（辩论 / 投票 / 辅助助理）不在 fund_manager、留给 M4。

### 4.4 backlog 判据闸门 triage（提交时点名 2 条，均判**不算触发**）

| 条目 | 闸门为何点名 | 逐条核 |
|---|---|---|
| `DEFECT-CTX-BAG-SHAPE` | 声明监视 `agents/base.py` | 不算（粒度差）：判据点名资料夹两格子字段 / `_is_ticker_query` / 价格闸读袋；本批改在 `_run_verification` / `_build_outline` / `_sanitize_verify_checklist`，无交集；且该条已是 🔔 已触发、账面不动 |
| `AF-residual` | 声明监视 `agents/base.py` | 不算（粒度差）：判据点的是 `make_decision_node` 里 `reports_block` 注入段，本批未碰 |

### 4.5 节点级 retro

**未到时点**：BK.2 还剩 M4 批；节点级 5 问在 M4 收口时做。

## 5. 裁决回填清单（§2.9.4 · 8 格）

本批落地的裁决 = 五件（A–E）+ 「读法不做」（基线判据）+ 「44/17 不成立」订正。

| 格 | 真值源 | 结论 |
|---|---|---|
| 1 | backlog **BK** 条目正文 | **合并后改**〔✅ 09-21 落账已改〕（同前三批先例：落账随合并同笔做；内容 = 本批三处 + 守护空转 + 真待补 10 → 8 + 登记待补 9 → 6） |
| 2 | backlog 引用该结论的其它条目 | N/A —— 其它条目不引 M3 数字；摸底 / 执行计划两份**规划文档**已加订正注（[摸底 §4.1](../../plans/BK2-M2-M4-plan-2026-09-16.md) · [执行计划 §3 / §4](../../plans/BK2-M2-M4-exec-plan-2026-09-16.md)） |
| 3 | 跑批与操作指南 | N/A —— 不改任何判据文本；新码走既有「本次退了哪几步」清单 |
| 4 | 验收判据表 | N/A —— 降级汇总在 D1 记录型、不参与判定，本批不新增维度 |
| 5 | 观察点表 | N/A —— 无 `O-*` 观察点变动 |
| 6 | 代码常量与注释 | 改了：[degradation.py](../../../src/committee/degradation.py) 码表三条 + 登记表三键注释；[risk_gate.py](../../../src/committee/agents/risk_gate.py) 留痕助手 docstring 写明「为什么当场记、不能事后读」；[base.py](../../../src/committee/agents/base.py) 两处注释 |
| 7 | 阶段路线图 / 主链路文档 | N/A —— S2 路线图只在 §4.7 顺手项提 BK 一句、不列子批状态；主链路文档不引 M3 数字 |
| 8 | auto-memory | **合并后改**〔✅ 09-21 落账已改〕 `project_bk_degradation.md`（终态 + 守护空转教训） |

盘点表本身（[BK.0 §2.3 / §2.5 / §3.0](../../plans/BK-G0-inventory-2026-09-14.md)）：#37 #44 翻已做、#63 新增即做、口径行加「M3 后余 20 行·真待补 8」。
