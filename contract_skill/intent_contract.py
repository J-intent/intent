#!/usr/bin/env python3
"""
Intent Contract Engine — 独立契约验证器

从 Intent 语言契约系统中提取的核心模块。
支持 Python 代码的 @requires / @ensures 注释契约。

用法：
    python3 intent_contract.py <file.py>          # 验证单个文件
    python3 intent_contract.py <file.py> --watch  # 持续监控
    python3 intent_contract.py --generate <func>  # 从函数签名生成契约模板

契约格式（注释中）：
    # @requires: x > 0
    # @ensures: result == x * 2
    def double(x: int) -> int:
        return x * 2

设计哲学：
    "进门前签合同（requires），出门前验货（ensures）"
    — Intent 语言契约系统
"""

import ast
import sys
import os
import re
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 安全的 eval 环境
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SAFE_BUILTINS = {
    "__builtins__": {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "enumerate": enumerate,
        "float": float,
        "int": int,
        "isinstance": isinstance,
        "len": len,
        "list": list,
        "max": max,
        "min": min,
        "range": range,
        "round": round,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "True": True,
        "False": False,
        "None": None,
    }
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 契约解析器
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class Contract:
    """单个函数的契约"""
    func_name: str
    requires: List[str] = field(default_factory=list)
    ensures: List[str] = field(default_factory=list)
    line: int = 0
    file: str = ""

    def is_empty(self) -> bool:
        return not self.requires and not self.ensures

    def summary(self) -> str:
        parts = []
        if self.requires:
            parts.append(f"    requires: {' AND '.join(self.requires)}")
        if self.ensures:
            parts.append(f"    ensures:  {' AND '.join(self.ensures)}")
        return f"  {self.func_name}:\n" + "\n".join(parts) if parts else f"  {self.func_name}: (无契约)"


def parse_contracts(source: str, filename: str = "") -> List[Contract]:
    """从 Python 源码中提取所有 @requires/@ensures 契约"""
    contracts = []
    lines = source.split('\n')

    def find_func_name(line_num: int) -> Optional[str]:
        """找到第 line_num 行之后第一个函数定义"""
        for i in range(line_num, len(lines)):
            stripped = lines[i].strip()
            # async def / def
            m = re.match(r'(?:async\s+)?def\s+(\w+)\s*\(', stripped)
            if m:
                return m.group(1)
            # class 方法
            m = re.match(r'\s*def\s+(\w+)\s*\(', stripped)
            if m:
                return m.group(1)
            # 最多找10行
            if i - line_num > 10:
                return None
        return None

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith('# @requires:') or stripped.startswith('# @ensures:'):
            contract = Contract(
                func_name="",
                line=i + 1,
                file=filename
            )

            # 收集所有连续的契约注释
            while i < len(lines):
                stripped = lines[i].strip()
                m_req = re.match(r'# @requires:\s*(.+)', stripped)
                m_ens = re.match(r'# @ensures:\s*(.+)', stripped)

                if m_req:
                    contract.requires.append(m_req.group(1).strip())
                elif m_ens:
                    contract.ensures.append(m_ens.group(1).strip())
                elif stripped.startswith('#'):
                    # 普通注释，跳过
                    pass
                else:
                    break
                i += 1

            # 找到紧邻的函数定义
            func_name = find_func_name(i)
            if func_name:
                contract.func_name = func_name

            if not contract.is_empty():
                contracts.append(contract)
        else:
            i += 1

    return contracts


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 契约验证器
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ContractViolation(Exception):
    """契约违反异常"""
    def __init__(self, func_name: str, condition: str, kind: str, actual: Any = None):
        self.func_name = func_name
        self.condition = condition
        self.kind = kind  # 'requires' or 'ensures'
        self.actual = actual
        icon = "[REQ]" if kind == "requires" else "[ENS]"
        msg = f"{icon} {func_name}: contract violation -- {kind}: {condition}"
        if actual is not None:
            msg += f" (实际值: {actual})"
        super().__init__(msg)


def verify_contract(source: str, contract: Contract, verbose: bool = False) -> List[str]:
    """
    验证单个契约：
    1. 解析函数的 AST
    2. 对 requires 条件：生成参数满足 requires 的测试输入，验证函数不崩溃
    3. 对 ensures 条件：用参数和 result 求值 ensures 表达式
    """
    errors = []

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [f"语法错误: {e}"]

    # 找到对应的函数节点
    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == contract.func_name:
                func_node = node
                break

    if func_node is None:
        return [f"未找到函数: {contract.func_name}"]

    # 提取函数代码并执行
    func_lines = source.split('\n')
    try:
        # 执行源码，获取函数对象
        ns: Dict[str, Any] = {}
        exec(source, ns)
        func = ns.get(contract.func_name)
        if func is None:
            return [f"无法加载函数: {contract.func_name}"]
    except Exception as e:
        return [f"加载函数失败: {e}"]

    # 解析参数名
    arg_names = [arg.arg for arg in func_node.args.args]

    # 生成测试输入：从 requires 条件推断参数值
    # 简单策略：尝试整数值 0..10 的组合
    test_cases = _generate_test_inputs(arg_names, contract.requires, ns)
    if not test_cases:
        # 默认：尝试几个常见值
        test_cases = _default_test_inputs(arg_names)

    ns_local = ns.copy()

    for args in test_cases[:20]:  # 最多测20组
        try:
            result = func(*args)
        except Exception as e:
            errors.append(f"[REQ] {contract.func_name}({_fmt_args(args)}): requires 违反 — 函数崩溃: {e}")
            continue

        # 验证 ensures
        verify_ns = ns_local.copy()
        verify_ns['result'] = result
        for name, val in zip(arg_names, args):
            verify_ns[name] = val

        for condition in contract.ensures:
            try:
                ok = eval(condition, SAFE_BUILTINS, verify_ns)
                if not ok:
                    errors.append(
                        f"[ENS] {contract.func_name}({_fmt_args(args)}): "
                        f"ensures violation — {condition} (result={result})"
                    )
            except Exception as e:
                errors.append(
                    f"[ENS] {contract.func_name}({_fmt_args(args)}): "
                    f"ensures '{condition}' eval failed — {e}"
                )

        if verbose and not errors:
            print(f"  [OK] {contract.func_name}({_fmt_args(args)}) = {result}")

    return errors


def _generate_test_inputs(
    arg_names: List[str],
    requires: List[str],
    ns: Dict[str, Any]
) -> List[List[Any]]:
    """从 requires 条件推断测试输入"""
    inputs = []
    for val in [0, 1, 2, 5, -1, -5]:
        # 对单参数函数尝试这些值
        args = [val for _ in arg_names]
        # 检查 requires
        try:
            verify_ns = ns.copy()
            for name, v in zip(arg_names, args):
                verify_ns[name] = v
            all_ok = all(
                eval(cond, SAFE_BUILTINS, verify_ns)
                for cond in requires
            )
            if all_ok:
                inputs.append(args)
        except Exception:
            pass
    return inputs


def _default_test_inputs(arg_names: List[str]) -> List[List[Any]]:
    """无 requires 时默认测试输入"""
    inputs = []
    for val in [0, 1, 2, 5, 10, -1, 100]:
        inputs.append([val for _ in arg_names])
    return inputs


def _fmt_args(args: List[Any]) -> str:
    return ", ".join(repr(a) for a in args)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 契约模板生成器
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_contract_template(source: str) -> str:
    """从 Python 源码生成契约注释模板"""
    tree = ast.parse(source)
    results = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('_') and node.name != '__init__':
                continue

            args = []
            for arg in node.args.args:
                name = arg.arg
                if name == 'self':
                    continue
                if arg.annotation:
                    args.append(f"{name}: {ast.unparse(arg.annotation)}")
                else:
                    args.append(name)

            # 推测可能的 requires
            hints = []
            for arg_name in [a.arg for a in node.args.args if a.arg != 'self']:
                hints.append(f"# @requires: {arg_name} > 0  # ← 替换为实际条件")

            # 推测可能的 ensures
            if node.returns:
                ret_type = ast.unparse(node.returns)
                hints.append(f"# @ensures: isinstance(result, {ret_type})  # ← 替换为实际保证")
            else:
                hints.append(f"# @ensures: result is not None  # ← 替换为实际保证")

            header = f"def {node.name}({', '.join(args)}):"
            results.append(f"# {'─'*50}")
            results.append(f"# {header}")
            results.extend(hints)
            results.append(f"# {'─'*50}")
            results.append("")

    return "\n".join(results) if results else "# 文件中未找到函数定义"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    parser = argparse.ArgumentParser(
        description="Intent Contract Engine — 独立契约验证器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s my_code.py             验证 my_code.py 中的所有契约
  %(prog)s .                       验证当前目录所有 Python 文件
  %(prog)s --generate my_code.py   生成契约模板
        """
    )
    parser.add_argument('target', nargs='?', help='文件或目录')
    parser.add_argument('--generate', '-g', action='store_true', help='生成契约模板')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--json', '-j', action='store_true', help='JSON 格式输出')
    args = parser.parse_args()

    if args.generate:
        if not args.target:
            print("错误: --generate 需要指定目标文件")
            sys.exit(1)
        source = Path(args.target).read_text(encoding='utf-8')
        template = generate_contract_template(source)
        print(template)
        return

    # 默认：验证
    if not args.target:
        parser.print_help()
        return

    target = Path(args.target)
    files = []
    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = sorted(target.rglob("*.py"))
    else:
        print(f"错误: 路径不存在 — {target}")
        sys.exit(1)

    total_contracts = 0
    total_violations = 0

    for filepath in files:
        try:
            source = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"[WARN]️  无法读取 {filepath}: {e}")
            continue

        contracts = parse_contracts(source, str(filepath))

        if not contracts:
            continue

        if args.verbose:
            print(f"\n[File] {filepath}")

        for contract in contracts:
            total_contracts += 1
            if args.verbose:
                print(contract.summary())

            errors = verify_contract(source, contract, verbose=args.verbose)
            if errors:
                total_violations += len(errors)
                for err in errors:
                    print(f"  [FAIL] {err}")

    # 摘要
    if total_contracts == 0:
        print("[NONE] 未找到 @requires/@ensures 契约注释")
        print("   提示: 用 --generate 生成模板")
    else:
        if total_violations == 0:
            print(f"\n[PASS] {total_contracts} contracts verified")
        else:
            print(f"\n[FAIL] {total_violations} violations ({total_contracts} contracts)")
            sys.exit(1)


if __name__ == '__main__':
    main()
