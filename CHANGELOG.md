# 更新日志

本项目的重大变更记录。版本遵循语义化版本。

---

## v2.1.0 — 字节码编译器（2026-10-17）

> AST 是意，字节码是言——言不尽意，但言可执行。语言分两阶段：先让它能跑，再让它跑得快。

| 特性 | 说明 |
|---|---|
| 字节码编译器 M10 | `src/intent_bytecode.py`：指令集 20 条 + Emitter（跳转回填）+ 栈式 VM（调用帧 + 死循环熔断） |
| CLI | `--compile file [--run-vm]`；编译信息走 stderr、程序输出走 stdout（与解释器可 diff 对照） |
| V0.1 覆盖 | let/算术/比较/print/if/while/函数调用（含递归）/return |
| 标准库扩张 | itertools（9 函数）+ collections（counter/most_common + Stack/Queue 类） |
| 行为对照 | tests/vm_check.intent + CI 逐字节 diff |

**修复的真 bug（V0.1 途中）**：TryExpr 与三元歧义（`x? == v`）、`RuntimeValue.copy` 漏子类（dict 传参即崩）、dict 键形态分裂（`_norm_key` 统一）、Resolver for-iterable 作用域深度错标、BIM 库 let 重赋值 ×3、单文件入口双模块类身份。

---

## v2.0.0 — 语言重新激活（2026-10-16）

> 心学为体，禅道为翼，马哲为用。
> v1.2 是「编译原理学习载体」的完成态；v2.0 是同一套哲学在「通用语言」方向的重新激活——
> 不是推倒重来，是给已验证的内核补上让它能面对世界的地基与生态。

**破坏性变更**：
- 契约违约（requires/ensures 未满足）从「静默记录」改为**抛 `ContractViolation`**——契约是身份证，违约必须被看见
- 文件模式语法错误行为不变（宽松执行，退出码 0）；测试模式与 `--check` 为严格模式（退出码 2）

### Phase 0：地基加固

| 特性 | 说明 |
|---|---|
| 调用栈与错误诊断 | `IntentError`/`ContractViolation` 异常体系 + Intent 级调用链 + 源码行光标渲染 + 退出码规范（0/1/2） |
| 测试框架 | `--test` 命令：`def test_*()` 约定 + `assert cond, "msg";` 断言语句 + 每文件独立解释器 |
| 语言规范 | `docs/spec.md`：从实现反向提取的权威规范，每个条目标注源码锚点 |
| CLI 现代化 | `-c` 直接执行 / `--check` 严格检查 / `--emit tokens\|ast` / `--version` / `args()` 命令行参数 |

### Phase 1：语言内核

| 特性 | 哲学映射 |
|---|---|
| `with` 语句 | 向死而生的块级特化——获取与释放在同一对花括号内对称出现，退出自动 `close()` |
| `f"..."` / `"""` 多行字符串 | 心即理——模板与数据在同一行相见 |
| `type` 别名 + `A \| B` Union | 不二法门的推广——一个东西的多种存在形态（`type` 为软关键字，不影响 `type()` 函数） |
| `T: Comparable` 泛型约束 | 类型参数的要求与 requires 同性质——违约走契约错误通道 |
| `catch e: ContractError` 异常层级 | 烦恼即菩提——错误作为一等值（`.type`/`.message`/`.stack`），按类型分流 |
| `yield from` 生成器委派 | 组合先于发明 |

### Phase 2：生态基建

| 特性 | 说明 |
|---|---|
| 包管理 V0.1 | `intent.toml` 清单 + `--install`（git/本地依赖）+ `./lib` 与 `~/.intent/lib` 搜索路径。刻意无版本求解器 |
| `export` 显式导出 | 你是社会关系的总和——暴露给外部才成为真实存在（补齐从未实现的特性） |
| Formatter | `--fmt`：token 流重排不动语义，4 空格/K&R/幂等，保留注释（gofmt 哲学：格式是默认秩序不是个人品味） |
| CI | GitHub Actions：全文件 `--check` + `--test` + formatter 幂等抽查 |
| demo 重写 | 从「幻想文档」（调用从未实现的标准库函数）改为只用真实特性的门面 |

### 修复的真 bug

- **DictValue 相等性**：`{"x":1} == {"x":1}` 恒 false（dataclass 空字段 eq 陷阱）——改为逐项递归比较
- **Result 成员路由缺失**：`r.unwrap()` / `r.is_ok` 不通——MemberAccess/CallExpr 补分支
- **`in` 右侧不支持 String**：`"子" in "字符串"` 报错——子串归属是格物的基本操作
- **Windows 三件套**：`from __future__ import annotations`（前向引用 NameError）、readline 降级、repl.bat 路径

### 测试与文档

- 测试从 0 → 61 用例（tests/ 10 文件）+ pkg fixture
- spec.md v2.0 / roadmap.md（含实施记录）/ philosophy_mapper.md 三处文档勘误
- examples/tests/std 全部 81 个文件通过严格语法检查

---

## v1.2.0（2026-07-03）

初版完成态：解释器全链路（Lexer→Parser→Resolver→树遍历）+ 契约引擎 + 8 章《用代码学哲学》+ BIM 标准库 8 模块。67 commits，「项目完结」。
