# Goal 复盘 — CRED.3.G2 簇 3 收口（2026-09-24）

> **层级**：**goal 级**（`retro_goal`）。节点 [S2 §4.7.6 CRED](../../roadmap/S2.md)：**三簇全部完成**（簇 1 六项 · 簇 2 六项 · 簇 3 三项）；下一棒 = 节点收口 **CRED.retro**（retro-node 5 问）。
> **PR**：[#321](https://github.com/JunoChenZt/subagent-for-investment/pull/321)（分支 `auto/cred-3-g2`·squash 合 main `dd58031`·纯跑批 + 文档·零代码改动）。
> **产出**：e2e 佐证 [cred-3-g2-e2e-20260924](../../observations/cred-3-g2-e2e-20260924/FINDINGS.md) · `DEFECT-DEBATE-STALE-PRIOR` close · 两条提示词候选挪 endgame §4 G8 · R7 收口 · 本 retro。
> **裁决**：条目关闭、提示词候选挪走（用户 2026-09-24）。
> ⚠️ 本簇 3.G0 / 3.G1 的实现与合并前 review 跨两个会话（另一会话在 `wt-cred-3-g1` 工作区推 #319 / #320，本会话做 review 修复、合并落账与本 goal）。

```xml
<retro_goal id="CRED.3.G2" timestamp="2026-09-24T00:00:00Z">

  <triggered_by>
    <condition n="2">刹车 8 问命中 Q8（条目关 / 不关 / 关且放弃提示词候选三个选法影响剩余项去处）—— 停下上升，用户裁「关闭、候选挪走」</condition>
    <condition n="3">暴露未预料行为：拿一个月前的断点在今天续跑，金价出处过期 29 天 → 审核记过期 → check③ 切计划降 HOLD。本身是 CRED.2.G3 的正确行为，但「旧断点续跑的决策会被时效闸改写」是之前续跑先例里没出现过的形态</condition>
    <condition n="4">新增 deferred：两条改提示词候选挪 endgame §4 G8，触发条件随迁</condition>
  </triggered_by>

  <tldr>
    这次把 2.G5 的教训用上了：检测类收口不指望实跑碰运气，而是**挑一个保证会碰上的起点**——8 月那跑的 seg7 断点，它的辩论里真有那处旧行情。
    结果检测在真实流水线里恰好标出那一处（trace ⑧⑨ / 归档 / Q9 三处一致），且合并前修的去重在真实数据上生效（一句话两个别名只记一条）。
    意外收获：旧断点在今天跑，金价出处过期 29 天，审核记过期、执行底线切计划 —— 这是簇 2「审核读出处日期」该标就标那一面**第一次在实跑里出现**，补上了 2.G5 缺的那一半。
  </tldr>

  <journey>
    <phase name="开工前核计划">
      3.G1 改动落在 `_build_result`（seg9 末）与 trace ⑧⑨ ⇒ seg7 续跑 seg8 + seg9 即可全部执行；起点选 8 月那跑（R6 从 main tracked 取断点），
      先用今日代码试加载确认兼容，再逐段放行。
    </phase>
    <phase name="两段实跑">
      seg8 ④′ 节 1 条（DXY 105 vs 99.1）；seg9 同 1 条 + 归档 + Q9 WARN。决策被 check③ 切 —— 先回审核理由与 enforcement_log 核实成因
      （`f1` 金价出处 08-26·已过 29 天 > 1 天窗·`original_decision: BUY`），确认是时效闸按设计工作、不是新故障，再下结论。
    </phase>
    <phase name="收口">
      按 1.G5 的 must_update 逐条核关闭条件：设计 pass §6「闸门不再为零」已满足 + 实跑该响的响；
      但条目挂着两条提示词候选、关了就没家 ⇒ 按 §2.11.9「没改的东西要有家」摆三个选法，用户裁挪到 endgame G8（同根）。
      BP 的新证据：BP 已关 = Q6 冻结档，不回写，只写去 FINDINGS 与 S2 2.G5 行前向注（R7 历史切刀）。
    </phase>
  </journey>

  <mistakes>
    <mistake>
      <what_went_wrong>无承重错误。一处小绕路：给记忆索引改状态时，脚本按旧文本断言失败 —— 另一会话已改过同一行（写成「#320 待合」）。</what_went_wrong>
      <fix_or_lesson>断言挡住了覆盖写；读回当前文本后在其基础上改。**教训**：多会话并行时，改共享文件（含 memory 索引）一律「读当前 → 断言锁原文 → 改」，别凭自己上次写的内容去替换。与 [[feedback_shared_worktree_race]] 同族。</fix_or_lesson>
    </mistake>
  </mistakes>

  <techniques>
    <technique>
      <pattern>检测类收口挑「保证会触发」的起点续跑，而不是跑一次全新流水线碰运气</pattern>
      <when_to_apply>收口要证「该响的响」时。本次 seg8+9 续跑 ≈$1.2，比全新九段便宜，且确定性地碰上目标形态（2.G5 retro should_update 的第一次落地）</when_to_apply>
    </technique>
    <technique>
      <pattern>决策被闸门改写时，先读闸门自己写的理由（审核 rationale / enforcement_log 的 original_decision）再定性</pattern>
      <when_to_apply>续跑 / 回放出现与原跑不同的决策时。本次「BUY → HOLD」一眼像回归，读闸门留痕即知是时效闸的正确行为</when_to_apply>
    </technique>
  </techniques>

  <proposals>
    <should_update type="guide" target="docs/observations/e2e-runs/segmented-e2e-guide.md（定向 resume 说明处）">
      <suggestion>补一句：**拿旧断点续跑 seg8/9 时，决策可能被时效闸改写**（CRED.2.G3 起审核读出处日期；断点里的现价出处按今天算会过期 → check③ 切计划降 HOLD）。
        要验与时效无关的改动，结论里须注明「决策改写来自旧断点时效」，别把它当回归，也别当决策质量样本。</suggestion>
      <rationale>07-20 / 07-22 / 08-05 / 09-10 的 seg8/9 续跑先例都在 CRED.2.G3 之前，没有这个现象；以后照先例续跑的人会第一次撞见「BUY 变 HOLD」。按 §2.10.5 归 guide。</rationale>
    </should_update>
    <observe>
      <item>Q9 试用期读数：第 1 次实跑响 1 条（8 月那处·人工确认为真旧行情）；全新实跑 0 条（09-23 回放）。升档判据待试用期数据累积，须用户裁。</item>
      <item>续跑重跑 triage 再次打回情绪分析师、新报告无人消费（同 09-10）—— 既有 observe 第 2 例。</item>
    </observe>
  </proposals>

  <evidence>
    <item>e2e：[cred-3-g2-e2e-20260924/](../../observations/cred-3-g2-e2e-20260924/FINDINGS.md)（seg8 + seg9 trace / calls / checkpoint / archive + 起点断点副本）</item>
    <item>终局质检：**13 pass / 1 warn（Q9）/ 0 fail / 2 n/a**，exit 0</item>
    <item>run-counter：已补录 `run-cred3g2-gold`</item>
    <item>DoD：Code review —— N/A（本 goal 零代码；3.G1 代码已在 #320 review 并修一处）· Corner case —— N/A · 冒烟 = seg8+9 实跑 · 彻底跑通 = 终局无 FAIL</item>
    <item>刹车 8 问：**Q8 命中**（条目处置三选一）→ 用户裁；Q7 本跑 ≈$1.20 由用户发起、逐段放行；其余未命中</item>
    <item>**Review finding 去处（§2.11.9）**：本 goal 未跑 code review（无代码改动）⇒ 「未跑 review」；3.G1 的 #320 review 1 条 finding = 已修（`b8291d11`）</item>
    <item>裁决回填清单（§2.9.4 八格）：① 条目正文 ✅（表行关闭格 + 正文关闭注）· ② 引用该结论的其它条目 ✅（endgame §4 G8 接收两条候选）· ③ 跑批指南 —— 本 goal 未改（should_update 已提，待 CRED.retro 节点收口时一并处置）+ 质量门 —— N/A · ④ 验收判据表 —— N/A（Q9 已在 #320 登记）· ⑤ 观察点表 —— N/A · ⑥ 代码 —— N/A · ⑦ S2 簇级行 + 3.G2 行 + 2.G5 行前向注 ✅ · 设计 pass 状态行 + 3.G2 行 + §6 行 ✅ · 3.G0 设计 pass 状态行 ✅ · ⑧ auto-memory ✅</item>
  </evidence>

</retro_goal>
```
