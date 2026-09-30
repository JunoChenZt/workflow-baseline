# CLAUDE.md — subagent-for-investment

本仓库的 Claude Code 协作约定。**优先级高于任何默认行为**。

## 北极星（永不越线）

**装备决策者，不取代决策者。**

❌ 永远不做：
- 自动下单 / 调仓 / 触发任何真实交易
- 调用券商、交易所、支付类 API 执行资金动作
- 任何"无人确认"地进入资金链路的行为

执行计划、触发器、提醒、组合分析、历史对比 — 这些是装备决策者，可以做。

## 强制红线（任一触发即立即停下问）

- 触及北极星（自动决策路径 / 资金动作 / 弱化合规文案）
- 生产部署 / 修改 `.env` / CI secrets / GitHub repo settings
- 不可逆 DB 操作（生产 migration / `DROP` / `TRUNCATE` / 批量 `UPDATE`）
- `git push --force` / `git reset --hard` 到非节点工作分支
- 批量删除文件 / 清理 archive / 清理 observation 证据
- 把 GitHub 仓库设为 public

完整 8 问刹车机制见 [docs/governance/workflow/05-brake-self-check.md](docs/governance/workflow/05-brake-self-check.md)；不确定是否触发 → 默认按"触发"处理。

## 自主范围（无需确认即可执行）

默认在节点工作分支上推进（命名 `auto/<node-id>`，如 `auto/A6.1.2`）。这是 `main` 的副本，给 Claude 自主推进 plan 用，节点合并后即删：

- 在节点工作分支内执行任意 git 操作（commit / push / 分支增删 / `gh pr` 全套）
- 删远程 PR 工作分支、改 CI 配置、改任何代码文档
- 仓库 private，产出只在内部流转

**例外（默认 main，不切节点工作分支）**：observation / ledger / docs-only 维护类小步提交（OBS-FIX、run-counter 落账、dated snapshot 等）。仅当 commit 不涉及代码逻辑、不影响主链路时适用。

不在自主范围内、又不在例外内 → 切节点工作分支 `auto/<node-id>`。两者都拿不准 → 停下问。

详细 git 规则（commit prefix、节奏、已知坑）见 [docs/governance/git-workflow.md](docs/governance/git-workflow.md)。

## 需要确认（先停下问我）

- 改 `.claude/settings.json` / `CLAUDE.md` / 权限配置
- 改 `requirements.txt` / `pyproject.toml` 主依赖版本（patch 升级可自主）
- 在节点工作分支之外做远程可见操作（推 main、合 main、改 main 上 CI 等）

## Workflow 入口

S2 阶段任务推进遵循 10 步主链路：

> 大任务 → 风险判定 → (高风险拆解 + 用户确认 / 低风险自走) → /goal → 自验 → 刹车自检 → DoD → evidence → goal 级 retro（按需）→ 节点级复盘 → PR

完整流程图、`/goal` XML 模板、DoD 四步详情见 [docs/governance/workflow.md](docs/governance/workflow.md)。

### 何时读基准文档

任务涉及以下任一情况时，**先读 [docs/governance/workflow.md](docs/governance/workflow.md) 再开工**：
- 用户提到 S2todo 节点 ID（A6.1.x / P4.B.x / FM-3p.x 等）
- 用户提到 "S2.1 / S2.2 / S2.3" 子阶段
- 任务触及 schema / prompt / fallback / archive replay / 路由
- 任务可能是大任务（涉及 ≥ 2 模块或核心链路）

不确定是否触发 → 默认按"触发"处理，读完再开工。

## Skill 体系

**真值源**: `docs/governance/workflow/` 子文档 (11 个)

**2 个 active subagent skill** (Task tool 显式调用):
- [pitfall-scout](.claude/skills/pitfall-scout/SKILL.md) — 扫已知坑表,subagent 模式
- [verification-report](.claude/skills/verification-report/SKILL.md) — 子阶段交接审视,subagent 模式 (2026-05-25 S2.1 首次实战 PASS)

**7 个 deprecated SKILL.md** (2026-05-14 标 deprecated,不删除作为设计参考):
详见 [.claude/skills/README.md](.claude/skills/README.md)

**关键**: 主 Claude 应该读 workflow 子文档执行规则,**不**通过 deprecated SKILL.md 中转。

## Task 前缀约定

每个 task description **必须**用以下前缀:

- `[GOAL]` — goal-level 任务,TaskUpdate 标 completed 时触发 TaskCompleted hook(产出 goal-done-reminder 提醒)
- `[STEP]` — goal 内的步骤,不触发 hook
- `[TASK]` — 杂项任务,不触发 hook

**示例**:
- `[GOAL] A6.1.1.1 schema + role 注册`
- `[STEP] 写 schema.py 含 QueryType enum`
- `[TASK] grep 现有 ROLES 看 query_class 命名风格`

**为什么**: TaskCompleted hook(`task_completed_to_pending.py`)基于 `[GOAL]`
前缀识别 goal 完成事件,写 pending 队列;UserPromptSubmit / SessionStart
hook(`pending_to_context.py`)读队列并注入 goal-done-reminder 提醒,
驱动主 Claude 跑 brake-self-check / DoD / retrospective-goal 评估。
没有前缀 = TaskCompleted hook 跳过该 task = 程序层闸门失效,仅靠本段语义层兜底。

## Skill 触发强制规则

> ℹ️ hook additionalContext 注入经路径 D 重写后在当前环境**已验证可用**
> (2026-05-19,全 7 case 通过)。2026-05-14 "VS Code 扩展通道限制" 归因已翻案
> 为伪根因 —— 真因是 Claude Code API 改名(TodoWrite→TaskCreate/TaskUpdate)
> + 输出缺 hookEventName 字段(详见 backlog 条目 L 翻案)。
>
> 本段 "Skill 触发强制规则" 与 hook 构成**双层防御**:hook = 程序化确定性
> 闸门(TaskCompleted→pending→注入);本段 = 语义层(主 Claude 读 workflow
> 子文档执行判断)。两层独立,任一失效另一层仍兜底,非主备关系。

A6.1.1 实证 7/9 普通 skill 全节点 0 触发。**workflow 子文档是真值源**,
主 Claude 必须直接 Read workflow 子文档执行规则,不通过 SKILL.md 中转。

**每个 [GOAL] 完成时** (TaskUpdate 标 completed),主 Claude 必须按顺序:

1. 跑 brake-self-check 8 问 → Read [docs/governance/workflow/05-brake-self-check.md](docs/governance/workflow/05-brake-self-check.md) §2.7
2. 跑 DoD 4 步 → Read [docs/governance/workflow/06-dod-and-evidence.md](docs/governance/workflow/06-dod-and-evidence.md) §2.8
3. 评估 retrospective-goal 6 条触发 → Read [docs/governance/workflow/07-retro-goal.md](docs/governance/workflow/07-retro-goal.md) §2.10.1

**节点收口前** (所有 [GOAL] done):

1. 跑 retrospective-node 5 问 → Read [docs/governance/workflow/08-retro-node-and-pr.md](docs/governance/workflow/08-retro-node-and-pr.md) §2.11
2. 起草 PR 描述 → 同上 §6

**子阶段交接时** (S2.1 / S2.2 末节点 PR 合并后):

显式派 verification-report subagent → Read [docs/governance/workflow/10-verification-report.md](docs/governance/workflow/10-verification-report.md)

**子阶段 gate close 前** (S2.X 第一轮 agent 工作完成后):

执行 Agent 现状审视 → Read [docs/roadmap/S2.md](docs/roadmap/S2.md) §4.6，产出 `docs/governance/agent-review-s2.X.md`

**节点起步前** (大任务进入后):

显式派 pitfall-scout subagent → Read [docs/governance/workflow/09-known-pitfalls.md](docs/governance/workflow/09-known-pitfalls.md)

**跑 e2e 前** (用户/任务含 `committee analyze` / "跑 e2e" / "段式跑" / `--stop-after` / "quality gate" / pipeline 整链路跑批):

Read [docs/observations/e2e-runs/segmented-e2e-guide.md](docs/observations/e2e-runs/segmented-e2e-guide.md) — 9 段映射、停点选择、续跑命令、产出位置。
仅改 e2e gate 配置 / 写 e2e 相关测试 / 读历史 archive 而不实跑 → 可跳过；
任何"实际启动 pipeline 跑批"动作前必读，避免一口气从头跑、出错重头烧 token。

**跑完 e2e 后**：跑 quality gate → Read [docs/governance/e2e-quality-gate.md](docs/governance/e2e-quality-gate.md)。

**给 gate 新增 / 调整检查前**：先在 [docs/governance/e2e-acceptance-standard.md](docs/governance/e2e-acceptance-standard.md) 登记维度归属 + 承重边界（hard-fail / advisory），遵守 §4 试用期规则——**所有新检查一律 WARN 试用，升 hard-fail 需用户裁决**。

**违反规则 = 触发 §2.7 Q5 (标准降低)**。

## Session 启动检查

每次 session 启动时，距离上次查看 [docs/governance/backlog.md](docs/governance/backlog.md) > 7 天 → 主动 view + 提示用户哪些 backlog 条目触发条件已满足。

实现方式：用 auto-memory 记 `backlog-last-review-date`，每次启动比对今天。

## 计划与状态

- 阶段待办：[docs/roadmap/S2.md](docs/roadmap/S2.md) / [docs/roadmap/S3.md](docs/roadmap/S3.md) / [docs/roadmap/S4.md](docs/roadmap/S4.md)（S2 ✅ 已收口 2026-09-28 · S3 可启动、尚未开工）
- **过程层基准**：[docs/governance/workflow.md](docs/governance/workflow.md) — workflow 详细规则、流程图、DoD 模板、已知坑表
- **Git 工作流**：[docs/governance/git-workflow.md](docs/governance/git-workflow.md) — commit prefix、节奏、push 已知坑、UTF-8 约束
- 详细架构设计：[docs/roadmap/roadmap-v3.4.md](docs/roadmap/roadmap-v3.4.md)（单一真值源）
- 推进时按 [docs/roadmap/S{N}.md](docs/roadmap/) 当前依赖与状态执行；每个 PR 完成后更新对应阶段 ledger

## 链接规范

所有引用到仓库内文件、文档、日志、报告、证据路径的地方，都必须使用 Markdown 活链接，而不是纯文本路径。
若文件路径不确定，不得伪造链接；应明确标注"路径待确认"。

## Plan / 设计文档规范

所有写入 [docs/plans/](docs/plans/) 的 plan / 拆解 / 设计文档，必须**同时服务两类读者**——**导读看得懂、正文做得出**：

- **非技术读者**（基金经理 / 产品 / 合规）：文档开头放一段**大白话导读**——每个子任务"做什么、为什么"，用类比讲清，**不出现**代码符号 / 文件名 / schema 名。
- **技术读者**：正文给出**用了什么**——涉及的文件、schema、节点、复用的现有机制（带 file:line 活链接），可直接据此执行。

双层写法参照 [docs/pipeline/dataflow-whole-pipeline.md](docs/pipeline/dataflow-whole-pipeline.md)。

## 默认沟通风格

> **基线在用户级 CLAUDE.md**（用户主目录 `.claude/` 下，不在本仓库内）「表达方式」一节：任何时候交流都用非技术、通顺的语言（结论先行 / 代码符号不当主语 / 一句话一件事），那里有正反案例和自检标准。本节是在此基线上的**项目特化补充**，冲突时以用户级为准。

- 中文回复，技术术语保留英文（术语可保留，但不得拿它当句子骨架——见用户级案例）
- 简短直接，不复述用户已知信息
- 拿不准的判断先问，不要默认走"激进路径"
- **事实纠错优先（R4，PR-C-incident 沉淀）**：当用户陈述与已知事实不符（如"还没 push"但已 push / "还没 commit"但已 commit / 任何数字/状态错位），下一句必须**先纠正事实**再做其他事。不允许"先跑验证命令拖延纠正时机"或"配合用户假设继续推进然后顺便提一句"——纠正必须显式且在前。
- **先证设计再判 bug（R5，F1-graph-join 事故沉淀，2026-06-11）**：判定"这是 bug 还是设计"之前，必须先 review 过设计文档 / 代码注释 / commit 记录等一手材料；一手材料缺失时，显式标注**"以下为推断，未经设计记录证实"**，并在动手修复前向用户确认设计意图。**禁止把自己推断的设计意图当应然直接开修。** 出处：fm-spec e2e 期间从 resume 异常反推 graph 拓扑"bug"并直接提出修法，被用户叫停后补查 dataflow 文档 / #135 commit / fresh 拓扑实验——结论虽与推断一致，但流程顺序错了：一手证据应在修法之前，不是之后补。
- **读 run / 归档记录先认 main 的 tracked 版本（R6，seg9-VERDICT 误判事故沉淀，2026-06-12）**：任何以 run 记录 / checkpoint / calls / trace / observation 归档为一手源的任务，**必须从 main 的 tracked 版本读**（`git show origin/main:<path>`），**不得只看当前分支工作树**。因为正式归档 commit 在 main，而调研 / 排查任务常在与 main 分叉的节点工作分支上跑——当前分支工作树里同名目录可能只剩**未跟踪残留**（失败转储 / 重试中间产物 / 清洗版），把残留当证据全集，会把"成功跑过"误判成"从没跑过"，措辞天差地别。开工前先 `git ls-tree origin/main <dir>` 拉正式归档清单，再据此读；`git status` 里目录是 `??` 未跟踪 = 强信号：正品在 main、本地是残留。出处：seg1-9 全链调研在 `auto/pr8c-fm-bagua-stalled` 分支跑，工作树只有 `FAILED-*` 残留，据此误断"seg9 八步未验证"；实际 main 上 tracked 的 `seg9-decision.*` 是完整成功记录（SELL / conf 6 / 49 claim_audits / prose_gate verified）。**这是 R4「先纠正事实」在证据源层面的前置：源选错，纠正再快也是错的。**
- **状态变更全仓收口（R7，PR2 关门口径切换沉淀，2026-06-26）**：任何**状态切换**（PR close/merge、决策翻案、flag 放弃、节点收口、defer→取消、口径从"留门"变"关门"等）落地时，**不允许只改"当下想到的那几处"**——必须按四步收口：① **宽 grep 全仓扫**该状态的所有引用，关键词要含**别名 / 旧框架词**（凭记忆列点必漏：本轮自列 7 处，宽 grep 实扫出 13 处 live + 5 处历史/规划）；② **区分 live 状态 vs 历史记录**——live（断言"现在"状态的导航 / 状态表 / 条目）**就地改口径**；历史 / 规划 / retro（point-in-time 记录）**加前向 banner 标 superseded、正文不动**（改正文 = 篡改历史）；**⚠️ 历史里还要再切一刀（2026-08-06 #226 收口实证）**：**closed backlog 条目 / 已冻结 verdict / 节点 retro = [Q6 冻结档](docs/governance/workflow/05-brake-self-check.md)，连 banner 都不加、连读法注解和错别字都不改**，前向事实一律写去**引用方**（活条目 / 真值源文档 / 入口导航）。只有"未冻结的历史/规划文档"才走"加 superseded banner、正文不动"。出处：#226 按本条原二分法走，closed 条目落进"历史"档 → "加 banner"看似合规 → 直接撞 Q6，其中 BB 的 banner 更明写"保留不改"（已 revert，前向事实改落 endgame §5）。**这不是执行体疏忽，是 R7 与 Q6 的规则接缝**；③ **连带项一并处理**——被取消的子任务、被移除的职责、相关 memory（含 MEMORY.md 索引）、对外可见的 PR/issue 评论，都要同步；④ 收口后**再 grep 一遍**确认 live 旧措辞清零（残留只应是"否定旧框架"的新文字）。出处：PR2 #161 关门时旧"留门"口径（PARKED / 可议翻 flag / 门修好就翻 / 为翻 flag 备料）散在 backlog / S2 / design / memory / 多个规划文档十余处，靠一次宽 grep 才扫全——避免"扫不干净、留旧措辞在角落 → 将来文档自相矛盾"。**这是对此前『状态变更缺收口』诊断的方法补全：以后按本套路走，不靠碰巧想到。**