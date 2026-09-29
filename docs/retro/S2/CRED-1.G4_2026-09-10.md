# Goal 复盘 — CRED.1.G4 check① 绑错 vs 真搬运错的判别力（2026-09-10）

> **层级**：**goal 级**（`retro_goal`），不是节点级。节点 [S2 §4.7.6 CRED](../../roadmap/S2.md) 共 15 个子项，
> 至此完成 1.G0 / 1.G1 / 1.G2 / 1.G3 / **1.G4（本篇·PR 待合）**；簇 1 尚欠 **1.G5 收口**，簇 2、簇 3 未开工；`retro_node` 5 问 = 子项 **CRED.retro**。
> **PR**：[#286](https://github.com/JunoChenZt/subagent-for-investment/pull/286) ✅ **已合 main `0e297ef`**（squash·2026-09-10·实现 `6338eed` + 落账 `e803725` + 冷审十修 `1f37ec6`·分支 `auto/cred-1-g4` 已删）。
> **条目**：`DEFECT-ANCHOR-FALSEPOS-HARDBLOCK`（**不在 G4 关**·随 1.G5 簇 1 收口统一处置）。
> **裁决**：D4-a = **B**；D4-b = **规则直接上 + 异模型复核员**（用户 2026-09-10 裁·不是设计稿原列的二选一）。

```xml
<retro_goal id="CRED.1.G4" timestamp="2026-09-10T00:00:00Z">

  <triggered_by>
    <condition n="2">刹车 8 问命中 Q3（AI 复核可撤硬拦 = 放行方向·北极星侧保护被单次判定撤销）/ Q5（改了 3 条既有 corner case 的期望）/ Q7（新增一条外部模型调用路）/ Q8（多方案）—— 四条均为用户在开工前显式裁定，不是执行中自判放行</condition>
    <condition n="4">改了 corner case（test_exec_floor.py 三条「年份登记值 → 软报」改「年份免检 → 跳过」）+ 新增 deferred（f16 类推算比值绑定：规则层不治、由复核员承接；候选 ③ 分析师侧校验留账）+ Q8 WARN 试用登记</condition>
    <condition n="6">节点风险层级 = 簇 1 中高（改承重闸门判据；本 goal 更越过「只降不升」红线一次·用户显式裁）</condition>
  </triggered_by>

  <tldr>
    报告出门前那道「证据抄错了」硬拦，历史上响过 5 次、5 次全是误报、零次真错。本 goal 按用户裁的 B 方案在比较之前先拒绝比不可比的
    （年份 / 百分比与小数 / 单位缩写，年份免检另补价格守卫），再按用户改裁的 D4-b 请一个不同家族的模型当复核员：
    机械判抄错之后它明确说「误报」才撤硬拦，撤了也只到「执行计划保留 + 打存疑标」这一档，其余一律维持硬拦。
    最重要的一课：**给一次红线例外配「结构性前提焊在代码里」比配「一段说明」有用** —— 独立性 / 输入隔离 / 输出封闭三条各有靶测，
    env 改错、模型换家、输出乱写，任何一条不满足复核员就自动缺席、硬拦照旧。
  </tldr>

  <journey>
    <phase name="指南与裁决演变（同一 session 三轮）">
      先按用户要求「只查环境不动手」出非技术指南：三方案优劣 + 上线方式三种 + 十条边角（年份免检误伤真价位 / 缩写词表抄坏 / 免检越宽盲区越大 /
      告警通道不得进决策者眼睛 / 年份免检吞掉两条软报 / 推算比值那类没治 / 回放前提没追 / 边界值 / 268 份能回放几份）。
      用户问「能不能叫 agent 来比」→ 答：写起来简单、用在硬拦裁决上危险（G5「只降不升」红线 / G6 嘱咐无效 / 08-14 编造出处三度复现无门拦），
      模型只宜「解释」或「加严」。用户再提「机械裁决 + 报错时 agent 看是不是误报」→ 摆三档权限（只写意见 / 可降软报 / 可撤销），
      指出没法校准（历史 0 真阳性·永远说误报也 5/5 满分）、同家族错误相关、登记册只留 60 字。用户最终裁：B + 不同模型复核 + 撤硬拦 + 计划保留打存疑标。
      按 CLAUDE.md「用户重申即为决定」照做，并把红线例外三前提写进代码与设计稿 §6。
    </phase>
    <phase name="实现">
      verify.py 三道保险（各带守卫）；exec_floor.py 分类出带三元组的明细、明细戳挂 fact quality_flags（grep 核：不进任何 LLM 提示词）、
      reviewer 注入点、disputed 戳；mismatch_review.py 新模块（provider 家族守卫 / 输入隔离 payload / 输出封闭解析 / fail-closed）；
      risk_gate.py disputed → caveat_only；decision.py 加 Optional 字段 execution_plan_caveat；Q8 WARN 试用；trace 渲染。
      三条既有 corner case 按设计稿 §3.5「年份两条转 skip 可接受」改期望，软报路改用非年份登记值继续守。
      新增 98 条靶测：三道保险两向 / 5 条历史误报逐字 fixture（G7 断点在盘时逐字复核）/ 反向变异 / 真阳性守护 / 复核四路 / 闸门四态 / Q8 / schema 兼容。
      全套 4281 passed。
    </phase>
    <phase name="冒烟（真 gemini-2.5-pro·非 mock）">
      刻意对全部 5 条历史误报叫复核员（生产里前 4 条已被规则免检、根本叫不到它）：全判 false_positive，含 f16 推算比值（理由点在「登记的是看涨合约数、断言是比值」）。
      再合成 3 条真抄错（3580↔358 出货量 / 201↔2010 元收盘价 / 42.27↔422.7 指数点位）：全判 true_error。8/8 两向，单条 8–15 秒。
      ⚠️ 真错侧全是合成样本，自然真阳性至今 0 —— 这个 8/8 读的时候要带这个前提。
    </phase>
  </journey>

  <mistakes>
    <mistake>
      <what_went_wrong>🔴 **最重**：这条红线例外赖以成立的三道防线，有两道在真实配置下是空的 —— 合并前 review 才发现。
        ① 独立性守卫比的是 `ANALYST_MODEL` / `DECISION_MODEL` 这几个 **tier 兜底常量**，而线上每个角色走 `model_for_role` 单独配
        （`.env` 里 `COMMITTEE_MODEL_BEAR=gemini-2.5-pro` 是未注释实配）⇒ 守卫会在"gemini 复核 gemini 自己写的数字"时说独立；
        ② `oc/<model>` 自成一族 ⇒ 同一模型换个写法就骗过守卫；
        ③ 提示词范例恰好是"撤硬拦"那一档、解析取第一个 JSON ⇒ 模型先复述格式就把范例取走（**实测复现**）。</what_went_wrong>
      <fix_or_lesson>三条全修（`producer_models_for_fact` 比 per-role 实配 + 剥 `oc/` 前缀 + 范例改最保守档 / 取最后一个对象 / 范例指纹）。
        **教训**：给一个"例外"写守卫时，我把守卫写得像回事就以为成立了，没去核**守卫判据在运行时到底 evaluate 在什么值上**。
        已升 🔴 进坑表「守卫要锚在它真正要守的那个对象上」。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>年份价格守卫拿**整句** search ⇒ 句子别处一个 `$180` 就把真年份拉回比较 —— **正好让本节点要治的 G7 那条误报复活**；
        反过来「index closed at 2000」这种值域内点位又被当年份放过。首版靶测只测了"典型句子"，两个方向都没看见。</what_went_wrong>
      <fix_or_lesson>守卫改为先 `locate_value_in_context` 定位登记值本身、只看紧邻窗口；定位不到 → 走拦侧。
        靶测补两条关键回归（带 `$180` 的真年份必须免检 / 不带 "points" 的点位必须照比）。同上坑表条目。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>百分比↔小数归一**只看数值形状**：0.03 ↔ 3 这种真抄错会被当表示法差异静默放过，连复核员都见不到。</what_went_wrong>
      <fix_or_lesson>加 **fact 侧证据要求**（断言里明说是百分比才归一）。教训：**结构规则也需要证据**——
        "形状对得上"离"是同一回事"还差一步，而这一步恰好是判据承重的地方。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>同步 LLM 调用直接跑在 async 决策节点上（同节点其它调用都 `to_thread`）；复核无条数上限；
        `attempts=1` 被我在注释里写成"最坏 2×"（核到 langchain-google-genai 源码：`attempts` 是**总尝试次数**）。</what_went_wrong>
      <fix_or_lesson>`asyncio.to_thread` + 预算 10 + attempts 2 / timeout 30。
        教训：**新增外部调用要照抄同一节点里既有调用的编排姿势**（阻塞模型 / 预算 / 超时三件套），不能只抄"怎么调"。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>复核员抛异常时审计写成「未配置复核员」—— 把一次**故障**记成了**配置状态**。</what_went_wrong>
      <fix_or_lesson>异常返回 `unsure` 带 `reviewer raised: …`。教训：fail-closed 的两种成因（没配 / 挂了）在审计里必须可区分，
        否则将来查"为什么复核没生效"会查错方向。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>新事件类型 `exec_floor_disputed_event` 没进流式协议白名单；8/8 冒烟只在会话里说过、没落盘；
        S2 状态表的图标还停在 🔲；dataflow 字段表漏了新字段。</what_went_wrong>
      <fix_or_lesson>全部补齐（冒烟已归档为 `docs/observations/cred-1-g4-review-smoke-20260910/`）。
        **图标那条是老毛病复发** —— memory 里「回填裁决改清单不只改详情·状态图标必须挪」正是说这个，我改了详情段没挪清单图标。</fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>年份守卫首版只写了 `pts?`，反例测试「index at 2000 points」当场红；
        给 `apply_evidence_transcription_flags` 补 docstring 时贴到了三引号外面（SyntaxError）。</what_went_wrong>
      <fix_or_lesson>两条都被测试/lint 当场抓住、零成本。前者印证「先列反例表再写正则」；后者提醒 Edit 锚点要选在 docstring 内。</fix_or_lesson>
    </mistake>
  </mistakes>

  <techniques>
    <technique>
      <pattern>红线例外的前提焊在代码里（独立性守卫 / 输入隔离 payload / 输出封闭解析），每条前提配一条「不满足 → 自动缺席」靶测</pattern>
      <when_to_apply>任何用户裁定的「方向例外」（放行侧的 AI 判定 / 放宽承重闸）—— 让例外的成立条件可机检，而不是靠注释与自觉</when_to_apply>
    </technique>
    <technique>
      <pattern>可见性明细不加 schema 字段：三元组写成带前缀的 quality_flags 项，闸门 / 质检 / trace 按前缀读；先 grep 核该字段不进任何 LLM 提示词</pattern>
      <when_to_apply>要给「闸门只读戳、不碰源表」这类结构性约束加人读明细，又不想动 pass0 schema 或让闸门读表②时</when_to_apply>
    </technique>
    <technique>
      <pattern>AI 判定路的冒烟必须两向：已知误报（期望撤）+ 合成真错（期望不撤），缺一边就没法说它「会判」</pattern>
      <when_to_apply>历史只有一类样本（本例只有误报）时；否则「永远说误报」也能拿满分</when_to_apply>
    </technique>
  </techniques>

  <proposals>
    <must_update target="docs/governance/workflow/09-known-pitfalls.md §3.2">
      <rule>守卫（免检条件 / 资格判定 / 独立性检查）必须锚在它真正要守的那个对象上：
        ① 判据 evaluate 在哪个对象上 —— 别把「这一句里有」当成「这个数字旁边有」；
        ② 比的是运行时**真正生效的值**，不是默认 / 兜底常量；
        ③ 同一实体的别名写法（前缀 / 大小写 / 网关包装）必须先归一再判；
        ④ 每道守卫配两向靶测：该守的守住 + 不该守的别误伤。</rule>
      <rationale>本 goal 合并前 review 十条里 3 条同此根因，且其中一条**直接让本节点要治的那条误报复活**
        （整句 search 让句子别处的 `$180` 把真年份拉回比较）。已落坑表 🔴。</rationale>
    </must_update>

    <should_update type="red-line">
      <suggestion>坑表加一条：「AI 判定被允许朝放行方向影响承重闸时，必须满足三个可机检前提 —— 复核模型与产出方不同 provider 家族 / 复核输入只含被审事实与出处、不含推理与决策 / 输出封闭三选一且只有一个字面能放行；并且只能放到带人读标记的中间档，不能放到干净放行。」</suggestion>
      <rationale>本 goal 是仓内第一次显式越过 G5 焊死的「只降不升」；下一次再有人提「叫个 agent 看看」，规则应当现成，而不是重走一遍本 session 的三轮辩论。按 §2.10.5 分流表归 red-line，由用户裁 adopt / defer。</rationale>
    </should_update>

    <should_update type="baseline">
      <suggestion>1.G5 收口抄录影子分歧时，同批抄录复核员记录（enforcement_log `evidence-mismatch-review`）：零也写零；并把「自然真阳性 = 0」作为一条显式基线登记，出现第一例时必须回看复核员当时的判定。</suggestion>
      <rationale>复核员的 8/8 里真错侧是合成的；它在自然真错上的表现是唯一还没被量过的东西，而那正是撤硬拦的代价所在。</rationale>
    </should_update>

    <observe>
      <item>复核员冒烟 N=8（5 历史误报 + 3 合成真错）8/8；单条 8–15 秒。累计到自然样本 ≥3 或首例自然真阳性时重评。</item>
      <item>免检跳过的 fact 不再单独打告警（设计稿原 D4-b 影子告警被 superseded）。若 1.G5 e2e 发现「跳过了但人想看」的需求，再议把 skip 三元组也写进 enforcement_log。</item>
      <item>年份免检的价格守卫是实现时补的、设计稿没写；它把免检收窄（拦侧）。守卫词表（货币 / 单位 / 价格词）N=1 版本，遇到漏形态按「先列反例再写正则」补。已知边界：`12m`（12 米）这类零空格非量纲写法仍会被当单位缩写。</item>
      <item>**方向性建议（review 提出·本轮刻意不做）**：更根本的修法是**在数字登记那一刻就标注**「这是年份 / 带单位 / 百分比」，
        而不是事后从 60 字上下文里猜。设计 pass 当年否决的是候选 ①「登记时**跳过**年份」（会少登记 26%、动印证计数），
        **没有评估过「登记时**加标注**、条目照登」这个版本** —— 那个版本不删条目、爆炸半径小得多。
        触发 = 下次动盖章登记逻辑（`number_stamp.py`）时一并评估；本轮不扩界（治标不扩界·[[feedback_treat_scope_no_creep]]）。</item>
    </observe>
  </proposals>

  <evidence>
    <item>实现 commit：`6338eed`（分支 `auto/cred-1-g4`）+ 落账 `e803725` + review 十修（本轮）</item>
    <item>靶测：tests/test_cred_g4_mismatch_review.py（**十修后 134 条**·含 10 条 review 逐条回归守护）+ tests/test_exec_floor.py（三条期望更新）；全套 **4317 passed** / 2 skipped / 2 xfailed</item>
    <item>冒烟（**已归档**）：[docs/observations/cred-1-g4-review-smoke-20260910/](../../observations/cred-1-g4-review-smoke-20260910/FINDINGS.md) —— 真 gemini-2.5-pro 两向 **8/8**（十修后重跑·8 条独立性守卫全部实跑通过·逐条结论落 `raw-verdicts.json`）</item>
    <item>**Review finding 去处（§2.11.9）**：坐实 **10** = 本 PR 修 **10** + 记账 **0** + 明确不做 **0**（10 = 10+0+0 ✅）。另有 1 条 review 提到但不属本轮的方向性建议（「在数字登记那一刻就标注年份 / 单位 / 百分比，而不是事后从 60 字上下文里猜」）—— 已记入本 retro `<observe>`，触发 = 下次动盖章登记逻辑</item>
    <item>回放：G7 seg9 断点（main tracked·R6）逐字复核 f60 fixture + 真实 facts/册跑对账 → f60 不再硬拦（skip:year）；f43/f82/f24 fixture 逐字取自 08-05 / 07-10 断点</item>
    <item>裁决回填清单（§2.9.4 八格）：① 条目正文 ✅ backlog `DEFECT-ANCHOR-FALSEPOS-HARDBLOCK` 09-10 块 · ② 其它条目 N/A（顶部「第 N 笔」banner 按惯例随 PR 合并的收口落账写）· ③ 指南 ✅ e2e-quality-gate.md Q8 行 + segmented guide Q1-Q8 · ④ 验收判据表 ✅ acceptance-standard §4 ④ 块 + 承重边界表 + 演进历史 · ⑤ 观察点表 N/A（无 O-* 观察点涉及）· ⑥ 代码常量与注释 ✅ exec_floor / verify / mismatch_review / config docstring + gate-mechanisms-map §3 + dataflow 整链 banner · ⑦ 路线图 ✅ S2 §4.7.6 状态行 + 子项行 + 簇级设计稿 D4 行 / §3.1.4 / 子项表 / 条目处置表 · ⑧ auto-memory ✅ project_cred_cluster1（本 session 末更新）</item>
  </evidence>

</retro_goal>
```
