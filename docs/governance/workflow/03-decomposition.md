# 03 Decomposition — 拆小任务 + `<goal>` XML 模板

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 骨架: [core/02 §3–6](../../../core/02-decompose.md) —— 规则本体以骨架为准，本文件是实例层（含项目参数与历史证据）
> 关联子文档: [docs/governance/workflow/02-pre-flight.md](02-pre-flight.md) / [docs/governance/workflow/04-goal-execution.md](04-goal-execution.md)
> 关联 skill: `goal-decomposition`（已 deprecated；详细规则现在本文件 §2.4，设计历史见 [docs/governance/skill-design.md §3.3](../skill-design.md#33-已-deprecated-skill7-个详细设计已迁至-workflow-子文档)）

## 何时读这份文档

[02-pre-flight.md](02-pre-flight.md) 5 问答完之后开始读，写 `<goal>` XML 时全程对照。Claude 拿到任何"大任务"都不得直接整体执行，必须先按此文档拆解。

## 概览

拆解原则（§2.4.1）+ 小任务拆解标准 5 条（§2.4.2）+ 完整 `<goal>` XML 模板（§2.4.3）+ 拆解产物落地（§2.4.4）+ 用户确认机制（§2.4.5）+ 节点 ≠ 小任务（§2.4.6）。每个小任务用 XML 表达后单独调用 `/goal`。

---

## 2.4 拆小任务

**仅在 §2.1 判定为大任务时执行此节**。

### 2.4.1 基本原则

任何"大任务"**不得直接整体执行**，必须先拆解为可验证、可回滚、边界清晰的小任务。

> 🔴 **拆解表里的操作性数字 = 待核假设，不是待办**（CRED.1.G5 retro 沉淀·2026-09-10）
>
> 写进 goal 表的「跑哪一段 / resume 从哪个断点起 / close 几条 / 跑几次」，是**拆解当天按印象写下的猜测**。
> **收口 goal 开工时必须逐条回到真值源核一遍再执行**：
> - 段落归属 → [`segments.py`](../../../src/committee/segments.py) 的 `members` + [段式跑指南](../../observations/e2e-runs/segmented-e2e-guide.md)
> - 条目能不能关 → **该条目正文自己写的关闭条件**（不是拆解表里的「close N 条」）
>
> **核出不一致时，改的是计划、不是标准**；并把「原计划为什么不对」**写回计划表**（划掉旧数 + 一句理由），不许悄悄改数。
>
> **实证（同一个 goal 里两条计划数字全部落地不成立）**：
> ① 「复用近跑 seg1–8·**只重跑 seg9**」—— 而 `audit_pass_0_5` 属 **seg8**，照做的话该 goal 改的审计**一行都不会执行 = 白跑一次**
> （指南早把这条标成「最容易踩的一处」，拆解时没对上）；
> ② 「**close 4 条**」—— 逐条核关闭条件：1 条早已关、2 条条件明确不满足、1 条够格但剩余项没有去处，**实际 0 条新 close**。
> 照数字执行 = 把没达成的条件当达成，**正是该节点要治的那个病**。
> 出处：[retro CRED-1.G5](../../retro/S2/CRED-1.G5_2026-09-10.md)。
> **同族两条在坑表 §3**（pitfall-scout 节点起步时读的是那张表）：「承重数字的判据必须取被观测系统自己写下的字段」
> + 「空头支票」（账目表写「解决 X 账」落地做不到·**「close N 条」是它的第三例**）→ [09-known-pitfalls.md](09-known-pitfalls.md)。

> 🟡 **检测类改动的收口判据，要写明「那一跑怎么保证碰得上」**（CRED.2.G5 retro should_update·2026-09-24 节点收口 adopt）
>
> 给「新检测 / 新标记 / 新闸门」写收口判据时，若要求「真跑里**该响的响**」，必须同时写明**用什么保证那一跑会碰上目标形态**：
> 选一个已知会触发的起点（如带目标形态的旧断点续跑）/ 指定归档回放为该面的正式证据 / 注入样本。否则一次自然跑批只能证「不乱响」那一半，
> 收口时只能靠用户当场裁定兜底。同理，**「比例在预测内」须给单跑区间**，只给历史聚合值时单跑读数只能说「在历史波动内」。
> **实证**：CRED.2.G5 两条判据都踩了（本跑没有噪音、没有过期出处；预测只有聚合 51.7%）→ 用户当场裁；
> CRED.3.G2 照本条改用「8 月那跑 seg7 续跑」，确定性地碰上目标形态。出处：[retro CRED-2.G5](../../retro/S2/CRED-2.G5_2026-09-24.md) · [retro CRED-3.G2](../../retro/S2/CRED-3.G2_2026-09-24.md)。

每个小任务必须通过单独的 `/goal` 执行，并在结果达成后，才能进入下一个小任务。

**禁止**一次性在同一个 `/goal` 中完成多个阶段、多个模块、多个风险等级不同的改动。

### 2.4.2 小任务拆解标准

每个小任务必须满足：

- **目标单一**：只解决一个明确问题
- **输入清楚**：知道要改什么、看什么、验证什么
- **输出可验收**：能用测试 / 日志 / diff / 运行结果判断是否完成
- **风险可控**：失败后可以回滚或停止，不会影响后续任务
- **边界明确**：不顺手改无关问题，不扩 scope

#### 成本 / 性能优化类节点：先安排一步「最小可证伪实验」（2026-08-11 AG 复盘 adopt）

拆**优化类**节点（省钱 / 提速 / 减 context）时，在昂贵的全链验收之前，
**默认前置一个 goal：用最小成本去证伪前提**——单段 / 单调用级，开销控制在角分级。

**为什么**：优化类节点的前提往往是"某处有重复 / 有浪费"，而这个前提**只在纸面上成立**，
落到调用粒度就可能不成立。前提一垮，后面所有验收预算全是白烧。

**实证（AG 节点）**：原拆解为阶段一 / 阶段二各排了 ≥2 次全链 e2e（共 ≥4 次）。
实际一次 **$0.14 的单段 A/B** 就直接否掉了整个阶段二分支——
八个分析师共用的前缀提到最前面之后，各角色首调命中量**两臂全为 0**，
因为它们是**并行**发出的、缓存要生效必须有先后。
若按原拆解走，会先花掉几美元跑完阶段一验收，再在阶段二发现收益为零。
出处：[ag-prompt-order-ab](../../observations/ag-prompt-order-ab/EVIDENCE.md)、[AG 节点复盘](../../retro/S2/AG_2026-08-11.md)。

**怎么设计这一步**：问自己"这个优化能成立，靠的是哪一条我还没验过的事实？"
然后用最小的真实调用去打它。注意是**证伪**不是**证实**——设计成"如果前提不成立，
这个实验会明确地失败"，而不是"跑一下看看数字好不好看"。

### 2.4.3 `<goal>` XML 模板

每个小任务用以下 XML 结构表达，作为 `/goal` 调用的输入：

```xml
<goal id="<node-id>.<sub-id>" parent_node="<node-id>" risk_level="high|low" tier="M|L">
  <objective>
    本小任务要达成的单一明确结果，一句话。
  </objective>

  <scope>
    <allow>
      <path>facts/cache.py</path>
      <path>tests/test_facts_cache.py</path>
    </allow>
    <forbid>
      <path>facts/router.py</path>
      <reason>路由层不在本 goal 范围；改动需独立 goal</reason>
    </forbid>
  </scope>

  <dependencies>
    <upstream status="done">A6.1.1</upstream>
    <upstream status="done">PR-8a</upstream>
  </dependencies>

  <steps>
    <step n="1">阅读 cache.py 现状与已有 WAL 模式约束</step>
    <step n="2">实现 query_classification 缓存命中率统计</step>
    <step n="3">补 corner case：缓存写入并发 / TTL 边界</step>
  </steps>

  <verification>
    <command>pytest tests/test_facts_cache.py -v</command>
    <command>pytest tests/test_query_classification.py::test_cache_hit_rate</command>
    <smoke>1 single_ticker + 1 macro_event end-to-end</smoke>
  </verification>

  <done_criteria>
    <criterion>所有 corner case 通过</criterion>
    <criterion>命中率统计写入 observation log</criterion>
    <criterion>未破坏 WAL 模式（schema replay 全过）</criterion>
  </done_criteria>

  <stop_conditions>
    <condition>触及 §2.7 任一硬边界 → 立即停</condition>
    <condition>archive replay 失败 → 立即停</condition>
    <condition>DoD 失败 ≥ 3 次 → 升级为重新拆解</condition>
  </stop_conditions>

  <fallback>
    <description>缓存层失败时，query_classification 走 regex / macro_event fallback</description>
    <reference>S2todo §6.1</reference>
  </fallback>
</goal>
```

**字段说明**：

- `id`：goal 全局唯一 ID，格式 `<节点 ID>.<sub-id>`，如 `A6.1.2.1`
- `parent_node`：所属 S2todo 节点
- `risk_level`：复用 [docs/governance/workflow/01-task-entry.md §2.2](01-task-entry.md#22-风险判定5-条触发即高风险) 风险判定结果，驱动后续是否需要用户确认
- `tier`：[01 §2.2.5](01-task-entry.md#225-任务分档s--m--l--2026-09-29-立) 档位。写 XML 的 goal 只会是 M 或 L（S 档不写 XML，整个任务是一个隐式 goal）；只许升不许自己降
- `<scope>`：`allow` 是白名单，`forbid` 是显式黑名单（防"顺手改"）
- `<dependencies>`：上游 goal / 节点；`status="done"` 必须在 [docs/governance/workflow/02-pre-flight.md §2.3](02-pre-flight.md#23-节点切入-5-问pre-flight-check) 第 1 问已确认
- `<steps>`：执行序列，每个 step 应对应 1-N 个 commit
- `<verification>`：自验命令，跑给 [docs/governance/workflow/04-goal-execution.md §2.6](04-goal-execution.md#26-goal-达成自验) 自验环节用
- `<done_criteria>`：DoD 通过的硬条件
- `<stop_conditions>`：强制中断条件（不等同于 done criteria 反义）
- `<fallback>`：来自 [02-pre-flight.md §2.3](02-pre-flight.md#23-节点切入-5-问pre-flight-check) 第 5 问，必填

### 2.4.4 拆解产物落地

- 大任务拆解结果写入 `docs/plans/<node-id>-decomposition.md`，不只在 chat
- 每个 `<goal>` 单独成块，可拷贝粘贴给 `/goal` 调用
- 拆解 markdown 顶部包含：节点 ID、子阶段、依赖图、`<goal>` 列表
- **双读者要求**（[CLAUDE.md Plan/设计文档规范](../../../CLAUDE.md)）：顶部必须含一段**非技术大白话导读**——每个 goal "做什么 / 为什么"，用类比讲、**不出现**代码符号 / 文件名 / schema；`<goal>` 正文保留技术细节（文件 / schema / 节点 / 复用机制）。即"导读看得懂、正文做得出"。

### 2.4.5 用户确认机制（仅高风险）

- **高风险节点**：拆解完成后**停下展示给用户**，等明确 "approve" 或 "调整" 后才进 [docs/governance/workflow/04-goal-execution.md §2.5](04-goal-execution.md#25-单个-goal-执行)
- **低风险节点**：拆解完成后直接进 §2.5，不停下；用户可随时打断
- 拿不准 → **默认按"高风险"处理**，停下问

### 2.4.6 节点 ≠ 小任务

- S2todo 表格中的 A6.1.x / P4.B.x 已经是"节点"级粒度
- 节点 ≠ 小任务：若一个节点能在 10 分钟内验证完成 → 单个 `<goal>`；否则按本节再拆
- 拆解结果作为 decomposition.md 文件落地，不依赖 chat 上下文

### 2.4.7 `<decomposition_input>` / `<decomposition_output>` 包装 schema

`goal-decomposition` 步骤的**完整输入/输出 schema**（消费 [01-task-entry.md §2.2](01-task-entry.md#22-风险判定5-条触发即高风险) 风险判定 + [09-known-pitfalls.md §3.11](09-known-pitfalls.md#311-pitfall-scout-subagent-工作方式) pitfall alerts + [02-pre-flight.md §2.3](02-pre-flight.md#23-节点切入-5-问pre-flight-check) 5 问）：

**输入 schema**：

```xml
<decomposition_input>
  <node_id>A6.1.2</node_id>
  <subphase>S2.1</subphase>
  <risk_level>high|low</risk_level>
  <judgment_reason>...</judgment_reason>
  <pitfall_alerts>
    <!-- 来自 pitfall-scout subagent 的输出，见 §3.11 -->
  </pitfall_alerts>
  <pre_flight_answers>
    <q1_dependencies>...</q1_dependencies>
    <q2_parallel>...</q2_parallel>
    <q3_risk_tier>...</q3_risk_tier>
    <q4_time_budget>...</q4_time_budget>
    <q5_fallback>...</q5_fallback>
  </pre_flight_answers>
  <task_description>...</task_description>
</decomposition_input>
```

**输出 schema**：

```xml
<decomposition_output>
  <node_id>A6.1.2</node_id>
  <decomposition_path>docs/plans/A6.1.2-decomposition.md</decomposition_path>
  <goals>
    <!-- 一个或多个 §2.4.3 定义的 <goal> 元素 -->
    <goal id="A6.1.2.1" parent_node="A6.1.2" risk_level="high">
      <!-- ... 字段同 §2.4.3 ... -->
    </goal>
  </goals>
  <user_confirmation_required>true|false</user_confirmation_required>
</decomposition_output>
```

**字段说明**：

- `risk_level` 直接复用 [01-task-entry.md §2.2](01-task-entry.md#22-风险判定5-条触发即高风险) 的判定结果，驱动 `user_confirmation_required`
- `<pitfall_alerts>` 中的具体 action 必须**进入** `<goal><stop_conditions>`，不能丢
- `<goals>` 是 §2.4.3 定义的 `<goal>` 元素的容器，每个 goal 独立可被 [04-goal-execution.md §2.5](04-goal-execution.md#25-单个-goal-执行) 消费
- `user_confirmation_required=true` → 拆解完成后必须 §2.4.5 停下问

---

## Cross-references

**上游（我引用谁）**：

- [01-task-entry.md](01-task-entry.md) — 风险判定结果（驱动 risk_level 属性 + 用户确认机制）
- [02-pre-flight.md](02-pre-flight.md) — 5 问答案（驱动 dependencies / fallback 等字段）
- [docs/roadmap/S2.md](../../roadmap/S2.md) — 节点定义 + §6 Fallback 路径参考

**下游（谁引用我）**：

- [04-goal-execution.md](04-goal-execution.md) — 单 goal 执行消费 `<goal>` XML 全部字段
- [05-brake-self-check.md](05-brake-self-check.md) — 消费 `<stop_conditions>`
- [06-dod-and-evidence.md](06-dod-and-evidence.md) — 消费 `<verification>` 和 `<done_criteria>`
- `goal-decomposition` SKILL — 产出 `<decomposition_output>` 包含 `<goal>` 列表
