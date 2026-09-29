# workflow-baseline

让 AI 自主推进任务时「不越线、不盲跑、交付可核」的过程规则：10 步主链路 + 分档路由 + 刹车 8 问 + DoD 三态 + 三栏交付单 + 复盘。从 `subagent-for-investment` 仓库独立出来，2026-09-29 起独立演进。

## 自动检查与台账

| 文件 | 干什么 |
|---|---|
| [checks.md](checks.md) | 每道自动检查的登记：抓什么 / 「它会响」证明 / 误报预算 / 承重（WARN 试用为主） |
| [scripts/](scripts/) | `lint_links` 断链 · `lint_config_slots` 骨架槽位与泄漏 · `lint_pr_body` 交付单格式 · `tier_check` 档位对账（路由器第一版）· `metrics_report` 划算度报告；各带 `--self-test` |
| [metrics.md](metrics.md) | 规则命中台账（上次拦到东西的日期）+ PR 台账（档位 / 返工 / ⚪）；零命中 90 天进退役候选 |
| [.github/workflows/checks.yml](.github/workflows/checks.yml) | push / PR 跑自测 + 检查，秒级 |

## 三层结构

| 层 | 位置 | 放什么 | 谁用 |
|---|---|---|---|
| **骨架** | [core/](core/README.md) | 规则本体，零项目名词，参数写成 `{{key}}` | 任何项目 |
| **配置** | [project-config.md](project-config.md) | 所有 `{{key}}` 的取值（红线 / 敏感路径 / 档位阈值 / 验证命令 / 路径 / 节奏） | 每个项目改自己的 |
| **实例** | [docs/governance/workflow/](docs/governance/workflow/README.md) | 骨架在原项目上的展开：规则 + 参数 + 历史证据 + 坑表 + [完整案例](docs/governance/workflow/examples/walkthrough-cli-json-flag.md) | 原项目；别人当案例看 |

冲突时：规则以骨架为准，参数以配置为准。

## 怎么接入（三步）

1. 复制 `core/` 到你的仓库。
2. 复制 `project-config.md`，把「本项目值」列改成你的（红线、敏感路径、验证命令、目录）。
3. 把 [core/01 §0](core/01-entry-and-routing.md) 的接入片段贴进你的 `CLAUDE.md` / `AGENTS.md`。

想先看一遍「从指令到交付长什么样」：[完整案例](docs/governance/workflow/examples/walkthrough-cli-json-flag.md)。

## 实例层入口

- [docs/governance/workflow.md](docs/governance/workflow.md) — 总纲：适用条件、Reading Order、10 步主链路流程图、维护协议
- [docs/governance/workflow/](docs/governance/workflow/) — 11 份子文档（按任务阶段切片，索引见 [workflow/README.md](docs/governance/workflow/README.md)）

| # | 子文档 | 阶段 |
|---|---|---|
| 01 | [task-entry](docs/governance/workflow/01-task-entry.md) | 任务进入 + 风险判定 + 分档 S / M / L（只升不降） |
| 02 | [pre-flight](docs/governance/workflow/02-pre-flight.md) | 节点切入 5 问 |
| 03 | [decomposition](docs/governance/workflow/03-decomposition.md) | 拆小任务 + `<goal>` XML |
| 04 | [goal-execution](docs/governance/workflow/04-goal-execution.md) | Goal 执行 + 自验 |
| 05 | [brake-self-check](docs/governance/workflow/05-brake-self-check.md) | 刹车自检 8 问 |
| 06 | [dod-and-evidence](docs/governance/workflow/06-dod-and-evidence.md) | DoD 四步（每步三态 ✅/❌/⚪）+ evidence + 三栏交付单 |
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

## 来源与演进

- 源仓库：`JunoChenZt/subagent-for-investment`（private），初始快照 main `ad07047a`，2026-09-29
- **自 2026-09-29 起本仓库独立演进，不再与源仓库同步**。第一次修改 = 外部评审六条建议中的第 3、5 条（见 [workflow.md §7.5](docs/governance/workflow.md#75-文档迭代历史非完整)）；其余 51 个引用文件仍是快照原样
- 同日第二笔 = 建议 2 按任务大小分档（[01 §2.2.5](docs/governance/workflow/01-task-entry.md#225-任务分档s--m--l--2026-09-29-立)）
- 同日第三笔 = 建议 1 分离通用规则与项目规则（[core/](core/README.md) + [project-config.md](project-config.md)；实例层原文不动）
- 同日第四笔 = 建议 4 自动检查（[checks.md](checks.md) 登记表 + [scripts/](scripts/) 四道检查 + [CI](.github/workflows/checks.yml)）与建议 6 划算度台账（[metrics.md](metrics.md) + `scripts/metrics_report.py`）
- 待商量：分档标准细化 + 完整路由器（[project-config §2](project-config.md) `tier.router`；`scripts/tier_check.py` 是第一版）

## 已知限制

- **一级链接全通**：12 份工作流文档内的每一条相对链接都已核过，在本仓库内可解析。
- **二级链接不保证**：被引用文件（如 S2.md、backlog.md、retro 记录）自己再往外指的链接，目标未打包，可能点不开。
- 根目录的 `CLAUDE.md` 是源仓库的项目指令快照。在本仓库里用 Claude Code 时它会被当作项目指令读取，其中的分支约定 / 红线针对源仓库，不一定适用于此处。
