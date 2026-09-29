# Workflow（S2 工作基准）

> **分层说明（2026-09-29 起）**：本文件与 [workflow/](workflow/) 11 份子文档是**实例层** —— 通用骨架在 `subagent-for-investment` 项目上的展开，含项目参数与历史证据。
> **规则本体的真值源是 [core/](../../core/README.md)（通用骨架）**，项目参数的真值源是 [project-config.md](../../project-config.md)。两处冲突时：规则以骨架为准、参数以配置为准，本层只作案例与证据。别的项目接入只需要 core/ + project-config.md，不需要本层。

> 本文件是 **S2 阶段过程层基准** 的导航 + 主链路总览 + 维护协议。
>
> **优先级**：[CLAUDE.md](../../CLAUDE.md) > 本文件 + [docs/governance/workflow/](workflow/) 子文档 > [docs/governance/git-workflow.md](git-workflow.md)。
>
> **文档关系**：
>
> - [CLAUDE.md](../../CLAUDE.md) — 顶层原则、强制红线、workflow 入口
> - 本文件 + [docs/governance/workflow/](workflow/) 子文档 — S2 阶段任务推进的完整过程规则（10 步主链路）
> - [docs/governance/git-workflow.md](git-workflow.md) — git 操作细节
> - [docs/roadmap/S2.md](../roadmap/S2.md) — 任务清单 / 节点状态
>
> **Reading Order**：进入任务时按 §0.1 表定位当前阶段读哪一份子文档；不要从头到尾读完。
>
> 与 [CLAUDE.md](../../CLAUDE.md) 冲突时以 [CLAUDE.md](../../CLAUDE.md) 为准。

---

## 0. 适用前置条件（误用防线）

本基准**仅在以下情况**自动套用：

- 当前任务对应 [docs/roadmap/S2.md](../roadmap/S2.md) 中的具体节点（含 ⚪ NOT STARTED / 🟡 PENDING / 🔵 IN PROGRESS）
- 推进方向与北极星 + 稳定性 + 节点 DoD 一致

**以下情况本文件只作参考**，不得自动套用 §1 主链路规则：

- 生产事故 / 安全热修（按用户即时指令；不走自主推进通道）
- S3 / S4 阶段任务（按各自基准；**S3 / S4 基准未建立时先停下问**）
- 与 S2 无关的脚手架 / 工具改进 / 一次性脚本
- 用户临时指令明确超出 S2 范围

不确定是否适用 → **默认按"非 S2"处理，停下问**，不要靠"差不多"开干。

---

## 0.1 Reading Order（什么时候读哪一份子文档）

本目录按主题切片成 11 个子文档。按当前任务阶段定位需要的子文档，不需要每次全文扫一遍：

| 当前所处阶段 | 必读子文档 |
|---|---|
| **第一次接入 / 想先看个完整例子** | [00-quickstart.md](workflow/00-quickstart.md)（二十行接入片段 + [完整案例](workflow/examples/walkthrough-cli-json-flag.md)）|
| 任务进入 / 接到新指令 | [01-task-entry.md](workflow/01-task-entry.md)（§2.1 大任务进入 + §2.2 风险判定 + **§2.2.5 定档 S / M / L**）|
| 节点起步（pre-flight） | [02-pre-flight.md](workflow/02-pre-flight.md)（§2.3 节点切入 5 问）|
| 拆小任务 / 写 `<goal>` XML | [03-decomposition.md](workflow/03-decomposition.md)（§2.4 拆解 + XML 模板）|
| Goal 执行中 + 自验 | [04-goal-execution.md](workflow/04-goal-execution.md)（§2.5 + §2.6）|
| Goal 完成 / 不确定是否触发刹车 | [05-brake-self-check.md](workflow/05-brake-self-check.md)（§2.7 8 问）|
| 刹车通过 → DoD + evidence | [06-dod-and-evidence.md](workflow/06-dod-and-evidence.md)（§2.8 + §2.9）|
| Non-trivial goal 后 | [07-retro-goal.md](workflow/07-retro-goal.md)（§2.10 三档 retro）|
| 节点收口 / 写 PR | [08-retro-node-and-pr.md](workflow/08-retro-node-and-pr.md)（§2.11 + §6 PR 模板）|
| 不确定是否触发已知坑 | [09-known-pitfalls.md](workflow/09-known-pitfalls.md)（§3 按子阶段查）|
| 子阶段交接 | [10-verification-report.md](workflow/10-verification-report.md)（§4 全套审视）|
| 拿不准节奏 / 并行限制 | [11-cadence.md](workflow/11-cadence.md)（§5）|
| 修改本基准 | 本文件 §7 维护协议 |

**Claude 自动应用此表**：进入任务时按"当前所处阶段"定位，只读对应子文档。子文档内自带"何时读 + 概览 + Cross-references"，独立可消费。

详细子文档清单见 [docs/governance/workflow/README.md](workflow/README.md)。

---

## 1. 10 步主链路总览

### 1.1 ASCII 流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                       1. 大任务进入                                  │
│                  (S2todo 节点 / 用户指令)                            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │  Q: 是否大任务?    │ ─── 否 ──┐
                    │  (§2.1 7 条判定)   │           │
                    └─────────┬──────────┘           │
                              │ 是                   │
                              ▼                      │
                    ┌────────────────────┐           │
                    │  2. 风险判定       │           │
                    │  (§2.2 5 条触发)   │           │
                    └─────────┬──────────┘           │
                              │                      │
                ┌─────────────┼─────────────┐        │
                │ 高风险      │             │ 低风险  │
                ▼             │             ▼        │
        ┌─────────────┐       │      ┌─────────────┐ │
        │ 用户确认拆解 │       │      │  低风险自走  │ │
        └──────┬──────┘       │      └──────┬──────┘ │
               │              │             │        │
               └──────────────┼─────────────┘        │
                              ▼                      │
                    ┌────────────────────┐           │
                    │  2.3 节点切入 5 问 │           │
                    │  (pre-flight)      │           │
                    └─────────┬──────────┘           │
                              │                      │
                              ▼                      │
                    ┌────────────────────┐           │
                    │  3. 拆小任务        │           │
                    │  (decomposition.md  │           │
                    │   + <goal> XML)     │           │
                    └─────────┬──────────┘           │
                              │                      │
                              ▼                      │
                    ┌────────────────────┐◄──────────┘
                    │  4. 单个 /goal      │
                    │     执行 (§2.5)     │◄────┐ 改方向重做
                    └─────────┬──────────┘     │
                              │                │
                  ┌───────────┤                │
                  │ 触及硬边界 │ 正常执行       │
                  ▼           ▼                │
        ┌─────────────┐  ┌─────────────────┐   │
        │ 立即停下    │  │  5. goal 达成    │   │
        │ (CLAUDE.md  │  │  (diff + 自验)   │   │
        │  红线)      │  └────────┬────────┘   │
        └─────────────┘           │            │
                                  ▼            │
                        ┌─────────────────┐    │
                        │  6. 刹车自检 8 问│    │
                        │     (§2.7)       │    │
                        └────────┬────────┘    │
                                 │             │
                       ┌─────────┤             │
                       │ 命中     │ 未命中      │
                       ▼         ▼             │
              ┌─────────────┐   │              │
              │  用户裁决    │   │              │
              │ 放行/改/停  │───┘──── 改方向 ──┘
              └─────────────┘
                       │ 放行
                       ▼
                ┌─────────────────┐
                │  7. DoD 四步     │
                │     (§2.8)       │
                └────────┬────────┘
                         │
              ┌──────────┤
              │ 失败      │ 通过
              ▼           ▼
       ┌──────────┐  ┌─────────────────┐
       │ 同 goal  │  │  8. evidence    │
       │  重做    │  │     收集 (§2.9)  │
       │ (≥3 次  │  └────────┬────────┘
       │  升级    │           │
       │  重拆)   │           ▼
       └────┬─────┘  ┌─────────────────────┐
            │        │  Q: non-trivial?    │
            │        │  (§2.10 6 条触发)   │ ─── 否 ──┐
            │        └─────────┬──────────┘           │
            │                  │ 是                   │
            │                  ▼                      │
            │        ┌─────────────────────┐          │
            │        │  9. goal 级 retro    │          │
            │        │  (skill:            │          │
            │        │   retrospective-    │          │
            │        │   goal)             │          │
            │        └──────┬──────────────┘          │
            │               │                         │
            │       ┌───────┼───────┐                 │
            │       │       │       │                 │
            │       ▼       ▼       ▼                 │
            │   must_   should_  observe              │
            │   update  update   登记观察              │
            │   落盘    分流 §   §2.10.6              │
            │   §3      2.10.5                        │
            │   ▲                                     │
            │   │                                     │
            └───┘                                     │
                                                      │
                    ┌─────────────────────┐◄─────────┘
                    │  Q: 节点全部 done?  │
                    └─────────┬──────────┘
                              │
                  ┌───────────┤
                  │ 否         │ 是
                  │            ▼
                  │   ┌─────────────────────┐
                  │   │ 10. 节点级复盘 + PR │
                  │   │  (§2.11)            │
                  │   │  - retrospective-   │
                  │   │    node 5 问         │
                  │   │  - 写 docs/retro/    │
                  │   │    S2/<node-id>_     │
                  │   │    <date>.md         │
                  │   │  - 开 PR (异步)     │
                  │   │  - 推下一节点       │
                  │   └─────────────────────┘
                  │
                  └──────► 回 step 4，跑下一 goal
```

**流程图说明**：

- ▼ = 正常推进；◄ = 返工 / 回流
- 菱形 Q 节点表示判定分叉，方框是动作
- 刹车红线（[CLAUDE.md](../../CLAUDE.md) 强制红线）可在任何步骤触发，箭头省略
- §2.7 用户裁决"停" → 升级 [CLAUDE.md](../../CLAUDE.md) 强制红线流程，不在主链路画

### 1.2 10 步一句话总览

| # | 一句话 | 子文档 |
|---|---|---|
| 1. 大任务进入 | 识别任务类型 + 是否大任务（7 条判定） | [01-task-entry.md](workflow/01-task-entry.md) |
| 2. 风险判定 | 5 条触发即高风险（高 → 用户确认拆解 / 低 → 自走） | [01-task-entry.md](workflow/01-task-entry.md) |
| 2.5 **分档** | S 小修 / M 普通 / L 完整；判据客观可核（文件数 / 行数 / 敏感路径 / 不新增 / 有现成验证）；每档「要做 / 不用做」矩阵；**只升不降**、DoD 前按 diff 对账自动升档 | [01-task-entry.md §2.2.5](workflow/01-task-entry.md#225-任务分档s--m--l--2026-09-29-立) |
| 2.3 Pre-flight | 节点切入 5 问（依赖 / 并行 / 风险档位 / 预算 / Fallback） | [02-pre-flight.md](workflow/02-pre-flight.md) |
| 3. 拆小任务 | 大任务拆成 `<goal>` XML + decomposition.md | [03-decomposition.md](workflow/03-decomposition.md) |
| 4. 单 goal 执行 | 按 `<steps>` 推进；触红线 / `<stop_conditions>` 即停 | [04-goal-execution.md](workflow/04-goal-execution.md) |
| 5. goal 达成自验 | 跑 `<verification>` + smoke + 自验报告 | [04-goal-execution.md](workflow/04-goal-execution.md) |
| 6. 刹车自检 8 问 | 任一是 / 不确定 → 停下等用户裁决 | [05-brake-self-check.md](workflow/05-brake-self-check.md) |
| 7. DoD 四步 | Code Review / Corner Case / 冒烟 / 彻底跑通；**每步三态 ✅ / ❌ / ⚪**（§2.8.0：没跑标 ⚪ 写原因，不算过也不算阻断，由用户决定收不收） | [06-dod-and-evidence.md](workflow/06-dod-and-evidence.md) |
| 8. evidence 收集 | 5 类 evidence 收齐 → summary 进 PR 描述；**交付一律用三栏交付单**（§2.9.5：改了什么 / 验证了什么怎么验 / 未验证什么为什么，第三栏没有写「无」）；**本 goal 若有裁决落地，另按 §2.9.4 的 8 格固定名单点名回填真值源**（每格「改了」或「N/A + 理由」，不许留空）| [06-dod-and-evidence.md](workflow/06-dod-and-evidence.md) |
| 9. goal 级 retro | 6 条触发任一 → must_update / should_update / observe | [07-retro-goal.md](workflow/07-retro-goal.md) |
| 10. 节点级复盘 + PR | 5 问 retro + 写 retro 文件 + 开 PR + 推下一节点 | [08-retro-node-and-pr.md](workflow/08-retro-node-and-pr.md) |

### 1.3 主链路 skill 一览（与 [skill-design.md §1 全景图 (2 active subagent + 7 deprecated)](skill-design.md#1-skill-全景图) 同步）

| # | skill name | 一句话 | goal-done-reminder 驱动? | 子文档 |
|---|---|---|---|---|
| 1 | `risk-judgment` | 判定大任务风险层级 (high/low) | 否 | [01-task-entry.md](workflow/01-task-entry.md) |
| 2 | `pitfall-scout` | subagent 扫坑表，返本任务相关 3-5 条 | 否 | [09-known-pitfalls.md](workflow/09-known-pitfalls.md) |
| 3 | `goal-decomposition` | 大任务拆成 `<goal>` XML 列表 | 否 | [03-decomposition.md](workflow/03-decomposition.md) |
| 4 | `brake-self-check` | goal 后跑 8 问刹车自检 | **是** | [05-brake-self-check.md](workflow/05-brake-self-check.md) |
| 5 | `dod-checklist` | DoD 四步 + evidence 收集 | **是** | [06-dod-and-evidence.md](workflow/06-dod-and-evidence.md) |
| 6 | `retrospective-goal` | non-trivial goal 后 must/should/observe | **是** | [07-retro-goal.md](workflow/07-retro-goal.md) |
| 7 | `retrospective-node` | 节点收口前 5 问 + sedimentation | 否（语义层） | [08-retro-node-and-pr.md](workflow/08-retro-node-and-pr.md) |
| 8 | `verification-report` | 子阶段交接全套审视，subagent 化 | 否 | [10-verification-report.md](workflow/10-verification-report.md) |
| 9 | `pr-template` | 按 §6 模板起草 PR 描述 | 否 | [08-retro-node-and-pr.md](workflow/08-retro-node-and-pr.md) |

> **`goal-done-reminder 驱动?` 列语义（路径 D 重写后，2026-05-19）**：
> 不再是 per-skill 独立 hook。单一 goal-done-reminder 机制（路径 D：
> `TaskCompleted` → pending JSONL → `UserPromptSubmit`/`SessionStart` 注入）
> 在每个 `[GOAL]` 完成时注入一次提醒，驱动主 Claude 按序跑
> **brake-self-check (4) + dod-checklist (5) + retrospective-goal (6)**。
> retrospective-node (7) 是**节点收口语义层**（"所有 [GOAL] done" 时触发，
> 非 [GOAL]-complete hook 驱动）。**真值源 = [CLAUDE.md](../../CLAUDE.md)
> "Task 前缀约定" + "Skill 触发强制规则"**；与之冲突以 CLAUDE.md 为准。
> 程序层（hook）+ 语义层（CLAUDE.md 强制规则）双层独立，任一失效另一层兜底。

详细 skill 设计（输入 / 输出 XML schema、hook 配置、边界）见 [skill-design.md §3 subagent skill 详细设计 + deprecated 索引](skill-design.md#3-subagent-化-skill-详细设计)。

---

## 7. 基准维护协议

### 7.1 迭代原则

- 本基准随 S2 推进迭代；任何新发现的"已知坑" / 边界 case → 回填 [workflow/09-known-pitfalls.md §3](workflow/09-known-pitfalls.md#3-已知坑--防回归-checklist)
- 节点完成时若 DoD 发现盲点 → 升级到 [workflow/06-dod-and-evidence.md §2.8](workflow/06-dod-and-evidence.md#28-dod-四步) DoD 展开条款
- 新发现的"自主推进出问题"案例 → 升级到 [workflow/05-brake-self-check.md §2.7](workflow/05-brake-self-check.md#27-刹车自检8-问) 刹车 8 问对应类别
- 与 [docs/roadmap/S2.md](../roadmap/S2.md) 不重复内容；本文是**过程层**，S2todo 是**任务层**

### 7.2 修改本文件的规则

- type(scope): `docs(baseline):`
- 重大调整需在 commit message 显式 `baseline:` scope 并停下问用户
- 重大调整包括：
  - 改主链路步骤数 / 顺序
  - 改风险判定 5 条 / 刹车 8 问 / DoD 四步的语义
  - 改 Reading Order 表格
  - 改 [workflow/09-known-pitfalls.md §3](workflow/09-known-pitfalls.md#3-已知坑--防回归-checklist) 已知坑的强度标记（🔴 / 🟡 / 🟢 之间互调）
  - 改 [workflow/07-retro-goal.md §2.10](workflow/07-retro-goal.md#210-goal-级-retro按需) retro 三档语义（must_update / should_update / observe）
  - 改 [workflow/07-retro-goal.md §2.10.5](workflow/07-retro-goal.md#2105-should_update-分流表) should_update 分流表
  - 改 [workflow/11-cadence.md §5.2](workflow/11-cadence.md#52-并行节点-wip-limit) 并行节点数上限

### 7.3 子阶段交接时的基准 review

- **S2.1 → S2.2 切换时**：
  - review [workflow/09-known-pitfalls.md](workflow/09-known-pitfalls.md) §3.3 §3.4 §3.5 是否还相关
  - review [workflow/10-verification-report.md §4.1](workflow/10-verification-report.md#41-触发时机) 通过标准是否达成
  - 按 [workflow/10-verification-report.md §4.2](workflow/10-verification-report.md#42-子阶段交接的审视清单) 审视清单走一遍
- **S2.2 → S2.3 切换时**：
  - 同上 [workflow/09-known-pitfalls.md](workflow/09-known-pitfalls.md) §3.6 §3.7
  - §4.2 审视清单
- **S2.3 完成时**：
  - 整个 S2 基准归档
  - 启动 S3 基准（继承 + 调整）
  - 所有 status = retired_after_phase_review 的已知坑统一归档

### 7.4 与其他文档的同步

| 子文档 / 章节改动 | 同步动作 |
|---|---|
| [05-brake-self-check.md](workflow/05-brake-self-check.md) §2.7 8 问 | 同步 `brake-self-check` SKILL.md |
| [07-retro-goal.md](workflow/07-retro-goal.md) §2.10 三档 / 模板 | 同步 `retrospective-goal` SKILL.md |
| [07-retro-goal.md](workflow/07-retro-goal.md) §2.10.5 分流表 | 同步 `retrospective-goal` + `retrospective-node` SKILL.md |
| [07-retro-goal.md](workflow/07-retro-goal.md) §2.10.6 observe 出口 | 同步 `retrospective-goal` SKILL.md |
| [08-retro-node-and-pr.md](workflow/08-retro-node-and-pr.md) §2.11 节点复盘 5 问 | 同步 `retrospective-node` SKILL.md |
| [06-dod-and-evidence.md](workflow/06-dod-and-evidence.md) §2.8 DoD 四步 | 同步 `dod-checklist` SKILL.md |
| [08-retro-node-and-pr.md](workflow/08-retro-node-and-pr.md) §6 PR 模板 | 同步 `pr-template` SKILL.md |
| [03-decomposition.md](workflow/03-decomposition.md) §2.4.3 `<goal>` XML | 同步 `goal-decomposition` SKILL.md |
| [09-known-pitfalls.md](workflow/09-known-pitfalls.md) §3.1 标记体系（强度/status） | 同步所有 retro skill + Verification Report 模板 |

修改 workflow 时**同步更新相关 SKILL.md** 是 §7.2 重大调整的必备步骤。

### 7.5 文档迭代历史（非完整）

- 2026-05-13：初版（10 步主链路 + 风险判定 + 刹车 8 问 + DoD + retro 三档）
- 2026-05-14：分层重构 — 主文件保留导航 + 总览 + 维护协议，详细规则切片到 `docs/governance/workflow/` 11 个子文档
- 2026-05-19：§1.3 `hook?` 列对齐路径 D — 改为 `goal-done-reminder 驱动?`，语义从 per-skill hook 改为单一 goal-done-reminder 机制（路径 D）；dod-checklist 否→是（CLAUDE.md [GOAL]-complete 序列含 DoD）、retrospective-node 是→否（节点收口语义层非 hook 驱动）。来源：backlog L 翻案 + CLAUDE.md 术语对齐（PR #117）
- 2026-09-29：本仓库从 `subagent-for-investment` 独立出来后的第一次基准修改（外部评审六条建议中的第 3、5 条）—— **建议 5**：DoD 每步改三态（[06 §2.8.0](workflow/06-dod-and-evidence.md#280-每一步的结果只有三态2026-09-29-立)）+ 固定三栏交付单（[06 §2.9.5](workflow/06-dod-and-evidence.md#295-交付单固定三栏2026-09-29-立)），把原先散在 05 §2.7.5 / 08 §6.2 / 09 §3 元规则三处的「未验证」规则收成一个格式；自验报告、Q5 上升出口、PR 模板同步。**建议 3**：新增 [00-quickstart.md](workflow/00-quickstart.md)（接入片段 + 压缩版 Reading Order）与 [完整案例](workflow/examples/walkthrough-cli-json-flag.md)。建议 1（拆通用骨架）、2（按大小分档）、4 / 6（自动检查与流程测量的季度动作）**未做**，待后续。
- 2026-09-29（同日第四笔）：**建议 4 + 6** —— 四道自动检查（[scripts/](../../scripts/)：链接 / 骨架槽位与泄漏 / 交付单格式 / 档位对账，各带 `--self-test` 作「它会响」证明）+ 登记表 [checks.md](../../checks.md)（抓什么 / 证明 / 误报预算 / 承重，一律 WARN 试用，断链与自测除外）+ CI [checks.yml](../../.github/workflows/checks.yml)；划算度台账 [metrics.md](../../metrics.md)（规则上次命中日期 / PR 档位·返工·⚪）+ `scripts/metrics_report.py`（≥ 90 天零命中进退役候选，只看趋势不做 A/B）。`tier_check` = 路由器第一版，细化标准仍待商量。**评审六条至此全部有落地或明确去处。**
- 2026-09-29（同日第三笔）：**建议 1 分离通用规则与项目规则** —— 新立 [core/](../../core/README.md) 通用骨架 8 份 + README（规则本体，零项目名词，所有参数写成 `{{key}}` 槽位）与 [project-config.md](../../project-config.md)（槽位清单 + 本项目取值，含 `tier.router` 待商量项）；本文件与 11 份子文档降为**实例层**（原文不动，头部加分层说明与骨架指针）。接入别的项目 = 复制 core/ + 改 project-config。用户同日提出「分档标准后面要再细化、可引入路由机制」→ 骨架把「定档」与「路由」拆成两节留接口，细化本身未做。建议 4 / 6 未做（落点已写进 core/07 §2 交接审视与 core/README §5）。
- 2026-09-29（同日第二笔）：**建议 2 按任务大小分档** —— [01 §2.2.5](workflow/01-task-entry.md#225-任务分档s--m--l--2026-09-29-立) 新立 S / M / L 三档：S 判据五条全部可用 `git diff --stat` 与路径核（≤ 3 文件 / ≤ 100 行 / 不碰敏感路径表 / 不新增能力依赖 / 有现成验证；两个数字为初值 WARN 试用）；每档「要做 / 不用做」矩阵；**只许升不许自己降**，DoD 前按实际 diff 对账、超出自动升档；「本档不要求」与 ⚪ 未验证两种记法分开。接线：03 `<goal tier>`、04 档位声明 + 自验报告、06 DoD 前对账 + 交付单档位行、05 八问不分档、08 PR 档位行 + S 档简版、00 接入片段与案例。**属 §7.2 重大调整（改主链路走法），用户 2026-09-29 拍板。** 建议 1 / 4 / 6 仍未做。
- 历次重大调整通过 `docs(baseline):` commit 记录，可通过 `git log docs/governance/workflow.md docs/governance/workflow/` 追溯
