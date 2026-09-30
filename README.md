# workflow-baseline

让 AI 自主推进任务时「不越线、不盲跑、交付可核」的一套过程规则，通用，零项目名词：**路由卡定档 → 拆解 → 执行自验 → 刹车 8 问 → DoD 三态 → 三栏交付单 → 复盘 → PR**。本仓库自己也按这套规则运作。

## 怎么接入（三步，不改骨架）

1. 复制 `core/` 到你的仓库。
2. 复制 [project-config.md](project-config.md)，把「本项目值」列改成你的（红线、L / M 路径、验证命令、目录）。
3. 把 [core/01 §0](core/01-entry-and-routing.md) 的接入片段贴进你的 `CLAUDE.md` / `AGENTS.md`（本仓库的 [CLAUDE.md](CLAUDE.md) 就是这么做的，可当样板）。

想先看一遍「从指令到交付长什么样」：[完整案例](core/examples/walkthrough-cli-json-flag.md)。

## 两层结构

| 层 | 位置 | 放什么 |
|---|---|---|
| **骨架** | [core/](core/README.md) | 规则本体，零项目名词，参数写成 `{{key}}`；8 份文档 + 1 个案例 |
| **配置** | [project-config.md](project-config.md) | 所有 `{{key}}` 的取值；本仓库填的是它自己的 |

冲突时：规则以骨架为准，参数以配置为准。

| # | 骨架文档 | 一句话 |
|---|---|---|
| 01 | [entry-and-routing](core/01-entry-and-routing.md) | 任务进入；事实 F1–F6 + 三个是非题 H1–H3 → S / M / L；路由卡；只升不降 |
| 02 | [decompose](core/02-decompose.md) | pre-flight 5 问；`<goal>` XML；M 单 goal 可用路由卡代替 scope / verification |
| 03 | [execute-and-verify](core/03-execute-and-verify.md) | 执行前自检；硬边界即停；自验报告 |
| 04 | [brake](core/04-brake.md) | 刹车 8 问；Q5「到上限不自行免判」；Q6 冻结档 |
| 05 | [dod-and-delivery](core/05-dod-and-delivery.md) | DoD 四步每步三态 ✅ / ❌ / ⚪；evidence；回填清单；**三栏交付单** |
| 06 | [retro](core/06-retro.md) | goal 级 retro 三档；节点级 5 问；finding 去处 N = a + b + c |
| 07 | [pr-and-handoff](core/07-pr-and-handoff.md) | PR 模板；里程碑交接；节奏与并行上限 |
| 08 | [pitfall-registry](core/08-pitfall-registry.md) | 坑表格式（带「路径:」）；只增不减；元规则；两遍扫描 |

## 自动检查与台账（本仓库自己的项目资产）

| 文件 | 干什么 |
|---|---|
| [checks.md](checks.md) | 每道自动检查的登记：抓什么 / 「它会响」证明 / 误报预算 / 承重（WARN 试用为主） |
| [scripts/](scripts/) | `router` 路由器（事实推档位 + 路由卡 + 声明对账）· `lint_links` 断链 · `lint_config_slots` 骨架槽位与泄漏 · `lint_pr_body` 交付单格式 · `metrics_report` 划算度报告；各带 `--self-test`，正式测试在 [tests/](tests/) |
| [pitfalls.md](pitfalls.md) | 本仓已知坑表（条目带路径，路由器按它命中） |
| [backlog.md](backlog.md) | 待办与里程碑；每条带触发条件 |
| [observations.md](observations.md) | retro 的 observe 登记，≥ 3 次同类升级 |
| [metrics.md](metrics.md) | 规则命中台账 + PR 台账；零命中 90 天进退役候选 |
| [.github/workflows/checks.yml](.github/workflows/checks.yml) | push / PR 跑自测 + pytest + 检查，秒级 |

## 来源与演进

- 从一个投资研究项目的工作流基准抽出（2026-09-29），当天按外部评审六条建议落地：分离骨架与配置、按任务大小分档、简短入口、可检测规则自动化、允许报告未验证、测量流程划算度；晚间分档升级为 v2 事实推档位 + 路由器。
- 2026-09-30 起本仓库用自己的规则（根 CLAUDE.md、一律走 PR），并删除全部源项目内部材料，只剩骨架 + 配置 + 本仓项目资产。变更记录在 [core/README §6](core/README.md)。
- 仓库 private。
