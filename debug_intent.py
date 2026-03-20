#!/usr/bin/env python3
"""Intent语言调试版本 - 追踪print语句解析问题"""

import sys
import os

# 添加调试追踪
DEBUG = True

def debug_log(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}", file=sys.stderr)

# 导入原始模块
sys.path.insert(0, 'C:/Users/阿J/intent/src')
from mini_intent import Lexer, Parser, Interpreter

# 临时修改Lexer来追踪
original_tokenize = Lexer.tokenize
def debug_tokenize(self):
    tokens = original_tokenize(self)
    debug_log(f"Token化完成，共 {len(tokens)} 个token")
    for i, tok in enumerate(tokens[:20]):  # 只显示前20个
        debug_log(f"  {i}: {tok}")
    return tokens

Lexer.tokenize = debug_tokenize

# 临时修改Parser来追踪
original_parse_statement = Parser.parse_statement
def debug_parse_statement(self):
    debug_log(f"parse_statement: 当前token = {self.current_token}")
    return original_parse_statement(self)

Parser.parse_statement = debug_parse_statement

# 测试
test_code = '''def main() {
 print("test");
 return 0;
}'''

print("=" * 50)
print("开始调试...")
print("=" * 50)

lexer = Lexer(test_code, "test.intent")
tokens = lexer.tokenize()

parser = Parser(tokens)
try:
    program = parser.parse()
    print("解析成功!")
except Exception as e:
    print(f"解析失败: {e}")
