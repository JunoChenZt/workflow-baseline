# Trading Debate 项目架构与路线图（v3.4）

整理日期：2026-05-13
版本：v3.4
状态：S1 已完成，S2 进行中（35-45%）

> ⚠️ **前向 banner（2026-07-29 docs-audit 加·正文一字不动）**：本篇是 **2026-05-13 的 point-in-time
> 架构快照**，其"状态/进度/枚举"随后已被实现推翻。**当下状态一律以 [S2.md](S2.md) 为准**；本篇留作
> 设计意图与演进史。已知与当前实现的偏离（不逐一改正文）：
>
> 1. **上方状态行**「S2 进行中（35-45%）」已 stale —— S2 现 **~100%**（见 [S2.md](S2.md) 顶部进度行）。〔2026-09-28 更新：**S2 已收口**，见 [收口报告](../observations/s2-close-report-2026-09-28.md)；S3 可启动〕
> 2. **DS-0 从 4 维度收为 3 维度**：`cross_role_alignment`（含 `CrossRoleAlignment` / `DivergentClaim`
>    schema）是**死输出**、全仓零 consumer，已随 [#206](https://github.com/JunoChenZt/subagent-for-investment/pull/206)（backlog AJ·2026-07-24）删除。
>    正文中凡出现"4 维度"、`CrossRoleAlignment` 者，均指当年设计。
> 3. **`watermark_claim_mismatch` 软 flag 已不存在**（随 #206 同批删）：DS-0 侧的水印-claim 初筛
>    是"空中楼阁"（没有 `[REF#]` 原始数据、物理核不了），prompt 与 sanity check 第 8 项一并移除；
>    真数字核对由下游 `exec_floor` check① 确定性承担。正文中所有"看到 `watermark_claim_mismatch`
>    flag 的 facts…"分支、以及"该 flag 比例 > 50% → warning"指标，均为**已废设计**。

## v3.4 主要变更（相对 v3.3）

| 维度 | v3.3 | v3.4 |
|---|---|---|
| **Phase 1 内容/格式分离** | 未讨论 | **新增附录 E：决策与时机（S2 维持现状 / S3 评估）** |
| **S2.2 观测指标** | 含分轮可见性指标 | **新增内容/格式分离相关的诊断指标** |
| **S2.3 观测指标** | 含 audit 指标 | **新增内容/格式分离相关的诊断指标** |
| **S3 backlog** | 含 web search 集成 | **新增 Phase 1 内容/格式分离改造项** |

### v3.4 核心增量

**问题**：v3.3 中 Phase 1 analyst 的内容和格式仍然是 LLM 一次性混合输出，没有分离。软 schema + 分诊员是事后容错机制，不是事前职责分离。

**v3.4 决策**：S2 维持现状（稳定性原则），S2.2 / S2.3 加入诊断指标，S3 基于真实数据决定是否做分离改造（借鉴 Phase 4 DeepSeek 助理模式）。

### 保留 v3.3 全部核心内容

稳定性原则 / Q1-Q5 全部锁定 / fund_manager Audit Pass / 组件失败完整 fallback / time budget 90s / degraded run / S2.2 任务重新编排 / S2.3 工期 4.5-5 周。

---

## v3.3 主要变更（相对 v3.2，保留参考）

| 维度 | v3.2 | v3.3 |
|---|---|---|
| **核心原则** | 隐含 | **新增第零章：稳定性原则——稳定能跑 > 质量** |
| **Q2 E 类规则** | 先全量再观测 | **E1 全量 / E2/E3 🔴 强检测 + 🟡🟢 条件触发 + 抽样兜底** |
| **Q3 水印对抗性** | fund_manager Phase 4 audit | **DeepSeek 助理初筛 + fund_manager Pass 0.5 audit（common_context + 智堡 MCP）** 〔智堡 MCP 已于 EVID-4/#135 移除·现纯 common_context〕 |
| **Q4 S2.1/S2.2 并行** | 待决 | **默认串行（单人），多人可并行（限定任务）** |
| **Q5 DeepSeek 助理质量** | 待决 | **3 层保证（schema validator + sanity check + fund_manager audit）** |
| **Tavily/Serper** | 曾考虑提前 | **仍保持 S3，与 bull/bear web search 一起做** |
| **audit 外部源** | 仅 common_context | **新增智堡 MCP（复用 S2.2 接入），3 次/run** 〔已于 EVID-4/#135 移除·退回"仅 common_context"〕 |
| **Fallback 路径** | 散落各章 | **新增第十六章：组件失败完整 fallback 路径** |
| **time budget 硬上限** | 缺失 | **单 run 90s + degraded run 机制** |
| **跨 phase 链式失败** | 缺失 | **新增 corner case** |
| **S2.2 任务编排** | Week 2 密集 | **D 类前置 Week 1 末，分轮可见性独占 Week 2** |
| **S2.3 工期** | 4 周 | **4.5-5 周（增加 audit pass 实现）** |

### 保留 v3.2 全部核心内容

北极星裁决 / S1-S4 框架 / Query Classification / 数据水印硬检查 / 软 schema 4 层降级 / 分诊员 A-F 类规则 / 复述退化检测 / 分轮可见性 / EvidenceItem schema 扩展 / 智堡 MCP / Observation Gate / 合规 4 层 + FAA / 数据源分阶段 / S2 子阶段切分 / DeepSeek 助理 + opus / Verification Report 模板

---

## 零、双重核心原则

### 0.1 北极星裁决原则

**北极星**：装备决策者，不取代决策者。

#### 默认不做
- 自动下单 / 自动调仓 / 无人确认的交易执行
- 长期记忆 / AI 投顾业务化

#### 可以做
- 执行计划（数字 + 锚定 + 来源）
- 风险触发器 / 再评估提醒
- 组合影响分析 / 历史决策对比

### 0.2 工程稳定性原则（v3.3 核心）

**稳定能跑 > 质量**。

#### 含义

- **不允许整 run 崩溃** 永远是第一优先级
- **质量保证机制的失败必须有 fallback**，不能把质量检查变成阻塞点
- **任何新增机制都要有"如果它挂了怎么办"的明确路径**
- **质量是渐进改善的方向，不是一次到位的承诺**
- **质量保证机制本身不能成为新的故障点**

#### 优先级排序

```
Priority 1: 整 run 不崩溃，永远产出最终报告（即使是 degraded report）
Priority 2: 单组件失败有明确 fallback
Priority 3: 多层 fallback 嵌套时仍有最终兜底
Priority 4: time budget 硬上限保证用户体验
Priority 5: 质量保证机制是改善方向，不是阻塞门
```

#### 在 v3.3 中的落地

- 每个新机制必须有"完全失败时怎么办"的明确路径（第十六章）
- 单 run 总延迟硬上限 = **120s**（超时降级）〔2026-09-08 由 90s 抬·出计划那笔 40→85s 连带·见 [S2 §6.7](S2.md#67-time-budget-硬上限)〕
- 整 run 的 fallback report 比例 > 50% → 标记 degraded run，仍产出
- 跨 phase 链式失败必须能产出 degraded report
- 所有质量保证机制失败时跳过，不阻塞

---

## 一、当前已完成工作与真实 Pipeline 结构

### 1.1 真实的 Pipeline 结构（2026-05-12 改名后）

```
Phase 1 · 调研: 8 analyst（各 1 次）
Phase 2 · 辩论（v3.2 分轮可见性）: bull/bear 3 轮
Phase 3 · 投票: 10 voters
Phase 4 · 裁决（v3.3 修订）:
    Pass 0: DeepSeek 助理（信息整理 + 一致性初筛）
    Pass 0.5: fund_manager Audit Pass（common_context 确定性核对；智堡 MCP 已移除·EVID-4/#135）
    fund_manager [claude-opus-4-7] 3-pass
```

### 1.2 当前已完成工作清单

> 截至 2026-05-13。详细 pending 任务 → [S2.md](S2.md) / [S3.md](S3.md) / [S4.md](S4.md)。

#### S1 MVP 主体（~95%）

- LangGraph 编排：START → 8 parallel analyst → 6 sequential debate → 10 parallel voter → fund_manager 3-pass → END
- 8 analyst role pipeline（macro / sentiment / technical / fundamentals / commodity / political / historian / economist）+ 10 voter + fund_manager
- SSE streaming + chunk event whitelist bucketing
- Frontend committee UI（CommitteePage / ExecutionPlanCard / ResearcherCard 等）
- Reference 库：N3 local agent Phase 1 国内 41 研究员 .md + Phase 2 大行 link 7-dim 提取（PR-3a 干净化 redact）

#### S2 已落地（约 35-45%）

| 类别 | 已完成 PR / commit |
|---|---|
| 治理 / 抽常量 | PR-0 spec commit `473a654` / B.1 6 项小 PR `ca32118` + `da3e6d2`（tier docstring / VOTING_ROLES 白名单 / fund_mgr 签名 / stage-level temp / EXECUTION_PLAN_CONTRACT / DEBATE_KEY_CLAIMS_CONTRACT 抽离）|
| 版权 redact | PR-3a `abc97ca`（104 文件 +6593/-12755；raw .txt → cited spans + 13 IB/Reuters stub）|
| Voice anchor 锁定 | PR-4（B.7.3 6 名册 + 6-rule 消费规则 + voice/1.0 → verbatim/1.0 升级钩子）|
| Schema 加性升级 | PR-5 `28790e7` / merged `0681770`（19 字段 + convergence_warning + `_COMMON_OUTPUT` 镜像）|
| Role prompt 激活 | PR-6 `22c15fb` / merged `663f500`（macro / sentiment / commodity / historian）+ PR-7-technical（含 _VOICE_ANCHOR_GUARDRAILS 段 + 17 negative guardrail 测试）|
| Breaking schema gate | PR-8a（`confidence: int 1-10` → `conviction: Literal[...]` 含 DATA_INSUFFICIENT）✅ **gate PASSED** |
| fundamentals 激活 | PR-8b（VOTING_ROLES 加 fundamentals + 7 段 prompt + bull/bear 回响室警示）✅ **gate PASSED** |
| 数据基础设施 | PR-10a `25ee916` + follow-up `88b3cd9`（Fact schema + SQLite cache + intent TTL；S2.1 召回层第一砖）|
| Voter 聚合 | PR-11d `cdc661c`（10-voter even-number median = 5th + 6th 平均 + IQR outlier）|
| KPI / as_of 一等公民 | PR-12d-1 `f96b135`（KPI Dashboard + as_of 字段化）|
| Portfolio Context Lite | PR-12e `3e49adc` + v2 fix `10796de`（prompt-level context injection）|
| 文案审计 | PR-14 `848f103`（去 "9-agent debate × 3 rounds" → "multi-agent investment committee / 研究—辩论—投票—裁决流程"）|
| Demo Compliance Layer | PR-DCL-1 `833d34f` + test `e0724c9`（ComplianceModal disclosure shell + 8 case 组件测试）/ PR-DCL-2 `5c9d820` + `e23d29b`（DecisionCard 视觉降权 + DEMO_COMPLIANCE_MODE env）/ PR-DCL-2 v2 `2b7d993`（desaturated directional tone）|
| OBS-FIX 修复（main 截至 `b10c765` 2026-05-07）| OBS-FIX-1 #64（failure_trigger 硬约束）/ OBS-FIX-2 #64（macro / historian scenarios 概率差异化）/ OBS-FIX-4 #60+#63（audit 输出落盘 + thinking budget 修）/ OBS-FIX-5（archive technical presence 事实复核）/ OBS-FIX-6 #67+#69（technical scenarios 结构化输出）/ OBS-FIX-7 #66（execution_plan take_profit null 边界）/ OBS-FIX-7-neighbor PR #80（StopLoss / EntryRange / TakeProfitItem null item-shape）|
| PR-8a hotfix 串 | inline `9eba875` TakeProfitItem null + `3c34b17` `_COMMON_OUTPUT` conviction 公共模板修 |
| Schema follow-up | as_of strict whitelist normalizer `77612dd`（observation enabler，freeze exception 已落 origin）|

#### S4 已落地（约 25%）

- **AS-1 安全硬化**（PR #88-92）：`/analyze` & `/analyze/stream` 鉴权 / `SECRET_KEY` production fail-fast / reset token 批量失效 / logout 不吞异常 / `tests/auth` 补齐
- 部署链：alembic + migrations 进镜像 `23257db`；slowapi.env include 进 wheel
- env 模板：`COMMITTEE_MODEL_FUNDAMENTALS` 补齐 `330bf9c`

#### 进行中 / 未启动

详细任务 → [S2.md](S2.md)（S2.1/2.2/2.3 主体 + P4.B Risk Gate）、[S3.md](S3.md)（三条线 + web search + 校准曲线）、[S4.md](S4.md)（AS-2/3/4）。

### 1.3 当前 Observation Gate 状态

| PR | 状态 |
|---|---|
| PR-8a | ✅ PASSED |
| PR-8b | ✅ PASSED |
| PR-8c | ⏸ PENDING（S2.1 freeze 后启动） |

---

## 二、四阶段总览

| 阶段 | 一句话 | 进度 |
|---|---|---|
| S1 · MVP | query → 结构化报告全链路 | ~95% ✅ |
| S2 · 决策助手 | 每个数字可审计 + 决策可对照历史 | ~35-45% 🟡 |
| S3 · 商业化原型 | 10 人付费 + 持续监控 + 视觉化 debate | 0% ⚪ |
| S4 · 用户自定义委员会 | 每用户带自己的配置 | ~25% |

---

## 三、当前架构（v3.3 完整版）

### 3.1 完整管道

```
═══════════ Phase 0: 信息召回 ═══════════
    Phase 0a: 公共数据召回
    ├─ Step 0.0: Query Classification（轻量 LLM）
    ├─ Step 0.1: 按类型构建 common_context
    ├─ Step 0.2: 并行召回
    │   【基础数据层】AKShare / yfinance / FRED / RSS
    │   【投研深度层】智堡 MCP（S2.2）
    └─ Step 0.3: 数据水印化（[REF#xxx]）
    ↓
═══════════ Phase 1: 并行研究 ═══════════
    8 个 analyst 并行（软 schema 模式）
    ↓
═══════════ Phase 1.5: 质量分诊 ═══════════
    Quality Gate Assistant [deepseek-chat]
    ├─ Python 规则预筛选（A/B/D + E1）
    ├─ LLM 检查（C + E2/E3 按 role 分级）
    └─ needs_rework + rework_reasons
    ↓
═══════════ Phase 2: 3 轮辩论（v3.2 分轮可见性）═══════════
    Round 1 封闭 / Round 2 半开放 / Round 3 收束
    ↓
═══════════ Phase 3: 并行投票 ═══════════
    10 voters
    ↓
═══════════ Phase 4: 最终裁决（v3.3 修订）═══════════

    Pass 0: DeepSeek 助理（信息整理 + 一致性初筛）
    ├─ 整理 4 维度 schema
    ├─ 初筛：水印 - claim 一致性
    │   └─ 不一致 → quality_flag: "watermark_claim_mismatch"
    └─ 严禁：方向判断 / 重新分析 / 散文写作

    Pass 0.5: fund_manager Audit Pass（v3.3 新增·⚠️ 智堡 MCP 层已于 EVID-4/#135 移除→下列"双重核验 / MCP 配额 / 30s 上限"均废·现纯 common_context 亚秒）
    ├─ 看到 watermark_claim_mismatch flag 的 facts
    ├─ 优先级排序：Strong* / 多 role 引用 / 关键论点
    ├─ 高优先级 fact: common_context + 智堡 MCP 双重核验
    ├─ 中优先级 fact: 仅 common_context 核验
    ├─ 智堡 MCP 配额: ≤ 3 次/run, 单次 ≤ 8s
    ├─ Pass 0.5 总耗时硬上限: 30s
    └─ 失败 fallback:
        · 智堡 MCP 不可用 → 仅 common_context 模式
        · 整 audit pass 失败 → 跳过到 Pass 1

    fund_manager [claude-opus-4-7] 3-pass
    ├─ Pass 1: outline（基于 audit 后的 facts_inventory）
    ├─ Pass 2: head + core_risks + execution_plan
    │          thesis 用 {ref:fX} 占位
    │          execution_plan 取 10 voter 中位数（PR-11d）
    └─ Pass 3: 各 section 并行 expand
    ↓
    强制 disclaimer（合规 L2）
    ↓
最终决策报告（含真实数据引用 + 来源链接 + 完整溯源链）
```

### 3.2 完整溯源链

```
用户读到 thesis 中的某个数字
    ↓ {ref:fX}
DeepSeek 整理的 facts_inventory[X]
    ↓ watermarks + cited_in_phase + audit_status
    ↓
原始召回数据 / 真实新闻 URL
```

### 3.3 认知层次的边界

| Phase | 消费什么 | 不消费什么 |
|---|---|---|
| Phase 0 | 数据源 API | — |
| Phase 1 | common_context | — |
| Phase 2 Round 1 | 8 analyst report | common_context |
| Phase 2 Round 2 | analyst + Round 1 + common_context | web search (S2) |
| Phase 2 Round 3 | analyst + Round 1/2 + common_context | 新数据来源 |
| Phase 3 | analyst + debate | common_context |
| Phase 4 Pass 0 | 全部上游 | — |
| Phase 4 Pass 0.5 | facts_inventory + common_context + 智堡 MCP | Tavily/Serper（S3）|
| Phase 4 fund_manager 3-pass | DeepSeek 整理 + 原始 + common_context | — |

---

## 四、Phase 2 分轮可见性详细设计（保留 v3.2）

详见 v3.2 第四章。核心点：

| 信息类型 | Round 1 | Round 2 | Round 3 |
|---|---|---|---|
| 8 analyst report | ✅ | ✅ | ✅ |
| 辩论历史 | ✅(空) | ✅(R1) | ✅(R1+R2) |
| common_context | ❌ | ✅ | ✅ |
| web search | ❌ | ⚪(S3) | ❌ |

F 类规则（分轮可见性合规检查）：F1-F5 见 v3.2。

EvidenceItem schema 扩展含 v3.3 新增 audit_status 字段（见 5.4）。

---

## 五、Phase 4 DeepSeek 助理 + Audit Pass（v3.3 修订）

### 5.1 设计哲学

```
DeepSeek 助理（Pass 0）= 信息整理员（覆盖率优先）
fund_manager Audit（Pass 0.5）= 终审（精确度优先，用 common_context + 智堡 MCP）
fund_manager 3-pass = 裁决 + 写作
```

### 5.2 DeepSeek 助理职责

- 信息整理员，不是分析师
- 严格 schema 输出
- 4 维度：facts_inventory + debate_summary + vote_distribution + cross_role_alignment
- 初筛：水印 - claim 一致性检查

### 5.3 4 维度输出 Schema（v3.3 微调）

```python
@dataclass
class FactInventoryItem:
    fact_id: str
    claim: str
    watermarks: list[str]
    cited_by_roles: list[str]
    cited_in_phase: list[str]
    source_type: Literal[...]
    as_of: str
    supporting_data: Optional[str]
    consensus_level: Literal["consensus", "majority", "minority", "single"]
    
    # v3.3 新增
    quality_flags: list[str] = Field(default_factory=list)
    audit_status: Literal[
        "not_audited", "audit_passed", "audit_confirmed_mismatch",
        "audit_partial_support", "audit_inconclusive",
        "audit_skipped", "audit_failed"
    ] = "not_audited"
    audit_rationale: Optional[str] = None
```

DebateSummary / VoteDistribution / CrossRoleAlignment 保留 v3.2 内容。

### 5.4 EvidenceItem audit_status 字段

```python
class EvidenceItem(BaseModel):
    claim: str
    source: str
    as_of: str
    source_type: Literal[
        "retrieved",
        "retrieved_from_common_context",
        "retrieved_from_web",
        "inferred",
        "DATA_INSUFFICIENT"
    ]
    cited_in_phase: Literal["phase_1", "phase_2_round_1", "phase_2_round_2", "phase_2_round_3"]
    retrieval_url: Optional[str] = None
    supporting_data: Optional[str] = None
    
    # v3.3 新增
    audit_status: Optional[Literal[
        "not_audited",
        "audit_passed",
        "audit_confirmed_mismatch",
        "audit_partial_support",
        "audit_inconclusive",
        "audit_skipped",
        "audit_failed"
    ]] = "not_audited"
    audit_rationale: Optional[str] = None
```

### 5.5 fund_manager Audit Pass（v3.3 新增）

#### 职责

```
看到 quality_flag: "watermark_claim_mismatch" 的 facts
    ↓
按优先级核验:
高优先级: common_context + 智堡 MCP 双重核验
中优先级: 仅 common_context
低优先级: 跳过（time budget 不足）
    ↓
audit_status 判定:
├─ 完全一致 → audit_passed
├─ 部分一致 → audit_partial_support
├─ 完全不一致 → audit_confirmed_mismatch
└─ 仍存疑 → audit_inconclusive
```

#### 优先级排序

1. Strong* conviction 相关 fact
2. 多 role 引用过的 fact
3. 在 bull/bear 关键论点中出现的 fact
4. 其他 mismatch fact

#### 边界

| 行为 | 允许 | 不允许 |
|---|---|---|
| 核验 evidence 真实性 | ✅ | — |
| 用 common_context 核对 | ✅ | — |
| 调用智堡 MCP 核验 | ✅ | 配额 ≤ 3 次/run |
| 调用 Tavily/Serper | ❌ | S3 才支持 |
| 标记 fact audit_status | ✅ | — |
| 影响 thesis 中引用与否 | ✅ | — |
| 推翻 bull/bear 整体论点 | ❌ | — |
| 降权 bull/bear 投票 | ❌ | Phase 3 已结束 |

#### Time Budget

```
Pass 0.5 总耗时硬上限 = 30s
智堡 MCP 单次超时 = 8s
智堡 MCP 调用配额 = 3 次/run

超时处理:
- 已 audit 保留结果
- 未 audit 标 audit_skipped
- 立即进入 Pass 1（不阻塞）

智堡 MCP 失败:
- 单次失败 → 跳过该 fact 智堡核验，仍可用 common_context
- 完全不可用 → audit 降级为"仅 common_context 模式"

整 audit pass 失败:
- 所有 mismatch fact 标 audit_failed
- 进入 Pass 1
```

#### Audit 结果如何影响 thesis 引用

| audit_status | 引用方式 |
|---|---|
| not_audited（无 flag） | 正常引用 |
| audit_passed | 正常引用 |
| audit_partial_support | 加 "based on interpretation of..." |
| audit_confirmed_mismatch | 不引用 |
| audit_inconclusive | 谨慎引用，可加 "subject to further verification" |
| audit_skipped / audit_failed | 谨慎引用 |

#### 智堡 MCP 在 audit 中的角色

```
智堡 MCP 不创建新 evidence:
- audit 是核验工具，不是 evidence 来源
- 智堡核验结果不进 evidence_log
- 仅记录在 audit_rationale 字段（fund_manager 内部参考）

智堡 MCP 调用模式（S2.2 同步调研）:
- 复用 Phase 0a 已用的 tool（默认）
- 如智堡 MCP 提供"按 claim 搜索"专门 tool，audit 用专门 tool
```

### 5.6 fund_manager Prompt 扩展（Pass 0.5）

```
【Pass 0.5: Audit Pass】

在做 outline 之前，先快速 audit facts_inventory:

1. 找出所有带 quality_flag: "watermark_claim_mismatch" 的 facts
2. 优先级排序:
   a. Strong* conviction 相关 fact - 智堡 + common_context 双重
   b. 多 role 引用过的 fact - 智堡 + common_context 双重
   c. bull/bear 关键论点中的 fact - 智堡 + common_context 双重
   d. 其他 mismatch fact - 仅 common_context

3. 对每个 fact:
   a. 找到对应的 [REF#xxx] 在 common_context 中的原文
   b. 核对 fact.claim 是否真的能由原文支撑
   c. 高优先级 fact: 如有疑虑，调用智堡 MCP 进一步核验
   d. 判定 audit_status

4. Time budget 30s，智堡 MCP 配额 3 次
5. 超时或失败 → 剩余 fact 标 audit_skipped

【边界】
- 不推翻 bull/bear 整体论点
- 你只决定 thesis 中如何引用 evidence
- 智堡核验结果不进 evidence_log

【失败处理】
- 智堡 MCP 单次失败 → 跳过该 fact 智堡核验，仍可用 common_context
- 智堡 MCP 完全不可用 → 降级为"仅 common_context 模式"
- audit 完全失败 → 进入 Pass 1，所有 fact 标 audit_skipped

【接下来 Pass 1-3】
- 不引用 audit_confirmed_mismatch fact
- audit_partial_support 加限定语
- audit_inconclusive / audit_skipped 谨慎引用
- 正常引用 audit_passed 和 not_audited
```

### 5.7 Fallback 机制

```python
async def phase_4_with_assistant(state: CommitteeState) -> dict:
    # Pass 0: DeepSeek 助理
    try:
        assistant_output = await asyncio.wait_for(
            deepseek_information_assistant(state),
            timeout=15
        )
    except (DeepSeekError, SchemaValidationError, asyncio.TimeoutError):
        log.warning("DeepSeek assistant failed, fallback to direct consumption")
        state.quality_flags.append("phase4_deepseek_assistant_failed")
        return await fund_manager_3pass_direct(state)
    
    # Pass 0.5: Audit Pass
    try:
        audit_result = await asyncio.wait_for(
            fund_manager_audit_pass(
                assistant_output,
                state.common_context,
                # 注：原 wisburg_mcp_quota=3 已废（2026-08-21 G4b·#263）——
                # 那道闸按连接计数、从未触发过；调用量的闸现在在 run 级
                # （run_budget，整趟跑批共用，默认 60，含 agent 侧 9 个角色）
            ),
            timeout=30
        )
        assistant_output = apply_audit_results(assistant_output, audit_result)
    except (asyncio.TimeoutError, AuditError):
        log.warning("Audit pass failed or timed out, skipping")
        state.quality_flags.append("phase4_audit_skipped")
    
    return await fund_manager_3pass(assistant_output, state)
```

### 5.8 DeepSeek 助理质量保证（v3.3 Q5 锁定）

#### 第 1 层: Schema Validator（必做）
- Pydantic 强制验证
- 验证失败 → 重试 1 次
- 重试仍失败 → fallback opus 直接消费原始数据

#### 第 2 层: Sanity Check（软警告，不阻塞）

| 检查 | 触发条件 | 处理 |
|---|---|---|
| facts_inventory 完全为空 | len == 0 | warning |
| facts_inventory 极少 | len < 3 | warning |
| facts_inventory 极多 | len > 50 | warning |
| bull/bear claims 为空 | len == 0 | warning |
| vote_distribution 与原 votes 不一致 | 重算对比 | warning |
| consensus_facts 超过 inventory 总数 | 不可能情况 | error，重试 |
| source_type 与水印矛盾 | 不一致 | warning |
| watermark_claim_mismatch flag 比例 > 50% | 异常高 | warning |

#### 第 3 层: fund_manager Audit（Pass 0.5）

见 5.5。

---

## 六、S2 详细设计

### 6.1 S2 子阶段切分

| 子阶段 | 工程量 | 累计 | 核心交付 |
|---|---|---|---|
| S2.1 召回层基础 + 软 schema 核心 | 5 周 | 5 周 | Query Classification + 召回 + 软 schema A/B/C |
| S2.2 投研深度 + 水印 + 复述 + 分轮可见性 | 3 周 | 8 周 | 智堡 MCP + D + E + F 类规则 |
| **S2.3 fund_manager + Audit Pass + 决策日志** | **4.5-5 周** | **12.5-13 周** | **DeepSeek 助理 + Audit Pass + Postgres** |

### 6.2 S2.1 详细任务（保留 v3.2）

Week 1-2: A6.1 召回层
Week 3-4: A1 软 schema + 分诊员 A/B/C
Week 5: PR-8c gate 启动 + 端到端联调 + S2.1 Verification Report

### 6.3 S2.2 详细任务（v3.3 重新编排）

**v3.3 调整理由**：v3.2 把 D 类水印硬检查 + 分轮可见性改造塞在 Week 2 一周内,任务密集风险高。v3.3 给每个改动独立验证窗口。

**Week 1: A6.2 智堡 MCP + D 类规则**

```
Day 1-2: MCPClientWrapper 抽象层
Day 3-4: wisburg-mcp-server 集成
         + 调研智堡 MCP tool 全集（含 audit 适用 tool）★ v3.3
Day 5-6: D 类水印硬检查（D1-D6）
Day 7: 智堡注入 common_context + D 类规则联调
```

**Week 2: 分轮可见性改造（独占）**

```
Day 1-2: LangGraph 拓扑改造（bull/bear → round_1/round_2/round_3）
Day 3-4: Prompt 分化
Day 5: EvidenceItem schema 扩展（source_type + cited_in_phase）
Day 6-7: F 类规则（F1-F5）实现 + 联调
```

**Week 3: E 类复述检测 + 整体联调**

```
Day 1-3: E 类复述退化检测
         - E1 字符相似度（全量）
         - E2/E3 LLM 评判（按 role 分级 + 条件触发）
Day 4-5: 端到端联调
Day 6-7: 30 runs 观测期 + S2.2 Verification Report
```

### 6.4 S2.3 详细任务（4.5-5 周，v3.3 修订）

**Week 1-2: DeepSeek 助理 + fund_manager 基础改造**

```
Week 1: DeepSeek 助理（Pass 0）
        - 4 维度 schema
        - Prompt 框架
        - Schema validator + sanity check
        - Fallback 机制
        
Week 2: fund_manager 基础 3-pass 改造
        - 消费 DeepSeek 整理结果 + 原始数据
        - thesis 用 {ref:fX} 占位
        - compliance_block 必填
```

**Week 2.5-3: fund_manager Audit Pass（v3.3 新增）**

```
Day 1-2: Audit Pass 实现
         - 优先级排序逻辑
         - common_context 核对
         - 智堡 MCP 复用（按 claim 搜索）
Day 3: audit_status 字段落地
Day 4-5: Audit Pass Prompt 扩展 + 测试
Day 6: Fallback 机制完整测试
```

**Week 3.5-4: 决策日志持久化**

```
Week 3 末-4 初: Postgres + decision_archive
                - decision_json 全量
                - query_hash / normalized_query
                - model_config_snapshot / price_snapshot

Week 4 末: 历史 list view + 收尾
           - 按时间倒序展示
           - 标的归一化
           - decision 卡片视觉降权
           - S2 整体回归测试
           - S2.3 Verification Report
```

### 6.5 S2 已 lock 的关键决策（v3.3 更新）

| 决策点 | 选择 |
|---|---|
| Phase 2 可见性 | 分轮可见性 |
| Round 2/3 web search | S3 backlog（Tavily/Serper） |
| EvidenceItem 新字段 | source_type 5 个 + cited_in_phase + audit_status |
| 分诊员 F 类规则 | S2.2 实施 |
| **fund_manager Audit Pass** | **S2.3 实施（common_context + 智堡 MCP，3 次/run）** |
| **智堡 MCP audit 调用** | **S2.2 同步调研 tool 全集** |
| **Tavily/Serper** | **仍保持 S3** |

### 6.6 S2 不做

- 多租户权限系统
- 复杂 diff highlight UI
- PDF 报告
- **Tavily/Serper web search**（推到 S3）
- Weighted median
- Hard price validation

---

## 七、Q2 E 类规则按 role 分级（v3.3 锁定）

### 7.1 E1 全量执行

| 规则 | 检测 | 适用 | 频率 |
|---|---|---|---|
| E1 | 字符级相似度 | 全部 role | 每 run 每 report |

### 7.2 E2/E3 按 role 分级 + 条件触发 + 抽样兜底

#### 🔴 role（fund_manager / fundamentals / technical）

100% 全量执行 E2/E3。

#### 🟡🟢 role（其他 6 个 analyst）

```python
def should_run_e2_e3(report, role):
    # 条件触发（必做）
    if report.quality_flags.contains("key_points_high_overlap_with_news"):
        return True
    if retrieved_ratio(report) > 0.8:
        return True
    if len(report.raw) < 2 * total_length(report.key_points):
        return True
    
    # 抽样兜底
    return random.random() < 0.2
```

### 7.3 成本与延迟预估

```
🔴 role: 3 × 2 = 6 次 LLM call
🟡🟢 role: 抽样兜底约 5 × 2 = 10 次 → 实际触发约 2-3 次
单 run E2/E3 总调用: 8-9 次
LLM (deepseek-chat) 成本: ~$0.008-$0.009 / run
并行执行延迟: 6-8s
```

### 7.4 S2.2 观测期数据驱动调整

- 条件触发能抓住 90%+ 复述案例 → 抽样兜底降到 1/10
- 不能 → 提高至 1/3
- E2/E3 误判率 > 20% → 调整 prompt

---

## 八、S2.1 验收口径与 Corner Case（保留 v3.2）

---

## 九、S2.2 验收口径与 Corner Case（v3.4 微调）

保留 v3.2/v3.3 内容,新增:

### 9.1 智堡 MCP audit tool 调研验收（v3.3 新增）

| 项 | 目标 | 级别 |
|---|---|---|
| 智堡 MCP tool 全集已调研 | 100% | ⭐ must |
| "按 claim 搜索"专门 tool 已确认 | 100% | ⭐ must |
| audit 适用 tool 文档化 | 100% | ⭐ must |

### 9.2 内容/格式分离诊断指标（v3.4 新增）

S2.2 召回层 + 软 schema + 水印机制完整上线后,观测以下指标,为 S3 是否做内容/格式分离改造提供数据依据。

**这些是 nice 指标（不阻塞 S2.2 进入 S2.3），用于 S3 backlog 决策。**

| 指标 | 含义 | 级别 |
|---|---|---|
| 软 schema 降级率 | LLM 输出无法直接 Pydantic 验证的比例 | nice |
| Pydantic 验证失败但 raw 文本质量高的比例 | 内容好但格式错的具体证据 | nice |
| Pydantic 验证通过但内容质量差的比例 | 格式好但内容空洞的具体证据 | nice |
| 各 role 软 schema 降级分布 | 哪些 role 更容易格式错 | nice |
| 软 schema 降级 vs 内容质量 cross-tab | 格式错与内容质量是否相关 | nice |

**判定标准**（S3 决策时使用）:
- 软 schema 降级率 > 15% → 内容/格式分离改造收益高
- "内容好格式错"案例占总失败 > 50% → LLM 注意力分散明显
- 否则 → 当前混合输出 + 软 schema 容错足够

---

## 十、S2.3 验收口径与 Corner Case（v3.4 修订）

### 10.1 功能验收

#### DeepSeek 助理

| 项 | 目标 | 级别 |
|---|---|---|
| 输出 schema 严格符合 | 100% | ⭐ must |
| facts_inventory 去重正确性 | > 90% | ⭐ must |
| watermark 链保留完整性 | 100% | ⭐ must |
| Fallback 触发时 opus 能直接消费 | 100% | ⭐ must |
| 助理成功率 | > 90% | ⭐ must |
| 助理输出无散文 | 100% | ⭐ must |

#### fund_manager Audit Pass（v3.3 新增）

| 项 | 目标 | 级别 |
|---|---|---|
| Audit Pass 正确执行 | 100% | ⭐ must |
| 智堡 MCP 配额硬限制（≤ 3/run） | 100% | ⭐ must |
| audit_status 完整记录 | 100% | ⭐ must |
| audit 失败时 fallback 不阻塞 | 100% | ⭐ must |
| 智堡 MCP 不可用时降级 | 100% | ⭐ must |
| thesis 引用 audit_confirmed_mismatch 比例 | < 1% | ⭐ must |
| thesis 引用 audit_partial_support 加限定语 | > 90% | ⭐ must |
| audit 平均延迟 | < 30s | ⭐ must |
| 人工抽查 audit 准确性（30 runs） | > 85% | ⭐ must |

#### fund_manager 改造

| 项 | 目标 | 级别 |
|---|---|---|
| thesis 中 `{ref:fX}` 引用率 | > 50% | ⭐ must |
| opus 引用了不存在 fact_id 比例 | < 2% | ⭐ must |
| 完整溯源链验证通过率 | > 80% | ⭐ must |
| fund_manager 延迟 vs S2.3 前 | 不超过 +10s | ⭐ must |

#### 决策日志持久化（保留 v3.2）

### 10.2 Corner Case 测试清单（全 must）

保留 v3.2 内容,新增:

#### Audit Pass 边界（v3.3 新增）

| 测试 | 预期行为 |
|---|---|
| 智堡 MCP 完全不可用 | audit 降级为"仅 common_context 模式" |
| 智堡 MCP 配额耗尽 | 剩余 fact 仅用 common_context |
| 智堡 MCP 单次超时（>8s） | 跳过该 fact，继续 |
| audit pass 超过 30s | 立即中断，未 audit 标 audit_skipped |
| audit 发现 common_context 内容本身就错 | 标 audit_confirmed_mismatch + 记录 audit_rationale |
| audit 中智堡结果与 common_context 矛盾 | 优先智堡，保留 common_context 引用 |
| fact 没有 mismatch flag 但可疑 | 允许主动 audit |
| 同 fact 多 section 引用 → 只 audit 一次 | ✅ |
| audit pass 完全失败（崩溃） | 所有 fact 标 audit_failed，进入 Pass 1 |
| DeepSeek 助理 fallback 模式下 audit | 跳过 audit pass |

### 10.3 内容/格式分离诊断指标（v3.4 新增）

S2.3 完成后，决策日志全量存档,可基于历史数据做更深入的内容/格式分析。

**这些是 nice 指标（不阻塞 S2.3 完成），用于 S3 backlog 决策。**

| 指标 | 含义 | 级别 |
|---|---|---|
| Phase 1 全 8 role 软 schema 降级率（30+ runs 累计） | 长期趋势 | nice |
| 内容质量人工评估 vs 软 schema 降级率相关性 | 是否独立维度 | nice |
| OBS-FIX-2 / 8 / 10 触发率（召回层引入后） | 内容质量改善程度 | nice |
| DeepSeek 助理失败率（Phase 4 Pass 0） | 单 LLM 多任务的稳定性 | nice |
| fund_manager Pass 0.5 audit 触发率 | 上游内容质量信号 | nice |
| 端到端 thesis 中 `{ref:fX}` 引用率（含 retrieved_from_common_context） | 内容质量稳定性 | nice |

**S3 决策路径**:

```
S2.3 完成后,基于以上数据:

Path A: 数据显示当前架构稳定
├─ 软 schema 降级率 < 10%
├─ OBS-FIX 类问题触发率 < 5%
├─ DeepSeek 助理失败率 < 10%
└─ → 不需要内容/格式分离改造,S3 专注其他工作

Path B: 数据显示注意力分散是瓶颈
├─ 软 schema 降级率 > 15%
├─ "内容好格式错"案例占多数
├─ DeepSeek 助理失败率 > 15%
└─ → S3 启动 Phase 1 内容/格式分离改造（见附录 E）

Path C: 数据混合,部分 role 需要改造
├─ 🔴 role（fund_manager / fundamentals / technical）问题集中
├─ 🟡🟢 role 表现稳定
└─ → S3 仅对 🔴 role 做分离改造（成本可控）
```

---

## 十一、Verification Report 模板（保留 v3.1）

v3.3 新增子章节:

### 稳定性专项验证（v3.3 新增）

```markdown
## 稳定性专项验证

### 单组件失败测试
- [ ] 组件 A 完全失败 → 整 run 仍产出报告
- [ ] ...

### 跨 phase 链式失败测试
- [ ] Phase 0a 部分失败 + Phase 1 部分返工失败 → degraded report
- [ ] Phase 2 单 round 失败 + Phase 4 Pass 0 失败 → degraded report

### Time Budget 验证
- [ ] 单 run P50: ____ s（目标 < 60s）
- [ ] 单 run P95: ____ s（目标 < 90s）
- [ ] 超时 90s 的 run 是否产出 degraded report

### Degraded Run 体验测试
- [ ] degraded report 明确告知用户数据不完整
- [ ] disclaimer 符合合规要求
- [ ] 用户人工评估可用性
```

---

## 十二、Phase 0a 详细设计（保留 v3.1）

---

## 十三、Schema 与质量保证（v3.3 更新）

### 13.1 AnalysisReport（保留 v3.1）

### 13.2 EvidenceItem（v3.3 含 audit_status）

详见 4.4 / 5.4。

### 13.3 软 Schema 4 层降级（保留 v3.1）

### 13.4 分诊员规则总表（A/B/C S2.1 落地 + D/E/F 占位）

**S2.1 范围说明**：本节定义 A/B/C 三类规则（Phase 1.5 质量分诊），供 A1.2 分诊员节点实现。
- E 类（复述退化检测）已在 §七 完整定义，本节不重复
- D 类（数据水印硬检查 D1-D6）延后到 S2.2 A6.2.3 节点
- F 类（分轮可见性 F1-F5）延后到 S2.2 F-vis.4 节点
- **Role 差异化必填集**延后到 S2.2（A 类仅全 role 共享最小集）

#### 13.4.1 A 类：Python 硬规则 / 格式 schema 层

**执行时机**：Phase 1 每个 analyst report 产出后，分诊员之前。纯 Python，不调 LLM。
**失败处理**：reject（标 `needs_rework=True`，触发单次返工）。

| 规则 | 检查 | 逻辑 | 失败 quality_flag |
|---|---|---|---|
| A1 | `headline` 非空且 ≤ 200 字符 | `0 < len(report.headline.strip()) <= 200` | `a1_headline_invalid` |
| A2 | `key_points` 数量 ∈ [3, 5] | `3 <= len(report.key_points) <= 5` | `a2_key_points_count` |
| A3 | `conviction` ∈ 合法枚举值 | `report.conviction in AnalysisReport.__fields__['conviction'].annotation.__args__` | `a3_conviction_invalid` |
| A4 | `raw` 非空且 ≥ 100 字符 | `len(report.raw.strip()) >= 100` | `a4_raw_too_short` |
| A5 | `evidence_log` 字段存在 | `hasattr(report, 'evidence_log') and isinstance(report.evidence_log, list)` | `a5_evidence_log_missing` |
| A6 | 最小必填集 = {headline, key_points, conviction, raw} | A1 + A2 + A3 + A4 联合 | （各规则独立标记） |

**A6 说明**：S2.1 仅检查全 role 共享最小必填集。Role 差异化必填集（如 economist 必须有 `theoretical_framework`、historian 必须有 `analogue_period`）延后到 S2.2，届时在 A6 规则基础上按 role 追加检查项。

```python
def run_a_class(report: AnalysisReport) -> list[str]:
    """返回失败的 quality_flag 列表。空 = 全通过。"""
    flags = []
    if not report.headline.strip() or len(report.headline) > 200:
        flags.append("a1_headline_invalid")
    if not (3 <= len(report.key_points) <= 5):
        flags.append("a2_key_points_count")
    if report.conviction not in VALID_CONVICTIONS:
        flags.append("a3_conviction_invalid")
    if len(report.raw.strip()) < 100:
        flags.append("a4_raw_too_short")
    if not hasattr(report, "evidence_log") or not isinstance(report.evidence_log, list):
        flags.append("a5_evidence_log_missing")
    return flags
```

#### 13.4.2 B 类：Python 软规则 / 跨字段一致性

**执行时机**：A 类全通过后执行。纯 Python，不调 LLM。
**失败处理**：reject（标 `needs_rework=True`），B4 例外（warning，见下）。

| 规则 | 检查 | 逻辑 | 失败处理 |
|---|---|---|---|
| B1 | conviction 强方向时 factors 非空 | conviction ∈ {Strong Overweight, Strong Underweight, Overweight, Underweight} 时 `bullish_factors` 或 `bearish_factors` 至少一边非空 | reject, `b1_conviction_factors_mismatch` |
| B2 | directional_calls 方向与 conviction 不矛盾 | 若 conviction=Overweight/Strong Overweight 且 directional_calls 全是 bearish → 矛盾；反之亦然 | reject, `b2_direction_contradiction` |
| B3 | macro/strategy role 必须有 scenarios | `role in ("political_analyst", "economist", "geopolitical") and len(report.scenarios) == 0` → fail | reject, `b3_scenarios_missing` |
| B4 | report 引用的 `[REF#xxx]` 在 common_context 中存在 | 正则提取 raw + key_points 中的 `[REF#X-NNN]`，检查每个是否在 `common_context.references` 的 ref_id 集合中 | **warning**（非 reject），`watermark_missing_refs` |

**B4 特殊处理**：S2.1 阶段水印基础设施刚铺设（A6.1.5），先观察错误模式。B4 失败不触发 `needs_rework`，仅在 quality_flags 中记录 `watermark_missing_refs=[REF#X-007, ...]`。S2.2 D 类规则上线后，B4 可升级为 reject 或归并到 D 类。

```python
def run_b_class(report: AnalysisReport, common_context: CommonContext) -> tuple[list[str], dict]:
    """返回 (reject_flags, warning_flags)。"""
    rejects = []
    warnings = {}

    # B1: conviction 强方向 → factors 非空
    if report.conviction in ("Strong Overweight", "Strong Underweight",
                              "Overweight", "Underweight"):
        if not report.bullish_factors and not report.bearish_factors:
            rejects.append("b1_conviction_factors_mismatch")

    # B2: directional_calls 方向一致性
    if report.directional_calls:
        bearish_count = sum(1 for d in report.directional_calls if "bearish" in d.direction.lower())
        bullish_count = len(report.directional_calls) - bearish_count
        if report.conviction in ("Overweight", "Strong Overweight") and bearish_count > bullish_count:
            rejects.append("b2_direction_contradiction")
        if report.conviction in ("Underweight", "Strong Underweight") and bullish_count > bearish_count:
            rejects.append("b2_direction_contradiction")

    # B3: macro/strategy role → scenarios 必填
    SCENARIO_ROLES = {"political_analyst", "economist", "geopolitical"}
    if report.role in SCENARIO_ROLES and not report.scenarios:
        rejects.append("b3_scenarios_missing")

    # B4: watermark 引用存在性（warning only）
    import re
    ref_pattern = re.compile(r"\[REF#[A-Z]-\d{3}\]")
    all_text = report.raw + " ".join(report.key_points)
    cited_refs = set(ref_pattern.findall(all_text))
    known_refs = {f"[{r.ref_id}]" for r in common_context.references}
    missing = cited_refs - known_refs
    if missing:
        warnings["watermark_missing_refs"] = sorted(missing)

    return rejects, warnings
```

#### 13.4.3 C 类：LLM 软规则 / 内容质量

**执行时机**：A/B 类全通过后执行。单次 LLM 调用 [deepseek-chat]。
**失败处理**：任一 C 规则 fail → reject（标 `needs_rework=True` + `rework_reasons`）。
**LLM 失败处理**：C 类整体跳过，`quality_flag` 标记 `c_check=skipped`（不视为 pass，下游可据此降级）。

| 规则 | 检查维度 | 判定标准 |
|---|---|---|
| C1 | `key_points` 内容质量 | 是否真的是分析要点（有具体论据 / 数据引用 / 因果推理），而非废话堆叠（空泛总结 / 重复 headline / 无信息量） |
| C2 | `bullish/bearish_factors` 言之有物 | 是否包含具体催化剂 / 风险因子 / 数据支撑，而非套话（"存在上行风险" / "市场情绪积极"之类） |
| C3 | `evidence_log` 引用真实性 | evidence_log 中的 claim 是否能在 common_context 数据中找到对应数据点，而非凭空编造 |
| C4 | `headline` 与 `raw` 一致性 | headline 是否准确概括 raw 分析内容的核心观点，而非与正文脱节 |

**LLM Prompt 结构**（单次调用）：

```
你是一个 analyst report 质量检查员。
请对以下 report 执行 4 项检查，每项返回 pass/fail + 理由。

Report:
- role: {role}
- headline: {headline}
- key_points: {key_points}
- bullish_factors: {bullish_factors}
- bearish_factors: {bearish_factors}
- evidence_log: {evidence_log}
- raw (前 500 字): {raw[:500]}

Common Context 数据摘要: {render_watermark_section(common_context.references)}

检查项：
C1: key_points 是否言之有物（有数据/因果推理 vs 废话堆叠）
C2: bullish/bearish_factors 是否有具体催化剂（vs 套话）
C3: evidence_log 引用是否能在 Common Context 中找到对应
C4: headline 是否准确概括 raw 核心观点

返回 JSON:
{"C1": {"status": "pass|fail", "reason": "..."}, "C2": ..., "C3": ..., "C4": ...}
```

**成本预估**：单 report 单次 deepseek-chat 调用 ~$0.001；8 analyst × 1 call = ~$0.008/run；并行执行 ≤ 3s。

#### 13.4.4 执行流与 Fallback 总览

```
Phase 1 analyst report 产出
    ↓
A 类 Python 硬规则（A1-A6）
    ├─ 任一 fail → needs_rework=True, rework_reasons=[flags]
    │              → 单次返工（attempt=2，失败→fallback report）
    └─ 全 pass ↓
B 类 Python 软规则（B1-B3 reject + B4 warning）
    ├─ B1-B3 任一 fail → needs_rework=True
    ├─ B4 fail → warning only（watermark_missing_refs 记录）
    └─ 全 pass ↓
C 类 LLM 软规则（C1-C4 单次调用）
    ├─ LLM 失败 → 跳过 C 类，c_check=skipped
    ├─ 任一 fail → needs_rework=True, rework_reasons=[C_flags]
    └─ 全 pass → report 进入 Phase 2

分诊员整体 Fallback:
    分诊员 LLM 失败 → 跳过 C 类 + E2/E3，仅 A/B/D/E1 生效
    Python 规则异常 → 跳过分诊员，所有 report 直接进 Phase 2
```

#### 13.4.5 S2.2 扩展预留

以下内容 S2.2 落地时填入本节：
- **D 类（D1-D6）**：数据水印硬检查，A6.2.3 节点实现
- **F 类（F1-F5）**：分轮可见性合规，F-vis.4 节点实现
- **A 类 role 差异化必填集**：按 role 追加 A6 检查项（如 economist → theoretical_framework 必填）

### 13.5 重跑控制（v3.3 扩展）

```python
# Phase 1 analyst 重跑（保留 v3.2）
async def analyst_with_gate(role, state, attempt=1):
    ...

# Phase 2 bull/bear 重跑（v3.3 新增）
async def debate_round_with_gate(role, round_num, state, attempt=1):
    statement = await run_debate_round(role, round_num, state)
    if attempt == 1:
        if has_f_class_violation(statement, round_num):
            return await debate_round_with_gate(role, round_num, state, attempt=2)
    if validation_failed_completely(statement):
        return create_placeholder_statement(role, round_num)
    return statement
```

---

## 十四、Prompt 设计：数据 vs 分析的边界（保留 v3.1）

---

## 十五、合规架构（保留 v3.1）

4 层 + FAA exemption + Per-role 风险等级。

---

## 十六、组件失败完整 Fallback 路径（v3.3 新增核心章节）

### 16.1 Phase 0a 召回层失败

| 失败场景 | Fallback |
|---|---|
| Query Classification LLM 失败 | 默认 single_ticker + regex 兜底提取 ticker |
| Regex 也无法提取 | 退化到 macro_event 模式 |
| 单数据源失败 | 跳过，其他源继续 |
| 所有数据源失败 | fallback common_context（含 query 解析） |
| 智堡 MCP 失败 | research_items = []，flag 标记 |
| 缓存层失败 | 直接访问数据源 |

**保证**：Phase 0a 永不阻塞 Phase 1 启动。

### 16.2 Phase 1 analyst 失败

| 失败场景 | Fallback |
|---|---|
| 单 analyst LLM 失败 | 重试 1 次 |
| 重试仍失败 | fallback report |
| 软 schema 全部降级失败 | full_fallback 模式（raw 兜底） |
| 全 8 analyst 都 fallback | degraded run flag，继续 Phase 2 |

**保证**：Phase 1 永远产出 8 个 AnalysisReport。

### 16.3 Phase 1.5 分诊员失败

| 失败场景 | Fallback |
|---|---|
| 分诊员 LLM 失败 | 跳过 C 类 + E2/E3，仅 A/B/D/E1 生效 |
| Python 规则失败（代码异常） | 跳过分诊员，所有 report 直接进 Phase 2 |
| 单 analyst 重跑失败 | fallback report，不阻塞其他 |

**保证**：分诊员永不阻塞整 run。

### 16.4 Phase 2 bull/bear 辩论失败

| 失败场景 | Fallback |
|---|---|
| 单 Round LLM 失败 | 重试 1 次，仍失败 → placeholder statement |
| LangGraph 拓扑切换失败 | fallback 到非分轮模式 |
| common_context 在 Round 2 之前失效 | Round 2/3 退化为封闭模式 |
| F 类规则重跑后仍失败 | 不阻塞，标记 quality_flag |
| 整轮辩论失败 | placeholder debate log，进入 Phase 3 |

**保证**：Phase 2 永远产出 6 个 debate statement。

### 16.5 Phase 3 投票失败

| 失败场景 | Fallback |
|---|---|
| 单 voter LLM 失败 | 投 DATA_INSUFFICIENT + 默认 execution_plan |
| 全部 voter 失败 | 用 Phase 1 conviction 推断 |
| 中位数计算异常 | 用平均数或 fallback execution_plan |

**保证**：Phase 3 永远产出 10 个 vote。

### 16.6 Phase 4 失败

| 失败场景 | Fallback |
|---|---|
| DeepSeek 助理 LLM 失败 | 重试 1 次 |
| 重试仍失败 / API 完全不可用 | opus 直接消费原始数据 |
| opus 上下文超限 | 按 role 优先级截断（🔴 优先） |
| Audit Pass 总超时 | 已 audit 保留，未 audit 标 audit_skipped |
| 智堡 MCP 不可用 | 降级为"仅 common_context audit 模式" |
| 智堡 MCP 配额满 | 剩余 fact 仅 common_context |
| fund_manager Pass 1-3 任一失败 | 重试 1 次 |
| 重试仍失败 | degraded thesis（仅 outline + execution_plan） |
| compliance_block 缺失 | 强制注入静态 disclaimer |

**保证**：Phase 4 永远产出最终决策报告。

### 16.7 Time Budget 硬上限

```
单 run 总延迟硬上限 = 120s   ← 2026-09-08 由 90s 抬（见 S2 §6.7）

各 phase 预算（参考）:
- Phase 0a 召回: ≤ 15s
- Phase 1 analyst（并行）: ≤ 20s
- Phase 1.5 分诊员: ≤ 8s
- Phase 2 辩论（串行 3 轮）: ≤ 25s
- Phase 3 投票（并行）: ≤ 10s
- Phase 4: ≤ 30s

超过 90s → 立即中断当前 phase,用已有部分结果产出 degraded report
```

### 16.8 Degraded Run 机制

```
触发条件（任一）:
- fallback report 比例 > 50%
- 总延迟 > 90s
- 某 phase 完全失败
- 多个关键组件失败

degraded run 处理:
1. 标记 degraded_run = True
2. 用已有数据产出最终报告
3. 报告开头明确告知:
   "⚠️ 本次分析数据召回 / 模型调用多次失败,结论可信度低。
    建议:重新发起分析 / 简化 query 重试 / 联系支持。"
4. compliance_block 强化
5. 决策日志标记 degraded
```

### 16.9 跨 Phase 链式失败的最终兜底

```
最坏情况:
Phase 0a 部分失败 + Phase 1 多 analyst fallback +
Phase 2 部分 placeholder + Phase 4 DeepSeek + 智堡都挂 +
opus 直接消费也接近超限

最终兜底 emergency_report:
- headline: "Trading Debate 分析降级 - 系统多组件失败"
- 简要 query 描述
- 已 fallback 的 phase 列表
- execution_plan: None
- compliance_block: 标准 disclaimer + 强化失败提示
- 用户能看到一个"系统报告了什么"，而不是 500 错误
- 决策日志记录完整失败链路
```

---

## 十七、Observation Gate 机制（保留 v3.2）

PR-8c 计划 S2.1 freeze 后启动,基于真实召回数据跑观测期。

---

## 十八、观测期指标（v3.3 新增）

### 18.1-18.6 保留 v3.1

### 18.7 DeepSeek 助理指标

| 指标 | 目标 |
|---|---|
| 助理成功率 | > 90% |
| 助理延迟 P95 | < 15s |
| schema 合规率 | 100% |
| facts_inventory 去重正确性 | > 90% |
| Sanity check 触发率 | < 20% |

### 18.8 fund_manager Audit Pass 指标（v3.3 新增）

| 指标 | 目标 |
|---|---|
| Audit Pass 触发率 | 5-30% |
| 智堡 MCP 调用比例 | 30-50% |
| audit_confirmed_mismatch 比例 | < 10% |
| audit_partial_support 比例 | 5-20% |
| audit_passed 比例 | > 60% |
| audit_skipped 比例 | < 10% |
| audit_failed 比例 | < 5% |
| audit 平均延迟（含智堡 MCP）| < 30s |
| 单 run 智堡调用次数（平均）| < 2 |

### 18.9 分轮可见性指标（保留 v3.2）

### 18.10 稳定性指标（v3.3 新增）

| 指标 | 目标 |
|---|---|
| 整 run 崩溃率（500 错误）| < 0.1% |
| degraded run 比例 | < 5% |
| time budget 超限率（>90s）| < 3% |
| 单 phase 完全失败率 | < 1% |
| 跨 phase 链式失败 emergency_report 产出率 | 100% |

### 18.11-18.12 整体性能指标

| 指标 | 目标 |
|---|---|
| 端到端延迟 P50 | < 60s |
| 端到端延迟 P95 | < 90s |
| 总成本（vs S2.3 前）| 下降 50%+ |
| 缓存命中率 | > 60% |

### 18.13 Grade Model 输出观测（v3.4 新增）

§9.2 / §10.3 / §18 中标 `nice` 的"内容质量"类指标，目前默认走人工抽样评估。可引入一个独立的 grade model（LLM-as-judge，与 Phase 1-4 主管线解耦）对决策日志做离线打分，将"内容质量"从主观抽查升级为可观测、可对齐的连续信号。

**定位**

- 只读：消费决策日志 / Verification Report，不回写主管线、不参与 fallback。
- 离线：与 90s time budget 解耦，跑批可慢。
- 旁路：失败不影响主 run 结果，符合"稳定能跑 > 质量"原则（§2）。

**适用观测点**

| 观测项 | 来源 | grade model 输出 |
|---|---|---|
| Phase 1 各 role 输出内容质量 | 决策日志 phase1 outputs | content_quality_score（0-5） |
| "内容好但格式错" / "格式好内容空洞" 分类 | 软 schema 降级 raw 文本 | content_vs_format_label |
| bull / bear thesis 论据强度 | Phase 2 round outputs | argument_strength_score |
| fund_manager thesis 引用质量 | Phase 4 thesis + `{ref:fX}` | citation_grounding_score |
| Round 复述退化判定（E2/E3 兜底） | round 输出对 | restatement_severity（兜底抽样） |
| audit_partial_support 限定语合规 | Phase 4 audit + thesis | hedge_compliance_label |

**实现约束**

- 模型独立于主 run（建议小模型 + 明确 rubric prompt），grade prompt 与被评 role prompt 分仓维护。
- 抽样 + 批跑，不要求 100% 覆盖；优先 OBS-FIX / audit_partial_support / 软 schema 降级样本。
- 输出落库到决策日志旁路表，不污染主 trace；可与 §9.2 / §10.3 / §18.7-18.10 的 `nice` 指标做 cross-tab。
- grade 自身评估：每批人工抽 30 条对齐，grade vs 人工 kappa < 0.6 时调整 rubric，不可作为唯一裁决依据。

**用途**

- 替代 §10.3 "内容质量人工评估"列的全量人工口径，保留人工对齐样本。
- 为 §19.4 S3 backlog 中"Phase 1 内容/格式分离改造"提供数据依据（§9.2 判定标准、附录 E 决策路径）。
- 不进入 PR-8 系列 gate hard-fail；阈值跟 [[feedback_pr8_tiered_gate]] 分层口径走。

---

## 十九、S3 详细设计（v3.3 整合 web search backlog）

### 19.1 S3 定位

10 人付费用户 + 决策监控 + 视觉化 debate。

### 19.2 三条线（保留 v3.1）

### 19.3 隐藏王炸:校准曲线（保留 v3.1）

### 19.4 S3 backlog（v3.3 整合 web search）

#### web search 集成（综合）

S3 阶段 Tavily + Serper 接入,服务两个使用场景:

| 使用场景 | 工具 |
|---|---|
| bull/bear Round 2 主动搜索 | Tavily + Serper |
| fund_manager Audit Pass 增强 | Tavily + Serper（在智堡基础上补强） |

#### bull/bear Round 2 web search tool

| 设计点 | 要求 |
|---|---|
| 调用配额 | bull/bear Round 2 各 ≤ 3 次 |
| Source whitelist | Tier 1 官方源 + Tier 2 主流财经媒体 |
| 结果水印化 | 生成新 watermark（REF#W-xxx） |
| 跨 round 状态 | Round 2 结果在 Round 3 仍可引用，不可新搜 |
| 性能预算 | Round 2 增加延迟 ≤ 30s |
| 失败处理 | search 失败不阻塞,bull/bear 退化到仅 common_context |

#### fund_manager Audit Pass 增强（S3）

| 设计点 | 要求 |
|---|---|
| 在 S2.3 智堡 MCP 基础上扩展 | 新增 Tavily/Serper 作为补充核验源 |
| 调用配额 | 单 run ≤ 5 次（含智堡 + Tavily/Serper）|
| 优先级 | 智堡 → Tavily Tier 1 → Serper |
| Pass 0.5 耗时硬上限 | 仍为 30s |
| 失败处理 | 任一 provider 失败 → 降级到其他 |

#### 其他 S3 backlog

| 项 | 触发条件 |
|---|---|
| advisory 三席激活 | 中文 voice 名册可得 |
| 金融 NER / sentiment 数据集 | web search 进入 facts schema |
| 预打分新闻 API | 免费 web search 信噪比不够 |
| **Phase 1 内容/格式分离改造** | **S2.2/S2.3 观测期数据显示软 schema 降级率高 / OBS-FIX 类问题持续 / 注意力分散明显（见附录 E）** |

### 19.5 S3 不做（保留 v3.1）

---

## 二十、S4 详细设计（保留 v3.1）

每个登录用户拥有自己的 committee 配置——自带 model / API key / Phase 1 prompt overlay。

| PR | 状态 |
|---|---|
| AS-1 安全硬化 | ✅ DONE |
| AS-2 设置存储 + 加密 | ⚪ |
| AS-3 运行时 resolver | ⚪ |
| AS-4 前端 AccountSettingsPage | ⚪ |

---

## 二十一、关键决策与约束（v3.3 更新）

### 21.1 架构哲学决策

| 决策点 | 选择 |
|---|---|
| 产品哲学 | 北极星：装备决策者 |
| **工程稳定性原则** | **稳定能跑 > 质量** |
| 阶段框架 | S1-S4 四阶段 |
| 延展性原则 | 每子阶段为下子阶段提供测试基础 |
| Query 解析 | 5 种类型化 |
| Evidence 真实性 | 数据水印硬检查 |
| 召回数据源策略 | 基础数据 5 直连 + 智堡 MCP 投研深度 |
| 数据源分阶段 | S2.1 免费 → S2.2 智堡 → S3 加 Tavily/Serper |
| Schema 严格程度 | 软 schema |
| 质量保证机制 | 分诊员 + 单次返工 |
| Phase 4 架构 | DeepSeek 助理 + Audit Pass + opus 3-pass |
| DeepSeek 助理失败 fallback | opus 直接消费原始数据 |
| **fund_manager Audit 外部源** | **S2.3:common_context + 智堡 MCP / S3:加 Tavily/Serper** |
| **Audit 失败 fallback** | **智堡失败 → 仅 common_context / 整 audit 失败 → 跳过到 Pass 1** |
| 子阶段完成判定 | Verification Report + Must 100% + Corner case 全 Must |
| fund_manager 黑洞 | Route A facts schema |
| Phase 2 输入边界 | 分轮可见性 |
| Round 2/3 web search | S3 backlog |
| 复述退化 E2/E3 | 🔴 强检测 + 🟡🟢 条件触发 + 抽样兜底（1/5） |
| 持久化 | Postgres |
| MCP 协议整合 | Wrapper 抽象层 |
| OBS-FIX 措辞 | 触发频率大幅下降 |
| 召回成功率指标 | 单源 + 复合分层 |
| PR-8c gate 启动时机 | S2.1 freeze 后 |
| 评级粒度 | 6-tier 含 DATA_INSUFFICIENT |
| 辩论结构 | 3 轮分轮可见性 |
| Voter 聚合 | 中位数（PR-11d） |
| 合规层 | 4 层 + FAA + Per-role 风险等级 |
| EvidenceItem 字段 | source_type 5 个 + cited_in_phase + audit_status |
| **time budget** | **单 run 硬上限 90s + degraded run** |

### 21.2 实施约束（v3.3 新增）

保留 v3.2 1-24 项,新增:

25. **稳定性原则:质量保证机制失败时跳过,不阻塞**
26. **time budget 硬上限单 run 90s,超时 → degraded run**
27. **fund_manager Audit Pass 必须有完整 fallback**
28. **智堡 MCP audit 配额硬限制 ≤ 3 次/run**
29. **degraded run 必须产出最终报告（不可拒绝产出）**
30. **emergency_report 在多组件链式失败时仍可产出**
31. **Tavily/Serper 保持 S3,不提前到 S2.3**

---

## 二十二、路线图全景（v3.3）

```
S1 MVP (95%) ─┐
              │
              ├─→ S2.1 召回层基础 + 软 schema 核心 [5 周]
              │     · Week 1-2: A6.1 召回层
              │     · ★ Week 2 末 freeze 接口
              │     · Week 3-4: A1 软 schema + 分诊员 A/B/C
              │     · Week 5: PR-8c gate 启动 + 联调
              │     · ★ S2.1 Verification Report
              │
              ├─→ S2.2 投研深度 + 水印 + 复述 + 分轮可见性 [3 周]
              │     · Week 1: A6.2 智堡 MCP + D 类规则
              │            （同步调研智堡 audit tool）
              │     · Week 2: 分轮可见性改造（独占）
              │     · Week 3: E 类复述检测 + 联调
              │     · ★ S2.2 Verification Report
              │
              ├─→ S2.3 fund_manager + Audit Pass + 决策日志 [4.5-5 周] ★ v3.3
              │     · Week 1-2: DeepSeek 助理 + fund_manager 基础改造
              │     · Week 2.5-3: fund_manager Audit Pass（v3.3 新增）
              │            - common_context + 智堡 MCP 双重核验
              │     · Week 3.5-4: Postgres + 历史 list view + 收尾
              │     · ★ S2.3 Verification Report
              │     ↓
              │     ✅ S2 完成
              │
              ├─→ S3 多租户 + 监控 + web search 集成 [5-7 周]
              │     ✅ Line A 用户认证子集
              │     ⚪ Line A 数据隔离 + 配额计费
              │     ⚪ Line B 监控 + 通知
              │     ⚪ Tavily/Serper 接入
              │     ⚪ bull/bear Round 2 web search
              │     ⚪ fund_manager Audit web search 增强
              │
              ├─→ S3 前端爆款 UX [4-8 周]
              │
              ├─→ S4 用户自定义委员会 [2-3 周]
              │
              └─→ 校准曲线（持续累积）
```

---

## 二十三、风险点（v3.3）

保留 v3.2 1-19 项,新增:

| # | 风险 | 缓解 |
|---|---|---|
| 20 | time budget 90s 硬上限可能触发过多 degraded run | 观测期数据驱动,如 degraded > 10% → 放宽到 120s |
| 21 | 智堡 MCP audit 可用性低于召回时 | 配额 3 次 + 失败降级 common_context |
| 22 | fund_manager 注意力被 Audit Pass 分散 | Audit Pass 独立优先级,只 audit 关键 fact |
| 23 | S2.3 工期延长 0.5-1 周 | 接受延长,Audit Pass 是 fund_manager 黑洞修复核心 |
| 24 | degraded run 用户体验差 | 明确告知 + 重试建议 + S3 监控告警 |

---

## 二十四、终态边界（北极星）

> **可信、可追溯、组合感知的研究助手——装备决策者,不取代决策者。**

S3 之后触及监管的领域**不规划**。S4 不在禁线内。

---

## 附录 A · 待决问题（v3.3 全部锁定）

### Q1: Phase 2 bull/bear 可见性 ✅ 已确认（v3.2）
分轮可见性方案。

### Q2: E 类规则按 role 分级 ✅ 已确认（v3.3）
E1 全量;E2/E3 🔴 100% + 🟡🟢 条件触发 + 抽样兜底（1/5）。

### Q3: 水印对抗性边界 ✅ 已确认（v3.3）
DeepSeek 初筛 + fund_manager Pass 0.5 audit（common_context + 智堡 MCP）。
Tavily/Serper audit 增强仍在 S3。
audit 边界:不推翻 bull/bear 论点。

### Q4: S2.1 freeze 后并行 S2.2 ✅ 已确认（v3.3）
默认串行;多人开发可并行（限定任务）。

### Q5: DeepSeek 助理质量分诊 ✅ 已确认（v3.3）
3 层:Schema validator + Sanity check + fund_manager Audit。

### Q6: F5 退化警告阈值 ⏸ S2.2 观测期决定

### Q7: Round 2 retrieved_from_common_context 范围 ⏸ S2.2 观测期决定

---

## 附录 B · 部署条件触发的合规 TODO

| 项 | 触发条件 | 估时 |
|---|---|---|
| IP 限制（Nginx）| 公网公开访问前 | 0.5-1 天 |
| PDPA 完整合规审计 | 接受用户注册前 | 1-2 周 |
| 商业化 FAA 合规复核 | 收费功能上线前 | 1-2 周 |
| 中国境内服务限制标注 | 中国境内部署前 | 0.5 天 |
| Query intent classifier 升级 | regex 被绕过 | 1 周 |

---

## 附录 C · TradingAgents 对比借鉴

### 我们超越 TradingAgents 的地方

| 独有能力 | 价值 |
|---|---|
| 6-tier 含 DATA_INSUFFICIENT | 认识论上重要 |
| 3 轮辩论 + 分轮可见性 | 真实辩论认知动态 |
| 8 个 analyst | 覆盖面更广 |
| 历史学家 role | 真实金融决策思维 |
| 10 voter 中位数 | 减少单点偏差 |
| 回响室警示 | 主动防群体思维 |
| 4 层合规 + FAA | 法律保护强 |
| 软 schema + 分诊员 + 水印 + audit | 多层质量保证 |
| Query Classification | 处理多样 query |
| DeepSeek 助理 + Audit Pass + opus | 黑洞解决 + 成本经济 + 终审 |
| **稳定性原则 + degraded run** | **稳定能跑 > 质量** |

---

## 附录 D · 记忆文件同步建议

1. MEMORY.md 主索引
2. **新增 architecture_stability_principle.md** ★ v3.3
3. **新增 architecture_audit_pass.md** ★ v3.3
4. architecture_phase2_round_visibility.md
5. architecture_phase4_deepseek_assistant.md
6. verification_report_template.md
7. architecture_retrieval_layer_v3.md
8. architecture_soft_schema_and_quality_gate_v3.md
9. prompt_design_data_vs_analysis.md
10. tradingagents_comparison.md
11. project_api_connectivity_followup.md
12. **新增 architecture_content_format_separation_decision.md** ★ v3.4

---

## 附录 E · 内容/格式分离的决策与时机（v3.4 新增）

### E.1 问题陈述

当前 v3.3 中,Phase 1 analyst 的 LLM 输出是**内容和格式一次混合产出**:

```
analyst LLM 一次输出:
├─ 内容（分析、推断、判断）
└─ 格式（JSON schema、字段名、conviction Literal、scenarios 结构...）

LLM 注意力同时分配在:
- 做正确的分析
- 符合复杂 JSON schema
```

**已知症状**（OBS-FIX 系列）:
- OBS-FIX-2: scenarios 概率不分化
- OBS-FIX-8: economist evidence_log 跨多 archive 全空
- OBS-FIX-10: as_of pattern mismatch
- 软 schema 降级（格式错导致部分字段失效）

**潜在根因**:LLM 注意力被格式约束分散,内容质量难以突破天花板。

### E.2 v3.3 / v3.4 的现状

| 机制 | 性质 | 是否解决"内容/格式分离" |
|---|---|---|
| 软 schema 4 层降级 | 事后容错（格式失败时不崩） | ❌ 不是分离,是降级 |
| 分诊员 A-F 类规则 | 事后检查 | ❌ 不是分离,是检查 |
| 数据水印 + Prompt 设计 | 事前 prompt 约束 | ❌ 不是分离,仍是混合输出 |
| Phase 4 DeepSeek 助理 | Phase 4 内部分离（整理 + 裁决） | ✅ 是分离,但只在 Phase 4 |
| Structured Output | v3.0 决定暂缓 | ❌ 是格式合规率工具,不是分离 |

**v3.4 现状**:Phase 1 没有内容/格式分离。

### E.3 设计选项

#### 选项 A：维持现状（一次混合输出 + 软 schema 容错）

```
LLM 一次输出 → 软 schema 降级容错 → 分诊员事后检查
```

| 维度 | 评估 |
|---|---|
| 工程复杂度 | 低（v3.3 已实现） |
| 成本 | 中（单 LLM 调用） |
| 延迟 | 中（单调用） |
| 内容质量天花板 | 受 LLM 注意力分散限制 |
| 稳定性 | 高（成熟容错） |

#### 选项 B：S2 改造内容/格式分离（双 LLM 调用）

```
Pass 1: analyst LLM 自由输出内容（散文 / 半结构化）
Pass 2: 格式化助理（deepseek-chat）映射到 schema
```

| 维度 | 评估 |
|---|---|
| 工程复杂度 | 高（每 analyst 加助理 = 8 个） |
| 成本 | 高（调用翻倍） |
| 延迟 | 高（可能超 90s time budget） |
| 内容质量天花板 | 显著提升 |
| 稳定性 | 引入新故障点 |

❌ **违背稳定性原则**,S2 阶段不做。

#### 选项 C：S3 才做（基于 S2 数据决定）

```
S2 保持现状,S2.2/S2.3 观测期收集数据
    ↓
S3 启动时基于真实数据决定:
├─ 数据显示稳定 → 不做
├─ 数据显示分散明显 → 全面改造
└─ 数据混合 → 仅 🔴 role 改造
```

| 维度 | 评估 |
|---|---|
| 工程复杂度 | 低（S2 阶段） |
| 决策依据 | 真实数据,不靠先验判断 |
| 稳定性 | 高（S2 保持稳定） |
| 灵活性 | 高（S3 可针对性改造） |

✅ **v3.4 选择此方案**。

#### 选项 D：S2 用"格式化助理"做分离（类似 Phase 4 DeepSeek 助理）

| 维度 | 评估 |
|---|---|
| 工程复杂度 | 高（8 个并行助理） |
| 与软 schema 关系 | 复杂（重叠？替代？） |
| 与 v3.3 关系 | 与稳定性原则冲突 |

❌ **S2 阶段不做**,但可作为 S3 改造的参考模式。

### E.4 v3.4 决策

```
S2 阶段：维持现状（选项 A）
├─ 理由 1：稳定性原则（稳定能跑 > 质量）
├─ 理由 2：v3.3 刚锁定，工程实施已经够多事
├─ 理由 3：软 schema + 分诊员能 catch 大部分问题
├─ 理由 4：召回层引入后内容质量改善空间未知,先看真实数据
└─ 理由 5：避免引入新复杂度和故障点

S2.2 / S2.3 阶段：收集诊断数据
├─ 软 schema 降级率（按 role 分布）
├─ "内容好格式错"案例比例
├─ "格式好内容空"案例比例
├─ OBS-FIX-2 / 8 / 10 触发率（召回层引入后）
├─ DeepSeek 助理失败率（Phase 4 Pass 0 单 LLM 多任务）
└─ fund_manager Pass 0.5 audit 触发率（上游内容质量信号）

S3 阶段：基于数据决定（选项 C 的延伸）
├─ Path A: 数据稳定 → 不做改造
├─ Path B: 数据显示分散明显 → 全面改造
└─ Path C: 仅 🔴 role 问题集中 → 针对性改造
```

### E.5 S3 改造方案设计（如触发）

如果 S2 观测期数据触发 Path B 或 Path C,S3 启动改造时按以下方案:

#### 借鉴 Phase 4 DeepSeek 助理模式

```
Phase 1 analyst（opus / deepseek 等）= 自由输出内容
    ↓ 内容文本（半结构化）
    ↓
格式化助理（deepseek-chat）= 把内容映射到 schema
    ↓ 完整 AnalysisReport JSON
    ↓
进入软 schema 降级机制（仍保留作为最后一道容错）
```

#### 失败 fallback

```
助理失败 → 重试 1 次
重试仍失败 → fallback 到当前一次混合输出模式
确保 Phase 1 永不崩溃
```

#### 实施范围

| Path | 改造范围 |
|---|---|
| Path B（全面） | 8 个 analyst 全部加助理 |
| Path C（针对性） | 仅 🔴 role：fund_manager / fundamentals / technical |

#### Time Budget 影响

```
当前 Phase 1（并行）: ≤ 20s
改造后 Phase 1（双串行 LLM 调用）: ≤ 35-40s

Time budget 总量 90s → 仍可容纳,但需要其他 phase 优化
```

#### 与软 schema 的关系

**软 schema 不撤掉**:
- 格式化助理也可能失败
- 助理映射出的 schema 也可能部分字段不合规
- 软 schema 仍是最后一道容错

**分诊员规则不变**:
- A-F 类规则继续生效
- 分离改造不影响事后检查机制

### E.6 风险与缓解

| 风险 | 缓解 |
|---|---|
| 改造引入新故障点 | 完整 fallback 到当前模式（重试 + 退回单 LLM） |
| 成本翻倍 | 助理用 deepseek-chat（便宜模型）+ 仅 🔴 role 改造 |
| 延迟超 90s | 数据驱动决策,只在收益明显时做 |
| 与 Phase 4 DeepSeek 助理冲突 | Phase 4 助理负责 facts 整理,Phase 1 助理负责 schema 映射,职责不同 |
| 分诊员规则可能需要调整 | S3 改造时同步评估 D/E 类规则在新架构下的有效性 |

### E.7 决策路径总览

```
┌─────────────────────────────────────────┐
│ v3.4: S2 阶段不做内容/格式分离          │
│ 理由: 稳定性原则                          │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ S2.2 完成: 收集软 schema 降级率等指标   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ S2.3 完成: 决策日志累计 30+ runs        │
│ 评估真实数据                              │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ S3 启动: 基于数据决定                    │
│ ├─ Path A: 不做                          │
│ ├─ Path B: 全面改造（8 role）            │
│ └─ Path C: 仅 🔴 role 改造               │
└─────────────────────────────────────────┘
```

### E.8 与其他设计决策的关系

| 关联设计 | 关系 |
|---|---|
| Phase 4 DeepSeek 助理 | 是 Phase 1 改造的参考模式（如触发） |
| 软 schema 4 层降级 | 改造后仍保留作为最后容错 |
| 分诊员 A-F 类规则 | 不变，继续事后检查 |
| Structured Output（v3.0 决定暂缓） | 与内容/格式分离是两件事,但解决目标有重叠;S3 改造时同步评估 |
| 稳定性原则 | E.4 的 S2 维持现状决策直接源于此原则 |

### E.9 v3.4 实施约束

新增约束（v3.4）:

32. **S2 阶段 Phase 1 不做内容/格式分离改造**
33. **S2.2 / S2.3 必须收集诊断指标，为 S3 决策提供数据**
34. **S3 改造决策必须基于真实数据（30+ runs），不靠先验判断**
35. **如 S3 改造，必须完整 fallback 到当前混合输出模式**

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|---|---|---|
| v1.0 | 2026-05-12 | 初稿（召回 + 智堡 MCP） |
| v2.0 | 2026-05-13 | 六点反馈修订 |
| v3.0 | 2026-05-13 | 整合原 roadmap |
| v3.1 | 2026-05-13 | Phase 4 DeepSeek 助理 + Verification Report |
| v3.2 | 2026-05-13 | Phase 2 分轮可见性 + F 类规则 |
| v3.3 | 2026-05-13 | 稳定性原则 + Q2-Q5 锁定 + fund_manager Audit Pass + time budget 90s + degraded run |
| **v3.4** | **2026-05-13** | **新增附录 E：内容/格式分离的决策与时机 + S2.2/S2.3 加入诊断指标 + S3 backlog 加 Phase 1 改造项 + 数据驱动 S3 决策** |

---

**文档状态**：v3.4 已锁定全部待决问题（Q1-Q5），Q6-Q7 观测期决定，内容/格式分离决策待 S3 数据驱动，可进入工程实施
**最后更新**：2026-05-13
