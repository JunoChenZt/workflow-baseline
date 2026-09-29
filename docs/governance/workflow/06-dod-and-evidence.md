# 06 DoD & Evidence — DoD 四步 + evidence 收集

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 骨架: [core/05](../../../core/05-dod-and-delivery.md) —— 规则本体以骨架为准，本文件是实例层（含项目参数与历史证据）
> 关联子文档: [docs/governance/workflow/05-brake-self-check.md](05-brake-self-check.md) / [docs/governance/workflow/07-retro-goal.md](07-retro-goal.md) / [docs/governance/workflow/08-retro-node-and-pr.md](08-retro-node-and-pr.md)
> 关联 skill: `dod-checklist`（已 deprecated；详细规则现在本文件 §2.8 + §2.9，设计历史见 [docs/governance/skill-design.md §3.3](../skill-design.md#33-已-deprecated-skill7-个详细设计已迁至-workflow-子文档)）

## 何时读这份文档

[05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) 刹车自检未命中（或用户裁决放行）之后，进入 [07-retro-goal.md §2.10](07-retro-goal.md#210-goal-级-retro按需) goal 级 retro 判定之前。

## 概览

- §2.8.0 **每一步结果只有三态**：✅ 通过 / ❌ 不过 / ⚪ 未验证 —— ⚪ 不算过、也不算阻断，带原因交付，由用户决定收不收；「能跑没跑」不是 ⚪，是盲跑
- §2.8 DoD 四步：Code Review / Corner Case / 冒烟 / 彻底跑通；任一 ❌ 回 [04-goal-execution.md §2.5](04-goal-execution.md#25-单个-goal-执行) 重做；≥ 3 次升级重新拆解
- §2.9 evidence 收集：5 类 evidence 路径汇总成 summary，进 PR 描述；缺失 / 盲跑 → 回 §2.8 补
- §2.9.5 **交付单（固定三栏）**：改了什么 / 验证了什么、怎么验的 / 未验证什么、为什么 —— 第三栏没有就显式写「无」，空白 = evidence 缺失；第三栏条数必须等于 DoD 三态表的 ⚪ 计数
- §2.9.4 **裁决落地 → 回填清单**：本 goal 若定了 / 改了 / 明确不改任何阈值、判据、条目状态，按 **8 格固定名单**逐项点名回填（每格「改了 <link>」或「N/A + 理由」，**不许留空**）—— 补的是 [R7](../../../CLAUDE.md)「状态切换」够不着的那条缝

---

## 2.8 DoD 四步

**时机**：[05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) 刹车自检未命中（或用户裁决放行）后。

**关联 skill**：`dod-checklist`（详见 SKILL.md）

### 2.8.0 每一步的结果只有三态（2026-09-29 立）

> **治的是什么**：DoD 只有「过 / 不过」两个格子时，「没跑」无处安放 —— 要么被写成「通过」（空泛的"全部通过"），要么被当成阻断硬撑（到上限还在磨）。
> 两种都是 [05 §2.7 Q5](05-brake-self-check.md#27-刹车自检8-问) 最常见的绕法。第三个格子把「没跑」变成一个**可以如实写出来、由人决定收不收**的合法状态。

| 态 | 定义 | 去向 |
|---|---|---|
| ✅ 通过 | **跑了**，结果符合 `<done_criteria>` | 进下一步 |
| ❌ 不过 | **跑了**，结果不符 | §2.8.5 同 goal 重做 |
| ⚪ 未验证 | **没跑**，且原因属于下面的闭集 | 带着进 §2.9；写进交付单第三栏（§2.9.5）；**由用户决定收不收** |

**⚪ 的原因闭集**（只认这四种，写别的就不是 ⚪）：

- (a) **环境 / 依赖缺**：无 API key、无网、无测试数据、无权限、目标服务不可达
- (b) **成本超预算**：token / 时间 / 费用到了上限 —— 这一种**必须先按 [05 §2.7.5「到上限不自行免判」](05-brake-self-check.md#275-8-问详细判定标准) 上升**，⚪ 是上升之后的书面形态，不是替代上升
- (c) **上游未就绪**：依赖的节点 / 数据 / 接口还没到位
- (d) **用户明示跳过**：用户说了这轮不验，引用那句话

**三条边界，防止第三格变成新的躲藏处**：

1. **能跑而没跑 = 盲跑，不是 ⚪** → 触发 Q5，停。⚪ 只给「跑不了」，不给「没来得及」。
2. **跑了红 = ❌，不是 ⚪** → 不许把失败改写成"未验证"。
3. **⚪ 不算过，也不算阻断** → goal 可以带 ⚪ 交付，但任何汇总（自验报告 / evidence summary / PR 描述 / 对话结尾）里**不得出现「全部通过 / 全绿 / all pass」**；带 ⚪ 的 goal 标记为 `done-unverified`，不是 `done`。

**进 DoD 前先做档位对账**（[01 §2.2.5.4](01-task-entry.md#2254-只升不降--自动升档)）：`git diff --stat <base>` 数文件、数行、对敏感路径表，与入口声明的档位比；任一超出 → 自动升档，先补齐新档位矩阵要求的步骤再进四步。**两种「没做」两种记法**：档位矩阵（[01 §2.2.5.3](01-task-entry.md#2253-每档要做什么不用做什么)）说不用做的写「本档不要求」，不进三态计数、不进交付单第三栏；矩阵要求做但没跑的才是 ⚪。

**DoD 结束时给三态计数**：`✅ a / ❌ b / ⚪ c`。**b 必须为 0** 才进 §2.9；c > 0 时每一条都要在交付单第三栏出现一次（§2.9.5 对账）。

### 2.8.1 Code Review

- self-review 必做
- schema / prompt / Fallback / 路由变更 → 必走 PR review（即使仓库 private 也建 PR 留 trace）
- review 视角：
  - **北极星**：未引入"假装是决策"的逻辑（自动下单 / 调仓 / 无人确认）
  - **稳定性**：未破坏已 ✅ DONE 节点；fallback 完整；不会让整 run 崩
  - **契约**：未突破 DEBATE_KEY_CLAIMS_CONTRACT / EXECUTION_PLAN_CONTRACT / role prompt 不可覆盖段
  - **测试设计质量**（A6.1.1.1 retro 沉淀）：
    - 每条测试是否无条件 assert（无 if/skip/mock 让 assert 整段不跑）
    - mock 设计是否会让测试看起来 pass 但实际未验证目标行为
    - 每条 assert 是否在所有合法输入下都会被求值
    - 测试代码是否存在"防御性 guard" 实为"隐式 skip" 的反模式（详 [05-brake-self-check.md §2.7.5 Q5](05-brake-self-check.md#275-8-问详细判定标准) 隐式 skip 4 类清单）

**输出**：review notes（markdown，进 PR 描述）

### 2.8.2 Corner Case

- **跑该段表列出的所有 case（不删、不放 skip）**
- 失败 → **优先修主路径 / 修 Fallback**
- **改 case 的硬门槛**：仅当 case 与产品目标 / 北极星 / S2todo 明确冲突时才允许改 case；改 case **必须在 PR 描述中显式写明**：
  - 原 case 内容（原文 quote）
  - 修改原因（哪条目标 / 哪条原则冲突 + 证据链接）
  - 影响范围（哪些下游 / 其他 case 受波及）
  - 是否需要回填新 case 替代
- 任何"为了通过把 case 放松"的改动 = 隐性降低测试标准，**禁止**（触发 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) Q5）
- 新发现 case → 回填该段表（持续累积，禁丢失）

**输出**：corner case 表的当前快照 + 新增 case 列表

### 2.8.3 冒烟

- 端到端最小 query 至少 1 single_ticker + 1 macro_event
- 整 run 不崩；fallback report 比例不上升
- P50 < 60s / P95 < **120s**（2026-09-08 由 90s 抬·[docs/roadmap/S2.md §7.4](../../roadmap/S2.md)）⚠️ 实测**端到端** 379–535s（大头在后 8 段：分析师 / 辩论 / 投票；**第一段实测仅 51.8s**）—— 该线长期是**目标**不是在守的闸

**输出**：smoke run 的 archive 路径 + 关键指标

### 2.8.4 彻底跑通才能进下一节点

- 任一项失败 → 修完再继续
- 任何 "known issue 先 skip" 必须升级为 deferred item 入 [docs/roadmap/S2.md §9](../../roadmap/S2.md) 并标明计划时机；**不允许沉默 skip**（沉默 skip 触发 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) Q5）

### 2.8.5 DoD 失败的处理

- DoD 任一步 ❌ 不过 → 回到 [04-goal-execution.md §2.5](04-goal-execution.md#25-单个-goal-执行) 同 goal 重做
- 重做次数：1-2 次正常；**≥ 3 次** → 升级为"goal 拆解有问题"，回到 [03-decomposition.md §2.4](03-decomposition.md#24-拆小任务) 重新拆解
- 重做过程中**不允许降低 DoD 标准**（触发 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) Q5）

### 2.8.6 DoD 无 ❌ → 进入 §2.9 evidence 收集

「无 ❌」= 四步全 ✅，或 ✅ 与 ⚪ 混合（§2.8.0）。有任何 ❌ 都回 §2.8.5，不进 §2.9。

### 2.8.7 临时脚本处置 (DoD 4 步完成后, 进 §2.9 前)

DoD 4 步全部 pass + §2.8.6 判定进入 §2.9 evidence 收集前,
主 Claude **必须**核对项目根 / tests/ 下无以下临时残留:

- `test_quick*.py` / `test_tmp*.py`
- `debug_*.py` / `dbg_*.py`
- `tmp_*.py` / `scratch_*.py`
- 任何"为了调试或快速验证"创建但不属于正式测试资产的脚本

**处置规则**:
- 有沉淀价值 → 转正为正式测试, 进 `tests/` 标准目录
- 一次性使用 → `rm` 删除
- **不允许**"留下次再说" / "可能以后还用得到"

**验证命令**:

```bash
find . -name "test_quick*.py" -o -name "test_tmp*.py" \
       -o -name "debug_*.py" -o -name "dbg_*.py" \
       -o -name "tmp_*.py" -o -name "scratch_*.py" 2>/dev/null
```

输出非空 = DoD 不通过, 必须处置后再进 DoD。

---

## 2.9 evidence 收集

**时机**：DoD 全过后，进 [07-retro-goal.md §2.10](07-retro-goal.md#210-goal-级-retro按需) retro 判定之前。

**关联 skill**：嵌入 `dod-checklist` skill 的后置动作（不单独 skill）。

### 2.9.1 evidence 类型

| 类型 | 来源 | 落地路径 |
|---|---|---|
| Review notes | §2.8.1 Code Review 输出 | PR 描述（不单独文件）/ 或 `docs/observations/<node-id>-review.md` |
| Corner case logs | §2.8.2 跑测的输出 | pytest 输出片段（embed in PR） / `tests/_archives/<timestamp>.log` |
| Smoke run logs | §2.8.3 冒烟 archive | `_archives/<timestamp>.json` |
| Archive replay result | 旧 archive 喂新 schema 的 replay log | `_archives/replay-<timestamp>.log` / 或 `N/A 不动 schema 时显式标` |
| 改 case 证据 | §2.8.2 改 case 时的必填四要素 | PR 描述 corner case 段 |

### 2.9.2 evidence 收集动作

1. **收集所有上述路径** → 形成清单
2. **验证路径真实存在**（防"盲跑不算"）
3. **生成 evidence summary**（结构化 markdown）：

   ```markdown
   ## Evidence Summary (goal <goal-id>)
   - Review notes: <path-or-PR-comment>
   - Corner case logs: <path>
   - Smoke archive: <path>
   - Archive replay: <path 或 N/A>
   - Modified cases: <count> (详见 PR §case 段)
   - 裁决回填清单: <见 §2.9.4，8 格逐项；本 goal 无裁决落地则 N/A>
   - DoD 三态计数: ✅ a / ❌ 0 / ⚪ c   ← §2.8.0；c 与交付单第三栏条数必须相等
   - 交付单: <见 §2.9.5；三栏齐、第三栏无则写「无」>
   ```

4. **evidence summary 进入 PR 描述模板**（[08-retro-node-and-pr.md §6](08-retro-node-and-pr.md#6-pr-描述模板决策溯源)）
5. **承重口径改动所依据的归档回放 / 探针，脚本与输出落一份 observation 产物**（`docs/observations/<node>-<goal>-<主题>-<日期>/` 下放 `replay.py` / `probe.py` + 输出 md，路径进 evidence summary 的 Archive replay 一格），不只写进 PR 描述或条目正文 —— PR 描述合并后难检索、数字无法复算。（CRED.1.G2 / 1.G3 retro baseline should_update·N=2·2026-09-24 节点收口 adopt；簇 2 / 簇 3 各 goal 已按此执行，本条把惯例写成规则。与 §2.8.7「临时脚本处置」不冲突：落进 observation 目录的回放脚本属证据资产、不是临时残留。）

### 2.9.3 evidence 缺失的处理

- 任一应有 evidence 缺失 → **不进 [07-retro-goal.md §2.10](07-retro-goal.md#210-goal-级-retro按需)**，回到 §2.8 补
- 显式标 N/A 必须有理由（如 "本 goal 不动 schema，无 archive replay"）
- 盲跑（没跑测就说 pass）= 触发 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) Q5，停

### 2.9.4 裁决落地 → **回填清单**（backlog **BU** 机制化 · 2026-09-04 立）

> **治的是什么**：做完一个裁决（线不动 / 立账 / 降档 / 观察点转正 / 口径改写…），
> **代码或条目改了，但别人照着办事的那几份文档没跟上** —— 真值源静默滞后。
> 受害者不是当事人，是**几周后照文档办事的那个人**：他白查一轮，还可能得出与事实**相反**的结论。
>
> **为什么单靠 [R7](../../../CLAUDE.md) 不够（规则接缝，非执行疏忽）**：R7 管的是「**状态切换**」
> （PR close/merge、翻案、flag 放弃、节点收口）；「**阈值裁决 / 条目立账**」不在它的触发事件类别里。
> 本节就是补这条缝。
>
> 🔑 **为什么必须是固定名单、不能靠当场想**：2026-08-31 那次**是照着列了清单再收口的**（BU 的正面数据点），
> 四处全同步 —— **但清单本身漏了 backlog 条目正文**，结果那条登记项的数字废弃了整整一周，
> 到 09-04 跑 e2e 才撞见。⇒ **人工现列清单必有盲区**。名单写死在这里，漏了看得见。

**何时触发**（任一为真，与 §2.9 其余步骤同批做）：

1. 定了、改了、或**明确不改**任何一条阈值 / 判据 / 预算线 / 触发条件
2. 立了、关了、降档了任何一条 backlog 条目或观察点
3. 把某个观察点转正成条目，或把某条规则/检查项**拔掉**
4. 改了任何"以后按这个口径办"的说法

**动作 —— 逐格过，每格必须给「改了 &lt;链接&gt;」或「N/A + 一句理由」，不许留空**：

| # | 候选真值源 | 典型形态 |
|---|---|---|
| 1 | **裁决自己那条 backlog 条目的正文** | 条目正文里引用的旧数字 / 旧阈值 —— ⚠️ **08-31 漏的就是这格**，放第一位 |
| 2 | [backlog](../backlog.md) 里**引用该结论的其它条目** | 别的条目正文引了这个数 / 这条线 |
| 3 | 跑批与操作指南（如[段式跑指南](../../observations/e2e-runs/segmented-e2e-guide.md)、[质量门](../e2e-quality-gate.md)） | 指南里的判据文本、指路链接 |
| 4 | [验收判据表](../e2e-acceptance-standard.md) | 维度归属 / 承重边界（hard-fail vs advisory） |
| 5 | [观察点表](../../observations/should_update_observations.md) | `O-*` 观察点的现值与计数 |
| 6 | 代码常量与注释 / docstring | 注释里写着旧值、旧机理 |
| 7 | 阶段路线图（[S2](../../roadmap/S2.md) 等）与主链路文档 | 状态表、预算线块 |
| 8 | **auto-memory**（含 `MEMORY.md` 索引行） | 记着旧结论的那条 memory |

**再加两道，与 R7 同一套手法**：

- **宽 grep 全仓扫**，关键词**必须含别名和旧框架词**（凭记忆列点必漏）。
- **分 live 与历史**：断言"现在如何"的 → **就地改口径**；point-in-time 记录（dated 落账块 / 归档 FINDINGS / 规划文档）→ **加前向一句，正文不动**；
  ⛔ **closed 条目 / 已冻结 verdict / 节点 retro = [Q6 冻结档](05-brake-self-check.md)，连 banner 都不加** —— 前向事实写去**引用方**。
- **收口后再 grep 一遍**，确认 live 旧措辞清零（残留只应是"否定旧框架"的新文字）。

**进 evidence summary**（§2.9.2 第 3 步模板追加一行）：

```markdown
- 裁决回填清单: <8 格逐项：改了 <link> / N/A + 理由>   ← 本 goal 无裁决落地则整行写 N/A
```

**缺失的处理**（与 §2.9.3 同级）：8 格里**任一格既没改也没写 N/A 理由** → 视同 evidence 缺失，
**不进 [§2.10 retro](07-retro-goal.md#210-goal-级-retro按需)**，回来补。

⚠️ **本节只要求"点名 + 交代"，不替你判断该不该改**：写 N/A 是完全正当的答案，
**空着不是**。这条纪律与 §2.9.3「显式标 N/A 必须有理由」同源。

### 2.9.5 交付单（固定三栏，2026-09-29 立）

> **治的是什么**：「未验证」的规则本来就有，但散在三处 —— [05 §2.7.5](05-brake-self-check.md#275-8-问详细判定标准)「到上限不自行免判」、
> [08 §6.2](08-retro-node-and-pr.md#62-pr-描述不可省略的段)「没跑 review 显式写未跑」、[09 §3 元规则](09-known-pitfalls.md)「报 0 / 全绿附成立条件」。
> 散着的规则靠记，记不住就退化成一句「全部通过」。本节把它们收成**每次交付都长一个样**的固定格式，格式本身就是提醒。

**何时用**：每个 goal 的最终汇报、每个节点 PR 描述（[08 §6](08-retro-node-and-pr.md#6-pr-描述模板决策溯源) 模板已内嵌）、任何"做完了"的对话收尾。**三栏都要有，顺序不变。**

```markdown
## 交付单 (goal <goal-id>)
档位: <S/M/L（入口）→ <同或升档>（DoD 对账）｜判据: <一行>>

### 改了什么
- <文件或模块>：<一句话说改动>
- ...

### 验证了什么、怎么验的
- <验证项>：<命令 / 手段> → <结果>   ← 报「0 问题 / 全绿」必附成立条件（扫了多少对象、凭什么是全集）
- ...

### 未验证什么、为什么
- <DoD 步骤或验证项> ⚪：原因 (a)/(b)/(c)/(d) + 一句说明 → 建议处置（等环境 / 请用户跑 / defer 到 <条目>）
- ...
（没有就写：无）
```

**四条硬规则**：

1. **第三栏不许空白**。没有未验证项就写「无」。空白 = evidence 缺失（与 §2.9.3 / §2.9.4 同级），不进 [§2.10 retro](07-retro-goal.md#210-goal-级-retro按需)。
2. **第三栏条数 = DoD 三态表的 ⚪ 计数**（§2.8.0）。不相等 = 有一条被藏了或被凑了，不许交付。这是抄 [§2.11.9](08-retro-node-and-pr.md#211-节点级复盘--pr-收口)「N = a + b + c 对不上不许合」的手法。
3. **第三栏每条只能用 §2.8.0 的四种原因**。写不进四种的，回去重看：多半是盲跑（→ Q5）或跑了红（→ ❌）。
4. **第三栏非「无」时，全文不得出现「全部通过 / 全绿 / all pass」**。第二栏可以逐项写 ✅，但不许给总评。
5. **档位行必填**（[01 §2.2.5](01-task-entry.md#225-任务分档s--m--l--2026-09-29-立)）：入口档位、DoD 对账后的档位、一行判据。S 档的交付单就是它全部的 evidence；档位行缺失 = 审的人无法核「本档不要求」站不站得住，视同第三栏空白。

**为什么是「格式」而不是再加一条规则**：本仓已有的三处规则证明"靠记"不够。固定格式让「没写第三栏」这件事**一眼可见**，审的人不用记规则也能问一句"第三栏呢"。

---

---

## Cross-references

**上游（我引用谁）**：

- [05-brake-self-check.md](05-brake-self-check.md) — 8 问未命中 / 用户裁决放行
- [03-decomposition.md](03-decomposition.md) — `<goal>` 的 `<verification>` / `<done_criteria>`
- [04-goal-execution.md](04-goal-execution.md) — 自验报告中的延迟 / fallback ratio 进冒烟段
- [docs/roadmap/S2.md](../../roadmap/S2.md) — §7.4 延迟预算 / §9 Deferred 入账 / 该段 corner case 表

**下游（谁引用我）**：

- [07-retro-goal.md](07-retro-goal.md) — DoD 全过 + evidence 收齐后进 retro 6 条触发判定
- [08-retro-node-and-pr.md](08-retro-node-and-pr.md) — evidence summary 进 PR 描述模板
- `dod-checklist` SKILL — 消费 §2.8 + §2.9 全节（含 §2.9.4 回填清单）
- [00-quickstart.md](00-quickstart.md) — 接入片段第 4 / 5 条引用 §2.8.0 三态 + §2.9.5 交付单；[完整案例](examples/walkthrough-cli-json-flag.md) 演示带 ⚪ 的交付
- [backlog.md](../backlog.md) — **BU** 条目触发条件 (B)「下次动收口文档时机制化」由 §2.9.4 兑现
