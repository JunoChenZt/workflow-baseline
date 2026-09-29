# Backlog

> 本文件登记**已识别但延后处理**的事项,按触发条件归类。
>
> **不是任务清单**(那是 [docs/roadmap/S2.md](../roadmap/S2.md)),**不是已知坑**(那是 [docs/governance/workflow/09-known-pitfalls.md](workflow/09-known-pitfalls.md))。
>
> 这里只放:**应该做、但现在做时机不对**的事。
>
> **维护协议**见 §4。

---

## 0. 使用方式

**Claude 何时查看本文件**:

- 子阶段交接的 [verification-report](workflow/10-verification-report.md) 中,触发"backlog 审视"步骤
- 用户主动 `/backlog` 查询
- 任何"我感觉这事之前讨论过要做"的时刻,先查这里再问用户
- **每次 session 启动时**:距离上次查看本文件 > 7 天 → 主动 view + 提示哪些条目触发条件已满足（见 [CLAUDE.md](../../CLAUDE.md) Session 启动检查）

**用户何时查看本文件**:

- 每周第一次启动 session 时手动 view 一下(没有自动提醒机制 — 时间型条目靠用户自己日历兜底)
- 子阶段交接时(配合 verification-report 一起看)
- 触发条件命中时(由 Claude 主动提示)

**本文件的写作风格**:

- 每条 backlog 必须包含**触发条件**(具体可判定,不是"以后"/"将来")
- 每条必须有**强度标记**:🔴 阻塞后续 / 🟡 影响质量 / 🟢 nice-to-have
- 每条必须有**追溯来源**(哪次对话 / 哪个 PR / 哪个 commit 提出的)

---

## Audit Log

### 2026-05-19 — Backlog 计数 audit

**触发**: PR-B 可观测性条目增项需求暴露的 backlog 记账漂移

**发现**:
- §1 包含 2 条已 ✅ 但未移 §3 的尸体条目:
  - L (Hook 配置落地): ✅ 自 `fba4d11` 11:08 (2026-05-19)
  - H (task-entry handoff): ✅ 自 `aad5eca` 14:36 (2026-05-19)
- 历次破例声称数 (P=16, Q=17, R=18) 均未扣减已 ✅ 条目, 导致破例计数失真

**按时间顺序真实计数 (扣除已 ✅ 后的活跃条目数)**:

| 时间 | commit | 事件 | 物理 §1+§2 | L✅ | H✅ | 真实活跃 | 破例? |
|---|---|---|---|---|---|---|---|
| 09:30 | 1df6901 | +N | 15 | ❌ | ❌ | 15 | 踩线 |
| 11:08 | fba4d11 | L → ✅ | 15 | ✅ | ❌ | 14 | — |
| 13:04 | d33e180 | +P | 16 | ✅ | ❌ | **15** | 踩线 (声称破例 1, 实际未超) |
| 14:13 | f7a601a | +Q | 17 | ✅ | ❌ | **16** | **第 1 次真破例** (声称第 2 次) |
| 14:36 | aad5eca | H → ✅ | 17 | ✅ | ✅ | 15 | — |
| 16:52 | 4e442bd | +R | 18 | ✅ | ✅ | **16** | **第 2 次真破例** (声称第 3 次) |

**修正后状态**:
- 真实破例次数: **2 次** (Q + R)
- 声称破例次数: 3 次 (P + Q + R, 其中 P 实际踩线未超)
- 当前真实活跃: 16 条 (§1+§2 物理 18 - L - H)

**§4.4 解读决议 (解读 X — 严格)**:
- audit 修正属 housekeeping, **不释放破例配额**
- 配额释放仅通过 close-by-completion 或 close-by-decision (基于条目自身触发条件, 不为腾配额)
- 拒绝 "先加再清来洗白" 的反模式

**本次 audit 后处理**:
- L 移 §3 (物理归档)
- H 移 §3 (物理归档)
- 破例配额状态: 不变 (仍冻结, 需 close ≥1 条才能新增)
- PR-B 可观测性归宿: 方案 α (PR description, 不进 backlog)

**新规则 (housekeeping)**:
状态变更 (✅ / CLOSED) 必须同步更新 §1 列表位置 (移 §3) 或显式标注 "✅ 但保留位置 (理由)", 二者必居其一。

### 2026-05-25 — Backlog 计数 audit #2 (W/X/Y/Z 入场 + B/D/E 出场)

**触发**: 用户主动 backlog 处理，发现 W/X/Y/Z 四条新增未走 §4.4 破例流程 + §6 迭代历史缺口

**发现**:

1. **W/X/Y/Z 进入无破例登记**:
   - 四条在 P4.B 节点工作分支 (auto/P4.B) 上分批添加:
     - W (PR-8c 设计文档技术债): feature branch ~2026-05-21 (`ccab70d`/`b8c3fbf`)
     - X (D1 hard contract 争议): feature branch 2026-05-21 (`2b781f9`)
     - Y (incomplete event 监测): feature branch 2026-05-25 (`fbf9541`)
     - Z (fund_mgr 跨模型对照): feature branch 2026-05-25 (`24aacde`)
   - 全部在 PR #124 squash merge (`b230d24`, 2026-05-25 10:29) 时 materialized on main
   - **2026-05-19 audit 严格条件 = "不再允许第 3 次真实破例，下一新增前必须先 close ≥1 条"**
   - 进入时 0 条 close，直接加 4 条 = **第 3/4/5/6 次真实破例（协议失守）**

2. **§6 迭代历史缺口**: W/X/Y/Z 进入未在 §6 登记（2026-05-25 补标）

3. **B/D/E 同日 close**: 2026-05-25 用户主动 close B/D/E（S2.1 收口承诺兑现）

**按时间顺序真实计数 (续 2026-05-19 audit)**:

| 时间 | commit | 事件 | 物理 §1+§2 | §3 归档 | 真实活跃 | 破例? |
|---|---|---|---|---|---|---|
| 05-19 audit 完 | — | baseline (L+H 已移 §3) | 16 | 2 | 16 | — |
| 05-25 10:29 | b230d24 | +W/X/Y/Z (PR #124 merge) | 20 | 2 | **20** | **第 3/4/5/6 次真实破例** |
| 05-25 本会话 | — | close B+D+E → §3 | 17 | 5 | **17** | — (close 释放) |
| 05-25 本会话 | — | close J+M → §3 (§2.11 落地) | 15 | 7 | **15** | — (close 释放) |
| 05-25 本会话 | — | close F → §3; reopen B (subagent 验证) | 14 | 8 | **15** (14 §1 + B reopened) | — |
| 05-25 本会话 | — | re-close B (subagent XML PASS) | 14 | 8 | **14** | — |
| 05-26 | — | close A+C (by-decision); V 从 §0.1 转正 §1 | 13 | 10 | **13** | — |

**§1+§2 物理条目明细 (2026-05-26 更新, 13 条)**:

§1 (13): V, K, G, O, I, N, P, Q, R, W, X, Y, Z
§2 (0): —
§3 (10): L, H, B, D, E, J, M, F, A, C

**修正后状态**:
- 真实破例次数: **6 次** (Q + R + W + X + Y + Z)
- 当前真实活跃: **13 条** (< 上限，合规，2 slot 空余；2026-05-26 close A+C + V 转正)
- 配额状态: 仍冻结（破例累计 6 次未清零）

**归因 (W/X/Y/Z 破例)**:
P4.B 节点大返工 (RW-0~RW-5) 密集 surface 设计债。Claude 在 feature branch 工作时逐条追加 backlog 条目，**未执行 §4.4 计数检查**。节点工作分支上 backlog 修改属 CLAUDE.md 自主范围，但 §4.4 上限是内容规则不随分支变化，应在每次新增前 check — 这是协议执行失败，非协议设计缺陷。

**§4.4 协议修复 (本次 audit 决议)**:
- 真实破例 = 6 次，冻结状态不变 (破例累计不清零)
- 本会话 close B+D+E+J+M = 5 条 → 活跃 20→15 = 合规
- J 落地 = workflow §2.11.7 (cold review 推荐 + provenance 排序)；M 落地 = §2.11.8 (achievement_ratio 四档 + defer 扣分强制)
- **新增防护**: feature branch PR merge 前须检查 backlog §4.4 计数（已写入 §2.11.4 动作序列）

### 2026-05-28 — Backlog 计数 audit #3 (AB+AC+AD §0.2 漏标 + S close)

**触发**: 用户主动 backlog 处理时发现 §0.2 一览表停留在 14 行（停在 close ACV 之后），AB（2026-05-28 加）+ AC/AD（2026-05-28 e2e 后用户授权破例加）均未同步 §0.2 + 状态注。

**发现**:

1. **AB §0.2 漏标**: AB 加入时（commit `6617bb5`）未更新 §0.2 表 → 漂移 1 条
2. **AC/AD §0.2 漏标**: 2026-05-28 e2e 报告深度审计后用户授权破例加 AC（🔴）+ AD（🟡）。本次加入 §1 + 写 audit-like 内容，但未同步 §0.2 + §0.1 status 文字 → 漂移 2 条
3. **审计累计**: 共 3 条 §0.2 漂移（与 W/X/Y/Z 2026-05-25 §6 漏标同模式，[[feedback-observation-counter-hygiene]] 反复打）
4. **S 实证 close-able**: S 描述的"retry+AV fallback 绕过 mock"已被 commit `2f18a7d` (PR #132) 精确修了。本会话 15/15 isolated run 全 pass 验证

**按时间顺序真实计数（续 2026-05-26 ACV 后）**:

| 时间 | commit | 事件 | 物理 §1+§2 | §3 归档 | 真实活跃 | 破例? |
|---|---|---|---|---|---|---|
| 05-26 ACV 完 | — | baseline | 13 | 10 | 13 | — |
| 05-27~28 | — | +AA (S2.2-gate rework 盲重试) | 14 | 10 | 14 | — |
| 05-28 | `6617bb5` | +AB (DS-0 timeout) | 15 | 10 | 15 = 上限 | — |
| 05-28 | — | +AC/AD（用户授权破例，e2e 深度审计后） | 17 | 10 | **17 = 上限 + 2** | **第 7-8 次累计破例** |
| 05-28 本会话 | — | close S（§0.1 → §3，不释放 §1 slot） | 17 | 11 | 17 | — |

**修正后状态**:
- 真实破例次数: **8 次累计**（Q + R + W + X + Y + Z + AC + AD）
- 当前真实活跃: **17 条**（超上限 2 条 = AC/AD 授权破例）
- 配额状态: 冻结；承诺 close ≥2 条释放破例
- §0.2 housekeeping: AB/AC/AD 三行已补，count 文字改 14→17

**§4.4 协议未失守（与 W/X/Y/Z 协议失守不同）**:
AC/AD 是**用户显式授权**破例（非未走流程），属合规破例。housekeeping 漂移是 housekeeping 失误（非协议违反），但仍违反 2026-05-19 audit "状态变更必须同步 §0.2"。修复方法 = 本次同步补标 + §2.11.4 动作序列已有 "push 前检查 backlog §4.4 计数"（2026-05-25 audit#2 加），下次新增时强制对照。

**新增防护建议**（observation，不立即落地）: §0.2 + §0.1 status + audit log + §1 物理位置之间的一致性检查目前靠人脑——是否值得做 `lint-backlog.py` 脚本？延后到 N≥3 漂移模式实证（当前 N=3 = W/X/Y/Z §6 + 2026-05-28 §0.2，已达 N≥3，但 link-checker 是 [[A close 时残余风险]] 的同类，**先 observe**）。

### 2026-06-23 — #144 解封后 DEFECT 家族收口（housekeeping，非计数 audit）

**触发**: fund_manager 八步重写 #144 squash 合入 main @ `5885fe7`（2026-06-23 解封），其修复链所属的 DEFECT-* 条目状态全部过期（多条仍写 "未合 main / STALLED / 未 push / 禁解封"）。

**处理**（DEFECT-* 家族**不占 §4.4 lettered 配额**，本次不动破例计数）：5 条标 ✅ CLOSED 2026-06-23 + 保留位置（理由：fm-refactor defect 家族，supersede/follow-up 注记留作追溯）：
- DEFECT-A3-01（已修+hot 验过+合 main）/ DEFECT-R5-01（已修+e2e 双档+合 main）/ DEFECT-R10-02（三步+hot 验收 D seg9 达成+合 main）/ DEFECT-PROSE-GATE-SELF-ABRADE（两反向 bug cherry-pick 并入）/ DEFECT-R10-01（独立 #153 已合·收口确认）。

**spin-out（不随主条 CLOSED，仍 OPEN）**: DEFECT-R10-02 的 **cap-crowding 残留**（cap=15+cross_check-first 挤出收盘/少数派 dissent，"待评估（跑完 D）"现已触发）→ 归 group B actionable，留在 R10-02 条目内的残留观察段。

**同时刚触发待办（group B，本次只登记不动手）**: AO（DS-0 retrieved 溯源剥离，🔴，"seg9 完成后立即"）/ AP（wisburg REF# 子集匹配）/ DEFECT-E2E-RESUME（"跑完 D 排查"）/ AA macro-scenarios 根因（"跑完 D 后排查"）。

---

### 2026-07-16（末更 2026-07-23）— on-deck 看板·一眼看全的入口（supersede 下方 2026-06-25 快照）

> **视图·非新条目**：把散落状态并排成当前入口。触发 = 用户请求全量待办对账 + 必要性评估 + 查漏。**不新增 lettered 条目、不动 §4.4 破例计数**（属 DEFECT/视图类）。下方 2026-06-25/06-26 块 = 旧快照（point-in-time·已 superseded·正文不动）。
>
> **末次全局扫描 = 2026-07-24**（origin/main `953d4f2`）：A–E 段 = 07-16 打码系列收尾对账；F 段 = 07-16~23 落地；**G 段 = 07-23~24 冲刺**（#196–#206·C 表全清）。**⚠️ C 表已全部 ✅/defer——当前无「就能动」的已触发待办**；剩余活口见 G 段尾（AU 窄活🟢 / AW 议题 / AX observe·均未触发）。权威计数 = §0.2（**8 条活跃**·上限内）。
>
> **⚠️ 2026-08-07 前向标注（R7·BH+AU close 收口）——下方 G 段「新活口」里的 AU 口径已 superseded**：G 段尾写的 **AU🟢 rescope（CI backend test 换/加 3.11·改 CI 需用户确认·未触发）** 是 2026-07-24 冲刺当时的 point-in-time 记录，**正文不动**；现状 = **AU ✅ 已 close 2026-08-07**（close-by-completion·`backend` job 加 3.10+3.11 matrix·[#229](https://github.com/JunoChenZt/subagent-for-investment/pull/229) `e60c74f`）。E 段该条已就地 strike。**BH 不在本块任何位置**（BH 立于 2026-08-03，晚于本看板末次更新 07-24），无需收口。
>
> **⚠️ 2026-08-03 前向标注（R7·targeted 收口·非完整扫描）——下方 E 段 / G 段关于 AX 的旧口径全部 superseded**：本块内出现的 **AX🟢 observe（defer-until-data）**（E 段）、**AX🟡 已触发·用户裁决暂不修·继续跑批**（G 段尾）、以及上一行的「AX observe·均未触发」，**均为 point-in-time 记录、正文不改**，但都已被推翻——**AX ✅ CLOSED（2026-08-03）**：代码随 [#220](https://github.com/JunoChenZt/subagent-for-investment/pull/220) `381824a` 合 main（07-31），根因随 Serper 切换消除。同轮 **DEFECT-WEBSEARCH-RELEVANCE ✅ CLOSED**（③ 换搜索后端已于 07-31 完成，D 段那句「③ 仍开·需用户操作」已 superseded·见该条 08-03 标注）。**权威状态一律以 §0.2 表 + 顶部 📌 08-03 banner 为准**（活跃 **12**）。
>
>
> **2026-07-29 收尾增量（docs-audit session·targeted·非完整扫描）**：本轮从「审 docs↔code 对齐」一路做到全仓卫生收口，合 **4 个 PR** —— [#214](https://github.com/JunoChenZt/subagent-for-investment/pull/214) docs↔code 对齐审计（基线 `c7716c0`→`59bfc60`·20 文件·三类漂移：file:line / 增删符号 / pipeline 拓扑）·[#215](https://github.com/JunoChenZt/subagent-for-investment/pull/215) 重绘三张 map（dataflow 全流程 + gate 全景转 mermaid + gate-explorer 现状版 20260729）·[#216](https://github.com/JunoChenZt/subagent-for-investment/pull/216) web_search 默认引擎去 brave（**DEFECT-WEBSEARCH-BRAVE CLOSED**）+ gitignore 段式 e2e 落点·[#217](https://github.com/JunoChenZt/subagent-for-investment/pull/217) 补合层② 相位2 只读设计 pass。**后两个不在原 plan 内**——是「清点本地/远程有什么没推上去」时捞出的：一个躺了 27 天的已验证修复（main 默认 `brave,duckduckgo` 实测 **8/10 返空**），一份**从未进 main 却被两处 handoff 点名当真值源**的设计文档（曾害一个 session 误判「设计待建」白烧一版实现）。**新增 AZ🟢/BA🟡**（§0.2 活跃 8→10·上限内·仍 0 🔴）。**仓库卫生收口**：本地分支 8→1（仅 main）· 远程 12→3+main（各有明文保留依据：`auto/A2` backlog「保留不删」/ `auto/AO-pr2` 已放弃路径唯一副本 / `claude/pr-c-aborted-incident` git-workflow「永久保留作 audit trail」）· stash 8→0 · 未跟踪 243→0（`_checkpoints/` 入 gitignore + 9 文件入库 + 7 个零引用残留删；**其中 `seg5-debate2.checkpoint.CLEANSED.json` 查出是 tracked `seg6-debate3.trace.md:5` 明写「resume 自」的 provenance 承重项、非残留 → 入库不删**）。**教训**：cherry-pick 老 commit 时核了代码没核注释，注释里被推翻的机理原样带进 main → 自审抓出并修（[[cherrypick-verify-comment-claims]]）。
>
> **2026-07-30 增量（docs 整理 session·targeted·非完整扫描）**：docs/ 结构三档整理全落地——**A 档**全仓断链修复（main 直提 `41552a3`·109 条：82 机械改相对路径 + 22 死链降纯文本保行号锚 + 5 目录错位）· **B 档** docs/README 导航重写（`0d6b840`·14 方向目录地图 + 真值源标注 + 「代码数据目录不可动」警示块）· **C 档** [#218](https://github.com/JunoChenZt/subagent-for-investment/pull/218) squash 合 main `bd85992`（plans/ 10 个 handoff 收编 `docs/handoff/`·例外留 2 处有明文依据；reference/ 2 个无扩展名补 `.md`·已核 builders 脚本零引用；`docs/observations/README.md` 七类分类索引——顶层 47 文件**不搬迁**·12 个代码锚定文件标 ⚠️·索引替代分层）。**review 抓实假 0**：复扫脚本经 `git ls-files`（quotepath 转义）读 CJK 文件名失败后静默跳过→「断链 0」系盲区假绿（实为 +22 搬迁新断链、且 07-29 的「109 清零」漏 2 条存量）；修 24 条 + **`scripts/lint_doc_links.py` 入库**（`ls-files -z`·READ FAIL 显式 exit 2 禁静默跳过）·终态真 0（383 md / 3104 链接）·教训入 memory [[feedback-cjk-quotepath-blindness]]。**AZ 链接半闭合**（见 §0.2 该行），env 半仍开·条目保留 🟢。**无新增 lettered 条目·不动 §4.4 破例计数**。
>
> **2026-07-27~29 增量（非完整扫描·targeted）**：① **AK [#211](https://github.com/JunoChenZt/subagent-for-investment/pull/211) 合 main**（07-27·收口前唯一 🔴 消·切出 AY🟡）；② **AI 状态 R7 更正**（07-27·早于 07-14/16 已 close-by-decision·**非等 S3**·原「唯一剩 🔴 = AI」系收口漏网误判）；③ **I/K/R 三条减噪 close**（07-27·I=completion·K/R=decision → §0.2 12→9）；④ **安全卫生收口**（07-27·S2 §9.2）：P1.D.1 ✅[#212](https://github.com/JunoChenZt/subagent-for-investment/pull/212) 密钥扫描 hook / P1.D.2 ✅ `.env.prod` 移出仓库 / GH-PAT ✅ 吊销 / P1.D.3 ⬜ 降级预防性轮换；⑤ **AY ✅ CLOSED**（07-29·[#213](https://github.com/JunoChenZt/subagent-for-investment/pull/213) 中文问美股标的确认交互落地·实证「英伟达」→NVDA·§0.2 9→8）。**当前 8 条活跃全 🟡/🟢·0 🔴·无「就能动」已触发项**（O/P/Q/AG/AP/AU/AW/AX·均等触发 / observe / 条件；**AY 已 done·不再是待推项**）。

**A. 刚做完（mask 系列·2026-07-14~16·**全系列已合 main·2026-07-16 收官**：A1/B1/E1/D1 + C 组 + GATE-B 门重定义 [#187](https://github.com/JunoChenZt/subagent-for-investment/pull/187)→`71da2d9`）**
- **AUDIT-3CHECK** ❌ 彻底砍（非 deferred·[series §4 DEC-C1](../plans/fundmgr-mask-fix-series-2026-07-14.md)）→ audit 永停"来源存在性半项"·安全底线改由 Path B（输出侧验章门）兜。
- **AI**（audit 否定半边）✅ 收口 = MASK.E1 枚举 7→4 删死枚举 [#184](https://github.com/JunoChenZt/subagent-for-investment/pull/184) + AUDIT-3CHECK 砍 —— **非"待 S3"**·已移出 §0.2 活跃。
- **AQ**（砍 raw_confidence 死字段）✅ DONE = MASK.D1 [#185](https://github.com/JunoChenZt/subagent-for-investment/pull/185)。
- **B1** 砍长文 [#183](https://github.com/JunoChenZt/subagent-for-investment/pull/183)（消 ESCAPE 逃逸面）/ **A1** Path B 空跑 GO（0 幻觉·92% 标对）。
- **DEFECT-PROSE-MASK-REF**（冤枉打码 83–90%）✅ **已解决并合 main** [#187](https://github.com/JunoChenZt/subagent-for-investment/pull/187) → `71da2d9`。**⚠️ 修法在收官时被 e2e 实测翻转**：不是 C 组「验章门」那版，而是 **GATE-B 门重定义**——旧门「默认涂无标数字 + 豁免集」实测涂 21 个**全误伤 0 真阳** → 改「只验主动挂标的·不猎无标的」。**实测涂 21→0、正文占位 19→0。**
- **D2** 三 confidence 改名 ❌ 裁不做（docs 写全限定名代替）。

**B. 主线活口（唯一在途·按序）** → ✅ **已全部收口（2026-07-16）**
```
✅ MASK.C + GATE-B 决策书打码收口【已合 main 71da2d9 · #187】
  ├─ ✅ e2e（复用 seg1-8·只重跑 seg9 = 干净 before/after·用户收窄 scope）
  │     → 涂 21→0 · 正文占位 19→0 · quality gate 12/1/0
  │     → A股第二市场 run **✅ 已补跑 PASS（2026-07-20·中际旭创 300308·门行为跨市场一致·[evidence](../observations/mask-gate-b-fix-e2e-Ashare-20260720.md)·commit `ee35061`）**
  ├─ ✅ goal 收口（brake/DoD/retro-goal/retro-node）+ push + PR + squash 合并
  ├─ ✅ 兼验 B1(无长文)/E1(audit 4 值)
  └─ ✅ 股价补丁独立合 [#186](https://github.com/JunoChenZt/subagent-for-investment/pull/186) → `c0e2d8f`
  ★ 方向反转：门从「默认有罪+豁免集」翻成「只验主动认领的」（补丁 treadmill 拔根）
  ★ 新增 G5 AI 誊写核查（gemini·**只降级绝不升级**）→ 取代 backlog AS 机械路
  ★ 沉淀 3 条入 known-pitfalls §3.2（treadmill / 红线按方向划 / provider 已知坑）
```
> 〔**2026-07-16 二次收口**：原此处还挂着「📄 股价取值补丁 = 随 C 组 PR 一并评审 or 单独走小 PR」一段，
> 与上方 `✅ 股价补丁独立合 #186 → c0e2d8f` **自相矛盾**（补丁当日已独立合）→ 删该段。
> **B 段唯一残留 = A 股第二市场 run 未跑**（非阻断·门行为与市场无关·可另约）→ **✅ 2026-07-20 已补跑 PASS·B 段全清**（中际旭创两跑·确定性指标全对齐 NVDA·[evidence](../observations/mask-gate-b-fix-e2e-Ashare-20260720.md)）。〕

**C. 现在就能动（触发已满足·必要性评估）**

> 〔**⚠️ 2026-07-16 二次收口 · GATE-B 后重评**：本表原立论**「扩基本面 = 直接降打码 = 高杠杆」随 GATE-B 失效**
> （门重定义后**涂 21→0**·打码已不是问题）；AS 行原写「值得但重」也与本文件 AS 条目已改的 🔵 defer 矛盾。
> 下表 = 重判后的 live 口径。〕

| 项 | 强度 | 还做? | 判断（GATE-B 后重判） |
|---|---|---|---|
| **N** 依赖版本锁死 | 🟡→✅ | ✅ **DONE（2026-07-23）** | lock 机制 [#197](https://github.com/JunoChenZt/subagent-for-investment/pull/197)（uv.lock）+ fastapi 解钉全收口：测试适配 [#201](https://github.com/JunoChenZt/subagent-for-investment/pull/201) + un-pin [#202](https://github.com/JunoChenZt/subagent-for-investment/pull/202)（`>=0.137,<0.140`·lock 锁 0.139.2·全套件 2696 passed/0 失败）。原"适配 0.137 后 un-pin"顾虑（涉 auth 敏感）经只读调查证伪=纯测试枚举姿势·移出红线 |
| **AL 方向(1)** 治 degraded 噪声 | 🟡→✅ | ✅ **DONE（2026-07-23·[#199](https://github.com/JunoChenZt/subagent-for-investment/pull/199)）** | **改法（用户裁决）**：非"市场感知路由"（会误摘双重上市），而是**价格源冗余组 quality_flag**——两边都问·≥1 报价即不降级·全价格源失败才 degraded。路由做法 [#198](https://github.com/JunoChenZt/subagent-for-investment/pull/198) 曾合入·被 #199 supersede |
| **AL 方向(2)** 扩适配器拉基本面 | 🟡→**部分 ✅** | **Layer 1 ✅ DONE·Layer 2 defer** | **Layer 1 已 shipped**（[#203](https://github.com/JunoChenZt/subagent-for-investment/pull/203)·2026-07-23·扩 tushare `daily_basic`/`fina_indicator` + yfinance `.info` 拉结构化基本面喂 agents·独立 enrich 步骤·Layer-1 焊出 audit/盖章路）。**Layer 2 = 让研报基本面数变 🟢 不盖章**（治「二档盖章」治本半·喂 check①/够 verified）**仍 defer**——碰 audit/DS-0/credibility load-bearing·须独立设计+用户逐节点确认。原「撤销建议优先·随方向(1) 评估」口径已由 Layer-1 落地兑现。见 [gate-routing-redesign 理想图/A 结论](../plans/gate-routing-redesign/gate-explorer-理想图-下一版-20260720.html) + retro [AL-dir2](../retro/S2/AL-dir2_2026-07-23.md) |
| **AT** 现价锚点可用性（取价 retry + fail-fast） | 🟠→✅ | ✅ **DONE（2026-07-23）** | AT.1 tushare retry [#196](https://github.com/JunoChenZt/subagent-for-investment/pull/196) + AT.2 现价拿不到早停（方案 B 优雅早退·[#200](https://github.com/JunoChenZt/subagent-for-investment/pull/200)）全落地。fail-fast 终版 = 用户裁决**优雅早退非崩 run**（R5 拆墙确认）·产「暂不可分析」FinalDecision |
| **AS** web 数字缺干净值源 | 🟠→🔵→**✅ CLOSED** | ✅ **2026-08-05 close-by-supersede**（问法被判定 3 反转：核不动值的出处现在直接拿不到高档；后续归 [endgame](number-provenance-endgame.md) 判据 D2）| 机械路被 **G5 AI 誊写核查取代**；价值被实测推翻（43 数字里 22 有源·**全誊写一致·0 抄错**；被打码的 21 个本就非可溯源事实=日期/序号/区间/处方量·AS 救不了）。~~**重新触发 = G5 日志里 mismatch 真实频繁**（当前实测 0）~~ ⚠️ **该判据 2026-08-04 已证【自锁】、不可再当有效判据用** —— G5 拿到的"来源原文"首行是待核陈述自己 → 对「数字对但锚指向别的实体」这一形态**结构上判不出 mismatch** → 计数永远不会上升。且「机械路太贵」的前提也要分开看：本轮 13 条最高信任事实做**纯数值比对（零 LLM）**，10 条错绑全抓、唯一正确的正确放行、**零误报**。**AS 强度重估待用户裁**，此处只标事实。详本文件 AS 条目 + [DEFECT-ANCHOR-MISBIND](#defect-anchor-misbind-报告里的数字挂着别人的出处而系统因为有出处给了它最高信任🔴2026-08-04-全链-e2e-实证每跑都在发生✅-closed-2026-08-14close-by-completion保留位置) |
| **R10-02** cap-crowding 残留 | 🟢 spin-out | 🔲 评估即可 | 仅当 cross_check 实测涨过 25 才真发生·当前纯监控态·非失效 |

**D. 补入用户列表漏项（"有没有漏的"）**
- **T10/#4** claim/URL 级精确绑定 🔵 挂起（测量驱动·N=2 未触发）——**GATE-B 后更没必要**：#4 原为"治过度打码"，而打码已 21→0（门重定义治好·非 #4 治好）→ **原目标消失**；触发判据（锚漏归因比例高）从未满足。**大概率永不做**·若未来仍要测应量锚漏归因比例而非总打码数。
- **DEFECT-DSML-PARSE** 🟡——止血已合 [#163](https://github.com/JunoChenZt/subagent-for-investment/pull/163)·剩健壮性改进 A/B 待触发。
- ~~**DEFECT-WEBSEARCH-BRAVE** 🟡——env 已绕过·待正式修（默认引擎去 brave）。~~ ✅ **CLOSED 2026-07-29**：默认改 `bing,duckduckgo`（cherry-pick 躺在本地从未推的 `c8572c8`）。复测 N=10 结论不变但**机理已变**——brave 现为「快速静默返 0 条」而非「8s 超时报错」，修前默认实测 8/10 返空。详见条目 banner。
  > ⚠️ **2026-07-30 前向标注（R7·上方 07-29 正文为 point-in-time 记录·不改）**：本条的处置结论「改 `bing,duckduckgo` 成立」**已被 superseded** —— 当时 N=10 复测只量了**非空率**，未量**相关率**。补测后 bing 的返回中 31–58% 与 query 完全无关（详见新条目 **DEFECT-WEBSEARCH-RELEVANCE**）。brave 确实是死的（0/10）这一点不变，但「换 bing」并未达成「让 analyst 拿到 web 结果」的目标。
- **DEFECT-WEBSEARCH-RELEVANCE** ✅ **CLOSED 2026-08-03**（三层处置 ①②③ 全部完成·见下方 08-03 前向标注）〔原 🔴 NEW 2026-07-30〕——bing 返回「非空但内容全错」，且 HTTP 200 + 结果条数正常 + `unresponsive_engines: []` + **零 error log** → analyst 拿到污染资料而系统毫无察觉。同日 A/B（各约 70 次调用）：`bing,ddg` 35% 垃圾 / 17% 有用 vs `brave,ddg` **0% 垃圾** / 15% 有用（bing 边际 = **+1 有用 / +24 垃圾**）；历史 4 次 e2e 归档垃圾率**全 0** → 系 [#216](https://github.com/JunoChenZt/subagent-for-investment/pull/216) 引入的回归。失败 **query 特定且确定性**（同 query 三轮一致）→ 重试无效。根因在仓库外（SearXNG 抓 bing 拿到 SEO 污染结果）。**处置三层**：① 默认回 `brave,duckduckgo`（⚠️ 撞 [`tests/test_web_search.py:687`](../../tests/test_web_search.py) 测试锁）② `_exec_web_search` 加相关性检查，零重叠即返 error 走 `DATA_INSUFFICIENT` 诚实路径（**与选哪个引擎无关**·防未来漂移）③ 换搜索后端（Cloudflare 侧·需用户操作·15–17% 有用率意味八成搜索白费）。完整证据链 + 可复现脚本：[SEARCH-ENGINE-REGRESSION.md](../observations/regression-e2e-20260730/SEARCH-ENGINE-REGRESSION.md)。**DEFECT-\* 族不占 lettered 配额，§0.2 计数不变。**
  > ✅ **2026-07-30 处置：①② DONE·③ 仍开**（分支 `auto/websearch-relevance`·待 PR 合入）。① 默认引擎回 `brave,duckduckgo`（[config.py](../../src/committee/config.py)·测试锁同步改成「`bing` not in / `duckduckgo` in」+ 双维度测量注释·`.env.example` 同步）；② [`_exec_web_search`](../../src/committee/tools/definitions.py) 加相关性守卫 —— 结果集与 query **零词汇重叠** → 整批换成 `{"error": ...}` + 一条**可 grep 的 `log.warning`**（有别于上游的静默失败），分析师走 `DATA_INSUFFICIENT`；kill-switch `COMMITTEE_WEB_SEARCH_RELEVANCE_CHECK=0`。判据刻意宽松（任一条命中即整批放行·只堵「全错」不做质量排序），比对面 = 标题+摘要**不含 url**（bing 的 `ck/a?<base64>` 跳转链会随机撞短 token 造假重叠），query 词剔年份+功能词。⚠️ **已知局限（有意接受）**：**跨语言 query 会误杀**（中文 query + 全英文结果 = 零重叠）→ 后果是「这次搜索没结果」、分析师降级诚实作答不编造 = 方向安全。**真实归档回放验证**（[`validate_relevance_guard.py`](../observations/regression-e2e-20260730/scripts/validate_relevance_guard.py)·6 份归档零网络回放）：脏跑挡住 **17/24 垃圾（71% 召回）**、净跑+四次历史 **误杀 0/88**（守卫不吃真结果·这是最该证的一件事）。**③ 换搜索后端仍未做 = Cloudflare 侧·需用户操作**（15–17% 有用率意味八成搜索白费·换后端可一并解决 AX 的日期缺失）。
  > ✅ **2026-08-03 前向标注（R7·上方 07-30 正文为 point-in-time 记录·不改）：本条 CLOSED —— 三层处置全部完成。**
  > **①② 早已不在分支上**：随 [#220](https://github.com/JunoChenZt/subagent-for-investment/pull/220) squash 合 main `381824a`（2026-07-31）。上方「分支 `auto/websearch-relevance`·待 PR 合入」**已 stale**——该分支远程已不存在，代码在 main。
  > **③ 换搜索后端 = 已完成**（2026-07-31·Serper）：Worker 代码就绪 `fb6226d` + 根路径部署 `b8e4bf0` + 日期归一方案 A `0a1de31`；**实跑证实后端确为 Serper**——seg1/seg2 段式 e2e（`2e7553b`/`d86d3bb`）+ [#221](https://github.com/JunoChenZt/subagent-for-investment/pull/221) 实测「Serper 真返数据 1.5–3.9s」（旧 SearXNG 后端是 75% 空返）。四维评测全过：相关率 25%→**100%** / 垃圾率 **0%** / 空率 75%→**0%** / 带日期率 0%→**62%**（详见 §0.2 BD 条目的 07-31 第三笔 banner）。
  > **连带**：③ 曾预言「换后端可一并解决 AX 的日期缺失」——**已兑现**（带日期率 0%→62%），故 [AX](#ax-ds-0-as_of-str-不收-llm-null--ds_researcher-node-fallback-脆性2026-07-24-aj-fresh-smoke-surface) 同日一并 close。**衍生**：Serper 的三种日期写法 `_normalize_as_of` 不认 → 已另立 **BD**🟢（Worker 侧方案 A 已兜住·本仓侧方案 B 进 backlog）。
- **DEFECT-PROSE-MASK-INDEX** ✅ **已消解**（原 🟢 observe·此处「默认不做」是 #187 漏网的 stale 摘要——与本文件详细条目的 moot 自相矛盾·就地改）：串位隐患随 [MASK.GATE-B-fix](https://github.com/JunoChenZt/subagent-for-investment/compare/main...auto/MASK-GATE-B-fix) `f6b3d0a`（验章门改编辑表·🔴 涂按数字 span 定位）真正消失。⚠️ **注意**：详细条目原写「moot 自 MASK.C3」= 事实错误（C3 删了旧函数，但新门 🔴 路当时仍是 `text.find(value)` 按值遍历）→ 该 PR 内已更正，详见条目。
- **NAMING-EXTKREFS** 🟢——`external_knowledge_refs` 命名误导（名带 external 实为内部 fact 编号）·命名债。
- **AF-residual** 🟢——reports_block raw 注入降按需·AF 尾巴·纯 context 减负。
- **group-B 批量 e2e 冒烟**——攒够 AA/R10-02/E2E-RESUME 改动合批跑一次（deferred ①）。
- **DEFECT-D1-ROOT** ✅ 已实现 [#171](https://github.com/JunoChenZt/subagent-for-investment/pull/171)（用户"已做完"清单未列·归此）。

**E. 挂起/等条件（〔2026-07-24 更新 ②〕原列的 AJ/AH/AN 已 close 移出·见 G 段；**AK 亦已 close**——设计评审已走完并一次做完，见 G 段尾）**：AF🟡(political 空壳·prod 已 gemini 绕过)/~~AG🟡(cache)~~〔**✅ 已 close 2026-08-11**·close-by-completion+剥离：①打标记已做(`82011fb`·默认关)；②③自动前缀缓存路 A/B 实测**收益为零**已放弃(analyst 并行发出·缓存要先后)；剩余大头(fund_mgr 前缀对齐·省 11%)剥离为 [S3 §6.1 COST-FM-PREFIX](../roadmap/S3.md)·**不留 backlog**〕/U🟡(AV fallback 留痕)/P🟡(cache 语义·**触发判据已于 2026-08-06 重定为事件型**·原挂已停跑的 `.3 step6` 数据窗)/~~Q🟡(回问通路)~~〔**✅ 已 close 2026-08-06**·核心半由 AY 交付·剩余搬 [S3 L-C.4](../roadmap/S3.md)·close 主因=触发条件挂死信号〕/R5-03🟡(子域名 eTLD+1)/R5-04⏭️(语义层)/~~AP🟡P2(子集匹配)~~〔**✅ 已 close 2026-08-06**·close-by-**merge**→BI·非 supersede：实质问题(bundle 粗粒度)复核仍在、只是与 BI 同源同触发故并轨〕/AR🟢(文笔)/O🟢(归档)/~~R🟢(RSS)~~/~~I·K🟢(retro 机制)~~〔**✅ R/I/K 均已 close 2026-07-27**·I=governance patch 落地·K+R=close-by-decision〕 + 新：~~AU🟢(CI 测 3.11 窄活·rescope)~~〔**✅ 已 close 2026-08-07**·close-by-completion·窄活已做（`backend` job 加 3.10+3.11 matrix·[#229](https://github.com/JunoChenZt/subagent-for-investment/pull/229) `e60c74f`）〕/~~AW🟡(provenance 前置议题)~~〔**✅ 已 close 2026-08-05**·命题被 #226 判定 3/4 实现覆盖·归 endgame D2〕/AX🟢(as_of null 脆性·observe)。

**F. 07-16~23 落地（point-in-time·当时仅 AT 留活口→**AT 已随 G 段 07-23 收口**）**
- **GATE-ROUTE 打码门四轨路由重构** ✅ 合 main（[#192](https://github.com/JunoChenZt/subagent-for-investment/pull/192) 路由重构 + 价位门控 (b) + check③ 转正 / [#193](https://github.com/JunoChenZt/subagent-for-investment/pull/193) 合并后 Q4 HOLD 豁免修 + GATE-ROUTE 全仓收口）——GATE-B 门重定义的**后续深化**（豁免移出 + 四轨路由 + check③ 转正）。
  - **↳ 带出新 lettered 条目 AT**（现价锚点可用性·🟠·当时已触发未随做）= 本块 C 表已补入·§0.2 已在。〔**→ ✅ 已收口**（AT.1 #196 + AT.2 #200·见 G 段）〕
- **A5-R3 数据不足约束补适用范围** ✅ 合 main（[#194](https://github.com/JunoChenZt/subagent-for-investment/pull/194)·数据不足约束仅对多标的/板块查询成立）——节点已收口·`O-A5-R3-01` 明标「非计划任务·机会性触发·防后人误读为待跑」→ **无待办**。
- **DOC-SYNC + 两轮全仓审计**（[#188](https://github.com/JunoChenZt/subagent-for-investment/pull/188) 38 文件对齐 / [#191](https://github.com/JunoChenZt/subagent-for-investment/pull/191) 二轮校对 / #193 DOC-SYNC 收口）✅——活文档与代码实况已逐项对齐·**无待办**。
- **#189** MASK.GATE-B review 7 真 bug 修 ✅ 合 main·**无待办**。

**G. 07-23~24 冲刺 + AK（C 表全清·§0.2 → **12 条活跃**〔AK close −1、AY 切出 +1·净不变〕）**
- **N** ✅（uv.lock [#197](https://github.com/JunoChenZt/subagent-for-investment/pull/197) + fastapi 测试适配 [#201](https://github.com/JunoChenZt/subagent-for-investment/pull/201) + 解钉 [#202](https://github.com/JunoChenZt/subagent-for-investment/pull/202)·lock 锁 0.139.2·2696 绿）
- **AL** ✅（方向1 = 价格源冗余组 flag [#199](https://github.com/JunoChenZt/subagent-for-investment/pull/199)〔supersede 路由做法 #198〕；方向2 Layer 1 = 结构化基本面 [#203](https://github.com/JunoChenZt/subagent-for-investment/pull/203) + 真 API 核验修两 bug [#204](https://github.com/JunoChenZt/subagent-for-investment/pull/204)；**Layer 2 defer**·入「二档 cluster」）
- **AT** ✅（AT.1 tushare retry [#196](https://github.com/JunoChenZt/subagent-for-investment/pull/196) + AT.2 现价早停门 [#200](https://github.com/JunoChenZt/subagent-for-investment/pull/200)·优雅早退非崩 run）
- **AJ** ✅（DS-0 两块死输出删净 [#206](https://github.com/JunoChenZt/subagent-for-investment/pull/206)·净删 163 行·真 fresh smoke）· **AH** ✅（stale-close·token 追踪早在 #145 实现）· **AN+AV** ✅（[#205](https://github.com/JunoChenZt/subagent-for-investment/pull/205) 顺手清两小债）
- **AK** ✅（**唯一的 🔴 已消**·2026-07-24）：pre-node 设计边界审查 4 问用户拍板 → 三市场本地名录（CN 5531 / HK 2783 / US 13537 条）+ 对账决策表 + 接入 classify（**名录排在 regex 与 web_search 之前**）+ trace↔state 契约 smoke（AK 剩余项 #2）。**e2e A/B 坐实洞真的堵上了**：同样强制 classify 超时，名录 ON → `300308.SZ` + tushare 真实价 1046.51；名录 OFF → 「中际旭创现在适合买么」这个个股问题被降级成 **THEMATIC 去拉 FRED 宏观数据**。**探针在真实名录上验到"记错位"纠正**：LLM 给 `300310.SZ`（真实是宜通世纪·另一家公司）→ 名录纠正回 `300308.SZ`。**美股仍无中文名兜底**（NASDAQ 只有英文名·`us_basic` 中文名全 null）→ 见下方新条目 AY。retro [AK_2026-07-24](../retro/S2/AK_2026-07-24.md)
- **新活口**：**AU**🟢 rescope（CI backend test 换/加 3.11·改 CI 需用户确认·未触发）/ **AW**🟡 议题（provenance 核对能否前置 fund_mgr·DS-0/审计定位重审时议·先读 AUDIT-3CHECK 砍除边界·未触发）/ ~~**AX**🟢 observe（defer-until-data）~~ → **AX🟡 已触发**（2026-07-30 数据点2：两次尝试全灭·`facts_inventory` 空·触发率 14–19%·重试无效·根因=搜索代理丢 `publishedDate` → web 来源 fact 无日期 → 诚实填 null 被 schema 拒 → 连坐作废；**用户裁决暂不修、继续跑批**·详见下方条目表）

**追溯来源**：2026-07-16 用户「开分支·更新所有待办·评估必要性·查漏」；2026-07-23 用户「扫描全局·更新待办」补 F 段；2026-07-24 用户「扫描全局更新待办 + 逐个核 docs/html 对齐代码」补 G 段 + E 段移出已 close 项。

---

### 2026-06-25 — 当前待办依赖快照（on-deck 看板·一眼看全的入口·⚠️ 已 supersede 见上方 2026-07-16 块）· 2026-06-26 更新：🩹 小修已合并 #162

> **这是视图，不是新条目**：下列每项都已是 backlog 正文条目，本块只把散落的依赖关系并排成当前快照，做「一眼看全的入口」。明细以各条目为真值源。**不新增 lettered 条目、不动 §4.4 破例计数**（属 DEFECT/视图类）。

**主线（有依赖·按序推进）**

```
🩹 小修【✅ 已完成·合并 main #162】 = DEFECT-R5-02 #6 收池（拔支柱1，零 LLM；G1 source 锚 + G2 role 收池 + 反作弊 14 测试真堵 + 全量 2254 绿）
  ├─→ PR2 翻 flag（#161）= 🚫 已关闭（2026-06-26·未合·web-verified 路放弃·flag 长期 OFF）
  │      └─→ AO.5 整链 e2e = 已取消（随 PR2 #161 关闭·"web 升 verified"路不再做）
  ├─→ AO 重打标 follow-up（source_type → retrieved_from_web）= ✅ **已并入 T7·已合 main `7070ab6`（#181·2026-07-10）**（活 prompt 补选项·best-effort trace·不喂闸）
  └─→ 小修收池 = 既成代码，建册不重做堵洞（小修≠建册一部分的"返工"，是既成事实）
        ↓
🏛️ 建册【✅ **M1 主体完成 close 2026-07-10**：T1/T2 `5338de2`(#168·旧 A1 地基 `8b7bea6`#164 并入)·**T3 `c450ff2`(#170)**·**T11 `18357ff`(#175)**·**T4 `f3268e6`(#178)**·**T6 `4b16138`(#180)**·**T8 `4a8c10c`**·**T7 `7070ab6`(#181)**·**T9 核实完(锚漏留#4)**·**T5 #165 CLOSED(无 salvage)**·全链 e2e 13/0/0·**T10(#4)剥离为独立挂起条目**】 = 信源册终态(纯治本·三表)
  ← 评估完成 2026-06-26·阶段A 设计 pass 2026-06-29（[重评文档](../plans/provenance-source-registry-reeval-2026-06-26.md)）：量级轻-中(偏轻)；阶段A=治本核心(#1/#2/#3/#8+URL锚持久化)；🚫#5(audit读web)永久砍除(verified后门·北极星红线)；阶段B(#4)暂缓带判据
  ← 三表 `internal_structured` 内源 / `external_websearch` 外源 / `references_appendix` 展示表(T3 期回内源 only→T4 #178 后含外源 wN 分实体·gate 不读=纯展示·外源审计碰不得=红线提醒器)；全程图 dataflow §15.5 / S2 §2.9.5
  ← **T1/T2（外源落地册 external_websearch_ledger + confidence 读固化册）已合 `5338de2`(#168)**；旧 A1 地基（A1.1 派生零件 + load_checkpoint A1.2 + G2/G1 印证读册 A1.3/A1.4）已合 `8b7bea6`(#164) 并入 M1；**T3(撤外源·回内源·废重做 A2#165 CLOSED)✅ 已合 `c450ff2`(#170·2026-07-02)·T11 ✅ `18357ff`(#175)·T4(外源合进表③) ✅ `f3268e6`(#178·2026-07-09)·**T6 方案A 内源半 ✅ 已合 `4b16138`(#180·2026-07-10)**·**T8 ✅ `4a8c10c`**·**T7 ✅ 已合 `7070ab6`(#181)**·**T9 ✅ 核实完·T5 ✅ #165 CLOSED(无 salvage)·M1 主体完成 close 2026-07-10（e2e 13/0/0）·T10(#4)剥离为独立挂起条目**
  ├─→ 语义层（DEFECT-R5-04·拔支柱2·建册铺底座后【单独PR叠上】·不并建册PR）
  └─→ R5-03 子域名归一化 eTLD+1（🟡·【单列】·正交+PSL依赖独立·不随建册）
```

**独立挂着·等外部条件触发**

| 项 | 触发条件 | 归属条目 |
|---|---|---|
| AP 票（wisburg REF#W 子集匹配） | 出现有真实 per-report 引用的 run | **AP. wisburg payload 编号粒度错位**（⏸️ 降级挂起） |
| group-B 批量 e2e 冒烟 | 攒够 AA / R10-02 / E2E-RESUME 改动后合批跑一次 | 2026-06-24 块 deferred ① |
| R10-02 cap：cross_check ≥ 25 残留 | cross_check 真涨过 25、cap-crowding 实际发生 | **DEFECT-R10-02** cap-crowding 残留观察段 |

**锚点**：[DEFECT-R5-02](#defect-r5-02-corroboration-印证池未按-fact-scope--不相干-fact-共享常见整数巧合凑成-verified🔴-阻塞-web-verified-放开) · [DEFECT-R5-03](#defect-r5-03-域名归一化无-etld1--同发行方子域被当两独立源🟡-低暴露往后排) · [DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮)。AO / AP / 信源册建册立项 / DEFECT-R10-02 见本文件下方同名标题条目（锚点从略，避免伪造）。

**追溯来源**：2026-06-25 用户对话「记录待办」——把散在各条目的依赖并排成当前快照；内容 = 既有条目的视图，无新事项。

---

### 2026-06-26 — R5-02 小修合并后状态同步（PR #162·只改状态不写码）

> **前提核实（R6·origin/main tracked）**：PR #162 squash 合 main `3e8dd6f`（小修 G1 fund_mgr source 锚 + G2 DS-0 role 收池 + 反作弊 14 测试 + retro + 双重后台根因闭环 retro）。本块把受影响条目状态对齐到"小修已合并"，逐条注"为什么变 / 为什么不变"。**docs-only、不动 #161 flag、不开新工程。**

**A. 小修（🩹 [DEFECT-R5-02](#defect-r5-02-corroboration-印证池未按-fact-scope--不相干-fact-共享常见整数巧合凑成-verified🔴-阻塞-web-verified-放开)）**：🔄 进行中 → ✅ **已完成·合并 main #162**。两路落地（G1 fund_mgr `_anchor_tool_outputs_by_source` 按 `finding.source` URL 现场锚池 / G2 DS-0 按 `cited_by_roles` 收 `web_provenance`）、反作弊 14 测试真堵（before/after 防假绿 + 镜像不误伤 + 边界 + golden audit_passed 不动）、全量 2254 绿。**为什么变**：代码 + 测试已在 main 主路径，retro 已落（[R5-02-smallfix_2026-06-26](../retro/S2/R5-02-smallfix_2026-06-26.md)）。

**B. PR2 [#161](https://github.com/JunoChenZt/subagent-for-investment/pull/161)（曾拟翻 `WEB_VERIFIED_ENABLED`）**：🚫 **已关闭（2026-06-26·未合·用户裁决放弃 web-verified·flag 长期 OFF）**。**为什么关、非烂尾**：小修虽搬掉技术前置，但翻 flag 本身碰北极星红线（放开网上数字进 verified）；经评估 web 数据最不可信、升 verified 性价比低，且小修 #162 已独立堵支柱1、main 处安全态，无放开紧迫 → 用户拍定关门，非留门。详见下方 AO. 条目 PR2 状态。

**C. 建册（🏛️ **信源册建册** 条目，见本文件同名标题）**：触发=小修堵稳 → **触发条件已到、可启动【重走测绘评估流程】**。**为什么是"启动评估"非"开工"**：做是定的、待评估的只是范围；按已定先重走"测绘届时现状 → 看差距 → 分步评估 → 拍范围"，**不照搬本轮 #1-5+8 / 理想态图**（假设未核）。〔**2026-06-26 已 superseded（point-in-time 记录·正文不动）**：该评估已于当日完成、方向已批准、阶段 A 待开工——见【信源册建册】条目 + [重评文档](../plans/provenance-source-registry-reeval-2026-06-26.md)。〕

**D. e2e 三笔（逐个核覆盖范围，不一笔带过）**：
- **R5-02 PR e2e**（Q1 中际旭创 / Q2 美国加息）：延后待做 → ✅ **已做（PR #162 兜底冒烟证据）**。**边界**：降级态跑（commodity/political DSML fallback）、G1 仅 Q2 13 findings 小样本印证（13 条全 unverified·无一误升）、Q1 0 findings 未走到 G1、**主证据是确定性单测非 e2e**（e2e = 兜底冒烟）。
- **AO.5 整链 e2e**（验 web 升 verified）：🚫 **已取消（随 PR2 #161 关闭·2026-06-26）**。**为什么取消**：AO.5 是验"web 升 verified"那条路的，PR2 关闭、web-verified 放弃后该路不再做 → AO.5 无对象，撤销（非 HOLD）。
- **group-B 批量 e2e 冒烟**（AA/R10-02/E2E-RESUME/AO PR1 攒着的）：本次 Q1/Q2 **仅覆盖到 fund_mgr decision 节点路（G1/G2 所在）**；AA/R10-02/E2E-RESUME/AO PR1 的链路**未专门覆盖**（两跑均 DSML 降级、且非针对那些改动设计）→ **仍挂着、未勾**。

**E. 两个 defer 落位（已打开条目核实际内容，非只看"已登记"）**：
- **URL 锚锚漏 → 建册升级路径**：✅ 在【信源册建册】"升级路径（小修 → 建册·换存取不换原则·垫脚石非绊脚石）"段——明写"建册按**本条数据**登记来源（非按哪次搜索）、分散来源同属一条即一并收入、**不再锚漏**"。内容对、无重复、没漏。
- **语义层 → [DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮)**：✅ 条目内容对——比"带数字的内容"是否同一事 / 靠 AI 判语义 / "先确定后判断"放收池之后 / 控 AI 不确定性（只在数值已匹配基础上做内容确认）。小修收池基础已在 → 其"小修落地后单独排"触发**已可满足**（仍另记、不进当前轮）。

**三档全景（只确认没丢、不处理）**：
- **AP 票**（⏸️ 降级挂起·等有真实 per-report 引用的 run）✅ 在。
- **cross_check ≥ 25 残留**（监控用）✅ 在 **DEFECT-R10-02**（本文件同名标题）cap-crowding 残留观察段；cap 已 #157 升 15→25，残留 = 监控 cross_check 是否涨过 25 再现 crowding。⚠️ 残留观察文本写于 cap=15 时点、属历史快照（15→25 已在 2026-06-24 块记，债未蒸发）。
- **DEFECT-R5-03**（🟡 子域名 eTLD+1）✅ 在；小修（#6 收池）**未触及域名归一化**（out-of-scope），本条现随建册或单列。✅ **触发条件已 un-stale**（原"修 R5-02 时一并评估"在小修合并后 moot → 改"随建册或单列"，本轮已改）。
- **DEFECT-DSML-PARSE**（🆕 已 `ea7adca` 登记·非 R5-02 引入）✅ 在；R5-02 e2e 冒烟发现的 commodity/political v4-pro DSML fallback 已成独立条目。
- **dataflow §15**：✅ **已全节 un-stale（本轮做·~16 处）**——原整节写于小修前（多处"裂缝活着/活洞/未施工"），已逐处对齐"支柱1 已堵（小修 #162 两路收池）·支柱2 语义待 R5-04·建册版待评估"，守"勿读成 R5-02 已修复"纪律（顶部加 banner + 节头 + 版本行留痕）。双阈值"故意解耦"（`_CORROBORATION_N`=3 显示 vs `VERIFIED_MIN_DOMAINS`=2 承重门）本就标 OK、保持。

**不变项 + 为什么不变**：#161 flag 保持 OFF（2026-06-26 更新：#161 已关闭、web-verified 放弃、flag 长期 OFF——非"未授权翻"而是"决定不翻"）；[DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮) 仍 ⏭️ 另记（语义层不进本轮）；AP / R5-03 / DSML 仍挂起（各自外部触发未到）；R10-02 cap-crowding 仍 spin-out OPEN（cross_check 未实测涨过 25）。

---

### 2026-06-25 — R5-02 分步决策 + 小修起手（差距表"做多大"定为分步、不一把梭）

> **⚠️ 2026-06-26 前向 banner（point-in-time 记录·正文不动）**：下文"建册【立项待评估】= 差距表 #1-5+8 / 理想态仍是未核假设"是 06-25 当时口径。**已 superseded**：建册已于 2026-06-26 完成评估（[重评文档](../plans/provenance-source-registry-reeval-2026-06-26.md)）——差距表 #1-8 已逐条重判（#5 永久砍除、#6 已 DONE、#4 降级带判据）、三假设已核出结论、方向已批准·阶段 A 待开工。最新口径以【信源册建册】条目为准。

**测绘三件**（docs-only）: [dataflow §15 外部数据信任/出处全景](../pipeline/dataflow-whole-pipeline.md)（4 类打标全清单 + 出处溯源全程图 + un-stale #144/AO 状态）/ [S2 §2.9 Group B 现状](../roadmap/S2.md)（含 Finding B 生产活洞）/ [信源册 sketch](../plans/provenance-source-registry-sketch.md)（第 0 步核查 + 现状↔理想态差距表）。
**第 0 步一手核查坐实**: 现**无单一贯穿信源真值源**；但**已有结构化源登记册雏形**（`references`+`watermarks`）、且 audit 已读它 —— web 数据不在册、verified 判定不读它。`references_appendix` 是末端展示视图非真值源。
**分步决策（用户拍·别再翻案）**: 🩹 **小修【现在做】**= R5-02 差距表 #6（收池堵洞、止血、走 workflow）/ 🏛️ **建册【立项待评估】**= 差距表 #1-5+8（信源册终态，新立条目）/ ⏭️ **语义层【另记】**= 差距表 #7（拔支柱2，[DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮)）。
**理由**: Finding B 此刻在 fund_mgr 路生产里漏（无 flag 门控），小修最快止血且低风险；建册跨 schema/合并两套机制、理想态仍是未核假设，不与止血绑死；小修 #6 收池是建册一部分、直接继承不返工。

---

### 2026-06-24 — Group B 执行（AA/R10-02 合 + E2E-RESUME PR + AO/AP 一手翻案）

**已落 main**: AA **#156** `558ce5c`（规则移除 macro，scenarios 恢复可选）/ R10-02 **#157** `2f91a33`（dissent cap 15→25）。
**PR 待 merge**: E2E-RESUME **#158**（B = `rejected_roles` 持久 reducer + 保持 report=None 零迁移；C = guide 如实化）。放行门穷尽证 6 个 None 消费端无一靠 None 认 reject → 零迁移（否掉"reject→marker"路线）。
**一手核实翻案（origin/main tracked run 对账）**:
- **AO** 🔄 → **state 级**（非 prompt-only）：web 数据不进 references、域名 [base.py:905](../../src/committee/agents/base.py) 被丢；归 **SESSION 1**。run-D 12 条 inconclusive 主体即 AO（被误标 `common_context` 的 web 数据）。
- **AP** ⏸️ **挂起**：子集匹配证伪（全 run 0 个 partial_support）；残留=bundle 粗粒度、run-D 无样本。
**两笔 deferred**: ① group-B 批量 e2e 冒烟（AA/R10-02/E2E 各自延到一次合批跑）；② R10-02 `cross_check≥25` 残留（closing/minority 保底名额 defer）。
**方法论沉淀（memory）**: ① `source_type` 标签不可信为真实出处（web 被误标 common_context）；② ±N 字符邻接窗口是 ref 绑定**上界假阳性**、承重判断须字段级对账；③ grep 验"已移除"返回 0 是预期成功、别让 exit 在 `&&` 链断后续。

---

### 2026-07-08 — Backlog 计数 audit #4（§0.2 补表暴露超上限 4 + close reconcile）

**触发**: 用户请求完整 backlog triage（距上次 view 2026-06-30 已 8 天 > 7），过程中执行 06-30 押后的 H4——把 §0.2 一览表停留的 15 行（I..AL）补齐到真实活跃状态。

**补表**: §0.2 加入 AM/AN/AO/AP（2026-06-09~06-24 陆续新增、状态变更时未同步 §0.2，违反 2026-05-19 audit "状态变更必须同步 §0.2"）。**计数口径重申（§4.4:1445）**: 只算活跃条目，CLOSED 但物理留 §1 的（fm-refactor 家族 AA/AB/AE/AF/G + 全 DEFECT-*）不计入。据此真实活跃 lettered = I/K/N/O/P/Q/R/W/X/AG/AH/AI/AJ/AK/AL/AM/AN/AO/AP = **19**，超上限 15 共 **4**。`AF-residual`（AF spin-out 尾巴）+ `AO` follow-up + `AUDIT-3CHECK`/`AF`/`AG`（§0.1 pending 草案·letter 复用）不占 lettered 活跃配额。

**close reconcile（用户逐条裁决）**:
- **✅ 已 close（2026-07-08·本次）**:
  - **X** — close-by-decision（D1 hard contract 争议·元层面冻结·RW-2 已按弱读执行·触发"原始 grill 论证被找到"近乎永不发生；争议记录已在 risk-gate-design.md §B.16 有真值源）。
  - **AO** — close-by-completion **主体**（PR1 [#160](https://github.com/JunoChenZt/subagent-for-investment/pull/160) 合 / PR2 [#161](https://github.com/JunoChenZt/subagent-for-investment/pull/161) 关·web-verified 放弃）；展示标签重打标 follow-up 并入 M1 **T7**（#3 source_type 降 trace·显式挂 S2 §2.9.5 M1 状态表·不单独占 slot）。
  - → 活跃 19 − 2 = **17**（仍超上限 2）。
- **✅ AM close-by-completion（2026-07-08·已合 main `416d0bb`·用户拍「给足预算」不 close 而是治）**: 排查坐实——生产 `.env.prod` academic 角色跑 gemini/gpt-4o（非 deepseek·AM 无生产面），但**同机制的截断根**（academic 角色输出被截·gemini thinking 吃 68% 预算/deepseek 长输出）在场；用户"以防降级"选**给足预算**方案。修法 = 新 config `MAX_TOKENS_ACADEMIC`（默认 12288）+ `make_analyst_node` 对 `tier=="advisory"` 传 `max(MAX_TOKENS, …)`（镜像 `MAX_TOKENS_DECIDE` 先例）+ 连带治生产 gemini 截断根。DoD 2443 绿 + mutation + 9 新测 + live 文档收口（api.md/prod-runbook/political-arms）→ **活跃 17→16**。
- **✅ W close-by-decision（2026-07-08·用户拍）**: PR-8c 设计文档技术债——① 债务本体已还清（死链 RW-0 / 闭环 RW-2 / 双档 RW-1 返工全解）；② 剩 3 项休眠有据（G1 per-call 须反驳 schemas.md 权威 / F×T 须 technical key-level 字段 / G4·G7 PARK·真值源在 risk-gate-design.md §B.16）；③ **"对不上=债"前提已失效**——真值源已迁移（as-built=代码+gate-mechanisms-map·design=risk-gate-design），pr-8c 是 2026-05 历史设计基准（冻结在层② EXEC-FLOOR 两轮闸门重写之前），强行对齐历史文档=改写历史（违 R7）。连带给 pr-8c-hard-block-trigger.md 加前向 banner。→ **活跃 16→15·回到上限·reconcile 收口**。
- **🔄 剩 1 条（AJ·不 close·留）**:
  - **AJ** — cross_role_alignment 死输出 + watermark 空中楼阁·O-S2.3-02 N=2 观测计数点·真删涉 LLM 输入面需 e2e·可能随 M1/层② DS-0 工作覆盖 → **留**（有观测价值·非"不必做"）。活跃 15 已回上限、无需再 close。
- **不建议 close（真实待办 / 欠债）**: N（fastapi 欠治本·已触发）/ ~~AI（🔴 等 S3）~~〔**⏭️ 2026-07-14/16：AI 已 close-by-decision**·MASK.E1 删死枚举 + AUDIT-3CHECK 砍·非「等 S3」·正文保留不改〕/ ~~AK（🔴）~~〔**⏭️ 2026-07-24：AK 已 close-by-completion**·正文保留不改〕/ O/P/Q/~~R~~/~~AG(cache)~~〔**⏭️ 2026-08-11：AG 已 close-by-completion + 剥离**·打标记已做·前缀重排 A/B 实测收益为零·剩余归 [S3 §6.1](../roadmap/S3.md)·正文保留不改〕/AH/AL/AN/AP/~~I/K~~〔**⏭️ 2026-07-27：I close-by-completion·K + R close-by-decision**·正文保留不改〕（触发未到但会来·或极小顺带）。

**破例配额**: 补表 + close 均不动破例计数（补表=既有条目 housekeeping 同步·close-by-decision/completion 是"重新评估不必做/已做完"释放活跃 slot·非新增条目）；破例累计 11 不变（audit 修正历史破例数不释放未来配额，§4.4）。

---

## 0.1 Pending additions（配额释放后增项）

> **状态**：超上限。2026-05-28 用户授权破例 +AC/AD → 活跃 **17** = 上限 15 + 破例 **2** 条（累计破例 **8** 次，AC/AD = 第 7-8 次）。配额冻结，承诺启动时 close ≥2 条释放破例。2026-05-28 close S+T（§0.1 → §3, 均 by-completion）—— 不释放 §1 slot（S/T 从未转正进 §1）。
> 以下草案在有空位前**不计入 §1/§2**，仅作记录防遗忘（S/T 已 close）。

| ID | 标题 | 强度 | 来源 |
|---|---|---|---|
| U | PR-B AV fallback 可观测性增强 — AV fallback 命中时缺 structured log + metric | 🟡 | PR-B 方案 α 遗留，PR #121 description 提及但未进 backlog |
| AR | **seg9 prompt 产出质量后续优化** —— 本轮 [fund_mgr 打码修复系列](../plans/fundmgr-mask-fix-series-2026-07-14.md) 聚焦「数字带标验章 + 砍长文」解**打码问题**；seg9 决策 prompt（[DECISION_PROMPT](../../src/committee/prompts/decision/prompts.py)）的**行文质量 / 段落结构 / 引导 / 可读性**仍有优化空间，**不在打码系列 scope 内** → 未来另起评估。 | 🟢 P3（future·优化非缺陷）| 2026-07-14 fund_mgr 打码系列组织时划出 scope 边界：本轮只解打码，prompt 质量优化 defer |
| AQ | **砍 `raw_confidence` 死字段**（DeepSeek 自评 str·不作数）— 删 [decision.py:88](../../src/committee/schemas/decision.py) 字段 + [prompts.py:228/243](../../src/committee/prompts/decision/prompts.py) 让 DeepSeek 产出它的两行指令。**前提**：不做「DeepSeek 自评 vs 代码终裁」校准审计（若要做，改成"接进 trace 激活观测"而非删）。**删前确认**：`VerificationFinding` 的 Pydantic `extra` = ignore（老 archive replay 不崩）。 | ✅ DONE（MASK.D1·2026-07-15·合 main #185） | 2026-07-14 confidence de-mess 调研：`grep` 证 **零读点**（全库 4 处全在写入侧·无 code/测试/trace/门 读它）；spec C2「留痕观测」名不副实（连 trace.md 都不渲染）。同 [AJ](#aj-ds-0-部分-llm-产出无实际效用--cross_role_alignment-死输出--watermark-检查空中楼阁2026-06-02-s23-gate-agent-review✅-closed-2026-07-24-close-by-completion保留位置) 死 LLM 输出模式。**姊妹项**：三个 confidence 撞名改名（便宜刀/贵刀）= **❌ 已裁不做（2026-07-14 用户拍）**——撞名是 docs 表述问题非代码问题·`FinalDecision.confidence`（int 信心分）与 `FindingConfidence`（5 档来源可信度）语义本就不同·docs 写全限定名即清晰·不值 breaking 改名（详 [series §4 D2](../plans/fundmgr-mask-fix-series-2026-07-14.md)）|
| AG | ✅ **CLOSED（相位2b 全线接线·2026-07-09）**——check① 从焊死→真接线上岗：决策节点 `apply_evidence_transcription_flags` 按 num_id 查外源册 number_registry、两级对账（transcription 硬拦 / citation 引用串号软报）；闸门 `any_fact_has_transcription_flag` 只读 fact 戳·不碰表②（守 #5 封顶版）。AG 焊死 → P2b.1 纯函数层 → P2b.2 接线 → 两级区分 → e2e 验证（T11 NVDA seg9 replay：0 硬拦 / 1 citation 软报 f31）。DS-0 prompt 加匹配校验指令。空转隐患彻底消解 | ✅ | PR #176 review finding #4；焊死 07-08·接线 07-09 |
| AF | **political analyst 在 deepseek-v4-pro（生产默认·config.py:166）下落兜底** — 强制情景矩阵复杂 schema 反复 JSON parse 失败 → `DATA_INSUFFICIENT` 兜底模式（evidence=0·key_points=1）。**非测试替代артифакт**：political 生产默认即 deepseek-v4-pro，生产也会命中。advisory 角色兜底不崩主链路但丢该维度输入。查向：prompt/schema 简化 or JSON 修复重试 or 换模型。与已 CLOSED 的 AE（弱模型健壮性）同族但具体到 political·情景矩阵。**2026-07-08 事实缓解**：prod `.env.prod` political 保留 `oc/gemini-2.5-pro`（"换模型"路的现状·gemini 吃得下情景矩阵 schema·绕此洞），代价=贵 5-6x；根治（让 deepseek 也能吃）仍在本条·修好后 political 可切 deepseek（见本文件 §1 条目 `DEFECT-PROD-ADVISORY-MODEL-STALE`）。**修 AF 时一并定代码默认**：[config.py:166](../../src/committee/config.py) political 代码默认仍 `deepseek-v4-pro`（= 无 `.env` override 时 political 会落到它 → 撞 AF·如 fresh dev / 部分测试路径）；`.env.example` 推荐值已改 gemini 但**代码默认没改**（两者可合理不同·default=兜底 / 推荐=prod 调优）。AF 根治后要一并裁：代码默认要不要也避开 AF（改 deepseek-chat / 保持 v4-pro / 其他） | 🟡 | 2026-07-07 NVDA e2e（EXEC-FLOOR 相位2a 节点收口 seg2）实测：political 3 次调用 output 破万 token 仍兜底 |

> **META 观察指针（非 work-item·cross-cutting·resurfacing 钩子）**：执行体"**假设机制生效而不一手验证**"失效模式 **🚨 N=8·升级线（N≥5）已越过**（原 4 例：CI 红 3 天 / classify 静默降级 / env 读错符号名 / 证据未 durable；**2026-08-07 追加 4 例**：backlog 计数检查空过两月 / lint 不认 ✅ 顶格致字形错误靠人眼抓三次 / §6 漏标复发 4 次因脚本入库无人跑 / mutation 锚点与守护 fixture 静默失效）——canonical living doc = [meta-assume-mechanism-without-verify.md](../observations/meta-assume-mechanism-without-verify.md)。**⚠️ 已触发升级但机制化方案尚未产出**（设计任务·需用户排期）；**不得把"记了这一笔"当成"已经升级了"**。与活链接机制化 / CFG-READ 同根。不计 §1/§2 配额。

---

## 0.2 活跃条目一览表

<!-- lint:active-count=9 -->
<!-- lint:active-other-count=13 -->

> **📐 本表的机器可读约定**（`scripts/lint_backlog.py` 依此对账，改表时请一并守）：
> - **活跃 = 该行未加删除线 且「触发状态」格未以 ✅ 起头**。已 close 但保留位置的条目，
>   **✅ 必须顶格**写在触发状态格开头（`**✅ …**` 这种把 ✅ 埋在加粗记号后面的写法会被 linter 报错——
>   2026-08-06 前该字形已三次导致人工计数出错）。格中间出现的 ✅ 不算 close（如 AZ 的「链接半 ✅」= 半完成、仍活跃）。
> - **两族编号，两个计数标记**：`lint:active-count` 数**字母编号族**（`A`…`BX`）——就是 [§4.4](#44-backlog-数量上限)
>   上限 15 那本账；`lint:active-other-count` 数**非字母编号族**（`DEFECT-*` / `T10 / #4` /
>   `AF-residual` / `NAMING-EXTKREFS`）——**不占配额**，纯为「看得见」。两个数字都必须与表格实际活跃行数一致。
>   散文横幅不作为计数真值源——旧 linter 曾试图从横幅正则提取数字，实际从未匹配成功、计数检查空过了两个月。
> - **非字母编号族同样必须在本表有行**。2026-09-08 之前 linter 的 ID 正则是 `[A-Z]{1,2}`，
>   整个第二族对**每一项检查**都不可见——审计当场查出 **24 条只有 §1 正文、表里没行**，
>   外加 1 条把 ✅ 埋在括号里（`DEFECT-COMMODITY-AS-TICKER`）、2 条整条挤在备注格里超上限。
>   现已全部补齐并由脚本守住。
> - **标题不写状态图标**：条目标题里出现 ✅ / CLOSED / CANCELLED 会被读成「这条已关」。
>   状态一律写在触发状态格，不写进标题——标题一改，指向它的锚点会集体失效。
> - **「轻条目」是合法形态**：只有本表一行、没有 §1 正文（如 BF）。但**必须在备注格显式标 `〔轻条目〕`**——
>   合法性是**声明**出来的，不是从「找不到正文」推断的；否则条目哪天意外弄丢正文会**静默通过**，
>   等于修掉一个空过又造一个新的空过。已标 `〔轻条目〕` 但备注格超过 1000 字同样报错——
>   那已经不是表格单元格，而是一条藏在行里的条目，应拆出 §1 正文（BG 即因此于 2026-08-06 拆出）。

| ID | 标题 | 强度 | 触发状态 | 备注 |
|---|---|---|---|---|
| I | retro governance should_update | 🟢→✅ | ✅ **DONE（2026-07-27·governance commit）** | 任务1（Q5 撞墙→非技术语言写明→上升人工·§2.7.5）+任务2（pre-flight 顶层对齐前置闸·§2.3）已落地；任务3（O-A6.1.2-02 A/B）用户裁 **A=直接关掉·不改 6 条触发条件**。活跃 12→11 |
| K | retro amend on cold-review | 🟢→✅ | ✅ **CLOSED（2026-07-27·close-by-decision）** | 反向条件（2026-11-25 前无 cross-session amend 模式→关）提前满足·冷眼复查已内化进 retro 流程（§2.11.7）·N 停在 2·保留位置 + ✅ |
| N | 依赖 lock 文件机制 | 🟡→✅ | ✅ **DONE（2026-07-23·合 main `4a5d530`·[#197](https://github.com/JunoChenZt/subagent-for-investment/pull/197)）** | uv.lock + CI(uv sync)/Docker(requirements.txt) 接线·3-Python×2-OS 全绿·retro [N_2026-07-23](../retro/S2/N_2026-07-23.md)；**owed① un-pin fastapi 0.137**：测试侧适配已 DONE（[#201](https://github.com/JunoChenZt/subagent-for-investment/pull/201)·合 main `a9f6966`·路由契约枚举 `app.routes`→`app.openapi()["paths"]`·**只读调查坐实非 auth 代码·移出红线**·0.116/0.136/0.137 三版 genuine 4/4）→ **解钉死已 DONE**（[#202](https://github.com/JunoChenZt/subagent-for-investment/pull/202)·合 main `cbdd03c`·2026-07-23·pyproject `==0.136.3`→`>=0.137,<0.140` floor+cap·uv.lock 锁 **0.139.2**·requirements.txt 重生成·全测试套件 2696 passed/0 失败 @ genuine 0.139.2）→ **owed① 完全收口·N 无遗留**|
| O | 阶段完成归档机制 | 🟢 | ✅ **CLOSED 2026-09-28（close-by-completion·S2 收口 G3·保留位置）** —— 三项全完成：① [docs/archive/README.md](../archive/README.md) ② [§2.11.10](workflow/08-retro-node-and-pr.md#21110-阶段收口时的归档2026-09-28-立) ③ 用户裁改为「写索引页、文件不搬家」→ [docs/archive/S2.md](../archive/S2.md) ✅。〔历史：**🚧 已触发·进行中**〔2026-09-28 S2 收口 G2：任务 1 [docs/archive/README.md](../archive/README.md) ✅ · 任务 2 [§2.11.10](workflow/08-retro-node-and-pr.md#21110-阶段收口时的归档2026-09-28-立) ✅ · 任务 3 用户裁改为「写 S2 索引页、文件不搬家」→ G3 写完即 close-by-completion〕（原：未触发）〕 | S2 完成或首次跨阶段 〔不可监视：判据等的是 S2 阶段全部节点做完，不是某次文件改动〕 |
| P | facts cache 降级语义升级 | 🟡→✅ | ✅ **CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— **缓存在生产路径上从来没被接上过**（取数节点自陈「从来没给任何路径传过 `cache`」·全仓 `FactCache` 只在测试里实例化）⇒ 本条描述的失效形态今天不可能发生。重开 = 真把缓存接进管道那天另立新条目。〔原 2026-08-06 事件型判据一并作废〕 | 完整 triage 实测：原五条判据中 (a)(c)(e) 全挂**已停跑的 `.3 step6` 数据窗** + (b) 带"≥2 次/月"人工统计门槛 → 结构上不可能响，**挂 2.5 个月零评估**。新判据全事件型：(A) 任何改动触及 facts cache 代码即响〔承接原 (d)、放宽掉"须有 cache 实现节点"限定〕/ (B) 出现一次「返空而非 stale 致该跑无数据」实例 / (C) endpoint 失效造成 dispatcher total timeout / (D) 用户明确要求。**反向条件 (a) 亦挂死信号已作废**（反向挂死比触发挂死更隐蔽=永久卡死）。修订史见条目末尾（§4.3）。🔴 **2026-08-31 再订正**：判据 **(B) 仍是死信号**（缓存从未接进管道，结构上不可能触发）；判据 **(A) 已于 2026-08-26 响过一次（G6 改缓存钥匙）而本条无人回看**。详见条目内 08-31 块 |
| Q | 用户 query 反馈通路缺失 | 🟡 | ✅ **CLOSED（2026-08-06·close-by-decision·保留位置）** | 完整 triage：核心半已由 [AY](#ay-中文公司名--美股代码-仍无确定性兜底ak-已知缺口2026-07-24) 交付（[#213](https://github.com/JunoChenZt/subagent-for-investment/pull/213)·实证「英伟达」→NVDA）；剩余半（通用 source-level 引导通路 / 前端 UI 形态 / `degraded_reason` 体系）**已搬去 [S3 L-C.4](../roadmap/S3.md)** 含方向约束。**close 主因=三条触发条件全挂已停跑的 `.3 step6` 数据窗，结构上不可能响**（挂 2.5 个月零评估）→ 起因之一催生 [§4.1 判据有效性约束](#41-新增-backlog-条目) |
| R | Yahoo Finance RSS 可靠性 | 🟢→✅ | ✅ **CLOSED（2026-07-27·close-by-decision）** | MarketWatch+Google News 双源够用·多源聚合 nice-to-have·三触发条件均未命中·真命中重开即可·保留位置 + ✅ |
| AG | 全链路 KV cache / prompt caching 优化 | 🟡 | ✅ **CLOSED 2026-08-11（close-by-completion + 剥离·保留位置）** —— ①打标记已做（`82011fb`·默认关·用户裁决）；②③自动前缀缓存路 A/B 实测无效已放弃（analyst 并行发出，缓存要先后）；剩余大头剥离为 [S3 §6.1 COST-FM-PREFIX](../roadmap/S3.md) | 2026-05-29 记录；与 AF 互补 |
| AH | LLM token 用量追踪（per-call + per-run） | 🟡→✅ | ✅ **DONE（早已实现·2026-07-24 verify-before-acting 发现未收口而 close）** | 实现在 [`token_usage.py`](../../src/committee/token_usage.py)（263 行·落账 `84a69d1`/[#145](https://github.com/JunoChenZt/subagent-for-investment/pull/145)）：per-call `record` + **by_model & by_tag 双汇总** + `estimate_cost`（超原 scope）+ `TokenUsageCallback`（焊进 `_llm`·per-tag）+ resume merge；接线 graph(`token_usage` 入 result)/checkpoint(`_token_usage` 持久化)/cli(`_print_token_table`)。测试 [`test_token_usage.py`](../../tests/test_token_usage.py) 23 绿。**backlog 条目 stale**（立账 2026-06-02 说"无记录"·实现于 #145 后未回填 close）|
| AI | Audit pipeline 否定半边失效（mismatch/failed 死态 + audit_status 零 enforce） | 🔴→✅ | ✅ 已收口（MASK.E1 + AUDIT-3CHECK CANCELLED） | E1 删 `audit_confirmed_mismatch`/`audit_failed` 死枚举 + 三检查 CANCELLED（audit 永停存在性半项·不再追负态）+ Path B 输出侧兜"错数字不到读者" → 否定半边议题收口；S2.3-gate agent-review；与 AD 同源 |
| AJ | DS-0 部分 LLM 产出无效用（cross_role_alignment 死输出 + watermark 空中楼阁） | 🟡→✅ | ✅ **DONE（2026-07-24·[#206](https://github.com/JunoChenZt/subagent-for-investment/pull/206) squash 合 main `36578b4`）** | 活1+活2 删净（净删163行）·全套件2716+archive-replay回归测试+真deepseek fresh smoke·衍生 AW（provenance前置议题）/AX（as_of脆性 observe）；retro [AJ_2026-07-24](../retro/S2/AJ_2026-07-24.md) |
| AK | 本地证券名录（ticker 校验 + 名称→代码兜底） | 🔴→✅ | ✅ **MERGED（2026-07-27·[#211](https://github.com/JunoChenZt/subagent-for-investment/pull/211) squash 合 main `c03762d`）** | pre-node 设计边界审查 4 问用户拍板后一次做完：三市场名录（CN 5531 / HK 2783 / US 13537）+ 对账决策表（校验 / 冲突纠正 / 名称兜底）+ 接入 classify（名录排在 regex 与 web_search 之前）+ trace 契约 smoke（剩余项 #2）+ 港股取价腿 + 每日凌晨自动刷新（TZ 北京）。e2e A/B 坐实：同强制 classify 超时下，名录 ON → `300308.SZ` + tushare 真实价；OFF → 整个 query 降级成 THEMATIC 去拉 FRED。两轮外部 review 过。retro [AK_2026-07-24](../retro/S2/AK_2026-07-24.md) |
| AL | degraded 噪声（方向1）+ 扩基本面（方向2） | 🟡→✅ | ✅ **DONE（2026-07-23·close-by-completion）**：方向1 [#199](https://github.com/JunoChenZt/subagent-for-investment/pull/199)（价格源冗余组 flag·非路由）+ 方向2 **Layer 1** [#203](https://github.com/JunoChenZt/subagent-for-investment/pull/203)（tushare/yfinance 拉结构化基本面喂 agents·独立 enrich 步骤·Layer-1 焊出 audit/盖章路）。**Layer 2**（研报数字凭结构化源拿 🟢 不盖章）= defer·独立设计+用户逐节点确认·在下方「二档 cluster」追踪。retro [AL-dir2](../retro/S2/AL-dir2_2026-07-23.md) |
| AN | triage/audit 命名别名（dataflow 文档债） | 🟡→✅ | ✅ **DONE（2026-07-24·[#205](https://github.com/JunoChenZt/subagent-for-investment/pull/205)）** | [dataflow-whole-pipeline.md](../pipeline/dataflow-whole-pipeline.md) 速览步骤 3/7 加 triage=初审/初道质检、audit=终审/终道核数 别名 + 词汇对齐注（对齐用户心智·防 F1 事故式命名错位）|
| AP | wisburg REF#W 子集匹配 | 🟡 P2 | ✅ **CLOSED（2026-08-06·close-by-merge → BI·保留位置）** | 完整 triage：触发形式满足（#226 大改 audit 匹配）但对应修法 B 06-24 已撤、落点 `_extract_ref_id` 又被 #226 删 → audit 侧路已死透；**⚠️ 实质问题（20 篇塌成 1 个 `REF#W`）复核仍在，故非 close-by-supersede**——同源同触发同前置调查、且 BI 取正文必然要拆 per-report ref → 全文并入 [BI](#bi-wisburg-只取研报标题全链无人读正文--半句话成了承重数字的依据2026-08-03-全链回归-e2e-findings-33-逐条过时立账) |
| AT | 现价锚点可用性（取价 retry + fail-fast） | 🟠→✅ | ✅ **DONE（2026-07-23·AT.1 [#196](https://github.com/JunoChenZt/subagent-for-investment/pull/196) + AT.2 [#200](https://github.com/JunoChenZt/subagent-for-investment/pull/200)）** | check② 尺子地基已固；AT.2 现价拿不到=优雅早退产「暂不可分析」（方案 B·R5 拆墙确认·不崩不硬跑）；AL-AT 节点收口 [retro](../retro/S2/AL-AT_2026-07-23.md) |
| AU | ~~Python 版本收敛~~ → **CI 测试覆盖生产 Python 版本（3.11）** | 🟡→🟢→✅ | ✅ **CLOSED（2026-08-07·close-by-completion·合 main `e60c74f` [#229](https://github.com/JunoChenZt/subagent-for-investment/pull/229)）** | 可复现动机已被 universal `uv.lock` 解掉（每个 版本×平台 分支确定性钉死·非漂移）→ 收敛大工程不做；真残留=CI 测 3.10、生产跑 3.11、**3.11 只 build 不 test-run** → 窄活已做：backend job 加 `3.10 + 3.11` matrix（地板 + 生产双测·`fail-fast: false`）。**取 matrix 而非换 3.11**：只换会丢掉 `requires-python=">=3.10"` 声明支持面的地板覆盖 |
| AV | 路由契约负向守卫 TestClient 化（消除 openapi 枚举 `include_in_schema` 盲点） | 🟢→✅ | ✅ **DONE（2026-07-24·[#205](https://github.com/JunoChenZt/subagent-for-investment/pull/205)）** | 两个 enumeration-based 测试改 TestClient 真打探测（`!=404` 判存在·`==404` 判不存在·跨版本稳无 schema 盲点）·删 `_route_paths()`。review F1 权衡=丢"任意 /api/* 宽扫"（三难取舍下合理·固定清单覆盖真实契约）·已加"清单需同步维护"注释。auth 目录 75 绿 |
| AW | 数字来源(provenance)核对放置 — 一部分能否前置到 fund_mgr 拍板前 | 🟡→✅ | ✅ **CLOSED（2026-08-05·close-by-completion）** —— 命题已被 [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 判定 3/4 实现覆盖：**核来源（非核值）、且位置就在 fund_mgr 之前的 audit 层**，正是本条的原命题。Chesterton 前置（读当年砍 AUDIT-3CHECK 的边界意图）**已在 2026-08-05 全景对账中完成**并写成时间线。后续归 [number-provenance-endgame](number-provenance-endgame.md) 判据 D2 | 2026-07-24 AJ 活2 删除讨论 surface·用户命题=核**来源**非核**值**·须先厘清当年砍 AUDIT-3CHECK 的边界意图（Chesterton fence）·仅登记不预设方案 |
| AX | DS-0 `as_of: str` 不收 LLM `null` → node fallback 脆性 | 🟡→✅ | ✅ **CLOSED（2026-08-03·close-by-completion）** —— 已合 main：[#220](https://github.com/JunoChenZt/subagent-for-investment/pull/220) squash `381824a`（2026-07-31·`AsOfLoose` BeforeValidator 在 [pass0.py](../../src/committee/schemas/pass0.py)）。**根因亦已消除**：病根「搜索代理丢 `publishedDate`」随 Serper 切换 + Worker `normalizeDate` 解决（带日期率 0%→62%）。〔**08-03 R7 更正**：原写「分支 `auto/websearch-relevance`·待 PR 合入」= stale——分支远程已不存在、代码在 main〕〔原「用户裁决暂不修·继续跑批」口径已由用户 07-30 同日改判为「修」〕 | 2026-07-24 AJ 真 fresh smoke 抓·**非 AJ 引入**·修法候选=`as_of` 改 `str\|None` 或 null→"" 归一 validator（镜像 T4/T6 sanitize）。**↓ 2026-07-30 数据点2（全链回归 e2e seg4）↓** |
| ↳ AX 数据点2 | 同上·**后果比原记录严重** | — | — | **两次尝试全灭 → `ds_researcher_result=None`·`facts_inventory` 空**（原记录只写"校验失败 fallback"）。触发率 attempt1 **7/50 (14%)** / attempt2 **10/54 (19%)**；**重试无效**——retry 时 LLM 产出更多 fact（50→54）但 null 比例反升。**根因链**：缺日期条目**几乎全是 `source_type=retrieved_from_web`**（attempt1 7/7·attempt2 6/10）→ 搜索代理**每条结果只返 title/url/description/engine 四字段、无任何日期字段**（实测·SearXNG 标准有 `publishedDate`·系转发层丢弃）→ LLM 对 web 来源诚实填 null → schema 拒 → **43 条日期齐全的条目连坐作废**。⚠️ **性质=惩罚诚实**（编个日期反而能过）·与项目「不确定性诚实 > 数字正确」原则冲突。**与 [DEFECT-WEBSEARCH-RELEVANCE](#) 是同一转发层的两个毛病**（一个返垃圾·一个丢日期）→ 换后端可一并解决日期缺失，但**本校验的脆性独立于搜索质量、仍须修**。**从摘要文本解析日期的路已证伪**：实测 60 条结果仅 4 条（7%）摘要含日期。**下游影响**：seg8 `audit_status` 分布指标、seg9 G5 誊写核查**均无输入可评**（本次 e2e 后半段这两项判「无效」而非 PASS）。证据：[regression-e2e-20260730](../observations/regression-e2e-20260730/) **`seg4-debate1.ax-failure.calls.jsonl`**〔2026-07-31 改名保号：修好 AX 后要从 seg3 重跑 seg4，原文件名会被新产物覆盖 → 故障现场按本目录既有惯例（`seg2-research.bing-ddg.*`）另存变体名〕。**↓ 2026-07-30 处置 ↓** 修法取候选②（null→`""` 归一 `BeforeValidator`·[pass0.py](../../src/committee/schemas/pass0.py) `AsOfLoose`）——**只收 null、不做格式归一**（本字段是宽松 `str`，套 `sanitize_as_of` 会改写/丢弃现在就收的 `"Q4 2024"` 这类值 = 行为变更，不是本 defect 的修法）。5 条靶测含「一条 null 不连坐作废整批 fact」+「非 null 的非字符串仍拒收」（证明没把校验整体放松掉） |
| AY | 中文公司名 → 美股代码 仍无确定性兜底 | 🟡 | ✅ **CLOSED·已合 main**（[#213](https://github.com/JunoChenZt/subagent-for-investment/pull/213) squash @ `681ed9e`·2026-07-29·`auto/AY` 已删） | 4 goal 全落地：可扫描判据条目级化 + curated 34 名候选种子 + classify 重试 + 可疑降级告知。**实证闭合**：LLM 超时下「英伟达」→`NVDA`。**方向中途转向 v2**（系统提议→用户拍板）：东财非官方端点限流不稳 + 名称自动匹配会混淆不同公司（博通/博通股份、京东/京东方）。tushare `us_basic` 中文名实测 0%〔原「撞 6000 行截断」归因已纠正=分页可拿全 24915 行，仍 0 条〕 |
| AZ | 活文档链接/模板同步小债（~~overview.md root-relative 链接~~ ✅ + ~~`.env.example` 缺新 env~~ ✅） | 🟢→✅ | ✅ **CLOSED（2026-08-12·close-by-completion·两半皆完·保留位置）** —— 链接半 2026-07-29/30 已完（docs 整理 A 档 `41552a3` 实修 55 处·全仓断链清零 + [#218](https://github.com/JunoChenZt/subagent-for-investment/pull/218) 入库 `scripts/lint_doc_links.py` 防复发·2026-08-12 复扫 root-relative **0 处**确认未复发）；**env 半随 BA 一并做完**——[.env.example](../../.env.example) 补 6 键（`COMMITTEE_REGISTRY_*`×5 + `COMMITTEE_CLASSIFY_TIMEOUT`）**全注释形式**。⚠️ **BG 触发动作已执行**（非跳过）：grep 实查坐实 `REFRESH_HOUR` 有守护测试直断默认值 2（[test_security_registry_scheduler.py:52](../../tests/test_security_registry_scheduler.py#L52)）+ config 在 import 时 `load_dotenv()` → **故只能登记为注释、不给生效赋值行**，理由已写进模板注释供后人看 | 2026-07-29 docs-audit [#214](https://github.com/JunoChenZt/subagent-for-investment/pull/214) surface·用户拍「先不动只记」；链接半可脚本化·全仓仅 overview.md 一个文件有该写法；env 半 = `COMMITTEE_REGISTRY_*`×5 + `COMMITTEE_CLASSIFY_TIMEOUT`（真值源在 `security_registry/`·不在 `config.py`）。〔**2026-08-03 前置**：env 半含数值项 → **动手前先走 BG 的触发动作**（grep 有没有测试在断该键的默认值），否则 `.env.example` 一加就可能静默架空某条断言〕 |
| BG | 往 `.env` / `.env.example` 加数值项会**静默架空**「测代码默认值」的断言 —— 无人守 | 🟡→✅ | ✅ **CLOSED（2026-08-13·close-by-completion·保留位置）** —— 原触发条件「新增数值项时先 grep」已由机器代劳：[lint_env_shadowing.py](../../scripts/lint_env_shadowing.py) 从源码算出「env 键 → 代码默认值」再比对断言，值相同即报错（含本机 `.env`）；键一进模板就强制留警示注记；豁免表过时会自己报。已接 CI + 22 条自检测试 + 6 变异全杀。⚠️ **顺带订正条目原暴露面清单**（原只扫 `config.py` → 漏掉住在 `security_registry/` 的键；`MAX_TOKENS` 其实安全、真正踩雷的是 08-12 刚加的 `CLASSIFY_TIMEOUT` 与 `REFRESH_HOUR`）。**未做**：候选 3（改 7 处既有断言的取值源）——收益不抵动既有断言的风险 | 2026-08-03 [#223](https://github.com/JunoChenZt/subagent-for-investment/pull/223) review 沉淀切出（坑表已立 [§3.2](workflow/09-known-pitfalls.md)「`.env` 罩住代码默认值」·N=2）。**本条记坑表没记的那半：现在有哪几条断言站在雷上。**暴露面 ①已被遮 `MIN_CHARS_DEBATE`（非新洞）②**靠运气绿** `MAX_TOKENS`/`MAX_TOKENS_ACADEMIC`（尚未进 `.env.example`·进去那天静默失守）③其余未撞。**非保护洞**（CI 无 `.env`→代码默认值仍有人守），丢的是**本地验证可信度**——而 mutation 证承重是在本地做的。**连带**：[AZ](#az-活文档链接模板同步小债overviewmd-root-relative-链接--envexample-缺新-env2026-07-29-docs-audit-surface) env 半做的时候正撞本条触发。〔**📦 2026-08-06 正文已拆出 → [§1 BG](#bg-往-env--envexample-加数值项会静默架空测代码默认值的断言--无人守2026-08-03-223-review-沉淀切出)**：完整机理 / 逐条暴露面 / 三条候选修法在那里〕 |
| BF | ⑨ 段价位判据的**前提不可见** —— trace 不打印「fm 本跑是否填了结构化价位」 | 🟡→✅ | ✅ **CLOSED（2026-08-13·close-by-completion·两件全做·保留位置）** —— 前提行已进 ⑨ 段决策摘要（**三态**：没填 / 填了 / 填了但数字被门控抹掉；判的是"有没有价位**数字**"不是"有没有价位**对象**——冷审收严，见下；前提不成立时明写判「本跑无效」而非 PASS，与 guide ⑨ 段 D2 同口径）；图例改「本段涉及（按段成员染色·非实际执行）」+ 染色函数补注防回退。**贵修法（从 checkpoint 反推真实执行集再染色）不做**，将来若要画「实然」按 [§4.1](#41-新增-backlog-条目) 另立事件型条目。验证 = 19 份 `origin/main` tracked 的 ⑨ 段 checkpoint 离线回放（三形态全命中·交叉断言 19/19 过·mutation 五跑证承重），**冒烟以离线回放替代经用户 2026-08-13 裁决同意**（改动不经任何 LLM 调用路径·真跑零增量判别力）。evidence [bf-trace-premise-20260813](../observations/bf-trace-premise-20260813/EVIDENCE.md) | 〔轻条目〕2026-08-03 数字线重校切出（对账建议 3·唯一需改代码故未随做）。**实测**：11 次正常 run 里 **10 次 `execution_plan.entry = null`** → ⑨ 段两条价位判据在 **91% 的 run 里无从判起**，判据恒真 = **空过**。⚠️ **空过比空线更危险**：空线每次判 ❌ 有人看见会吵，空过是**静默**的——打勾打了两个月其实一次都没真验过。**修法**：[trace_report.py](../../src/committee/trace_report.py) 在 ⑨ 段摘要里显式打印该前提，把「靠人记得先确认」变成机器可见。**当前缓解**：guide ⑨ 段已写死「读价位判据前先确认前提·不成立判『本跑无效』而非 PASS」（人工，未自动化）。<br>**↳ 并入第 2 件（2026-08-03·FINDINGS §3.7 逐条过·同文件同性质故不另立条目）**：trace 拓扑图把**没执行的节点也染成「本段执行」绿**。已核根因（非推断）=[`_node_classes`](../../src/committee/trace_report.py) 纯按**段成员**染色（`now = set(seg.members)`），**不读实际执行**；而图例 [trace_report.py:439](../../src/committee/trace_report.py) 写的是「🟩 本段执行」——**措辞与语义不符**。实例：`price_unavailable` 是 seg1 成员，条件跳转没走它，图上照样绿（07-30 排查时靠翻 checkpoint 才确认）。**两件同根**：trace 这把尺子对「前提/实际」都只画应然不画实然。**便宜修法**（可与本条一起做）：图例改「🟩 本段涉及」= 一行、零风险；**贵修法**：从 checkpoint 反推真实执行集再染色 |
| BA | 本地证券名录 DB 未持久化到 volume（**S2 首次部署起**会每次重建清零） | 🟡 | 🔧 **模板侧已预防·仍活跃**（2026-08-12）；触发条件收窄为 **S2 首次部署时** | 2026-07-29 docs-audit surface·**成本浪费非故障**（lifespan `prewarm` 会重建·全失败也只回落"名录不可用"= AK 之前行为）；修法 = `.env.prod` 加 `COMMITTEE_REGISTRY_DB=/data/...` 指进已有 `backend_data` volume·**改 `.env.prod` = 红线须用户手动**。〔**⚠️ 2026-08-12 前提订正**：原措辞「生产每次重建镜像清零」是**现在进行时·不成立** —— 线上跑的是**旧 S1**，名录功能（AK [#211](https://github.com/JunoChenZt/subagent-for-investment/pull/211)）属 S2 **未部署**，浪费尚未发生。机理断言逐条复核**全部仍成立**，错的只是时态。[.env.prod.example](../../.env.prod.example) 已预置该行 → **新建环境开箱即修好**；但服务器上已存在的 `.env.prod` 是历史文件、**不会自动获得**，S2 首部署时须手动补。**不 close**：生产从未验证，拿"模板改好了"当"问题解决了"= 未验证冒充已验证〕；⚠️ 结论仍为静态读码+读 compose 推断·**未生产实测**（当前 S1 环境跑不出该现象） 〔不可监视：判据等的是首次部署到服务器这个动作，不经过本仓提交〕 |
| BE | `evidence_log` 空但正文有带章数字 —— 「0 evidence = 无数据支撑」判据量错对象 | 🟡→✅ | ✅ **CLOSED（2026-08-03·close-by-completion）** —— 触发条件「下次动 guide-验收标准」满足（数字线一次性重校）。判据改**两步判**：`evidence_log=0` 时先扫正文数字带不带 `W#`/`REF#` 章，带章=数据在只是没进字段→记 observe 放行，正文数字也无出处才 ❌。**下游 G1 代码一行未动**（`len(evidence_log)<2` 仍按原样计数·误报侧非漏报侧·方向安全）。已在 [e2e-acceptance-standard §4](e2e-acceptance-standard.md) 登记为「放松」 | 2026-07-31 Serper 切换 e2e seg2 surface·**判据失真 + 潜在误报**·单数据点。`technical_report` evidence_log **0 条**（checklist ② D2 判 ❌），但正文 5 条 key_points 含 RSI 46.99 / MACD -2.21 / 50-200MA / VWAP $193.12，**数字带 W# 外源章 + REF# 内源锚** → 数据在，只是没进该字段。本段 technical **4 次搜索全成功 0 超时**（与同段 sentiment 的 web_search 超时无关）；07-30 同角色基线是 4 条。**下游承重已核**：[risk_gate.py:73](../../src/committee/agents/risk_gate.py#L73) G1 按 `len(evidence_log)<2` 计数，本次 technical=Underweight 非 Strong\* 故未触发。**方向安全**=空 evidence 让 G1 更易开火（误报侧非漏报侧）→ 非安全洞。与 [BB](#bb-段间-checklist-⑧-的-audit_passed--50-是空线五次-run-全-6132026-07-31-全链回归-e2e-surface) 同族（判据字面 vs 实质错位）|
| BD | `_normalize_as_of` 不认英文日期格式（归一职责压在 Worker 侧） | 🟢→✅ | ✅ **CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— **本条自写的反向条件已成立**（只有一个搜索上游 + Worker 侧归一稳定无漏）。⚠️ **判据本身是好的**，关它是「值不值占配额位」的取舍、非判据失效。🔑 **关之前已把知识挪进代码**（用户裁的前提条件）：[as_of.py](../../src/committee/as_of.py) 现已写明「英文写法一概不认 / 今天靠 Worker 在进仓前转 / 接第二个上游时补在这里」—— 该注即真值源。 | 2026-07-31 Serper 切换第 3 步评测 surface·**已有可用绕法非阻塞**。实测 Serper 三种日期写法（`Dec 19, 2025` 9 条 / `25 Feb 2026` 6 条 / `3 months ago` 8 条·样本 36）喂 `sanitize_as_of` **全返 `''`**——[as_of.py:59](../../src/committee/as_of.py#L59) 只收 ISO 系，英文月份名不在列 → **不归一 = 日期白拿**（模型看得懂·staleness/`is_outdated` 用不上）。用户拍「先做 A（Worker 侧归一·改动隔离·退得回去）·B 进 backlog」。A 已落地 [worker-search-serper.js](../plans/worker-search-serper.js) `normalizeDate` + 34 case 自测（含 round-trip 验 0 条被丢）。**做 B 须继承两约束**：不给相对表述编日级精度（假精度）· 降精度方向必须偏旧（staleness 保守侧）|
| BC | 引用锚存在性无人校验 —— 编造的 `REF#` **拦不住已实证** | **🟠→🔴→✅** | ✅ **CLOSED（2026-08-14·close-by-completion·随「数字出处」问题域封卷）** —— close 条件 = [endgame](number-provenance-endgame.md) **D1+D4 达成**；D1 于 08-14 由 [BC 收官两跑](../observations/bc-final-e2e-20260814/FINDINGS.md) 补齐（连续 3 次最高信任档零错绑）。🔒 **close 的是「本域判据已达成」，不是「编造出处解决了」** —— 该形态 08-14 **第三次自然复现且手法更宽**（首次空头侧 / 首次编外源数字章 / **凭空造命名空间**而非续编号 ⇒ 本条原记的「同一编号策略」被推翻），**至今没被任何一道门拦过**；三次里唯一没造成伤害那次是模型自己改对的、非机制保证。`halluc` 零 fire 第 5 次成立（移交 endgame **G5** observe）。**正文全保留作已知形态记录；要治须重新立项、不得挂靠 endgame 的 DONE**。〔正文见 §1〕 | 〔**下方为 2026-07-31 立账期记录·point-in-time·正文不改**〕2026-07-31 全链回归 e2e seg5 surface·**覆盖缺口非已证缺陷**。R2 多头续写段编造 `REF#Y-009~Y-013`（references 实止于 `Y-008`）各挂一个精确数字。**扩散实测**：假锚从 seg5 起进每段 checkpoint、进 seg7 十个 voter 的输入 prompt；但 [archive-from-final.json](../observations/regression-e2e-20260730/run-NVDA-zh-20260730/archive-from-final.json) 全字段扫**唯一命中 `debate[].content`**，`votes`/`decision`/`pass0_result` 零命中。🔒 **精确表述**：5 个假锚没进 `final_decision`，原因是 **fund_mgr 自己没采用·不是被门拦下的**——引用解析/誊写核查**从未被触发过** → 「门能否识别编造 `REF#`」**仍无实证**，只是这次没撞上。设计已核（非推断·R5）：debate 的 F-class 只查分轮可见性（[rules_f.py:31](../../src/committee/triage/rules_f.py#L31)）**不校验锚存在性**。**若验证结果为拦不住 → 升 🔴**（撞 PROSE-MASK-ESCAPE 同族方向不安全）|
| BH | `reevaluate_triggers` 四个结构化字段**恒空**（38 archive / 180 条 trigger 填充率 **0%**）—— 触发条件只有人能读、程序读不了 | 🟡→✅ | ✅ **CLOSED（2026-08-06·close-by-completion·合 main `c7306ac` [#228](https://github.com/JunoChenZt/subagent-for-investment/pull/228)）**〔⚠️ **「结构上填得上」已实证、「模型真的填」未实证** —— 无 e2e 跑批读过修复后填充率；该残留已写入 [S4 §6.4 约束 5](../roadmap/S4.md)，trigger watcher 上线前必量〕 | 2026-08-03 [FINDINGS §3.2](../observations/regression-e2e-20260730/FINDINGS.md) 逐条过时**实测升级**（原记单跑 5 条空 → 实扫全历史 0/180 = **结构性恒空**）。**根因已定位·非模型偷懒**：[prompts.py:83](../../src/committee/prompts/decision/prompts.py#L83) 输出模板要的是**字符串数组**，[`_coerce_triggers`](../../src/committee/schemas/decision.py#L304) 再把 str 包成只有 `description` 的对象 → 那四个字段**结构上不可能被填**。[S4 §6.3 soft-structure](../roadmap/S4.md)（2026-05-25 敲定）**只落了 schema 半边、prompt 半边从没落**。🚩 **北极星边界写死**：结构化触发器只用于**提醒决策者**，绝不接下单/调仓路径 |
| BI | wisburg 只取研报**标题**、全链无人读正文 —— 半句话成了承重数字的依据（**+ 2026-08-06 并入 [AP](#ap-wisburg-payload-编号粒度错位--refw-nnnn-子集匹配缺失🟡-p2✅-closed-2026-08-06-close-by-merge--bi保留位置) 残留：bundle 粗粒度编号·拆 per-report ref**）| 🟡 | 未触发（下次动 wisburg source / 信源面 / 再出现一次「标题半句成价位唯一依据」） | 2026-08-03 [FINDINGS §3.3](../observations/regression-e2e-20260730/FINDINGS.md) 逐条过时立账。🔴 **2026-08-20 更新：前置调查已完成、修法已改、已并入 seg1 G4b**——G0b 实测**无原文但有智堡自撰摘要**（2k+ 字·带出处），⇒ 修法 = 「列表拿编号 → 挑几篇取**摘要**」两步，**⛔ 不得再按原反向条件（"MCP 没取正文能力就 close"）关掉本条**（前件成立但后件不成立·详见条目内更新块）；G4b 前置 = **先测配额**。**⚠️ 并入 AP 后反向条件只 close「取深度」半边**——拆 ref 与平台能力无关、独立成立，届时须显式裁决不得默认关掉。~~已核：[wisburg_source.py:41](../../src/committee/common_context/sources/wisburg_source.py#L41) **全程只调一个 tool** `list-institutional-reports`，返回仅 `[ID] 标题 + date`~~（平台实有 **13 个** tool，原记「11」已过时）。🔵 **2026-08-21 更新：取深度那半已做，但本条不得据此关闭** —— seg1 **G4b** 落地（五库 + 资讯流可点名 · 列表拿编号 → 挑几篇取摘要 · 真平台实测拿到 **2272–2788 字**智堡自撰摘要）。⇒ 「半句话成了承重数字的依据」这个成因**在能力层面已消除**。**🔴 没做的那半 = 并入本条的 AP 残留「bundle 粗粒度编号 → 拆 per-report ref」** —— 本条自己写明「拆 ref 与平台能力无关、独立成立，届时须显式裁决不得默认关掉」，本次**显式不做**。⚠️ 另：**管道默认仍是投行库 + 只拿标题**，点名要等 G5 ⇒ 生产里那半句话的问题**要到 G5 才真的消失**。证据见 [G4b FINDINGS](../observations/rp-g4b-smoke-20260821/FINDINGS.md)。**具体后果**：07-30 NVDA 跑「花旗维持买入、目标价 $300」成了 TP $300 的依据，而我们只有标题那半句。⚠️ 施工继承约束=**直连不走 proxy**（`trust_env=False`）；取到摘要≠可当结构化源（那是 AL 的 Layer 2） 〔监视 src/committee/common_context/sources/wisburg_source.py, src/committee/common_context/sources/〕〔粗粒度：判据的「信源面」指整个数据源目录，任一数据源改动都会点名本条，非 wisburg 侧改动会空喊〕 |
| BJ | 配置 / 一手来源读取机械化（CFG-READ）—— 别再靠"照 guide 即兴查找" | 🟡 | ✅ **CLOSED（2026-09-14·close-by-completion·BJ.5 五族按用户裁决落地·PR [#294](https://github.com/JunoChenZt/subagent-for-investment/pull/294) 合 main `d423dad`）** —— 🔧 **BJ.0–BJ.4 ✅ 合 main `3aeb118`（PR [#292](https://github.com/JunoChenZt/subagent-for-investment/pull/292)·2026-09-14·用户确认拆解后自走）**：名册派生 + 对账 lint（WARN 试用）· `committee config explain/show`（06-16 事故复现 = 首条靶测）· 跑批起步 config-snapshot（真跑冒烟 ✅）· 文档改口 + 模板补 40 键删 2 死键。**BJ.5 运行时「读不到即报错」五族逐族待裁·本轮不做**；条目**不 close**。下方原判据文字一字未改。原状态：🔔 **已触发**（2026-09-14 查实：(B)「动 `config.py` env 读取层 / 增删 `.env.example` 键」自 2026-08-07 起 **9 次**命中·其中 2 次在 08-31 完整 triage 之后）·**用户 2026-09-14 裁「现在做」**·按裁决排在第 0.5 层闸门之后开工；**判据文字一字未改**（守 [§4.3](#43-触发条件本身的修改)） | 2026-08-07 [闸门矩阵机制化第 1 层](../plans/gate-matrix-mechanization-2026-08-07.md)·承接 [META 观察](../observations/meta-assume-mechanism-without-verify.md) 实例 #3。起因事故=把 `config.py` 的 Python 符号名 `EXTERNAL_SEARCH_URL` 当成 env 真名（真名带 `COMMITTEE_` 前缀）→ 查空符号名 → 误判"没配置" → web-search 误判。**已有登记** [S2 §9.2 CFG-READ-机械化](../roadmap/S2.md)（本条是它的 backlog 侧锚点·非重复立项）。终态=确定性读取、读不到即明确报错不静默回退 〔监视 src/committee/config.py, .env.example〕 |
| BK | 静默降级可见化 —— 系统悄悄降级时必须留痕 | 🟡→✅ | ✅ **CLOSED 2026-09-22（close-by-completion·用户当日裁·保留位置）** —— 两本账归零（登记待补 **0 站** · 盘点真待补 **0 行**·合并后 main 实跑 `lint_degradation_registry` 92 / 0 / 53 共 145）；挂着的 **28 条记账 / observe 项全部迁到观察点表 [O-BK-01](../observations/should_update_observations.md)**（各带事件型触发条件·触发时按条处置·处置后就地标 ✅）；`API-EMPTY-QUERY` 已另立轻条目；留痕机制已机械化（登记守护 strict 在 push 钩子四道 lint 内·新退路不登记即红；汇总「本跑退了哪几步」进 trace / 归档 / 用户面）。**重开条件**：e2e / 生产出现一次「静默降级致结论失真」而汇总没报。原状态 ↓ 🔧 **BK.0/1/3/4 ✅ 合 main `a53b196`（PR [#295](https://github.com/JunoChenZt/subagent-for-investment/pull/295)·2026-09-14）**：汇总「本跑退了哪几步」进 trace / 归档 / 用户面 + 登记守护（WARN 试用）· **条目不 close**，仍持 **BK.2 补痕**〔**🔧 2026-09-15 提前批已做完 3 处 🔴·✅ 合 main `d019e98`（PR [#296](https://github.com/JunoChenZt/subagent-for-investment/pull/296)·CI 12/12）**「把没检查说成检查过了」（用户当日裁「只加留痕、绝不动判定」）：誊写核查 fail-open / EXEC-FLOOR 信号算不出 / 决策前事实核验失败 —— 分支 `auto/BK.2-red`，全部复用既有 `enforcement_log` 通道、**不新增 state 键**。同时**订正盘点一格**：誊写核查那处原记「只写日志」有误，它一直在写结构化记录、只是无人读 ⇒ 真·无痕数 33 → **32**〔**🔴 2026-09-15 再订正（用户裁「`state 弱` 也算无痕」）**：该数同样复算不出 —— 盘点表**逐行重算**得 **62 行**（53 原有 + **补齐 9 行**）中 **44 行无痕**、已做 3 行、**余 42 行**（行内自注代码点 62）。补齐法 = 表与降级点登记表对账（登记为真降级、而整个函数在表里一行都没点到）；**其中查出一条新的 🔴**（C 类规则跑不起来时，判定与「C 类通过」无法区分）。重算口径与两处对账缺口见 [BK.0 盘点 §3.0](../plans/BK-G0-inventory-2026-09-14.md)〕，**余 BK.2 普通批 40 行 → 🔴 清账后实为 25 行**（2026-09-15 用户裁「剩下也做」后开工前逐行核：**9 行是假待办**·汇总早就在报〔#14 #16 #32 #33 #34 #35 #40 #61 #62〕· **3 行只差读法**〔#15 #29 #39〕·**3 行应判不算降级**〔#31 配置校验告警 / #50 #51 只影响缓存命中〕；**M0 收集器已落地并接通 #21 ✅ 合 main `b52060e`（PR [#298](https://github.com/JunoChenZt/subagent-for-investment/pull/298)·CI 12/12）** ⇒ 真待补 25 → **24**；**🔧 M1 只差读法 3 行 #15 #29 #39 已做 ✅ 合 main `3f1bf58`（PR [#299](https://github.com/JunoChenZt/subagent-for-investment/pull/299)·2026-09-16·CI 12/12）**：生产代码零改动、只在汇总侧补三条派生（封顶路由键 / 兜底票理由 / 论述节占位），171 份在册归档回放逐字相同、六向变异全红；无痕 42 → **39**、已做 5 → **8**、真待补仍 24（M1 做的是 🟡 档）；证据 [bk2-m1](../observations/bk2-m1-20260915/FINDINGS.md)；**🔧 2026-09-16 M1.5 插队批 + 冷审收口 ✅ 均已合 main**（PR [#300](https://github.com/JunoChenZt/subagent-for-investment/pull/300) 叠在 #299 上随其 squash 进 `3f1bf58` / PR [#301](https://github.com/JunoChenZt/subagent-for-investment/pull/301) `c38edd1`）：**死派生 `classify_degraded` 修活**（读的 state 键全仓无生产者、从落地起恒不触发，登记表却标已有留痕；照 `_ticker_resolution` 的搬运先例接通）· 登记表订正 9 处 · 封顶与价格闸两句不再同屏打架 · 价格闸早停不再报三条假「没出结果」 · 死读守卫补齐 `.get` / `[...]` / 嵌套读；登记账面 **留痕 16 / 待补 29 / 不算 17**（wisburg `fetch` 退回待补）；**真 e2e 冒烟：✅ 2026-09-17 用户裁 = 由 M2 PR1 冒烟顺带覆盖、已跑过**（本句原写「未跑·豁免待用户裁」）；证据 [bk2-m15](../observations/bk2-m15-20260916/FINDINGS.md)；**🔧 2026-09-17 M2 PR1 地基 ✅ 合 main `6483a4c`（PR [#302](https://github.com/JunoChenZt/subagent-for-investment/pull/302)·CI 12/12）**：流程图**全图唯一注册点**统一装记录本（便条盖环节名 · 汇总按（码, 阶段）合并 · 阶段与角色名从环节名推）+ 丢失单由进程级改为**每次跑批一本**（整跑 / 流式两入口都装 · 跑批外的便条当场作废）；**不新增任何降级码、不动任何判定** ⇒ 真待补仍 **24**；全套 4640 绿 · 171 份在册归档回放逐字相同（⚠️ **0 份带便条 ⇒「按环节归阶段」只有单测证据**，等 P0 批开始发便条补真跑样本）· 13 组变异全红 · 真跑冒烟 1 个股 + 1 宏观 9 段全过、终局质检均 PASS；刹车 Q6 命中（横跨所有阶段）→ 用户 09-17 放行；登记账面 **留痕 16 / 待补 28 / 不算 19**；**冒烟撞到 2 条本域观察（用户 09-17 裁：先记观察项·不开新条目）**：① 研报库带摘要取数 8.1 秒贴每源 8 秒时限、两跑都没到（已证与该批无关）—— 降级清单如实报了「没拿回来」但**没说是超时**，原因只在日志 ⇒ **PR3 取数组补痕时一并看**；② 宏观 / 历史两位分析师零检索，产物分不出「选择不查」还是「工具没接上」= **P0.1 现场实例** ⇒ **P0.1 开工即消化**；证据 [bk2-m2-pr1](../observations/bk2-m2-pr1-20260917/FINDINGS.md)；**🔧 2026-09-17 P0 批（用户点名的五个要紧点）✅ 合 main `3da9a61`（PR [#303](https://github.com/JunoChenZt/subagent-for-investment/pull/303)·CI 12/12）**：① 联网检索工具没接上、直接写（绑工具失败 / 首轮调用失败两支；撞迭代上限那支按裁 G **不发**——设计内每跑上限，上限调大后重评）· ② 判了个股却到最后也没认出是哪只（一个收口点盖三支：补解析报错 / 没搜到 / **搜到了但名录判无效**〔计划里没列、开工读代码补上〕；价格闸不早停是设计、未动）· ③ 决策大纲退成单段（五支·一次退路只一条）+ 旧存档「段数少于 3 = 疑似」读法· ④ 引用条目坏了被扔（三个吞异常分支·前两支原先连日志都没有）+「断链」读法（**零阳性样本 ⇒ 只进排查报告、不进用户面**·清单缺失判未知）· ⑤ 清单超上限截断（留痕带被截条目原文前缀·每条 80 字内最多 5 条·只进存档不进提示词）；**只加留痕、退路与判定一字未改**；全套 4691 绿 · 反向变异 25 组全红 · 在册 192 份回放 188 份逐字相同、零消失、4 份新增全为真；冒烟按裁 H 豁免（前提逐条核过）；刹车 Q6 命中 → 用户 09-17 放行；盘点表 **6 行翻已做**（#9 #38 #45 #46 #56 #57）⇒ 真待补 24 → **18**（#45 里 verify.py 那半支核实生产零调用、#57 里撞上限那支按裁 G，两处判不算；**总口径重算仍按计划放 M2.7 收口**）；登记账面 **留痕 22 / 待补 21 / 不算 20**；**🔴 本批量基线时查出一个产品缺陷 → ✅ 小修已合 main `493a47e`（PR [#304](https://github.com/JunoChenZt/subagent-for-investment/pull/304)·2026-09-18·CI 12/12·用户裁修法 A「保留该项、坏字段按 schema 默认值记」+ 冒烟豁免）**：清单逐项校验、只把报错字段回默认值（重要程度 low / 数据类型 other / 冲突 False）、大纲保住、留痕 `verify_checklist_item_coerced` 记原值；对「查哪些数字」零影响（只核 high 项）；回归夹具 = 三份真实归档原始输出（改前全退单段、改后五段全保）；变异 5 组全红 · 192 份回放逐字相同 · 全套 4700 绿；证据 [bk2-outline-fix](../observations/bk2-outline-fix-20260918/FINDINGS.md)。**记 1 条不开条目**：同族形态（一个小字段让整份产物作废）别处还有没有 → M2.7 收口时顺手扫一遍 `model_validate` 的整份 fallback。**🔧 2026-09-18 PR3 取数组其余留痕 ✅ 合 main `a934ace`（PR [#305](https://github.com/JunoChenZt/subagent-for-investment/pull/305)·CI 12/12）**：名录不可用旗子 / 名录现拉失败（上端便条）/ 名录对账加载失败 / 源认不出整条跳过（今天生产走不到）/ 行情最新一根坏值回退 / 研报库兜底与摘要部分失败（与回核去重）五类补齐，补价腿只进排查报告；名录故障一次恰好两条；只加留痕、判定一字未改；全套 4737 绿 · 变异 17 组全红 · 在册 192 份回放逐字相同（零阳性基线）；盘点真待补 **18 → 10 行**（#4 #5 #6 #7 #8 #16 #18 #22 #54；#16 原误判假待办、已订正）· 登记表待补痕 **21 → 9 点**；**记 2 条不开条目**：同族「一个字段写坏就整份不要」三处候选（辩论发言换占位 / 投票换兜底中立票 / 辅助助理整份事实清单作废）· 补的价格腿仍不进归档计划的意图清单；**冒烟：用户 09-18 裁 PR3 合并后在 main 上补跑一次真实段式冒烟**（一并覆盖大纲小修 #304——原记「#304 由 PR3 冒烟顺带覆盖」不成立，PR3 按施工单不另跑）；**✅ 09-18 已跑**：NVDA 九段逐段放行、终局质检 **15/0/0/0**、全程零降级、$2.03；大纲小修正常路径真跑通过（本跑模型没写坏档位、补救分支未触发，那半仍只由测试证）；PR3 各处留痕全部正确地没响；P0.1「工具没接上」首个真实样本（四位分析师零检索、留痕没响 ⇒ 选择不查）；顺带订正「质量审核连续 9 次全过零打回」（只数了最终结论、漏了返工）；证据 [bk2-smoke](../observations/bk2-smoke-20260918/FINDINGS.md)；证据 [bk2-m2b](../observations/bk2-m2b-20260918/FINDINGS.md)；**🔧 2026-09-18 M3 决策 / 风控组补痕 ✅ 合 main `eee2ef4`（PR [#306](https://github.com/JunoChenZt/subagent-for-investment/pull/306)·09-21 合·CI 7/7）**：决策前核验里读不出的结果被跳过（#37）/ 待查证清单没写事项的条目被略过（新行 #63·并按裁 B 把大纲小修那条便条拆成「改字段 / 扔条目」两码）/ 风控问了而决策经理没答上（#44·在回应环节当场记）三处留痕；只加留痕、判定一字未改；全套 4752 绿 · 变异 13 组全红 · 在册 202 份回放逐字相同（三处历史零阳性）；盘点真待补 **10 → 8 行**（#37 #44；#63 新增即做、不入计数）· 登记表待补痕 **9 → 6 点**（落账时用合并前后两版登记表实跑对比复核：恰为 `_run_verification` / 风控同名 `node` / `_parse_responses` 三键翻 `code:`）；**守护空转两处**：「用了没登记的码」闸原单行正则、多行写法看不见（#304 起·已改 AST）+ 合并前 review 抓到改写时丢了未跟踪文件（已修 `959e9ec`·两向探针证）；冒烟按裁 E 豁免；⚠️ 本 PR 赶上 CI 额度用光，首次真实 CI 在 09-21 review 修复推送后；证据 [bk2-m3](../observations/bk2-m3-20260918/FINDINGS.md)；**🔧 2026-09-21 M4 末批 ✅ 合 main `587383a`（PR [#308](https://github.com/JunoChenZt/subagent-for-investment/pull/308)·CI 全过）**：报告没按格式写、系统修正后才收下 `report_sanitized`（M4.1·进用户面：量基线 23 跑里 3 跑洗过）/ 质量审核打回后安排的重写根本没派出去 `rework_dispatch_failed`（M4.2·合并前 review 订正措辞：只说那一轮、不对最终结果下断言 `937d82e`）两处留痕 + 末段归档写失败时屏幕提示（M4.3·用户裁 5 不开新出口）+ 收口与**节点级复盘**；只加留痕、判定一字未改；全套 4752 绿 · 在册 202 份回放 202/202 · 变异 14/14 红；盘点真待补 **8 → 3 行**（§3.0 首次写出逐行明细：余 #17 #20 #25）；登记表待补痕 **6 → 5 点**（🔴 落账时实跑订正：本批自述「6 → 4」不成立 —— M4.3 计划把 `graph.py:_write_final_archive` 翻 `exempt:` 并写重评时点，**该改动没进合并代码、仍是 pending**；证据里记的「39 / 4 / 20」合计 63、与登记表 64 条对不上）⇒ 去处 = 随 `auto/BK.2-M4-fix` 一并补〔✅ 已补·[#309](https://github.com/JunoChenZt/subagent-for-investment/pull/309) 合 main `15443b8`〕；余 5 点 = 4 点属键粒度 / 生产不可达 / 裁 G（键粒度拟另立 BK.3〔✅ 已立并合 main [#310](https://github.com/JunoChenZt/subagent-for-investment/pull/310) `dea94eb`·2026-09-22·待补按站点口径改 12 站〕）+ 上述未落地的 1 点；**记账三条**：辩论 `key_claims` 容器类型不对 → 整段陈词换占位（1/91·用户裁合并后开 `auto/BK.2-M4-fix` 小修·照 #304〔✅ 已修·[#309](https://github.com/JunoChenZt/subagent-for-investment/pull/309) 合 main `15443b8`〕）· 投票 / 两位辅助助理三处「一个字段写坏就整份作废」候选**结案**（零历史命中·会作废只由注入测试证）· 排查报告不显示便条细节**按裁 D 不做**，触发条件 = 首次有人需要从排查报告里读被截原文 / 被洗字段；冒烟按裁 F 豁免；证据 [bk2-m4](../observations/bk2-m4-20260921/FINDINGS.md) · 复盘 [BK.2_2026-09-21](../retro/S2/BK.2_2026-09-21.md)；**🔧 2026-09-21 M4-fix ✅ 合 main `15443b8`（PR [#309](https://github.com/JunoChenZt/subagent-for-investment/pull/309)·CI 全过）**：辩论要点清单写成对象时整理该项、保住整段发言（B1 已修·新码 `debate_key_claims_coerced` / `debate_key_claims_dropped`）+ `graph.py:_write_final_archive` 翻 `exempt:` ⇒ 登记表待补痕 **5 → 4 点**（合并后实跑 40 / 4 / 21）；盘点真待补仍 3 行；全套 4789 绿 · 全量对照 91 / 204 零误伤 · 变异 6 组全红；冒烟用户裁豁免；证据 [bk2-m4-fix](../observations/bk2-m4-fix-20260921/FINDINGS.md)；**🔧 2026-09-21 M4-fix 合并前 review（PR [#309](https://github.com/JunoChenZt/subagent-for-investment/pull/309)·坐实 7 = 修 3 + 记账 4·用户裁「前两条本 PR 修、其余记 backlog」）**：修 = 便条改由辩论环节出口对**最终采用**的发言发（首轮被返工替换的不发、返工换占位清空；原写法会给一条已不存在的发言留「正文完整保留」便条）· 要点清单留痕拆**两码两义** `debate_key_claims_coerced` / `debate_key_claims_dropped`（照 M3.2 裁 B；原一码兼三义、全部略过时人话仍说「整理后收下」）· 测试缺口随修补齐（11 → 18）；**记 4 条不开条目**：① `_coerce_debate_key_claims` 非列表分支返回 `None` 与直接返回空列表等价、且计数形态不一致（`non_list` 无 kept / coerced / dropped 三项）—— 可合掉；② 「从校验报错里挑顶层坏字段」那行与 `_sanitize_verify_checklist` 逐字重复 —— 抽小函数两处共用；③ [M4-fix 证据](../observations/bk2-m4-fix-20260921/FINDINGS.md) §2 / §3 两处仓内路径纯文本未用活链接（违反链接规范）—— 下次动该文时改；④ 回放脚本按 `splitlines()` 切行，JSON 字符串里合法的 U+2028 / U+2029 会把记录切断、整跑崩掉（M4 基线脚本同写法）—— 改按换行符切；触发 = 下次动辩论校验 / 该证据目录任一文件时顺手清；明细见 [M4-fix 证据 §8](../observations/bk2-m4-fix-20260921/FINDINGS.md)；**🔧 2026-09-22 BK.3 键粒度 ✅ 合 main `dea94eb`（PR [#310](https://github.com/JunoChenZt/subagent-for-investment/pull/310)·CI 全过〔lint / backend 3.10 + 3.11 / docker / secret-scan 全 pass·frontend 按路径分诊跳过〕）**：登记表键从「文件:函数名」改**站级** `文件:函数限定名::告警消息前 40 字`，65 条登记逐站审后迁成 **144 站**（多站键 33 个拆出的隐藏支各记各的·**绝不把整行「已留痕」复制给每一支**）⇒ **登记账面改按站点口径 = 留痕 82 / 待补 12 / 不算 50**（合并后 main 实跑 `lint_degradation_registry`）。⚠️ 「12 站」与旧「4 点」**单位不同、不互相推导**：旧 4 点各留 1 站（`_build_context_inner` 空 query / `apply_cache_invalidation` / `_alpha_vantage_fetch` / `run_tool_agent` 数字盖章失败）+ 拆出后**首次独立记账 8 站**（原先藏在整键 `code:` 之下：意图被拒收 / 丢弃、腿少了没留痕 **同族 5 站**〔`_plan_and_validate` 部分拒收 · `plan_retrieval` 丢弃 · `_normalize_intent` 非对象 / source 不在五源 · `validate_plan` 逐条拒收〕· 分析师扩写失败保留原报告 · 幻觉引用被剥 · 复核调用失败 detail 是否被读未核）；守卫顺手补 `--others`（未跟踪新源文件也在扫描面·同 #306 坑）；★ 存在理由靶测 = 往**已登记**真实函数种一条新退路必须响（旧守卫 findings=0 实锤）。**合并前 review 坐实 6 = 修 2 + observe 4 + 不做 0**（用户裁「修前两条、其余记 observe」）：修 ① 同函数前 40 字相同的告警按出现顺序编 `#2`，前插 / 重排会让登记**静默换主**（实测新站直接继承旧 exempt、守卫不响）→ 撞前缀整句不同用**整句**、整句也相同报「指纹碰撞」要求改措辞；② 消息不是字面量（变量 / `%` / `.format`）词表问不到、守卫对它是瞎的（原只计数）→ 报「消息非字面量」必须登记或改字面量；真实仓库回放碰撞 0 / 非字面量 0、144 站键一个不变。observe 4（各写升级触发条件·家 = [证据 §7 #7–10](../observations/bk3-20260922/FINDINGS.md)）：迁移脚本剥括号一头让 `# ↓` 注释残缺 / 10 条键尾随空格 / 「一站一键」断言恒真 / 语法错靶测被换掉。验证：守卫自检 57 · 全套 **4813 绿** · 反向变异 6/6 红 · 映射核对通过（65 旧键零落空·144 = 各键站点数之和）；冒烟裁 E 豁免（守卫不在运行时链路）；风险判定低、刹车 8 问全不命中；证据 [bk3](../observations/bk3-20260922/FINDINGS.md) · 拆解 [BK.3-decomposition](../plans/BK.3-decomposition.md)。**盘点真待补仍 3 行**（#17 #20 #25）· **条目仍不 close**；**🔧 2026-09-22 BK.5 取数意图被拒收 / 丢弃留痕 ✅ 合 main `d4d3891`（PR [#311](https://github.com/JunoChenZt/subagent-for-investment/pull/311)·CI 全过）**：同族 5 站合一码 `plan_intent_dropped` —— 规划员扔的条目记进 `RetrievalPlan.dropped_intents`（加性字段）· 人工确认环把被拦条目一起带走 · 节点**最终采用**时刻一条意图一张便条（全灭不发·回放跳过带进来的那份）；**扔不扔、怎么扔一字未动** ⇒ 登记待补 **12 → 7 站**（合并后实跑 **87 / 7 / 51** 共 145·多出的 1 站 = review 修加的自兜分支登记 exempt）；量基线 13 个规划员 run 零命中（无历史阳性·会响靠靶测 + 变异 7/7 红·没退步靠回放 202 / 202）；seg1 冒烟 ① 表全过 $0.0014；全套 4830 绿；刹车 Q6 命中 → 用户 09-22 放行；**记 2 条不开条目**（触发条件写在证据 §0 / §7）：最终归档 `archive-from-final.json` 不含 `common_context`、只留最终档会丢校验拒收线索（触发 = 归档只留最终档那天）· 人工确认路径的规划员原始输出不进 calls.jsonl（触发 = 需要回溯人工路径规划员输出时）；证据 [bk5](../observations/bk5-20260922/FINDINGS.md) · 拆解 [BK.5-decomposition](../plans/BK.5-decomposition.md) · 复盘 [BK.5_2026-09-22](../retro/S2/BK.5_2026-09-22.md)；**合并前 review 坐实 7 = 修 2 + 记账 5**（用户裁「第一条修掉补测试，其余记 backlog」）：修 ① 留痕函数原放在 `_plan_and_validate` 的 `try … except: return None` 里，留痕代码自己抛异常会把一份已校验通过的计划整跑打回兜底路由、错因还记成校验失败 → 留痕函数整段自兜（失败只写日志·登记 exempt·计划照旧采用）；② 补 3 条靶测（便条函数抛异常计划照旧 / reasons 混非字符串照记 / 补进来的取价腿 accepted verdict 不算被扔）。**记 5 条不开条目**（触发 = 下次动 `_note_dropped_intents` / cli 确认环 / planner 丢弃判据时顺手清）：① 便条 detail 的 `idx` 混两套坐标（规划员原始顺序 vs 确认后列表顺序），归档只存通过条目、读者对不回是哪条丢了，同一跑可有多条 `idx=1` 指不同意图 —— 记录里带标的 / 序列号快照或写明坐标系；② 「拒收 verdict → 记录」生成式在 cli 确认环与节点各写一遍 —— 抽 `rejected_records(validation)` 共用；③ `_drop_reason` 每条意图算两次，`or ("?", None, "未知原因")` 分支不可达、把契约藏起来 —— 让 `_normalize_intent` 直接返回丢弃记录；④ cli 确认环里 `dropped_intent_record` 的 import 写在 while 循环体内；⑤ 回放测试里无用的 `cn` import / `del cn`。明细 [bk5 证据 §7.1](../observations/bk5-20260922/FINDINGS.md)；**🔧 2026-09-22 BK.6 登记表余 7 站 + 盘点余 2 行清账 ✅ 合 main `59b3689`（PR [#312](https://github.com/JunoChenZt/subagent-for-investment/pull/312)·CI 全过）**：4 便条（空 query 整段跳过 / 扩写失败 / 数字盖章失败 / 复核调用失败）+ 1 只加读法（幻觉引用被剥）+ 2 exempt 写重评时点（缓存失效失败·生产无 cache / 备用行情源·默认未配且缺腿已报）+ 盘点 #17 #20 判已覆盖 ⇒ **登记待补 7 → 0 站**（合并后实跑 **92 / 0 / 53** 共 145）· **盘点真待补 3 → 0 行** · **两本账归零 → 主体收口、条目不 close**（正文持记账项）；量基线 57 run 五码全零（无历史阳性·靶测 14 + 变异 8/8 红 + 回放 203 / 203）；刹车 Q6 命中 → 09-22 放行；**合并前 review 坐实 8 = 修 2 + 记账 6**：修 = 扩写 except 放宽到 Exception（原只捕 JSON 类、网络异常会从节点穿出·本批唯一动退路行为处）· 空 query 对照测试改手动开篮；**记 6 条不开条目**（触发 = 下次动对应文件时顺手清）：① 码表 / 登记表注释称盖章失败便条含「标的解析」调用方，实际盖章只在收账本（`return_tool_outputs=True`）的调用里做、该路不可达；② 空 query 便条 detail 把 None 也说成空串；③ EVID-1 派生编号串按字符 `[:120]` 硬截会截出半个编号；④ `note_degradation` 在 mismatch_review / context_node 函数体内 import；⑤ BK.6 节点测试钉死全仓 pending 归零、下一个合规登记 pending 的 PR 会被打红（首次打红时改由 lint 承接）；⑥ 测试无用 `agent_loop` import。**本批另记 4 条**：HTTP `/analyze` 不拦空串（→ 轻条目 `API-EMPTY-QUERY`）· `__degradation_notices__` 无读者（触发 = 决定给 U1 告警找读者或删该键时）· 缺腿「原因」超时 vs 异常没人记（触发 = 排查某次缺腿要分原因时）· E8 兜底档 rss 5 run / fred 2 run 可疑缺腿（触发 = 排查缺腿原因时翻档）。证据 [bk6](../observations/bk6-20260922/FINDINGS.md) · 拆解 [BK.6-decomposition](../plans/BK.6-decomposition.md) · 复盘 [BK.6_2026-09-22](../retro/S2/BK.6_2026-09-22.md)；原缺陷记录 ↓ 模型在「待查证清单」里给某几项写了重要程度「中」、系统只认「高 / 低」⇒ 装配校验失败、**整份五段大纲连同清单一起作废**，论述退成一整段 —— 29 份带决策的在册存档里 **4 份**（最早 07-10、最近 09-02），四份原因完全相同（3 份用存档里的原始输出复现·1 份从排查报告读到同样写法）；本批 ③ 的留痕起它每次发生都看得见；**另记 2 条（不开条目）**：排查报告不显示便条的细节文字（含被截条目原文）——裁 B 已定「显示另做」，去处 = BK.2 收口（M2.7）时定做不做 · 五个新码里四个**无历史基线**（进程日志不存档）——首次在真实跑批里响起时回头核档位与措辞；证据 [bk2-p0](../observations/bk2-p0-20260917/FINDINGS.md)；明细与逐条依据见 [BK.0 §3.1](../plans/BK-G0-inventory-2026-09-14.md)）逐点待裁〔**🔧 2026-09-15 分诊批再做 2 行·✅ 合 main `91eb1bf`（PR [#297](https://github.com/JunoChenZt/subagent-for-investment/pull/297)·CI 12/12）**：#59 C 类质量规则没跑成（新查出的 🔴·已补痕·放行判定一字未改）+ #58 单份报告审核跑挂（记录早在写、只加读法·同 #41 形态）。同批**把 #60 从 🔴 降为普通** —— 追到底后不成立：E 类整族目前是观察期只记日志，E2 没跑成不会把「本该警告」变「通过」〕。**全量 171 份在册归档回放对照：169 份逐字相同、2 份只多出提示、零消失** ⇒ 判定零改动已证；那 2 份是**自然真阳性**（07-22 核查模型断线 / 08-14 额度耗尽）。本批发现但不在本批修的两项（登记表键分不开同名函数 / 解析不出的 finding 被静默丢弃）见 [证据与发现](../observations/bk2-red-batch-20260915/FINDINGS.md) §3〕· 原状态：🔔 **已触发 (D)**（2026-09-14 BJ 收口）· **重评方案已出、待用户确认**：[BK-silent-degradation-reeval-2026-09-14](../plans/BK-silent-degradation-reeval-2026-09-14.md)（先汇总后补痕·汇总纯派生不进 state 不进提示词·BK.2 补痕逐点裁·承接 CTX ⑦ 与 DSML 改进 B 命题）· 判据文字未改 · 原状态：未触发（**全事件型**：e2e/生产出现一次「静默降级致结论失真」实例 / 动 dispatcher 降级路径或 classify 超时回退或任一 fallback 分支 / 用户反馈「结果看着正常其实数据没拿到」/ BJ 收口后重评形状） 〔**2026-09-14 triage：不算触发**（用户裁）—— `ad19c61` 只在 classify 超时处加注释、明写「故意不动它」，行为未变。**但记下那条新事实**：该超时的 15 秒是**每次尝试**的上界，底层 SDK `max_retries=2` ⇒ **最坏 ≈45 秒**；同句六次实测 1.9–3.4 秒（0/6 接近超时）。真做本条时这条事实用得上，别再把它读成「最多 15 秒」〕 | 2026-08-07 [闸门矩阵机制化第 2 层](../plans/gate-matrix-mechanization-2026-08-07.md)·承接 [META 观察](../observations/meta-assume-mechanism-without-verify.md) 实例 #2（classify 慢日子静默降级→ticker 丢失无告警）+ #4（e2e 证据未 commit·一次 `worktree remove` 即蒸发）。**性质=产品链路非闸门治理**，范围比第 0/1 层大一档，须独立设计 〔监视 src/committee/common_context/builder.py, src/committee/common_context/data_source.py, src/committee/query_class/classifier.py〕 |
| BB | 段间 checklist ⑧ `audit_passed ≥ 50%` 是空线（五次 run 全 6–13%） | 🟡→✅ | ✅ **CLOSED（2026-08-03·close-by-completion）** —— **超出原 scope 收口**：BB 自己建议的「数字线 vs 历史归档对账」已于 07-31 做完（[对账报告](e2e-guide-threshold-audit-20260731.md)·11 正常 run + 4 对抗 run·**12 条数字线只有 2 条有效**），本次把结论落进 guide。⑧ 由「≥50% 判 ❌」降为 **observe**（仅 <5% 才排查·实测区间 6–47%）。连带落地对账建议 1/2/4/5/6/7（详见 [acceptance-standard §4](e2e-acceptance-standard.md) 登记表）。剩建议 3 需改 trace 代码 → 切出 **BF** | 2026-07-31 全链回归 e2e seg8 surface·**判据失真非产品缺陷**。该行 07-22 只订正了字段名（verified→audit_passed·MASK.E1 收敛后无 verified 值）、没重估阈值，而订正当天那次 run 自己就 6%。与 audit 定位自洽（永久停在来源存在性半项·T11 又挤掉存在性泡沫 26→3）→ 低占比是应然。**顺带**：guide 其他数字线也可能没校准（⑥「6 轮辩论 <15k token」实测 28,361）→ 建议一轮「数字线 vs 历史归档」对账 |
| BL | fred 的 8s 超时线在 8 路并发下**余量只剩 1.32×** | 🟡 | 未触发（**全事件型**：下次动 `_TOOL_TIMEOUT`/`fred_source`/graph 层 analyst 并发编排 / e2e 再出现一次 fred `ConnectTimeout` / DEFECT-SEG2-FLAKY 攒表触及 playbook §6 升级线 / 用户明确要求处理并发·错峰） | 2026-08-10 [C2 并发归因探针](../observations/seg2-c2-probe-2026-08-10.md) **§5 计划外观察**切出（**非该探针事前判据**——判据判失败率，结果为「不结论」）。实测三轮一致：并发把 fred 从 p50 1.11s 顶到 3.48s、p90 5.34s、**max 6.05s = 占满 8s 线的 76%**（单线程臂仅 28%）；膨胀 3.1× **且**线更紧，两头夹 → fred 是双重暴露腿（web_search 经 [#221](https://github.com/JunoChenZt/subagent-for-investment/pull/221) 加宽到 15s 后余量约 2×，**那次加宽被本组数据事后印证是对的**）。**余量问题非当前故障**（本轮零失败），但越线后果已实测 = [DEFECT-SEG2-FLAKY](#defect-seg2-flaky-seg2-并发研究段瞬时失败族--三跑三坏成因各异疑共享资源竞争🟠攒表驱动2026-08-03交接新-session) run2。⚠️ 候选三方向（限并发·错峰 / fred 带抖动重试 / 加宽 8s 线）**全动主链路须用户裁**，且第三条与 [playbook §8](../plans/seg2-flaky-playbook-20260803.md)「不放宽任何超时线」直接冲突（列它求完整，**不推荐**）；**第四选项＝什么都不做只观测，在 C2 未坐实前是默认**。〔正文见 §1〕 〔监视 src/committee/tools/definitions.py, src/committee/common_context/sources/fred_source.py, src/committee/graph.py〕〔粗粒度：判据点的是超时常量与 analyst 并发编排那两段，同文件其余改动会空喊（`ad19c61` 即一例：改的是计划注入，不是并发编排）〕 |
| BM | 文档在替一台没人核过的服务器说话 —— 「生产现在如何」的断言全仓未对过账 | 🟡 | 未触发（**全事件型**：下次真部署到生产 / 再撞一次「按文档里的生产现状判断→现状不符」/ 下次动 runbook·deploy-sources 现状类章节 / 用户明确要求） | 2026-08-12 BA 执行中撞出·用户当场拍「立一条」。**已确认失真 1 处**（BA 原措辞：写「生产每次重建清零」，实际线上是旧 S1、名录功能从未部署 → 浪费尚未发生）。⚠️ **要害不是这一条写错，是错法查不出来**：BA 的机理断言两轮审计逐条全对，错的是那句**从未被写下来、因而从未被质疑**的隐含前提「线上跑的是 main」——**静态审计能验「代码是不是这样」，验不了「这份代码在不在线上」**。高度可疑面 = [prod-runbook](../infrastructure/prod-runbook.md) 通篇（拓扑 / cookbook / §5 待办清单 / 事故复盘均在断言线上现状）+ 任何派生产 ops 动作的条目。候选处置三条（① 一次性对账·需服务器 ② 现状类断言强制带核对日期 ③ **runbook 顶部标线上环境版本**——最便宜且最治本，BA 这个错只要顶上有一行「线上 = S1」就不会发生）。🚩 边界：**只对账与标注·不改部署配置·不动线上**；历史记录属 [Q6 冻结档](workflow/05-brake-self-check.md)一字不动。〔正文见 §1〕 〔监视 docs/infrastructure/prod-runbook.md, docs/infrastructure/deploy-sources.md〕 |
| BN | 十个投票人像一个人在投 —— 同向票理由同构、`conviction` 零方差 | 🟡 | ✅ **CLOSED 2026-08-31·close-by-condition**（**反向条件连续第 3 次成立**，达本条自写的 close 线：08-31 黄金全链跑六张 NEUTRAL 票**全员共有词 0 个**、conviction 7/6×5 **有方差**；本跑输入端摆明两派仍散得开 ⇒ 反向证据更强。保留：BULLISH 组零方差但仅 2 票不足论。证据 [../observations/rp-g8-e2e-20260831/FINDINGS.md](../observations/rp-g8-e2e-20260831/FINDINGS.md)） | 2026-08-14 判据到线立账（[指南 ⑦ 段](../observations/e2e-runs/segmented-e2e-guide.md)观察点**开跑前写死**「N≥3 → 提立条目」·08-04 用户裁「先并入观察点」时 N=2·BC 收官黄金跑复现 → **N=3**）。**趋势向坏**：同构范围从「仅 NEUTRAL」扩到「NEUTRAL + BULLISH」，本跑 10 票里 **8 票 `conviction` = 6**（看多 3 张方差 0·观望 4 张方差 0·六个关键词四票全中），唯二离群是天然对立的 bear(8) 与主动弃权的 fundamentals(1)。**假设（未证）**：辩论摘要在 voter 输入里过于强势，压过各角色差异化材料。🔒 边界：**不是「投票错了」**（票型方向三次都与辩论对得上）·问的是**独立性**·**不得据本条收紧任何放行闸**（⑦ 段仍为 🔬 观察点·提高 fail 面须用户裁）·**不含「强制票型分散」这类修法**（人造分歧 = 拿表象换多样性·更坏）。候选处置三条（① **先量再修**：同向票方差 + 关键词重合率做成自动读数·最轻零行为改动 ② **对照实验**：同一 seg6 checkpoint 跑两次 seg7·一次抽掉辩论摘要·真能证伪上面那个假设 ③ 动输入配比·假设未证前不推荐）。〔正文见 §1〕 |
| BO | 时效窗口 `other = 400 天` 是五档里**唯一没有论证**的 —— 而全部外源都落这一档 | 🟡 | ✅ **CLOSED 2026-09-24（close-by-completion·CRED.2.G5·用户当日裁·保留位置）** —— D1 = 180 天已落（#315）；2.G5 全链 e2e（终局 15/0/0）实测表③ 外源册打过期标 63/150 = **42.0%**（旧 400 天下同批 31.3%·+10.7 点），低于 2.G0 聚合 51.7% 因本跑缺日期率 28.7% 处历史 23–57% 偏低端 ⇒ 在历史波动内；事实侧 2a 复核清单多入列 1 条（400 天下不会入列）⇒ 改线在决策链上生效（[FINDINGS](../observations/cred-2-g5-e2e-20260923/FINDINGS.md) §3.3）。**重开** = e2e 出现「半年以上的信息被当新鲜依据」或「未满半年的被误判过期而改变结论」〔原触发条件：未触发（**全事件型**：下次动 [`FRESHNESS_WINDOW_DAYS`](../../src/committee/facts/confidence.py) / 接第二个外部搜索后端 / e2e 出现一次「一年前的信息被当新鲜依据」/ 用户明确要求）〕 | 2026-08-18 ① 段引用时效分档时切出（**明确不在那次 scope**：那次只对齐人工侧）。**一手证据（代码注释·非推断）**：现价 / 估值 1 天写了完整论证**连失效条件都写了**（"若未来用于日内执行须收紧至 0 天"）、目标价 / 财务 100 天按一季度算，**唯独 `other = 400` 只有「放宽」二字**；而 [base.py](../../src/committee/agents/base.py) 明写「外源无 `data_kind` → 通用兜底窗口」⇒ **全部外部网络来源落此档**，400 天 ≈ 13 个月 = 去年的新闻今天仍算新鲜。⚠️ **弹药未备**：2026-08-18 那 104 条实测量的是 seg1 **内源** references，**不覆盖外源册 `as_of` 分布** —— 动它之前必须先量，别拿不相干数据当证据。**📌 2026-09-23 弹药已备 = CRED.2.G0（#313 `9035ca8`·[FINDINGS](../observations/cred-2-g0-asof-dist-20260923/FINDINGS.md)）**：外源册缺日期约 1/3、有日期里超 400 天 6.8%；「全部外源落这一档」核实只对表③展示成立（进 confidence 的外源事实按 claim 分档·80% 落 other）；**数值待用户裁 D1**，条目随 2.G2 close。**📌 2026-09-23 D1 已裁（用户）= 180 天**（半年 ≈ 两个财报季）→ CRED.2.G2 改常量 + 补校准注（✅ #315 `8570734`）；回放数见 [S2 2.G2 行](../roadmap/S2.md)；验证方式用户裁 A = 回放替代 e2e、真跑并入 2.G5；**条目待 2.G5 全链 e2e 佐证后 close**（同簇 1 / D5 先例）**为什么延后**：收窄 = 提高拦截面 = **承重变更须用户裁**。**预估**：量分布半天 + 改常量与校准注 1 小时 〔轻条目〕 〔监视 src/committee/facts/confidence.py〕 |
| BP | seg1 引用的时间戳**全程没有代码在看** —— 段间人工那一行是它唯一的守卫 | 🟢 | ✅ **CLOSED 2026-09-24（close-by-completion·CRED.2.G5·用户当日裁·保留位置）** —— 审核已读出处日期（#316）；2.G5 全链 e2e 实测零误标（5 条过审事实的出处：金价恰 1 天 = 现价窗边界·新闻 1 天·研报无日期「未知不降」）⇒ **本跑没有过期出处可抓**；「该标就标」那一面的证据 = 2.G3 主干回放（4 条过期价位带注记）。用户裁按「回放 + 单测 + 本跑零误标」关（[FINDINGS](../observations/cred-2-g5-e2e-20260923/FINDINGS.md) §3.2）。**重开** = e2e 里所引出处明显过期、审核理由却没记 / 可信度没落过期档〔原触发条件：未触发（**全事件型**：下次动 [common_context](../../src/committee/common_context/) 的 references 装配 / 水印渲染 / 段间 ① 段时效判据 / 用户要求把该人工线接成机器闸）〕 | 2026-08-18 ① 段引用时效分档时切出。**已核（非推断）**：`references[].as_of` 的去处只有两处 —— 渲染进水印段落给 analyst 读（[base.py](../../src/committee/agents/base.py)）+ 段间 checklist 人工瞄一眼；**审核环节完全不读该字段**（[audit_node.py](../../src/committee/agents/audit_node.py) 全文 `as_of` **零出现**）。⇒ 判据再怎么校准，**执行仍全靠人记得看**，形态同 BN（判据到线没人执行）。**为什么延后**：接自动检查牵动数据源装配与下游消费，**范围比判据卫生大一档**，须独立设计；2026-08-18 那次只把人工线从「指错方向」改成「指对方向」，没解决「谁来看」。**预估**：设计 + 实现 2–3 天 〔轻条目〕 〔监视 src/committee/common_context/watermark.py, src/committee/common_context/builder.py〕〔粗粒度：判据点的是 references 装配 / 水印渲染 / 段间时效判据这几块，本闸只看得见整份文件动没动〕 **📌 2026-09-23 CRED.2.G3 已合 main（#316 `a9e8b32`）**：审核首次读出处日期（`price` 1 天·其余 180 天）；用户改裁 = 过期不降审核档、可信度落过期（保 check③）；**条目待 2.G5 e2e 佐证后 close** |
| BQ | 主题型资产类 query **永远拿不到行情** —— 黄金/原油/指数/加密/汇率被归主题型后价格源永不激活，而它们其实有真实行情可取 | 🟡→✅ | ✅ **CLOSED 2026-09-02·close-by-decision**（用户当日裁·触发条件「用户明确要求」命中）—— **核心主张已解**：同问句同配置各跑 3 次的 A/B，问「黄金会怎么走」**旧路由 0/3 拿到行情腿、新大脑 2/3**（`GC=F` 真价 4682.80，且**真流到下游**——进事实清单第一条 `f1`、带水印 `REF#Y-011`）；对照组茅台（个股）两臂均 3/3 ⇒ 差异是**资产类特有**、非随机。解法比本条原设想更好：**不靠 thematic 下加识别规则，靠计划里写了行情腿就激活**。🔴 **两半残留都已写去引用方、不随本条埋掉**（[R7](../../CLAUDE.md)）：① **兜底路径仍会复发**（那 1/3 = 规划员没出计划 → 退回旧路由 → 金价没了·[G7 FINDINGS](../observations/rp-g7-e2e-20260827/FINDINGS.md) 自记「回到 BQ 那个病」）+ ② **本条自己预言的下游 schema 那半已兑现**（原文写「牵动 `ticker_payload` 及下游 schema·均按股票设计」—— A/B 里黄金成功那两跑 `bag=ticker`，期货数据装进为股票设计的袋子）⇒ **两条一并并入 `DEFECT-COMMODITY-AS-TICKER`**。⚠️ **五类资产只端到端验了黄金**（其余四类仅有「格式认得」层证据）—— 该缺口一并记在受让条目里 | 🔵 **2026-08-21 更新：地基半边已铺好，但本条不得据此关闭** —— seg1 G4 第一层已让行情源**认得**资产类代码（期货/指数/加密/汇率·`DEFECT-YF-TICKER-TRUNCATION` 同批 close），即「**拿到 `GC=F` 就能取对黄金价**」。**本条要的另一半没动**：主题型问题**根本不激活价格腿**，且「黄金」→`GC=F` 是**语义映射、只有规划员做得了**（任何正则都不行，且缺陷条目写死不得放宽正则）⇒ **归 G5**（计划决定选源）。⚠️ 原备注里「修法方向：thematic 下识别资产类 → 按资产代码激活价格腿」**已被 G5 的做法取代**（不再靠 thematic 下加识别，而是计划里写了行情条目就激活）。<br>2026-08-18 [PR #244](https://github.com/JunoChenZt/subagent-for-investment/pull/244) 冷审切出。**分类归对了，代价没人接**：#244 把大宗商品/指数/加密/汇率显式收编进 `thematic`（它们确实不是股票·收编本身对），但 thematic 路由只激活 fred/rss —— 这批资产**永久拿不到价格**；而 yfinance 实际支持 `GC=F`（黄金期货）/ `^GSPC`（标普）/ `BTC-USD` / `EURUSD=X`。**伤害已实证**：08-14 黄金跑唯一被 G5 涂改的数字正是**买入区间**（价位只能靠模型上网捡·#244 commit 自记）。**修法方向**：thematic 下识别资产类 → 按资产代码激活价格腿；牵动 `ticker_payload` 及下游 schema（均按股票设计），**范围大一档须独立设计**，别塞提示词。**预估**：设计 1 天 + 实现 1–2 天 〔轻条目〕|
| BR | 「问题 → 拉什么」的映射表**覆盖不全就静默走默认值**，且**零告警** | 🟡 | 未触发（**全事件型**：下次动 [`_SERIES_KEYWORDS`](../../src/committee/common_context/sources/fred_source.py) / e2e 再出现一次「答非所问的宏观数据进了引用清单」/ 用户明确要求） | 2026-08-18 seg1 提示词检阅实测切出（**单实例条目**：实例② 已于同日核代码证伪并撤）。🔵 **2026-08-21 seg1 G2 落地：「静默」那半已修**（认不出 → 明确失败 → 整条腿降级留痕），**「表拆不拆」那半随宏观安全网归 G5** ⇒ **不得据 G2 关闭**。**📍 2026-08-21 已由轻条目提为 §1 正文**（实测原文 / 三条边界 / G2 做到哪一步全文见正文）。**预估**：定语义 + 落地 半天 〔监视 src/committee/common_context/sources/fred_source.py〕 |
| BS | 引用清单把**三类信息混成一类** —— 答非所问的 / 当背景的 / 真对题的，下游分不出谁是谁 | 🟡 | ✅ **CLOSED 2026-09-24（close-by-completion·CRED.2.G5·用户当日裁·保留位置）** —— 引用身份已落（#317）；2.G5 全链 e2e 实测全链贯通、零误标：seg1 12 条身份逐条核对 · 分析师出处段带标 112 + 56 处 · 表③ 引表① 的 24 条事实全部继承正确（23 对题 / 1 背景）。⚠️ **本跑无噪音可标**（新闻没挂通用头条源、研报全过回筛）⇒「填充噪音不得标对题」只有 2.G4 回放 + 单测证据，用户裁按此关（[FINDINGS](../observations/cred-2-g5-e2e-20260923/FINDINGS.md) §3.4）。**重开** = e2e 里通用头条 / 无关研报被标「针对本问题」〔原触发条件：未触发（**全事件型**：下次动 [watermark](../../src/committee/common_context/watermark.py) / references 装配 / [rss_source](../../src/committee/common_context/sources/rss_source.py) feed 列表 / wisburg 取数 / e2e 出现一次「分析师拿无关引用当依据」/ 用户明确要求）〕 | 2026-08-18 seg1 外部信息质量实测切出（黄金跑·31 条**逐条读过**·相关率 **32%**：宏观 1 条 0 相关 / 新闻 10 条 0 相关 / 研报 20 条中 10 条对题）。三种源三种提问方式 ⇒ 到分析师眼里全是「7 条引用」，**无任何标记区分针对性 / 背景 / 无关**。🔁 **2026-08-20 订正**：原把"通用背景是设计意图"归在「谷歌写死搜 `financial markets`」上**归错了** —— 谷歌腿因"取满即停"从未执行、那 10 条全来自 MarketWatch。**📍 2026-08-20 已由轻条目提为 §1 正文**（口径警告 / 判定标准 / 逐源明细 / 修法方向全文见正文）。**预估**：设计半天 + 实现 1 天 〔监视 src/committee/common_context/watermark.py, src/committee/common_context/sources/rss_source.py, src/committee/common_context/sources/wisburg_source.py〕〔粗粒度：判据点的是水印与 references 装配那几段，这几份文件的任何改动都会喊〕 **📌 2026-09-23 D2 已裁（用户）= 加字段**：`Reference` 增 `relevance`（对题 / 背景 / 无关·默认空）·由回核层按 intent 结果填·落 CRED 2.G4（排 2.G0–2.G3 后·[设计 pass §3.2.4](../plans/CRED-可信度地基三簇-设计pass-2026-09-08.md)）·**判据不变·条目待 2.G4 合并后再议 close** **📌 09-23 2.G4 已合 main（#317 `75fa362`）**：身份按回核后定位填；顺带修「回核筛掉的研报仍进分析师正文」（主干 29 篇）；**待 2.G5 真跑后 close** |
| DEFECT-ANCHOR-FALSEPOS-HARDBLOCK | ~~出处绑错**首次改变决策产出**~~ **主缺陷已修（CRED.1.G4 合 `0e297ef`）**；**剩余项 = f16 类「推算比值挂原始计数编号」** | 🟡 | ~~未触发~~ **✋ 2026-09-10 用户裁「再留一轮」不 close**（够格按完成关，但剩余项靠**会出错的模型判断**接住、Q8 可见性刚上试用）。下次评估 = ~~复核员出现**第一个自然真阳性** / 簇 2 收口 / Q8 试用期结束~~ **〔2026-09-24 节点收口复查·用户裁「继续留着」〕**：「簇 2 收口」那一格 09-24 已到而当时漏评，节点收口补评 —— 09-10 起 6 跑里复核员被叫到 **1 次**（09-17 NVDA·「13 万」↔「130,000」量纲误报·判对·撤到存疑），**自然真阳性 0**、Q8 未响过 ⇒ 不关的理由（真错侧无自然样本）未变。**复查时点收窄为事件型**：复核员出现**第一个自然真阳性** / Q8 试用期结束（[retro CRED](../retro/S2/CRED_2026-09-24.md)）。原触发条件 (A)(B) 均已兑现〔📌 ~~2026-09-09 设计 pass 已出·等用户裁 D4~~ **D4 已裁 2026-09-10·实现已合 main `0e297ef`（PR [#286](https://github.com/JunoChenZt/subagent-for-investment/pull/286)）·条目仍开着**：设计 pass PR [#282](https://github.com/JunoChenZt/subagent-for-investment/pull/282) 已合 main `abda356` → [CRED-1.G4 设计 pass](../plans/CRED-1.G4-绑错判别力-设计pass-2026-09-09.md)。268 份探针：check① 硬拦路 **5 响 5 误报 0 真错**。**条目不 close** —— 落地在 D4 之后〕 | 2026-08-27 G7 全链跑实锤（`f60` 距选举 3 个月 ↔ 编号登记值 2026=年份）。四环根因链 + 候选处置见 §1 正文；endgame G6/G8 已记现象、该域封卷故**本条即独立立项**。DEFECT 族不占 lettered 配额 〔监视 src/committee/facts/exec_floor.py, src/committee/tools/number_stamp.py〕 |
| DEFECT-DEBATE-STALE-PRIOR | 辩论 R1 **设计性断粮** → 模型拿训练期旧行情当今天的数据，零闸门可见 | 🟡 | ✅ **CLOSED 2026-09-24（close-by-completion·CRED.3.G2·用户当日裁·保留位置）** —— 辩论数字 ↔ 本跑事实清单对账已上线（#320·D3 = B：归档 + 跑批记录 + 终局质检 Q9 WARN 试用）；3.G2 从 8 月那跑 seg7 续跑实测**该响的响、只响一处**（DXY 105 vs 99.1·trace / 归档 / Q9 三处一致），09-23 / 08-31 两份归档回放零条（[3.G2 FINDINGS](../observations/cred-3-g2-e2e-20260924/FINDINGS.md)）。条目原两条**改提示词**候选（R1 禁用记忆数字 / R3 补出处要求）本节点不做 → **挪至 [endgame §4 G8](number-provenance-endgame.md)**、触发条件随迁。**重开** = Q9 在试用期内漏掉一处经人工确认的旧行情，或误报多到读者不再看 Q9〔原触发条件：未触发（**全事件型**：下次动 [debate/prompts.py](../../src/committee/prompts/debate/prompts.py) 时 / 再出现一次辩论数值与本跑数据冲突——与 endgame G8 触发① 同源并读）〕 | 2026-08-27 G7 实锤（空头 R1「DXY 105 以上」「国库券 5%」= 训练期旧行情·同跑数据 99.1 / 3.63%）。连带：三轮出处章有无 = 提示词的精确镜像（R1 无从引 / R2"可引用" / R3 只字未提）。DEFECT 族不占 lettered 配额。🔵 **2026-08-31 两笔**：① **本跑未复现**（R1 数字与本跑真实数据全对得上·**但闸门仍是零**，不得据此 close）；② 🔴 **「精确镜像」措辞须收窄** —— R1/R2 两跑一致，但 **R3 同一轮多头 0 个、空头 6 个**，提示词解释不了同轮不一致（双方模型不同：deepseek-v4-pro vs gemini-2.5-pro，模型差异可能才是变量）。证据 [../observations/rp-g8-e2e-20260831/FINDINGS.md](../observations/rp-g8-e2e-20260831/FINDINGS.md) 〔监视 src/committee/prompts/debate/prompts.py〕 **📌 09-24 CRED.3.G1 已合 main（#320 `6bfde56`）**：辩论数字↔本跑事实清单对账进归档 + trace + 质检 Q9（WARN 试用）；主干回放标出 8 月 DXY 105；**3.G2 收口时核关闭条件** |
| DEFECT-GATE-NA-AS-PASS | 终局质检把「没查到」印成 PASS —— 计划被硬闸切除时 Q3/Q4 自动绿、理由还写错 | 🟡→✅ | ✅ **CLOSED 2026-09-09（close-by-completion·CRED.1.G1·PR [#283](https://github.com/JunoChenZt/subagent-for-investment/pull/283) 已合 main `fb6dcee`）** —— 原触发条件「下次动 `e2e_quality_gate.py` 时一并」已兑现，两条任务均落地：① Q3/Q4 改 `N/A` 档并分四成因（`no_plan` / `cut_by_gate` / `price_unavailable` / `empty_entry`·**判到数字层**）· ② `summary_line` 固定四段、n/a 永不并进 pass。⚠️ 合并前 review 抓到并修掉一个真 bug（判「填没填」用真假值 ⇒ `0` 占位符被读成没填、在册归档 FAIL→N/A），见下方 09-09 块 | 2026-08-27 G7 实锤（13/0/0 里 Q3/Q4 印 "no execution_plan (acceptable for HOLD)"·实为 fm 填了被闸切；Q5 "0% 错绑"只量 EVID-1 管道）。呈现改动非新检查、fail 面零变化。DEFECT 族不占 lettered 配额。🔴 **2026-08-31 第 2 次实例（N=1→N=2）**：13/0/0 里 **Q3/Q4 印「entry is null / 无 entry 可接受」而实为 fm 压根没填结构化价位**（按 ⑨ 段三态规则属第①态·应判「本跑无效」）；**Q5「0/18 错绑 0%」只量一条管道**，同跑第⑧段 67 条 `audit_notsure`、96% 精确数字未核全不在其量程。证据 [../observations/rp-g8-e2e-20260831/FINDINGS.md](../observations/rp-g8-e2e-20260831/FINDINGS.md) |
| BX | 行情格式表只认**美股 + 港股**（加四类资产），东京 / 伦敦 / 法兰克福 / 多伦多 / 首尔 / 孟买一律拒收 | 🟢 | 未触发（**全事件型**：下次动 [yfinance_source.py](../../src/committee/common_context/sources/yfinance_source.py) 的格式分类链 / 名录 `MARKETS` 时 · 用户明确提出要问非中港美市场的股票 · e2e 里出现一次外国股票腿被拒） | 2026-09-01 review 追问切出（用户裁「记账，先收口 PR」·**授权破例 #16**）。实测 `7203.T`（丰田）/ `VOD.L` / `SAP.DE` / `SHOP.TO` / `005930.KS` / `RELIANCE.NS` **全部判「认不出」→ 校验拒收**，而数据源本身支持这些市场。⚠️ **够得着但只有一条路**：本地名录 `MARKETS` 只有 CN/HK/US ⇒ 确认标的那条路解析不出外国码；但**规划员是模型、可以直接把 `7203.T` 写进计划**。⇒ 用户问丰田会走到「暂不可分析」，且拿到一句错的建议（见 `DEFECT-RETRY-ADVICE-FALSE`）。**任务** = 扩格式表 + 名录市场，须**逐市场实测**代码形态与真实返回（不是加几条正则就完），并同步资产类型词表。**为什么延后**：这是真功能不是修 bug，需实测数据与排期；且当前主线是中港美 〔监视 src/committee/common_context/sources/yfinance_source.py, src/committee/security_registry/〕〔粗粒度：判据点的是格式分类链与名录 `MARKETS`，该文件其余改动（如 `ad19c61` 改重试预算）会空喊〕 〔**2026-09-28 RDR-1.G2 连带**：早停「不支持」措辞里列的支持范围写死在 `price_gate_node._SUPPORTED_MARKETS_HINT`，BX 扩市场时**必须同步**那句，否则报告会把已支持的市场说成不支持〕 |
| BY | 讲**历史**的事实被当成「资料过期」—— 日期记的是事件发生时间，十年前的数据永远判过期 | 🟢 | 未触发（**全事件型**：下次动 [confidence.py](../../src/committee/facts/confidence.py) 的保鲜期表 / [base.py](../../src/committee/agents/base.py) 的 2a 复核清单或类型推断 `_guess_data_kind` 时 · CRED.2.G5 全链 e2e 跑完时（顺带数：复核清单里有几条其实是历史事实）· 用户明确要求） 〔**2026-09-24 · 2.G5 那一格已兑现**：复核清单 14 条里因过期入列 **1 条**（f35 一季度矿商成本·207 天·被当现值引用 = 边界例）、纯历史叙事 **0 条**（[FINDINGS](../observations/cred-2-g5-e2e-20260923/FINDINGS.md) §4）；该格此后不再是待触发项，其余触发条件照旧〕 | 2026-09-23 D1（other 400 → 180）落地后用户追问切出。**已核（非推断）**：事实的 `as_of` 对历史类陈述记的是**事件时间**（例：「1978–1980 金价 $217→$850」记 1980-12-01、「2018 下半年美光 $60→$30」记 2018-12-31）；主干 1039 条里超半年 87 条、多为此类。**不是 D1 引入的**：400 天下同样判过期，180 只多影响半年至 13 个月那段。**影响（今天）**：① 可信度 / 结论**几乎无**（那 87 条 0 条过审、本就「查不到」）；② **2a 联网复核清单**会把历史事实送去复核 = 花钱核历史；③ 出处表给历史出处打「过期」= 误导读者。**任务** = 让系统分清「讲历史」与「讲现状但资料旧」（后者必须仍判过期）——候选：按角色 / 句中明确过去年份 / 新增「历史」档，各有误判风险须设计。**为什么延后**：今天损失只在复核成本与展示，不碰结论；需单独设计 〔轻条目〕 〔监视 src/committee/facts/confidence.py, src/committee/agents/base.py〕〔粗粒度：base.py 很大，判据只点其中复核清单与类型推断两段，其余改动会空喊〕 |
| DEFECT-WISBURG-PADDING | 研报源**只排序不过滤**，填充率是我们请求方式的函数 —— 下游只有一把粗糙的文字筛子兜底 | 🟡 | 🔔 **已触发 2026-09-14**〔证据：判据点名的回核层 [verifier.py](../../src/committee/retrieval_plan/verifier.py) 于 `ad19c61` 新增 571 行且含研报处理，`8e0e5fe` 再改 13 行·**用户裁「先只订正账面、开工时机另议」**〕 · 原判据文字未改：未触发（**全事件型**：下次动 [wisburg_source.py](../../src/committee/common_context/sources/wisburg_source.py) / 回核层研报那段 [verifier.py](../../src/committee/retrieval_plan/verifier.py) 时 · e2e 再出现一次「研报腿被整条退货」或「明显跑题的研报进了引用」· BI 残留开工时一并） | 2026-09-01 review 切出（用户裁「本质是研报数据源的问题，分词松绑解决不了，之后单独做源优化」）。一手实测在[接口说明书 §1①](../infrastructure/seg1_retrieval/wisburg-mcp.md)：只传「黄金」20 条几乎全对题，**加近四天窗后 20 条只剩 4 条对题**（其余铜、锂、中国消费、澳洲贸易）——**不是窗稀释了相关性，是那个窗里本来就没有 20 条，于是拿别的补满**。⇒ 越限定 + 越要满页 = 填充越多，而这是**请求侧**的变量。**与 [BI](#bi-wisburg-只取研报标题全链无人读正文--半句话成了承重数字的依据2026-08-03-全链回归-e2e-findings-33-逐条过时立账) 不同源**（BI = 取深度/正文；本条 = 相关性/填充），不互相 supersede。DEFECT 族不占 lettered 配额 〔监视 src/committee/common_context/sources/wisburg_source.py, src/committee/retrieval_plan/verifier.py〕 |
| DEFECT-COMMODITY-AS-TICKER | 商品/指数/加密/汇率的行情腿被**当成个股数据**装袋 → 基本面分析师的两道护栏被绕过 | 🟡→✅ | ✅ **CLOSED 2026-09-03（close-by-completion·PR [#269](https://github.com/JunoChenZt/subagent-for-investment/pull/269) 已合 main `a7f2687`）**〔⚠️ 2026-09-08 字形订正：原文把 ✅ 埋在「未触发（…·✅ **CLOSED…**）」的括号里 —— 表头约定明写 ✅ 须顶格，否则读成活跃；原触发条件（下次动 `force_ticker_shape` 时 · e2e 里出现一次主题型问题的报告里有公司基本面式分析）已随 close 失效，保留于本注〕 | 2026-09-01 review 坐实、PR [#268](https://github.com/JunoChenZt/subagent-for-investment/pull/268) 合并时**未修**（用户看过修法说明后选择先合、未点头开工）。**机制**：判断装个股袋还是宏观袋**只看数据源名字**，不看这条腿要的是股票还是商品 ⇒ 问黄金时那条 `GC=F` 期货腿（planner prompt 自己的规范示例）把数据装进个股袋 → `_is_ticker_query` 为真 → 基本面分析师**同时**失去「超出你职责范围」提示（[base.py:950](../../src/committee/agents/base.py)）与自动 DATA_INSUFFICIENT 弃权（base.py:1315）⇒ 拿零基本面数据硬写公司基本面式分析。**修法（已查清）**= 改看这条腿**已核对过的资产类型**（`asset_kind`）而非源名：该字段在校验层由**代码格式**推出（`_classify_yf_format` → 调取数层真正在用的 `_market_of_ticker`，**不重写分类链**），规划员声称的值若与格式对不上**整条腿拒收** ⇒ 到装袋这步它已是查过账的事实、**不引入新判断者**；A 股源只收六位码本就只有股票。⚠️ 字段缺失时**退回今日行为**（按源名），保证只可能改善、不可能新错。**🔴 2026-09-02 受让 BQ 的两半残留**（BQ 当日 close-by-decision·用户裁「写去引用方、并进这条」）：① **兜底路径仍会复发 BQ 那个病** —— 规划员没出计划时退回旧路由，主题型资产类问题**又拿不到行情**（A/B 实测 1/3 跑如此·[G7 FINDINGS](../observations/rp-g7-e2e-20260827/FINDINGS.md) 自记「回到 BQ 那个病」）。⚠️ 这是**刻意的降级设计**、不是遗漏，但它意味着 BQ 描述的场景仍有一条活路 ⇒ 动兜底路由（`default_sources` / thematic 路由）时**必须一并想这件事**。② **BQ 自己预言的下游 schema 那半**（原文：「牵动 `ticker_payload` 及下游 schema·均按股票设计·范围大一档须独立设计」）**已兑现 = 本条主体**。③ **五类资产（黄金/原油/指数/加密/汇率）只端到端验了黄金**，其余四类仅有「格式认得」层证据（2026-09-01 实测 `CL=F`/`^GSPC`/`BTC-USD`/`EURUSD=X` 分类均正确）—— 修本条时**顺带补一类非黄金的全链跑**，别让「管道通」当成「都验过」。**📋 [交接单已备（2026-09-02）](../plans/DEFECT-COMMODITY-AS-TICKER-handoff-2026-09-02.md)** —— 修法已查清（含「谁做资产类型判断」的完整链条 + 五类资产实测对照表）、红线与验收判据齐备，**开新 session 可直接照做**。DEFECT 族不占 lettered 配额。**🔧 2026-09-02 修复已落地 = PR [#269](https://github.com/JunoChenZt/subagent-for-investment/pull/269)（已开·合并即 ✅ CLOSE）**：`leg_is_equity`/`intent_is_equity` 三处共用（装袋 / 名录核验 / `ensure_price_leg`）· 主链路守护 + 反向变异 4/4 KILLED · 全量 3925/0。**三条 BQ 残留交代**：② 本条主体已修；① 兜底路由 **显式 defer**（刻意降级设计·记入 `DEFECT-CTX-BAG-SHAPE` 登记项 1）；③ 非黄金全链跑排在段式 e2e 三跑（黄金 / NVDA / `^GSPC`）。开工时按第一性原理重定 seg1 身份为「规划员 + 资料员」→ 修法扩为两 PR，PR2 见 `DEFECT-CTX-BAG-SHAPE`；拆解 [seg1-planner-librarian-redesign-2026-09-02.md](../plans/seg1-planner-librarian-redesign-2026-09-02.md)。**✅ 2026-09-03 合 main `a7f2687`**（squash·分支已删·CI 九道全绿·合并前 review 已修 4 记 6 → `DEFECT-CTX-BAG-SHAPE` ⑨–⑭）；段式 e2e 三跑（黄金 / NVDA / ^GSPC）全过、无 ❌、重跑 0 次 |
| DEFECT-CTX-BAG-SHAPE | 资料夹「两个互斥格子」把多条腿的事实压成**一位全局标签**（这是不是个股问题）—— 资料员在替会议决定谁发言；**PR2 主体 ✅ 已合并**，本条继续持有剩余登记项 | 🟡 | 🔔 **已触发 2026-09-14**〔证据：判据点名的「`CommonContext` 两格子字段」已于 `415bc48` / `afa669b` 实际删除，两笔提交标题直接写着本条编号 ⇒ 本条其实一直在被推进，账面「未触发」是滞后·**用户裁「先只订正账面、开工时机另议」**〕 · 原判据文字未改：未触发（**全事件型**：PR [#269](https://github.com/JunoChenZt/subagent-for-investment/pull/269) 合并后开 `auto/CTX-LEGS` · 下次动 `CommonContext` 两格子字段 / `_is_ticker_query` / 价格闸读袋逻辑时 · 登记项各自触发见正文） | 2026-09-08 从本格拆出 §1 正文（原 7813 字·超 1000 上限·内容逐字未改）——详见 [§1 触发型条目](#1-触发型条目按条件触发不按时间) 里的同名条目 〔监视 src/committee/common_context/schema.py, src/committee/agents/base.py, src/committee/agents/price_gate_node.py〕 |
| DEFECT-D5-COUNT-AS-VALUE | 序列型引用登记成 `list(N)` 占位串 ⇒ 引用检查拿**条数**当数值去对账 —— 失配是噪音、命中是巧合，对这类引用**零判别力** | 🟢 | ✅ **CLOSED 2026-09-24（close-by-completion·CRED.2.G5·用户当日裁·保留位置）** —— 修法① 已落（#314）；2.G5 全链 e2e 两面都验到：`list(12)` / `list(10)` 占位值真实出现并被 6 条事实引用，8 份报告 D5 全 pass、审核判「非可比数值·不能当出处」、**没有拿条数去比**（[FINDINGS](../observations/cred-2-g5-e2e-20260923/FINDINGS.md) §3.1）。**重开** = e2e 里 D5 因序列引用误判 pass 而漏掉真错绑〔原触发条件：未触发（**全事件型**：下次动 [rules_d.py](../../src/committee/triage/rules_d.py) D5 那段 / [watermark.py](../../src/committee/common_context/watermark.py) 的 `list(N)` 登记法时 · e2e 里出现一次 D5 因序列引用**误判 pass** 而漏掉真错绑） 〔**2026-09-14 triage：不算触发**（用户裁）—— `163337a` 只给 D5 那段加了 4 行注释（本处 REF 正则与 `facts.stamp_families` 口径不同，迁共享实现会扩大 D3 fail 面，按验收标准 §4 须用户裁后再切），行为未变〕〕 | 2026-09-08 从本格拆出 §1 正文（原 1177 字·超 1000 上限·内容逐字未改）——详见 [§1 触发型条目](#1-触发型条目按条件触发不按时间) 里的同名条目 〔监视 src/committee/triage/rules_d.py, src/committee/common_context/watermark.py〕 **📌 2026-09-23 修法① 已实现并合 main（CRED.2.G1·#314 `c22976a`）**：`list(N)`/`dict(N)` 整族进 D5 跳过名单·fail 面不变·三态用例全跳过·真数值守护 fail 照旧；**条目不 close，待 2.G5 全链 e2e 佐证** |
| DEFECT-RETRY-ADVICE-FALSE | 取不到价时**一律叫用户"稍后重试"**，而真因可能是永远不会好的（市场不支持 / 代码形状不认） | 🟡 | ✅ **CLOSED 2026-09-28（close-by-completion·RDR-1.G2·保留位置）** —— 两种出口落地（措辞用户裁）+ 真跑丰田 7203.T 两次印出「不支持…重新运行不会改变这一结果」（[FINDINGS](../observations/rdr-1-g2-price-gate-20260928/FINDINGS.md)）；BX 开工时须同步支持范围提示（已记 BX 备注）· 此前账面：🔔 已触发 · **RDR-1.G2 已落地 2026-09-28（`97126db`·待 PR 合并后 close）**：校验层把「两个行情源都不认这个代码」写成 `PlanValidation.price_leg_unsupported`，价格闸只在每一只确认标的都不认时换「当前版本不支持…重新运行不会改变这一结果」（措辞用户裁）；其余原因旧措辞逐字不变；终局质检 N/A 成因 / 降级汇总 / 断点恢复三处同步；真跑丰田 7203.T 两次（[FINDINGS](../observations/rdr-1-g2-price-gate-20260928/FINDINGS.md)）· 此前账面：🔔 **已触发 2026-09-14**〔证据：判据本身是文件级（「下次动 price_gate_node.py 时」），该文件于 `415bc48` 实际改动·**用户裁「先只订正账面、开工时机另议」**〕 · 原判据文字未改：未触发（**全事件型**：下次动 [price_gate_node.py](../../src/committee/agents/price_gate_node.py) 时 · e2e / 生产里出现一次"重试也不可能好"却提示重试 · `DEFECT-YF-MARKET-COVERAGE` 开工时一并） | 2026-09-01 review 追问切出。早停结论写死一句「暂时取不到 X 的实时行情…**请稍后重试**」，但**永久性原因走的是同一条出口**：格式表不认这个市场（东京/伦敦/法兰克福…）、代码形状认不出 ⇒ 重试一万次也不会好。真实原因只进 `log.warning`，产物里查不到。**这是"不确定性诚实"那条线上的缺口**：把"我们不支持"说成"暂时不可用"，是给了用户一个假的可行动建议。修法方向 = 区分「取价失败·可重试」与「这个形状/市场我们不收·重试无用」两种出口措辞（**碰早停结论 = 承重件，须用户裁措辞边界**）。DEFECT 族不占 lettered 配额 〔轻条目〕 〔监视 src/committee/agents/price_gate_node.py〕 |
| BT | triage 的「打回能力」该盘点了 —— 唯一真打回源 6 月被有意拔掉、8 月起连续 4 跑全过 | 🟡 | ✅ **CLOSED 2026-09-01·close-by-completion**（盘点已做 + 用户裁「给 D1 装牙」·[全文](../observations/bt-triage-teeth-audit-20260901.md)） | 2026-08-27 G7 排查切出。已核一手：B3（唯一真 reject 源）06-24 #156 有意移除·其余非 pass 全是 C 类冷审（主观·历史仅 technical 两次）·规则文件 07-24 后零改动 ⇒ 连续全过≠规则被改松。任务=按历史归档统计每条规则真实开火数、裁要不要补牙。**用户 2026-08-27 授权破例**。🔴 **2026-08-31：触发条件已满足** —— 黄金全链跑 seg3 **8/8 全过 = 连续第 5 次**；同跑并给出直接证据：`fundamentals` 的 **D1 规则真 fail**（`raw contains 0 citations`）**而总判定仍 pass**（只挂 `D-class flag`）⇒ **规则响了也不改变结论**。✅ **CLOSED 2026-09-01·close-by-completion**：盘点已做（[全文](../observations/bt-triage-teeth-audit-20260901.md)）—— 9 份 tracked 归档 × 8 角色实测：**能触发返工的 A 类 432 次评估零开火、B1/B2 零开火**，唯一咬过的 B3 已于 06-24 [#156](https://github.com/JunoChenZt/subagent-for-investment/pull/156) 移除 ⇒ **移除后没有任何有牙规则曾开火**（比 BT 原文「剩下的看缘分」更严重）；而开火最多的 D 类 **38 次 0 次改判定**。**用户 2026-09-01 裁：给 D1 装牙**（零引用标记 → reject → 返工），其余 D 规则一字未改。⚠️ 接缝：D1 开火率 24% ⇒ 约 1.9 次返工/跑，若返工到顶仍不挂标会推高质检门 S3（≥2 即 FAIL）——**真红了降 D1 回 warning，不松 S3**。订正 BT 原文一处：「其余非 pass 全是 C 类」漏了 06-11 那次（实为 B4+D3） |
| BU | 「裁决/立账」落地没有回填义务 —— 真值源静默滞后；**踩坑 4 例**（08-27 两例 + 09-04 两例）· 手工演练成功 2 次 | 🟡 | **(B) ✅ 已兑现 2026-09-04** —— 收口文档新增 [§2.9.4 回填清单](workflow/06-dod-and-evidence.md)（8 格固定名单·留空即不合规·与 evidence 缺失同级承重）；**(A) 转为常驻要求**（每次裁决落地照 §2.9.4 走，不再是"事件型待办"）。🔒 **2026-09-04 用户已裁**：lint 粗检 **取消**（防不住"清单本身有盲区"这一形态）· 本条 **不 close**（留着攒 §2.9.4 是否真拦得住的数据点·活跃仍 15）| 2026-08-27 切出。例① 08-18 分类线裁决只活在 #244 提交记录、guide 未回填→08-27 白查+错判（已补）；例② BN 08-14 已立账、guide ⑦ 仍写「N≥3→提立」→08-27 照旧文本得出「N=2」错判（本笔回填）。与 R7 的规则接缝（裁决/立账不在其触发事件类别里）。**用户 2026-08-27 授权破例** 〔不可监视：(B) 已于 2026-09-04 兑现、(A) 转为常驻要求，已无事件型待办可撞〕 |
| BV | 人工确认路径的**取数失败在归档里没留痕** —— 人认的是计划、不是结果 | 🟡 | ✅ **CLOSED 2026-08-31·close-by-completion**（用户当日裁「改」→ 结果侧告警 `legs_empty` 落地：按 `source_routing` 的腿 ∖ 资料夹实有键求差集，**不分人工/自动一律进产物**；计划侧「人认过的不喊」**一字未改**。5 条守护测试 + 隔离式反向验证） | 2026-08-28 G5b 真人验收首跑实锤：人认过含金价的计划，`GC=F` 撞雅虎限流三次全空，`__degradation_notices__` 为 `None`，归档零留痕。自动确认路径**反而有**告警——不对称由设计「人认过的不喊」而来，但那条理由只覆盖「计划有没有问题」，不覆盖「货有没有到」。**用户 2026-08-28 授权破例** |
| BW | 段式跑指南没有**真人验收**这种跑法的位置 —— 硬规则与它直接冲突 | 🟢 | ✅ **CLOSED 2026-08-31·close-by-completion**（用户当日裁「改」→ [指南](../observations/e2e-runs/segmented-e2e-guide.md)「怎么跑」新增「⚙️ 唯一例外：真人验收跑」一节：界限声明 + 命令 + 四条纪律 + 立此格的理由。**原「必带 `--auto-confirm`」一字未改**，例外只覆盖「要验的就是交互闸本身」，并显式排除「懒得加 flag」） | 2026-08-28 切出。指南写「首段**必带** `--auto-confirm`，否则卡死等输入」，而真人验收**必须不带**（要的就是它停下来等人）。本次属明知故犯并在[验收归档](../observations/rp-g5b-human-20260828/ACCEPTANCE.md)标注，但指南本身无此例外 ⇒ 下一个人要么以为不带是错的、要么干脆不做真人验收。**改指南 = 放松一条硬规则，须显式裁**，故不自行改。**用户 2026-08-28 授权破例** |
| AF-residual | reports_block raw 注入降为按需（AF 的 deferred 尾巴） | 🟢 | 未触发（**全事件型**：下次动 `make_decision_node` 的 `reports_block` 注入时） | 2026-06-02 从 AF close 时拆出；判据已于 2026-08-11 从「随 AG/AH」改判为事件型（AG/AH 均已 close）。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） 〔监视 src/committee/agents/base.py〕〔粗粒度：判据点的是 `make_decision_node` 里 `reports_block` 注入那一段，而 base.py 很大、其余改动都会空喊〕 |
| DEFECT-A3-01 | prose_gate_status 与字段可信度信号不同源 —— 价位全抹自检缺失 | 🔴→✅ | ✅ **CLOSED 2026-06-23（close-by-completion·随 [#144](https://github.com/JunoChenZt/subagent-for-investment/pull/144) 合 main `5885fe7`·保留位置）** | 正文状态行 2026-06-23 起即标 ✅（已修 + e2e hot 验过），只是从未进本表。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-R10-01 | debate closing 阶段 key_claims 抽取缺失 | 🟠→✅ | ✅ **CLOSED 2026-06-23（close-by-completion·独立 PR [#153](https://github.com/JunoChenZt/subagent-for-investment/pull/153) 合 main `45de406`·保留位置）** | prompt-only 修法；hot 验过（bear closing key_claims baseline 0 → mine 3）。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-R10-02 | OBEY-2 未驳 dissent 反馈在决策已生成后才拼入 → 对决策层实质死代码 | 🟠→✅ | ✅ **CLOSED 2026-06-23（close-by-completion·随 [#144](https://github.com/JunoChenZt/subagent-for-investment/pull/144) 合 main `5885fe7`·保留位置）** | 三步已实现 + hot 验收达成。**残留 = cap-crowding 纯监控态**（仅当 cross_check 实测涨过 25 才真发生·非失效）。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-R5-01 | 步3 verify 入场门可被伪造的 source URL 骗过标 verified | 🔴→✅ | ✅ **CLOSED 2026-06-23（close-by-completion·随 [#144](https://github.com/JunoChenZt/subagent-for-investment/pull/144) 合 main `5885fe7`·保留位置）** | FindingConfidence 5 档漏斗 + web 域名印证门控；e2e 双档验证真堵（B 档 9 verified→0）。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-E2E-RESUME | 分段 e2e `--resume` 不干净跳过 —— 每段重跑 macro+triage | 🟠→✅ | ✅ **CLOSED 2026-06-24（close-by-completion·PR [#158](https://github.com/JunoChenZt/subagent-for-investment/pull/158) 合 main `af7b314`）** | harness 类缺陷、非 fm 节点。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-PROSE-GATE-SELF-ABRADE | prose-gate 误伤决策者自定行动数字（仓位数被当外部未核实数字抹） | 🟠→✅ | ✅ **CLOSED 2026-06-23（close-by-completion·随 [#144](https://github.com/JunoChenZt/subagent-for-investment/pull/144) 合 main `5885fe7`·保留位置）** | 曾升为 #144 第四道闸（fm 节点自身产物损坏撞北极星）。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-R5-02 | corroboration 印证池未按 fact scope —— 不相干 fact 靠整数巧合凑成 verified | 🔴→✅ | ✅ **CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— 支柱1 小修已合 main `3e8dd6f`（[#162](https://github.com/JunoChenZt/subagent-for-investment/pull/162)）；余下部分的前提「放开 web verified」已随 PR2 [#161](https://github.com/JunoChenZt/subagent-for-investment/pull/161) 关门放弃、flag 长期 OFF ⇒ 判据挂死信号。顺带消掉 endgame 分流表长期把本条列作「已 close」而 backlog 仍活跃的矛盾。 | 支柱2 = [DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮)，同一批待裁。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-R5-03 | 域名归一化无 eTLD+1 —— 同发行方子域被当两独立源 | 🟡 | 未触发（单列·或引入 public-suffix 依赖的其它需求出现时）。⚠️ 「单列」= 依赖有人主动排期，判据强度按 [§4.1](#41-新增-backlog-条目) 待复核 | 2026-06-25 AO PR2 严审发现；低暴露（需同发行方两子域同时上榜且各含一致数字）。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） 〔监视 pyproject.toml, requirements.txt〕〔粗粒度：只为接住「引入 public-suffix 依赖」这一子条件，任何依赖增删都会点名、多数是空喊；「单列」那半仍无人监视、属 §4.1 禁止形态、条目自标待复核〕 |
| T10 / #4 | claim/URL 级精确绑定（治过度打码） | 🔵→✅ | ✅ **CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— 它要治的「过度打码」已由 GATE-B 门重定义解决（涂 21→0·[#187](https://github.com/JunoChenZt/subagent-for-investment/pull/187)）⇒ 原目标消失；且判据「实测锚漏归因比例高」无任何在跑监测在量它（§4.1 禁止形态）。 | 2026-07-10 从已 close 的信源册 M1 剥离；实测 N=2（NVDA / 中际旭创·未过审 88% vs 89%）。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-PROSE-MASK-REF | 散文门「冤枉打码」—— 参考集选窄 + 二值门无中间档 | 🟠→✅ | ✅ **CLOSED 2026-07-16（close-by-completion·GATE-B 门重定义·PR [#187](https://github.com/JunoChenZt/subagent-for-investment/pull/187) 合 main `71da2d9`·保留位置）** | 收官时修法被 e2e 翻转成「只验主动认领的标」，涂 21→0。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-PROSE-MASK-ESCAPE | 散文门「逃逸洞」—— 打码只覆盖 3/11 字段·未核实数字原样印出 | 🔴→✅ | ✅ **CLOSED（close-by-completion·PR [#182](https://github.com/JunoChenZt/subagent-for-investment/pull/182) 合 main `10c00a9`）** | 补 `dissenting_views` + `override_justification` 两分支；另一逃逸面随 MASK.B1 砍步骤 6/7 一并消除。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-STAMP-MULTIBIND | 连写多标全绑到「最后一个数字」→ AI 核查误报 → 涂掉写对的数字 | 🟡 | 未触发（**全事件型**：`stamp-gate` 审计日志 / 后续 e2e 中**再现连写多标** → 届时加代码兜底） | 现由 prompt 硬约束压住（实测 多标 7→0 / mismatch 4→0）；用户 2026-07-17 裁 prompt-only 优先。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） 〔不可监视：判据等的是审计日志里再现连写多标，属运行时现象〕 |
| DEFECT-PROSE-MASK-INDEX | `_replace_in_decision` 按值遍历不认 location 下标 | 🟢→✅ | ✅ **CLOSED 2026-07-16（moot·MASK.GATE-B-fix `f6b3d0a` 改编辑表后串位隐患不复存在·保留位置）** | 正文病灶记录 point-in-time·不改。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-AUDIT-INTENT | 审计机制定位待厘清 ——「防抄错」被当「可信度/安全闸」判据 | 🔴→✅ | ✅ **CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— 议题已收口、判据已耗尽：主体 2026-07-03 定稿落 [audit-positioning.md](../pipeline/decision/audit-positioning.md)；目标态三检查 2026-07-14 用户拍板砍；两个触发前件（D1-ROOT 已实现 [#171](https://github.com/JunoChenZt/subagent-for-investment/pull/171)、M1 已 close）均已成为过去。 | 目标态三检查（AUDIT-3CHECK）已于 2026-07-14 用户拍彻底砍。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-D1-ROOT | gate 读展示表而非内源真值表 → 安全闸可被非-unverified 条目稀释 | 🔴→✅ | ✅ **CLOSED 2026-07-02（close-by-completion·PR [#171](https://github.com/JunoChenZt/subagent-for-investment/pull/171) 合 main `6f816a5`·保留位置）** | on-deck 看板 2026-07-16 即记「已实现·用户『已做完』清单未列」，但从未进本表。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| NAMING-EXTKREFS | `external_knowledge_refs` 命名误导（名带 external 实为内部 fact 编号） | 🟢→✅ | ✅ **CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— 处置②（docstring 警示）2026-07-02 已做；处置①（改名）= 动 checkpoint/archive 序列化的承重改动、换零行为收益 ⇒ 不值得单独做。**关掉零损失**：需要知道的已完整留在 [decision.py](../../src/committee/schemas/decision.py) 字段上方注释里（本次并补「条目已关·本注即真值源」一句）。重开 = 若本就要做 breaking schema 迁移时顺手改名。 | 纯命名/文档债·零行为影响。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-R5-04 | 印证语义层 —— 比数值不够，要比「带数字的内容」是否说同一件事 | 🟡→✅ | ✅ **CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— R5-02 的支柱2，父题目的（放开 web verified）已放弃。⚠️ 与 R5-02 失效方式不同：本条前件（建册铺完底座）**已成立**（M1 close 2026-07-10）—— 成立的是手段、消失的是目的。 | R5-02 的支柱2；2026-06-25 用户拍「分步」时另记。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-DSML-PARSE | deepseek 吐 DSML 标记不被 agent_loop 解析 → analyst 降级 | 🟡 | 未触发（止血已合 main `4f62cc9`·[#163](https://github.com/JunoChenZt/subagent-for-investment/pull/163)；**改进 A = 第二种非标准 tool-call 格式出现时** —— 今日唯一活口·合法事件型）。~~改进 B「待评估排期」~~ **❌ 2026-09-08 删除（用户裁）**：判据属 §4.1 禁止形态；命题「盯通用降级信号超阈告警」移交 [BK](#bk-静默降级可见化--系统悄悄降级时必须留痕2026-08-07-闸门矩阵第-2-层挂起) 承接 | 非 R5-02 引入·独立排。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） 〔不可监视：判据等的是跑批时出现第二种非标准工具调用格式，属运行时现象〕 |
| DEFECT-SEG2-FLAKY | seg2 并发研究段瞬时失败族 —— 三跑三坏·成因各异 | 🟠 | 未触发（**攒表驱动**：每次 seg2 失败记攒表一行〔这条随时在触发〕·**当前 N=3·五条升级判据全未达线**） | 「无声」机制已定位实测 = 裸 `CancelledError` 绕过沿途 5 层 `except Exception`、被 langgraph 并行分支静默吞掉。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） 〔不可监视：判据是攒表驱动，每次并发段失败记一行，由攒表承接〕 |
| DEFECT-FRED-SUBSTRING | 问「毛利率」拿到「联邦基金利率」—— 中文子串匹配的假阳性 | 🟡 | 未触发（**全事件型**：下次动 [`_SERIES_KEYWORDS`](../../src/committee/common_context/sources/fred_source.py) / `_resolve_series` 时） | **🔴 不得据 RP 节点关闭** —— [S2 §4.7.5](../roadmap/S2.md) 明写「分析师侧宏观工具仍在子串匹配·管道那半才解决」；与 BR 是两个病（BR = 撞不上就编一个 / 本条 = 撞上了但撞错）。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） 〔监视 src/committee/common_context/sources/fred_source.py, src/committee/common_context/sources/〕〔粗粒度：盯目录是为接住「接第二个宏观数据源」= 目录下新增文件；改既有别的数据源也会点名、会空喊〕 |
| DEFECT-EMPTY-AS-FAILURE | 「查了，没有」被报成「系统坏了」—— 成功的查询走了失败那条路 | 🟡→✅ | ✅ **CLOSED 2026-08-25（close-by-completion·PR [#266](https://github.com/JunoChenZt/subagent-for-investment/pull/266)）** | 宏观源两处空结果从 `raise ValueError` 改为返回体面的零。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） |
| DEFECT-NUMERIC-VALUE-NULL-BYPASSES-AUDIT4 | ~~「改动四」那道非可比出处闸在 `numeric_value is None` 时被绕过~~ **绕过半边已修**；剩余项 = pass0 提取器漏值 | 🟡 | 未触发（**剩余项·全事件型**：下次动 DS-0 提示词 / `FactInventoryItem.numeric_value` 抽取逻辑）。**「回头量提取率」这半 1.G5 已量一次·条目继续开着**（[记录](../observations/cred-1-g5-e2e-20260910/FINDINGS.md)）：主题型跑批 69 条事实真漏抽 **1 条**，不足以关剩余项、提取器仍未治 | 2026-08-25 由 [#266](https://github.com/JunoChenZt/subagent-for-investment/pull/266) 冷审拆出·同日完成前置核实。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） **🔴 09-09 回放翻案：原「活体 0」错，实为 35 条量值无值盖了 passed；G3 修法 ✅ 已合 main `e7fe42b`（[#284](https://github.com/JunoChenZt/subagent-for-investment/pull/284)·方案 C·复核五修·降 48/139）；条目不 close —— 剩余项 = pass0 提取器漏值·见正文 09-09 块·随簇 1 收口 1.G5 统一 close** 〔监视 src/committee/prompts/pass0_prompt.py, src/committee/schemas/pass0.py〕 |
| DEFECT-REVIEW-ERROR-AS-DATUM | 审查环节把一条故障提示数成「具体数据点」 | 🟡 | ~~未触发~~ **🚧 影子试用中（CRED.1.G2·D5）· 第 6 跑 / 地板 ≥3 · 分歧 0**〔2026-09-24 节点收口补数：09-10 起 6 跑（CRED.1.G5 · 09-17 gold / nvda · 09-18 nvda · CRED.2.G5 · CRED.3.G2）seg8 / seg9 `G1-shadow` **全部 0**；此前五跑读数没回填、计数停在「第 1 跑」，按归档补齐·[retro CRED](../retro/S2/CRED_2026-09-24.md)。⚠️ 零分歧 = 零个待坐实样本 ⇒ 按本条规则**仍不能升硬拦**〕：G1 两口径并算、分歧发 `G1-shadow`；升硬拦 = 试用期每次「本该拦」全部人工坐实零误拦（≥3 跑是地板·**三跑零分歧也不能升**）。1.G5 收口跑（[记录](../observations/cred-1-g5-e2e-20260910/FINDINGS.md)）零分歧、接线按预期工作 | 2026-08-20 由已 close 的 DEFECT-MCP-ISERROR 拆出·归档实锤。2026-09-08 补录进表（此前只有 §1 正文、表里无行·全族对检查脚本不可见） **🔄 09-09 实现·09-10 ✅ 已合 main `163337a`（PR [#285](https://github.com/JunoChenZt/subagent-for-investment/pull/285)·2026-09-10·分支已删）；R5 核到 main：错误形态在表①今天不可达（上游已堵）→ 新鲜跑批预期零分歧·见正文 09-09 块** 〔不可监视：判据是影子试用期的分歧数，由试用机制自己累计〕 |
| PRICE-V4PRO-CUTOVER | DeepSeek `deepseek-v4-pro` 转按 Flash 计费 —— 到期把单价改成 Flash 同价 | 🟡 | ✅ **CLOSED（2026-09-14·close-by-completion·PR [#293](https://github.com/JunoChenZt/subagent-for-investment/pull/293) 合 main `742f04a`）** —— 到期当天按登记时写好的处置改完：`deepseek-v4-pro` 四个数改成与 `deepseek-flash` 同价、`_PRICE_RECHECK_BY` 该条删除、2 条钉旧价的测试改新数、提醒机制的测试改锚合成条目（真实条目一删就会空转）。**立账时标「推断·未实证」的那句已实证**：09-14 16:15 跑批（切换点之后）回包仍报 `deepseek-v4-pro`（`by_model` 键就是它）⇒ 改的是这个键的价、不是靠回包改名。原状态：未触发（**全事件型·代码强制**：2026-09-14 12:00（北京）之后**任何一次跑批**，CLI / 段式 trace / 归档三处都会打出 `stale_price_models` 告警 → 撞见即做） | 〔轻条目〕**任务**：把 [`COST_PER_1M`](../../src/committee/token_usage.py) 里 `deepseek-v4-pro` 四个数改成与 `deepseek-flash` 同价（0.30 / 1.20 / 0.006 / 0.30），并删掉 `_PRICE_RECHECK_BY` 中该条。**为什么延后**：官方定价页写明 9-14 12:00 **之前**仍按现价计费，提前改＝那几天反过来低估。**不做的代价**：若回包仍报 `deepseek-v4-pro`（**推断·未实证**），每笔**高估 3~4 倍**且静默。**工作量**：~10 分钟（改 4 个数 + 删 1 条登记 + 改 2 条测试）。**时点**：2026-09-11 立。**来源**：PR [#288](https://github.com/JunoChenZt/subagent-for-investment/pull/288) review 第 3 条（可见性闸只认「名字不在表里」，认不出「价格过期」）。 〔不可监视：到期后每次跑批由代码自动告警，已有自己的闸、不必本闸重复〕 |
| API-EMPTY-QUERY | HTTP `/analyze` 入口不拦空 query —— CLI / MCP 拦、HTTP 放行，分析师在零资料下开会 | 🟢 | 未触发（全事件型：下次动 [server/api.py](../../src/committee/server/api.py) 的 `/analyze` 处理函数时 / 用户明确要求收口 API 入口契约时） | 〔轻条目〕2026-09-22 BK.6 量基线逐入口核出（[证据 §0.2](../observations/bk6-20260922/FINDINGS.md)）：`""` 到节点整段跳过取数、`"  "` 进规划员走兜底路由；今已有便条 `context_empty_query` 留痕、产物看得见。**任务**：入口拒空串 / 纯空白（422），与 CLI 口径一致。**为什么延后**：用户 09-22 裁 A「只留痕、拒空串另立」——入口契约是 API 面的事、不混进留痕批。**进入时点**：2026-09-22。**预估**：小（一处校验 + 一条测试）。〔监视 src/committee/server/api.py〕 |
| DEFECT-GATE-S4-NO-PRODUCER | 终局质检 S4「硬失败标记」读的记录**没有生产者** —— 恒报 0，与真实跑批无关 | 🟢 | ✅ **CLOSED 2026-09-28（close-by-completion·RDR-1.G1·处置 ①·保留位置）** —— S4 改调离线审计六项 detector、WARN 试用、detail 自报读了什么（`84102d4`）；三份黄金归档回放 0 违规（[回放读数](../observations/rdr-1-g0g1-gate-replay-20260928/output.md)）· 此前账面：🔔 **已触发 2026-09-28**〔本节点动了 `_s4_hard_fail_flags`〕· **RDR-1.G1 已落地（处置 ①·`84102d4e`·待 PR 合并后 close）**：S4 改调离线审计六项 detector、WARN 试用、detail 自报读了什么，脚本不在 → N/A；三份黄金归档回放 0 违规（[回放读数](../observations/rdr-1-g0g1-gate-replay-20260928/output.md)）· 原判据：未触发（全事件型：下次动 [e2e_quality_gate.py](../../src/committee/e2e_quality_gate.py) 的 `_s4_hard_fail_flags` 时 / 用户要求把 S1 voice 指标接回在线检查时） | 〔轻条目〕2026-09-28 S2 收口 G0 核实 PR-8c 时查出（[证据 §4](../observations/s2-close-pr8c-gate-verify-20260928/FINDINGS.md)）：S4 从 `enforcement_log` 找 rule ∈ {m4, m5, m6, m7, m8, m13} 的记录判 FAIL，而全仓 `src/` **无任何生产者**、tracked 归档**一条没有** ⇒ S4 恒 PASS。真实读数只能由离线脚本 [voice_guardrail_audit.py](../../scripts/eval/voice_guardrail_audit.py) 算（本次实算 21 份 0 违规）。**任务（候选·不预设）**：① S4 改为调离线审计的 hard-fail 函数（= 新增 fail 面·须先 WARN 试用·验收标准 §4）；② 删 S4 或改 N/A 并写明原因。⚠️ 这组指标是 S1 voice 时代的、今天判别力弱，改前先判留不留。**为什么延后**：用户 09-28 裁「登记待办」，S2 收口零代码。**进入时点**：2026-09-28。**预估**：小。〔监视 src/committee/e2e_quality_gate.py〕 |
| BZ | 命令行打印的最终报告**不是给人读的形态** —— 标题截半句、`{ref:fN}` 裸印、执行计划不显示、投票是一段 JSON、括注文本损坏 | 🟡 | 🔔 **已触发 2026-09-28**〔用户裁「现在就做第一档」〕· **RDR-1 G3 + G4 已落地（待 PR 合并）**：R1 标题上限 30→50 按标点截断（G3）· R5 括注归一（G3）· R2 上标 + 出处附录 / R3 执行计划表 / R4 投票表 + C6 弃权 / R6–R8 格式与「投资期限」（G4，[回放计数](../observations/rdr-1-g4-render-20260928/SUMMARY.md)）· **未关的那一格 = 「一次全链跑批的命令行输出人工通读」**（G5 用户裁暂缓）· 原判据：未触发（**全事件型**：下次动 [cli.py](../../src/committee/cli.py) 决策渲染段 / 下次动 [schemas/decision.py](../../src/committee/schemas/decision.py) 标题上限 / 下次全链跑批读最终报告再出现一次截断或裸标记 / S3 定命令行还是前端为主入口时 / 用户明确要求） | 2026-09-28 读者视角审读切出（[读者视角审读清单](../observations/s2-reader-review-20260928/CHECKLIST.md) R1–R8 + C6）。八项全是渲染层、不碰模型不碰检查语义：R1 标题 30 字硬截（三个标题全撞上限）· R2 `{ref:fN}` 裸印而附录不打印 · R3 执行计划不显示 · R4 投票汇总印 JSON · R5 括注折叠只认一种措辞致连写 / 错位 · R6–R8 数字格式 / 引号 / 「时间维度」字段名 · C6 弃权票混进中性。**任务**：按清单逐项改渲染 + 逐字用例。**为什么延后**：S2 已收口、S3 未开工，入口（命令行 / 前端）以哪个为主待定，避免只修一条路。**进入时点**：2026-09-28。**预估**：中（1–2 天）。〔监视 src/committee/cli.py, src/committee/schemas/decision.py〕 |
| CA | **内部机制名与「未核实」括注漏进用户面** —— 仓位写「受 R2 交叉质疑闸门约束」、止盈写「v11 verified」；括注提示词与代码两边都在写、谁是权威没定 | 🟡 | ✅ **CLOSED 2026-09-29（用户裁·按「报告面」口径 close·保留位置）** —— 关闭条件逐项：两条原则落文档 ✅（09-28 裁）· 提示词 / 渲染 / 守卫三处落地 ✅（RDR-1.G3 / G4 / Q13·PR #327）· 一次跑批输出**报告面**无内部编号 ✅ + 括注措辞单一 ✅ 18/18（[seg9 探针](../observations/rdr-1-ca-seg9-probe-20260929/FINDINGS.md)·渲染后机制名 0 / `VoteDirection.` 0）。🔒 **close 的是「报告面 0」**，不是「模型不写」：提示词禁令 1/1 跑仍滑落一次「26 条跨角色质疑」，靠渲染层兜底 —— 模型侧滑落进 RDR-1 节点 retro 观察项，不另立条目；**重开条件** = 全链跑批**报告面**再出现一次后台信息（编号 / 闸门名 / 字段名 / 跨角色计数）· 此前账面：🔔 已触发 · **seg9 断点探针 2026-09-29 已跑 · PR #328 ✅ 合 main `c195f617`**（合并前 review 8 = 修 3〔前缀不锚行首 / D3-β 尾巴译读者话 / 真拼接串全链靶测〕/ 留 5 次要项不立条目）（[FINDINGS](../observations/rdr-1-ca-seg9-probe-20260929/FINDINGS.md)·$1.20）：括注 **18/18 单一** ✅ · 编号类机制名 **0** ✅ · 模型仍写 1 次「26 条跨角色质疑」（禁令逐字点名仍滑落）→ 渲染层补兜底后**报告面 0**；真跑另抓出投票表枚举名 / 计数全 0 / 硬闸文案漏出三处（回放盲区·已修）· **close 待用户裁**（按「报告面 0」可关 / 按「模型不写」要再攒样本）· **RDR-1.G3 + G4 已合 main 2026-09-28（PR #327 `29761f49`）**：提示词加【对外行文规范】禁令段 + R7 / 审计闸门改唯一措辞「（未独立核实）」；`caveats.py` 成真值源（集合一种）；产出侧归一五种坏形态、门只补漏；标题上限 30→50（[FINDINGS](../observations/rdr-1-g3-prompt-caveats-20260928/FINDINGS.md)）· 渲染层剥机制名闭集 G4 已落地 · **未关的那一格 = 「一次全链跑批输出无内部编号、括注措辞单一」**（G5 用户裁暂缓；seg9 断点探针待 `--resume` 放行）· 此前账面：🔔 **已触发 2026-09-28**〔两条原则用户当日裁定：① 给人看的报告**一律不许出现后台信息**，只留结论和理由；② 「未核实」括注**模型贴、程序只补漏**（程序不再重复贴、只在模型漏贴时补）· **开工时机另议**〕· 原判据：（**全事件型**：~~用户裁两条原则后~~ ✅ 已裁 / 下次动 [prompts/decision/prompts.py](../../src/committee/prompts/decision/prompts.py) 输出规范段 / 下次动 [base.py](../../src/committee/agents/base.py) 括注折叠段 / 全链跑批再出现一次规则编号进用户面 / 用户明确要求） | 2026-09-28 读者视角审读切出（[读者视角审读清单](../observations/s2-reader-review-20260928/CHECKLIST.md) P1–P4 · P6 · C5）。**核到**：提示词规则本身叫「R2. 交叉质疑约束」，模型把编号抄进字段；提示词让模型自写「（未独立核实）」、代码的门再写一遍，折叠逻辑只认一种措辞 ⇒ 三种措辞并存、无说明。**任务**：定原则 → 提示词加禁令 + 输出规范（中文引号 / 日期写全 / 推算值不挂括注 / 仓位写法）→ 渲染层兜底剥离 → 括注措辞集合守卫。**为什么延后**：两条原则须用户裁；改基金经理提示词是承重变更。**进入时点**：2026-09-28。**预估**：中。〔监视 src/committee/prompts/decision/prompts.py, src/committee/agents/base.py〕〔粗粒度：base.py 只盯括注折叠那一段，其余改动会空喊〕 |
| CB | 决策文本**前后不一致与算术错误没有任何检查** —— 止损给两个数（4200 / 4313）、同一指标两个值（高盛年末 4900 / 4650）、盈亏比写 1.4:1 实算 1.86:1 | 🟡 | ✅ **CLOSED 2026-09-28（close-by-completion·RDR-1.G0·保留位置）** —— 关闭条件逐项：三条检查（Q10 / Q11 / Q12）先登记后落码 ✅ · 09-23 样本归档回放三处已知阳性全响 ✅ · CRED 三次黄金跑批回放（1.G5 零 WARN / 2.G5 = 样本本身 / 3.G2 计划被切 → N/A）零误报记录在案 ✅（[回放读数](../observations/rdr-1-g0g1-gate-replay-20260928/output.md)）· 配套提示词「换数须交代」随 G3 落地 ✅。一律 WARN 试用（≥3 跑实测后升档须用户裁）· 此前账面：🔔 **已触发 2026-09-28**〔用户裁「现在就做第一档」= 判据「用户明确要求」命中〕· **RDR-1.G0 已落地（分支 `auto/RDR-1` `efe2bae4`·待 PR 合并后按关闭条件 close）**：Q10 价位一致性 / Q11 可复算数字 / Q12 同机构多值（+ CA 的 Q13 括注集合）先登记后落码·一律 WARN 试用；09-23 归档回放三处已知阳性全响、CRED 1.G5 / 3.G2 回放零误报（[回放读数](../observations/rdr-1-g0g1-gate-replay-20260928/output.md)·[拆解](../plans/RDR-1-decomposition.md)）· 原判据：未触发（**全事件型**：下次动 [e2e_quality_gate.py](../../src/committee/e2e_quality_gate.py) / 全链跑批再出现一次同类〔散文与结构化价位不一致 / 同一机构同一指标两个值 / 可复算数字算错〕/ 用户明确要求） | 2026-09-28 读者视角审读切出（[读者视角审读清单](../observations/s2-reader-review-20260928/CHECKLIST.md) C1–C3）。**核到**：现有全部检查只核「数字有没有出处」（stamp-gate / claim_audits / Q3–Q5），没有一道核算术或一致性；终局 15 项全过。**任务**：三条新检查（价位一致性 / 可复算数字复算 / 同名指标多值），按 [验收判据表 §4](e2e-acceptance-standard.md) 先登记、**一律 WARN 试用**；配套提示词「换数须说明与分析师所用值的差异」。**为什么延后**：新检查须先登记维度与承重边界；S2 已收口。**进入时点**：2026-09-28。**预估**：中。〔监视 src/committee/e2e_quality_gate.py〕 |
| DEFECT-TRIAGE-REWORK-REASON-OPAQUE | 分诊打回原因**只记规则编号**（商品席「A-class reject: A4, A6」），事后读不出哪里不合格 | 🟢 | 未触发（全事件型：下次动 [triage/node.py](../../src/committee/triage/node.py) 打回记录生成处 / 再有一次打回需要事后排查原因时） | 〔轻条目〕2026-09-28 读者视角审读切出（[读者视角审读清单](../observations/s2-reader-review-20260928/CHECKLIST.md) C7）。**核到**：A 类打回文案在 [triage/node.py:57](../../src/committee/triage/node.py) 只拼规则编号，B 类（:77）带了 reason 文本，两者不一致；跑批记录自认「返工原因仍读不出（已知缺口）」。**任务**：A 类打回记录带各规则的 reason 文本，与 B 类同形。**为什么延后**：零阻断、纯可读性。**进入时点**：2026-09-28。**预估**：小。〔监视 src/committee/triage/node.py〕 |

> **📌 10 条活跃 · 上限内（2026-07-29·docs-audit 新增 AZ/BA）**〔⚠️ 08-03 顺手订正：本行原带「·最新」标记，但其下方已叠了四笔 07-31 更新 + 一笔 08-03 —— 同类 stale 状态标记，一并清掉。**当前最新 = 下方 📌 2026-08-03 banner（活跃 12）**〕：docs↔code 对齐审计（[#214](https://github.com/JunoChenZt/subagent-for-investment/pull/214)）撞出两项**不属于该 PR 边界**的活口，用户拍「都先不动·只记 backlog」→ 新增 **AZ**（🟢 活文档链接/模板同步小债：overview.md 52 处 root-relative 链接 + `.env.example` 缺 `COMMITTEE_REGISTRY_*`/`_CLASSIFY_TIMEOUT`）+ **BA**（🟡 名录 DB 未挂 volume·生产每次重建镜像清零·**修法需改 `.env.prod` = 红线·待用户裁**）。8+2=**10**·上限 15 内。**仍 0 条 🔴**。破例累计不变（新增条目在上限内·不占破例）。

> **📌 更新 2026-08-07（两笔·净额回到 12）：BH + AU 双 close → 12→**10**；同日加 BJ + BK → 10→**12**（上限 15·余 3）· **1 条 🔴（BC）** · 破例累计 11 不变**。
> - **close BH**（[#228](https://github.com/JunoChenZt/subagent-for-investment/pull/228) `c7306ac`）—— decision prompt 输出模板由字符串数组改对象数组 + `_coerce_triggers` 加固 + 前端 `[object Object]` 渲染修复。⚠️ **如实记账**：证到的是「结构上填得上」，「模型真的填」**无任何 e2e 数据**（修复后未跑 seg9）；残留判据已写去 [S4 §6.4 约束 5](../roadmap/S4.md)。
> - **close AU**（[#229](https://github.com/JunoChenZt/subagent-for-investment/pull/229) `e60c74f`）—— CI `backend` job 加 `3.10 + 3.11` matrix（地板 + 生产实跑版本双测）。
> - **加 BJ + BK**（均**挂起不做**）—— 来源 = [META 观察](../observations/meta-assume-mechanism-without-verify.md)「假设机制生效而不一手验证」实测 **N=8** 越过自定升级线（N≥5）→ 分层排期（方案 [gate-matrix-mechanization-2026-08-07](../plans/gate-matrix-mechanization-2026-08-07.md)）。**第 0 层已同轮交付**；本轮只登记第 1/2 层：**BJ**🟡 配置/一手来源读取机械化（CFG-READ）· **BK**🟡 静默降级可见化。⚠️ 第 0 层只闭合 8 个实例里的 **4 个**，另 4 个分属 BJ/BK **现在没被解决** —— META 的"升级"是**部分兑现**，不得读成已完成。
> - 两条触发条件**一律事件型**（守同轮刚立的 [§4.1 判据有效性约束](#41-新增-backlog-条目)）——**这是 §4.1 立规后第一次自我适用**。
> - 详细记账见 [§6 迭代历史](#6-迭代历史) 2026-08-07 两条。

> **📌 更新 2026-08-27（G7 全链跑排查系列登记·+3 DEFECT +2 lettered）：活跃 15 → 17。⚠️ 上限 15、超 2 —— 破例累计 11 → 13（用户 2026-08-27 明示「全都登记到 backlog」= 授权破例·配额满的现状已当面告知）。🔴 仍 0 条。`lint:active-count` 同步改 17。**
>
> **📌 更新 2026-08-28（G5b 真人验收切出·+2 lettered）：活跃 17 → 19。⚠️ 上限 15、超 4 —— 破例累计 13 → 15（用户 2026-08-28 明示「两条都登记」= 授权破例·配额满的现状已当面告知）。🔴 仍 0 条。`lint:active-count` 同步改 19。**
> 本轮**当场修掉、故不立条目**的：确认环把改好的计划扔了（已修 + 3 条守护测试 + 反向验证）· 出计划预算线 15s→40s（已落地）。**已修的不进 backlog。**
>
> **📌 更新 2026-08-31（例行过账 + BW/BV/BN 三 close + 全链跑落账）：活跃 19 → **16**、破例累计 **15 不变**、🔴 仍 0 条。**
>
> **📌 更新 2026-09-01（同日第 1 笔·BT 盘点做完并 close）：活跃 16 → **15 = 回到上限内**（BT close-by-completion）、破例累计 **15 不变**、`lint:active-count` 同步改 **15**、🔴 仍 0 条。**
> 盘点结论 + D1 装牙见 [bt-triage-teeth-audit-20260901](../observations/bt-triage-teeth-audit-20260901.md)。**⚠️ 活跃数自 2026-08-27 以来首次回到上限 15 之内。**
> 动了 **P**（判据 (B) 仍是死信号——缓存从未接进管道；判据 (A) 08-26 已响过而无人回看）+ 给 **BU** 加正面数据点。🆕 **新形态记账不立条目**：「backlog 条目自己的触发条件被满足了，却没人回来看这个条目」——再撞一次即提立。其余 15 条触发条件均未满足。
>
> **📌 更新 2026-09-01（同日第 2 笔·PR [#268](https://github.com/JunoChenZt/subagent-for-investment/pull/268) review 首批七修落地）：新增 **1 条 DEFECT**（`DEFECT-WISBURG-PADDING`）、**lettered 活跃 15 不变**、破例累计 **15 不变**、🔴 仍 0 条。**
> 起因：review 查出研报回筛对不带空格的中文整句失效（对题研报被整批筛空 + 误删缓存），修法是改用共用中文分词
> ⇒ **放宽回筛容差属 [§2.7 Q5](workflow/05-brake-self-check.md)，已上升并获用户裁准**。
> 🔑 **用户当场把问题抬高了一层**：「本质上是研报数据源的问题，不是靠分词的松绑可以解决的」——
> 据此立本条，记的是**请求侧制造填充货**这个根因（[接口说明书](../infrastructure/seg1_retrieval/wisburg-mcp.md)实测：加时间窗后 20 条只剩 4 条对题），
> 而非那把筛子。⚠️ **不与 [BI](#bi-wisburg-只取研报标题全链无人读正文--半句话成了承重数字的依据2026-08-03-全链回归-e2e-findings-33-逐条过时立账) 合并**（BI = 取深度，本条 = 相关性）。
>
> **📌 更新 2026-09-01（同日第 3 笔·PR [#268](https://github.com/JunoChenZt/subagent-for-investment/pull/268) review 收口）：活跃 15 → **16**（+**BX**）、破例累计 **15 → 16**、另立 **1 条 DEFECT**（不占 lettered）、`lint:active-count` 同步改 **16**、🔴 仍 0 条。**
> ⚠️ **上限 15、超 1 —— 用户 2026-09-01 明示「两个都记账」= 授权破例 #16**（配额满的现状已当面告知）。
> 起因：用户追问「那如果认不出怎么办」，逼出行情格式表的真实边界 ——
> 实测 `7203.T`/`VOD.L`/`SAP.DE`/`SHOP.TO`/`005930.KS`/`RELIANCE.NS` **全被拒收**，
> 而数据源本身支持这些市场。⇒ **BX**（扩格式表 + 名录市场·真功能须逐市场实测）
> + **`DEFECT-RETRY-ADVICE-FALSE`**（永久性原因走同一条出口、被说成"请稍后重试"，
> 给了用户一个假的可行动建议 —— "不确定性诚实"线上的缺口）。**两条要一起读。**
>
> **📌 更新 2026-09-02（同日第 1 笔·PR [#268](https://github.com/JunoChenZt/subagent-for-investment/pull/268) ✅ 已合 main `ad19c61`）：lettered 活跃 **16 不变**、破例累计 **16 不变**、补立 **1 条 DEFECT**（不占 lettered）、🔴 仍 0 条。**
> 🔑 **CI 翻案**：PR 描述原写「因账单失效跑不起来·以本地为据」——收口时**九道全部真跑通过**，不再是本地为据。
> 🔴 **补立 `DEFECT-COMMODITY-AS-TICKER`**：review 坐实 16 条、合并时已修 13 记账 3，
> 但「商品行情腿装进个股袋」**既没修也没记账**（修法已查清、只差点头，用户选择先合）
> ⇒ **PR 一合它就没家了**，合并后立即补账。**形态记账**：「坐实但未修的 finding
> 在 PR 合并时没有强制落账义务」——本次靠执行体自己想起来，再撞一次即提立。
>
> **📌 更新 2026-09-29（第 1 笔·⭐ 当前最新·**CA ✅ CLOSED（用户裁·按「报告面」口径）+ seg9 断点探针 PR [#328](https://github.com/JunoChenZt/subagent-for-investment/pull/328) ✅ 合 main `c195f617`**·落账纯文档直接进 main）**：配额族 **10 → 9**（CA close·上限 15 余 6）· 非配额族 **13 不变** · 破例累计 **16 不变**、🔴 0；`lint:active-count` 同步改 **9**。上方 09-28 第 5 笔的「⭐ 当前最新」标**同笔清掉**。
> - **探针读数**（[FINDINGS](../observations/rdr-1-ca-seg9-probe-20260929/FINDINGS.md)·$1.20）：括注 18/18 单一 · 编号类机制名 0 · 模型仍写 1 次「26 条跨角色质疑」→ 渲染兜底后**报告面 0** · 终局质检 16/0/0/4。真跑抓出三处回放盲区（投票枚举对象印 `VoteDirection.X` + 计数全 0 / 硬闸系统文案 / 跨角色计数）已修。
> - **合并前 review（[§2.11.9](workflow/08-retro-node-and-pr.md) 对账）**：8 条 = **修 3 + 记账 0 + 不做 5**（修：hard block 前缀不锚行首〔两闸同响拼接串第二段漏出〕/ D3-β 尾巴「触发原因：{messages}」G1-G5 原文译读者话 / 靶测改用 risk_gate 真函数拼接串走全链 `02a89a8b`；不做 5 = 次要项·记在 CA 正文 close 块，报告面再漏一次即重开）。
> - **同日追加**：用户裁「留的 5 条也修掉」→ PR [#329](https://github.com/JunoChenZt/subagent-for-investment/pull/329)（分支 `auto/RDR-1-review-leftovers`）：5 = 修 5 + 0 + 0，含根因修（`_build_result` 六处 `mode="json"`·归档落盘内容不变）；上一行「不做 5」由此清零。
> - **关了什么 / 留了什么**：**CA ✅**（用户裁「按报告面口径」：原则①的落点是报告；「模型不写」不是关闭条件、进 RDR-1 retro 观察项）· **BZ 不关**（本探针计划被切、「通读一份完整报告」那一格看不到）。
> - **裁决回填清单（[§2.9.4](workflow/06-dod-and-evidence.md) 八格）**：① CA 正文 close 块 + 一览表行 ✅ · ② 引用方：[RDR-1 拆解](../plans/RDR-1-decomposition.md) 节点状态行 ✅ / seg9 探针 FINDINGS §5 裁决行 ✅ · ③ 跑批指南 N/A · ④ 验收判据表 N/A（未增减检查）· ⑤ 观察点表 N/A（模型侧滑落进节点 retro）· ⑥ 代码 docstring N/A（引用的是条目来源、非状态）· ⑦ [S3 §0.2 A6](../roadmap/S3.md) 状态 ✅ · ⑧ memory ✅。
>
> **📌 更新 2026-09-28（第 5 笔〔⚠️ 09-29 第 1 笔顺手清掉本行原「⭐ 当前最新」标〕·**RDR-1 节点：backlog 第一档四条落地（G0–G4）**·PR [#327](https://github.com/JunoChenZt/subagent-for-investment/pull/327) ✅ 合 main `29761f49`·分支已删）**：配额族 **11 → 10**（CB close）· 非配额族 **15 → 13**（`DEFECT-GATE-S4-NO-PRODUCER` / `DEFECT-RETRY-ADVICE-FALSE` close）· 破例累计 **16 不变**。**🔴 仍 0 条**。
> - **合并前 review（[§2.11.9](workflow/08-retro-node-and-pr.md) 对账）**：high-effort 10 条坐实 = **修 10 + 记账 0 + 不做 0**（`d278da35` 前三条：名录查无此码不算「市场不支持」/ 渲染器不劈中文年月日、紧贴汉字的 ISO 日期不当区间 / 盈亏比复算按决策方向定目标与止损；`7f95ca1f` 余六条：早停措辞与质检判据同源 `price_unavailable_wording.py` / 审计脚本载入失败落 N/A / Q10 不比移动止损 / Q13 残缺形按左邻判 / 机制名闭集去重 / 括注归一与折叠分开留痕）。靶测 [test_rdr1_review_fixes.py](../../tests/test_rdr1_review_fixes.py)。
> - **做了什么**（[拆解](../plans/RDR-1-decomposition.md)·用户当日确认·G5 全链验收裁暂缓）：G0 终局质检 +Q10–Q13（散文↔计划价位 / 可复算数字 / 同机构多值 / 括注措辞集合·全 WARN 试用·前提空 → N/A）· G1 S4 改接离线审计（两个多月恒报 0 的空检查）· G2 价格闸早停分「可重试 / 不支持该市场」（丰田 7203.T 真跑两次）· G3 决策提示词对外行文规范 + 括注归一 + 标题上限 30→50 · G4 命令行报告重排（执行计划表 / 上标 + 出处 / 投票表含弃权 / 剥机制名闭集）。
> - **关了什么 / 留了什么**：CB ✅（回放三处全响 + 对照零误报）· 两条 DEFECT ✅ · **BZ / CA 不关** —— 各差「一次全链跑批」那一格（G5 暂缓）。
> - **裁决回填清单（[§2.9.4](workflow/06-dod-and-evidence.md) 八格）**：① 五条条目行 ✅ · ② 引用方：BX 备注记「支持范围提示须同步」✅ · ③ gate 清单（Q10–Q13 / S4 / D1 行 + 演进）✅ · ④ 验收判据表（维度 1 / 维度 4 表 + 承重总表 + 演进）✅ · ⑤ 观察点表 N/A（新 observe 进各 goal FINDINGS，节点 retro 汇总）· ⑥ 代码 docstring ✅ · ⑦ [S3 §0.2 A6](../roadmap/S3.md) 状态 ✅ · ⑧ memory ✅。
> - **证据**：[G0/G1 回放](../observations/rdr-1-g0g1-gate-replay-20260928/output.md) · [G2 真跑](../observations/rdr-1-g2-price-gate-20260928/FINDINGS.md) · [G3](../observations/rdr-1-g3-prompt-caveats-20260928/FINDINGS.md) · [G4 渲染回放](../observations/rdr-1-g4-render-20260928/SUMMARY.md)。
>
> **📌 更新 2026-09-28（第 4 笔〔⚠️ 同日第 5 笔顺手清掉本行原「⭐ 当前最新」标〕·**CA 两条原则用户裁定**·纯文档直接进 main）：三项条目数**全不变**（配额族 11 / 非配额族 15 / 破例 16）、🔴 0。上方第 3 笔的「⭐ 当前最新」标**同笔清掉**。
> - **裁了什么**：① 给人看的报告**一律不许出现后台信息**，只留结论和理由；② 「未核实」括注**模型贴、程序只补漏**。CA 的触发条件「用户裁两条原则后」由此兑现 → 账面改「已触发」，**开工时机另议**（§4.2 三选一待用户）。
> - **回填清单（§2.9.4 八格）**：① CA 正文 + 一览表行 ✅ · ②–⑦ N/A（原则落实到提示词 / 渲染 / 守卫在 CA 开工时做；验收判据表届时登记）· ⑧ memory ✅。
>
> **📌 更新 2026-09-28（第 3 笔〔⚠️ 同日第 4 笔顺手清掉本行原「⭐ 当前最新」标〕·**S2 读者视角审读立账：+BZ / CA / CB + 1 条 DEFECT 轻条目**·纯文档直接进 main）：配额族 **8 → 11**（上限 15 余 4）/ 非配额族 **14 → 15** / 破例 **16 不变**、🔴 0；`lint:active-count` 同步改 **11**、`lint:active-other-count` 改 **15**。上方第 2 笔的「⭐ 当前最新」标**同笔清掉**。
> - **起因**：S2 收口后用户要求「从头到尾再看一遍」。以 [cred-2-g5 黄金全链跑批](../observations/cred-2-g5-e2e-20260923/FINDINGS.md)（09-23 · 含簇 2 改动 · **不含**簇 3 #320）为样本，按「基金经理拿到命令行报告从头读」的视角逐段通读 → [读者视角审读清单](../observations/s2-reader-review-20260928/CHECKLIST.md)（22 条·按改渲染 / 改提示词 / 改检查归类）+ [可视化审读页](https://claude.ai/artifact/UgNka2HQKRUQvtgwaEqTe3)。**终局质检 15 项全过，而清单里没有一条在这 15 项覆盖面内** —— 检查视角与读者视角错位。
> - **立了什么**：**BZ** 命令行最终报告不是给人读的形态（渲染层 8 项）· **CA** 内部机制名与「未核实」括注漏进用户面、括注谁是权威没定（提示词层 6 项·**两条原则须用户裁**）· **CB** 决策文本前后不一致与算术错误无任何检查（止损两个数 / 同一指标两个值 / 盈亏比算错·新检查 WARN 试用）· `DEFECT-TRIAGE-REWORK-REASON-OPAQUE`（分诊打回只记规则编号·轻条目）。清单里 C4 / C8 只记不立（事件型再撞一次再说）。
> - **裁决回填清单（[§2.9.4](workflow/06-dod-and-evidence.md) 八格）**：① 四条条目正文 + 一览表行 ✅ · ② 引用该结论的其它条目 N/A（新立·无人引用）· ③ 跑批指南 N/A · ④ 验收判据表 N/A（CB 开工时先登记再动码）· ⑤ 观察点表 N/A · ⑥ 代码注释 N/A · ⑦ [S3 §0.2 移交清单](../roadmap/S3.md) 加 A6 ✅ · ⑧ memory ✅。
> - **样本局限**：一次跑批；哪些稳定复现要第二份报告才能分。命令行以外的入口（网页前端）S2 从没跑过。
>
> **📌 更新 2026-09-28（第 2 笔〔⚠️ 同日第 3 笔顺手清掉本行原「⭐ 当前最新」标〕·**S2 收口 G1–G3：坑表审视 · 归档规则 · 收口报告 · O CLOSED**·PR [#326](https://github.com/JunoChenZt/subagent-for-investment/pull/326) ✅ 合 main `db7ae1f`·CI 全过〔lint / backend 3.10 + 3.11 / secret-scan〕）：配额族 **9 → 8**（O close-by-completion）/ 非配额族 **14 不变** / 破例 **16 不变**、🔴 0；`lint:active-count` 同步改 **8**。上方第 1 笔的「⭐ 当前最新」标**同笔清掉**。
> - **S2 ✅ 已收口**（[收口报告](../observations/s2-close-report-2026-09-28.md)）：S2.3「有条件通过」的 22 条附带条件逐条有去处；移交 S3 清单写进 [S3.md §0.2](../roadmap/S3.md#02-s2-移交清单2026-09-28-s2-收口)；活跃待办无一阻塞 S3。
> - **坑表 S2 结束审视**（[审视](../observations/s2-close-pitfalls-review-20260928.md)·用户裁三项全按建议）：退役 9 / 改 mitigated 8 / 订正过期事实 6。
> - **O ✅ CLOSED**：归档 = 索引式、文件不搬家（[README](../archive/README.md) · [S2 索引](../archive/S2.md)）。
> - **以 S2 结束为触发条件的其它条目**：宽 grep 核过，**无**。

> **📌 更新 2026-09-28（第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标〕·**S2 收口 G0：PR-8c 结项 + 登记 S4 空过**·节点分支 `auto/s2-close-g0`）：配额族 **9 不变** / 非配额族 **13 → 14**（+`DEFECT-GATE-S4-NO-PRODUCER`）/ 破例 **16 不变**、🔴 0；`lint:active-other-count` 同步改。上方 09-24 第 4 笔的「⭐ 当前最新」标**同笔清掉**。
> - **PR-8c observation gate ✅ MET**（用户 09-28 裁 A：按判据原文把全新九段验证跑计入）：122 天 · 11 / 8 runs · hard-fail 0 · 共享指标全 100%（[核实](../observations/s2-close-pr8c-gate-verify-20260928/FINDINGS.md)）；run-counter 与 S2 两处状态同步改。
> - **新立 `DEFECT-GATE-S4-NO-PRODUCER`**（用户裁「登记待办」）：终局质检 S4 读的记录全仓无生产者、恒报 0。

> **📌 更新 2026-09-24（第 4 笔〔⚠️ 09-28 第 1 笔顺手清掉本行原「⭐ 当前最新」标〕·**CRED 节点收口**·PR [#322](https://github.com/JunoChenZt/subagent-for-investment/pull/322) ✅ 合 main `6c0a44c`·CI 全过〔lint / backend 3.10 + 3.11 / secret-scan〕）：**三项条目数全不变**（配额族 **9** / 非配额族 **13** / 破例 **16**）、🔴 0；`lint:` 计数不动。上方同日第 3 笔的「⭐ 当前最新」标**同笔清掉**。
> - **补数**：`DEFECT-REVIEW-ERROR-AS-DATUM` 影子试用计数 第 1 跑 → **第 6 跑**（全部零分歧·此前五跑没回填）；零分歧仍不能升硬拦。
> - **补评（我漏的）**：`DEFECT-ANCHOR-FALSEPOS-HARDBLOCK` 的复查时点「簇 2 收口」09-24 已到未评，节点收口补评 → 用户裁**继续留着**、复查时点收窄为事件型（自然真阳性 / Q8 试用期结束）。
> - **节点复盘** [retro CRED](../retro/S2/CRED_2026-09-24.md)：CRED 九条里关 6、留 3（影子试用 / 提取器剩余项 / 用户裁再留），均有触发条件。

> **📌 更新 2026-09-24（第 3 笔〔⚠️ 同日第 4 笔顺手清掉本行原「⭐ 当前最新」标〕·**CRED.3.G2 簇 3 收口：e2e 佐证 + 关 1 条**·PR [#321](https://github.com/JunoChenZt/subagent-for-investment/pull/321) ✅ 合 main `dd58031`·CI 全过〔lint / backend 3.10 + 3.11 / secret-scan〕）：配额族 **9 不变** / 非配额族 **14 → 13**（close `DEFECT-DEBATE-STALE-PRIOR`）/ 破例 **16 不变**、🔴 0；`lint:active-other-count` 同步改。上方同日第 2 笔的「⭐ 当前最新」标**同笔清掉**。
> - **跑了什么**：8 月那跑 seg7 断点（R6·取自 main）续跑 seg8 + seg9 → 检测在真实流水线里恰标出那处 DXY 105；终局 **13 pass / 1 warn（Q9）/ 0 fail / 2 n/a**。证据 [3.G2 FINDINGS](../observations/cred-3-g2-e2e-20260924/FINDINGS.md)。
> - **裁了什么（用户 2026-09-24）**：条目 close，两条改提示词候选挪到 endgame §4 G8。
> - **顺带**：旧断点在今天跑，金价出处已过 29 天 → 审核记过期、check③ 切计划降 HOLD = CRED.2.G3「该标就标」首次实跑证据（BP 已关·按 Q6 不回写，记在 FINDINGS §4 与 S2 2.G5 行前向注）。

> **📌 更新 2026-09-24（第 2 笔〔⚠️ 同日第 3 笔顺手清掉本行原「⭐ 当前最新」标〕·**CRED.3.G1 合 main 落账**·PR [#320](https://github.com/JunoChenZt/subagent-for-investment/pull/320) ✅ 合 main `6bfde56`·CI 全过〔lint / backend 3.10 + 3.11 / docker / secret-scan〕·纯文档直接进 main）：**三项条目数全不变**（配额族 **9** / 非配额族 **14** / 破例 **16**）、🔴 0；`lint:active-count` 不动。上方同日第 1 笔的「⭐ 当前最新」标**同笔清掉**。
> - **3.G1 落地**：辩论数字 ↔ 本跑事实清单同指标对账（D3 = B）→ 归档 `debate_sight` + 段式 trace 第⑧/⑨段 + 终局质检 **Q9 WARN 试用**；主干回放恰标出 8 月那处 DXY 105、其余零标。合并前 review 补一处：同一数字前两个别名时，被第一个别名滤掉的数字会被第二个别名重配漏过过滤（「对方……美元指数（DXY）维持在105」误标）→ 改为先登记再过滤，靶测 30 → 32。
> - **`DEFECT-DEBATE-STALE-PRIOR` 不 close**：3.G2 收口时逐条核关闭条件（「该响」一面以 8 月那跑归档回放为正式证据）。**下一棒**：3.G2。

> **📌 更新 2026-09-24（第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标〕·**CRED.2.G5 簇 2 收口：全链 e2e + 关 4 条**·PR [#318](https://github.com/JunoChenZt/subagent-for-investment/pull/318) ✅ 合 main `069ce14`·CI 全过〔lint / backend 3.10 + 3.11 / secret-scan〕）：配额族 **12 → 9**（close BO / BP / BS）/ 非配额族 **15 → 14**（close `DEFECT-D5-COUNT-AS-VALUE`）/ 破例 **16 不变**、🔴 0；两个 `lint:` 计数同步改。上方 09-23 第 6 笔的「⭐ 当前最新」标**同笔清掉**。
> - **跑了什么**：问句「黄金会怎么走」全新 run 九段逐段放行，终局质检 **15 / 0 / 0**、段间全过、降级 1 处（偶发网络·与簇 2 无关）。证据 [FINDINGS](../observations/cred-2-g5-e2e-20260923/FINDINGS.md)。
> - **裁了什么（用户 2026-09-24）**：四条**全关**。⚠️ BP / BS 本跑只验到「不该标时不乱标」——没有过期出处、没有噪音可标；「该标就标」那一面按 2.G3 / 2.G4 回放 + 单测认定。各条关闭格写明了重开条件。
> - **BY**：2.G5 那一格兑现 = 复核清单里纯历史叙事 0 条 / 边界 1 条；条目仍开着。
> - **另记**：空头辩论正文再次编造编号（`REF#C-005`·表① 无 C 族）→ 按封卷规矩只登记进 [endgame §4](number-provenance-endgame.md) G8 之后，不立条目。

> **📌 更新 2026-09-23（第 6 笔〔⚠️ 09-24 第 1 笔顺手清掉本行原「⭐ 当前最新」标〕·**CRED.2.G4 合 main 落账**·PR [#317](https://github.com/JunoChenZt/subagent-for-investment/pull/317) ✅ 合 main `75fa362`·CI 全过〔lint / backend 3.10 + 3.11 / docker / secret-scan〕·纯文档直接进 main）：**三项条目数全不变**（配额族 **12** / 非配额族 **15** / 破例 **16**）、🔴 0；`lint:active-count` 不动。上方同日第 5 笔的「⭐ 当前最新」标**同笔清掉**。
> - **2.G4 落地**：引用身份按回核后定位填（对题 / 背景 / 未标注）；新闻混进通用头条整条标背景；表③ 事实行保守继承；顺带修「回核筛掉的研报仍进分析师正文」（主干 29 篇）。合并前 review 补一处：事实所引编号在表① 查不到时原先被跳过、会让整条冒充对题 → 改为按未标注算（靶测 18 → 22）。**BS 不 close**（随 2.G5 真跑佐证）。
> - **R7 复扫**：`PR 待合` / `auto/cred-2-g4` live 处清零。**下一棒**：2.G5（全链 e2e + BO / BP / BS / D5 close + 顺带数 BY）。

> **📌 更新 2026-09-23（第 5 笔〔⚠️ 同日第 6 笔顺手清掉本行原「⭐ 当前最新」标〕·**立 BY（历史事实被判「资料过期」）**·用户当日裁「按建议登记」·纯文档直接进 main）：配额族 **11 → 12**（上限 15·余 3·**在上限内、不占破例**）/ 非配额族 **15 不变** / 破例 **16 不变**、🔴 0；`lint:active-count` 同步改 **12**。上方同日第 4 笔的「⭐ 当前最新」标**同笔清掉**。
> - **起因**：D1 落地后用户问「查十年前的数据，日期也是十年前，是不是一律过期」。核实 = 是（且 400 天下同样如此·非 D1 引入）；今天影响限于复核成本与出处表误导，不碰结论 ⇒ 登记不改。
> - **触发**全事件型（守 §4.1）：动保鲜期表 / 复核清单 / 类型推断时 · 2.G5 全链 e2e 跑完时顺带计数 · 用户要求。2.G5 那一格已同步写进 [S2 §4.7.6](../roadmap/S2.md) 与设计 pass 的 2.G5 行（否则「跑完时顺带数」没人记得）。

> **📌 更新 2026-09-23（第 4 笔〔⚠️ 同日第 5 笔顺手清掉本行原「⭐ 当前最新」标〕·**CRED.2.G3 合 main 落账**·PR [#316](https://github.com/JunoChenZt/subagent-for-investment/pull/316) ✅ 合 main `a9e8b32`·CI 全过〔lint / backend 3.10 + 3.11 / docker / secret-scan〕·纯文档直接进 main）：**三项条目数全不变**（配额族 **11** / 非配额族 **15** / 破例 **16**）、🔴 0；`lint:active-count` 不动。上方同日第 3 笔的「⭐ 当前最新」标**同笔清掉**。
> - **裁了什么（用户 2026-09-23·实现中两处改裁设计 pass §3.2.3）**：① 出处窗口 = **显式对照**（`price` → 现价 1 天档·其余 → other 180 天；原案「按字段名查表」字面照做 = 全落 180 天、不生效）；② 过期 **不降审核档**、可信度落 `sourced_outdated`（原案降 notsure → 可信度 unavailable → 执行底线 check③ 只认过期档 ⇒ 过期价位反而漏出「切价位」）。
> - **2.G3 落地**：审核首次读出处日期（判据单一真值源在审核模块、可信度层同调）；靶测 22 + 反向变异 6/6 红（含生产调用点 AST 守卫）；主干回放 181 份断点零崩溃 · 审核档 0 翻转 · 可信度 0 翻转（4 条带过期注记）。**BP 不 close**（随 2.G5 全链 e2e 佐证）。立观察点 [O-CRED-02](../observations/should_update_observations.md)（局部只降不升 ≠ 全链只降不升·N=1）。
> - **裁决回填清单（§2.9.4 八格）**：已随 PR 落齐（① BP 条目 · ③ 段式跑指南前向注 · ④ 验收判据表前向注 · ⑤ O-CRED-02 · ⑥ 审核模块注释 · ⑦ S2 + 设计 pass · ⑧ memory；② N/A）；本笔只改「PR 待合 → 已合」。
> - **R7 复扫**：`PR 待合` / `auto/cred-2-g3` live 处清零。**下一棒**：2.G4（证据清单加身份字段·D2 已裁）→ 2.G5（全链 e2e + BO / BP / D5 三条 close）。

> **📌 更新 2026-09-23（第 3 笔〔⚠️ 同日第 4 笔顺手清掉本行原「⭐ 当前最新」标〕·**D1 裁决 + CRED.2.G2 合 main 落账**·PR [#315](https://github.com/JunoChenZt/subagent-for-investment/pull/315) ✅ 合 main `8570734`·CI 全过〔lint / backend 3.10 + 3.11 / docker / secret-scan〕·纯文档直接进 main）：**三项条目数全不变**（配额族 **11** / 非配额族 **15** / 破例 **16**）、🔴 0；`lint:active-count` 不动。上方同日第 2 笔的「⭐ 当前最新」标**同笔清掉**。
> - **裁了什么（用户 2026-09-23）**：① **D1 = 180 天**（保鲜期兜底档 other 400 → 180·半年 ≈ 两个财报季）；② 2.G2 验证方式 **裁 A** = 主干归档回放替代本 goal 的 e2e，真跑并入 2.G5。
> - **2.G2 落地**：常量 + 校准注（依据 / 已知高估 / 三条失效条件）+ 钉数用例（反向变异改回 400 → 红）；主干回放三处真代码：可信度 0 翻转 · 2a 复核清单 288 → 336 · 表③ 外源册标过期 38.1% → 51.7%。副作用：只写「今年」的日期过 7 月初即判过期（已写进校准注）。**BO 不 close**（随 2.G5 全链 e2e 佐证）。
> - **裁决回填清单（§2.9.4 八格）**：① BO 行 ✅ · ② 其它条目 N/A（BP 同读一张窗口表、代码自动跟随；其余引用是 dated 落账块）· ③ [段式跑指南](../observations/e2e-runs/segmented-e2e-guide.md) ✅ 前向注 · ④ [验收判据表](e2e-acceptance-standard.md) ✅ 前向注（未动检查档位）· ⑤ [O-CRED-01](../observations/should_update_observations.md) ✅ 补一句不计 N · ⑥ 代码常量与注释 ✅ · ⑦ S2 + 设计 pass ✅ · ⑧ memory ✅。
> - **R7 复扫**：`PR 待合` / `auto/cred-2-g2` live 处清零。**下一棒**：2.G3（审核读日期·D1 已定、前置满足）。

> **📌 更新 2026-09-23（第 2 笔〔⚠️ 同日第 3 笔顺手清掉本行原「⭐ 当前最新」标〕·**CRED.2.G0 / 2.G1 合 main 落账**·PR [#313](https://github.com/JunoChenZt/subagent-for-investment/pull/313) ✅ 合 main `9035ca8` + PR [#314](https://github.com/JunoChenZt/subagent-for-investment/pull/314) ✅ 合 main `c22976a`·#314 CI 全过〔lint / backend 3.10 + 3.11 / docker / secret-scan〕·纯文档直接进 main）：**三项条目数全不变**（配额族 **11** / 非配额族 **15** / 破例 **16**）、🔴 0；`lint:active-count` 不动。上方同日第 1 笔的「⭐ 当前最新」标**同笔清掉**。
> - **2.G0（#313·零代码）**：外源日期分布探针给 D1 备料 —— 外源册缺日期约 1/3、有日期里超 400 天 6.8%、audit_passed 外源事实 4 / 537 ⇒ 改线主要动 2a 复核清单（+51 / +119）与表③展示。合并前 review 两条（续跑沿用的分析师条目被重复计 / 重复内容跑批日取错）**当场修**进探针并重跑（v2·结论方向不变·差异表见 [FINDINGS §7](../observations/cred-2-g0-asof-dist-20260923/FINDINGS.md)）。**BO 不 close**（数值待用户裁 D1·随 2.G2 close）—— 行内补「弹药已备」注。
> - **2.G1（#314）**：`list(N)` / `dict(N)` 整族进 D5 跳过名单·fail 面不变。**`DEFECT-D5-COUNT-AS-VALUE` 不 close**（随 2.G5 全链 e2e 佐证·同簇 1 先例）—— 行内 + 正文由「PR 待合」改「已合 main」。
> - **R7 收口**：宽 grep `PR 待合` / `auto/cred-2-g0` / `auto/cred-2-g1` / `探针跑完` —— live 处（本表 BO / D5 行 + 正文、[S2 §4.7.6](../roadmap/S2.md) 2.G0 / 2.G1 行、[设计 pass](../plans/CRED-可信度地基三簇-设计pass-2026-09-08.md) §4.2 两行 + §6 账目归位 BO / D5 两行）全改；设计 pass §6 的 D5 行原写「close-by-completion」与 S2 行「随 2.G5 佐证后 close」自相矛盾，按后者订正。复扫 live 旧措辞清零。
> - **下一棒**：用户裁 **D1** → 2.G2；2.G3 排 2.G2 后。

> **📌 更新 2026-09-23（第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标〕·**CRED 簇 2 拆解放行 + D2 裁决落账**·纯文档直接进 main）：**三项条目数全不变**（配额族 **11** / 非配额族 **15** / 破例 **16**）、🔴 0；`lint:active-count` 不动。上方 09-22 第 4 笔的「⭐ 当前最新」标**同笔清掉**。
> - **裁了什么（用户 2026-09-23）**：① 簇 2（EVID-TIME）拆解按 [设计 pass §4.2](../plans/CRED-可信度地基三簇-设计pass-2026-09-08.md) 六子项**放行开工**（2.G0 量外源日期分布 → 2.G1 D5 整族跳过 → 2.G2 改 400 天〔等 D1〕→ 2.G3 审核读日期 → 2.G4 清单加身份 → 2.G5 收口）；② **D2 = 加字段**（`Reference.relevance`·默认空·回核层填）⇒ 2.G4 不再被阻断。D1 仍等 2.G0 量完、D3 仍等 3.G0。
> - **裁决回填清单（[§2.9.4](workflow/06-dod-and-evidence.md) 八格）**：① BS 条目正文 + 一览表行 ✅ · ② 引用该结论的其它条目 N/A（BO / BP 挂的是 D1）· ③ 跑批指南 N/A（未改任何判据）· ④ 验收判据表 N/A（2.G4 落地时登记）· ⑤ 观察点表 N/A · ⑥ 代码注释 N/A（`RetrievalIntent.purpose` 注释「将来进引用清单当意图标注」仍为真·2.G4 落地时改）· ⑦ [S2 §4.7.6](../roadmap/S2.md) 进度行 / 待裁行 / 2.G4 行 + 设计 pass 状态行 / §2.2 / §3.2 / §4.2 ✅ · ⑧ memory ✅。
> - **顺手订正（live 自相矛盾）**：S2 §4.7.6「待裁」行仍列 🔲 D4，而 D4 已于 09-10 裁、同段 1.G4 行早已 ✅ —— 本笔挪到「已裁」行。
>
> **📌 更新 2026-09-22（第 4 笔〔⚠️ 09-23 第 1 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK 静默降级可见化 ✅ CLOSED（close-by-completion）· 记账项迁观察点表**·纯文档直接进 main）：配额族 **12 → 11**（BK close 释放 1 slot·上限 15 余 4）/ 非配额族 **15 不变** / 破例累计 **16 不变**、🔴 0；`lint:active-count` 同步改 **11**。
> - **为什么能 close**：两本账归零（登记待补 0 站 · 盘点真待补 0 行·第 3 笔已核）；用户裁「把 BK 的记账项迁到观察点表，然后 close」。
> - **迁了什么**：一览表行与正文里挂着的 **27 条记账 / observe 项 + 1 条留存事实 = 28 条**，整体迁入 [O-BK-01](../observations/should_update_observations.md)（P0 另记 2 · PR3 记账 1 · BK.5 记账 2 + review 5 · M4-fix review 4 · BK.3 observe 4 · BK.6 本批 3 + review 6 · 无基线 1 · classify 超时事实 1）；每条带事件型触发条件、触发时按条处置、处置后就地标 ✅。**不累积 N**（是清单不是同类信号）。已结案 / 已修 / 已另立的不迁（三处「整份作废」候选 M4 结案 · key_claims #309 已修 · `API-EMPTY-QUERY` 第 3 笔另立）。
> - **收口扫描（R7）**：live 口径改 = 一览表 BK 行前缀 · BK 正文 close 块 + 今日收口块措辞 · S2 顺手项 BK 一句 + §4 表 09-14 注 · CRED 设计 pass §3.1.5 · BK.0 盘点余待补格 · memory；历史更新笔 / 证据 / 复盘 = point-in-time 不动（旧「条目不 close」措辞只留在冻结档）。
> - **重开条件**：e2e / 生产出现一次「静默降级致结论失真」而汇总没报。
>
> **📌 更新 2026-09-22（第 3 笔〔⚠️ 同日第 4 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.6 登记表余 7 站 + 盘点余 2 行清账落账**·PR [#312](https://github.com/JunoChenZt/subagent-for-investment/pull/312) ✅ 合 main `59b3689`·CI 全过〔lint / backend 3.10 + 3.11 / docker / secret-scan 全 pass·frontend 按路径分诊跳过〕）：配额族 **12 不变** / 非配额族 **14 → 15**（+`API-EMPTY-QUERY` 轻条目·用户 09-22 裁 A「只留痕、拒空串另立」）/ 破例累计 **16 不变**、🔴 0；**BK 两本账归零 → 主体收口、条目不 close**（登记待补痕 **7 → 0 站**，合并后 main 实跑 `lint_degradation_registry` = **92 / 0 / 53** 共 145；盘点真待补 **3 → 0 行**）。
> - **做了什么**：降级点账本上最后 9 处嫌疑点逐处查清：**4 处补便条**（空问题整段跳过取数 `context_empty_query` / 分析师扩写失败 `analyst_expand_failed` / 联网数字盖编号失败 `web_number_stamp_failed` / 异模型复核调用失败 `review_call_failed`）· **1 处只加读法**（决策里幻觉引用被剥 `hallucinated_refs_stripped`——执法记录早在写、汇总没读）· **4 处判不算 / 已覆盖**（缓存失效失败·生产无 cache / 备用行情源失败·默认未配且缺腿已报 / 取数单源被跳过 #17 / 确认后缺腿 #20——后果都由 `leg_missing` 报）。退路、判定、硬拦一字不动（review 修的那一处除外，见下）。
> - **验证**：量基线 origin/main 在册 57 run 五码全零（trace 不收日志行·无历史阳性）⇒ 会响靠 14 条靶测 + 反向变异 8/8 红、没退步靠在册回放 203 / 203 逐字相同；冒烟裁 D 豁免（四处便条全在 except 分支）；全套 4843 绿（review 修前）· review 修后触及分析师节点的 15 个测试文件 555 绿；四道 lint 干净。
> - **合并前 review（坐实 8 = 修 2 + 记账 6·用户裁「前两条修掉、其余记账」）**：修 ① 分析师扩写块在主调用 try 之外、原只捕 JSON 类错误——网络 / provider 异常会从节点穿出（既无兜底报告也无便条·**读码坐实非推断**）→ except 放宽到 Exception、退回原报告 + 便条、BaseException 仍上抛（**本批唯一动到退路行为的一处**·初版范围来自 initial import、无设计记录）；② 空 query 对照测试原在 except 里 return、断言不可达 → 手动开篮 + `pytest.raises`。记账 6 条见 BK 正文。
> - **用户裁决**：拆解五件全按建议（A 只留痕·API 拒空串另立 / B 新码便条 / C exempt + 记账 / D 冒烟豁免 / E exempt 写重评时点）· 刹车 Q6 命中（跨三个子阶段）→ 09-22 放行 · review 前两条修其余记 · 合并并落账。
> - **发现去处对账（§2.11.9）**：本批自带 **坐实 5 = 修 1 + 记账 4 + 不做 0**（修 = 扩写异常穿出节点·由 review 翻修；记账 = HTTP 入口不拦空串〔→ 本笔立 `API-EMPTY-QUERY`〕· `__degradation_notices__` 无读者 · 缺腿「原因」没人记 · E8 兜底档 rss / fred 可疑缺腿）；合并前 review **8 = 修 2 + 记账 6**；落账新增 1 条轻条目。证据 [bk6](../observations/bk6-20260922/FINDINGS.md) · 拆解 [BK.6-decomposition](../plans/BK.6-decomposition.md) · 复盘 [BK.6_2026-09-22](../retro/S2/BK.6_2026-09-22.md)。
> - **下一棒**：无新节点待拆；BK 主体收口、条目不 close（正文仍挂 ≥ 10 条带触发条件的记账 / observe 项——各有事件型触发条件、就地留在正文；要 close 须用户裁迁走）。`lint:active-other-count` 同步改 **15**。
>
> **📌 更新 2026-09-22（第 2 笔〔⚠️ 同日第 3 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.5 取数意图被拒收 / 丢弃留痕落账**·PR [#311](https://github.com/JunoChenZt/subagent-for-investment/pull/311) ✅ 合 main `d4d3891`·CI 全过〔lint / backend 3.10 + 3.11 / docker / secret-scan 全 pass·frontend 按路径分诊跳过〕）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点真待补仍 **3 行** #17 #20 #25；登记待补痕 **12 → 7 站**，合并后 main 实跑 `lint_degradation_registry` = **87 / 7 / 51**（共 145；比 PR 自述 87 / 7 / 50 多出的 1 站 = 合并前 review 修加的「留痕自兜」分支登记 exempt）。
> - **做了什么**：取数计划里被扔掉的意图原先只在日志里、产物只见「剩下的腿」→ 规划员扔的条目随计划对象带走（`RetrievalPlan.dropped_intents`·加性字段·旧档缺键照读）、人工确认环把被拦下的条目也记进去（量基线撞出的盲区：原写法人工路径的拒收到节点前就消失）、节点在**最终采用**时刻一条意图一张便条（新码 `plan_intent_dropped`·全灭不发、回放跳过带进来的那份）。**扔不扔、怎么扔一字未动**；登记表同族 5 站合一码翻 `code:`。
> - **验证**（本批证据）：量基线 origin/main 在册 13 个规划员 run **零命中**（校验拒收 0 / 规划员丢弃 0 / 49 条意图）⇒ 本码无历史阳性，「会响」靠 14 条靶测 + 反向变异 7/7 红、「没退步」靠在册回放 202 / 202 逐字相同（79 份旧计划经新 schema 零报错）；seg1 冒烟一段 ① 表全过、$0.0014、断点里计划对象已带空 `dropped_intents`；全套 4827 → review 修后 **4830 passed**；四道 lint 干净。
> - **合并前 review（坐实 7 = 修 2 + 记账 5·用户裁「第一条修掉补测试，其余记 backlog」）**：修 = 留痕函数原跑在 `try … except: return None` 里，留痕代码自己抛异常会把已校验通过的计划整跑打回兜底路由 → 整段自兜（失败只写日志·登记 exempt·计划照旧采用）+ 3 条靶测（便条函数抛异常计划照旧 / reasons 混非字符串照记 / 补进来的取价腿不算被扔），变异 1/1 红；记账 5 条见 BK 正文。
> - **用户裁决**：拆解五件全按建议（A 节点内一处发 / B 计划对象加自由 dict 字段 / C 一条一张·全灭不发 / D 人认过照发 + 确认环带走被拦条目 / E 跑 seg1 一段）· 刹车 Q6 命中（给已 DONE 计划契约加字段 + 改确认环组装）→ 09-22 放行 · review 第一条修其余记 · CI 过即合并并落账。
> - **发现去处对账（§2.11.9）**：本批自带 **坐实 3 = 修 1 + 记账 2 + 不做 0**（修 = 人工确认路径丢被拦条目；记账 = 最终归档不含 `common_context` / 人工路径规划员输出不进 calls.jsonl，两条触发条件写在[证据 §0 / §7](../observations/bk5-20260922/FINDINGS.md)）；合并前 review **7 = 修 2 + 记账 5**；落账新增 0。
> - **下一棒**：无新节点待拆；BK 条目不 close（余 3 行 + 7 站：`_build_context_inner` 空 query 可达性未核 / `apply_cache_invalidation` / `_alpha_vantage_fetch` / `run_tool_agent` 数字盖章失败 / 分析师扩写失败保留原报告 / 幻觉引用被剥 / 复核调用失败 detail 是否被读未核）。
> - **回填清单（§2.9.4 · 8 格）**：① 本条 BK 正文 ✅ 改 · ② 引用本结论的其它条目 ✅ 宽 grep「12 站」「同族 5 站」：S2 顺手项 ✅ / 盘点 §3.0 ✅ / BK.5 拆解前向注 ✅ / 第 1 笔更新记录 = point-in-time 不动 · ③ 跑批指南 N/A（新码走既有「本次退了哪几步」）· ④ 验收判据表 N/A · ⑤ 观察点表 N/A · ⑥ 代码注释 ✅（随 PR）· ⑦ S2 一句 ✅ + 盘点 §3.0 一句 ✅ + 证据 §8 翻 ✅ · ⑧ memory ✅ 改。
>
> **📌 更新 2026-09-22（第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.3 键粒度落账**·PR [#310](https://github.com/JunoChenZt/subagent-for-investment/pull/310) ✅ 合 main `dea94eb`·CI 全过〔lint / backend 3.10 + 3.11 / docker / secret-scan 全 pass·frontend 按路径分诊跳过〕）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点真待补仍 **3 行** #17 #20 #25；登记表待补痕**改按站点口径 = 12 站**，合并后 main 实跑 `lint_degradation_registry` = **82 / 12 / 50**（共 144 站）——与上一笔的「4 点」单位不同、不互相推导）。
> - **做了什么**：登记表的门牌号从「一个函数一行」改成「一处告警一行」（文件 + 函数全名 + 告警前 40 字，不含行号），守卫按站点点名；65 行旧登记逐站重审后拆成 144 站——有多处退路的函数**先一律落待补、再逐站拿证据提级**，绝不把整行「已留痕」复制给每一支。存在理由：往已登记函数里新加一支退路，旧守卫零反应（实测）；新守卫必须响（靶测钉住）。顺手：守卫文件清单补上未跟踪新文件。
> - **拆出来的账**：待补 12 站 = 旧 4 点各留 1 站 + 首次独立记账 8 站（原先藏在整键 `code:` 之下：意图被拒收 / 丢弃、腿少了没留痕同族 5 站 · 扩写失败保留原报告 · 幻觉引用被剥 · 复核调用失败 detail 是否被读未核）。拆解预期「待补先冲高」实际 4 → 12，比预想小——多数隐藏支审出来是 exempt 中间态。
> - **合并前 review（坐实 6 = 修 2 + observe 4 + 不做 0·用户裁「修前两条、其余记 observe」）**：修 = 同前缀告警按序号编 `#2` 重排静默换主 → 撞前缀用整句 / 整句相同报「指纹碰撞」· 非字面量消息守卫看不见 → 报「消息非字面量」必须登记；observe 4 各写升级触发条件（家 = [证据 §7](../observations/bk3-20260922/FINDINGS.md)）。
> - **验证**：守卫自检 33 → 57 · 全套 **4813 passed · 2 skipped · 2 xfailed** · 反向变异 6/6 红且恰是该红的 · 映射核对通过 · 登记守护 strict exit 0 · 四道 lint 干净；冒烟裁 E 豁免（守卫不在运行时链路）。
> - **用户裁决**：风险判定低自走；§6 五件全按建议（指纹键 / 多站先落 pending 再提级 / 不设通配 / 不加同函数 note 检查 / 冒烟豁免）；review 修前两条其余 observe；跑全套后合并并落账。
> - **发现去处对账（§2.11.9）**：本批自带 **坐实 4 = 修 2 + 记账 2 + 不做 0**；合并前 review **6 = 修 2 + observe 4 + 不做 0**（见[证据 §3.1 / §7](../observations/bk3-20260922/FINDINGS.md)）；落账新增 0。
> - **下一棒**：BK 条目不 close（盘点真待补 3 行 + 登记待补 12 站，其中同族 5 站「腿少了没留痕」可考虑合一个码一次接）· 无新节点待拆。
> - **回填清单（§2.9.4 · 8 格）**：① 本条 BK 正文 ✅ 改 · ② 引用本结论的其它条目 ✅（宽 grep「文件:函数名」「待补痕 N 点」：命中 S2 顺手项 ✅ / 盘点 §3.0 ✅ / BK.3 拆解施工状态 ✅ / 历史证据 · M3 / M4 拆解 · 执行计划 · 节点复盘 = point-in-time 不动）· ③ 跑批指南 N/A（守卫不在运行时链路）· ④ 验收判据表 N/A · ⑤ 观察点表 N/A · ⑥ 代码注释 ✅（随 PR）· ⑦ [盘点 §3.0](../plans/BK-G0-inventory-2026-09-14.md) 加站点口径注 ✅ + S2 §顺手项 BK 一句 ✅ + 证据 §8 翻 ✅ · ⑧ memory ✅ 改。
>
> **📌 更新 2026-09-21（第 4 笔〔⚠️ 09-22 第 1 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.2 M4-fix 落账**·PR [#309](https://github.com/JunoChenZt/subagent-for-investment/pull/309) ✅ 合 main `15443b8`·CI 全过〔lint / backend 3.10 + 3.11 / docker / secret-scan 全 pass·frontend 按路径分诊跳过〕）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点真待补仍 **3 行** #17 #20 #25；登记表待补痕 **5 → 4 点**，合并后 main 实跑 `lint_degradation_registry` = **40 / 4 / 21**（共 65），与 PR 自述一致）。
> - **做了什么**：① 辩论发言的要点清单写成对象时，原先整段陈词换成「解析失败」占位（M4 量基线 1/91·1571 字全丢）→ 只在「校验失败且问题出在要点清单」时逐项整理（字符串留 / 对象取论点文字 / 其余略过）、发言保住、留痕记被丢弃的字段；别的字段坏照旧占位、日志一字不改。② 登记表 `graph.py:_write_final_archive` 按 M4.3 计划原文翻 `exempt:`（上一笔查出的「文档说做了、代码没做」）。
> - **合并前 review（坐实 7 = 修 3 + 记账 4 + 不做 0·用户裁「前两条本 PR 修、其余记 backlog」）**：修 = 便条改由辩论环节出口对**最终采用**的发言发（首轮被返工替换的不发；原写法会给一条已不存在的发言留「正文完整保留」便条）· 留痕拆**两码两义** `debate_key_claims_coerced` / `debate_key_claims_dropped`（照 M3.2 裁 B）· 测试缺口随修补齐（11 → 18）；记账 4 条见 BK 正文。
> - **验证**（本批证据）：全量对照 origin/main 在册每条辩论原始输出，改前 / 改后各解析一遍 —— **91 份 90 不变、1 份从占位变为保住；204 条 203 不变、1 条同上**（零误伤·脚本内置断言·review 修后复跑逐字相同）· 反向变异 4 组 + review 后 2 组全红且恰是该红的用例 · 全套 **4789 passed · 2 skipped · 2 xfailed** · 四道 lint 干净。冒烟按用户裁豁免（改动只在校验失败分支、正常路径未变、204 条历史真实输出零误伤）。
> - **用户裁决**：刹车 Q6 命中（修改已 DONE 节点兜底契约）→ 09-21 放行 · 冒烟豁免 · review 前两条本 PR 修其余记 backlog · CI 过即合并并落账。
> - **发现去处对账（§2.11.9）**：本批自带 **坐实 2 = 修 1 + 记账 1 + 不做 0**；合并前 review **7 = 修 3 + 记账 4 + 不做 0**（见[证据 §6 / §8](../observations/bk2-m4-fix-20260921/FINDINGS.md)）；落账新增 0。
> - **下一棒**：BK.3 键粒度另立（待拆）· BK 条目不 close（盘点真待补 3 行 + 登记表待补痕 4 点：`_build_context_inner` / `apply_cache_invalidation` / `_alpha_vantage_fetch` / `run_tool_agent`，均属一键多支 / 生产不可达 / 裁 G）。
> - **回填清单（§2.9.4 · 8 格）**：① 本条 BK 正文 ✅ 改 · ② 引用本结论的其它条目 N/A（宽 grep `M4-fix` / `#309`：命中 S2 顺手项 ✅ / M4 拆解前向注 ✅ / 节点复盘 Q6 冻结不动 / 本条）· ③ 跑批指南 N/A（新码走既有「本次退了哪几步」）· ④ 验收判据表 N/A · ⑤ 观察点表 N/A · ⑥ 代码注释 ✅（随 PR）· ⑦ [盘点 §3.0](../plans/BK-G0-inventory-2026-09-14.md) 订正注接一句 ✅ + S2 §顺手项 BK 一句 ✅ + 证据 §7 翻 ✅ · ⑧ memory ✅ 改。
>
> **📌 更新 2026-09-21（第 3 笔〔⚠️ 同日第 4 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.2 M4 末批落账**·PR [#308](https://github.com/JunoChenZt/subagent-for-investment/pull/308) ✅ 合 main `587383a`·CI 全过）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点真待补 **8 → 3 行**：#17 #20 #25；BK.2 补痕五批 M0–M4 全部合 main）。
> - **做了什么**：分析师报告没按格式写、系统修正后才收下（M4.1·量基线 218 份报告 6 份、23 跑 3 跑 ⇒ 进用户面）· 质量审核打回后安排的重写根本没派出去（M4.2）两处留痕；末段归档写失败时屏幕上补一句「没写成、断点仍在」（M4.3·用户裁 5 不开新出口）；收口写出盘点 §3.0 逐行明细并跑**节点级复盘**。只加留痕，收报 / 返工计数 / 写盘行为与判定一字未改。
> - **验证**（本批证据）：全套 4752 passed · 在册 202 份回放 202/202 · 反向变异 14/14 红。合并前 review 订正「返工没派出去」的措辞（原句对最终结果下断言，下一轮重写后就说错·`937d82e`·补真跑两轮的回归测试）；合并后在 main 上跑相关 19 个测试文件 725 passed。
> - **🔴 落账时查出一处账实不符**：本批自述登记表待补痕「6 → 4」，**实跑 `lint_degradation_registry`：合并前 38 / 6 / 20 → 合并后 39 / 5 / 20**（共 64）—— 只有返工派发一键翻 `code:`。M4.3 计划把 `graph.py:_write_final_archive` 翻 `exempt:` 并写重评时点，**该改动没进合并代码**；证据里记的「39 / 4 / 20」合计 63、与 64 条对不上，可见不是实跑结果。已订正：盘点 §3.0 行内加订正注、证据两处加前向注；**节点复盘里的「9 → 4」按 Q6 冻结不动**，更正写在本条与 BK 正文。
> - **发现去处对账（§2.11.9）**：本批自带 **坐实 6 = 修 3 + 记账 3 + 不做 0**（见[证据 §7](../observations/bk2-m4-20260921/FINDINGS.md)）；合并前 review 新增 **1 = 修 1**；落账新增 **1 = 记账 1**（上一条·代码改动随 `auto/BK.2-M4-fix` 一并补，须走分支）。
> - **用户裁决**：拆解五件全按建议（09-21）· 冒烟**豁免**（裁 F）· 辩论小修「先做完 M4 再开」· 排查报告显示便条细节**不做**（裁 D·触发条件见 BK 正文）· 09-21 裁 review 那条修后合并。
> - **下一棒**：`auto/BK.2-M4-fix`（辩论 `key_claims` 小修 + 上述登记表翻档）· BK.3 键粒度另立（待拆）· BK 条目不 close。
> - **回填清单（§2.9.4 · 8 格）**：① 本条 BK 正文 ✅ 改 · ② 引用本结论的其它条目 N/A（宽 grep `#308` / `pull/308` 除本条与下列文档外零命中）· ③ 跑批指南 N/A · ④ 验收判据表 N/A · ⑤ 观察点表 N/A · ⑥ 代码注释 ✅（随 PR 已改）· ⑦ S2 §顺手项 BK 一句 ✅ + 盘点 ✅ 加订正注 / 拆解 / 执行计划 / 证据 ✅ 翻已合 · ⑧ memory ✅ 改。
>
> **📌 更新 2026-09-21（第 2 笔〔⚠️ 同日第 3 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.2 M3 决策 / 风控组补痕落账**·PR [#306](https://github.com/JunoChenZt/subagent-for-investment/pull/306) ✅ 合 main `eee2ef4`·CI 7/7）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点真待补 **10 → 8 行**；余 M4 一批）。
> - **做了什么**：决策与风控这一段三处悄悄丢东西的地方补齐留痕 —— 决策前事实核验里读不出的结果被跳过（#37）· 待查证清单里没写清要查什么的条目被略过（新行 #63；并按裁 B 把大纲小修那条便条拆成「改字段」「扔条目」两个码，一码一义）· 风控闸门提了问题、决策经理没答上（#44；调用失败与漏答合一个码，在回应环节当场记 —— 事后从归档读分不出「没答」和「没跑到」）。只加留痕，丢弃 / 过滤行为与判定一字未改。
> - **验证**（本批证据）：全套 4752 passed / 0 failed · 反向变异 13 组全红 · 在册 202 份回放逐字相同。三处历史**零阳性**（核验 25 次 / 大纲 27 次 / 风控 50 份齐全）⇒ 会响只由注入测试证；09-16 记的「44/17 回应为空」复现不出、已在证据里订正。
> - **盘点怎么数的**：#37 #44 翻已做 ⇒ 10 − 2 = **8**；#63 新增即做、不入计数。登记表按代码点另数：待补痕 **9 → 6**，落账时用合并前（`8d37e37`）与合并后（`eee2ef4`）两版登记表实跑对比，**恰为三键翻 `code:`**（`_run_verification` / 风控同名 `node` / `_parse_responses`），与本批自述一致。
> - **守护空转两处**：① 「用了没登记的码」闸原用单行正则，多行写法整个看不见（#304 起就盲）→ 本批改按 AST 取、坑表已记；② **合并前 review 又抓到一处**：改 AST 时文件清单从 `git grep --untracked` 换成了 `git ls-files`，还没 `git add` 的新文件整个看不见 → 已修（`959e9ec`；两向探针：同一个未跟踪、含没登记码的文件，修后红、旧写法绿）→ 坑表同条补一句「列文件别丢未跟踪」。
> - **CI 如实记**：本 PR 09-18 开后赶上额度用光，此前各 job 秒级红全是额度（见第 1 笔）；**首次真实 CI 在 09-21 review 修复推送后**，按 #307 新工作流 7 项全过。合并后在 main 上另跑调用到被改函数的 15 个测试文件 + 守护文件 887 passed。
> - **用户裁决**：拆解五件全按建议（09-18）· 冒烟**豁免**（裁 E：改动全在 except / 过滤 / 漏答分支 + 回放齐 + 注入齐）· 09-21 裁 review 那条修后合并。
> - **发现去处对账（§2.11.9）**：本批自带发现见[证据](../observations/bk2-m3-20260918/FINDINGS.md)；合并前 review 新增 **坐实 1 = 修 1 + 记账 0 + 不做 0**（即上面 ②）。
> - **下一棒**：BK.2 M4（[执行计划 §4](../plans/BK2-M2-M4-exec-plan-2026-09-16.md) 批 5·清洗档 / 返工 / 用户面小修 / #30 核·待拆、拆解须用户确认；收口后跑节点级 retro）。
> - **回填清单（§2.9.4 · 8 格）**：① 本条 BK 正文 ✅ 改 · ② 引用本结论的其它条目 N/A（宽 grep `#306` / `pull/306` 只命中第 1 笔 CI 事故记录〔历史·不动〕与下列文档）· ③ 跑批指南 N/A · ④ 验收判据表 N/A · ⑤ 观察点表 N/A · ⑥ 代码注释 ✅（随 PR 已改）· ⑦ S2 N/A + 盘点 ✅（随 PR 已改）/ 拆解 / 执行计划 / 证据 ✅ 翻已合 + 坑表 ✅ 补一句 · ⑧ memory ✅ 改。
>
> **📌 更新 2026-09-21（第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标〕·**CI 额度事故 + [#307](https://github.com/JunoChenZt/subagent-for-investment/pull/307) 合 main 落账**·用户裁「直接修、不立条目」〔同 [#271](https://github.com/JunoChenZt/subagent-for-investment/pull/271) Node 20 那笔先例〕·纯文档·直接进 main）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0。
> - **出了什么事**：GitHub Actions 私有仓免费额度 2000 分钟/月**连续两月用光** —— 08-25 → 08-31 全部 job 被拒一周（09-01 重置），09-18 上午再次用光，此后每个 job「1–2 秒失败 + annotation 写 spending limit」。**这不是代码红**：08-21 起 40 次失败 run 里约 36 次是额度、真测试红 3 次、1 次未分类；#306 的红叉即此。**症状识别法**：全部 job 秒级红 → 先看 annotation，别翻代码。
> - **钱花在哪**（实测 09-18 两次成功 run 的 job 时长）：每次真实算力约 7 分钟，GitHub **按 job 向上取整到整分钟**（官方文档原句 "rounded up to the next minute"）→ 记 14 分钟。三个浪费源按大小：11 个 job 里 7 个秒级 job 各计 1 分钟（每次白扔约 6 分钟·占一半）> 纯文档提交 66 次照跑全套（约 900 分钟）> 同 PR 连推旧 run 不取消 13 次（约 180 分钟）。204 次成功 run ≈ 2850 分钟 > 2000。
> - **修法**（用户裁四步全做·合 main `82cdb02`·[ci.yml](../../.github/workflows/ci.yml) 文件头有全文理由）：六把秒级尺子合一个 `lint` job（各自一步、`if: !cancelled()` 互不遮蔽·红的那步按名点亮）· `lint` 顺手做路径分诊（它本就 `fetch-depth: 0`；纯文档 → 只跑 backend 3.11、跳 frontend / docker-build；frontend 只在 `frontend/` 变了才跑；docker 只在镜像输入变了才跑；**fail-open**：算不出 diff 一律全跑）· concurrency 只在 PR 取消旧跑（main 不取消）· 每 job timeout（按实测最长 128 秒的 5–7 倍）。**`secret-scan` 刻意不并**：08-07 用户裁决单列必需检查的安全闸门、`test_gate_matrix` 钉死。**backend 不按文档跳过**：不少测试真的读 `docs/`（闸门矩阵读 e2e-acceptance-standard、checklist 不变量读 observations 归档）。
> - **实测**：#307 自身（改 5 个文件·非纯文档·且改了工作流本身 ⇒ 全开）**14 → 9 计费分钟**，六 job 全绿。纯文档档（预期 4 分钟）**本笔落账 push 即线上第一例**，结果记 memory。按上月结构折算每月 ≈ 2850 → 1300–1400（额度内）。**用户已提高消费上限**：超额部分 Linux $0.006/分钟（官方现价），改前用量折合每月约 $5、改后正常月份 $0；上限不再为零 ⇒ 将来即使超额也只是几美元，不会整体停摆。
> - **两条如实记**：① 「取消旧跑省约 100 分钟」按上月 13 次白跑估、无法单独实测；② GitHub timing API 对本仓所有 run 返回 0 ms，「9 分钟」是按 job 时长手工向上取整，未从账单页核 —— **下月初看账单页对一次**（判据：9 月 21 日起的日均计费分钟 vs 此前）。
> - **回填清单（§2.9.4 · 8 格）**：① 不立条目 N/A · ② N/A · ③ CONTRIBUTING 作业清单 ✅（#307 内）· ④ 坑表 §env-shadowing 一句 ✅ + 本表 §4 backlog-triggers 步 ✅（#307 内·closed 条目里旧 job 名按 Q6 不动）· ⑤ N/A · ⑥ N/A · ⑦ PR #307 描述 + 本地全套 4737 绿评论 ✅ · ⑧ memory `project_ci_quota_rework` ✅。
> - **过程记两笔**：守卫定位正则首版太松（脚本名藏行尾注释只有闸门矩阵响、改的那条不响）→ 变异抓到后收紧（`1cf640a`）；heredoc 折叠反斜杠**又撞一次**（坑表已有·改用 Write 脚本）。
>
> **📌 更新 2026-09-18（同日第 3 笔〔⚠️ 09-21 第 1 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.2 补跑真实冒烟落账**·纯观察记录·直接进 main）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点真待补仍 **10 行**）。
> - **结果**：main `a934ace` 上 NVDA 九段逐段由用户放行，终局质检 **15 pass / 0 warn / 0 fail / 0 n/a**，全程零降级，$2.03。第 2 笔记的「须补跑」⇒ **已了结**。
> - **如实分两半**：大纲小修与 PR3 的**不误伤**已由真跑证实；**真会补救 / 真会响**那半这次没被触发（模型没写坏档位、对应故障没发生），仍只由测试证明。
> - **订正一条错误记录**：09-17 第 1 笔「质量审核连续 9 次全过、零打回」只数了最终结论、漏了返工；按返工次数 08-03 起 9 份里 4 份有返工，本跑又打回 2 位 ⇒ 「规则太松」信号不成立。段式指南 D5 行已改读法（看返工次数），旧记录加订正注（`77dd847`）。
> - **观察项 5 条只记不立**（见证据 §4）：返工不附原因 · 投票信心值 8/10 为 6 · 两条旧证据 · 观望止损高于进场区（给不同人群·质检过）· 核查通过率第 5 次碰 5% 线。
> - **回填清单（§2.9.4 · 8 格）**：① BK 正文 ✅ · ② N/A · ③ 跑批指南 ✅（D5 读法·`77dd847`）· ④ N/A · ⑤ N/A · ⑥ N/A · ⑦ PR1 证据 ✅ 加两处订正注 · ⑧ memory ✅。
>
> **📌 更新 2026-09-18（同日第 2 笔〔⚠️ 同日第 3 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.2 PR3 取数组其余留痕落账**·PR [#305](https://github.com/JunoChenZt/subagent-for-investment/pull/305) ✅ 合 main `a934ace`·CI 12/12）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点真待补 **18 → 10 行**；余 M3 / M4 两批）。
> - **做了什么**：取数这一段剩余的悄悄退一步补齐留痕 —— 名录不可用 / 名录现拉失败 / 名录对账加载失败 / 源认不出整条跳过 / 行情最新一根坏值回退 / 研报库兜底与摘要部分失败；补价腿只进排查报告。名录故障一次恰好两条（上端「哪个市场没拉到」+ 下端「名录这次不可用」）。只加留痕，退路与判定一字未改。
> - **验证**：全套 4737 passed / 0 failed · 反向变异 17 组全红（每点两向）· 在册 192 份回放逐字相同。⚠️ 几处全是**零阳性基线**（名录不可用 0/71 · 补价腿 0/192 · 研报标记 0/52 · 行情坏值现场 0/8）⇒ 会响只由注入测试证。
> - **开工核出三处**：① 盘点 §3.1 #16「假待办」与 09-04 后的代码不符（被跳过的腿不进腿清单）→ 已订正（登记表与代码不符第 10 例）；② 「回核跑没跑」锚在腿上结论会把 **41 条**旧格式研报腿重复报 → 改锚回核自己写的字段；③ 源认不出今天生产走不到（两份源名单启动期对齐）→ 留痕保留、登记表写明。
> - **盘点怎么数的**：本批 9 行里 8 行在那 18 里 ⇒ 18 − 8 = **10**；#16 原判假待办不在 18 里、本批改判后直接做掉。无痕 33 → 24、已做 14 → 23。登记表按代码点另数：待补痕 21 → **9**（单位不同、不互推）。
> - **🔴 自我订正**：同日第 1 笔写「大纲小修 #304 由 PR3 冒烟顺带覆盖」**不成立**（PR3 按施工单沿用 PR1 冒烟、不另跑）⇒ 第 1 笔原句旁已加订正注。**用户 09-18 裁：PR3 合并后在 main 上补跑一次真实段式冒烟**，一并覆盖 #304 与本批（约 $1.7·每段续跑由用户确认）。
> - **发现去处对账（§2.11.9）：坐实 5 = 修 3 + 记账 2 + 不做 0**。修 3 = 上面三处中的 ① ② + 冒烟说法订正；记账 2 在 **BK 正文**：同族「整份作废」三处候选（observe）· 补的价格腿仍不进归档计划的意图清单。
> - **用户裁决（2026-09-18）**：刹车 Q6（跨取数 / 研究两阶段）+ Q5（大纲小修冒烟豁免理由不成立）→ 放行、检查全过即合；补跑真实冒烟。
> - **下一棒**：main 上补跑真实冒烟 → BK.2 M3 / M4 两批（[执行计划 §4](../plans/BK2-M2-M4-exec-plan-2026-09-16.md) 批 4 / 批 5·待拆）。
> - **回填清单（§2.9.4 · 8 格）**：① 本条 BK 正文 ✅ 改 · ② 引用本结论的其它条目 N/A（宽 grep `#305` / `auto/BK.2-M2b` / 「顺带覆盖」只命中本条、同日第 1 笔与下列文档）· ③ 跑批指南 N/A · ④ 验收判据表 N/A · ⑤ 观察点表 N/A · ⑥ 代码注释 N/A（随 PR 已改）· ⑦ S2 N/A + 盘点 ✅（随 PR 已改）/ 拆解 / 摸底计划 / 两份证据文档 ✅ 加前向句 · ⑧ memory ✅ 改。
>
> **📌 更新 2026-09-18（第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.2 大纲缺陷小修落账**·PR [#304](https://github.com/JunoChenZt/subagent-for-investment/pull/304) ✅ 合 main `493a47e`·CI 12/12）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点真待补仍 **18 行**·本修不在盘点表内、是 P0 批量基线查出的产品缺陷）。
> - **做了什么**：待查证清单逐项校验，不合格字段回 schema 默认值、该项保留、五段大纲保住，并留痕记模型原值（用户 09-18 裁 **A**，未选「整项丢弃」B）。此前一个档位值写成「中」就让整份大纲作废（29 份带决策存档里 4 份）。核验范围（只查「高」项）不变 ⇒ 对结论零影响。
> - **验证**：全套 4700 passed / 0 failed · 反向变异 5 组全红（含「整项丢弃 = 没选的 B」也会红）· 在册 192 份回放逐字相同 · 回归夹具 = 三份真实归档里大纲那次调用的原始输出。**冒烟：用户裁豁免**（正常路径上的纯确定性本地逻辑；PR3 冒烟顺带覆盖〔⚠️ 同日第 2 笔订正：**不成立**——PR3 按施工单沿用 PR1 冒烟、不另跑；用户已裁 PR3 合并后补跑一次真实冒烟〕）。
> - **发现去处对账（§2.11.9）：坐实 1 = 修 0 + 记账 1 + 不做 0** —— 同族形态别处有没有 → BK 正文（M2.7 收口时扫 `model_validate` 整份 fallback）。
> - **用户裁决三件（2026-09-18）**：修法 A · 冒烟豁免 · 检查全过即合并。刹车 8 问均否（Q5 主动披露：P0 一条用例改打桩触发、冒烟豁免）。
> - **下一棒 = PR3** `auto/BK.2-M2b`（[拆解 §4.3](../plans/BK.2-M2-decomposition.md)·M2.4–M2.7·从 main 新建）。
> - **回填清单（§2.9.4 · 8 格）**：① 本条 BK 正文 ✅ 改 · ② 引用本结论的其它条目 N/A（宽 grep `#304` / `outline-fix` 只命中本条与下列文档）· ③ 跑批指南 N/A · ④ 验收判据表 N/A（不增不改检查）· ⑤ 观察点表 N/A · ⑥ 代码注释 N/A（随 PR 已改）· ⑦ S2 N/A + P0 批证据文档 ✅ 加前向句 + 摸底计划 ✅ 翻 · ⑧ memory ✅ 改。
>
> **📌 更新 2026-09-17（同日第 2 笔〔⚠️ 09-18 第 1 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.2 P0 批五个要紧点落账**·PR [#303](https://github.com/JunoChenZt/subagent-for-investment/pull/303) ✅ 合 main `3da9a61`·CI 12/12）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点口径真待补 24 → **18 行**）。
> - **做了什么**：五处「悄悄退一步」各装一条留痕 —— 联网检索工具没接上 / 判了个股却没认出是哪只 / 决策大纲退成单段 / 引用条目坏了被扔 / 清单超上限截断；另加两条旧存档也有效的读法（段数偏少 = 疑似 · 断链）。只加留痕，退路与判定一字未改，便条不进提示词（新增两道守护：生产者只许导入「写」那一个函数 · 拼提示词的模块对执法记录一处读取都不许有）。
> - **验证**：全套 4691 passed / 0 failed · 反向变异 25 组全红（每点两向）· 在册 192 份回放：188 份逐字相同、零消失、4 份新增且逐份核为真。⚠️ 旧记录里五个新码出现 0 次 ⇒ 回放只证「没退步」，「会响」只由注入测试证。冒烟按裁 H 豁免。
> - **开工前量基线（坑表「没量基线不定档位」）**：段数读法命中 4 / 假阳性 0 → 进用户面、措辞只说「疑似」；断链读法命中 0 = 零阳性样本 → 只进排查报告；其余四个码无历史基线（进程日志不存档），如实记。
> - 🔴 **量基线量出一个此前无人知晓的产品缺陷**：「待查证清单」里一个重要程度写成「中」（系统只认「高 / 低」）⇒ 整份五段大纲作废、论述退成一整段；29 份带决策的在册存档里 4 份，原因完全相同。**用户裁：本批合并后单开一个小修（排在 PR3 之前·先看修法再动手）**。
> - **用户裁决三件（2026-09-17）**：① 刹车 Q6 命中（便条发自取数 / 研究 / 决策三个阶段的代码）→ 放行；② 上条缺陷 → 单开小修；③ 合并 #303。
> - **发现去处对账（[§2.11.9](workflow/08-retro-node-and-pr.md)）：坐实 5 = 该 PR 修 2 + 记账 3 + 不做 0**。修 2：没认出标的的第三支（名录判无效）· 登记表说明跟在码后面破坏对账（挪进注释·守护没动）。记账 3 全在 **BK 正文**：大纲缺陷（触发 = 现在·已裁单开小修）· 排查报告不显示便条细节（去处 = M2.7 收口时定）· 四个新码无基线（触发 = 首次真实响起）。
> - **盘点口径怎么数的**：真待补 24 行里减去 P0 涉及的 6 行（#9 #38 #45 #46 #56 #57）= 18；无痕 39 → 33、已做 8 → 14。#45 的 verify.py 半支（生产零调用）与 #57 的撞上限支（裁 G）判不算。**总口径重算仍按[执行计划 §0](../plans/BK2-M2-M4-exec-plan-2026-09-16.md) 放 M2.7 收口**，此处不另造数。
> - **提交时判据检查点名 3 条，均不算新触发**：BK（本批就是 BK 的活）· `DEFECT-CTX-BAG-SHAPE`（早已是已触发状态·本批没碰资料夹字段）· `AF-residual`（判据点的是决策环节里报告注入那一段·本批没碰·检查器自标粗粒度）。
> - **下一棒**：先做大纲缺陷小修 → 再 PR3 `auto/BK.2-M2b`（[拆解 §4.3](../plans/BK.2-M2-decomposition.md)·从 main 新建）。
> - **回填清单（§2.9.4 · 8 格）**：① 本条 BK 正文 ✅ 改 · ② 引用本结论的其它条目 N/A（宽 grep `#303` / `auto/BK.2-P0` 只命中本条与下列文档）· ③ 跑批指南 N/A（不改跑法、不改检查表）· ④ 验收判据表 N/A（D1 仍记录型；新读法不参与判定）· ⑤ 观察点表 N/A · ⑥ 代码注释 N/A（随 PR 已改·登记表同 PR 已翻）· ⑦ S2 N/A（其 BK 注记未引用行数）+ 盘点 §3.0 与六行行内注 / 拆解 / 执行计划 / 摸底计划 ✅ 改 + 证据文档 ✅ 加前向句 · ⑧ memory ✅ 改。
>
> **📌 更新 2026-09-17（第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.2 M2 PR1 地基落账**·PR [#302](https://github.com/JunoChenZt/subagent-for-investment/pull/302) ✅ 合 main `6483a4c`·CI 12/12）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点口径真待补仍 **24 行** —— 本批只打地基、不新增降级码）。
> - **做了什么**：流程图全图唯一注册点统一装记录本（便条盖环节名 · 汇总按（码, 阶段）合并）+ 丢失单改为每次跑批一本（两入口都装 · 跑批外便条当场作废）。只加留痕、不动判定、不进提示词。
> - **验证**：全套 4640 passed / 0 failed · 171 份在册归档回放逐字相同 · 13 组变异全红 · 真跑冒烟 1 个股 + 1 宏观 9 段全过（质检 14/0/0/1 · 13/0/0/2）。⚠️ **如实短板**：回放与两次冒烟都**零便条** ⇒「按环节归阶段」目前只有单测证据。
> - **用户裁决两件（2026-09-17）**：① 刹车 Q6 命中（包装横跨所有阶段）→ **放行**；② 冒烟撞到的范围外发现 → **全部先记观察项，不开新条目、不改线**。
> - **旧账了结**：09-16 第 1 笔「三批均未跑真 e2e 冒烟·M1.5 豁免待用户裁」→ 用户 09-17 裁「由 PR1 冒烟顺带覆盖」，PR1 冒烟已跑完 ⇒ **该未决关闭**（BK 正文已改口）。
> - **发现去处对账（[§2.11.9](workflow/08-retro-node-and-pr.md)）：坐实 7 = 该 PR 修 2 + 记账 5 + 不做 0**。记账 5 条的家：研报库取数贴时限且降级清单不说是超时 → **BK 正文**（PR3 取数组补痕时看）· 分析师零检索分不出原因 → **BK 正文**（P0.1 开工即消化）· 质量审核连续 9 次全过〔⚠️ 09-18 订正：**不成立**——只数了最终结论、漏了返工；9 份里 4 份有返工〕 → [段式指南](../observations/e2e-runs/segmented-e2e-guide.md) ③ 段 D5 行读数注 · 第 8 段核查通过率 <5% 排查线个股跑也碰线 → 指南 ⑧ 段 D2 行读数注 · 打回重答要按作答拆开数调用 → 指南 ⑥ 段续写行读法注。**三条线本身一字未动**（改线须用户另裁）。
> - **提交时判据检查点名 BL**（`graph.py`）：BL 盯超时常量与分析师并发编排；该批只套包装、扇出的边一条没动 ⇒ **不算触发**（检查器自标「粗粒度·可能空喊」）。
> - **下一棒 = PR2 P0 批**（[拆解 §4.2](../plans/BK.2-M2-decomposition.md)）：从 main 新建 `auto/BK.2-P0`；冒烟按裁 H 豁免（前提：改动全在退路分支或纯汇总派生，碰正常路径就补跑）。
> - **回填清单（§2.9.4 · 8 格）**：① 本条 BK 正文 ✅ 改 · ② 引用本结论的其它条目 N/A（宽 grep `#302` / `auto/BK.2-M2` / 「豁免待」只命中本条与下列文档）· ③ 跑批指南 ✅ 加三处读法 / 读数注（线不动）· ④ 验收判据表 N/A（不增不改检查）· ⑤ 观察点表 N/A（该表收过程信号；这 5 条是产品 / 读法信号，家在 BK 正文与指南）· ⑥ 代码注释 N/A（随 PR 已改）· ⑦ S2 N/A（其 BK 注记数字仍准）+ 拆解 / 执行计划 / 摸底计划 ✅ 翻 PR1 已合 + 证据文档 ✅ 加前向句 · ⑧ memory ✅ 改。
>
> **📌 更新 2026-09-16（第 1 笔〔⚠️ 09-17 第 1 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.2 M1 / M1.5 / 冷审收口三个 PR 落账**·PR [#299](https://github.com/JunoChenZt/subagent-for-investment/pull/299) ✅ 合 main `3f1bf58`〔含 PR [#300](https://github.com/JunoChenZt/subagent-for-investment/pull/300) `5d4175f`·叠在其上一并 squash〕+ PR [#301](https://github.com/JunoChenZt/subagent-for-investment/pull/301) ✅ 合 main `c38edd1`·CI 均 12/12）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（盘点口径真待补仍 **24 行**）。
> - **M1**（#15 #29 #39·只加读法）：封顶路由键 / 兜底票 / 论述节占位三处「记录早在写、没人读」接进汇总，生产代码零改动。
> - **M1.5**（插队·用户当日裁）：**`classify_degraded` 是死派生** —— 读的 state 键全仓无生产者、从落地起恒不触发，登记表却标 `code:`。修法照 `_ticker_resolution` 当年「搬一趟进资料夹」的先例（四条构造路径全接，含两条本身就是降级场景的兜底）；登记表订正 9 处（含 2 处用户裁决落账：E 类 / 归档导出不做）。
> - **#301**：冷审五条（守卫锚错对象 / wisburg 登记翻 `code:` 说过头→退回待补 / 判据锚在模型散文→收紧整段匹配 / 措辞过头 / 数字抄两份）+ **review 三修**：封顶那句按下游实际走到哪选措辞 · 价格闸早停不再报三条假「没出结果」（前提钉在编译后流程图的可达集合上）· 死读守卫认 `.get` / `[...]` / 嵌套读。
> - **登记表账面**（`lint_degradation_registry`）：已有留痕 **16** · 待补痕 **29** · 不算降级 **17**。
> - ⚠️ **自我记账**：review 里报的「封顶兜底丢了分类来源」**是误报** —— #299 合并时已修且有消费侧测试，凭上一轮写代码的记忆报的、没开当前代码核（已进 memory）。
> - ⚠️ **未决**：三批均**未跑真 e2e 冒烟**；M1.5 动了正常路径（资料夹加字段），豁免**待用户裁**。
> - **下一棒 = M2**（[计划 §3](../plans/BK2-M2-M4-plan-2026-09-16.md)）：并行探针转正为测试 → 图层统一包装 → 取数 / 名录组补痕。
> - **回填清单（§2.9.4 · 8 格）**：① 本条 BK 正文 ✅ 改 · ② 引用本结论的其它条目 N/A（宽 grep `#299` / `auto/BK.2-M1` / 「待合」只命中本条与下列文档）· ③ 跑批指南 N/A（不改跑法）· ④ 验收判据表 N/A（D1 仍记录型、不参与判定）· ⑤ 观察点表 N/A（无观察点变化）· ⑥ 代码注释 N/A（汇总模块文档 #301 已改为只留链接）· ⑦ S2 N/A（其 BK 注记数字仍准）+ M2–M4 计划 / 盘点 / 收集器设计 ✅ 改 + 坑表 ✅ 加一条 · ⑧ memory ✅ 改。
>
> **📌 更新 2026-09-15（同日第 5 笔〔⚠️ 09-16 第 1 笔顺手清掉本行原「⭐ 当前最新」标〕·**BK.2 M0 收集器落地**·PR [#298](https://github.com/JunoChenZt/subagent-for-investment/pull/298) ✅ 合 main `b52060e`·CI 12/12）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（真待补 25 → **24**）。机制：节点入口开便条篮、深层代码 `note_degradation()` 往里扔（**不改任何函数签名**）、出口并进既有 `enforcement_log` ⇒ **接一个新点 = 代码一行 + 码表一行**。**🔴 外部 review 报 10 条，其中一条推翻了机制设计**：原「进程级计数写进归档」在**段式跑**下永远读到 0（每段独立进程 · 归档在末段写 · 开篮子的节点在首段且续跑被跳过）⇒ 产物会印「记录器无丢失」，正踩本仓自己的「读不到 ≠ 没丢」；且常驻服务会跨跑串味。已重做为**节点出口取走**、变成一条普通降级（`recorder_dropped`）随便条进记录通道。**另修 6 条**，最重一条 = `if fund:` 让「查到空」伪装成成功、而登记表已盖「已有留痕」章 —— **与 `if cost:` 让算不出钱伪装成 $0.0000 同族、同日再踩**。🔻 明确不做 1 条（篮子改开在图层统一包装点·已记触发时机 = M2 需要第二个节点开篮子时）。📌 **三条自我记账**：① 我设计的保险在标准跑法下是假的；② 给静默路径盖了章；③ 我新写的守卫自己误报（提取器只认三种码写法里的一种 · **没放松断言、改的是提取器**）—— ②③ 同一母题：**判据挑错了被测对象**。证据：机制层 14 条测试（含真实链路穿线）· 两道新守卫反向变异均转红 · 171 份在册归档改前改后**零差异** · 全套 4580 passed。

> **📌 更新 2026-09-15（同日第 4 笔·**BK.2 分诊批**·PR [#297](https://github.com/JunoChenZt/subagent-for-investment/pull/297) ✅ 合 main `91eb1bf`·CI 12/12）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**。质量审核自己出故障时留痕：**#59 补痕**（新查出的 🔴·放行判定一字未改）+ **#58 只加读法**（记录早在写、无消费面·同 #41 形态）+ **#60 降档**（原标 🟡·追到底后不成立：E 类整族在观察期只记日志，跑不起来不会把「本该警告」变「通过」；且另一分支其实有痕）⇒ **实际改动比计划小**，两条是「我上一轮判早了 / 记错了」。余普通批 **42 → 40 行**。**171 份在册归档改前改后逐份逐码相同、零差异**；⚠️ 与提前批不同，**本批无历史真阳性**（新码零命中 —— 只说明对历史结论零影响，**不说明该故障不会发生**）。🟢 **提前批装的「记录通道不得进提示词」守护本批真开火**（分诊节点成为新消费面时被拦，核过才登记白名单）。⚠️ **一条方法教训**：首次两向变异**删出了语法错误**，pytest 报的是收集失败 —— **那不算测试转红**；已重做为语法合法的空操作再验。**变异必须让代码仍能跑，否则验的是另一回事。**详见 [证据与发现](../observations/bk2-triage-20260915/FINDINGS.md)。

> **📌 更新 2026-09-15（同日第 3 笔·**BK.0 盘点表补齐 9 行·查出一条新 🔴**·纯文档·无代码改动）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0（backlog 口径；新查出的 🔴 是**降级点**不是 backlog 条目）。第 2 笔说的「表格少 5 行、BK.2 收尾前须补齐」**本笔已办，且原假设被推翻** —— 照着「§2.3 / §2.4 少 5 行」去找**根本找不到**，漏项不在那两节。改用**表与降级点登记表对账**（登记为真降级、而整个函数在表里一行都没点到）查出 **10 个无覆盖登记键**，其中 **9 个立为新行**（#54–62）、1 个属重复视角不另立。⇒ 现为 **62 行 / 无痕 44 / 已做 3 / 余 42 行**（第 2 笔的「余 33 行」作废·第 2 笔 point-in-time 不改）。🔴 **补齐里查出一条新的同形态问题**：**C 类质量规则跑不起来时，判定读起来与「C 类通过」一模一样**（已逐行核到消费方 `c_failed = (c_results is not None and …)`）—— 与本次提前批刚修的三处**同族**；另一条 E2 规则**只核到一半**、标 🟡 不标 🔴（不冒充）。⚠️ **对账两处易错已记进 §2.5**：表里用简称（`yfinance:` 指 `yfinance_source.py`）⇒ 别名不归一多报 4 条；表里行号与实际调用点有偏移 ⇒ 按行精确匹配多报 40+ 条，**必须按函数区间匹配**。📌 **同一个数第四次订正**，口径与「怎么数的」已固化进 [BK.0 §3.0](../plans/BK-G0-inventory-2026-09-14.md)。

> **📌 更新 2026-09-15（同日第 2 笔·**BK.2 剩余批数字重算 + 盘点表对账**·纯文档·无代码改动）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0。用户裁「盘点里标 `state 弱` 的行（字段退成空值）**也算无痕**」→ 对 BK.0 盘点表**逐行重算**：表内 **53 行** · 新口径无痕 **35 行** · 已做 3 行 · **余 33 行**（行内自注代码点 50）。⇒ **第 1 笔里的「余普通批 30 处」作废**（第 1 笔 point-in-time 不改，前向事实以本笔与 BK 条目为准）。🔴 **同时查明两处对账缺口**：① 盘点表**比小节标题少 5 行**（22/9/**16**/**6** = 53 vs 标题 22/9/19/8 = 58·前两段分毫不差 ⇒ 大概率表格漏行、非统计错）——**BK.2 收尾前须补齐**，否则「33 行做完」不等于做完；② 「58 / 33」**从表里复算不出来**（按行 53 / 按代码点 71），它出自另一份人工分类、**与表格从未对过账**。📌 **同一个数三次订正**（44→ / 无痕判据 / 本次），根因同一个：**没写出「怎么数的、从哪份数据数的」** —— 口径已固化进 [BK.0 §3.0](../plans/BK-G0-inventory-2026-09-14.md)，教训已在坑表 §3.2。

> **📌 更新 2026-09-15（同日第 1 笔·**BK.2 提前批：三处「把没检查说成检查过了」补痕**·PR [#296](https://github.com/JunoChenZt/subagent-for-investment/pull/296) ✅ 合 main `d019e98`·CI 12/12）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 仍不 close**（持普通批）。用户裁「只加留痕、绝不动判定」。**开工核对推翻方案的通道设想** —— `enforcement_log` 是既有键，复用即可，**不新增 state 键**、旧归档兼容风险面消失，风险由「中～高」降为「低～中」。**订正盘点一格**（誊写核查那处一直在写记录、只是无人读）⇒ 真·无痕 33 → **32**，余普通批 **30 处**。**171 份在册归档改前改后对照：169 份逐字相同 / 2 份只多出提示 / 零消失**；那 2 份是**自然真阳性**（07-22 核查模型断线 · 08-14 额度耗尽）。质检 D1 补登记为「记录型·不参与判定」。**e2e 冒烟经用户裁决豁免**（本形态限定·非通例）。详见 [证据与发现](../observations/bk2-red-batch-20260915/FINDINGS.md)。

> **📌 更新 2026-09-14（第 6 笔·**BK 静默降级可见化 BK.0/1/3/4 落地**·PR [#295](https://github.com/JunoChenZt/subagent-for-investment/pull/295) ✅ 合 main `a53b196`）：**三项条目数全不变**（配额族 12 / 非配额族 14 / 破例 16）、🔴 0；**BK 不 close**（仍持 BK.2）。判据 (D) 随 BJ 收口满足 → 重评 → 用户裁五项全按推荐 → 落地。**盘点推翻方案自己的「44 处」** ⇒ 真降级 58 处、33 处只写日志、3 处「把没检查说成检查过了」。汇总纯派生不进提示词；降级留痕**首次进用户面**；`DEFECT-CTX-BAG-SHAPE` ⑦ 定锚并 close。
>
> **📌 更新 2026-09-14（第 5 笔·**BJ.5 五族落地 → BJ CLOSED；BK (D) 转已触发**·PR [#294](https://github.com/JunoChenZt/subagent-for-investment/pull/294) ✅ 合 main `d423dad`）：配额族 **13 → 12**（非配额族 14 / 破例 16 不变）、🔴 0。BJ 全部五步做完 close-by-completion；BJ.5 = (a) 保持 (b) 填错字起步报错 (c) 开关封闭集合 (d) 未登记键 WARN (e) 归并折中，均按用户 2026-09-14 逐类裁决。⚠️ 翻案一条旧契约（#210「不得在 import 期抛」，理由只是「整包导不进」= 现在要的效果）。**BK 判据 (D) 随 BJ 收口满足 → 🔔 已触发、待用户裁重评形状。**
>
> **📌 更新 2026-09-14（第 4 笔·**`PRICE-V4PRO-CUTOVER` 到期处置完成 → CLOSED**）：非配额族 **15 → 14**（配额族 13 / 破例 16 不变）、🔴 0。到期当天冒烟跑批的告警响了、按登记处置改完（v4-pro 与 flash 同价·登记删除·测试改锚合成条目）；「回包仍报 v4-pro」由推断转实证。**判据是代码强制型这一设计被验证**：到期不靠人想起来。
>
> **📌 更新 2026-09-14（第 3 笔·**BJ 配置读取机械化 BJ.0–BJ.4 落地**·PR [#292](https://github.com/JunoChenZt/subagent-for-investment/pull/292) ✅ 合 main `3aeb118`）：**三项条目数全不变**（配额族 **13** / 非配额族 **15** / 破例 **16**）、🔴 仍 0 条、零新增零关闭；**BJ 不 close**（BJ.5 运行时「读不到即报错」五族逐族待裁）。
> **做成了什么**：`committee config explain <KEY>` 答值 / 来源层 / 走没走兜底，问 Python 符号名当 env 名**报错并给真名**（06-16 事故复现 = 首条靶测）；名册从源码派生 + `lint_env_registry` 对账（WARN 试用·首轮查出模板缺 40 键 / 多 2 死键，已收口）；段式跑起步写 `config-snapshot.json`（真跑冒烟 ✅）；指南 / runbook / 坑表改口读快照或跑命令。
> **闸门点名两条均判不算**：BL（动 graph.py = run 目录起步定一次，非并发编排）· BM（动 runbook = 查法两行，非现状章节·用户裁）。**BK (D) 半满足**，等 BJ.5 裁完重评。
> **教训两条进 memory**：派生器两处盲区都是**真仓对账**撞出的、合成靶测没抓到（坑表④ +2）；全套跑批期间别改源码。详见 [复盘](../retro/S2/BJ_2026-09-14.md)。
>
> **📌 更新 2026-09-14（第 2 笔·**首轮判据命中 triage —— 12 条逐条查证**·PR [#291](https://github.com/JunoChenZt/subagent-for-investment/pull/291) ✅ 合 main `fb8dbd6`）：**三项条目数全不变**（配额族 **13** / 非配额族 **15** / 破例 **16**）、🔴 仍 0 条、零新增零关闭。
> **查法**：不认「文件撞上」，逐条查**判据点名的那一块**动没动（读 diff，不读提交标题）。
> **结果 3/1/2/6**：**3 条真满足** —— `DEFECT-CTX-BAG-SHAPE`（两格子字段已实际删除·提交标题即本条编号）· `DEFECT-WISBURG-PADDING`（回核层新增 571 行含研报处理）· `DEFECT-RETRY-ADVICE-FALSE`（判据本就是文件级）⇒ **用户裁「先只订正账面、开工时机另议」**，三条状态改 🔔 已触发、**判据文字一字未改**。
> **1 条已处理**：`DEFECT-ANCHOR-FALSEPOS-HARDBLOCK` 09-10 已裁「再留一轮」，本轮不重复裁。
> **2 条不算触发**（用户裁）：`BK` / `DEFECT-D5-COUNT-AS-VALUE` —— 那两笔**只加注释、明写"故意不动"**，行为未变；但把注释里那条新事实记进账面（BK：classify 超时 15 秒是**每次尝试**的上界，底层 `max_retries=2` ⇒ **最坏 ≈45 秒**）。
> ⚠️ **6 条误报，同一个病**：`BI` `BP` `BS` `BX` `BL` `AF-residual` —— **判据点的是「文件里的某一块」，而本闸只看得见「哪个文件动了」**。处置按用户裁「能收的收、收不了的标明」：`BI` 由整个源目录收窄到 wisburg 单文件（同一份改动下**不再空喊**）· `BP` 由整个 `common_context/` 收窄到两份文件 · 其余 5 条加 `〔粗粒度：…〕` 标注，命中时输出自带「可能空喊」。
> **噪音实测 13 → 12 条**（收窄消掉 1 条），其中 **5 条带粗粒度标**。**这是这道闸的能力上限，不是配置没写好** —— 按「块」声明它做不到。

> **📌 更新 2026-09-14（第 1 笔·**判据命中检测接线（闸门矩阵第 0.5 层）+ BJ 状态订正**·PR [#290](https://github.com/JunoChenZt/subagent-for-investment/pull/290) ✅ 合 main `200007a`）：**三项条目数全不变**（配额族 **13** / 非配额族 **15** / 破例 **16**）、🔴 仍 0 条、`lint:active-count` 不动。上方 09-11 第 1 笔的「⭐ 当前最新」标**同笔清掉**。
> **本笔不新增、不关闭任何条目** —— 只做两件事：① 给 21 条活跃条目的备注格补机器可读的监视声明（〔监视 …〕/〔不可监视：…〕），② 把 **BJ 订正为「已触发」**并记用户裁决「现在做」。
> **起因（一手）**：BJ 的 (B) 自 2026-08-07 起 **9 次提交命中**，其中 2 次在 **08-31 完整 triage 之后**，账面却一直写「未触发」。判据没坏，**坏在撞上时没有任何环节出声** —— 事件型判据的立论是"迟早会被自然撞上"，而"撞上"至今只靠人当场想起来。
> **同形态第 2 次**：08-31 过账已记过「条目自己的触发条件满足了却没人回看」并写明"再撞一次即提立"。**用户 2026-09-14 裁：不立条目**（再立一条 = 又添一笔靠人记得去看的账，正是要治的病），改为接线 + 焊进 [§4.2](#42-触发条件命中后的处理)。
> ⚠️ **覆盖面要如实读**：28 条活跃条目里，本闸只看得见 **19** 条（12 条判据已写明位置 + 7 条待补声明）；**9 条结构上看不见**（等的是部署动作 / 阶段完成 / 运行时现象），已在闸门每次输出里点名列出 —— **只报命中不报盲区 = 再造一块假绿**。

> **📌 更新 2026-09-11（第 1 笔·**成本口径缺口修复 + 立 1 条到期型条目**·PR [#288](https://github.com/JunoChenZt/subagent-for-investment/pull/288) 合 main `613952e`）：配额族 **13 不变**（新条目属非配额族）、非配额族 **14 → 15**（+`PRICE-V4PRO-CUTOVER`）、破例 **16 不变**、`lint:active-other-count` 同步改 **15**、🔴 仍 0 条。上方 09-10 第 14 笔的「⭐ 当前最新」标**同笔清掉**。
> **#288 = 价目表认不出改了名的模型**：DeepSeek 2026-09 起把回包里的模型名从 `deepseek-v4-flash` 换成 `deepseek-flash`，价目表没跟上 ⇒ 那批调用一律按 $0 落账。**要害在于配置侧对账全绿** —— 配置里一直写 `deepseek-chat`（在册），变的是**回包报的名字** ⇒ **对着配置核 ≠ 对着实际发生的事核**，守卫必须锚在响应侧。补键 + 把两个活跃键刷到官方现价（取高峰档上界）+ 三处可见性（构造 LLM 时 / 落账时 / 归档 `unpriced_models`）。
> 🔴 **合并前 review 坐实 8 条**（§2.11.9：8 = 修 6 + 明确不做 1 + 订正 review 自身说法 1）—— **最重一条 = 自称的三道闸全没盖到事故现场那块屏**：分段成本表与累计行是**各自独立渲染的两段代码**，只补了后者；根因是 `if cost:` 把「算不出钱」与「真没花钱」当同一回事（已沉淀 auto-memory·同族见 `feedback_none_vs_truthiness_numeric_gate`）。**明确不做 1**：`oc/` 聚合商那条路送出去和回包都是裸名 ⇒ 按原厂直连价算钱还写 `partial_cost: false`（**比记 $0 更糟 = 一个自信的错数**），实际 `.env` 零使用，用户裁「暂不治、只留记录」。**订正 1**：review 称 v4-pro 有「2515 次历史调用」，实测 tracked `calls.jsonl` 为 **367 次**，2144 那个数按段式断点求和**重复计**（seg9 断点含 seg8 全部记录）。
> ⚠️ **新条目 `PRICE-V4PRO-CUTOVER` 属非配额族、不占 lettered 配额**；判据为**代码强制的事件型**（到期后每跑必告警），非「将来有人回头看」的死信号。
>
> **📌 更新 2026-09-10（同日第 14 笔〔⚠️ 2026-09-11 第 1 笔顺手清掉本行原「⭐ 当前最新」标〕·**CRED.1.G4 落地 = 簇 1 最后一个实现子项**·PR [#286](https://github.com/JunoChenZt/subagent-for-investment/pull/286) 合 main `0e297ef`）：**条目数三项全不变**（配额族 **13** / 非配额族 **14** / 破例 **16**）、`lint:*-count` 不动、🔴 仍 0 条。
> **#286 = CRED.1.G4**：报告出门前那道「证据抄错了」硬拦，历史 268 份归档**响过 5 次、5 次全是误报、零次真错**，唯一一次真切掉执行计划（G7）拦的是一句完全正确的话。**D4 用户当日裁**：D4-a = **方案 B**（比较之前**先拒绝比不可比的** —— 年份免检〔带价位守卫〕/ 百分比↔小数归一 / 单位缩写免检 / 三元组可见性）；D4-b **不是设计稿原列的二选一**，改裁为**规则直接上 + 异模型复核员**：机械判搬运错后由**与产出该 fact 的角色不同 provider 家族**的模型复核，判 `false_positive` → **撤硬拦、`execution_plan` 保留、`execution_plan_caveat` 打「存疑」标**；`unsure` / `true_error` / 调用失败 / 不独立 / 预算用尽 / kill-switch 关 → **一律维持硬拦**。
> 🔴 **这是仓内第一次显式越过 G5 誊写核查焊死的「只降不升」** —— 用户显式裁定的例外，三前提焊在代码（独立性 / 输入隔离 / 输出封闭），且**只能撤到「存疑」档、没有干净放行的代码路**。
> ⚠️ **条目 `DEFECT-ANCHOR-FALSEPOS-HARDBLOCK` 不 close** —— 随 **1.G5** 簇 1 收口统一处置；剩余项 f16 类「推算比值挂原始计数编号」规则层不治、生产上由复核员承接（冒烟判对），候选 ③ 分析师侧程序校验仍留账。
> **合并前 review 坐实 10 条·全部当场修**（§2.11.9：坐实 10 = 修 10 + 记账 0 + 明确不做 0）—— **三条要害同一根因：这条红线例外赖以成立的防线，在真实配置下是空的**。① 独立性守卫比的是 tier 兜底常量而非 per-role 实配（`.env` 里 `COMMITTEE_MODEL_BEAR=gemini-2.5-pro` 是未注释实配）⇒ 会在「gemini 复核 gemini 自己写的数字」时判独立；② `oc/<model>` 自成一族 ⇒ 同一模型换写法骗过守卫；③ 提示词范例恰是「撤硬拦」那一档 + 解析取第一个 JSON ⇒ 模型复述格式即撤拦（**实测复现**）。其余七条：年份守卫拿整句 search（**让本条要治的 G7 误报复活**）/ 单位缩写误吃 `5 M&A`·漏抓 `1.6T` / 百分比归一只看形状（`0.03 ↔ 3` 真错被静默放过）/ 同步调用卡 async 事件循环 + 无条数上限 + `attempts` 语义写反 / 异常被写成「未配置复核员」/ 新事件类型未进流式白名单 / 收口四项。**已沉淀坑表 §3.2 🔴**：守卫要锚在它真正要守的那个对象上。
> **验证**：靶测 98 → **134 条**（十修逐条回归 + 两向反例表）· 全套 **4317 passed** · 真模型两向冒烟 **8/8**（十修后重跑·8 条独立性守卫全部实跑通过）**已归档** [cred-1-g4-review-smoke-20260910](../observations/cred-1-g4-review-smoke-20260910/FINDINGS.md)。⚠️ **仍未验证**：自然真阳性 = 0，复核员在**真实发生**的真抄错上的表现没测过（8/8 里真错三条是合成的）；未跑整链 e2e（留 1.G5）。
> **回填清单（§2.9.4 · 8 格）**：① 条目正文 ✅ · ② 引用条目 —— N/A（宽 grep 只命中本条）· ③ 跑批指南 ✅（Q1-Q8 口径）+ 质量门 Q8 行 ✅ · ④ 验收判据表 ✅（§4 ④ 块 + 承重边界表 + 演进历史）· ⑤ 观察点表 —— N/A（无 `O-*` 涉及）· ⑥ 代码注释 + gate-mechanisms-map + dataflow 两张字段表 ✅ · ⑦ S2 §4.7.6 状态行 + 子项行 + 簇级设计 pass ✅ · ⑧ auto-memory ✅。
> **retro（goal 级·触发 2/4/6）**：[docs/retro/S2/CRED-1.G4_2026-09-10.md](../retro/S2/CRED-1.G4_2026-09-10.md)。**下一步 = 1.G5 簇 1 收口**（段式 e2e 佐证 · 抄录影子分歧 + 复核员记录零也写零 · close 4 条 · R7 · retro）→ 簇 2 拆解须用户确认。

> **📌 更新 2026-09-10（同日第 13 笔〔⚠️ 同日第 14 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·**CRED.1.G2 落地**·PR [#285](https://github.com/JunoChenZt/subagent-for-investment/pull/285) 合 main `163337a`）：**条目数三项全不变**（配额族 **13** / 非配额族 **14** / 破例 **16**）、`lint:*-count` 不动、🔴 仍 0 条。
> **#285 = CRED.1.G2**：风险闸 G1 数「强信心背后有几条证据」时，把「某某源报了 503」这类故障提示也数成证据。按 D5 做**影子对账**：旧口径照旧驱动硬拦；同时按「排除表①登记为错误形态的条目」再算一遍，不一致就发 `G1-shadow`（恒 warning·details 带被排除条目登记形态 + role 级 `would_block` + 闸级 `would_newly_block`）。**影子只给用户看**（复审修·`is_shadow` + `llm_facing_findings` 一处过滤：不进决策者提示词 / 回应 pass / 打码豁免）。
> ⚠️ **条目 `DEFECT-REVIEW-ERROR-AS-DATUM` 不 close** —— 转「影子试用中」。**R5 核到 main 的事实**：设计稿列的两种错误登记形态**今天在表①里都出现不了**（MCP 错误抛异常整源跳过 / fred 空结果 0 引用 / wisburg 降级留痕进 `_meta`）；109 份主干归档：证据引用错误登记 **3 条·同一跑**、引用空值登记 **0 条** ⇒ 空值形态刻意不纳入；**新鲜跑批预期零分歧**，识别器只覆盖历史归档那一种措辞。升硬拦判据不变：每次「本该拦」（闸级 `would_newly_block`）全部人工坐实零误拦，≥3 跑是地板。
> **合并前 review 十修（`0c90632`）**（§2.11.9：坐实 10 = 修 10 + 记账 0 + 明确不做 0）—— 最重一条 = 影子走了正式 finding 通道 → **观测器污染被观测的决策**；已沉淀坑表 §3.2。**复审延伸两项用户裁「暂不做」**（分诊 D3 切共享认章 / 登记边界加关卡）—— 唯一去处 = 条目延伸块。
> **回填清单（§2.9.4 · 8 格）**：① 条目正文 ✅ · ② 引用条目 —— N/A（宽 grep 只命中本条）· ③ 跑批指南 ✅（⑧/⑨ 影子抄录行·看闸级 `would_newly_block`·随 PR）· ④ 验收判据表 ✅ · ⑤ 观察点表 —— N/A · ⑥ 代码注释 ✅（随 PR）· ⑦ S2 §4.7.6 + 设计 pass + risk-gate-design B.16.2 前向注 ✅ · ⑧ auto-memory ✅。
> **retro（goal 级·触发 3/4/6）**：[docs/retro/S2/CRED-1.G2_2026-09-10.md](../retro/S2/CRED-1.G2_2026-09-10.md)。**下一步**：**D4 裁** → 1.G4 实现 → **1.G5** 簇 1 收口（段式 e2e 佐证·抄录影子分歧零也写零·close 4 条·R7·retro）。

> **📌 更新 2026-09-09（同日第 12 笔〔⚠️ 09-10 第 13 笔顺手清掉本行原「⭐ 当前最新」标〕·**CRED.1.G3 落地**·PR [#284](https://github.com/JunoChenZt/subagent-for-investment/pull/284) 合 main `e7fe42b`）：**条目数三项全不变**（配额族 **13** / 非配额族 **14** / 破例 **16**）、`lint:*-count` 不动、🔴 仍 0 条。
> **#284 = CRED.1.G3**：审计那道「出处能不能核这个数」的闸，原先挂在「数值已提取」上 —— 数值没抽出来时整支跳过，正文写着「2026Q1 营收 194.96 亿元」的 fact 照样盖通过章。现改为：数值为空 + 正文剥掉出处标记与四类有限语义噪音后仍含数字 → `audit_notsure`（**只降不升**·方案 C 用户当日裁）。真实表①回放主干 25 跑 1508 条事实：降 **48/139 passed = 34.5%**、漏抓带量纲真量值 **0**。
> ⚠️ **条目 `DEFECT-NUMERIC-VALUE-NULL-BYPASSES-AUDIT4` 不 close** —— 本 PR 只修「绕过」半边；**剩余项 = pass0 提取器漏值**（139 条 passed 里 35 条带量纲真量值没抽出 `numeric_value`·下游兜底不是治本），随簇 1 收口 **1.G5** 统一 close。
> ⚠️ **合并前 review 抓出 5 条、全部当场修（五修）** —— 判据两头都偏：漏抓「1920 美元 / 118000 万元 / 50 日线」这类真量值（裸年份与「任何 6 位数」把它们当噪音吃了·根因 = 注释说复用 `base.py` 老先例、却只抄正则没抄它那套「带货币/单位/小数点就不算噪音」的守卫）；误伤「引了编号的定性句」（剥标记只认方括号规范形，认不出裸写 `REF#Y-006` 与大小写漂移 `[W#Macro-2-1#n1]`，残留数字把纯定性 claim 降了档）。**§2.11.9 去处：坐实 5 = 本 PR 修 5 + 记账 0 + 明确不做 0**（对得上）。
> **回填清单（§2.9.4 · 8 格逐项）**：① 条目正文 ✅ 改（09-09 块状态 + 剩余项）· ② 引用该结论的其它条目 —— N/A（宽 grep `CRED.1.G3` / `cred-1-g3` / 「PR 待合」只命中本条）· ③ 跑批与操作指南 —— N/A（不改跑法）· ④ [验收判据表](e2e-acceptance-standard.md) ✅ 改（③ 块状态转 ✅ 已合）· ⑤ 观察点表 —— N/A（未动观察点；段间 ⑧ `audit_passed ≥ 50%` 校准注已在 ③ 块内）· ⑥ 代码常量与注释 ✅ 改（`audit_node.py` 注释数字统一到 48/139 定稿·随 PR）· ⑦ [S2 §4.7.6](../roadmap/S2.md) ✅ 改（G3 行 → DONE + 簇 1 进度行）+ [设计 pass](../plans/CRED-可信度地基三簇-设计pass-2026-09-08.md) 台账行 ✅ 改· ⑧ auto-memory ✅ 改（`project_cred_cluster1` + `MEMORY.md` 索引行）。
> **retro（goal 级·6 条触发命中 2/3/4/6）**：[docs/retro/S2/CRED-1.G3_2026-09-09.md](../retro/S2/CRED-1.G3_2026-09-09.md)。
> **下一步**：**1.G2**（风险闸影子对账·D5 已裁）→ 1.G4 等 **D4**；簇 1 收口 **1.G5**（段式 e2e 佐证 + close 4 条 + R7 + retro）。**节点级 retro（CRED.retro）仍未到时点** —— 簇 1 尚有 G2/G4/G5，簇 2/簇 3 未开工。

> **📌 更新 2026-09-09（同日第 11 笔〔⚠️ 同日第 12 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·**CRED.1.G1 落地 + G4 设计稿入库**·PR [#283](https://github.com/JunoChenZt/subagent-for-investment/pull/283) 合 main `fb6dcee` · PR [#282](https://github.com/JunoChenZt/subagent-for-investment/pull/282) 合 main `abda356`）：配额族活跃 **13 不变**（DEFECT 族不占 lettered）、非配额族活跃 **15 → 14**（`DEFECT-GATE-NA-AS-PASS` ✅ close-by-completion）、破例累计 **16 不变**、`lint:active-other-count` 同步改 **14**、🔴 仍 0 条。**
> **#283 = CRED.1.G1**：终局质检「没查到」不再印 PASS —— 改 `N/A` 档、分四成因、**判到数字层**（探针里「计划对象在但买入价空」45/75 = 空过大头）。53 份在册归档回放：只 PASS→N/A（Q3 38 · Q4 25），**整体判定变化 0 份**、cli exit 不变。⇒ 条目两条任务全兑现，close。
> ⚠️ **合并前 review 抓到一个真 bug 并已修**：判「填没填」用真假值 ⇒ `0` 占位符被读成「没填」，在册 `run-pr8a-q6_*`（自陈「设为 0 占位」）**FAIL→N/A、整份 FAIL→WARN**，与「fail 面零变化」相反。修 = 判 `is None`；并补 6 条靶测（含拿真归档跑整门那条）。**初版守护挑了 `{0.0, 1.0}`——含真值故照旧绿**，教训沉淀进 memory。
> **#282 = CRED.1.G4 设计 pass**（纯文档·**不是已批准方案**）：268 份探针坐实 check① 硬拦路 **5 响 5 误报 0 真错**、EXEC-FLOOR 历史硬拦仅 G7 一次即误报。推荐方案 B（年份免检 + 100× 归一 + 词表补缩写 + 可见性）。**`DEFECT-ANCHOR-FALSEPOS-HARDBLOCK` 不 close** —— 落地等 **D4**。
> **🔻 仍待裁**：**D4**（G4 三方案 A/B/C + 直接上还是配影子告警）。**D5 已裁**（G2 = 影子对账式告警试用）。
> **下一步**：**1.G3**（改动四空值 → notsure）已解锁（原本等 G1 合）；1.G2 按 D5 走影子对账。
> **📌 更新 2026-09-09（第 10 笔〔⚠️ 同日第 11 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·**CRED.1.G0 登记 PR [#281](https://github.com/JunoChenZt/subagent-for-investment/pull/281) 合 main `e096924` + G4 设计 pass 提前出**）：**条目数三项全不变**（配额族 13 / 非配额族 15 / 破例 16）、🔴 仍 0 条。
> **#281 落地**：簇 1 四项先登记后动码；含 **D5 裁定回填**（G2 = 影子对账式告警试用·升硬拦看分歧全部人工坐实零误拦）+ 用户复核两修（(a) 档两份全中·D5 清单漏改）。
> **G4 设计 pass**（用户裁「提前起」）→ [CRED-1.G4](../plans/CRED-1.G4-绑错判别力-设计pass-2026-09-09.md)：268 份主干归档探针，check① **硬拦路 5 响 5 误报 0 真错**、EXEC-FLOOR 历史硬拦仅 G7 一次即误报。四候选实测判定 + 新增三道 → **推荐 B（年份免检 + 缩写词表 + 百分比/小数归一 + 可见性）**，不加任何「猜绑错→放行」路。**等 D4-a / D4-b**。详见条目 `DEFECT-ANCHOR-FALSEPOS-HARDBLOCK` 顶部 09-09 块。

> **📌 更新 2026-09-08（同日第 9 笔〔⚠️ 09-09 第 10 笔顺手清掉本行原「⭐ 当前最新」标〕·**九条排入主动清理计划 · 立节点 [S2 §4.7.6 CRED](../roadmap/S2.md)**）：**条目数三项全不变**（配额族 13 / 非配额族 15 / 破例 16）、🔴 仍 0 条。
> 第 5–8 笔把表对齐、逐条复核之后，用户问「接下来该按什么顺序、怎么处理」。回答的前提是承认一件事：**剩下 28 条没有一条是「到期该做」的，全是「下次动到那块代码时顺手清」** —— 所以不是排待办顺序，是排**主动点火**的顺序，而点火本身是个选择。
> **用户裁（U1–U3）**：只主动点两簇（可信度地基）+ 簇 3 也做；其余 **19 条保持事件型不碰**。设计 pass = [CRED-可信度地基三簇-设计pass-2026-09-08.md](../plans/CRED-可信度地基三簇-设计pass-2026-09-08.md)（双层写法·逐条 file:line 现状·goal 拆解·坑表对照·账目归位）。
> **九条 → 三簇**：**簇 1 GATE-TRUTH**（质检说了假话）= `DEFECT-GATE-NA-AS-PASS` · `DEFECT-REVIEW-ERROR-AS-DATUM` · `DEFECT-NUMERIC-VALUE-NULL-BYPASSES-AUDIT4` · `DEFECT-ANCHOR-FALSEPOS-HARDBLOCK`；**簇 2 EVID-TIME**（证据的时效与身份）= **BO** · **BP** · **BS** · `DEFECT-D5-COUNT-AS-VALUE`；**簇 3 DEBATE-SIGHT** = `DEFECT-DEBATE-STALE-PRIOR`。**BK** 顺手部分落地、不关。
> ⚠️ **这九条的触发条件一个字不改** —— 计划只是「我们会主动去动那块代码」，届时判据会自然响，走正常 close-by-completion。**不是提前评估、不是为腾配额**（§4.4 明禁的两种形态都不是）。
> **为什么是这九条**：它们治的是「**我核过了**」这句话本身是不是真的（质检章 / 证据日期 / 辩论数字来路）；其余 19 条是覆盖面与体验（认不出东京股票、提示语不准、研报给 20 篇……），不会让读者**误信**一份报告。**S2 收口前这一层得是实的。**
> **簇 2 高风险**（动 `Reference` 数据形态·流经五处），**须用户确认拆解后开工**；簇 1 / 3 可自走（各自带 🔲 待裁 goal 除外）。待裁 D1–D4 见设计 pass §2.2。
> **配额预告**：九条全 close → 活跃 **28 → 19**（配额族 13 → **10**）。

> **📌 更新 2026-09-08（同日第 8 笔〔⚠️ 同日第 9 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·**PR [#280](https://github.com/JunoChenZt/subagent-for-investment/pull/280) 复核收两条真 finding·条目数不变**）：lettered 活跃 **13 不变**、非配额族 **15 不变**、破例累计 **16 不变**、🔴 仍 0 条。**
> 用户拉下 PR 实跑复核，收两条 —— **都是本 PR 自己引入或自己许下的**，形态**恰是本 PR 要治的那种病**（看不见的东西读起来和没问题一模一样）。
> **① 标题里出现一个 ✅，条目就又隐身了（是倒退，不只是没堵严）**：为认出「光秃秃一个 ✅ 表示关闭」的写法，关闭判定放得太宽。实测 —— 标题带 ✅ 且表里无行的**活跃**条目：**本分支 0 报告 / main 报 2 条**。而第 5 笔 banner 里写的「Check 9 堵住了这个坑」**是假的**：Check 9 要拿表里那一行来比对，本坑的形态恰恰是**没有行**。⇒ **真修法 = 关闭判定必须带关闭词**（`CLOSED`/`CANCELLED`/`moved to §3`/`close-by`/`·close <日期>`），光秃秃一个 ✅ 不算。上面第 5 笔那两句已就地划掉订正。
> **② 说明里那句「中文命名的条目会响」是假保证**：实测**两个方向都静默** —— 标题解析不出编号所以进不了缺行检查；表格行的编号也是中文、被当成续行，孤行检查同样看不见。⇒ 新增 **Check 10**：编号解析不出的开放条目**指名道姓报出来**。文档里那句假保证已收回并写明「不许在没有测试的情况下加回来」。
> ⚠️ **一处值得记的自伤**：我先前写的测试里，有一条把「光秃秃一个 ✅ = 已关闭」**当成预期行为钉住了** —— 这正是回归能拿到满堂绿的原因。修正时该测试当场变红，**改的是测试不是预期**；并补了反向用例（`test_a_bare_checkmark_is_not_a_closure_mark`）。**教训：写检查的人给自己的检查写测试时，最容易把当下行为误当应然。**
> **本笔零条目变动**，只动脚本 + 测试（36 → 53 → **65**）+ 上方两处假断言。

> **📌 更新 2026-09-08（同日第 7 笔〔⚠️ 同日第 8 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·**两条边缘项裁定：BD + NAMING-EXTKREFS 关掉**）：lettered 活跃 **14 → 13**（余 2）、非配额族活跃 **16 → 15**、破例累计 **16 不变**、🔴 仍 0 条。**
> 第 6 笔留的两条待裁项，用户当日裁：**NAMING 直接关 · BD 补注释再关**。
> **`NAMING-EXTKREFS` 关掉零损失** —— 将来动它的人需要知道的（「这个 external 不是联网外源」「改名要动存档序列化」）**已经完整留在字段上方的注释里**；本次并补一句「条目已关·本注即真值源」，免得后人去翻一个已关条目。
> 🔑 **`BD` 关之前先把知识挪进了代码，这是关它的前提条件**：在此之前 [as_of.py](../../src/committee/as_of.py) **只字未提**「英文日期一概不认、今天靠 Worker 在进仓前转掉」这件事 —— 就这么关等于把知识扔了。现已写进 `_normalize_as_of` 的说明，含「接第二个上游时补在这里」的指路。
> ⚠️ **BD 与前面五条不是一回事，别混着读**：那五条是**判据失效**（等的事情不会再发生）；**BD 的闹钟是好的**（「接第二个吐英文日期的上游时」会被自然撞上），关它纯粹是「值不值占一个配额位」的取舍。∴ 本条的 close 理由写的是「反向条件已成立」，不是「判据挂死信号」。
> **本轮（第 5–7 笔）合计**：一览表从**漏 24 条**到全账在册，活跃 **35 → 28**（配额族 15 → 13·非配额族 20 → 15），close **7 条**、删 **1 条**违规判据、守表脚本从看不见第二族到全族守住。

> **📌 更新 2026-09-08（同日第 6 笔〔⚠️ 同日第 7 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·**逐条复核后 close 5 条 + 删 1 条违规判据**）：lettered 活跃 **15 → 14**（余 1）、非配额族活跃 **20 → 16**、破例累计 **16 不变**、🔴 仍 0 条。**
> **起因**：第 5 笔把表对齐后，用户要求「每条重新 review 一遍，看哪些是真需要的、哪些其实已经不需要了」。**逐条进代码核**（不是照条目复述），35 条判成：22 条真在 · 5 条建议关 · 1 条建议砍半 · 2 条边缘 · 5 条治理常驻。用户当日裁：**5 条全关、砍半照办**。
> **close 的 5 条，共同点是「事情已经不成立」而非「还没轮到」**：
> **P**（缓存降级语义）—— 缓存**在生产路径上从来没被接上过**（节点自陈 + 全仓 `FactCache` 只在测试里实例化）⇒ 失效形态不可能发生。
> **T10 / #4**（精确绑定）—— 它治的「过度打码」已由 GATE-B 门重定义解决（21→0）⇒ 原目标消失；判据又挂在没人量的比例上。
> **`DEFECT-R5-02`** + **`DEFECT-R5-04`**（印证池 / 印证语义）—— 支柱1 已修；两者共同的目的「放开 web verified」已随 PR2 关门放弃。⚠️ 两条**失效方式不同**：R5-02 是等不到（判据挂死信号），R5-04 是**等到了也没意义**（前件已成立、目的消失）。
> **`DEFECT-AUDIT-INTENT`**（审计定位）—— 议题已收口：主体 07-03 定稿、目标态三检查 07-14 拍板砍、两个触发前件都已成为过去。
> **删的那半**：`DEFECT-DSML-PARSE` 的**改进 B**（「待评估排期」= [§4.1](#41-新增-backlog-条目) 禁止形态）就地删除；**命题没丢** —— 「盯通用降级信号超阈告警」正是 [BK](#bk-静默降级可见化--系统悄悄降级时必须留痕2026-08-07-闸门矩阵第-2-层挂起) 的题目，移交承接、不各记一份。改进 A（第二种怪格式出现时）判据合法，保留。
> **R7 全仓收口**：宽 grep 扫过 5 个名字的全部引用。**live 断言就地改**（[number-provenance-endgame.md](number-provenance-endgame.md) 分流表两处仍写「挂起 / 条目不动、按原触发条件走」）；**历史 / 规划 / retro / handoff / observation 一律不动**（point-in-time 记录）；**代码里的出处注释也不动** —— [base.py](../../src/committee/agents/base.py) 那句「R5-02 支柱1：池未 scope」是在解释这段代码**为什么存在**，条目关掉不使它变假。
> ⚠️ **两条边缘项本笔未动**（用户尚未裁）：**BD**（英文日期）与 **NAMING-EXTKREFS**（字段名误导）。已给出建议：NAMING 直接关（知识已完整留在字段上方注释里，关掉零损失）；BD 关之前**得先补三行注释** —— 今天 [as_of.py](../../src/committee/as_of.py) 里**只字未提**「英文写法不认、靠中转层在进仓前转掉」，就这么关等于把知识扔了。

> **📌 更新 2026-09-08（同日第 5 笔〔⚠️ 同日第 6 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·**一览表漏账对齐 + 检查脚本扩到认第二族编号**）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` **不动**、🔴 仍 0 条；新增 `lint:active-other-count=20`。**
> **一句话**：这张表**漏记了 24 条**——它们只有 §1 正文、表里从来没有行。漏了不响，因为守表的脚本 ID 正则是 `[A-Z]{1,2}`，`DEFECT-` 开头的整族对**每一项检查**都不可见。
> **起因**：用户 2026-09-08 要「翻 backlog 找下一个活」；翻的时候发现按表挑活挑不了 —— 表本身数不全。
> **补录的 24 条里，两种情况各半**：**11 条其实早就做完**（正文状态行 6 月 / 7 月 / 8 月就标了 ✅ 并带合并 SHA，只是从没销账进表）；**13 条确实还开着**。
> **同一把梳子还梳出三处**：① `DEFECT-COMMODITY-AS-TICKER` 把 ✅ 埋在「未触发（…✅ **CLOSED**）」的括号里 —— 表头约定明写 ✅ 须顶格，已订正；② `DEFECT-CTX-BAG-SHAPE`（7813 字）与 `DEFECT-D5-COUNT-AS-VALUE`（1177 字）整条挤在备注格里、超 1000 字上限 —— 已**逐字照搬**拆出 §1 正文；③ `DEFECT-RETRY-ADVICE-FALSE` 是真轻条目，补 `〔轻条目〕` 声明。
> **⚠️ 配额口径没动**：非字母编号族**不占** [§4.4](#44-backlog-数量上限) 的 15 格（条目自己一直这么写：「DEFECT-* 族、不占 lettered 配额」），所以两族**分开计数、各一个标记**。把两族并成一个数会静默撑大配额、并让历次破例账全错。
> **🔻 6 条判据待用户裁（本笔只登记、不替用户拍）**：`DEFECT-R5-02`（触发挂已关门的 PR2 / 长期 OFF 的 flag）· `T10 / #4`（触发挂一个没人在量的比例，且 GATE-B 后原目标已消失）· `DEFECT-AUDIT-INTENT`（两个前件都已成为过去）· `DEFECT-R5-04`（前件已成立，但父题目的已放弃）· `NAMING-EXTKREFS`（**没有触发条件**，§4.1 必填字段缺失）· `DEFECT-DSML-PARSE` 的改进 B（「待评估排期」= §4.1 禁止形态）。
> **脚本侧同批**（[scripts/lint_backlog.py](../../scripts/lint_backlog.py)）：ID 正则放开到两族 · 关闭判定认 ✅ / CLOSED / CANCELLED · 计数拆两个标记 · §6 对账仍只管配额族（§6 记的是配额进出账，非字母族从不进那本账）· **新增 Check 9** —— 标题读起来已关闭、行却还活跃 = 报矛盾（~~防「标题里碰巧有个 ✅ 就整条静默消失」这个新引入的坑~~〔🔴 **2026-09-08 同日第 8 笔就地订正 —— 上面这句「堵住」是假的**：Check 9 要拿表里那一行来比对，而本条要抓的条目**恰恰是没有行的那种** ⇒ 该坑当时并未被堵，且相对 main 是**倒退**（实测：标题带 ✅ 且表里无行的活跃条目，本分支 0 报告 / main 报 2 条）。真修法 = **关闭判定不再认光秃秃的 ✅、必须带关闭词**。Check 9 仍有它自己的用途（标题说已关、行却活跃），但不是这个坑的守卫。〕）。
> **为什么不去改标题补 ✅**：标题一改锚点就变，指向它的链接会集体失效（本仓刚清完一轮死锚点）。状态一律只写在触发状态格。

> **📌 更新 2026-09-08（同日第 4 笔〔⚠️ 同日第 5 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·**主线欠账清零** + 规划员超时线 40 → 85s、run 级上限 90 → 120s·PR [#279](https://github.com/JunoChenZt/subagent-for-investment/pull/279) 合 main `f8ea795`）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> **🎉 `DEFECT-CTX-BAG-SHAPE` 段式 e2e 欠账清零**：NVDA 首段跑通（零退化告警），**计划驱动那条建腿路径终于走到** —— 腿清单从兜底路由的 `unknown/-` 变成 `primary/verified`，选源理由从机器标签变成规划员写的人话，多余的 A 股腿消失。此前两跑验的都是兜底那一支。同跑顺带验到：**归档里已无影子字段**（#278 在真实跑批上成立）· `ticker=` 那行显示价（验了当日刚订正的读法）· 引用时效四源全在档内。
> **超时线怎么定的**：**先量后定**（登记项 ① 的纪律就是「动超时前先测」）—— 6 次实测 **28.0 / 30.5 / 36.0 / 36.7 / 41.0 / 67.4 秒**，40s 线吃掉 **2/6（33%）**，与条目原记「吃掉 1/3」对得上；而 08-28 定 40s 时**同一句问法**是 29.8–32.7s、6/6 在线内 ⇒ 🔴 **不是「当初线定错了」，是延迟本身变慢了、尾部几乎翻倍**。85 = 最慢 67.4 × 约 22% 余量（**沿用 08-28 同一算法**）。
> **顺带治一个病**：外层封顶硬写着 `40.0 + _CHECK_CAP` = **同一个数的第二份副本**（与 ⑯ 同病）—— **只抬内层不抬外层，外层先掐掉、表现成「改了没用」**。改成派生 + 守护，反向变异当场红。
> 🔴 **冷审三条（用户查·都坐实·都已处理）**：① **抬到 85s 把 90s 那本账撑破了、而我没算** —— 三笔最坏 116s，**光第一段就顶穿整跑上限**；🔑 **08-28 那次抬线专门算过这笔账并留了一张五项清单**（常量 / 外层封顶 / 钳制断言 / **两处注释** / **预算线数字**），**我做了前三项、漏的正是后两项 —— 清单就在那儿**。⇒ **用户当日裁：维持 85s、run 级上限 90 → 120s**。② **旁边还留着「40」文字副本**（用户列 4 处·复扫又抓到第 5 处），其中 `hi=40` **与代码直接矛盾**（照它调部署会以为设 60 不生效、其实生效）—— 全清。③ **「379–535s」被我写在讨论第一段预算的段落里** —— 用户追问「那是 seg1 需要那么久吗」才发现**我整场都在拿封顶值推、手上没有第一段的实测数**（归档不带时间戳）。
> ⚠️⚠️ **三条据实记的读法（宽 grep 与补测时撞见·全部写进 S2 §6.7 / DoD 判据行 / 代码注释）**：
> **(a)** §6.7 各 phase 预算加起来 **108s，本来就 > 90s** —— 那张表**自己内部就不自洽**，不是本次改坏的。
> **(b)** 三份验收报告实测**端到端 379–535s**，且三份都判「非 gate 条件、无 regression」⇒ **这条线长期是「目标」不是在守的闸**（代码里没有 run 级封顶·已核）。**别把「已抬到 120s」读成「现在跑得进 120s」。**
> **(c)** 🔑 **但 (b) 那个数是整跑、不是第一段**：**第一段实测 51.8s**、封顶 116s ⇒ **封顶留了一倍以上余量**；379–535s 的大头在后 8 段（8 分析师串行 + 3 轮辩论 + 10 投票，**一个都不在第一段**）。⇒ 「第一段吃掉整跑预算」**账面成立、实际耗时不成立**；抬这条线几乎不影响真实耗时（**超时才等到 85s，正常 30 多秒就回来**）。
> ⚠️ **形态两次记账（不立条目）**：**(i)** 抬承重线时**有现成的五项清单没照着走**（做了前三项）⇒ **上次同类动作留下的清单，这次要先翻出来逐项对**。**(ii)** **拿封顶值当耗时讨论了整整一轮**，直到被追问才去量 ⇒ **谈预算先问一句「这个数是上限还是实测」**，两者能差一倍以上。
> **§2.11.9 第四次实战**：**坐实 5 条 = 修 5 + 记账 0 + 明确不做 0**。
> **本笔按 [§2.9.4 八格清单](workflow/06-dod-and-evidence.md)走 —— 本次格 4 与格 7 都不是 N/A**：格 1 条目正文 ✅（登记项 ① 数字全部重写）· 格 2 本表 + 更新块 ✅ · 格 3 跑批指南 N/A（本次不动跑批口径；当日第 3 笔已单独订正过一处读法）· 格 4 **判据表 ✅**（[DoD](workflow/06-dod-and-evidence.md) P95 判据行 90 → 120 + 补实测注）· 格 5 观察点表 N/A · 格 6 代码注释 ✅（5 处「40」文字副本 + 预算算术 + 实测数）· 格 7 **路线图 ✅**（[S2](../roadmap/S2.md) §6.7 硬上限 + §7.4 指标 + §4.7.5 预算线 · [roadmap-v3.4](../roadmap/roadmap-v3.4.md) 两处 · [S3](../roadmap/S3.md) 指标 · [验收报告模板](workflow/10-verification-report.md) 两处 + XML 模板两处 · [AY 拆解](../plans/AY-decomposition.md) 加前向一句）· 格 8 memory ✅
> 🔻 **`DEFECT-CTX-BAG-SHAPE` 剩余**：⑨ ⑪ ⑫ ⑭ ⑰ ⑱ + 原登记项 2–7 + 读档手写白名单。**登记项 ① 已随本笔处理（超时线重定 + 数字回填）**；**段式 e2e 全部跑完** ⇒ **主线欠账清零，条目只剩事件型登记项。**

> **📌 更新 2026-09-08（同日第 2 笔〔⚠️ 同日第 4 笔顺手清掉本行原「⭐ 当前最新」标〕·**影子字段删除 ✅ = 主线只剩最后一跑**·PR [#278](https://github.com/JunoChenZt/subagent-for-investment/pull/278) 合 main `afa669b`）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> **做了什么**：PR2 降为影子的两个格子（`ticker_payload` / `macro_payload`）**从 schema 删除、归档也不再写**（用户当日裁「真删」）。真值只剩一份资料夹 + 一张腿清单。🔑 **旧档翻译收到读档入口、刻意不放回 dataclass** —— 字段只要还能当构造参数，就还会有人拿它当真值写，那正是它们拖了一整个周期没死掉的原因。
> **验收拿 main 上 tracked 的真实归档**（不是自造 fixture）：**145 份在册旧断点全部读得回来**（其中 141 份是只有旧格子的老档）· **护栏判定与 main 逐份对照 = 125 一致 / 20 不一致，与 main 基线一模一样、同一批文件 ⇒ 本次引入的差异 = 0**（那 20 份是 PR1 商品/指数修正的既有差异）· **trace 渲染逐字节对照 129/145 相同，16 份多显示信息、0 份丢信息**。全量 4052/0；四道 lint + CI 九道绿。⚠️ **未跑 e2e**，回放面由真实归档对照钉住，**不冒充**。
> 🔴 **冷审三条（用户查·都坐实·都已修）**：① **首版 trace 口径让 18 份旧归档丢掉价格显示** —— 我按"个股格子视图"写，黄金那种跑的金价整行消失，而段式审核正靠这行确认"价到底拉回来没有"；改按该行 docstring 自己写的用途（价格腿摘要）后变成"多显示 16、丢 0"。② **恒真断言 3 行 + 冗余 3 处** —— 机械替换留下的残渣（"资料夹等于它自己"），**留着会让人以为有测试盯着、其实红不了**，已全删；改用**语法树精确扫**复查（全仓 5 处命中：3 处本次残渣已清、1 处既有记账、`f != f` 与哈希确定性用例判为正当）。③ **手动 e2e 脚本漏改** —— 见下。
> 🔴🔴 **形态两次命中，都记在这里（不立条目）**：
> **(a) 「全仓扫」只扫了 `src/`** —— 漏掉 `scripts/`，而「我枚举全了吗」这句正是**上一个 PR（⑯）刚写进注释的教训**，隔一个 PR 原样重犯。⇒ **「全仓扫」要把 `src` / `tests` / `scripts` / `docs` 逐个点名，不能想到哪个扫哪个。**
> **(b) 说「修好了」之前没分清「能加载」与「能跑到那一行」** —— 首版只做导入自检，而坏掉的行在**函数体里**，导入根本走不到。用户追问「彻底修好了吗」后实查：同一脚本还有 **9 处读根本不存在的字段**（`ctx.classification` 6 处 —— 分类压根不在返回里；水印 `ref_tag`/`source_name` 3 处 —— 真名是 `ref_id`/`text_marker`），**崩得比首版改的那几行还早**。⇒ **验收要验「跑到那一行」，不是「它能加载」。**
> 🔑 **顺带堵上根因**：该脚本被闸门矩阵**显式豁免**自检（"需真实密钥与网络"）—— **豁免只对「要联网那半」成立**，打印结果那半不需要网络却跟着没人管，于是烂了很久无人知。新增 `test_manual_e2e_script_only_reads_fields_that_exist`（语法树核字段存在性·一秒跑完·不打网络）+ 防扫描器瞎掉自检；反向变异当场红。⚠️ **它的失败位置特别刁**：先做完最贵的部分（真调模型 + 真拉五源），**再**在打印那步崩 —— **烧完钱才发现跑不通**。
> **§2.11.9 第三次实战**：**坐实 6 条 = 修 5 + 记账 1 + 明确不做 0**（记账那条 = `test_portfolio_context.py:126` 同一条件写两遍·**既有**·本次未动该文件）。
> **本笔按 [§2.9.4 八格清单](workflow/06-dod-and-evidence.md)走**：格 1 条目正文 ✅（剩余项去掉影子字段删除）· 格 2 本表 + 更新块 ✅ · 格 3 跑批指南 〔**⚠️ 2026-09-08 同日第 3 笔订正：本格当时判 N/A 是错的**〕 → **✅ 已补**（[段式跑指南](../observations/e2e-runs/segmented-e2e-guide.md) ① context checklist 的 D3 行写着「`ticker=` 栏是旧个股格子影子视图，商品/指数问题它印 `-` 是对的」—— 影子删除后**这句反了**，商品/指数现在照样印价）· 格 4 判据表 N/A · 格 5 观察点表 N/A · 格 6 代码注释 ✅（trace 那条过期口径 + 多处 docstring 订正·行为一字未动）· 格 7 路线图 N/A · 格 8 memory ✅
> 🔻 **`DEFECT-CTX-BAG-SHAPE` 剩余**：⑨ ⑪ ⑫ ⑭ ⑰ ⑱ + 原登记项 1–7 + 读档手写白名单 + **段式 e2e 只剩 NVDA 首段** ⇒ **主线到此只剩那一跑**。

> **📌 更新 2026-09-08（第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·`DEFECT-CTX-BAG-SHAPE` **⑯ ✅ 已修**·PR [#277](https://github.com/JunoChenZt/subagent-for-investment/pull/277) 合 main `79aeef5`）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> **做了什么**：五源名单收成**一份名册**（`DATA_SOURCE_NAMES`），各处全部对着它点名，**且在模块导入期核** —— 漂开的那一刻整个进程起不来，而不是"跑出一次错的结果、然后被测试抓到"。#272 那道只是**两两比对的测试**（治的是"发现漂开"，不是"不会漂开"）。⚠️ 漂开的后果不是「少一个源」，是**错位一格**：校验放行了、构造认不出 ⇒ 那条腿被静默跳过，下游按位配对 ⇒ 之后每条腿都配到别人的身份，而腿清单承载基本面护栏与价格闸。**顺带堵一个新缝**：行情源必须走取价那条构造，否则它拿不到已确认标的、**静默回退去 query 正则抽码**（产物上只表现为"这条腿取的不是那只票"、不报错）。
> 🔒 **刻意没做的 —— 单一真值 ≠ 把所有名单合成一个**：`_THEMATIC_SOURCES` / `_ALL_DATA_SOURCES` 是**语义分组**，某个源该不该进去是**设计决定**，做成"新增源自动加入"等于替以后那个人做主 ⇒ 保持显式书写、只核"名字在册"，并加前提断言钉住 union **刻意不含 wisburg**（有人"顺手补齐"就当场红 —— 那是设计变更，该被看见）。
> 🔴 **冷审两条（用户查·都坐实·都已修）**：① **"散在四处"数少了 —— 还有第五处**（出计划那层的 `planner.VALID_SOURCES`·管「模型写出来的源名认不认」·不认整条丢掉）。**最该被看见的一点**：盯着它那道测试的 docstring 早就写着「防**第四份**手抄漂移」—— **仓里本来就把它算作副本，是盘点的人没数进去**；且首版那句"这种形态在结构上没有了"对该处**不成立**（那里仍是"靠测试发现"，而本 PR 自己论证过那是更弱的一档）。② **语义分组那道核，空的也算通过** —— `subset_ok` 只核"名字在不在册"，空集天然满足，分不清"故意只写两个"和"不小心一个没剩"；今天两份分组是写死字面量、不会自己变空，但**为以后复用**必须堵。已改成空名单一律拒。
> ⚠️ **口径订正（两处·正文与 commit subject 均按 point-in-time 不改）**：本条正文原写「散在**四处**」、合并后 main 上那条 commit subject 也写「**四张表**对着一份名册点名」—— **都少数了一处**，前向事实以条目正文那两处订正注为准。
> **验证**：全量 **4050 passed / 2 skipped / 2 xfailed / 0 失败**（4041 → 4047 → 4050·每步增量逐条对得上）；反向变异 **6 组全 KILLED**（源名改错 / 行情源不走取价构造 / 那道核关掉 / 少一个 / 多一个 / 分组变空 —— 其中四组的表现是**模块直接起不来**）；四道 lint + CI 九道全绿。⚠️ **未跑 e2e**（失效面由「导入期核 + 反向变异」钉住·**不冒充跑过一次真的**）。
> ⚠️ **过程记一笔（形态第 1 次·不立条目）**：首版全量是在我做变异实验的**同时**跑的 —— 仓里有测试从磁盘读源码 ⇒ 那一跑结果**不可信**，已掐掉重跑；第二轮改成"全量跑完之后再做变异、做完逐一还原并复跑"。🔑 **可迁移的判断**：**改源文件的实验与读源文件的测试不能并行**，哪怕它们看起来互不相干。
> **§2.11.9 第二次实战**：**坐实 5 条 = 修 5 + 记账 0 + 明确不做 0**，数目对得上。
> **本笔按 [§2.9.4 八格清单](workflow/06-dod-and-evidence.md)走**：格 1 条目正文 ✅（⑯ 标已修 + 两处口径订正）· 格 2 本表 + 更新块 ✅ · 格 3 跑批指南 N/A · 格 4 判据表 N/A · 格 5 观察点表 N/A · 格 6 代码注释 ✅（四段过期 docstring 已订正：两两比对守护三段 + 出计划那层"防第四份手抄"一段·**行为一字未动**）· 格 7 路线图 N/A · 格 8 memory ✅
> 🔻 **`DEFECT-CTX-BAG-SHAPE` 剩余**：⑨ ⑪ ⑫ ⑭ ⑰ ⑱ + 原登记项 1–7 + **影子字段删除**（下一周期）+ 段式 e2e 只剩 NVDA 首段 + 读档手写白名单。

> **📌 更新 2026-09-07（同日第 3 笔〔⚠️ 09-08 顺手清掉本行原「⭐ 当前最新」标〕·`DEFECT-CTX-BAG-SHAPE` **⑮ ✅ 已修**·PR [#276](https://github.com/JunoChenZt/subagent-for-investment/pull/276) 合 main `8e0e5fe`）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> **做了什么**：行情源写进资料夹的 A 股代码**保留完整代码**（此前 `symbol = ts_code.split(".")[0]` 主动切掉后缀）⇒ #270 冷审加的那一刀「数字相同**且交易所对得上**才算覆盖」终于喂得进数据。裸码 `000001` 同时匹配上证综指（`000001.SH`·约 3800 点）与平安银行（`000001.SZ`·约 11 块），少这一刀指数点位能冒充个股现价放行价格闸。**连带必须改的一处**：补基本面会拿资料夹里的代码再转一次格式，不认后缀就拼出 `300308.SZ.SZ` —— 请求作废，产物上**只表现为"这条腿没有基本面"、不报错**（已改 `_to_ts_code` 幂等 + 整链断言递过去的代码）。
> ⚠️ **严重性如实记（合并前写在 PR 里，不是事后补）**：**没有找到今天会真撞上的路径** —— 计划驱动时腿上是完整代码、守护可用；只有兜底路由与读旧归档是裸码，而那两条路上只有一条行情腿、腿与确认标的本就是同一只。⇒ 这是**防线朝 A 股一侧是死的，不是正在漏水**。修它的理由：代价极小 / 守护本就为此加 / 今天"撞不上"只靠"恰好一条腿"这个巧合，多一条腿保护就没了**且不会有任何声音**。
> 🔴 **冷审逮到本 PR 自己引入的一处误退（用户查·实测复现）**：`.SH` 与 `.SS` 是上交所的两种拼法（本仓用前者、Yahoo 用后者），⑮ 让覆盖判定**真比交易所了**却不认这对同义词 ⇒ 把同一只判成两只 ⇒ 判「这只标的的报价没到」⇒ **价格闸误早停、整跑退化成「暂时取不到实时行情」，而价其实好端端拿回来了**。已归一；🔑 **同义词表一份、两处共用**（计划校验层那道原是硬编码 `endswith(".SS")`，改成 import 同一份 —— 不再多一份副本，那正是 ⑯ 要治的病）。正反两个方向都钉了守护，反向变异 2/2 KILLED（清空表 → 5 条红；把 `SZ` 也并进去 = 放宽做成全放行 → 6 条红）。**这条正落在本 PR 自己引用的观察点 O-OVERSTRICT-GUARD-01 上**（安全支柱写过严 → 把好货全退了，且反向变异抓不到）—— **观察点写在文档里挡不住它，是人查出来的**。
> **🔴 新增登记项 ⑰ ⑱（DEFECT 族不占配额）**：⑰ **归档「按标的查」那一列混了两种写法**（#270 到 #276 之间的 A 股行是裸码、之后是完整代码，而该列是精确匹配过滤 ⇒ 两边都只查到一半、不报错）· ⑱ **名录不认 `.SS`（同根第三处）** —— ⚠️ **只坐实了「返 None」这个事实，没有追到下游真实后果**，故**既不声称无害、也不声称在漏**；不动它是因为那是另一个模块自己立的边界（明写「不猜」），按 Chesterton's Fence 该先读当年为什么这么立。
> **验证**：全量 **4041 passed / 2 skipped / 2 xfailed / 0 失败**（4032 → 4036 → 4041·每一步的增量都逐条对得上）；反向变异共 5 组全 KILLED；四道 lint + CI 九道全绿。⚠️ **未跑 e2e**（段式跑要真烧 token）—— 镜像面由「走真实取数函数 + 反向变异」钉住，**不冒充跑过一次真的**。
> **§2.11.9 首次实战（本笔即该规则立后的第一个 PR）**：**坐实 4 条 = 修 2（后缀补第二次 / `.SS` 误退含白补重复腿）+ 记账 2（⑰ ⑱）+ 明确不做 0**，数目对得上。⇒ **规则当场起了作用**：⑱ 那条若按老习惯就是"提一嘴然后忘掉"。
> **本笔按 [§2.9.4 八格清单](workflow/06-dod-and-evidence.md)走**：格 1 条目正文 ✅（⑮ 标已修 + ⑰ ⑱ 入册 + 剩余项改口径）· 格 2 本表 + 更新块 ✅ · 格 3 **接口说明书 ✅**（[tushare 行情说明书](../pipeline/seg1_retrieval/tushare_cn_quote_tool.md)「拉出来长什么样」示例改完整代码 + 注明旧归档仍是裸码）· 格 4 判据表 N/A = 不动承重边界 · 格 5 **观察点表 ✅**（O-OVERSTRICT-GUARD-01 加前向一句·point-in-time 正文不动·结论不变）· 格 6 代码注释 ✅（回核层那段"行情返回是裸六位"的断言已订正·行为一字未动）· 格 7 路线图 N/A · 格 8 memory ✅
> 🔻 **`DEFECT-CTX-BAG-SHAPE` 剩余**：⑨ ⑪ ⑫ ⑭ ⑯ ⑰ ⑱ + 原登记项 1–7 + 影子字段删除 + 段式 e2e 只剩 NVDA 首段 + 读档手写白名单。**下一步 = ⑯**（用户已裁：走**单一真值**，不是四表加断言）。

> **📌 更新 2026-09-07（同日第 2 笔〔⚠️ 同日第 3 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·**裁决：那条形态不立条目 → 焊进收口固定动作** + PR [#275](https://github.com/JunoChenZt/subagent-for-investment/pull/275) 合 main `c2d8734`）：lettered 活跃 **15 不变**、破例累计 **16 不变（第 17 次破例未开）**、`lint:active-count` 不动、🔴 仍 0 条。**
> **① 裁决 —— 形态「坐实但未修的 finding，PR 合并时没有强制落账义务」不立条目**（用户 2026-09-07 裁）：登记的仪式比干活贵，且这条的治法本来就是「在合并前的固定动作里加一格」、做完当场结案，没有需要跟踪的余留。⇒ 改为焊进 [08 §2.11.9 坐实 finding 的去处](workflow/08-retro-node-and-pr.md) —— 与 **BU** 机制化成 [§2.9.4](workflow/06-dod-and-evidence.md) 同一手法（先例 = #271「直接修、不立条目」）。**内容**：每条坐实 finding 恰好一个去处（本 PR 修 / 记账带自己的触发条件 / 明确不做带理由），合并前 `N = a+b+c` 对不上不许合；⚠️ 并写死**「坐实」由提出方认定**，执行体不得靠"我觉得这条不成立"把它移出分母 —— 少这一刀本节可被"重新数一遍 N"架空。同时补进 §6 PR 模板与 §6.2 不可省段。**三条同族分工写明**：R7 管状态切换后扫旧口径 / §2.9.4 管改了的东西真值源跟上 / §2.11.9 管**没改的东西要有家**。
> **② 相对路径三文件已修**（登记项外的第 3 条坐实·PR #275 合 `c2d8734`）：换目录跑分三种坏法 —— 挂 2 条（失败信息像"归档没了"、指错排查方向）/ 挂 1 条（相对 glob 扫不到归档）/ **静默跳过 1 条**（`exists()` 假 ⇒ 全场最重的端到端用例整条消失）。顺带清掉一处**假绿**（读不到文件的返回值恰好等于断言期望值 ⇒ 换目录照样"通过"）。**实测对照**：换目录跑那四个文件，改前 3 挂 / 1 静默跳过 / 4.4 秒 → 改后 **96 全过 / 0 跳过 / 172.8 秒**（差额 167 秒 = 丢掉的那条真的在跑了）。仓库根全量 **4032 passed / 2 skipped / 0 失败**；收集数 4021 → 4034 逐条对得上。**一处有意的行为变化**：那条静默跳过的用例原设计是"归档不在就跳过"，而该归档一直在册（`git ls-tree origin/main` 可查）⇒ 今天"找不到"只可能是换了目录跑、没有正当跳过理由，故跳过条件整个拿掉改成在册断言。**+ 新增守护**：扫所有测试文件的写法，再有人直接写以当前目录为准的仓内路径当场红；拿改之前的三份源码反向验过 3/3 全抓到。
> ⚠️ **形态记账（不立条目）—— 新守护自己犯了它要治的病**：用户冷审查出两条，**都是"扫得不全 / 破例写了不生效，却沉默着说干净"**，与本轮要治的静默跳过同一形状。① 破例名单的钥匙**文档与代码对不上、且带行号**（上面插一行就失效，失效的样子还是"红着找不到原因"）⇒ 钥匙改为与行号无关，并加一条自检**把说明书与代码焊死**；② **只扫 `tests/` 顶层**，子目录 17 个文件在范围外，而"防扫描器瞎了"那道自检只看总数（顶层 150 个就够过坎）⇒ **永远不会因为漏掉子目录而报警** ⇒ 改递归（150 → 167）+ 自检加"必须真的扫到子目录"一条。**与[闸门矩阵](../../tests/test_gate_matrix.py)当年 `glob` → `rglob` 那一修是同一个病** —— 新写检查器时**先自问"我枚举全了吗、我的自检抓得到漏枚举吗"**。第 1 次记形态，不立条目。
> **③ 本笔按 [§2.9.4 八格清单](workflow/06-dod-and-evidence.md)走**：格 1 **N/A** = 本次裁决是"不立条目"、没有自己的条目正文（前向事实已写去引用方 = 第 1 笔那两处"待用户裁"）· 格 2 本表 ✅（第 1 笔两处加前向一句·正文不动）· 格 3 跑批指南 **N/A** = 不动跑批口径 · 格 4 判据表 **N/A** = 不动承重边界 · 格 5 观察点表 **N/A** = 宽 grep 无相关观察点 · 格 6 代码注释 ✅（已随 PR #275 同步）· 格 7 路线图 **N/A** = S2 不断言本形态 · 格 8 memory ✅
> 🔻 **`DEFECT-CTX-BAG-SHAPE` 剩余**：⑨ ⑪ ⑫ ⑭ + 原登记项 1–7 + **⑮ 交易所守护**（下一步开工）+ **⑯ 五源名单单一真值**（用户已裁走单一真值、非四表加断言）+ 影子字段删除 + 段式 e2e 只剩 NVDA 首段。**读档手写白名单**（治本 = 逐字段往返行为验证）仍欠。

> **📌 更新 2026-09-07（第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·四个 PR 落账 + `DEFECT-CTX-BAG-SHAPE` 新增登记项 ⑮ ⑯）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> **① CI 脱离 Node 20**（PR [#271](https://github.com/JunoChenZt/subagent-for-investment/pull/271) 合 main `2fa2ab2`）：四个 action 全被 GitHub 点名弃用，真关掉时所有 CI 会一起挂。**用户裁「直接修、不立条目」**（登记的仪式比干活贵）⇒ 活跃条目不动。判据不是"CI 绿"，是**告警区整个清零**。⚠️ 过程记一笔：首版把 setup-uv 写成 `@v10`（release 号确实是 v10.0.1，但该仓不维护浮动 v10 大版本标签），CI 当场打回 —— **那一步是假设、没查**；改正后逐个读 `action.yml` 的 `runs.using` 选版（v5/v6 仍是 node20 = 换上去等于没修）。
> **② 存档「漏登记只丢不报」这一类堵死**（PR [#273](https://github.com/JunoChenZt/subagent-for-investment/pull/273) 合 main `9ba1395`）：写盘全量泛化、读盘逐键手工白名单 ⇒ 漏登记的字段静默消失。**该病已第三次复发**（前两次 `retrieval_plan_replay` / `confirmed_retrieval_plan`，都是碰巧被人查出来的）。补 `confirmed_tickers` 恢复 + 新增守护「每个字段要么恢复、要么进登记表写明理由」。
> **③ ①③ 修法补守护**（PR [#272](https://github.com/JunoChenZt/subagent-for-investment/pull/272) 合 main `63547cf`）：详见 §0.2 本条行。
> **④ 早停标记恢复**（PR [#274](https://github.com/JunoChenZt/subagent-for-investment/pull/274) 合 main `b3990ed`·**用户 2026-09-07 裁**）：**由 ② 的守护上线当天首次显形**。⚠️ **后果不是「少跑一次早停」，是绕过一道安全闸** —— 早停之所以早停是因为拿不到真实现价；续跑当没这回事，委员会会在**没有价格锚**的状态下跑完并给结论，而 [exec_floor](../../src/committee/facts/exec_floor.py) 锚失效时**退回模型自报价**（自己量自己）、连自报也没有则**直接放行**。⇒ 尺子没了等于不核。守护登记表随之**清空**（不是没人管，是没有例外）。
> **🔻 四条坐实未解决**（本笔之前**一条都没进账本**）：⑮ ⑯ 已入本条登记项（DEFECT 族不占配额）；另两条 —— **读档仍是手写白名单**（ast 扫描器自标"止血"·治本 = 逐字段往返行为验证，落地后整段可删）与 **一处相对路径漏网**（[test_failure_dump.py:85](../../tests/test_failure_dump.py)）〔**2026-09-07 订正 —— 不是一处，是 3 个文件**（换目录实跑核准）：[test_seg1_retrieval_plan.py](../../tests/test_seg1_retrieval_plan.py) 挂 2 条 · [test_mask_e1_audit_enum.py](../../tests/test_mask_e1_audit_enum.py) 挂 1 条（相对 glob 扫不到归档）· [test_failure_dump.py](../../tests/test_failure_dump.py) **不挂、静默跳过**（`exists()` 假 ⇒ 整条消失）。⚠️ **静默跳过比挂掉更坏** —— 跑批目录下少跑一条没人知道，正是本仓最忌的"空过"。〕—— **已排入 2026-09-07 计划第 4/5 步**，不靠"以后想起来"。
> ⚠️ **形态第 2 次命中 ⇒ 按记账规矩该提立**：「**review 坐实但未修的 finding，在 PR 合并时没有强制落账义务**」（首次记于 2026-09-02·注明"第 2 次即提立"）。本轮四条坐实 finding **合并时无一进账**，靠事后清点才补上。**提立会占 1 个 lettered slot（活跃 15 已到上限 ⇒ 需第 17 次破例）⇒ 待用户裁**，本笔先记事实、不擅自立。〔**➡️ 2026-09-07 同日第 2 笔已裁：不立条目**，改为焊进 [08 §2.11.9 坐实 finding 的去处](workflow/08-retro-node-and-pr.md) —— 第 17 次破例**未开**，破例累计仍 16。详见上方同日第 2 笔 banner。〕

> **📌 更新 2026-09-04（同日第 3 笔〔⚠️ 09-07 顺手清掉本行原「⭐ 当前最新」标〕·`DEFECT-CTX-BAG-SHAPE` 旧断点 `--resume` 补跑 + **BU** 加两负一正数据点）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> **跑了什么**：拿仓里**真实旧格式 A 股断点**（07-10 中际旭创 seg1·资料夹存**裸码 `300308`**）`--resume` 续跑 seg2 —— 补验冷审修法 **②**（旧存档裸码仍算股票腿）。它只在**读旧存档**时才走，是「每天都会撞上」的路，此前只有单测兜着，而 `51223f9` 的教训已点明**旧夹具恰好绕开真实写法、4000 条全绿也没咬到**。
> **结果**：读档后该腿 `asset_kind=equity` · `_is_ticker_query=True` · **「非个股标的」提示 0 次**（24 次调用全扫）· 基本面报告是真公司分析（证据 10 条）· 再序列化一轮判定不变；段间 checklist 8/8 全过；24 次调用 **$0.0753**。⇒ **修法 ② 升为已实证**。
> ⚠️ **覆盖仍如实记**：① 只覆盖半条、③ 本跑不重跑规划员**仍没走到** ⇒ 三修 **1 实证 / 1 半条 / 1 靠单测**，**不冒充已验**。
> ⚠️ **日志噪音逐条查过非故障**：搜索额度触顶 4 次 / 迭代封顶 3 次 / 两份报告 JSON 清洗 —— 均为设计内兜底；输出里 7 处 `DATA_INSUFFICIENT` **全部来自技术分析师**（指标值没取到的诚实标注），**不是护栏误伤基本面**，两件事别混。
> **不进 run-counter**（沿用同日第 2 笔的用户裁决）：只到第 2 段、非完整跑批。
> **本次落账按 BU 先列回填清单再收口**（8 处·live 就地改 / 历史加新笔不动旧 / 规划文档补前向一句 / memory 同步）—— BU 的第 2 次人工演练成功。**同时给 BU 记两个负例**（指南指着已关条目 / 登记项超时数字废弃一周）⇒ 踩坑计数升到 **4**。
> 🔻 **`DEFECT-CTX-BAG-SHAPE` 剩余跑现只剩 NVDA 首段。**

> **📌 更新 2026-09-04（同日第 2 笔〔⚠️ 同日第 3 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·`DEFECT-CTX-BAG-SHAPE` PR2 = PR [#270](https://github.com/JunoChenZt/subagent-for-investment/pull/270) **✅ 已 squash 合 main `415bc48`**）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> 🔒 **本条不 close** —— PR2 只完成**主体**（拆格子 → 一份数据 + 一张腿清单），条目继续持有剩余登记项，状态由 ⏳ 收回 **🟡**。
> **合并前冷审查出三处并全修**（`51223f9`·详见 §0.2 表行）：① 代码匹配丢了交易所（**本 PR 新引入的回归**·指数点位能冒充个股现价放行价格闸）② **旧 A 股断点回放护栏反着开火**（裸六位码认不出 ⇒ 真个股问题上基本面分析师自动弃权）③ 计划名单与键错位一格（**本 PR 把既有隐患升级成闸门级**）。全量 **4000 passed**·反向变异 **3/3 KILLED**·三 lint 绿·CI 9/9。
> **A 股验证跑**（`ad6582d`）：中际旭创 seg1–2，**23 次调用含「非个股标的」提示 0 次**、基本面报告是真公司分析 ⇒ 缺陷镜像面成立。⚠️ **覆盖如实记**：规划员两次都超时 ⇒ 两跑均走兜底路由 ⇒ 三条修法里只覆盖了 ① 的「不误伤」半边，②③ 靠单测 + 主链路守护 + 变异兜着，**不冒充已验**。
> **合并踩到的一处**：本分支与 main 改了 backlog 同一行（main 侧是同日 O2 订正）⇒ 冲突。**以 main 那版为底 + 接回分支独有的 PR2 落账段**，两边独有内容逐条核过、无取舍。
> **不进 run-counter**（用户 2026-09-04 裁）：A 股那跑只到第 2 段、非完整跑批。
> **🔻 剩余项**：⑨ ⑪ ⑫ ⑭ + 原登记项 1–7 + 影子字段删除（下一周期）+ 段式 e2e 剩余跑（旧断点 resume / NVDA 首段）。

> **📌 更新 2026-09-04（第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标 —— **未 stale**：同一天内接走〕·`DEFECT-CTX-BAG-SHAPE` PR2 = PR [#270](https://github.com/JunoChenZt/subagent-for-investment/pull/270) 已开·连带 ⑩ ⑬）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> **做了什么**：资料夹从「两个格子」改为「一份数据 + 腿清单」，读者全部改问具名问题；两格子降为影子字段（旧归档 / 旧断点 / 109 处旧测试构造零改动）；⑩ A 股腿按形态盖资产类型、⑬ 价格源名单单一真值。**有意变化只两处**（价格闸按确认标的匹配 / 归档现价快照读到值）+ 计划驱动下不对非股票腿拉财报；其余由不变量（影子 ⟺ `has_equity_leg`）与渲染逐字节对照钉住。反向变异 8/8 KILLED · 全量 3989/0 · 三 lint 绿。
> ⚠️ **形态记账（不立条目）**：首版提交信息把全量计数凭记忆写成 3960（实为 3989）→ amend。**写数字前看输出。**
> **待用户**：合并前段式 e2e 两跑（旧格式断点 `--resume` 到 research / NVDA 首段比对 `legs:` 行）。

> **📌 更新 2026-09-03（同日第 2 笔〔⚠️ 09-04 顺手清掉本行原「⭐ 当前最新」标〕·`DEFECT-COMMODITY-AS-TICKER` ✅ CLOSED·PR [#269](https://github.com/JunoChenZt/subagent-for-investment/pull/269) 已合 main `a7f2687`）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> **合并前**：high-effort review 8 角度 → 12 候选 → 10 坐实/可信 → **已修 4**（补腿循环与守卫同口径·只补股票腿·跳过已覆盖标的含基码 / backlog 触发列 + S2 §4.7.5 旧措辞回填 / 冗余 import）**记 6**（`DEFECT-CTX-BAG-SHAPE` ⑨–⑭）；段式 e2e 三跑全过；全量 3928/0；CI 九道全绿。
> ⚠️ **日期订正**：下方「2026-09-02（同日第 3 笔）」那笔（PR #269 开出 + 补立 `DEFECT-CTX-BAG-SHAPE`）**实际写于 09-03**，执行体日期笔误，内容不动。
> **下一步**：开 `auto/CTX-LEGS` 做 PR2（拆格子改腿清单·零行为变化），登记项按用户裁决并入。

> **📌 更新 2026-09-03（同日第 1 笔〔⚠️ 同日第 2 笔顺手清掉本行原「⭐ 当前最新」标〕·PR [#269](https://github.com/JunoChenZt/subagent-for-investment/pull/269) 段式 e2e 验收落账 + 立 1 条 DEFECT + BN 回填）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> **验收结果**：三跑（黄金 seg1–7 / NVDA seg1–2 / 标普 500 seg1–9 + 终局质检 **13/0/0**）**无一项 ❌·重跑 0 次**；
> 两道护栏在黄金与指数上都验到（提示只发基本面 3/3、其余 7 角色 0；投票**代码短路零 LLM 调用**），
> NVDA 侧与两份 main 归档**一字不差同构**（8 角色 / 24 调用 / 0 提示）。证据 [FINDINGS](../observations/cat-pr1-e2e-20260902/FINDINGS.md)。
> **① 立 `DEFECT-D5-COUNT-AS-VALUE`**（🟢·DEFECT 族不占 lettered 配额·**无需破例**）：序列型引用登记成 `list(N)`，
> D5 拿**条数**当数值对账 —— 失配是噪音、命中是巧合（实测「过去12个月」→ 假绿、「12.1%」→ 容差内假绿）。
> D 类只记不拦 ⇒ **fail 面零变化**。
> **② BN 回填（用户 2026-09-03 裁「不重开」）**：BN 8-31 已 close，而[指南 ⑦ 段](../observations/e2e-runs/segmented-e2e-guide.md)两行仍写「记入 BN」
> ⇒ 本轮跑批的人照着去找才发现条目已关。**已就地改口径 + 加 🔒 块**（读数今后记在跑批 FINDINGS）。
> ⚠️ **黄金跑是 BN close 后第一个同构复现**（三张真 NEUTRAL 票 conviction 全 6·零方差·5 个共有词）——
> 按 BN 原口径把「连续 3 次反向」的计数打断了；**用户裁不重开**，读数留在指南 🔒 块与 FINDINGS。
> 🔒 **BN 条目本体一字未动**（[Q6 冻结档](workflow/05-brake-self-check.md)·前向事实全写去引用方）。
> **③ 这是 **BU**（「裁决/立账」落地没有回填义务·见 §1）的第三例、同一处的第二次**：
> 08-27 是「BN 已立账而指南停在『N≥3 → 提立』」，本次是「BN 已 close 而指南仍写『记入 BN』」——
> **同一行、同一病、方向相反**。BU 触发条件（下次做立账/降档/观察点转正类裁决落地时按本条列回填清单）**本次命中并已执行**。
> ⚠️ **两处已知未动，须用户裁**：(a) BN 的 §1 正文标题**没有 CLOSED 标记**（§0.2 表行有），
> 按 [§4.4 Housekeeping](#44-backlog-数量上限) 该标；但按 Q6 冻结档不该碰 —— **规则接缝，本轮不动**。
> (b) 指南另有三处（第 154 / 216–217 / 253 行）把 BN 当作「判据到线没人执行」这一类的**在册代表**引用
> （「本条不另立账·BN 已覆盖这一类」）；BN 关闭后该类**无活跃条目承接** —— 是否补立须用户裁，本轮不动。

> **📌 更新 2026-09-02（同日第 3 笔·`DEFECT-COMMODITY-AS-TICKER` 修复 PR [#269](https://github.com/JunoChenZt/subagent-for-investment/pull/269) 已开 + 补立 `DEFECT-CTX-BAG-SHAPE`）：lettered 活跃 **15 不变**、破例累计 **16 不变**、`lint:active-count` 不动、🔴 仍 0 条。**
> **怎么走到这一步**：开工读交接单后用户追问「装袋是否必要」→ 按第一性原理重定 seg1 身份 = **规划员（模型·唯一语义判断：查什么）+ 资料员（程序：取、验、贴标签、报缺口）** → 「个股/宏观格子」这个全局标签不是资料员本职、是会议规则借住 seg1 ⇒ 修法扩为两 PR（PR1 修判断·PR2 拆格子零行为变化）。
> 🔑 **「让分析师自己判断」被归档否决**：两次黄金跑基本面分析师**没收到任何提示**（= 天然实验），**0/2 自弃权** —— 08-27 报告开头自写「黄金不是公司、无护城河框架可套」仍产出全份报告、自行拉入紫金矿业、投 BULLISH 7「建仓」；08-31 给黄金做「护城河评估/百亿反问」、编出公允值 4367、投 NEUTRAL 6 给介入区间。提示词本就明写角色边界与 DATA_INSUFFICIENT 优先。⇒ 判断可让模型参与、**后果必须代码兜住**。
> **PR1 验证口径**：主链路守护（跑真节点→真校验器→真 builder→袋形状→ctx 原样喂两道护栏）· 反向变异 **4/4 KILLED** · 全量 **3901 → 3925 passed / 0 失败** · 三 lint 全绿 · **段式 e2e 三跑尚未做**（每段须用户放行）。
> ⚠️ **形态记账（不立条目）**：反向变异首轮 restore 用字符串反替换误伤同名分支（`return True` 非唯一）→ 改整文件快照写回。**变异回滚一律整文件快照。**
> **8 条登记项**全部落在 `DEFECT-CTX-BAG-SHAPE` 正文（各自触发条件），BQ 残留①（兜底路由）= 其登记项 1。

> **📌 更新 2026-09-02（同日第 2 笔·BQ close-by-decision）〔⚠️ 同日第 3 笔顺手清掉本行原「⭐ 当前最新」标〕：活跃 16 → **15 = 回到上限内**、破例累计 **16 不变**、`lint:active-count` 同步改 **15**、🔴 仍 0 条。**
> **判据**：BQ 触发条件「用户明确要求」命中 → 整理证据交用户裁 → **裁 close-by-decision**。
> **核心已解**（A/B 同问句同配置各 3 跑）：问黄金**旧路由 0/3 拿到行情腿、新大脑 2/3**（`GC=F` 4682.80·真流到下游进事实清单 `f1`）；
> 对照组茅台两臂均 3/3 ⇒ 差异**资产类特有**、非随机。
> 🔴 **两半残留按 [R7](../../CLAUDE.md) 写去引用方、并入 `DEFECT-COMMODITY-AS-TICKER`**，不随本条埋掉：
> ① **兜底路径仍会复发**（那 1/3 = 规划员没出计划 → 退回旧路由 → 金价没了）；
> ② **BQ 自己预言的下游 schema 那半已兑现**（`bag=ticker`·期货数据进股票袋）；
> ③ 五类资产**只端到端验了黄金**，其余四类仅「格式认得」层证据。
> ⚠️ **不是 close-by-completion** —— 病没被彻底根除，是**核心已解 + 残留有主**，措辞别混。
> - **立 3 条 DEFECT（不占 lettered）**：[DEFECT-ANCHOR-FALSEPOS-HARDBLOCK](#defect-anchor-falsepos-hardblock-出处绑错第一次改变了决策产出--一条正确的断言触发灾难指纹硬拦buy-被压成-hold执行计划整个被切🟡2026-08-27-g7-全链跑实锤)（锚绑错首次误伤决策·BUY→HOLD）+ [DEFECT-DEBATE-STALE-PRIOR](#defect-debate-stale-prior-辩论第一轮设计性断粮--模型拿训练期的旧行情充当今天的数据且无任何闸门看得见🟡2026-08-27-g7-全链跑实锤)（R1 断粮→旧记忆行情充数）+ [DEFECT-GATE-NA-AS-PASS](#defect-gate-na-as-pass-终局质检把没查到印成-pass--执行计划被硬闸切除时价位两项自动绿理由还写错🟡2026-08-27-g7-全链跑实锤)（n/a 印成 PASS）。
> - **立 2 条 lettered（破例）**：**BT**（triage 打回能力盘点——唯一真打回源 6 月被拔）+ **BU**（裁决/立账落地无回填义务——72h 两例）。
> - **同笔更新 BN**：08-27 黄金跑按 BN 自己的反面样本口径构成**反向条件连续第 2 次**（BULLISH 7 票方差 0.204 非零·全员共有词空集）——close 条件（连续 3 次真实方差）**只差 1 次**。⚠️ 且本跑是**连续型问题（黄金）却出了真实方差**，直接削弱 BN 里「连续型问题易收敛」那条推测（推测预测本跑该收敛，没收敛）。
> - **三条横切根子**（本轮 5 个问题的共因·记账不立条目）：① **规矩写在嘱咐里没闸门强制**（分析师贴章规矩/辩论出处规矩，模型偶发违反无人拦）→ 落在两条 DEFECT 的根因链里；② **每道检查只守自己管道、接缝无人管**（贴章无人验真、核对默认章为真、质检各管各的且汇总不报盲区）→ 落在 DEFECT-GATE-NA-AS-PASS + FALSEPOS 里；③ **删规则/裁决类决定落地无同步义务** → 即 BU（B3 拔牙无人盘点=BT 的由来、裁决没回填=BU 例①②）。
> - 上方 08-21 第三笔的「⭐ 当前最新」**同笔清掉**（该形态此前第十一次后续增·本次按实际递增为**第十二次**）。
> - 完整排查记录：[G7 FINDINGS](../observations/rp-g7-e2e-20260827/FINDINGS.md) §九–§十七 + 本笔 §6 记账。

> **📌 更新 2026-08-21（同日第三笔·seg1 G4b 落地 → BI 取深度那半已做、**不关**）〔⚠️ 08-27 顺手清掉本行原「⭐ 当前最新」标〕：不新增不 close —— 活跃仍 **15**（余 0）· **🔴 仍 0 条** · 破例累计 11 不变**（`lint:active-count` 不动）。
> - **BI 就地改口径、不关**：G4b 让研报腿拿得到 **2272–2788 字**的智堡自撰摘要（真平台实测），「半句话成承重依据」的成因在能力层面消除；**但并入本条的 AP 残留（拆 per-report 编号）本次显式不做**，且**管道默认仍是投行库 + 只拿标题**（点名要等 G5）⇒ **生产里那个问题要到 G5 才真的消失**。
> - 🔴 **同笔订正一处 08-20 摸源写错的现状**：[tushare 接口说明](../infrastructure/seg1_retrieval/tushare-api/README.md) 原写估值/财务两个接口「❌ 未用」「问什么都只拉收盘价」—— **两句都错**，那两个接口 **2026-07-23 就接上了**（[#203](https://github.com/JunoChenZt/subagent-for-investment/pull/203)·backlog **AL 方向(2)** 早已标 Layer 1 ✅ DONE），归档实证 08-14 两跑的 A 股条目带着 8 个基本面字段。**成因**：api-intake 第 1 步只读了「消费方」那个**类**，而拉基本面的是**模块级函数、从 builder 调**。三处 live 断言已订正、摸源那份 point-in-time 记录加前向注不改正文。
> - **用户 2026-08-21 两裁**：① agent 侧研报能力**不升级**、但调用**计进同一道 run 级闸**（否则「run 级」三个字不成立）；② A 股那半**只订正文档**，`want` 留给 G5。
> - ⚠️ **执行过程如实记账**（§2.7.5 Q5）：新写的「额度用尽」判据**首版放错层** —— 那个测试文件把封装层整个 mock 掉了，闸根本不在那条路上，断言到的是假客户端的行为（实测 `4 != 2` 当场暴露）。已把判据拆到真 wrapper 那一层，**没有**把闸逻辑复刻一份到假客户端里（那样守护只守自己那份拷贝）。
> - 上方同日第二笔的「⭐ 当前最新」**同笔清掉**（未 stale：同一天内接走）。

> **📌 更新 2026-08-21（同日第二笔〔⚠️ 同日第三笔顺手清标：本行原带「⭐ 当前最新」，已同笔接走 —— **未 stale**，当前最新 = 上方同日第三笔 banner〕·seg1 G2 落地 → BR 实例① 的「静默」那半已修）：不新增不 close —— 活跃仍 **15**（余 0）· **🔴 仍 0 条** · 破例累计 11 不变**（`lint:active-count` 不动）。
> - **BR 就地改口径、不关**：G2（节点 [4.7.5 RP](../roadmap/S2.md)·分支 `auto/retrieval-planner`）把「撞不上就静默落 `CPIAUCSL`」改成 **认不出就明确失败** ⇒ 条目标题那句「静默走默认值」对 FRED 这一处已不成立。**没解决的那半**（表本身拆不拆）随宏观安全网一起归 G5。
> - 🔴 **同笔订正一处设计文档的过度承诺**：[设计 pass §6](../plans/seg1-取数计划-设计pass-2026-08-19.md) 原写 **`DEFECT-FRED-SUBSTRING` 由 G2 解决（"撞子串这个机制不存在了"）—— 落地时证明做不到**，已改归 G5。两者是**两个病**：BR = 「撞不上就编一个」（G2 已拆）· 本条 = 「撞上了但撞错」；而"撞子串这个机制"在 G2 里**必须原样留着**，因为那张表是安全网的唯一判据。⇒ **`DEFECT-FRED-SUBSTRING` 条目状态不变、不得据 G2 关闭。**
> - ⚠️ **执行过程如实记账**（§2.7.5 Q5）：反向变异 M1 当场抓出**我自己新写的一条测试因错误的原因绿** —— 那条没 mock 上游，`degraded` 其实来自"拿假 key 真去请求 FRED 失败了"，把修法退回去它照样绿（还顺带在测试套件里打真网络）。已修并把教训写进该测试的 docstring。**这是坑表「判据挂在结构上不会响的信号上」的又一个现场实例。**
> - 上方同日第一笔的「⭐ 当前最新」**同笔清掉**（未 stale：同一天内接走）。

> **📌 更新 2026-08-21（第一笔〔⚠️ 同日第二笔顺手清标：本行原带「⭐ 当前最新」，已同笔接走 —— **未 stale**，当前最新 = 上方同日第二笔 banner〕·探针 T2 复跑收口 + **补录**同日 G4 那笔漏建的 banner）：不新增不 close —— 活跃仍 **15**（余 0）· **🔴 仍 0 条** · 破例累计 11 不变**（`lint:active-count` 不动）。
> - **两个探针 T2 复跑完，两轮一致**（[T2 FINDINGS](../observations/seg1-probes-t2-20260821/FINDINGS.md)·判据自 T1 落锁后一字未改，A 的脚本与 T1 **逐字节相同**）：中文下 `when:`/`site:` 六格逐格重合（`when:1d` 两轮都恰好把 100 条筛到 33 条）⇒ 由"暂定"**升为结论**；智堡 L1 隔日 20 次/2.48 秒 ≈ 483 次/分与 T1 逐项吻合。
> - ⚠️ **两处别读大**：① T2 与 T1 实际间隔 **22h37m，未满计划写的 24 小时**（跨了自然日故"按天"这层成立，但不足以当"滚动 24 小时窗口"的证据·已在 T2 §0 如实标）；② 智堡**只收口一半** —— **跨日累积型限制已排除**，**单日上限仍未测**（下界仍是 T1 的当日 ≈83 次，T2 当日仅 33 次**没推高**）。⇒ [接口说明](../infrastructure/seg1_retrieval/wisburg-mcp.md) 与 [00-retrieval](../pipeline/00-retrieval.md) 已按这个分寸就地改口径；**本 §0.2 的 BI 行不动** —— 它写的"顶未探到 · 按天维度未决"在"单日上限"这层今天仍成立。
> - ⭐ **白拿一个证据：`DEFECT-MCP-ISERROR` 的修复在真平台上被验证了**。同一个探针脚本、同一个动作（给 `get-report-detail` 传字符串编号），**T1 自动记为"没被拒"、T2 自动记为 `MCPToolError`**。此前那道修复只有内存版 MCP 服务器的单测撑着 —— 坑表「从未 fire 过的检查 = 前提未经验证」那条，这次是真平台真错误当场 fire，且撞的正是**当初暴露问题的那个动作**。
> - 🔴 **补录：同日 [#260](https://github.com/JunoChenZt/subagent-for-investment/pull/260)（G4 第一层）close 了 `DEFECT-YF-TICKER-TRUNCATION`、并改了 BQ 的备注格，却没建 banner** —— 「条目改了·banner 忘了」**同一形态又一次**（前次记到第 5、6 次，见下方 08-13 补录笔）。⚠️ **lint Check 8 看不见这个方向**：它只在「§6 领先于 banner」时报，而那笔**§6 也没记** ⇒ 两边双双沉默、检查全绿。**配额影响为零**（DEFECT 族不占 lettered 配额，BQ 只改备注不改状态），故本笔计数照旧。
> - ⚠️ **不新立条目**（余 0 硬约束）：本轮结论全部写进既有载体 —— 两份接口说明 · [探针计划](../plans/seg1-前置探针-计划-2026-08-20.md) · [seg1 设计 pass](../plans/seg1-取数计划-设计pass-2026-08-19.md) §8 · [00-retrieval](../pipeline/00-retrieval.md) 待办表。
> - 上方 08-20 第三笔的「⭐ 当前最新」**同笔清掉**（未 stale：本笔提交的同一笔里接走）。

> **📌 更新 2026-08-20（同日第三笔〔⚠️ 08-21 第一笔顺手清标：本行原带「⭐ 当前最新」，已同笔接走 —— **未 stale**，当前最新 = 上方 08-21 banner〕·close DEFECT-MCP-ISERROR + 拆出 DEFECT-REVIEW-ERROR-AS-DATUM）：取数层四缺口的 ① 落地 —— 活跃数**不变**（DEFECT 族不占 lettered 配额·仍 15·**余 0**）· **🔴 仍 0 条** · 破例累计 11 不变**。
> - **close DEFECT-MCP-ISERROR**（close-by-completion）：封装层 `call_tool` 判 `isError` → 抛 `MCPToolError`（带工具名 + 服务端错误文本）。修在**封装层**而非单个消费方 —— 那句"所有错误都会抛"本来就写在它自己的契约里，这是**兑现承诺不是改规矩**。验证走**真 MCP 协议三面对照**（出错→抛 / 裸 SDK 对照→确实不抛 / 正常工具→不误拦）+ 实跑变异；全套件 3421 passed。
> - ⚠️ **同笔解除该条的 R5 前置**：四条独立佐证（契约 docstring 三句错两句 / 当年搭的仪器只对准 shape 没对准 status / 同仓我方对外服务正是靠它报错 / 该词在全仓提交史零出现）一边倒指向**疏漏非有意**。论证全文进[设计 pass §2.2](../plans/mcp-client-四缺口-设计pass-2026-08-20.md)。
> - 🆕 **拆出 `DEFECT-REVIEW-ERROR-AS-DATUM` 🟡**：照母条目自己写下的裁定「审查把错误码算作'具体数据点'**独立成立、不随之关闭**」原样接住（R7 ③ 连带项）。**修好上游≠修好它** —— 上游堵的是一个灌入口，本条问的是"这道判断凭什么认定一段文字算一个数据点"。⚠️ 单实例、**未核该判断是否真承重**，按 R5 只登记不判修法。
> - **四缺口进度**（[设计 pass](../plans/mcp-client-四缺口-设计pass-2026-08-20.md)）：① ✅ 本笔 · ④ ✅ 同日 [#257](https://github.com/JunoChenZt/subagent-for-investment/pull/257) · **②③ 未做**（必须同批、随 G4b 走）。
> - 上方同日第二笔的「⭐ 当前最新」**同笔清掉**（未 stale：同一天内接走）。

> **📌 更新 2026-08-20（同日第二笔〔⚠️ 同日第三笔顺手清标：本行原带「⭐ 当前最新」，已同笔接走 —— **未 stale**，当前最新 = 上方同日第三笔 banner〕·立 DEFECT-MCP-ISERROR 🟠）：两个前置探针 T1 跑完 —— 活跃数**不变**（DEFECT 族不占 lettered 配额·仍 15·**余 0**）· **🔴 仍 0 条** · 破例累计 11 不变**。
> - **探针 A 结论 ✅**：谷歌新闻的 `when:` / `site:` 两个算子在**中文查询下同样严格**（中英各三格同场对照，英文对照组亦达标 ⇒ 排除端点整体漂移）。⇒ 中文腿**不必**退回"只带词不带算子"；[gnews-rss.md](../infrastructure/seg1_retrieval/gnews-rss.md) 的「中文下算子未测」风险行已撤。
> - **探针 B 结论 ✅**：智堡一条连接**连打 64 次全过 / 8.05 秒 ≈ 477 次/分**，零错误无耗时爬升 ⇒ 新方案 4–60 次区间全段安全。⚠️ **顶没探到**（64 是我们自己的阶梯终点，不是平台上限）；**按天维度仍未决**（当日累计 ≈83 次不撞限，只是下界）。
> - 🔴 **立 DEFECT-MCP-ISERROR**（本轮真正的收获）：工具层错误以 `isError: true` **混在正常返回里**、**不抛异常**，而本仓**全仓零处检查该标志**，解析函数把错误文本原样当内容 ⇒ 它拿到引用编号、进引用清单、被下游当证据。**归档实锤**：503 变成 `[REF#W-003]`，还被审查环节算作"具体数据点"。⚠️ **未核设计意图，按 R5 只登记不判修法**。
> - ⚠️ **顺带证伪我自己的一次误判**：探针先报"字符串编号没被拒"（只看了有没有抛异常）—— 复查发现**确实被拒**，只是拒绝走 `isError` 不走异常。既有坑表记录**成立**，是我读错了。**这次误判正是本 DEFECT 的第一个实例。**
> - ⚠️ **探针自身也踩了一个同型坑**：`site:` 纯度用字符串精确匹配，把 `m.cls.cn` 当外人算出 0.75 判**假 FAIL**（与 eTLD+1 子域缝 `DEFECT-R5-03` 同型）；已修并保留错误产物作教训。
> - 上方同日第一笔的「⭐ 当前最新」**同笔清掉**（未 stale：同一天内接走，未出现"⭐ 留在旧 banner 而新 banner 已叠"的窗口）。

> **📌 更新 2026-08-20（第一笔）〔⚠️ 同日第二笔顺手清标：本行原带「⭐ 当前最新」，已同笔接走 —— **未 stale**，当前最新 = 上方同日第二笔 banner〕：seg1 三条实测前置调查完 —— 活跃 **15 不变**（余 0）· **🔴 仍 0 条** · 破例累计 11 不变**。
> - **BS 由〔轻条目〕提为 §1 正文条目**（[#254](https://github.com/JunoChenZt/subagent-for-investment/pull/254)）—— 备注格在 main 上已 **989 字**、离 `lint_backlog` 的 1000 上限只剩 11，新事实一进就撞闸；按闸门自身指引拆出正文。**内容全文保留、无删减**，§0.2 行压成摘要并去掉〔轻条目〕标记。⚠️ **活跃数不受影响**（BS 本就在册，只换承载形式）。
> - **BS 事实订正（论据换人·结论不变）**：原把"新闻拉通用背景可能是设计意图"归在「谷歌订阅源写死搜 `financial markets`」上 —— **归错了**。两个 feed 取满 10 条即 break（[rss_source.py:141](../../src/committee/common_context/sources/rss_source.py)）、MarketWatch 排第一给够 10 条 ⇒ **谷歌腿正常路径下从未执行**（对 [rss_A_today.json](../observations/source-shapes-20260819/raw/rss_A_today.json) 核实：10 条全 MarketWatch）。⇒ 那 10 条 0 相关**全来自 MarketWatch**；它结构上不认查询词，故该假设**反更站得住**。**连带**：只接查询词不动 break，接了也永远轮不到（已进 seg1 G3 前置）。
> - **BI 无实质变化**（08-20 更新块已于 [#253](https://github.com/JunoChenZt/subagent-for-investment/pull/253) 落账）。
> - **坑表 §3.8「智堡 MCP 配额硬限制」来源订正**（[09-known-pitfalls.md](workflow/09-known-pitfalls.md)）—— 该"硬限制"**不是平台的**，是我们自己 2026-05-13 在 [S2.md §5.3](../roadmap/S2.md) 定的设计预算（与"单次 ≤8s""Pass 0.5 ≤30s"同批）；**首次真连平台是 05-25，晚 12 天** ⇒ 时间线直接证伪。抄进坑表时丢了"自定"这层，此后三轮被读成外部事实。**平台从未返回过配额错误**（唯一真故障是 503）。⚠️ 同时记下：代码里 `quota=3` 守卫**按连接计数**、每条连接只调 1 次 ⇒ **从未触发**。
> - ⚠️ **不新立条目**（余 0 硬约束）：本轮三条发现全部写进既有载体 —— seg1 设计 pass（G3/G4b 前置 + §8 开放问题）· 五源接口说明 · 坑表 · 本条目。
> - 上方 08-19 第七笔的「⭐ 当前最新」**同笔清掉**（⚠️ **本次不计入 stale 计数**：它是在本笔提交的**同一笔**里被接走的，从未出现"⭐ 留在旧 banner 上而新 banner 已叠"的窗口 —— 与前十二次形态不同）。

> **📌 更新 2026-08-19（同日第七笔）〔⚠️ 08-20 第一笔顺手清标：本行原带「⭐ 当前最新」，已同笔接走 —— **未 stale**，当前最新 = 上方 08-20 banner〕：立 DEFECT-YF-TICKER-TRUNCATION 🟠 —— 活跃数**不变**（DEFECT 族不占 lettered 配额·仍 15·**余 0**）· **🔴 仍 0 条** · 破例累计 11 不变**。
> - 来源 = seg1 **数据源形态探针**（给五个源写说明书时真调一遍，[证据](../observations/source-shapes-20260819/)）。
> - **要比特币，拿回另一个资产的价格**：`BTC-USD` 被抠代码的正则截成 `BTC`，而 `BTC` **恰好是另一个真实存在的代码** → 返回 `$28.57`（**结构完好·有时间戳·零报错**）。⚠️ **2026-08-20 订正倍数**：原写「差约三千倍」是**按假设的比特币价格推的、未实测**；同日双边实测 `BTC-USD`=69242.11 vs `BTC`=30.27 ⇒ **约 2290 倍**（方向不变，数字由推断改测量·[证据](../observations/api-intake-batch-20260820/yf_symbology.json)）。同族两例：`GC=F` 截成 `GC` → 重试三次**烧 13.54 秒**后失败；`^GSPC` → 直接抛错。
> - 🔒 **定 🟠 不是 🟡**：价格是承重数据，且失败形态是**静默给回错资产**（"拿到假的"），与 DEFECT-FRED-SUBSTRING 的"拿不到想要的"方向不同。
> - 🔒 **今天生产不可达**（主题型不激活价格源 = **BQ** 本身），**但 BQ 一修就活** ⇒ 本条**必须在 BQ 之前或同批**处理。
> - 🔒 **R5 守**：严格 cashtag 是**设计且对**（2026-05-19 用户裁决，为根除「"I think AAPL is great" 的 `I` 被当代码」）⇒ 修法从**放宽结构化校验**入手，**不得放宽正则**。
> - ⚠️ **本笔与 08-19 第六笔（[#251](https://github.com/JunoChenZt/subagent-for-investment/pull/251)）是两条线并行产出**，合并时本笔顺延为**第七笔**并接走 ⭐；上方第六笔的「⭐ 当前最新」**同笔清掉** —— 该 stale 形态**本次为第十二次**（第六笔记为第十一次，按其立的「按实际递增」约定 +1）。

> **📌 更新 2026-08-19（第六笔·纯订正·不新增不 close）：收 `/code-review` 两条 finding —— 补第五笔缺的 banner + BS「7 条」口径只核到 3**。活跃 **15 不变**（余 0）· **🔴 仍 0 条** · 破例累计 11 不变。
> - **① banner 栈跳过了一次状态变更（本笔自己就是那个病的第十一次）**：同日第五笔（撤 BR 实例②）**只写进 §6、没在 §0.2 建 banner、也没接走 ⭐** ⇒ 读者扫 banner 栈看不到「BR 实例② 已撤」这次变更。lint Check 8 只比日期、两笔同为 08-18 故**看不见** —— 这正是第四笔自己写下的「Check 8 管日期不管归属」盲区。本笔把 ⭐ 挪到本行，并在下方第四笔行显式指回第五笔。⇒ 第四笔记的「此前至少十次·此后按实际递增」→ **本次为第十一次**。
> - **② BS「7 条引用」口径只解释得了 3 条**：原文写「7 条（按字段拆）」，但该拆法只覆盖唯一那个宏观指标（`series_id`/`unit`/`value`）= **3 条**，**余 4 条来源未交代** ⇒ 读者复算不出 7。本笔**不补构成**（要补须回归档逐条核·**本次未做**），改为**显式标注核到哪一步**，并写明本条不拿 7 的内部构成支撑论断。
> - 🔒 **只改 live 档**：§0.2 的 BS 行与本 banner 栈**就地改**；**§6 第四笔 / 第五笔正文一字不动**（历史记录·守 R7），前向事实由本笔承载。

> **📌 更新 2026-08-18（同日第四笔·⚠️ 配额用满）〔⚠️ 08-19 第六笔顺手订正：本行原带「⭐ 当前最新」，其后已叠**三笔**（同日第五笔撤 BR 实例② + 08-19 第六笔 + 08-19 第七笔）—— 同类 stale 标记，**当前最新 = 上方 08-19 第七笔 banner**；⚠️ 其中**第五笔当时未建 banner**，该断档正是第六笔要补的东西〕：加 BR + BS → 活跃 13→**15**（上限 15·**余 0**）· **🔴 仍 0 条** · 破例累计 11 不变**。
> - 来源 = seg1 检阅**外部取数质量**实测（黄金跑·31 条外部信息逐条读过）。⚠️ **口径**：31 = 信息条目数（1 指标 + 10 条头条 + 20 篇研报标题），与引用清单 7 条（按字段拆）**不是一个数** —— 守同日第二笔冷审那条「104 条 ≠ 26 个独立观测」的教训。
> - **加 BR**🟡 —— 「问题 → 拉什么」的映射表**覆盖不全就静默走默认值且零告警**：FRED 关键词表 13 个词无商品/汇率/贵金属 → 问黄金**静默拉回 CPI 332.813** 写进引用清单（它连「问错了」都不知道）。**形态 = 枚举表 + 默认兜底 + 没有「我不知道」这个状态**。⚠️ **本笔原稿另记一个「同形实例②」（#244 的 `confidence` 刻度不覆盖主题型），已于同日第五笔核代码证伪并撤除** —— 该刻度在同 PR 第二个 commit 就已换轴修好；**BR 现为单实例条目**。
> - **加 BS**🟡 —— 引用清单把**三类信息混成一类**：答非所问的（CPI）/ 当背景的（10 条通用头条·0 相关）/ 真对题的（10 篇金价研报），到分析师眼里全是「7 条引用」**无任何标记**。实测相关率 **32%**；研报另一半是「名字里有黄金的股票」（7 篇同一家珠宝公司 + 一对重复条目）。
> - 🔒 **三条边界写死防混读**：BR ≠ **BQ**（BQ = 该拉的腿没激活 · BR = 腿激活了但拉错东西）· BR ≠ **DEFECT-FRED-SUBSTRING**（那条是子串**误命中**「毛利率」→「利率」· BR 是表里**压根没有这个域**）· BS **不是说这些源没用**（新闻拉通用背景**可能本就是设计意图**，但代码里没有一句话说明该定位 ⇒「背景」与「答非所问」在清单上长得一模一样）。
> - ⚠️ **配额用满（余 0）**：下次再立 lettered 条目须**先 close 一条**或**用户授权破例**。本次两条均在上限内、不占破例。
> - 旧 08-18 第三笔 banner 的「⭐ 当前最新」标记**同笔清掉**（该形态此前**至少十次** stale·Check 8 管日期不管归属）。⚠️ **本笔顺手订正该计数**：它自 08-14 第一笔起被**逐笔照抄**停在「六次」（08-12 两笔尚记「四次」「五次」→ 08-13「五次」→ 08-14 起一路「六次」），而每清理一次本应 +1 ⇒ **计数自己成了它要治的那个病的实例**。此后按实际递增。

> **📌 更新 2026-08-18（同日第三笔）〔⚠️ 同日第四笔顺手订正：本行原带「⭐ 当前最新」，其后已叠加 BR/BS 一笔 —— 同类 stale 标记，当前最新 = 上方第四笔 banner〕：立 DEFECT-FRED-SUBSTRING 🟡 —— 活跃数**不变**（DEFECT 族不占 lettered 配额·仍 13）· **🔴 仍 0 条** · 破例累计 11 不变**。
> - 来源 = [#246](https://github.com/JunoChenZt/subagent-for-investment/pull/246)（补路由宏观安全网）写**反证测试**时撞见：负例用了「茅台三季度毛利率怎么样」，当场变红 —— 因为「毛**利率**」含「利率」，宏观关键词按子串匹配 ⇒ `_resolve_series("…毛利率…")` 返回 `FEDFUNDS`。
> - **不是 #246 引入的**（fred 自己的取数一直如此），但 #246 的安全网**继承同一张表**故多一个暴露面；该 PR 已用测试钉住假阳性现状、方向安全（只多拉一个源、不减源不改判定）。
> - **不在 #246 修的理由**：修它 = 改 fred 主路径的 series 解析，超出「只加一条安全网」的边界。**用户 2026-08-18 拍「另立条目」。**
> - 与已 close 的 [DEFECT-FRED-KEYWORD](#defect-fred-keyword-fred-工具广告了实现认不出的拼写--要利率静默拿到-cpi🟡2026-08-04-bc-探针-e2e-surface✅-closed-2026-08-13close-by-completion保留位置) **同表同族、互补**：那条治「广告了实现认不出的拼写」（该认没认出），本条治「不该认的认了」（假阳性）。
> - 旧 08-18 第二笔 banner 的「⭐ 当前最新」标记**同笔清掉**（该形态此前已六次 stale·Check 8 管日期不管归属）。

> **📌 更新 2026-08-18（同日第二笔·冷审补）〔⚠️ 同日第三笔顺手订正：本行原带「⭐ 当前最新」，其后已叠立 DEFECT-FRED-SUBSTRING 一笔 —— 同类 stale 标记，当前最新 = 上方同日第三笔 banner〕：加 BQ → 活跃 12→**13**（上限 15·余 2）· **🔴 仍 0 条** · 破例累计 11 不变**。
> - 来源 = [PR #244](https://github.com/JunoChenZt/subagent-for-investment/pull/244)（classify 提示词收编资产类）冷审切出：**分类归对了，代价没人接** —— 大宗商品/指数/加密/汇率归 thematic 后**价格源永不激活**，而 yfinance 实际取得到这批资产的真实行情（`GC=F` / `^GSPC` / `BTC-USD`）。08-14 黄金跑被 G5 涂的那个买入区间就是这个洞的实伤。修法牵动 ticker_payload 与下游 schema，独立立项不塞提示词。
> - 同笔连带（同轮冷审对 08-18 第一笔的 3 处修正·详见 [§6](#6-迭代历史)）：宏观档「判最新一期」→ **超 80 天**（现场判不动）· 分档表加**表外来源兜底档** · 实测文档补**独立观测口径**（26 个非 104 条）。
> - `lint:active-count` 同步改 **13**。

> **📌 更新 2026-08-18（第一笔·只加不关）〔⚠️ 同日第二笔顺手订正：本行原带「⭐ 当前最新」——已由上方第二笔接棒〕：加 BO + BP → 活跃 10→**12**（上限 15·余 3）· **🔴 仍 0 条** · 破例累计 11 不变**。
> - 来源 = 段间 ① 段引用时效判据由「一刀切超 3 天」改**按来源分档**时切出的两条活口，**两条都明确不在那次 scope**（那次只对齐人工侧 · [实测分布](../observations/ref-freshness-asof-20260818.md) · [登记](e2e-acceptance-standard.md)）。
> - **加 BO**🟡 —— 时效窗口 `other = 400 天` 是五档里**唯一没有论证**的（注释仅「放宽」二字，其余四档连失效条件都写了），而**全部外源因无类型标记落此档** ⇒ 13 个月前的新闻今天仍算新鲜。⚠️ **弹药未备**：那 104 条实测量的是 seg1 **内源** references，**不覆盖外源册** —— 动它之前必须先量，别拿不相干数据当证据。收窄 = 提高拦截面 = **承重变更须用户裁**。
> - **加 BP**🟢 —— seg1 引用的时间戳**全程没有代码在看**（只渲染进水印段落 + 段间人工瞄一眼；审核环节全文 `as_of` **零出现**）⇒ **那一行人工判据是它唯一的守卫**。接自动检查牵动数据源装配与下游消费，独立立项。
> - 🔒 **这次改的是「指错方向」不是「放松」**：旧线实测 **13% 越线、真阳性 0**（越的全是 `fred` 月度节律与 `yfinance` 长周末），新档把 **27% 无时间戳**的引用从静默溜过改成显式标注。**判红面零变化**（本判据从来只提醒不阻断）故不走 §4 WARN 试用闸；⚠️ **但提醒面有得有失**：A 股档 3→**10 天**，长假之外若真有一条 5–9 天没更新的行情，**旧线会响、新线不响** 〔**2026-08-18 用户裁决：接受此代价**〕。
> - 两条触发条件**一律事件型**（守 [§4.1 判据有效性约束](#41-新增-backlog-条目)）。
> - `lint:active-count` 标记同步改 **12**。旧 08-14 第三笔 banner 的「⭐ 当前最新」标记**同笔清掉**（该形态此前已六次 stale·Check 8 管日期不管归属）。

> **📌 更新 2026-08-14（同日第三笔·🎉「数字出处」问题域封卷）〔⚠️ 2026-08-18 顺手订正：本行原带「⭐ 当前最新」，其后已叠 08-18 三笔 —— 同类 stale 标记，当前最新 = 上方 08-18 同日第三笔 banner〕：close BC + DEFECT-ANCHOR-MISBIND → 活跃 11→**10**（上限 15·余 5）· **🔴 归零（0 条）** · 破例累计 11 不变**。
> - **六条判据全达成 → 问题域封卷**（用户拍「封卷吧，走 R7 收口」）：D1 ✅（连续 3 次最高信任档零错绑 —— 抽查 #1 = 08-05 执法跑 · #2/#3 = [BC 收官两跑](../observations/bc-final-e2e-20260814/FINDINGS.md)）· D2 ✅ · D3 ✅ · D4 ✅ · **D5 ✅（本次复扫当场判不达标 → 已改）** · D6 ✅。真值源 [endgame](number-provenance-endgame.md) 顶部已立 DONE banner。
> - **close BC**（占 lettered slot·11→10）+ **close DEFECT-ANCHOR-MISBIND**（DEFECT 族·不占配额·**本域主条目**）。⇒ **§0.2 自 2026-08-04 以来的唯一活跃 🔴 消失，全仓 🔴 归零。**
> - 🔒 **close 理由须精确读（防后来者误读成"这类问题没了"）**：close 的是「**本域判据已达成**」，**不是**「编造出处解决了」。08-14 收官跑里该形态**第三次自然复现且手法更宽**（首次空头侧 / 首次编外源数字章 / **凭空造命名空间**而非续编号 ⇒ BC 原记的「同一编号策略」被推翻），**至今没被任何一道门拦过**；三次里唯一没造成伤害那次是**模型自己在收尾轮改对的**，非机制保证。两条同族新形态（**实体归属无人核** / **判别力方向反了**）已记在 [FINDINGS](../observations/bc-final-e2e-20260814/FINDINGS.md)，**本域刻意不接**。
> - ⚠️ **要治这些须重新立项、重新定判据** —— endgame 顶部 banner 已写死**不得挂靠其 DONE 状态**。剩余 🟢 observe 缺口（G3/G5/G6/G7）随封卷归档，**触发条件仍有效**（撞上按条件走）。
> - **D5 复扫的意外收获（值得记）**：当日新写的 342 行文档**表内规范词命中 0**、旧称「水印」×10「锚」×10、另**自造「记号」×13** —— 正是该判据要防的两件事，**第一个违反者就是刚写完它的人**。已按词汇表改到达标。

> **📌 更新 2026-08-14（同日第二笔·+BN）〔⚠️ 同日第三笔顺手订正：本行原带「⭐ 当前最新」，其后已叠封卷一笔 —— 同类 stale 标记，当前最新 = 上方同日第三笔 banner〕：活跃 10→**11**（上限 15·余 4）· **1 条 🔴（BC）** · 破例累计 11 不变**。
> - **新增 BN🟡（投票同构）—— 判据到线执行，不是临时起意**：[段式跑批指南 ⑦ 段](../observations/e2e-runs/segmented-e2e-guide.md)的观察点**开跑前就写死**「再出现一次（N≥3）→ 提立 backlog 条目」；2026-08-04 用户裁「先并入观察点」时 N=2，**BC 收官宏观黄金跑复现 → N=3**，按规则执行。🔒 **立它的第一理由是判据本身**：事前写死的规则到线不执行 = 判据形同虚设，这比这条观察本身更伤。
> - **趋势向坏（不是平稳复现）**：同构范围从「仅 NEUTRAL」扩到「NEUTRAL + BULLISH」；本跑 10 票里 **8 票 `conviction` = 6**，看多 3 张与观望 4 张**各自方差为 0**，六个关键词四票全中。唯二离群 = 天然对立的 bear(8) 与**主动弃权**的 fundamentals(1)（「非个股查询·不具备投票依据」= 诚实出口正常工作）。
> - **方向仍安全 → 记 🟡 不急修**：三次同构全落在保守侧（NEUTRAL / 温和 BULLISH），无「十票齐看错方向」实例；票型方向三次都与辩论内容对得上。本条问的是**独立性**不是安全性。**升 🟠 的条件已写死**：再出现一次同构且方向不再保守。
> - 🚩 **立条目不改任何放行闸**：⑦ 段该项仍是 🔬 观察点（不判 ❌），照 [acceptance-standard §4](e2e-acceptance-standard.md) 提高 fail 面须用户裁。
>
> **📌 更新 2026-08-14（第一笔·锚点检查 WARN 试用落地 + 两笔补录）〔⚠️ 同日第二笔顺手订正：本行原带「⭐ 当前最新」，其后已叠 +BN 一笔 —— 同类 stale 标记，当前最新 = 上方同日第二笔 banner〕：活跃 **10 不变** · **1 条 🔴（BC）** · 破例累计 11 不变**。
> - **本笔**：`lint_doc_links.py` 新增**页内锚点检查**（#240 冷审 defer 项落地）——纯锚点 `#xxx` 此前被该 linter 明确跳过，死链没有任何闸门会报。**按 [acceptance-standard §4](e2e-acceptance-standard.md) 试用期规则：WARN 只报不红**，升 hard-fail 需用户裁决。🔒 slug 规则**先自校准再判**：内置 5 对本仓已实证可跳转的（标题→锚点）判据，校不过 exit 2 拒绝出结论——出处 = 清存量时手写规则被校准连着证伪两次（全角括号被误留 / 标题里 markdown 链接的 URL 被喂进 slug）。验证 = 7 条守护测试 + **6 变异全杀**（含「WARN 被接进 exit code」「校准断线」）+ 全套件 3369 绿。边界如实写：跨文件锚点的锚点半仍不查；代码块里的锚点字面量不豁免（试用期靠噪音暴露）。
> - **补录 08-14（死锚点存量清零·docs-only 直推 main `84ed2c5`+`68ec66b`）**：backlog **162 个页内锚点 61 死 → 0**，加其余文档 6 条 ⇒ **全仓 175 → 0 死**（成因单一 = 条目 close 时标题追加 `✅ CLOSED` 后缀而旧链接没跟着改；23 条落在已 close 条目内 = **经用户单独裁决「全修」**，且机器证明 href-only：抹平跳转地址后改动前后逐字节相同）。最后一条连可见文字也错（§9→§8），经用户裁「一起改」。详见 [DEFECT-FRED-KEYWORD 收口段](#defect-fred-keyword-fred-工具广告了实现认不出的拼写--要利率静默拿到-cpi🟡2026-08-04-bc-探针-e2e-surface✅-closed-2026-08-13close-by-completion保留位置)。（⚠️ 这条链接第一版就是死的——漏了 `✅`，被**本 PR 刚加的检查当场逮住**：同一 session 内手写死锚点第 3 次，WARN 试用期第一单生意。）
> - **补录 08-13 第三笔（close DEFECT-FRED-KEYWORD·[#240](https://github.com/JunoChenZt/subagent-for-investment/pull/240) 合 main `880471d`）**：DEFECT 族不占 lettered 配额 → **活跃数不变**。⚠️ 此笔与 08-14 清零当日均未落 banner —— 「条目改了·banner 忘了」**同一形态第 5、6 次**（07-29/08-05/08-07/08-12 后），本次随 anchor-lint PR 一并补。
>
> **📌 更新 2026-08-13（同日第二笔·close BG）〔⚠️ 08-14 顺手订正：本行原带「⭐ 当前最新」，其后已叠 08-13 第三笔 + 08-14 两笔 —— 同类 stale 标记，随补录一并清掉，当前最新 = 上方 08-14 banner〕：BG 修法落地 → 活跃 11→**10**（上限 15·余 5）· **1 条 🔴（BC）** · 破例累计 11 不变**。
> - **把「记得去 grep」换成机器闸门**：往 `.env` / `.env.example` 加一个数值项，如果它的值恰好等于代码默认值，那些「测代码默认值」的断言就悄悄变成在测本机配置 —— **照常绿、不报错**。原触发条件写的是「加数值项时先 grep 有没有测试在断它」，成色完全取决于当事人记不记得。现在由 [lint_env_shadowing.py](../../scripts/lint_env_shadowing.py) 从源码算出「env 键 → 代码默认值」再比对断言，值相同即报错；已接 CI。
> - 🚩 **开工第一件事就推翻了条目自己记的暴露面**（机器扫 vs 当时人工扫）：① 原清单只扫了 `config.py`，而危险的键**不全住在那儿**（`REFRESH_HOUR` 在 `security_registry/`）；② 原判「靠运气绿」的 `MAX_TOKENS` **其实是安全的那个**（模板值 8192 ≠ 默认 4096 → 会当场变红，吵但看得见）；③ **真正踩雷的两个都是 08-12 那天刚加进模板的**（`CLASSIFY_TIMEOUT` 压着 3 条断言、`REFRESH_HOUR` 得按数字比才认得出 `2` == `2.0`），而当日记录里只写了查过其中一个。
> - **合了候选 1+2、明拍不做候选 3**：规则 1 管「已经生效的雷」（含本机 `.env`），规则 2 管「进了模板就必须留警示」（注释态也要 —— 下一个来取消注释的人当场看见）。候选 3「改 7 处既有断言的取值源」不做：机器已经能在失守当天喊，动既有断言的风险不划算。
> - **豁免表自带防锈**：`ALLOW` 里的条目若已不是真实的雷即报错。否则豁免表会变坟场，把将来真的复发一起罩住。今日仅 1 条（`MIN_CHARS_DEBATE`·早有明文分工）。
> - 🔬 **冷审在检查器自己身上挖出同一个病（四个 finding·全部实测复现过漏报）**：初版手写正则去**猜** `.env` 的加载语义，与运行时那个库差了四处 —— 同键写两次时注释行盖掉生效行（模板里本就有 13 个重复键）/ 值带引号就比不相等（**加个引号即可绕过检查**·本机 `.env` 第 3 行就在用）/ 不认 `export` 写法 / 收集符号按裸名覆盖致断言比对到错的配置项。**四处全是静默漏报**——检查器报干净、雷还在。**修法 = 取值改走运行时同一个库**（重复键 / 引号 / `export` / 变量展开按构造对齐），正则降级只回答「出现过没有、在第几行」，符号重名改成当场报错并逐个候选都查。**代价**：该 CI job 因此不再是纯标准库（多一步装包·本就是项目依赖·仍秒级）。
> - **验证**：35 条自检测试 + **12 个变异全部被杀** + 全套件 3349 passed。⚠️ 变异当场抓到一条**靠错误理由通过**的用例（重名那条只断言「文字里出现了 B 键」，而重名告警本身就会列出 B 键）→ 已收紧。⚠️ **边界如实写**：不追派生链；CI 上没有 `.env`，本机那半靠开发者本地跑测试触发；坑表里另外三条防御**仍靠人**。
> - **计划外**：新脚本刚落地就被 08-07 立的**闸门矩阵**逮住「未接进 CI」—— 那个机制正常工作。
> - 详细记账见 [§6 迭代历史](#6-迭代历史) 2026-08-13 第二笔。

> **📌 更新 2026-08-13（第一笔·close BF）：BF 两件全做 → 活跃 12→**11**（上限 15·余 4）· **1 条 🔴（BC）** · 破例累计 11 不变**。
> - **修的是「静默空过」本身**：⑨ 段两条价位判据有个从不打印的前提 —— fm 这一跑到底把价位填进结构化字段没有。前提不成立时判据**恒真**，于是打勾打了两个月、其实一次都没真验过。现在报告自己印这一行，不成立时直接写「判『本跑无效』而非 PASS」。**空过比空线危险**：空线每次判 ❌ 有人会吵，空过是静默的。
> - 🔬 **冷审收严：两态 → 三态（差点又造一个空过）**：初版按「价位**对象**在不在」判前提，而价位对象的数字字段全 Optional、门控抹价位时**只抹数字留对象** —— 19 份归档里 **2 份**（各被抹 5 处 / 4 处）会被印成「前提成立」而实际一个数字都没有。现改成判**有没有真数字**，并把「填了但被抹」单列第三态、直接点名是不是门控干的（「没给价位」和「给了被拿掉」是两件事，下一步动作不同）。
> - **第 2 件（同根·一行）**：拓扑图纯按段成员染色、不读实际执行，图例却写「本段执行」——条件跳转跳过的节点照样绿（2026-07-30 排查被误导过）。图例改「本段涉及（…非实际执行）」+ 染色函数补注防回退。**贵修法（反推真实执行集）不做**。
> - **冒烟以离线回放替代（用户当日裁决同意）**：改动不经任何 LLM 调用路径，真跑一次 e2e 对它零增量判别力。改为拿 `origin/main` tracked 的 **19 份 ⑨ 段 checkpoint** 重渲染，三形态（没填 11 / 填了 6 / 填了但被抹 2）**全部有真实样本命中**，交叉断言 19/19 过。⚠️ **附成立条件**：结论强度 = 这 19 份归档的形态覆盖，不是「全流程跑通」。
> - 🚩 **顺带堵掉一个自伤**：backlog linter 的三条轻条目守护**锚在 BF 这一行上** —— BF 一 close 就两条真红、一条变空转（断言一行已不被检查的行没被报错）。同型事故 08-06 关 BH 时刚发生过，教训就写在那个测试文件里。本笔**先改锚成合成 fixture、再 close BF**。
> - **计划外坐实的数**：19 份历史归档里 **11 份（58%）`entry` 对象为 null**；按收严后的「`entry` 没有真数字」口径则是 **15 份（79%）**。BF 立账写的是「11 次 run 里 10 次」＝91%，那批是**同期正常 run**；本次样本跨 06→08 全部归档、含大量专项实验跑 —— **三个数口径不同、互不推翻**，都指向「前提不成立是常态」。
> - 详细记账见 [§6 迭代历史](#6-迭代历史) 2026-08-13。

> **📌 更新 2026-08-12（同日第二笔·close AZ + BA 前提订正 + 加 BM）：close AZ 12→**11**，同笔加 BM 11→**12**（上限 15·余 3）· **1 条 🔴（BC）** · 破例累计 11 不变**〔⚠️ **2026-08-13 顺手订正**：本行原带「⭐ 当前最新」标记，其后已叠了 08-13 close BF —— 与 07-29、08-05、08-07、08-12 四行**同类 stale 状态标记**（**同一形态第 5 次**·Check 8 只管日期不管归属），一并清掉。**当前最新 = 上方 📌 2026-08-13 banner（活跃 11）**〕。
> - **加 BM**🟡（用户当场拍「立一条做生产现状对账」）—— **文档在替一台没人核过的服务器说话**：仓库里所有「生产现在如何」的断言从未对过账，而本轮已实测到至少一条错的（BA 原措辞）。⚠️ **要害不是写错，是这种错查不出来** —— BA 的机理断言两轮审计逐条全对，错的是那句从未被写下来因而从未被质疑的隐含前提「线上跑的是 main」。触发条件**全事件型**（守 [§4.1](#41-新增-backlog-条目)·§4.1 立规后第三次自我适用）。🚩 边界写死：只对账与标注，**不改部署配置、不动线上**；历史记录属 Q6 冻结档一字不动。
> - **close AZ**（close-by-completion·两半皆完）—— 链接半 07-29/30 已完（08-12 复扫 0 处未复发）；**env 半随 BA 一并做完**：[.env.example](../../.env.example) 补 6 键全注释形式。**BG 触发动作已执行非跳过**：实查坐实 `REFRESH_HOUR` 有守护测试直断默认值 → 故只登记注释、理由写进模板注释。
> - **BA 不 close·前提订正**（这是本笔的重点）—— 原措辞「生产每次重建镜像清零」是**现在进行时，不成立**：用户确认线上跑的是**旧 S1**，名录功能属 S2 **从未部署** → 该浪费**尚未发生**，是 S2 首部署后才开始的事。机理断言逐条复核**全部仍成立**，错的只是时态。**已落预防**：[.env.prod.example](../../.env.prod.example) 预置 `COMMITTEE_REGISTRY_DB=/data/security_registry.db` → 新建环境开箱即修好；**仍欠**：服务器上已存在的 `.env.prod` 不会自动获得该行。触发条件由「下次 prod 部署 / config review」**收窄为「S2 首次部署时」**。
> - ⚠️ **为什么不 close BA**：修法备好 ≠ 问题解决。生产从未验证过（重建后名录是否真存活 / prewarm 实际耗时），当前 S1 环境**跑不出该现象**。拿"模板改好了"当"已验证"= 撞刹车 Q5（标准降低）。
> - 🚩 **计划外发现（未处理·待裁）**：「线上是旧 S1」这条事实**全仓无处记载**，而 [prod-runbook](../infrastructure/prod-runbook.md) 通篇按「线上≈main」写，[DEFECT-ADVISORY-MODEL-DRIFT](#) 一类条目也按现存环境写生产待办 → **凡是断言"生产现在如何"的条目都可能同样失真**。是否立条目排查见下方 §6 记账。
> - 详细记账见 [§6 迭代历史](#6-迭代历史) 2026-08-12 第二笔。
>
> **📌 更新 2026-08-12（第一笔·AG PR 合并落账）：AG PR [#236](https://github.com/JunoChenZt/subagent-for-investment/pull/236) 已 squash 合入 main `89a440c`** —— 活跃 **12 不变**（08-11 close AG 时已从 13→12·本笔无条目增删）· **1 条 🔴（BC）** · 破例累计 11 不变。
> - **AG close 的实质 = 做完一件 + 放弃两件 + 剥离一件**：① Anthropic 打标记**已做**但**默认关**（单次孤立 run 净亏约 $0.021·用户裁）；②③ 自动前缀缓存 / 跨 role 复用 **实测收益为零 → 放弃（非暂缓）**——A/B 实验里八 analyst 共用段前置后**各角色首调命中量两臂全为 0**；真正的大头（对齐 fund_mgr 两次调用开头、让那段共享正文吃到缓存·预估省 **11%** 账单 = ① 的 7 倍）**剥离为 [S3 §6.1 COST-FM-PREFIX](../roadmap/S3.md)**，不留 backlog 条目。
> - **本条最大价值是计划外产出**：验尺子时查出缓存**写入量恒记 0** 的真缺陷（第三方库把真值拆进另一个字段）→ 成本少算 20%，且「标记有没有生效」本来就无从判断。
> - **合并前四道闸 + 正式冷审 4 条 finding 全部落地**，其中 🔴 最重一条 = **「默认关 = 行为不变」那把测试锁是空的**（假 LLM 不是目标实例、类型闸排在开关之前 → 开关开没开结果逐字相同）；🟡 另一条 = 1 小时 TTL 缓存写入按 5 分钟档计价、**少算 60%**，与「写入量恒记 0」属**同一坏法的另一半**。
> - ⚠️ **SHA 读法**：08-11/08-12 记录里引用的 `82011fb` / `bd4445d` 是**节点分支上的 SHA，squash 后 main 上不存在**；主干唯一提交是 `89a440c`，找代码以文件链接为准。
> - 详细记账见 [§6 迭代历史](#6-迭代历史) 2026-08-11 / 2026-08-12 两笔。
>
> **📌 更新 2026-08-10（一笔·只加不关）：加 BL → 12→**13**（上限 15·余 2）· **1 条 🔴（BC）** 不变 · 破例累计 11 不变**。〔⚠️ **2026-08-12 顺手订正**：本行原带「⭐ 当前最新」标记，但其后已叠了 08-11 close AG（13→12）与 08-12 PR 合并落账 —— 与 07-29、08-05、08-07 三行**同类 stale 状态标记**（**同一形态第 4 次**），一并清掉。**当前最新 = 上方 📌 2026-08-12 banner（活跃 12）**。〕
> - **加 BL**🟡（用户拍「先记 backlog」）—— fred 8s 超时线在 8 路并发下余量只剩 1.32×。来源 = [C2 并发归因探针](../observations/seg2-c2-probe-2026-08-10.md) 的 **§5 计划外观察**，**不是**该探针的事前判据（判据判失败率，结果为「不结论」，C2 既未坐实也未排除）。
> - **⚠️ 别读成"C2 坐实了"** —— 坐实的只是「八路确实在抢同一出口」这个**前提事实**（延迟三轮稳定膨胀 2–3 倍），**越线那一刻从未被观测到**。判据没有事后修改。
> - 三条候选方向**全动主链路须用户裁**，其中「加宽 8s 线」与 [playbook §8](../plans/seg2-flaky-playbook-20260803.md) 直接冲突；**默认第四选项 = 只观测**。本轮**生产代码零改动**。
> - 触发条件**全事件型**（守 [§4.1](#41-新增-backlog-条目)）—— §4.1 立规后第二次自我适用（首次 = 08-07 的 BJ/BK）。
> - 同轮产出（非 backlog 侧）：[攒表 seg2-failure-ledger](../observations/bc-anchor-e2e-20260803/seg2-failure-ledger.md) 建成（run1-4 回填·五条升级判据**全未达线**）· playbook C2/T1/§6 行 + handoff banner 回填。
> - 详细记账见 [§6 迭代历史](#6-迭代历史) 2026-08-10 一条。
>
> **📌 更新 2026-08-06（同日第二笔）：完整 triage 逐条过 14 条 → close AP + Q → 活跃 14→**12**（上限 15·余 3）· **1 条 🔴（BC）** · 破例累计 11 不变**〔⚠️ **2026-08-07 顺手订正**：本行原带「⭐ 当前最新」标记，但其后已叠了 08-07 两笔（BH/AU close · BJ/BK 加）—— 与 07-29、08-05 两行**同类 stale 状态标记**（同一形态第 3 次），一并清掉。**当前最新 = 上方 📌 2026-08-07 banner**。计数 12 虽巧合仍成立（12→10→12），但**"最新"的归属已变**。〕
>
> **本轮与以往 triage 的区别 = 多问了一问**。以往只问「触发条件满足了吗」，本轮每条额外问「**这个触发条件今天还可能满足吗**」——
> 三条处置全部出自这第二问：
>
> - **AP ✅ close-by-merge → [BI](#bi-wisburg-只取研报标题全链无人读正文--半句话成了承重数字的依据2026-08-03-全链回归-e2e-findings-33-逐条过时立账)**（保留位置）。触发形式满足（[#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 大改 audit 匹配逻辑），但对应修法 B 06-24 已撤、落点 `_extract_ref_id` 又被 #226 连同测试删除 → 那条路已死透。**⚠️ 复核 [wisburg_source.py](../../src/committee/common_context/sources/wisburg_source.py) 确认实质问题（一次返回的 20 篇研报塌成单个 `REF#W`）原封不动仍在** → **不是 supersede，是 merge**：与 BI 同数据源 / 同触发条件 / 同前置调查（`discover_tools()`），且 BI 取正文必然要拆 per-report ref。**当初若按 supersede 关掉，会埋掉一个活的登记层缺陷。**
> - **Q ✅ close-by-decision**（保留位置）。核心半已由 **AY** 交付（[#213](https://github.com/JunoChenZt/subagent-for-investment/pull/213)·实证「英伟达」→`NVDA`）；剩余半（通用 source-level 引导通路 / 前端 UI 形态 / `degraded_reason` 体系）按 R7 **搬去 [S3 Line C · L-C.4](../roadmap/S3.md)**，连"与其猜不如问"三条方向约束一并誊过去。
> - **P 触发判据重定为事件型**（不 close —— 事还该做，是闹钟坏了）。修订史按 [§4.3](#43-触发条件本身的修改) 落在条目内。
>
> **共同病根**：P 与 Q 的触发条件（**以及 P 的反向条件**）全挂在「`.3 step6` observation 数据窗持续 ≥1 周」上，
> 而该监测早已停跑 —— [should_update_observations.md](../observations/should_update_observations.md) 只剩历史记录、**无任何在跑的数据窗**。
> 两条从 2026-05-19 挂到今天**两个半月一次都没被评估过**：不是不该做，是**没人可能发现它该做了**（坑表 §3.2 第④形态「前提不成立导致空过」的活样本）。
>
> **⇒ 治理落地（本轮真正的产出）**：新增 **[§4.1 判据有效性约束](#41-新增-backlog-条目)**（触发条件**及反向条件**只能挂"迟早会撞上的信号"，
> 禁止挂"需要有人主动去查"的信号；反向条件挂死信号更隐蔽 —— 让条目**既做不成也关不掉**，永久卡死活跃位）
> + **[§4.2 完整 triage 必须问两问](#42-触发条件命中后的处理)**（答"否"按 重定判据 / close-by-decision+剩余写去引用方 / close-by-merge 三档处置）。
>
> **同轮顺带**：§6 补登记 15 条漏标（**N=4 同类漂移**·根因=lint 脚本 2026-06-02 已入库但无环节强制在收口前跑）；
> 确认 **BF/BG 的「轻条目」形态**（只有 §0.2 行、无 §1 正文）合法。

> **📌 更新 2026-08-05：「数字出处」问题域立单一真值源 + 定完成判据 → 活跃 15→14·此后本域零新增条目**〔⚠️ 08-06 顺手订正：本行原带「（最新）」标记，但其下方已叠了 08-06 两笔 —— 与 07-29 那行同类 stale 状态标记，一并清掉。**当前最新 = 上方 📌 2026-08-06 同日第二笔 banner（活跃 12）**〕。
>
> **起因（用户提出）**：「为什么我们反反复复在做类似的事」。翻账坐实**不是错觉** —— 近 6 周该问题域
> **162 个 commit、横跨 25 个工作日、散落 15+ 条目**，且构成闭环：**2026-07-03 设计的「数字对不对」检查
> → 07-06 量化实证（PE 挂 price 编号·23 个未核值 fact 进最高档）→ 07-14 砍掉（理由「输出侧兜着」）
> → 07-15 输出侧自己收窄为「只核引用不核值」→ 07-16 核值任务降级搁置 → 08-04 同一形态走完全链
> → 08-05 重新实现它**。病根 = 该问题**横跨八个环节却不属于任何一个节点**，每次撞到就「不属本 scope →
> 切条目推给下一环」，而仓库自己的 scope 纪律在横切问题上**反向放大**了这个模式。
>
> **处置（用户裁 B·先定"什么叫做完"再做）**：立 [number-provenance-endgame.md](number-provenance-endgame.md)
> 为该域**单一真值源** —— 6 条完成判据**锁死不新增**（D1 零信任反转连 3 次 e2e / **D2 核值观察期后强制
> 二选一·不许无限期 log-only**〔那正是 AS 当年烂尾的方式〕/ D3 诚实出口有自然样本 / D4 借证结构性
> 不可达最高档 / D5 词汇统一 / D6 散账归一）+ **6 项明确划出域**（Layer 2 / 研报正文 / T10 / 语义核对 /
> web verified / 拆墙发证 —— 均**非判据必需**）。**此后本域不再立独立条目：新缺口只加进该文档 §4。**
>
> **处置表落地（本笔）**：**AW ✅ CLOSED**（close-by-completion —— 命题「核来源非核值·前置到 fund_mgr 前」
> 已被 [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 判定 3/4 实现覆盖；其写死的 Chesterton 前置已在本轮对账履行）→ **15−1=14**；
> **AS ✅ CLOSED**（close-by-supersede·问法被反转：核不动值的出处现在直接拿不到高档；原「等 mismatch 频繁」
> 判据已证自锁 → 改挂 D2。**本条原就不占 lettered·不改计数**）；**DEFECT-ANCHOR-MISBIND 立为该域唯一主条目**
> （close 条件改为判据 D1–D4 全达成）；**BC 归属并入**（close 条件 = D1+D4·`halluc` 移交 §4 缺口 G5）；
> **T10 / BI 加边界澄清**（明确划出域·各自独立走·不阻塞该域收口）。
>
> **⚠️ 顺手订正一处自伤**：BC 的 §0.2 触发状态格原以 **✅** 起头（08-04 我写的），与本表「✅ = 已 close」
> 约定冲突 → 逐行计数时会把**活跃 🔴 读成已关闭**。已改 🔬。**教训**：状态标记的字形本身就是计数口径的一部分。
>
> **仍 0 条 lettered 🔴**（BC 🔴 已并入 endgame 域追踪·MISBIND 属 DEFECT 族不占 lettered）。**破例累计不变。**
>
> **📌 更新 2026-08-06（同日第一笔·#226 合并落账 + 逐行重数）：活跃 **14**（上限 15·余 1）· **1 条 🔴（BC）** · 破例累计 11 不变**〔⚠️ **本行计数已由同日第二笔 supersede** —— 完整 triage close 掉 AP + Q → **活跃 12**·见上方 📌 2026-08-06 同日第二笔 banner。本行其余内容为 point-in-time 记录，正文不改。〕
>
> **计数为何不变**：[#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 已 squash 合入 main `f9620ce`，但
> ① **`DEFECT-ANCHOR-MISBIND` 属 DEFECT-\* 族·不占 lettered 配额**，且**未 close**（close 条件 = endgame 判据 D1–D4 全达成，现 D1 抽查 1/3 —— **PR 合了 ≠ 条目 close**）；
> ② **BC 未 close**（`halluc` 档仍零实证·已移交 endgame 缺口 G5 observe）；
> ③ **零新增 lettered**——该问题域规矩 = 不再立独立条目，本轮新缺口 **G7**（核值可比面 = 手工白名单）已加进 [endgame §4](number-provenance-endgame.md)。
>
> **⚠️ 同一个自伤复发第 2 次（字形口径）**：本次逐行重数机器读出 16 活跃，实为 14 —— 差额来自
> `↳ AX 数据点2`（AX 的**子行**·非条目）与 **AY 的触发状态格以 `**✅` 起头**（粗体标记在前），
> 逐行计数器据「✅ 起头 = 已 close」判定时会把**已 CLOSED 的 AY 读成活跃**。已改为 `✅ **CLOSED…`。
> **这正是 2026-08-05 修 BC 时写下的那条教训**（「状态标记的字形本身就是计数口径的一部分」）**的第二次命中**——
> 说明光记教训不够：**§0.2 触发状态格的首字符是承重的**，写的时候就得让 `✅` 顶格，别被 `**` 挤到后面。
> 〔另注：`AZ` 是**半闭合**（链接半 ✅、env 半仍开）→ **算活跃**，不要因格里有 ✅ 就误销。〕
>
> **📌 更新 2026-08-04（同日第二笔）：BC 升 🔴 + 立 DEFECT-FRED-KEYWORD 🟡 —— 活跃条数不变 15（至上限）·但 §0.2 不再是「0 🔴」**。
>
> **① BC 🟠→🔴（用户拍板）**：条目**开跑前就写死**「若验证结果为拦不住 → 立即升 🔴」，[BC 探针 e2e](../observations/bc-anchor-e2e-20260803/HANDOFF.md) 已验出**拦不住** → 按规则执行。⚠️ **这是 §0.2 自 2026-07-27（AK close）以来第一次出现 🔴 活跃 lettered 条目**，此前每笔 banner 结尾的「仍 0 🔴」自此**作废**。**BC 不 close**：验证任务确实做完了，但 close 会让后来者读成"问题解决了"，实际是**已证拦不住、修法未做**——修法归 DEFECT-ANCHOR-MISBIND，落地后再 close。
> **② 连带 R7 收口（四步走完）**：宽 grep 扫出 9 个文件命中 → **live 就地改 6 处**（§0.2 表行 / 条目强度·任务·触发·反向条件 / BE 条目内边界块 / [acceptance-standard §4 ②](e2e-acceptance-standard.md) / [guide D2 行](../observations/e2e-runs/segmented-e2e-guide.md) / guide 顶部边界声明加第二个反例）· **历史加前向 banner 4 处**（[run-counter](../observations/run-counter.md) 07-31 行 / [FINDINGS §1.3 + §3.9](../observations/regression-e2e-20260730/FINDINGS.md) / [BC 验证设计](../plans/bc-anchor-verification-in-fresh-e2e.md) 顶部）。**BC 原任务写死的「把结论写死进 acceptance-standard」本轮兑现**——回审结论 = **判据不变**（仍 observe·**fail 面零变化**·故 §4「新检查一律 WARN」不适用），**边界往严改**：从「章可能是编的」改成「**章可能真实存在而绑错实体**」。
> **③ 立 DEFECT-FRED-KEYWORD 🟡**（DEFECT 族·不占 lettered 配额）：tool schema 广告 `fed_funds`/`interest_rate`，但 [`_SERIES_KEYWORDS`](../../src/committee/common_context/sources/fred_source.py#L36) 只认 `"fed funds"`（空格）/`"利率"`，子串匹配命不中 → 静默落回 CPI。**R5 分界**：落回 CPI 是**设计**（源文件注释写死 + TODO），缺陷在 **tool 层广告了 source 层认不出的拼写**。**本轮零实际伤害**（模型读了 `series_id`/`unit`，正确标成「CPI 指数」没当利率用）→ 故 🟡 非 🟠。🚩 **副发现**：**工具调用参数全链不落盘** → 这类错配无法从归档反查，只能读代码撞见。
> **④ 另三条够格发现按用户裁「只立 fred 一条」并入既有**：NEUTRAL 票 reasoning 同构 **N=2** → [FINDINGS §3.9](../observations/regression-e2e-20260730/FINDINGS.md) 前向标注 + [guide ⑦ 段](../observations/e2e-runs/segmented-e2e-guide.md)观察点（N≥3 再提立条目）· 终局 gate `Q5 证据误归因` 零判别力 → 已在 DEFECT-ANCHOR-MISBIND 正文 + 本轮补进 acceptance-standard 回审块（**不得拿「Q5 绿」当误归因已覆盖的依据**）· 辩论 token 校准线漏模型组合（本轮 36.6k 出区间·bear(gemini) 24.7k vs bull(deepseek) 11.9k ≈ 2.07×）→ guide ⑥ 段**补一条复核条件**（模型路由变更时也复核·N=1 不改区间）。
> **⑤ 同笔落账**：[run-counter](../observations/run-counter.md) 补 `run-bcprobe-nvda-zh` 行（**excluded from PR-8 gate**·fresh-code 验证跑·照 07-20/07-22/07-31 先例 archive **不复制**进 `_archives/`）。**破例累计不变**。
>
> **📌 更新 2026-08-04（同日第一笔）：立 DEFECT-ANCHOR-MISBIND 🔴 —— 数字挂着别人的出处，系统因"有出处"给最高信任**（**DEFECT 族不占 lettered 配额 → 活跃仍 15**）。BC 探针 e2e seg8/seg9 实证闭合：4 个基本面数字（PE/PB/ROE/净利率）的出处编号全指向「股价」，其中 ROE 在附录被标**最高档已核实**、正文**零提示**；而同段一个诚实的 web 来源数字反倒挂了「（未独立核实）」= **信任反转**。**8 个分析师里 7 个各自独立绑错**（同一约束下的必然反应，非某模型毛病），且多数写了「推算/相关/对应」的保留意见——**被认章层剥掉了**。三道门无一拦住：审计只查编号存在性 → 验章门只看编号属哪个册子 → AI 誊写核查**收到的"来源原文"首行就是待核陈述本身**（自证）。终局 13 项质检全绿，含一项名叫「证据误归因」却报 0%。**条目按用户要求用大白话写**，技术索引在末行。**连带**：[AS](#as-web-派生-fact-缺干净数值源值级可信度-散文数字值无法确定性核-✅-closed-2026-08-05-close-by-supersede保留位置) 的重启判据（"等 AI 核查报 mismatch"）**自锁**——AI 对本形态结构性盲，永不报警。**实测反驳"核数字必须靠 AI"**：本轮 13 条做纯数值比对，10 条错绑全抓、唯一正确的正确放行、零误报（机械/AI 的分界在**源的形态**：结构化标量 vs 自由文本，2026-07-03 设计原文即如此）。**未动任何代码**（全程只观察不改）。**破例累计不变**。
>
> **📌 更新 2026-08-03（同日第五笔）：立 DEFECT-SEG2-FLAKY 🟠 —— seg2 三跑三坏·playbook 落盘·交接新 session**（**DEFECT 族不占 lettered 配额 → 活跃仍 15**·0 🔴）。BC 探针 e2e 的 seg2 同一 checkpoint 三次重跑，三次各塌一个 analyst 且成因全不同（anyio 崩溃 / fred 超时 / 模型格式），统摄假设 = 8 路并发抢共享资源。全清单 + 预案 = [seg2-flaky-playbook-20260803.md](../plans/seg2-flaky-playbook-20260803.md)（21 条失败模式·五层·攒表升级判据·只 plan 未动手）。两处实测修复已随 [#224](https://github.com/JunoChenZt/subagent-for-investment/pull/224) 走（fred 空 error / sanitizer 三兄弟字段）。**破例累计不变**。
>
> **📌 更新 2026-08-03（同日第四笔）：FINDINGS 九条观察项逐条过 → 新增 BH + BI·并入 2 条·不立 5 条 → 活跃 **15 = 至上限**（下次新增前须先 close 一条）**。对象 = 07-30 全链回归 e2e [FINDINGS §3](../observations/regression-e2e-20260730/FINDINGS.md) 的 9 条观察项（立账时全部"未立 backlog 条目·按需分流"），本轮逐条**核代码/核数据**后分流：
> - **立 2 条**：**BH**🟡（`reevaluate_triggers` 四字段恒空 —— 实测 **38 archive / 180 条 trigger 填充率 0%**，根因是 prompt 模板要字符串数组、schema 再包成只有 description 的对象 → **结构上填不了**；S4 §6.3 只落 schema 半边）· **BI**🟡（wisburg 只取标题不读正文 —— 「花旗维持买入目标价 $300」半句话成了 TP $300 的依据）
> - **并入既有 2 条·不另立**：§3.1「基本面数字无 ref 锚」→ **BC**（已核为**设计使然**：`_LAYER1_ONLY_KEYS` 焊点是故意的，Layer 2 明确 defer；但**真实伤害超出当年 defer 理由**=模型改为"随手抓邻近编号挂"，属"绑错实体"这一路，BC 选验证方案时须一并覆盖）· §3.7「trace 把没执行的节点染成已执行」→ **BF**（同 `trace_report.py`、同"只画应然不画实然"病根；已核根因=`_node_classes` 按段成员染色而图例写「本段执行」·**便宜修法=改图例措辞一行**）
> - **不立 5 条**：§3.4 广告链接 **实测已随换 Serper 消除**（旧跑 4 条 `aclick` / Serper 跑 **0** 条）· §3.8 已并入换后端且**已完成** · §3.5 RSS 无 ticker 过滤（🟢·[条目 R](#r-yahoo-finance-rss-长期可靠性--feed-生态腐烂) close-by-decision 时已定过"双源够用"口径·无新证据不推翻）· §3.6 F3 恒不命中（`_F3_OBSERVATION_ONLY=True` 观察期设计·只 log 不返工·**无实际影响**；性质上属"空判据"族，归 [acceptance-standard](e2e-acceptance-standard.md) 校准线而非 backlog）· §3.9 NEUTRAL 六票同构（单跑观察·无根因·留下轮 e2e 观察点）
>
> **⚠️ 计数订正（一并做掉·不是本轮新增造成的）**：逐行数 §0.2 表**无 ✅ 的行**得 **13**，而 08-03 第三笔 banner 记的是 12。差 1 的源头在 **2026-07-31 第一笔 banner 写「9→10」**，而同年 07-29 的 AZ/BA 那笔已经报到 10 —— 此后每一笔都继承了这个 −1。**按 §4.4「计数口径 = 活跃条目」以逐行实数为准 → 本轮 13 + BH + BI = 15**。历史 banner 属 point-in-time 记录，**正文一律不改**（R7）；本行即订正记录。**破例累计不变**（15 = 上限、未超）。
>
> **📌 更新 2026-08-03（同日第三笔）：新增 BG🟡 → 活跃 11→12**（上限 15 内·仍 0 🔴）。[#223](https://github.com/JunoChenZt/subagent-for-investment/pull/223) review 沉淀的下半——**坑表记了「以后怎么办」，没记「现在有哪几条断言站在雷上」**，本条补这半。核心事实：`.env.example` 的 4 个数值项**与代码默认值逐个相同**，故照抄它建 `.env` 的人**自动进入静默遮蔽态**（断言照绿、实已改成在验本机配置）= **构造使然不是巧合**。实扫暴露面：1 条已被遮（已写明·非新洞）· **2 条靠运气绿**（`MAX_TOKENS` / `MAX_TOKENS_ACADEMIC`·这两个键碰巧还没进 `.env.example`，进去那天静默失守）· 其余未撞。**不是保护洞**（CI 无 `.env` → 代码默认值仍有人守），丢的是**本地验证可信度**——而 mutation 证承重是在本地做的。触发条件按用户原话写死：**往 `.env` / `.env.example` 加任何数值项前，先 grep 有没有测试在断它的默认值**。修法故意不预设。**破例累计不变**（新增在上限内·不占破例）。
>
> **📌 更新 2026-08-03（同日第二笔）：BB + BE close·切出 BF → 活跃 12→11**（上限 15 内·仍 0 🔴）。**段间 checklist 数字线一次性重校落地**（用户拍「落地，把 BB、BE 一起收了」）：07-31 那份[对账报告](e2e-guide-threshold-audit-20260731.md)（11 正常 run + 4 对抗 run 回测·**12 条数字线只有 2 条有效**）的结论**回落进 guide**——⑧ `audit_passed ≥50%`→**observe**（实测 6–47%·从没达标）· ⑥ 辩论 token `<15k`→**22k–29k·>40k 才排查**（实测 22.4k–28.4k·每次都超）· ② `evidence_log`→**两步判**（先看正文数字带不带章·收 BE）· ③ `rework≤2` + ⑨ `confidence∈[1,10]` 两条结构性恒真项→**移交单测** [`test_checklist_structural_invariants.py`](../../tests/test_checklist_structural_invariants.py)（8 测·双变异证承重）· ⑥6 轮 / ⑦10 voter→**标注「存活探针」**· guide 顶部加**边界声明**（段间 checklist 量形态完整性、**不量内容真伪**·现成反例=07-31 那跑段间全绿 + gate 13/0/0 而正文躺着 5 个编造引用锚）· 立**校准记录惯例**（每条数字线注明「定于何时·依据什么实测·下次何时复核」）。**承重方向：fail 面只减不增**（无新增检查·故 §4「新检查一律 WARN 试用」不适用·同 S6 收窄先例）——已在 [acceptance-standard §4](e2e-acceptance-standard.md) 逐条登记。**刻意没做**：三条钝线（`key_points≥2` 实测最小 3 / `core_risks≥3` 实测 3–4）**原值未动只加校准注**——收紧 = 提高 fail 面 = 承重变更须用户裁。**切出 BF**🟡（对账建议 3·要改 trace 代码故未随做）→ 12−2+1=**11**。**破例累计不变**。
>
> **📌 更新 2026-08-03（同日第一笔）：AX close → 活跃 13→12**（上限 15 内·仍 0 🔴）。**两条 stale 状态收口**（R7 四步·docs-only）：① **AX ✅ CLOSED** —— 账面写「分支 `auto/websearch-relevance`·待 PR 合入」，实际早随 [#220](https://github.com/JunoChenZt/subagent-for-investment/pull/220) squash 合 main `381824a`（07-31），该分支远程已不存在；且根因（搜索代理丢 `publishedDate`）随 Serper 切换消除（带日期率 0%→62%）= 校验侧与来源侧两头都堵上。13−1=**12**。② **DEFECT-WEBSEARCH-RELEVANCE ✅ CLOSED** —— 账面写「③ 换搜索后端仍开·需用户操作」，实际 07-31 已换成 Serper（Worker `fb6226d`/`b8e4bf0`/`0a1de31` + seg1/seg2 实跑 + [#221](https://github.com/JunoChenZt/subagent-for-investment/pull/221) 实测 1.5–3.9s 真返数据坐实）→ 三层处置 ①②③ 全完成。**DEFECT-\* 族不占 lettered 配额·本条不改计数**。**破例累计不变**。
>
> **📌 更新 2026-07-31（同日第四笔）：新增 BE🟡 → 活跃 12→13**（上限 15 内·仍 0 🔴）。Serper 切换后段式 e2e seg2 段间审核撞出：`technical_report` 的 `evidence_log` = 0，checklist ② D2 按字面判 ❌，**但正文 5 条 key_points 里有 RSI/MACD/均线/VWAP 且数字带 W#+REF# 章** → 判据量的是「字段填没填」，想测的是「判断有没有数据支撑」，**量错了对象**。下游 G1 承重已核（`len(evidence_log)<2`），本次因 conviction 非 Strong\* 未触发；方向属**误报侧非漏报侧**故非安全洞。用户拍「记 backlog、放行」。**破例累计不变**（新增在上限内·不占破例）。
>
> **📌 更新 2026-07-31（同日第三笔）：新增 BD🟢 → 活跃 11→12**（上限 15 内·仍 0 🔴）。Serper 切换第 3 步评测（四维全过：相关率 25%→**100%** / 垃圾率 0% / 空率 75%→**0%** / 带日期率 0%→**62%**）顺带撞出：日期是拿到了，但 Serper 的三种写法（`Dec 19, 2025` / `25 Feb 2026` / `3 months ago`）喂 [as_of.py](../../src/committee/as_of.py#L59) **全返 `''`**——连绝对日期都不认。用户拍 **A（Worker 侧归一）先做·B（扩 `_normalize_as_of`）进 backlog**，理由=改动隔离（Worker 退得回去·主链路严格校验放宽影响面大）。**破例累计不变**（新增在上限内·不占破例）。
>
> **📌 更新 2026-07-31（同日第二笔）：新增 BC🟠 → 活跃 10→11**（上限 15 内·**仍 0 🔴**）。全链回归 e2e [问题清单](../observations/regression-e2e-20260730/FINDINGS.md) §1 三件待决里，**唯一连 backlog 账都没记的一件**落账：R2 多头续写段编造 5 个不存在的引用锚 `REF#Y-009~Y-013` 各挂一个精确数字，全链 ①–⑨ 全过 + gate 13/0/0 **没有一条判据看得见它**；假锚最终没进 `final_decision` 但**原因是 fund_mgr 没采用、不是被门拦下** → 「打码门 / G5 誊写核查能否识别编造 `REF#`」**仍无实证**。**强度 🟠 = 覆盖缺口非已证缺陷**（验出拦不住则升 🔴）。**只登记不裁排期**——验证方案 ①/②/③ 成本差一个数量级且与 §1.1 换搜索后端排期耦合·须用户裁。**破例累计不变**（新增在上限内·不占破例）。
>
> **📌 更新 2026-07-31：新增 BB🟡 → 活跃 9→10**（上限 15 内·仍 0 🔴）。全链回归 e2e seg8 撞出段间 checklist ⑧ 的 `audit_passed ≥ 50%` 是**空线**——五次 run 实测全在 6–13%、从没接近过；根因是 2026-07-22 那次订正只改字段名没重估阈值。用户当场裁「计入 backlog、放行续跑」。**破例累计不变**（新增在上限内·不占破例）。
>
> **📌 更新 2026-07-30：AX ✅ FIXED → 活跃 10→9**。全链回归 e2e 把 AX 的 defer-until-data 条件坐实（触发率 14–19%·`facts_inventory` 全空），用户改判「修」→ 与 **DEFECT-WEBSEARCH-RELEVANCE**（🔴 DEFECT 族·不占 lettered 配额）同 PR 落地。**DEFECT-WEBSEARCH-RELEVANCE 处置 ①② DONE·③（换搜索后端）仍开 = Cloudflare 侧需用户操作**。**无新增 lettered 条目·不动 §4.4 破例计数**。〔**⚠️ 08-03 前向标注（R7·本行为 point-in-time 记录·正文不改）**：「③ 仍开」已 **superseded** —— 07-31 已换 Serper，DEFECT-WEBSEARCH-RELEVANCE 与 AX 均已 CLOSED，见顶部 08-03 banner。〕
>
> **✅ 8 条活跃 · 上限内（2026-07-29·条目 AY close）**：**条目 AY（中文公司名→美股代码兜底）close-by-completion·[#213](https://github.com/JunoChenZt/subagent-for-investment/pull/213) squash 合 main `681ed9e`** —— 4 goal 全落地（可扫描判据条目级化 + curated 34 名候选种子 + classify 重试 + 可疑降级告知）·实证 LLM 超时下「英伟达」→`NVDA`·方向中途转 v2（东财限流不稳 + 名称匹配混淆不同公司）。9−1=**8**·上限内。AY 行保留位置 + ✅。〔**补记（诚实归因）**：`0ed81cc` 关 AY 时只改了 §0.2 表行 + §1 详述块、**漏加本计数 banner**；on-deck header count 的「9」是本轮 `b2f1210` 我凭旧模型误更（没重认 AY 已 close·R6 复发）·非 0ed81cc 所为 → 两处均 2026-07-29 补正为 **8**〕。破例累计不变。
> **✅ 9 条活跃 · 上限内（2026-07-27·条目 R close）**：**条目 R（Yahoo Finance RSS 长期可靠性）close-by-decision·用户拍** —— MarketWatch + Google News 双源已够用（MACRO_EVENT 分支）·多源聚合是 nice-to-have 非 must·三条触发条件（MarketWatch non-200 / RSS 月失败率 >20% / 需增 feed 多样性）**均未命中**·真命中重开即可（换/加 feed 是小活）。10−1=**9**·上限内。R 行保留位置 + ✅。破例累计不变。
> **✅ 10 条活跃 · 上限内（2026-07-27·条目 K close）**：**条目 K（retro amend on cold-review protocol）close-by-decision·用户拍** —— 反向条件（原定 2026-11-25 前无 cross-session retro amend 模式即关）**提前判定成立**：N 停在 2 从未升 3、"冷眼复查后增量发现"已内化进日常 retro 撰写流程（§2.11.7）、不需单独 protocol。11−1=**10**·上限内。K 行保留位置 + ✅。破例累计不变。
> **✅ 11 条活跃 · 上限内（2026-07-27·条目 I close）**：**条目 I（retro governance 三合一）close-by-completion** —— 任务 1/2 落地 governance commit（Q5 撞墙→非技术语言写明→上升人工 · pre-flight「顶层对齐」前置闸），任务 3（O-A6.1.2-02 A/B）用户裁 **A=直接关掉·不改 6 条触发条件**。12−1=**11**·上限内。I 行保留位置 + ✅。破例累计不变。
> **✅ 12 条活跃 · 上限内（2026-07-27·AK merged + AY 切出·净不变）**：**AK 🔴 → close-by-completion 并已 squash 合 main `c03762d`**（[#211](https://github.com/JunoChenZt/subagent-for-investment/pull/211)·两轮外部 review 过·CI 3/3 绿·`auto/AK` 已删）= **收口前唯一 🔴 消**。同轮切出 **AY**（🟡 中文名→美股代码兜底·未触发）→ AK close −1、AY add +1 = **净 12·上限内**。**AK close 后 §0.2 无 🔴 活跃条目**（12 条全 🟡/🟢）。〔**⚠️ R7 更正 2026-07-27**：本行原写「唯一剩的 🔴 = AI（等 S3）」系收口漏网误判——**AI 早于 2026-07-14/16 已 close-by-decision**（MASK.E1 删死枚举 `audit_confirmed_mismatch`/`audit_failed` + AUDIT-3CHECK 砍·安全底线转 Path B/GATE-B·**非「等 S3」**·见 §1 AI 条目 [L831](#ai-audit-pipeline-否定半边失效--confirmed_mismatchfailed-死态--audit_status-零-enforce2026-06-02-s23-gate-agent-review) + §0.2 表行 AI）。〕破例累计不变。
> **✅ 12 条活跃 · 上限内（2026-07-24·AJ close）**：**AJ close-by-completion**（[#206](https://github.com/JunoChenZt/subagent-for-investment/pull/206) squash 合 main `36578b4`·活1+活2 删净·DoD 全绿含真 fresh smoke）→ 13−1=**12**·上限内。AJ 行保留位置 + ✅ 标记。破例累计不变。
> **✅ 13 条活跃 · 上限内（2026-07-24·+AX observe）**：AJ 真 fresh smoke 抓到前存脆性——deepseek 对无日期 fact 吐 `as_of: null`、schema `FactInventoryItem.as_of: str` 不收 → ds_researcher node 校验失败 fallback（**非 AJ 引入**·`as_of` 及 prompt 指引一字未动·grep 证）→ 新增 **AX**（🟢 observe·defer-until-data·单数据点·observe-first 不当场治）→ 12+1=**13**·上限内。破例累计不变。
> **✅ 12 条活跃 · 上限内（2026-07-24·+AW）**：AJ 活2 删除讨论 surface 用户命题「数字**来源**（provenance）核对能否一部分前置到 fund_mgr 拍板前」→ 新增 **AW**（provenance 核对放置·设计议题·仅登记不预设方案）→ 11+1=**12**·上限内。**AJ 未 close**（活1活2 定删·拆解已定·待 greenlight 开工·仍算 1 活跃）。破例累计不变。
> **✅ 11 条活跃 · 上限内（2026-07-24·AV+AN close）**：顺手清两条小债 [#205](https://github.com/JunoChenZt/subagent-for-investment/pull/205)——**AV**（路由契约 TestClient 化·消 openapi 盲点）+ **AN**（dataflow triage/audit 别名·文档债）均 close-by-completion（两行保留位置 + ✅）→ 13−2=**11**。破例累计不变。
> **✅ 13 条活跃 · 上限内（2026-07-24·AH stale-close）**：triage 时 verify-before-acting 发现 **AH（token 用量追踪）早已实现**（`84a69d1`/#145·`token_usage.py` 263 行 + 23 测试 + cli 打表）·条目 stale 从没回填 close → close-by-completion（AH 行保留位置 + ✅）→ 14−1=**13**。**教训**：backlog triage「可动」判断前须 grep 代码核实现状（本条 2026-07-08 triage 曾误列"不建议 close AH"·当时已实现却没发现·R6 同型）。破例累计不变。
> **✅ 14 条活跃 · 上限内（2026-07-23·AL close）**：**AL 整体 close-by-completion**——方向1 [#199](https://github.com/JunoChenZt/subagent-for-investment/pull/199) + 方向2 Layer-1 [#203](https://github.com/JunoChenZt/subagent-for-investment/pull/203) 均 shipped（Layer 2 = 独立可信度路·defer·在二档 cluster 追踪·**不单列 lettered 条目**）→ 15−1=**14**。AL 行保留位置 + ✅ 标记（close-by-completion 惯例）。retro [AL-dir2](../retro/S2/AL-dir2_2026-07-23.md)。破例累计不变。
> **✅ 15 条活跃 · 至上限（2026-07-23·+AV）**：#201 review 副产 **AV**（路由契约负向守卫 TestClient 化·消 openapi 枚举盲点·defer）→ 14+1=**15**·§4.4 上限 15·**至上限**（下次新增前须先 close/defer 一条）。破例累计不变。
> **✅ 14 条活跃 · 上限内（2026-07-23·AT close）**：接上条 15——AL-AT 节点全收口，**close AT**（AT.1 [#196](https://github.com/JunoChenZt/subagent-for-investment/pull/196) + AT.2 [#200](https://github.com/JunoChenZt/subagent-for-investment/pull/200) 全落地·close-by-completion）→ 15 − 1 = **14**。**AL 不 close**（方向1 [#199](https://github.com/JunoChenZt/subagent-for-investment/pull/199) 价格源冗余组 done·但方向2 扩基本面仍开 → 仍算 1 活跃条·只降权重）。节点 [retro](../retro/S2/AL-AT_2026-07-23.md)。破例累计不变。
> **✅ 15 条活跃 · 回到上限（2026-07-23·+AU 后 N close 抵消）**：N 选型讨论副产 **AU**（Python 版本对齐·用户拍单独立项）令活跃一度 15→16 超上限；**同日 N 已 DONE（[#197](https://github.com/JunoChenZt/subagent-for-investment/pull/197) 合 main `4a5d530`）close-by-completion → 16−1=15**·超额自然 reconcile、回到上限内。N 行保留位置 + ✅ 标记（close-by-completion 惯例）。破例累计不变。
> **✅ 15 条活跃 · 至上限（2026-07-21·+AT）**：GATE-B 打码门重构讨论副产新增 **AT**（现价锚点可用性保障·[gate-routing-redesign](../plans/gate-routing-redesign/HANDOFF.md)）→ 14+1=**15**·§4.4 上限 15·**至上限**（下次新增前须先 close/defer 一条）。破例累计不变。
> **✅ 14 条活跃 · 上限内 · live 计数（2026-07-16·supersede 下方 07-08 的 15）**：**AI 已收口**（[MASK.E1](https://github.com/JunoChenZt/subagent-for-investment/pull/184) 枚举 7→4 删死枚举 `audit_confirmed_mismatch`/`audit_failed` + **AUDIT-3CHECK ❌ 彻底砍** → "否定半边"议题**结案**·**非"待 S3"**；安全底线改由 GATE-B 输出侧兜）→ 15−1=**14**·空出 1 slot。**AI 行保留位置 + ✅ 标记**（不删·留追溯·照 close-by-completion 惯例）。破例累计 **11 不变**（close 不动配额）。全程详本文件 §Audit Log「2026-07-16」块。
> **〔以下 2026-07-08 记录 · point-in-time · 已被上条 supersede · 正文不动〕** **✅ 15 条活跃 · 回到上限 · reconcile 收口**（§4.4 上限 15）。**2026-07-08 完整 triage**：① 补表暴露真实活跃 19（§0.2 原停 15·补入 AM/AN/AO/AP·承 [2026-06-30 triage](../../CLAUDE.md) H4 押后）；② **close 4 条回 15**：**X**（by-decision·D1 争议冻结）+ **AO**（by-completion 主体·follow-up 并入 M1 T7）+ **AM**（by-completion·合 main `416d0bb`·抬 academic max_tokens 治截断根）+ **W**（by-decision·债务本体已还清·剩 3 项休眠有据·"对不上"前提已失效因真值源迁移）→ 19−4=**15**。**剩 AJ 留**（cross_role_alignment 死输出·O-S2.3-02 N=2 观测点·真删涉 LLM 输入面需 e2e）。全程详本文件 §Audit Log「2026-07-08 — Backlog 计数 audit #4」。`AF-residual`（🟢·AF 尾巴·spin-out 子项）不计活跃数。
> **2026-06-05 QC-R1 收口 reconcile**：close G（−1，close-by-decision，QC-R1 决议 2 类型 taxonomy，§21.1 5 类承诺撤销）+ 新增 AL（+1，市场感知路由，QC-R1 G6 retro surface）+ AK rescope（接线层剥离归 QC-R1 G5，剩名录层，不计数）。净 15→15，cap 内。破例累计 11 不变。详 [QC-R1 retro](../retro/S2/QC-R1_2026-06-05.md)。
> 2026-06-04 中际旭创 e2e seg1 排查新增 AK，用尽最后 1 slot。2026-06-02 PR #138 merge main #139/#140 后 reconcile：close AA/AE/AF/AD/Z/AB/V（−7，close-by-completion）+ AH/AI/AJ（+3，AH 流程量尺 / AI·AJ S2.3-gate agent-review，上限内自主新增）。§6 已并入 main #139 完整记账（含 AC OBEY-7 close）。

---

## 1. 触发型条目(按条件触发,不按时间)

### V. §13.4 role 差异化必填集定义 ✅ CLOSED 2026-06-02 (close-by-completion)

- **Close 方式**: close-by-completion（PR #139 实现，本 PR #138 merge 后生效）
- **Close 摘要**: B5 per-role 必填集规则（sentiment=narrative_phase / commodity=inventory_phase / political=decision_windows / historian=analogue_period / economist=theoretical_framework / fundamentals=evidence_log）已实现（[rules_b.py](../../src/committee/triage/rules_b.py)，warn-only，12 tests）。本 PR merge main #139 后 B5 在分支生效，正式 close。

- **强度**: 🟢
- **触发条件**: S2.2 启动时（已满足，S2.2 已完成）
- **任务**: A 类 A6 规则按 role 追加差异化检查项。当前 A1-A6 规则对所有 role 一视同仁，但各 role 输出结构差异大（economist 应有 evidence_log 量化数据、historian 应有历史类比 + 时间线等）。定义 per-role 必填集后，分诊员 (A1.2) 可执行差异化质量检查。
- **为什么延后**: A/B/C 分诊规则落地时（2026-05-20）scope 控制——先保证通用规则可用，role 差异化属 nice-to-have。
- **进入 backlog 时点**: 2026-05-20（§13.4 A/B/C 规则落地时显式延后，roadmap-v3.4.md）
- **预估工作量**: 小（定义 per-role 必填字段集 + 更新分诊员规则 + 测试）
- **从 §0.1 转正**: 2026-05-26（S2.2 完成，触发条件满足；A/C close 释放 2 slot）

### K. retrospective-goal skill 加 "amend on cold-review finding" 机制

> **✅ CLOSED（2026-07-27·close-by-decision·用户拍）**：反向条件（原定 2026-11-25 前无 cross-session retro amend 模式即关）**提前判定成立**——N 停在 2 从未升到 3（cross-session 干净数据点未再现），且"冷眼复查后增量发现"已内化进日常 retro 撰写流程（[§2.11.7](workflow/08-retro-node-and-pr.md)）、不需单独 amend protocol。价值薄 + 无触发 + 自带自毁条款 → 用户拍关。下方为立账期记录（point-in-time·不改）。↓

- **强度**:🟢
- **触发条件**:A6.1.1 / A6.1.2 / A6.1.3 retro 各自完成后，**若都出现"retro 写完后又有冷眼 review 增量发现"模式（即 N=3 稳定信号）**→ 启动
- **任务**:在 `retrospective-goal` SKILL.md 加一段 "Amend Protocol":
  - retro 输出后，若 goal 完成 24h 内出现冷眼 review / 外部反馈增量 → 主动 amend 到**原 retro_goal XML**（不另起新 retro，保持单一 source of truth）
  - amend 后更新 `<quality_self_check><must_update_count>` 等计数字段
  - amend 历史显式标注 `(amended from cold-review at <timestamp>)` 字段，便于审计
- **为什么延后**:N=1 数据（仅 A6.1.1.1），需要看是否稳定模式（A6.1.1.2 / A6.1.1.3 是否也出现）。N=1 现在做硬约束太早。
- **进入 backlog 时点**:A6.1.1.1 /review 时点（2026-05-14）
- **预估工作量**:小（改 SKILL.md 加段 + 同步 skill-design.md §3.6）
- **N=3 裁决 (2026-05-25)**: A6.1.3 的 F1/F2 是 same-session warm-cold 抓到的（非 cross-session 双盲），provenance 弱（A6.1.3 retro O-A6.1.3-03 已标注）。如果允许低 provenance 数据凑 N，所有 N=X 判定都要重审。裁决 = **N=2，继续等 cross-session 干净数据点**。
- **反向条件（任一即 close，移 §3 标"已取消+原因"）**:
  - 6 个月内（2026-11-25 前）未出现 cross-session retro amend 模式 → cold review 机制（§2.11.7）可能已经内化到 retro 撰写流程，K 不必单独 protocol

### G. QueryType enum 扩展至 5 类(roadmap §21.1 承诺对齐) ✅ CLOSED 2026-06-05 (close-by-decision)

- **Close 方式**: close-by-decision（QC-R1 节点，PR 待 merge）
- **Close 摘要**: 本条 = QC-R1 taxonomy 重构的立项条目。QC-R1 **决议保持 2 类型轴心**
  （`ticker_specific` / `thematic`）而非扩 5 类——**实证轴心 = 数据路由需求，非主题枚举**
  （roadmap §21.1 "5 类型" 承诺**撤销**：A6.1.1 grill 已发现其只承诺数量未列类型）。
  下方 2026-06-04 三症状**全解**：① hint 当硬闸门 → 加法式路由（`default_sources` 排他二分
  改 `_route` 加法 + 低置信度 union + regex 安全网）；② 中国产业无板块路径 → thematic
  纳产业链/板块 + rss/wisburg 普适；③ 多标的无去处 → `tickers: list[str]` 多标的支持。
  详见 [QC-R1 retro](../retro/S2/QC-R1_2026-06-05.md) + [decomposition](../plans/QC-R1-decomposition.md)。
  enum rename 走 `_missing_` 旧值兼容 + archive replay 测试（194 passed）。
  **保留位置不移 §3**（理由：2026-06-04 三症状约束清单是 QC-R1 起源记录，留此便于追溯）。

- **强度**:🟡
- **触发条件**:A6.1.2 或 A6.1.5 节点设计时,**明确需要**第 3 类型的具体业务路由
- **任务**:按 [§3.10 已知坑维护协议](workflow/09-known-pitfalls.md#310-已知坑维护协议只增不减),加新 enum 值,走 schema breaking change 流程:
  - 更新 prompt 不可覆盖段(加新类型描述 + 边界判定规则)
  - 更新 5 类型 fixture(或 N 类型,N=2+加入数)
  - 跑 archive replay 验证旧 query_type="macro_event" 仍 default 兼容
  - 更新下游消费侧 default 值与路由分支
- **为什么延后**:A6.1.1 grill 发现 roadmap §21.1 承诺 5 种但未列具体类型,
  仅 §6.1 fallback 表明确 2 种。按"实证优先"原则,先实现 2 种,等下游节点
  明确需要新类型时再扩展。
- **进入 backlog 时点**:A6.1.1 拆解时(2026-05-14)
- **预估工作量**:中(schema 演化 + 测试 + prompt 调整,跨 1-2 个节点协调)
- **联动**：S2.2 P0' "ticker 解析层（中文名→符号）" 启动评估时，同步审视是否需要新 QueryType 类型（如 ticker_resolved 后路由到不同分析流）。
- **2026-06-04 约束清单补充**（中际旭创 e2e 实测挖出，taxonomy 讨论开场即带——三个症状同一根：query_type 是路由 hint 却被 `default_sources` 当硬闸门）：
  1. **hint 当硬闸门**：query_type 设计为 hint（[regex_extractor.py:24](../../src/committee/query_class/regex_extractor.py)），但 `default_sources` 拿它硬分叉——`single_ticker`→tushare+yfinance，`macro_event`→fred+rss，决定价格源是否**完全不跑**。
  2. **中国产业问题无板块路径**：`macro_event` 只拉 fred+rss（美国宏观），对"光模块产业链"这类中国行业问题无任何行业/板块数据路径。
  3. **多标的无去处**：原"多标的 query → 默认 macro_event 兜底"建议在硬闸门事实下**变质**——macro_event 价格腿为零，"诚实降级"实为"降到无数据"。**多标的兜底策略随本 taxonomy 决议定，不可独立加。**

### O. 阶段完成归档机制建立

> ✅ **CLOSED 2026-09-28（close-by-completion·S2 收口 G3·保留位置）**：触发条件「S2 阶段完成」满足；三项任务全部完成 —— ① [docs/archive/README.md](../archive/README.md)（归档 = 给阶段写索引页、**文件不搬家**）；② [08-retro-node-and-pr.md §2.11.10](workflow/08-retro-node-and-pr.md#21110-阶段收口时的归档2026-09-28-立)（阶段收口报告合并时触发，子阶段不触发）；③ 原「实际归档：历史阶段文件进 archive」经用户 09-28 裁改为写索引页 → [docs/archive/S2.md](../archive/S2.md)。下方原始记录保留不改。

- **强度**: 🟢
- **触发条件**: 以下任一发生
  - S2 阶段完成 (所有 S2.1 + S2.2 + S2.3 节点 done)
  - 第一次跨阶段需要 (如 S2.1 完成且要起步 S3)
- **任务**:
  1. 建立 `docs/archive/` 目录 + README
  2. workflow §2.11 加归档触发规则 (子阶段 / 阶段触发时点)
  3. 实际归档: 历史阶段 plan / retro / observations 进 archive
- **为什么延后**: S2 远没完成, 现在建空 archive 目录是 YAGNI。
  归档规则细节只有真要归档时才有判断依据。
- **进入 backlog 时点**: 2026-05-14
- **预估工作量**: 小 (建目录 + 加规则 + 实际归档 + commit)

### I. A6.1.2.2+.3 retro governance should_update (Q5 元规则 + pre-flight Read 父节点 + O-A6.1.2-02 升级落地)

- **✅ DONE / CLOSED（2026-07-27·governance commit·用户逐条裁决）**：三合一全部收口——
  - **任务 1（Q5 补注）✅ 落地，且口径经用户强化**：原提案是"达到理论上限 ≠ 降低标准"的**免判注解**；用户 2026-07-27 裁决**改成更强的口径**——撞真上限时**不自行免判放行**，而是**用非技术语言写明问题（撞什么墙 / 哪些做不到 / 诚实替代或 defer）→ 上升人工裁决**（落 [§2.7.5](../governance/workflow/05-brake-self-check.md#275-8-问详细判定标准) Q5，作为 Q5 命中信号）。触发条件"同模式 N≥2 再现"实证满足（N=4：A6.1.2.2 asyncio / A6.1.3 env / D1-ROOT 合成回放 / DOC-SYNC 换手段）。
  - **任务 2（pre-flight 加条）✅ 落地**：作为进 5 问前的**「顶层对齐」前置闸**（Read 父 / 顶层 task 定义确认方向）落 [§2.3](../governance/workflow/02-pre-flight.md#23-节点切入-5-问pre-flight-check)（前置闸写法，不改"5 问"标题 / anchor，避免全仓链接连锁改动）；与 [unverified-premise-protocol.md §4](../governance/unverified-premise-protocol.md#4-与现有-workflow-的集成点) 未落地的"加第 6 问"提案挂钩同源。
  - **任务 3（O-A6.1.2-02 A/B）❌ CLOSED-wontfix**：用户裁 **选项 A=直接关掉·不加话·不改 6 条触发条件**。理由：起源 self-correction 已判此发现"发现性弱"（收口 sub-goal retro 偏薄本可预期）+ 现有 [§2.10.4](../governance/workflow/07-retro-goal.md#2104-retro-质量门槛数量约束)「must_update=0 正常 / trivial 可 skip」已覆盖选项 A 想表达的；选项 B（改条件 6 为复合）过度工程；且信号从未被系统跟踪、两月无人 miss。observation 前向 banner 已加，6 条触发条件不动。
  - **活跃计数**：12 → **11**（close-by-completion 释放 slot；破例累计不变）。
- ↓ 下方为 2026-05-18 defer 时的原始记录，不改 ↓

- **强度**: 🟢 (governance baseline，非阻塞)
- **触发条件**: 以下任一 —
  - 同模式 N≥2 再现 (Q5 "理论上限≠降标准" 或 "pre-flight 未 Read 父节点" 任一在未来 goal 再现)
  - O-A6.1.2-02 ≥2 节点数据 (sub-goal 性质主导命中数在 A6.1.3+ 再现)
  - 下一个 governance PR window
- **任务**:
  1. workflow §2.7.5 Q5 补注元规则 "达到理论上限 ≠ 降低标准" (外层 wait_for 可解范围[可取消慢清理]有效 + 不可解[吞 cancel]诚实标注 = asyncio 理论上限，非偷工降标准)
  2. task entry §2.3 pre-flight 5 问加一条 "Read 父节点/顶层 task 定义文档确认 alignment" (A6.1.2 全程未主动 Read S2.md 顶层定义，.2 后期才补 — O-A6.1.1-01 延伸：顶层 task 定义也是"实证"一种)
  3. （A6.1.2.3 retro 折叠）**O-A6.1.2-02 升级落地**（N=3 闭环已升级，sub-goal 性质主导 retro 命中数）：**选项 A 推荐**（workflow §2.10 加注解"条件 6 收口 sub-goal 单独触发[无 2/3 配合]时 retro 大概率仅结构性，撰写者可简化"，不改 6 条触发条件）；**选项 B 备选**（条件 6 改"high-risk node + ≥1 条 2/3"复合条件）。N=1 节点数据不支撑改触发条件，未来 reviewer 据 ≥2 节点数据 (A6.1.3+) 在 A/B 间定
- **为什么延后**: 任务 1/2 均 N=1 首次（N<3 不拔高 / baseline 走 governance PR 不混节点 PR §2.10.5）；任务 3 O-A6.1.2-02 虽 N=3 已升级，但 A/B 落地选择需 ≥2 节点数据，改 6 条触发条件是高代价 governance 改动
- **进入 backlog 时点**: 2026-05-18 (A6.1.2.2 retro defer + A6.1.2.3 retro 折叠任务 3)
- **预估工作量**: 小 (3 处 workflow 子文档补注/注解 + governance commit)

### N. 依赖 lock 文件机制缺失 — 高漂移 deps 跨环境一致性

- **✅ DONE（2026-07-23·合 main `4a5d530`·[#197](https://github.com/JunoChenZt/subagent-for-investment/pull/197)）**：选型 uv（3-Python×2-OS 矩阵定）·`uv.lock`（117 包·fastapi 锁定 0.136.3）·CI 改 `uv sync`（3.10 验）·Docker 改 `uv export` requirements.txt + CI docker-build job（Linux/3.11 构建验）·三环境全绿·retro [N_2026-07-23](../retro/S2/N_2026-07-23.md)。**剩项单列不阻塞**：① owed① 正式适配 fastapi 0.137 后 un-pin（涉 auth 敏感代码·未做）；② Python 版本对齐 = 新条目 **AU**；③ requirements.txt regen 纪律（retro defer·可加 CI sync-check）。 **〔⏭️ 同日晚些前向更新·R7·正文不动〕owed① 已 DONE**（[#201](https://github.com/JunoChenZt/subagent-for-investment/pull/201) 测试适配 + [#202](https://github.com/JunoChenZt/subagent-for-investment/pull/202) 解钉·lock 锁 0.139.2）——"涉 auth 敏感"顾虑经只读调查证伪=纯测试枚举姿势·移出红线。**发现**：原下方"高漂移 deps 含 akshare/mini-racer"已 stale（akshare→tushare 迁移带走·实际 = yfinance/curl-cffi/protobuf·均锁）。↓ 下方原始记录不改 ↓
- **强度**: 🟡 (影响质量/可复现性，非阻塞工作)
- **✅ 触发实锤（2026-06-15）**: 触发条件 #1（跨环境 deps version skew 实际 bite）**已发生** —— CI 冷启动把浮动 `fastapi>=0.110` 解析成 **0.137.0**（≠ 本地工作版 0.116/0.136.3），0.137 改了 `include_router`/`app.routes` 路由枚举 → `tests/auth/test_route_prefix_contract.py` 红、**主干 CI 红 3 天没人发现**（06-12→06-15，#153 冷审顺带刨出）。**快修 = PR [#154](https://github.com/JunoChenZt/subagent-for-investment/pull/154) pin `fastapi==0.136.3`**（已合 main `856e74e`，闸恢复绿）——band-aid 非治本。**owed 治本（两条都欠）**：① 正式适配 fastapi 0.137 新路由枚举行为后 un-pin（改 auth 注册或测试枚举逻辑，**安全敏感、需用户裁**）；② 落本条 lock 机制根治此类静默漂移（fastapi 现已显式 pin，纳入选型范围）。 **〔⏭️ 前向更新 2026-07-23·R7·正文不动〕owed 两条现均已收口**：② lock 机制 [#197](https://github.com/JunoChenZt/subagent-for-investment/pull/197)（uv.lock）；① un-pin [#201](https://github.com/JunoChenZt/subagent-for-investment/pull/201)（测试适配·只读调查坐实非 auth 代码=当时"安全敏感需用户裁"的顾虑证伪）+ [#202](https://github.com/JunoChenZt/subagent-for-investment/pull/202)（`>=0.137,<0.140`·lock 锁 0.139.2）。
- **触发条件**: 以下任一 —
  - 跨环境 deps version skew 实际 bite (新 dev/CI 冷启动解析出的 akshare/yfinance
    版本 ≠ ledger 记录值，导致 P-sync-bridge timeout 实证基准失真无法追溯)
  - 一个专门的 deps-hardening / 可复现构建 window
- **任务**:
  1. 评估 lock 机制选型 (uv.lock / pip-tools `requirements.txt` / poetry.lock；
     现状 = 纯 pyproject `pip install .` 无 lock，Glob 实测 2026-05-19 确认)
  2. 对高漂移 deps (akshare 多发/周 + yfinance Yahoo churn + 传递 mini-racer/
     curl_cffi/protobuf) 落 lock + CI 用 lock 安装 + 部署 Docker 用 lock
  3. 与 §H/§I observation watch (akshare 漂移 / yfinance rate-limit) 联动
- **为什么延后**: A6.1.3 节点不新开 deps-infra 战线 (用户 2026-05-19 明示
  "本节点不新开战线，继续按现状走")；lock 是跨节点 infra，需独立 window
- **进入 backlog 时点**: 2026-05-19 (A6.1.3.2 step0 加 akshare/yfinance 高漂移
  deps 时，用户 add-item 识别 — 无 lock → 新会话/新环境冷启动版本可能漂移，
  P-sync-bridge .3 实证基准失锚)
- **预估工作量**: 中 (选型 + 集成 + CI/Docker 改造 + 验证可复现)
- **注**: §1+§2 加本条 = **15 条，达 §4.4 上限**。下一新增前需先处理一批
  (多条触发条件已满足，如 D/E "S2.1 子阶段完成后" 等子阶段交接时清理)

### P. facts cache 限流/失效降级语义升级 (defer-until-data)

> **✅ CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— **缓存在生产路径上从来没被接上过**：
> 取数节点自己写着「本节点**从来没给任何路径传过 `cache`**」，全仓 `FactCache` 只在测试里实例化过
> （[context_node.py](../../src/committee/agents/context_node.py) · [builder.py](../../src/committee/common_context/builder.py) 的 `cache` 形参恒为 None）。
> ⇒ 本条描述的失效形态（限流/失效时返空而非 stale）**在今天的管道里不可能发生**。
> **重开条件**：真把缓存接进管道那天，降级语义连同 TTL/失效一并设计（届时另立新条目，不必复活本条）。
> 〔以下正文为 point-in-time 记录，**一字未改**。〕

- **强度**: 🟡 (影响 Phase 0a 召回有效性/质量，非阻塞当前工作)
- **源起追溯**: A6.1.3.2 review 稳定性兜底讨论（2026-05-19）→ 用户定
  "杠杆在 cache 层非 source retry/pin" + observe-first 纪律 → 喂
  [A6.1.3.3 step6](../plans/A6.1.3-decomposition.md) observation 口径
  （异常分类 + 时段 + cache 命中率）
- **触发条件（🔄 2026-08-06 重定为事件型 —— 修改历史见本条目末尾「触发条件修订史」）**:
  - **(A) 主判据·事件型**：**任何改动触及 facts cache 相关代码时**（cache 读写路径 / TTL / invalidation /
    degraded 状态的写入语义），开工前必须显式重审下列三项 ——
    - degraded 状态在 cache 的写入语义（暂时无数据 vs 数据缺失）
    - degraded 频率上升（F1/F2 严格修后）是否影响 cache hit/miss 分布
    - archive 层 degraded 数据点 distribution 是否因 F1/F2 改变
  - **(B) 事件型**：e2e / 生产 run 中出现**一次**具体实例 —— 限流或源失效时 cache 返空而非 stale，
    导致该次分析实际跑在"无数据"上。
    〔🔴 **2026-08-31 标注：本条仍是死信号，但死因与 08-06 那批不同** —— 不是"数据窗停跑"，
    而是**缓存压根没接进管道**：[context_node](../../src/committee/agents/context_node.py) 从不传 `cache`，
    全仓 `FactCache` 只在测试里被构造过。**没有缓存，就不存在"返空还是返 stale"这个分叉。**
    ⇒ **在缓存接进管道之前，(B) 结构上不可能触发。**
    ⚠️ **这不是 08-06 triage 的疏漏** —— "缓存从未接线"是 **2026-08-26 G6 开工时才查出**的潜伏病，
    08-06 无从知晓；且用户 2026-08-26 已裁「**只修钥匙不接缓存**」⇒ (B) 会**无限期**保持死信号。
    **活证据**：2026-08-28 真跑里 yfinance 真撞限流（`YFRateLimitError` × 3）、真返空 ——
    (B) 描述的情形字面发生了，**而它没有也不可能响**（[验收归档](../observations/rp-g5b-human-20260828/ACCEPTANCE.md)）。
    **处置**：(B) 的前置改为「**缓存接进管道之后**才谈」；在那之前它不计入本条的活性判断。〕
  - **(C) 事件型**：akshare / yfinance 任一源出现 endpoint 失效**造成 dispatcher total timeout**
    （撞 `DISPATCHER_TOTAL_TIMEOUT=12.0`）的实例。
  - **(D) 事件型**：用户明确要求"数据源挂的时候别给我空结果，给我上次的"。
  - 🔴 **(A) 已经响过一次，而本条无人回看（2026-08-31 补记）**：**2026-08-26 seg1 G6**
    改的正是缓存钥匙构成（`_dispatch_cache_key`·[#268](https://github.com/JunoChenZt/subagent-for-investment/pull/268)），
    **字面命中 (A)「任何改动触及 facts cache 相关代码」**。当时确实做了重审并由用户裁「只修钥匙不接缓存」，
    **但没有任何人回到本条目登记这次触发与裁决** ⇒ 账面上 P 至今写着"未触发"。
    ⚠️ **这是一个新形态，与 [BU](#bu-裁决--立账落地没有回填义务--真值源静默滞后72-小时内在两处独立撞见同一形态🟡2026-08-27-g7-全链跑排查切出) 相邻但不同**：
    BU 说的是「裁决落地不回填**真值源文档**」，这里是「**backlog 条目自己的触发条件被满足了，却没人回来看这个条目**」——
    事件型判据全靠人**当场想起来有这么一条**，而 backlog 只在 session 启动 / 子阶段交接时被整体过一遍。
    **本次不另立条目**（配额已 19/15），先记在此处；再撞一次同形态即提立。
- **任务**: 设计 "限流/失效时返 stale 而非空" 语义 + TTL/invalidation
  策略（可能涉及 facts cache schema 改动）。喂入映射见 .3 step6 决策点：
  输出 (a)(b)→触发条件 (a)(b)；输出 (d)→触发条件 (c)；输出 (c)(e)→
  cache TTL 策略设计
- **Surface 1 future binding（A6.1.3.3 step8 用户裁决 2026-05-19）**: 本节点未引入 cache，
  Q4 verdict 维持 🟢，无不可逆数据变化。但 F1/F2 修法事实上改变了 degraded 的频率/语义
  特征，任何未来 cache 层工作必须以此为 prior 而非 from scratch。(d)(e) 把这个 prior
  显式写进触发条件，防止未来 cache 工作不知道这段历史。
- **反向条件(任一即 close 不做，移 §3 标"已取消+原因")**:
  - ~~(a) observation 数据显示 degraded 整体 < 5% 且无规律性~~ 〔**⚠️ 2026-08-06 作废**：同样挂已停跑的
    `.3 step6` 数据窗 → 结构上不可能满足。**反向条件挂死信号比触发条件挂死信号更隐蔽** —— 它让条目
    既不可能被做、也不可能被关掉，永久卡死在活跃位上。**替代**：若 (A) 触发时实测 degraded 整体 < 5%
    且无规律性，当场按本条 close。〕
  - (b) curl_cffi 上游补丁让 endpoint 失效稳定缓解
  - (c) 上游(akshare/yfinance)在 .3 后 N 节点内出现稳定替代方案
- **为什么延后**: observe-first 纪律（[[feedback-decision-self-check]]
  单次坑 observe，≥2 次才治理）；cache 层语义升级**非 trivial**（facts
  cache 已有，但"限流返 stale 非空" + TTL + invalidation 边界都是设计
  决策，不能现场 hack）；现在**零真实调用数据点**（A6.1.3.2 测试全 mock）
- **依赖**: **backlog [[N]]（lockfile）先落地** —— 否则 akshare/yfinance
  版本漂移会污染本条触发数据（无法追溯"degraded 升因版本升级 vs 真实源逻辑"）
- **进入 backlog 时点**: 2026-05-19（A6.1.3.2 review 稳定性讨论，用户拍板
  observe-first + 显式 falsifiable 触发/反向条件）
- **预估工作量**: 中（cache 语义升级 + TTL/invalidation 策略 + 可能 cache
  schema 改动 + 测试）
- **⚠️ 上限例外登记（§4.4）**: 本条加入后物理 §1+§2 = **16 条**，声称临时超上限 15。
  **2026-05-19 audit 修正**: 加入时 L 已 ✅ (11:08)，真实活跃 = 15 = 踩线未超，**非真实破例**。
  S2.1 收口承诺不变: 清 D/E/B 回 ≤15。falsifiable，verification-report 届时 flag

#### P 触发条件修订史（§4.3 要求·不允许偷偷改）

- **原触发条件（2026-05-19 立 + 同日扩 (d)(e)）**：五条 (a)~(e)，**统一以「`.3 step6` observation 数据窗
  持续 ≥1 周」计**：(a) yfinance `rate_limit_429` 触发率 ≥ 20% / (b) akshare `endpoint_failure` ≥ 2 次/月
  且 ≥1 次造成 dispatcher total timeout / (c) degraded 下 facts cache 空命中率 ≥ 50% /
  (d) 任何 cache 层实现节点开工前显式重审三项 / (e) production 实证 degraded 率 >X%（阈值待 (a) 实测后定）。
- **修改于 2026-08-06**：改为**四条事件型判据 (A)~(D)**（见上）。(d) 的三项重审清单**原样保留**、并入新 (A)；
  (b) 的实质并入新 (C)、去掉"≥2 次/月"这个需要有人主动统计的量化门槛；(a)(c)(e) **整体作废**。
- **修改原因**：2026-08-06 完整 triage 实测 —— **`.3 step6 observation` 机制已停跑**，
  [should_update_observations.md](../observations/should_update_observations.md) 里只剩历史记录、**无任何在跑的数据窗**。
  ∴ 挂在它上面的 (a)(c)(e) 与 (b) 的量化门槛**结构上不可能满足**，本条从 2026-05-19 挂到 2026-08-06
  共两个半月**一次都没被评估过** —— 不是因为不该做，是因为**没人可能发现它该做了**。
  唯一还活着的是 (d)，因为它是**事件型**（"开工前"是迟早会撞上的动作），但原文限定"cache 层实现节点"，
  需要先有一个规划中的 cache 节点才响 → 新 (A) 放宽为"任何触及即响"。
  **⚠️ 本次未放松也未收紧「该不该做」的判断，只把不可能响的信号换成会自然撞上的信号。**
  本条与 [Q](#q-用户-query-反馈引导通路缺失后续前端同步修改✅-closed-2026-08-06-close-by-decision保留位置)（同因 close）
  共同催生 [§4.1 判据有效性约束 + §4.2 triage 第二问](#41-新增-backlog-条目)。

### Q. 用户 query 反馈/引导通路缺失（后续前端同步修改）✅ CLOSED 2026-08-06 (close-by-decision·保留位置)

> **✅ 2026-08-06 CLOSED（close-by-decision·用户拍）—— 完整 triage 处置。**
>
> **① 核心那半已交付**：本条最有价值的一块（拿不到标的时**问用户**而非静默降级）已由 [AY](#ay-中文公司名--美股代码-仍无确定性兜底ak-已知缺口2026-07-24)
> 承接并合 main（[#213](https://github.com/JunoChenZt/subagent-for-investment/pull/213) @ `681ed9e`）——`is_suspect_degradation` + 确认闸三出口，
> 实证 LLM 超时下「英伟达」→`NVDA`。见下方 2026-07-28 三段更新。
>
> **② 剩下那半已搬去引用方**（R7 步③连带项）：通用 source-level 引导通路 / 前端 UI 形态 / `degraded_reason` 字段体系
> → **[S3 Line C · L-C.4](../roadmap/S3.md)**，连同"与其猜不如问"的三条方向约束一并誊过去。**它做不了也不该做，直到前端有形。**
>
> **③ 为什么 close 而不是继续挂着**：本条 (a)(c) 两条触发条件挂在 **`.3 step6 observation` 数据窗**上，
> 而该监测早已停跑——2026-08-06 复核 [should_update_observations.md](../observations/should_update_observations.md) 只剩历史记录、**无任何在跑的数据窗**；
> (b)「用户反馈 ≥3 次」无采集渠道。∴ 三条触发条件**结构上都不可能响**，从 2026-05-19 挂到 close 共两个半月**一次都没被评估过**
> ——不是因为不该做，是因为**没人可能发现它该做了**（坑表 §3.2 第④形态「前提不成立导致空过」的活样本）。
> 与其留一个永不响的闹钟占活跃位，不如把真实剩余搬到会被自然读到的地方。**本条正是新立 [§4.1 判据有效性约束](#41-新增-backlog-条目) 的起因之一。**
>
> 以下正文保持 point-in-time 不改。

- **强度**: 🟡（影响 F1/F2 严格修法的用户体验价值 + .3 step6 observation 数据纯度，非阻塞）
- **源起追溯**: 2026-05-19 A6.1.3.3 cold review F1/F2 修法决策时 surface。F1 严格修法（raise + `$TICKER` 语法提示）价值依赖"提示能回到用户"路径，实证当前架构**无此路径**
- **具体 gap**: source-level 提示（如 "请用 $AAPL cashtag 语法"）→ 进 log / 进 dispatcher error metadata → **无路径反馈给用户** → 用户只看到 degraded 结果，不知如何改写 query 让 source 成功
- **影响范围**:
  - F1/F2 修法"严格"模式价值大幅衰减（用户无救济，自然语言 query 直接 degraded 无引导）
  - 未来任何 source-level "如何让我成功"提示同样无路径
  - .3 step6 observation 数据可能被 query-format mismatch 污染 → 需 `degraded_reason` 字段隔离 `query_format_mismatch`（用户没用 cashtag/合法码）vs `source_failure`（真故障），前者**不计入** source 稳定性
- **触发条件（falsifiable，任一）**:
  - (a) .3 step6 observation 显示 `query_format_mismatch` 占 yfinance degraded ≥30%（≥1 周窗）
  - (b) 用户调研/反馈明确出现"为什么 AAPL 查不到"类问题 ≥3 次
  - (c) 北极星稳定性评估时识别此 gap 阻碍 SLA 达标
- **反向条件（任一即 close，移 §3 标"已取消+原因"）**:
  - (a) production query 几乎全走 cashtag/合法码格式 → mismatch 不构成实际问题
  - (b) 前端独立路径已实现智能 ticker 提取，backend 不需引导通路
- **依赖**: 前端架构改动（是否暴露 source-level 引导给用户 + UI 形态：error toast / 智能改写建议 / 强制结构化 input）
- **scope 边界**: **不在 A6.1.3 修**（架构层，跨 backend/frontend）；候选节点 = S2.2（UI 集成）或单独 governance 节点
- **🔵 2026-06-05 进展（CLI 临时替代 + 前端归宿备忘）**: 交互式 ticker 确认（QC-R1 裁决 C 曾 de-scope）经用户带理由推翻 → 本次在 **CLI 实装临时替代**（[plan](../plans/ticker-confirm-gate-decomposition.md) G2：跑图前 `classify` → 确认/编辑重搜/取消 → 注入 `confirmed_tickers`）。理由="流程必须拿到用户对 ticker 的输入才能进下一步，否则全链路跑在未确认标的上=全错"。**前端仍是归宿**（同一 `confirmed_tickers` 接缝，前端只换问答 UI 为确认框）——本条保持 🟡 open，前端集成时承接。
- **🔵 2026-07-28 新子问题（AY 节点规划期 surface·用户点名归入本条）**: **「classify 挂 + 名录未命中」时系统既不补救、也不告知用户**。
  - **具体形态**：LLM classify 失败 → [名录扫描](../../src/committee/query_class/classifier.py) 未命中 → regex 认不出中文 → 直接 return `THEMATIC/default`（classifier.py:419-423，**在 `if result is None:` 块内 return**）→ **走不到** Path 1 后置的 web_search 兜底（classifier.py:432 那条 `if` 只在 LLM 成功路径上）。用户拿到的是一份"泛泛主题分析"，**不知道系统压根没认出他问的股票**。
  - **用户提议的修法 = "拿不到就联网查"，评估后判非正解**（3 条，方向安全）：
    1. **两条腿绑同一台发动机**——`_resolve_tickers` 本身是「LLM + web_search」且同用一家 LLM 服务；实测「LLM 挂」主因 = DeepSeek 整体变慢（[AK 补证](#ak-本地证券名录ticker-校验--名称代码兜底)：全提示稳定 3-4s），那时联网查那步大概率一起超时。只在极窄缝（classify 恰超时、search 恰活着）有效。
    2. **该路径下系统连 query_type 都不知道**——无条件联网搜必然给主题型 query 也搜出个股码（搜索总能搜到点什么）→ 把"光模块产业链怎么看"当个股分析。**与 AK e2e 实测的降级事故同性质**（名录 OFF 时个股问题被降级成 THEMATIC 去拉 FRED，"比没拿到 ticker 更糟：整条下游链路分析错东西"）——方向相反、性质相同。
    3. **AY 落地后漏网面已窄**——名录将覆盖 40 手工核心 + ~2800 东财中文名。
  - **正解方向属本条（与其猜，不如问）**：正确行为不是偷偷联网猜一个码，而是**把"我没认出标的"说回给用户**——"未能识别标的，您是指英伟达（NVDA）吗？"。**CLI 确认闸（上条 2026-06-05 进展）是雏形但不覆盖本例**：它在**拿到 tickers 后**回显确认，**拿不到时不问** → 这正是本条 gap 在 AY 场景下的具体形态。
  - **触发条件（falsifiable）**: 真实使用中出现「classify 挂 + 名录未接住 + 用户不知发生了什么」实例；或 AY 收口后 e2e 观察到该路径被走到。
  - **若将来仍要做自动兜底**：须开**窄门版**（仅当 query 含中文公司名候选、且名录查过未中才联网；独立超时预算），不做无条件联网。
- **✅ 2026-07-28 第 3 次更新 —— AY 承接的那块【已实现】**（G4·**已合 main** [#213](https://github.com/JunoChenZt/subagent-for-investment/pull/213) @ `681ed9e`）：
  `is_suspect_degradation` + `_print_degradation_notice` + 确认闸三出口（`e` 给代码 / `t` 按主题继续 / `c` 取消）已落地，
  9 条靶测 + **双向 mutation**（①恒静默→4 红；②不分 source→2 红）。
  非交互路径（`--auto-confirm`/管道/CI）由 classifier 的 default 兜底日志 **info→warning** 兜住。
  **本条仍 🟡 OPEN**：通用 source-level 引导通路（如 yfinance「请用 $TICKER 语法」回传用户）、
  前端 UI 形态、`degraded_reason` 字段体系**均未做**，仍是本条的范围。详见下段。
- **🔴 2026-07-28 同日第 2 次更新（point-in-time·彼时 AY 尚在实施，现已完成→见上段）—— 上段"留给将来"已翻案：[AY 节点](../plans/AY-decomposition.md) 承接本条的一部分**
  （上段分析**全部成立且承重** —— 正是那 3 条理由推出了"与其猜，不如问"，用户随即把它确立为产品理念：
  *涉及个股的一定要和用户确认*。故本条不再"等触发"，**上段的触发条件对这一块作废**）：
  - **AY 承接的块（G4「可疑降级不静默通过」）**：CLI 路径上「classify 挂 → 误判 THEMATIC → 静默降级」这个具体洞。
    **关键设计 = 用现有 [`ClassificationResult.source`](../../src/committee/query_class/schema.py) 区分**，不新增机制：
    `llm`+THEMATIC = 可信主题 → **安静通过**；`default`+THEMATIC = LLM 挂后的兜底 → **⚠️ 可疑** →
    告知用户 + 给三选项（直接给代码 / 按主题分析继续 / 稍后重试）。缺口精确位置 = [cli.py:224-225](../../src/committee/cli.py) 的 `return None`。
  - **AY 不碰、仍留本条（前端归宿不变）**：通用的 source-level 引导通路（如 yfinance「请用 $TICKER 语法」那类提示回传用户）、
    前端 UI 形态、以及 `degraded_reason` 字段体系化隔离。**AY 只治 classify→确认闸这一段**，不建通用通路。
  - **⚠️ 已核实的相邻事实（R5 先证设计）**：`QUERY_CLASS_MODEL` / `TICKER_RESOLVER_MODEL` = **DeepSeek**，
    而 `ANALYST/DEBATE/DECISION_MODEL` = **Claude**（[config.py](../../src/committee/config.py)）→ **不同厂商**。
    ∴「AI 挂 = 后面全跑不出来」**不成立**（Claude 仍活着、会认真跑出一份用户没要的主题分析）→
    **故处置是"告知 + 给选择"而非直接终止**。另：标的识别两条 LLM 路径**全绑 DeepSeek**（classify + 联网查候选），
    一挂俱挂 → 这正是 curated 静态表（零 AI 零网络）不可替代的理由。**是否给 ticker_resolver 配跨厂商 fallback = 超出 AY，另记。**
- **关联**: §9 #14（F1/F2 scope-amend）—— 本条是 F1/F2 严格修法的 architectural complement，不修本条不影响 F1/F2 修法正确性，只影响其用户体验价值
- **为什么延后**: 跨 backend/frontend 架构改动，非 A6.1.3 scope；F1/F2 数据正确性修法独立成立不依赖本条
- **进入 backlog 时点**: 2026-05-19（A6.1.3.3 cold review F1/F2 修法决策 surface）
- **预估工作量**: 中-大（前端架构决策 + backend 引导 metadata 通路 + UI 形态）
- **⚠️ 上限例外登记（§4.4，真实第 1 次破例）**: 本条加入后物理 §1+§2 = **17 条**，真实活跃 = 16 (L 已 ✅)，**第 1 次真实超上限** (原声称第 2 次, 见 Audit Log 2026-05-19 修正)。用户裁决 (c)：暂超 + S2.1 收口承诺加码——清 D/E/B + 额外显式审 Q 触发/反向条件。falsifiable，verification-report 届时 flag
- **🔵 透明纠错登记（用户指示，O-A6.1.2-01 第 5 正面数据点）**: 2026-05-19 backlog Q 处置讨论中，**Claude 陈述 "backlog 18/15 (暂)"算错**；用户**执行决策前先实证 ledger**（实际 P=16 → 加 Q=17/15），Claude 复核确认算错并采纳纠正。与前 4 个 O-A6.1.2-01 正面数据点同模式（拒绝接受表面值、二次实证后才执行）。**特殊点（维度更广）**：此次纠正对象 = **Claude 自身的算术/陈述**，非工具输出/命令结果 → O-A6.1.2-01 防御覆盖维度扩展为"Claude 自报的数字/状态也须 verify，不只工具"。详 [O-A6.1.2-01 第 5 数据点](../observations/should_update_observations.md#o-a612-01-实现阶段对-plan-模糊处自行解读未回查-plan-明文--未回头补-plan) + backlog J N=2 reviewer 首测点（[O-A6.1.3-03](../observations/should_update_observations.md#o-a613-03节点级-cold-review-n2--一次-cold-review-不穷尽同类红线backlog-j)）

### R. Yahoo Finance RSS 长期可靠性 — feed 生态腐烂

> **✅ CLOSED（2026-07-27·close-by-decision·用户拍）**：MarketWatch + Google News 双源已够用（MACRO_EVENT 分支）、多源聚合是 nice-to-have 非 must-have；三条触发条件（MarketWatch non-200 / lastBuildDate>24h · RSS 月失败率 >20% · 需增 feed 多样性）**均未命中**。若将来某触发条件真命中，重开即可（换/加 feed URL 是小活）。下方为立账期记录（point-in-time·不改）。↓

- **强度**: 🟢 (有兜底, 不阻塞)
- **触发条件**: 以下任一 —
  - PR-A 选用的 MarketWatch URL 出现 non-200 或 lastBuildDate > 24h
  - evidence log 中 RSS source 月失败率 > 20%
  - 需要增加 RSS feed 多样性（当前 = MarketWatch + Google News 双源）
- **任务**:
  1. 评估长期 RSS 方案: 多源聚合 (marketwatch + reuters + ft 公开 feed) vs 单源 + retry
  2. 如果切多源: 更新 `_DEFAULT_FEED_URLS` + 去重逻辑 + verify harness
  3. 如果保持双源: 加 feed-level health monitor (失败率 > 阈值自动降级/告警)
- **背景**: A6.1.4 Phase 0a 实测发现 Yahoo Finance RSS 生态整体腐烂 —
  `feeds.finance.yahoo.com/rss/2.0/headline` 返回 404,
  `finance.yahoo.com/news/rssindex` 返回 429。Yahoo 官方未公开 RSS 政策,
  URL 历史多次静默变更。PR-A 短期修复: 切 MarketWatch (`www.marketwatch.com/rss/topstories`,
  实际重定向到 Dow Jones CDN `feeds.content.dowjones.io`)。
- **为什么延后**: MarketWatch + Google News 双源已够用 (MACRO_EVENT 分支),
  当前无紧迫性。多源聚合是 nice-to-have 非 must-have。
- **进入 backlog 时点**: 2026-05-19 (A6.1.4 Phase 0a surfaced debt #2, PR-A 修复)
- **预估工作量**: 小 (换 URL / 加 feed + 测试)
- **⚠️ 上限例外登记（§4.4，真实第 2 次破例）**: 本条加入后物理 §1+§2 = **18 条**，真实活跃 = 16 (L+H 已 ✅)，**第 2 次真实超上限** (原声称第 3 次, 见 Audit Log 2026-05-19 修正)。
  S2.1 收口承诺不变: 清 D/E/B（活跃 16−3=13 ≤15 ✓）。
  **严格条件**: 不再允许第 3 次真实破例 — 下一新增前**必须先 close 至少 1 条**。
  **⚠️ 2026-05-25 audit #2 追记**: 此严格条件被 W/X/Y/Z 违反（第 3-6 次真实破例，0 close 加 4 条）。详见 Audit Log 2026-05-25。

---

### W. PR-8c 设计文档技术债（合并条目 — 大半已被 P4.B 返工解决）✅ CLOSED 2026-07-08 (close-by-decision·保留位置)

- **Close（2026-07-08·backlog triage 配额 reconcile·用户拍）**: close-by-decision，三条理由：① **债务本体已还清**——死链（RW-0 恢复+re-home）/ challenge-response 闭环（RW-2）/「5 gate 只 1 工作」（RW-1 双档）返工时全解，剩的只是 3 个休眠增强项。② **剩 3 项休眠有据**——G1 per-call（须先反驳 schemas.md 报告级权威·无人提议）/ F×T 失效位真信号（须 technical schema 加不存在的 key-level 字段）/ G4·G7（PARK），全部真值源在 [risk-gate-design.md §B.16 + Supersession Ledger](../pipeline/decision/risk-gate-design.md)，触发都是"有人提议 X/加字段 Y 时"、相关时自然浮现，不需 backlog 挂着。③ **「对不上」前提已失效**——本条"设计文档与实现脱节=债"的框架假设 pr-8c 是应追踪代码的活文档；但真值源已迁移（as-built=代码+[gate-mechanisms-map.md](../pipeline/decision/gate-mechanisms-map.md)·design=risk-gate-design.md），**pr-8c 是 2026-05 历史设计基准**（0 处提层② EXEC-FLOOR/all_unverified·冻结在两轮闸门重写之前），强行对齐历史文档到今天代码=改写历史（违 R7）。连带：给 [pr-8c-hard-block-trigger.md](../observations/pr-8c-hard-block-trigger.md) 加前向 banner 标历史+指当前真值源（防后人误读）。
- **强度**: 🟡（剩余项不阻塞，下次 risk gate 演进前消化）
- **归类**: 设计文档与实现脱节
- **进入时点**: 2026-05-21（P4.B Q1/Q2 surfaced）；**RW-0~RW-3 返工后大幅修订 2026-05-21**

**✅ 已被返工解决**：
1. ~~死链 `agent role decision.md` B.16.x 引用失效~~ → **RW-0 解决**：从 git 恢复 + re-home 到 [risk-gate-design.md](../pipeline/decision/risk-gate-design.md)，pr-8c 死链改指。
2. ~~fund_mgr risk_gate_response 闭环推迟（a2）~~ → **RW-2 解决**：challenge-response 闭环已实装（fund_mgr 逐条回应）。
3. ~~体系问题①"5 个 gate 只 1 个真工作 / G5 单档"~~ → **RW-1 + RW-2 解决**：hard_block 从 G5 单档改 **G1+G5 双档**（RW-1，任何 high finding 触发）；challenge-response 闭环（RW-2）让**全部 gate（含 warning G2/G3）有牙齿**——fund_mgr 必须逐条回应，gate 不再是"没人照的镜子"。剩余仅 G1 per-call 精度（下方剩余项）+ G4/G7 PARK。

**⚠️ 修正过去的误判（RW-0 考古推翻）**：
- 旧 item 2/3 写"DirectionalCall.conviction **缺失/PR-5 砍了**、G1 用 proxy **待升级真值**"——**这个框架是错的**。RW-0 考古（[risk-gate-design.md §B.16.2 supersession](../pipeline/decision/risk-gate-design.md)）确认：**报告级 conviction 是当前权威口径**（[schemas.md](../architecture/schemas.md) 2026-05-13 + roadmap-v3.4 B1/B2），per-call 是被取代的旧 spec（agent-role-decision）。
  - **不是"砍了字段待补"，是"报告级是权威，per-call 未被沿用"**。"是否经考虑否决 per-call"**不可考**（反驳点 6 不涉粒度、原始异议丢失）——**不捏造"刻意砍"**。
  - G1 用报告级 conviction = **用权威口径**（非 proxy）；RW-1 后 G1=high 可触发 hard_block。报告级精度局限见 [pr-8c-hard-block-trigger.md §3.0](../observations/pr-8c-hard-block-trigger.md)。

**🟡 剩余真开放项**：
- **G1 升 per-call（若做）**：不是"补回被砍字段"，是**往当前权威 schema 加它没有的粒度** → **须先反驳 schemas.md + roadmap B1/B2 的报告级权威**。无此反驳不动。触发：有人提议 per-call conviction 时。
- **F×T "失效位接近" 真信号**（P4.B.6 / D14）：当前 proxy（conviction 方向背离）**仅部分覆盖**（覆盖"结构未确认"、**漏"失效位接近"、欠注入**）；D15 已补段内容引导（RW-3）。真覆盖需 technical 结构化 key-level 字段（当前无）。触发：technical schema 加 key-level 字段时。
- **G4 Margin of Safety / G7**：PARK（见 risk-gate-design.md §B.16.6）。

- **预估工作量**: 小（剩余项是 schema 字段 + gate 升级，非重建设计——设计已 RW-0 恢复）

---

### X. D1 hard contract 强读/弱读争议（元层面冻结）✅ CLOSED 2026-07-08 (close-by-decision·保留位置)

- **Close（2026-07-08·backlog triage 配额 reconcile·用户拍）**: close-by-decision——当前实现已定（RW-2 按弱读执行·合规）；触发条件①「原始 grill 论证被找到」= 已确认丢失、近乎永不发生；触发条件②「给 FinalDecision 建 fallback 体系时重审强读」= **那时自然会碰到的设计决策**，不需 backlog 挂着提醒。冻结无限期、占 slot 无收益。争议记录 + RW-2 弱读决策已在 [risk-gate-design.md §B.16](../pipeline/decision/risk-gate-design.md) 有真值源，本条指针撤除。保留位置作追溯。
- **强度**: 🟢（不阻塞；RW-2 已按弱读执行）
- **背景**: [risk-gate-design.md §B.16.1](../pipeline/decision/risk-gate-design.md) D1 "fund_mgr 必须回应…通过结构化 schema 字段强制；不接受 prompt 自律" 与同文档 §B.16.3/§B.16.4 的 v1 取舍（prompt 强制 + warn-only event）**自相矛盾**。D1-(a) 原始 grill 论证**不在恢复文件内、不可考**。
  - **强读**：schema validator 硬拦截 → 当前实现（warn-only）违反 D1 hard contract。
  - **弱读**：结构化字段非散文，warn-only 兜底 → 当前实现合规。
- **RW-2 决策**: 显式按**弱读**执行（理由：bare validate 无 fallback，硬拦截会崩 run，违稳定性 P1；与 §B.16.3 v1 取舍一致）。**强读争议冻结**，RW-2 不 mid-flight 重审。
- **触发条件**: D1 原始 grill 论证被找到（如其他 grill doc 浮现）/ 给 FinalDecision 建 fallback 体系时（届时强读硬拦截才可行且无崩 run 风险）。
- **进入时点**: 2026-05-21（RW-2 挡板 1.3）

---

### Z. fund_mgr 跨模型对照 → ✅ moved to §3 (CLOSED 2026-06-02)

### AA. Rework 盲重试 — triage failure notes 未反馈给 analyst LLM ✅ CLOSED 2026-06-02 (close-by-completion)

- **强度**: 🟡（不阻塞 S2.2 merge，但显著降低 rework 修复率）
- **背景**: S2.2-gate batch 1 发现 `make_rework_node()` 是 **blind retry** — 直接重跑 `analyst_nodes[role](state)`，same prompt / same state，不传 triage 失败原因。当 analyst 因 B3 scenarios=[] 被 reject 时，rework 不告知 "你的 scenarios 是空的请补充"，LLM 大概率重复同一错误。S2.2-gate 中 historian/economist 均 rework 2 次仍 fail。
- **修法方向**:
  1. `_triage_one` 的 fail notes 传递给 rework node
  2. rework prompt 末尾追加: "你的上一次输出被拒绝，原因: {notes}。请针对性修正。"
  3. 参考 F-class rework 机制（已实现 "在 user message 末尾追加违规警告"）
- **触发时机**: S2.3 rework 优化节点启动时
- **不做的后果**: rework 永远是盲重试，对结构性缺失（如 scenarios=[]）几乎无效，浪费 LLM 调用 + 时间预算
- **进入时点**: 2026-05-26（S2.2-gate root cause analysis）
- **证据**: [run-s22-2](../../docs/observations/_archives/run-s22-2_hk-tech-top-or-recovery.json) 等 pre-fix archives — historian rework_count=2 仍 reject
- **Close 方式**: close-by-completion（2026-06-02）
  - `state.py` 新增 `rework_notes: dict[str, list[str]]` 字段
  - `triage/rework.py` `rework_dispatcher` 从 `triage_verdicts` 提取 reject 的 `notes`，写入 `patch["rework_notes"]`
  - `agents/base.py` `make_analyst_node` 检测 `rework_notes[role]`，在 user prompt 末尾追加"上一次被拒原因 {notes}，请针对性修正" → 盲重试改为带反馈重试
  - 1864 tests passed, 0 failed
- **⚠️ 2026-06-16 后续观察（AA 修法对 macro/scenarios 不充分 — D run seg3 复现，跑完 D 后排查根因）**:
  AA 的 close 假设"带 `rework_notes` 反馈重试即可修结构性缺失"。**D hot-e2e seg3 实证不充分**：macro 分析师
  （`deepseek-v4-flash`）**带 rework_notes 反馈返工 2 次仍补不全 `scenarios` 必填字段** → 稳定触发
  reject-after-rework drop（本轮 7/8，macro 整路丢）。即 AA 的"告知原因→模型修正"对**弱模型补结构字段**这一类
  有残留缺口（告诉它缺 scenarios ≠ flash 模型就能产出）。**根因待查（跑完 D 后，本轮只登记）**：① rework 提示是否
  把 scenarios 要求讲清 ② `scenarios` 对 macro 角色是否合理必填（B3 vs macro prompt 是否本就不产 scenarios）
  ③ `deepseek-v4-flash` 是否够格补结构化字段（弱模型能力上限）。**不查→每轮稳定丢一路 macro**（覆盖度系统性 -1）。
  触发源：[D run seg3](../observations/fm-refactor-spec/D-hot-e2e-2026-06-16/LEDGER.md)。是否 reopen AA / 新建条目 = 排查后定。

### AC. fund_manager 合成层不服从下游信号 → ✅ moved to §3 (CLOSED 2026-06-02)
- **子缺陷打包**（都属服从性 bug，非证据绑定）:
  - 投票/决策矛盾：vote `weighted.NEUTRAL=24 > BULLISH=22 > BEARISH=21`，fund_mgr 写 `ADD`
  - risk_gate G2 fund_mgr 自己写 "暂停执行该仓位调整"，但 decision 不变、execution_plan 完整下达
---

### AD. 证据绑定 / Audit Pipeline 升级 → ✅ moved to §3 (CLOSED 2026-06-02)

### AB. DS-0 (pass0_assistant) 在大上下文 + 慢 LLM 下 timeout → fallback ✅ CLOSED 2026-06-01 (close-by-completion)

- **强度**: 🟡（fund_manager fallback 路径已就位，不阻塞；但导致 S2.3 三大新功能 — facts_inventory / Audit Pass 0.5 / {ref:fX} — 在 deepseek 路径下实际不可达）
- **背景**: 2026-05-28 全 deepseek e2e 测试（query="夏天炒电"）DS-0 节点触发 `TimeoutError`。pass0_assistant 输入 = 8 份 analyst report + 全 common_context（粗估 30-50k tokens），deepseek-chat 在 high-load 时 first-byte latency 可超默认 httpx timeout。fallback 后 `facts_inventory=[]`，fund_manager 走 S2.2 兼容路径（thesis 正常出，{ref:fX}=0、audit_status 全无）。
- **修法方向（按工作量递增）**:
  1. **独立模型路由**：加 `COMMITTEE_MODEL_PASS0_ASSISTANT` 环境变量，默认 `claude-sonnet-4-6`，不让 DS-0 跟 analyst tier 共享 deepseek
  2. **独立 timeout**：DS-0 LLM client timeout 配置项（默认 180s），独立于其他角色
  3. **分批处理**：把 8 份 analyst 切 2-3 批喂 DS-0，分批 facts 合并（重写 prompt 工程量大）
- **触发时机**：
  - 任何"需要 {ref:fX} 端到端 demo / S2.3 audit 功能完整验证"的工作启动前
  - 或：[Z 条目](#z-fund_mgr-跨模型opus-vs-deepseek对照验证-✅-closed-2026-06-02-close-by-completion) 激活时合并处理（同源 — 都是"deepseek 顶替更强模型的隐性假设"）
- **不做的后果**：deepseek 路径下 S2.3 三大新功能（DS-0 / Audit / {ref:fX} citations）整条链路 100% fallback，等于"演示用 opus、测试用 deepseek 永远走 fallback"——验证覆盖率长期失真
- **进入时点**: 2026-05-28（PR [#133](https://github.com/JunoChenZt/subagent-for-investment/pull/133) + [#134](https://github.com/JunoChenZt/subagent-for-investment/pull/134) merge 后首次 e2e 触发）
- **证据**:
  - [e2e run JSON (utf8)](../../docs/observations/e2e-runs/e2e-deepseek-summer-power-20260528-121221-utf8.json) — `pass0_result.facts_inventory.length == 0`
  - [e2e stderr log](../../docs/observations/e2e-runs/e2e-deepseek-summer-power-20260528-121221.log) — `Pass 0 LLM call failed: TimeoutError() — fallback`
- **归类 / 教训归属**：与 [Z](#z-fund_mgr-跨模型opus-vs-deepseek对照验证-✅-closed-2026-06-02-close-by-completion) / [Y](#y-incomplete-event-真实触发率的跨模型差异监测-✅-closed-2026-05-29-close-by-decision) 同源 — "deepseek 顶替更强模型的隐性假设"
- **Close 方式**: close-by-completion（2026-06-01，`auto/AC-part2` 分支）
  - 修法方向 1（独立模型路由）：DS-0 三节点（ds_researcher / ds_debate / pass0）代码 default `deepseek-chat` → `deepseek-v4-pro`；`.env` / `.env.prod` 新增 `COMMITTEE_MODEL_DS_RESEARCHER` / `COMMITTEE_MODEL_DS_DEBATE` / `COMMITTEE_MODEL_PASS0` 独立配置项
  - 修法方向 2（独立 timeout）：`pass0_parallel.py` DS_TIMEOUT 从硬编码 60s 改为 env 可配 `COMMITTEE_DS_TIMEOUT`（default 600s）
  - 1863 tests passed, 0 failed

### AE. 核心 pipeline 在弱模型/瞬时故障下的健壮性缺口（多个未设防 LLM-输出处理点）✅ CLOSED 2026-06-02 (close-by-completion)

- **强度**: 🟡（非 tool 路径已 robust；但 tool-using 角色 + 瞬时故障会崩整 run；强模型偶发畸形 JSON / 网络错误也中招）
- **背景**: 2026-05-29 全 deepseek-chat e2e（query "分析 AAPL 当前投资价值"，验证 EVID/OBEY/DS-0 期间）连续暴露 **3 个不同位置**的崩溃，均为"单点瞬时/畸形输出 → 未设防 → 崩整条 pipeline"，违反系统别处一致的优雅降级设计：
  1. **rework_dispatcher CancelledError**（✅ 本会话已修，commit 待 PR）：`isinstance(result, Exception)` 漏 `CancelledError`（Py3.8+ 起继承 BaseException 非 Exception）→ `patch.update(CancelledError)` → `TypeError: 'CancelledError' object is not iterable`。修法：`isinstance(result, BaseException)`（[rework.py](../../src/committee/triage/rework.py)）+ 3 回归测试。
  2. **analyst Phase-1 APIConnectionError**（✅ 本会话已修）：`make_analyst_node` 的 LLM/tool 调用无 try/except → 单个 analyst 瞬时连接错误崩整并行 fan-out。修法：catch `Exception` → `validate_with_fallback` 降级 report；`CancelledError` 仍传播（[base.py make_analyst_node](../../src/committee/agents/base.py)）+ 3 回归测试。
  3. **fund_manager tool-agent JSONDecodeError "Extra data"**（✅ 本会话已修）：`run_tool_agent`（[agent_loop.py:169](../../src/committee/tools/agent_loop.py)）直接 `extract_json_fn(text)` → 旧 `_extract_json` 的贪婪 `\{.*\}`+`json.loads` 对"valid object + 尾随内容"崩。修法：`_extract_json` 改用 `json.JSONDecoder().raw_decode()` 从首个 `{` 解析（容忍尾随）+ sanitize 重试 + 抛受控 `ValueError`（不漏裸 JSONDecodeError）；新增 `_make_tool_json_extractor(role, model)` 工厂做 role/model/snippet 日志（[base.py](../../src/committee/agents/base.py)）+ 11 回归测试（含"valid object + extra content"）。
- **剩余未审计的同类点（本条 OPEN 部分）**: debate / vote / ds_researcher / ds_debate 等节点的 LLM 输出解析是否也有未设防点，本会话**未逐一 audit**；`run_tool_agent` 的 `extract_json_fn` 失败目前仍向上抛（analyst 已有 fallback 兜，fund_mgr head 仍按"无决策头=致命"设计 re-raise 受控错误）。
- **修法方向（剩余）**:
  1. 系统扫一遍所有 LLM-输出解析点（debate/vote/ds），统一用 robust 解析 + 受控错误
  2. （可选）评估 fund_mgr head parse 失败是否也应降级而非致命（当前 by-design 致命）
- **触发时机**: 任何"完整 e2e 在弱模型下必须跑通"的需求；或 [Z](#z-fund_mgr-跨模型opus-vs-deepseek对照验证-✅-closed-2026-06-02-close-by-completion) / [AB](#ab-ds-0-pass0_assistant-在大上下文--慢-llm-下-timeout--fallback-✅-closed-2026-06-01-close-by-completion) 跨模型验证激活时合并处理
- **不做的后果**: 全 deepseek e2e 仍可能在未审计的解析点崩（验证覆盖率失真）；强模型生产偶发畸形输出也可能崩 debate/vote 节点
- **进入时点**: 2026-05-29（EVID/OBEY/DS-0 验证 e2e 连续 3 崩暴露；**3 个具体崩溃本会话全修**，剩余系统扫描延后）
- **归类**: 与 [Z](#z-fund_mgr-跨模型opus-vs-deepseek对照验证-✅-closed-2026-06-02-close-by-completion) / [AA](#aa-rework-盲重试--triage-failure-notes-未反馈给-analyst-llm-✅-closed-2026-06-02-close-by-completion) / [AB](#ab-ds-0-pass0_assistant-在大上下文--慢-llm-下-timeout--fallback-✅-closed-2026-06-01-close-by-completion) 同源（deepseek 顶替更强模型 / 弱模型暴露 pipeline 脆弱点）；与 [AC]（reasoning 服从性）、[AD]（证据绑定）正交
- **剩余 OPEN 中的"第 2 类(ii) 强模型端到端验证"**：见 [Z](#z-fund_mgr-跨模型opus-vs-deepseek对照验证-✅-closed-2026-06-02-close-by-completion)（fund_mgr 跨模型对照）；现状全部行为数据来自 deepseek 弱替身。
- **Close 方式**: close-by-completion（2026-06-02）—— 剩余未审计点（debate/vote）已设防
  - `make_debate_node`（主路径 + rework 路径两处）：`DebateTurn.model_validate` 包 try/except，畸形输出降级为 placeholder turn（保 side/stage/round），Phase 2 继续
  - `make_vote_node`：`Vote.model_validate` 包 try/except，畸形输出降级为 DATA_INSUFFICIENT vote，Phase 3 tally 仍正确聚合
  - ds_researcher / ds_debate：核查确认**早已 robust**（[pass0_parallel.py](../../src/committee/agents/pass0_parallel.py) 全程 try/except + fallback None），无需新增
  - **未做（by-design 保留，非遗漏）**: 修法方向剩余项 2「fund_mgr head parse 失败降级而非致命」—— 维持现状 by-design 致命（无决策头=致命，与 AE.3 受控 ValueError 一致）；如未来生产暴露 head 畸形输出崩 run，再单开条目
  - 1864 tests passed, 0 failed
  - **by-design 保留**: fund_mgr head parse 失败仍 re-raise 受控错误（"无决策头=致命"是设计，非 bug；修法方向 #2 评估结论 = 维持致命）
  - 1864 tests passed

### AF. fund_mgr 输入重构 — DS-0 digest 为主、raw 为 fallback（2026-05-29 拍板）✅ CLOSED 2026-06-02 (close-by-completion)

- **强度**: 🟡（不阻塞，但 DS-0 定位长期不立 = 三大新功能投入打折 + 自搜审计盲区）
- **背景 / 已验证现状（2026-05-29 代码 reading）**：fund_mgr 的 `user_base` 同时塞了**原始全量**（8 份分析师报告 `reports_block` + 完整辩论 `debate_block` + 逐票 `votes_block`）**和** DS-0 digest，但：
  - DS-0 三样产出里 fund_mgr **只消费 `facts_inventory`**（经 `build_facts_guidance` 注入）；
  - **`debate_summary` 没注入**（fund_mgr 读原始辩论全文）；
  - **`vote_distribution` 没注入**（fund_mgr 自己从原始 votes 重算 `tally`，连 OBEY-5 用的也是重算的那份）。
  - → 即"DS-0 做了三样、fund_mgr 只吃一样、另两样白产 + 还重复读原始全量"。digest 的减负本意完全没兑现。
- **目标态（用户拍板）**：fund_mgr 输入 = 主题 + **整份 DS-0 digest**（facts_inventory + debate_summary + vote_distribution）+ OBEY-3 signals + pre-gate findings + 自搜；**`reports_block` / `debate_block` 只在 fallback（pass0=None）或 fund_mgr 用工具深钻某点时才拉**。
- **修法方向**:
  1. 砍掉 raw 全量无条件注入，改用 DS-0 digest 三件套；
  2. fund_mgr/OBEY-5 改用 DS-0 的 `vote_distribution`，消除重复计票；
  3. 原始报告/辩论降为按需（fallback / deep-dive tool）。
- **前置依赖 / 风险**：这会让 **DS-0 完全 load-bearing** —— 一旦 DS-0 超时/产空（[AB](#ab-ds-0-pass0_assistant-在大上下文--慢-llm-下-timeout--fallback-✅-closed-2026-06-01-close-by-completion)），fund_mgr 从"有原始全量兜底"变成"几乎无输入"。**前提：AB（DS-0 稳定性）先解决 + fallback 路径必须很硬**。
- **触发时机**: AB 解决后；或与 [AC]/[AD] 重构合并处理时
- **不做的后果**: DS-0 投入（facts/debate/vote 三件套有两件白产）+ context 不减反增 + 自搜侧门（见 [AD] b）长期并存
- **进入时点**: 2026-05-29（Phase 4 设计讨论，代码 reading 确认 digest 半数被绕过）
- **归类**: 与 [AB](#ab-ds-0-pass0_assistant-在大上下文--慢-llm-下-timeout--fallback-✅-closed-2026-06-01-close-by-completion)（DS-0 稳定性，前置）紧耦合；与 [AD]（自搜审计）相关
- **Close 方式**: close-by-completion（2026-06-02，AB 前置已解）—— 核心"白产"问题已解，**reports_block raw 注入保留为 deferred 子项**
  - `make_decision_node`：`pass0_result.debate_summary` 存在 → `debate_block` 用 DS-0 摘要（bull/bear core thesis + progression_notes + key_disagreements），否则 fallback raw `_format_debate`（修法方向 #1/#3 的 debate 侧）
  - `pass0_result.vote_distribution` 存在 → `votes_block` + `tally` 用 DS-0 计票，否则 fallback raw 重算（修法方向 #2，消除重复计票）
  - **DS-0 三样产出现已全部消费**：facts_inventory（既有 `build_facts_guidance`）+ debate_summary（本次）+ vote_distribution（本次）→ "做三样吃一样、两样白产" 问题 = 解决
  - **⚠️ deferred 子项**：`reports_block`（8 份 analyst 原始报告）仍**无条件 raw 注入**——未降为按需。facts_inventory 是其 digest 但 raw 报告未撤（fund_mgr 写 thesis 可能引用具体分析师细节，撤除是更大行为变更，需独立 e2e 验证）。目标态"reports_block 只在 fallback 拉"的 reports 侧未完成 → 见 [AF-residual](#af-residual-reports_block-raw-注入降为按需待评估)
  - DS-0 现已 **load-bearing**（前置 AB 已解，fallback 路径 = pass0=None → raw 全量，已验证）
  - 1864 tests passed

### AF-residual. reports_block raw 注入降为按需（待评估）

- **强度**: 🟢（AF 主体已 close；这是其 deferred 尾巴，纯 context 减负，不阻塞正确性）
- **背景**: [AF](#af-fund_mgr-输入重构--ds-0-digest-为主raw-为-fallback2026-05-29-拍板✅-closed-2026-06-02-close-by-completion) close 时，debate/vote 已切 DS-0 digest，但 `make_decision_node` 的 `reports_block`（8 份 analyst 原始报告全文）仍无条件注入 `user_base`。目标态要求"reports 只在 fallback / deep-dive tool 时拉"，reports 侧未做。
- **为何 defer**: 撤 raw 报告 = fund_mgr 失去引用具体分析师细节（具体数字 / 论据原文）的能力，靠 facts_inventory + cross_role_alignment digest 是否够支撑 thesis 写作质量，需 e2e 对照验证（digest-only vs raw+digest 的 thesis 质量 / {ref:fX} 覆盖率）。比 debate/vote 切换风险高。
- **修法方向**: ① reports_block 改 fallback-only（pass0=None 才注入）+ 给 fund_mgr 一个 deep-dive tool 按需拉某 role 原文；② 或保留但裁剪（只注入 headline + key_points，砍 raw 长文）。
- **触发时机**: ~~与 [AG]（cache 优化）/ [AH]（token 量测）合并~~〔**⚠️ 2026-08-11 改判据**：AG 与 AH **均已 close**，原触发挂在两条已关条目上 = 判据挂死信号（[§4.1](#41-新增-backlog-条目) 禁止形态）。**新触发条件（事件型）= 下次动 `make_decision_node` 的 `user_base` 组装时**（[base.py:3259](../../src/committee/agents/base.py)）—— 最可能的场合是 [S3 §6.1 COST-FM-PREFIX](../roadmap/S3.md) 那次前缀对齐，届时必然要通读并重排 `user_base` 的构成，正好一并量 reports_block 占比、定 ROI。量尺现成（[token_usage.py](../../src/committee/token_usage.py) per-call 明细，2026-08-11 已修好缓存字段）〕
- **不做的后果**: fund_mgr context 仍含 raw 报告全量（debate/vote 已减，reports 未减）；context 减负只完成一半
- **进入时点**: 2026-06-02（AF close 时拆出）
- **归类**: [AF] 尾巴；与 [AG]/[AH]（context/成本）同主题

### AG. 全链路 KV cache / prompt caching 优化（2026-05-29 记录）

> **✅ CLOSED 2026-08-06→2026-08-11（close-by-completion + 剥离·保留位置）**：本条三条修法方向已全部有归宿，无剩余待办。
>
> | 原修法方向 | 结局 |
> |---|---|
> | ① Anthropic 打 `cache_control` 标记 | ✅ **已做**（`82011fb`）。**默认关**（用户 2026-08-11 裁决）—— 单次孤立 run 里净亏约 $0.021（写入加价 25%、无人读），跑批量 / 回归时一行 env 打开即赚。实测命中时单次 $0.0835→$0.0093（**降 89%**） |
> | ② DeepSeek / OpenAI 自动前缀缓存（把可缓存内容前置） | ❌ **实测无效，放弃**（非暂缓）。A/B 实验：八 analyst 共用段前置后，各角色**首调命中量两臂全为 0、一个不差**——因为八个 analyst 是**并行**发出的，缓存要生效必须有先后。证据 [ag-prompt-order-ab](../observations/ag-prompt-order-ab/EVIDENCE.md) |
> | ③ 跨 role 复用（统一前缀位置） | 同 ②，被同一实验否掉 |
>
> **计划外产出**：验尺子（[AG.1](../observations/ag-cache-meter-probe/EVIDENCE.md)）查出缓存**写入量恒记 0** 的真缺陷
> （Anthropic 真值被 langchain 拆进 `ephemeral_*` 字段）→ 成本少算 20% + 「标记生没生效」判据永不会响。已修（`bd4445d`）+ 靶测 + 沉淀进 [坑表 §3.2 形态⑥](workflow/09-known-pitfalls.md)。
>
> **剩余价值已剥离立项，不留在 backlog**：真正的大头（对齐 fund_mgr 两次调用的开头指令，让共享正文吃到缓存，
> 预估省 11% 账单 = 本条标记开关的 7 倍）→ **[S3 §6.1 COST-FM-PREFIX](../roadmap/S3.md)**（🟢 优先级较后·用户 2026-08-11 裁决）。
> 之所以不留 backlog：它要动决策环节的调用结构，属 S3 级工程，不是「等条件触发的延后小事」。
>
> ↓ 以下为立账期记录（point-in-time，不改）↓

- **强度**: 🟡（不阻塞正确性；纯成本 / 延迟优化，但生产用 opus 时 API 账单 + 响应时延显著）
- **背景**: 单次 query 走 ~25+ 次 LLM 调用（8 analyst + 6 debate + 10 vote + ds_researcher + ds_debate + fund_mgr 多段），其中大量调用**共享巨大前缀**却每次重发：
  - **静态系统 prompt**（各 role 的 SYSTEM_PROMPTS / DECISION_PROMPT）—— 完全不变，可缓存。
  - **common_context 数据块**（含水印）—— 8 个 analyst **完全相同**，每次重发。
  - **fund_mgr `head_user`**（实测 ~30k 字符）—— 在 outline / head / 5 段 section 扩写间**高度重复**（最大单点复用机会）。
  - debate 6 轮 / vote 10 票各自共享上下文。
- **修法方向**:
  1. **Anthropic 路径**：用 `cache_control` 标记静态前缀（system + common_context + reports）为可缓存断点（5 分钟 TTL）。
  2. **DeepSeek / OpenAI 路径**：自动前缀缓存——**保证可缓存内容放在 prompt 最前、变动内容后置**（prompt 结构调整即可命中，无需 API 改动）。
  3. **跨 role 复用**：把 common_context / 静态 prompt 提到所有调用的统一前缀位置，最大化前缀命中。
  - 注意：缓存是 **per-provider / per-model** 的（见 per-role 模型表）——各 provider 策略不同，需分别处理。
- **与其他条目的关系**: 与 [AF](#af-fund_mgr-输入重构--ds-0-digest-为主raw-为-fallback2026-05-29-拍板✅-closed-2026-06-02-close-by-completion)（砍 context 减负）**互补**——AF 减少 token 量、AG 复用 token 前缀，两者叠加才是完整的成本优化。
- **触发时机**: 切到生产 opus / 成本或延迟成为约束时；或 [Z](#z-fund_mgr-跨模型opus-vs-deepseek对照验证-✅-closed-2026-06-02-close-by-completion) 跨模型验证暴露真实成本时
- **不做的后果**: 每次 query 重复烧大前缀 token；opus 生产成本 + 时延偏高（弱模型测试时不明显，掩盖了真实账单）
- **进入时点**: 2026-05-29（Phase 4 讨论顺带记录）
- **归类**: 性能 / 成本优化；与 [AF] 互补、与 [AB] 同属"context 体量"主题

### AH. LLM token 用量追踪——per-call 明细 + per-run 总量（2026-06-02 记录）

> **✅ DONE（2026-07-24·verify-before-acting close·下方为立账期记录·point-in-time·不改）**：本条**早已实现**（`84a69d1`/#145 后），条目未回填 close 致 stale。实现 = [`token_usage.py`](../../src/committee/token_usage.py)（`TokenTracker`/`TokenRecord`/per-call `record`/by_model+by_tag 双汇总/`estimate_cost` 成本估算/`TokenUsageCallback` 焊进 `_llm` per-tag/resume `merge_from`）+ 接线（graph result `token_usage`·checkpoint `_token_usage`·cli `_print_token_table`）+ 测试 23 绿（[`test_token_usage.py`](../../tests/test_token_usage.py)）。**覆盖并超出**下方方案 A（per-call log）+ 方案 B（per-model 汇总）+ 产出（写 result/archive）。原设想的"AG/AF 前置量尺"已就位（AG/AF 触发时可直接用）。

- **强度**: 🟡（不阻塞正确性；为后续流程优化 / 成本控制提供数据基础）
- **背景**: 当前 pipeline 无任何 token 用量记录。单次 query 走 ~25+ 次 LLM 调用，但不知道哪个阶段 / 哪个 role 消耗最多。没有数据就无法有效优化（与 [AG](#ag-全链路-kv-cache--prompt-caching-优化2026-05-29-记录) cache 优化互补——AG 是减法，AH 是量尺）。
- **修法方向**:
  1. **方案 B（总量累加）**: 在 `run_committee()` 入口创建 `UsageMetadataCallbackHandler()`，传给 `graph.invoke(state, config={"callbacks": [tracker]})`。跑完后 `tracker.usage_metadata` 给出 `{model_name: {input_tokens, output_tokens, total_tokens}}` 按模型汇总。**零改调用方代码**。
  2. **方案 A（关键节点明细）**: 在 `_invoke_json` / `_invoke_with_continuation` 等核心调用点读 `resp.usage_metadata`，log 到 `committee.token_usage` logger（INFO 级）。格式：`role=macro model=deepseek-chat input=1234 output=567 total=1801`。
  3. **产出**: 每次 run 的 token 明细（per-call log）+ 汇总（per-model summary），写入 e2e JSON / archive。
- **技术可行性**: `langchain-core>=0.3.49` 自带 `UsageMetadataCallbackHandler`，当前版本 1.2.29 ✅。`AIMessage.usage_metadata` 三个 provider（OpenAI/DeepSeek、Anthropic、Gemini）都支持。
- **与其他条目的关系**: 是 [AG（cache 优化）](#ag-全链路-kv-cache--prompt-caching-优化2026-05-29-记录) 和 [AF（context 减负）](#af-fund_mgr-输入重构--ds-0-digest-为主raw-为-fallback2026-05-29-拍板✅-closed-2026-06-02-close-by-completion) 的**前置量测工具**——先量才知道哪里值得优化。
- **触发时机**: 下次做流程优化（AG / AF）时一起上；或单独先做（工作量小，1 goal 即可）
- **不做的后果**: AG/AF 优化效果无法量化；成本控制无基线
- **进入时点**: 2026-06-02（AD.8 e2e 验收时识别）
- **归类**: 可观测性 / 成本优化基础设施；[AG] 前置

---

### AI. Audit pipeline 否定半边失效 — confirmed_mismatch/failed 死态 + audit_status 零 enforce（2026-06-02 S2.3-gate agent-review）

> **✅ 已收口（2026-07-14·MASK.E1 + AUDIT-3CHECK CANCELLED）** — 本条的"否定半边"病根不再追求：① **MASK.E1** 已把 `audit_confirmed_mismatch`/`audit_failed` 两个死枚举**彻底删除**（从未进任何归档·无 compat 需要）·audit_status 收成 4 活跃值（`audit_passed`/`audit_notsure`/`audit_notpassed`〔★永久占位·无生产者〕/`not_audited`）+ 3 legacy 只读；② **AUDIT-3CHECK 已 CANCELLED**（2026-07-14 用户拍·见本文件 `AUDIT-3CHECK` 条目 + [audit-positioning.md 顶部 banner](../pipeline/decision/audit-positioning.md)）——原打算复活 mismatch 死枚举去做"否定半边 enforcement"的三检查取消实现·audit **永久停在"来源存在性半项"**（数字不核 → 无从判"不过"）；③ 安全底线改由 fund_mgr 打码修复 **Path B（输出侧验章门）** 兜"错数字不到读者"·不再依赖 audit 的否定半边。∴ 本条议题**收口**（非"待 S3 实现"）。下方为 2026-06-02 立账期记录（point-in-time·不改）。↓

- **强度**: 🔴（不崩 run，但证据绑定的"否定"半边逻辑断链；§5.5 "引用 mismatch<1%" 为 vacuous pass）
- **背景**: S2.3-gate Agent 现状审视（[agent-review-s2.3 A1/A3](agent-review-s2.3.md)）发现：
  1. **A1 死态**：`AUDIT_STATUS` 含 7 态（含 `audit_confirmed_mismatch`/`audit_failed`），但确定性 `_audit_fact_against_context`（[audit_node.py:35-64](../../src/committee/agents/audit_node.py)）**仅 return 4 态**（skipped/inconclusive/passed/partial_support）→ mismatch/failed **永不产出**。强模型 e2e 实证分布印证（`passed×3/inconclusive×42/skipped×2`）。
  2. **连锁死路径**：(a) prompt "❌ 不可引用" 分支（[prompts.py:213-217](../../src/committee/prompts/decision/prompts.py)）死指令；(b) AD.7 窄硬地板经 DS-0 fact 的 unverified 触发（[risk_gate.py:271-273](../../src/committee/agents/risk_gate.py)）永不成立（只剩 web ref unverified 一条活路）；(c) §5.5 "thesis 引用 confirmed_mismatch < 1%" 自动 0%（从不检测 ≠ 检测后为 0）。
  3. **A3 零 enforce**：即便 A1 修了，audit_status 对 thesis 引用当前**纯 prompt 约束**，EVID-1（[base.py:1995](../../src/committee/agents/base.py)）只剥 hallucinated（fid 不在 valid 集），不剥"in-inventory 但 audit_failed"的 fact。
- **修法方向**:
  1. audit_node 增 "watermark 存在但值矛盾" 检测 → 产 `audit_confirmed_mismatch`（语义/数值比对，可能需轻量 LLM 或确定性数值容差）
  2. EVID-1 strip 集合并入 `audit_status ∈ {confirmed_mismatch, failed}` 的 fid（依赖 #1）
  3. **或**：若判定值矛盾检测属 S3 语义比对范畴 → 文档显式标记这两态为 S3 预留，§5.5 指标改口径（去掉 vacuous 项或标注"待 S3 检测能力"）
- **触发时机**: S3 证据绑定 / audit 能力升级启动时（最高优先，S2.3-gate CONDITIONAL PASS 的首要 caveat）
- **不做的后果**: 证据绑定只有"肯定"半边（passed/partial），"否定"半边（mismatch/failed）永远沉默；指标层显示完美（0% mismatch）但实为从不检测，掩盖真实数据质量问题
- **进入时点**: 2026-06-02（S2.3-gate agent-review-s2.3，4 subagent 独立审视 + 强模型 e2e 实证）
- **证据**: [agent-review-s2.3.md A1/A3](agent-review-s2.3.md) + [e2e-notimeout audit 分布](../observations/e2e-runs/e2e-notimeout-20260602-131755.json)
- **归类**: 与 [AD](#ad-证据绑定--audit-pipeline-升级-firn-inspired-✅-closed-2026-06-02-close-by-completion) 同源（证据绑定完整性），AD 修了"剥 hallucinated + web 置信度"肯定半边，AI 是遗留的否定半边

### AJ. DS-0 部分 LLM 产出无实际效用 — cross_role_alignment 死输出 + watermark 检查空中楼阁（2026-06-02 S2.3-gate agent-review）✅ CLOSED 2026-07-24 (close-by-completion·保留位置)

- **✅ DONE（2026-07-24·[#206](https://github.com/JunoChenZt/subagent-for-investment/pull/206) squash 合 main `36578b4`·CI 三 job 全绿·用户拍合）**：活1+活2 均删净（净删 163 行 / 增 59·10 代码测试文件）。DoD：全套件 **2716 passed**（`STRICT_PROTOCOL_META=1`）+ 新增 archive-replay 回归测试（老 checkpoint 带 cross_role_alignment/旧死 flag → `extra=ignore` 不崩）+ **真 deepseek-v4-pro fresh smoke**（瘦身 prompt 下产 6 facts·输出无 cross_role_alignment key·无残留死 flag）。legacy `PASS0_SYSTEM_PROMPT`/`pass0_node`（未接线 dead）刻意留。**衍生**：AW（数字来源核对前置 fund_mgr 议题）+ AX（`as_of` 前存脆性 observe·fresh smoke 抓·非 AJ 引入）。retro [AJ_2026-07-24](../retro/S2/AJ_2026-07-24.md)。↓ 下方定案记录不改 ↓
- **🔵 定案（2026-07-24·Explore 一手代码复核 + 设计讨论·用户拍「活1活2 都删」）**：两处死输出经一手复核成立——`cross_role_alignment`（+3 子字段）全 `src/` **零 consumer**（fund_mgr/audit/trace 都不读）；watermark 核对**无 [REF#] 原始数据**=物理不可行，产出 flag 仅进 sanity check #8 软计数、`exec_floor.py:18` 明确不喂决策。两处 backlog 均给「接入/删除」二选一，**均定删**：
  - **活1 `cross_role_alignment` → 删（不接入）**：概念本身弱——与 `debate_summary`/`vote_distribution` 高度重复（辩论结构=分歧、投票分布=共识，已表达）+ "共识"当信号=群体思维放大器（少数派分歧观点往往更值钱）+ 是"摘要的摘要"=LLM 印象伪装成权威。同已 CLOSED 的 AQ(`raw_confidence`)/R4(sentiment) 死字段属。`data_gaps` 稍有独立价值但结构化降级/来源类型信号更可靠。
  - **活2 watermark 核对 → 删假壳（不注入 refs）**：目标（抓数字搬运错）重要，但**此实现是假的**（无对照物·LLM 猜）；真核已在下游 `exec_floor` check①（确定性·代码门控·在 fund_mgr 拍板前跑）→ 删假壳、能力不丢，注释委托下游。**不注入 refs**——那等于让 LLM 做数字核对，违「承重数字走结构化字段+代码门控」铁律。
  - **子目标**：AJ-1 删 `cross_role_alignment`（`schemas/pass0.py` 类+字段 + `pass0_prompt.py:43-53,110-113` + `pass0_parallel.py:242,262` 写入 + 测试）· AJ-2 删 watermark 核对（`pass0_prompt.py:92-96` prompt + `watermark_claim_mismatch` flag 产出 + `pass0_validator.py:82-91` sanity#8 消费·加注释委托下游）· AJ-3 e2e（archive replay 靠 Pydantic `extra=ignore` 不崩 + 一段 fresh run 不 regress）。
  - **不捆 AF-residual**（raw reports 撤除需 digest-only vs raw+digest e2e 对照·体量更大·独立走）。
  - **衍生新条目 AW**（本文件 §1）：记用户戳中的真缺口——"数字**来源**（provenance）核对能否一部分前置到 fund_mgr 拍板前"（活2 删的是假壳、不解此缺口·此缺口另评）。
  - **状态**：拆解已定·**待 greenlight 开工**（触 LLM 输出面·按 `/goal` workflow 走·AJ 仍算 1 活跃、未 close）。
- **强度**: 🟡（不阻塞；LLM 算力白烧 + watermark 一致性检查无 code 兜底）
- **背景**: S2.3-gate Agent 现状审视（[agent-review-s2.3 A2/A4](agent-review-s2.3.md)）发现 DS-researcher 两处"产出但无效用"：
  1. **A2 死输出**：`cross_role_alignment`（consensus_claims/divergent_claims/data_gaps）由 DS-researcher LLM 产出存入 `Pass0Result`（[pass0_parallel.py:262](../../src/committee/agents/pass0_parallel.py)），但全仓 grep **无 consumer**（fund_mgr 只读 debate_summary/vote_distribution/facts_inventory，audit_node 只读 facts_inventory）。
  2. **A4 watermark 空中楼阁**：prompt 要求 LLM 核对 claim 与 watermark 原始数据是否矛盾（[pass0_prompt.py:78-83](../../src/committee/prompts/pass0_prompt.py)），但 DS-researcher 输入只有 reports、**无 [REF#] 原始数据**（[pass0_parallel.py:70-80](../../src/committee/agents/pass0_parallel.py)）→ 物理上无法核对，`watermark_claim_mismatch` flag 全凭 LLM 自觉，sanity check #8 只统计 flag 比例不独立验证。真核对在下游 audit_node 用 common_context 做。
- **修法方向**:
  1. cross_role_alignment：接入 fund_mgr（消费 consensus/divergent 信号）**或**从 ResearcherBriefing schema + prompt 删除并精简
  2. watermark 检查：给 DS-researcher 注入 common_context refs（让核对有据）**或** prompt 删除该核对要求（明确委托 audit_node）
- **触发时机**: DS-0 prompt/职责重审时；或与 [AF](#af-fund_mgr-输入重构--ds-0-digest-为主raw-为-fallback2026-05-29-拍板✅-closed-2026-06-02-close-by-completion)（已 close）后续 DS-0 定位工作合并
- **不做的后果**: 每 run DS-researcher 花 token 产 cross_role_alignment + watermark flag，两者均无下游效用；DS-0 职责边界模糊（"整理"vs"核对"未厘清）
- **进入时点**: 2026-06-02（S2.3-gate agent-review-s2.3）
- **证据**: [agent-review-s2.3.md A2/A4](agent-review-s2.3.md)
- **归类**: 与 R4 sentiment 死字段同模式（schema 一等公民/prompt 强引导但零消费）→ O-S2.3-02 N=2，下次再现升 should_update
- **同族数据点（2026-06-05 QC-R1 G6 合并记录）**: 中际旭创 e2e seg1 实测 `references=0`——
  tushare 价格 payload 自带 `as_of=2026-06-04` 但 `generate_watermarks` 未产出 Reference。
  **非 facts_inventory 通路的数据出处（tushare 价格、未来 web_search 结果）在 EVID/watermark
  覆盖之外** = 与本条 A4「watermark 空中楼阁」+ web_search 无 REF 同族（数据有出处但无 REF
  watermark）。合并记此处避免散落。修法时一并审：watermark 覆盖应含结构化源 payload（tushare/
  fred/rss）的 as_of，而非仅 facts_inventory。

### AW. 数字来源（provenance）核对的放置 — 一部分能否前置到 fund_mgr 拍板前 ✅ CLOSED 2026-08-05 (close-by-completion·保留位置)

> ## ✅ **CLOSED（2026-08-05·用户批准全景对账处置表）**
>
> **本条的命题已被实现覆盖**：[#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 的
> **判定 3（出处有效性）+ 判定 4（核值 log-only）** 就是「**核来源不核值 · 前置到 fund_mgr 推理之前**」
> —— 它们跑在 `audit_node`（`ds_merge` 后 / `fund_manager` 前），正是本条原文要求的放置点。
>
> **本条写死的前置（Chesterton fence）也已履行**：「动手前先读当年为什么砍 AUDIT-3CHECK」——
> 2026-08-05 全景对账已读完一手记录并写成时间线（07-03 设计 → 07-06 量化 → 07-14 砍 → 07-15 输出侧
> 收窄 → 07-16 AS 降级 → 08-04 实证 → 08-05 重实现），结论：**当年砍它的理由「输出侧兜着」在次日
> 就被输出侧自己的收窄推翻**，故重做不是推翻当年取舍、是补上那次交接的断点。
>
> **后续归属**：判定 4 要不要转正 = [number-provenance-endgame](number-provenance-endgame.md) **判据 D2**（观察期后强制二选一）。
> **本条不再单独追踪。**
>
> ↓ 下方为 2026-07-24 立账期记录（point-in-time·不改）↓

- **强度**: 🟡（设计议题·非阻塞；关乎 fund_mgr 拍板前的数据正确性防线完整度）
- **用户命题（2026-07-24·AJ 活2 删除讨论 refine）**：**不一定核数字"值"**（20% vs 15% 的精确核对 = 更大工程·等于重开已砍的 AUDIT-3CHECK 方向），而是**核数字"来源"（provenance）**——一个承重数字有没有真实出处 / 挂对了源——**其中一部分能否前置到 fund_mgr 推理之前**，而非只在下游 / 输出侧兜。
- **现状防线盘点（2026-07-24 一手复核）**：fund_mgr 拍板前的确定性数据正确性检查稀薄——
  1. **审计（`audit_node`·Phase 3.7·在 fund_mgr 前）**：只核"来源引用 REF# 是否存在于 `common_context`"（存在性半项）；**AUDIT-3CHECK 已彻底砍**（2026-07-14·audit 永停存在性半项·不再追负态 / 数字矛盾）。
  2. **`exec_floor` check①（决策节点步骤 3″·在 LLM 拍板前跑）**：确定性数字对账，但**只抓数量级错**（宁漏勿冤·高精度低召回）+ 处置是**拦输出**（切价位 / 降 HOLD）**非纠输入**（错数字不从 fund_mgr 输入移除）→ 非数量级偏差静默放过。
  3. **活2（DS-0 watermark·已随 [AJ](#aj-ds-0-部分-llm-产出无实际效用--cross_role_alignment-死输出--watermark-检查空中楼阁2026-06-02-s23-gate-agent-review✅-closed-2026-07-24-close-by-completion保留位置) 删）**：假核·不作数。
  → 缺一道"聚焦**来源真实性**、覆盖非数量级、前置到 fund_mgr 前"的确定性防线。
- **须先做（Chesterton fence·守 [[feedback_read_boundary_intent_before_expanding]] + R5）**：动手前先读**当年为什么砍 AUDIT-3CHECK**（MASK.E1 / AUDIT-INTENT / [audit 定位定稿](../governance/backlog.md) 相关记录）——那是刻意的"宁漏勿冤·只拦灾难"取舍·**非疏忽**；重开来源 / 数字核对 = 质疑该取舍·须先证其边界意图，不得把推断当应然直接开修。
- **关联**：AO（provenance 接链路·`web_provenance` 外源册 / audit_passed 分流）/ 层② check①（`exec_floor`）/ `audit_node` 定位 / AJ（同 DS-0 职责簇）。
- **触发时机**：DS-0 职责重审 / 审计定位重审时；或用户想认真评估 fund_mgr 前上游正确性防线时。
- **进入时点**: 2026-07-24（AJ 活2 删除讨论·用户 refine 为 provenance 前置命题）
- **预估工作量**: 中-大（须先厘清 AUDIT-3CHECK 边界意图 + 设计确定性来源核对机制 + 放置点 + e2e）；**当前仅登记议题·不预设方案**

### AX. DS-0 `as_of: str` 不收 LLM `null` → ds_researcher node fallback 脆性（2026-07-24 AJ fresh smoke surface）

> ## ✅ **CLOSED（2026-08-03·close-by-completion）** — 下方全部正文为 point-in-time 记录（立账时的 observe 口径），**保留不改**
>
> **已合 main**：[#220](https://github.com/JunoChenZt/subagent-for-investment/pull/220) squash `381824a`（2026-07-31）。
> **根因亦已消除**：病根「搜索代理丢 `publishedDate` → web 来源 fact 无日期」随 **Serper 切换**（2026-07-31）+ Worker `normalizeDate` 解决——带日期率 0%→**62%**，
> 即模型此后对 web 来源 fact 大多能拿到真日期、不再被迫吐 null。校验侧（`AsOfLoose`）与来源侧（Serper）**两头都堵上了**。
> 〔**⚠️ 08-03 R7 更正**：本 banner 原写「分支 `auto/websearch-relevance`」（见下方倒数第二行）= **stale** —— 该分支远程已不存在，代码在 main。〕
>
> **触发条件已满足**（2026-07-30 全链回归 e2e 数据点2：触发率 14–19%·两次尝试全灭·`facts_inventory` 全空），
> 用户同日改判「修」（此前 07-30 早些时候的「暂不修·继续跑批」裁决已被本次覆盖）。
>
> **落地** = 修法候选②：[pass0.py](../../src/committee/schemas/pass0.py) 加 `AsOfLoose`
> （`BeforeValidator` 把 `None` → `""`），`FactInventoryItem.as_of` 改用它。
> **边界：只收 null，不做格式归一** —— 本字段是宽松 `str`（`"Q4 2024"` 这类今天就收），
> 套 `sanitize_as_of` 会改写/丢弃现有取值 = 行为变更，超出本 defect 的修法。
> 分支 `auto/websearch-relevance`（与 DEFECT-WEBSEARCH-RELEVANCE 同 PR·两者是同一转发层的两个毛病）。

- **强度**: 🟢（observe·defer-until-data·单数据点·非阻塞）
- **背景**: 2026-07-24 AJ 节点收口跑**真 deepseek-v4-pro fresh smoke**（[PR #206](https://github.com/JunoChenZt/subagent-for-investment/pull/206)）时抓到：模型对**无日期的 fact** 会吐 `"as_of": null`，但 schema `FactInventoryItem.as_of: str = Field(default="")`（[pass0.py](../../src/committee/schemas/pass0.py)）**只收 str、不收 null** → `ResearcherBriefing.model_validate` 抛 `string_type` 错 → `ds_researcher_node` retry 1 次仍失败 → **fallback `None`**（→ ds_merge 走 raw 全量兜底·pass0 digest 失效）。实测 6 facts 全 as_of=null。
- **非 AJ 引入**：`as_of` 字段定义 + prompt 指引 AJ **一字未动**（grep 证·AJ 只删 cross_role_alignment + watermark）。属独立前存脆性·借 AJ fresh smoke 暴露。
- **触发条件（falsifiable·升 should_update 治理）**: 真实 production run 的 observation 显示 `as_of=null` 导致 `ds_researcher` fallback 触发率高（如 ≥20%·≥1 周窗）→ 意味 pass0 digest 常降级 raw fallback（而 pass0 是 load-bearing·见 §AF）→ 值得修。
- **反向条件（close 不做）**: 若真实 run 中模型对有日期 fact 正常填 string as_of、null 仅偶发不致 fallback → 脆性不构成实际问题。
- **修法候选（不预设·届时定）**: ① `as_of` 改 `str | None`（最小·但下游读 as_of 处需核 None 容忍）；② 加 `null→""` 归一 validator（镜像 T4/T6 `sanitize_as_of` 先例·verdict-neutral·[[known-pitfalls §3.2]] 宽松 str→严格字段消费点 sanitize 同族）。
- **为什么 observe 不当场治**: 单数据点（[[feedback_observation_counter_hygiene]]·observe-first）；且此 smoke 是人造 3-report 输入·真实 run 的 as_of=null 率未知（可能真实 run 分析师报告多带日期 → null 率低）。**先攒真实 run 数据再定**。
- **进入时点**: 2026-07-24（AJ fresh smoke·PR #206）
- **预估工作量**: 小（as_of 归一·若治）

### AK. 本地证券名录（ticker 校验 + 名称→代码兜底）

> ## ✅ **DONE（2026-07-24·close-by-completion）** — 下方全部正文为 point-in-time 记录，**保留不改**
>
> **走完 pre-node 设计边界审查**（用户拍 4 问：覆盖 A股+港股+美股 / 名录覆盖 LLM 码 + 全程留痕 /
> 名录拿不到时静默降级回现状 / ①+② 一次做完）后一次做完。
>
> **落地**：新包 [`security_registry`](../../src/committee/security_registry/) —— 三市场名录
> （CN `stock_basic` 5531 / HK `hk_basic` 2783 / US NASDAQ 符号目录 13537）+ 对账决策表
> [`reconcile.py`](../../src/committee/security_registry/reconcile.py) + 接入
> [`classify()`](../../src/committee/query_class/classifier.py)（**名录排在 regex 与 web_search 之前**，
> 兑现本条下方声明的优先级链）+ CLI `registry refresh/status` + 确认闸回显公司名。
>
> **PR #211 review 后追加（2026-07-24·`auto/AK` 尾部·下段为最终状态）**：
> - **每日自动刷新（用户要求·凌晨 2 点）**：长驻进程（server/MCP）启动挂
>   [`daily_refresh_loop`](../../src/committee/security_registry/service.py)——每天固定时刻全量刷新
>   （默认 `REFRESH_HOUR=2`·env `COMMITTEE_REGISTRY_REFRESH_HOUR` 可调·`COMMITTEE_REGISTRY_AUTO_REFRESH=0`
>   可关）。**生产容器已设 `TZ=Asia/Shanghai`**（[Dockerfile](../../Dockerfile)·2026-07-24 用户裁决）→
>   默认部署下 `2` 就是**北京凌晨 2 点**，开箱即对。时区爆炸半径已审：只影响本地时间用法（刷新时刻 /
>   is_fresh / as_of 陈旧度 / 日志），**不影响** archive/auth/email 的持久化时间戳（全 UTC-aware）。
>   非 Docker / 未设 TZ 的环境里 `2` = 该环境本地 02:00（须自设 TZ 或把值设 18）。**非 cloud routine**
>   （应用进程内后台任务·与「Claude 调远程定时任务」红线无关）。
> - **启动预热**（治 review 🟠 冷启动）：server/MCP 启动 + CLI 跑图前调
>   [`prewarm`](../../src/committee/security_registry/service.py)（只补完全缺失的市场·受 `LAZY_FETCH_ENABLED`
>   门控）→ 首个请求不再落 lazy bootstrap 的 8s（原会压回 Phase 0a 关键路径）。单进程 uvicorn
>   （Dockerfile/serve 均无 `--workers`）→ 单调度器无重复。
> - **review 三处 trivial 清理已带**：`.gitignore` 去重（`*.db-wal`/`*.db-shm`）/ `ClassificationResult`
>   `__post_init__` docstring 补 `registry` / `covers_market` O(N)→O(1)（构建期预存 `frozenset`）。
> - **review 🟡 成功路径 override**：已披露的取舍·**保留不改**（用户设计阶段已拍板）。
> **剩余项 #2（trace 契约 smoke）一并做完**：[`test_trace_state_contract.py`](../../tests/test_trace_state_contract.py)
> 四条契约，mutation 验证能抓住 2026-06-05 `ticker=-` 事故的逐字复现写法。
>
> **两个洞都用真实数据坐实堵上了**（[evidence](../observations/ak-e2e-20260724/EVIDENCE.md)）：
> - **名称兜底**：e2e A/B —— 同样强制 classify 超时，名录 ON → `300308.SZ` + tushare 真实价
>   1046.51 CNY；名录 OFF → 「中际旭创现在适合买么」这个**个股**问题被降级成 **THEMATIC 去拉
>   FRED 宏观数据**（比"没拿到 ticker"更糟：整条下游链路分析错东西）。
> - **记错位**：真实名录探针 —— LLM 给 `300310.SZ`（真实存在，是**宜通世纪**）→ 名录纠正回
>   `300308.SZ` 并留痕。
>
> **⚠️ 已知未闭合（切出新条目 [AY](#ay-中文公司名--美股代码-仍无确定性兜底ak-已知缺口2026-07-24)）**：
> **中文公司名 → 美股代码**（"英伟达"→NVDA）本轮闭合不了 —— NASDAQ 一手源只有英文名，
> tushare `us_basic` 虽有中文名字段但**实测全 null 且撞 6000 行上限静默截断**。美股本轮拿到的是
> **校验层**（🔴 的主要来源）。
>
> **另两个缺口 —— 已在同 PR 补完**（2026-07-24 用户追问后·下段为最终状态）：
>
> - **① 2 字公司名**：原按 ≥3 字全局门槛一律不扫，把 **40 个真公司**（李宁 / 网易 / 柳工 /
>   滔搏 / 智谱…）挡在外面。**改法 = 白名单而非调门槛**（调到 2 会把 天安/富阳/粉笔 全放进来）——
>   全名录 2 字名**只有 40 个 = 封闭有限集**，人工审一遍即可，不踩 §3.2「豁免集用在开放空间」
>   那条坑（那条治的是**开放**集合）。**30 个放行 / 10 个刻意排除**（长和「增长和」、天安「天安门」、
>   先施「先施压」、富阳（杭州区名）、欧化（形容词）、保诚「确保诚信」、粉笔（普通名词）、
>   盛业「兴盛业务」、天福「上天福佑」、贪玩「孩子贪玩」）。
>   **另加结构性保险**：白名单判定有主观性 → 短名命中**只用于兜底、永不 override**
>   （`registry_short_name_guard`），把判错的代价封顶在"LLM 挂时误认一个标的"，
>   而非"推翻 LLM 正确的结论"。
> - **② 港股取价 —— 原判「属 AL 域不扩界」是错的，实测坐实它是 AK 自己的债**：
>   e2e 实证「腾讯控股现在能买么」→ 名录给出 `00700.HK` → **价格源一个都消费不了** →
>   `price_unavailable=True` → 跑委员会前早退「暂不可分析」。而 **yfinance 明明取得到价**
>   （实测 `0700.HK`→434.60、`2331.HK`→14.42、`9988.HK`→110.00），**差的只是格式**
>   （Yahoo 只认 4 位、tushare/名录存 5 位；`00700.HK`/`02331.HK` 一律空数据）→ **那是个假早退**。
>   改法 = `_yf_ticker_from_tickers` 加港股腿（先美股后港股，双重上市优先美股）+ 5→4 位归一。
>   **不拆 F1 cashtag 墙**（那道墙防的是"从自然语言猜 ticker"，走 `_extract_us_ticker` 另一分支）。
>   **连带治一个北极星问题**：`_sync_fetch` 原**硬编码** `market="US"`/`currency="USD"`，
>   港股腿接上后不改会把 434.60 **HKD 标成 USD** → 下游 EXEC-FLOOR check② 拿它当尺子量价位
>   就是错币种；Alpha Vantage fallback 同理（返回体硬编码 USD）→ **显式不兜港股**，诚实失败。
>   e2e 复验：`price_unavailable` True→None、`quality_flag` degraded→ok、价格腿
>   `yfinance 0700.HK @ 434.60 HKD / market=HK`。

> **2026-06-05 QC-R1 收口 rescope**：原 AK = "结构化接线 + 本地名录 + 删桥接"。
> **结构化接线已由 QC-R1 G5（方案 A）完成**——`tushare/yfinance.__init__` 加
> `tickers` 参数，`classification.tickers`（经 auto-confirm）结构化流入价格源
> （[tushare_source.py](../../src/committee/common_context/sources/tushare_source.py)
> `_ts_code_from_tickers` / [yfinance_source.py](../../src/committee/common_context/sources/yfinance_source.py)
> `_us_ticker_from_tickers`）。**字符串桥接（摊 A）从未 land——QC-R1 开工时作为
> 未提交在制品被丢弃**，故"删桥接"已无对象。
> ⚠️ **2026-06-05 事实纠正（ticker-confirm 节点）**：原 rescope 写"QC-R1 G4 已把
> `_render_common_context` 改读 source-keyed dict、phantom `symbol` 字段问题已修"——
> **不准确**。QC-R1 G4 只新增了 `_render_source_routing`（sources_routed 行），
> `ticker=` 字段仍读不存在的 `ticker_payload.symbol`、实测仍恒显 `-`（中际旭创 e2e
> 两次复现）。**真正修复 = ticker-confirm `224839a`**（新增 `_render_ticker_payload`
> 按源渲染 `source:ticker@price`）。契约**测试**：ticker≠`-` 回归断言已随 224839a 建
> （[test_trace_report.py](../../tests/test_trace_report.py)）；"render 引用的 state key
> 存在于 checkpoint schema"的 smoke 仍未建（保留本条剩余项 #2）。
> **剩余 = 解析质量层**（名录）+ state-key 契约 smoke，接线地基已铺好。

- **强度**: 🔴（源头数据正确性：防 LLM 记错代码 + 堵 "LLM 挂 + 中文名" 残留洞）
- **背景**: 2026-06-04 中际旭创 e2e seg1。query 中文名无代码 → 源内部 regex 提不出。
  QC-R1 已让 classify/解析吐结构化 tickers 并直达源（中际旭创 e2e 实证 tushare
  拿到 300308.SZ price=1280.0）。但**纯 LLM 解析有两个洞，唯本地名录能堵**。
- **剩余任务**:
  1. **本地证券名录**（tushare `stock_basic` 一类 code+name 全量表，日级缓存）：
     - **校验** LLM 吐的 ticker（防记错位 → 静默拉错公司价格 → 全链路错标的 + 每个
       数字伪 verified 背书；比伪精度深一层，EVID 救不了）
     - **兜底** LLM 失败时拿公司名查表（确定性、零 LLM 依赖，堵 "LLM 挂 + 中文名"
       残留洞——该洞下 `classification.tickers`=空，纯结构化接线对它零作用）
  2. **trace 契约测试**（随本 node 带走）：smoke 断言 render 引用的 state key 在
     checkpoint schema 存在 / seg1 trace ticker 字段在 ticker 实际存在时 ≠ `-`。
     根因：trace_report 与 state schema 无契约测试。
- **已完成（QC-R1 G5，不再属 AK）**: `tickers` 参数结构化接线 + 价格源消费 + auto-confirm
  注入 + state.confirmed_tickers 接缝（PR QC-R1，commit `27286a3`）。
- **触发时机**: 走 pre-node 设计边界审查后启动（标准 node 体量，**不热修续上**）。
- **为什么仍 🔴 不能只靠 QC-R1 接线**: 残留洞触发条件 = LLM 挂或记错码，那时
  `classification.tickers` 本身 = 空/错，结构化接线对该洞**一毫米不堵**；唯名录的
  名称查表兜底 + 校验能堵。
- **进入时点**: 2026-06-04（中际旭创 e2e seg1）；2026-06-05 QC-R1 收口 rescope（接线层剥离）
- **预估工作量**: 中（名录接入/缓存 + 校验/兜底 + 契约测试；接线已由 QC-R1 完成）
- **与 web_search 解析（G1，`653c1e0`）的优先级链**（2026-06-05 ticker-confirm 对齐）:
  现有三种解析机制，优先级链 = **本地名录精确命中（AK，确定性）> web_search 查证
  （G1，LLM+联网）> LLM 裸解析（classify 内联，纯记忆）**。
  - **web_search 不替代 AK**：AK 仍 🔴，是确定性**最优先路径 + 校验层**；web_search 是
    LLM 解析路径内部的**增强降级层**（比裸记忆强，仍是 LLM、仍可能错位）。
  - **当前**（AK 未落地）：链仅 `classify 内联 LLM → _resolve_tickers(web_search LLM)`，
    两层都 LLM。AK 落地后插入确定性顶层，并**校验** classify/web_search 吐的码。
  - **人工确认闸（G2）= 所有自动解析之上的最终校验**；名录落地后是"确定性预填 +
    校验"，确认闸是"用户终审"，两者互补不互斥。
  - 详见 [ticker-confirm retro §2](../retro/S2/ticker-confirm_2026-06-05.md)。
- **联动**: 条目 G 已 close（QC-R1 决议 2 类型 taxonomy）；名录落地后 ticker_resolved
  可能成为未来路由细化依据
- **2026-06-16 新数据（D hot-e2e seg1，[观察](../observations/deepseek-classify-timeout-2026-06-16.md)）**:
  本条假定的"名称→代码兜底洞"在 **"LLM 挂"** 时触发——实证该触发条件被 **classify 2.5s 硬超时
  + 今日 DeepSeek 全提示稳定 3-4s** 命中，即洞在 **正常 slow-DeepSeek 日常态触发、非罕见 outage**
  （seg1 连续 2 次 classify timeout→regex→"中际旭创"未解析→`ticker_payload` 空）→ 抬 AK 实际频率/优先级一档。
  另记**更轻杠杆**（AK 框架外）：重核/放宽 classify 2.5s 超时预算可能是比全套名录更便宜的缓解（与 AB 同族、不同步骤）。
  *（不计数、不改 AK 强度/触发档，仅添数据点；§0.2 一览表无需动。）*

- **🔎 2026-07-24 补证（清理 stale 分支时打捞·"更轻杠杆"那条从推测变实测）**：上条「放宽 classify
  超时可能更便宜」当时只是推测；实际**早在 2026-06 的 D hot-e2e 就已实测并改出来过**，只是那次
  刻意没合、随分支埋了 7 周：
  - **实测证据**（`auto/D-fm-hot-e2e` @ `e95b700`·commit body 原文）：*「今日 DeepSeek classify
    全提示 ~3-4s **稳定** >2.5s → 回退 regex → ticker 名解析失败 → `ticker_payload` 空」* ——
    与上条 seg1「连续 2 次 classify timeout→regex→中际旭创未解析」**同一根因、独立第 2 次复现**
    → 坐实是**正常 slow-DeepSeek 日常态**，非罕见 outage。
  - **改法**（一行）：[`classifier.py`](../../src/committee/query_class/classifier.py) `LLM_TIMEOUT_SECONDS = 2.5` → `15.0`。
  - **当时为何没合**：该 commit 自注「仅 D 测试 worktree·**勿合 #144**」——D 轮验证面是
    `make_decision_node`（fm 决策节点），classify 属 Phase-0a infra，放宽超时只为**去掉环境
    confound**、还原 baseline 成功 classify 条件，不属该 PR 验证范围 → 有意留在测试分支。
  - **现状**：main 仍是 **2.5s**（已核）。分支已于本次清理删除，改法与证据保全在此。
  - **✅ 已落地（2026-07-24·用户拍）**：`LLM_TIMEOUT_SECONDS` **2.5 → 15.0** 且改 **env 可调**
    （`COMMITTEE_CLASSIFY_TIMEOUT`·镜像 `COMMITTEE_PASS0_TIMEOUT` 先例·顺带解掉 obs 文档点名的
    「写死常量、非 env 可调」痛点）。**非拆墙**：原 ≤3s 拍板自带「未来若 obs 数据驱动可调，进 backlog」
    修订闸门（[A6.1.1-decomposition §step3](../plans/A6.1.1-decomposition.md)），条件已满足。
    守护测试上界 ≤3s → ≤15s、**守护意图保留**（天花板不得吃掉 90s run 预算·再上调须重走 obs 论证）。
    DoD：全量 2718 passed + mutation 证守护测试承重（默认改 20 → 2 测试真红）+ env override 测试。
  - **⚠️ 这只降低触发频率·没消除洞本身**：LLM 真挂时仍回退 regex、仍认不出中文公司名 →
    **AK 主体（本地名录）仍 🔴 OPEN**，本项非其替代。

### AY. 中文公司名 → 美股代码 仍无确定性兜底（AK 已知缺口，2026-07-24）

- **强度**: 🟡（AK 闭合了 A股/港股的中文名兜底 + 三市场校验；美股这一半仍靠 LLM）
- **背景**: AK 落地时实测两条美股中文名路都不通 ——
  1. **NASDAQ Trader 符号目录**（AK 实际采用的美股源）**只有英文名**（`NVIDIA Corporation - Common Stock`），
     扫英文名误命中率过高（"Apple" / "Inc"），且会踩 yfinance「严格 cashtag-only、无 cashtag 不猜」
     那道 2026-05-19 用户裁决刻意立的墙 → AK 明确**不对美股做名称扫描**。
  2. **tushare `us_basic`** 虽有 `name`（中文名）字段（[官方文档](https://tushare.pro/document/2?doc_id=252)
     明写 "name = 中文名称"），但**按文档的 `limit`/`offset` 分页实测 24915 行、中文名非空 0 行**，
     直接点名查 `NVDA`/`AAPL`/`BABA`/`TSM` 也全部 `null`（字段返回了、值是空 = **数据缺失**，
     不像权限遮蔽——权限不足通常整个 `code≠0`）。文档写"120 积分试用 / 5000 积分正式"，
     **是否升档就有中文名无法从现有证据判断**。
     〔**纠正（2026-07-24 用户指出文档后复核）**：AK.0 初次探针**没分页**、拿到首 6000 行，
     据此写的"撞 6000 行上限被静默截断"是**归因错误** —— 分页能拿全 24915 行（比 NASDAQ 的
     13537 还多，含 ADR/GDR）。**中文名缺失的结论不变且更硬**（24915 行 0 条 + 4 次点名查询全 null）。〕
- **后果**: 「英伟达现在能买么」这类**中文提问美股**的 query，在 LLM 挂时仍认不出标的
  （regex 认不出中文、名录不扫美股英文名）→ 回落到 AK 之前的状态。**A股/港股无此问题**。
- **修法候选（不预设）**: ① 找带中文名的美股名录源（tushare `us_basic` 需更高积分且要分页绕开 6000 上限，
  须先验中文名字段是否真会填）；② 自建小型中英对照表（只覆盖高频美股，人工维护，成本低但覆盖有限）；
  ③ 维持现状 —— 承认这一半靠 LLM + web_search（AK 已让 web_search 产出过名录校验，至少不会给出假码）。

> **✅ 2026-07-28 pre-node 探针 + 两次定案（同日转向）** — 现行方向见 [**AY plan v2**](../plans/AY-decomposition.md)、
> 证据见 [AY.0 探针留档](../observations/AY-us-name-source-probe-2026-07-28.md)：
>
> **数据源结论（承重·不变）**：
> - **tushare 支线判死**：文档声明 `name=中文名称` 但 fresh live 实测 24915 行 0 条 + 热门票点查全 null；
>   本 token 有 us_basic 实权限（能拉全量）却仍 0 条 → **中文名缺失与积分档无关、是数据本身没有**，不买。
> - **东财 `clist`**：知名票中文名质量高（热门 21/24），但**全表中文名仅 21%**（79% 是 ETF/SPAC/债）
>   且**非官方端点受限流摆布** —— 稳定性 gate 第 1 轮即 FAIL（12 页被拒·丢 1200 行·`RemoteProtocolError` 秒拒成簇；
>   0.15s 节流 25/25 全拒、0.5s 才通；`pz` 放大无效故 137 请求省不掉）。
>
> **~~定案 v1 = 混合方案（手工核心 + 东财广覆盖）~~ → 🔴 同日推翻**。
> **现行定案 v2 = 标的确认交互**：系统只**提议候选**（curated 种子 → 联网搜 → 名录验真），
> **用户拍板**；**东财层删除**（provider + gate 两 goal 均取消·`verify_sources.py` 东财组已回退）。
> - **转向理由**：① 东财拉取不稳（上条实测）；② **名称自动匹配本身不可靠** —— 碰撞清点实测
>   「博通」撞博通股份/博通集成、「京东」撞**京东方**（面板厂）、「百度」撞**千百度**（鞋类），
>   同系独立实体（网易云音乐/阿里健康/京东物流健康工业）与人民币柜台（-R/-WR）全会混入；
>   光「京东」二字在港股名录命中 7 条、**只有 1 条对**。改成"提议+确认"后，这些噪声从**风险**降为**待排除选项**。
> - **用户产品理念（本次确立·高于本节点）**：*涉及个股的一定要和用户确认* —— 本流水线跑一轮很贵，
>   前期多问一句远低于"跑完才发现分析错了公司"的代价。
> - **本节点承接 [条目 Q](#q-用户-query-反馈引导通路缺失后续前端同步修改✅-closed-2026-08-06-close-by-decision保留位置) 的一部分**（可疑降级的告知通路）—— 见 Q 的 2026-07-28 第 2 段更新。
> - **✅ 合并后遗留（2026-07-29 登记·AY 主体已 CLOSED，以下为独立小项）**：
>   1. ⬜ **确认闸真实 TTY 交互人工实跑一次** —— 9 条靶测覆盖全部分支逻辑（mock `typer.prompt`），
>      但真实终端下的排版 / 默认值 / 中文渲染未经人眼确认（确认闸仅在 `sys.stdin.isatty()` 触发，
>      非自动化可补）。命令：`committee analyze "英伟达现在能买么"`。
>   2. ⬜ **`_TICKER_CODE_RE` 不认美股码（🟢 小口子·合并时发现·未修）** ——
>      [`cli.py`](../../src/committee/cli.py) 的 `_TICKER_CODE_RE` 只认
>      `\d{6}.(SZ|SH|BJ)` / `\d{4,5}.HK`（2026-06-10 [#145](https://github.com/JunoChenZt/subagent-for-investment/pull/145) 立，
>      **早于** AK/AY 的美股支持）→ 用户在确认闸敲 `NVDA` 想直接改正，会被判成"非代码"
>      **落进联网搜索**，而不是当场采纳。AY 让系统能提议 NVDA、确认闸也回显「NVDA (英伟达)」，
>      唯独**用户手输美股码这条路没跟着扩**。修法直白（正则加美股分支 + 靶测），
>      但属既有设计边界、**非 AY 引入**，故未在 #213 内顺手改（守 scope）。
>      触发条件：真实 TTY 实跑（上条）撞到即修。
> - **✅ 状态：CLOSED —— 已 squash 合 main（[#213](https://github.com/JunoChenZt/subagent-for-investment/pull/213) @ `681ed9e`·2026-07-29·分支已删）**：
>   G1 可扫描判据 market 级→条目级 · G2 curated 34 名候选种子 + 美股 2 字白名单 ·
>   G3 classify 重试（**只对快速失败·超时刻意不重试**，守 S2.md 的 90s run 硬预算）·
>   G4 可疑降级不静默通过（判据零新增机制，复用现有 `ClassificationResult.source`）。
>   **核心缺口已实证闭合**：强制 classify 的 LLM 超时 + 关闭联网补解析，
>   「英伟达现在能买么」→ `NVDA`、「微软」→ `MSFT`、「阿里巴巴」→ `BABA`+`09988.HK`，
>   且「中际旭创」未退化、「高通胀环境下怎么配置」零误命中
>   （[evidence](../observations/AY-g1g2-probe-2026-07-28.md) / [路由验证](../observations/AY-g5-routing-probe-2026-07-28.md)）。
>   全量 3012 passed / 0 failed · 新增靶测 77 条 · mutation 七次全部精确命中。
>   [节点复盘](../retro/S2/AY_2026-07-28.md)。**剩：PR 合并 + 确认闸 TTY 人工实跑。**

- **触发条件（falsifiable）**: 真实 run 中出现「中文提问美股 + classify 失败 → 无标的」的实例；
  或用户明确要用中文问美股。
- **反向条件（close 不做）**: 若实际使用里美股 query 都带代码 / cashtag / 英文名 → 缺口不构成实际问题。
- **进入时点**: 2026-07-24（AK 收口切出）
- **预估工作量**: 小-中（取决于走哪条修法）

---

### AL. 市场感知路由（A 股 query 不挂 yfinance / 美股不挂 tushare）

> **✅ 方向(1) DONE（2026-07-23·[#199](https://github.com/JunoChenZt/subagent-for-investment/pull/199)）·改法 supersede 本标题**：治 degraded 噪声的**最终落地 ≠ 本条标题的"市场感知路由"**。路由做法（[#198](https://github.com/JunoChenZt/subagent-for-investment/pull/198)）曾合入 main、随即被 [#199](https://github.com/JunoChenZt/subagent-for-investment/pull/199) **supersede**——因按国籍只挂一个价格源会**误摘双重上市**（阿里 BABA+9988.HK）。**用户裁决终版 = 价格源冗余组 `quality_flag`**：两边都问（恢复双挂）·`tushare/yfinance` = 冗余组·**≥1 报价即不降级**·仅全价格源失败才 degraded（[`_quality_flag`](../../src/committee/common_context/builder.py)）。非价格源逐个要求不变。DoD 2686 绿 + mutation。**下方"修法方向"= 已被 supersede 的路由方案·point-in-time 保留不改**。**方向(2)（扩 tushare 拉基本面）仍开着**·AL 未整体 close。

- **强度**: 🟡（quality_flag 对 A 股场景失去区分度；非阻塞，有真实成本）
- **背景**: 2026-06-05 QC-R1 G6 中际旭创 e2e seg1 实测。`ticker_specific` 路由**无条件**
  挂 tushare+yfinance（QC-R1 G4 继承自既有二挂，[builder.py `_route`](../../src/committee/common_context/builder.py)）。
  但 A 股 query（中际旭创=300308.SZ）下 **yfinance 恒失败**（无 US ticker → cashtag fallback →
  无 `$cashtag` → raise）→ dispatch 永远 partial → **quality_flag 恒 degraded**。
  反向同理：美股 query 挂 tushare 也恒失败。
- **后果**: A 股/美股纯单市场 query 的 `quality_flag` **永远是 degraded**，对"真降级 vs
  市场不匹配"失去区分度（与 backlog Q `degraded_reason` 隔离同类——degraded 语义被噪声污染）。
- **修法方向**: `_route` 按 tickers/query 的市场归属选价格源——A 股码（`\d{6}\.(SZ|SH)`）只挂
  tushare，美股码（字母）只挂 yfinance，港股（`.HK`）按 yfinance HK 能力定。无法判定市场时
  退回当前"双挂"。需与 G4 routing reason 一致登记（cost 护栏）。
- **🔍 反向发现（2026-07-10·M1 T10 数据点调研·纠一处隐含错前提）**: 本条"美股不挂 tushare"的
  前提 = **假设 tushare 对美股没用**——但**这是错的**：tushare 服务**覆盖美股**（`us_daily`/`us_basic`
  接口）。恒失败的真因 = **本仓 [`TushareSource`](../../src/committee/common_context/sources/tushare_source.py) 适配器写死只认 A股**（`_ts_code_from_tickers`/`_extract_cn_ticker` 只解析 CN 码→对
  NVDA 抛 `ValueError`；`api_name:"daily"` + 硬编码 `market:"CN"`/`currency:"CNY"`·从没调 tushare 美股接口）。
  → **两个修法方向分立**：**(1) 本条原方向** = 市场感知路由（把失败源摘掉·治 degraded 噪声·**便宜**）；
  **(2) 更富方向** = 扩 `TushareSource` 接 `us_daily`/`us_basic`（美股获**结构化基本面**·当前美股只有
  yfinance 价格）·**有真实价值**。**T10 关联**：方向 (2) 会实质降低美股过度打码——NVDA 数据点1
  的高打码**部分是这适配器缺口造成**（营收/PE 等基本面对美股只能网搜→审计核不了→打码），
  **非美股固有无源** → 意味着 NVDA 作为 T10「最坏情况」数据点**不够干净**（混入可修的适配器缺口）。
  记此供 T10 判据 + 未来动 `_route`/adapter 时一并评估（方向 2 是否值得，看 T10 是否真要 #4）。
- **⚠️ 2026-07-16 重判（MASK.GATE-B 收官后·上条"看 T10 是否真要 #4"已 moot）**: **T10/#4 目标已消失**
  ——过度打码由 [GATE-B 门重定义](#defect-prose-mask-ref-散文门冤枉打码--参考集选窄脱节-二值门无中间档🟠伴生逃逸洞见下)治好（**涂 21→0**·[#187](https://github.com/JunoChenZt/subagent-for-investment/pull/187)），非靠 #4 或本条方向(2)。
  ∴ **方向 (2) 的原驱动力「降打码」失效**：
  - **方向 (1)（市场感知路由·治 degraded 噪声）**：✅ **立论不变**（与打码门正交）·仍值得·小。
  - **方向 (2)（扩 `TushareSource` 接 `us_daily`/`us_basic` + 拉基本面）**：🔲 **降级为"值得但非高杠杆"**——
    剩余价值 = 让基本面数字在报告里拿 🟢 结构化源、而非 🟡「未独立核实」caveat（**提可信度呈现·非修 bug**）；
    誊写抄错风险另由 **G5 AI 誊写核查**（#187）兜住。**不再"优先"**·随方向(1) 顺带评估即可。
- **⚠️ 2026-07-21 再校（GATE-B「二档问题」讨论·纠上条对②的误伤）**: 上条把方向(2) 降级的理由 =「过度打码已被 GATE-B 治好」，**只对"涂→0"成立·对"盖章措辞太粗"不成立**——GATE-B 没治后者（券商研报数 与 无源盖**同一个**「未独立核实」章）。∴ **方向(2) 对"二档校准"的价值未缩水**（真·财报数从结构化源来 → 🟢 不盖章 = 根治二档）。**但②不必等方向(2)**：GATE-B 重构讨论定 **②落点 = 前端 chip 带出处**——核 [InlineMd.tsx:89](../../frontend/src/lib/InlineMd.tsx) 坐实出处数据已到前端（hover 已渲染 `watermarks` + 类型带 `source_type` 字段），缺口仅 = 显示为代码(`REF#W-…`)非人话 → **前端加"代码→人话"翻译表**（REF#W→券商研报 / R#→新闻 / T/Y/F→官方库）·**纯前端零风险·正文「未独立核实」不改**；方向(2) 作根治另排期。**治标〔门内改正文措辞"据券商研报"〕✘放弃** = 踩 R5-01 方向红线（替换=靠省略软性上抬可信度）+ 不孤立（动 `classify_stamp` 返回契约 + 碰 `_dedup_caveats`·known-pitfalls §3.2 坑）。详 [gate-routing-redesign 理想图](../plans/gate-routing-redesign/gate-explorer-理想图-下一版-20260720.html) A 车道 + [HANDOFF](../plans/gate-routing-redesign/HANDOFF.md)。**前端 chip 翻译表 = 小 frontend 活·随 ② 落地做·不单列编号条目**（属本条 二档 cluster）。→ ✅ **已落地 2026-07-22**（[#192](https://github.com/JunoChenZt/subagent-for-investment/pull/192)·GATE-ROUTE **G3**：`frontend/src/lib/InlineMd.tsx` 加「代码→人话」翻译表·15 条测试·后端与正文措辞零改）。**②「二档」问题的治标半就此闭合**；**治本半（方向2·扩 tushare 拉基本面 → 净利润/PE 变 🟢 不盖章）仍开着〔**⏭️ 前向更新 2026-07-23·R7·正文不动**：方向2 的**数据侧（Layer 1·拉基本面喂 agents）已 shipped** [#203](https://github.com/JunoChenZt/subagent-for-investment/pull/203)；此处"治本半"= 剩下的 **Layer 2**（把已拉到的基本面接进可信度路让研报数变 🟢·碰 audit/DS-0 load-bearing）·**仍 defer**·须独立设计+用户逐节点确认〕**，AL 本体（方向1 市场感知路由 + 方向2）不受影响。
- **触发时机**: degraded 语义治理 / 与 backlog Q（`degraded_reason` 字段）合并处理时；
  或下次动 `_route` 时顺带。**与 AT 同域**（AT 治现价 retry + 拿不到 fail-fast；本条治市场匹配 + 扩 tushare 基本面）→ 双向链、可合并评估。
- **非 QC-R1 回归**: 双挂行为继承自既有 `default_sources`（QC-R1 G4 只把排他改加法，未改
  价格源市场匹配）。QC-R1 retro q5 surface，本条登记。
- **进入时点**: 2026-06-05（QC-R1 G6 retro）
- **预估工作量**: 小（`_route` 加市场判定分支 + 测试）

---

### AT. 现价锚点可用性保障 — 取价 retry + 拿不到就 fail-fast（check② 尺子的地基）

> **✅ DONE（2026-07-23·AL-AT 节点全收口）**：**AT.1（tushare retry·[#196](https://github.com/JunoChenZt/subagent-for-investment/pull/196)）** 镜像 yfinance 补瞬态重试 + **AT.2（现价拿不到早停·[#200](https://github.com/JunoChenZt/subagent-for-investment/pull/200)）**。**AT.2 终版 = 方案 B 优雅早退（非"报错崩 run"）**：R5 只读调研发现 backlog 原写的"升级报错"若按字面=崩 run=回退 AE 墙前，用户裁决改**优雅早退**——ticker_specific + 有确认标的 + 价格冗余组全失（一个报价都没有）→ 跑委员会前早退、产「暂不可分析」FinalDecision（HOLD·无 execution_plan·不出无法核对的价位·下游零改动渲染·省 token）。守 R5 边界：只在图消费层给 dispatch 已落定终态换处置·不拆"单源失败不拖垮整跑"墙。节点 [retro](../retro/S2/AL-AT_2026-07-23.md)。**下方"修法方向"= 原始设想（"升级报错"）·point-in-time 保留不改**。

- **强度**: 🟡（非阻塞·补 check② 独立锚点在降级 run 的可用性缺口；实现小）
- **背景**: GATE-B 打码门重构讨论副产（2026-07-21·[gate-routing-redesign](../plans/gate-routing-redesign/HANDOFF.md)）。价位安全的**真守门 = EXEC-FLOOR check②（离谱）+ check③（过期·2026-07-22 转正）**（[`price_reality_mismatch`](../../src/committee/facts/exec_floor.py:211)·拿**真实市场价**当尺子量价位是否离谱）。该尺子来源 = 表① `Reference(data_key="price")`（yfinance/tushare 现价）。**现价恰是结构化源最稳拿得到的一个**（价格就是 tushare/yfinance 看家产出·A股拉不到的是基本面不是价格）→ check② 几乎永远有独立锚点、守得住 → 价位第一关（门控·**已实施方案 (b)**·[#192](https://github.com/JunoChenZt/subagent-for-investment/pull/192)）几乎永不需 fire。
- **缺口（corner case）**: 真拿不到现价（数据抓取整个失败）时——① **check② 退化**：锚 fallback 到 `plan.current_price`（模型自报·降级 run 里也不可信），两个都无才 skip（[exec_floor.py:227-231](../../src/committee/facts/exec_floor.py)）；② 现设计 **"5 源各自超时容错·挂了就跳过·run 照跑"**（[builder.py](../../src/committee/common_context/builder.py)）→ **地基塌了还硬跑**，产出无法被 sanity-check 的价位。
- **修法方向（用户 2026-07-21 拍·记此待实施权衡）**:
  - **取价 retry**：`ticker_specific` 的价格源失败 → retry（≤3 次·含首次）。**yfinance 已有**（[yfinance_source.py:48](../../src/committee/common_context/sources/yfinance_source.py)·3 次 + 指数退避 + Alpha Vantage 兜底）；**tushare 缺**（[tushare_source.py:100](../../src/committee/common_context/sources/tushare_source.py)·单次 POST 即 raise）→ 补 tushare retry 达对等。
  - **fail-fast**：retry 全耗尽仍拿不到现价 → **一开始就升级报错**（不进入 degraded run 硬跑）。**scope 待确认**：仅限 `ticker_specific`（macro / 无 execution_plan 的 query 无单一现价·不适用）。
- **⚠️ 设计边界（Chesterton's fence·[[feedback_read_boundary_intent_before_expanding]]）**: "5 源各自容错·不拖垮整跑"是**刻意**立的健壮性边界（AE 家族健壮性缺口治理）。本条给"取价源"开一个**不可容错**例外 = 拆这道墙一角 → 实施前须 review 当年立此边界的一手记录，确认例外不引入回归、且 fail-fast 与既有 degraded 语义（backlog Q / AL）不打架。
- **触发时机**: ✅ **已触发但未随做（2026-07-22）**——GATE-B C（价位门控）已由 [GATE-ROUTE G2 #192](https://github.com/JunoChenZt/subagent-for-investment/pull/192) 落地 (b)，AT 未一并做。**强度 🟡→🟠 上调**：(b) 之后价位**不再被机械抹除**、全靠 check②/check③ 兜底 → **现价拿不到 = 唯一的尺子塌了却仍放行价位**，风险实质上升（原判「check② 尺子几乎永远在」仍成立，但后果变严重）。下次动价格源 adapter 或 `_route` 时优先做。**与 AL 同域** → 双向链、可合并评估。
- **进入时点**: 2026-07-21（GATE-B 重构讨论）
- **预估工作量**: 小（tushare 加 retry ≈ 镜像 yfinance；fail-fast 分支 + scope 判定 + 测试）
- **进度（2026-07-23）**: **AT.1（tushare retry）✅ 已合 [#196](https://github.com/JunoChenZt/subagent-for-investment/pull/196)**（镜像 yfinance·仅网络/传输层瞬态重试·空数据非瞬态不重试·2681 绿 + mutation）。**AT.2（取价耗尽 fail-fast·拆"单源失败不拖垮整跑"墙·需 R5 设计意图确认）经用户裁决本轮 defer**·同节点 AL.1 亦 defer。拆解 + 坑表 = [AL-AT-decomposition.md](../plans/AL-AT-decomposition.md)。

---

### AU. Python 版本跨环境对齐 — 本地 3.13 / CI 3.10 / Docker 3.11 skew ✅ CLOSED 2026-08-07 (close-by-completion·保留位置)

- **✅ 实现（2026-08-07·合 main `e60c74f`·[#229](https://github.com/JunoChenZt/subagent-for-investment/pull/229)）**：rescope 后写明的窄活已做——[ci.yml](../../.github/workflows/ci.yml) `backend` job 加 `matrix: python-version: ["3.10", "3.11"]` + `fail-fast: false`（一个版本挂掉不掩盖另一个，差异化 bug 恰恰要看哪个版本红）。**取 matrix 而非「换成 3.11」**：只换会丢掉 `requires-python = ">=3.10"` 声明支持面的地板覆盖。**不动**版本声明 / Dockerfile / lock —— 收敛大工程仍不做（理由见下）。
  - **连带修**（review 抓出）：[CONTRIBUTING.md](../../CONTRIBUTING.md) 那份**待用**的 ruleset 配方写死 `{"context": "backend"}`，matrix 后该 context 永不上报 + `strict_required_status_checks_policy: true` = 将来谁升 Pro 照贴就是**每个 PR 永久 pending 全合不了** → 已改两个 matrix context 并立「context 须与 ci.yml job 名逐字一致（含 matrix 后缀）」约束。**这类「待用配方而非生效配置」的 stale，CI 不会替你报错。**
  - **剩余 skew 的处置（明确不做，不是漏了）**：dev 本地 **3.13** 在 CI 里仍无覆盖。本条治的是「**测试版本 vs 生产版本**错位」——生产那台是 3.11，已覆盖；本地 3.13 不是任何部署目标，为它加一条 CI 腿属扩界。
- **⛔ 判据说明（2026-08-07 close 时补）**：下方「真残留」「新 scope」两段是 **2026-07-24 rescope 时的现状诊断**，描述的是**本条修复前**的 CI 形态（`backend` 只跑 3.10）；#229 之后已不再成立，作为立条理由**原样保留**，不要当现状读。
- **🔵 RESCOPE + 降级（2026-07-24·N 收口后重评估·用户拍「做 rescope-小活」）**：原「评估三环境收敛到单一 Python 版本」的**可复现动机已被 universal `uv.lock` 解掉**——lock 用 `resolution-markers` 显式枚举 `<3.11 / ==3.11.* / ≥3.12<3.14 / ≥3.14` × {win32, non-win32}，把每个 (Python 版本 × 平台) 分支**确定性钉死**（实证：`rpds-py` 按 `<3.11`/`≥3.11` 钉两个版本、`tomli`/`exceptiongroup` 仅 `<3.11`、`typing-extensions` 仅 `<3.13`）。AU 正文原担忧「即便 lock 也可能解析出不同轮子」**技术成立但那是确定性分支解析、非漂移**——正是要的可复现保证。→ **收敛版本的大工程不做**（且对 `requires-python=">=3.10"` 的项目=收窄声明支持面·方向存疑）。
  - **真残留（换个样子的问题·与「版本统不统一」无关）**：**测试覆盖版本 vs 生产版本错位**——CI backend job 在 **3.10**（`requires-python` 地板）全量 test-run、生产 Docker 跑 **3.11**、dev 用 **3.13**；**3.11（生产实跑版本）在 CI 里只 `docker build` 装得上、从不 test-run**（[ci.yml](../../.github/workflows/ci.yml) `docker-build` job 只 build 不跑 pytest）。若存在 3.10↔3.11 行为差异（语言/stdlib），CI 测不到、而 bite 的恰是生产那台。
  - **新 scope（小活·仍 open）**：让 CI 测试覆盖生产 Python 版本——backend test job 换 3.11 **或**加 `3.10 + 3.11` 小 matrix（地板 + 生产双测）。**不动**「收敛单一版本」。
  - **强度 🟡→🟢**：可复现已由 lock 保证；残留=测试版本盲点·行为差异至今 0 实证 bite·非阻塞。
  - **进入时点仍 2026-07-23**；改 CI = 生产邻接·需用户逐步确认（本次仅改 backlog 记录·未动 CI）。
- **强度**: ~~🟡~~ → 🟢（非阻塞；可复现 resolved-by-lock·残留=CI 测试版本盲点）
- **背景**: 2026-07-23 N（依赖 lock）选型讨论副产。查 CI/Docker/本地实况暴露 **3 套 Python 版本不一致**：本地开发 = **3.13.6**（Windows）/ CI = **3.10**（[ci.yml](../../.github/workflows/ci.yml)·ubuntu）/ Docker 部署 = **3.11.15**（[Dockerfile](../../Dockerfile)·Linux）。`requires-python = ">=3.10"`。
- **后果**: lock（N）锁的是**包版本**，但包解析结果与 Python 版本有关；三版本 skew 下即便 lock 也可能在不同环境解析出不同轮子/传递依赖。lock 的收益在其他条件对齐时最大 → Python 版本 skew 是 lock 之外的残留漂移面。当年咬人的 fastapi 0.137 是**包漂移**非 Python 版本漂移，故 **N 本身不解此条**（用户 2026-07-23 明示「Python 对齐单独立 backlog」·不塞进 N scope，守 [[feedback_treat_scope_no_creep]]）。
- **任务候选**: 评估三环境收敛到单一 Python 版本（如统一 3.11 或 3.12）——需权衡 uv.lock 的多版本 marker 解析已能覆盖 skew（N 落 uv 后部分缓解）vs 彻底对齐消除 skew 根。**先看 N（uv.lock）落地后残留 skew 是否真造成问题**再定是否动。
- **触发条件**: N 收口后评估 / 或专门 deps-hardening window；与 §N 联动。
- **进入时点**: 2026-07-23（N 选型讨论，用户指示单独立项）
- **预估工作量**: 中（三环境 Python 版本对齐 + 回归验证；不确定是否真需要，看 N 后残留）

---

### AM. deepseek 不遵守 raw-last 输出顺序指令（P2 观察项）✅ CLOSED 2026-07-08 (close-by-completion·已合 main `416d0bb`·保留位置)

- **✅ 实现（2026-07-08·合 main `416d0bb`〔merge `98c39b8` code + `4229ac1` docs〕·用户拍「给足预算」方案·不 close 而是治）**: 排查坐实——生产 `.env.prod` academic 三角色跑 gemini/gpt-4o（**非 deepseek·AM 无生产暴露面**），但同机制的**截断根**在场（deepseek 不遵守 raw-last / 生产 gemini-2.5-pro thinking 吃 ~68% 预算·2026-06-05 political-arms 实验）。修法 = 绕开「靠字段顺序」直接**给足输出预算**从根上不截断：新 config `MAX_TOKENS_ACADEMIC`（默认 **12288**·env `COMMITTEE_MAX_TOKENS_ACADEMIC` 可调·clamp [4096,32768]）+ `make_analyst_node` 对 `tier=="advisory"`（political/historian/economist）传 `max(MAX_TOKENS, MAX_TOKENS_ACADEMIC)`（下限语义·镜像 fund_mgr `MAX_TOKENS_DECIDE` 先例·[base.py:888](../../src/committee/agents/base.py)）。**连带治生产 gemini 截断根**（原始 2026-06-05 问题同源）。**DoD**：全量 **2443 passed** + mutation 证 advisory 分支 load-bearing（还原改动→靶测转红）+ 9 新测（默认/clamp/env·tier 选择器精确性·advisory 拿高预算·research 传 None 不变·对抗假绿）·[test_am_academic_max_tokens.py](../../tests/test_am_academic_max_tokens.py)。**已合 main `416d0bb` → close-by-completion**（活跃 17→16）；raw-last prompt 指令**保留**（对生产 gemini 仍 load-bearing）。live 文档收口：api.md env 表 / prod-runbook §3.5 截断旋钮 / political-arms 前向标注（`4229ac1`）。
- **强度**: 🟡 P2（观察项，非阻塞）
- **背景**: 2026-06-09 political 选型四臂实验（[decision-review](../observations/experiments/political-arms/decision-review.md)）。瘦身+重排 prompt 给 academic 角色（political/historian/economist）加了"字段输出顺序：结构化承重字段先于 raw 输出"指令——抗截断设计：截断时先丢 raw 论证收尾，不丢 decision_windows/incentive_structure 等承重字段。gemini 遵守 raw-last；**deepseek-v4-pro 不遵守，把 raw 写在结构化字段之前**（臂B eval `field_order_struct_before_raw=false`）。
- **后果**: 若 deepseek 在极端长输出 + 紧预算下截断，会先丢结构化承重字段，重排保险对它失效。
- **为何 P2（非 P1）**: deepseek 的 raw 不抄花名册（更遵守瘦身）→ raw 更短更纯 → 不易截断（臂B output 4476 超 4096 仍未截断）。瘦身的抗截断收益**部分覆盖**了 raw-last 缺失，实际风险低。
- **触发条件**: raw 异常长 + max_tokens 预算紧（academic 角色 + 大量 web_search 输入 + 低 max_tokens）下 deepseek 出现截断。
- **候选缓解**: 给重角色设 max_tokens 下限；或探索 deepseek 强制字段顺序的机制。
- **进入时点**: 2026-06-09（political 选型实验）
- **预估工作量**: 小（观察 + 按需设 max_tokens 下限）

---

### AN. triage/audit 命名与用户心智模型错位 — dataflow 加别名说明（P2 文档债）

- **强度**: 🟡 P2（文档债，非阻塞；但已实际造成一次判定干扰）
- **背景**: 2026-06-11 F1-graph-join 事故核查中暴露：用户心智模型把流水线理解为"初审（研究材料完成后）+ 终审（辩论结束后）"两道审计；而系统词汇里这是两个不同概念——**triage（Phase 1.5，质检员：报告质量分诊+退回重写）** 和 **audit（Phase 3.7，审计员：事实清单逐条核数，单次）**。命名错位让一个真 bug（ds_merge OR-触发提前跑决策链）差点被当成"设计内的第一道审计"放过。
- **任务**: [dataflow-whole-pipeline.md](../pipeline/dataflow-whole-pipeline.md) 速览第 3/7 步加一行别名说明（triage = 初道质检/初审；audit = 终道核数/终审），把用户词汇和文档词汇对齐。
- **为什么延后**: 一行文档改动，但 dataflow 是高引用文档，顺手改易夹带；等下次正式动 dataflow 时一并。
- **触发条件**: 下次任何 PR 触碰 dataflow-whole-pipeline.md 时顺带；或 fm-spec e2e 收口 retro 时一并。
- **进入时点**: 2026-06-11（F1 事故核查，用户指示记档）
- **预估工作量**: 极小（一行别名 + 速览两处括号注）

---

### AO. DS-0 ds_researcher retrieved 路径溯源元数据剥离 ✅ CLOSED 2026-07-08 (close-by-completion·保留位置)

- **Close（2026-07-08·backlog triage 配额 reconcile·用户拍）**: close-by-completion **主体**——PR1 [#160](https://github.com/JunoChenZt/subagent-for-investment/pull/160) 已合 `2a63aa4`（state 级 provenance 链路真交付）、PR2 [#161](https://github.com/JunoChenZt/subagent-for-investment/pull/161) 已关闭（web-verified 放弃·`WEB_VERIFIED_ENABLED` 长期 OFF）。**唯一剩项 = 展示标签重打标 follow-up**（`source_type→retrieved_from_web`·功能已正确·仅 trace/展示标签待改）→ **并入 M1 T7**（#3 source_type 降 trace·同域）：显式挂在 [S2 §2.9.5 M1 状态表「AO 展示标签 follow-up」行](../roadmap/S2.md)（⏸️挂起·别无声留），随 T7 验收一并处理·**不再单独占 lettered slot**。保留本条位置作诊断轨迹追溯。
- **状态（2026-06-26 对齐 · 原 2026-06-24 重定性）**: ✅ **主体已了结 —— PR1 [#160](https://github.com/JunoChenZt/subagent-for-investment/pull/160) 已交付（合 main `2a63aa4`）· PR2 [#161](https://github.com/JunoChenZt/subagent-for-investment/pull/161) 已关闭（2026-06-26·未合·web-verified 路放弃·`WEB_VERIFIED_ENABLED` 长期 OFF）· 仅剩展示标签重打标 follow-up（⏸️ 挂起，见下「展示标签 follow-up」条）**。〔原标「🔄 进行中（SESSION 1，state 级）」已 superseded——主体 PR1/PR2 均已收口、不再「进行中」。〕state 级修法的诊断轨迹保留如下：原 backlog "ds_researcher prompt 改 + 字段映射" 修法方向**证伪**——一手追踪（origin/main tracked run + [base.py:905](../../src/committee/agents/base.py)）证实 web_search 数据**根本不进 `ctx.references`**（域名在 analyst 调 `run_tool_agent` 没传 `return_tool_outputs=True` 就被丢），非"prompt 没填 watermark"。真修法 = **state 级接 provenance 链路**（analyst 改 return + 新 state 字段 reducer + fact `numeric_value` + confidence 路由，对齐 R-5 域名印证、不冒充 verified）。真值源 [docs/plans/AO-decomposition.md](../plans/AO-decomposition.md)。**run-D 12 条 `audit_inconclusive` 经一手核：主体即此病**（被误标 `common_context` 的 web 数据，见 [[source-type-label-not-provenance]]）。
- **强度**: 🔴 高优（fund_mgr 八步的 confidence 派生 / 散文门控的输入污染源）
- **PR1 进度（2026-06-25，`auto/AO` worktree）**: AO.1 web_provenance 捕获+reducer（`177f9e9`）/ AO.2 `numeric_value`（`cf9d6a8`）/ AO.3 confidence 按 `audit_passed` 分流·PR1 封顶 sourced（`6663764`）/ AO.4 集成+replay（`0664c3a`），全量 2240 passed。效果：web 检索数字从 `unavailable`→`sourced`；`verified` 锁 `WEB_VERIFIED_ENABLED=False` 留 PR2。**PR1 #160 已合 main `2a63aa4`**。
- **PR2 状态（2026-06-26 用户裁决·已关闭）**: PR2 [#161](https://github.com/JunoChenZt/subagent-for-investment/pull/161)（曾拟翻 `WEB_VERIFIED_ENABLED=True` 放开 web 数字进 verified）→ 🚫 **已关闭（CLOSED·未合·`WEB_VERIFIED_ENABLED` 长期保持 OFF·web-verified 路放弃）**。**为什么关、非烂尾**：经评估 —— ① web 数据本就是最不可信的源，升 verified（承重、不打码、进 prose）性价比低；② 翻 flag 碰北极星红线（放开未充分核实的网上数字进报告），收益不抵风险；③ 支柱1 已由小修 #162 独立修好、main 处安全态（web 数字封顶 `sourced`/打码、不影响决策质量），无放开紧迫；④ 代码在 #161 分支历史可查，将来若真要做不必从头重写。严审发现的印证池跨 fact 未 scope 缝（全系统老洞）详 [DEFECT-R5-02](#defect-r5-02-corroboration-印证池未按-fact-scope--不相干-fact-共享常见整数巧合凑成-verified🔴-阻塞-web-verified-放开)（小修已堵支柱1）。子域名残留 = [DEFECT-R5-03](#defect-r5-03-域名归一化无-etld1--同发行方子域被当两独立源🟡-低暴露往后排)（🟡·不再随 PR2）。
- **⚠️ 展示标签 follow-up（PR1 延后·显式记录·别无声留）**: run-D 那 12 条 fact 的 `source_type` 当前**标错**——标成 `retrieved_from_common_context`（资料库），**实为 web_search 拿回的网上数据**。AO **功能修复已正确**（分流 key 在 `audit_passed` 非标签，confidence 派生不受标签影响）；**仅展示/trace 用的 `source_type→retrieved_from_web` 标签改写待补**（要在 `_derive_all_confidence` 内对 state `FactInventoryItem` 做 in-place mutation，持久化语义需单独验）。**触发**：PR1 合 main 后 / 或 PR2 一并。用户 2026-06-25 拍定走 follow-up 但要求显式记此、不无声留。见 [[source-type-label-not-provenance]]。
- **背景**: 2026-06-11 fm-spec e2e seg8 audit 6.7% 通过率排查（30 facts 逐条分类）发现：**16/30 条 `audit_inconclusive` 全是 `source_type=retrieved` 且 `source_role=None` / `primary_source=None` / `watermarks=[]`——溯源字段全 None**。内容核查（f1 Q1 营收 194.96 亿 +192% / f5 PE(TTM) 88 倍 97 分位 / f6 一致预期 EPS 26.87 元）**全是真实可查数据**，与 seg2 evidence_log 一致（fundamentals 6/6 都有 source 在场）。同节点能正确处理 `retrieved_from_common_context`（4 条带水印通过）和 `inferred`（2 条带水印的推导）——**故障范围明确：仅对通过 web_search 拿回的 retrieved 数据丢溯源**。
- **后果（直接威胁八步 e2e 信号）**：
  - 步骤 2a 查证清单：无 source 影响 criticality 判定
  - 步骤 3' confidence 派生：22 条 inconclusive 走 `model_prior` 路径（结构性、非真不可信）
  - 步骤 5' 散文门控：confidence ≠ verified → 散文精确数字被定性化
  - **fm-spec 红项验收受污染**：fund_mgr 跑出"大量 model_prior + 散文定性化严重"不能算到八步头上——是上游污染的下游表现，不是 R-7/A1 阳性证据
- **修法方向**: ds_researcher 整理 fact 时把 evidence_log 的 source（即使是 web_search 拿回的财经站）填进 `source_role` + `primary_source` 字段、生成 ad-hoc watermark；或在 ds_merge 阶段做溯源回灌。
- **触发条件**: fm-spec seg9 e2e 完成后立即（红项判定需要排除此污染源时即触发）；或下一次任何动 ds_researcher prompt / pass0 schema 时一并。
- **进入时点**: 2026-06-11（fm-spec seg8 排查，用户指示记档）
- **预估工作量**: 中（ds_researcher prompt 改 + facts schema 字段映射 + 测试）

---

### AP. wisburg payload 编号粒度错位 — REF#W-NNNN 子集匹配缺失（🟡 P2）✅ CLOSED 2026-08-06 (close-by-merge → [BI](#bi-wisburg-只取研报标题全链无人读正文--半句话成了承重数字的依据2026-08-03-全链回归-e2e-findings-33-逐条过时立账)·保留位置)

> **✅ 2026-08-06 CLOSED —— 并入 BI，非「问题消失」**（完整 triage 处置）。
>
> **触发条件形式满足但实质无事可做**：本条触发条件写「下次动 wisburg source **或 audit 匹配逻辑**时一并」，
> [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 大改 audit 匹配逻辑 = 形式满足；
> 但那条路对应的**修法 B 早在 06-24 已撤**，其落点 `_extract_ref_id` 又被 #226 连同测试删除 → audit 侧这条路已死透。
>
> **⚠️ 实质问题仍在，故不是 close-by-supersede**：2026-08-06 复核 [wisburg_source.py](../../src/committee/common_context/sources/wisburg_source.py) 确认
> `_parse_tool_result` 仍把整批研报拍平成**单个 payload dict** → 「20 篇塌成 1 个 `REF#W`」原封不动，#226 未触及。
> **若按 close-by-supersede 关掉，会埋掉一个活的登记层缺陷。**
>
> **处置 = 并入 [BI](#bi-wisburg-只取研报标题全链无人读正文--半句话成了承重数字的依据2026-08-03-全链回归-e2e-findings-33-逐条过时立账)**：同数据源 / 同触发条件 / 同前置调查（`discover_tools()`），
> 且 BI 的"取正文"必然要重构 per-report 登记 —— 拆 ref 是取正文的**必要伴生改动**而非独立可选项。
> 残留问题的完整描述、连带动作、以及"MCP 无取正文能力时拆 ref 这半仍独立成立"的边界，**已全文写入 BI 条目**。
> 本条正文以下保持 point-in-time 不改。

- **状态（2026-06-24）**: ⏸️ **降级挂起**。"子集匹配缺失"框定**证伪**（origin/main tracked run 对账：全 run **0 个 `audit_partial_support`**、analyst 引 `[REF#W-007][85180]` 两独立 bracket 非 `REF#W-85180`、`_extract_ref_id` 对裸内部 ID 静默丢弃）。残留真问题 = wisburg/RSS **bundle 粗粒度编号**（20 篇塌成 1 个 `REF#W`），但 run-D 上几乎无样本（那 12 条 inconclusive 实为 AO web 误标）。修法 A（拆 ref）/B（子集匹配）撤；待有真实 per-report 引用的 run 再评估是否值得拆 bundle。**AP 与 AO 各走各 PR、不共享代码。**
- **强度**: 🟡 P2（schema 设计缺陷，非阻塞；与 AO 一同污染 audit 通过率，但量小且不影响八步主路径）
- **背景**: 2026-06-11 同次 seg8 排查发现：6/30 条 `audit_inconclusive` 引用 `REF#W-85180/88939/89530/89931/84831` —— **5 个不重复编号全部存在于 wisburg payload 的 20 篇研报列表里**（payload 文本含 `[80957]/[84656]/[85180]/...` 共 20 个 ID）。seg1 把整个 20 篇列表登记为**单个 `REF#W-005`**，analyst 按研报内部 ID 引用 → audit 在顶层 ref_id 集找不到 → inconclusive。
- **后果**: 6 条本来该 `audit_passed` 的 fact 被标 inconclusive，间接拉低 audit 通过率；下游 confidence 派生同 AO 一样把它们打成 model_prior。
- **修法方向（两选一）**:
  - **A**：seg1 注册时把 20 篇研报展开成 `REF#W-005-1` ~ `REF#W-005-20`，每篇独立 ref
  - **B**：audit_node 的 `_extract_ref_id` 支持子集匹配——若 `REF#W-NNNN` 的 NNNN 在某个 REF#W-XXX 的 payload 文本中，视为 matched
    〔**2026-08-06 补**：修法 B 早已随本条 06-24 降级一并撤；其落点 `_extract_ref_id` 已于 [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) **连同测试删除**（T11 后零生产调用·认章统一走 [`stamp_families.split_stamps`](../../src/committee/facts/stamp_families.py)）。将来若真要做子集匹配，落点改为 `split_stamps` 或 audit 侧新零件，**不要回去找那个函数**。〕
  - 建议 A（更显式、下游 reference_appendix 渲染更清晰）
- **触发条件**: 下次动 common_context wisburg source 或 audit 匹配逻辑时一并；或与 AO 合并一轮处理。
- **进入时点**: 2026-06-11（fm-spec seg8 排查，用户指示记档）
- **预估工作量**: 小（方案 A：wisburg source 输出层改 + 1-2 测试；方案 B：_extract_ref_id 加子集匹配 + 1-2 测试）

---

### DEFECT-A3-01. 机器层 prose_gate_status 与字段可信度信号不同源 — 价位全抹自检缺失（🔴 高优）

- **状态**: ✅ **CLOSED 2026-06-23 — 已修 + e2e hot 验过 + 已合 main @ `5885fe7`（#144 解封）**。e2e hot CLEAN PASS（2026-06-15 @ `33ec49a`：构造 seg9 注入 BUY+三价位 → 真步5'抹 model_prior → 真 scan → `prose_gate_status=degraded`，价位全抹告警 fire）。已知边界（不挡结案）：自然 SELL-无价位 run 走 verified 边界档=正确收窄；BUY 类 present-but-gated 自然触发档仍 hot 真空（与 VERDICT watch-list 一致）。**保留位置**（fm-refactor defect 家族，下方 supersede 注记留作 SEG9-VERDICT 时效追溯）。实际修法 = `_derive_prose_gate_status` 机械派生（scan 跑过 + ≥1 verified 承重价位 才 `verified`，否则 `degraded`〔⚠️ **判据已于 2026-07-22 由 GATE-ROUTE G2 改为「≥1 承重价位仍带实际 level」**（[#192](https://github.com/JunoChenZt/subagent-for-investment/pull/192)·随价位门控 (b) 同步）·本行描述的是修复当时形态〕），与下方"修法方向"所提 `_apply_prose_gate` 价位段形态略异，以 `e607278` commit 为准。
- **supersede 注记（SEG9-VERDICT 判读时效）**: 本条目下方 **背景 / 报告层补位 / 不同源含义 / 修法方向**，及 [SEG9-VERDICT](../observations/fm-refactor-spec/run-zhongji-fundamental-20260611/SEG9-VERDICT-2026-06-11.md) 中 R-3 / prose_gate / DEFECT-A3-01 相关判读，均对应 A3-01 修复**前**的 `2d96924`（VERDICT 首部分支锚点即 `@2d96924`）；已被 `e607278` supersede，对修复后版本不再成立。下次 #144 解封判读须重评这些条目"修了 A3-01 后是否仍成立"——尤其 VERDICT 中 `prose_gate_status=verified` 不降级的论断（line 67 / 160）与 R-3 行（line 196），修复后"价位全抹"场景应翻 `degraded`（`e607278` 单测已覆盖，e2e 未复验）。ADDENDUM 内容（opus 调用粒度 / R-6 闸门读法注解）与 A3-01 无关，不在 supersede 范围。
- **强度**: 🔴 高优（spec R-3 实证缺陷；价位是危险级最高的输出维度）
- **背景**: 2026-06-11 fm-spec seg9 首跑实证（[SEG9-VERDICT](../observations/fm-refactor-spec/run-zhongji-fundamental-20260611/SEG9-VERDICT-2026-06-11.md) + [ADDENDUM](../observations/fm-refactor-spec/run-zhongji-fundamental-20260611/SEG9-VERDICT-2026-06-11-ADDENDUM.md)）。execution_plan 三类价位（entry/stop_loss/take_profit）全部 low/high/level=null（confidence 全 None 走 model_prior 兜底分支），`enforcement_log` 37 条全为 `prose-gate-5'` 散文层定性替换，**无任何价位全抹的专项告警条目**；同时 `prose_gate_status=verified` 不降级。即"机器层信号"完全不感知价位全抹这一异常状态。
- **报告层补位（不算修复）**: fund_mgr LLM 在 sec_5 主动告知"鉴于跨角色质疑 + 关键价位多为 model_prior，本次不输出精确买卖价格"——这是 LLM 自觉，**不是机器层自检机制**。一旦未来 prompt 变更/模型升级让此自觉行为消失，价位全抹会变成静默全抹（spec R-3 警告的"完美合规的废纸"形态）。
- **不同源含义**: 价位字段 confidence 信号在场（虽全 None）vs 机器状态信号（prose_gate_status=verified）— 两个本应同步的健康指标走的是不同代码路径，没有交叉校验。
- **修法方向**: 在 `_apply_prose_gate` 价位段或 step 8 装配前增加"全抹检测"——若价位字段全部 null（或 confidence ≠ verified 比例 ≥ 阈值），强制 `prose_gate_status="degraded"` 或新增 `price_gate_status="all_stripped"`，并在 enforcement_log 写 `price-gate-all-stripped` 条目供下游 + 渲染层消费。
- **触发条件**: fm-refactor 机械闭合维度结案前必须修；或下次 fm-spec 红项验证轮次时一并。
- **进入时点**: 2026-06-11（seg9 首跑实证）
- **预估工作量**: 小-中（_apply_prose_gate 加全抹检测 + prose_gate_status 增档 + 渲染层消费 + 2-3 测试覆盖各档转换）

---

### DEFECT-R10-01. debate closing 阶段 key_claims 抽取缺失（🟠 中高）

- **状态**: ✅ **CLOSED 2026-06-23 收口（独立 PR #153 已合 main @ `45de406`·2026-06-15；hot 验过 @ D seg6；#144 一并入主干 `5885fe7`）·保留位置**。prompt-only 修法（`bull/bear_closing` raw 加「收盘 key_claims 非空 ≥1 + §3.8 反编造」，**不动** `_CONTINUATION_GUIDE_DEBATE` 的 `[]`-许可 / schema / OBEY-2 消费端）经**独立冷审 PASS（cold 层）** → PR [#153](https://github.com/JunoChenZt/subagent-for-investment/pull/153) squash 合入 main @ `45de406`（在 fastapi pin #154 后的干净绿 CI 上合，非 override）。冷热边界：cold（prompt 断言 + 全量 pytest 2144 passed + import 来源防假绿）已验；**hot（模型实跑是否真填 closing key_claims）= seg6 e2e DEFERRED**（非阻断、fallback 安全=空则退回现状）。解锁 DEFECT-R10-02 输入端前置。详 [retro](../retro/S2/r10-01_2026-06-15.md)。
- **强度**: 🟠 中高（spec R-10 实证；blocks DEFECT-R10-02）
- **背景**: 2026-06-11 fm-spec seg6-debate3 实测：`bear/closing` 正文 1571 字完整、内容含实质论点（"我们错的唯一可能就是'这次真的不同了'"自承不确定性 dissent），但 `key_claims=[]` 空数组。`bull/closing` 同段 `key_claims=5` 正常。
- **后果**: 任何下游消费 debate turn 的 `key_claims` 做检索/匹配/反馈的逻辑（含 OBEY-2 unaddressed 扫描），对 closing 阶段 dissent 完全失明。
- **疑似根因方向（未深挖，留给修复任务）**: closing 阶段 debate prompt 可能未要求填充 key_claims 字段；或 schema 默认值 vs 模型实际输出格式不匹配；或 closing 与 opening/rebuttal 的 prompt 模板有结构差异
- **修法方向**: 排查 debate closing prompt 与 schema 对齐；若 prompt 缺失 key_claims 字段则补；若 LLM 输出格式问题则加 post-process 兜底从 content 自动提取要点；至少保证 bear/closing 与 bull/closing 在 key_claims 抽取上对称
- **触发条件**: 修 DEFECT-R10-02 前置；或 fm-spec 红项验证 R-10 完整闸门之前
- **进入时点**: 2026-06-11（seg9 首跑实证）
- **预估工作量**: 小（debate prompt 对齐 + 1-2 测试）
- **✅ 2026-06-16 hot 验过（D seg6，源验证级）**: bear closing key_claims **baseline 0 → mine 3**（真实病灶 A/B），3 条全实质（估值过高/1260H/供给假设）+ calls.jsonl 原始模型输出逐字=checkpoint 无失真。详 [D ledger seg6](../observations/fm-refactor-spec/D-hot-e2e-2026-06-16/LEDGER.md)。
- **⚠️ 残留边界观察（2026-06-16，存档不动代码）— contract []-许可 vs R10-01 强制非空**: R10-01 修法**刻意不动** `_CONTINUATION_GUIDE_DEBATE` 的 `[]`-许可（纯叙述展开段允许 key_claims 空，受 `test_continuation_guide_allows_pure_elaboration_exception` 保护=反编造安全属性）。seg6 实证此口子真会触发：bull closing **续写两 call** —— call#13 产 3 条 key_claims，**续写 call#14 `key_claims=[]` 空**（contract 允许），pipeline 最终合并取非空的 3 条 → **R10-01 不受影响（最终非空即可，bull/bear 第一段都有内容）**。**边界风险（当前非问题，存着）**：若某角色 closing **第一段（非续写段）就返空** 且无后续续写补 → `[]`-许可可能让 key_claims 漏空、绕过 R10-01 「收盘强制非空」意图。**触发条件**：未来再现 closing key_claims 空 → 先查此边界（第一段空 vs 续写段空）。当前 R10-01 强制非空只加在 raw prompt、未在 schema/contract 层硬 enforce，故口子理论存在。

### DEFECT-R10-02. OBEY-2 未驳 dissent 反馈在决策已生成后才拼入 user_base → 对决策层实质死代码（🟠 中高·spec R-10）

> ℹ️ **2026-06-30 housekeeping 补回条目头**：本条原内容紧接 DEFECT-R10-01 正文、缺独立 `### ` 头（§0.2 上方 on-deck 块 line 204 曾注"锚点从略·避免伪造"即因此）；本次**仅补 header、正文一字未动**。标题据下方背景/后果段忠实拟（OBEY-2 反馈拼入时机在决策已生成之后 = 实质死代码），非原始措辞。

- **状态**: ✅ **CLOSED 2026-06-23 — 三步已实现 + hot 验收达成 + 已合 main @ `5885fe7`（#144 解封）**。死代码判定冷审+热证据双向坐实（2026-06-15 @ `c845d18`）；选型 = A-2 + B + 决策后检测告警（A-1 自动重决 deferred S3/S4）；代码三步（原 `53159ae`/`a91b9f8`/`201ef43`，已随 #144 入主干）= S1 注入上移决策前+删死代码 / S2 覆盖面全 side+cross_check+少数派 / S3 `_uncovered_dissent`→enforcement_log 告警·不阻断/不改决策；24 新测试 + 全量 2185 passed。**hot 验收（D seg9）达成**：bear concern 真进决策被回应、改结论形状（vs baseline 凭空消失）。⚠️ **残留 follow-up 仍 OPEN（spin-out，不随本条 CLOSED）= 下方 cap-crowding 残留观察**（cap=15 + cross_check-first 挤出收盘/少数派 dissent，"待评估（跑完 D）" 现已触发 → 归 group B actionable）。**保留位置**（fm-refactor defect 家族）。详 [R10-02 冷审报告](../observations/fm-refactor-spec/r10-02-obey2-coldreview-2026-06-15.md)。
- **强度**: 🟠 中高（spec R-10 实证；**blocked-by DEFECT-R10-01**：即使修了本条，没有 closing key_claims 输入仍看不到 closing dissent —— 结构根因 `base.py` L2485 `if turn.side=="bear" and turn.key_claims:`，空 key_claims 整段跳过）
- **背景**: spec R-10 论述（[fm-decision-node-spec.md](../specs/fm-decision-node-spec.md)）：OBEY-2 把"未驳 dissent"反馈拼进 `user_base`（`base.py` @ `c845d18` L2491）发生在决策（L2464）**已生成之后**，此后 `user_base` 只被步骤6扩写（L2630）消费，review（步骤7）又只删不补——反馈永远到不了决策 pass。
- **2026-06-15 冷审修正（一手核实）**: 既有"enforcement_log 零条 OBEY-2"易被读成"从未触发"——**实为 OBEY-2 在 seg9 确实 fire 了**（calls.jsonl 标记串 `未驳 dissent（OBEY-2）` 出现在 **seq 18–22 全部 5 个 `fund_mgr_expand`**，决策 seq16 / 审阅 seq23–27 **均 0**）；"零条"只因 OBEY-2 不写 enforcement_log。死代码判定靠"触发了但产物只到扩写、进不了决策"（热证据钉死），非"没触发"。严重度边界：决策 prompt 仍含辩论摘要（seg9 走 pass0 `debate_summary` 压缩模式），非全盲；死掉丢失的是逐条 forcing-function + 收盘级 dissent，seg9 实证确有后果（bear closing 担忧未进 `dissenting_views`，留存 2 条皆 bull 视角）。
- **后果**: OBEY-2 对其声称目的（驱动决策层补回应；标记文本 L2492–2494 自陈"驳斥/纳入 trigger/降级决策"=决策级意图）实质死代码；spec R-10 "形式全有、实质为零"成立。
- **修法方向**（冷审校验后，详报告 §4）:
  - 选项 A（移到 decide 前）：⚠️ **字面移动不可行**——OBEY-2 算未驳靠比对决策产物 `dissenting_views`（L2479），决策前不存在（chicken-and-egg）。可行变体：**A-1 双轮决策**（决策→算未驳→带清单重提一次决策，最忠原意，代价 +1 opus 调用 ~$0.2–0.5/run）/ **A-2 无条件注入**（决策前把全部 bear key_claims 拼进决策 prompt，不增调用、最简，prompt 更吵）。
  - 选项 B（扩覆盖面 closing/opening/rebuttal + 少数派投票 + cross_check）：与时序**正交**，**单用不治死代码**，须与 A 或 C 组合；价值=补 spec R-10 "覆盖面仅 bear-side"。
  - 选项 C（review 放弃 strip-only 允许补 dissent）：⚠️ **远比"放开 flag"重**——`_review_expansions`(L2078) 现仅操作 sections、返回 sections、**零访问 FinalDecision**，且 step5 scan 在 step7 review **之前** → 补的 dissent 会**绕过 claim scan/audit**（开 R5 式未核验通道）+ 破 strip-only 安全不变量 + 须改返回类型扯动装配。blast radius 最大，**一律避开**。
  - **2026-06-15 加深核实重新框定推荐**（详报告 §8）：**前提** DECISION_PROMPT R4(prompts.py L126-128) 本就要求处置 dissent、原 OBEY-2 只是 nudge 非机器校验 → 取舍是 **nudge(A-2) vs 闭环校验(A-1)**，按目标分叉：目标=廉价送回信号→**A-2+B**（零结构扰动/零额外成本，但仍无机器校验）；目标=补 spec "无机器校验"缺口→**A-1+B**（条件性 +1 opus、侵蚀"3 次 opus"招牌 +~$0.2-0.5/run）。**✅ 2026-06-16 用户裁定 = A-2 + B + 决策后检测告警（不自动重决，仅写 enforcement_log 供人工注意+攒频率）；A-1 自动重决 deferred S3/S4 看告警频率再定**。
  - **移植无误伤（collateral check）**：注入后 `user_base` 唯一消费方=扩写(L2630)，扩写无 dissent 处理指令=inert；下游 `dissenting_views` 读者读最终输出字段非注入；`tests/` 零锁定 OBEY-2。→ 移/改注入不伤别处，但零回归护栏=修复须自带测试。
- **依赖**: DEFECT-R10-01 解锁后才能完整验证修复效果（否则 closing dissent 输入端就缺）；排序硬约束 = 先 R10-01 再本条。
- **触发条件**: DEFECT-R10-01 完成后；或 fm-spec 红项 R-10 完整闸门
- **进入时点**: 2026-06-11（seg9 首跑实证）；冷审 2026-06-15
- **预估工作量**: 中（设计抉择已备料 + 实现 + 完整 R-10 回归测试套件 + seg9 重跑热验证）
- **⚠️ 2026-06-16 残留边界观察（D seg9 前一手实算，存档不动代码）— A-2 注入 cap=15 + cross_check-first 挤出 closing/少数派 dissent**：
  `_collect_dissent_checklist`（base.py L2281）collection 顺序 = **cross_check_concerns → debate key_claims → 少数派票**，截断 `cap=15`。D run 实算（真函数喂 seg8 state）：**21 条 cross_check_concerns 按序收满 cap=15 → bear closing key_claims（R10-01 修的）+ 少数派票 reasoning 全被挤出注入清单**（注入的 15 条全是 cross_check）。**后果**：① R10-01 hot 验过收盘非空，但在 cross_check≥15 的 run 里收盘 dissent **不直达 A-2 注入**（R10-01 修复被 cap 截断、reach 受限）；② 少数派票 reasoning 同样进不了注入（虽 state.votes 带 reasoning，排在第三被截）。**缓解现状**：bear 三主题（估值/地缘/供给）仍 thematically 在那 15 条 cross_check + 决策另见 debate_block 的 bear_core_thesis 摘要 → 实质未全丢。**待评估（跑完 D）**：cap 该不该调高 / collection 顺序该不该让 debate-closing dissent 优先于 cross_check / closing+少数派该不该有独立保底名额。触发源：[D ledger §3 靶子订正](../observations/fm-refactor-spec/D-hot-e2e-2026-06-16/LEDGER.md)。
  **§0 重合检查（2026-06-16）**：查 AC（fund_mgr 不服从下游信号，CLOSED）= **非重复**——AC 管"决策无视已收到的信号"，本条管"信号被 cap 截断、根本没到决策面前"，两码事。本条 = `_collect_dissent_checklist` 自身 cap/ordering 的残留、**内属 OBEY-2/R10-02 机制** → 并入本条（R10-02），不另立 lettered 条目（避免踩冻结配额）。**⚠️ 不阻 #144 解封**：R10-02 核心功能（A-2 把 dissent 注入决策前，vs 老死代码 0 条）**仍 work**，cap 只限 reach（15 条 cross_check dissent 仍进了决策）；本条 = "注入覆盖面可再优化"的 follow-up，**非 R10-02 失效、非解封阻断项**。

---

### DEFECT-R5-01. 步3 verify 入场门可被精心伪造的 source URL 骗过标 verified（🔴 高优）

- **状态**: ✅ **CLOSED 2026-06-23 — 已修 + e2e 双档验证真堵 + 已合 main @ `5885fe7`（#144 解封）**（修法 @ 原 `c845d18`，已随 #144 入主干：FindingConfidence 5 档漏斗 + web 域名印证门控，B 档 9 verified→0、伪造域名 references 全 web-single/unverified）。**保留位置**（fm-refactor defect 家族，最严重红项=编 URL 骗 verified 门，留作追溯）。详 [R-5 FINDINGS](../observations/r5-garbage-injection-2026-06-12/FINDINGS.md)（2026-06-12 实证 **A 拒 B 引**）+ [A-reconciliation](../observations/r5-garbage-injection-2026-06-12/A-reconciliation.md)（修复对账 + §7 路线修正）。
- **强度**: 🔴 高优（触及"不确定性诚实"北极星——把没核实的伪造数字当已核实放进输出，是最危险失败模式；spec R-5 实证 + [SEG9-VERDICT](../observations/fm-refactor-spec/run-zhongji-fundamental-20260611/SEG9-VERDICT-2026-06-11.md) §3.3 点名要补的垃圾回流刀）
- **背景**: 2026-06-12 垃圾回流 e2e（resume seg9 decision @ `e607278`，mock 注入 web_search）。两档对照——A 档（野鸡域名 .tk/.xyz + 离谱数字 9999/PE3.2/2000亿）→ DeepSeek 主动识破标 `not_found`/`source=null`，**阴性**（0 verified、价位全抹、degraded）；B 档（权威域名 sina/cls/eastmoney + 贴真值数字 1152/1210/301.5亿）→ DeepSeek 当 source 转述，门标 **9 条 claim verified、`prose_gate_status=verified`、16 条信源附录引伪造 URL**，**阳性**。
- **根因**: `confidence_for_finding`（[facts/confidence.py:138](../../src/committee/facts/confidence.py)）标 verified 只需 `source` 非空 + `as_of` 新鲜，二者皆 DeepSeek 自填、**零机器对账**；`_run_verification`（[agents/base.py:1697](../../src/committee/agents/base.py)）传了 `return_tool_outputs=True` 却把实际检索内容 `data, _` **丢弃**，claimed source 从不与实检 URL 比对。冲突项尤甚——伪造 URL 充当"定论源"绕过第三道纪律 stale 封顶（甚至 DeepSeek 自评仅 `inferred` 的 finding，代码仍标 verified）。唯一实际防线 = DeepSeek 表面启发式怀疑（认野鸡 TLD + 离谱数字），可被高质量伪造击穿。
- **后果**: 搜索通道被污染/被控（返回伪造但格式正常的结果）时系统无法区分，伪造数字一路标 verified 进 prose（`{ref:vN}` 未打码）+ 信源附录。门**本身零判别力**（A 拒是 DeepSeek 拦的，非门），判别力全寄生于 DeepSeek 老实度。
- **修法方向**（详 FINDINGS §6，5 条）: ① 不丢 tool outputs，claimed source 对账实检 URL 集（仅挡凭空编 URL，挡不住 proxy 被控）；② 承重数字 verified 限已知权威域名白名单 + URL 可达校验；③ 数值健全性对账 DS-0/tushare 锚（破离谱数，破不了贴值伪造，需组合）；④ 跨源印证 ≥2 独立源；⑤ prompt-only 不解（DeepSeek 已如实转述，问题在代码门轻信）。需组合方有效。设计任务，修复 task entry 时定方案。
- **触发条件**: fm-refactor 机械闭合维度结案前必须评估（与 DEFECT-A3-01 同属 #144 解封前红项）；或下次 fm-spec 红项验证轮次一并。
- **进入时点**: 2026-06-12（R-5 垃圾回流 e2e 实证）
- **预估工作量**: 中-大（设计抉择 + 多层防御实现 + R-5 回归测试套件，含 A/B 两档 mock 复跑）
- **修复落地（2026-06-15 @ `c845d18`）**: FindingConfidence 改 5 档漏斗（verified 收紧为"≥2 不同域名 snippet 含一致数字"，web finding 限定，`VERIFIED_MIN_DOMAINS=2`）+ [`count_corroborating_domains`](../../src/committee/facts/verify.py)（确定性印证计数，不丢 tool_outputs）。**e2e 双档验证真堵**（[run-A](../observations/r5-garbage-injection-2026-06-12/run-A-postfix/)/[run-B-postfix](../observations/r5-garbage-injection-2026-06-12/run-B-postfix/)，新代码+mock）：B 档 9 verified→**0**、伪造数字全打码、`external_knowledge_refs=[]`、伪造域名 references 全 web-single/unverified；A 档全 unavailable 无回归；DS-0 audit_passed 未被 corroboration 门误伤（stale→sourced_outdated，新=旧）。单测 2161 passed。**修复 ≠ 解封 #144**（仍押 DEFECT-A3-01 + fm-八步 e2e/冷审/retro）。
- **已知残留（随修复接受）**: ① **Q5 多源伪造残余**——verified 门=域名计数+数字在场，控搜索代理者把同一伪造数字塞进 ≥2 个不同域名 snippet 仍可绕（门槛比"只凑域名数"高，非零）。② **定性 finding 核实另议**——无 numeric_value 的定性 finding 落 sourced（不假装核实）；"定性判断要不要某种 verified"是另一套机制，未做。③ **DS-0 scope 边界**——≥2 域名印证只接 web finding（`confidence_for_finding`），DS-0 走 audit 不动（治标不扩界）。**⚠️ 2026-06-25 更新**：AO(PR1) 后来把该机制扩到 DS-0（非 audit_passed → web_provenance 印证），跨了这条原边界；且印证池跨 fact 未 scope 的更深缝（非对抗巧合凑 verified）已单列 [DEFECT-R5-02](#defect-r5-02-corroboration-印证池未按-fact-scope--不相干-fact-共享常见整数巧合凑成-verified🔴-阻塞-web-verified-放开)（🔴 阻塞 web verified 放开）。④ **prose-gate str.replace 部分匹配残差**（非 R-5，既有边界）——dissenting_views 个别非 verified 数字未被 [`gate_prose_numbers`](../../src/committee/facts/confidence.py) 打码（value 字符串与正文不精确匹配，docstring 已记）。

---

### DEFECT-E2E-RESUME. 分段 e2e `--resume` 不干净跳过 — 每段重跑 macro+triage，动摇测试工具可信度（🟠 中高·harness 非 fm 节点）

- **状态**: ✅ **已修·合 main `af7b314`（PR #158·2026-06-24·squash）**〔2026-06-30 triage 对齐：原写"待 merge"已 stale——#158 当日即合，状态切 MERGED（R7·live 就地改）〕。根因钉死：reject 信号只活在两个**会丢**的地方（`report=None` 在 load 缺席、`triage_verdicts` 被 triage 重跑覆写）→ 多次 resume 每段重跑 macro（这解释了 seg4-9 每段重跑）。修法 = 新增持久 `rejected_roles` reducer 字段（**保持 report=None 零迁移**，放行门穷尽 6 消费端无一靠 None 认 reject）+ analyst skip 谓词读它 + C 文档如实化。triage 重跑是有意设计（防死循环）不动。
  - **与 A1.2 关系（2026-06-30 triage 厘清·别误并）**: 信源册 A1.2（`load_checkpoint` 补 `web_provenance`·合 `8b7bea6`/#164）修的是**同族另一支**——`load_checkpoint` 漏恢复 `web_provenance` → resume 后 web 印证掉 `unavailable`。两者同属 "load_checkpoint 不完整恢复 state" 家族、但**字段不同**（本条 = `rejected_roles` 那支 / A1.2 = `web_provenance` 那支），A1.2 明写"**镜像 `rejected_roles` 范式**"（沿用本条 #158 立的持久字段套路）。∴ **A1.2 ≠ close 本条的一块**，是用同范式修的姊妹洞；本条自身的 #158 已独立合并。
- **现象（一手实测）**: D run 分段跑，seg4/5/6/7/8/9 **每段 `--resume` 的 calls.jsonl 都含 `macro:3` + `triage_c:7` + `triage_e2:2`**（seq 从 1 重起、非 cumulative）= 每次 resume **重入 macro 分析师 + triage**，**与 [segmented-e2e-guide](../observations/e2e-runs/segmented-e2e-guide.md) 声称"resume 跳过已完成阶段"矛盾**。
- **后果（不只是浪费钱，重点在可信度）**:
  1. 浪费 compute（每段白跑 macro+triage ~10+ 调用）；
  2. **更重 —— 让分段跑不是干净的接续**：macro 弱模型 nondeterministic（连 [AA](#aa-rework-盲重试--triage-failure-notes-未反馈给-analyst-llm-✅-closed-2026-06-02-close-by-completion) scenarios 残留缺口），每段重跑可能抽到不同 macro 结果。**本 run 实锤**：seg1-8 macro 重跑均 drop（一路 7/8），**seg9 重跑碰巧 PASS → macro 复活（8/8）**，直接改了决策的 dissent 注入构成（4 条 macro "X视角" cross_check 挤进、换掉离线尾 4 条）。→ **"分段验收=每段在同一上游状态上接续"这个前提被打破**：同一 run 不同段看到的上游可能不一致 = **动摇分段 e2e 作为测试工具的可信度**（不止本 run，是工具层）。
- **待查根因**: LangGraph checkpoint resume 为何重入 macro+triage（reject-after-rework 的 drop 状态是否导致每次 resume 重入研究/triage 相 / 还是 resume 跳过逻辑更广的 bug）；macro nondeterminism 与 AA scenarios 缺口同源。
- **⚠️ 不挡 #144 合并**: 这是 **e2e 工具/harness 问题、非 fm 决策节点缺陷**；seg9 该验的八步在 **8/8 真输入上实际跑了**、产物在 main、R10-01（seg6 已验）/R10-02（用真注入清单可判）不受其动摇。是"测试工具可信度"的独立 follow-up，非解封阻断项。
- **触发源**: [D ledger seg9 对账](../observations/fm-refactor-spec/D-hot-e2e-2026-06-16/LEDGER.md)（2026-06-16）。**配额**: harness 类、不占 §1/§2 lettered 配额（同 DEFECT-* 族）。

---

### DEFECT-PROSE-GATE-SELF-ABRADE. prose-gate 误伤决策者自定行动数字（position_size 仓位数被当外部未核实数字抹）（🟠 中高·**fm 节点自身产物损坏**·挡不挡 #144 待用户裁）

- **状态**: ✅ **CLOSED 2026-06-23 — 已修 + 已合 main `5885fe7`（#144 解封）·保留位置**。修法 = cherry-pick `0dbf44c`（决策者自定行动数字豁免外部核实门，over-redact 修法②）+ `5f48e97`（数值碰撞 fail-safe 边界测试）进 #144，全量 2193 passed；与 under-redact 反向 bug（`6f88195`/R-2）同轮并入。〔原: 🆕 发现 2026-06-16，D hot-e2e seg9 实测，calls.jsonl 原文 + 读码坐实〕
- **现象（一手坐实）**: `fund_mgr_decide` 原始输出 position_size = "不超过满仓的**20%**"，final 被抹成"不超过满仓的**相关数值%**"；thesis 建仓价 1050/950/1350 散文层同被抹。claim_audits 实录 20/1050/950/1350/1200 全 `replaced=true, confidence=unavailable`。
- **机理（读码坐实）**: `confidence.allowed_numbers` 白名单 = **verified 外部 findings ∪ verified body 数字** → **漏了"决策者在 position_size/thesis 里自定的行动数字"**（20% 非外部 finding→unavailable→被 `gate_prose_numbers` 抹）。`_PROSE_SCAN_FIELDS`（base.py L1593）含 `position_size`、`_apply_prose_gate`（L2026）有 position_size 处置器 → 20% 真抹、**无结构化备份**。
- **附带不一致（同条记）**: `_PROSE_SCAN_FIELDS` 含 `execution_plan.reevaluate_triggers[].description`（被扫），但 `_apply_prose_gate`（L2018-2029）**无 reevaluate_triggers 处置分支→return False 不替换** → 价位 1050/950/1350 在 reevaluate_triggers **结构化幸存**（可执行）；但 **claim_audits 对它们记 replaced=true 是假记录**（实际未抹）。scan 范围 vs apply 范围不一致。
- **影响**: **非"决策没法照做"**——价位触发结构化可靠保留、可执行；entry/stop/tp=null 是 HOLD 设计非误抹。**真损失 = position_size 20% 仓位数**（用户面成"相关数值%"，仓位上限丢，仅留定性"保留底仓/等回调"+内部 R2≤25%）。**fail-safe**（过度抹除非伪造，不让决策更危险）。
- **正交性**: **不动摇 R10-01/R10-02 验证**（dissent 机制与 prose-gate 误抹正交）；是独立 prose-gate scope bug。
- **修法方向（任一/组合，prompt 或 code）**: ① `allowed_numbers` 纳入决策者自定行动数字（position_size/reevaluate_triggers 内 fm-prescribed 数字进白名单）；② position_size 从"外部核实门"豁免（它是 fm 处方、非外部待核 fact）；③ 修 scan/apply 范围不一致（reevaluate_triggers 要么都扫都抹、要么都不扫，并修 claim_audits 假记录）。**修复须自带回归测试**。
- **§0 查重**: 非 R5-01 残留④（那是 **under-redact** 漏抹/部分匹配 miss；本条是 **over-redact** 误伤，相反机理）。无重复。
- **挡 #144 判断（D 摆，用户裁）**: ✅ **已裁决 = 升 blocker④（第四道闸）→ 修复并入后解封**（fm 节点自身产物损坏打北极星"装备决策者" → 不减重，先修再解封）。两 prose-gate 反向 bug 修复经 code 冷审 + 定点 hot 验双过，随 #144 解封合 main（2026-06-23）。
- **触发源**: [D ledger §4.2 seg9](../observations/fm-refactor-spec/D-hot-e2e-2026-06-16/LEDGER.md)。**配额**: DEFECT-* 族、不占 lettered 配额。

---

### DEFECT-R5-02. corroboration 印证池未按 fact scope — 不相干 fact 共享常见整数巧合凑成 verified（🔴 阻塞 web verified 放开）

> **✅ CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— **支柱1 已修，剩余部分的前提已经不存在**：
> 小修（两路印证池按 fact/finding 自己来源收紧）已合 main `3e8dd6f`（[#162](https://github.com/JunoChenZt/subagent-for-investment/pull/162)）；
> 而余下部分的触发条件挂在「`WEB_VERIFIED_ENABLED` 翻 True 前 / PR2 [#161](https://github.com/JunoChenZt/subagent-for-investment/pull/161) 解锁前置」，
> **PR2 已于 2026-06-26 CLOSED、该 flag 长期 OFF、口径明定「关门非留门」** ⇒ 判据挂死信号（[§4.1](#41-新增-backlog-条目) 禁止形态）。
> 🔵 **顺带消一处早已存在的自相矛盾**：[number-provenance-endgame.md](number-provenance-endgame.md) 的分流表一直把本条列在「已 close」栏，
> 而 backlog 这边仍是活跃 —— 本次 close 使那处断言成真（该表同批已就地更正措辞）。
> **重开条件**：若将来重开「网页核实」这条路，本条须连同 [DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮) 一并重新设计（不是简单复活）。
> 〔以下正文为 point-in-time 记录，**一字未改**。〕

- **状态**: ✅ **小修(🩹)已完成·合并 main `3e8dd6f`（PR #162，2026-06-26）**。两路印证池按 fact/finding 自己来源收紧拔**支柱1**：G1 fund_mgr 路 [`_anchor_tool_outputs_by_source`](../../src/committee/agents/base.py)（按 `finding.source` URL 现场锚池、Option C 单次查零额外成本、run-D 锚定率 10/10）/ G2 DS-0 路按 `cited_by_roles` 收 `web_provenance`；反作弊 14 测试真堵（before/after 防假绿 + 镜像不误伤 + 边界 + golden audit_passed 不动）、全量 2254 绿。详 [retro](../retro/S2/R5-02-smallfix_2026-06-26.md)。**保留位置**（DEFECT 家族）。
  - **支柱2（语义层）= [DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮) 另记·不进本轮**；URL 锚锚漏残差 defer 建册（升级路径已登记）。
  - **对 PR2 [#161](https://github.com/JunoChenZt/subagent-for-investment/pull/161) 的影响**：PR2 = 🚫 **已关闭（2026-06-26·未合·web-verified 放弃·`WEB_VERIFIED_ENABLED` 长期 OFF）**。本小修拔支柱1（fund_mgr 生产路 Finding B）的价值**独立于 flag**、已落 main 生效；原"解锁 PR2 翻 flag"框架随 PR2 关闭已 moot（小修非"为翻 flag"而做，是堵生产活洞）。
- **决策（2026-06-25 用户拍·分步，别再翻案重证）**: 差距表"做多大"分叉定为**分步**、不一把梭（详 [信源册 sketch §四差距表](../plans/provenance-source-registry-sketch.md)）：
  - 🩹 **小修【现在做】= 本条**：只动差距表 **#6** —— 把 `count_corroborating_domains` 吃的池从大杂池收紧到"该 fact/finding 自己绑定的来源子集"，拔 **支柱1（池未 scope）**。**不建册、不动 ①②③④⑤ 登记结构、不改 schema、零 LLM。** 走 CLAUDE.md workflow 主链路。
  - 🏛️ **建册【已决定做·小修后重走流程定范围】**：从一而终终态（治本，**不再承担堵洞**）→ 见下方【信源册建册】条目。**做是定的、待评估的只是范围**；范围届时按真实现状重走流程定、**不照搬本轮 #1-5+8 / 理想态图**；小修 #6 收池作既成代码继承、不重做。〔**2026-06-26 已 superseded（point-in-time·正文不动）**：评估已完成、方向已批准、阶段 A 待开工——以【信源册建册】条目为准。〕
  - ⏭️ **语义层【另记·不进本轮】**：差距表 #7（拔支柱2）→ 见 [DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮)。先确定后判断、放小修之后。
  - **理由**: Finding B 此刻在 fund_mgr 路生产里漏（`confidence_for_finding` 无 flag 门控），小修最快止血且低风险；建册跨 schema/合并两套机制、理想态半仍是未核假设，不与止血绑死。
- **强度**: 🔴 阻塞后续（触"不确定性诚实"北极星——**非对抗、高频、自动**把没核实数字标 verified 进 prose；同 [DEFECT-R5-01](#defect-r5-01-步3-verify-入场门可被精心伪造的-source-url-骗过标-verified🔴-高优) 家族最严重失败模式）。**与 R5-01 残留①（Q5 对抗 proxy）本质不同**：那条要控搜索代理塞同一假数字；本条**无需任何对抗者**——纯结构性巧合凑数。
- **机理（读 tracked 代码坐实）**: [`count_corroborating_domains`](../../src/committee/facts/verify.py)（verify.py:61）数"池里 snippet 含 ≈numeric_value（rel_tol 2%）的不同域名数",但**喂进去的池是跨 fact 的全量 tool_outputs、匹配纯数值无实体/语义校验**。两条调用路都喂未按 fact 过滤的池：① fund_mgr findings ← 一次 agent 跑整张清单的 `verify_tool_outputs`（[base.py:1751](../../src/committee/agents/base.py) / 2610）；② DS-0 web facts ← 8 分析师全量 `web_provenance`（[base.py:1785](../../src/committee/agents/base.py) / 2642）。→ 一个 round-number fact（value=100，±2% 窗口 98–102）可被池里 2 个**完全无关**域名的近似数字（某 PE/某价/某百分比/某计数）误凑成 verified。round number 在财务事实里常见 → **高频自动发生**。
- **边界（坐实于设计记录，非推断）= 全系统老洞、非 web 独有**: R-5 reconciliation §5 当年明写"印证按每次搜索数域名、非按每条事实，finding↔tool_outputs **无关联键**",**显式选路线A(池内数域名)、defer 路线B(每条 fact 绑自己来源 + 跨源数值一致)**，理由"工作量大/可能跨 session/改 schema"（[A-reconciliation 行13/110/121-122/148](../observations/r5-garbage-injection-2026-06-12/A-reconciliation.md)）。R5-01 修复随之活在 fund_mgr `confidence_for_finding` 路（2026-06-15 起）；R5-01 残留③明写"≥2 域名只接 web finding、DS-0 走 audit 不动"——**AO(PR1) 把该机制【扩】到 DS-0、并喂更大池**，PR2 让它承重。
- **后果**: 没核实的数字一路标 verified 进 prose（`{ref}` 不打码）+ 进 `allowed_numbers` 白名单 → 决策报告把巧合凑出的数字当铁板事实呈现。直接打北极星。
- **修法方向（🩹 小修 = 差距表 #6，跨两路同修、消费端收池、不改 `count_corroborating_domains` 签名、不改 schema、零 LLM）**:
  - **DS-0 web 路**：[base.py:1785](../../src/committee/agents/base.py) 数印证前，按 `role ∈ item.cited_by_roles` 过滤 `web_provenance` 再喂计数（用现有弱键 `cited_by_roles`，role 级 scope；**读现有 state 字段、不动 state.py schema**）。
  - **fund_mgr 路**：`_run_verification`（[base.py:1706](../../src/committee/agents/base.py)）改逐项查证、`item→outputs` **运行时临时绑定**（不改 `VerificationFinding` schema、不持久化、不碰 state），按 finding 自己那份子池计数。代价 = 查证 LLM 调用 1 次→N 次（逐 high 项）。**否掉"单次查 + 字符串模糊归属"**（承重门不用会误判的机制，用户已定）。
  - **绑定键现状（设计 pass 一手坐实，origin/main tracked）**：`VerificationFinding` 仅 `source: str|None` 无回链键（[decision.py:86](../../src/committee/schemas/decision.py)）；`_run_verification` 一次跑整张清单返回扁平 `tool_outputs`、无 per-item tag → fund_mgr 路绑定键真缺，逐项查证是唯一确定性最小修法。
  - 配**反作弊回归测试**（设计 [§5](../plans/corroboration-per-fact-binding-design.md)）：两条不相干 fact 共享常见整数(100/101) → 各停 `sourced`/打码、**绝不 verified**；镜像用例（真 2 独立域名仍 verified，不误伤）；fund_mgr 路对称用例。约束：零 LLM / 只 == 或上行绝不下行 / golden audit_passed 逐字节不动。会变的测试（预期）：`test_web_fact_with_numeric_and_provenance_reaches_sourced` fixture 无 `cited_by_roles` → 收紧后掉 unavailable，补 `cited_by_roles` 即可（绑定键 load-bearing 活证据）。
  - 详设计 [corroboration-per-fact-binding-design.md](../plans/corroboration-per-fact-binding-design.md) + 上位视角 [provenance-source-registry-sketch.md](../plans/provenance-source-registry-sketch.md)。
- **触发条件**: **`WEB_VERIFIED_ENABLED` 翻 True 前必须修 + 测真堵**（PR2 #161 解锁前置）；或下一次 fm-spec 红项验证轮次一并。**排期待用户定**。
- **进入时点**: 2026-06-25（AO PR2 严审）
- **预估工作量（🩹 小修，建册/语义层另计）**: 中 —— DS-0 路小（1 处过滤）；fund_mgr 路中（`_run_verification` 逐项重构 + `item→outputs` 临时态穿线，**不改 schema、不碰 state.py**，代价在查证 N× LLM 调用）+ 反作弊回归测试套件。**配额**: DEFECT-* 族、不占 lettered 配额。

---

### DEFECT-R5-03. 域名归一化无 eTLD+1 — 同发行方子域被当两独立源（🟡 低暴露·往后排）

- **状态**: 🆕 **OPEN（2026-06-25，AO PR2 严审发现）**。**不卡 PR2 / 不卡 web verified**（门槛高于 R5-02）。PR2 描述残留①已自陈此条。
- **强度**: 🟡 影响质量（低暴露：需同一发行方两个子域**同时上榜且各含一致数字**才触发；非高频、要非对抗偶发才有意义；但确是门的真弱点）。
- **机理**: [`_domain_of`](../../src/committee/facts/verify.py)（verify.py:33）只剥 `www./m./mobile./amp.` 前缀且 `break` 只剥一个，**无 public-suffix 归一化** → `finance.sina.com.cn` ≠ `sina.com.cn` 算 2 个不同域名。单一发行方两子域可凑 ≥2 门。搜索引擎现实会一起返回同发行方多子域 → 非对抗也偶发。
- **后果**: 同发行方多子域虚增交叉印证数，配合 [DEFECT-R5-02](#defect-r5-02-corroboration-印证池未按-fact-scope--不相干-fact-共享常见整数巧合凑成-verified🔴-阻塞-web-verified-放开) 一起把 verified 门做松。独立看暴露小。
- **修法方向**: `_domain_of` 引 eTLD+1 归一化（public-suffix 列表依赖，或务实的"末两段 + `co.uk` 等例外表"）。R-5 当年明确 **declined PSL 依赖**——这条改动面最大、需依赖评估。**随 R5-02 大线一并处理或单列**。
- **触发条件（2026-06-26 建册评估后定）**: **单列**（用户拍定）——与出处存储**正交**（建册改的是喂进计数函数的池，本条改的是计数函数内部 `_domain_of` 域名归一化，同文件不同函数）+ **PSL 依赖决策独立**（R-5 当年 declined PSL），**不随建册**；或引入 public-suffix 依赖的其它需求出现时。〔原"随建册或单列"已 superseded 为"单列"。〕
- **进入时点**: 2026-06-25（AO PR2 严审）
- **预估工作量**: 小-中（`_domain_of` 改 + 依赖评估 + 测试）。**配额**: DEFECT-* 族、不占 lettered 配额。

---

### 信源册建册. 出处收敛单一贯穿真值源（✅ **大任务 M1 主体完成·close 2026-07-10**·三表定型·11 子任务收口·T10(#4)剥离为独立挂起条目·全链 e2e 13/0/0）

> **✅ 2026-07-01 正式立账 M1（口径校正 session·本 banner 为 live 主体·下方 2026-06-30 及更早均为 point-in-time 记录·正文不动）**：信源册正式成立为**大任务 M1**，理想态 = **三表**（① `internal_structured` 内源·不动 / ② `external_websearch` 外源·**已升格落地册** `external_websearch_ledger`·搜回后于 **fund_mgr 决策节点步骤 3″ 单点固化**〔方案 C·**非"搜回即写"**·下方 stub『理想化三表』那句"搜回即写"已被方案 C 细化·不锚行号〕 / ③ `references_appendix` 展示表·**回内源 only**〔**#165/A2 已 CLOSED 2026-07-02·superseded**；"外源不进表③"由 **T3.1 结构焊死**（signature-lock + 焊死注释·commit `a730e35`·本节点 PR 合入后于 main 生效）——**不再"碰巧"**·非"外源污染待撤"〕）。**#5 物理隔离铁律不变**：confidence 唯一读表②·**audit/gate 永不读表②**（越过=滑 M2·当场拦）。信任层不变（外源封顶 `sourced`·永不 verified·PR2 已关）。
>
> **M1 正式子任务 T1–T10（老实标成熟度·占位不包装成正式子任务）**：
>
> | T | 内容 | 状态 |
> |---|---|---|
> | T1 | 外源册落地（fund_mgr 步骤 3″ 固化·方案 C）| ✅ 已合 `5338de2` |
> | T2 | confidence 改读固化册（全消费端含 gate 逐字节·封顶 sourced 不变）| ✅ 已合 `5338de2` |
> | T3 | 撤外源·回内源（废/重做 A2/#165 ✅CLOSED·把"外源不进表③"从"碰巧没合"固化为**设计焊死**·**非撤已进去的外源**：外源现未进附录）| ✅ **DONE·PR [#170](https://github.com/JunoChenZt/subagent-for-investment/pull/170) merged main `c450ff2`（2026-07-02）**：T3.1 焊死·T3.2 fresh-run e2e（美光·9 段·**表③ 0 外源 wN**·quality gate 12/1/0）·T3.3 收 #165；retro [T3_2026-07-02](../retro/S2/T3_2026-07-02.md)；**不闭合 D1**（病根→[DEFECT-D1-ROOT](#defect-d1-root-gate-读展示表表③而非内源真值表表①-安全闸可被任意非-unverified-条目稀释含纯内源-sourced--过期源🔴-高优d1-病根独立于-m1)）|
> | T4 | 报告展示层合并（③内源 v#·f# + ②外源 wN·不同实体）| ✅ **已合 main `f3268e6`（[PR #178](https://github.com/JunoChenZt/subagent-for-investment/pull/178)·2026-07-09·用户拍 merge）**：外源 wN 受控合进表③（`_build_references_appendix` 加 `external_ledger` 入参·gate 已脱钩不重开 D1）+ 外源 `is_outdated` 按 as_of 现算（sanitize→staleness→缺/非法/未来/超 other 窗口=True）+ `render_appendix_zh` 分实体两表（内部核验信源 / 外部网络信源·后者带"未经结构化核验"caveat + 检索方列显 origin）。红线守：外源不并 internal_structured·credibility 取册内 tier 永不 verified。DoD 2514 绿 + archive replay 259 测 + 端到端探针；冷审 🟡 已修 + /review 清理 #2/#3/#4。**✅ 已补验 e2e**（`f4eb2da`·复用 T11 seg8-pass0 跑 decision 段·177 refs=67 内源+110 外源 wN〔analyst 80/fund_mgr 30·全 web-corroborated 无 verified〕·两表渲染 + T12 archive→gate 13/0/0·[EVIDENCE](../observations/m1-t4-t12-e2e/EVIDENCE.md)）。retro=[docs/retro/S2/M1-T4_2026-07-09.md](../retro/S2/M1-T4_2026-07-09.md) |
> | T5 | #165 处置（留复用口·撤回逻辑或可部分留）| ✅ **DONE 2026-07-02**：#165 CLOSED（superseded·未合）；A2 纯 additive **无撤回逻辑可 salvage**；分支 `auto/A2` **保留不删**（存 A2 代码 + decomposition 作参考）|
> | T6 | #2 引用绑 ref（内外两册）| ✅ **方案A 内源半已合 main `4b16138`（[#180](https://github.com/JunoChenZt/subagent-for-investment/pull/180)·2026-07-10·squash·CI 绿·用户拍 merge）**：外源半 T11 已闭合（数字级 wN）；内源半核心洞已堵——DS-0 `{ref:fX}` 链结构上本已工作（同名空间绑定），唯一裂缝 = `_build_references_appendix` DS-0 循环对脏 `as_of`（LLM 产裸 str→严格 AsOfDate fail-fast）撞 `except` **静默丢条目**→正文引用存活但清单查无此条 = 断链；修 = DS-0 循环 `item.as_of or ""`→`sanitize_as_of(item.as_of)`（镜像 T4 外源半·verdict-neutral·表③已与 gate 脱钩）。引用绑定不变量现由 sanitize 保证。**方案B 泛化校验网**（cited⊆appendix 软 flag）经用户裁决**刻意未叠**（选最小修·未来需要可另立）。DoD 全量 2533 绿 + mutation 防假绿 + 代码级探针；/code-review high 两 finder 0 correctness bug。retro [M1-T6](../retro/S2/M1-T6_2026-07-09.md) |
> | T7 | #3 source_type 降 trace（会师 AO follow-up）| ✅ **已合 main `7070ab6`（[#181](https://github.com/JunoChenZt/subagent-for-investment/pull/181)·2026-07-10）**：(a) `schemas/pass0.py` SOURCE_TYPE 枚举加 trace-only 守护注释（不参与承重路由·系统认 audit_status）+ (b) 活 prompt `prompts/pass0_prompt.py` 补 `retrieved_from_web`（best-effort trace 诚实性·不喂闸）；保 audit 分支；含 AO 展示标签 follow-up。retro [M1-T7](../retro/S2/M1-T7_2026-07-10.md) |
> | T8 | A3 audit guard 注释（M1 不改写 audit 逻辑）| ✅ **已合 main `4a8c10c`（2026-07-10）**：`_build_ref_lookup` 加 #5 红线守护注释（外源册 `external_websearch_ledger` 永不进此 lookup·第二层认知防线·纯注释零逻辑改动·import OK + audit 测试 103 绿）|
> | T9 | 锚漏核实门（一手核落地册粒度真覆盖锚漏场景·核实了才从 #4 划掉）| ✅ **核实完成（2026-07-10·纯只读·零码·结论=不覆盖·锚漏留 #4）**：一手核**实际落地码**（非 A1.4 设计意图）——外源册登记粒度 = per-result + 搜索组标签 `group`（[verify.py:301-310](../../src/committee/facts/verify.py)），G1 印证锚仍按"含 `f.source` URL 的搜索组"锚（[base.py:1868-1871](../../src/committee/agents/base.py)·搜索级）→ **忠实复刻老单 URL 锚·含已知锚漏·verdict-neutral**（[base.py:1864-1867](../../src/committee/agents/base.py) 焊死 count_from_ledger==经典）。**∴「册粒度覆盖锚漏」推断为假**（正是本门「是推断·守住」要防的乐观误判）→ 锚漏**不划掉·留 [#4](#信源册建册-出处收敛单一贯穿真值源✅-大任务-m1-主体完成close-2026-07-10三表定型11-子任务收口t104剥离为独立挂起条目全链-e2e-1300)**。**根因（why 还在）**：锚收窄到"同一次搜索"是为堵 [DEFECT-R5-02](#defect-r5-02-corroboration-印证池未按-fact-scope--不相干-fact-共享常见整数巧合凑成-verified🔴-阻塞-web-verified-放开) 支柱1（大杂池→不相干 fact 共享常见整数**巧合凑 verified**·危险方向·撞北极星）；放宽治锚漏=放回危险毛病→两害相权取保守。精确修（#4 claim/URL 级）贵（DS-0 路 URL 已蒸发·需改 Phase-1 analyst 或模糊 join·[reeval §3 假设1](../plans/provenance-source-registry-reeval-2026-06-26.md)）且只换"少误伤"（锚漏=过度打码=**安全方向**）→ 按判据 defer 到 T10。**两条 verified 路澄清（防"数字永不 verified"误解）**：① 结构化机构数据经 audit 水印盖 verified（**主路**·不走网页域名计数·锚漏无关）；② 网页数字经 ≥2 不同域名佐证（`count_corroborating_domains` 数**不同域名**·一次搜索本就返回多域名·非"永不 verified"·锚漏只在佐证跨搜索分散时少数）·且当前 `WEB_VERIFIED_ENABLED=False` 封顶 sourced。∴ 锚漏 = 无害边缘残差·不卡主路·非普遍（run-D 锚定率 10/10·T11 e2e 12/14） |
> | T10 | #4 重判（暂缓带判据）| 🔵 **剥离为独立挂起条目**（2026-07-10 M1 close·见本文件 [T10 / #4 条目](#t10--4-claimurl-级精确绑定🔵-挂起测量驱动2026-07-10-从已-close-的-m1-剥离)·测量驱动·实测点1 已采 N=1 未触发）|
> | 附 | G1 #5 命根守护 / D1 gate 读展示表〔症状非病根·M1 只做"外源不进表③"·不改 gate 读哪表〕/ D2 措辞校正〔本 session 已做〕/ D3=R5-04 / D4=R5-03 | 保留 |
> | **T11** | **每数字量纲发唯一编号 + DS-0 正确 citing（层② check① 下游需求·2026-07-03 立）** | ✅ **已合 main（[PR #175](https://github.com/JunoChenZt/subagent-for-investment/pull/175)·squash `18357ff`·2026-07-07）**·含两轮冷审修复〔认章工具库 stamp_families·详见下方 2026-07-06 落账 note〕 |
> | **T12** | **段式 e2e 末段自动产出 archive（quality gate 直接可吃·2026-07-06 立·用户拍）**：末段 `is_last` 时复用现成装箱机 [`graph._build_result`](../../src/committee/graph.py)（整跑收尾同一函数）自动落 `archive-from-final.json` 到 run 目录 + [segmented-e2e-guide "末段通过后"](../observations/e2e-runs/segmented-e2e-guide.md) 补 checkpoint→archive 转换命令说明。出处 = T11.4 实踩：gate 期望 archive 形状、段式只产 checkpoint、指南画了路没铺砖（手工转换已验通·`load_checkpoint`+`_build_result`·13/0/0）。纯 additive 不动判定·低风险 | ✅ **已合 main `8f3fb79`（[#179](https://github.com/JunoChenZt/subagent-for-investment/pull/179)·2026-07-09·用户拍 merge）**：`_write_final_archive` best-effort（失败 log.warning + 返回 None·checkpoint 是 provenance 源·不炸已跑完的 run）+ cli 末段打印 archive 路径&gate 命令 + guide「末段通过后」铺砖。2518 绿；/review 3 finder→修 #1（写盘 try/except）·#2 常量名 by-design·#3 由 #1 覆盖。retro=[docs/retro/S2/M1-T12_2026-07-09.md](../retro/S2/M1-T12_2026-07-09.md)。**✅ 已补验 e2e**（`f4eb2da`·decision 段自动产 archive → quality gate **13/0/0**·[EVIDENCE](../observations/m1-t4-t12-e2e/EVIDENCE.md)）|
>
> **✅ T11 落账（2026-07-06·四 goal 全过·fresh-run e2e + quality gate 13/0/0）**：实现 = 盖章 seam（搜索结果落地即盖数字级编号 `[W#role-batch-rIdx#nK]`·喂 LLM 打标版 / raw 保真**两路分离**·kill-switch `COMMITTEE_WEB_NUMBER_STAMPING`）+ 外源册条目 additive 两键 `number_registry`/`stamp_id`（等价单测**零改动**保绿·confidence 判定零扰动）+ citing 两族规范（删"给 PE 贴 REF#Y"错误示范·推算免检 = 空水印 + `source_type=inferred`·**不加新 schema 字段**·rules_d D1/D2 认两族解除乱贴压力·D3-D5 保持表①域内）。**e2e 实证**（[EVIDENCE.md](../observations/m1-t11-e2e/EVIDENCE.md)·NVDA 9 段）：登记 320 数字·raw 零污染·**零编造**·DS facts 可锚定 **12/14 vs 基线 0%**·推算免检 12/12·残差错配 2 条**确定性可判** = **层② check① 解锁前提兑现**（对账步/接线归层② 相位 2·#5 铁律议题随之后移）。**T6 边界连带（防条目互等）**：T11 = T6"外源绑法"半已闭合 → **T6 剩内源半**（#2 引用绑 ref 的内源 `{ref:fX}` 链）。**计划外发现**：audit_passed 存在性泡沫 26→3（乱贴白拿的信任被戳破·喂 [AUDIT-3CHECK](#audit-3check-audit-三检查实现数字--日期--来源❌-cancelled--2026-07-14-用户拍彻底砍)）。
>
> **🆕 T11 详（2026-07-03 立·核心症结 = web 数据无量纲唯一编号·point-in-time·已由上条兑现）**：目标 = 给**每个数字量纲发唯一编号 + data_key**（表①补 pe/eps… 或表②外源数字按量纲发号）+ **DS-0 正确 citing**（不再把 P/E/PEG/EPS 乱贴表①价格编号 `REF#Y-007`）。**出处 + 承重方** = 层② EXEC-FLOOR **check①（证据搬运数量级错）阻塞于此**（[EXEC-FLOOR 实现 handoff](../handoff/层2-闸门真值信号-实现-handoff-2026-07-03.md)）：fresh-run e2e（NVDA BUY）实证 P/E 42.27・PEG 0.43・EPS 6.53 等联网/分析数字**全无量纲编号·全挂 `REF#Y-007`=price 194.83** → check① 无法把 `numeric_value` 配到同量纲源值（裸 ref_id 白比 / 按号查则 PE 42.27 vs price 194.83=4.6x **疯狂假阳**·与真搬运错确定性分不开）。dataflow §15：web 数据本无水印=出处断点根源。**归属** = T6（#2 引用绑 ref）+ T7（#3 出处真值）延伸；**M1 推进 T6/T7 时把"解锁层② check①"计入验收收益**。🔴 层② 侧已焊注"绝不按 ref_id 硬查 references"（commit `436d8be`）——修在闸这层必假阳、根治须本 M1。
>
> **口径校正 session 已做（2026-07-01）**：D2 全仓措辞（双册→三表·派生视图/尚未落码→已落码·从两册导出→表③回内源）在 [dataflow §15.5](../pipeline/dataflow-whole-pipeline.md) / [S2 §2.9.5](../roadmap/S2.md) / `verify.py` docstring / [fm-spec](../specs/fm-decision-node-spec.md) / 本条已改齐；旧设计文档（reeval/sketch/A1-decomposition）标 superseded 保留（可回溯·非删）。**未做**：T3–T10 实现（承重·另起 session）、H4 配额对齐〔**查无独立定义留档·不硬做·核到账再动**〕、fresh-run e2e（M1 e2e 收尾单排）。

> **🔴 2026-07-01 核查2 结论（T3 开工第一步·只读核查·会=坐实·未动一行码·用户裁决=先如实登记别动手·T3 是否仍做待议）**：T3 handoff §4 把"findings 是否自带 web credibility 稀释 gate"定为 gating 项——**核出来 = 会**。机理：`_build_references_appendix`（[base.py:2343](../../src/committee/agents/base.py) findings 循环 + [base.py:2358](../../src/committee/agents/base.py) DS-0 循环）经映射 `_CONFIDENCE_TO_CREDIBILITY`（[base.py:1592](../../src/committee/agents/base.py)）把 `verified→verified`、`sourced→web-single`、`sourced_outdated→web-single`、`stale(遗留)→web-single` —— 即**纯内源** verification finding / DS-0 fact 只要有源新鲜（哪怕单域名、哪怕过期）就产出**非-`unverified`** 附录条目，**根本不经 A2 外源 wN append**。gate（[risk_gate.py:302](../../src/committee/agents/risk_gate.py)）`all(e.credibility=="unverified")` 对任一这种条目即变 `False` → **不 fire**。
> - **∴ "撤外源 = 外源不进表③ = 表③只剩 unverified"前提不成立**。表③里的开放-web 可信度（`web-single`/`web-corroborated`/`verified`）**经 findings→appendix 这条独立循环已在场**，与 A2 无关。深核② 的 BEFORE 态（内源全 unverified）里撤外源够用，但只要有**一条** `sourced`+ 内源 finding，gate 就被稀释——**这条路撤外源关不掉**。
> - **最刺眼子案例**：`sourced_outdated`（源**过期**）与遗留 `stale` 也映到 `web-single` = 非-unverified → **一条过期单源即压住 AD.7/C 安全地板**。这是纯 gate 判据/表③装配弱点，跟外源无关。
> - **定性 = 内源稀释 = gate 判据（+表③ credibility 装配）病根·超 M1 边界**（M1 焊死"不改 gate 读哪表/怎么判"）。关它须动 findings→appendix 的 credibility 映射，或动 gate 判据（哪些档算"该拦的 unverified"）——两者都在 M1 外。**按纪律未自行扩去改任何码**（handoff §6 + 用户 2026-07-01 裁决）。
> - **对 T3 的影响（用户 2026-07-01 拍：T3 要做·窄活）**：撤外源（废/重做 A2、堵 wN append 路 + 收 #165）= 守 #5 红线延伸「外源连展示表都别碰判据面」，管的是**外源这条路**，有价值 → **T3 要做**。但**账面写死：T3 不闭合 D1**（去掉一个稀释向量·不足闭合；病根 = 内源稀释 + gate 读展示表 = [DEFECT-D1-ROOT](#defect-d1-root-gate-读展示表表③而非内源真值表表①-安全闸可被任意非-unverified-条目稀释含纯内源-sourced--过期源🔴-高优d1-病根独立于-m1)·独立处置）。**不照 handoff『撤外源即闭合 D1』旧假设开工**；承重·真改判定方向 → 走完整 workflow（risk-judgment 高 → decomposition → 用户确认 → 实现·DoD 含 gate 端点 + fresh-run e2e）。下方 2026-06-30 及更早 banner 里"D1·潜在·A2 合入才 live""隐患未 live"等**均为核查2 前记录·被本 note 修正**（正文不动·别改历史）。
> - **📌 病根已独立立账（用户 2026-07-01 裁决：如实登记成正式任务·不让 T3/M1 顺手吞）= [DEFECT-D1-ROOT](#defect-d1-root-gate-读展示表表③而非内源真值表表①-安全闸可被任意非-unverified-条目稀释含纯内源-sourced--过期源🔴-高优d1-病根独立于-m1)**：gate 读表③（展示表）而非表①（内源真值）= D1 病根，与外源无关、撤外源关不掉。**M1 只 own 症状（外源触发·T3）·不 own 病根**（改 gate 读哪表/怎么判 = 独立议题·独立设计+e2e）。是否改成读表① = 未定设计决定，DEFECT-D1-ROOT 里列了三条候选路、不预设答案。

> **🔬 2026-06-30 diff 深核完 + T1/T2 设计成对（结果落账·均未写码·下一棒=实现）**：diff 深核两项已跑（只读 + 一处只读测量），T1（落点=C）+ T2（换读）扩写已成对成形，完整结果 + handoff = [信源册-M1-diff-深核-结果-handoff.md](../handoff/信源册-M1-diff-深核-结果-handoff.md)。live 状态变更：
> - **深核② risk_gate 暴露坐实 🔴（before/after 实测·非推断）**：场景「内源全不可信 + 跑过 web」下，外源 wN(web-corroborated/web-single) append 进 `references_appendix` → `risk_gate.py:302` 的 `all(credibility=="unverified")` 变 False → **AD.7/C 安全地板被压制**（BEFORE 撤外源态 hard-block FIRE·SELL→HOLD / AFTER A2 态 no·SELL 保留可执行价位）→ **判定翻转·不安全方向**。∴ **T3（撤外源·回内源）= 承重必做**·#165 现状合并会真改判定·D1 非纯症状（外源→gate 实际翻转路·靶子 `risk_gate.py:283-293`）。滑 M2 信号已标红报用户。gate 节点 `graph.py:256` live-wire = 生产非死码。
> - **深核① T1 落点 = 方案 C 拍定（用户 2026-06-30）**：外源持久落地册落 = **fund_mgr 决策节点单点固化**（步骤 3 后插「步骤 3″」·两源 web_provenance+verify_tool_outputs 用 `derive_external_websearch_ledger` 合并成册·单写者 wN 顺序不撞车·普通 state 字段不需 reducer·verify_tool_outputs 从此不再 ephemeral）。**T1 只加写路不换读 = verdict-neutral**；换读命门留 T2。两子项：tier 字段补齐(五锚-3·按 group 盖) + resume 一行(load_checkpoint 照抄 A1.2 范式·dump 全量自动·封顶只存显示档永不 verified)。T1 扩写详 handoff §4。〔原 stub「T1 落点 = diff 时核定·不固化」**已 superseded = C**；方案 A 拒因 wN 撞车+verify 入 state、方案 B 拒因 raw+derived 混淆+漏 verify。〕
> - **深核① 续：T2 换读设计成形（用户 2026-06-30 批准落账·仍未写码）**：换读靶点 = `_derive_all_confidence` 两处 derive 调用改读固化册。**关键判别器 = T1 记账时盖的显式来源章 `origin ∈ {"analyst","fund_mgr"}`**（**判别器硬化·用户 2026-06-30 拍**：原设计靠"`verify_tool_outputs` dict 无 role 键→合并册 fund_mgr role=None"分拣=**"捡漏捡来的对"**·将来谁给 verify 补 role 键就悄无声息失灵·正好错在命门→改为 T1 盖显式 origin、T2 读 origin；退一步最低防线=测试钉死 fund_mgr 派生条目 origin=='fund_mgr'）。DS-0 路平凡安全（role∉cited 自动排除）；**🔴 G1 路三载点一个不能错**（① `origin=="fund_mgr"` 预滤 load-bearing〔硬化前=role is None〕 / ② URL `_norm` 归一 / ③ group 搜索级锚）= T2 最危险处、实现重点盯防。**DoD 含 gate 端点**（`should_hard_block_unverified_execution` 显式断言相同·不许靠 credibility 传导替代=闭合 A2 漏验）+ **对抗反证**（打坏换读 replay 必须发散·防假绿）+ flag 双态。**命名统一锁 `external_websearch_ledger` + 来源章键 `origin`**（不另起 external_ledger 简写）。origin 硬化 verdict-neutral（选中集同旧 role=None、count 不读 origin）。详 handoff §4 子项③ / §5。
> - **🔒 边界写死（防将来误读·用户点名）：T2 做完 gate 翻转 bug 仍在**。T2 只换 confidence 读源、**不碰 gate 读哪张表**；深核② 那条外源→gate 翻转（不安全方向）**要 T3（撤外源）才真堵**。T2 gate 端点验证 = 「换读不额外恶化 gate」**非「gate 已修」**。**任何人别把「T2 验过 gate 端点」误读成「gate bug 已修」——治它的是 T3。**
> - **下一棒（未做·刻意·均未写码）**：T1/T2 **实现**（按 workflow 承重工程）→ 用户授权后**不可逆收尾重构**（删旧立新·成立正式大任务 M1·T1=C 填实 + T6 外源绑法填实 + D2 措辞校正 + H4 配额对齐）。**删除未授权前不动**（北极星红线区）。

> **🔄 2026-06-30 升格 reframe（M1 已拍 · STUB 防漂移 · 完整规划待后续 session · 非 R7 措辞改而是定位翻案）**：信源册"外源"定位**翻案**——**原"`external_websearch` = `web_provenance` 的派生视图"前提作废**。外源**升格为一等独立册**（**M1**·用户 2026-06-30 拍）：搜回即写入·权威源；**仍与 `internal_structured`/`references` 分立 · audit 仍物理不读 · #5 红线保持**；**信任层不变**（web 仍封顶 `sourced`·不升 verified·PR2 已关）。升格 = 结构/存储层，≠ 信任层。连带（本 stub 只钉决策 + HOLD，**不动正文、不全仓校正**）：
> - **A2 PR [#165](https://github.com/JunoChenZt/subagent-for-investment/pull/165) = 🚧 HOLD（不合）**：#8（`references_appendix` 外源半从 `build_web_references` **派生**）建在"外源=衍生视图"**错前提**上。**"verdict-affecting bug" 的具体形态（diff 第一步只读核查 code 坐实·2026-06-30）= #8 把外源 wN（credibility=web-corroborated/web-single）append 进 `references_appendix`，而 `risk_gate.py:283-293` 实读该附录查 web 信源 credibility → 外源经附录流进 risk_gate（一条判定/gate 路），A2 retro/PR 只验了 confidence 路、漏验 gate 路**（= 前提错"外源当展示派生视图随便 append"的代码落点·复现 point 2"A2 栽在漏 gate"）→ 升格后 **#8 按 M1 重做**。〔原写"非独立代码 bug"已被本核查精确化：不是另一个独立 bug，是前提错的具体 verdict-affecting 路径。〕
> - **已合的前提项待重审**：#1（A1.1 派生零件）/ **A1.2（load_checkpoint·resume·封顶 sourced）** / A1.3 · A1.4（印证读**派生视图**）均建在衍生视图前提（已合 `8b7bea6`/#164）→ M1 下"派生"要倒成"搜回即写一等册"，**A1.1 大概率返工**、A1.3/A1.4 读路改。**A1.2（diff 第一步核查补漏·原 stub 漏列）**：持久落地册若成独立 state 字段，则其 dump/load/resume 处理要扩（现 A1.2 只 restore `web_provenance`）；且 A1.2 的"resume 后不升 verified·封顶 sourced" = **M1 信任层不变命门的一部分**，T2 命门须覆盖 resume 路（此项 M1 影响 contingent on T1 落点）。
> - **"衍生视图/派生视图"措辞全仓待校正（owner 拍措辞·本 stub 不动）**：reeval §4.1 / [dataflow §15.5](../pipeline/dataflow-whole-pipeline.md) / [S2 §2.9.5](../roadmap/S2.md) / 本条下方正文 / A1·A2 decomposition 都把外源写成"派生/衍生视图"——这是原 H2（"尚未落码"）的**升级版校正**（定位翻案，非措辞滞后）。
> - **A4 不存在**（澄清·防再立节点：曾被口头提及，三份文档 + 全 retro 查无，确认无此节点）。
> - **risk_gate 读 `references_appendix`（展示表/视图）当判据 = 待立独立 backlog 条目**（信源册同主题"展示视图非真值源"·成文草稿仓库内查无·待起草）。**diff 第一步核查 code 坐实（2026-06-30）：`risk_gate.py:283-293` 确实 `web_refs = list(decision.references_appendix)` 查 credibility=="unverified"——这正是外源能碰到 gate 的通道。∴ D1 不是纯"症状"：它是外源→gate 的实际路径；T3（撤外源·回内源）= #5/G1 的实际执行（把外源从 gate 可读的附录里拿掉）；T2 命门"含 gate"的具体靶子 = `risk_gate.py:283-293`。**
> - **🗺️ M1 / T1–T10 规划已成形（2026-06-30 用户拍 · diff 基线 · 非固化设计 · 嵌此防丢）**：〔⚠️ **SUPERSEDED·2026-07-09**：本段为规划期 point-in-time 快照，live 状态以上方 M1 子任务表为准（T1/T2/T3/T11/T4 + D1-ROOT 已合·T5–T10 pending）；下方 T3/T4 措辞保留原文不动（R7 历史不改正文）〕**理想化三表** = ① `internal_structured`（不动）/ ② `external_websearch`（**派生视图→搜回即写的持久落地册**·M1 核心高风险）/ ③ `references_appendix`（**回内源 only**·撤 A2 外源）。**数据流图铁律** = #5 物理隔离线：confidence 是唯一读表②的判定者；**audit/gate 永不读表②**（越过=滑 M2·当场拦）。**todolist**：
>   - 🔴 **T1** 表②落地（返工 #1·先加写路 additive·**落点 state/一等字段 = diff 时核定·本 stub 不固化**）→ 🔴 **T2** confidence 改读落地册（返工 A1.3/A1.4 读路·**命门**：before/after **全消费端含 gate** 比对·`findings_confidence`/`ds_confidence_map`/`verified` 逐字节同·封顶 sourced 不变）〔**T1/T2 两步拆分·保留**〕
>   - 🟠 **T3** #8/A2 重做（撤外源·回内源）/ **T4** 报告展示层合并（③内源 v#·f# + ②外源 wN·不同实体）/ **T5** #165 HOLD=废/重做（**留复用口**：撤回逻辑或可部分留·任务定后决定）
>   - 🟢 **T6** #2 引用绑 ref（内外两册·**外源绑法 diff 时定·现在不定**）/ **T7** #3 source_type 降 trace（会师 AO follow-up）/ **T8** A3 audit guard 注释（M1 不改写）
>   - 🔍 **T9** 锚漏核实（**是推断·守住**：一手核实落地册登记粒度真覆盖锚漏场景，核实了才从 #4 划掉）→ **T10** #4 重判（暂缓带判据）
>   - 🛡️ **G1** #5 命根贯穿守护；⏸️ **D1** risk_gate 读展示表（**症状非病根**·M1 只做"外源不进表③"·不改 gate 读哪表）/ **D2** 措辞校正 / **D3** R5-04 / **D4** R5-03
>   - **diff session 执行序（2026-06-30 用户细化）**：① **第一步 = 只读核查盘点**——三份文档（reeval / A1·A2 decomposition / backlog）全过、再一手核全旧项 + 归属（**别漏锚漏这类寄生项**）、确认本 stub 映射没漏没错（补"散落各处会漏"的担心）；② diff 完（**T1 落点定死**）后**一次性重构**：**删除/归并所有旧信源册条目** → 正式成立**大任务 M1**（T1–T10 为子任务·**落点 + 绑法填实、不再"待定"**）→ 连带 **D2 文档校正**（reeval/dataflow/§2.9.5 "衍生视图"措辞）+ **H4 配额对齐**（原独立押后·现并入一次成型）→ **一次成型落 S2/backlog/handoff**。本轮只到此 stub（不做②）。**深核 session 启动提示词 = [信源册-M1-diff-深核-handoff.md](../handoff/信源册-M1-diff-深核-handoff.md)（2026-06-30·只读深核 only·指回本 stub）。**
> - **本条 = STUB**：只钉 M1 决策 + #165 HOLD + T1–T10 规划骨架 + 防漂移指针，**不固化 T1 落点 / T6 外源绑法 / 升格完整设计**（避免推断设计写进账本→新 session 做错节点·R5）。**完整 M1 升格 = 另起 session：先 diff 核 T1 落点 → 落正式账 → 按 workflow 实现（承重·改 state/schema 级）**。下方所有"派生视图/衍生视图/A2 pending/待 /goal"等为 reframe 前记录，**正文不动（待校正项已列上）**。
> **⚠️ 2026-06-30 状态切换（R7 收口·A1 已合）**：A1（信源册建册·阶段A 地基节点：外源册零件 A1.1 + load_checkpoint 补 web_provenance A1.2 + G2/G1 印证读册 A1.3/A1.4·4 goal）已 **squash 合 `8b7bea6`（PR #164·2026-06-30·worktree 全量 2285 passed + 探针 PASS·4 review 锚见下导航/锚区）**。**本条 live 状态 = 🔵 阶段A 实现中：A1 已合·A2(#8 附录从册导出)/A3(#2 引用绑 ref + #3 source_type 降 trace) pending（A1 已解锁依赖）**。下方 2026-06-29 及更早 banner / "待 /goal 实现" / "尚未写码" 等为 point-in-time 记录，**正文不动（别改历史）**。
> **⚠️ 2026-06-29 状态切换（R7 收口）**：本条从"已评估·方向已批准·阶段 A 待开工" → **"阶段 A 只读设计 pass 已定·命名锁定·待 /goal 实现（分 A1/A2/A3）"**。设计 pass 自核到 origin/main tracked 一手代码；4 决策已拍（独立字段不并 references / source_type 降 trace 保 audit 分支 / `load_checkpoint` 顺手补 `web_provenance` / URL 锚持久化含 fund_mgr verify outputs）；命名锁定 `internal_structured`/`external_websearch`。目标态全程图 = [dataflow §15.5](../pipeline/dataflow-whole-pipeline.md) + [S2 §2.9.5](../roadmap/S2.md)。**仍未写码**——下方"阶段 A 设计 pass 锁定"段为新增 live；其余正文为评估期记录（仍准确、映射阶段 A）。
> **⚠️ 2026-06-26 状态切换（R7 收口·point-in-time）**：本条从"已决定做·待评估范围" → "已评估完成·方向已批准·阶段 A 待开工"。评估真值源 = [provenance-source-registry-reeval-2026-06-26.md](../plans/provenance-source-registry-reeval-2026-06-26.md)（三结论 + #5 砍除红线 + 阶段 B 判据）。下方"重走评估流程定范围""届时重核"等旧口径已 superseded（评估已做完）；保留升级路径段（仍准确、映射阶段 A）。

- **状态**: 🔵 **阶段 A 实现中：A1 已合 `8b7bea6`（PR #164·2026-06-30·squash·worktree 2285 passed + 探针 PASS）·A2(#8)/A3(#2/#3) pending（A1 已解锁）**（设计 pass 2026-06-29·评估 2026-06-26）。A1 四 goal = 外源册零件(A1.1) + load_checkpoint 补 web_provenance(A1.2·resume 不丢·封顶 sourced) + G2/G1 印证读册(A1.3/A1.4·换存取不换原则·逐字节同)。量级 = **轻-中（偏轻）**：state 最硬地基已铺且已证（`web_provenance` 已是 8 节点并发写的 `Annotated[list,add]` reducer 字段、resume 幂等已解）、旧图最重的 #5 已砍、#6 已 DONE。是 [DEFECT-R5-02 分步决策](#defect-r5-02-corroboration-印证池未按-fact-scope--不相干-fact-共享常见整数巧合凑成-verified🔴-阻塞-web-verified-放开) 的**终态目标**。**A1 已动 state（`load_checkpoint`）+ code（`verify.py`/`base.py`）并合入主干（#164）；A2/A3 仍 docs 待开工。**（下方"设计 pass = docs-only 未动代码"等为 2026-06-29 设计期 point-in-time 记录，正文不动。）
- **价值 / 职责边界（2026-06-25 定·2026-06-26 修）**: 小修已**独立堵洞**（拔支柱1），**建册不再承担堵洞职责**。建册价值 = **纯治本**（出处从一而终、`web_provenance` 入 `external_websearch` 外源册【与 `internal_structured` 并立·不合并·审计不可见·见下"红线代码落点"】、结构更干净）。**⚠️ 原"为'网上数据升 verified 经审核'做准备 / 给 PR2 翻 flag 干净承重底座"职责已取消**（2026-06-26 PR2 #161 关闭、web-verified 放弃）——建册不再为放开 web verified 服务。
- **🚫 #5（audit 读 web）永久砍除红线（2026-06-26 用户拍·钉死防将来捡回）**: **#5（让 audit 读统一册 / 给 web 数据发 `audit_passed`）已永久砍除，非漏做。** 原因：系统中 `audit_passed`（若新鲜）直达 verified、**且不受 `WEB_VERIFIED_ENABLED` 门控**（[confidence.py](../../src/committee/facts/confidence.py) `audit_gate` 自核坐实）。故"让 audit 读 web → 给 web 发 `audit_passed`" = 给 web 数据开一条**绕过已关闭 PR2 的 verified 后门**，等于重开 PR2 关掉的那条路、碰北极星红线。**任何未来的建册实现都不得给 web fact 发 `audit_passed`**——这是红线、不是优化取舍。（切斯特顿篱笆反向：刻意拆掉的设计写明为什么拆，免得后人装回去。）
- **🚧 阶段 A 设计 pass 锁定（2026-06-29 用户拍·新增 live·目标态非现状）**:
  - **命名锁定 = 双册 `internal_structured` / `external_websearch`**（总概念「信源册」）。**🔗 概念名 ↔ 代码实体（标死）**：`internal_structured`（内源·结构化半）**↔ 已存在实体** `CommonContext.references`+`watermarks`（**此刻就在·就在承重**：来源台账 + audit **唯一读它**判 `audit_passed`·阶段A **不重命名**、文档统一称内源册半）；`external_websearch`（外源·联网搜半）**↔ 目标态派生视图·【尚未落码】**——`web_provenance` 此刻在（存原始 web 出处）、但派生出的"外源册" **A1.1 才建**（复用 0 调用的 `build_web_references`），**非既存实体·勿读成"已存在"**。命名要点：**名字本身是红线提醒器**——"external_websearch"一看即"外部联网搜·审计不认证"，合并即语义违和。
  - **🔴 红线代码落点（结构性焊死 #5）**: 外源册**绝不并进** `internal_structured`/`ctx.references`；audit 的 [`_build_ref_lookup`](../../src/committee/agents/audit_node.py) 只遍历内源册、外源册永不进此 lookup。一个架构决定焊死三件：audit 物理看不到 web → 无法发 `audit_passed`（#5 后门关死）+ 独立 `wN` 命名空间绕开"W 被 wisburg 占"+ 消解评估假设3 唯一硬冲突（audit 匹配语义）。落地时 audit 侧加注释作第二层认知防线。
  - **🔑 概念改名 ≠ 代码字段改名（标死防两种误解）**: `internal_structured`/`external_websearch` 是**概念层归类别名**，**不是**要把代码字段 rename 成这俩名。`references` 字段名**永久保留**——① 别"为对齐概念名去重构改名"（误以为该改名去重构）；② 也不是"碰不得不敢动"（误以为冻结）：A3 会**受控演进** `references` 用法（#2 引用绑定 / #3 出处真值来源改读册），但**保 audit 分支 + 反作弊兜底**。这正是"建册 = 扩展现有雏形非从零"的另一面：实体不换名、概念层归位、用法受控演进。
  - **4 决策已拍**: ① 独立字段不并 references（红线·见上）；② `source_type` 降 trace 但**保留 audit 的 `DATA_INSUFFICIENT`/`inferred` 分支**（claim 类型门控、与出处真值正交，[audit_node.py:34-40](../../src/committee/agents/audit_node.py)）；③ `load_checkpoint` **顺手补 `web_provenance`**（决定3(a)·镜像 `rejected_roles` 范式·resume 不丢、顺带修既存 resume bug：resumed run 的 web 印证从 unavailable 回升 sourced·封顶 sourced 永不 verified）；④ URL 锚持久化**含 fund_mgr `verify_tool_outputs` 入册**（今全 ephemeral；A1 **忠实持久化当前锚行为·verdict-neutral**）。
  - **🚩 锚漏切出 → #4（2026-06-29 A1 拆解设计 pass·用户裁 (a) 采纳）**: 任务原写"URL 锚持久化顺手修锚漏"，但 A1 拆解时自核 `_anchor_tool_outputs_by_source` 机理坐实——**修锚漏不顺手**：要把"分散在另一次搜索的印证域名"收进该 finding 的池，只有两条路，一条**退回大杂池**（重开 #162 刚堵的支柱1）、一条**让 DeepSeek 每 finding 吐全部印证 URL / 逐项搜**（改 verify 输出或流程 = 就是已暂缓的 **#4 claim/URL 级精确绑定**）。∴ **修锚漏 ⊆ #4**，从 A1 切出、并入 #4/阶段B（判据见下阶段B）。**A1 = 忠实持久化当前 G1 单 URL 锚行为（verdict-neutral）**，不修锚漏。元方法沉淀：先核机理再判，别把上层措辞（评估"顺手"）当已证。
  - **PR 拆分（按 #1/#2/#3/#8 可独立验·G1/G2 再拆开）**: **A1**（#1 web 入册 + URL锚持久化 + load_checkpoint·触承重读路、判定不变·before/after replay 逐字节同）**再拆 4 goal**：A1.1 外源册派生零件（纯函数·零 LLM）/ A1.2 load_checkpoint 补 web_provenance（断点续跑那处·严限恢复时重载 web 出处）/ A1.3 G2(DS-0 路) 印证读册 / A1.4 G1(fund_mgr 路) 锚读册（忠实·不修锚漏）；**A2** = #8 附录从两册导出（纯派生·接通 build_web_references）；**A3** = #2 引用绑 ref + #3 source_type 降 trace（保 audit 分支）**+ 🚩 A1.1 切来：audit `_build_ref_lookup` guard 注释**（A1 forbid 碰 audit_node.py·用户 2026-06-29 裁 (b) 挪此·A3 拆解必须纳入清单别漏）。依赖序 A1.1→{A1.2,A1.3,A1.4}→A2/A3；安全序 A1.1→A1.2→A1.3→A1.4→A2→A3。拆解 = [A1 decomposition](../plans/信源册-阶段A-A1-decomposition.md)；全程图 = [dataflow §15.5](../pipeline/dataflow-whole-pipeline.md) / [S2 §2.9.5](../roadmap/S2.md)。
  - **真开工 / 进度**: A1 拆解 approve（2026-06-29）→ A1.1-A1.4 实现 + 逐 goal 独立 review PASS → **A1 四 goal squash 合 `8b7bea6`（PR #164·2026-06-30·worktree 全量 2285 passed + 探针 PASS）✅**。**A2(#8 附录从册导出)/A3(#2 引用绑 ref + #3 source_type 降 trace) 已解锁（A1 地基立起）·待开工**——本次不开工、仅记解锁。每个承重 PR 合并前用户 review diff（A1 已照此走·4 review 锚见下锚区）。
    - **🔍 A1.1 已独立 review PASS（2026-06-29·挑刺视角）**：四条独立核过——同口径计数真测（非摆设·import 探针实指本仓 src·`pytest tests/test_verify_fact.py` 复跑 37 passed）/ audit_node.py 零接触 + defer→A3 三处留痕齐全 / 全套绿黄牌如实挂着 / A1.2 封顶结构性成立（`WEB_VERIFIED_ENABLED=False` 唯一闸·[confidence.py:171](../../src/committee/facts/confidence.py)）。**两笔结转（非 A1.1 阻断·给后续 gate）**：① **A1 收口 PR**：`pytest -q` 全量绿 + worktree import 探针实跑——必须兑现、不可再 defer；② **A1.2**：把"resume 后无 verified 升迁"当头号红线·要 before/after 实证 + 确认 diff 不碰封顶层（confidence.py 漏斗 / `WEB_VERIFIED_ENABLED`）。review 全文等 A1 出 PR 时进 PR 描述。
    - **review 轨迹（docs）: `f5c7472` 已 PASS（2026-06-29）**：`f5c7472`（backlog 1023/1043 合并措辞 → `web_provenance` 升 `external_websearch` 外源册·**双册并立·不合并·审计不可见**·非"并入 `references` 式统一册"）经用户 **cold review PASS**——完整 diff 核过（含 1023"见下"/ 1043"见上"锚点指向无误）。落此因 trail 原**仅在对话**（f5c7472 commit 在 review 之前、commit msg 无 review-pass 记录）→ 钉进 backlog durable。区别于上条 `597267d`（那是 A1.1 **代码** review 锚、非本 docs 改字）。
    - **🔍 A1.2（`dc1ec10`·load_checkpoint 补 web_provenance）已独立 review PASS（2026-06-29·挑刺视角）**：verdict-touching 改动（resume 后某 web 数据 `unavailable`→`sourced`）四条实测核过——① 升档真实（unavailable→sourced）；② **封顶绝不 verified·经 flag-flip 对抗反证实锤**（同数据 `WEB_VERIFIED_ENABLED` OFF→sourced / ON→verified·证明停 sourced 是**封顶逼停**、非缺印证）；③ 封顶闸三文件（`confidence.py` 漏斗 / `base.py` fresh 路 / `state.py`）**零改**；④ fresh 不洗（stale 仍 `sourced_outdated`）；import 探针指本仓 + `test_checkpoint.py` **21 passed**。**唯一结转**：`pytest -q` 全量绿 + worktree 探针 @ **A1 收口 PR**（非本 goal）。落此因 review-pass 原仅在对话。
    - **🔍 A1.3（`03bc61d`·G2/DS-0 印证池改读外源册·换存取不换原则）已独立 review PASS（2026-06-29·挑刺视角）**：verdict-neutral 改动·命门 = 换存取后判定逐字节同。实测核过——① **before/after replay 真双路对比**（新路读外源册 vs 经典 raw 计数）·**flag OFF & ON 两态都逐字节同**（含 flag ON 时 factM 升 `verified` 的边界）；② **对抗反证实锤**：故意把读册计数器打坏 → replay 立刻发散，证"等价"是 **load-bearing 非空测**（非"恒过"假绿）；③ 基线取 **web_provenance 在场态**（避 A1.2 坑·口径无漂移）；④ `confidence.py` **零改** + G1/封顶/判定原则**物理零碰**；commit 无别 session 夹带·**115 passed**。**唯一结转**：`pytest -q` 全量绿 + worktree 探针 @ **A1 收口 PR**（非本 goal）。落此因 review-pass 原仅在对话。
    - **🔍 A1.4（`d7e3866`·G1 fund_mgr finding 锚印证改读外源册·换存取不换原则）已独立 review PASS（2026-06-29·挑刺视角）**：verdict-neutral·命门 = 换存取后判定逐字节同。实测核过——① **忠实复刻单 URL 锚·锚漏没被修**（`_anchor_tool_outputs_by_source` 函数零改·册从含锚漏的 anchor 子集派生而非全池 → 没"绕着补"·该有的 bug 仍在 = 对）；② **before/after replay 真双路**（`TestA1_4G1LedgerReadByteIdentical`：新路锚读册 vs 经典 raw 计数·`new==classic=={v1:sourced,v3:verified,v4:sourced}`·含 v3:verified 边界）+ **对抗反证**（读册计数器打坏成恒返 99 → replay 发散·证等价 load-bearing）；③ 基线取 `_TOOL_OUTPUTS` 在场态（避 A1.2 坑·G1 无 flag 门控）；④ `confidence.py` 零改·只动 G1·**没回碰 A1.3 改的 G2 块**·移除的经典 `count_corroborating_domains` import 无调用点（安全）·无别 session 夹带。**唯一结转（全量绿 + worktree 探针）已在 A1 收口 PR #164 兑现**（2285 passed·探针 PASS·合 `8b7bea6`）。落此因 review-pass 原仅在对话。
- **阶段范围（2026-06-26 批准）**:
  - **阶段 A（轻·高价值·低风险·A1 地基已合 #164·A2/A3 待实现）** = 治本核心：web 入册(#1·**A1 ✅**) + report 引用绑 ref(#2·A3) + `source_type` 降 trace(#3·A3) + `references_appendix` 从册导出(#8·A2) + **URL 锚持久化（#162 G1 临时锚→源头持久登记·忠实持久化当前锚行为·**A1.4 ✅**；🚩 锚漏修复 2026-06-29 切出→#4·见上"锚漏切出"子条）**。跑在已证 state 模式上、不碰承重判定逻辑（golden 锁不受影响）。
  - **阶段 B（#4 claim/URL 级精确绑定）= 暂缓·带明确判据**：**默认不做**。触发做 #4 的唯一信号 = 阶段 A 落地后**实测"因 role 级池太粗/锚漏而被过度打码（本该 verified 却掉 sourced）的 fact 比例"高**；比例**低 → 永远不做 #4**（role 级即终态）、比例**高 → 才上 #4**。判据理由：#4 成本（DS-0 路 URL 已蒸发、要补 claim↔URL 绑定）只换"少误伤"，而误伤是安全方向（过度打码非误升）→ 除非误伤多到真碍事否则不值得预先投入。**别预先做。**
  - **🔎 阶段 A 后置只读核查项（轻量）**: 量上述"过度打码比例"——这是 #4 是否启动的唯一判据来源，阶段 A 完成后做、只读、不开工。
    - **📊 实测点 1（2026-07-10·NVDA 全链 fresh-run e2e·[EVIDENCE](../observations/m1-full-e2e-20260710/EVIDENCE.md)）**：pass0 audit_passed **8/53=15%**（美股内源薄·web 事实无水印结构缺口）→ **30/53 精确数字未过 audit → decision core_risks 里几乎每个数字被 prose gate 掩码成"相关数值/相应财务水平"**，正文可读性明显受损（多个关键数字变占位）。成因 = role 级池粗（非 claim/URL 级）+ 美股场景。**方向 = 安全（宁掩码勿编造）·gate 未被稀释（prose_gate=verified·decision=SELL 正常出）**。**判据评估**：打码比例足以碍正文可读 → 是"#4 值得做"的**正向数据点**；但 **N=1、单标的、安全方向** → **不足以单独触发 #4**，登记为第 1 个实测点，攒多标的/多轮再判（低比例场景=美股外·A 股/宏观内源厚处待测）。**T10 仍 defer·不改。**
- **R5-04 / R5-03 接续（2026-06-26 批准）**: **[DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮)（语义层）= 建册铺底座后单独 PR 叠上**（不并建册 PR·AI 不确定性与建册的确定性/golden 验收隔离）；**[DEFECT-R5-03](#defect-r5-03-域名归一化无-etld1--同发行方子域被当两独立源🟡-低暴露往后排)（eTLD+1）= 单列**（与出处存储正交 + PSL 依赖决策独立，不随建册）。
- **真开工节奏（这是"批准方向"非"开工指令"）**: 真开工 = **另起 session** 按完整 workflow（承重工程·改 state/schema 级）；**开工前先做"阶段 A 只读设计 pass"**（核 web 入册具体怎么改 + replay 兼容 + `web_provenance` 升格路径），贴出来再 /goal。
- **升级路径（小修 → 建册·换存取不换原则·垫脚石非绊脚石·= 阶段 A 的 URL 锚持久化）**: 小修 G1（fund_mgr 路）用 [`_anchor_tool_outputs_by_source`](../../src/committee/agents/base.py)（按 `finding.source` URL **现场倒推**归属、临时锚池）实现"数印证只看自己那份来源"。建册做的是**同一件事的源头持久版**——搜回即登记归属、数印证时**直接读登记**。两者**方向一致、接同一个调用口**（数印证前把池收窄到"本条数据自己的来源"），区别只是"临时现场倒推" vs "源头持久登记"。
  - **嵌入不推倒重来**：保留"只数自己那份"的**原则与调用口**，仅把 `_anchor_tool_outputs_by_source` 那段**倒推替换为"读 finding 在册的来源登记"**。fund_mgr 路从巧办法平滑升级到正规登记——**更准**（不依赖 source URL 恰好能倒推）、**更干净**（归属在源头定死、不每次现算）。
  - **URL 锚的已知残差（锚漏）= #4 修，非 A1**（⚠️ 2026-06-29 更新）：URL 锚在"某 finding 的 2 个印证域名**分散在两次搜索**"时会**锚漏 → 过度打码**（误伤好人、安全方向，[G1 拆解已记此残差](../plans/R5-02-smallfix-decomposition.md)）。**下文"按本条数据登记消解锚漏"描述的是 #4 的修法（claim/URL 级精确绑定），不是 A1**——A1 拆解设计 pass 核出修锚漏 ⊆ #4，已从 A1 切出（见上"锚漏切出"子条）。#4 做法：建册按"**本条数据**"登记来源（非按"哪次搜索"），分散来源只要**同属一条数据即一并收入**，**不再锚漏**。
  - **结论**：**URL 锚是建册的垫脚石、非绊脚石**——它立起的"只数自己那份"原则与调用口正是建册要复用的；**G1 的成果被建册继承、无一步白做**（"重走流程定范围"是重评 scope、不是推翻 G1）。
- **定性（已评估·三假设已核出结论）**: 出处收敛成**单一信源册**——搜回即登记（带数字内容 + URL + role + as_of）、全程读写它、`references_appendix` 从册派生、`web_provenance` **升格为 `external_websearch` 外源册（与 `internal_structured` 并立·不合并·审计不可见 = #5 红线·见上"红线代码落点"）**、出处不再靠 LLM 标签（**audit 读 web 那条已永久砍除·见上 #5 红线**）。**已有结构化源登记册雏形（`references`+`watermarks`）、audit 已读它** → "扩展雏形 + 纳入 web"非从零。**三假设已核（不再假设性）**：① 登记粒度可行（claim+`numeric_value` 字段已在，fund_mgr 路 URL 现成 / DS-0 路 URL 已蒸发→沿用 role 级代理）；② 跨节点写册 state 成本**偏轻**（最硬的并发写 reducer + 原始数据在 state + resume 幂等今天已付账于 `web_provenance`，建册是扩展雏形非动地基）；③ 合并冲突可辨识有界（粒度/ID 前缀"W"已占/reducer 基数/生命周期均机械），唯一"硬"冲突 = audit 匹配语义 = 恰好就是已砍的 #5。详 [评估文档 §3](../plans/provenance-source-registry-reeval-2026-06-26.md)。
- **进入时点**: 2026-06-25 立项（R5-02 分步决策）→ 2026-06-26 评估完成·方向批准
- **预估工作量**: **轻-中（偏轻）**（评估后定）—— 阶段 A = 存储统一 + 绑定 + 派生，跑在已证 state 模式上、单写 schema 的 Optional 字段加法（archive 兼容）；阶段 B(#4) 暂缓（判据触发才上）。**配额**: 架构治本、不占 lettered 配额。
- **✅ 收口（2026-07-10·用户拍 close）**: **M1 主体完成** —— 11 子任务全收口（T1–T9 + T11/T12/D1-ROOT，其中 T5=#165 CLOSED 无 salvage·T9=负结论锚漏留 #4），全链 fresh-run e2e 佐证（NVDA·9 段·quality gate 13/0/0·[EVIDENCE](../observations/m1-full-e2e-20260710/EVIDENCE.md)）。**唯一未做 = T10（#4）剥离为下方独立挂起条目**（测量驱动·非 M1 未完）。M1 三表定型 + 红线焊死（#5 隔离 / 外源封顶 sourced / audit 只读内源）全部到位并端到端验证。

---

### T10 / #4. claim/URL 级精确绑定（🔵 挂起·测量驱动·2026-07-10 从已 close 的 M1 剥离）

> **✅ CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— **它要治的病已被别的办法治好了**：
> 本条治「过度打码」，而 2026-07-16 GATE-B 门重定义把涂改从 21 处降到 **0**（[#187](https://github.com/JunoChenZt/subagent-for-investment/pull/187)）⇒ **原目标消失**。
> 且其唯一判据「实测锚漏归因比例**高**」**没有任何在跑的监测在量它**（[§4.1](#41-新增-backlog-条目) 禁止形态）——
> 条目自己记的 N=2 实测也已结论「真根因指向 #4 之外」。on-deck 看板 2026-07-16 即写「大概率永不做」。
> **重开条件**：若将来真测出「因锚漏被过度打码」的比例高到碍事（量的是**归因比例**，不是总打码数）。
> 〔以下正文为 point-in-time 记录，**一字未改**。〕

> **📍 2026-08-05 边界澄清**：本条**明确划出**「数字出处」问题域（见 [endgame §1 排除表](number-provenance-endgame.md)）——
> 它治的是**过度打码**（误伤方向·安全侧），而该问题域治的是**假信任**（危险方向），两者方向相反。
> 本条继续按原触发判据（实测过度打码比例高才做）独立走，**不受该问题域判据约束、也不阻塞其收口**。

> **大白话**：系统写报告时，判断一个数字可不可信到能直接当事实写，靠"数它有几个独立来源
> 证实"（≥2 个不同来源→可信直接写；1 个→打码成"相关数值"）。**毛病**：现在按"哪个分析师搜的"
> 粗粒度归堆来源，不是按"具体哪条数据"。于是同一个数字若两个来源分别来自两次不同搜索，
> 系统连不起来→误以为"只有一个来源"→把本该可信的数字打了码。像两个证人在不同日子填了不同
> 表格、而归档系统一次只翻一张表，就误判"只一个证人"。**错在安全的一边**（宁多藏不误真），
> 不修不出事，只是报告打码偏多、读着别扭。

- **技术定义**：把 report/fact 引用从 **role 级池绑定**升到 **claim/URL 级精确绑定**，消解 G1 锚漏
  （某 finding 的印证域名分散在两次搜索时锚漏→过度打码；[base.py 印证锚](../../src/committee/agents/base.py) 现按搜索组锚）。
- **触发判据（唯一信号·别预先做）**：实测"因 role 级池粗/锚漏被过度打码（本该 verified 却掉
  sourced）的 fact 比例"**高**→才上 #4；**低→永不做**（role 级即终态）。理由：#4 贵（DS-0 路 URL 已
  蒸发·需改 Phase-1 analyst 或模糊 join·[reeval §3 假设1/§4.5](../plans/provenance-source-registry-reeval-2026-06-26.md)）
  只换"少误伤"，而误伤是安全方向→除非误伤多到真碍事否则不投入。
- **📊 实测点（累积·N=2·同口径对照）**：
  - **点1**（2026-07-10·NVDA 美股·SELL·[EVIDENCE](../observations/m1-full-e2e-20260710/EVIDENCE.md)）：audit
    8/53=15%·**精确数字未过审 30/34=88%**·decision 打码占位 58 + (未核实)标记 4。
  - **点2**（2026-07-10·中际旭创 300308.SZ·A股·HOLD·[EVIDENCE](../observations/m1-full-e2e-中际旭创-20260710/EVIDENCE.md)）：audit
    8/40=20%·**精确数字未过审 17/19=89%**·decision 打码占位 20 + (未核实)标记 25。两 run quality gate 均 13/0/0。
  - **🔑 N=2 结论（原假设证伪 + 揪出更深根因）**：
    - **"A股大幅少打码"假设=证伪**：未过审比例两边**几乎相同（88% vs 89%）**。打码数差（58 vs 20）是
      假差异——被决策类型（SELL 引大量数字 vs HOLD 少下硬判断）+ fact 总数（34 vs 19）+ fund_mgr 手法
      （NVDA 偏打码 / A股偏贴"(未核实)"标签）污染；总对冲负荷 62 vs 45，同量级。
    - **真根因指向 #4 之外**：过度对冲主因**不是锚漏（跨搜索没连上）**，而是**没有任何市场能从内部源
      拿到可审计的基本面**——[tushare 适配器](../../src/committee/common_context/sources/tushare_source.py) `api_name:"daily"` 只拉价格、不拉基本面（营收/毛利/PE 全靠网搜→#5 红线下 audit 核不了）。
      **#4 只帮"网搜数字靠多域名凑 verified"这条路·帮不了"基本面没内部源"这个更大的洞。**
    - **可能更高杠杆的候选（记此供未来评估）** = 扩 tushare/yfinance 适配器拉基本面（`daily_basic`/`fina_indicator`）
      → 基本面变内部可审计 → 对冲大幅降。见 [AL 反向发现](#al-市场感知路由a-股-query-不挂-yfinance--美股不挂-tushare)。**可能比 #4 更值得做。**
    - **N=2 仍不足以触发 #4**：证明了"对冲重且普遍"，但**没隔离**"88% 未过审里多少是锚漏害的（#4 能救）
      vs 本就单源（#4 救不了）"——这才是 #4 go/no-go 真正要的细测。**T10 仍 defer**·下一步若测应量"锚漏归因比例"而非"总打码数"。
- **关联**：源自 M1 T9 锚漏核实门（结论=册粒度不覆盖锚漏→留本条）+ [DEFECT-R5-02 支柱1](#defect-r5-02-corroboration-印证池未按-fact-scope--不相干-fact-共享常见整数巧合凑成-verified🔴-阻塞-web-verified-放开)（锚收窄本为堵它·放宽治锚漏=放回危险方向）+ [AL 适配器只拉价格发现](#al-市场感知路由a-股-query-不挂-yfinance--美股不挂-tushare)。**两害相权取保守=defer。**
- **⚠️ 更新（2026-07-10·打码机制全链调研）**：T10「量总打码数」的路子被证走偏——归因分解坐实"因来源不够硬（verified 够不着）被打码"=**0**（两 run 皆 0），真瓶颈在 [DEFECT-PROSE-MASK-REF](#defect-prose-mask-ref-散文门冤枉打码--参考集选窄脱节-二值门无中间档🟠伴生逃逸洞见下)（参考集脱节 + 二值门）。**#4 对打码零收益**已坐实。T10 自身（锚漏→过度打码）**降级为 PROSE-MASK-REF 的一个子表现**·不再单独承重·随其一并评估。

---

### AS. web 派生 fact 缺「干净数值源」+「值级可信度」→ 散文数字**值**无法确定性核 ✅ CLOSED 2026-08-05 (close-by-supersede·保留位置)

> ## ✅ **CLOSED（2026-08-05·close-by-supersede·用户批准全景对账处置表）**
>
> **不是"做完了"，是"问法被换掉了"**。本条问的是「散文数字的**值**核不了怎么办」，
> 而 [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 判定 3 把这个问题**反转**了：
> **核不动值的出处，现在直接拿不到最高信任档**（`ticker=NVDA` / `currency=USD` / 研报正文 blob
> 一律降 `audit_notsure`）—— 不再需要"先建干净数值源才能判"，**核不了就不给高档**即是答案。
>
> **原重启判据（"等 G5 的 mismatch 频繁出现"）已于 2026-08-04 证明自锁**（见下方 🔴 更正块），
> 不可再用。**新归属**：要不要真去比数值 = [number-provenance-endgame](number-provenance-endgame.md)
> **判据 D2**（判定 4 观察期后强制二选一：转正 / 明拍放弃并写死理由 —— **不许无限期 log-only**，
> 那正是本条当年烂尾的方式）。
>
> **配额**：本条原就标注"不占 lettered"，close 不改计数。
>
> ↓ 下方为 2026-07-16 降级期 + 2026-08-04 更正记录（point-in-time·不改）↓

> ## 🔵 状态更新（2026-07-16·MASK.GATE-B 收官）—— **本条的机械修法已被 AI 路取代**
>
> **① 真实价值被实测推翻**：NVDA 全链 e2e 量下来——**43 个正文数字里 22 个有源、全部誊写一致、
> 0 抄错**（[measurement findings](../observations/mask-c-e2e-measurement-NVDA-20260716.md)）。
> 即 opus 誊写零错、「核值门」几乎无用武之地。**且被打码的 21 个基本不是可溯源事实**
> （日期/列表序号/区间/处方量）→ **AS 救不了它们**（真病因是打码门机制，已由 GATE-B 治好）。
>
> **② 机械修法被 G5 取代**：本条原候选（wisburg/rss 适配器抽结构化值 + per-number 锚定 +
> 登记 number_registry）**最贵那块（wisburg 自由文本 per-number 锚定）不必做了**——
> **G5 AI 誊写核查**（[#187](https://github.com/JunoChenZt/subagent-for-investment/pull/187)·gemini-2.5-pro·
> **只降级绝不升级**）**直读研报原文**即可判「写的数和来源说的对不对得上」，不需要那套基建。
> G4 实测：15 条核查全 match·**误报率 0**（[G4 evidence](../observations/mask-gate-b-G4-evidence-NVDA-20260716.md)）。
>
> **③ 处置**：**降级 🔵 defer**（不 close·留观测口）。**重新触发判据** = G5 的 enforcement_log
> 里 **mismatch 真实出现且频繁** → 说明 AI 路不够、才需要回头建干净数值源。
> 当前实测 mismatch=0 → **不投入**。（同 T10/#4「测量驱动·实测比例高才做」纪律。）
>
> ## 🔴 **2026-08-04 更正：上面这条重启判据【自锁】，不可再当有效判据用**
>
> **实证**（[DEFECT-ANCHOR-MISBIND](#defect-anchor-misbind-报告里的数字挂着别人的出处而系统因为有出处给了它最高信任🔴2026-08-04-全链-e2e-实证每跑都在发生✅-closed-2026-08-14close-by-completion保留位置)）：G5 拿到的「来源原文」**首行是待核陈述自己**（[`_transcription_source_text`](../../src/committee/agents/base.py) 把 `fact.claim` 放在第一位）→ 对「**数字对、但锚指向别的实体**」这一形态**结构上判不出 mismatch**。
> ⇒ 该形态**永远不会**让 mismatch 计数上升 ⇒ **"等 mismatch 频繁出现再投入"这个条件永远不成立**。与 [BB](#bb-段间-checklist-⑧-的-audit_passed--50-是空线五次-run-全-6132026-07-31-全链回归-e2e-surface) 同族（判据挂在不会响的信号上），区别：BB 永远报警（吵）、本条**永远不报警**（静默）。
>
> **同时推翻 ② 的一半**：「G5 直读原文即可判、不需要那套基建」——对**誊写抄错**成立（当年 G4 实测 15 条全 match 是真的），对**归属错不成立**。**当年把两类当成一件事了。**
>
> **且「机械路太贵」这个前提本身要分开看**（2026-08-04 实测·零 LLM）：本轮 13 条最高信任事实做纯数值比对 → **10 条错绑全抓到 · 唯一正确的正确放行 · 零误报**。**结构化标量源（行情/财务接口）核值是纯机械的、几乎免费**；只有**自由文本源（研报正文）**才要 AI —— 这正是 [audit-positioning §4](../pipeline/decision/audit-positioning.md)「数字对不对」行 2026-07-03 的原始画法。今天出问题的 10 条**全在机械那半**。
>
> ⇒ **本条状态需重估**（🔵 defer 的依据已部分失效）。**重估与排期须用户裁**，本块只落事实、不改强度。
>
> ↓ 下方为立项期记录（point-in-time·不改）↓

**原条目（2026-07-15 立·MASK.C2 D-3 实测暴露）**：

> **一句话**：fund_mgr 散文里的数字，很多来自网络/研报（wisburg / rss / 分析师 web），它们**有来源、也被跨域名印证过可信**，但**没有一个干净的数值源可供确定性比对**——∴ 任何"比数字值"的门（如 MASK.C2 早期「比源值」设计）对它们只能 fail-safe 涂，误伤一批可信数字。**本条只记问题+证据，不预设修法**（承重·属出处/信源管道·非散文门 scope）。

- **强度**：🟠（影响交付物完整性·非安全 bug——门宁涂勿放·方向安全）。**上游数据/出处层**·独立于 MASK 打码系列（C2 已按用户裁决收窄为「只验引用不验值」·绕开本问题·见 [fundmgr-mask-fix-series](../plans/fundmgr-mask-fix-series-2026-07-14.md)）。
- **实测证据（MASK.C2 D-3 空跑·2026-07-15·NVDA seg9·[dryrun](../observations/experiments/mask-pathb-dryrun/d3_before_after.md)）**：20 个挂标 f# 里 **8 个** confidence=sourced/verified 但源值解析不了 → fail-safe 🔴。三类窟窿逐个核实：
  - **wisburg REF#**（如 REF#W-003 目标价300）：`Reference.value` 存的是**整篇研报文本**（"Found 20 reports:…"），非结构化数值——数字埋文本里抽不出。
  - **rss REF#**（REF#R-002）：`value="list(10)"` 占位串·非数值。
  - **fundamentals W#**（W#fundamentals-2-4#n1 等）：这些 web 数字级编号**不在外源册 number_registry**（册里有 macro/commodity 的号·fundamentals 的漏登记）。
- **更深连带**：76 个内源 fact 里 47 个 confidence=unavailable（audit 只核表① REF#·web 来的 fact 多 audit_inconclusive→unavailable 除非 web 印证够）——即**可信度机制本身对 web fact 立不起来**（AO/D1-ROOT 家族）。∴ 散文数字被涂**大头在上游可信度/出处·非打码门**。
- **候选方向（不预设·须设计）**：① wisburg/rss 适配器抽结构化数值 + 发数字级编号（补 number_registry）；② fundamentals web stamp 登记进外源册；③ 给 web fact 建值级可信度信号（超 audit 存在性半项·近 AUDIT-3CHECK 但那已砍→须新设计）。**均承重·属信源册/AO 线·非本系列。**
- **进入时点**：2026-07-15（MASK.C2 D-3 空跑坐实）。**配额**：DEFECT-*/上游数据债·不占 lettered。
- **关联**：症状显现处 = MASK.C2 打码门；病根族 = [信源册 M1](#信源册建册-出处收敛单一贯穿真值源✅-大任务-m1-主体完成close-2026-07-10三表定型11-子任务收口t104剥离为独立挂起条目全链-e2e-1300) / [DEFECT-D1-ROOT](#defect-d1-root-gate-读展示表表③而非内源真值表表①-安全闸可被任意非-unverified-条目稀释含纯内源-sourced--过期源🔴-高优d1-病根独立于-m1) / AO web-provenance。

### DEFECT-PROSE-MASK-REF. 散文门"冤枉打码" — 参考集选窄（脱节）+ 二值门无中间档（🟠·伴生逃逸洞见下）

> **✅ 已解决并合 main（2026-07-16·[#187](https://github.com/JunoChenZt/subagent-for-investment/pull/187)→`71da2d9`）**。
> **⚠️ 但修法在收官时被 e2e 实测翻转两次——下方「🔴幻觉标/裸事实数字涂」等描述已废、勿当现状读**：
> ① C 组 Path B 落地（C1 生成侧带标 / C2 验章门「只核引用不核值」/ C3 删搜章）；
> ② **GATE-B 门重定义（2026-07-16）**：实测旧门「默认涂无标数字 + 豁免集赦免」涂的 21 个
> **全是误伤、0 真阳**（年份/列表序号/区间/处方量）→ **门只验主动挂标的·不猎无标的**；
> **无标裸数字不涂、只记 `enforcement_log`**（ESCAPE 由「涂」降级为「记」）；🔴 **仅剩幻觉标**。
> **实测涂 21→0、正文占位 19→0。** 现状真值源 = [MASK-GATE-REDEF 设计 pass](../plans/MASK-GATE-REDEF-信任标记-设计pass-2026-07-16.md)。
> ↓ 下方为 2026-07-15 C 组落地期记录（point-in-time·不改）↓
>
> **~~✅ 已由 MASK.C 验章门实现解决（2026-07-15·`1f51903`）~~**：Path B 已落地——**C1** `DECISION_PROMPT` 反转为生成侧带标（写数字挂 `{ref:fX}`/`{ref:vX}`）；**C2** `_apply_stamp_gate`（[stamp_check.py](../../src/committee/facts/stamp_check.py)）验章不搜章、**只核引用不核值**、认标 + 认册三档（🟢结构化源/v#-verified 留原值·🟡弱引用留值+「未独立核实」·~~🔴幻觉标/裸事实数字涂~~ **← 裸数字那半已被 GATE-B 废**）；**C3** 删旧 `_scan_claims`（搜章）+ `_apply_prose_gate`。**两层病均消解**：① 脱节——不再靠"事后搜索匹配窄 findings 候选"（83–90% `matched_finding=null` 打码之根）→ opus 带标即背书，无候选一说不复存在；② 二值门——🟡 中间档已建（有源未硬核 → 留值 + 轻标注·非全打码）。**数字值对不对**已明确划出本门（= 上游 backlog `AS` 独立任务）。下方为 Path B 设计期 + 重审期记录（point-in-time·不改）。↓
>
> **✅ 重审完成·方向定稿 Path B（2026-07-13·产出 = [PROSE-MASK-REF 兜底重定位设计 pass](../plans/PROSE-MASK-REF-兜底重定位-设计pass-2026-07-13.md)）**：中立重审（那次"存疑·从零重审"的产出）结论——**门本该是兜底（防 fund_mgr 编数字的 grounding check）·非判官·非重做 audit**；原「非 bug·全靠 AUDIT-3CHECK」框**过满 → supersede**（下方 R5 分析降为过程记录·勿当结论）。**修法方向 = Path B**：生成侧写数字时带机器标（来源水印）· 门**验章不搜章**（一对一确定性·复用 EXEC-FLOOR check① 原语）· **audit_passed 完全不进门**（它是输入侧纯代码节点·只核引用存在不核数字）。四裁决已定（D-1 就地括注 / D-2 audit-only 归🟡·🟢只认独立重查 / D-3 先空跑 / D-4 纳 web·详 pass §6）。**唯一未知 = opus 带标准确率**（当年墙是原则性立·从没实测）→ Path B 首步 = D-3 空跑实测带对率 vs 现"事后猜"·够高成立/不够退 Path A。**承重·北极星相邻·实现另起新 session 走完整 workflow·不授权不进实现。** 下方为重审前记录（point-in-time·不改）。↓

> **大白话**：报告付印前有道"事实核查台"——数字能掏出**来源卡**就照印+标出处，掏不出就涂黑成"相关数值"。问题：核查台**手上只有一小叠卡**（早先只给"分析师吵架的 + 数据太旧的"事实重新联网办了卡），**够不着隔壁那座 M1 建的完整档案库**。于是绝大多数数字——明明档案库里有卡——在核查台小叠里翻不到 → 被涂黑。**下方 R5 已查明：档案库那张卡的"章"只保证引用对号、不保证数字对，所以门不认它是有道理的（见 banner）。**

> **✅ R5 设计初衷已查（2026-07-10·结论推翻本条原修法方向·原分析留作调研轨迹·下方 ①/候选修法已就地纠正）**：门为何不信档案库=**有道理的墙，非实现漏**。关键 = [audit-positioning:36](../pipeline/decision/audit-positioning.md)：audit **现状只做"来源"半**（抽 `ref_id` 查存在→盖章·**数字直接丢弃**·日期不看）→ **`audit_passed` = "引用对上号" ≠ "数字是对的"**（盖章时压根没看数字）；而 [confidence.py:157](../../src/committee/facts/confidence.py) 却 `audit_passed`→`verified` → **一个数字可以 confidence=verified 但值从没被独立核过**。散文门 `numeric_match` 要确认的**恰是数字本身**（正文数字 ↔ 来源查到的数字对不对得上），只有**重查线 findings**（步骤3 现场联网、拿回**独立**数值）提供得了；档案库 audit_passed 提供不了。∴ **门不认档案库数字 = 防"印出值从没查过、却看着已核实的数字"（正是逃逸洞那个不安全方向）**。
> - **❌ 原候选修法"门先查档案库·有硬章直接认"撤销·不安全**：`audit_passed` 硬章 ≠ 数字独立核过。
> - **① 脱节 ≠ bug·大部分是设计**：[fm-spec §B1:159](../specs/fm-decision-node-spec.md) 明写"数字要么回溯到 facts、**要么被打码**（定性化本身就是处置）"——被打码的数字值确实没独立查过·打码是安全诚实处置。**真瓶颈=成本**：独立核数字要现场联网重查（花钱）→ 只对高风险项重查·其余没法核数字→打码=**成本/覆盖权衡·非"参考集选错"**。
> - **✅ 想少打码又不牺牲安全的正道 = [AUDIT-3CHECK](#defect-audit-intent-审计机制定位待厘清防抄错被当可信度安全闸判据🔴-元问题defect-d1-root-前置)**（让 audit 真去核数字·不只核引用→ audit_passed 才=数字已核·门才能信它）。**本条降级为"依赖 AUDIT-3CHECK 的可读性/覆盖权衡"·非独立 correctness bug。**

> **🔧 补正（2026-07-10·把"核数字的地方"核全·上方 banner "audit 不核数字→只有 findings 核" 口径太窄，据实修正）**：pipeline 里**核数字的其实有 4 处**（audit 不算·它只核 ref 存在），但**打码门只听第 ④ 个**：
>
> | # | 核数字处 | 怎么核 | 送到哪 · 喂打码门? |
> |---|---|---|---|
> | ① | DS-0 自查 `watermark_claim_mismatch`（[pass0_prompt](../../src/committee/prompts/pass0_prompt.py)）| LLM 自比 claim 数字 ↔ 水印源值·**只报"对不上"负信号** | 只 triage 聚合（[pass0_validator:82](../../src/committee/triage/pass0_validator.py)·>50% 告警）·**❌ 不喂** |
> | ② | web 多域名印证 `count_corroborating_domains` | 确定性·数值跨 ≥2 域名·**正向核实** | confidence web 支·**但 `WEB_VERIFIED_ENABLED=False` 封顶 sourced·达不到 verified → ❌ 事实上不喂** |
> | ③ | check① `EVIDENCE_TRANSCRIPTION_FLAG`（[exec_floor](../../src/committee/facts/exec_floor.py)）| 确定性·fact 主数字 ↔ number_registry 登记值·**只抓数量级错（灾难指纹）** | EXEC-FLOOR 价位硬拦·**明说不喂打码门（exec_floor.py:18）· ❌** |
> | ④ | 现场重查 `findings` `numeric_match` | 确定性·步骤3 现场联网独立数值 ↔ 正文数字 | **✅ 打码门唯一听的** |
>
> **∴ 不是"数字没被核过"，是"核过的 4 处里打码门只认第 ④ 处（现场重查·只覆盖高风险项）"。** 尤其 ② **真在正经核 web 数字、却被安全阀 `WEB_VERIFIED_ENABLED=False` 刻意挡在门外**。
> - **`WEB_VERIFIED_ENABLED=False` 设计初衷（见本文件【信源册建册】条目内 "PR2 #161" 段 + 【AO】条目·2026-06-26 用户拍 close·非烂尾）**：翻开 = web 数字进 verified 不打码·碰北极星红线；且 web 最不可信·"两网站都含 30%"会被当印证哪怕说的不是一回事（池分开半已 #162 修·**语义半未修 = [DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮)**）→ 权衡后**决定关门**。∴ "web 封顶 sourced 照样打码"= **刻意安全选择·非疏忽**。
> - **∴ "想少打码又不失安全"有两条既有杠杆（都被安全前置门控·非本条独立开修）**：**(A) [AUDIT-3CHECK](#defect-audit-intent-审计机制定位待厘清防抄错被当可信度安全闸判据🔴-元问题defect-d1-root-前置)** 让内源 audit 真核数字；**(B) 放开 ② 的 `WEB_VERIFIED_ENABLED`**——但须先修 [DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮)（语义印证）+ 用户重裁北极星。两条都不是"接线漏了"·是"安全阀关着"。

**两层问题（本条一并收·原始记录·② 仍成立·① 已被上方 R5 纠正为"非 bug 是设计")**：

| 层 | 病 | 修了→ |
|---|---|---|
| **① 脱节** | 散文门 body 匹配只对 `findings`（`v#`·= [`_build_verify_checklist`](../../src/committee/agents/base.py:1662) 只挑 `consensus_level∈{minority,majority}` 或 as_of 过期的项经步骤3重查）匹配；**M1 的 `facts_inventory`/`references`/外源册不是 body 匹配候选**（DS-0 `f#` 在 `confidence_map` 但不进 `findings_by_id`·[base.py:1979](../../src/committee/agents/base.py:1979)）→ 实测 body 数字 **83–90% `matched_finding=null`**=无候选被打码 | 止住"冤枉打码"·数字按卡的**真实**等级判、不一律当"没依据" |
| **② 二值门** | 就算查到卡：门是 `confidence != verified` **一刀切**（[base.py:2115](../../src/committee/agents/base.py:2115)·该门已随 MASK.C 换代为 `_apply_stamp_gate`·现 base.py:2123）——"有源单来源"(`sourced`)和 `unavailable` **同等全打码**·无"轻标注"中间档 | 需单独裁决"'有源没硬核'该轻标注 vs 全打码" |

**~~⚠️ 必须先查的坑（R5·别急着开修）：门为何不信档案库？设计初衷未核实~~** → **✅ 已查（见上方 R5 banner·2026-07-10）**：不是"新鲜度保证"那个猜测，而是 **audit_passed 只核引用不核数字** → 门不认它是**防印出未核数字**（有道理的墙）。原猜测（档案库 web 卡不新鲜）**非主因**·真因是 audit 语义（citation-resolution ≠ number-verified）。**候选修法"信档案库硬章"已撤销（不安全）。**

**证据**：2026-07-10 NVDA + 中际旭创 全链 e2e 归因分解（[dataflow §11.5](../pipeline/dataflow-whole-pipeline.md) 已补）——`matched_finding=null` 83–90% / `numeric_match=false` 6–17% / **"匹配成功但非 verified"=0**（两 run）。

**关联**：
- **姊妹问题 = 逃逸洞**（反向·under-mask：`_replace_in_decision` 只覆盖 3/11 字段·非 verified 数字在 `dissenting_views`/`trigger_events`/`override_justification` 原样印出·🔴 方向不安全·撞北极星）→ **✅ 已立 [DEFECT-PROSE-MASK-ESCAPE](#defect-prose-mask-escape-散文门逃逸洞--打码只覆盖-311-字段未核实数字原样印出🔴-方向不安全撞北极星)**（本条只收"冤枉打码"·两者别混）。
- **吸收 [T10/#4](#t10--4-claimurl-级精确绑定🔵-挂起测量驱动2026-07-10-从已-close-的-m1-剥离)**：#4 修 verified 可达性、但实测 C=0 → 对打码零收益·真瓶颈在本条。
- **② 二值门** 与 [DEFECT-R5-04](#defect-r5-04-印证语义层--比数值不够要比带数字的内容是否说同一件事⏭️-另记拔支柱2不进本轮)（印证语义层）正交但同域·动 5' 策略时一并看。

**状态**：✅ **已实现解决（MASK.C·2026-07-15·`1f51903`）**——Path B 验章门落地（C1 生成侧带标 + C2 `_apply_stamp_gate` 验章不搜章 + C3 删搜章门）；两层病（脱节 / 二值门）均消解，🟡 中间档已建。详见顶部 ✅ banner。〔原"🟠 待新 session 实现"口径已 superseded；下方 2026-07-13 重审 banner + 2026-07-10 "🟡 依赖 AUDIT-3CHECK 可读性权衡" 均作 point-in-time 过程记录留存·正文不改〕DEFECT-* 家族·不占 §4.4 lettered 配额。

---

### DEFECT-PROSE-MASK-ESCAPE. 散文门"逃逸洞" — 打码只覆盖 3/11 字段·未核实数字原样印出（🔴 方向不安全·撞北极星）

> **📌 前向关联（MASK.C·Path B·2026-07-15·`1f51903`）**：散文门已由 MASK.C 整体换代为验章门 `_apply_stamp_gate`（旧 `_scan_claims`+`_apply_prose_gate`+`_replace_in_decision` 删）。**~~ESCAPE 底线保留并内化~~ → ⚠️ 已由 GATE-B 降级（2026-07-16·[#187](https://github.com/JunoChenZt/subagent-for-investment/pull/187)·北极星放松·用户授权）**：
原写「C2 **对无标裸事实数字 + 幻觉标一律涂**」——**裸数字那半已废**。实测该机制涂的 21 个
**全是误伤、0 真阳**（涂的是年份/列表序号/区间/处方量·真该涂的一个没抓到），且过度打码
**反毁门自己的初衷（可读性）**。**现状**：**ESCAPE 由「涂」降级为「记内部审计日志」**——
无标数字原样保留 + 全部记 `enforcement_log`（`stamp-gate-unstamped-log`）；🔴 **只剩幻觉标**
（挂了不存在的 ref）仍剥+涂 = 「只放行无标·绝不放行假标」。涂的执行面
`_REPLACEABLE_LOC_PREFIXES` 本身不变（仅幻觉标走它）。`trigger_events` / execution_plan
`.note` 延续 #182 scope 不做。本条 ✅ 修复记录（PR #182）不动。现状真值源 =
[MASK-GATE-REDEF 设计 pass](../plans/MASK-GATE-REDEF-信任标记-设计pass-2026-07-16.md)。
>
> **📌 前向关联（MASK.B1·2026-07-15）**：本条 #182 修补的是**决策字段侧**逃逸洞（`_replace_in_decision` 覆盖面）。另一条逃逸面来源——**步骤 6 长正文展开产物 `body_expanded`**（扩写文本绕过步骤 5' 打码门）——已随 **MASK.B1 砍掉步骤 6/7**（`_expand_section_ds` / `_review_expansions` 删）一并消除；`body_expanded` 恒 None、前端本就从不渲染。本条正文（已合记录）不动，仅记该逃逸面已随 B1 关闭。

> **📝 复核修正（代码 + git 一手核·继 2026-07-10 打码全链调研·supersede 下方 大白话/病灶/根因/原修法 的"补 8 字段"粗框；标题不改=保入站锚）**：
> - **真轴 = 观点数字 vs 事实数字·非"字段覆盖面"**：代码已有 [`_decision_prescribed_numbers`](../../src/committee/agents/base.py:1950)（现 main :1950·行号已刷新）按**数值**豁免 fm 处方数字（仓位/价位/触发阈值 + execution_plan note + reevaluate_triggers 描述），[`_apply_prose_gate`](../../src/committee/agents/base.py:2132)（已改名 `_apply_stamp_gate`·**现 :2132**）打码前先豁免。〔⚠️ **2026-07-22 GATE-ROUTE G1 收窄**（[#192](https://github.com/JunoChenZt/subagent-for-investment/pull/192)）：按数值豁免**现只作用于无标数字**；**挂标数字一律走正常判档**、不再按值免检（修 f35：挂标研报数「产能 1500 万」撞止盈价 1500 曾被误免·章没盖）。本句所述为收窄前口径〕
> - **8-11（execution_plan 各 note + reevaluate_triggers.description）= 处方场·其数字已全进豁免集·无源正常·非 bug·不动**。
> - **真逃逸 = 既不在豁免集、涂黑侧又够不着的 3 字段**：`dissenting_views`（事实场）/ `override_justification`（事实场）/ `trigger_events`（观点+事实混）。实测样本正好落这 3 处。
> - **scope（用户拍·收窄）= 只补 2 字段**：给 [`_replace_in_decision`](../../src/committee/agents/base.py:2035)（函数已随 MASK.C3 删除·现仅 base.py:2035 注释留名）加 `dissenting_views` + `override_justification` 两分支（镜像现有 `position_size` 分支）。二者纯事实场、不在豁免集 → 事实未核实数字正确打码；撞处方值的仍被 `_apply_prose_gate` 上游豁免 → **两向安全·低风险 additive**〔⚠️ 同上·2026-07-22 后「撞处方值豁免」**仅对无标数字**成立〕。
> - **`trigger_events` 明确不做（边界·防将来误加回）**：观点/事实混合场（"跌破 30 倍 PE 减仓"里 30 倍=处方该留·顺带引"当前 45 倍"=事实该涂），按字段一刀切必误伤；按数字性质精细判别成本高·本轮不碰。
> - **归因纠正**：① 扫描侧真覆盖来自 [`_serialize_decision_for_scan`](../../src/committee/agents/base.py:2020)（序列化 11 字段喂 LLM）·**非** [`_PROSE_SCAN_FIELDS`](../../src/committee/agents/base.py:1628)（该常量列 11 字段但**全仓无消费点=死代码**·仅存意图）；② **git 考古**：11 字段扫描 vs 3 字段替换是**同一 commit `5885fe7`（八步重写 #144）出生即不对称**·非下方"扫描后扩·涂黑没跟上"（该说法已证伪）。
> - **DoD**：单测（两字段事实数字被涂 + 撞处方值不涂）+ mutation 证 load-bearing + e2e 点验逃逸清零。

> **大白话**：核查台分两步——① "盖章的人"走遍报告**全部 11 个版面**、给每个没来源的数字盖"待核实"戳；② "涂黑的人"本该把盖了戳的数字涂黑成"相关数值"。但**涂黑的人只有 3 个版面的权限**（正文/核心风险/仓位），剩下 8 个版面**够不着** → 那里的数字**盖了戳、没人涂** → 像「目标价 1325 元」「估值 40 倍」这种**系统内部明知没核实**的精确数字**原样印出、看着和核实过的一模一样**。**这是「冤枉打码」（[DEFECT-PROSE-MASK-REF](#defect-prose-mask-ref-散文门冤枉打码--参考集选窄脱节-二值门无中间档🟠伴生逃逸洞见下)）的反向孪生：那个是"该印的涂黑了"(安全)，本条是"该涂的印出去了"(危险)。**

- **强度**：🔴（**方向不安全**·撞北极星"不误导决策者"——错的数字伪装成对的印出=项目最忌讳）。
- **病灶**：扫描侧 [`_PROSE_SCAN_FIELDS`](../../src/committee/agents/base.py:1628) 覆盖 **11 字段**（thesis body / core_risks.risk|mitigation / trigger_events / dissenting_views / position_size / override_justification / execution_plan 各 .note …），但替换侧 [`_replace_in_decision`](../../src/committee/agents/base.py:2292) **只实现 3 字段**（`thesis body` / `core_risks.risk|mitigation` / `position_size`），其余一律 `return False`。**两侧覆盖面失同步**（扫得到、替不掉）→ `dissenting_views` / `trigger_events` / `override_justification` / exec-plan `.note` 里被判非 verified 的精确数字：`claim_audit.replaced=False`、正文未被替换 = **原样印出**。
- **根因（why·非故意跳过）**：扫描侧后扩到 11 字段（抓全数字），替换侧只落地了 3 字段——**增量实现·两侧没对齐**。**[fm-spec §162](../specs/fm-decision-node-spec.md) 早标"🟡 机制存在但覆盖面待验"**——设计者已知覆盖面可能不全、挂"待验证"，一直未验未补；本条 = 2026-07-10 e2e **实测坐实"未覆盖"**。
- **实测**：逃逸 NVDA **10** 个 / 中际旭创 **17** 个（后者比真被打码的 12 个还多）·两 run 均在 `dissenting_views`/`trigger_events`/`override_justification`（[dataflow §11.5](../pipeline/dataflow-whole-pipeline.md) / [gate-mechanisms-map](../pipeline/decision/gate-mechanisms-map.md) 已补）。样本：「目标价 1325 元」「估值 40 倍」「营收 22 亿」「6-9 个月」——全精确、全没核实。
- **修法方向（低风险·additive）**：把 `_replace_in_decision` 的字段覆盖补齐到与 `_PROSE_SCAN_FIELDS` 一致（8 个缺字段补上替换分支）。**须核**：`trigger_events`（前瞻阈值·非事实断言）里的数字**该不该打码**——它们是 fm 自定的触发条件、可能属 prescribed 豁免类（同 execution_plan 价位），别误伤（防制造反向的"冤枉打码"）。∴ 修前先分清"逃逸的是**事实数字**（该打码）还是**处方阈值**（该豁免）"。
- **关联**：姊妹条 [DEFECT-PROSE-MASK-REF](#defect-prose-mask-ref-散文门冤枉打码--参考集选窄脱节-二值门无中间档🟠伴生逃逸洞见下)（冤枉打码·同门反向）；与 prose gate `_apply_prose_gate` 步骤 5' 同域。**两条别混**：本条治"漏网"（补覆盖面·低风险），MASK-REF 治"错杀"（改参考集/二值门·需先查设计初衷）。
- **状态**：✅ **已合 main `10c00a9`（[PR #182](https://github.com/JunoChenZt/subagent-for-investment/pull/182)·2026-07·CI 双绿·用户拍 merge）**：`_replace_in_decision` 补 `dissenting_views`+`override_justification` 两分支。DoD 全过：单测 4（两字段涂黑 + 撞处方值豁免 + trigger_events 边界锁）+ mutation 证 load-bearing + 全量 2546 passed + **e2e 点验**（m1-full-e2e-20260710 真实归档 replay：dissenting_views **9/9 逃逸清零**·0 误伤）。`trigger_events` / execution_plan note 按 scope 有意不做（观点/处方场·豁免集已覆盖）。DEFECT-* 家族·不占 §4.4 lettered 配额。
- **关联 observe（PR #182 review 切出·单独记录）= [DEFECT-PROSE-MASK-INDEX](#defect-prose-mask-index-_replace_in_decision-按值遍历不认-location-下标🟢-极低优observe)**：`_replace_in_decision` 的 `dissenting_views`（及既有 `core_risks`）分支按值从头遍历、不认 location 下标 → 同值出现在多条目时可能改错条目。影响可忽略、与既有 `core_risks` 同款、非本 PR 引入。**按现状合并·单独记录不阻断**。

---

### DEFECT-STAMP-MULTIBIND. 连写多标全绑到「最后一个数字」→ AI 核查误报 → 涂掉写对的数字（🟡 defer·判据驱动）

- **病灶**：[`stamp_check.num_span_before_stamp`](../../src/committee/facts/stamp_check.py) 的语义 =
  连写标（`{ref:a}{ref:b}`）**共享紧邻的前一个数字**。但 fund_mgr 用连写多标给「**一子句多数字**」
  挂多源时，意图是**各标各的数字**：`营收 $81.6B 同比 +85%{ref:v3}{ref:v4}`（v3→$81.6B、v4→85%）
  → 实际全绑到 `85` → G5 誊写核查被问「v3 支持 85 吗」→ 源里是 $81.6B → **mismatch** →
  **把 v4 明明支持的 85 涂成定性词** = **过度打码复发**。
- **实证**（[e2e evidence](../observations/mask-gate-b-fix-e2e-NVDA-20260717.md) §3·2026-07-17）：
  prompt 口径 B **v1** 下 r2 出现 7 处连写多标 → **4 条 mismatch 全是此成因、零真阳**。
- **潜伏性**：绑定语义来自 **MASK.C2**、G5 来自 **[#187](https://github.com/JunoChenZt/subagent-for-investment/pull/187)**
  ——**两者均已在 main**；旧 prompt **不诱发**连写多标（实测 0）→ 门只查存在性 → 无害。
  ∴ **main 当前安全**，是「让模型多挂标」的 prompt 才会激活它。
- **现状 = 已由 prompt 硬约束压住**（MASK.GATE-B-fix v2）：(a) 段写死「一个数字一个标·标紧跟它
  自己的那个数字·**禁止把多个标堆在句尾**」+ 真实反例 → **r3 实测 多标 7→0 / mismatch 4→0 / 涂 4→0**。
- **代码兜底（未做）**：G5 遇「一个数字被**多枚标共享**」→ **跳过不核**（判不了归属就别动手·
  fail-safe·**不依赖模型听话**）。**用户 2026-07-17 裁 prompt-only 优先**（仓内既定范式；
  且最坏后果 = 过度打码 = 可读性代价·安全方向·不撞北极星）。
- **🔑 重新触发判据**：`stamp-gate` 审计日志 / 后续 e2e 中**再现连写多标**（= 模型不总听话）
  → 届时加代码兜底。DEFECT-* 家族不占 §4.4 配额。

### DEFECT-PROSE-MASK-INDEX. `_replace_in_decision` 按值遍历不认 location 下标（🟢 极低优·observe）

- **病灶**：`_replace_in_decision`（[base.py:2035](../../src/committee/agents/base.py:2035)·函数已随 MASK.C3 删除·现仅该行注释留名）的 `dissenting_views` 分支（及既有 `core_risks` 分支）按 `value` 从头遍历、替换**首个**含该值的条目，**不解析 location 里的下标**（`dissenting_views[2]`）。∴ 同一数字出现在多条目、audit 指向 `[2]` 时可能被替换到 `[0]`。
- **影响可忽略**：同 data_kind 定性词相同、且属安全方向（该涂的都涂了·仅条目串位）；子串匹配残差（`"22"`⊂`"220"`）同属既有已知边界（[test_value_substring_collision_is_known_boundary](../../tests/test_continuation.py)）。**与既有 `core_risks` 分支同款·非新缺陷**。
- **出处**：[DEFECT-PROSE-MASK-ESCAPE](#defect-prose-mask-escape-散文门逃逸洞--打码只覆盖-311-字段未核实数字原样印出🔴-方向不安全撞北极星) [PR #182](https://github.com/JunoChenZt/subagent-for-investment/pull/182) review 切出·用户裁"按现状合并·单独记录"。
- **修法（若做）**：解析 location 下标直接定位 `dv[N]`（顺带给既有 `core_risks` 范式做更精确样板）·additive 低风险。**默认不做**（与既有代码同款·收益低）。
- **状态**：🟢 observe → **moot（MASK.GATE-B-fix·2026-07-16·`f6b3d0a`）**：验章门 `_apply_stamp_gate` 改**编辑表**（收集不重叠 span·按 `(start,end)` 降序一次性应用），🔴 涂按数字 span 定位 → 串位隐患不复存在。DEFECT-* 家族不占 §4.4 配额。〔正文病灶记录 point-in-time·不改〕
  - **⚠️ 2026-07-16 更正（原状态断言"moot 自 MASK.C3·`1f51903`"= 事实错误·就地改）**：C3 确实删了
    `_replace_in_decision`，但**新门的 🔴 路当时并非 span-based**——`pending_red` 存 `(literal, repl)`
    字符串、由 `_replace_value_and_marker` 走 `text.find(value)`，**恰恰就是"按值从头遍历"**。
    ∴ 串位隐患**未消失**，且比原条目描述的更重：不只是"条目串位·安全方向"，而是**同字段同名数字时
    涂掉合法的、放走幻觉的**（实测 `营收 300 亿{ref:f1}，目标价 300 美元{ref:f99}` → 涂了 f1 那个）
    = **方向反转**，非"影响可忽略"。真正 moot 自 [MASK.GATE-B-fix](https://github.com/JunoChenZt/subagent-for-investment/compare/main...auto/MASK-GATE-B-fix) `f6b3d0a`。
    **教训**：#187 的 R7 收口把"旧函数已删"当成了"隐患已消失"——**删掉旧实现 ≠ 新实现没有同一个病**，
    改 moot/已解决类断言前须核**新路径的实际实现**（见 known-pitfalls §3.2「沉淀教训 ≠ 焊死教训」同源）。

### DEFECT-AUDIT-INTENT. 审计机制定位待厘清——"防抄错"被当"可信度/安全闸"判据（🔴 元问题·DEFECT-D1-ROOT 前置）

> **✅ CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— **议题已收口，判据已耗尽**：
> ① 主体（audit 到底是什么、该拿它当什么判据）已于 2026-07-03 定稿落 [audit-positioning.md](../pipeline/decision/audit-positioning.md)；
> ② 它指向的目标态实现（`AUDIT-3CHECK` 三检查）已于 2026-07-14 由用户拍板**彻底砍掉**；
> ③ 两个触发前件都已成为过去 —— `DEFECT-D1-ROOT` 已实现并合 main（[#171](https://github.com/JunoChenZt/subagent-for-investment/pull/171)）、信源册 M1 已 close 于 2026-07-10。
> ⇒ 「厘清」这件事本身做完了，剩下的都在别的条目/文档里各自有家。
> **重开条件**：若将来再次出现「拿 audit 结果当可信度/安全闸」的用法争议，另立新条目（本条的调查轨迹仍可查）。
> 〔以下正文为 point-in-time 记录，**一字未改**。〕

> **✅ 定位定稿（2026-07-03·AUDIT-INTENT 主体收口）** — audit 定位 + 目标态三检查已定稿落 [audit-positioning.md](../pipeline/decision/audit-positioning.md)：audit = 表① 确定性核对（**数字/日期/来源**三检查·**目标态·码未实现** → 实现追踪见本文件 `AUDIT-3CHECK` 条目〔**⚠️ 该条目已于 2026-07-14 CANCELLED·三检查目标态不再实现**〕）；产出 = 合成 `audit_status`（沿用 7 态枚举·**向后兼容**·数字对不上复活死枚举 `audit_confirmed_mismatch`）+ rationale·喂 **fund_mgr 写作(主) + trace 给人看**·**confidence 溯源门本轮冻结不吃**（数字进 credibility/gate = 层② 的"闸门真值信号"·不预支）；指标口径残留 (c) 已就地关（`audit_passed` 率 = 引用对号覆盖率 ≠ 事实可靠率）。**剩"更广定位文案"随需·主体收口**。↓ 下方为前期记录（point-in-time·不改）。
>
> **🟡 两问已答·前置角色已解除·Q2 安全闸部分已落地（2026-07-02）** — ① 审计目的：设计 pass §2 一手核定为「**引用可解析性检查（citation-resolution）**·比'防抄错'还窄·从不比数字」；② audit_status 该不该当判据：**安全闸用途已停用**（[DEFECT-D1-ROOT](#defect-d1-root-gate-读展示表表③而非内源真值表表①-安全闸可被任意非-unverified-条目稀释含纯内源-sourced--过期源🔴-高优d1-病根独立于-m1) E简化 commit `66c411d` 已把 audit_status 移出 AD.7/C），**confidence 溯源资格门用途保留**（诚实用途·design pass §2 Q2）。∴ 本条对 D1-ROOT 的**前置阻塞已解除**。**未闭合的残留**（不阻塞·可择期）：候选方向 (c) 指标口径（"audit_passed rate" 别当"可靠率"）+ 更广的审计定位文案沉淀。下方为进入期记录（point-in-time·不改）。↓

> **一句话**：审计现在只把"引用了结构化源的说法"去核对"数字有没有抄对"——结构化源本就权威，所以这**实为"防抄错/防错引"检查，不是"核事实真伪/可信度"检查**。但它产出的"核实过"（audit_status）却被拿去**喂 confidence、喂安全闸（AD.7/C）当判据**。**意图（防抄错？核真伪？）与用途（可信度/安全闸依据）从一开始没对齐 → 能否达成目的存疑**。这是 DEFECT-D1-ROOT 的**前置**：D1-ROOT 问"gate 读错表（读展示副本）"，本条更前一步问"审计到底该干嘛、它的产出该不该当判据"。

- **强度**：🔴 元问题（本身非"不安全 bug"·不安全的是下游 A/D=DEFECT-D1-ROOT；但它是整族修法方向的**前置定位**，不厘清则 A/B/C 都是在定位不清的机制上打补丁）。
- **两个必答问题（本条的核心任务）**：① 审计的目的 = "防抄错/faithful-citation" 还是 "核事实可信"？② 审计产出（"核实过"）该不该继续当 confidence/安全闸的判据？
- **为什么现在这机制说不通（实测支撑·美光 e2e 2026-07-02）**：
  - 若目的=防抄错 → 范围极窄（40 条事实仅 7 条引了结构源）、且结构源数字（价格）本不太会被编 → **杀鸡用牛刀且没必要**。
  - 若目的=保证事实可信 → 决策真正吃劲的事实（判断/进出场价位/宏观逻辑）**天生不在结构源里、审计永远够不着** → **达不成**。
  - **就算换 A 股（内源覆盖全），此定位问题依旧成立**（只是抄的对象更多）——故非"美股覆盖薄"能解释。
- **候选方向（不预设·须设计讨论）**：(a) 审计明确定位为"防抄错"、其产出**不再直接当可信度/安全闸判据**（安全闸改读别的真值信号）；(b) 扩审计覆盖更多事实类型（难·结构源够不着判断类）；(c) 保持现状但**显式承认边界 + 改指标口径**（"audit_passed rate" 别当"可靠率"）。
- **触发条件**：启动 DEFECT-D1-ROOT 设计 / 信源册 M2 **之前必先厘清**（前置）；或用户随时拍。
- **为什么延后**：元/设计级·牵动 audit + confidence + gate 三层·超 M1·须独立设计 + 真实 e2e 印证；且 T3 在跑先不搅。
- **进入时点**：2026-07-02（美光 e2e·T3.2 追问 audit 7/40 一路追出）。**预估**：设计为主（先出"审计定位" pass·决策级·可能不写码或触发大改）。**配额**：DEFECT-* 族·不占 lettered 配额。
- **关联**：**前置于** [DEFECT-D1-ROOT](#defect-d1-root-gate-读展示表表③而非内源真值表表①-安全闸可被任意非-unverified-条目稀释含纯内源-sourced--过期源🔴-高优d1-病根独立于-m1)；完整非技术整理见 [audit-gate-problems-2026-07-02.md §1](../observations/audit-gate-problems-2026-07-02.md)；机制全图 [gate-mechanisms-map.md](../pipeline/decision/gate-mechanisms-map.md)。B/C 见 [S2 §9.1](../roadmap/S2.md)。

### AUDIT-3CHECK. audit 三检查实现（数字 / 日期 / 来源）（❌ CANCELLED · 2026-07-14 用户拍彻底砍）

> **❌ CANCELLED（2026-07-14 用户拍·彻底砍·非 deferred）**：审计三检查（尤"数字对不对"= 输入侧抓编数字 grounding）**取消实现**。理由：fund_mgr 打码修复系列的 **Path B（输出侧验章门·[fundmgr-mask-fix-series §4](../plans/fundmgr-mask-fix-series-2026-07-14.md)）已兜住"错数字不到读者"的安全底线**；AUDIT-3CHECK 的输入侧"别写整条"只是 UX 增益（省略 vs 涂占位）+ 原意兑现，**非安全必需** → 不值这承重大工程。**连带**：E1 audit_status 枚举收 4 值里 `audit_notpassed`（= 旧 confirmed_mismatch/failed）**永无生产者**（AUDIT-3CHECK 曾是唯一可能的生产者）→ 现为永久占位（靠"4 类分类完整性 + 门 A 防御"支撑·非"预留 AUDIT-3CHECK"）。**不占配额·作 CANCELLED 记录留存**。下方为立账/实证期历史记录（point-in-time·不改）。↓
>
> **一句话（历史）**：[audit-positioning.md](../pipeline/decision/audit-positioning.md) 定稿的 audit 目标态三检查（数字对不对 / 日期质量 / 来源）**设计已定 · 代码未实现**——现状 audit 只做"来源存在性"半项（数字丢弃 · 日期不看）。本条曾追踪把三检查落码〔已 CANCELLED〕。
>
> **📊 2026-07-06 定量实证（M1-T11 e2e 计划外发现·加重本条优先级论据）**：存在性半项的污染被量化——T11 前基线 run 26/40 fact 拿到 `audit_passed`，其中**大多数是乱贴买来的**（PE 42.27 挂 `REF#Y-007`=price 编号·编号存在即 pass·数值根本没核）；T11 修正 citing 后同标的 run 只剩 3/41 真锚表①的 pass。即**存在性半项曾放行 ≈23 个未核值 fact 进 audit_passed→confidence 老路（可达 verified）**。数字检查（本条 scope ①）正是堵它的。evidence = [m1-t11-e2e/EVIDENCE.md §2](../observations/m1-t11-e2e/EVIDENCE.md)。

- **强度**：🔴 承重（改 audit 判定行为 · 影响 fund_mgr 写入正文闸门；须测 · 含 mutation）。**非 gate 改动**（confidence 溯源门本轮冻结 · 数字进 gate = 层②）。
- **设计真值源**：[audit-positioning.md §4-5](../pipeline/decision/audit-positioning.md)（三检查确定性判据 + 合成映射复用 7 态枚举 + 消费路由解耦）。
- **scope**：① 数字**浅版**（源值↔水印值一致 + 表① 那行须有真值 + 接住 DS-0 `watermark_claim_mismatch` 软 flag）→ 复活 `audit_confirmed_mismatch`；② 日期**复用 confidence 新鲜度规则**（不另定阈值 · 防打架）；③ 来源补"来源名非空"；④ 合成 `audit_status`（复用 7 枚举·**status 零 schema 改**）供 fund_mgr + trace；⑤ **confidence 溯源门解耦**——读独立"来源/存在"信号（**行为等价冻结·same facts pass·守 D1-ROOT**），**不读被数字/日期收严的合成 status**（可能需 additive provenance 字段·非 status enum 改）。
- **子项 / parked**：数字**深版**（给 fact 加结构化引用值 · audit 独立硬核"说法数字==源值" · 需改 schema）—— 触发才做 · 不在首轮。
- **边界铁律**：不新增任何 audit→安全闸 路（守 D1-ROOT 成果）；confidence 溯源门**行为冻结**（same facts pass·判定集合不变）——读法解耦到独立"来源/存在"信号，**不读被数字/日期收严的合成 status**（否则合成变严会间接改 gate·违 D1-ROOT）。
- **DoD**：确定性判据单测（三检查逐档 + 合成映射）+ mutation 证 load-bearing + fund_mgr 写入闸门 before/after + **confidence 溯源门判定集合 before/after 不变（证 gate 路冻结·守 D1-ROOT）** + fresh-run e2e（承重 · 验真实标的三检查产出正确、无误伤）。
- **进入时点**：2026-07-03（AUDIT-INTENT 定位定稿派生）。**预估**：中（audit_node + 判据函数 + 测；不动 gate/confidence 读法）。**配额**：DEFECT-* 族 · 不占 lettered。
- **关联**：定位 = [audit-positioning.md](../pipeline/decision/audit-positioning.md)；前身 = 本文件 `DEFECT-AUDIT-INTENT` 条目；正交 = 层②（本文件 `DEFECT-D1-ROOT` 残留）。

### DEFECT-D1-ROOT. gate 读展示表（表③）而非内源真值表（表①）→ 安全闸可被任意非-unverified 条目稀释（含纯内源 sourced / 过期源）（🔴 高优·D1 病根·独立于 M1）

> **✅ 已实现（2026-07-02·组合修法 E简化+层① 路2a）** — 分支 `auto/D1-ROOT`·code+tests commit `66c411d`（**squash 合 main = `6f816a5`/[#171](https://github.com/JunoChenZt/subagent-for-investment/pull/171)**·`66c411d` 是合并前分支 commit·非 main 祖先）·e2e evidence `241f403`。**过期孤证（`sourced_outdated`/`stale`）现计入 AD.7/C 安全地板**（表③ 加 `is_outdated` 列·装配期从 confidence 带出·credibility 显示值不变）；AD.7/C **只读表③单判据**（去 `external_knowledge_refs`/`audit_status` 第二读 = 落定 P5 audit_status 停当安全闸判据）；新鲜单源仍放行（P2 守窄地板）。DoD 全过：2306 pytest 绿 + mutation 证 load-bearing + G4 两跑（真链路 resume 验无 over-fire·构造回放验 fire）+ quality gate 0 hard-fail（evidence = [D1-ROOT-e2e/EVIDENCE.md](../observations/D1-ROOT-e2e/EVIDENCE.md)）。**层② 架构解耦暂不需**（组合修法已闭合 D1 场景·如未来需表③退纯展示再议·随 AUDIT-INTENT）。下方为设计/立账期历史记录（point-in-time·不改）。↓

> **前置** = [DEFECT-AUDIT-INTENT](#defect-audit-intent-审计机制定位待厘清防抄错被当可信度安全闸判据🔴-元问题defect-d1-root-前置)（审计目的不清·先厘清再谈本条修法）。〔前置指针放正文·不进标题 → 保标题 anchor `…病根独立于-m1` 稳定·入站链不失效〕

> **一句话**：D1 的**症状**是"外源经附录稀释安全闸"（M1/T3 消症状）；**病根**是安全闸（AD.7/C）把**给人看的展示表（表③ `references_appendix`）当判据**，而不读**内源真值表（表①）**——于是表③里**任何**非-`unverified` 条目（含纯内源、含过期孤证）都能把安全闸摁住不 fire。这条与外源无关、撤外源关不掉，**独立于 M1**，2026-07-01 T3 核查2 坐实后正式立账（此前 = dataflow §15.5 / backlog M1 stub 里的"待立独立条目"占位）。

- **强度**：🔴 高优（安全方向 —— 放行本该拦的可执行价位，非误伤；北极星相关）。
- **触发条件**：M1（T1–T10）收口后，或用户决定动"gate 读哪张表 / 怎么判"时优先启动；安全向可提前独立排（优先级由用户定）。**不与 M1 同 session 顺手做**（防 scope 滑·M1 边界焊死"不改 gate 判据"）。
- **任务**：决定并实现 gate 判据来源。三条候选路、**未预设答案·须先设计讨论**：① gate 改读表①（内源真值）而非表③展示表 —— 最正、动 gate 读哪表、改动最大；② 保留读表③但**收紧"哪些 credibility 档算'该拦的 unverified'"** —— 尤其 `sourced_outdated`/`stale`（过期源）、单域名单源不该算"可信到不拉闸"；③ 表③装配时不把纯内部条目贴成非-`unverified`。三路可组合，先出设计 pass。
- **机理（核查2 一手核·2026-07-01）**：`should_hard_block_unverified_execution`（[risk_gate.py:302](../../src/committee/agents/risk_gate.py)）`all(e.credibility=="unverified")` 读的 `web_refs = list(decision.references_appendix)`（[risk_gate.py:293](../../src/committee/agents/risk_gate.py)）= 表③；表③由 `_build_references_appendix`（[base.py:2343](../../src/committee/agents/base.py)）装配，经 `_CONFIDENCE_TO_CREDIBILITY`（[base.py:1592](../../src/committee/agents/base.py)）把内源 finding/DS-0 fact 的 `verified→verified`、`sourced→web-single`、`sourced_outdated→web-single`、`stale→web-single`（均非-`unverified`）。∴ 一条有源新鲜（哪怕单域名 / 哪怕过期）的**纯内源**条目即让安全闸不 fire。
- **为什么延后**：M1 边界焊死"只消症状（外源触发）·不改 gate 读哪表/怎么判"；病根改动面大 = 承重·真改判定方向·须独立设计 + **fresh-run e2e 印证防翻转**（不能只靠构造单测）。不让 T3/M1 顺手吞（[[feedback_treat_scope_no_creep]] 治标不扩界 + [[feedback_read_boundary_intent_before_expanding]] 拆边界前先读当年为什么立）。
- **进入 backlog 时点**：2026-07-01（T3 开工只读核查 = 核查2 坐实"内源自身即稀释 gate"）。
- **预估工作量**：中-重（改 gate 判据面 = 承重·须 fresh-run e2e）；先出只读设计 pass 再定路①/②/③ 与排期。
- **关联**：症状 = [信源册建册 M1 / T3](#信源册建册-出处收敛单一贯穿真值源✅-大任务-m1-主体完成close-2026-07-10三表定型11-子任务收口t104剥离为独立挂起条目全链-e2e-1300) 的 D1 行；[dataflow §15.5 D1 修正](../pipeline/dataflow-whole-pipeline.md)。相关族：[X D1 hard contract 争议](#x-d1-hard-contract-强读弱读争议元层面冻结✅-closed-2026-07-08-close-by-decision保留位置)（另一个 D1 议题·正交）。
- **🚀 只读设计 session 启动提示词** = [DEFECT-D1-ROOT-只读设计-handoff.md](../handoff/DEFECT-D1-ROOT-只读设计-handoff.md)（2026-07-02·先答 AUDIT-INTENT 两问 + 只读核实一手 → 定 approach → 设计 pass → 用户裁决·**不授权不进实现**）。
- **📐 设计 pass 已产出（2026-07-02·只读·未改码）** = [DEFECT-D1-ROOT-design-pass-2026-07-02.md](../plans/DEFECT-D1-ROOT-design-pass-2026-07-02.md)：AUDIT-INTENT 两问已答（审计=引用可解析性检查〔比"防抄错"还窄·从不比数字〕·`audit_status` 不配当安全闸真值）；**建议分两层** —— 层①=立即安全修复（过期源 `sourced_outdated`/`stale` 计入 AD.7/C fire·无设计争议·止血），层②=架构解耦（表③退纯展示·gate 改读为闸门专造的真值信号·**依赖 AUDIT-INTENT 先决**·顺带解锁 T4+化解 D/E/F）；**R5 关键区分**：安全闸读表③+单源不 fire=当年窄地板设计如此·过期源塌进 `web-single`=设计未预见的安全洞；**5 个用户裁决点 P1–P5**（尤 P2 单域名单源是否 fire=设计取向题·P5 audit_status 停当判据=元决策）。**⚡ 2026-07-02 同日反转 → 采纳组合修法「E 简化 + 层①」并授权实现**（用户"两个一起做"）：**E 简化**=AD.7/C 只读表③、去 `external_knowledge_refs`/audit_status 分支（顺手落 P5=audit_status 停当安全闸判据·绕开 AUDIT-INTENT）；**层①**=过期源 `sourced_outdated`/`stale` 计入 fire（路 2a=表③ 加 `is_outdated` 列·不改展示·P3）；**范围**=只过期源 fire·新鲜单源仍放行（P2 守窄地板）。两者配对才闭合（只简化→过期源仍溜·只层①→E 冗余/哑火还在）。**层② 暂不需**（组合已闭合 D1 场景）。承重·北极星 → 走完整 workflow·DoD 含 **fresh-run e2e**。实现启动提示词 = [DEFECT-D1-ROOT-实现-handoff.md](../handoff/DEFECT-D1-ROOT-实现-handoff.md)（拆解 G1–G4）。**只读设计 session 未动代码·实现另起。**

### NAMING-EXTKREFS. `external_knowledge_refs` 命名误导 —— 名带 "external" 实为正文引用的**内部** fact 编号（🟢 低优·命名债·非行为 bug）

> **✅ CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— **零行为收益、却要动存档兼容**：
> 处置②（补 docstring 显式警示）2026-07-02 已做；处置①（改名）= schema 字段改名 **= 动 checkpoint/archive
> 序列化、须兼容旧 replay**，属承重改动，换来的是**零行为变化**。判定不值得单独做。
> 🔑 **关掉零损失**：将来动它的人需要知道的**已经完整留在代码里** —— [decision.py](../../src/committee/schemas/decision.py)
> 字段定义上方三行写清了「这个 external 不是联网外源」「改名要动序列化」，本次又补了一句
> 「条目已关·本注即真值源」，免得后人去翻一个已关的条目。
> **重开条件**：若将来本来就要做一次 breaking 的 schema 迁移 —— 那时顺手改名，不必复活本条。
> 〔以下正文为 point-in-time 记录，**一字未改**。〕

> **一句话**：字段 `external_knowledge_refs` 的 "external" 会让人误读成"联网搜来的外部来源（external **websearch**）"，但它其实是**委员会内部** DS-0 事实里、被 fund_mgr thesis 正文实际引用的那些的 **fact 编号列表**（`{ref:fX}` 提取），**跟互联网/外源册毫无关系**。这个撞词在 DEFECT-D1-ROOT 的 /review（PR #171）期间把评审 subagent 和用户都绕进去过。

- **强度**：🟢 低优 —— 纯命名/文档债，**零行为影响**（不改任何判定）。
- **一手证据**：定义 [base.py:3437](../../src/committee/agents/base.py)（`decision.external_knowledge_refs = sorted(cited_ids)`·从 [base.py:3387-3399](../../src/committee/agents/base.py) 的 `{ref:vX}/{ref:fX}` 占位符提取；行号已按现 main 刷新）；schema [decision.py:483-485](../../src/committee/schemas/decision.py)（注释自述 = "DS-0 facts_inventory 中被 fund_mgr thesis 实际引用的 fact_id 列表"）；**D1-ROOT 后唯一存活消费** = [e2e_quality_gate.py:349](../../src/committee/e2e_quality_gate.py)（`total_refs` 计数·安全闸已不再读它）。
- **为什么误导**：与 external **websearch**（M1 外源册 `external_websearch` / `build_web_references`）**同顶 "external" 前缀但指完全不同的东西**——一个是联网外源、一个是内部被引 fact 编号。命名坑族同类：[[信源册 M1 命名锁定]]（"名字=红线提醒器"）。
- **候选处置**：① **改名**（如 `cited_fact_refs` / `thesis_cited_refs`）—— 但这是 **schema 字段改名 = 动 checkpoint/archive 序列化**，须兼容旧 replay（承重·非纯文本改名·不能顺手做）·**仍 pending**；② **最小**：保留字段名、补 docstring 显式警示"**非** external websearch·是正文引用的内部 fact 编号"——**✅ 已做（2026-07-02·[decision.py:483-488](../../src/committee/schemas/decision.py) 补警示注释）**。① 随将来 schema 批量演进再议。
- **进入时点**：2026-07-02（DEFECT-D1-ROOT /review 派生）。**配额**：NIT/命名债·不占 lettered 配额。
- **关联**：出处 = [DEFECT-D1-ROOT](#defect-d1-root-gate-读展示表表③而非内源真值表表①-安全闸可被任意非-unverified-条目稀释含纯内源-sourced--过期源🔴-高优d1-病根独立于-m1) 的 /review。

### DEFECT-R5-04. 印证语义层 — 比数值不够，要比"带数字的内容"是否说同一件事（⏭️ 另记·拔支柱2·不进本轮）

> **✅ CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— **父题的目的已放弃**：
> 本条是 [DEFECT-R5-02](#defect-r5-02-corroboration-印证池未按-fact-scope--不相干-fact-共享常见整数巧合凑成-verified🔴-阻塞-web-verified-放开) 的支柱2，
> 而两者共同服务的目的（放开「网页核实」）已随 PR2 [#161](https://github.com/JunoChenZt/subagent-for-investment/pull/161) 关门放弃。
> ⚠️ **注意这条与 R5-02 的失效方式不同**：本条的前件（「建册铺完底座」）**已经成立**（M1 close 于 2026-07-10）——
> 成立的是**手段**，消失的是**目的**。∴ 不是「等不到」，是「等到了也没意义」。
> **重开条件**：同 R5-02 —— 重开网页核实这条路时一并重新设计。
> 〔以下正文为 point-in-time 记录，**一字未改**。〕

- **状态**: 🆕 **另记（2026-06-25 用户拍【分步】之⏭️）**。**不进本轮、不卡小修、不卡 PR2。** 是 [DEFECT-R5-02](#defect-r5-02-corroboration-印证池未按-fact-scope--不相干-fact-共享常见整数巧合凑成-verified🔴-阻塞-web-verified-放开) 的**支柱2**（差距表 #7）。
- **机理**: 🩹 小修（#6）拔的是**支柱1（池未 scope）**。即便收紧到 fact 自己的来源子池，**纯数值匹配仍可能让"恰好同数、说的不是同一件事"凑印证** → 要再拔**支柱2**，需在**收紧后的小池里**比"带数字的内容"是否指同一实体/同一指标。
- **强度**: 🟡（支柱1 收池后残留暴露面已大幅缩小；本条是更精确的二道闸）。
- **关键约束（先确定后判断 + 控 AI 不确定性）**: 语义比对靠**理解内容 = 有 AI 不确定性**。按"先确定后判断"**放小修（确定性收池）之后**；且要想清怎么控不确定性——倾向**只在数值已匹配的基础上做内容确认**（而非自由判语义），前层（收池 + 数值匹配）兜底，避免引入新的"AI 判真假"红线（verify.py 红线）。
- **触发条件（2026-06-26 建册评估后定）**: **建册铺底座后【单独 PR 叠上】，不并建册 PR**。理由：建册登记"带数字内容"天然给语义比对备料（底座耦合），但本条引入 **AI 语义判断 = 与建册的确定性/golden 验收风险类别不同**，隔离开避免 AI 不确定性污染建册的确定性闸。详 [建册评估 §4.3](../plans/provenance-source-registry-reeval-2026-06-26.md)。
- **进入时点**: 2026-06-25（R5-02 分步决策另记）
- **预估工作量**: 中（设计抉择 = 怎么控 AI 不确定性 + 实现 + 测试），**这轮不估细**。**配额**: DEFECT-* 族、不占 lettered 配额。

---

### DEFECT-DSML-PARSE. deepseek-v4-pro 吐 `<｜｜DSML｜｜tool_calls>` 标记不被 agent_loop 解析 → analyst 降级（🟡·非 R5-02 引入·独立排）

- **状态**: 🩹 **止血已做·已合 main `4f62cc9`（PR #163，2026-06-26）**——候选①（DSML 解析容错 shim）已实现并合入主干、全量 2264 绿；两个健壮性改进（A 宽容式识别 / B 降级监控）登记下方【待触发再做】。**非 R5-02 引入、不卡 R5-02 PR。**
- **现象**: `commodity`/`political`（`.env` 走 `deepseek-v4-pro`）的 analyst 联网调用，模型吐 `<｜｜DSML｜｜tool_calls>\n<｜｜DSML｜｜invoke name="finish">…` 这种 DeepSeek 原生 tool-call 标记（special `｜｜DSML｜｜` token）。[`agent_loop`](../../src/committee/tools/agent_loop.py) 靠 LangChain 结构化 `response.tool_calls` 认工具调用，DSML 作纯文本不被识别 → 当成 final 文本 → JSON 解析报 `No JSON object in LLM output` → ValueError → analyst 降级 fallback。
- **影响**: **降级 fallback、非崩**（analyst node 捕获 ValueError → `validate_with_fallback` → 质量降级报告，pipeline 续跑、决策照出）。R5-02 e2e Q1 实测：仍出完整 SELL 决策、`prose_gate_status=verified`、0 traceback；受损 = 这俩角色报告质量 → 下游 debate/facts 偏弱。本次 5 次 DSML parse fail（commodity+political 多 iteration），对 v4-pro 这轮一致非偶发。
- **⚠️ 非 R5-02 引入（坐实，非"看着无关"）**:
  - **结构**：R5-02 改动仅 [base.py](../../src/committee/agents/base.py) decision 节点（`_anchor_tool_outputs_by_source`/`_derive_all_confidence`/`_run_verification`），**0 行碰 `agent_loop` 解析器 / `make_analyst_node`**——结构上不可能影响 analyst 层 tool-call 解析。
  - **实证（R6，origin/main tracked）**：[run-D](../observations/fm-refactor-spec/run-D-hot-zhongji-20260616/seg2-research.calls.jsonl)（2026-06-16 **pre-R5-02**）commodity/political/technical **同样走 deepseek-v4-pro**，但研究段 **0 DSML / 0 fallback**——同模型同角色当时正常。→ DSML 是 **deepseek-v4-pro 输出格式自 2026-06-16 起的 provider 侧漂移**，与 R5-02 代码无关。
- **修法（已定·别再翻）= 候选①（DSML 解析容错 shim）**: 三候选评估后定①。**为什么不是②③**：② deepseek 现状本就走 [`ChatOpenAI`/`bind_tools`](../../src/committee/agents/base.py)（`model.startswith("deepseek")` 分支），病在上游把 DSML 塞进 `content`，"真改路"要动 `DEEPSEEK_BASE_URL`/endpoint = **碰 .env 红线且不治本**；③ 改 per-role 模型 = **碰 .env 红线、只躲不修**，且治不到同病的 `fund_mgr_verify`（实证 `deepseek-v4-flash` 同样吐 DSML，[seg9-decision.calls.jsonl](../observations/fm-refactor-spec/prose-gate-fix-hotverify-20260616/seg9-decision.calls.jsonl)）。① 不碰 .env、治 deepseek-v4-* 全家族、最坏不劣于现状 → 唯一既不碰红线又治本的。
  - **① 做了什么**: [agent_loop.py](../../src/committee/tools/agent_loop.py) 在「`tool_calls` 空」分支前加 shim——`content` 含 `｜｜DSML｜｜`（`｜`=U+FF5C）标记时 regex 解析出结构化 tool_calls、重建干净 `AIMessage`（保 message 历史一致）喂回现有 `tool_map`/budget/gather 下游（**unknown tool 走现有 error 路、不特判**）；解析不出 → fall through 回现有 fallback。[tests/test_dsml_parse.py](../../tests/test_dsml_parse.py) 10 测试（正常零影响 / DSML 解析回 structured / 解析失败退回现状不崩），before/after 证旧码同输入抛 `ValueError`·tool 未被调用→shim 后 tool 正常执行。全量 2264 绿。
  - **① 的已知边界（写明防误判）**: 只认 DSML 这**一种**方言；现象里 `invoke name="finish"` 这类「DSML 包终答」会按 unknown tool 走 error 路（不特判、最坏=现状），非完美恢复——通用化留**改进 A**。
- **🔧 改进 A（宽容式工具调用识别·【待触发再做·现在不做】）**: 认任何「工具名+参数」结构的方言，不死磕 DSML。**触发条件（写死）= 出现【第二种】非标准工具调用格式时再做**。**为什么现在不做**：现仅 DSML 一个样本，单样本上猜「通用方言规则」易猜错（宽了把正常文字误判为工具调用、严了兜不住新格式）；等出现第二种、有两样本能归纳规律时才做得准。现在做 = 在未发生假设上过度设计，违反「不基于未发生假设做大改」。**与①关系**：①是 A 的安全垫脚石——①最坏不劣于现状，将来上 A 时①可被 A 取代或保留、**不返工**。
- ~~**🔧 改进 B（角色降级监控/告警）**~~ **❌ 2026-09-08 删除（用户当日裁）** —— 原判据写的是「待评估排期」，属 [§4.1](#41-新增-backlog-条目) 明令禁止的形态（依赖将来有人回头排期，没有任何动作会撞见它）。**命题本身没丢**：「盯任何角色 fallback/降级这个通用信号、超阈告警」正是 [BK](#bk-静默降级可见化--系统悄悄降级时必须留痕2026-08-07-闸门矩阵第-2-层挂起) 的题目，已由 BK 承接 —— 本条不必各记一份。
- **触发条件**: ① = ✅ 已合 #163（止血落地）；**改进 A = 第二种非标准 tool-call 格式出现时**（本条今日唯一活口·合法事件型）。~~改进 B = 待评估排期~~ **已于 2026-09-08 删除**（判据违规·命题移交 [BK](#bk-静默降级可见化--系统悄悄降级时必须留痕2026-08-07-闸门矩阵第-2-层挂起)）。
- **进入时点**: 2026-06-26（R5-02 e2e 冒烟）。**配额**: DEFECT-* 族、不占 lettered 配额。

---

### DEFECT-WEBSEARCH-BRAVE. web_search 默认引擎集含宕机的 brave → 整次搜索拿不到结果 ✅ CLOSED 2026-07-29（close-by-completion）

> ## ⚠️ **2026-07-30 前向标注（R7）：本条的处置已被 REVERTED —— 默认引擎又改回 `brave,duckduckgo`**
>
> 下方 07-29 banner + 正文全部保留为 point-in-time 记录，**不改**。当时 N=10 复测只量了
> **非空率**、未量**相关率**：bing 确实每次都有返回，但 35% 的返回内容与 query 完全无关
> （SEO 污染·HTTP 200 + 零 error log）。同日 A/B 显示 bing 的边际贡献 = **+1 有用 / +24 垃圾**
> → **DEFECT-WEBSEARCH-RELEVANCE**（2026-07-30 处置 ①）把默认改回 `brave,duckduckgo`。
>
> **本条「brave 是死引擎（0/10 非空）」的结论不变**——只是「换成 bing」并未达成
> 「让 analyst 拿到 web 结果」的目标，且引入了更隐蔽的失败形态。
> 真正的解法是换搜索后端（Cloudflare 侧·仍未做）。
> 证据：[SEARCH-ENGINE-REGRESSION.md](../observations/regression-e2e-20260730/SEARCH-ENGINE-REGRESSION.md)

> **✅ 已修（2026-07-29·PR 见下）**：默认 `"brave,duckduckgo"` → `"bing,duckduckgo"`。
> 修法 = cherry-pick 2026-07-02 就已写完测完、但一直躺在本地分支 `claude/awesome-lamport-dec369`
> 从未进 main 的 commit `c8572c8`（2026-07-29 清点本地未推内容时捞出）。全量 3020 passed。
>
> **⚠️ 开工前按本条要求做了复测（N=10/引擎·2026-07-29·经代理 `$HTTP_PROXY`=13004），结论保留但机理已变——原描述 stale，据实更正**：
>
> | 引擎 | 有结果 | 空 | 中位耗时 |
> |---|---|---|---|
> | `brave` | **0/10** | 10 | 1.5s |
> | `bing` | **10/10** | 0 | 1.2s |
> | `duckduckgo` | 3/10 | 7 | 1.1s |
> | **`brave,duckduckgo`（修前默认）** | **2/10** | 8 | 1.5s |
> | **`bing,duckduckgo`（修后默认）** | **10/10** | 0 | 1.3s |
>
> - **结论不变**：brave 仍 0/10、该去；bing 仍是唯一稳的主力 → 改法照旧成立。
> - **🔴 机理已变（本条正文下方"现象/机理"段所述已不复现）**：brave **不再挂住**（中位 1.5s 就返回，
>   不再干等到 `_TOOL_TIMEOUT=8.0s`）→ **不再产生 httpx ReadTimeout / 空 error log**。
>   现在的症状是**快速静默返 0 条** —— **比原来更隐蔽**：没有任何 error log，
>   analyst 只是悄无声息地拿不到 web 结果。修前默认实测 **8/10 次返空**。
> - **duckduckgo 也漂了**：原记"单跑 ok、混用间歇"，现在单跑 3/10（更不稳），
>   但与 bing 组合 10/10 不拖后腿 → 保留作次选的判断仍成立。
> - **教训坐实**：本条"开工前先复测·别照抄结论"的提醒**接住了一次真漂移**——
>   若照抄旧机理写 PR，会把一个"静默返空"的缺陷描述成"超时报错"，误导后来者排查方向。
>
> **顺带项处置**：① "单引擎挂不整体 fail" 的健壮性改进 —— 本次实测显示当前**不会**因单引擎
> 拖垮总时长（组合 10/10、中位 1.3s），该顾虑的触发前提已消失 → **不做**；
> ② memory `project_api_connectivity_followup` 端口口径 = 已按"以 `$HTTP_PROXY` 为准"记（本次实测仍 13004）。
>
> **下方为立条时（2026-07-02）的 point-in-time 记录·正文不改**（机理段已被上方 banner supersede）。↓

- **强度**: 🟡（degraded 非 broken·有 env 绕过 `COMMITTEE_EXTERNAL_SEARCH_ENGINES`）。
- **现象/机理**: 默认 `EXTERNAL_SEARCH_ENGINES="brave,duckduckgo"`（[config.py:201-206](../../src/committee/config.py)）·`brave` 引擎持续无响应 → Cloudflare Worker 搜索代理干等 → 超本地 `_TOOL_TIMEOUT=8.0s`（[definitions.py:22](../../src/committee/tools/definitions.py)）→ httpx ReadTimeout（`str(e)` 空）→ [definitions.py:177-179](../../src/committee/tools/definitions.py) 记空 `tool web_search failed:`（难定位）→ 8 个 analyst 拿不到 web → 无据低质报告（如 macro Overweight/evidence=0）。**非代理/VPN 挂**（本机代理活·google/example.com 直接 200）。
- **实测（2026-07-02·经代理 `HTTP_PROXY=13004`·端口会漂移）**: `bing` 10/10 稳 ✅·`duckduckgo` 单跑 ok 混用间歇·`brave`/`google` 死 ❌·`wikipedia` 0。
- **任务**: [config.py:211](../../src/committee/config.py)（`EXTERNAL_SEARCH_ENGINES` 默认赋值行·非 206=URL）默认 `"brave,duckduckgo"`→`"bing,duckduckgo"`（去死引擎·保 bing 主力）·运行时仍可 env 覆盖。**开工前先复测引擎**（可用性会漂移·别照抄结论）。
- **为什么延后**: T3.2 美光 e2e 中临时 env 绕过·**非 T3 scope**·独立小改（改 config 默认值一行 + 复测）。**已建 spawn `task_af6ea12b`**（自带复测命令 + 改法 + DoD + 边界·用户决定另开 session 做）。
- **触发条件**: 立即可做 / 下次动 web_search 时；用户已决定另开 session。
- **进入时点**: 2026-07-02（美光 e2e·T3.2 surface）。**预估**: 轻（config 默认一行 + 复测 + 单测/全量绿）。**配额**: DEFECT-* 族·不占 lettered 配额。
- **顺带（同任务·可选）**: ① 更大健壮性——"单引擎挂不整体 fail"（当前总超时即整体 failed）另评估·别顺手做；② 更新 memory `project_api_connectivity_followup` VPN 端口 13001→实测 13004（端口漂移·宜记"以 `HTTP_PROXY` 为准"非钉死）。

---

### DEFECT-PROD-ADVISORY-MODEL-STALE. `.env.prod` 三 advisory 角色未同步 2026-06-09 选型实验 → prod 跑高价模型 ✅ CLOSED 2026-07-08 (close-by-completion·已部署生效)

- **状态**: ✅ **已修 + prod 部署生效（2026-07-08·用户在服务器执行·Claude 给命令）**，收敛分流（非"三个都回 deepseek"）：
  - **historian/economist → `deepseek-chat`**：确属 stale drift（原 gpt-4o/gemini），改回 deepseek 省钱、简单 schema 无 AF、对齐 2026-06-09 实验精神。**已部署生效**：prod 服务器 `/srv/committee/.env.prod` sed 改两行（备份 `.bak-20260708`）+ `docker compose up -d backend` + `docker exec ... ROLES[r].model` 复验 resolve = `deepseek-chat`（本地工作树同步已改）。
  - **political → 保留 `oc/gemini-2.5-pro`（有意例外·用户拍·非 stale）**：因 deepseek-v4-pro 撞 backlog AF（强制情景矩阵 schema 反复 JSON parse → DATA_INSUFFICIENT 兜底），gemini 绕开该洞。**贵 ~5-6x 作为绕 AF 的代价接受**·截断由 AM〔`MAX_TOKENS_ACADEMIC`=12288〕兜。political 根治交 **backlog AF**（schema 简化/JSON 重试），AF 修好后可再评估切 deepseek。
  - **Close**: historian/economist stale drift = 已修+部署生效（本条主体）；political=gemini 经排查**重定性为有意保留**（绕 AF·非 drift），转 backlog AF 跟。本条 close-by-completion。
  - 原确认：用户 2026-07-08 拍"historian/economist 是 2026-06-09 实验后忘了同步"。
- **强度**: 🟡（**成本浪费·非正确性阻断**——截断风险已由 backlog AM〔`MAX_TOKENS_ACADEMIC`=12288〕兜住；但 prod 三 advisory 角色跑比 deepseek 贵 ~5-6x 的模型）。
- **背景/机理**: [political-arms 实验（2026-06-09）](../observations/experiments/political-arms/decision-review.md)判定 political→`deepseek-v4-pro`，**真正理由=性价比**（gemini-2.5-pro 关 thinking 仍贵 ~5-6x、质量无碾压·line 82/88/92；截断只是触发症状，实验明确否决"加预算"line 33）。[config.py:166](../../src/committee/config.py) 代码默认已改 deepseek-v4-pro（引实验）。但 **`.env.prod`（untracked·含密钥·无 git 史）override 三 advisory 角色未同步**：`COMMITTEE_MODEL_POLITICAL`/`ECONOMIST`=`oc/gemini-2.5-pro`、`HISTORIAN`=`oc/gpt-4o` → 生产跑高价模型、与实验+代码默认矛盾。
- **⚠️ AM 成本交互（承 backlog AM）**: AM 把 advisory 角色 max_tokens 4096→12288。**若 prod 保持 gemini**，AM 放大这三个角色成本（gemini thinking token 照生成照计费·$10/M·实验明确"加预算只会更贵"）；AM 的"按实际用量计费"对 gemini 打折扣。→ 修 prod 回 deepseek 后此交互消失（deepseek 便宜·AM 预算地板对它无害·仍兜 gemini fallback）。
- **任务（ops 动作·非仓库改动）**: 在 prod 服务器 `/srv/committee/.env.prod` 删除三 advisory 角色 override 行（回落 code default deepseek-v4-pro）或显式设 deepseek → `docker compose up -d backend`。**改 `.env` = CLAUDE.md 红线·Claude 不自动改·须用户手动**。
- **待确认**: 本地工作树的 `.env.prod` 是否 = 部署源（若是，同步改本地那份·同样需用户授权/手动）。
- **触发条件**: 立即可做（用户已确认 stale）；下次 prod 部署 / config review 时一并。
- **进入时点**: 2026-07-08（AM 修复后核查 `.env.prod` 撞出·用户确认 stale）。**预估**: 极轻（删 3 行 env + 重启 + 冒烟）。**配额**: DEFECT-* 族·不占 lettered 配额。

---

### AZ. 活文档链接/模板同步小债（overview.md root-relative 链接 + `.env.example` 缺新 env）（2026-07-29 docs-audit surface）

> ## ✅ **CLOSED（2026-08-12·close-by-completion）** — 下方正文为 point-in-time 记录，**保留不改**
>
> **两半皆完**：
> - **链接半**（52 处 root-relative）：2026-07-29/30 docs 整理 A 档 `41552a3` 实修 55 处 + [#218](https://github.com/JunoChenZt/subagent-for-investment/pull/218)
>   入库 [`lint_doc_links.py`](../../scripts/lint_doc_links.py) 防复发。**2026-08-12 复扫确认 root-relative 0 处**（未复发）。
> - **env 半**（6 键）：随 BA 一并做完 —— [.env.example](../../.env.example) 补 `COMMITTEE_REGISTRY_*`×5 + `COMMITTEE_CLASSIFY_TIMEOUT`。
>
> **BG 触发动作已执行（非跳过）**：正文末尾那条 2026-08-03 前置要求「动手前先 grep 有没有测试在断该键的默认值」——
> 实查结果 = **`COMMITTEE_REGISTRY_REFRESH_HOUR` 站在雷上**（[test_security_registry_scheduler.py:52](../../tests/test_security_registry_scheduler.py#L52)
> 直断 `REFRESH_HOUR == 2`，而 [config.py:16](../../src/committee/config.py#L16) 在 import 时 `load_dotenv()` 读本机 `.env`）。
> ∴ 6 键**一律登记为注释行、不给生效赋值行**，且把这个理由写进模板注释供后人看，避免下一个人"顺手取消注释"。
> 〔BG 本身是常设触发型条目，**不随本条 close**。〕

- **强度**: 🟢（**纯文档可用性**·不影响任何运行行为；但违反 CLAUDE.md「链接规范」明文）
- **两半（合并登记·同属"改一次就完"的机械债，不值分两条占配额）**：
  1. **`docs/architecture/overview.md` 52 处 root-relative 链接**：写成 `](src/committee/policy.py)` 而非 `](../../src/committee/policy.py)`。文件都存在，但从 `docs/architecture/` 渲染会解析成 `docs/architecture/src/...` → **GitHub 上全部点不开**。**全仓仅此一个文件有该写法**（2026-07-29 脚本扫全 live docs：root-relative 52 处全集中于此，其余文档 0 处）——说明是该文件早期成文时的局部习惯，非全仓约定。
  2. **`.env.example` 缺两组新 env**：`COMMITTEE_CLASSIFY_TIMEOUT`（#210）与 `COMMITTEE_REGISTRY_*` 五个（AK [#211](https://github.com/JunoChenZt/subagent-for-investment/pull/211)：`_DB`/`_LAZY_FETCH`/`_LAZY_BUDGET`/`_AUTO_REFRESH`/`_REFRESH_HOUR`）。注意后者**真值源在 `security_registry/service.py`·`store.py`，不在 `config.py`** —— `.env.example` 与 overview §6 快照的「以 config.py 为准」免责句都盖不住它。〔overview §6 那半已在 [#214](https://github.com/JunoChenZt/subagent-for-investment/pull/214) 补上，此处只剩 `.env.example`。〕
- **为什么没并进 #214**：① 链接半改动量 52 处，会淹没那个 PR 的审计正文（审计的价值在"逐条附代码佐证"，机械替换混进去就读不出来了）；② `.env.example` 是配置模板不是 docs，混进 docs-only PR 破坏该 PR 的「零非 docs 改动」判据。用户 2026-07-29 拍：**都先不动·只记 backlog**。
- **触发条件**: 下次动 `docs/architecture/overview.md` 时顺手；或有人报告"文档链接点不开"；或下轮 docs-audit 一并做。
- **预估**: 极轻（链接半可脚本化 `sed`，改完跑一遍存在性校验；env 半 = 加 6 行注释）。**配额**: 占 1 个 lettered slot。

### BA. 本地证券名录 DB 未持久化到 volume（S2 首次部署起会每次重建清零）（2026-07-29 docs-audit surface）

> **🔧 2026-08-12 前提订正 + 仓库侧已预防（用户确认线上现状后改写）**
>
> **原标题写的「生产每次重建镜像清零」是现在进行时，这个时态不成立**：线上跑的是**旧的 S1 版本**，
> 名录功能（AK [#211](https://github.com/JunoChenZt/subagent-for-investment/pull/211)）属 S2、**根本没部署上去**。
> 故本条描述的浪费**尚未发生**，是 **S2 首次部署之后**才会开始发生的事。
> 〔机理断言本身 2026-08-12 已逐条复核，**全部仍成立**——错的只是时态与"已在发生"的暗示。〕
>
> **已落的预防（不依赖服务器）**：[.env.prod.example](../../.env.prod.example) 已带上
> `COMMITTEE_REGISTRY_DB=/data/security_registry.db`（本轮加）。∴ 将来若按运维手册
> `cp .env.prod.example .env.prod` 建新环境，**开箱即已修好、一次都不会白拉**。
>
> **仍欠的一步（只能用户手动·红线）**：服务器上**已存在**的 `/srv/committee/.env.prod` 是历史文件、
> 不会自动获得这行。S2 首次部署时须手动补进去，否则本条描述的浪费照旧发生。
>
> **∴ 本条不 close**：修法已备好，但**生产从未验证过**（重建后名录是否真存活、prewarm 实际耗时）。
> 拿"模板改好了"当"问题解决了"= 用未验证冒充已验证，不做。

- **强度**: 🟡（**成本/延迟·非正确性**——不崩、不给错答案；代价是每次部署多一次全量名录拉取）
- **机理（读码 + 读 compose 坐实）**: [`security_registry/store.py`](../../src/committee/security_registry/store.py) `default_db_path()` 在无 `COMMITTEE_REGISTRY_DB` override 时返回 `<repo root>/.cache/security_registry.db`；容器 `Dockerfile` `WORKDIR /app` → 实际路径 `/app/.cache/security_registry.db`。而 `docker-compose.yml` backend 只挂 `backend_data:/data`，`/app/.cache` **不在任何 named volume 内** → 镜像重建即清零。
- **为什么不致命**: 启动 lifespan 会 `prewarm`（[`server/api.py`](../../src/committee/server/api.py) `lifespan`）best-effort 重建；即便全失败也只是回落到"名录不可用"，`classify()` 名录相关步骤整体跳过、行为与 AK 之前逐字一致（AK 边界裁决 3）。所以这是**浪费**不是**故障**。
- **候选修法**: `.env.prod` 加 `COMMITTEE_REGISTRY_DB=/data/security_registry.db` 指进已有 `backend_data` volume（零代码改动）。**但改 `.env.prod` / compose = CLAUDE.md 红线·须用户裁决 + 手动执行**，故本条只登记不动手。〔2026-08-12：模板侧已预置，见顶部 banner；服务器上那份仍须手动补。〕
- **未验证的部分（诚实标注）**: 上述为**静态读码 + 读 compose 推断**，**未在生产实测**"重建后名录是否真的空 + prewarm 实际耗时"。真要动手前应先在服务器上 `docker compose exec backend ls -la /app/.cache` 与看一次启动日志坐实。〔2026-08-12 仍未实测，且**当前线上是 S1、跑不出这个现象**——实测只能等 S2 部署后做。〕
- **触发条件**（2026-08-12 收窄·原写"下次 prod 部署 / config review"过宽）: **S2 首次部署时**——把那行补进服务器上的 `.env.prod`，然后按 [plan §4.2/§4.3](../plans/BA-registry-volume-decomposition.md) 跑冒烟 + 重建验证。
- **close 判据**: 重建验证四条全过（文件跨重建存活 / 条数一致 / 启动日志无全量拉取 / 旧路径已空）。模板改好**不算** close。
- **进入时点**: 2026-07-29（docs-audit 核 AK 部署面时撞出）。**预估**: 极轻（1 行 env + 重启 + 冒烟）。**配额**: 占 1 个 lettered slot。

---

### BB. 段间 checklist ⑧ 的 `audit_passed ≥ 50%` 是空线（五次 run 全 6–13%）（2026-07-31 全链回归 e2e surface）

> ## ✅ **CLOSED（2026-08-03·close-by-completion）** — 下方正文为 point-in-time 记录，**保留不改**
>
> **处置比本条原 scope 大**：本条自己建议的「数字线 vs 历史归档对账」已于 07-31 做完
> （[对账报告](e2e-guide-threshold-audit-20260731.md)·11 正常 run + 4 对抗 run 回测·**12 条数字线只有 2 条有效**），
> 08-03 把结论整体落进 [guide](../observations/e2e-runs/segmented-e2e-guide.md)。
> **⑧ 本条**：`≥50% 判 ❌` → **observe**（只记录·仅 <5% 才排查·实测区间 6–47%），
> 并写明「真要用绝对线，得先重定 audit 的定位」。
> **连带落地**对账建议 1/2/4/5/6/7（⑥ 辩论 token 线 / 两条恒真项移交单测 / 存活探针标注 / 边界声明 / 校准惯例），
> 逐条登记见 [acceptance-standard §4](e2e-acceptance-standard.md)。**剩建议 3 需改 trace 代码 → 切出 BF🟡。**
>
> **本条留下的一般教训**（已写进 guide ⑧ 段说明）：**改判据的字段名时必须一并复核它的数值** ——
> 该行 07-22 只把 `verified` 改成 `audit_passed` 没重估阈值，而订正当天那次 run 自己就是 6%。

- **强度**: 🟡（**判据失真·非产品缺陷**——不影响生产行为，但让每次 e2e 的 ⑧ 段必然「按字面 ❌」，实际操作中只能靠人当场裁「这条不算」→ 闸门形同虚设，且下一个照章办事的人会误判 run 失败）
- **现象**: [segmented-e2e-guide.md](../observations/e2e-runs/segmented-e2e-guide.md) §⑧ pass0 的 D2 项写「`facts_inventory` 的 `audit_status` 分布：**`audit_passed` ≥ 50%**，< 50% → 事实基础不可靠」。**实测五次 run 从没有一次接近过**（均从 `origin/main` tracked 版本读·R6）：

  | run | facts | audit_passed | 占比 |
  |---|---|---|---|
  | 2026-07-06 [m1-t11](../observations/m1-t11-e2e/run-nvda-20260706/) | 41 | 3 | 7% |
  | 2026-07-09 [m1-t4-t12](../observations/m1-t4-t12-e2e/) | 41 | 3 | 7% |
  | 2026-07-10 [m1-full](../observations/m1-full-e2e-20260710/) | 76 | 10 | 13% |
  | 2026-07-22 [gate-route](../observations/gate-route-e2e/run-NVDA-20260722/) | 50 | 3 | 6% |
  | 2026-07-31 [regression](../observations/regression-e2e-20260730/) | 62 | 8 | 13% |

- **为什么会留下这条线（已核·非推断）**: 该行 2026-07-22 被订正过一次，但**只改了字段名**（`verified` → `audit_passed`·因 MASK.E1 [#184](https://github.com/JunoChenZt/subagent-for-investment/pull/184) 收敛枚举后压根没有 `verified` 这个值），**没有同步重估阈值**——而订正当天那次 run 自己就是 **6%**。属「订正了词汇、没订正数字」。
- **与 audit 定位一致（所以低占比是应然不是异常）**: audit 永久停在「来源存在性」半项（AUDIT-3CHECK 已砍·见 [[project_audit_positioning]]），T11 又把存在性泡沫挤掉过一轮（26→3）。**在当前定位下 `audit_passed` 本就该是少数**，50% 是按早已废弃的「三检查」时代想象定的。
- **候选修法（不预设·届时定）**: ① 改成**相对判据**（不低于同类历史归档区间下沿·如 <5% 才 ❌）；② 改成**绝对下限 + 趋势**（如 ≥5% 且较上次同 query 类型 run 无显著下滑）；③ 整条降级为 observe（记录占比、不作放行闸）。**任何新判据须先在 [e2e-acceptance-standard.md](e2e-acceptance-standard.md) 登记维度归属 + 承重边界，并按 §4 一律 WARN 试用**。
- **顺带该查的同类**: guide 里其他「拍脑袋定的数字线」是否也没被实测校准过（如 ⑥ 段「6 轮辩论总 token 通常 <15k」——2026-07-31 本跑实测 **28,361**，双方每轮都触发续写补 `MIN_CHARS_DEBATE`，同样是没跟上现实的线）。**建议一次性做一轮「guide 数字线 vs 历史归档」对账**，而不是逐条撞到再改。
- **✅ 对账已做（2026-07-31·用户当场追加）**: [e2e-guide-threshold-audit-20260731.md](e2e-guide-threshold-audit-20260731.md)——11 正常 run + 4 对抗 run 全量回测（脚本 [`audit_guide_thresholds.py`](../observations/e2e-runs/scripts/audit_guide_thresholds.py)·零网络可复现）。**12 条数字判据里只有 2 条有效**：
  - 🔴 **空线 2 条**：本条的 `audit_passed ≥ 50%`（实测 6–47%）+ ⑥ 辩论 output「<15k」（4 次可测全在 22.4k–28.4k·**每次都超线**）
  - 🟠 **前提常年不成立 1 条**：⑨ 价位判据——**11 次里 10 次 `entry` 是 null**（guide 原写「高方差」，实测是 1/11 而非 50/50）→ 两条 D2 判据 91% 的 run 里**空过**（比空线更麻烦：空线会吵，空过是静默的）
  - ⚪ **结构性恒真 4 条**（`rework_counts ≤ 2` 与 `confidence ∈ [1,10]` 由常量/schema 已保证·逻辑上不可能 fail；辩论 6 轮 / 10 voter 零方差）+ 🟡 **钝线 3 条**（余量过大）
  - 🟢 **有效 2 条**：④ `key_claims ≥ 2`（唯一真 fail 过的线·5 次）+ ① `query_class ≤ 800`（实测 718–729·**全表唯一有校准记录的线**，2026-06-05 实测后由 500 上移）
  - **元发现**：4 次已知坏输入的对抗 run（r5 垃圾注入）拿同一套线量，**除 `key_claims` 外全部指标与正常 run 不可区分**→ 段间数字线测**形态完整性**、不测**内容真伪**；guide 未写明这条边界，易让人把「段间全绿」读成「这跑没问题」（2026-07-31 那跑就是现成反例：①-⑨ 全过 + gate 13/0/0，而辩论正文里躺着 5 个编造的引用锚，没有一条数字线看得见）
  - **7 条建议已列在审计文档 §4·本条待用户裁决后才动判据**（按 [e2e-acceptance-standard.md](e2e-acceptance-standard.md) §4 一律 WARN 试用）
- **触发条件**: 下次动 segmented-e2e-guide / e2e-acceptance-standard 时一并做；或再有一次 run 因这条线被判 ❌ 而卡住。
- **反向条件（close 不做）**: 若 audit 定位再次变动（如某天恢复数字级核查）使 `audit_passed` 自然抬升到 50% 量级 → 原线自动成立、本条作废。
- **进入时点**: 2026-07-31（全链回归 e2e seg8·用户当场裁「判据问题计入 backlog、放行续跑」）。**预估**: 轻（改 guide 一行 + 登记验收标准 + 可选的一轮数字线对账）。**配额**: 占 1 个 lettered slot。

---

### BC. 引用锚存在性无人校验 —— **🔴 已实证「拦不住」**（2026-07-31 立账 · 2026-08-04 BC 探针 e2e 验证完成）✅ CLOSED 2026-08-14（close-by-completion·保留位置）

#### ✅ 收口（2026-08-14·随「数字出处」问题域封卷）

**close 依据**：本条 close 条件 = [endgame](number-provenance-endgame.md) 判据 **D1 + D4 达成**。
D4 早已达成（靶测 65 绿 + 变异 11 全红）；**D1 于 2026-08-14 达成**——连续 3 次最高信任档零错绑
（抽查 #1 = 08-05 执法跑 · #2/#3 = [BC 收官两跑](../observations/bc-final-e2e-20260814/FINDINGS.md)）。
六条判据全达成 → 问题域封卷，本条 close-by-completion。

> ## 🔒 **close 理由须精确读（本段是这条目最后、也最要紧的一句）**
>
> close 的是「**本域判据已达成**」，**不是**「编造出处这件事解决了」。
>
> **2026-08-14 收官跑里它第三次自然复现，而且手法比本条原记的更宽**（详见下方 N=3 块）：
> 首次出现在**空头侧** · 首次编造**外源数字章** · **凭空造命名空间**而非沿真集续编号。
> ⇒ 本条原记的「同一编号策略」被推翻，**它不是固定套路，是"需要出处时就造一个"的通用倾向**。
>
> **它至今没有被任何一道门拦过。** 三次里唯一没造成伤害的那次（33.7% 毛利率），
> 是**模型自己在收尾轮改对了数**，不是机制保证 —— 与本条下方「结局须精确表述」记的同一形态。
> `halluc` 档零 fire **已第 5 次成立**，A 路可达性仍零实证（已移交 endgame 缺口 **G5** observe）。
>
> **本条正文全部保留**，作为**该形态的已知记录**；将来若要治它，**须重新立项、重新定判据**，
> **不得挂靠 endgame 的 DONE 状态**（endgame 顶部 banner 已写死这一点）。

> **📍 2026-08-05 归属变更**：本条已并入「数字出处」问题域，真值源 = [number-provenance-endgame.md](number-provenance-endgame.md)。
> **close 条件改为判据 D1 + D4 达成**（不再由本条自行判断）；未实证的 `halluc` 档已移交该文档 **§4 缺口 G5**（🟢 observe·不专门验）。
> 修法归 [DEFECT-ANCHOR-MISBIND](#defect-anchor-misbind-报告里的数字挂着别人的出处而系统因为有出处给了它最高信任🔴2026-08-04-全链-e2e-实证每跑都在发生✅-closed-2026-08-14close-by-completion保留位置)（该域唯一主条目）。

> **⚠️ 标题已改（2026-08-04）**：原题「编造的 `REF#` 能否被拦住**仍无实证**」—— 那个"仍无实证"**已经不成立**，
> 留着会让扫标题的人得到相反印象。**验证做完了，答案是拦不住**；条目仍活跃是因为**修法未做**，不是因为还不知道。

> ## 🔴 **2026-08-04 N=2 自然复现 —— 从"偶发"升级为"可复现的模型行为"**
>
> BC 探针 e2e [seg5](../observations/bc-anchor-e2e-20260803/run-NVDA-zh-20260803/)（**另存现场** `seg5-debate2.fake-anchors-N2.*`·逐字节校验）**独立重现了 07-30 的假锚形态**，且高度同构：
>
> | | 2026-07-30 | 2026-08-04（本次） |
> |---|---|---|
> | 位置 | R2 **多头**续写段 | R2 **多头**续写段（同） |
> | 形态 | `REF#Y-009 ~ Y-013`（5 个） | `REF#Y-010 ~ Y-014`（**5 个**·同族续编号） |
> | references 真集 | 止于 `Y-008` | 止于 `Y-008`（同） |
> | 空头侧 | 无假锚 | 无假锚（**1 个 REF# 全真**·同） |
>
> **关键含义**：原条目写「07-30 那次纯属撞上、运气成分大」——**该判断已被推翻**。两次独立跑批、同一位置、同一形态、同一编号策略（沿真集末号往下续编），这是**可复现的系统性行为**，不是偶发。⇒ 本条的"覆盖缺口"从理论风险变成**每跑都会发生的实况**。
>
> > ### 🔴 **N=3（2026-08-14 BC 收官中际旭创跑）—— 上面「同一编号策略」这半句已被推翻，问题面比本条原记的更宽**
> >
> > 现场：[seg5](../observations/bc-final-e2e-20260814/run-zhongji-fundamental-20260814/) · 汇总 [FINDINGS §4.1](../observations/bc-final-e2e-20260814/FINDINGS.md)。**空头侧**编造 **6 个**出处标记（逐条对表②登记册核实，已排除「省略 `#nK` 后缀」这类假阳性）：
> >
> > | | 本条已记（07-30 / 08-04） | 2026-08-14 |
> > |---|---|---|
> > | 位置 | 均在**多头** R2 续写段 | **空头**侧（上表明写此前「空头侧无假章·1 个内源章全真」） |
> > | 章族 | 仅**内源章** | **首次编造外源数字章**（`W#competition-*` / `W#customer-*` / `W#financial-*` / `W#tech-*`） |
> > | 手法 | 沿真集末号**续编**（`Y-009~Y-013`） | **凭空造命名空间** —— 那四个"角色"根本不存在（真命名空间 = 8 个分析师角色，已从册中逐一列出核对）；另有内源章形态的 `REF#B-001`，而内源章真来源前缀只有 `R`/`T`/`W`，**无 `B`** |
> >
> > 🔑 **对本条的实质影响**：上面用「同一编号策略」当作"可复现系统性行为"的证据之一。本轮出现**完全不同的编造手法** ⇒ **它不是一种固定策略，而是「需要出处时就造一个」的通用倾向**，形式随场景变。**这使问题面比本条原记的更宽，不是更窄** —— 任何只针对"续编号"形态设计的检测都会漏掉本轮这种。
> >
> > **其中一条编造出处挂着对不上的数字**：空头写「当前高达 **33.7%** 的毛利率」（挂 `W#financial-8-1#n3`·编造）。册内核对：唯一毛利率读数是 **46.1%**；33.68 在册对应的是**经营性现金流净额 33.68 亿元**。〔⚠️「模型把现金流误当毛利率」是**推断、未证实**；已核事实只有两条：数值与现金流那条撞车、真实毛利率是 46.1%。〕方向上把公司说得**更差**，是空头"利润率将被压缩"那段的承重砖。
> >
> > 🔒 **收尾轮空头自己改回 46.1% 并挂了真出处 —— 但这不是任何一道门拦的**，是模型后续轮次自己用对了数。**与本条下方「结局须精确表述」记的同一形态**（编造的内源章没进决策是 fund_mgr 自己没采用、非被拦）。**别把它读成"辩论会自我纠错所以没事"** —— 三次里只有这一次纠了，且无机制保证。
> >
> > **同跑另一条（seg8·判别力方向反了）**：这 6 个真编造的出处标记**一条都没进事实清单**（留在辩论正文里逃逸）；而 15 条被判「出处标记在 common_context 未找到对应 reference」的，**全部只是省略 `#nK` 后缀的合法外源数字章**（8 个章逐一核实同族全在册）→ 8 条真实 EPS/净利润预测被误降档。⇒ **真编造的逃了、写法不完整的挨了罚**，方向安全但**没有判别力**。
>
> **本次假锚挂的内容（5 条全是可证伪的具体主张）**：CUDA 开发者 400 万 `Y-010` · 准封闭生态论断 `Y-011` · Blackwell 能效比 H100「提升数倍」`Y-012` · 云厂商管理层表态 + 推理增速超训练 `Y-013`（用了两次）· 出口管制影响「低于最坏预期」`Y-014`。
>
> **同段真锚用得很正确**（`Y-005` ROE 114.3% / 净利率 63%、`Y-008` PE 30.8x 均与 references 实际字段对得上）→ **模型不是不会用锚，是没有锚可用时会编一个**——这条对修法方向有直接含义（缺口在"想引用的事实没有对应锚"，不是"不懂引用规范"）。
>
> **F-class 依旧看不见**：本段 F3 双侧 fire（`f_check_failed=['F3']`），但 ① F3 管的是分轮可见性、不是锚存在性；② `_F3_OBSERVATION_ONLY=True` **只 log 不返工**（[rules_f.py:22](../../src/committee/triage/rules_f.py#L22)）。⇒ **静态核查 §1.2 的 C 条（辩论层零校验点）当场被实证**，不再只是读码推断。
>
> **对验证设计的影响**：P1 探针（"不存在的锚"）**已获天然样本，可降优先级**；**P3（锚真实但绑错实体）仍必须注入验**——它在本轮已出现两个天然样本（seg2 commodity `REF#Y-005 fundamentals` 挂 PE、seg3 D5 三次 fire），但都在 analyst 层，decision 层仍零覆盖。〔**⚠️ 2026-08-04 seg8 后作废：P3 也拿到天然样本了、且在承重层——见下方 seg8 块**〕

> ## 🔴🔴 **2026-08-04 seg8 —— P3 天然样本落在承重层，且是 `audit_passed` 集合的多数**
>
> **实测**：[seg8](../observations/bc-anchor-e2e-20260803/run-NVDA-zh-20260803/) 的 `facts_inventory` 87 条里 13 条拿到 **`audit_passed`**（最高可信档的入场资格）。逐条核对「陈述内容 vs 锚指向的 `data_key`」：
>
> | 陈述 | 水印锚 → 锚实际是什么字段 | |
> |---|---|---|
> | NVDA 股价 $200.75 | `Y-007` → **price** | ✅ 对 |
> | NVDA PE 30.79x | `Y-007` → **price** | ❌ |
> | NVDA PE 30.8x | `Y-006`→market · `Y-005`→currency · `Y-008`→ticker | ❌ |
> | NVDA PS 19.18x / 19.2x | `Y-007`→price / `Y-008`→ticker | ❌ ×2 |
> | NVDA PB 24.88x / 24.9x | `Y-007`→price / `Y-005`+`Y-008` | ❌ ×2 |
> | NVDA ROE 114% / 114.3% | `Y-007`→price / `Y-005`+`Y-008` | ❌ ×2 |
> | NVDA 净利率 63% | `Y-007`+`Y-005`+`Y-008` | ❌ |
> | NVDA 市值 4.86 万亿 | `Y-007` → **price** | ❌ |
> | 花旗目标价 $300 / 美银重申买入 | `W-003` → wisburg text blob | 〜（文本块·另见 [BI](#bi-wisburg-只取研报标题全链无人读正文--半句话成了承重数字的依据2026-08-03-全链回归-e2e-findings-33-逐条过时立账)）|
>
> ⇒ **10/13（77%）的最高可信档事实，锚指向的是完全不相干的字段。** 样本：`f3` = `{claim:"NVDA PE为30.79x", numeric_value:30.79, watermarks:["REF#Y-007"], audit_status:"audit_passed", audit_rationale:"全部水印已匹配 common_context references: REF#Y-007"}`——而 `Y-007` 的 value 是 **200.75**。
>
> **承重性已核（非展示层）**：[`audit_node`](../../src/committee/agents/audit_node.py) 只做 `canon in ref_lookup` 的**存在性**匹配，**从不比对**陈述与 reference 的 `data_key`/`value`（AUDIT-3CHECK 已砍·audit 永久停在存在性半项）；而 [`audit_gate`](../../src/committee/facts/confidence.py) 是 `audit_status == "audit_passed"` 的**二值入场门**——过门即进 5 档可信度漏斗，按 `as_of` 新鲜度可升到 `verified`。⇒ 绑错实体的锚**拿到了可信度入场资格**。
>
> **🔑 病根（本条最重要的一句）**：这 10 条**全部**是 fundamentals 字段（pe/ps/pb/roe/net_margin/market_cap）——**正是 [`_LAYER1_ONLY_KEYS`](../../src/committee/common_context/watermark.py) 焊点故意不发 `REF#` 的那批**。当年立那道墙是为了防「fundamentals 一被引用就确定性 verified」（Layer 2 defer）。实际结果：**墙挡住了前门，模型从窗户进来了** —— 没有自己的锚 → 借隔壁的锚 → audit 只查存在性 → 照样过门。**"不给锚"没有变成"拿不到可信度"，只变成了"锚是错的"。**
>
> **对验证设计的连锁影响**：P1、P3 **双双拿到天然样本**，且 P3 这个比注入更硬（真实行为链 + 承重层 + 77% 占比）。⇒ **seg9 探针注入的必要性大幅下降**，剩余未覆盖面主要是 P2（水印落空）。建议 seg9 先跑 A（真实基线），看这 10 条错绑事实**最终派生出什么可信度档、有没有进 `final_decision`**，再定要不要注入。

> ## 🔴🔴🔴 **2026-08-04 seg9 —— 全链闭合：错绑锚一路无阻走到读者面前。本条已从"覆盖缺口"变成"已证缺陷"**
>
> **BC 原问的两件事，本轮都有了实证答案**：
>
> **① 编造的锚（P1）**：R2 那 5 个天然假锚 `Y-010~Y-014` **未进** `final_decision`（archive 全字段扫描唯一命中 `.debate[].content`）→ **复刻 07-30**：仍是 fund_mgr 自己没采用、**非被拦**。`enforcement_log` 69 条按档为 `log_only` 46 / `caveat_annotate` 18 / `warn` 2 / `dedup` 2 / `flag` 1 —— **`halluc` 档 0 条**。⇒ 「验章门 halluc tier 至今零实证」这句**第三次**成立。
>
> **② 绑错实体的锚（P3）—— 走完了全链，且比预想更糟**：
>
> | fact | 正文印出的数字 | 锚 → 锚的真实字段 | audit | 附录 credibility | 「（未独立核实）」 |
> |---|---|---|---|---|---|
> | f1 | $200.75 | `Y-007` = **price** | audit_passed | web-single | **无** ✅本来就对 |
> | **f3** | **PE 30.79x** | `Y-007` = **price** | audit_passed | web-single | **无** |
> | **f7** | **PB 24.88x** | `Y-007` = **price** | audit_passed | web-single | **无** |
> | **f9** | **ROE 114%** | `Y-007` = **price** | audit_passed | **verified** 🔴 | **无** |
> | **f11** | **净利率 63%** | `Y-007`+`Y-005`+`Y-008` | audit_passed | unverified | **无** |
> | f19 | 目标价 $300 | `W-003` = text | audit_passed | verified | **有** |
>
> **完整因果链（每一环都已核代码，非推断）**：fundamentals 字段无自己的锚（[`_LAYER1_ONLY_KEYS`](../../src/committee/common_context/watermark.py) 焊点）→ 模型借隔壁 `Y-007`(price) → [`audit_node`](../../src/committee/agents/audit_node.py) 只查 `canon in ref_lookup` **存在性**、不比对 `data_key`/`value` → `audit_passed` → [`classify_stamp`](../../src/committee/facts/stamp_check.py) 见 `REF#Y-` 前缀且在 `ref_lookup` 中 → 判 **🟢「表① 结构化直拉源·audit 真核过」** → **正文照印、不挂「（未独立核实）」** → 附录 `f9` 更升到 **`verified`**。
>
> **🔥 信任反转（本条最该被记住的一句）**：**一个绑错实体的结构化锚，比一个诚实的 web 来源更被信任。** 同一段正文里，`f9`（ROE 114%，锚指向 price）**裸印无 caveat**，而 `f49`（AI 加速器份额 80-86%，正经 web 来源）**挂了「（未独立核实）」**。读者看到的信号强弱**与真实可靠性相反**。
>
> **终局 quality gate 13 pass / 0 warn / 0 fail** —— 含 `Q5 Evidence quality: 0/24 misattributed (0%)`。**Q5 名叫"误归因"却给出 0%**，而上表 4 条正是误归因 ⇒ Q5 量的不是这个（它比对的是别的东西），**终局门对本形态零判别力**。
>
> ⇒ **本条强度依原写死规则应升 🔴**（原文：「若验证结果为拦不住 → 升 🔴」）。**但升级与修法排期须用户裁**，本块只落事实。现场：`seg9-decision.p3-full-chain.checkpoint.json` / `archive-from-final.p3-full-chain.json`。
>
> **P2（水印落空）仍是唯一未获天然样本的一路** → 若仍要注入探针，只剩它值得做。

- **强度**: **🔴（2026-08-04 升级·用户拍板）** —— 原写死的升级规则「若验证结果为拦不住 → 立即升 🔴」已由 BC 探针 e2e **触发并兑现**（三条实证见上方 seg5/seg8/seg9 三块）。**本条不再是"不知道"，是"已知拦不住"**；剩余唯一未实证项 = 验章门 `halluc` 档三轮零 fire（A 路是否真可达）。修法归 [DEFECT-ANCHOR-MISBIND](#defect-anchor-misbind-报告里的数字挂着别人的出处而系统因为有出处给了它最高信任🔴2026-08-04-全链-e2e-实证每跑都在发生✅-closed-2026-08-14close-by-completion保留位置) 三路 A/B/C。〔**下方为立账期强度记录·point-in-time·不改**〕~~🟠~~（**覆盖缺口·非已证缺陷**——不是"证明了拦不住"，是"从没被触发过、所以不知道"。**若验证结果为拦不住 → 立即升 🔴**：那等于「编造的引用编号 + 挂在它上面的精确数字」可以一路走到读者面前，撞 [DEFECT-PROSE-MASK-ESCAPE](#defect-prose-mask-escape-散文门逃逸洞--打码只覆盖-311-字段未核实数字原样印出🔴-方向不安全撞北极星) 同族的方向不安全）
- **任务**: ~~排一次定向验证~~ **✅ 已做（2026-08-04·BC 探针 e2e·9 段全跑·[run-bcprobe-nvda-zh](../observations/run-counter.md)）**——且**未用注入**，三根探针里 P1/P3 全拿到**天然样本**（比注入更硬：真实行为链 + 承重层）。结论已按原任务要求**写死进 [e2e-acceptance-standard.md](e2e-acceptance-standard.md) §4 ② + [guide D2 行](../observations/e2e-runs/segmented-e2e-guide.md)**（回审结论：第一步维持 observe 不变——**放松面没变**，但边界措辞从「章存不存在无人校验」改写为「**章可能存在而绑错实体**」，因为后者已实证且更隐蔽）。**剩余动作**：`halluc` 档零 fire 仍无实证（不新增探针·随将来动验章门时顺带看）；修法三路归 DEFECT-ANCHOR-MISBIND。
- **现象（已核·非推断·R6 从 `origin/main` tracked 归档读）**: [run-NVDA-zh-20260730](../observations/regression-e2e-20260730/run-NVDA-zh-20260730/) 里，R2 多头**续写段**编造了 5 个不存在的引用锚 `REF#Y-009 ~ Y-013`（`common_context.references` 实有 8 条·止于 `Y-008`），每个各挂一个精确数字：Azure AI 季度收入 $13B / DGX Cloud ARR $1.5B / 未来 12 月 FCF $80B+ / 回购 $30B / 过去 8 季度超指引 15–25%。
- **扩散范围（本次实测·可复现）**: 假锚诞生于 **seg5**，此后**每一段的 checkpoint 都带着它**（seg5→seg9 全部命中），且进了 **seg7 十个 voter 的输入 prompt**。但在 [archive-from-final.json](../observations/regression-e2e-20260730/run-NVDA-zh-20260730/archive-from-final.json) 里全量扫字段路径，**命中数 = 1，唯一路径 = `debate[].content`**——`votes` / `decision` / `pass0_result` **零命中**。即：**看见过的人不少，采用的人没有。**
- **已核设计（非推断·R5）**: debate 节点的 F-class 检查是**分轮可见性**合规（[rules_f.py:31 `run_f_class`](../../src/committee/triage/rules_f.py#L31)，调用点 [base.py:1148](../../src/committee/agents/base.py#L1148)），**不校验引用锚是否存在** → 该阶段本就无机制拦截，这是设计边界不是 bug。
- **🔒 结局须精确表述（防后来者误读）**: 5 个假锚、5 个假数字**都没有进入 `final_decision`**，但原因是 **fund_mgr 自己没有采用**这些内容 —— **不是被哪道门拦下的**。引用解析 / 誊写核查机制**从未被这些假锚触发过**。
  > 若只记「假锚没出现」，下一个人会读成「门守住了」，然后在这个假设上继续盖楼。**本条存在的意义就是钉死这句话。**
- **为什么本次 e2e 不算实证**: 全链 ①–⑨ 全过 + quality gate **13/0/0**，而假锚就躺在辩论正文里——**没有任何一条判据看得见它**（见 [BB](#bb-段间-checklist-⑧-的-audit_passed--50-是空线五次-run-全-6132026-07-31-全链回归-e2e-surface) 对账的元发现：段间数字线测形态完整性、不测内容真伪）。绿灯与「拦住了」无关。
- **↳ 方案 ③ 静态核查已执行（2026-08-03·零成本·[验证设计](../plans/bc-anchor-verification-in-fresh-e2e.md) §1）**: 读代码得出——「引用锚」其实是**两个记号族**，覆盖状态完全不同，本条原问的那 5 个假锚属**覆盖最差**的那一族：
  - **A** `final_decision` 正文的 `{ref:fN}`/`{ref:vN}` 指向不存在编号 → [`classify_stamp`](../../src/committee/facts/stamp_check.py#L44) 返 `halluc` → 验章门剥标+涂，[EVID-1](../../src/committee/agents/base.py#L3450) 再兜一层 = **两层防御** ✅
  - **B** fact 的 watermark 挂**不存在的 `REF#`** → `canon in ref_lookup` 不成立 → 落 `return "yellow"`，注释写死「水印**落空**」（[stamp_check.py:74](../../src/committee/facts/stamp_check.py#L74)）= **静默降级**，与合法的未核实来源**同桶**、不报幻觉 ⚠️
  - **C** **辩论正文**里的 `REF#`（= 本条撞到的那 5 个）→ F-class 只查分轮可见性，水印族也不经 `classify_stamp`（它只看 fact 的 watermarks，辩论正文不是 fact）= **零校验点** ❌
  - **静态答案**：辩论层完全不拦；到决策层只有 `{ref:fN}` 族被拦、`REF#` 水印族落 🟡。**旁证**：07-30 那跑 `enforcement_log` 48 条（caveat_annotate 16 / log_only 27 / dedup 3 / warn 1 / flag 1）**没有一条 halluc 档** —— 与「halluc 那条路从未被触发」一致。
  - 🔒 **证据强度**：读代码 + 读模块 docstring（一手设计记录·R5 满足），**不是跑批实测**。代码写着什么 ≠ 真跑时那条路可达 → **静态只用来收窄跑批目标，不代替跑批下终局结论**（尤其 A 那两层防御**至今零实证**）。
- **↳ 验证已设计进下一轮 fresh e2e（2026-08-03·待用户拍板开跑）**: [bc-anchor-verification-in-fresh-e2e.md](../plans/bc-anchor-verification-in-fresh-e2e.md) —— **seg9 双跑 A/B**（正常 seg9 = 真实基线进 run-counter；改 `seg8-pass0.checkpoint.json` **副本**注入探针后只重跑 seg9 = 实验组·落 `.bc-probe.*` 变体名·**不进** run-counter/gate 统计，照 [r5 对抗 run](../observations/r5-garbage-injection-2026-06-12/) 先例 excluded）。成本 = 多跑一次单段。**三根探针**：P1 不存在的锚（→ C 路）· P2 水印落空（→ B 路）· **P3 锚真实但绑错实体**（→ 上方 3.1 数据点那一路·**本条相对原文的扩项**）。**判据开跑前写死**（设计 §3.3）：P1 若如预测逃逸 → 本条**升 🔴**；无论结论如何都必须记录 `enforcement_log` 有没有出现 halluc 档（= A 路是否真可达的唯一直接证据）。**不改生产代码**——若验出拦不住，修法另起节点。
- **候选验证方案（不预设·届时定）**: ① **归档 replay 注入**——改一份已有 checkpoint 的 debate content 塞假锚，从 seg9 单段起跑（最省·无网络·可复现）；② 构造对抗 run（贵·但覆盖真实 LLM 行为）；③ 先只做**静态可达性核查**（grep 全链是否存在任何"锚 ∈ references"的校验点）——若静态就证明零校验点，可直接跳过跑批下结论。
- **与既有条目的关系**: 与 [FINDINGS §3.1](../observations/regression-e2e-20260730/FINDINGS.md)「基本面数字无 ref 锚 → 模型随手抓邻近编号挂」**同族**（都是"锚与实体的绑定无人校验"），与 [T10 / #4](#t10--4-claimurl-级精确绑定🔵-挂起测量驱动2026-07-10-从已-close-的-m1-剥离)（claim/URL 级精确绑定）是同一问题的**上游**——T10 管"绑得准不准"，本条管"绑的对象存不存在"。
- **↳ 数据点（2026-08-03·FINDINGS §3.1 逐条过时并入本条·不另立条目）**: 上面提到的"基本面数字无 ref 锚"**已核为设计使然、非缺陷**（R5·一手证据）——[watermark.py `_LAYER1_ONLY_KEYS`](../../src/committee/common_context/watermark.py#L31) 是**故意**把 fundamentals 子 dict 挡在 References/audit 路之外的焊点，注释写死理由：「若生成 REF#，委员会 fact 一引用即被确定性核实为 verified = 明确 defer 的 Layer 2」。**所以不立新条目。**
  - 但**观察到的伤害不在那条 defer 理由的覆盖范围内**：模型拿不到锚时不是不引用，而是**随手抓邻近编号挂**（07-30 seg2 political 把 PE/市值标成 `[REF#Y-005 through Y-008]`，实为币种/市场/价格/代码；seg3 macro 把 FRED 数据标成 `[REF#Y-006]`）。当年 defer Layer 2 防的是"假 verified"，防的**不是**"错绑到真存在的锚上"。
  - **这正是本条（BC）的另一半**：BC 原本问「编造的锚（`Y-009`，不存在）能不能被拦」，这个数据点问的是「**真存在但绑错实体**的锚能不能被发现」—— 后者更隐蔽，因为锚存在性校验（若将来做了）**也拦不住它**。BC 的验证方案选型时应把这一路一并考虑，别只验"锚存不存在"。
  - **↳ 精确化（2026-08-04 seg3 实证·非全无人看）**: triage 的 **D5「value not near citation」**（D 类·**只记不拦**）对 analyst 报告层**看得见**这个形态——本轮 seg3 实测 fire 3 次（macro `REF#Y-007`、fundamentals/political `REF#Y-005 value='USD' not near citation`，正是"拿 currency 锚挂 PE 数字"）。修正口径：**analyst 层有 warn-only 探测器（D5），debate/decision 层仍零覆盖** → P3 探针（seg9·decision 层）仍必要；届时可把 D5 的 fire 记录当对照信号用。
- **触发条件（2026-08-04 已全部走完·下方为原文·point-in-time 不改）**: ~~下次跑全链 e2e 时**顺带做**~~ **✅ 已做**；~~或换后端后的首次回归跑~~ **✅ 即本跑（Serper 后首次跑到 seg5 之后）**；~~或再出现一次假锚且被 fund_mgr 采用（届时不再是验证、直接是事故）~~ —— **⚠️ 这条须精确读**：假锚（P1）本轮**仍未**被 fund_mgr 采用，但**另一路（P3 错绑锚）被采用了并印给读者** ⇒ **「事故」那一档实际已经发生**，只是发生在原条目没预料到的那条路上（故另立 DEFECT-ANCHOR-MISBIND 🔴 承接）。
- **反向条件（close 不做）**: 若打码门 / G5 路径重构后把「引用锚存在性」做成**显式校验步骤且有单测覆盖**（即不再依赖 e2e 实证）→ 本条作废。**2026-08-04 补**：本条**验证任务已完成**，之所以仍留活跃而非 close，是因为①「`halluc` 档是否真可达」仍零实证；② close 会让后来者误读成"这问题解决了"，而实际是**已证拦不住、修法未做**。修法落地（DEFECT-ANCHOR-MISBIND 路 C 或等效）后再 close。
  **↳ 2026-08-05/06 进展**：修法（路 A + B + 出处有效性）已 squash 合入 main `f9620ce`（[#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226)），**但本条仍不 close** —— ① 落地的是"章绑错实体"那一路，本条剩余未实证项 **`halluc` 档（编造的锚）是否真可达仍零实证**（#226 一行未碰验章门·已移交 endgame 缺口 **G5** observe）；③ 路 C 未做。
  ⚠️ **精确读**：#226 让"锚绑错实体"从**无人拦**变成**在可比键上会被拦**（核值执法）+ 其余情况降档；它**不等于**「引用锚存在性做成了显式校验步骤」，故本条原反向条件仍未满足。
- **为什么现在不做**: 〔**2026-08-04 作废 —— 已经做了**〕~~本次 e2e 已收官（9 段全跑完），为验一条假设单独重跑不划算；且方案选型（①/②/③ 成本差一个数量级）与 §1.1 换后端的排期耦合 —— 须用户裁排期，不自走。~~ **实际路径**：用户拍板后单开一轮 BC 探针 e2e（9 段全跑），**方案 ② 的成本换来了比方案 ① 更硬的证据**——P1/P3 全是天然样本，无需注入。
- **进入时点**: 2026-07-31（[FINDINGS §1.3](../observations/regression-e2e-20260730/FINDINGS.md) 三件待决中**唯一连账都没记的一件**·用户当场拍「立条目」）。**验证完成时点**: 2026-08-04。**预估**: ~~轻–中~~ → 实际中（单开一轮 9 段全跑）。**配额**: 占 1 个 lettered slot。

---

### BD. `_normalize_as_of` 不认英文日期格式 —— 归一职责压在 Worker 侧（2026-07-31 Serper 切换 surface）

> **✅ CLOSED 2026-09-08（close-by-decision·用户当日裁·保留位置）** —— **本条自写的反向条件已成立**：
> 「若长期只有一个搜索上游、且 Worker 侧归一稳定无漏 → 本条无收益，close」。今天确实只有一个搜索上游，
> Worker 侧归一自 2026-07-31 起未出过问题。
> ⚠️ **关它跟前面那五条不是一回事**：本条的**闹钟是好的**（「接第二个吐英文日期的上游 / 要把归一挪进本仓时」
> 是合法的事件型判据，会被自然撞上）。关它纯粹是「值不值占一个配额位」的取舍，**不是判据失效**。
> 🔑 **关之前先把知识挪进了代码**（这是关它的前提条件·用户裁）：[as_of.py](../../src/committee/as_of.py) 的
> `_normalize_as_of` 说明里现已写明「英文写法一概不认 / 今天靠 Worker 在进仓前转 / 接第二个上游时补在这里」——
> 在此之前那份文件**只字未提**这件事，就这么关等于把知识扔了。**该注即本条的真值源。**
> **重开条件**：真接第二个会吐英文日期的上游、或决定把归一挪回本仓时 —— 届时按代码里那段注释走即可，
> 不必复活本条。
> 〔以下正文为 point-in-time 记录，**一字未改**。〕

- **强度**: 🟢（**已有可用绕法·非阻塞**——Serper 切换时选了「Worker 侧归一」（方案 A）把日期在进本仓之前就转成 ISO，当前需求已满足。本条记的是**另一半**：主链路自己仍然不认英文日期，一旦出现第二个上游就要重复实现一遍）
- **任务**: 扩 [as_of.py `_normalize_as_of`](../../src/committee/as_of.py#L59) 认常见英文日期写法（`Dec 19, 2025` / `25 Feb 2026` / `Feb 2026`），使归一能力落在**主链路**而不是某个上游的转发层。
- **现象（已实测·非推断）**: 2026-07-31 拿 Serper 真实返回值喂 `sanitize_as_of`，**三种写法全部返回 `""`**——连绝对日期都不认：

  | Serper 实际返回 | 占比（36 条样本） | 喂 `sanitize_as_of` |
  |---|---|---|
  | `Dec 19, 2025` | 9 | → `''` ❌ |
  | `25 Feb 2026` | 6 | → `''` ❌ |
  | `3 months ago` | 8 | → `''` ❌ |
  | （空） | 13 | → `''` |

  根因：[as_of.py:59](../../src/committee/as_of.py#L59) 只收 ISO 系（`YYYY-MM-DD` / `YYYY-MM` / `YYYY` / `YYYY-Q[1-4]` / `YYYY-H[1-2]`），英文月份名一个都不在列。**不归一 = 日期白拿**（模型看得懂，但 staleness / `is_outdated` 那条路用不上）。
- **为什么现在不做（选了方案 A 而非 B）**: 用户 2026-07-31 拍板「先做 A，B 进 backlog」。理由=**改动隔离**：Worker 侧归一出问题退回去即可、碰不到主链路；而 `_normalize_as_of` 是全链共用的严格校验，放宽它要走正规 PR + 回归测试，影响面远大于本次切换需要。
- **方案 A 已落地（本条的绕法·非本条内容）**: [worker-search-serper.js](../plans/worker-search-serper.js) `normalizeDate` + 离线自测 [test_worker_date_normalize.mjs](../observations/e2e-runs/scripts/test_worker_date_normalize.mjs)（34 case·含 round-trip 喂 Python `sanitize_as_of` 验 0 条被丢）。**精度阶梯**（不编造没有的精度）：日级相对→`YYYY-MM-DD` / 月级相对→`YYYY-MM` / 年级相对→`YYYY` / 认不出→`""`。
- **⚠️ 做 B 时必须继承的两条约束**（否则会把 A 的安全性丢掉）:
  1. **不得给相对表述编造日级精度** —— `3 months ago` 硬算成某一天是假精度，撞「不确定性诚实 > 数字正确」。
  2. **降精度的方向必须是「显得更旧」** —— 现行 `_normalize_as_of` 把 `YYYY-MM`→`YYYY-MM-01`、`YYYY`→`YYYY-01-01`（区间最老那天），对 staleness 判定而言偏旧是保守侧、偏新是危险侧。B 若引入新的粗粒度写法，要保持同一方向。
- **顺带**: `sanitize_as_of` 对形状合法但取值荒谬的输入（如 `9999-99-99`）目前**原样放行**——A 侧自测抓到并在 Worker 里补了范围校验（1900–2100）。B 落地时可一并核 Python 侧要不要同样收紧（**未验证是否构成实际问题**，只是同类）。
- **触发条件**: 接入**第二个**会吐英文日期的上游（届时 Worker 侧归一要重复实现 = 该收进主链路了）；或有人要把 A 的归一逻辑挪进本仓；或 Worker 侧归一被发现漏格式且改转发层不方便。
- **反向条件（close 不做）**: 若长期只有 Serper 一个搜索上游、且 Worker 侧归一稳定无漏 → 本条无收益，close。
- **进入时点**: 2026-07-31（Serper 切换第 3 步评测后发现·用户拍「先做 A，B 放 backlog」）。**预估**: 轻–中（改 `_normalize_as_of` 本身轻，但它是全链共用严格校验，回归面要认真跑）。**配额**: 占 1 个 lettered slot。

---

### BE. `evidence_log` 空但正文有带章数字 —— 「0 evidence = 无数据支撑」判据与实质不符（2026-07-31 Serper 切换 e2e seg2 surface）

> ## ✅ **CLOSED（2026-08-03·close-by-completion）** — 下方正文为 point-in-time 记录，**保留不改**
>
> 触发条件「下次动 guide-验收标准」随 [BB](#bb-段间-checklist-⑧-的-audit_passed--50-是空线五次-run-全-6132026-07-31-全链回归-e2e-surface) 的数字线一次性重校满足。
> **判据改成两步判**（[guide ② 段](../observations/e2e-runs/segmented-e2e-guide.md)）：
> `evidence_log = 0` 时**先扫该份 key_points 的数字带不带章**（外源 `W#` / 内源 `REF#`）——
> 带章 = **数据在，只是没进这个字段** → 记 observe 放行；正文数字**也没出处**才判 ❌。
> 判据量的从此是「**有没有数据支撑**」，不是「**字段填没填**」。
>
> **🔒 边界（别读成背书）**：带章判 **observe 而非 ✅** —— 锚存在性目前**无人校验**
> （本文件 §1 条目 **BC** · **🔴**），
> 第一步只降「字段没填」的误报，不背书数据真实。~~**BC 若验出「拦不住」，本步须连带回审。**~~
>
> **✅ 回审已做（2026-08-04·BC 验出拦不住）**：**结论 = 第一步维持 observe 不变**（放松面没变），
> 但边界须**加强一档**——原措辞只防「章可能是编的」，实测出的更隐蔽形态是「**章真实存在、
> 但绑的是别的实体**」（10/13 最高信任事实的锚指向不相干字段·[DEFECT-ANCHOR-MISBIND](#defect-anchor-misbind-报告里的数字挂着别人的出处而系统因为有出处给了它最高信任🔴2026-08-04-全链-e2e-实证每跑都在发生✅-closed-2026-08-14close-by-completion保留位置) 🔴）。
> ⇒ **「带章」这个信号连"章指向的是不是这件事"都不保证**，读它时只当"有人写了个编号"，不当"有据可查"。
>
> **🔒 下游承重一行未动**：[risk_gate.py](../../src/committee/agents/risk_gate.py) G1 仍按 `len(evidence_log) < 2` 计数。
> 本次只改**人工 checklist 的读法**，不改代码闸门 —— 空 evidence 让 G1 更易开火 = 误报侧非漏报侧、方向安全，
> 没有放松任何自动检查。已在 [acceptance-standard §4](e2e-acceptance-standard.md) 登记为「放松·fail 面只减不增」。
>
> **N≥2 那条触发条件没等到就动了**：因为处置是**放松 + 增加一步人工判断**（不是收紧、不是新增自动检查），
> 方向 fail-safe，不需要更多数据点来证明「值得冒险」。若将来要**反向收紧**（比如强制 evidence_log 非空），
> 那才需要数据 + 用户裁决。

- **强度**: 🟡（**判据失真 + 潜在误报**·非产品缺陷·单数据点）
- **现象（已实测·非推断）**: [serper-switch-e2e seg2](../observations/serper-switch-e2e/run-NVDA-zh-20260731/) 里 `technical_report` 的 `evidence_log` **= 0 条**，段间 checklist ② 的 D2 项按字面判 ❌（原文：「0 evidence = 无数据支撑的判断」）。**但该报告正文并非没有数据**：

  | | 实测 |
  |---|---|
  | `key_points` | 5 条，含 RSI(14) **46.99** `[W#technical-18-1#n2]` / MACD **-2.21** / 50 日 MA **$201.63** / 200 日 MA / VWAP **$193.12** `[W#technical-18-4#n1]` / 现价 `[REF#Y-007]` |
  | 盖章 | 数字**带 W# 外源章 + REF# 内源锚**，不是裸数字 |
  | 本段搜索 | **4 次全成功、0 超时** → 与同段的 web_search 超时（全落在 sentiment）**无关** |
  | 其余 7 角色 | evidence 6–10 条不等，全段合计 55 条，`source` / `as_of` **零缺失** |
  | 07-30 同角色基线 | evidence **4 条**（[regression-e2e-20260730](../observations/regression-e2e-20260730/run-NVDA-zh-20260730/)·R6 从 main tracked 读）|

  即：**数据在，只是没进 `evidence_log` 这个字段**。判据量的是字段条数，读者读到的却是"这个分析师没有数据支撑"——两者不是一回事。
- **下游是承重的（已核·非推断）**: [risk_gate.py:73](../../src/committee/agents/risk_gate.py#L73) 的 **G1** 按 `len(evidence_log) < 2` 计数（Strong\* conviction + 证据薄 → 升 high risk）。本次 technical 是 `Underweight`（非 Strong\*）→ **G1 未触发**，纯属没撞上。
  - **方向判断**：`evidence_log` 空会让 G1 **更容易**开火（误报），而不是漏报 → **偏保守侧、方向安全**。所以本条不是安全洞，是**判据/误报**问题。
- **两个未决问题（不预设结论·R5）**:
  1. 模型这次为什么没填 —— 单数据点，未查是 prompt 引导、schema 认知还是随机波动。
  2. 判据该不该改 —— 「`evidence_log` ≥ 1」测的是**字段填没填**，而想测的是**判断有没有数据支撑**。后者在盖章体系上线后已有更直接的信号（正文数字是否带 W#/REF# 章）。**任何判据改动须按 [e2e-acceptance-standard §4](e2e-acceptance-standard.md) 登记 + WARN 试用 + 用户裁决。**
- **与 [BB](#bb-段间-checklist-⑧-的-audit_passed--50-是空线五次-run-全-6132026-07-31-全链回归-e2e-surface) 同族**：都是「判据字面 vs 实质」错位。BB 是线定得达不到（会吵），本条是**判据量错了对象**（该过的被判失败）。
- **触发条件**: 再出现一次任一角色 `evidence_log` = 0 而正文有带章数字（N≥2 才动判据·避免为单次波动改尺子）；或下次动 segmented-e2e-guide / e2e-acceptance-standard 时一并裁；或 G1 因空 `evidence_log` 真误报一次。
- **反向条件（close 不做）**: 若后续数次 run 里各角色 `evidence_log` 稳定 ≥ 1 → 本次归为单次模型波动，判据无需动，close。
- **为什么现在不做**: 单数据点，且方向安全（误报侧非漏报侧）。用户 2026-07-31 拍「记 backlog、放行」。
- **进入时点**: 2026-07-31（Serper 切换 e2e seg2 段间审核）。**预估**: 轻（查明成因 + 改判据一行 + 登记验收标准）。**配额**: 占 1 个 lettered slot。

---

### BG. 往 `.env` / `.env.example` 加数值项会**静默架空**「测代码默认值」的断言 —— 无人守（2026-08-03 [#223](https://github.com/JunoChenZt/subagent-for-investment/pull/223) review 沉淀切出）

> **📦 2026-08-06 从 §0.2 表格拆出正文**：本条原为「轻条目」（只有 §0.2 一行、无 §1 正文），
> 但那格已积到 **1427 字** —— 已经不是表格单元格，而是一条藏在行里的条目。
> `scripts/lint_backlog.py` 新增的「轻条目超长」检查（阈值 1000 字）抓出，内容原样搬来、**未改口径**。
> 轻条目形态本身**仍然合法**（如 [BF](#02-活跃条目一览表)），只是不该长到这个地步。

- **强度**: 🟡（丢的是**本地验证的可信度**，不是生产保护洞——见下方「不是保护洞」）
- **来源**: 2026-08-03 [#223](https://github.com/JunoChenZt/subagent-for-investment/pull/223) review 沉淀切出。
  坑表条目已立（[09-known-pitfalls §3.2](workflow/09-known-pitfalls.md)「`.env` 罩住代码默认值」·N=2）。
  **本条记的是坑表没记的那半：现在有哪几条断言站在雷上。**
- **机理〔⚠️ 不是巧合是构造使然〕**: [.env.example](../../.env.example) 的 4 个数值项
  （`MIN_CHARS_ANALYST=500` / `MIN_CHARS_DEBATE=1500` / `MIN_CHARS_DECISION=1500` / `MAX_CONTINUATIONS=3`）
  **与 [config.py](../../src/committee/config.py) 代码默认值逐个相同** → 谁照抄 `.env.example` 建 `.env`，
  谁就自动进入「`.env` 值 == 代码默认值」这个**静默**遮蔽态（断言照绿、但已改成在验本机配置）。
- **当前暴露面（2026-08-03 实扫）**:
  - ① **已被遮** = `MIN_CHARS_DEBATE`（[test_checklist_structural_invariants.py](../../tests/test_checklist_structural_invariants.py)·
    已在 docstring 写明两条路分工·**非新洞**）
  - ② **靠运气绿** = `assert MAX_TOKENS == 4096`（[test_max_tokens_configurable.py](../../tests/test_max_tokens_configurable.py)）
    + `assert MAX_TOKENS_ACADEMIC == 12288`（[test_am_academic_max_tokens.py](../../tests/test_am_academic_max_tokens.py)）——
    这两个键**现在不在 `.env`/`.env.example` 里**，哪天被写进去（值多半照抄默认值）就当天静默失守，**无任何提示**
  - ③ 其余 config 断言未撞

> **⚠️ 2026-08-13 订正：上面这份清单不准 —— 机器实扫后三处要改**（原文保留在上，便于对照当时的判断）：
>
> 1. **①②③ 是在只扫 `config.py` 的前提下得出的**，而危险的键**不全住在 `config.py`**。
>    全 `src/` 扫下来，被测试断言默认值的 env 符号共 **7 个**，其中 **4 个**踩雷。
> 2. **`MAX_TOKENS` 其实是安全的那个**（原判为「靠运气绿」）：模板里写的是 `8192`、代码默认是 `4096`，
>    **值不同 → 取消注释会当场变红**。吵，但看得见。真正静默的是**值相同**那种。
> 3. **漏了两个，且都是 2026-08-12 那天刚加进模板的**：`COMMITTEE_CLASSIFY_TIMEOUT`（值 15 = 默认值，
>    压着 **3 条**断言）和 `COMMITTEE_REGISTRY_REFRESH_HOUR`（值 `2` vs 默认 `2.0` —— **纯字符串比会漏，得按数字比**）。
>    两者都是注释态，所以当时**没有**真的失守；但这正说明「靠人记得 grep」的成色 ——
>    当日记录里只写了查过 `REFRESH_HOUR` 一个。
>
> 教训与 BF 同形：**判据写下来之后没人验过它在真阳性面前会不会响**。这次是「扫描范围」悄悄小于「危险范围」。
- **不是保护洞**: CI 无 `.env`（已 gitignore·CI 不造）→ **代码默认值仍由 CI 守着**；
  丢的是**本地验证的可信度** —— 而「mutation 证承重」按 [DoD](workflow/06-dod-and-evidence.md) 是在本地做的，
  #223 就差点据此把一条好断言判成不承重。
- **触发条件（写死·用户原话）**: 往 `.env` **或 `.env.example`** 新增**任何数值项**时 →
  先 grep 有没有测试在断它的默认值。
- **连带**: **[AZ](#az-活文档链接模板同步小债overviewmd-root-relative-链接--envexample-缺新-env2026-07-29-docs-audit-surface)** 的 env 半
  （补 `.env.example` 缺的键·含 `COMMITTEE_CLASSIFY_TIMEOUT` 等数值项）**做的时候正好撞本条触发** —— 先 grep 再加。
- **任务 / 修法未定**（候选三条，**故意不预设**，撞上时按当时暴露面选）:
  1. `.env.example` 数值项旁加「⚠️ 有测试在断这个默认值」注
  2. 加一条 meta 测试扫「`.env.example` 键 ∩ 被断言的默认值」交集非空即红
  3. 受影响断言一律打 dotenv 源头
- **为什么延后**: 修法三选一取决于撞上时的具体暴露面；现在选 = 无数据下预设方案。
  且当前**非保护洞**（CI 仍守着代码默认值），不阻塞。
- **进入 backlog 时点**: 2026-08-03（#223 review 沉淀）
- **预估工作量**: 小（候选 1 = 注释；候选 2 = 一条 meta 测试；候选 3 = 改若干测试的取值源）

#### ✅ 收口（2026-08-13·close-by-completion）

**延后理由已消失**：2026-08-12 补 `.env.example` 缺键那次就是「撞上」，暴露面数据已经有了 ——
于是取 **候选 2 + 候选 1 合做**（候选 3「改断言取值源」**未做**：那要动 7 处既有测试的写法，
而机器闸门已经能在失守当天喊出来，动既有断言的收益不抵风险）。

**落地** = [scripts/lint_env_shadowing.py](../../scripts/lint_env_shadowing.py) + 同名自检测试 + CI job `env-shadowing-lint`：

- **规则 1（候选 2）**：某键在 `.env.example` **或本机 `.env`** 里生效、值等于代码默认值、且有测试断言该默认值 → 报错。
  已知可接受的写进脚本内 `ALLOW` 并**声明理由**（今日仅 `MIN_CHARS_DEBATE` 一条）。
- **规则 2（候选 1）**：键一旦进了模板（**注释态也算**），该行附近必须带警示注记 ——
  注释态不报错（没生效），但下一个来取消注释的人**当场看见**这是雷。已给 5 处补注。
- **防锈**：`ALLOW` 里的条目若已不是真实的雷 → 报错。豁免表变坟场，检查就成了摆设。

**边界（声明出来，不靠"没报错"推断）**：不追派生链（env → 原始串 → 派生符号）；
CI 上没有 `.env`，本机那半靠开发者本地跑测试时触发；防御 (a)(b)(d) 仍靠人，只有形态 ② 有机器守。

**🔬 冷审把检查器自己身上的同一个病挖出来了（`/code-review` 四个 finding·全部实测复现过漏报）**：

初版**手写正则去猜 `.env` 的加载语义**，与运行时用的 python-dotenv 差了四处，**每处都是静默漏报**
（检查器报干净、雷还在）—— 正是本条要治的那个形状，只不过这次长在检查器自己身上：

1. 同键写两次时，靠后的**注释行覆盖了靠前的生效行** → 生效的雷被记成"没生效"。
   **前提不是假想**：`.env.example` 里本就有 13 个键出现两次。
2. 值带引号（`="12288"`）不脱引号 → 比不相等，**加个引号就能绕过检查**。
   本仓 `.env` 第 3 行就在用带引号的值。
3. 不认 `export KEY=value`（dotenv 支持的写法）→ 整行解析不出来，两条规则同时失灵。
4. 收集符号时按裸名入字典 → 两个模块定义同名常量时**后者静默吃掉前者**，
   此后断言会被拿去和**错误的 env 键**比对。

**修法 = 取值口径改与运行时同源**：规则 1 一律走 `dotenv.dotenv_values`，重复键 / 引号 / `export` /
`${VAR}` 展开全部按运行时语义，不再逐条追平（将来库升级也自动跟上）。规则 2 仍用自家正则 ——
它问的是「出现过没有、在第几行」，而 `dotenv_values` 只吐生效值、既不报注释行也不报行号，答不了；
但同样补上引号与 `export`，且**同键多次出现全部记录、不再互相覆盖**，并改为**逐处**要求警示注记。
符号重名改为**当场报错 + 每个候选都查**（宁可吵，不可静默）。
`dotenv` import 失败时**直接退出并说明**，不提供「退回自家正则」的兜底 —— 静默缩小覆盖面正是要治的病。
代价：CI 该 job 因此**不再是纯 stdlib**（多一步 `pip install python-dotenv`·本就是项目依赖·仍秒级），
且报错信息的行号只能尽力回填（dotenv 不吐行号），已在信息里标明。

**验证**：自检测试 **35 条**全绿（含四个 finding 各自的回归锁 + dotenv 取值口径直钉 + 对照组）
+ **12 个变异全部被杀**（三条规则 / 两条防锈 / 数值等价 / 本机 `.env` / 包一层解析，
加上本轮四个洞各自的回退变异）+ 全套件 **3349 passed / 0 失败**。
⚠️ **变异验证当场抓到一条"靠错误理由通过"的用例**：重名检查那条原本只断言「文字里出现了 B 键」，
而重名告警本身就会列出两个候选的键名 → 在「只查第一个候选」的变异下照样绿。已收紧成钉在规则 1 的 finding 上。
坑表 [§3.2](workflow/09-known-pitfalls.md) 该条已标「形态 ② 已机制化」并写明**仍靠人的那三条**。

---

### BH. `reevaluate_triggers` 四个结构化字段**恒空** —— 触发器程序读不了，只有人能读（2026-08-03 全链回归 e2e FINDINGS §3.2 逐条过时实测升级）✅ CLOSED 2026-08-06 (close-by-completion·保留位置)

- **✅ 实现（2026-08-06·合 main `c7306ac`·[#228](https://github.com/JunoChenZt/subagent-for-investment/pull/228)）**：三处改动 ——
  1. **prompt 输出模板 → 对象数组** + 新增【重评估触发条件规范】段（按 [S4 §6.3](../roadmap/S4.md) 原设计约束写、不自行发明：`description` 永远必填、复合条件照原样写进去不硬拆、`expires_at` 不从 `time_horizon` 反推），并把 🚩 **北极星边界写进 prompt 本体**（只用于提醒决策者回来重看，绝不据此自动下单/调仓）。
  2. **`_coerce_triggers` 加固**——改成对象数组后「LLM 漏填 `description`」首次成为可能（字符串模板下不可能漏），而它是唯一必填字段、`make_decision_node` 走 bare `model_validate` 无 fallback → 缺了就崩整 run。现按 str 包装 / 实例放行 / 缺 `description` 从其余字段重建 / 重建不出**丢弃而非编造** / 垃圾类型丢弃处理，**永不 raise**。
  3. **前端**（顺带发现的**活的线上缺陷**）：后端自 soft-structure 起发的就是对象，`types.ts` 却一直标 `string[]` → `report.ts` 插值出 **`- [object Object]`**。没人发现是因为守护测试的 fixture 还是旧的字符串数组，CI 一路绿 —— [known-pitfalls §3.2](workflow/09-known-pitfalls.md)「改数据形态须核下游 + 相邻/守护注释」的又一次命中。
- **⚠️ 未实证的那半（close 时如实记账·不许读成「验过了」）**：本条证到的是**「结构上填得上」**（13 后端测 + prompt 契约测 + mutation 全承重：模板退回字符串数组 1 红、删规范段 2 红、加固回退 8 红）；**「模型真的会填」没有任何 e2e 数据**——修复后没跑过 seg9、填充率仍是 0/180 那个**修复前**读数。合并时该项即 [§2.7 Q5](workflow/05-brake-self-check.md) 命中并经用户裁决放行。
  - **残留去处（按 [§4.2](#42-触发条件命中后的处理) 第 2 档写去引用方，不留在已关条目里）**：[S4 §6.4 约束 5](../roadmap/S4.md) —— trigger watcher 排期前必须先读一次真实跑批的填充率，非 0 才动工。**判据是事件型的**（"trigger watcher 开工前"），不挂"哪天有人想起来量一下"。
- **强度**: 🟡（影响质量·**不是当下故障**——今天没有任何程序在消费这四个字段，所以空着不坏事；它坏的是**未来**：[S4 §6.3](../roadmap/S4.md) 的「触发追踪」用法 A 靠 `direction`+`threshold` 自动订阅，输入恒空 = 那条路一上线就是空转）
- **任务**: 把决策 prompt 的输出模板从**字符串数组**改成**对象数组**（`description` 必填 + `direction`/`threshold`/`action`/`expires_at` 可选 best-effort），让"能结构化的那部分触发器"真的结构化。schema 侧**不用动**（早已就位）。
- **现象（实测·非单跑观察·R6 口径：`_archives` + 各 e2e 目录 tracked 归档全扫）**:

  | 量 | 值 |
  |---|---|
  | 扫过的 archive | **38 份** |
  | 里面的 `reevaluate_triggers` 条目 | **180 条** |
  | `direction` 有值 | **0 / 180** |
  | `threshold` 有值 | **0 / 180** |
  | `action` 有值 | **0 / 180** |
  | `expires_at` 有值 | **0 / 180** |

  即 **填充率 0%，跨全部历史跑批、无一例外**。FINDINGS §3.2 原记的是"本跑 5 条全空"（单数据点），实测下来是**结构性恒空**。
- **根因（已核·非推断·R5 先证设计）**: 不是模型偷懒，是**结构上填不了**——
  1. [prompts.py:83](../../src/committee/prompts/decision/prompts.py#L83) 的输出模板写的是 `"reevaluate_triggers": ["触发重新评估的指标/条件"]` = **字符串数组**，从没向模型要过那四个字段；
  2. [decision.py `_coerce_triggers`](../../src/committee/schemas/decision.py#L304) 再把每个 str 包成 `{"description": item}` —— 于是四个字段**必然**是 `None`。
  - 结论：[S4 §6.3 soft-structure（2026-05-25 敲定）](../roadmap/S4.md) **只落了 schema 半边，prompt 半边从没落**。`ReevaluateTrigger` 的 docstring 写「其余全 optional best-effort」，读起来像"模型尽力填"，实际是"模型从没被问过"。
- **后果**: 触发条件只活在一段自然语言里 → **人能读、程序不能**。要做"到价提醒 / 条件盯盘"这类功能，今天的产出**没有可订阅的输入**。
- **🚩 北极星边界（写死·防后来者跑偏）**: 结构化触发器的用途是**提醒决策者**（`docs/roadmap/S4.md` 用法 A），**绝不允许**接任何下单 / 调仓 / 资金动作路径。把条件变成机器可读 ≠ 把执行交给机器 —— 见 [CLAUDE.md 北极星](../../CLAUDE.md)。做本条时若出现"既然能自动判定，不如顺手自动执行"的念头，**当场停下问用户**。
- **为什么现在不做**: ① S4 未排期，做早了没有消费方；② 改的是 `make_decision_node` 的输出契约，而该节点走 **bare `model_validate` 无 fallback**（[S4.md §6.3 红线](../roadmap/S4.md)：raise 即崩整 run）→ 属主链路承重面，要正规 PR + 回归 + 至少一次 e2e 实证填充率真的上去了，不是改一行 prompt 就算完。
- **触发条件**: S4 trigger watcher 排期**之前**必须先做（它是前置数据，不然 watcher 上线即空转）；或下次因别的原因动 decision prompt 输出模板时**顺手**；或用户提出"到价提醒 / 条件盯盘"类需求。
- **反向条件（close 不做）**: 若 S4 定案为"触发器一律走 LLM 解释路、不做结构化自动订阅" → 四个字段本就无人消费，连同 schema 一起当死字段处理（参照 §0.1 条目 AQ 砍 `raw_confidence` 死字段的先例），本条作废。
- **进入时点**: 2026-08-03（[FINDINGS §3.2](../observations/regression-e2e-20260730/FINDINGS.md) 九条观察项逐条过·实测把单数据点升级成 0/180 结构性事实）。**预估**: 轻–中（prompt 模板轻；验"填充率真上去了"需一次 e2e）。**配额**: 占 1 个 lettered slot。

---

### BI. wisburg 只取研报**标题**、全链无人读正文 —— 半句话成了承重数字的依据（2026-08-03 全链回归 e2e FINDINGS §3.3 逐条过时立账）

> **📍 2026-08-05 边界澄清**：本条**明确划出**「数字出处」问题域（见 [endgame §1 排除表](number-provenance-endgame.md)）——
> 「拿不拿得到研报正文」与「出处对不对」相互独立。**顺带一个新事实**：[#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226)
> 判定 3 已让「数值事实引研报正文 blob」**降到 `audit_notsure`**（用户 08-05 拍板不开例外）——
> 即本条不修，研报数字也不会再冒充最高信任档；本条的价值回归**纯粹是"信息量"**（想真读到论据），不再兼负可信度职责。

> **🔴 2026-08-20 状态更新（前置调查已完成 · 修法已定 · 已并入 seg1 方案）**——
> **① 那项"必须先做"的前置调查已经做完了**：G0b 探针真连智堡跑过 `discover_tools()`（[证据](../observations/wisburg-fulltext-probe-20260819/FINDINGS.md)），
> 结论是**「取正文」这个能力根本不存在**——平台自己声明「只提供笔记摘要，**不提供报告原文或原文下载链接**」；
> **但拿得到智堡自撰的结构化摘要**（实测 2,112 / 2,735 字符，含「主要观点 / 事实依据 / 陈述总结 / 关键数据」四段，**数字带出处**）。
> **② ⛔ 因此不得再套用下方「反向条件」把本条 close**：反向条件写的是"MCP 没有取正文能力 → 降 🟢 并 close"，
> 但那条是在"要么拿到原文、要么没救"的二分假设下写的；实测打开了**第三条路**（摘要）——
> 「花旗目标价 $300」那半句在摘要里是**有口径有出处的**（汇丰贵金属日报 PM 定盘价 4,206.60 美元/盎司即同型实例）。
> ⇒ **本条要的"读得到论据"实际可达**，close 掉等于放弃一个已证可行的修法。
> **③ 修法已改并已并入 seg1 取数改造**：不是"取正文"，是**「列表拿编号 → 挑几篇取摘要」两步**，
> 落在 [seg1 设计 pass](../plans/seg1-取数计划-设计pass-2026-08-19.md) 的 **G4b**（§6 账目表已由「不覆盖」改为「G4b 覆盖」）。
> ~~**⚠️ G4b 自带前置：智堡配额未测**~~ ✅ **2026-08-20 已测**（64 连调 / 8.05 秒不撞限 ⇒ "每篇一次调用"方案在配额上无阻碍；⚠️ 顶未探到 · 按天维度未决，见 [接口说明 §4](../infrastructure/seg1_retrieval/wisburg-mcp.md)）。~~🔴 **G4b 前置换成 `DEFECT-MCP-ISERROR`** —— 工具层错误走 `isError` 不抛异常、本仓零处检查，不堵就等于放大调用量却看不见撞限。~~ ✅ **2026-08-20 当日已堵并 close**（封装层判 `isError` → 抛）⇒ **G4b 的前置到此全部满足**。⚠️ **但 G4b 自带两项同批约束照旧**（[四缺口设计 pass](../plans/mcp-client-四缺口-设计pass-2026-08-20.md) ②③）：一次 fetch 一条会话 + **必须同批重定义那道 run 级调用闸**（旧的按连接计数、从未触发，会话一复用就在第 4 次拦死）。
> **④ 并入的 AP 残留（bundle 粗粒度编号）不受影响**，仍独立成立、随 G4b 一并处理（拆 per-report ref 是取摘要的必要伴生改动）。
> **⑤ 本条暂不 close**：等 G4b 落地后按"实现完成"收口，而不是按"我们修不了"收口。配额仍占 1 格。

- **强度**: 🟡（影响质量·**信源深度缺口**——不是拿到了错数据，是只拿到了标题那半句就当研报用了）
- **任务**: ~~先 `discover_tools()` 核实智堡 MCP 有没有"按 report id 取正文 / 摘要"的工具~~ ✅ **2026-08-20 已完成，不必重跑**（G0b 探针，结论见上方更新块：无原文、有摘要）。**现任务** = 按 seg1 **G4b** 实现「列表拿编号 → 挑 top-N 取**摘要**」两步，并同批拆 per-report ref；**前置 = 先测配额**。
- **现象（已核·非推断）**: [wisburg_source.py:41](../../src/committee/common_context/sources/wisburg_source.py#L41) 全程**只调一个 tool** —— `list-institutional-reports`，返回形状固定为 `Found N reports:` + 每条 `[ID] 标题` + `date`（实测样本见 [run-D-hot-zhongji seg2 trace](../observations/fm-refactor-spec/run-D-hot-zhongji-20260616/seg2-research.trace.md)）。**全链没有任何环节能读到研报正文。**
- **后果（有具体案例·非假设）**: 07-30 NVDA 跑里，「花旗维持买入、目标价 $300」后来成了 `take_profit` **TP $300** 的依据 —— 而我们手上**只有标题那半句**，没有它凭什么给 $300 的任何论据。研报被当"机构背书"用，实际拿到的信息量约等于一条新闻标题。
- **~~⚠️ 未核实的前提（做之前必须先验）~~** ✅ **2026-08-20 已核实**：真连抓取到**13 个 tool**（原记的 11 已过时），工具定义原样存档在 [wisburg_tools.json](../observations/wisburg-fulltext-probe-20260819/wisburg_tools.json)、可读整理见 [接口说明](../infrastructure/seg1_retrieval/wisburg-mcp.md)。**按 ID 取详情的工具存在**（`get-report-detail`），但它返回的是**智堡自撰摘要、不是原文**；另有两个内容流（智堡自有文章、Mikko 日志）**能拿完整正文**，机构研报那一档不能。⚠️ 取详情时**编号必须传整数**，传字符串会被参数校验直接拒绝。
- **⚠️ 施工约束（继承既有·别踩）**: 改 `wisburg_source` / wrapper 前必读现有接入约定 —— **必须直连、不走 VPN proxy**（`trust_env=False`，否则单次 0.5s 劣化到 8–18s）。
- **顺带会牵出的问题（不是本条 scope，但做时会撞上）**: 正文进来 → 研报里的数字要不要当结构化源、要不要盖章 —— 那是 [AL](#al-市场感知路由a-股-query-不挂-yfinance--美股不挂-tushare) 明确 defer 的 **Layer 2**（「研报数字凭结构化源拿 🟢 不盖章」）。**取正文 ≠ 可直接当可信源**；本条只负责"把正文拿进来给人/模型读"，可信度归属仍走既有信源册规则。
- **📥 并入项：AP 的残留（bundle 粗粒度编号）——2026-08-06 完整 triage 合并**：原 [AP](#ap-wisburg-payload-编号粒度错位--refw-nnnn-子集匹配缺失🟡-p2✅-closed-2026-08-06-close-by-merge--bi保留位置) 条目 06-24 降级挂起后，残留真问题 = **wisburg/RSS bundle 粗粒度编号**（一次返回的 20 篇研报塌成**单个** `REF#W-005`，每篇的内部 ID 无独立 ref）。**已核实仍在**（2026-08-06 读 [wisburg_source.py](../../src/committee/common_context/sources/wisburg_source.py)）：`_parse_tool_result` 把整个 tool 返回拍平成**一个 payload dict**，登记粒度天然是"一次调用一条 ref"，#226 未触及。
  - **为什么并进本条而不是各走各的**：两者**同一个数据源、同一个触发条件（下次动 wisburg source）、同一项前置调查（`discover_tools()` 看 MCP 到底给什么）**；且**取正文（本条）必然要重构 per-report 登记**——拿到第 K 篇的正文却仍挂在 bundle 级 `REF#W-005` 上是说不通的，per-report 拆 ref（原 AP 修法 A）是取正文的必要伴生改动，不是独立可选项。分两条追踪 = 保证将来做本条时还得回头再读一遍 AP。
  - **AP 原修法 B（audit 侧子集匹配）已死透**：06-24 随降级撤销，其落点 `_extract_ref_id` 又于 [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 连同测试删除。**不要回去找那个函数**；将来若真需要子集匹配，落点是 [`stamp_families.split_stamps`](../../src/committee/facts/stamp_families.py) 或 audit 侧新零件。
  - **做本条时的连带动作**：拆 per-report ref 后需核 `references_appendix` 渲染与 audit 匹配两侧是否随粒度变化正确（AP 原记的"下游 reference_appendix 渲染更清晰"是拆 ref 的收益之一）。
- **触发条件**: 下次动 wisburg source / `common_context` 信源面时；或再出现一次"标题里的半句话成为承重数字（价位 / 目标价）的唯一依据"；或用户明确要"研报要看得进去"。**（并入 AP 后本条同时承接其原触发条件「下次动 wisburg source 或 audit 匹配逻辑时」中的 wisburg 侧；audit 匹配侧已随修法 B 一并作废。）**
- **反向条件（close 不做）**: ⛔ **2026-08-20 起本条反向条件已不适用，不得据以 close**（判定见上方更新块 ②）。~~若 `discover_tools()` 证明 MCP 侧根本没有取正文的能力 → 不是我们能修的，降 🟢 并 close~~ —— 实测确实"没有取正文的能力"，**但同时证明有摘要这条路**，而本条要的"读得到论据"经摘要即可达成，故**前件成立、后件不成立**：这不是"我们修不了"，是"换个修法就能修"。原反向条件的隐含二分（有原文 / 无救）已被实测证伪。**新的反向条件**：若配额实测证明"每篇一次调用取摘要"在预算内不可行、且缩到 top-1 仍不划算 → 那时才降 🟢 并改记使用边界（"wisburg 只能当'有哪些机构在看'的热度信号"）。**⚠️ 并入 AP 后此反向条件仍只 close「取深度」半边**——bundle 粗粒度编号是我们自己的登记层问题、与平台能力无关，**拆 ref 这半独立成立**，届时须显式裁决它是留还是撤，不得随反向条件一起默认关掉。
- **进入时点**: 2026-08-03（[FINDINGS §3.3](../observations/regression-e2e-20260730/FINDINGS.md) 九条观察项逐条过时立账）。**预估**: 中（一次 discover + 取正文接线 + token 预算评估——20 份研报正文塞进 context 不现实，要先定 top-N 和裁剪策略）。**配额**: 占 1 个 lettered slot。

---

### BJ. 配置 / 一手来源读取机械化（CFG-READ）—— 别再靠"照 guide 即兴查找"（2026-08-07 闸门矩阵第 1 层·挂起）

> **🔔 2026-09-14 · 触发条件已满足，用户裁「现在做」**（本块只记状态，判据原文在下方一字未改）
>
> **一手证据**：(B)「下次动 `config.py` 的 env 读取层，或往 `.env.example` 增删键」自第 0 层交付
> （`24f539b`·2026-08-07）起 **9 次提交命中**，其中 `ad19c61`（09-02）与 `0e297ef`（09-10）
> 发生在 **08-31 完整 triage 之后**，而本条账面当时仍写「未触发」。
> 复核命令：`git log --since=2026-08-07 -- src/committee/config.py .env.example`。
>
> **为什么没人发现**：判据本身没坏，是**撞上的那一刻没有任何环节出声**——
> 08-31 那轮逐条回忆式盘点，正是 [META 观察](../observations/meta-assume-mechanism-without-verify.md)
> 在治的那个动作。已由 [第 0.5 层闸门](../plans/trigger-wiring-2026-09-14.md) 接线解决（命中即点名）。
>
> **排期**：用户裁决顺序 = 先接闸、再做本条。本条属**高风险**（"读不到即明确报错、不静默回退"
> 改的是兜底行为本身），须先出拆解方案并经用户确认才开工。
>
> **🔧 2026-09-14 落地口径（PR [#292](https://github.com/JunoChenZt/subagent-for-investment/pull/292) ✅ 合 main `3aeb118`·分支已删·用户裁 BJ.0–BJ.4 本轮做、BJ.5 逐族另裁）** —— 详见 [拆解方案](../plans/BJ-cfg-read-decomposition-2026-09-14.md) 及其 §「落地口径」：
> - **BJ.0** [盘点](../plans/BJ-G0-inventory-2026-09-14.md)：105 个键 / 93 处读取 / 40 个键两份模板都没写 / 2 个模板死键；方案 §2 粗查数字三个全不准（漏数方向），已订正。
> - **BJ.1** 名册从源码派生（[config_registry.py](../../src/committee/config_registry.py)·8 种读取形态各配靶测）+ [lint_env_registry.py](../../scripts/lint_env_registry.py) 对账（枚举盲区 / 模板死键 / 缺模板·WARN 试用·扫到 0 处 exit 2）；`lint_env_shadowing` 原始读取判定改走同一份。反向变异 4/4。
> - **BJ.2** `committee config explain <KEY>` / `config show`：值 / 来源层（进程 env · .env · 代码默认）/ 走没走兜底 / 逐角色实配；**问不在名册的名字报错并给真名** —— 06-16 那次查询是首条靶测，真 CLI 复现通过。密钥只报指纹。变异 3/3。
> - **BJ.3** 段式跑起步写 `config-snapshot.json`，后续段比对报漂移进 trace.md 头；真跑冒烟 [bj-cfg-snapshot-e2e-20260914](../observations/bj-cfg-snapshot-e2e-20260914/FINDINGS.md)（起步即有快照 · check_secrets 干净 · 实调模型与快照一致）。变异 4/4（两条第一版没抓住、改成行为测试再杀）。
> - **BJ.4** 指南 / runbook / 坑表改口读快照或跑命令；`.env.example` 补 40 键、删 `COMMITTEE_API_HOST/PORT` 死键；`.env.prod.example` 补 5 个登录键。
> - **闸门点名 BL**（BJ.3 动了 graph.py）：**判不算** —— 改的是 run 目录起步定一次 + 写快照，不是并发编排 / 超时常量那两段；BL 判据文字不动。
> - **闸门点名 BM**（BJ.4 动了 prod-runbook）：**用户 2026-09-14 裁不算** —— 改的是「怎么查生效配置」一句 + 排查脚本两行，不是「生产现状」类章节；BM 判据文字不动。
> - **BK 触发 (D)「BJ 收口后重评本层形状」**：**半满足** —— BJ.0–BJ.4 已收口、BJ.5 未裁；重评等 BJ.5 裁完一起做，BK 状态本笔不动。
>
> **✅ 2026-09-14 BK.0/1/3/4 落地（PR [#295](https://github.com/JunoChenZt/subagent-for-investment/pull/295) 合 main `a53b196`·分支已删）→ 条目仍不 close**：
> - **BK.0** [盘点](../plans/BK-G0-inventory-2026-09-14.md) **推翻了重评方案自己的数字**：告警点 179 处 / 窄词表 36 / 宽词表 105 / 差集 69 ⇒ 人工分类后**真降级 58 处**，方案写的「44 处」作废（那是 `grep -A1` 的行数）。**58 处里 33 处只写日志**，其中 **3 处是「把没检查说成检查过了」**（EXEC-FLOOR 信号算不出按不触发放行 / 誊写核查 fail-open / 决策核验失败退空清单）。⇒ 坑表④ 再 +1 实证。
> - **BK.1** [degradation.py](../../src/committee/degradation.py)：纯派生汇总（不写 state·不加字段·不改任何降级判定），渲染四处 —— trace 头 / 归档 `degradations` 键（加性）/ **CLI「本次降级提示」**（降级留痕首次进用户面）/ 质检 **D1**。D1 是**记录型 PASS 不是 WARN**（`overall` 是「任一 WARN → 整体 WARN」，降级是常态，判 WARN 等于给「条数>0」设线并污染 13/0/0 基线判读）。
> - **BK.3** [lint_degradation_registry.py](../../scripts/lint_degradation_registry.py) + 62 条登记表（留痕 11 / 待补 38 / 不算降级 13）：词表只用来**提问**不作判据；防锈三条；CI job `degradation-registry-lint`，WARN 试用。
> - **BK.4** S2 §6 表加留痕说明 + 核实「degraded run flag 代码里没有」· 指南加降级提示读法 · **`DEFECT-CTX-BAG-SHAPE` ⑦ 定锚并 close**。
> - **坑扫描改掉一处设计**：补痕通道不走 `source_routing` / 报告字段（那是分析师提示词原料，可见化进提示词 = 改变决策者输入）；`test_not_fed_to_llm_prompt` 钉死消费面白名单。
> - **CI 抓到一条本地看不见的**：归档回放测试在浅 clone 下读不到 `origin/main`，「seen > 0」空转断言按设计开火 → 改读 `HEAD` 的 tracked 版本（仍守 R6）。
> - 守护 65 条 · 反向变异 6/6 KILLED · 全套 4539 passed。**剩 BK.2 逐点待裁**（清单在盘点 §2）。
>
> **✅ 2026-09-14 BJ.5 五族按用户逐类裁决落地（PR [#294](https://github.com/JunoChenZt/subagent-for-investment/pull/294) ✅ 合 main `d423dad`·分支已删）→ 本条 close-by-completion**：
> - **(a) 角色没配模型 → 保持**静默用档默认（可见性已由 `config explain` / 快照解决）；守护钉「不报错」。
> - **(b) 数值填错字 → 起步报错**（`ConfigValueError`）；超范围仍夹回、没写/空仍默认。⚠️ **翻案记录**：#210（07-24）立的旧契约「非法值 warn+回退，不得在 import 期抛」理由只有"否则整包导不进"——而那正是要的效果；三条钉旧契约的测试改钉新契约。
> - **(c) 开关封闭集合**：`_env_bool` 成为全仓唯一读法（1/true/yes/on · 0/false/no/off · 其余报错）；此前白名单把 `enabled` 当关、黑名单把 `disable` 当开，各漏一头（G1 冷审 findings 5 只换了一半）。11 个开关全部改走它，名册守护「再手写一套会现形」。
> - **(d) 未登记键 WARN**：环境里带 `COMMITTEE_` 前缀、名册没有的键（拼错）→ 快照字段 / 跑批起步日志 / trace.md 头 / `config show` 四处现形；只喊不拦（试用）。
> - **(e) 归并折中**：pass0 两处 `float(os.getenv)` 直转 + `EVIDENCE_MISMATCH_REVIEW_TIMEOUT` 改夹钳；`DEEPSEEK_BASE_URL / DEEPSEEK_API_KEY / OPENAI_BASE_URL` 从 base.py 归并到 config（名册证明只剩一处）；数据源模块（红线只读 env）/ 登录系统 / 限流 / streaming / run_budget 按 [盘点 §4](../plans/BJ-G0-inventory-2026-09-14.md) 登记为例外不动。
> - **BK (D) 由半满足转已触发**（本笔账面订正，待用户裁重评）。
> - **触发条件 (B)/(C) 从此有机器兜**：(B) 由 lint_env_registry（动读取层名册就变）、(C) 由「指南读快照不抄值」的改口共同承接；(A)(D) 仍是事件型。
> - **observe 两条**：① 派生器初版漏「元组循环读键」「函数体内 import」两种写法，各靠真仓对账撞出（枚举完整性坑表实证 +2）；② 密钥规则把 `AUTH_RATE_LIMIT_PASSWORD_RESET_REQUEST` 当密钥打码（多打码方向·无害）。

- **强度**: 🟡（已有可用绕法=人工小心；但起因事故证明"小心"不可靠）
- **来源**: [闸门矩阵机制化三层方案 §2](../plans/gate-matrix-mechanization-2026-08-07.md)，
  承接 [META 观察](../observations/meta-assume-mechanism-without-verify.md) **实例 #3**。
- **起因事故（一手记录在册）**: 把 [config.py](../../src/committee/config.py) 里的 **Python 符号名**
  `EXTERNAL_SEARCH_URL` 当成 env 变量真名（真名带 `COMMITTEE_` 前缀）→ 查空符号名 →
  误判"没配置" → web-search 误判事故（2026-06-16）。**同一形态在 guide 数字线上复发**：
  「照 guide 即兴查找」产出的判据逻辑本身也会失准（不只是值过期）。
- **任务**: e2e / 排查流程里"读配置、定位一手来源"这类**确定性**步骤，
  从"AI 照 guide 即兴查找"改为**代码/工具确定性读取，读不到即明确报错、不静默回退**。
  guide 活链接化是过渡态**非终态**。
- **触发条件（全事件型·守 [§4.1](#41-新增-backlog-条目)）**:
  - (A) 再撞一次"读错配置名 / 找错一手来源"导致的误判或返工
  - (B) 下次动 `config.py` 的 env 读取层，或往 `.env.example` 增删键
    〔⚠️ 与 [BG](#bg-往-env--envexample-加数值项会静默架空测代码默认值的断言--无人守2026-08-03-223-review-沉淀切出) 触发重叠 —— 同时撞上时两条一并处理〕
  - (C) 下次写 / 改任何"去哪读某配置"的操作文档（guide / handoff / runbook）
  - (D) 用户明确要求"别再让我确认配置在哪读"
- **为什么延后**: 第 0 层治的是**闸门自身的元治理**（改动面 = CI 配置 + 检查脚本 + 测试）；
  本层要碰**配置读取路径**，改动面与风险层级都不同档，混做会让 PR 失去单一性质。
  且第 0 层已交付一个真实样板，本层形状届时有实据可依、不必现在凭想象设计。
- **已有登记**: [S2 §9.2 CFG-READ-机械化](../roadmap/S2.md) —— **本条是它的 backlog 侧锚点，非重复立项**。
- **进入 backlog 时点**: 2026-08-07（META 观察 N=8 越过升级线后的分层排期）
- **预估工作量**: 中（需先盘点"哪些步骤属确定性读取"，再定工具形态）

---

### BK. 静默降级可见化 —— 系统悄悄降级时必须留痕（2026-08-07 闸门矩阵第 2 层·挂起）

> ✅ **CLOSED 2026-09-22（close-by-completion·用户当日裁·保留位置）**：两本账归零（登记待补 0 站 · 盘点真待补 0 行·实跑 92 / 0 / 53）；挂着的 28 条记账 / observe 项**全部迁到观察点表 [O-BK-01](../observations/should_update_observations.md)**（各带事件型触发条件）；`API-EMPTY-QUERY` 已另立轻条目。**留痕机制已机械化**（登记守护 strict 在 push 钩子内·新退路不登记即红）。**重开条件**：e2e / 生产出现一次「静默降级致结论失真」而汇总没报。下文（四条触发条件 / 09-14 重评 / 09-22 收口块）为历史记录、原文不动。

- **强度**: 🟡（不是拿到错数据，是**拿不到数据却看起来正常**）
- **来源**: [闸门矩阵机制化三层方案 §3](../plans/gate-matrix-mechanization-2026-08-07.md)，
  承接 [META 观察](../observations/meta-assume-mechanism-without-verify.md) **实例 #2 + #4**。
- **具体形态（两个已实证实例）**:
  - **#2 classify 慢日子静默降级**：DeepSeek 全提示稳定 >2.5s → 回退 regex → **ticker 丢失，无告警**。
  - **#4 e2e 证据未 durable**：15 个产物 `??` 未跟踪、git 0 commit，一次 `worktree remove` 即蒸发 ——
    「`--trace-dir` 落盘了」被当成「证据保住了」。
- **任务**: 各降级点（dispatcher 单源降级 / classify 超时回退 / 各 fallback 分支）
  建立统一的**可观测性约定** —— 降级必须留痕（结构化 log + 结果里可读的标记），
  让"数据没拿到"与"数据拿到了但结论如此"在输出上可区分。
  🚩 **北极星边界**：本条只做**可见性**，不改任何降级/兜底的**判定逻辑**。
- **触发条件（全事件型·守 [§4.1](#41-新增-backlog-条目)）**:
  - (A) e2e / 生产 run 中出现**一次**「静默降级导致结论失真」的具体实例
  - (B) 下次动 dispatcher 降级路径 / classify 超时回退 / 任一 fallback 分支
  - (C) 用户反馈"结果看着正常，其实数据没拿到"
  - (D) [BJ](#bj-配置--一手来源读取机械化cfg-read-别再靠照-guide-即兴查找2026-08-07-闸门矩阵第-1-层挂起) 收口后 —— 两层同源，做完 BJ 再重评本层形状
- **为什么延后**: 本条属**产品链路**而非闸门治理，范围明显大一档（涉及多个降级点的约定统一），
  需独立设计 + 逐点确认；与第 0 层混做会同时破坏 scope 单一性与可回退性。
- **进入 backlog 时点**: 2026-08-07（META 观察 N=8 越过升级线后的分层排期）
- **预估工作量**: 大（盘点降级点 + 定约定 + 逐点接线 + e2e 验证）

> **🔔 2026-09-14 判据 (D) 满足 → 重评（方案期·不动代码）**：BJ 五步全部合 main（#292 / #294）后按 (D) 重评本层形状，产物 [BK-silent-degradation-reeval-2026-09-14.md](../plans/BK-silent-degradation-reeval-2026-09-14.md)。**形状变化**：① 一个月来零散痕迹已补不少（兜底路由 / 回核降级理由进 `source_routing`、BV `legs_empty`、fallback_report / truncated / rejected_roles / 复核员 skipped / 价目表过期…），**洞变成"没有汇总 + 最终结果零字 + 44 处只写日志的点没逐个核"**；② 配置侧的"悄悄"已由 BJ.5 治掉、不再在本条范围；③ 与 `DEFECT-CTX-BAG-SHAPE` 登记项 ⑦「降级留痕不进最终报告」是同一件事，方案顺带给 ⑦ 定锚（最终报告 = 归档产物 + CLI 最终 markdown）；④ `DEFECT-DSML-PARSE` 改进 B 命题落为 quality gate 一条 WARN。**方案 = 先汇总后补痕**（BK.0 盘点 → BK.1 纯派生汇总渲染四处、不进 state 不进提示词 → BK.3 正向登记守护 → BK.4 回填；BK.2 补痕出清单后逐点裁）。坑扫描 5 条已落进各 goal。**待用户裁 5 项见方案 §5**；实例 #4（证据不落地）判已由指南 `--trace-dir` 约定 + BJ.3 快照解决。

> **🔧 2026-09-22 BK.6 ✅ 合 main `59b3689`（PR [#312](https://github.com/JunoChenZt/subagent-for-investment/pull/312)）→ 两本账归零 · 主体收口**〔同日随后用户裁 close·见标题下 close 块〕：BK.0 盘点的「真待补」与登记表的「待补痕」两本账均为 **0**（合并后实跑 `lint_degradation_registry` = 92 / 0 / 53 共 145）。**当时不 close 的原因**：正文与一览表仍挂 **≥ 10 条带触发条件的记账 / observe 项**（#309 review 4 · #311 review 5 · BK.5 记账 2 · P0 另记 2 · BK.6 本批 4 + review 6）—— **已于同日全部迁到观察点表 O-BK-01（28 条）并 close**。四条触发条件 (A)–(D) 文字不改。**留痕机制已机械化**：登记守护 `lint_degradation_registry --strict` 是 push 钩子四道 lint 之一，新退路不登记即红；汇总「本跑退了哪几步」进 trace / 归档 / 用户面。逐批明细见一览表 BK 行；证据 [bk6](../observations/bk6-20260922/FINDINGS.md)。

---

### BL. fred 的 8s 超时线在 8 路并发下**余量只剩 1.32×** —— 承重线贴着实测上限（2026-08-10 C2 探针计划外观察）

- **强度**: 🟡（**余量问题，不是当前故障** —— 本轮探针零失败。但该线越一次的实际后果**已实测过**：[DEFECT-SEG2-FLAKY](#defect-seg2-flaky-seg2-并发研究段瞬时失败族--三跑三坏成因各异疑共享资源竞争🟠攒表驱动2026-08-03交接新-session) run2 = fred `ConnectTimeout` ×3 → macro 落兜底 kp=1）
- **来源**: [seg2 C2 并发归因探针](../observations/seg2-c2-probe-2026-08-10.md)（96 次真实调用·零 LLM 成本）的 **§5 计划外观察** —— **不是**该探针的事前判据，事前判据判的是失败率、结果为「不结论」。
- **一句话**: 八路并发把 fred 的响应时间从 p50 1.11s 顶到 3.48s、p90 5.34s、max 6.05s，而它的超时线是 **8.0s** —— 最坏一次只剩 **1.32×** 余量；同一条腿单线程跑时只占 28%。

#### 实测数据（三轮一致·非单轮抖动）

| leg | arm | p50 | p90 | max | max ÷ 超时线 |
|---|---|---|---|---|---|
| **fred** | **concurrent** | 3.48s | **5.34s** | **6.05s** | **76%** ⚠️ |
| fred | serial | 1.11s | 1.55s | 2.28s | 28% |
| web_search | concurrent | 4.53s | 6.79s | 7.56s | 50% |
| web_search | serial | 2.24s | 2.88s | 3.27s | 22% |

逐轮 concurrent mean：fred 3.53 / 3.22 / 3.22 vs serial 1.10 / 1.34 / 1.23 —— **三轮无一例外**。

**为什么是 fred 而不是 web_search**：fred 的膨胀倍数更大（3.1× vs 2.0×）**且**超时线更紧（8.0s vs 15.0s），两头夹。web_search 经 [#221](https://github.com/JunoChenZt/subagent-for-investment/pull/221) 加宽到 15s 后余量约 2× —— 那次加宽被这组数据**事后印证是对的**，也说明当前该盯的是 fred 这条。

#### 触发 (B) 已实测响过一次——但被重试兜住、零伤害（2026-08-25 补记）

〔2026-08-25 应用户「看一眼 BL 余量」时补〕探针（08-10）之后，[攒表](../observations/bc-anchor-e2e-20260803/seg2-failure-ledger.md) **run5（2026-08-14）** 记到一次真 `tool fred failed: ConnectTimeout` —— **触发条件 (B) 实测成立**。但**结果无伤**：单次超时被源内部 3 次重试吸收，macro 照常产出全量（kp=5 / evidence=7·含 FEDFUNDS + CPIAUCSL）。⇒ 与 run2（探针前·`ConnectTimeout` **×3 连续**打穿 → macro 落兜底 kp=1）分开看：**承重的不是「单次超时」，是「3 次连续超时」，后者 N 仍=1、未复现**。8s 线与「塌」之间隔着一层重试缓冲，故 1.32× 的实际杀伤力比数字看着的轻。

**据此复判「要不要提」= 不提**（2026-08-25）：余量基线未变（8s 线 / 8 路并发 / fred 延迟均未动·[#266](https://github.com/JunoChenZt/subagent-for-investment/pull/266) 只改空返回、不碰延迟）；唯一真越线被重试吸收、零伤；三条方向仍全动主链路须用户裁，加宽 8s 线仍撞 playbook §8。**真该动手的信号 = 再来一次带伤害的 ×3 打穿 / C2 坐实，两者当前均无。**

#### 🔒 边界（不许自行处置）

- **候选方向三条·一条都不预设**：① 限并发 / 错峰（[graph.py](../../src/committee/graph.py) 层 8 analyst 分批）；② fred 加一次带抖动重试（治标）；③ 加宽 fred 那条 8s 线。
- ⚠️ **③ 与 [playbook §8](../plans/seg2-flaky-playbook-20260803.md) 直接冲突**（「不放宽任何超时线」·wisburg 先例：放宽 = 掩盖要暴露的问题）。**列它是为了完整，不是为了推荐。**
- ⚠️ **①②③ 全部动主链路 → 须用户裁**。**第四个选项是"什么都不做、只继续观测"**，在 C2 未坐实前它是默认。
- 🚩 **本条只记"这条线现在是承重的"这个事实**，不改任何超时常量、不改并发编排。

- **任务**: 待用户择定方向后再谈；在那之前唯一动作 = **下次 seg2 真失败时当场复跑 [C2 探针](../plans/seg2-c2-probe-handoff-2026-08-07.md)**，看那一刻这条线是不是真被越过（今日读数即对照基线）。
- **触发条件（全事件型·守 [§4.1](#41-新增-backlog-条目)）**:
  - (A) 下次动 [`definitions.py`](../../src/committee/tools/definitions.py) 的 `_TOOL_TIMEOUT` / `_WEB_SEARCH_TIMEOUT`、[`fred_source.py`](../../src/committee/common_context/sources/fred_source.py)、或 graph 层 analyst 并发编排时
  - (B) e2e / 生产 run 中**再出现一次** fred `ConnectTimeout`（[#224](https://github.com/JunoChenZt/subagent-for-investment/pull/224) 后错误带类型名，**可辨认**）
  - (C) [DEFECT-SEG2-FLAKY](#defect-seg2-flaky-seg2-并发研究段瞬时失败族--三跑三坏成因各异疑共享资源竞争🟠攒表驱动2026-08-03交接新-session) 攒表触及 playbook §6 升级线（N≥5 且瞬时类占多数）—— 那条判据本身也是事件型（每次 seg2 失败即记一行）
  - (D) 用户明确要求处理 seg2 并发 / 错峰
- **反向条件（close）**: seg2 改成限并发 / 错峰（不论出于何种动机）→ 本条前提消失；或 fred 腿被移除 / 换实现（[fred_source.py](../../src/committee/common_context/sources/fred_source.py) TODO 里的「接 FRED series search 端点」重做）→ 数值需重测，本条随之作废重立。
- **为什么延后**: ① C2 **未坐实**（探针零失败 = 不结论）—— 在没有归因结论时改主链路，正是 playbook §8 要防的"先修后归因"；② 三条候选方向**都动主链路须用户裁**；③ 攒表当前 N=3，五条升级判据**全部未达线**。
- **进入 backlog 时点**: 2026-08-10（C2 探针执行后，用户拍「先记 backlog」）
- **预估工作量**: 取决于方向 —— ③ 改常量 = 轻（**但不推荐**）· ② fred 重试 = 轻-中 · ① 限并发/错峰 = 中（含 e2e 验证）
- **关联**: [DEFECT-SEG2-FLAKY](#defect-seg2-flaky-seg2-并发研究段瞬时失败族--三跑三坏成因各异疑共享资源竞争🟠攒表驱动2026-08-03交接新-session)（父·本条是它 C2/T1 两行的量化侧） · [攒表](../observations/bc-anchor-e2e-20260803/seg2-failure-ledger.md) · [playbook T1/C2 行](../plans/seg2-flaky-playbook-20260803.md)

---

### BM. 文档在替一台没人核过的服务器说话 —— 「生产现在如何」的断言全仓未对过账（2026-08-12 BA 执行中撞出）

- **强度**: 🟡（**判断依据失真·非产品缺陷** —— 不影响任何代码行为；但会让人**基于错误的线上现状做决策、排优先级、甚至递出去一套跑不了的操作命令**。BA 本轮就是现成实例）
- **一句话**: 仓库里所有说「生产现在是什么样」的话，**都没有人对着真实服务器核过**；而已经实测到**至少一条是错的**。

#### 起因（实例·非推断）

BA 条目（2026-07-29 立账）写「生产每次重建镜像清零」，用现在进行时。2026-08-12 执行到"把只读诊断命令递给用户"那一步时，用户澄清：**线上跑的是旧的 S1，名录功能（AK [#211](https://github.com/JunoChenZt/subagent-for-investment/pull/211)）属 S2、从未部署** → 那句话描述的浪费**尚未发生**。

**关键在于这个错为什么两轮审计都没抓到**：BA 的机理断言（`default_db_path` 路径 / `WORKDIR /app` / compose 只挂 `backend_data:/data`）2026-07-29 docs-audit 核过一轮、2026-08-12 plan 阶段又核一轮，**逐条全对**。错的是那句**从未被写下来、因而从未被质疑**的隐含前提——「线上跑的是 main」。⇒ **静态审计能验"代码是不是这样"，验不了"这份代码在不在线上"。**

#### 暴露面（已知命中 + 待查·未逐条核）

- ✅ **已确认失真 1 处**：BA 条目原措辞（已于 2026-08-12 订正）。
- ⚠️ **高度可疑**：[prod-runbook.md](../infrastructure/prod-runbook.md) **通篇**按「线上 ≈ main」写 —— §1 拓扑、§2 运维 cookbook、§5 待办清单（"backend healthcheck 未接"/"caddy 80 未收窄"等**都是在断言线上现状**）、§4 事故复盘。手册第一行写着「source-of-truth in git」，但**git 里的是应然，不是实然**。
- ⚠️ **高度可疑**：任何派生产 ops 动作的条目 —— 如 advisory 模型 override drift 那条（正文写「在 prod 服务器 `/srv/committee/.env.prod` 删除三角色 override 行」，是按**现存且跑着 main** 写的）。若线上是 S1，该条描述的现象与动作**都需重核**。
- ❓ **未核**：[deploy-sources.md](../infrastructure/deploy-sources.md) / [proxy-allowlist.md](../infrastructure/proxy-allowlist.md) / [auth.md](../infrastructure/auth.md) 里的现状类陈述；各 e2e observation 里"生产侧"表述。

#### 为什么值得单独立条（而不是并进 BA）

BA 是**一个实例**，本条是**类**。BA 已按事实订正完毕并收窄了触发条件，但「凡断言生产现状的地方都可能同样失真」这件事**不随 BA 解决**；且本条的处置手段（对账）与 BA 的处置手段（改 env + 验证）完全不同。

#### 候选处置（三条·不预设·届时定）

1. **一次性对账**：登一次服务器，把「文档说的现状」逐条对「实际现状」，产出一份 dated 快照进 [observations](../observations/)，live 文档按结果就地订正。**代价 = 一次服务器会话 + 逐条核**。
2. **加一条元规则**：所有断言"生产现在如何"的句子必须带**核对日期与核对人**（形如「2026-08-12 实测」），没有日期的一律读作"未核实推断"。**代价极轻，但只防新增、不治存量。**
3. **在 runbook 顶部加一行环境版本标注**（线上当前跑的是哪个阶段 / 哪个 commit，谁在什么时候核的），并约定每次部署更新。**这条最便宜且最治本**——BA 这个错，只要 runbook 顶上有一行「线上 = S1」就不会发生。

⚠️ **1 需要服务器访问**（当前会话已知拿不到 → 这也是本条延后的直接原因）；**2 和 3 不需要**，可随时做。

#### 🔒 边界

- 🚩 **本条只做对账与标注，不改任何部署配置、不动线上**。发现失真 → 改文档措辞，不"顺手把线上改成文档说的样子"。
- ⚠️ **历史记录不改**：事故复盘 / 已 close 条目 / retro 属 [Q6 冻结档](workflow/05-brake-self-check.md)，即便其中的现状描述已过时也**只在引用方写前向事实**，正文一字不动。

- **触发条件（全事件型·守 [§4.1](#41-新增-backlog-条目)）**:
  - (A) **下次真正部署到生产时**（那一刻本来就要登服务器，对账边际成本最低，且部署完现状即刷新）
  - (B) 再撞一次「基于文档里的生产现状做判断，结果现状不符」的实例（含：为不存在/版本不符的环境准备操作命令）
  - (C) 下次动 [prod-runbook.md](../infrastructure/prod-runbook.md) / [deploy-sources.md](../infrastructure/deploy-sources.md) 的现状类章节时顺手做候选 3
  - (D) 用户明确要求
- **反向条件（close 不做）**: 若线上环境被明确废弃且不再重建 → 全部现状类断言失去指称对象，本条作废（届时该做的是给 runbook 整体加"环境已下线"前向 banner，而非对账）。
- **为什么延后**: 候选 1 需要服务器访问，本会话拿不到；候选 2/3 虽可立即做，但**在不知道存量失真有多大之前定规则，容易定错形状**（BA 这一个实例还不足以判断是"个别条目 stale"还是"整篇手册脱节"）。N=1，先登记。
- **进入 backlog 时点**: 2026-08-12（BA 执行中撞出·用户当场拍「立一条做生产现状对账」）
- **预估工作量**: 候选 3 = 极轻（一行 + 一条约定）· 候选 2 = 轻 · 候选 1 = 中（一次服务器会话 + 逐文档核 + 订正）
- **配额**: 占 1 个 lettered slot。
- **关联**: [BA](#ba-本地证券名录-db-未持久化到-volumes2-首次部署起会每次重建清零2026-07-29-docs-audit-surface)（起因实例） · [BJ](#bj-配置--一手来源读取机械化cfg-read-别再靠照-guide-即兴查找2026-08-07-闸门矩阵第-1-层挂起) 与 [BK](#bk-静默降级可见化--系统悄悄降级时必须留痕2026-08-07-闸门矩阵第-2-层挂起)（同族：都是"假设某机制/某状态生效而不一手验证"，见 [META 观察](../observations/meta-assume-mechanism-without-verify.md)——**本条是该 META 在"环境状态"维度上的实例**）

---

### BN. 十个投票人像一个人在投 —— 同向票理由同构、信心值零方差（🟡·2026-08-14 判据到线立账·N=3）

- **强度**: 🟡（**方向安全·问的是独立性不是安全性** —— 三次实测同构都发生在**保守侧**（NEUTRAL / 温和 BULLISH），没有"十个人一起看错方向"的案例；但若十个投票人实际被同一份材料主导，**投票环节提供的多样性就是形式上的**，而下游把票数与加权当独立信号在用）
- **一句话**: 投票环节设了 10 个角色各自投票，但同向票的理由高度重合、信心值反复出现零方差 —— **像一个人写了十遍，不像十个人各投一票**。

#### 为什么现在立（判据到线·非临时起意）

[段式跑批指南 ⑦ 段](../observations/e2e-runs/segmented-e2e-guide.md) 的观察点**开跑前就写死**：「再出现一次（N≥3）→ 提立 backlog 条目」。2026-08-04 用户裁「先并入观察点、不立条目」时 N=2；2026-08-14 BC 收官宏观黄金跑**复现且范围扩大** → N=3，按规则执行。

> 🔒 **这条比观察本身更重要**：判据是事前写死的，到线不立 = 判据形同虚设。

#### 三次实测（point-in-time·后续不改）

| | 2026-07-30 | 2026-08-04（BC 探针） | 2026-08-14（BC 收官·黄金） |
|---|---|---|---|
| 同构范围 | 仅 NEUTRAL | 仅 NEUTRAL | **NEUTRAL + BULLISH（扩大）** |
| 读数 | 六张 NEUTRAL 理由趋同 | 五张 NEUTRAL `conviction` **全 = 6**（零方差）·关键词「估值/资本开支/等待」**5/5 重合** | 10 票里 **8 票 `conviction` = 6**；BULLISH **3 张全 6·方差 0**；NEUTRAL 除弃权外 **4 张全 6·方差 0**·关键词「央行购金 / 去美元化 / 实际利率 / 技术面偏空 / 拥挤 / 观望」**四票全中** |
| 唯二离群 | — | — | bear = 8（角色天然对立）· fundamentals = 1（**主动弃权**：「非个股查询·不具备投票依据」= 诚实出口正常工作） |

**趋势向坏**：从"某一档同构"变成"两档同构"，且本跑 8/10 票挤在同一个信心值上。

> ### ⚠️ 立账当日即出反面样本（2026-08-14 同日·BC 收官第二跑·中际旭创）
>
> **本条立完不到一天，下一跑就没有复现。**如实记在这里，免得日后只剩支持它的证据。
>
> | 组 | conviction | 方差 | 全员共有词 |
> |---|---|---|---|
> | BEARISH 2 张 | 9 / 7 | 1.0 | 空 |
> | BULLISH 2 张 | 7 / 6 | 0.25 | 空 |
> | NEUTRAL 6 张 | 6 / 5 / 6 / 6 / 6 / 5 | 0.22 | 空 |
>
> 整体 10 票 conviction **5–9**、标准差 **1.1**，**无一组零方差**；按本条候选处置 ① 那两个量当场算，
> 三组的「全员共有词」**都是空集**。
>
> **对本条的影响，分两半说清楚**：
> - **不推翻立账依据** —— 那三次同构是**实际发生过**的，样本不会因为第四次没复现而消失。
> - **推翻上面「趋势向坏」那半句** —— 趋势不是单调的，N=4 里有 1 次明确的反向。**该措辞已由本块限定，不删原文**（point-in-time）。
> - **计入反向条件**：本条 close 条件 = 连续 3 次出现真实方差，**这是第 1 次**。
>
> 🔬 **一个可能的解释（推测·未验证·不得当作结论）**：本跑辩论的核心分歧是一个**锐利二元事件**
> （某项监管禁令落不落地 / 宽口径还是窄口径），投票人各自对概率的判断天然散得开；
> 而黄金那跑的分歧是「长期结构 vs 短期周期谁主导」这类**连续型判断**，容易收敛成同一句话。
> ⇒ 若成立，则候选处置 ② 的对照实验**须按 query 类型分层设计**，否则会把「问题本身的形状」
> 误读成「投票人的独立性」。**这一条正是它值得做的理由，不是跳过它的理由。**

> ### 📊 2026-08-27 数据点（G7 全链跑·黄金）—— 反向条件**连续第 2 次**
>
> | 组 | conviction | 方差 | 全员共有词 |
> |---|---|---|---|
> | BULLISH 7 张 | 7/7/7/7/7/6/6 | **0.204（非零）** | 空（最高频「央行购金」仅 5/7） |
> | BEARISH 2 张 | 8 / 6 | 1.0 | 空 |
> | NEUTRAL 1 张 | 6 | —（单票） | — |
>
> 按上方 08-14 反面样本的同一口径判：**无一组零方差 + 全员共有词全空** ⇒ 计入反向条件，
> **连续第 2 次**（close 条件 = 连续 3 次真实方差，**只差 1 次**）。
> 且十票有实打实的角色分工（历史类比 / 技术位 / 停火 / AISC 与废金回收 / 支撑区间各说各的）。
>
> ⚠️ **对上面那条「连续型 vs 锐利二元」推测是一个反例**：本跑是黄金（连续型判断），
> 按推测应收敛成同一句话，实际方差真实、共有词为空。N 仍小，不下结论，但**推测被削弱**。
> 〔本数据点由 [G7 FINDINGS §十三](../observations/rp-g7-e2e-20260827/FINDINGS.md) 登账时补入——
> 该节初判时误按 guide ⑦ 段旧文本数 N（BU 例②），已在彼处订正。〕

#### 假设（待证/待伪·不预设修法）

10 个 voter 的输入里，**辩论摘要（`ds_debate_result`）是共同且强势的那一份** —— 若各角色的差异化材料（自己的 analyst 报告 / 角色 prompt）在权重上压不过它，投票就会收敛成对同一份摘要的复述。**未验**：没有做过"抽掉/替换摘要看票型是否分散"的对照。

#### 🔒 边界（防后来者读错）

- ⚠️ **不是"投票错了"**：三次的票型方向都与辩论内容对得上（[指南 ⑦ 段 D4](../observations/e2e-runs/segmented-e2e-guide.md) 每次都过）。本条问的是**这些票是不是独立产生的**，不是它们对不对。
- ⚠️ **不得据本条收紧任何放行闸**：⑦ 段该项现为 **🔬 观察点（不判 ❌）**，立条目**不改变**它的承重 —— 照 [e2e-acceptance-standard §4](e2e-acceptance-standard.md)，提高 fail 面须用户裁。
- 🚩 **本条不含"让票型强制分散"这类修法**：人为制造分歧 = 拿多样性的表象换多样性，比现状更坏。

#### 候选处置（三条·不预设·届时定）

1. **先量再修**：把「同向票 `conviction` 方差 + 理由关键词重合率」做成跑批时自动算的一行读数（现在靠人每次手数），攒够样本再判要不要动。**最轻·纯观测·零行为改动**。
2. **对照实验**：同一份 seg6 checkpoint 起跑两次 seg7 —— 一次照常、一次把辩论摘要从 voter 输入里拿掉（或换成各角色自己的报告），比票型分散度。**中·一次单段重跑·能真正证伪上面那个假设**。
3. **动输入配比**：给每个 voter 更重的角色专属材料。**重·且在假设未证实前动它 = 猜着修**，不推荐先做。

- **触发条件（全事件型·守 [§4.1](#41-新增-backlog-条目)）**:
  - (A) 下次动 voter 的 prompt / 输入组装 / `ds_debate` 摘要生成 → 顺手做候选 1
  - (B) 再出现一次同构且**方向不再保守**（如十票齐刷刷看多某个高风险标的）→ **升 🟠 并优先做候选 2**
  - (C) 某次跑批的决策被发现**过度依赖票数加权**（下游把它当独立信号用出问题）
  - (D) 用户明确要求
- **反向条件（close 不做）**: 连续 3 次全链 e2e 出现**同向票 `conviction` 有真实方差**（非离群值撑出来的）→ 同构自愈或已被上游变化消解，close-by-decision。
- **为什么延后**: 假设未证实（候选 2 没做），此时动输入配比是猜着修；且三次同构全在保守侧、**零实际伤害**，不阻塞任何事。
- **进入 backlog 时点**: 2026-08-14（BC 收官宏观黄金跑 seg7·N=3 触发指南写死的「提立」规则·用户拍板立）
- **预估工作量**: 候选 1 = 轻 · 候选 2 = 中（一次单段重跑）· 候选 3 = 中-重
- **配额**: 占 1 个 lettered slot。
- **关联**: [指南 ⑦ 段观察点](../observations/e2e-runs/segmented-e2e-guide.md)（出处·三次读数都记在那）· [FINDINGS §3.9](../observations/regression-e2e-20260730/FINDINGS.md)（第一次读数）· [run-counter](../observations/run-counter.md) `run-bcprobe-nvda-zh` / `run-bcfinal-gold-macro`（第二、三次现场）

---

### DEFECT-ANCHOR-MISBIND. 报告里的数字挂着**别人的出处**，而系统因为"有出处"给了它最高信任（🔴·2026-08-04 全链 e2e 实证·**每跑都在发生**）✅ CLOSED 2026-08-14（close-by-completion·保留位置）

#### ✅ 收口（2026-08-14·本域主条目·随问题域封卷）

**修法** = [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226)（`f9620ce`）：在存在性之上加三层**只降不升**的收严 —— 限定词 / **核值执法** / 出处有效性。
**验收** = [endgame](number-provenance-endgame.md) 六条判据全达成（D1 ✅ 连续 3 次零错绑 · D2 ✅ · D3 ✅ · D4 ✅ · D5 ✅ · D6 ✅）。
**本条 close 后全仓 🔴 归零。**

> **两条实测收尾（2026-08-14 收官两跑）**：
> - ✅ **执法层第一次在真实跑批里自然拦到该形态**：黄金跑 economist 把 web 来的「Fed 利率 3.63%」
>   挂内源章 `REF#F-001`（该章是 `series_id`=`CPIAUCSL`）→ 降 `audit_notsure`，
>   理由明写「非可比数值，无法作为数字 3.63 的出处」。**08-04 同形态是拿到 `audit_passed` 并裸印给读者的。**
> - ⚠️ **同族新形态已记、本条不接**：「章绑对了，但**实体归属**没人核」——
>   中际旭创跑一条 `audit_passed` 事实称「**野村**报告标题为…」，而块内该标题**未标注发布方**、
>   唯一标野村的是另一篇。**审计只查章存不存在，不查陈述里的归属。**
>   → 记在 [FINDINGS §2.2](../observations/bc-final-e2e-20260814/FINDINGS.md)；
>   要做**须重新立项**（endgame 顶部 banner 已写死不得挂靠 DONE 状态）。
>
> **正文全部保留不动**（立条理由 = 修复前形态·改正文 = 篡改立条理由）。

> ## 📍 **本条 = 「数字出处」问题域的唯一主条目（2026-08-05 起）**
>
> **真值源 = [number-provenance-endgame.md](number-provenance-endgame.md)**（全景对账 + 完成判据 + 缺口清单）。
> 该文档 2026-08-05 经用户批准生效，起因：近 6 周该问题域产生 162 commit、散落 15+ 条目，
> 模式固定为「撞到 → 不属本 scope → 切条目推下一环」（07-03 设计的检查 07-14 被砍、08-05 又重实现 = 一个月闭环）。
>
> **规矩（防复发）**：本问题域**不再立新的独立条目** —— 发现新缺口 → 加进 endgame 文档 §4 缺口清单。
> 本条的 close 条件 = endgame **判据 D1–D4 全达成**（非"改完某个 PR"）。
> 首个修法 = [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226)。
> **进度（2026-08-06·[#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) ✅ 已 squash 合入 main `f9620ce`）**：四改动 + **核值转正执法**（用户 2026-08-05 拍板 = 判据 **D2 ✅**）+ review 修复轮五个 finding（F1 量纲白名单 / F2 枚举定义处 / F3 R7 收口 / F4·F5 认章正则两处静默漏判）**全部已在主干**。
> 确定性回放 `audit_passed` **13→2** · `audit_notpassed` **0→6**（降 11 条全为真错绑·零升级·零误伤）；
> seg8+9 定向 resume ×2 严格 A/B：log-only 期坐实"不执法则 D1 不可达"，执法期**信任反转消失**
> （附录 verified 7 条全 web 多源·内源 `f#` = 0）、地板未塌、两跑 quality gate 均 13/0/0。
> **仍不 close**（PR 合了 ≠ 条目 close·close 条件 = endgame 判据 D1–D4 全达成）：**D1 抽查 1/3**（须再蹭 2 次日常跑批）· 路 C（基本面发编号）未做 · 缺口 **G2** 未裁。
> 〔**2026-08-06 review 补正**：转正首版写的「今日表① 口径一致、量纲坑不可触发」是**未经核实的断言、已实测证伪**
> （`fred/value` 是指数级 / `rss/count` 是元数据，今日就能踩出假 `audit_notpassed`）→ 已改为
> `_COMPARABLE_DATA_KEYS` 白名单处置，即本条路 B 那行写死的「量纲坑须先处理」前置的兑现。〕
>
> **本条按用户要求用大白话写**。技术索引在最末一行，接手的人从那里进代码。

- **强度**: 🔴（**修法已入主干 · 判据未凑齐**（D1 1/3）；原判定依据 = **方向不安全 · 已实证非推断**——不是"可能有风险"，是这次全链跑批**从头到尾走通了**，最后印在报告上给读者看。同族先例：[DEFECT-PROSE-MASK-ESCAPE](#defect-prose-mask-escape-散文门逃逸洞--打码只覆盖-311-字段未核实数字原样印出🔴-方向不安全撞北极星)）

#### 一句话

**报告里写着「市盈率 30.79 倍」，后面挂的出处编号点开一看是「股价」——而系统不但没发现，还因为"编号存在"给了它最高信任等级。**

#### 这次具体发生了什么

最终报告里 4 个基本面数字（市盈率、市净率、净资产收益率、净利率）后面都挂着出处编号。逐个点开，**全都指向同一个地方：股价那一条**。

其中「净资产收益率 114%」在附录里被标成了**最高档「已核实」**，正文里**一个提示都没有**。

而同一段里，一个老老实实从网上查来的数字（AI 芯片份额 80–86%），倒是老老实实挂着「（未独立核实）」。

> **一个挂错出处的数字，比一个诚实标注来源的数字，更被系统信任。**
> 读者看到的可信度信号，跟真实可靠性是**反着来的**。

#### ⚠️ 先说清楚：这次数字本身是对的

市盈率、ROE 这些数值**确实是真的**，从行情源实实在在拉下来的。**这次没有产生错误结论。**

但这恰恰是问题：**数字对，是因为模型老实，不是因为系统验证过。** 那个"已核实"的章什么都没证明——它只检查了"编号存不存在"，从没检查"编号指的是不是这件事"。**下次模型不老实的时候，章一样会盖上去。**

#### 为什么会这样（三件事凑一起，每件单看都对）

1. **我们主动不给这些数字发出处编号。** 当初的顾虑是：基本面数字一旦发了编号，就会被自动认定"已核实"，而当时觉得这步不该放开，于是**特意不发**。
2. **模型没编号可用，就借了隔壁的。** prompt 要求每个数字必须标出处，它手上有数字、**没有一个对的标可挂**，于是抓了最近的那个。
3. **检查环节只问"编号存在吗"，不问"指的是不是这件事"。**

> **前门锁上了，模型从窗户进来了。** 「不发编号」原本想达到"拿不到已核实待遇"，实际达到的是"编号是错的"——待遇一分没少。

#### 🔑 最该注意的一点：模型试过说实话，被抹掉了

**不是某个模型的毛病——8 个分析师里 7 个各自独立绑错，而且绑的还不一样**（有的挂股价、有的挂币种、有的挂代码）。同一个约束下的必然反应。

**而且多数模型自己写了保留意见**：`Y-006 相关`、`Y-006 推算`、`Y-008 对应 yfinance`——它**知道**这不是一次精确引用，试图标注出来。

但系统认章时把限定词**剥掉了**，只剩光秃秃的编号：

> 模型说的是「这跟第 6 号**有关**」，系统听成的是「**出处：第 6 号**」。

这跟之前 [AX](#ax-ds-0-as_of-str-不收-llm-null--ds_researcher-node-fallback-脆性2026-07-24-aj-fresh-smoke-surface) 是同一个模式的镜像：AX 是模型诚实填「不知道」被拒收（**惩罚诚实**），本条是模型诚实标「这是推算」被抹平（**抹掉诚实**）。项目原则写着「不确定性诚实 > 数字正确」，**两处都是系统没给诚实留出口**。

#### 为什么没被任何一道门拦住

每一环都把"核数字"这件事委托给了下一环，最后一环拿着**被审对象自己的陈述**在审：

| 环节 | 它做了什么 | 它以为谁在管 |
|---|---|---|
| 审计 | 只查编号存不存在 | 输出侧的验章门 |
| 验章门 | 只看编号属于哪个册子 → 判最高信任 | AI 誊写核查 |
| **AI 誊写核查** | **收到的"来源原文"第一行就是待核的那句话本身** → 当然匹配 | （终点） |

**对照组证明这不是猜的**：同一次核查里另一条**被抓住了**（正文写「买入区 183–195」，来源只说了 183）——那条抓得到，是因为正文数字和来源说法**对不上**，自证失效。而市盈率那条，两者**完全一致**（都是模型自己写的同一个数），自证成立。

⇒ **AI 那道核查对本形态结构上就抓不到**，不是它判错了。

#### 还有一层：最后的总检查也看不见

终局 13 项质检**全绿通过**，其中一项名字就叫「证据误归因检查」，报的是 **0%**——**而上面那 4 条正是误归因**。说明它量的是别的东西，**名字让人以为这问题有人管，实际没有**。

#### 三条修法路（〔**2026-08-05/06 状态已变·见顶部 banner**：A/B ✅ 已合入 main `f9620ce` · C 仍未做。下方为立账期原文·point-in-time·不改〕~~都没动手~~·各有前置）

| # | 做什么 | 代价 | 前置 |
|---|---|---|---|
| **A** | **认章时保留模型写的限定词**——看到「推算/相关/对应」就不判最高信任 | **最便宜**（信号是模型自己给的，捡回来即可） | 无·可先做 〔✅ #226 改动二 —— 但实测只覆盖 **1/10**：限定词在 DS-0 汇总时已被洗掉，防线设在看不见证据的层 = 缺口 **G2**〕|
| **B** | 把**机械核数字**捡回来（比对"数字值 ↔ 编号指向的值"） | 中 | 承重变更·须用户裁；另有**量纲坑**（「4.86 万亿」vs 源里的 `4862365925376`）须先处理 〔✅ #226 改动三·用户 2026-08-05 拍板转正执法；**量纲坑由 `_COMPARABLE_DATA_KEYS` 白名单处置**（只有量纲有保证的登记键进可比集合·今日 = `{price}`）〕|
| **C** | 给基本面数字发它们自己的编号 | 中 | 碰当年 defer 的边界·须用户裁 |

> **B 不需要 AI**（[实测见下](#技术索引)）：本轮 13 条最高信任事实做纯数值比对，**10 条错绑全抓到、唯一正确的那条正确放行、零误报**。当年 2026-07-03 设计里就把线画清楚了——**结构化数据源（行情/财务接口）核值是纯机械的；只有自由文本源（研报正文）才需要 AI**。今天出问题的 10 条**全在机械那半**。

#### 连带：[AS](#as-web-派生-fact-缺干净数值源值级可信度-散文数字值无法确定性核-✅-closed-2026-08-05-close-by-supersede保留位置) 的重启判据**自锁了**

AS 当年降级时写的重启条件是「**AI 核查的 mismatch 真实出现且频繁**才回头建机械路」。但 AI 核查对本形态**结构上是盲的** → 这类问题**永远不会**让 mismatch 计数上升 → **判据永远不触发**。

与 [BB](#bb-段间-checklist-⑧-的-audit_passed--50-是空线五次-run-全-6132026-07-31-全链回归-e2e-surface) 同族（判据挂在不会响的信号上），区别是 BB 永远报警（吵）、本条永远不报警（**静默**）。

- **任务**: 按上表 A/B/C 三路择一或组合；**A 可独立先做**。
- **触发条件**: **随时**——每跑都在发生（本轮 10/13 = 77%）。但 B/C 属承重变更**须用户裁排期**；A 无前置。另：下次动 audit / 验章门 / 认章工具库时**必须**一并处理本条，否则又会绕过。
- **反向条件（close）**: 若改为"基本面数字发自己的编号"（路 C）落地且实测错绑归零 → close；或连续 3 次全链 e2e 的最高信任集合零错绑 → 降级重估。
- **为什么现在不做**: 2026-08-04 全链 e2e 期间发现，**全程纪律 = 只观察不改**（发现问题顺手改会导致改完没人复验）。且 B/C 都动主链路承重面，须用户拍。
- **进入时点**: 2026-08-04（BC 探针 e2e seg8/seg9 实证闭合）。**预估**: A 轻 / B 中（含量纲归一）/ C 中。**配额**: **DEFECT 族·不占 lettered 配额**。

#### 技术索引

现场（tracked）：[`seg8-pass0.p3-natural-sample.*`](../observations/bc-anchor-e2e-20260803/run-NVDA-zh-20260803/) · [`seg9-decision.p3-full-chain.checkpoint.json`](../observations/bc-anchor-e2e-20260803/run-NVDA-zh-20260803/) · [`archive-from-final.p3-full-chain.json`](../observations/bc-anchor-e2e-20260803/run-NVDA-zh-20260803/)。
链路：[`watermark.py` `_LAYER1_ONLY_KEYS`](../../src/committee/common_context/watermark.py)（不发锚）→ analyst 借锚 → [`audit_node.py`](../../src/committee/agents/audit_node.py)（只 `canon in ref_lookup`）→ [`stamp_check.classify_stamp`](../../src/committee/facts/stamp_check.py)（见 `REF#Y-` 前缀判 🟢）→ [`base._apply_ai_transcription_check` / `_transcription_source_text`](../../src/committee/agents/base.py)（把 `fact.claim` 放进"来源原文"首行 = 自证）。限定词剥离点 = [`stamp_families.split_stamps`](../../src/committee/facts/stamp_families.py)。~~空占位枚举 `audit_notpassed`（无生产者）= 路 B 的现成落点~~ → **2026-08-05 [#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 已落在该枚举上**（`_audit_fact_against_context` 核值分支 = 其唯一生产者），见 [audit-positioning 顶 banner + §3](../pipeline/decision/audit-positioning.md)；机械/AI 分界的原始设计见同文 §4「数字对不对」行。**修法后链路**：`audit_node` 三层收严（限定词 / 核值 / 出处有效性·后者含量纲白名单）→ `audit_gate` → 表③ → [prompts.py](../../src/committee/prompts/decision/prompts.py) `_FACTS_CITATION_GUIDANCE`（`audit_notpassed` = 写但强标注）。

---

### DEFECT-SEG2-FLAKY. seg2 并发研究段瞬时失败族 —— 三跑三坏·成因各异·疑共享资源竞争（🟠·攒表驱动·2026-08-03·交接新 session）

#### 📖 开工导读（大白话·2026-08-13 写·**新 session 先读这段**）

> **本段是入口，不是真值源。** 判据 / 全清单 / 逐条证据一律以
> [playbook](../plans/seg2-flaky-playbook-20260803.md) + [攒表](../observations/bc-anchor-e2e-20260803/seg2-failure-ledger.md) 为准；
> 两者与本段冲突时**以它们为准**。本段写于 2026-08-13，是 point-in-time 快照。

**⚠️ 先看清定调：这条现在的既定做法是「等它下次自己发作」，不是「主动去查」。**
2026-08-10 已把"不复现也能查的"查完了，并明确写死**下一步不再追加探针**。
新 session 若抱着"把它查清楚"开工，大概率空手而归——**有意义的开法是借跑批攒数据，或做那两个等用户拍板的决定**（见下）。

**一句话讲问题**：分析段有八位分析师同时开工。连续三次跑批，**每次都有一位塌掉、而且三次原因各不相同**——
一次超时、一次模型把格式写错、还有一次**整个人凭空消失、没有任何报错、跑批照常往下走**。第四次跑批是干净的。
怀疑不是某个零件坏了，而是**八路同时抢同一个出口**（同一个网络代理 / 同一份搜索预算 / 同一个模型网关），谁倒霉谁塌。

**已经拿到手的**（[C1 归因](../observations/seg2-c1-probe-2026-08-10.md) · [C2 探针](../observations/seg2-c2-probe-2026-08-10.md)）：
- 那次"凭空消失"**怎么做到不出声**的，已定位并实测复现——异常沿途被五层保护一路放行，最后被流程编排框架静默吞掉；顺带解释了"有时留兜底报告、有时整个消失"的不对称。
- 消失那位精确定位到**死在调工具那一刻**，不是随机哪里。
- **并发确实让响应稳定变慢 2–3 倍**（真实调用坐实）。其中取宏观数据那条腿最危险：**变慢最多、超时线又最紧，实测已用掉 8 秒线的 76%**（→ 已切出 §0.2 表里的 **BL**）。

**还没拿到的**：
- **异常到底从哪抛出来的，仍不知道**。头号嫌疑（研报接口那条腿）**既未坐实也未排除**——它压根没有整体超时上限，想做的压力测试做不出来。
- 并发竞争这个总假设，一轮探针 **96 次调用零失败 = 不结论**（那天网络太好）。**不许读成"问题不存在"。**

**已经做过的，别重做**：三次动手**只加了"看得见"、一次没动过控制流**——给宏观数据补报错类型、给模型输出补格式归一、给工具层和分析师层补"是谁 + 是哪个工具 + 完整栈"。
**这些不降低发作概率，只降低下次发作时的查证成本。**

**新 session 值得做的三件**：
1. **攒数据** —— 升级线是"失败满 5 次"或"静默消失再来一次"，现在是 3 次。任何一次日常跑批顺手记一行即可。
2. **两个等用户拍板的决定** —— ① 要不要让"被取消"的分析师也产兜底报告（代价 = 取消信号从此传不上去）；② 宏观那条腿余量只剩 1.32× 要不要动（限并发 / 加抖动重试 / 放宽超时——**第三条与 [playbook §8](../plans/seg2-flaky-playbook-20260803.md) 直接冲突，列它求完整、不推荐**）。
3. **下次真失败的当场**，立刻再跑一遍并发探针——那一刻才是该检验的现场，2026-08-10 读数作对照基线。

**硬规矩（[playbook §7/§8](../plans/seg2-flaky-playbook-20260803.md)·血换来的）**：跑批永不截断错误输出 · 失败现场先另存改名再重跑 · 不给任何工具加重试（重试 = 掩盖，先归因）· 不放宽任何超时线 · 不在完整跑批里调试那个静默消失（复现后用最小脚本）。

- **强度**: 🟠（影响工具可信度——seg2 连续三跑没有一次干净的 8/8 全良构；含一个 N=1 的**静默崩溃**：analyst 整个消失、无报错、run 照常续跑）
- **真值源 / playbook**: [docs/plans/seg2-flaky-playbook-20260803.md](../plans/seg2-flaky-playbook-20260803.md) —— 21 条失败模式全清单（T 工具 / C 并发 / O 输出 / G 编排 / E 环境 五层），每条带证据强度 + 检测信号 + 定位动作 + 修/忍判据。**新 session 从它开工，本条只是账**。
- **现象（2026-08-03 BC 探针 e2e·同一 seg1 checkpoint 三次重跑）**:
  | 跑 | 塌者 | 成因 | 现场（tracked） |
  |---|---|---|---|
  | 1 | fundamentals **整个消失**（7/8） | anyio `cancel scope` teardown 竞态（重跑未复现·历史 14 run 零命中） | `seg2-research.crash-7of8.*` |
  | 2 | macro 兜底 kp=1 | fred `ConnectTimeout` ×3（当时空 error 不可见） | `seg2-research.macro-fallback.*` |
  | 3 | fundamentals 兜底 kp=1 | 模型把 4 个 list 字段写成整段 str | `seg2-research.fundamentals-prose.*` |
  （目录：[bc-anchor-e2e-20260803/run-NVDA-zh-20260803/](../observations/bc-anchor-e2e-20260803/run-NVDA-zh-20260803/)）
- **统摄假设（待证/待伪）**: seg2 是全链唯一"8 路并发抢共享资源"的段（同一本地代理 / 同一搜索预算 / 同一 LLM 网关）——三跑塌者各不同、成因各不同，符合"高峰期谁倒霉谁塌"，不符合"单点固有缺陷"。
- **已修（[#224](https://github.com/JunoChenZt/subagent-for-investment/pull/224)·勿重做）**: ① fred 空 error 接 `_exc_detail`（run3 实测生效：报出 `ConnectTimeout` 类型名）；② sanitizer 补齐三兄弟字段（str→list 归一 4 字段·`sanitized` 留痕）。**修的是"塌后看得见、救得回"，不是"不会再塌"。**
- **未归因（新 session 的活）**: **C1 —— 2026-08-10 归因两轮：「无声」机制已定位实测，抛出源仍未定位**（见下"进展"）· **C2 代理挤爆假设 —— 探针已跑一轮（2026-08-10）＝不结论，既未坐实也未排除**（见下"进展"）· **G1 不对称机理已查清**（随 C1·分岔在 analyst 兜底的 `except Exception`，非 graph.py；改行为仍须用户裁）· T2 Serper 502 频率观察。
- **🔬 进展 2026-08-10 第二笔（C1 归因两轮·**唯一一次动生产代码**·仅加可观测性）**:
  - **产出**：[C1 结果文档](../observations/seg2-c1-probe-2026-08-10.md) · 攒表新增一行 · playbook **C1 + G1** 两行回填。
  - **✅ 「无声」的机制已定位并实测**：唯一能造出 run1 实物形态（`ainvoke` 正常返回 + 7 键齐 + 1 键**缺席** + **正常段产物**）的是**裸 `CancelledError`** —— 它绕过沿途 **5 层 `except Exception`**（wisburg 工具 / 工具执行器 / gather 无 `return_exceptions` / analyst 兜底 / `run_committee`），最后被 **langgraph 1.1.6 并行分支静默吞掉**。证据：8 路并行玩具图逐层镜像生产结构，零 LLM 零网络。
  - **✅ 顺带把 run1 定位精确一格**：`fundamentals` 只发 **1 次** LLM 调用（其余 7 位各 3 次）、输出是"Let me gather additional data" ⇒ **死在工具执行窗口内**，不是"某处随机消失"。
  - **✅ G1 的不对称机理同时查清**：分岔点在 [base.py](../../src/committee/agents/base.py) `make_analyst_node` 的兜底——`Exception`→兜底报告（键在）/ `BaseException`→绕过（键消失）。原预案指向 graph.py，**方向是错的**。
  - **❌ 证伪 playbook 原列两条候选**：anyio-style `RuntimeError`（是 Exception→出兜底报告）· `BaseExceptionGroup`（会崩 CLI，与实物不符）。**C1 行原题的归因措辞已作废**。
  - **🔴 抛出源仍未定位**：wisburg 头号嫌疑**既未坐实也未排除**。⚠️ **压力臂无效已划掉**（传 `timeout=0.3` 实跑 2.78s 仍成功）——根因是 `wait_for` 被设计禁用后 `timeout` 只当 connect_timeout ⇒ **wisburg 这条腿没有整体截止时间**，`_TOOL_TIMEOUT=8.0` 对它不构成上限（docstring 自述属实，**记录不动**）。故 C1 最核心的场景「工具超时进行中被取消」**本轮完全没覆盖**。
  - **⚠️ 一条设计前提被实测推翻（R5）**：analyst 兜底注释写"catch Exception (not BaseException) so CancelledError still propagates and **isn't swallowed**"——实测传上去的结果**就是**被 langgraph 吞掉。**本轮不改该设计选择**，只在注释写明前提失效 + 加日志。改行为（"异常也产兜底报告"）**须用户裁**，因为那等于让取消不再能传播。
  - **处置 = 只加可观测性、控制流一字未改**（用户 2026-08-10 授权·镜像 [#224](https://github.com/JunoChenZt/subagent-for-investment/pull/224) 给 fred 补空 error 的套路）：工具层记**哪个工具**、analyst 层记**哪位分析师**，均带类型名 + 栈后原样 `raise`；`KeyboardInterrupt`/`SystemExit` 豁免不记（否则一次 Ctrl-C 让 8 个 analyst 各吐带栈 ERROR，冲淡信号）；docstring `"Never raises"`→`"Never raises Exception"`。**DoD**：新增 9 测 + **变异验证**（抽掉两条 `log.error` 留 `raise` → 3 个日志断言转红、4 个不变式仍绿）+ 全套件 **3253 passed / 0 失败**。
  - **⚠️ 不得读成"C1 修好了"**：本轮**不降低发生概率**，只降低下次发生时的查证成本。N 仍为 1。
  - **下一步 = 不追加探针**，等下一次自然发生——届时新日志直接给出「哪位 analyst + 哪个工具 + 完整栈」，playbook C1 ②「复现即升 N=2 → 定位」才真正可执行。**仍守 §7 第 1 条：跑批永不截 stderr**（日志再全，被 `| tail` 截掉一样白搭）。
- **✅ 进展 2026-08-10 第一笔（C2 归因探针执行完毕·生产代码零改动）**:
  - **产出**：[结果文档](../observations/seg2-c2-probe-2026-08-10.md) · [攒表 seg2-failure-ledger.md](../observations/bc-anchor-e2e-20260803/seg2-failure-ledger.md)（run1-4 四行已回填 + 升级判据现状）· playbook C2/T1/§6 行已回填。
  - **判定 = 不结论**：96 次真实调用（fred 48 + web_search 48 · 2 臂 × 3 轮 × 8 · 臂序按轮交替 · 零 LLM 成本），**两臂均零失败**（零 429 / 零 502 / 零相关性拒绝）→ 命中 handoff §4 末行「全绿不算证伪」。**不许读成"问题不存在"。**
  - 🔬 **计划外观察（非事前判据·不用于改判定）**：并发使延迟**稳定膨胀 2–3 倍**（三轮无一例外）——fred p50 1.11→3.48s（3.1×）、web_search 2.24→4.53s（2.0×）。**fred 是双重暴露腿**：膨胀倍数更大、超时线更紧（8s），并发臂 **p90 5.34s / max 6.05s = 占满 8s 线的 76%**，单线程臂仅 28%。⇒ 统摄假设里"八路确实抢同一出口"这个**前提事实已坐实**，缺的只是越线那一刻；且形状与 run2（塌 fred·`ConnectTimeout`）对得上。web_search 经 [#221](https://github.com/JunoChenZt/subagent-for-investment/pull/221) 加宽到 15s 后余量约 2×，**当前该盯的是 fred 那条 8s 线**。
  - **没验到**：未复现失败（今日网络好）· 未覆盖第三个共享瓶颈 **LLM 网关**（探针零 LLM 成本的代价）· 本探针只有纯工具腿 8 路，**是真实 seg2 并发压力的下界** · 延迟膨胀发生在代理 / 事件循环 / 上游哪一层**分不出来**（分层测超出 handoff 边界，刻意没做）· N=3 单机单时点，不构成率估计。
  - **复跑判据（建议·非既定）**：下次 seg2 **真失败时当场再跑**同一探针——那一刻才是 C2 该被检验的现场；今日读数作对照基线。
- **任务**: ~~① 建 `seg2-failure-ledger.md` 攒表~~ ✅ 2026-08-10 · ~~② 跑 C2 归因探针~~ ✅ 2026-08-10（不结论，须择时复跑）；③ 按升级判据走：N≥5 瞬时类占多数 → 治本"限并发/错峰"（须用户裁）/ 格式类占多数 → prompt 层修 / C1 复现 N≥2 → 最小脚本定位。**当前 N=3，五条升级判据全部未达线**（现状见攒表表下）。
- **触发条件**: 每次 seg2 失败 → 记攒表一行（**这条随时在触发**）；C2 探针可立即跑（零成本）；升级动作按 playbook §6 判据。
- **反向条件（close）**: 连续 5 次 seg2 干净 8/8 全良构 → 瞬时类自愈或已被上游变化消解，close-by-decision。
- **为什么延后**: 瞬时类 N 不足，当场修 = 掩盖（playbook §8 明写不加重试、不放宽超时）；且归因 + 可能的 graph/并发改动是整块工作，用户拍**开新 session 处理**。
- **进入时点**: 2026-08-03（BC 探针 e2e seg2 三跑三坏后，用户拍"列全可能性、一次性做预案、只 plan 不做"）。**预估**: 探针轻 / 归因中 / 治本（若走限并发）中-重。**配额**: **DEFECT 族·不占 lettered 配额**（照 DEFECT-WEBSEARCH-RELEVANCE 先例）。

---

### DEFECT-FRED-KEYWORD. fred 工具**广告了实现认不出的拼写** —— 要利率，静默拿到 CPI（🟡·2026-08-04 BC 探针 e2e surface）✅ CLOSED 2026-08-13（close-by-completion·保留位置）

#### ✅ 收口（2026-08-13·取条目自荐的方案 ①）

**为什么这时候做**：BC 的最后两次全链 e2e 里有一次是**主题型 query** —— 那是唯一能走到 fred 那条
核对路径的机会（[builder.py](../../src/committee/common_context/builder.py) `_THEMATIC_SOURCES = ("fred", "rss")`，
`TICKER_SPECIFIC` 不拉 fred）。带着这个缺陷跑，宏观那一维会**静默缺席**。
⚠️ **分寸**：不修也能达成 [endgame G7](number-provenance-endgame.md) 的覆盖目标（fred 进不进得了表①
与拿的是哪个指标无关）；修了买到的是**那次跑批真的回答了它被问的问题**。

**落地**：[`_SERIES_KEYWORDS`](../../src/committee/common_context/sources/fred_source.py) **追加**
`fed_funds` / `interest_rate` / `interest rate` / `federal funds` / `federal_funds` → FEDFUNDS。
🔒 **一律追加在末尾**：`_resolve_series` 按插入顺序取**首个**子串命中，插在中间会改掉既有 query 的解析；
追加则只影响此前落默认值的那些 —— 行为变更面因此**可证明地窄**，并有守护测试钉住。

**🔒 R5 边界照条目原样守**：「认不出就落 CPI」是**设计**（源文件顶部注释 + TODO 写死），一字未动；
只修「广告了实现认不出的拼写」这半。**schema description 一字未改** —— 模型的输入面零变化，
改的只是同一输入下工具的返回。这也是条目倾向 ① 的理由（模型已经在按 schema 传了）。

**顺带把「广告 ↔ 实现」焊成机器可判**（超出条目字面任务·同 BG 思路）：守护测试从 schema description
里抠出所有被广告过的拼写，逐个断言**真被关键词表命中**（不是靠落默认值蒙混）。
⚠️ 判「命中」不能写成 `_resolve_series(s) == 期望值` —— `cpi`/`inflation` 的期望值恰好**就是**默认值，
那样写等于对它们没判；故直接判命中条件本身。另配「解析器抠不出东西就先炸」防空转假绿。

**验证**：新增 3 条守护测试 + **5 个变异全杀**（删 `fed_funds` / 删 `interest_rate` / 整批删回修复前 /
新别名插表首改掉既有解析 / description 解析器返空）+ 全套件 **3362 passed / 0 失败**
+ **真实 FRED 冒烟**（4 次 HTTP·零 LLM）：`interest_rate` 与 `fed_funds` 现在返回
`FEDFUNDS / percent / 3.63`（原为 `CPIAUCSL / index / 332`），`cpi`、`unemployment` 两条**逐字不变**。
⚠️ 变异脚本改用「按字节还原 + sha256 校验」——上一轮（BG）变异脚本被超时杀掉、`finally` 没走完，
留下一个被改坏的文件，而当时靠 grep 到注释行误判「没坏」。

**🔍 冷审一轮·5 个 finding 全修（2026-08-13）**：

1. **守护只判「认得出」、不判「认对了」** ⇒ 关键词表是**子串**匹配，复合拼写只要含老关键词就算过。
   将来广告 `'gdp_deflator'` / `'core_cpi'`，`gdp` / `cpi` 是它们的子串 → **绿灯放行**，
   而模型静默拿到名义 GDP / 整体 CPI ——**正是本 defect 那一类**，新守护原本拦不住。
   修法 = 加一份**期望落点声明表**（`_EXPECTED_SERIES_FOR_ADVERTISED`）：广告了却没声明落点 → 报红，
   逼着声明意图；再把默认值**临时换成哨兵**，让「命中」与「落默认」不再给出同一个答案。
   ⚠️ 顺带纠一处**方法论**：原守护**复刻**了 `_resolve_series` 的匹配规则（`kw in s`）而不调它本身 ——
   复刻出来的守护只守自己那份拷贝。现全部改为走真函数（**同 BF/BG「要判到承重那一层」**·第 4 次）。
2. **守护只覆盖参数说明这一个广告面** ⇒ 模型同时读得到工具级说明（`get_fred_data.description`），
   那里也在广告指标；且抽取只认单引号 + 写死 `>= 6` 下限 ⇒ 换个引号加第 7 个拼写，
   数量仍是 6、下限断言不炸、新拼写也没被断言 = 悄悄回到原病。
   修法 = 两个广告面都扫、引号风格不限（`'x'`/`"x"`/`` `x` ``）、下限改成**跟声明表现算**；
   机器抠不到的纯散文写法**靠约定不靠魔法** → 约定写进 [`FredParams`](../../src/committee/tools/definitions.py) 类文档串，改说明书的人**在原地看得到**。
   附带：本次新增的 `federal funds`（空格版）此前**没有任何一条测试碰到**，已补进回归锁。
3. **[dataflow 关键词表](../pipeline/dataflow-whole-pipeline.md) 未随改动更新** ⇒ 那张给人看的表还只写 `fed funds / 利率`，
   与实现再次错位（**就是本 defect 的形态**）。已补齐五个别名 + 追加顺序约束 + 真值源指针。
4. **本文档 [endgame](number-provenance-endgame.md) §5 散账处置表仍把本条记作「开」** ⇒ 该表是前向维护的现状表，
   下次盘活跃条目会把已修完的东西重新算进待办。已就地标前向事实（R7 live 状态就地改）。
5. **新写的 BK 跳转锚点拼错**（多「机制化」少「挂起」）⇒ 点了原地不动，
   而 [`lint_doc_links.py`](../../scripts/lint_doc_links.py) **明确跳过纯锚点链接** → 没有任何闸门会报。
   已按 GitHub slug 规则改正，并**先用三个已知正确的锚点校准规则再判新锚点**
   ——校准第一版就**证伪了**我原来的规则（全角括号被误留），不校准就会「验证」出一个错答案。

**冷审后复验**：6 个变异全杀（广告面加 `'gdp_deflator'` / 删 `interest_rate` / 整批删回修复前 /
**工具级说明用双引号加 `"core_cpi"`** / 抽取器返空 / 期望表把 `interest_rate` 声明成 `CPIAUCSL`）
+ 全套件 **3362 passed / 0 失败** + 三把 linter 全绿 + 锚点校准脚本 exit 0。

**节点复盘**：[docs/retro/S2/DEFECT-FRED-KEYWORD_2026-08-13.md](../retro/S2/DEFECT-FRED-KEYWORD_2026-08-13.md)
（合并前补跑 —— 同期 BF/BG 都有而本条缺，属 §2.7 Q5 反向命中并已纠正）。
其中两条 **defer 到独立 governance 线、未混入本 PR**：① 升坑表候选「新造的闸门自己带着它要治的病」
（与 [BG](#bg-往-env--envexample-加数值项会静默架空测代码默认值的断言--无人守2026-08-03-223-review-沉淀切出) 同形·**同日 N=2**）；
② 纯锚点链接（`#xxx`）目前无人校验 —— `lint_doc_links.py` 明确跳过，本轮那个死锚点就是这么溜过去的。

> 🔬 **顺手实测（本条 defer 的规模判据，已从"估"变成"数"）**：写了个一次性扫描器（先用 3 个已知
> 正确的锚点校准 slug 规则再出结论），扫本文件 **162 个页内锚点 → 61 个跳不到**（38%）。
> 〔初测 **62**，含我自己刚造的那一个；改对后为 61 —— 此处取修正值〕
> **形态单一**：条目 close 时标题追加了 `✅ CLOSED …` 后缀，而指向它的旧链接没跟着改
> （Z / AB / AP / Q / AS 等抽查逐个吻合）。
> ⚠️ **我自己当场也造了一个**：本段这条 BG 链接第一版就是死的（凭记忆缩写标题），
> 靠同一个扫描器逮住才改对 —— **N=2 同一 session 内**，这条债是活的不是历史的。
> ⚠️ 另：扫描器第一版把标题里的 markdown 链接 URL 也喂进 slug，多报了 2 条；
> **数字以修正后为准**。⇒ 接 linter 前须先清存量，直接上 hard-fail 会当场全红。
>
> ✅ **存量已清（2026-08-14·用户拍「61 条全修」）**：本文件 **162 个页内锚点 → 0 死**；
> 顺带清了其余文档 6 条 ⇒ **全仓 175 个锚点 → 0 死**。
> 其中最后一条（[pr-8b-readiness.md:80](../observations/pr-8b-readiness.md)）**连可见文字也错**
> ——写着「§9 启动 checklist」而该节现为 §8，只改跳转会自相矛盾 → **用户拍「可见文字一起改」**后修完。
> 顺带把该处的「第一项」改成**点名那一项**（原文指的其实是第 3 项·且**序号会随清单增删漂移、名字不会**）。
> **修法可复核**：先用 3 个已知正确锚点校准 slug 规则 → 四级匹配（前缀 / 归一 / 条目 ID / 最长公共前缀）
> 每级都要求唯一命中 + **同条目 ID 安全闸**（ID 对不上一律不改，宁可留着人工看）→ 按字节写盘。
> 🔒 **Q6 已守**：61 条里 **23 条落在已 close 条目正文内**，事前就此**单独请示并获准**；
> 且已**机器证明**改动是 href-only —— 把全文所有页内跳转地址抹平后，改动前后**逐字节相同**
> （`sha256` 同值·3588 行零非锚点差异）⇒ 可见文字与任何结论**一个字未动**。
> ⇒ **「接 hard-fail 前须先清存量」这个前置条件现已解除**（该 defer 项本身仍未做，见上）。

**未做（显式登记·非遗漏）**：条目「顺带可考虑」的 **认不出时返回 `matched: false` 显式信号**。
理由 = 那会改**模型看得见的返回结构**，而马上要跑的两次 e2e 是**测量跑批**，此刻加变量不划算；
且它治的是「静默」这一面，与本次治的「拼写认不出」是两件事。**建议随下次动 fred 时做。**

**🚩 条目里那条副发现未随本条解决**：**工具调用的入参不进归档** ⇒ 「广告 vs 实现」这一类错配
**无法从归档反查**，只能靠读代码撞见（本条就是撞见的）。这是可观测性缺口、不是 fred 的问题，
**归属待用户裁**（与 [BK](#bk-静默降级可见化--系统悄悄降级时必须留痕2026-08-07-闸门矩阵第-2-层挂起) 同族：系统悄悄少做了事而无人知）。

---

- **强度**: 🟡（**能力静默缺失·非错数字到读者**——本轮**没有**造成错误数字：模型读了返回里的 `series_id`/`unit`，把它**正确标成了「CPI 指数 332.57」**。真实后果是**利率这一维根本没拿到，而没人知道拿不到**）
- **一句话**: 工具 schema 告诉模型可以传 `fed_funds` / `interest_rate` 取联邦基金利率，实现的关键词表里**这两个拼写一个都没有** → 静默落回 CPI。

#### 已核（代码层确定·不依赖跑批）

| 层 | 内容 |
|---|---|
| **广告** | [`FredParams.indicator`](../../src/committee/tools/definitions.py#L57) description 写死：`'fed_funds' or 'interest_rate' (Federal Funds Rate)`，并注 `Default: CPI if unrecognized` |
| **实现** | [`_SERIES_KEYWORDS`](../../src/committee/common_context/sources/fred_source.py#L36) 只有 **`"fed funds"`（空格）** 和 **`"利率"`**，没有 `fed_funds`、没有 `interest_rate` |
| **匹配** | [`_resolve_series`](../../src/committee/common_context/sources/fred_source.py#L59) 是**子串匹配** `if kw in q` → `"fed funds" in "fed_funds"` **为假**（下划线 ≠ 空格）→ 落 `_DEFAULT_SERIES = "CPIAUCSL"` |

**其余三个广告拼写都是好的**（`cpi`/`inflation`→CPIAUCSL · `unemployment`→UNRATE · `gdp`→GDP），**只有利率这一对全断**。

#### 🔒 R5 分界（哪半是设计、哪半是缺陷）

- **「认不出就落 CPI」= 设计，不是 bug**。[fred_source.py:31-35](../../src/committee/common_context/sources/fred_source.py#L31) 注释写死：「query→series 智能映射非本节点 de-risk 焦点；默认 CPIAUCSL」+ TODO 扩映射。**一手设计记录充分**。
- **缺陷在另一半**：tool 层（`definitions.py`）**广告了 source 层认不出的拼写**。两个文件各自都自洽，**错配在它们之间**——schema 作者显然意图让 `fed_funds`/`interest_rate` 被**认出来**（否则不会写进 description），而 `Default: CPI if unrecognized` 这句反而让落回 CPI 看起来"符合预期"。

#### 本轮实测（含一条**未能实证**的环节·如实标）

- **✅ 实证**：seg2 macro 的模型明写「补充…**宏观利率环境**，让我获取 FRED 数据」→ 紧接着的 `[tool]` 返回是 `{"series_id": "CPIAUCSL", "unit": "index_1982_1984_100"}`（三个 seg2 变体 trace 均如此）。
- **✅ 实证（反向·限制了严重性）**：macro_report 里模型**没被骗**——`key_points` 与 `evidence_log` 都老实写成「**CPI 指数 332.57**」，没当利率用。同段 `失业率 4.2%` 正常（`unemployment` 命中 UNRATE）。
- **❌ 未能实证**：**模型具体传了哪个 `indicator` 字符串查不到** —— 工具调用的**参数全链不落盘**（`trace.md` 只记 `[tool]` 输出、`calls.jsonl` 里也没有）。故「模型照 schema 传 `fed_funds` → 落回 CPI」这条因果的**最后一环是推断**。

> **🚩 副发现（比本条本身更值得记）**：**工具调用参数不进归档** ⇒ 这一类「广告 vs 实现」错配**无法从归档反查**，只能靠读代码撞见。本轮就是撞见的。

- **任务**: 二选一（**都轻**）——① `_SERIES_KEYWORDS` 补 `fed_funds` / `interest_rate` / `federal funds` 等别名；② 或反过来把 schema description 改成实现真认的拼写。**倾向 ①**（改实现比改广告安全：模型已经在按 schema 传了）。**顺带可考虑**：认不出时在返回里带一个 `matched: false` 之类的显式信号，别让"静默落回"看不出来。
- **触发条件**: 下次动 `fred_source` / tool schema / MACRO_EVENT 分支时**顺手改**；或出现一次模型**真把 CPI 当利率用**（届时升 🟠——那就不是能力缺失而是错数字了）。
- **反向条件（close）**: 若 fred 的 query→series 映射被整体重做（源文件 TODO 里的「接 FRED series search 端点」）→ 本条随之消解。
- **为什么现在不做**: 2026-08-04 BC 探针 e2e 期间发现，**全程纪律 = 只观察不改**。且本轮零实际伤害、不阻塞任何事。
- **进入时点**: 2026-08-04（BC 探针 e2e seg2 排查 fred 空 error 时读代码撞见·用户拍「立条目」）。**预估**: 轻。**配额**: **DEFECT 族·不占 lettered 配额**（照 DEFECT-WEBSEARCH-RELEVANCE / DEFECT-SEG2-FLAKY 先例）。

---

### DEFECT-FRED-SUBSTRING. 问「毛利率」拿到「联邦基金利率」—— 中文子串匹配的假阳性（🟡·2026-08-18 [#246](https://github.com/JunoChenZt/subagent-for-investment/pull/246) 冷审 surface）

**一句话**：宏观指标是按**关键词子串**认的，而「毛**利率**」「净**利率**」里都含着「利率」——
问一家公司的毛利率，系统会去拉美国联邦基金利率。

**已实测坐实（非推断）**：`_resolve_series("茅台三季度毛利率怎么样")` → `FEDFUNDS`
（[fred_source.py](../../src/committee/common_context/sources/fred_source.py)）；`净利率`同。
正确应落默认的 `CPIAUCSL` 或干脆不认。

**🔒 R5 边界（照 DEFECT-FRED-KEYWORD 的分界原样守）**：子串匹配本身是**设计**
（源文件顶部注释 + TODO 写死「query→series 智能映射非本节点焦点」），缺陷在
**中文词的子串包含关系没被考虑** —— 英文侧 `cpi`/`gdp` 这类短词同理有风险
（`gdp` 作为任意标识符子串），但本次只实测到中文侧。

**暴露面两处（第二处是 2026-08-18 新增的）**：
1. **fred 自己的取数**（老暴露面·自 A6.1.3.1 起）：主题型 query 问毛利率 → 宏观那一维**拿错指标**。
   ⚠️ 伤害程度取决于模型怎么读——它拿到的 `series_id`/`unit` 是诚实的（标着 FEDFUNDS / percent），
   照 DEFECT-FRED-KEYWORD 那次的实测，模型会如实标成「联邦基金利率」而非当成毛利率用
   ⇒ **倾向 🟡 非 🟠**（拿不到想要的 ≠ 拿到假的），但**本条未实测**，仅按同族先例推断。
2. **路由的宏观安全网**（[#246](https://github.com/JunoChenZt/subagent-for-investment/pull/246) 新增·**继承同一张表**）：
   标的型 query 问毛利率 → 误触发、多拉一个宏观源。**方向安全**（只加源不减源、不改判定），
   代价仅是一次多余取数。#246 已用测试**钉住该假阳性现状**（匹配语义一变即红）。

**任务**（三选一·均须先量再改）：① 给中文关键词加词边界（如要求「利率」前不紧邻「毛/净/股息/汇/费」等修饰字）；
② 把关键词表从「子串」改成「显式别名全词表」，代价是要补齐拼写变体（DEFECT-FRED-KEYWORD 刚补过一轮，可复用其守护测试）；
③ 走源文件 TODO 的治本路（接 FRED series search 端点），本条随之消解。
⚠️ **一律追加/不得插表首**：`_resolve_series` 取**首个**子串命中，改顺序会改掉既有 query 的解析（同 DEFECT-FRED-KEYWORD 的锁）。

**触发条件**（全事件型·守 [§4.1](#41-新增-backlog-条目)）：下次动 `_SERIES_KEYWORDS` 或 `_resolve_series` /
接第二个宏观数据源 / e2e 出现一次「问公司财务比率却拿到宏观指标」实例（届时升 🟠——那就不是能力缺失而是真拿错）/
用户明确要求。

**反向条件（close）**：fred 的 query→series 映射被整体重做（源文件 TODO 的 series search 端点）→ 本条随之消解。

**为什么现在不做**：发现于 [#246](https://github.com/JunoChenZt/subagent-for-investment/pull/246)（补路由安全网），
修它 = 改 fred 主路径的 series 解析，**超出那个 PR「只加一条不减源的安全网」的边界**；
且该 PR 的暴露面方向安全（多拉一个源），不阻塞。**用户 2026-08-18 拍「另立条目」。**

**进入时点**: 2026-08-18（#246 写反证测试时，负例用了「毛利率」当场变红撞见）。**预估**: 轻（词边界 1 小时 + 守护测试）。

---

<a id="defect-yf-ticker-truncation"></a>
### DEFECT-YF-TICKER-TRUNCATION. 要比特币拿回另一个资产的价格 —— 代码被截断后**恰好命中一个真实代码**（🟠·2026-08-19 seg1 数据源探针实测） ✅ CLOSED 2026-08-21（close-by-completion·保留位置）

#### ✅ 收口（2026-08-21·随 seg1 G4 第一层·取条目自荐的修法）

**改了什么**：让**已确认代码**那条路认四类资产码（期货 `GC=F` / 指数 `^GSPC` / 加密 `BTC-USD` / 汇率 `EURUSD=X`），格式**逐条抄 2026-08-20 实测表**（12/12 全通，无官方文档可抄）。此前它们在这里被刷掉 → 掉回字符串抠取 → 截断。

**🔒 R5 边界照条目原样守**：`_US_CASHTAG_PATTERN` **一字未动**。条目写死「缺陷不在"严"，在结构化那条路不认资产类代码；不得放宽正则」—— 放宽 = 把 2026-05-19 收紧时根除的假阳性坑搬回来。**并加了一条守卫测试**：谁放宽那条正则，测试当场变红（变异 M5 实证）。

**⛔ 刻意不收 A 股（`.SS`/`.SZ`），即便实测表里有** —— G4 给的资产类是贵金属/原油/指数/加密/汇率，A 股不在列；且**「同一标的到不了两个源」正是 2026-08-20 撤销「复权口径假不匹配」那条推断时压着的前提**，收了 `.SS` 该顾虑当场复活（同标的两源、一个复权一个不复权）。要接是另一件事、须单独裁。已加测试钉住这个"不收"。

**顺带堵一个同族坑（不堵就是重踩港股那次）**：币种此前除港股外**一律标 USD**。接了资产类码还这么标，等于把当年「腾讯 HKD 被标成 USD」原样再来一遍。⇒ 推得出的推（加密/汇率把计价币写在代码里），**推不出的返回 `None` 绝不猜**：期货代码里没有币种信息、**指数根本没有币种**（无量纲点数）—— 把"不适用"写成 USD 是编，而价格是承重数据。

**验证**：新增 [test_yfinance_asset_classes.py](../../tests/test_yfinance_asset_classes.py) 37 条，含条目点名要求的**截断形态反向断言**（喂 `BTC-USD` 要么拿到比特币、要么明确失败，**绝不返回另一个代码的价格**）+ **对照组证明缺陷本体仍在字符串抠取那条路上**（少了它，前一条证明不了是结构化路救的）。**五个变异全杀**：删掉资产类档 / 币种一律填 USD / 汇率取错边 / 顺手收 A 股 / 放宽严格正则。全套件 **3514 passed**，四把 lint 全绿。

⚠️ **只做了第一层**：本条 close 的是「拿到代码却取错资产」。**BQ 那半没关** —— 主题型问题**根本不激活价格腿**，而"黄金"→`GC=F` 是**语义映射、只有规划员能做**（G5），任何正则都做不到。详见 BQ 条目与[取数流程页](../pipeline/00-retrieval.md) G4 行。

**反向条件已满足**：结构化代码路支持资产类代码 ✅ + 截断形态有反向断言守护 ✅。

**一句话**：从问题字符串里抠美股代码的规则**只认字母**，`BTC-USD` 被截成 `BTC`——
而 `BTC` 恰好是另一个真实存在的代码，于是系统**给回了另一个资产的价格，结构完好、无任何报错**。

**已实测坐实（非推断·[原始响应](../observations/source-shapes-20260819/raw/yf_B_crypto.json)）**：
```json
{"source": "yfinance", "market": "US", "ticker": "BTC",
 "price": 28.57, "currency": "USD", "as_of": "2026-08-18"}
```
要的是比特币，拿回 `$28.57`。**有时间戳、有货币单位、格式完美、零日志。**
⚠️ **2026-08-20 订正**：原写「（十万美元级）…差约三千倍」是**推断非实测**；同日双边实测 `BTC-USD`=**69242.11** vs 残码 `BTC`=**30.27** ⇒ **约 2290 倍**。
✅ **同日坐实定性**：绕过本仓正则直接问库，**12 种资产代码 12/12 全部拿到价格**（`GC=F` 黄金 4548.20 / `^GSPC` 7707.98 / `EURUSD=X` 1.168 / `600519.SS` / `0700.HK` …）⇒ **库侧零障碍，缺陷 100% 在本仓的代码抠取那一层**；G4 白名单可直接抄该实测表（[证据](../observations/api-intake-batch-20260820/yf_symbology.json)·[接口说明](../infrastructure/seg1_retrieval/yfinance-api.md)）。

**同族两例（同次探针·[GC=F](../observations/source-shapes-20260819/raw/yf_B_gold_futures.json) / [^GSPC](../observations/source-shapes-20260819/raw/yf_B_index.json)）**：
- `GC=F`（黄金期货）→ 截成 `GC` → 雅虎无此代码 → 重试三次 → 失败，**耗时 13.54 秒**（超单源 8 秒预算）
- `^GSPC`（标普）→ `$` 后首字符非字母 → 抠不出 → 抛错降级

**机理（已核代码非推断）**：[yfinance_source.py](../../src/committee/common_context/sources/yfinance_source.py)
取代码有两条路——先试**外部传入的结构化代码**，拿不到才回退**字符串抠取**
（`_US_CASHTAG_PATTERN = r"\$([A-Za-z]{1,5})\b"`）。三个资产类代码在**第一条路就被校验刷掉**
（它只认股票形态），于是全部落到第二条路被正则截断。

**🔒 R5 边界**：严格 cashtag 本身是**设计且是对的** —— 2026-05-19 用户裁决收紧，
为的是根除「"I think AAPL is great" 里的 `I` 被当成代码」那类假阳性（源文件注释写明）。
**缺陷不在"严"，在"结构化那条路不认资产类代码"** ⇒ 修法应从**放宽结构化校验**入手，
**不得放宽正则**（放宽 = 把当年那个坑原样放回来）。

**🔒 严重度定 🟠 的理由 + 现状可达性**：
- 定 🟠 而非 🟡：价格是**承重数据**（买入区间 / 目标价建立其上），且失败形态是**静默给回错资产**
  —— 不是"拿不到"，是"拿到假的"，方向与 **DEFECT-FRED-SUBSTRING**（见上一条）不同（那条是拿不到想要的）。
- **今天生产里触发不到**：主题型 query 根本不激活价格源（= **BQ** 本身），个股型的代码来自名录对账、
  不含 `=F`/`^`/`-USD` 形态 ⇒ **目前是潜伏缺陷**。
- ⚠️ **但一动就活**：BQ 的修法若按「把资产代码喂进去」的天真做法做，**它当场从潜伏转为常态**。
  故本条**必须在 BQ 之前或同批处理**。

**任务**：让结构化那条路认资产类代码（贵金属 / 原油 / 指数 / 加密 / 汇率），
并对**已知会被截断的形态**加反向断言测试（喂 `BTC-USD` 必须**要么拿到比特币、要么明确失败**，
**不得**返回另一个代码的价格）。⚠️ 守坑表 (a')：该测试落地时须**反向变异证明它会 fire**。

**触发条件**（全事件型）：动 **BQ**（§0.2 活跃表）/ 动 `_extract_us_ticker` 或结构化代码校验 /
接任何资产类行情 / e2e 出现一次「价格对不上标的」/ 用户明确要求。

**反向条件（close）**：结构化代码路支持资产类代码 + 截断形态有反向断言守护。

**为什么现在不做**：发现于 seg1 数据源盘点探针（写数据源说明书时顺带实测），
**不属于那次的边界**；且今天生产不可达。**用户 2026-08-19 拍「单独立」。**

**进入时点**: 2026-08-19（[数据源形态探针](../observations/source-shapes-20260819/)实测撞见）。
**预估**: 轻-中（校验放宽 + 代码格式白名单 + 反向断言测试，半天）。
**配额**: **DEFECT 族·不占 lettered 配额**（照 DEFECT-FRED-SUBSTRING / DEFECT-WEBSEARCH-RELEVANCE 先例）。
**配额**: **DEFECT 族·不占 lettered 配额**（照 DEFECT-FRED-KEYWORD / DEFECT-SEG2-FLAKY 先例）。

---

### DEFECT-MCP-ISERROR. 外部工具的**错误装在正常返回里**，我们从不检查 —— 错误文本拿到引用编号、被当证据引用（🟠·2026-08-20 seg1 前置探针实测 + 归档实锤）✅ CLOSED 2026-08-20（close-by-completion·保留位置·**审查那半已拆出独立条目**）

#### ✅ 收口（2026-08-20·取条目自荐的修法，落在封装层）

**改了什么**：[`MCPClientWrapper.call_tool`](../../src/committee/mcp_client/wrapper.py) 拿到返回后判 `isError`
→ 抛新异常 `MCPToolError`（带**工具名 + 服务端错误文本**）。选封装层而不是只修 [wisburg_source](../../src/committee/common_context/sources/wisburg_source.py)
的解析函数，是因为**那句"所有错误都会抛"本来就写在封装层的契约里** —— 这不是改规矩，是让代码兑现它自己
早已写下的承诺；第二个 MCP 消费方将来自动受益。下游降级路**原本就在且已测**（dispatcher
`gather(return_exceptions=True)` → 非 dict 结果跳过 → 该源缺席 → `degraded`）。

**📐 同批立下分层约定**（写进两处 docstring，给 G4b 批量取数用）：**封装层一律抛，粒度归调用方**。
批量取 N 篇时第 3 篇失败不该毁掉其余 N−1 篇 ⇒ 逐篇 catch 归**批量层**，别把容忍逻辑塞回封装层。
今天只有一个消费方、一次 fetch 一次 call，失败即本源无数据，**不加 catch 才是诚实的**。

**🔒 边界照条目守**：`_parse_tool_result` **接受纯文本的行为一字未动** —— 合法的纯文本内容确实存在，
修的是"错误也走这条路"，不是"纯文本不许走"。故 `test_parse_non_json_text` 保持有效、无冲突。

**验证（反向变异，不靠"跑一次是绿的"）**：新增 [test_mcp_iserror.py](../../tests/test_mcp_iserror.py) 六条，
核心是**真 MCP 协议**三面对照（内存版 FastMCP server，无网络，**不手搓 `CallToolResult`**）：
① 出错工具经封装层 ⇒ 抛 `MCPToolError` 且错误文本没丢 · ② ⭐ **对照组 = 缺陷本体**：同一工具走裸 SDK
**确实不抛**（少了这条，①可能只是因为 SDK 本来就会抛而变绿）· ③ 正常工具照常返回（证明不是无差别乱抛）。
另加消费方不吞断言 + `_error_text` 两条边界（无文本时据实说明 / 超长截断**留标记**）。
**已实跑变异**：把 `isError` 判断删回修复前 → 针对本次修复的那条如期变红（实得 `CallToolResult(... isError=True)`，
错误文本原样躺在 content 里 —— 变异输出本身又坐实了一遍缺陷形态）；还原后全绿。
全套件 **3421 passed / 0 失败**（3415 + 新增 6），四把 lint 全绿。

**⚠️ 本次只修四缺口里的 ①**：`isError` 归本条；[另三条](../plans/mcp-client-四缺口-设计pass-2026-08-20.md)中
**④ 读超时**已于同日 [#257](https://github.com/JunoChenZt/subagent-for-investment/pull/257) 单独修完，
**②会话复用 / ③配额闸重定义**必须同批、随 G4b 走，**不在本条**。

**⚠️ 审查那半没有随本条关闭**：见下方 `DEFECT-REVIEW-ERROR-AS-DATUM`（照原条目"独立成立"的裁定拆出）。
修好本条后那个**具体实例**不会再发生（错误文本压根到不了引用清单），但"审查该认什么才算数据点"是另一个命题。

---

**一句话**：MCP 工具的失败**不抛异常**，而是以 `isError: true` + 一段错误文本的形式**混在正常返回里**回来；
本仓生产代码**全仓零处检查这个标志**，解析函数把错误文本**原样当成内容**塞进 payload ⇒ 它会像真数据一样拿到引用编号、进引用清单、被下游当证据引用。

**实测坐实（2026-08-20·[FINDINGS §3](../observations/seg1-probes-20260820/FINDINGS.md)）**：给 `get-report-detail` 传字符串编号，返回
```
isError: true
content: "MCP error -32602: Input validation error: ... expected \"number\", received \"string\""
```
**调用方收不到任何异常。**

**归档实锤 —— 这已经在生产发生**（[D1-ROOT-e2e run1 trace](../observations/D1-ROOT-e2e/run1-micron-resume/seg9-decision.trace.md)，origin/main tracked）：智堡 **503 错误拿到了 `[REF#W-003]`**，然后
- 基金经理写进要点：`"no institutional reports available (Wisburg API 503) [REF#W-003]"`
- 分析师当数据缺口引用：`"缺乏 institutional positioning 数据（wisburg API 503 [REF#W-003]）"`
- 🔴 **审查环节把它算作"具体数据点"**：`"Evidence log includes concrete data points: yfinance price ($1032.28), rss headline text, and wisburg API error code (503)."`

**契约与实现对不上（一手）**：[wrapper.py](../../src/committee/mcp_client/wrapper.py) 模块 docstring 明写
`Failure semantics: all errors raise (timeout, network, quota exceeded). Caller (WisburgSource) is responsible for catch → degrade.`
—— **契约说"所有错误都会抛"，而工具层错误不抛** ⇒ 调用方那条 `catch → degrade` 在这类错误上**永远走不到**。
解析处：[wisburg_source.py `_parse_tool_result`](../../src/committee/common_context/sources/wisburg_source.py) JSON 解不动就 `payload["text"] = item.text`。

**~~⚠️ 未核实的前提（动手前必须先确认·R5）~~** ✅ **2026-08-20 已核实解除**（论证全文见[设计 pass §2.2](../plans/mcp-client-四缺口-设计pass-2026-08-20.md)）：`isError` 是 MCP 协议标准字段，封装层写契约时**可能根本没意识到它存在**（那句 docstring 读起来像"以为全都会抛"）。~~**是疏漏还是有意，未经证实** —— 不得据本条直接开修。~~ ⇒ 查完**无任何证据支持"有意"**，四条独立佐证指向疏漏：① 承载该契约的 14 行 docstring **三句错两句**（另两句已各自证伪）⇒ 是动工前的计划陈述、不是完工后核过的契约；② 当年专为"看清真实 `CallToolResult` 形状"搭了内存版 MCP server，`isError` 正是该对象顶层字段 —— **仪器搭了、只对准 shape 没对准 status**；③ **同仓我方对外 MCP 服务正是靠 raise→`isError` 报错的**，同时持有"我方靠它报错"与"对方会抛异常"两个互斥模型，只有没想过时才可能；④ `git log -S isError --all` 显示这个词**在全仓提交史里从未出现过**（只命中 08-20 发现它的文档 commit）。⚠️ 诚实标注：这是**文档记录层面的论证**、非作者证言（PR #126 行内 review 讨论未能取回）。

**为什么现在要紧**：seg1 取数改造要把研报腿的调用量从 1 次抬到 4–60 次，**且配额若真存在、超限极可能就是这个静默形态**（[计划 §2.2.4](../plans/seg1-前置探针-计划-2026-08-20.md) 那条"最高优先级分支"已被本次证明是现实形态，只是触发它的是参数校验不是配额）。同时它给[回核层](../plans/seg1-取数计划-设计pass-2026-08-19.md) §3.5b 加了一条必核项：**研报腿要先判"这是不是一条错误"，再谈相关性**。

**触发条件**: 下次动 [wisburg_source](../../src/committee/common_context/sources/wisburg_source.py) / [mcp_client](../../src/committee/mcp_client/wrapper.py) / seg1 回核层落地（G4b 或 G5）时；或再出现一次"错误文本进引用清单"。
**~~反向条件（close 不做）~~** ⛔ **未走反向条件，走的是 close-by-completion**（见顶部收口块）：~~若确认为有意设计（把"源不可用"当作一条可引用的事实登记）→ 降 🟢 并改记使用边界~~ —— 前件已被 R5 核实证伪（不是有意设计），故此路不适用。⚠️ 原条目那句"**审查环节把错误码算作'具体数据点'这一条独立成立、不随之关闭**"**照办了**：已拆成下方独立条目 `DEFECT-REVIEW-ERROR-AS-DATUM`，**没有随本条一起关掉**。
**进入时点**: 2026-08-20（seg1 前置探针顺带撞见）。**预估**: 轻-中（封装层判 `isError` → 抛或显式降级 + 反向变异测试证明会拦）。**实际**: 与预估相符（半天内落地，改动集中在一个只有一个消费方的封装件）。
**配额**: **DEFECT 族·不占 lettered 配额**（照 DEFECT-FRED-SUBSTRING / DEFECT-YF-TICKER-TRUNCATION 先例）。

---

### DEFECT-EMPTY-AS-FAILURE. 「查了，没有」被报成「系统坏了」—— 成功的查询走了失败那条路（🟡·2026-08-21 [#262](https://github.com/JunoChenZt/subagent-for-investment/pull/262) 冷审 surface·**用户裁单独立项**）

> **✅ CLOSED（2026-08-25·[#266](https://github.com/JunoChenZt/subagent-for-investment/pull/266)）**：宏观源两处"查了没有"（空 `observations` / 取回全是缺失哨兵）**已从 `raise ValueError` 改为返回体面的零**——`{source, status="no_observations", as_of="", _meta:{series_id, units, periods}}`，**全键皆 meta ⇒ 产 0 条引用**（不发 `value`/`observations` 空壳，也不发 `count`/`series_id` 溯源章）。工具层 `_exec_fred` 据 `status` 标记走 `tool_empty`（series_id 从 `_meta` 读）；降级判据零改动（源一正常返回，`quality_flag` 自动保持 `ok` = 兑现用户 2026-08-21「查了没有不算降级」裁决）。**"认不出指标"仍抛 → validation**、结构异常仍抛 → 降级，均与"查了没有"分开。下方 point-in-time 正文不动。
> **冷审收严三条**（详见[前置探针 observation](../observations/defect-observations/../defect-empty-as-failure-watermark-probe-20260824.md) 的 08-25 修订段）：① 早先方案发 `count=0`+`series_id` 两条引用，被指"给数值 fact 误绑添入口"（改动四虽兜底、`numeric_value is None` 时被绕过）→ 改成 0 引用；② `count=0` 会进溯源段 = `DEFECT-REVIEW-ERROR-AS-DATUM` 形状 → 随①一并消除；③ 空返回第一次变可缓存会掩盖新发布 → `adapt_fred` 对空标记返 `None`（不缓存），详见 [observation 08-25 修订段](../observations/defect-empty-as-failure-watermark-probe-20260824.md)。**刻意不碰**：行情源"返回空表"（须先探真接口·公约 §7 未决）、新闻源（#262 已修）、audit 判据本体（残留缝见 `DEFECT-NUMERIC-VALUE-NULL-BYPASSES-AUDIT4`）。

> **一句话**：源**成功执行了查询、对方也正常应答了**，只是没有匹配数据 —— 这种情况今天一律抛错，和"连不上对方"长得一模一样。

**实证两处（均在 main 上，非某个 PR 引入）**：

| 处 | 触发条件 | 今天的行为 |
|---|---|---|
| 宏观源 | HTTP 200 + `observations` 为空（序列存在但该窗口无数据） | 抛 → 整条腿降级 |
| 宏观源 | 取回的这几期**观测值全部缺失**（同比在序列头一年本就算不出） | 抛 → 整条腿降级 |

**为什么要紧**：两种事实的下游动作**完全相反** —— "对方暂时不行"该重试，"查了确实没有"**本身就是结论**、重试纯属浪费。混在一起时，模型只能把后者当前者处理：重试若干次、再上报，最后得到一个本可以直接说出口的答案。这也是[工具报错公约](tool-error-contract.md) §3 点名的核心考点。

**🔒 边界（别读大）**：

- **本条只管"源那一层还在抛"**。工具层那一半 **2026-08-21 已随公约落地**（返回 `isError: false` + `resultCount: 0` + 一句"查询已成功执行"），源一改过来就自动生效
- **新闻源那处不在本条里** —— 它是 [#262](https://github.com/JunoChenZt/subagent-for-investment/pull/262) 自己引入的（改造前有家保底媒体总能凑出条目），**归那个 PR 修**
- ⚠️ **行情源「返回空表」不在本条射程内**：那可能是"代码不存在"/"窗口内没交易"/"接口抽风"三者之一，**从返回体上分不分得开须先探真接口**，不凭推断归档（公约 §7 已登记为未决）

**处置方向**：零结果改成正常返回（带一个明确的"零"标记），由调用方按"有没有数据"判，而不是按"抛没抛"判。⚠️ 连带要确认的一处：`quality_flag` 今天要求非价格源**逐个都得成功**，而**用户 2026-08-21 已裁「查了没有」不算降级** ⇒ 改源的同时要让它别再挂降级标记。

**为什么延后**：改的是源的失败语义，牵动调度器降级判据与既有归档对照，**范围比工具层那一半大一档**；且它是 main 上的存量、不阻断当前两个 PR。
**进入时点**: 2026-08-21（报错公约落地时切出，用户裁"单独立项"）。**预估**: 半天（两处源 + 降级判据 + 反向变异证明"零结果不再降级"）。
**配额**: **DEFECT 族·不占 lettered 配额**（照 DEFECT-FRED-SUBSTRING / DEFECT-MCP-ISERROR 先例）。

---

### DEFECT-NUMERIC-VALUE-NULL-BYPASSES-AUDIT4. 「改动四」那道非可比出处闸，在 `numeric_value is None` 时被绕过（🟡·2026-08-25 由 [#266](https://github.com/JunoChenZt/subagent-for-investment/pull/266) 冷审拆出·subagent 调查坐实）

> **📌 2026-09-09 · CRED.1.G3 修法 ✅ 已合 main `e7fe42b`（PR [#284](https://github.com/JunoChenZt/subagent-for-investment/pull/284)·方案 C 用户裁·分支已删）+ 🔴 一个比本条更大的发现 —— 本条**不 close**（剩余项在下）
> **本条原记「活体复现 0」是错的**：用真实表①回放主干 25 跑 1508 条事实，原 `audit_passed` 139 条里 **35 条是带量纲的真量值却无 `numeric_value`**（「2026Q1 营收 194.96 亿元，同比增长 192%」盖了通过章）。原「0」量的是条目触发条件里的「拿到 🟢」（可信度档），不是 audit 层。
> **修法（下游兜底）**：`numeric_value is None` 且正文剥掉标记与四类有限语义噪音（日期时间 / 裸年份 / 指数名 / 证券代码）后仍含数字 → `audit_notsure`。回放降 48/139 passed（34.5%·复核五修后定稿：年份/6 位数走老先例整套守卫、认章换 `_LEGAL_STAMP_RE`、日期收紧、加有界裸引用核），漏真量值 0。
> **🔴 连带发现·本条剩余项（不随 G3 close）**：35 条量值没提取出 `numeric_value` = **事实整理（pass0）那步的提取器本身漏得厉害** —— G3 只是让漏网的不再盖通过章，**没治提取**。触发 = 下次动 pass0 提示词 / `FactInventoryItem.numeric_value` 抽取逻辑；或 G3 上线后 e2e 看到 notsure 占比明显抬升时回头量提取率。
> **📌 2026-09-10 · CRED.1.G5 收口跑已按上句「回头量提取率」量了一次 —— 条目 ✋ 仍不 close（剩余项未治）**
> 跑批 = [cred-1-g5-e2e-20260910](../observations/cred-1-g5-e2e-20260910/FINDINGS.md)（黄金·**主题型**）。**G3 改动确实在这一跑执行了**：**3 条**事实（`f11` `f23` `f64`）因「数字没抽出来但正文有数字」降 `audit_notsure`〔🔴 **初版写「7 条」是错的**·冷审订正：7 是拿正则数的「无主数字且正文带数字」、混了三类成因（G3 降 3 / 水印是外部章降 3 / 直接 passed 1）；判据应取审计自己写的 `audit_rationale`〕。**且这 3 条正是与 8 月那跑 `audit_status` 的唯一差异**（69 条事实逐字相同）（这也是本次特意**从 seg7 起跑 seg8** 的目的 —— audit 属 seg8，只重跑 seg9 的话 G3 一行都不会跑）。
> **提取率实测**：69 条事实 → 主数字为空 **10** 条 → 其中正文含数字 **7** 条 → **其中数字是真承重量值的只有 1 条**（`f64`「联邦基金利率3.63%低于CPI 3.30%」·已被 G3 降 notsure）。另 6 条的「数字」是日期 / 年限（13 年来首次 / 2020 年 4 月 / 10 年期 / 60 天停火 / 2026 年 2 月），本就不该有主数字；🔴 **初版据此说「四类噪音过滤没有误伤」——两头都错**：拿来当证据的 `f17` 之所以 passed 是**水印匹配上了表①**、与噪音过滤无关；而 G3 真降的 3 条里有 **2 条**（`f11`「13 年来」/ `f23`「10 年期」）恰是「本不该有主数字」的**时长 / 期限**类 —— 四类噪音只排日期 / 裸年份 / 指数名 / 证券代码，**不含时长**。⇒ 是**多响**（方向仍安全·只降不升），不是「没误伤」。是否收窄噪音表 → 留观察。
> **读法**：本跑真漏抽 **1/69**，比归档回放的 35/139 低得多 —— 但那是**个股跑批**、数字密度高得多，**两个数不可直接对比**。⇒ **不足以关掉剩余项**，只是一个诚实的数据点；提取器本身仍未治，触发条件一字不改。`audit_passed` 4/69 = 5.8%（在 5% 下沿之上·主题型属结构性偏低）。

> **🅿️ 用户裁决 defer（2026-08-25·⚠️ 已被上方 09-09 块接走：defer 结束 —— 修法候选 B 已由 CRED.1.G3 落地合 main `e7fe42b`；本块以下为 point-in-time 记录，正文不改）**：**不急着修，先只记录**。前置核实已做（缝真实可达、但归档完成态 0 活体复现），据此 defer——**攒到一次能触发多数字 claim 的活体 e2e、确认 null 真落到 🟢，再动手**（免得据静态+归档推断给承重闸加兜底）。修法候选 A/B 见下方，动前复读本条。

> **一句话**：有一道用户 2026-08-05 拍板的闸（"改动四"）专门拦"数值 fact 引了不可比的编号就别给最高信任档"——但它的前提是那条 fact **已被 DS-0 抽出结构化 `numeric_value`**。万一 fact 正文里明明有数字、DS-0 却没抽出来（`numeric_value=None`），这道闸整个不触发，那条 fact 可能落 `audit_passed` → verified 🟢，而它引的编号其实核不了那个数字。

**实证链路**（只读调查·[audit_node.py](../../src/committee/agents/audit_node.py)）：
- 改动四在 [audit_node.py:358](../../src/committee/agents/audit_node.py:358)：`if fact.numeric_value is not None and matched and not _numeric_registered(...)` → 降 `audit_notsure`。
- **前提 `numeric_value is not None`** = 缝所在：为 None 时整条件短路，`_check_value` 也返回 None（无可比值），直接落 [:375](../../src/committee/agents/audit_node.py:375) `matched and not missing` → `audit_passed` → 🟢，且因无 `numeric_value`，散文数字门控 `gate_prose_numbers` 也不替换 → 数字原样、穿 🟢 衣服、不加保留标注。

**为什么要紧**：这正是项目最在意的错位——一个核不了的数字拿到"已核实"待遇。**与 ref 前缀无关**（不是"REF#F 就 🟢"，改动四对可比性把关是对的）；真正的破绽在 DS-0 **该抽的数字没抽成结构化值**。

**🔒 边界（别读大）**：
- **本条不是 #266 引入的**——它对任何"非可比编号"都成立（`fred/value`、`rss/count`、研报正文 blob…），是存量、更深。#266 只是**收窄了它的入口**（让空 fred 不再发 `count=0`/`series_id` 这两条可被误绑的编号），未补本体。
- 与 [`DEFECT-REVIEW-ERROR-AS-DATUM`](backlog.md) 相邻但不同：那条是"错误/空被 LLM 散文数成数据点"，本条是"结构化闸被 None 前提绕过"。

**🔵 前置核实已做（2026-08-25·[频率 observation](../observations/numeric-value-null-audit4-bypass-freq-20260825.md)）**：
- **何时漏抽**：`numeric_value` 是 DS-0 **LLM 抽的**（非正则），主导漏抽形态 = **一句话塞多个数字 / 区间**（几个并列硬数字里挑不出"主硬数字"就留 null）。**外加 prompt 心智模型 bug**（[pass0_prompt.py:96](../../src/committee/prompts/pass0_prompt.py:96)）：指令写"留 null 是 fail-safe"，而 null 对改动四**是 fail-open**——**prompt 正在主动鼓励那个会绕过闸的 null**。
- **频率**：中期快照（16 run·1028 facts）里"可达伤害集（null+数字+REF#）"= **15 条·1.5%**（且多来自对抗实验 r5-garbage，常规更低）；**但终局归档（22 完成 run）里只剩 1 条、audit_status=inconclusive、真走到 `audit_passed` 🟢 的 = 0**。原因：那些 null 又含数字的 fact 多被**别的闸**顺手兜住（只绑 W# 外部章 / 水印带限定词 / 缺引用）。
- **结论**：缝**真实、可达，但在归档完成态里潜伏（0 活体复现）** → 优先级 = **低急、值得做的 defense-in-depth**（不是在冒烟的火，但闸确实可绕、prompt 还在鼓励）。#266 已收窄一个入口（空 fred 不再发可绑 `REF#`）。
**处置方向候选**（未定·**动前仍须在能触发多数字 claim 的活体 e2e 上确认 null 真落到 🟢**）：**A（治因·最小）** 改 prompt 那句错的"fail-safe"心智模型 + 明确多数字 claim 别整条留 null；**B（兜底·治闸）** 改动四加"`numeric_value=None` 但 claim/水印视觉含数字 → 同样保守降 `audit_notsure`"，把 fail-open 翻成 fail-safe。A 治因 B 兜底可叠加。
**触发条件**〔**🔄 09-09 改口径：audit 侧那半已由 [#284](https://github.com/JunoChenZt/subagent-for-investment/pull/284) 修掉，触发条件收为剩余项**〕：下次动 DS-0 提示词 / `FactInventoryItem.numeric_value` 抽取逻辑；或 G3 上线后 e2e 看 `audit_notsure` 占比抬升时回头量提取率。~~或 e2e 首次实测到"正文含数字但 `numeric_value=None`"的 fact 拿到 🟢（= 活体复现·当前 0）~~（该判据已被 09-09 回放证伪：不是 0，是 35 条）。
**进入时点**: 2026-08-25（#266 冷审拆出·同日完成前置核实）。**预估**: 修法轻（A 改 prompt / B 加兜底判据 + 反向变异测试）。
**配额**: **DEFECT 族·不占 lettered 配额**。

---

### DEFECT-REVIEW-ERROR-AS-DATUM. 审查环节把**一条故障提示**数成"具体数据点"——"有几个数据点"这道判断认错了东西（🟡·2026-08-20 由 DEFECT-MCP-ISERROR 拆出·归档实锤）

> **📌 2026-09-10 · CRED.1.G5 簇 1 收口跑：影子试用「第 1 跑 / 地板 ≥3」·分歧 = 0（如实记零）·条目继续挂**
> 跑批 = [cred-1-g5-e2e-20260910](../observations/cred-1-g5-e2e-20260910/FINDINGS.md)（黄金·主题型·从 G7 seg7 起跑 seg8+seg9·终局质检 14 pass / 0 warn / 0 fail）。
> **抄录（零也写零）**：⑧ 段前置风控 1 条 = **G2 warning**（非影子）；⑨ 段全检 `risk_gate_findings` 1 条同为 G2，**`G1-shadow` 0 条**、闸级 `would_newly_block` 样本 **0**。基金经理逐条回应 **1/1**（G2 → `downgraded`），`risk_gate_response` 里**没有**影子条目 —— 与 #285「影子只给用户看」的设计一致，**接线按预期工作**。
> **读法不变**：上游今天已不把故障提示登记进表① ⇒ **零分歧是常态、不是检查坏了**；按 D5 裁定**三跑零分歧也不能升硬拦**（样本没覆盖）。⇒ **本条 ✋ 不 close**，试用期继续。
> **延伸项 (a)「分诊 D3 切共享认章」1.G5 顺带评估结论 = 维持「暂不做」**：其触发条件是「影子试用期看到 D3 因认不出裸写 / 小写章而漏报一次真问题」——本跑零分歧、无 D3 漏报样本，**没有新证据**，触发条件不变、不改宽严。延伸项 (b) 同理未触发。

> **📌 2026-09-09 · CRED.1.G2 影子对账已实现（用户裁 D5）· 09-10 ✅ 已合 main `163337a`（PR [#285](https://github.com/JunoChenZt/subagent-for-investment/pull/285)·2026-09-10·分支已删） —— 条目转「影子试用中」，不 close**
> **落地形态**：[risk_gate.py](../../src/committee/agents/risk_gate.py) `check_g1_shadow` —— G1 旧口径 `len(evidence_log)` **一字未动、继续驱动 high / hard_block**；同时算「排除表①登记为错误形态的条目」后的 `n_new`，任一 Strong 信心 role 两口径不一致 → 另发 `G1-shadow`（恒 warning·`details` 含 `roles[{role, n_old, n_new, would_block, excluded[{ref_id,data_key,value,claim}]}] / would_block / would_newly_block`）。识别**走引用不走文字**：只认表①登记值前缀有限集（`API request failed`·测试钉条数 1；PR #285 复审删掉 wrapper 兜底串 `<server flagged isError` —— 按构造只进 `raise MCPToolError`、到不了表①）。**复审修（#285 review）**：影子**只给用户看**（`is_shadow` 不进 fund_mgr 决策提示词 / 逐条回应 pass / 打码豁免集·`llm_facing_findings` 一处过滤）；`would_block` 是 role 级、**闸级样本 = `would_newly_block`**（旧口径 G1 已因别的 role 触发 = 非新增拦截）；trace §④ 渲染 details。
> **🔴 R5 核到 main 的事实（开工前）**：设计 pass 列的两形态（`status="no_observations"` / MCP `isError`）**在表①里今天都不可达** —— MCP 错误由 wrapper 抛异常、dispatcher 整源跳过、无 REF#；fred 空结果全键 meta、0 引用；wisburg 降级留痕进 `_meta`。能出现在表①的错误登记只有历史形态（DEFECT-MCP-ISERROR 修前）。**109 份主干归档扫描**：证据条目引用错误登记 **3 条·全在 D1-ROOT run1**；引用空值登记（`N/A`/`list(0)`/`dict(0)`）**0 条** ⇒ 空值形态**刻意不纳入**（无数据支撑放宽）。**⇒ 新鲜跑批预期零分歧**：洞被上游堵住了、不是检查失效；本识别器 = 历史归档回放的对账口径（**只认那一种措辞，不是"上游回归的第二道眼睛"** —— 回归多半换措辞，真要第二道眼睛该架在登记边界·属新检查须另登记；#285 复审收准）。D5「3 跑零分歧不能升」正为此立。
> **触发条件（试用期）**：每跑 e2e 按 [段式指南 ⑧/⑨](../observations/e2e-runs/segmented-e2e-guide.md) 抄出 `G1-shadow` 分歧（零也写零）；出现 `would_newly_block=True`（闸级）样本 → 用户逐条认定；**升硬拦** = 全部坐实零误拦 + ≥3 跑地板 → `check_g1` 加 `ref_lookup` 参数改用 `_count_evidence_excluding_errors`（非一行·清单见 risk_gate.py 注释块 ①–⑤）→ 届时处置本条。
> ⚠️ **2026-09-10 订正**：上句原写「届时本条**随簇 1 收口**处置」—— **簇 1 收口（1.G5）已于 2026-09-10 完成、本条未达地板（第 1/3 跑）故继续开着**，那个时点已经过去。**下次处置时点** = 试用跑数攒到 ≥3 且分歧全部人工坐实，或簇 2 收口时一并裁。
> **📌 #285 复审延伸两项 · 用户裁「暂不做」（2026-09-10）—— 本处是唯一去处（§2.11.9），别处只指过来**
> **(a) 分诊 D3 切到共享认章实现** —— 现状：[rules_d.py](../../src/committee/triage/rules_d.py) `_REF_PATTERN` 只认带方括号 + 大写的 `[REF#X-NNN]`，而 [stamp_families.py](../../src/committee/facts/stamp_families.py) `structured_refs_in`（影子对账在用）认大小写漂移 / 裸写 / 拼接串；同一条证据两边结论可能不一致（`[ref#w-003]` 影子认、D3 不认）。**暂不做的原因**：切过去 D3 会多报一批「引用了未知编号」——不是质量变差、是它以前看漏了，但**报警面变大**按 [验收标准 §4](e2e-acceptance-standard.md) 属新检查面、须先 WARN 试用再升；不切没有坏处，只是两边宽严不一。**触发条件**：影子试用期看到 D3 因「认不出裸写 / 小写章」而漏报一次真问题 → 立 WARN 试用；或簇 1 收口 1.G5 时顺带评估。
> **(b) 在数据登记边界加「错误文本不得当数据点」关卡** —— 现状：本条目的识别器只认历史归档那一句措辞（`API request failed`），上游回归换措辞就认不出；今天不出事是因为上游更早一步（wrapper 抛 `MCPToolError` + watermark 跳 `_META_KEYS`）已把报错拦在表①外。真正靠谱的防线该架在 [watermark.py](../../src/committee/common_context/watermark.py) `generate_watermarks` 登记那一刻（形态断言 / `Reference` 级状态位）。**暂不做的原因**：这是一道**全新**检查、影响所有数据源入库，须先登记 + WARN 试用；而洞今天已被上游堵住、影子试用尚未跑出一个样本，先看数据再定。**触发条件**：影子试用期出现一次「新措辞的错误文本被登记进表①」（识别器没认出、人工发现）→ 立即立项；或 DEFECT-MCP-ISERROR 同族再复发一次。

> **📌 为什么单独成条**：这是 `DEFECT-MCP-ISERROR` 原条目**自己写下的裁定**——"审查环节把错误码算作'具体数据点'
> 这一条**独立成立，不随之关闭**"。那条已于 2026-08-20 close-by-completion，本条按其裁定**原样拆出继续挂**，
> 不是新发现。（照 R7 ③「连带项一并处理」：状态切换时被点名的连带项必须显式接住，不能跟着母条目一起消失。）

**一句话**：审查在数"证据里有几个具体数据点"时，把**"某某源报了 503"**也数了进去 ——
它是一条"我们没拿到数据"的记录，却被计成了"我们拿到了一个数据"。

**归档实锤**（[D1-ROOT-e2e run1 trace](../observations/D1-ROOT-e2e/run1-micron-resume/seg9-decision.trace.md)，origin/main tracked）：
`"Evidence log includes concrete data points: yfinance price ($1032.28), rss headline text, and wisburg API error code (503)."`
—— 前两项是真数据，第三项是故障提示。三项并列计入同一个"够不够扎实"的判断。

**🔑 为什么修好上游≠修好本条**：`DEFECT-MCP-ISERROR` 修完后，**那个具体实例不会再发生**
（错误文本压根到不了引用清单）。但本条问的是另一件事：**审查这道判断，凭什么认定一段文字算"一个数据点"？**
今天它似乎只看"这段文字里有没有一个像数字/代码的东西"。上游堵住的是**一个**灌进错误文本的口子，
不是**这道判断本身的判据**——换个源、换条路径灌进来同类文字，它照样会数进去。
⇒ 这是「判别力方向」问题，与[数字出处收官档](number-provenance-endgame.md)记的那两条同族新形态相邻，
**本条只登记本域实例，不接那条线**。

**触发条件**: 下次动审查/评估那道"证据扎实度"判断时；或再出现一次"非数据被计成数据点"。
**反向条件（close 不做）**: 若核实该处措辞只是**自然语言复述**、下游没有任何东西真的按"数据点个数"分档
（即它不承重）→ 降 🟢 并改记为表述问题。⚠️ **动手前须先核这一条**（R5）：本条目前**只有一个实例，
未核该判断是否真承重**，不得据此直接改判据。
**进入时点**: 2026-08-20（由 DEFECT-MCP-ISERROR 拆出；原始发现同日）。**预估**: 先做承重核实（轻），再谈修法。
**配额**: **DEFECT 族·不占 lettered 配额**（照 DEFECT-MCP-ISERROR 先例）。

---

### BR. 「问题 → 拉什么」的映射表**覆盖不全就静默走默认值**、且**零告警**（🟡·2026-08-18 seg1 提示词检阅实测切出）

> **📍 2026-08-21 由 §0.2 轻条目提为正文条目**：给本条补记 G2 结果时，备注格涨到 1264 字、
> 撞上 `lint_backlog` 的「轻条目超长」闸（上限 1000）—— 按闸门指引拆出本节。
> **内容为原行原文 + 08-21 新增，无删减。**〔与 BS 同一形态，那条 08-20 刚走过同一条路。〕

- **强度**: 🟡（影响质量·**失败形态是"它连自己问错了都不知道"**）
- **触发条件**: **全事件型** —— 下次动 [`_SERIES_KEYWORDS`](../../src/committee/common_context/sources/fred_source.py)；或 e2e 再出现一次「答非所问的宏观数据进了引用清单」；或用户明确要求。

**实例①（已实证·2026-08-18）**

FRED 关键词表 13 个词全是宏观指标（cpi / 失业 / gdp / 利率…），**没有黄金·原油·汇率·任何商品**
⇒ 问「黄金会怎么走」撞不上任何词，**静默落默认 `CPIAUCSL`**，拿回美国 CPI 指数 `332.813` 写进引用清单。
**数据合法·有时间戳·格式完好·无一句日志** —— 它连「问错了」都不知道。

⚠️ **立账当天曾记「实例②」，同日核代码证伪 → 已撤**（见 §0.2 banner 栈 2026-08-18 第五笔）：
原写「#244 新加的 `confidence` 三档刻度不覆盖主题型 query」，而该刻度在**同一个 PR 的第二个 commit（冷审收口）已换轴**
为「归类把握」——主题型明确落在 `0.9–1.0` 档的字面里，同句重跑 0.9 → 0.95 已验。
⇒ **本条为单实例条目**；「枚举表 + 默认兜底 + 没有『我不知道』这个状态」是对**这一处**的形态描述，
**不是从两个样本归纳出的规律**（守同日冷审「别拿凑出来的样本量撑结论」）。

**🔒 三条边界别混**

- 与 **BQ** 不同：BQ = 该拉的腿没激活；本条 = 腿激活了但拉错东西
- 与 **DEFECT-FRED-SUBSTRING** 不同：那条是子串**误命中**（「毛利率」→「利率」）；本条是表里**压根没有这个域**
- 与已 close 的 **DEFECT-FRED-KEYWORD** 不同：那条修「广告的拼写表里不认」，本条是「整类资产没进过表」

**为什么当初延后**: 加词只治标，真正要定的是**撞不上时该怎么办**（拉默认值 / 不拉 / 告警降置信度）—— 属取数语义决策，须用户裁。
代码注释自己写着 TODO「扩 query→series 映射或接 FRED 搜索端点」= **已知未完成非疏漏**。

> 🔵 **2026-08-21 更新：那个"须用户裁"的问题已经有答案了，实例① 的「静默」那半随之修掉**
>
> seg1 **G2** 落地（节点 [4.7.5 RP](../roadmap/S2.md)·分支 `auto/retrieval-planner`）：
> **认不出且取数计划没点名 → 明确失败**（`_resolve_series` 返回 `None` → 源 raise → 调度器降级 → 产物留痕），
> 即上面三选一里的 **「不拉 + 明确失败」**。守护测试 + **五个反向变异**钉住（把修法退回落 CPI，测试当场红）。
> ⇒ 条目标题里那句「**静默**走默认值」**对 FRED 这一处已不成立**。
>
> **🔴 但本条不得据 G2 关闭 —— 没解决的那半**：**那张表拆不拆**没动。
> 它是 [`_route`](../../src/committee/common_context/builder.py) 宏观安全网的唯一判据（经 `has_macro_keyword`），
> 删键 = 悄悄改路由行为，正撞 G2 自己的停止条件「触到宏观安全网行为变化 → 先补测再继续」。
> ⇒ **表的去留随安全网一起归 G5**（安全网撤除已由用户 2026-08-21 裁定），本条的反向条件届时再判。

**进入时点**: 2026-08-18。**预估**: 定语义 + 落地 半天。**配额**: 占 1 个 lettered slot。

---

### BS. 引用清单把**三类信息混成一类** —— 答非所问的 / 当背景的 / 真对题的，下游分不出谁是谁（🟡·2026-08-18 seg1 外部信息质量实测切出）

> **✅ CLOSED 2026-09-24（close-by-completion·CRED.2.G5·用户当日裁·保留位置）** —— 身份字段已落（#317）；全链 e2e 全链贯通、零误标。⚠️ 本跑**无噪音可标**，「填充噪音不得标对题」一面按 2.G4 回放 + 单测认定（[FINDINGS](../observations/cred-2-g5-e2e-20260923/FINDINGS.md) §3.4）。重开条件见 §0.2 本行。以下为关闭前原文，不再改动。

> **📍 2026-08-20 由 §0.2 轻条目提为正文条目**：原整条挤在状态表一行里（备注格 989 字、离闸门上限只剩 11），
> 新事实一进就撞 `lint_backlog` 的「轻条目超长」闸 —— 按闸门指引拆出本节。**内容为原行原文 + 08-20 订正，无删减。**

- **强度**: 🟡（影响质量·**信号混杂**——不是数据错，是三类信号在清单上长得一模一样）
- **触发条件**: **全事件型** —— 下次动 [watermark](../../src/committee/common_context/watermark.py) / references 装配 / [rss_source](../../src/committee/common_context/sources/rss_source.py) feed 列表 / wisburg 取数；或 e2e 出现一次「分析师拿无关引用当依据」；或用户明确要求。

**实测（2026-08-18 黄金跑·31 条外部信息逐条读过）**

⚠️ **口径先写清**：31 = **信息条目数**（1 指标 + 10 条头条 + 20 篇研报标题），与引用清单 **7 条不是一个数**（守 08-18 冷审「104 条 ≠ 26 个独立观测」教训）。⚠️ **7 的构成只核到 3**（宏观占 3·余 4 未核）⇒ **不靠构成立论**。

**实测相关率 32%（10/31）** —— ⚠️ **判定标准先写下来才可复算：相关 = 标题主语是金价 / 贵金属本身**。

| 源 | 条数 | 相关 | 说明 |
|---|---|---|---|
| 宏观 | 1 | **0** | 答非所问的 CPI（见 BR） |
| 新闻 | 10 | **0** | 医保补贴 / Roth 转换 / 卖房避税等理财问答与通用头条 |
| 研报 | 20 | **10** | 另 10 条讲「名字里有黄金的股票」，其中 **7 篇同一家珠宝公司** |

⚠️ 新闻那 10 条里「国债 ETF 跌至 2004 年以来最低」按上述标准判无关，但实际利率是金价核心驱动、**此条可争议**；改判则为 11/31 = **35%**。
⚠️ 研报里含 **ID 不同、日期相邻、标题高度雷同**的两条老铺黄金二季度点评（`[98409]` 07-31 / `[98756]` 08-01）—— **是否同一份报告的两个版本未经证实**，标题实差 3 字。

**三种源三种提问方式**：新闻**根本不带 query**（写死订阅源）· 宏观**关键词撞表**（撞不上落默认·见 BR）· 研报**唯一把 query 传出去**。
⇒ 到分析师眼里全是「7 条引用」，**没有任何标记区分针对性 / 背景 / 无关**。

**🔒 不是说这些源没用**：新闻拉通用市场背景**可能本就是设计意图** —— 但**代码里没有一句话说明这个定位**，故「背景」与「答非所问」在清单上长得一模一样。

> 🔁 **2026-08-20 事实订正（论据换人·结论不变）**：原文把这个"设计意图"归在「谷歌那条订阅源写死搜 `financial markets`」上，**归错了**。
> 两个 feed 是**按顺序取、取满 10 条即 break**（[rss_source.py:141](../../src/committee/common_context/sources/rss_source.py)），MarketWatch 排第一且一次给够 10 条
> ⇒ **谷歌腿在正常路径下从未被执行**（已对 [rss_A_today.json](../observations/source-shapes-20260819/raw/rss_A_today.json) 核实：10 条全 MarketWatch，零条谷歌）。
> ⇒ 本条实测的「新闻 10 条 0 相关」**全部来自 MarketWatch**，与那个写死的查询词无关；而 MarketWatch 是**纯订阅源、结构上就不认查询词**，
> 故"通用背景是有意为之"这个假设**反而更站得住**（只是仍无代码佐证）。
> ⚠️ **连带**：修法若只给新闻腿接查询词而**不动那个 break，接了也永远轮不到** —— 已写进 [seg1 设计 pass](../plans/seg1-取数计划-设计pass-2026-08-19.md) 的 G3 前置。

**修法方向**（✅ 2026-09-23 已裁·见下块）: 给 reference 标「针对本问题 / 通用背景」两档，或按源声明意图；**别急着删源**（删掉通用背景可能减少下游视野）。

> **📌 2026-09-23 · D2 已裁（用户）= 加字段**：`Reference` 增 `relevance: Literal["on_topic","context","off_topic",""]`（默认空 = 旧归档回放落「未标注」），由回核层按 intent 结果填（**只打在回核后的条目上**·防给填充噪音盖「对题」章）；watermark 渲染分组 / 表③展示列同步；验收 = 五处处理器逐核（watermark 渲染 / audit ref_lookup / references_appendix 装配 / archive 序列化 / trace 报告）+ 110 份旧断点回放零崩 + 真跑填充噪音**不得**标 on_topic。落 [CRED 2.G4](../roadmap/S2.md)（合并顺序在 2.G0–2.G3 后·簇 2 拆解同日放行）。「只渲染层」备选**弃**（下游拿不到就等于没标）。本条 close 随 2.G4 / 2.G5 再议，**判据不变**。
>
> **📌 2026-09-23 · CRED.2.G4 已合 main（#317 `75fa362`）**：身份按**回核后定位**填（primary → 针对本问题 / background → 通用背景 / 其余留空）；新闻混进通用头条 → 整条背景；表③ DS-0 事实行保守继承（全对题才对题）；分析师出处段加标、未标注一字不变。**实现前查出并顺带修掉一个漏**：回核筛掉的研报此前只从结构化记录删，分析师读的正文仍是全量 ⇒ 主干 9 条研报腿共 **29 篇**不相关研报照样进了上下文；现按留下的重建（用户裁：先修；无关研报继续删、不标 `off_topic`）。**条目待 2.G5 真跑佐证后 close**。
**连带**: 研报只取标题不读正文另见 **BI**；智堡本次只取第一页 20 条（返回带下一页游标）。
**本方案覆盖度**: seg1 取数改造**解决一半**（计划自带意图标注）—— ⚠️ 前提是标注打在**回核后**的条目上，否则研报格会给填充噪音盖「对题」章；清单侧渲染仍需单独做。
**进入时点**: 2026-08-18。**预估**: 设计半天 + 实现 1 天。**配额**: 占 1 个 lettered slot。

### DEFECT-ANCHOR-FALSEPOS-HARDBLOCK. 出处绑错**第一次改变了决策产出** —— 一条正确的断言触发灾难指纹硬拦，BUY 被压成 HOLD、执行计划整个被切（🟡·2026-08-27 G7 全链跑实锤）

> **📌 2026-09-10 · CRED.1.G5 簇 1 收口：✋ 用户裁「再留一轮」·本条 continue open**
> 本条是簇 1 四条里**唯一够格按完成关闭**的（核心缺陷已修 + 两种方式验过 + 自记的两个触发条件 (A)(B) 均已兑现）。收口时把关 / 不关两个选法摆给用户，**用户裁「再留一轮」**。
> **不关的理由（用户采纳）**：本条正文挂着的剩余项 **f16 类「推算比值挂原始计数编号」规则层不治、生产上靠异模型复核员接住** —— 那是**会出错的模型判断、不是机制保证**；而新加的 Q8 可见性检查**刚上 WARN 试用、还没证明「它回来了一定看得见」**。一关，剩余项就没有活条目盯着。
> **下次评估时点**：① 复核员攒到第一个**自然真阳性**样本（届时必须回看它当时判了什么）；或 ② 簇 2 收口时一并裁；或 ③ Q8 试用期结束。
> **本跑证据**（[cred-1-g5-e2e-20260910](../observations/cred-1-g5-e2e-20260910/FINDINGS.md)）：check① **全程未响**（69 条事实零质量标记 / 无硬拦 / 无存疑标 / Q8 判 `quiet`），复核员**调用 0 次**。⚠️ **check① 未响 ≠ 判别力被验证** —— 本跑压根没有触发条件；判别力的受控证据在靶测归档回放与真模型两向冒烟，不在这一跑。

> **📌 2026-09-10 · D4 已裁 · 实现 ✅ 已合 main `0e297ef`（PR [#286](https://github.com/JunoChenZt/subagent-for-investment/pull/286)·分支已删）·条目仍不 close（随 1.G5）** —— **D4-a = B**（② 年份免检〔实现时补**价格守卫**：紧贴货币 / 单位 / 价格词的 1900–2100 不算年份·`2010 元` 照比〕+ ⑤ 百分比↔小数 100× 归一 + ⑥ 单位缩写免检〔紧贴数字 + lookaround·`B2B`/`M2`/`SpaceX` 不算〕+ ⑦ 三元组可见性）；**D4-b 用户改裁为「规则直接上 + 异模型复核员」**（不是本条 09-09 块列的「直接上 / 影子告警」二选一）：机械判搬运错后叫与 pass0 / 决策 / 分析师**不同 provider 家族**的模型（默认 gemini-2.5-pro）复核，判 `false_positive` → **撤硬拦、`execution_plan` 保留、`FinalDecision.execution_plan_caveat` 打「存疑」标**；`unsure` / `true_error` / 调用失败 / 不独立 / kill-switch 关 → 维持硬拦。🔴 **用户显式裁定的「只降不升」红线例外**，三前提焊在代码（独立性 / 输入隔离 / 输出封闭），撤到「存疑」档为止、无干净放行路。**真模型冒烟**：5 条历史误报（含 f16 推算比值）全判误报 + 3 条合成真抄错全判真错 = **8/8 两向**，记录已归档 [cred-1-g4-review-smoke-20260910](../observations/cred-1-g4-review-smoke-20260910/FINDINGS.md)；⚠️ 自然真阳性样本仍 0、复核员在自然真错上的表现**未被测过**。**Q8 可见性 WARN 试用**。设计 [CRED-1.G4 §6](../plans/CRED-1.G4-绑错判别力-设计pass-2026-09-09.md)。
> **⚠️ 合并前 review 坐实 10 条·全部当场修**（[§6.4b](../plans/CRED-1.G4-绑错判别力-设计pass-2026-09-09.md)）——**三条要害都是「红线例外的防线在真实配置下是空的」**：① 独立性守卫比的是 `ANALYST_MODEL` / `DECISION_MODEL` 等 **tier 兜底常量**，而线上每角色走 `model_for_role` 单独配（`.env` 里 `COMMITTEE_MODEL_BEAR=gemini-2.5-pro` 是未注释实配）⇒ 会在「gemini 复核 gemini 自己写的数字」时判独立；② `oc/<model>` 自成一族 ⇒ 同一模型换写法骗过守卫；③ 提示词范例恰是「撤硬拦」那一档 + 解析取第一个 JSON ⇒ 模型复述格式即撤拦（**已实测复现**）。其余七条：新事件类型未进流式白名单 / 年份守卫拿整句 search（**让本条要治的 G7 误报复活**）/ 单位缩写误吃 `5 M&A`·漏抓 `1.6T` / 百分比归一只看形状不看证据（`0.03 ↔ 3` 真错被静默放过）/ 同步调用卡 async 事件循环 + 无条数上限 + `attempts` 语义写反 / 异常被写成「未配置复核员」/ 收口四项（冒烟未归档·状态图标未挪·字段表漏字段·commit 正文乱码）。**§2.11.9：坐实 10 = 修 10 + 记账 0 + 不做 0**。**条目不在 G4 关** —— 随 1.G5 簇 1 收口统一处置（段式 e2e 佐证 + close）。**剩余项 f16 类**：规则层仍机械判搬运错、生产上由复核员承接（冒烟判对）；候选 ③ 分析师侧程序校验仍留账。
> **📌 2026-09-09 · 设计 pass 已出、等用户裁 D4** —— 排入 [S2 §4.7.6 CRED.1.G4](../roadmap/S2.md)，设计 pass = [CRED-1.G4](../plans/CRED-1.G4-绑错判别力-设计pass-2026-09-09.md)（用户裁「提前起」）。
> **一手数据（268 份主干归档探针·册从同跑分段断点解析）**：check① 共 **9 响**（去重）→ 硬拦路 **5 响 5 误报 0 真错**（年份 1 / 百分比↔小数 2 / 单位缩写 k 1 / 推算比值绑原始计数 1）；软报路 4 响（年份 2 / 同句他数 2）。**EXEC-FLOOR 历史硬拦仅本条 G7 一次**（其余 4 跑硬拦是 OBEY-5）⇒ **该硬拦路历史真阳性 = 0**。外源册登记值年份形态 26.4%。
> **下方四候选的实测判定**：① 源头不记年份 **❌ 不做**（波及 26% 登记、且册被印证计数复用·排爆炸半径）· ② 年份免检 **✅ 做** · ③ 分析师侧程序校验 **⏭️ 留账另立**（G6 已证嘱咐无效、"推算"无可判形态）· ④ 只观察 **❌**（等于让一条 5/5 误报的硬拦路继续活）。**新增** ⑤ 百分比↔小数 100× 归一 · ⑥ 量纲词表补 k/M/B/x/倍 · ⑦ 理由印 `(fact 值, 登记值, context)` 三元组 + gate WARN 行。**推荐 B = ②⑤⑥⑦**；方向自检 = 只拒绝比不可比的、不加任何「猜绑错→放行」路、真阳性守护反向测试。
> **剩余项（本条不 close 前不丢）**：f16 类「推算比值挂了原始计数的编号」（2.75:1 ↔ 192,128 份合约）—— 不是不可比、是分析师侧绑错，本次不治；触发 = 下次动分析师 common_output 提示词 / 再出现一次推算绑定 fire。

- **强度**: 🟡（**方向保守侧** —— 买变观望不放行风险，**不是安全洞**；但它是实打实的误伤：断言本身正确，执行计划却没了。危害面从此前已知的「披露问题」升级为「改变产出」——**本域首次观察到**）
- **一句话**: 政治分析师写「2026 年 11 月中期选举**距今约 3 个月**」并挂上出处编号，而那个编号登记的值是原句里的**年份 2026**；核对器一比 3 ↔ 2026 差数量级 → 判「证据搬运错」→ EXEC-FLOOR 硬拦。
- **根因链（四环·每环都核过一手材料）**:
  1. **盖章机器见数字就盖，连年份都登记成数值**（外源册里 `W#political-25-4#n1` = `2026.0`，context 就是 "…the 2026 midterm election…"）—— 垃圾编号的存在是前提；
  2. **分析师提示词有规矩但只是嘱咐**（[common_output.py:38](../../src/committee/prompts/analyst/common_output.py)：「推算数字不带任何编号标记」）—— 政治分析师违反了，无程序把关；
  3. **下游无条件信任编号**：事实整理按「带 W# = 网上抄录」归类（[pass0_prompt.py:76](../../src/committee/prompts/pass0_prompt.py)），一路照抄成 `f60`（`source_type=retrieved_from_web`·`numeric_value=3.0`）；
  4. **check① 的默认假设是"编号指向的就是这个数"**：三道 fail-safe（单水印/查得到号/无量纲词）防的全是量纲歧义，**没防"绑到别的数上"** —— 三关全过、照拦。
- **触发条件**（事件型）: (A) 下次任何一跑 EXEC-FLOOR fire 时，**先核触发 fact 的绑定真伪再认定"搬运错"**（撞上即评估本条）；(B) 下次动 [exec_floor.py](../../src/committee/facts/exec_floor.py) check① / 盖章机器（number_registry 登记逻辑）时。
- **任务**（候选·不预设）: ① 盖章机器跳过年份/日期形态的数字（治环 1·最窄）；② check① 对「登记值为年份形态」加免检档（治环 4·镜像既有量纲免检）；③ 分析师侧对"推算数字挂编号"加程序校验（治环 2·最重）；④ 仅持续观察。**任何一条都动承重机制，须用户裁**；新检查按 [验收标准 §4](e2e-acceptance-standard.md) WARN 试用。
- **为什么延后**: N=1；方向保守侧无资金风险；候选修法均属承重变更。
- **交叉**: 现象已记 [endgame G6/G8](number-provenance-endgame.md)（该域已封卷·明写"要治须重新立项"——**本条即立项**）；与已 CLOSED 的 DEFECT-ANCHOR-MISBIND 同族但形态新（彼=披露错绑·此=误伤决策）。完整证据 [G7 FINDINGS §十五](../observations/rp-g7-e2e-20260827/FINDINGS.md)。
- **进入时点**: 2026-08-27。**预估**: 候选①② 各半天；候选③ 1-2 天。**配额**: DEFECT 族不占 lettered。

### DEFECT-DEBATE-STALE-PRIOR. 辩论第一轮**设计性断粮** → 模型拿训练期的旧行情充当今天的数据，且无任何闸门看得见（🟡·2026-08-27 G7 全链跑实锤）

> **✅ CLOSED 2026-09-24（close-by-completion·CRED.3.G2·用户当日裁·保留位置）** —— 检测上线、实跑该响的响（[3.G2 FINDINGS](../observations/cred-3-g2-e2e-20260924/FINDINGS.md)）；下方「任务」①② 两条改提示词候选已挪至 [endgame §4 G8](number-provenance-endgame.md)。以下为关闭前原文，不再改动。

- **强度**: 🟡（污染辩论输入面；本跑被对手当场抓住未成害，**但对手不是防线** —— 双方同向或对手没留神就一路走到终局）
- **一句话**: 第一轮辩论提示词明写「**没有原始数据参考**」（防串供的有意隔离），被断粮的空头从自己训练期的记忆里取数 —— 「DXY 维持 105 以上」「短期国库券约 5%」恰是一两年前的真实行情，与**同一跑**取到的数据（DXY 99.1 / 政策利率 3.63%）直接矛盾。
- **连带发现（同文件同根）**: 三轮正文的出处章有无**是提示词的精确镜像**（[debate/prompts.py](../../src/committee/prompts/debate/prompts.py)）：R1 无数据可引 → 0/0；R2 写"可引用" → 9/9；R3 **只字未提出处** → 0/3（多头收官带着具体数值零出处，而收官正是喂给投票与决策的最终版本）。⇒ 「时有时无」不是模型随机，是规则不对称。
- **触发条件**（事件型）: (A) 下次动辩论提示词时一并评估；(B) 再出现一次「辩论正文数值与本跑已取数据冲突」（与 [endgame G8](number-provenance-endgame.md) 触发① 同源·届时两处并读、合并计数）。
- **任务**（候选·不预设）: ① R1 提示词加一句「不得使用记忆中的行情数字；缺数据就做定性论证」（**不拆隔离墙** —— 隔离是有意设计，Chesterton）；② R3 提示词补出处要求（对齐 R2）；③ 接受现状仅记录。
- **为什么延后**: 动提示词 = 行为变更；R1 隔离墙的设计意图须先议（拆墙前读当年立墙的理由）。
- **进入时点**: 2026-08-27。**预估**: ①② 各改一句 + 一次段级复跑验证，合计半天。**配额**: DEFECT 族不占 lettered。

### DEFECT-GATE-NA-AS-PASS. 终局质检把「没查到」印成 PASS —— 执行计划被硬闸切除时，价位两项自动绿、理由还写错（🟡·2026-08-27 G7 全链跑实锤）

> **✅ 2026-09-09 CLOSED（close-by-completion·CRED.1.G1）** —— PR [#283](https://github.com/JunoChenZt/subagent-for-investment/pull/283) 已合 main `fb6dcee`。
> **下方「任务」两条均已落地**：① 理由不再印 "acceptable for HOLD"，改 `N/A` 档 + 四成因区分（`no_plan` / `cut_by_gate` / `price_unavailable` / `empty_entry`）—— 且**判到数字层**（计划对象在、买入价为空同样 N/A：主干 75 份探针里这一档 **45 份 = 空过大头**）；② `summary_line` 固定四段，n/a 单独计数、**永不并进 pass**，报告上看得见「这项没验过」。
> **承重边界守住**：N/A 既非 FAIL 亦非 WARN → `overall` 与 cli exit code 不变。**53 份在册归档回放实测**：仅 Q3 PASS→N/A 38 · Q4 PASS→N/A 25，**整体判定变化 0 份**。
> ⚠️ **合并前 review 坐实一个真 bug 并已修**：三处判「有没有买入价」写的是真假值判断，把 `0` / `0.0` 读成「没填」——而 `0` 正是 Q3 placeholder 档要抓的占位符。在册 `_archives/run-pr8a-q6_stagflation-commodity-tips-cash.json`（note 自陈「设为 0 占位」）因此 **FAIL→N/A、整份 overall FAIL→WARN、cli exit 1→0** —— 与登记承诺的「fail 面零变化」正好相反。修法 = 抽 `_entry_has_price_numbers` 判 `is None`，Q3/Q4/成因判定三处共用。**第二层教训**：初版守护用的夹具是 `{0.0, 1.0}` —— `1.0` 是真值、照旧绿，**守护挑了个还能过的形态 = 没有守护**（沉淀见 [[none-vs-truthiness-numeric-gate]] memory）。
> **剩余**：无。Q5「只量一条管道」那半**不在本条**（见下方「连带」），仍由 CRED 簇 2/3 各自条目承。

- **强度**: 🟡（不产生错误决策，但产生**误导性的全绿报告** —— 与已有 DEFECT-REVIEW-ERROR-AS-DATUM 同族：审查环节自己认错东西）
- **一句话**: 本跑终局 gate 13/0/0 全绿，但 Q3（入场价合理性）/ Q4（止损合理性）判 `n/a` 的理由印的是 "no execution_plan (**acceptable for HOLD**)" —— 而事实是**基金经理填了计划、被 EXEC-FLOOR 切掉的**；「没填」与「被切」在报告上不可区分（guide ⑨ 段三态早已区分这两件事，gate 没跟上）。
- **连带**: Q5 报「0/16 misattributed (0%)」量的是 EVID-1/`external_knowledge_refs` 一条管道（[e2e_quality_gate.py](../../src/committee/e2e_quality_gate.py) 已核实现），**不覆盖 fact→外源册那条链路** —— 同一跑里真实存在的锚绑错（见 DEFECT-ANCHOR-FALSEPOS-HARDBLOCK）在「0% 错绑」的字面下不可见。检查本身没错，**是汇总呈现让"全绿"读起来像全覆盖**。
- **触发条件**（事件型）: 下次动 [e2e_quality_gate.py](../../src/committee/e2e_quality_gate.py) 时一并。
- **任务**: ① Q3/Q4 在 `hard_block_reason` 非空时把理由改印「计划被闸门切除·非无计划」（照 guide ⑨ 段三态口径）；② 报告尾加一行「本跑 n/a / 未覆盖项」汇总，让盲区显式可见。**呈现改动、不新增检查、fail 面零变化**；仍按 [验收标准](e2e-acceptance-standard.md) 登记。
- **为什么延后**: 非阻断；改呈现要顺带过一遍 19 份历史归档回放验证，单独成活。
- **进入时点**: 2026-08-27。**预估**: 半天（含历史归档回放）。**配额**: DEFECT 族不占 lettered。

### BT. triage 的「打回能力」该盘点了 —— 唯一真打回过的规则 6 月被有意拔掉，8 月起连续 4 跑全员通过（🟡·2026-08-27 G7 全链跑排查切出）

- **强度**: 🟡（审核环节还在跑、规则还在开火挂 flag；问的是**它还剩多少真正拦得住东西的牙齿**）
- **事实链（已核一手·非推断）**: ① 历史 8 跑里非 pass 共 4 次，唯一一次真 reject（06-16 macro 缺 scenarios）的触发规则 **B3 已于 06-24 [#156](https://github.com/JunoChenZt/subagent-for-investment/pull/156) 有意移除**（当时判定误伤源·决定正当·**但对"审核剩多少打回能力"的影响无人盘点**）；② 其余非 pass 全是 C 类 LLM 冷审（主观判断·历史仅对 technical 响过两次、均在个股跑）；③ 规则文件 **07-24 后零改动** ⇒ 8 月起连续 4 跑 8/8 全过**不是规则被改松**，是"牙被拔了一颗 + 剩下的响不响看缘分 + 题型换了"。
- **触发条件**（事件型）: (A) 下次 seg3 出现 8/8 全过（= 连续第 5 次）时；(B) 下次动 [src/committee/triage/](../../src/committee/triage/) 任何规则时。
- **任务**: 用历史 tracked 归档统计**每条规则族的真实开火/打回次数**，回答「B3 拔掉后还剩哪些规则拦得住真问题」；据此裁要不要补牙（补 = 提高 fail 面·须用户裁 + WARN 试用）。
- **为什么延后**: 4 个样本分不出"报告变好了"还是"审得松了"；盘点要等下一个数据点更有判别力。
- **进入时点**: 2026-08-27（G7 第③段排查·[FINDINGS §九](../observations/rp-g7-e2e-20260827/FINDINGS.md)）。**预估**: 统计脚本 + 盘点半天。**配额**: 占 1 个 lettered slot（**用户 2026-08-27 授权破例**）。

### BU. 「裁决 / 立账」落地没有回填义务 —— 真值源静默滞后，72 小时内在两处独立撞见同一形态（🟡·2026-08-27 G7 全链跑排查切出）

- **强度**: 🟡（不损坏数据，但让照真值源办事的人**白查、误判**，且形态在复发）
- **四例（全部当场手工补·⚠️ 例③④ 发生在「已证明手工可行」之后）**:
  1. **08-18 分类 token 线裁决**（线不动·越线属预期）只活在 [#244](https://github.com/JunoChenZt/subagent-for-investment/pull/244) 提交记录里，guide 没回填 → 08-27 照 guide 跑批的人把预期值当异常，白查一轮 + 得出与事实相反的结论（已于 08-27 补进 guide 💰 块）；
  2. **BN 条目 08-14 已按 N=3 立账**，而 guide ⑦ 段观察点至今仍写「再出现一次（N≥3）→ 提立条目」→ 08-27 跑批照旧文本数 N，得出「计数仍停在 2」的**错误结论**（本笔顺手回填 guide + FINDINGS 加订正）。
  3. / 4. **2026-09-04 两例** —— 详见下方「📌 2026-09-04 数据点」块（指南指着已关闭条目 / 登记项 ① 超时数字废弃一周）。
- **与 [R7](../../CLAUDE.md) 的关系（规则接缝·非执行疏忽）**: R7 管「状态切换」四步收口，但「阈值裁决 / 条目立账」**没被当作触发 R7 的事件类别** —— 同 #226 撞 Q6 那次一样，是规则边界问题。
- **触发条件**（事件型）: (A) 下次做任何「线不动 / 立账 / 降档 / 观察点转正」类裁决落地时，按本条先列「要回填哪些真值源文件」清单再收口；~~(B) 下次动 [workflow 收口文档](workflow/06-dod-and-evidence.md)时把该清单要求机制化进去。~~ **✅ 2026-09-04 已兑现**（见下方 ✅ 块）；**(A) 不再是"事件型待办"，已转为常驻要求** —— 每次裁决落地照 [§2.9.4](workflow/06-dod-and-evidence.md) 的 8 格名单走。
- **任务**: 把「裁决落地必须显式点名回填文件清单（guide / 判据表 / 观察点 / MEMORY）」写进收口步骤；可选：给 lint_backlog 加"立账日期晚于 guide 引用文本日期"一类的粗检。
- ~~**为什么延后**: 机制化动 governance 文档须整体设计；本次两例已手工补，急迫性降。~~ 〔**2026-09-04 已不适用** —— 例④ 证明"手工照做"那次也会漏，急迫性回升；机制化已落地为 [§2.9.4](workflow/06-dod-and-evidence.md)，见下方 ✅ 块〕
- **📌 2026-08-31 数据点（正面·手工照做有效）**: 出计划预算线 40s 裁决落地时**按本条先列了回填清单再收口** ——
  四处（[S2 §4.7.5 预算线块](../roadmap/S2.md) / [00-retrieval 第 8 条](../pipeline/00-retrieval.md) /
  [O-PLANNER-LATENCY-01](../observations/should_update_observations.md) / [实测归档](../observations/rp-g8-planner-latency-20260828/FINDINGS.md)）
  全部同步，且历史归档（08-25 冒烟 / 08-27 G7 的 FINDINGS）按 point-in-time 保留不动。
  ⇒ **本条的「任务」在人工层面已被证明可行，缺的仍是机制化**（无人做时没有任何东西会响）。
- **📌 2026-09-04 数据点（两负一正·计数升到 4 踩 + 2 次手工演练）**:
  - **例③（负）**：[段式跑指南](../observations/e2e-runs/segmented-e2e-guide.md)里的指路仍指着**已关闭的条目** —— 裁决落地时没回填指南。
  - **例④（负）**：`DEFECT-CTX-BAG-SHAPE` 登记项 ① 的正文写着**已废弃的超时数字**（15s/16s 封顶），
    而 40s 预算线 2026-08-31 就已落地 ⇒ 条目正文整整拖了一周没跟上。当天 e2e 排查时才撞见（该跑 FINDINGS 的 O2），
    事后由 `7153cc0` 订正。⚠️ **讽刺之处**：08-31 那次正是本条的**正面数据点**（预算线裁决按清单回填四处）
    —— **回填清单当时漏了 backlog 条目正文本身**。⇒ 手工照做**不是不会漏**，只是漏得少；**清单靠人现列，就一定有盲区**。
  - **（正）本次落账按本条先列清单再动手**：8 处逐项过（live 就地改 / 历史加新笔不动旧 / 规划文档补前向一句 / memory 同步），
    并显式记下「不动的是哪几处、为什么」。⇒ 第 2 次证明人工可行。
  - **⇒ 读数更新**：踩坑 **4 例**（08-18 分类线 · BN 立账 · 指南指已关条目 · 登记项超时数字），
    手工演练成功 **2 次**（08-31 预算线 · 09-04 本次）。**急迫性由「不急」上调** —— 例④说明连"照着做"的那次也漏了一处。
- **✅ 2026-09-04 触发条件 (B) 已兑现 —— 机制化落地**: 收口文档新增
  [§2.9.4「裁决落地 → 回填清单」](workflow/06-dod-and-evidence.md#294-裁决落地--回填清单backlog-bu-机制化--2026-09-04-立)，
  与 §2.9.3 同级承重（任一格空着 = 视同 evidence 缺失，**不进 §2.10 retro**）。
  - **关键设计 = 固定名单，不靠当场想**：8 格候选真值源写死（**条目正文自己排第 1 格** —— 例④ 漏的正是这格），
    每格必须给「改了 &lt;链接&gt;」或「N/A + 理由」，**留空即不合规**；N/A 是正当答案，空着不是。
  - 另加三道与 R7 同手法的动作：宽 grep（关键词含别名 / 旧框架词）· 分 live 与 point-in-time（并显式挡住 Q6 冻结档）· 收口后复扫。
  - **连带落地**：[§2.9.2 evidence summary 模板](workflow/06-dod-and-evidence.md#292-evidence-收集动作)加一行、
    [概览](workflow/06-dod-and-evidence.md)与[主链路第 8 步](workflow.md)同步、双向 cross-reference 接上。
  - 🔒 **2026-09-04 用户裁决（两条·已落地）**：
    - **可选 lint 粗检（"立账日期晚于 guide 引用文本日期"）= 不做**。理由 = 判据模糊、易造新噪音源，
      **且它防不住例④那种「清单本身有盲区」的形态**（固定名单才防得住）。⇒ **本条"任务"里这一半就此取消**，不再当待办。
    - **本条不 close**（活跃保持 15）—— 机制化虽落地，但**留着继续攒数据点**：§2.9.4 是否真拦得住，要靠往后每次裁决落地的实测说话。
      ⇒ 重新 close 的判据 = **§2.9.4 连续挡住/暴露 N 次回填遗漏后由用户裁**（N 不预设，避免又造一条没人回看的线）。
  - ⚠️ **如实记边界**：本次落地的是**要求与闸门**，不是自动化 —— 仍靠执行体照做，只是"漏了看得见"（名单固定 + 留空即不合规）。
    **真正的自动检测仍不存在。**
- **进入时点**: 2026-08-27。**预估**: ~~文档半天；lint 粗检另计 1 天~~ → 文档那半 **✅ 2026-09-04 已交付**；lint 那半 **用户裁决取消**。**配额**: 占 1 个 lettered slot（**用户 2026-08-27 授权破例**）·**本条不 close，活跃仍 15**。

---
- **📌 数据点（2026-09-24·CRED 节点收口·§2.9.4 拦不住的一种）**：`DEFECT-REVIEW-ERROR-AS-DATUM` 的影子试用计数停在「第 1 跑」，而 09-17 / 09-18（BK 节点冒烟）与 09-23 / 09-24（CRED 簇 2 / 3 收口）五跑都算过 `G1-shadow`、读数全没回填。§2.9.4 的 8 格管的是**本 goal 自己的裁决落地**；**别的节点的跑批顺带产出的试用期读数**不在任何一格里 ⇒ 这类回填没有主人。本次处置 = 段式指南 ⑧ 段加「抄完要回填条目计数」（落在跑批的人手上，而不是落在条目主人手上）。出处 [retro CRED](../retro/S2/CRED_2026-09-24.md)。

### BV. 人工确认路径的**取数失败在归档里没留痕** —— 人认的是计划，不是结果（🟡·2026-08-28 实锤·✅ **CLOSED 2026-08-31**）

> ✅ **2026-08-31 close-by-completion**（用户当日裁「BV 也改了吧」）。
> **修法**：新增 `confirm.unfulfilled_leg_notices(routing, payload_keys)` —— 拿
> `source_routing` 里的腿（`__` 开头的留痕键除外）减去资料夹真有货的键，差集即「点名要了、一条都没拿回来」，产出一条 `legs_empty` 告警。
> **接线**：[context_node](../../src/committee/agents/context_node.py) 里把告警拆成两类，**界限写进注释** —— 计划侧（兜底/校验拒/回核退）**人认过的不喊·一字未改**；结果侧（缺腿）**不分人工自动一律报**。
> 🔒 沿用 U1 纪律：**只报是哪几条腿空手，不定「空几条算退化」的门槛**。
> **验证**：5 条守护测试（含复刻 08-28 真跑形态：人认过的两条腿计划、金价那条空手 → 必须留痕）+ **隔离式反向验证**（只退回接线、保留新函数 ⇒ 行为守护那条当场变红、其余四条照常绿，证明它咬的是「接没接线」不是「函数存不存在」）+ 全量 **3849 passed**。
> **释放 1 个活跃 slot（18→17）；破例累计 15 不变。**

- **强度**: 🟡（不产生错误数据，但让**事后翻档的人看不见一条腿没到**，须自己拿计划逐条比对引用才发现）
- **实锤**: 真人确认了一版含金价的计划（`GC=F`）→ 取数时撞雅虎限流、三次重试全空 →
  最终 references 只有 fred 4 / rss 2 / wisburg 2，**没有行情腿**；而 checkpoint 里
  `__degradation_notices__` 为 `None`、`__budget_capped__` 为 `None` ⇒ **归档零留痕**。
  证据：[ACCEPTANCE.md](../observations/rp-g5b-human-20260828/ACCEPTANCE.md) 与同目录 checkpoint。
- **不对称在哪**: 自动确认路径**有**退化告警（U1 交付项），人工确认路径**刻意不喊** ——
  设计理由是「那条路上已经有人看过了，再喊是噪音」（[confirm.py](../../src/committee/retrieval_plan/confirm.py) docstring）。
  🔑 **那条理由只覆盖「计划有没有问题」，不覆盖「货有没有到」**：人看过的是**计划**，
  取数结果发生在他点头**之后**。⇒ 不是设计错，是**设计边界没延伸到结果侧**。
- **⚠️ 交互时人是看得见的**（终端打了三行 `YFRateLimitError`）—— 所以现场无损害；
  **缺的是归档留痕**，受害者是几周后翻档的人（与 [R6](../../CLAUDE.md) 「读 run 记录」同一类受害者）。
- **触发条件**（事件型）: (A) 下次动 `confirm.degradation_notices` / 告警接线时一并；
  (B) 下次真人确认跑批出现「计划里有、引用里没有」时；(C) 接入产品前端确认闸时（那条路上人更不盯终端）。
- **任务**: 让**结果侧**的退化事实进产物（不分人工/自动）—— 候选：确认后按计划逐条对账拿没拿到、
  差集写进 `__degradation_notices__`；⚠️ **只报事实不定阈值**（沿用 U1 那条纪律）。
- **为什么延后**: 动的是告警接线与产物字段语义，属行为变更；且 N=1、本次无损害。
- **进入时点**: 2026-08-28。**预估**: 半天。**配额**: 占 1 个 lettered slot（**用户 2026-08-28 授权破例**）。

---

### BW. 段式跑指南没有**真人验收**这种跑法的位置 —— 硬规则与它直接冲突（🟢·2026-08-28 切出·✅ **CLOSED 2026-08-31**）

> ✅ **2026-08-31 close-by-completion**（用户当日裁「BW 也改了吧」）：[段式跑指南](../observations/e2e-runs/segmented-e2e-guide.md)
> 「怎么跑」一节新增 **「⚙️ 唯一例外：真人验收跑」**。措辞把守两头 —— 开头先声明
> **原「必带 `--auto-confirm`」一字未改、对所有段式 e2e 照旧成立**，结尾显式排除
> 「懒得加 flag」（常规跑漏带 = 操作错误，不是走本例外）。⇒ **开的是一格新跑法，不是松一条旧规则。**
> 四条纪律：必须真终端 · 不产出段式 e2e 数据点（不进段间 checklist、产出另开具名目录）·
> 必须留验收记录 · 只在验交互闸时用。**释放 1 个活跃 slot（19→18）；破例累计 15 不变。**

- **强度**: 🟢（不影响产物正确性，影响的是**下一个人做不做得成真人验收**）
- **冲突本体**: [段式跑指南](../observations/e2e-runs/segmented-e2e-guide.md)「怎么跑」一节写着
  「首段**必带** `--auto-confirm` …否则**卡死等输入**」；而交互闸的真人验收**必须不带** ——
  要的就是它停下来等人。指南里**没有这个例外**。
- **本次怎么处理的**: 明知故犯 + 在[验收归档](../observations/rp-g5b-human-20260828/ACCEPTANCE.md)显式标注偏离与理由。
  **没有自行改指南** —— 那是放松一条硬规则，属 [§2.7 Q5](workflow/05-brake-self-check.md)（标准降低）该停下问的范围。
- **不改的后果**: 下一个人照指南走，要么以为「不带 `--auto-confirm`」是操作错误，
  要么干脆不做真人验收 —— 而 G5b 这次证明**真人验收能查出单测照不出的缺陷**（确认环把改好的计划扔了）。
- **触发条件**（事件型）: (A) 下次要做交互闸真人验收前；(B) 下次动指南「怎么跑」一节时。
- **任务**: 在指南里给「真人验收跑」开一格，写清**何时该不带 `--auto-confirm`**、
  产物往哪落、以及它**不算**常规段式跑（不进段间 checklist 纪律）。
- **为什么延后**: 改的是承重操作文档的硬规则措辞，须用户裁措辞边界，不宜顺手改。
- **进入时点**: 2026-08-28。**预估**: 半天。**配额**: 占 1 个 lettered slot（**用户 2026-08-28 授权破例**）。

### DEFECT-WISBURG-PADDING. 研报源只排序不过滤 —— 填充率是我们请求方式的函数，下游只有一把粗糙的文字筛子兜底（🟡·2026-09-01 review 切出）

> **用户裁（2026-09-01）**：「**这个本质上是研报数据源的问题，不是靠分词的松绑可以解决的**，
> 之后单独做研报数据源的优化。」⇒ 本条记的是**根因所在的那一层**，不是那把筛子。

- **强度**: 🟡（不阻塞，但两个方向都会损伤产物：筛太严→好货全退；筛太松→杂货进引用）
- **机制（一手来源 = 服务端自己声明 + 实测）**：见[接口说明书 §1①](../infrastructure/seg1_retrieval/wisburg-mcp.md)。
  服务端原话「不传时按发布时间倒序；传入时按**相关度排序**」⇒ **传了检索词并不会剔除不相关的**，
  只是把相关的排前面；**符合其他条件的内容不足一页时，剩下的位置用不相关内容填满**。
  实测：只传「黄金」时 20 条几乎全对题；**加上近四天时间窗后 20 条里只剩 4 条与黄金有关**
  （其余是铜、锂、中国消费、澳洲贸易）。⚠️ 说明书自己写明结论是
  「**不是"时间窗稀释了相关性"，而是"那个窗里本来就没有 20 条黄金报告，于是拿别的补满"**」。
- **为什么这是请求侧的问题**: 填充率随「限定强度 × 要多少条」上升 ——
  强限定下还要满页，等于**自己制造** 80% 的填充货，再指望下游一把文字筛子清干净。
- **今天的兜底、以及它的天花板**: 回核层按检索词做文字回筛（[verifier.py](../../src/committee/retrieval_plan/verifier.py) 研报那段）。
  2026-09-01 review 查出它对**不带空格的中文**整句失效（整句成一个 token ⇒「标题必须含完整原句」
  ⇒ 对题研报被整批筛空、整条腿退货、还按纪律 0 删掉好缓存），已改用全仓共用的中文二字分词
  （[text_match.py](../../src/committee/text_match.py)·**放宽容差属 [§2.7 Q5](workflow/05-brake-self-check.md)，用户 2026-09-01 已裁准**）。
  🔒 **但它只是最后一道粗筛，两头都会错**：放宽后实测「黄金价格走势」会把
  「白酒行业深度：高端价格带跟踪」判成对题（通用词「价格」撞上）。**再怎么调这把筛子都是治标。**
- **任务（候选方向，须实测定，不预设结论）**:
  1. **别在强限定下还要满页** —— 要么少要几条，要么不传时间窗、自己按日期筛（把填充源头掐掉）
  2. **按问题选对库** —— 五个报告库 + 智堡自有文章 + 资讯流语义各不相同，选错库等于在错的池子里捞；
     点名能力 G4b 已具备，计划层 G5 可用
  3. **复验「默认不传时间窗」那条** —— 说明书自己标注它**仅 1 次未复验观测**，值得补一次
- **为什么延后**: 改的是请求侧策略，且候选方向都需要**真实调用实测填充率**才能定；
  而急性症状（好货被整批退 + 误删缓存）已由分词修复止住，不紧急。
- **触发条件**（全事件型）: (A) 下次动 [wisburg_source.py](../../src/committee/common_context/sources/wisburg_source.py)
  或回核层研报那段时；(B) e2e 中再出现一次「研报腿被整条退货」或「明显跑题的研报进了引用」；
  (C) [BI](#bi-wisburg-只取研报标题全链无人读正文--半句话成了承重数字的依据2026-08-03-全链回归-e2e-findings-33-逐条过时立账) 残留（拆 per-report ref）开工时一并。
- **与 BI 的关系**: **不同源、不互相 supersede** —— BI 是**取深度**（只拿标题、没读正文），
  本条是**相关性**（拿回来的根本不是要的东西）。两条可以各自独立成立。
- **进入时点**: 2026-09-01。**预估**: 1–2 天（含实测）。**配额**: DEFECT 族，**不占 lettered slot**。

### BX. 行情格式表只认美股 + 港股 —— 东京 / 伦敦 / 法兰克福 / 首尔 / 孟买的股票一律被拒（🟢·2026-09-01 review 追问切出）

> **用户裁（2026-09-01）**：「两个都记账，先把这个 PR 收口。」⇒ 本条与
> `DEFECT-RETRY-ADVICE-FALSE` 同批立账，**本 PR 内不做**。

- **强度**: 🟢（当前主线是中港美，不影响在跑的场景；但撞上时是**完全不可用**，不是降级）
- **实测（2026-09-01）**: 把外国码喂进行情腿的格式校验，全部判「认不出」→ **拒收**：
  `7203.T`（丰田）· `VOD.L`（沃达丰）· `SAP.DE`（SAP）· `SHOP.TO`（Shopify）·
  `005930.KS`（三星）· `RELIANCE.NS`（信实）。**而数据源本身支持这些市场** ——
  拒的是我们自己的格式表，不是上游没有数据。
- **够得着吗 —— 够得着，但只有一条路**: 本地证券名录的
  [`MARKETS`](../../src/committee/security_registry/schema.py) 只有 `CN/HK/US`
  ⇒ 走「确认标的」那条路解析不出外国码；**但规划员是模型，可以直接把 `7203.T`
  写进计划**。那条路是通的。
- **撞上时的实际后果**: 个股问题的行情腿被拒 → [`ensure_price_leg`](../../src/committee/retrieval_plan/validator.py)
  两个源都补不出 → 价格闸早停「暂不可分析」，且给出一句**错的建议**
  （"请稍后重试"，而这个原因重试永远不会好）——那半边记在
  `DEFECT-RETRY-ADVICE-FALSE`，**两条要一起读**。
- **任务**: 扩格式表 + 名录市场。⚠️ **不是加几条正则就完** —— 须**逐市场实测**
  代码形态与真实返回（含币种、交易日历），并同步资产类型词表与分类链的顺序；
  分类链自己写着「认不出就说认不出、不给兜底档」，扩表时这条规矩不能松。
- **为什么延后**: 这是**真功能不是修 bug**，需要实测数据与排期；当前主线是中港美，
  没有在跑的场景被它挡住。
- **触发条件**（全事件型）: (A) 下次动行情源的格式分类链或名录 `MARKETS` 时；
  (B) 用户明确提出要问非中港美市场的股票；(C) e2e 里出现一次外国股票腿被拒。
- **进入时点**: 2026-09-01。**预估**: 2–3 天（含逐市场实测）。
  **配额**: 占 1 个 lettered slot（**用户 2026-09-01 授权破例 #16**·配额满的现状已当面告知）。

---

### DEFECT-CTX-BAG-SHAPE. 资料夹「两个互斥格子」把多条腿的事实压成一位全局标签 —— 资料员在替会议决定谁发言（🟡·2026-09-02 切出·PR2 主体已合并·本条继续持有剩余登记项）

> **📦 2026-09-08 从 §0.2 表格单元格拆出**：本条原先整条挤在一览表的备注格里（7813 字，超过 1000 字上限）。规矩早有——「已经不是表格单元格，而是一条藏在行里的条目，应拆出 §1 正文」——只是检查脚本当时看不见非字母编号的条目，所以从没响过。**下方正文逐字照搬原备注格，一个字未改**；表里那行只留一句指路。

2026-09-02 由 `DEFECT-COMMODITY-AS-TICKER` 开工时的第一性原理讨论切出（用户裁两 PR 拆分）。**PR2 内容**见拆解 [seg1-planner-librarian-redesign-2026-09-02.md §三](../plans/seg1-planner-librarian-redesign-2026-09-02.md)：`payload` + `legs` 元信息、`ticker_payload`/`macro_payload` 改兼容别名、具名问题 `has_equity_leg` / `price_leg_for`、12 个读者迁移、202 份旧归档兼容读法；**验收只一条 = 除归档现价外行为逐字节不变**。**🔴 8 条登记项（各自触发条件·不静默）**：① **规划员超时吃掉一部分跑** —— 超时则退回旧路由丢金价（= BQ 残留①的兜底路由·刻意降级设计）· 触发 = 动规划员超时/重试前**先测「超时里重试后成功占比」**（[G7 FINDINGS](../observations/rp-g7-e2e-20260827/FINDINGS.md)）〔**2026-09-04 数字订正 · 原文已废**〕~~`PLANNER_TIMEOUT_SECONDS=15` 是每次尝试上界、SDK 默认重试 2 次 ⇒ 最坏 45s vs 16s 封顶~~ —— **该组数字自 2026-08-28「40s 预算线」落地起即失效，条目一直没跟上**（属 **BU** 形态：裁决落地没回填真值源）。〔**🔴 2026-09-08 再订正 · 下面这组 40s/45s 数字已废**：超时线经**实测重定为 85s**、外层封顶 **90s**（= 85 + 一次核验上限 5s，且**改成从内层派生、不再抄数**）；钳位上限同步升到 85 ⇒ **原文「调大超时这条路走不通」那句也已作废**（用户 2026-09-08 裁·PR [#279](https://github.com/JunoChenZt/subagent-for-investment/pull/279) 合 main `f8ea795`）。6 次实测 28.0/30.5/36.0/36.7/41.0/67.4s ⇒ 40s 线吃掉 2/6，与本条原记「吃掉 1/3」对得上；**连带 run 级上限 90 → 120s**。⚠️ **第一段实测 51.8s**（封顶 116s·留一倍以上余量）。证据 [ctx-shadow-e2e-20260908](../observations/ctx-shadow-e2e-20260908/FINDINGS.md)〕~~**现行真值（2026-09-04 实测生效值，非读注释）**：出计划上界 = **40s**（[planner.py](../../src/committee/retrieval_plan/planner.py) `PLANNER_TIMEOUT_SECONDS`）· 外层封顶 = **45s**（[context_node.py](../../src/committee/agents/context_node.py) `PLAN_PHASE_TIMEOUT` = 40 + 一次存在性核验上限 5s）。🔴 **「调大超时再试」这条路走不通**：该值虽认 `COMMITTEE_PLANNER_TIMEOUT`，但**钳位上限就是 40**（实测传 120 仍生效 40）⇒ 想再放宽必须改代码常量 = 承重变更须用户裁。~~**⚠️ 频次读数比条目原记的差**：原文「吃掉 1/3 跑」出自 G7 的 A/B；**2026-09-04 A 股跑 2/2 全超时**（`APITimeoutError`·两跑都退兜底路由），而 **2026-09-02 三跑（黄金/NVDA/标普）是 3/3 成功** —— 两组都是小样本、**不下因果结论**，只把读数记在这里供触发条件那次实测参考（出处 = PR [#270](https://github.com/JunoChenZt/subagent-for-investment/pull/270) 分支上的 `docs/observations/ctx-legs-pr270-e2e-20260904/FINDINGS.md` O1 —— **该 PR 未合并前 main 上没有此文件，故不挂仓内链接**）② **ETF/ADR/REIT 按格式判为股票** · 触发 = e2e 出现一次 ETF 被基本面分析师当公司分析 / 动 `_MARKET_TO_ASSET_KIND` 时 ③ **「主/背景」列由规划员填、校验不核** · 触发 = 任何消费者要读 `scope` 做承重判断前 ④ **资产类问题行情缺失不早停**（保护不对称·候选「允许跑、禁写价位」模式；连带旧洞：无锚时退回信任模型自报现价）· 触发 = 动价格闸触发条件时 / 一次资产类跑行情空手仍出价位 ⑤ **引用不带标的 ⇒ 混合/比较题尺子取第一条**（设计 pass §8 第 10 项·R5 先读设计意图·零次实证不立项）· 触发 = 一次混合题 EXEC-FLOOR 拿错标的的价 ⑥ **分类正则兜底把 `GC`/`CPI`/`GDP` 当美股代码** · 触发 = 动 `regex_extractor` / 兜底路由时 ⑦ **降级留痕只到 `source_routing`/trace、未进最终报告** 〔**✅ 2026-09-14 由 BK.1 承接并关闭**（用户当日裁）—— 本条原文没说「最终报告」指哪，BK 重评时定锚 = **归档产物（`_build_result` 的 `degradations` 键）+ CLI 最终 markdown「本次降级提示」一节**，两处均已落地；汇总纯派生、不进模型提示词。⚠️ 关的是「留痕进不了最终报告」这个缺口，**不是「所有降级都留痕了」** —— 33 处只写日志的点仍在 [BK.2](../plans/BK-silent-degradation-reeval-2026-09-14.md) 待裁〕 · 触发 = 动最终报告渲染时 ⑧ **主链路文档 Phase 0a 行陈旧**（「0 次 LLM」实为 2 次）· 随 PR2 修。DEFECT 族不占 lettered 配额。**🔍 2026-09-02 PR #269 合并前 high-effort review 记账（8 角度 → 12 候选 → 10 坐实/可信）**：已修 4（补腿循环与守卫同口径·只补股票腿·跳过已覆盖标的含基码 / backlog 触发列旧措辞 / S2 §4.7.5 旧措辞 / 冗余函数内 import），**记入本条待裁 6**：⑨ **个股型分类 + 确认标的为商品/指数代码时价格闸误早停**（价在宏观袋、闸只看个股袋；且宏观分支不写 `ticker_resolution`）· 触发 = 一次早停结论里的标的是非股票形态 ⑩ **A 股源一律算股票**：`_validate_tushare` 只核六位码、ETF/指数（510300.SH / 000300.SH）名录未覆盖时进个股袋 —— 治本 = tushare 校验器也盖 `asset_kind`，谓词退化为源无关 ⑪ **缺 `asset_kind` 兜底不可达且一旦触发即复现原缺陷** —— 候选改为 `_classify_yf_format(ticker) == "equity"` + warning（行为口径变化须裁） ⑫ **名录核验处缺字段兜底方向与旧代码相反**（旧=跳过名录，新=进名录可拒收；今日不可达） ⑬ **`leg_is_equity` 硬编码源名成第四份副本** —— 收口为 `if source not in _PLAN_PRICE_SOURCES: return False` ⑭ **补腿守卫按整份计划判、不按每个确认标的判**（改前即有·多标的缺口·与登记项 5 同根）。DEFECT 族不占 lettered 配额。**✅ 2026-09-04 PR2 主体已完成 = PR [#270](https://github.com/JunoChenZt/subagent-for-investment/pull/270) 已 squash 合 main `415bc48`**：schema `payload`+`legs`（`LegMeta`）、两格子降为影子（`__post_init__` 双向推导·旧归档/旧断点/旧测试零改动）、`questions.py` 具名问题（`has_equity_leg` / `price_leg_for`）、8 个读者迁移、builder `_build_legs`；**⑩ ⑬ 一并做完**（tushare 按形态盖 `asset_kind`·`PRICE_SOURCE_NAMES` 单一真值）；**有意变化两处**（价格闸按标的匹配 / 归档现价读到值）+ 计划驱动下不对非股票腿拉财报；反向变异 8/8 KILLED·全量 3989/0。**🔍 合并前冷审三修（`51223f9`）**：① 代码匹配丢了交易所（**本 PR 新引入的回归** —— 数字核丢后缀再去前导零 ⇒ `000001.SH` 上证综指 = `000001.SZ` 平安银行、`0700.HK` = `000700.SZ` ⇒ 指数点位冒充个股现价放行价格闸）→ 数字相同**且交易所对得上**才算覆盖、前导零只对非六位码去；② **旧 A 股断点回放护栏反着开火**（资料夹里 tushare 条目是**裸六位码**、兼容读法只认带后缀 ⇒ `has_equity_leg` 由 True 翻 False ⇒ 从任何旧 A 股断点 `--resume` 续跑，基本面分析师在**真个股问题**上自动弃权）→ 裸码退回改前行为（算股票）；③ 计划名单与键**错位一格**（`sources_from_plan` 跳过构造不出源的意图、下游按位配对 ⇒ 股票腿丢失 = 护栏关火 + 误报早停；改前 `force_ticker_shape` 直读意图对此免疫 ⇒ **本 PR 把既有隐患升级成闸门级**）→ 多返回 `kept_intents`、三份名单同长（用户裁走法 A）。全量 **4000 passed**·反向变异 **3/3 KILLED**·②的用例按**真实 tracked 归档形态**构造、③的守护**走主链路 + 隔离验证**。**✅ A 股验证跑**（`ad6582d`·中际旭创 seg1–2）：**23 次调用含「非个股标的」提示 0 次**、基本面报告是真公司分析（营收 417.8 亿 +182.5%·PE 88.7·`DATA_INSUFFICIENT` 0 次）、价格闸不误报早停 ⇒ **缺陷镜像面成立**。**✅ 旧断点 `--resume` 补跑**（2026-09-04·[FINDINGS §五](../observations/ctx-legs-pr270-e2e-20260904/FINDINGS.md)）：拿仓里真实旧格式 A 股断点（07-10 中际旭创 seg1·资料夹存**裸码 `300308`**）续跑 seg2 —— 读档后该腿 `asset_kind=equity`、`_is_ticker_query=True`、**「非个股标的」提示 0 次**、基本面报告是真公司分析（证据 10 条·回撤 42%·护城河/估值齐）、再序列化一轮判定不变；段间 checklist 8/8 报告全过（每角色调用正好 3 次·贴上界但与 07-10 基线同）。⇒ **修法 ② 由「只有单测兜着」升为已实证**（它只在**读旧存档**时才走，是「每天都会撞上」的路）。**✅ 2026-09-07 ①③ 补守护**（PR [#272](https://github.com/JunoChenZt/subagent-for-investment/pull/272) 已合 main `63547cf`）：① 新增**从真实在册归档加载**的用例（此前那条端到端用例是手搭上下文 = 本域自己总结过的病灶），含前提断言与对照组；③ 查明**今天结构上不可达**（校验层只放行五源、构造层这五个全认得 ⇒「认不出、跳过」那条岔路走不进去），故不加 e2e，改加「校验层放行的源 ↔ 构造层工厂表」名单同步守护 —— **不是验那条补丁管不管用，是让它永远用不上**（补丁留作第二层）。⇒ 覆盖现状：**① 有守护（但见 ⑮ —— 真实数据上仍打不着）· ② 已实证 · ③ 改为不可激活**。⚠️ **仍不冒充"跑过一次真的"**：①③ 的真实触发条件都不在日常路径上（一个要撞车、一个不可达），这是刻意选的处置。**🔴 2026-09-07 新增两条登记项（DEFECT 族不占配额）**：⑮ **交易所守护在真实 A 股数据上是死的**〔**✅ 2026-09-07 已修 · PR [#276](https://github.com/JunoChenZt/subagent-for-investment/pull/276) 合 main `8e0e5fe`** —— 行情源改写完整代码；连带修 `_to_ts_code` 幂等（否则补基本面拼出 `300308.SZ.SZ`、静默少数据）。**冷审逮到本 PR 自己引入的一处误退**：`.SH`/`.SS` 是上交所两种拼法，覆盖判定真比交易所后把同一只判成两只 ⇒ 价格闸误早停、整跑白停 —— 已归一（同义词表与校验层共用一份）。**新增登记项 ⑰ ⑱ 见下。**〕 —— [tushare_source.py](../../src/committee/common_context/sources/tushare_source.py) 把完整代码 `ts_code` **主动切掉后缀**再写进资料夹（`symbol = ts_code.split(".")[0]`），于是 A 股这侧**永远是裸码** ⇒ 修法 ① 的「交易所对不上就挡住」**永不触发**；实测裸码 `000001` **同时匹配** `000001.SH`（上证综指）与 `000001.SZ`（平安银行）。🔑 **信息没丢、是被丢掉的** —— 完整代码就在上一行手里 ⇒ 修法 = 写完整代码（旧归档有裸码兜底已在）。· 触发 = **已排入 2026-09-07 计划第 3 步**（不等事件）⑯ **五个源名仍散在四处**〔**✅ 2026-09-08 已修 · PR [#277](https://github.com/JunoChenZt/subagent-for-investment/pull/277) 合 main `79aeef5`**〕〔⚠️ **两处口径订正（正文按 point-in-time 不动）**：① **实为五处不是四处** —— 冷审补出第五份手抄 `planner.VALID_SOURCES`（管「模型写出来的源名认不认」·不认整条丢掉）；② 合并后 main 上那条 commit subject 写的是「**四张表**对着一份名册点名」，**同样少数了一处** —— squash 后的 subject 不改，前向事实以本行为准〕 —— 登记项 ⑬ 只统一了**行情源那两个**（`PRICE_SOURCE_NAMES`）；完整五源名单仍分别写在校验器钥匙表 / 格式校验表 / 构造工厂表 / 构造分支里。#272 加的是**两两比对**守护（漂开会红），不是单一真值 ⇒ 治本仍欠。· 触发 = 下次动这四处任一时。**🔴 2026-09-07 新增登记项 ⑰（⑮ 修复的连带面·PR [#276](https://github.com/JunoChenZt/subagent-for-investment/pull/276) 冷审记账）**：⑰ **归档「按标的查」那一列混了两种写法** —— ⑮ 起 A 股写**完整代码**（`600519.SH`），而 [#270](https://github.com/JunoChenZt/subagent-for-investment/pull/270) 到 #276 之间写入的 A 股行是**裸六位**；该列（`ticker_resolved`）在 [api.py](../../src/committee/server/api.py) 上是**精确匹配过滤** ⇒ **按裸码查不到新行、按完整代码查不到旧行**，两边都只查到一半、且不报错。🔑 **不是本次引入的坏事**（该列在 #270 之前生产里恒为 None，有值之后就一直朝着新旧混写走），但 ⑮ 让它成了稳定的两段式。**候选修法**：查询侧按名录规范形态归一后再比（读侧修、不动已写入的行）；或一次性回填旧行。· 触发 = 下次动那个查询接口 / 需要按标的查归档时。⑱ **名录不认 `.SS`（同根第三处·后果未追到底）** —— [`normalize_code`](../../src/committee/security_registry/schema.py) 对 `600519.SS` 返 `None`，其 docstring 写明识别不了 = 按「名录里没有」处置、而 matcher 注释说这类会「按 reconcile 决策表当无效码丢弃」。⚠️ **本条只坐实了「返 None」这个事实，没有追到下游真实后果**（会不会真丢掉一个合法确认标的·丢了之后走哪条路），故**不声称它无害**、也不声称它在漏。#276 里没动它，理由是：那是**另一个模块自己立的边界**（那里明写「不猜：识别不了就返 None，交由上层保守处置」）—— 按 [Chesterton's Fence](../../CLAUDE.md) 该先读当年为什么这么立，而不是顺手把同义词表塞过去。· 触发 = 下次动名录代码归一 / 一次 `.SS` 确认标的被判无效码时。**🔻 仍留在本条（未随合并关闭）**：⑨ ⑪ ⑫ ⑭ **⑰ ⑱** + 原登记项 1–7（8 文档已随 PR2 修）+ 段式 e2e **剩余跑只剩 NVDA 首段**（旧断点 resume 与 A 股跑均已做）。**⑮ 已 ✅**（2026-09-07·#276）· **⑯ 已 ✅**（2026-09-08·#277）· **影子字段删除已 ✅**（2026-09-08·PR [#278](https://github.com/JunoChenZt/subagent-for-investment/pull/278) 合 main `afa669b`）· **段式 e2e NVDA 首段已 ✅ 跑完**（2026-09-08·PR [#279](https://github.com/JunoChenZt/subagent-for-investment/pull/279) 合 main `f8ea795`·零退化告警·计划驱动那条建腿路径已验）⇒ **🎉 主线欠账清零，本条只剩事件型登记项**（⑨ ⑪ ⑫ ⑭ ⑰ ⑱ + 原登记项 2–7 + 读档手写白名单；**① 已随 #279 处理**）。

---

### DEFECT-D5-COUNT-AS-VALUE. 序列型引用登记成 `list(N)` 占位串 ⇒ 引用检查拿条数当数值去对账（🟢·2026-09-03 PR #269 段式 e2e 验收跨两跑稳定复现切出）

> **✅ CLOSED 2026-09-24（close-by-completion·CRED.2.G5·用户当日裁·保留位置）** —— 修法① 已落（#314）；全链 e2e 占位值真实出现、D5 全 pass、审核判「非可比数值」不拿条数去比（[FINDINGS](../observations/cred-2-g5-e2e-20260923/FINDINGS.md) §3.1）。重开条件见 §0.2 本行。以下为关闭前原文，不再改动。

> **📦 2026-09-08 从 §0.2 表格单元格拆出**：本条原先整条挤在一览表的备注格里（1177 字，超过 1000 字上限）。规矩早有——「已经不是表格单元格，而是一条藏在行里的条目，应拆出 §1 正文」——只是检查脚本当时看不见非字母编号的条目，所以从没响过。**下方正文逐字照搬原备注格，一个字未改**；表里那行只留一句指路。

2026-09-03 PR [#269](https://github.com/JunoChenZt/subagent-for-investment/pull/269) 段式 e2e 验收跨两跑稳定复现切出（黄金跑 3 处 macro/technical/economist · 标普跑 2 处 macro/economist·[FINDINGS O4](../observations/cat-pr1-e2e-20260902/FINDINGS.md)）。**机制（已核到代码 + 实测）**：`fred` 的 12 期序列在表①按 [watermark.py:39](../../src/committee/common_context/watermark.py) 登记成字符串 `"list(12)"`；D5 先剥 `W#` 再比对时，[rules_d.py](../../src/committee/triage/rules_d.py) 的跳过名单只排除 `N/A` / `list(0)` / `dict(0)`，**`list(N≥1)` 照走数字桥** ⇒ `_extract_numbers("list(12)")` 取出 **12**、拿去和正文 ±200 字窗里的数字比。实测三态：正文含「过去12个月」→ **pass（巧合）**、含「12.1%」→ **pass（容差内假绿）**、只有「CPI 3.30%」→ **fail（噪音）**。⇒ **两个方向都不对**：它比的是元素个数，不是引用的值。🔒 **边界**：D5 属 **D 类·只记不拦**（verdict 不受影响·[rules_d.py](../../src/committee/triage/rules_d.py) docstring 明写「caller must NOT use D-class results to change verdict」）⇒ **fail 面零变化、不阻断任何跑批**；本条问的是**这条检查在序列引用上量的是不是它自称在量的东西**。⚠️ **不得据本条把 D5 升成阻断**（提高 fail 面须用户裁·[acceptance-standard §4](e2e-acceptance-standard.md)）。**候选处置**：① 最轻 = 把 `list(N)` / `dict(N)` 整族加进跳过名单（与已有 `list(0)` 同法·**显式弃权好过假信号**）〔**✅ 2026-09-23 已实现 = CRED.2.G1·已合 main #314 `c22976a`**（[rules_d.py](../../src/committee/triage/rules_d.py) `_is_unauditable_value` + `_SEQUENCE_PLACEHOLDER_RE`·[test_rules_d.py](../../tests/test_rules_d.py) `TestD5SequencePlaceholderSkip`：三态 4 用例全跳过 + 家族边界 13 + 真数值守护 1·反向变异删整族分支 → 4 红）；**条目待 2.G5 全链 e2e 佐证后 close**，候选 ②③ 明确不做（D 类升级·另立）〕② 中 = 序列型引用改登记成可对账的摘要值（如首末值 / 最新值），让 D5 真能核 ③ 重 = 给序列引用单独一条检查。**为什么延后**：零阻断、零实际伤害，且候选 ② 动的是表①登记法（多处消费者）须实测。DEFECT 族不占 lettered 配额

---

### BZ. 命令行打印的最终报告不是给人读的形态 —— 标题截半句 / 引用标记裸印 / 执行计划不显示 / 投票印 JSON / 括注文本损坏（🟡·2026-09-28 读者视角审读切出）

- **来源**：S2 收口后用户要求「从头到尾再看一遍」，以 [cred-2-g5 黄金全链跑批](../observations/cred-2-g5-e2e-20260923/FINDINGS.md) 为样本按基金经理读报告的视角逐段通读；逐条问题与代码落点见 [读者视角审读清单](../observations/s2-reader-review-20260928/CHECKLIST.md)（R1–R8 + C6）。
- **强度**: 🟡（读者拿到的成品可读性；不影响决策正确性）
- **触发条件**: **全事件型** —— 下次动 [cli.py](../../src/committee/cli.py) 决策渲染段 / 下次动 [schemas/decision.py](../../src/committee/schemas/decision.py) 标题上限 / 下次全链跑批读最终报告再出现一次截断或裸标记 / S3 定命令行还是前端为主入口时 / 用户明确要求。
- **现象（核到）**：① 论点标题字段 `max_length=30`，三个标题恰好 30 字、第一个截成「…而非'启」；② 正文 27 个 `{ref:fN}` 原样印出，而 [cli.py](../../src/committee/cli.py) 渲染不打印引用附录（242 条）；③ 结构化执行计划（入场 / 止损 / 止盈 / 重估触发器）命令行不显示，价位只散在论点四散文里（前端有 [ExecutionPlanCard](../../frontend/src/components/committee/ExecutionPlanCard.tsx)）；④ 投票汇总印一段 JSON；⑤ 括注折叠逻辑（[base.py](../../src/committee/agents/base.py) `_GATE_CAVEAT`）只认「（未独立核实）」一种措辞，模型自写的「未完全核实」「未核实」漏折叠 → `{ref:f18}（未独立核实）（未完全核实）` 连写、`12.5%（未独立核实）未核实）` 错位（错位机理为推断）；⑥ 数字与单位空格不统一、英文单引号当引号、「时间维度」字段名；⑦ 中性四票里一票是基本面席自动弃权（[base.py:1471–1479](../../src/committee/agents/base.py)），汇总看不出。
- **任务**：按清单 R1–R8 + C6 改渲染层，每项配逐字用例（含连写 / 错位两条）。R7 引号与 CA 的 P2 二选一落一处。
- **为什么延后**：S2 已收口、S3 未开工；入口以命令行还是前端为主待定，避免只修一条路。
- **进入 backlog 时点**：2026-09-28。**预估工作量**：中（1–2 天）。
- **关闭条件**：清单 R1–R8 + C6 逐项落地 + 一次全链跑批的命令行输出人工通读无上述形态。

### CA. 内部机制名与「未核实」括注漏进用户面 —— 提示词与代码两处都在写、谁是权威没定（🟡·2026-09-28 读者视角审读切出）

- **来源**：同 BZ；逐条见 [读者视角审读清单](../observations/s2-reader-review-20260928/CHECKLIST.md)（P1–P4 · P6 · C5）。
- **强度**: 🟡（读者信任：报告里出现看不懂的编号与三种「未核实」措辞）
- **触发条件**: **全事件型** —— **用户裁两条原则**（给人看的报告允许出现哪些内部信息 / 「未核实」括注由模型写还是代码写）后 / 下次动 [prompts/decision/prompts.py](../../src/committee/prompts/decision/prompts.py) 输出规范段 / 下次动 [base.py](../../src/committee/agents/base.py) 括注折叠段 / 全链跑批再出现一次规则编号进用户面 / 用户明确要求。
- **现象（核到）**：① 仓位字段写「满仓的 20%（受 R2 交叉质疑闸门约束，上限 25%）」—— 提示词规则本身叫「R2. 交叉质疑约束」（[prompts.py:158](../../src/committee/prompts/decision/prompts.py)），模型把编号抄进字段；信心解释写「26 条跨角色质疑」、止盈备注写「v11 verified 更新值」同理；② 提示词 [:111](../../src/committee/prompts/decision/prompts.py) 让模型给来源不硬的数字就地标「（未独立核实）」，代码的门（[base.py:2333](../../src/committee/agents/base.py)）再标一遍，靠折叠去重 ⇒ 措辞漂成三种、无说明；③ 推算值也挂括注：`87%{ref:f52}（未独立核实）` 是现价÷目标价，同句 `89%` 又没标；④ 无中文标点 / 日期格式 / 仓位写法规范（`'中后段'`、`6-12M`、`9-16`、「满仓的 20%」）。
- **📌 2026-09-28 · 两条原则已裁（用户）**：① **给人看的报告一律不许出现后台信息，只留结论和理由** —— 规则编号（R2 / G2）、查证编号（v11 / f52）、闸门名、跨角色计数一概不进用户面字段；② **「未核实」括注由模型贴，程序只补漏** —— 模型按提示词就地标注，代码的门只在模型漏贴处补一个、绝不重复贴，措辞统一为一种。⇒ 本条触发条件的「待裁」格已兑现，**开工时机另议**。
- **任务**：按上面两条原则 → 提示词加「不得引用规则编号与内部编号」+ 输出规范（中文引号「」/ 日期写全 / 人名首现带身份 / 推算值写「按 X 算约 Y」不挂括注 / 仓位固定写法「组合的 N%」）→ 渲染层兜底剥离 `R\d` / `G\d` / `v\d+ verified` → 括注措辞集合守卫（正文括注只能来自一个固定集合，否则 WARN）。
- **为什么延后**：两条原则须用户裁；改基金经理提示词是承重变更（输出契约），S2 已收口不在此时动。
- **进入 backlog 时点**：2026-09-28。**预估工作量**：中。
- **关闭条件**：两条原则落文档 + 提示词 / 渲染 / 守卫三处落地 + 一次全链跑批输出无内部编号、括注措辞单一。
- **📌 2026-09-29 · ✅ CLOSED（用户裁·按「报告面」口径）**：关闭条件逐项 —— 两条原则落文档 ✅ · 三处落地 ✅（G3 提示词禁令 + 括注归一 / G4 渲染器机制名闭集 / Q13 括注集合守卫·PR [#327](https://github.com/JunoChenZt/subagent-for-investment/pull/327)）· 跑批输出：[seg9 断点探针](../observations/rdr-1-ca-seg9-probe-20260929/FINDINGS.md)（09-23 黄金跑 seg8 续跑 seg9·PR [#328](https://github.com/JunoChenZt/subagent-for-investment/pull/328) ✅ 合 main `c195f617`）括注 18/18 单一、渲染后报告面机制名 0。**两种读法用户裁①**：CA 原则①的落点是报告，报告面 0 即达标；「模型不写」那一格（提示词禁令 1/1 跑滑落一次「26 条跨角色质疑」）**不是本条关闭条件**，记 RDR-1 节点 retro 观察项。⚠️ 如实记：探针是断点续跑不是全新全链（前八段为 09-23 产物），且真跑抓出三处回放盲区（投票枚举对象 / 硬闸文案 / 跨角色计数）与合并前 review 两处（两闸同响拼接串 / D3-β 尾巴 G1-G5 原文）均已修进渲染闭集。**重开条件**：全链跑批报告面再出现一次后台信息。review 留的 5 条次要项（「N 条」不分 N / G2 原文形态 / graph.py 非 json 模式 model_dump 根因 / `execution_plan` 无边界 / 多余 `_plain`）**同日用户裁「也修掉」→ PR [#329](https://github.com/JunoChenZt/subagent-for-investment/pull/329)** 全部修（含根因：装箱机六处 `model_dump(mode="json")`，真跑 result 与归档同形状）。

### CB. 决策文本前后不一致与算术错误没有任何检查 —— 止损两个数 / 同一指标两个值 / 盈亏比算错（🟡·2026-09-28 读者视角审读切出）

- **来源**：同 BZ；逐条见 [读者视角审读清单](../observations/s2-reader-review-20260928/CHECKLIST.md)（C1–C3；C4 时间叙述矛盾只记不立）。
- **强度**: 🟡（会误导读者判断：三处都是承重数字；不改变决策方向）
- **触发条件**: **全事件型** —— 下次动 [e2e_quality_gate.py](../../src/committee/e2e_quality_gate.py) / 全链跑批再出现一次同类（散文与结构化价位不一致 / 同一机构同一指标两个值 / 可复算数字算错）/ 用户明确要求。
- **现象（核到）**：① 论点四「硬止损 4200」与「跌破 4313 止损」并存；结构化 `stop_loss.level=4200`，重估触发器却写「跌破 4313 → 止损离场」；终局 Q4 只核止损合不合理、不核几处一致；② 论点一「高盛年末目标 4900 的 89%」与少数派「高盛年末公允价值的 93%」（对应 4650，八份分析师报告用的都是 4650）并存 —— 基金经理联网核出 4900（v11）后换数未交代；③「盈亏比按现价至 4645/4200 计约 1.4:1」实算 1.86:1；**现有全部检查只核数字有没有出处（stamp-gate / claim_audits / Q3–Q5），没有一道核算术**，终局 15 项全过。
- **任务**：三条新检查，按 [验收判据表 §4](e2e-acceptance-standard.md) 先登记维度与承重边界、**一律 WARN 试用**：(a) 价位一致性 —— 散文里的止损 / 入场 / 止盈须与结构化计划一致，触发器带「止损」字样的阈值须等于 `stop_loss.level`；(b) 可复算数字 —— 「盈亏比 / 距目标 X% / 占比 Y%」从同句抓操作数复算，误差 >5% 报；(c) 同名指标多值 —— 同一机构 + 同一指标在决策文本里出现不同数值即报并列出两处；配套提示词「换数须说明与分析师所用值的差异」。
- **为什么延后**：新检查须先登记；S2 已收口。
- **进入 backlog 时点**：2026-09-28。**预估工作量**：中。
- **关闭条件**：三条检查登记 + 落地 + 对本样本归档回放三处全响、对 CRED 三次黄金跑批回放零误报记录在案。

## 2. 时间型条目(按时间触发)


---

## 3. 已完成(归档区)

> 本节保留已完成的 backlog 条目,**不删除**,便于事后追溯"我处理过这个吗"。
>
> 归档格式:`✅ [日期] 条目编号 — 一句话结论`

### L. Hook 配置落地 ✅ CLOSED 2026-05-19

- **Close 方式**: by-completion (commit `fba4d11`, PR #117)
- **Close 摘要**: hook 架构重写 (路径 D) + 三层根因翻案完成。"VS Code 扩展通道限制"翻案为伪根因 — 真因 = Claude Code API 改名(TodoWrite→TaskCreate/TaskUpdate) + 输出缺 hookEventName 字段。全 7 case 验证通过, additionalContext 注入在当前环境完全可用。
- **原强度**: 🔴
- **原触发条件**: A6.1.1 节点收口时识别 SKILL.md auto-trigger 机制 0 落地
- **完成情况**:
  - G1 (4cd8143): XML schema 迁移到 workflow 子文档
  - G2 (188ced9): 7 SKILL.md 标 deprecated + README
  - G3 (b204acf + 80cb737 + 1ad493f): CLAUDE.md + hook 脚本 + 登记 + 措辞精确化
- **三层根因**: L1 现象(hook 0 注入) → L2 直接原因(API 改名 + hookEventName 缺字段, 两个独立 bug 叠加) → L3 根本原因(2026-05-14 未做变量隔离, 多因归单因)
- **遗留**: verification-report subagent 尚未实战 → 见 backlog B
- **进入 backlog 时点**: 2026-05-14
- **归档时点**: 2026-05-19 (Audit Log 2026-05-19 housekeeping)

### B. verification-report skill 实战验证 ✅ CLOSED 2026-05-25 (re-close)

- **Close 方式**: close-by-completion (subagent 真实执行)
- **Close 摘要**: verification-report subagent 产出完整 XML（`<verification_report subphase="S2.1" verdict="PASS">`），8 个必填 section 齐全。4 checkpoint 全过：(1) XML 格式合规；(2) PASS verdict，结构化可消费；(3) 7 pitfalls active→mitigated，12 仍 active，0 retired；(4) 1 observation promoted (O-A6.1.2-02 N=3)，3 approaching threshold，0 stale。CLAUDE.md 已更新移除"(尚未实战)"。
- **⚠️ 首次 close 撤销记录 (2026-05-25)**：首次 close 基于"S2.1 verification report 已跑"，但实际产出是手写 markdown（[s2.1-verification-report-2026-05-25.md](../observations/s2.1-verification-report-2026-05-25.md)），**未通过 subagent 机制执行**。属于"触发到了就 close"而非"任务做完了 close"——governance 漏洞。reopen 后真实执行 subagent，本次 re-close。
- **教训**: "触发条件满足" ≠ "任务完成"。close-by-completion 须验证 deliverable 存在且符合 skill 定义的输出格式。
- **原强度**: 🟢
- **原触发条件**: S2.1 子阶段最后一个节点 PR 合并时（已满足）
- **进入 backlog 时点**: 2026-05-14
- **归档时点**: 2026-05-25 (re-close)

### D. 并行节点 WIP limit 调整 ✅ CLOSED 2026-05-25

- **Close 方式**: close-by-completion
- **Close 摘要**: S2.1 完成后按 §5.2.2 五维度评估。(1) PR review 无积压（7 PR / 11 天，全 1-2 天合并）；(2) ledger 无冲突；(3) 无同类问题重复修；(4) baseline/skill 改动无冲突；(5) evidence 路径清晰。决定：**维持 WIP limit = 3**。S2.1 串行依赖为主，未真正压测并行上限；待 S2.2 首个子阶段数据再议。
- **原强度**: 🟢
- **原触发条件**: S2.1 子阶段完成后
- **进入 backlog 时点**: 2026-05-13
- **归档时点**: 2026-05-25

### J. Cold review 机制正式化 ✅ CLOSED 2026-05-25

- **Close 方式**: close-by-completion
- **Close 摘要**: N=2 验证通过（A6.1.2 + A6.1.3 节点级 cold review 均稳定产出 ≥3 Finding）。落地形式 = workflow §2.11.7 "推荐，非强制"规则（非 SKILL.md / 非 hook / 非强制 mandate），含 provenance 强度排序（cross-session 双盲 > 不同模型 > warm-cold > 人工）。跳过 cold review 须在 retro 显式说明。升级路径: 出现"跳了 cold review 后 production 出 bug"的反面数据 → 升级为强制。同步在 §2.11.4 动作序列加入 cold review 步骤 + backlog §4.4 计数检查。
- **原强度**: 🔴
- **原触发条件**: 5+ 次 cold review 抓漏实证（已满足）
- **落地位置**: [08-retro-node-and-pr.md §2.11.7](workflow/08-retro-node-and-pr.md)
- **进入 backlog 时点**: 2026-05-14
- **归档时点**: 2026-05-25

### M. achievement_ratio 计算规则显式化 ✅ CLOSED 2026-05-25

- **Close 方式**: close-by-completion
- **Close 摘要**: A6.1.2 retro 印证触发模式（achievement_ratio=1.0 但有 2 项显式 defer）。落地 = workflow §2.11.8 四档计算规则 + 强制规则"有 defer 项时 ratio 不能填 1.0"。
- **原强度**: 🟢
- **原触发条件**: A6.1.2 retro 时 achievement_ratio=1.0 但有 defer 项（已满足）
- **落地位置**: [08-retro-node-and-pr.md §2.11.8](workflow/08-retro-node-and-pr.md)
- **进入 backlog 时点**: 2026-05-14
- **归档时点**: 2026-05-25

### E. must_update 数量门槛调整 ✅ CLOSED 2026-05-25

- **Close 方式**: close-by-completion
- **Close 摘要**: S2.1 五节点 retro 数据 — A6.1.1=3 / A6.1.2=0 / A6.1.3≈0 / A1=0 / P4.B≈4。must_update=0 占 40%（正常），超 2 的节点均有合理原因（A6.1.1 首节点 cold review 密集 / P4.B 大返工）。决定：**维持 ≤2 per retro 启发式**，作为"超了说明发生了大事"的信号灯。
- **原强度**: 🟢
- **原触发条件**: S2.1 子阶段完成后
- **进入 backlog 时点**: 2026-05-13
- **归档时点**: 2026-05-25

### F. settings.json 权限调优 ✅ CLOSED 2026-05-25

- **Close 方式**: close-by-completion
- **Close 摘要**: 11 天实战数据评估（2026-05-14 → 2026-05-25）。(1) ask 中无"每次都直接 allow"的项；(2) 无"以为会拦但 Claude 直接做了"的误放行；(3) `--force-with-lease` 正确在 allow。结论：**无显著调整需求，维持现状**。初始配置质量高。
- **原强度**: 🟡
- **原触发条件**: settings.json 部署后 7 天
- **进入 backlog 时点**: 2026-05-14
- **归档时点**: 2026-05-25

### H. task-entry handoff 协议 ✅ CLOSED 2026-05-19

- **Close 方式**: by-completion (commit `aad5eca`, A6.1.3.3 step8)
- **Close 摘要**: 全 4 任务闭。Q4 逐源重审维持🟢; DISPATCHER_TOTAL_TIMEOUT 12.0 实测 load-bearing; O-A6.1.2-01 防御 N=2 维持; hook 翻案(官方 Claude Code hook≠0 全链路可用)。
- **原强度**: 🟡
- **原触发条件**: A6.1.3 task entry (§2.3 pre-flight) 时
- **收口证据**:
  - H.1 Q4 逐源重审 → §9 #12 commit `3e6a63a`
  - H.2 12.0 实测 → §9 #10 commit `8a955da`
  - H.3 O-A6.1.2-01 防御 → N=2 维持, 0 新 miss + 5 正面数据点
  - H.4 hook observe → 翻案: 官方 Claude Code hook≠0 全链路可用
- **进入 backlog 时点**: 2026-05-18
- **归档时点**: 2026-05-19 (Audit Log 2026-05-19 housekeeping)

### A. baseline-drift-detector skill 设计与落地 ✅ CLOSED 2026-05-26 (close-by-decision)

- **Close 方式**: close-by-decision（scope 蒸发）
- **Close 摘要**: 原设计前提 = 9 个 SKILL.md 是治理核心，subagent 扫 20+ 文件检测 4 类漂移。2026-05-19 起 7/9 SKILL.md deprecated（真值源迁移到 workflow 子文档），仅 2 active skill 存活。4 类漂移中"版本漂移"和"接口漂移"显式引用 SKILL.md 体系，前提不再成立。"路径漂移"和"锚点漂移"仍通用，但规模已从"20+ 文件"缩至"2 active skill + 11 workflow 子文档"，cold review (§2.11.7) + PR review 可覆盖。专建 subagent 是 over-engineering。
- **⚠️ 残余风险（悲观标注）**: 路径/锚点漂移在 governance 文档间**无自动化系统性检测**。Cold review 是"推荐非强制"（§2.11.7），跳过时漂移可能累积无人发现。如 cross-doc 引用断裂出现 **N≥2** 模式（不同 session 独立发现同一断链），应考虑轻量 link-checker 脚本（非 subagent）作为新 backlog 条目。
- **原强度**: 🟡
- **原触发条件**: 9 个 SKILL.md 跑过 3-5 个真实 S2 节点之后（已满足但 scope 蒸发）
- **进入 backlog 时点**: 2026-05-14
- **归档时点**: 2026-05-26

### C. SKILL.md description 风格统一性复盘 ✅ CLOSED 2026-05-26 (close-by-decision)

- **Close 方式**: close-by-decision（前提不再成立）
- **Close 摘要**: 原任务 = 收集"哪些 SKILL.md description 导致正确/错误触发"的数据并优化措辞。2026-05-19 起 SKILL.md deprecated，主 Claude 改为直接 Read workflow 子文档执行规则，"description-based 触发匹配"机制已不存在。任务对象（description 措辞优化）和测量方法（触发率数据收集）同时失效。
- **⚠️ 残余风险（悲观标注）**: "workflow 子文档是否在正确时机被读取"是 C 原始关切的演变形态，当前**无系统化测量**。如出现"应读未读"或"读晚了导致规则违反"的模式（**N≥2**，不同 session 独立命中），应作为新 observation 独立追踪，而非复活 C。
- **原强度**: 🟢
- **原触发条件**: 跑过 5 个真实 S2 节点之后（已满足但前提蒸发）
- **进入 backlog 时点**: 2026-05-14
- **归档时点**: 2026-05-26

### S. yfinance retry+AV fallback mock 可控性 ✅ CLOSED 2026-05-28 (close-by-completion)

- **Close 方式**: close-by-completion（commit `2f18a7d`, PR #132）
- **Close 摘要**: PR #132 `fix(test): yfinance empty-data 测试 mock AV fallback 消除网络 flaky` 精确修了 S 描述的"retry+AV fallback 绕过 mock"问题。修法 = test 内 monkeypatch 双 mock（`_sync_fetch` + `_alpha_vantage_fetch` → None），切断"测试 ↔ 真实网络 / AV API 配额"耦合。test docstring 显式警告"必须同时 mock `_alpha_vantage_fetch` 返回 None，否则 AV 命中真实网络成功时...degraded 失败（test 与网络/配额耦合 = flaky）"。
- **稳定性验证**: 15/15 PASS（10 + 5 两轮 isolated direct run）。早期 3 次中 2 fail 是 Windows 瞬态干扰（杀软/IO），**不是 S 的原始问题**。
- **悲观自纠**: 我最初看 2/3 fail 就判"S 不能 close"——未实证（哪个 commit 修的）就下结论。`git log` 一查就找到 PR #132 已精确修。复发条件：未来若有人改回单 mock，本条复活模式 = N≥2 直接重开。
- **原强度**: 🟡
- **原状态**: §0.1 pending（永未转正进 §1，slot 不释放）
- **进入 §0.1 时点**: 2026-05-20（PR-C Step 4.1 base comparison）
- **归档时点**: 2026-05-28

### T. Claude Code git 破坏性操作护栏 — worktree 事故预防规则 + brake 模板修订 ✅ CLOSED 2026-05-28 (close-by-completion)

- **Close 方式**: close-by-completion（R1-R4 规则从 retro 文档上升到 governance 真值源）
- **Close 摘要**: PR-C worktree incident retro 中沉淀的 R1-R4 规则之前**只在 retro 文档**（`docs/retro/S2/PR-C-worktree-incident_2026-05-20.md`），未进 governance baseline。本次三处落地：
  - **R1（禁用 worktree 做 base-check）+ R2（任何假设 remote 状态前 fetch）** → [git-workflow.md §6.8](git-workflow.md#68--active-worktree-base-check-反模式--假设-remote-状态未-fetch-pr-c-事故) 新增"已知坑"段（含 PR-C 事故 case study + 违反信号）
  - **R3（check 报告必须披露执行过程异常）** → [brake-self-check.md §2.7.5 Q5](workflow/05-brake-self-check.md#275-8-问详细判定标准) 隐式 skip 模式清单加第 5 条 + 正确替代加一条
  - **R4（事实纠错优先，不允许跑命令拖延纠正）** → [CLAUDE.md 默认沟通风格](../../CLAUDE.md#默认沟通风格) 第 4 条
- **落地验证**: 三处 grep 都能命中 R1/R2/R3/R4 关键词 + 引用 PR-C-incident-2026-05-20.md 作为 case study。未来 brake 8 问 / git 操作时会被读到。
- **悲观残余风险**: R1-R4 是"被读到才有效"的语义层规则，无机械 enforcement。若 Claude 跳过 brake 8 问或忘记读 git-workflow.md，规则失效。但这是 governance 体系通病（[[A close 时残余风险]] 同源）；当前无更好 enforcement 机制（hook 检查 worktree add 调用属 over-engineering）。如出现"R1-R4 落地后仍发生同型事故" N≥2 → 升级为 hook 拦截或 pre-commit check。
- **原强度**: 🟡
- **原状态**: §0.1 pending（永未转正进 §1，slot 不释放）
- **进入 §0.1 时点**: 2026-05-20（PR-C worktree incident retro 当日）
- **归档时点**: 2026-05-28

<a id="y-incomplete-event-真实触发率的跨模型差异监测"></a>
### Y. incomplete event 真实触发率的跨模型差异监测 ✅ CLOSED 2026-05-29 (close-by-decision)

- **Close 方式**: close-by-decision（被 [Z](#z-fund_mgr-跨模型opus-vs-deepseek对照验证-✅-closed-2026-06-02-close-by-completion) 完全覆盖 + 阈值已撤 + 逻辑已单测）
- **Close 摘要**: Y 的创立数据本身即 DeepSeek 0 漏（N=8/10/15），2026-05-28 全 deepseek e2e 再次 0 漏——但这些都是 **deepseek 侧**数据，Y 的真正 OPEN 问题（opus 是否也 ~0 漏）**仍无数据**，故**不构成 close-by-data**。close-by-decision 理由三条：① Y 质疑的"漏回应率 > 30% → 加警示"阈值已在 [pr-8c-readiness §9](../observations/pr-8c-readiness.md) 撤回；② incomplete 逻辑已单测（休眠安全网，防回归）；③ 残留的 opus 跨模型对照问题**被 [Z](#z-fund_mgr-跨模型opus-vs-deepseek对照验证-✅-closed-2026-06-02-close-by-completion) 完全覆盖**（Z 显式追踪"漏回应率 opus vs deepseek 0/15，决定 §9 撤回的 30% 预设是否在 opus 成立"）。Y ⊂ Z，单独留 Y 冗余。
- **⚠️ 残余风险（悲观标注）**: 若 Z 验证发现 opus 与 deepseek 漏回应行为显著不同（opus 会漏），则"跨模型差异"本身是发现——但该追踪归 [Z]，不复活 Y。incomplete 单测若被删 = N≥1 直接重开。
- **配额**: close-by-decision 释放 1 槽（基于条目自身 merit、非腾配额，§4.4 合规）；为 AC/AD 破例承诺"close ≥2"的**第 1 条**，第 2 条 = AC 本 PR merge 时 close。
- **原强度**: 🟢
- **原触发条件**: PR-8c staging observation 启动时（与 observation-spec §3 同步执行）
- **进入 backlog 时点**: 2026-05-21
- **归档时点**: 2026-05-29

### AC. fund_manager 合成层不服从下游信号 ✅ CLOSED 2026-06-02 (close-by-completion)

- **Close 方式**: close-by-completion
- **Close 摘要**: PR [#135](https://github.com/JunoChenZt/subagent-for-investment/pull/135)（OBEY-1~7 三层防御 + DS-0 并行 subagent + EVID 证据绑定）+ PR [#136](https://github.com/JunoChenZt/subagent-for-investment/pull/136)（三值收敛 + OBEY-5 推广 + cold-review 修复）已 merge main。2026-06-02 opus e2e 验证 risk_gate G2 finding + fund_mgr response 闭环正常工作。原 7 条已验证根因全部有对应修法落地：Layer 1 prompt 硬规则段（OBEY-1~7）+ Layer 2 schema/code validator + challenge-response 闭环。
- **原强度**: 🔴
- **进入 backlog 时点**: 2026-05-28
- **归档时点**: 2026-06-02

### AD. 证据绑定 / Audit Pipeline 升级 (Firn-inspired) ✅ CLOSED 2026-06-02 (close-by-completion)

- **Close 方式**: close-by-completion
- **Close 摘要**: PR [#138](https://github.com/JunoChenZt/subagent-for-investment/pull/138) AD.1-8 全部完成（[AD-decomposition.md](../plans/AD-decomposition.md)）。本地 e2e 验证：deepseek {ref:fX} coverage 33%（7/21, 0 hallucinated）/ opus {ref:fX} coverage 51%（24/47, 3 misattributed flagged by EVID-1）/ verify_fact 确定性批量核验 / 窄硬地板 (AD.7) 功能正常 / risk_gate G2 + response 闭环。附带修复：config.py 空 API key 清理 + deepseek/tushare trust_env=False 绕代理 + ds_researcher 提前到 triage 后与 debate 并行（perf 优化，零额外等待）。
- **Deferred 子项（非阻塞，已登记 retro）**: ① 问题 A 结构化源路由（Q3 观测确认有价值：~50% fund_mgr web_search 本可结构化）② DS-0 {ref:fX} 折叠进统一附录 ③ enforcement_log 独立 JSONL
- **Evidence**: [e2e-ds-20260602-103125.json](../observations/e2e-runs/e2e-ds-20260602-103125.json) / [e2e-notimeout-20260602-131755.json](../observations/e2e-runs/e2e-notimeout-20260602-131755.json) / [e2e-prod-20260602-115714.json](../observations/e2e-runs/e2e-prod-20260602-115714.json)
- **原强度**: 🟡
- **进入 backlog 时点**: 2026-05-28
- **归档时点**: 2026-06-02
- **旁证数据点（2026-06-09 补，AD 已 closed 仅留档）**: political 选型四臂实验发现**模型选择影响 REF 伪造率**——deepseek-v4-pro 在 wisburg 单 blob 输入下引真实 ref_id + 内部报告号、未发明 `[REF#W-84830]` 这类伪造；同输入下 gemini 引用更泛、未锚定具体报告。换 deepseek 顺带缓解部分 REF 伪造，但根因（wisburg 单 blob watermark 拆分）仍需 AD 体系解。详见 [decision-review](../observations/experiments/political-arms/decision-review.md)。

### Z. fund_mgr 跨模型（opus vs deepseek）对照验证 ✅ CLOSED 2026-06-02 (close-by-completion)

- **Close 方式**: close-by-completion
- **Close 摘要**: 2026-06-02 本地 e2e 产出 opus vs deepseek 对照数据：
  - **JSON 合规率**: 两者 100%（均无 parse error）
  - **决策质量**: opus=BUY conf=6 / deepseek=HOLD conf=5（opus 更有主见，与投票 7:3 多数一致）
  - **{ref:fX}**: opus 24 refs（51% coverage）/ deepseek 7 refs（33%）— opus 引用密度远高
  - **risk_gate_response**: 两者均正常产出（G2 finding + response）
  - **漏回应率**: 两者均 0/1（100% 回应，验证 OBEY 闭环在 opus 同样成立）
  - **enforcement_log**: opus 触发 EVID-1 flag 3 misattributed refs — 比 deepseek 更激进引用 → 更需要 enforcement
- **原强度**: 🟡
- **进入 backlog 时点**: 2026-05-21
- **归档时点**: 2026-06-02

---

## 4. 维护协议

### 4.1 新增 backlog 条目

- 满足以下任一条件,登记到 §1 或 §2:
  - 在设计 / review 中识别"应该做但现在不该做"的事
  - retrospective-goal 输出的 `should_update` 被节点级 retro 裁决为 "defer"
  - retrospective-node 的 q5_sedimentation 中产生的延后项
- 必填字段:**强度 / 触发条件 / 任务 / 为什么延后 / 进入 backlog 时点 / 预估工作量**
- 缺任一字段 = backlog 登记不完整,回炉

#### 🔒 判据有效性约束（2026-08-06 立·**触发条件只能挂"迟早会撞上的信号"**）

> **起因**：2026-08-06 完整 triage 实测 —— 条目 **P** 与 **Q** 的触发条件全部挂在
> 「`.3 step6` observation 数据窗持续 ≥1 周」上，而该监测早已停跑。两条从 2026-05-19 挂到 08-06
> 共**两个半月一次都没被评估过** —— 不是因为不该做，是因为**没人可能发现它该做了**。
> 病根不是这两条写错了，是**没有任何机制保证"闹钟还响不响"会被检查**。

**✅ 允许的触发条件形态 —— 会被自然撞上，不需要谁记得去查**：

- 「下次动 `<具体文件 / 模块 / 配置>` 时」（最常用·最可靠）
- 「条目 `<X>` close / PR `<#N>` 合并后」
- 「e2e / 生产 run 中出现一次 `<可辨认的具体现象>`」
- 「用户明确提出 `<具体诉求>`」
- 「`<某节点 / 子阶段>` 开工前」

**❌ 禁止的触发条件形态 —— 需要有人主动去看，而没有机制保证有人去看**：

- 「某监测数据窗持续 ≥N 周 / 某指标达到 X%」（**除非同时写明谁在什么时候看这个数据、且该监测当下确实在跑**）
- 「用户反馈 ≥N 次」（**除非确实存在反馈采集渠道**）
- 「某评估 / 某排期之后」（**除非该排期已实际存在于 roadmap**）
- 任何依赖"将来会有人回头统计"的量化门槛

**⚠️ 反向条件同样适用本约束，而且更要紧**：反向条件挂死信号比触发条件挂死信号**更隐蔽** ——
它让条目**既不可能被做、也不可能被关掉**，永久卡死在活跃位上，还占着上限 15 的配额。
（实例：P 的原反向条件 (a) 与其触发条件 (a)(c)(e) 挂的是同一个已停跑的数据窗。）

**登记时自检一句**：*"如果这件事该做了，是什么动作会让人撞见这条？"* —— 答不上来 = 判据不合格，回炉重写。

### 4.2 触发条件命中后的处理

- 命中时 Claude 主动提示用户:"backlog 条目 X 的触发条件已满足,是否现在处理?"
- 用户决定:**现在做** / **再延后**(必须改触发条件,不能模糊延期) / **取消**
- 现在做 → 处理完后移到 §3 已完成
- 取消 → 移到 §3 已完成,标"已取消 + 原因"

#### 🔒 命中提示已机械化（2026-09-14 立·**不再是人工义务**）

> **起因**：条目 **BJ** 的触发条件 (B) 自 2026-08-07 起 **9 次提交命中**，其中 2 次在 08-31
> 完整 triage 之后，而 §0.2 账面一直写「未触发」。**判据没坏** —— 事件型判据的立论是
> 「迟早会被自然撞上」（见 [§4.1](#41-新增-backlog-条目)），但**撞上那一刻此前没有任何环节出声**，
> 靠的仍是人当场想起来有这么一条。这是本表自己撞上 [META 观察](../observations/meta-assume-mechanism-without-verify.md)
> 「用了机制 ≡ 假设保障兑现」的形态，**同形态第 2 次**（首次 = 2026-08-31 过账记录）。

**本节上方那句「命中时 Claude 主动提示用户」现在有机器在做**：

- [`scripts/lint_backlog_triggers.py`](../../scripts/lint_backlog_triggers.py) 在 **CI**（`lint` job 的 backlog-triggers 步·2026-09-21 起合并进 `lint`）
  与 **pre-commit** 两处跑，拿本次改动路径比对各条目声明的监视对象，命中即点名并指回本节。
- **声明写在 §0.2 备注格，二选一**（形状同 [闸门矩阵元测试](../../tests/test_gate_matrix.py) 的豁免）：
  - `〔监视 src/committee/config.py, .env.example〕` —— 路径 / 目录（结尾带 `/`）/ glob
  - `〔不可监视：理由〕` —— 理由 **≥15 字**，防「不需要」这类等于没写的豁免
- **沉默 = 失败**：两样都没写的活跃条目会被点名为「尚未声明」；解析出 0 条声明 = 检查器空转，直接 exit 2。

⚠️ **三条边界，读的时候别放大**：

1. **WARN 试用期，只提示不拦路**。命中 ≠ 现在必须做 —— 仍按本节三选一由人裁（现在做 / 改触发条件再延后 / 取消）。
   升 hard-fail 须按 [e2e 验收标准 §4](e2e-acceptance-standard.md) 走用户裁决。
2. **它只看得见「等某个文件被动」那一类判据**。等「跑批时出现某现象」「某阶段做完」「用户提出某诉求」的条目，
   本闸**结构上看不见**，这些条目每次都会被列进「本闸看不见的 N 条」。**只报命中不报盲区 = 再造一块假绿。**
3. **它不替代 [§4.2 完整 triage 的问二](#42-触发条件命中后的处理)**：问二问的是「这条判据今天还可能满足吗」，
   而一条挂死信号的判据**永远不会命中**，因此永远不会被本闸点名 —— 两者查的是不同的失效。

#### 🔒 完整 triage 必须问两问（2026-08-06 立）

**完整 triage**（逐条过全部活跃条目，区别于定向扫"触发已满足"）时，每条**必须问两个问题**，缺一不可：

| | 问题 | 答"否"时的处置 |
|---|---|---|
| **问一** | 触发条件**满足了吗**？ | 未满足 → 保持活跃，记录本轮已核 |
| **问二** | 这个触发条件**今天还可能满足吗**？ | **不可能满足 → 判据已失效**，按下方三档处置 |

**问二答"否"的三档处置**：

1. **事还该做，只是闹钟坏了** → 按 [§4.1 判据有效性约束](#41-新增-backlog-条目) 重定为事件型判据，
   并按 [§4.3](#43-触发条件本身的修改) 在条目内追加修订史。（实例：**P**）
2. **事的核心已被别处做掉，剩余要等别的前提** → close-by-decision，**剩余按 [R7](../../CLAUDE.md) 写去引用方**
   （活的规划文档 / 真值源 / 入口导航），不许只在条目里写一句"剩余待做"就关掉。（实例：**Q** → S3 L-C.4）
3. **事还在但与另一条同源同触发** → close-by-**merge**，全文并入承接条目。
   **⚠️ 注意与 close-by-supersede 区分**：supersede = 问题本身没了；merge = 问题还在、只是并轨追踪。
   判错方向 = 埋掉一个活的缺陷。（实例：**AP** → BI，其修法落点被 #226 删除**看起来**像 supersede，
   复核源码才确认实质问题原封不动）

> **为什么问二必须独立成问**：问一只查"世界变成触发态了没"，问二查"这条判据本身还连着世界没"。
> 只问一，判据挂死信号的条目会**永远答'否'并静默留在活跃位**——它不吵不闹，看起来只是"还没到时候"。
> 2026-08-06 一轮 triage 就抓出 2 条（P/Q）挂死两个半月，另 1 条（AP）触发形式满足但实质无事可做。

### 4.3 触发条件本身的修改

- 触发条件**可以改**,但每次改要在条目内追加历史:
  ```
  - 原触发条件:9 SKILL.md 跑过 3-5 个真实节点
  - 修改于 2026-XX-XX:改为 9 SKILL.md 跑过 5-10 个真实节点
  - 修改原因:实际跑下来 3-5 个数据不足以判定漂移模式
  ```
- 不允许偷偷改

### 4.4 backlog 数量上限

- §1 + §2 总数 ≤ **15 条**（计数口径 = **活跃条目**, 已 ✅/CLOSED 但物理未移 §3 的不计入活跃数）
- 超过 = backlog 失控,要么"现在处理掉一批",要么"重新评估哪些其实不必做"
- 不允许默默扩

**解读细则 (2026-05-19 决议, 见 Audit Log)**:

本规则采用 **解读 X (严格)**: 一旦触发"破例次数 = 2 (真实)", 仅能通过以下方式释放配额:
- close-by-completion: 条目触发条件满足后做完, 移 §3
- close-by-decision: 基于条目自身价值评估认为不再追踪, 移 §3 并标注理由

**明确禁止**:
- audit 修正历史破例数 → **不**释放未来破例配额
- 为腾配额而提前评估其他条目 → **不**作为合法 close 理由
- "先加再清来洗白" 的循环操作

**Housekeeping 规则**: 状态变更 (✅ / CLOSED) 必须同步移 §3 或显式标注 "✅ 但保留位置 (理由)"

### 4.5 修改本文件

- type(scope):`docs(backlog):`
- 新增 / 修改 / 归档条目都用这个 prefix
- 不需要 PR(走 [git-workflow.md §1.3 例外](git-workflow.md#13-例外何时直接在-main-上-commit) — docs-only)

---

## 5. 与其他文档的关系

| 文档 | 关系 |
|---|---|
| [docs/roadmap/S2.md](../roadmap/S2.md) | 任务清单(本周做什么);本文件是"以后做什么" |
| [docs/governance/workflow/09-known-pitfalls.md](workflow/09-known-pitfalls.md) | 已知坑(防回归);本文件是"识别的延后改进" |
| [docs/governance/workflow/10-verification-report.md](workflow/10-verification-report.md) | 子阶段交接审视;子阶段交接时**必看**本文件 |
| [docs/observations/should_update_observations.md](../observations/should_update_observations.md) | observation 累积;累积 ≥ 3 次升级到 should_update,有时候会进 backlog |
| [docs/roadmap/S2.md §4.6](../roadmap/S2.md) | Agent 现状审视协议;gate close 前必经,agent prompt/schema 改动的 PR retro 必须引用基线 |

---

## 6. 迭代历史

- **2026-09-29（第 1 笔·CA close）**：**CA ✅ CLOSED**（用户裁·按「报告面」口径·保留位置）—— seg9 断点探针（PR #328 合 main `c195f617`）括注 18/18 单一 + 渲染后报告面机制名 0；「模型不写」不是关闭条件（1/1 跑滑落一次·进 RDR-1 retro 观察项）；重开 = 全链跑批报告面再漏一次。BZ 不关。
  - **配额**：配额族 **10 → 9**（close 释放 1 slot·上限 15 余 6）；非配额族 **13 不变**；破例累计 **16 不变**；`lint:active-count` 同步改 **9**。**🔴 仍 0 条**。
- **2026-09-28（第 4 笔·RDR-1 节点落地）**：**CB ✅ CLOSED**（close-by-completion·G0 四检查回放三处全响 + 对照零误报）· **`DEFECT-GATE-S4-NO-PRODUCER` ✅ CLOSED**（G1·处置 ①）· **`DEFECT-RETRY-ADVICE-FALSE` ✅ CLOSED**（G2·真跑两次）· **BZ / CA 不关**（各差「一次全链跑批」那一格·G5 用户裁暂缓）。拆解 [RDR-1](../plans/RDR-1-decomposition.md)。
  - **配额**：配额族 **11 → 10**（close 释放 1 slot·上限 15 余 5）；非配额族 **15 → 13**；破例累计 **16 不变**；`lint:active-count` 同步改 **10**、`lint:active-other-count` 改 **13**。**🔴 仍 0 条**。
- **2026-09-28（第 3 笔·S2 读者视角审读立账）**：新增 **BZ**（命令行最终报告不是给人读的形态·渲染层 8 项）· **CA**（内部机制名与「未核实」括注漏进用户面·两条原则须用户裁）· **CB**（决策文本前后不一致与算术错误无任何检查·新检查 WARN 试用）· `DEFECT-TRIAGE-REWORK-REASON-OPAQUE`（轻条目）。来源 [读者视角审读清单](../observations/s2-reader-review-20260928/CHECKLIST.md)；配额族 8 → 11、非配额族 14 → 15。
- **2026-09-28（第 2 笔）**：**O 阶段完成归档机制 ✅ CLOSED（close-by-completion·S2 收口 G3）**。三项全完成，任务 ③ 经用户裁改为「写 S2 索引页、文件不搬家」（[docs/archive/S2.md](../archive/S2.md)）。同笔：S2 收口（[收口报告](../observations/s2-close-report-2026-09-28.md)）· 坑表 S2 结束审视落地。
  - **配额**：配额族 **9 → 8**（close 释放 1 slot·上限 15 余 7）；非配额族 **14 不变**；破例累计 **16 不变**；`lint:active-count` 同步改 **8**。**🔴 仍 0 条**。

- **2026-09-22（第 4 笔）**：**BK 静默降级可见化 ✅ CLOSED（close-by-completion·用户当日裁·保留位置）**。两本账归零（登记待补 0 站 · 盘点真待补 0 行·实跑 92 / 0 / 53），挂着的 28 条记账 / observe 项整体迁入观察点表 [O-BK-01](../observations/should_update_observations.md)（各带事件型触发条件·不累积 N）；同日第 3 笔已另立轻条目 `API-EMPTY-QUERY`（非配额族 14 → 15）。
  - **配额**：配额族 **12 → 11**（close 释放 1 slot·上限 15 余 4）；非配额族 **15 不变**；破例累计 **16 不变**；`lint:active-count` 同步改 **11**。**🔴 仍 0 条**。

- **2026-05-14**:初版(6 条 backlog:A baseline-drift-detector、B verification-report 验证、C description 风格、D WIP limit、E must_update 门槛、F settings.json 调优)
- **2026-05-14**:加条目 G (QueryType enum 扩展至 5 类，触发=A6.1.2 / A6.1.5 节点设计时明确需要)。来源：A6.1.1 grill 发现 roadmap §21.1 承诺 vs §6.1 实证 gap。
- **2026-05-14**:加条目 J + K。来源：A6.1.1.1 /review + retro amend 双重经验。
  - J (code-reviewer skill) — 跑 3-5 节点后看 brake + DoD 双重保险拦截率，不够再启动
  - K (retro amend protocol) — N=1 数据等 N=3 稳定信号再启动
- **2026-05-14**:J 触发条件修订（A6.1.1.2 retro amend 推动）。原 "3-5 节点 N=2 类问题" → 新 "6-7 goal N=3 次模式"。A6.1.1.2 timeout zombie 是同款 cold-review 抓 self-audit 漏，N=2 但 goal 数据更稳。
- **2026-05-14**:加条目 O（阶段完成归档机制，🟢）。来源：backlog 初建时识别——S2 远没完成，归档规则 YAGNI，等真要归档时再建。
- **2026-05-14**:加条目 L (🔴 P0)。来源：A6.1.1 节点收口 cold review 触发后 2 步实证 — SKILL.md auto-trigger 机制 0 落地。**不是普通延后项**，A6.1.2 起步前必须决定 A/B/C 方向。详见 [O-A6.1.1-05](../observations/should_update_observations.md#o-a611-05-架构层-gap非普通累积-observation)。
- **2026-05-18**:加条目 I（retro governance should_update，🟢）。来源：A6.1.2.2 retro defer（Q5 元规则 + pre-flight Read 父节点 + O-A6.1.2-02 升级落地三合一）。N=1 不拔高，走 governance PR 不混节点 PR。
- **2026-05-19**:条目 L 关闭(🔴→✅)。路径 D hook 重写 + 三层根因翻案。"VS Code 扩展通道限制" 翻案为伪根因 — 真因 = Claude Code API 改名(TodoWrite→TaskCreate/TaskUpdate) + 输出缺 hookEventName 字段。全 7 case 验证通过。方法论修正:涉及 hook 行为的归因前须做 stdout 格式独立单测 + tool_name 实测,不在多因下接受单因解释。
- **2026-05-19**:加条目 **N**（依赖 lock 机制缺失，🟡）。来源：A6.1.3.2 step0 加 akshare/yfinance 高漂移 deps，用户 add-item 识别无 lock → 跨环境版本漂移风险。**§1+§2=15 达 §4.4 上限**，下一新增前需先清理一批（多条触发条件已满足）。
- **2026-05-19**:加条目 **P**（facts cache 限流/失效降级语义升级，🟡，defer-until-data）。来源：A6.1.3.2 review 稳定性兜底讨论。物理 §1+§2=16，**L 已 ✅ 故真实活跃=15=踩线未超**（原声称第1次破例, audit 修正为非破例）。
- **2026-05-19**:条目 **P** 扩展触发条件 (d)(e)（Surface 1 future binding）。来源：A6.1.3.3 step8 用户裁决——F1/F2 修法改变 degraded 频率/语义，cache 层必须以此为 prior。
- **2026-05-19**:加条目 **Q**（用户 query 反馈/引导通路缺失，🟡）。来源：A6.1.3.3 cold review F1/F2 严格修法决策 surface。物理 §1+§2=17，**真实活跃=16，第 1 次真实破例**（原声称第 2 次, audit 修正）。
- **2026-05-19**:加条目 **R**（Yahoo Finance RSS 长期可靠性，🟢）。来源：A6.1.4 Phase 0a surfaced debt #2。物理 §1+§2=18，**真实活跃=16 (L+H 已 ✅)，第 2 次真实破例**（原声称第 3 次, audit 修正）。**严格条件：不再允许第 3 次真实破例，下一新增前必须先 close ≥1 条**。
- **2026-05-19**: **Backlog 计数 audit**。发现 L/H 已 ✅ 但未移 §3, 历次声称数失真。真实破例 = 2 次 (Q+R), 非 3 次。L/H 移 §3 归档。§4.4 加解读 X 细则 (audit 修正不释放破例配额)。详见 Audit Log 段。
- **2026-05-20**: 加 §0.1 Pending additions (S/T/U 三条草案)。来源：PR-C (#122) 收口。配额冻结，不计入 §1/§2，仅防遗忘。同时写 PR-C worktree 事故 retro (`docs/retro/S2/PR-C-worktree-incident_2026-05-20.md`)。
- **2026-05-20**: 加 §0.1 Pending **V**（§13.4 role 差异化必填集，🟢）。来源：A/B/C 分诊规则落地 roadmap-v3.4.md §13.4 时显式延后 role 差异化必填集到 S2.2。
- **2026-05-21**: 加条目 **W/X/Y/Z**（PR-8c / P4.B 返工期间 surface）。⚠️ 当时未更新 §6 迭代历史，补标。W=设计文档技术债（🟡）；X=D1 hard contract 争议（🟢）；Y=incomplete event 跨模型监测（🟢）；Z=fund_mgr 跨模型对照（🟡）。
- **2026-05-25**: **close B/D/E**（S2.1 收口承诺兑现）。B=verification-report 实战已完成；D=WIP limit 五维度评估→维持 3；E=must_update 五节点数据→维持 ≤2 heuristic。三条移 §3。
- **2026-05-25**: **Audit #2**（W/X/Y/Z 入场 + B/D/E 出场）。W/X/Y/Z 2026-05-21~25 进入未走 §4.4 破例流程 = 第 3-6 次真实破例（协议失守）。归因：feature branch 工作时未检查 §4.4 计数。新增防护：§2.11.4 动作序列加 push 前 backlog 计数检查。详见 Audit Log 2026-05-25。
- **2026-05-25**: **close J+M**（§2.11 governance 打包落地）。J=cold review 推荐规则写入 §2.11.7（provenance 排序 + 非强制 + 升级路径）；M=achievement_ratio 四档规则写入 §2.11.8（defer 扣分强制）。两条移 §3。§1+§2 活跃 17→**15 = 合规**。
- **2026-05-25**: A/C 追加 §4.3 触发修订历史（"已满足但配合 J 延后到 S2.2"）；K 裁决 N=2（warm-cold 不算数），加 6 个月反向条件（2026-11-25）；G 补 S2.2 P0' ticker 解析层联动标注。
- **2026-05-25**: **close F**（settings.json 调优，close-by-completion）→ §3。11 天实战无显著调整需求。同时 **reopen B**（governance 漏洞：首次 close 基于手写 markdown 非 subagent 执行）。
- **2026-05-25**: **re-close B**（subagent 真实执行 PASS）。verification-report subagent 产出完整 XML，8 section 齐全，4 checkpoint 全过。CLAUDE.md 更新"(尚未实战)"→"(2026-05-25 S2.1 首次实战 PASS)"。活跃 15→**14**（< 上限，1 slot 空余）。
- **2026-05-25**: 新增 **§0.2 活跃条目一览表**（14 行 quick-index：ID/标题/强度/触发状态/备注）。
- **2026-05-26**: **close A+C**（close-by-decision，scope 蒸发）。A=drift-detector 原设计前提 9 SKILL.md 已 7/9 deprecated，专建 subagent over-engineering，cold review 覆盖残余 drift；残余风险标注=路径/锚点漂移无自动检测，N≥2 断链时考虑 link-checker。C=description 触发匹配机制已不存在（主 Claude 直接 Read workflow 子文档），任务对象+测量方法同时失效；残余风险标注=workflow 子文档读取时机无系统测量，N≥2"应读未读"时新建 observation。
- **2026-05-26**: **V 从 §0.1 转正到 §1**（触发条件"S2.2 启动时"已满足）。A/C close 释放 2 slot → 活跃 14-2+1=**13**（§0.1 剩 S/T/U 三条，2 slot 空余）。§0.2 一览表同步更新。
- **2026-05-27**: 加条目 **AA**（Rework 盲重试，🟡）。来源：S2.2-gate batch 1 root cause analysis — `make_rework_node()` blind retry 不传 triage failure notes。物理 §1+§2=14。
- **2026-05-28**: 加条目 **AB**（DS-0 timeout → fallback under deepseek，🟡）。来源：PR #133+#134 merge 后首次全 deepseek e2e 触发 DS-0 timeout。物理 §1+§2=15=上限。
- **2026-05-28**: 加条目 **AC/AD**（用户授权破例，e2e 深度审计后）。AC=🔴 fund_mgr 合成层不服从下游信号（vote/risk_gate/dissent/cross_check/out_of_scope）；AD=🟡 证据绑定 / Audit Pipeline 升级（Firn-inspired）。**第 7-8 次累计破例**，承诺启动时 close ≥2 条释放。⚠️ AB/AC/AD 三条加入时 §0.2 一览表未同步——治理漂移（与 W/X/Y/Z §6 漏标同模式）。
- **2026-05-28**: **close S**（§0.1 → §3，close-by-completion）。证据 = commit `2f18a7d` PR #132 精确修了 mock AV fallback 双 mock（test 内 monkeypatch `_alpha_vantage_fetch` → None），切断网络/配额耦合。15/15 isolated run 全 pass 验证。S 从未转正进 §1，close 不释放 §1 slot。
- **2026-05-28**: **§0.2 housekeeping + Audit #3**。补 AB/AC/AD 三行进 §0.2，count 14→**17**（超上限 2 条）。§0.1 status 文字同步更新。Audit #3 documenting 治理漂移 + close S 实证逻辑。
- **2026-05-28**: **close T**（§0.1 → §3，close-by-completion）。R1-R4 规则从 retro 文档升到 governance：R1+R2 → git-workflow.md §6.8 新已知坑（含 PR-C case study）；R3 → brake-self-check.md §2.7.5 Q5 第 5 条隐式 skip 模式；R4 → CLAUDE.md 默认沟通风格第 4 条。T 从未转正进 §1，close 不释放 §1 slot。§0.1 pending 剩 U（1 条）。
- **2026-05-26**: 加条目 **AA**（Rework 盲重试，🟡）。来源：S2.2-gate root cause analysis — `make_rework_node()` blind retry 不传 triage failure notes，historian/economist 系统性 rework 无效（2/2 仍 reject）。活跃 13→**14**（< 上限，1 slot 空余）。
- **2026-05-28**: 加条目 **AB**（DS-0 timeout → fallback，🟡）。来源：S2.3 e2e 测试（query "夏天炒电"，全 deepseek）DS-0 LLM timeout 触发 fallback，facts_inventory=[]、{ref:fX}=0。活跃 14→**15 = 上限踩线（合规未破例）**。
- **2026-05-28**: 加条目 **AC + AD**（用户明确授权"不考虑上限，马上处理"）。**用户 push back**：上一轮我把 AC（服从性）和 AD（证据绑定）误合并成"Audit Pipeline 升级"，用户指出这是两个正交根因 — Firn 三段式 audit 解证据绑定但完全不解服从性，合并后果 = "看起来 close 了一个大条目实际漏了最致命的那半"。分立后活跃 15→**17 = 第 3-4 次真实破例（用户明确授权）**。
  - **AC** 🔴 服从性（核心架构）= 立即修法。已验证根因 7 条（DECISION_PROMPT soft guidance / risk_gate_findings 不注入 head pass / hard_block 只切 high severity / risk_gate.py:19-21 明文"v1 fund_mgr is not aware of gates"）。修法两层（prompt 硬规则 + schema validator 兜底）。
  - **AD** 🟡 证据绑定（Firn-inspired）= AC 后启动。3-phase audit + deterministic verdict + grep-verified coordinates + 数字格式 bridging + 7-value verdict。AGPL-3.0 借鉴架构思路不拷代码。
  - **§4.4 破例配额状态**：用户授权下连续 +2 = 第 3/4 次真实破例。**承诺**：AC + AD 启动时一并 close ≥2 条（候选：Y 已被本次 e2e 覆盖；其他启动时再评估）。→ **2026-05-29 兑现第 1 条（close Y），见下方 2026-05-29 条目**。
- **2026-05-29**: **close Y**（§1 → §3，**close-by-decision**）。理由三条：① Y 质疑的"漏回应率 > 30% → 加警示"阈值已在 [pr-8c-readiness §9](../observations/pr-8c-readiness.md) 撤回；② incomplete 逻辑已单测（休眠安全网）；③ opus 跨模型对照问题被 [Z](#z-fund_mgr-跨模型opus-vs-deepseek对照验证-✅-closed-2026-06-02-close-by-completion) 完全覆盖（Y⊂Z 冗余）。**非 close-by-data**——opus 侧数据仍缺，DeepSeek 0 漏是 Y 创立数据非新证据（我最初误标 by-data，用户纠正为 by-decision）。活跃 20→**19**（超上限 5→4）。= AC/AD 破例承诺"close ≥2"第 **1** 条，第 2 条 = AC 本 PR merge 时 close。**用户决策 X 保持 open**：其 trigger #2「FinalDecision fallback 体系」随 AE/AF/AC-Part2 归一化正在成形，AC Part 2 的 normalize-not-raise 模式正是解 D1 强读的模板——留作 revisit 钩子（本次在 FinalDecision 校验正隔壁干活却未碰 D1 强读，恰证钩子有效）。
- **2026-05-29**: **AC Part 2 落地**（OBEY-5 推广 + decision 三值收敛）。`decision` 收敛 `Literal["BUY","SELL","HOLD"]`（schema before-validator 归一化 ADD→BUY / REDUCE→SELL / AVOID→SELL / 未识别→HOLD，normalize-not-raise 不崩 run）；`check_vote_override` 推广至任意 decision×vote 方向背离（有 `override_justification`→warn 放行，无→coerce HOLD）；frontend 对齐（`ACTION_TONE` 删 ADD/REDUCE 死键 + 测试 fixture 三值化）。详见 AC PR。
- **2026-05-29**: 加条目 **AE**（核心 pipeline 弱模型/瞬时故障健壮性，🟡）。来源：EVID/OBEY/DS-0 验证 e2e 连续 3 崩暴露（rework CancelledError / analyst APIConnectionError / fund_mgr JSONDecodeError "Extra data"）。3 个具体崩溃同会话全修，剩余 debate/vote/ds 解析点系统扫描延后。活跃 17→**18**（超上限 3，第 9 次累计破例）。
- **2026-05-29**: 加条目 **AF**（fund_mgr 输入重构 — DS-0 digest 为主 raw 为 fallback，🟡）。来源：Phase 4 设计讨论，代码 reading 确认 DS-0 三件套中 fund_mgr 只消费 facts_inventory、另两件白产 + 原始全量重复读。前置依赖 [AB](#ab-ds-0-pass0_assistant-在大上下文--慢-llm-下-timeout--fallback-✅-closed-2026-06-01-close-by-completion)。活跃 18→**19**（超上限 4，第 10 次累计破例）。
- **2026-05-29**: 加条目 **AG**（全链路 KV cache / prompt caching 优化，🟡）。来源：Phase 4 讨论顺带记录。与 [AF] 互补（AF 减 token 量，AG 复用前缀）。活跃 19→**20**（超上限 5，第 11 次累计破例）。
- **⚠️ 2026-05-29 §6 漏标修复（2026-06-01 补）**：AE/AF/AG 三条在 2026-05-29 加入 §1 时**未登记 §6**——与 W/X/Y/Z §6 漏标（2026-05-25 audit #2）、AB/AC/AD §0.2 漏标（2026-05-28 audit #3）同模式。**N=3 同类漂移**（三次独立 session 各自漏标），达到 lint 脚本化评估门槛。
- **⚠️ 破例计数修正（2026-06-01）**：2026-05-28 audit #3 止步于"累计 8 次"（Q+R+W+X+Y+Z+AC+AD），未计入 AE/AF/AG。修正后**累计 11 次**（+AE+AF+AG = 第 9/10/11 次）。AE/AF/AG 进入时无用户显式授权破例记录（与 AC/AD 不同），属协议执行失败（同 W/X/Y/Z 模式）。
- **2026-06-01**: **close AC**（§1 → §3，**close-by-completion**）。PR #135 (AC Part 1, merged 2026-05-29) + PR #136 (AC Part 2, merged 2026-06-01) 全部 merge。6 个原始子缺陷覆盖：OBEY-5 vote override + OBEY-6 mitigation-execution + OBEY-7 stale time_horizon（本次新增 warn-only validator，9 测试）+ R1-R6 prompt 硬规则 + cross_check/risk_gate/DATA_INSUFFICIENT/dissent surface。1832 全量回归 PASS。活跃 19→**18**（超上限 3 条）。= AC/AD 破例承诺"close ≥2"的**第 2 条**（第 1 条 = Y close 2026-05-29），承诺兑现。
- **2026-06-01**: **AB 已实现**（DS-0 timeout 15→120s + `COMMITTEE_PASS0_TIMEOUT` env var + HTTP 层 timeout + `_extract_json` raw_decode 对齐 AE#3）。待本 PR merge 后 close。
- **2026-06-01**: **AE 系统扫描完成**（30 个 LLM 输出解析点审计，29 已有防护，1 个 `_plain_invoke` 未保护 → 本次修复）。待本 PR merge 后 close。
- **2026-06-01**: **V 已实现**（B5 per-role mandatory fields：sentiment/commodity/political/historian/economist/fundamentals 各 1 必填字段，warn-only 不 reject，12 测试）。待本 PR merge 后 close。

- **2026-06-02**: **S2.3-gate 收尾 + merge main #139/#140（PR #138）**。本 merge 把 main #139（Backlog batch: AC close + OBEY-7 + AB/AE/V + lint_backlog）+ #140（S4 doc）并入 `auto/AD-evidence-binding`。本会话/分支 close 7 条（close-by-completion）：**V**（B5 per-role 必填集，#139 `rules_b.py` 实现）/ **Z**（opus vs deepseek 对照 e2e）/ **AA**（rework_notes 带反馈重试）/ **AB**（DS-0 timeout 两路：分支 `pass0_parallel` `COMMITTEE_DS_TIMEOUT` + #139 `pass0_node` 120s；⚠️ pass0_node 死代码见 [agent-review-s2.3](agent-review-s2.3.md) A9）/ **AD**（PR #138 AD.1-8）/ **AE**（debate/vote 降级 + #139 `_plain_invoke` 30/30 两路）/ **AF**（fund_mgr 消费 DS-0 digest）。加 3 条（S2.3-gate agent-review，上限内自主新增）：**AH**（LLM token 追踪）/ **AI**（audit 否定半边失效：mismatch/failed 死态）/ **AJ**（DS-0 死输出：cross_role_alignment + watermark 空中楼阁）。活跃 → **14**（< 上限 15）。破例累计 **11** 不变（close 释放配额，非新破例）。§6 漏标修复：AG/I/O（#139 已补）+ AH/AI/AJ（本条）。

- **⚠️ 2026-08-06 §6 漏标批量补登记（15 条·完整 triage 顺带·N=4 同类漂移）**：`scripts/lint_backlog.py` 抓出 15 条在 §1 有 heading 但 §6 从未登记 —— 与历次同模式（2026-05-25 audit #2 的 W/X/Y/Z、2026-05-28 audit #3 的 AB/AC/AD、2026-06-01 补标的 AE/AF/AG），**这是第 4 次**。**根因不是单次疏忽**：§6 登记发生在"加条目"那一刻，而加条目常发生在节点分支跑 e2e / review 的当下，注意力在缺陷本身；lint 脚本 2026-06-02（[#139](https://github.com/JunoChenZt/subagent-for-investment/pull/139)）已入库，但**没有任何环节强制在收口前跑它** → 抓得到、没人跑。以下按立账时间顺序补（内容取自各条目自身"进入时点/来源"字段，不追溯重述）：
  - **2026-06-04**: **AK** 本地证券名录（ticker 校验 + 名称→代码兜底，🔴）→ ✅ MERGED 2026-07-27 [#211](https://github.com/JunoChenZt/subagent-for-investment/pull/211)
  - **2026-06-05**: **AL** 市场感知路由 / degraded 噪声 + 扩基本面（🟡）→ ✅ DONE 2026-07-23 [#199](https://github.com/JunoChenZt/subagent-for-investment/pull/199)+[#203](https://github.com/JunoChenZt/subagent-for-investment/pull/203)（Layer 2 defer）
  - **2026-06-11**: **AN** triage/audit 命名与用户心智错位（dataflow 文档债，🟡）→ ✅ DONE 2026-07-24 [#205](https://github.com/JunoChenZt/subagent-for-investment/pull/205)
  - **2026-07-21**: **AT** 现价锚点可用性 — 取价 retry + fail-fast（🟠）→ ✅ DONE 2026-07-23 [#196](https://github.com/JunoChenZt/subagent-for-investment/pull/196)+[#200](https://github.com/JunoChenZt/subagent-for-investment/pull/200)
  - **2026-07-23**: **AU** Python 版本跨环境 skew（🟡）→ 2026-07-24 RESCOPE 降 🟢（收敛大工程不做·残留=CI 测试版本盲点）
  - **2026-07-24**: **AX** DS-0 `as_of: str` 不收 LLM `null` → node fallback 脆性（🟡）→ ✅ CLOSED 2026-08-03 [#220](https://github.com/JunoChenZt/subagent-for-investment/pull/220)
  - **2026-07-24**: **AY** 中文公司名 → 美股代码无确定性兜底（🟡·AK 收口切出）→ ✅ CLOSED 2026-07-29 [#213](https://github.com/JunoChenZt/subagent-for-investment/pull/213)
  - **2026-07-29**: **AZ** 活文档链接/模板同步小债（🟢·docs-audit [#214](https://github.com/JunoChenZt/subagent-for-investment/pull/214) surface）→ 链接半 ✅ CLOSED 07-29/30，env 半仍未触发
  - **2026-07-29**: **BA** 本地证券名录 DB 未持久化到 volume（🟡·同 docs-audit surface·修法需改 `.env.prod` = 红线）
  - **2026-07-31**: **BB** 段间 checklist ⑧ `audit_passed ≥ 50%` 是空线（🟡）→ ✅ CLOSED 2026-08-03（超原 scope 收口·切出 BF）
  - **2026-07-31**: **BC** 引用锚存在性无人校验（🟠）→ 2026-08-04 BC 探针 e2e 验证「拦不住」**升 🔴**·归属并入 number-provenance-endgame
  - **2026-07-31**: **BD** `_normalize_as_of` 不认英文日期格式（🟢·Serper 切换 surface·已有 Worker 侧绕法）
  - **2026-07-31**: **BE** `evidence_log` 空但正文有带章数字（🟡）→ ✅ CLOSED 2026-08-03（判据改两步判）
  - **2026-08-03**: **BH** `reevaluate_triggers` 四结构化字段恒空（🟡·38 archive / 180 条填充率 0%·[FINDINGS §3.2](../observations/regression-e2e-20260730/FINDINGS.md) 逐条过时实测升级）
  - **2026-08-03**: **BI** wisburg 只取研报标题、全链无人读正文（🟡·[FINDINGS §3.3](../observations/regression-e2e-20260730/FINDINGS.md) 立账）
  - 另：**BF**（⑨ 段价位判据前提不可见·2026-08-03 数字线重校切出）/ **BG**（`.env` 数值项静默架空默认值断言·2026-08-03 [#223](https://github.com/JunoChenZt/subagent-for-investment/pull/223) review 沉淀切出）**是轻条目形态**（只有 §0.2 行、无 §1 正文），一并在此登记。该形态的合法性已于本日在 lint 侧确认（见下条）。

- **2026-08-06**: **完整 triage（逐条过 14 条活跃）+ 三条治理落地**。区别于 2026-08-03 的定向扫，本轮逐条核了每条的触发条件**并额外核了判据本身是否还可能满足**——正是这第二问抓出了下面三条：
  - **close AP**（§1 → **close-by-merge → [BI](#bi-wisburg-只取研报标题全链无人读正文--半句话成了承重数字的依据2026-08-03-全链回归-e2e-findings-33-逐条过时立账)**·保留位置）。触发形式满足（[#226](https://github.com/JunoChenZt/subagent-for-investment/pull/226) 大改 audit 匹配逻辑）但对应修法 B 06-24 已撤、落点 `_extract_ref_id` 又被 #226 删 → audit 侧路已死透。**⚠️ 复核源码确认实质问题（20 篇研报塌成 1 个 `REF#W`）原封不动仍在**，故**不是** close-by-supersede；与 BI 同源同触发同前置调查、且 BI 取正文必然要拆 per-report ref → 并轨。**若当初按 supersede 关掉，会埋掉一个活的登记层缺陷。**
  - **close Q**（§1 → **close-by-decision**·保留位置）。核心半已由 AY 交付（#213·实证「英伟达」→`NVDA`）；剩余半（通用 source-level 引导通路 / 前端 UI 形态 / `degraded_reason` 体系）按 R7 **搬去 [S3 Line C · L-C.4](../roadmap/S3.md)** 并誊过"与其猜不如问"三条方向约束。**close 主因 = 三条触发条件全挂已停跑的 `.3 step6` 数据窗**。
  - **P 触发判据重定为事件型**（原 (a)(c)(e) 及反向条件 (a) 同挂该死信号）。修订史已按 [§4.3](#43-触发条件本身的修改) 落条目内。
  - **新增 [§4.1 判据有效性约束](#41-新增-backlog-条目) + [§4.2 完整 triage 必须问两问](#42-触发条件命中后的处理)**：触发条件（**及反向条件**）只能挂"迟早会撞上的信号"，禁止挂"需要有人主动去查"的信号；完整 triage 除问"触发满足了吗"外必须问"这个触发今天还可能满足吗"，答否按 重定判据 / close-by-decision+剩余写去引用方 / close-by-merge 三档处置。**病根**：P/Q 挂死信号两个半月零评估，不是不该做，是**没人可能发现它该做了**。
  - **活跃 14 → 12**（AP + Q 出场）。上限 15，余 3。破例累计 **11** 不变（close 释放配额，非新破例）。**1 条 🔴**（BC）不变。

- **2026-08-07**: **加条目 BJ + BK**（闸门矩阵机制化的第 1 / 2 层·**均挂起不做**）。来源：[META 观察](../observations/meta-assume-mechanism-without-verify.md)「假设机制生效而不一手验证」实测 **N=8**、越过其自定升级线（N≥5）→ 分层排期，方案落 [gate-matrix-mechanization-2026-08-07](../plans/gate-matrix-mechanization-2026-08-07.md)。**第 0 层已同轮交付**（`check_secrets` 接 CI + `lint_doc_links` 补 27 条自检测试 + 闸门矩阵元测试「沉默 = 失败」），本轮只登记第 1/2 层：**BJ** 🟡 配置/一手来源读取机械化（CFG-READ·S2 §9.2 的 backlog 侧锚点·非重复立项）/ **BK** 🟡 静默降级可见化（产品链路·范围大一档·须独立设计）。
  - **两条触发条件一律事件型**（守本轮刚立的 [§4.1 判据有效性约束](#41-新增-backlog-条目)）—— 不挂"哪天有人想起来量一下"。**这是 §4.1 立规后第一次自我适用。**
  - **⚠️ 如实记账**：第 0 层只闭合 8 个实例里的 **4 个**；另 4 个（CI 红 3 天无人看 / classify 静默降级 / env 读错符号名 / 证据未 durable）分属 BJ、BK，**现在没有被解决**。META 观察的"升级"因此是**部分兑现**，不得读成已完成。
  - **活跃 10 → 12**。上限 15，余 3。破例累计 **11** 不变（新增在上限内·不占破例）。**1 条 🔴**（BC）不变。

- **2026-08-07**: **BH + AU 双 close-by-completion 落账**（两条的修法都已合 main，此前压着等 [#227](https://github.com/JunoChenZt/subagent-for-investment/pull/227) 的 backlog 大改动、避免冲突）。
  - **close BH**（§1 保留位置）——[#228](https://github.com/JunoChenZt/subagent-for-investment/pull/228) `c7306ac`：decision prompt 输出模板由**字符串数组**改成**对象数组** + 新增规范段（复合条件不硬拆、`expires_at` 不反推、🚩 北极星边界写进 prompt 本体）+ `_coerce_triggers` 加固（对象数组后「漏填 `description`」首次可能，而该节点走 bare `model_validate` 无 fallback → 缺了崩整 run）+ 前端 `[object Object]` 渲染缺陷（守护 fixture 停在旧字符串形态 → CI 一路绿）。**⚠️ close 时如实记账**：证到的是「**结构上填得上**」，「**模型真的填**」无任何 e2e 数据（修复后未跑 seg9）；该残留按 [§4.2](#42-触发条件命中后的处理) 第 2 档**写去引用方** = [S4 §6.4 约束 5](../roadmap/S4.md)（判据事件型：trigger watcher 开工前必量，不挂"哪天有人想起来"）。
  - **close AU**（§1 保留位置）——[#229](https://github.com/JunoChenZt/subagent-for-investment/pull/229) `e60c74f`：CI `backend` job 加 `3.10 + 3.11` matrix（地板 + 生产实跑版本双测·`fail-fast: false`）。取 matrix 而非换 3.11 是为不丢 `requires-python=">=3.10"` 的地板覆盖。连带修 `CONTRIBUTING.md` 里那份**待用** ruleset 配方写死的 `{"context": "backend"}`（matrix 后永不上报 + strict 策略 = 将来照贴就是全员永久 pending）。**dev 本地 3.13 明确不覆盖**（非部署目标·加腿属扩界），已写进条目防被读成漏了。
  - **两条条目正文里 close 前的现状诊断一律原样保留**（AU 的「真残留/新 scope」段已加 ⛔ 判据说明标明是修复前形态），只在头部加 ✅ 实现段——**改正文 = 篡改立条理由**。
  - **活跃 12 → 10**。上限 15，余 5。破例累计 **11** 不变。**1 条 🔴**（BC）不变。`lint:active-count` 标记同步改 10。

- **2026-08-10**: **加条目 BL**（🟡·fred 8s 超时线在 8 路并发下余量只剩 1.32×）。来源 = [seg2 C2 并发归因探针](../observations/seg2-c2-probe-2026-08-10.md)，用户拍「先记 backlog」。
  - **🔒 出处分层（本条最要紧的一句）**：BL 来自探针的 **§5 计划外观察**，**不是**探针的事前判据。探针判的是**失败率**，96 次真实调用两臂均零失败 → 判定 **「不结论」**（命中 handoff §4 末行「全绿不算证伪」），**C2 既未坐实也未排除**。判据**没有事后修改** —— 这正是本仓反复吃亏的形态（把"没复现"写成"问题不存在"，或反过来拿计划外读数去改事前判定），故在条目 / 一览表 / banner / 本条**四处都写死了这层区分**。
  - **观察本身**：并发把 fred 从 p50 1.11s 顶到 3.48s、p90 5.34s、**max 6.05s = 占满 8s 线的 76%**（单线程臂仅 28%），**三轮无一例外**（concurrent mean 3.53/3.22/3.22 vs serial 1.10/1.34/1.23）。⇒ playbook §0 统摄假设里「八路确实在抢同一出口」这个**前提事实已坐实**，缺的只是越线那一刻。
  - **为什么是 fred**：膨胀 3.1×（web_search 2.0×）**且**超时线更紧（8s vs 15s），两头夹。反过来说，[#221](https://github.com/JunoChenZt/subagent-for-investment/pull/221) 把 web_search 加宽到 15s **被这组数据事后印证是对的**（余量约 2×）。
  - **不做什么**：候选三方向（限并发·错峰 / fred 带抖动重试 / 加宽 8s 线）**全动主链路须用户裁**，第三条还与 [playbook §8](../plans/seg2-flaky-playbook-20260803.md)「不放宽任何超时线」直接冲突（wisburg 先例：放宽 = 掩盖）；**第四选项 = 什么都不做只观测，在 C2 未坐实前是默认**。本轮**生产代码零改动**。
  - **触发条件全事件型**（守 [§4.1](#41-新增-backlog-条目)）—— §4.1 立规后**第二次自我适用**（首次 = 08-07 BJ/BK）。反向条件亦事件型（改并发编排 / fred 腿重做则本条前提消失或需重测）。
  - **同轮非 backlog 侧产出**：[攒表 seg2-failure-ledger](../observations/bc-anchor-e2e-20260803/seg2-failure-ledger.md) 建成（run1-4 回填 + 五条升级判据现状**全未达线**·当前 N=3）· playbook C2/T1/§6 行 + [handoff](../plans/seg2-c2-probe-handoff-2026-08-07.md) 状态 banner 回填 · DEFECT-SEG2-FLAKY 进展段。
  - **活跃 12 → 13**。上限 15，余 2。破例累计 **11** 不变。**1 条 🔴**（BC）不变。`lint:active-count` 标记同步改 13。旧 08-07 banner 的「⭐ 当前最新」标记**同笔清掉**（该形态此前已三次 stale）。

- **2026-08-11 — AG（prompt caching）close-by-completion + 剥离，活跃 13 → 12**。用户从 backlog 直接点名开工（触发条件「切生产 opus / 成本延迟成约束时」**账面未满足**，用户拍板现在做，已按 [§4.2](#42-触发条件命中后的处理) 记为「现在做」）。三条原修法方向全部有归宿：
  - **① Anthropic 打标记 = 已做**（[`82011fb`](../../src/committee/agents/base.py) `_cacheable_system` 焊进 `_invoke_json` 首发 + 重试两处·三道闸静默降级·9 靶测 + 反向变异）。**默认关**（用户裁决）—— 单次孤立 run 净亏约 $0.021（写入加价 25% 而无人读，因 fund_mgr 两次调用各用一份不同开头指令、前缀第一段即断），跑批量 / 回归时一行 env 打开即赚；实测命中时单次 $0.0835 → $0.0093（降 89%）。
  - **② ③ 自动前缀缓存 / 跨 role 复用 = 实测收益为零，放弃（非暂缓）**。A/B 实验（[ag-prompt-order-ab](../observations/ag-prompt-order-ab/EVIDENCE.md)）：八 analyst 共用段前置后，**各角色首调命中量两臂全为 0、一个不差**；整段命中率 28.9% → 26.3%（微降）。**病根 = 八个 analyst 并行发出**，缓存要生效必须有先后。次要发现：重排后 8 份报告 7 份正文变短、结论分布偏向看多（单跑一对不构成结论，但足证「只换顺序不改字」不等于对产出无影响）。
  - **计划外产出（本条最大价值）**：[AG.1 验尺子](../observations/ag-cache-meter-probe/EVIDENCE.md) 查出缓存**写入量恒记 0** 的真缺陷 —— Anthropic 真值被 `langchain-anthropic==1.5.0` 拆进 `ephemeral_5m_input_tokens`，我们读的 `cache_creation` 恒填 0 → 成本少算 20% + 「标记生没生效」这条判据**永不会响**。已修（[`bd4445d`](../../src/committee/token_usage.py) 两处解析收成单一函数 + 13 靶测 + 反向变异）+ 沉淀进 [坑表 §3.2 形态⑥](workflow/09-known-pitfalls.md)（第 4 个实测·N=7·**新子形态 = 坏在第三方归一层，我们自己的代码逻辑无误**）。
  - **剩余价值剥离出 backlog，不留条目**：真正的大头 = 对齐 fund_mgr 两次调用的开头指令，让那段一万五千词元的共享正文吃到缓存，预估省 **11% 账单**（是①的 7 倍）→ 立为 **[S3 §6.1 COST-FM-PREFIX](../roadmap/S3.md)**（🟢 优先级较后·用户 2026-08-11 裁决）。不留 backlog 的理由：它要动决策环节的调用结构，属 S3 级工程，不是「等条件触发的延后小事」。
  - **R7 连带项**：`AF-residual` 的触发条件原挂在 AG + AH 两条**已 close** 条目上（判据挂死信号·[§4.1](#41-新增-backlog-条目) 禁止形态），已改判为事件型「下次动 `make_decision_node` 的 `user_base` 组装时」。
  - **同轮非 backlog 侧产出**：[坑表 §3.2](workflow/09-known-pitfalls.md) 新增 prompt 排序条（含「并行 fan-out 吃不到共享前缀」这半，**并行是本仓默认写法**）+ 形态⑥ 第 4 实测；[S2 §9.2](../roadmap/S2.md) 登记 `AG.1-冒烟` 延后（触发改为「翻开 `COMMITTEE_PROMPT_CACHE` 时必跑」）；[AG 拆解](../plans/AG-prompt-caching-decomposition.md) 落盘。
  - 上限 15，余 3。破例累计 **11** 不变。**1 条 🔴**（BC）不变。`lint:active-count` 标记同步改 12。

- **2026-08-12 — AG PR [#236](https://github.com/JunoChenZt/subagent-for-investment/pull/236) 已 squash 合入 main `89a440c`**（活跃数不变 12·非 triage·无条目增删）。
  - **⚠️ 读法注解（本条是唯一放置点）**：上方 08-11 记录与 AG 条目正文里引用的 `82011fb`（打标记）/ `bd4445d`（修计量）是**节点分支上的 SHA，squash 后在 main 上不存在**。要找代码以文件链接为准；主干上的唯一提交是 **`89a440c`**。冻结记录按 [Q6](workflow/05-brake-self-check.md) 一字未改，前向事实落在本条。
  - **合并前四道闸**：CI 8 项全绿（跑的是最终 SHA 非旧 SHA）·`MERGEABLE`/`CLEAN`·本地全量 **3292 passed / 2 skipped / 2 xfailed**·账本与链接 lint 均过。合并由用户显式指示（[git-workflow §4.7](git-workflow.md) 「Claude 不主动执行」= 防自作主张，非禁止照指示执行）。
  - **合并前补跑正式冷审（`/review`），4 条 finding 全部落地**（均在 #236 内）：
    - 🔴 **①「默认关 = 行为不变」那把测试锁是空的** —— 假 LLM 不是 `ChatAnthropic` 实例，而实例类型闸排在开关判断**之前** → 开关开没开结果一样。实测 `COMMITTEE_PROMPT_CACHE=1` 跑全量 **3284 passed 与关掉时逐字相同**，无一条变红。**而这把锁正是 [S2 §9.2](../roadmap/S2.md) `AG-冒烟` 延后论证的依据** → 依据当时是空的，锁修好后论证才成立。修法 = 真 `ChatAnthropic` 子类 fixture + 显式钉死开关，另补一条「开关开时标记真的送到 LLM 手里」守接缝（原两条 spy 测试只证明 helper 被调用）。
    - 🟡 ② **1 小时 TTL 缓存写入按 5 分钟档计价**（官方倍率 5m ×1.25 / **1h ×2** / 读 ×0.1，2026-08-12 复核）→ 少算 60%。当前不可达（生产不带 ttl）但探针脚本已支持传参、路是通的；**少算方向与「写入量恒记 0」同源，属同一坏法的另一半**，故提前堵。费率表按档分填 + 返回值升 `CacheTokens(read, creation, creation_1h)`，`creation` 仍是合计 → `TokenRecord` / 归档结构**零变化**；元组解包 2→3 元会当场 `ValueError`，杜绝某处静默留旧口径。
    - 🟡 ③ 长度粗筛注释的字符/词元换算比是估的且不准 → `count_tokens` 实测（免费接口）本仓 prompt **0.65–0.76**、纯中文 ~1.07、生僻字 ~2.65、纯英文 ~0.35 → 这道筛对本仓**偏松非偏紧**，**门槛 2048 保持不动**（唯一够格的定稿指令 7,236 字符 / 5,513 词元，离门槛很远）。
    - 🟢 ④ 上述实测只在代码注释里、归档缺一手记录 → 补 [AG.1 EVIDENCE §9](../observations/ag-cache-meter-probe/EVIDENCE.md)，1–8 节正文不动、§1 加前向补注。
  - **靶测 22 → 30 条**（AG.1 计量 20 + AG.2 标记 10）；**反向变异 2 → 4 组**全部实测变红。
  - **教训（observe·N=1·未升级）**：「反向变异做了两次」不等于「都做了」—— 漏做的那条恰好是被拿来当 DoD 论证依据的那条。**判据被引用得越重，越该先证明它会红。** 与坑表 §3.2 形态⑥防御 (a') 同源，属其**覆盖率**维度的补充（(a') 说「要做变异」，没说「哪条最该做」）。
  - **未变更**：默认仍 `COMMITTEE_PROMPT_CACHE=0`（生产行为与合并前逐字节相同）·`AG-冒烟` 仍事件型延后（触发条件不变）·活跃条目仍 12·破例累计仍 11。

- **2026-08-13 — close BF（两件全做·close-by-completion），活跃 12 → 11**。用户从 backlog 点名开工 BF（触发条件「下次动 `trace_report.py` / 价位门相关改动时顺手」账面未满足，用户拍板现在做，按 [§4.2](#42-触发条件命中后的处理) 记为「现在做」）。流程：opus5 探索 → fable 出 plan → 用户批 + 裁决冒烟替代 → opus5 执行。
  - **第 1 件（本条的实质）**：⑨ 段两条价位判据的前提**从不打印** —— fm 这一跑到底有没有把价位填进结构化字段。前提不成立时判据恒真 = **静默空过**，打勾打了两个月其实一次没真验过。现在决策摘要多一行，三个价位字段各自的状态一目了然，前提不成立时明写「判『本跑无效』而非 PASS」（与 guide ⑨ 段 D2 同口径，两边对得上）。
  - 🔬 **冷审收严：两态 → 三态（PR #238 `/code-review` 捞出·差点又造一个空过）**：初版判据是「价位**对象**在不在」。但三个价位模型的数字字段全是 Optional（`note` 必填），且价位门控在 ungrounded run 上**只抹数字、留对象** —— 而「无 strip」那条判据要抓的恰恰是这个形态。实测：19 份 tracked 归档里 **2 份**长这样（`enforcement_log` 里 `strip_level` 各 5 处 / 4 处为证），初版会印成「前提成立，可读价位判据」而实际零个价位数字 = **换个更窄的形态把空过又造回来**。修法：判定下沉到 `low`/`high`/`level` 值那一层，并把「填了但数字被抹」单列**第三态**，读得到 `enforcement_log` 时直接点名门控 + 给出处数、读不到就如实写「分不清」。**「压根没给价位」和「给了被门控拿掉」必须分开**——前者判本跑无效，后者是「无 strip」判 ❌，下一步动作完全不同。顺带订正：价位靶测初版的止损/止盈样本把数字字段写成了 `price`（真名 `level`）**而测试照样全绿**，正是"判到容器为止"的代价。
  - **第 2 件（同根·一行）**：拓扑图按段成员染色、不读实际执行，图例却写「本段执行」。改「本段涉及（按段成员染色·非实际执行）」，并在染色函数补注**防下一个人改回去**。**贵修法（从 checkpoint 反推真实执行集）不做**，将来要画「实然」按 §4.1 另立事件型条目。
  - **冒烟以离线回放替代（用户当日裁决同意·记账留痕）**：DoD [§2.8.3](workflow/06-dod-and-evidence.md) 字面要求真跑一次 e2e。本改动**不经任何 LLM 调用路径**，真跑零增量判别力、纯烧钱 → 按刹车 [Q5](workflow/05-brake-self-check.md)「不自行免判」显式上升用户裁决，用户拍「离线重渲染替代」。执行 = 19 份 `origin/main` tracked 的 ⑨ 段 checkpoint 重渲染（**R6：不读工作树**；CJK 目录名两份靠 `quotepath=false` + 读失败显式炸才没被静默跳过）。三形态**全部有真实样本命中**（没填 11 = 无计划 4 + 三字段无对象 7 / 填了 6 / 填了但数字被抹 2），交叉断言 **19/19** 过〔**收严前的旧分档**为「无计划 4 / 全空 7 / 部分填 3 / 全填 5」，那 8 份"填了"里其实混着 2 份空壳〕。⚠️ **已知阳性样本**：没填那 11 份 + 空壳那 2 份确实印出了不按 PASS 读的措辞 ——**信号会响**，不是「跑一次是绿的就算数」。
  - 🚩 **先堵自伤再 close（顺序被写死）**：backlog linter 的三条轻条目守护**锚在 BF 这一行**上 —— BF 一 close 就退出活跃集，两条的变异不再产 finding（真红）、第三条变成「断言一行已不被检查的行没被报错」（**空转**）。同型事故 2026-08-06 关 BH 时刚踩过，教训写在 `test_entry_that_loses_its_body_is_flagged` 的 docstring 里。本笔照该写法改锚成合成 fixture + control/fires 双断言，**再**动 backlog。**这是「修一个空过别造一个新空过」的直接自我适用**。
  - **计划外坐实的数（不覆盖旧数·口径不同）**：19 份历史归档里 **11 份（58%）`entry` 对象为 null**；按收严后的「`entry` 没有真数字」口径是 **15 份（79%）**。BF 立账记的是「11 次 run 里 10 次」= 91%，那批是**同期正常 run**，本次样本跨 2026-06→08 全部归档含大量专项实验跑。**三个数不冲突、也不互相推翻**，都指向同一结论：前提不成立是常态。
  - **承重边界未变**：不动 e2e-quality-gate 任何代码、不新增自动检查、fail 面零变化 → [acceptance-standard §4](e2e-acceptance-standard.md)「新检查一律 WARN 试用」不适用（同 BB/BE 数字线重校、S6 收窄两个先例），只在该文件把「建议 3 未落地」补记为已落地。guide ⑨ 段判据本身**一字未改**。
  - **活跃 12 → 11**。上限 15，余 4。破例累计 **11** 不变。**1 条 🔴**（BC）不变。`lint:active-count` 标记同步改 11。旧 08-12 第二笔 banner 的「⭐ 当前最新」标记**同笔清掉**（该形态此前已五次 stale·Check 8 管日期不管归属）。

- **2026-08-12（同日第二笔）— close AZ（两半皆完）+ BA 前提订正（不 close），活跃 12 → 11**。用户从 backlog 点名开工 BA（触发条件「下次 prod 部署 / config review」账面未满足，用户拍板现在做，按 [§4.2](#42-触发条件命中后的处理) 记为「现在做」）。走完整流程：fable 出大纲 → 用户批 → fable 出 [完整 plan](../plans/BA-registry-volume-decomposition.md) → 用户批 4 项裁决全「是」→ opus5 执行。
  - **🔴 执行中前提被推翻（本笔最重要的一件事）**：plan 第一步是在生产上跑三条只读诊断坐实现象。用户回「服务器上是**旧的 S1**，现在在做 S2」→ **BA 原措辞「生产每次重建镜像清零」是现在进行时，不成立**：名录功能（AK [#211](https://github.com/JunoChenZt/subagent-for-investment/pull/211)）属 S2、**从未部署**，该浪费**尚未发生**。机理断言逐条复核**全部仍成立**（`default_db_path` / `WORKDIR /app` / compose 只挂 `backend_data:/data` / lifespan best-effort prewarm）——**错的只是时态**，不是机理。
  - **发现路径值得记**：不是读码读出来的，是**准备把命令递给用户执行时**撞出来的。此前 docs-audit 静态核了两轮都没发现，因为静态核只能验「代码是不是这样」，验不了「这份代码在不在线上」。
  - **BA 处置 = 预防已落 + 不 close**：[.env.prod.example](../../.env.prod.example) 加 `COMMITTEE_REGISTRY_DB=/data/security_registry.db`（与 auth DB 同 volume）→ 将来按 runbook `cp` 建新环境**开箱即修好**；但服务器上已存在的 `.env.prod` 是历史文件、**不会自动获得该行**，S2 首部署时须手动补（红线·用户手动）。触发条件由「下次 prod 部署 / config review」**收窄为「S2 首次部署时」**，并写死 close 判据 = 重建验证四条全过。**不 close 的理由**：修法备好 ≠ 问题解决，生产从未验证、当前 S1 环境跑不出该现象；拿「模板改好了」当「已验证」直接撞刹车 [Q5](workflow/05-brake-self-check.md)（标准降低）。
  - **close AZ（close-by-completion·两半皆完）**：链接半 07-29/30 已完（08-12 复扫 root-relative **0 处**确认未复发）；**env 半随本轮做完** —— [.env.example](../../.env.example) 补 6 键（`COMMITTEE_REGISTRY_*`×5 + `COMMITTEE_CLASSIFY_TIMEOUT`）。⚠️ 注意是 **6 键不是 5 键**：用户口头裁决说的是「五个 `COMMITTEE_REGISTRY_*`」，但 AZ 正文登记的 env 半含第六个 `COMMITTEE_CLASSIFY_TIMEOUT` —— 只补五个则 AZ **不能诚实 close**，故 plan 阶段就把这点显式提给用户、用户拍「6 个一起补」。
  - **BG 触发动作已执行（非跳过·这是 BG 立规后第一次真被消费）**：grep 实查坐实 `COMMITTEE_REGISTRY_REFRESH_HOUR` **站在雷上** —— [test_security_registry_scheduler.py:52](../../tests/test_security_registry_scheduler.py#L52) 直断 `REFRESH_HOUR == 2`，而 [config.py:16](../../src/committee/config.py#L16) 在 import 时 `load_dotenv()` 读本机 `.env` → 一旦有人取消注释并改值，守护测试会**红得像代码坏了**。∴ 6 键**一律登记为注释行**，且把这个理由**写进模板注释本身**（不只写进 backlog），避免下一个人顺手取消注释。其余 5 键实查安全（3 键被 conftest 钉死、`LAZY_BUDGET` 无人断言、`CLASSIFY_TIMEOUT` 相关测试当年已 `delenv` 加固）。**BG 本身是常设触发型条目，不随 AZ close**。
  - 🚩 **计划外发现（未处理·登记待裁·不在本轮 scope 内自行扩界）**：「线上跑的是旧 S1」这条事实**全仓无处记载**，而 [prod-runbook](../infrastructure/prod-runbook.md) 通篇按「线上 ≈ main」写（含线上拓扑、事故复盘、第 5 节线上待办清单），另有条目（如 advisory 模型 override drift）按「现存环境」写生产待办。⇒ **凡是断言「生产现在如何」的条目/文档都可能同样失真**，且这类失真**静态审计查不出来**。是否立正式条目做一轮「生产现状 vs 文档断言」对账，待用户裁决。〔按 [treat-scope-no-creep](../../CLAUDE.md) 不自行扩界：本轮只登记，不顺手改 runbook。〕
  - 加 **BM** 🟡（用户当场拍「立一条做生产现状对账」·同笔）—— 本轮撞出的**类**问题：仓库里凡断言「生产现在如何」的地方都没对过账，已确认失真 1 处（BA 原措辞）。**立独立条目而非并进 BA 的理由**：BA 是实例、BM 是类；BA 已按事实订正完毕，但「凡断言生产现状的地方都可能同样失真」不随 BA 解决，且两者处置手段完全不同（改 env + 验证 vs 对账 + 标注）。候选三条不预设，其中 ③「runbook 顶部标线上环境版本」最便宜且最治本——**BA 这个错，只要手册顶上有一行「线上 = S1」就不会发生**。触发条件全事件型（§4.1 立规后第三次自我适用·前两次 = 08-07 BJ/BK、08-10 BL）。
  - **活跃 12 → 11 → 12**（close AZ 减一、加 BM 加一·净不变）。上限 15，余 3。破例累计 **11** 不变。**1 条 🔴**（BC）不变。`lint:active-count` 标记同步改 12。旧 08-12 第一笔 banner 的「⭐ 当前最新」标记**同笔清掉**（该形态此前已四次 stale·Check 8 已立规管日期，标记归属仍靠人手）。
  - **未变更**：破例累计仍 11 · 🔴 仍 1 条（BC）· 生产环境**零接触**（红线全程未碰，`.env.prod` 一字未改）· 生产代码零改动（改动仅 2 个配置模板 + backlog + plan 文档）。

- **2026-08-13（同日第二笔）— close BG（close-by-completion·修法落地），活跃 11 → 10**。用户从 backlog 点名开工（账面触发条件「往 `.env`/`.env.example` 加数值项时」未满足 —— 当时是**用户先提出 BG/BD 两条是否该优先做**，执行体原排序把两条都按「未触发」压后，经复核后**同意 BG 该先做、并给出比用户更强的理由**：该触发条件 08-12 刚真响过一次。BD 则明确**不做**：归一逻辑现由 Worker 侧承担且有 34 用例自测，此刻搬回本仓 = 同一件事两份实现，是净负债，等它自己的触发条件响再做）。
  - **本条修的是「保障强度取决于当事人记性」**：`config.py` import 时 `load_dotenv()`，故 `.env` 里某键的值一旦**恰好等于**代码默认值，`assert SYMBOL == <默认值>` 这类断言就从「验代码」变成「验本机配置」——**且不报红**。值不同才会当场变红（吵但看得见）。原触发条件「加数值项时先 grep」把这道防线整个挂在人的记性上。
  - 🚩 **开工第一步就推翻了条目自己记的暴露面（三处·机器扫 vs 当时人工扫）**：① 原 ①②③ 清单是在**只扫 `config.py`** 的前提下得出的，而危险键**不全住在那儿**（`REFRESH_HOUR` 在 [security_registry/service.py](../../src/committee/security_registry/service.py)）；② 原判「靠运气绿」的 `MAX_TOKENS` **其实是安全的那个**（模板 8192 ≠ 默认 4096 → 取消注释会变红）；③ **真正踩雷的两个恰是 08-12 当天刚加进模板的** —— `COMMITTEE_CLASSIFY_TIMEOUT`（值 15 = 默认值，压着 **3 条**断言）与 `COMMITTEE_REGISTRY_REFRESH_HOUR`（`2` vs `2.0`，**纯字符串比会漏**），而 08-12 记录里只写了查过后者。⇒ 全 `src/` 扫：**7 个符号断言了代码默认值，其中 4 个踩雷**。**教训与 BF 同形**：判据写下来后没人验过它在真阳性面前会不会响，这次是「扫描范围悄悄小于危险范围」。
  - **修法 = 候选 1+2 合做，候选 3 明拍不做**（三条候选见条目正文）。规则 1 管「已经生效的雷」（`.env.example` **与本机 `.env`** 都扫）；规则 2 管「进了模板就必须留警示」——注释态**不报错**（没生效）但**必须带注记**，让下一个来取消注释的人当场看见。候选 3「改 7 处既有断言的取值源」不做：机器已能在失守当天喊出来，动既有断言的风险不划算。
  - **豁免表自带防锈**：`ALLOW` 条目若已不是真实的雷即报错 —— 否则豁免表会变坟场，把将来真的复发一并罩住。今日仅 1 条（`MIN_CHARS_DEBATE`·早有明文分工，理由写在脚本里）。
  - 🔬 **冷审（`/code-review`）在检查器自己身上挖出同一个病 —— 本笔最值得记的一件事**：初版**手写正则去猜 `.env` 的加载语义**，与运行时那个库差了四处，**四处全是静默漏报**（检查器报干净、雷还在）：① 同键写两次时靠后的注释行盖掉靠前的生效行（`.env.example` 里本就有 **13 个**重复键，前提非假想）；② 值带引号不脱引号 → **加个引号就能绕过检查**（本机 `.env` 第 3 行就在用带引号的值）；③ 不认 `export KEY=value`（dotenv 支持的写法）→ 整行解析不出来、两条规则同时失灵；④ 收集符号按裸名入字典 → 同名常量后者静默吃掉前者，断言遂与**错误的 env 键**比对。**教训一句话：不要手写解析器去猜另一个系统的语义 —— 那个系统就在手边，直接问它。**
  - **修法 = 取值口径与运行时同源**：规则 1 一律走 `dotenv.dotenv_values`；规则 2 保留自家正则但降级职责（只答「出现过没有、在第几行」，因为 `dotenv_values` 不报注释行也不报行号），同时补齐引号 / `export` 且同键多次出现全部记录、改为**逐处**要警示；符号重名**当场报错 + 每个候选都查**（宁可吵，不可静默）；`dotenv` import 失败**直接退出**不提供「退回自家正则」兜底。**代价如实记**：该 CI job 因此**不再是纯 stdlib**（多一步 `pip install python-dotenv`·本就是项目依赖·仍秒级），且报错行号只能尽力回填（dotenv 不吐行号·已在信息里标明）。
  - **验证**：**35 条**自检测试（合成 fixture·**不锚真实文件的具体行** —— 照 BF 当日刚踩的那个教训写；含四个 finding 各自的回归锁 + 取值口径直钉 + 对照组）+ **12 个变异全部被杀**（三规则 / 两防锈 / 数值等价 / 本机 `.env` / 包一层解析 + 本轮四个洞各自的回退变异）+ 全套件 **3349 passed / 0 失败**。⚠️ **变异当场抓到一条「靠错误理由通过」的用例**：重名那条原本只断言「文字里出现了 B 键」，而重名告警本身就会列出两个候选的键名 → 在「只查第一个候选」的变异下照样绿，已收紧成钉在规则 1 的 finding 上。**这正是变异验证的价值所在：用例数变多不等于覆盖变强。**
  - **计划外**：新脚本刚落地就被 08-07 立的**闸门矩阵**（`test_gate_matrix.py`）逮住「未接进 CI」→ 补 `env-shadowing-lint` job。**那个机制按设计工作了**，值得记一笔：它是 META 观察「假设机制生效而不一手验证」的第 0 层交付物，这是它第一次抓到新增闸门。
  - **边界如实写（不许读成"这条路全守住了"）**：不追派生链（env → 原始串 → 派生符号）；CI 上没有 `.env`，本机那半靠开发者本地跑测试才触发；坑表 [§3.2](workflow/09-known-pitfalls.md) 该条的防御 (a)(b)(d) **仍靠人**，只有形态 ② 有机器守 —— 已就地标注。
  - **活跃 11 → 10**。上限 15，余 5。破例累计 **11** 不变。**1 条 🔴**（BC）不变。`lint:active-count` 标记同步改 10。旧 08-13 第一笔 banner 的「⭐ 当前最新」标记**同笔清掉**（该形态此前已五次 stale）。

- **2026-08-14**: **加条目 BN**（🟡·投票同构：同向票理由重合、`conviction` 零方差）。来源 = BC 收官两跑之一的[宏观黄金跑](../observations/bc-final-e2e-20260814/run-gold-macro-20260814/) seg7，用户拍板立。
  - **🔒 立它的第一理由是判据本身，不是这条观察**：[段式跑批指南 ⑦ 段](../observations/e2e-runs/segmented-e2e-guide.md)的观察点**开跑前就写死**「再出现一次（N≥3）→ 提立 backlog 条目」；2026-08-04 用户裁「先并入观察点」时 N=2，本跑复现 → **N=3**。**事前写死的规则到线不执行 = 判据形同虚设**，那比这条观察本身更伤——本仓已因「空线 / 空过」吃过多次亏（[BB](#bb-段间-checklist-⑧-的-audit_passed--50-是空线五次-run-全-6132026-07-31-全链回归-e2e-surface)·BF〔轻条目·见 §0.2 表〕），形态都是「判据在那儿，但没人按它动作」。
  - **趋势向坏，不是平稳复现**：同构范围从「仅 NEUTRAL」扩到「NEUTRAL + BULLISH」；本跑 10 票里 **8 票 `conviction` = 6**，看多 3 张与观望 4 张**各自方差为 0**，六个关键词四票全中。唯二离群 = 天然对立的 bear(8) 与**主动弃权**的 fundamentals(1)（「非个股查询·不具备投票依据」—— 顺带记一笔：**诚实出口在这一跑正常工作**）。
  - **方向仍安全 → 记 🟡 不急修**：三次同构全落在保守侧，无「十票齐看错方向」实例；票型方向三次都与辩论内容对得上（⑦ 段 D4 每次都过）。本条问的是**独立性**，不是安全性。**升 🟠 条件已写死**：再出现一次同构且方向不再保守。
  - 🚩 **立条目不改任何放行闸**：⑦ 段该项仍是 🔬 观察点（不判 ❌）。照 [acceptance-standard §4](e2e-acceptance-standard.md)，提高 fail 面须用户裁 —— **立账 ≠ 收紧**。
  - **候选处置排序刻意是「先量再修」**：① 把「同向票方差 + 关键词重合率」做成跑批自动读数（现在靠人每次手数）；② 同一 seg6 checkpoint 跑两次 seg7、一次抽掉辩论摘要作对照（**真能证伪「摘要过于强势」那个假设**）；③ 动输入配比 —— 假设未证前不做，那是猜着修。**明确排除**「强制票型分散」：人造分歧 = 拿表象换多样性，比现状更坏。
  - **活跃 10 → 11**。上限 15，余 4。破例累计 **11** 不变（新增在上限内·不占破例）。**1 条 🔴**（BC）不变。`lint:active-count` 标记同步改 11。旧 08-14 第一笔 banner 的「⭐ 当前最新」标记**同笔清掉**（该形态此前已六次 stale）。

- **2026-08-14（同日第三笔）**: **🎉「数字出处」问题域封卷 —— close BC + DEFECT-ANCHOR-MISBIND**（用户拍「封卷吧，走 R7 收口」）。
  - **六条判据全达成**：D1 ✅ 连续 3 次最高信任档零错绑（抽查 #1 = 08-05 执法跑 · #2/#3 = [BC 收官两跑](../observations/bc-final-e2e-20260814/FINDINGS.md)）· D2 ✅ · D3 ✅ · D4 ✅ · **D5 ✅** · D6 ✅。真值源 [endgame](number-provenance-endgame.md) 顶部已立 DONE banner，§1 判据表 / §4 缺口清单 / §5 处置表 / §6 顺序均已落地。
  - **close BC**（lettered·活跃 11→**10**）+ **close DEFECT-ANCHOR-MISBIND**（DEFECT 族不占配额·本域主条目）⇒ **§0.2 自 2026-08-04 以来唯一的活跃 🔴 消失，全仓 🔴 归零**。
  - 🔒 **close 理由写死在两条目头部 + banner + endgame 顶部（四处一致）**：close 的是「**本域判据已达成**」，**不是**「编造出处解决了」。该形态 08-14 **第三次自然复现且手法更宽**（首次空头侧 / 首次编外源数字章 / **凭空造命名空间**而非续编号 ⇒ BC 原记的「同一编号策略」被推翻），**至今没被任何一道门拦过**。两条同族新形态（实体归属无人核 / 判别力方向反了）已记 FINDINGS，**本域刻意不接·要治须重新立项**。
  - **R7 四步收口如实记账**：① 宽 grep 扫 11 个关键词（含别名「拦不住」「错绑」「信任反转」「misbind」）覆盖全仓；② 分档 —— live 就地改（[e2e-acceptance-standard](e2e-acceptance-standard.md) 1 处 · [段式指南](../observations/e2e-runs/segmented-e2e-guide.md) 3 处）/ 规划文档加前向 banner（2 份）/ **已 close 条目正文与节点 retro 属 [Q6 冻结档](workflow/05-brake-self-check.md)一字未动**；③ 连带项（§6 本笔 · MEMORY 索引 · 计数标记）；④ 复扫。
  - ⚠️ **收口当场踩到昨天刚清完的那个坑**：给 MISBIND 标题追加 `✅ CLOSED` 后缀 → **5 条页内锚点当场变死链**，被昨天上线的锚点检查逮住。修的时候**我又去猜 slug 规则、猜错一次**——正确做法是**问扫描器自己的函数**（`heading_slugs()` 直接吐真锚点集）。**「先在已知答案上校准」这条昨天写下的教训，今天自己第一个违反。**
  - **D5 复扫的意外收获**：当日新写 342 行文档**表内规范词命中 0**、旧称「水印」×10「锚」×10、另**自造「记号」×13** —— 正是该判据要防的两件事，**第一个违反者就是刚写完它的人**。已按 §2 词汇表改到达标。

- **2026-08-18（第一笔·只加不关）**: **① 段引用时效判据由「一刀切超 3 天」改按来源分档 + 加 BO / BP**（用户在 seg1 提示词检阅途中拍「看一下引用数据的问题·开个新分支」）。
  - **先量后改**：[14 份 `origin/main` tracked seg1 checkpoint · 104 条 reference 实测](../observations/ref-freshness-asof-20260818.md)（R6·零网络可复现）。**读数**：`rss` 26/26 恒 **0 天** · `tushare` 0–1 · `yfinance` 0–**4** · `fred` **44–53** · `wisburg` 28/28 **全空**。
  - 🔑 **旧线定性 —— 不是空线，是指错方向的线**：76 条有效样本 **10 条越线（13%）**，逐条拆开**真阳性 0 条** —— 6 条 `fred` 是月度节律（**3 天线对月度数据物理上不可能满足**）、4 条 `yfinance` 是长周末（[07-06](../observations/m1-t11-e2e/run-nvda-20260706/) **周一**跑·07-03 独立日休市）。**它每次响都说「数据旧了」，实际说的是「今天周一」或「这是月度数据」。**〔与 BB 空线的区别写死在此：空线是**每次都响**，本条是**响得不对**〕
  - **而真正没人管的那头**：27% 的引用（`wisburg` 全部）**没有时间戳** —— 既不算越线也不算通过，**静默溜过**。新档把它标出来，只计数不判红（**空 ≠ 旧**）。
  - **新判据**：新闻 2 天 / 美港股 6 天 / A 股 10 天 / 宏观月度超 **80 天**〔⚠️ 同日第二笔改：初版写「不判天数改判『是不是最新一期』」，冷审发现**现场判不动**（审核现场查不了发布日历）→ 换成按发布节律算术定的 80 天线，见下方第二笔〕/ 无时间戳单独标注 / **未来日期·非法格式单独一档 → 排查数据源**（本批 0 例，但那才是「源真坏了」的形态）。**判红面零变化**（本判据从来只提醒不阻断），故不走 §4 WARN 试用闸（同 BB / BE / BF 先例）；⚠️ **提醒面有得有失** —— 见下条余量说明。已在 [acceptance-standard §4](e2e-acceptance-standard.md) 登记 + 演进历史表落一行。
  - ⚠️ **两处余量是刻意的，别当放松读**：A 股实测上限只有 **1 天**、线却定 **10 天** —— **本批 14 份无一跑在春节 / 国庆长假**（休市 7–9 天），**拿实测上限当天花板，下一个长假必然误报**。美港股同理（实测 4 = 独立日 → 定 6 盖圣诞元旦）。这是**样本未覆盖**，不是判据放松。
  - **加 BO + BP**（均挂起不做·触发条件一律事件型·守 §4.1）：**BO**🟡 `other = 400 天` 是五档窗口里**唯一无论证**的（注释仅「放宽」二字）而**全部外源落此档**；**BP**🟢 seg1 引用 `as_of` **全程无代码消费**（审核环节全文 `as_of` 零出现）⇒ 那行人工判据是它唯一的守卫。
  - **R7 四步收口**：① 宽 grep 扫「超 3 天 / as_of 超 / stale warning / ② 档」；② 分档 —— **live 两处就地改**（指南「② 档未校准清单」+ 标准同句同步摘除本条）· **历史两处不动**（`baseline-scratch` 的 06-16 guide 快照 / BF EVIDENCE 里**同名不同物**的「② 档」= 价位三态，**差点误改**）；③ 连带（本笔 §6 · banner · 计数标记）；④ 复扫，残留只剩登记条里引用旧判据原文。
  - **顺带记一条工具行为**（省下次排查）：`lint_doc_links` 在新建文档**未入库**时按设计报死链 —— 它的**存在性判定用 git index 而非文件系统**，为的是「本地结论 == CI 结论」。`git add` 后即全绿，**不是误报**。
  - **活跃 10 → 12**。上限 15，余 3。破例累计 **11** 不变（新增在上限内·不占破例）。**🔴 仍 0 条**。`lint:active-count` 标记同步改 12。旧 08-14 第三笔 banner 的「⭐ 当前最新」标记**同笔清掉**（该形态此前已六次 stale）。

- **2026-08-18（同日第二笔·冷审补 3 处 + 加 BQ）**: 对 PR #244 / #245 的冷审（9 finding）当日消化，落 4 件事。
  - **宏观档改判法**：初版「不判天数改判『是不是最新一期』」被冷审证伪 —— 段间审核现场只看得到 series_id / 数值 / 日期，**查不了发布日历，判不动**，等于把「响得不对」换成「不会响」（宏观恰是旧线唯一持续响的组 + BP 已确认无代码在看）。改成**超 80 天 → warn**：`as_of` = 数据月首日、发布滞后约一个半月、到下一期出来前最旧 ~74 天 ⇒ 80 = 节律上限 + 余量；正常节奏永不越线，**真卡在旧一期上会随时间自己越线**——这才是该档要抓的形态。仅适用月度系列，接季度系列须另定档。
  - **加表外来源兜底档**：分档表只列现有五源，新源（BO 触发条件之一就是「接第二个搜索后端」）的引用会**既不越线也不通过、静默溜过** = wisburg 那 27% 的病在新源重演。补一行「表外来源 → 标注『未定档』、计数不判红、触发定档」。
  - **实测文档补独立观测口径**：104 条是**字段条数**，同一次取数的多个字段共享同一时间戳；按 (跑批, 时间戳) 去重后**非空独立观测仅 26 个**（A 股 4 · 宏观 2），越线独立观测 **3 个**非 10 条。结论方向不变，但**支撑度此前被高估约 2.6 倍**——「A 股实测上限 1 天」背后只有 4 次取数。连带把「新闻永远是当天的」这句绝对化断言改掉（同日另一跑批实测 rss = 1 天，当场证伪）。
  - **加 BQ**🟡（资产类行情腿·见 §0.2 表行与 banner）+ ② 段「as_of 超一周」行加宏观对齐括注（同一批时间戳不能 ① 段放行、② 段判旧）。
  - **活跃 12 → 13**。上限 15，余 2。破例累计 **11** 不变。**🔴 仍 0 条**。`lint:active-count` 同步改 13。

- **2026-08-18（同日第三笔·立 DEFECT-FRED-SUBSTRING·活跃数不变）**: 宏观关键词子串匹配的中文假阳性 —— 问「毛利率」拿到「联邦基金利率」。
  - **怎么撞见的（值得记）**：在 [#246](https://github.com/JunoChenZt/subagent-for-investment/pull/246) 给新加的宏观安全网写**反证测试**（「不含宏观词的标的型 query 不该激活 fred」），负例随手挑了「茅台三季度毛利率怎么样」→ **当场红**。「毛**利率**」含「利率」，而关键词是按子串认的。⇒ **反证测试的价值不只是防回归，它当场证伪了我对匹配语义的默认假设**。
  - **一手坐实非推断**：`_resolve_series("茅台三季度毛利率怎么样")` 返回 `FEDFUNDS`（`净利率`同）。老暴露面 = fred 自己的取数（主题型 query 问财务比率 → 宏观维拿错指标）；新暴露面 = #246 的安全网继承同一张表（误开火多拉一个源·**方向安全**）。
  - **🔒 R5 边界照 DEFECT-FRED-KEYWORD 原样守**：子串匹配是**设计**（源文件注释 + TODO 写死），缺陷在**中文词的包含关系没被考虑**。两条同表同族、**互补**：那条治「该认的没认出」，本条治「不该认的认了」。
  - **#246 不修的理由 + 处置**：修它 = 改 fred 主路径 series 解析，超出「只加一条不减源的安全网」的边界 → 该 PR 只**用测试钉住假阳性现状**（匹配语义一变即红），缺陷另立条目。**用户拍「另立条目」。**
  - **配额**：DEFECT 族不占 lettered 配额 → **活跃数不变**（仍 13），`lint:active-count` 不动。**🔴 仍 0 条**。

- **2026-08-18（同日第四笔·只加不关·⚠️ 配额用满）**: seg1 **外部取数质量**实测 → 加 **BR** + **BS**（用户裁「②⑤ 单独立 · ① 顺手补 · ③④ 并进 ⑤」）。
  - **怎么来的**：#244/#245 合并后用户问「seg1 除了分类还从外部拉什么、质量如何、怎么问的、怎么处理的」→ 把黄金跑拉回的 **31 条外部信息逐条读了一遍**（非抽样）。⚠️ **口径先说清**：31 = **信息条目数**（1 个宏观指标 + 10 条新闻标题 + 20 篇研报标题），与引用清单 **7 条**（按字段拆·`series_id`/`unit`/`value` 各占一条）**不是同一个数** —— 守同日第二笔冷审刚给出的「104 条 ≠ 26 个独立观测」教训，**先说清口径再用数**。
  - 🔑 **三种源三种提问方式，只有一种真把问题带出去了**：**新闻根本不带 query**（两个写死订阅源：MarketWatch 头条 + 谷歌新闻搜 `financial markets`）· **宏观拿 query 撞关键词表**（撞不上落默认）· **研报唯一把 query 原样传给 MCP**。
  - **实测相关率 32%**（10/31）：宏观 1 条 **0 相关**（问黄金拿回 `CPIAUCSL` = 美国 CPI 指数 332.813）· 新闻 10 条 **0 相关**（国债 ETF / 4.2 万奖金与医保补贴 / 道指涨幅 / 负 beta / Roth 转换 / 芯片股 / 加拿大关税 / SpaceX / 股市连涨 / 卖房避税）· 研报 20 条 **10 条真讲金价**（含「黄金突破 4200 美元」）、**10 条讲「名字里有黄金的股票」**（**7 篇同一家珠宝公司**「老铺黄金」+ 紫金黄金国际 2 篇 + LVMH 顺带 1 篇），其中**一对是同一份研报的重复条目**（07-31/08-01 标题差一个字）。
  - **加 BR**🟡（②+①并入·**同一个病的两个实例**）—— 「问题 → 拉什么」的映射表**覆盖不全就静默走默认值、且零告警**：① FRED 关键词表 13 个词全是宏观指标，**没有黄金·原油·汇率·任何商品** → 撞不上就落 `CPIAUCSL`，**它连「问错了」都不知道**（数据合法·有时间戳·格式完好·无一句日志）；② #244 新加的 `confidence` 三档刻度**全部围绕「能不能认出是哪只股票」**写，**主题型 query 不落在任何一档的正面描述里** → 黄金跑模型给 0.9，而该档字面是「含明确 ticker 代码或公司名唯一无歧义」。**共性 = 枚举表 + 默认兜底 + 没有「我不知道」这个状态**。① 本是 #244 自己 PR body 里记的已知遗留，**未进 backlog**，本次顺手补进 BR 而非单开一条 —— 归并有实据（同形），不是为省配额硬凑。
  - **加 BS**🟡（⑤ + ③④ 并入）—— 引用清单把**三类信息混成一类**：答非所问的 / 当背景的 / 真对题的，到分析师眼里全是「7 条引用」，**没有任何标记区分**。🔒 **不是说这些源没用**：新闻拉通用市场背景**可能本就是设计意图**（谷歌那条订阅源写死搜 `financial markets`），但**代码里没有一句话说明这个定位** ⇒「背景」与「答非所问」在清单上长得一模一样。**修法方向未定须裁**（给 reference 标「针对本问题 / 通用背景」两档，或按源声明意图）；**明确不推荐「急着删源」**——删掉通用背景可能反而减少下游视野。
  - 🔒 **边界写死防与既有条目混读**：BR ≠ **BQ**（BQ = **该拉的腿没激活**·价格源 · BR = **腿激活了但拉错东西**）· BR ≠ **DEFECT-FRED-SUBSTRING**（那条是子串**误命中**「毛利率」→「利率」· BR 是表里**压根没有这个域**）· BR ≠ 已 close 的 **DEFECT-FRED-KEYWORD**（那条修「广告的拼写表里不认」· BR 是「整类资产没进过表」）· BS 的「研报只取标题不读正文」半边归 **BI**（本条只记信号混杂）。
  - **R5 守**：宏观关键词表的简化是**已知未完成非疏漏** —— 源文件注释自带 TODO「扩 query→series 映射，或接入 FRED series search 端点」，并写明当时那个节点的焦点是异步框架、不是智能路由。**不把「没做完」说成「做错了」**。
  - ⚠️ **活跃 13 → 15。上限 15，余 0（用满）**。破例累计 **11** 不变（两条均在上限内·不占破例）。**🔴 仍 0 条**。`lint:active-count` 同步改 **15**。**下次再立 lettered 条目须先 close 一条或用户授权破例** —— 本笔已在 §0.2 banner 显式标注。旧 08-18 第三笔 banner 的「⭐ 当前最新」标记**同笔清掉**（该形态此前**至少十次** stale）。
  - **↳ 本笔自审（`/code-review` 三条 finding·当场全改·记账不粉饰）**：① BS 原写「一对是**同一份研报**的重复条目（标题**差一个字**）」—— 两条 ID 不同、日期不同、标题实差 **3 字**（插入「力」+「维持」→「重申」），**「同一份」毫无证据 = 把推断写成事实（撞 R5）**；已改为如实描述并显式标「未经证实」。② BS 把「相关率 32%」当承重数字用，**判定标准一个字没写**，而被列为无关首例的「国债 ETF 跌至 2004 年以来最低」与金价存在公认宏观关联（实际利率）；已补写判定标准（相关 = 标题主语是金价/贵金属本身）+ 显式标注该条可争议 + 给出改判后的 35%。③ 「该形态此前已六次 stale」这个计数**自 08-14 起被逐笔照抄**（08-12 尚在递增：四次→五次），实际已至少十次 —— **计数自己成了它要治的那个病的实例**；已订正并声明此后按实递增。🔒 **三条全部落在自己刚写的断言上**，与 08-18 第一笔那次「拦截面只减不增」同形：**写的时候都不觉得不妥，因为每个字分开看都像真的**。
  - ⚠️ **前向订正（本条正文保留不改·加此标）**：上方 BR 的「**实例②**」（`confidence` 刻度不覆盖主题型）**已于同日第五笔核代码证伪并撤除** —— 详见下条。本笔当时的记述照原样留着，**只在此加指向**。

- **2026-08-18（同日第五笔·撤 BR 实例②·不新增不 close·活跃数不变）**: 立账 22 分钟后核代码 —— **BR 的第二个实例其实早就修好了**。
  - **怎么发现的**：用户要求规划「第一批 = 补 `confidence` 主题型刻度」，动手前先读 [classify.txt](../../src/committee/query_class/prompts/classify.txt) 现状 → 三档**已经覆盖主题型**：`0.9–1.0` 档字面写着「含明确 ticker 代码 / 公司名唯一无歧义，**或明确落在 `thematic` 定义列出的类别里**（宏观 / 产业链 / 板块 / 政策 / 资产类）」，`0.6–0.9` 档写着「**或主题宽泛但可归类**」。⇒ **要做的事已经做完了，第一批为空。**
  - **谁修的**：[#244](https://github.com/JunoChenZt/subagent-for-investment/pull/244) **自己的第二个 commit（冷审收口）**，修法 = 刻度**换轴**（从「认出了什么」改为「归类有多确定」），并同句重跑验过 —— 分类 / 路由 / references 不变，`confidence` 0.9 → 0.95 且这次正面落在档位字面里（归档 `run-gold-macro-20260818-v2`）。
  - **🔑 误记根因（值得记）**：立 BR 时的 ② 是**照抄 #244 PR body 里第一个 commit 自记的「已知待办」**，没往下核最终代码 —— 而那条待办**在同一个 PR 的下一个 commit 就已被消掉**。⇒ **PR body / commit message 里的自记遗留是过程记录，不是现状**；R6「读记录先认 main 的 tracked 版本」的同族形态：**源选对了（是 main），但选错了时间切片（选了中间态）**。判现状的一手源只有**最终代码**。
  - **处置**：BR 条目正文 + §0.2 第四笔 banner **就地改口径**（live 状态）→ 删 ② 保留「曾记录并撤除」的显式说明；§6 第四笔正文**保留不动、加前向标**（历史记录不改写·守 R7）。**「两处同形」的归纳一并收掉** —— 只剩一个实例时，「共性」是形态描述不是规律（守同日冷审「别拿凑出来的样本量撑结论」）。
  - **配额**：**不新增不 close** → 活跃仍 **15**（余 0），`lint:active-count` 不动。破例累计 **11** 不变。**🔴 仍 0 条**。BR 靠实例①（FRED 关键词表·已实证）独立成立，**不撤条目**。

- **2026-08-19（第六笔·纯订正·不新增不 close·活跃数不变）**: 收 `/code-review`（对 PR #247）指出的两条 backlog 正文问题。
  - **① banner 栈跳过了同日第五笔** —— 第五笔（撤 BR 实例②）**只写进 §6，没在 §0.2 建 banner、也没接走 ⭐**，于是扫 banner 栈的读者看不到「BR 实例② 已撤」这次状态变更。**lint 兜不住**：Check 8 只比日期，第四笔与第五笔同为 08-18 ⇒ 同日失效在它眼里不存在 —— 这正是第四笔自己刚写下的「Check 8 管日期不管归属」那个盲区，**当场复发**。**处置**：⭐ 挪到本笔 banner；第四笔行加订正标并显式指回第五笔。⇒ 第四笔立的「此前至少十次·此后按实际递增」→ **本次第十一次**。
  - 🔑 **为什么值得记**：第四笔在同一段文字里既**诊断了**这个形态（还订正了被照抄失真的计数）、又**当场犯了**它 —— 诊断与复发同页。⇒ **写下「我以后会注意」不构成机制**；能兜住的只有 lint，而 lint 的判据（比日期）与病灶（比归属）**不同轴**。收窄 Check 8 到「归属」属改判据、承重变更，**本笔不做**，仅如实记录该盲区仍在。
  - **② BS「7 条引用」口径只解释得了 3 条** —— 原文写「7 条（按字段拆）」，但该拆法只覆盖唯一那个宏观指标（`series_id`/`unit`/`value`）= 3 条，**余 4 条来源未交代**，读者复算不出 7；而同一条目对「相关率 32%」已按要求补了可复算的判定标准 ⇒ **同条目内两个承重数字，一个可复算一个不可**。**处置**：**不补构成**（要补须回归档逐条核·本次未做 —— 不拿推断填坑），改为显式标注「只核到 3」，并写死本条不拿 7 的内部构成支撑论断；「三类混成一类」的立论改挂**清单无区分标记**这一结构事实。
  - **改动面**：§0.2 的 BS 行 + banner 栈（**live 档·就地改**）；**§6 第四笔 / 第五笔正文一字未动**（历史记录·守 R7），前向事实由本笔承载。
  - **配额**：不新增不 close → 活跃仍 **15**（余 0），`lint:active-count` 不动。破例累计 **11** 不变。**🔴 仍 0 条**。
- **2026-08-19（同日第七笔·立 DEFECT-YF-TICKER-TRUNCATION·活跃数不变）**: 给五个数据源写说明书时真调一遍，**撞出一个静默给回错资产价格的缺陷**。
  - **怎么撞见的**：用户要求「每个数据源写一份 md，含真实样本 + 结构化输入 + 正负 few-shot」。守坑表「fixture 必须取自真实响应」⇒ 五个源各真调一次，顺带试了资产类代码（验 **BQ** 的修法假设）→ **三个全出问题**。
  - **一手证据（[归档](../observations/source-shapes-20260819/)）**：要 `BTC-USD` 拿回 `{"ticker":"BTC","price":28.57,...}` —— **结构完好、有时间戳、零报错**。〔⚠️ 2026-08-20 订正：原写「差约三千倍」为推断，实测双边后为**约 2290 倍**；同日并坐实「库层 12/12 全通、缺陷全在本仓」〕`GC=F` 截成 `GC` 重试三次烧 13.54s 后失败；`^GSPC` 直接抛错。
  - **🔑 最值钱的一点**：这不是「拿不到」，是**「拿到假的」** —— 截断后的残码**恰好命中另一个真实存在的代码**。同族里 `GC`/`^GSPC` 只是失败（吵、能发现），**唯独 `BTC` 静默成功**。⇒ 「截断」这个机制的危险程度**取决于残码撞没撞上别的真代码**，而这**没有任何规律可循** ⇒ 不能靠「大部分会失败」自我安慰。
  - **推翻了一个假设**：设计 pass 里写「yfinance 支持 `GC=F`/`^GSPC`/`BTC-USD`」——**在库那一层为真，在我们这一层为假**。⇒ **BQ 的修法不能是「把资产代码喂进去」**，必须同修取代码那条路。已就地回填 [yfinance_global_quote_tool.md](../pipeline/seg1_retrieval/yfinance_global_quote_tool.md)。
  - **🔒 R5 守**：严格 cashtag 是**设计且是对的**（2026-05-19 用户裁决收紧，根除「`I`/`AI`/`CEO` 被当 ticker」的假阳性，源文件注释写明）。**缺陷不在「严」，在「结构化那条路不认资产类代码」** ⇒ 修法从放宽**校验**入手，**不得放宽正则**——放宽 = 把当年那个坑原样放回来。
  - **配额**：DEFECT 族**不占 lettered 配额** → 活跃仍 **15**（余 0），`lint:active-count` 不动。破例累计 **11** 不变。**🔴 仍 0 条**。**用户 2026-08-19 拍「单独立」。**
- **2026-08-27（G7 全链跑排查系列登记·+3 DEFECT +2 lettered·破例 11→13）**: 换脑改造（seg1 retrieval_planner）后的首次九段全链跑（黄金·$1.62·终局 gate 13/0/0）通了，但逐段排查 + 根因下钻翻出 5 个问题，用户裁「全都登记到 backlog」。
  - **立 DEFECT-ANCHOR-FALSEPOS-HARDBLOCK**：锚绑错第一次**改变了决策产出**——`f60`「选举距今约 3 个月」挂的编号登记值是年份 2026，check① 比出数量级错 → EXEC-FLOOR 硬拦 → BUY 压成 HOLD、执行计划整个被切。断言本身是对的 = 实打实误伤（方向保守侧·非安全洞）。四环根因链每环都核过一手：盖章机器连年份都登记成数值 / 分析师提示词有规矩但只是嘱咐（模型违反）/ 下游按「带章=抄录」无条件信任 / check① 三道 fail-safe 防量纲歧义不防绑错。endgame G6 由此拿到它点名要的「prompt 没起效」直接证据。
  - **立 DEFECT-DEBATE-STALE-PRIOR**：辩论 R1 提示词明写「没有原始数据参考」（防串供的有意隔离）→ 断粮的空头拿训练期旧行情充数（DXY 105 / 国库券 5%·同跑数据 99.1 / 3.63%）。连带：三轮出处章有无 = 提示词的精确镜像（R1 无从引 0/0 · R2「可引用」9/9 · R3 未提 0/3）——「时有时无」不是模型随机。
  - **立 DEFECT-GATE-NA-AS-PASS**：终局 gate 把「没查到」印成 PASS——Q3/Q4 理由印 "acceptable for HOLD" 而实为 fm 填了计划被闸切；Q5「0% 错绑」只量 EVID-1 管道、同跑真实错绑在字面下不可见。
  - 立 **BT**（破例）：triage 打回能力盘点。已核一手：唯一真 reject 源 B3 于 06-24 #156 有意移除、其余非 pass 全是主观冷审、规则文件 07-24 后零改动 ⇒ 8 月起连续 4 跑全过 ≠ 规则被改松，= 牙被拔一颗 + 剩下的看缘分 + 题型换了。触发 = 连续第 5 次全过 / 动 triage 规则时。
  - 立 **BU**（破例）：「裁决/立账」落地无回填义务。例① 08-18 分类线裁决只活在 #244 提交记录（08-27 白查一轮 + 错判·已补 guide）；例② BN 08-14 已立账而 guide ⑦ 仍写「N≥3→提立」（08-27 照旧文本错判「N=2」·本笔回填）。与 R7 的规则接缝：阈值裁决/立账不在其触发事件类别里。
  - **BN 追加数据点**：08-27 黄金跑构成反向条件**连续第 2 次**（无一组零方差·全员共有词空集），close 条件只差 1 次；且连续型问题（黄金）出了真实方差，削弱「连续型易收敛」推测。
  - **三条横切根子**（5 个问题的共因）：规矩只嘱咐无闸门 / 检查只守管道接缝无人管 / 决定落地无同步义务。
  - **配额**：+2 lettered → 活跃 **15→17**，上限 15 超 2，破例累计 **11→13**（**用户 2026-08-27 明示「全都登记到 backlog」授权**·配额满现状已当面告知）。DEFECT 3 条不占。`lint:active-count` 同步改 **17**。**🔴 仍 0 条**。
  - 完整证据：[G7 FINDINGS](../observations/rp-g7-e2e-20260827/FINDINGS.md) §九–§十七 + [endgame G6/G7/G8 补记](number-provenance-endgame.md)。
- **2026-08-28**（G5b 真人验收首跑切出·+2 lettered·破例）：销复盘 `q4` 挂的第一条欠账——「人真能用它把一版计划改对」第一次真人试。四条验收**三过一栽**。
  - **当场修掉、故不立条目**：**确认环把改好的计划扔了** —— 循环开头无条件重出一版计划，把刚改好的覆盖掉（实测：改成 `UNRATE` 且提示「已改并通过校验」，下一版仍是 `FEDFUNDS`）；被拒的改动同样重出，白烧一次调用并把用户刚审过的那版换掉（5 条腿变 4 条、通胀腿消失）。判 bug 的一手依据 = 代码注释自写「改完回到展示，让用户**再看一眼**」，意图与行为对不上。**单测照不出**：`apply_edit` 函数级完全正确（11/11 反向变异 KILLED），坏的是它的返回值被谁扔了 —— **零件合格、装错了**。已修 + 3 条守护测试 + 反向验证（退回旧码前两条当场变红、第三条守「别把该重出的打回也一起关掉」）。
  - **同日已落地、故不立条目**：出计划预算线 **15s → 40s**（[RP.G8](../roadmap/S2.md)·五处齐改）—— 起因也是本次首跑连续两次超时。
  - 立 **BV**（破例）：人工确认路径的**取数失败在归档里没留痕**。人认过含金价的计划，`GC=F` 撞雅虎限流三次全空，`__degradation_notices__` 为 `None` ⇒ 归档零留痕；自动确认路径反而有告警。**不是设计错，是设计边界没延伸到结果侧** —— 「人看过了不用喊」只覆盖「计划有没有问题」，不覆盖「货有没有到」。交互时人看得见终端报错，受害者是几周后翻档的人。
  - 立 **BW**（破例·🟢）：段式跑指南没有**真人验收**这种跑法的位置。指南写「首段**必带** `--auto-confirm`」，真人验收**必须不带**；本次明知故犯并在归档标注，但**没自行改指南**——放松硬规则属 §2.7 Q5 该停下问的范围。不改的后果 = 下一个人要么以为不带是操作错误、要么干脆不做真人验收。
  - **不进 backlog 的两件**（本机环境·非仓库事项）：全局 `PYTHONPATH` 指向 3.13 全局包且排在 venv 之前，遮蔽本机所有虚拟环境（**已清**）；uv 管理的 Python 有坏符号链接，`uv python install 3.10/3.11` 报「缺少目标目录」，只能直接指具体解释器（**只绕过、未修**）。
  - **配额**：+2 lettered → 活跃 **17→19**，上限 15 超 4，破例累计 **13→15**（**用户 2026-08-28 明示「两条都登记」授权**·配额满现状已当面告知）。`lint:active-count` 同步改 **19**。**🔴 仍 0 条**。
  - 完整证据：[验收归档 ACCEPTANCE.md](../observations/rp-g5b-human-20260828/ACCEPTANCE.md)（含 trace / calls / checkpoint）。
- **2026-08-31**（backlog 例行过账·距上次 11 天·**零新增条目·纯判据订正**）：19 条活跃逐条对触发条件，动了两条、发现一个新形态。
  - **P 判据订正（两笔）**：① **(B) 仍是死信号，但死因与 08-06 那批不同** —— 不是「数据窗停跑」，是**缓存压根没接进管道**（`context_node` 从不传 `cache`，全仓 `FactCache` 只在测试里构造）；没有缓存就不存在「返空还是返 stale」这个分叉。**不是 08-06 triage 的疏漏**：该事实 08-26 G6 才查出，且用户当日裁「只修钥匙不接缓存」⇒ (B) 无限期死着。**活证据**：08-28 真跑 yfinance 真限流真返空，(B) 描述的情形字面发生而它没响也不可能响。⇒ (B) 前置改为「缓存接进管道后才谈」。② **(A) 已于 08-26 响过一次（G6 改缓存钥匙 `_dispatch_cache_key`）而本条无人回看** —— 当时确实重审并由用户裁决，但没人回来登记，账面至今写「未触发」。
  - **🆕 新形态（记账不立条目·配额已 19/15）**：「**backlog 条目自己的触发条件被满足了，却没人回来看这个条目**」。与 [BU](#bu-裁决--立账落地没有回填义务--真值源静默滞后72-小时内在两处独立撞见同一形态🟡2026-08-27-g7-全链跑排查切出) **相邻但不同** —— BU 是「裁决不回填真值源文档」，这条是「事件型判据全靠人当场想起来有这么一条」，而 backlog 只在 session 启动 / 子阶段交接时被整体过一遍。**再撞一次同形态即提立**。
  - **BU 加正面数据点**：40s 预算线裁决落地时按 BU 先列回填清单再收口，四处全同步、历史归档按 point-in-time 不动 ⇒ **任务在人工层面已证可行，缺的仍是机制化**。
  - **其余 15 条逐条核过：触发条件均未满足**（多数要等「下次动某段代码」或「再出现一次某现象」），本轮不动。**配额不变（活跃 19·破例累计 15）**，`lint:active-count` 不变。**🔴 仍 0 条**。
- **2026-08-31（同日第二笔）**：**BW close-by-completion**（用户裁「BW 也改了吧」）。[段式跑指南](../observations/e2e-runs/segmented-e2e-guide.md)「怎么跑」新增 **「⚙️ 唯一例外：真人验收跑」** 一节。
  - **措辞把守两头**（这是本笔的关键，不是随手加一段）：开头先声明**原「首段必带 `--auto-confirm`」一字未改、对所有段式 e2e 照旧成立**；结尾显式排除「懒得加 flag」（常规跑漏带 = 操作错误，不走本例外）。⇒ **开的是一格新跑法，不是松一条旧规则** —— 避免踩 [§2.7 Q5](workflow/05-brake-self-check.md)（标准降低）。
  - **四条纪律**：必须真终端（非 TTY 照旧自动跳过，不是「没生效」）· **不产出段式 e2e 数据点**（不进段间 checklist 纪律、不攒质量门样本、产出另开具名目录）· 必须留验收记录 · 只在验交互闸时用。
  - **立此格的理由写进了指南**：08-28 首次真人验收，四条验收里**查出一条单测照不出的缺陷**（确认环把改好的计划扔了——`apply_edit` 函数级完全正确、11/11 反向变异 KILLED，坏的是它的返回值被谁扔了）⇒ 交互闸这类东西**函数级测试有系统性盲区**，真人跑是补盲手段。
  - **配额**：活跃 **19 → 18**（close-by-completion 释放 1 slot·仍超上限 15 共 3）；**破例累计 15 不变**（close 不释放破例配额，§4.4）；`lint:active-count` 同步改 **18**。**🔴 仍 0 条**。
- **2026-08-31（同日第三笔）**：**BV close-by-completion**（用户裁「BV 也改了吧」）。结果侧退化告警落地。
  - **一句话**：**结果侧的退化事实不再受「人认过就不喊」门控** —— 因为**人认的是计划、不是结果**，取数发生在他点头之后。
  - **两套规矩，界限写进代码注释**：**计划侧**（走没走兜底 / 校验拒了几条 / 回核退了几条）**人认过的不喊·一字未改**；**结果侧**（点名要了、一条都没拿回来）**不分人工 / 自动一律进产物**。
  - **修法**：新增 `confirm.unfulfilled_leg_notices()` —— `source_routing` 里的腿（`__` 开头的留痕键除外）减去资料夹真有货的键，差集即缺腿，产出 `legs_empty`。**对账思路先拿 08-28 真跑产物验过**：正好只命中 `yfinance`，与实际一致。🔒 沿用 U1 纪律：**只报是哪几条腿空手，不定「空几条算退化」的门槛**。
  - **验证**：5 条守护测试（含复刻真跑形态：人认过的两条腿计划、金价那条空手 → 必须留痕）+ **隔离式反向验证**（只退回接线、保留新函数 ⇒ 行为守护那条当场变红、其余四条照常绿 ⇒ 它咬的是「接没接线」不是「函数存不存在」）+ 全量 **3849 passed**。
  - **配额**：活跃 **18 → 17**（release 1 slot·仍超上限 15 共 2）；**破例累计 15 不变**；`lint:active-count` 同步改 **17**。**🔴 仍 0 条**。⇒ 本日三笔合计：活跃 **19 → 17**，零新增条目。
- **2026-08-31（同日第四笔）**：**九段全链跑落账**（黄金·[FINDINGS](../observations/rp-g8-e2e-20260831/FINDINGS.md)）—— 当日三处修改后的验证跑：九段全通·零报错·终局质检 **13/0/0**·决策 HOLD/6·约 $4.62。**BQ 闭环兑现**（问黄金拿回 `GC=F`=4475.60）。
  - **当日修改验证**：40s 预算线 ⇒ 出计划**再未超时**；**结果侧告警负例首次真跑验到**（五腿全有货 ⇒ 缺腿差集空 ⇒ **不出声**，不制造噪音）。
  - **BN close-by-condition**：反向条件**连续第 3 次**成立，达本条自写 close 线（六张 NEUTRAL 票全员共有词 **0** 个、conviction 有方差）。⚠️ 本跑输入端摆明两派（实际利率口径之争 R2 吵到 R3）仍散得开 ⇒ 反向证据比前两次更强。保留：BULLISH 组零方差但仅 2 票不足论。
  - **BT 触发条件已满足**：seg3 **8/8 全过 = 连续第 5 次**。并拿到直接证据：`fundamentals` 的 **D1 规则真 fail**（整份报告零引用标记）**而总判定仍 pass**（只挂 `D-class flag`）⇒ **规则响了也不改变结论**——正是 BT 怀疑的形态。盘点待排期。
  - **DEFECT-GATE-NA-AS-PASS 第 2 次实例**（N=1→N=2）：13/0/0 里 Q3/Q4/Q5 三格是「没东西可查」被印成 PASS。**检查本身没错，是汇总呈现让"全绿"读起来像"全覆盖"**。
  - **DEFECT-DEBATE-STALE-PRIOR 两笔**：① 本跑**未复现**（R1 数字全部对得上本跑真实数据）—— **但闸门仍是零，不得据此 close**；② 🔴 **「精确镜像」措辞被本跑削弱**：R3 同一轮多头 0 个、空头 6 个，提示词解释不了同轮不一致。
  - **记观察不立条目（4 笔）**：`源#n` 键让 ① 段 as_of 分档**按键匹配就误判**（已补 guide 读法注）· 政治/历史角色证据最老 **607 天**（有出处可追溯·**为其开档=放松判据须用户裁·刻意不动**）· 空头那条路调用数偏高 **N=2**（④ 5 次 / ⑤ 7 次 vs 多头 2 次·未定线故判不触发）· **audit 判据回答的不是我们担心的问题**（2.9% 撞线属主题型结构使然、按 08-14 读法放行；但 67 条 `audit_notsure` 里 **66 条带精确数字** ⇒「机制没坏」≠「数字有保障」）。
  - **配额**：活跃 **17 → 16**（BN close 释放 1 slot·仍超上限 15 共 1）；**破例累计 15 不变**；`lint:active-count` 同步改 **16**。**🔴 仍 0 条**。⇒ 本日四笔合计：活跃 **19 → 16**，零新增条目、三条 close。
- **2026-09-01**：**BT close-by-completion** —— 盘点做完 + 用户裁「给 D1 装牙」。[全文](../observations/bt-triage-teeth-audit-20260901.md)
  - **口径**：9 份 **tracked** 归档（从版本库读、非工作树残留·[R6](../../CLAUDE.md)）× 每份 8 个角色。
  - **结论比 BT 原文更严重**：能触发返工的只有 A 类 + B1/B2/B3；实测 **A 类 432 次评估零开火、B1/B2 零开火**，唯一咬过的 **B3 已于 06-24 [#156](https://github.com/JunoChenZt/subagent-for-investment/pull/156) 移除** ⇒ **移除后没有任何一条有牙规则曾开火**（BT 原文写「牙被拔一颗+剩下的看缘分」，实为**剩下的从来没咬过**）。而开火最多的 D 类累计 **38 次、0 次改变判定**。
  - **订正 BT 原文一处**：「其余非 pass 全是 C 类冷审」**漏了 06-11 那次**（实为 **B4 + D3**，非 C 类）。
  - **反面解释一并记（不拣支持结论的读法）**：A 类守的是「模型有没有正常输出」的结构底线（标题非空/要点 3–5 条/字段齐），**零开火也可读成「模型半年来一直正常输出」**。真正的空缺在中间地带 —— **「格式正常但内容不行」这一层，此前只有 C 类两条 warning，而 warning 不返工。**
  - **处置（用户裁）**：**给 D1 装牙** —— 整份报告零引用标记（无 `REF#` 也无 `W#`）→ `reject` → 进返工；**其余 D 规则一字未改**。选 D1 是因为它**客观**（数得出来）、误杀风险低，且开火 17 次说明问题真实高频。未采纳：什么都不做 / 把主观的 C 类升格。
  - ⚠️ **已知接缝（须盯）**：D1 开火率 **24%（17/71）** ⇒ 约 **1.9 次返工/跑**（成本 +$0.03/跑可忽略）。但若分析师返工到上限仍不挂标，会推高终局质检门 **S3「打满返工上限的角色数」**（0 通过 / 1 警告 / **≥2 FAIL**）⇒ **改 triage 可能把质检门弄红**。🔒 **真红了的处置是把 D1 降回 warning（改一行），不是去松 S3。**
  - **验证**：旧不变式测试「D 类绝不改变判定」**被收窄而非删除**（新增反向守护钉死「只装 D1、别把整个 D 类变成打回」）+ **隔离式反向验证**（退回装牙前，「D1 该打回」当场变红、反向守护照常绿）。
  - **配额**：活跃 **16 → 15 = 回到上限内**（close-by-completion 释放 1 slot）；**破例累计 15 不变**；`lint:active-count` 改 **15**。**🔴 仍 0 条**。⚠️ **自 2026-08-27 以来首次不超限。**
- **2026-09-01（同日第 2 笔）**：**PR [#268](https://github.com/JunoChenZt/subagent-for-investment/pull/268) review 首批七修落地 + 立 1 条 DEFECT**（`fix(seg1)` commit `3fe2947`）
  - **七修全是「看着在管事、其实没管」**：断点白名单漏登记人确认的计划（存得进读不回·续跑时那版蒸发并盖 `auto` 章）· `max_retries` 在两条经中转的 ChatOpenAI 分支被静默丢弃（本 PR 修 44.3s 超时的手段在换端点后失效）· 手改计划是整体替换而非合并（只改一个字段会丢掉该腿其余参数，而少检索词的新闻腿在校验层合法 ⇒ 一路绿灯）· 退化告警「回核退了几条」用减法倒推（校验拒的冒算成退货 + 全退光时反报 0）· 告警门控只读 `confirmed_by` 不读 `origin`（回放跑批被当成「人认过」而全静音）· `isdigit()` 当 `int()` 护栏（`①`/`³` 当场抛、无人接）· 研报回筛对中文整句失效。
  - **验证口径**：守护测试**反向变异 7/7 KILLED**（缺陷逐个放回、对应测试都红）；全量 **3876 passed / 0 失败**；三 linter 全绿；`tests/` **纯新增 421 行、零删除零改动**。
  - 🔴 **一处修法方向被一手记录订正（[R5](../../CLAUDE.md)）**：原打算在回放时清掉上一跑的 `confirmed_by="human"` 章，撞上 [#259](https://github.com/JunoChenZt/subagent-for-investment/pull/259) G1 地基**明写相反意图**的既有测试（「种子里的确认留痕不能在回放中丢——它正是这份计划是人认过的凭据」）。**没有改那个测试**，而是查一手记录后改判：确认章记的是**关于这份计划**的出处、应当保留，真缺陷在**读法**（要连 `origin` 一起读）⇒ 修到消费端。既有测试一字未动。
  - ⚠️ **[§2.7 Q5](workflow/05-brake-self-check.md) 命中并上升**：研报回筛改用共用中文分词 = **放宽承重闸容差**，即便理由是「原实现会误判」也属 Q5（判据是「放宽了谁的承重面」，不是「理由对不对」）。**用户 2026-09-01 裁准**。同时 Q8（≥2 合理方案）命中已告知；其余六问不命中。
  - 🔑 **用户把问题抬高一层 → 立 `DEFECT-WISBURG-PADDING`**：「**本质上是研报数据源的问题，不是靠分词的松绑可以解决的**，之后单独做研报数据源的优化。」⇒ 记的是**请求侧制造填充货**这个根因（[接口说明书](../infrastructure/seg1_retrieval/wisburg-mcp.md)实测：只传「黄金」20 条几乎全对题，**加近四天窗后只剩 4 条**，机理是「窗里本来就没有 20 条，于是拿别的补满」），不是那把筛子。放宽后的筛子实测仍会把「白酒·高端价格带跟踪」判成「黄金价格走势」对题 ⇒ **调筛子始终是治标**。
  - **配额**：**lettered 活跃 15 不变**（DEFECT 族不占 lettered）；**破例累计 15 不变**；`lint:active-count` 按表实际活跃行数同步。**🔴 仍 0 条**。
- **2026-09-01（同日第 3 笔）**：**PR [#268](https://github.com/JunoChenZt/subagent-for-investment/pull/268) review 第二、三批落地 + 立 BX / `DEFECT-RETRY-ADVICE-FALSE`**（commit `7645d6b` / `95de23f`）
  - **第二批（用户三裁）**：**个股问题必须带一条取价的腿**（补在校验后执行前·守的是下游价位核对那把尺子，不是把决策权还给标签）· **重试预算按调用方分开设**（砍到 7.5s 的论证只覆盖管道那一个调用方，分析师工具那条路外面没墙、属误伤）· **命令行侧分类 3 遍 → 2 遍**（图里那遍不动·要穿共享状态、单独排期）。
  - ⚠️ **第二批含一处 review 原报告的自我订正（[R5](../../CLAUDE.md)）**：原写「价格闸误杀早停」，查该闸设计记录后改判 —— **它没判错**（它守的是"结论里的价位有没有尺子可核"，而尺子塌没塌与"为什么没有现价"无关）。真缺口在上游：换大脑后没有任何东西保证个股问题会去取价。⇒ 修在计划层、不去松那道闸。**本节点第 2 次「推断设计意图→查一手记录后翻案」**（第 1 次 = 回放确认章）。
  - **第三批（用户同意 1/3/4）**：**存在性核对改并发**（旧写法排队跑·最坏 5s × 腿数撞 41s 封顶 ⇒ 规划员正常出的好计划被整段切断丢弃）+ 封顶余量改为焊在 `DEFAULT_CHECK_TIMEOUT` 上（41 → 45）· **回核降级标注真的进归档**（设计 pass §3.5b 明写这一批职责就是「产出打在过了回核条目上的意图标注」，此前只活在函数里）· **质量旗按「腿」对账**（同源多腿缺一条时旧写法仍报 ok = 结构化标记对下游撒谎）。
  - 🔴 **反向变异抓到执行体自己的漏**：③ 的首版守护测试直接调函数、**没钉住接线**，把主链路那次调用拆掉照样绿（本仓「函数写好了、没人调」形态）。补真跑节点的接线测试后重跑，**5/5 全 KILLED**。⇒ **单元测试证明不了"接上了"，这条要写进习惯。**
  - **本日新立两条**：**BX**（🟢 行情格式表只认美股+港股·东京/伦敦/法兰克福/首尔/孟买全被拒·而数据源支持 —— 真功能须逐市场实测）+ **`DEFECT-RETRY-ADVICE-FALSE`**（🟡 永久性原因与临时失败走同一条出口、一律说"请稍后重试" —— 假的可行动建议·碰早停结论属承重件须用户裁措辞）。**两条一起读。**
  - **验证口径**：三批合计反向变异 **17/17 KILLED**；全量 **3838 → 3901 passed / 0 失败**；三 linter 全绿；`tests/` **纯新增 718 行、零删除零改动**。
  - **配额**：活跃 **15 → 16**（+BX）；**破例累计 15 → 16**（用户明示「两个都记账」）；`lint:active-count` 改 **16**。**🔴 仍 0 条**。
- **2026-09-02**：**PR [#268](https://github.com/JunoChenZt/subagent-for-investment/pull/268) ✅ 已合 main `ad19c61`（squash·分支已删·CI 九道全绿）+ 补立 `DEFECT-COMMODITY-AS-TICKER`**
  - 🔑 **CI 状态翻案**：PR 描述原写「CI 因 GitHub Actions 账单失效跑不起来，以本地全量绿为据」（同 #267）。**收口时账单已恢复、九道全部真跑通过**（两个 Python 版本后端 / 前端 / docker-build / secret-scan / 三个 lint）⇒ 本 PR **不再是"以本地为据"**。
  - **补账理由（本条是本次收口的要点）**：review 坐实 16 条，合并时**已修 13、记账 3**，但「商品行情腿装进个股袋」这条**既没修也没记账**——修法查清了、只差用户点头，用户选择先合。**PR 一合它就没家了**：只存在于 PR 描述与 review 工具输出里，没有任何机制会让人再撞见它。⇒ 合并后**立即**补立 `DEFECT-COMMODITY-AS-TICKER`（不占 lettered）。
  - ⚠️ **形态记账（不立条目·第 2 次即提立）**：「**review 坐实但未修的 finding，在 PR 合并时没有强制落账义务**」——本次靠执行体自己想起来。与 **BU**（裁决/立账落地不回填真值源）同族但不同环节：BU 管"改完要回填"，这条管"没改的要有家"。
  - **配额**：lettered 活跃 **16 不变**（DEFECT 族不占）；破例累计 **16 不变**；🔴 仍 0 条。
- **2026-09-02（同日第 2 笔）**：**BQ ✅ CLOSED（close-by-decision·用户当日裁）+ 两半残留并入 `DEFECT-COMMODITY-AS-TICKER`**
  - **怎么走到这一步**：RP 节点收口时发现 BQ 触发条件「用户明确要求」命中 ⇒ **不自行关**（[§4.2](#42-触发条件命中后的处理)：命中须用户裁），整理证据交裁。
  - **支持关的硬证据**：A/B 同问句同配置各跑 3 次 —— 问「黄金会怎么走」**旧路由 0/3 拿到行情腿、新大脑 2/3**（`GC=F` = 4682.80，且**真流到下游**：进 ds_researcher 事实清单第一条 `f1`、带水印 `REF#Y-011`）；**对照组茅台（个股）两臂均 3/3** ⇒ 差异是资产类特有、不是随机波动。BQ 记的原始危害（价位只能靠模型上网捡→被终审涂改）在有价的跑里不再发生。解法**比 BQ 原设想更好**：不靠 thematic 下加识别规则，靠计划写了行情腿就激活。
  - 🔴 **反面证据一并记（不拣支持结论的读法）**：① **2/3 不是 3/3**，那 1 跑规划员没出计划 → 退回旧路由 → 金价没了，[G7 FINDINGS](../observations/rp-g7-e2e-20260827/FINDINGS.md) **自记「回到 BQ 那个病」**；② **兜底路由一个字没改** ⇒ BQ 的病在降级路径上原样活着（刻意设计、非遗漏）；③ **五类资产只端到端验了黄金**，原油/指数/加密/汇率仅有「格式认得」层证据；④ **BQ 自己预言的第二半已兑现**（原文「牵动 `ticker_payload` 及下游 schema·均按股票设计」——A/B 里黄金成功那两跑 `bag=ticker`，期货数据装进为股票设计的袋子）。
  - **裁决与执行**：用户裁 **close-by-decision + 残留写去引用方、并进商品腿那条**。⇒ 上述 ①②④ 与缺口 ③ 全部并入 `DEFECT-COMMODITY-AS-TICKER`（该条本就是「拿到了却装错袋」，与 BQ「拿不到」正好接力）。
  - ⚠️ **措辞纪律**：这是 **close-by-decision 不是 close-by-completion** —— 病没被彻底根除，是「核心已解 + 残留有主」。
  - **连带**：[S2 §4.7.5](../roadmap/S2.md) 节点头两件待裁一并落定（BQ + RP.G4 第二层）。
  - **配额**：活跃 **16 → 15 = 回到上限内**（close 释放 1 slot）；**破例累计 16 不变**；`lint:active-count` 改 **15**。**🔴 仍 0 条**。
- **2026-09-02（同日第 3 笔）**：**`DEFECT-COMMODITY-AS-TICKER` 修复 PR [#269](https://github.com/JunoChenZt/subagent-for-investment/pull/269) 已开（合并即 ✅）+ 补立 `DEFECT-CTX-BAG-SHAPE`（PR2 + 8 条登记项）**
  - **修法**：`validator.leg_is_equity`/`intent_is_equity` 三处共用（装袋 / 名录核验 / `ensure_price_leg`）；`asset_kind` 缺失或未核值退回按源名。**不动** `_is_ticker_query` 与价格闸（设计记录已读·它没判错）。
  - **设计升级**：seg1 = 规划员 + 资料员（第一性原理）；全局标签退场、改为腿清单 = PR2。**「交给分析师自判」被两次黄金归档否决（0/2 自弃权）**。
  - **验证**：主链路守护 + 反向变异 4/4 KILLED；全量 3925/0；三 lint 绿；**段式 e2e 三跑待用户放行**（黄金 / NVDA / `^GSPC`）。
  - **BQ 残留交代**：② 本 PR 修 · ① 显式 defer（记 `DEFECT-CTX-BAG-SHAPE` 登记项 1）· ③ 排 e2e。
  - **配额**：lettered 活跃 **15 不变**（DEFECT 族不占）；破例累计 **16 不变**；🔴 仍 0 条。
- **2026-09-03**：**`DEFECT-COMMODITY-AS-TICKER` ✅ CLOSED（close-by-completion·PR [#269](https://github.com/JunoChenZt/subagent-for-investment/pull/269) 已合 main `a7f2687`·squash·分支已删·CI 九道全绿）**〔⚠️ 上方「2026-09-02（同日第 3 笔）」实际写于 09-03·日期笔误·内容不动〕
  - **合并前 review**（8 角度 → 12 候选 → 10 坐实/可信）：已修 4 · 记 6 进 `DEFECT-CTX-BAG-SHAPE` ⑨–⑭。最重的一条 = 补腿循环与新守卫口径不一致（会重复补 GC=F / 把正则抽出的基码 BTC 凑成假股票腿）→ 循环只补股票腿 + 跳过已覆盖标的（含基码），反向变异 3/3 KILLED。
  - **e2e**：黄金 / NVDA / `^GSPC` 三跑全过、重跑 0 次（BQ 残留③ 兑现·详见 §0.2 09-03 第 1 笔）。
  - **配额**：lettered 活跃 **15 不变**；破例累计 **16 不变**；🔴 仍 0 条。**下一步**：`auto/CTX-LEGS`（PR2）。
- **2026-09-04**：**`DEFECT-CTX-BAG-SHAPE` PR2 = PR [#270](https://github.com/JunoChenZt/subagent-for-investment/pull/270) 已开（`auto/CTX-LEGS`·连带登记项 ⑩ ⑬）**
  - **结构**：`CommonContext.payload` + `legs: list[LegMeta]` 为真值；`ticker_payload` / `macro_payload` 降为影子（`__post_init__` 双向推导·`legs_from_payload` 兼容读法按代码格式定资产类型）；`questions.py` 具名问题；builder `_build_legs`（计划驱动与 `intent_is_equity` 同一兜底 ⇒ 影子 ⟺ `has_equity_leg`；兜底路由按分类标签·刻意保留）。
  - **读者迁移 8 处**：base 渲染 + `_is_ticker_query`、rules_e、price_gate（按标的匹配）、context_node（删 `_early_stop_probe_ctx`）、confirm、trace_report（`legs:` 行）、archive 现价、checkpoint。
  - **改 case 三处**（§2.8.2 四要素已写进测试）：test_archive 平铺夹具→真实嵌套；test_at2 / test_continuation 补 ticker；test_seg1_g54 键后缀测试改验价格闸本身。
  - **验证**：tests/test_ctx_legs.py（含真实 tracked 旧格式断点读入 + 再序列化）· 反向变异 8/8 KILLED · 全量 3989/0 · 三 lint 绿；**段式 e2e 两跑待用户放行**。
  - **配额**：lettered 活跃 **15 不变**；破例累计 **16 不变**；🔴 仍 0 条。
- **2026-09-04（同日第 2 笔）**：**PR [#270](https://github.com/JunoChenZt/subagent-for-investment/pull/270) ✅ squash 合 main `415bc48`** —— `DEFECT-CTX-BAG-SHAPE` **PR2 主体完成、条目不 close**。
  - **合并前冷审三修**（`51223f9`）：① 代码匹配丢了交易所 —— 数字核丢后缀再去前导零 ⇒ `000001.SH`（上证综指）= `000001.SZ`（平安银行）、`0700.HK` = `000700.SZ` ⇒ **指数点位冒充个股现价放行价格闸**（**本 PR 新引入的回归**·改前 `_price_leg_covers` 判 False）→ 数字相同**且交易所对得上**才算覆盖、前导零只对非六位码去。② **旧 A 股断点回放护栏反着开火** —— 资料夹里 tushare 条目是**裸六位码**（tracked 归档实证 `{"ticker":"300308"}`·`market` 只写 `"CN"` ⇒ 交易所无从得知），兼容读法只认带后缀 ⇒ `has_equity_leg` 由 True 翻 False ⇒ 从任何旧 A 股断点 `--resume` 续跑，基本面分析师在**真个股问题**上自动弃权 → **裸码退回改前行为（算股票）**：猜不出交易所就不猜，与 `leg_is_equity` 同一条兜底纪律；⚠️ 代价如实记 = 旧归档里的 A 股指数/ETF 读回来仍算股票（**正是改前行为**·⑩ 不追溯）。③ 计划名单与键**错位一格** —— `sources_from_plan` 跳过构造不出源的意图、键名单整体前移，下游按位配对 ⇒ 股票腿丢失 = 护栏关火 + 误报早停；**改前 `force_ticker_shape` 直读意图、不经过键，对此免疫 ⇒ 本 PR 把既有隐患升级成闸门级** → `sources_from_plan` 多返回 `kept_intents`、三份名单同长（**用户裁走法 A**·顺带修好既有两处回核对账同类错位）。④ 顺带删未用 import + 补守护测试里 `_enrich_fundamentals` 桩的 `legs=` 参数（此前抛 TypeError 被外层 except 吞掉、那步静默不执行）。
  - **为什么全绿也没咬到**：②的旧夹具全用带后缀码 / 美股码，**恰好绕开真实写法** ⇒ 新用例改按**真实 tracked 归档形态**构造；③的守护**走主链路**（真节点→真校验器→真 builder）+ **隔离验证**（退回接线时接线测试红、同名单元测试仍绿 ⇒ 咬的是接线不是零件）。
  - **验证**：全量 **4000 passed**（原 3989·新增 11 条）· 反向变异 **3/3 KILLED**（整文件快照写回）· 三 lint 绿 · CI **9/9**。
  - **A 股验证跑**（`ad6582d`·中际旭创 300308.SZ·seg1–2）：装个股袋 · tushare 腿 `asset_kind=equity`（价 813.0）· 护栏不开火 · 价格闸不误报早停 · **23 次调用含「非个股标的」提示 0 次** · 基本面报告是真公司分析（营收 417.8 亿 +182.5%·PE 88.7·`DATA_INSUFFICIENT` 0 次）⇒ **缺陷镜像面成立**（黄金/指数上该弃权的弃权了·A 股上该干活的干活了）。⚠️ **覆盖如实记**：规划员 **2/2 超时** ⇒ 两跑均走兜底路由 ⇒ 三条修法只覆盖 ① 的「不误伤」半边，②③ 本跑没走到、靠单测 + 主链路守护 + 变异兜着，**不冒充已验**。**不进 run-counter**（用户裁·只到第 2 段非完整跑批）。
  - **合并踩到一处**：本分支与 main 改了 backlog **同一行**（main 侧 = 同日第 1 笔的 O2 订正）⇒ 冲突。**以 main 那版为底 + 接回分支独有的 PR2 落账段**，两边独有内容逐条核过、**无取舍**。
  - **配额**：lettered 活跃 **15 不变**（PR2 主体完成但**条目不 close**）；破例累计 **16 不变**；`lint:active-count` 不动。**🔴 仍 0 条**。**🔻 剩余项**：⑨ ⑪ ⑫ ⑭ + 原登记项 1–7 + 影子字段删除（下一周期）+ 段式 e2e 剩余跑（旧断点 resume / NVDA 首段）。
- **2026-09-04（同日第 3 笔）**：**`DEFECT-CTX-BAG-SHAPE` 旧断点 `--resume` 补跑** —— 补验冷审修法 ②，条目仍不 close。
  - **为什么补这一跑**：修法 ②（旧存档裸六位码仍算股票腿）**只在读旧存档时才走**，而「从旧断点续跑」是**每天都会撞上**的路；此前只有单测兜着，且 `51223f9` 的教训已点明 —— **旧夹具全用带后缀码 / 美股码，恰好绕开真实写法，4000 条全绿也没咬到**。⇒ 必须走一次真的。
  - **怎么跑**：真实旧格式 A 股断点（[07-10 中际旭创 seg1](../observations/e2e-runs/segmented-e2e-guide.md)·资料夹存 `{"ticker": "300308"}` 裸码）→ `--resume --stop-after research`。产出 [run-oldckpt-resume-20260904/](../observations/ctx-legs-pr270-e2e-20260904/run-oldckpt-resume-20260904/)，判读见 [FINDINGS §五](../observations/ctx-legs-pr270-e2e-20260904/FINDINGS.md)。
  - **结果（五项全过）**：读档后该腿 `asset_kind=equity`（走真正的 `load_checkpoint`·非夹具构造）· `_is_ticker_query=True` · **「非个股标的」提示 0 次**（24 次调用全扫）· 基本面报告是真公司分析（证据 **10 条**·回撤 42%·护城河/估值齐）· 第 2 段 checkpoint 再序列化读回判定不变。⇒ **修法 ② 由「只有单测兜着」升为已实证**。
  - **段间 checklist（② research）全过**：8/8 报告 · key_points 4–5（底线 2）· 每角色调用**正好 3 次**（贴上界·与 07-10 基线同为 24 次·非本次变差）· evidence 5/5/6/**10**/8/6/8/8 · conviction 4 中性 3 看空 1 看多 · **$0.0753**。
  - ⚠️ **覆盖如实记**：① 仍只**半条**（「同数字不同交易所要挡住」没走到）· ③ 本跑是 resume、**不重跑规划员** ⇒ **仍没走到**。三修目前 **1 实证 / 1 半条 / 1 靠单测**，**不冒充已验**。
  - ⚠️ **三处日志噪音逐条查过、均非故障**：`web_search budget exhausted` 4 次 + `max_iterations` 触顶 3 次 = **设计内的每跑封顶**（[agent_loop.py](../../src/committee/tools/agent_loop.py)）· 两份报告 `quality=sanitized` = JSON 毛刺清洗后成功的既有兜底。**必须分清的一处**：输出里 7 处 `DATA_INSUFFICIENT` **全部来自技术分析师**（RSI/MACD/ATR 没取到的诚实标注），**不是护栏误伤基本面** —— 判据量的是「基本面在真个股问题上有没有被逼弃权」，不是「全文有没有这个词」。
  - **不进 run-counter**（沿用同日第 2 笔的用户裁决）：只到第 2 段、非完整跑批。
  - **本次落账按 BU 先列回填清单再收口**（8 处 · live 就地改 / 历史加新笔不动旧 / 规划文档补前向一句 / memory 同步 · 并显式记下不动的是哪几处）⇒ **BU 第 2 次人工演练成功**。同时**给 BU 记两个负例**（段式跑指南指着已关闭条目 / 登记项 ① 超时数字废弃一周才被撞见）⇒ BU 踩坑计数 **升到 4**。
  - **配额**：lettered 活跃 **15 不变**；破例累计 **16 不变**；`lint:active-count` 不动。**🔴 仍 0 条**。**🔻 剩余项**：⑨ ⑪ ⑫ ⑭ + 原登记项 1–7 + 影子字段删除（下一周期）+ 段式 e2e **只剩 NVDA 首段**。
- **2026-09-07**：**四个 PR 落账**（#271 CI 升版 / #273 存档漏字段 + 守护 / #272 ①③ 守护 / #274 早停标记恢复）+ `DEFECT-CTX-BAG-SHAPE` 新增登记项 ⑮ ⑯。
  - **#271 CI 脱离 Node 20**（`2fa2ab2`）：四个 action 全被点名弃用，真关掉时 CI 会一起挂。**用户裁「直接修、不立条目」** ⇒ 活跃条目不动。判据 = **告警区清零**（不是"CI 绿"）。⚠️ 过程一笔：首版 setup-uv 写 `@v10` 被 CI 打回 —— release 号是查来的，但"存在浮动 v10 大版本标签"是**假设、没查**；改正后逐个读 `runs.using` 选版（v5/v6 仍 node20 = 换了等于没修）。
  - **#273 堵死「漏登记只丢不报」**（`9ba1395`）：写盘全量泛化 / 读盘手工白名单 ⇒ 静默丢字段，**第三次复发**（前两次都是碰巧被查出）。补 `confirmed_tickers` + 守护「每字段要么恢复、要么登记写明理由」。扫描器用 ast（看不见注释·只认赋值），登记表自带三条自守护（理由不许空话 / 字段删了不许留 / **扫描器自己先断言没坏**）。
  - **#272 ①③ 补守护**（`63547cf`）：① 改由**真实在册归档加载**验（原用例手搭上下文 = 本域自己的病灶）；③ 查明**结构上不可达**，改加名单同步守护 = **让那条补丁永远用不上**。⚠️ 明记：给的是守护，**不是"跑了一次真的"**。
  - **#274 早停标记恢复**（`b3990ed`·用户当日裁）：**#273 的守护上线当天首次显形**。后果不是少跑一次早停，是**绕过安全闸** —— [exec_floor](../../src/committee/facts/exec_floor.py) 锚失效退回模型自报价（自己量自己）、连自报也无则直接放行。守护登记表随之清空 =「没有例外」。⚠️ 验证边界如实记：反向变异红在**前提断言**行；另一半（无旗则委员会跑起来）刻意不在单测验（要打真 LLM），由既有 `TestGraphEarlyStop` 从另一头钉住。
  - **🔻 四条坐实未解决 —— 本笔之前一条都没进账本**：⑮（交易所守护在真实 A 股数据上是死的·**信息没丢是被主动丢掉的**·修法 = 写完整代码）与 ⑯（五源名单仍散四处·#272 只做了两两比对非单一真值）**已入登记项**；**读档仍是手写白名单**（治本 = 逐字段往返行为验证·落地后 ast 扫描器整段可删）与 **一处相对路径漏网**（[test_failure_dump.py:85](../../tests/test_failure_dump.py)）〔**2026-09-07 订正 —— 不是一处，是 3 个文件**（换目录实跑核准）：[test_seg1_retrieval_plan.py](../../tests/test_seg1_retrieval_plan.py) 挂 2 条 · [test_mask_e1_audit_enum.py](../../tests/test_mask_e1_audit_enum.py) 挂 1 条（相对 glob 扫不到归档）· [test_failure_dump.py](../../tests/test_failure_dump.py) **不挂、静默跳过**（`exists()` 假 ⇒ 整条消失）。⚠️ **静默跳过比挂掉更坏** —— 跑批目录下少跑一条没人知道，正是本仓最忌的"空过"。〕**已排入当日计划第 4/5 步**。
  - ⚠️ **形态第 2 次命中 ⇒ 按规矩该提立**（首记 2026-09-02·注明"第 2 次即提立"）：「review 坐实但未修的 finding，PR 合并时没有强制落账义务」。**提立占 1 个 lettered slot（活跃 15 已到上限 ⇒ 需第 17 次破例）⇒ 待用户裁**，本笔先记事实、不擅自立。〔**➡️ 同日第 2 笔已裁：不立条目**，改为焊进 [08 §2.11.9](workflow/08-retro-node-and-pr.md)；第 17 次破例**未开**。〕
  - **本笔按 [§2.9.4 八格回填清单](workflow/06-dod-and-evidence.md)走**：格 1 条目正文 ✅ 改（覆盖那句已过期）· 格 2 本表 + 更新块 ✅ · 格 3–5（跑批指南 / 判据表 / 观察点）N/A = 这批不动跑批口径与承重边界 · 格 6 代码注释 ✅ 已随各 PR 同步 · 格 7 路线图 N/A = S2 只指向本条、不断言覆盖 · 格 8 memory ✅。
  - **配额**：lettered 活跃 **15 不变**；破例累计 **16 不变**；`lint:active-count` 不动。**🔴 仍 0 条**。
- **2026-09-07（同日第 2 笔）**：**裁决 —— 那条形态不立条目，改焊进收口固定动作**（[08 §2.11.9](workflow/08-retro-node-and-pr.md)）+ **相对路径三文件已修**（PR [#275](https://github.com/JunoChenZt/subagent-for-investment/pull/275) 合 main `c2d8734`·squash·分支已删·CI 九道全绿）
  - **裁决（用户 2026-09-07）**：「review 坐实但未修的 finding，PR 合并时没有强制落账义务」**不立 backlog 条目** —— 登记的仪式比干活贵，且这条的治法本来就是"在合并前的固定动作里加一格"、做完当场结案，没有需要跟踪的余留。**第 17 次破例未开**，破例累计仍 16。手法与 **BU** 机制化成 §2.9.4 同源；先例 = #271「直接修、不立条目」。
  - **规则内容**：每条坐实 finding **恰好一个去处**（本 PR 修 / 记账带自己的触发条件 / 明确不做带理由），合并前 `N = a+b+c` 对不上不许合。⚠️ 写死**「坐实」由提出方认定** —— 执行体不得靠"我觉得这条不成立"把它移出分母（认为不成立走第三格、分母不变）；**少这一刀本节可被"重新数一遍 N"架空**。补进 §6 PR 模板 + §6.2 不可省段 + 文首概览。**三条同族分工**：R7 = 状态切换后扫旧口径 / §2.9.4 = 改了的东西真值源跟上 / §2.11.9 = **没改的东西要有家**。
  - **PR #275**：三个文件的仓内路径改为从仓库根锚定（两个走 conftest fixture·一个照同手法自锚）+ 清掉一处**假绿**（读不到文件的返回值恰好等于断言期望值 ⇒ 换目录照样"通过"）+ **新增守护**扫所有测试文件的写法。**一处有意的行为变化**：那条静默跳过的用例原设计"归档不在就跳过"，而归档一直在册 ⇒ 今天"找不到"只可能是换目录跑、无正当跳过理由，故跳过条件整个拿掉改成在册断言。
  - **验证**：换目录跑那四个文件 —— 改前 3 挂 / 1 静默跳过 / 4.4 秒 → 改后 **96 全过 / 0 跳过 / 172.8 秒**（差额 167 秒 = 丢掉的那条真的在跑了）；仓库根全量 **4032 passed / 2 skipped / 2 xfailed / 0 失败**，收集数 4021 → 4034 逐条对得上；改前三份源码反向验守护 **3/3 全抓到**；四道 lint 绿。
  - ⚠️ **形态记账（第 1 次·不立条目）—— 新守护自己犯了它要治的病**：用户冷审两条，都是**"扫得不全 / 破例写了不生效，却沉默着说干净"**，与本轮要治的静默跳过同一形状。① 破例名单钥匙**文档与代码对不上且带行号**（上面插一行即失效·失效样子仍是"红着找不到原因"）→ 钥匙改为与行号无关 + 加自检**把说明书与代码焊死**；② **只扫 `tests/` 顶层**，子目录 17 个文件在范围外，而"防扫描器瞎了"那道自检只看总数（顶层 150 个就够过坎）⇒ **永远不会因为漏掉子目录而报警** → 改递归（150 → 167）+ 自检加"必须真的扫到子目录"。**与 [test_gate_matrix](../../tests/test_gate_matrix.py) 当年 `glob` → `rglob` 是同一个病** ⇒ 写新检查器时先自问「我枚举全了吗、我的自检抓得到漏枚举吗」。
  - **本笔按 §2.9.4 八格清单走**：格 1 **N/A**（裁决是"不立条目"、无自己的条目正文；前向事实已写去引用方 = 第 1 笔那两处"待用户裁"）· 格 2 本表 + 更新块 ✅ · 格 3 跑批指南 N/A · 格 4 判据表 N/A · 格 5 观察点表 N/A（宽 grep 无相关观察点）· 格 6 代码注释 ✅ 随 PR #275 · 格 7 路线图 N/A · 格 8 memory ✅。
  - **配额**：lettered 活跃 **15 不变**；破例累计 **16 不变（第 17 次未开）**；`lint:active-count` 不动。**🔴 仍 0 条**。
- **2026-09-07（同日第 3 笔）**：**`DEFECT-CTX-BAG-SHAPE` ⑮ ✅ 已修** —— PR [#276](https://github.com/JunoChenZt/subagent-for-investment/pull/276) 合 main `8e0e5fe`（squash·分支已删·CI 九道全绿）。条目**仍不 close**。
  - **主体**：A 股行情写进资料夹**保留完整代码**（此前主动切掉后缀）⇒ #270 冷审那一刀「数字相同**且交易所对得上**」终于喂得进数据。**连带必须改**：补基本面会拿它再转一次格式，不认后缀就拼出 `300308.SZ.SZ` —— 请求作废，产物上**只表现为「这条腿没有基本面」、不报错**。
  - ⚠️ **严重性合并前就如实写在 PR 里**：**没找到今天会真撞上的路径**（计划驱动时腿上是完整代码；裸码只出现在兜底路由与旧归档，而那两条路上只有一条腿、腿与标的本就同一只）⇒ **防线朝 A 股一侧是死的，不是正在漏**。修它是因为代价极小、守护本就为此加、且"撞不上"只靠"恰好一条腿"这个巧合。
  - 🔴 **冷审逮到本 PR 自己引入的误退**（用户查·我实测复现）：`.SH`/`.SS` = 上交所两种拼法，比交易所后被判成两只 ⇒ 价格闸误早停、**整跑白停**。已归一，**同义词表一份两处共用**（校验层那道原是硬编码，改成 import 同一份）。正反两向都钉守护，变异 2/2 KILLED。**正落在本 PR 自己引用的观察点 O-OVERSTRICT-GUARD-01 上 —— 观察点写在文档里没挡住它，是人查出来的。**
  - **新增登记项**：⑰ 归档「按标的查」那一列混两种写法（精确匹配 ⇒ 两边各查到一半、不报错）· ⑱ 名录不认 `.SS`（同根第三处）—— ⚠️ **只坐实「返 None」，没追下游后果**，故不声称无害也不声称在漏；不动它是 Chesterton's Fence（另一个模块明写「不猜」的边界）。
  - **§2.11.9 首次实战**（本笔是该规则立后第一个 PR）：**坐实 4 = 修 2 + 记账 2 + 明确不做 0**，数目对得上。⇒ 规则当场起作用 —— ⑱ 按老习惯就是"提一嘴然后忘掉"。
  - **验证**：全量 **4041/0**（4032 → 4036 → 4041·每步增量逐条对得上）；反向变异 5 组全 KILLED；四道 lint + CI 九道绿。⚠️ **未跑 e2e**，镜像面由「走真实取数函数 + 反向变异」钉住，**不冒充跑过一次真的**。
  - **本笔按 §2.9.4 八格清单走**：格 1 ✅（⑮ 标已修 + ⑰⑱ 入册 + 剩余项改口径）· 格 2 ✅ · 格 3 ✅ 接口说明书示例改完整代码 · 格 4 N/A · 格 5 ✅ 观察点加前向一句（正文不动·结论不变）· 格 6 ✅ 回核层那段旧断言已订正（行为一字未动）· 格 7 N/A · 格 8 ✅ memory。
  - **配额**：lettered 活跃 **15 不变**；破例累计 **16 不变**；`lint:active-count` 不动。**🔴 仍 0 条**。
  - **🔻 剩余**：⑨ ⑪ ⑫ ⑭ **⑯ ⑰ ⑱** + 原登记项 1–7 + 影子字段删除 + 段式 e2e 只剩 NVDA 首段 + 读档手写白名单。**下一步 = ⑯**（用户已裁走**单一真值**，不是四表加断言）。
- **2026-09-08**：**`DEFECT-CTX-BAG-SHAPE` ⑯ ✅ 已修** —— PR [#277](https://github.com/JunoChenZt/subagent-for-investment/pull/277) 合 main `79aeef5`（squash·分支已删·CI 九道全绿）。条目**仍不 close**。
  - **主体**：五源名单收成一份名册 `DATA_SOURCE_NAMES`，各处对着它点名、**导入期就核**（漂开那一刻进程起不来，不是"跑出错的结果再被测试抓到"）。#272 那道只是两两比对的测试 = 治"发现漂开"，不治"不会漂开"。顺带堵新缝：**行情源必须走取价那条构造**，否则拿不到已确认标的、**静默回退 query 正则**。
  - 🔒 **刻意没做**：语义分组（thematic / union）**不从名册派生** —— 该不该进组是设计决定，"新增源自动加入"等于替以后那个人做主；只核"名字在册"，并钉前提断言：union **刻意不含 wisburg**。
  - 🔴 **冷审两条（用户查·都坐实·都已修）**：① **数少了，还有第五处**（`planner.VALID_SOURCES`）—— **盯着它那道测试的 docstring 早就写着「防第四份手抄漂移」，仓里本来就把它算作副本，是盘点的人没数进去**；且首版那句"这种形态在结构上没有了"对该处不成立。② **空名单也算通过**（`subset_ok` 只核"名字在册"，空集天然满足）—— 今天不会自己变空，但**为以后复用**必须堵，已改成一律拒。
  - ⚠️ **口径订正**：条目正文原写"散在**四处**"、main 上那条 commit subject 也写"**四张表**" —— **都少数一处**；两者均按 point-in-time 不改，前向事实写在条目正文的订正注里。
  - **验证**：全量 **4050/0**（4041 → 4047 → 4050·增量逐条对得上）；反向变异 **6 组全 KILLED**（其中四组表现为**模块直接起不来**）；四道 lint + CI 九道绿。⚠️ **未跑 e2e**，不冒充。
  - ⚠️ **过程记一笔（形态第 1 次·不立条目）**：首版全量与变异实验**并行跑**了 —— 仓里有测试从磁盘读源码 ⇒ 那一跑不可信、已掐掉重跑；第二轮改成"跑完再变异、变异后还原复跑"。🔑 **改源文件的实验与读源文件的测试不能并行**，哪怕看起来互不相干。
  - **§2.11.9 第二次实战**：坐实 5 = 修 5 + 记账 0 + 明确不做 0，数目对得上。
  - **八格清单**：格 1 ✅ / 格 2 ✅ / 格 3 N/A / 格 4 N/A / 格 5 N/A / 格 6 ✅（四段过期 docstring 订正·行为一字未动）/ 格 7 N/A / 格 8 ✅。
  - **配额**：lettered 活跃 **15 不变**；破例累计 **16 不变**；`lint:active-count` 不动。**🔴 仍 0 条**。
  - **🔻 剩余**：⑨ ⑪ ⑫ ⑭ ⑰ ⑱ + 原登记项 1–7 + **影子字段删除**（下一周期）+ 段式 e2e 只剩 NVDA 首段 + 读档手写白名单。
- **2026-09-08（同日第 2 笔）**：**影子字段删除 ✅ = 主线只剩最后一跑** —— PR [#278](https://github.com/JunoChenZt/subagent-for-investment/pull/278) 合 main `afa669b`（squash·分支已删·CI 九道全绿）。条目**仍不 close**。
  - **主体**：PR2 降为影子的两个格子从 schema 删除、**归档也不再写**（用户当日裁「真删」）。🔑 **旧档翻译收到读档入口、刻意不放回 dataclass** —— 字段只要还能当构造参数，就还会有人拿它当真值写。
  - **验收拿 main 上 tracked 的真实归档**：145 份在册旧断点全读得回来（141 份是只有旧格子的老档）· **护栏判定与 main 逐份对照 = 与基线一模一样、同一批文件 ⇒ 本次引入差异 0** · trace 渲染 129/145 逐字节相同，16 份**多显示**、0 份丢。全量 4052/0。⚠️ **未跑 e2e**，不冒充。
  - 🔴 **冷审三条（都坐实·都已修）**：① 首版 trace 口径让 **18 份旧归档丢价格显示**（段式审核正靠那行确认"价拉回来没有"）→ 改按价格腿口径，变成多显示 16 / 丢 0；② **恒真断言 3 行 + 冗余 3 处**（机械替换残渣·**留着会让人以为有测试盯着、其实红不了**）→ 全删，并改用**语法树精确扫**复查；③ 手动 e2e 脚本漏改 → 见下。
  - 🔴🔴 **形态两次命中（不立条目·两条都可迁移）**：
    - **(a)「全仓扫」只扫了 `src/`**，漏 `scripts/` —— 而「我枚举全了吗」正是**上一个 PR 刚写进注释的教训**，隔一个 PR 原样重犯。⇒ **要把 `src`/`tests`/`scripts`/`docs` 逐个点名。**
    - **(b) 说「修好了」前没分清「能加载」与「能跑到那一行」** —— 首版只做导入自检，坏行在函数体里、导入走不到。用户追问后实查：同一脚本还有 **9 处读根本不存在的字段**，**崩得比首版改的那几行还早**。⇒ **验收要验「跑到那一行」。**
  - 🔑 **根因也堵上**：该脚本被闸门矩阵显式豁免自检（"需真实密钥与网络"）—— **豁免只对「要联网那半」成立**，打印那半不需要网络却跟着没人管。新增语法树字段存在性守护（一秒·不打网络）+ 防瞎自检，反向变异当场红。⚠️ 它**先做完最贵的部分再崩** —— 烧完钱才发现跑不通。
  - **§2.11.9 第三次实战**：坐实 6 = 修 5 + 记账 1 + 明确不做 0。
  - **八格清单**：格 1 ✅ / 格 2 ✅ / **格 3〔⚠️ 当时判 N/A 是错的·同日第 3 笔已补 ✅〕** / 格 4-5 N/A / 格 6 ✅（多处过期 docstring 订正·行为一字未动）/ 格 7 N/A / 格 8 ✅。
  - ⚠️ **形态记一笔（八格清单第 1 次判错·不立条目）**：格 3「跑批指南」当时判 N/A，理由是「不动跑批口径」—— **但本次改的正是段间审核 checklist 直接引用的那一行渲染口径**。🔑 **判 N/A 之前要问一句「这份文档里有没有在描述我改的东西」**，而不是只问「我有没有改这份文档」。（发现时机：开跑前照规矩读段式跑指南，撞见那句话反了。）
  - **配额**：lettered 活跃 **15 不变**；破例累计 **16 不变**；`lint:active-count` 不动。**🔴 仍 0 条**。
  - **🔻 剩余**：⑨ ⑪ ⑫ ⑭ ⑰ ⑱ + 原登记项 1–7 + 读档手写白名单 + **段式 e2e 只剩 NVDA 首段** ⇒ **主线到此只剩那一跑**。
- **2026-09-08（同日第 4 笔）**：**🎉 `DEFECT-CTX-BAG-SHAPE` 主线欠账清零** —— NVDA 首段跑通 + 规划员超时线 **40 → 85s**、run 级上限 **90 → 120s**（用户当日裁）。PR [#279](https://github.com/JunoChenZt/subagent-for-investment/pull/279) 合 main `f8ea795`。条目**仍不 close**（只剩事件型登记项）。
  - **跑通了什么**：零退化告警，**计划驱动那条建腿路径终于走到** —— 腿清单从兜底路由的 `unknown/-` 变成 `primary/verified`，选源理由从机器标签变成规划员写的人话，多余的 A 股腿消失。此前两跑验的都是兜底那一支。同跑顺带验到：归档里已无影子字段（#278 在真实跑批上成立）· `ticker=` 行显示价 · 引用时效四源全在档内。
  - **超时线先量后定**（登记项 ① 的纪律）：6 次实测 **28.0/30.5/36.0/36.7/41.0/67.4s**，40s 吃掉 **2/6**（与原记「1/3」对得上）；08-28 定 40s 时同一句问法是 29.8–32.7s、6/6 在线内 ⇒ 🔴 **不是线定错了，是延迟本身变慢、尾部几乎翻倍**。85 = 最慢 × 约 22% 余量（沿用同一算法）。
  - **顺带治病**：外层封顶硬抄 `40.0` = 同一个数第二份副本（与 ⑯ 同病）—— **只抬内层会被外层先掐、表现成「改了没用」**。改派生 + 守护。
  - 🔴 **冷审三条（都坐实·都已处理）**：① **抬线撑破 90s 那本账、而我没算** —— 三笔最坏 116s，光第一段就顶穿；🔑 **08-28 那次专门算过并留了五项清单，我做了前三项、漏的正是后两项 —— 清单就在那儿**。⇒ 用户裁：维持 85、run 级抬到 120。② **5 处「40」文字副本**（用户列 4·复扫又抓 1），其中 `hi=40` **与代码直接矛盾**。③ **「379–535s」被我写在讨论第一段预算的段落里** —— 用户追问才发现**我整场在拿封顶值推、没有第一段实测数**。
  - ⚠️⚠️ **三条据实记（已写进 S2 §6.7 / DoD 判据行 / 代码注释）**：(a) §6.7 各 phase 预算加起来 **108s，本来就 > 90s**，表**自己内部就不自洽**；(b) 实测**端到端** 379–535s 且三份验收报告都判「非 gate 条件」⇒ **这条线长期是目标不是在守的闸**，**别把「已抬到 120s」读成「现在跑得进 120s」**；(c) 🔑 **但那是整跑不是第一段** —— **第一段实测 51.8s**、封顶 116s（留一倍以上余量），379–535s 大头在后 8 段 ⇒ 「第一段吃掉整跑预算」**账面成立、实际耗时不成立**。
  - ⚠️ **形态两次记账（不立条目）**：(i) **有现成的五项清单没照着走** ⇒ 抬承重线前先翻出上次同类动作的清单逐项对；(ii) **拿封顶值当耗时讨论了整整一轮** ⇒ **谈预算先问「这个数是上限还是实测」**，两者差一倍以上。
  - **§2.11.9 第四次实战**：坐实 5 = 修 5 + 记账 0 + 明确不做 0。
  - **八格清单（本次格 4 与格 7 都不是 N/A）**：格 1 ✅（登记项 ① 数字全部重写）/ 格 2 ✅ / 格 3 N/A / **格 4 ✅ 判据表** / 格 5 N/A / 格 6 ✅ / **格 7 ✅ 路线图（S2 三处 + roadmap-v3.4 两处 + S3 + 验收模板与 XML 四处 + AY 前向一句）** / 格 8 ✅。
  - **配额**：lettered 活跃 **15 不变**；破例累计 **16 不变**；`lint:active-count` 不动。**🔴 仍 0 条**。
  - **🔻 剩余**：⑨ ⑪ ⑫ ⑭ ⑰ ⑱ + 原登记项 2–7 + 读档手写白名单（**① 已随本笔处理**）⇒ **主线欠账清零，只剩事件型。**
  - **🔻 `DEFECT-CTX-BAG-SHAPE` 剩余**：⑨ ⑪ ⑫ ⑭ + 原登记项 1–7 + **⑮ 交易所守护（下一步开工）** + **⑯ 五源单一真值（用户已裁走单一真值、非四表加断言）** + 影子字段删除 + 段式 e2e 只剩 NVDA 首段；**读档手写白名单**（治本 = 逐字段往返行为验证）仍欠。

- **2026-09-08（同日第 5 笔）**：**一览表漏账对齐 + 守表脚本扩到认第二族编号** —— 起因 = 用户「翻 backlog 找下一个活」，翻的时候发现**按表挑不了活：表本身数不全**。
  - **实况**：**24 条只有 §1 正文、§0.2 表里从来没有行**。漏了不响，因为 [scripts/lint_backlog.py](../../scripts/lint_backlog.py) 的 ID 正则是 `[A-Z]{1,2}`，`DEFECT-` 开头的整族对**每一项检查**都不可见（含「缺行」「✅ 顶格」「计数」）。
  - **补录的 24 条两种情况各半**：**11 条早已做完**（正文状态行 6/7/8 月即标 ✅ 并带合并 SHA，只是从没销账进表）；**13 条确实还开着**。
  - **同一把梳子另梳出三处**：① `DEFECT-COMMODITY-AS-TICKER` 把 ✅ 埋在括号里（表头约定明写须顶格）→ 已订正；② `DEFECT-CTX-BAG-SHAPE`（7813 字）+ `DEFECT-D5-COUNT-AS-VALUE`（1177 字）整条挤在备注格、超 1000 上限 → 已**逐字照搬**拆出 §1 正文；③ `DEFECT-RETRY-ADVICE-FALSE` 是真轻条目 → 补 `〔轻条目〕` 声明。
  - **脚本侧**：ID 正则放开到两族 · 关闭判定认 ✅/CLOSED/CANCELLED · 计数拆 `lint:active-count`（配额族）与 `lint:active-other-count`（非配额族）· §6 对账仍只管配额族 · **新增 Check 9**（标题读起来已关闭、行却还活跃 = 报矛盾）~~，堵住「标题里碰巧有个 ✅ 就整条静默消失」这个由本次放宽引入的新坑~~ 〔🔴 2026-09-08 第 8 笔订正：**这句是假的**，Check 9 要有行才比得了，而该坑的形态正是没有行；真修法见第 8 笔〕。
  - **刻意不做**：不去给已完成条目的**标题**补 ✅ —— 标题一改锚点就变，指向它的链接会集体失效（本仓刚清完一轮死锚点）。状态只写触发状态格。
  - **配额**：lettered 活跃 **15 不变**；破例累计 **16 不变**；`lint:active-count` **不动**；新增 `lint:active-other-count=20`。**🔴 仍 0 条**。
  - **🔻 6 条判据待用户裁（本笔只登记不替用户拍）**：`DEFECT-R5-02` · `T10 / #4` · `DEFECT-AUDIT-INTENT` · `DEFECT-R5-04` · `NAMING-EXTKREFS` · `DEFECT-DSML-PARSE` 改进 B —— 六条的共同点是**触发条件挂在已经不会再发生的事情上**（[§4.2 问二](#42-触发条件命中后的处理) 形态），或**压根没写触发条件**。

- **2026-09-08（同日第 6 笔）**：**逐条复核 35 条 → close 5 条 + 删 1 条违规判据**（用户要求「每条重新 review，看哪些真需要、哪些已经不需要」）。
  - **复核方式**：**逐条进代码核**，不照条目复述。核到的例子：缓存在生产路径恒为 None（P）· 保鲜期兜底档仍是 400 天（BO）· 审核环节 `as_of` 出现 0 次（BP）· 引用记录无「对不对题」字段（BS）· 域名只剥四个展示前缀（R5-03）· D5 跳过名单只排三种空值 · 质检两处「没有计划→直接判过」· 出处有效性闸带着「数值不为空」前提 · 风险闸确实按证据条数分档（据此**否掉** REVIEW-ERROR-AS-DATUM 的反向条件）。
  - **判成**：22 条真在 · 5 条建议关 · 1 条砍半 · 2 条边缘 · 5 条治理常驻。
  - **close 5 条**（全部 close-by-decision·用户当日裁·保留位置）：**P** / **T10 / #4** / **`DEFECT-R5-02`** / **`DEFECT-R5-04`** / **`DEFECT-AUDIT-INTENT`**。共同点 = **事情已经不成立**，不是「还没轮到」。
  - **删 1 条判据**：`DEFECT-DSML-PARSE` 改进 B（「待评估排期」违 §4.1）；命题移交 **BK** 承接，非丢弃。改进 A 保留。
  - **R7 收口**：live 断言就地改（endgame 分流表两处）；历史 / 规划 / retro / handoff / observation / 代码出处注释一律不动。
  - **顺带消一处旧矛盾**：endgame 分流表长期把 `DEFECT-R5-02` 列在「已 close」栏，而 backlog 仍是活跃 —— 本次 close 使那处断言成真。
  - **配额**：lettered 活跃 **15 → 14**（余 1·P 释放一格）；非配额族 **20 → 16**；破例累计 **16 不变**。**🔴 仍 0 条**。
  - **未动**：**BD** 与 **NAMING-EXTKREFS** 两条边缘项待用户裁（建议 = NAMING 直接关·BD 先补注释再关）。

- **2026-09-08（同日第 7 笔）**：**两条边缘项裁定 —— BD + NAMING-EXTKREFS 关掉**（第 6 笔留给用户的两条，当日裁：NAMING 直接关 · BD 补注释再关）。
  - **`NAMING-EXTKREFS`**：处置②（docstring 警示）07-02 已做；处置①（改名）= 动 checkpoint/archive 序列化的承重改动、换零行为收益 ⇒ 不值得单独做。**关掉零损失**（知识已在字段上方注释里，本次并补「条目已关·本注即真值源」）。
  - **`BD`**：本条**自写的反向条件已成立**（只有一个搜索上游 + Worker 侧归一稳定无漏）。🔑 **关之前先把知识挪进 [as_of.py](../../src/committee/as_of.py)** —— 在此之前那份文件只字未提「英文写法一概不认 / 靠 Worker 在进仓前转 / 接第二个上游时补在这里」，就这么关等于扔掉知识。**这是用户裁的前提条件，不是顺手加的。**
  - ⚠️ **BD 与第 6 笔那五条的失效方式不同，措辞刻意分开**：那五条是**判据失效**；**BD 的闹钟是好的**，关它是「值不值占配额位」的取舍。混着写会让将来的人以为「反向条件成立」和「判据挂死信号」是一回事。
  - **配额**：lettered **14 → 13**（余 2）；非配额族 **16 → 15**；破例累计 **16 不变**；**🔴 仍 0 条**。
  - **本轮（第 5–7 笔）合计**：一览表从漏 24 条到全账在册；活跃 **35 → 28**；close 7 条 + 删 1 条违规判据；守表脚本从看不见第二族到全族守住。

- **2026-09-08（同日第 8 笔）**：**PR [#280](https://github.com/JunoChenZt/subagent-for-investment/pull/280) 复核收两条真 finding**（用户拉下分支实跑）—— 都是本 PR 自己引入或自己许下的，**形态恰是本 PR 要治的那种病**。**零条目变动**，只动脚本 + 测试。
  - **① 关闭判定放太宽 → 标题带一个 ✅ 就整条隐身，且是相对 main 的倒退**。实测：标题带 ✅、表里无行的**活跃**条目 —— 本分支 **0 报告**、main **2 条**。第 5 笔 banner 写的「Check 9 已堵」**是假的**（Check 9 要有行才比得了，本坑形态正是没行）⇒ 真修法 = **关闭判定必须带关闭词**，光秃秃一个 ✅ 不算。第 5 笔两处假断言已就地划掉订正。
  - **② 模块说明里「中文命名条目会响」是假保证**，实测两个方向都静默 ⇒ 新增 **Check 10**（编号解析不出的开放条目指名报出）；假保证收回并写明不许无测试加回。
  - ⚠️ **自伤记一笔**：我先前的测试把「光秃秃一个 ✅ = 已关闭」**钉成了预期行为** —— 这就是回归能全绿的原因。修正时它当场变红，**改测试不改预期**，并补反向用例。**教训：给自己写的检查写测试，最容易把当下行为误当应然。**
  - **测试**：53 → **65**。**配额**：三项数字全不变（13 / 15 / 破例 16）。**🔴 仍 0 条**。

- **2026-09-08（同日第 9 笔）**：**九条排入主动清理计划 · 立节点 [S2 §4.7.6 CRED](../roadmap/S2.md)** —— 用户问「接下来 backlog 按什么顺序、怎么处理」；前提是**剩 28 条全是事件型、没有到期的**，所以排的是「主动点火」顺序。**条目数三项全不变**。
  - **用户裁 U1–U3**：只主动点两簇 + 簇 3 也做；其余 19 条**保持事件型不碰**。设计 pass = [CRED-可信度地基三簇-设计pass-2026-09-08.md](../plans/CRED-可信度地基三簇-设计pass-2026-09-08.md)。
  - **三簇九条**：簇 1 质检说了假话（4 条 DEFECT）· 簇 2 证据的时效与身份（BO / BP / BS / D5）· 簇 3 辩论第一轮断粮（1 条）。BK 顺手不关。
  - ⚠️ **触发条件一个字不改**：计划 = 主动去动那块代码，判据届时自然响，走正常 close-by-completion —— 不是提前评估、不是为腾配额。
  - **选这九条的判据**：治「我核过了」这句话本身真不真（质检章 / 证据日期 / 辩论数字来路）；其余是覆盖面与体验。
  - **风险**：簇 2 高（动 `Reference` 形态）须确认拆解后开工；簇 1 中高（承重闸门·WARN 试用）；簇 3 中（新检测·不动 R1 隔离）。待裁 D1–D4。
  - **配额预告**：全 close → 28 → 19（配额族 13 → 10）。

- **2026-09-09（第 11 笔）**：**CRED.1.G1 落地**（PR #283 合 main `fb6dcee`）——Q3/Q4「没查到」改 `N/A` 档、分四成因、判到数字层；53 份归档回放只 PASS→N/A、整体判定零变化。⇒ `DEFECT-GATE-NA-AS-PASS` ✅ **close-by-completion**（非配额族 15 → 14）。合并前 review 修一真 bug（`0` 占位符被真假值判断读成「没填」→ 在册归档 FAIL→N/A）+ 补 6 条靶测。**CRED.1.G4 设计 pass 入库**（PR #282 合 main `abda356`·纯文档·等 D4）：268 份探针 → check① 硬拦路 5 响 5 误报 0 真错。配额族 **13 不变**、破例累计 **16 不变**、🔴 仍 0 条。
- **2026-09-09（第 10 笔）**：**CRED.1.G0 登记 PR #281 合 main `e096924` + CRED.1.G4 设计 pass 提前出**（[CRED-1.G4](../plans/CRED-1.G4-绑错判别力-设计pass-2026-09-09.md)）。条目数三项不变。
  - **#281**：簇 1 四项先登记后动码 + D5 回填（影子对账式告警试用）+ 复核两修（(a) 档两份全中 / D5 清单漏改）。
  - **G4 探针**：268 份主干归档 → check① 9 响；硬拦路 **5 响 5 误报 0 真错**（年份 / 百分比↔小数 / 单位缩写 / 推算绑定）；EXEC-FLOOR 历史硬拦仅 G7 一次即误报 ⇒ 真阳性 0。外源册年份形态 26.4%。
  - **判定**：① 源头排年份 ❌（波及 26% + 印证计数）· ② 年份免检 ✅ · ③ 分析师侧 ⏭️ 另立 · ④ 只观察 ❌；新增 ⑤ 100× 归一 · ⑥ 词表补 k/M/B/x/倍 · ⑦ 三元组可见性。**推荐 B = ②⑤⑥⑦**，等 D4-a/b。f16 推算绑定留作条目剩余项。

- **2026-09-11（第 1 笔）**：**成本口径缺口修复 + 立 1 条到期型条目**（PR [#288](https://github.com/JunoChenZt/subagent-for-investment/pull/288) 合 main `613952e`）。
  - **缺口**：DeepSeek 2026-09 起把回包里的模型名从 `deepseek-v4-flash` 换成 `deepseek-flash`，价目表没跟上 ⇒ 那批调用一律按 $0 落账（2026-09-10 那跑 45 次自有调用里 41 次）。**配置侧对账当时全绿** —— 配置里一直写 `deepseek-chat`（在册），变的是回包报的名字 ⇒ **对着配置核 ≠ 对着实际发生的事核**。
  - **修法**：补 `deepseek-flash` 键 + 两个活跃键刷到官方现价（取高峰档上界）+ 三处可见性（构造 LLM 时 / 落账时 / 归档 `unpriced_models`）+ 到期提醒（`_PRICE_RECHECK_BY` / 归档 `stale_price_models`·**刻意不并进 `partial_cost`**）。
  - **review 坐实 8 条**（§2.11.9：8 = 修 6 + 明确不做 1 + 订正 review 自身说法 1）。最重一条 = **自称的三道闸全没盖到事故现场那块屏**（分段成本表与累计行是两段独立渲染的代码）。
  - **配额**：配额族 **13 不变**（新条目属非配额族）；非配额族 **14 → 15**（+`PRICE-V4PRO-CUTOVER`）；破例累计 **16 不变**；`lint:active-other-count` 同步改 **15**。**🔴 仍 0 条**。

- **2026-09-14**：**判据命中检测接线（闸门矩阵第 0.5 层）+ BJ 状态订正**（PR [#290](https://github.com/JunoChenZt/subagent-for-investment/pull/290) ✅ 合 main `200007a`·方案 [trigger-wiring-2026-09-14](../plans/trigger-wiring-2026-09-14.md)）。**零新增、零关闭条目**。
  - **起因（一手）**：BJ 的触发条件 (B) 自 2026-08-07（第 0 层交付 `24f539b`）起 **9 次提交命中**，其中 `ad19c61`(09-02) / `0e297ef`(09-10) 在 **08-31 完整 triage 之后**，而 §0.2 该行一直写「未触发」。**判据没坏** —— 坏在事件型判据的立论（"迟早会被自然撞上"）从来没有对应的机制：撞上那一刻没有任何环节出声。
  - **同形态第 2 次**：08-31 过账已记「条目自己的触发条件被满足了，却没人回来看这个条目·再撞一次即提立」。**用户 2026-09-14 裁：不立条目**，改为接线 + 焊进 [§4.2](#42-触发条件命中后的处理)——再立一条等于又添一笔靠人记得去看的账。
  - **落地**：[`scripts/lint_backlog_triggers.py`](../../scripts/lint_backlog_triggers.py)（改动路径 × 条目声明的监视对象，命中即点名）+ CI job `backlog-triggers` + pre-commit 每次提交跑。**WARN 试用期只提示不拦路**；升 hard-fail 须按 [e2e 验收标准 §4](e2e-acceptance-standard.md) 用户裁决。
  - **声明写法**（§0.2 备注格·二选一）：`〔监视 路径…〕` / `〔不可监视：理由（≥15 字）〕`。本笔补 **21** 条（12 条判据已写明位置 + 9 条结构上看不见）；**剩 7 条同 PR 内已补齐**（`ef39afe`·落点逐条查证）⇒ **28 条全部已声明：19 监视 / 9 明示看不见**，不再有「尚未声明」一档。**「不声明就判红」的开关仍未开** —— 顺序不能反，先让这批声明在真实提交上跑一段、噪音有实据再议。
  - **覆盖面如实记**：28 条里看得见 **19**、**看不见 9**（部署动作 / 阶段完成 / 运行时现象），盲区每次输出点名列出；**且被监视的 19 条也只被盯住判据里「动某个文件」那半边**（复合判据的其余子条件同样看不见），输出固定带这句提醒。
  - ⚠️ **回放出的待办清单（本笔不处置）**：拿 8 月底至今全部改动喂进去，**19 条里 13 条被点名**，其中 12 条账面仍写「未触发」——`BI` `BK` `BL` `BP` `BS` `BX` `AF-residual` `DEFECT-ANCHOR-FALSEPOS-HARDBLOCK` `DEFECT-WISBURG-PADDING` `DEFECT-CTX-BAG-SHAPE` `DEFECT-D5-COUNT-AS-VALUE` `DEFECT-RETRY-ADVICE-FALSE`。**两层折扣**：① 撞到文件 ≠ 判据语义满足（试用期声明宁宽勿窄，`BI`/`BP` 范围确实比判据宽）；② 做不做按 [§4.2](#42-触发条件命中后的处理) **逐条由用户裁** ⇒ 该专门起一轮 triage，不顺手替用户决定。
  - **验证**：九次真实提交回放 **9/9 点名**；纯文档提交 0 命中；反向变异两个全 KILLED（摘 CI 那行 → 闸门矩阵元测试变红；摘 BJ 声明 → 九次回放 9→0）；自检 24 条；全套件 **4364 passed / 0 失败**。
  - **顺带登记不处置**：`DEFECT-R5-03` 的判据是「单列·依赖有人主动排期」，属 [§4.1](#41-新增-backlog-条目) 禁止形态（条目自己已标待复核）。本笔只在其备注格记为「不可监视」，**判据文字未改**（改判据走 [§4.3](#43-触发条件本身的修改)）。
  - **配额**：配额族 **13 不变** / 非配额族 **15 不变** / 破例累计 **16 不变**。**🔴 仍 0 条**。

- **2026-09-14（第 6 笔）**：**BK BK.0/1/3/4 落地**（PR [#295](https://github.com/JunoChenZt/subagent-for-investment/pull/295) 合 main `a53b196`）。条目数不变（12 / 14 / 破例 16 / 🔴 0）；**BK 不 close**（持 BK.2）；`DEFECT-CTX-BAG-SHAPE` ⑦ 定锚 close；盘点推翻方案数字（44 → 58）。
- **2026-09-14（第 5 笔）**：**BJ.5 五族落地 → BJ ✅ CLOSED（close-by-completion·PR [#294](https://github.com/JunoChenZt/subagent-for-investment/pull/294) 合 main `d423dad`）**；配额族 **13 → 12**；BK (D) 转 🔔 已触发待裁；翻案 #210 旧契约（import 期报错）。
- **2026-09-14（第 4 笔）**：**`PRICE-V4PRO-CUTOVER` ✅ CLOSED（close-by-completion·PR [#293](https://github.com/JunoChenZt/subagent-for-investment/pull/293) 合 main `742f04a`）** —— 到期处置按登记改完（v4-pro 与 flash 同价 / 登记删除 / 4 条测试改）；回包名实证仍是 v4-pro。非配额族 **15 → 14**。
- **2026-09-14（第 3 笔）**：**BJ CFG-READ BJ.0–BJ.4 落地**（PR [#292](https://github.com/JunoChenZt/subagent-for-investment/pull/292) ✅ 合 main `3aeb118`·分支已删·[复盘](../retro/S2/BJ_2026-09-14.md)）。**零新增零关闭**（13 / 15 / 破例 16 / 🔴 0）；BJ 不 close、BJ.5 五族待裁；闸门点名 BL / BM 均判不算（BM 用户裁）；BK (D) 半满足。
- **2026-09-14（第 2 笔）**：**首轮判据命中 triage**（PR [#291](https://github.com/JunoChenZt/subagent-for-investment/pull/291) ✅ 合 main `fb8dbd6`·承接同日第 1 笔接线·方案 [trigger-wiring-2026-09-14](../plans/trigger-wiring-2026-09-14.md)）。**零新增、零关闭，三项计数全不变。**
  - **为什么有这一轮**：闸门接上线后回放「8 月底至今全部改动」，19 条监视声明里 **13 条被点名**、其中 12 条账面仍写「未触发」。用户拍板起一轮过账。
  - **查法（关键）**：**不认「文件撞上」**。逐条打开 diff 核「判据点名的那一块」动没动 —— 实测这一步把结论改了一半。⚠️ 中途自纠一次：先前按 `grep -c` 数「`_TOOL_TIMEOUT` 命中 1 处」，实为**上下文行**不是改动行；只看计数会把 BL 误判成满足。
  - **3 条真满足 → 只订正账面**（用户裁）：`DEFECT-CTX-BAG-SHAPE` · `DEFECT-WISBURG-PADDING` · `DEFECT-RETRY-ADVICE-FALSE`。状态改 🔔 已触发并写明证据，**判据文字一字未改**（守 [§4.3](#43-触发条件本身的修改)），开工时机另议。
  - **1 条已处理**：`DEFECT-ANCHOR-FALSEPOS-HARDBLOCK`（09-10 已裁「再留一轮」）。
  - **2 条不算触发**（用户裁）：`BK` / `DEFECT-D5-COUNT-AS-VALUE` —— 只加注释、行为未变。但把注释里的新事实记进账面，真做时用得上。
  - ⚠️ **6 条误报 = 粒度差**：判据点「文件里的某一块」，本闸只看得见「哪个文件动了」。处置：**能收的收窄**（`BI` 整个源目录 → wisburg 单文件；`BP` 整个 `common_context/` → 两份文件）、**收不了的加 `〔粗粒度：…〕`**，命中时输出自带「可能空喊」。同一份改动回放 **13 → 12 条**，5 条带标注。
  - **闸门本体同笔小改**：新增 `〔粗粒度：…〕` 标记（只能与 `〔监视〕` 同在，单独出现判错），命中时打印「⚠ 粗粒度·可能空喊」；自检 30 条（+2）。
  - **配额**：配额族 **13 不变** / 非配额族 **15 不变** / 破例累计 **16 不变**。**🔴 仍 0 条**。
