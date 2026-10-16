# intent_bytecode.py — 字节码编译器与栈式 VM（M10, V0.1 核心子集）
#
# 心学为体：AST 是意，字节码是言——言不尽意，但言可执行
# 禅道为翼：编译一次，执行多次；心不再每次都临场
# 马哲为用：同样的语义，从「每次现场解释」到「先沉淀后执行」
#
# V0.1 覆盖（刻意最小）：let/let mut、算术与比较运算、print、
# if/else、while、函数定义与调用、return。其余特性（闭包/管道/
# match/Result/契约/with/生成器）由 M11 逐轮扩展。
#
# 架构：
#   Emitter   AST → Instruction[]（带回填的跳转）
#   VM        栈式执行：值栈 + 调用帧（局部变量 + ip + 代码）

from mini_intent import (
    ASTNode, VariableDecl, Assignment, BinaryOp, UnaryOp, Literal, Variable,
    IfStmt, WhileStmt, FunctionDef, ReturnStmt, PrintStmt, CallExpr,
    IntValue, FloatValue, StringValue, BoolValue, NoneValue, RuntimeValue,
)


# ── 指令集 ────────────────────────────────────────────
# 每条指令 = (opcode: str, arg)，arg 含义随 opcode：
#   常量/变量操作: LOAD_CONST <值> | LOAD_VAR <名> | STORE_VAR <名>
#   算术/比较:     ADD SUB MUL DIV MOD EQ NE LT LE GT GE
#   控制流:        JUMP <addr> | JUMP_IF_FALSE <addr>（弹出栈顶）
#   函数:          CALL <参数个数> | RET
#   输出:          PRINT <参数个数>
#   栈:            POP
class Op:
    LOAD_CONST = "LOAD_CONST"
    LOAD_VAR = "LOAD_VAR"
    STORE_VAR = "STORE_VAR"
    ADD, SUB, MUL, DIV, MOD = "ADD", "SUB", "MUL", "DIV", "MOD"
    EQ, NE, LT, LE, GT, GE = "EQ", "NE", "LT", "LE", "GT", "GE"
    JUMP, JUMP_IF_FALSE = "JUMP", "JUMP_IF_FALSE"
    CALL, RET = "CALL", "RET"
    PRINT, POP = "PRINT", "POP"


# ── 发射器：AST → 指令序列 ────────────────────────────
class Emitter:
    """把 AST 编译为字节码。跳转目标用回填（先占位后补齐）"""

    def __init__(self):
        self.code = []            # List[Tuple[str, Any]]
        self.functions = {}       # 函数名 -> FunctionDef（供 VM 建帧）

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
            self.compile_expr(node.operand)
            # V0.1: 仅负号（其余一元运算 M11 扩展）
            self.emit(Op.LOAD_CONST, IntValue(0))
            self.emit(Op.SUB)
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
                raise NotImplementedError(f"字节码 V0.1 不支持运算符: {node.op}")
            self.emit(op)
        elif isinstance(node, CallExpr) and isinstance(node.func, Variable):
            # 函数调用作为表达式: 结果留栈
            for arg in node.args:
                self.compile_expr(arg)
            self.emit(Op.CALL, (node.func.name, len(node.args)))
        else:
            raise NotImplementedError(
                f"字节码 V0.1 不支持表达式: {type(node).__name__}（M11 扩展）")

    # ── 语句 ──
    def compile_stmt(self, node):
        if isinstance(node, VariableDecl):
            self.compile_expr(node.value)
            self.emit(Op.STORE_VAR, node.name)

        elif isinstance(node, Assignment):
            if node.op == '=':
                self.compile_expr(node.value)
                self.emit(Op.STORE_VAR, node.target)
            else:
                # 复合赋值: x += v → LOAD_VAR x; <v>; ADD; STORE_VAR x
                self.emit(Op.LOAD_VAR, node.target)
                self.compile_expr(node.value)
                op_map = {'+=': Op.ADD, '-=': Op.SUB, '*=': Op.MUL, '/=': Op.DIV}
                self.emit(op_map[node.op])
                self.emit(Op.STORE_VAR, node.target)

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
            for stmt in node.body:
                self.compile_stmt(stmt)
            self.emit(Op.JUMP, loop_start)
            self.patch(jump_false, len(self.code))

        elif isinstance(node, ReturnStmt):
            if node.value is not None:
                self.compile_expr(node.value)
            else:
                self.emit(Op.LOAD_CONST, NoneValue())
            self.emit(Op.RET)

        elif isinstance(node, FunctionDef):
            # 函数体编译为独立指令序列，存入函数表
            sub = Emitter()
            for stmt in node.body:
                sub.compile_stmt(stmt)
            # 函数末尾兜底 RET（无显式 return）
            sub.emit(Op.LOAD_CONST, NoneValue())
            sub.emit(Op.RET)
            sub.functions = self.functions
            self.functions[node.name] = {
                'params': [p[0] for p in node.params],
                'code': sub.code,
                'emitter': sub,
            }

        elif isinstance(node, CallExpr) and isinstance(node.func, Variable):
            # 顶层裸调用语句（如 foo(1);）——V0.1 仅支持直接函数名调用
            for arg in node.args:
                self.compile_expr(arg)
            self.emit(Op.CALL, (node.func.name, len(node.args)))
            self.emit(Op.POP)  # 调用结果丢弃

        else:
            raise NotImplementedError(
                f"字节码 V0.1 不支持语句: {type(node).__name__}（M11 扩展）")


def compile_program(ast) -> Emitter:
    """Program → Emitter（含主代码与函数表）

    与解释器行为对齐：顶层函数（含 main）进函数表；
    主代码末尾自动调用 main（无参函数约定）。
    """
    em = Emitter()
    # 先编译所有顶层函数（FunctionDef 经 compile_stmt 进函数表）
    for func in ast.functions.values():
        em.compile_stmt(func)
    for stmt in ast.statements:
        em.compile_stmt(stmt)
    # 自动调用 main（解释器约定的程序入口）
    if 'main' in em.functions:
        em.emit(Op.CALL, ('main', 0))
        em.emit(Op.POP)
    em.emit(Op.LOAD_CONST, NoneValue())
    em.emit(Op.RET)
    return em


# ── 栈式 VM ───────────────────────────────────────────
class Frame:
    """调用帧：局部变量 + 返回地址 + 归属代码"""

    def __init__(self, code, ret_ip, locals_dict):
        self.code = code
        self.ip = 0
        self.ret_ip = ret_ip
        self.locals = locals_dict


class VM:
    """栈式虚拟机。V0.1: 全局函数表 + 值栈 + 帧栈"""

    MAX_STEPS = 1_000_000  # 死循环熔断

    def __init__(self, emitter: Emitter, builtins_print):
        self.main_code = emitter.code
        self.functions = emitter.functions
        self.stack = []
        self.frames = []
        self._print = builtins_print
        self.globals = {}

    def _resolve_var(self, name):
        # 帧局部优先，回退全局
        if self.frames and name in self.frames[-1].locals:
            return self.frames[-1].locals[name]
        if name in self.globals:
            return self.globals[name]
        raise NameError(f"VM: 未定义的变量 '{name}'")

    def _store_var(self, name, value):
        if self.frames:
            self.frames[-1].locals[name] = value
        else:
            self.globals[name] = value

    def _binary(self, op: str):
        right = self.stack.pop()
        left = self.stack.pop()
        lv = left.value if isinstance(left, RuntimeValue) else left
        rv = right.value if isinstance(right, RuntimeValue) else right
        if op == Op.ADD:
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
            self.stack.append(BoolValue(res))
        elif isinstance(res, int):
            self.stack.append(IntValue(res))
        elif isinstance(res, float):
            self.stack.append(FloatValue(res))
        else:
            self.stack.append(StringValue(res))

    def run(self) -> RuntimeValue:
        code = self.main_code
        ip = 0
        steps = 0
        while ip < len(code):
            steps += 1
            if steps > self.MAX_STEPS:
                raise RuntimeError(f"VM: 超过 {self.MAX_STEPS} 步，疑似死循环，已熔断")
            op, arg = code[ip]
            ip += 1

            if op == Op.LOAD_CONST:
                self.stack.append(arg)
            elif op == Op.LOAD_VAR:
                self.stack.append(self._resolve_var(arg))
            elif op == Op.STORE_VAR:
                self._store_var(arg, self.stack.pop())
            elif op in (Op.ADD, Op.SUB, Op.MUL, Op.DIV, Op.MOD,
                        Op.EQ, Op.NE, Op.LT, Op.LE, Op.GT, Op.GE):
                self._binary(op)
            elif op == Op.JUMP:
                ip = arg
            elif op == Op.JUMP_IF_FALSE:
                cond = self.stack.pop()
                if not (cond.value if isinstance(cond, RuntimeValue) else cond):
                    ip = arg
            elif op == Op.PRINT:
                args = [self.stack.pop() for _ in range(arg)][::-1]
                self._print(args)
            elif op == Op.POP:
                self.stack.pop()
            elif op == Op.CALL:
                fname, argc = arg
                fn_args = [self.stack.pop() for _ in range(argc)][::-1]
                if fname not in self.functions:
                    raise NameError(f"VM: 未定义的函数 '{fname}'")
                fn = self.functions[fname]
                locals_dict = {}
                for pname, pval in zip(fn['params'], fn_args):
                    locals_dict[pname] = pval
                self.frames.append(Frame(fn['code'], ip, locals_dict))
                code = fn['code']
                ip = 0
            elif op == Op.RET:
                ret_val = self.stack.pop()
                if self.frames:
                    frame = self.frames.pop()
                    code = self.main_code if not self.frames else self.frames[-1].code
                    ip = frame.ret_ip
                self.stack.append(ret_val)
            else:
                raise RuntimeError(f"VM 未知指令: {op}")

        return self.stack[-1] if self.stack else NoneValue()
