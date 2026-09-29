# Goal 复盘 — CRED.1.G3 改动四空值兜底（2026-09-09）

> **层级**：**goal 级**（`retro_goal`），不是节点级。
> **为什么不是节点级**：本 goal 属节点 [S2 §4.7.6 CRED](../../roadmap/S2.md)，该节点共 15 个子项，
> 目前只完成 1.G0 / 1.G1 / 1.G3；簇 1 尚欠 **1.G2 / 1.G4 / 1.G5**，簇 2（须用户确认拆解）与簇 3 未开工，
> 节点收口的 `retro_node` 5 问本身就是子项 **CRED.retro**。按 [08 §2.11](../../governance/workflow/08-retro-node-and-pr.md) 「节点所有 goal done 之后」的时机约束，
> 现在跑节点级复盘会得出一份必须重做的东西 ⇒ 本轮只做 goal 级 + PR 落账。
> **PR**：[#284](https://github.com/JunoChenZt/subagent-for-investment/pull/284) 合 main `e7fe42b`（squash·分支 `auto/cred-1-g3` 已删）
> **条目**：`DEFECT-NUMERIC-VALUE-NULL-BYPASSES-AUDIT4`（**不 close**·剩余项见下）

```xml
<retro_goal id="CRED.1.G3" timestamp="2026-09-09T07:00:00Z">

  <triggered_by>
    <condition n="2">刹车 8 问 Q5 命中（承重口径收紧·波及 34.5% 的 audit_passed）→ 已停下请裁，用户裁方案 C</condition>
    <condition n="3">暴露未预料行为：登记时写的「活体 0 例」被真实表①回放证伪 —— 原 passed 139 条里 35 条是带量纲真量值却无 numeric_value</condition>
    <condition n="4">新增 deferred 项：pass0 提取器漏值（留在条目正文·随 1.G5 统一 close）</condition>
    <condition n="6">节点风险层级 = 簇 1 中高（改承重闸门）</condition>
  </triggered_by>

  <tldr>
    审计里那道「出处能不能核这个数」的闸原先挂在「数值已提取」上，数值没抽出来时整支被绕过。
    本 goal 补上空值兜底（只降不升），真实回放降 48/139 passed、漏抓带量纲真量值 0。
    最重要的一条教训不在修法本身，而在**判据的边界**：为了不把日期、年份、股票代码误当量值，
    实现方引了仓内先例（base.py AD.2 §c）—— 但**只抄了它的正则、没抄它配套的守卫**，
    于是「1920 美元」「118000 万元」这类真价位被当噪音吃掉，闸在自己要堵的形态上漏了。
    合并前 review 把两头偏差全抓出来（5 条·8/8 真机复现），当场五修后才合。
  </tldr>

  <journey>
    <phase name="登记前提被回放推翻">
      按 1.G0 的「先登记后动码」，③ 块写着本项「活体 0 例」。动手前拿真实表①回放主干 25 跑
      1508 条事实，结果是 35 条带量纲真量值无 numeric_value 却盖了通过章 —— 「0」是把条目触发条件里的
      「拿到 🟢」（可信度档）误抄成了 audit 层。⇒ 病比登记估计的大得多，登记依据当场订正。
    </phase>
    <phase name="判据选型交用户裁">
      「正文含数字」怎么算，三个方案实测对照：A 任何数字（降 55·拖进 9 条纯日期/名字噪音）、
      B 只认带量纲（仓内先例已判 treadmill·漏「8100 点」类）、C 剥四类有限语义噪音（降 46·漏 0）。
      因波及三成以上 passed、连带打码面积变化 = 承重变更 ⇒ 停下请裁，用户裁 C。
    </phase>
    <phase name="review 五修">
      合并前 review 抓 5 条，每条在真机 + 真实归档事实上复现（8 例探针）：
      ① 裸年份吃「1920 美元」② 任何 6 位数吃「118000 万元」③ 剥标记只认方括号规范形、
      认不出裸写 REF#Y-006 与大小写漂移 [W#Macro-2-1#n1] ④「N月N日N年N季」吃「50 日线」
      ⑤ 裸写引用核 R-002 残留 002 把定性句降档。逐条修后回放定稿 48/139、漏 0，靶测 32 → 48 条。
    </phase>
  </journey>

  <mistakes>
    <mistake>
      <what_went_wrong>
        引仓内先例时**只抄了正则、没抄先例配套的守卫**。base.py 的 `_is_noise_number` 是一整套判断
        （带货币前缀 / 单位或量级后缀 / 小数点 → 不算噪音；6 位数还须 A 股板块前缀），
        本实现只搬了 `_THESIS_YEAR_RE` 与「6 位」这两个形状，守卫丢了 ⇒ 排除集**悄悄变宽**，
        闸在自己要堵的形态（真价位无数值）上反而漏。注释还写着「同 base._THESIS_YEAR_RE」，
        读起来像已对齐，掩盖了差异。
      </what_went_wrong>
      <fix_or_lesson>
        复用先例要**整段复用、能 import 就 import**，不抄形状。本轮修法直接 import
        `_ASHARE_CODE_PREFIXES` / `_THESIS_YEAR_RE` 并逐 token 走同口径守卫（`_is_noise_token`），
        不再另抄一份。已升 must_update 进 [坑表 §3.2](../../governance/workflow/09-known-pitfalls.md)。
      </fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>
        剥出处标记用的是**盖章机器的免打标区正则**（只认方括号规范形、W# 段全小写），
        而本文件同时另有一套更全的认章正则 `_LEGAL_STAMP_RE`（方括号 / 裸 core / IGNORECASE）。
        「复用而不另抄」的方向是对的，**但复用错了那一份** —— 抄来的那份服务的是「已打标文本」，
        前提是标记都规范；claim 是 LLM 自由文本，前提不成立。
      </what_went_wrong>
      <fix_or_lesson>
        选复用对象时先问「这份判据当年是在什么输入前提下写的，我这里的输入满足吗」。
        修法 = 换成同文件的 `_LEGAL_STAMP_RE`（同一文件里就有更贴的那份）。
      </fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>
        回放（25 跑 1508 条事实）是本 goal 唯一的量化依据，但**没有落盘成 observation 归档** ——
        数字只活在 PR 描述与 commit body 里，复算得重跑一次脚本。
      </what_went_wrong>
      <fix_or_lesson>
        承重数字的回放结果应留一份可回查的产物（见下方 should_update）。本轮如实记为 evidence 缺口，
        不假装有路径。
      </fix_or_lesson>
    </mistake>
  </mistakes>

  <techniques>
    <technique>
      <pattern>
        判据类改动，**两头都要探**：既探「该抓的抓不抓得到」（漏抓 = 闸白开），
        也探「不该抓的会不会误伤」（误伤 = 无谓降档）。本轮 5 条 finding 正好两头各占一半。
      </pattern>
      <when_to_apply>任何「识别 / 排除 / 噪音过滤」类判据，尤其是只降不升的保守闸。</when_to_apply>
    </technique>
    <technique>
      <pattern>
        用**真实归档事实**当探针，而不是自编 fixture：本轮 review 的 5 条里有 2 条直接踩在
        主干归档的真 claim 上（f19 的「引用[REF#R-002]但R-002未提及此信息」、
        f29 的「50 日线…下穿 200 日线」），自编 fixture 撞不出来。
      </pattern>
      <when_to_apply>判据吃的是 LLM 自由文本时；写 fixture 前先从 main tracked 归档取样（R6）。</when_to_apply>
    </technique>
  </techniques>

  <proposals>
    <must_update target="docs/governance/workflow/09-known-pitfalls.md §3.2">
      <rule>
        复用仓内先例时，先例往往是「正则 + 守卫」一整套；**只抄正则 = 悄悄放宽识别范围**。
        能 import 就 import，不抄形状；注释写「同 X」之前先核对是不是真的同。
      </rule>
      <rationale>本 goal 5 条 review finding 里 2 条（①②）同此一个根因，且都发生在承重闸上。</rationale>
    </must_update>

    <should_update type="baseline">
      <suggestion>
        承重口径改动若以「归档回放 N 条」为依据，回放脚本与结果应落一份 observation 产物
        （路径进 evidence summary），而不是只写进 PR 描述。
      </suggestion>
      <rationale>
        按 §2.10.5 分流 = baseline 类 ⇒ **不混进本 PR**；本轮 defer，留待簇 1 收口 1.G5 一并评估
        （1.G5 本就要跑段式 e2e 佐证、会产出归档）。
      </rationale>
    </should_update>

    <observe>
      <signal>
        含数字的**型号 / 法案号**（H200 / 1.6T / H.R. 3447）被判为「正文含数字」。
        本轮刻意不追（开放集·测试里如实记为 True）。若 e2e 出现定性 fact 因型号被降档，即为一次计数。
      </signal>
      <why_insufficient>
        今日主干归档里这类 fact 的水印都是 W# 外部章 ⇒ 走不到本分支，实际零影响。
        累积 ≥3 次同类再升 should_update（§2.10.6）。
      </why_insufficient>
    </observe>
  </proposals>

  <quality_self_check>
    <must_update_count>1</must_update_count>
    <verdict>该跑 —— 触发 4 条（2/3/4/6），且产出 1 条 must_update 与 3 条真实 mistake，非仪式性。</verdict>
  </quality_self_check>

</retro_goal>
```

---

## 刹车自检 8 问（[§2.7](../../governance/workflow/05-brake-self-check.md)）

| # | 问 | 判定 |
|---|---|---|
| Q1 | 生产可用性 | 否（S2 未部署·线上跑的是旧 S1） |
| Q2 | 敏感配置 | 否 |
| Q3 | 北极星 / 合规边界 | 否（收紧信任档，方向与北极星同侧） |
| Q4 | 不可逆数据 | 否 |
| Q5 | 标准降低 | **命中 → 已停下请裁** —— 收紧方向本身不是降标准，但**波及 34.5% 的 `audit_passed`、连带影响打码面积** = 承重变更；用户 2026-09-09 裁方案 C 后才落地 |
| Q6 | 改写已完成节点历史 | 否 |
| Q7 | 用户成本 / 外部依赖 | 否 |
| Q8 | ≥2 合理方案影响路线 | 命中 → A/B/C 三方案实测对照后由用户裁 C |

## DoD 四步（[§2.8](../../governance/workflow/06-dod-and-evidence.md)）

| 步 | 结论 |
|---|---|
| Code Review | ✅ 合并前跑高强度 review，坐实 5 条、当场全修（五修 `a87fa1b`）；复验 19 条探针零偏差 |
| Corner Case | ✅ 靶测 48 条两向（该降的降 / 不该降的不降 + 复核 8 例 + 守卫镜像 7 例 + 排除集条数钉住 = 8） |
| 冒烟 | 🟡 **以真实表①回放代替**（25 跑 1508 条事实·降 48/139·漏 0）；**未跑真实 pipeline** —— 段式 e2e 佐证是簇 1 收口 **1.G5** 的既定动作，非本 goal 遗漏 |
| 彻底跑通 | ✅ audit 相关六文件 204 passed；CI 九项检查全绿（含 backend py3.10 / py3.11 全套件），跑在最终提交 `a87fa1b` 上、非旧提交 |

**执行过程无异常路径声明**（§2.7.5 隐式 skip 清单第 5 条）：本轮无 worktree 切换、无 cherry-pick、
无 skip / xfail；合并为 squash、远程分支自动删除、本地分支因 squash 血缘断裂改用 `-D` 删（先按内容 grep 确认已在 main）。

## Evidence 路径

- Review notes：本轮 review 的 5 条 finding 与复验探针 —— **记在本文件 + backlog 09-09 第 12 笔 banner**（无独立 observation 文件·见上方 mistake ③）
- Corner case logs：[tests/test_audit_change4_null_numeric.py](../../../tests/test_audit_change4_null_numeric.py)（48 条）+ [tests/test_t11_stamping.py](../../../tests/test_t11_stamping.py)（三处夹具补值）
- Smoke run logs：**N/A** —— 本 goal 未跑 pipeline；回放数字见 PR [#284](https://github.com/JunoChenZt/subagent-for-investment/pull/284) 与 main `e7fe42b` commit body
- Archive replay result：真实表①回放 25 跑 1508 条事实（seg9 断点 `state.common_context.references`）→ 降 48/139、漏 0；**产物未落盘·路径待确认**
- 改 case：三处 t11 测试夹具补 `numeric_value=194.83`（**断言不动**·补的是「真实 pass0 事实必带值」这个前提），理由记在测试文件注释与 commit body

## 裁决回填清单（[§2.9.4](../../governance/workflow/06-dod-and-evidence.md) · 8 格）

| # | 真值源 | 处置 |
|---|---|---|
| 1 | 条目正文 | ✅ 改 —— [backlog `DEFECT-NUMERIC-VALUE-NULL-BYPASSES-AUDIT4`](../../governance/backlog.md) 09-09 块转「已合」、defer 块加前向一句、触发条件收为剩余项 |
| 2 | 引用该结论的其它条目 | N/A —— 宽 grep `CRED.1.G3` / `cred-1-g3` / 「PR 待合」只命中本条与下列四处 |
| 3 | 跑批与操作指南 | N/A —— 不改跑法、不改质量门判据 |
| 4 | [验收判据表](../../governance/e2e-acceptance-standard.md) | ✅ 改 —— ③ 块抬头 🚧 PR 待合 → ✅ 已合 `e7fe42b` |
| 5 | [观察点表](../../observations/should_update_observations.md) | N/A —— 未动观察点；段间 ⑧「`audit_passed` ≥ 50%」的校准注已在 ③ 块内写明 |
| 6 | 代码常量与注释 | ✅ 改 —— [audit_node.py](../../../src/committee/agents/audit_node.py) 注释数字统一到 48/139 定稿（随 PR 一起合） |
| 7 | 阶段路线图 | ✅ 改 —— [S2 §4.7.6](../../roadmap/S2.md) G3 行 → DONE + 簇 1 进度行；[设计 pass](../../plans/CRED-可信度地基三簇-设计pass-2026-09-08.md) 4.1 台账行 → ✅ |
| 8 | auto-memory | ✅ 改 —— `project_cred_cluster1` + `MEMORY.md` 索引行 |

## Review finding 去处（[§2.11.9](../../governance/workflow/08-retro-node-and-pr.md)）

**坐实 5 = 本 PR 修 5 + 记账 0 + 明确不做 0** ✅ 对得上。

| # | finding（提出方认定坐实） | 去处 |
|---|---|---|
| ① | 裸年份正则吃掉「1920 美元 / 2050 美元」这类真价位 → 闸漏抓 | 修（逐 token 走 base.py 老先例整套守卫） |
| ② | 「任何 6 位数」吃掉「118000 万元 / 250000 台」 → 闸漏抓 | 修（6 位须 A 股板块前缀·直接 import 先例常量） |
| ③ | 剥标记只认方括号规范形，裸写 `REF#Y-006` / 大小写漂移 `[W#Macro-2-1#n1]` 漏剥 → 定性句被误降 | 修（换本文件 `_LEGAL_STAMP_RE`） |
| ④ | 「N月N日N年N季」过宽，吃掉「50 日线 / 200 日线」均线周期 → 闸漏抓 | 修（日期收紧·裸「N 日」「NN 年」不吃） |
| ⑤ | 裸写引用核 `R-002` 残留 `002` → 纯定性 claim 被降档 | 修（有界剥除 `X-NNN`·中文紧贴处用 lookaround 而非词边界） |

⚠️ 顺带记一条**不算 finding、但值得留痕**的观察：型号 / 法案号（H200 / 1.6T / H.R. 3447）仍会被判为「正文含数字」，
**刻意不追**（开放集·今日主干归档里这类 fact 全挂 W# 外部章、走不到本分支），已进上方 `<observe>`。

## 下一棒

- **1.G2**（风险闸影子对账·D5 已裁）→ **1.G4** 等 **D4** → **1.G5** 簇 1 收口（段式 e2e 佐证 + close 4 条 + R7 + retro-goal 评估）
- 节点级 `retro_node` 5 问 = 子项 **CRED.retro**，等簇 1 / 簇 2 / 簇 3 全部收口后跑
