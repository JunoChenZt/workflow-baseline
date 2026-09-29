# 07 Retro Goal — Goal 级 retro

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 骨架: [core/06 §1](../../../core/06-retro.md) —— 规则本体以骨架为准，本文件是实例层（含项目参数与历史证据）
> 关联子文档: [docs/governance/workflow/06-dod-and-evidence.md](06-dod-and-evidence.md) / [docs/governance/workflow/08-retro-node-and-pr.md](08-retro-node-and-pr.md) / [docs/governance/workflow/09-known-pitfalls.md](09-known-pitfalls.md)
> 关联 skill: `retrospective-goal`（已 deprecated；详细规则现在本文件 §2.10，设计历史见 [docs/governance/skill-design.md §3.3](../skill-design.md#33-已-deprecated-skill7-个详细设计已迁至-workflow-子文档)）

## 何时读这份文档

[06-dod-and-evidence.md §2.9](06-dod-and-evidence.md#29-evidence-收集) evidence 收集完成后。6 条触发条件任一为真才跑 retro；否则 skip。产出 must_update / should_update / observe 三档。

## 概览

- §2.10.1 触发条件 6 条（命中任一才跑）
- §2.10.2 三档输出定义（must_update / should_update / observe）
- §2.10.3 `<retro_goal>` XML 结构
- §2.10.4 数量门槛（默认 ≤ 2 must_update / retro）
- §2.10.5 should_update 分流表
- §2.10.6 observe 累积出口（连续 ≥ 3 次同类 → 升级 should_update）
- §2.10.7 must_update 落盘
- §2.10.8 输出 → 节点全部 done 判定

---

## 2.10 goal 级 retro（按需）

**时机**：evidence 收集完成后。

**关联 skill**：`retrospective-goal`（详见 SKILL.md）

### 2.10.1 触发条件（6 条触发即跑 retro）

Run retro if ANY of the 6 conditions hold:

1. Goal had rework (DoD 失败重做)
2. Goal triggered any [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) brake (8 问命中或 [04-goal-execution.md §2.5.3](04-goal-execution.md#253-执行中的硬边界即时停) 硬边界即停)
3. Goal exposed an unexpected pitfall in schema / prompt / fallback / archive replay / 路由
4. Goal modified a corner case, changed a DONE node's contract, or added a deferred item
5. Goal needed ≥ 3 DoD retries
6. Goal belongs to a high-risk node (per [01-task-entry.md §2.2](01-task-entry.md#22-风险判定5-条触发即高风险))

If NONE hold → **skip retro**，直接进 "节点全部 done?" 判定。

### 2.10.2 Retro 三档输出

每个 retro 输出分为三档（**must_update / should_update / observe**），分别承担不同责任：

| 档位 | 定义 | 处置 |
|---|---|---|
| **must_update** | 不改会导致未来重复犯错或违反红线 | 立即落盘到 [09-known-pitfalls.md §3](09-known-pitfalls.md#3-已知坑--防回归-checklist) 已知坑 / [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) 刹车条件 / SKILL.md |
| **should_update** | 值得改，但不阻塞当前节点 | 按 §2.10.5 分流表处置 |
| **observe** | 先观察，不立即改规则；数据不足 | 进入 `docs/observations/should_update_observations.md`；§2.10.6 累积出口 |

### 2.10.3 Retro 产物结构

输出**结构化 XML 块**（默认 inline 在 chat，特定情况落盘）：

```xml
<retro_goal id="<goal-id>" timestamp="<ISO 8601>">
  <triggered_by>
    <!-- 列出 §2.10.1 6 条触发条件中本 retro 命中的条目 -->
    <condition n="1">DoD 失败重做 2 次</condition>
    <condition n="3">暴露 schema 未预料行为</condition>
  </triggered_by>

  <tldr>
    2-3 sentences: what was attempted, what was achieved,
    the single most important takeaway.
  </tldr>

  <journey>
    <phase name="<descriptive-name>">
      What happened, what was tried, what worked / what didn't.
      Include actual error messages or paths to evidence when relevant.
    </phase>
    <!-- repeat 1-3 phases -->
  </journey>

  <mistakes>
    <mistake>
      <what_went_wrong>...</what_went_wrong>
      <fix_or_lesson>...</fix_or_lesson>
    </mistake>
  </mistakes>

  <techniques>
    <technique>
      <pattern>...</pattern>
      <when_to_apply>...</when_to_apply>
    </technique>
  </techniques>

  <proposals>
    <!-- 三档,任一档可为空 -->
    <must_update target="<workflow 子文档 §X.Y 或 SKILL.md path>">
      <rule>Hard rule that affects future behavior.</rule>
      <rationale>...</rationale>
    </must_update>

    <should_update type="correctness|baseline|threshold|red-line">
      <suggestion>...</suggestion>
      <rationale>按 §2.10.5 分流表归类并标 type。</rationale>
    </should_update>

    <observe>
      <signal>...</signal>
      <why_insufficient>累积 ≥ 3 次同类则升级 should_update (§2.10.6)。</why_insufficient>
    </observe>
  </proposals>

  <quality_self_check>
    <!-- §2.10.4 自检：retro 是否本不该跑 -->
    <must_update_count>N</must_update_count>
    <is_trivial>true|false</is_trivial>
    <retro_should_have_been_skipped>true|false</retro_should_have_been_skipped>
  </quality_self_check>
</retro_goal>
```

### 2.10.4 Retro 质量门槛（数量约束）

- **每个 retro 默认最多提出 1-2 个 must_update**。该限制是**初始经验值**，用于防止流程改进噪音过载
- **must_update = 0 是正常现象**，不强求产出沉淀（说明当前 skills / baseline 已覆盖常见问题）
- **若连续多个节点出现 must_update 长期 ≥ 2**：应在节点复盘中检查 retro 触发条件是否过松、should_update 是否可降级为 observe
- **若连续多个节点 must_update = 0**：说明当前规则已稳，属正常现象，不需调整
- **单次确有 > 2 个 must_update**：必须说明为什么这些更新都属于阻塞级流程缺陷，而非普通优化建议
- **must_update 必须可执行**：写"应该改进 prompt 设计哲学"不算；写"§3.2 加一条 'A1.2 实施前 grill A/B/C/D/F 类完整规则'"算

**这条是数量门槛，不是绝对真理**。它是初始 heuristic，子阶段复盘时可调。

### 2.10.5 should_update 分流表

`should_update` **不能默认全部混进当前节点 PR**。按改动性质分类处置：

| should_update 类型 | 是否进当前节点 PR | 处理方式 | 例子 |
|---|---|---|---|
| **correctness / schema / test 必需** | ✅ 是 | 纳入节点 PR | 当前节点暴露了 schema validator 缺口；测试 fixture 需同步；实现必须补 fallback guard |
| **当前节点实现直接依赖** | ✅ 是 | 纳入节点 PR | 当前节点的代码逻辑直接依赖这个 should_update 才能正确 |
| **baseline / skill / template / workflow** | ❌ 默认否 | 单独 governance PR 或 main 直接 commit（按 [docs/governance/git-workflow.md §1.3](../git-workflow.md#13) 例外） | 修改本文件；修改 workflow skill；修改 PR template |
| **经验值调整 / 策略阈值** | ❌ 否 | 进入 observation，阶段复盘拍板 | 并行节点数从 3 调到 5；must_update 数量门槛调整 |
| **涉及红线 / 权限 / 生产** | ❌ 否 | 人工确认后另行处理 | 任何触及 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) Q1 / Q3 / Q4 的"流程改进"必须人工确认 |

**分流原则**：

- 默认 conservative：拿不准属于哪类 → 进 governance PR 或 observe，不混进节点 PR
- 一个 PR 应该只有一个"性质"：要么是节点功能，要么是流程治理，不混搭

### 2.10.6 observe 累积出口

`observe` 不是黑洞，有明确出口机制：

1. **登记位置**：`docs/observations/should_update_observations.md`
2. **登记内容**：
   - goal-id + timestamp
   - observed signal（观察到什么）
   - 当前数据为何不足以升级为 should_update
3. **累积升级条件**：**连续 ≥ 3 次同类 observation** → 升级为 should_update，重新走 §2.10.5 分流表
4. **审视时机**：
   - 子阶段交接（[10-verification-report.md §4](10-verification-report.md#4-verification-report-触发点) Verification Report 触发）必看一遍
   - 节点级复盘 [08-retro-node-and-pr.md §2.11](08-retro-node-and-pr.md#211-节点级复盘--pr-收口) q5_sedimentation 时也可触发审视

**同类 observation 的判定**：

- 相同的 target（同一文件 / 同一规则 / 同一阈值）
- 相同的 signal type（如"延迟超预算"、"fallback ratio 上升"）
- 不同 goal 但表现相同

### 2.10.7 must_update 的落盘

- **必须落盘**到对应位置（[09-known-pitfalls.md §3](09-known-pitfalls.md#3-已知坑--防回归-checklist) 已知坑、[05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) 刹车条件、新 SKILL.md）
- 落盘走 [docs/governance/git-workflow.md §1.3](../git-workflow.md#13) 例外（main 直接 commit）
- commit prefix: `docs(baseline):` 或 `docs(retro):`

### 2.10.8 输出

- `<retro_goal>` XML 块（inline）
- 已落盘的 must_update 文件路径列表
- 待 [08-retro-node-and-pr.md §2.11](08-retro-node-and-pr.md#211-节点级复盘--pr-收口) 处置的 should_update 列表（按 §2.10.5 分类）
- observe 登记的条数 + 累积升级触发情况

进入 "节点全部 done?" 判定 → 否回 [04-goal-execution.md §2.5](04-goal-execution.md#25-单个-goal-执行)；是进 [08-retro-node-and-pr.md §2.11](08-retro-node-and-pr.md#211-节点级复盘--pr-收口)。

---

## Cross-references

**上游（我引用谁）**：

- [06-dod-and-evidence.md](06-dod-and-evidence.md) — evidence summary（消费输入）
- [01-task-entry.md](01-task-entry.md) — 第 6 条触发条件复用 §2.2 风险判定
- [05-brake-self-check.md](05-brake-self-check.md) — 第 2 条触发条件复用 §2.7 8 问 / §2.5.3 硬边界

**下游（谁引用我）**：

- [09-known-pitfalls.md](09-known-pitfalls.md) — must_update 落盘到 §3
- [08-retro-node-and-pr.md](08-retro-node-and-pr.md) — should_update 进 q5_sedimentation；retro 三档汇总
- [10-verification-report.md](10-verification-report.md) — observe 累积审视入口
- [docs/governance/git-workflow.md](../git-workflow.md) — must_update 落盘走 §1.3 例外
- `retrospective-goal` SKILL — 消费 §2.10 全节
