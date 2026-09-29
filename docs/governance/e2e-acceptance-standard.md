# E2E 验收标准（6 维框架 · 共识版）

> **状态**：共识草案（2026-06-04）。本文是"每次 e2e 至少该关心什么"的**完整标准 / 北极星**；
> [e2e-quality-gate.md](e2e-quality-gate.md) 是本标准**已落地的结构层子集**（S1-S6 / Q1-Q13 / D1）。
> 两者关系：本文定义"该查什么 + 承重边界 + auto/judge/defer 分类"，gate 文档记录"现在代码实际查了什么"。

---

## 导读（大白话，给基金经理 / 产品 / 合规）

每次让委员会跑一个投研问题、跑完，要能回答这几个问题——就像审一份外部分析师的报告：

1. **跑顺了吗**：有没有中途卡壳、反复重来。（稳定性）
2. **数字可信吗**：报告里引用的"营收 194 亿"这种事实数字，是真有数据背书，还是模型顺口编的？（**价位另说**：买入/止损/止盈是决策者*推算的目标*、天然拿不到"官方证实"，故不按"逐个要背书"判——改由「整篇有据才放行」+「跟真实市场价比是否离谱」兜，见 §4 (b) 登记）没把握的数字有没有老实说成"大致区间"而不是装精确。（数字可信度）
3. **信息新鲜吗**：用的关键事实是不是过时的？有没有把"上个月已经发生的事"当成"未来的风险"来讲。（时效性）
4. **自己跟自己一致吗**：结论说"买"，但投票多数看空、执行计划又写着减仓——这种自相矛盾有没有被消解，还是糊过去了。（内部一致性）
5. **真答了我问的吗？该下判断的地方下了没？** 我问"什么价位买入合适"，报告是正面给了价位，还是绕成"再等等信号"和稀泥？核心分歧有没有被真正裁决，还是用 NEUTRAL 糊过去？问题有歧义时（比如同名两家公司），是先问清楚还是自己混着答了。（判断质量 + 回应核心关切）
6. **事后看准吗**：30 天后回头看，当初定的"跌破 X 就走"那些条件触发了没、触发后建议对不对。这是唯一的真考试。（事后校准）

外加一条横切的：**这一份花的钱（token）值不值**。

**一条贯穿原则**：宁可报告老实说"这点我不确定"，也不要把没把握的事写得像有把握——**错的数字伪装成对的，比承认不知道更危险**。

---

## 0. 四条设计原则（先立规矩，再谈各维）

这四条决定了每个检查"怎么做、能不能当真"：

**① 承重检查必须是代码层；LLM-judge 只能 advisory，不能 hard-fail。**
半数质量维（语义类）只能靠"派一个模型去审报告"实现。但用一个会出错的模型去验另一个模型，错误会叠加——违反[不确定性诚实原则](unverified-premise-protocol.md)。所以：
- **hard-fail 闸门**（FAIL = 不落盘）只用**结构化、可复现的代码检查**。
- **LLM-judge** 的产出是 **flag 给人看 / WARN**，永不自动 block。
- 承重判断（如"精确数字必须有 verified 背书"——**限引用型事实数字**；`execution_plan` 价位自 2026-07-22 起走 run 级 grounding 地板，见 §4）走**代码门控**，不交给 judge。

**② calibration（第 6 维）有数据契约前置依赖。**
"30 天后逐条核对可证伪条款"要可行，条款必须机器可读。现状（已核 [schemas/decision.py](../../src/committee/schemas/decision.py)）：
- `trigger_events: list[str]` —— **自由文本**，无法逐条判定"触发了没"。
- `ExecutionPlan.reevaluate_triggers` —— **结构化模型**，calibration-ready。
- `time_horizon: str`（"中期"）—— 需 →天数映射才能匹配回看周期。

**结论**：D5"可证伪条件具体可观测"不只是质量要求，它是 D6 的**数据契约**。D6 真要做，先得让 trigger 结构化（或只认 `reevaluate_triggers`）+ `time_horizon`→天数。

**③ 过程分（前 5 维）与结果分（第 6 维）分开记，长期看相关性。**
- 一次蒙对的烂分析 比 一次踩雷的好分析 **更危险**——别用结果反推过程对错。
- 真正该优化的信号 = **"过程分高的报告，事后是否也更准"** 的相关性。
- 两个陷阱：
  - **样本量**：N<30 时该相关性是噪音（Wilson：0/5 命中上界 ~52%，0/30 ~12%）。早期别据单次 outcome 调系统。
  - **HOLD 偏置**：永远 HOLD 永不证伪但无用。outcome 记分必须给"**该出手没出手**"的机会成本也记一笔，否则系统会学会用"和稀泥 HOLD"刷准确率——恰好砸了 D5。

**④ "token 值不值" 现在没有分母。**
D6 outcome 出来前，"值不值"只能用**代理指标**：成本 vs 过程质量分、重试浪费率、离群贵的角色。真正的 cost/value 要等 calibration 给出 outcome 当分母。所以消耗维**早期只报数、不设硬阈值**。

---

## 1. 六维 + 消耗：逐维标准

每行标注：**数据来源** · **可自动化程度**（✅已实现 / 🟢数据已有可加代码 / 🔵需 LLM-judge / 🔴需新基建）· **承重边界**（hard-fail / advisory）。

### 维度 1 · 稳定性（能不能跑通、过程干不干净）

| 子项 | 数据 | 程度 | 边界 | 现状 |
|---|---|---|---|---|
| 跑通（有 decision + query） | archive | ✅ | hard-fail | S1 |
| schema 字段齐全 | decision | ✅ | hard-fail | S2 |
| ~~无 m4-m13 hard-fail flag~~ **voice 硬规则 m4/m5/m6/m7/m8/m13 零 critical 违规** | ~~enforcement_log~~ **离线审计脚本 [voice_guardrail_audit.py](../../scripts/eval/voice_guardrail_audit.py) 现算**（读 technical 报告 + directional_calls + evidence_log） | ✅ | ~~hard-fail~~ **WARN 试用**（2026-09-28 · RDR-1.G1）| S4 —— ⚠️ 旧判据读 `enforcement_log` 里 `rule ∈ {m4…m13}`，全仓无生产者、恒 PASS 两个多月（backlog `DEFECT-GATE-S4-NO-PRODUCER`·S2 收口 G0 核实）；改接离线审计 = **首次真正上线**，故按 §4 走 WARN 试用，不继承纸面 hard-fail；脚本不在 → N/A |
| thesis 段有正文 | decision | ✅ | WARN | S5 |
| triage rework ≤1 角色 | rework_counts | ✅ | ≥2 fail | S3 |
| **LLM 层重试浪费**（parse 重试 / 续写 / 工具循环） | **段式 trace（新）** | 🟢 | advisory | **未实现**：trace 现在能看到每节点多次调用，可加"重试率"统计 |
| **本跑退了哪几步**（降级条数 + 逐条码） | 归档 `degradations`（[degradation.py](../../src/committee/degradation.py) 纯派生） | ✅ | **记录型·不参与判定**（见 §2 说明） | **D1**（2026-09-14 落地·PR [#295](https://github.com/JunoChenZt/subagent-for-investment/pull/295)）〔**⚠️ 补登记 2026-09-15**：该项代码先落地、本文档漏登记，违反 §4「先登记再落地」。补记于此，边界未变〕 |

### 维度 2 · 数字可信度（伪精度检出）

| 子项 | 数据 | 程度 | 边界 | 现状 |
|---|---|---|---|---|
| entry / stop 非占位符（0.0/1.0）| execution_plan | ✅ | hard-fail | Q3/Q4 |
| 引用归属误标 ≤30% | enforcement_log(EVID-1) | ✅ | >50% fail | Q5 |
| **正文每个精确数字都有 verified 背书** | `claim_audits`/`audit_status`（数据已有，见 [schemas/pass0.py](../../src/committee/schemas/pass0.py)）| 🟢 | **WARN 试用**→待数据后升 hard-fail | **未实现**：可加"未背书的精确数字→必须降级定性"检查。⚠️ 数字↔claim 匹配是模糊启发式（改写/单位转换/日期误识），误报率未知；且 web search 来源数字无 REF 水印、claim_audits 无对应背书——上线即大面积触发。先 WARN 试用、实测误报率后再走 §4 升 hard-fail |
| 非 verified 是否被降级为定性表述 | claim_audits + 正文 | 🔵 | advisory | 需 judge 读正文 |
| **execution_plan 价位 grounding**（2026-07-22 GATE-ROUTE (b) 补登记）| `confidence_map` + execution_plan | ✅ | **运行时承重**（非 gate 检查）| **run 级地板** `_GROUNDING_MIN_VERIFIED=2`：整篇 verified 数 ≥2 → 放行全部价位原样；<2 → 抹全部 level。**真守门委托** = EXEC-FLOOR **check②**（价位↔表①真实市场价数量级）+ **check③**（过期锚点·2026-07-22 转正）+ hard_block。⚠️ 刻意**不**逐价位要求 verified——分析型目标价结构上够不到（详 [fm-spec §A1](../specs/fm-decision-node-spec.md)）|

### 维度 3 · 时效性

| 子项 | 数据 | 程度 | 边界 | 现状 |
|---|---|---|---|---|
| 关键事实 as_of 与决策日距离 | `as_of`（一等公民，见 [as_of.py](../../src/committee/as_of.py) / watermark）| 🟢 | advisory（超阈 WARN）| **未实现**：可加 max/median staleness |
| "内蒙式错误"（已发生的事被当未来风险）| trigger_events / 风险条目 vs as_of | 🔵 | advisory | 需 judge 判 framing |

### 维度 4 · 内部一致性

| 子项 | 数据 | 程度 | 边界 | 现状 |
|---|---|---|---|---|
| decision 方向 ↔ 投票多数 | decision + votes | 🟢 | advisory | **未实现**（运行时不校）|
| decision ↔ execution_plan（**SELL/REDUCE** 不应带买入区间）| decision | ✅(运行时) + ✅(gate S6) | hard_block | 运行时 Phase 4b risk gate 踩红线时切 plan。gate S6 = 冗余断言。⚠️ **2026-07-22 收窄**：原写「HOLD 不应带买入计划」**判据有误已废**——「观望」是对*当前价位*的判断，"现在别追、跌到 X 值得买" = HOLD + 目标买入区间**互补非矛盾**（用户裁决）。真正该拦的语义冲突只有 **SELL/REDUCE 带 entry**（schema 契约原文）。详见 §4「S6 判定收窄」 |
| 风险条数 ≥3（G5 对齐）| core_risks | ✅ | WARN | Q7 |
| decision 方向 ↔ 散文结论自洽 | 正文 | 🔵 | advisory | 需 judge |
| 角色间数字打架是否被消解而非掩盖 | reports + 正文 | 🔵 | advisory | 需 judge |
| **散文价位 ↔ 结构化计划一致**（止损 / 止盈 / 入场；触发器带「止损」的阈值 = stop_loss.level） | decision 散文字段 + execution_plan | ✅ | **WARN 试用**（advisory·永不 FAIL） | **Q10**（2026-09-28 · RDR-1.G0 · backlog CB·C1）· 前提空 → N/A 不 PASS |
| **可复算数字复算**（盈亏比 / 「X 的 Y%」/ 「距 X … Y%」按现价复算·误差 >5%） | decision 散文 + current_price | ✅ | **WARN 试用**（advisory·永不 FAIL） | **Q11**（2026-09-28 · RDR-1.G0 · backlog CB·C2）· 无现价 / 没抓到 → N/A |
| **同一机构价格预测多值**（显式值 + 「现价…的 Y%」隐含值；带「下调 / 从 X 至 Y」的修订不算） | decision 散文 | ✅ | **WARN 试用**（advisory·永不 FAIL） | **Q12**（2026-09-28 · RDR-1.G0 · backlog CB·C3）· 无带值提及 → N/A |
| **「未核实」括注措辞不漂出闭集**（[caveats.py](../../src/committee/caveats.py) `CAVEAT_ALLOWED`；残缺形也点名） | decision 散文 | ✅ | **WARN 试用**（advisory·永不 FAIL） | **Q13**（2026-09-28 · RDR-1.G0 · backlog CA·C5）· 零括注 = PASS |

### 维度 5 · 判断质量 + 回应核心关切

| 子项 | 数据 | 程度 | 边界 | 现状 |
|---|---|---|---|---|
| confidence ∈[4,8]（非无信号 / 非过度自信）| decision | ✅ | WARN | Q1 |
| 情景完备（≥3 场景 ≥2 角色）| reports | ✅ | WARN | Q6 |
| 方向性判断覆盖 ≥3 角色 | reports | ✅ | WARN | Q2 |
| 核心分歧真裁决 vs NEUTRAL 和稀泥 | debate + decision | 🔵 | advisory | 需 judge（HOLD+低 conf+多数 NEUTRAL 可做启发式预筛）|
| 可证伪条件具体可观测（有数字/阈值/日期）| trigger_events | 🟢半 | advisory | **未实现**：可正则筛"是否含可量化条件"，质量再交 judge。⚠️ 目标字段随原则②数据契约决议同步——若 D6 决定只认 `reevaluate_triggers`，本预筛也应切换到该字段，避免 D5 在查一个 D6 已放弃的字段 |
| 留白是否诚实 | 正文 | 🔵 | advisory | 需 judge |
| **回应核心关切（答非所问）** | query_type（[query_class](../../src/committee/query_class/)）+ decision/execution_plan | 🟢半 | advisory | **未实现 · 最新维度**：query 核心问句 → 应有答案槽（问价格→entry 非空；问方向→有明确 BUY/SELL）。歧义澄清（Marvel 同名案）需 judge |

### 维度 6 · 事后校准（30 天回看 · outcome，与前 5 维分开记分）

| 子项 | 程度 | 现状 |
|---|---|---|
| 逐条核对可证伪条款（trigger 触发了没、触发后建议对不对，而非只看涨跌）| 🔴 | **无基建**（S4 / roadmap §6.5 AutoResearch 量化迭代占位）|
| 周期匹配 time_horizon（30 天初评 + 到期终评）| 🔴 | 同上；依赖原则② 的 time_horizon→天数 |
| HOLD 偏置机会成本（"该出手没出手"）| 🔴 | **需反事实基准定义**：出手了→按什么价位/仓位算？比触发核对难一个量级。roadmap 第 3 批落地时最先卡住的项 |
| 过程分 vs outcome 相关性（系统真正优化信号）| 🔴 | 同上；注意原则③ 两陷阱 |

### 横切 · 消耗（token / 成本）

| 子项 | 数据 | 程度 | 边界 | 现状 |
|---|---|---|---|---|
| 每步 / 每角色 / 每段 token + 成本 | token_usage + 段式 trace | 🟢 | 只报数 | 数据全有（[token_usage.py](../../src/committee/token_usage.py)）|
| 重试浪费率 | trace | 🟢 | advisory | 可加 |
| "值不值" | —— | 🔵/🔴 | —— | 缺分母（见原则④），等 D6 outcome |

---

## 2. 承重边界总表（哪些能 hard-fail）

> 原则①：只有**结构化代码检查**能 hard-fail；judge 类一律 advisory/WARN。

**可 hard-fail（FAIL=不落盘）**：S1 完成 / S2 schema / ~~S4 hard-fail flag~~（2026-09-28 起 S4 改 WARN 试用·见维度 1 表）/ **S6 SELL/REDUCE 带买入区间** / Q3·Q4 占位符 / Q5 误引用>50%。

> ⚠️ **S6 补录（2026-07-22）**：S6 自 2026-06-04 起即有 FAIL 列（见 [e2e-quality-gate.md](e2e-quality-gate.md) S6 行）却**一直漏在本清单外**；2026-07-22 收窄其判据时一并补录。判据 = SELL/REDUCE 携带 `execution_plan.entry`（买入区间）→ FAIL。

**WARN 试用（待升 hard-fail）**：「精确数字无 verified 背书」—— 模糊匹配误报率 + web search 盲区未实测，先 WARN 跑数据再升级（§4 试用期规则）。

**记录型（只印数、不参与任何判定）**：**D1「本跑退了哪几步」**（2026-09-14 落地 · 2026-09-15 补登记）。

> **为什么比 WARN 还弱、而不是按 §4「一律 WARN 试用」办**：`overall` 的算法是「任一 WARN → 整体 WARN」。
> 而**降级是常态**（跑批几乎每次都会退某一步），判 WARN 等于给「条数 > 0」暗设了一条阈值线，
> 并把既有的 13/0/0 全绿基线全部拉成警告、失去可比性。用户 2026-09-14 裁的是「只记录、不设阈值」。
> ⇒ 它**不是一道检查**，是一栏读数；§4 的「新检查一律 WARN 试用」管的是会影响判定的检查，
> 本项在判定上恒等于 PASS，故不适用。**将来若要给某一类降级单独设线，那是新检查，须按 §4 走 WARN 试用。**

**advisory / WARN（flag 给人，不 block）**：所有 🔵 judge 类、as_of staleness、decision↔votes 一致性、答非所问、token、retry 浪费、confidence/场景/风险/覆盖计数（S5/Q1/Q2/Q6/Q7）、**Q8 check① 可见性**（2026-09-10 · WARN 试用·只印「响没响 + 三元组」不判对错）、**Q9 辩论数字冲突**（2026-09-24 · WARN 试用·只标记不纠正）。、**Q10–Q13 决策文本一致性四检查**（2026-09-28 · RDR-1.G0 · WARN 试用·advisory：Q10 散文↔计划价位 / Q11 可复算数字 / Q12 同机构多值 / Q13 括注措辞集合；**前提空一律 N/A 不 PASS**；升 hard-fail 须 ≥3 跑实测误报率后用户裁）

---

## 3. 落地 roadmap（本文先共识，实现分批）

1. **现在就能加（🟢，用现有数据，无需新 schema）**：as_of staleness · decision↔votes/execution_plan 一致性 · 答非所问（query_type→答案槽）· 精确数字 verified 背书 · 成本/重试浪费统计。→ 作为 e2e_quality_gate 新增 S6+/Q8+ 检查。
2. **LLM-judge 层（🔵，advisory）**：内蒙式 framing · 散文↔决策一致 · 和稀泥裁决 · 留白诚实 · 歧义澄清。→ 独立"审稿 agent"，输出 flag，**不进 hard-fail**。
3. **calibration（🔴，S4）**：先补**数据契约**（trigger_events 结构化 / time_horizon→天数），再建回看调度 + 逐条触发核对 + 过程-结果相关性追踪。

---

## 4. 维护协议

- 本文是**标准**（该查什么）；[e2e-quality-gate.md](e2e-quality-gate.md) 是**实现**（现在查了什么）。新增检查时：先在本文对应维度登记 + 标 auto/judge/defer + 承重边界，再到 gate 文档/代码落地，两边同步。
- **新检查试用期规则**：所有新增检查**一律 WARN 试用**，跑 ≥3 次真实 e2e + 实测误报率后，方可走下条升级流程升为 hard-fail。这比逐条争论承重边界干净——先拿数据说话。
- 承重边界（hard-fail vs advisory）调整 = 重大变更，需停下问用户（呼应 [workflow.md §7.2](workflow.md)）。
- **运行时委托项登记**：D4 "HOLD↔execution_plan" 委托 Phase 4b risk gate 运行时保障，gate 不重复评分。此类委托必须在此显式登记——**被委托方变更时必须回审 gate 覆盖**。当前登记：
  - D4 HOLD→execution_plan 切除 → 委托 Phase 4b（hard_block 节点）。建议加冗余 gate 断言（defense in depth）。
  - ⚠️ **2026-07-22 修正（GATE-ROUTE G2）**：上条推导出的 **S6「HOLD 不许带 entry」判据前提有误·已收窄**，详见下方「S6 判定收窄」条。

- **段间 checklist 数字线一次性重校（2026-07-31 对账 → 2026-08-03 落地·用户裁决「落地」）**
  - **对象**：[segmented-e2e-guide.md](../observations/e2e-runs/segmented-e2e-guide.md) 的**段间人工 checklist**，
    **不是** [e2e-quality-gate](e2e-quality-gate.md) 的 S1-S6 / Q1-Q7 —— **gate 代码一行未动**，本次无任何 hard-fail 档位变更。
  - **依据**：[对账报告](e2e-guide-threshold-audit-20260731.md)（11 正常 run + 4 对抗 run 回测·零网络可复现）。
  - **逐条登记**：

    | 判据 | 维度 | 原承重 | 新承重 | 方向 |
    |---|---|---|---|---|
    | ⑧ `audit_passed ≥ 50%` | D2 数字 | 段间 ❌（阻断续跑） | **observe**（记录·仅 <5% 才排查） | **放松**（实测 6–47%·从没达标 = 空线） |
    | ⑥ 辩论总 output `<15k` | 消耗 | 段间 ❌ | **22k–29k·>40k 才排查** | **放松**（实测 22.4k–28.4k·每次都超 = 空线） |
    | ② `evidence_log ≥ 1` | D2 数字 | 段间 ❌ | **两步判**（先看正文数字带不带章·带章记 observe） | **放松**（判据原本量错对象·backlog BE） |
    | ③ `rework_counts ≤ 2` | D1 稳定 | 段间人工 | **移交单测** | 不变（结构性恒真·本就不可能 fail） |
    | ⑨ `confidence ∈ [1,10]` | D1 稳定 | 段间人工 | **移交单测** | 不变（同上） |
    | ⑥ 6 轮 / ⑦ 10 voter | D1 稳定 | 段间 ❌ | 保留·**改标注「存活探针」** | 不变（纯命名·15/15 零方差） |

  - **为什么不走 §4「新检查一律 WARN 试用」**：本次**没有新增任何检查**，全部是
    **放松既有判据 / 移交承重 / 改标注** —— fail 面**只减不增**、方向 fail-safe。
    （同 S6 收窄的先例逻辑：WARN 试用期是给「新增检查」的闸门，不是给「拆自己的空线」的。）
  - **⚠️ 刻意没做的事**：对账 #8/#10 两条**钝线**（`key_points ≥2` 实测最小 3–5 / `core_risks ≥3` 实测 3–4）
    **原值未动，只加了校准注**。收紧它们 = **提高 fail 面 = 承重变更**，按本节第 3 条须停下问用户 —— 本次未问，故未动。
    〔⚠️ **别把 #9 也读进这句**：对账 #9 = `evidence_log ≥ 1`，同属钝线，但它**本次改了**（上表第 3 行·两步判·方向放松），
    不属「原值未动」那一档 —— **阈值没动、动的是读法**，校准注同样已补〕
  - **连带立的惯例**：guide 每条数字线旁须注明「定于何时·依据什么实测·下次何时复核」
    （对账建议 7）。理由是实测的：全表唯一有校准记录的线，也正好是唯一「紧但不空」的线。
    〔**2026-08-27 补注 · 上句的「实例」已不成立，惯例本身不变**〕当年举的那个实例（① 段
    `query_class` input 线）后来**两度失去「紧但不空」**：2026-08-14 由 ≤800 上移至 ≤900
    （余量约 12%·「紧」让出），2026-08-18 [#244](https://github.com/JunoChenZt/subagent-for-investment/pull/244)
    重写分类提示词后实测稳定 **≈1120**、**每跑必越** —— **用户 2026-08-18 当场裁「线保留不动、
    越线属预期非回归」**，故该线现已落进本节自己定义的「空线」档。⇒ **结论（有校准记录的线才有成色）
    不变，只是不能再拿这条线当正面例子。** 完整经过与读法见
    [guide ① 段的 💰 块](../observations/e2e-runs/segmented-e2e-guide.md)；**是否重新定线未裁，属敞口**。
    **落地时发现惯例当场就有例外**，故在 guide 里写死三档兜底口径：① 有 📐 校准注 · ② 标 📐 **未校准**
    （判据没进 07-31 那轮对账、连准不准都没测过·下轮优先补）· ③ 两条【存活探针】不需要校准注。
    ⚠️ ② 档**不在对账报告 §1 总表里** —— 总表只覆盖被测的 12 条，「没被测」≠「测了发现钝」。
    当前 ② 档 **3 条**：② 段每角色调用数 ≤3 / `as_of` 超一周 · ④ 段 `facts_inventory ≥5`。
    〔**2026-08-18 摘除一条**〕~~① 段 `as_of` 超 3 天~~ —— 已由 104 条 reference 实测校准成
    **按来源分档**、转入 ① 档（有 📐 校准注），见下方「① 段引用时效」登记条。
  - **② 两步判的边界（防误读）**：第一步「数字带 `W#`/`REF#` 章 → 放行」只降**「字段没填」的误报**，
    **不是对数据真实性的背书** —— 锚存在性无人校验（[backlog BC](backlog.md)）。故带章判 **observe 而非 ✅**；
    ~~BC 若验出「拦不住」，本步须连带回审~~（按本节「运行时委托项登记」同理：被依赖方变更时必须回审依赖方）。
  - **↳ ✅ 回审已执行（2026-08-04·BC 验出「拦不住」·[run-bcprobe-nvda-zh](../observations/run-counter.md)）**
    —— **承重结论：判据不变**（第一步仍 observe·**fail 面零变化**·故 §4「新检查一律 WARN 试用」不适用）。
    **变的是边界措辞，往严的方向**：
    - **原措辞防的是「章可能是编的」**（锚不存在）。实测这一路 N=2 可复现，但**没进最终决策**。
    - **实测出的真危险是另一路：章真实存在、绑的却是别的实体。** 13 条 `audit_passed` 里
      **10 条**（77%）的锚指向不相干字段（`PE 30.79x` 的锚指向 `price`），且**走完全链印给读者**，
      其中 `ROE 114%` 在附录被标 **verified**、正文**零 caveat** → [DEFECT-ANCHOR-MISBIND](backlog.md) 🔴→✅ **CLOSED 2026-08-14**（随「数字出处」问题域[封卷](number-provenance-endgame.md)）。
    - ⇒ **「带章」这个信号，连"章指向的是不是这件事"都不保证。** 读它时只当"有人写了个编号"，
      **不当"有据可查"**；判 observe 的理由从此是「章的**指向**未经校验」，而不只是「章的**存在性**未经校验」。
    - 🔒 **同时记死一条反面证据**：本跑终局 quality gate **13 pass / 0 warn / 0 fail**，其中
      `Q5 证据误归因` 报 **0%** —— 而上述 4 条正是误归因。**Q5 对本形态零判别力**，
      **不得**把「Q5 绿」当作「误归因已被覆盖」的依据（名字让人以为有人管，实际没管）。
  - ~~**未落地项**：对账建议 3（让 trace 自动打印「fm 本跑是否填了结构化价位」）需改 trace 渲染代码，
    另开 → backlog **BF**🟡。在它落地前，⑨ 段两条价位判据**仍靠人工先确认前提**。~~
  - **↳ ✅ 已落地（2026-08-13·[backlog BF](backlog.md) close）** —— ⑨ 段决策摘要现在自己打印
    「价位前提」行，分三态 —— **没填 / 填了 / 填了但数字被门控抹掉**，后两种之外一律
    明写**判「本跑无效」而非 PASS**（判的是"有没有价位数字"，不是"有没有价位对象"）；
    前提确认从「靠人记得先翻 checkpoint」变成**读报告里的现成行**。
    **承重边界：fail 面零变化** —— 不动 gate 任何代码、不新增自动检查，只把已有的人工前提可视化，
    故 §4「新检查一律 WARN 试用」不适用（同 BB/BE 数字线重校、S6 收窄先例）。
    ⑨ 段判据本身**一字未改**。验证 = 19 份 tracked ⑨ 段 checkpoint 离线回放（三形态全命中·19/19），
    evidence [bf-trace-premise-20260813](../observations/bf-trace-premise-20260813/EVIDENCE.md)。

- **S6 判定收窄（2026-07-22·用户裁决 A·GATE-ROUTE G2）**
  - **维度归属**：维度 1 稳定性（结构化代码检查）· **承重边界：维持 hard-fail**（只收窄判定范围，不改承重档位）。
  - **原判据**：`decision == "HOLD"` 且 `execution_plan.entry` 有 low/high → FAIL。
  - **新判据**：`decision ∈ {SELL, REDUCE}` 且 `execution_plan.entry` 有 low/high → FAIL；**HOLD 带 entry 不再判 FAIL**。
  - **为什么原判据错（用户领域裁决 2026-07-22）**：**「观望」是对*当前价位*的判断，不是对*该标的*的判断**。
    决策者说"现在别追，但跌到 950-1000 我认为值得买"——**HOLD + 目标买入区间是互补的、不是矛盾的**，
    而且正是"装备决策者"该给的信息（告诉他什么价位才有吸引力）。把它判成 FAIL 会**逼着系统删掉用户最想要的东西**。
  - **原判据从哪来（根因）**：由上条「D4 HOLD→execution_plan 切除」委托登记推导而来——但那条描述的是
    **hard_block 踩风控红线后切计划、并把决策降级为 HOLD** 这一*结果*；S6 把它**逆推成了「HOLD ⟹ 不该有计划」这一通则**
    （逆命题当原命题）。核实：① [schema 契约](../../src/committee/schemas/decision.py) 只规定
    **SELL/REDUCE 必须置 null**（理由=entry 渲染为"买入"色调·卖出场景复用会语义混乱），**从未禁 HOLD**；
    ② runtime 中**不存在**「HOLD ⟹ entry 必须 null」的逻辑——唯二清 plan 处（hard_block / OBEY-5）
    都另有原因（踩红线 / 决策被投票否决整体作废），非"因为是 HOLD"。
  - **为什么现在才发现（价值点）**：旧价位门控**无条件抹掉非 verified 价位** → S6 永远查不到 entry 值 →
    **恒"通过" = 死码**。GATE-ROUTE G2 改 (b) 放行价位后它才第一次真跑，随即暴露前提错误。
    ⚠️ **教训（同族于 check③）**：**死码检查的危险不在"不干活"，而在"前提错了也没人知道"**——
    check③ 死得无害（少拦一道），S6 死得有害（错判据潜伏）。凡"因上游恒不产生该状态而永不 fire"的检查，
    上游一旦放开，必须**先复核其判据前提**、而非默认它正确。
  - **不走 WARN 试用期的理由**：本次是**收窄既有 hard-fail 的误判范围**（FAIL 面只减不增·方向 fail-safe），
    非"新增检查"，故 §4 新检查一律 WARN 试用规则不适用；真正该防的语义冲突（SELL/REDUCE 带买入区间）
    **原样保留 hard-fail**。

- **Q4 HOLD 豁免收窄（2026-07-22·S6 同源错前提的漏网·DOC-SYNC A1）**
  - **维度归属**：维度 2 数字可信度（结构化代码检查）· **承重边界：WARN（不变）**——只改触发范围，不动档位。
  - **原判据**：`stop_loss` 为空时，`direction == "HOLD" or not entry` → PASS（即 **HOLD 一律豁免**）。
  - **新判据**：`(direction == "HOLD" and not entry) or not entry` → PASS；
    **HOLD + 有 entry + 无 stop_loss → WARN**（与其余方向性决策同待遇）。
  - **为什么是 bug（非口径调整）**：该函数 **docstring 自己写着**「HOLD with entry but no stop: **WARN**
    (missing protection)」，代码却让 HOLD 一律 PASS ——**代码与自身说明书相反**。
  - **与 S6 同源**：两者都建立在「HOLD 不会有 entry」这一**已被推翻的前提**上（见上条「S6 判定收窄」）。
    旧价位门控恒抹价位 → HOLD 带 entry 不可能出现 → 该豁免**永不被检验** = 又一处**死码掩盖的错前提**。
    GATE-ROUTE G2 改 (b) 放行价位后，**HOLD 带 entry 成为常态**（e2e 实证：中际旭创跑即 HOLD），
    于是「给了买入区间却没有保护位」会**静默 PASS** —— 正是 Q4 设立时要防的那件事。
  - **方向**：WARN 面**只增不减**（更严）→ 属**收紧**，不放松任何既有保护；不影响 hard-fail 判定。
  - **教训（S6 R7 补扫的再次实证）**：修一处错前提后，须**按该前提**再扫一轮所有依赖它的判据——
    我改 S6 时只扫了「S6」关键词，没扫「HOLD + entry」这个**前提本身**，故漏了 Q4。
- **① 段引用时效：一刀切「超 3 天」→ 按来源分档（2026-08-18·用户裁「按此顺序开工」）**
  - **对象**：[segmented-e2e-guide.md](../observations/e2e-runs/segmented-e2e-guide.md) ① 段**人工 checklist**
    的「`references` 的 `as_of` 是今天或近日 / 数据源超过 3 天 → stale warning」一行。
    **不是** [quality gate](e2e-quality-gate.md) 的 S1-S6 / Q1-Q7 —— **gate 代码一行未动**，无任何 hard-fail 档位变更。
  - **维度归属**：维度 3 时效性 · **承重边界：observe / WARN**（原判据本就是段间人工 warn，非阻断闸）。
  - **依据**：[实测分布](../observations/ref-freshness-asof-20260818.md)
    （14 份 `origin/main` **tracked** seg1 checkpoint · **104 条 reference** · R6 · 零网络可复现）。
  - **原判据实测表现（这才是改它的理由）**：76 条有效样本 **10 条越线（13%）**，逐条拆开
    **真阳性 0 条** —— 6 条是 `fred` 月度节律（44–53 天·**3 天线对月度数据物理上不可能满足**）、
    4 条是 `yfinance` 长周末（07-06 **周一**跑·07-03 独立日休市）。
    ⇒ **它不是空线**（空线是每次都响），**是指错方向的线：把节律当故障**。
    而真正没被它管到的——**27% 的引用根本没有时间戳**（`wisburg` 28/28 全空）——**静默溜过**。
  - **新判据**：按来源分档 —— 新闻超 2 天 / 美港股行情超 6 天 / A 股行情超 10 天 /
    宏观月度超 **80 天**（= 发布节律上限 ~75 + 余量；初版拟改判「是不是最新一期」，
    冷审发现**现场判不动**——审核现场查不了发布日历，等于把「响得不对」换成「不会响」，
    故改回可判的天数线，算术见[实测分布 §5](../observations/ref-freshness-asof-20260818.md)）/
    **无时间戳单独标注**（计数不判红）/
    **未来日期·非法格式单独一档 → 排查数据源**（本批 0 例，但那才是"源真坏了"的形态）/
    **表外来源单独标注「未定档」并触发定档**（冷审补——否则接入新源时其引用
    既不越线也不通过，wisburg 那 27% 静默溜过在新源上重演）。
    ⚠️ 依据的**独立观测口径**：104 条是字段条数，按 (跑批, 时间戳) 去重后非空独立观测
    仅 **26 个**（A 股 4 次·宏观 2 次），支撑度按此读。
  - **方向：判红面零变化 · 提醒面有得有失（如实记·别只读前半句）** ——
    **得** = 13% 误报归零（越线的全是节律不是故障）+ **27% 无时间戳**引用从静默溜过改为显式标注；
    **失** = A 股档由 3 天放宽到 **10 天**，**长假之外**若真有一条 5–9 天没更新的行情，
    **旧线会响、新线不响** 〔**2026-08-18 用户裁决：接受此代价，保持 10 天**〕。
    本判据从来只提醒不阻断（fail 面本就是零），故同 BB / BE / BF 先例
    **不走 §4「新检查一律 WARN 试用」**（那闸门是给**新增 fail 面**的）。
    ⚠️ 分档数字系首次投用，**一律带 📐 校准注 + 复核触发条件**。
  - **⚠️ 刻意留的余量（防下一个长假误报）**：A 股线定 **10 天**而非实测上限 1 天 ——
    **本批 14 份无一跑在春节 / 国庆长假**（休市 7–9 天），**实测上限不能当天花板用**；
    同理美港股定 6 天（实测 4 = 独立日连假）。这是**样本未覆盖**，不是判据放松。
  - **本次刻意没做的两件（各立 backlog·均须用户裁）**：
    - `FRESHNESS_WINDOW_DAYS["other"] = 400` **是五档窗口里唯一没有论证的**
      （[confidence.py](../../src/committee/facts/confidence.py) 注释仅「放宽」二字），
      而**全部外源因无 `data_kind` 落此档** → 13 个月前的新闻今天仍算新鲜。
      收窄 = **提高拦截面 = 承重变更**，按本节第 3 条须停下问用户 —— 本次未问，故未动。
      〔**2026-09-23 前向**：D1 用户裁 other **400 → 180 天**并补齐校准注（CRED.2.G2）—— 「唯一没有论证」已不成立〕
    - seg1 引用 `as_of` **全程无代码消费**（只渲染进水印段落 + 人工瞄一眼；
      审核环节根本不读该字段）→ 接自动检查牵动数据源与下游，**独立立项**。
      〔**2026-09-23 前向**：审核环节已开始读这批日期（CRED.2.G3）—— 所引出处过期会记进审核理由、该事实可信度落「有源但过期」；「全程没有代码在看」已不成立〕
  - **两套尺子从未对齐（记账不修）**：人工线 3 天 vs 代码线 `FRESHNESS_WINDOW_DAYS` 1–400 天，
    量的是同一件事、**差 133 倍**、互不知道对方存在。**本次只对齐人工侧**。

- **CRED 簇 1 GATE-TRUTH 四项登记（2026-09-08 · 节点 [S2 §4.7.6](../roadmap/S2.md) · 设计 pass [CRED §3.1](../plans/CRED-可信度地基三簇-设计pass-2026-09-08.md)）**
  - **本块登记的是「该查什么、算什么档」**；实现分别在 CRED.1.G1–G4 各自 PR（先登记后动码·本节第 1 条）。四项的**共同形态**：检查自己说了假话 —— 不是数据错，是「我核过了」这句话是假的。
  - **依据（2026-09-08 主干归档只读探针·R6 从 `origin/main` tracked 清单读·75 份有决策的归档）**：
    决策里「计划」的形态分布 = **(a) 无计划且无硬闸理由 2** / **(b) 硬闸切除 9**（例：OBEY-5 vote-divergence block）/ **(c) 现价早退 0** / **(d) 有计划且买入价有数 19** / **(e) 有计划对象但买入价为空 45**。
    〔09-09 复核：复核者按另一取样范围独立数出 (d)(e) = **23 / 46**，差在算哪些文件、**结论不变**；(a)=2 三次计数一致。〕
    🔴 **(a) 档两份全中、没有一例"正常的没计划"**（09-09 复核订正·原只点名一份）：`run-nf2_csi300-oil-rerun-post-66`（**ADD**）与 `run-pr8a-q3_blackrock-multi-asset-rebalance-2026`（**BUY**）—— 都带**完整仓位建议**、都无计划、都无硬闸理由；两道题都是**主题型 / 多资产问法**、无单一可定价标的。⇒ "没价位"本身不算错，**但 (a) 的理由不能写"决策本身无价位"**，否则 G1 落地后会对最该被点出来的形态（有仓位建议却无计划的 BUY/ADD）盖章"不适用"。
    🔑 **(e) 是大头**：今天 Q3 对它也判 PASS（`entry is null → PASS`）。⇒ 「没查到」的判据**必须判到数字层**，只看"计划对象在不在"会把这 45 例原样留成空过（坑表：判"有没有"须判到承重层·容器在≠内容在）。

  **① Q3 / Q4「没查到」不再印 PASS（CRED.1.G1 · ✅ 已落地 2026-09-09）**
  - ✅ **实现已合 main `fb6dcee`**（PR [#283](https://github.com/JunoChenZt/subagent-for-investment/pull/283)）—— 本条登记的判据与承重边界**逐条兑现**：N/A 档 + 四成因 + 判到数字层；53 份在册归档回放**只 PASS→N/A**（Q3 38 · Q4 25）、**整体判定变化 0 份**、`overall` 与 cli exit 不变 = 承诺的「fail 面零变化」实测成立。⚠️ 合并前 review 修一真 bug：判「填没填」若用真假值，`0` 占位符会被读成「没填」⇒ 该 FAIL 的滑进 N/A（**方向与本承诺相反**）—— 定案口径 = **写了 `0` 算写了**，落 placeholder FAIL。`DEFECT-GATE-NA-AS-PASS` 随之 close。
  - **维度归属**：维度 2 数字可信度（结构化代码检查）· **承重边界：Q3 由 PASS 改 N/A · Q4 的 WARN 档不动**；gate 新增 `N/A` verdict。
  - **原判据**：`if not ep: PASS`（Q3 detail 还写 "acceptable for HOLD/non-specific"）；`entry is null → PASS`。
  - **新判据**：`execution_plan` 为空 **或** `entry` 的 low/high **皆为 None** → **`N/A`**（不是 PASS）。〔09-09 实现时收准：**写了 0 = 写了** —— `{0.0, 0.0}` 是占位符，须落既有 FAIL 档；判 `is None` 不判真假值。初版用真假值判，让主干在册 `run-pr8a-q6_*` 从 FAIL 滑成 N/A、overall FAIL→WARN、exit 1→0 = 与本块「fail 面零变化」承诺相反，review 在合并前抓住〕detail 分三成因、理由原文照抄：
    (a) `hard_block_reason` 空 = **无硬闸理由的无计划**（实况 = 主题型 / 多标的问法、无单一可定价标的；**detail 不得写"决策本身无价位"**——两份实例都带完整仓位建议）；(b) `hard_block_reason` 非空且非 (c) = **系统切除**（风险闸 / OBEY-5）；(c) `hard_block_reason` 为「取不到…稍后重试」= 现价早退（[price_gate_node.py](../../src/committee/agents/price_gate_node.py) 也写该字段，**光靠字段非空分不开 (b)(c)**，按内容判）。
  - **方向**：**fail 面零变化**（PASS→N/A 不新增 FAIL/WARN）。`overall` 不受影响（N/A 既非 FAIL 亦非 WARN）；cli exit code（`overall != FAIL`）不变。
    ⚠️ **产物形状变**：`summary_line` 多一个 n/a 计数（「13 pass / 0 warn / 0 fail」→ 四段）。历史记录里的「13/0/0」是 point-in-time，**不改**。
  - **为什么不走 WARN 试用**：非新增检查、fail 面不增 —— 同 S6 收窄 / Q4 豁免收窄 / BF 先例。**但**它是 gate 结果的**新枚举值** → 按坑表「新数据形态流经多模块（N=4）」逐核下游：trace 渲染 / 汇总打印 / guide ⑨ 段读法 / [e2e-quality-gate.md](e2e-quality-gate.md) 判据表 —— **同 PR 按 R7 收口**。
  - **靶测前提（坑表：靶测依赖「某输入落在某状态」须先 assert 前提）**：(a)(b) 两条测例各自 `assert` 前提（`hard_block_reason` 空 / 非空）；(b) 的 fixture **逐字取自** `docs/observations/D1-ROOT-e2e/run1-micron-resume` seg9（OBEY-5 block·2026-09-08 取样）；(e) 一条取自 `_archives/run-01_nvda-after-strength.json`。反向变异：把 N/A 改回 PASS，新测试须红。
  - ⚠️ **另立判据、本次不判（09-09 复核后由"顺带记一例"改"整档两例全中"）**：「**有仓位建议却无计划**」（BUY/ADD + `position_size` 非空 + `execution_plan` 空）—— (a) 档两份**全部**是这个形态（`run-nf2_csi300-oil-rerun-post-66` ADD / `run-pr8a-q3_blackrock-multi-asset-rebalance-2026` BUY）。它该不该 WARN 是独立于 Q3/Q4 的另一道判据；**G1 实现时必须把 (a) 的 N/A detail 与这道判据分开**，不能让 N/A 把它盖住。样本 N=2、非零星异常，不混进本条。

  **② 风险闸 G1 数证据条数时排除错误条目（CRED.1.G2 · ✅ D5 已裁 2026-09-09 · 影子对账已落地 · ✅ 已合 main `163337a`（PR [#285](https://github.com/JunoChenZt/subagent-for-investment/pull/285)·2026-09-10·分支已删） · 复审十修：影子只给用户看）**
  - **维度归属**：维度 2（G1 = 强信心 + 证据 < 2）· **承重边界：G1 `severity="high"` → 可触发 hard_block**（[risk_gate.py](../../src/committee/agents/risk_gate.py) RW-1）⇒ 让 G1 更常响 = **提高拦截面 = 承重变更** → 按本节第 3 条**须用户裁（D5）**，**不自走**。〔设计 pass 原标「自走」系误判，本块更正〕
  - **原判据**：`len(r.evidence_log) < 2`，条目一律计数。
  - **新判据（拟）**：条目**引用的编号在表①登记值为错误 / 空结果形态**（`status="no_observations"`·[DEFECT-EMPTY-AS-FAILURE](backlog.md) 落地形态 / MCP `isError`）→ **不计**。
    〔**09-09 落地收准（R5·开工前核到 main）**：上面括号里两形态在**表①里今天都不可达** —— MCP 工具错误由 wrapper 抛异常、整源跳过、无 REF#；fred 空结果全键是 meta、0 条引用；wisburg 降级留痕进 `_meta`。能出现在表①的错误登记**只有历史形态**（DEFECT-MCP-ISERROR 修前·2026-06）：`data_key="text"`、登记值以 `API request failed` 开头（D1-ROOT run1 逐字）。识别器 = **一条登记值前缀的有限集**（`API request failed`·测试钉条数 1；PR #285 复审删掉了原第二条 wrapper 兜底串 `<server flagged isError` —— 它按构造只进 `raise MCPToolError`、永远到不了表①，是死条目）；**空值登记（`N/A` / `list(0)` / `dict(0)`）刻意不纳入** —— 109 份主干归档里被证据引用的空值登记 **0 条**、错误登记 **3 条（全在同一跑）**，没有数据支撑放宽。⇒ **新鲜跑批很可能零分歧**：这不是检查失效，是洞被上游堵住了；D5 的「3 跑零分歧不能升」正为此立。⚠️ **本识别器只认历史归档那一种措辞、不是"上游回归的第二道眼睛"**（回归多半换措辞；真要第二道眼睛该架在登记边界 = 新检查、须另登记）。落点 = [risk_gate.py](../../src/committee/agents/risk_gate.py) `check_g1_shadow`：`G1-shadow`（恒 warning·`details={roles:[{role,n_old,n_new,would_block,excluded:[{ref_id,data_key,value,claim}]}], would_block, would_newly_block}`·`would_block` 是 role 级、**闸级样本看 `would_newly_block`**（新口径本该拦 ∧ 旧口径 `check_g1` 没响；G1 已因别的 role 触发 = 非新增拦截））；`check_g1` 一字未动；升硬拦 = `check_g1` 加 `ref_lookup` 参数改用 `_count_evidence_excluding_errors`（**不是一行**：含两处调用点 + message + 旧测试跟上·清单在 risk_gate.py 注释块 ①–⑤·须用户裁）。**复审修（#285 review·2026-09-09）：影子只给用户看** —— `RiskGateFinding.is_shadow` 条目**不进** fund_mgr 决策提示词、**不进**逐条回应 pass、**不进**打码豁免数字集（`llm_facing_findings` 一处过滤；warning 的"必须被 fund_mgr 回应"契约对影子不适用），否则观测器污染被观测的决策；trace §④ 现渲染 `details` 明细。〕
    🔒 **走引用、不走文字**：主干归档逐字样本 `{"claim": "Institutional reports unavailable due to Wisburg API 503 error", "source": "Wisburg [REF#W-003]", "as_of": "", …}`（D1-ROOT-e2e/run1-micron-resume seg9）—— 条目本身**没有结构化错误标记**，claim 是自由文本，只有 `[REF#W-003]` 指向的登记值能判。按文字匹配 = 编 fixture 自洽（坑表 🔴）。
  - **方向**：**收紧**（G1 fire 面只增不减）。与「默认拒绝 + 豁免集」坑对照：排除条件是**正向识别**错误形态（有限集），不是豁免集。
  - ~~**D5 要裁两件**：(i) 做不做；(ii) 做的话，排除后**新增的 fire** 先按 `severity="warning"` 记 ≥3 跑（WARN 试用）还是直接 high。**建议 (ii) 先 WARN 试用**~~
  - ✅ **D5 裁定（用户 · 2026-09-09）：做；先只告警试用，不直接硬拦。试用形态 = 影子对账；升硬拦看「分歧全部人工坐实、零误拦」，不看跑了几次。**
    - **为什么做**：明知是错的证据条目还被当「有效支撑」算进去 = **错的数字伪装成对的**（本仓核心原则：不确定性诚实 > 数字好看）。不做 = 风险闸在「有错证据撑着」时保持沉默 —— **这比它多响几次更危险**。
    - **为什么不能直接硬拦（两个未量的不确定性）**：(a) **会多响多少** —— 排除后触发面扩大到什么程度是猜的（可能偶尔多响一次，也可能每跑都拦）；(b) **「错误条目」认得准不准** —— 无结构化标记、靠引用推，识别误判 = 排除的是好证据 = 闸因假信号拦人 = **自己写的守卫把 bug 钉成预期**（[坑表 2026-09-08 沉淀](workflow/09-known-pitfalls.md)）。两个没量之前上硬拦 = 承重变更凭猜测落地。
    - **试用怎么试才有用 —— 影子对账，不是只挂个 WARN**：每跑**同时算两个数** —— 旧口径证据数、新口径证据数；**只要两者不一致**，就把「被排除的条目、排除理由、按新口径本该拦」打进告警（`severity="warning"`）。**试用期内硬拦仍按旧口径**。这样每一次分歧都是**可审的样本**，不只是一条「我响了」。
    - **升硬拦判据**：试用期内**每一次「本该拦」都由用户逐条认定为真阳性、零误拦**。出现一次误拦 → 留在告警档，**先修识别再谈升级**。**≥3 跑是地板，不是放行条件**：3 跑里一次分歧都没有也不能升 —— 那说明样本没覆盖到触发场景，继续试。
    - **实现落点（G2 据此写）**：G1 内部产出 `n_old` / `n_new` 两个数；`n_old` 继续驱动现有 high；`n_old != n_new` 时另发一条 `G1-shadow`（warning）携带排除明细 + role 级 `would_block`（= 强信心 ∧ n_new<2 ∧ ¬(n_old<2)）+ **闸级 `would_newly_block`**（= 任一 role would_block ∧ 旧口径 G1 没响·试用期人工坐实的是它）；影子不进任何 LLM 消费面；升级 = 把 G1 切到 `n_new`（须用户裁·改动清单见 risk_gate.py 注释块）。

  **③ audit 改动四：`numeric_value` 为空 → `audit_notsure`（CRED.1.G3 · ✅ 已合 main `e7fe42b`·PR [#284](https://github.com/JunoChenZt/subagent-for-investment/pull/284)·2026-09-09 · 方案 C 用户 2026-09-09 裁 · 复核五修后定稿）**
  - **维度归属**：维度 2 数字可信度 · **承重边界：advisory**（audit 不是 gate；gate 读表①不读 audit·D1-ROOT）。
  - **原判据**：[audit_node.py](../../src/committee/agents/audit_node.py) 改动四 `if fact.numeric_value is not None and …` → 为 None 时整支跳过，fact 可落 `audit_passed`。
  - **新判据**：`numeric_value is None` **且正文含数字** → `audit_notsure`（"数值未提取·无法核"）；正文无数字 → 行为不变。**只降不升**，与改动四同一铁律。
    〔**09-09 落地收准 · 方案 C（用户裁）**：「正文含数字」= 剥掉出处标记（`[REF#…]` / `[W#…]` / `{ref:…}`）**再剥四类有限语义噪音**后仍有数字 —— 日期时间（ISO 日期 / N月N日N年N季 / Q1–4）· 裸 4 位年份 · 指数名里的数（标普500 / S&P 500…）· 证券代码（6 位 A 股 / .HK .SS .SZ）。**这是有限语义类、有先例**（base.py AD.2 §c 裸年份 / A 股码跳过），**不是开放豁免表**：计数（「20 份中至少 8 份」）、分位、周数不排除、本就该降。备选 A（任何数字）多降 9 条纯日期/名字噪音；备选 B（只认带量纲的数）仓内先例已判 treadmill 且漏「8100 点」类。〕
  - **方向**：收紧（`audit_passed` 比例↓）。**下游消费者**（坑表：改分母 = 行为变）：`audit_passed` 是可信度**入场门**（[confidence.py:78](../../src/committee/facts/confidence.py#L78)）→ 这批 fact 落 `unavailable` → **正文打码↑**（安全侧·读者可见）；段间 ⑧ `audit_passed ≥ 50%` 已是 observe（<5% 才排查）**不撞红，补校准注**；AO 分流（base.py）按 `audit_passed` 走老路，不受影响。
  - ~~**依据**：活体 **0 例**（条目自记）~~ 🔴 **09-09 订正：这句是错的**。用真实表①回放主干 **25 跑 1508 条事实**（seg9 断点 `state.common_context.references` · 最终归档不带表①）：原 `audit_passed` **139 条里 35 条是带量纲的真量值却无 `numeric_value`**（「2026Q1 营收 194.96 亿元，同比增长 192%」这种盖了通过章）。⇒ 病比登记估计的大得多；「活体 0」系把条目触发条件里的「拿到 🟢」（可信度档）误抄成 audit 层。**前后对照（登记要求·已跑）**：裸数字判据降 **55/139**（含 9 条纯日期/名字噪音）；**方案 C 降 46/139 = 33.1%、放过那 9 条、漏抓带量纲真量值 0**。〔**09-09 复核五修后定稿：降 48/139 = 34.5%（带量纲 37 + 无量纲 11）、漏 0**。复核抓出的是判据两头的偏差：①裸年份吃「1920 美元」②任何 6 位数吃「118000 万元」→ 逐 token 走 base.py 老先例的**整套守卫**（带货币/单位/小数点不算噪音·6 位须 A 股前缀），不只抄正则；③剥标记换本文件 `_LEGAL_STAMP_RE`（裸 core / 大小写漂移）④「N日」不吃均线周期（年只吃 4 位年）⑤加有界裸引用核 `X-NNN`；型号（H200 / 1.6T）是开放集刻意不追〕⚠️ **连带发现（不在本 goal 范围·记 backlog `DEFECT-NUMERIC-VALUE-NULL-BYPASSES-AUDIT4` 正文）**：35 条量值没提取出 `numeric_value` = 事实整理那步的**提取器本身漏得厉害**，本项是下游兜底、不是治本。

  **④ check① 绑错 vs 真搬运错的判别力（CRED.1.G4 · ✅ D4 已裁 · ✅ 已合 main `0e297ef`·PR [#286](https://github.com/JunoChenZt/subagent-for-investment/pull/286)·2026-09-10·合并前冷审十修）**
  - **维度归属**：维度 2 · **承重边界：hard-fail（EXEC-FLOOR 灾难指纹·北极星侧）· 档位不动**；改的是**判别力**。
  - **方向不对称（坑表：红线按方向划）**：拿不准**一律归"真搬运错"**（降级侧）；只有明确证据才允许判"绑错"。设计 pass 须列"哪种证据才算"，并 mutation 证不存在"绑错 → 放行"以外的升级路。
  - **验收两边都要**：G7 归档（[rp-g7-e2e-20260827](../observations/rp-g7-e2e-20260827/FINDINGS.md)）那条正确断言不再误拦 **且** [test_exec_floor.py](../../tests/test_exec_floor.py) 真搬运错用例全拦。只过一边 = 移了阈值、没提判别力。
  - **✅ 2026-09-10 裁定落地（[CRED-1.G4 §6](../plans/CRED-1.G4-绑错判别力-设计pass-2026-09-09.md)）**——承重边界**两处变动，均为用户显式裁**：
    1. **check① transcription 触发面收窄**（四道免检：量纲词 / 单位缩写 / 年份〔带价格守卫〕/ 百分比↔小数归一）—— 拒绝比不可比的、不判绑错；fail 面只减不增，按 S6 先例**不走 WARN 试用**；真阳性守护 + 反向变异靶测守住。
    2. **🔴 AI 复核可撤硬拦（原则 ① 的显式例外）**：机械判搬运错后由**不同 provider 家族**的模型复核，判 `false_positive` → 撤硬拦、`execution_plan` 保留、`FinalDecision.execution_plan_caveat` 打「存疑」标；`true_error` / `unsure` / 调用失败 / 不独立 / kill-switch 关 → 维持硬拦。原则 ①「LLM-judge 只能 advisory」在此**未被推翻**：复核员**不能 block、也不能干净放行**，只能把一次硬拦降到「存疑 + 给人看」档；三前提（独立性 / 输入隔离 / 输出封闭）焊在代码。真模型冒烟 8/8 两向（5 历史误报 + 3 合成真错）；⚠️ 自然真阳性仍 0。
    3. **Q8「check① 可见性」新增·WARN 试用**（§4 规则）：`execution_plan_caveat` 非空 → WARN(disputed)；`hard_block_reason` 含 check① → WARN(hard_block)；都无 → PASS。不判对错、只印三元组；升档须用户裁。
  - **下游消费者回审**（横切表补）：`overall` / cli exit 不变（Q8 至多 WARN）· `summary_line` 计数 +1 项 · trace_report 加 ⚠️ caveat 行 · fund_mgr 提示词**零变化**（`quality_flags` / `enforcement_log` / caveat 均不进提示词）。

  **横切 · 本簇改动的下游消费者一览**（动手前逐个追问"新形态下它的判定还是原来那个吗"）：`overall`（不变）· `summary_line`（+n/a 计数）· cli exit（不变）· `audit_passed` 入场门（G3 ↓）· AO 分流（不变）· 段间 ⑧（observe·补注）· 层② check①（吃 hard_block·G2 若做则 fire ↑）· BK 静默降级留痕（顺手·不关）。

  **⑤ Q9「辩论数字与本跑数据冲突」（CRED.3.G1 · D3 = B · 用户 2026-09-24 裁 · 设计 [3.G0 设计 pass](../plans/CRED-3.G0-辩论数字冲突检测-设计pass-2026-09-24.md)）**
  - **维度归属**：维度 2 数字可信度（辩论第一轮按设计断粮，模型凭训练记忆写旧行情——例：2026-08 空头写「美元指数维持在 105 以上」，同一跑事实清单里是 99.1）· **承重边界：advisory / WARN 试用（§4）·永不 FAIL**；升档须用户裁 + 试用期数据。
  - **判据**：读归档 `debate_sight`（[facts/debate_sight.py](../../src/committee/facts/debate_sight.py) 在装归档时对运行状态算）：键缺失 → **N/A**（旧归档·读不到≠没有）；值为空（无底可对：没辩论 / 没事实清单 / 事实里没有认得的指标）→ **N/A**；非空 → **WARN**（印前 3 条）；空列表 → **PASS**。只比**同一指标**，事实里同一指标任一值对上即不标（宁漏勿误）。
  - **依据**：[主干回放](../observations/cred-3-g1-debate-sight-replay-20260924/replay-output.md) 按辩论内容去重 48 份：无底可对 38 / 0 条 9 / 有冲突 1（即 8 月那处 DXY 105·同一句只记一条）。⚠️ 五类误报过滤是照主干 17 条误报写的（在答案上调出来的）——**WARN 本身不代表出错**，要人看片段判。
  - **下游消费者回审**：`overall` —— 出现冲突时整体落 WARN（与 Q8 同档·§4 试用期本意）；cli exit 不变（`overall != FAIL`）· `summary_line` 多一项：新跑 PASS / N/A / WARN 之一，**旧基线「15 pass」与新跑不能直接逐数比**（多了 Q9 这一项）· 段式 trace 第⑧/⑨段新增「④′ 辩论数字对账」一节（渲染器对运行状态调同一函数）· **决策链零变化**（不写运行状态、不进任何提示词）。

- 与 [docs/observations/e2e-runs/segmented-e2e-guide.md](../observations/e2e-runs/segmented-e2e-guide.md)（怎么跑）配合：本文是"跑完查什么"，guide 是"怎么一段段跑 + trace"。

### 演进历史

| 日期 | 变更 | 原因 |
|---|---|---|
| 2026-09-28 | **S4 改接离线审计·WARN 试用**（RDR-1.G1 · 用户裁处置 ①）：不再读 `enforcement_log` 幽灵规则名，直接调 `voice_guardrail_audit.py` 六项 detector 数 critical 违规；0 → PASS（印六项分布）/ ≥1 → WARN / 脚本不在 → N/A。**fail 面：纸面减一项**（那项从未生效过） | S4 读的记录全仓无生产者，恒报 0（backlog `DEFECT-GATE-S4-NO-PRODUCER`） |
| 2026-09-28 | **Q10–Q13 决策文本一致性四检查 新增·WARN 试用**（RDR-1.G0 · backlog CB C1–C3 + CA C5）：先登记后落码；每条 detail 自报前提，前提空 → N/A；`overall` 可因它们落 WARN、exit 不变；09-23 黄金归档回放三处已知阳性 + 括注漂移全响，CRED 1.G5 / 3.G2 归档回放零 WARN 误报（3.G2 计划被切 → 三条 N/A） | 09-23 黄金跑批止损两个数（4200 / 4313）、盈亏比 1.4:1 实算 1.86:1、高盛 4900 与隐含 4683 并存、括注三种措辞 + 残缺形，终局 15 项全绿——此前没有一道检查核「数字之间对不对得上」（backlog **CB** / **CA**）|
| 2026-09-24 | **Q9 辩论数字冲突 新增·WARN 试用**（CRED.3.G1·D3 = B）：先登记后落码；`overall` 可因它落 WARN、exit 不变 | 辩论第一轮凭记忆写旧行情，此前零检查看得见（backlog `DEFECT-DEBATE-STALE-PRIOR`） |
| 2026-09-10 | **D4 裁定落地**（CRED.1.G4）：① check① transcription 触发面收窄（四道免检·fail 面只减不增·不走试用）；② 🔴 **异模型复核可撤硬拦到「存疑」档**（原则 ① 显式例外·三前提焊代码·不能 block 不能干净放行）；③ **Q8 可见性 WARN 试用** | 用户裁：历史 268 份归档该硬拦路 5 响 5 误报 0 真错；复核员默认 gemini（与 pass0 deepseek / 决策 claude 不同家族）；冒烟 8/8 两向但真错侧为合成样本 |
| 2026-06-04 | 初版 6 维框架 + 4 原则 + 承重边界 | 用户提出 e2e 验收 4 维（稳定/质量/KPI/消耗）框架，对照现有 S1-S5/Q1-Q7 缺口梳理成共识 |
| 2026-06-04 | cold review 修正 5 处 | 🚩1 精确数字背书降 WARN 试用（web search 盲区+模糊匹配误报率未知）; 🚩2 D4 HOLD↔ep 加冗余断言 + 运行时委托登记; 🟡3 D6 HOLD 偏置独立标 🔴+反事实基准; 🟡4 D5 trigger 前向引用; 导读 #5 双问对齐 D5 全覆盖; §4 固化"新检查一律 WARN 试用期"规则 |
| 2026-09-09 | **D5 裁定**：G1 排除错误条目 —— 做；**影子对账式告警试用**（两口径并算·分歧打明细·硬拦仍走旧口径）；升硬拦 = 分歧全部人工坐实零误拦，≥3 跑是地板非放行条件 | 用户裁；两个未量的不确定性（多响多少 / 识别准不准）量清前不上硬拦 |
| 2026-09-08 | **CRED 簇 1 四项登记**：Q3/Q4「没查到」→ N/A 档（判到数字层）· G1 排除错误条目〔**待裁 D5**·G1 high 可触发 hard_block = 承重变更〕· 改动四空值 → notsure · check① 判别力〔待裁 D4〕。**先登记后动码**，实现在 CRED.1.G1–G4 | backlog 逐条复核后立 [S2 §4.7.6](../roadmap/S2.md)；主干归档探针 75 份：**计划对象在但买入价空 45 例 = 空过大头**，故 N/A 判据须判到数字层 |
| 2026-08-18 | **① 段引用时效由「一刀切超 3 天」改「按来源分档」**（observe/WARN·gate 代码零改动）；同日冷审补 3 处：宏观档由「判最新一期」改**超 80 天**（现场判不动 → 换可判的线）· 加**表外来源兜底档** · 依据补**独立观测口径**（26 个非 104 条） | 14 份 tracked 归档 104 条 reference 实测：该线 **13% 越线、真阳性 0** —— 越的全是节律（`fred` 月度 44–53 天 / `yfinance` 长周末 4 天），**不是空线是指错方向**；而 **27% 引用无时间戳**反倒静默溜过。**判红面零变化**故不走 WARN 试用闸；⚠️ **提醒面有真实损失**：A 股档 3→10 天，长假外 5–9 天的陈旧行情不再提醒（**用户裁决接受**），余量因**长假未进样本** |
| 2026-07-22 | **S6 判定收窄**：「HOLD 不许带 entry」→「**SELL/REDUCE** 不许带 entry」（维持 hard-fail） | 用户领域裁决：**「观望」是对当前价位的判断**，"现在别追、跌到 950-1000 值得买" = HOLD + 目标买入区间**互补非矛盾**，正是"装备决策者"该给的。原判据由「D4 HOLD→ep 切除」委托登记**逆推**而来（把 hard_block 的*结果*当成 HOLD 的*通则*），与 schema 契约（只禁 SELL/REDUCE）及 runtime 实况（无此逻辑）均不符。**因旧价位门控恒抹价位 → S6 恒不 fire = 死码 → 错前提潜伏至今**；GATE-ROUTE G2 改 (b) 放行价位后首次真跑才暴露。收窄=FAIL 面只减不增，故不走 WARN 试用期 |
