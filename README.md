# subagent-workflow-baseline

Claude Code 自主推进任务的过程层基准（10 步主链路 + 刹车自检 + DoD + retro），从 `subagent-for-investment` 仓库独立打包。

## 内容

- [workflow.md](workflow.md) — 总纲：适用条件、Reading Order、10 步主链路流程图、维护协议
- [workflow/](workflow/) — 11 份子文档（按任务阶段切片，索引见 [workflow/README.md](workflow/README.md)）

| # | 子文档 | 阶段 |
|---|---|---|
| 01 | [task-entry](workflow/01-task-entry.md) | 任务进入 + 风险判定 |
| 02 | [pre-flight](workflow/02-pre-flight.md) | 节点切入 5 问 |
| 03 | [decomposition](workflow/03-decomposition.md) | 拆小任务 + `<goal>` XML |
| 04 | [goal-execution](workflow/04-goal-execution.md) | Goal 执行 + 自验 |
| 05 | [brake-self-check](workflow/05-brake-self-check.md) | 刹车自检 8 问 |
| 06 | [dod-and-evidence](workflow/06-dod-and-evidence.md) | DoD 四步 + evidence |
| 07 | [retro-goal](workflow/07-retro-goal.md) | Goal 级 retro 三档 |
| 08 | [retro-node-and-pr](workflow/08-retro-node-and-pr.md) | 节点复盘 + PR 模板 |
| 09 | [known-pitfalls](workflow/09-known-pitfalls.md) | 已知坑表 |
| 10 | [verification-report](workflow/10-verification-report.md) | 子阶段交接审视 |
| 11 | [cadence](workflow/11-cadence.md) | 节奏 + 并行限制 |

## 来源

- 源仓库：`JunoChenZt/subagent-for-investment`（private），路径 `docs/governance/workflow.md` + `docs/governance/workflow/`
- 快照：main `ad07047a`，2026-09-29
- 正文**逐字保留**，未做任何改写

## 已知限制

正文中指向源仓库其他文件的链接（`CLAUDE.md`、`docs/roadmap/S2.md`、`docs/governance/skill-design.md`、`git-workflow.md`、observations / retro / plans 等）在本仓库内**无法解析**。总纲与 11 份子文档之间的互链完整可用。
