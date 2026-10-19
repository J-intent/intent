#!/usr/bin/env python
# tools/infer_selftest.py — L3a 局部类型推断自测
#
# 纯静态特性不能用 .intent 运行时测试当判定（测不到编译期行为）——
# 本工具直接驱动 TypeChecker，断言无标注变量的推断结果，
# 以及「推断结果参与标注处检查」的正反例。
#
# 用法：
#   python tools/infer_selftest.py           局部推断用例
#   python tools/infer_selftest.py --returns L3b 返回推断用例（未实现则失败）
#
# 判定口径：
#   推断用例：期望的 {变量名: 类型} 必须是 inferred_vars 的子集
#   （多推出来的不罚——只锁「该推出来的必须推对」）

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'src'))

from mini_intent import Lexer, Parser, TypeChecker  # noqa: E402


def _infer(code: str):
    tokens = Lexer(code).tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    if parser.errors:
        raise SyntaxError(f"语法错误: {parser.errors[0]}")
    checker = TypeChecker(ast, "<selftest>")
    errors = checker.check()
    return checker, errors


# (名称, 代码, 期望推断 {变量: 类型}, 期望错误数)
LOCAL_CASES = [
    ("整数字面量", 'def main() { let a = 1; return 0; }',
     {'a': 'Int'}, 0),
    ("浮点字面量", 'def main() { let a = 1.5; return 0; }',
     {'a': 'Float'}, 0),
    ("字符串字面量", 'def main() { let s = "x"; return 0; }',
     {'s': 'String'}, 0),
    ("布尔比较", 'def main() { let c = 1 < 2; return 0; }',
     {'c': 'Bool'}, 0),
    ("let 链传递", 'def main() { let a = 1; let b = a; return 0; }',
     {'a': 'Int', 'b': 'Int'}, 0),
    ("二元运算数值提升",
     'def main() { let a = 1; let b = a + 1.5; return 0; }',
     {'b': 'Float'}, 0),
    ("字符串拼接保型",
     'def main() { let s = "a" + "b"; return 0; }',
     {'s': 'String'}, 0),
    ("列表字面量", 'def main() { let l = [1, 2]; return 0; }',
     {'l': 'List'}, 0),
    ("字典字面量", 'def main() { let d = {"k": 1}; return 0; }',
     {'d': 'Dict'}, 0),
    ("三元分支统一", 'def main() { let t = true ? 1 : 2; return 0; }',
     {'t': 'Int'}, 0),
    ("if 表达式分支统一",
     'def main() { let x = if true { 10 } else { 20 }; return 0; }',
     {'x': 'Int'}, 0),
    ("管道取函数返回标注",
     'def f(x: Int) -> String { return "s"; }\n'
     'def main() { let p = 1 |> f; return 0; }',
     {'p': 'String'}, 0),
    ("类构造推断为类名",
     'class P {\n def init() {}\n}\n'
     'def main() { let p = P(); return 0; }',
     {'p': 'P'}, 0),
    ("推断参与标注检查(应报错)",
     'def main() { let a = 1; let b: String = a; return 0; }',
     {}, 1),
    ("无标注一律放过(未知不报)",
     'def main() { let u = mystery(); let v: String = "ok"; return 0; }',
     {}, 0),
]


def run_local() -> int:
    passed = 0
    failed = []
    for name, code, expect, want_errors in LOCAL_CASES:
        try:
            checker, errors = _infer(code)
        except Exception as e:
            failed.append((name, f"解析/检查异常: {e}"))
            continue
        problems = []
        if len(errors) != want_errors:
            problems.append(f"期望 {want_errors} 处错误, 实得 {len(errors)} 处")
        for var, typ in expect.items():
            got = checker.inferred_vars.get(var)
            if got != typ:
                problems.append(f"{var} 期望推断 {typ}, 实得 {got}")
        if problems:
            failed.append((name, "; ".join(problems)))
        else:
            passed += 1
            detail = ", ".join(f"{k}:{v}" for k, v in expect.items()) or "无期望"
            print(f"[PASS] {name}: {detail}")
    for name, why in failed:
        print(f"[FAIL] {name}: {why}")
    print(f"\n局部推断自测: {passed}/{len(LOCAL_CASES)} 通过")
    return 0 if not failed else 1


# L3b 返回推断用例（--returns; 未实现时如实失败，不假通过）
RETURN_CASES = [
    ("返回标注推断为 Int",
     'def f() { return 1; }\ndef main() { let x: Int = f(); return 0; }',
     {'f': 'Int'}, 0),
    ("无标注返回误用应报错",
     'def f() { return 1; }\ndef main() { let x: String = f(); return 0; }',
     {'f': 'Int'}, 1),
    ("字符串返回推断",
     'def s() { return "x"; }\ndef main() { let y: String = s(); return 0; }',
     {'s': 'String'}, 0),
    ("调用链借用推断",
     'def f() { return 1; }\ndef g() { return f(); }\n'
     'def main() { let z: Int = g(); return 0; }',
     {'f': 'Int', 'g': 'Int'}, 0),
    ("分支返回统一(同为 Int)",
     'def f(c: Bool) { if c { return 1; } else { return 2; } }\n'
     'def main() { let x: Int = f(true); return 0; }',
     {'f': 'Int'}, 0),
    ("分支返回不统一 → 不猜",
     'def f(c: Bool) { if c { return 1; } else { return "s"; } }\n'
     'def main() { let x = f(true); return 0; }',
     {}, 0),
    ("无 return 的函数不推",
     'def v() { let a = 1; }\ndef main() { let x = v(); return 0; }',
     {}, 0),
]


def run_returns() -> int:
    passed = 0
    failed = []
    for name, code, expect, want_errors in RETURN_CASES:
        try:
            checker, errors = _infer(code)
        except Exception as e:
            failed.append((name, f"解析/检查异常: {e}"))
            continue
        problems = []
        if len(errors) != want_errors:
            problems.append(f"期望 {want_errors} 处错误, 实得 {len(errors)} 处")
        for var, typ in expect.items():
            got = getattr(checker, 'inferred_returns', {}).get(var)
            if got != typ:
                problems.append(f"{var} 期望返回推断 {typ}, 实得 {got}")
        if problems:
            failed.append((name, "; ".join(problems)))
        else:
            passed += 1
            print(f"[PASS] {name}")
    for name, why in failed:
        print(f"[FAIL] {name}: {why}")
    print(f"\n返回推断自测: {passed}/{len(RETURN_CASES)} 通过")
    return 0 if not failed else 1


def main(argv) -> int:
    if '--returns' in argv:
        return run_returns()
    return run_local()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
