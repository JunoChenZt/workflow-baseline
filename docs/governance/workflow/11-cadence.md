# 11 Cadence — 推进节奏

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 骨架: [core/07 §3](../../../core/07-pr-and-handoff.md) —— 规则本体以骨架为准，本文件是实例层（含项目参数与历史证据）
> 关联子文档: [docs/governance/workflow/03-decomposition.md](03-decomposition.md) / [docs/governance/workflow/08-retro-node-and-pr.md](08-retro-node-and-pr.md) / [docs/governance/workflow/10-verification-report.md](10-verification-report.md)
> 关联 skill: (主流程参考)

## 何时读这份文档

- 节点粒度 / 单 goal 时长拿不准 → 读 §5.1 / §5.3
- 想开第 4 个并行节点工作分支 → 读 §5.2 WIP limit + §5.2.2 调整机制
- 节点 PR 创建后想立刻推下一节点 → 读 §5.4

## 概览

§5.1 节奏总览（节点 1-3 天 / `/goal` 单任务 / commit / PR / 合并 / gate 启动）+ §5.2 并行 WIP limit 3 + 调整机制 + §5.3 单 goal 时间预算 + §5.4 节点完成到下一节点起步间隔。

---

## 5. 推进节奏

### 5.1 节奏总览

| 单位 | 节奏 |
|---|---|
| 节点粒度 | 1-3 天 = 1 节点。超过 → 拆子节点（在 S2todo 加 .x.y 子任务，按 [03-decomposition.md §2.4.2](03-decomposition.md#242-小任务拆解标准) 标准）|
| `/goal` 粒度 | 单个 `/goal` 内只动 1 个小任务；不混阶段、模块、风险等级 |
| commit 节奏 | 节点内可多 commit；节点 done 后 squash merge 自动产生 main 上的 1 个 commit；S2todo 状态更新单独 1 个 `docs(todo):` commit（按 [docs/governance/git-workflow.md §2.6](../git-workflow.md#26-commit-节奏)） |
| PR 节奏 | 每个节点收口 = 1 PR；PR 描述作为决策溯源（详 [08-retro-node-and-pr.md §6](08-retro-node-and-pr.md#6-pr-描述模板决策溯源)）|
| 合并条件 | DoD 4 步全过 + [08-retro-node-and-pr.md §2.11](08-retro-node-and-pr.md#211-节点级复盘--pr-收口) 节点级复盘完成 |
| gate 启动 | S2.1 完整 done → 启动 PR-8c observation gate（14d / ≥ 30 runs）|

### 5.2 并行节点 WIP limit

**默认并行节点数上限：≤ 3 个节点工作分支同时 open**。

**该值是初始 WIP limit，不代表技术上最多只能并行 3 个**。

#### 5.2.1 不允许并行的场景

- 两节点撞同一文件
- 两节点依赖关系串行
- 两节点都是高风险

#### 5.2.2 观察 + 调整机制

节点复盘 [08-retro-node-and-pr.md §2.11](08-retro-node-and-pr.md#211-节点级复盘--pr-收口) 时观察以下 5 个维度：

1. **PR review 是否积压**：用户 review 跟不上 Claude 推进速度
2. **ledger 状态冲突**：S2todo 状态更新出现冲突或混乱
3. **重复修同类问题**：多个并行节点修同一类 bug，应该合并而非并行
4. **baseline / skill 改动冲突**：多个 PR 同时修 baseline 或 skill
5. **evidence 路径混乱**：observation / retro 文件命名出现冲突

**调整规则**：

- 连续 **2 个子阶段无上述问题** → 可议提高到 4-5（需用户确认）
- 出现 ledger / PR / evidence 混乱 → **降到 2**（自动调整，不需用户确认）
- 调整结果写入下次 [10-verification-report.md §4](10-verification-report.md#4-verification-report-触发点) Verification Report

**强约束**：超过 3 个并行 → 需要人工确认。

### 5.3 单 goal 的时间预算

- **小 goal**：≤ 30 分钟（含 DoD + evidence）
- **中 goal**：30 - 90 分钟
- **大 goal**：> 90 分钟 → 应该再拆（[03-decomposition.md §2.4.6](03-decomposition.md#246-节点--小任务)）

### 5.4 节点完成到下一节点起步的间隔

- 异步 PR 模式下，节点 PR 创建后**立即继续**下一节点
- 但需先确认下一节点的 [02-pre-flight.md §2.3](02-pre-flight.md#23-节点切入-5-问pre-flight-check) 第 1 问"依赖"已满足（依赖的上一节点已合 main，或 main 上已有等价改动）
- 依赖未满足 → 切换到无依赖节点；都需等待 → 停下问

---

## Cross-references

**上游（我引用谁）**：

- [03-decomposition.md](03-decomposition.md) — §2.4.2 拆解标准 / §2.4.6 节点 ≠ 小任务
- [02-pre-flight.md](02-pre-flight.md) — §2.3 第 1 问依赖确认
- [08-retro-node-and-pr.md](08-retro-node-and-pr.md) — §2.11 节点级复盘（WIP 5 维度观察入口） / §6 PR 模板
- [docs/governance/git-workflow.md](../git-workflow.md) — §2.6 commit 节奏

**下游（谁引用我）**：

- [10-verification-report.md](10-verification-report.md) — §4.2 第 4 条审视 §5.2 并行节点数
