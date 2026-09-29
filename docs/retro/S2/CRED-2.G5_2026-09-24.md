# Goal 复盘 — CRED.2.G5 簇 2 收口（2026-09-24）

> **层级**：**goal 级**（`retro_goal`）。节点 [S2 §4.7.6 CRED](../../roadmap/S2.md)：簇 1 六项 + **簇 2 六项（2.G0–2.G5）全部完成**；簇 3 未开工；`retro_node` 5 问 = 子项 **CRED.retro**（仍未到时点）。
> **PR**：[#318](https://github.com/JunoChenZt/subagent-for-investment/pull/318)（分支 `auto/cred-2-g5`·squash 合 main `069ce14`·纯跑批 + 文档·零代码改动）。
> **产出**：全链段式 e2e [cred-2-g5-e2e-20260923](../../observations/cred-2-g5-e2e-20260923/FINDINGS.md) · 四条条目 close · R7 收口 · 本 retro。
> **裁决**：四条全关（用户 2026-09-24·其中 BS 的「本跑无噪音可标」与 BP 的「本跑无过期出处」两处缺口当面摆出后裁定）。

```xml
<retro_goal id="CRED.2.G5" timestamp="2026-09-24T00:00:00Z">

  <triggered_by>
    <condition n="2">刹车 8 问命中 Q8（BS 关 / 补一跑再关 / 挂着等，三个选法改变账面与成本）—— 停下上升，用户裁「现在就关」；其余三条同轮裁全关</condition>
    <condition n="3">暴露未预料行为：① 检测类改动的「真跑佐证」要看运气 —— 本跑没有噪音、没有过期出处，BS / BP「该标就标」那一面在自然跑批里根本没被触发；② seg8 跨日跑，金价出处恰好压在 1 天窗边界</condition>
    <condition n="6">节点风险层级 = 簇 2 高（动 `Reference` 形态）</condition>
  </triggered_by>

  <tldr>
    簇 2 四项改动凑在一起跑了一次全新的九段 e2e：终局质检 15 项全绿、段间全过、四条条目用户裁全关。
    但这次最该记下的不是那个绿，而是**收口判据本身写得太依赖运气**：设计表写「真跑佐证填充噪音不得标对题」「sourced_outdated 比例在预测内」，
    而一次自然跑批**不保证会出现噪音或过期出处**，预测也只有一个历史聚合值、没有单跑区间。
    结果是 D5 两面都验到、BO 只能说「在历史波动内」、BP / BS 只验到「不乱标」—— 四条的证据强度其实不一样，已在各自关闭格里分开写明。
  </tldr>

  <journey>
    <phase name="开工前">
      按 CLAUDE.md 先读段式指南全文。沿用簇 1 的教训逐条核计划：2.G5 行写「全链 e2e 一跑·不复用旧段」—— 与簇 2 改了 seg1 数据形态一致，
      **本次计划数字核下来是对的**（与 1.G5「只重跑 seg9」那次相反）。问句选「黄金会怎么走」，为与 CRED.1.G5 / rp-g7 / rp-g8 逐项可比。
    </phase>
    <phase name="九段逐段放行">
      每段按 checklist 核完、停下等用户放行。途中三件值得记的：
      ① seg1 读出身份标全链正确，但同时发现**本跑没有噪音**（规划员没挂通用头条源、研报全过回筛）—— 当场告诉用户，没等到收口才说；
      ② seg7 trace 把辩论摘要印成「facts_inventory=0」，打开 checkpoint 看实物（`debate_summary` 五块都有内容），确认是渲染套错格式、不是空产出（想拿 main 上历史 trace 对照，没取到可比的渲染行）；
      ③ seg8 审核零「过期」字样 —— 先回代码核判据（`>` 才算过期·金价恰 1 天 = 边界）再下「正确结果」的结论，没把「没报警」直接当证据。
      seg6 空头编了 `REF#C-005`（表① 无 C 族），追到 seg9 确认只留在辩论原文。
    </phase>
    <phase name="收口">
      终局 15/0/0。逐条核关闭条件后如实摆出 BS 的缺口，用户裁四条全关。
      2a 复核清单先用函数重算得 14 条，随后按 1.G5 的 must_update 回到**系统实际发出的查证清单**逐条核对一致再入记录。
    </phase>
  </journey>

  <mistakes>
    <mistake>
      <what_went_wrong>FINDINGS 初稿两处写错：「占位值被 11 条事实引用」（实为 6 条·把两个编号的引用次数和事实条数混了）、历史波动出处写成 2.G0 §2（实在 §3）。
        另 2a 复核清单的「14 条」初稿出处是我自己调函数重算，不是系统产物。</what_went_wrong>
      <fix_or_lesson>提交前自查全部订正，14 条改为引 seg9 `fund_mgr_verify` 实际输入（逐条一致）。
        同 1.G5 那条 must_update 的同族复现 N+1，但这次在**进 backlog / S2 之前**抓到 —— 规则在起作用，只是起草时仍会先写临时数。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>给 S2 写回的脚本在写盘前 print 了一行含 ⚪ 的调试输出，撞 GBK 控制台编码崩掉；且调试输出显示我把表格列号数错了一位。</what_went_wrong>
      <fix_or_lesson>崩在写盘前、文件未动（`git diff --quiet` 确认）；改成断言列内容再写。**教训**：改表格单元格用断言锁住「这一格原来是什么」，比打印肉眼看可靠。</fix_or_lesson>
    </mistake>
  </mistakes>

  <techniques>
    <technique>
      <pattern>收口跑批中途一发现「本跑碰不到某条判据」就当场说，而不是跑完再补一句</pattern>
      <when_to_apply>检测类改动的 e2e 佐证。本次 seg1 就知道 BS 没噪音，提前说让用户有时间考虑「补一跑还是按回放认定」</when_to_apply>
    </technique>
    <technique>
      <pattern>「零报警」先回判据代码核边界，再下「正确」结论</pattern>
      <when_to_apply>任何拿「没响」当结果的场合。本次核出金价恰在窗口边界 = 结论成立但离翻转只差一天，这个信息只有核代码才看得到</when_to_apply>
    </technique>
  </techniques>

  <proposals>
    <should_update type="process" target="docs/governance/workflow/03-decomposition.md §2.4.1">
      <suggestion>拆解时给**检测类改动**写收口判据，若要求「真跑里该响的响」，须同时写明**怎么保证那一跑会碰上**
        （选一个已知会触发的问句 / 用归档回放作为该面的正式证据 / 注入样本），否则判据只剩「不乱响」那一半。
        同理，「比例在预测内」须给单跑区间，不能只给历史聚合值。</suggestion>
      <rationale>2.G5 设计行两条判据都踩了：BS「真跑佐证填充噪音不得标对题」—— 本跑无噪音；BO「sourced_outdated 比例在 2.G0 预测内」—— 预测只有聚合 51.7%，单跑 42.0% 只能说「在历史波动内」。
        两条最后都靠用户当场裁定兜住，但这个裁定本可在拆解时就避免。按 §2.10.5 分流归 process。</rationale>
    </should_update>

    <should_update type="code-small" target="src/committee/segmented trace 渲染">
      <suggestion>seg7 trace 的 `ds_debate_result` 按事实清单格式渲染成「facts_inventory=0 · audit_status: -」，应改为渲染它真实的五块摘要（或至少印「debate_summary=N 块」）。</suggestion>
      <rationale>checklist ⑦ 该项判「空 = 失败」，照 trace 读会误报。本次已在段式指南 ⑦ 行加读法注兜底；代码修不在本 goal 范围（本 goal 零代码）。</rationale>
    </should_update>

    <observe>
      <item>**跨日边界**：seg1 取数与 seg8 审核隔一天，金价出处 1 天 = 现价窗边界。分段跑越拖，越容易让「现价过期」的判定取决于跑批节奏而不是数据本身。N=1，记一笔。</item>
      <item>**编造编号再次复现**（`REF#C-005`·凭空造命名空间·只在辩论正文）—— 已登记进 [endgame §4](../../governance/number-provenance-endgame.md) G8 之后，不立条目。</item>
      <item>**triage 重跑撞网络失败不重试**：seg8 起步 triage 全量重跑时 commodity 的 C 类检查一次 `APIConnectionError` 就放弃（降级已如实可见）。resume 每段都重跑 triage ⇒ 段越多、撞网络的机会越多。N=1。</item>
      <item>本跑 $1.85（全新九段·基金经理 $1.07）—— 全新九段收口跑的成本量级，供以后估算。</item>
    </observe>
  </proposals>

  <evidence>
    <item>段式 e2e：[cred-2-g5-e2e-20260923/](../../observations/cred-2-g5-e2e-20260923/FINDINGS.md)（九段 trace / calls / checkpoint / archive 全量落盘；段间 checklist 结果落 FINDINGS §2）</item>
    <item>终局质检：`e2e_quality_gate archive-from-final.json` → **15 pass / 0 warn / 0 fail / 0 n/a**，exit 0</item>
    <item>run-counter 逐跑台账：已补录 `run-cred2g5-gold` 行</item>
    <item>DoD 四步：Code review —— N/A（零代码改动）· Corner case —— N/A（未改码·沿用 2.G4 合并时 CI 全绿）· 冒烟 = 本次九段 e2e · 彻底跑通 = 终局 15/0/0</item>
    <item>刹车 8 问：**Q8 命中**（BS 三个处置选法）→ 停下上升、用户裁；Q7（费用）本跑 $1.85 由用户明确发起、每段放行，不另升；其余未命中</item>
    <item>**Review finding 去处（§2.11.9）**：本 goal 未跑 code review（无代码改动）⇒ 整段写「未跑 review」</item>
    <item>裁决回填清单（§2.9.4 八格）：① 条目正文 ✅（BO / BP / BS / D5 四行关闭格 + BS / D5 正文关闭注 + BY 读数）· ② 引用该结论的其它条目 ✅（endgame §4 G8 补记）· ③ 跑批指南 ✅（⑦ 段读法注）+ 质量门 —— N/A（判据未动）· ④ 验收判据表 —— N/A（未新增 / 调整检查）· ⑤ 观察点表 —— N/A（O-CRED-02 / 03 本跑无新读数）· ⑥ 代码常量与注释 —— N/A（零代码）· ⑦ S2 §4.7.6 簇级进度行 + 2.G1–2.G5 行 ✅ · 设计 pass 状态行 + 2.G5 行 + 条目处置表四行 ✅ · ⑧ auto-memory ✅</item>
  </evidence>

</retro_goal>
```
