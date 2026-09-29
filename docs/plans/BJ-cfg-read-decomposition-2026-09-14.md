# BJ · 配置读取机械化（CFG-READ）—— 拆解方案（2026-09-14）

> **性质**：高风险节点的拆解方案，**等用户确认后才开工**（[03 §2.4.5](../governance/workflow/03-decomposition.md)）。本文不动任何代码。
> **上游**：backlog 条目 [BJ](../governance/backlog.md)（2026-09-14 已触发·用户裁「现在做」）· [S2 §9.2 CFG-READ-机械化](../roadmap/S2.md) · [闸门矩阵三层方案 §2](gate-matrix-mechanization-2026-08-07.md) · [第 0.5 层方案 §2](trigger-wiring-2026-09-14.md)（判本条高风险的出处）。
> **起因事故**：2026-06-16 把代码里的名字 `EXTERNAL_SEARCH_URL` 当成环境变量真名（真名 `COMMITTEE_EXTERNAL_SEARCH_URL`）去查，查空 → 误判"没配置"（[D ledger §1 环境就绪栏](../observations/fm-refactor-spec/D-hot-e2e-2026-06-16/LEDGER.md)·[META 观察实例 #3](../observations/meta-assume-mechanism-without-verify.md)）。
> **已知坑扫描**：pitfall-scout 2026-09-14 返回 5 条（全部 active），逐条落进下方各 goal 的 `<stop_conditions>`；原文见 §6。
> **🔧 落地口径（2026-09-14·本行是导航就地改；下文各节 point-in-time 不动）**：BJ.0–BJ.4 已落地（PR [#292](https://github.com/JunoChenZt/subagent-for-investment/pull/292) ✅ 合 main `3aeb118`·分支已删），与下文拆解的差异：
> ① BJ.2 的运行时侧逻辑放**新模块** [config_explain.py](../../src/committee/config_explain.py)（名册模块须保持纯标准库、可按路径单独加载，不能装运行时逻辑）；并在 [committee/__init__.py](../../src/committee/__init__.py) 加一行 `ENV_AT_IMPORT` 快照（不加就分不出「进程 env」与「.env」，坑①）。
> ② BJ.3 碰了 [graph.py](../../src/committee/graph.py) 的 `run_committee` **起步段**（run 目录定一次 + 写快照）与 `_emit_segment_artifacts` 传参 —— 是 I/O 接线、不是图拓扑；`<forbid>` 的本意（不动拓扑）仍守。顺手修了缺省落点带时间戳时起步/落盘各算一次会分家的既有隐患。
> ③ BJ.4 `<allow>` 补上两份 env 模板与 [architecture/overview.md](../architecture/overview.md)（盘点 §2.1/2.2 的 40 缺键 / 2 死键要在模板上收口）。
> ④ BJ.1 派生器两处盲区各由真仓对账撞出后补上（元组循环读键 / 函数体内 import），均已进靶测。
> ⑤ **BJ.5 五族已按用户 2026-09-14 逐类裁决落地**（PR [#294](https://github.com/JunoChenZt/subagent-for-investment/pull/294) ✅ 合 main `d423dad`）：(a) 保持 · (b) 填错字起步报错（翻案 #210「不得在 import 期抛」旧契约，理由只是"整包导不进"= 要的效果）· (c) `_env_bool` 封闭集合成唯一读法 · (d) 未登记键 WARN 四处现形 · (e) 归并折中（pass0 两处直转 + 一处 config 内直转改夹钳；三个网关键从 base.py 归并；其余登记例外）。下文 §5 BJ.5 的选项表 point-in-time 不动。
> 证据：BJ.3 真跑 [bj-cfg-snapshot-e2e-20260914](../observations/bj-cfg-snapshot-e2e-20260914/FINDINGS.md)。

---

## 大白话导读（不需要懂代码）

### 出了什么事

这套系统有几十个"旋钮"（用哪个模型、超时多久、开不开某个开关），旋钮的值可以从三层来：当场的环境、本机的配置文件、代码里写死的默认值。今天要知道"某个旋钮现在到底是多少、从哪层来的"，办法是**人去翻代码和配置文件、凭经验找**。

6 月那次事故就是这么来的：翻代码看到一个名字，以为它就是配置项的名字，去环境里查，查不到，判成"没配置"。其实那只是代码里的内部叫法，真名多了个前缀。**没有任何东西告诉查的人"你查的这个名字根本不存在"**——它只是安静地返回空。

后来又发现同一个病换了个形状：跑批指南里抄的那些数字线（超时多少、上限多少）会过期，因为它们也是人手抄下来的（[#155](https://github.com/JunoChenZt/subagent-for-investment/pull/155) 一次对齐了 4 处）。

### 要做什么（一句话）

**把"查配置"从一件靠人小心的事，改成一条命令；问错名字当场报错，而不是安静给空。**

具体分五步，前四步不改系统任何行为，只是加读取工具和改文档：

1. **盘点**：先数清楚到底有多少个旋钮、各自在哪里读、哪些没写进模板。现在手里的数字（57 个、27 个没登记、35 处散读）是一次粗查得来的，开工前要按更严的口径重数一遍。
2. **旋钮名册**：从代码自动生成一份"合法旋钮清单"，不靠人手维护。名字不在册上就是不存在。
3. **一条查询命令**：问"某旋钮现在多少"，答"值 + 从哪层来 + 是不是走了兜底"。问一个不在册上的名字 → **报错**，这就是 6 月事故的解药。密码类的旋钮只报"设了/没设"，永远不显示值。
4. **每次跑批开头自动存一份配置快照**：以后核对"这次跑用的是什么配置"看快照，不翻文件。快照同样不含任何密钥。
5. **文档改口**：跑批指南、运维手册里所有"去某文件看某项"的说法，改成"跑这条命令"。

### 哪一步是真的有风险、要你拍板

第五步之外还有一个**第六步**：让系统在**运行时**遇到"读不到 / 读错"就报错、不再悄悄退回默认值。这才是真正改变系统行为的部分——比如某个角色的模型名写错了，今天会悄悄用默认模型跑完，改了之后会直接停下来。

这一步**每一类兜底单独裁**（§4 列了五类，各给保守 / 折中 / 激进三档），本轮默认只做前五步；第六步等你逐类拍板后另开。

### 这轮不做什么

- 不改任何旋钮的默认值、不改任何兜底逻辑（那是第六步，单独裁）。
- 新加的检查一律先"只提醒不拦路"（仓里规矩：新检查 WARN 试用，升硬拦要你裁）。
- 不把密钥写进任何落盘产物。

---

## 技术正文

### 1. 顶层对齐（[02 §2.3 第 0 问](../governance/workflow/02-pre-flight.md)）

- [S2 §9.2 CFG-READ-机械化](../roadmap/S2.md) 终态原文：**「e2e 中"读配置/定位来源"类确定性步骤，从"AI 照 guide 即兴查找"机械化为"代码/工具确定性读取，读不到即明确报错、不静默回退"。guide 活链接化是过渡非终态。」**
- [gate-matrix §2](gate-matrix-mechanization-2026-08-07.md)：本层要碰**配置读取路径**，与第 0 层（闸门元治理）分档。
- ⚠️ 终态那句「读不到即明确报错」有**两种读法**，本方案把它们拆开：
  - **读法 A（查询侧）**：查询工具对"不存在的键名"报错，对"存在但未设"报"未设·走默认"。**不改运行时行为**。= BJ.1–BJ.3。
  - **读法 B（运行时侧）**：系统起步时读到非法值 / 缺值就报错，不回退。**改兜底行为** = 高风险。= BJ.5，逐族裁。
  - 事故的直接病因是读法 A 缺失（查了个不存在的名字没人喊）；读法 B 是终态措辞的字面延伸，[第 0.5 层方案 §2](trigger-wiring-2026-09-14.md) 判高风险正是冲它。

### 2. 现状一手（2026-09-14 查·数字附计数方法，开工 BJ.0 重核）

| 事实 | 数 | 计数方法 | 盲区（BJ.0 要补） |
|---|---|---|---|
| `config.py` 里 `os.getenv` 读取处 | ~30 | `grep -n "os.getenv" src/committee/config.py` | 不含 `_clamp_int/_clamp_float` 的间接读 |
| `config.py` **之外**直读 `os.environ/getenv` | 35 处 / 15 模块 | `grep -rn "os.environ\|getenv" src/committee` 去掉 config.py | 只认这两种写法；`from os import getenv`、`environ[...]` 没扫 |
| 源码里出现的 `COMMITTEE_*` 键 | 57 | 字面量 grep 去重 | **动态拼键**（`f"COMMITTEE_MODEL_{role}"`、`COMMITTEE_TEMPERATURE_{stage}`）只算到前缀 |
| 其中 `.env.example` 没有的 | 27 | `comm -23` | 同上；且非 `COMMITTEE_` 前缀的第三方键（`TUSHARE_TOKEN` 等）未计 |
| 同一键在 >1 文件里被读 | 5 个（`TUSHARE_TOKEN` 3 文件·`FRED_API_KEY`/`WISBURG_API_KEY`/`DEEPSEEK_API_KEY`/`OPENAI_BASE_URL` 各 2） | 逐键 grep 文件数 | — |
| 测试面 | 87 个测试文件 import `committee.config`；20 个 `monkeypatch.setenv("COMMITTEE_…")` | grep -l | — |
| 已有可复用件 | [lint_env_shadowing.py](../../scripts/lint_env_shadowing.py)（BG·CLOSED）已用 AST 从源码枚举「env 键 → 符号 → 默认值」（`_env_read` / `collect_env_symbols`）；[healthcheck.py](../../scripts/healthcheck.py) 已按角色 ping 模型 | — | 它只追 `_READERS = {"_clamp_int","_clamp_float","getenv","get"}`，不追派生链 |
| 跑批产物今天记了什么配置 | `calls.jsonl` 每次调用带模型名；**超时 / 开关 / 引擎集等一概不记** | 看 [run-nvda-20260908](../observations/ctx-shadow-e2e-20260908/run-nvda-20260908/) 三件套 | — |
| 文档里"去哪读配置"的说法 | [segmented-e2e-guide.md](../observations/e2e-runs/segmented-e2e-guide.md)（`MAX_CONTINUATIONS=3` 等数字线）· [prod-runbook.md](../infrastructure/prod-runbook.md)（`COMMITTEE_MODEL_<ROLE>` 优先级段·`.env.example:89` 推荐值 OPEN 项） | grep | handoff / LEDGER 类历史文档不改（point-in-time） |

**今天的静默回退形态（BJ.5 的裁决对象）**——全部出自 [config.py](../../src/committee/config.py)：

| 族 | 现行为 | 例 |
|---|---|---|
| (a) 角色模型回退 | `model_for_role`：`COMMITTEE_MODEL_<ROLE>` 未设 → 静默用 tier 常量 | 坑表实证 B：守卫比的是 tier 常量，线上每角色实配不同 |
| (b) 数值夹钳 | `_clamp_int/_clamp_float`：非法值 → `log.warning` + 回退默认；越界 → 夹回 | 坑表明说这是**保守方向**，别一刀切 |
| (c) 布尔开关 | `raw in ("1","true","yes","on")`：拼错（`ture`）= 静默关 | `COMMITTEE_PROMPT_CACHE` / `FORCE_OPENAI_COMPAT` / `EVIDENCE_MISMATCH_REVIEW` … |
| (d) 未登记键 | 环境里有 `COMMITTEE_XXX` 但代码从不读 → 无任何提示 | 键名拼错整条配置失效且无声 |
| (e) 散读 | 15 模块各自 `os.environ.get`，各带各的默认 | `TUSHARE_TOKEN` 三处各读一遍 |

### 3. 风险判定（[01 §2.2](../governance/workflow/01-task-entry.md)）

```
风险层级: 高
理由: 仅 BJ.5 触及条件 1（Fallback 行为本身）；BJ.0–BJ.4 五条全不触发（不动 schema / prompt / 路由 / 外部依赖 / archive replay，
      新增物为只读工具 + 落盘快照 + 文档）。整体按高走 → 本方案须用户确认；确认后 BJ.0–BJ.4 各自低风险自走。
```

### 4. 节点切入 5 问（[02 §2.3](../governance/workflow/02-pre-flight.md)）

| # | 答 |
|---|---|
| 1 依赖 | 第 0.5 层 [#290](https://github.com/JunoChenZt/subagent-for-investment/pull/290) ✅ 合 main `200007a`；BG 的 [lint_env_shadowing.py](../../scripts/lint_env_shadowing.py) ✅ 在 main（复用其枚举）。无其他上游 |
| 2 并行块 | 撞文件核对：`config.py` 当前无进行中分支在动（CRED 簇 2 未开工；`PRICE-V4PRO-CUTOVER` 到期动作改的是 token 价目表不是 config）。BJ.4 改 guide —— guide 是高频改动文件，走 rebase 即可 |
| 3 风险档位 | 高（因 BJ.5）；不触 hard_block / breaking → 普通 PR review gate，不需 ≥30 runs / 14d |
| 4 time budget | BJ.3 在 run 起步多一次进程内读取 + 一次小文件写，毫秒级，不落任何 phase 预算 |
| 5 Fallback | BJ.2 是只读命令，失败 = 命令报错，主链路无感。BJ.3 快照写失败 → **起步即报错退出、不带病跑**（写不进 trace-dir 的跑批后面的 trace.md 同样写不进；静默无文件 = 坑表"空过"形态） |

### 5. Goal 拆解

> 分支：`auto/BJ`。顺序 BJ.0 → BJ.1 → BJ.2 → BJ.3 → BJ.4；BJ.5 **不在本轮**，逐族裁后另开分支。

```xml
<decomposition_output node="BJ" risk_level="high">
  <user_confirmation_required>true</user_confirmation_required>

  <goal id="BJ.0" parent_node="BJ" risk_level="low">
    <objective>盘点：把"读配置"类确定性步骤列全，并按更严口径重核 §2 的每个数字。零代码改动。</objective>
    <scope>
      <allow><path>docs/plans/BJ-G0-inventory-2026-09-14.md</path></allow>
      <forbid><path>src/**</path><reason>只读盘点</reason></forbid>
    </scope>
    <dependencies><upstream status="done">#290 第 0.5 层</upstream></dependencies>
    <steps>
      <step n="1">用 AST（复用 lint_env_shadowing._env_read 的枚举，不另写第二套）重数：所有 os.environ / os.getenv / from os import getenv / environ[...] 读取处，含动态拼键；每个数附"计数方法 + 成立条件"</step>
      <step n="2">15 模块散读逐处裁决表：归并进 config.py / 登记为例外（如 fred_source 文档明写"仅只读 os.environ"的红线）</step>
      <step n="3">列出 e2e guide / runbook / 段间 checklist 里所有"人去读配置"的步骤（= BJ.4 的改口清单）</step>
      <step n="4">列出密钥类键（名含 KEY / TOKEN / SECRET / PASSWORD + 显式补录）= BJ.2/BJ.3 的脱敏名单</step>
    </steps>
    <verification><command>盘点表每个数字旁有计数命令，可重跑</command></verification>
    <done_criteria>
      <criterion>§2 的 57 / 27 / 35 三个数各自重核并写明差异</criterion>
      <criterion>散读逐处裁决表无"待定"行</criterion>
    </done_criteria>
    <stop_conditions>
      <condition>【坑④ 枚举完整性】任一计数只靠单一 grep 写法、没附成立条件 → 不许写进表</condition>
      <condition>盘点发现散读处 > 50 或密钥键名单无法闭合 → 停下报，重估 BJ.1 形状</condition>
    </stop_conditions>
    <fallback><description>纯文档，无运行时影响</description></fallback>
  </goal>

  <goal id="BJ.1" parent_node="BJ" risk_level="low">
    <objective>旋钮名册：从源码派生的"合法 env 键"单一真值（不手写清单）+ 两条 lint（WARN 试用）。</objective>
    <scope>
      <allow>
        <path>src/committee/config_registry.py</path>
        <path>scripts/lint_env_registry.py</path>
        <path>scripts/lint_env_shadowing.py</path>
        <path>tests/test_config_registry.py</path>
        <path>.github/workflows/ci.yml</path>
      </allow>
      <forbid><path>src/committee/config.py</path><reason>本 goal 不改任何读取行为；只从它派生</reason></forbid>
    </scope>
    <dependencies><upstream status="pending">BJ.0</upstream></dependencies>
    <steps>
      <step n="1">把 lint_env_shadowing 的 AST 枚举抽成可复用函数（它继续 import 同一份，避免两套推导各说各话）</step>
      <step n="2">名册条目 = 键名 / 读取处 / 默认值 / 类型族(a–e) / 是否密钥 / 是否动态拼（动态拼记模式 + 合法后缀集：角色名来自 ROLES、stage 来自枚举）</step>
      <step n="3">lint ①：源码读了但名册推不出（= 枚举盲区）→ 红；lint ②：.env.example 出现的键（注释态也算）不在名册 → 红（防写错键名进模板）</step>
      <step n="4">接 CI job（WARN 试用，不 hard-fail）+ pre-commit</step>
    </steps>
    <verification>
      <command>pytest tests/test_config_registry.py -v</command>
      <command>python scripts/lint_env_registry.py  # 必须打印"枚举到 N 个键 / M 处读取"，N=0 即 exit 2</command>
    </verification>
    <done_criteria>
      <criterion>名册覆盖 BJ.0 重核后的全部键（含动态拼）</criterion>
      <criterion>反向变异：往 .env.example 塞一个拼错键 → lint ② 红；往 src 加一处 environ["X"] 新写法 → lint ① 红</criterion>
    </done_criteria>
    <stop_conditions>
      <condition>【坑③ 守护空转】脚本无"枚举到 N 个"断言、或 N=0 仍绿 → 不许合</condition>
      <condition>【坑① .env 罩住】测试若意在代码默认值必须 patch dotenv.load_dotenv；意在生效值必须断言写全三层来源</condition>
      <condition>发现必须手写维护的清单 > 5 行 → 停下问（手写清单 = 又一笔靠人记得的账）</condition>
    </stop_conditions>
    <fallback><description>名册是派生物，派生失败 = lint 报错，不影响运行时</description></fallback>
  </goal>

  <goal id="BJ.2" parent_node="BJ" risk_level="low">
    <objective>查询命令 `committee config explain &lt;KEY&gt;` / `committee config show`：答"生效值 + 来源层 + 是否走了回退"；问不在名册的名字 → 硬报错。</objective>
    <scope>
      <allow>
        <path>src/committee/cli.py</path>
        <path>src/committee/config_registry.py</path>
        <path>tests/test_config_explain.py</path>
      </allow>
      <forbid><path>src/committee/config.py</path><reason>只读它，不改它的任何读取 / 回退</reason></forbid>
    </scope>
    <dependencies><upstream status="pending">BJ.1</upstream></dependencies>
    <steps>
      <step n="1">来源层判定：进程 env（load_dotenv 前快照）/ .env / 代码默认 / 角色回退（逐角色调 model_for_role 记实配，不 dump tier 常量）</step>
      <step n="2">别名归一：oc/ 前缀、大小写、同义键（OPENAI_COMPAT_API_KEY or OPENAI_API_KEY）显式列出并在输出里标"实际取自哪个"</step>
      <step n="3">密钥类：只输出 已设/未设 + 来源层 + 长度或哈希前 8 位，永不输出值</step>
      <step n="4">未登记键名 → exit≠0 + 提示"不是已登记 env 键；相近的有：…"（相近推荐用名册做编辑距离）</step>
      <step n="5">首条靶测 = 06-16 事故复现：explain EXTERNAL_SEARCH_URL 必须报错而非返回空；explain COMMITTEE_EXTERNAL_SEARCH_URL 必须报"未设·走默认 workers.dev"</step>
    </steps>
    <verification>
      <command>pytest tests/test_config_explain.py -v</command>
      <command>committee config explain EXTERNAL_SEARCH_URL ; test $? -ne 0</command>
      <command>FAKE=… committee config show | grep -c "$FAKE_KEY_VALUE"  # 必须为 0</command>
    </verification>
    <done_criteria>
      <criterion>事故阳性样本靶测通过；反向变异（把"未登记即报错"改成返回 None）→ 靶测红</criterion>
      <criterion>逐角色输出的模型名与 calls.jsonl 实跑记录一致（拿一份 tracked 归档核）</criterion>
      <criterion>密钥反向靶测：塞假 key 进 env，全部输出 grep 不到该串</criterion>
    </done_criteria>
    <stop_conditions>
      <condition>【坑② 锚错对象】输出若只有模块级常量、没有逐角色实配 → 不许合</condition>
      <condition>【坑⑤ 密钥出仓】任何路径能让密钥值进 stdout / 文件 → 立即停</condition>
      <condition>【坑③】"未登记即报错"没有反向变异证明会响 → 不许合</condition>
    </stop_conditions>
    <fallback><description>新增只读子命令，失败即命令报错；analyze / serve 路径不经过它</description></fallback>
  </goal>

  <goal id="BJ.3" parent_node="BJ" risk_level="low">
    <objective>跑批起步写 config-snapshot.json 进 trace-dir（schema 同 BJ.2 输出），段间 checklist 的"配置正确"类核对改读快照。</objective>
    <scope>
      <allow>
        <path>src/committee/cli.py</path>
        <path>src/committee/trace_report.py</path>
        <path>tests/test_config_snapshot.py</path>
        <path>docs/observations/e2e-runs/segmented-e2e-guide.md</path>
      </allow>
      <forbid><path>src/committee/graph.py</path><reason>快照在 CLI 起步写，不进图拓扑</reason></forbid>
    </scope>
    <dependencies><upstream status="pending">BJ.2</upstream></dependencies>
    <steps>
      <step n="1">analyze 起步（含 --resume 续跑）写 &lt;trace-dir&gt;/config-snapshot.json；续跑时与首段快照 diff，不同即在 trace.md 顶部打一行 WARN（不拦）</step>
      <step n="2">写失败 → 起步报错退出（不带病跑）</step>
      <step n="3">guide "每段产出 3 件" 改为 4 件；§① 段间 checklist 的模型路由 / 数字线核对改为"读快照字段 X"</step>
    </steps>
    <verification>
      <command>pytest tests/test_config_snapshot.py -v</command>
      <smoke>一次 --stop-after context 段式跑（真跑·按 segmented-e2e-guide）：产出含快照；快照里 grep 不到任何密钥串；逐角色模型名与该跑 calls.jsonl 一致</smoke>
    </verification>
    <done_criteria>
      <criterion>快照落在 trace-dir 且随 observation 归档进 main 时无密钥（用 scripts/check_secrets.py 扫一遍）</criterion>
      <criterion>续跑配置漂移 WARN 有反向变异证明会响（改一个 env 再 --resume → trace.md 顶部出现 WARN）</criterion>
    </done_criteria>
    <stop_conditions>
      <condition>【坑⑤】快照 schema 未先定密钥脱敏规则 → 不许写第一行代码</condition>
      <condition>【坑③】快照写失败被 try/except 吞掉 → 不许合</condition>
      <condition>快照需要改 graph / checkpoint schema 才能实现 → 停下问（那是 archive replay 面）</condition>
    </stop_conditions>
    <fallback><description>写失败即起步失败；不影响已有归档的读取（快照是新增文件，旧 run 目录没有它也能 --resume）</description></fallback>
  </goal>

  <goal id="BJ.4" parent_node="BJ" risk_level="low">
    <objective>文档改口：所有"去某文件看某配置"的活步骤改为"跑 committee config explain …"；历史文档不动。</objective>
    <scope>
      <allow>
        <path>docs/observations/e2e-runs/segmented-e2e-guide.md</path>
        <path>docs/infrastructure/prod-runbook.md</path>
        <path>docs/governance/workflow/09-known-pitfalls.md</path>
        <path>docs/governance/backlog.md</path>
        <path>docs/roadmap/S2.md</path>
      </allow>
      <forbid><path>docs/observations/**/LEDGER.md</path><reason>point-in-time 记录，R7 只加不改</reason></forbid>
    </scope>
    <dependencies><upstream status="pending">BJ.2</upstream></dependencies>
    <steps>
      <step n="1">按 BJ.0 第 3 步清单逐条改口；数字线（如 MAX_CONTINUATIONS=3）改为"以快照字段为准"，正文不再抄值</step>
      <step n="2">S2 §9.2 状态 + BJ 条目按 §2.9.4 八格回填；BJ 触发 (C)"写/改去哪读配置的文档"从此由 BJ.1 lint ② 兜住</step>
      <step n="3">R7 宽 grep 收口：config.py / .env.example / "去 … 查" 全仓扫，live 改口、历史加 banner</step>
    </steps>
    <verification><command>python scripts/lint_doc_links.py</command><command>grep 复扫：live 文档里"去 config.py 看"类措辞清零</command></verification>
    <done_criteria><criterion>guide 里不再有手抄配置值</criterion></done_criteria>
    <stop_conditions><condition>改到 handoff / LEDGER 正文 → 停（Q6 冻结档）</condition></stop_conditions>
    <fallback><description>docs-only</description></fallback>
  </goal>

  <goal id="BJ.5" parent_node="BJ" risk_level="high" status="NOT-IN-THIS-ROUND">
    <objective>运行时"读不到 / 读错即报错、不静默回退"—— §2 五族逐族裁后另开分支。</objective>
    <steps>
      <step n="1">(a) 角色模型回退：保持 / 回退时 log.warning / 回退时报错 —— 三选一</step>
      <step n="2">(b) 数值夹钳：保持（坑表：保守方向）/ 仅非法值报错、越界仍夹 —— 二选一</step>
      <step n="3">(c) 布尔拼错：不在 {1,true,yes,on,0,false,no,off,空} 即报错 —— 做 / 不做</step>
      <step n="4">(d) 环境里存在未登记 COMMITTEE_* 键：起步 WARN（试用）→ 升硬拦须再裁</step>
      <step n="5">(e) 15 模块散读：按 BJ.0 裁决表归并 / 登记例外</step>
    </steps>
    <stop_conditions><condition>任一族改动前须用户逐族裁；【坑表】默认拒绝+豁免集会变 treadmill，红线按方向划</condition></stop_conditions>
  </goal>
</decomposition_output>
```

### 6. pitfall-scout 原文（2026-09-14）

| # | 坑（§3.2 通用） | 严重度 | 落在哪个 goal |
|---|---|---|---|
| ① | 断言 config 常量前先证 .env 没罩住它；读出来的是生效值不是默认值；CI 无 .env | 🟡 | BJ.1 / BJ.2 测试写法 |
| ② | 守卫要锚在真正要守的对象上（tier 常量 ≠ 逐角色实配；oc/ 前缀先剥） | 🔴 | BJ.2 输出必须逐角色 |
| ③ | 判据挂在结构上不会响的信号上；扫描类守护要断言"扫到 N 个"；落地必做反向变异 | 🔴 | BJ.1 lint / BJ.2 未登记即报错 / BJ.3 写失败 |
| ④ | 枚举型验证宣称全绿前先证工具看得见全部对象（动态拼键、别名导入是盲区） | 🔴 | BJ.0 重核三个数 |
| ⑤ | 密钥永不明文（§3.9 原则跨段适用）：快照落盘 = 进 main | 🔴 | BJ.2 / BJ.3 脱敏 + 反向靶测 |

### 7. 要用户裁的（确认本方案 = 对下面各项表态）

1. **本轮范围 = BJ.0–BJ.4，BJ.5 逐族另裁** —— 同意 / 调整？
2. **名册走"从源码派生"而非手写**（推荐）—— 代价：动态拼键要靠模式 + 合法后缀集；收益：没有第二笔靠人记得的账。
3. **快照随 observation 归档进 main**（推荐，因已脱敏）—— 还是只留本地？
4. **BJ.5 五族**现在先表个倾向也行，不表就等 BJ.4 收口后再议（BK 那条明写"BJ 收口后重评"，两层同源，届时一起看）。

### 8. 明确不做

- 不改 `config.py` 任何读取 / 默认 / 回退（BJ.5 之前）。
- 不升任何新检查为 hard-fail（[e2e-acceptance-standard §4](../governance/e2e-acceptance-standard.md) 试用期规则）。
- 不动 BK；不改历史 LEDGER / handoff 正文。
- 不在快照或命令输出里放任何密钥值。
