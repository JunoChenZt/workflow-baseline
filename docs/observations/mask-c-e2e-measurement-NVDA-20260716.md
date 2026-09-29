# MASK.C e2e 测量 findings — 誊写核对概率 + 过度打码坐实（NVDA·2026-07-16）

> **性质**：MASK.C 收口 e2e 的第一个测量 run（NVDA·`docs/observations/_checkpoints/run-NVDA-还能追吗-20260715-172312`）。
> 目的双重：① 验 MASK.C 掩码修复（9 段全过 + quality gate 12/1/0）；② 量 backlog **AS**（誊写核对）真实价值。
> 真值源 = seg9 checkpoint（`final_decision.claim_audits`）+ fund_mgr(opus) 原始输出 diff。

## 大白话导读

- 我们本来担心「决策书里的数字来自网络、没法核对是否抄错」，想为此建一套「誊写核对」（backlog AS）。
- 真跑一遍量下来：**opus 把所有有来源的数字都抄对了，一个没抄错**——誊写核对门几乎没用武之地。
- 而真正让报告变丑的过度打码，**不是**「事实没法核对」，而是把**年份、列表序号、决策者自己写的仓位/价位区间**当成外部数字给涂了。这是 MASK.C 自己的打磨 bug，跟 AS 无关，而且更该修、更便宜。

## 一、AS 测量结果 —— 誊写核对概率 ≈ 0

43 个正文数字（`claim_audits`）分四类：

| 类 | 数量 | 说明 |
|---|---|---|
| ① 有源 + 誊写一致（numeric_match=True） | **22** | opus 全抄对 |
| ② 有源 + 值不匹配（= 抓到抄错） | **0** | 一个抄错都没有 |
| ③ 无源被打码 | **21** | 见第二节——**基本不是可溯源事实** |
| ④ 其他 | 0 | |

- confidence 分布：verified 17 / sourced 4 / unavailable 21 / controversial 1。
- **可溯源事实全部保留且抄对**：目标价 $300、共识 $316.79、股价 $203.53、营收增速 85% 等都在 22 个保留里。
- **结论**：真跑中 opus 誊写零错 → **誊写核对门 fire 0 次**。**AS 价值远低于预期**（N=1·NVDA·A股 run 待确认）。AS 应降优先级 / defer。

## 二、真正的过度打码 = 豁免缺口 + caveat 叠加（可修条目·坐实）

被打码的 21 个基本不是外部事实。fund_mgr(opus) 原始输出 vs 最终打码版 diff（DEFINITIVE）：

| 原文 | 打码后 | 类别 |
|---|---|---|
| `2025 年` / `2026 年` | `相关数值25 年` / `相关数值26 年` | 年份（带标路径连带） |
| `2027H2` | `2027H相关数值` | 半年标 digit |
| `(1) …(2)…(3)` | `(相关数值) …(2)…` | **列表序号·且不一致** |
| `5-10% 仓位` | `相关数值-10% 仓位` | 决策者处方仓位区间 |
| `$170-180` | `$170-相关数值` | 价位区间端点 |
| `6-12 月` / `1.8M` | `6-相关数值 月` / `相关数值.8M` | 时间区间 / 量级整数部 |
| — | `（未独立核实）（未独立核实）（未核实）` 三连 | **caveat 叠加** |

### Root cause（读码坐实·两条路）

**A. 裸数字 scan 漏豁免**（[`_apply_stamp_gate`](../../src/committee/agents/base.py) line 2168-2193 + [`_is_noise_number`](../../src/committee/agents/base.py) line 157）
- `_is_noise_number` 只认**完整 4 位年**（`2025` 匹配→skip）+ A股 6 位码；**列表序号 `(1)` 的 "1"、区间端点 `5`/`180`/`12`、`2027H2` 的 "2"** 全 `noise=False` → 漏。
- `_decision_prescribed_numbers`（line 1950）只扫**结构化 `position_size`/`execution_plan` 字段**、**不扫 thesis 正文** → 正文里写的仓位/价位区间不在豁免集（按数值匹配也只豁免恰好等于结构化值的那个端点）。

**B. 带标短语连带打码 + caveat 叠加**（stamp path·line 2142-2163 + CAVEAT line 2131）
- `Blackwell 2025年 5.2M→2026年 1.8M{ref:fX}` 整段挂一个 🟡 标 → `nums_before_stamp` 把**年份**连同数字圈进 → 年份被 caveat/涂。
- `（未独立核实）`（stamp-gate CAVEAT）+ `（未核实）`（[verify-block](../../src/committee/agents/base.py) line 1936-1942·fund_mgr 按 prompt 自写）**双系统 + 无 dedup** → 三连叠加。

### 可修条目（供 backlog 立项·按便宜→贵）

1. **列表序号豁免**（便宜）：scan 跳 `(\d)` / `\d[.)、]` 列表序号。**definitely wrong·安全无损**。
2. **caveat dedup**（便宜）：同一 location 去重 `（未独立核实）`/`（未核实）`，双系统合一。
3. **年份/半年标 scan 加固**（中）：`2027H2` 的 "2"、带标短语里 `nums_before_stamp` 圈进的年份——年份识别扩到「4 位年 ± H[12] / 前后紧邻年」。
4. **正文处方区间豁免**（中偏贵）：`_decision_prescribed_numbers` 扩到扫 thesis 正文的仓位/价位/时间区间，或区间端点「一端已豁免则另一端连带豁免」。需 scan 带 location·治本。

## 三、对 MASK.C 收口的影响

- **功能正确**：掩码在事实上正确（0 抄错·可溯源事实全保留·83-90% 冤枉打码已治）。
- **但打磨未净**：上述过度打码让报告仍有「相关数值25年」「(相关数值)」「（未独立核实）×3」的丑态——而**可读性正是 MASK.C 的初衷**。是否阻断 MASK.C 合并 = 待用户裁（非安全问题·过度打码是安全方向；但伤初衷）。
- **A股 run 待确认**：本 findings N=1（NVDA·web-heavy）。A股（tushare 结构化 fundamentals）run 会确认 pattern 是否一致 + 补 AS 结构化那格样本。

## 关联

- backlog **AS**（誊写核对·本 findings 降其优先级）
- backlog **AF/AA/DEFECT-E2E-RESUME**（fundamentals rework 退化·见同 run OBSERVATION-fundamentals-rework-drop（`_checkpoints/run-NVDA-还能追吗-20260715-172312/OBSERVATION-fundamentals-rework-drop.md`·跑批工作目录·未入库））
- [fundmgr-mask-fix-series](../plans/fundmgr-mask-fix-series-2026-07-14.md) / [DEFECT-PROSE-MASK-REF](../governance/backlog.md)
