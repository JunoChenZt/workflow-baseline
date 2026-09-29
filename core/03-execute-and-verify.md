# 03 单 goal 执行 · 自验

> **何时读**：拿到一个 `<goal>`（或 S 档的隐式 goal）即将动手时。
> **输出**：代码改动 + commit 序列 + 自验报告 → 进 [04 刹车](04-brake.md)。

## 1. 执行前自检

0. **路由卡**（[01 §5](01-entry-and-routing.md)）：入口跑过路由器、卡已贴在 goal 头部；没有卡 = 没跑路由器，回 01。S 档没有 XML，这张卡就是它的全部头部。
1. **scope 自检**：即将改的文件**全部**在 `<scope><allow>` 里？超出 → 停下问。S 档与 M 档单 goal 以路由卡的改动清单为界。
2. **依赖自检**：`<upstream status="done">` 真的完成了？没真完成 → 停下问。
3. **停止条件注入**：把 `<stop_conditions>` 加进本轮上下文，每次工具调用前快速核对。

## 2. 按 `<steps>` 推进

- 每个 step 对应 1–N 个 commit；step 结束 commit + push 到工作分支（`{{git.work_branch}}`）。
- step 间不混 scope；遇到「顺手改」的诱惑 → 停下，记为新 goal 候选。
- 执行中发现 `<goal>` 本身有问题：**小偏离**（不影响 objective）→ 当前 goal 内继续，commit message 说明；**大偏离**（done_criteria 会变 / 引入新 scope）→ 停下，回 [02](02-decompose.md) 重拆，作废当前 goal。

## 3. 执行中的硬边界（即时停，不等自验或刹车）

- 触及 `{{red_lines}}` 任一
- 触及 `<stop_conditions>` 任一
- 发现需要改 `<forbid>` 列表里的文件
- S 档：发现要碰 `{{paths.l}}` / `{{paths.m}}` 里的路径 = 升档信号

**停下的动作**：保留未 commit 的改动；输出「刹车原因 + 当前状态 + 建议下一步」；等人裁决。

## 4. 自验

**时机**：所有 steps 完成、commit + push 完毕、进刹车之前。

**动作**：

1. 逐条执行 `<verification><command>`：完整运行不省略；记录 stdout / stderr / 退出码；失败 → 不继续，回 §2 修。
2. 跑 `<verification><smoke>`（矩阵要求的档位）：对照 `{{budget.latency}}` / `{{budget.fallback_ratio}}`。指标超线 → **flag 不阻塞**，写 `quality_flag`，让刹车 + DoD 兜底。
3. 写自验报告：

```markdown
## Self-verification Report
- Goal: <goal-id>
- Tier: <S/M/L（入口）→ <同或升档>（按实际 diff 核）｜判据一行>
- Commands run: N
- Pass: M / Fail: N-M
- Smoke: pass / fail / unverified(<原因 a/b/c/d>) / 本档不要求
- Unverified: <没跑的 command 或 smoke 逐条 + 原因；没有写「无」>
- Fallback ratio: X% (baseline: {{budget.fallback_ratio}})
- Latency: P50 A / P95 B (budget: {{budget.latency}})
- quality_flag: <有则列>
```

`skipped` 不是合法值：没跑就是 `unverified` 且必须带 [05 §1](05-dod-and-delivery.md) 四种原因之一；写不进四种的就是盲跑（刹车 Q5）。

**输出**：自验报告 + 通过 / 失败 / 带未验证项 三态 + quality_flag。通过或带未验证项 → 进 [04](04-brake.md)；失败 → 回 §2。
