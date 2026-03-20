#!/usr/bin/env python3
"""直接patch Parser来添加调试"""

import sys
sys.path.insert(0, 'C:/Users/阿J/intent/src')

# 读取原始文件
with open('C:/Users/阿J/intent/src/mini_intent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在parse_statement方法开头添加调试
debug_code = '''    def parse_statement(self) -> Optional[ASTNode]:
        """解析语句"""
        # ===== DEBUG =====
        print(f"[DEBUG] parse_statement: current_token = {self.current_token}")
        # ===== END DEBUG =====
        
        # 跳过开头的换行符 - 关键修复
        while self.match(TokenType.NEWLINE):
            self.advance()
'''

# 替换parse_statement方法
old_parse_statement = '''    def parse_statement(self) -> Optional[ASTNode]:
        """解析语句"""
        # 跳过开头的换行符 - 关键修复
        while self.match(TokenType.NEWLINE):
            self.advance()'''

content = content.replace(old_parse_statement, debug_code)

# 在parse_print_stmt开头也添加调试
debug_print = '''    def parse_print_stmt(self) -> PrintStmt:
        """解析打印语句"""
        # ===== DEBUG =====
        print(f"[DEBUG] parse_print_stmt called!")
        # ===== END DEBUG =====
        start_token = self.expect(TokenType.IDENTIFIER, 'print')'''

old_print = '''    def parse_print_stmt(self) -> PrintStmt:
        """解析打印语句"""
        start_token = self.expect(TokenType.IDENTIFIER, 'print')'''

content = content.replace(old_print, debug_print)

# 写入调试版本
with open('C:/Users/阿J/intent/src/mini_intent_debug.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("调试版本已创建")

# 测试
from mini_intent_debug import Lexer, Parser, Interpreter

test_code = '''def main() {
 print("test");
 return 0;
}'''

lexer = Lexer(test_code)
tokens = lexer.tokenize()
print("Token化完成")

parser = Parser(tokens)
try:
    program = parser.parse()
    print("解析成功!")
except Exception as e:
    print(f"解析失败: {e}")
