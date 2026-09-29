# 01 Task Entry — 大任务进入 + 风险判定

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 关联子文档: [docs/governance/workflow/02-pre-flight.md](02-pre-flight.md) / [docs/governance/workflow/03-decomposition.md](03-decomposition.md) / [docs/governance/workflow/04-goal-execution.md](04-goal-execution.md)
> 关联 skill: `risk-judgment`（已 deprecated；详细规则现在本文件 §2.2，设计历史见 [docs/governance/skill-design.md §3.3](../skill-design.md#33-已-deprecated-skill7-个详细设计已迁至-workflow-子文档)）

## 何时读这份文档

任务进入主链路的第一步。Claude 拿到新指令（用户即时指令 / S2todo 节点 / 上游解锁）时，先读本文档完成"识别任务类型 + 是否大任务 + 风险层级"判定。判定后再决定走哪条流程。

## 概览

本文档覆盖 10 步主链路的前两步：§2.1 大任务进入（识别类型 + 是否大任务）+ §2.2 风险判定（5 条触发即高风险）。判定后分流：

- **非大任务** → 跳过 §2.2 §2.3 §2.4，直接进 §2.5 单 goal 执行
- **大任务 + 低风险** → 进 §2.3 节点切入 5 问，无需用户确认
- **大任务 + 高风险** → 停下等用户确认拆解方案后再进 §2.3

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

- 是大任务 → §2.2 风险判定
- 非大任务 → 跳过 §2.2 / [docs/governance/workflow/02-pre-flight.md §2.3](02-pre-flight.md#23-节点切入-5-问pre-flight-check) / [docs/governance/workflow/03-decomposition.md §2.4](03-decomposition.md#24-拆小任务)，直接进 [docs/governance/workflow/04-goal-execution.md §2.5](04-goal-execution.md#25-单个-goal-执行) 单 goal 执行（轻量推进）

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

---

## Cross-references

**上游（我引用谁）**：

- [CLAUDE.md](../../../CLAUDE.md) — 强制红线（风险判定与红线的关系）
- [docs/governance/workflow.md §0](../workflow.md#0-适用前置条件误用防线) — 适用前置（判定任务类型时参考）
- [docs/roadmap/S2.md](../../roadmap/S2.md) — S2todo 节点表（任务来源 + 大节点标记）
- [docs/infrastructure/source-readiness-checklist.md](../../infrastructure/source-readiness-checklist.md) — 数据源 production readiness checklist（条件 4 触及时引用，A6.1.4 新增）

**下游（谁引用我）**：

- [02-pre-flight.md](02-pre-flight.md) — 高风险确认后进入 §2.3 pre-flight 5 问
- [03-decomposition.md](03-decomposition.md) — pre-flight 后进入 §2.4 拆小任务
- [04-goal-execution.md](04-goal-execution.md) — 非大任务直接进 §2.5 单 goal 执行
- `risk-judgment` SKILL — 消费本文档定义的 5 条触发条件输出 `risk_level` + `judgment_reason`
