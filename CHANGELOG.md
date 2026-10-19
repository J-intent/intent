# 更新日志

本项目的重大变更记录。版本遵循语义化版本。

---

## v2.27.0 — L3b 返回推断：无标注函数也能被检查（2026-10-19）

> 标注是可选的，检查不该是可选的。L3b 让无返回标注的函数
> 也带着推断类型参与标注检查——调用方写错标注，当场被拦。
> 版本 2.26.0 → 2.27.0。

**L3b 返回推断**（tools/infer_selftest.py --returns 7/7）

- `TypeChecker.inferred_returns`：无返回标注的函数从 `return` 表达式推断（迭代收敛，上限 = 函数数 + 1——调用链上被调方先出结果，调用方才能借）
- 推断规则：单 return 直接取；多分支统一（同型 / 数值混合 → Float）；**分支不统一即不猜**（显式信任原则）；无 return 不推
- 调用点借用：`_infer_call` 对无标注函数返回推断结果 → `let x: String = f()`（f 返回 Int）**当场报错**
- 可观测：`--types --show-inferred` 增加 `返回推断: f: Int` 行
- 测试 7 用例：Int/String 推断、调用链借用、分支统一、分支不统一不猜、无 return 不推
- 边界（诚实清单）：不推成员访问/下标/闭包/递归函数（递归的自引用推断会得到 None——不猜）；推断仅用于标注检查，不改变运行时（spec §6 限制 33）

**质量门**：infer_selftest 15/15 + --returns 7/7；typecheck 25/25；--test 333/334；vm_diff 77/77；spec v1.26.0（§6 限制 33 扩展）。

**LangForge**：77/89（86%），类型线 L1→L2→L3a→L3b 连推，剩余旁路 11（L4/L5a·b 皇冠、A3b、M3a-c、I2b1·2、Q3a·b、E6）。

---

## v2.26.0 — L3a 局部类型推断：let 链传递 + 推断可观测（2026-10-19）

> 推断的核心不在「能猜」，在「链能传下去」。这一轮挖出检查器的真根因：
> 每条语句都 `dict(env)` 复制，let 链在第二条就断了——
> 修好之后 `let a = 1; let b = a;` 的 b 才是 Int。
> 版本 2.25.0 → 2.26.0。

**L3a 局部推断核心**（tools/infer_selftest.py 15/15；typecheck 25/25 无回归）

- **根因修复：env 传递链**。原 `check()` 每条语句 `dict(env)` 复制、`_recurse_value` 每项复制——同作用域的 let 链在第二条语句就断（`let a = 1; let b = a` 的 b 推不出）。改为：**同一作用域共享一份 env，块边界（if/while/for 体）整块共享一份拷贝**——块内链可传递、块内声明不污染外层
- 推断补齐：三元表达式（分支统一，数值混合提升 Float）、if 表达式（块尾类型）、管道 `x |> f`（取目标函数返回标注）、类构造（返回类名，L2 联动）
- 推断结果可观测：`TypeChecker.inferred_vars` + CLI `--types --show-inferred` 打印 `推断: name: Type`
- **判定方式纠偏**：L3a/L3b 是纯静态特性，原判定用 `.intent` 运行时测试文件（测不到编译期行为）——改为 `tools/infer_selftest.py`（fixture 直接驱动 TypeChecker，断言推断结果 + 推断参与标注检查的正反例）；PROGRESS_PLAN 与引擎判定同步（零漂移纪律）
- 边界（诚实清单）：不推成员访问/下标/闭包返回值/跨函数调用链；返回类型推断属 L3b（`--returns` 用例已备好，未实现即失败，不假通过）

**质量门**：infer_selftest **15/15**；typecheck_selftest **25/25**；--test 333/334；vm_diff 77/77；spec v1.25.0（§5 `--show-inferred`、§6 限制 33）。

**LangForge**：76/89（85%），类型线 L1→L2→L3a 连推，剩余旁路 12。

---

## v2.25.0 — L2 结构化类型：Protocol + 鸭子类型静态化（2026-10-19）

> 类型线开打。结构化类型不问「你是谁家的孩子」（继承声明），
> 只问「你会做什么」（方法集）——鸭子类型的静态化。
> 运行时 `implements` 是检查口，`--types` 在标注处当场拦截。
> 版本 2.24.1 → 2.25.0。

**L2 结构化类型**（tests/test_protocol.intent 10 测试 + typecheck 4 用例）

- 语法：`protocol Name { def m1() -> T; def m2(...); }`——`protocol` 为**软关键字**（identifier + 「名字 + `{`」才生效，作变量名不受影响）；AST 新节点 `ProtocolDef`（只记方法名，签名一致性留完整版）
- 运行时：`ProtocolValue` 登记方法名集合；`implements(obj, proto)` 沿继承链查方法存在性（实例/类对象均可用，标量→false）；`protocol_methods(proto)` 出方法名清单（诊断用）；非 protocol 参数显式抛 TypeError
- **静态侧（--types）**：`TypeChecker` 预收集 protocol 方法集与 class 方法集（继承链两遍收敛）；`_infer_call` 对类构造返回类名；`_compatible_one` 遇协议标注做结构子类型检查（`类方法集 ⊇ 协议方法集`）——缺方法在标注处/实参处当场报错，未知实际类型仍按「推断处放过」原则信任
- 测试：运行时 10/10（符合/缺方法/多方法/继承链/类对象/标量/反射/鸭子类型/错误参数/字符串化）；--types 新增 4 用例（覆盖通过/缺方法报错/继承链算数/实参传递报错），typecheck_selftest 25/25
- 边界（诚实清单）：只比方法名不比签名；嵌套 protocol 不查；运行时鸭子类型缺方法仍在调用时炸（NameError），`implements` 只是显式检查口（spec §6 限制 32）

**质量门**：--test **333/334 过 0 败 1 跳**（323→333，+10）；vm_diff **77/77 一致**（新测试文件自动纳入）；--check 过；typecheck_selftest 25/25；spec v1.24.0（§3.2 协议语义、§4.1 内置 166、§6 限制 32）。

**LangForge**：75/89（84%），关键路径已通，剩余旁路 14（类型 L3/L4/L5、A3b、M3a-c、I2b1/2、Q3a/b、E6）。

---

## v2.24.1 — I3b C 扩展 GC 钩子 + 判定防真空第三例（2026-10-19）

> 自己的判定自己咬：I3b 的 `contains ["gc"]` 被输出里 **"gcc"** 的三个字母
> 蒙混过关——钩子根本没实现却"通过"了。收紧成「GC 钩子」，并把钩子做实。
> 版本 2.24.0 → 2.24.1。

**I3b GC 钩子**（tools/csdk/loader.py + selftest）

- `_LIVE` 弱引用集合：原生模块加载即登记（`load_native` / `make_simulated_module`），被 GC 回收或显式 `unload_native` 即出表
- `live_native_modules()` 可观测出口；selftest 断言登记数 `1 → 0`（卸载即注销）
- 官方扩展示例：`example.c` 的高速数值核（`native_sum_range` / `native_square`）
- 边界（诚实清单）：GC 钩子 = 生命周期登记（弱引用），不是让 C 代码持有/释放 Intent 值——后者需要 ABI 对象模型，留后续

**判定纠偏第三例**：原判定 `contains ["gc"]` 误匹配编译器检测行里的 "gcc"。收紧为 `["GC 钩子"]`（实现专属证据词）。三类真空已入库：M3b（未知 flag 照常执行）、S4b（两边充数）、I3b（子串误匹配）——**判定子串必须是实现独有的词，不能是环境里随便出现的字母组合**。

**质量门**：csdk selftest 全通（ABI v1 + GC 钩子）；--test 323/324；vm_diff 76/76；spec v1.23.0 §6 限制 30 补充 GC 钩子口径。

---

## v2.24.0 — EX4 调试器增强 + I3a C 扩展 SDK（2026-10-19）

> 调试器从「能停」到「停得准」：条件断点与 watch 表达式让断点带脑子。
> C 扩展 SDK 打通「用 C 写 Intent 原生模块」的握手礼——ABI 先立，
> 编译产物交给有编译器的机器（本机没有，如实标注）。版本 2.23.0 → 2.24.0。

**EX4 调试器增强**（tests/_demo_conditional_bp.intent 演示，判定含「条件断点」）

- **条件断点**：`break N if EXPR`（交互）+ 源内指令 `// @break N if EXPR`；命中行后于当前作用域求值，为真才停；条件求值失败显式打印原因并按无条件命中（调试器静默比崩溃危险）
- **watch 表达式**：`watch EXPR` / `unwatch N|all` + 源内指令 `// @watch EXPR`——每次停顿打印观察值，求值失败同样显式标注
- **非 TTY 自动放行**：stdin 非终端（管道/CI）时命令循环入口直接放行——修掉 `input()` 在「管道开着不写」时永久阻塞的挂死根因（引擎判定第一次就撞上了）
- 源内指令让演示自包含：不依赖交互输入也能验证条件命中与 watch 输出

**I3a C 扩展 SDK**（tools/csdk/，selftest 含「ABI」）

- `intent_api.h`：ABI v1 契约——`IntentModule{abi_version,count,funcs}` + `IntentFuncEntry{name,arity,fn}` + 注册入口 `intent_module_register`；版本不匹配加载器显式拒绝
- `example.c`：示例扩展（`native_sum_range` / `native_square`）
- `loader.py`：`load_native(path)` → 调注册入口读函数表 → 包装为 Intent builtin；`run_source` 新增 `inject_builtins` 注入点（宿主注入原生函数）
- `selftest.py`：**双路径验证**——检测到 C 编译器（gcc/clang/cl）则编译 example.c 加载真 DLL；没有则用 ctypes 回调表走同一条 load→读表→调用路径。两条路都经 Intent 侧调用断言 `native_sum_range(1,100)=5050` / `native_square(12)=144` + ABI 版本校验
- **诚实标注**：本机无 C 编译器（gcc/clang/cl 均无），selftest 输出明示「C 编译路径未验证」——ABI 已验证，编译产物待有编译器的机器复验（spec §6 限制 30）

**质量门**：--test 323/324（EX4 仅动调试器路径，普通执行零开销）；vm_diff 76/76；csdk selftest 全通；spec v1.23.0（§5、§6 限制 30-31）。

**LangForge**：74/89（83%），关键路径已通，剩余均为旁路（类型 L2/L3/L4/L5、A3b、M3a-c、I2b、I3b、Q3、L2）。

---

## v2.23.0 — P3b Ed25519 包签名 + P4 .intentp 构建分发（2026-10-19）

> 包管理补齐末端两环：发布能立字据（签名），制品能成卷（.intentp）。
> 签名不依赖 openssl/GPG——纯标准库自持 RFC 8032 最小实现，
> 用标准向量自证正确性（第一次跑就抓出漏 clamping 的实现偏差）。
> 版本 2.22.0 → 2.23.0。

**P3b Ed25519 包签名**（tools/intent_sign.py + registry 集成，selftest 含「签名」）

- 新模块 `tools/intent_sign.py`：RFC 8032 Ed25519 最小实现（纯标准库，零外部依赖）——`keygen` 生成 sk.key/pk.pub（base64）、`--selftest` 用 RFC 8032 §7.1 测试向量 1 逐字节自证（公钥/签名/篡改拒绝/清单敏感性四项）
- 签名对象 = **文件清单摘要**（`relpath:sha256(content)` 排序拼接）——增/删/改任一文件都会改变摘要；与包格式解耦
- registry 集成：`publish --sign-key` 签名并写入索引（signature/pubkey）；`install` 先验签后落盘，篡改即拒；HTTP 通道同样携带/校验签名（验签失败不接触磁盘）
- selftest 扩签名链路：keygen → 签名发布 → 验签安装（正例）→ 篡改快照 → 安装必须失败（本地 + HTTP 双路）
- 踩坑两处：① 漏了 RFC 8032 的私钥标量 clamping，自签自验能过但公钥对不上标准向量——自证正确性的价值；② Windows 文本模式写文件 `\n→\r\n` 会改变清单摘要字节，HTTP 验签必失败——落盘改二进制写

**P4 .intentp 构建分发**（tools/pack.py，selftest 含 round-trip）

- 格式（format_version 1）：zip = `metadata.json`（name/version/files/entry_points/built_at）+ `files/<原结构>`——标准库可拆开看，不造私有二进制
- `build <pkg-dir>`（校验 [project]/[scripts] 与包内文件存在性）；`inspect`；`install --dest`：解包到 `dest/<name>/` + 按 `[scripts]` 生成 `bin/<cmd>.bat`（Windows）与 `bin/<cmd>`（sh），解释器路径嵌入 `sys.executable`
- selftest 真跑启动器（subprocess 执行 .bat 断言包程序输出）——round-trip 的终点是「装完能执行」，不是「文件在那儿」
- 踩坑：`.bat` 必须按系统 ANSI 编码写（cmd.exe 按代码页读脚本，UTF-8 写的含中文用户名路径会乱码成「找不到路径」）；子进程输出按 UTF-8 容错解码（中文 Windows 代码页不一致）

**质量门**：registry selftest 全通（publish/重复拒绝/list/默认最新/旧版/不存在 + 签名: keygen/签名发布/验签安装/篡改检测 + http round-trip）；pack selftest 全通；``--test`` 323/324（无回归）；vm_diff 76/76；spec v1.22.0（§5 工具链、§6 限制 28-29）。

**LangForge**：**P 链关键路径全线打通**（P3a→P3b→P4 三连），进度 71/89（79%），剩余均为旁路轨道（类型/互操作/属性测试/调试）。

---

## v2.22.0 — Phase 7 首批：A3a async/await + P3a HTTP 注册表 + S4b doc 收口（2026-10-19）

> 协程从语言进入语法：async 即惰性，await 即挂起，run 即蹦床——
> 底座是 S3 刚打好的 threadlet，不新造轮子。包管理同时从目录走上网络：
> 本地 registry 套一层 HTTP，publish/install 走 URL 即跨机。版本 2.21.0 → 2.22.0。

**A3a async/await 协程**（tests/test_async.intent 11 测试，全过）

- 语法：`async def f(...)` + `await expr` + 内置 `run(coro)`；`async`/`await` 均为**软关键字**（后随 `def` / 表达式起点才取得关键字地位，作标识符不受影响）；支持类内 async 方法
- 语义：调用即惰性返回 `<coroutine>`（体一行不跑）；`await` 求值出内层协程后经 `do_yield` 挂起（与 S3 yield 同一握手），`run` 以蹦床递归驱动内层、把结果送回避挂起点；async 函数无显式 `return` 时结果为 `None`（对齐 Python，普通函数的隐式返回约定不变）
- 实现：`AsyncValue` + 复用 `GeneratorController`（线程协作式协程）；控制器新增 `final_result`（done 消息同载，供 run 取返回值）；`execute_function`/`_execute_method` 各加惰性分支；异常沿驱动链自然穿透到 `run` 调用点
- 边界（诚实清单）：async 生成器（async + yield）显式拒绝；无事件循环/IO 多路复用（await 串行驱动，A3b）；`await` 软关键字歧义见 spec §6 限制 27
- **双引擎一致**：VM 对 async def 整条委托 + AwaitExpr 走 RUN_AST——vm_diff 自动纳入新测试文件且 76/76 一致

**P3a HTTP 注册表服务**（tools/registry.py selftest 含 http round-trip）

- `serve` 命令：stdlib `ThreadingHTTPServer`——`GET /index.json` 查询索引、`GET /pkg/<name>/<ver>/<file>` 下载、`POST /publish` 发布（JSON {name, version, files}）
- 客户端：`publish`/`install` 带 `--registry-url` 即走 HTTP 通道；install 按索引 files 清单逐文件下载后落 `lib/`
- 索引新增 `files` 字段（本地 publish 与 HTTP 发布共用）；发布校验（包名/版本/含 .intent）本地与 HTTP 同一套规则；路径穿越防护；版本冲突 409
- selftest 扩 HTTP round-trip：真起服务（临时端口）→ HTTP 发布 → 索引查询 → HTTP 安装 → 内容校验 → 重复发布被拒（409）

**S4b 标准库 doc 页收口**

- `tools/gen_docs_site.py --api` 全量再生：43 个模块页（对齐 43 个真实模块；`std/__init__.intent` 是包标记不计）+ 文档站 58 页
- LangForge 判定同时收紧为子集检查（原「页数≥模块数」两边各充一个数，脆弱平衡——见 PROGRESS_PLAN 判定纠偏记录）

**质量门**：--test **323/324 过 0 败 1 跳**（312→323，+11）；vm_diff **76/76 一致**（新文件自动纳入）；registry selftest 全通（含 HTTP）；spec v1.21.0（§3.2 协程、§4.1 内置 164、§6 限制 27）。

**LangForge**：Phase 7 注入后首批 3 任务闭环（P3a/S4b/A3a），进度 69/89（77%），关键路径 P3b→P4。

---

## v2.21.0 — S3：生成器完整化（真惰性协程）（2026-10-19）

> 旧实现：生成器函数**饿收集**——调用即跑完整个函数体，yield 的值攒成
> List 返回。send/throw/close 无从谈起（没有挂起点），无限生成器直接挂死。
> 本版换成线程协作式协程（threadlet）：体跑独立线程，双队列握手，
> 任意时刻只有一个线程在跑，共享解释器状态靠上下文切换白名单保存/恢复。

**新语义（对齐 CPython）**

- 调用即惰性：`g()` 返回 `<generator>`，函数体一行不跑；首个 `next()` 才启动
- `next(g)` 拉一个值，耗尽返回 `None`（语言约定，无 StopIteration 通道）
- `g.send(v)`：v 递送到 yield 表达式（`let x = yield v` 的 x 即 v）；首 send 必须 None
- `g.throw(e)`：在挂起点抛错——生成器内 catch 接得住，未捕获则到调用方
- `g.close()`：关闭信号是 BaseException 子类，业务 catch 吞不掉（对齐 GeneratorExit）
- `yield` 表达式化：`let x = yield v;`；裸 yield 产出 None（旧版为 0，已迁移）
- `yield from` 对生成器源：逐项 pull 且 send 值透传；列表/字典源逐项交出
- `for x in g` 真懒遍历：不预取，无限生成器可用；break/return 提前退出自动收摊协程线程

**实现要点**

- `GeneratorController`：协程线程 + in_q/out_q 双队列；`_GEN_CTX_ATTRS` 白名单
  （current_scope/call_stack/return_flag/current_line/… ）在切换点保存恢复；
  global_scope/functions/builtins 共享——正是生成器闭包所见的世界
- 嵌套生成器：外层线程驱动内层控制器（owner 链），close 沿链传播有界收摊
- 生成器方法（class 内 yield）：`this` 由协程线程重建后注入
- requires 在首个 pull 时验（惰性）；ensures 不验（无返回值可验，Python 同语义）
- 修一个被掩盖的旧 bug：`_has_yield_in_body` 递归进嵌套函数体，把外层误标
  成生成器——饿收集时代无症状，真惰性后「调用即返回」会直接吃掉外层执行

**边界（诚实清单）**：字节码 VM 无生成器路径（VM 差分纪律：不跑含 yield 的文件）；
协程线程内 profiler 打点关闭（帧栈纪律与协程切换冲突），覆盖率打点保留；
异常在调用方 pull 点抛出的栈快照为「生成器创建链 + 生成器帧」，不含 pull 点调用链；
生成器线程阻塞在 channel 等无界操作时 close 有界返回（2s），留 daemon 线程。

**测试**：tests/test_generator_full.intent 20 用例（惰性证明/send/throw/close/
吞不掉/break 收摊/嵌套/闭包/方法/requires 惰性违约）；test_generators_p1.intent
语义迁移至 collect() 物化；全量回归 312/313 绿（1 跳过为既有）。

---

## v2.20.0 — S2b：f-string 完整化（2026-10-19）

> 对齐 Python f-string 三形态：调试格式 / 嵌套引号 / 格式规格。
> 旧实现是正则 `[^}]+` 扫描——不敢放嵌套括号（切片/字典/调用）；
> 且插值区内引号会提前终止字符串（`"${d["k"]}"` 直接语法错误）。

- **调试格式 `${x=}`**：输出 `x=<值>`（表达式原文 + `=` + 求值）；`${x=:.2f}` 可叠加规格
- **格式规格 `${x:spec}`**：新内置 `format(v, spec)`——白名单校验（拒花括号）后原样委托 Python `format()`；fill/align/sign/0宽度/千分位/精度/类型（d e f g x o b % s）全支持
- **嵌套引号**：lexer 插值区括号深度 + 嵌套子串跟踪，`"${d["k"]}"` / `"${d['n']}"` 合法；三引号字符串同规则
- 插值扫描器重写：括号深度感知——切片 `${l[1:3]}` 的冒号不再是规格分隔符（深度1 才算），字典/调用/嵌套字符串内的括号不误计
- tests/test_fstring_advanced.intent 12 用例；全量回归 292/293 绿（1 跳过为既有）

---

## v2.19.0 — Q4：基准套件（2026-10-19）

> 性能要对数字说话，不靠"感觉不慢"。benchmarks/ 三类基准 +
> 运行器 + 基线报告，回退超 20% 自动标红。

- `benchmarks/fib.intent`：fib(25) 递归（调用链试金石）+ fib_iter(10000) 循环/局部变量，附迭代=递归自检
- `benchmarks/attrs.intent`：实例字段读/写各 10 万次 + cache_stats 命中率（M2 缓存有效性有数：实测命中率 99.9996%）
- `benchmarks/contracts.intent`：同构函数对（带契约 vs 不带）量化契约税——实测 55%，spec §6 记录
- `benchmarks/run_benchmarks.py`：每基准跑 3 次取最小值；`--update` 重写基线；与 BASELINE.md 对比超 +20% 判回退并非零退出
- 基线来自真实运行（Ryzen 7 9700X / Win11 / Python 3.12），不手写编造

---

## v2.18.0 — E3 + Q2：语句覆盖率 + 契约覆盖率（2026-10-19）

> 修掉一个被掩假的 done：E3 源码覆盖率 10-17 被同名 id 的「示例库」
> （examples≥20 恒真）掩成 done，实际 `--coverage` 从未实现（未知 flag
> 被 parse_known_args 吞掉）。本轮落地真实现，Q2 契约维度同轮交付。
> 引擎 id 撞车 bug 已上报阿J（langforge.py 不在本自动化改动范围）。

**E3 语句覆盖率（`--coverage file`）**

- `CoverageTracker`：execute_statement 入口打点（含 def 行/方法行的注册处打点）；分母 = AST 全量遍历的非表达式语句行
- 测试文件口径：无 main 时执行全部 `test_*` 函数（与 `--test` 一致），否则报告是 0% 空壳
- 崩溃也出报告（错误进 stderr，报告进 stdout，退出码 1）——覆盖到哪看见到哪

**Q2 契约覆盖率（`--coverage --contracts`）**

- requires/ensures 逐子句按身份计（AST 节点 id 去重——覆盖率不是执行次数，实测踩过 150% 的坑已修）
- 报告：契约覆盖率总况 + requires/ensures 分项；未调用函数的契约不进分子（部分覆盖场景实测 2/3）

**边界（诚实清单）**：裸表达式语句（`f();`）不计分母；行级口径（同行多语句算一条）。

---

## v2.17.0 — S2a 切片：海象赋值 + 切片赋值（2026-10-19）

> 语法糖补全的第一刀：表达式级赋值与列表写入侧。lexer 一层合并
> （:= 此前被 : 单字符快通道劈成两截）、parser 最低优先级挂点、
> 求值器/reolver 各一分发；切片赋值复用 SliceExpr，零新求值路径。
> 中途踩坑已修：parse_statement 下标赋值检测一度把 index 传成整个
> SubscriptExpr（求值索引变读取，未命中键即 KeyError）——A/B（stash）
> 定位后修复，全量回归 280/281 绿。

**海象 `:=`**

- 新 AST `WalrusExpr(name, value)`；`parse_expression` 最低优先级（低于三元/管道/逻辑或/比较）
- 求值：存在则 assign，否则 declare；返回被赋的值；左部非变量显式语法错误
- resolver 同步：海象名入当前作用域（否则局部绑定后续引用掉到全局查找）
- lexer：`:` 快通道前合并 `:=` 双字符（`::` 不受影响）

**切片赋值 `l[a:b] = v`**

- parse_statement 赋值检测认 SliceExpr（切片读取的产物即赋值目标）
- 执行器切片分支：步长限 1、右侧限列表、Python slice 增删长度语义、负索引
- 错误路径全显式：扩展切片 TypeError / 复合操作符 RuntimeError / 字符串 TypeError

**测试**：tests/test_syntax_sugar.intent 12 用例（含 `or` 返回 Bool 的本语言语义锁）。

---

## v2.16.0 — X2：反射完整化切片（2026-10-19）

> 反射四件套 + callable + std/inspect 纯 Intent 封装。边界如实记录：
> 实例作函数参数是值拷贝（参数绑定 `arg_value.copy()`，既有语义）——
> 经函数参数 setattr 不传播回调用方，inspect 因此不提供 setdefault
> （承诺了语言给不了的事就是撒谎）；`let` 别名共享引用，别名侧
> setattr 生效。函数元数据内省（signature/params）留后续切片。

**内置（X2）**

- `getattr(obj, name)` / `setattr(obj, name, v)` / `hasattr(obj, name)` / `dir(obj)`（字段+方法含继承链）
- `callable(x)`：函数/类/FFI/Python 桥/mock/有 `__call__` 的实例
- `ClassValue.all_method_names()`：继承链方法名枚举（dir 的地基）

**std/inspect.intent（纯 Intent 封装）**

- `getmembers` / `get(obj, name, default)` / `attr_names` / `is_field` / `is_method`
- tests/test_reflect.intent 11 用例，含参数拷贝语义的对照锁定

---

## v2.15.0 — M2 切片：实例属性访问缓存 + 命中率可观测（2026-10-19）

> 按拆解指引落地最小切片：缓存表 + 测试骨架 + 微基准命中率。
> 诚实记录：端到端 A/B（30000 次 `p.sum()`）0.99x——树遍历解释器
> 开销主导，2x 微基准留待隐藏类/调用点内联缓存迭代。

**缓存表（`InstanceValue`）**

- `get()`：缓存命中免 `fields`/方法表两级查找；未命中填缓存（字段 + 方法查找结果，类创建后方法表即稳定）
- `set()` 写透同步——无失效窗口；`execute_member_assignment` 的直写 fields 两处改道 `set()`（缓存一致性）
- `copy()` 得新实例新缓存（字段直赋，不经 set）

**可观测性**

- `cache_stats()` → `[命中, 未命中]`（模块级聚合）；`cache_reset()` 清零
- tests/test_inline_cache.intent：写透语义/方法查找/微基准（4300 次读取，未命中仅 sum 首次查找，稳态命中率 99.98%）
- 实测备忘：方法查找路径缓存后约为 `find_method` 链的 1/3；端到端被解释器固定成本摊平——如实记录，不吹 2x

---

## v2.13.0 — X3 + M4：dunder 协议全家 + 函数级剖析（2026-10-19）

> 两个切片一轮落地。X3 补完元编程协议面；M4 把「看不见的慢」
> 变成一张表：函数级调用/累计/自身时间 + 分配热点。profiler 未启用时
> 热路径只多一次属性判断，零开销。

**X3 dunder 协议全家**

> 元编程协议从「运算符重载 + 两个内置分发」扩到完整协议面：解释器新增
> 七个分发点（调用/迭代/with/归属/dict 键/字符串化），`next()`/`repr()`
> 两个内置，`!=` 回退 `__eq__` 取反。VM 经委托通道零改动。既有
> `__iter__`(返回列表)/`__len__`/`__str__`/比较系路径原样回归。

- `__call__`：`obj(args)` 两条路径（作用域变量 + 成员访问持有）→ `_execute_method`
- `__next__`：`next(it)` 内置；for 循环支持 `__iter__` 返回迭代器对象或自身即迭代器——树遍历边界预取为列表（`_drain_iterator`，100 万项安全上限；生成器仍真惰性）
- `__enter__`/`__exit__`：with 语句协议化，`__enter__` 返回值绑定 as 名，`__exit__` 收退出错误值；无协议实例维持旧约定（绑资源 + `close()`），tests/test_with.intent 全绿回归
- `__contains__`：`x in obj`
- `__hash__`：实例作 dict 键——`_dict_key` 统一入口（字面量/推导式/下标读写/has_key/in 六处），返回 Int/String 为键
- `__repr__`：`repr()` 内置 + `_value_to_str` 回落链 `__str__` → `__repr__` → 结构渲染
- `!=` 未定义 `__ne__` 时回退 `__eq__` 取反（对齐 Python 默认推导）

**M4 `--profile`（函数级，cProfile 等价切片）**

- `FunctionProfiler`：挂接 `execute_function`/`_execute_method` 帧入出；自身时间 = 累计 − 直接子调用（`_stack` 逐层上报）；`time.perf_counter` 单调时钟
- 输出按累计降序：函数名/调用次数/累计(s)/自身(s) + 墙钟总耗时
- 顺带修复：`_execute_method` 帧名取 `class_value`（不存在属性）→ `klass.name`，方法帧恢复 `类.方法` 前缀（错误调用链同受益）

**M4 `--mem-profile`（分配热点）**

- MM1 注册表增 `alloc_by_type` 计数；实例按类名聚合（原先 `get_type()` 对实例返回 StringType，类型名失真）
- 输出：累计分配/当前存活/已回收 + 按类型存活与累计分配表

**测试**：tests/test_dunder.intent 12 用例（协议面全覆盖）；全量回归 254/255（1 为既有演示性 skip）。

---

## v2.12.0 — X1 二批：装饰器完整化切片（带参/语句级）+ lru_cache（2026-10-19）

> 最小切片把「装饰器能用」推进到「装饰器够用」：带参工厂、语句级声明、
> 有界缓存三块落地，全程零语言级扩张——parser 收表达式、解释器多一次
> 求值、std 多一个纯 Intent 模块，VM 经委托通道零改动。版本 2.11.0 → 2.12.0。

**带参装饰器 `@deco(args)`**（parser + 解释器，无新语法）

- 新 AST 节点 `Decorator(name, args, is_call)`——`FunctionDef.decorators` 由 `List[str]` 改为 `List[Decorator]`（blast radius 5 处，全部核对）
- parser `_parse_decorators()` 提取为公共 helper：顶层 `program()` 与语句级 `parse_statement()` 共用；带参形态参数沿用 `parse_call_expr` 括号约定（括号内可换行）
- `is_call` 区分 `@deco` 与 `@deco()`（零参调用形态，对齐 Python 语义）
- 应用期两形态：裸 `deco(fv)` / 带参 `deco(args...)(fv)`——参数在当前作用域求值，工厂返回值非函数则显式警告（不静默）
- **实证锁定的栈序**：应用顺序 = 声明顺序（自上而下），先应用者居内——**末位装饰器最外，与 Python 的首位最外相反**（既有行为，非对称探针 `@tag_a @tag_b` → log [B, A] 证实；修掉 v2.11.0 以来「自外向内」的误导注释）

**语句级装饰器（函数体内 def）**

- `parse_statement()` 顶部识别 `@`：收集装饰器 → 要求紧跟 `def` → 复用 `execute_statement` FunctionDef 分支的既有应用路径
- 价值：函数体内装饰的执行时机在顶层 import/let **之后**——装饰器工厂可见闭包变量，绕开提升期时序限制（spec §6 限制 21 的语句级出口）

**`lru_cache(f, cap)`**（std/functools.intent，纯 Intent 零内置依赖）

- 真 LRU：命中即刷新访问序（命中键移序尾），满容淘汰序头（最久未访问）
- Intent 字典无 delete——刷新与淘汰都靠重建字典 + 闭包重绑定（提升期已实证可用）；代价命中 O(cap)，宜取小 cap（教学/演示级，非高性能缓存）
- `cap < 1` 显式抛 `ValueError`（显式失败不静默）；键限标量（字典键规范），富键调用方自行编码

**测试**（tests/test_decorator.intent 6 → 13，+7）

- 带参工厂副作用记账（`@repeat(3)` 内层三次）/ 参数透传闭包（`@tag("tagged")`——裸形态下 label 未绑定，调用即错，锁定 is_call 路径）/ 零参调用形态（`@setup()` 行为锁定）/ 带参+裸栈序 / 语句级带参装饰器（工厂恰调一次 + 包装器恰调一次）/ lru_cache 完整淘汰链（含「序头在重算中被淘汰」的二级效应）/ cap=0 显式失败
- 设计注记：顶层 `@setup()` 原想断言「工厂恰调一次」，但顶层 `let mut` 在提升期不可见（限制 21 同根）——该证据移入语句级测试，顶层改用纯行为锁定

**质量门**：--test **242/243 过 0 败 1 跳**（235→242，+7）；vm_diff **69/69 一致**（新测试文件自动纳入双引擎对照）；--check 新文件过；spec v1.12.0（§3.2 装饰器形态、§4.2 functools lru_cache、§6 限制 21 更新）。

**完整 X1 剩余（更新断点）**：wraps（需函数元数据内省，X2 反射）/ partial（需 *args 变长形参，语言级）/ 模块导入装饰器的提升期时序（需「def 即语句执行」改造）。

---

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
