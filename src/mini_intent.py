#!/usr/bin/env python3
"""
Intent语言完整解释器 v1.2
融合：心学为体，禅道为翼，马哲为用
目标：让代码清晰地表达意图
"""

import sys
import os
import re
import json
import math
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Tuple, Union, Callable
from enum import Enum
from collections import ChainMap

# ==================== 解决 Windows 的 readline 问题 ====================
try:
    # 尝试导入 readline（Unix/Linux/macOS）
    import readline
except ImportError:
    # Windows 系统，尝试 pyreadline3
    try:
        import pyreadline3 as readline
    except ImportError:
        # 如果都没有，创建一个虚拟的 readline
        class DummyReadline:
            @staticmethod
            def parse_and_bind(*args, **kwargs):
                pass
            @staticmethod
            def set_completer(*args, **kwargs):
                pass
            @staticmethod
            def add_history(*args, **kwargs):
                pass
        readline = DummyReadline()
        if sys.platform == "win32":
            print("提示: 可以安装 pyreadline3 以获得更好的命令行体验")
            print("安装命令: pip install pyreadline3")

# ==================== 常量定义 ====================
VERSION = "1.2.0"
PHILOSOPHY_SLOGAN = "心学为体，禅道为翼，马哲为用"

# ==================== 哲学翻译器 ====================
class PhilosophyTranslator:
    """哲学翻译器：连接代码与东方智慧"""
    
    def __init__(self, mapping_file: Optional[str] = None):
        self.mapping = self._load_mapping(mapping_file)
        self._setup_philosophy_explanations()
    
    def _load_mapping(self, mapping_file: Optional[str]) -> Dict:
        """加载哲学映射"""
        default_mapping = {
            "keywords": {
                "def": {"chinese": "功夫", "philosophy": "在事上磨炼的技艺"},
                "func": {"chinese": "功夫", "philosophy": "在事上磨炼的技艺"},
                "let": {"chinese": "格物", "philosophy": "探究具体事物"},
                "var": {"chinese": "变数", "philosophy": "变化之数"},
                "const": {"chinese": "常数", "philosophy": "不变之数"},
                "return": {"chinese": "归元", "philosophy": "回归本源"},
                "if": {"chinese": "若", "philosophy": "条件假设"},
                "else": {"chinese": "否则", "philosophy": "另一种可能"},
                "elif": {"chinese": "或若", "philosophy": "或者如果"},
                "for": {"chinese": "遍历", "philosophy": "逐一经历"},
                "while": {"chinese": "当", "philosophy": "持续条件满足"},
                "break": {"chinese": "破", "philosophy": "打破循环"},
                "continue": {"chinese": "续", "philosophy": "继续循环"},
                "match": {"chinese": "配", "philosophy": "模式匹配"},
                "requires": {"chinese": "事上练", "philosophy": "实践前的条件"},
                "ensures": {"chinese": "持志", "philosophy": "实践后的承诺"},
                "invariant": {"chinese": "常道", "philosophy": "始终不变"},
                "pure": {"chinese": "无住", "philosophy": "不执外相"},
                "effect": {"chinese": "着相", "philosophy": "与外交互"},
                "import": {"chinese": "引", "philosophy": "引入他山之石"},
                "from": {"chinese": "自", "philosophy": "来自"},
                "as": {"chinese": "为", "philosophy": "作为"},
                "print": {"chinese": "印", "philosophy": "印刻思想"},
                "Int": {"chinese": "整", "philosophy": "完整的数"},
                "Float": {"chinese": "浮", "philosophy": "浮动的数"},
                "String": {"chinese": "文", "philosophy": "文化的载体"},
                "Bool": {"chinese": "是非", "philosophy": "对错的判断"},
                "List": {"chinese": "列", "philosophy": "有序排列"},
                "Dict": {"chinese": "典", "philosophy": "键值对应"},
                "None": {"chinese": "空", "philosophy": "空无所有"},
                "True": {"chinese": "真", "philosophy": "真实不虚"},
                "False": {"chinese": "假", "philosophy": "虚妄不实"},
                "and": {"chinese": "且", "philosophy": "同时成立"},
                "or": {"chinese": "或", "philosophy": "任一成立"},
                "not": {"chinese": "非", "philosophy": "否定"},
                "in": {"chinese": "于", "philosophy": "在其中"},
                "is": {"chinese": "是", "philosophy": "等同"},
                "main": {"chinese": "主", "philosophy": "一切根本"}
            }
        }
        
        if mapping_file and os.path.exists(mapping_file):
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    user_mapping = json.load(f)
                # 深度合并映射
                default_mapping["keywords"].update(user_mapping.get("keywords", {}))
                print(f"🧘 已加载哲学映射: {mapping_file}")
            except Exception as e:
                print(f"⚠ 映射文件加载失败: {e}")
        
        return default_mapping
    
    def _setup_philosophy_explanations(self):
        """设置哲学解释"""
        self.philosophy_explanations = {
            "def": "心学为体：函数如功夫，需明确意图与契约",
            "requires": "事上练：实践前需条件具备，如心学之'在事上磨炼'",
            "ensures": "持志：实践后需坚守结果，如心学之'持志如心痛'",
            "pure": "禅道为翼：纯函数如'无住生心'，不执外相",
            "let": "格物：探究事物之理，明确变量本质",
            "return": "归元：回归本源，函数终有归宿",
            "if": "辩证：条件判断，如马哲之具体问题具体分析"
        }
    
    def translate_code(self, code: str, mode: str = "display") -> str:
        """翻译代码为哲学视角
        
        Args:
            code: 原始代码
            mode: 'display'显示哲学术语，'explain'显示哲学解释
        """
        lines = code.split('\n')
        translated_lines = []
        
        for line in lines:
            translated_line = line
            
            # 替换关键字
            for en_keyword, info in self.mapping["keywords"].items():
                chinese = info.get("chinese", en_keyword)
                # 使用单词边界匹配
                pattern = r'\b' + re.escape(en_keyword) + r'\b'
                translated_line = re.sub(pattern, chinese, translated_line)
            
            # 根据模式添加解释
            if mode == "explain" and not line.strip().startswith("//"):
                for en_keyword, info in self.mapping["keywords"].items():
                    if en_keyword in line and en_keyword in self.philosophy_explanations:
                        explanation = self.philosophy_explanations[en_keyword]
                        if "//" not in translated_line:
                            translated_line += f"  // {explanation}"
                        break
            
            translated_lines.append(translated_line)
        
        return '\n'.join(translated_lines)
    
    def get_keyword_philosophy(self, keyword: str) -> Dict[str, str]:
        """获取关键字的哲学信息"""
        if keyword in self.mapping["keywords"]:
            return self.mapping["keywords"][keyword]
        return {"chinese": keyword, "philosophy": ""}

# ==================== 词法分析 ====================
class TokenType(Enum):
    """Token类型枚举"""
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    SYMBOL = "SYMBOL"
    OPERATOR = "OPERATOR"
    EOF = "EOF"
    NEWLINE = "NEWLINE"

@dataclass
class Token:
    """词法单元"""
    type: TokenType
    value: str
    line: int
    column: int
    filename: str = ""
    
    def __str__(self):
        return f"{self.type.name}:{repr(self.value)}@{self.line}:{self.column}"
    
    def __repr__(self):
        return str(self)

class Lexer:
    """词法分析器 - 将代码分解为Token"""
    
    KEYWORDS = {
        'def', 'func', 'let', 'var', 'const', 'return', 'if', 'else', 'elif',
        'for', 'while', 'break', 'continue', 'match', 'requires', 'ensures',
        'invariant', 'pure', 'effect', 'import', 'from', 'as', 'export', 'default',
        'Int', 'Float', 'String', 'Bool', 'List', 'Dict', 'None', 'True', 'False',
        'and', 'or', 'not', 'in', 'is'
    }
    
    SYMBOLS = {
        '(', ')', '{', '}', '[', ']', ',', ':', ';', '=', '.', '->', '=>',
        '+', '-', '*', '/', '%', '**', '//', '==', '!=', '<', '>', '<=', '>=',
        '!', '&&', '||', '&', '|', '^', '~', '<<', '>>', ':=', '++', '--',
        '+=', '-=', '*=', '/=', '%=', '**=', '//=', '&=', '|=', '^=', '<<=', '>>='
    }
    
    SINGLE_SYMBOLS = set('(){}[],:;.=+-*/%<>!&|^~')
    
    def __init__(self, code: str, filename: str = ""):
        self.code = code
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
    def current_char(self) -> Optional[str]:
        """获取当前字符"""
        if self.pos < len(self.code):
            return self.code[self.pos]
        return None
    
    def peek_char(self, n: int = 1) -> Optional[str]:
        """向前看n个字符"""
        if self.pos + n < len(self.code):
            return self.code[self.pos + n]
        return None
    
    def advance(self, n: int = 1):
        """前进n个字符"""
        for _ in range(n):
            if self.current_char() == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self):
        """跳过空白字符"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """跳过注释"""
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '*':
            self.advance(2)  # 跳过/*
            while (self.current_char() and 
                   not (self.current_char() == '*' and self.peek_char() == '/')):
                self.advance()
            if self.current_char() == '*':
                self.advance(2)  # 跳过*/
    
    def read_string(self):
        """读取字符串字面量"""
        quote = self.current_char()
        start_pos = self.pos
        self.advance()  # 跳过开头的引号
        
        while self.current_char() and self.current_char() != quote:
            if self.current_char() == '\\':  # 处理转义字符
                self.advance()
            self.advance()
        
        if not self.current_char():
            raise SyntaxError(f"未结束的字符串，行 {self.line}")
        
        value = self.code[start_pos + 1:self.pos]
        self.tokens.append(Token(TokenType.STRING, value, self.line, self.column, self.filename))
        self.advance()  # 跳过结尾的引号
    
    def read_number(self):
        """读取数字"""
        start_pos = self.pos
        
        # 读取整数部分
        while self.current_char() and self.current_char().isdigit():
            self.advance()
        
        # 检查小数部分
        if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
            self.advance()  # 跳过小数点
            while self.current_char() and self.current_char().isdigit():
                self.advance()
        
        # 检查科学计数法
        if self.current_char() and self.current_char().lower() == 'e':
            self.advance()
            if self.current_char() in '+-':
                self.advance()
            while self.current_char() and self.current_char().isdigit():
                self.advance()
        
        value = self.code[start_pos:self.pos]
        self.tokens.append(Token(TokenType.NUMBER, value, self.line, self.column, self.filename))
    
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
        
        self.tokens.append(Token(token_type, value, self.line, self.column, self.filename))
    
    def read_operator_or_symbol(self):
        """读取运算符或符号"""
        char = self.current_char()
        
        # 先检查是否是标点符号
        if char in '(){}[],:;.':
            self.tokens.append(Token(TokenType.SYMBOL, char, self.line, self.column, self.filename))
            self.advance()
            return
        
        # 尝试读取运算符
        start_pos = self.pos
        for length in range(3, 0, -1):
            if self.pos + length <= len(self.code):
                candidate = self.code[self.pos:self.pos + length]
                if candidate in self.SYMBOLS:
                    self.tokens.append(Token(TokenType.OPERATOR, candidate, self.line, self.column, self.filename))
                    self.advance(length)
                    return
        
        raise SyntaxError(f"未知符号: '{char}'，行 {self.line}，列 {self.column}")
    
    def tokenize(self) -> List[Token]:
        """执行词法分析"""
        while self.current_char():
            # 跳过空白
            if self.current_char() in ' \t\r':
                self.skip_whitespace()
                continue
            
            # 跳过注释
            if (self.current_char() == '#' or 
                (self.current_char() == '/' and self.peek_char() in ['/', '*'])):
                self.skip_comment()
                continue
            
            # 处理换行
            if self.current_char() == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column, self.filename))
                self.advance()
                continue
            
            # 字符串
            if self.current_char() in ('"', "'"):
                self.read_string()
                continue
            
            # 数字
            if self.current_char().isdigit() or (self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit()):
                self.read_number()
                continue
            
            # 标识符或关键字
            if self.current_char().isalpha() or self.current_char() == '_':
                self.read_identifier()
                continue
            
            # 运算符或符号
            self.read_operator_or_symbol()
        
        # 添加EOF标记
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column, self.filename))
        return self.tokens

# ==================== 抽象语法树 ====================
@dataclass
class ASTNode:
    """抽象语法树基类"""
    line: int = 0
    column: int = 0
    filename: str = ""
    
    def accept(self, visitor: 'ASTVisitor'):
        """访问者模式"""
        method_name = f'visit_{self.__class__.__name__.lower()}'
        method = getattr(visitor, method_name, visitor.generic_visit)
        return method(self)

@dataclass
class Program(ASTNode):
    """程序节点"""
    statements: List[ASTNode] = field(default_factory=list)
    functions: Dict[str, 'FunctionDef'] = field(default_factory=dict)
    
    def add_statement(self, stmt: ASTNode):
        self.statements.append(stmt)
    
    def add_function(self, func: 'FunctionDef'):
        self.functions[func.name] = func

@dataclass
class FunctionDef(ASTNode):
    """函数定义节点"""
    name: str = ""
    params: List[Tuple[str, str]] = field(default_factory=list)  # (参数名, 类型)
    return_type: Optional[str] = None
    requires: List['Expression'] = field(default_factory=list)  # 前置条件
    ensures: List['Expression'] = field(default_factory=list)   # 后置条件
    body: List[ASTNode] = field(default_factory=list)  # 函数体语句
    is_pure: bool = False
    effects: List[str] = field(default_factory=list)
    
    def get_param_names(self) -> List[str]:
        return [name for name, _ in self.params]

@dataclass
class VariableDecl(ASTNode):
    """变量声明"""
    name: str = ""
    var_type: Optional[str] = None
    value: Optional['Expression'] = None
    is_const: bool = False

@dataclass
class Assignment(ASTNode):
    """赋值语句"""
    target: str = ""
    value: 'Expression' = None
    op: str = "="  # =, +=, -=, 等

@dataclass
class ReturnStmt(ASTNode):
    """返回语句"""
    value: Optional['Expression'] = None

@dataclass
class PrintStmt(ASTNode):
    """打印语句"""
    args: List['Expression'] = field(default_factory=list)

@dataclass
class IfStmt(ASTNode):
    """条件语句"""
    condition: 'Expression' = None
    then_branch: List[ASTNode] = field(default_factory=list)
    elif_branches: List[Tuple['Expression', List[ASTNode]]] = field(default_factory=list)
    else_branch: List[ASTNode] = field(default_factory=list)

@dataclass
class WhileStmt(ASTNode):
    """循环语句"""
    condition: 'Expression' = None
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class ForStmt(ASTNode):
    """for循环"""
    var: str = ""
    iterable: 'Expression' = None
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class BreakStmt(ASTNode):
    """break语句"""
    pass

@dataclass
class ContinueStmt(ASTNode):
    """continue语句"""
    pass

@dataclass
class ImportStmt(ASTNode):
    """import语句"""
    module_name: str = ""
    alias: str = ""
    import_path: str = ""

@dataclass
class ExportStmt(ASTNode):
    """export语句"""
    exports: list = field(default_factory=list)
    is_default: bool = False

@dataclass
class Expression(ASTNode):
    """表达式基类"""
    pass

@dataclass
@dataclass
class MemberAccess(Expression):
    """成员访问表达式，如 module.function"""
    obj: Expression = None
    member: str = ""
    line: int = 0
    column: int = 0

@dataclass
class Literal(Expression):
    """字面量表达式"""
    value: Any = None
    literal_type: str = ""  # 'int', 'float', 'string', 'bool', 'none'
    
    def __post_init__(self):
        if self.literal_type == "" and self.value is not None:
            if isinstance(self.value, bool):
                self.literal_type = 'bool'
            elif isinstance(self.value, (int, float)):
                self.literal_type = 'int' if isinstance(self.value, int) else 'float'
            elif isinstance(self.value, str):
                self.literal_type = 'string'
            elif self.value is None:
                self.literal_type = 'none'

@dataclass
class Variable(Expression):
    """变量表达式"""
    name: str = ""

@dataclass
class BinaryOp(Expression):
    """二元运算表达式"""
    left: Expression = None
    op: str = ""
    right: Expression = None

@dataclass
class UnaryOp(Expression):
    """一元运算表达式"""
    op: str = ""
    operand: Expression = None

@dataclass
class CallExpr(Expression):
    """函数调用表达式"""
    func: str = ""
    args: List[Expression] = field(default_factory=list)

# ==================== 语法分析器 ====================
class Parser:
    """语法分析器 - 将Token流转换为AST"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else Token(TokenType.EOF, "", 0, 0)
    
    def advance(self):
        """前进到下一个token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token(TokenType.EOF, "", 0, 0)
    
    def peek(self) -> Token:
        """查看下一个token"""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(TokenType.EOF, "", 0, 0)
    
    def expect(self, token_type: TokenType, value: Optional[str] = None) -> Token:
        """期望当前token符合要求"""
        if self.current_token.type != token_type:
            # 修复：提供更友好的错误信息
            expected = f"{token_type.value}" + (f" '{value}'" if value else "")
            got = f"{self.current_token.type.value} '{self.current_token.value}'"
            raise SyntaxError(f"期望 {expected}，但得到 {got}，行 {self.current_token.line}")
        
        if value is not None and self.current_token.value != value:
            raise SyntaxError(f"期望 '{value}'，但得到 '{self.current_token.value}'，行 {self.current_token.line}")
        
        token = self.current_token
        self.advance()
        return token
    
    def match(self, token_type: TokenType, value: Optional[str] = None) -> bool:
        """检查当前token是否匹配"""
        if self.current_token.type != token_type:
            return False
        if value is not None and self.current_token.value != value:
            return False
        return True
    
    def parse(self) -> Program:
        """解析整个程序"""
        program = Program()
        
        while not self.match(TokenType.EOF):
            # 跳过无关token
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue
            
            # 解析函数定义
            if self.match(TokenType.KEYWORD, 'def'):
                func = self.parse_function_def()
                program.add_function(func)
            # 解析语句
            else:
                stmt = self.parse_statement()
                if stmt:
                    program.add_statement(stmt)
        
        return program
    
    def parse_function_def(self) -> FunctionDef:
        """解析函数定义"""
        start_token = self.expect(TokenType.KEYWORD, 'def')
        func = FunctionDef(line=start_token.line, column=start_token.column, filename=start_token.filename)
        
        # 函数名
        func.name = self.expect(TokenType.IDENTIFIER).value
        
        # 参数列表
        self.expect(TokenType.SYMBOL, '(')
        func.params = self.parse_parameter_list()
        self.expect(TokenType.SYMBOL, ')')
        
        # 返回类型
        if self.match(TokenType.OPERATOR, '->'):
            self.advance()
            func.return_type = self.expect(TokenType.IDENTIFIER).value
        
        # 契约
        while True:
            if self.match(TokenType.KEYWORD, 'requires'):
                self.advance()
                func.requires.append(self.parse_expression())
            elif self.match(TokenType.KEYWORD, 'ensures'):
                self.advance()
                func.ensures.append(self.parse_expression())
            elif self.match(TokenType.KEYWORD, 'pure'):
                self.advance()
                func.is_pure = True
            elif self.match(TokenType.KEYWORD, 'effect'):
                self.advance()
                self.expect(TokenType.SYMBOL, '[')
                while not self.match(TokenType.SYMBOL, ']'):
                    if self.match(TokenType.IDENTIFIER) or self.match(TokenType.STRING):
                        func.effects.append(self.current_token.value)
                        self.advance()
                    if self.match(TokenType.SYMBOL, ','):
                        self.advance()
                self.expect(TokenType.SYMBOL, ']')
            else:
                break
        
        # 函数体
        self.expect(TokenType.SYMBOL, '{')
        # 跳过可能的换行符
        while self.match(TokenType.NEWLINE):
            self.advance()
        while not self.match(TokenType.SYMBOL, '}'):
            stmt = self.parse_statement()
            if stmt:
                func.body.append(stmt)
            # 跳过可能的换行符
            while self.match(TokenType.NEWLINE):
                self.advance()
        self.expect(TokenType.SYMBOL, '}')
        
        return func
    
    def parse_parameter_list(self) -> List[Tuple[str, str]]:
        """解析参数列表 - 支持有类型和无类型参数"""
        params = []
        
        if not self.match(TokenType.SYMBOL, ')'):
            # 第一个参数
            param_name = self.expect(TokenType.IDENTIFIER).value
            # 检查是否有类型标注 (param: Type)
            param_type = "Any"  # 默认类型
            if self.match(TokenType.SYMBOL, ':'):
                self.advance()  # 消耗冒号
                param_type = self.expect(TokenType.IDENTIFIER).value
            params.append((param_name, param_type))
            
            # 更多参数
            while self.match(TokenType.SYMBOL, ','):
                self.advance()  # 消耗逗号
                param_name = self.expect(TokenType.IDENTIFIER).value
                # 检查是否有类型标注
                param_type = "Any"
                if self.match(TokenType.SYMBOL, ':'):
                    self.advance()  # 消耗冒号
                    param_type = self.expect(TokenType.IDENTIFIER).value
                params.append((param_name, param_type))
        
        return params
    
    def parse_statement(self) -> Optional[ASTNode]:
        """解析语句"""
        # 跳过开头的换行符 - 关键修复
        while self.match(TokenType.NEWLINE):
            self.advance()
        
        # 检查是否遇到函数体结束符 - 关键修复
        if self.match(TokenType.SYMBOL, '}'):
            return None
        
        # 空语句
        if self.match(TokenType.SYMBOL, ';'):
            self.advance()
            return None
        
        # 变量声明
        if self.match(TokenType.KEYWORD, 'let') or self.match(TokenType.KEYWORD, 'var') or self.match(TokenType.KEYWORD, 'const'):
            return self.parse_variable_decl()
        
        # 返回语句
        if self.match(TokenType.KEYWORD, 'return'):
            return self.parse_return_stmt()
        
        # 打印语句
        if self.match(TokenType.IDENTIFIER, 'print'):
            return self.parse_print_stmt()
        
        # 条件语句
        if self.match(TokenType.KEYWORD, 'if'):
            return self.parse_if_stmt()
        
        # 循环语句
        if self.match(TokenType.KEYWORD, 'while'):
            return self.parse_while_stmt()
        
        if self.match(TokenType.KEYWORD, 'for'):
            return self.parse_for_stmt()
        
        # 控制语句
        if self.match(TokenType.KEYWORD, 'break'):
            stmt = BreakStmt(line=self.current_token.line, column=self.current_token.column)
            self.advance()
            self.expect(TokenType.SYMBOL, ';')
            return stmt
        
        if self.match(TokenType.KEYWORD, 'continue'):
            stmt = ContinueStmt(line=self.current_token.line, column=self.current_token.column)
            self.advance()
            self.expect(TokenType.SYMBOL, ';')
            return stmt
        
        # Import语句
        if self.match(TokenType.KEYWORD, 'import'):
            return self.parse_import_stmt()
        
        # Export语句
        if self.match(TokenType.KEYWORD, 'export'):
            return self.parse_export_stmt()
        
        # 赋值语句
        if self.match(TokenType.IDENTIFIER) and self.peek().value in ('=', '+=', '-=', '*=', '/=', '%=', '**='):
            return self.parse_assignment()
        
        # 函数调用
        if self.match(TokenType.IDENTIFIER) and self.peek().value == '(':
            return self.parse_expression_stmt()
        
        # 表达式语句
        expr = self.parse_expression()
        if expr:
            self.expect(TokenType.SYMBOL, ';')
            return expr
        
        return None
    
    def parse_variable_decl(self) -> VariableDecl:
        """解析变量声明"""
        keyword = self.current_token.value
        is_const = keyword == 'const'
        start_token = self.current_token
        self.advance()  # 跳过let/var/const
        
        decl = VariableDecl(
            line=start_token.line,
            column=start_token.column,
            is_const=is_const
        )
        
        # 变量名
        decl.name = self.expect(TokenType.IDENTIFIER).value
        
        # 类型注解
        if self.match(TokenType.SYMBOL, ':'):
            self.advance()
            decl.var_type = self.expect(TokenType.IDENTIFIER).value
        
        # 初始值
        if self.match(TokenType.OPERATOR, '='):
            self.advance()
            decl.value = self.parse_expression()
        
        self.expect(TokenType.SYMBOL, ';')
        return decl
    
    def parse_import_stmt(self) -> ImportStmt:
        """解析import语句"""
        start_token = self.expect(TokenType.KEYWORD, 'import')
        stmt = ImportStmt(line=start_token.line, column=start_token.column)
        
        # 解析模块名（支持点号分隔，如 std.math）
        parts = []
        parts.append(self.expect(TokenType.IDENTIFIER).value)
        
        # 支持点号分隔的模块名 (如 import std.math)
        while self.match(TokenType.SYMBOL, '.'):
            self.advance()  # 消耗点号
            parts.append(self.expect(TokenType.IDENTIFIER).value)
        
        stmt.module_name = ".".join(parts)
        
        # 检查是否有别名: import xxx as yyy
        if self.match(TokenType.KEYWORD, 'as'):
            self.advance()
            stmt.alias = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.SYMBOL, ';')
        return stmt
    
    def parse_export_stmt(self) -> ExportStmt:
        """解析export语句"""
        start_token = self.expect(TokenType.KEYWORD, 'export')
        stmt = ExportStmt(line=start_token.line, column=start_token.column)
        
        # 检查是否是默认导出: export default
        if self.match(TokenType.KEYWORD, 'default'):
            self.advance()
            stmt.is_default = True
            # 默认导出可以是函数或表达式
            if self.match(TokenType.KEYWORD, 'def'):
                # export default def xxx() {}
                func = self.parse_function_def()
                stmt.exports.append(func.name)
                # export def 后面不需要分号
            else:
                # export default <expression>
                expr = self.parse_expression()
                stmt.exports.append(expr)
                self.expect(TokenType.SYMBOL, ';')
        else:
            # 普通导出: export { xxx, yyy } 或 export def xxx() {}
            if self.match(TokenType.SYMBOL, '{'):
                self.advance()
                # export { name1, name2, ... }
                while not self.match(TokenType.SYMBOL, '}'):
                    name_token = self.expect(TokenType.IDENTIFIER)
                    stmt.exports.append(name_token.value)
                    
                    if self.match(TokenType.SYMBOL, ','):
                        self.advance()
                    else:
                        break
                self.expect(TokenType.SYMBOL, '}')
                self.expect(TokenType.SYMBOL, ';')
            elif self.match(TokenType.KEYWORD, 'def'):
                # export def function_name() {}
                func = self.parse_function_def()
                stmt.exports.append(func.name)
                # export def 后面不需要分号
            else:
                # export let/var/const
                decl = self.parse_variable_decl()
                stmt.exports.append(decl.name)
                # 变量声明已经包含了分号
        
        return stmt
    
    def parse_return_stmt(self) -> ReturnStmt:
        """解析返回语句"""
        start_token = self.expect(TokenType.KEYWORD, 'return')
        stmt = ReturnStmt(line=start_token.line, column=start_token.column)
        
        if not self.match(TokenType.SYMBOL, ';'):
            stmt.value = self.parse_expression()
        
        self.expect(TokenType.SYMBOL, ';')
        return stmt
    
    def parse_print_stmt(self) -> PrintStmt:
        """解析打印语句"""
        start_token = self.expect(TokenType.IDENTIFIER, 'print')
        stmt = PrintStmt(line=start_token.line, column=start_token.column)
        
        self.expect(TokenType.SYMBOL, '(')
        
        # 解析参数
        if not self.match(TokenType.SYMBOL, ')'):
            stmt.args.append(self.parse_expression())
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                stmt.args.append(self.parse_expression())
        
        self.expect(TokenType.SYMBOL, ')')
        self.expect(TokenType.SYMBOL, ';')
        return stmt
    
    def parse_if_stmt(self) -> IfStmt:
        """解析条件语句"""
        start_token = self.expect(TokenType.KEYWORD, 'if')
        stmt = IfStmt(line=start_token.line, column=start_token.column)
        
        # 条件
        stmt.condition = self.parse_expression()
        
        # then分支
        self.expect(TokenType.SYMBOL, '{')
        while not self.match(TokenType.SYMBOL, '}'):
            branch_stmt = self.parse_statement()
            if branch_stmt:
                stmt.then_branch.append(branch_stmt)
        self.expect(TokenType.SYMBOL, '}')
        
        # elif分支
        while self.match(TokenType.KEYWORD, 'elif'):
            self.advance()
            elif_cond = self.parse_expression()
            self.expect(TokenType.SYMBOL, '{')
            elif_body = []
            while not self.match(TokenType.SYMBOL, '}'):
                branch_stmt = self.parse_statement()
                if branch_stmt:
                    elif_body.append(branch_stmt)
            self.expect(TokenType.SYMBOL, '}')
            stmt.elif_branches.append((elif_cond, elif_body))
        
        # else分支
        if self.match(TokenType.KEYWORD, 'else'):
            self.advance()
            self.expect(TokenType.SYMBOL, '{')
            while not self.match(TokenType.SYMBOL, '}'):
                branch_stmt = self.parse_statement()
                if branch_stmt:
                    stmt.else_branch.append(branch_stmt)
            self.expect(TokenType.SYMBOL, '}')
        
        return stmt
    
    def parse_while_stmt(self) -> WhileStmt:
        """解析while循环"""
        start_token = self.expect(TokenType.KEYWORD, 'while')
        stmt = WhileStmt(line=start_token.line, column=start_token.column)
        
        # 条件
        stmt.condition = self.parse_expression()
        
        # 循环体
        self.expect(TokenType.SYMBOL, '{')
        while not self.match(TokenType.SYMBOL, '}'):
            body_stmt = self.parse_statement()
            if body_stmt:
                stmt.body.append(body_stmt)
        self.expect(TokenType.SYMBOL, '}')
        
        return stmt
    
    def parse_for_stmt(self) -> ForStmt:
        """解析for循环"""
        start_token = self.expect(TokenType.KEYWORD, 'for')
        stmt = ForStmt(line=start_token.line, column=start_token.column)
        
        # 循环变量
        stmt.var = self.expect(TokenType.IDENTIFIER).value
        
        # in关键字
        self.expect(TokenType.KEYWORD, 'in')
        
        # 可迭代对象
        stmt.iterable = self.parse_expression()
        
        # 循环体
        self.expect(TokenType.SYMBOL, '{')
        while not self.match(TokenType.SYMBOL, '}'):
            body_stmt = self.parse_statement()
            if body_stmt:
                stmt.body.append(body_stmt)
        self.expect(TokenType.SYMBOL, '}')
        
        return stmt
    
    def parse_assignment(self) -> Assignment:
        """解析赋值语句"""
        target = self.expect(TokenType.IDENTIFIER).value
        op_token = self.expect(TokenType.OPERATOR)
        stmt = Assignment(
            target=target,
            op=op_token.value,
            line=op_token.line,
            column=op_token.column
        )
        
        stmt.value = self.parse_expression()
        self.expect(TokenType.SYMBOL, ';')
        return stmt
    
    def parse_expression_stmt(self) -> Expression:
        """解析表达式语句"""
        expr = self.parse_expression()
        self.expect(TokenType.SYMBOL, ';')
        return expr
    
    def parse_expression(self) -> Expression:
        """解析表达式"""
        # 跳过开头的换行符 - 关键修复
        while self.match(TokenType.NEWLINE):
            self.advance()
        
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Expression:
        """解析逻辑或"""
        expr = self.parse_logical_and()
        
        while self.match(TokenType.KEYWORD, 'or'):
            op_token = self.current_token
            self.advance()
            right = self.parse_logical_and()
            expr = BinaryOp(left=expr, op='or', right=right, line=op_token.line, column=op_token.column)
        
        return expr
    
    def parse_logical_and(self) -> Expression:
        """解析逻辑与"""
        expr = self.parse_comparison()
        
        while self.match(TokenType.KEYWORD, 'and'):
            op_token = self.current_token
            self.advance()
            right = self.parse_comparison()
            expr = BinaryOp(left=expr, op='and', right=right, line=op_token.line, column=op_token.column)
        
        return expr
    
    def parse_comparison(self) -> Expression:
        """解析比较表达式"""
        expr = self.parse_addition()
        
        while self.match(TokenType.OPERATOR) and self.current_token.value in ('==', '!=', '<', '>', '<=', '>='):
            op_token = self.current_token
            self.advance()
            right = self.parse_addition()
            expr = BinaryOp(left=expr, op=op_token.value, right=right, line=op_token.line, column=op_token.column)
        
        return expr
    
    def parse_addition(self) -> Expression:
        """解析加减法"""
        expr = self.parse_multiplication()
        
        while self.match(TokenType.OPERATOR) and self.current_token.value in ('+', '-'):
            op_token = self.current_token
            self.advance()
            right = self.parse_multiplication()
            expr = BinaryOp(left=expr, op=op_token.value, right=right, line=op_token.line, column=op_token.column)
        
        return expr
    
    def parse_multiplication(self) -> Expression:
        """解析乘除法"""
        expr = self.parse_unary()
        
        while self.match(TokenType.OPERATOR) and self.current_token.value in ('*', '/', '%', '//', '**'):
            op_token = self.current_token
            self.advance()
            right = self.parse_unary()
            expr = BinaryOp(left=expr, op=op_token.value, right=right, line=op_token.line, column=op_token.column)
        
        return expr
    
    def parse_unary(self) -> Expression:
        """解析一元运算"""
        if self.match(TokenType.OPERATOR) and self.current_token.value in ('+', '-', '!'):
            op_token = self.current_token
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(op=op_token.value, operand=operand, line=op_token.line, column=op_token.column)
        
        return self.parse_primary()
    
    def parse_primary(self) -> Expression:
        """解析基本表达式"""
        # 先跳过可能存在的换行符 - 关键修复
        while self.match(TokenType.NEWLINE):
            self.advance()
        
        token = self.current_token
        
        # 字面量
        if self.match(TokenType.NUMBER):
            self.advance()
            try:
                value = int(token.value) if '.' not in token.value and 'e' not in token.value.lower() else float(token.value)
            except ValueError:
                value = float(token.value)
            return Literal(value=value, literal_type='int' if isinstance(value, int) else 'float', 
                          line=token.line, column=token.column)
        
        elif self.match(TokenType.STRING):
            self.advance()
            return Literal(value=token.value, literal_type='string', line=token.line, column=token.column)
        
        elif self.match(TokenType.KEYWORD, 'True'):
            self.advance()
            return Literal(value=True, literal_type='bool', line=token.line, column=token.column)
        
        elif self.match(TokenType.KEYWORD, 'False'):
            self.advance()
            return Literal(value=False, literal_type='bool', line=token.line, column=token.column)
        
        elif self.match(TokenType.KEYWORD, 'None'):
            self.advance()
            return Literal(value=None, literal_type='none', line=token.line, column=token.column)
        
        # 变量
        elif self.match(TokenType.IDENTIFIER):
            self.advance()
            
            # 函数调用
            if self.match(TokenType.SYMBOL, '('):
                return self.parse_call_expr(token.value)
            
            # 属性访问 (如 std.math)
            result = Variable(name=token.value, line=token.line, column=token.column)
            
            # 支持连续的属性访问: std.math.add
            while True:
                if self.match(TokenType.SYMBOL, '.'):
                    self.advance()  # 消耗点号
                    if self.match(TokenType.IDENTIFIER):
                        member_name = self.current_token.value
                        member_token = self.current_token
                        self.advance()
                        result = MemberAccess(obj=result, member=member_name, line=member_token.line, column=member_token.column)
                    else:
                        raise SyntaxError(f"期望属性名，但得到 {self.current_token}")
                elif self.match(TokenType.SYMBOL, '('):
                    # 函数调用 - 需要处理MemberAccess作为函数的情况
                    if isinstance(result, MemberAccess):
                        # 返回一个特殊的CallExpr，包含MemberAccess信息
                        call = CallExpr(func=result, line=result.line, column=result.column)
                        self.expect(TokenType.SYMBOL, '(')
                        # 解析参数
                        if not self.match(TokenType.SYMBOL, ')'):
                            call.args.append(self.parse_expression())
                            while self.match(TokenType.SYMBOL, ','):
                                self.advance()
                                call.args.append(self.parse_expression())
                        self.expect(TokenType.SYMBOL, ')')
                        result = call
                    elif isinstance(result, Variable):
                        result = self.parse_call_expr(result.name)
                    else:
                        break
                else:
                    break
            
            return result
        
        # 列表
        elif self.match(TokenType.SYMBOL, '['):
            return self.parse_list_expr()
        
        # 括号表达式
        elif self.match(TokenType.SYMBOL, '('):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.SYMBOL, ')')
            return expr
        
        # 修改错误信息，提供更友好的提示
        if token.type == TokenType.NEWLINE:
            raise SyntaxError(f"表达式不完整，在第{token.line}行第{token.column}列意外换行")
        else:
            raise SyntaxError(f"无法解析表达式，意外的token: {token}，行 {token.line}")
    
    def parse_call_expr(self, func_name: str) -> CallExpr:
        """解析函数调用"""
        start_token = self.current_token
        self.expect(TokenType.SYMBOL, '(')
        
        call = CallExpr(func=func_name, line=start_token.line, column=start_token.column)
        
        # 解析参数
        if not self.match(TokenType.SYMBOL, ')'):
            call.args.append(self.parse_expression())
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                call.args.append(self.parse_expression())
        
        self.expect(TokenType.SYMBOL, ')')
        return call
    
    def parse_list_expr(self) -> 'ListExpr':
        """解析列表表达式"""
        start_token = self.expect(TokenType.SYMBOL, '[')
        expr = ListExpr(line=start_token.line, column=start_token.column)
        
        if not self.match(TokenType.SYMBOL, ']'):
            expr.elements.append(self.parse_expression())
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                expr.elements.append(self.parse_expression())
        
        self.expect(TokenType.SYMBOL, ']')
        return expr

@dataclass
class ListExpr(Expression):
    """列表表达式"""
    elements: List[Expression] = field(default_factory=list)

# ==================== 类型系统 ====================
class Type:
    """类型基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        if isinstance(other, Type):
            return self.name == other.name
        return False
    
    def can_assign_from(self, other: 'Type') -> bool:
        """检查是否可以从此类型赋值"""
        return self == other

class IntType(Type):
    """整数类型"""
    
    def __init__(self):
        super().__init__("Int")
    
    def can_assign_from(self, other: Type) -> bool:
        return isinstance(other, (IntType, FloatType))

class FloatType(Type):
    """浮点数类型"""
    
    def __init__(self):
        super().__init__("Float")
    
    def can_assign_from(self, other: Type) -> bool:
        return isinstance(other, (IntType, FloatType))

class StringType(Type):
    """字符串类型"""
    
    def __init__(self):
        super().__init__("String")

class BoolType(Type):
    """布尔类型"""
    
    def __init__(self):
        super().__init__("Bool")

class ListType(Type):
    """列表类型"""
    
    def __init__(self, element_type: Type):
        super().__init__(f"List[{element_type}]")
        self.element_type = element_type
    
    def can_assign_from(self, other: Type) -> bool:
        if isinstance(other, ListType):
            return self.element_type.can_assign_from(other.element_type)
        return False

# ==================== 运行时值 ====================
class RuntimeValue:
    """运行时值基类"""
    
    def __init__(self, type: Type, value: Any = None):
        self.type = type
        self.value = value
        self.is_constant = False
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return f"{self.type}({repr(self.value)})"
    
    def get_type(self) -> Type:
        return self.type
    
    def to_bool(self) -> bool:
        """转换为布尔值"""
        return bool(self.value)
    
    def copy(self) -> 'RuntimeValue':
        """创建副本 - 修复：返回正确的子类类型"""
        # 根据类型返回正确的子类实例
        if isinstance(self, IntValue):
            return IntValue(self.value)
        elif isinstance(self, FloatValue):
            return FloatValue(self.value)
        elif isinstance(self, StringValue):
            return StringValue(self.value)
        elif isinstance(self, BoolValue):
            return BoolValue(self.value)
        elif isinstance(self, ListValue):
            return ListValue(self.value.copy() if self.value else [])
        else:
            return RuntimeValue(self.type, self.value)

class IntValue(RuntimeValue):
    """整数值"""
    
    def __init__(self, value: int):
        super().__init__(IntType(), value)
    
    def __str__(self):
        return str(self.value)

class FloatValue(RuntimeValue):
    """浮点数值"""
    
    def __init__(self, value: float):
        super().__init__(FloatType(), value)
    
    def __str__(self):
        return str(self.value)

class StringValue(RuntimeValue):
    """字符串值"""
    
    def __init__(self, value: str):
        super().__init__(StringType(), value)
    
    def __str__(self):
        return self.value

class BoolValue(RuntimeValue):
    """布尔值"""
    
    def __init__(self, value: bool):
        super().__init__(BoolType(), value)
    
    def __str__(self):
        return "真" if self.value else "假"  # 中文输出
    
    def to_bool(self) -> bool:
        return self.value

class ListValue(RuntimeValue):
    """列表值"""
    
    def __init__(self, values: List[RuntimeValue], element_type: Type):
        super().__init__(ListType(element_type), values)
    
    def __str__(self):
        items = ", ".join(str(v) for v in self.value)
        return f"[{items}]"
    
    def get(self, index: int) -> RuntimeValue:
        if 0 <= index < len(self.value):
            return self.value[index]
        raise IndexError(f"列表索引 {index} 越界")
    
    def set(self, index: int, value: RuntimeValue):
        if 0 <= index < len(self.value):
            if not self.type.element_type.can_assign_from(value.type):
                raise TypeError(f"无法将 {value.type} 赋值给 {self.type.element_type}")
            self.value[index] = value
        else:
            raise IndexError(f"列表索引 {index} 越界")

# ==================== 作用域 ====================
class Scope:
    """作用域"""
    
    def __init__(self, parent: Optional['Scope'] = None):
        self.parent = parent
        self.symbols: Dict[str, RuntimeValue] = {}
        self.constants: set[str] = set()
    
    def declare(self, name: str, value: RuntimeValue, is_const: bool = False, allow_redefine: bool = False):
        """声明变量"""
        if name in self.symbols and not allow_redefine:
            raise NameError(f"变量 '{name}' 已在此作用域中声明")
        
        self.symbols[name] = value
        if is_const:
            self.constants.add(name)
    
    def assign(self, name: str, value: RuntimeValue):
        """赋值变量"""
        if name in self.symbols:
            if name in self.constants:
                raise ValueError(f"无法修改常量 '{name}'")
            self.symbols[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise NameError(f"未定义的变量 '{name}'")
    
    def get(self, name: str) -> RuntimeValue:
        """获取变量值"""
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"未定义的变量 '{name}'")
    
    def has(self, name: str) -> bool:
        """检查变量是否存在"""
        if name in self.symbols:
            return True
        elif self.parent:
            return self.parent.has(name)
        return False
    
    def enter(self) -> 'Scope':
        """进入子作用域"""
        return Scope(parent=self)
    
    def exit(self) -> Optional['Scope']:
        """退出当前作用域"""
        return self.parent

# ==================== 契约验证器 ====================
class ContractVerifier:
    """契约验证器 - 真正验证requires/ensures"""
    
    def __init__(self, interpreter: 'Interpreter'):
        self.interpreter = interpreter
        self.error_messages = []
    
    def verify_requires(self, requires: List[Expression], context: Dict[str, Any]) -> bool:
        """验证前置条件"""
        if not requires:
            return True
        
        self.error_messages = []
        all_passed = True
        
        for i, condition in enumerate(requires):
            try:
                result = self.interpreter.evaluate_expression(condition, context)
                if isinstance(result, BoolValue) and result.value:
                    print(f"  ✓ 前置条件{i+1}: {self.expr_to_str(condition)}")
                else:
                    print(f"  ✗ 前置条件{i+1}失败: {self.expr_to_str(condition)}")
                    self.error_messages.append(f"前置条件{i+1}失败: {self.expr_to_str(condition)}")
                    all_passed = False
            except Exception as e:
                print(f"  ⚠ 前置条件{i+1}验证错误: {e}")
                self.error_messages.append(f"前置条件{i+1}验证错误: {e}")
                all_passed = False
        
        return all_passed
    
    def verify_ensures(self, ensures: List[Expression], result: RuntimeValue, context: Dict[str, Any]) -> bool:
        """验证后置条件"""
        if not ensures:
            return True
        
        all_passed = True
        context['result'] = result
        
        for i, condition in enumerate(ensures):
            try:
                eval_result = self.interpreter.evaluate_expression(condition, context)
                if isinstance(eval_result, BoolValue) and eval_result.value:
                    print(f"  ✓ 后置条件{i+1}: {self.expr_to_str(condition)}")
                else:
                    print(f"  ✗ 后置条件{i+1}失败: {self.expr_to_str(condition)}")
                    self.error_messages.append(f"后置条件{i+1}失败: {self.expr_to_str(condition)}")
                    all_passed = False
            except Exception as e:
                print(f"  ⚠ 后置条件{i+1}验证错误: {e}")
                self.error_messages.append(f"后置条件{i+1}验证错误: {e}")
                all_passed = False
        
        return all_passed
    
    def expr_to_str(self, expr: Expression) -> str:
        """表达式转换为字符串"""
        if isinstance(expr, BinaryOp):
            return f"{self.expr_to_str(expr.left)} {expr.op} {self.expr_to_str(expr.right)}"
        elif isinstance(expr, UnaryOp):
            return f"{expr.op}{self.expr_to_str(expr.operand)}"
        elif isinstance(expr, Variable):
            return expr.name
        elif isinstance(expr, Literal):
            return str(expr.value)
        elif isinstance(expr, CallExpr):
            args = ", ".join(self.expr_to_str(arg) for arg in expr.args)
            return f"{expr.func}({args})"
        return str(expr)
    
    def get_errors(self) -> List[str]:
        """获取验证错误"""
        return self.error_messages

# ==================== 模块系统 ====================
class Module:
    """模块类"""
    def __init__(self, name: str, filepath: str = ""):
        self.name = name
        self.filepath = filepath
        self.exports = {}  # 导出的符号
        self.symbols = {}  # 模块内所有符号
        self.is_loaded = False
        self.dependencies = set()  # 依赖的模块

    def add_export(self, name: str, value: Any):
        """添加导出符号"""
        self.exports[name] = value

    def add_symbol(self, name: str, value: Any):
        """添加模块符号"""
        self.symbols[name] = value

    def get_export(self, name: str) -> Any:
        """获取导出符号"""
        return self.exports.get(name)

    def get_symbol(self, name: str) -> Any:
        """获取模块符号"""
        return self.symbols.get(name)

    def get_all_exports(self) -> Dict[str, Any]:
        """获取所有导出"""
        return self.exports.copy()


class ModuleSystem:
    """模块系统管理器"""
    def __init__(self, interpreter: 'Interpreter'):
        self.interpreter = interpreter
        self.modules: Dict[str, Module] = {}  # 已加载的模块
        self.module_cache: Dict[str, Module] = {}  # 模块缓存
        self.search_paths: List[str] = ['.', './std', 'std']  # 模块搜索路径
        self.loading_modules: set = set()  # 正在加载的模块（用于检测循环导入）

    def import_module(self, module_name: str, import_path: Optional[str] = None) -> Module:
        """导入模块"""
        # 检查是否已加载
        if module_name in self.modules:
            return self.modules[module_name]

        # 检查循环导入
        if module_name in self.loading_modules:
            raise ImportError(f"检测到循环导入: {module_name}")

        # 查找模块文件
        module_file = self._find_module_file(module_name, import_path)
        if not module_file:
            raise ImportError(f"找不到模块: {module_name}")

        # 检查缓存
        if module_file in self.module_cache:
            module = self.module_cache[module_file]
            self.modules[module_name] = module
            return module

        # 加载模块
        module = self._load_module(module_name, module_file)

        # 缓存模块
        self.module_cache[module_file] = module
        self.modules[module_name] = module
        return module

    def _find_module_file(self, module_name: str, import_path: Optional[str]) -> Optional[str]:
        """查找模块文件"""
        # 如果有明确的导入路径
        if import_path:
            if os.path.exists(import_path):
                return import_path
            # 尝试添加 .intent 扩展名
            if not import_path.endswith('.intent'):
                intent_path = import_path + '.intent'
                if os.path.exists(intent_path):
                    return intent_path

        # 将点号分隔的模块名转换为路径
        module_path = module_name.replace('.', os.sep)

        # 在搜索路径中查找
        possible_names = [
            f"{module_path}.intent",
            f"{module_path}/__init__.intent",
            f"{module_name}.intent",  # 也尝试原始名称
        ]

        for search_path in self.search_paths:
            for name in possible_names:
                filepath = os.path.join(search_path, name)
                if os.path.exists(filepath):
                    return os.path.abspath(filepath)

        return None

    def _load_module(self, module_name: str, filepath: str) -> Module:
        """加载模块文件"""
        module = Module(module_name, filepath)

        # 标记为正在加载
        self.loading_modules.add(module_name)

        try:
            # 读取模块文件
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()

            # 创建模块作用域
            old_scope = self.interpreter.current_scope
            module_scope = Scope()
            self.interpreter.current_scope = module_scope

            # 保存当前模块
            old_module = getattr(self.interpreter, 'current_module', None)
            self.interpreter.current_module = module

            try:
                # 解析并执行模块代码
                lexer = Lexer(code, filepath)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()

                # 执行模块代码
                self.interpreter.execute_program(ast)

                # 收集模块中的所有符号（暂时全部导出）
                for name, value in module_scope.symbols.items():
                    module.add_symbol(name, value)
                    module.add_export(name, value)

                # 也收集函数定义
                for name, func_def in self.interpreter.functions.items():
                    if name not in ['main']:
                        module.add_export(name, func_def)

            finally:
                # 恢复作用域和模块
                self.interpreter.current_scope = old_scope
                self.interpreter.current_module = old_module

            module.is_loaded = True
            return module

        except Exception as e:
            raise ImportError(f"加载模块失败: {module_name} ({filepath}): {e}")
        finally:
            # 移除加载标记
            self.loading_modules.discard(module_name)

# ==================== 解释执行器 ====================
class Interpreter:
    """解释执行器"""
    
    def __init__(self):
        self.global_scope = Scope()
        self.contract_verifier = ContractVerifier(self)
        self.current_scope = self.global_scope
        self.functions: Dict[str, FunctionDef] = {}
        self.builtins = self._setup_builtins()
        self.return_flag = False
        self.return_value: Optional[RuntimeValue] = None
        self.break_flag = False
        self.continue_flag = False
        # 模块系统支持
        self.modules: Dict[str, 'Module'] = {}
        self.module_search_paths = ['.', './std', 'std', './lib', 'lib']
        self.current_file_dir = ""  # 当前执行文件的目录
        # 初始化模块系统
        self.module_system = ModuleSystem(self)
        # 模块导出追踪
        self.module_exports: Dict[str, Dict] = {}  # module_name -> { name: (type, value) }
        self.current_module_name: str = None
        self.current_module_exports: Dict = {}  # 当前模块的导出
    
    def add_module_search_path(self, file_dir: str):
        """添加基于文件目录的搜索路径"""
        if file_dir:
            self.current_file_dir = file_dir
            # 将文件目录加入搜索路径开头
            std_dir = os.path.join(file_dir, 'std')
            lib_dir = os.path.join(file_dir, 'lib')
            self.module_search_paths = [file_dir, std_dir, lib_dir] + self.module_search_paths
    
    def _setup_builtins(self) -> Dict[str, Callable]:
        """设置内置函数"""
        return {
            'print': self._builtin_print,
            'len': self._builtin_len,
            'range': self._builtin_range,
            'int': self._builtin_int,
            'float': self._builtin_float,
            'str': self._builtin_str,
            'bool': self._builtin_bool,
            'type': self._builtin_type,
            'abs': self._builtin_abs,
            'max': self._builtin_max,
            'min': self._builtin_min,
            'sum': self._builtin_sum,
        }
    
    def _builtin_print(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置print函数"""
        output = " ".join(str(arg) for arg in args)
        print(output)
        return IntValue(0)
    
    def _builtin_len(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置len函数"""
        if len(args) != 1:
            raise TypeError(f"len() 期望1个参数，得到 {len(args)}个")
        
        value = args[0]
        if isinstance(value, (ListValue, StringValue)):
            return IntValue(len(value.value))
        raise TypeError(f"len() 不支持类型 {value.type}")
    
    def _builtin_range(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置range函数"""
        if len(args) == 1:
            start, stop, step = 0, args[0].value, 1
        elif len(args) == 2:
            start, stop, step = args[0].value, args[1].value, 1
        elif len(args) == 3:
            start, stop, step = args[0].value, args[1].value, args[2].value
        else:
            raise TypeError(f"range() 期望1-3个参数，得到 {len(args)}个")
        
        values = [IntValue(i) for i in range(start, stop, step)]
        return ListValue(values, IntType())
    
    def _builtin_int(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置int函数"""
        if len(args) != 1:
            raise TypeError(f"int() 期望1个参数，得到 {len(args)}个")
        
        value = args[0]
        if isinstance(value, (IntValue, FloatValue)):
            return IntValue(int(value.value))
        elif isinstance(value, StringValue):
            try:
                return IntValue(int(value.value))
            except ValueError:
                raise ValueError(f"无法将字符串 '{value.value}' 转换为整数")
        raise TypeError(f"int() 不支持类型 {value.type}")
    
    def _builtin_float(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置float函数"""
        if len(args) != 1:
            raise TypeError(f"float() 期望1个参数，得到 {len(args)}个")
        
        value = args[0]
        if isinstance(value, (IntValue, FloatValue)):
            return FloatValue(float(value.value))
        elif isinstance(value, StringValue):
            try:
                return FloatValue(float(value.value))
            except ValueError:
                raise ValueError(f"无法将字符串 '{value.value}' 转换为浮点数")
        raise TypeError(f"float() 不支持类型 {value.type}")
    
    def _builtin_str(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置str函数"""
        if len(args) != 1:
            raise TypeError(f"str() 期望1个参数，得到 {len(args)}个")
        
        return StringValue(str(args[0].value))
    
    def _builtin_bool(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置bool函数"""
        if len(args) != 1:
            raise TypeError(f"bool() 期望1个参数，得到 {len(args)}个")
        
        return BoolValue(bool(args[0].value))
    
    def _builtin_type(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置type函数"""
        if len(args) != 1:
            raise TypeError(f"type() 期望1个参数，得到 {len(args)}个")
        
        return StringValue(str(args[0].type))
    
    def _builtin_abs(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置abs函数"""
        if len(args) != 1:
            raise TypeError(f"abs() 期望1个参数，得到 {len(args)}个")
        
        value = args[0]
        if isinstance(value, IntValue):
            return IntValue(abs(value.value))
        elif isinstance(value, FloatValue):
            return FloatValue(abs(value.value))
        raise TypeError(f"abs() 不支持类型 {value.type}")
    
    def _builtin_max(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置max函数"""
        if not args:
            raise TypeError(f"max() 期望至少1个参数，得到 0个")
        
        if len(args) == 1 and isinstance(args[0], ListValue):
            values = [v.value for v in args[0].value]
        else:
            values = [v.value for v in args]
        
        if all(isinstance(v, (int, float)) for v in values):
            max_val = max(values)
            return IntValue(max_val) if isinstance(max_val, int) else FloatValue(max_val)
        raise TypeError(f"max() 所有参数必须是数字")
    
    def _builtin_min(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置min函数"""
        if not args:
            raise TypeError(f"min() 期望至少1个参数，得到 0个")
        
        if len(args) == 1 and isinstance(args[0], ListValue):
            values = [v.value for v in args[0].value]
        else:
            values = [v.value for v in args]
        
        if all(isinstance(v, (int, float)) for v in values):
            min_val = min(values)
            return IntValue(min_val) if isinstance(min_val, int) else FloatValue(min_val)
        raise TypeError(f"min() 所有参数必须是数字")
    
    def _builtin_sum(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置sum函数"""
        if len(args) != 1:
            raise TypeError(f"sum() 期望1个参数，得到 {len(args)}个")
        
        if not isinstance(args[0], ListValue):
            raise TypeError(f"sum() 期望列表参数")
        
        values = args[0].value
        if not values:
            return IntValue(0)
        
        if all(isinstance(v, IntValue) for v in values):
            total = sum(v.value for v in values)
            return IntValue(total)
        elif all(isinstance(v, (IntValue, FloatValue)) for v in values):
            total = sum(v.value for v in values)
            return FloatValue(total)
        raise TypeError(f"sum() 列表元素必须是数字")
    
    def execute_program(self, program: Program, module_mode: bool = False, module_name: str = None) -> RuntimeValue:
        """执行整个程序
        module_mode=True 时只注册函数/变量，不执行main（用于模块加载）
        """
        # 模块追踪初始化
        in_module_mode = False
        
        if module_mode and module_name:
            in_module_mode = True
            # 保存当前的导出表
            if not hasattr(self, '_saved_module_exports'):
                self._saved_module_exports = getattr(self, 'module_exports', {})
            if not hasattr(self, '_saved_current_exports'):
                self._saved_current_exports = getattr(self, 'current_module_exports', {})
            self.module_exports = {}
            self.current_module_name = module_name
            self.module_exports[module_name] = {}
            self.current_module_exports = {}
        
        try:
            # 注册所有函数
            for func in program.functions.values():
                self.functions[func.name] = func
                # 模块模式下同时写入当前作用域，供导入方使用
                if module_mode:
                    self.current_scope.declare(func.name, func, False, allow_redefine=True)
            
            # 执行全局语句（变量声明等）
            result = IntValue(0)
            for stmt in program.statements:
                # 跳过 ExportStmt，它们会在最后统一处理
                if isinstance(stmt, ExportStmt):
                    continue
                result = self.execute_statement(stmt)
                if self.return_flag:
                    break
            
            # 处理 export 语句（在所有函数和变量都注册之后）
            for stmt in program.statements:
                if isinstance(stmt, ExportStmt):
                    self.execute_export(stmt)
            
            # 模块模式下不执行main
            if module_mode:
                # 保存导出信息到模块缓存
                if module_name:
                    self._module_cache = getattr(self, '_module_cache', {})
                    self._module_cache[module_name] = {
                        'exports': dict(self.module_exports.get(module_name, {})),
                        'functions': {k: v for k, v in self.functions.items() if k in self.module_exports.get(module_name, {})}
                    }
                return result
            
            # 查找并执行main函数
            if 'main' in self.functions:
                print("🚀 执行main函数:")
                result = self.execute_function(self.functions['main'], [])
            
            return result
        finally:
            # 恢复模块追踪状态（只有在进入时才恢复）
            if in_module_mode:
                if hasattr(self, '_saved_module_exports'):
                    self.module_exports = self._saved_module_exports
                    delattr(self, '_saved_module_exports')
                if hasattr(self, '_saved_current_exports'):
                    self.current_module_exports = self._saved_current_exports
                    delattr(self, '_saved_current_exports')
    
    def execute_statement(self, stmt: ASTNode) -> RuntimeValue:
        """执行语句"""
        if isinstance(stmt, VariableDecl):
            return self.execute_variable_decl(stmt)
        elif isinstance(stmt, Assignment):
            return self.execute_assignment(stmt)
        elif isinstance(stmt, ReturnStmt):
            return self.execute_return(stmt)
        elif isinstance(stmt, PrintStmt):
            return self.execute_print(stmt)
        elif isinstance(stmt, IfStmt):
            return self.execute_if(stmt)
        elif isinstance(stmt, WhileStmt):
            return self.execute_while(stmt)
        elif isinstance(stmt, ForStmt):
            return self.execute_for(stmt)
        elif isinstance(stmt, BreakStmt):
            return self.execute_break()
        elif isinstance(stmt, ContinueStmt):
            return self.execute_continue()
        elif isinstance(stmt, ImportStmt):
            return self.execute_import(stmt)
        elif isinstance(stmt, ExportStmt):
            return self.execute_export(stmt)
        elif isinstance(stmt, Expression):
            return self.evaluate_expression(stmt)
        else:
            raise RuntimeError(f"未知语句类型: {type(stmt).__name__}")
    
    def execute_variable_decl(self, stmt: VariableDecl) -> RuntimeValue:
        """执行变量声明"""
        value = self.evaluate_expression(stmt.value) if stmt.value else self.get_default_value(stmt.var_type)
        self.current_scope.declare(stmt.name, value, stmt.is_const)
        return value
    
    def get_default_value(self, type_name: Optional[str]) -> RuntimeValue:
        """获取默认值"""
        if type_name == "Int":
            return IntValue(0)
        elif type_name == "Float":
            return FloatValue(0.0)
        elif type_name == "String":
            return StringValue("")
        elif type_name == "Bool":
            return BoolValue(False)
        elif type_name and type_name.startswith("List"):
            return ListValue([], IntType())
        return IntValue(0)
    
    def execute_assignment(self, stmt: Assignment) -> RuntimeValue:
        """执行赋值语句"""
        value = self.evaluate_expression(stmt.value)
        
        if stmt.op == "=":
            self.current_scope.assign(stmt.target, value)
        else:
            # 复合赋值
            old_value = self.current_scope.get(stmt.target)
            if stmt.op == "+=":
                new_value = self._binary_op(old_value, "+", value)
            elif stmt.op == "-=":
                new_value = self._binary_op(old_value, "-", value)
            elif stmt.op == "*=":
                new_value = self._binary_op(old_value, "*", value)
            elif stmt.op == "/=":
                new_value = self._binary_op(old_value, "/", value)
            elif stmt.op == "%=":
                new_value = self._binary_op(old_value, "%", value)
            elif stmt.op == "**=":
                new_value = self._binary_op(old_value, "**", value)
            elif stmt.op == "//=":
                new_value = self._binary_op(old_value, "//", value)
            else:
                raise RuntimeError(f"不支持的赋值操作符: {stmt.op}")
            
            self.current_scope.assign(stmt.target, new_value)
        
        return value
    
    def execute_return(self, stmt: ReturnStmt) -> RuntimeValue:
        """执行返回语句"""
        value = self.evaluate_expression(stmt.value) if stmt.value else IntValue(0)
        self.return_flag = True
        self.return_value = value
        return value
    
    def execute_print(self, stmt: PrintStmt) -> RuntimeValue:
        """执行打印语句"""
        values = [self.evaluate_expression(arg) for arg in stmt.args]
        return self._builtin_print(values)
    
    def execute_if(self, stmt: IfStmt) -> RuntimeValue:
        """执行条件语句"""
        # 评估条件
        condition = self.evaluate_expression(stmt.condition)
        
        if condition.to_bool():
            # 进入then分支作用域
            old_scope = self.current_scope
            self.current_scope = self.current_scope.enter()
            
            result = IntValue(0)
            for branch_stmt in stmt.then_branch:
                result = self.execute_statement(branch_stmt)
                if self.return_flag or self.break_flag or self.continue_flag:
                    break
            
            self.current_scope = old_scope
            return result
        
        # 检查elif分支
        for elif_cond, elif_body in stmt.elif_branches:
            elif_cond_val = self.evaluate_expression(elif_cond)
            if elif_cond_val.to_bool():
                old_scope = self.current_scope
                self.current_scope = self.current_scope.enter()
                
                result = IntValue(0)
                for branch_stmt in elif_body:
                    result = self.execute_statement(branch_stmt)
                    if self.return_flag or self.break_flag or self.continue_flag:
                        break
                
                self.current_scope = old_scope
                return result
        
        # 执行else分支
        if stmt.else_branch:
            old_scope = self.current_scope
            self.current_scope = self.current_scope.enter()
            
            result = IntValue(0)
            for branch_stmt in stmt.else_branch:
                result = self.execute_statement(branch_stmt)
                if self.return_flag or self.break_flag or self.continue_flag:
                    break
            
            self.current_scope = old_scope
            return result
        
        return IntValue(0)
    
    def execute_while(self, stmt: WhileStmt) -> RuntimeValue:
        """执行while循环"""
        result = IntValue(0)
        
        while True:
            # 评估条件
            condition = self.evaluate_expression(stmt.condition)
            if not condition.to_bool():
                break
            
            # 进入循环体作用域
            old_scope = self.current_scope
            self.current_scope = self.current_scope.enter()
            
            # 执行循环体
            for body_stmt in stmt.body:
                result = self.execute_statement(body_stmt)
                if self.return_flag:
                    self.current_scope = old_scope
                    return result
                elif self.break_flag:
                    self.break_flag = False
                    self.current_scope = old_scope
                    break
                elif self.continue_flag:
                    self.continue_flag = False
                    break
            
            self.current_scope = old_scope
            
            if self.break_flag:
                break
        
        return result
    
    def execute_for(self, stmt: ForStmt) -> RuntimeValue:
        """执行for循环"""
        result = IntValue(0)
        
        # 获取可迭代对象
        iterable = self.evaluate_expression(stmt.iterable)
        
        if not isinstance(iterable, ListValue):
            raise TypeError(f"for循环期望列表，得到 {iterable.type}")
        
        for item in iterable.value:
            # 进入循环体作用域
            old_scope = self.current_scope
            self.current_scope = self.current_scope.enter()
            
            # 设置循环变量
            self.current_scope.declare(stmt.var, item.copy(), False)
            
            # 执行循环体
            for body_stmt in stmt.body:
                result = self.execute_statement(body_stmt)
                if self.return_flag:
                    self.current_scope = old_scope
                    return result
                elif self.break_flag:
                    self.break_flag = False
                    break
                elif self.continue_flag:
                    self.continue_flag = False
                    break
            
            self.current_scope = old_scope
            
            if self.break_flag:
                break
        
        return result
    
    def execute_break(self) -> RuntimeValue:
        """执行break语句"""
        self.break_flag = True
        return IntValue(0)
    
    def execute_continue(self) -> RuntimeValue:
        """执行continue语句"""
        self.continue_flag = True
        return IntValue(0)
    
    def execute_import(self, stmt: ImportStmt) -> RuntimeValue:
        """执行import语句"""
        module_name = stmt.module_name
        alias = stmt.alias if stmt.alias else module_name
        
        # 检查模块是否已加载（缓存）
        if module_name in self.modules:
            module_scope = self.modules[module_name]
        else:
            # 查找模块文件（支持点号分隔，如 std.math → std/math.intent）
            module_file = self._find_module_file(module_name)
            if not module_file:
                print(f"[警告] 找不到模块: {module_name}")
                return IntValue(0)
            
            # 加载模块（module_mode=True，不执行main）
            try:
                with open(module_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # 保存当前状态
                old_scope = self.current_scope
                old_functions = dict(self.functions)
                
                # 创建模块作用域
                module_scope = Scope(parent=self.global_scope)
                self.current_scope = module_scope
                
                # 解析并执行模块代码（module_mode=True）
                lexer = Lexer(code, module_file)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                self.execute_program(ast, module_mode=True, module_name=module_name)
                
                # 把模块内注册的函数也存入模块作用域
                for fname, fdef in self.functions.items():
                    if fname not in old_functions:
                        module_scope.declare(fname, fdef, False, allow_redefine=True)
                
                # 把导出信息也存入模块作用域
                if module_name in getattr(self, 'module_exports', {}):
                    for name, (exp_type, value) in self.module_exports[module_name].items():
                        if exp_type == 'function':
                            module_scope.declare(name, value, False, allow_redefine=True)
                
                # 也从 _module_cache 获取导出信息
                module_cache = getattr(self, '_module_cache', {})
                if module_name in module_cache:
                    for name, func in module_cache[module_name].get('functions', {}).items():
                        module_scope.declare(name, func, False, allow_redefine=True)
                        self.functions[name] = func
                
                # 恢复状态
                self.current_scope = old_scope
                self.functions = old_functions
                
                # 缓存模块
                self.modules[module_name] = module_scope
                
            except Exception as e:
                if 'old_scope' in dir():
                    self.current_scope = old_scope
                if 'old_functions' in dir():
                    self.functions = old_functions
                print(f"[警告] 加载模块失败: {module_name}, {e}")
                return IntValue(0)
        
        # 将模块中的所有符号导入当前作用域（以 alias.name 形式）
        module_scope = self.modules[module_name]
        for name, value in module_scope.symbols.items():
            # 以 alias.name 形式注册（如 std.add）
            qualified_name = f"{alias}.{name}"
            # 只在作用域中注册一次（qualified name）
            if not self.current_scope.has(qualified_name):
                self.current_scope.declare(qualified_name, value, False)
            # 如果是函数定义，注册到 self.functions
            if hasattr(value, 'body'):  # FunctionDef 有 body 属性
                self.functions[qualified_name] = value
        
        # 创建一个带module_ref的模块值，用于属性访问（如 std.add()）
        module_value = RuntimeValue(StringType(), alias)
        module_value.module_ref = module_scope  # 保存模块引用
        # 也以模块名注册
        if not self.current_scope.has(alias):
            self.current_scope.declare(alias, module_value, False)
        
        return IntValue(0)
    
    def execute_export(self, stmt: ExportStmt) -> RuntimeValue:
        """执行export语句"""
        print(f"[DEBUG execute_export] current_module_name={getattr(self, 'current_module_name', 'N/A')}")
        print(f"[DEBUG execute_export] functions keys={list(self.functions.keys())}")
        
        if not hasattr(self, 'current_module_name') or not self.current_module_name:
            # 非模块模式下，export 不做任何事
            return IntValue(0)
        
        if stmt.is_default:
            # 默认导出 export default xxx
            if 'default' in self.current_module_exports:
                self.module_exports[self.current_module_name]['default'] = self.current_module_exports['default']
            else:
                print(f"[警告] 默认导出没有值")
        else:
            # 普通导出 export { xxx, yyy }
            for name in stmt.exports:
                # 先从函数表中获取（export def 会注册到这里）
                if name in self.functions:
                    func = self.functions[name]
                    self.module_exports[self.current_module_name][name] = ('function', func)
                    # 同时注册到当前作用域（用于模块内访问）
                    self.current_scope.declare(name, func, False, allow_redefine=True)
                elif name in self.current_scope.symbols:
                    value = self.current_scope.symbols[name]
                    self.module_exports[self.current_module_name][name] = ('name', value)
                else:
                    print(f"[警告] 导出 '{name}' 不存在")
        
        return IntValue(0)
    
    def _find_module_file(self, module_name: str) -> Optional[str]:
        """查找模块文件，支持点号分隔（如 std.math → std/math.intent）"""
        # 将点号转为路径分隔符
        path_parts = module_name.replace('.', os.sep)
        
        search_paths = []
        if self.current_file_dir:
            search_paths.append(self.current_file_dir)
        search_paths.extend(self.module_search_paths)
        search_paths.append(os.getcwd())
        
        # 去重
        seen = set()
        unique_paths = []
        for p in search_paths:
            np = os.path.normpath(p)
            if np not in seen:
                seen.add(np)
                unique_paths.append(np)
        
        for base in unique_paths:
            # 尝试 base/std/math.intent
            candidate = os.path.join(base, path_parts + '.intent')
            if os.path.exists(candidate):
                return candidate
            # 尝试 base/std/math/__init__.intent
            candidate_init = os.path.join(base, path_parts, '__init__.intent')
            if os.path.exists(candidate_init):
                return candidate_init
        
        return None
    
    def execute_function(self, func: FunctionDef, args: List[RuntimeValue]) -> RuntimeValue:
        """执行函数"""
        print(f"📋 执行函数: {func.name}")
        
        # 准备验证上下文
        context = {
            'args': args,
            'variables': {name: val for name, val in self.current_scope.symbols.items()}
        }
        
        # 验证前置条件
        if func.requires:
            print("⚖️  验证前置条件...")
            if not self.contract_verifier.verify_requires(func.requires, context):
                print("❌ 前置条件验证失败，停止执行")
                return IntValue(1)
        
        # 保存旧的变量状态
        old_scope = self.current_scope
        self.current_scope = self.current_scope.enter()
        
        # 设置参数
        for (param_name, param_type), arg_value in zip(func.params, args):
            self.current_scope.declare(param_name, arg_value.copy(), False)
        
        # 执行函数体
        result = IntValue(0)
        for stmt in func.body:
            result = self.execute_statement(stmt)
            if self.return_flag:
                self.return_flag = False
                break
        
        # 验证后置条件
        if func.ensures:
            print("⚖️  验证后置条件...")
            context['result'] = result
            context['variables'] = {name: val for name, val in self.current_scope.symbols.items()}
            
            if not self.contract_verifier.verify_ensures(func.ensures, result, context):
                print("⚠️  后置条件验证失败")
        
        # 恢复作用域
        self.current_scope = old_scope
        
        return result
    
    def evaluate_expression(self, expr: Expression, context: Optional[Dict] = None) -> RuntimeValue:
        """评估表达式"""
        if context is None:
            context = {}
        
        if isinstance(expr, Literal):
            if expr.literal_type == 'int':
                return IntValue(expr.value)
            elif expr.literal_type == 'float':
                return FloatValue(expr.value)
            elif expr.literal_type == 'string':
                return StringValue(expr.value)
            elif expr.literal_type == 'bool':
                return BoolValue(expr.value)
            elif expr.literal_type == 'none':
                return RuntimeValue(IntType(), 0)  # None的表示
            else:
                return RuntimeValue(IntType(), expr.value)
        
        elif isinstance(expr, Variable):
            # 检查是否是内置函数
            if expr.name in self.builtins:
                # 返回一个特殊的函数值
                return RuntimeValue(IntType(), expr.name)  # 简化处理
            
            # 从作用域获取变量
            return self.current_scope.get(expr.name)
        
        elif isinstance(expr, MemberAccess):
            # 计算左侧对象的值
            obj_value = self.evaluate_expression(expr.obj, context)
            
            # 如果obj_value是模块引用，获取模块导出
            if hasattr(obj_value, 'module_ref'):
                module = obj_value.module_ref
                # 检查是否是Module对象
                if hasattr(module, 'get_export'):
                    member_val = module.get_export(expr.member)
                    if member_val is not None:
                        return member_val
                    raise NameError(f"模块 '{obj_value.value}' 没有导出成员 '{expr.member}'")
                elif hasattr(module, 'symbols'):
                    # 是Scope对象，从symbols中获取
                    if expr.member in module.symbols:
                        return module.symbols[expr.member]
                    raise NameError(f"模块 '{obj_value.value}' 没有导出成员 '{expr.member}'")
            
            # 如果是普通对象，尝试作为属性访问
            # 对于简单的实现，我们直接在作用域中查找 module.member
            full_name = f"{obj_value.value}.{expr.member}" if hasattr(obj_value, 'value') else f"{obj_value}.{expr.member}"
            result = self.current_scope.get(full_name)
            if result is not None:
                return result
            
            # 尝试在模块中查找
            if hasattr(obj_value, 'value'):
                module_name = obj_value.value
                if hasattr(self, 'module_system') and module_name in self.module_system.modules:
                    module = self.module_system.modules[module_name]
                    if hasattr(module, 'get_export'):
                        member_val = module.get_export(expr.member)
                        if member_val is not None:
                            return member_val
                    elif hasattr(module, 'symbols'):
                        if expr.member in module.symbols:
                            return module.symbols[expr.member]
            
            raise NameError(f"无法访问成员 '{expr.member}'")
        
        elif isinstance(expr, BinaryOp):
            left = self.evaluate_expression(expr.left, context)
            right = self.evaluate_expression(expr.right, context)
            return self._binary_op(left, expr.op, right)
        
        elif isinstance(expr, UnaryOp):
            operand = self.evaluate_expression(expr.operand, context)
            return self._unary_op(expr.op, operand)
        
        elif isinstance(expr, CallExpr):
            # 处理MemberAccess作为函数的情况 (如 std.math.add(x, y))
            if isinstance(expr.func, MemberAccess):
                # 获取模块名和函数名
                func_obj = expr.func.obj
                func_member = expr.func.member
                
                # 获取模块名
                if isinstance(func_obj, Variable):
                    module_name = func_obj.name
                elif isinstance(func_obj, MemberAccess):
                    # 处理嵌套成员访问
                    if isinstance(func_obj.obj, Variable):
                        module_name = f"{func_obj.obj.name}.{func_obj.member}"
                    else:
                        module_name = str(func_obj)
                else:
                    module_name = str(func_obj.value) if hasattr(func_obj, 'value') else str(func_obj)
                
                full_func_name = f"{module_name}.{func_member}"
                
                # 先检查functions字典中是否有这个函数
                if full_func_name in self.functions:
                    func = self.functions[full_func_name]
                    args = [self.evaluate_expression(arg, context) for arg in expr.args]
                    return self.execute_function(func, args)
                
                # 尝试在模块作用域中查找
                if hasattr(self, 'module_system') and module_name in self.module_system.modules:
                    module = self.module_system.modules[module_name]
                    # 从symbols中查找
                    if hasattr(module, 'symbols') and func_member in module.symbols:
                        func = module.symbols[func_member]
                        args = [self.evaluate_expression(arg, context) for arg in expr.args]
                        return self.execute_function(func, args)
                
                raise NameError(f"未定义的函数: {full_func_name}")
            
            # 检查是否是内置函数
            if expr.func in self.builtins:
                args = [self.evaluate_expression(arg, context) for arg in expr.args]
                return self.builtins[expr.func](args)
            
            # 检查是否是用户定义函数
            if expr.func in self.functions:
                func = self.functions[expr.func]
                args = [self.evaluate_expression(arg, context) for arg in expr.args]
                return self.execute_function(func, args)
            
            raise NameError(f"未定义的函数: {expr.func}")
        
        elif isinstance(expr, ListExpr):
            elements = [self.evaluate_expression(elem, context) for elem in expr.elements]
            if not elements:
                return ListValue([], IntType())
            
            # 确定元素类型
            element_type = elements[0].type
            for elem in elements[1:]:
                if not element_type.can_assign_from(elem.type):
                    raise TypeError(f"列表元素类型不一致: {element_type} 和 {elem.type}")
            
            return ListValue(elements, element_type)
        
        else:
            raise RuntimeError(f"不支持的表达式类型: {type(expr).__name__}")
    
    def _binary_op(self, left: RuntimeValue, op: str, right: RuntimeValue) -> RuntimeValue:
        """执行二元运算"""
        # 算术运算
        if op in ('+', '-', '*', '/', '//', '%', '**'):
            if isinstance(left, (IntValue, FloatValue)) and isinstance(right, (IntValue, FloatValue)):
                left_val = left.value
                right_val = right.value
                
                if op == '+':
                    result = left_val + right_val
                elif op == '-':
                    result = left_val - right_val
                elif op == '*':
                    result = left_val * right_val
                elif op == '/':
                    if right_val == 0:
                        raise ZeroDivisionError("除数不能为零")
                    result = left_val / right_val
                elif op == '//':
                    if right_val == 0:
                        raise ZeroDivisionError("除数不能为零")
                    result = left_val // right_val
                elif op == '%':
                    if right_val == 0:
                        raise ZeroDivisionError("除数不能为零")
                    result = left_val % right_val
                elif op == '**':
                    result = left_val ** right_val
                
                # 确定结果类型
                if isinstance(left, IntValue) and isinstance(right, IntValue) and op in ('+', '-', '*', '//', '%', '**'):
                    if op == '/' or (op == '//' and left_val % right_val != 0):
                        return FloatValue(float(result))
                    return IntValue(int(result))
                else:
                    return FloatValue(float(result))
        
        # 比较运算
        elif op in ('==', '!=', '<', '>', '<=', '>='):
            if isinstance(left, (IntValue, FloatValue)) and isinstance(right, (IntValue, FloatValue)):
                left_val = left.value
                right_val = right.value
                
                if op == '==':
                    result = left_val == right_val
                elif op == '!=':
                    result = left_val != right_val
                elif op == '<':
                    result = left_val < right_val
                elif op == '>':
                    result = left_val > right_val
                elif op == '<=':
                    result = left_val <= right_val
                elif op == '>=':
                    result = left_val >= right_val
                
                return BoolValue(bool(result))
        
        # 逻辑运算
        elif op == 'and':
            return BoolValue(left.to_bool() and right.to_bool())
        elif op == 'or':
            return BoolValue(left.to_bool() or right.to_bool())
        
        # 字符串连接
        elif op == '+' and isinstance(left, StringValue) and isinstance(right, StringValue):
            return StringValue(left.value + right.value)
        
        raise TypeError(f"不支持的操作: {left.type} {op} {right.type}")
    
    def _unary_op(self, op: str, operand: RuntimeValue) -> RuntimeValue:
        """执行一元运算"""
        if op == '-':
            if isinstance(operand, (IntValue, FloatValue)):
                if isinstance(operand, IntValue):
                    return IntValue(-operand.value)
                else:
                    return FloatValue(-operand.value)
        elif op == '+':
            if isinstance(operand, (IntValue, FloatValue)):
                return operand
        elif op == '!':
            return BoolValue(not operand.to_bool())
        
        raise TypeError(f"不支持的一元操作: {op} {operand.type}")

# ==================== REPL交互式环境 ====================
class IntentREPL:
    """Intent语言交互式REPL"""
    
    def __init__(self, interpreter: Interpreter, translator: PhilosophyTranslator):
        self.interpreter = interpreter
        self.translator = translator
        self.show_philosophy = False
        self.history = []
        
    def print_welcome(self):
        """打印欢迎信息"""
        print(f"""
╔═══════════════════════════════════════════════════════╗
║              Intent REPL v{VERSION}                    ║
║         {PHILOSOPHY_SLOGAN}                ║
║  输入代码执行，.help查看命令，.exit退出               ║
╚═══════════════════════════════════════════════════════╝
        """)
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
📋 REPL命令:
  .help          显示此帮助信息
  .exit/.quit    退出REPL
  .clear         清除所有变量和函数
  .vars          显示当前所有变量
  .funcs         显示当前所有函数
  .history       显示历史命令
  .mode          切换哲学/普通模式
  .demo          运行演示程序
  .run <文件>    运行.intent文件
  
📝 示例代码:
  let x = 10
  let y = 20
  x + y
  
  def add(a: Int, b: Int) -> Int { return a + b; }
  add(5, 3)
  
  print("Hello, Intent!")
        """
        print(help_text)
    
    def show_variables(self):
        """显示所有变量"""
        scope = self.interpreter.current_scope
        vars_info = []
        
        # 收集当前作用域及所有父作用域的变量
        while scope:
            for name, value in scope.symbols.items():
                vars_info.append((name, value))
            scope = scope.parent
        
        if not vars_info:
            print("没有定义变量")
            return
        
        print("📊 当前变量:")
        for name, value in vars_info:
            print(f"  {name} = {value} ({value.type})")
    
    def show_functions(self):
        """显示所有函数"""
        if not self.interpreter.functions:
            print("没有定义函数")
            return
        
        print("📋 当前函数:")
        for name, func in self.interpreter.functions.items():
            params = ", ".join([f"{p[0]}: {p[1]}" for p in func.params])
            return_type = f" -> {func.return_type}" if func.return_type else ""
            print(f"  {name}({params}){return_type}")
    
    def show_history(self):
        """显示历史记录"""
        if not self.history:
            print("没有历史记录")
            return
        
        print("📜 历史记录:")
        for i, cmd in enumerate(self.history[-10:], 1):  # 只显示最近10条
            print(f"  {i:2d}. {cmd}")
    
    def run_demo(self):
        """运行演示程序"""
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
        
        print("🎬 运行演示程序:")
        print("-" * 40)
        
        if self.show_philosophy:
            print("🧘 哲学视角:")
            print(self.translator.translate_code(demo_code, "display"))
            print("-" * 40)
        
        self.run_code(demo_code)
        print("-" * 40)
    
    def run_file(self, filename: str):
        """运行.intent文件"""
        if not os.path.exists(filename):
            print(f"错误: 文件不存在 {filename}")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
            
            print(f"📁 运行文件: {filename}")
            print("-" * 40)
            
            if self.show_philosophy:
                print("🧘 哲学视角:")
                print(self.translator.translate_code(code, "display"))
                print("-" * 40)
            
            self.run_code(code)
            print("-" * 40)
        except Exception as e:
            print(f"错误: {e}")
    
    def run_code(self, code: str):
        """运行Intent代码"""
        try:
            # 词法分析
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            # 语法分析
            parser = Parser(tokens)
            ast = parser.parse()
            
            # 解释执行
            result = self.interpreter.execute_program(ast)
            
            print(f"✅ 程序执行成功")
            if result is not None and not isinstance(result.value, int) or result.value != 0:
                print(f"返回值: {result}")
            
        except SyntaxError as e:
            print(f"❌ 语法错误: {e}")
        except RuntimeError as e:
            print(f"❌ 运行时错误: {e}")
        except Exception as e:
            print(f"❌ 未知错误: {type(e).__name__}: {e}")
    
    def evaluate_line(self, line: str) -> Any:
        """评估单行代码"""
        # 如果是命令，处理命令
        if line.startswith('.'):
            return self.handle_command(line)
        
        # 添加到历史
        self.history.append(line)
        
        # 尝试作为表达式求值
        try:
            # 如果是表达式，自动包装在print中
            if not any(line.strip().startswith(keyword) for keyword in 
                      ['def ', 'let ', 'var ', 'const ', 'if ', 'for ', 'while ']):
                # 可能是表达式，尝试求值
                expr_code = f"print({line});"
                self.run_code(expr_code)
                return
        
        except:
            pass
        
        # 作为普通代码执行
        if not line.endswith(';') and not line.endswith('}'):
            line += ';'
        
        self.run_code(line)
    
    def handle_command(self, command: str) -> bool:
        """处理REPL命令，返回True表示继续，False表示退出"""
        cmd = command.strip().split()
        
        if not cmd:
            return True
        
        if cmd[0] == '.exit' or cmd[0] == '.quit':
            print("再见！🧘")
            return False
        
        elif cmd[0] == '.help':
            self.show_help()
        
        elif cmd[0] == '.clear':
            self.interpreter = Interpreter()
            self.interpreter.current_scope = self.interpreter.global_scope
            print("🧹 已清除所有变量和函数")
        
        elif cmd[0] == '.vars':
            self.show_variables()
        
        elif cmd[0] == '.funcs':
            self.show_functions()
        
        elif cmd[0] == '.history':
            self.show_history()
        
        elif cmd[0] == '.mode':
            self.show_philosophy = not self.show_philosophy
            mode = "哲学视角" if self.show_philosophy else "普通模式"
            print(f"🔄 切换为: {mode}")
        
        elif cmd[0] == '.demo':
            self.run_demo()
        
        elif cmd[0] == '.run' and len(cmd) > 1:
            self.run_file(cmd[1])
        
        else:
            print(f"未知命令: {cmd[0]}")
            print("输入 .help 查看可用命令")
        
        return True
    
    def run(self):
        """运行REPL主循环"""
        self.print_welcome()
        
        while True:
            try:
                # 读取输入
                try:
                    line = input(">>> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()  # 换行
                    print("输入 .exit 退出")
                    continue
                
                # 跳过空行
                if not line:
                    continue
                
                # 处理命令或代码
                if not self.handle_command(line) if line.startswith('.') else True:
                    self.evaluate_line(line)
                    
            except SystemExit:
                break
            except Exception as e:
                print(f"错误: {e}")

# ==================== 主程序 ====================
def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description=f'Intent语言解释器 v{VERSION} - {PHILOSOPHY_SLOGAN}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
使用示例:
  python mini_intent.py hello.intent           # 普通执行
  python mini_intent.py hello.intent -p       # 显示哲学视角
  python mini_intent.py -d                    # 运行演示程序
  python mini_intent.py -r                    # 启动REPL
  
哲学映射文件:
  默认位置: philosophy/mapping.json
  可以自定义: python mini_intent.py file.intent -m my_map.json
        '''
    )
    
    parser.add_argument('filename', nargs='?', help='Intent源文件')
    parser.add_argument('-p', '--philosophy', action='store_true', help='显示哲学视角')
    parser.add_argument('-m', '--mapping', default='philosophy/mapping.json', help='哲学映射文件路径')
    parser.add_argument('-d', '--demo', action='store_true', help='运行演示程序')
    parser.add_argument('-r', '--repl', action='store_true', help='启动REPL交互环境')
    parser.add_argument('-t', '--tokens', action='store_true', help='显示词法分析结果')
    parser.add_argument('-a', '--ast', action='store_true', help='显示语法分析结果')
    
    args = parser.parse_args()
    
    # 创建翻译器
    translator = PhilosophyTranslator(args.mapping)
    
    # 创建解释器
    interpreter = Interpreter()
    
    # 启动REPL
    if args.repl:
        repl = IntentREPL(interpreter, translator)
        if args.philosophy:
            repl.show_philosophy = True
        repl.run()
        return
    
    # 演示程序
    if args.demo:
        demo_code = '''def main() {
    print("=== Intent语言演示 ===");
    print("心学为体，禅道为翼，马哲为用");
    
    // 变量声明
    let x = 10;
    let y = 20;
    
    // 计算
    let sum = x + y;
    let product = x * y;
    
    // 输出结果
    print("x =", x);
    print("y =", y);
    print("x + y =", sum);
    print("x * y =", product);
    
    // 条件判断
    if (x > 5) {
        print("x 大于 5");
    } else {
        print("x 不大于 5");
    }
    
    // 循环
    let i = 1;
    while (i <= 3) {
        print("循环计数:", i);
        i = i + 1;
    }
    
    return 0;
}'''
        
        if args.philosophy:
            print("🧘 哲学视角代码:")
            print("=" * 60)
            print(translator.translate_code(demo_code, "display"))
            print("=" * 60)
            print("\n⚙️  执行结果:")
            print("-" * 40)
        
        run_code(demo_code, interpreter, args)
        return
    
    # 检查文件参数
    if not args.filename and not args.repl and not args.demo:
        parser.print_help()
        return
    
    # 读取文件
    try:
        with open(args.filename, 'r', encoding='utf-8') as f:
            code = f.read()
        # 设置当前文件目录，用于模块搜索
        file_dir = os.path.dirname(os.path.abspath(args.filename))
        interpreter.add_module_search_path(file_dir)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.filename}")
        print("提示: 请确保文件存在，或使用 --demo 运行演示程序")
        return
    
    # 显示哲学视角
    if args.philosophy:
        print("🧘 哲学视角代码:")
        print("=" * 60)
        print(translator.translate_code(code, "display"))
        print("=" * 60)
        print("\n⚙️  执行结果:")
        print("-" * 40)
    
    # 运行代码
    run_code(code, interpreter, args)

def run_code(code: str, interpreter: Interpreter, args):
    """运行Intent代码"""
    try:
        # 1. 词法分析
        if args.tokens:
            print("🔤 词法分析...")
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            print("\n词法分析结果:")
            for i, token in enumerate(tokens[:50]):  # 限制显示前50个token
                print(f"  {i:3d}: {token}")
            if len(tokens) > 50:
                print(f"  ... 还有 {len(tokens)-50} 个token")
            print()
        
        # 2. 语法分析
        if args.ast:
            print("📐 语法分析...")
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            print("\n语法分析结果:")
            for func in ast.functions.values():
                print(f"  函数: {func.name}")
                if func.params:
                    params = ", ".join([f"{p[0]}: {p[1]}" for p in func.params])
                    print(f"    参数: {params}")
                if func.return_type:
                    print(f"    返回类型: {func.return_type}")
                if func.requires:
                    print(f"    前置条件: {func.requires}")
                if func.ensures:
                    print(f"    后置条件: {func.ensures}")
                print(f"    语句数: {len(func.body)}")
            print()
        
        # 3. 解释执行
        print("⚡ 解释执行...\n")
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        result = interpreter.execute_program(ast)
        
        print(f"\n✅ 程序执行成功")
        if result is not None and not (isinstance(result.value, int) and result.value == 0):
            print(f"返回值: {result}")
        
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
    except RuntimeError as e:
        print(f"❌ 运行时错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

# ==================== 程序入口 ====================
if __name__ == '__main__':
    print(f"""
╔═══════════════════════════════════════════════════════╗
║              Intent 语言解释器 v{VERSION}              ║
║         {PHILOSOPHY_SLOGAN}                ║
╚═══════════════════════════════════════════════════════╝
    """)
    main()