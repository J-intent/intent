#!/usr/bin/env python3
"""详细追踪第一次parse_statement调用"""

import sys
sys.path.insert(0, 'C:/Users/阿J/intent/src')

from mini_intent_debug import Lexer, Parser, Token, TokenType

test_code = '''def main() {
 print("test");
 return 0;
}'''

lexer = Lexer(test_code)
tokens = lexer.tokenize()

print("完整Token列表:")
for i, t in enumerate(tokens):
    print(f"  {i}: {t}")

print("\n" + "=" * 50)

parser = Parser(tokens)

# 模拟parse_function_def的过程
print("\n模拟函数体解析:")
print(f"1. 初始: {parser.current_token}")

parser.advance()  # def
print(f"2. def: {parser.current_token}")

parser.advance()  # main
print(f"3. main: {parser.current_token}")

parser.advance()  # (
print(f"4. (: {parser.current_token}")

parser.advance()  # )
print(f"5. ): {parser.current_token}")

parser.advance()  # {
print(f"6. {{ : {parser.current_token}")

parser.advance()  # NEWLINE
print(f"7. NEWLINE: {parser.current_token}")

# 现在进入循环
print("\n进入while循环...")
print(f"检查: not self.match(TokenType.SYMBOL, '}') = {not parser.match(TokenType.SYMBOL, '}')}")
print(f"当前token: {parser.current_token}")

# 调用parse_statement
# 第一步：跳过NEWLINE
while parser.match(TokenType.NEWLINE):
    print(f"  跳过NEWLINE: {parser.current_token}")
    parser.advance()
    
print(f"跳过NEWLINE后: {parser.current_token}")

# 第二步：检查空语句
print(f"检查空语句: match(SYMBOL, ';') = {parser.match(TokenType.SYMBOL, ';')}")

# 第三步：检查变量声明
print(f"检查let: match(KEYWORD, 'let') = {parser.match(TokenType.KEYWORD, 'let')}")
print(f"检查var: match(KEYWORD, 'var') = {parser.match(TokenType.KEYWORD, 'var')}")
print(f"检查const: match(KEYWORD, 'const') = {parser.match(TokenType.KEYWORD, 'const')}")

# 第四步：检查return
print(f"检查return: match(KEYWORD, 'return') = {parser.match(TokenType.KEYWORD, 'return')}")

# 第五步：检查print
print(f"检查print: match(ID, 'print') = {parser.match(TokenType.IDENTIFIER, 'print')}")
print(f"  当前token type = {parser.current_token.type}")
print(f"  当前token value = {parser.current_token.value}")
