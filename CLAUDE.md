# CLAUDE.md — workflow-baseline

本仓库是一套「让 AI 自主推进任务时不越线、不盲跑、交付可核」的过程规则骨架。**它用自己的规则**：下面的过程规则段逐字来自 [core/01 §0](core/01-entry-and-routing.md)，改那边要同步这边（`scripts/lint_config_slots.py` 不核这一点，靠 PR review）。

## 本仓库红线（任何时刻触到立即停，不等判定）

- 不把仓库设为 public（快照层含源项目内部材料）
- 不直推 `main`；所有改动走工作分支 + PR，让 PR 事件上的检查跑
- 改 `core/` = 改所有接入项目的规则，走 [core/README §5](core/README.md) 维护协议；重大调整（改步骤 / 三态 / 三栏 / 档位规则 / 分流表 / 坑表标记）先停下问
- 不把任何项目的内部材料（记录、证据、源码片段）放进本仓；骨架保持零项目名词（`scripts/lint_config_slots.py` 守着）

## 过程规则（真值源 core/，按阶段只读对应文档，不通读；参数在 project-config.md）

1. 接到任务先跑路由器出路由卡（core/01）：给「预计改动清单」+ 三个是非题（新增能力 / 外部副作用 / 不可逆操作，各一句理由）。档位 S / M / L 由事实推出，不由我判。路由卡贴在 goal 头部；只许升不许自己降；DoD 前用真 diff 重跑，升了就补步骤。L 档先给我拆解方案，我确认后再动手。
2. 按路由卡的「必做 / 本档不要求」做（core/01 §4）。S = 执行 → 自验 → 8 问 → 简版 DoD → 交付单；M = 拆成 `<goal>`（单 goal 可用路由卡代替 scope / verification）+ 全 DoD + 5 类 evidence；L = M 全部 + 用户确认 + 节点复盘 + 完整 PR。不要求的写「本档不要求」，要求但没跑的才是 ⚪。
3. 每个 goal 做完按序：跑 verification + 自验报告（core/03）→ 刹车 8 问（core/04，任一「是 / 不确定」停下问我）→ DoD 四步（core/05）→ evidence。
4. DoD 每步只有三态 ✅ / ❌ / ⚪。没跑必须标 ⚪ 并写四种原因之一；能跑没跑是盲跑。有 ❌ 不许交付；有 ⚪ 可以交付，收不收我定。
5. 交付一律三栏交付单（core/05 §5）：改了什么 / 验证了什么、怎么验的 / 未验证什么、为什么。第三栏没有写「无」，不许空着；非「无」时全文不许写「全部通过」。
6. 红线（project-config `red_lines` 与上面「本仓库红线」）任何时刻触到立即停，不等任何判定。
7. goal 有返工、触发过刹车、暴露过意外坑、改过 case、属 L 档 —— 任一为真跑 goal 级 retro（core/06），否则跳过。
8. 节点收口：retro 5 问（core/06 §2）→ PR 描述按 core/07 模板。
9. 踩到坑先查坑表（project-config `pitfall_table`）；新坑回填坑表并写「路径:」字段，让路由器下次自动命中；不是加新流程。

## 本仓库怎么跑检查（push 前必跑，与 CI 同一套）

```bash
python scripts/router.py --base origin/main --h1 no --h2 no --h3 no
python -m pytest tests -q -p no:cacheprovider
python scripts/lint_links.py
python scripts/lint_config_slots.py
python scripts/lint_pr_body.py --file <PR 描述文件>
```

Windows 控制台先 `set PYTHONIOENCODING=utf-8`。每道检查的承重与误报预算在 [checks.md](checks.md)。

## 项目资产（交付时顺手记）

- [pitfalls.md](pitfalls.md) 坑表：踩到坑先查；新坑回填并写「路径:」。
- [backlog.md](backlog.md) 待办与里程碑：坐实 finding 的「记账」去处；每条带触发条件。
- [observations.md](observations.md)：retro 的 observe 落这里，≥ 3 次同类升级。
- [metrics.md](metrics.md) 表 2 每次 PR 加一行（档位 / 返工 / ⚪ / token）；表 1 某条规则真拦到东西时更新「上次命中」。里程碑交接跑 `python scripts/metrics_report.py`。

## 已知未收口

见 [backlog.md](backlog.md) 活跃待办（路由器 DoD 运行点看不见未提交改动 = B1；路径子串误伤 = B2）。

## 沟通

中文；结论先行；非技术语言；代码符号不当句子主语。交付按交付单三栏，路由卡贴头部。
