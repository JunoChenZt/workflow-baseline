# project-config — 项目配置槽位（骨架读这份，接入项目只改这份）

> **两层关系**：[core/](core/README.md) 是通用骨架（规则本体，不含任何项目名词）；本文件是**项目配置**，骨架里所有 `{{key}}` 的取值都在这里。
>
> **本文件当前的「本项目值」= 本仓库自己的**（本仓库用自己的规则）。接入别的项目：复制 `core/` + 复制本文件，把「本项目值」列改成你的，骨架不用动。「说明」列写这个槽位为什么存在、改它会影响哪一步。
>
> §10 的机器可读块是脚本读的；上面表格是人读的；两处同义，改阈值改 §10。

## 0. 项目身份

| key | 本项目值 | 说明 |
|---|---|---|
| `project.name` | `workflow-baseline` | 只用于命名与引用 |
| `project.instructions_file` | [CLAUDE.md](CLAUDE.md) | 给 AI 读的项目顶层指令；[core/01 §0](core/01-entry-and-routing.md) 的接入片段贴在这里 |
| `project.north_star` | 让 AI 自主推进任务时不越线、不盲跑、交付可核；骨架保持通用，零项目名词 | 刹车 Q3 的语义来源；别的项目换成自己的「永不越线」一句话 |

## 1. 红线与确认清单（刹车 Q1–Q4、执行中硬边界读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `red_lines` | 把仓库设为 public；`git push --force` / `reset --hard` 到 `main`；直推 `main`（一律走 PR）；删除或改写 git 历史；改 `core/` 而不走 [core/README §5](core/README.md) 维护协议 | **任何档位、任何步骤**触到即立即停，不等判定 |
| `confirm_before` | 改本文件 §10 的阈值与路径表；改 `.github/`；改 `checks.md` 里任何一道检查的承重；删除任何跟踪文件 | 不是红线，但动之前先问 |
| `autonomous_scope` | 在 `auto/<主题>` 工作分支内任意 git 操作；开 / 改 PR；改 core / scripts / tests / 台账（走 PR）。**例外**：`metrics.md` / `observations.md` 的追加行可与所属 PR 同批 | S 档「可不开 PR」在本仓**不适用**：本仓一律走 PR |

## 2. 分档与路由（core/01 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `tier.router` | `scripts/router.py`：入口 `--planned <files> --h1/--h2/--h3`；DoD 前 / CI `--base <ref>`（H 与声明档位从 PR 描述读）；`--json` 给工具用 | 由事实推档位、出路由卡；声明低于算出即报。**WARN 试用**（[checks.md](checks.md)） |
| `tier.buckets` | tests / docs / infra / config / src / other（正则见 §10，顺序即优先级） | F1：每个路径归一个桶 |
| `tier.s_limits` | src ≤ 3 文件 ≤ 100 行；tests ≤ 5 / ≤ 300；docs ≤ 5 / 不限行；config、infra 任何改动不是 S；other ≤ 3 / ≤ 100 | 按桶分开的 S 上限；**初值 WARN 试用**，按 `tier.metrics` 季度调 |
| `tier.same_dir_rule` | `scripts/` 与配对的 `tests/` 算同一顶层目录 | 跨顶层目录即至少 M |
| `tier.test_map` | `scripts/<名>.py → tests/test_<名>.py` | F6：src 文件找不到配对测试即不满足 S |
| `tier.dependency_files` | `pyproject.toml` / `requirements*.txt` / lock 文件（本仓目前无依赖文件） | F5：有改动即 L |
| `paths.l` | `.github/`；本文件；`core/README.md`（维护协议） | F3：命中即 **L** —— 改 CI、改阈值、改维护协议都是治理动作 |
| `paths.m` | `core/`；`scripts/`；`checks.md`；`CLAUDE.md` | F3：命中即至少 **M** —— 改骨架 = 改所有接入项目的规则 |
| `tier.human_flags` | H1 新增能力 / H2 外部副作用 / H3 不可逆操作，各一句理由 | 唯一的人声明；答不准按「是」；DoD 时 diff 反查明显形态兜底（跳过 .md / .txt / .rst） |
| `tier.metrics` | [metrics.md](metrics.md) 表 2 的档位列（`S → M` 计升档）与返工列 | 调 `tier.s_limits` 的依据；`scripts/metrics_report.py` 汇总 |

## 3. 任务来源与账本（core/01 / 02 / 06 / 07 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `roadmap_file` | [backlog.md](backlog.md)（本仓待办即任务清单） | pre-flight 第 1 问「上游完成了吗」查这里 |
| `roadmap.node_id_pattern` | `B<n>`（待办条目）/ `M<n>`（里程碑） | 工作分支 `auto/<主题>` |
| `design_truth_source` | [core/README.md](core/README.md) §1–§5 | pre-flight「顶层对齐」读这里 |
| `backlog_file` | [backlog.md](backlog.md) | 坐实 finding「记账」去处；每条带自己的触发条件 |
| `backlog.quota` | 活跃条目 ≤ 12；超了先关一条 | 「记账」去处的容量约束 |
| `plans_dir` | `docs/plans/`（按需创建） | L 档拆解文件落这里 |
| `retro_dir` | `docs/retro/`（按需创建） | L 档节点 retro 文件 `<主题>_<YYYY-MM-DD>.md` |
| `observations_dir` | `docs/observations/`（按需创建） | 回放 / 探针产物 |
| `observation_ledger` | [observations.md](observations.md) | retro 三档里 observe 的登记处；累积 ≥ `retro.observe_promote_at` 升级 |
| `pitfall_table` | [pitfalls.md](pitfalls.md) | 本仓已知坑表；按 [core/08](core/08-pitfall-registry.md) 维护；条目带「路径:」供路由器匹配 |

## 4. 验证手段与阈值（core/03 / 05 / 07 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `verify.unit` | `python -m pytest tests -q -p no:cacheprovider` | 自验 `<command>` 与 DoD Corner Case 的默认手段 |
| `verify.lint` | `python scripts/lint_links.py` / `python scripts/lint_config_slots.py` / 五个脚本 `--self-test` | S 档判据 5「现成验证手段」的候选 |
| `verify.smoke` | 全套检查本地跑一遍（unit + lint + `scripts/router.py --base origin/main` + `scripts/lint_pr_body.py` 核 PR 描述） | DoD 第 3 步「冒烟」的定义；S 档不要求 |
| `verify.smoke_guide` | [CLAUDE.md](CLAUDE.md)「怎么跑检查」段 | 跑之前读 |
| `budget.latency` | N/A（本仓无运行时） | 自验报告里写 N/A |
| `budget.fallback_ratio` | N/A | 同上 |
| `contracts` | DoD 三态与四种 ⚪ 原因的语义（core/05 §1）；交付单三栏与五条硬规则（core/05 §5）；路由卡字段（core/01 §5） | DoD Code Review「契约」视角对照物：改脚本不许悄悄改这些语义 |
| `archive_replay` | N/A（本仓无归档）；evidence 写 `N/A + 理由` | — |
| `acceptance_standard` | [checks.md](checks.md)（新检查一律 WARN 试用，升 hard-fail 需用户裁） | 任何新增自动检查的登记处 |

## 5. 节奏与配额（core/07 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `wip_limit` | 2 个工作分支同时 open | 并行上限；本仓单人维护，2 够用 |
| `goal.time_budget` | 小 ≤ 30 min / 中 30–90 / 大 > 90 → 再拆 | 单 goal 预算 |
| `node.size` | 1 个 PR = 1 个节点；≤ 1 天 | 节点粒度 |
| `retro.must_update_cap` | 每次 retro 1–2 条 | 数量门槛 |
| `retro.observe_promote_at` | 连续 ≥ 3 次同类 | observe → should_update |

## 6. Git 与 PR（core/07 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `git.work_branch` | `auto/<主题>`，PR 合并后删 | 工作分支命名 |
| `git.commit_prefix` | `docs` / `docs(core)` / `fix(router)` / `test` / `chore` | commit subject 约定 |
| `git.merge` | squash；PR title = main 上 commit subject；PR body 进 commit body | PR 模板「复盘只放 TL;DR」的原因 |
| `git.utf8` | commit body 别放 emoji；Windows 控制台 `PYTHONIOENCODING=utf-8`；subprocess 一律 `encoding="utf-8"` | 已知坑（[pitfalls.md](pitfalls.md)） |

## 7. 里程碑交接（core/07 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `milestones` | M0 骨架成立（2026-09-29 ✅）；M1 本仓自用（根 CLAUDE.md + 走 PR + 去内部材料，进行中）；M2 第二个项目接入 | 交接审视触发点，每个里程碑一次 |
| `milestone.hard_fail_checks` | M1：CI 绿、`lint_config_slots` 0 泄漏、全仓 0 断链、本仓一次 S 档任务走完；M2：另一个仓库按 README 三步接入，不改 core 一个字 | PASS / FAIL 判据 |
| `milestone.report_dir` | `docs/observations/verification-<里程碑>-<日期>.md`（按需创建） | 交接报告落地 |

## 8. Agent 与工具环境（core/README 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `task_prefixes` | `[GOAL]` / `[STEP]` / `[TASK]` | 任务描述前缀 |
| `hooks` | 无（本仓不带 hook；程序层闸门 = CI） | 语义层靠 CLAUDE.md，程序层靠 [checks.yml](.github/workflows/checks.yml) |
| `subagents` | 无 | 坑表短，不需要 subagent 扫描 |
| `comms.style` | 中文；结论先行；非技术语言；代码符号不当句子主语 | 交付单与对话收尾的表达要求 |

## 9. 自动检查与台账（core/README §5、core/07 §2 读这里）

| key | 本项目值 | 说明 |
|---|---|---|
| `checks.registry` | [checks.md](checks.md) | 每道自动检查的登记：抓什么 / 「它会响」证明 / 误报预算 / 承重 / 上次响 |
| `checks.ci` | [.github/workflows/checks.yml](.github/workflows/checks.yml) | self-test + pytest + lint_links 断链 = hard-fail；其余 `continue-on-error` |
| `checks.link_scope` | 全仓（§10 为 `null`） | 内部快照已删，链接检查不再需要范围限定 |
| `metrics.ledger` | [metrics.md](metrics.md) | 表 1 规则命中台账、表 2 PR 台账 |
| `metrics.retire_after_days` | 90 | 零命中超过这个天数进退役候选 |
| `metrics.report` | `python scripts/metrics_report.py` | 里程碑交接时跑 |

## 10. 机器可读块（脚本读这里，与上面表格同义；改阈值改这里）

`scripts/_config.py` 解析下面这个围栏。`buckets` 顺序即优先级，正则对路径 `search`；`s_limits` 每桶 `[文件上限, 行上限]`，`null` = 不限，`[0, 0]` = 任何改动不是 S；`paths.l` / `paths.m` 是正则；`test_map` 是 `[匹配, 替换]`；`pitfalls.path_field` 是坑表条目里路径字段的前缀；`core_leak_terms` 是骨架里不许出现的项目名词与项目路径；`checks.link_scope` 为 `null` 表示全仓。

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
    "same_dir_pairs": [["scripts/", "tests/"]],
    "test_map": [["^scripts/([^/]+)\\.py$", "tests/test_\\1.py"]],
    "dependency_files": ["pyproject\\.toml$", "requirements[^/]*\\.txt$", "\\.lock$", "package\\.json$"]
  },
  "paths": {
    "l": ["^\\.github/", "^project-config\\.md$", "^core/README\\.md$"],
    "m": ["^core/", "^scripts/", "^checks\\.md$", "^CLAUDE\\.md$"]
  },
  "pitfalls": {"table": "pitfalls.md", "path_field": "路径:"},
  "core_leak_terms": ["subagent-for-investment", "docs/governance", "docs/observations", "docs/retro", "docs/plans", "backlog.md", "CLAUDE.md", "pitfalls.md"],
  "metrics": {"ledger": "metrics.md", "retire_after_days": 90},
  "checks": {"link_scope": null}
}
```

## 11. 尚未填的槽位

- `plans_dir` / `retro_dir` / `observations_dir` 目录尚未创建（第一个 L 档任务或第一次里程碑交接时创建）
