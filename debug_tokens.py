# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\Users\阿J\intent\src')

from mini_intent import Lexer, TokenType

code = """
export def multiply(a, b) {
    return a * b;
}

def main() {
    print("test");
}
"""

lexer = Lexer(code)
tokens = lexer.tokenize()

for i, t in enumerate(tokens):
    print(f"{i}: {t.type} '{repr(t.value)}' @ {t.line}:{t.column}")
