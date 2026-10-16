# Intent 完善路线图 — 对标 Python 生态的系统性升级方案

> 心学为体，禅道为翼，马哲为用
> 定位：**意图清晰的通用编程语言**。BIM 是特色战场，不是天花板。
> 本文档是所有语言改进的唯一裁决依据。任何新特性提案，先过「设计宪法」，再进路线图。

---

## 一、设计宪法（不可违背的六条）

从《用代码学哲学》8 章提炼。每条宪法是过滤一切特性提案的筛子——通不过的，不做。

| # | 宪法 | 来源 | 含义 |
|---|------|------|------|
| 1 | **声明即存在** | 心即理（第1章） | `let` 默认不可变；可变必须显式 `mut`。不许倒退成 Python 式默认可变 |
| 2 | **代码即意图** | 心即理 | 语法必须让意图裸露。禁止为性能/便利引入隐藏行为（隐式转换、隐式类型提升） |
| 3 | **一切皆表达式** | 第1章 | if/match/try/for 都是表达式。新控制流不允许出现"不产生值的语句" |
| 4 | **错误是另一种正常** | 烦恼即菩提（第5章） | `Result<T,E>` + `?` 是一等错误通道。异常机制只用于真正的契约违反 |
| 5 | **知行合一** | 第2章 | `|>` 管道是认知结构不是语法糖。数据处理 API 必须可管道化 |
| 6 | **可验证的良知** | 实事求是（第4章） | `requires/ensures` 是语言级契约，运行时强制验证。这是 Intent 区别于一切语言的身份证，任何重构不许削弱它 |

**宪法执行方式**：每个特性提案必须附带「哲学映射」一节，说明它强化了哪条宪法、削弱了哪条。只强化不削弱的才进 Phase 1+。

---

## 二、现状盘点：Intent v1.2.0 vs Python 3.12

### 2.1 能力矩阵

| 板块 | Python | Intent 现状 | 差距判定 |
|------|--------|-------------|---------|
| 词法/语法/解释器 | 全链路 | 全链路（Lexer→Parser→Resolver→树遍历，9435 行） | ✅ 对等 |
| 基础语法 | let/def/class/if/for/while/with | let/let mut/def/class/if/match/for/while/defer | ✅ 对等（无 with，defer 部分覆盖） |
| 不可变默认 | 无（默认可变） | `let` 默认不可变 | ⬆️ 超越 |
| 模式匹配 | match（3.10+） | match（范围/解构/guard/穷举检查） | ✅ 对等 |
| 管道 | 无（函数嵌套） | `|>` 管道 | ⬆️ 超越 |
| 契约 | 无（icontract 等第三方） | requires/ensures 运行时验证 | ⬆️ 核心特色 |
| 错误处理 | Exception + raise | Result<T,E> + ? + try/catch/finally | ✅ 对等（堆栈追踪缺失） |
| 闭包/生成器 | 完整 | 闭包 ✅ / yield ✅ | 🔶 缺 yield from / send |
| 面向对象 | 完整（协议/描述符/metaclass） | class/继承/覆盖/enum/运算符重载 | 🔶 缺接口协议、属性描述符 |
| 类型系统 | 动态 + 渐进类型（mypy） | 纯运行时动态类型；函数级泛型参数替换 | 🔶 无静态检查、无类型别名/Union |
| 并发 | threading/asyncio/multiprocessing | **零** | ❌ 完全缺失 |
| 标准库 | 200+ 模块 | 19 模块（通用 10 + BIM 8），70+ 内置函数 | ❌ 缺网络/数据/正则/算法库 |
| 包管理 | pip + PyPI + venv | 无。import 仅相对路径/std 目录 | ❌ 完全缺失 |
| 测试框架 | unittest/pytest | 无（靠 examples/ 手动跑） | ❌ 完全缺失 |
| Formatter | black | 无 | ❌ |
| Linter | ruff/flake8 | 无 | ❌ |
| LSP/IDE | 完整生态 | 无 | ❌ |
| 文档生成 | Sphinx | 无（docstring 未定义语法） | ❌ |
| 语言规范 | PEP + 参考手册 | 无正式 spec（散见于 8 章书稿） | ❌ |
| 调用栈追踪 | traceback | 只有 Python 层 traceback，无 Intent 级栈 | ❌ |

### 2.2 已有资产（升级的基石，不许推倒重来）

1. **解释器全链路**：Lexer/Parser/Resolver/Interpreter 四件套，作用域解析正确（闭包安全），模块系统带循环依赖检测
2. **契约引擎双形态**：语言内 `requires/ensures` + 语言无关的 `contract_skill/intent_contract.py`（可嵌入 LLM 编程助手）
3. **哲学资产**：8 章书稿 + philosophy/mapping.json + philosophy_mapper.md——这是竞品抄不走的护城河
4. **BIM 标准库**：8 模块 ~1700 行，管道 A* 路由可直接移植 C#
5. **泛型参数替换机制**：`identity<T>(x: T) -> T` 已能工作，是类型系统的种子

---

## 三、路线图总览：四个 Phase

```
Phase 0 地基加固 ──── 错误堆栈 / CLI / 语言规范 / 测试框架       （一切的前提）
Phase 1 语言内核 ──── 语法补全 / 类型系统 / 错误处理深化          （编程体验）
Phase 2 生态基建 ──── 包管理 / formatter / linter / 文档生成      （可用性）
Phase 3 标准库+并发 ─ 高频库扩张 / 并发模型 / LSP                （通用性）
```

**排序逻辑**：先让语言「可调试、可测试、可描述」（P0），再补「写得舒服」（P1），再建「生态循环」（P2），最后扩「能力边界」（P3）。Python 的胜利不是语法胜利，是生态胜利——但 Intent 现在连 spec 都没有，谈生态是空中楼阁。

---

## 四、Phase 0：地基加固

> 目标：让 Intent 从「能跑的 Demo」变成「可维护的语言」。

> **实施进度**：P0.1 ✅｜P0.2 ✅｜P0.3 ✅｜P0.4 ✅｜P1.1~P1.5 ✅｜P2.1 ✅｜P2.2 ✅（2026-10-16）｜**P2.5 CI → 下一步**

### 4.1 Intent 级调用栈与错误诊断 【P0】✅ 已完成

**缺口**：现在函数内出错只抛 Python 异常，用户看到的是 `mini_intent.py line 5649`，看不到 Intent 调用链。

**方案**：
- Interpreter 维护 `call_stack: List[Frame]`（函数名/行号/列号/源文件），execute_function 出入栈
- 运行时错误统一包装为 `IntentError`，携带：错误类型、消息、Intent 源位置、调用栈快照
- CLI 层渲染：源码行 + `^` 光标 + 调用链，对齐 Python traceback 的信息密度
- 契约违反用专属子类 `ContractViolation(requires/ensures 哪个条款、实际值、期望条件)`——契约是身份证，错误信息必须第一个被看见

**哲学映射**：致良知——良知不是感觉，是可检验的条件。错误信息是把「检验失败」精确指认给当事人。

**验收**：任意深层嵌套调用出错，输出含完整 Intent 调用链与出错行高亮。

**实施记录（2026-10-16）**：4 处改动——
1. `mini_intent.py` 新增 `IntentError`/`ContractViolation`/`CallFrame`（异常体系与栈帧）
2. `execute_function`/`_execute_method` 包装为薄壳：入栈→委托 inner→异常穿帧时快照调用链→finally 出栈（不逐处改 raise 点，反膨胀）
3. 契约违反从「静默失败」升级为抛 `ContractViolation`（携带违约条款/期望/实际）
4. CLI 新增 `wrap_intent_error`+`render_intent_error`：错误消息+源码行光标+调用链从外到内+退出码规范（0/1/2）

实测效果：
```
❌ 契约违反: 契约违约(requires): 前置条件1失败: b != 0.0 — 函数 safe_divide 拒绝执行
   at tests/t_contract_violation.intent:3:22
   3 |     requires b != 0.0
                         ^
   调用链(从外到内):
     main (tests/t_contract_violation.intent:13)
     compute (tests/t_contract_violation.intent:14)
     safe_divide (tests/t_contract_violation.intent:10)
```
回归：13/14 examples 通过；唯一失败的 demo.intent 为遗留 lambda 参数语法问题（旧代码同样失败），记入 P1 待办。

### 4.2 测试框架 `intent test` 【P0】

**缺口**：19 个模块、9435 行解释器，零自动化测试。regression 靠人肉。

**方案**：
- 语法：`test "名称" { assert expr; }` 块，或复用 `contract.intent` 的 assert 体系
- CLI：`python src/mini_intent.py --test [path]` 收集 `tests/**/*.intent`，报告通过/失败/断言详情
- 断言失败时带契约上下文（哪个 requires 没满足）
- 第一批用例：每个语言特性一个测试文件（复用现有 `_t_*.intent` 调试文件，它们本来就是回归测试的雏形）

**哲学映射**：实践是检验真理的唯一标准——测试就是把「真理」变成可重复执行的实践。

**验收**：一条命令跑完全部回归；CI 能挂。

**实施记录（2026-10-16）**：零语法侵入方案——
- 约定：测试文件中 `def test_xxx()` 函数即用例；`assert cond, "msg";` 为断言语句（**无括号**，assert 是关键字语句）；每个测试文件独立 Interpreter 保证状态隔离
- CLI：`python src/mini_intent.py --test [path]`（默认 `tests/`，`_` 开头文件跳过）
- 断言失败复用 P0.1 的错误渲染（源码位置+调用链），退出码 0/1/2
- **测试模式严格**：parser.errors 非零即失败（文件模式仍是宽松模式，见待办 T3）

**成果**：`tests/` 8 个测试文件 33 个用例全绿；examples 29/29 回归通过。

**测试框架即先知——首轮就抓出 1 个真 bug + 3 个文档/实现不一致**：

| # | 发现 | 处理 |
|---|------|------|
| B1 | **DictValue 相等性 bug**：`{"x":1} == {"x":1}` 恒 false（dataclass 空字段 eq 陷阱，`_t_dict_eq` 只 print 不 assert 所以藏了 3 个月） | ✅ 已修：Dict 比较改为逐项递归（与 List 同策略） |
| T1 | match range 模式 `90..100` **未实现**（philosophy_mapper.md 文档超前） | 测试暂用 `if guard`；实现记入 P1 |
| T2 | class 继承实际语法是 `class Dog < Animal`，mapper 文档写的是 `class B : A`（错） | 测试已按实现写；**修文档记入 P0.3** |
| T3 | Result 无成员方法路由，`r.unwrap()`/`r.is_ok` 不通 | ✅ 已修：MemberAccess+CallExpr 加 ResultValue 分支 |
| T4 | 文件模式宽松执行：语法错误只警告不阻断，退出码 0（假通过） | 记入 P0.4：`--check` 严格模式 |

### 4.3 语言规范文档 spec.md 【P0】

**缺口**：现在「Intent 是什么」散落在 8 章书稿（教学视角）和 9435 行实现（权威视角）里，没有正式的规范。

**方案**：
- `docs/spec.md`：词法（关键字/字面量/运算符全表）→ 语法（每个构造的 EBNF + 语义）→ 类型系统规则 → 标准库 API 签名
- 规范从**实现提取**而非凭空写：每个条目标注对应源码位置，保证 spec 与实现不漂移
- 这是以后写编译器/移植 C#/给社区贡献的锚点

**验收**：新人只读 spec.md + 8 章书稿，能正确写出任何合法 Intent 程序。

**实施记录（2026-10-16）**：
- 产出 `docs/spec.md`（v1.2.0）：词法全表→类型系统→语法（每构造标注源码锚点）→标准库 API→CLI→已知限制诚实清单→文档勘误记录
- 规范从实现反向提取，并用脚本实证每个关键字的真实支持度：**零分支预留关键字** `func`/`invariant`/`is`/`from`；`var`/`const` 实为 `let` 别名；`pure`/`effect` 仅记录不强制；位运算/复合赋值/`:=`/`++`/`--` 词法接受语义未实现
- **修正 philosophy_mapper.md 三处文档错误**：class 继承 `:` → `<`、类内方法 `};` → `}`、match range 改 guard 形式并注明未实现
- 新增 `tests/test_pipe.intent`（2 用例）——spec 声明的每个能力都应有测试背书，全量 **35/35 通过**

### 4.4 CLI 现代化 【P1】

**现状**：argparse 已有 run/tokens/ast/repl/demo/philosophy。
**补齐**：
- `-c "code"` 直接执行代码串（对齐 Python `-c`）
- `--emit ast|tokens` 输出到文件而非 stdout
- `--version` / `--check`（只解析不执行，做 lint 前置）
- 退出码规范：0 成功 / 1 运行时错误 / 2 用法错误（CI 依赖这个）

**实施记录（2026-10-16）**：
- 新增 `-c`（直接执行）、`--version`、`--check`（只解析，治宽松假通过）、`--emit tokens|ast FILE`（分析结果写文件）
- `parse_known_args`：源文件后的额外参数透传——新增 `args()` 内置（程序与世界的接口），**Intent 从此能写命令行工具**（philosophy_mapper.intent 立即受益，从跑不通到完整工作）
- 顺手修复 demo 代码 `let i` → `let mut i`（不可变变量做循环计数器，演示门面居然是坏的）
- 全量回归：tests 35/35、examples 30/30、demo/repl 冒烟全过

---

## 五、Phase 1：语言内核补全

> 目标：对齐 Python 的「写得舒服」，且每项都有哲学加成。

> **实施进度（2026-10-16 全部完成）**：P1.1 with ✅｜P1.2 f-string/多行 ✅｜P1.3a 类型别名+Union ✅｜P1.3b 泛型约束 ✅｜P1.4 异常层级 ✅｜P1.5 yield from ✅。全量 61/61 测试通过，examples 30/30，demo/repl 正常。测试 61 个（较 P0 末的 35 个新增 26 个 P1 用例）。

**实施记录**：
- **P1.1 with**：`with expr as x { body }`，块退出自动调 `close()`——defer 的块级特化（3 用例）
- **P1.2 字符串**：`f"..."` 前缀（显式插值宣告）+ `"""` 三引号多行（4 用例）；顺带发现并修复 **`in` 右侧不支持 String** 的真缺口（子串归属）
- **P1.3a 类型系统**：`type X = ...` 软关键字别名 + `A | B` Union（6 用例）。软关键字模式：`type(x)` 函数调用不受影响。**发现并记载设计规则**：Int 标注接受 Float 是刻意的数值互通（非 bug）
- **P1.3b 泛型约束**：`T: Comparable`，违约抛 ContractError 走契约错误通道（3 用例）
- **P1.4 异常层级**：ErrorValue 一等错误值（.type/.message/.stack）+ `catch e: ContractError` 类型分流，不匹配继续传播（5 用例）
- **P1.5 yield from**：生成器委派转发，支持 List/Dict 键（5 用例）

### 5.1 with 语句 —— 资源作用域 【P1】

**Python 参照**：`with open(f) as fh:` 自动管理资源生命周期。
**Intent 缺口**：有 `defer`（函数级、逆序、无条件）但没有块级作用域资源管理。
**设计**：
```intent
with open("data.txt") as fh {
    let content = fh.read_all();
};  // 作用域结束自动 close —— defer 在块级的具体化
```
**设计思路**：`defer` 是「功成身退」的函数级表达，`with` 是它的块级特化——资源获取（open）与释放（close）在同一个可见的花括号内对称出现，比 defer 更直观。两者共存：defer 管函数级清理，with 管块级资源。
**哲学映射**：向死而生——获取资源的那一刻，释放它的代码已经在等待。

### 5.2 字符串能力补齐 【P1】

**缺口**（对照 Python str）：f-string 插值、多行字符串、split/join 的完整语义（已有部分内置函数）。
**设计**：
```intent
let name = "Intent";
let greeting = f"你好，{name}，版本 {version()}";   // f-string
let poem = """心学为体
禅道为翼
马哲为用""";                                          // 多行字符串
```
**设计思路**：f-string 让「模板与数据在同一行相见」——心即理：你写下的字面与变量名，就是意图本身，不需要 `.format()` 这种间接层。
**优先级说明**：词法层改动小（`f"..."` 前缀 + `"""` 三引号），解释器加一个字符串插值求值，投入产出比高。

### 5.3 类型系统深化 【P1，最重要】

**缺口**：现在是纯运行时动态类型（无静态推断——`grep infer` 零命中）。函数级泛型有参数替换但无约束。

**分三步走，不许一步到位**（反膨胀）：

**Step 1 — 类型别名与 Union（语法层，1-2 天）**：
```intent
type Meters = Float;
type Shape = Circle | Square;   // Union：一个东西的多种存在形态
```
Union 的哲学：**不二法门**的推广——enum 是「封闭的几种」，Union 是「开放的几种」。

**Step 2 — 泛型约束（复用已有替换机制，2-3 天）**：
```intent
def max_of<T: Comparable>(items: List<T>): T { ... };
```
约束在调用点检查，违反报契约级错误（Comparable 不是可比较的 → 这不是类型错误，是**契约违反**，复用现有错误通道）。

**Step 3 — 可选静态检查器（独立工具，Phase 2）**：
不做完整类型推断（那是 mypy 级别的工程）。做一个**契约驱动的轻量检查器**：利用已有的 `requires/ensures` 和类型标注，做「声明一致性」检查——参数个数、标注类型与实参的明显不匹配、match 穷举性。Resolver 已经有语义分析遍的骨架，扩它。
**设计原则**：Intent 的类型策略是「契约优先，类型其次」——静态检查永远服务于契约验证，不追求图灵完备的类型理论。

### 5.4 错误处理深化 【P1】

**缺口**：Result/? / try/catch/finally 已有。缺：
- **异常层级**：定义内置异常树（`ContractError` / `ValueError` / `IndexError`...），`catch` 支持按类型捕获：`catch e: ContractError { ... }`
- **错误上下文**：catch 块内可访问 `e.message` / `e.stack`（来自 4.1 的调用栈）
- **panic/recover**：**不做**——与「错误是另一种正常」冲突。不可恢复错误用 `ensures` 表达。

```intent
try {
    let r = risky()?;      // Err 自然传播，不恐慌
} catch e: ContractError {
    // 契约违反：这不是程序的错，是调用方式错了
    print("合同违约：", e.message);
} finally {
    cleanup();
};
```

**哲学映射**：烦恼即菩提——catch 按类型分流，就是「认识你的烦恼是什么种类，然后对症转化」。

### 5.5 生成器补全 【P2】

**缺口**：有 yield，缺 `yield from`（委派）和生成器 `send`/`close` 协议。
**方案**：`yield from` 实现简单（解释器层转发）；`send` 需要双向通道，与并发模型的 channel 天然衔接——放 Phase 3 与并发一起做。

---

## 六、Phase 2：生态基建

> 目标：让 Intent 从「一个人的语言」变成「可协作的语言」。Python 赢在生态，不赢在语法。

> **实施进度**：P2.1 ✅｜P2.2 ✅｜P2.3 ✅｜P2.4 ✅｜P2.5 ✅（均 2026-10-16）｜**Phase 2 收官 → P3 标准库与并发**

> v2.0.0 里程碑：P0（4 项）+ P1（6 项）+ P2（5 项）共 15 个课题完成；61 测试；81 文件全过 check/lint/doc；CI 五步（check/test/lint/doc/fmt 幂等）。

### 6.2 Formatter `intent fmt` 【P1】✅ 已完成

**实施记录（2026-10-16）**：
- token 流重排不动语义：4 空格缩进、K&R 花括号、`;`/match 分支 `,` 换行、二元运算符两侧空格、`:` 前紧贴后空格、管道/`=>` 两侧空格
- Lexer 加 `keep_comments` 开关（Parser 路径零影响）：注释产 COMMENT token——**代码的哲学注释是灵魂，formatter 不许丢**
- Token 加 `is_fstring` 标记：formatter 还原 `f"..."` 前缀与字符串引号（Lexer 原本剥掉）
- 幂等验证通过；真实文件（lesson_01/std.str）格式化后 `--check` 全过
- 顺手修两个输出污染：banner 与 pyreadline 提示改为仅 TTY/stderr 显示（`--fmt > file` 管道纯净）
- 已知限制（诚实记录）：不补缺失分号（保守不动语义）、80 列不断行、无可配置项（gofmt 哲学）

### 6.1 包管理 【P1，生态第一优先级】✅ 已完成

**实施记录（2026-10-16）**：
- `intent.toml` 清单（tomllib 解析）：`[project]` name/version + `[deps]`（git url / 本地路径）
- `--install <url>` 单个安装 / `--install` 无参按清单批量（本地复制、git pull 更新、clone --depth 1）
- 启动时注入 `./lib` 与 `~/.intent/lib`（全局库）到模块搜索路径
- 模块查找加第三种候选 `<name>/<name>.intent`（npm 风格，git 仓库开箱即用）
- **顺手补实现了从未存在的 `export` 语句**（spec 里那条是从 README 抄的未验证条目——ExportStmt 是孤儿 AST，Lexer 连 export 关键字都没有）。现在 `export a, b;` 显式声明模块边界，无声明维持全量导出（兼容）
- 测试 runner 补上模块搜索路径注入（fixture 从任意 cwd 可跑）
- 全量 61/61 + fixture 2/2 通过

**仍然不做**：版本求解器、注册表（出现 3+ 真实第三方需求再做）。

### 6.1 包管理 【P1，生态第一优先级】

**设计**（刻意最小化，反 pip 膨胀）：
```
project/
  intent.toml      # [project] name/version + [deps] 名称 = "版本约束"
  src/
  tests/
```

**三件套，分两期**：
- **V0.1（本地优先，无注册表）**：`intent.toml` 声明 + `import` 支持从 `./lib`、`~/.intent/lib` 解析 + `intent install <git-url>` 克隆到本地 lib。**不碰版本求解器**——约束只支持 `=` 和 `>=`，冲突了直接报错让人工裁决
- **V0.2（注册表）**：只有当出现 3 个以上真实第三方包需求再做。注册表先做静态文件托管（GitHub Pages + JSON 索引），不做 PyPI 级基础设施

**哲学映射**：天地与我并生（第7章）——包管理是「万物一体」的基础设施：你的代码与世界连接。但连接贵在**简单可信**，版本求解器是复杂性瘟疫，V0.1 刻意不治。

### 6.2 Formatter `intent fmt` 【P1】

**设计**：token 流重排，不动 AST 语义。规则刻意少：4 空格缩进、80 列、`;` 保留（Intent 的分号是「一句话说完了」的句号，有哲学含义不删）、行尾注释对齐。**不追求配置化**——gofmt 的成功就在于没有配置。
**哲学映射**：大道不称——格式不该是个人品味，是语言的默认秩序。你不需要选择，秩序本自存在。

### 6.3 Linter `intent lint` 【P2】✅ 已完成

**实施记录（2026-10-16）**：AST 静态检查不执行，四条规则对应四条哲学：
- E1 `let` 常量被重新赋值（不可变是默认）——**作用域敏感**：块内 let 不出块、方法间同名互不相干（初版按函数分组误报，重写为域栈递归下降）
- W1 空 catch 块（沉默的 catch 比没有 catch 更糟）
- I1 顶层函数无契约（契约是身份证）
- W2 import 未使用（不带多余的东西上路）

分级 E/W/I，有 E 退出 1；全量 81 文件 0 错误级。**又抓出 3 个宽松模式掩盖的真问题**（BIM 库 let 后改值，执行时会炸只是没被调用）。
原设计中的「let mut 从未被赋值」规则暂缓（误报率高，收益低）。

### 6.4 文档生成 `intent doc` 【P2】✅ 已完成

**实施记录（2026-10-16）**：`--doc` 从函数签名 + 上方注释块 + 契约生成 markdown（`_unparse` 表达式反打印，`ensures result >= 0` 而非 AST repr）；类输出方法列表。全量 81 文件生成不崩。
docstring 语法未新增 spec（`///`/`"""` 二选一的决策推迟到有真实需求）；当前用函数上方 `//` 注释块作文档——注释即文档，不发明第二套。

### 6.5 CI 与发布 【P1】✅ 已完成

**实施记录（2026-10-16）**：
- `.github/workflows/ci.yml`：push/PR 触发，五步——全文件 `--check`（81 个文件严格模式）+ `--test` + `--lint`（0 错误级）+ `--doc`（全文件不崩）+ formatter 幂等抽查
- CI 前置清理：修掉宽松模式掩盖的 3 个脏文件（lesson_03 字符串嵌引号、lesson_05 `catch {`、std/contract.intent 关键字撞名死函数），**重写 demo.intent**（原文件调用一堆从未实现的标准库函数，是「幻想文档」；现为 8 特性真实门面）
- 版本 v1.2.0 → **v2.0.0**（契约违约行为破坏性变更）；CHANGELOG.md 记录全history
- 本地模拟 CI 三步全过；tests 61/61；全部 81 个 .intent 文件通过严格语法检查

- GitHub Actions：push 跑 `intent test`（Phase 0.2）+ `intent check`（6.3）
- 版本语义：语义化版本 + CHANGELOG.md，每次发布附「新增特性的哲学映射」——**发布说明就是书稿的连载**。这条对内容 IP 战略有直接价值

---

## 七、Phase 3：标准库扩张与并发

### 7.1 标准库优先级（按「通用语言必备度」排序）

| 优先级 | 模块 | 内容 | 理由 |
|--------|------|------|------|
| P1 | `re` 正则 | 匹配/替换/切分/编译 | Python 生态基石，文本处理绕不开 |
| P1 | `datetime` | 日期运算/格式化/时区 | time.intent 只有时间戳，业务代码天天要 |
| P1 | `itertools` | permutations/combinations/product/chain | 组合爆炸的穷举——「格物」的基础设施 |
| P1 | `collections` | deque/Counter/defaultdict/namedtuple | 数据结构全家桶，Python 日用好物 |
| P2 | `csv` | 读写（对齐 Python csv 模块） | BIM 数据导出/导入刚需 |
| P2 | `sqlite3` | 嵌入式数据库绑定 | 阿J 的地球OL/DynoManager 都是 SQLite，自建语言不吃自己的库说不过去 |
| P2 | `functools` | partial/compose/lru_cache | compose 与管道 `|>` 天然一家 |
| P2 | `http` client | GET/POST/JSON | 通用语言的门票；LLM API 调用靠它 |
| P3 | `struct`/`base64` | 二进制/编码 | BIM 文件处理 |
| P3 | `heapq`/`bisect` | 算法库 | 管道路由 A* 已内联在 bim 模块，通用化提取 |
| P3 | `threading`/`queue` | 线程安全队列 | 与 7.2 并发模型一起 |

**每加一个模块的纪律**：模块必须带 `requires/ensures` 契约；必须进 spec.md；必须配测试。标准库是语言的样板戏——标准库自己违约，契约宪法就是笑话。

> **实施进度（2026-10-16）**：itertools ✅｜collections ✅｜re/datetime → 下一步。
> itertools 落地为 chain/zip_longest/cycle/enumerate/flatten/unique/chunk/groupby/count_where（permutations/combinations/product 留待真实需求——反膨胀，先交付「日常 80%」）。
> collections 落地为 counter/most_common + Stack/Queue 类（deque/defaultdict/namedtuple 缓议）。
> **过程中修掉 3 个解释器真 bug**：`x? == v` 的 TryExpr/三元歧义（panic mode 吞 `?`）、`RuntimeValue.copy` 漏子类（dict 传参即崩，第 9 个真 bug）、dict 键形态分裂（get/set/has_key 归一 `_norm_key`，第 8 个）。测试 61→76。

### 7.2 并发模型 【P2，最后做】

**为什么最后**：树遍历解释器加并发是伤筋动骨的手术，语法、运行时、标准库三线联动。放在生态基建之后，且必须想清楚哲学定位。

**三个候选，按哲学契合度**：

| 方案 | 机制 | 哲学契合 | 成本 |
|------|------|---------|------|
| A. Channel + goroutine | `spawn f()` + `ch <- v` / `<- ch` | ⭐⭐⭐ 「知行合一」的时空分离：发送者与接收者各自节奏，数据在中间相遇 | 高（调度器） |
| B. async/await | `async fn` + `await` | ⭐⭐ 与管道流式天然合，但关键字抄袭 Python，无哲学加成 | 中 |
| C. 结构化并发 | `scope { spawn ...; }` 作用域结束自动 join | ⭐⭐⭐ 「向死而生」：并发任务的生命周期在创建时就被限定 | 中高 |

**推荐 C 的结构化并发 + A 的 channel 通信**：`spawn` 出来的任务必须挂在某个作用域上，作用域退出时等待/取消——这符合 Intent 的「声明即存在」宪法：任务的生与死都在声明处可见。channel 作为唯一通信原语（不共享内存）。
**Step 1 最小切片**：解释器内嵌 Python threading 实现 `spawn` + 线程安全 channel，只做演示级；Step 2 再考虑协程调度器。
**验收**：能写生产者-消费者管道：`data |> producer |> consumer` 的并发版。

---

## 七点五、Phase 4：字节码编译器（M10 ✅ 2026-10-17）

> 语言分两阶段：先让它能跑（树遍历解释器），再让它跑得快（字节码 + VM）。
> AST 是意，字节码是言——言不尽意，但言可执行。

**实施记录（2026-10-16/17）**：
- `src/intent_bytecode.py`：指令集 20 条 + Emitter（AST → 指令，跳转回填）+ 栈式 VM（值栈 + 调用帧 + 100 万步熔断）
- CLI：`--compile file [--run-vm]`；编译元信息走 stderr、程序输出走 stdout——与解释器 stdout 可直接 diff
- **M10 V0.1 覆盖**：let/let mut、算术与比较运算、print、if/else、while、函数定义与调用（含递归 fib 验证）、return
- 行为对照测试：`tests/vm_check.intent`（while 累加 + 递归 fib + if/else），CI 步骤「VM 与解释器行为对照」逐字节 diff
- **M11（下一步）**：闭包/管道/match/Result/契约/with/生成器——按 LangForge 无人值守闭环逐轮扩展
- 途中修复：Resolver 的 for-iterable 作用域深度错标（普通变量作 iterable 时 NameError，range() 因内置 fallback 掩盖）；单文件入口的 `sys.modules['mini_intent']` 注册（防辅助模块重新加载出第二套类定义）

---

## 八、明确的「不做」清单（反膨胀防线）

| 不做 | 理由 |
|------|------|
| JIT / 字节码编译 | 树遍历解释器的使命是「清晰」不是「快」。性能优化留给未来的 C# 移植版 |
| 完整的静态类型推断 | 违反「代码即意图」：推断让类型藏起来。契约 + 标注已经够 |
| pip 级版本求解器 | 复杂性瘟疫。V0.1 本地优先，约束冲突人工裁决 |
| 宏系统 | match + 装饰器 + 管道已覆盖 99% 场景，宏打开的是不可读性地狱 |
| panic/recover | 违反「错误是另一种正常」 |
| 多后端（LLVM/WASM） | 生态没起来前，多后端是多份维护噩梦 |
| 运算符重载扩展到全部魔术方法 | Python 的 `__add__` 家族是过度设计，保留当前核心运算符即可 |
| bf2py.py / zh2py.py | Dynamo 时代历史玩具，与语言无关，建议归档到 `attic/` |

---

## 九、执行顺序与工作量（人日）

| 阶段 | 项目 | 工作量 | 累计 |
|------|------|--------|------|
| P0.1 | 调用栈与错误诊断 | 3 | 3 |
| P0.2 | 测试框架 | 3 | 6 |
| P0.3 | spec.md | 2 | 8 |
| P0.4 | CLI 现代化 | 1 | 9 |
| P1.1 | with 语句 | 1 | 10 |
| P1.2 | 字符串（f-string/多行） | 2 | 12 |
| P1.3a | 类型别名 + Union | 2 | 14 |
| P1.3b | 泛型约束 | 3 | 17 |
| P1.4 | 异常层级 + catch 类型 | 2 | 19 |
| P2.1 | 包管理 V0.1 | 4 | 23 |
| P2.2 | formatter | 3 | 26 |
| P2.5 | CI + 发布流程 | 1 | 27 |
| P3.1a | re + datetime + itertools + collections | 6 | 33 |
| P3.1b | csv + sqlite3 + functools + http | 8 | 41 |
| P2.3/P2.4 | linter + doc 生成 | 5 | 46 |
| P1.5/P3.2 | yield from + 并发模型 | 10 | 56 |

**27 人日（P0+P1+P2 核心）后，Intent 达到「可认真当生产力工具介绍给外人」的门槛。** 前 9 人日（整个 P0）优先做——那是所有后续工作的地基。

---

## 十、与长期战略的衔接

1. **每个新特性 = 书稿新素材**：8 章之后还有第 9-14 章的选题已经摆在路上——with（向死而生块级版）、Union（不二法门推广）、结构化并发（生死声明处）、包管理（万物一体的基础设施）。语言演进与内容 IP 是同一条生产线
2. **契约引擎是独立产品线**：`contract_skill/` 持续演进为 LLM 编程助手的「意图验证层」——这是最快可能圈外变现的资产，与语言演进解耦、双线并进
3. **BIM 库保持特区地位**：管道路由等 8 模块不追通用化，保持可直接移植 C# 的纯净度——它是「圈内能力圈外化」的桥，不是语言的包袱

---

*「不是先有一个『编程语言』的本质再去实现它。路线图不是命运，是当前的觉知——随时可以格它。」*
