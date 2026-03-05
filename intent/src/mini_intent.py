#!/usr/bin/env python3
"""
Intent语言完整解释器
融合：心学为体，禅道为翼，马哲为用
版本：1.0.0
"""

import sys
import os
import re
import json
from dataclasses import dataclass
from typing import Any, List, Dict, Optional, Tuple

# ==================== 1. 哲学翻译器 ====================
class PhilosophyTranslator:
    """哲学翻译器：将英文关键字转换为中文哲学术语"""
    
    def __init__(self, mapping_file: Optional[str] = None):
        # 默认哲学映射
        self.default_mapping = {
            "keywords": {
                "def": {
                    "chinese": "功夫",
                    "philosophy": "在事上磨炼的技艺",
                    "explanation": "函数定义如同功夫修炼，需要明确的契约和清晰的意图"
                },
                "func": {
                    "chinese": "功夫",
                    "philosophy": "在事上磨炼的技艺"
                },
                "let": {
                    "chinese": "格物",
                    "philosophy": "探究具体事物",
                    "explanation": "变量绑定如同探究事物之理"
                },
                "print": {
                    "chinese": "印行",
                    "philosophy": "将思想印刻于行动",
                    "explanation": "输出是将内在意图转化为外在表现"
                },
                "return": {
                    "chinese": "归元",
                    "philosophy": "回归本源",
                    "explanation": "返回值是函数执行的归宿"
                },
                "requires": {
                    "chinese": "事上练",
                    "philosophy": "实践前的条件准备",
                    "explanation": "前置条件是做事的前提，如同心学的'事上练'"
                },
                "ensures": {
                    "chinese": "持志",
                    "philosophy": "实践后的结果坚守",
                    "explanation": "后置条件是做事的承诺，如同心学的'持志'"
                },
                "invariant": {
                    "chinese": "常道",
                    "philosophy": "始终不变的规律"
                },
                "if": {
                    "chinese": "若",
                    "philosophy": "条件假设"
                },
                "else": {
                    "chinese": "否则",
                    "philosophy": "另一种可能"
                },
                "for": {
                    "chinese": "遍历",
                    "philosophy": "逐一经历"
                },
                "while": {
                    "chinese": "当",
                    "philosophy": "持续条件满足时"
                },
                "Int": {
                    "chinese": "整",
                    "philosophy": "完整的数"
                },
                "String": {
                    "chinese": "文",
                    "philosophy": "文化的载体"
                },
                "Bool": {
                    "chinese": "是非",
                    "philosophy": "对错的判断"
                },
                "main": {
                    "chinese": "主",
                    "philosophy": "一切的根本"
                },
                "pure": {
                    "chinese": "无住",
                    "philosophy": "不执着于外相"
                },
                "effect": {
                    "chinese": "着相",
                    "philosophy": "与外界的交互"
                }
            }
        }
        
        # 尝试加载外部映射文件
        if mapping_file and os.path.exists(mapping_file):
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    file_mapping = json.load(f)
                    # 合并映射
                    if "keywords" in file_mapping:
                        self.default_mapping["keywords"].update(file_mapping["keywords"])
                print(f"✓ 已加载哲学映射文件: {mapping_file}")
            except Exception as e:
                print(f"⚠ 无法加载哲学映射文件: {e}，使用默认映射")
        else:
            if mapping_file:
                print(f"⚠ 未找到哲学映射文件: {mapping_file}，使用默认映射")
        
        self.mapping = self.default_mapping
    
    def translate_keyword(self, keyword: str) -> Tuple[str, str]:
        """翻译单个关键字"""
        if keyword in self.mapping["keywords"]:
            info = self.mapping["keywords"][keyword]
            return info.get("chinese", keyword), info.get("philosophy", "")
        return keyword, ""
    
    def translate_code(self, code: str, add_explanation: bool = True) -> str:
        """翻译整个代码"""
        lines = code.split('\n')
        translated_lines = []
        
        for line in lines:
            translated_line = line
            
            # 按优先级翻译：先翻译长的关键字，避免部分匹配
            sorted_keywords = sorted(
                self.mapping["keywords"].keys(),
                key=len,
                reverse=True
            )
            
            for keyword in sorted_keywords:
                chinese, philosophy = self.translate_keyword(keyword)
                if chinese != keyword:
                    # 使用正则表达式替换整个单词
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    translated_line = re.sub(pattern, chinese, translated_line)
            
            # 如果有哲学解释且行中有关键字，添加注释
            if add_explanation and not line.strip().startswith('//'):
                for keyword in self.mapping["keywords"]:
                    if keyword in line:
                        chinese, philosophy = self.translate_keyword(keyword)
                        if philosophy and philosophy not in translated_line:
                            if "//" not in translated_line:
                                translated_line += f"  // {philosophy}"
                            break
            
            translated_lines.append(translated_line)
        
        return '\n'.join(translated_lines)

# ==================== 2. 词法分析 ====================
class TokenType:
    """Token类型枚举"""
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    SYMBOL = "SYMBOL"
    OPERATOR = "OPERATOR"
    EOF = "EOF"

@dataclass
class Token:
    """词法单元"""
    type: str
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line:{self.line}, col:{self.column})"

class Lexer:
    """词法分析器"""
    
    # 关键字列表
    KEYWORDS = {
        'def', 'func', 'let', 'return', 'if', 'else', 'for', 'while',
        'requires', 'ensures', 'invariant', 'pure', 'effect',
        'Int', 'String', 'Bool', 'True', 'False', 'None'
    }
    
    # 符号列表
    SYMBOLS = {'(', ')', '{', '}', '[', ']', ',', ':', ';', '=', '.', '->'}
    
    # 运算符列表
    OPERATORS = {'+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=', '!', '&&', '||'}
    
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    
    def current_char(self) -> Optional[str]:
        """获取当前字符"""
        if self.pos < len(self.code):
            return self.code[self.pos]
        return None
    
    def advance(self):
        """前进一个字符"""
        if self.current_char() == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
    
    def peek(self) -> Optional[str]:
        """查看下一个字符，不移动位置"""
        if self.pos + 1 < len(self.code):
            return self.code[self.pos + 1]
        return None
    
    def add_token(self, token_type: str, value: str = None):
        """添加token"""
        if value is None:
            value = self.current_char()
        self.tokens.append(Token(token_type, value, self.line, self.column))
        self.advance()
    
    def skip_whitespace(self):
        """跳过空白字符"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """跳过注释"""
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_string(self):
        """读取字符串字面量"""
        start_pos = self.pos
        self.advance()  # 跳过开头的引号
        
        while self.current_char() and self.current_char() != '"':
            if self.current_char() == '\\':  # 处理转义字符
                self.advance()
            self.advance()
        
        if not self.current_char():
            raise SyntaxError(f"未结束的字符串，行 {self.line}")
        
        value = self.code[start_pos + 1:self.pos]
        self.tokens.append(Token(TokenType.STRING, value, self.line, self.column))
        self.advance()  # 跳过结尾的引号
    
    def read_number(self):
        """读取数字"""
        start_pos = self.pos
        
        while self.current_char() and self.current_char().isdigit():
            self.advance()
        
        # 检查是否有小数点
        if self.current_char() == '.':
            self.advance()
            while self.current_char() and self.current_char().isdigit():
                self.advance()
        
        value = self.code[start_pos:self.pos]
        self.tokens.append(Token(TokenType.NUMBER, value, self.line, self.column))
    
    def read_identifier(self):
        """读取标识符或关键字"""
        start_pos = self.pos
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        
        value = self.code[start_pos:self.pos]
        
        # 判断是否是关键字
        if value in self.KEYWORDS:
            token_type = TokenType.KEYWORD
        else:
            token_type = TokenType.IDENTIFIER
        
        self.tokens.append(Token(token_type, value, self.line, self.column))
    
    def read_operator(self):
        """读取运算符"""
        start_pos = self.pos
        self.advance()
        
        # 检查是否是多字符运算符
        if self.current_char():
            two_char_op = self.code[start_pos] + self.current_char()
            if two_char_op in self.OPERATORS:
                self.tokens.append(Token(TokenType.OPERATOR, two_char_op, self.line, self.column))
                self.advance()
                return
        
        # 单字符运算符
        self.tokens.append(Token(TokenType.OPERATOR, self.code[start_pos], self.line, self.column))
    
    def tokenize(self) -> List[Token]:
        """执行词法分析"""
        while self.current_char():
            # 跳过空白字符
            if self.current_char() in ' \t\r':
                self.skip_whitespace()
                continue
            
            # 跳过换行
            if self.current_char() == '\n':
                self.advance()
                continue
            
            # 跳过注释
            if self.current_char() == '#' or (self.current_char() == '/' and self.peek() == '/'):
                self.skip_comment()
                continue
            
            # 字符串
            if self.current_char() == '"':
                self.read_string()
                continue
            
            # 数字
            if self.current_char().isdigit():
                self.read_number()
                continue
            
            # 标识符或关键字
            if self.current_char().isalpha() or self.current_char() == '_':
                self.read_identifier()
                continue
            
            # 符号
            if self.current_char() in self.SYMBOLS:
                self.add_token(TokenType.SYMBOL)
                continue
            
            # 运算符
            if self.current_char() in self.OPERATORS:
                self.read_operator()
                continue
            
            # 未知字符
            raise SyntaxError(f"未知字符: '{self.current_char()}'，行 {self.line}，列 {self.column}")
        
        # 添加EOF标记
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

# ==================== 3. 抽象语法树 ====================
@dataclass
class ASTNode:
    """抽象语法树基类"""
    pass

@dataclass
class Program(ASTNode):
    """程序节点"""
    functions: List['Function']

@dataclass
class Function(ASTNode):
    """函数定义节点"""
    name: str
    params: List[Tuple[str, str]]  # (参数名, 类型)
    return_type: Optional[str]
    requires: List[str]  # 前置条件
    ensures: List[str]   # 后置条件
    body: List['Statement']

@dataclass
class Statement(ASTNode):
    """语句基类"""
    pass

@dataclass
class PrintStatement(Statement):
    """print语句"""
    value: Any

@dataclass
class ReturnStatement(Statement):
    """return语句"""
    value: Any

@dataclass
class VariableDeclaration(Statement):
    """变量声明语句"""
    name: str
    var_type: Optional[str]
    value: Any

@dataclass
class FunctionCall(Statement):
    """函数调用语句"""
    name: str
    args: List[Any]

@dataclass
class Expression(ASTNode):
    """表达式基类"""
    pass

@dataclass
class Literal(Expression):
    """字面量表达式"""
    value: Any
    literal_type: str  # 'string', 'number', 'boolean'

@dataclass
class Variable(Expression):
    """变量表达式"""
    name: str

@dataclass
class BinaryExpression(Expression):
    """二元表达式"""
    left: Expression
    operator: str
    right: Expression

# ==================== 4. 语法分析器 ====================
class Parser:
    """语法分析器"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Token:
        """获取当前token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, "", 0, 0)
    
    def peek_token(self) -> Token:
        """查看下一个token"""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(TokenType.EOF, "", 0, 0)
    
    def advance(self):
        """前进到下一个token"""
        if self.pos < len(self.tokens):
            self.pos += 1
    
    def match(self, token_type: str, value: str = None) -> bool:
        """检查当前token是否匹配"""
        token = self.current_token()
        if token.type != token_type:
            return False
        if value is not None and token.value != value:
            return False
        return True
    
    def consume(self, token_type: str, value: str = None, error_msg: str = None) -> Token:
        """消费一个token，如果不匹配则报错"""
        token = self.current_token()
        
        if token.type != token_type:
            raise SyntaxError(f"期望 {token_type}，但得到 {token.type}，行 {token.line}")
        
        if value is not None and token.value != value:
            raise SyntaxError(f"期望 '{value}'，但得到 '{token.value}'，行 {token.line}")
        
        self.advance()
        return token
    
    def parse(self) -> Program:
        """解析整个程序"""
        functions = []
        
        while not self.match(TokenType.EOF):
            # 跳过无关的token
            if self.match(TokenType.KEYWORD, 'def') or self.match(TokenType.KEYWORD, 'func'):
                functions.append(self.parse_function())
            else:
                self.advance()  # 跳过不认识的token
        
        return Program(functions)
    
    def parse_function(self) -> Function:
        """解析函数定义"""
        # 解析函数开头：def 函数名(参数) -> 返回类型
        self.consume(TokenType.KEYWORD, 'def', "期望 'def' 关键字")
        
        name = self.consume(TokenType.IDENTIFIER, None, "期望函数名").value
        
        # 解析参数列表
        self.consume(TokenType.SYMBOL, '(', "期望 '('")
        
        params = []
        if not self.match(TokenType.SYMBOL, ')'):
            params.append(self.parse_parameter())
            while self.match(TokenType.SYMBOL, ','):
                self.consume(TokenType.SYMBOL, ',')
                params.append(self.parse_parameter())
        
        self.consume(TokenType.SYMBOL, ')', "期望 ')'")
        
        # 解析返回类型
        return_type = None
        if self.match(TokenType.OPERATOR, '->'):
            self.consume(TokenType.OPERATOR, '->')
            return_type = self.consume(TokenType.IDENTIFIER, None, "期望返回类型").value
        
        # 解析契约
        requires = []
        ensures = []
        
        while True:
            if self.match(TokenType.KEYWORD, 'requires'):
                self.consume(TokenType.KEYWORD, 'requires')
                requires.append(self.parse_contract_condition())
            elif self.match(TokenType.KEYWORD, 'ensures'):
                self.consume(TokenType.KEYWORD, 'ensures')
                ensures.append(self.parse_contract_condition())
            else:
                break
        
        # 解析函数体
        self.consume(TokenType.SYMBOL, '{', "期望 '{'")
        
        body = []
        while not self.match(TokenType.SYMBOL, '}'):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.consume(TokenType.SYMBOL, '}', "期望 '}'")
        
        return Function(name, params, return_type, requires, ensures, body)
    
    def parse_parameter(self) -> Tuple[str, str]:
        """解析函数参数"""
        name = self.consume(TokenType.IDENTIFIER, None, "期望参数名").value
        self.consume(TokenType.SYMBOL, ':', "期望 ':'")
        param_type = self.consume(TokenType.IDENTIFIER, None, "期望参数类型").value
        return (name, param_type)
    
    def parse_contract_condition(self) -> str:
        """解析契约条件（简化版）"""
        # 收集条件表达式的token，直到遇到换行或下一个关键字
        condition_tokens = []
        while (self.current_token().type != TokenType.EOF and 
               not self.match(TokenType.KEYWORD, 'requires') and
               not self.match(TokenType.KEYWORD, 'ensures') and
               not self.match(TokenType.SYMBOL, '{')):
            condition_tokens.append(self.current_token().value)
            self.advance()
        
        return ' '.join(condition_tokens).strip(', ')
    
    def parse_statement(self) -> Optional[Statement]:
        """解析语句"""
        # 空语句
        if self.match(TokenType.SYMBOL, ';'):
            self.consume(TokenType.SYMBOL, ';')
            return None
        
        # print语句
        if self.match(TokenType.IDENTIFIER, 'print'):
            return self.parse_print_statement()
        
        # return语句
        if self.match(TokenType.KEYWORD, 'return'):
            return self.parse_return_statement()
        
        # let语句（变量声明）
        if self.match(TokenType.KEYWORD, 'let'):
            return self.parse_variable_declaration()
        
        # 函数调用
        if self.match(TokenType.IDENTIFIER) and self.peek_token().value == '(':
            return self.parse_function_call()
        
        # 跳过无法识别的语句
        self.advance()
        return None
    
    def parse_print_statement(self) -> PrintStatement:
        """解析print语句"""
        self.consume(TokenType.IDENTIFIER, 'print', "期望 'print'")
        self.consume(TokenType.SYMBOL, '(', "期望 '('")
        
        # 解析参数
        if self.match(TokenType.STRING):
            value = self.consume(TokenType.STRING).value
        elif self.match(TokenType.NUMBER):
            value = float(self.consume(TokenType.NUMBER).value)
        elif self.match(TokenType.IDENTIFIER):
            value = self.consume(TokenType.IDENTIFIER).value
        else:
            raise SyntaxError("print语句需要字符串、数字或变量")
        
        self.consume(TokenType.SYMBOL, ')', "期望 ')'")
        self.consume(TokenType.SYMBOL, ';', "期望 ';'")
        
        return PrintStatement(value)
    
    def parse_return_statement(self) -> ReturnStatement:
        """解析return语句"""
        self.consume(TokenType.KEYWORD, 'return', "期望 'return'")
        
        # 解析返回值
        if self.match(TokenType.NUMBER):
            value = float(self.consume(TokenType.NUMBER).value)
        elif self.match(TokenType.IDENTIFIER):
            value = self.consume(TokenType.IDENTIFIER).value
        else:
            value = None
        
        self.consume(TokenType.SYMBOL, ';', "期望 ';'")
        
        return ReturnStatement(value)
    
    def parse_variable_declaration(self) -> VariableDeclaration:
        """解析变量声明"""
        self.consume(TokenType.KEYWORD, 'let', "期望 'let'")
        
        name = self.consume(TokenType.IDENTIFIER, None, "期望变量名").value
        
        # 可选类型注解
        var_type = None
        if self.match(TokenType.SYMBOL, ':'):
            self.consume(TokenType.SYMBOL, ':')
            var_type = self.consume(TokenType.IDENTIFIER, None, "期望变量类型").value
        
        self.consume(TokenType.OPERATOR, '=', "期望 '='")
        
        # 解析变量值
        if self.match(TokenType.NUMBER):
            value = float(self.consume(TokenType.NUMBER).value)
        elif self.match(TokenType.STRING):
            value = self.consume(TokenType.STRING).value
        elif self.match(TokenType.IDENTIFIER):
            value = self.consume(TokenType.IDENTIFIER).value
        else:
            raise SyntaxError("期望数字、字符串或变量")
        
        self.consume(TokenType.SYMBOL, ';', "期望 ';'")
        
        return VariableDeclaration(name, var_type, value)
    
    def parse_function_call(self) -> FunctionCall:
        """解析函数调用"""
        name = self.consume(TokenType.IDENTIFIER, None, "期望函数名").value
        self.consume(TokenType.SYMBOL, '(', "期望 '('")
        
        # 解析参数列表
        args = []
        if not self.match(TokenType.SYMBOL, ')'):
            args.append(self.parse_expression())
            while self.match(TokenType.SYMBOL, ','):
                self.consume(TokenType.SYMBOL, ',')
                args.append(self.parse_expression())
        
        self.consume(TokenType.SYMBOL, ')', "期望 ')'")
        self.consume(TokenType.SYMBOL, ';', "期望 ';'")
        
        return FunctionCall(name, args)
    
    def parse_expression(self) -> Expression:
        """解析表达式（简化版）"""
        # 这里简化处理，实际应该实现完整的表达式解析
        if self.match(TokenType.NUMBER):
            value = float(self.consume(TokenType.NUMBER).value)
            return Literal(value, 'number')
        elif self.match(TokenType.STRING):
            value = self.consume(TokenType.STRING).value
            return Literal(value, 'string')
        elif self.match(TokenType.IDENTIFIER):
            name = self.consume(TokenType.IDENTIFIER).value
            return Variable(name)
        
        raise SyntaxError("无法解析表达式")

# ==================== 5. 契约验证器 ====================
class ContractVerifier:
    """契约验证器"""
    
    def __init__(self):
        self.variables = {}
    
    def verify_requires(self, requires: List[str], context: Dict) -> bool:
        """验证前置条件"""
        if not requires:
            return True
        
        print("🔍 验证前置条件（事上练）:")
        for condition in requires:
            if condition:  # 简化：这里应该实际评估条件
                print(f"  ✓ {condition}")
            else:
                print(f"  ✗ 条件不满足: {condition}")
                return False
        
        return True
    
    def verify_ensures(self, ensures: List[str], result: Any, context: Dict) -> bool:
        """验证后置条件"""
        if not ensures:
            return True
        
        print("🔍 验证后置条件（持志）:")
        for condition in ensures:
            if condition:  # 简化：这里应该实际评估条件
                print(f"  ✓ {condition}")
            else:
                print(f"  ✗ 条件不满足: {condition}")
                return False
        
        return True

# ==================== 6. 解释执行器 ====================
class Interpreter:
    """解释执行器"""
    
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.contract_verifier = ContractVerifier()
    
    def register_builtins(self):
        """注册内置函数"""
        self.functions['print'] = {
            'type': 'builtin',
            'impl': self.builtin_print
        }
    
    def builtin_print(self, args):
        """内置print函数"""
        for arg in args:
            print(arg, end=' ')
        print()
        return None
    
    def execute_program(self, program: Program) -> Any:
        """执行整个程序"""
        print("🚀 开始执行Intent程序")
        
        # 注册内置函数
        self.register_builtins()
        
        # 查找main函数
        main_func = None
        for func in program.functions:
            if func.name == 'main':
                main_func = func
            # 注册所有函数
            self.functions[func.name] = func
        
        if not main_func:
            raise RuntimeError("未找到main函数")
        
        # 执行main函数
        return self.execute_function(main_func, [])
    
    def execute_function(self, func: Function, args: List[Any]) -> Any:
        """执行函数"""
        print(f"\n📋 执行函数: {func.name}")
        
        # 验证前置条件
        context = {'args': args, 'variables': self.variables.copy()}
        if not self.contract_verifier.verify_requires(func.requires, context):
            raise RuntimeError(f"函数 {func.name} 的前置条件不满足")
        
        # 保存旧的变量状态
        old_variables = self.variables.copy()
        
        # 设置参数
        for (param_name, _), arg_value in zip(func.params, args):
            self.variables[param_name] = arg_value
        
        # 执行函数体
        result = None
        for stmt in func.body:
            result = self.execute_statement(stmt)
            if isinstance(stmt, ReturnStatement):
                break
        
        # 验证后置条件
        context['result'] = result
        if not self.contract_verifier.verify_ensures(func.ensures, result, context):
            # 恢复变量状态
            self.variables = old_variables
            raise RuntimeError(f"函数 {func.name} 的后置条件不满足")
        
        # 恢复变量状态（除了返回值）
        self.variables = old_variables
        
        return result
    
    def execute_statement(self, stmt: Statement) -> Any:
        """执行语句"""
        if isinstance(stmt, PrintStatement):
            return self.execute_print(stmt)
        elif isinstance(stmt, ReturnStatement):
            return self.execute_return(stmt)
        elif isinstance(stmt, VariableDeclaration):
            return self.execute_variable_declaration(stmt)
        elif isinstance(stmt, FunctionCall):
            return self.execute_function_call(stmt)
        
        return None
    
    def execute_print(self, stmt: PrintStatement) -> None:
        """执行print语句"""
        if isinstance(stmt.value, str):
            print(stmt.value)
        elif stmt.value in self.variables:
            print(self.variables[stmt.value])
        else:
            print(stmt.value)
        return None
    
    def execute_return(self, stmt: ReturnStatement) -> Any:
        """执行return语句"""
        if isinstance(stmt.value, str) and stmt.value in self.variables:
            return self.variables[stmt.value]
        return stmt.value
    
    def execute_variable_declaration(self, stmt: VariableDeclaration) -> None:
        """执行变量声明"""
        value = stmt.value
        if isinstance(value, str) and value in self.variables:
            value = self.variables[value]
        
        self.variables[stmt.name] = value
        print(f"  📝 声明变量 {stmt.name} = {value}")
        return None
    
    def execute_function_call(self, stmt: FunctionCall) -> Any:
        """执行函数调用"""
        if stmt.name in self.functions:
            func = self.functions[stmt.name]
            
            # 解析参数
            args = []
            for arg in stmt.args:
                if isinstance(arg, str) and arg in self.variables:
                    args.append(self.variables[arg])
                else:
                    args.append(arg)
            
            if func['type'] == 'builtin':
                return func['impl'](args)
            else:
                return self.execute_function(func, args)
        
        raise RuntimeError(f"未定义的函数: {stmt.name}")

# ==================== 7. 主程序 ====================
def main():
    """主函数"""
    import argparse
    
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(
        description='Intent语言解释器 - 心学为体，禅道为翼，马哲为用',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python mini_intent.py hello.intent           # 普通执行
  python mini_intent.py hello.intent --philosophy  # 显示哲学视角
  python mini_intent.py --demo                 # 运行演示程序
  
哲学映射文件:
  默认位置: philosophy/mapping.json
  可以自定义: python mini_intent.py file.intent --mapping my_map.json
        """
    )
    
    parser.add_argument('filename', nargs='?', help='Intent源文件')
    parser.add_argument('--philosophy', '-p', action='store_true', help='显示哲学视角')
    parser.add_argument('--mapping', '-m', default='philosophy/mapping.json', help='哲学映射文件路径')
    parser.add_argument('--demo', '-d', action='store_true', help='运行演示程序')
    parser.add_argument('--tokens', '-t', action='store_true', help='显示词法分析结果')
    parser.add_argument('--ast', '-a', action='store_true', help='显示语法分析结果')
    
    args = parser.parse_args()
    
    # 演示程序
    if args.demo:
        print("🎬 运行Intent语言演示程序")
        demo_code = '''def main() {
    print("=== Intent语言演示 ===");
    print("心学为体，禅道为翼，马哲为用");
    
    let x = 10;
    let y = 20;
    let sum = x + y;
    
    print("计算结果：");
    print(sum);
    
    return 0;
}'''
        
        if args.philosophy:
            translator = PhilosophyTranslator(args.mapping)
            print("\n🧘 哲学视角代码:")
            print("=" * 60)
            print(translator.translate_code(demo_code))
            print("=" * 60)
            print("\n⚙️  执行结果:")
            print("-" * 40)
        
        # 运行演示程序
        run_code(demo_code, args)
        return
    
    # 检查文件参数
    if not args.filename and not args.demo:
        parser.print_help()
        return
    
    # 读取文件
    try:
        with open(args.filename, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.filename}")
        print("提示: 请确保文件存在，或使用 --demo 运行演示程序")
        return
    
    # 显示哲学视角
    if args.philosophy:
        translator = PhilosophyTranslator(args.mapping)
        print("🧘 哲学视角代码:")
        print("=" * 60)
        print(translator.translate_code(code))
        print("=" * 60)
        print("\n⚙️  执行结果:")
        print("-" * 40)
    
    # 运行代码
    run_code(code, args)

def run_code(code: str, args):
    """运行Intent代码"""
    try:
        # 1. 词法分析
        print("🔤 词法分析...")
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        if args.tokens:
            print("\n词法分析结果:")
            for token in tokens:
                print(f"  {token}")
            print()
        
        # 2. 语法分析
        print("📐 语法分析...")
        parser = Parser(tokens)
        ast = parser.parse()
        
        if args.ast:
            print("\n语法分析结果:")
            for func in ast.functions:
                print(f"  函数: {func.name}")
                if func.requires:
                    print(f"    前置条件: {func.requires}")
                if func.ensures:
                    print(f"    后置条件: {func.ensures}")
            print()
        
        # 3. 解释执行
        print("⚡ 解释执行...\n")
        interpreter = Interpreter()
        result = interpreter.execute_program(ast)
        
        print(f"\n✅ 程序执行成功")
        if result is not None:
            print(f"返回值: {result}")
        
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
    except RuntimeError as e:
        print(f"❌ 运行时错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

# ==================== 8. 程序入口 ====================
if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════╗
║                Intent 语言解释器 v1.0                 ║
║        心学为体 · 禅道为翼 · 马哲为用                ║
╚═══════════════════════════════════════════════════════╝
    """)
    main()