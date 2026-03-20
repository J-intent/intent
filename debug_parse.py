# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\Users\阿J\intent\src')

from mini_intent import Lexer, Parser

code = """
export def multiply(a, b) {
    return a * b;
}
"""

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

print(f"Functions: {list(ast.functions.keys())}")
print(f"Statements: {[type(s).__name__ for s in ast.statements]}")
