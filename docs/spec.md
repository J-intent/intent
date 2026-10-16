# Intent 语言规范 v1.2.0

> 心学为体，禅道为翼，马哲为用
> **本文档是 Intent 的权威规范**，从实现（`src/mini_intent.py`）反向提取，每个条目标注源码锚点。
> 教学视角见 `docs/chapter_01~08_*.md`；设计哲学见 `docs/philosophy_mapper.md`。
> 规范与实现冲突时，以本文件标注的源码行为为准，并提 issue 修文档。

**状态标注**：✅ 已实现 ｜ 🔜 已预留（词法接受，语义未完整） ｜ ⚠️ 文档曾写错（已在本版修正）

---

## 1. 词法

### 1.1 字符与注释

源码 UTF-8。三种注释（`Lexer.skip_comment` mini_intent.py:262）：

```intent
# 井号注释
// 双斜杠注释
/* 块注释 */
```

### 1.2 标识符与关键字

标识符：字母/下划线开头，含字母数字下划线。

**关键字**（`Lexer.KEYWORDS` mini_intent.py:203）按支持度分三档：

| 已实现 ✅ | let, def, return, if, else, elif, for, while, break, continue, match, requires, ensures, import, as, class, this, mut, fn, try, catch, finally, defer, assert, enum, yield, and, or, not, in |
|---|---|
| 字面量关键字 ✅ | true, false, null（None/True/False 同义接受） |
| 记录性注解 ✅ | pure（`func.is_pure`，仅记录不强制）, effect `[...]`（效果列表，仅记录） |
| 别名（兼容，推荐用主形式） | var, const ≡ let |
| 预留未实现 🔜 | func（用 def/fn）, from（用 import）, is（用 ==）, invariant（契约扩展） |

**内置类型标识符**（非关键字，`Lexer.BUILTIN_TYPES` mini_intent.py:212）：`Int` `Float` `String` `Bool` `List` `Dict`

### 1.3 字面量

| 类型 | 形式 | 示例 |
|---|---|---|
| Int | 十进制数字 | `42` `-7` |
| Float | 带小数点或科学计数 | `3.14` `1e-3` |
| String | 双引号，支持 `\` 转义 | `"hello\n"` |
| f-string | `f"..."` 前缀（显式插值宣告） | `f"${name} 好"` |
| 插值字符串 | `${expr}` 内嵌求值 | `"${name} 得分 ${score}"` |
| 多行字符串 | `"""..."""` 或 `'''...'''`，保留换行 | 见下 |
| Bool | `true` / `false` | |
| Null | `null` | |
| List | `[a, b, c]` | `[1, 2, 3]` |
| Dict | `{key: value}` | `{"x": 1}` |

### 1.4 运算符全表（`Lexer.SYMBOLS` mini_intent.py:216）

| 类别 | 运算符 |
|---|---|
| 算术 | `+` `-` `*` `/` `%` `**` `//` |
| 比较 | `==` `!=` `<` `>` `<=` `>=` |
| 逻辑 | `and` `or` `not`（关键字形式） |
| 位运算 🔜 | `&` `|` `^` `~` `<<` `>>`（词法接受，语义未实现） |
| 赋值 | `=` `+=` `-=` `*=` `/=` `%=` `**=` `//=` 等 🔜（除 `=` 外预留） |
| 结构 | `(` `)` `{` `}` `[` `]` `,` `:` `;` `.` |
| 箭头 | `->`（返回类型） `=>`（match 分支/λ） |
| 管道 | `|>` |
| 其他 | `@`（装饰器） `:=` `++` `--` 🔜 |

---

## 2. 类型系统

### 2.1 类型规则（Intent 与 Python 的根本分歧）

1. **运行时动态类型**：值在运行时携带类型；没有编译期类型检查
2. **类型推断 = 心即理**：`let x = 10;` 无需标注，系统知道 `x: Int`
3. **let 默认不可变**：`let` 声明的变量不可重新赋值；`let mut` 显式宣告可变（`Scope.declare` mini_intent.py:3040 附近，违例报「无法修改常量」）
4. **契约优先于类型**：`requires/ensures` 是运行时可验证的断言，比类型标注更受信任
5. **数值互通（刻意宽松）**：`Int` 标注接受 `Float` 值（`IntType.can_assign_from` 显式设计）；类型别名与 Union 同理遵循各底层成员规则
6. **泛型约束即契约**：`T: Comparable` 违约抛 `ContractError`（契约错误通道），不是普通 TypeError

### 2.2 类型标注语法

```intent
let x: Int = 10;              // 显式标注(可选)
def f(a: Float, b: Float): Float { ... }   // 参数与返回类型
def g<T>(x: T): T { ... }     // 泛型函数(类型参数从实参推断)
```

### 2.3 内建类型

| 类型 | 值类型 | 相等性 |
|---|---|---|
| Int | 64 位整数 | 值相等 |
| Float | 双精度浮点 | 值相等 |
| String | Unicode 字符串 | 值相等 |
| Bool | true/false | 值相等 |
| List | 有序序列，元素可为混合类型 | 逐元素递归相等（`_binary_op` mini_intent.py:6186） |
| Dict | 字符串/数值键 → 值 | 键集合一致 + 值逐项递归相等（mini_intent.py:6200，2026-10-16 修复） |
| Result<T,E> | Ok(v) / Err(e) | — |

### 2.4 Result<T,E>（烦恼即菩提）

```intent
let r = Ok(42);               // 构造: Ok(v) / Err(e)
let r2 = safe_divide(10, 0)?; // ? 操作符: Err 向上传播,Ok 解包
r.is_ok                       // Bool 属性
r.unwrap()                    // 方法: Ok 返回值,Err 抛 NameError
```

### 2.5 泛型（函数级）与约束

```intent
def identity<T>(x: T): T { return x; };
identity(42);      // T = Int

def max_of<T: Comparable>(a: T, b: T): T { ... };
max_of(3, 7);      // Int 满足 Comparable → 7
max_of(Ok(1), Ok(2));  // Result 不满足 → ContractError(契约违约)
```

内置约束：`Comparable`（Int/Float/String/Bool）、`Numeric`（Int/Float）。未知约束宽容放行。
类型别名（`type Meters = Float;`）为透明同义词；Union（`A | B`）任一成员合法即通过。

---

## 3. 语法

> 语句以 `;` 结尾（一句话说完了）。顶层结构 = 函数定义 + 全局语句。

### 3.1 变量声明

```
let [mut] name [: Type] = expr ;
```
⚠️ `var`/`const` 是 `let` 的兼容别名，新代码用 `let`。

### 3.2 函数定义

```
def name(params) [: ReturnType] [requires ...] [ensures ...] { body } ;
```
- 默认参数：`def f(x: Int, y: Int = 10) { ... }`
- Lambda：`fn(x) { return x * 2; }` 或 `fn(x) => x * 2` 🔜（箭头体未实现，用块体）
- 闭包：函数可嵌套定义，携带诞生环境（`_t_clret.intent` 验证）
- 装饰器：`@deco def f() {...}` 🔜（解析支持，执行路径有限）
- 生成器：函数体内 `yield expr;`，收集为 List 返回（mini_intent.py:5367）
- 生成器委派（P1.5）：`yield from expr;`——可迭代对象的元素逐个转发（支持 List/Dict 键）

**契约**（一等公民，Intent 的身份证）：
```intent
def divide(a: Float, b: Float): Float
    requires b != 0.0          // 进门签合同:不满足则拒绝执行(抛 ContractViolation)
    ensures result * b == a    // 出门前验货:result 是返回值的特殊名
{
    return a / b;
};
```

### 3.3 控制流

```intent
if cond { ... } else if cond2 { ... } else { ... }   // if 是表达式,可 let r = if c { 1 } else { 0 };
while cond { ... };
for x in iterable { ... };          // iterable: List / Dict(遍历键) / range()
for (k, v) in dict { ... };         // 解包遍历
break; continue;
"sub" in "string";                 // in 右侧支持 String(子串归属)
```

### 3.3b with 语句（P1.1，块级资源管理）

```intent
with Resource("db") as r {          // 块退出时自动调用 r.close()(若有)
    r.use();
};
```

### 3.3c 类型别名与 Union（P1.3a）

```intent
type Meters = Float;                // 别名: 透明同义词(type 是软关键字)
type Shape = Circle | Square;       // Union: 任一成员合法即通过
let x: Int | String = 42;
```

### 3.4 match 模式匹配（表达式，强制穷举检查）

```intent
let grade = match score {
    "A" => "优秀",              // 字面量
    n if n >= 90 => "A",        // 守卫(变量绑定 + if 条件)
    _ => "其他",                // 通配符(有意识地放弃穷举)
};
```

支持的模式：字面量 / 变量绑定 / `_` 通配 / or 模式 `A | B` / 构造器解构。
**match range 模式（`90..100`）🔜 未实现**——philosophy_mapper.md 曾写成已支持，实际需用 `if` 守卫（2026-10-16 测试发现）。
穷举检查：无通配/变量/或模式覆盖全部字面量时，静态报 `MatchError`（`_check_match_exhaustive` mini_intent.py:1509）。

### 3.5 错误处理

```intent
try { risky(); } catch e { handle(e); } finally { cleanup(); };
defer { cleanup(); };        // 作用域退出时逆序执行(函数级)
```

- `catch` 必须带变量名：`catch e { }` 或 `catch (e) { }`（lesson_05 曾写 `catch {`，2026-10-16 确认为文档错误）
- `try/catch/finally` 皆为表达式
- **catch 按类型分流（P1.4）**：`catch e: ContractError { }`——类型不匹配的异常继续传播；错误值成员 `e.type` / `e.message` / `e.stack`
- 不可恢复错误不用异常，用契约（宪法第 4 条）

异常类型名（`PY_TO_INTENT_EXC` 映射）：ContractError / AssertError / ValueError / TypeError / IndexError / KeyError / ZeroDivisionError / NameError / RuntimeError / SyntaxError / ImportError。

### 3.6 类与枚举

```intent
class Point {                 // ⚠️ 继承用尖括号: class Dog < Animal(不是冒号!)
    def init() { this.x = 0; }        // 构造器
    def set(x: Int) { this.x = x; }   // 方法(类体内 } 后不加分号)
    def get(): Int { return this.x; }
};
let p = Point();              // 实例化
p.set(3);                     // 方法调用
p.x;                          // 字段访问

enum Direction { North, South, East, West };   // 枚举:变体注册为全局常量
```

运算符重载：实例定义 `__add__`/`__eq__` 等方法即生效（`_binary_op` mini_intent.py:6225）。

### 3.7 管道与推导式

```intent
let result = data |> filter(valid) |> map(transform);   // |> 管道:从左到右
let squares = [x * x for x in nums if x > 2];           // 列表推导式
let m = {k: len(k) for k in pairs};                     // 字典推导式
```

### 3.8 模块系统

```intent
import std.math;              // 标准库
import mylib;                 // 项目文件(搜索路径: 文件目录及其 std/ lib/ ./ ./std ./lib + ~/.intent/lib)
import mylib as ml;           // 别名
export my_func, my_const;     // 显式导出(P2.1): 无 export 声明的模块维持全量导出(兼容)
```

模块查找优先级：`<base>/<name>.intent` → `<base>/<name>/__init__.intent` → `<base>/<name>/<name>.intent`（npm 风格）。
模块 = 文件；循环导入检测（`_import_stack`）；每个模块独立执行，导入时注册其导出符号。

### 3.9 包管理（P2.1，V0.1 本地优先）

项目清单 `intent.toml`：

```toml
[project]
name = "myproj"
version = "0.1.0"

[deps]
mathkit = { git = "https://github.com/x/mathkit.git" }  # git 依赖
utils   = "../utils"                                     # 本地路径依赖
```

- `--install <url>`：安装单个依赖（git clone --depth 1 到 `./lib/<name>`）
- `--install`（无参）：按 intent.toml 的 `[deps]` 批量安装（本地路径复制、git  pull --ff-only 更新）
- 启动时：`./lib` 与 `~/.intent/lib`（全局库）自动加入模块搜索路径
- **刻意不做版本求解器**：依赖值即源地址（git url / 本地路径），clone HEAD；版本约束冲突人工裁决

---

## 4. 标准库

### 4.1 内置函数（70+，`_setup_builtins` mini_intent.py:3481）

| 类别 | 函数（签名） |
|---|---|
| 输出断言 | `print(...)` `assert(cond, msg)` |
| 集合 | `len(x)` `keys(d)` `values(d)` `push(l, v)` `pop(l)` `insert(l, i, v)` `remove_at(l, i)` `enumerate(l)` `zip(a, b)` `range(...)` `reversed(x)` `sorted(x)` `any(l)` `all(l)` `contains(x, v)` |
| 类型转换 | `int(x)` `float(x)` `str(x)` `bool(x)` `type_of(x)` `type(x)` |
| 数学 | `abs(x)` `min(...)` `max(...)` `sum(l)` `sqrt(x)` `pow(a, b)` `floor/ceil/round(x)` `log/exp/cos/sin/tan/acos/asin/atan(x)` `atan2(a, b)` `pi` `random()` `randint(a, b)` |
| 字符串 | `split(s, sep)` `join(l, sep)` `trim(s)` `ord(c)` `chr(n)` `starts_with/ends_with(s, p)` `replace(s, a, b)` `to_upper/to_lower(s)` `substr(s, start, end)` |
| Result | `ok(v)` `err(e)` |
| 文件 | `read_file(p)` `write_file(p, c)` `list_dir(p)` `file_exists(p)` `is_dir/is_file(p)` `make_dir(p)` `delete_file(p)` `file_size(p)` `file_modified(p)` |
| 系统 | `env(k)` `cwd()` `ch_dir(p)` `shell(cmd)` `platform()` `path_join/basename/dirname/ext(p)` `now()` `sleep(ms)` `input(prompt)` `version()` `args()` |
| 序列化 | `json_parse(s)` `json_dump(v)` |

### 4.2 std 模块（`std/*.intent`）

| 模块 | 函数 |
|---|---|
| `str` | length, is_empty, concat, repeat, contains, starts_with, ends_with, index_of, last_index_of, substring, to_upper, to_lower, replace, cut, glue, strip, match_at |
| `math` | add, multiply, square, abs, max, min |
| `list` | sum, contains, any, all, take, drop, zip, map, filter, reduce |
| `itertools` | chain, zip_longest, cycle, enumerate, flatten, unique, chunk, groupby, count_where |
| `collections` | counter, most_common, class Stack(push/pop/peek/size/is_empty), class Queue(enqueue/dequeue/peek/size/is_empty) |
| `time` | current_timestamp, delay, timestamp_ns, elapsed_ms, elapsed_ns |
| `json` | parse, stringify, read_json, write_json |
| `random` | random_val, rand_int, uniform, choice, dice |
| `fs` | ls, exists, is_directory, is_regular_file, mkdir, remove, read_all, write_all, size_bytes, mtime |
| `os` | getenv, curdir, chdir, run, sys_platform, home_dir |
| `sys` | read_file, write_file, timestamp, debug, exit |
| `contract` | assert, require_positive, require_non_negative, require_in_range, require_divisor_non_zero, require_non_empty, ensure_result_not_null, ensure_result_in_range, ensure_length_le_original, ensure_result_positive, mut |
| `bim/*` | unit(单位换算) / geometry(Vector3D 等) / transform(矩阵) / solid / polygon / pipe / pipe_fittings / pipe_routing(A* 3D 寻路) |

字典方法（P3.1）：`d.has_key(k)` / `d.keys()` / `d.values()`；dict 键统一为 Python 标量形态（`DictValue._norm_key`），int/float/str/bool 键均可，`{1: "a"}` 与 `squares[3]` 自然工作。

### 4.3 字节码编译器（M10, V0.1 核心子集）

`src/intent_bytecode.py`：AST → 字节码 → 栈式 VM。V0.1 覆盖 let/let mut、算术与比较、print、if/else、while、函数定义与调用（含递归）、return；指令集 20 条（LOAD_CONST/LOAD_VAR/STORE_VAR/算术比较/JUMP/JUMP_IF_FALSE/CALL/RET/PRINT/POP）。跳转用回填（两遍补齐）。VM 有 100 万步死循环熔断。其余特性（闭包/管道/match/Result/契约/with/生成器）属 M11。
输出约定：编译元信息走 stderr，程序输出走 stdout——`--compile --run-vm` 的 stdout 与解释器 stdout 可直接 diff 对照（tests/vm_check.intent + CI 步骤）。
注：`src/mini_intent.py` 作为 `__main__` 运行时会把自身注册进 `sys.modules['mini_intent']`——辅助模块 `from mini_intent import ...` 才不会重新加载出第二套类定义。

---

## 5. CLI

```
python src/mini_intent.py <file>           # 执行
python src/mini_intent.py <file> [args...] # 执行, 额外参数经 args() 读取
python src/mini_intent.py -c "code"        # 直接执行代码串
python src/mini_intent.py --check [file]   # 只解析不执行: 干净退出0, 错误退出2
python src/mini_intent.py --compile file.intent [--run-vm]  # M10: 编译字节码(可选 VM 执行)
python src/mini_intent.py --emit tokens|ast <file>   # 分析结果写文件
python src/mini_intent.py --test [path]    # 测试(默认 tests/, _ 开头跳过)
python src/mini_intent.py --lint file.intent         # 静态检查(let 重赋值/空 catch/无契约/未用 import)
python src/mini_intent.py --doc file.intent          # 生成 markdown 模块文档
python src/mini_intent.py --fmt file.intent         # 格式化, 输出到 stdout(重定向即写回)
python src/mini_intent.py --install [url]     # 安装依赖(不带 url 按 intent.toml 批量)
python src/mini_intent.py --version        # 版本
python src/mini_intent.py -t / -a          # 只看 tokens / AST
python src/mini_intent.py -r               # REPL
python src/mini_intent.py -d               # 演示
python src/mini_intent.py -p               # 哲学视角翻译
```

退出码：0 成功 ｜ 1 运行时/测试失败 ｜ 2 用法/语法错误（`--check`）。
banner 与 pyreadline 提示只在 TTY 显示（`--fmt > file` 等管道场景输出纯净）。
⚠️ 文件模式当前为**宽松执行**（语法错误警告后继续，退出码 0）——测试模式与 `--check` 严格。CI 请用 `--check` + `--test`。

---

## 6. 已知限制（诚实清单）

| # | 限制 | 状态 |
|---|------|------|
| 1 | 树遍历解释器，无字节码/JIT | 设计选择（清晰优先） |
| 2 | 并发（async/thread/channel）完全缺失 | 路线图 P3.2 |
| 3 | 包管理（intent.toml/注册表）缺失，import 仅文件级 | V0.1 ✅ 已实现（2026-10-16：intent.toml + --install + lib 搜索路径；注册表待真实需求） |
| 4 | 位运算、复合赋值、`:=`/`++`/`--` 词法接受但语义未实现 | 预留 |
| 5 | match range 模式、类型别名/Union 未实现 | ~~路线图 P1.3~~ ✅ 已实现（2026-10-16，match range 仍未实现） |
| 6 | 静态类型检查缺失（Resolver 只做作用域分析） | 设计选择（契约优先） |
| 7 | f-string/多行字符串：插值 `${}` 已支持；`f"..."` 前缀与 `"""` 三引号未实现 | ✅ 已实现（2026-10-16） |
| 8 | formatter/linter/LSP 缺失 | formatter ✅ linter ✅ doc ✅ 已实现（2026-10-16）；LSP 仍缺 |
| 9 | with 语句 | ✅ 已实现（2026-10-16） |
| 10 | yield from / 泛型约束 | ✅ 已实现（2026-10-16） |

---

## 7. 文档勘误记录（本版修正）

| 位置 | 原文 | 修正 | 依据 |
|---|---|---|---|
| philosophy_mapper.md | `class B : A { ... }` | `class B < A { ... }` | Parser mini_intent.py:1006 |
| philosophy_mapper.md | `90..100 => "A"` | match range 未实现，用 `n if n >= 90 => "A"` | `_parse_pattern` 无 range 分支 |
| chapter_05（lesson_05.intent） | `catch { ... }` | `catch e { ... }` | parse_try_stmt mini_intent.py:1318 |
| README.md | `let mut` 演示 counter = counter + 1 等 | 保持（非错误） | — |

---

*规范版本 v1.2.0 · 2026-10-16 从实现提取 · 与 mini_intent.py @ c93cd68+ 对齐*
