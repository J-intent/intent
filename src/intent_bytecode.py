# intent_bytecode.py — 字节码编译器与栈式 VM（V0.3）
#
# 心学为体：AST 是意，字节码是言——言不尽意，但言可执行
# 禅道为翼：编译一次，执行多次；心不再每次都临场
# 马哲为用：同样的语义，从「每次现场解释」到「先沉淀后执行」
#
# V0.2 覆盖（在 V0.1 骨架上扩展）：
#   原生字节码：let/let mut、算术与比较、not、print、if/else、while、
#               break/continue、函数定义与调用、闭包（环境链捕获）、
#               管道（编译期 desugar 为嵌套调用）、Result ? 传播、
#               契约检查（requires 进门 / ensures 出门）
#   委托通道（RUN_AST）：match / 类与对象 / with / 方法调用 / for /
#               生成器 / 装饰器 / 泛型等重特性——AST 节点原样交给
#               树遍历解释器执行，与 VM 共享同一环境（VMScope 桥）。
#               语义因此与解释器逐位一致（同一 AST、同一 builtin）。
#
# V0.3 性能（T7）：主循环热指令全内联——局部别名（stack/push/pop/
#   frames/env/code/ip）、环境链变量解析内联、双侧 IntValue 算术/
#   比较快路径、argc≤1 闭包调用免列表构造。委托点前同步 self.env，
#   慢路径仍走原方法——语义与 V0.2 逐位一致（vm_diff 全量对照）。
#
# 架构：
#   Emitter   AST → Instruction[]（带回填的跳转/委托上下文）
#   VM        栈式执行：值栈 + 帧栈 + 环境链（Env: 词法作用域）
#   VMClosure 闭包值：编译码 + 定义时环境（FunctionValue 子类——
#             解释器侧零改动即可调度）
#   VMScope   Scope 协议适配器：解释器作用域 ↔ VM 环境链双向可见
#
# 已知边界（诚实记录，不假装覆盖）：
#   - 委托块（match 块体/with 体）内的 break/continue 经流控标志
#     回传 VM 循环；委托块外（顶层）的 break/continue 宽松忽略
#   - 委托执行中解释器若声明 defer，清理动作不跨 VM 帧传播

from mini_intent import (
    ASTNode, Expression, VariableDecl, Assignment, BinaryOp, UnaryOp, Literal,
    Variable, IfStmt, WhileStmt, FunctionDef, ReturnStmt, PrintStmt, CallExpr,
    BreakStmt, ContinueStmt,
    LambdaExpr, PipeExpr, TryExpr, MemberAccess,
    IntValue, FloatValue, StringValue, BoolValue, NoneValue, RuntimeValue,
    ListValue, FunctionValue, ClassValue, InstanceValue, ResultValue, Scope,
    ContractViolation,
)


# ── 指令集 ────────────────────────────────────────────
# 每条指令 = (opcode: str, arg)，arg 含义随 opcode：
#   常量/变量: LOAD_CONST <值> | LOAD_VAR <名> | STORE_VAR <名> | ASSIGN_VAR <名>
#   算术/比较: ADD SUB MUL DIV MOD EQ NE LT LE GT GE | NOT
#   控制流:   JUMP <addr> | JUMP_IF_FALSE <addr>（弹出栈顶）
#   函数:     CALL <(名,个数)> | CALL_VALUE <个数> | MAKE_CLOSURE <meta> | RET
#   输出:     PRINT <参数个数> | POP
#   Result:   UNWRAP_OK <函数末尾RET地址>（? 传播: Err 跳末尾提前返回）
#   契约:     RAISE <违约消息>
#   委托:     RUN_AST <(节点, 'expr'|'stmt', 循环起点|None, 循环出口|None)>
class Op:
    LOAD_CONST = "LOAD_CONST"
    LOAD_VAR = "LOAD_VAR"
    STORE_VAR = "STORE_VAR"
    ASSIGN_VAR = "ASSIGN_VAR"
    ADD, SUB, MUL, DIV, MOD = "ADD", "SUB", "MUL", "DIV", "MOD"
    EQ, NE, LT, LE, GT, GE = "EQ", "NE", "LT", "LE", "GT", "GE"
    NOT = "NOT"
    JUMP, JUMP_IF_FALSE = "JUMP", "JUMP_IF_FALSE"
    CALL, CALL_VALUE, MAKE_CLOSURE, RET = "CALL", "CALL_VALUE", "MAKE_CLOSURE", "RET"
    PRINT, POP = "PRINT", "POP"
    UNWRAP_OK = "UNWRAP_OK"
    RAISE = "RAISE"
    RUN_AST = "RUN_AST"


# 算术/比较指令集 — 主循环内联快路径的分派判据（frozenset 哈希查找）
_ARITH_OPS = frozenset({
    Op.ADD, Op.SUB, Op.MUL, Op.DIV, Op.MOD,
    Op.EQ, Op.NE, Op.LT, Op.LE, Op.GT, Op.GE,
})


# ── 环境链：词法作用域的运行时载体 ────────────────────
class Env:
    """变量环境：vars + parent 链。

    闭包的本质：函数记住定义时的 Env，调用时以它为父层建新 Env。
    """

    __slots__ = ('vars', 'parent', '_scope')

    def __init__(self, parent: 'Env' = None):
        self.vars = {}
        self.parent = parent
        self._scope = None

    @property
    def scope(self) -> 'VMScope':
        """惰性构建解释器侧适配器（整个链只包一次）"""
        if self._scope is None:
            self._scope = VMScope(self)
        return self._scope


class VMScope(Scope):
    """Scope 协议适配器 — 解释器与 VM 环境之间的桥。

    symbols 与 Env.vars 是同一个 dict 对象：解释器侧声明的变量
    VM 立即可见，VM 侧存储的变量解释器也读得到——委托通道
    （RUN_AST）因此能与原生字节码共享同一套变量。

    继承 Scope（而非鸭子类型）是有意的：解释器模块系统用
    isinstance(x, Scope) 校验 module_ref 链条（execute_import
    的层级挂载），子类身份让 VM 全局环境能直接充当解释器的
    global_scope——嵌套 import 解析外层模块时沿作用域链找到的
    就是 VM 里的正版模块树，不会另建垃圾树。
    """

    def __init__(self, env: Env):
        super().__init__(parent=None)
        self.symbols = env.vars          # 共享 dict，双向可见
        self._env = env
        self.parent = VMScope(env.parent) if env.parent is not None else None

    def declare(self, name: str, value, is_const: bool = False,
                allow_redefine: bool = False):
        if name in self.symbols and not allow_redefine:
            raise NameError(f"变量 '{name}' 已在此作用域中声明")
        self.symbols[name] = value
        if is_const:
            self.constants.add(name)

    def assign(self, name: str, value):
        s = self
        while s is not None:
            if name in s.symbols:
                if name in s.constants:
                    raise ValueError(f"无法修改常量 '{name}'")
                s.symbols[name] = value
                return
            s = s.parent
        raise NameError(f"未定义的变量 '{name}'")

    def get(self, name: str):
        s = self
        while s is not None:
            if name in s.symbols:
                return s.symbols[name]
            s = s.parent
        raise NameError(f"未定义的变量 '{name}'")

    def has(self, name: str) -> bool:
        s = self
        while s is not None:
            if name in s.symbols:
                return True
            s = s.parent
        return False

    def get_opt(self, name: str):
        s = self
        while s is not None:
            if name in s.symbols:
                return s.symbols[name]
            s = s.parent
        return None

    def enter(self) -> Scope:
        """进入子作用域（委托块内部使用，解释器语义）"""
        return Scope(parent=self)

    def exit(self):
        return self.parent

    def ancestor(self, depth: int):
        scope = self
        for _ in range(depth):
            if scope.parent is None:
                raise RuntimeError(f"作用域深度不足: 请求 depth={depth}")
            scope = scope.parent
        return scope

    def get_at(self, depth: int, name: str):
        return self.ancestor(depth).symbols[name]

    def assign_at(self, depth: int, name: str, value) -> None:
        scope = self.ancestor(depth)
        if name in scope.constants:
            raise ValueError(f"无法修改常量 '{name}'")
        scope.symbols[name] = value


# ── 发射器：AST → 指令序列 ────────────────────────────
class Emitter:
    """把 AST 编译为字节码。跳转目标用回填（先占位后补齐）。

    builtin_names: 解释器 builtin 名集合——调用名落在其中且非本文件
    定义的用户函数时，整条调用委托解释器解析（builtin / 模块注入符号）。
    """

    def __init__(self, builtin_names=()):
        self.code = []                   # List[Tuple[str, Any]]
        self.functions = {}              # 函数名 → meta（原生编译的顶层/嵌套函数）
        self._builtin_names = set(builtin_names or ())
        self._unwraps = []               # 待回填 UNWRAP_OK → 本函数末尾 RET
        self._ensures = None             # 当前编译函数的 ensures 条款
        self._contract_fails = []        # 待回填契约违约跳转 (pos, msg)
        self._loops = []                 # 循环栈: {'start', 'breaks', 'continues', 'flows'}

    def emit(self, op: str, arg=None) -> int:
        self.code.append((op, arg))
        return len(self.code) - 1

    def patch(self, pos: int, target: int):
        op, _ = self.code[pos]
        self.code[pos] = (op, target)

    # ── 表达式 ──
    def compile_expr(self, node):
        if node is None:
            self.emit(Op.LOAD_CONST, NoneValue())
            return
        if isinstance(node, Literal):
            if node.literal_type == 'int':
                self.emit(Op.LOAD_CONST, IntValue(node.value))
            elif node.literal_type == 'float':
                self.emit(Op.LOAD_CONST, FloatValue(node.value))
            elif node.literal_type == 'string':
                self.emit(Op.LOAD_CONST, StringValue(node.value))
            elif node.literal_type == 'bool':
                self.emit(Op.LOAD_CONST, BoolValue(node.value))
            else:
                self.emit(Op.LOAD_CONST, NoneValue())
        elif isinstance(node, Variable):
            self.emit(Op.LOAD_VAR, node.name)
        elif isinstance(node, UnaryOp):
            if node.op in ('not', '!'):
                self.compile_expr(node.operand)
                self.emit(Op.NOT)
            elif node.op == '-':
                # 0 - x（操作数后压会算成 x - 0 — V0.1 遗留 bug, 已修）
                self.emit(Op.LOAD_CONST, IntValue(0))
                self.compile_expr(node.operand)
                self.emit(Op.SUB)
            else:
                self._delegate_expr(node)
        elif isinstance(node, BinaryOp):
            self.compile_expr(node.left)
            self.compile_expr(node.right)
            op_map = {
                '+': Op.ADD, '-': Op.SUB, '*': Op.MUL, '/': Op.DIV, '%': Op.MOD,
                '==': Op.EQ, '!=': Op.NE, '<': Op.LT, '<=': Op.LE,
                '>': Op.GT, '>=': Op.GE,
            }
            op = op_map.get(node.op)
            if op is None:
                self._delegate_expr(node)
                return
            self.emit(op)
        elif isinstance(node, LambdaExpr):
            if any(p[2] is not None for p in node.params):
                self._delegate_expr(node)   # 默认参数 — 解释器绑定
            else:
                self._compile_lambda(node)
        elif isinstance(node, PipeExpr):
            # 管道: left |> right → right(left)（编译期 desugar）
            self.compile_expr(self._desugar_pipe(node))
        elif isinstance(node, TryExpr):
            # ? 传播: Err → 跳函数末尾 RET 提前返回; Ok → 解包
            self.compile_expr(node.expr)
            pos = self.emit(Op.UNWRAP_OK, None)
            self._unwraps.append(pos)
        elif isinstance(node, CallExpr):
            self._compile_call(node)
        else:
            # match / 成员访问 / if 表达式 / 列表字典字面量等 —
            # 委托通道: 原样 AST 交解释器, 共享当前环境
            self._delegate_expr(node)

    def _desugar_pipe(self, node):
        """PipeExpr → 嵌套 CallExpr（右结合折叠）"""
        if isinstance(node, PipeExpr):
            left = self._desugar_pipe(node.left)
            return CallExpr(func=node.right, args=[left],
                            line=getattr(node, 'line', 0),
                            column=getattr(node, 'column', 0))
        return node

    def _compile_lambda(self, node):
        """匿名函数 → 独立指令序列 + MAKE_CLOSURE（运行时捕获当前 Env）"""
        sub = Emitter(self._builtin_names)
        stmts = node.body
        implicit_tail = bool(stmts) and isinstance(stmts[-1], Expression)
        for stmt in (stmts[:-1] if implicit_tail else stmts):
            sub.compile_stmt(stmt)
        if implicit_tail:
            sub.compile_expr(stmts[-1])   # 隐式返回: 末表达式值留栈
        else:
            sub.emit(Op.LOAD_CONST, NoneValue())
        epilogue = sub.emit(Op.RET)
        for pos in sub._unwraps:
            sub.patch(pos, epilogue)
        meta = {
            'params': [p[0] for p in node.params],
            'code': sub.code,
            'name': getattr(node, 'name', '<lambda>'),
            'ast': node,
        }
        self.emit(Op.MAKE_CLOSURE, meta)

    def _compile_call(self, node):
        func = node.func
        if isinstance(func, MemberAccess):
            # 方法调用 obj.m(args) — 调度语义重在解释器, 整条委托
            self._delegate_expr(node)
            return
        # 可名前缀: Variable.name 或旧式 str
        name = None
        if isinstance(func, Variable):
            name = func.name
        elif isinstance(func, str):
            name = func
        if name is not None and name in self._builtin_names \
                and name not in self.functions:
            # builtin（或尚未定义的符号）— 解释器按 作用域→builtin 解析
            self._delegate_expr(node)
            return
        # 栈布局: [callee, arg1..argN]，CALL_VALUE 逆序弹参数再弹被调
        self.compile_expr(func)
        for arg in node.args:
            self.compile_expr(arg)
        self.emit(Op.CALL_VALUE, len(node.args))

    def _delegate_expr(self, node):
        pos = self.emit(Op.RUN_AST, (node, 'expr', None, None))
        self._record_flow(pos)

    def _delegate_stmt(self, node):
        pos = self.emit(Op.RUN_AST, (node, 'stmt', None, None))
        self._record_flow(pos)

    def _record_flow(self, pos: int):
        """RUN_AST 在循环体内时登记流控上下文（循环结束后回填出口）"""
        if self._loops:
            self._loops[-1]['flows'].append(pos)

    # ── 语句 ──
    def compile_stmt(self, node):
        if isinstance(node, VariableDecl):
            self.compile_expr(node.value)
            self.emit(Op.STORE_VAR, node.name)

        elif isinstance(node, Assignment):
            if node.op == '=':
                self.compile_expr(node.value)
                self.emit(Op.ASSIGN_VAR, node.target)
            else:
                # 复合赋值: x += v → LOAD_VAR x; <v>; ADD; ASSIGN_VAR x
                self.emit(Op.LOAD_VAR, node.target)
                self.compile_expr(node.value)
                op_map = {'+=': Op.ADD, '-=': Op.SUB, '*=': Op.MUL,
                          '/=': Op.DIV, '%=': Op.MOD}
                if node.op not in op_map:
                    self._delegate_stmt(node)
                    return
                self.emit(op_map[node.op])
                self.emit(Op.ASSIGN_VAR, node.target)

        elif isinstance(node, PrintStmt):
            for arg in node.args:
                self.compile_expr(arg)
            self.emit(Op.PRINT, len(node.args))

        elif isinstance(node, IfStmt):
            self.compile_expr(node.condition)
            jump_false = self.emit(Op.JUMP_IF_FALSE, None)
            for stmt in node.then_branch:
                self.compile_stmt(stmt)
            if node.else_branch:
                jump_end = self.emit(Op.JUMP, None)
                self.patch(jump_false, len(self.code))
                for stmt in node.else_branch:
                    self.compile_stmt(stmt)
                self.patch(jump_end, len(self.code))
            else:
                self.patch(jump_false, len(self.code))

        elif isinstance(node, WhileStmt):
            loop_start = len(self.code)
            self.compile_expr(node.condition)
            jump_false = self.emit(Op.JUMP_IF_FALSE, None)
            self._loops.append({'start': loop_start, 'breaks': [],
                                'continues': [], 'flows': []})
            for stmt in node.body:
                self.compile_stmt(stmt)
            loop = self._loops.pop()
            for cpos in loop['continues']:
                self.patch(cpos, loop['start'])
            self.emit(Op.JUMP, loop['start'])
            exit_addr = len(self.code)
            self.patch(jump_false, exit_addr)
            for bpos in loop['breaks']:
                self.patch(bpos, exit_addr)
            # 委托块的流控上下文: (循环起点, 循环出口)
            for fpos in loop['flows']:
                op, arg = self.code[fpos]
                self.code[fpos] = (op, (arg[0], arg[1], loop['start'], exit_addr))

        elif isinstance(node, BreakStmt):
            if not self._loops:
                self._delegate_stmt(node)
                return
            self._loops[-1]['breaks'].append(self.emit(Op.JUMP, None))

        elif isinstance(node, ContinueStmt):
            if not self._loops:
                self._delegate_stmt(node)
                return
            self._loops[-1]['continues'].append(self.emit(Op.JUMP, None))

        elif isinstance(node, ReturnStmt):
            if node.value is not None:
                self.compile_expr(node.value)
            else:
                self.emit(Op.LOAD_CONST, NoneValue())
            if self._ensures:
                # ensures: result 绑定返回值, 逐条验收, 违约跳违约块
                self.emit(Op.STORE_VAR, 'result')
                for ens in self._ensures:
                    self.compile_expr(ens)
                    self._contract_fails.append(
                        (self.emit(Op.JUMP_IF_FALSE, None), 'ensures'))
                self.emit(Op.LOAD_VAR, 'result')
            self.emit(Op.RET)

        elif isinstance(node, FunctionDef):
            self._compile_function_def(node)

        else:
            # match/类/with/for/try/import/generators... — 委托通道
            self._delegate_stmt(node)

    def _compile_function_def(self, node: FunctionDef):
        # 生成器 / 装饰器 / 泛型 / 默认参数 / async — 语义重在解释器, 整条声明委托
        if (node.is_generator or node.decorators or node.type_params
                or getattr(node, 'is_async', False)
                or any(p[2] is not None for p in node.params)):
            self._delegate_stmt(node)
            return

        sub = Emitter(self._builtin_names)
        sub._ensures = node.ensures
        # requires: 进门验收, 违约跳违约块（位于函数末尾 RET 之后, 兜底不可达）
        for req in node.requires:
            sub.compile_expr(req)
            sub._contract_fails.append(
                (sub.emit(Op.JUMP_IF_FALSE, None), 'requires'))
        # 隐式返回: 函数体末条为表达式时, 其值即返回值（与解释器对齐）
        stmts = node.body
        implicit_tail = bool(stmts) and isinstance(stmts[-1], Expression)
        for stmt in (stmts[:-1] if implicit_tail else stmts):
            sub.compile_stmt(stmt)
        if implicit_tail:
            sub.compile_expr(stmts[-1])
        else:
            sub.emit(Op.LOAD_CONST, NoneValue())
        if node.ensures:
            sub.emit(Op.STORE_VAR, 'result')
            for ens in node.ensures:
                sub.compile_expr(ens)
                sub._contract_fails.append(
                    (sub.emit(Op.JUMP_IF_FALSE, None), 'ensures'))
            sub.emit(Op.LOAD_VAR, 'result')
        epilogue = sub.emit(Op.RET)
        for pos in sub._unwraps:
            sub.patch(pos, epilogue)
        # 违约块: 每条 JUMP_IF_FALSE 各自指向一条 RAISE
        fn_label = f"def {node.name}"
        for pos, clause in sub._contract_fails:
            sub.patch(pos, len(sub.code))
            sub.emit(Op.RAISE,
                     f"契约违反: {clause} 条款未满足（{fn_label}）")
        meta = {
            'params': [p[0] for p in node.params],
            'code': sub.code,
            'name': node.name,
            'ast': node,
        }
        # 运行时: MAKE_CLOSURE 捕获当前 Env → STORE_VAR 绑定函数名
        self.emit(Op.MAKE_CLOSURE, meta)
        self.emit(Op.STORE_VAR, node.name)
        self.functions[node.name] = meta


def compile_program(ast, builtin_names=None) -> Emitter:
    """Program → Emitter（含主代码与函数表）

    与解释器行为对齐：顶层函数（含 main）经 MAKE_CLOSURE 绑定到全局
    环境；主代码末尾自动调用 main（无参函数约定）。
    """
    em = Emitter(builtin_names)
    # 先编译所有顶层函数（定义先于任何语句执行 — 与解释器注册顺序一致）
    for func in ast.functions.values():
        em.compile_stmt(func)
    for stmt in ast.statements:
        em.compile_stmt(stmt)
    # 自动调用 main（解释器约定的程序入口）
    if 'main' in ast.functions:
        em.emit(Op.LOAD_VAR, 'main')
        em.emit(Op.CALL_VALUE, 0)
        em.emit(Op.POP)
    em.emit(Op.LOAD_CONST, NoneValue())
    epilogue = em.emit(Op.RET)
    for pos in em._unwraps:
        em.patch(pos, epilogue)
    return em


# ── 栈式 VM ───────────────────────────────────────────
class Frame:
    """调用帧：被调代码 + 返回地址 + 调用方/被调方环境"""

    __slots__ = ('code', 'ret_ip', 'caller_env', 'env')

    def __init__(self, code, ret_ip, caller_env: Env, callee_env: Env):
        self.code = code
        self.ret_ip = ret_ip
        self.caller_env = caller_env
        self.env = callee_env


class VMClosure(FunctionValue):
    """VM 闭包：编译码 + 定义时环境。

    继承 FunctionValue 是有意为之——解释器侧调用分发零改动：
    解释器拿到它就按 func_def(AST) + closure(VMScope) 树遍历执行,
    语义与原生字节码路径一致。VM 侧优先走原生帧。
    """

    def __init__(self, meta: dict, env: Env):
        super().__init__(meta['ast'], env.scope)
        self.meta = meta
        self.env = env


class _VMReturn(Exception):
    """委托块内 return 的信号 — 把值递回 VM 调用链"""

    def __init__(self, value):
        self.value = value


class VM:
    """栈式虚拟机。V0.2: 全局环境 + 值栈 + 帧栈 + 环境链"""

    MAX_STEPS = 10_000_000  # 死循环熔断（fib(25) 约 400 万步量级）

    def __init__(self, emitter: Emitter, interpreter):
        self.main_code = emitter.code
        self.functions = emitter.functions
        self.interpreter = interpreter
        self._print = interpreter._builtin_print
        self.stack = []
        self.frames = []
        self.global_env = Env()
        self.env = self.global_env
        self._entry = (self.main_code, 0)
        # 桥接: 解释器的 global_scope 换成 VM 全局环境的适配器 —
        # 委托执行中的嵌套 import 沿作用域链能找到 VM 里的模块树
        for k, v in getattr(interpreter.global_scope, 'symbols', {}).items():
            self.global_env.vars.setdefault(k, v)
        interpreter.global_scope = self.global_env.scope

    # ── 变量: 环境链解析 ──
    def _resolve_var(self, name: str):
        env = self.env
        while env is not None:
            if name in env.vars:
                return env.vars[name]
            env = env.parent
        raise NameError(f"VM: 未定义的变量 '{name}'")

    def _assign_var(self, name: str, value):
        env = self.env
        while env is not None:
            if name in env.vars:
                env.vars[name] = value
                return
            env = env.parent
        raise NameError(f"VM: 未定义的变量 '{name}'")

    # ── 算术/比较 ──
    # Op → 源运算符（委托解释器 _binary_op 时用）
    _OP_TO_SRC = {
        Op.ADD: '+', Op.SUB: '-', Op.MUL: '*', Op.DIV: '/', Op.MOD: '%',
        Op.EQ: '==', Op.NE: '!=', Op.LT: '<', Op.LE: '<=',
        Op.GT: '>', Op.GE: '>=',
    }

    def _binary_values(self, left, op: str, right):
        """二元运算（值进值出）—_binary 的纯函数核心。

        主循环内联整型快路径的回退通道：对象运算/容器运算/字符串拼接
        等重情形走这里，与 _binary 同一份逻辑（零重复实现的镜像）。
        """
        # 对象运算（运算符重载 __add__/__eq__…）— 委托解释器, 零重复实现
        if isinstance(left, InstanceValue) or isinstance(right, InstanceValue):
            return self._delegate_binop(left, op, right)
        lv = left.value if isinstance(left, RuntimeValue) else left
        rv = right.value if isinstance(right, RuntimeValue) else right
        # 容器运算（与解释器对齐的常用子集）
        if op == Op.ADD and isinstance(left, ListValue) and isinstance(right, ListValue):
            return ListValue(left.value + right.value,
                             element_type=left.type.element_type)
        if op == Op.MUL and isinstance(left, ListValue) and isinstance(right, IntValue):
            return ListValue(left.value * int(right.value),
                             element_type=left.type.element_type)
        if op == Op.MUL and isinstance(left, IntValue) and isinstance(right, ListValue):
            return ListValue(int(left.value) * right.value,
                             element_type=right.type.element_type)
        if op == Op.ADD:
            # 字符串拼接（操作数是 str 或 StringValue 的值域）
            if isinstance(lv, str) or isinstance(rv, str):
                res = str(lv) + str(rv)
            else:
                res = lv + rv
        elif op == Op.SUB:
            res = lv - rv
        elif op == Op.MUL:
            res = lv * rv
        elif op == Op.DIV:
            res = lv / rv
        elif op == Op.MOD:
            res = lv % rv
        elif op == Op.EQ:
            res = lv == rv
        elif op == Op.NE:
            res = lv != rv
        elif op == Op.LT:
            res = lv < rv
        elif op == Op.LE:
            res = lv <= rv
        elif op == Op.GT:
            res = lv > rv
        elif op == Op.GE:
            res = lv >= rv
        else:
            raise RuntimeError(f"VM 未知二元运算: {op}")
        # 结果包回 RuntimeValue（int/float/bool/string）
        if isinstance(res, bool):
            return BoolValue(res)
        elif isinstance(res, int):
            return IntValue(res)
        elif isinstance(res, float):
            return FloatValue(res)
        else:
            return StringValue(res)

    def _binary(self, op: str):
        """栈式二元运算入口（保留供外部调用；主循环已内联快路径）"""
        right = self.stack.pop()
        left = self.stack.pop()
        self.stack.append(self._binary_values(left, op, right))

    # ── 委托通道 ──
    def _delegate_scope(self):
        return self.env.scope

    def _run_ast(self, node, kind: str):
        """RUN_AST: 把 AST 节点交给树遍历解释器, 共享当前环境"""
        interp = self.interpreter
        old_scope = interp.current_scope
        interp.current_scope = self._delegate_scope()
        try:
            if kind == 'expr':
                return interp.evaluate_expression(node)
            interp.execute_statement(node)
            return None
        finally:
            interp.current_scope = old_scope

    def _delegate_call(self, callee, args):
        """CALL_VALUE 的解釋器分支: FunctionValue/ClassValue 调度"""
        interp = self.interpreter
        old_scope = interp.current_scope
        interp.current_scope = self._delegate_scope()
        try:
            if isinstance(callee, ClassValue):
                return callee.call(interp, args)
            if isinstance(callee, FunctionValue):
                return interp.execute_function(callee, args)
            raise NameError(f"VM: 无法调用的值 {callee!r}")
        finally:
            interp.current_scope = old_scope

    def _delegate_binop(self, left, op: str, right):
        """对象运算符重载 — 委托解释器 _binary_op（同一份调度逻辑）"""
        interp = self.interpreter
        old_scope = interp.current_scope
        interp.current_scope = self._delegate_scope()
        try:
            return interp._binary_op(left, self._OP_TO_SRC.get(op, op), right)
        finally:
            interp.current_scope = old_scope

    def _enter_frame(self, closure: VMClosure, args, ret_ip: int):
        """VM 闭包调用: 以定义时环境为父层建新帧"""
        meta = closure.meta
        env = Env(parent=closure.env)
        for pname, pval in zip(meta['params'], args):
            env.vars[pname] = pval
        self.frames.append(Frame(meta['code'], ret_ip, self.env, env))
        return meta['code'], 0, env

    # ── 主循环 ──
    # V0.3 性能优化（T7）：热指令全部内联，消除逐指令的方法调用与
    # 属性查找——
    #   · 局部别名：stack/push/pop/frames/env/code/ip 全部驻留局部变量
    #   · 变量解析内联：LOAD_VAR/STORE_VAR/ASSIGN_VAR 直接走环境链
    #   · 整型快路径：双侧 IntValue 的算术/比较不再进 _binary 通用分发
    #   · 调用内联：argc≤1 的 VMClosure 调用免去列表构造与方法往返
    # 委托点（RUN_AST/_delegate_call）前同步 self.env，保证解释器侧
    # 看到的始终是当前环境；慢路径仍走原方法，语义逐位不变。
    def _execute_loop(self, code, ip):
        stack = self.stack
        push = stack.append
        pop = stack.pop
        frames = self.frames
        env = self.env
        main_code = self.main_code
        interp = self.interpreter
        # 热路径局部别名（全局查找 → 局部查找）
        _IntValue = IntValue
        _FloatValue = FloatValue
        _BoolValue = BoolValue
        _Env = Env
        _Frame = Frame
        _VMClosure = VMClosure
        _RuntimeValue = RuntimeValue
        steps = 0
        max_steps = self.MAX_STEPS
        code_len = len(code)

        while ip < code_len:
            steps += 1
            if steps > max_steps:
                raise RuntimeError(f"VM: 超过 {max_steps} 步，疑似死循环，已熔断")
            op, arg = code[ip]
            ip += 1

            if op == Op.LOAD_CONST:
                push(arg)
            elif op == Op.LOAD_VAR:
                e = env
                while e is not None:
                    v = e.vars
                    if arg in v:
                        push(v[arg])
                        break
                    e = e.parent
                else:
                    self.env = env
                    push(self._resolve_var(arg))
            elif op == Op.STORE_VAR:
                env.vars[arg] = pop()
            elif op == Op.JUMP:
                ip = arg
            elif op == Op.JUMP_IF_FALSE:
                cond = pop()
                if not (cond.value if isinstance(cond, _RuntimeValue) else cond):
                    ip = arg
            elif op in _ARITH_OPS:
                r = pop()
                l = pop()
                # 整型快路径：fib 类数值热点（bool 不是 IntValue 子类，
                # type() is 精确匹配不会误吞 BoolValue）
                if type(l) is _IntValue and type(r) is _IntValue:
                    lv = l.value
                    rv = r.value
                    if op == Op.ADD:
                        push(_IntValue(lv + rv))
                    elif op == Op.SUB:
                        push(_IntValue(lv - rv))
                    elif op == Op.MUL:
                        push(_IntValue(lv * rv))
                    elif op == Op.DIV:
                        push(_FloatValue(lv / rv))
                    elif op == Op.MOD:
                        push(_IntValue(lv % rv))
                    elif op == Op.EQ:
                        push(_BoolValue(lv == rv))
                    elif op == Op.NE:
                        push(_BoolValue(lv != rv))
                    elif op == Op.LT:
                        push(_BoolValue(lv < rv))
                    elif op == Op.LE:
                        push(_BoolValue(lv <= rv))
                    elif op == Op.GT:
                        push(_BoolValue(lv > rv))
                    else:
                        push(_BoolValue(lv >= rv))
                else:
                    push(self._binary_values(l, op, r))
            elif op == Op.CALL_VALUE:
                argc = arg
                if argc == 1:
                    a0 = pop()
                    callee = pop()
                    if type(callee) is _VMClosure:
                        meta = callee.meta
                        params = meta['params']
                        e = _Env(callee.env)
                        if len(params) == 1:
                            e.vars[params[0]] = a0
                        frames.append(_Frame(meta['code'], ip, env, e))
                        code = meta['code']
                        code_len = len(code)
                        ip = 0
                        env = e
                    else:
                        self.env = env
                        push(self._delegate_call(callee, [a0]))
                elif argc == 0:
                    callee = pop()
                    if type(callee) is _VMClosure:
                        meta = callee.meta
                        e = _Env(callee.env)
                        frames.append(_Frame(meta['code'], ip, env, e))
                        code = meta['code']
                        code_len = len(code)
                        ip = 0
                        env = e
                    else:
                        self.env = env
                        push(self._delegate_call(callee, []))
                else:
                    call_args = [pop() for _ in range(argc)][::-1]
                    callee = pop()
                    if isinstance(callee, _VMClosure):
                        code, ip, env = self._enter_frame(callee, call_args, ip)
                        code_len = len(code)
                    else:
                        self.env = env
                        push(self._delegate_call(callee, call_args))
            elif op == Op.RET:
                rv = pop()
                if frames:
                    frame = frames.pop()
                    env = frame.caller_env
                    code = frames[-1].code if frames else main_code
                    code_len = len(code)
                    ip = frame.ret_ip
                push(rv)
            elif op == Op.POP:
                pop()
            elif op == Op.NOT:
                v = pop()
                truth = v.value if isinstance(v, _RuntimeValue) else v
                push(_BoolValue(not truth))
            elif op == Op.MAKE_CLOSURE:
                push(_VMClosure(arg, env))
            elif op == Op.ASSIGN_VAR:
                val = pop()
                e = env
                while e is not None:
                    if arg in e.vars:
                        e.vars[arg] = val
                        break
                    e = e.parent
                else:
                    self.env = env
                    self._assign_var(arg, val)
            elif op == Op.PRINT:
                pargs = [pop() for _ in range(arg)][::-1]
                self._print(pargs)
            elif op == Op.RUN_AST:
                node, kind, _ls, _le = arg
                self.env = env
                val = self._run_ast(node, kind)
                # 流控标志回传（先于入栈, 避免跳转留下僵值）
                if interp.return_flag:
                    rv = interp.return_value
                    interp.return_flag = False
                    interp.return_value = None
                    raise _VMReturn(rv)
                if interp.break_flag:
                    interp.break_flag = False
                    if arg[3] is not None:
                        ip = arg[3]
                        continue
                elif interp.continue_flag:
                    interp.continue_flag = False
                    if arg[2] is not None:
                        ip = arg[2]
                        continue
                if kind == 'expr':
                    push(val)
            elif op == Op.UNWRAP_OK:
                v = pop()
                if isinstance(v, ResultValue):
                    if v.is_ok:
                        push(v.ok_value)
                    else:
                        push(v)
                        ip = arg   # Err → 跳函数末尾 RET, 提前返回
                else:
                    push(v)
            elif op == Op.RAISE:
                raise ContractViolation(arg)
            elif op == Op.CALL:
                # 兼容路径: 名字直调（函数表 → 全局环境）
                fname, argc = arg
                call_args = [pop() for _ in range(argc)][::-1]
                if fname in self.functions:
                    closure = _VMClosure(self.functions[fname], self.global_env)
                    code, ip, env = self._enter_frame(closure, call_args, ip)
                    code_len = len(code)
                else:
                    callee = self.global_env.vars.get(fname)
                    if callee is not None:
                        if isinstance(callee, _VMClosure):
                            code, ip, env = self._enter_frame(callee, call_args, ip)
                            code_len = len(code)
                        else:
                            self.env = env
                            push(self._delegate_call(callee, call_args))
                    else:
                        raise NameError(f"VM: 未定义的函数 '{fname}'")
            else:
                raise RuntimeError(f"VM 未知指令: {op}")

        self.env = env
        return stack[-1] if stack else NoneValue()

    def run(self) -> RuntimeValue:
        """执行到程序结束。委托块内的 return 经 _VMReturn 回传调用链。"""
        while True:
            try:
                return self._execute_loop(*self._entry)
            except _VMReturn as sig:
                if self.frames:
                    frame = self.frames.pop()
                    self.env = frame.caller_env
                    self.stack.append(sig.value)
                    parent = self.frames[-1] if self.frames else None
                    self._entry = (
                        (self.main_code if parent is None else parent.code),
                        frame.ret_ip,
                    )
                    continue
                self.stack.append(sig.value)
                return self.stack[-1]
