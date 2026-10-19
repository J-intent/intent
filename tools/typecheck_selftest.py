#!/usr/bin/env python3
"""L1 渐进类型检查器自测(正反例判定)。

路线图出口标准: 「应报错的报, 不应报的不报」。
每个用例: (名称, Intent 代码, 期望错误数)。错误数以报告条数计。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from mini_intent import Lexer, Parser, TypeChecker  # noqa: E402

CASES = [
    # ---- 反例: 应报错 ----
    ("变量声明标注不符",
     'def main() { let x: Int = "hello"; return 0; }', 1),
    ("布尔标注不收整数",
     'def main() { let ok: Bool = 1; return 0; }', 1),
    ("返回标注不符",
     'def f() -> Int { return "oops"; }\ndef main() { let r = f(); return 0; }', 1),
    ("实参与形参标注不符",
     'def greet(name: String) -> String { return name; }\n'
     'def main() { let r = greet(42); return 0; }', 1),
    ("多处错误全报",
     'def main() { let a: Int = "x"; let b: Bool = 3.5; return 0; }', 2),
    ("别名穿透后仍报错",
     'type Meters = Float;\ndef main() { let m: Meters = "tall"; return 0; }', 1),
    ("Union 成员全不符仍报错",
     'def main() { let x: Int | String = true; return 0; }', 1),
    # ---- 正例: 不应报错 ----
    ("标注正确",
     'def main() { let x: Int = 42; let s: String = "ok"; return 0; }', 0),
    ("数值互通 Int 收 Float",
     'def main() { let x: Int = 1.5; return 0; }', 0),
    ("数值互通 Float 收 Int",
     'def main() { let x: Float = 3; return 0; }', 0),
    ("无标注一律放过",
     'def main() { let a = "s"; let b = 1; let c = a + "x"; return 0; }', 0),
    ("Union 命中成员",
     'def main() { let x: Int | String = "s"; return 0; }', 0),
    ("别名解析通过",
     'type Meters = Float;\ndef main() { let m: Meters = 1.5; return 0; }', 0),
    ("泛型参数视为 Any",
     'def identity<T>(x: T) -> T { return x; }\n'
     'def main() { let a = identity(1); let b = identity("s"); return 0; }', 0),
    ("Any 标注放过",
     'def f(x: Any) -> Any { return x; }\ndef main() { let r = f(1); return 0; }', 0),
    ("未知推断放过(内置白名单外)",
     'def main() { let n: Int = len("abc"); return 0; }', 0),
    ("字符串拼接标注正确",
     'def main() { let s: String = "a" + "b"; return 0; }', 0),
    ("比较结果布尔标注正确",
     'def main() { let b: Bool = 1 < 2; return 0; }', 0),
    ("容器只查基类",
     'def main() { let xs: List = [1, 2, 3]; let m: Dict = {"a": 1}; return 0; }', 0),
    ("分支内声明不污染外层",
     'def main() { if true { let x: Int = 1; } let y: String = "ok"; return 0; }', 0),
    ("正确实参传递",
     'def add(a: Int, b: Int) -> Int { return a + b; }\n'
     'def main() { let s = add(1, 2); return 0; }', 0),
    # ---- L2 结构化类型: 协议符合性(方法集覆盖) ----
    ("协议: 方法集覆盖通过",
     'protocol Drawable { def draw() -> String; }\n'
     'class Circle {\n def init() {}\n def draw() -> String { return "c"; }\n}\n'
     'def main() { let d: Drawable = Circle(); return 0; }', 0),
    ("协议: 缺方法应报错",
     'protocol Drawable { def draw() -> String; }\n'
     'class Blob {\n def init() {}\n def paint() -> String { return "b"; }\n}\n'
     'def main() { let d: Drawable = Blob(); return 0; }', 1),
    ("协议: 继承链方法算数",
     'protocol Drawable { def draw() -> String; }\n'
     'class Base {\n def draw() -> String { return "b"; }\n}\n'
     'class Sub < Base {\n def init() {}\n}\n'
     'def main() { let d: Drawable = Sub(); return 0; }', 0),
    ("协议: 实参传递缺方法报错",
     'protocol Drawable { def draw() -> String; }\n'
     'class Blob {\n def paint() -> String { return "b"; }\n}\n'
     'def render(d: Drawable) -> String { return d.draw(); }\n'
     'def main() { let r = render(Blob()); return 0; }', 1),
]


def run():
    passed = failed = 0
    for name, code, expect in CASES:
        tokens = Lexer(code).tokenize()
        parser = Parser(tokens, code)
        ast = parser.parse()
        errors = TypeChecker(ast, name).check()
        ok = len(errors) == expect
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: 期望 {expect} 处错误, 实得 {len(errors)} 处")
        if not ok:
            for e in errors:
                print(f"       · {e}")
            failed += 1
        else:
            passed += 1
    print(f"\n类型检查器自测: {passed}/{len(CASES)} 通过"
          + (f", {failed} 失败" if failed else ""))
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(run())
