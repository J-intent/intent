#!/usr/bin/env python3
"""tools/intent_py.py — Python 调用 Intent 模块（I2b: 共生期反向桥）

用途
  Intent 侧已能 `import python.X`（I2a）。本工具提供反方向：Python 侧
  直接加载一个 .intent 文件，并把其中的顶层 `def` 暴露成普通 Python
  可调用对象，参数/返回值自动在 Python 原生类型与 Intent RuntimeValue
  之间转换。

用法（作为库）
    from tools.intent_py import load

    m = load("examples/hello.intent")
    print(m.add(1, 2))          # Intent 函数当 Python 函数调

  支持的参数/返回值：int / float / str / bool / None / list / dict。
  顶层 let/const 会在 load() 时执行（模块初始化），函数内可正常引用。

用法（命令行自检）
    python tools/intent_py.py --selftest

  自检会在临时目录生成演示模块，覆盖：整数加法、字符串拼接（依赖顶层
  常量）、列表求和（带 requires 契约）、参数个数/类型错误、契约违约。

错误口径
  - 加载/解析/模块初始化失败 → IntentLoadError
  - 调用边界（参数个数、类型、关键字参数）→ IntentCallError
  - Intent 侧 requires/ensures 违约 → IntentContractError（消息原样保留）
  - 其余 Intent 运行时错误 → IntentCallError（消息原样保留，cause 链到原异常）

退出码：--selftest 全通 0，失败 1。
"""

import os
import sys
import tempfile
import traceback

# ── 定位解释器源码（本工具位于 <project>/tools/）────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT = os.path.dirname(_HERE)
_SRC = os.path.join(_PROJECT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import mini_intent as _mi  # noqa: E402


# ── 异常体系 ────────────────────────────────────────────────

class IntentBridgeError(RuntimeError):
    """反向桥错误的基类。"""


class IntentLoadError(IntentBridgeError):
    """加载/解析/模块初始化失败。"""


class IntentCallError(IntentBridgeError):
    """调用边界错误：参数个数、参数类型、返回值不可转换等。"""


class IntentContractError(IntentBridgeError):
    """Intent 契约违约（requires/ensures）。

    `clause` 保留违约子句（"requires" / "ensures"），消息与 Intent 侧一致。
    """

    def __init__(self, message: str, clause: str = ""):
        super().__init__(message)
        self.clause = clause


# ── 值转换 ──────────────────────────────────────────────────

def _to_intent(value, where: str):
    """Python 原生值 → Intent RuntimeValue（桥入参）

    标量/列表/字典/None 自动转换；其余类型显式拒绝，不静默降级。
    """
    if value is None:
        return _mi.NoneValue()
    # bool 必须先于 int：Python 中 bool 是 int 的子类
    if isinstance(value, bool):
        return _mi.BoolValue(value)
    if isinstance(value, int):
        return _mi.IntValue(value)
    if isinstance(value, float):
        return _mi.FloatValue(value)
    if isinstance(value, str):
        return _mi.StringValue(value)
    if isinstance(value, (list, tuple)):
        return _mi.ListValue([_to_intent(item, f"{where}[{i}]")
                              for i, item in enumerate(value)])
    if isinstance(value, dict):
        entries = {}
        for key, item in value.items():
            if isinstance(key, bool):
                entries[key] = _to_intent(item, f"{where}[{key!r}]")
            elif isinstance(key, (int, float, str)):
                entries[key] = _to_intent(item, f"{where}[{key!r}]")
            else:
                raise IntentCallError(
                    f"参数 {where} 的字典键类型 {type(key).__name__} 不受支持"
                    "（仅支持 str/int/float/bool）")
        return _mi.DictValue(entries)
    raise IntentCallError(
        f"参数 {where} 的类型 {type(value).__name__} 不受支持"
        "（支持 int/float/str/bool/None/list/dict）")


def _to_python(value, where: str = "返回值"):
    """Intent RuntimeValue → Python 原生值（桥返回值）"""
    if isinstance(value, _mi.NoneValue):
        return None
    if isinstance(value, (_mi.IntValue, _mi.FloatValue,
                          _mi.StringValue, _mi.BoolValue)):
        return value.value
    if isinstance(value, _mi.ListValue):
        return [_to_python(item, f"{where} 的元素") for item in value.value]
    if isinstance(value, _mi.DictValue):
        return {key: _to_python(item, f"{where}[{key!r}]")
                for key, item in value.value.items()}
    # I2a 桥对象：还原为原始 Python 对象
    if isinstance(value, _mi.PyObjectValue):
        return value.obj
    if isinstance(value, _mi.RuntimeValue):
        raise IntentCallError(
            f"{where} 的类型 {value.get_type().name} 无法转换为 Python 原生值"
            "（支持 int/float/str/bool/None/list/dict）")
    return value


# ── 单个函数包装 ────────────────────────────────────────────

class IntentFunction:
    """一个 Intent 顶层函数的 Python 可调用包装。

    调用语义：
      1. 校验参数个数（含默认值区间），拒绝关键字参数；
      2. Python 值 → Intent RuntimeValue；
      3. interp.execute_function 执行（requires/ensures 照常生效）；
      4. Intent 返回值 → Python 原生值。
    """

    def __init__(self, module: "IntentModule", func_def, interp):
        self._module = module
        self._func_def = func_def
        self._interp = interp
        self.__name__ = func_def.name
        self.__qualname__ = func_def.name
        self.__doc__ = self._build_doc(func_def)

    @staticmethod
    def _build_doc(func_def) -> str:
        params = ", ".join(
            f"{name}: {decl}" if decl else name
            for name, decl, _default in func_def.params)
        ret = f" -> {func_def.return_type}" if func_def.return_type else ""
        lines = [f"Intent 函数 {func_def.name}({params}){ret}"]
        for cond in getattr(func_def, "requires", None) or []:
            lines.append(f"  requires: {_expr_text(cond)}")
        for cond in getattr(func_def, "ensures", None) or []:
            lines.append(f"  ensures: {_expr_text(cond)}")
        return "\n".join(lines)

    @property
    def params(self):
        """形参描述 [(name, type, default_expr_or_None), ...]"""
        return list(self._func_def.params)

    def _check_arity(self, args) -> None:
        params = self._func_def.params
        required = sum(1 for p in params if len(p) < 3 or p[2] is None)
        total = len(params)
        got = len(args)
        if required == total:
            expected = f"{total}"
        else:
            expected = f"{required}~{total}"
        if got < required or got > total:
            raise IntentCallError(
                f"调用 {self.__name__} 参数个数不符：期望 {expected} 个，得到 {got} 个"
                f"（形参：{', '.join(p[0] for p in params) or '无'}）")

    def __call__(self, *args, **kwargs):
        if kwargs:
            raise IntentCallError(
                f"调用 {self.__name__} 不接受关键字参数"
                f"（收到：{', '.join(kwargs)}）；请按位置传参")
        self._check_arity(args)

        intent_args = []
        for i, arg in enumerate(args):
            pname = self._func_def.params[i][0]
            intent_args.append(_to_intent(arg, f"'{pname}'（{self.__name__} 第 {i + 1} 个参数）"))

        interp = self._interp
        # 宿主调用没有外层 Intent 调用点：行号归零，让错误定位落到函数定义行
        interp.current_line = 0
        interp.current_col = 0
        try:
            result = interp.execute_function(self._func_def, intent_args)
        except _mi.ContractViolation as exc:
            raise IntentContractError(
                str(exc), clause=getattr(exc, "clause", "") or "") from exc
        except _mi.IntentError as exc:
            raise IntentCallError(str(exc)) from exc
        except Exception as exc:  # noqa: BLE001 — 桥边界统一翻译为可捕获的调用错误
            raise IntentCallError(
                f"调用 {self.__name__} 失败：{exc}") from exc
        finally:
            # 参数绑定阶段抛错时解释器可能停在函数作用域；统一回到全局，
            # 保证下一次调用看到的是同一份模块状态。
            interp.current_scope = interp.global_scope
            interp.return_flag = False
            interp.return_value = None
            interp.current_filename = self._module.path

        return _to_python(result, f"{self.__name__} 的返回值")

    def __repr__(self):
        return f"<IntentFunction {self.__name__} from {self._module.path}>"


def _expr_text(expr) -> str:
    """契约表达式的简短文本（仅供文档字符串展示）。"""
    text = getattr(expr, "raw", None) or getattr(expr, "source", None)
    if text:
        return text
    return repr(expr)


# ── 模块包装 ────────────────────────────────────────────────

class IntentModule:
    """已加载的 Intent 模块。

    - 顶层 def 作为属性访问，返回可调用对象；
    - `.functions` 是 {名字: IntentFunction}；
    - `.name` / `.path` 记录来源；
    - `__getattr__` 命中缺失函数时给出可用函数列表。
    """

    def __init__(self, path: str, interp, functions: dict):
        self.path = path
        self.name = os.path.splitext(os.path.basename(path))[0]
        self._interp = interp
        self.functions = functions

    def __getattr__(self, name):
        functions = self.__dict__.get("functions", {})
        if name in functions:
            return functions[name]
        available = ", ".join(sorted(functions)) or "（无顶层函数）"
        raise AttributeError(
            f"Intent 模块 {self.__dict__.get('path', '?')} 没有顶层函数 "
            f"{name!r}；可用：{available}")

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(self.functions))

    def __repr__(self):
        return (f"<IntentModule {self.name!r} "
                f"functions={sorted(self.functions)}>")


# ── 加载入口 ────────────────────────────────────────────────

def load(path: str) -> IntentModule:
    """加载 .intent 文件并返回 IntentModule。

    顶层 let/const 立即执行（模块初始化）；顶层 def 不执行，只注册。
    main 不会自动运行（module_mode=True）。
    """
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise IntentLoadError(f"Intent 模块不存在：{path}")

    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            code = fh.read()
    except OSError as exc:
        raise IntentLoadError(f"读取 Intent 模块失败：{path}：{exc}") from exc

    try:
        lexer = _mi.Lexer(code, path)
        tokens = lexer.tokenize()
        parser = _mi.Parser(tokens, code)
        program = parser.parse()
        if parser.errors:
            first = parser.errors[0]
            raise IntentLoadError(f"Intent 语法错误：{path}：{first}")
    except IntentLoadError:
        raise
    except _mi.IntentError as exc:
        raise IntentLoadError(f"Intent 解析失败：{path}：{exc}") from exc
    except Exception as exc:
        raise IntentLoadError(f"Intent 解析失败：{path}：{exc}") from exc

    interp = _mi.Interpreter()
    interp.cli_args = []
    interp.current_filename = path
    # 模块内的 import std.x / import 相对包以文件所在目录为根
    file_dir = os.path.dirname(path)
    interp.current_file_dir = file_dir
    for candidate in (file_dir, os.path.join(_PROJECT, "std"),
                      os.path.join(_PROJECT, "lib")):
        if candidate not in interp.module_search_paths:
            interp.module_search_paths.insert(0, candidate)

    try:
        interp.execute_program(program, module_mode=True)
    except _mi.ContractViolation as exc:
        raise IntentContractError(
            f"模块 {path} 初始化契约违约：{exc}",
            clause=getattr(exc, "clause", "") or "") from exc
    except _mi.IntentError as exc:
        raise IntentLoadError(f"模块 {path} 初始化失败：{exc}") from exc
    except Exception as exc:
        raise IntentLoadError(f"模块 {path} 初始化失败：{exc}") from exc

    module = IntentModule(path, interp, {})
    for name, func_def in program.functions.items():
        # 装饰器可能在注册期替换实现，优先用解释器函数表的最终版本
        effective = interp.functions.get(name, func_def)
        module.functions[name] = IntentFunction(module, effective, interp)
    return module


# ── 自检 ────────────────────────────────────────────────────

_DEMO_SOURCE = '''// I2b 反向桥演示模块：Python 调用 Intent
// 顶层常量在 load() 时执行（模块初始化），函数体引用它验证初始化顺序。

const SUFFIX = "!";

def add(a: Int, b: Int): Int {
    return a + b;
};

def concat(a: String, b: String): String {
    return a + b + SUFFIX;
};

def sum_list(xs: List[Int]): Int requires len(xs) > 0 {
    let mut total = 0;
    for x in xs {
        total = total + x;
    };
    return total;
};
'''


def _selftest() -> int:
    """端到端自检：生成临时 Intent 模块 → Python 侧调用 → 断言。"""
    checks = []

    def check(label, fn):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 — 自检要报告全部失败
            checks.append((label, False, f"{type(exc).__name__}: {exc}"))
            traceback.print_exc()
        else:
            checks.append((label, True, ""))
            print(f"  ok  {label}")

    with tempfile.TemporaryDirectory(prefix="intent_py_") as tmp:
        module_path = os.path.join(tmp, "demo_module.intent")
        with open(module_path, "w", encoding="utf-8") as fh:
            fh.write(_DEMO_SOURCE)

        print(f"[selftest] 演示模块：{module_path}")
        mod = load(module_path)
        print(f"[selftest] 已加载：{mod!r}")

        check("顶层函数暴露为 Python 属性",
              lambda: _eq(sorted(mod.functions), ["add", "concat", "sum_list"]))
        check("加法：mod.add(2, 3) == 5", lambda: _eq(mod.add(2, 3), 5))
        check("顶层 const 初始化：mod.concat('In', 'tent') == 'Intent!'",
              lambda: _eq(mod.concat("In", "tent"), "Intent!"))
        check("列表往返：mod.sum_list([1, 2, 3, 4]) == 10",
              lambda: _eq(mod.sum_list([1, 2, 3, 4]), 10))

        check("参数个数不符报 IntentCallError",
              lambda: _expect_error(lambda: mod.add(1), IntentCallError,
                                    contains="参数个数不符"))
        check("参数类型不符报 IntentCallError",
              lambda: _expect_error(lambda: mod.add("1", 2), IntentCallError,
                                    contains="类型不匹配"))
        check("不支持的关键字参数显式报错",
              lambda: _expect_error(lambda: mod.add(a=1, b=2), IntentCallError,
                                    contains="关键字参数"))
        check("requires 违约被 Python 侧捕获",
              lambda: _expect_error(lambda: mod.sum_list([]), IntentContractError,
                                    contains="requires"))

    failed = [c for c in checks if not c[1]]
    print()
    if failed:
        print(f"[selftest] 失败 {len(failed)}/{len(checks)}：")
        for label, _ok, msg in failed:
            print(f"  FAIL {label} — {msg}")
        return 1

    print(f"[selftest] 全部通过 {len(checks)}/{len(checks)}")
    print("round-trip OK: Python -> Intent 模块（含顶层初始化与契约违约路径）")
    return 0


def _eq(actual, expected) -> None:
    if actual != expected:
        raise AssertionError(f"期望 {expected!r}，实际 {actual!r}")


def _expect_error(fn, exc_type, contains: str = "") -> None:
    try:
        fn()
    except exc_type as exc:
        if contains and contains not in str(exc):
            raise AssertionError(
                f"异常消息缺少 {contains!r}：{exc}") from exc
        return
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(
            f"期望 {exc_type.__name__}，实际 {type(exc).__name__}: {exc}") from exc
    raise AssertionError(f"期望抛出 {exc_type.__name__}，实际正常返回")


# ── 入口 ────────────────────────────────────────────────────

def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if "--selftest" in sys.argv[1:]:
        return _selftest()

    print("tools/intent_py.py — Python 调用 Intent 模块（I2b 反向桥）")
    print()
    print("用法（库）：")
    print("  from tools.intent_py import load")
    print("  m = load('path/to/module.intent')")
    print("  m.some_function(1, 2)")
    print()
    print("用法（自检）：")
    print("  python tools/intent_py.py --selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
