# Skill 设计文档

> **本文件定位（重构后 2026-05-14）**：subagent 化 skill 的设计真值源 + 跨 skill 一致性元规则。
>
> ⚠️ **重要状态变化**：A6.1.1 节点实证发现 9 个 skill 中 7 个非 subagent skill 节点期 0 触发。本次重构（skill-system-refactor）将设计真值源迁移到 `docs/governance/workflow/` 子文档：
>
> - **workflow.md 子文档 = 真值源**（主 Claude 实际读的执行手册；XML schema 已迁移至此）
> - **本文件 = subagent 化 skill 设计真值源**（仅 `pitfall-scout` + `verification-report`）+ 跨 skill 一致性元规则
> - **7 个 deprecated skill**（risk-judgment / goal-decomposition / brake-self-check / dod-checklist / retrospective-goal / retrospective-node / pr-template）：详细设计已迁至对应 workflow 子文档；此处保留占位反映 9 skill 设计历史
>
> 详见 §7.4 迭代历史。
>
> 父文档：[docs/governance/workflow.md](workflow.md)
> 关联：[docs/governance/git-workflow.md](git-workflow.md) / [CLAUDE.md](../../CLAUDE.md)

---

## 0. 设计原则

### 0.1 单一职责

每个 skill 只解决一类问题。如果一个 skill 既判风险又拆任务，说明应该拆成两个。

判定标准：**一个 skill 的"触发条件 + 输入 + 输出" 能用 3 行说清楚**；说不清就该拆。

### 0.2 引用 workflow.md 而非重复

SKILL.md 内不重写规则，只引用 [docs/governance/workflow.md](workflow.md) 子文档章节。

- ✅ "按 [workflow/05-brake-self-check.md §2.7](workflow/05-brake-self-check.md#27-刹车自检8-问) 跑 8 问"
- ❌ 在 SKILL.md 里把 8 问全文复述一遍

这条原则确保：workflow.md 改了规则，skill 自动跟着改；不会出现"workflow.md 说 A、SKILL.md 说 B"的漂移。

### 0.3 现状：skill 系统主要由 workflow 子文档驱动

A6.1.1 实证（2026-05-14 verified）：`.claude/settings.json` hooks 段空（时点记录，见下更新）；主 Claude 全节点 0 次 Read 任何 `.claude/skills/<name>/SKILL.md`；9 SKILL.md 中 7 个普通 skill 0 触发；仅 `pitfall-scout`（subagent 化 via Task tool）100% 触发。

> ✅ **更新（2026-05-19，backlog L CLOSED）**：hooks 已落地——`.claude/settings.json` 现有完整 hooks 段（PreToolUse / TaskCompleted / UserPromptSubmit / SessionStart，G3 由 b204acf + 80cb737 + 1ad493f 完成）。上段"hooks 段空"为 2026-05-14 时点记录，已过期。

**结论**：主 Claude 实际依赖 workflow 子文档 + 训练记忆 + cold review，**非 SKILL.md 强制触发**。仅 2 个 subagent 化 skill 通过 Task tool 显式派遣机制可靠；hook 层（2026-05-19 落地）另构成程序化闸门。详见 §1 / §4。

### 0.4 接口稳定 vs 内容可变

subagent 化 skill 的**输入 / 输出 XML schema 必须稳定**（改它 = 改 workflow.md，需重大调整流程）。

skill 的**内部 prompt / 措辞 / 例子可变**（实现细节迭代，不影响协作）。

### 0.5 失败处理统一风格

所有 skill 遇到失败时的默认行为：

1. **不丢已有产物**：保留前置 skill 的输出
2. **输出失败原因 + 当前状态 + 建议下一步**（统一格式见 §6.5）
3. **停下问用户，不自动 retry > 1 次**（具体 skill 可覆盖）
4. **触发 [CLAUDE.md](../../CLAUDE.md) 强制红线时立即停**，不进入失败处理流程

### 0.6 跨 skill 一致性规则（护栏）

详见 §6。简而言之：

- XML 根标签命名一致（`<retro_goal>` / `<retro_node>` / `<goal>` / `<pitfall_alerts>` / `<verification_report>`）
- 引用 workflow.md 用 `[docs/governance/workflow.md §X.Y](workflow.md#xy)` 格式
- 时间戳用 ISO 8601
- skill 之间的数据传递永远通过结构化 XML，不靠 chat 上下文

### 0.7 subagent 化 skill

部分 skill 标注为 subagent 化执行，理由是它们**读量大、产出短**，适合 subagent 隔离 context 后只返回结构化结果。

当前 2 个：

- `pitfall-scout` — 读 §3 已知坑全表（≈ 400 行），返回 3-5 条 alerts
- `verification-report` — 读 §3 + 所有节点 retro + observation 累积，返回 PASS/FAIL + summary

详见 §3 详细设计、§6.9 subagent 化 skill 的额外约束。

---

## 1. Skill 全景图

### 1.1 当前生效（2 个 subagent 化 skill）

| # | skill name | 一句话定位 | trigger | 对应 workflow 子文档 |
|---|---|---|---|---|
| 1 | `pitfall-scout` | subagent 扫描 §3 已知坑表，返回本任务相关 3-5 条 | 节点工作分支起步前 / 用户主动 | [workflow/09-known-pitfalls.md §3.11](workflow/09-known-pitfalls.md#311-pitfall-scout-subagent-工作方式) |
| 2 | `verification-report` | 子阶段交接的 §4 全套审视，subagent 化 | 子阶段最后一个节点 PR 合并后 / 用户主动 | [workflow/10-verification-report.md §4.6](workflow/10-verification-report.md#46-verification-report-subagent-工作方式) |

详细设计见 §3.1 / §3.2。

### 1.2 已 deprecated（7 个非 subagent skill）

A6.1.1 实证 0 触发；详细规则已迁至 workflow 子文档；SKILL.md 保留但不当强制机制：

| skill name | 已迁至 workflow 子文档 | 此前 skill-design.md 位置 |
|---|---|---|
| `risk-judgment` | [workflow/01-task-entry.md §2.2](workflow/01-task-entry.md#22-风险判定5-条触发即高风险) | 历史 §3.1 |
| `goal-decomposition` | [workflow/03-decomposition.md §2.4.3 + §2.4.7](workflow/03-decomposition.md#243-goal-xml-模板) | 历史 §3.3 |
| `brake-self-check` | [workflow/05-brake-self-check.md §2.7](workflow/05-brake-self-check.md#27-刹车自检8-问) | 历史 §3.4 |
| `dod-checklist` | [workflow/06-dod-and-evidence.md §2.8 + §2.9](workflow/06-dod-and-evidence.md) | 历史 §3.5 |
| `retrospective-goal` | [workflow/07-retro-goal.md §2.10](workflow/07-retro-goal.md#210-goal-级-retro按需) | 历史 §3.6 |
| `retrospective-node` | [workflow/08-retro-node-and-pr.md §2.11](workflow/08-retro-node-and-pr.md#211-节点级复盘--pr-收口) | 历史 §3.7 |
| `pr-template` | [workflow/08-retro-node-and-pr.md §6](workflow/08-retro-node-and-pr.md#6-pr-描述模板决策溯源) | 历史 §3.9 |

**deprecated 的含义**：

- 这些 skill 对应的**规则仍生效**（workflow 子文档真值源）
- SKILL.md 文件本身**不删除**（G2 范围 — 标 deprecated 但保留为参考文档）
- 主 Claude 跑 workflow 时**直接读 workflow 子文档**，不再依赖 SKILL.md 中转
- 未来若实证某条 deprecated skill 通过 hook 或显式 invoke 真生效，可"恢复"为生效 skill（需重新走设计协议）

### 1.3 关键观察

- **2 个 subagent 化 skill** 通过 Task tool 派遣，机制 100% 可靠（不靠语义匹配）
- **7 个 deprecated skill** 的语义匹配触发机制实证无效；规则已落 workflow 子文档
- workflow.md 子文档 = 主 Claude 执行手册；本文件 = subagent skill 设计 + 元规则

---

## 2. Skill 协作流

### 2.1 主驱动：workflow.md 子文档

主 Claude 拿到任务后按 [workflow.md 10 步主链路](workflow.md) 走，在每个子文档对应步骤直接产出（包括 XML 输出）。**不通过 SKILL.md 中转**。

### 2.2 Subagent 调度

仅 2 个 subagent skill 需要主 Claude 主动派 Task tool：

| 时机 | Subagent | 输入 | 输出 → 消费 |
|---|---|---|---|
| 节点工作分支起步前 | `pitfall-scout` | 任务上下文 + §3 全表 | `<pitfall_alerts>` (3-5 条) → 进 `<decomposition_input>`；每条 `<action>` 必须落地到 `<goal><stop_conditions>` |
| 子阶段最后一个节点 PR 合并后 | `verification-report` | 子阶段全部节点 retro + §3 快照 + observation 累积 + ledger | `<verification_report>` (PASS/FAIL) → 落盘 `docs/observations/`；PASS 解锁下一子阶段，FAIL 该子阶段后续节点不得开工 |

### 2.3 协作约束

- **subagent 不修改文件**：只读 + 产出 XML，实际落盘由主 Claude 完成（详 §6.9）
- **deprecated skill 的"协作"实际由 workflow 子文档驱动**：如 `goal-decomposition` 的 `<decomposition_input>` schema 已在 [workflow/03-decomposition.md §2.4.7](workflow/03-decomposition.md#247-decomposition_input--decomposition_output-包装-schema)，主 Claude 直接按 workflow 产出，不调 SKILL.md

---

## 3. Subagent 化 skill 详细设计

### 3.1 `pitfall-scout`

**定位**：subagent 化的已知坑识别。读 §3 对应子阶段 + 通用节，结合任务描述，返回本任务相关的 3-5 条坑 alerts。

**为什么 subagent 化**：§3 全表 ≈ 400 行；主对话直接读消耗大量 context。subagent 隔离后只返回 < 30 行结构化 alerts。

**何时触发**：节点工作分支起步前（主 Claude 在 [workflow/02-pre-flight.md](workflow/02-pre-flight.md) 阶段调用） / 用户主动 `/pitfall-scout`。

**输入**：任务描述 + 子阶段（S2.1/S2.2/S2.3）+ 涉及文件/模块/节点 ID + `<goal>` XML（若已拆解）。

**输出 schema**（同时在 [workflow/09-known-pitfalls.md §3.11](workflow/09-known-pitfalls.md#311-pitfall-scout-subagent-工作方式)，此处为 subagent skill 真值源）：

```xml
<pitfall_alerts task_ref="<task-id 或 goal-id>" subphase="S2.1|S2.2|S2.3">
  <scanned_sections>
    <section>§3.2 通用</section>
    <section>§3.3 S2.1 召回层</section>
  </scanned_sections>
  <alerts count="3-5">
    <pitfall ref="§3.3" severity="🔴" status="active">
      <pitfall_text>Query Classification LLM 必带 regex / macro_event fallback</pitfall_text>
      <relevance>本 goal 改 facts/cache.py，触发"缓存层 WAL 模式"约束；若同时改 query_classification 必须保 fallback</relevance>
      <action>改动前 grill cache.py 的 WAL 实现 + 确认 fallback 链未断</action>
    </pitfall>
    <!-- 3-5 条 -->
  </alerts>
  <skipped_irrelevant>
    <section ref="§3.7">S2.2 D/E/F 类规则 — 本任务在 S2.1，跳过</section>
  </skipped_irrelevant>
</pitfall_alerts>
```

**上下游**：消费节点起步前任务上下文 + 读 [workflow/09-known-pitfalls.md §3](workflow/09-known-pitfalls.md#3-已知坑--防回归-checklist) 全表；产出 `<pitfall_alerts>` 进 `<decomposition_input>`（详 [03-decomposition.md §2.4.7](workflow/03-decomposition.md#247-decomposition_input--decomposition_output-包装-schema)）。

**边界**：

- 不修改 §3（must_update 落盘是 [workflow/07-retro-goal.md §2.10.7](workflow/07-retro-goal.md#2107-must_update-的落盘) 职责）
- 不判风险（[workflow/01-task-entry.md §2.2](workflow/01-task-entry.md#22-风险判定5-条触发即高风险)） / 不拆任务（[workflow/03-decomposition.md §2.4](workflow/03-decomposition.md#24-拆小任务)）
- alerts ≤ 5 条；超过 = 任务范围过大，建议先拆任务再扫
- 若 §3 对应子阶段表为空 → 输出空 alerts + 标注"该子阶段坑表未建立"
- subagent 无状态：每次任务起步重新调用，不复用 context

---

### 3.2 `verification-report`

**定位**：子阶段交接的 §4 全套审视。subagent 化，跑完整 verification report 模板，输出 PASS/FAIL。

**为什么独立成 skill 而非 retrospective-node 的 mode**：稀疏事件（每子阶段仅 1 次，S2 总 3 次）+ 读量大（§3 全表 + 所有节点 retro + observation 累积 + ledger）+ 输出只需 verdict + summary → subagent 隔离 context 最优。

**何时触发**：子阶段最后一个节点 PR 合并后主 Claude 自动调用 / 用户主动 `/verification-report S2.1`。不由 hook 强制（子阶段完成不是高频事件）。

**输入**：子阶段 ID + 该子阶段所有节点 retro 文件路径 + §3 当前快照 + `docs/observations/should_update_observations.md` + S2todo ledger + 子阶段对应 hard-fail 检查项（如 S2.1 的 m4/m5/m6/m7/m8/m13）。

**输出 schema**（同时在 [workflow/10-verification-report.md §4.6](workflow/10-verification-report.md#46-verification-report-subagent-工作方式)，此处为 subagent skill 真值源）：

```xml
<verification_report subphase="S2.1|S2.2|S2.3" timestamp="<ISO 8601>" verdict="PASS|FAIL">
  <node_completion>
    <node id="A6.1.1" status="done" commit="<hash>"/>
    <!-- 所有节点 -->
  </node_completion>

  <hard_fail_checks>
    <check name="m4" status="pass|fail" evidence="<path>"/>
    <!-- 6 项或更多 -->
  </hard_fail_checks>

  <observation_metrics>
    <fallback_ratio current="X%" baseline="Y%"/>
    <p50 current="A ms" budget="60s"/>
    <p95 current="B ms" budget="120s"/>
    <archive_replay all_pass="true|false"/>
  </observation_metrics>

  <pitfall_status_review>
    <status_change pitfall_ref="§3.3 item-2" from="active" to="mitigated" reason="..."/>
    <still_active count="N">
      <ref>§3.3 item-1</ref>
    </still_active>
    <retired count="M">
      <ref>§3.4 item-5</ref>
    </retired>
  </pitfall_status_review>

  <observation_accumulation_review>
    <promoted_to_should_update count="N">
      <signal>...</signal>
      <reason>累积 ≥ 3 次</reason>
    </promoted_to_should_update>
    <stale_observations count="M">
      <signal>...</signal>
    </stale_observations>
  </observation_accumulation_review>

  <empirical_value_review>
    <must_update_count_trend>
      <avg_per_node>1.2</avg_per_node>
      <adjustment_suggested>none|raise|lower</adjustment_suggested>
    </must_update_count_trend>
    <parallel_wip_actual_peak>3</parallel_wip_actual_peak>
    <wip_adjustment_suggested>none|raise_to_4|lower_to_2</wip_adjustment_suggested>
  </empirical_value_review>

  <deferred_items>
    <item>...</item>
  </deferred_items>

  <final_verdict>
    <result>PASS|FAIL</result>
    <fail_reasons>
      <reason>...</reason>
    </fail_reasons>
    <next_subphase_unblocked>true|false</next_subphase_unblocked>
  </final_verdict>
</verification_report>
```

**上下游**：消费子阶段全部节点 retro + §3 快照 + observation 累积 + ledger；产出 `docs/observations/{sN}-verification-report-<date>.md`（[workflow/10-verification-report.md §4.5](workflow/10-verification-report.md#45-verification-report-模板) 模板）+ 触发 §3 status 调整（`docs(baseline):` commit）+ 触发经验值微调（[workflow/07-retro-goal.md §2.10.4](workflow/07-retro-goal.md#2104-retro-质量门槛数量约束) / [workflow/11-cadence.md §5.2](workflow/11-cadence.md#52-并行节点-wip-limit)）。FAIL 时升级 deferred 进 [S2todo §9](../roadmap/S2.md)。

**边界**：

- 不修改 workflow.md（用户决定 + `docs(baseline):` commit）
- 不能跳过 hard_fail 任一项（[workflow/10-verification-report.md §4.4](workflow/10-verification-report.md#44-fail-处理) FAIL 处理）
- 不擅自删 §3 已知坑（[workflow/09-known-pitfalls.md §3.10](workflow/09-known-pitfalls.md#310-已知坑维护协议只增不减) 只增不减；只能改 status 不能删条目）
- FAIL 时该子阶段后续节点不得开工直到修复（但 Claude 可继续工作其他子阶段无关节点）
- subagent 输出 ≤ 200 行（详细数据进落盘文件，主对话只接 verdict + summary）
- subagent 系统 prompt 应包含 workflow/10 §4 + workflow/09 §3 + workflow/07 §2.10 + workflow/11 §5.2

---

### 3.3 已 deprecated skill（7 个，详细设计已迁至 workflow 子文档）

以下 7 个 skill 的详细设计 / XML schema / 边界规则 / 上下游引用**已迁移到对应 workflow 子文档**。此处仅保留占位 + 索引，反映 9 skill 设计历史。**主 Claude 跑这些步骤时应直接读对应 workflow 子文档**，不再依赖 SKILL.md 中转层。

| skill | 历史定位 | 详细设计现位置 |
|---|---|---|
| `risk-judgment` | 判定大任务的风险层级 (high/low) | [workflow/01-task-entry.md §2.2](workflow/01-task-entry.md#22-风险判定5-条触发即高风险) |
| `goal-decomposition` | 把大任务拆成 `<goal>` XML 列表 | [workflow/03-decomposition.md §2.4.3 + §2.4.7](workflow/03-decomposition.md#243-goal-xml-模板) |
| `brake-self-check` | goal 完成后跑 8 问刹车自检 | [workflow/05-brake-self-check.md §2.7](workflow/05-brake-self-check.md#27-刹车自检8-问) |
| `dod-checklist` | 执行 DoD 四步并收集 evidence | [workflow/06-dod-and-evidence.md §2.8 + §2.9](workflow/06-dod-and-evidence.md) |
| `retrospective-goal` | non-trivial goal 完成后产 must/should/observe | [workflow/07-retro-goal.md §2.10](workflow/07-retro-goal.md#210-goal-级-retro按需) |
| `retrospective-node` | 节点收口前 5 问 + sedimentation | [workflow/08-retro-node-and-pr.md §2.11](workflow/08-retro-node-and-pr.md#211-节点级复盘--pr-收口) |
| `pr-template` | 按 §6 模板起草 PR title + description | [workflow/08-retro-node-and-pr.md §6](workflow/08-retro-node-and-pr.md#6-pr-描述模板决策溯源) |

---

## 4. Hook 设计

> ✅ **状态更新（2026-05-19，backlog L CLOSED）**：hook 已落地——`.claude/settings.json` 现有完整 hooks 段（PreToolUse / TaskCompleted / UserPromptSubmit / SessionStart，G3 由 b204acf + 80cb737 + 1ad493f 完成）。以下为 2026-05-14 落地前的时点记录，保留原文。
>
> ⚠️ **原状态（2026-05-14 verified，已过期）**：本节描述的 3 个 hook 在 `.claude/settings.json` 中 **0 落地**。
>
> A6.1.1 节点收口 cold review 触发后 2 步实证：
> - `.claude/settings.json` hooks 段为空（40 行只含 permissions）
> - 主 Claude 全节点 0 次 Read 任何 `.claude/skills/<name>/SKILL.md`
> - 9 SKILL.md 中 7 个普通 skill 节点期 0 触发；仅 `pitfall-scout`（subagent 化 via Task tool）100% 触发
>
> 实际行为：Skill 触发依赖主 Claude 的语义匹配 + 主 Claude 自觉，**非 hook 强制注入**。
>
> [Backlog L](../governance/backlog.md#l-hook-配置落地--closed-2026-05-19)（✅ 已 CLOSED 2026-05-19）跟踪本节实际落地工作。本次 skill-system-refactor 拆 3 个 goal：
>
> - G1（本 PR）：XML schema 迁移到 workflow 子文档 + skill-design.md 缩水
> - G2：7 个 SKILL.md 标 deprecated + `.claude/skills/` 加 README
> - G3：CLAUDE.md + hook + backlog/observations 登记
>
> **G3 已于 2026-05-19 完成（backlog L CLOSED），hook 机制已实际生效**；本节其余内容为落地前设计记录。

### 4.1 Hook 总览（设计意图）

| Hook | 事件点 | 触发的 skill | 注入内容 |
|---|---|---|---|
| pre-tool-use | 工具调用前 | （无，直接阻塞） | 检查目标路径是否触及 [CLAUDE.md](../../CLAUDE.md) 红线 |
| post-goal | goal 完成标记后 | 提醒主 Claude 读 [workflow/05-brake-self-check.md §2.7](workflow/05-brake-self-check.md#27-刹车自检8-问) + [workflow/07-retro-goal.md §2.10](workflow/07-retro-goal.md#210-goal-级-retro按需) | "Goal completed. Run brake-self-check; evaluate retrospective-goal trigger." |
| pre-PR | `gh pr create` 命令调用前 | 提醒主 Claude 读 [workflow/08-retro-node-and-pr.md §2.11](workflow/08-retro-node-and-pr.md#211-节点级复盘--pr-收口) | "Node closure detected. MUST run retrospective-node before opening PR." |

### 4.2 各 hook 设计意图（已落地，2026-05-19，backlog L CLOSED）

- **pre-tool-use**：每次工具调用前检查路径是否触及 [CLAUDE.md](../../CLAUDE.md) 红线（`.env` / 生产 DB / repo settings）；触及 → 阻塞 + 提示停下问用户
- **post-goal**：goal 完成标记后注入提醒指向 [workflow/05-brake-self-check.md §2.7](workflow/05-brake-self-check.md#27-刹车自检8-问) + [workflow/07-retro-goal.md §2.10.1](workflow/07-retro-goal.md#2101-触发条件6-条触发即跑-retro)（具体 marker 待 G3 决定）
- **pre-PR**：`gh pr create` 命令前检查是否已跑 retrospective-node 流程；没跑 → 阻塞 + 要求按 [workflow/08-retro-node-and-pr.md §2.11.3](workflow/08-retro-node-and-pr.md#2113-复盘强制度) 跑

### 4.3 subagent 化 skill 不需要 hook

`pitfall-scout` 由主流程编排（节点起步前主 Claude 主动派 Task tool）；`verification-report` 由稀疏事件触发（最后一个节点 PR 合并 + 子阶段标 ✅，主 Claude 主动识别）。Hook 配置冗余。

### 4.4 Hook 实现注意事项

- 具体配置语法依赖 Claude Code 版本，本节只定义事件点 + 作用，不写具体 settings.json
- 实现时指向 workflow 子文档，不指向 deprecated SKILL.md
- Hook 不能替代 workflow 子文档内容，只触发主 Claude Read

---

## 5. 文件组织

### 5.1 当前生效 skill 目录（2 个 subagent）

```
.claude/skills/
  pitfall-scout/SKILL.md          # subagent 化（生效）
  verification-report/SKILL.md    # subagent 化（生效）
```

**subagent 化 skill 在 SKILL.md frontmatter 标注**：

```yaml
---
name: pitfall-scout
description: ...
execution_mode: subagent  # 标识此 skill 由 subagent 执行
---
```

主对话 Claude 看到 `execution_mode: subagent` 时，通过 Task tool 派 subagent 而非自己执行。

### 5.2 已 deprecated skill 目录（7 个）

```
.claude/skills/
  risk-judgment/SKILL.md          # deprecated，详细规则在 workflow/01-task-entry.md §2.2
  goal-decomposition/SKILL.md     # deprecated，详细规则在 workflow/03-decomposition.md §2.4
  brake-self-check/SKILL.md       # deprecated，详细规则在 workflow/05-brake-self-check.md §2.7
  dod-checklist/SKILL.md          # deprecated，详细规则在 workflow/06-dod-and-evidence.md §2.8
  retrospective-goal/SKILL.md     # deprecated，详细规则在 workflow/07-retro-goal.md §2.10
  retrospective-node/SKILL.md     # deprecated，详细规则在 workflow/08-retro-node-and-pr.md §2.11
  pr-template/SKILL.md            # deprecated，详细规则在 workflow/08-retro-node-and-pr.md §6
```

**deprecated SKILL.md 文件保留为参考文档**，G2 范围将在每个 SKILL.md 顶部加 deprecated banner。

### 5.3 关联文件

- `docs/plans/<node-id>-decomposition.md`：goal-decomposition 流程产物（[workflow/03-decomposition.md §2.4.4](workflow/03-decomposition.md#244-拆解产物落地)）
- `docs/retro/S2/<node-id>_<YYYY-MM-DD>.md`：retrospective-node 流程产物（[workflow/08-retro-node-and-pr.md §2.11.2](workflow/08-retro-node-and-pr.md#2112-节点级复盘的产物)）
- `docs/observations/should_update_observations.md`：retrospective-goal 的 observe 累积（[workflow/07-retro-goal.md §2.10.6](workflow/07-retro-goal.md#2106-observe-累积出口)）
- `docs/observations/{sN}-verification-report-<date>.md`：verification-report 流程产物（§3.2 / [workflow/10-verification-report.md §4.3](workflow/10-verification-report.md#43-落地路径)）
- [`docs/governance/workflow/09-known-pitfalls.md`](workflow/09-known-pitfalls.md) §3：retrospective-goal 的 must_update 落盘目标

---

## 6. 跨 skill 一致性规则

### 6.1 XML 标签命名

- 根标签：snake_case + 单数（`<retro_goal>` / `<retro_node>` / `<goal>` / `<pitfall_alerts>` / `<verification_report>`）
- 子标签：snake_case
- 属性：snake_case
- 不用 camelCase / kebab-case

### 6.2 引用 workflow.md 的格式

统一写法：`[docs/governance/workflow/0X-name.md §X.Y](workflow/0X-name.md#xy)`

- 锚点用小写 + 短横线（GitHub 默认）
- 不缩写"§"为"sec." / "section"

### 6.3 时间戳格式

- 统一 ISO 8601：`2026-05-13T14:32:00Z`
- 日期（无时间）：`2026-05-13`
- 不用 `2026/05/13` / `May 13, 2026`

### 6.4 节点 ID 格式

- S2todo 节点：`A6.1.2` / `P4.B.4` / `FM-3p.1` 等
- Goal sub-id：`<节点 ID>.<sub-id>`，如 `A6.1.2.1` / `A6.1.2.2`
- 不用 `A-6.1.2` / `a6.1.2`

### 6.5 失败处理风格

所有 skill 失败时输出：

```
status: fail
reason: <一句话>
current_state: <当前已完成什么 / 已产出什么>
suggested_next: <下一步建议>
need_user_judgment: true|false
```

### 6.6 数据传递

- skill 之间通过结构化 XML（workflow 子文档 + 本文件 §3 定义的输出 schema）传递
- 不靠 chat 上下文传递（下游 skill 不假设上游的 chat 输出格式）
- skill 输出 XML 后 Claude 主流程可加自然语言解释，但**XML 是真值**

### 6.7 修改本文件的规则

- 修改本文件 = 治理设计层变更
- commit prefix：`docs(baseline):` + 显式 `baseline:` scope
- 重大调整（改 subagent skill 接口契约 / 加新 skill / 退役 skill）需 PR + 用户确认
- 修改本文件**必须同步检查 workflow 子文档**是否还匹配（schema 字段一致性）

### 6.8 SKILL.md 实现的不变量

实现生效 skill（2 个 subagent）的 SKILL.md 时，以下不变量必须满足：

1. SKILL.md frontmatter 的 `description` 字段简洁清晰（< 200 字符），便于 Claude 语义匹配
2. SKILL.md 正文不重复 workflow.md 的规则文本，只引用子文档章节
3. SKILL.md 必须包含本文件 §3 对应的输出 schema（实现层必需）
4. SKILL.md 必须包含本文件 §3 对应的"边界"列表（防 skill 越界）
5. SKILL.md 失败处理段必须符合本文件 §6.5 风格
6. SKILL.md 之间不互相引用（只通过 XML 接口协作）
7. subagent 化 skill 必须在 frontmatter 标 `execution_mode: subagent`

**deprecated SKILL.md 不再要求遵守这些不变量**（G2 范围将正式标 deprecated）。

### 6.9 subagent 化 skill 的额外约束

subagent 化 skill（`pitfall-scout` / `verification-report`）必须遵守：

1. **输出必须是结构化 XML**：不允许自然语言报告（主对话无法可靠解析）
2. **输出长度 ≤ 200 行**：超过 = 应该落盘到文件，主对话只接 summary
3. **不修改任何文件**：subagent 只读 + 产出 XML；实际落盘由主对话 Claude 用 `docs(baseline):` / `docs(retro):` commit 完成
4. **无状态**：每次调用重新读输入，不依赖前次 subagent 的 context
5. **失败处理**：subagent 失败 → 输出 `<status>fail</status>` + 原因 → 主对话决定 retry / 升级用户

---

## 7. 设计文档维护协议

### 7.1 修改频率

- 本文件**应稳定**：每次修改都意味着 subagent skill 的 SKILL.md / workflow 子文档可能要同步改
- 修改触发：
  - 新增 / 退役 subagent skill
  - 改 subagent skill 接口契约（输入 / 输出 XML）
  - 改协作流（谁调用谁）
  - 改 hook 设计（事件点 / 注入内容）
  - 重大调整 deprecated skill 的恢复 / 物理删除

### 7.2 不应触发本文件修改的场景

- SKILL.md 内部 prompt 措辞调整
- SKILL.md 内部例子增减
- SKILL.md 内部 frontmatter description 优化
- workflow 子文档 schema 字段细节调整（应同步本文件 §3 schema 但不一定全文重写）

### 7.3 和 workflow.md 的关系

- **workflow.md 子文档 = 规则真值源 + 主 Claude 执行手册**（主 Claude 实际读的）
- 本文件 = subagent 化 skill 设计真值源 + 跨 skill 元规则
- workflow.md 改规则 → 本文件检查对应 subagent skill 是否需调
- 本文件改 subagent skill → workflow.md 同步检查 schema 字段（[workflow/09-known-pitfalls.md §3.11](workflow/09-known-pitfalls.md#311-pitfall-scout-subagent-工作方式) / [workflow/10-verification-report.md §4.6](workflow/10-verification-report.md#46-verification-report-subagent-工作方式)）

### 7.4 迭代历史

- **2026-05-13**：初版（7 skill + 3 hook + 6 一致性规则）
- **2026-05-14 (am)**：扩展至 9 skill（+ `pitfall-scout`、`verification-report`），引入 subagent 化机制
- **2026-05-14 (pm) - skill-system-refactor**：A6.1.1 实证发现 7 个非 subagent skill 节点期 0 触发。
  - **G1**（本次提交）：XML schema 迁移到 workflow 子文档（5 个 schema 进 5 个文件）；本文件缩水（1244 → ~500 行）：删除 deprecated 7 skill 的详细设计 §3.{1,3,4,5,6,7,9}，保留 §3.{2,8} 完整；§4 hook 设计加 ⚠️ 落地警告 banner；§1 全景图改写为"2 生效 + 7 deprecated"；定位改为"subagent skill 设计 + 元规则真值源"
  - **G2**（待做）：7 个 deprecated SKILL.md 标 deprecated banner（不删除）；`.claude/skills/` 加 README 说明
  - **G3**（当时待做；✅ 已于 2026-05-19 落地，backlog L CLOSED，b204acf + 80cb737 + 1ad493f）：CLAUDE.md 删 9 skill 索引改为指向 workflow + 2 subagent；`.claude/settings.json` 配置生效 hook；backlog L + observations 登记
- 历次重大调整通过 `docs(baseline):` commit 记录
