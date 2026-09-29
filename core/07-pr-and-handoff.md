# 07 PR 描述 · 里程碑交接 · 节奏

> **何时读**：节点收口要开 PR；一个里程碑（`{{milestones}}`）交给下一个；拿不准并行几个 / 多久停一次。

## 1. PR 描述模板（决策溯源）

S 档可不开 PR（按 `{{autonomous_scope}}`）；开则简版 = 「档位声明 + 交付单」两段。M / L 档按下面全模板。

```markdown
## 节点
- 档位: [S / M / L（入口）→ 同或升档（DoD 对账）｜判据一行；用户裁降的引用原话]
- ID / 里程碑 / 依赖（上游已完成列表）/ 拆解（N 个 goal，链接拆解文件）

## DoD 三态（每步 ✅ / ⚪，❌ 必须为 0 才能开 PR）
- Code Review / Corner Case / 冒烟 / 彻底跑通：各一行 + 计数 ✅ a / ❌ 0 / ⚪ c

## 交付单（三栏必齐，见 core/05 §5）
### 改了什么 / ### 验证了什么、怎么验的 / ### 未验证什么、为什么（没有写：无）

## Evidence 路径（必填，盲跑不算）
- Review notes / Corner case logs / Smoke / Archive replay（N/A 写理由）/ 改 case 四要素

## Review finding 去处（跑过 review 就必填，见 core/06 §3）
- 坐实 N = 修 a / 记账 b（链接）/ 明确不做 c（各一句理由）；没跑 review 整段写「未跑 review」

## 风险与 Fallback
- 风险层级 / 引入的 fallback / 北极星与稳定性边界 / 8 问触发情况（未触发 或 触发哪条 + 裁决）

## 复盘 TL;DR
- 目标达成度一句话 / process issue / 本 PR 内已 adopt / defer 到 governance PR / observed / 完整 retro 链接

## 后续
- 解锁的下游 / 新 corner case 回填 / deferred 入账
```

**不可省略**：档位行、DoD 三态 + 计数、交付单三栏、evidence 路径、finding 去处、风险与 fallback、复盘 TL;DR。

**为什么复盘只放 TL;DR**：`{{git.merge}}` 是 squash，PR body 会进主干 commit body；完整复盘在 `{{retro_dir}}` 文件里，链接即可。

## 2. 里程碑交接（Verification Report）

**时机**：每个里程碑（`{{milestones}}`）结束时一次，最后一个节点 PR 合并后。数据量大（要读坑表全表 + 所有节点 retro + observe 累积 + 路线图账本），**subagent 化**执行，主对话只接 verdict + summary。

**通过标准**：`{{milestone.hard_fail_checks}}`，逐项 pass / fail 附证据。任一不达 → **FAIL**，不得进下一里程碑；FAIL 项升级为修复待办并登记；FAIL 触发 Q5 → 停下问。

**审视清单（每次必看）**：

1. **坑表 status 审视**：哪些 active 可降 mitigated；哪些 mitigated 可标 stale_candidate；哪些 stale_candidate 可退役（[08 §2](08-pitfall-registry.md)）
2. **observe 累积审视**：≥ `{{retro.observe_promote_at}}` 的升级；不再相关的标 stale
3. **经验值审视**：must_update 数量趋势、是否调 `{{retro.must_update_cap}}`
4. **并行数审视**：实际峰值、是否触发 §3 调整
5. **上一里程碑遗留的 `unverified_in_production` 项**：每项是否已有 verification_path 并兑现

**落地**：`{{milestone.report_dir}}`。模板：节点完成情况（ID + commit）/ hard-fail 逐项 / 观测数据（fallback 比例、延迟、回放）/ 坑表状态调整 / observe 审视 / 经验值审视 / deferred 项 / 总判定 PASS / FAIL + 理由。

**同时做「基准 review」**：本里程碑的坑表分段是否还相关；骨架与实例层是否有该退役的规则（连续零命中的）；这是评审建议 6「测量流程是否划算」的落点 —— 严格前后对照做不成，可行的是每条规则记「上次拦到东西的日期」，季度退役长期零命中的。

## 3. 节奏

| 单位 | 节奏 |
|---|---|
| 节点粒度 | `{{node.size}}`；超过拆子节点 |
| goal 粒度 | 单 goal 只动 1 个小任务；预算 `{{goal.time_budget}}` |
| commit | 节点内多 commit；合并 squash 成 1 个；账本状态更新单独 commit |
| PR | 每个节点收口 = 1 PR |
| 合并条件 | DoD 无 ❌ + 节点级 retro 完成 + finding 去处对上 |

**并行上限** `{{wip_limit}}`。不允许并行：撞同一文件 / 依赖串行 / 都是高风险。观察五个维度（review 积压、账本冲突、重复修同类、基准改动冲突、evidence 路径混乱）：连续两个里程碑无问题 → 可议上调（需人确认）；出现混乱 → 自动降到 2。超上限需人工确认。

**节点间隔**：异步 PR 模式下，PR 建好**立即继续**下一节点，但先确认其 pre-flight 第 1 问「依赖」已满足；未满足 → 切无依赖节点；都要等 → 停下问。

**同工作树多 session**：破坏性 git 操作前当场重查 status / log，拿 SHA 不拿相对引用，commit 前核当前分支。
