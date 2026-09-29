# Goal 复盘 — CRED.1.G2 风险闸 G1 排除错误条目：影子对账试用（2026-09-10）

> **层级**：**goal 级**（`retro_goal`），不是节点级。节点 [S2 §4.7.6 CRED](../../roadmap/S2.md) 共 15 个子项，
> 至此完成 1.G0 / 1.G1 / 1.G2 / 1.G3；簇 1 尚欠 **1.G4（等 D4）/ 1.G5**，簇 2、簇 3 未开工；`retro_node` 5 问 = 子项 **CRED.retro**。
> **PR**：[#285](https://github.com/JunoChenZt/subagent-for-investment/pull/285) 合 main `163337a`（squash·实现 `cf998d6` + 复审十修 `0c90632`·分支 `auto/cred-1-g2` 已删）
> **条目**：`DEFECT-REVIEW-ERROR-AS-DATUM`（**不 close**·转「影子试用中」；复审延伸两项用户裁「暂不做」·唯一去处 = 条目延伸块）

```xml
<retro_goal id="CRED.1.G2" timestamp="2026-09-10T00:00:00Z">

  <triggered_by>
    <condition n="3">暴露未预料行为：设计 pass 列的两种「错误登记形态」在今天的登记表里都不可达（上游已把错误挡在登记之外）—— 识别器实际域 ≈ 历史归档那一种措辞</condition>
    <condition n="4">新增 deferred 项：复审延伸两项（分诊 D3 切共享认章 / 登记边界加关卡）用户裁暂不做，记入条目延伸块；空值登记形态是否纳入留 1.G5 看 e2e</condition>
    <condition n="6">节点风险层级 = 簇 1 中高（改承重闸门·本 goal 以影子 + WARN 试用落地）</condition>
  </triggered_by>

  <tldr>
    风险闸 G1 把「某某源报了 503」这类故障提示也数成了证据。按用户 D5 裁定做影子对账：旧口径照旧驱动硬拦，
    新口径（排除登记为错误形态的条目）只在两者不一致时发一条 `G1-shadow` 告警，附分歧明细供用户认定。
    两课：① **影子首版走了正式 finding 通道 → 自动进决策者提示词 + 回应 pass = 观测器污染被观测的决策**，
    合并前 review 抓出、一处过滤修掉；② 开工前核到**设计稿的两种错误形态今天在登记表里都出现不了**，
    这道识别器在新鲜跑批上大概率零分歧 —— 不是检查失效，是洞已被上游堵住；D5「3 跑零分歧不能升」正为此立。
  </tldr>

  <journey>
    <phase name="R5：先证设计再动手">
      设计 pass §3.1.2 的「现状」核的是 risk_gate.py 那一行（`len(evidence_log) < 2`），没核登记表。
      开工前追到数据形态：MCP 工具错误现由 wrapper 抛异常、dispatcher 整源跳过、不发编号；fred 空结果全键 meta、
      0 条引用；wisburg 降级留痕进 `_meta`。⇒ 设计稿列的 `status="no_observations"` / MCP `isError` 在表①里都不可达。
      扫 origin/main 全部 109 份主干归档：证据条目引用错误登记 3 条（全在 D1-ROOT run1·2026-06 修 DEFECT-MCP-ISERROR 之前）；
      引用空值登记（N/A / list(0) / dict(0)）0 条。⇒ 识别器只收历史那一种措辞，空值形态不纳入（无数据支撑放宽）。
    </phase>
    <phase name="实现：影子对账 + additive schema">
      `check_g1` 一字未动；新增 `check_g1_shadow`（Strong 信心 role 两口径不一致 → `G1-shadow`·恒 warning·details 带
      被排除条目登记形态 + would_block）；`RiskGateFinding.gate` 枚举加值 + 可选 `details`；两个闸节点从 state.common_context
      取表①（复用 audit 的 `_build_ref_lookup`）；认章复用 `split_stamps`。靶测 21 条，全套件 4178 绿。
    </phase>
    <phase name="合并前 review 十修（另一 session·0c90632）">
      最重一条：影子走正式 finding 通道 → 进 fund_mgr 预检段、逐条回应 pass、打码豁免数字集 —— 观测器变成了输入。
      修 = `is_shadow` + `llm_facing_findings` 一处过滤三个 LLM 消费面，事件 / 断点 / 归档 / trace 照带；只有影子的跑批回到
      "零 finding"路径（不多烧模型调用）。其余：role 级 `would_block` 之上加闸级 `would_newly_block`（指南 ⑧/⑨ 改看它）；
      「影子永不硬拦」测试原为空测（决策无计划 → 早退）换带价位 BUY 并先证 high 会拦；trace 渲染 details；删死前缀
      `<server flagged isError`（按构造到不了表①）；REF# 提取上提为 `stamp_families.structured_refs_in`；靶测 21 → 26。
    </phase>
  </journey>

  <mistakes>
    <mistake>
      <what_went_wrong>
        影子告警按设计稿字面「另发一条 G1-shadow（warning）」走了正式 `RiskGateFinding` 通道。我在 PR 描述里
        **看见了**这个连带（"会注入决策者预检段并要求回应"），却把它当"与装备决策者一致"放行 ——
        没有问「观测器被观测对象看见之后，样本还干不干净」。
      </what_went_wrong>
      <fix_or_lesson>
        影子 / 试用 / 只记录类产物，价值全在被观测对象不知道它存在；接进现成管道前先列**全部下游消费面**，
        逐个问「这一面看见它会不会改变行为」。已升 must_update 进坑表 §3.2。
      </fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>
        设计 pass 的「现状（核到代码）」只核了闸门那一行，没核**登记表今天还会不会出现那种形态**；
        我首版注释还把识别器说成"上游回归的第二道眼睛"，复审指出回归多半换措辞、这话站不住。
      </what_went_wrong>
      <fix_or_lesson>
        一手材料要核到数据形态那一层，不止代码那一行；识别器只认历史归档那一句措辞，文档已收准。
        本 goal 单例 → observe（并入坑表同一条的连带段·N=1）。
      </fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>
        「影子永不硬拦」的守护测试首版是空测：给的决策没有 execution_plan，`should_hard_block` 看 severity 之前就早退，
        把 severity 改成 high 也照样绿。
      </what_went_wrong>
      <fix_or_lesson>
        守护测试要先证明「同一夹具下该拦的会拦」再证「本对象不拦」；与 [none-vs-truthiness](../../governance/workflow/09-known-pitfalls.md)
        那条同族 —— 自己给守卫写的测试最容易把空跑钉成预期。
      </fix_or_lesson>
    </mistake>
  </mistakes>

  <techniques>
    <technique>
      <pattern>开工前拿主干归档做全量探针（109 份 · 错误登记被引用 3 / 空值 0），先量识别器的真实域，再决定要不要放宽。</pattern>
      <when_to_apply>任何「识别 / 排除」类判据落地前；尤其设计稿的形态列表来自条目正文而非当下代码时。</when_to_apply>
    </technique>
    <technique>
      <pattern>只降不升 + 影子并算：旧口径照旧驱动承重动作，新口径只产可审样本，升级靠人工逐条认定而非跑数。</pattern>
      <when_to_apply>改承重闸门且"会多响多少"未量时（D5 先例）。</when_to_apply>
    </technique>
  </techniques>

  <proposals>
    <must_update target="docs/governance/workflow/09-known-pitfalls.md §3.2">
      <rule>影子 / 观测类机制不得走会改变被观测对象输入的通道；接管道前列全下游消费面逐个问「看见会不会改行为」。</rule>
      <rationale>#285 复审十修第 1 条·承重闸上的观测器污染；已落盘。</rationale>
    </must_update>
    <should_update type="baseline">
      <suggestion>归档全量探针（识别器域测量）应留一份 observation 产物，而不是只写进 PR / 条目正文（与 G3 retro 同一条·N=2）。</suggestion>
      <rationale>§2.10.5 = baseline 类·不混进本 PR；留 1.G5 收口时一并评估。</rationale>
    </should_update>
    <observe>
      <signal>试用期每跑 e2e 的 `G1-shadow` 分歧数（零也写零）；出现闸级 `would_newly_block=True` 即一个待认定样本。</signal>
      <why_insufficient>上游已堵，预期零分歧；≥3 跑是地板，样本没覆盖到触发场景时不得升硬拦（D5）。</why_insufficient>
    </observe>
  </proposals>

  <quality_self_check>
    <must_update_count>1</must_update_count>
    <verdict>该跑 —— 触发 3 条（3/4/6）、1 条 must_update、3 条真实 mistake（含一次空测），非仪式性。</verdict>
  </quality_self_check>

</retro_goal>
```

---

## 刹车自检 8 问（[§2.7](../../governance/workflow/05-brake-self-check.md)）

| # | 问 | 判定 |
|---|---|---|
| Q1–Q4 | 生产 / 敏感配置 / 北极星 / 不可逆 | 否（影子永不进 hard_block；schema 改动 additive；未部署） |
| Q5 | 标准降低 | 否 —— 硬拦口径一字未动；新检查按 §4「WARN 试用」规则；空测被复审抓出后补实 |
| Q6 | 改写已完成节点历史 | 否 |
| Q7 | 用户成本 | 否（只有影子的跑批不多烧模型调用·复审修 ②） |
| Q8 | ≥2 合理方案影响路线 | **命中 → 已由 D5 裁决**（影子对账 vs 直接硬拦）；复审延伸两项亦已由用户裁「暂不做」 |

## DoD 四步（[§2.8](../../governance/workflow/06-dod-and-evidence.md)）

| 步 | 结论 |
|---|---|
| Code Review | ✅ 合并前 /code-review 8 角度 + 逐条验证，坐实 10 条全修（`0c90632`） |
| Corner Case | ✅ 靶测 26 条：逐字夹具前提 assert / 验收 ①②③ / 反向镜像 / 认章变体 / 接线 / 回读兼容 / 用户专属通道 4 条 / 编号去重 |
| 冒烟 | 🟡 **未跑 pipeline** —— 段式 e2e 佐证是簇 1 收口 1.G5 的既定动作；量化依据 = 109 份归档全量探针 |
| 彻底跑通 | ✅ 全套件 4157 passed / 2 skipped / 2 xfailed（复审后）；CI 九项全绿于 `0c90632` |

**执行过程声明**（§2.7.5 第 5 条）：实现与复审分两个 session；复审后 PR 描述的 §2.11.9 段是**合并前**才补上的（原写"尚未跑 review"）—— 数目对上后才合。合并 squash、远程分支自动删、本地分支按内容 grep 确认后 `-D`。

## Evidence 路径

- Review notes：`0c90632` commit 正文（十修清单）+ 本文件
- Corner case logs：[tests/test_risk_gate_g1_shadow.py](../../../tests/test_risk_gate_g1_shadow.py)
- Smoke run logs：N/A（不跑 pipeline·1.G5 统一佐证）
- Archive replay result：109 份主干归档全量探针（错误登记被引用 3 / 空值 0）—— **产物未落盘**（记为 should_update·N=2）
- 改 case：无（t11 等既有测试未动）

## 裁决回填清单（[§2.9.4](../../governance/workflow/06-dod-and-evidence.md) · 8 格）

| # | 真值源 | 处置 |
|---|---|---|
| 1 | 条目正文 | ✅ `DEFECT-REVIEW-ERROR-AS-DATUM` 09-09 块转已合 + 复审延伸两项（用户裁暂不做·唯一去处） |
| 2 | 引用该结论的其它条目 | N/A —— 宽 grep `cred-1-g2` / `CRED.1.G2` / `G1-shadow` 只命中本条与下列各处 |
| 3 | 跑批与操作指南 | ✅ 段式指南 ⑧/⑨ 影子抄录行（看闸级 `would_newly_block`·随 PR） |
| 4 | [验收判据表](../../governance/e2e-acceptance-standard.md) | ✅ ② 块落地收准 + 已合 |
| 5 | 观察点表 | N/A —— 试用期计数放本条目触发条件，不另立 O-* |
| 6 | 代码常量与注释 | ✅ 随 PR（识别前缀收成一条·"第二道眼睛"措辞删） |
| 7 | 阶段路线图 | ✅ S2 §4.7.6 G2 行 → DONE + 簇 1 进度行；设计 pass 状态行 + 4.1 台账；risk-gate-design B.16.2 前向注 |
| 8 | auto-memory | ✅ `project_cred_cluster1` + `MEMORY.md` 索引行 |

## Review finding 去处（[§2.11.9](../../governance/workflow/08-retro-node-and-pr.md)）

**坐实 10 = 本 PR 修 10 + 记账 0 + 明确不做 0** ✅（清单见 `0c90632` commit 正文；PR 描述合并前已补同一行）。
复审延伸两项（分诊 D3 切共享认章 / 登记边界加关卡）**不是 finding**、是修法内的分支 —— 用户裁「暂不做」，唯一去处 = 条目延伸块。

## 下一棒

- **D4 裁** → 1.G4 实现 → **1.G5** 簇 1 收口（段式 e2e 佐证 + 抄录 `G1-shadow` 分歧〔零也写零〕+ close 4 条 + R7 + retro）
- 节点级 `retro_node` = CRED.retro，等三簇全部收口
