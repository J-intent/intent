# 更新日志

本项目的重大变更记录。版本遵循语义化版本。

---

## v2.11.0 — X1 装饰器最小切片：functools 系 + 顶层函数一等值修复（2026-10-19）

> 装饰器的骨架早已在库里睡灰：parser 收名字、解释器应用 dec_func(fv)——
> 缺的只是 functools 家族，和一个「函数能当值传」的根因修复。
> 版本 2.10.0 → 2.11.0。

**X1 装饰器最小切片**（tests/test_decorator.intent 6 测试，全过）

- 机制基线（既有，本轮实证锁定）：`@deco` 语法 + execute_program 应用 `deco(fn)` + 装饰器栈自外向内
- 新模块 std/functools.intent：`compose(f, g)`（右先生效）/ `memoize(f)`（单参记忆化，闭包捕获 cache，无淘汰子集）——纯 Intent 零内置依赖
- **根因修复**：顶层普通函数只进 `self.functions` 表（可按名调用）不进作用域——函数作实参传递时 `未定义的变量`。execute_program 顶层函数一律 declare 入全局作用域（函数是一等值）
- 测试锁定：裸装饰/副作用记账/双层栈/memoize 缓存命中证据（同参三次内层只算一次）/compose 右先生效/@traced_cache 递归记忆化
- **VM 一致性修复**：装饰器应用逻辑下沉 `_apply_decorators`，execute_program 提升期与 execute_statement FunctionDef 分支（VM 委托通道）共用——修复 VM 路径装饰器不应用导致的双引擎分歧（vm_diff DIVERGE 1 → 0）
- 完整 X1 剩余（已 note 断点）：带参装饰器 `@deco(1,2)`（parser 只存名字）、函数体内的装饰器不应用、模块导入装饰器的提升期时序问题（import 早于提升期应用——需「def 即语句执行」改造）、wraps（需函数元数据内省）、partial（需 *args）、lru 淘汰策略

**质量门**：--test 235/236 过 0 败 1 跳（229→235，+6）；vm_diff 69/69 一致（含 test_decorator 双引擎对照）；spec v1.11.0（§4.2 functools、§6 限制 21）。

---

## v2.10.0 — Phase 6 二批：Python 桥最小切片 + CBWD 洞口合并移植（2026-10-19）

> 寄生期皇冠落地第一块：`import python.math` 跑通真 Python 生态。
> CBWD 的合并逻辑搬进 Intent——不是抄代码，是算法逐例对齐后才签收。
> 版本 2.9.0 → 2.10.0。

**I2a Python 互操作桥最小切片**（tests/test_pybridge.intent 6 测试，全过）

- `import python.X` 经 importlib 加载真 Python 模块；符号包成桥值**命名空间挂载**（`math.sqrt` 可用，全链 `python.math.sqrt` 亦可用）——刻意不平扁注入，防遮蔽核心内置（与 std import 的边界偏差见 spec §3.8）
- 双向编排：标量/列表/字典/None 自动转换；富对象包不透明 PyObjectValue 句柄（可传回 Python，Intent 侧不探内部）
- 新值类型 PyFuncValue（可调用，走 CallExpr callable 分发）/ PyObjectValue；MemberAccess 调用路径补 callable 分发（原先只认 FunctionValue/ClassValue，桥函数会撞「无法调用」）
- 异常策略：Python 侧异常 → RuntimeError 带原类型名，显式失败不静默
- 测试：math 函数/常量/全链、json round-trip、statistics.mean、Python 异常显式化
- 完整 I2a 剩余（15 人日中的未做部分）：类实例化/关键字参数/Python 回调 Intent/子模块链/pip 三方包 round-trip

**BD4 CBWD 移植最小切片：洞口合并**（std/bim/cbwd.intent + tests/test_bim_cbwd.intent 8 测试，全过）

- 移植源：D:\Desktop\CBWD\COM.py 的纯算法内核——bbox_3d_gap_mm / can_merge_openings / find_merge_groups（连通分量 + 空间哈希预筛）；剥掉 Revit/WinForms 依赖，单位统一 mm（COM.py 原 ft 几何在边界换算，算法内无 304.8 魔法数）
- 函数：bbox_gap_mm / can_merge（含圆柱表面间隙精修）/ find_merge_groups（预筛路径）/ find_merge_groups_slow（O(n²) 兜底）/ groups_signature
- 对照基准 tools/cbwd_reference.py：COM.py 算法的 Python 参考提取 + `--parity` 同输入同签名对齐（24 洞口合成数据 × 3 距离 × 双路径 = 6/6）+ `--selftest` 12/12
- 测试覆盖：间隙度量、gap==D 边界合并、传递链、圆柱精修（bbox 近但表面间隙超限不合并）、空表/单元素边缘、预筛==慢路径、合成数据 D=150/D=80 与参考签名逐字一致
- 与 COM.py 的刻意差异：参考工具两路径均返回组成员**下标**（COM.py 原返回元素对象）——签名比较需稳定身份
- BD4 完整判定剩余：Dynamo 里跑出与 CBWD 一致结果（需 Revit 环境）+ 翻弯/标签排列算法移植 + 组边界计算与参数写回

**质量门**：--test 229/230 过 0 败 1 跳（215→229，+14）；vm_diff 68/68 一致（65→68，3 个新测试文件自动纳入且双引擎一致）；cbwd_reference selftest 12/12 + parity 6/6；revit_bridge selftest 10/10；pyrevit_hook selftest 6/6；spec v1.10.0（§3.16 新增、§4.2 bim/cbwd、§6 限制 20）。

---

## v2.9.0 — Phase 6 首批：FFI 最小切片 + Revit 桥 + pyRevit 适配（2026-10-19）

> BIM 落地线开工：桥不造轮子——ctypes 是 CPython 自己的答案，
> 寄生期复用宿主 ABI；句柄是唯一的跨边界引用，Intent 侧永远不见 .NET 对象。
> 版本 2.8.0 → 2.9.0。

**I1 C ABI FFI 最小切片**（tests/test_ffi.intent 8 测试，全过）

- 新内置 6 个：`ffi_load(path)` / `ffi_func(lib, name, restype, argtypes)` / `ffi_struct(names, types)` / `ffi_field_get(s, name)` / `ffi_field_set(s, name, v)` / `ffi_sizeof(s)`
- 新值类型：LibValue / ForeignFuncValue（可调用，走 CallExpr callable 分发）/ StructValue；均引用语义
- 类型映射：Int→c_int / Float→c_double / Str→c_char_p(utf-8) / Bool→c_int / Ptr→c_void_p / Struct→指针 / Void→无返回
- restype 声明期钉死（默认 c_int 会把指针/字符串返回截断成 int）；`Struct` 形参显式 byref（**实测根因：未声明 argtypes 的 ctypes 对 Structure 实例按值传递——GetCursorPos 传实例 ret=0，byref ret=1**）
- 测试走真实 Windows API：msvcrt.strlen / user32.GetSystemMetrics / user32.GetCursorPos 出参写回；负例：符号缺失/库缺失/类型名白名单/参数个数
- 完整 I1 剩余（20 人日中的未做部分，已 note 断点）：回调 CFUNCTYPE、数组/联合、varargs、头文件解析、`foreign` 语法糖

**BD2 Revit API 桥**（tools/revit_bridge.py，selftest 10/10）

- UnwrapElement 模式：`__unwrap__()`（pyRevit）/ `InternalElement`（Dynamo）/ `unwrap()` 三形态识别，非元素值透传
- ElementRegistry：handle ↔ element 双向注册，wrap 幂等，句柄顺序分配（与 Revit ElementId 解耦），失效句柄 RuntimeError 显式失败
- RevitSession：send（元素→handle）/ read_props（边界读属性成 Intent 字典）/ run（prelude 注入 + RuntimeValue 树脱壳）/ recv（handle→元素，混合值透传）
- 端到端：mock Revit 世界上跑真实 Intent 选管规则（std/bim/unit 参与），身份保持验证

**BD3 pyRevit 适配**（tools/pyrevit_hook.py，selftest 6/6）

- CPython3 模式按钮流程 button_main：选元素 → send/read_props → Intent 规则 → 原生结果
- 宿主定位：显式 host 参数优先，否则沿调用栈向上 3 帧找 `__revit__`（按钮 script.py 的模块全局）；兼容 ActiveUIDocument/uidoc/直挂三种 Selection 形态
- check_intent 自检 + 宿主缺失显式报错带指引

**BD1 模板修复**（tools/dynamo_node.py，三处从未实跑过的断点）

- `geometry.point(...)` 不可用：import 扁平注入符号但中间名 `geometry` 不存在，且 bim/geometry 无 point() 函数 → 改 `Point3D() + create()`
- 返回值是 RuntimeValue 树 Dynamo 吃不下 → 模板改返回扁平 [x, y, z]，附 `_native` 脱壳；富几何转换（→ DesignScript Point）属 BD4 范围
- std/ 按 cwd 相对查找 → 模板切到 intent 根再跑，finally 还原

**质量门**：--test 215/216 过 0 败 1 跳（207→215，+8）；vm_diff 66/66；LSP 冒烟全通；registry/venv/typecheck selftest 全过；spec v1.9.0（§3.15 新增、§3.8 扁平注入边界、§4.1 156→162、§6 限制 17-19）。

---

## v2.8.0 — L1 渐进类型系统：mypy-lite 切片（2026-10-18）

> 契约是运行时可验证的主防线，类型是静态提示的副防线。
> 已知的检查，未知的放过；显式的信任，不猜——这是渐进类型的诚实。
> Phase 5 十二任务全部收官，47/47 = 100%。版本 2.7.0 → 2.8.0。

**L1 渐进类型系统**（tools/typecheck_selftest.py 21/21；tests/test_types_annotations.intent 5 测试）

- 新 CLI `--types [file]`：静态类型检查（mypy-lite），通过 exit 0，类型错误逐条报告 exit 1，语法错误 exit 2
- 新类 `TypeChecker`（src/mini_intent.py）：标注处检查 + 推断处放过
  - 三处检查：变量声明 `let x: T = expr`、调用实参 vs 本模块函数形参标注、`return` vs 返回标注
  - 推断器（轻量）：字面量 / 标注环境 / 内置返回白名单 / 本模块函数返回标注 / 算术比较运算规则
  - 数值互通（spec §2.1）：Int/Float 双向接受；Union 任一成员合法；泛型参数视为 Any；类型别名透明解析
  - 容器只查基类（List[Int] 元素类型不查，留待完整版）；`CallExpr.func` 为 Variable 节点的本模块调用同样检查
- 修复两处实现 bug：`func` 位为 Variable 节点时误当作不可哈希键崩溃（`TypeError: unhashable type`）；调用目标名提取统一走 `_call_target_name`
- 标注语法层（参数/返回/变量/泛型）本已就绪（P1.3 期），本轮补齐的是检查器本体
- 全仓库 `--types` 扫描零误报（tests/test_type_system.intent 两处报错为故意负例，`--check` 对 std/itertools2.intent 多行 export 的语法拒绝是既有行为）
- 已知边界：容器元素类型检查、全量局部推断、Union 值类型推断——留待完整版（20 人日口径中的剩余部分）

---

## v2.7.0 — Phase 5 三批：channel 通信 + 测试框架深化 + 事后调试 + 虚拟环境（2026-10-18）

> 并发的第二块拼图：spawn/scope 管任务的生死，channel 管任务间的对话。
> 测试框架从「能跑」到「能说话」：跳过是诚实的，预期异常是正面的，参数化是个案定位的。
> 崩溃不再是终点：帧快照存档，停机后进场检视。版本 2.6.0 → 2.7.0。

**CC2 channel 通信**（tests/test_channel.intent 8 测试）

- 新表达式 `ch <- v`（SendExpr）/ `<- ch`（RecvExpr）；词法 `<-` 进 SYMBOLS（无空格即通道，比较请留空格）
- 新内置 `chan()` / `chan(n)`（无界/容量 n）/ `close(ch)`
- 语义：Go channel 子集——缓冲满发送阻塞、空接收阻塞、关闭后发送报错、关闭后排空再接收抛 ChannelClosedError（显式失败不返回哑值）
- 线程安全由底层 queue.Queue 保证；通道引用语义（copy 返回自身，传参共享）
- 判定：多生产者多消费者 10 条消息无损 + 关闭排空语义 + 非通道类型拒绝

**TQ1 测试框架深化**（tests/test_framework_advanced.intent 9 通过 + 1 演示跳过）

- fixture 约定：setup/teardown 文件级钩子，运行器逐用例环绕（失败/skip 也清理；teardown 自身失败即用例失败）
- `expect_error(fn, type)`：预期异常——返回捕获的 ErrorValue，未抛错/类型不符报 AssertionError
- `skip(reason)`：SkipTest 信号，运行器摘要单独计数（`9/10 通过, 0 失败, 1 跳过`）
- `param_cases(cases, fn)`：参数化，用例展开传参，失败带用例序号
- mock 四件套：`mock(name)`（可直接调用）/ `mock_return` / `mock_calls` / `mock_call_count`
- CallExpr 新增可调用值分发（mock 等测试替身直接调用）

**EX2 事后调试**（判定：`--postmortem tests/_demo_error_stack.intent` 含「帧」，exit 0）

- 帧快照链：异常穿帧时每层 execute_function/_execute_method 挂本帧局部变量（`_intent_frames`，从外到内）
- 关键修复：帧快照取自建帧时挂到 `CallFrame.scope` 的本帧作用域——异常路径上内层作用域不恢复，从 current_scope 取会导致张冠李戴（首版即踩此坑）
- `--postmortem`：诊断渲染 → 快照写盘 `.intent_postmortem.json`（停机可捡回）→ 帧检视（frames/frame N/vars/where/quit），默认停出错帧；非交互 EOF 自动收尾 exit 0

**PK2 虚拟环境**（tools/venv.py，selftest 9/9）

- `create`（.venv/{lib,bin,venv.json}）/ `install`（源 → 全局缓存 → .venv/lib，缓存原子落位）/ `list` / `activate`（PATH + INTENT_VENV 片段）
- 全局缓存 `~/.intent/cache/packages/<name>@<version>/`，INTENT_HOME 可覆盖
- 隔离性：两项目各装各版本互不污染；venv 安装不落全局库；解释器侧 .venv/lib 进搜索路径且优先于全局库
- 端到端：venv install 后 Intent 程序 import 包成功

**其他**

- 测试 185 → 203（+18）；spec v1.7.0（§1.4 运算符、§3.12-3.14 新章、§4.1 内置 105→156 修正漂移、§5 CLI、§6 限制 #2）；LSP 关键字补 spawn/scope/raise
- 零回归：--test 203/0 失败；vm_diff 62/62；venv selftest 9/9

---

## v2.6.0 — Phase 5 二批：依赖解析 + 异常链 + 结构化并发 + 社区基建（2026-10-18）

> 错误作为一等值有了完整的生命周期：构造（error）→ 抛出（raise）→ 因果（from）→ 渲染（链）。
> 并发从零到一：spawn + scope，没有孤儿线程。版本 2.4.0 → 2.6.0（含 v2.4.0→v2.5.0 间 VERSION 常量漂移修正）。

**PK1 依赖解析器**（判定：`--install --dry-run tests/pkg_fixture` 含「依赖解析」，exit 0）

- CLI：`--dry-run`（只解析不安装）；`--install <dir>`（含 intent.toml 的目录按项目批量）
- semver：三段式解析（缺段补 0，正式版 > 预发布版）；约束 `^` `~` `>=` `<=` `>` `<` `=` `*`，逗号 AND
- 解析：BFS 依赖图 → 约束累积（钻石合并）→ 候选枚举（路径单候选 / 注册表多版本）→ 公共兼容集取最高（回退）→ 无解报冲突（exit 1 不写锁）
- `intent.lock`（JSON）：version/source/deps/required_by；安装前写入
- fixture：tests/pkg_fixture（钻石：alpha ^1.0 ∧ beta >=1.2.0 → mathkit 1.2.0）+ tests/pkg_fixture_conflict（^1.0 ∧ ^2.0 无解）
- 刻意不做：SAT 求解、git tag 枚举

**EX1 异常链**（tests/test_exception_chain.intent 7 测试）

- 新语句 `raise <错误值> [from <原因>]`；新内置 `error(type, message)` 构造一等错误值
- `raise` 接受 ErrorValue 原样 / `Err(...)` 取内层 / 字符串简写（RuntimeError）；其余明确 TypeError
- `ErrorValue.__cause__` 成员访问；顶层渲染「异常链(__cause__, 从起因到外层)」
- 穿帧快照不丢；catch 按类型定向捕获兼容
- 刻意不做：`__context__` 隐式上下文

**CC1 结构化并发**（tests/test_concurrency.intent 6 测试）

- 新语句 `spawn <可调用>;` / `spawn f(args);` + `scope { ... }` 块
- 语义：调用点求值；任务登记进 scope 任务表；块退出自动 join；任务异常 join 处重抛；scope 外 spawn 拒绝（无孤儿线程）
- 实现：Python threading 演示级，每任务独立 Interpreter，闭包作用域共享（GIL 下不相交数据安全）
- Resolver 新增三语句作用域解析；VM 经 RUN_AST 委托通道零改动兼容（vm_diff 62/62）
- 刻意不做：channel（CC2）、async/await（A3）

**CM1 社区基建**：.github/ISSUE_TEMPLATE/（bug_report + feature_request + config.yml）；README 增「路线图与社区」节指向 ROADMAP_LONGTERM.md；discussions 待 GitHub 开启

**质量门**：--test 185/185（172→185，+13）；vm_diff 62/62（60→62）；新测试文件 --check/--lint/--doc 全过（CI 同款）；spec v1.6.0 同步零漂移。

---

## v2.5.0 — Phase 5 首批：标准库扩张 + 内存管理 + 两个语言级修复（2026-10-18）

> 知行合一——spec 先立的 `else if` 补票落地，`and`/`or` 短路归正；标准库 18 → 33 模块。

**语言级修复（根因级，非症状级）**

| 修复 | 根因 | 修法 |
|---|---|---|
| `else if` 链不可用 | parser else 分支只接受 `{`；panic 恢复把后续语句错位到外层（模块加载时函数体泄洪到顶层，级联失败） | else 后随 if → 嵌套 IfStmt（与 elif 等价）；tests/test_control_flow.intent +2 回归 |
| `and`/`or` 两侧 eager 求值 | BinaryOp 统一走 `_binary_op`，右操作数无条件求值——`i < len(l) and l[i] < x` 在边界越界（heapq/bisect 全族中招） | evaluate_expression 入口拦截逻辑运算按需求值；返回类型保持 BoolValue 兼容；VM 经委托通道同受益 |

**标准库 SL1 高频库（12 新模块，判定 std 模块数 ≥30：18 → 33）**

| 模块 | 内容 |
|---|---|
| glob/shutil/tempfile/uuid/hashlib/hmac/secrets/decimal | 内置支撑（23 个新 builtin：glob_match、shutil_×3、tempfile_×3、uuid_×2、hash_×4、hmac_×2、secrets_×3、decimal_×5） |
| statistics/textwrap/csv/argparse/pathlib | 纯 Intent 实现（契约封门；无转义纪律走 chr(34)/chr(10)/chr(92)） |

**标准库 SL2 组合数学（stdlib/itertools2.intent，14 测试全过）**
permutations/combinations/product/heappush/heappop/bisect_left/bisect_right/insort + MinHeap/Deque/DefaultDict/ChainMap 四类；heap/bisect 为演示级实现（有序插入/线性定位），语义与 Python 对齐。

**内存管理 MM1（寄生策略，设计文档先行）**
`docs/memory_design.md`：候选策略三选一（自持 RC / 自持分代 GC / 寄生+观测），选定寄生——
容器创建即登记弱引用（`_ObjectRegistry`，List/Dict/Instance 三构造点挂接，VM 同路径覆盖），
循环垃圾委托宿主 CPython 分代 GC；std/memory.intent 五函数（mem_live/alloc_total/mem_stats/gc_collect/ref_count）；
tests/test_memory.intent 5/5（分配可观测/累计单调/自引用可诊断/**循环可回收**/统计形态）。

**新探明边界**（已入 spec §6 诚实清单）：`lst.push(x)` 方法式调用不支持（须 `push(lst, x)`）；
`ListValue.copy()` 不处理环（自引用列表作函数实参无限递归，M2 期修）；
`import std.X` 符号注入会遮蔽核心内置（pathlib.join → 改名 join_path 避让）。

**语义零漂移**：`--test` **172/172**（126 → 172，+46：itertools2 14 + highfreq 25 + memory 5 + control_flow 2）；
vm_diff **60/60 一致**；spec v1.5.0 同步（§3.3 else if / §4.1 104 内置 / §4.2 十五新模块 / §4.4 内存 / §6 四条新限制）。

---

## v2.4.0 — 工具链满编 + DAG 全任务收官（2026-10-18）

> 言不尽意，然言可逮意——35/35 全 done，五轨道（核心/标准库/工具链/稳定性/生态）100%。

| 特性 | 说明 |
|---|---|
| 标准库 B9 encoding | `std/encoding`：base64_encode/decode、gzip_compress/decompress、urlencode/urldecode（gzip 二进制以 base64 文本承载——Intent 字符串是文本；非法输入抛 ValueError）+ 6 builtin + 10 测试 |
| 工具链 C7 调试器 | CLI `--debug`：断点（break N）、单步（step）、放行（continue）、变量检视（print EXPR / vars）、调用栈（backtrace）、断点列表、quit。pdb 风格启动即暂停在起点；`execute_statement` 入口 hook；非交互 stdin EOF 自动放行 exit 0 |
| 工具链 C8 LSP | `tools/lsp/`：LSP 2.0 基线子集 stdio JSON-RPC 服务器——诊断（复用 Lexer/Parser，与 `--check` 同源）、补全（关键字+文档 def+内置函数+std 模块）、跳转（本文件 def/let/var/const 声明行）。`smoke_test.py` 14 项端到端全通 |
| 工具链 C9 文档站 | `tools/gen_docs_site.py` → `docs/site/index.html`：单文件零依赖静态站（37 页：规范/教程/哲学/标准库 API），客户端即时搜索，file:// 可开；暗色主题 |
| 工具链 C6 CI/CD | `.github/workflows/ci.yml` 七步：全库 check → 回归 test → 全库 lint → doc 生成 → fmt 幂等抽查 → VM 对照 → D5 性能门禁。本地全模拟通过；Actions 实跑待 push + workflow scope 授权 |
| 稳定性 D4 fuzz | `tests/test_fuzz.intent` 12 边界用例：索引/除法/None/类型混淆/字符串/数学/字典/深递归/大整数/空容器/随机采样范围契约/契约违约。判定哲学：边界输入必得可捕获 Intent 错误或确定值，解释器永不崩 |
| 稳定性 D5 门禁 | CI 相对性能门禁：同一次 run 内 VM 须严格快于解释器（fib(25) 正确性双检）——不受 CI 机器绝对速度影响。关键路径 T1→T7→D5 全部收官 |
| 生态 E2 标准库参考 | `docs/api/` 25 模块页 + 索引（`gen_docs_site.py --api` 生成，与 `--doc` 同源） |
| 生态 E4 包注册表 | `tools/registry.py`：publish/list/install 三命令 + selftest；本地目录注册表（`registry/<name>/<version>/` + registry.json），install 落 lib/ 即解释器搜索路径，装完可直接 import |
| 生态 E5 贡献指南 | `CONTRIBUTING.md`：五条项目纪律 / 提交流程 / 架构导览 / 加 std 模块五步清单 / 工具链速查 / 治理 |

**语义零漂移**：`--test` **126/126**（+22：encoding 10 + fuzz 12）；vm_diff **56/56 一致**；LSP 冒烟 14/14；注册表 selftest 6/6；文档站转换校验 37 页。

**新探明边界**（有意不为，已入 CONTRIBUTING「已知边界」）：`//` 是行注释致整除运算符源码不可达（用 `/` 真除法）；`len(None)` → AttributeError；`1e308*10` → inf，`str(inf)` 抛 OverflowError（均可捕获）；`-7%2=1` floor 语义；字典缺键抛 RuntimeError（KeyError 转译）。

---

## v2.3.0 — VM 性能 4.3x + datetime/re 标准库（2026-10-17）

> 言不尽意，然言可逮意——VM 从「能跑」到「跑得快」；标准库再添两只地面部队。

| 特性 | 说明 |
|---|---|
| VM V0.3 性能（T7） | 主循环热指令全内联：局部别名（stack/push/pop/frames/env/code/ip）、环境链变量解析内联、双侧 IntValue 算术/比较快路径、argc≤1 闭包调用免列表构造。fib(25)：VM ≈788ms vs 解释器 ≈3415ms ≈ **4.3x**（超 3x 目标） |
| 性能基准文件 | `tests/perf_check.intent`：fib(25) + `Time:` 计时行（vm_diff 归一化，两侧 stdout 可逐位对照） |
| 标准库 B4 datetime | `std/datetime`：now/today/parse/format/add_days/add_hours/diff_days/diff_seconds/weekday/parts/timestamp/from_timestamp/to_timezone（ISO 字符串表示，非法输入抛 ValueError）+ 12 builtin + 11 测试 |
| 标准库 B8 re | `std/re`：test/full_match/find_all/groups/replace/split（match 是语言关键字，锚定整串命名 full_match）+ 6 builtin + 8 测试 |

**语义零漂移**：`_binary` 重构为 `_binary_values`（值进值出），原 `_binary` 保留为栈式入口；委托点前同步 `self.env`——优化前后 vm_diff 全量对照 **55/55 一致**，`--test` **104/104**，全库编译冒烟 97/98（唯一失败 `_t_class.intent` 为根目录未入库的存量语法错误文件，与本次改动无关）。

---

## v2.2.0 — VM 全特性覆盖 + http/sqlite 标准库（2026-10-17）

> 言不尽意，然言可逮意——V0.1 的字节码是骨架，V0.2 让它长出血肉。

| 特性 | 说明 |
|---|---|
| VM V0.2 原生覆盖 | 闭包（Env 环境链 + MAKE_CLOSURE）、管道（编译期 desugar）、Result ? 传播（UNWRAP_OK）、契约检查（requires/ensures）、not、break/continue、隐式返回 |
| 委托通道 RUN_AST | match/类/with/方法调用/生成器/泛型/默认参数等经 VMScope 适配器交解释器执行，共享同一环境——任意 Intent 程序可编译，语义与解释器逐位一致 |
| VMScope 桥 | Scope 真子类；VM 启动时把解释器 global_scope 桥接为 VM 全局环境，嵌套 import 复用正版模块树（否则另建垃圾树覆盖） |
| 对象运算符重载 | `__add__`/`__eq__` 等经解释器 `_binary_op` 委托，零重复实现 |
| 标准库 B6 http | `std/http`：get/post/get_json/post_json + 本地测试服务器（serve_start/serve_stop，不依赖外网） |
| 标准库 B7 sqlite | `std/sqlite`：open/exec/query/close 句柄式 API，查询返回行字典列表 |
| 差分测试工具 | `tools/vm_diff.py`：examples/ + tests/test_* 全量 VM vs 解释器逐位比对（51/51 一致） |

**修复的真 bug**：一元负号编译顺序错误（V0.1 遗留：`-3` 编译成 `3-0`）；字符串拼接优先级错误（`op==ADD and lv是str or rv是str` 使任何含字符串的 `==` 恒真）；`_py_to_runtime` 字典键未规范化（json_parse 的 dict 无法下标取值，连带影响 http/sqlite 新库）。

**回归**：`--test` 85/85 通过（新增 http 5 + sqlite 4）；`--compile` 62/62 文件通过；VM 差分 51/51 一致。

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
