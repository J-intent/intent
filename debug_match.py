# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\Users\阿J\intent\src')

# 测试TokenType
from mini_intent import Lexer, Parser

code = """
export def multiply(a, b) {
    return a * b;
}
"""

lexer = Lexer(code)
tokens = lexer.tokenize()

for t in tokens:
    print(f"{t.type}: '{t.value}' @ {t.line}:{t.column}")
