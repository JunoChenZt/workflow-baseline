# E2E Quality Gate Checklist

> 自动化 post-run 检查，覆盖稳定性（能不能跑完）和质量（内容能不能用）两个维度。
> 代码实现: [`src/committee/e2e_quality_gate.py`](../../src/committee/e2e_quality_gate.py)
>
> **本文 = 已落地的结构层子集**。完整验收标准（6 维框架 + 承重边界 + auto/judge/defer 分类、
> 含本文尚未实现的 时效性 / 内部一致性 / 答非所问 / 事后校准 等维度）见
> [e2e-acceptance-standard.md](e2e-acceptance-standard.md)。新增检查前先在那边登记维度归属。

## Usage

```bash
# 直接运行
python -m committee.e2e_quality_gate docs/observations/_archives/run-xxx.json

# 通过 CLI
committee quality-gate docs/observations/_archives/run-xxx.json
committee quality-gate docs/observations/_archives/run-xxx.json --json
```

Exit code: 0 = PASS/WARN, 1 = FAIL

---

## Stability Checks (S1-S6)

| ID | Check | PASS | WARN | FAIL |
|----|-------|------|------|------|
| **S1** | Pipeline completion | archive has `decision` + `query` | — | missing decision or query |
| **S2** | Schema completeness + value validity | 所有必填字段存在且合法：`decision` ∈ 合法 enum、`confidence` int/float ∈[1,10]、`time_horizon` 非空、`trigger_events` 非空 list | — | 缺字段或字段值不合法 |
| **S3** | Triage rework limit | 0 role hit rework_limit | 1 role | >=2 roles |
| **S4**（2026-09-28 改接·**WARN 试用**） | Voice hard-rule flags（离线审计 [voice_guardrail_audit.py](../../scripts/eval/voice_guardrail_audit.py) 的 m4/m5/m6/m7/m8/m13 六项 detector 现算） | 0 critical 违规（detail 印六项 pass/n/a 分布 + 读了什么） | ≥1 critical 违规（印 metric + 位置 + 片段） | —（试用期不 FAIL） |
| ↳ **N/A** | 审计脚本不在此环境 / 脚本抛错 → N/A 不是 PASS。⚠️ 旧判据「enforcement_log 里 rule ∈ {m4…m13}」全仓无生产者、恒 PASS（backlog `DEFECT-GATE-S4-NO-PRODUCER`），已删 |
| **S5** | Thesis sections | 所有 section 有 body | 有 section body 为空 | 0 sections |
| **S6** | SELL/REDUCE no buy-entry (defense-in-depth) | direction ∉{SELL,REDUCE} 或 无 entry 值 | — | SELL/REDUCE 但 `execution_plan.entry`（买入区间）有值 = 语义冲突（schema 锁 entry 为"买入区间"）|

## Quality Checks (Q1-Q13)

| ID | Check | PASS | WARN | FAIL |
|----|-------|------|------|------|
| **Q1** | Confidence range | conf ∈ [4, 8] | conf < 4 or > 8 | conf missing |
| **Q2** | Directional calls coverage | >=6/total roles 有 dc | 3-5 roles | <3 roles |
| **Q3** | Entry price plausibility | entry 真实价位 | — | entry = 0.0/1.0 placeholder 或 low > high |
| ↳ **N/A**（2026-09-09） | 无 execution_plan **或** entry 的 low/high **皆为 None** → **N/A 不是 PASS**（⚠️ **写了 0 = 写了**：`{0.0, 0.0}` 是占位符，落 FAIL 档不落 N/A —— 判 `is None` 不判真假值，初版在此破过、review 抓住）；detail 分四成因：`no_plan`（无硬闸理由的无计划）/ `cut_by_gate`（硬闸切除·EXEC-FLOOR / OBEY-5 / 风险闸）/ `price_unavailable`（现价早退）/ `empty_entry`（计划对象在但无价位数字·探针大头 45/75）。`value="n/a/<cause>"` | | |
| **Q4** | Stop-loss plausibility（方向感知） | level 合理 | 做多 stop>=entry.low；**有 entry 但无 stop（含 HOLD·缺保护位）** | level = 0.0/1.0 placeholder |
| ↳ **N/A**（2026-09-09） | 无 execution_plan，或 **无 stop_loss 且 entry 的 low/high 皆为 None** → **N/A 不是 PASS**（entry 写了 0 仍算「给了买入区间」→ 没止损照旧 WARN）（原「无 entry → PASS」已废）；成因同 Q3。**有 stop_loss 时照常判 level（原有行为不动）；WARN 档不动**。53 份归档回放：Q4 N/A 25 / PASS 26 / FAIL 2（FAIL 为既有占位符止损） | | |
| **Q5** | Evidence quality (EVID-1) | misattributed <= 30% | 31-50% 或 enforcement_log 缺失 | > 50% |
| **Q6** | Scenario completeness | >=3 scenarios from >=2 roles | >=3 from 1 role | 0 scenarios |
| **Q7** | Core risks count + mitigation quality | >=3 且各有实质性 mitigation | >=3 但有空泛 mitigation；或 1-2 条 | 0 |
| **Q8**（2026-09-10 · **WARN 试用**·advisory） | Evidence mismatch visibility（EXEC-FLOOR check① 响没响、响在哪条事实上） | check① 未响（无硬拦、无存疑标）—— **PASS 不是 N/A**：检查跑了、没响 | `execution_plan_caveat` 非空（复核撤拦·计划保留但**存疑**·`value=disputed`）**或** `hard_block_reason` 含 check①（硬拦切除·`value=hard_block`）；detail 印三元组「fX: fact 值 ↔ 登记值 @编号「出处 context」」 | — |
| **Q9**（2026-09-24 · **WARN 试用**·advisory） | Debate numbers vs run facts（辩论里的指标数字与本跑事实清单同指标对不上） | 对过了、都对得上 —— 读归档 `debate_sight` 为空列表；**键缺失（旧归档）或值为空（无底可对）→ N/A 不是 PASS** | `debate_sight` 非空：印前 3 条「side R轮 指标=辩论值（本跑值）」；只标记不纠正，WARN ≠ 出错，要人看片段判 | — |
| **Q10**（2026-09-28 · **WARN 试用**·advisory） | Prose vs plan price consistency（散文里的止损 / 止盈 / 入场价位 ↔ `execution_plan`；触发器带「止损」的 threshold ↔ `stop_loss.level`） | 抓到的价位全部一致 | 任一不一致（印位置 + 片段 + 结构化值） | — |
| ↳ **N/A** | `execution_plan` 没有任何价位数字（本跑无效·含被硬闸切除）；或散文里没抓到带价位数字的关键词句 → **N/A 不是 PASS**。数字归最近关键词，紧跟「支撑 / 阻力 / 均线」的算参照位不比 |
| **Q11**（2026-09-28 · **WARN 试用**·advisory） | Recomputable numbers（「盈亏比 A/B 计约 R:1」「现价…X 的 Y%」「距 X … Y%」按 `current_price` 复算） | 复算全部在 5% 内（百分点另给 1 点绝对容差） | 任一算错（印复算值） | — |
| ↳ **N/A** | 没有 `current_price`；或散文里没抓到可复算表述 |
| **Q12**（2026-09-28 · **WARN 试用**·advisory） | Same institution, multiple values（同一机构的价格预测：显式值 + 「现价…的 Y%」隐含值；带「下调 / 上调 / 从 X 至 Y」的修订句不算） | 各机构值内部一致 | 同一机构任两值差 >2%（列两处） | — |
| ↳ **N/A** | 没有带数值的机构价格预测提及。机构名是闭集（[代码](../../src/committee/e2e_quality_gate.py) `_INSTITUTION_RE`·从黄金跑批 grep 得出）|
| **Q13**（2026-09-28 · **WARN 试用**·advisory） | Caveat wording set（「未核实」括注只能来自 [caveats.py](../../src/committee/caveats.py) `CAVEAT_ALLOWED`） | 全部在集合内（零括注也是 PASS） | 措辞漂出集合 / 缺左括号的残缺形（点名 + 位置） | — |

## Record-only (D1)

| ID | Check | PASS | WARN | FAIL |
|----|-------|------|------|------|
| **D1**（2026-09-14 · 记录型·不判） | Degradation count（本跑退了几步 + 逐条码·读归档 `degradations`） | 永远 PASS·只印数 | — | — |
| ↳ **N/A** | 旧归档没有 `degradations` 键 → N/A（读不到不等于 0） |

## Overall Verdict

> **N/A 档（2026-09-09·CRED.1.G1）**：既非 FAIL 亦非 WARN → **不影响 overall、不影响 cli exit code**（`overall != FAIL`）。但 `summary_line` 固定四段「N pass / N warn / N fail / **N n/a**」，n/a **永不并进 pass** —— 报告上看得见「这项没验过」。历史记录里的「13 pass / 0 warn / 0 fail」是 point-in-time，不改。登记：[acceptance-standard §4 ① 块](e2e-acceptance-standard.md)。

- **PASS**: 全部 check PASS 或 N/A
- **WARN**: 有 WARN 但无 FAIL — 可落地到 ledger，需在 notes 标注 warn 项
- **FAIL**: 有 FAIL — **不进入正式 `_archives/` 或 `run-counter.md` ledger**，需修复后重跑

注：`--json > archive.json` 产出的是临时文件，FAIL 指不进入正式归档目录和 ledger。

## Gate 集成

每次 e2e 跑完后执行 quality gate：
1. `python -m committee.cli analyze "query" --json > archive.json`
2. `python -m committee.e2e_quality_gate archive.json`
3. PASS/WARN → 落盘到 `_archives/` + 补 `run-counter.md` ledger
4. FAIL → 不落盘，排查问题

## 跑批模式：一口气 vs 段式（排查 / 续跑）

上面 §Usage 是**一口气跑完**的常规模式（gate 验产出质量）。当出现以下场景时切到
**段式跑**——按 9 段在屏障节点逐段停 + 存 checkpoint + 出全量 trace 报告，便于
定位 / 续跑 / 不重复烧 token：

- e2e gate 标 FAIL，需要定位是哪个段（context / research / triage / debate / votes / pass0 / decision）出问题
- prompt 或 schema 调整后想只重跑下游某段、不重跑前面已 OK 的段
- 想看每次 LLM 调用的完整 prompt + 原始输出 + 段内 state diff

详见 [docs/observations/e2e-runs/segmented-e2e-guide.md](../observations/e2e-runs/segmented-e2e-guide.md)。
入口：`python -m committee.cli analyze "<query>" --stop-after <段 key>`；
真值源代码 [`src/committee/segments.py`](../../src/committee/segments.py)。

段式跑同样产出可喂给 quality gate 的 archive（最后一段 `decision` 跑完时 state 完整），
但日常 gate 验证仍优先用一口气模式（更接近生产路径、不付段式 trace 内存代价）。

## 已知限制 & TODO

- **Q3/Q4 价位真实性**：只拦 0.0/1.0 占位符，不能拦模型编出的 99999 / 假价位。⚠️ **2026-07-22 起「谁来兜」已明确**：离谱价位的守门由**运行时 EXEC-FLOOR check②**承担（读表① 真实市场价·entry/止损 3x、止盈 5x 数量级判据）——gate 侧 Q3/Q4 仅作冗余断言、不是主保护。gate 侧若要补精度，仍可接 `price_snapshot` 做 ±X% 检查。
- **Q6/Q7 只计数不审质量**：3 个 scenarios / 3 个 core_risks 不代表可用。Q7 已加 mitigation 空泛检测（first step）；scenario 的触发条件/影响/应对质量需 LLM-judge（按 acceptance-standard 原则① = advisory only）。
- **链接路径校验**：相对路径正确性靠 CI / 本地 link checker 脚本（session 内已有 python 校验）。

## 指标演进

| 日期 | 变更 | 原因 |
|------|------|------|
| 2026-09-28 | **S4 改接离线审计**（RDR-1.G1·WARN 试用）：删幽灵规则名判据，调 `voice_guardrail_audit.py` 六项 detector；0 违规 PASS / ≥1 WARN / 脚本不在 N/A | S4 两个多月恒报 0，与真实跑批无关（`DEFECT-GATE-S4-NO-PRODUCER`）|
| 2026-09-28 | **Q10–Q13 决策文本一致性四检查**（RDR-1.G0·WARN 试用·advisory）：散文↔计划价位 / 可复算数字 / 同机构多值 / 括注措辞集合；前提空 → N/A；`overall` 可落 WARN、exit 不变。同日补 D1 进本清单 + 加「代码注册项 ↔ 本清单」守护测试（`tests/test_e2e_quality_gate_rdr1.py`） | 09-23 黄金跑批止损两个数 / 盈亏比算错 / 高盛两个值 / 括注三种措辞，15 项全绿（backlog CB / CA）；D1 此前漏在清单外 |
| 2026-06-03 | 初版 S1-S5 + Q1-Q7 | PR-8c gate 首轮 e2e 实证设定 |
| 2026-06-04 | S2 加值校验 · S4/Q5 缺失→WARN · Q2 ≥6 · Q4 方向感知+null 语义 · Q7+mitigation · S6 HOLD 冗余 · 措辞修正 | cold review 9 项修正（acceptance-standard 共识后首次同步） |
| 2026-07-22 | **S6 判据收窄**：「HOLD 不许带 entry」→「**SELL/REDUCE** 不许带买入区间」（维持 hard-fail·FAIL 面只减不增·故不走 WARN 试用期）+ 补 16 条靶测（此前**零覆盖**） | GATE-ROUTE G2·用户裁决。原判据由「hard_block 切计划降 HOLD」**逆推**而来（逆命题当原命题），与 schema 契约（只禁 SELL/REDUCE）及 runtime 实况均不符。「观望」是对*当前价位*的判断——HOLD + 目标买入区间**互补非矛盾**。**因旧价位门控恒抹价位 → S6 恒 PASS = 死码 → 错前提潜伏至今**；G2 改 (b) 放行价位后首次真跑才暴露。详见 [acceptance-standard §4](e2e-acceptance-standard.md) |
| 2026-09-24 | **Q9 辩论数字冲突**（CRED.3.G1·WARN 试用·advisory）：读归档 `debate_sight`；冲突 WARN / 零条 PASS / 旧归档或无底可对 N/A。`overall` 可落 WARN、exit code 不变 | 辩论第一轮凭记忆写旧行情此前零检查看得见；登记见 [e2e-acceptance-standard](e2e-acceptance-standard.md) §4 ⑤ 块 |
| 2026-09-10 | **Q8 check① 可见性**（CRED.1.G4·WARN 试用·advisory）：硬拦切除 / 复核撤拦存疑 两态各印三元组；没响 = PASS。`overall` / exit code 不变 | 历史 268 份归档 check① 硬拦路 5 响 5 误报，每次都要人翻归档才知拦的是什么；D4 裁复核员可撤硬拦到「存疑」档 → 撤了什么必须在报告上看得见。详 [acceptance-standard §4 ④](e2e-acceptance-standard.md) |
| 2026-09-09 | **Q3/Q4「没查到」→ N/A 档**（CRED.1.G1）：无计划 / entry 无价位数字不再印 PASS；detail 分四成因（no_plan / cut_by_gate / price_unavailable / empty_entry）；summary_line 四段；WARN 档与 overall 不动 | G7（08-27）实锤：计划被 EXEC-FLOOR 切除、gate 13/0/0 全绿、理由印 "acceptable for HOLD" —— 「没填」与「被切」不可区分；1.G0 探针：计划对象在但 entry 空 45/75 是大头，只看对象在不在会留成空过 |
| 2026-07-22 | **Q4 HOLD 豁免收窄**：`HOLD 一律 PASS` → 判据改看「**有没有给 entry**」（有 entry 无 stop → WARN·含 HOLD）+ 补 10 条靶测 | **S6 同源错前提的漏网**（改 S6 时只扫「S6」关键词、没扫「HOLD+entry」这个*前提本身*）。函数 docstring 自陈「HOLD with entry but no stop: WARN」，**代码却与之相反**——旧价位门控恒抹价位 → HOLD 带 entry 不可能出现 → 该豁免永不被检验 = 又一处**死码掩盖的错前提**。(b) 后 HOLD 带 entry 成常态 → 「给了买入区间却没保护位」静默 PASS。WARN 面只增不减=收紧。回测两 G4 run 判定不变。详 [acceptance-standard §4](e2e-acceptance-standard.md) |
