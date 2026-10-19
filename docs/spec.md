# Intent 语言规范 v1.8.0

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

| 已实现 ✅ | let, def, return, if, else, elif, for, while, break, continue, match, requires, ensures, import, as, class, this, mut, fn, try, catch, finally, defer, assert, enum, yield, and, or, not, in, raise, spawn, scope |
|---|---|
| 字面量关键字 ✅ | true, false, null（None/True/False 同义接受） |
| 记录性注解 ✅ | pure（`func.is_pure`，仅记录不强制）, effect `[...]`（效果列表，仅记录） |
| 别名（兼容，推荐用主形式） | var, const ≡ let |
| 预留未实现 🔜 | func（用 def/fn）, is（用 ==）, invariant（契约扩展） |

> `from` 已在 EX1 启用：`raise <错误值> from <原因>`（非 import 的 from）。

**内置类型标识符**（非关键字，`Lexer.BUILTIN_TYPES` mini_intent.py:212）：`Int` `Float` `String` `Bool` `List` `Dict`

### 1.3 字面量

| 类型 | 形式 | 示例 |
|---|---|---|
| Int | 十进制数字 | `42` `-7` |
| Float | 带小数点或科学计数 | `3.14` `1e-3` |
| String | 双引号，支持 `\` 转义 | `"hello\n"` |
| f-string | `f"..."` 前缀（显式插值宣告） | `f"${name} 好"` |
| 插值字符串 | `${expr}` 内嵌求值 | `"${name} 得分 ${score}"` |
| 调试插值 | `${expr=}` 输出 `expr=值`（可叠规格 `${x=:.2f}`） | `"${x=}"` → `x=42` |
| 格式规格插值 | `${expr:spec}` 对齐 Python format()（fill/align/sign/宽度/精度/类型） | `"${pi:.2f}"` `"${n:05d}"` `"${s:*^7}"` |
| 嵌套引号 | 插值区内引号不终止字符串（括号深度 + 子串跟踪） | `"${d["k"]}"` |
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
| 箭头 | `->`（返回类型） `=>`（match 分支/λ） `<-`（CC2 通道发送/接收） |
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

标注是提示，不是枷锁：`intent check --types`（`--types`）做渐进类型静态检查——**标注处检查 + 推断处放过**（mypy-lite，L1）：

- 变量声明 `let x: T = expr`、调用实参 vs 形参标注、`return` vs 返回标注，三处可推断即检查；
- 推断不出类型的一律放过（显式信任，不猜）；
- 数值互通（§2.1）：Int/Float 双向接受；
- Union 标注任一成员合法；泛型参数视为 Any；类型别名透明解析；
- 容器只查基类（`List[Int]` 的元素类型不查，留待完整版）；
- 契约优先于类型：`requires/ensures` 是运行时可验证的主防线，类型是静态副防线。

正反例判定自测：`tools/typecheck_selftest.py`（21/21）。已知边界：`std/itertools2.intent` 的多行 `export` 语法不被 parser 接受（`--check` 同拒，宽松执行模式容忍）——类型检查以语法干净为前提。

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
- 装饰器（X1）：`@deco def f() {...}`（裸形态）/ `@deco(args) def f() {...}`（带参工厂，先求值 `deco(args)` 出真装饰器再应用）；应用顺序 = 声明顺序（自上而下），先应用者居内——末位装饰器最外（与 Python 的首位最外相反，测试锁定）；语句级（函数体内）`def` 的装饰器同样生效
- 生成器（S3）：函数体内 `yield expr;` 即为生成器函数——**调用即惰性**，返回 `<generator>`（函数体一行不跑，首个 `next()` 才启动）。协议（语义对齐 CPython）：
  - `next(g)` 拉一个值；耗尽返回 `None`（语言约定：无 StopIteration 通道）
  - `g.send(v)` 把 v 递送到 yield 表达式（`let x = yield v;` 的 x 即 v）；首个 send 必须为 None
  - `g.throw(e)` 在挂起点抛错：生成器内 catch 接得住，未捕获则异常在调用方 pull 点抛出
  - `g.close()` 关闭生成器：关闭信号是 BaseException 子类，业务 catch(Exception) 吞不掉（对齐 GeneratorExit）；break/return 提前退出 for 遍历时自动收摊
  - `for x in g` 真懒遍历（不预取，无限生成器可用）；裸 `yield` 产出 None
  - 实现：线程协作式协程（threadlet）——体跑独立线程，双队列握手；共享解释器状态在切换点按白名单保存/恢复（§6 限制表列边界）
- 生成器委派（P1.5）：`yield from expr;`——可迭代对象的元素逐个转发（List/Dict 键/生成器源；生成器源 send 值透传）
- 协程（A3a）：`async def f(...) {...}` + `await expr` + 内置 `run(coro)`——**调用即惰性**，返回 `<coroutine>`（体一行不跑）；`await` 求值出内层协程后挂起当前协程，`run` 以蹦床递归驱动内层、把结果送回避挂起点。`async`/`await` 均为**软关键字**（后随 `def` / 表达式起点时才取得关键字地位，作标识符不受影响）；支持类内 async 方法；async 函数无显式 `return` 时结果为 `None`（对齐 Python）。底层复用 S3 threadlet（协程线程 + 双队列），暂无事件循环与并发调度（A3b）
- 结构化类型（L2）：`protocol Name { def m(args) -> Ret; ... }` 声明方法名集合（`protocol` 为软关键字）；运行时 `implements(obj, proto)` 沿继承链查方法存在性（能力即身份，不要求声明关系）、`protocol_methods(proto)` 返回方法名清单；静态侧 `--types` 对标注为协议的位置做结构子类型检查（类方法集 ⊇ 协议方法集，继承链算数）

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

> `else if` 链 2026-10-18 落地：parser 将 `else` 后随的 `if` 解析为嵌套 IfStmt（与 `elif` 语义等价）——规范先立、实现补票（tests/test_control_flow.intent 回归）。

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

**属性访问缓存（M2 切片）**：实例属性读取经 `InstanceValue.get()`——缓存命中免 `fields`/方法表两级查找；`set()` 写透同步（无失效窗口，init 赋过的字段读即命中）；方法查找结果同样入缓存（类创建后方法表即稳定）。诊断内置：`cache_stats()` 返回 `[命中数, 未命中数]`（模块级聚合），`cache_reset()` 清零。实测（30000 次 `p.sum()` 端到端 A/B）：与缓存前 0.99x 持平——树遍历的解释器开销主导，缓存价值在方法查找路径与可观测性；隐藏类/调用点内联缓存/2x 微基准为后续迭代。统计为近似值（并发 spawn 下非原子）。

**dunder 协议全家（X3）**——实例定义即生效，分派点如下：

| 协议 | 触发 | 约定 |
|---|---|---|
| `__init__(args)` | `ClassName(args)` 实例化 | `init` 为兼容别名 |
| `__call__(args)` | `obj(args)` | 实例可调用；支持作用域变量与成员访问两条路径 |
| `__iter__()` | `for x in obj` | 返回 List（既有路径）或返回带 `__next__` 的迭代器 |
| `__next__()` | `next(obj)` / for 遍历 | 返回 `None` 表示耗尽（语言无 StopIteration 通道） |
| `__enter__()` | `with obj as name` | 返回值绑定 as 名；无则维持旧约定（绑定资源本身） |
| `__exit__(err)` | with 块退出 | 收退出时的错误值（无错传 `None`）；暂不承担抑制语义 |
| `__len__()` | `len(obj)` | 返回 Int |
| `__contains__(x)` | `x in obj` | 返回 Bool |
| `__eq__`/`__ne__`/`__lt__`/`__le__`/`__gt__`/`__ge__` | 比较运算符 | `!=` 未定义 `__ne__` 时回退 `__eq__` 取反 |
| `__add__`/`__sub__`/`__mul__`/`__div__`/`__mod__`/`__pow__`/`__floordiv__` | 算术运算符 | 右操作数优先时可定义 `__radd__` 等反射方法 |
| `__getitem__(k)` / `__setitem__(k, v)` | `obj[k]` / `obj[k] = v` | 下标协议 |
| `__hash__()` | 实例作 dict 键 | 返回 Int/String，以该值为键（`_dict_key` 归一） |
| `__str__()` / `__repr__()` | `print(obj)` / `repr(obj)` | `__str__` 优先，回落 `__repr__`，再无走结构渲染 |

### 3.7 管道与推导式

```intent
let result = data |> filter(valid) |> map(transform);   // |> 管道:从左到右
let squares = [x * x for x in nums if x > 2];           // 列表推导式
let m = {k: len(k) for k in pairs};                     // 字典推导式
```

### 3.7b 语法糖（S2a 切片）

**海象赋值 `:=`**（表达式级赋值，优先级最低——低于三元/管道/逻辑或/比较）：

```intent
let a = (n := 5);          // 求值 5 → 绑定 n → 返回 5
while ((v := produce()) <= 3) { push(log, v); }   // 条件里消费并暂存
```
- 左部必须是变量名（`(obj.x := 1)` 是语法错误，显式报错）；已存在则赋值，否则当前作用域声明
- 推导式内的海象绑在推导式作用域（随推导结束失效——与 Python 的泄露语义不同，已知边界）

**切片赋值**（读取早已支持，S2a 补写入侧）：

```intent
let mut l = [1, 2, 3, 4, 5];
l[1:3] = [20, 30];         // 等长替换
l[1:2] = [20, 21, 22];     // 增长
l[1:4] = [9];              // 收缩
l[:2] = [10, 11]; l[3:] = [40]; l[:] = [7];   // 省头/省尾/全切片
l[-2:] = [99];             // 负索引（Python slice 语义）
```
- 步长限 1（扩展切片 `l[::2] = ...` 显式 TypeError）；右侧限列表（替换语义，允许增删长度）
- 复合操作符（`l[1:2] += ...`）显式 RuntimeError；字符串目标显式 TypeError
- 剩余断点：星号解包 / 位置 only / match 类模式+守卫（后续轮次）

### 3.8 模块系统

```intent
import std.math;              // 标准库
import mylib;                 // 项目文件(搜索路径: 文件目录及其 std/ lib/ ./ ./std ./lib + ~/.intent/lib)
import mylib as ml;           // 别名
export my_func, my_const;     // 显式导出(P2.1): 无 export 声明的模块维持全量导出(兼容)
```

模块查找优先级：`<base>/<name>.intent` → `<base>/<name>/__init__.intent` → `<base>/<name>/<name>.intent`（npm 风格）。
模块 = 文件；循环导入检测（`_import_stack`）；每个模块独立执行，导入时注册其导出符号。

**扁平注入语义（已知边界，2026-10-19 记）**：`import std.bim.unit;` 把模块符号**扁平**注入当前作用域（`mm_to_m(...)` 裸调可用），同时挂载嵌套链 `std.bim.unit.mm_to_m(...)`；但中间名 `unit` **不是**独立符号——`unit.mm_to_m(...)` 报 NameError。历史模板（tools/dynamo_node.py BD1）曾踩此坑，BD2 期已修正。

### 3.9 包管理（P2.1 + PK1 依赖解析，V0.2 本地优先）

项目清单 `intent.toml`：

```toml
[project]
name = "myproj"
version = "0.1.0"

[deps]
mathkit = { path = "lib/mathkit", version = "^1.2" }   # 路径依赖 + 语义化约束
utils   = "../utils"                                   # 路径依赖(无约束)
web     = { git = "https://github.com/x/web.git", version = ">=2.0, <3.0" }
```

- `--install <url>`：安装单个依赖（git clone --depth 1 到 `./lib/<name>`）
- `--install <dir>`：`<dir>` 含 intent.toml → 按该项目批量解析安装（否则视为单个依赖源）
- `--install`（无参）：按当前目录 intent.toml 的 `[deps]` 批量安装
- `--install --dry-run [dir]`：**依赖解析预演**——约束合并/冲突检测/解析计划，不安装不写锁（PK1 判定入口）
- 启动时：`./lib` 与 `~/.intent/lib`（全局库）自动加入模块搜索路径

**PK1 依赖解析器**（`resolve_dependencies` mini_intent.py:8550）：

- 约束语法：`*`（任意）/ `^1.2`（兼容：≥1.2.0 <2.0.0）/ `~1.2`（补丁级：≥1.2.0 <1.3.0）/ `>=` `<=` `>` `<` `=` / 逗号分隔多段（AND 语义）；语义化版本三段式，缺段补 0，正式版高于预发布版
- 解析算法：BFS 走依赖图 → 约束累积（钻石依赖合并）→ 候选枚举（路径依赖单候选；本地注册表 `registry/` 多版本候选）→ **公共兼容集取最高版本**（最新不满足自动回退次高）→ 无解报 `依赖冲突`（退出码 1，不写锁）
- `intent.lock`（JSON）：锁定每包 version/source/deps/required_by；非 dry-run 安装前写入
- 刻意不做：全局 SAT 求解；git 依赖的 tag 枚举（未克隆无版本可读，install 后校验）

### 3.10 错误处理：raise 与异常链（EX1）

```intent
try {
    raise error("KeyError", "缺键 name") from inner_err;   // 显式因果链
} catch e {
    print(e.type);            // "KeyError" — 定向捕获
    print(e.__cause__.type);  // 起因类型(无 from 时为 None)
    print(e.message);         // 消息
    print(e.stack);           // Intent 调用链快照
};
```

- `error(type, message)` 内置：构造一等错误值（raise 的原料）
- `raise <错误值>`：ErrorValue 原样抛；`Err("boom")` 取内层消息；字符串简写 → `RuntimeError`；其余类型明确拒绝（TypeError）
- `raise X from Y`：`X.__cause__ = Y`——因果显式化，不猜
- 未捕获到顶层：渲染含「异常链(__cause__, 从起因到外层)」段（`render_intent_error`）
- 刻意不做：`__context__`（隐式上下文，异常处理中再抛新错的自动挂链）

### 3.11 结构化并发：spawn 与 scope（CC1）

```intent
let mut results = [];
def work(lo: Int, hi: Int) { ... push(results, partial_sum); };

scope {
    spawn work(0, 50);        // 派生任务(调用点求值)
    spawn work(50, 100);
};                            // 块退出 = 汇合点: 全部任务自动 join
// 此处两个任务必已完成
```

- `spawn <可调用>;` / `spawn f(args);`：Python threading 演示级实现；每个任务跑在独立 Interpreter 上，闭包作用域经 FunctionValue 共享
- `scope { ... }`：并发作用域——块内 spawn 的任务在块退出时统一 join；任务异常在 join 处重抛（第一个，不沉没）
- scope 外的 spawn 被拒绝（RuntimeError）——**没有孤儿线程**
- 词法作用域：scope 块是独立词法作用域（Resolver 同 try 块语义）
- 刻意不做：async/await（A3）、自由线程安全（A4）；channel 已由 CC2 交付（§3.12）

### 3.12 channel 通信（CC2）

```intent
let ch = chan();        // 无界缓冲; chan(n) = 容量 n(满则发送阻塞)
scope {
    spawn producer(ch); // 任务间经通道握手 — 不共享内存, 传递消息
    spawn consumer(ch);
};
ch <- 42;               // 发送: 阻塞直至入队; 通道已关闭则报错
let v = <- ch;          // 接收: 空则阻塞等待
close(ch);              // 关闭: 发送此后再报错; 接收排空剩余即止
```

- `ch <- v`（SendExpr）/ `<- ch`（RecvExpr）：与 Go channel 同形的词法（`<-` 是最优先级外的最低优先级运算符——`a<-b` 无空格即通道发送，比较请留空格）
- 线程安全由底层 `queue.Queue` 保证，不自己造锁；阻塞/关闭语义：缓冲满发送阻塞、空接收阻塞、关闭后排空再接收抛 `ChannelClosedError`（显式失败，不返回哑值）
- 通道是引用语义：传参/赋值共享同一通道（`copy()` 返回自身）
- 刻意不做：select 多路复用、带超时的 receive（A3 async 期再议）

### 3.13 测试框架深化（TQ1）

在 D1（`--test` + `test_*` 函数 + `assert`）之上的 pytest 子集等价物——无装饰器语法前的约法：

```intent
def setup() { ... };    // fixture 钩子: 每个用例前由运行器调用
def teardown() { ... };// fixture 钩子: 每个用例后调用(失败/skip 也清理)

def test_x() {
    let err = expect_error(fn() { items[99]; }, "IndexError");  // 预期异常
    skip("环境不具备");                                          // 诚实跳过
    param_cases([[1, 2], [3, 4]], fn(a, b) { ... });            // 参数化
    let m = mock("svc"); m(1);                                  // 测试替身
    assert mock_call_count(m) == 1, "调用被记录";
};
```

- `expect_error(fn, type)`：断言 fn() 抛出指定类型——返回捕获的 ErrorValue；未抛错或类型不符 → AssertionError（坏路径也是契约的一部分）
- `skip(reason)`：抛出 SkipTest，运行器计为「跳过」——既非通过也非失败，摘要单独计数（`9/10 通过, 0 失败, 1 跳过`）
- `param_cases(cases, fn)`：cases 是用例列表，每项展开传给 fn；失败带用例序号（定位到个案）
- `mock(name)` / `mock_return(m, v)` / `mock_calls(m)` / `mock_call_count(m)`：记录调用序列的测试替身，可直接调用 `m(args)`
- setup/teardown 是文件级约定（与 test_* 同文件定义），运行器负责环绕；teardown 自身失败即用例失败

### 3.14 帧快照与事后调试（EX2）

```intent
python src/mini_intent.py --postmortem tests/_demo_error_stack.intent
```

- 异常穿帧时，每层 `execute_function`/`_execute_method` 把本帧局部变量快照挂上异常（`_intent_frames`，从外到内）——帧快照取自建帧时挂在 `CallFrame.scope` 上的本帧作用域，各帧各的本地人
- `--postmortem`：渲染完整诊断（D3）→ 帧快照写盘 `.intent_postmortem.json`（停机后可捡回）→ 帧检视 + 命令循环（`frames` / `frame N` / `vars` / `where` / `quit`）；默认停在出错帧（最内层）
- 非交互（stdin EOF）自动收尾，退出码 0——postmortem 的职责是接住崩溃，不是复制失败
- 与 C7 `--debug` 的分工：debugger 事前（打断点逐步走），postmortem 事后（栈已冻结，只检视不执行）

### 3.15 C ABI FFI（I1 最小切片，ctypes 背载）

```intent
let lib = ffi_load("msvcrt");                          // 加载 .dll/.so
let strlen = ffi_func(lib, "strlen", "Int", ["Str"]);  // 声明外部函数
print(strlen("hello"));                                // 5

let pt = ffi_struct(["x", "y"], ["Int", "Int"]);       // 结构体(平铺标量)
ffi_field_set(pt, "x", 42);
let user32 = ffi_load("user32");
let get_cursor = ffi_func(user32, "GetCursorPos", "Int", ["Struct"]);
get_cursor(pt);                                        // 结构体按引用传(出参)
print(ffi_field_get(pt, "x"));
```

- 类型名白名单：`Int`(c_int) / `Float`(c_double) / `Str`(c_char_p, utf-8) / `Bool`(c_int) / `Ptr`(c_void_p) / `Struct`(指针语义) / `Void`(仅返回)；声明期校验，未知类型名抛 ValueError
- `Struct` 形参 = 指向结构体的指针（Win32 出参/入参指针模式）——**未声明 argtypes 的 ctypes 函数对 Structure 实例按值传递，必须显式 byref**（实测 GetCursorPos：传实例 ret=0，byref ret=1）
- 符号不存在 / 库加载失败 / 实参个数或类型不符 → RuntimeError/TypeError，显式失败不返回哑值
- 架构立场：寄生期复用宿主 CPython 的 ctypes，不自己造 ABI 桥（ROADMAP §0.1）
- **完整 I1 剩余**（20 人日中的未做部分）：回调（CFUNCTYPE）、数组/联合、varargs、头文件解析、`foreign` 语法糖——最小切片已交付并通过 8 项测试（tests/test_ffi.intent，Windows 真实 API msvcrt/user32）

### 3.16 Python 互操作桥（I2a 最小切片，寄生期标志）

```intent
import python.math;                 // 加载真 Python 模块
print(math.sqrt(16.0));             // 4.0 — 命名空间成员调用
print(python.math.floor(3.7));      // 3  — 全链亦可
let text = json.dumps({"a": 1});    // import python.json 后
```

- **命名空间挂载**：`import python.X` 经 importlib 加载真模块，符号包成桥值挂到 `X`（末段名独立可用）；**不平扁注入**——防遮蔽核心内置（与 std import 扁平注入的边界偏差是刻意设计，见 §3.8）
- 双向编排：标量/列表/字典/None 自动转换；富对象（类实例等）包成不透明 `PyObjectValue` 句柄（可传回 Python，不可在 Intent 侧探内部）
- 异常策略：Python 侧任何异常 → RuntimeError（带原类型名）——显式失败，不静默 None
- 架构立场：I2 是路线图 ROI 最高的单个任务（ROADMAP §0.1）；寄生期解决生态从零
- **完整 I2a 剩余**（15 人日中的未做部分）：类实例化、关键字参数、Python 回调 Intent、子模块链、pip 三方包 round-trip（requests/numpy）

---

## 4. 标准库

### 4.1 内置函数（166，`_setup_builtins` mini_intent.py:4305）

| 类别 | 函数（签名） |
|---|---|
| 输出断言 | `print(...)` `assert(cond, msg)` |
| 集合 | `len(x)` `keys(d)` `values(d)` `push(l, v)` `pop(l)` `insert(l, i, v)` `remove_at(l, i)` `enumerate(l)` `zip(a, b)` `range(...)` `reversed(x)` `sorted(x)` `any(l)` `all(l)` `contains(x, v)` |
| 协议（X3） | `next(it)`（迭代器下一元素，耗尽返回 `None`） `repr(x)`（调试表示，实例走 `__repr__`） `run(coro)`（A3a 驱动协程至完成，返回其返回值） `implements(obj, proto)`（L2 结构化符合性，能力即身份） `protocol_methods(proto)`（L2 方法名清单） |
| 缓存诊断（M2） | `cache_stats()`（`[命中, 未命中]`） `cache_reset()`（清零，微基准/测试的确定性起点） |
| 反射（X2） | `getattr(obj, name)` `setattr(obj, name, v)` `hasattr(obj, name)` `dir(obj)`（字段+方法含继承链，排序） `callable(x)`（函数/类/FFI/桥/mock/有 `__call__` 的实例） |
| 类型转换 | `int(x)` `float(x)` `str(x)` `bool(x)` `type_of(x)` `type(x)` |
| 格式化（S2b） | `format(v, spec)`（格式规格对齐 Python：fill/align/sign/0宽度/千分位/精度/类型；花括号拒收；容器/None 先 str 化再套字符串规格） |
| 数学 | `abs(x)` `min(...)` `max(...)` `sum(l)` `sqrt(x)` `pow(a, b)` `floor/ceil/round(x)` `log/exp/cos/sin/tan/acos/asin/atan(x)` `atan2(a, b)` `pi` `random()` `randint(a, b)` |
| 字符串 | `split(s, sep)` `join(l, sep)` `trim(s)` `ord(c)` `chr(n)` `starts_with/ends_with(s, p)` `replace(s, a, b)` `to_upper/to_lower(s)` `substr(s, start, end)` |
| Result | `ok(v)` `err(e)` `error(type, message)`（构造一等错误值，EX1） |
| 文件 | `read_file(p)` `write_file(p, c)` `list_dir(p)` `file_exists(p)` `is_dir/is_file(p)` `make_dir(p)` `delete_file(p)` `file_size(p)` `file_modified(p)` |
| 系统 | `env(k)` `cwd()` `ch_dir(p)` `shell(cmd)` `platform()` `path_join/basename/dirname/ext(p)` `now()` `sleep(ms)` `input(prompt)` `version()` `args()` |
| 序列化 | `json_parse(s)` `json_dump(v)` |
| HTTP（B6） | `http_get(url)` `http_post(url, body)` `http_get_json(url)` `http_post_json(url, v)` `http_serve_start(port)` `http_serve_stop(port)`（本地测试服务器，不依赖外网） |
| SQLite（B7） | `sqlite_open(path)` `sqlite_exec(h, sql)` `sqlite_query(h, sql)` `sqlite_close(h)`（句柄式；查询返回行字典列表） |
| 正则（B8） | `re_test(p, t)` `re_full_match(p, t)` `re_find_all(p, t)` `re_groups(p, t)` `re_replace(p, r, t)` `re_split(p, t)`（非法模式抛 ValueError） |
| 日期时间（B4） | `datetime_now()` `datetime_today()` `datetime_parse(iso)` `datetime_format(iso, fmt)` `datetime_add_days/hours(iso, n)` `datetime_diff_days/seconds(a, b)` `datetime_weekday(iso)` `datetime_parts(iso)` `datetime_timestamp(iso)` `datetime_from_timestamp(ts)` `datetime_to_timezone(iso, off)`（ISO 字符串表示；非法输入抛 ValueError） |
| 压缩编码（B9） | `enc_base64_encode(s)` `enc_base64_decode(s)` `enc_gzip_compress(s)` `enc_gzip_decompress(s)` `enc_urlencode(s)` `enc_urldecode(s)`（gzip 二进制以 base64 文本承载；非法输入抛 ValueError） |
| 文件通配（SL1） | `glob_match(pattern)`（Python glob 语义，空表=无匹配） |
| 高级文件（SL1） | `shutil_copy_file(src, dst)` `shutil_move(src, dst)` `shutil_rmtree(path)`（失败抛 RuntimeError） |
| 临时文件（SL1） | `tempfile_mkdtemp()` `tempfile_mkstemp(prefix)` `tempfile_tempdir()` |
| UUID（SL1） | `uuid_uuid4()` `uuid_uuid4_hex()` |
| 摘要（SL1） | `hash_md5/sha1/sha256/sha512(text)`（UTF-8 输入，十六进制摘要） |
| 消息认证（SL1） | `hmac_sha256(key, msg)` `hmac_sha256_verify(key, msg, sig)`（常量时间比对） |
| 安全随机（SL1） | `secrets_token_hex(n)` `secrets_rand_below(n)` `secrets_choice(lst)`（CSPRNG；空表选择抛 ValueError） |
| 十进制（SL1） | `decimal_add/sub/mul/div(a, b)` `decimal_compare(a, b)`（字符串承载，28 位精度；非法数字抛 ValueError，除零抛 ZeroDivisionError） |
| 内存观测（MM1） | `mem_live_count()` `mem_alloc_total()` `mem_stats_info()` `gc_collect_now()` `ref_count_of(obj)`（设计文档 docs/memory_design.md） |
| 通道（CC2） | `chan()` `chan(n)`（创建无界/容量 n 通道） `close(ch)`（关闭：发送报错、接收排空即止） |
| 测试框架（TQ1） | `skip(reason)` `expect_error(fn, type)` `param_cases(cases, fn)` `mock(name)` `mock_return(m, v)` `mock_calls(m)` `mock_call_count(m)` |
| FFI（I1 最小切片） | `ffi_load(path)` `ffi_func(lib, name, restype, argtypes)` `ffi_struct(names, types)` `ffi_field_get(s, name)` `ffi_field_set(s, name, v)` `ffi_sizeof(s)`（ctypes 背载；类型名白名单 Int/Float/Str/Bool/Ptr/Struct + Void；见 §3.15） |

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
| `http` | get, post, get_json, post_json, serve_start, serve_stop |
| `sqlite` | open, exec, query, close |
| `re` | test, full_match, find_all, groups, replace, split |
| `datetime` | now, today, parse, format, add_days, add_hours, diff_days, diff_seconds, weekday, parts, timestamp, from_timestamp, to_timezone |
| `encoding` | base64_encode, base64_decode, gzip_compress, gzip_decompress, urlencode, urldecode（gzip 二进制以 base64 文本承载；非法输入抛 ValueError） |
| `itertools2`（SL2） | permutations, combinations, product, heappush, heappop, bisect_left, bisect_right, insort, class MinHeap, class Deque, class DefaultDict, class ChainMap（纯 Intent；heap/bisect 为有序插入/线性定位的演示级实现，语义与 Python 一致） |
| `glob`（SL1） | glob（通配符匹配） |
| `shutil`（SL1） | copy_file, move, rmtree |
| `tempfile`（SL1） | mkdtemp, mkstemp, tempdir |
| `uuid`（SL1） | uuid4, uuid4_hex |
| `hashlib`（SL1） | md5, sha1, sha256, sha512（md5/sha1 仅校验和与兼容用途） |
| `hmac`（SL1） | sha256, sha256_verify |
| `secrets`（SL1） | token_hex, rand_below, choice（密码学安全随机） |
| `decimal`（SL1） | add, sub, mul, div, compare（字符串承载的精确十进制） |
| `statistics`（SL1） | mean, median, variance, stdev（纯 Intent；总体方差，契约封门） |
| `textwrap`（SL1） | wrap, fill, indent, shorten（纯 Intent；换行走 chr(10)） |
| `csv`（SL1） | parse_line, serialize_row, parse（RFC 4180 子集；引号走 chr(34)） |
| `argparse`（SL1） | parse, get（--key value 对 + 裸 --flag 置真；演示级） |
| `pathlib`（SL1） | name, stem, suffix, parent, join_path, with_suffix（纯 Intent；不叫 join——避让核心内置） |
| `memory`（MM1） | mem_live, alloc_total, mem_stats, gc_collect, ref_count（寄生策略：弱引用注册表 + 宿主分代 GC；docs/memory_design.md） |
| `functools`（X1） | compose(f, g)（右先生效的组合）/ memoize(f)（单参记忆化，无淘汰子集）/ lru_cache(f, cap)（真 LRU：命中刷新访问序，满容淘汰最久未访问；cap<1 显式抛 ValueError；Intent 字典无 delete，刷新与淘汰靠重建字典） |
| `bim/*` | unit(单位换算) / geometry(Vector3D 等) / transform(矩阵) / solid / polygon / pipe / pipe_fittings / pipe_routing(A* 3D 寻路) / **cbwd**(BD4：洞口合并——连通分量+空间哈希预筛，与 CBWD 参考逐例一致) |

字典方法（P3.1）：`d.has_key(k)` / `d.keys()` / `d.values()`；dict 键统一为 Python 标量形态（`DictValue._norm_key`），int/float/str/bool 键均可，`{1: "a"}` 与 `squares[3]` 自然工作。

### 4.3 字节码编译器与栈式 VM（V0.3）

`src/intent_bytecode.py`：AST → 字节码 → 栈式 VM。

**原生字节码覆盖**：let/let mut、算术与比较、not、print、if/else、while、break/continue、函数定义与调用（含递归）、return、**闭包**（MAKE_CLOSURE 捕获定义时环境，Env 链实现词法作用域）、**管道**（编译期 desugar 为嵌套调用）、**Result ? 传播**（UNWRAP_OK：Err 跳函数末尾 RET 提前返回）、**契约检查**（requires 进门验收 / ensures 经 return 重写验收，违约抛 ContractViolation）。函数体末条为表达式时其值即返回值（与解释器隐式返回一致）。

**委托通道（RUN_AST）**：match / 类与对象 / with / 方法调用 / for / try / 生成器 / 装饰器 / 泛型 / 默认参数等重特性——AST 节点原样交给树遍历解释器执行，与 VM 共享同一环境（VMScope 适配器：`symbols` 与 `Env.vars` 为同一 dict，双向可见）。VMScope 是 Scope 的真子类，VM 启动时将解释器 `global_scope` 桥接为 VM 全局环境——嵌套 import 沿作用域链找到 VM 里的正版模块树。对象运算符重载（`__add__`/`__eq__`…）经 `_binary_op` 委托，零重复实现。任何未原生覆盖的节点都走委托通道——**任意 Intent 程序可编译**。

**架构**：Emitter（回填跳转/委托上下文）→ VM（值栈 + 帧栈 + 环境链）；VMClosure 是 FunctionValue 子类——解释器侧调用分发零改动。委托块内的 return 经 `_VMReturn` 信号回传 VM 调用链；break/continue 经流控标志回传原生循环。

**V0.3 性能（T7）**：主循环热指令全内联——`stack/push/pop/frames/env/code/ip` 驻留局部变量；LOAD_VAR/STORE_VAR/ASSIGN_VAR 直接走环境链；双侧 IntValue 的算术/比较走快路径（bool 不是 IntValue 子类，`type() is` 精确匹配不误吞）；argc≤1 的闭包调用免列表构造。委托点前同步 `self.env`，慢路径仍走原方法。基准：fib(25) VM ≈788ms vs 解释器 ≈3415ms ≈ **4.3x**（`tests/perf_check.intent`，`Time:` 计时行走 vm_diff 归一化）。

**已知边界**：委托块外的 break/continue 宽松忽略；VM 错误抛原生异常（无 P0.1 诊断渲染）；程序级「返回值」 CLI 摘要行两侧暂不一致。

输出约定：编译元信息走 stderr，程序输出走 stdout——`--compile --run-vm` 的 stdout 与解释器 stdout 可直接 diff 对照。
差分测试工具：`python tools/vm_diff.py`（默认跑 examples/ + tests/test_*，逐位归一化比对，退出码 1 表示有语义分歧）。
注：`src/mini_intent.py` 作为 `__main__` 运行时会把自身注册进 `sys.modules['mini_intent']`——辅助模块 `from mini_intent import ...` 才不会重新加载出第二套类定义。

### 4.4 内存管理（MM1，寄生策略）

容器值（List/Dict/Instance）在 `__init__` 即登记进模块级 `_ObjectRegistry`（弱引用表，不拉长寿命）。
循环垃圾委托宿主 CPython 分代 GC；`gc_collect_now()` = 快照 → `gc.collect()` → 快照，差值即回收容器数。
语义：`mem_live()` 存活容器数；`alloc_total()` 累计创建（单调增）；`mem_stats()` 含 by_type 分布；
`ref_count(obj)` 为宿主观测值（含解释器内部引用，只做诊断）。
设计文档：`docs/memory_design.md`（含 M2/M3 演进与四条已知限制）。
已知限制：`ListValue.copy()` 不处理环——自引用列表作为 Intent 函数实参会无限递归（形参复制传值语义，M2 期修）。

---

## 5. CLI

```
python src/mini_intent.py <file>           # 执行
python src/mini_intent.py <file> [args...] # 执行, 额外参数经 args() 读取
python src/mini_intent.py -c "code"        # 直接执行代码串
python src/mini_intent.py --check [file]   # 只解析不执行: 干净退出0, 错误退出2
python src/mini_intent.py --types [file]   # L1: 渐进类型静态检查(mypy-lite: 标注处检查+推断处放过)
python src/mini_intent.py --types --show-inferred file.intent  # L3a: 打印无标注变量的推断结果
python src/mini_intent.py --compile file.intent [--run-vm]  # M10: 编译字节码(可选 VM 执行)
python src/mini_intent.py --emit tokens|ast <file>   # 分析结果写文件
python src/mini_intent.py --test [path]    # 测试(默认 tests/, _ 开头跳过)
python src/mini_intent.py --lint file.intent         # 静态检查(let 重赋值/空 catch/无契约/未用 import)
python src/mini_intent.py --doc file.intent          # 生成 markdown 模块文档
python src/mini_intent.py --fmt file.intent         # 格式化, 输出到 stdout(重定向即写回)
python src/mini_intent.py --install [url|dir]  # 安装依赖(url 单个; dir 含 intent.toml 按项目批量; 无参按当前目录批量)
python src/mini_intent.py --install --dry-run [dir]  # PK1: 依赖解析预演(约束合并/冲突检测, 不安装)
python src/mini_intent.py --debug file.intent  # C7+EX4: 调试模式(条件断点 break N if EXPR / watch / 单步 / 调用栈)
python tools/csdk/selftest.py  # I3a: C 扩展 SDK 端到端自检(ABI v1: 加载→注册→Intent 调用)
python src/mini_intent.py --postmortem file.intent  # EX2: 事后调试(帧快照存档 + 崩溃后进场检视)
python src/mini_intent.py --profile file.intent  # M4: 函数级剖析(调用次数/累计/自身时间, cProfile 等价切片)
python src/mini_intent.py --mem-profile file.intent  # M4: 内存分配热点(MM1 注册表按类型分配计数)
python src/mini_intent.py --coverage file.intent  # E3: 语句覆盖率(执行打点 + AST 分母)
python src/mini_intent.py --coverage --contracts file.intent  # Q2: 叠加契约覆盖率(requires/ensures 子句级)
python benchmarks/run_benchmarks.py [filter] [--update]  # Q4: 基准套件(每基准3次取最小; --update 重写基线; 超+20%判回退)
python tools/venv.py create|install|list|activate  # PK2: 虚拟环境(.venv 隔离 + 全局缓存 + PATH)
python tools/registry.py publish|list|install [--registry-url URL] [--sign-key KEY]  # P3: 本地/HTTP 注册表 + Ed25519 签名
python tools/registry.py serve [--port P]   # P3a: HTTP 注册表服务(GET /index.json、GET /pkg/<n>/<v>/<f>、POST /publish)
python tools/registry.py keygen [--out DIR]  # P3b: 生成 sk.key / pk.pub(base64)
python tools/intent_sign.py --selftest      # P3b: Ed25519 RFC 8032 向量自检
python tools/pack.py build|inspect|install  # P4: .intentp 包格式(zip+metadata) + console_scripts 入口(bin/)
python src/mini_intent.py --version        # 版本
python src/mini_intent.py -t / -a          # 只看 tokens / AST
python src/mini_intent.py -r               # REPL
python src/mini_intent.py -d               # 演示
python src/mini_intent.py -p               # 哲学视角翻译
```

退出码：0 成功 ｜ 1 运行时/测试失败/类型错误（`--types`）｜ 2 用法/语法错误（`--check`/`--types`）。
banner 与 pyreadline 提示只在 TTY 显示（`--fmt > file` 等管道场景输出纯净）。
⚠️ 文件模式当前为**宽松执行**（语法错误警告后继续，退出码 0）——测试模式与 `--check` 严格。CI 请用 `--check` + `--test`。

---

## 6. 已知限制（诚实清单）

| # | 限制 | 状态 |
|---|------|------|
| 1 | 执行引擎 | 双轨：树遍历解释器 + 字节码 VM（V0.3，fib25 ≈4.3x）；无 JIT |
| 2 | 并发（async/channel） | 🔜 部分实现（2026-10-18 CC1：spawn + scope 结构化并发，Python threading 演示级；CC2：channel 通信原语 `ch <- v` / `<- ch` / close；async/await（A3）排队） |
| 3 | 包管理（intent.toml/注册表）缺失，import 仅文件级 | ✅ 已实现（2026-10-16：intent.toml + --install + lib 搜索路径；2026-10-18：本地目录注册表 publish/list/install；PK1 依赖解析器 semver 约束 + 冲突解决 + intent.lock，--dry-run 预演） |
| 4 | 位运算、复合赋值、`:=`/`++`/`--` 词法接受但语义未实现 | 预留 |
| 5 | match range 模式、类型别名/Union 未实现 | ~~路线图 P1.3~~ ✅ 已实现（2026-10-16，match range 仍未实现） |
| 6 | 静态类型检查缺失（Resolver 只做作用域分析） | ✅ 已实现（2026-10-18 L1：`--types` 渐进类型检查——标注处检查 + 推断处放过，mypy-lite 最小切片；容器元素类型/全量推断留待完整版） |
| 7 | f-string/多行字符串：插值 `${}` 已支持；`f"..."` 前缀与 `"""` 三引号未实现 | ✅ 已实现（2026-10-16；2026-10-19 S2b 完整化：`${x=}` 调试格式 / 嵌套引号 / `${x:spec}` 格式规格，见 §2 字符串表） |
| 8 | formatter/linter/LSP 缺失 | formatter ✅ linter ✅ doc ✅ 已实现（2026-10-16）；LSP ✅ 已实现（2026-10-18，tools/lsp/） |
| 9 | with 语句 | ✅ 已实现（2026-10-16） |
| 10 | yield from / 泛型约束 | ✅ 已实现（2026-10-16；2026-10-19 S3：生成器真惰性完整化——send/throw/close/yield 表达式/for 懒遍历，见 §3.2） |
| 11 | `//` 是行注释——整除运算符在源码中不可达（`5 // 0` 被词法吞为注释） | 已知语言限制（用 `/` 真除法；修法需词法上下文歧义消解，排队） |
| 12 | `str(inf)` 抛 OverflowError（1e308*10 → inf 时）；字典缺键抛 RuntimeError（KeyError 转译）；`len(None)` 抛 AttributeError | 行为快照，均可被 catch 捕获（见 tests/test_fuzz.intent） |
| 13 | 内置无方法式调用：`lst.push(x)` 不被支持，须写自由函数 `push(lst, x)`（成员访问不回退内置） | 语法选择（类方法才行）； |
| 14 | `ListValue.copy()` 不处理环：自引用列表作 Intent 函数实参 → 无限递归（形参复制传值） | M2 期修（copy 带 memo 表）；诊断路径直调内置绕行 |
| 15 | `import std.X` 将模块全部符号注入当前作用域，可能遮蔽核心内置（如 pathlib.join 曾遮蔽 join） | 命名避让（join_path）；根治需改 import 语义，排队 |
| 16 | `and`/`or` 原为两侧 eager 求值（`i < len(l) and l[i] < x` 边界越界） | ✅ 已修复（2026-10-18：短路求值，返回类型保持 BoolValue；VM 经委托通道同受益） |
| 17 | `import std.X` 扁平注入符号，但中间名（如 `unit`）不是独立符号，`unit.mm_to_m(...)` 报 NameError | 已知边界（2026-10-19 BD2 期实证）；用裸名 `mm_to_m(...)` 或全链 `std.bim.unit.mm_to_m(...)`；BD1 模板已修正 |
| 18 | FFI 仅最小切片：无回调/数组/联合/varargs/头文件解析/`foreign` 语法糖 | I1 剩余部分（20 人日中的未做部分，ROADMAP 维度 8 已注断点） |
| 19 | `run_source` 对容器返回 RuntimeValue 树（ListValue.value 内为 IntValue 等），非原生类型 | 桥侧已脱壳（tools/revit_bridge.py `_to_native`）；宿主接入时需自行转换 |
| 20 | Python 桥（I2a）无关键字参数/类实例化/回调 | 最小切片边界（spec §3.16）；完整版随 I2a 剩余部分 |
| 21 | 装饰器在提升期应用，早于顶层 import/let — 模块导入的装饰器（`@memoize` from std.functools）或引用顶层变量的装饰器参数找不到 | X1 已知边界（2026-10-19 实证）；**带参装饰器 / 零参调用形态 / 语句级（函数体内）装饰器已于 v2.12.0 支持**（语句级执行时机在 import/let 之后，不受此限）；本文件定义的装饰器可用；根治随「def 即语句执行」改造（X1 断点） |
| 22 | 契约税实测 55%（`benchmarks/contracts.intent`：trivial 函数 10 万次调用，guarded 2602ms vs plain 1623ms） | 2026-10-19 Q4 实测记录；契约是灵魂不砍，优化方向：验证器子句缓存/短路（重函数上摊薄） |
| 23 | 生成器仅解释器支持；字节码 VM 无生成器路径（VM 差分纪律：VM 不跑含 yield 的文件） | S3 已知边界（2026-10-19）；VM 生成器化随字节码协程支持排队 |
| 24 | 协程线程内 profiler 打点关闭（帧栈纪律与协程切换冲突）；覆盖率打点保留（计数型无栈纪律） | S3 已知边界（2026-10-19）；--profile 不含生成器内部帧 |
| 25 | 生成器异常在调用方 `next()/send()/throw()` 处抛出的栈快照为「生成器创建链 + 生成器帧」，不含 pull 点的调用链 | S3 已知边界（2026-10-19）；与 Python「生成器帧单独显示」同向 |
| 26 | 生成器线程阻塞在无界操作（如 channel 接收）时，`close()` 有界返回（2s），留 daemon 线程 | S3 已知边界（2026-10-19）；不无限等，也不强杀 |
| 27 | async 生成器（async 函数内 yield）显式拒绝；协程无事件循环/并发调度（`await` 按顺序串行驱动）；`await` 软关键字在「标识符 await 后随表达式」的写法上会被当作 await 表达式 | A3a 已知边界（2026-10-19）；async 生成器与事件循环/IO 多路复用归 A3b 及后续 |
| 28 | 包签名为自持 Ed25519（RFC 8032 最小参考实现，selftest 用标准向量自证）：工具级，不做侧信道防护；密钥/签名格式为 base64 文本，**不与 minisign 二进制互操作**；签名覆盖「文件清单摘要」（relpath+内容 sha256），不覆盖 zip 时间戳等元数据 | P3b 已知边界（2026-10-19）；对 minisign 格式互操作按需再加适配层 |
| 29 | `.intentp` 入口点只支持「脚本文件」级（`[scripts] cmd = "x.intent"`），`模块:函数` 级入口未做；`.bat` 启动器按系统 ANSI 编码写（cmd.exe 代码页限制），解释器路径嵌入为安装时的 `sys.executable` | P4 已知边界（2026-10-19）；`:func` 入口与跨机可迁移启动器（路径重定位）留后续 |
| 30 | C 扩展 SDK（ABI v1）只支持 `long long` 整数、元数 1-2；浮点/字符串/结构体/回调映射未做。GC 钩子 = 原生模块弱引用生命周期登记（加载登记/卸载注销，`live_native_modules` 可观测），不是让 C 代码持有/释放 Intent 值的对象模型。本机无 C 编译器——`selftest.py` 自动检测：有编译器则编译 example.c 验真 DLL，无则用 ctypes 回调表验证同一 ABI（输出明示"C 编译路径未验证"） | I3a/I3b 已知边界（2026-10-19）；ABI 与 GC 钩子已端到端验证，编译产物待有编译器的机器复验 |
| 31 | 调试器增强（EX4）未做远程调试；非 TTY stdin 时命令循环直接放行（不读命令）；条件表达式求值失败按无条件命中处理（显式打印原因） | EX4 已知边界（2026-10-19）；远程调试（socket 附加）留后续 |
| 32 | 结构化类型（L2）只比方法名，不比参数/返回签名；嵌套 protocol（protocol 内嵌 protocol）不查；运行时鸭子类型缺方法在**调用时**才炸（NameError），`implements` 只是显式检查口 | L2 已知边界（2026-10-19）；签名一致性与递归结构留完整版 |
| 33 | 局部推断（L3a）覆盖：字面量 / 变量 / 一元 / 二元（数值提升）/ 三元与 if 表达式（分支统一）/ 管道（取目标函数返回标注）/ 类构造（类名）/ 容器字面量（基类）；**不推**：成员访问、下标、闭包返回值、函数体内的跨函数调用链；返回类型推断属 L3b | L3a 已知边界（2026-10-19）；推断结果可用 `--show-inferred` 观测，`tools/infer_selftest.py` 锁定 |

---

## 7. 文档勘误记录（本版修正）

| 位置 | 原文 | 修正 | 依据 |
|---|---|---|---|
| philosophy_mapper.md | `class B : A { ... }` | `class B < A { ... }` | Parser mini_intent.py:1006 |
| philosophy_mapper.md | `90..100 => "A"` | match range 未实现，用 `n if n >= 90 => "A"` | `_parse_pattern` 无 range 分支 |
| chapter_05（lesson_05.intent） | `catch { ... }` | `catch e { ... }` | parse_try_stmt mini_intent.py:1318 |
| README.md | `let mut` 演示 counter = counter + 1 等 | 保持（非错误） | — |

---

*规范版本 v1.25.0 · 2026-10-19 从实现提取 · 与 mini_intent.py 工作区对齐（v2.26.0：L3a 局部推断——§5 `--show-inferred`、§6 限制 33；此前 v2.25.0 L2 结构化类型）*
