# observations — observe 登记表

> retro 三档里的 **observe**（[core/06 §1.5](core/06-retro.md)）落这里：数据不足、先看着。同类（同 target + 同 signal）累积 ≥ `retro.observe_promote_at`（3）→ 升级 should_update，重新走分流表。里程碑交接必看一遍；不再相关的标 stale，不删行。

| # | target | signal | 首次 | 次数 | 每次一句 | 状态 |
|---|---|---|---|---|---|---|
| O-1 | `scripts/router.py` H 反查 | 声明「否」但 diff 有迹象的 ⚠ 来自非操作文本（tests/ 用例、docstring、字符串字面量） | 2026-09-30 PR #2 | 1 | ① 本仓 router.py 文档字符串与测试文本里的「DROP TABLE / push --force」 | 观察中 |
| O-2 | `tier.s_limits` / `paths.*` | 路由器对本仓给不出 S 档的频率（配置换成本仓取值后重新观察） | 2026-09-30 | 1 | ① 换配置前：`.github/` 一律 L、脚本名含 router 即 M | 观察中 |
