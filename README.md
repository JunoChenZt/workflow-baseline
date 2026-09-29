# subagent-workflow-baseline

Claude Code 自主推进任务的过程层基准（10 步主链路 + 刹车自检 + DoD + retro），从 `subagent-for-investment` 仓库独立打包。

## 入口

- [docs/governance/workflow.md](docs/governance/workflow.md) — 总纲：适用条件、Reading Order、10 步主链路流程图、维护协议
- [docs/governance/workflow/](docs/governance/workflow/) — 11 份子文档（按任务阶段切片，索引见 [workflow/README.md](docs/governance/workflow/README.md)）

| # | 子文档 | 阶段 |
|---|---|---|
| 01 | [task-entry](docs/governance/workflow/01-task-entry.md) | 任务进入 + 风险判定 |
| 02 | [pre-flight](docs/governance/workflow/02-pre-flight.md) | 节点切入 5 问 |
| 03 | [decomposition](docs/governance/workflow/03-decomposition.md) | 拆小任务 + `<goal>` XML |
| 04 | [goal-execution](docs/governance/workflow/04-goal-execution.md) | Goal 执行 + 自验 |
| 05 | [brake-self-check](docs/governance/workflow/05-brake-self-check.md) | 刹车自检 8 问 |
| 06 | [dod-and-evidence](docs/governance/workflow/06-dod-and-evidence.md) | DoD 四步 + evidence |
| 07 | [retro-goal](docs/governance/workflow/07-retro-goal.md) | Goal 级 retro 三档 |
| 08 | [retro-node-and-pr](docs/governance/workflow/08-retro-node-and-pr.md) | 节点复盘 + PR 模板 |
| 09 | [known-pitfalls](docs/governance/workflow/09-known-pitfalls.md) | 已知坑表 |
| 10 | [verification-report](docs/governance/workflow/10-verification-report.md) | 子阶段交接审视 |
| 11 | [cadence](docs/governance/workflow/11-cadence.md) | 节奏 + 并行限制 |

## 目录结构

与源仓库**同构**，这样文档里的相对链接原样可用。除上面 12 份工作流文档外，其余 51 个文件都是它们**直接链接到**的引用对象，按原路径放置：

- `CLAUDE.md` — 顶层原则 / 红线 / workflow 入口
- `docs/governance/` — git-workflow、skill-design、backlog、e2e 验收标准与质检门、未验前提协议等
- `docs/roadmap/` — S2 任务清单、roadmap v3.4
- `docs/observations/` / `docs/retro/S2/` / `docs/plans/` — 坑表与 retro 引用的观察记录、节点复盘、拆解文档
- `docs/infrastructure/` / `docs/pipeline/` / `docs/archive/` — 被引用的基础设施与流水线文档
- `src/` / `scripts/` / `tests/` — 被引用的代码文件（仅供阅读定位，**不构成可运行工程**）

## 来源

- 源仓库：`JunoChenZt/subagent-for-investment`（private）
- 快照：main `ad07047a`，2026-09-29
- 所有文件**逐字保留**，未做任何改写

## 已知限制

- **一级链接全通**：12 份工作流文档内的每一条相对链接都已核过，在本仓库内可解析。
- **二级链接不保证**：被引用文件（如 S2.md、backlog.md、retro 记录）自己再往外指的链接，目标未打包，可能点不开。
- 根目录的 `CLAUDE.md` 是源仓库的项目指令快照。在本仓库里用 Claude Code 时它会被当作项目指令读取，其中的分支约定 / 红线针对源仓库，不一定适用于此处。
