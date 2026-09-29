# core — 通用骨架（不含任何项目名词）

> **这是什么**：一套让 AI 自主推进任务时「不越线、不盲跑、交付可核」的过程规则。它只写规则本体；项目自己的红线、阈值、路径、命令全部是 `{{key}}` 槽位，取值在 [project-config.md](../project-config.md)。
>
> **三层关系**：
>
> | 层 | 位置 | 放什么 | 谁改 |
> |---|---|---|---|
> | 骨架 | `core/`（本目录） | 规则本体，通用 | 只在规则本身要变时改，走 §5 维护协议 |
> | 配置 | [project-config.md](../project-config.md) | 所有 `{{key}}` 的取值 | 每个项目接入时改这一份 |
> | 实例 | [docs/governance/workflow/](../docs/governance/workflow/README.md) | 骨架在原项目上的展开：规则 + 参数 + 历史证据 + 坑表 | 原项目维护；别的项目不需要 |
>
> **冲突时**：规则以骨架为准；参数以配置为准；实例层只作案例与证据。
>
> **接入别的项目**：复制 `core/` + 复制 `project-config.md` 改「本项目值」列 + 把 [01](01-entry-and-routing.md) 顶部的接入片段贴进项目指令文件。三步，不用改骨架。

## 1. 十步主链路（一句话版）

| # | 一句话 | 骨架文档 |
|---|---|---|
| 1 | 判定：是不是大任务（`{{big_task_triggers}}` 七条）| [01](01-entry-and-routing.md) |
| 2 | 风险：`{{risk.high_triggers}}` 五条任一命中即高 | [01](01-entry-and-routing.md) |
| 2.5 | **定档与路由**：S / M / L，只升不降，DoD 前按 diff 对账 | [01](01-entry-and-routing.md) |
| 3 | 拆解：pre-flight 5 问 → `<goal>` XML | [02](02-decompose.md) |
| 4 | 执行：执行前自检 → 按 steps 推进 → 硬边界即停 | [03](03-execute-and-verify.md) |
| 5 | 自验：跑 verification → 自验报告 | [03](03-execute-and-verify.md) |
| 6 | 刹车 8 问：任一「是 / 不确定」停下问人 | [04](04-brake.md) |
| 7 | DoD 四步，每步三态 ✅ / ❌ / ⚪ | [05](05-dod-and-delivery.md) |
| 8 | evidence + **三栏交付单** | [05](05-dod-and-delivery.md) |
| 9 | goal 级 retro（六条触发任一才跑）| [06](06-retro.md) |
| 10 | 节点级 retro 5 问 → PR → 里程碑交接 | [06](06-retro.md) / [07](07-pr-and-handoff.md) |
| — | 坑表怎么建、怎么维护、怎么扫 | [08](08-pitfall-registry.md) |

红线（`{{red_lines}}`）不在任何一步里，它在**每一步之上**：任何时刻触到就停。

## 2. 什么时候读哪份

| 你现在在做什么 | 读 |
|---|---|
| 第一次接入 | 本文件 + [01](01-entry-and-routing.md) 顶部接入片段 |
| 刚接到任务 | [01](01-entry-and-routing.md) |
| 大任务要拆 | [02](02-decompose.md) |
| 在做一个 goal | [03](03-execute-and-verify.md) |
| goal 做完 | [04](04-brake.md) → [05](05-dod-and-delivery.md) |
| 出过事的 goal / 节点收口 | [06](06-retro.md) |
| 开 PR / 阶段交接 / 拿不准节奏 | [07](07-pr-and-handoff.md) |
| 撞了坑 / 要建坑表 | [08](08-pitfall-registry.md) |

不要从头到尾读完。每份骨架文档头部有「何时读」。

## 3. 骨架不做什么

- 不定项目红线、北极星、验收阈值、目录结构。那些是配置。
- 不含任何一条具体的「已知坑」。坑表是项目资产，骨架只定它的格式与维护协议（[08](08-pitfall-registry.md)）。
- 不含历史证据与出处。「为什么立这条规则」的实证在实例层各文档的「治的是什么」段落里；骨架只保留规则和一句话动机。

## 4. 记法约定

- `{{key}}`：配置槽位，取值见 [project-config.md](../project-config.md)。
- ✅ / ❌ / ⚪：DoD 三态，通过 / 不过 / 未验证（[05 §1](05-dod-and-delivery.md)）。
- 「本档不要求」：档位矩阵说不用做；与 ⚪ 是两种记法，不混（[01 §4](01-entry-and-routing.md)）。
- 「停下问」：保留当前状态、写明原因与建议、等人裁决；不是放弃，也不是继续。

## 5. 骨架维护协议

- **改骨架 = 改所有接入项目的规则**。commit 前缀 `docs(core):`，并在 [CHANGELOG](#6-changelog) 追加一行。
- **重大调整须人拍板**：改步骤数或顺序；改七条 / 五条 / 八问 / 四步 / 三态 / 三栏的语义；改档位矩阵；改 retro 三档或分流表；改坑表标记体系。
- **配置项不进骨架**：发现骨架里出现了项目名词、具体路径、具体数字 → 那是配置泄漏，抽成 `{{key}}`。
- **实例层不反向约束骨架**：实例层加了新规则，先问「这条对任何项目都成立吗」；成立才进骨架，否则留在实例层。
- **新增自动检查**：先在 `{{checks.registry}}` 登记（抓什么 / 「它会响」证明 / 误报预算 / 承重），再写脚本，再接 `{{checks.ci}}`，顺序不许反；一律 WARN 试用，升 hard-fail 需人裁。每加一道检查配「它会响」的证明（脚本自带 `--self-test`，自测挂了 CI 直接红）和误报预算，否则只是把「AI 记不住」换成「程序响了没人信」。
- **流程划算不划算，用代理指标看，不做前后对照**：`{{metrics.ledger}}` 记每条规则「上次拦到东西的日期」和每个 PR 的档位 / 返工 / ⚪ 数；里程碑交接跑 `{{metrics.report}}`，≥ `{{metrics.retire_after_days}}` 天零命中的进退役候选（退役走 [08 §2](08-pitfall-registry.md) 协议）。**每踩一个坑就加一道流程**是这套东西最大的风险，退役动作要定期化。

## 6. CHANGELOG

- 2026-09-29：初版。从 `subagent-for-investment` 的 11 份 workflow 子文档抽出通用骨架（评审建议 1「分离通用规则与项目规则」）；同日已先落地建议 5（DoD 三态 + 交付单）、建议 3（quickstart）、建议 2（分档）。分档标准细化与路由机制待商量（[project-config §2](../project-config.md) `tier.router`）。
- 2026-09-29（同日）：建议 4 + 6 落地。四道自动检查 + 一个报告脚本（`scripts/`，各带 `--self-test`）、检查登记表 `{{checks.registry}}`、CI `{{checks.ci}}`（WARN 试用为主）、台账 `{{metrics.ledger}}` + `{{metrics.report}}`。`tier_check` 是路由器第一版（算 S 判据 1–3；判据 4–5 与是否 L 提示人核）。§5 补两条维护原则。
