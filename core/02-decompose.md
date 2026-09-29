# 02 Pre-flight 5 问 · 拆解为 `<goal>`

> **何时读**：M / L 档，判定完、动手前。S 档跳过本文件。
> **输出**：5 问答案 + 一个或多个 `<goal>` XML（L 档还要落盘 + 用户确认）。

## 1. 顶层对齐（进 5 问前的前置闸）

动手拆之前，先读本任务的父级定义（`{{roadmap_file}}` 对应节点 + `{{design_truth_source}}` 相关段），确认拆解方向与顶层要求一致。**没读 → 先读再拆；方向不一致 → 停下问**，别按自己的理解往下拆。顶层定义本身也是一种必须先验证的前提。真值源可能在**未合分支**，`git branch -a` / `git ls-tree` 先查，别当「待建」跳过。

## 2. Pre-flight 5 问

| # | 问题 | 失败应对 |
|---|---|---|
| 1 | **依赖**：上游节点全部完成了吗？ | 等上游完成再开（除非可证明无依赖） |
| 2 | **并行**：目前主干 / 其他工作分支 / 进行中的任务会撞同一文件吗？ | 撞 → 改串行；不撞 → 并行（上限 `{{wip_limit}}`） |
| 3 | **风险档位**：复用 [01 §2](01-entry-and-routing.md) 结果 | 高 → 需用户确认拆解 + PR 必走 review |
| 4 | **时间 / 资源预算**：落在 `{{goal.time_budget}}` 哪一档？超预算怎么办？ | 超 → 重新评估或拆分 |
| 5 | **Fallback**：完全失败时哪条路兜底？ | 没有就**先补 Fallback 再写主路径** |

每条 1–2 行回答；任一问答不出 / 应对不清 → 停下问。答案进 `<goal>` 的 `<dependencies>` / `<fallback>` 字段。

## 3. 拆解原则

- 大任务**不得直接整体执行**，必须先拆成可验证、可回滚、边界清晰的小任务；一个 `<goal>` 只动一个小任务，不混阶段、模块、风险等级。
- 每个小任务：**目标单一 / 输入清楚 / 输出可验收 / 风险可控 / 边界明确**（不顺手改无关问题）。
- **拆解表里的操作性数字是待核假设**（跑哪一段、关几条、跑几次）：收口时逐条回真值源核一遍再执行；核出不一致改的是计划不是标准，并把「原计划为什么不对」写回计划表。
- **优化类任务先安排一步最小可证伪实验**：省钱 / 提速 / 减 context 的前提往往只在纸面成立，先用角分级开销证伪再做全链验收。
- **检测类改动的收口判据要写明「那一跑怎么保证碰得上」**：选已知会触发的起点、指定回放为正式证据、或注入样本；否则一次自然跑批只能证「不乱响」那一半。

## 4. `<goal>` XML 模板

```xml
<goal id="<node-id>.<sub-id>" parent_node="<node-id>" risk_level="high|low" tier="M|L">
  <objective>本小任务要达成的单一明确结果，一句话。</objective>
  <scope>
    <allow><path>…</path></allow>
    <forbid><path>…</path><reason>…</reason></forbid>
  </scope>
  <dependencies><upstream status="done">…</upstream></dependencies>
  <steps>
    <step n="1">…</step>
  </steps>
  <verification>
    <command>{{verify.unit}} …</command>
    <smoke>{{verify.smoke}}（不要求的档位写「本档不要求」）</smoke>
  </verification>
  <done_criteria><criterion>…</criterion></done_criteria>
  <stop_conditions>
    <condition>触及 {{red_lines}} 任一 → 立即停</condition>
    <condition>需要改 <forbid> 里的文件 → 停</condition>
    <condition>DoD ❌ ≥ 3 次 → 升级重拆</condition>
    <!-- 坑表扫描返回的每条 action 必须落到这里，不能丢 -->
  </stop_conditions>
  <fallback><description>…</description></fallback>
</goal>
```

- `scope.allow` 是白名单，`forbid` 是显式黑名单，防「顺手改」。
- `dependencies` 的 `status="done"` 必须在 5 问第 1 问已确认。
- `tier` 只会是 M 或 L；S 档不写 XML。只升不降（[01 §5](01-entry-and-routing.md)）。

## 5. 落盘与确认

- **M 档**：`<goal>` 可 inline 在对话；拆完直接进 [03](03-execute-and-verify.md)，用户可随时打断。
- **L 档**：写入 `{{plans_dir}}/<node-id>-decomposition.md`，顶部含节点 ID、依赖图、`<goal>` 列表，以及一段**非技术导读**（每个 goal 做什么 / 为什么，不出现代码符号）；拆完**停下等用户 approve 或调整**。拿不准 → 按 L 处理。
- 节点 ≠ 小任务：一个节点若 10 分钟内能验证完成 → 单个 `<goal>`；否则再拆。

## 6. 输入 / 输出包装（给自动化用）

```xml
<decomposition_input>
  <node_id/><risk_level/><tier/><judgment_reason/>
  <pitfall_alerts/>          <!-- 08 §4 扫描结果 -->
  <pre_flight_answers/>      <!-- §2 五问 -->
  <task_description/>
</decomposition_input>

<decomposition_output>
  <node_id/><decomposition_path/>
  <goals><!-- 一个或多个 §4 的 <goal> --></goals>
  <user_confirmation_required>true|false</user_confirmation_required>
</decomposition_output>
```

`user_confirmation_required = true`（L 档）→ 必须 §5 停下问。
