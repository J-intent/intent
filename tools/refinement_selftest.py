#!/usr/bin/env python
# tools/refinement_selftest.py — L5 契约即类型自测（requires 精炼）
#
# 皇冠任务：`def f(x: Int) requires x > 0` 之后，`f(-1)` 不必等到运行时
# 才炸——`--types` 在编译期就按字面量实参判定 requires，违约即报。
#
# 判定口径：每个用例 (名称, 代码, 期望错误数)；错误用例必须报「契约精炼」，
# 防止被其他类型错误凑数（判定防真空）。
#
# 用法：
#   python tools/refinement_selftest.py          L5a 骨架用例
#   python tools/refinement_selftest.py --full   L5b 完整用例（含多参/组合谓词）

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'src'))

from mini_intent import Lexer, Parser, TypeChecker  # noqa: E402


def _check(code: str):
    tokens = Lexer(code).tokenize()
    parser = Parser(tokens, code)
    ast = parser.parse()
    if parser.errors:
        raise SyntaxError(f"语法错误: {parser.errors[0]}")
    checker = TypeChecker(ast, "<refine>", source_lines=code.splitlines())
    return checker.check()


# (名称, 代码, 期望错误数) — 错误用例必须含「契约精炼」字样
BASE_CASES = [
    ("除零精炼拦截",
     'def divide(a: Float, b: Float): Float requires b != 0 { return a / b; }\n'
     'def main() { let r = divide(10, 0); return 0; }', 1),
    ("除零精炼放行",
     'def divide(a: Float, b: Float): Float requires b != 0 { return a / b; }\n'
     'def main() { let r = divide(10, 2); return 0; }', 0),
    ("正数精炼拦截",
     'def positive(x: Int) requires x > 0 { return x; }\n'
     'def main() { let r = positive(-1); return 0; }', 1),
    ("正数精炼放行",
     'def positive(x: Int) requires x > 0 { return x; }\n'
     'def main() { let r = positive(5); return 0; }', 0),
    (">= 边界: 0 合法",
     'def nonneg(x: Int) requires x >= 0 { return x; }\n'
     'def main() { let r = nonneg(0); return 0; }', 0),
    (">= 边界: -1 拦截",
     'def nonneg(x: Int) requires x >= 0 { return x; }\n'
     'def main() { let r = nonneg(-1); return 0; }', 1),
    ("字面量在左的比较",
     'def small(x: Int) requires 0 < x { return x; }\n'
     'def main() { let r = small(-3); return 0; }', 1),
    ("非字面量实参不猜",
     'def positive(x: Int) requires x > 0 { return x; }\n'
     'def main() { let n = 0 - 1; let r = positive(n); return 0; }', 0),
    ("== 精炼拦截",
     'def exactly5(x: Int) requires x == 5 { return x; }\n'
     'def main() { let r = exactly5(3); return 0; }', 1),
    ("== 精炼放行",
     'def exactly5(x: Int) requires x == 5 { return x; }\n'
     'def main() { let r = exactly5(5); return 0; }', 0),
]

FULL_CASES = [
    ("合取谓词: 第一项违约",
     'def pos2(x: Int, y: Int) requires x > 0 and y > 0 { return x + y; }\n'
     'def main() { let r = pos2(-1, 2); return 0; }', 1),
    ("合取谓词: 全满足放行",
     'def pos2(x: Int, y: Int) requires x > 0 and y > 0 { return x + y; }\n'
     'def main() { let r = pos2(1, 2); return 0; }', 0),
    ("双参比较: a < b 拦截",
     'def ordered(a: Int, b: Int) requires a < b { return b - a; }\n'
     'def main() { let r = ordered(5, 3); return 0; }', 1),
    ("双参比较: a < b 放行",
     'def ordered(a: Int, b: Int) requires a < b { return b - a; }\n'
     'def main() { let r = ordered(1, 2); return 0; }', 0),
    ("双参+合取: 第二项违约",
     'def range_ok(a: Int, b: Int) requires a > 0 and a < b { return b; }\n'
     'def main() { let r = range_ok(3, 2); return 0; }', 1),
    ("浮点精炼拦截",
     'def frac_positive(x: Float) requires x > 0.5 { return x; }\n'
     'def main() { let r = frac_positive(0.3); return 0; }', 1),
    ("浮点精炼放行",
     'def frac_positive(x: Float) requires x > 0.5 { return x; }\n'
     'def main() { let r = frac_positive(0.8); return 0; }', 0),
    ("多子句: 第二条违约",
     'def safe_div(a: Int, b: Int) requires b > 0 and b != 1 { return a / b; }\n'
     'def main() { let r = safe_div(10, 1); return 0; }', 1),
    ("@refine-off 显式豁免",
     'def positive(x: Int) requires x > 0 { return x; }\n'
     'def main() { let r = positive(-1); return 0; }  // @refine-off',
     0),
]


def _run(cases, title: str) -> int:
    passed = 0
    failed = []
    for name, code, want in cases:
        try:
            errors = _check(code)
        except Exception as e:
            failed.append((name, f"解析/检查异常: {e}"))
            continue
        problems = []
        if len(errors) != want:
            problems.append(f"期望 {want} 处, 实得 {len(errors)} 处: {errors}")
        if want > 0 and not any('契约精炼' in e for e in errors):
            problems.append("错误信息里没有「契约精炼」——可能被其他错误凑数")
        if problems:
            failed.append((name, "; ".join(problems)))
        else:
            passed += 1
            print(f"[PASS] {name}")
    for name, why in failed:
        print(f"[FAIL] {name}: {why}")
    print(f"\n{title}: {passed}/{len(cases)} 通过")
    return 0 if not failed else 1


def main(argv) -> int:
    if '--full' in argv:
        base = _run(BASE_CASES, "契约精炼·基础")
        if base != 0:
            return base
        return _run(FULL_CASES, "契约精炼·完整（多参/组合谓词）")
    return _run(BASE_CASES, "契约精炼·骨架")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
