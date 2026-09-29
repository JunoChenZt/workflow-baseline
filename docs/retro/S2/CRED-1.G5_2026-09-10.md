# Goal 复盘 — CRED.1.G5 簇 1 收口（2026-09-10）

> **层级**：**goal 级**（`retro_goal`）。节点 [S2 §4.7.6 CRED](../../roadmap/S2.md) 共 15 个子项，
> 至此 **簇 1 六个子项（1.G0–1.G5）全部完成**；簇 2、簇 3 未开工；`retro_node` 5 问 = 子项 **CRED.retro**（仍未到时点）。
> **PR**：[#287](https://github.com/JunoChenZt/subagent-for-investment/pull/287)（分支 `auto/cred-1-g5`·`22b11c2` 跑批 + `d97ef44` 落账 + 冷审十修）。
>
> 🔴 **本 retro 初版有三处承重数字抄自跑批记录的错值，已随记录一并订正**（PR #287 冷审 10 条抓出）：
> **① G3 降级 7 条 → 实为 3 条**（`f11` `f23` `f64`·判据取审计自己写的 rationale，不是我数的正则）；
> **② 「本跑花费 $1.73」→ 那是累计**（含 8 月 $0.61），本跑新增 ≈$1.12 且 **41 次调用按 $0 计价**；
> **③ 「事实清单不是同一份」→ 说反了**，69 条逐字相同，`audit_status` 唯一差异就是 G3 降的那 3 条。
> 另订正 **④「run-counter 2026-05-25 起停更」是错的** —— 停更的只是开头那张 PR-8 闸门表，**逐跑台账一直在更新（最近 2026-08-14）**，本跑已补录。
> **产出**：段式 e2e 佐证 [cred-1-g5-e2e-20260910](../../observations/cred-1-g5-e2e-20260910/FINDINGS.md) · 三条条目就地处置 · R7 收口 · 本 retro。
> **裁决**：出处绑错那条是否 close → **用户裁「再留一轮」**（2026-09-10）。

```xml
<retro_goal id="CRED.1.G5" timestamp="2026-09-10T00:00:00Z">

  <triggered_by>
    <condition n="2">刹车 8 问命中 Q8（路线选择：出处绑错条目 close / 不 close 两个选法会改变账面）—— 已按 §2.7.3 停下上升，用户裁「再留一轮」</condition>
    <condition n="3">暴露未预料行为：**收口计划自己写错了跑法** —— 「只重跑 seg9」会让 G3 的改动一行都不执行（audit 属 seg8）</condition>
    <condition n="4">新增 deferred：三条条目全部维持开着，各自写明下次评估时点；延伸项 (a) 顺带评估结论 = 维持暂不做</condition>
    <condition n="6">节点风险层级 = 簇 1 中高</condition>
  </triggered_by>

  <tldr>
    簇 1 四项改动凑在一起跑了一次段式 e2e：终局质检 14 项全绿、执行计划完整活下来、影子对账与复核员两项都零、如实记零。
    但这个 goal 最有价值的产出不是那个绿，而是**两件"计划说的和实际该做的不一样"**：
    ① 收口计划写的「只重跑 seg9」是错的 —— 审计属第八段，照做的话 G3 白跑；
    ② 计划写的「close 4 条」达不到 —— 逐条核关闭条件，一条早已关、两条条件明确不满足、一条够格但剩余项没家。
    **最后 0 条新 close，而这正是簇 1 要治的那个病的镜像：不让账面说假话。**
  </tldr>

  <journey>
    <phase name="开工前核实跑法（避开了白跑一次）">
      按 CLAUDE.md 规矩先读段式跑指南。指南里有一条标着「最容易踩的一处」：`audit_pass_0_5` 属 **seg8**、不属 seg9，
      改 audit 却按惯例做 seg9-resume，改动一个都不会跑。而簇 1 里 G3 改的正是 audit。
      ⇒ 收口计划（设计稿 2026-09-08 写的「复用近跑 seg1–8·只重跑 seg9」）**在这一点上从写下来那天就是错的**。
      改为从 **seg7 断点起跑 seg8 + seg9**。事后验证这个改法是对的：seg8 里 **3 条**事实（`f11` `f23` `f64`）走了 G3 的新分支
      —— 而且这 3 条**正是本跑与 8 月那跑 `audit_status` 的唯一差异**（69 条事实逐字相同），改动面精确可数。
      〔🔴 初版这里写「7 条」，是我拿正则数的「无主数字且正文带数字」，**不是审计的实际判定**；已订正〕
    </phase>
    <phase name="跑批与佐证">
      起点选 G7 gold（2026-08-27）—— 簇 1 四条问题里有两条就是那一跑实锤的。seg8 → 段间 checklist 全过 → 停下等放行 →
      seg9 → checklist 全过 → 终局质检 **14 pass / 0 warn / 0 fail / 0 n/a**。
      决策 BUY、计划完整（4500–4600 / 止损 4350 / 三档止盈），与原跑的 HOLD + 计划被切形成对照。
      ⚠️ 但**这个对照不是受控 A/B** —— 🔴 **初版给的理由是错的**（写「事实清单不是同一份」，实测**逐字相同**）。
      正确理由：**seg9 的基金经理是重新跑的非确定性模型调用**，且 seg9 整段代码变过（影子 + 四道免检 + 复核员 + 存疑标）
      ⇒ 决策不同有多个可能来源。受控证据在靶测的归档回放，e2e 只是「整条链路跑得通」的佐证。
      中途出过一次自己的读数错误：把「逐条回应 0 条」当成漏回应，拿 main 上两次历史跑对照才发现**回应挂在决策对象里、是 1/1**。
    </phase>
    <phase name="逐条核关闭条件 → 0 条新 close">
      计划写「close 4 条」。逐条读各自的关闭条件：
      ① 质检那条 **G1 时已关**；② 风险闸那条在影子试用期、用户定的地板是 ≥3 跑（这是第 1 跑）**不能关**；
      ③ 审计空值那条剩余项是「提取器本身漏」、G3 只做了下游兜底**不能关**；
      ④ 出处绑错那条**够格按完成关**，但正文挂着的剩余项一关就没家 —— 摆两个选法给用户，裁「再留一轮」。
      顺带按条目自己的触发条件量了一次提取率（69 条事实真漏抽 1 条），并给了延伸项 (a) 的评估结论。
    </phase>
  </journey>

  <mistakes>
    <mistake>
      <what_went_wrong>🔴 **最重（合并前冷审抓出·10 条里 3 条是承重数字错）**：跑批记录里三个数字写错，且已抄进 retro / backlog / S2。
        共同根因 —— **我用自己写的临时正则去数「G3 降了几条」，而不是读审计自己写下的判定理由**；
        「7 条」于是把三类不同成因（G3 降 3 / 水印是外部章降 3 / 直接 passed 1）混成一个数，
        再拿它当「从 seg7 起跑是对的」的证据。同批错的还有：把 CLI 的**累计**花费当本跑花费；把「事实清单不是同一份」当成
        「非受控 A/B」的理由（实测 69 条**逐字相同**）。</what_went_wrong>
      <fix_or_lesson>三处全部就地订正（不是加注解）。**教训：跑批记录里的每个承重数字，判据必须是被观测系统自己写下的字段
        （`audit_rationale` / `enforcement_log` / 归档 diff），不是我为了写记录临时凑的判据** ——
        临时判据看起来能对上，但它数的往往是**另一个东西**。已提 must_update。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>「G3 的噪音过滤没有误伤」这句**两头都错**：拿来当证据的 `f17` 之所以 passed 是**水印匹配上了表①**、与噪音过滤无关；
        而 G3 真降的 3 条里有 2 条（「13 年来」「10 年期」）恰恰是我自己列为「本就不该有主数字」的时长 / 期限类。</what_went_wrong>
      <fix_or_lesson>订正为：G3 在时长 / 期限类断言上会**多响**（四类噪音只排日期 / 裸年份 / 指数名 / 证券代码，不含时长），
        方向仍安全（只降不升），但不是「没误伤」。是否收窄噪音表 → 留 observe。
        **教训**：论证「某个过滤器没误伤」时，**证据必须是那个过滤器自己的判定路径**，不能拿一个碰巧同向的结果充数。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>断言「run-counter 是 PR-8 时期专用台账、2026-05-25 起停更」⇒ 据此**不补录本跑**。
        实际只读了文件开头那张 PR-8 闸门进度表，**下面还有一张一直在更新的逐跑台账（最近 2026-08-14）**，
        而且里面正有两条同形态的 seg8+9 定向 resume 跑。</what_went_wrong>
      <fix_or_lesson>已补录本跑。**教训**：判「这份台账已经不用了」之前**要把文件读完** ——
        我拿开头一节的「最后更新」当了整份文档的状态。与 [[feedback_verify_before_acting]] 同族。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>把「逐条回应 0 条」当成了闸门漏回应（差点写成一个不存在的缺陷）—— 实际是我读错了字段：
        回应挂在决策对象里，我读的是 state 顶层。</what_went_wrong>
      <fix_or_lesson>拿 main 上两次历史跑（R6）对照才发现。**教训**：判「这次跑批出了个新问题」之前，先拿历史跑对同一个字段读一遍 ——
        对照能同时验「我读对了没有」和「这是不是新出现的」。与 [[feedback_narrative_can_be_deep_and_wrong]] 同族。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>只验了「不响」那一半（本跑 check① 全程安静），没验「会响」—— 而**安静既可能是判别力对了、也可能是闸门坏了**，
        本跑数据里分不开；用现成归档几秒就能补。另：段间 checklist 两张表只念在对话里、**没进归档**。</what_went_wrong>
      <fix_or_lesson>两条都已补（记录 §3.5「会响」归档补验 + §3.6 checklist 逐项落盘）。
        **教训**：拿「没报警」当证据时，同一轮必须给出「会报警」的对照，否则那个绿说明不了任何事。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>收口计划里的两条数字（「只重跑 seg9」「close 4 条」）**都是设计时的猜测，落地时都不成立**。
        前者会让一整个 goal 的改动不被执行；后者若照做就是把没达成的条件当达成。</what_went_wrong>
      <fix_or_lesson>两条都当场纠正并把「为什么原计划不对」写回计划表（不是悄悄改数）。
        **教训**：拆解阶段写下的「跑哪一段 / 关几条」是**待核假设、不是待办**；收口时必须逐条回到真值源核一遍
        （段落归属核 `segments.py` + 指南；关闭条件核条目正文）。已提 must_update。</fix_or_lesson>
    </mistake>
  </mistakes>

  <techniques>
    <technique>
      <pattern>定向 resume 前先查「我改的那个节点属于哪一段」，从**它所在段的前一段**断点起跑</pattern>
      <when_to_apply>任何拿旧断点验新改动的场合。真值源 = `segments.py` 的 `members`；只看「惯例上大家都 resume seg9」会白跑</when_to_apply>
    </technique>
    <technique>
      <pattern>试用期指标「零也写零」，并在记录里同时写清**为什么零是常态**</pattern>
      <when_to_apply>影子 / WARN 试用类机制。只写「0」会被后人读成「跑了没事」；要写明洞已被上游堵住、零分歧不等于检查有效</when_to_apply>
    </technique>
    <technique>
      <pattern>佐证类跑批的记录里单开一节「不能过度解读的地方」</pattern>
      <when_to_apply>凡是拿 e2e 结果支持某个结论时。本次写了四条（非受控 A/B、未响≠判别力被验、一跑不是样本、主题型形态偏差）</when_to_apply>
    </technique>
  </techniques>

  <proposals>
    <must_update target="docs/governance/workflow/09-known-pitfalls.md §3（🔴 新条 + 扩既有「空头支票」条至 N=3）">
      <rule>跑批 / 验收记录里的**每个承重数字**，判据必须是**被观测系统自己写下的字段**
        （`audit_rationale` / `enforcement_log` / 归档 diff / 台账行），**不是为了写记录临时凑的判据**。
        临时判据看起来能对上，但它数的往往是**另一个东西**。
        同理：论证「某个过滤器没误伤」时，证据必须落在**那个过滤器自己的判定路径**上；
        拿「没报警」当证据时，同一轮必须给出「会报警」的对照。</rule>
      <rationale>本 goal 合并前冷审 10 条里 3 条是承重数字错，共同根因就是这个：「G3 降了 7 条」是我用临时正则数的
        （实为 3 条，且那 7 条混了三类不同成因）；「本跑花 $1.73」是把 CLI 的累计当本跑；
        「事实清单不是同一份」实测逐字相同。三个错值都已抄进 retro / backlog / S2 才被抓住。
        **放坑表是因为 pitfall-scout 在节点起步时读的是那张表** —— 初版把沉淀只放进 03-decomposition，scout 看不见。</rationale>
    </must_update>

    <must_update target="docs/governance/workflow/03-decomposition.md §2.4.1（+ 坑表交叉引用行）">
      <rule>拆解阶段写进 goal 表的**操作性数字**（跑哪一段 / resume 从哪起 / close 几条 / 跑几次）是**待核假设，不是待办**。
        收口 goal 开工时必须逐条回到真值源核一遍再执行：段落归属核 `segments.py` + 段式跑指南；
        条目关闭核该条目正文自己的关闭条件。**核出不一致时，改的是计划、不是标准** —— 并把「原计划为什么不对」写回计划表，不许悄悄改数。</rule>
      <rationale>本 goal 两条计划数字全部落地不成立：「只重跑 seg9」会让 G3 的改动一行不执行（audit 属 seg8）；
        「close 4 条」实际 0 条够格。前者是白跑一次，后者若照做就是让账面说假话 —— 而簇 1 治的正是这个病。</rationale>
    </must_update>

    <should_update type="baseline">
      <suggestion>影子对账与异模型复核员的试用计数，建议在条目里维护一个显式计数行（当前：影子 1/3 跑·分歧 0；复核员 0 次调用·自然真阳性 0），
        每次 e2e 收口时 +1，而不是靠翻各次 FINDINGS 数。</suggestion>
      <rationale>D5 的升级判据挂在「跑数 + 全部坐实零误拦」上；跑数散在各次记录里，几轮之后没人数得清。按 §2.10.5 分流表归 baseline。</rationale>
    </should_update>

    <observe>
      <item>簇 2 的收口行（2.G5）同样写着「close 4 条」—— 那也是拆解期的猜测，届时按上面的 must_update 逐条核，不要照抄。</item>
      <item>🔴 **订正**：初版写「run-counter 2026-05-25 起停更 ⇒ 不补录」是**错的** —— 停更的只是开头那张 PR-8 闸门进度表，
        **下面的逐跑台账一直在更新（最近 2026-08-14）**，且已有两条同形态的 seg8+9 定向 resume 跑在册。**本跑已补录**。
        `_archives/` 那半仍不落（照 07-20 / 07-22 / 07-31 / 08-05 先例：验证跑非 naturalistic 样本，直接指 run 目录）。</item>
      <item>**G3 在时长 / 期限类断言上会多响**（四类噪音只排日期 / 裸年份 / 指数名 / 证券代码，不含「13 年来」「10 年期」这类）。
        方向安全（只降不升），本跑 3 条降级里占 2 条。是否收窄噪音表 → 留观察，触发 = 再出现一次明显多响、或下次动 G3 判据时。</item>
      <item>**一次「产出没人要」的返工**：triage 按 resume 设计重跑并把情绪分析师打回重写（`rework_counts={'sentiment':1}`，8 月为 `None`），
        实测报告确实变了 —— 但事实清单来自断点里冻结的 DS 结果、投票辩论早已跑完 ⇒ **那份新报告无人消费、白花一次调用**。
        属 resume 语义的既有设计，本跑不追，记一笔。</item>
      <item>**价目表缺 `deepseek-flash`**（表里只有 `deepseek-v4-flash`）⇒ 每跑都有一批调用记 $0，成本口径系统性偏低。
        代码层小修，**不在本 PR 范围**，已另立。</item>
      <item>本跑 API 花费约 $1.73（其中基金经理 3 次调用 $1.03）。段式收口跑的成本量级记一笔，供以后估算。</item>
      <item>提取率 N=1（主题型 69 条真漏抽 1 条）。与归档回放的 35/139（个股）**不可直接比**；要判提取器好坏得有个股跑批的同口径数。</item>
    </observe>
  </proposals>

  <evidence>
    <item>段式 e2e：[docs/observations/cred-1-g5-e2e-20260910/](../../observations/cred-1-g5-e2e-20260910/FINDINGS.md)（seg8 + seg9 trace / calls / checkpoint / archive 全量落盘）</item>
    <item>终局质检：`e2e_quality_gate archive-from-final.json` → **14 pass / 0 warn / 0 fail / 0 n/a**，exit 0</item>
    <item>段间 checklist：⑧ ⑨ 两段逐项对照，全过、无 ❌ —— **两张表已逐项落盘**（[FINDINGS §3.6](../../observations/cred-1-g5-e2e-20260910/FINDINGS.md)；初版只念在对话里、未进归档，冷审抓出后补）</item>
    <item>「会响」补验：[FINDINGS §3.5](../../observations/cred-1-g5-e2e-20260910/FINDINGS.md) —— 拿 m1-full-e2e-20260710 的 76 条真实事实跑今日代码，`f16` 仍判搬运错、闸门切计划降 HOLD、理由印出三元组</item>
    <item>run-counter 逐跑台账：已补录 `run-cred1g5-gold` 行（照 `run-opendoor-*` 两条同形态 seg8+9 resume 跑的写法）</item>
    <item>Code review：本 goal **零代码改动**（纯跑批 + 文档），无 review 面</item>
    <item>Corner case / 单测：本 goal 未改码，沿用 G4 合并时的全套 4317 绿；未新增测试</item>
    <item>刹车 8 问：**Q8 命中**（close / 不 close 两个选法影响账面）→ 已停下上升、用户裁「再留一轮」；其余七问未命中</item>
    <item>**Review finding 去处（§2.11.9）**：本 goal 未跑 code review（无代码改动）⇒ 整段写「未跑 review」</item>
    <item>裁决回填清单（§2.9.4 八格）：① 条目正文 ✅ 三条各就地补（含本跑数据点 + 下次评估时点）· ② 引用该结论的其它条目 —— N/A（宽 grep「随 1.G5 / close 4 条」只命中本簇自己的计划行与 dated 落账块）· ③ 跑批指南 —— N/A（跑法一字未改；本次是**按指南纠正计划**，不是改指南）+ 质量门 —— N/A（判据未动）· ④ 验收判据表 —— N/A（未新增 / 调整任何检查）· ⑤ 观察点表 —— N/A（无 `O-*` 涉及）· ⑥ 代码常量与注释 —— N/A（零代码改动）· ⑦ S2 §4.7.6 簇 1 进度行 + 1.G5 子项行 ✅ · 簇级设计 pass 状态行 + 1.G5 行 + 条目处置表三行 ✅ · G4 设计 pass §5 账目行 ✅ · ⑧ auto-memory ✅</item>
  </evidence>

</retro_goal>
```
