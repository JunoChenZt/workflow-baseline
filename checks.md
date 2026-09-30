# checks — 自动检查登记表（评审建议 4）

> **原则**（[core/README §5](core/README.md)）：文字负责解释判断原则，程序负责执行明确的检查。**每加一道检查必须配「它会响」的证明和一个误报预算**，否则只是把「AI 记不住」换成「程序响了没人信」。
>
> **承重**：新检查一律 **WARN 试用**（CI 里 `continue-on-error`），升 hard-fail 需用户裁。表里「承重」列是当前状态，改它要在这张表落一笔。
>
> **误报预算**：连续 N 次响都是误报 → 停用或改判据，不许「大家都知道它爱乱响」地留着。

## 登记

| 检查 | 抓什么（对应规则） | 脚本 / 触发 | 「它会响」证明 | 误报预算 | 承重 | 上次响 | 登记日 |
|---|---|---|---|---|---|---|---|
| `lint_links` | 全仓 .md 相对链接指向不存在的文件；锚点不存在（core/README §5） | `scripts/lint_links.py`，CI 每次 push / PR；`checks.link_scope` 为 null = 全仓（内部快照已删，不再需要范围） | `--self-test`：造断链与坏锚点，必须报；好链接不报；正式测试 `tests/test_lint_links.py` | 断链 0 容忍；锚点近似 GitHub 规则，误报 3 次即改算法 | 断链 **hard-fail**（沿用源项目 `lint_doc_links.py` 先例）；锚点 WARN | 2026-09-29 首跑：本地脚本斜杠 bug 误报 19 条（已修，不计） | 2026-09-29 |
| `lint_config_slots` | core/ 用了 project-config 没定义的 `{{key}}`；core/ 出现项目名词（core/README §5「配置项不进骨架」） | `scripts/lint_config_slots.py`，CI 每次 push / PR | `--self-test`：未定义槽位与泄漏词各造一例，必须报；CHANGELOG 里的出处不报；正式测试 `tests/test_lint_config_slots.py` | 泄漏词表 `core_leak_terms` 由配置维护；误报 = 通用词被当项目词，3 次即从表里删 | **WARN 试用** | 未 | 2026-09-29 |
| `lint_pr_body` | 交付单五条硬规则（core/05 §5）+ finding 去处 N = a+b+c（core/06 §3）：缺档位行 / 三栏不齐 / 第三栏空白 / 带 ⚪ 写「全部通过」/ ⚪ 计数对不上 / a+b+c ≠ N | `scripts/lint_pr_body.py`，CI 在 PR 事件读 PR body | `--self-test`：六种坏形态各会响，两种好形态不响；正式测试 `tests/test_lint_pr_body.py` | 正则识别中文标题与「无」，误报 3 次即改；只在 PR 事件跑，不拦直接 push | **WARN 试用** | 未 | 2026-09-29 |
| `router` | 路由器 v2：由事实（桶 / 路径 / 坑表 / 依赖 / 测试可得）+ H1–H3 推档位、出路由卡；声明档位低于算出即报（core/01 §5 只升不降）；DoD 时反查 H 声明 | `scripts/router.py`：入口 `--planned` / DoD `--base` / CI PR 事件 `--base --pr-body-file` | `--self-test`：12 种事实各推对档位、反查出 2 条警告、声明行与 H 行解析；正式测试 `tests/test_router.py` | 阈值与路径表由配置维护；误报 = 该 S 的被判 M，进 `metrics.md` 表 2 作调阈值依据；H 反查只抓明显形态，漏报不算误报 | **WARN 试用** | 未 | 2026-09-29（v1 `tier_check` 同日退役） |
| `metrics_report` | 不拦：读 `metrics.md` 报退役候选（≥ 90 天零命中）与 PR 趋势（建议 6） | `scripts/metrics_report.py`，里程碑交接手动跑 | `--self-test`：零命中 / 从未命中进候选、近期命中不进、月度合计对得上；正式测试 `tests/test_metrics_report.py` | 只报不拦，无误报概念；台账没人记会满屏「从未命中」，那是信号不是误报 | 报告 | — | 2026-09-29 |

## 没做成检查的规则（为什么）

- **刹车 8 问**：判断题，机器判不了。程序层只能做「goal 完成时提醒去跑」（源项目用 hook 做了，本仓无 hook 环境）。
- **「能跑没跑 = 盲跑」**：需要知道哪些命令可跑，机器判不了；`lint_pr_body` 只能核第三栏格式，判不了原因真假。
- **路由器 DoD 运行点看不见未提交改动**（2026-09-30 探针实测）：`--base` 模式比的是 `base...HEAD`，工作树里没 commit 的改动不计。DoD 前常常还没提交 → 第二运行点目前只对「先 commit 再跑」有效。修法待定（比 `git diff base` 含工作树，或加 `--worktree` 开关）。
- **M 档路径表按子串匹配误伤**（同日实测）：文件名含 quality / gate / router 的文档也被判 M。待改成按路径段或桶限定。
- **H1–H3 三个人声明**：`router` 只在 DoD 时用 diff 反查明显形态（新 CLI 选项 / 新网络 import / 删除操作），抓不全；答「否」的真假仍靠自觉。
- **回填清单 8 格**：格式可以核（每格非空），本仓真值源少（backlog / observations / pitfalls / core），暂不值得做成检查。

## 维护

- 新增检查：先在这张表登记（抓什么 / 证明 / 预算 / 承重 = WARN），再写脚本，再接 CI。顺序不许反。
- 升 hard-fail：用户裁，理由写在「承重」列。
- 一道检查 `--self-test` 挂了 = 那道检查不可信，CI 直接红，不看它的正式结果。
- **正式测试在 `tests/test_<脚本名>.py`**（与配置 `tier.test_map` 的命名约定一致，路由器据此认「有配对测试」）：覆盖命令行入口、退出码、配置读取、边界形态，以及在真实仓库上的集成跑法；`--self-test` 保留为 CI 里最快的一道冒烟。
