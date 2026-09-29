# AG.1 验尺子 —— 缓存计量在真阳性面前会不会响

> 日期：2026-08-11 ｜ 分支：`auto/AG` ｜ 探针：[scripts/probe_prompt_cache.py](../../../scripts/probe_prompt_cache.py)
> 拆解出处：[AG-prompt-caching-decomposition.md](../../plans/AG-prompt-caching-decomposition.md) AG.1

---

## 结论先行

**尺子的读取侧三家都准，写入侧 Anthropic 那半是坏的 —— 已修。**

坏法很典型：Anthropic 明明返回了「这次写入缓存 5,520 token」，但中间那层库把这个数**拆到了别的字段**，我们只认原来那个名字 → 缓存写入量**永远记 0**。后果两层：① 账少算（写入按基础价 ×1.25 计费，记 0 等于这笔没算，实测**单次低估 20%**）；② 拆解里原定的判据「见到写入量大于 0 就算标记生效」**永远不会响** —— 正是坑表 §3.2 形态⑥：判据写得对、前提也成立，坏的是执行检查那段代码它自己。

**顺带把 AG.2 的可行性也证实了**：给最贵那家打上标记后，第二次调用命中 5,502 / 5,525 token（99.6%），单次成本从 $0.0835 降到 $0.0093（**降 89%**）。不打标记则两次都是 0。

**Gemini 是坏消息**：两种形态都试了，一次都没命中；且返回里**没有任何未被解析的缓存字段**，所以是真没命中，不是我们读丢了。

---

## 1. 官方参数（2026-08-11 逐条核对，不凭记忆）

| provider | 缓存是否自动 | 最小可缓存长度 | 命中报在哪 |
|---|---|---|---|
| Anthropic `claude-opus-4-7` | **否**，须打标记 | **2,048 token** | `cache_read_input_tokens` / `cache_creation_input_tokens` |
| Google `gemini-2.5-pro` | 是（implicit 默认开） | 2,048 token | `total_cached_tokens` |
| DeepSeek | 是（自动前缀缓存） | 未公布 | `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens` |

Anthropic 补充：前缀按 `工具定义 → 开头指令 → 对话消息` 顺序匹配；单请求最多 4 个断点；5 分钟有效期的写入价 = 基础输入价 ×1.25、读取价 = ×0.1。低于最小长度时标记被**静默忽略、不报错** —— 所以「没报错」不等于「缓存生效」。

> 〔2026-08-12 补〕本行只记了 5 分钟档。写入价**按有效期分两档**，1 小时档 = ×2 —— 见 [§9.1](#91-写入价按有效期分两档1-小时档是-2)。另：「2,048 token」这个门槛按**词元**算，与字符数的换算比实测见 [§9.2](#92-字符与词元的换算比长度粗筛用)。

来源：[Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) / [Gemini context caching](https://ai.google.dev/gemini-api/docs/caching) / [DeepSeek KV cache](https://api-docs.deepseek.com/guides/kv_cache)

---

## 2. 探针实测（首跑，修尺子之前）

样本刻意用**生产里真实的长 prompt**：决策定稿指令 7,236 字符、技术面角色指令 12,145 字符。两次调用的用户消息**刻意不同**，这样若第二次命中，证明命中的是开头那段本身，而不是「整个请求一模一样」这种平凡情况。

| # | 场景 | 第 1 次 | 第 2 次 | 判定 |
|---|---|---|---|---|
| ① | DeepSeek 同一开头连发两次 | in 5,173 / 命中 0 | in 5,175 / **命中 5,120** | ✅ 尺子会响 |
| ② | DeepSeek 换不同开头 | 命中 0 | 命中 0 | ✅ 尺子不假响 |
| ③ | Anthropic **不打标记** | in 5,524 / 命中 0 / $0.0835 | in 5,525 / 命中 0 / $0.0835 | ✅ 证实不打标记就没缓存 |
| ④ | Anthropic **打标记** | in 5,524 / 命中 0 / $0.0835 | in 5,525 / **命中 5,502** / **$0.0093** | ✅ 标记真的有效 |
| ⑤ | Gemini 同一开头连发两次 | 命中 0 | 命中 0 | ❌ 没命中 |
| ⑥ | Gemini 同正文前缀、不同开头（复刻辩论形态） | 命中 0 | 命中 0 | ❌ 没命中 |

> ④ 的第 1 次显示「写入 0」是**尺子的毛病**，不是没写入 —— 见下节。

---

## 3. 查出的缺陷：缓存写入量永远记 0

同一次响应，两处读数打架：

```
原始返回 response_metadata.usage:
    cache_creation_input_tokens = 5520     ← API 明说写了 5520
    cache_read_input_tokens     = 0

库归一后 usage_metadata.input_token_details:
    cache_read                  = 0
    cache_creation              = 0        ← 恒填 0
    ephemeral_5m_input_tokens   = 5520     ← 真值被拆到了这里
    ephemeral_1h_input_tokens   = 0
```

本仓的计量表只读 `cache_creation` → 拿到 0。库版本 `langchain-anthropic==1.5.0`。

**为什么这条特别难发现**：不报错、测试不红、账单表照常打印、每个数字看着都合理。**只有拿一个必然写入缓存的阳性样本去打它，才会露馅。**

### 修法

把两处解析（[token_usage.py](../../../src/committee/token_usage.py) 与 [trace.py](../../../src/committee/trace.py)）收成**一个函数**，写入量为 0/空时回退去认 `ephemeral_5m` + `ephemeral_1h` 之和。收成一处是因为原先两边各写一份 —— 正是坑表里「改一处留半截」的形状。

读取侧三家都填得对，不需要回退。将来若库修好了直接填 `cache_creation`，回退不会覆盖它（已有靶测锁住）。

### 修复前后（同一次全新的带标记调用，端到端走生产计量路径）

| | 缓存写入量 | 该次记账成本 |
|---|---|---|
| 修复前 | 0 | $0.0835 |
| 修复后 | **5,520** | **$0.1042** |

即：这类调用此前**每次少算 20% 的钱**。

### 守护

[tests/test_token_usage_cache_fields.py](../../../tests/test_token_usage_cache_fields.py) —— 13 条断言，payload **全部取自本次探针的真实返回**，不是构造的。

**反向变异已做**（按坑表 §3.2 防御 (a')：跑一次是绿的不构成证据，坏掉的检查也是绿的）：把回退逻辑摘掉后，5 条断言变红；装回去后全绿。

---

## 4. Gemini：真没命中，不是读丢了

原始返回里 `input_token_details` **只有 `cache_read` 一个键**，没有任何未被解析的缓存字段（对比 Anthropic 那边多出的两个 `ephemeral_*`）。所以这是「implicit 缓存在我们的调用形态下没命中」，不是「命中了但我们没读到」。

两种形态都试过：同一开头连发两次（⑤）、同正文前缀但每轮换开头（⑥，复刻辩论环节的真实形态）。都是 0。

**未验的可能原因**（不下结论）：implicit 缓存的命中窗口、后端负载、是否要求更长前缀、代理路径是否影响。要弄清得另立专项（对应拆解 §4 拍板项 5）。

---

## 5. 对后续的影响

| 项 | 结论 |
|---|---|
| AG.2 贴标记 | **可以做，且有据** —— 标记有效性已实证（命中率 99.6%、成本降 89%） |
| AG.3 原判据「见到写入量 > 0 = 标记生效」 | **若不修尺子则永不会响**。现已修，判据可用 |
| Gemini | 本轮**只观测不改码**的决定得到支持 —— 没有「标记」可打，且 implicit 实测不命中 |
| 历史归档里的成本数字 | **偏低**。所有含 Anthropic 调用的历史记账都少算了缓存写入那部分；但此前从未打过标记，写入量本就为 0，**故历史数字实际未受影响**，仅从现在起（AG.2 打标记后）该修才承重 |

---

## 6. 局限

- 每个场景只跑一对，未定噪声地板 —— 但本次判据是**定性的**（命中 / 不命中），不是比较量级差异，单对足够
- 只测了 `claude-opus-4-7` / `gemini-2.5-pro` / `deepseek-v4-flash` 三个具体型号，未外推
- Gemini 的「没命中」是**当前调用形态下**的结论，不等于 implicit 缓存对本仓永远无用
- 首跑的原始读数**未存成 JSON**（脚本在 Windows 控制台打 emoji 撞编码崩在最后一步，数据本身完好、见上表；脚本已改成纯 ASCII 标记并自动建目录，后续跑会正常归档）

---

## 7. Goal 级复盘（retro_goal AG.1）

```xml
<retro_goal id="AG.1" timestamp="2026-08-11">
  <triggered_by>
    <condition n="2">刹车 8 问 Q7 命中 —— 探针真调用产生费用（约 $0.5）</condition>
    <condition n="4">新增 deferred item —— DoD 冒烟一步延后至 AG.2（已登记 S2 §9.2）</condition>
    <condition n="6">属高风险节点 —— 拆解判定 AG 阶段一整体高风险</condition>
  </triggered_by>

  <tldr>
    AG.1 原定是「验个尺子走过场」，实际查出计量表写入侧恒 0 的真缺陷（第三方归一层把真值
    搬到了别的字段名下），并顺带实证了 AG.2 可行（命中 99.6%、成本降 89%）与 Gemini 不可行。
    最重要的一条：这条缺陷只有拿「必然阳性」的真调用样本去打才会露馅 ——
    它不报错、测试不红、账单表照常打印、每个数字看着都合理。
  </tldr>

  <journey>
    <phase name="核官方参数">
      不凭记忆查三家文档。查出 opus-4-7 最小可缓存 2,048 token，且低于门槛时标记被
      **静默忽略、不报错** —— 直接推翻了「没报错 = 生效了」这个默认假设，
      也决定了后面必须看返回数字而不是看有没有异常。
    </phase>
    <phase name="六场景探针 + 对照组设计">
      关键不是「跑一次看看命中多少」，而是③④这组对照：同一份文本、唯一变量是打不打标记。
      两次调用还刻意换了提问，排除「整个请求一模一样」这种平凡命中。
      没有对照组的话，④的命中会被归因成「缓存本来就会命中」而不是「标记起了作用」。
    </phase>
    <phase name="读数打架 → 追到原始返回">
      ④第 2 次读到 5,502，第 1 次却报「写入 0」——没写进去哪来的读出来？
      把 provider 原始返回整个打出来，才看到真值 5,520 被拆进了 ephemeral_5m。
      **这一步是整个 goal 的价值所在**：如果止步于「读取侧验通了，PASS」，缺陷会原样留着。
    </phase>
    <phase name="修 + 反向变异 + 端到端确认">
      两处解析收成一个函数；13 条靶测用真实返回形状；摘掉修复后 5 条变红、装回全绿；
      再发一次全新真调用确认端到端记对（$0.0835 → $0.1042）。
    </phase>
  </journey>

  <mistakes>
    <mistake>
      <what_went_wrong>
        向用户口头下过两个未核实的判断：说决策环节「跨段反复重发十几次」（实际贵模型全程仅 3 次
        调用），以及把共用段长度说成 6.2k 字符（那是 UTF-8 文件字节数，实际 4,260 字符）。
        其中第一条已经被写进坑表并推上 main 才被自己核出来。
      </what_went_wrong>
      <fix_or_lesson>
        承重数字必须现场实测再说出口，尤其是**要写进真值源文档**的。
        「量级差不多」不是可以省掉核实的理由 —— 这次两条错的量级都不离谱，但一条把
        优化方向指错了（以为决策环节反复重发 = 大肥肉，实际根本没这回事）。
      </fix_or_lesson>
    </mistake>
    <mistake>
      <what_went_wrong>
        探针脚本在 Windows 控制台打 emoji 撞 GBK 编码崩在最后一步，把首跑的 JSON 归档冲没了
        （数据靠 console 输出才留住）。写文件的动作排在了打印之后。
      </what_went_wrong>
      <fix_or_lesson>
        面向本机控制台的脚本一律用纯 ASCII 标记；**先落盘再打印**，别让展示层的失败毁掉数据。
        已改（含自动建目录）。
      </fix_or_lesson>
    </mistake>
  </mistakes>

  <techniques>
    <technique>
      <pattern>
        验「某个开关有没有效」时做对照组：同一份输入跑两遍，唯一变量是开关本身。
      </pattern>
      <when_to_apply>
        任何「加了 X 之后指标变好了」的结论。没有对照组时，指标变好可以被归因到任何东西。
      </when_to_apply>
    </technique>
    <technique>
      <pattern>
        两次调用刻意换掉可变部分（这里是提问），让命中只可能来自被测的那段前缀。
      </pattern>
      <when_to_apply>
        验证缓存 / 复用 / 去重类机制时，防止「整体完全相同」这种平凡解冒充真结论。
      </when_to_apply>
    </technique>
    <technique>
      <pattern>
        两个读数互相矛盾时（能读出、却说没写入），去看**未经加工的原始返回**，
        别在归一后的视图里绕。中间归一层是信息丢失的高发地带。
      </pattern>
      <when_to_apply>
        任何依赖第三方 SDK / 库归一后字段的排查。
      </when_to_apply>
    </technique>
  </techniques>

  <proposals>
    <must_update target="09-known-pitfalls.md §3.2 形态⑥">
      <rule>
        判据若依赖**第三方库归一后**的字段，落地时必须：①拿一次**真调用的阳性样本**证明它会响
        （构造 payload 不算 —— 构造时用的正是你以为的那个字段名）；②把那次真实返回的
        **原始形状**固化进测试 fixture，让日后升级库时的字段漂移会被抓到。
      </rule>
      <rationale>
        形态⑥原有三个实测都坏在**我们自己写的**检查代码里；本例我们的逻辑无误，
        坏在**两者之间的第三方归一层**——版本一升就可能悄悄换字段名，
        而没有任何测试会因此变红（单测喂的是自造 payload，永远是旧字段名）。
        这是同族的新子形态，值得单列。**已落盘。**
      </rationale>
    </must_update>

    <observe>
      <signal>
        面向本机控制台的辅助脚本用非 ASCII 装饰字符，在 Windows GBK 控制台会整份崩掉。N=1。
      </signal>
      <why_insufficient>
        单次事故，且已在本脚本内修掉。若再出现 2 次同类（脚本因展示层编码毁掉数据），
        升级为 should_update，考虑写进脚本编写约定。
      </why_insufficient>
    </observe>
  </proposals>

  <quality_self_check>
    <must_update_count>1</must_update_count>
    <is_trivial>false</is_trivial>
    <retro_should_have_been_skipped>false</retro_should_have_been_skipped>
  </quality_self_check>
</retro_goal>
```

---

## 8. 产物

| 文件 | 内容 |
|---|---|
| [scripts/probe_prompt_cache.py](../../../scripts/probe_prompt_cache.py) | 探针（六个场景 + `--raw` 原始字段转储 + `--dry-run`） |
| [tests/test_token_usage_cache_fields.py](../../../tests/test_token_usage_cache_fields.py) | 靶测，真实返回形状 |
| [src/committee/token_usage.py](../../../src/committee/token_usage.py) | `extract_cache_tokens` 单一真值源 + 回退 |
| [src/committee/trace.py](../../../src/committee/trace.py) | 改为共用同一解析 |

---

## 9. 冷审补测（2026-08-12·PR [#236](https://github.com/JunoChenZt/subagent-for-investment/pull/236) review 追加）

> 本节是**后补**，上面 1–8 节是 08-11 当时的记录，正文不动。
> 补的两个数都用**免费的** `count_tokens` 接口与官方文档核，未产生调用费用。

### 9.1 写入价按有效期分两档，1 小时档是 ×2

§1 只记了 5 分钟档的倍率（×1.25）。官方文档（2026-08-12 复核）三个倍率齐全：

| 档位 | 相对基础输入价 |
|---|---|
| 5 分钟有效期写入 | ×1.25 |
| **1 小时有效期写入** | **×2** |
| 读取（命中 / 续期） | ×0.1 |

**两档差 60%。** 原实现把两档的写入量加成一个数、整笔按 5 分钟档计价 —— 生产当前恒走 5 分钟档所以踩不到，但探针脚本的 `_as_cached_blocks` 已支持传有效期参数，路是通的。**少算的方向与 §3 那个「写入量恒记 0」完全一致，属同一种坏法的另一半**，故提前堵上而非留注释等人记得。

修法：费率表按档分开填，解析函数把 1 小时档单独拆出来供计价，对外报的写入量仍是合计（归档结构零变化）。反向变异双验：长档按短档计价 → 3 条测试变红；解析不再拆档 → 5 条变红。

### 9.2 字符与词元的换算比（长度粗筛用）

最小可缓存长度门槛按**词元**算，而 `PROMPT_CACHE_MIN_CHARS` 数的是**字符**。原注释按「1 词元 ≈ 1 字符」估，实测差一个数量级：

| 内容形态 | 词元/字符 | 2,048 词元约合 |
|---|---|---|
| **本仓真实 prompt**（中英混排 + markdown） | 0.65–0.76 | ~2,700–3,150 字符 |
| 纯中文散文 | ~1.07 | ~1,914 字符 |
| 生僻字 | ~2.65 | ~773 字符 |
| 纯英文 | ~0.35 | ~5,850 字符 |

> 测法：`anthropic.Anthropic().messages.count_tokens(model="claude-opus-4-7", system=<文本>, ...)`，本仓三份真实 prompt + 四组构造样本。

**对本仓的意义**：这道粗筛**放得偏松而非偏紧** —— 2,048~2,700 字符那段会被放行、然后被 API 静默忽略标记（行为与不打标记完全相同，无害）。偏紧那个方向（纯中文约 1,914 字符就够门槛却被拦）本仓当前不会发生。

**门槛值保持 2,048 不动**：唯一够格的那份开头指令（fund_mgr 定稿用）是 **7,236 字符 / 5,513 词元**，离门槛很远，换算比再浮动也翻不到界外。要让「绝不误拦」在最坏情况（生僻字 2.65）下也成立，得压到约 770 字符 —— 那样这道粗筛就基本不筛了，不划算。

### 9.3 顺带核实的三份真实 prompt 长度

| prompt | 字符 | 词元 | 够 2,048 门槛？ |
|---|---|---|---|
| 决策定稿指令（`DECISION_PROMPT`） | 7,236 | 5,513 | ✅ |
| 决策提纲指令（`DECISION_OUTLINE_PROMPT`） | 678 | 516 | ❌ |
| 技术面角色指令 | 12,145 | 7,904 | ✅（但走 analyst 一路，非 Anthropic） |

这组数**印证了 AG.2 默认关的算账前提**：贵模型三次调用里只有定稿那次过得了门槛，而它一次跑批只发生一遍 —— 只写不读，单跑一次净亏。
