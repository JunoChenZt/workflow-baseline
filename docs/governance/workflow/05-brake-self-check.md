# 05 Brake Self-Check — 刹车自检 8 问

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 骨架: [core/04](../../../core/04-brake.md) —— 规则本体以骨架为准，本文件是实例层（含项目参数与历史证据）
> 关联子文档: [docs/governance/workflow/04-goal-execution.md](04-goal-execution.md) / [docs/governance/workflow/06-dod-and-evidence.md](06-dod-and-evidence.md)
> 关联 skill: `brake-self-check`（已 deprecated；详细规则现在本文件 §2.7，设计历史见 [docs/governance/skill-design.md §3.3](../skill-design.md#33-已-deprecated-skill7-个详细设计已迁至-workflow-子文档)）

## 何时读这份文档

[04-goal-execution.md §2.6](04-goal-execution.md#26-goal-达成自验) 自验通过之后、进入 [06-dod-and-evidence.md §2.8](06-dod-and-evidence.md#28-dod-四步) DoD 之前。**默认放行，触发任一即停**。

## 概览

刹车机制 = 事后审查兜底；不是日常审批。8 问对应 8 类边界（生产 / 敏感配置 / 北极星 / 不可逆 / 标准降低 / 历史改写 / 用户成本 / 路线选择）。任一是 / 不确定 → 升级人工。命中后保留代码状态，输出判定，停下等用户裁决（放行 / 改方向 / 停）。

---

## 2.7 刹车自检（8 问）

**时机**：[04-goal-execution.md §2.6](04-goal-execution.md#26-goal-达成自验) 自验通过后，进入 [06-dod-and-evidence.md §2.8](06-dod-and-evidence.md#28-dod-四步) DoD 之前。

**关联 skill**：`brake-self-check`（详见 SKILL.md）

**定位**：刹车机制 = 默认放行，触发任一即停。**不是日常审批**，是"goal 做完了，但跑 8 问发现可能越界"的兜底。**不分档**：[01 §2.2.5.3](01-task-entry.md#2253-每档要做什么不用做什么) 的 S 档省掉了拆解、5 问、5 类 evidence，但 8 问不省 —— 它一屏以内，省的是错误的地方。

### 2.7.1 8 问 checklist

默认自主推进；以下任一答案为"是"或"不确定"，**升级人工确认**：

1. 是否可能影响生产可用性？
2. 是否可能泄露或修改敏感配置？
3. 是否可能改变系统的合规边界或北极星定位？
4. 是否可能造成不可逆数据变化？
5. 是否在降低测试、schema、prompt、fallback 或 archive replay 标准？
6. 是否会改写已完成节点的历史记录？
7. 是否需要用户承担额外费用、外部依赖或安全风险？
8. 是否存在两个以上合理方案，且选择会影响后续路线？

→ **任一是 / 不确定 → 停止执行并提请人工确认**，不要靠"应该没问题"通过。

### 2.7.2 8 问背后的分类（用于自检时定位）

每问对应一类边界，方便 Claude 判断时心里有依据：

| # | 问题类别 | 对应边界 |
|---|---|---|
| 1 | 生产 | 部署 / restart 生产服务 / `.env` 修改 |
| 2 | 敏感配置 | API key / DB 凭据 / repo settings |
| 3 | 北极星 / 合规 | 自动决策路径 / 合规文案 / 视觉降权 |
| 4 | 不可逆 | DB migration / `DROP` / 删除生产数据 |
| 5 | 标准降低 | 跳过 DoD / 改 case / 沉默 skip |
| 6 | 历史改写 | 回滚已 DONE / 改 commit hash 引用 |
| 7 | 用户成本 | 新外部服务 / 新数据源 / 限流 / 隐私 |
| 8 | 路线选择 | ≥ 2 个合理方案 → 用户决定 |

### 2.7.3 命中后的动作

1. **保留当前代码状态**（已 commit 的不回滚）
2. **输出"命中 / 不命中"判定**，命中的问的具体描述
3. **停下等用户裁决**：
   - 放行 → 进 [06-dod-and-evidence.md §2.8](06-dod-and-evidence.md#28-dod-四步) DoD
   - 改方向 → 回 [04-goal-execution.md §2.5](04-goal-execution.md#25-单个-goal-执行) 重做 goal（不重新拆解）
   - 停 → 升级 [CLAUDE.md](../../../CLAUDE.md) 强制红线流程

### 2.7.4 不命中后的动作

直接进入 [06-dod-and-evidence.md §2.8](06-dod-and-evidence.md#28-dod-四步) DoD 四步，不停。

### 2.7.5 8 问详细判定标准

每问的具体判定细则展开：

**Q1 生产可用性**

- 包含：deploy / restart 生产服务、改 `.env` / `.env.prod` / CI secrets / GitHub repo settings、真实 API key / 数据库连接串 / 账号凭据的写盘、展示、迁移或清理、修改仓库可见性（private → public）
- 命中 = 停

**Q2 敏感配置**

- 包含：上述 Q1 同款，但侧重"配置文件本身"而非"服务行为"
- 重叠允许；任一命中即停

**Q3 北极星 / 合规边界**

- 包含：自动下单 / 调仓 / 无人确认决策路径、合规文案 / 风险提示 / 视觉降权逻辑被弱化或删除
- **这是 [CLAUDE.md](../../../CLAUDE.md) 强制红线**，触发即停，无商量

**Q4 不可逆数据**

- 包含：生产 DB migration / stamp / upgrade（`alembic upgrade head` / `alembic stamp` / `alembic downgrade`）、删除、覆盖、回滚生产数据、destructive SQL（`DROP` / `TRUNCATE` / `DELETE without where` / 批量 `UPDATE`）、Alembic 多头 / TimescaleDB / 历史 stamp 对齐
- 命中 = 停

**Q5 标准降低**

- 包含：跳过 DoD 任一步、修改 corner case 以通过测试、降低 schema / prompt / fallback / archive replay 标准、出现 "known issue 先 skip" 但没有登记 deferred item、30-run / 14d gate 需要启动 / 暂停 / 提前结束 / 降级
- **改 case 必须升级人工**：详见 [06-dod-and-evidence.md §2.8.2](06-dod-and-evidence.md#282-corner-case) DoD Corner Case 改 case 门槛
- **隐式 skip 模式识别清单**（命中任一 = Q5 命中，A6.1.1.1 retro 沉淀）：
  1. `if cond: assert ...` 模式 — env / 配置 / 路径不命中时 assert 整段不跑（看到 `if` 包 `assert` 立即扣问 "cond 不命中时 assert 跑不跑？"）
  2. mock 设计让测试看起来 pass 但实际未验证目标行为
  3. `pytest.skip()` / `pytest.xfail()` 未在 PR 描述显式标 deferred
  4. 测试在某些环境（CI / 本地 / 特定 OS）下条件分支跳过 assert
  5. **check / gate / audit 报告只报"N/N pass"结果，不披露执行过程中的异常 / worktree 切换 / 跨目录操作 / cherry-pick 修复 / 任何意外路径**（PR-C-incident R3 沉淀，2026-05-20）—— 隐式抹除了"中间出过问题"的事实，等于以结果掩盖过程的标准降低
- **正确替代**：
  - `assert cond ...`（fail-on-violation，主动断言条件）
  - 用 `monkeypatch` / fixture 主动制造测试需要的条件
  - 显式 `pytest.skip()` 同时在 PR 描述登记 deferred item
  - check / gate 报告**必须包含执行过程描述**（步骤、异常、绕过路径）；若全程顺利亦显式声明"无异常路径"，不让读者推测
- **收窄用户已拍板的承重闸 → 不自行免判，按 §2.7.3 停下上升人工**（2026-08-06 沉淀·#226 review 修复实证）：修 review finding / 自审 finding 时，若改动**缩小了一道用户已拍板的承重闸的覆盖面**（执法范围 / 触发集合 / 判据白名单收窄 / 容差放宽），**即便理由是"原实现会误判"**，也属 Q5 命中。
  - **判据是"这个改动缩小了谁的承重面"，不是"我的理由对不对"** —— 理由成不成立由拍板的人判。
  - 出处：#226 用户拍板"核值转正执法"次日，实现方自审发现量纲坑（`fred/value` 指数级 / `rss/count` 元数据会产生假否定），自行加白名单把执法面收窄到 `{price}` 并直接 commit+push，未走上升。论证本身经用户追认成立，**但它依赖实现方自己下的量纲判断**，属该由用户裁的范围。
  - **与上一条同源**：都是执行体拿一个看似正当的理由（"我到上限了" / "我修的是 bug"）给自己开闸 —— 这正是 Q5 最容易被架空的方式。
- **达到真实技术 / 环境上限 → 不自行免判，按 §2.7.3 停下上升人工**（2026-07-27 用户裁决；A6.1.2.2 asyncio 吞 `CancelledError` + A6.1.3 env 无 key + D1-ROOT 合成回放 + DOC-SYNC 换验证手段 累积）：当你怀疑某目标受限于客观上限、"再努力也过不去"时，**这本身就是 Q5 命中信号**，**不允许**自行判定"这是上限、不算降标准"就放行。正确动作两步：
  1. **用非技术语言写明问题**：撞的是什么墙、因此哪些做不到 / 没验证、诚实的替代或 defer 是什么（写给非技术决策者看，不堆代码符号 / 文件名 / 栈信息）
  2. **上升人工裁决**：由用户判定这是"真上限"还是"变相降标准"—— 不由执行体自证清白
  3. **上升的书面形态 = ⚪ 未验证 + 原因 (b)**（2026-09-29 补）：裁决放行后，这一项在 DoD 三态表里标 ⚪、在交付单第三栏写明「原因 (b) + 用户裁决出处」（[06 §2.8.0](06-dod-and-evidence.md#280-每一步的结果只有三态2026-09-29-立) / [§2.9.5](06-dod-and-evidence.md#295-交付单固定三栏2026-09-29-立)）。**不许**因为用户放行就把它写成 ✅ —— 放行的是"带着未验证交付"，不是"验证通过"。
  - **为什么不自行免判**：Q5 是防"降标准"的闸；让执行体自己宣布"我到上限了所以没问题"，恰恰是这道闸最容易被绕过的方式（用上限叙事掩盖静默 skip / 删 case / 放松断言）。把判断权交回用户，闸才不被自己架空。

**Q6 历史改写**

- 包含：改 `pyproject.toml` 主依赖 major / minor 版本、跨 phase 重构、影响 ≥ 2 个 phase 的代码 / schema / prompt、修改已 DONE 节点的核心契约 / commit hash 引用 / 历史判断、回滚已 PASSED 的 PR
- **已声明冻结状态的判读档触碰类**（2026-06-11 baseline 收紧）：**verdict / 节点 retro / closed backlog 条目** 在被声明"冻结"后的**任何触碰** —— 含导航、链接、反向索引、元数据修补、读法注解、错别字 —— **即 Q6 命中，无"仅改元数据 / 不动正文"例外**。可发现性缺口去**引用方补**（独立 ADDENDUM 档 / 入口侧加链 / watch-list 加 pointer / 反向索引落在引用方），**不动冻结档本体**。依据：fm-spec seg9 ADDENDUM 路径 A 落地实证（2026-06-11，详见 [O-FM-spec-01](../../observations/should_update_observations.md)）。
  - ⚠️ **与 [CLAUDE.md R7](../../../CLAUDE.md) 第②步的接缝（2026-08-06 #226 实证补）**：R7 的二分法是「live 就地改 / 历史加 banner」，**closed 条目会被归进"历史"档，于是"加 banner"看起来合规** —— 实际撞本条。R7 第②步已同步补上冻结档 carve-out；**跑 R7 收口时，第②步分完 live/历史后必须再问一句"这份历史是不是冻结档"**。

**Q7 用户成本 / 外部依赖**

- 包含：引入新外部服务 / 新数据源 / 新 API 调用路径，且涉及费用、隐私、限流或合规风险

**Q8 路线选择**

- 包含：存在 2 个以上合理方案，选择影响后续路线
- 不命中标准：只有 1 个明显方案 / 选择是细节微调不影响路线

### 2.7.6 与 §2.5.3 执行中硬边界的区别

参见 [docs/governance/workflow/04-goal-execution.md §2.5.3](04-goal-execution.md#253-执行中的硬边界即时停)。

| 维度 | §2.5.3 执行中硬边界 | §2.7 goal 后 8 问 |
|---|---|---|
| 时机 | 工具调用前 / step 执行中 | goal 完成 + 自验通过后 |
| 触发 | 即将动手就停 | 已经做完，问"做的对不对" |
| 范围 | 限于 CLAUDE.md 红线 + `<stop_conditions>` | 8 问全部分类 |
| 默认 | 触发即停 | 任一是 / 不确定 → 停 |

§2.5.3 是"事前刹车"，§2.7 是"事后审查"。两者都不可省。

---

## Cross-references

**上游（我引用谁）**：

- [CLAUDE.md](../../../CLAUDE.md) — 强制红线（Q3 等价于红线 + Q1/Q2 重叠）
- [04-goal-execution.md](04-goal-execution.md) — §2.5.3 执行中硬边界（事前刹车） / §2.6 自验通过为进入前置
- [03-decomposition.md](03-decomposition.md) — `<goal>` 的 `<stop_conditions>`

**下游（谁引用我）**：

- [06-dod-and-evidence.md](06-dod-and-evidence.md) — 8 问通过后进 DoD 四步
- [04-goal-execution.md](04-goal-execution.md) — 命中后"改方向"回 §2.5 重做 goal
- `brake-self-check` SKILL — 消费 §2.7.1 8 问 + §2.7.5 详细判定标准
