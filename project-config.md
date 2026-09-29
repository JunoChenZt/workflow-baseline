# project-config — 项目配置槽位（骨架读这份，别的项目只改这份）

> **三层关系**：[core/](core/README.md) 是通用骨架（规则本体，不含任何项目名词）；本文件是**项目配置**（骨架里所有 `{{key}}` 的取值）；[docs/governance/workflow/](docs/governance/workflow/README.md) 是骨架在 `subagent-for-investment` 项目上的**实例层**（规则 + 项目参数 + 历史证据）。
>
> **接入别的项目 = 复制 core/ + 复制本文件改「本项目值」列**。骨架文档本身不用动。
>
> 骨架里写 `{{tier.s.max_files}}` 这种形式的地方，取值就在下面对应行。「说明」列写这个槽位为什么存在、改它会影响哪一步。

## 0. 项目身份

| key | 本项目值 | 说明 |
|---|---|---|
| `project.name` | `subagent-for-investment` | 只用于命名与引用 |
| `project.instructions_file` | [CLAUDE.md](CLAUDE.md) | 给 AI 读的项目顶层指令；骨架的接入片段复制到这里 |
| `project.north_star` | 装备决策者，不取代决策者：不自动下单 / 调仓 / 进入任何无人确认的资金链路 | 刹车 Q3 与红线的语义来源；别的项目换成自己的「永不越线」一句话 |

## 1. 红线与确认清单（刹车 Q1–Q4、执行中硬边界读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `red_lines` | 触及北极星（自动决策 / 资金动作 / 弱化合规文案）；生产部署 / 改 `.env` / CI secrets / repo settings；不可逆 DB 操作（生产 migration / `DROP` / `TRUNCATE` / 批量 `UPDATE`）；`git push --force` / `reset --hard` 到非工作分支；批量删除文件 / 清理归档与证据；仓库设为 public | **任何档位、任何步骤**触到即立即停，不等判定。来源 [CLAUDE.md](CLAUDE.md)「强制红线」 |
| `confirm_before` | 改 `.claude/settings.json` / `CLAUDE.md` / 权限配置；改主依赖版本（patch 升级除外）；在工作分支之外做远程可见操作 | 不是红线，但动之前先问。来源 CLAUDE.md「需要确认」 |
| `autonomous_scope` | 在 `auto/<node-id>` 工作分支内任意 git 操作；删远程 PR 分支；改 CI 配置；改代码与文档。**例外**：docs-only 维护类小步提交可直接 main | 骨架 S 档「可不开 PR」的边界由这里定 |

## 2. 分档与路由（core/01 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `tier.s.max_files` | 3 | S 档判据 1：改动文件数上限。**初值，WARN 试用**，按 `tier.metrics` 季度调 |
| `tier.s.max_lines` | 100 | S 档判据 2：增删合计行数上限。同上 |
| `tier.s.same_dir_rule` | `src/<模块>/` 与配对的 `tests/` 算同一处 | S 档判据 1 的「同一顶层目录」怎么算 |
| `sensitive_paths` | schema / prompt / fallback / 路由 / 闸门与质检判据（gate、acceptance、quality）；配置目录、`.env*`、`.claude/settings*`、权限配置；`.github/`、migrations、`pyproject.toml` / `requirements*.txt` / lock；生产部署脚本与 runbook | diff 里出现即至少 M 档；与 `risk.high_triggers` 之一同时命中即 L |
| `risk.high_triggers` | ① 触及 schema / prompt / fallback / 路由（已完成节点的契约）② 触及硬拦截决策路径 / 合规边界 ③ 跨 ≥ 2 个阶段或子阶段 ④ 新外部依赖 / 新数据源 / 新 API（须同步跑 [source-readiness-checklist](docs/infrastructure/source-readiness-checklist.md)）⑤ 改归档回放兼容性 | 风险判定五条；任一命中 = 高风险 = L 档 |
| `big_task_triggers` | ① ≥ 2 个模块 / 目录 / 阶段 ② 触及核心链路（schema / prompt / runtime / fallback / 归档回放 / CI）③ 新增能力而非单点修复 ④ 多 agent / 多子任务 / 多验收标准 ⑤ 需要跑完整 DoD / corner case / 冒烟 / observation ⑥ 10 分钟内无法完成并验证 ⑦ 路线图标为大节点 | 大任务判定七条；任一命中 = 大任务 |
| `tier.metrics` | [metrics.md](metrics.md) 表 2「PR 台账」的档位列（`S → M` 计升档）与返工列 | 调 `tier.s.*` 阈值的依据；`scripts/metrics_report.py` 汇总 |
| `tier.router` | 第一版 = `scripts/tier_check.py`（按 diff 算 S 判据 1–3 与最低档位；判据 4–5 与「是否 L」提示人核；CI PR 事件 WARN 试用） | ⏳ **仍待商量**：用户 2026-09-29 提出「分档标准后面要再细化、可引入路由机制」。脚本只是种子：阈值与敏感路径读 §10 机器可读块，细化标准时改块不改脚本；要做成真正的路由器（输出「走哪些步骤」）时扩这一格 |

## 3. 任务来源与账本（core/01 / 02 / 06 / 07 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `roadmap_file` | [docs/roadmap/S2.md](docs/roadmap/S2.md)（S2 已收口）/ `docs/roadmap/S3.md`（未打包进本仓） | 任务清单与节点状态；pre-flight 第 1 问「上游 done 了吗」查这里 |
| `roadmap.node_id_pattern` | `A6.1.x` / `P4.B.x` / `CRED-1.Gx` 等 | 节点 ID 长什么样；工作分支 `auto/<node-id>` 用它 |
| `design_truth_source` | [docs/roadmap/roadmap-v3.4.md](docs/roadmap/roadmap-v3.4.md) | pre-flight「顶层对齐」读这里；拆解方向不能偏离它 |
| `backlog_file` | [docs/governance/backlog.md](docs/governance/backlog.md) | 坐实 finding「记账」去处；条目配额上限见其 §4.4 |
| `plans_dir` | `docs/plans/` | 拆解产物 `<node-id>-decomposition.md` 落这里 |
| `retro_dir` | `docs/retro/S2/`（S3 起换 `docs/retro/S3/`） | 节点 retro 文件 `<node-id>_<YYYY-MM-DD>.md` |
| `observations_dir` | `docs/observations/` | 冒烟归档、回放脚本、探针产物 |
| `observation_ledger` | [docs/observations/should_update_observations.md](docs/observations/should_update_observations.md) | retro 三档里 observe 的登记处；累积 ≥ `retro.observe_promote_at` 升级 |
| `pitfall_table` | [docs/governance/workflow/09-known-pitfalls.md §3](docs/governance/workflow/09-known-pitfalls.md) | 已知坑表；按 core/08 的标记体系维护 |

## 4. 验证手段与阈值（core/03 / 05 / 07 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `verify.unit` | `pytest tests/<受影响文件> -v`；全套 `pytest`（≈ 4300 条） | 自验 `<command>` 与 DoD Corner Case 的默认手段 |
| `verify.lint` | `scripts/lint_doc_links.py`（文档链接）/ `scripts/lint_env_registry.py`（配置对账）/ pyflakes | S 档判据 5「现成验证手段」的候选 |
| `verify.smoke` | 端到端最小 query：1 个个股 + 1 个宏观事件；整跑不崩；fallback 报告比例不上升 | DoD 第 3 步「冒烟」的定义；S 档不要求 |
| `verify.smoke_guide` | [段式跑指南](docs/observations/e2e-runs/segmented-e2e-guide.md) → 跑完接 [质量门](docs/governance/e2e-quality-gate.md) | 实跑前必读；分段跑避免出错重头 |
| `budget.latency` | P50 < 60s / P95 < 120s（**目标线**，实测端到端 379–535s，长期未守） | 自验报告 / 冒烟输出里的对照值；超了 flag 不阻塞 |
| `budget.fallback_ratio` | 不高于上一基线 | 冒烟判据；上升 → `quality_flag` |
| `contracts` | `DEBATE_KEY_CLAIMS_CONTRACT` / `EXECUTION_PLAN_CONTRACT` / 各角色 prompt 不可覆盖段 | DoD Code Review「契约」视角对照物 |
| `archive_replay` | 旧归档喂新 schema 必须能回放 | 动 schema 的 goal 必带；不动则 evidence 写 N/A + 理由 |
| `acceptance_standard` | [e2e-acceptance-standard.md](docs/governance/e2e-acceptance-standard.md)（新检查一律 WARN 试用，升 hard-fail 需用户裁） | 任何新增自动检查的登记处 |

## 5. 节奏与配额（core/07 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `wip_limit` | 3 个工作分支同时 open；超过需人工确认 | 并行上限；出现账本 / PR / 证据混乱自动降到 2 |
| `goal.time_budget` | 小 ≤ 30 min / 中 30–90 / 大 > 90 → 再拆 | 单 goal 预算 |
| `node.size` | 1–3 天 = 1 节点；超过拆子节点 | 节点粒度 |
| `retro.must_update_cap` | 每次 retro 1–2 条 | 数量门槛，防流程噪音 |
| `retro.observe_promote_at` | 连续 ≥ 3 次同类 | observe → should_update 的升级线 |
| `backlog.quota` | lettered 活跃条目上限见 backlog §4.4；DEFECT 族不占配额 | 「记账」去处的容量约束 |

## 6. Git 与 PR（core/07 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `git.work_branch` | `auto/<node-id>`，节点合并后即删 | 工作分支命名 |
| `git.commit_prefix` | `feat` / `fix` / `docs(baseline)` / `docs(retro)` / `docs(todo)` / `docs(backlog)`；细则 [git-workflow.md](docs/governance/git-workflow.md) | commit subject 约定 |
| `git.merge` | squash；PR title = main 上 commit subject；PR body 进 commit body；head 分支自动删（stacked PR 会漂 base） | PR 模板「复盘只放 TL;DR」的原因 |
| `git.utf8` | commit body 别放 emoji（heredoc 编成乱码）；文件名含中文用 `ls-files -z` | 已知坑 |

## 7. 里程碑交接（core/07 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `milestones` | S2.1 / S2.2 / S2.3（S2 已于 2026-09-28 收口；S3 里程碑待定义） | 交接审视触发点，每个里程碑一次 |
| `milestone.hard_fail_checks` | S2.1：6 项（m4/m5/m6/m7/m8/m13）= 0、fallback 比例 ≤ 基线、旧归档回放全过、P95 < 120s；S2.2：30 跑 schema hard fail = 0、单次返工修复率 ≥ 80%；S2.3：全链路通过 + 引用率 > 50% | 交接报告的 PASS / FAIL 判据；别的项目换成自己的 |
| `milestone.report_dir` | `docs/observations/{sN}-verification-report-YYYY-MM-DD.md` | 交接报告落地路径 |

## 8. Agent 与工具环境（core/README 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `task_prefixes` | `[GOAL]` / `[STEP]` / `[TASK]` | 任务描述前缀；`[GOAL]` 完成触发 hook 提醒跑刹车 / DoD / retro |
| `hooks` | TaskCompleted → pending 队列 → UserPromptSubmit / SessionStart 注入 goal-done 提醒；PreToolUse 拦 `--resume` 续跑要求确认 | 程序层闸门；与骨架的语义层规则双层独立 |
| `subagents` | `pitfall-scout`（起步扫坑表）/ `verification-report`（里程碑交接） | 两个 subagent 化 skill；其余 7 个 SKILL.md 已 deprecated，规则本体在文档 |
| `comms.style` | 中文；结论先行；非技术语言；代码符号不当句子主语 | 交付单与对话收尾的表达要求，来源用户级指令 |

## 9. 自动检查与台账（core/README §5、core/07 §2 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `checks.registry` | [checks.md](checks.md) | 每道自动检查的登记：抓什么 / 「它会响」证明 / 误报预算 / 承重 / 上次响。**先登记再写脚本再接 CI** |
| `checks.ci` | [.github/workflows/checks.yml](.github/workflows/checks.yml) | self-test + lint_links 断链 = hard-fail；其余 `continue-on-error` |
| `checks.link_scope` | 见 §10 机器可读块：维护层（骨架 / 配置 / 台账 / 实例层工作流文档） | 链接检查只扫这些；51 个快照引用文件的二级链接指向未打包文件，不在范围（已知 1000+ 条，不算断链） |
| `metrics.ledger` | [metrics.md](metrics.md) | 表 1 规则命中台账、表 2 PR 台账 |
| `metrics.retire_after_days` | 90 | 零命中超过这个天数进退役候选（只报，退役走 core/08 §2 协议） |
| `metrics.report` | `python scripts/metrics_report.py` | 里程碑交接时跑；输出退役候选 + 月度趋势 |

## 10. 机器可读块（脚本读这里，与上面表格同义；改阈值改这里）

`scripts/_config.py` 解析下面这个围栏。`sensitive_paths` 是正则，对 diff 里的路径 `search`；`core_leak_terms` 是骨架里不许出现的项目名词；`same_dir_pairs` 里的目录对视为同一顶层目录。

```json project-config
{
  "tier": {
    "s_max_files": 3,
    "s_max_lines": 100,
    "same_dir_pairs": [["src/", "tests/"]]
  },
  "sensitive_paths": [
    "(^|/)schemas?/", "(^|/)prompts?/", "fallback", "(^|/)rout(er|ing)",
    "gate", "acceptance", "quality",
    "(^|/)config/", "\\.env", "\\.claude/settings", "^\\.github/",
    "migrations/", "pyproject\\.toml$", "requirements[^/]*\\.txt$", "\\.lock$",
    "deploy", "runbook"
  ],
  "core_leak_terms": [
    "S2.1", "S2.2", "S2.3", "S2todo", "A6.1", "P4.B", "CRED-", "RDR-1", "PR-8",
    "committee", "fund_mgr", "tushare", "yfinance", "智堡",
    "DEBATE_KEY_CLAIMS", "EXECUTION_PLAN_CONTRACT",
    "docs/roadmap", "docs/observations", "docs/retro", "docs/plans", "backlog.md", "CLAUDE.md"
  ],
  "metrics": {
    "ledger": "metrics.md",
    "retire_after_days": 90
  },
  "checks": {
    "link_scope": [
      "README.md", "project-config.md", "checks.md", "metrics.md",
      "core/", "docs/governance/workflow.md", "docs/governance/workflow/"
    ]
  }
}
```

## 11. 尚未填的槽位

- `milestones` 的 S3 定义
- `tier.router` 的完整路由器（输出「走哪些步骤」，见 §2）
