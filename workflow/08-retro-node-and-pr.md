# 08 Retro Node & PR — 节点级复盘 + PR 描述模板

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 关联子文档: [docs/governance/workflow/07-retro-goal.md](07-retro-goal.md) / [docs/governance/workflow/06-dod-and-evidence.md](06-dod-and-evidence.md)
> 关联 skill: `retrospective-node` + `pr-template`（均已 deprecated；详细规则现在本文件 §2.11 / §6，设计历史见 [docs/governance/skill-design.md §3.3](../skill-design.md#33-已-deprecated-skill7-个详细设计已迁至-workflow-子文档)）

## 何时读这份文档

节点所有 goal done 之后，PR 创建之前。本文档覆盖节点级复盘 5 问 + retro 产物落盘 + PR 描述模板（决策溯源）。

## 概览

- §2.11 节点级复盘：5 问 XML 结构 + 复盘文件命名 + 应用 q5_sedimentation 中应进本节点 PR 的 should_updates
- **§2.11.9 坐实 finding 的去处**：跑过 review 就必给 —— 每条 finding 恰好一个去处（修了 / 记账 / 明确不做），数目对不上不许合
- **§2.11.10 阶段收口时的归档**：阶段收口报告合并时建 `docs/archive/<阶段>.md` 索引页，文件不搬家
- §6 PR 描述模板：节点 / DoD / Evidence / **Review finding 去处** / 风险与 Fallback / 复盘 TL;DR 等 7 段固定结构
- §6.1-6.3 PR 描述与 commit message / 不可省段 / 复盘段 TL;DR 化的理由

---

## 2.11 节点级复盘 + PR 收口

**时机**：节点所有 goal done 之后。

**关联 skill**：`retrospective-node` + `pr-template`

### 2.11.1 节点级复盘 5 问

由 `retrospective-node` skill 执行，输出**结构化 XML 块**：

```xml
<retro_node id="<node-id>" subphase="S2.1|S2.2|S2.3" timestamp="<ISO 8601>">
  <q1_objective>
    <!-- 目标达成度 -->
    <achievement_ratio>0.0-1.0</achievement_ratio>
    <unachieved>...</unachieved>
    <reasons>...</reasons>
  </q1_objective>

  <q2_decomposition>
    <!-- 拆解准确度 -->
    <assessment>...</assessment>
    <wrong_granularity>...</wrong_granularity>
  </q2_decomposition>

  <q3_surprises>
    <!-- 意外与坑;ref_retro_goal 指向暴露此 surprise 的 goal retro -->
    <surprise ref_retro_goal="<goal-id>">...</surprise>
    <brake_judgment_review>...</brake_judgment_review>
  </q3_surprises>

  <q4_dod_blindspots>
    <!-- DoD 盲点 -->
    <missed_corner_cases>...</missed_corner_cases>
    <smoke_gaps>...</smoke_gaps>
    <差不多_moments>...</差不多_moments>
    <unverified_in_production>
      <!-- "逻辑通过 ≠ 实际验证":
           列在本节点 unit test 范围外、需 production 数据 /
           真实环境验证才能确认的项。常见例子:
             - 因依赖条件未达成(如节点不在子阶段末)而 skip 的 skill / 模块
             - 仅在 mock / 模拟数据上验证、未跑过真实 archive 的路径
             - 接口契约 review 通过但未端到端实跑的集成点
           每项必须给出 verification_path:
             "verification-report" | "skill-verification-todo" | "backlog" | "next-node" -->
      <item>
        <description>...</description>
        <verification_path>...</verification_path>
      </item>
    </unverified_in_production>
  </q4_dod_blindspots>

  <q5_sedimentation>
    <!-- 聚合所有 goal retro 的 <proposals>,按 [07-retro-goal.md §2.10.5](07-retro-goal.md#2105-should_update-分流表) 分流 -->
    <must_updates_already_applied>
      <item path="<file>" rule="..."/>
    </must_updates_already_applied>

    <should_updates_decisions>
      <should_update type="correctness|baseline|threshold|red-line"
                     decision="adopt|defer|reject">
        <suggestion>...</suggestion>
        <decision_reason>...</decision_reason>
        <target_pr>this_node | governance_pr | docs_commit | observation</target_pr>
      </should_update>
    </should_updates_decisions>

    <observes_accumulated>
      <count_by_signal>...</count_by_signal>
      <promoted_to_should_update>
        <!-- ≥ 3 次同类 → 升级 -->
      </promoted_to_should_update>
    </observes_accumulated>
  </q5_sedimentation>

  <next_node_unblocked>
    <!-- 解锁的下游节点(Cross-ref S2todo) -->
    <unblocked_node>A6.1.3</unblocked_node>
  </next_node_unblocked>
</retro_node>
```

### 2.11.2 节点级复盘的产物

**复盘文件命名**：`docs/retro/S2/<node-id>_<YYYY-MM-DD>.md`

- 节点 ID 在前，日期戳在后
- 同节点重做（撤销 PR 再来）产生多个文件，按日期区分：
  ```
  docs/retro/S2/
    A6.1.2_2026-05-13.md
    A6.1.2_2026-05-15.md  ← 同节点第二次（重做）
  ```

**产物清单**：

1. **完整 `<retro_node>` 写到** `docs/retro/S2/<node-id>_<YYYY-MM-DD>.md`
2. **PR 描述只嵌入复盘 TL;DR + adopted/deferred 裁决结果**（§6 模板的"复盘"段）
3. **PR 描述引用完整 retro 路径**：`docs/retro/S2/<node-id>_<YYYY-MM-DD>.md`
4. **所有 q5_sedimentation 中 "adopt 进本节点 PR" 的 should_updates**：在 PR 开 PR 之前应用
5. **其他类型的 should_updates**：按 [07-retro-goal.md §2.10.5](07-retro-goal.md#2105-should_update-分流表) 分流（governance PR / docs commit / observation / 人工确认）

**为什么 PR 描述只嵌 TL;DR 不嵌完整复盘**：

- squash merge 后 PR 描述进入 main commit body
- 完整复盘进 main history 会让 history 变重
- TL;DR + 链接 既保留 review 可见性，又不污染 main

### 2.11.3 复盘强制度

- **不可省**：每个节点收口必做
- **可缩**：低风险节点 5 问每问 1 句话即可；高风险节点必须完整
- **沉默跳过 = 触发 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) Q5（降低标准）**

### 2.11.4 节点级复盘后的动作序列

```
节点所有 goal done
  → 跑 retrospective-node skill
  → 写 docs/retro/S2/<node-id>_<YYYY-MM-DD>.md（main 上 1 个 docs(retro): commit）
  → 应用 q5_sedimentation 中 type=correctness/schema/test 的 should_updates 到节点工作分支
  → type=baseline/skill/template 的 should_updates 拆为独立 governance PR 或 docs commit（不混入节点 PR）
  → type=threshold 的 should_updates 登记到 docs/observations/should_update_observations.md
  → type=red-line 的 should_updates 停下问用户
  → [推荐] 跑 cold review（§2.11.7），Finding 追加到 retro 文件
  → push 节点工作分支
  → [push 前] 检查 backlog §4.4 计数（本 PR 是否新增 backlog 条目导致超限）
  → gh pr create (按 git-workflow.md §4)
  → 输出 PR 链接
  → [PR merge 后] 更新 Plan.md 状态 (§2.11.5)
  → [PR merge 后] 清理本节点 worktree + 本地分支 (§2.11.6)
  → 异步：继续推 S2todo 下一节点
```

详细 git 操作见 [docs/governance/git-workflow.md §4.6](../git-workflow.md#46)。

### 2.11.5 Plan.md 状态更新 (节点收口必做)

节点 PR merge 后, 主 Claude **必须**把 `docs/plans/<node-id>-decomposition.md` 顶部更新为:

```markdown
**节点状态**: ✅ 已完成 (YYYY-MM-DD, PR #<num> merged to main)
**回顾**: 见 [docs/retro/S2/<node-id>_<date>.md](../retro/S2/<node-id>_<date>.md)
```
原顶部若有 "用户确认状态" / "decomposition 状态" 等字段, 改为 "节点状态" 统一; `grep "节点状态.*已完成" plan.md` 空 = 收口不完整。

### 2.11.6 Worktree / 分支清理 (节点 PR merge 后必做)

节点 PR merge 后，主 Claude **必须**清理本节点对应的 worktree 和本地分支：

```bash
# 1. 列出残留 worktree
git worktree list

# 2. 删除本节点 worktree（若从 worktree 内执行，先切到主仓库目录）
git worktree remove .claude/worktrees/<worktree-name> --force

# 3. 删除本地分支（远程分支已被 gh pr merge --delete-branch 删除）
git branch -d <branch-name>

# 4. 若 worktree remove 报 Permission denied（进程占用），
#    检查目录是否为空壳（无 .git 文件），空壳直接 rm -rf
```

**为什么必做**：

- Claude Code worktree 隔离模式每个 session 创建一个 worktree，session 结束后不自动清理
- 累积的空 worktree 目录占磁盘 + 污染 `git worktree list` 输出
- 残留的本地分支让 `git branch` 列表膨胀，降低可读性

**豁免**：当前 session 正在使用的 worktree 不清理（session 结束时由 Claude Code 自行回收）。

### 2.11.7 Cold review（推荐，非强制）

**时机**：节点级复盘完成后、PR merge 前。

**推荐做法**：节点收口时跑一次 cold review，产出 Finding 列表。Finding **不阻断 PR**，但**必须登记到节点 retro 文件**作 self-correction 数据点。

**如果跳过 cold review**：节点 retro 必须显式说明"本节点未跑 cold review + 原因"（如：低风险节点 / 时间约束）。沉默跳过 = 触发 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) Q5（降低标准）。

**载体选择（按 provenance 强度排序）**：

| 优先级 | 载体 | provenance 等级 |
|---|---|---|
| 1 | Cross-session 双盲（新 session、不同对话） | 🟢 高 |
| 2 | 不同模型（GPT-4 / Gemini / 等） | 🟢 高 |
| 3 | 同 session warm-cold（间隔后自己 review） | 🟡 中 |
| 4 | 人工自审 | 🟡 中 |

低 provenance 载体可以用，但 retro **必须标注 provenance 等级**，便于回溯"哪些发现来自强 provenance / 弱 provenance"。

**数据来源**：backlog J N=2 验证 — A6.1.2 + A6.1.3 节点级 cold review 均稳定产出 ≥3 Finding。cross-session 与 warm-cold 均有数据，warm-cold provenance 弱于 cross-session（A6.1.3 retro O-A6.1.3-03 已标注）。

**升级路径**：出现 N≥1 个"跳了 cold review 后 production 出 bug"的反面数据 → 升级为强制。

**Agent 现状审视（§4.6 交叉引用）**：改动 agent prompt / schema / 必填规则的 PR，retro 必须引用 [S2.md §4.6 Agent 现状审视](../../roadmap/S2.md) 基线文档（`docs/governance/agent-review-s2.X.md`）并更新对应行。防止"改了 prompt 但没人记得"漂移。来源：S2.2-gate 三根因（economist stub 空置 / REF# 注入漏 / rework 盲重试）。

### 2.11.8 achievement_ratio 计算规则

**适用范围**：`<retro_node>` XML 的 `<q1_objective>` 段 `<achievement_ratio>` 字段。

| 分档 | 含义 | 条件 |
|---|---|---|
| **1.0** | 节点目标 100% 达成 | 无 defer 项、无 unachieved 项 |
| **0.9-0.99** | 主要目标达成，有少量 defer | 1-N 个 defer 项已显式登记（backlog 或 S2todo） |
| **0.7-0.89** | 部分目标达成 | 需 backlog / S2todo 跟进的重要未完项 |
| **< 0.7** | 节点应升级回拆解或重做 | 核心目标未达成 |

**强制规则**：**有 defer 项时 ratio 不能填 1.0**。defer 必须扣分（最高 0.99）。

**来源**：backlog M — A6.1.2 retro `achievement_ratio=1.0` 但有 2 项显式 defer（真实数据源接入 + DISPATCHER_TOTAL_TIMEOUT 验证），印证"自动标 1.0 但有 defer 项"的模式。本规则阻断此模式再现。

### 2.11.9 坐实 finding 的**去处**（合并前必给 · 2026-09-07 立）

> **治的是什么**：review 查出一堆 finding，合并时修掉一部分，剩下那些「**坐实、但这次不修**」的
> **没有强制去处** —— 于是它们随 PR 一起合进 main，**从此没有家**。
> 靠的是执行体事后自己想起来补账；想不起来，就是一条查清楚过的问题凭空消失。
>
> **两次实证**：
>
> | 时间 | 场景 | 后果 |
> |---|---|---|
> | 2026-09-02 | PR [#269](https://github.com/JunoChenZt/subagent-for-investment/pull/269)：16 条坐实、修 13 记 3 | 「商品行情腿装进个股袋」既没修也没记账 ⇒ **PR 一合它就没家了**，靠合并后立即补账才救回（补立 `DEFECT-COMMODITY-AS-TICKER`）。当时记为形态，注明"第 2 次即提立" |
> | 2026-09-07 | #271–#274 四个 PR | **四条坐实 finding 合并时无一进账**，靠事后清点才补上（⑮ ⑯ + 读档白名单 + 相对路径） |
>
> **用户 2026-09-07 裁：不立 backlog 条目**（登记的仪式比干活贵；且 lettered 活跃 15 已满，
> 提立要开第 17 次破例）—— 直接把这道义务焊进收口固定动作，与 [§2.9.4](06-dod-and-evidence.md#294-裁决落地--回填清单backlog-bu-机制化--2026-09-04-立) 同一手法。
>
> **与邻近两条的分工**（三条同族、不同环节，别混）：
>
> | 规则 | 管的环节 |
> |---|---|
> | [R7](../../../CLAUDE.md) 全仓收口 | **状态切换**落地后，旧口径要扫干净 |
> | [§2.9.4](06-dod-and-evidence.md#294-裁决落地--回填清单backlog-bu-机制化--2026-09-04-立) 回填清单 | **改了的东西**，真值源要跟上 |
> | **本节** | **没改的东西**，要有家 |

**何时触发**：任何 PR 合并前，只要这轮跑过 review（cold review / high-effort review /
用户当面指出 / 自查）**且产出过 finding**。与 §2.11.7 的关系：那节管"finding 要登记到
retro 文件"，本节管"每一条必须有且只有一个去处，且数目对得上"。

**动作 —— 每条坐实 finding 恰好一个去处，不许留空**：

| 去处 | 落在哪 | 判据 |
|---|---|---|
| **本 PR 修了** | PR 描述 + commit | 有对应改动；承重的还要有守护 |
| **进 backlog** | 条目正文 / 登记项（DEFECT 族不占 lettered 配额） | 带**它自己的触发条件** —— "以后再说"不算 |
| **明确不做** | PR 描述里一句理由 | 说清"为什么这不是问题"或"为什么代价不值" |

⛔ **"提了一嘴、没写进任何地方"不算去处。** 合并前 PR 描述里数目必须对得上：

```
坐实 N 条 = 本 PR 修 a + 记账 b + 明确不做 c
```

**a + b + c ≠ N 就不许合。**

⚠️ **"坐实"由**提出方**认定，不由被审方认定** —— 执行体不得靠"我觉得这条不成立"把它移出分母；
认为不成立就走第三格（明确不做 + 理由），**分母不变**。少了这一刀，本节可以被"重新数一遍 N"架空。

**缺失的处理**：合并后才发现有 finding 没去处 → **立即补账**，并在 backlog 落账块里记一笔。
（本条规则自己就是这么被补出来的 —— 两次都是事后清点才救回。）

### 2.11.10 阶段收口时的归档（2026-09-28 立）

> 来源：backlog O 任务 2，S2 收口 G2 落地。归档**是什么、怎么做**见 [docs/archive/README.md](../../archive/README.md)，本节只管**何时做、做到什么算完**。

**何时触发**：**阶段**收口（S2 / S3 / …）的收口报告合并时。**子阶段交接不触发**：子阶段已有交接报告做系统回顾，再建一层索引没人读。

**动作（与收口报告同一个 PR）**：

1. 在 `docs/archive/` 建 `<阶段>.md` 索引页，按 README §1 的六类逐类列全；
2. 在索引页给每类标明适用的既有规则（Q6 冻结 / R7 前向说明），不另立冻结规则；
3. **不搬任何文件**；要搬走 README §3，另需用户裁；
4. 在阶段真值源 `docs/roadmap/<阶段>.md` 顶部加一行指向索引页；
5. **收口报告里的移交清单，同一个 PR 写进下一阶段的 roadmap 文件**（S2 收口复盘沉淀：S2.3 交接报告写了「S3 必含」四项，此后三个多月 S3.md 一条都没收，交接实际断了）。

**做到什么算完**：索引页存在，六类各有内容或写明「本阶段无」；下一阶段 roadmap 里能找到移交清单；`scripts/lint_doc_links.py` 全绿。

---

---

## 6. PR 描述模板（决策溯源）

每个节点收口 PR 描述应含以下结构：

```markdown
## 节点
- ID: [如 A6.1.2 / P4.B.4]
- 子阶段: [S2.1 / S2.2 / S2.3]
- 依赖: 上游 ✅ 节点列表
- 拆解: [本节点拆为 N 个 /goal 小任务，列出 ID 或链接 docs/plans/<node-id>-decomposition.md]

## DoD 通过证据
- [ ] Code Review: [review notes / 自查结论]
- [ ] Corner Case: [跑过的 case 列表 + 结果]
- [ ] 冒烟: [query + 延迟 + fallback ratio]
- [ ] 彻底跑通: 无 known issue skip / 无回归

## Evidence 路径（必填，盲跑不算）
- Review notes: `<docs/observations/<node-id>-review.md 或 PR comment hash>`
- Corner case logs: `<path-to-test-log 或 pytest 输出片段>`
- Smoke run logs: `<path-to-smoke-archive 或 _archives/ 时间戳>`
- Archive replay result: `<path-to-replay-log 或 N/A 不动 schema 时显式标>`
- 改 case（如有）: `<引用 §2.8.2 必填四要素的具体位置>`

## Review finding 去处（跑过 review 就必填 · §2.11.9）
- 坐实 N 条 = 本 PR 修 a / 记账 b（条目或登记项链接）/ 明确不做 c（各带一句理由）
- [N ≠ a+b+c 就不许合；本轮没跑 review 则整段写"未跑 review"]

## 风险与 Fallback
- 风险层级: [低 / 中 / 高（按 §2.2 判定）]
- 引入的 Fallback 路径: [如：智堡 MCP 失败 → 仅 common_context]
- 北极星 / 稳定性边界: [未触及 / 已校验]
- §2.7 8 问刹车触发情况: [未触发 / 触发了哪条 + 用户裁决结果]

## 复盘 TL;DR

- **节点目标达成度**: [一句话]
- **Process issue found**: [若有；无则填"无"]
- **Adopted improvement (本 PR 内应用)**: [若有；无则填"无"]
- **Deferred to governance PR**: [若有；列单独 PR 链接 / 计划]
- **Observed (待累积)**: [若有；进 observation 队列]
- **完整 retro**: [docs/retro/S2/<node-id>_<YYYY-MM-DD>.md](../retro/S2/<node-id>_<YYYY-MM-DD>.md)

## 后续
- 解锁的下游节点: [...]
- 新发现 corner case 回填: [...]
- Deferred 入账: [若有 known issue 升级为 deferred]
```

### 6.1 PR 描述与 commit message 的关系

- PR title 就是 squash merge 后 main 上的 commit subject（详 [docs/governance/git-workflow.md §4.3](../git-workflow.md#43)）
- PR description 会被 squash merge 自动追加到合并后 commit body
- 所以写好 PR description = 写好 main 上的最终 commit message
- **复盘段只放 TL;DR + 链接**，完整复盘在 `docs/retro/`，避免污染 main history

### 6.2 PR 描述不可省略的段

- 节点 ID / 子阶段 / 依赖
- DoD 4 项的 ✅
- Evidence 路径
- **Review finding 去处**（跑过 review 就必填，见 §2.11.9；没跑则显式写"未跑 review"）
- 风险与 Fallback
- 复盘 TL;DR + 完整复盘链接

可选段：流程改进建议（无则省略）、后续（无则省略）

### 6.3 PR 描述里的复盘段为什么是 TL;DR

- squash merge 后 PR description 进入 main commit body
- 完整复盘进 main 会让 history 变重
- TL;DR + 链接 既保留 review 可见性，又不污染 main history
- 完整复盘在 `docs/retro/S2/<node-id>_<YYYY-MM-DD>.md`，可独立追溯

---

## Cross-references

**上游（我引用谁）**：

- [07-retro-goal.md](07-retro-goal.md) — 所有 `<retro_goal>` 列表（q5_sedimentation 聚合输入） / §2.10.5 分流表
- [06-dod-and-evidence.md](06-dod-and-evidence.md) — evidence 路径 / DoD 4 项进 PR 描述
- [01-task-entry.md](01-task-entry.md) — §2.2 风险判定结果进 PR 风险段
- [05-brake-self-check.md](05-brake-self-check.md) — 8 问刹车触发情况进 PR 风险段 / Q5 沉默跳过约束
- [docs/governance/git-workflow.md](../git-workflow.md) — §4 PR 创建 / §4.3 PR title / §4.6 节点收口动作

**下游（谁引用我）**：

- [10-verification-report.md](10-verification-report.md) — 节点 retro 文件被子阶段交接审视消费
- [docs/governance/git-workflow.md](../git-workflow.md) §4 — 引用 §6 PR 模板填 PR description
- `retrospective-node` SKILL — 消费 §2.11 全节
- `pr-template` SKILL — 消费 §6 全节
