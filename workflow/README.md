# Workflow 子文档导航

本目录是 [docs/governance/workflow.md](../workflow.md) 的分层切片。主文档保留 §0 适用前置 + §0.1 Reading Order + §1 主链路总览 + §7 维护协议；详细规则按主题分在 11 个子文档里。

## 子文档清单

| 文件 | 内容 | 关联 skill |
|---|---|---|
| [01-task-entry.md](01-task-entry.md) | 大任务进入 + 风险判定 (§2.1 + §2.2) | risk-judgment |
| [02-pre-flight.md](02-pre-flight.md) | 节点切入 5 问 (§2.3) | pitfall-scout / goal-decomposition |
| [03-decomposition.md](03-decomposition.md) | 拆小任务 + `<goal>` XML (§2.4) | goal-decomposition |
| [04-goal-execution.md](04-goal-execution.md) | 单 goal 执行 + 自验 (§2.5 + §2.6) | (主流程) |
| [05-brake-self-check.md](05-brake-self-check.md) | 刹车自检 8 问 (§2.7) | brake-self-check |
| [06-dod-and-evidence.md](06-dod-and-evidence.md) | DoD 四步 + evidence (§2.8 + §2.9) | dod-checklist |
| [07-retro-goal.md](07-retro-goal.md) | Goal 级 retro (§2.10) | retrospective-goal |
| [08-retro-node-and-pr.md](08-retro-node-and-pr.md) | 节点级复盘 + PR 模板 (§2.11 + §6) | retrospective-node / pr-template |
| [09-known-pitfalls.md](09-known-pitfalls.md) | 已知坑 + 维护协议 (§3) — **不再细拆**（subagent 要读全表） | pitfall-scout / verification-report |
| [10-verification-report.md](10-verification-report.md) | Verification Report (§4) | verification-report |
| [11-cadence.md](11-cadence.md) | 推进节奏 (§5) | (主流程参考) |

## 怎么读这些文档

按主文档 [docs/governance/workflow.md §0.1](../workflow.md#01-reading-order) 的 Reading Order 表定位当前阶段读哪一份；不要从头到尾读完——会浪费 context。

## 9 个 workflow skill 怎么用这些子文档

skill 体系（skill-system-refactor，2026-05-14）重构后：

- **7 个非 subagent skill 已 deprecated**：详细规则现在 workflow 子文档（见上表"关联 skill"列），主 Claude 直接读子文档执行，不再依赖 SKILL.md 中转
- **2 个 subagent 化 skill 生效**：`pitfall-scout`（详见 [09-known-pitfalls.md §3.11](09-known-pitfalls.md#311-pitfall-scout-subagent-工作方式)）/ `verification-report`（详见 [10-verification-report.md §4.6](10-verification-report.md#46-verification-report-subagent-工作方式)）
- skill 设计真值源 + 一致性元规则见 [docs/governance/skill-design.md](../skill-design.md)

## 修改规则

修改任一子文档 = 修改 workflow 基准，按 [docs/governance/workflow.md §7](../workflow.md#7-基准维护协议) 维护协议走，必要时同步 SKILL.md。
