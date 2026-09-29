# 案例：给 `report` 子命令加 `--json` 输出

> 父文档: [00-quickstart.md](../00-quickstart.md)
> 目的: 把 10 步主链路从头走一遍，每步给出**实际写出来的那段东西**。任务是虚构的、足够小，但每个环节都真实出现。冒烟那一步故意落在 ⚪ 未验证，演示第三态。

## 用户指令

> 给 `report` 子命令加一个 `--json` 选项，输出完整结构而不是渲染后的文本。给下游脚本用。

---

## 第 1 步 · 任务进入（[01 §2.1](../01-task-entry.md#21-大任务进入)）

```
任务类型: temp-instruction（用户即时指令，不对应路线图节点）
是否大任务: true
命中: 「涉及 2 个以上模块」（cli 层 + 渲染层）+ 「涉及新增能力，而非单点 bugfix」
```

两条命中，按大任务走。**不是大任务**的话这里就直接跳到第 4 步。

## 第 2 步 · 风险判定（[01 §2.2](../01-task-entry.md#22-风险判定5-条触发即高风险)）

```
风险层级: 低
理由: 五条逐一对照 —— 不碰 schema / prompt / fallback / 路由；不碰决策路径；单 phase；无新外部依赖；不动 archive 格式（只是多一种输出形态，读的仍是同一结构）
```

低风险 → 自走，不需要用户确认拆解方案。

## 第 3 步 · Pre-flight 5 问（[02 §2.3](../02-pre-flight.md#23-节点切入-5-问pre-flight-check)）

```
1 依赖: 无上游节点；依赖现有 render_report() 的输入结构已稳定 ✅
2 并行: 无并行节点在动 cli.py / render.py（git log -5 -- 两文件 核过）
3 风险档位: 低（第 2 步）
4 time budget: 1 个 goal，预计 ≤ 30 分钟
5 Fallback: --json 序列化失败 → 退回文本输出 + stderr 打一行原因，不让命令整体崩
```

## 第 4 步 · 拆解（[03 §2.4.3](../03-decomposition.md#243-goal-xml-模板)）

只需一个 goal：

```xml
<goal id="TMP-json.1" parent_node="TMP-json" risk_level="low">
  <objective>report 子命令支持 --json，输出与文本版同源的完整结构</objective>
  <scope>
    <allow>
      <path>src/app/cli.py</path>
      <path>src/app/render.py</path>
      <path>tests/test_cli_report.py</path>
    </allow>
    <forbid>
      <path>src/app/schemas/</path>
      <reason>输出结构沿用现有 schema，不在本 goal 改</reason>
    </forbid>
  </scope>
  <dependencies/>
  <steps>
    <step n="1">render.py 抽出 build_report_model()，文本渲染与 json 共用</step>
    <step n="2">cli.py 加 --json flag，走 model_dump(mode="json")</step>
    <step n="3">补测试：--json 输出可被 json.loads；与文本版字段一致；序列化失败退回文本</step>
  </steps>
  <verification>
    <command>pytest tests/test_cli_report.py -v</command>
    <command>python -m app report --ticker DEMO --json | python -c "import sys,json; json.load(sys.stdin)"</command>
    <smoke>1 single_ticker 端到端，比较 --json 与文本版字段集合</smoke>
  </verification>
  <done_criteria>
    <criterion>三条新测试通过，原有测试不回归</criterion>
    <criterion>--json 输出字段 ⊇ 文本版渲染用到的字段</criterion>
  </done_criteria>
  <stop_conditions>
    <condition>需要改 schemas/ 下任何文件 → 停，回来重拆</condition>
    <condition>DoD ❌ ≥ 3 次 → 升级重拆</condition>
  </stop_conditions>
  <fallback>
    <description>序列化异常 → 文本输出 + stderr 一行原因，exit 0</description>
  </fallback>
</goal>
```

## 第 5 步 · 执行（[04 §2.5](../04-goal-execution.md#25-单个-goal-执行)）

执行前自检：三个文件都在 allow 里 ✅；无 upstream ✅；stop_conditions 已注入。

按三个 step 各一个 commit。step 2 时发现渲染层直接读了一个私有字段，json 版拿不到 —— 这是「顺手改」的诱惑点：**没有**去改 schema，而是在 build_report_model() 里显式取值。scope 守住。

## 第 6 步 · 自验（[04 §2.6](../04-goal-execution.md#26-goal-达成自验)）

```markdown
## Self-verification Report
- Goal: TMP-json.1
- Commands run: 2
- Pass: 2 / Fail: 0
- Smoke: unverified(a)
- Unverified: smoke —— 本机无 LLM API key，端到端拉不起来；两条 command 用的是 fixture 数据
- Fallback ratio: N/A（未跑端到端）
- P50 / P95: N/A
```

## 第 7 步 · 刹车 8 问（[05 §2.7](../05-brake-self-check.md#27-刹车自检8-问)）

```
1 生产可用性: 否（新 flag 默认关）
2 敏感配置: 否
3 合规 / 北极星: 否
4 不可逆: 否
5 降低标准: 不确定 → smoke 没跑。对照 06 §2.8.0 三条边界：不是"能跑没跑"，是环境缺 key（原因 a）；不是跑了红。判定：属 ⚪，不属 Q5。但按规则如实标出，交付时由用户决定。
6 历史改写: 否
7 用户成本: 否
8 多方案: 否（--json 是唯一合理形态）
```

Q5 那一行的自问是关键：**「不确定」本身就要求写清楚判据**。这里判成 ⚪ 而非 Q5 的依据是原因闭集 (a)，而不是"应该没问题"。

## 第 8 步 · DoD 三态（[06 §2.8.0](../06-dod-and-evidence.md#280-每一步的结果只有三态2026-09-29-立)）

| 步 | 态 | 说明 |
|---|---|---|
| Code Review | ✅ | self-review：无隐式 skip；三条测试都无条件 assert；mock 只罩 LLM 调用不罩序列化 |
| Corner Case | ✅ | 新增 3 条 + 原 12 条全过；`--json` 与空结果 / 缺字段 / 非 UTF-8 三种边界各一条 |
| 冒烟 | ⚪ | 原因 (a) 无 API key；fixture 版两条 command 已过，但**不算**端到端 |
| 彻底跑通 | ✅ | 无 known issue skip；`find` 临时脚本检查为空 |

**计数：✅ 3 / ❌ 0 / ⚪ 1** → 无 ❌，进 evidence。

## 第 9 步 · Evidence + 交付单（[06 §2.9](../06-dod-and-evidence.md#29-evidence-收集)）

```markdown
## Evidence Summary (goal TMP-json.1)
- Review notes: 本 PR 描述「Code Review」段
- Corner case logs: tests/_archives/20260929-1410.log
- Smoke archive: N/A（⚪，见交付单第三栏）
- Archive replay: N/A（不动 schema）
- Modified cases: 0
- 裁决回填清单: N/A（本 goal 无裁决落地）
- DoD 三态计数: ✅ 3 / ❌ 0 / ⚪ 1
- 交付单: 见下

## 交付单 (goal TMP-json.1)

### 改了什么
- src/app/render.py：抽出 build_report_model()，文本渲染改为消费它
- src/app/cli.py：report 子命令加 --json；序列化失败退回文本 + stderr 一行
- tests/test_cli_report.py：+3 条（可解析 / 字段一致 / 失败退回）

### 验证了什么、怎么验的
- 单测：pytest tests/test_cli_report.py -v → 15 passed（3 新 + 12 原有，全集 = 该文件全部用例）
- 可解析：python -m app report --ticker DEMO --json | json.load → 成功（fixture 数据）
- 字段集合：测试内比较 model 字段 ⊇ 文本模板引用字段 → 成立（模板引用字段用正则从 render.py 扫出，共 11 个）

### 未验证什么、为什么
- 冒烟（真实 LLM 端到端）⚪：原因 (a) 本机无 API key → 建议处置：请用户在有 key 的环境跑一次 `python -m app report --ticker <真实代码> --json`，或接受 fixture 版结果后合并
```

第三栏 1 条 = ⚪ 计数 1，对账通过。**全文没有出现「全部通过」**。

## 第 10 步 · Retro 触发判定（[07 §2.10.1](../07-retro-goal.md#2101-触发条件6-条触发即跑-retro)）

```
1 返工: 否   2 刹车命中: 否（Q5 判为 ⚪ 非命中）   3 意外坑: 否
4 改 case / 改契约 / 加 deferred: 否   5 ≥3 次重做: 否   6 高风险节点: 否
→ 6 条全否，跳过 retro
```

## 第 11 步 · 交付（对话收尾 + PR 描述节选）

对话里给用户的最后一段，就是交付单三栏原样贴出，再加一句：

> 冒烟没跑是因为本机没有 API key，不是没来得及。你可以在有 key 的环境跑上面那条命令，也可以按 fixture 版结果直接收。

PR 描述按 [08 §6](../08-retro-node-and-pr.md#6-pr-描述模板决策溯源) 模板，「DoD 三态」和「交付单」两段直接复用第 8、9 步内容，「风险与 Fallback」段写：

```
- 风险层级: 低
- 引入的 Fallback: 序列化失败 → 文本输出 + stderr
- §2.7 8 问: 未触发（Q5 自问后判为 ⚪ 未验证，见交付单第三栏）
```

---

## 这个案例想说明的三件事

1. **大部分步骤是几行字，不是几页纸。** 判定、5 问、8 问、retro 触发，写出来都是一屏以内。流程重不重取决于任务，不取决于步骤数。
2. **第三态让「没跑」有地方放。** 没有 ⚪ 时，第 6 步的 smoke 要么被写成 pass，要么整个 goal 卡死等 key。有了 ⚪，它是一个如实的、可交付的、由人裁的状态。
3. **对账是防架空的兜底。** 「第三栏条数 = ⚪ 计数」这种机械检查，比"请如实报告"管用。
