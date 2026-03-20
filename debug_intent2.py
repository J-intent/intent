#!/usr/bin/env python3
"""Intent语言调试版本 - 详细追踪"""

import sys
sys.path.insert(0, 'C:/Users/阿J/intent/src')

from mini_intent import Lexer, Parser, Interpreter

test_code = '''def main() {
 print("test");
 return 0;
}'''

print("代码:", repr(test_code))
print("=" * 50)

lexer = Lexer(test_code, "test.intent")
tokens = lexer.tokenize()

print("Token列表:")
for i, tok in enumerate(tokens):
    print(f"  {i}: {tok}")

print("=" * 50)
print("开始解析...")

parser = Parser(tokens)

# 手动逐步执行，看看问题出在哪里
# 首先解析函数定义
parser.expect(lexer.KEYWORDS.__class__._member_names_ if hasattr(lexer.KEYWORDS, '__class__') else None)
