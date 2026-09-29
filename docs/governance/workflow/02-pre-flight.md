# 02 Pre-flight — 节点切入 5 问

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 关联子文档: [docs/governance/workflow/01-task-entry.md](01-task-entry.md) / [docs/governance/workflow/03-decomposition.md](03-decomposition.md)
> 关联 skill: `pitfall-scout`（设计见 [docs/governance/skill-design.md §3.1](../skill-design.md#31-pitfall-scout)）/ `goal-decomposition`（已 deprecated；详细规则现在 [03-decomposition.md §2.4](03-decomposition.md#24-拆小任务)，设计历史见 [skill-design.md §3.3](../skill-design.md#33-已-deprecated-skill7-个详细设计已迁至-workflow-子文档)）

## 何时读这份文档

节点起步前的最后一次 pre-flight 检查。[01-task-entry.md](01-task-entry.md) 判定为大任务（不论高 / 低风险）之后，进入 [03-decomposition.md](03-decomposition.md) 拆解之前必读。

## 概览

进 5 问前先过**「顶层对齐」前置闸**（Read 父 / 顶层 task 定义，确认方向没跑偏，见 §2.3）。5 个问题逐一回答（每条 1-2 行）：依赖 / 并行 / 风险档位 / time budget / Fallback。答案作为 §2.4 拆解时 `<goal>` XML 的输入字段。任一问答不出 / 应对不清 → 停下问。

---

## 2.3 节点切入 5 问（pre-flight check）

**时机**：大任务进入 §2.4 拆解之前，节点起步的最后一次 pre-flight 检查。

**仅在 §2.1 判定为大任务时执行此节**。

**0. 顶层对齐（进 5 问前的前置闸）**：动手拆解前，先 Read 本节点的父 / 顶层 task 定义（[docs/roadmap/S2.md](../../roadmap/S2.md) 对应节点 + [docs/roadmap/roadmap-v3.4.md](../../roadmap/roadmap-v3.4.md) 相关段），确认拆解方向与顶层要求一致。**没读 → 先读再拆；方向不一致 → 停下问，别按自己的理解往下拆。** 顶层定义本身也是一种必须先验证的"前提"（与 [unverified-premise-protocol.md §4](../unverified-premise-protocol.md#4-与现有-workflow-的集成点) 提案同源 —— 那里的"验证事实前提"这里落成"验证顶层对齐"）。真值源可能在**未合分支**（handoff 点名的设计常在未合节点分支）→ `git branch -a` / `git ls-tree` 先查，别当"待建"跳过。**起因**：A6.1.2 全程未主动 Read 顶层定义、后期才发现方向偏差（backlog 条目 I 任务 2；O-A6.1.1-01「顶层定义也是一种实证」延伸）。

| # | 问题 | 失败应对 |
|---|---|---|
| 1 | **依赖**：上游节点（[docs/roadmap/S2.md](../../roadmap/S2.md) 串行约束）全部 ✅ DONE 了吗？ | 等上游 done 再开（除非可证明无依赖）|
| 2 | **并行块**：本节点能与哪些其他节点同时推？目前 main 上 / 其他节点工作分支 / 进行中的节点是否会撞同一文件？ | 撞文件 → 改串行；不撞 → 并行 |
| 3 | **风险层级（复用 §2.2 判定）**：高风险 → 需用户确认拆解 + PR 必走 review；触及 hard block / breaking → 高风险 gate（≥30 runs / 14d）| 标对 gate 档位 |
| 4 | **time budget**：本节点引入的延迟落入哪个 phase？是否符合 [docs/roadmap/S2.md §6.7](../../roadmap/S2.md) 预算？ | 超预算 → 重新评估或拆分 |
| 5 | **Fallback**：完全失败时 [docs/roadmap/S2.md §6](../../roadmap/S2.md) 哪条路径兜底？ | 没有就**先补 Fallback 再写主路径** |

**Claude 的动作**：

1. 5 问逐一回答（每条 1-2 行）
2. 答案进入 §2.4 拆解时作为 `<goal>` XML 的输入字段（`<dependencies>` / `<fallback>` 等）
3. 任一问答不出 / 应对不清 → 停下问

**输出**：5 问的回答清单，作为 §2.4 拆解的输入。

**和 [docs/governance/workflow/01-task-entry.md §2.2](01-task-entry.md#22-风险判定5-条触发即高风险) 风险判定的区别**：

- §2.2 风险判定 = 决定**走哪条流程**（高 / 低风险路径分叉）
- §2.3 节点切入 5 问 = **节点起步前的 checklist**（上游 / 并行 / 风险档位 / 预算 / Fallback）
- 5 问的第 3 问复用 §2.2 的结果，不重复判定

---

## Cross-references

**上游（我引用谁）**：

- [01-task-entry.md](01-task-entry.md) — 风险判定结果（第 3 问复用）
- [docs/roadmap/S2.md](../../roadmap/S2.md) — 节点依赖串行约束 + §6 Fallback 路径 + §6.7 time budget
- [docs/infrastructure/source-readiness-checklist.md](../../infrastructure/source-readiness-checklist.md) — 数据源变更/新增时的 production readiness checklist (A6.1.4 新增)

**下游（谁引用我）**：

- [03-decomposition.md](03-decomposition.md) — 5 问答案作为拆解输入
- `pitfall-scout` SKILL — 第 1 问"依赖"可辅助判定上游 done 状态
- `goal-decomposition` SKILL — 消费 5 问答案进入 `<pre_flight_answers>` 输入字段
