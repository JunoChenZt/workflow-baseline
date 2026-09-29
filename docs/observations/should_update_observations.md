# should_update Observations 累积

> 本文件登记 retrospective-goal / retrospective-node 输出的 `<observe>` 信号。
>
> **累积规则**（per [workflow §2.10.6](../governance/workflow/07-retro-goal.md#2106-observe-累积出口)）：
> 同类信号累积 ≥ 3 次 → 升级为 should_update，重新进入节点级 retro 分流。
>
> 不是任务 backlog（那是 [docs/governance/backlog.md](../governance/backlog.md)）。
>
> 本文件首次建立：2026-05-14（A6.1.1 节点级复盘）

---

## 0. Observation 计数粒度统一规则（2026-05-18 reconcile）

所有 `O-*` observation 计数采用 **sub-goal 粒度**（A6.1.1 / A6.1.2.1 /
A6.1.2.2 / A6.1.2.3 = 各 1 个独立工作周期），**不用 parent-node 粒度**。

理由：
- sub-goal = 一个完整 C 阶段闸门的工作单元（brake/DoD/retro 各一次）；
  parent-node 只在 .3 收口整体回顾，粒度过粗
- 升级触发线 N≥3 用 sub-goal 粒度响应更快、信号更精确
- 跨 observation 混用粒度 → N 升级触发判断失精度（基础设施级问题）
- "parent-node 内密集复发" 信号通过各 entry 的 **密度告警** 字段补充，
  不改主计数（既保精度又不丢"集中爆发"信号）

历史：O-A6.1.2-01 .2 retro 撰写时曾选 parent-node 粒度（commit
ad464a2 / 600e0b0），.3 C.3 准备阶段 reconcile 统一为 sub-goal 粒度。
O-A6.1.1-01 本来就是 sub-goal 粒度，不变。

---

## 1. 当前活跃 observations

### O-A6.1.1-01: "plan 阶段用假设/记忆而非实测数据"（原标题"plan 写约定但未先 grep 现有约束"，2026-05-15 扩展定义）

- **来源**：A6.1.1.1 retro（原定义）+ A6.1.2.1 commit b461165 review（定义扩展时点）
- **信号描述**（扩展后）：plan 阶段需要现有约束 / baseline 数字 / 命名风格等事实输入时，用记忆 / 假设 / 历史引用而非当场实测（grep / 跑 baseline 测试 / Read 现有文件等）→ execution 阶段必偏离 → 必须事后回头修正
  - 子模式 1：plan 约定 role / 路径 / 文件结构 → 未先 grep 现有 lock / 约定（原定义）
  - 子模式 2：plan 引用 baseline 数字 / 测数预期 → 未先跑 baseline 跟现状实测（扩展）
  - 子模式 3：plan 估 import 风格 / 测试组织风格 → 未先 grep 相邻模块约定（扩展）
- **跨节点累积次数**（每节点合记 1 次大事件）：**2**
  - **节点 1 = A6.1.1**：B.1#1 tier lock + tests/ 扁平约定均未 grep（子模式 1，合记 1 次大事件）
  - **节点 2 = A6.1.2.1**：测数 baseline 引用错（retro "229" 当全仓库基线，实际 848；子模式 2）+ builder.py import 路径写 `src.committee.xxx` 未先 grep A6.1.1 现有 `from committee.xxx` 约定（子模式 3）— 合记 1 次大事件
- **触发升级**：跨节点累积 ≥ 3 次（每节点 1 次大事件）→ 升级为 should_update（adopt 进 q2_decomposition checklist 强约束："plan 引用任何现状数据必须当场实测"）
- **当前判断**：N=2，未达升级门槛 1 步；A6.1.2.2 / .3 / A6.1.3 任一节点再发生 1 次"plan 阶段用假设而非实测" → N=3 立即升级
- **元层复现告警**（2026-05-18，commit 894e1d9）：编辑 §9 pending 清单时，凭"上一个是 8 往后加"假设直接写 #10/#11，没回数实际行数 / 没更新 header（实际 10 行却编号 1-8,10,11 跳号 + header stale "8 条"）。**这是在登记 O-A6.1.1-01 升级候选的同一份元工作里复现该模式**。性质："防御机制现场失效" — 比常规复现严重一档（元工作本应是该模式的反思现场，反思现场都防不住 = 反思失效）。处置：**不 bump N**（保持"每节点合记 1 次"规则一致性，N 仍 2），但 A6.1.2.1 retro must_update 强制要求防御机制扩展到**元工作维度**（doc 编辑 / observation 登记 / plan amend），不止主工作（写代码 / 写 plan）。修正自检方式见 [decomposition.md §9 编号自检](../plans/A6.1.2-decomposition.md#9-节点收口-pending-actionsa6123-收口时统一处理10-条)。

### O-A6.1.1-02: "self-audit pass 但 cold review 抓到 🔴/🟡"

- **来源**：A6.1.1.1 + A6.1.1.2 retro
- **信号描述**：brake-self-check 8 问 + DoD 4 步全 pass，但 `/review` 仍抓到 self-audit 漏掉的问题
- **本节点累积次数**：2（A6.1.1.1 沉默 skip + A6.1.1.2 timeout zombie）
- **触发升级**：累积 ≥ 3 次（按 [backlog J 修订触发条件](../governance/backlog.md#j-code-reviewer-skill-设计与落地) 2026-05-14）→ 启动 code-reviewer skill 设计
- **当前判断**：N=2，未达升级门槛；A6.1.2 / A6.1.3 / A6.1.4 是否复现 + 模式稳定性决定

### O-A6.1.1-03: "主动 audit 按新规则抓到自己反模式"

- **来源**：A6.1.1.2 retro
- **信号描述**：§2.7.5 + §2.8.1 新规则落地后，下个 goal 主动 audit 时**自己抓到**反模式（不是事后 /review 抓的），证明规则展开真生效
- **本节点累积次数**：1（A6.1.1.2 主动抓 or-assert 模糊验证模式）
- **触发升级**：累积 ≥ 3 次同类 → 证据更强，可考虑减少对 cold review 的依赖
- **当前判断**：N=1，需更多数据

### O-A6.1.1-04: "断言用 `or` 接受多个结果 = 模糊验证模式"

- **来源**：A6.1.1.2 retro
- **信号描述**：`assert X == A or X == B` / `assert X == A or X is None` 等模式接受多个结果都 pass = 实际未精确验证目标行为，是 §2.7.5 Q5 类型 2 (mock 假 pass) 的近亲
- **本节点累积次数**：1（A6.1.1.2 测试 `Fed 加息周期` 用 `== "Fed" or is None`）
- **触发升级**：累积 ≥ 3 次 → 升级为 should_update，扩展 §2.7.5 类型 2 定义
- **当前判断**：N=1

### O-A6.1.1-05 [架构层 gap，非普通累积 observation]：SKILL.md auto-trigger 机制 0 落地

- **来源**：A6.1.1 节点收口验证（2026-05-14，由 cold review 触发后 Step 1/2 实证）
- **实证 1**：`.claude/settings.json` hooks 段为空（verified — 文件 40 行只含 permissions）→ [skill-design.md §4](../governance/skill-design.md#4-hook-设计) 设计的 3 个 hook (pre-tool-use / post-goal / pre-PR) **0 落地**
- **实证 2**：主 Claude 全节点 **0 次 Read** 任何 `.claude/skills/<name>/SKILL.md` 文件（verified — chat 历史无 Read tool 调用 skills/）
- **实证 3**：9 SKILL.md 中 **7 个普通 skill 节点期 0 触发**（risk-judgment / goal-decomposition / brake-self-check / dod-checklist / retrospective-goal / retrospective-node / pr-template），仅 pitfall-scout (subagent 化 via Task tool) **100% 触发**（1/1 应触发次数）
- **本节点累积次数**：1（但 evidence strength = 整节点 0/7 普通 skill 触发 + hook 0 配置 = 双重实证，**不靠 N 累积**）
- **触发升级**：**不进 N ≥ 3 累积规则** — 作为架构层 gap 直接进 [backlog L](../governance/backlog.md#l-skill-触发机制根本性问题--hook-配置落地)（🔴 P0，A6.1.2 起步前必解决）
- **关联 cold review 抓到 🔴 的归因更新**：
  归因不是简单"规则展开不足"，至少 3 层：
  1. SKILL.md 0 invoke（本条已实证）
  2. 规则展开不够细（A6.1.1 已部分补 §2.7.5 / §2.8.1 / §3.2 共 3 条 must_update）
  3. self-audit 元缺陷（N=2 不足以排除，需独立验证）
  Hook 落地解决 (1)，但 (2)(3) 需要在 backlog L 之后独立验证。
- **当前判断**：N=1 但证据强度极高（双重实证），**跳过累积直接进 backlog L**
- **A6.1.2 持续实证**（2026-05-18，A6.1.2.3 retro 落盘）：A6.1.2 节点 **N=3 sub-goal（.1/.2/.3）全程 0** goal-done-reminder hook 触发（O-pre-01 #1 step6 实证 commit 760fd98）。workflow 纯**用户手动驱动 + 主 Claude 直读 workflow 子文档** works（C 阶段 .1/.2/.3 共 3 次完整跑通：brake 8 问 + DoD 4 步 + retro）。强化 backlog L 🔴 P0 不变：**hook architectural gap 不阻塞工作但持续存在**，手动 workaround works 是关键正面实证（A6.1.3 持续观察是否仍 0 hook）。
- **A6.1.3 持续实证 — 新会话冷启动样本当场登记**（2026-05-18，A6.1.3 task-entry 时即记，不等 .3 收口回填，防跨会话切换丢数据点）：本会话是 A6.1.2 节点收口后的**独立新会话（跨会话冷启动）** = A6.1.2 retro cold review A.Finding 3 标记的"跨会话稳定性关键测试"。**忠实口径（不美化）**：task-entry 阶段无 `[GOAL]` 完成事件，goal-done-reminder hook **本就不应在此阶段触发**——此处实证的**不是** goal-completion hook 行为，而是**跨会话冷启动下"用户手动驱动 + 主 Claude 直读 workflow 子文档"机制本身仍 works**（新会话 0 上下文继承，仍正确走完 task-entry：Read pre-flight 6 文档 + §2.2 风险判定 + pitfall-scout subagent 隔离 + §2.3 5 问 + §2.4 拆解 + §2.4.5 high-risk 停下确认）= A.Finding 3 跨会话稳定性的**首个正面数据点（task-entry 范围）**。真正的 goal-completion hook=0 数据在 A6.1.3.1/.2/.3 各 `[GOAL]` 完成时累积，.3 step 6(b) 汇总。A6.1.3 全程作为 backlog L 持续 observe 窗口。
- **A6.1.3 会话 N+1 观察 — retro 自动捕获 vs 人工沉淀 mismatch（用户 2026-05-19 提出，A6.1.3.2 step0 期间）**：用户询问 retro 是否自动记录 → 揭示 **workflow 隐式假设（retro 依赖人工沉淀，三档分流靠 .3 节点 retro 手动消费）与用户预期（surface 事件自动捕获、不靠人记）之间存在 mismatch**。本会话具体触发证据：用户在"放行进 DoD"时主动要求"提前 pin 下来，免得 .3 retro 时忘"（§9 #3/#4/#5 = 用户手动补的防丢机制，正是 mismatch 的现场补偿）。**这深化 backlog L（2026-05-19 根因修正后）**：L 根因经本轮对话用户确认 = **Cursor Claude CLI runtime 无 hook 能力**（非旧表述"VS Code 扩展 additionalContext 注入失效"，后者已 supersede）。故 workflow 设计前提 = 0 hook，人工沉淀设计本身有 UX 失配（用户须手动 pin 才不丢 = 防御负担转嫁用户）。L 解决空间 (a) 接受约束加强人工纪律 / (b) 切官方 Claude Code（25+ hook，可做自动 retro queue）/ (c) 等 Cursor 提供 hook；自动 retro queue（brake-hit/swap-defer/surface → 自动入候选队列）仅 (b)/(c) 可行。详 [backlog L 修订史](../governance/backlog.md#l-skill-触发机制根本性问题--hook-配置落地)。随 L 跟踪（非独立 N 累积，L 架构 gap 直接进 backlog 不走 N≥3）。
- **runtime-premise 元观察（用户 2026-05-19 提出 + 主 Claude 照实认）**：本会话前几轮顺着"backlog L 架构 gap / hook=0"语境推演，**未先问"跑在什么 runtime"**。若一开始对齐 runtime（Cursor CLI 无 hook），"retro 是否自动记录"本可直接答"你的环境根本没有 hook，必然不会自动记录"，省掉绕圈 + 避免在"VS Code 扩展有 hook 但 additionalContext 不注入"的**错误前提**上推演（2026-05-14 旧发现即此错误前提产物）。**教训**：workflow / 工具机制讨论时，**runtime 假设须先对齐**（runtime 决定 hook/skill/注入能力的有无），否则易在错误前提下推演。这是 O-A6.1.1-01"凭假设而非实测"在**元层（讨论前提）**的延伸 —— runtime 也是一种须先实证对齐的"现状事实"。N=1（本会话首次系统识别），随 L 跟踪 + .3 retro 评估是否升 should_update（pre-flight §2.3 加"runtime/工具能力前提对齐"候选，关联 backlog I 类 governance）。
- **🔵 hook 二次实证翻案（2026-05-19b 本会话，A6.1.3 接手后第一动作，handoff 明确要求记）**：runtime 从 Cursor CLI → **官方 Claude Code（25+ lifecycle hook）**。本会话 **HOOK-TEST 实证**：`.claude/settings.json` 已配 3 hook（`task_completed_to_pending.py` / `pending_to_context.py`×2）；`[GOAL]` task 标 completed → TaskCompleted hook 写 `.claude/.state/pending_brake_check.jsonl` → UserPromptSubmit/SessionStart 读队列注入 additionalContext **全链路实测通过**。→ **backlog L 解决空间 (b)（切官方 Claude Code 解锁自动 retro queue）= live 验证正向，hook≠0**。修订史链：2026-05-14"VS Code 不注入" → 2026-05-19a"Cursor CLI 0 hook" → **2026-05-19b 官方 Claude Code 实证 hook≠0 可用**（前两版均"未先实证 runtime 即推断"，本版当场实证 trust 本版，[[project-g3-env]] memory 已同步翻案）。**双层防御现状**：hook 程序层（已验证可用）+ CLAUDE.md"Skill 触发强制规则"语义层（主 Claude 直读 workflow 子文档），两层独立非主备；本会话核对后 workflow 仍语义层驱动为主（hook 注入与语义层执行不冲突，hook 是兜底加强非替代）。**对 O-A6.1.1-05 本体的影响**：实证 3"7 普通 skill 0 触发"不受影响（那是 SKILL.md invoke 问题非 hook）；实证 1"hooks 段为空"**已 stale**（现有 3 hook 且可用）→ 本 observation 的"架构层 gap"性质从"hook 0 落地"收窄为"SKILL.md auto-invoke 0（仍开放）+ hook 已落地可用（gap 已闭此半）"。backlog L 据此可推进 (b) 落地评估（非本节点 scope，节点收口 retro 评估）。
- **Self-correction 翻案**（append 2026-05-19，原观察记录不改，保审计链）：上方"实证 1 hooks 段为空 → 3 hook 0 落地""持续 0 hook 触发""backlog L 🔴 P0 不变"的根因归属**已翻案**。真因非"架构层 gap 不可修复"，而是两个独立 bug：(a) Claude Code v2.1.19+ TodoWrite→TaskCreate/TaskUpdate API 改名，旧 `PostToolUse→TodoWrite` matcher 永不命中；(b) 输出缺 `hookEventName` 字段。路径 D 重写（`TaskCompleted` → pending JSONL → `UserPromptSubmit`/`SessionStart` 注入）全 7 case 验证通过，hook 注入在当前环境**可用**。**[backlog L](../governance/backlog.md#l-skill-触发机制根本性问题--hook-配置落地) 已关闭（🔴→✅）**，三层根因 + 方法论修正见该条目（PR #117）。本观察的"双重实证（0/7 skill + hook 0 配置）"中 hook 部分不再成立；SKILL.md 0 invoke 部分（归因 1/2/3 的 1）仍是事实但已由路径 D 程序层 + CLAUDE.md 语义层双层覆盖。归因 (2)(3)（规则展开 / self-audit 元缺陷）与本翻案无关，仍待独立验证。**O-A6.1.1-05 状态：hook gap 部分 resolved，不再"持续 observe hook=0"；A6.1.3 观察点改为"路径 D hook 是否在新会话冷启动稳定触发"**。

### O-A6.1.2-01: "实现阶段对 plan 模糊处自行解读，未回查 plan 明文 / 未回头补 plan"

- **来源**：A6.1.2.1 commit b461165 brake-self-check Q5 自审发现（2026-05-15）
- **信号描述**：实现阶段遇到 plan 模糊 / 推论可两种解读时，自行选一种解读推进，未停下回查 plan 明文是否支持此解读 / 未回头给 plan 补明文。
  - 与 O-A6.1.1-01 是**对偶问题**，不能合并：
    - **O-A6.1.1-01**：plan 阶段用假设/记忆而非当场实测数据（防御点：plan 前 grep / 跑 baseline 实测）
    - **O-A6.1.2-01**：实现阶段对 plan 模糊处自行解读，未回查 plan 明文（防御点：实现前回查 plan + 模糊处停下回头补 plan 明文）
- **本节点触发证据**：A6.1.2.1 step 4 plan 写"内部 dispatcher 仅占位，真正多源调度在 .2"，verification smoke 字面要求"sources 非空 → quality_flag != 'minimal'"。我自行推论 "dispatcher 占位 ⇒ quality_flag 也占位 ⇒ 实现写死 'ok' 字面量"，**这步推论 plan 未明文允许**。`builder.py` 主路径 `quality_flag="ok"` + `test_normal_path_returns_ok_placeholder` 断言 `== "ok"` 与 plan 字面要求 `!= "minimal"` 形成 gap。
- **跨节点累积次数**（**sub-goal 粒度，与 O-A6.1.1-01 统一**，2026-05-18 reconcile，见 §0 规则）：**2**
  - **A6.1.2.1**（sub-goal，1 次）：子实例 = dispatcher 占位 → quality_flag 占位 plan 暗含推论（commit 27a5b93 回填）+ DoD §2.8.3 援引 A6.1.1.1 commit body precedent 未回查 workflow §2.8.3 明文（同 sub-goal 内 2 子实例合记 1 次）
  - **A6.1.2.2**（sub-goal，1 次）：子实例 = step 2 timeout 来源 plan 未明文 Gap4（Read .1 builder L10-12 实证，不自行解读 → 用户裁决，commit 58b6916）+ step 8 partial-success quality_flag plan 4 处自相矛盾（不自行裁决 → 用户裁决，commit 0a2a70c）（同 sub-goal 内 2 子实例合记 1 次）
- **密度告警**：A6.1.2 parent 内 **2/2 sub-goal 触发（100% 复发率）**，远高于平均跨节点复发率 —— "plan 模糊/矛盾处自行解读"模式在 A6.1.2 期间**集中爆发**，防御点尚未充分内化（retro must address；不改主 N 计数，作额外维度信号）
- **触发升级**：sub-goal 粒度累积 ≥ 3 次 → 升级 should_update（adopt 进 q4_goal_execution checklist："实现遇 plan 模糊/矛盾处必须停下回头补 plan 明文，不自行推论"）
- **当前判断**：**N=2 维持**（.3 C.3 审视：A6.1.2.3 step 0-7 **0 次"plan 模糊处自行解读"** — step 0 grep 真实路径/step 7 cat 实证/step 0.5 方式Y amend/§9#1 实测/粒度 reconcile 用户裁决，全防御 held）。**复发率 100%（.1+.2 sub-goal 2/2）→ 本节点末 50%（.3 sub-goal 1/1 防御 held）**。判定：防御点跨 4 sub-goal 内化的**"进行时"信号非"已完成"结论** —— **A6.1.3 task entry 是关键测试**（真实数据源接入产生新一批 plan 模糊处，能否维持 .3 防御 held 决定 N=2 维持 vs 升级）。不升级不降级，继续 observe（A6.1.3 验证，关联 backlog H）
- **正面执行数据点 inventory（A6.1.3 期间，用户 pin，step8 retro 必一次性归位防漏 — 先列 raw 再分析 pattern）**：本节点"防御点正面执行"（拒绝接受表面值 / 二次实证后才执行 / 透明登记非降标准）累积 **5 个**：
  1. **test_hook.py:79 残留 surface** —— 拒绝含糊"清理"，明确 surface 残留
  2. **last_completed_goals.json 处置** —— 拒绝伪造 commit message
  3. **C5 误打包 `reset --soft` + 透明报告** —— 误操作不掩盖
  4. **grep 假阴性二次实证** —— `**bold**` 干扰 regex，拒绝接受 grep 表面 0 命中
  5. **17/15 数字 vs Claude 自报 18（2026-05-19，本轮新增，用户 pin）** —— 用户执行决策前先实证 ledger（P=16→Q=17），Claude 自报 18 算错被纠正、复核采纳。**维度扩展**：前 4 个纠正对象 = 工具输出/命令结果；本条 = **Claude 自身陈述/算术** → O-A6.1.2-01 防御覆盖从"工具输出须 verify"扩展到"Claude 自报数字/状态也须 verify"。详 [backlog Q 透明纠错登记](../governance/backlog.md#q-用户-query-反馈引导通路缺失后续前端同步修改)
  - **判别准则不变**（O-A6.1.1-01）：`[改断言/删 case/放松 = 降标准]` vs `[拒表面值+二次实证+透明登记 = 正面防御]`。5 个均后者
  - step8 retro 据此 inventory 分析 pattern（**先列 raw 再分析，不边写边漏** — 用户 pin）

### O-A6.1.2-02: "high-risk node 条件 6 对全部 sub-goal 恒触发"

> ⏭️ **2026-07-27 结案（用户裁决 · backlog 条目 I 任务 3）**：升级落地 A/B 选项 **不做** —— 用户裁 **选项 A=直接关掉·不加话·不改 §2.10.1 的 6 条触发条件**。理由：下方 self-correction 已判此发现"发现性弱"（收口 sub-goal retro 偏薄本可预期）；现有 [§2.10.4](../governance/workflow/07-retro-goal.md#2104-retro-质量门槛数量约束)「must_update=0 正常 / trivial 可 skip」已覆盖选项 A 想说的；选项 B（改条件 6 为复合）过度工程；信号从未被系统跟踪、两月无人 miss。**6 条触发条件不动**。下方为 point-in-time 记录，正文不改。

- **来源**：A6.1.2.1 retro（C.3 retro 6 条触发评估，2026-05-18）
- **信号描述**：节点级 high-risk 一次判定（§2.2）→ retro 触发条件 6 对该节点全部 sub-goal 恒为真，等于每个 sub-goal 必跑 retro。A6.1.2.1 retro 命中 4/6（2/3/4/6），频次偏高但有实质内容（非形式空跑）。
- **跨节点累积次数**：**3（N≥3 升级线达成，已闭环升级 should_update）**（数据点 1 = A6.1.2.1 / 2 = A6.1.2.2 / 3 = A6.1.2.3 retro）
- **数据点对比**：
  - 数据点 1（A6.1.2.1，实现 sub-goal）：命中 **4 条**（2/3/4/6），must_update 0，实质丰富（Q5 surface 链 + cold review 4 findings）
  - 数据点 2（A6.1.2.2，实现 sub-goal）：命中 **4 条**（2/3/4/6），must_update 0，实质丰富（timeout overclaim 顶住用户建议 + partial 4 处矛盾 + step 11 REPL 实证）
  - 数据点 3（A6.1.2.3，**收口 sub-goal**）：命中 **2 条（4/6）**，must_update 0，实质丰富（O-A6.1.2-02 闭环 + 粒度 reconcile + archive 双覆盖）
  - **闭环结论**：.1/.2（实现 sub-goal，有 plan/pitfall surface → 触发 2/3）vs .3（收口 sub-goal，无新实现 → 2/3 天然不触发，仅结构性 4/6）→ **sub-goal 性质（实现 vs 收口）主导 retro 命中数**，"high-risk node 恒 4 条"**被证伪**
- **升级**：**N=3 已升级 should_update**（O-A6.1.2-02 升级落地：选项 A 推荐[workflow §2.10 加注解，条件 6 收口 sub-goal 单触发可简化 retro，不改 6 条] + 选项 B 备选[条件 6 改"high-risk + ≥1 条 2/3"复合]；N=1 节点数据不支撑改触发条件，未来 reviewer 据 ≥2 节点定。→ backlog/governance 跟踪）
- **当前判断**：闭环（用户预设升级机制兑现）。整体回顾 + governance PR 时落地选项 A/B
- **self-correction（cold review A.Finding 2，2026-05-18 node-level /review）**：升级闭环的发现性弱，勿过度表述 ——
  1. **结论可预期**："实现 sub-goal 有 plan/pitfall surface → 命中 2/3；收口 sub-goal 无新实现 → 不命中" 在 plan 拆 3 goal（实现/实现/收口）时即可推演，机制只是把已知结构复述了一遍，非机制驱动的新认知
  2. **升级动作的循环依赖**：升级因"用户预设 N≥3 即升级"而触发（时间到点），非"发现迫使升级"；表述应为"预设升级机制按期兑现/执行一次"，不是"机制驱动了升级"
  3. **保留有效性**：触发线 N=3 客观达成、升级动作本身有效（选项 A/B 待 ≥2 节点定）—— 降级的是**认知层表述**，非升级决策本身

### O-A6.1.2-03 [候选]: "QualityFlag 三档不覆盖 out_of_scope 语义"

- **来源**：A6.1.2.2 期间 Read S2.md §5.3 FM-pipeline.1 "非个股 query 不投票" surface（2026-05-18，S2.md alignment 反思校准点 2）
- **信号描述**：当前 QualityFlag（ok / degraded / minimal）三档都是"试着拉数据的不同质量"，没有"这个 query 根本不该跑"的语义档位（OUT_OF_SCOPE / UNSUPPORTED）
- **触发**：未来 A6.1.1 扩 query_type / A6.1.3 / FM-pipeline.1 接入时若引入 OUT_OF_SCOPE 类型，A6.1.2 fallback 路径 + QualityFlag 可能需扩
- **当前判断**：A6.1.1 实际 **2 类型**（SINGLE_TICKER / MACRO_EVENT，非 5 类型 — 用户口述"5类型"实指 roadmap §21.1 "5种类型化"哲学承诺 / backlog G 未落地扩展，非 A6.1.1 现 enum；按 O-A6.1.1-01 防御登记实际值不传播未实证口述）。2 类型均不含 out_of_scope，暂无紧迫性
- **跨节点累积次数**：N=1（本节点首次系统识别）
- **升级触发**：FM-pipeline.1（S2.3）实施时若发现 A6.1.2 schema 真不够用 → 升级 should_update + amend QualityFlag 定义；或 backlog G（QueryType 扩 5 类）落地时若含 out_of_scope 类型 → 同步评估

### O-A6.1.2-04 [候选]: "用户建议的设计也可能踩 known pitfall，需顶住用户拍板优先 known pitfall + 实证"

- **来源**：A6.1.2.2 step 11 outer wait_for surface（2026-05-18）
- **信号描述**：用户拍板的设计若邻近 known pitfall（pitfall #3 §3.2 等），不因"用户已拍"放过 —— REPL 实证 + surface 限制，让 known pitfall + 工程实证决定，非"用户说了算"。本会话 surface 演进轨迹：plan 模糊 → plan 矛盾 → plan 缺顶层 → **用户建议本身**（step 11 outer wait_for 注释 overclaim "防 gather 内部异常卡死"，实际防不了吞 cancel 协程）
- **source of truth ranking**（本节点实战确立）：工程实证 + known pitfall > 用户拍板 > plan 明文 > plan 暗含
- **跨节点累积次数**：N=1（step 11 首次"顶住用户建议 because known pitfall"）
- **触发升级**：≥ 2 次（未来 goal 再现"顶住用户建议 because known pitfall + 实证"）→ 升级 should_update，明文化 source-of-truth ranking 进治理 ground rule（brake-self-check 解释或 §2.7 补注）
- **当前判断**：N=1，原 retro must_update 候选，按 N<3 规则 + [feedback-decision-self-check] "单次坑 observe ≥2~3 再治理文档" + A6.1.2.1 retro 自修正 1→0 先例 → 降为 observe（非过早形式化）

### O-A6.1.2-05 [候选]: "基础设施级精度问题当场 reconcile 不延后（vs 包装成治理流程延期）"

- **来源**：A6.1.2.3 C.3 准备阶段 O-A6.1.1-01/O-A6.1.2-01 粒度 reconcile（2026-05-18，commit 173ce4f）
- **信号描述**：跨 observation 计数粒度冲突（sub-goal vs parent-node）发现时，**当场 5 分钟决策 + edit 统一**（加 §0 规则 + 密度告警保留信号），**不延后到 should_update governance 跟踪**。判据：基础设施级精度问题（计数器粒度歧义污染未来 N 升级触发判断），越早 reconcile 代价越低；延后 = 把 5 分钟决策包装成治理流程（元层化轻度复发）。区别于需 PR/版本化的真 should_update。
- **跨节点累积次数**：N=1（本会话首次"当场 reconcile 不延后"）
- **触发升级**：≥ 2 次"基础设施级精度问题当场修 vs 延后"判断点 → 明文化进 should_update_observations.md §4 维护协议（"何时当场 reconcile vs 何时延 should_update"判据）
- **当前判断**：N=1，technique 已记 A6.1.2.3 retro XML 沉淀；observe 累积等 A6.1.3+ 再现

### O-A6.1.2-pre-01 [等待实证 observation, 提前登记]

- **节点**: A6.1.2 (尚未开始)
- **登记时点**: 2026-05-14 (skill-system-refactor 完成时,提前登记)
- **待实证项**:
  1. **goal-done-reminder hook 实际触发率** — 期望 ≥ 90%；失败应对：检查 [GOAL] 前缀使用一致性
  2. **触发后主 Claude 真 invoke 率** — 期望 ≥ 70%（hook 提醒后真跑 brake/DoD/retro）；失败应对：加强 CLAUDE.md 规则
  3. **cold review 抓到的 🔴 数量** — 期望 < 1 次 (vs A6.1.1 的 2 次)；失败应对：skill invoke 不够,接受 cold review 必做 (backlog J 升级)
  4. **verification-report subagent 实际 invoke 率** — 期望 = **仅 S2.1 末节点必 invoke**（A6.1.2 是 S2.1 中间节点 → 0 invoke 符合设计**非失败**；原措辞"≥1 次 A6.1.2 末或 S2.1 子阶段末"自相矛盾，2026-05-18 A6.1.2.3 retro 修正）；失败应对：S2.1 末节点仍 0 invoke 才触发 verification-report 与 7 deprecated skill 一并重新评估
  5. **`差不多_moments` 中文 XML tag 实际编码问题** — 期望 0 问题；失败应对：改英文 tag
- **评估时点**: A6.1.2 节点级 retro 时核对以上 5 项

- **实证结果**（A6.1.2.3 step 6 登记，2026-05-18，**忠实记录含 gap 不美化**）：
  1. **goal-done-reminder hook 触发率**：期望 ≥90% → **实测 0**（重大 expectation miss）。证据：全会话 0 个 `<system-reminder>` 含 goal-done brake/DoD/retro 注入内容；workflow 全程由**用户手动驱动 + 主 Claude 直读 workflow 子文档**执行，非 hook 注入。根因 = VS Code 扩展 hook 只执行 command 不注入 additionalContext（CLAUDE.md "Skill 触发强制规则" + O-A6.1.1-05 + backlog L 已 codify，本会话**实证确认该架构 gap**）。**（2026-05-19b 翻案，史实保留 O-A6.1.1-01 anti-stale-truth-source）**：此根因表述属 Cursor-CLI runtime 期。runtime 已切官方 Claude Code，HOOK-TEST 实证 hook≠0 全链路可用 → 见 O-A6.1.1-05 "hook 二次实证翻案" bullet（权威翻案记录，本 #1 不改史只加指针）。
  2. **触发后真 invoke 率**：hook=0 故"hook 触发后"比率**不适用**。但 brake/DoD/retro **实际跑了**：A6.1.2.1 + A6.1.2.2 各 1 完整 C 阶段（C.1 brake 8 问 + C.2 DoD 4 步 + C.3 retro）+ A6.1.2.3 进行中。证据：commit 27a5b93/b6eab25（.1 C 收口）+ .2 C 阶段 chat + commit。非 hook 驱动下"每个 [GOAL] 真跑完整 C"= 100%，但驱动源 = 用户手动 + workflow 子文档直读。
  3. **cold review 🔴 数**：期望 <1（vs A6.1.1 2 🔴）→ **实测 0 🔴** ✓ **达标**。证据：A6.1.2.1 `/review` cold review 抓 4 finding 全 🟡（注解约定 / QualityFlag overlap / __post_init__ docstring / payload TODO），0 🔴；commit a291383 §9 #5-8。
  4. **verification-report invoke**：期望 ≥1（A6.1.2 末或 S2.1 子阶段末）→ **实测 0**。但 A6.1.2 **非 S2.1 末节点**，设计上 verification-report 在 S2.1 子阶段末节点才触发 → 0 invoke **符合设计非失败**。**期望措辞本身有 bug**（"≥1 次 A6.1.2 末" 应为 "仅 S2.1 末节点必 invoke"）→ **✅ 已修正（本 commit，§6.1 PR 前 O-pre-01 #4）**：item 4 期望改为"仅 S2.1 末节点必 invoke，A6.1.2 中间节点 0 invoke 符合设计"。证据：A6.1.2 是 S2.1 中间节点；0 个 verification-report Task 调用（chat 历史）。
  5. **中文 XML tag 编码**：期望 0 问题 → **实测 0** ✓ **达标**。证据：decomposition.md 全程 `<goal>/<step>/<scope>` XML tag + 中文 UTF-8 正常；本会话多次 Read decomposition.md 中文无乱码（控制台 GBK 乱码是 Windows stdout 显示问题非文件问题，已多次验证 Read 文件内容正常）。
- **§9 #4（O-A6.1.1-01 .3 升级候选统计）**：.3 期间"用假设而非实测"= **0 新 miss**（step 0 grep 主动抓到 decomposition `_archives/*.json` 路径简写假设 → 修正全路径，**防御 held 非 miss**）。O-A6.1.1-01 N 不变（parent-node 粒度 A6.1.2 whole = 1 event 含 4 子实例，.3 step 0 grep 防御成功非新子实例）。
- **5 项汇总**：达标 2（#3 cold review 0🔴 / #5 编码 0）；重大 miss 1（#1 hook=0 → backlog L 实证确认架构 gap）；不适用 1（#2 hook=0 比率 N/A 但 brake/DoD/retro 实跑了）；期望措辞 bug 1（#4 期望本身错需修正）。

### O-A6.1.3-01 [load-bearing 观察口径 lock]：dispatcher 结构化 observation 口径（喂 backlog P）

- **来源**：A6.1.3.3 .3-s2 step6（用户 2026-05-19 定口径，A6.1.3.2 review 稳定性讨论收敛）
- **性质**：**非累积 observation，是观察口径 lock**——锁定"未来生产运行时按此 schema 收集数据"，使 [backlog P](../governance/backlog.md#p-facts-cache-限流失效降级语义升级-defer-until-data) 触发条件 falsifiable。N 不适用。
- **6.A 结构化口径**（真值源 = [decomposition A6.1.3.3 step6](../plans/A6.1.3-decomposition.md)，此处不重复 schema 全文，引用为准 O-A6.1.1-01 单一真值源）：每次 dispatcher 调用 append-only JSON line（timestamp / source / status / error_class / source_duration_ms / dispatcher_total_ms / cache_state_at_degraded）；error_class taxonomy = rate_limit_429 / network_timeout / not_found / endpoint_failure / parse_error / null；最少观察窗 ≥1 周连续（工作日+周末覆盖 Yahoo 时段差）；输出 (a)-(e) 喂 backlog P 触发 (a)(b)(c)。
- **⚠️ scope 诚实口径（O-A6.1.1-01 不美化）**：本 step6 = **口径登记，非 logger 落地**。结构化 JSON-line logger **实现 = OUT OF .3 scope**（.3 scope.forbid 锁 builder.py，dispatcher instrumentation 须改 builder.py）+ ≥1 周数据窗 **须生产部署**（.3 内不可得）。故现状 = **口径锁定 + 数据收集条件明文 + 触发 wired，实际数据 0**。logger 落地 = 节点收口后独立小节点 / backlog（不在 A6.1.3）。**禁说"observation 已启动收集数据"——准确说法是"observation 口径已锁，待生产部署 + logger 落地后按此收集"**。
- **关联**：[[backlog-P]] 触发数据源 / decomposition §9 #10（yfinance source_duration_ms load-bearing）/ s1→s2 micro-check (B)

### O-A6.1.3-02：A6.1.3.3 .3-s1/s2 实证发现合并（yfinance α→β + Q4 nuance + §9#9 口径）

- **来源**：A6.1.3.3 .3-s1（真实探针）+ .3-s2 step3（Q4 逐源实证），2026-05-19
- **信号描述（忠实含 gap）**：
  1. **yfinance α→β SUSPECT**：A6.1.3.2 M4 锁 yfinance=α（download timeout= 让 thread ~T 终止）。.3-s1 探针实测 `download(timeout=8)` **跑 30021ms 返 empty**（Yahoo block 疑似）→ α 从 CONFIRMED 降 SUSPECT（N=1+empty 混淆**不过度断言 α 必假**，O-A6.1.1-01）。docstring α 措辞修正 = OUT OF .3 scope，defer 节点收口后 follow-up（§9 #10）
  2. **Q4 预判被实证翻（O-A6.1.2-01 payoff）**：预判"4 源 read-only 无写副作用"→ 逐源实证 **yfinance 确写磁盘 tz-cache SQLite**（peewee ACID）；akshare 88 行纯 requests.get 实证无写盘。Q4 仍🟢（ACID + 幂等内部 cache 非我方数据），但预判不完整被实证纠正（§9 #12）
  3. **§9#9 gap 闭合口径如实**：.3-s1 e2e_real 闭 #9 但 yfinance shape=env 实证 / akshare shape=仅 doc-level（本 env 代理挡 eastmoney）→ 禁说"全闭"（§9 #11）
- **计数**：A6.1.3.3 sub-goal 粒度（§0 规则），关联 O-A6.1.2-01（.3 防御 held：3 处均 surface+方式Y amend 未自行解读 → A6.1.3 关键测试**正向**，喂 O-A6.1.2-01 N=2 维持判断）、O-A6.1.1-01（实证翻预判正面 payoff）
- **决策影响**：均非升级项，喂 backlog P / §9 / 节点 retro；yfinance α SUSPECT + 30s + 写盘 = 三独立信号共同强化 [backlog P] yfinance watch + 节点收口后 docstring follow-up

### O-A6.1.3-03：节点级 cold review N=2 + "一次 cold review 不穷尽同类红线"（backlog J）

- **来源**：A6.1.3.3 .3-s3 step7 独立 subagent cold review（2026-05-19）
- **provenance**：warm-cold（独立 general-purpose subagent 0-context + 独立推理链，但同 model+session）= backlog J 三档 warm-cold 偏强端，**非** cross-session/cross-model 双盲（O-A6.1.1-01 不冒充）
- **数据点 1（backlog J "≥3 Finding 稳定产出"）**：A6.1.2 节点级 N=1（1🟡/2🟢）→ A6.1.3 节点级 **N=2（6 Finding：2🔴/2🟡/2🟢）≥3 ✓**。两次均稳定产出 ≥3，**但 provenance 都非 cross-session 双盲**（A6.1.2=用户/同会话档；A6.1.3=subagent warm-cold）→ backlog J §2.11 落地规则须注明"≥3 稳定但弱 provenance；强 provenance(cross-session)样本仍 N=0"
- **数据点 2（关键，O-A6.1.1-02 关联）**：**F1/F2 = 原 Finding 1 的同类北极星 bug 延伸**。A6.1.3.2 self-review 已注意到 yfinance 假阳性但**合理化为"残留 .3 observe"**；用户当时把 Finding 1 scope 限到"静默默认"。cold review 实证它普通英文句就触发 → **"一次 review（A6.1.3.2 self-review）+ 一次窄 scope 裁决不足以穷尽同类红线 bug，需 N≥2 review 才 surface 同类多实例"**。直接喂 backlog J "**N=2 是否充分**"问题 —— 本例证明 N=1（仅 self-review）会漏同类红线，支持 cold review 机制必要性（非"self-audit 够了"）
- **处置**：F1/F2/F4 用户裁决现在修（方式 Y .3 scope-amend，§9 #14）；F3 defer；连带架构 gap → backlog Q。本 observation 喂 backlog J §2.11 落地（step8 retro 评估，N=2 跨节点 + provenance 对比）
- **计数**：A6.1.3.3 sub-goal 粒度；与 O-A6.1.1-02（self-audit pass / cold 抓）合流证据——F1/F2 是该模式又一实例（self 合理化 → cold 翻）
- **backlog J N=2 reviewer 首测点（用户 2026-05-19 pin）**：未来 N=2+ cold review **第一个要测**："reviewer 在接受 Claude **任何数字/状态陈述**前是否独立 verify？" 判据：若 reviewer 直接接受 Claude 自报数字（如本轮"18/15"未经核对）→ **review 质量打折，纪律不及格**。依据 = O-A6.1.2-01 第 5 数据点（Claude 自报算错，用户二次实证拦截）—— 证明"接受 Claude 表面陈述"是真实 review 失效面，非假想。backlog J §2.11 落地规则须含此首测点

### O-S2.2-01: "PR TODO 空置跨多个 PR/cold review 无人发现"

- **来源**：S2.2-gate root cause analysis（2026-05-26）
- **信号描述**：economist `ROLE_OVERRIDE = ""`（空字符串）自 PR-7 起空置，经过 PR-7/PR-8a/PR-8b/F-vis/E-class 五个 PR 和多次 cold review 全部未发现，直到 S2.2-gate 实跑暴露 B3 reject。根因：code-level review 看"文件存在 + import 正确"就 pass，不检查"文件内容是否有效"；behavior-level validation（实跑）才能抓到
- **关联**：O-A6.1.1-02（self-audit pass / cold review 抓）同类模式——但本例更严重：连 cold review 也没抓到（O-A6.1.1-02 是 cold review 抓到了，本例是 gate 实跑才抓到）
- **处置**：observe (N=1)。已通过 [S2.md §4.6 Agent 现状审视](../roadmap/S2.md)协议系统化防护。若 S2.3 再次出现同类空置 → N=2 升级
- **计数**：S2.2-gate 粒度（独立工作周期）

### O-S2.2-02: "cold review 在 code-level vs behavior-level 存在盲区"

- **来源**：S2.2-gate root cause analysis（2026-05-26）
- **信号描述**：三个系统性问题（REF# 注入漏、historian raw guidance 不足、economist stub）均通过了 W1-W3 期间的 code-level review，只有 behavior-level validation（端到端实跑 + archive 分析）才暴露。cold review 的 provenance 排序（[§2.11.7](../governance/workflow/08-retro-node-and-pr.md)）未区分 code-level 和 behavior-level 两种 review 维度
- **关联**：O-A6.1.1-02 升级版——从"self-audit 漏 / cold review 抓"升级为"cold review 也漏 / gate 实跑才抓"，防线层级更高
- **处置**：observe (N=1)。S2.3 gate 时评估 cold review 是否需要增加"behavior-level 抽样检查"环节（跑 1 个 query 看输出而非只看代码）
- **计数**：S2.2-gate 粒度

### O-WS-01: "风险判定基于实现路径假设时应 spike 后 finalize"

- **来源**：WS.0-WS.3 retro（2026-05-27），条件 6 命中
- **信号描述**：拆解阶段将 web search 判 HIGH risk（条件 1：修改 `_invoke_json` 核心路径 = DONE node runtime 契约）。WS.0 spike 发现 Anthropic `web_search` 是 server-side single invoke，实现走纯加法路径（新增 `_invoke_json_with_search` + if/else 分发），核心路径零变更，实际风险 LOW。拆解阶段的 HIGH 判定基于"需改核心路径"的假设，而非实证 — 是 O-A6.1.1-01（plan 阶段用假设而非实测）在风险判定维度的延伸。
- **教训**：高风险判定若基于"实现路径假设"（非已知约束），应标注 PROVISIONAL-HIGH，spike 后 finalize。不在 spike 前 lock。
- **跨节点累积次数**：N=1（首次系统识别）
- **触发升级**：≥ 3 次"spike 后风险判定大幅降级" → 升级 should_update，明文化进 §2.2 风险判定补注
- **当前判断**：N=1，observe

### O-FM-spec-01: "修 X 埋 X" — 治理类修动作里复发同类元缺陷（**N=3 已升级 should_update**）

- **来源**：fm-refactor-spec seg9 verdict 收口轮次（2026-06-10 ~ 2026-06-11），3 次跨 goal 复发
- **信号描述**：主 Claude 在"修一个治理 / 沉淀缺口"时，**当场又埋同一类缺口**（修补动作本身复现被修问题）。元层 = 反思现场本应内化的防御点，反思现场都防不住 = 防御失效模式。与 O-A6.1.1-01"plan 用假设" / O-A6.1.2-01"实现凭自行解读"同根（防御点在**治理 / 元工作维度**再扩展），与 O-A6.1.1-01 元层复现告警同类机制。
- **3 次出处**（每次 = 1 个跨 goal 数据点）：
  1. **GOAL #7 B2**（docs 与 as-is 对齐期间）—— [run-zhongji-fundamental-20260611](fm-refactor-spec/run-zhongji-fundamental-20260611/) seg9 verdict 同步轮次
  2. **GOAL #16 A 路径**（ADDENDUM 路径选择期间）—— 见 [SEG9-VERDICT-2026-06-11-ADDENDUM.md](fm-refactor-spec/run-zhongji-fundamental-20260611/SEG9-VERDICT-2026-06-11-ADDENDUM.md) "触发路径" 段：GOAL #7 后用户点出两处补强 → 触发 Brake Q6（verdict 已冻结） → 走路径 A 独立 ADDENDUM
  3. **GOAL #17 α+β 合并自查**（封存前最后定夺当场自查发现 2 例 α+β）—— ADDENDUM 落盘流程内合并自查实证
- **触发升级**：N≥3 同类跨 goal 复发 → §2.10.6 升级线达成 → **从 observe 升为 should_update**
- **升级处置（按 §2.10.5 分流表）**：baseline / 治理流程类 → **单独 governance PR 或 main 直接 commit**（§1.3 例外）。本 commit 已同步收紧 [05-brake-self-check.md §2.7.5 Q6](../governance/workflow/05-brake-self-check.md#275-8-问详细判定标准)，新增"已声明冻结状态的判读档触碰类"判定（含导航 / 链接 / 元数据 / 反向索引 / 错别字，无"仅改元数据"例外；可发现性缺口去引用方补，不动冻结档本体）。
- **关联**：O-A6.1.1-01（plan 用假设元层延伸）/ O-A6.1.2-01（实现凭自行解读元层延伸）/ Brake §2.7.5 Q6 收紧
- **当前判断**：**N=3 已升级 should_update（本 commit 闭环）**。后续若再现"治理修动作埋同类缺口" → 喂下一轮 should_update 实证（验证 Q6 收紧是否内化）
- **计数粒度**：跨 goal 粒度（§0 规则；3 个 goal 均在同一 fm-spec seg9 收口轮次内连续复发，密度告警 = 集中爆发模式与 O-A6.1.2-01 .1/.2 sub-goal 100% 复发率同型）

### O-DOC-SYNC-01: "修完一处'错前提'后，未按前提本身再扫一轮" （**N=2**）

- **来源**：GATE-ROUTE + DOC-SYNC 收尾轮（2026-07-22），跨节点 2 次
- **信号描述**：修复一个由**错误前提**导致的缺陷后，只 grep**被修对象的名字**，没 grep**那个前提本身** →
  同一前提埋下的**兄弟缺陷**漏网。共性 = 把"前提"当成了"这一处的局部原因"，而它其实是**跨多处的公共依赖**。
- **2 次出处**：
  1. **GATE-ROUTE G2**：改价位门控时只扫「带 level ⟺ verified」这个不变量的字面 → 漏掉建立在同一前提上的 quality gate **S6**
  2. **修 S6 时**：只扫关键词「S6」，没扫前提本身「HOLD + entry」 → 漏掉同族的 **Q4 HOLD 豁免**
     （两者都因旧门恒抹价位而**永不被检验** = 死码掩盖的错前提）
- **教训（待升级后成文）**：修错前提类缺陷时，**搜索词必须是前提的语义描述**（如「HOLD 会不会有 entry」），
  而非被修函数 / 检查项的名字。前提是公共依赖 → 必然有兄弟。
- **跨节点累积次数**：N=2
- **触发升级**：≥ 3 次 → 升级 should_update，进 [known-pitfalls §3.2](../governance/workflow/09-known-pitfalls.md)
- **当前判断**：N=2，observe（**未达 §2.10.6 升级线，不提前升级**）
- ⚠️ **计数勘误（同 session 内自纠）**：DOC-SYNC 期间口头曾称"机制图行号块是本模式第三次"——**不成立，不计入**。
  行号块属**锚点腐烂**（见 O-DOC-SYNC-02），机制不同；且那一次**扫了并且抓到了**，
  是本教训的**首个正向应用**。把成功案例记成失败次数会污染升级线判据。
- **关联**：O-FM-spec-01（"修 X 埋 X"·同属"修动作自身的元缺陷"家族）

### O-DOC-SYNC-02: "文档内的代码行号锚点静默腐烂" （N=1）

- **来源**：DOC-SYNC 收尾轮（2026-07-22）
- **信号描述**：[机制图 HTML](../plans/gate-routing-redesign/gate-explorer-理想图-下一版-20260720.html)
  顶部「真值源」块自称 **"全部实读核对过 2026-07-21"**，一天后实测 **16 条代码锚点中 11 条行号已过期**
  （其后 G2 / G5 / EVID-1 各段又有增删）。腐烂**无任何信号**——文档看起来完好，行号看起来精确，
  只有真去 `sed -n` 才发现指到了别处。其中 1 条（前端 chip `InlineMd.tsx:64-103`）**当初就指错了**，
  指到一段讲斜体的注释，与漂移无关。
- **危险性**：行号**看起来比符号名更精确**，所以更容易被信任；而它恰恰是最易腐的锚。
  "已核对过"的声明会让后人跳过验证 → 假精确比不给锚更糟。
- **本轮已就地治**：全块改准 + **每条附符号名**（认符号比认行号可靠）+ 顶部加"行号是易腐锚，改 base.py 后本块须重核"。
- **未治**：全仓其他文档同病（backlog 已有"行号漂移"条目，全仓整改仍暂缓）。
- **跨节点累积次数**：N=1
- **触发升级**：≥ 3 次"文档行号锚点被发现批量过期" → 升级 should_update（候选规则：文档引用代码位置**必须带符号名**，行号只作辅助）
- **当前判断**：N=1，observe

### O-DOC-SYNC-03: "给自己的产出报统计数，未按最终 diff 点验" （N=1）

- **来源**：DOC-SYNC 收尾轮（2026-07-22）
- **信号描述**：完成锚点重核后口头报"**11 个锚点里 8 个已漂**"——**两个数都错**，实为"**16 条锚点中 11 条过期**"。
  错因 = 计数时把「条目」与「子锚点」两种粒度数混（如「豁免名单构造」一条含 3 个子锚点、仅 1 个过期）。
  **加重情节**：该错数**被写进了 HTML 顶部**（= 给后人留了个假真值），事后以 `88befcb` 勘误。
  用户一句"漂了的 8 处修改了吗"才触发点验。
- **教训（待累积）**：**未验证的断言不因出自自己而豁免**——改动本身逐条核过，不等于事后的统计描述也核过。
  报数前按最终 diff 点一遍，成本极低。
- **跨节点累积次数**：N=1
- **触发升级**：≥ 3 次"自报统计数与实际 diff 不符" → 升级 should_update
- **当前判断**：N=1，observe
- **关联**：verify-before-acting（未验证前提当真值）/ CLAUDE.md R4（事实纠错优先）

### O-A5-R3-01: "R3 数据不足约束零实测覆盖 —— 加不加检查须测量驱动" （N=0 触发）

- **来源**：A5 重评（2026-07-22·DOC-SYNC 后续）
- **信号描述**：`DECISION_PROMPT` **R3**（DATA_INSUFFICIENT 角色覆盖领域不给具体价位）
  **从未在任何真实 run 里触发过** —— GATE-ROUTE 两跑（NVDA / 中际旭创）均**无** DATA_INSUFFICIENT 角色。
  即：这条约束的实际遵守率、违反形态、以及"是否需要机器检查"**全部零数据**。
- **为何现在才成为问题**：(b) 之前旧价位门控恒抹非 verified 价位 → 即便违反 R3 也大概率被抹掉
  = **违规被机制性掩盖**；(b) 之后价位存活 → 违规会真的进报告。
  **这是 S6 / Q4 同一个错前提家族的第三例**（前两例是死码，本例是"从未写过的检查"）。
- **为何不现在加检查**：① 零数据 —— 不知道要防的是什么形态；
  ② 用户澄清设计意图（2026-07-22）= R3 **本就冲着多标的 / 板块查询**，单标的场景语义不成立，
  当时规则写得比意图宽 → **先补适用范围**（已做：prompt R3 + `base.py` 注入句两处同步）；
  ③ 规则零实测时先加检查 = **把说不清的规则固化进代码**，比不加更糟（以后没人敢动，还以为它对）。
- **需要什么数据才能决策**：**一次多标的 / 板块查询的完整 e2e**（该场景下 R3 才真正生效），
  观察 fund_mgr 是否遵守、违反形态是什么。
  ⚠️ **非计划任务，机会性触发**（2026-07-22 用户裁定）：**不专门安排跑**，
  等将来自然碰上多标的 / 板块查询那一次顺带观测。别的 session 读到本条**勿理解成"有人正在跑"**。
- **顺带记一个未实测的推断**：注入句原为**无条件插入**（任一角色 DATA_INSUFFICIENT 即插），
  单标的场景下照字面读可能被理解成"那就别给价位了" → **价位全灭 = 顶北极星**
  （把 (b) 刚修好的病从后门放回来）。**推断，无实测证据**；本轮补适用范围即为堵这个口。
- **触发升级**：拿到多标的 / 板块 e2e 数据后重评；若观察到真实违反 → 按 §2.10.5 分流决定检查形态
  （新增 gate 检查须先在 [e2e-acceptance-standard §4](../governance/e2e-acceptance-standard.md) 登记 + **一律 WARN 试用**）
- **当前判断**：**不加检查·等数据**。已完成的动作仅为"补适用范围"（prompt-only·零新增机器判定）
- **不占 backlog 条目**：backlog 当前 **15/15 至上限**（新增前须先 close 一条），
  且本项缺的是"实测数据"而非"待办工程" → observation 通道是正确归属
- **关联**：A5 重评就地注记（[agent-review-s2.3.md](../governance/agent-review-s2.3.md) A5 段）/ S6 / Q4 错前提家族

---

### O-AY-01: "守护测试守住了字面、守不住意图" （N=1·**2 子实例**·🔺密度告警）

- **来源**：AY G3（2026-07-28·classify 重试）—— **两个子实例同属 G3**，按
  [§0](#0-observation-计数粒度统一规则2026-05-18-reconcile) sub-goal 粒度**合记**，
  N 不 bump（先例：O-A6.1.2-01「N=1（4 子实例）」）。
- 🔺 **密度告警（本条最要紧的信息）**：**同一 sub-goal 内复发**——这是本文件迄今
  最紧的复发密度（既有密度告警最紧为 parent-node 内）。且子实例 2 **未被节点自身
  任何防线拦住**（77 条靶测 + 7 次 mutation + 全量 3012 绿 + DoD 四步全过），
  靠 **PR 外部 cross-context review** 才捞出。**这否证了本条原记的"未造成损失"**（见下）。
- **信号描述**：既有守护测试 `test_llm_timeout_seconds_is_within_phase_budget` 断言的是
  **常量** `LLM_TIMEOUT_SECONDS <= 15.0`，其 docstring 明写守护意图 =
  「classify 单步超时天花板不得吃掉 90s run 硬预算」。而 AY plan 原案「重试 3 次」
  会让实际最坏耗时变成 **3×15+退避 ≈ 48s（占预算 53%）**，
  **该断言却不会变红** —— 风险转移到了**新增的代码路径**（重试循环）上，常量纹丝不动。
- **与既有信号的区别**：
  - 与 [O-GATE-ROUTE-02](#) / §3.2「靶测须先 assert 前提」不同：那些讲**检查没跑过 / 前提没建立**；
  - **本条讲检查一直在跑、一直绿，但它的作用域没覆盖新路径** —— 守护的"锚点选错了层"
    （锚在常量上，而风险在"由常量+新代码共同决定的行为量"上）。
- **化解手法（已内建，可复用）**：新增守护时**锚定意图量而非实现常量** ——
  本次加的 `TestBudgetGuard` 断言的是 `LLM_TIMEOUT_SECONDS + 退避总和 <= 18s`
  （"最坏总耗时"这个意图量），日后谁把超时重新纳入重试，它会立刻红。

#### 子实例 1（登记时·2026-07-28 retro）— 锚点选错**层**

- 形态：断言钉在**常量**上，风险在"常量 + 新代码路径共同决定的行为量"上。
- **未造成损失**：写 plan 时未查该守护 → 差点按原案实施；实现前主动查了守护测试
  才发现冲突，当场改设计（超时不重试）。

#### 子实例 2（同日·PR #213 review 捞出）— 枚举**不完备**，且**真的漏了**

- 形态：`_is_fast_transient` 的 docstring / hints 表 / plan 表格 / PR body **四处**
  都声明「502·503·504 重试」，但通用 `"timeout"` 子串排除跑在 hints 之前，而 504 的
  reason phrase 自带 "Gateway Timeout" → **504 永不重试**、`"gateway timeout"` hint 是
  **可证明的死条目**。而靶测参数化**恰好只列了 502/503** —— 漏掉的正是唯一会红的那个。
- **守住的字面** = "有重试逻辑且 502/503 会重试"；**守不住的意图** = "502·503·504 都会重试"。
- ⚠️ **与子实例 1 的机制差异（值得分开记）**：子实例 1 是**锚点层级**选错
  （锚常量 vs 锚意图量）；子实例 2 是**示例枚举不完备**（锚点层级对，但用有限枚举
  验证一条全称声明，且枚举避开了反例）。同属"字面 vs 意图"族，**化解手法不同**：
  前者靠"锚意图量"，后者靠"**声明里出现的每个枚举项都必须有对应用例**"（本次修法：
  504 两种真实 httpx 报文形态各一条 + mutation 证转红）。
- **造成了实际缺陷**（虽方向安全）：不重试 = 回落旧行为、不多吃预算、不出错结果，
  损失仅"本可救回的一次 504 没救"。**但它逃过了节点全部自查防线**，见上方密度告警。

- **触发升级**：≥3 次同类 → 升 should_update，考虑在
  [09-known-pitfalls.md §3.2](../governance/workflow/09-known-pitfalls.md) 加
  「加新代码路径时，问它绕过了哪个守护的**意图**（而非哪个断言）」
  +（子实例 2 新增）「**声明里枚举了 N 项，靶测就必须覆盖 N 项** —— 漏掉的那项
  往往正是会红的那项」。
- 🔗 **与 O-GATE-ROUTE-02**（N=2·「坑表条目写下后·下一个 goal 当场复现」·
  仅登记于 §6 迭代历史 2026-07-22 两条，无 §1 条目）**收敛**：
  两条现在指向**同一个化解方向** —— 这类坑靠"记得"防不住，需**机械化手段**
  （测试模板强制"前提/枚举完备性"栏位、或 lint 规则）。两条**暂不合并**（根因不同：
  那条是"沉淀后即刻复发"= 沉淀有效性，本条是"守护锚点/枚举选择"= 守护设计），
  但若任一先到 N≥3，升级时**须一并评估另一条**，因为机械化手段大概率是同一套。

---

### O-AY-02: "编译期静态数据注入，破坏了基于该结构的'完整性'判断" （N=1）

- **来源**：AY G2（2026-07-28·curated 美股中文名注入名录索引）
- **信号描述**：`SecurityIndex.covers_market(market)` 的语义前提 =
  **「该市场的名录数据完整到可以据此判定某个码是假的」**（其 docstring 自称
  "本函数最容易写错、后果最严重的一处"）。把仅 34 名的 curated 静态表注入索引后，
  若让它一并计入 `_markets`，`covers_market("US")` 就变 True —— 于是在 store 为空时
  （网络挂 / 首启），[reconcile](../../src/committee/security_registry/reconcile.py) 会把
  LLM 给出的**任何非本表美股码判成无效丢弃** = 把"降级"变成"破坏正确输入"。
- **性质**：**结构被复用于两种不同强度的用途**（"能查到吗"=弱 / "完整到能证伪吗"=强），
  新数据源只满足弱用途，却顺带满足了强用途的**判定入口**。
  与 §3.2「改数据形态须核下游」同族，但**下游读的字段一个都没变** —— 变的是
  同一字段背后的**数据完备性假设**。
- **化解手法（已内建）**：`SecurityIndex.__init__` 显式分参
  （`entries` = 权威全量源，计入 `_markets`；`curated` = 补充条目，**刻意不计入**），
  并加 `TestCoversMarketSafety` 4 条固定，mutation 证承重。
- **本次未造成损失**：写测试时先想"它会不会让 covers_market 变 True" → 当场发现并分参。
- **触发升级**：≥3 次同类 → 升 should_update，考虑沉淀
  「往一个带'覆盖度/完备性'语义的结构里注入部分数据源前，先问它是否也被用作**证伪依据**」。

---

### O-BK-01 [记账清单·迁自 backlog BK close 2026-09-22]：静默降级可见化收口后挂着的 28 条记账 / observe 项

- **来源**：[backlog BK](../governance/backlog.md)（2026-09-22 close-by-completion·用户裁「记账项迁观察点表、close BK」）。BK 各批（P0 / PR3 / M4 / M4-fix / BK.3 / BK.5 / BK.6）合并前 review 与量基线坐实、**当时裁「不修只记」**的发现，原本挂在 BK 一览表行与正文里；BK 两本账归零后条目 close，清单整体迁到这里。
- **性质**：一张清单，不是同类信号 —— **不累积 N**；每条各自独立，触发时按条处置（修 / 升 should_update / 明确不做），处置后**在本表就地标 ✅ 并写去处**，不删行。
- **触发条件全部事件型**（守 [backlog §4.1](../governance/backlog.md#41-新增-backlog-条目) 判据有效性约束）：绝大多数是「下次动某文件时顺手清」；#22 / #23 / #24 是「出现一次某现象」；#18 是用户已裁不做、等首次有人需要。
- **不在本清单的同族项**：HTTP `/analyze` 不拦空 query 已另立轻条目 `API-EMPTY-QUERY`（backlog 非配额族）；BK.3 §7 #2 / #4 的「记账」已随 BK.6 清账落地。

| ID | 项 | 触发条件（事件型） | 出处 |
|---|---|---|---|
| O-BK-01 | 缺腿「原因」（超时 vs 异常）没人记 —— 降级清单只说「没拿回来」不说为什么；09-17 冒烟里研报库带摘要取数 8.1 秒贴每源 8 秒时限即此形态 | 排查某次缺腿要分原因时 | [bk6 §7 #3](bk6-20260922/FINDINGS.md) · [bk2-m2-pr1](bk2-m2-pr1-20260917/FINDINGS.md) |
| O-BK-02 | `__degradation_notices__`（U1 退化告警写进 `source_routing` 的整串文本）全仓无读者；盘点 #20「cli only」指的是终端那行 | 决定给 U1 告警找读者、或删该键时 | [bk6 §7 #2](bk6-20260922/FINDINGS.md) |
| O-BK-03 | E8 兜底档 rss 5 run / fred 2 run 的可疑缺腿（量基线翻档时看到） | 排查缺腿原因时翻档 | [bk6 §0.1](bk6-20260922/FINDINGS.md) |
| O-BK-04 | `ensure_price_leg` 补进来的价格腿仍不进归档计划的意图清单（只进排查报告） | 下次动 `ensure_price_leg` / 归档计划意图清单时 | [bk2-m2b](bk2-m2b-20260918/FINDINGS.md)（PR3 记账） |
| O-BK-05 | 最终归档 `archive-from-final.json` 不含 `common_context`，只留最终档会丢校验拒收线索 | 归档只留最终档那天 | [bk5 §0](bk5-20260922/FINDINGS.md) |
| O-BK-06 | 人工确认路径的规划员原始输出不进 calls.jsonl | 需要回溯人工路径规划员输出时 | [bk5 §7](bk5-20260922/FINDINGS.md) |
| O-BK-07 | `plan_intent_dropped` 便条 detail 的 `idx` 混两套坐标（规划员原始顺序 vs 确认后列表顺序）；归档只存通过条目、同一跑可有多条 `idx=1` 指不同意图 —— 记录里带标的 / 序列号快照或写明坐标系 | 下次动 `_note_dropped_intents` / cli 确认环 / planner 丢弃判据时顺手清 | [bk5 §7.1 ①](bk5-20260922/FINDINGS.md) |
| O-BK-08 | 「拒收 verdict → 记录」生成式在 cli 确认环与节点各写一遍 —— 抽 `rejected_records(validation)` 共用 | 同上 | [bk5 §7.1 ②](bk5-20260922/FINDINGS.md) |
| O-BK-09 | `_drop_reason` 每条意图算两次；`or ("?", None, "未知原因")` 分支不可达、把契约藏起来 —— 让 `_normalize_intent` 直接返回丢弃记录 | 同上 | [bk5 §7.1 ③](bk5-20260922/FINDINGS.md) |
| O-BK-10 | cli 确认环里 `dropped_intent_record` 的 import 写在 while 循环体内 | 同上 | [bk5 §7.1 ④](bk5-20260922/FINDINGS.md) |
| O-BK-11 | 回放测试里无用的 `cn` import / `del cn` | 同上 | [bk5 §7.1 ⑤](bk5-20260922/FINDINGS.md) |
| O-BK-12 | 码表 / 登记表注释称 `web_number_stamp_failed` 有三个调用方含「标的解析」；实际盖章只在收账本（`return_tool_outputs=True`）的调用里做，`classifier.py` 不带该参 ⇒ 该路不可达；传递矩阵那行的理由是一条发不出此码的路径 | 下次动码表注释 / 标的解析真接盖章时一并改 | [bk6 §7 R3](bk6-20260922/FINDINGS.md) |
| O-BK-13 | `context_empty_query` 便条 detail 硬写「为空串」，`query=None` 同样触发 —— 改 `query={query!r}` | 首次真实响起核措辞时 | [bk6 §7 R4](bk6-20260922/FINDINGS.md) |
| O-BK-14 | `note_degradation` 在 `mismatch_review.py` / `context_node.py` 函数体内 import（无循环风险·模块级更省，也避开静态派生盲区） | 下次动这两个文件 | [bk6 §7 R6](bk6-20260922/FINDINGS.md) |
| O-BK-15 | `_evid1_events` 编号串按字符 `[:120]` 硬截会截出半个编号 —— 改按条数截 | 首次真实响起核措辞时 | [bk6 §7 R5](bk6-20260922/FINDINGS.md) |
| O-BK-16 | `_coerce_debate_key_claims` 非列表分支返回 `None` 与直接返回空列表等价、且计数形态不一致（`non_list` 无 kept / coerced / dropped 三项）—— 可合掉 | 下次动辩论校验时 | [M4-fix §8 ①](bk2-m4-fix-20260921/FINDINGS.md) |
| O-BK-17 | 「从校验报错里挑顶层坏字段」那行与 `_sanitize_verify_checklist` 逐字重复 —— 抽小函数两处共用 | 下次动辩论校验时 | [M4-fix §8 ②](bk2-m4-fix-20260921/FINDINGS.md) |
| O-BK-18 | 排查报告不显示便条的细节文字（被截条目原文 / 被洗字段）—— 用户裁 D 不做 | 首次有人需要从排查报告里读被截原文 / 被洗字段时 | [bk2-p0](bk2-p0-20260917/FINDINGS.md) · [bk2-m4](bk2-m4-20260921/FINDINGS.md) |
| O-BK-19 | BK.6 节点测试钉死「全仓登记表无 `pending:`」；下一个合规登记 pending 的 PR 会把该测试打红 | 首次被打红时改由 `lint_degradation_registry` 报告承接 | [bk6 §7 R7](bk6-20260922/FINDINGS.md) |
| O-BK-20 | `test_degradation_bk6.py` 无用的 `agent_loop` import + `del` | 下次动该测试文件 | [bk6 §7 R8](bk6-20260922/FINDINGS.md) |
| O-BK-21 | BK.3 迁移脚本 `strip(" ——（）")` 只剥括号一头，登记表 `# ↓` 依据注释多条读起来像截断（≥ 4 处：`classify` / `refresh` / `_lazy_bootstrap` / `WisburgSource.fetch`） | 下次改那几条依据注释时 | [bk3 §7 #7](bk3-20260922/FINDINGS.md) |
| O-BK-22 | 登记表已有 10 条键尾随空格（指纹截 40 字后以空格结尾；人手抄写易丢、出错不提示差异是一个空格） | 出现一次「过时 + 未登记同时响、肉眼看键一样」的排查 ⇒ 升为修（fingerprint 加 rstrip + 迁 10 键） | [bk3 §7 #8](bk3-20260922/FINDINGS.md) |
| O-BK-23 | 真实仓库靶测「一站一键」断言按构造恒真（序号后缀保证唯一），测不到碰撞；要守「真实仓库指纹碰撞 0」应断言 `all(ordinal == 1)` | 真实仓库首次出现 `[指纹碰撞]` 时一并改 | [bk3 §7 #9](bk3-20260922/FINDINGS.md) |
| O-BK-24 | 原钉「源文件语法错要显式炸」的靶测被换成非 UTF-8 用例，语法错这一支失去覆盖 | 任何人给 `scan_sites` 的 `ast.parse` 套 try/except 前先补回这条靶测 | [bk3 §7 #10](bk3-20260922/FINDINGS.md) |
| O-BK-25 | M4-fix 证据 §2 / §3 两处仓内路径纯文本未用活链接（违反链接规范） | 下次动该文时改 | [M4-fix §8 ③](bk2-m4-fix-20260921/FINDINGS.md) |
| O-BK-26 | 回放脚本按 `splitlines()` 切行，JSON 字符串里合法的 U+2028 / U+2029 会把记录切断、整跑崩掉（M4 基线脚本同写法）—— 改按换行符切 | 下次动该证据目录任一文件时 | [M4-fix §8 ④](bk2-m4-fix-20260921/FINDINGS.md) |
| O-BK-27 | 新便条码大多**无历史基线**（进程日志不存档、trace 不收日志行）：P0 批 4 码 · BK.6 5 码 · BK.5 `plan_intent_dropped` · M3 / M4 各码 —— 「会响」只由靶测 + 变异证 | 某码首次在真实跑批里响起时回头核档位（用户面 / 排查报告）与措辞 | [bk2-p0](bk2-p0-20260917/FINDINGS.md) · [bk6 §0.1](bk6-20260922/FINDINGS.md) |
| O-BK-28 | **留存事实**（09-14 triage 记下·非任务）：classify 超时的 15 秒是**每次尝试**的上界，底层 SDK `max_retries=2` ⇒ 最坏 ≈ 45 秒；同句六次实测 1.9–3.4 秒（0/6 接近超时）—— 别再读成「最多 15 秒」 | 下次动 classify 超时回退时用得上 | [backlog BK 行 09-14 triage 注](../governance/backlog.md) |

### O-CRED-01: "时效判据的输入本身不干净 —— 日期缺失与粗精度归一让『过时』被系统性高估" （N=1）

- **来源**：CRED.2.G0（2026-09-23·外源 as_of 分布只读探针·[FINDINGS](cred-2-g0-asof-dist-20260923/FINDINGS.md) §3.5）
- **信号描述**：给 D1（400 天保鲜期）备料时发现，任何一条线在量之前都先被两件输入侧的事盖住：
  ① 外源册（带日期时代）**33.6%** 条目没有日期（搜索结果不带 `publishedDate`·原样落空串），confidence / 表③ 一律按「过期」处理 —— 线画哪都拦不到它们；
  ② 裸年份按设计归一成 `YYYY-01-01`（[`_normalize_as_of`](../../src/committee/as_of.py) docstring 明写），在「超 400 天」的外源册条目里占 **24%**（22/92·原值全是裸年份）〔v2 去重订正后数·v1 记 28%（37/133）含续跑重复计数〕—— 真实发布日最多晚 364 天，「过时」被高估。
- **性质**：与 §3.2「守卫要锚在它真正要守的对象上」同族的**输入侧**版本：阈值裁得再准，输入字段一空一粗，判据量到的就不是「信息多旧」而是「取数有没有带日期」。**不是 bug**（两处都是设计性处理），是判据的前提没被写出来。
- **为什么只 observe**：改线（D1）归用户裁；补日期归取数侧（seg1 取数质量线）；BD 已 2026-09-08 close-by-decision。本条只记「裁阈值前先量输入干净度」这一动作值不值得成规则 —— 一次不够。
- **触发升级**：再出现 ≥ 2 次「裁一条阈值 / 判据线时，量出来输入字段的缺失或精度问题比阈值本身影响更大」→ 升 should_update：在 [03-decomposition.md §2.4.1](../governance/workflow/03-decomposition.md) 计划数字核验那条里加「阈值类裁决备料须先报输入字段的缺失率与精度」。
- **2026-09-23 补（D1 裁 180 后·不计 N）**：线收到 180 天后，②的高估面**扩大**：只写「今年」的信息（归一成当年 1 月 1 日）过了 7 月初就被判过期（400 天下要到次年 2 月才会）。已写进 [confidence.py](../../src/committee/facts/confidence.py) 校准注「已知高估」+ 失效条件 ③；治本仍归取数侧。

### O-CRED-02: "局部『只降不升』≠ 全链只降不升 —— 降档后的那一档可能正好是下游某道闸看不见的档" （N=1）

- **来源**：CRED.2.G3（2026-09-23·审核读出处日期）。
- **信号描述**：设计 pass 写「出处过期 → 审核降 `audit_notsure`·只降不升」，在审核这一层确实只降；但 notsure → 可信度 `unavailable`，而执行底线 check③（[exec_floor.py](../../src/committee/facts/exec_floor.py) `outdated_anchor_mismatch`）按用户 2026-07-07 裁**只认过期档、不认未核实** ⇒ 一个靠过期股价撑着的价位，原本会被切、改后反而放过 = **越严越松**。实现时顺着下游消费者逐个查才撞见；主干回放 4 条恰好没撞上（价位没引那几条事实），**靠回放发现不了**。用户裁 = 审核档不动、可信度落 `sourced_outdated`。
- **性质**：档位不是一条单调的线，是一张「哪道闸认哪几档」的表。「往低档挪」只在**每个消费者都把新档当成至少一样严**时才安全；check③ 把 `sourced_outdated` 当最严、把 `unavailable` 当「交给披露层」，两档在它眼里不可比。
- **为什么只 observe**：一次；本轮已修。
- **触发升级**：再出现 ≥ 2 次「某处改成降档 / 换档，下游某道闸因此不再响」→ 升 should_update：在 [05-brake-self-check.md](../governance/workflow/05-brake-self-check.md) Q5 加一条「改任何档位产出前，列出该档的全部消费者，逐个核新档在它那里是否至少一样严」。

### O-CRED-03: "改了结构化记录、没改给人 / 模型读的那份正文 —— 同一份货两处存放，只动一处" （N=1·同族见 memory「渲染点不止一处」）

- **来源**：CRED.2.G4（2026-09-23·引用身份实现前核代码）。
- **信号描述**：研报回核按检索词把不相关的从 `_meta.reports`（结构化记录）里删了，并记下「回筛掉 N 篇」；但分析师真正读的是同一条腿的 `text` 正文（服务端原样的全量列表 + 摘要），**没跟着改** ⇒ 主干 9 条研报腿共 29 篇被判不相关的研报照样进了分析师上下文。留痕、计数、测试都盯着结构化那份，**全绿**。已在本 goal 修（按留下的重建正文）。
- **性质**：「验货」的效果要落在**消费者实际读的那份**上。同一批货只要有两份表示（结构化 + 渲染文本），只改其一 = 看起来生效、实际没生效。与 memory「说『已覆盖』前调出当天产物逐字核，别对脑内架构图核」同族。
- **为什么只 observe**：本域第一次；已修。
- **触发升级**：再出现 ≥ 2 次「过滤 / 降级只改了结构化记录，下游读的文本没跟着变」→ 升 should_update：在 [09-known-pitfalls.md](../governance/workflow/09-known-pitfalls.md) §3.2 立一条「过滤类改动须对消费者实际读的那份做前后对比」。

## 2. 已升级到 should_update（归档）

（首次建立，目前为空）

> O-FM-spec-01 已升级 should_update（2026-06-11），登记 + 详情仍保留在 §1 内并标"N=3 已升级"，便于后续复盘审视；§2 待真"归档退役"再迁入。

---

## 3. 已 stale / 不再相关（归档）

（首次建立，目前为空）

---

## 4. 维护协议

- 每次节点级 retro `<q5_sedimentation>` 产出的 `<observes_accumulated>` → 追加到 §1
- 累积 ≥ 3 次同类 → 升级到 should_update，移到 §2 已升级
- 子阶段 verification-report 审视时 → 若信号已退役（如新规则覆盖了原信号）→ 移到 §3 stale
- 修改本文件 commit prefix：`docs(observations):`

---

## 5. 与其他文档的关系

| 文档 | 关系 |
|---|---|
| [docs/governance/backlog.md](../governance/backlog.md) | backlog 是"identified delay"，本文件是"信号累积等升级"；累积 ≥ 3 → 升级后可能进 backlog |
| [docs/governance/workflow/07-retro-goal.md §2.10.6](../governance/workflow/07-retro-goal.md#2106-observe-累积出口) | 累积升级协议真值源 |
| [docs/governance/workflow/10-verification-report.md §4.2](../governance/workflow/10-verification-report.md#42-子阶段交接的审视清单) | 子阶段交接时审视本文件全部信号 |

---

## 6. 迭代历史

- **2026-05-14**：首次建立（A6.1.1 节点级复盘）。登记 4 条 observations：
  - O-01: plan 未 grep 约束（N=2）
  - O-02: self-audit pass + cold review 抓（N=2，关联 backlog J 触发）
  - O-03: 主动 audit 抓自己反模式（N=1）
  - O-04: or-assert 模糊验证（N=1）
- **2026-05-14**（同日补）：加 O-05 [架构层 gap]。来源：cold review 触发后 2 步实证验证。
  - SKILL.md auto-trigger 0 落地 / hook 0 配置 / 7 普通 skill 0 触发 — 跳过 N ≥ 3 累积规则，直接进 backlog L（🔴 P0）。
- **2026-05-14**（skill-system-refactor 期间）：加 O-A6.1.2-pre-01（5 项 A6.1.2 待实证）。来源：skill-system-refactor 完成时提前登记 hook 注入实测、verification-report invoke 率等评估项。
- **2026-05-15**（A6.1.2.1 commit b461165 后）：扩展 **O-A6.1.1-01** 定义：从"plan 写约定但未先 grep 现有约束"扩展为"plan 阶段用假设/记忆而非实测数据"（含 baseline 数字引用未实测 / import 风格未 grep 相邻模块约定）。跨节点累积语义化（每节点合记 1 次大事件），A6.1.2.1 合记成第 2 次大事件，N=2，再 1 节点即升级。来源：A6.1.2.1 内部触发 2 次（测数错估 + import 风格偏离），合记后总 N=2。
- **2026-05-15**（A6.1.2.1 brake-self-check Q5 自审后）：新增 **O-A6.1.2-01** "实现阶段对 plan 模糊处自行解读"（O-A6.1.1-01 对偶问题，不同根因不合并）。N=1。来源：Q5 自审 surface "plan 暗含 vs 明文 gap"（dispatcher 占位 → quality_flag 占位 推论 plan 未明文），已通过 plan 回填 root-cause-fix。
- **2026-05-18**（A6.1.2.1 retro 撰写前置）：O-A6.1.1-01 加 **元层复现告警**（commit 894e1d9 编辑 §9 时凭假设跳号，元工作内复现该模式）。N 不 bump（仍 2，规则一致），但 retro must_update 强制防御机制扩展到元工作维度。来源：retro 前置 §9 bug fix 自检。
- **2026-05-18**（A6.1.2.1 retro 收口）：O-A6.1.2-01 加 子实例 2（DoD §2.8.3 援引 precedent，retro 裁决同根因不 bump N，仍 1 含 2 子实例）；新增 **O-A6.1.2-02**（high-risk node 条件 6 恒触发现象，N=1）。retro must_update=0（元层防御闸 N=1 归 observe，规则一致非过早形式化）。来源：A6.1.2.1 retro 三档分流。
- **2026-05-18**（A6.1.2.2 step 11 S2.md alignment 反思）：新增 **O-A6.1.2-03 [候选]**（QualityFlag 三档不覆盖 out_of_scope 语义，N=1）。来源：Read S2.md §5.3 FM-pipeline.1 surface 的校准点 2。登记时纠用户口述"A6.1.1 5类型"为实际 2 类型（O-A6.1.1-01 防御不传播未实证口述）。
- **2026-05-18**（A6.1.2.2 retro 落盘）：O-A6.1.2-01 加 .2 期间 2 子实例（step 2 timeout 来源 + step 8 partial 矛盾），节点改 parent-node 粒度 N 仍 1（含 4 子实例），**surface 与 O-A6.1.1-01 sub-goal 粒度不一致待 reconcile**；O-A6.1.2-02 升 N=2（数据点 2 = A6.1.2.2 retro，.1+.2 命中完全一致 2/3/4/6，第 3 数据点 .3 决定是否升级条件 6/4 降级），新增 **O-A6.1.2-04 [候选]**（顶住用户建议 because known pitfall，N=1，原 must_update 候选降 observe）。来源：A6.1.2.2 retro 三档分流（must_update=0）。
- **2026-05-18**（A6.1.2.3 C.3 准备阶段 reconcile）：加 **§0 计数粒度统一规则** = 全 observation 用 sub-goal 粒度（非 parent-node）。O-A6.1.2-01 parent-node→sub-goal，N=1（4 子实例）→ **N=2**（A6.1.2.1 + A6.1.2.2 各 1 次，同 sub-goal 内多子实例合记），加**密度告警**（A6.1.2 内 2/2 sub-goal 100% 复发率，集中爆发 retro must address）。O-A6.1.1-01 不变（本来 sub-goal）。N=2 距升级线 N≥3 仅差 1，.3 C.3 审视决定升级 vs 维持。来源：.3 C.1 Q8 surface 粒度不一致 → 不延后 should_update governance，当场 reconcile（基础设施级精度问题）。
- **2026-05-18**（A6.1.2.3 retro 落盘）：**O-A6.1.2-02 升 N=3 闭环升级**（数据点 3 = A6.1.2.3 收口 sub-goal 命中 2<4 → sub-goal 性质主导命中数，"high-risk 恒 4 条"证伪；升级 should_update 选项 A/B → backlog/governance）；**O-A6.1.2-01 N=2 维持**（.3 0 自行解读，复发率 100%→50%，防御内化"进行时"，A6.1.3 关键测试）；**O-A6.1.1-05 加 A6.1.2 持续实证**（N=3 sub-goal 全程 0 hook，手动 workaround works）；新增 **O-A6.1.2-05 [候选]**（基础设施级精度当场 reconcile 不延后，N=1）。来源：A6.1.2.3 retro 三档分流（must_update=0）。
- **2026-05-18**（A6.1.3 task-entry，新会话冷启动）：**O-A6.1.1-05 加 A6.1.3 持续实证 — 新会话冷启动样本当场登记**（不等 .3 收口回填，防跨会话切换丢数据点；用户点 3 要求）。忠实口径：task-entry 无 `[GOAL]` 完成故 hook 本不应触发，实证的是跨会话冷启动下手动驱动机制仍 works（A6.1.2 retro A.Finding 3 跨会话稳定性首个正面数据点，task-entry 范围）；goal-completion hook=0 数据在 .1/.2/.3 累积。来源：A6.1.3 task-entry 用户对齐点 3。
- **2026-05-19**（A6.1.3.2 step0 期间）：**O-A6.1.1-05 加 (1) A6.1.3 会话 N+1 观察 — retro 自动捕获 vs 人工沉淀 mismatch + (2) runtime-premise 元观察**。用户确认 runtime = **Cursor Claude CLI 无 hook 能力**（取代 2026-05-14 旧表述"VS Code 扩展 additionalContext 注入失效"，旧表述 supersede 保留作史）→ **backlog L 根因修正重写**（状态 ✅完成→🔵根因修正/解决空间 (a)接受约束/(b)切官方 Claude Code 做自动 retro queue/(c)等 Cursor hook OPEN；§4.3 修订史已记）。runtime-premise 元观察：主 Claude 前几轮未先对齐 runtime 即顺"架构 gap"语境推演（错误前提），照实认 miss；教训 = workflow/工具机制讨论 runtime 假设须先对齐（O-A6.1.1-01 元层延伸）。随 L 跟踪 + .3 retro 评估是否升 should_update。来源：用户本轮对话确认 runtime + 反思。
- **2026-05-19**（路径 D hook 重写收口）：**O-A6.1.1-05 append self-correction 翻案**——"hook 0 落地 / 持续 observe hook=0 / backlog L 🔴 P0 不变" 根因翻案为伪根因（真因 = API 改名 + 输出缺 hookEventName 字段，非架构不可修复）。路径 D 全 7 case 验证通过，**backlog L 关闭（🔴→✅）**。原观察记录不改（保审计链），append 修正 + A6.1.3 观察点改为"路径 D 新会话冷启动稳定性"。来源：PR #117 三层根因翻案。
- **2026-05-26**（S2.2-gate root cause analysis）：新增 **O-S2.2-01**（PR TODO 空置跨多 PR 无人发现，N=1）+ **O-S2.2-02**（cold review code-level vs behavior-level 盲区，N=1）。来源：S2.2-gate 三根因分析——economist ROLE_OVERRIDE 空置 / REF# 注入漏 / rework 盲重试均通过 W1-W3 code-level review，仅 gate 实跑暴露。O-S2.2-02 与 O-A6.1.1-02 关联但层级更高（cold review 也漏 vs cold review 能抓）。已通过 S2.md §4.6 Agent 现状审视协议系统化防护。
- **2026-05-27**（WS.0-WS.3 web search retro）：新增 **O-WS-01**（风险判定基于实现路径假设应 spike 后 finalize，N=1）。来源：拆解阶段判 HIGH（"改 _invoke_json 核心路径"假设），spike 后发现走纯加法 LOW 路径。O-A6.1.1-01 风险判定维度延伸。
- **2026-06-11**（fm-spec seg9 收口轮次 + ADDENDUM 落盘）：新增 **O-FM-spec-01** "修 X 埋 X — 治理修动作里复发同类元缺陷"（**N=3 一次性升级 should_update**）。3 出处 = GOAL #7 B2 / GOAL #16 A 路径 / GOAL #17 α+β 合并自查（同 fm-spec seg9 收口轮次内跨 goal 集中复发）。同 commit 收紧 [05-brake-self-check.md §2.7.5 Q6](../governance/workflow/05-brake-self-check.md#275-8-问详细判定标准)，新增"已声明冻结判读档触碰类（含导航/链接/元数据/反向索引/错别字无例外）"判定。来源：ADDENDUM 路径 A 落地实证 + 封存前最后定夺合并自查。性质 = O-A6.1.1-01 / O-A6.1.2-01 在治理 / 元工作维度的延伸。
- **2026-07-02**（信源册 M1·T3.1 retro）：新增 **O-T3-01 "signature-lock 作为『结构性无通道』不变量的焊死模式"**（N=1）。T3.1 要"外源永不进 references_appendix"，实现选择 = `inspect.signature` 钉死函数入参 == 恰好三内源（catch A2 式悄悄加 web 入参），而非"断言输出无某值"——后者对"未传外源数据时"的 A2 版本无区分力、会假绿。mutation 已证 load-bearing（加 A2 式 web 入参 → 测试立即红）。可复现场景 = 其他 #5 隔离 / no-channel 守护（如 audit 永不读外源册）。≥3 次同类 → 升 should_update（沉淀通用坑表条目"结构性不变量优先焊接口签名、而非焊输出值"）。来源：T3.1 retro-goal（仅高风险节点条件 6 触发·commit `a730e35`）。
- **2026-07-22**（GATE-ROUTE.1 retro）：新增 **O-GATE-ROUTE-01 "同名不同物符号导致下游追查差点走偏"**（N=1）。G1 改 `ClaimAudit.numeric_match`（**字段**）后追下游消费方，仓内同时存在 `confidence.numeric_match()`（**函数**）——裸 grep 返回 31KB 混合结果，若不分型即得出"消费方全在 verify/confidence 层、与本改动无关"的**错误安心结论**，从而漏掉真正的传导链（`numeric_match` → `external_knowledge_refs` → e2e quality gate Q5 的 ratio 分母）。本次靠人工分辨化解、未造成实际损失（该链已核方向安全 = 只增大分母、ratio 只朝 PASS 移动 = 度量修正非标准放松，并加集成测试锁死）。**化解手法** = 对字段用 `.<name>` 属性访问模式搜、对函数用调用模式搜，先分型再列消费方。≥3 次同类（尤其若某次真漏了消费方）→ 升 should_update，考虑在 [09-known-pitfalls.md §3.2](../governance/workflow/09-known-pitfalls.md) 加"同名符号先分型再追消费方"。性质 = §3.2「改数据形态须核下游」的**执行细节层**缺口（规则本身记得、执行时差点被同名带偏）。来源：GATE-ROUTE.1 retro-goal（触发条件 2/4/6）。
- **2026-07-22**（GATE-ROUTE.2 retro）：新增 **O-GATE-ROUTE-02 "坑表条目写下后·下一个 goal 当场复现"**（N=1）。G1 retro 刚把「靶测依赖『某输入落在某集合/某状态』时必须先 assert 前提成立」沉淀进 [09-known-pitfalls.md §3.2](../governance/workflow/09-known-pitfalls.md)，**紧接着的 G2** 写 check③ 转正靶测时**当场踩同一坑**——沿用默认 head payload（`decision="HOLD"`）导致 `assert decision == "HOLD"` **空过**（本来就是 HOLD，闸没干活也过），靠看 `execution_plan is not None` 才发现。已修（改 actionable 决策 + 补前提断言）。**指向的问题**：这类坑**靠"记得"防不住**——沉淀当轮即失效，说明需要机械化手段（如测试模板强制"初态断言"栏位、或 fixture 约定），而非依赖注意力。≥3 次同类 → 升 should_update，考虑做成 checklist / fixture 约定。**与既有 O-FM-spec-01「修 X 埋 X」区别**：那条是*治理修动作里*复发同类元缺陷；本条是*沉淀后即刻复发*（沉淀有效性问题，非治理动作自身缺陷）。来源：GATE-ROUTE.2 retro-goal（触发条件 2/3/4/6）。
- **2026-07-22（补·PR #192 self-review）**：**O-GATE-ROUTE-02 升 N=2**。第 2 个数据点 = **同一 commit 内复发**：G1 把「靶测须先 assert 前提成立」写进 [09-known-pitfalls.md §3.2](../governance/workflow/09-known-pitfalls.md) 的**那次提交**（`0c44097`）里，新增的集成测试 `test_stamped_fact_colliding_with_prescribed_now_counted_in_refs` 自己就没建立撞号前提（沿用默认 head payload·**无 execution_plan** → 1500 从未进 prescribed 集合 → 旧代码下也绿、锁不住它名字声称的回归）。**PR self-review 捞出并已修**（显式注入 `take_profit.level=1500` + 前提断言 + mutation 证转红）。修的过程又暴露一层：前提须断言在**门入口时刻**（prescribed 门前算），断门后的 decision 会因 (b) 抹 level 而假失败。**N=2 距升级线 1 步**——若第 3 次出现，升 should_update：这类坑靠「记得」防不住，需机械化手段（测试模板强制「初态/前提」栏位、或 lint 规则）。
- **2026-07-28**（AY 节点收口 retro）：新增 **O-AY-01 "守护测试守住了字面、守不住意图"**（N=1）+ **O-AY-02 "编译期静态数据注入破坏基于该结构的完整性判断"**（N=1）。O-AY-01 出处 = G3：既有守护断言钉在**常量** `LLM_TIMEOUT_SECONDS <= 15.0`，而 plan 原案「重试 3 次」把实际最坏耗时抬到 ~48s（占 90s run 预算 53%），**该断言不会红**——风险转移到了新增的**代码路径**上。化解 = 新守护锚定**意图量**（`TestBudgetGuard` 断言"最坏总耗时 ≤18s"）而非实现常量。**与 O-GATE-ROUTE-02 区别**：那条讲检查没跑过/前提没建立，本条讲**检查一直绿但作用域没覆盖新路径**（守护锚点选错层）。O-AY-02 出处 = G2：`covers_market` 的语义前提是"该市场数据完整到能证伪某个码"，把仅 34 名的 curated 静态表计入 `_markets` 会让 store 空时把 LLM 给的**任何非表内美股码判成无效丢弃** = 降级变破坏。**下游读的字段一个没变**，变的是同一字段背后的**数据完备性假设**（§3.2「改数据形态须核下游」的姊妹形态）。化解 = `SecurityIndex.__init__` 显式分参、curated 刻意不计入 `_markets` + 4 条安全测试 + mutation。两条均**未造成实际损失**（实现前主动核查守护 / 写测试时先问"会不会让 covers_market 变 True"）。来源：AY 节点 retro（G3 触发条件 2/3；G2 触发条件 1/3/4）。
- **2026-07-28（补·PR #213 review）**：**O-AY-01 加第 2 子实例，N 维持 1 + 🔺密度告警**。
  ⚠️ **同时更正上条记录**：上条结尾「两条均**未造成实际损失**」——**对 O-AY-01 已不成立**
  （O-AY-02 仍成立）。第 2 子实例 = 同一 G3 内，`_is_fast_transient` 把 `"timeout"` 通用子串
  排除放在 `_FAST_TRANSIENT_HINTS` 之前，而 504 的 reason phrase 自带 "Gateway Timeout"
  → **504 永不重试**、`"gateway timeout"` hint 成可证明的死条目，与 docstring / hints 表 /
  plan 表格 / PR body **四处声明的「502·503·504 重试」相反**；靶测参数化**恰好只列 502/503**，
  漏的正是唯一会红的那个。**已修**（hints 检查前移·超时不重试属性逐字不变 + 504 两种真实
  httpx 报文形态用例 + mutation 证恢复旧顺序 2 红·commit `061c163`）。
  **计数按 [§0](#0-observation-计数粒度统一规则2026-05-18-reconcile) sub-goal 粒度合记 → N 仍 1**
  （两子实例同属 AY G3；先例 O-A6.1.2-01「N=1（4 子实例）」）。
  **但三点比 N 数字更值得记**：① **同一 sub-goal 内复发** = 本文件迄今最紧密度；
  ② 子实例 2 **逃过节点全部自查防线**（77 靶测 + 7 mutation + 全量 3012 绿 + DoD 四步），
  靠 **PR 外部 cross-context review** 才捞出 —— 这是"未造成损失"被否证的实质；
  ③ **机制与子实例 1 不同**（1 = 锚点选错**层**·锚常量非意图量；2 = 示例**枚举不完备**·
  用有限枚举验证全称声明且枚举避开反例），故**化解手法也不同**，条目内已分记。
  与 **O-GATE-ROUTE-02（N=2）收敛于同一化解方向**（靠"记得"防不住·需机械化手段），
  暂不合并（根因不同），但任一先到 N≥3 时须一并评估。来源：PR #213 review 修正轮。
- **2026-07-29（PR #213 合并前）**：新增 **O-CI-01 "DoD 的『全量绿』只在本地取证，未看 CI —— 环境依赖型假绿"**（N=1）。
  出处 = AY PR #213：PR body 的 DoD 写「全量 3012 passed / 0 failed」，但 **`auto/AY` 三次 CI 全红**
  （`60ae18f` / `c7a51b0` / `77ccdbe`），从 PR 开出起就红、**无人看**。根因不在产品码在靶测：
  `test_choice_e_accepts_manual_code` 名为「用户直接给代码」却喂 `"NVDA"`，而 `_TICKER_CODE_RE`
  只认 A股/港股码 → 落进 `_resolve_by_name` → **真实联网 LLM 调用**：本地有凭据即绿
  （且每跑一次烧一次 API），CI 无凭据即 `IndexError`。**信号本体不是"某个测试写错了"，
  而是"本地全量绿被当成了 DoD 的充分证据"** —— 本地环境带凭据 / 带缓存 / 带 `.env`，
  与 CI 的洁净环境不等价，**只有 CI 绿才是可复现的绿**。
  **化解手法（本次已用，可复用）**：怀疑环境依赖时，**剥净凭据跑全量**
  （`env OPENAI_API_KEY= DEEPSEEK_API_KEY= ANTHROPIC_API_KEY= TUSHARE_TOKEN= ALPHA_VANTAGE_API_KEY= pytest tests/`）
  —— 本次一跑即在本地复现 CI 的失败，定位耗时 < 1 分钟。修后同法验证 3020 passed。
  **与既有 §3.2「假绿」条目的区别**：那条讲**测试没覆盖到代码**（一行没测到）；
  本条讲**测试真跑了、但依赖了 CI 没有的环境**（覆盖到了，可复现性没有）。
  **与 memory `feedback_worktree_editable_pth_falsegreen` 同族**（那条是 `.pth` 钉错源码树 → 测的是旧码），
  三者共同的元问题 = **"绿"的成立条件未被显式陈述**。
  **触发升级**：≥3 次同类 → 升 should_update，考虑在 DoD 清单（[06-dod-and-evidence.md](../governance/workflow/06-dod-and-evidence.md)）
  加一条硬闸：**「DoD 的『彻底跑通』以 CI 结论为准；本地绿只是必要条件」**，
  并在 PR 收口前强制 `gh pr checks` 核一次。来源：PR #213 合并前 CI 核查。

- **2026-07-30（DOCS-C docs 整理 retro）**：新增 **O-REVIEW-SMALL-01 "小改动 / docs-only 的正式 cross-context review 仍捞出真缺口"（N=2·口径=不同实例维度合并计数·显式声明）**。
  实例 ①（code 小改动）M1-T12 #179：/review 捞出 archive 写盘无 try/except 的 robustness 缺口（教训已入 memory「别以改动小跳过 review」）；
  实例 ②（docs-only）DOCS-C #218：用户 review 捞出 22 条搬迁断链 + 复扫工具 CJK quotepath 盲区——**自查工具本身是盲的，"0" 只有外部视角能证伪**（自查在盲区内自洽）。
  **维度差异声明**（per 计数器卫生）：① 是代码 robustness、② 是文档链路 + 验证工具，target 不同但信号同型 =「改动小 ⇒ 可跳过正式 review」这一直觉被证伪。
  **升级预备**：N=3 时评估在 [08-retro-node-and-pr.md](../governance/workflow/08-retro-node-and-pr.md) §6 PR 收口加「docs-only / 小 PR 不豁免 review」硬提示。
  与 O-AY-01 子实例 2（逃过全部自查防线、靠 cross-context review 捞出）同向不同 target，分开计数。来源：PR #218 review。

- **2026-08-06（#226 review 修复 retro）**：新增 **O-MUTSCRIPT-01 "改源码的一次性验证脚本无 try/finally，异常中断污染工作树"（N=1）**。
  实例：为证 F4/F5 修法承重，写脚本把源文件改成变异体 → 跑 pytest → 还原。
  第一版无 `try/finally`，在**打印 emoji 时撞 GBK 编码崩溃**（Windows 控制台默认 cp936），
  于是变异体留在了 `audit_node.py` 里；靠随后读文件才发现，当场还原并加 `try/finally` + `PYTHONIOENCODING=utf-8` 重跑。
  **信号本体**：验证脚本自己成了污染源——它**修改被验证对象**，一旦中途死掉，工作树进入"看起来正常、实则挂着变异体"的状态；
  若当时直接 commit，就会把变异体当修法发出去（且测试会红，但如果变异恰好在未覆盖分支则静默）。
  **化解手法（可复用）**：① 改源码的一次性脚本一律 `try/finally` 还原；② 跑完显式核 `git diff --stat` 而非假设已还原；
  ③ Windows 上脚本输出避免 emoji，或统一 `PYTHONIOENCODING=utf-8`。
  **为何不升 should_update**：N=1，且属工具使用习惯而非流程缺陷；本次已被发现，无实际外泄。
  **触发升级**：≥3 次同类（一次性脚本中断污染工作树）→ 升 should_update，考虑写进
  [06-dod-and-evidence.md](../governance/workflow/06-dod-and-evidence.md) 变异测试段。来源：PR #226 review 修复。

- **2026-08-21（seg1 RP.G2 retro）**：新增 **O-DEGRADE-AMBIG-01 "『这条腿空了』在产物里分不出是「源答不了这个问题」还是「我们的表覆盖不全」"（N=1）**。
  实例：G2 让宏观源在认不出指标时**明确失败 → 整条腿降级**（backlog **BR** 实例① 的正面处置）。
  冒烟实测两种情形都会走到同一个出口：① 问「黄金会怎么走」—— **FRED 库里本来就没有现货金价**（G0 双验证坐实），
  这条腿空着**是对的**；② 将来某个**真宏观**问题因关键词表没收那个词而认不出 —— 这条腿空着是**我们的缺口**。
  两者在 `quality_flag` / `macro_payload` 里**长得一模一样**，唯一的区分线索藏在错误文本里，而错误文本不进产物结构。
  **为什么现在不动**：数据不足（N=1，且第二种情形今天还没实测到过）；
  更要紧的是**判据现在定就是凭空猜** —— 要区分它们，本质上需要"这个源覆不覆盖这个问题域"这个判断，
  而那正是 **G5 规划员**要做的事（它出计划时就该知道黄金不归宏观源管，压根不写这条腿）。
  ⇒ **很可能 G5 一接线这个歧义就自然消失**（腿根本不会被激活），所以现在造一套区分机制有白做的风险。
  **触发升级**：G5 接线后若该歧义**仍然存在**，或在此之前实测到第二种情形 ≥2 次 → 升 should_update，
  届时考虑在降级留痕里加一档"本源不覆盖该问题域"与"本源覆盖但没认出来"的区分。
  来源：[G2 冒烟与真 API 验证 §3](rp-g2-smoke-20260821/FINDINGS.md)。

- **2026-08-25（seg1 RP.G5.1 retro）**：新增 **O-SPEC-DRIFT-01 "说明书『倒推的输入规格』与落地构造参数漂移"（N=2）**。
  实例①：wisburg 说明书 §3 写字段 `category`，G4b 落地的构造参数叫 `library` —— 从 08-21 落地到 08-25 建 prompt 守护时才被发现（4 天无人察觉）。**已修**。
  实例②：同表 `top_k` 描述为"取几篇摘要"，实际构造参数 `top_k` 是列表条数；摘要篇数是独立参数 `summary_top_k`（上界 `MAX_SUMMARY_TOP_K=5`），原表缺此行。**code review #267 发现，同 PR 修**。
  **信号本体**：五份说明书是设计期"倒推"出来的输入规格，实现落地后**没有回写对齐的机制**；
  prompt↔说明书那半现在有守护（#267 指纹门 + 锚点门，其中一条锚就是钉 `library` 同名），**说明书↔源构造参数那半仍靠人**。
  **升级评估**：N=2，且均为同一张表同一次 review 发现；两处已修。G5.2 校验层落地时天然要再对一遍全部五源字段名，是免费的复查点。**暂维持不升级**，但触发线已从"≥1 处"收紧为"G5.2 对字段时若**再发现**同类 → 立刻升"。
  来源：[PR #267](https://github.com/JunoChenZt/subagent-for-investment/pull/267)。

- **2026-08-25（seg1 RP.G5.1 retro）**：新增 **O-PLANNER-LATENCY-01 "planner 出计划延迟贴近 15s 硬上界"（N=2）**。
  实例：真实冒烟两跑 —— 黄金 7.6s、茅台 **14.3s**（距 U3 第一笔 ≤15s 上界仅 0.7s）。deepseek-v4-pro 出长 JSON 是主要开销。
  超时后果有界：返回 None 走降级链（退回按标签路由），不崩、但那次 run 拿不到规划员的计划。
  **触发升级**：G5.4 接线后真实跑批里超时率 > 0 或 P95 贴顶 → 升 should_update，在 U3 框架内议（换更快模型 / 缩 prompt），**不静默上调 15s**。
  来源：[rp-g5-smoke-20260825/FINDINGS.md](rp-g5-smoke-20260825/FINDINGS.md)。

  > 🔴 **2026-08-27 G7 实测：触发条件已满足，本条升 should_update。**
  > 出计划+校验**中位数 11.5s / 天花板 15s，余量仅约 3.5 秒**；同句 6 次里 **1 次真超时降级**（超时率 > 0）。
  > **顺带查出一件更要紧的**：那 15 秒原本**根本不是硬上界** —— SDK 默认重试 2 次 ⇒ 最坏 ≈45s，
  > 实测跑出 44.3s（已修：规划员那条路 `max_retries=0`，见 [G7 FINDINGS §5](rp-g7-e2e-20260827/FINDINGS.md)）。
  > ⇒ **修完之后余量问题才露出来**：以前是"超时了还在重试"，现在是"真的就是不够快"。
  > **处置（按本条原文：不静默上调 15s）**：三条候选 —— 换更快模型 / 缩 prompt / 回 U3 框架议抬预算，
  > **均须用户裁**，且都超出 seg1 剩余范围 ⇒ **本条转入 backlog 候选**，seg1 收口时一并提。

  > ✅ **2026-08-28 用户已裁：抬预算线至 ≤25s**（三条候选里选「抬线」——改动最小、最可逆、不动模型行为；换更快模型 / 缩 prompt 留作后手）。**本条据此收口为待办，不再是待议观察**：
  > 已登记为 [S2 §4.7.5 **RP.G8**](../roadmap/S2.md)（含四处齐改的落地清单——漏掉外层封顶那处则抬线完全无效）。
  > ⚠️ **代码尚未改，今天仍是 15s**；本块存在即是为了不再重演 [BU「裁决落地无回填义务」](../governance/backlog.md)。

  > 🔴 **2026-08-28 同日翻案（据实记，不抹前一块）**：G5b 真人验收首跑连续两次超时 → 排查证明**本条赖以立项的「余量约 3.5 秒」是 N=1 问法的读数**。控制变量对照（同模型 · 系统提示词逐字节相同 · 输入 token 与缓存命中全同，**只换问句**）：G7 那句「黄金会怎么走」中位 **9.9s**、8 次零超线；另三句正常问法（含段式跑指南的标准问句）**6/6 超线、29.8–32.7s**。
  > ⇒ **耗时跟着输出长度走，输出长度由用户怎么问决定（差 2–3 倍）** ⇒ 「抬到 25s」不够、当日作废。
  > ✅ **同日重裁：≤40s**（= 三种正常问法实测最慢 32.7s + 约 22% 余量）。**本条至此收口**，✅ **同日已落地**（五处齐改·全量测试绿），见 [S2 §4.7.5 RP.G8](../roadmap/S2.md)。
  > 证据 [rp-g8-planner-latency-20260828](rp-g8-planner-latency-20260828/FINDINGS.md)；处置候选见 [S2 §4.7.5 RP.G8](../roadmap/S2.md)。
  > 📌 **本条真正的教训升级为方法论**：同一句话重复 N 次得到的是**那句话的方差**，不是**问法之间的方差** —— 与 [样本量不等于行数](../governance/backlog.md) 同源（**重复不产生独立观测**）。凡「按实测定线」的场合，先问一句**变的是什么、没变的是什么**。

- **2026-08-25（seg1 RP.G5.2 retro）**：新增 **O-COPIED-NEGATIVE-EXAMPLE-01 "把没核过的负例照抄进承重物"（N=1）**。
  实例：说明书 §5 的负例 `{"ticker": "600520.SH", "why": "模型记得是这个"}` 被我当成"编造码"**照抄进 planner prompt + 单测 + 冒烟对照组**三处；
  G5.2 冒烟走真名录时才发现 **600520.SH 是真实上市公司（三佳科技）**，从来不是编造码。
  **信号本体**：负例是**教材**——prompt 里的负例在教模型什么不该做，测试里的负例在定义"什么算被拦住"。
  照抄一个**没核过事实的负例**，等于把一条假事实同时焊进模型的行为与测试的判据（坑表第 7 条「自造 fixture 焊死猜测」的**变体**：
  这次不是自造，是**沿用他人未核的样本**，比自造更隐蔽——它看起来有出处）。
  **本次代价很小**（校验层行为正确、冒烟当场撞见），但同样的模式若发生在"某个失败形态的负例"上，会让守护测试**测一个不存在的病**。
  **顺带的正收益**：核实后这个负例变强了 —— 真实形态是「码存在但不是那一家」（同 BTC 截码家族），比"编个不存在的码"危险得多，已写进说明书与 prompt。
  **触发升级**：再出现 1 次「照抄未核负例进 prompt/测试」→ 升 should_update，考虑在 [06-dod-and-evidence](../governance/workflow/06-dod-and-evidence.md) 的测试设计质量清单里加一条
  「负例的事实性也要核，不因它有出处而豁免」。来源：[G5.2 冒烟](rp-g5-smoke-20260825/g52-validator-smoke.md)、[PR #268](https://github.com/JunoChenZt/subagent-for-investment/pull/268)。

- **2026-08-25（seg1 RP.G5.3 retro）**：新增 **O-OVERSTRICT-GUARD-01 "安全支柱写过严 → 把好货全退了，且反向变异测不出"（N=2）**。
  实例①：回核层「核返回代码与计划**逐字一致**」（设计 pass §3.5b 原文），照字面实现会把**每一条 A 股腿**误杀 ——
  行情返回的 `ticker` 是**裸六位**（`600519`），计划里写的是 `600519.SH`。〔**➡️ 2026-09-07 前向补记**（正文按 point-in-time 不动）：行情源已改为写**完整代码**（`DEFECT-CTX-BAG-SHAPE` ⑮ —— 切掉后缀会让覆盖判定那道「交易所对不上就挡住」在 A 股侧永远打不着）。**本观察点结论不变**：回核层取裸六位核对的写法**保留**（旧归档仍是裸码、计划两种写法都收），误杀风险与本条论断照旧成立。〕
  实例②：第 0 道「空手而归」判据首版只看顶层键，而研报/新闻改造后货装在 `_meta.reports` / `_meta.items` 里 ⇒ **有货的返回被判成空手而归**。
  **信号本体**：安全支柱的失败有两个方向 —— 「该拦的没拦住」和「不该拦的全拦了」。
  我们的验收纪律（反向变异）**只覆盖前者**：变异证得了"把检查删掉测试会红"，证不了"这个检查没有误杀正常输入"。
  更麻烦的是**产物上两者看不出区别**：误杀的结果也是"这条腿空了"，与"真没拿到"同形（与 O-DEGRADE-AMBIG-01 同源）。
  **本次的化解**：两个方向各钉测试 —— 正样本钉"不该拦的要过"（A 股裸码、子域算自己人），
  反向样本钉"别把放宽做成全放行"（真换了公司仍要拦、`_meta` 空仍算空手而归）；
  变异集里**专门加两条"误杀方向"变异**（子域不算自己人 / A 股逐字比较），12/12 全 KILLED。
  **为何不升 should_update**：N=2 且都在同一个 goal 内当场发现并修掉；更要紧的是**真实误杀率要到 G5.4/G7 才测得到**，
  现在把它写成流程规则等于凭 2 个样本定规矩。
  **触发升级**：G5.4/G7 真实数据下若出现「回核误杀」实例（尤其研报相关性回筛）→ 升 should_update，
  考虑在 [06-dod-and-evidence](../governance/workflow/06-dod-and-evidence.md) 的变异测试段加一条
  「安全支柱的变异集必须含误杀方向，正样本不可省」。来源：[G5.3 落地记录](rp-g5-smoke-20260825/g53-verifier-notes.md)、[PR #268](https://github.com/JunoChenZt/subagent-for-investment/pull/268)。

- **2026-08-26（seg1 RP.G5.4 retro）**：新增 **O-MUTATION-CATCHES-FALSE-GREEN-01 "反向变异抓出的不是产品缺陷，而是测试本身为错误的原因绿"（N=1）**。
  实例：G5.4 变异 **X4（kill-switch 失效）SURVIVED** —— 拆掉"关掉规划员就不调它"那道闸，测试**照样绿**。
  查因**不是产品坏了**：那条测试先装了计数桩，随后调用的辅助函数 `_run_node` **无条件覆盖**同一个函数，
  于是计数器永远是 0、**与开关根本无关** ⇒ 它从写下那一刻起就在为错误的原因绿。
  **信号本体**：反向变异的常规用途是"证明检查会拦"，本次它的实际收益是**证伪了一条测试的有效性** ——
  这正是坑表第 5 条形态⑧「被测系统多条路通往同一结果、测试没堵别的路」，
  而**只跑测试（哪怕全绿、哪怕反复跑）永远发现不了**。
  **可复用的判据**：测试与辅助函数**装同一个桩**时要问一句"谁后装谁赢"；
  凡"断言某个东西**没被调用**"的测试，尤其容易因桩被覆盖而恒真。
  **为何不升 should_update**：N=1，且现有纪律（每道闸配反向变异）已经把它抓出来了 —— 是纪律**生效**的证据，不是纪律有缺口。
  **触发升级**：再出现 1 次「变异抓出的是测试假绿而非产品缺陷」→ 升 should_update，
  考虑在 [06-dod-and-evidence](../governance/workflow/06-dod-and-evidence.md) 测试设计质量清单加一条
  「共享 fixture/辅助函数覆盖测试自装的桩」。来源：[PR #268](https://github.com/JunoChenZt/subagent-for-investment/pull/268)。

- **2026-08-26（seg1 RP.G5.4 retro）**：新增 **O-HALF-CLOSED-DEFECT-01 "缺陷有两条路，修了一条会看起来像全修好了"（N=1）**。
  实例：`DEFECT-FRED-SUBSTRING`（问毛利率拿回联邦基金利率）有**两条活路** ——
  ① 管道路径（G5.4 让计划点名编号，**已解决**）；② **分析师侧宏观工具**（`definitions._exec_fred`
  构造的是**不带计划**的源，走的还是子串匹配，**原封不动**）。
  更险的是：那条缺陷的**唯一守护测试挂在宏观安全网上**，而 G5.4 正好撤掉了安全网 ——
  **顺手删掉那条测试，缺陷就会看起来像修好了**（全仓再没有任何东西提它）。已把守护挪到 `_resolve_series`。
  **信号本体**：与 scout S1「账目归位空头支票」同族，但多一层 —— 不只是"账记得太早"，
  而是**撤掉旧机制时会连带撤掉它携带的守护**，于是"没有测试红"被误读成"问题没了"。
  **可复用的判据**：撤掉任何机制前，先问「**有没有别的东西的守护挂在它身上**」——
  grep 那个机制名，看命中的测试**实际在守什么**，不是在守这个机制的测试要**搬家**而不是删除。
  **触发升级**：再出现 1 次「撤机制连带撤守护」→ 升 should_update。
  来源：[PR #268](https://github.com/JunoChenZt/subagent-for-investment/pull/268)、[S2 §4.7.5](../roadmap/S2.md)。

- **2026-08-26（seg1 RP.G5b retro）**：新增 **O-REDUNDANT-CODE-MASKS-DEFECT-01 "冗余的保险代码会掩护真缺陷，让变异测试失效"（N=1）**。
  实例：`confirm.apply_edit` 结尾多盖了一次 `edited=True`，而校验层归一时**本来就原样带回**它 —— 纯冗余。
  反向变异 Y4 打在**承重**那行（`candidate` 的 `edited=True`）上时，**冗余行把结果补了回来 ⇒ 测试照样绿**，变异幸存。
  删掉冗余后 Y4 才咬得住。
  **信号本体**：写"保险起见再盖一次"看起来无害，实则**给缺陷加了一层掩护** ——
  它不改变正确行为，却让"这行代码承不承重"变得测不出来。
  与坑表第 5 条形态⑧（多条路通往同一结果）同源，但这里的第二条路是**我们自己出于谨慎加的**。
  **可复用的判据**：同一个字段在一条链上被赋值 ≥2 次时问一句「拆掉其中任意一处，会有测试红吗」——
  两处都拆不红 = 至少一处是掩护。
  **为何不升 should_update**：N=1，且现有纪律（每道闸配反向变异）把它抓出来了。
  **触发升级**：再出现 1 次「冗余赋值掩护变异」→ 升 should_update。
  来源：[G5b 落地记录](rp-g5-smoke-20260825/g5b-confirm-notes.md)、[PR #268](https://github.com/JunoChenZt/subagent-for-investment/pull/268)。

- **2026-08-26（seg1 RP.G5b retro）**：**O-MUTSCRIPT-01 补第二个实例（N=1→2·反方向）**。
  原条目（2026-08-06）记的是「改源码的一次性脚本无 try/finally，异常中断**污染**工作树」。
  本次是**反方向的同源问题**：变异脚本用 `git checkout -- <path>` 还原，
  而我在跑变异前有一处**正当但未提交**的改动 ⇒ 被脚本连带**冲掉**。
  后果不是污染而是**丢改动 + 误判**：Y4 第二轮仍幸存，一度以为是测试有洞，
  查了一轮才发现是自己的修复被还原了。
  **合并后的可复用纪律**：一次性改源码的脚本，**跑之前先 commit**（干净工作树是它的前提），
  跑完 `git status` 确认 —— 前者防"被还原"，后者防"没还原"。
  **触发升级**：本条已 N=2（两个方向各一），再出现 1 次 → 升 should_update，
  考虑写进 [06-dod-and-evidence](../governance/workflow/06-dod-and-evidence.md) 变异测试段。

- **2026-08-26（seg1 RP.G6 retro）**：**O-MUTATION-CATCHES-FALSE-GREEN-01 补第二、三、四个实例（N=1→4）**。
  G6 第一轮反向变异 7 条里**幸存 4 条**，逐条查因**全部是测试本身没用**，产品代码没错：
  - **Z3/Z4**（缓存读或写少带一段钥匙）：只拆一边 → 永远 miss → "换了计划要重新取"这个断言**照样成立**。
    该由**反向那条**（"计划没变**要**命中"）来抓 —— 我一开始把变异指错了靶。
    ⇒ 可复用判据：**验"该变的变了"必须配一条"不该变的没变"**，否则单向断言会被"永远失效"这种坏法蒙混过关。
  - **Z7**（同源两条腿共用一把钥匙）：第一遍两条腿是**并发**取的、缓存都还空，
    共用钥匙也各 fetch 一次 ⇒ 断言在**有病和没病时都成立**。撞车只在**第二遍**读缓存时现形。
    ⇒ 可复用判据：**缓存/幂等类的测试必须跑第二遍** —— 第一遍必然 miss，什么都证明不了。
  - **Z2**（钥匙没透传到 `build_common_context`）：那一层**根本没被测到**，只在下游 `dispatch_sources` 验了。
    ⇒ 可复用判据：**一条数据要穿过几层，就得在每层各有守护**，只测两端会漏中间。
  **累计 N=4**（G5.4 的 X4 + 本次三条）⇒ **已达原定升级线**。
  **升级评估**：这四次的共性是"反向变异的真实收益里，**证伪测试有效性**的占比不低于**证明检查会拦**"。
  但四次全部**被现有纪律当场抓住**（每道闸配反向变异），说明纪律**生效**、不是有缺口 ⇒ **暂不升 should_update**，
  改为**收紧触发线**：再出现 1 次「变异抓出测试假绿」→ **直接升**，并在
  [06-dod-and-evidence](../governance/workflow/06-dod-and-evidence.md) 测试设计质量清单加上面三条可复用判据。
  来源：[G6 落地记录](rp-g5-smoke-20260825/g6-cache-key-notes.md)、[PR #268](https://github.com/JunoChenZt/subagent-for-investment/pull/268)。

- **2026-08-31（seg1 RP.G8 全链跑）**：新增 **O-BEAR-PATH-CALLS-01 "空头那条路调用数持续高于多头"（N=2）**。
  实例：④ debate1 多头 2 次 / 空头 **5** 次；⑤ debate2 多头 2 次 / 空头 **7** 次。两段同向，空头走 `gemini-2.5-pro`（$0.165 → $0.274），
  多头走 `deepseek-v4-pro`。⑤ 段 checklist 有「远超 → 续写失控」但**未定线**，故本次判**不触发**；
  ⑥ 段续写上限未打满（最多 3 / 上限 4）⇒ **非失控形态**，更像该模型多一轮工具或重试。
  **触发升级**：再出现 1 次（N=3）或某轮打满续写上限 → 升 should_update，查 gemini 那条路多出来的调用是什么。
  来源：[rp-g8-e2e-20260831/FINDINGS.md](rp-g8-e2e-20260831/FINDINGS.md) §三.7。

- **2026-08-31（seg1 RP.G8 全链跑）**：新增 **O-AUDIT-CRITERION-MISMATCH-01 "audit 判据回答的不是我们担心的问题"（N=1）**。
  实例：⑧ 段 `audit_passed` **2/69 = 2.9%** 撞 5% 下沿 —— 按 [guide 08-14 读法](e2e-runs/segmented-e2e-guide.md)先看 `query_type`，
  本跑 `thematic` 属**结构使然**，记录后放行（**这一步按规矩走了，避开了「照错位口径下结论」的错判**）。
  ⚠️ **但**同一批数据里，67 条 `audit_notsure` **有 66 条带精确数字**。
  **信号本体**：「2.9% 结构上正常」与「96% 的精确数字无人核」**两句都对，而判据只回答了前一句** ——
  判据量的是「audit 机制有没有坏」，我们担心的是「数字有没有保障」，**不是同一件事**。
  与 [DEFECT-GATE-NA-AS-PASS](../governance/backlog.md) 同族（**检查没错，是它答的题不是我们问的题**），
  但那条讲的是**呈现**、这条讲的是**判据的量程**。
  **触发升级**：再出现 1 次「判据放行而担心的事没被覆盖」→ 升 should_update，在
  [e2e-acceptance-standard](../governance/e2e-acceptance-standard.md) 里补「这条判据覆盖不到什么」一栏。
  ⚠️ **本次刻意不动任何判据**（改判据 = 承重变更须用户裁）。
  来源：[rp-g8-e2e-20260831/FINDINGS.md](rp-g8-e2e-20260831/FINDINGS.md) §三.8。

- **2026-09-22（backlog BK close）**：新增 **O-BK-01 记账清单（28 条·不累积 N）** —— 静默降级可见化两本账归零（登记待补 0 站 · 盘点真待补 0 行）后 BK close-by-completion，各批 review / 量基线裁「不修只记」的 27 条 + 1 条留存事实整体迁入，各带事件型触发条件；处置后就地标 ✅。来源：[backlog BK 行](../governance/backlog.md) · [bk6 §7](bk6-20260922/FINDINGS.md) 等。
- **2026-09-23（CRED.2.G0 retro-goal）**：新增 **O-CRED-01**（N=1）—— 时效判据的输入本身不干净（外源册 1/3 缺日期 + 粗精度年份归一成 1 月 1 日），裁阈值前先量输入干净度。来源：[cred-2-g0 FINDINGS §3.5](cred-2-g0-asof-dist-20260923/FINDINGS.md)。
- **2026-09-23（CRED.2.G3 retro-goal）**：新增 **O-CRED-02**（N=1）—— 局部只降不升 ≠ 全链只降不升：审核降 notsure 会让执行底线 check③ 看不见过期价位；用户裁改为可信度落过期。
- **2026-09-23（CRED.2.G4 retro-goal）**：新增 **O-CRED-03**（N=1）—— 回核筛研报只改了结构化记录、分析师读的正文没跟着改（主干 29 篇漏进上下文·已修）。
