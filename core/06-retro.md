# 06 复盘：goal 级（三档）· 节点级（5 问）· finding 去处

> **何时读**：goal 的 evidence 收齐后（§1 判要不要跑）；节点所有 goal 完成时（§2）；任何跑过 review 的 PR 合并前（§3）。
> **原则**：复盘产出的是**可执行的规则变更**，不是感想。教训优先焊进测试或删掉产坑的机制，加流程是最后的选择。

## 1. goal 级 retro

### 1.1 六条触发（任一为真才跑，不分档）

1. 有返工（DoD ❌ 重做）
2. 触发过刹车（8 问命中或执行中硬边界即停）
3. 暴露了契约 / fallback / 回放 / 路由层面的意外坑
4. 改了 corner case、改了已完成节点的契约、或新增 deferred 项
5. DoD 重做 ≥ 3 次
6. 属高风险（L 档）

六条全否 → **跳过 retro**，直接进「节点全部完成？」判定。

### 1.2 三档输出

| 档 | 定义 | 处置 |
|---|---|---|
| **must_update** | 不改会导致未来重复犯错或违反红线 | **立即落盘**到 `{{pitfall_table}}` / 刹车条件 / 骨架或实例文档 |
| **should_update** | 值得改，但不阻塞当前节点 | 按 §1.4 分流表 |
| **observe** | 先观察，数据不足 | 登记到 `{{observation_ledger}}`；§1.5 累积出口 |

**数量门槛**：每次 retro 默认最多 `{{retro.must_update_cap}}` 条 must_update。must_update = 0 是正常现象。单次 > 上限须说明为什么都是阻塞级缺陷。must_update **必须可执行**：写「应该改进设计哲学」不算，写「某节加一条『做 X 前先核 Y』」才算。连续多节点 must_update 长期超上限 → 检查触发条件是否过松。

### 1.3 产物

```xml
<retro_goal id="<goal-id>" timestamp="<ISO 8601>">
  <triggered_by><condition n="…">…</condition></triggered_by>
  <tldr>2–3 句：试了什么、成了什么、最重要的一个 takeaway</tldr>
  <journey><phase name="…">发生了什么、试了什么、哪些有效 / 无效；附错误信息或证据路径</phase></journey>
  <mistakes><mistake><what_went_wrong/><fix_or_lesson/></mistake></mistakes>
  <techniques><technique><pattern/><when_to_apply/></technique></techniques>
  <proposals>
    <must_update target="<文档 §x 或文件>"><rule/><rationale/></must_update>
    <should_update type="correctness|baseline|threshold|red-line"><suggestion/><rationale/></should_update>
    <observe><signal/><why_insufficient/></observe>
  </proposals>
  <quality_self_check>
    <must_update_count/><is_trivial/><retro_should_have_been_skipped/>
  </quality_self_check>
</retro_goal>
```

### 1.4 should_update 分流表

不能默认全部混进当前节点 PR：

| 类型 | 进当前 PR？ | 处置 |
|---|---|---|
| correctness / 契约 / 测试必需 | ✅ | 纳入节点 PR |
| 当前实现直接依赖 | ✅ | 纳入节点 PR |
| baseline / 骨架 / 模板 / 流程 | ❌ | 单独 governance PR 或 docs commit |
| 经验值 / 阈值调整 | ❌ | 进 observation，阶段复盘拍板 |
| 涉及红线 / 权限 / 生产 | ❌ | 人工确认后另行处理 |

拿不准 → governance PR 或 observe，不混进节点 PR。一个 PR 只有一个性质。

### 1.5 observe 累积出口

登记：goal-id + 时间 + 观察到什么 + 为何数据不足。**同类**（同 target + 同 signal 类型）累积 ≥ `{{retro.observe_promote_at}}` → 升级 should_update 重新分流。审视时机：里程碑交接必看；节点级复盘 q5 时也可触发。observe 不是黑洞。

### 1.6 must_update 落盘

必须落盘到对应位置（坑表 / 刹车条件 / 文档），commit 前缀 `{{git.commit_prefix}}` 的 baseline 或 retro 类。

## 2. 节点级 retro（M 简版 / L 完整）

**时机**：节点所有 goal 完成。**不可省**（沉默跳过 = Q5）；M 档每问一句话；L 档完整写入 `{{retro_dir}}/<node-id>_<YYYY-MM-DD>.md`（同节点重做按日期分文件）。

```xml
<retro_node id="<node-id>" timestamp="…">
  <q1_objective><achievement_ratio>0–1</achievement_ratio><unachieved/><reasons/></q1_objective>
  <q2_decomposition><assessment/><wrong_granularity/></q2_decomposition>
  <q3_surprises><surprise ref_retro_goal="…"/><brake_judgment_review/></q3_surprises>
  <q4_dod_blindspots>
    <missed_corner_cases/><smoke_gaps/><差不多_moments/>
    <unverified_in_production>
      <!-- 「逻辑通过 ≠ 实际验证」：只在 mock 上验过、未端到端实跑的集成点、因依赖未达成而 skip 的模块；
           每项给 verification_path：交接报告 | 待办 | 下一节点 -->
      <item><description/><verification_path/></item>
    </unverified_in_production>
  </q4_dod_blindspots>
  <q5_sedimentation>
    <must_updates_already_applied/>
    <should_updates_decisions><should_update type="…" decision="adopt|defer|reject"><target_pr/></should_update></should_updates_decisions>
    <observes_accumulated><count_by_signal/><promoted_to_should_update/></observes_accumulated>
  </q5_sedimentation>
  <next_node_unblocked/>
</retro_node>
```

**动作序列**：跑 5 问 → （L）写 retro 文件 → adopt 的 correctness 类 should_update 应用到工作分支 → baseline 类拆独立 PR → threshold 类登记 observe → red-line 类停下问 → （推荐）cold review，finding 追加进 retro → push → 开 PR（[07](07-pr-and-handoff.md)）→ 合并后更新 `{{roadmap_file}}` 状态、清理工作分支。

**achievement_ratio**：按 done_criteria 逐条计，不按感觉。**PR 描述只放 TL;DR + 链接**，完整 retro 在文件（squash 后 PR body 进 commit body，别让 history 变重）。

## 3. 坐实 finding 的去处（合并前必给）

> **治的是什么**：review 查出一堆 finding，合并时修掉一部分，剩下「坐实但这次不修」的没有强制去处，随 PR 合进主干后从此没有家。

**何时**：任何 PR 合并前，只要这轮跑过 review（cold / 高强度 / 用户当面指出 / 自查）且产出过 finding。

**每条坐实 finding 恰好一个去处**：

| 去处 | 判据 |
|---|---|
| 本 PR 修了 | 有对应改动；承重的还要有守护 |
| 记账到 `{{backlog_file}}` | 带**它自己的触发条件**，「以后再说」不算 |
| 明确不做 | PR 描述一句理由 |

PR 描述里数目必须对得上：**坐实 N = 修 a + 记账 b + 不做 c；a + b + c ≠ N 不许合。** 「坐实」由**提出方**认定，被审方认为不成立就走第三格，**分母不变** —— 少这一刀本节可被「重新数一遍 N」架空。合并后才发现漏了 → 立即补账。

**三条同族规则的分工**：状态切换后扫旧口径（全仓收口）/ 改了的东西真值源跟上（[05 §4.1](05-dod-and-delivery.md) 回填清单）/ **没改的东西要有家**（本节）。
