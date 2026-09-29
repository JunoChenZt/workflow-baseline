# 01 Task Entry — 大任务进入 + 风险判定

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 关联子文档: [docs/governance/workflow/02-pre-flight.md](02-pre-flight.md) / [docs/governance/workflow/03-decomposition.md](03-decomposition.md) / [docs/governance/workflow/04-goal-execution.md](04-goal-execution.md)
> 关联 skill: `risk-judgment`（已 deprecated；详细规则现在本文件 §2.2，设计历史见 [docs/governance/skill-design.md §3.3](../skill-design.md#33-已-deprecated-skill7-个详细设计已迁至-workflow-子文档)）

## 何时读这份文档

任务进入主链路的第一步。Claude 拿到新指令（用户即时指令 / S2todo 节点 / 上游解锁）时，先读本文档完成"识别任务类型 + 是否大任务 + 风险层级"判定。判定后再决定走哪条流程。

## 概览

本文档覆盖 10 步主链路的前两步：§2.1 大任务进入（识别类型 + 是否大任务）+ §2.2 风险判定（5 条触发即高风险）。判定后分流：

- **非大任务** → 过 §2.2.5 S 判据：5 条全满足 = **S 档**，跳过 §2.2 §2.3 §2.4 直接进 §2.5；任一不满足 = **M 档**
- **大任务 + 低风险** = **M 档** → 进 §2.3 节点切入 5 问，无需用户确认
- **大任务 + 高风险** = **L 档** → 停下等用户确认拆解方案后再进 §2.3
- §2.2.5 **任务分档（2026-09-29 立）**：三档各自「要做 / 不用做」矩阵；判据客观可核；**只许升不许自己降**；DoD 前用实际 diff 对账、超了自动升档

---

## 2.1 大任务进入

**输入**：

- 用户即时指令（"推进 A6.1.2"、"修一下 prompt 的 X 问题"）
- 或 [docs/roadmap/S2.md](../../roadmap/S2.md) 表格中 ⚪ NOT STARTED / 🟡 PENDING 的节点
- 或上一节点收口后下一节点的依赖解锁

**Claude 的动作**：

1. **识别任务类型**：
   - 是 S2todo 节点？→ 标定节点 ID，进入 §2.2 风险判定
   - 是临时小指令？→ 评估是否在 [docs/governance/workflow.md §0](../workflow.md#0-适用前置条件误用防线) 适用前置之内
   - 是生产事故 / 热修？→ **不走本基准**，按用户即时指令处理
2. **识别"是否大任务"**：触发以下任一即视为大任务：
   - 涉及 2 个以上模块 / 文件夹 / phase
   - 涉及 schema / prompt / runtime / fallback / archive replay / CI/CD 任一核心链路
   - 涉及新增能力，而非单点 bugfix
   - 涉及多个 agent、多个 subtask 或多个验收标准
   - 执行后需要跑完整 DoD / corner case / smoke / observation
   - agent 无法在 10 分钟内明确完成并验证
   - 节点本身在 [docs/roadmap/S2.md](../../roadmap/S2.md) 标记为大节点

**输出**：

- 任务类型：`s2-node` / `temp-instruction` / `hotfix-out-of-scope`
- 是否大任务：`true` / `false`
- 若是 s2-node：节点 ID + 子阶段（S2.1 / S2.2 / S2.3）

**失败处理**：

- 任务类型识别不出 → 停下问用户："这个任务属于 S2 节点 / 临时指令 / 别的范畴？"
- 用户指令模糊（"看看代码"）→ 不进入主链路，按聊天处理

**分支**：

- 是大任务 → §2.2 风险判定（结果决定 M / L 档，§2.2.5）
- 非大任务 → 先过 §2.2.5 的 S 判据 5 条：**全满足 = S 档**，跳过 §2.2 / [02 §2.3](02-pre-flight.md#23-节点切入-5-问pre-flight-check) / [03 §2.4](03-decomposition.md#24-拆小任务)，直接进 [04 §2.5](04-goal-execution.md#25-单个-goal-执行) 按 S 档矩阵轻量推进；**任一不满足 = M 档**，按 M 档矩阵走（要拆解、要全 DoD）

---

## 2.2 风险判定（5 条触发即高风险）

**仅在 §2.1 判定为大任务时进入此节**。

**5 条触发条件**（任一为真即视为高风险）：

1. 触及 schema / prompt / Fallback / 路由（已 DONE 节点契约）
2. 触及 hard_block 决策路径 / 北极星合规边界
3. 涉及 ≥ 2 个 phase 或跨子阶段（S2.1 / S2.2 / S2.3 跨界）
4. 引入新的外部依赖 / 新数据源 / 新 API — 触及时须同步跑 [source-readiness-checklist](../../infrastructure/source-readiness-checklist.md)（A6.1.4 Phase 0a 新增治理项）
5. 修改 archive replay 兼容性（旧 archive 喂新 schema 必须能 replay）

**Claude 的动作**：

1. 对照 5 条逐一判定，输出**判定理由**（≤ 3 行）：

   ```
   风险层级: 高
   理由: 触及条件 1（修改 fund_mgr prompt 段 6 hard_block 路径）+ 条件 2（北极星合规边界）
   ```

2. 高风险 → 进入 [docs/governance/workflow/02-pre-flight.md §2.3](02-pre-flight.md#23-节点切入-5-问pre-flight-check) 拆小任务前**先停下，等用户确认拆解方案**
3. 低风险 → 直接进 [docs/governance/workflow/02-pre-flight.md §2.3](02-pre-flight.md#23-节点切入-5-问pre-flight-check) 拆小任务，无需用户确认

**输出**：

- `risk_level`: `high` / `low`
- `judgment_reason`: ≤ 3 行说明

**失败处理 / 兜底**：

- 判定结果"不确定" → **默认按"高风险"处理**，停下问
- 用户后续可以推翻判定（"这个其实低风险，别等我"）
- 判定理由过长（> 3 行）= 判定本身有问题，回炉
- "5 条都不触发" 不等于零风险，仍要走 [docs/governance/workflow/02-pre-flight.md §2.3](02-pre-flight.md#23-节点切入-5-问pre-flight-check) 拆解流程，只是免去用户确认

**与 [CLAUDE.md](../../../CLAUDE.md) 强制红线的关系**：

- 强制红线 = "立即停"（任何阶段触发都停），不等风险判定
- 风险判定 = "走哪条流程"（高风险需用户确认拆解 / 低风险自走）
- 触及红线的任务，风险判定永远是"高"，且必须停下问，不进 [docs/governance/workflow/02-pre-flight.md §2.3](02-pre-flight.md#23-节点切入-5-问pre-flight-check)

## 2.2.5 任务分档（S / M / L · 2026-09-29 立）

> **治的是什么**：修一个错别字，按字面也要走 XML 拆解、5 类 evidence、节点复盘。流程成本与任务风险不匹配，结果只有两种：
> 要么流程被悄悄绕开（沉默跳过 = [05 Q5](05-brake-self-check.md#27-刹车自检8-问)），要么把执行者拖到不愿意用。
> 现有机制其实已经有一半：§2.1「非大任务直接进 §2.5」、[07 §2.10.1](07-retro-goal.md#2101-触发条件6-条触发即跑-retro) 六条不命中就跳过 retro、
> 项目指令里「docs-only 小步提交」例外。缺的是把它做成**显式三档**，每档写死「要做什么、不用做什么」。
>
> **最要紧的设计点：档位由谁判。** 让执行者自己判档，就是「自己给自己开闸」—— Q5 那个老问题换了个入口。
> 所以本节三条底线：**判据客观可核**（数文件、看路径、看 diff，不看"我觉得"）；**只许升、不许自己降**；**DoD 前用实际 diff 对账，超了自动升档**。

### 2.2.5.1 三档定义

| 档 | 定义 | 对应现有判定 |
|---|---|---|
| **S 小修** | §2.1 判为**非大任务**，且下面 S 判据 **5 条全满足** | 非大任务 |
| **M 普通** | §2.1 大任务 + §2.2 低风险；**或** 非大任务但 S 判据任一不满足 | 大任务 + 低风险 |
| **L 完整** | §2.1 大任务 + §2.2 高风险；**或** 触及项目红线；**或** 用户点名 | 大任务 + 高风险 |

**S 判据**（5 条全满足才是 S；每条都能用 `git diff --stat` 或路径核，不需要判断力）：

| # | 判据 | 怎么核 |
|---|---|---|
| 1 | 改动文件 **≤ 3 个**，且在同一个顶层目录下（`src/<模块>/` 与它配对的 `tests/` 算同一处） | `git diff --stat` 数文件、看路径 |
| 2 | 增删合计 **≤ 100 行** | `git diff --stat` 末行 |
| 3 | **不碰敏感路径表**（§2.2.5.2）任何一项 | diff 路径对表；「碰」= 出现在 diff 里，不看改了几行 |
| 4 | **不新增**能力 / 外部依赖 / 配置项 —— 形态限于：bugfix、typo、文档、注释、只加测试、重命名、日志文案 | 看 diff 内容；出现新 import 第三方包 / 新 env 读取 / 新 CLI 选项即不满足 |
| 5 | 有**现成**的验证手段可立即跑：受影响的测试文件已存在，或 lint / 链接检查能覆盖 | 列出那条命令；列不出就不是 S |

判据 1、2 的数字是**初值，WARN 试用**（本仓 [验收标准 §4 试用期规则](../e2e-acceptance-standard.md) 同款）：记录「S 档被自动升档的次数」和「S 档交付后返工的次数」，一个季度后按这两个数调松紧，不凭感觉改。

### 2.2.5.2 敏感路径表（项目配置）

碰到任何一项，档位至少 M；同时命中 §2.2 五条之一则 L。本表是**项目配置**，别的项目接入时按自己的目录换；本仓初值 = §2.2 五条 + 项目指令「需要确认」清单的并集：

- schema / prompt / fallback / 路由 / 闸门与质检判据（gate、acceptance、quality）
- 配置目录、`.env*`、`.claude/settings*`、任何权限配置
- CI 配置（`.github/`）、数据库 migrations、依赖清单（`pyproject.toml` / `requirements*.txt` / lock 文件）
- 生产部署脚本与 runbook

### 2.2.5.3 每档要做什么、不用做什么

| 步骤 | S 小修 | M 普通 | L 完整 |
|---|---|---|---|
| 01 判定 + **档位声明** | ✓ 一行 | ✓ | ✓ + 用户确认拆解方案 |
| 02 pre-flight 5 问 | **不用** | ✓ | ✓ + 派 pitfall-scout |
| 03 拆解 `<goal>` XML | **不用**（整个任务 = 1 个隐式 goal） | ✓ | ✓ + decomposition.md 落盘 + 用户确认 |
| 04 执行 + 自验 | ✓（verification = 受影响测试 + lint） | ✓ | ✓ |
| 05 刹车 8 问 | ✓ **不省**（一屏以内） | ✓ | ✓ |
| 06 DoD 四步 | Code Review ✓ / Corner Case = 跑受影响测试 / 冒烟 **本档不要求** / 彻底跑通 ✓ | 四步全 | 四步全 |
| 06 evidence | **只交交付单三栏**（§2.9.5） | 5 类 evidence + 交付单 | 5 类 + 交付单 + 回填清单（§2.9.4） |
| 07 goal 级 retro | 6 条触发**照旧**（只在出事时响，不分档） | 同 | 同 |
| 08 节点级 retro 5 问 | **不用** | ✓ 简版（5 问各一行，不落 retro 文件） | ✓ 完整（落 `docs/retro/`） |
| 08 PR | **可不开**，直接进工作分支；开则简版描述 = 档位声明 + 交付单 | 完整模板 | 完整模板 + review |
| 08 cold review | 不用 | 可选 | 推荐 |
| 09 坑表 | 撞坑时查 | 起步时扫一遍相关子阶段 | pitfall-scout 必派 |

**两种「没做」是两种记法，不许混**：矩阵说不用做的，写「**本档不要求**」；矩阵要求做但没跑的，才是 [06 §2.8.0](06-dod-and-evidence.md#280-每一步的结果只有三态2026-09-29-立) 的 **⚪ 未验证**。交付单第三栏只放 ⚪；「本档不要求」不进第三栏，但交付单**头部必须写档位**，让审的人能自己核「不要求」站不站得住。

### 2.2.5.4 只升不降 + 自动升档

1. **入口声明**：判定完写一行，进自验报告与交付单头部：`档位: S ｜ 判据: 2 文件 / 41 行 / 无敏感路径 / bugfix / pytest tests/test_x.py`。写不出五个判据值的，不是 S。
2. **DoD 前对账**（[06 §2.8.0](06-dod-and-evidence.md#280-每一步的结果只有三态2026-09-29-立) 之前）：跑 `git diff --stat <base>`，数文件、数行、对敏感路径表，与入口声明比。**任一超出 → 自动升档**到对应档，补做升档后矩阵新增的步骤（S → M 至少补：一段 objective / scope / verification 的简版 goal、完整 DoD 四步、5 类 evidence）。升档写进头部：`档位: S → M（DoD 对账：diff 触及 config/）`。
3. **禁止自己降档**：执行者在任何时点都不得把档位往下改。唯一例外 = 用户明确说，且声明里引用原话：`档位: M → S（用户裁：「这个不用拆」）`。
4. **拿不准 → 高一档**。与 §2.2「不确定按高风险」同一条原则。
5. **S 档的隐式 goal 仍受 stop_conditions**：做到一半发现要碰敏感路径，那一刻就是升档信号 —— 停下按 M / L 走，不是「顺手改完再说」。

**与其他机制的关系**：项目指令里「docs-only 维护类小步提交」例外 = S 档的一个实例；三档只改「做多少」，**不改红线** —— 红线任何档都立即停；[07 §2.10.1](07-retro-goal.md#2101-触发条件6-条触发即跑-retro) 六条触发不分档。

**输出**：`tier`: `S` / `M` / `L` + 一行判据；进 `<goal tier="...">`（[03 §2.4.3](03-decomposition.md#243-goal-xml-模板)）、自验报告、交付单头部。

---

## Cross-references

**上游（我引用谁）**：

- [CLAUDE.md](../../../CLAUDE.md) — 强制红线（风险判定与红线的关系；「需要确认」清单是 §2.2.5.2 敏感路径表的来源之一）
- [docs/governance/workflow.md §0](../workflow.md#0-适用前置条件误用防线) — 适用前置（判定任务类型时参考）
- [docs/roadmap/S2.md](../../roadmap/S2.md) — S2todo 节点表（任务来源 + 大节点标记）
- [docs/infrastructure/source-readiness-checklist.md](../../infrastructure/source-readiness-checklist.md) — 数据源 production readiness checklist（条件 4 触及时引用，A6.1.4 新增）

**下游（谁引用我）**：

- [02-pre-flight.md](02-pre-flight.md) — 高风险确认后进入 §2.3 pre-flight 5 问
- [03-decomposition.md](03-decomposition.md) — pre-flight 后进入 §2.4 拆小任务
- [04-goal-execution.md](04-goal-execution.md) — 非大任务直接进 §2.5 单 goal 执行
- `risk-judgment` SKILL — 消费本文档定义的 5 条触发条件输出 `risk_level` + `judgment_reason`
- [04-goal-execution.md](04-goal-execution.md) §2.5.1 / §2.6.2 — 档位声明进执行前自检与自验报告；[06-dod-and-evidence.md](06-dod-and-evidence.md) §2.8.0 — DoD 前档位对账、「本档不要求」与 ⚪ 的区分；[08-retro-node-and-pr.md](08-retro-node-and-pr.md) §6 — PR 模板档位行 + S 档简版
