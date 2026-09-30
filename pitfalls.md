# pitfalls — 本仓库已知坑表

> 格式与维护协议见 [core/08](core/08-pitfall-registry.md)：强度 🔴 / 🟡 / 🟢 × status active / mitigated / stale_candidate / retired；只增不减；每条带出处、**「路径:」**（路由器按它匹配改动清单，🔴 active 命中即至少 M）、「动作:」（路由器塞进停止条件）、守护。
> 条目的理想终点是被一条测试替代，然后标 mitigated。加流程之前先问能不能焊进测试。
> 对任何项目都成立的元规则在 [core/08 §3](core/08-pitfall-registry.md)，这里只放本仓真踩过的。

## 1. 脚本与 CI

- 🔴 [active] 管道会吞退出码：`pytest | tail` 后接 `&&`，判的是 tail 的退出码，红着也往下走（2026-09-30 · PR #2 复盘：红着提交了一笔）
  路径: ^\.github/, ^scripts/, ^CLAUDE\.md$
  动作: 命令链里不用管道判成败；要看尾巴就先落文件再判，或用 PIPESTATUS
  暴露方式：提交后 CI 复跑才看见；守护：无守护，靠本条（CI 里的 pytest 步没有管道）
- 🟡 [mitigated] Windows 下 subprocess 按 locale（GBK）解码，读含中文的 git 输出直接崩（2026-09-30 · PR #2：路由器 DoD 运行点第一次真跑就崩）
  路径: ^scripts/.*\.py$
  动作: subprocess 一律 `encoding="utf-8", errors="replace"`；stdout 开头 `reconfigure`
  暴露方式：真 diff 含中文才触发，ASCII 测试看不见；守护：`tests/test_router.py::test_main_base_mode_uses_real_git_diff` 用中文内容
- 🟡 [mitigated] 文档里写「DROP TABLE」「push --force」是在讲规则，H 反查把它当成操作打假警告（2026-09-30 · PR #2）
  路径: ^scripts/router\.py$
  动作: 改反查范围前先问「哪种文案会误触」；.md / .txt / .rst 已跳过，tests/ 与字符串字面量未跳过（观察点 O-1）
  守护：`tests/test_router.py` 的 .md 豁免用例
- 🔴 [active] 工具的 heredoc 会折叠反斜杠、超长会截断：`\\.` 写成 `\.`、整段脚本执行到一半（2026-09-29 两次）
  路径: ^scripts/, ^tests/
  动作: 生成含反斜杠的源码或正则用文件写入工具，不用 heredoc；写完扫 0x08 字节；长脚本先落文件再跑
  守护：无守护，靠本条
- 🟡 [active] `git add -A` 把 `__pycache__` 带进仓（2026-09-29：15 个 .pyc 提交后才发现）
  路径: ^tests/, ^scripts/
  动作: add 前看一眼 status；`.gitignore` 已有，新目录记得补
  守护：`.gitignore`
- 🟡 [mitigated] 链接检查在 Windows 下 glob 返回反斜杠路径，相对链接全部误判成断链（2026-09-29：首跑报 19 条，实为 0）
  路径: ^scripts/lint_links\.py$
  动作: 路径一律先 `as_posix()` 再拼相对链接
  守护：`scripts/lint_links.py` 用 `relative_to().as_posix()`；`tests/test_lint_links.py`
- 🟢 [mitigated] GBK 控制台打不出 ✓ 等字符，脚本在最后一行 print 崩、看起来像自测失败（2026-09-29）
  路径: ^scripts/
  动作: 脚本入口 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
  守护：五个脚本入口已加

## 2. 路由与分档

- 🟡 [mitigated] 默认值的方向要和规则一致：H 漏答 / 拼错曾静默按「否」算（放行方向），而规则是「拿不准往高一档」（2026-09-30 review）
  路径: ^scripts/router\.py$
  动作: 任何「默认」「兜底」「解析不出」的分支，先问它落在放行还是拦截那一侧；拦截侧才是默认
  守护：`tests/test_router.py` 的缺声明 → L、非法值 → 报错两个用例

- 🟡 [active] M 档路径表按子串匹配会误伤：文件名含 quality / gate / router 的文档也判 M（2026-09-30 探针）
  路径: ^project-config\.md$, ^scripts/router\.py$
  动作: 改路径表时用锚定的正则（`^core/` 而不是 `core`）；本仓 §10 已按目录锚定
  守护：无守护，靠本条；待办 B2
- 🟡 [active] 路由器 DoD 运行点比的是 `base...HEAD`，工作树未提交的改动看不见（2026-09-30 探针）
  路径: ^scripts/router\.py$
  动作: DoD 前先 commit 再跑，或等待办 B1 的 `--worktree`
  守护：无守护，靠本条；待办 B1
