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

## 2. 分档与路由（core/01 读这里 · v2 · 2026-09-29 七点裁定）

| key | 本项目值 | 说明 |
|---|---|---|
| `tier.router` | `scripts/router.py`：入口 `--planned <files> --h1/--h2/--h3`；DoD 前 / CI `--base <ref>`（H 与声明档位从 PR 描述读）；`--json` 给工具用 | 由事实推档位、出路由卡（必做 / 不要求 / 验证命令 / 停止条件）；声明低于算出即报。**WARN 试用** |
| `tier.buckets` | tests / docs / infra / config / src / other（正则见 §10，顺序即优先级） | F1：每个路径归一个桶 |
| `tier.s_limits` | src ≤ 3 文件 ≤ 100 行；tests ≤ 5 / ≤ 300；docs ≤ 5 / 不限行；config、infra 任何改动不是 S；other ≤ 3 / ≤ 100 | 按桶分开的 S 上限；**初值 WARN 试用**，按 `tier.metrics` 季度调 |
| `tier.same_dir_rule` | `src/` 与配对的 `tests/` 算同一顶层目录 | 跨顶层目录即至少 M |
| `tier.test_map` | `src/<模块>/<名>.py → tests/test_<名>.py`；`scripts/<名>.py → tests/test_<名>.py` | F6：src 文件找不到配对测试即不满足 S |
| `tier.dependency_files` | `pyproject.toml` / `requirements*.txt` / lock 文件 / `package.json` | F5：有改动即 L |
| `paths.l` | schema / prompt / migrations / `.github/` / 依赖清单 / `.env*` / `.claude/settings*` / deploy / runbook | F3：命中即 **L** |
| `paths.m` | fallback / 路由 / 闸门（gate）/ acceptance / quality / 配置目录 | F3：命中即至少 **M** |
| `tier.human_flags` | H1 新增能力 / H2 外部副作用 / H3 不可逆操作，各一句理由 | 唯一的人声明；答不准按「是」；DoD 时 diff 反查明显形态兜底 |
| `tier.metrics` | [metrics.md](metrics.md) 表 2「PR 台账」的档位列（`S → M` 计升档）与返工列 | 调 `tier.s_limits` 的依据；`scripts/metrics_report.py` 汇总 |
| ~~`big_task_triggers`~~ / ~~`risk.high_triggers`~~ / ~~`sensitive_paths`~~ | v1 键，2026-09-29 晚退役 | 七条 / 五条里能机检的并入 F1–F6，其余并入 H1–H3；敏感路径拆成 `paths.l` / `paths.m` |

**待商量 → 已定（2026-09-29）**：用户提出「分档标准要再细化、可引入路由机制」，七个决定点全按建议裁定（见 [core/README §6](core/README.md) CHANGELOG）。**仍开放**：H1–H3 自答的兜底只靠 diff 反查明显形态，抓不全；坑表老条目「路径:」未回填。

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

`scripts/_config.py` 解析下面这个围栏。`buckets` 顺序即优先级，正则对路径 `search`；`s_limits` 每桶 `[文件上限, 行上限]`，`null` = 不限，`[0, 0]` = 任何改动不是 S；`paths.l` / `paths.m` 是正则；`test_map` 是 `[匹配, 替换]`；`pitfalls.path_field` 是坑表条目里路径字段的前缀；`core_leak_terms` 是骨架里不许出现的项目名词。

```json project-config
{
  "tier": {
    "buckets": [
      ["tests", "(^|/)tests?/|(^|/)test_[^/]+\\.py$|_test\\.py$"],
      ["docs", "\\.md$|(^|/)docs/"],
      ["infra", "^\\.github/|(^|/)migrations/|pyproject\\.toml$|requirements[^/]*\\.txt$|\\.lock$|(^|/)Dockerfile|(^|/)deploy|runbook"],
      ["config", "(^|/)config/|\\.env|\\.claude/|\\.ya?ml$|\\.toml$|\\.ini$|\\.json$"],
      ["src", "\\.(py|ts|js|go|rs|java|sh)$"]
    ],
    "s_limits": {"src": [3, 100], "tests": [5, 300], "docs": [5, null], "config": [0, 0], "infra": [0, 0], "other": [3, 100]},
    "same_dir_pairs": [["src/", "tests/"]],
    "test_map": [["^src/[^/]+/(?:.+/)?([^/]+)\\.py$", "tests/test_\\1.py"], ["^scripts/([^/]+)\\.py$", "tests/test_\\1.py"]],
    "dependency_files": ["pyproject\\.toml$", "requirements[^/]*\\.txt$", "\\.lock$", "package\\.json$"]
  },
  "paths": {
    "l": ["(^|/)schemas?/", "(^|/)prompts?/", "(^|/)migrations/", "^\\.github/",
          "pyproject\\.toml$", "requirements[^/]*\\.txt$", "\\.lock$", "\\.env", "\\.claude/settings", "deploy", "runbook"],
    "m": ["fallback", "(^|/)rout(er|ing)", "gate", "acceptance", "quality", "(^|/)config/"]
  },
  "pitfalls": {"table": "docs/governance/workflow/09-known-pitfalls.md", "path_field": "路径:"},
  "core_leak_terms": [
    "S2.1", "S2.2", "S2.3", "S2todo", "A6.1", "P4.B", "CRED-", "RDR-1", "PR-8",
    "committee", "fund_mgr", "tushare", "yfinance", "智堡",
    "DEBATE_KEY_CLAIMS", "EXECUTION_PLAN_CONTRACT",
    "docs/roadmap", "docs/observations", "docs/retro", "docs/plans", "backlog.md", "CLAUDE.md"
  ],
  "metrics": {"ledger": "metrics.md", "retire_after_days": 90},
  "checks": {
    "link_scope": ["README.md", "project-config.md", "checks.md", "metrics.md",
                   "core/", "docs/governance/workflow.md", "docs/governance/workflow/"]
  }
}
```

## 11. 尚未填的槽位

- `milestones` 的 S3 定义
