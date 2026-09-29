# Frontend

`frontend/` 目录，Vite + React + TypeScript + Tailwind + shadcn/ui。

## 入口

- Build：`cd frontend && npm run build`
- Dev：`npm run dev`（Vite dev server）
- Output：`frontend/dist/`（Caddy serve）

## 路径与前缀

- axios `baseURL=/api`（[frontend/src/lib/api.ts](../../frontend/src/lib/api.ts)）
- 实际请求路径：`/api/auth/me` → Caddy 剥 `/api` → 后端 `/auth/me`
- 详见 [api.md](api.md#路径前缀)

## 主要页面 / 组件

- `pages/CommitteePage` — 主分析界面（query 输入、SSE 流式渲染）
- `components/committee/` — `AgentCard` / `PhaseResearch` / `PriceLadder` / `CollapsibleExecutionPlan` 等
- `components/compliance/` — `ComplianceModal` / `ResearchOnlyBadge` / `Footer`（DCL-1）
- `lib/compliance/` — `texts.ts` / `store.ts`（DCL 视觉降权 store）

## SSE 渲染

- `fetch` + `ReadableStream` 解 `text/event-stream`
- 按事件 `type` 分桶：`phase` / `analyst_done` / `debate_turn_chunk` / `vote` / `decision_chunk` / `done` / `error`
- 续写 chunk 累积到对应 turn / decision 文本

## 视觉决策（与 governance/compliance.md 联动）

- 历史 list view **按时间倒序**，不按 conviction 排序（视觉降权，[governance/compliance.md](../governance/compliance.md)）
- bear 色调改 warn（不用红色，避免暗示交易动作）
- `**bold**` markdown 全局渲染（PR-8a frontend pass）

## 国际化

当前只有中文 + 部分英文。无 i18n 抽象层。

## 状态

- account-system frontend 已落（PR #88–#92 + #95）—— 登录、注册、灰度
- conviction 字段渲染从 `confidence: int 1-10` 改为 `conviction: string Literal`（PR-8a / PR #79）

## TODO

- 历史复盘可视化（S3）
- 校准曲线视图（S3）
- 多 portfolio 切换 UI（S4）

### 🟡 PARKED — L3 Schema-driven rendering（2026-05-06 决策）

**触发条件**：PR-8a / PR-8b / PR-8c 全部 merge **且** 各 14d post-merge observation 通过 → schema 稳定 → 才开 frontend 适配 PR。截至 2026-05-14，PR-8a / 8b 已 merge，8c 待落。

**Guardrail**（北极星 + spec 一致性）：**不为"前端方便"反向改 schema / prompt / runner**。前端始终消费 backend 给的字段；如发现字段不够好，走 spec discussion 升级 schema，**不在 frontend 临时 adapter 兜底**。

**当前问题**（2026-05-06 visual audit 发现）：

1. **Markdown 不渲染** —— `PhaseDebate.tsx`（Bubble）+ `DecisionCard.tsx`（thesis_sections）用 `<p whitespace-pre-wrap>{text}</p>` 直出 LLM 输出，导致 `**bold**` / list / blockquote 字面显示
2. **信息密度失衡** —— debate Bubble 与 thesis_section 默认全文展开（每段可达千字），缺"看提纲再决定深读"机制
3. **Research 阶段反向砍光** —— `AgentCard.tsx` 用 `line-clamp-3 + key_points.slice(0, 3)` 把 report 砍光，PR-5 加性 19 字段（`evidence_log` / `cross_check_concerns` / `directional_calls` / `scenarios` / `crowding_score` / `narrative_phase` / `term_structure` / `marginal_cost` / `theoretical_framework` / `fragile_assumptions` / `sensitivity_analysis` / ...）**完全不可见**

**为什么不做 L1 / L2 半成品**：
- L1（仅 `react-markdown`）只解决字面显示，不动密度问题
- L2（markdown + 渐进 disclosure）甜点但 schema 未稳；PR-8a `confidence → conviction` breaking 已改前端，再做容易重写
- L3（schema-driven，覆盖所有结构化字段）是终态，但强依赖 PR-8a/8b/8c **最终 schema 形态**（尤其 fundamentals 段 6 + risk_gate_response / hard_block_reason / core_risks）

**L3 应覆盖字段清单**（按 spec 落地顺序）：
- **已落地**（PR-5 加性 + PR-8a/8b）：`evidence_log` / `cross_check_concerns` / `directional_calls` / `scenarios` / `crowding_score` / `narrative_phase` / `contrarian_direction` / `inventory_phase` / `term_structure` / `marginal_cost` / `decision_windows` / `incentive_structure` / `analogue_period` / `similarity_score` / `structural_breaks` / `theoretical_framework` / `fragile_assumptions` / `sensitivity_analysis` / `endogenous_feedback` / `convergence_warning`(FinalDecision) / `conviction` Literal
- **等 PR-8c**：`risk_gate_response` / `hard_block_reason` / `core_risks: list[CoreRisk]`（schema warn-only，无 min_length——"≥3 条" 由 G5 gate 检测，见 [pr-8c-readiness.md §2.1 Implementation deviation](../observations/pr-8c-readiness.md)）/ 4 gate findings

**L3 设计原则建议**（开工时再细化）：
- 单一 markdown renderer 中央化（`react-markdown` + `remark-gfm`），所有 LLM 输出走它
- 默认 collapsed = 标题 + 关键 1-3 行预览；展开看完整 markdown
- 结构化字段按类型分组（chip / accordion / mini-table），不全部铺平
- 视觉降权与北极星一致：scenarios / directional_calls 不做强烈红绿，`invalidation_trigger` 加 outline warn
- AgentCard 维持 preview 形态；详情走侧抽屉 / 模态

**显式不在 P8.1 范围**（北极星红线）：
- ❌ 反向改 schema 让前端少处理（违 guardrail）
- ❌ 引入额外 LLM 在前端"重写"原文为更简洁版本
- ❌ 复杂 diff highlight UI
