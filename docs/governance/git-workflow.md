# Git Workflow

> 本仓库的 git 实操规则。**优先级**：[CLAUDE.md](../../CLAUDE.md) > 本文件 > [./workflow.md](./workflow.md)。
>
> 覆盖：分支策略、commit 规则、push 与远程、PR 流程、UTF-8 约束、已知坑。
>
> 不覆盖：阶段任务推进的过程规则（见 [./workflow.md](./workflow.md)）、任务清单（见 [roadmap/S2.md](../roadmap/S2.md)）。

---

## 1. 分支策略

### 1.1 main 的角色

- 受保护分支，是真值源
- 不在 main 上直接 commit 代码改动
- 只接受两类输入：
  - 从节点工作分支 squash 合并的 PR
  - 满足 §1.3 例外的小步提交

### 1.2 节点工作分支

每个 [S2todo](../roadmap/S2.md) 节点开**独立工作分支**，互不干扰，可以并行存在多个：

- **命名**：`auto/<node-id>`，节点 ID 来自 S2todo（如 `auto/A6.1.2` / `auto/P4.B.4` / `auto/FM-3p.1`）
- **base**：从最新 main 切出（`git checkout -b auto/A6.1.2 main`）
- **生命周期**：节点合并到 main 后**立即删除**（本地 + 远程）
- **不复用**：一个节点 ID 对应一个分支；返工或重做也用同名分支重新切

**好处**：

- 异步堆 PR 时分支互不干扰，review 顺序任意
- 分支名自带节点 ID,从 GitHub PR 列表一眼能看出对应哪个节点
- 节点失败 / 撤销时直接删分支，main 干净

### 1.3 例外：何时直接在 main 上 commit

满足**全部**以下条件时，可以不开工作分支、直接在 main 上 commit：

- 改动类型 ∈ {observation 落账、ledger 更新、docs-only 维护、dated snapshot}
- 不涉及代码逻辑（不改 `.py` / `.ts` / `.sql` / `.yml` 业务文件）
- 不影响主链路（不改 schema / prompt / fallback / 路由 / archive replay）
- 单次 commit 改动 ≤ 1 个文件 或 ≤ 50 行（粗略边界，用于自检）

典型例子：

- `docs(observations): record OBS-FIX-7 verified done`
- `docs(todo): mark A6.1.1 ✅ DONE with commit hash`
- `chore(ledger): bump run-counter to 47`

**不满足例外 → 切节点工作分支**。两者都拿不准 → 停下问。

### 1.4 其他分支命名

| 用途 | 命名 | 何时建 / 何时删 |
|---|---|---|
| 节点工作分支 | `auto/<node-id>` | 节点起步建 / squash merge 后删 |
| 实验性探索 | `exp/<short-desc>` | 用完即删 |
| 大型架构改造（跨多节点）| `arch/<topic>` | 用完即删，需用户确认建立 |

**不要**：

- `feat/*` / `fix/*` 这种按 commit type 命名的分支（type 应该出现在 commit message 里）
- `main-auto-temp`（已废弃，迁移到 `auto/<node-id>`）

### 1.5 节点分支与 main 同步

节点工作分支在推进期间，可能 main 已被其他节点的 PR 合并更新。同步策略：

- **默认不主动 rebase**：节点工作进行中，main 上小步合并不影响当前节点
- **必须 rebase 的场景**：
  - 节点工作分支与 main 出现实际冲突
  - 节点依赖的上游节点刚被合并（如本节点依赖 A6.1.1，A6.1.1 刚合 main）
- **Rebase 方式**：`git fetch origin && git rebase origin/main`
- **冲突复杂时**：停下问，不要靠"应该没问题"硬来

---

## 2. Commit 规则

### 2.1 格式：Conventional Commits

```
type(scope): 中文一句话标题

中文详细说明（可选，多行）。
解释 why 和影响范围。

Plan: docs/<plan-file>.md#<anchor>
Co-authored-by: <协作者> <email>
```

**首行约束**：

- `type`：从 §2.2 固定列表选，不发明新 type
- `scope`：从 §2.3 常用列表选，或新增（中英文都可）
- `subject`：中文一句话，简短直接，**结尾不加句号**
- 总长度建议 ≤ 72 字符
- PR 号 `(#N)` 由 GitHub 自动追加，手写 commit 不带

**正文约束**：

- 中文为主，技术术语保留英文
- 解释 **why**（这个改动为什么必要）和 **影响范围**（动了哪些下游）
- 不复述 diff
- UTF-8 落盘（§5）

**Trailers**：

- `Plan: docs/<plan-file>.md#<anchor>` — 引用计划锚点（推荐，便于追溯）
- `Co-authored-by:` — 协作者署名（Cursor / Claude / 人类）

### 2.2 Type 固定列表

只用这 5 个 type，不发明新 type：

| type | 用途 | 例子 |
|---|---|---|
| `feat` | 新功能 / 新能力 | `feat(auth): 增加 SSO 登录流程` |
| `fix` | bug 修复 | `fix(prompt): 修复 bear_opening prior_debate 过滤遗漏` |
| `docs` | 文档变更 | `docs(roadmap): 整合 S4 阶段到主路线图` |
| `chore` | 杂活、构建、配置 | `chore(env): 升级 ruff 至 0.6.x` |
| `test` | 测试相关 | `test(eval): 增加 fundamentals corner case` |

**Workflow 改动的 type 归类**：

| Workflow 动作 | type(scope) |
|---|---|
| 节点级复盘文件落盘 | `docs(retro):` |
| Goal 级 retro 触发的已知坑回填 | `docs(baseline):` |
| 基准文档（S2-baseline / git-workflow）修改 | `docs(baseline):` |
| S2todo 状态更新（标 ✅ + commit hash） | `docs(todo):` |
| 计划文档调整（roadmap / TODO 大段改） | `docs(plans):` |

### 2.3 Scope 常用列表

**英文（高频）**：

`auth` / `schema` / `prompt` / `frontend` / `deploy` / `llm` / `cli` / `env` / `roadmap` / `todo` / `observations` / `eval` / `plans` / `ops` / `qa` / `healthcheck` / `retro` / `baseline`

**中文（实战出现过）**：

`基本面` / `前端`

**选择原则**：

- 优先英文 scope
- 中文 scope 仅当业务术语没有自然英文对应时使用
- 一个 commit 只用一个 scope；跨 scope 的改动 → 拆 commit

### 2.4 已弃用前缀

以下风格在 PR #50 之前出现过，**新提交不要再用**：

- `PR-X: ...` / `PR-K1: ...` / `PR-12e: ...` — 编号式 prefix
- `PR-L-sweep / ledger: ...` — 双段斜杠
- 任何不在 §2.2 的 type

### 2.5 OBS-FIX 不是 commit 前缀

`OBS-FIX-N` 是 observation gate 的**编号**，出现在 commit **正文里**，不是 subject 前缀：

```
fix(prompt): 修复 as_of DATA_INSUFFICIENT prompt-schema 冲突

OBS-FIX-10 触发：as_of 字段在 prompt 要求"必填"
但 schema 允许 null，导致 4 个 archive replay 失败。

Plan: docs/roadmap/S2.md#OBS-FIX-10
```

涉及 OBS-FIX 的 commit subject 仍然用 `fix(prompt):` / `fix(schema):` / `docs(observations):` 这种标准 type，不写 `OBS-FIX-10:` 当 subject prefix。

### 2.6 Commit 节奏

| 时机 | 节奏 |
|---|---|
| `/goal` 内 | 可多 commit，按 step 自然切分 |
| Goal 完成 | 不需要额外"goal 收口 commit"；最后一个 step commit 即收口 |
| 节点完成 | **不手动 commit 收口** — squash merge 时 main 自动产生 1 个 commit |
| 节点合并后 | 在 main 上 1 个 `docs(todo):` commit 标 ✅ DONE + 引用 squashed commit hash（这个 commit 走 §1.3 例外，不开新分支）|

---

## 3. Push 与远程同步

### 3.1 节点工作分支的 push

- `git push origin auto/<node-id>` — 任意时机，越早 push 越早能在 GitHub 看见 diff
- `git push --force-with-lease` — 仅在 rebase 后用，**不要**用 `--force`
- 不要 push 已存在的同名远程分支（先确认远程是上次合并后的残留则先删）

### 3.2 main 的 push

- 满足 §1.3 例外的 commit 可以直接 `git push origin main`
- 节点 PR 合并 = GitHub 上 squash merge，**不需要本地 push main**
- **绝不** `git push --force` 到 main

### 3.3 已知坑：push 不稳定

本地 `git push` 偶尔超时 / 失败：

- **应对**：重试 / 换 SSH / 等网络
- **禁止**：用 GitHub Git Database API 上传文件
  - 原因：API 上传**会丢非 ASCII 字符**
  - 历史教训：PR #39 翻车，commit message 和文档里的中文全变乱码
- 真的 push 不上去 → 停下问，不要绕道

### 3.4 远程分支清理

节点 PR 合并后清理：

```bash
# 删本地
git checkout main && git pull
git branch -d auto/<node-id>

# 删远程
git push origin --delete auto/<node-id>
```

如果用 `gh pr merge --delete-branch` 合并，远程会自动删，只剩本地。

### 3.5 🔒 保留分支清单（**删之前先看这里**）

以下分支**当年被明确决定要留**，不是忘了清。删掉它们**不是清理，是推翻已写下的决定**，
而且不可逆（远程 ref 删了本地 reflog 救不回来），还会让下方"出处"里的引用变断链。

| 分支 | 留它干什么 | 出处（一手记录） | 什么条件下才可以删 |
|---|---|---|---|
| `auto/A2` | 存 A2 代码 + decomposition 作参考（[#165](https://github.com/JunoChenZt/subagent-for-investment/pull/165) CLOSED·superseded·纯 additive 无可 salvage） | [backlog](backlog.md) 信源册 T5 行「**保留不删**」 | 用户明确判定 A2 那条路的参考价值已消失 |
| `auto/AO-pr2` | 已放弃的 web-verified 路（[#161](https://github.com/JunoChenZt/subagent-for-investment/pull/161) CLOSED 未合·`WEB_VERIFIED_ENABLED` 长期 OFF）的**唯一代码副本** | backlog `AO` 条目指着它 | 该问题域整体收口、且用户确认不再需要"当年为什么放弃"的一手材料 |
| `claude/pr-c-aborted-incident-2026-05-20` | PR-C worktree 事故的 audit trail | [§6.8](#68-🔴-active-worktree-base-check-反模式--假设-remote-状态未-fetch-pr-c-事故) + [PR-C retro](../retro/S2/PR-C-worktree-incident_2026-05-20.md) 明写「选项 A：**永久保留**」 | **不删**（当年选的就是永久保留） |

留着的成本≈0：三个 ref，不跑 CI、不进搜索、不碰主链路。

#### ⚠️ 判断"某分支还有没有活"——**只信内容比对，别信 commit 数**

squash 合并会让分支上**已经落地**的 commit 全部显示成"未合"，`git log main..branch` 因此完全不可信。

```bash
# ① 分支独有的文件（tip 级 tree 比对）
comm -23 <(git ls-tree -r --name-only <branch> | sort) \
         <(git ls-tree -r --name-only origin/main | sort)

# ② 分支独有的内容（两点 diff 的 + 行 = 分支有 main 无）
git diff origin/main <branch> | grep '^+' | grep -v '^+++'
```

**别用 `git diff main...branch`（三点）** —— 它会把 main 侧的删除也列成"分支侧新增"，误导过一次。

**两个实测坑（2026-08-10 清 `auto/GATE-MATRIX` 时各踩一次）**：

1. **"独有文件"里混着改名/搬家**，不等于内容丢了 —— 当时 3 条分支都"独有"两个 `docs/reference/` 文件，
   实为 [#218](https://github.com/JunoChenZt/subagent-for-investment/pull/218) 给它们补了 `.md` 扩展名；
   `prompts/role_prompts/*` 也只是搬去了 `prompts/analyst/role_prompts/*`。**逐个追溯改名/移动记录再下结论。**
2. **Git Bash 会把 `origin/main:<path>` 里的冒号当路径分隔符改写**（MSYS 路径转换），导致
   `git cat-file -e "origin/main:.github/workflows/ci.yml"` 假报"文件不在 main"。
   → 用 `export MSYS_NO_PATHCONV=1`，或改用 PowerShell。**假报会直接把"该不该删"判反。**

---

## 4. PR 流程

### 4.1 何时开 PR

- **节点级 PR**：每个节点工作分支推进完成（DoD 全过 + retro 已做）→ 1 个 PR
- **不开 PR 的场景**：满足 §1.3 例外的小步提交（直接 main commit + push）

### 4.2 PR base 与 head

| 项 | 值 |
|---|---|
| `base` | `main`（永远） |
| `head` | `auto/<node-id>`（节点工作分支） |
| **跨节点合并** | 不允许；每个节点独立 PR |
| **分支链 PR**（base: 另一节点分支）| 不允许；如果依赖未合并，等上游合完再开本节点 PR |

### 4.3 PR title

**PR title 自身必须是合规的 commit subject**（因为 squash merge 后会变成 main 上的 commit subject）：

```
type(scope): 中文一句话标题
```

例子：

- `feat(schema): A6.1.2 缓存命中率统计与 WAL 模式验证`
- `fix(prompt): F-vis.2 bear_opening prior_debate round 过滤修复`
- `docs(baseline): 新增 S2 工作基准 + git workflow 文档`

**不要**在 title 里加 `(#N)` — GitHub 合并时自动追加。

### 4.4 PR description 模板

PR description 按 [./workflow/08-retro-node-and-pr.md §6](./workflow/08-retro-node-and-pr.md#6-pr-描述模板决策溯源) 的模板填。核心字段：

- 节点 ID + 子阶段 + 依赖
- 拆解（小任务列表）
- DoD 通过证据（Code Review / Corner Case / 冒烟 / 跑通）
- Evidence 路径
- 风险与 Fallback
- 后续

PR description 在 squash merge 时**会被自动追加到合并后 commit 的 body 里**（取决于 GitHub squash 设置），所以写好 description 等于写好 main 上的最终 commit message。

### 4.5 PR review 模式

- **异步**：Claude 创建 PR 后**继续推下一个节点**，不停下等
- **可堆 PR**：多个节点 PR 可以同时 open，用户按任意顺序 review / 合并
- **用户回到线上时批量处理 PR**：approve / request changes / close

Claude 不主动催 review。

### 4.6 Claude 创建 PR 后的动作序列

```
节点 done
  → 步骤 9：节点级复盘（skill: retrospective-node）
  → 写复盘文件 docs/retro/<node-id>.md（main 上一个 docs(retro): commit，§1.3 例外）
  → push 节点工作分支
  → gh pr create --base main --head auto/<node-id> --title "..." --body-file <pr-description-path>
  → 输出 PR 链接
  → 继续推 S2todo 下一节点（不停）
```

### 4.7 PR 合并方式：Squash & merge

- **GitHub 设置**：仓库 settings → Pull Requests → 勾选 "Allow squash merging"，其他合并方式建议禁用
- **合并按钮**：选 "Squash and merge"
- **squash 后的 commit message**：
  - subject = PR title
  - body = PR description + 分支上各 commit message 拼接（GitHub 自动）
- **合并命令**（Claude 不主动执行；用户在 GitHub UI 上点合并）：

  ```bash
  # 用户的等价命令（参考）
  gh pr merge <N> --squash --delete-branch
  ```

### 4.8 合并后清理

- GitHub 自动删远程节点分支（若开启 `--delete-branch`）
- 本地清理：`git checkout main && git pull && git branch -D auto/<node-id>`
- 在 main 上补 1 个 `docs(todo): mark <node-id> ✅ DONE @ <squashed-commit-hash>` commit（§1.3 例外）

### 4.9 PR 失败 / 撤销

| 场景 | 动作 |
|---|---|
| User request changes | Claude 在节点工作分支上继续 commit / push；PR 自动更新 |
| User close PR | 删本地 + 远程分支；节点状态在 S2todo 标"撤销 + 原因" |
| Claude 自己发现 PR 不该合 | 用 `gh pr close` 关闭 + 在 PR 评论里说明 + 删分支 |

---

## 5. UTF-8 约束

### 5.1 必须 UTF-8 落盘的内容

- commit message（subject + body + trailer）
- 代码注释里的中文
- 文档（`.md` / `.txt` / `.rst`）
- PR title / description
- Issue title / body

### 5.2 验证

提交前检查：

```bash
# 检查最近一个 commit message 编码
git log -1 --pretty=%B | file -
# 期望：UTF-8 Unicode text
```

如果出现 `ISO-8859` / `unknown-8bit` / 乱码 → **回到 §3.3 已知坑**，可能用错了上传方式。

### 5.3 不允许的做法

- 用 GitHub Git Database API 上传中文文件（必丢字符）
- 在不支持 UTF-8 的 shell 里 echo 中文写 commit message
- 把中文文档保存成 GBK / GB2312 / Big5 编码

### 5.4 PR body 文件编码约束 (Windows 环境)

PR body 文件 (如 `scratch/<node-id>-pr-body.md`) **必须**用 UTF-8 + LF 行尾。

Windows PowerShell 默认 CRLF 行尾, 上传到 `gh pr edit --body-file` 后,
squash merge commit body 会包含 `\r` 字符, 污染 git log。

**正确写法**:

```powershell
# PowerShell 5+: 用 Out-File 显式指定 -Encoding utf8 + -NoNewline
$content | Out-File -FilePath scratch/<node-id>-pr-body.md -Encoding utf8 -NoNewline

# 或更显式:
[System.IO.File]::WriteAllText("scratch/<node-id>-pr-body.md", $content, [System.Text.UTF8Encoding]::new($false))
```

**验证**:

```bash
# merge 后核对 main 上 squash commit body 无 \r 字符
git log main -1 --format="%B" | xxd | grep "0d 0a"
```

输出非空 = 有 CRLF 污染, 需在下次 PR 时改用 LF。

---

## 6. 已知坑（git 专项）

### 6.1 本地 push 不稳定

- 症状：`git push` 偶发 timeout / connection reset
- 应对：重试 / 换 SSH / 等网络稳定
- 不要：用 API 绕道（§3.3）

### 6.2 GitHub Database API 丢字符

- 历史教训：PR #39 因 API 上传，中文 commit message + 文档全变乱码
- 永久禁用：本仓库**不用** Git Database API 上传任何包含中文的文件

### 6.3 节点工作分支与 main 同步

- 节点工作分支落后 main 时，按 §1.5 处理
- Rebase 后**只用** `--force-with-lease`，不用 `--force`

### 6.4 Force push 红线

`git push --force` / `git reset --hard` 到非节点工作分支的远程分支 = 强制红线（[CLAUDE.md](../../CLAUDE.md) 强制红线节）。

节点工作分支上 `--force-with-lease` 允许，但要在 PR 描述里说明 rebase 原因。

### 6.5 squash merge 与 commit hash 引用

- 节点工作分支上的 commit hash 在 squash merge 后**不存在于 main**
- 引用合并后的 commit 用 main 上的新 hash（PR 合并时 GitHub 会显示）
- S2todo ledger 里标"✅ DONE @ <hash>"用的是 main 上的 squashed hash，不是分支上的

### 6.6 节点分支同名复用

- 节点 A6.1.2 失败 / 撤销后，下次重做该节点仍用 `auto/A6.1.2`
- 重做前确保旧分支已删（本地 + 远程）
- 不要用 `auto/A6.1.2-v2` 这种衍生名

### 6.7 🟡 [active] self-referential commit hash 反模式

**症状**：commit A 内的文件引用 "commit A 的 hash"，但 hash 只在 commit 完成后才存在 → chicken-and-egg。

**根因**：Git 的 commit hash 是内容 hash，不能在内容里包含自己。

**实证**：skill-system-refactor G3 (commit b204acf) 时，backlog.md L 条目写 "G3 本次 commit"，
随后 80cb737 fixup 补 b204acf 到 completion details 段，但**漏改了状态行的同一 hash 引用**。
fixup 模式容易漏处。

**3 种修法（按推荐度）**：

1. **不引用自己的 hash**（推荐）：commit 内文件只描述"本次完成 X"，hash 由 git log 自查。
   - 代价：失去文档内点击式溯源
   - 收益：1 个 commit，无 chicken-and-egg

2. **延迟引用**：commit 时用占位符（如 `commit <pending>`），完成后 fixup 1 次
   - 代价：占位符美观度
   - 收益：比 #3 简洁

3. **fixup commit**（谨慎使用）：先 commit 不含 hash 的版本，后续 commit 补 hash
   - 代价：多 1 个 commit，容易漏改多处（本次就漏了）
   - 适用：hash 引用多处或必须用具体 hash 的场景
   - commit message 用 `docs(scope):` 避免 changelog 噪音

**G3 实证教训**：选 #3 时，**必须 grep 全文** confirm 所有 hash 引用都改全。
否则 fixup 解决了一处，漏了另一处，surface 第二次。

### 6.8 🔴 [active] worktree base-check 反模式 + 假设 remote 状态未 fetch (PR-C 事故)

**症状**：用 `git worktree add` 做 PR base 与变更态对比；或在未 `git fetch` 的情况下基于"我记得 main 是 X"假设做 cherry-pick / rebase / base-check。

**实证**：2026-05-19~20 PR-C (A6.1.4 Tushare 替代 akshare) 中：
1. Claude 创建 worktree 做 base-check 验证，跨目录操作破坏了主工作树
2. 未 `git fetch origin` 即假设 PR-A "未合入"，cherry-pick 孤儿 commit `2ad399b`（旧版本）
3. main 实际已有 `246c1d7`（PR #121 = PR-A + PR-B 官方版本）→ 旧 PR-A 代码混入 PR-C 分支 → scope 污染
4. 污染分支 `claude/pr-c-aborted-incident-2026-05-20` 推远程保留 audit trail
5. 重做版 PR #122 严格白名单 5 步流程才修复

详见 [docs/retro/S2/PR-C-worktree-incident_2026-05-20.md](../retro/S2/PR-C-worktree-incident_2026-05-20.md)。

**规则**：

| # | 规则 | 适用场景 |
|---|------|----------|
| **R1** | **禁用 `git worktree` 做 base-check** — 改用 `git stash push` / `git stash pop` 或 checkout-then-back | 任何需要对比 base 与变更态的场景 |
| **R2** | **任何假设 remote 状态的操作前，先 `git fetch origin`** — 包括 cherry-pick / rebase / base-check / "我以为 main 还是 X" | cherry-pick / rebase / base-check / 任何依赖 remote 当前状态的判断 |

**为什么不用 worktree**：worktree 在 Claude Code 的多目录上下文容易跨目录污染主工作树；stash 单一工作树语义清晰、可回滚；checkout-then-back 简单可控。

**为什么必须 fetch**：`git status` 显示的"远程 ahead/behind"信息只有在 fetch 后才是当前的；不 fetch 就基于上次本地认知判断 = 基于过时状态做不可逆操作。

**违反信号**（Claude 自检 / 用户挑战触发）：

- 提议 `git worktree add` → **立即拒绝，引用 R1**，改 stash / checkout-then-back
- 做 base comparison / cherry-pick / rebase 但未先 `git fetch` → **要求先 fetch，引用 R2**，再决定下一步
- 任何 "我以为 main 是 X" 的话语 → fetch 验证后再说

### 6.9 🔴 [active] `git add <目录>/` 在本仓是高危操作（DOC-SYNC 事故·2026-07-22）

**症状**：`git add docs/` 一次吞进 **248 个未跟踪文件 / 82 万行**（`_checkpoints/` 全量、
`docs/about-me.md`、实验目录、`FAILED-*` 转储等），本意只想提交 6 个改动文件。

**根因不是手滑，是本仓的结构性状态**：工作区**常年**存在大量未跟踪残留——
段式 e2e 的失败转储、重试中间产物、清洗版 checkpoint、个人笔记等（事故当时 11 个 `??` 顶级条目，
展开后 248 个文件）。这些残留**有意不提交也不删**（是排查素材，且 R6 明确"正品在 main、
本地是残留"），于是 `git add <目录>/` 的语义在本仓**永远**是"把残留一起吞了"，而非"提交我改的东西"。

**处置**：已 `git reset --soft` 回退 + 改用显式文件列表重提（最终 6 files changed 正确）。
**未污染任何已推送分支**——但这纯属发现得早。

**规则**：

| # | 规则 |
|---|------|
| **R1** | **docs / observation 类提交一律用显式文件列表** — `git add docs/a.md docs/b.md`，不用目录、不用 `-A`、不用 `.` |
| **R2** | **`git add` 之后、`git commit` 之前，必看一眼 `git status --short`** — 只应出现你点名的那几个 `M`/`A`；出现意料外的条目 = 立即 `reset` |

**为什么不靠 `.gitignore` 治**：这些残留**不该被永久忽略**（部分将来要正式归档），
忽略掉反而会让"该提交的证据"静默消失——比误提交更难发现。约束加在 `add` 动作上、不加在文件上。

**违反信号**：任何 `git add` 后面跟的是目录 / `.` / `-A` → 停下改显式列表。

详见 [docs/retro/S2/DOC-SYNC_2026-07-22.md](../retro/S2/DOC-SYNC_2026-07-22.md)。

---

## 7. 快速参考

### 7.1 标准节点推进的 git 命令序列

```bash
# 起步
git checkout main && git pull
git checkout -b auto/A6.1.2

# 推进期间（可重复）
# ... 改代码 ...
git add <files>
git commit -m "feat(schema): A6.1.2 缓存命中率统计实现

详细说明...

Plan: docs/roadmap/S2.md#A6.1.2"
git push -u origin auto/A6.1.2

# 节点 done（DoD + retro 全过）后
gh pr create \
  --base main \
  --head auto/A6.1.2 \
  --title "feat(schema): A6.1.2 缓存命中率统计与 WAL 模式验证" \
  --body-file <pr-description-path>

# 输出 PR 链接 → 继续下一节点
```

### 7.2 标准小步提交（§1.3 例外）的 git 命令序列

```bash
git checkout main && git pull
# ... 改文档 / 落账 ...
git add <files>
git commit -m "docs(observations): record OBS-FIX-7 verified done

Plan: docs/roadmap/S2.md#OBS-FIX-7"
git push origin main
```

### 7.3 PR 合并后清理（用户合完 PR 后 Claude 做）

```bash
git checkout main && git pull
git branch -D auto/A6.1.2

# 远程通常 GitHub 自动删；如未删：
git push origin --delete auto/A6.1.2

# 在 main 上标 S2todo
# ... 改 docs/roadmap/S2.md，A6.1.2 行加 ✅ DONE + 合并 commit hash ...
git add docs/roadmap/S2.md
git commit -m "docs(todo): mark A6.1.2 ✅ DONE @ <hash>

Plan: docs/roadmap/S2.md#A6.1.2"
git push origin main
```

---

## 8. 与其他文档的关系

| 文档 | 关系 |
|---|---|
| [CLAUDE.md](../../CLAUDE.md) | 顶层；本文件是其 "Git 提交约定" 节的展开 |
| [docs/governance/workflow.md](./workflow.md) | 过程层导航；详细 PR 模板见 [./workflow/08-retro-node-and-pr.md §6](./workflow/08-retro-node-and-pr.md#6-pr-描述模板决策溯源)，被本文件 §4.4 引用 |
| [docs/roadmap/S2.md](../roadmap/S2.md) | 任务层；节点 ID 来源；S2todo 状态由本文件 §4.8 维护 |
| [docs/roadmap/roadmap-v3.4.md](../roadmap/roadmap-v3.4.md) | 架构层；不直接关联，但 commit 引用其节点 ID |

---

## 9. 维护协议

- 本文件随实践迭代；新发现的 git 坑回填 §6
- 修改本文件用 `docs(baseline):` type
- 重大调整（如改分支策略 / 改合并方式）需在 commit message 显式 `baseline:` scope 并停下问用户