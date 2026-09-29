# 段式 e2e 跑批指南（一段一段跑 + 全量 trace）

> **为什么**：完整 e2e 一次跑到底，中途某段出问题很难定位，且每次重跑都从头烧
> token。段式跑 = 跑到一个**屏障节点**就停、存档、出一份详尽 trace 报告，确认无误
> 再续跑下一段。任一段失败，前面各段的产出和 trace 都已落盘，排查 + 重试只针对那一段。

## 9 个停点（单一真值源：[`src/committee/segments.py`](../../../src/committee/segments.py)）

| # | key | 停在 | 干了啥 |
|---|---|---|---|
| 1 | `context` | `build_context` | 查询分类 + 公共上下文 |
| 2 | `research` | `research_done` | 8 个 analyst 并行研究 |
| 3 | `triage` | `triage_passed` | triage + rework 返工环 |
| 4 | `debate1` | `debate_bear_opening` | 辩论 R1 opening（+ ds_researcher 并行）|
| 5 | `debate2` | `debate_bear_rebuttal` | 辩论 R2 rebuttal |
| 6 | `debate3` | `debate_done` | 辩论 R3 closing |
| 7 | `votes` | `ds_debate` | 10 个 voter 投票 + ds_debate |
| 8 | `pass0` | `risk_gate_pre_check` | ds_merge + audit + 前置风控 |
| 9 | `decision` | END | fund_manager + 风控闸门 + hard_block |

## 怎么跑（每段必须人工审核放行）

**核心纪律**：每段跑完 → 打开 `trace.md` → **按下方 §段间审核 checklist 逐项检查** → 确认通过才执行续跑命令。**不得跳过检查直接续跑**。

**轮次隔离（硬规则）**：Claude 在同一轮回复中**严禁连续跑多段**。每段跑完后，呈现 checklist 审核结果即结束该轮回复，等待用户下一条消息明确放行才跑下一段。利用对话轮次的天然隔离强制人工审核。违反 = 触发 §2.7 Q5（标准降低）。

**第一段**（全新 run，自动建 `run-<slug>-<时间戳>/` 目录）：

```bash
python -m committee.cli analyze "NVDA 还能追吗" --stop-after context --auto-confirm
```

> ⚠️ **首段必带 `--auto-confirm`**（ticker-confirm G2）：全新 run 跑图前有交互式 ticker 确认闸，
> TTY 下会停下等用户确认标的。段式 e2e 是自动化跑批 → 必须 `--auto-confirm` 跳过，否则**卡死等输入**。
> （续跑命令走 `--resume`，不经确认闸，无需此 flag。非 TTY/管道环境也会自动跳过。）

### ⚙️ 唯一例外：**真人验收跑**（2026-08-28 立·backlog BW）

> 🔑 **先说清界限**：上面那条「必带 `--auto-confirm`」**一字未改**，对**所有段式 e2e** 照旧成立。
> 本节说的是**另一种跑法** —— 它**不是段式 e2e**，只是恰好复用同一个命令。

**什么时候不带 `--auto-confirm`**：当你要验的**就是交互闸本身**（跑图前的标的确认闸 /
出计划后的[计划确认闸](../../../src/committee/cli.py)）。这类跑法的目的是**让它停下来等人** ——
"卡死等输入"在这里不是故障，是**被验的行为**。

```bash
python -m committee.cli analyze "黄金还能追吗" --stop-after context     --trace-dir "docs/observations/<节点>-human-<日期>"
```

**四条纪律**：

1. **必须在真终端里跑**（代码判的是"输入是不是终端"）。管道 / CI / 非 TTY 环境**照旧自动跳过确认闸** ——
   在那些地方不带这个 flag 也停不下来，不是"没生效"。
2. **它不产出段式 e2e 数据点**：不进段间审核 checklist 纪律、不用于攒质量门样本、
   不与常规跑批混在同一个 run 目录。产出另开具名目录（如 `rp-g5b-human-20260828/`）。
3. **必须留一份验收记录**（`ACCEPTANCE.md` 一类）：逐条验收项 + 实跑证据 + 没过的那条怎么处置。
4. **只在验交互闸时用**。拿它跑常规 e2e = 每段停下等人，既慢又把段间纪律搅乱。

**为什么值得单独开这一格**（不是为了放松标准）：2026-08-28 首次真人验收，
**四条验收里查出一条单测照不出的缺陷** —— 确认环把用户改好的计划扔了
（`apply_edit` 函数级完全正确、11/11 反向变异 KILLED，坏的是**它的返回值被谁扔了**：
零件合格、装错了）。⇒ 交互闸这类东西，**函数级测试有系统性盲区**，真人跑是补盲的手段。
证据：[rp-g5b-human-20260828/ACCEPTANCE.md](../rp-g5b-human-20260828/ACCEPTANCE.md)。

⚠️ **本例外不适用于「懒得加 flag」**：常规段式跑漏带 `--auto-confirm` 导致卡死，
是操作错误，不是走了本节这条路。

跑完后：
1. 打开 `seg1-context.trace.md`
2. 按 §段间审核 checklist 的「① context」表逐项检查
3. **全部 ✅ 后**，执行打印出的续跑命令：

```bash
python -m committee.cli analyze --resume "<上段>/seg1-context.checkpoint.json" \
    --stop-after research --trace-dir "<run 目录>"
```

4. 重复：打开 trace → checklist → 放行 → 下一段……直到 `decision`。

**任一 checklist 项标 ❌**：停下排查，不续跑。修复后可从当段 checkpoint 重跑该段（`--resume` 同一个 checkpoint + 同一 `--stop-after`），前面各段不重跑。

- `--stop-after` 支持 key 或序号（`research` == `2`）。
- 🔑 **定向 resume 验某个改动前，先查那个节点属于哪一段**（真值源 = [`segments.py`](../../../src/committee/segments.py) 的 `members`）——
  **从该节点所在段的前一段 checkpoint 起跑**，否则 resume 会加载**旧代码已经写好该节点产物**的 checkpoint、
  你的改动**根本不执行 = 白跑一次**。**最容易踩的一处**：`audit_pass_0_5` 属 **seg8（pass0）**、不属 seg9 ——
  改 audit 却按惯例做 seg9-resume，四个改动一个都不会跑（2026-08-05 开工前核实避开）。
  ⚠️ 别照搬 07-20 / 07-22 那批 seg9-resume 先例：**它们改的是 seg9 里的门，落点不同**。
  ⚠️ **拿旧断点续跑 seg8/9，决策可能被时效闸改写**（2026-09-24 CRED.3.G2 实测·节点收口 adopt）：CRED.2.G3 起审核读出处日期，断点里的现价出处按**今天**算会过期（现价窗 1 天）→ 可信度落过期 → EXEC-FLOOR check③ 切计划、BUY 降 HOLD。07-20 / 07-22 / 08-05 / 09-10 那批续跑先例都在 2.G3 之前，没有这个现象。⇒ 验与时效无关的改动时，结论里注明「决策改写来自旧断点时效」，**别当回归、也别当决策质量样本**（出处 [3.G2 FINDINGS](../cred-3-g2-e2e-20260924/FINDINGS.md) §4）。
- `--trace-dir` 缺省时：resume 落上一段同目录、全新 run 落 `docs/observations/_checkpoints/run-<slug>-<ts>/`。
  ⚠️ **该默认落点自 2026-07-29 起已 gitignore**（跑批工作目录·非归档）→ **产物提交不上**。
  要留证据就**显式传 `--trace-dir <具名目录>`**（如 `docs/observations/<节点>-e2e/run-<slug>-<日期>/`，
  与既有 `m1-full-e2e-*/`、`gate-route-e2e/` 同规格）；默认落点只当 scratch 用。
- 想一口气跑完仍用旧法（不传 `--stop-after`），但**跳过了段间检查，风险自担**。
- ⚠️ **resume 重跑语义（如实，2026-06-24 修正）**：上面「前面各段不重跑」对 **analyst / build_context** 成立（skip-wrapper no-op，已产出的不重算），但**不**对 **triage / rework_dispatcher**——它俩**每次 resume 都重跑**，是**有意设计**（[`graph.py`](../../../src/committee/graph.py) "Never skip-wrap these two"：若 skip-wrap 会致 resume 陷无限 no-op 死循环；triage 是确定性规则、对固定报告幂等，重跑不改结论）。
  - **E2E-RESUME 修复（2026-06-24，`rejected_roles` 持久字段）之后**：被 triage **reject** 的 analyst（其 report 置 None）**不再**每段被误判"没做完"而重跑。修复前实测 `macro` seg4-9 **每段都重跑**——根因是 reject 信号只活在两个会丢的地方（report=None 在 load 缺席、`triage_verdicts` 被 triage 重跑覆写），第 2 次 resume 即丢；且 macro 走弱模型重跑引入**非确定性**、改了上游覆盖度 → 动摇了"分段跑 ≈ 整跑"的等价前提。现由 `rejected_roles`（reducer 累积、跨 checkpoint 持久、triage 重跑碰不到）让 analyst 跳过谓词跨多次 resume 稳定认得已 reject 的 role。

## 每段产出 3 件 + 1 份配置快照（落在 run 目录）

- `seg{N}-{key}.trace.md` — **排查主入口**：
  - ① Mermaid 全 pipeline 流程图（本段节点🟩高亮 / 已跑⬜ / 待跑⬛，框内标产出的 state key）
  - ② 本段数据流（节点 | 消费 | 产出）
  - ③ **调用了哪些** —— 每次 LLM 调用的 tag/model/token/cost 汇总 + **完整 system+user prompt 和模型原始输出**（md 内截断，全文见 jsonl）
  - ④ **输出了哪些** —— 段内 state diff，按类型渲染（报告/投票/辩论/决策…）
  - ⑤ token 小计（本段）+ 累计
- `seg{N}-{key}.calls.jsonl` — 每行一次 LLM 调用的**全量** prompt + 输出（程序消费用）
- `seg{N}-{key}.checkpoint.json` — 该段完整 state，供下一段 `--resume`（含累计 token usage）

失败时落 `FAILED-<ts>.checkpoint.json` + `FAILED-<ts>.calls.jsonl`（崩溃前已捕获的调用）。

- **降级提示**（2026-09-14 起·backlog BK.1）：每段 `trace.md` 头部若出现 「⚠️ **本跑降级 N 处**」块，说明这一段（或之前各段）有退而求其次的地方 —— **段间对比数字前先看这里**，它解释了为什么某些资料缺、某路分析是兜底版、某个检查没跑成。末段的 `archive-from-final.json` 里同一份清单落在 `degradations` 键，终局质检的 **D1** 把条数摆出来（**记录型·不判**，理由见 [e2e_quality_gate.py](../../../src/committee/e2e_quality_gate.py) 里 `_d1_degradation_count` 的 docstring）。⚠️ 它只列**有结构化留痕的**那些；系统里还有一批退路目前只写在日志里（[BK.0 盘点](../../plans/BK-G0-inventory-2026-09-14.md)）。
- `config-snapshot.json` — **本 run 的配置基线**（2026-09-14 起·backlog BJ.3）：跑批**起步**就写（失败跑也有），逐键「生效值 / 来源层（进程 env · .env · 代码默认）/ 走没走兜底」+ **逐角色实配模型**；密钥只记「已设·长度·指纹」永不记值。
  **段间要核「这次跑用的什么配置」一律读它，不翻 `.env`、不抄代码常量**（06-16 拿符号名当 env 名查空误判的那类事，就是这么来的）。
  后续段起步与它比对，**有漂移** → 该段 `trace.md` 头部当场打 ⚠️ 块 + 另存 `seg{N}-{key}.config-drift.json`；无漂移一字不加。
  同一份形状随时可看：`python -m committee.cli config show --json`；单个键：`committee config explain <KEY>`（问错名字会报错并给真名）。

## 段间审核 checklist（每段放行前必过）

> **验收标准真值源**：[docs/governance/e2e-acceptance-standard.md](../../../docs/governance/e2e-acceptance-standard.md)（6 维框架）。
> 本节把 6 维拆到 9 段——每段只列**该段能查且该查**的项。D6 事后校准是终局维度、D2/D3/D5 部分子项需 LLM-judge（标 🔵），此处只列人工可判/trace 可见的。
>
> **怎么用**：打开该段 `trace.md`，按下表逐项对照。trace.md 的 §③（调用明细）和 §④（state diff）是主要数据源。全部 ✅ 才放行；任一 ❌ 停下排查不续跑。
>
> ---
>
> ### ⚠️ 这套 checklist 量的是什么、不量什么（边界声明）
>
> **量**：**形态完整性** —— 节点有没有跑、产出有没有形状、字段有没有填。
> **不量**：**内容真伪** —— 数字是不是编的、引用锚是不是存在、论据是不是真的。
> 内容真伪归 **audit / 打码门 / 终局 quality gate** 管，分工本身合理，但**别把两件事读成一件**。
>
> **现成反例（不是假设）**：2026-07-31 那次跑，段间 ①–⑨ 全过、quality gate 13/0/0，
> 而辩论正文里躺着 **5 个编造的引用锚**（`REF#Y-009~Y-013`，references 实止于 `Y-008`），
> **全程没有任何一条数字线看得见它**（→ [backlog BC](../../governance/backlog.md)）。
> 更硬的证据：拿 4 次**已知投毒**的对抗 run 量同一套线，**除 `key_claims` 外每一项都落在正常 run 区间里、分不出来**
> （[对账报告 §3](../../governance/e2e-guide-threshold-audit-20260731.md)）。
>
> **第二个反例，比上一个更硬（2026-08-04 BC 探针跑）**：这次不是"编造的锚没人看见"，
> 是**绑错实体的锚一路走到读者面前**——13 条最高信任事实里 **10 条**的锚指向不相干字段
> （正文写 `PE 30.79x`，锚点开是 `price`），`ROE 114%` 在附录被标 **verified**、正文**零 caveat**，
> 而同段一个诚实的 web 来源数字反倒挂着「（未独立核实）」= **信任信号与真实可靠性反着来**。
> 段间 ①–⑨ 全过、终局 gate **13/0/0**，其中一项**名叫「证据误归因」的检查报 0%**
> （→ [DEFECT-ANCHOR-MISBIND](../../governance/backlog.md) 🔴→✅ **CLOSED 2026-08-14**（随「数字出处」问题域[封卷](../../governance/number-provenance-endgame.md)））。
> ⇒ **绿灯不但不等于"内容真"，连"名字写着在管这件事的检查"都可能没在管。**
>
> **所以：「段间全绿」≠「这跑没问题」，只等于「流程没断」。**
>
> ### 📐 数字线的校准惯例（2026-07-31 立·对账报告建议 7）
>
> 本节每条**带数字的判据**旁必须注明三件事：**定于何时 · 依据什么实测 · 下次何时复核**。
>
> 立这条惯例的理由是实测出来的：全表 12 条数字线里，**唯一有校准记录的（① 分类 token 线）
> 也正好是唯一「紧但不空」的线** —— 这不是巧合。没有校准记录的线要么空（每次判失败）、
> 要么钝（余量大到永远不响）。**新增数字线时一并写校准注，否则不要加。**
>
> ⚠️ **2026-08-14 后续（本惯例的第一个反面教训·不改上段结论）**：① 那条线**已由 ≤800 上移至 ≤900**，
> 「紧但不空」这个属性**随之让出**（余量约 12%）—— 故上段「唯一紧但不空」的实例现已**不再成立**，
> 但结论（有校准记录的线才有成色）不变。**真正的教训在另一头**：那条线的复核触发条件
> （「classify prompt 再次重写时」）写得好好的、也**确实在六到八月间被满足了三次**，
> 却**没有任何机器会喊它** —— 直到读数真的越线才被逼着补做。
> ⇒ **写校准注只解决「线是怎么来的」，不解决「谁提醒你该复核了」**。后半仍是敞口，
> 形态同 [backlog BN](../../governance/backlog.md)（判据到线没人执行）。
>
> **兜底口径**（别让惯例变成空文）：数字线分三档 ——
>
> - ① **有 📐 校准注**：定于何时 / 依据什么 / 何时复核都写着；
> - ② **标 📐 未校准**：判据本身没进 07-31 那轮对账，**连「它准不准」都还没测过** —— 下轮对账优先补；
> - ③ **两条【存活探针】**（⑥ 6 轮 / ⑦ 10 voter）：零方差、拓扑决定，不需要校准注。
>
> 注意 ② 那档**不在** [对账报告 §1 总表](../../governance/e2e-guide-threshold-audit-20260731.md) 里
> ——总表只覆盖被测的 12 条，**"没被测"和"测了发现钝"是两回事**，前者连数据都没有。
> 当前 ② 档已知有：② 段每角色调用数 ≤3 / `as_of` 超一周 · ④ 段 `facts_inventory ≥5`。
> 〔**2026-08-18 摘除一条**〕~~① 段 `as_of` 超 3 天~~ —— 已由 [104 条实测](../ref-freshness-asof-20260818.md)
> 校准成**按来源分档**、转入 ① 档（有 📐 校准注），详见 ① 段的 🕐 块。

---

### ① context（查询分类 + 公共上下文）

| 维度 | 检查项 | 看 trace.md 哪里 | 判定 |
|---|---|---|---|
| D1 稳定 | `common_context` 产出非空 | §④ state diff | 空 = build_context 失败 |
| D1 稳定 | `query_type` 分类合理（`ticker_specific` / `thematic`，2 类闭枚举） | §③ classify 调用输出 | 分类错 → 下游全歪，必须修 |
| D3 时效 | 〔**2026-09-04 PR2 起读法**：看 §④ 的 `legs:` 行 —— **确认标的自己的腿** `到`（`arrived`）且有 price；`ticker=` 栏〔**2026-09-08 订正 —— 旧读法已废**：影子字段已删，该栏改按**价格腿摘要**渲染，**不再是「个股格子视图」** ⇒ 原文「商品/指数问题它印 `-` 是对的」**反了**：现在商品 / 指数问题**照样印价**（黄金 `yfinance:GC=F@4682.79`、标普 `yfinance:^GSPC@7666.60`）。改前它们恒印 `-`，142 份在册归档里有 16 份因此看不到已经取回的价。⇒ **这一栏现在也能当「价到底拉回来没有」的判据用**，不限个股型〕〕资料夹里该腿有 price 且非 null（适用 `ticker_specific` 型） | §④ common_context 摘要（`legs:` 行 + `ticker=` 栏） | 无 price → 下游 entry 校验没基准。⚠️ **2026-07-22 重要性上调**：(b) 后价位**不再被机械抹除** → 现价是 EXEC-FLOOR check② 的**唯一独立尺子**。〔**2026-07-23 处置已落地（AT ✅）**：取价 retry [#196](https://github.com/JunoChenZt/subagent-for-investment/pull/196) + 现价全失**优雅早停**产「暂不可分析」（[#200](https://github.com/JunoChenZt/subagent-for-investment/pull/200)）——e2e 里看到早停即此机制在跑，**非 run 失败**；不再存在"无 price 硬跑到 check② 退化"路径〕 |
| D3 时效 | `references` 的 `as_of` **按来源分档看**（不是一把尺子量到底） | §④ references 列表 | **分档判**（超线 = warn 看一眼，非 ❌ 阻断）：**新闻 `rss`** 超 **2 天** · **美港股行情 `yfinance`** 超 **6 天** · **A 股行情 `tushare`** 超 **10 天** · **宏观月度 `fred`** 超 **80 天**（= 月度发布节律上限 ~75 + 余量：`as_of` 是数据月首日、发布滞后约一个半月、到下一期出来前最旧可到 ~74 天；正常节奏永不越线，**真卡在旧一期上会随时间自己越线**。仅适用月度系列，接入季度系列须另定档）· **无时间戳**（`wisburg` 恒空）→ **单独标注、计数不判红**（空 ≠ 旧） · **未来日期 / 非法格式** → **单独一档，排查数据源**（这才是"源真坏了"，与"正常的旧"分开）· **表外来源**（本行没列的任何新数据源）→ **单独标注「未定档」、计数不判红，并为它定档**〔⚠️ **2026-08-31 读法注（不改判据·只防误读）**：计划驱动下**同源第二条腿的键是 `源#n`**（第 1 条裸源名、第 2 条起加后缀，见 [builder.sources_from_plan](../../../src/committee/common_context/builder.py)）——本行分档**按源名**，`fred#2` 仍按 `fred` 的 80 天判。**人工照表看不会错，按键自动匹配会把它误判成「表外来源·未定档」**（2026-08-31 审计脚本当场踩中·[实测](../rp-g8-e2e-20260831/FINDINGS.md)）〕（否则新源引用既不越线也不通过 = wisburg 那 27% 的病重演）。📐 **校准**：定于 **2026-08-18**·依据 = [14 份 tracked 归档 104 条 reference 实测](../ref-freshness-asof-20260818.md)（`rss` 26/26 恒 **0** · `tushare` 0–1 · `yfinance` 0–**4** · `fred` **44–53** · `wisburg` 28/28 **全空**；⚠️ 按 (跑批, 时间戳) 去重后**独立观测仅 26 个**——A 股 4 次、宏观 2 次，支撑度按此读）·**下次复核 = 新增数据源时 / 某档连续 3 次跑批越线时**。⚠️ **A 股 10 天与美港股 6 天是刻意留的余量**：本批**无一跑在春节 / 国庆长假**（休市 7–9 天），**实测上限不能当天花板用**。〔**2026-08-18 前旧线 · point-in-time · 已废**〕~~数据源超过 3 天 → stale warning。📐 未校准（未纳入 07-31 对账·下轮补）~~ —— **废因见下方 🕐 块**（该线实测 13% 越线、**真阳性 0**） |
| 消耗 | 分类调用 input token ≤ **900**（轻量任务）<br>🔴 **本线自 2026-08-18 起每跑必越** | §⑤ 本段合计 | **⚠️ 先读这句再判**：实测稳定 **≈1120**，**越线属已裁决的预期状态**（2026-08-18 用户裁：**线保留不动、越线非回归**·详见下方 💰 块）—— **看见 ≈1120 不要重新排查**，它不是异常。本线仍要抓的只剩一件事：**数倍级高于 ≈1120** 才是它设计上要拦的**模型路由错配**。📐 **校准**：**2026-08-14 由 ≤800 上移至 ≤900（用户裁）**·依据 = **同句同模型两次实测 725 → 804**（见下方说明）·余量约 12%·🔴 **下次复核 = 敞口**（08-18 只裁了「线不动」，**没同时给新的复核触发条件**——须另裁）。〔**2026-08-18 前 · point-in-time · 已被 08-18 裁决取代**〕~~下次复核 = 再次出现同句读数逼近 900 时（届时先查是不是提示词又长了，再谈调线）~~。〔**2026-06-05 校准记录 · point-in-time · 不改**〕~~定于 2026-06-05（QC-R1 G2）·依据中际旭创 e2e 实测 input 732·下次复核 = classify prompt 再次重写时·⭐ 全表唯一「紧但不空」的线（11 次实测 718–729·贴线未越）~~ |

> **分类 token 线 2026-06-05 由 ≤500 上移至 ≤800（QC-R1 G2）**：classify prompt 重写后
> 新增 tickers 数组输出规则 + 多标的/产业链示例，system prompt 基线变大（中际旭创 e2e 实测
> input 732，cache read 640，cost ≈ $0.0001）。≤800 反映 G2 后现实，非放松——仍能抓"远超"
> 的路由错配。
>
> ---
>
> **📐 2026-08-14 再上移至 ≤900（用户裁）—— 这条线第一次真被越过，越的原因不是它要抓的那件事**
>
> **触发**：BC 收官第二跑（中际旭创·**与当年定线用的是同一句问话**）实测 **input 804**，越线。
> 该线的复核触发条件原本就写着「classify prompt 再次重写时」——六月到八月间那块代码改过三次
> （[#210](https://github.com/JunoChenZt/subagent-for-investment/pull/210) 超时改 env 可调 ·
> [#211](https://github.com/JunoChenZt/subagent-for-investment/pull/211) 本地名录校验 ·
> [#213](https://github.com/JunoChenZt/subagent-for-investment/pull/213) 中文问美股标的确认），
> **条件早已满足，只是没人复核** ⇒ 这次是被读数逼着补做。
>
> **同句同模型两次实测**（R6·历史读数取自 `origin/main` tracked 归档，非本地残留）：
>
> | 时间 | query | model | input | cache read |
> |---|---|---|---|---|
> | 2026-06-11（[run-zhongji-fundamental-20260611](../fm-refactor-spec/run-zhongji-fundamental-20260611/)） | 基于中际旭创基本面…… | `deepseek-v4-pro` | **725** | 640 |
> | 2026-08-14（[run-zhongji-fundamental-20260814](../bc-final-e2e-20260814/run-zhongji-fundamental-20260814/)） | **一字不差** | **同一个** | **804** | **768** |
>
> **变量已控到只剩一个**：query 一字不差、模型一模一样 → **+79 全部来自 system prompt 增长**
> （缓存前缀 640→768 = +128，正是那三次改动堆进去的）。⇒ **不是路由错配**，而该线的判定说明
> 写的就是「远超 → 查模型路由是否错配」——**它响的不是它要抓的那件事**。
>
> **为什么取 900 而不是贴着 804 设线**：这条线的价值在抓**路由错配**，那类错配是**数倍级**的
> （如某 role 误配成带 thinking token 的贵模型），900 完全抓得住；而贴线设置的代价是**下次任何一次
> prompt 微调又响一次假警报**，重复今天这轮排查。⚠️ **如实记账 = 这是一次放松**：本线原本是
> 全表唯一「紧但不空」的那条（11 次实测 718–729 贴线未越），上移到 900 后余量约 12%，
> **「紧」这个属性就此让出去了** —— 换来的是不再因提示词自然增长而误报。
>
> 🔒 **别把这次读成「线太严所以调松」**：**线没错，是缺人复核**。复核触发条件写得好好的、
> 也确实被满足了，只是**没有任何机器会喊它** —— 靠"下次动 prompt 的人记得回来改线"。
> 这与 [backlog BG](../../governance/backlog.md)（`.env` 静默架空断言）、
> [BN](../../governance/backlog.md)（判据到线没人执行）**是同一形态的第三例**：
> 判据都写下来了，执行全靠人记得。**本条不另立账**（BN 已覆盖「判据到线不执行」这一类），
> 只在此标注形态归属。
>
> ---
>
> **💰 2026-08-18：这条线被正式越过，用户当场裁「线不动、越线认了」（补录于 2026-08-27）**
>
> **触发**：[#244](https://github.com/JunoChenZt/subagent-for-investment/pull/244) 重写分类提示词
> （收编大宗商品等资产类 + 给 confidence 定刻度 + 补「标的型但代码留空」示范 + 冷审两处收口）。
> 提示词本体 **2462 → 3706 字符**。
>
> **读数两跳**（同句同模型·出处 = #244 提交记录本身）：
>
> | 时点 | input | 说明 |
> |---|---|---|
> | 改前（= 08-14 基线） | **795** | 未越线 |
> | #244 第一段改动后 | **1060** | 首次真越 ≤900 |
> | #244 冷审收口后 | **1120** | 当前值 |
>
> **用户 2026-08-18 裁决：该线保留不动，越线属预期、非回归** ⇒ 故当时**未改 guide**。
> 下游零变化是当场验过的（附归档 [run-gold-macro-20260818](../classify-prompt-e2e-20260818/run-gold-macro-20260818/)
> 与 [-v2](../classify-prompt-e2e-20260818/run-gold-macro-20260818-v2/)）：**同句重跑分类仍 `thematic`、
> 数据源路由不变、7 条 references 逐条同构** —— 多出来的 token **不在输出文本里**，全在系统提示词。
>
> **2026-08-27 复现**（seg1 G7 第①段·[归档](../rp-g7-e2e-20260827/run-gold-20260827/)）：
> 换了一句**更短**的问话（「黄金会怎么走」），读数**仍是 1120**、缓存前缀 1024
> ⇒ 增量确实在系统提示词、与问句长短无关，**更不是路由错配**（模型仍是 `deepseek-v4-pro`，配置正确）。
>
> 🔒 **本条要记的教训与上面那条 08-14 的不是同一环 —— 别读串了**：
> 08-14 断在「**没人复核**」；**08-18 复核发生了**，改 prompt 的人当场注意到越线并升级，用户当场裁决 ——
> **那一环是好的**。断的是**下一环**：**裁决只写进了提交记录，没回填到这份 guide**。
>
> 后果在 08-27 当场兑现：照 guide 跑第①段的人看见 1120，把**已裁决的预期值**当成异常，
> 重查了一轮，还得出「触发条件又满足了却没人复核」这个**与事实相反**的结论 ——
> 而真相是复核做了、你也裁了，只是这份文档不知道。
>
> ⇒ 与 BG / BN 同族但**位置不同**：BG/BN = 「判据到线没人执行」；本条 = **「裁得好好的，没回填真值源」**。
> **同样不另立账**，只在此标注形态归属，并把口径落到上表那一格。
>
> ⚠️ **如实记账（不擅动）**：这条线现在**每跑必响** = 落进本节自己定义的「**空线**」那一档，
> 而本惯例明说空线没成色。是否重新定线（贴 1120 上方另设 / 改成相对判据 / 降为 observe）
> **本次不动** —— 那是新的承重变更，须用户另裁；同时 08-18 只裁了「线不动」、
> **没给新的复核触发条件**，这个敞口一并挂在上表那一格。

> ### 🕐 **引用时效线为什么从「一刀切 3 天」改成按来源分档（2026-08-18·用户裁）**
>
> **旧线不是空线，是指错方向的线。** [14 份 tracked 归档 104 条 reference 实测](../ref-freshness-asof-20260818.md)：
> 76 条有效样本里 **10 条越线（13%）**，逐条拆开**真阳性 0 条** ——
>
> | 越线来源 | 条数 | 天数 | 真实原因 |
> |---|--:|---|---|
> | `fred` | 6 | 44–53 天 | **月度指标**：8 月中旬能拿到的最新一期就是 7 月初的 ⇒ **3 天线物理上不可能满足** |
> | `yfinance` | 4 | 4 天 | **长周末**：[07-06](../m1-t11-e2e/run-nvda-20260706/) 是**周一**跑，前一交易日 07-02（07-03 独立日休市）⇒「4 天旧」是正常的 |
>
> ⇒ 它每次响都说「数据旧了」，实际说的是「今天周一」或「这是月度数据」。**把节律当故障。**
>
> **而真正没人管的那头**：`wisburg` 28/28 **没有时间戳**（占全部引用 **27%**）——
> 既不算越线也不算通过，**静默溜过**。新档把它标出来，只计数不判红（**空 ≠ 旧，两回事**）。
>
> 🔒 **判红面零变化，提醒面有得有失 —— 如实记，别只读前半句**：
> **得** = 旧线 13% 误报归零 + **27% 无时间戳**引用从静默溜过改为显式标注；
> **失** = A 股档由 3 天放宽到 **10 天**，**长假之外**若真有一条 5–9 天没更新的行情，
> **旧线会响、新线不响** 〔**2026-08-18 用户裁决：接受此代价，保持 10 天**〕。
> 本行从来只提醒不阻断（fail 面本就是零），故不适用
> [验收标准 §4](../../governance/e2e-acceptance-standard.md)「新检查一律 WARN 试用」
> —— 那闸门是给**新增 fail 面**的。
>
> ⚠️ **两处余量是刻意留的，别当放松读**：A 股行情实测上限只有 **1 天**，线却定 **10 天** ——
> 因为**这 14 份没有一份跑在春节 / 国庆长假**（休市 7–9 天），
> **拿实测上限当天花板，下一个长假必然误报**。美港股同理（实测 4 = 独立日连假 → 定 6 盖圣诞元旦）。
> 这是**样本未覆盖**，不是判据放松。
>
> ⚠️ **本次没做、已立账的两件**（见 [backlog](../../governance/backlog.md)）：
> ① **本行是这批引用唯一的守卫** —— 它们的时间戳**全程没有代码在看**（只渲染进水印段落给分析师读 +
> 本行人工瞄一眼，审核环节根本不读该字段）；〔**2026-09-23 前向**：审核环节已开始读这批日期（CRED.2.G3）—— 所引出处过期会记进审核理由、该事实可信度落「有源但过期」；「全程没有代码在看」已不成立〕
> ② 代码侧另有一套时效窗口（`FRESHNESS_WINDOW_DAYS`：现价 1 / 估值 1 / 目标价 100 / 财务 100 / **其他 400**），
> 与本行**量同一件事、差 133 倍、互不知道对方存在**；其中 `other = 400` 是五档里**唯一没有论证**的
> （[confidence.py](../../../src/committee/facts/confidence.py) 注释仅「放宽」二字），
> 而**全部外源因无类型标记落此档** ⇒ 13 个月前的新闻今天仍算新鲜。收窄 = 提高拦截面 = **承重变更须用户裁**。
> 〔**2026-09-23 前向**：D1 用户裁 other **400 → 180 天**并补齐校准注（CRED.2.G2）—— 「唯一没有论证」已不成立〕

---

### ② research（8 analyst 并行研究）

| 维度 | 检查项 | 看 trace.md 哪里 | 判定 |
|---|---|---|---|
| D1 稳定 | 8 份 `*_report` 全部产出 | §④ state diff（逐角色） | 缺报告 = 节点失败 |
| D1 稳定 | 无 fallback 空报告（headline 非空、key_points ≥ 2） | §④ 每份 report 摘要 | 空 headline / 0 key_points = 模型没答。📐 **校准**：定于 2026-07-31·11 次 run 实测**最小值 3–5**（从没接近 2）→ **已知钝线·方向对但不会提前响**·**下次复核 = 有一次真跌破 3 时**（届时再评估要不要上移，**收紧 = 提高 fail 面·须用户裁**） |
| D1 稳定 | LLM 重试次数：每角色调用数 ≤ 3（含 web search 工具循环） | §③ 调用汇总表 calls 列 | >3 = parse 失败重试或工具循环失控。📐 **未校准**（未纳入 07-31 对账·下轮补） |
| D2 数字 | `evidence_log` 每份 ≥ 1 条，且有 `source` 和 `as_of` | §④ evidence=N | **两步判，别只看字段**：`evidence_log = 0` 时**先扫该份 key_points 的数字有没有带章**（外源 `W#` / 内源 `REF#`）——带章 = **数据在，只是没进这个字段** → 记 observe 放行，不判 ❌；正文数字**也没出处**才是「无数据支撑」→ ❌。⚠️ 判据量的是「有没有数据支撑」，**不是「字段填没填」**（[backlog BE](../../governance/backlog.md)·2026-07-31 seg2 实测：`technical_report` evidence_log=0 但正文 5 条 key_points 带 RSI/MACD/均线/VWAP 且**数字全带章**）。**下游承重未改**：[risk_gate.py](../../../src/committee/agents/risk_gate.py) G1 仍按 `len(evidence_log) < 2` 计数（**代码一行没动**），空 evidence 让 G1 更易开火 = **误报侧非漏报侧**、方向安全。<br>🔒 **带章 ≠ 章为真**：第一步只降「字段没填」的误报，**不构成对数据真实性的背书** —— 章**既不保证存在、也不保证指对**（[backlog BC](../../governance/backlog.md) 🔴→✅ **CLOSED 2026-08-14**（随「数字出处」问题域[封卷](../../governance/number-provenance-endgame.md)））。故带章走 **observe 而非 ✅**。<br>**✅ 回审已做（2026-08-04·BC 验出「拦不住」）**：**判据不变**（仍 observe·fail 面零变化），**边界往严改**——原来只防「章是编的」，实测出的更隐蔽形态是「**章真实存在、绑的却是别的实体**」：13 条 `audit_passed` 里 **10 条**锚指向不相干字段（`PE 30.79x` 的锚指向 `price`），且**走完全链印给读者**、`ROE 114%` 还在附录标 **verified** 正文零 caveat（[DEFECT-ANCHOR-MISBIND](../../governance/backlog.md) 🔴→✅ **CLOSED 2026-08-14**（随「数字出处」问题域[封卷](../../governance/number-provenance-endgame.md)））。⇒ 读「带章」时只当**"有人写了个编号"**，别当**"有据可查"**。<br>📐 **校准**：定于 2026-07-31·11 次 run 实测**最小值 3–5**（对账 #9·从没跌破 1）→ **已知钝线**（本次改的是**读法**不是阈值）·**下次复核 = 有一次正文数字也无出处真判 ❌ 时** |
| D3 时效 | evidence 里 `as_of` 与今天差距 | §④ 或 §③ 原始输出 | 超一周的关键事实 → 标注 stale。⚠️ **宏观类不按本行一周线判**（2026-08-18 与 ① 段分档口径对齐：月度节律下 44–75 天是常态，**超 80 天才异常**——同一批时间戳不能 ① 段放行、本段判旧）。📐 **未校准**（未纳入 07-31 对账·下轮补） |
| D4 一致 | conviction 分布：不全是 Neutral（不全和稀泥）也不全一致（不独立思考）| §④ conviction 字段 | 8 个全 Neutral / 全 Strong Overweight → 可疑 |
| D5 判断 | 每份 key_points 有实质内容（不是模板句） | §③ 原始输出快扫 | "需要进一步观察"重复出现 → 信号弱 |
| 消耗 | 每角色 token 对比：有没有离群贵的（模型路由错配，如某 role 误配成带 thinking-token 的贵模型，单角色 token 数倍于同档） | §⑤ 按 model 分组 | 离群角色 → **读 run 目录 `config-snapshot.json` 的 `roles[<role>].model` 与 `layer`**（那是运行时实配·不是 tier 常量），再与 §③ 调用表的 model 列对照；**别去翻 `.env`**〔2026-09-14 BJ.3 改口〕 |

---

### ③ triage（质量审核 + rework）

| 维度 | 检查项 | 看 trace.md 哪里 | 判定 |
|---|---|---|---|
| D1 稳定 | `triage_verdicts` 有值、每角色有 verdict | §④ state diff | 缺 = triage 节点异常 |
| D1 稳定 | 某 role `rework_counts=2` 且报告仍 reject = 重试耗尽强行放行，**信号弱** | §④ rework_counts + verdicts 对照 | 这是**有判别力的那半**，保留。〔**2026-07-31 移出**：原同格还写「每角色 ≤ 2，>2 = 不可能」——上限由 `MAX_REWORK_PER_ROLE=2` 常量保证、**逻辑上不可能失败**，人每段读一遍零收益 → 已移交单测 [`test_checklist_structural_invariants.py`](../../../tests/test_checklist_structural_invariants.py)（常量被改会在那里红）〕 |
| D4 一致 | reject 的角色确实被 rework 了（rework_counts > 0） | §④ verdicts + rework_counts 对照 | reject 但 rework_counts=0 = rework 没跑 |
| D5 判断 | verdicts 不全是 pass（全过 = 橡皮图章，triage 没实际审） | §④ verdicts 分布 | 8/8 pass 每次都是 → 规则太松<br>📌 **读法（2026-09-18 订正·线不动）**：**最终**结论按设计几乎总是 pass —— 被打回的报告返工重写、再审通过后，第一轮的「打回」会被覆盖掉。⇒ **看「有没有打回」要读 `rework_counts`（返工次数），不读最终 verdicts**。按返工次数重数：08-03 起在册 9 份第 3 段断点里 **4 份有返工**（08-03 NVDA · 08-14 中际旭创 · 09-02 黄金 · 09-02 标普），09-18 NVDA 补跑又有 2 位返工 ⇒ 审核**在打回**，「规则太松」信号**不成立**。〔原 09-17 读数注写「连续 9 次全过、零打回」**只数了最终结论、漏了返工**，已撤；出处 [09-18 补跑冒烟](../bk2-smoke-20260918/run-nvda-20260918/)〕⚠️ 另记一个缺口：返工提示**不附打回原因**、第一轮结论被覆盖 ⇒ 产物里读不出「为什么被打回」。 |
| 消耗 | triage 主体是规则引擎，但 **C 类（`triage_c`·rules_c）+ E 类（`triage_e2`·rules_e）是 LLM 检查**（跨角色核 / 证据核）——有这两类 LLM 调用**是设计如此、非漏洞**（2026-07-07 订正：旧"triage 纯规则零 LLM"stale）；resume 每段 triage 全重跑 → 这两类会重复计入 | §⑤ | 出现 `triage_c`/`triage_e2` **以外**的 LLM tag（如 analyst 角色名）→ 才是 rework 重跑或架构问题 |

---

### ④ debate1（R1 opening + ds_researcher 并行）

| 维度 | 检查项 | 看 trace.md 哪里 | 判定 |
|---|---|---|---|
| D1 稳定 | `debate_log` 新增 2 轮（bull/opening + bear/opening） | §④ +2 轮 | 缺 = 辩论节点失败 |
| D1 稳定 | `ds_researcher_result` 产出非空 | §④ ds_researcher_result | 空 = facts 提取失败 |
| D2 数字 | ds_researcher 的 `facts_inventory` 有 ≥ 5 条 fact | §④ facts_inventory=N | <5 = 事实基础薄弱。📐 **未校准**（未纳入 07-31 对账·下轮补）⚠️ 但**不是没数据**：AX 那次实测 0 条（两次尝试全灭·`facts_inventory` 空）就是本条真该开火的形态 |
| D4 一致 | bull 和 bear 各自立论，不互相抄（内容无实质重叠） | §③ 两个 debate 调用的 output | 复制粘贴式 → prompt 问题 |
| D5 判断 | `key_claims` 每方 ≥ 2 条实质性主张 | §④ claims=N | 0 claims = 空辩论。⭐ **全表唯一真 fail 过的线**——`claim 最少 = 0` 出现 5 次（06-11 一次正常 run + **全部 4 次对抗 run**），也是**投毒 run 上唯一被区分出来的指标**（[对账 §3](../../governance/e2e-guide-threshold-audit-20260731.md)）。📐 **校准**：定于 2026-07-31·15 次 run 实测 **0–5**·**下次复核 = 连续 10 次 run 再没 fail 过时**（届时评估是否上移） |
| 消耗 | ds_researcher（并行）不应比单个 debate turn 贵太多 | §⑤ 对比 | ds_researcher 离群贵 → 检查模型 |

---

### ⑤ debate2（R2 rebuttal）

| 维度 | 检查项 | 看 trace.md 哪里 | 判定 |
|---|---|---|---|
| D1 稳定 | `debate_log` 新增 2 轮（bull/rebuttal + bear/rebuttal） | §④ +2 轮 | 缺 = 失败 |
| D4 一致 | rebuttal 是否真正回应对方 R1 的 claims（不是自说自话） | §③ prompt 里有 prior_debate → output 是否引用 | 完全忽略对方论点 → 辩论无效 |
| D5 判断 | 有新论据出现（不只是重复 R1） | §③ output 快扫 | 纯复述 R1 → 没有信息增量 |
| 消耗 | 与 R1 相当 | §⑤ | 远超 → 续写失控 |

---

### ⑥ debate3（R3 closing）

| 维度 | 检查项 | 看 trace.md 哪里 | 判定 |
|---|---|---|---|
| D1 稳定 | **【存活探针·非质量判据】** `debate_log` 累计 6 轮 | §④ 累计 6 | <6 = 缺轮。⚠️ **名实相符标注（2026-07-31）**：15/15 run **零方差全 = 6**，由 graph 拓扑决定 → 它只证明「节点没崩」，**不证明辩论有质量**，别把它的 ✅ 读成质量已检查 |
| D5 判断 | closing 有总结性判断（不只是重复前两轮） | §③ output | 纯复述 = 没有收敛 |
| D5 判断 | bull/bear 的最终立场有分歧（不是共识收敛成同一结论） | §③ 两方 output 对比 | 双方结论一致 → 辩论失去意义 |
| 消耗 | **【成本记录项·observe·不判】** 6 轮辩论总 output token —— **只记一笔看趋势，不作排查触发** | §⑤ 累计 | **只记录**。📐 **重定于 2026-08-14（用户裁）**·依据 = **10 个独立跑批的分轮实测**（见下方说明）。〔**2026-07-31 原线 · point-in-time · 已废**〕~~22k–29k 双向排查线；>40k 查续写失控；<15k 查截断~~ —— **该线已由数据证伪其诊断力**，理由与替代见下方 📊 块 |
| D1 稳定 | **有没有轮次打满续写上限**（上限 = run 目录 `config-snapshot.json` 里 `COMMITTEE_MAX_CONTINUATIONS` 的生效值〔2026-09-14 BJ.3 改口：**不再在本表抄值**，此前写的「=3 → 每轮最多 4 次」是抄下来的数字线、会过期〕→ 每轮最多 上限+1 次调用） | §③ 调用汇总表按 debate tag 数 calls | **这是替代总量线的那条**：打满 = 续写反复触发仍不收敛 = 「失控」的**实际形态**。⚠️ **排查线不是 fail 线**——打满不必然有问题（可能那轮内容确实长），但值得当场看一眼是哪一轮、正文是不是真的塞满了。📐 **校准**：定于 **2026-08-14**·依据 10 跑实测 **8 跑没打满 / 2 跑打满**（有真实变化 = 有判别力）·**下次复核 = `COMMITTEE_MAX_CONTINUATIONS` 变更时**（⚠️ 该常量 **env 可调**，与 `MIN_CHARS_DEBATE` 同族坑——改 env 不动代码即可废掉本线且 code review 看不见）<br>📌 **2026-09-17 读法注**：**被打回重答的轮次，两次作答的调用会记在同一个标签下**（实例：空头开场触发可见性规则 F2 被打回，标签下计 6 次 = 首答 2 + 重答 4）。⇒ 要**按「每次作答」拆开数**（发给模型的首条是完整题目 = 新一次作答），否则会把「打回重答」误读成「续写失控」。出处 [BK.2 PR1 证据 §5](../bk2-m2-pr1-20260917/FINDINGS.md) |

> ### ⏬ 2026-08-14 已从本表移交单测的两条
>
> 〔**2026-08-14 已移交单测·本行从人工表移出**〕~~每轮最终正文 ≥ `MIN_CHARS_DEBATE`（抓截断）~~ → 由 [`test_checklist_structural_invariants.py`](../../../tests/test_checklist_structural_invariants.py) 承重（`test_min_chars_debate_is_the_per_turn_floor` 钉「续写停止条件用的就是该常量」）。实测 10 跑**最短 1512–1617**，全部刚过 1500 = **结构决定**。
> 〔**2026-08-14 已移交单测·本行从人工表移出**〕~~每轮调用次数 ≤ 4~~ → 同文件两条承重：`test_max_continuations_is_three`（钉**生效值**·已加进 [env-shadowing 豁免](../../../scripts/lint_env_shadowing.py) 并附理由）+ `test_continuation_loop_bound_matches_constant`（**行为断言**·真数 invoke 次数·变异验证已杀「循环多跑一轮」）。


> ### 📊 **总量线为什么被废掉（2026-08-14·10 跑分轮实测·用户裁）**
>
> **原线**：区间 22k–29k · >40k 查续写失控 · <15k 查截断。**问题**：近三次实测 36.6k / 46.2k / 44.6k，
> **今日 2/2 全越 40k** —— 它正从「排查线」滑向「每跑必响」，而每次排查的结论**都是「不是失控」**。
>
> **决定性反证（这条才是废它的真理由，不是"响太多"）**：
>
> | 跑 | 六轮总 output | 单轮最多调用 | 打满上限？ |
> |---|---|---|---|
> | m1-full-e2e 2026-07-10 | 36,648 | **4** | ✅ 打满 |
> | BC 探针 2026-08-03/05 | 36,594 | **4** | ✅ 打满 |
> | **BC 收官·黄金 08-14** | **46,172**（历史最高） | **3** | ❌ 没打满 |
> | **BC 收官·中际旭创 08-14** | **44,639** | **3** | ❌ 没打满 |
> | 其余 6 跑 | 22,427 – 28,361 | 2–3 | ❌ 没打满 |
>
> ⇒ **总量最高的两跑反而没打满续写上限；打满的两跑总量在中游。**
> 「总量高 ⇒ 续写失控」这条推理链**被数据直接切断**。
> 总量实际测的是**模型草稿有多啰嗦**（吐出来但没留进正文的部分）= **成本面，不是失控面**。
>
> **分布对照（10 跑）**：总 output **22,427–46,172（2.06×）** vs 每轮最短正文 **1,512–1,617（1.07×）**
> vs 每轮最长正文 **1,763–2,207（1.25×）**。**宽的那个没有诊断力，窄的那些是结构决定的。**
>
> **处置**：① 总量降**成本记录项**（只记趋势·不触发排查）；② 新增**「有没有打满续写上限」**作排查线
> （8:2 分布 = 真有判别力）；③ 两条结构线**待移交单测**（移交前不删）。
>
> 🔒 **这次改的是「量什么」，不是「把线放松」** —— fail 面零变化（⑥ 段本就全是排查线、无 fail 项）。

---

### ⑦ votes（10 voter + ds_debate）

| 维度 | 检查项 | 看 trace.md 哪里 | 判定 |
|---|---|---|---|
| D1 稳定 | **【存活探针·非质量判据】** 10 个 voter 全部投票（每个有 vote + conviction） | §④ +10 votes | 缺 = 投票节点失败。⚠️ **名实相符标注（2026-07-31）**：15/15 run **零方差全 = 10**，由 graph 拓扑决定 → 只证「节点没崩」，不证投票有质量。<br>👁 **观察点（2026-08-04·N=2·不是判据、只记）**：**NEUTRAL 票的 reasoning 高度同构** —— 07-30 六张 conviction 全 = 6；08-04 五张 conviction 全 = 6 且关键词 5/5 重合。**两跑同构** ⇒ 怀疑 10 个 voter 被同一份辩论摘要主导，多样性成形式。**跑批时顺手记一笔 NEUTRAL 票的 conviction 方差**；~~N≥3 时提立条目~~ ✅ **已于 2026-08-14 按 N=3 立账为 [backlog BN](../../governance/backlog.md)（08-27 回填本行·此前文本停在 N=2 导致 08-27 跑批错判「仍 N=2」·即 BU 例②）**——~~后续读数（含反向条件计数）**记入 BN，不再在本行数 N**~~ 〔**2026-09-03 订正 · BN 已 CLOSED**〕**BN 于 2026-08-31 close-by-condition**（反向条件连续 3 次成立）⇒ **不再有可记账的活跃条目**，读数改记在本行 + 当次跑批 FINDINGS。详见下方 D5 行的 🔒 块。（[FINDINGS §3.9](../regression-e2e-20260730/FINDINGS.md)）|
| D1 稳定 | `ds_debate_result` 产出非空 | §④ | 空 = debate briefing 失败。📌 **读法（2026-09-24 订正·渲染已修·线不动）**：§④ 这一行现在按辩论摘要的真实结构印 ——「`debate_summary: N/5 块有内容（…）· quality_warnings=M`」+ 多空核心论点各一句；摘要缺失或五块全空时明写「`debate_summary=**空**`」，**看见「空」即按本行判 debate briefing 失败**。〔**修前读法 · point-in-time · 已废**〕~~§④ 这一行会印成「`facts_inventory=0 · audit_status: -`」—— 是 trace 渲染套用了事实清单的格式，不是没产出；判空要打开 checkpoint 看 `debate_summary`~~（修前现场见 [CRED.2.G5 FINDINGS](../cred-2-g5-e2e-20260923/FINDINGS.md) §2；**2026-09-24 前的旧 trace 仍是旧印法**，读旧 trace 时照旧读法） |
| D4 一致 | 投票分布与辩论内容方向一致（bull 多→BULLISH 多） | §④ vote 列表 vs 辩论印象 | 完全相反 → 投票没参考辩论 |
| D4 一致 | 不全票一致（10/10 同向 = 没有独立判断） | §④ vote 分布 | 全票 → 可疑 |
| D5 判断 | **🔬 观察点（不判 ❌·N≥3 才提立条目）**：同向票的 `reasoning` 是否**高度同构** —— 关键词大面积重合 + `conviction` 零方差 | §④ 逐票 reasoning 对读 | **只记不拦**。实测 **N=2**：07-30 六张 NEUTRAL 理由趋同；2026-08-04 BC 探针跑五张 NEUTRAL **`conviction` 全部 = 6**（零方差）、关键词「估值」5/5·「资本开支」5/5·「等待」5/5 重合，措辞近同模板。**方向不是安全洞**（NEUTRAL 属保守侧），问的是**独立性**：10 个 voter 若被同一份辩论摘要主导，多样性就成了形式。~~再出现一次（N≥3）→ 提立 backlog 条目（2026-08-04 用户裁「先并入观察点、不立条目」）~~ ✅ **该立账已于 2026-08-14 发生 = [backlog BN](../../governance/backlog.md)（N=3·08-27 回填本行）**——~~本行今后只管「跑批时把同向票方差 + 全员共有词记进 BN」，正反例都记（BN 有反向条件计数）~~ 〔**2026-09-03 订正 · 见下方 🔒 块**〕。出处 [FINDINGS §3.9](../regression-e2e-20260730/FINDINGS.md) |
| D5 判断 | 每票 `reasoning` 非空且有实质内容 | §④ 或 §③ output | 空 reasoning = 投了但没说为什么 |
| D5 判断 | conviction 分布合理（不全是 7/10 或全是 3/10） | §④ conviction 数值 | 窄分布 → 可能模型惰性 |
| 消耗 | 10 个 voter 总消耗合理 | §⑤ | 单个 voter 离群 → 路由 |

> ### 🔒 **BN 已 CLOSED —— 这两行的读数今后记在哪（2026-09-03 订正）**
>
> **事实**：[backlog BN](../../governance/backlog.md)（十票像一个人投）**已于 2026-08-31 close-by-condition**
> —— 反向条件「连续 3 次同向票有真实方差」达成（08-14 / 08-27 / 08-31）。
> ⇒ 上面两行原写的「记入 BN」**做不到了**：按 [Q6 冻结档](../../governance/workflow/05-brake-self-check.md)，已 close 的条目不再接受追加。
>
> **为什么现在才订正 —— 这是 [BU](../../governance/backlog.md) 的第三例，不是新形态**：
> BN 8-31 关闭时，本行没被回填；2026-09-03 跑批的人照本行去找 BN，才发现它已经关了
> （08-27 那次是反过来：BN 已立账而本行还停在「N≥3 → 提立」）。**同一处、同一病、方向相反的第二次。**
>
> **今后怎么记**：同向票 `conviction` 方差 + 全员共有词，**记在当次跑批的 FINDINGS 里**，
> 本行只作提示；**不再有活跃条目吃这个读数**。若要重开追踪，须用户裁（重开 = 占配额）。
>
> **📊 2026-09-03 读数（PR1 验收三跑·一正一反·[FINDINGS](../cat-pr1-e2e-20260902/FINDINGS.md)）**：
>
> | 跑 | 组 | conviction | 方差 | 全员共有词 |
> |---|---|---|---|---|
> | 黄金（thematic） | NEUTRAL 3 张（排除自动弃权） | 6 / 6 / 6 | **0（零方差）** | **5 个**：短期·长期·央行购金·支撑·方向 |
> | 黄金 | BULLISH 5 张 | 6/6/7/7/6 | 0.24 | 空 |
> | 标普 500（thematic） | NEUTRAL 4 张（排除自动弃权） | 5/6/6/6 | 0.19 | 2 个：估值·等待 |
> | 标普 500 | BEARISH 3 张 | 9/7/6 | 1.6 | 1 个：估值 |
>
> ⚠️ **黄金那跑是 BN close 之后的第一个同构复现** —— 按 BN 原口径（无一组零方差 + 共有词全空）
> 它**不满足反向**，等于把连续计数打断了。**用户 2026-09-03 裁：不重开 BN**，读数留在本块与跑批 FINDINGS。
> 🔒 **本块不改任何放行判据** —— ⑦ 段该项仍是 🔬 观察点（不判 ❌），fail 面零变化。

---

### ⑧ pass0（ds_merge + audit + 前置风控）

| 维度 | 检查项 | 看 trace.md 哪里 | 判定 |
|---|---|---|---|
| D1 稳定 | `pass0_result` 产出非空 | §④ | 空 = merge/audit 失败 |
| D1 稳定 | `risk_gate_pre_findings` 产出（可以为空列表，但 key 必须存在） | §④ | key 缺失 = pre-gate 节点没跑 |
| D2 数字 | **【影子试用·CRED.1.G2·D5】** `risk_gate_pre_findings` 里有没有 `G1-shadow`；有则**逐条抄出 `details.roles[*].excluded`、role 级 `would_block` 与闸级 `would_newly_block`**（trace §④ 现已渲染这些明细行·#285 复审修）供用户认定 | §④ findings | **只记录、不判 ❌**（硬拦仍走 G1 旧口径；影子不进 fund_mgr 提示词）。分歧 = 可审样本：**`would_newly_block=True`** 的每一条由用户认定真阳性/误拦（`would_block` 只是 role 级短缺·G1 已因别的 role 触发时不算新增拦截）；**零分歧也要写「零」**（升硬拦判据：全部坐实零误拦·≥3 跑是地板非放行条件）。⚠️ 今日上游已不把错误登记进表①，零分歧是常态、不是检查坏了。📌 **抄完要回填条目计数**（2026-09-24 节点收口 adopt）：本跑的 `G1-shadow` 分歧数 + 异模型复核员调用数（`enforcement_log` 里 `evidence-mismatch-review`）**收口前**回填到 [`DEFECT-REVIEW-ERROR-AS-DATUM` / `DEFECT-ANCHOR-FALSEPOS-HARDBLOCK`](../../governance/backlog.md) 的计数行 —— 09-17 至 09-24 五跑读数全没回填、计数停在「第 1 跑」，是节点收口时翻归档才补上的 |
| D2 数字 | **【observe·不作放行闸】** `facts_inventory` 的 `audit_status` 分布：**记录 `audit_passed` 占比** | §④ audit_status 统计 | **只记录、不判 ❌**；仅当 **< 5%**（低于历史下沿）才停下排查。📐 **校准**：定于 **2026-07-31**·依据 11 次 run 实测 **6% – 47%**·**下次复核 = audit 定位变更时**（见下方说明）。⚠️ **2026-07-22 订正**：原写「verified ≥ 50%」**照做不了**——`audit_status` 的活跃值是 `audit_passed`/`audit_notsure`/`audit_notpassed`/`not_audited`（[schemas/pass0.py](../../../src/committee/schemas/pass0.py)·MASK.E1 #184 收敛），**没有 `verified`**（那是 `confidence` 轴的档位·两轴不同物）。<br>📌 **2026-08-14 补适用范围（阈值不动·只补读法）**：**5% 下沿是按 `ticker_specific` 跑批校准的，`thematic` 跑结构上够不着** —— BC 收官宏观黄金跑实测 **2.4%（2/82）撞线**，排查结论是**结构使然、非 audit 坏了**：主题型无 `ticker_payload` → 表① 只有 **7 条** references（3 fred + 2 rss + 2 wisburg），而 80 条 `audit_notsure` 拆开是 **66 条「水印均为外部数据章（W# 族）·audit 不核 web」+ 12 条「推断性断言无水印·跳过核验」+ 仅 2 条真降档**。⇒ **撞线时先看 `query_type`**：`thematic` → 属预期形态，记录后放行，不必逐条排查；`ticker_specific` → 才按原意排查（历史 6%–47% 区间**全部来自个股跑批**）。<br>📌 **2026-09-17 读数注（阈值不动·只记读数）**：**个股跑也碰线了** —— 09-17 NVDA 跑 **1.4%（72 条里 1 条）**；主线入库 13 份第 8 段断点里 **08-05 以来已有 4 份 < 5%**（2.3% / 2.4% / 1.4% / 2.9%）。每次碰线排查结论相同：核查按设计只核内部数据表、不核网页，而分析师取证以联网为主 ⇒ 读数由取证结构决定。该线正从「排查线」滑向「常响线」（同 ⑥ 段总量线 08-14 被废前的形态）。用户 09-17 裁：**先记观察、暂不改线**；复核时点照上文「audit 定位变更时」。出处 [BK.2 PR1 证据 §7](../bk2-m2-pr1-20260917/FINDINGS.md) |
| D2 数字 | unverified 的精确数字有多少（为 D2 "精确数字背书" 做预判） | §④ 或 §③ 找 unverified 条目 | 大量 unverified 精确数字 → 正文可信度低 |
| D3 时效 | facts_inventory 里 `as_of` 覆盖率（有几个 fact 带时间戳） | §④ 或 §③ | 无 as_of = 无法评时效 |
| D2 数字 | **【WARN 试用·CRED.3.G1】** 辩论里的指标数字与本跑事实清单对不对得上 | §④′ 辩论数字对账 | **只记录、不判 ❌**：有条目就逐条读片段判是不是凭记忆写的旧行情；「无底可对」≠「0 条」（前者是没法查）。终局质检 Q9 读同一结果 |
| 消耗 | audit 是轻量规则引擎，cost 应很低 | §⑤ | 有 LLM 调用 → 查架构 |

> **⑧ `audit_passed` 为什么从「≥50% 判失败」降为 observe（2026-07-31·[backlog BB](../../governance/backlog.md) 收口）**
>
> 11 次 run 实测 **6%–47%，从没有一次达标**，最高的 47% 还差 3 个百分点 —— 这是**空线**（照字面每次都判失败）。
> 但根因不是系统坏了，而是**线是按早已废弃的「三检查」时代想象定的**：
> audit 现在**永久停在「来源存在性」半项**（AUDIT-3CHECK 已砍·安全底线转 Path B / GATE-B 输出侧验章门），
> T11 又把存在性泡沫挤掉过一轮（26→3）。**在当前定位下 `audit_passed` 本就该是少数**。
>
> 该行 2026-07-22 被订正过一次，但**只改了字段名没重估阈值**——而订正当天那次 run 自己就是 6%。
> 教训：**改判据的字段名时必须一并复核它的数值**，否则改完的线看着新、其实照样空。
>
> **承重变化方向**：⑧→observe = **fail 面只减不增**（原本每次必判 ❌），
> 故不适用 [e2e-acceptance-standard §4](../../governance/e2e-acceptance-standard.md) 的「新检查一律 WARN 试用」规则（那是给**新增**检查的）。
> **真要用绝对线，得先重定 audit 的定位** —— 定位一天不变，绝对线就一天不可用。

---

### ⑨ decision（fund_manager + 风控闸门 + hard_block）

| 维度 | 检查项 | 看 trace.md 哪里 | 判定 |
|---|---|---|---|
| D1 稳定 | `final_decision` 产出、`risk_gate_findings` 产出 | §④ | 缺 = fund_mgr/gate 失败 |
| D2 数字 | **【影子试用·CRED.1.G2】** `risk_gate_findings` 里的 `G1-shadow`（与 ⑧ 同一条·全检时重算）：`details.would_newly_block=True` → 「新口径本该拦、旧口径没拦」的一次样本（#285 复审修：不再看 `hard_block_reason` —— 它只在 D2-β 候选时才写，HOLD / 无计划的跑批 G1 响了也没有这个字段；闸级判定已在 finding 里算好）。影子不进 fund_mgr 逐条回应 pass，`risk_gate_response` 里**不会**有 `G1-shadow` 条目 | §④ findings | 只记录；样本进本跑 FINDINGS / 对账报告，供 D5 升级裁决 |
| D1 稳定 | `decision` ∈ {BUY, SELL, HOLD}（ADD→BUY / REDUCE→SELL / AVOID→SELL / 无法识别→HOLD，由 before-validator 归一化） | §④ decision 摘要 | 出现非三值 = **归一化失效**（这半有判别力：before-validator 是运行时逻辑，可能真漏）。〔**2026-07-31 移出**：原同格还查 `confidence ∈ [1,10]`——由 `FinalDecision.confidence` 的 `ge/le` 约束保证、**逻辑上不可能越界** → 已移交单测 [`test_checklist_structural_invariants.py`](../../../tests/test_checklist_structural_invariants.py)（schema 约束被拆会在那里红）〕|
| D2 数字 | `execution_plan.entry` 非占位符（非 0.0/1.0），low ≤ high | §④ execution_plan | 占位符 = 模型没认真填 |
| D2 数字 | **价位 level 是否存活**（GATE-ROUTE (b) 后）：grounded run（`confidence_map` verified ≥2）应**原样保留**；被抹时 enforcement_log 须有 `price-gate-5'` / `ungrounded` 记录 | §④ execution_plan + enforcement_log | 被抹却无 `ungrounded` 记录 = 静默抹除，排查 |
| D2 数字 | ⚠️ **读上一条前先确认前提**：fm 本跑是否**真把价位填进结构化字段**（`entry`/`stop_loss`/`take_profit`）——若全 null（价位写进了 `reevaluate_triggers` 散文），则「价位存活/无 strip」两项**判『本跑无效』而非 PASS** | §④ execution_plan | **fm 填不填结构化价位是高方差行为**（旧码同起点两跑 1:1 分裂）→ 前提不成立时判据恒真=空过（[known-pitfalls §3.2](../../governance/workflow/09-known-pitfalls.md) 第三形态）。📐 **校准**：定于 2026-07-31·11 次 run 实测 **10 次 `entry = null`（1/11 才填）** —— **比「1:1 分裂」的旧描述极端得多**，意味上面两条价位判据在 **91% 的 run 里无从判起**。⚠️ **空过比空线更危险**：空线每次判 ❌ 有人看见会吵，**空过是静默的**——打勾打了两个月，其实一次都没真验过。**故本条前提确认必须先做、不许跳**。✅ **已自动化（2026-08-13·对账建议 3 落地·[backlog BF](../../governance/backlog.md) close）**：§④ 决策摘要现在自带一行「**价位前提（guide ⑨ 段）**」，**前提确认改读这一行**，不必再翻 checkpoint。分**三态**（判的是"有没有价位数字"，不是"有没有价位对象"）：**① 没填** = 计划为 null 或三个价位字段无对象 → 行里写「判『本跑无效』而非 PASS」；**② 填了** = 至少一个 `low`/`high`/`level` 带真数字 → 「前提成立，可读价位判据」；**③ 填了但数字被抹** = 对象在（`note` 还写着依据）、数字全 null → **不按 PASS 读**，且行里直接点名是不是价位门控 `strip_level` 干的（读得到 `enforcement_log` 时给出处数，读不到就写"分不清"）。**③ 与 ① 必须分开**：前者是给了价位被门控拿掉（「无 strip」一项判 ❌），后者是压根没给（判本跑无效），下一步动作完全不同。〔**2026-08-13 冷审收严**：初版按"对象在不在"判，19 份 tracked 归档里有 2 份（门控抹了 5 处 / 4 处）被印成「前提成立」而实际一个数字都没有 = 换个窄形态把空过又造了回来〕。判据承重**一字未改**，变的只是前提可不可见 |
| D2 数字 | `core_risks` ≥ 3 且 mitigation 非空泛 | §④ core_risks | <3 = G5 应触发；空泛 = 应对不实。📐 **校准**：定于 2026-07-31·11 次 run 实测 **3 或 4·从没低于 3**（疑似 prompt 硬性要求 3 条）→ **已知钝线**·**下次复核 = prompt 改动条数引导时**。⚠️ 真正有判别力的是「mitigation 空不空泛」这半（人工判），不是条数 |
| D3 时效 | trigger_events 里没有"已经发生的事被当未来条件" | §④ 或 §③ 原始输出 | 🔵 内蒙式错误需人工判断 |
| D4 一致 | decision 方向 ↔ 投票多数方向一致 | §④ decision vs §⑦ votes | 反向 → fund_mgr 是否有说明为什么 |
| D4 一致 | **SELL/REDUCE** → execution_plan 无 entry（S6 对齐） | §④ | SELL/REDUCE 带买入区间 = 语义冲突。⚠️ **2026-07-22 收窄**：原写「HOLD 无 entry」**已废**——「观望」是对*当前价位*的判断，"现在别追、跌到 X 值得买" = HOLD + 目标买入区间**互补非矛盾**，**HOLD 带 entry 属正常、不要排查** |
| D4 一致 | hard_block_reason 有值时，decision 已被降级为 HOLD | §④ 是否有 ⛔ | 有 hard_block 但 decision 不是 HOLD = 逻辑错 |
| D5 判断 | **回应核心关切**：用户问什么 → decision 有没有正面回答 | query vs §④ 决策摘要 | 问"什么价位买" → 有 entry；问"方向" → 有明确 BUY/SELL |
| D5 判断 | trigger_events 含具体可量化条件（有数字/阈值/日期） | §④ trigger_events | 全是 "市场变化" 类泛语 → 不可证伪 |
| D5 判断 | risk_gate_response 逐条回应了 findings（非漏项） | §④ risk_gate_response 条数 vs findings 条数 | 漏回应 → 闸门形同虚设 |
| 消耗 | fund_mgr（通常 opus）是最贵单步，但 thesis 产出最大 | §⑤ | 超预期 → 续写轮次是否失控 |

---

### 末段通过后：跑终局 quality gate

第 9 段（`decision`）跑完时，段式 runner **自动**在 run 目录落一份
`archive-from-final.json`（T12·2026-07-09）——这份就是整跑收尾同一装箱机
（[`graph._build_result`](../../../src/committee/graph.py)）的产出，**quality gate 直接可吃**，
无需手工转换。末段 CLI summary 会打印它的路径 + 现成命令：

```bash
# 末段跑完后，run 目录已有 archive-from-final.json（CLI summary 已给出完整命令）
python -m committee.e2e_quality_gate <run-dir>/archive-from-final.json
```

> **旧 run / 手工兜底**：T12 前的 run 目录只有 `seg9-decision.checkpoint.json`（无 archive）。
> 手工转换 = `load_checkpoint(<末段 checkpoint>)` → `_build_result(final_state, query, tracker)`
> → `json.dump` 成 archive（[graph.py](../../../src/committee/graph.py) 同函数）。T12 把这一步自动化了。

quality gate 是**终局结构化检查**（S1-S6 / Q1-Q9·Q8 = check① 可见性·2026-09-10 WARN 试用·Q9 = 辩论数字冲突·2026-09-24 WARN 试用），与段间 checklist 互补：
- 段间 checklist = **过程审核**（每段输入输出形态 + 人工语义判断）
- quality gate = **产出审核**（最终 archive 的结构化自动检查）

两者都 PASS → 可正式落盘到 `_archives/` + `run-counter.md` ledger。

## 已知点

- **trace 仅段式模式开**（`--stop-after` 触发）；普通跑不付全量捕获的内存代价。
- token 费率：[`token_usage.py`](../../../src/committee/token_usage.py) `COST_PER_1M` 的
  `deepseek-v4-flash` / `deepseek-v4-pro` 单价 2026-06-04 已补齐 / 修正，以
  [DeepSeek 官方 API 文档](https://api-docs.deepseek.com/quick_start/pricing) 为准；
  其他 provider（Anthropic / Google）的费率未重核，新增模型时请同步该表。
- **段内成本归属**：trace 报告里"本段合计"按 `on_llm_end` 触发时间归到当前段。
  rework 重试同一节点的 LLM 调用会被双重计入（[`token_usage.py`](../../../src/committee/token_usage.py)
  module docstring 标注的已知偏差），段式排查时若发现某段 calls 数远超预期，先查
  triage rework_counts。
- 实测（2026-06-04）：research 段 8 analyst 跨 3 provider（deepseek-v4-flash/pro、
  gemini-2.5-pro）、含 web-search 工具多轮调用，23 次 LLM 调用全量捕获无误。
