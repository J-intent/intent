#!/usr/bin/env python3
"""
Intent语言完整解释器 v1.2
融合:心学为体,禅道为翼,马哲为用
目标:让代码清晰地表达意图
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
    # 尝试导入 readline(Unix/Linux/macOS)
    import readline
except ImportError:
    # Windows 系统,尝试 pyreadline3
    try:
        import pyreadline3 as readline
    except ImportError:
        # 如果都没有,创建一个虚拟的 readline
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
PHILOSOPHY_SLOGAN = "心学为体,禅道为翼,马哲为用"

# ==================== 哲学翻译器 ====================
class PhilosophyTranslator:
    """哲学翻译器:连接代码与东方智慧"""

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
            "def": "心学为体:函数如功夫,需明确意图与契约",
            "requires": "事上练:实践前需条件具备,如心学之'在事上磨炼'",
            "ensures": "持志:实践后需坚守结果,如心学之'持志如心痛'",
            "pure": "禅道为翼:纯函数如'无住生心',不执外相",
            "let": "格物:探究事物之理,明确变量本质",
            "return": "归元:回归本源,函数终有归宿",
            "if": "辩证:条件判断,如马哲之具体问题具体分析"
        }

    def translate_code(self, code: str, mode: str = "display") -> str:
        """翻译代码为哲学视角

        Args:
            code: 原始代码
            mode: 'display'显示哲学术语,'explain'显示哲学解释
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
        'invariant', 'pure', 'effect', 'import', 'from', 'as',
        'None', 'True', 'False', 'true', 'false', 'null',
        'and', 'or', 'not', 'in', 'is',
        'class', 'this', 'mut', 'fn'  # 类系统 + 匿名函数
    }

    # 内置类型名 - 不是关键字,只是预定义的类型标识符
    BUILTIN_TYPES = {'Int', 'Float', 'String', 'Bool', 'List', 'Dict'}

    SYMBOLS = {
        '(', ')', '{', '}', '[', ']', ',', ':', ';', '=', '.', '->', '=>',
        '+', '-', '*', '/', '%', '**', '//', '==', '!=', '<', '>', '<=', '>=',
        '!', '&&', '||', '&', '|', '^', '~', '<<', '>>', ':=', '++', '--',
        '+=', '-=', '*=', '/=', '%=', '**=', '//=', '&=', '|=', '^=', '<<=', '>>=',
        '|>'  # 管道操作符
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
            raise SyntaxError(f"未结束的字符串,行 {self.line}")

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
        if char in '(){}[],:;.?' :
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

        raise SyntaxError(f"未知符号: '{char}',行 {self.line},列 {self.column}")

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

    def __hash__(self):
        """基于对象标识的哈希(等同于 Java 默认的 identity hash)"""
        return id(self)

    def __eq__(self, other):
        """基于对象标识的相等性"""
        return self is other

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
    type_params: List[str] = field(default_factory=list)  # 泛型参数如 ['T', 'U']
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
    """成员访问表达式,如 module.function"""
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

@dataclass
class LambdaExpr(Expression):
    """匿名函数表达式: fn(params) { body }"""
    params: List = field(default_factory=list)    # [(name, type_annotation)]
    body: List[ASTNode] = field(default_factory=list)
    return_type: str = None

# ==================== 语法分析器 ====================
class Parser:
    """语法分析器 - 将Token流转换为AST"""

    def __init__(self, tokens: List[Token], source: str = None):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else Token(TokenType.EOF, "", 0, 0)
        self.previous = Token(TokenType.EOF, "", 0, 0)  # 上一个消费的 token
        self.errors: List[str] = []  # 收集所有语法错误
        self.panic_mode = False  # panic mode: 跳过 token 直到找到同步点
        self.source_lines: List[str] = None  # 源码行（用于错误上下文）
        if source:
            self.source_lines = source.split('\n')

    def advance(self):
        """前进到下一个token"""
        self.previous = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token(TokenType.EOF, "", 0, 0)

    def _set_source(self, source: str):
        """设置源码，用于错误信息上下文"""
        self.source_lines = source.split('\n')

    def _format_error(self, token: Token, message: str) -> str:
        """格式化带源码上下文的错误信息"""
        line_num = token.line
        col_num = token.column
        header = f"语法错误: {message}"
        loc = f"   at line {line_num}, column {col_num}"

        if self.source_lines and 0 < line_num <= len(self.source_lines):
            src = self.source_lines[line_num - 1]
            src_display = f"   {line_num} | {src}"
            pointer = ' ' * (len(f"   {line_num} | ") + col_num - 1) + '^'
            return f"{header}\n{loc}\n{src_display}\n{pointer}"
        else:
            return f"{header}\n{loc}"

    def error(self, token: Token, message: str):
        """记录错误并抛出。panic_mode 下只抛出不记录(抑制级联报错)"""
        formatted = self._format_error(token, message)
        if not self.panic_mode:
            self.errors.append(formatted)
        self.panic_mode = True
        raise SyntaxError(formatted)

    def synchronize(self):
        """跳过 token 直到语句边界(; / 关键字 / } / EOF)"""
        self.panic_mode = False
        safety = 0

        while not self.match(TokenType.EOF) and safety < 5000:
            safety += 1
            # 刚跳过了一个分号 → 语句边界
            if self.previous.type == TokenType.SYMBOL and self.previous.value == ';':
                return

            # 下一 token 是语句起始关键字 → 可以重新开始
            statement_starters = {
                'let', 'var', 'const', 'def', 'if', 'while', 'for',
                'return', 'break', 'continue', 'print', 'import', 'export',
                'class'
            }
            if self.current_token.type == TokenType.KEYWORD and self.current_token.value in statement_starters:
                return
            if self.current_token.type == TokenType.IDENTIFIER and self.current_token.value in statement_starters:
                return

            # 遇到 } 块结束 → 停止(让调用者处理)
            if self.match(TokenType.SYMBOL, '}'):
                return

            self.advance()

    def peek(self) -> Token:
        """查看下一个token"""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(TokenType.EOF, "", 0, 0)

    def expect(self, token_type: TokenType, value: Optional[str] = None) -> Token:
        """期望当前token符合要求。遇错调用 error() → 抛出 SyntaxError"""
        if self.current_token.type != token_type:
            expected = f"{token_type.value}" + (f" '{value}'" if value else "")
            got = f"{self.current_token.type.value} '{self.current_token.value}'"
            self.error(self.current_token, f"期望 {expected},但得到 {got}")
            # error() 会 raise,此行不会执行

        if value is not None and self.current_token.value != value:
            self.error(self.current_token, f"期望 '{value}',但得到 '{self.current_token.value}'")

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
        """解析整个程序 - 带 panic mode 错误恢复。始终返回 Program,调用者检查 self.errors"""
        program = Program()

        while not self.match(TokenType.EOF):
            # 跳过无关token
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue

            # 跳过孤立的 } (可能是错误恢复后的残留,或裸块结束)
            if self.match(TokenType.SYMBOL, '}'):
                self.advance()
                continue

            try:
                # 解析函数定义
                if self.match(TokenType.KEYWORD, 'def'):
                    func = self.parse_function_def()
                    if func is not None:
                        program.add_function(func)
                # 解析类声明
                elif self.match(TokenType.KEYWORD, 'class'):
                    cls = self.parse_class_decl()
                    if cls is not None:
                        program.add_statement(cls)
                # 解析语句
                else:
                    stmt = self.parse_statement()
                    if stmt:
                        program.add_statement(stmt)
            except SyntaxError:
                # error() 已记录错误,跳至下一个同步点继续解析
                self.synchronize()

        return program

    def parse_function_def(self) -> FunctionDef:
        """解析函数定义"""
        start_token = self.expect(TokenType.KEYWORD, 'def')
        func = FunctionDef(line=start_token.line, column=start_token.column, filename=start_token.filename)

        # 函数名
        func.name = self.expect(TokenType.IDENTIFIER).value

        # 泛型参数: identity<T>(x: T) -> T
        if self.match(TokenType.OPERATOR, '<'):
            self.advance()
            func.type_params.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                func.type_params.append(self.expect(TokenType.IDENTIFIER).value)
            self.expect(TokenType.OPERATOR, '>')

        # 参数列表
        self.expect(TokenType.SYMBOL, '(')
        func.params = self.parse_parameter_list()
        self.expect(TokenType.SYMBOL, ')')

        # 返回类型 (支持 :Type 和 ->Type 两种语法)
        if self.match(TokenType.SYMBOL, ':'):
            self.advance()
            func.return_type = self._parse_type_annotation()
        elif self.match(TokenType.OPERATOR, '->'):
            self.advance()
            func.return_type = self._parse_type_annotation()

        # 契约
        while True:
            # 跳过换行
            while self.match(TokenType.NEWLINE):
                self.advance()

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

        # 跳过契约与函数体之间的换行
        while self.match(TokenType.NEWLINE):
            self.advance()

        # 函数体
        self.expect(TokenType.SYMBOL, '{')
        while not self.match(TokenType.SYMBOL, '}'):
            stmt = self.parse_statement()
            if stmt:
                func.body.append(stmt)
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
                param_type = self._parse_type_annotation()
            params.append((param_name, param_type))

            # 更多参数
            while self.match(TokenType.SYMBOL, ','):
                self.advance()  # 消耗逗号
                param_name = self.expect(TokenType.IDENTIFIER).value
                # 检查是否有类型标注
                param_type = "Any"
                if self.match(TokenType.SYMBOL, ':'):
                    self.advance()  # 消耗冒号
                    param_type = self._parse_type_annotation()
                params.append((param_name, param_type))

        return params

    def parse_lambda_expr(self) -> 'LambdaExpr':
        """解析匿名函数表达式: fn(params) { body }"""
        start_token = self.expect(TokenType.KEYWORD, 'fn')
        
        # 参数列表
        self.expect(TokenType.SYMBOL, '(')
        params = self.parse_parameter_list()
        self.expect(TokenType.SYMBOL, ')')
        
        # 可选的返回类型
        return_type = None
        if self.match(TokenType.SYMBOL, ':'):
            self.advance()
            return_type = self._parse_type_annotation()
        elif self.match(TokenType.OPERATOR, '->'):
            self.advance()
            return_type = self._parse_type_annotation()
        
        # 函数体
        self.expect(TokenType.SYMBOL, '{')
        body = []
        while not self.match(TokenType.SYMBOL, '}'):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.expect(TokenType.SYMBOL, '}')
        
        return LambdaExpr(
            params=params, body=body, return_type=return_type,
            line=start_token.line, column=start_token.column
        )

    def parse_class_decl(self) -> Optional['ClassStmt']:
        """解析类声明 class Name < SuperClass { methods... }"""
        start_token = self.expect(TokenType.KEYWORD, 'class')
        name_token = self.expect(TokenType.IDENTIFIER)
        class_name = name_token.value

        # 继承
        superclass = None
        if self.match(TokenType.OPERATOR, '<'):
            self.advance()
            super_token = self.expect(TokenType.IDENTIFIER)
            superclass = super_token.value

        self.expect(TokenType.SYMBOL, '{')

        cls = ClassStmt(name=class_name, superclass=superclass,
                        line=start_token.line, column=start_token.column)

        while not self.match(TokenType.SYMBOL, '}') and not self.match(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue
            if self.match(TokenType.KEYWORD, 'def'):
                method = self.parse_function_def()
                if method:
                    cls.methods.append(method)
            elif self.match(TokenType.KEYWORD, 'let'):
                # 类字段声明 let x: Int;
                self.advance()
                fname = self.expect(TokenType.IDENTIFIER).value
                cls.fields.append(fname)
                if self.match(TokenType.SYMBOL, ':'):
                    self.advance()
                    self._parse_type_annotation()
                self.expect(TokenType.SYMBOL, ';')
            else:
                self.error(self.current_token, f"类体内只允许 def 方法或 let 字段声明")

        self.expect(TokenType.SYMBOL, '}')
        return cls

    def parse_statement(self) -> Optional[ASTNode]:
        """解析语句"""
        # 跳过开头的换行符 - 关键修复
        while self.match(TokenType.NEWLINE):
            self.advance()

        # 检查是否遇到函数体结束符 - 关键修复
        if self.match(TokenType.SYMBOL, '}'):
            return None

        # 裸块作用域(Intent 不支持独立 {} 块)
        if self.match(TokenType.SYMBOL, '{'):
            self.error(self.current_token, 'Intent 不支持裸块作用域 "{...}",变量作用域由函数和 if/else 自然界定')
            self.advance()  # 跳过 {
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
            # 跳过后续换行 → 函数体末尾的表达式允许省略分号
            while self.match(TokenType.NEWLINE):
                self.advance()
            if not self.match(TokenType.SYMBOL, '}'):
                self.expect(TokenType.SYMBOL, ';')
            return expr

        return None

    def parse_variable_decl(self) -> VariableDecl:
        """解析变量声明"""
        keyword = self.current_token.value
        start_token = self.current_token
        self.advance()  # 跳过let/var/const

        # 检测 mut 关键字: let mut x = ... 表示可变变量
        if keyword == 'let' and self.match(TokenType.KEYWORD, 'mut'):
            is_const = False
            self.advance()  # 跳过 mut
        elif keyword == 'var':
            is_const = False
        elif keyword == 'let':
            is_const = True
        else:
            is_const = (keyword == 'const')

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
            decl.var_type = self._parse_type_annotation()

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

        # 解析模块名(支持点号分隔,如 std.math)
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

    def parse_if_expr(self) -> IfExpr:
        """解析 if 表达式 - else 是必须的,因为表达式必须总有值"""
        start_token = self.current_token  # 'if' keyword
        self.advance()  # 消耗 if

        condition = self.parse_expression()

        self.expect(TokenType.SYMBOL, '{')
        then_body = []
        while not self.match(TokenType.SYMBOL, '}'):
            s = self.parse_statement()
            if s:
                then_body.append(s)
        self.expect(TokenType.SYMBOL, '}')

        # if 表达式必须有 else
        if not self.match(TokenType.KEYWORD, 'else'):
            self.error(start_token, "if 表达式必须有 else 分支")
            return IfExpr(line=start_token.line, column=start_token.column)
        self.advance()

        self.expect(TokenType.SYMBOL, '{')
        else_body = []
        while not self.match(TokenType.SYMBOL, '}'):
            s = self.parse_statement()
            if s:
                else_body.append(s)
        self.expect(TokenType.SYMBOL, '}')

        return IfExpr(condition=condition, then_body=then_body, else_body=else_body,
                      line=start_token.line, column=start_token.column)

    def parse_match_expr(self) -> 'MatchExpr':
        """解析 match 表达式: match value { pat [if guard] => body, ... }"""
        start_token = self.current_token  # 'match'
        self.advance()

        value = self.parse_expression()

        self.expect(TokenType.SYMBOL, '{')
        cases = []
        while not self.match(TokenType.SYMBOL, '}'):
            case = self._parse_match_case()
            if case:
                cases.append(case)
            # 逗号分隔分支
            if self.match(TokenType.SYMBOL, ','):
                self.advance()
        self.expect(TokenType.SYMBOL, '}')

        # 穷举性检查
        self._check_match_exhaustive(cases, start_token)

        return MatchExpr(value=value, cases=cases, line=start_token.line, column=start_token.column)

    def _check_match_exhaustive(self, cases, token) -> None:
        """静态检查 match 分支是否穷举所有可能情况"""
        # 收集所有叶子模式（展平或模式）
        all_patterns = []
        for case in cases:
            all_patterns.extend(self._flatten_or_pattern(case.pattern))

        # 通配符 _ → 总是穷举
        if any(isinstance(p, WildcardPattern) for p in all_patterns):
            return
        # 变量模式也匹配一切
        if any(isinstance(p, VariablePattern) for p in all_patterns):
            return

        # Bool 穷举: true + false 必须同时存在
        bool_values = set()
        has_non_bool = False
        for p in all_patterns:
            if isinstance(p, LiteralPattern) and isinstance(p.value, bool):
                bool_values.add(p.value)
            elif isinstance(p, LiteralPattern):
                has_non_bool = True
        if bool_values and not has_non_bool:
            if True not in bool_values:
                self.error(token, "match 未穷举: Bool 类型缺少 true 分支")
                return
            if False not in bool_values:
                self.error(token, "match 未穷举: Bool 类型缺少 false 分支")
                return
            return  # 纯 Bool match 已穷举

        # 构造器模式: 如果只用了 Ok/Err，两者都需要
        constructors = set()
        has_other_pattern = False
        for p in all_patterns:
            if isinstance(p, ConstructorPattern):
                constructors.add(p.constructor)
            elif not isinstance(p, LiteralPattern):
                has_other_pattern = True
        if constructors and not has_other_pattern:
            if 'Ok' in constructors and 'Err' in constructors:
                return  # Result 穷举
            if 'Ok' not in constructors:
                self.error(token, "match 未穷举: Result 类型缺少 Ok 分支")
            if 'Err' not in constructors:
                self.error(token, "match 未穷举: Result 类型缺少 Err 分支")
            return

        # 无法静态确定但无通配符 → 警告
        if not has_other_pattern and not constructors:
            self.error(token,
                f"match 缺少通配符 _ 分支，可能未穷举所有情况")

    def _flatten_or_pattern(self, pattern: 'MatchPattern') -> list:
        """展平或模式为叶子模式列表"""
        if isinstance(pattern, OrPattern):
            result = []
            for p in pattern.patterns:
                result.extend(self._flatten_or_pattern(p))
            return result
        return [pattern]

    def _parse_match_case(self) -> Optional['MatchCase']:
        """解析单个 match 分支: pattern [if guard] => body"""
        # 跳过换行
        while self.match(TokenType.NEWLINE):
            self.advance()
        if self.match(TokenType.SYMBOL, '}'):
            return None

        token = self.current_token
        pattern = self._parse_pattern()

        # 可选的守卫
        guard = None
        if self.match(TokenType.KEYWORD, 'if'):
            self.advance()
            guard = self.parse_expression()

        # => 箭头 (tokenized as OPERATOR by lexer)
        self.expect(TokenType.OPERATOR, '=>')

        # 体: 单表达式 或 块 { ... }
        if self.match(TokenType.SYMBOL, '{'):
            self.advance()
            body_block = []
            while not self.match(TokenType.SYMBOL, '}'):
                s = self.parse_statement()
                if s:
                    body_block.append(s)
            self.expect(TokenType.SYMBOL, '}')
            return MatchCase(pattern=pattern, guard=guard, body_block=body_block,
                            line=token.line, column=token.column)
        else:
            body = self.parse_expression()
            return MatchCase(pattern=pattern, guard=guard, body=body,
                            line=token.line, column=token.column)

    def _parse_pattern(self) -> MatchPattern:
        """解析匹配模式: literal | variable | _ | or_pattern"""
        # 通配符 _
        if self.match(TokenType.IDENTIFIER, '_'):
            token = self.current_token
            self.advance()
            # 如果 _ 后跟 | 则是或模式的开始
            if self.match(TokenType.SYMBOL, '|'):
                return self._parse_or_pattern(WildcardPattern())
            return WildcardPattern()

        # null
        if self.match(TokenType.KEYWORD, 'null') or self.match(TokenType.KEYWORD, 'None'):
            self.advance()
            return LiteralPattern(value=None)

        # true / false
        if self.match(TokenType.KEYWORD, 'True') or self.match(TokenType.KEYWORD, 'true'):
            self.advance()
            return LiteralPattern(value=True)
        if self.match(TokenType.KEYWORD, 'False') or self.match(TokenType.KEYWORD, 'false'):
            self.advance()
            return LiteralPattern(value=False)

        # 数字
        if self.match(TokenType.NUMBER):
            token = self.current_token
            self.advance()
            val = int(token.value) if '.' not in token.value else float(token.value)
            return LiteralPattern(value=val)

        # 字符串
        if self.match(TokenType.STRING):
            token = self.current_token
            self.advance()
            return LiteralPattern(value=token.value)

        # 标识符 → 变量模式 或 构造器模式 (Ok(v)/Err(e))
        if self.match(TokenType.IDENTIFIER):
            token = self.current_token
            name = token.value

            # 构造器模式: Ok(inner) / Err(inner)
            if name in ('Ok', 'Err') and self.peek() and self.peek().type == TokenType.SYMBOL and self.peek().value == '(':
                self.advance()  # 消费 Ok/Err
                self.expect(TokenType.SYMBOL, '(')
                inner = self._parse_pattern()
                self.expect(TokenType.SYMBOL, ')')
                return ConstructorPattern(constructor=name, inner=inner)

            self.advance()
            return VariablePattern(name=token.value)

        self.error(self.current_token, f"不支持的匹配模式")
        return WildcardPattern()

    def _parse_or_pattern(self, first: MatchPattern) -> OrPattern:
        """解析或模式: pat1 | pat2 | pat3"""
        patterns = [first]
        while self.match(TokenType.SYMBOL, '|'):
            self.advance()
            patterns.append(self._parse_pattern())
        return OrPattern(patterns=patterns)

    def _parse_type_annotation(self) -> str:
        """解析类型标注: Int | List[Int] | Dict[String, Int] | Result[Int, String]"""
        base = self.expect(TokenType.IDENTIFIER).value

        # 泛型参数 (支持 <> 和 [])
        if self.match(TokenType.OPERATOR, '<') or self.match(TokenType.SYMBOL, '['):
            bracket = self.current_token.value
            self.advance()
            args = []
            # 第一个类型参数
            next_type = self._parse_type_annotation()
            args.append(next_type)
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                args.append(self._parse_type_annotation())
            if bracket == '<':
                self.expect(TokenType.OPERATOR, '>')
            else:
                self.expect(TokenType.SYMBOL, ']')
            return f"{base}<{', '.join(args)}>"

        return base

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
        """解析表达式 - 管道具有最低优先级"""
        return self.parse_pipe()

    def parse_pipe(self) -> Expression:
        """解析管道表达式 left |> right
        管道语义: right 必须是可调用表达式, left 作为参数传入
        左结合: a |> f |> g => (a |> f) |> g => g(f(a))
        """
        expr = self.parse_logical_or()

        while self.match(TokenType.OPERATOR) and self.current_token.value == '|>':
            op_token = self.current_token
            self.advance()
            right = self.parse_logical_or()
            expr = PipeExpr(left=expr, right=right, line=op_token.line, column=op_token.column)

        return expr

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

        return self.parse_postfix()

    def parse_postfix(self) -> Expression:
        """解析后缀运算符链: .member (args) [index] ?"""
        expr = self.parse_primary()
        
        while True:
            # 函数调用
            if self.match(TokenType.SYMBOL, '('):
                self.advance()
                call = CallExpr(func=expr, line=expr.line, column=expr.column)
                if not self.match(TokenType.SYMBOL, ')'):
                    call.args.append(self.parse_expression())
                    while self.match(TokenType.SYMBOL, ','):
                        self.advance()
                        call.args.append(self.parse_expression())
                self.expect(TokenType.SYMBOL, ')')
                expr = call
            
            # 属性访问 / 属性赋值
            elif self.match(TokenType.SYMBOL, '.'):
                dot_token = self.current_token
                self.advance()
                member_name = self.current_token.value
                member_token = self.current_token
                self.advance()
                
                # 属性赋值: obj.field = value 或 obj.field += value
                if self.match(TokenType.OPERATOR) and self.current_token.value in (
                    '=', '+=', '-=', '*=', '/=', '%=', '**='):
                    op = self.current_token.value
                    self.advance()
                    val = self.parse_assignment_value()
                    expr = SetExpr(obj=expr, name=member_name, value=val,
                                  line=member_token.line, column=member_token.column)
                    break  # SetExpr 是终端的，不能再继续链式
                else:
                    expr = MemberAccess(obj=expr, member=member_name,
                                       line=member_token.line, column=member_token.column)
            
            # 下标访问
            elif self.match(TokenType.SYMBOL, '['):
                self.advance()
                index_expr = self.parse_expression()
                self.expect(TokenType.SYMBOL, ']')
                expr = SubscriptExpr(obj=expr, index=index_expr,
                                    line=self.current_token.line, column=self.current_token.column)
            
            # ? 操作符 — Err 提前返回
            elif self.match(TokenType.SYMBOL, '?'):
                token = self.current_token
                self.advance()
                expr = TryExpr(expr=expr, line=token.line, column=token.column)
            
            else:
                break
        
        return expr
    
    def parse_assignment_value(self) -> Expression:
        """解析赋值右侧的值（用于 SetExpr）"""
        return self.parse_expression()

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

        elif self.match(TokenType.KEYWORD, 'True') or self.match(TokenType.KEYWORD, 'true'):
            self.advance()
            return Literal(value=True, literal_type='bool', line=token.line, column=token.column)

        elif self.match(TokenType.KEYWORD, 'False') or self.match(TokenType.KEYWORD, 'false'):
            self.advance()
            return Literal(value=False, literal_type='bool', line=token.line, column=token.column)

        elif self.match(TokenType.KEYWORD, 'None') or self.match(TokenType.KEYWORD, 'null'):
            self.advance()
            return Literal(value=None, literal_type='none', line=token.line, column=token.column)
        
        # this 关键字
        elif self.match(TokenType.KEYWORD, 'this'):
            self.advance()
            return ThisExpr(line=token.line, column=token.column)
        
        # if 表达式: if cond { expr1 } else { expr2 }
        elif self.match(TokenType.KEYWORD, 'if'):
            return self.parse_if_expr()

        # match 表达式: match value { pattern => body, ... }
        elif self.match(TokenType.KEYWORD, 'match'):
            return self.parse_match_expr()

        # 匿名函数: fn(params) { body }
        elif self.match(TokenType.KEYWORD, 'fn'):
            return self.parse_lambda_expr()

        # 变量
        elif self.match(TokenType.IDENTIFIER):
            self.advance()
            return Variable(name=token.value, line=token.line, column=token.column)

        # 列表
        elif self.match(TokenType.SYMBOL, '['):
            return self.parse_list_expr()

        # 字典
        elif self.match(TokenType.SYMBOL, '{'):
            return self.parse_dict_expr()

        # 括号表达式
        elif self.match(TokenType.SYMBOL, '('):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.SYMBOL, ')')
            return expr

        # 修改错误信息,提供更友好的提示
        if token.type == TokenType.NEWLINE:
            self.error(token, f"表达式不完整,在第{token.line}行第{token.column}列意外换行")
        else:
            self.error(token, f"无法解析表达式,意外的token: {token.value},期望表达式")

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

    def parse_dict_expr(self) -> 'DictExpr':
        """解析字典表达式 {key: value, ...}"""
        start_token = self.expect(TokenType.SYMBOL, '{')
        expr = DictExpr(line=start_token.line, column=start_token.column)

        if not self.match(TokenType.SYMBOL, '}'):
            key = self.parse_expression()
            self.expect(TokenType.SYMBOL, ':')
            value = self.parse_expression()
            expr.entries.append((key, value))
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                key = self.parse_expression()
                self.expect(TokenType.SYMBOL, ':')
                value = self.parse_expression()
                expr.entries.append((key, value))

        self.expect(TokenType.SYMBOL, '}')
        return expr

@dataclass
class ListExpr(Expression):
    """列表表达式"""
    elements: List[Expression] = field(default_factory=list)

@dataclass
class DictExpr(Expression):
    """字典表达式 {key: value, ...}"""
    entries: List[Tuple[Expression, Expression]] = field(default_factory=list)  # (key_expr, value_expr)

@dataclass
class SubscriptExpr(Expression):
    """下标访问表达式 obj[index]"""
    obj: Expression = None
    index: Expression = None
    line: int = 0
    column: int = 0

# ── Match(模式匹配) ─────────────────────────────────

@dataclass
class MatchPattern(ASTNode):
    """匹配模式基类"""
    pass

@dataclass
class LiteralPattern(MatchPattern):
    """字面量模式: 1, "hello", true, null"""
    value: Any = None

@dataclass
class VariablePattern(MatchPattern):
    """变量模式: n(绑定匹配值)"""
    name: str = ""

@dataclass
class WildcardPattern(MatchPattern):
    """通配符模式: _(匹配任意值)"""
    pass

@dataclass
class OrPattern(MatchPattern):
    """或模式: 1 | 2 | 3"""
    patterns: List[MatchPattern] = field(default_factory=list)

@dataclass
class ConstructorPattern(MatchPattern):
    """构造器模式: Ok(v), Err(e) - 解构 Result 等"""
    constructor: str = ""  # "Ok" | "Err"
    inner: Optional[MatchPattern] = None  # 内部模式 (v, e)

@dataclass
class MatchCase(ASTNode):
    """match 分支: pattern [if guard] => body"""
    pattern: MatchPattern = None
    guard: Optional[Expression] = None
    body: Optional[Expression] = None  # 单表达式体
    body_block: List[ASTNode] = field(default_factory=list)  # 块体

@dataclass
class MatchExpr(Expression):
    """match 表达式: match value { pattern => body, ... }"""
    value: Expression = None
    cases: List[MatchCase] = field(default_factory=list)
    line: int = 0
    column: int = 0

# ── 异常 ──────────────────────────────────────────────

class MatchError(Exception):
    """match 未覆盖所有情况"""
    def __init__(self, message: str, line: int = 0):
        self.line = line
        super().__init__(message)

@dataclass
class PipeExpr(Expression):
    """管道表达式 left |> right
    语义: 将 left 求值后作为参数传给 right 调用 → right(left)
    例如: data |> filter 等价于 filter(data)
          data |> filter |> map 等价于 map(filter(data))
    """
    left: Expression = None
    right: Expression = None
    line: int = 0
    column: int = 0

@dataclass
class IfExpr(Expression):
    """if 表达式: if cond { then } else { else }
    区别于 IfStmt:else 是必须的,求值为所选分支的结果
    """
    condition: Expression = None
    then_body: List[ASTNode] = field(default_factory=list)
    else_body: List[ASTNode] = field(default_factory=list)
    line: int = 0
    column: int = 0

@dataclass
class TryExpr(Expression):
    """? 运算符: expr ?  -- 遇 Err 提前 return"""
    expr: Expression = None
    line: int = 0
    column: int = 0


# ── 面向对象:类系统 ──────────────────────────────

@dataclass
class ClassStmt(ASTNode):
    """类声明 class Name < SuperClass { methods... }"""
    name: str = ""
    superclass: Optional[str] = None
    methods: List['FunctionDef'] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)  # let 声明的字段名

@dataclass
class GetExpr(Expression):
    """属性读取 obj.property"""
    obj: Expression = None
    name: str = ""

@dataclass
class SetExpr(Expression):
    """属性赋值 obj.property = value"""
    obj: Expression = None
    name: str = ""
    value: Expression = None

@dataclass
class ThisExpr(Expression):
    """this 关键字 - 当前实例引用"""
    pass


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

class NoneType(Type):
    """空类型 - 只有一个值 None/null"""

    def __init__(self):
        super().__init__("None")

    def can_assign_from(self, other: Type) -> bool:
        return isinstance(other, NoneType)

class DictType(Type):
    """字典类型 Dict[K, V]"""

    def __init__(self, key_type: Type, value_type: Type):
        super().__init__(f"Dict[{key_type}, {value_type}]")
        self.key_type = key_type
        self.value_type = value_type

    def can_assign_from(self, other: Type) -> bool:
        if isinstance(other, DictType):
            return (self.key_type.can_assign_from(other.key_type) and
                    self.value_type.can_assign_from(other.value_type))
        return False

class ResultType(Type):
    """Result<T, E> - 成功或失败的结果类型"""

    def __init__(self, ok_type: Type, err_type: Type):
        super().__init__(f"Result[{ok_type}, {err_type}]")
        self.ok_type = ok_type
        self.err_type = err_type

    def can_assign_from(self, other: Type) -> bool:
        if isinstance(other, ResultType):
            return (self.ok_type.can_assign_from(other.ok_type) and
                    self.err_type.can_assign_from(other.err_type))
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
        """创建副本 - 修复:返回正确的子类类型"""
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

    def __eq__(self, other):
        if isinstance(other, FloatValue):
            return self.value == other.value
        return NotImplemented

    def __hash__(self):
        return hash(float(self.value))

class StringValue(RuntimeValue):
    """字符串值"""

    def __init__(self, value: str):
        super().__init__(StringType(), value)

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, StringValue):
            return self.value == other.value
        return NotImplemented

    def __hash__(self):
        return hash(self.value)

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

    def __init__(self, values: List[RuntimeValue], element_type: Type = None):
        if element_type is None:
            element_type = IntType() if not values else values[0].get_type()
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

class NoneValue(RuntimeValue):
    """空值 - Intent 中的 None/null"""

    def __init__(self):
        super().__init__(NoneType(), None)

    def __str__(self):
        return "空"

    def __repr__(self):
        return "None"

    def to_bool(self) -> bool:
        return False

class DictValue(RuntimeValue):
    """字典值 - 键值对集合"""

    def __init__(self, entries: Dict = None, key_type: Type = None, value_type: Type = None):
        """entries: Python dict key (str/int/float) → RuntimeValue"""
        if entries is None:
            entries = {}
        if key_type is None:
            key_type = StringType()
        if value_type is None:
            value_type = IntType()
        super().__init__(DictType(key_type, value_type), entries)

    def __str__(self):
        items = ", ".join(f"{k}: {v}" for k, v in self.value.items())
        return f"{{{items}}}"

    def __repr__(self):
        return str(self)

    def get(self, key) -> RuntimeValue:
        val = self.value.get(key)
        if val is not None:
            return val
        # 松散匹配：如果 raw value 跟 dict key 的 RuntimeValue.value 相等
        raw_key = key
        if isinstance(key, (StringValue, IntValue, FloatValue, BoolValue)):
            raw_key = key.value
        for k, v in self.value.items():
            if (isinstance(k, (StringValue, IntValue, FloatValue, BoolValue))
                    and k.value == raw_key):
                return v

    def set(self, key, value: RuntimeValue):
        self.value[key] = value

    def to_bool(self) -> bool:
        return len(self.value) > 0

@dataclass
class ResultValue(RuntimeValue):
    """Result<T, E> 值 - 可能成功也可能失败"""
    is_ok: bool = True

    def __init__(self, ok_type: Type, err_type: Type):
        super().__init__(ResultType(ok_type, err_type), None)
        self.is_ok = True
        self.ok_value = None
        self.err_value = None
        self.ok_type = ok_type
        self.err_type = err_type

    def __str__(self):
        if self.is_ok:
            return f"Ok({self.ok_value})"
        return f"Err({self.err_value})"

    def __repr__(self):
        return str(self)

    def get_type(self) -> Type:
        return ResultType(self.ok_type, self.err_type)

    def to_bool(self) -> bool:
        return self.is_ok

    def unwrap(self) -> RuntimeValue:
        """解包 Ok 值,如果是 Err 则抛异常"""
        if self.is_ok:
            return self.ok_value
        raise NameError(f"unwrap 了 Err: {self.err_value}")

    def copy(self) -> 'ResultValue':
        rv = ResultValue(self.ok_type, self.err_type)
        rv.is_ok = self.is_ok
        rv.ok_value = self.ok_value.copy() if self.ok_value else None
        rv.err_value = self.err_value.copy() if self.err_value else self.err_value
        return rv

def make_ok(value: RuntimeValue, err_type: Type = None) -> ResultValue:
    """创建 Ok 值"""
    if err_type is None:
        err_type = StringType()
    rv = ResultValue(value.get_type(), err_type)
    rv.is_ok = True
    rv.ok_value = value
    return rv

def make_err(error: RuntimeValue, ok_type: Type = None) -> ResultValue:
    """创建 Err 值"""
    if ok_type is None:
        ok_type = IntType()
    rv = ResultValue(ok_type, error.get_type())
    rv.is_ok = False
    rv.err_value = error
    return rv

@dataclass
class FunctionValue(RuntimeValue):
    """函数值 - 闭包载体

    持有函数定义 AST + 捕获的定义时作用域(closure)。
    这是实现闭包的关键:内部函数记住它被定义时的环境。
    """
    func_def: Any = None           # FunctionDef AST 节点
    closure: Any = None            # 定义时的 Scope

    def __init__(self, func_def, closure):
        display_name = getattr(func_def, 'name', '<lambda>')
        super().__init__(StringType(), display_name)
        self.func_def = func_def
        self.closure = closure

    def __str__(self):
        contract = ""
        func_def = self.func_def
        if hasattr(func_def, 'requires') and func_def.requires:
            contract += "⚖️"
        if hasattr(func_def, 'is_pure') and func_def.is_pure:
            contract += "🧘"
        display_name = getattr(func_def, 'name', '<lambda>')
        return f"<功夫 {contract}{display_name}>"

    def __repr__(self):
        return str(self)

    def copy(self):
        return FunctionValue(self.func_def, self.closure)


@dataclass
class ClassValue(RuntimeValue):
    """类对象 - 可调用的类型工厂"""
    name: str = ""
    methods: Dict[str, FunctionValue] = field(default_factory=dict)
    superclass: Optional['ClassValue'] = None

    def __init__(self, name: str, methods: Dict[str, FunctionValue], superclass=None):
        super().__init__(StringType(), name)
        self.name = name
        self.methods = methods
        self.superclass = superclass

    def find_method(self, name: str) -> Optional[FunctionValue]:
        """查找方法(含继承链)"""
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.find_method(name)
        return None

    def call(self, interpreter, args: List[RuntimeValue]) -> RuntimeValue:
        """实例化类:创建 InstanceValue,调用 init"""
        instance = InstanceValue(self)
        init_method = self.find_method('init')
        if init_method:
            # 用 interpreter 执行 init 方法
            interpreter._execute_method(init_method, instance, args)
        return instance

    def copy(self):
        return ClassValue(self.name, self.methods, self.superclass)

    def __str__(self):
        return f"<类 {self.name}>"

    def __repr__(self):
        return str(self)


@dataclass
class InstanceValue(RuntimeValue):
    """类实例 - 持有字段和方法表的对象"""
    klass: ClassValue = None
    fields: Dict[str, RuntimeValue] = field(default_factory=dict)

    def __init__(self, klass: ClassValue):
        # 实例类型名 = 类名
        super().__init__(StringType(), klass.name)
        self.klass = klass
        self.fields = {}

    def get(self, name: str) -> Optional[RuntimeValue]:
        """读取字段"""
        if name in self.fields:
            return self.fields[name]
        # 回退到方法
        method = self.klass.find_method(name)
        if method:
            return method
        return None

    def set(self, name: str, value: RuntimeValue):
        """设置字段"""
        self.fields[name] = value

    def copy(self):
        inst = InstanceValue(self.klass)
        inst.fields = {k: v.copy() for k, v in self.fields.items()}
        return inst

    def __str__(self):
        items = ", ".join(f"{k}: {v}" for k, v in self.fields.items())
        return f"<{self.klass.name} {{{items}}}>"

    def __repr__(self):
        return str(self)


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

    def ancestor(self, depth: int) -> 'Scope':
        """向上走 depth 层(深度解析用)

        depth=0 返回自身,depth=1 返回 parent,以此类推
        """
        scope = self
        for _ in range(depth):
            if scope.parent is None:
                raise RuntimeError(f"作用域深度不足: 请求 depth={depth}")
            scope = scope.parent
        return scope

    def get_at(self, depth: int, name: str) -> RuntimeValue:
        """从第 depth 层祖先作用域获取变量(闭包支持)"""
        return self.ancestor(depth).symbols[name]

    def assign_at(self, depth: int, name: str, value: RuntimeValue) -> None:
        """向第 depth 层祖先作用域赋值变量"""
        scope = self.ancestor(depth)
        if name in scope.constants:
            raise ValueError(f"无法修改常量 '{name}'")
        scope.symbols[name] = value

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
        self.loading_modules: set = set()  # 正在加载的模块(用于检测循环导入)

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
                parser = Parser(tokens, code)
                ast = parser.parse()

                # 执行模块代码
                self.interpreter.execute_program(ast)

                # 收集模块中的所有符号(暂时全部导出)
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
        # ── Resolver 集成:locals 字典 ──
        # key: Expression AST 节点, value: 该变量引用的作用域深度
        # 空字典表示未经过 resolver,走旧版链式查找
        self.locals: Dict[Any, int] = {}
        # ── 错误上下文跟踪 ──
        self.source_lines: List[str] = []
        self.current_line: int = 0
        self.current_col: int = 0

    def resolve(self, expr, depth: int) -> None:
        """Resolver 回调:记录表达式的变量深度

        用 id(expr) 作为 key,绕过 dataclass 的 unhashable 问题。
        """
        self.locals[id(expr)] = depth

    def look_up_variable(self, name: str, expr) -> RuntimeValue:
        """查找变量 - 优先用 Resolver 确定的深度

        如果 Resolver 已经确定了这个表达式的变量深度,
        用 get_at(depth, name) 精确获取(闭包安全)。
        否则回退到旧的链式查找。
        """
        expr_id = id(expr)
        if expr_id in self.locals:
            depth = self.locals[expr_id]
            return self.current_scope.get_at(depth, name)
        else:
            # 全局变量或未解析的变量:链式查找
            return self.global_scope.get(name)

    def _run_resolver(self, program) -> None:
        """运行语义分析遍(Resolver)

        在执行之前静态遍历 AST,为每个变量引用标注作用域深度。
        如果 Resolver 发现错误(如变量在自身初始化器中引用),
        错误会累积但不会阻止执行(宽松模式)。
        """
        try:
            from intent_resolver import Resolver
            resolver = Resolver(self)
            resolver.resolve_program(program)
            if resolver.errors:
                print(f"⚠️  [语义分析] 发现 {len(resolver.errors)} 个问题:")
                for err in resolver.errors[:5]:  # 最多显示5个
                    print(f"   • {err}")
                if len(resolver.errors) > 5:
                    print(f"   ... 还有 {len(resolver.errors) - 5} 个")
        except ImportError:
            # Resolver 模块不存在时静默跳过
            pass
        except Exception as e:
            print(f"⚠️  [语义分析] 运行失败: {e}")

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
            'Ok': self._builtin_ok,
            'Err': self._builtin_err,
            'read_file': self._builtin_read_file,
            'write_file': self._builtin_write_file,
            # std/time
            'now': self._builtin_now,
            'sleep': self._builtin_sleep,
            # std/json
            'json_parse': self._builtin_json_parse,
            'json_dump': self._builtin_json_dump,
            # std/math
            'sqrt': self._builtin_sqrt,
            'pow': self._builtin_pow,
            'floor': self._builtin_floor,
            'ceil': self._builtin_ceil,
            # std/random
            'random': self._builtin_random,
            'randint': self._builtin_randint,
            # input
            'input': self._builtin_input,
            # string
            'split': self._builtin_split,
            'join': self._builtin_join,
            'trim': self._builtin_trim,
            'ord': self._builtin_ord,
            'chr': self._builtin_chr,
            # sys
            'version': self._builtin_version,
        }

    def _builtin_print(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置print函数"""
        output = " ".join(str(arg) for arg in args)
        print(output)
        return IntValue(0)

    def _builtin_len(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置len函数"""
        if len(args) != 1:
            raise TypeError(f"len() 期望1个参数,得到 {len(args)}个")

        value = args[0]
        if isinstance(value, (ListValue, StringValue, DictValue)):
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
            raise TypeError(f"range() 期望1-3个参数,得到 {len(args)}个")

        values = [IntValue(i) for i in range(start, stop, step)]
        return ListValue(values, IntType())

    def _builtin_int(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置int函数"""
        if len(args) != 1:
            raise TypeError(f"int() 期望1个参数,得到 {len(args)}个")

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
            raise TypeError(f"float() 期望1个参数,得到 {len(args)}个")

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
            raise TypeError(f"str() 期望1个参数,得到 {len(args)}个")

        return StringValue(str(args[0].value))

    def _builtin_bool(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置bool函数"""
        if len(args) != 1:
            raise TypeError(f"bool() 期望1个参数,得到 {len(args)}个")

        return BoolValue(bool(args[0].value))

    def _builtin_type(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置type函数"""
        if len(args) != 1:
            raise TypeError(f"type() 期望1个参数,得到 {len(args)}个")

        return StringValue(str(args[0].type))

    def _builtin_abs(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置abs函数"""
        if len(args) != 1:
            raise TypeError(f"abs() 期望1个参数,得到 {len(args)}个")

        value = args[0]
        if isinstance(value, IntValue):
            return IntValue(abs(value.value))
        elif isinstance(value, FloatValue):
            return FloatValue(abs(value.value))
        raise TypeError(f"abs() 不支持类型 {value.type}")

    def _builtin_max(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置max函数"""
        if not args:
            raise TypeError(f"max() 期望至少1个参数,得到 0个")

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
            raise TypeError(f"min() 期望至少1个参数,得到 0个")

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
            raise TypeError(f"sum() 期望1个参数,得到 {len(args)}个")

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

    def _builtin_ok(self, args: List[RuntimeValue]) -> RuntimeValue:
        """Ok(value) - 创建成功的 Result"""
        if len(args) != 1:
            raise TypeError(f"Ok() 期望1个参数,得到 {len(args)}个")
        return make_ok(args[0])

    def _builtin_err(self, args: List[RuntimeValue]) -> RuntimeValue:
        """Err(error) - 创建失败的 Result"""
        if len(args) != 1:
            raise TypeError(f"Err() 期望1个参数,得到 {len(args)}个")
        return make_err(args[0])

    def _builtin_read_file(self, args: List[RuntimeValue]) -> RuntimeValue:
        """read_file(path) — 读取文件内容为字符串"""
        if len(args) != 1:
            raise TypeError(f"read_file() 期望1个参数,得到 {len(args)}个")
        path = args[0]
        if not isinstance(path, StringValue):
            raise TypeError(f"read_file() 参数必须是字符串")
        try:
            with open(path.value, 'r', encoding='utf-8') as f:
                return StringValue(f.read())
        except FileNotFoundError:
            raise RuntimeError(f"文件不存在: {path.value}")
        except PermissionError:
            raise RuntimeError(f"没有权限读取文件: {path.value}")

    def _builtin_write_file(self, args: List[RuntimeValue]) -> RuntimeValue:
        """write_file(path, content) — 写入字符串到文件"""
        if len(args) != 2:
            raise TypeError(f"write_file() 期望2个参数(path, content),得到 {len(args)}个")
        path, content = args[0], args[1]
        if not isinstance(path, StringValue):
            raise TypeError(f"write_file() 第1个参数必须是字符串")
        if not isinstance(content, StringValue):
            raise TypeError(f"write_file() 第2个参数必须是字符串")
        try:
            with open(path.value, 'w', encoding='utf-8') as f:
                f.write(content.value)
            return IntValue(0)
        except PermissionError:
            raise RuntimeError(f"没有权限写入文件: {path.value}")

    # ══ std/time ──
    def _builtin_now(self, args: List[RuntimeValue]) -> RuntimeValue:
        """now() — 返回当前 Unix 时间戳（秒，浮点）"""
        import time
        return FloatValue(time.time())

    def _builtin_sleep(self, args: List[RuntimeValue]) -> RuntimeValue:
        """sleep(seconds: Float) — 暂停指定秒数"""
        import time
        if len(args) != 1:
            raise TypeError(f"sleep() 期望1个参数,得到 {len(args)}个")
        secs = args[0]
        if isinstance(secs, IntValue):
            secs = FloatValue(float(secs.value))
        if not isinstance(secs, FloatValue):
            raise TypeError(f"sleep() 参数必须是数字")
        time.sleep(secs.value)
        return IntValue(0)

    # ══ std/json ──
    def _builtin_json_parse(self, args: List[RuntimeValue]) -> RuntimeValue:
        """json_parse(json_str: String) — 解析 JSON 字符串为 Dict/List"""
        import json as _json
        if len(args) != 1:
            raise TypeError(f"json_parse() 期望1个参数,得到 {len(args)}个")
        if not isinstance(args[0], StringValue):
            raise TypeError(f"json_parse() 参数必须是字符串")
        try:
            py_val = _json.loads(args[0].value)
        except _json.JSONDecodeError as je:
            raise ValueError(f"JSON 解析失败: {je.msg} (第{je.lineno}行第{je.colno}列)")
        return self._py_to_runtime(py_val)

    def _builtin_json_dump(self, args: List[RuntimeValue]) -> RuntimeValue:
        """json_dump(value) — 将值序列化为 JSON 字符串"""
        import json as _json
        if len(args) != 1:
            raise TypeError(f"json_dump() 期望1个参数,得到 {len(args)}个")
        py_val = self._runtime_to_py(args[0])
        return StringValue(_json.dumps(py_val, ensure_ascii=False))

    def _py_to_runtime(self, py_val):
        """Python 原生值 → Intent RuntimeValue"""
        if isinstance(py_val, dict):
            d = DictValue()
            for k, v in py_val.items():
                d.value[StringValue(k)] = self._py_to_runtime(v)
            return d
        elif isinstance(py_val, list):
            return ListValue([self._py_to_runtime(item) for item in py_val])
        elif isinstance(py_val, bool):
            return BoolValue(py_val)
        elif isinstance(py_val, int):
            return IntValue(py_val)
        elif isinstance(py_val, float):
            return FloatValue(py_val)
        elif isinstance(py_val, str):
            return StringValue(py_val)
        elif py_val is None:
            return NoneValue()
        return StringValue(str(py_val))

    def _runtime_to_py(self, val):
        """Intent RuntimeValue → Python 原生值"""
        if isinstance(val, IntValue):
            return val.value
        elif isinstance(val, FloatValue):
            return val.value
        elif isinstance(val, StringValue):
            return val.value
        elif isinstance(val, BoolValue):
            return val.value
        elif isinstance(val, NoneValue):
            return None
        elif isinstance(val, ListValue):
            return [self._runtime_to_py(item) for item in val.value]
        elif isinstance(val, DictValue):
            return {self._runtime_to_py(k): self._runtime_to_py(v) for k, v in val.value.items()}
        elif isinstance(val, InstanceValue):
            # 类实例 → {"fields": ...} 字典
            d = {}
            for k, v in val.fields.items():
                d[k] = self._runtime_to_py(v)
            return d
        return str(val)

    # ══ std/math 补充 ──
    def _builtin_sqrt(self, args: List[RuntimeValue]) -> RuntimeValue:
        """sqrt(x: Float) — 平方根"""
        import math
        if len(args) != 1:
            raise TypeError(f"sqrt() 期望1个参数,得到 {len(args)}个")
        x = float(args[0].value)
        return FloatValue(math.sqrt(x))

    def _builtin_pow(self, args: List[RuntimeValue]) -> RuntimeValue:
        """pow(base: Float, exp: Float) — 幂运算"""
        if len(args) != 2:
            raise TypeError(f"pow() 期望2个参数,得到 {len(args)}个")
        return FloatValue(float(args[0].value) ** float(args[1].value))

    def _builtin_floor(self, args: List[RuntimeValue]) -> RuntimeValue:
        """floor(x: Float) — 向下取整"""
        import math
        if len(args) != 1:
            raise TypeError(f"floor() 期望1个参数,得到 {len(args)}个")
        return IntValue(int(math.floor(float(args[0].value))))

    def _builtin_ceil(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ceil(x: Float) — 向上取整"""
        import math
        if len(args) != 1:
            raise TypeError(f"ceil() 期望1个参数,得到 {len(args)}个")
        return IntValue(int(math.ceil(float(args[0].value))))

    # ══ std/random ──
    def _builtin_random(self, args: List[RuntimeValue]) -> RuntimeValue:
        """random() — 返回 [0,1) 均匀分布浮点数"""
        import random
        return FloatValue(random.random())

    def _builtin_randint(self, args: List[RuntimeValue]) -> RuntimeValue:
        """randint(lo: Int, hi: Int) — [lo, hi] 闭区间随机整数"""
        import random
        if len(args) != 2:
            raise TypeError(f"randint() 期望2个参数,得到 {len(args)}个")
        lo = int(args[0].value)
        hi = int(args[1].value)
        return IntValue(random.randint(lo, hi))

    # ══ input ──
    def _builtin_input(self, args: List[RuntimeValue]) -> RuntimeValue:
        """input(prompt: String) — 读取用户输入"""
        prompt = args[0].value if args else ""
        s = input(prompt)
        return StringValue(s)

    # ══ string operations ──
    def _builtin_split(self, args: List[RuntimeValue]) -> RuntimeValue:
        """split(s: String, sep: String) — 按分隔符切割字符串"""
        if len(args) != 2:
            raise TypeError(f"split() 期望2个参数(s, sep),得到 {len(args)}个")
        s = args[0].value
        sep = args[1].value
        return ListValue([StringValue(part) for part in s.split(sep)])

    def _builtin_join(self, args: List[RuntimeValue]) -> RuntimeValue:
        """join(sep: String, parts: List[String]) — 用分隔符连接列表"""
        if len(args) != 2:
            raise TypeError(f"join() 期望2个参数(sep, parts),得到 {len(args)}个")
        sep = args[0].value
        if not isinstance(args[1], ListValue):
            raise TypeError(f"join() 第2个参数必须是列表")
        parts = [item.value for item in args[1].value]
        return StringValue(sep.join(parts))

    def _builtin_trim(self, args: List[RuntimeValue]) -> RuntimeValue:
        """trim(s: String) — 去除首尾空白"""
        if len(args) != 1:
            raise TypeError(f"trim() 期望1个参数,得到 {len(args)}个")
        return StringValue(args[0].value.strip())

    def _builtin_ord(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ord(ch: String) — 字符→整数码点"""
        if len(args) != 1:
            raise TypeError(f"ord() 期望1个参数,得到 {len(args)}个")
        s = args[0].value
        if len(s) != 1:
            raise ValueError(f"ord() 期望长度为1的字符串,得到 '{s}'")
        return IntValue(ord(s))

    def _builtin_chr(self, args: List[RuntimeValue]) -> RuntimeValue:
        """chr(n: Int) — 整数码点→字符"""
        if len(args) != 1:
            raise TypeError(f"chr() 期望1个参数,得到 {len(args)}个")
        return StringValue(chr(int(args[0].value)))

    # ══ sys ──
    def _builtin_version(self, args: List[RuntimeValue]) -> RuntimeValue:
        """version() — 返回 Intent 解释器版本"""
        return StringValue("Intent 1.0.0-alpha | 心学为体 禅道为翼 马哲为用")

    def _set_source(self, code: str) -> None:
        """设置源码行列表,用于错误上下文显示"""
        self.source_lines = code.split('\n')

    def _error_context(self, msg: str) -> str:
        """格式化运行时错误,附加行号和源码片段"""
        parts = [msg]
        if self.source_lines and 0 < self.current_line <= len(self.source_lines):
            line = self.current_line
            col = self.current_col
            src = self.source_lines[line - 1]
            parts.append(f"   at line {line}, column {col}")
            # 显示源码行
            parts.append(f"   {line} | {src}")
            # 指示箭头
            if col > 0:
                indent = 4 + len(str(line))
                parts.append(f"   {' ' * indent}{' ' * (col - 1)}^")
        return '\n'.join(parts)

    def _track_node(self, node) -> None:
        """跟踪当前执行的 AST 节点位置"""
        if hasattr(node, 'line'):
            self.current_line = node.line or self.current_line
        if hasattr(node, 'column'):
            self.current_col = node.column or self.current_col

    def execute_program(self, program: Program, module_mode: bool = False) -> RuntimeValue:
        """执行整个程序
        module_mode=True 时只注册函数/变量,不执行main(用于模块加载)
        """
        # ── 语义分析遍(Resolver)──
        self._run_resolver(program)

        # 注册所有函数
        for func in program.functions.values():
            self.functions[func.name] = func
            # 模块模式下同时写入当前作用域,供导入方使用
            if module_mode:
                self.current_scope.declare(func.name, func, False, allow_redefine=True)

        # 执行全局语句(变量声明等)
        result = IntValue(0)
        for stmt in program.statements:
            result = self.execute_statement(stmt)
            if self.return_flag:
                break

        # 模块模式下不执行main
        if module_mode:
            return result

        # 查找并执行main函数
        if 'main' in self.functions:
            print("🚀 执行main函数:")
            result = self.execute_function(self.functions['main'], [])

        return result

    def execute_statement(self, stmt: ASTNode) -> RuntimeValue:
        """执行语句"""
        self._track_node(stmt)
        try:
            return self._execute_statement_safe(stmt)
        except (NameError, ValueError, TypeError, RuntimeError, IndexError, KeyError, ZeroDivisionError) as e:
            msg = str(e)
            # 防止多层嵌套调用重复包装（如 main→bad() 在每层 execute_statement 都触发）
            if '   at line' in msg:
                raise
            # KeyError 特殊处理：Python 的 KeyError.__str__ 使用 repr() 显示
            # 导致错误信息中引号被双重转义，统一转为 RuntimeError
            if isinstance(e, KeyError):
                raise RuntimeError(self._error_context(msg))
            raise type(e)(self._error_context(msg))

    def _execute_statement_safe(self, stmt: ASTNode) -> RuntimeValue:
        """执行语句（内部，不含错误包装）"""
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
        elif isinstance(stmt, Expression):
            return self.evaluate_expression(stmt)
        elif isinstance(stmt, ClassStmt):
            return self.execute_class_decl(stmt)
        else:
            raise RuntimeError(f"未知语句类型: {type(stmt).__name__}")

    def execute_variable_decl(self, stmt: VariableDecl) -> RuntimeValue:
        """执行变量声明"""
        value = self.evaluate_expression(stmt.value) if stmt.value else self.get_default_value(stmt.var_type)

        # ? 操作符提前返回时不校验类型（错误值正在传播）
        if self.return_flag:
            return value

        # 类型推断:当未标注类型时,从初始值推断
        effective_type = stmt.var_type
        if (effective_type is None or effective_type == "Any") and stmt.value:
            effective_type = self._infer_type_from_value(value)

        # 运行时类型校验
        if effective_type and effective_type != "Any":
            self._check_type(value, effective_type, f"变量 '{stmt.name}'")

        self.current_scope.declare(stmt.name, value, stmt.is_const)
        return value

    def _infer_type_from_value(self, value: RuntimeValue) -> str:
        """从运行时值推断类型名"""
        t = value.get_type()
        mapping = {
            IntType: "Int", FloatType: "Float", StringType: "String",
            BoolType: "Bool", NoneType: "None", ListType: "List", DictType: "Dict"
        }
        for cls, name in mapping.items():
            if isinstance(t, cls):
                return name
        return "Any"

    def _unify_types(self, decl_str: str, actual_type, bindings: Dict[str, str]):
        """统一类型标注与运行时的 Type 对象，填充类型参数绑定

        decl_str: 声明中的类型标注字符串，如 "List<T>" 或 "T"
        actual_type: 实际的 Type 对象，如 ListType(IntType())
        bindings: 类型参数 → 具体类型名的映射
        """
        if not decl_str:
            return

        # 情况1: decl_str 本身就是一个类型参数名
        if decl_str in bindings or self._is_type_param(decl_str):
            bindings[decl_str] = actual_type.name
            return

        # 情况2: decl_str 是 List<T> 对应 actual 是 ListType(X)
        if decl_str.startswith("List<") and decl_str.endswith(">"):
            inner = decl_str[5:-1]   # "T"
            if isinstance(actual_type, ListType):
                self._unify_types(inner, actual_type.element_type, bindings)
            return

        # 情况3: decl_str 是 Dict<K,V>
        if decl_str.startswith("Dict<") and decl_str.endswith(">"):
            inner = decl_str[5:-1]
            parts = [p.strip() for p in inner.split(",")]
            if isinstance(actual_type, DictType) and len(parts) == 2:
                self._unify_types(parts[0], actual_type.key_type, bindings)
                self._unify_types(parts[1], actual_type.value_type, bindings)
            return

    def _is_type_param(self, name: str) -> bool:
        """判断一个类型名是否是泛型参数（首字母大写单字母）= 类型变量"""
        return bool(name) and len(name) == 1 and name[0].isupper()

    def _subst_type(self, type_name: str, bindings: Dict[str, str]) -> str:
        """将类型标注中的泛型参数替换为推断出的具体类型
        identity<T>(x: T) -> T  +  T=Int → Int
        """
        if not type_name or not bindings:
            return type_name
        # 词法化: Dict<T, Int> → ["Dict<", "T", ", ", "Int", ">"]
        result = type_name
        for tp, concrete in bindings.items():
            # 只替换单词级别的 T，避免 "T" 出现在 "Tuple" 中
            import re
            pattern = r'(?<![a-zA-Z0-9_])' + re.escape(tp) + r'(?![a-zA-Z0-9_])'
            result = re.sub(pattern, concrete, result)
        return result

    def _type_from_name(self, type_name: str) -> Optional[Type]:
        """类型名 → Type 实例"""
        if type_name == "Int":
            return IntType()
        elif type_name == "Float":
            return FloatType()
        elif type_name == "String":
            return StringType()
        elif type_name == "Bool":
            return BoolType()
        elif type_name == "None":
            return NoneType()
        elif type_name == "Dict" or type_name.startswith("Dict["):
            # Dict[K, V] - 宽松处理,默认 String→Int
            if "[" in type_name:
                inner = type_name[type_name.index("[")+1:type_name.index("]")]
                parts = [p.strip() for p in inner.split(",")]
                kt = self._type_from_name(parts[0]) if len(parts) >= 1 else StringType()
                vt = self._type_from_name(parts[1]) if len(parts) >= 2 else IntType()
                return DictType(kt, vt)
            return DictType(StringType(), IntType())
        elif type_name == "List" or type_name.startswith("List["):
            # List[Int] / List[Float] 等
            inner = "Int"
            if "[" in type_name:
                inner = type_name[type_name.index("[")+1:type_name.index("]")]
            return ListType(self._type_from_name(inner))
        return None

    def _check_type(self, value: RuntimeValue, type_name: str, context: str = "") -> None:
        """运行时类型校验 - 不匹配时抛出 TypeError"""
        if type_name == "Any":
            return
        expected = self._type_from_name(type_name)
        if expected is None:
            return  # 未知类型,宽容处理
        if not expected.can_assign_from(value.get_type()):
            # 基类名宽松匹配:裸类型名(如 Dict)允许匹配任何同族泛型(如 Dict<String, Int>)
            # 避免类型推断后精确校验因泛型参数不一致而误报
            if not value.get_type().name.startswith(type_name):
                actual = value.get_type().name
                msg = f"类型不匹配{context}: 期望 {type_name},但得到 {actual}"
                raise TypeError(msg)

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
                    self.current_scope = old_scope
                    break
                elif self.continue_flag:
                    self.continue_flag = False
                    break

            self.current_scope = old_scope

            if self.break_flag:
                self.break_flag = False
                break

        return result

    def execute_for(self, stmt: ForStmt) -> RuntimeValue:
        """执行for循环"""
        result = IntValue(0)

        # 获取可迭代对象
        iterable = self.evaluate_expression(stmt.iterable)

        if not isinstance(iterable, ListValue):
            raise TypeError(f"for循环期望列表,得到 {iterable.type}")

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
                    break
                elif self.continue_flag:
                    self.continue_flag = False
                    break

            self.current_scope = old_scope

            if self.break_flag:
                self.break_flag = False
                break

        return result

    def execute_match(self, expr: 'MatchExpr', context: dict = None) -> RuntimeValue:
        """执行 match 表达式"""
        match_value = self.evaluate_expression(expr.value, context)

        for case in expr.cases:
            bindings = {}
            if self._pattern_match(case.pattern, match_value, bindings):
                if case.guard:
                    # 守卫条件:在绑定变量的作用域中求值
                    old_scope = self.current_scope
                    self.current_scope = self.current_scope.enter()
                    try:
                        for name, val in bindings.items():
                            self.current_scope.declare(name, val)
                        guard_result = self.evaluate_expression(case.guard, context)
                        if not guard_result.to_bool():
                            self.current_scope = old_scope
                            continue
                    except Exception:
                        self.current_scope = old_scope
                        raise
                    self.current_scope = old_scope

                # 执行体
                old_scope = self.current_scope
                self.current_scope = self.current_scope.enter()
                result = IntValue(0)
                try:
                    for name, val in bindings.items():
                        self.current_scope.declare(name, val)

                    if case.body:
                        result = self.evaluate_expression(case.body, context)
                    else:
                        for stmt in case.body_block:
                            result = self.execute_statement(stmt)
                            if self.return_flag or self.break_flag:
                                break
                finally:
                    self.current_scope = old_scope
                return result

        raise MatchError(f"match 表达式未覆盖所有情况: {match_value}", expr.line)

    def _pattern_match(self, pattern, value: RuntimeValue, bindings: dict) -> bool:
        """尝试匹配一个模式,成功时将绑定写入 bindings dict"""
        if isinstance(pattern, WildcardPattern):
            return True

        if isinstance(pattern, LiteralPattern):
            if isinstance(value, NoneValue):
                return pattern.value is None
            if isinstance(value, BoolValue) and isinstance(pattern.value, bool):
                return value.value == pattern.value
            if isinstance(value, IntValue) and isinstance(pattern.value, int):
                return value.value == pattern.value
            if isinstance(value, FloatValue) and isinstance(pattern.value, (int, float)):
                return value.value == pattern.value
            if isinstance(value, StringValue) and isinstance(pattern.value, str):
                return value.value == pattern.value
            return False

        if isinstance(pattern, VariablePattern):
            bindings[pattern.name] = value
            return True

        if isinstance(pattern, OrPattern):
            for sub in pattern.patterns:
                if self._pattern_match(sub, value, bindings):
                    return True
            return False

        if isinstance(pattern, ConstructorPattern):
            if not isinstance(value, ResultValue):
                return False
            if pattern.constructor == 'Ok' and value.is_ok:
                if pattern.inner:
                    return self._pattern_match(pattern.inner, value.ok_value, bindings)
                return True
            if pattern.constructor == 'Err' and not value.is_ok:
                if pattern.inner:
                    return self._pattern_match(pattern.inner, value.err_value, bindings)
                return True
            return False

        raise MatchError(f"不支持的匹配模式: {type(pattern).__name__}")

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

        # 检查模块是否已加载(缓存)
        if module_name in self.modules:
            module_scope = self.modules[module_name]
        else:
            # 查找模块文件(支持点号分隔,如 std.math → std/math.intent)
            module_file = self._find_module_file(module_name)
            if not module_file:
                print(f"[警告] 找不到模块: {module_name}")
                return IntValue(0)

            # 加载模块(module_mode=True,不执行main)
            try:
                with open(module_file, 'r', encoding='utf-8') as f:
                    code = f.read()

                # 保存当前状态
                old_scope = self.current_scope
                old_functions = dict(self.functions)

                # 创建模块作用域
                module_scope = Scope(parent=self.global_scope)
                self.current_scope = module_scope

                # 解析并执行模块代码(module_mode=True)
                lexer = Lexer(code, module_file)
                tokens = lexer.tokenize()
                parser = Parser(tokens, code)
                ast = parser.parse()
                self.execute_program(ast, module_mode=True)

                # 把模块内注册的函数也存入模块作用域（包装为 FunctionValue 支持模块内互调）
                for fname, fdef in self.functions.items():
                    if fname not in old_functions:
                        fv = FunctionValue(fdef, module_scope)
                        module_scope.declare(fname, fv, False, allow_redefine=True)

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

        # 将模块中的所有符号导入当前作用域
        module_scope_obj = self.modules[module_name]

        # ── 层级模块注册 (如 std.math → 注册 "std", "std" 内注册 "math") ──
        alias_parts = alias.split('.')
        # 构建嵌套：从最外层向内逐层
        outer_name = alias_parts[0]          # "std"
        # 如果最外层还不存在，创建它
        if not self.current_scope.has(outer_name):
            outer_scope = Scope(parent=self.global_scope)
            outer_val = RuntimeValue(StringType(), outer_name)
            outer_val.module_ref = outer_scope
            self.current_scope.declare(outer_name, outer_val, False)
        else:
            outer_val = self.current_scope.get(outer_name)
            outer_scope = getattr(outer_val, 'module_ref', None)
            if outer_scope is None or not isinstance(outer_scope, Scope):
                outer_scope = Scope(parent=self.global_scope)
                outer_val.module_ref = outer_scope
        # 逐层挂载
        cursor_scope = outer_scope
        cursor_val = outer_val
        for i in range(1, len(alias_parts)):
            part = alias_parts[i]
            prefix = '.'.join(alias_parts[:i+1])
            if part not in cursor_scope.symbols:
                inner_scope = Scope(parent=self.global_scope)
                inner_val = RuntimeValue(StringType(), prefix)
                inner_val.module_ref = inner_scope
                cursor_scope.declare(part, inner_val, False, allow_redefine=True)
            else:
                existing = cursor_scope.symbols[part]
                if hasattr(existing, 'module_ref') and isinstance(existing.module_ref, Scope):
                    inner_scope = existing.module_ref
                else:
                    inner_scope = Scope(parent=self.global_scope)
                    existing.module_ref = inner_scope
                inner_val = existing
            cursor_scope = inner_scope
            cursor_val = inner_val
        # 把模块实际符号挂到最内层（FunctionDef 包成 FunctionValue 以支持高阶函数传参）
        for name, value in module_scope_obj.symbols.items():
            if hasattr(value, 'body'):
                # 函数: 包成 FunctionValue（闭包=模块作用域）
                fv = FunctionValue(value, module_scope_obj)
                cursor_scope.declare(name, fv, False, allow_redefine=True)
                full_name = f"{alias}.{name}"
                self.functions[full_name] = fv
            else:
                cursor_scope.declare(name, value, False, allow_redefine=True)

        return IntValue(0)

    def _find_module_file(self, module_name: str) -> Optional[str]:
        """查找模块文件,支持点号分隔(如 std.math → std/math.intent)"""
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

    def execute_function(self, func, args: List[RuntimeValue],
                          closure_scope: Optional[Scope] = None) -> RuntimeValue:
        """执行函数 - 支持闭包和泛型类型推断

        如果 func 是 FunctionValue,自动提取其闭包作用域。
        闭包作用域作为新作用域的 parent,而非当前的 current_scope。
        泛型参数从实参类型推断,代入形参注解和返回类型注解。
        """
        # 提取 FunctionValue 的闭包
        if isinstance(func, FunctionValue):
            func_def = func.func_def
            if closure_scope is None:
                closure_scope = func.closure
        else:
            func_def = func

        # LambdaExpr 没有 name 属性，用特殊名称
        func_name = getattr(func_def, 'name', '<lambda>')
        print(f"📋 执行函数: {func_name}")

        # ── 泛型类型推断 ──
        type_bindings: Dict[str, str] = {}
        type_params = getattr(func_def, 'type_params', [])
        if type_params:
            # 对每个参数：统一声明的类型标注与实际类型，解出类型参数的绑定
            for (param_name, decl_type), arg_value in zip(func_def.params, args):
                if decl_type:
                    self._unify_types(decl_type, arg_value.get_type(), type_bindings)
            # 未绑定类型参数的 fallback
            for tp in type_params:
                if tp not in type_bindings:
                    type_bindings[tp] = "Any"
            # 代入形参标注和返回类型
            subst_params = [(name, self._subst_type(pt, type_bindings))
                            for name, pt in func_def.params]
            subst_return = self._subst_type(func_def.return_type, type_bindings)
        else:
            subst_params = func_def.params
            subst_return = func_def.return_type

        # 保存旧的变量状态,用闭包作用域作为父作用域
        old_scope = self.current_scope
        parent = closure_scope if closure_scope is not None else old_scope
        self.current_scope = Scope(parent=parent)

        # 设置参数(在验证契约之前,使参数名可用于 requires/ensures)
        # 同时进行运行时类型校验(使用泛型代入后的类型)
        for (param_name, param_type), arg_value in zip(subst_params, args):
            if param_type and param_type != "Any":
                self._check_type(arg_value, param_type, f"@ 参数 '{param_name}' (函数 {func_name})")
            self.current_scope.declare(param_name, arg_value.copy(), False)

        # 准备验证上下文(包含参数绑定)
        context = {
            'args': args,
            'variables': {name: val for name, val in self.current_scope.symbols.items()},
            'params': {p[0]: v.copy() for p, v in zip(func_def.params, args)}
        }

        # 验证前置条件
        func_requires = getattr(func_def, 'requires', [])
        if func_requires:
            print("⚖️  验证前置条件...")
            if not self.contract_verifier.verify_requires(func_requires, context):
                print("❌ 前置条件验证失败,停止执行")
                self.current_scope = old_scope
                return IntValue(1)

        # 执行函数体

        # 执行函数体
        result = IntValue(0)
        for stmt in func_def.body:
            result = self.execute_statement(stmt)
            if self.return_flag:
                self.return_flag = False
                break

        # 验证后置条件
        func_ensures = getattr(func_def, 'ensures', [])
        if func_ensures:
            print("⚖️  验证后置条件...")
            # 将 result 放入全局作用域,使 ensures 表达式的 result 可解析
            self.global_scope.symbols['result'] = result
            if not self.contract_verifier.verify_ensures(func_ensures, result, context):
                print("⚠️  后置条件验证失败")
            del self.global_scope.symbols['result']

        # 恢复作用域
        self.current_scope = old_scope

        # 校验返回类型(使用泛型代入后的返回类型)
        if subst_return and subst_return != "Any":
            self._check_type(result, subst_return, f"@ 返回值 (函数 {func_name})")

        return result

    def execute_class_decl(self, stmt: 'ClassStmt') -> RuntimeValue:
        """执行类声明 — 创建 ClassValue 并注册到作用域"""
        # 解析父类
        superclass = None
        if stmt.superclass:
            sv = self.current_scope.get(stmt.superclass)
            if sv and isinstance(sv, ClassValue):
                superclass = sv
            else:
                raise NameError(f"父类 {stmt.superclass} 未找到或不是类")
        
        # 创建方法 — 每个方法包装为 FunctionValue
        methods = {}
        for method_def in stmt.methods:
            fv = FunctionValue(method_def, self.current_scope)
            methods[method_def.name] = fv
        
        # 创建 ClassValue
        class_value = ClassValue(stmt.name, methods, superclass)
        
        # 注册到当前作用域
        self.current_scope.declare(stmt.name, class_value, False)
        
        return class_value
    
    def _execute_method(self, method: FunctionValue, instance: 'InstanceValue', args: List[RuntimeValue]):
        """在实例上下文中执行方法"""
        func_def = method.func_def
        closure = method.closure
        
        # 创建方法作用域
        method_scope = Scope(parent=closure)
        
        # 绑定参数
        for i, param in enumerate(func_def.params):
            param_name = param[0] if isinstance(param, tuple) else param
            if i < len(args):
                method_scope.declare(param_name, args[i], False)
            else:
                # 默认值
                method_scope.declare(param_name, self.get_default_value(None), False)
        
        # 注入 this
        method_scope.declare('this', instance, True)
        
        # 保存并切换作用域 + return 状态
        old_scope = self.current_scope
        old_return_flag = self.return_flag
        old_return_value = self.return_value
        self.current_scope = method_scope
        
        # 执行函数体
        self.return_flag = False
        result = IntValue(0)
        try:
            for stmt in func_def.body:
                result = self.execute_statement(stmt)
                if self.return_flag:
                    break
        finally:
            self.current_scope = old_scope
            self.return_flag = old_return_flag
            self.return_value = old_return_value
        
        return result

    def _get_member_access_instance(self, member_access):
        """从 MemberAccess 链中获取根实例（如 p.distance → p = InstanceValue）"""
        current = member_access
        while isinstance(current, MemberAccess):
            current = current.obj
        if isinstance(current, Variable):
            val = self.current_scope.get(current.name)
            if isinstance(val, InstanceValue):
                return val
        elif isinstance(current, ThisExpr):
            return self.current_scope.get('this')
        return self.evaluate_expression(current)

    def evaluate_expression(self, expr: Expression, context: Optional[Dict] = None) -> RuntimeValue:
        """评估表达式"""
        self._track_node(expr)
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
                return NoneValue()
            else:
                return RuntimeValue(IntType(), expr.value)

        elif isinstance(expr, Variable):
            # 先从作用域查找(变量可遮蔽内置函数名)
            expr_id = id(expr)
            if expr_id in self.locals:
                depth = self.locals[expr_id]
                try:
                    return self.current_scope.get_at(depth, expr.name)
                except KeyError:
                    pass  # 变量未找到,继续检查内置函数
            else:
                # 链式查找当前作用域(含祖先链)
                try:
                    return self.current_scope.get(expr.name)
                except NameError:
                    pass  # 继续检查内置函数

            # 变量作用域中未找到,检查内置函数
            if expr.name in self.builtins:
                return RuntimeValue(IntType(), expr.name)

            raise NameError(f"未定义的变量 '{expr.name}'")

        elif isinstance(expr, MemberAccess):
            # 计算左侧对象的值
            obj_value = self.evaluate_expression(expr.obj, context)

            # InstanceValue 属性访问 (this.field / obj.field) — 优先于模块查找
            if isinstance(obj_value, InstanceValue):
                member_val = obj_value.get(expr.member)
                if member_val is not None:
                    return member_val
                raise NameError(f"实例没有属性 '{expr.member}'")

            # 如果obj_value是模块引用,获取模块导出
            if hasattr(obj_value, 'module_ref'):
                module = obj_value.module_ref
                # 检查是否是Module对象
                if hasattr(module, 'get_export'):
                    member_val = module.get_export(expr.member)
                    if member_val is not None:
                        return member_val
                    raise NameError(f"模块 '{obj_value.value}' 没有导出成员 '{expr.member}'")
                elif hasattr(module, 'symbols'):
                    # 是Scope对象,从symbols中获取
                    if expr.member in module.symbols:
                        return module.symbols[expr.member]
                    raise NameError(f"模块 '{obj_value.value}' 没有导出成员 '{expr.member}'")

            # 如果是普通对象,尝试作为属性访问
            # 对于简单的实现,我们直接在作用域中查找 module.member
            full_name = f"{obj_value.value}.{expr.member}" if hasattr(obj_value, 'value') else f"{obj_value}.{expr.member}"
            try:
                result = self.current_scope.get(full_name)
                if result is not None:
                    return result
            except NameError:
                pass

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

        elif isinstance(expr, SubscriptExpr):
            obj = self.evaluate_expression(expr.obj, context)
            index = self.evaluate_expression(expr.index, context)
            if isinstance(obj, ListValue):
                return obj.get(index.value)
            elif isinstance(obj, DictValue):
                val = obj.get(index.value)
                if val is None:
                    raise KeyError(f"字典中没有键 '{index.value}'")
                return val
            elif isinstance(obj, StringValue):
                idx = index.value
                if idx < 0 or idx >= len(obj.value):
                    raise IndexError(f"字符串索引 {idx} 越界")
                return StringValue(obj.value[idx])
            else:
                raise TypeError(f"不支持对 {obj.get_type()} 类型使用下标访问 []")

        elif isinstance(expr, PipeExpr):
            # 管道: left |> right → right(left)
            left_val = self.evaluate_expression(expr.left, context)

            # 右侧如果是函数名,直接查找函数(不经过变量求值)
            if isinstance(expr.right, Variable):
                fname = expr.right.name
                if fname in self.builtins:
                    return self.builtins[fname]([left_val])
                if fname in self.functions:
                    return self.execute_function(self.functions[fname], [left_val])
                raise NameError(f"管道右侧未定义的函数: {fname}")

            right_val = self.evaluate_expression(expr.right, context)

            if isinstance(right_val, FunctionValue):
                return self.execute_function(right_val, [left_val])

            if isinstance(right_val.value, str):
                fname = right_val.value
                if fname in self.builtins:
                    return self.builtins[fname]([left_val])
                if fname in self.functions:
                    return self.execute_function(self.functions[fname], [left_val])

            raise TypeError(f"管道右侧必须是可调用对象")

        elif isinstance(expr, IfExpr):
            # if 表达式:求值条件,选择分支,返回结果
            cond_val = self.evaluate_expression(expr.condition, context)
            body = expr.then_body if cond_val.to_bool() else expr.else_body

            old_scope = self.current_scope
            self.current_scope = self.current_scope.enter()
            result = IntValue(0)
            for stmt in body:
                result = self.execute_statement(stmt)
                if self.return_flag or self.break_flag or self.continue_flag:
                    break
            self.current_scope = old_scope
            return result

        elif isinstance(expr, MatchExpr):
            return self.execute_match(expr, context)

        elif isinstance(expr, TryExpr):
            # ?,Err 传播: expr ?
            result = self.evaluate_expression(expr.expr, context)
            if isinstance(result, ResultValue) and not result.is_ok:
                # Err → 提前 return
                self.return_flag = True
                self.return_value = result
                return result
            # Ok → 解包内部值
            if isinstance(result, ResultValue):
                return result.ok_value
            # 非 Result 类型 → 透传
            return result

        elif isinstance(expr, ThisExpr):
            # this 关键字 — 返回当前实例
            this_val = self.current_scope.get('this')
            if this_val is None:
                raise NameError("this 只能在类方法中使用")
            return this_val

        elif isinstance(expr, SetExpr):
            # 属性赋值: obj.field = value
            obj = self.evaluate_expression(expr.obj, context)
            if not isinstance(obj, InstanceValue):
                raise TypeError(f"只能对实例设置属性，但得到 {type(obj).__name__}")
            val = self.evaluate_expression(expr.value, context)
            obj.set(expr.name, val)
            return val

        elif isinstance(expr, BinaryOp):
            left = self.evaluate_expression(expr.left, context)
            right = self.evaluate_expression(expr.right, context)
            return self._binary_op(left, expr.op, right)

        elif isinstance(expr, UnaryOp):
            operand = self.evaluate_expression(expr.operand, context)
            return self._unary_op(expr.op, operand)

        elif isinstance(expr, CallExpr):
            # 提取函数名（兼容多种写法）
            func_name = None
            if isinstance(expr.func, Variable):
                func_name = expr.func.name
            elif isinstance(expr.func, str):
                func_name = expr.func

            # 1️⃣ 检查作用域中的 FunctionValue（lambda/闭包/变量赋值的函数）
            if func_name:
                try:
                    var_val = self.current_scope.get(func_name)
                except NameError:
                    var_val = None
                if var_val is not None:
                    args = [self.evaluate_expression(arg, context) for arg in expr.args]
                    # ClassValue → 类实例化
                    if isinstance(var_val, ClassValue):
                        return var_val.call(self, args)
                    # FunctionValue → 调用 lambda 或闭包
                    if isinstance(var_val, FunctionValue):
                        return self.execute_function(var_val, args)

            # 2️⃣ 处理MemberAccess作为函数的情况 (如 std.math.add(x, y) 或 p.method())
            if isinstance(expr.func, MemberAccess):
                # 先求值 MemberAccess 链，获取实际函数/方法
                func_val = self.evaluate_expression(expr.func, context)
                args = [self.evaluate_expression(arg, context) for arg in expr.args]

                # 检查根对象是 InstanceValue 还是模块 → 不同调度方式
                instance = self._get_member_access_instance(expr.func)
                is_instance_call = isinstance(instance, InstanceValue)

                # FunctionDef → 模块函数（兼容旧格式）
                if hasattr(func_val, 'body'):
                    return self.execute_function(func_val, args)
                # FunctionValue → 实例方法=走 _execute_method, 模块函数=走 execute_function
                if isinstance(func_val, FunctionValue):
                    if is_instance_call:
                        return self._execute_method(func_val, instance, args)
                    return self.execute_function(func_val, args)

                raise NameError(f"无法调用 {func_val}")

            # 检查是否是内置函数
            if func_name and func_name in self.builtins:
                args = [self.evaluate_expression(arg, context) for arg in expr.args]
                return self.builtins[func_name](args)

            # 检查是否是用户定义函数
            if func_name and func_name in self.functions:
                func = self.functions[func_name]
                args = [self.evaluate_expression(arg, context) for arg in expr.args]
                return self.execute_function(func, args)

            # 回退到旧的 expr.func 字符串比较（向后兼容）
            if isinstance(expr.func, str):
                if expr.func in self.builtins:
                    args = [self.evaluate_expression(arg, context) for arg in expr.args]
                    return self.builtins[expr.func](args)
                if expr.func in self.functions:
                    func = self.functions[expr.func]
                    args = [self.evaluate_expression(arg, context) for arg in expr.args]
                    return self.execute_function(func, args)

            raise NameError(f"未定义的函数: {func_name or expr.func}")

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

        elif isinstance(expr, DictExpr):
            entries = {}
            for key_expr, value_expr in expr.entries:
                key_val = self.evaluate_expression(key_expr, context)
                val_val = self.evaluate_expression(value_expr, context)
                # 用字符串/数值作为键
                key = key_val.value
                entries[key] = val_val
            # 字典字面量宽松类型:键=String,值=不限制
            if not entries:
                return DictValue({}, StringType(), IntType())
            # 用首个条目的类型作为默认类型标注
            first_key = next(iter(entries.keys()))
            first_val = entries[first_key]
            kt = StringType() if isinstance(first_key, str) else IntType()
            return DictValue(entries, kt, first_val.get_type() if entries else IntType())

        elif isinstance(expr, LambdaExpr):
            # 创建闭包 - 捕获当前作用域
            return FunctionValue(expr, self.current_scope)

        else:
            raise RuntimeError(f"不支持的表达式类型: {type(expr).__name__}")

    def _binary_op(self, left: RuntimeValue, op: str, right: RuntimeValue) -> RuntimeValue:
        """执行二元运算"""
        # 字符串拼接
        if op == '+' and isinstance(left, StringValue) and isinstance(right, StringValue):
            return StringValue(left.value + right.value)
        # 字符串 + 任意类型 → 字符串拼接
        if op == '+' and isinstance(left, StringValue):
            right_str = right.value if isinstance(right, StringValue) else str(right.value)
            return StringValue(left.value + right_str)
        if op == '+' and isinstance(right, StringValue):
            left_str = left.value if isinstance(left, StringValue) else str(left.value)
            return StringValue(left_str + right.value)

        # 列表拼接
        if op == '+' and isinstance(left, ListValue) and isinstance(right, ListValue):
            return ListValue(left.value + right.value,
                           element_type=left.type.element_type if left.type.element_type else right.type.element_type)
        # 列表重复
        if op == '*' and isinstance(left, ListValue) and isinstance(right, IntValue):
            return ListValue(left.value * int(right.value), element_type=left.type.element_type)
        if op == '*' and isinstance(left, IntValue) and isinstance(right, ListValue):
            return ListValue(int(left.value) * right.value, element_type=right.type.element_type)

        # 字符串重复
        if op == '*' and isinstance(left, StringValue) and isinstance(right, IntValue):
            return StringValue(left.value * int(right.value))
        if op == '*' and isinstance(left, IntValue) and isinstance(right, StringValue):
            return StringValue(int(left.value) * right.value)

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

            # 字符串比较
            if isinstance(left, StringValue) and isinstance(right, StringValue):
                if op == '==':
                    return BoolValue(left.value == right.value)
                elif op == '!=':
                    return BoolValue(left.value != right.value)
                elif op == '<':
                    return BoolValue(left.value < right.value)
                elif op == '>':
                    return BoolValue(left.value > right.value)
                elif op == '<=':
                    return BoolValue(left.value <= right.value)
                elif op == '>=':
                    return BoolValue(left.value >= right.value)

            # None 比较
            if isinstance(left, NoneValue) and isinstance(right, NoneValue):
                if op == '==':
                    return BoolValue(True)
                elif op == '!=':
                    return BoolValue(False)
            elif isinstance(left, NoneValue) or isinstance(right, NoneValue):
                if op == '==':
                    return BoolValue(False)
                elif op == '!=':
                    return BoolValue(True)

        # 逻辑运算
        elif op == 'and':
            return BoolValue(left.to_bool() and right.to_bool())
        elif op == 'or':
            return BoolValue(left.to_bool() or right.to_bool())

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
║  输入代码执行,.help查看命令,.exit退出               ║
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
    print("心学为体,禅道为翼,马哲为用");

    let x = 10;
    let y = 20;
    let sum = x + y;

    print("计算结果:");
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
            parser = Parser(tokens, code)
            ast = parser.parse()

            # 如有解析错误,报告但不阻止执行(尽可能多的正确部分仍可执行)
            if parser.errors:
                print(f"⚠️  发现 {len(parser.errors)} 个语法错误:")
                for err in parser.errors:
                    print(f"    • {err}")

            # 设置源码用于错误上下文
            self.interpreter._set_source(code)

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
        # 如果是命令,处理命令
        if line.startswith('.'):
            return self.handle_command(line)

        # 添加到历史
        self.history.append(line)

        # 尝试作为表达式求值
        try:
            # 如果是表达式,自动包装在print中
            if not any(line.strip().startswith(keyword) for keyword in
                      ['def ', 'let ', 'var ', 'const ', 'if ', 'for ', 'while ']):
                # 可能是表达式,尝试求值
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
        """处理REPL命令,返回True表示继续,False表示退出"""
        cmd = command.strip().split()

        if not cmd:
            return True

        if cmd[0] == '.exit' or cmd[0] == '.quit':
            print("再见!🧘")
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
    print("心学为体,禅道为翼,马哲为用");

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
        # 设置当前文件目录,用于模块搜索
        file_dir = os.path.dirname(os.path.abspath(args.filename))
        interpreter.add_module_search_path(file_dir)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.filename}")
        print("提示: 请确保文件存在,或使用 --demo 运行演示程序")
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
            parser = Parser(tokens, code)
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
        parser = Parser(tokens, code)
        ast = parser.parse()

        # 如有解析错误,报告但不阻止执行(尽可能多的正确部分仍可执行)
        if parser.errors:
            print(f"⚠️  发现 {len(parser.errors)} 个语法错误(已跳过):")
            for err in parser.errors:
                print(f"    • {err}")
            print()

        result = interpreter.execute_program(ast)

        if parser.errors:
            print(f"\n⚠️  程序部分执行成功({len(parser.errors)} 个错误已跳过)")
        else:
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