# audit_pass_0_5 定位定性（审计做什么 · 产出给谁 · 边界）

> **定位**：`audit_pass_0_5`（审计节点）"**是什么 / 不是什么 / 产出给谁用 / 不碰什么**"的**单一权威源**。供 [DEFECT-D1-ROOT 层②](../../governance/backlog.md) / 信源册 M2 引用。
> **产出背景**：2026-07-03 AUDIT-INTENT 厘清（[DEFECT-AUDIT-INTENT](../../governance/backlog.md)）定稿。
> **真值源 = 代码**（本文带 `file:line`）；本文是**定位 + 目标态设计**，**实现状态见 §6**（目标态三检查=设计已定·**码未实现**）。
> **区别于** [gate-mechanisms-map.md](gate-mechanisms-map.md)（as-built 全图 · audit 只是其中一格）——本文专讲 audit 这一格的定位。
>
> ## ⏭️ **2026-08-05 前向标注（正文与下方 CANCELLED banner 均为 point-in-time 记录·不改）**
>
> **§4 三检查的第一项「数字对不对」已复活并 ✅ 转正执法**（[#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 判定 4·比对 fact 主数字 ↔ 表① 登记值·容差 2%）。
> 〔**2026-08-05 首版为 `log-only`（只写 `log.warning`、不改 `audit_status`）；同日用户拍板提前转正**
> —— 依据是实测非推演：log-only 期实跑看得见 6 条错绑但不处置，其中 3 条仍走到附录 `verified`
> ⇒ 不执法则判据 D1（零信任反转）**结构性永不可达**。故下方"只记日志/依然无生产者"的旧措辞已作废。〕
> 同 PR 另加**判定 3「出处有效性」**（数值事实所引编号在表①登记的全非**可比**数值 → `audit_notsure`）
> —— 这条**不在原三检查设计里**，是本轮实证补的。
>
> **∴ 顶部「audit 永久停在 §3 as-built 形态」这句已不再成立**（判定层面亦然）：
> `audit_notpassed` 自 2026-08-05 起**有了唯一生产者** = 值核对失败分支。
> ⚠️ **但仍不是三检查复活**：日期不看；核值**只在量纲有保证的登记键上做**
> （[`audit_node.py`](../../../src/committee/agents/audit_node.py) `_COMPARABLE_DATA_KEYS`·今日 = `{price}`），
> `fred/value`（index / percent / billions_usd 随 series 变）、`rss/count`（元数据）落白名单外 →
> 走判定 3 如实 `audit_notsure`，**绝不发假 `audit_notpassed`**（假否定会被 fund_mgr 写进正文
> ⇒ 系统主动做内容为假的断言，比漏判更糟）。自由文本源（研报正文）核值仍不做。
> **写作待遇**：`audit_notpassed` = **写但强标注**，非"不写"（见 §5 表下方注）。
>
> **为什么重做不算推翻当年取舍**：当年砍它的理由是「输出侧验章门已兜住『错数字不到读者』」，
> 而输出侧**次日（07-15）就自我收窄为「只核引用不核值」** —— 交接断在那里、无人复查。详见
> [number-provenance-endgame.md](../../governance/number-provenance-endgame.md) 的一个月闭环时间线。
>
> **后续归属**：~~判定 4 转不转正 = 该文档**判据 D2**（观察期后强制二选一·不许无限期 log-only）~~
> → **D2 已 ✅ DONE（2026-08-05 转正落地）**；剩余判据（D1 零信任反转抽查 ×3 / D3 / 缺口 G2）
> 仍归 [number-provenance-endgame.md](../../governance/number-provenance-endgame.md)。本文件不再单独追踪该议题。
>
> ↓ 下方为 2026-07-14 CANCELLED 记录（point-in-time·不改）↓
>
> **❌ 目标态三检查已 CANCELLED（2026-07-14 用户拍·彻底砍）**：§4/§5 的三检查（尤"数字对不对"）**取消实现**（backlog [`AUDIT-3CHECK`](../../governance/backlog.md) 标 CANCELLED）。理由：fund_mgr 打码修复 **Path B（输出侧验章门）已兜住"错数字不到读者"安全底线**，audit 的输入侧数字核验非安全必需、不值承重工程。〔**连带失效（2026-07-24）**：§4 设计里"接住 DS-0 `watermark_claim_mismatch` 软 flag 当输入"——该 flag 本体已随 [#206](https://github.com/JunoChenZt/subagent-for-investment/pull/206)（backlog AJ·DS-0 死输出删除）不复存在。〕**∴ audit 永久停在 §3 as-built 形态**（"来源存在性"半项·数字丢弃·日期不看）。§1/§2 定位定性（audit = 确定性核对员 · 装备决策者 · 非安全闸判据）**仍有效**；§4/§5 目标态**作已放弃设计留存**（不删·point-in-time）。E1 audit_status 收 4 值里 `audit_notpassed` 因此永无生产者（占位）。

---

## 1. 大白话导读（非技术读者：基金经理 / 产品 / 合规）

- **audit 是个"照章办事的核对员"**：拿委员会整理出的每条事实，去系统自己拉的**权威档案柜（表①）**里核对，给它盖一个"核实状态"章。
- **它只做确定性核对**——不猜、不做判断、无 AI，像查字典：同样输入永远同样结果。
- **它盖的章主要给"基金经理写决策报告"用**：对不上的事实就别写进正文。这是**装备决策者，不替他决策**。
- **它证明不了"这件事在世界上是真的"**：决策真正吃劲的判断 / 进出场价位 / 宏观逻辑天生没法核对，审计够不着——这是诚实边界，不是毛病。
- 本文把"审计该核什么、盖的章给谁用、不碰什么"一次说清。

---

## 2. 定位定性（是什么 / 不是什么）

**是**：表①（内源结构化数据）内容的**确定性核对**——现 as-built = **来源存在性 + 引用精确性 + 出处有效性 + 可比键上的核值**（§3）。〔原目标态"三检查（数字/日期/来源·§4）"于 2026-07-14 **CANCELLED**；但 2026-08-05 [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 已在存在性之上加了三层只降不升的收严，~~audit 永久停在半项态~~ 口径作废·见顶 banner〕

**不是**：
- **不是核事实真伪的神谕**——无水印的判断 / 价位 / 宏观够不着（美光 e2e 40 条仅 7 passed 的机制根因）。
- **不是 AI 判断**——纯规则、零 LLM/MCP。
- **不是安全闸判据**——`audit_status` 已由 [DEFECT-D1-ROOT](../../governance/backlog.md) E简化移出 AD.7/C（落定 AUDIT-INTENT Q2）。

**"核实过"的真实语义** = 引用能对上号 +（目标态）数字搬运无误 + 来源明确，**≠"这件事是真的"**。

---

## 3. 现状 as-built（一手 file:line · 2026-07-03）

- **节点**：[`audit_pass_0_5`](../../../src/committee/agents/audit_node.py)，跑在 `ds_merge` 后 / `fund_manager` 前（[graph.py](../../../src/committee/graph.py)）；**纯确定性零 LLM/MCP**（[audit_node.py:122](../../../src/committee/agents/audit_node.py#L122)）。
- **存在性（底座）**：抽水印 `ref_id` → 查是否存在于表①（`common_context.references`）→ 盖章。**日期不看**。
- **★ 2026-08-05 [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 在底座之上加的三层收严**（全部只降不升·纯机械零 LLM·排序 = 精确性 → 核值 → 有效性）：
  - **引用精确性**（`_stamp_has_qualifier`）：章之外还有实质文字（`REF#Y-006 推算` / `[REF#Y-005 through Y-008]`）→ 该 watermark 不进 matched → 整体最高 `audit_notsure`。
    判据 = **剥掉合法章形态后残留里还有字母或数字**（`[^\W_]`·全脚本·不枚举关键词=开放集）；
    合法形态 = 裸 core / `[REF#Y-007]` / `[REF#T-001: price=35.8]`（**内联值必须带方括号**——
    无括号时正则会一路吞到串尾把限定词当内联值吃掉·2026-08-06 修）。
  - **核值**（`_check_value`）：fact 主数字 ↔ 所引编号在表① 的登记值比对（容差 2%），全不匹配 → **`audit_notpassed`**。⚠️ **只在 `_COMPARABLE_DATA_KEYS` 白名单键上做**（今日 = `{price}`）——`fred/value`、`rss/count` 量纲/语义不可比，落白名单外。~~"数字丢弃"~~ 口径作废。
  - **出处有效性**（`_numeric_registered` 为空）：数值事实所引编号登记的全非可比数值（`currency=USD` / `ticker=NVDA` / 研报正文 blob / 白名单外键）→ `audit_notsure`。
  - 引用本身不精确时**不升级**成 `audit_notpassed`（连它在引哪条都不确定，"值对不上"这个更强的断言没有立足点）。
- **智堡 MCP 核验层已于 EVID-4/#135（`5b0be8b`）移除**——引入版 `251f603` 曾实现（`_try_mcp_audit`/`_priority_score`），原设计见 [S2 §5.3 banner](../../roadmap/S2.md) / [09-known-pitfalls §122-124](../../governance/workflow/09-known-pitfalls.md)。
- **`audit_status` 枚举 = MASK.E1 后 4 活跃 + 3 legacy 只读**（[pass0.py:43](../../../src/committee/schemas/pass0.py)·E1 把乱 7 值收成 4 个自然判决类别）：**活跃 4 值** = `audit_passed`（核过对上）/ `audit_notsure`（audit_node 产·合并旧 `audit_partial_support`+`audit_inconclusive`+`audit_skipped` 三态）/ `audit_notpassed`（★**已启用**·2026-08-05 转正·**唯一生产者** = `_audit_fact_against_context` 核值分支；~~永久占位·无生产者~~ 作废）/ `not_audited`（没查·异常态默认）；**legacy 只读 3 值** = `audit_partial_support` / `audit_inconclusive` / `audit_skipped`（保留 Literal 成员仅为旧 archive replay 兼容·新代码不产·下游按 `audit_notsure` 同档处理）；**已删** = `audit_confirmed_mismatch` / `audit_failed`（从未进任何归档·命中皆 prompt 文本·随数字核验/MCP 一起删·无 compat 需要）。

---

## 4. 目标态：三检查（确定性 · 2026-07-03 定稿 · 码未实现）

> **铁律**：每项检查只有 ✅过 / ❌不过 / ⬜没法核（缺料）三结局，且**"没法核"绝不算"过"**（缺料如实标缺料）。

| 检查 | 怎么判（确定性） | 注记 |
|---|---|---|
| **数字对不对** | ref 号 → 表① 那行 `value`（原始源值）↔ fact 引用的数字，容忍范围内且口径一致 → 过；对不上 → 不过；无数字 → 没法核 | 确定性能硬核的是"源值 ↔ 水印值 + 那行须有真值"；**说法层**（大白话数字对不对）天生要 LLM → **接住 DS-0 的 `watermark_claim_mismatch` 软 flag 当输入**，不假装独立硬核。深版（给 fact 加结构化引用值·audit 独立硬核）= 改 schema·parked（§6） |
| **日期质量** | 表① 那行 `as_of`：缺失/畸形/未来/超新鲜窗口 → 不过 | ⚠️ **复用 confidence 现成新鲜度规则（同一套窗口）**，不另定阈值——否则"小重复"变"audit 说旧 / confidence 说新"打架。同一把尺 = 同答案算两遍·无害 |
| **来源** | ref 号在表① 找得到 + 来源名非空(+url) → 过；挂空引用/来源空 → 不过 | audit 今天已做一半（存在性），补"来源名非空"即完整 |

**合成规则（保守）+ 复用现有 7 态枚举（零 schema 改）**：

| 情形 | → `audit_status` |
|---|---|
| 三项全过（含日期新鲜）| `audit_passed` |
| **数字❌** | **`audit_confirmed_mismatch`**（复活死枚举）|
| 日期❌（`as_of` 过期/畸形）| `audit_inconclusive`（过期存疑 · 与 confidence `sourced_outdated` 重复 = 用户接受的"小重复"）|
| 来源❌（挂空引用/来源空）| `audit_inconclusive` |
| 缺料（无数字/无水印）| `audit_skipped` |
| 部分水印匹配 | `audit_partial_support` |
| 核验异常 | `audit_failed`（复活死枚举）|

> **用户决策（2026-07-03）**：audit 自己直接做三检查（接受与 confidence 在"日期"上的一点点重复·量小）。

---

## 5. 产出落地 + 消费者 + 边界

**产出形态（决策 A(a)）**：单个**合成 `audit_status`**（沿用 7 态枚举·**向后兼容**）+ `audit_rationale` 带三项细节（"数字✅ 日期✅ 来源❌"）。**读法**：fund_mgr + trace **不改读法**（仍读 `audit_status`）；**confidence 溯源门改读解耦的"来源/存在"信号**（**非**合成 status·见决策 B 的关键澄清）。

**三消费者（全部实测在用）**：

| 消费者 | 怎么用 | 性质 | 出处 |
|---|---|---|---|
| **fund_mgr 写入正文闸门** | 按 `audit_status` 决定**怎么写进决策正文**（passed→写 / 存疑→写但标注 / **`audit_notpassed`→写但必须显式点明"该数字未能与所引来源核对上"**·2026-08-05 由 ~~不写~~ 改：机械上分不清"抄错"与"挂错出处"，实测 6/6 是后者，删真数字比标注更糟）| **装备决策者 · 主用途** | [prompts.py:317-323](../../../src/committee/prompts/decision/prompts.py#L317-L323) |
| **confidence 溯源门** | 只有 `audit_passed` 走内源核实路 → credibility → 表③ → **间接连安全闸** | ⚠️ **承重 · 唯一通向 gate 的路** | [confidence.py:67](../../../src/committee/facts/confidence.py) |
| **trace / 指标** | 输出 `audit_status` 计数 | 给人看 | [trace_report.py:296-301](../../../src/committee/trace_report.py#L296-L301) |

> **🔄 2026-08-05 [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 实际走的是"不解耦"那条路**（本节 point-in-time·正文不改）：
> 下方"confidence 溯源门必须读独立信号"是为**三检查**写的要求，而 #226 只做**只降不升**的收严，
> `confidence.py` / `risk_gate.py` **一行未改** —— 合成 `audit_passed` 变窄 → 更多 fact 落 `unavailable`
> → 表③ 更多 `unverified` → AD.7/C 安全地板**只会更容易 fire，不会被压制** ⇒ 方向安全，
> 不构成下方担心的"违 D1-ROOT"（那担心的是收严让判定朝**不安全**方向翻）。
> seg9 实跑核过：地板未塌（verified 7 ≥ 2）、strip=0、quality gate 13/0/0。
> **若将来加"升信任"方向的检查，本节的解耦要求立即重新生效。**

**消费路由（决策 B · 解耦）**：三检查让 audit **变严**，但——
- ✅ **fund_mgr 写作 + trace 给人看**：吃"变严后"的丰富结论（数字对不上就别写进正文 = 你要的"基石"把关）。
- 🔴 **confidence 溯源门本轮冻结（"行为冻结"·非"读法字面不动"）**：⚠️ **关键澄清**——合成 `audit_passed` 因数字/日期收严后变严，**若 confidence 继续读合成 status，其入门集合会被间接收严 → credibility → gate 变（违 D1-ROOT）**。∴ AUDIT-3CHECK **必须让 confidence 溯源门读一个不受数字/日期收严影响的独立"来源/存在"信号**（= 今天 `audit_passed` 的存在性判据 · **same facts pass · 行为等价冻结**），**而非合成 status**。数字/日期结论只流到 fund_mgr + trace。〔与决策 A(a) 的"向后兼容"不冲突：兼容只对 fund_mgr + trace 成立；confidence 的读法必须解耦，否则 A(a)+B 自相矛盾。〕

**边界铁律**：audit 变丰富，**不新增任何 "audit → 安全闸" 的路**（守 [DEFECT-D1-ROOT](../../governance/backlog.md) 刚把 audit_status 移出闸的成果）。**"数字准确度要不要进 credibility/gate" = 层② 的"闸门真值信号"设计，不在本轮预支。**

**指标口径**（关掉 AUDIT-INTENT 候选 c 残留）：`audit_passed` 率 = **引用对号覆盖率**，**≠ 事实可靠率**——[trace_report.py:296-301](../../../src/committee/trace_report.py#L296-L301) 的计数勿当"可靠率"读。

---

## 6. 实现状态 + 给层② 的前提

- **目标态三检查 = ❌ CANCELLED（2026-07-14 用户拍彻底砍）** → [backlog `AUDIT-3CHECK`](../../governance/backlog.md) 已标 CANCELLED。原追踪（承重·改 audit 行为·数字深版子项）**取消**。~~audit 永久停在 §3 as-built~~ 〔**2026-08-05 起不成立**：#226 启用了三检查给"数字对不上"预留的判决位（`audit_notpassed`），但**不是**三检查的实现方案——日期仍不看、核值只覆盖量纲有保证的键、自由文本源不做。见顶 banner〕。
- **给层② 的前提约束（AUDIT-INTENT 作为层②前置的正经交付）**：`audit_status` **≠ 闸门真值信号**——它是引用可解析性（非可信）、findings 根本无此字段、旧编码方向反了。**∴ 层② 须新造"闸门真值信号"（融合有无源 + 新鲜度 + 印证数），不得复用 `audit_status`。**
- **层② 现状**：本轮全程在 AUDIT-INTENT，**层② 一行未动**；三检查与层②基本正交（层②管"闸读什么真值"·三检查管"audit 内部怎么核"）。层② 仍 pending。

---

## 7. 关联

- 前身议题 = [DEFECT-AUDIT-INTENT](../../governance/backlog.md)；病根族 = [DEFECT-D1-ROOT](../../governance/backlog.md)；~~实现追踪 = AUDIT-3CHECK~~ **实现已 CANCELLED（2026-07-14·三检查不做）**。
- 机制全图 = [gate-mechanisms-map.md](gate-mechanisms-map.md)（audit 是其中一格）；三表定义 = [dataflow §15.5](../dataflow-whole-pipeline.md)。
- 原始设计（含已移除的 MCP 层）= [S2 §5.3](../../roadmap/S2.md) / [S2.3-decomposition Goal 3](../../plans/S2.3-decomposition.md)（均带 superseded banner）。
