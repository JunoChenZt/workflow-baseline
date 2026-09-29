# 未验证前提协议（task #8/#9）

> **定位**：当任何事实断言、数字阈值、替代物被当前提使用时，本协议定义**验证要求和
> 违反后的处置**。不是 checklist（那是 brake-self-check），是**识别规则 + 分类 + 动作**。
>
> **来源**：P4.B 返工全程 6 次同模式失败 + 跨节点累积观察（O-A6.1.2-01 / O-A6.1.1-01），
> 合计 7 个 case study。详见 [P4.B 综合复盘 §2](../retro/S2/P4.B_comprehensive_retro_2026-05-25.md)。
>
> **生效范围**：所有 S2+ 节点。本协议是 workflow 补充件，不替代
> [brake-self-check](workflow/05-brake-self-check.md)（Q5 "标准降低"覆盖 deviation 判定）
> 或 [DoD](workflow/06-dod-and-evidence.md)（smoke 覆盖验证动作），而是补上游——
> **在前提进入推理链之前拦截**。

---

## 1. 核心规则

**任何被当前提使用的断言，必须标注验证状态。**

```
[verified: <方法>]   — 已验证（git / grep / doc / test / 人工确认）
[unverified: assumed] — 未验证，当假设用
```

**未验证的前提不能作为**：
- deviation 的理由（"因为 X 不存在所以改做 Y" → X 的存在性必须 verified）
- 阈值的来源（"用 30% 因为旧 doc 写了 30%" → 旧 doc 的 30% 有无推导必须查）
- 等价替代的依据（"用 A 替 B 因为等价" → 等价性必须 verified 或显式标 unverified）

---

## 2. 七类前提 + 对应验证动作

基于 7 个 case study 归纳的分类。每类对应一个识别信号和一个最小验证动作。

### 类型 A：存在性断言（"X 不存在 / X 已删除"）

**case study**：`agent role decision.md` "不存在"——Glob 没匹配带空格文件名，
直接接受"设计真值源丢了"，在此基础上临场补了 5 个 deviation。实际被 PR-2a 删除，
`git log --diff-filter=D` 可恢复。

| 识别信号 | 验证动作 |
|---|---|
| Glob/grep 返回空 + 你准备据此做决策 | `git log --diff-filter=D -- '*关键词*'` 查删除历史 |
| 引用一个"应该存在但找不到"的文件 | `git show <commit>:<path>` 尝试恢复 |

**判定**：验证后仍不存在 → 标 `[verified: git-history-checked, truly absent]`；
可恢复 → 恢复后用恢复版本，不临场重建。

### 类型 B：因果叙事（"Y 是因为 Z 导致的"）

**case study**："`PR-5 砍了` DirectionalCall.conviction"——未读 PR-5 commit 就
接受了"字段被砍"的因果叙事。实际 per-call conviction 从未进入当前权威 schema
（schemas.md 报告级是权威），"是否刻意砍"不可考。

| 识别信号 | 验证动作 |
|---|---|
| 用"X 砍了 / 删了 / 改了 Y"作为推理起点 | 读对应 commit / PR diff，确认动作 + 动机 |
| rationale 不可考（没找到讨论记录 / 原始异议） | 措辞降级为"当前结构如此 + rationale 不可考"，**不捏造因果** |

**判定**：找到 commit + 明确 rationale → `[verified: commit <hash>]`；
不可考 → `[unverified: causal-narrative-unconfirmable]`，不当硬前提。

### 类型 C：数字阈值（"用 N% 作为门槛"）

**case study**：pr-8c-readiness §9 的"漏回应率 > 30% → 加警示"——继承自旧 doc，
**无推导**，假设"会漏"。被 DeepSeek N≤15 **0%** 数据反驳。

| 识别信号 | 验证动作 |
|---|---|
| 用一个数字（30% / k=6 / N≥3）且找不到推导文档 | 问"来源记录在哪"；无推导 = **未验证起点** |
| 数字来自旧 doc 且旧 doc 本身没论证 | 标 `[unverified: inherited-threshold]`，observation 校准 |

**判定**：有推导 → `[verified: doc <path>]`；无推导 → 降级为 observation 起点
（数据驱动校准），**不当硬真值做 if/else 决策**。

### 类型 D：替代等价（"用 A 替 B，结果等价"）

**case study**：DeepSeek 替 opus 冒烟——5/5 合规 / 0/15 漏 / 3/3 D15 主题，
但这是 **deepseek 基准非 opus 基准**。生产 fund_mgr 是 opus。

| 识别信号 | 验证动作 |
|---|---|
| 用 model-A 的测试数据推断 model-B 行为 | 显式标"基准是 A 非 B"，差异本身要监测 |
| 用 proxy 字段替代真字段 | 标 proxy 局限 + 欠覆盖面 |

**判定**：等价性经验证（同输入同输出 N≥k） → `[verified: equivalence-tested]`；
未验证 → `[unverified: substitute]`，**结论不可直接推广到真值**。

### 类型 E：自我调和（"这个解读恰好让矛盾消失"）

**case study**：D1 弱读——B.16.1 "schema 强制"与 B.16.3/4 "warn-only"矛盾。
弱读（"结构化字段非散文 = 合规"）恰好验证既有实现，被用户挡回为动机性偏差。

| 识别信号 | 验证动作 |
|---|---|
| 两份文档矛盾 + 你的解读恰好验证现有工作 | 主动找**反驳**你解读的证据（更晚文档 / 原始讨论） |
| 措辞从强变弱且无新信息 | 问"这次变化是新信息还是调和压力" |

**判定**：找到支撑弱读的独立证据 → `[verified: independent-evidence <ref>]`；
找不到 → 冻结争议，**不在实施中默认采纳倒向既有工作的解读**。

### 类型 F：版本权威（"X 版本的说法是对的"）

**case study**：per-call conviction 是"被砍待补的真值"——实际当前权威 schema
（schemas.md 2026-05-13）就是报告级，per-call 是被取代的旧 spec（agent-role-decision），
恢复 per-call = 往权威结构**加它没有的粒度**，须先反驳当前权威。

| 识别信号 | 验证动作 |
|---|---|
| 恢复的旧文档与当前权威文档冲突 | 认**权威晚版**（按日期 + 单一真值源层级） |
| "补回被砍字段"的表述 | 扫**更晚**的文档看字段是否被显式取代 |

**判定**：旧版确实是权威且未被取代 → `[verified: authoritative-version <path>]`；
已被取代 → 用当前权威，旧版标 `[superseded]`。

### 类型 G：文档内部矛盾（"同一文档 §A 与 §B 冲突"）

**case study**：pr-8c-readiness §2.2（"方向性 + plan 就切"）与 §5（"findings 表明
不应执行才切"）——字面张力，§5 的 findings 限定是必要条件，但 detail 在死链 B.16.4。

| 识别信号 | 验证动作 |
|---|---|
| 同一文档两处描述不一致 | 找**限定条件更强**的那处，确认是否有支撑文档 |
| 限定条件指向死链 / 外部文档 | 恢复或重建外部文档**后**才做实施决策 |

**判定**：找到限定文档且一致 → 按限定版执行；死链 / 矛盾不可解 →
**停下写设计 doc 厘清后再实施**（P4.B process win：hard-block-trigger.md 就是此产物）。

---

## 3. 链路断言回溯

当发现"前提 X 来自另一环的结论 Y"时：

```
X 是否 verified?
  ├─ 否 → 验证 X（按 §2 分类）
  └─ 是 → Y（X 的来源）是否 verified?
              ├─ 否 → 验证 Y（回溯一层）
              └─ 是 → OK，链路可信
```

**P4.B 的链路**：
```
"设计真值源丢了" [unverified: 类型 A]
  → "临场补 deviation" [依赖上一环]
    → "deviation 已文档化 = OK" [类型 E: 自我调和]
      → "cold review 通过" [依赖上一环的框架]
```

每一环都依赖上一环未验证的结论。**链路上任何一环回溯验证，整条链路就会断裂**
——这正是用户 `git log --diff-filter=D` 做到的事。

**操作规则**：当 deviation 的理由引用另一个断言时，回溯到源头确认 verified 状态。
回溯深度 ≤ 3（超过 3 层 = 链路本身有设计问题，停下重审架构）。

---

## 4. 与现有 workflow 的集成点

| workflow 步骤 | 集成方式 |
|---|---|
| [§2.3 pre-flight 5 问](workflow/02-pre-flight.md) | 加第 6 问："本任务依赖的事实前提有哪些？各自验证状态？" |
| [§2.7 brake-self-check Q5](workflow/05-brake-self-check.md) | Q5 "标准降低"扩展：deviation 的理由如果引用未验证前提 = Q5 触发 |
| [§2.8 DoD](workflow/06-dod-and-evidence.md) | DoD step 2 "回归"扩展：检查本节点引入的断言是否标注了验证状态 |
| [§2.10 retro](workflow/07-retro-goal.md) | retro 条件 3 "surprise" 扩展：surprise 的根因是否是未验证前提 |
| cold review | prime 协议候选：reviewer 不看 PR 描述、只给 diff + 设计文档（待验证有效性） |

---

## 5. 7 个 case study 索引

| # | 类型 | 简述 | 来源 |
|---|---|---|---|
| 1 | A 存在性 | `agent role decision.md` "不存在" | P4.B RW-0 |
| 2 | B 因果 | "PR-5 砍了 conviction" | P4.B RW-0 考古 |
| 3 | C 阈值 | 30% 漏回应率无推导 | P4.B cold review → backlog Y |
| 4 | D 替代 | DeepSeek ≠ opus | P4.B 冒烟 → backlog Z |
| 5 | E 调和 | D1 弱读动机性偏差 | P4.B RW-2 → backlog X |
| 6 | F 版本 | per-call conviction "被砍待补" | P4.B RW-0 → backlog W |
| 7 | G 内部矛盾 | §2.2 vs §5 hard_block 触发张力 | P4.B.5 设计 doc |

---

## 6. 维护

- 新 case study 命中已有类型 → 追加到该类型的 case study 列表
- 新 case study 不匹配任何类型 → 新增类型（A-Z 编号续）
- 类型的验证动作证明无效（N≥3 次执行但未拦截）→ 修改验证动作或升级为更强机制
- 本协议是**草案**——至少跑过 2 个节点后再评估是否 promote 到 workflow 正式条款

---

**Generated**: 2026-05-25
**Status**: 草案（待用户审定 + 至少 2 节点实战验证后 promote）
**关联 backlog**: [W](backlog.md#w-pr-8c-设计文档技术债合并条目--大半已被-p4b-返工解决) / [X](backlog.md#x-d1-hard-contract-强读弱读争议元层面冻结) / [Y](backlog.md#y-incomplete-event-真实触发率的跨模型差异监测) / [Z](backlog.md#z-fund_mgr-跨模型opus-vs-deepseek对照验证)
