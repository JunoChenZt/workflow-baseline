# 04 Goal Execution — 单 /goal 执行 + 自验

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 关联子文档: [docs/governance/workflow/03-decomposition.md](03-decomposition.md) / [docs/governance/workflow/05-brake-self-check.md](05-brake-self-check.md) / [docs/governance/workflow/09-known-pitfalls.md](09-known-pitfalls.md)
> 关联 skill: (主流程，非 skill；下游接 `brake-self-check`)

## 何时读这份文档

拿到一个 `<goal>` XML 块即将进入 `<steps>` 执行时。本文档覆盖执行前自检、执行中硬边界（事前刹车）、执行中偏离处理、以及 goal 完成后的自验报告生成。

## 概览

- §2.5 单 goal 执行：执行前自检（scope / dependencies / stop_conditions）+ 按 `<steps>` 推进 + 即时刹车（[CLAUDE.md](../../../CLAUDE.md) 红线 + `<stop_conditions>`） + 偏离处理
- §2.6 自验：跑 `<verification>` 命令 + smoke + 生成结构化自验报告

**自验通过后** → 进 [05-brake-self-check.md](05-brake-self-check.md) §2.7 刹车自检 8 问。

---

## 2.5 单个 /goal 执行

**输入**：一个 `<goal>` XML 块。

### 2.5.1 执行前自检

进入 `<steps>` 之前，Claude 自检：

0. **档位声明**（[01 §2.2.5.4](01-task-entry.md#2254-只升不降--自动升档)）：一行 `档位: S/M/L ｜ 判据: …`。S 档没有 XML，这一行就是它的全部头部；做到一半发现要碰敏感路径 = 升档信号，停下按 M / L 走
1. **scope 自检**：本 goal 即将改的文件**全部**在 `<scope><allow>` 列出？有任何超出 → 停下问（S 档无 allow 列表时，以档位声明里的文件数 / 目录为界）
2. **dependencies 自检**：所有 `<upstream status="done">` 在 [docs/roadmap/S2.md](../../roadmap/S2.md) 真的标 ✅ ？没真 done → 停下问
3. **stop_conditions 注入**：把 `<stop_conditions>` 加入本轮上下文，每个工具调用前快速核对

### 2.5.2 执行 `<steps>`

按 `<steps>` 的顺序执行：

- 每个 step 可对应 1-N 个 commit
- step 结束后 commit + push 到节点工作分支（按 [docs/governance/git-workflow.md §2.6](../git-workflow.md#26-commit-节奏) 节奏）
- step 间不混 scope；遇到"顺手改"的诱惑 → 停下，记为新 goal 候选

### 2.5.3 执行中的硬边界（即时停）

执行任何 step 时，若发现即将触及以下任一情况 → **立即停**，不等到 §2.6 自验或 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) 自检：

- 触及 [CLAUDE.md](../../../CLAUDE.md) 强制红线（北极星 / 生产 / 不可逆 DB / force push / 批量删除 / 仓库 public）
- 触及 `<stop_conditions>` 任一条件
- 发现需要修改 `<forbid>` 列表的文件

**停下的具体动作**：

1. 保留当前未 commit 的改动（不丢）
2. 输出"刹车原因 + 当前状态 + 建议下一步"给用户
3. 等待用户裁决

### 2.5.4 执行中的偏离处理

若执行中发现 `<goal>` 本身有问题（拆解错了 / 范围漏了 / 依赖判错了）：

- **小偏离**（不影响 `<objective>`）：在当前 goal 内继续，commit message 说明
- **大偏离**（影响 `<objective>` / 引入新 scope）：**停下**，回到 [03-decomposition.md §2.4](03-decomposition.md#24-拆小任务) 重新拆解，作废当前 goal

**判断标准**：偏离会让本 goal 的 `<done_criteria>` 改变 → 大偏离；只是步骤微调 → 小偏离。

### 2.5.5 输出

- 改动的代码 / 文件
- 节点工作分支上的 commit 序列
- 自验运行的结果（进入 §2.6）

---

## 2.6 goal 达成自验

**输入**：`<goal>` XML 中 `<verification>` 段的命令清单 + `<steps>` 执行后的代码状态。

### 2.6.1 自验时机

- 所有 `<steps>` 已完成
- 节点工作分支上 commit + push 完毕
- 进入 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) 刹车自检之前

### 2.6.2 自验动作

1. **逐条执行 `<verification><command>`**：
   - 完整运行，不省略
   - 输出 stdout / stderr / 退出码
   - 失败的命令 → 不进入 §2.6.3，回到 §2.5 修
2. **跑 `<verification><smoke>`** (若有)：
   - 端到端最小 query：至少 1 single_ticker + 1 macro_event
   - 整 run 不崩；fallback report 比例 ≤ 基线
3. **结果汇总成自验报告**（结构化 markdown 块）：

   ```markdown
   ## Self-verification Report
   - Goal: <goal-id>
   - Tier: <S/M/L（入口）→ <同或升档>（自验时按实际 diff 核）｜判据一行>
   - Commands run: N
   - Pass: M / Fail: N-M
   - Smoke: pass / fail / unverified(<原因 a/b/c/d>)
   - Unverified: <没跑的 command 或 smoke 逐条列 + 原因；没有写「无」>
   - Fallback ratio: X% (baseline: Y%)
   - P50: A ms / P95: B ms
   ```

   `skipped` 不再是合法值：没跑就是 `unverified`，且必须带 [06 §2.8.0](06-dod-and-evidence.md#280-每一步的结果只有三态2026-09-29-立) 四种原因之一；写不进四种的就是盲跑（Q5）。

### 2.6.3 自验失败的处理

- 任一 `<command>` 失败 → **不继续**，回到 §2.5 修代码
- Smoke 失败 → 同上
- Fallback ratio 上升 → **flag 而非阻塞**，写入 `quality_flag`，但允许进入 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问)（让 8 问 + DoD 兜底）
- P95 超 [docs/roadmap/S2.md §7.4](../../roadmap/S2.md) 预算 → 同 fallback ratio：flag 而非阻塞

### 2.6.4 输出

- 自验报告（markdown 块）
- 通过 / 失败 / 带未验证项 三态（unverified 项原样带进 DoD 三态表与交付单第三栏，[06 §2.9.5](06-dod-and-evidence.md#295-交付单固定三栏2026-09-29-立)）
- 任何 `quality_flag`

**进入 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) 的前置**：通过 + 自验报告已生成。

---

## Cross-references

**上游（我引用谁）**：

- [03-decomposition.md](03-decomposition.md) — `<goal>` XML 全部字段
- [CLAUDE.md](../../../CLAUDE.md) — 强制红线（执行中硬边界）
- [docs/governance/git-workflow.md](../git-workflow.md) — commit 节奏（§2.6） / 节点工作分支推 push
- [docs/roadmap/S2.md](../../roadmap/S2.md) — 节点 done 状态确认 + §7.4 延迟预算

**下游（谁引用我）**：

- [05-brake-self-check.md](05-brake-self-check.md) — 自验通过后进 8 问刹车
- [06-dod-and-evidence.md](06-dod-and-evidence.md) — 自验报告中的 fallback ratio / P50 / P95 进 DoD 冒烟段
