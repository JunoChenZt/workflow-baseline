# 10 Verification Report — 子阶段交接审视

> 父文档: [docs/governance/workflow.md](../workflow.md)
> 关联子文档: [docs/governance/workflow/09-known-pitfalls.md](09-known-pitfalls.md) / [docs/governance/workflow/07-retro-goal.md](07-retro-goal.md) / [docs/governance/workflow/11-cadence.md](11-cadence.md)
> 关联 skill: `verification-report`（设计见 [docs/governance/skill-design.md §3.2](../skill-design.md#32-verification-report)）

## 何时读这份文档

子阶段交接时（S2.1 → S2.2 / S2.2 → S2.3 / S2.3 结束）。每个子阶段仅触发一次。subagent 化执行：跑 §4.2 全套审视，输出 PASS/FAIL。

## 概览

§4.1 触发时机 + 通过标准（每子阶段独立 gate）+ §4.2 审视清单（已知坑 status / observation 累积 / 经验值审视 / WIP 审视）+ §4.3 落地路径 + §4.4 FAIL 处理 + §4.5 完整模板。

---

## 4. Verification Report 触发点

### 4.1 触发时机

| 时机 | 必含 | 通过标准（pass/fail gate）|
|---|---|---|
| S2.1 完成 | S2.1 Verification Report + 稳定性专项验证（[docs/roadmap/S2.md §8.3](../../roadmap/S2.md)）+ PR-8c readiness 文档 | 6 项 hard-fail（m4/m5/m6/m7/m8/m13）= 0；fallback report 比例 ≤ 基线；旧 `_archives/*.json` replay 全过；time budget P95 < **120s**（2026-09-08 由 90s 抬） |
| S2.2 完成 | S2.2 Verification Report + 30 runs 数据 + 内容/格式分离诊断指标（nice）| 30 runs 中 schema hard fail = 0；F 类违规率量化 + 单次返工修复率 ≥ 80%；格式失败率不上升（如上升必书面解释）；分轮可见性 R1 封闭 / R2 半开放 / R3 收束 = byte-equal 设计 |
| S2.3 完成 | S2.3 Verification Report + S2 整体回归测试（含 archive replay）| audit / 引用渲染 / 决策日志全链路通过（见 [docs/roadmap/S2.md §5.5](../../roadmap/S2.md) must 列表全 ✅）；旧 archive replay 不崩；端到端 P50 < 60s / P95 < **120s**（2026-09-08 由 90s 抬）；thesis `{ref:fX}` 引用率 > 50% |

### 4.2 子阶段交接的审视清单

每次 Verification Report 触发时，**必看**以下内容：

1. **[09-known-pitfalls.md §3](09-known-pitfalls.md#3-已知坑--防回归-checklist) 已知坑表 status 审视**：
   - 哪些 active 项可降为 mitigated？
   - 哪些 mitigated 项可降为 stale_candidate？
   - 哪些 stale_candidate 项可标 retired_after_phase_review？
2. **`docs/observations/should_update_observations.md` 审视**：
   - 累积 ≥ 3 次的 observe → 升级 should_update 重新分流
   - 不再相关的 observation → 标 stale，归档
3. **[07-retro-goal.md §2.10.4](07-retro-goal.md#2104-retro-质量门槛数量约束) retro 数量门槛审视**：
   - 子阶段内 must_update 数量趋势？
   - 是否需要调整 1-2 个 / retro 的初始 heuristic？
4. **[11-cadence.md §5.2](11-cadence.md#52-并行节点-wip-limit) 并行节点数审视**：
   - 子阶段内并行节点数实际表现？
   - 是否触发 §5.2.2 的"降到 2 / 升到 4-5"调整？

### 4.3 落地路径

- `docs/observations/{sN}-verification-report-YYYY-MM-DD.md`

### 4.4 FAIL 处理

- 任一通过标准不达 → Verification Report 标 **FAIL**
- FAIL 不得进下一子阶段 / 启动 gate
- FAIL 具体项必须升级为该子阶段的修复 backlog 并入 [docs/roadmap/S2.md §9 Deferred](../../roadmap/S2.md) 或开新节点
- FAIL 触发 [05-brake-self-check.md §2.7](05-brake-self-check.md#27-刹车自检8-问) Q5（标准降低）→ 必须停下问

### 4.5 Verification Report 模板

```markdown
# S2.{N} Verification Report — YYYY-MM-DD

## 节点完成情况
- [节点 ID]: ✅ DONE @ <commit-hash>
- ...

## Hard-fail 检查（6 项 / 30 runs / ...）
- m4: pass / fail (+ evidence)
- ...

## 观测期数据
- Fallback ratio: X% (baseline Y%)
- P50: A ms / P95: B ms (budget Z ms)
- ...

## Archive replay
- 旧 archive 喂新 schema 全过: pass / fail
- 失败项: ...

## 子阶段已知坑表（§3.{N}）状态审视
- 🔴 active 项: 已修复 / 仍开放
- 🟡 active 项: ...
- 🟢 active 项: ...
- 本次审视调整: active → mitigated 的条目 / mitigated → stale_candidate / ...

## Observation 累积审视
- 累积 ≥ 3 次同类 → 升级 should_update 列表: ...
- 标 stale 的 observation: ...

## 经验值审视（§2.10.4 / §5.2）
- 本子阶段 must_update 平均数量: ...
- 本子阶段并行节点数实际峰值: ...
- 调整建议: ...

## 子阶段 Deferred 项
- 入 [S2todo §9 Deferred](../../roadmap/S2.md): ...

## 总判定
- PASS / FAIL
- 理由: ...
```

### 4.6 verification-report subagent 工作方式

`verification-report` 是 **subagent 化 skill**（通过 Task tool 派遣，详见 [skill-design.md §3.2](../skill-design.md#32-verification-report)）。主对话 Claude 在子阶段最后一个节点 PR 合并后调用，subagent 读 §3 全表 + 所有节点 retro + observation 累积 + ledger，输出 PASS/FAIL XML + summary。

**为什么 subagent 化**：跑 §4.2 全套审视需要读 §3 全表 + 所有节点 retro + observation 累积 + S2todo ledger，数据量大。subagent 隔离 context，主对话只接 verdict + summary。

**输入**：

- 子阶段 ID（S2.1 / S2.2 / S2.3）
- 该子阶段所有节点 retro 文件路径
- §3 当前快照
- `docs/observations/should_update_observations.md`
- S2todo 当前 ledger 状态
- 子阶段对应的 hard-fail 检查项（如 S2.1 的 m4/m5/m6/m7/m8/m13）

**输出 schema**：

```xml
<verification_report subphase="S2.1|S2.2|S2.3" timestamp="<ISO 8601>" verdict="PASS|FAIL">
  <node_completion>
    <node id="A6.1.1" status="done" commit="<hash>"/>
    <!-- 所有节点 -->
  </node_completion>

  <hard_fail_checks>
    <check name="m4" status="pass|fail" evidence="<path>"/>
    <!-- 6 项或更多 -->
  </hard_fail_checks>

  <observation_metrics>
    <fallback_ratio current="X%" baseline="Y%"/>
    <p50 current="A ms" budget="60s"/>
    <p95 current="B ms" budget="120s"/>
    <archive_replay all_pass="true|false"/>
  </observation_metrics>

  <pitfall_status_review>
    <!-- §3 当前子阶段表的 status 审视 -->
    <status_change pitfall_ref="§3.3 item-2" from="active" to="mitigated" reason="..."/>
    <still_active count="N">
      <ref>§3.3 item-1</ref>
    </still_active>
    <retired count="M">
      <ref>§3.4 item-5</ref>
    </retired>
  </pitfall_status_review>

  <observation_accumulation_review>
    <!-- §4.2 第 2 条 -->
    <promoted_to_should_update count="N">
      <signal>...</signal>
      <reason>累积 ≥ 3 次</reason>
    </promoted_to_should_update>
    <stale_observations count="M">
      <signal>...</signal>
    </stale_observations>
  </observation_accumulation_review>

  <empirical_value_review>
    <!-- §4.2 第 3、4 条 -->
    <must_update_count_trend>
      <avg_per_node>1.2</avg_per_node>
      <adjustment_suggested>none|raise|lower</adjustment_suggested>
    </must_update_count_trend>
    <parallel_wip_actual_peak>3</parallel_wip_actual_peak>
    <wip_adjustment_suggested>none|raise_to_4|lower_to_2</wip_adjustment_suggested>
  </empirical_value_review>

  <deferred_items>
    <item>...</item>
  </deferred_items>

  <final_verdict>
    <result>PASS|FAIL</result>
    <fail_reasons>
      <!-- 仅 FAIL 时 -->
      <reason>...</reason>
    </fail_reasons>
    <next_subphase_unblocked>true|false</next_subphase_unblocked>
  </final_verdict>
</verification_report>
```

**约束**：

- subagent **不修改 workflow.md 本身**（用户决定 + `docs(baseline):` commit）
- 不能跳过 hard_fail 任一项（§4.4 FAIL 处理）
- **不擅自删 §3 已知坑**（[09-known-pitfalls.md §3.10](09-known-pitfalls.md#310-已知坑维护协议只增不减) 只增不减；只能改 status 不能删条目）
- FAIL 时不阻塞 Claude 继续工作其他子阶段无关节点,但**该子阶段后续节点不得开工**直到修复
- subagent 输出 ≤ 200 行（详细数据进落盘文件,主对话只接 verdict + summary）

**下游消费**：

- 落盘 `docs/observations/{sN}-verification-report-<date>.md`（§4.3）
- 触发 §3 status 实际调整（commit `docs(baseline):` 落盘）
- 触发经验值微调（[07-retro-goal.md §2.10.4](07-retro-goal.md#2104-retro-质量门槛数量约束) / [11-cadence.md §5.2](11-cadence.md#52-并行节点-wip-limit) 的实际配置变化）
- FAIL 时：升级具体项为 deferred，进 [S2todo §9](../../roadmap/S2.md)

---

## Cross-references

**上游（我引用谁）**：

- [09-known-pitfalls.md](09-known-pitfalls.md) — §3 已知坑全表（status 审视输入）
- [07-retro-goal.md](07-retro-goal.md) — §2.10.4 数量门槛 / §2.10.6 observation 累积出口
- [11-cadence.md](11-cadence.md) — §5.2 并行节点 WIP limit（审视输入）
- [08-retro-node-and-pr.md](08-retro-node-and-pr.md) — 子阶段各节点 retro 文件（聚合输入）
- [docs/roadmap/S2.md](../../roadmap/S2.md) — §5.5 / §8.3 通过标准 / §9 Deferred 入账

**下游（谁引用我）**：

- [09-known-pitfalls.md](09-known-pitfalls.md) — 触发 §3 status 调整 / §3.10 维护协议
- [07-retro-goal.md](07-retro-goal.md) — observe 升级 should_update 重新分流
- `verification-report` SKILL — 消费 §4 全节
