#!/usr/bin/env python3
"""
Intent语言完整解释器 v1.2
融合:心学为体,禅道为翼,马哲为用
目标:让代码清晰地表达意图
"""

from __future__ import annotations

import sys
import os
import re
import time
import threading
import queue
import ctypes

# 提升 Python 递归限制（Intent 递归函数需要更深的调用栈）
sys.setrecursionlimit(100000)
import json
import math
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Tuple, Union, Callable
from enum import Enum
from collections import ChainMap, deque

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
        if sys.platform == "win32" and sys.stderr.isatty():
            print("提示: 可以安装 pyreadline3 以获得更好的命令行体验", file=sys.stderr)
            print("安装命令: pip install pyreadline3", file=sys.stderr)

# ==================== 常量定义 ====================
VERSION = "2.21.0"
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
            except Exception:
                pass

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
    COMMENT = "COMMENT"

@dataclass
class Token:
    """词法单元"""
    type: TokenType
    value: str
    line: int
    column: int
    filename: str = ""
    is_fstring: bool = False   # P2.2: f"..." 前缀标记(formatter 还原前缀)

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
        'class', 'this', 'mut', 'fn',  # 类系统 + 匿名函数
        'try', 'catch', 'finally', 'defer',  # 错误处理 + 延迟执行
        'raise',  # 异常链(EX1): raise <错误值> from <原因>
        'with',  # 块级资源管理(P1.1)
        'export',  # 显式模块导出(P2.1)
        'assert',  # 断言
        'enum',  # 枚举
        'yield',  # 生成器
        'spawn', 'scope',  # 结构化并发(CC1): 派生任务 + 作用域退出自动 join
    }

    # 内置类型名 - 不是关键字,只是预定义的类型标识符
    BUILTIN_TYPES = {'Int', 'Float', 'String', 'Bool', 'List', 'Dict'}

    SYMBOLS = {
        '(', ')', '{', '}', '[', ']', ',', ':', ';', '=', '.', '->', '=>', '@',
        '+', '-', '*', '/', '%', '**', '//', '==', '!=', '<', '>', '<=', '>=',
        '!', '&&', '||', '&', '|', '^', '~', '<<', '>>', ':=', '++', '--',
        '+=', '-=', '*=', '/=', '%=', '**=', '//=', '&=', '|=', '^=', '<<=', '>>=',
        '|>',  # 管道操作符
        '<-'  # 通道发送(CC2): ch <- v / <- ch
    }

    SINGLE_SYMBOLS = set('(){}[],:;.=+-*/%<>!&|^~@')

    def __init__(self, code: str, filename: str = "", keep_comments: bool = False):
        self.code = code
        self.filename = filename
        self.keep_comments = keep_comments  # formatter 专用: 注释也产 token
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

    def read_comment(self):
        """读取注释并产 COMMENT token(formatter 专用)"""
        start_line, start_col = self.line, self.column
        start_pos = self.pos
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '*':
            self.advance(2)
            while (self.current_char() and
                   not (self.current_char() == '*' and self.peek_char() == '/')):
                self.advance()
            if self.current_char() == '*':
                self.advance(2)
        value = self.code[start_pos:self.pos].rstrip()
        self.tokens.append(Token(TokenType.COMMENT, value, start_line, start_col, self.filename))

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
        """读取字符串字面量 — 支持三引号多行字符串(P1.2)

        S2b: 插值区 ${...} 内引号不终止字符串 — "${d["k"]}" 合法
        (嵌套引号; 插值区内再遇引号按子字符串跳过, 括号深度计数)。
        """
        quote = self.current_char()
        # 三引号多行字符串: """...""" 或 '''...'''
        if self.code[self.pos:self.pos + 3] == quote * 3:
            self.advance(3)  # 跳过开头的三引号
            start_pos = self.pos
            interp_depth = 0
            while self.current_char():
                if interp_depth == 0 and self.code[self.pos:self.pos + 3] == quote * 3:
                    break
                c = self.current_char()
                if c == '\\':  # 处理转义字符
                    self.advance()
                    self.advance()
                    continue
                if c == '$' and self.peek_char() == '{':
                    interp_depth += 1
                    self.advance()
                    self.advance()
                    continue
                if c == '{':
                    interp_depth += 1
                elif c == '}' and interp_depth > 0:
                    interp_depth -= 1
                elif c in '"\'' and interp_depth > 0:
                    self._skip_nested_string(c)
                    continue
                self.advance()
            if not self.current_char():
                raise SyntaxError(f"未结束的多行字符串,行 {self.line}")
            value = self.code[start_pos:self.pos]
            tok = Token(TokenType.STRING, value, self.line, self.column, self.filename)
            tok.is_fstring = getattr(self, '_pending_fstring', False)
            self._pending_fstring = False
            self.tokens.append(tok)
            self.advance(3)  # 跳过结尾的三引号
            return
        start_pos = self.pos
        self.advance()  # 跳过开头的引号

        interp_depth = 0
        while self.current_char():
            c = self.current_char()
            if c == '\\':  # 处理转义字符
                self.advance()
                self.advance()
                continue
            if interp_depth == 0 and c == quote:
                break
            if c == '$' and self.peek_char() == '{':
                interp_depth += 1
                self.advance()
                self.advance()
                continue
            if c == '{':
                interp_depth += 1
            elif c == '}' and interp_depth > 0:
                interp_depth -= 1
            elif c in '"\'' and interp_depth > 0:
                self._skip_nested_string(c)
                continue
            self.advance()

        if not self.current_char():
            raise SyntaxError(f"未结束的字符串,行 {self.line}")

        value = self.code[start_pos + 1:self.pos]
        tok = Token(TokenType.STRING, value, self.line, self.column, self.filename)
        tok.is_fstring = getattr(self, '_pending_fstring', False)
        self._pending_fstring = False
        self.tokens.append(tok)
        self.advance()  # 跳过结尾的引号

    def _skip_nested_string(self, quote_char: str):
        """插值区内嵌套字符串: 从当前引号跳到收尾引号之后(\\ 转义感知)"""
        self.advance()  # 过开引号
        while self.current_char():
            if self.current_char() == '\\':
                self.advance()
                self.advance()
                continue
            if self.current_char() == quote_char:
                self.advance()  # 过收尾引号
                return
            self.advance()

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

        # f 前缀字符串(P1.2): f"..." 显式插值字符串(行为与普通字符串一致,
        # 插值 ${} 本就内置; f 是意图的显式宣告 — 模板与数据在同一行相见)
        if value == 'f' and self.current_char() == '"':
            self._pending_fstring = True
            self.read_string()
            return

        # 判断是否是关键字
        if value in self.KEYWORDS:
            token_type = TokenType.KEYWORD
        else:
            token_type = TokenType.IDENTIFIER

        self.tokens.append(Token(token_type, value, self.line, self.column, self.filename))

    def read_operator_or_symbol(self):
        """读取运算符或符号"""
        char = self.current_char()

        # S2a: := 海象运算符 — ':' 在单字符快通道里, 提前合并为双字符
        # (:: 双冒号不受影响: 后字符是 ':' 不是 '=')
        if char == ':' and self.peek_char() == '=':
            self.tokens.append(Token(TokenType.OPERATOR, ':=', self.line, self.column, self.filename))
            self.advance(2)
            return

        # 先检查是否是标点符号
        if char in '(){}[],:;.?@' :
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

            # 注释: 默认跳过; keep_comments 模式产 COMMENT token(formatter 保留注释)
            if (self.current_char() == '#' or
                (self.current_char() == '/' and self.peek_char() in ['/', '*'])):
                if self.keep_comments:
                    self.read_comment()
                else:
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
class Decorator(ASTNode):
    """X1: 装饰器声明 — @name(裸形态) 或 @name(args)(带参工厂形态)

    裸形态: 装饰器本身即函数值, 应用为 dec(fn)
    带参形态: deco(args...) 先求值出真装饰器, 再应用为 deco(args)(fn)
    is_call 区分 @deco 与 @deco()(零参调用形态, 对齐 Python 语义)
    """
    name: str = ""
    args: List['Expression'] = field(default_factory=list)
    is_call: bool = False

@dataclass
class FunctionDef(ASTNode):
    """函数定义节点"""
    name: str = ""
    type_params: List[str] = field(default_factory=list)  # 泛型参数如 ['T', 'U']
    type_param_constraints: Dict[str, str] = field(default_factory=dict)  # P1.3b: {'T': 'Comparable'}
    params: List[Tuple[str, str, Any]] = field(default_factory=list)  # (参数名, 类型, 默认值表达式或None)
    return_type: Optional[str] = None
    requires: List['Expression'] = field(default_factory=list)  # 前置条件
    ensures: List['Expression'] = field(default_factory=list)   # 后置条件
    body: List[ASTNode] = field(default_factory=list)  # 函数体语句
    is_pure: bool = False
    effects: List[str] = field(default_factory=list)
    is_generator: bool = False  # 包含 yield 则为 True
    is_async: bool = False      # A3a: async def — 调用返回协程(惰性)
    decorators: List['Decorator'] = field(default_factory=list)  # 装饰器声明列表(@name 或 @name(args))

    def get_param_names(self) -> List[str]:
        return [name for name, _, _ in self.params]

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
class MemberAssignment(ASTNode):
    """成员赋值: this.x = value 或 obj.field = value"""
    obj: 'Expression' = None
    member: str = ""
    value: 'Expression' = None
    op: str = "="  # =, +=, -=, 等

@dataclass
class SubscriptAssignment(ASTNode):
    """下标赋值: obj[key] = value 或 obj[key] += value"""
    obj: 'Expression' = None
    index: 'Expression' = None
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
    vars: list = field(default_factory=list)  # 解包变量列表,如 [i, x]
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
class TryStmt(ASTNode):
    """try-catch语句"""
    try_body: List[ASTNode] = field(default_factory=list)
    catch_var: str = ""       # catch (e) 中的变量名
    catch_body: List[ASTNode] = field(default_factory=list)
    finally_body: List[ASTNode] = field(default_factory=list)  # 可选 finally 块
    catch_types: List[str] = field(default_factory=list)  # P1.4: catch e: ContractError(空=全部)

@dataclass
class DeferStmt(ASTNode):
    """defer 语句 — 延迟执行,在作用域退出时执行"""
    body: List[ASTNode] = field(default_factory=list)
    line: int = 0
    column: int = 0

@dataclass
class WithStmt(ASTNode):
    """with 语句 — 块级资源管理(P1.1)

    获取资源与释放资源在同一对花括号内对称出现 —
    defer 的函数级特化: 清理代码在出生时就写好了。
    块退出时, 资源若提供 close 方法则自动调用。
    """
    resource: Optional["Expression"] = None
    var_name: str = ""
    body: List[ASTNode] = field(default_factory=list)
    line: int = 0
    column: int = 0

@dataclass
class TypeAliasStmt(ASTNode):
    """类型别名(P1.3a): type Meters = Float; type Shape = Circle | Square;

    别名是透明的同义词; Union 是「不二法门」的推广 —
    一个东西的多种存在形态, 任一成员合法即通过。
    """
    name: str = ""
    aliased_type: str = ""
    line: int = 0
    column: int = 0

@dataclass
class YieldStmt(ASTNode):
    """yield 语句 — 生成器产出值"""
    value: Optional["Expression"] = None
    from_expr: Optional["Expression"] = None  # P1.5: yield from expr 委派转发
    line: int = 0
    column: int = 0


@dataclass
class RaiseStmt(ASTNode):
    """raise 语句(EX1) — raise <错误值> [from <原因>];

    错误是一等值: raise 把 error() 构造的错误值抛回控制流,
    from Y 把因果链显式化(__cause__) — 不猜, 直接说谁导致谁。
    """
    value: Optional["Expression"] = None
    cause: Optional["Expression"] = None
    line: int = 0
    column: int = 0


@dataclass
class SpawnStmt(ASTNode):
    """spawn 语句(CC1) — spawn <可调用>; / spawn f(args);

    结构化并发: 派生出的任务登记进当前 scope 的任务表,
    scope 退出时统一 join — 没有孤儿线程, 异常不沉没。
    """
    expr: Optional["Expression"] = None
    line: int = 0
    column: int = 0


@dataclass
class ScopeStmt(ASTNode):
    """scope 块(CC1) — scope { ... };

    并发作用域: 块内 spawn 的全部任务, 在块退出时自动 join
    (Zig Go 的结构化并发语义); 任务异常在 join 处重抛。
    """
    body: List[ASTNode] = field(default_factory=list)
    line: int = 0
    column: int = 0

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
class YieldExpr(Expression):
    """S3: yield 表达式 — `let x = yield v` 的递送点(send 的值即本表达式值)"""
    value: Optional["Expression"] = None
    from_expr: Optional["Expression"] = None  # yield from expr 委派转发
    line: int = 0
    column: int = 0


@dataclass
class AwaitExpr(Expression):
    """A3a: await 表达式 — 挂起当前协程, 把内层协程交给驱动线程,
    驱完拿到其结果作为本表达式的值(线程协作式协程背载)"""
    operand: Optional["Expression"] = None
    line: int = 0
    column: int = 0


def _expr_contains_yield(node) -> bool:
    """S3: 递归检测 AST 节点(含表达式子树)中是否有 YieldExpr"""
    if isinstance(node, YieldExpr):
        return True
    if hasattr(node, '__dataclass_fields__'):
        for f in node.__dataclass_fields__:
            if _expr_contains_yield(getattr(node, f, None)):
                return True
    elif isinstance(node, (list, tuple)):
        for item in node:
            if _expr_contains_yield(item):
                return True
    return False

@dataclass
class SendExpr(Expression):
    """ch <- v(CC2) — 通道发送表达式

    把 v 送入通道 ch; 缓冲满则阻塞, 通道已关闭则报错(Go 语义)。
    求值结果为 None — 发送是动作, 不是值。
    """
    chan: Optional["Expression"] = None
    value: Optional["Expression"] = None
    line: int = 0
    column: int = 0

@dataclass
class RecvExpr(Expression):
    """<- ch(CC2) — 通道接收表达式

    从通道 ch 取出下一个值; 空则阻塞等待,
    已关闭且无剩余数据则抛 ChannelClosedError(显式失败, 不返回哑值)。
    """
    chan: Optional["Expression"] = None
    line: int = 0
    column: int = 0

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

    def match_double_colon(self) -> bool:
        """检查是否是 :: (两个连续的 : SYMBOL)"""
        return (self.current_token.type == TokenType.SYMBOL and self.current_token.value == ':' and
                self.peek() is not None and self.peek().type == TokenType.SYMBOL and self.peek().value == ':')

    def consume_double_colon(self):
        """消费 :: (两个连续的 : SYMBOL)"""
        self.advance()  # 第一个 :
        self.advance()  # 第二个 :

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
                # 收集装饰器 (如 @log, @timed, @repeat(3))
                decorators = self._parse_decorators()

                # 解析函数定义
                is_async = self._consume_async()
                if self.match(TokenType.KEYWORD, 'def'):
                    func = self.parse_function_def()
                    if func is not None:
                        func.is_async = is_async
                        func.decorators = decorators
                        program.add_function(func)
                elif decorators:
                    # 装饰器后没有 def → 错误
                    self.error(self.current_token, "装饰器 @ 必须紧跟函数定义")
                    self.synchronize()
                # 解析类声明
                elif self.match(TokenType.KEYWORD, 'class'):
                    cls = self.parse_class_decl()
                    if cls is not None:
                        program.add_statement(cls)
                # 解析语句
                else:
                    stmt = self.parse_statement()
                    if stmt:
                        if isinstance(stmt, FunctionDef):
                            # 带装饰器的函数(parse_statement 处理 @)
                            program.add_function(stmt)
                        else:
                            program.add_statement(stmt)
            except SyntaxError:
                # error() 已记录错误,跳至下一个同步点继续解析
                self.synchronize()

        return program

    def parse_enum_def(self) -> 'EnumDef':
        """解析枚举定义: enum Direction { North, East, South, West }"""
        token = self.expect(TokenType.KEYWORD, 'enum')
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SYMBOL, '{')
        self._skip_newlines()

        variants = []
        if not self.match(TokenType.SYMBOL, '}'):
            first = self.expect(TokenType.IDENTIFIER).value
            variants.append(first)
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                self._skip_newlines()
                if not self.match(TokenType.SYMBOL, '}'):
                    variants.append(self.expect(TokenType.IDENTIFIER).value)
            self._skip_newlines()

        self.expect(TokenType.SYMBOL, '}')
        return EnumDef(name=name, variants=variants)

    def _consume_async(self) -> bool:
        """A3a: 消费 async 软关键字前缀(仅当后随 def 时才吞)

        软关键字: `async` 仍是合法标识符(变量名/函数名可用),
        只在 `async def` 组合里取得关键字地位 — 与 type 别名同思路。
        """
        if (self.match(TokenType.IDENTIFIER, 'async')
                and self.peek() is not None
                and self.peek().type == TokenType.KEYWORD
                and self.peek().value == 'def'):
            self.advance()
            return True
        return False

    def _parse_decorators(self) -> List['Decorator']:
        """X1: 收集装饰器序列 @name / @name(args) — 顶层与语句级共用

        每条装饰器后允许换行(@ 与 def 可分行书写);
        带参形态的参数沿用 parse_call_expr 的括号约定(括号内可换行)。
        """
        decorators = []
        while self.match(TokenType.SYMBOL, '@'):
            at_token = self.current_token
            self.advance()
            dec_name = self.expect(TokenType.IDENTIFIER).value
            dec = Decorator(name=dec_name, line=at_token.line,
                            column=at_token.column)
            # 带参形态: @deco(arg1, arg2)
            if self.match(TokenType.SYMBOL, '('):
                dec.is_call = True
                self.advance()
                if not self.match(TokenType.SYMBOL, ')'):
                    self._skip_newlines()
                    dec.args.append(self.parse_expression())
                    while self.match(TokenType.SYMBOL, ','):
                        self.advance()
                        self._skip_newlines()
                        dec.args.append(self.parse_expression())
                self._skip_newlines()
                self.expect(TokenType.SYMBOL, ')')
            decorators.append(dec)
            # 跳过行尾换行
            while self.match(TokenType.NEWLINE):
                self.advance()
        return decorators

    def parse_function_def(self) -> FunctionDef:
        """解析函数定义"""
        start_token = self.expect(TokenType.KEYWORD, 'def')
        func = FunctionDef(line=start_token.line, column=start_token.column, filename=start_token.filename)

        # 函数名
        func.name = self.expect(TokenType.IDENTIFIER).value

        # 泛型参数: identity<T>(x: T) -> T; 约束(P1.3b): max_of<T: Comparable>
        if self.match(TokenType.OPERATOR, '<'):
            self.advance()
            tp_name = self.expect(TokenType.IDENTIFIER).value
            func.type_params.append(tp_name)
            if self.match(TokenType.SYMBOL, ':'):
                self.advance()
                func.type_param_constraints[tp_name] = self.expect(TokenType.IDENTIFIER).value
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                tp_name = self.expect(TokenType.IDENTIFIER).value
                func.type_params.append(tp_name)
                if self.match(TokenType.SYMBOL, ':'):
                    self.advance()
                    func.type_param_constraints[tp_name] = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.OPERATOR, '>')

        # 参数列表
        self.expect(TokenType.SYMBOL, '(')
        self._skip_newlines()
        func.params = self.parse_parameter_list()
        self._skip_newlines()
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

        # 检测是否是生成器函数（包含 yield 语句）
        func.is_generator = self._has_yield_in_body(func.body)

        return func

    def _has_yield_in_body(self, body: List[ASTNode]) -> bool:
        """递归检测函数体中是否包含 yield(语句或表达式 — S3: `let x = yield v`)

        嵌套 FunctionDef 不递归 — 它的 yield 属于它自己(旧版递归进嵌套
        函数体会把外层误标成生成器: 饿收集时代被掩盖, S3 真惰性后
        「调用即返回生成器」会直接吃掉外层执行 — 回归已锁)。
        """
        for stmt in body:
            if isinstance(stmt, YieldStmt):
                return True
            if isinstance(stmt, FunctionDef):
                continue  # 嵌套函数: 它的生成器性在它自己调用时判定
            if _expr_contains_yield(stmt):
                return True
            if hasattr(stmt, 'body'):
                if self._has_yield_in_body(stmt.body):
                    return True
            if hasattr(stmt, 'then_branch'):
                if self._has_yield_in_body(stmt.then_branch):
                    return True
                for _, elif_body in getattr(stmt, 'elif_branches', []):
                    if self._has_yield_in_body(elif_body):
                        return True
                if hasattr(stmt, 'else_branch') and stmt.else_branch:
                    if self._has_yield_in_body(stmt.else_branch):
                        return True
            if hasattr(stmt, 'try_body'):
                if self._has_yield_in_body(stmt.try_body):
                    return True
            if hasattr(stmt, 'catch_body'):
                if self._has_yield_in_body(stmt.catch_body):
                    return True
            if hasattr(stmt, 'finally_body') and stmt.finally_body:
                if self._has_yield_in_body(stmt.finally_body):
                    return True
        return False

    def parse_parameter_list(self) -> List[Tuple[str, str, Any]]:
        """解析参数列表 - 支持有类型/无类型参数、默认值、this作为参数名
        返回: [(name, type, default_expr_or_None), ...]
        """
        params = []

        def _read_param_name() -> str:
            """读取参数名,允许 this 关键字"""
            if self.match(TokenType.KEYWORD, 'this'):
                self.advance()
                return 'this'
            return self.expect(TokenType.IDENTIFIER).value

        if not self.match(TokenType.SYMBOL, ')'):
            # 第一个参数
            param_name = _read_param_name()
            param_type = "Any"
            if self.match(TokenType.SYMBOL, ':'):
                self.advance()
                param_type = self._parse_type_annotation()
            # 检查默认值 (param: Type = expr)
            default_expr = None
            if self.match(TokenType.OPERATOR, '='):
                self.advance()
                default_expr = self.parse_expression()
            params.append((param_name, param_type, default_expr))

            # 更多参数
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                self._skip_newlines()
                param_name = _read_param_name()
                param_type = "Any"
                if self.match(TokenType.SYMBOL, ':'):
                    self.advance()
                    param_type = self._parse_type_annotation()
                default_expr = None
                if self.match(TokenType.OPERATOR, '='):
                    self.advance()
                    default_expr = self.parse_expression()
                params.append((param_name, param_type, default_expr))

        return params

    def parse_lambda_expr(self) -> 'LambdaExpr':
        """解析匿名函数表达式: fn(params) { body }"""
        start_token = self.expect(TokenType.KEYWORD, 'fn')
        
        # 参数列表
        self.expect(TokenType.SYMBOL, '(')
        self._skip_newlines()
        params = self.parse_parameter_list()
        self._skip_newlines()
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
            elif self.match(TokenType.IDENTIFIER, 'async'):
                # A3a: 类内 async def — 软关键字(仅后随 def 时吞)
                is_async = self._consume_async()
                if not is_async or not self.match(TokenType.KEYWORD, 'def'):
                    self.error(self.current_token, "async 必须紧跟 def")
                    self.synchronize()
                    continue
                method = self.parse_function_def()
                if method:
                    method.is_async = True
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

        # 装饰器语句(X1 二批): @deco / @deco(args) 必须紧跟 def —
        # 覆盖函数体内等语句级位置的 def(顶层走 program() 收集路径)
        if self.match(TokenType.SYMBOL, '@'):
            decorators = self._parse_decorators()
            is_async = self._consume_async()
            if not self.match(TokenType.KEYWORD, 'def'):
                self.error(self.current_token, "装饰器 @ 必须紧跟函数定义")
                self.synchronize()
                return None
            func = self.parse_function_def()
            if func is not None:
                func.is_async = is_async
                func.decorators = decorators
            return func

        # 变量声明
        if self.match(TokenType.KEYWORD, 'let') or self.match(TokenType.KEYWORD, 'var') or self.match(TokenType.KEYWORD, 'const'):
            return self.parse_variable_decl()

        # 返回语句
        if self.match(TokenType.KEYWORD, 'return'):
            return self.parse_return_stmt()

        # 生成器 yield
        if self.match(TokenType.KEYWORD, 'yield'):
            return self.parse_yield_stmt()

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

        # 嵌套函数定义（闭包）
        # A3a: async def — 软关键字前缀(函数体内的协程定义)
        is_async = self._consume_async()
        if self.match(TokenType.KEYWORD, 'def'):
            func = self.parse_function_def()
            if func is not None:
                func.is_async = is_async
            return func

        # 枚举定义
        if self.match(TokenType.KEYWORD, 'enum'):
            return self.parse_enum_def()

        # try-catch 语句
        if self.match(TokenType.KEYWORD, 'try'):
            return self.parse_try_stmt()

        # raise 语句(EX1): raise <错误值> [from <原因>] ;
        if self.match(TokenType.KEYWORD, 'raise'):
            token = self.current_token
            self.advance()
            value = self.parse_expression()
            cause = None
            if self.match(TokenType.KEYWORD, 'from'):
                self.advance()
                cause = self.parse_expression()
            self.expect(TokenType.SYMBOL, ';')
            return RaiseStmt(value=value, cause=cause,
                             line=token.line, column=token.column)

        # spawn 语句(CC1): spawn <可调用>; / spawn f(args);
        if self.match(TokenType.KEYWORD, 'spawn'):
            token = self.current_token
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.SYMBOL, ';')
            return SpawnStmt(expr=expr, line=token.line, column=token.column)

        # scope 块(CC1): scope { ... } — 退出自动 join
        if self.match(TokenType.KEYWORD, 'scope'):
            token = self.current_token
            self.advance()
            self.expect(TokenType.SYMBOL, '{')
            scope_stmt = ScopeStmt(line=token.line, column=token.column)
            while not self.match(TokenType.SYMBOL, '}'):
                s = self.parse_statement()
                if s:
                    scope_stmt.body.append(s)
            self.expect(TokenType.SYMBOL, '}')
            return scope_stmt

        # with 语句(P1.1): with expr [as name] { body }
        if self.match(TokenType.KEYWORD, 'with'):
            return self.parse_with_stmt()

        # 类型别名(P1.3a): type Name = TypeExpr; — type 是软关键字,
        # 只在「type IDENT =」模式出现时生效, 否则回退(如 type(x) 内置函数调用)
        if self.match(TokenType.IDENTIFIER, 'type'):
            saved_pos = self.pos
            self.advance()
            if (self.match(TokenType.IDENTIFIER)
                    and self.peek().type == TokenType.OPERATOR
                    and self.peek().value == '='):
                return self.parse_type_alias()
            self.pos = saved_pos

        # defer 语句
        if self.match(TokenType.KEYWORD, 'defer'):
            token = self.current_token
            self.advance()
            def_stmt = DeferStmt(line=token.line, column=token.column)
            self.expect(TokenType.SYMBOL, '{')
            while not self.match(TokenType.SYMBOL, '}'):
                s = self.parse_statement()
                if s:
                    def_stmt.body.append(s)
            self.expect(TokenType.SYMBOL, '}')
            return def_stmt

        # assert 语句
        if self.match(TokenType.KEYWORD, 'assert'):
            token = self.current_token
            self.advance()
            cond = self.parse_expression()
            msg = None
            if self.match(TokenType.SYMBOL, ','):
                self.advance()
                msg = self.parse_expression()
            self.expect(TokenType.SYMBOL, ';')
            return AssertStmt(condition=cond, message=msg, line=token.line, column=token.column)

        # Import语句
        if self.match(TokenType.KEYWORD, 'import'):
            return self.parse_import_stmt()

        # Export语句: export name1, name2; — 显式声明模块边界(P2.1)
        if self.match(TokenType.KEYWORD, 'export'):
            return self.parse_export_stmt()

        # 成员赋值语句: this.x = ... 或 obj.field = ... 或 this.min.x = ... (链式)
        if self.match(TokenType.KEYWORD, 'this') and self.peek() and self.peek().type == TokenType.SYMBOL and self.peek().value == '.':
            # 检查是否是赋值（链式 .x.y.z = ... 或单层 .x = ...）
            if self._is_member_assignment_chain():
                return self.parse_member_assignment()
        if self.match(TokenType.IDENTIFIER) and self.peek() and self.peek().type == TokenType.SYMBOL and self.peek().value == '.' and \
           self.tokens[self.pos + 2].type == TokenType.IDENTIFIER and \
           self.pos + 3 < len(self.tokens) and self.tokens[self.pos + 3].value in ('=', '+=', '-=', '*=', '/=', '%=', '**='):
            return self.parse_member_assignment()

        # 下标赋值语句: obj[key] = value (由 parse_expression 后的表达式语句分支处理)
        # 无需单独检测——parse_expression 返回 SubscriptExpr 后再检查赋值

        # 赋值语句
        if self.match(TokenType.IDENTIFIER) and self.peek().value in ('=', '+=', '-=', '*=', '/=', '%=', '**=', '//='):
            return self.parse_assignment()

        # 函数调用
        if self.match(TokenType.IDENTIFIER) and self.peek().value == '(':
            return self.parse_expression_stmt()

        # 表达式语句
        saved_pos = self.pos
        saved_token = self.current_token
        expr = self.parse_expression()
        if expr:
            # 下标/切片赋值检测: SubscriptExpr/SliceExpr 后跟赋值操作符
            # (S2a: l[a:b] = v — 切片读取的产物是 SliceExpr, 同样可作赋值目标)
            if isinstance(expr, (SubscriptExpr, SliceExpr)) and self.current_token and self.current_token.value in ('=', '+=', '-=', '*=', '/=', '%=', '**=', '//='):
                op = self.current_token.value
                self.advance()
                value = self.parse_expression()
                self.expect(TokenType.SYMBOL, ';')
                # SliceExpr 整体即索引(切片); SubscriptExpr 取内层 index
                index_expr = expr if isinstance(expr, SliceExpr) else expr.index
                return SubscriptAssignment(
                    obj=expr.obj, index=index_expr, value=value, op=op,
                    line=expr.line, column=expr.column
                )
            # 跳过后续换行 → 函数体末尾的表达式允许省略分号
            while self.match(TokenType.NEWLINE):
                self.advance()
            if not self.match(TokenType.SYMBOL, '}'):
                self.expect(TokenType.SYMBOL, ';')
            return expr

        return None

    def _is_member_assignment_chain(self) -> bool:
        """检查从当前位置开始是否是链式成员赋值 (this.x.y = ... 或 this.x = ...)"""
        # 保存当前位置和token
        saved_pos = self.pos
        saved_token = self.current_token
        self.advance()  # 跳过 this
        if not self.match(TokenType.SYMBOL, '.'):
            self.pos = saved_pos
            self.current_token = saved_token
            return False
        self.advance()  # 跳过 .
        # 沿着 .ident 链前进
        while self.match(TokenType.IDENTIFIER):
            self.advance()
            if self.match(TokenType.SYMBOL, '.'):
                self.advance()  # 继续链
                continue
            else:
                # 链结束，检查是否是赋值操作符
                if self.current_token and self.current_token.value in ('=', '+=', '-=', '*=', '/=', '%=', '**='):
                    self.pos = saved_pos
                    self.current_token = saved_token
                    return True
                break
        self.pos = saved_pos
        self.current_token = saved_token
        return False

    def parse_member_assignment(self) -> 'MemberAssignment':
        """解析成员赋值: this.x = value 或 obj.field = value 或 this.min.x = value (链式)"""
        start_token = self.current_token
        
        # 解析对象部分 (this 或 identifier)
        if self.match(TokenType.KEYWORD, 'this'):
            obj = Variable(name='this', line=start_token.line, column=start_token.column)
            self.advance()
        else:
            obj = Variable(name=self.expect(TokenType.IDENTIFIER).value, line=start_token.line, column=start_token.column)
        
        self.expect(TokenType.SYMBOL, '.')
        member = self.expect(TokenType.IDENTIFIER).value
        
        # 检查是否是链式: this.min.x = ... → MemberAccess(this, min) 作为 obj, x 作为 member
        while self.match(TokenType.SYMBOL, '.'):
            # 当前 obj.member 变成新的 obj
            obj = MemberAccess(
                obj=obj,
                member=member,
                line=start_token.line,
                column=start_token.column
            )
            self.advance()  # 跳过 .
            member = self.expect(TokenType.IDENTIFIER).value
        
        op_token = self.expect(TokenType.OPERATOR)
        value = self.parse_expression()
        self.expect(TokenType.SYMBOL, ';')
        
        return MemberAssignment(
            obj=obj,
            member=member,
            op=op_token.value,
            value=value,
            line=start_token.line,
            column=start_token.column
        )

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

    def parse_export_stmt(self) -> ExportStmt:
        """解析 export 语句(P2.1): export name1, name2;

        显式声明模块边界 — 你是社会关系的总和,
        暴露给外部才成为真实存在。
        """
        start_token = self.expect(TokenType.KEYWORD, 'export')
        stmt = ExportStmt(line=start_token.line, column=start_token.column)
        stmt.exports.append(self.expect(TokenType.IDENTIFIER).value)
        while self.match(TokenType.SYMBOL, ','):
            self.advance()
            stmt.exports.append(self.expect(TokenType.IDENTIFIER).value)
        self.expect(TokenType.SYMBOL, ';')
        return stmt

    def parse_type_alias(self) -> 'TypeAliasStmt':
        """解析类型别名(P1.3a): type Name = TypeExpr;

        调用时 current token 已是别名名(软关键字分支已跳过 type)。
        """
        start_token = self.current_token
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.OPERATOR, '=')
        aliased = self._parse_type_annotation()
        self.expect(TokenType.SYMBOL, ';')
        return TypeAliasStmt(name=name, aliased_type=aliased,
                             line=start_token.line, column=start_token.column)

    def parse_with_stmt(self) -> 'WithStmt':
        """解析 with 语句(P1.1): with expr [as name] { body }"""
        start_token = self.expect(TokenType.KEYWORD, 'with')
        stmt = WithStmt(line=start_token.line, column=start_token.column)
        stmt.resource = self.parse_expression()
        if self.match(TokenType.KEYWORD, 'as'):
            self.advance()
            stmt.var_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SYMBOL, '{')
        while not self.match(TokenType.SYMBOL, '}'):
            s = self.parse_statement()
            if s:
                stmt.body.append(s)
        self.expect(TokenType.SYMBOL, '}')
        if self.match(TokenType.SYMBOL, ';'):
            self.advance()
        return stmt

    def parse_try_stmt(self) -> 'TryStmt':
        """解析 try-catch 语句"""
        start_token = self.expect(TokenType.KEYWORD, 'try')
        stmt = TryStmt(line=start_token.line, column=start_token.column)

        # try 块
        self.expect(TokenType.SYMBOL, '{')
        while not self.match(TokenType.SYMBOL, '}'):
            s = self.parse_statement()
            if s:
                stmt.try_body.append(s)
        self.expect(TokenType.SYMBOL, '}')

        # 跳过换行
        while self.match(TokenType.NEWLINE):
            self.advance()

        # catch 块 (可选)
        if self.match(TokenType.KEYWORD, 'catch'):
            self.advance()
            # catch (e) 或 catch e
            if self.match(TokenType.SYMBOL, '('):
                self.advance()
                stmt.catch_var = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.SYMBOL, ')')
            else:
                stmt.catch_var = self.expect(TokenType.IDENTIFIER).value
            # P1.4: 可选类型过滤 catch e: ContractError
            if self.match(TokenType.SYMBOL, ':'):
                self.advance()
                stmt.catch_types.append(self.expect(TokenType.IDENTIFIER).value)
            self.expect(TokenType.SYMBOL, '{')
            while not self.match(TokenType.SYMBOL, '}'):
                s = self.parse_statement()
                if s:
                    stmt.catch_body.append(s)
            self.expect(TokenType.SYMBOL, '}')

            # 跳过换行
            while self.match(TokenType.NEWLINE):
                self.advance()

        # finally 块 (可选)
        if self.match(TokenType.KEYWORD, 'finally'):
            self.advance()
            self.expect(TokenType.SYMBOL, '{')
            while not self.match(TokenType.SYMBOL, '}'):
                s = self.parse_statement()
                if s:
                    stmt.finally_body.append(s)
            self.expect(TokenType.SYMBOL, '}')

        return stmt

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

    def parse_yield_stmt(self) -> YieldStmt:
        """解析 yield 语句 — 生成器产出值; yield from expr 委派转发(P1.5)"""
        start_token = self.expect(TokenType.KEYWORD, 'yield')
        stmt = YieldStmt(line=start_token.line, column=start_token.column)

        # yield from expr — 把可迭代对象的产出逐个转发
        if self.match(TokenType.KEYWORD, 'from'):
            self.advance()
            stmt.from_expr = self.parse_expression()
            self.expect(TokenType.SYMBOL, ';')
            return stmt

        if not self.match(TokenType.SYMBOL, ';'):
            stmt.value = self.parse_expression()

        self.expect(TokenType.SYMBOL, ';')
        return stmt

    def parse_yield_expr(self) -> YieldExpr:
        """解析 yield 表达式(S3) — yield [expr] / yield from expr

        语句位 yield 走 parse_yield_stmt; 表达式位(赋值右侧/实参/运算)
        走本入口 — yield 产出的同时可接收 send 进来的值:
        `let received = yield produced;`
        """
        start_token = self.expect(TokenType.KEYWORD, 'yield')
        expr = YieldExpr(line=start_token.line, column=start_token.column)

        if self.match(TokenType.KEYWORD, 'from'):
            self.advance()
            expr.from_expr = self.parse_expression()
            return expr

        # 裸 yield: 后面是 ; } 或换行 — 无产出值(对齐语句形语义)
        if not (self.match(TokenType.SYMBOL, ';')
                or self.match(TokenType.SYMBOL, '}')
                or self.match(TokenType.NEWLINE)):
            expr.value = self.parse_expression()
        return expr

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
            if self.match(TokenType.KEYWORD, 'if'):
                # else if 链 → 嵌套 IfStmt(标准悬空 else 处理, 与 elif 语义等价)
                # 修根因: 原实现 else 后只接受 '{', Python 式 else if 触发
                # panic 恢复把后续语句错位到外层, 模块加载时函数体泄洪到顶层
                nested = self.parse_if_stmt()
                stmt.else_branch.append(nested)
            else:
                self.expect(TokenType.SYMBOL, '{')
                while not self.match(TokenType.SYMBOL, '}'):
                    branch_stmt = self.parse_statement()
                    if branch_stmt:
                        stmt.else_branch.append(branch_stmt)
                self.expect(TokenType.SYMBOL, '}')

        return stmt

    def parse_if_expr(self) -> "IfExpr":
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

        # 标识符 → 变量模式 或 构造器模式 (Ok(v)/Err(e)) 或枚举路径
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

            # 枚举路径模式: Direction::North
            # 先消费 IDENTIFIER，然后检测 ::
            self.advance()  # 消费 Direction
            if self.match_double_colon():
                self.consume_double_colon()
                variant = self.expect(TokenType.IDENTIFIER).value
                return EnumPattern(enum_name=name, variant=variant)
            # 不是 ::，回退到变量模式
            return VariablePattern(name=name)

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
        """解析类型标注: Int | List[Int] | Dict[String, Int] | Result[Int, String] | A | B"""
        base = self.expect(TokenType.IDENTIFIER).value

        # Union 类型(P1.3a): A | B — 不二法门的推广
        if self.match(TokenType.OPERATOR, '|'):
            parts = [base]
            while self.match(TokenType.OPERATOR, '|'):
                self.advance()
                parts.append(self._parse_type_annotation())
            return " | ".join(parts)

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

        # 检查是否是解包语法: for (i, x) in items
        if self.match(TokenType.SYMBOL, '('):
            self.advance()  # 跳过 (
            stmt.vars.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                stmt.vars.append(self.expect(TokenType.IDENTIFIER).value)
            self.expect(TokenType.SYMBOL, ')')
        else:
            # 单变量: for x in items
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

    def _is_subscript_assignment(self) -> bool:
        """前瞻检查: 从当前位置往后, ] 之后是否是赋值操作符?"""
        saved = self.pos
        bracket_depth = 0
        try:
            while self.pos < len(self.tokens):
                tok = self.tokens[self.pos]
                if tok.value == '[':
                    bracket_depth += 1
                elif tok.value == ']':
                    bracket_depth -= 1
                    if bracket_depth == 0:
                        # 找到匹配的 ], 检查下一个
                        if self.pos + 1 < len(self.tokens):
                            nxt = self.tokens[self.pos + 1].value
                            return nxt in ('=', '+=', '-=', '*=', '/=', '%=', '**=', '//=')
                        break
                self.pos += 1
            return False
        finally:
            self.pos = saved

    def parse_subscript_assignment(self) -> 'SubscriptAssignment':
        """解析下标赋值: obj[key] = value"""
        start_token = self.current_token
        obj_name = self.expect(TokenType.IDENTIFIER).value
        obj = Variable(name=obj_name, line=start_token.line, column=start_token.column)
        self.expect(TokenType.SYMBOL, '[')
        index = self.parse_expression()
        self.expect(TokenType.SYMBOL, ']')
        op_token = self.expect(TokenType.OPERATOR)
        value = self.parse_expression()
        self.expect(TokenType.SYMBOL, ';')
        return SubscriptAssignment(
            obj=obj, index=index, value=value, op=op_token.value,
            line=start_token.line, column=start_token.column
        )

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
        """解析表达式 - 三元 > 通道发送 > 管道 > 逻辑或 > ...

        CC2: ch <- v 是发送表达式, 优先级最低(右部吃到语句/参数尾),
        与 Go 的 ch <- v 语句位一致。
        """
        expr = self.parse_ternary()
        # S2a: 海象赋值 := — 表达式级赋值, 左部必须是变量;
        # 右部递归吃三元级(or/and/管道都低于它), `x := a or b` => `x := (a or b)`
        if self.match(TokenType.OPERATOR, ':='):
            op_token = self.current_token
            self.advance()
            if not isinstance(expr, Variable):
                self.error(op_token, "海象赋值 := 左侧必须是变量名(如 (n := f()))")
            value = self.parse_ternary()
            expr = WalrusExpr(name=expr.name, value=value,
                              line=op_token.line, column=op_token.column)
        while self.match(TokenType.OPERATOR) and self.current_token.value == '<-':
            op_token = self.current_token
            self.advance()
            right = self.parse_ternary()
            expr = SendExpr(chan=expr, value=right, line=op_token.line, column=op_token.column)
        return expr

    def parse_ternary(self) -> Expression:
        """解析三元表达式 cond ? then : else"""
        expr = self.parse_pipe()
        if self.match(TokenType.SYMBOL, '?'):
            token = self.current_token
            self.advance()
            # 区分三元 vs TryExpr: 三元需要 ? 后面有表达式;
            # ? 后是 : / 行尾 / ; / ) 或二元运算符(== != < > 等)时,
            # 这是后缀 TryExpr(result?), 回退让 postfix 处理
            if (self.match(TokenType.SYMBOL, ':') or self.match(TokenType.NEWLINE)
                    or self.match(TokenType.SYMBOL, ';')
                    or self.match(TokenType.SYMBOL, ')')
                    or self.match(TokenType.OPERATOR)):
                # TryExpr: result? (后缀)
                # 回退,让 postfix 处理
                self.pos -= 1
                return expr
            then_expr = self.parse_pipe()
            self.expect(TokenType.SYMBOL, ':')
            else_expr = self.parse_ternary()  # 递归支持嵌套三元
            expr = TernaryExpr(condition=expr, then_expr=then_expr, else_expr=else_expr,
                              line=token.line, column=token.column)
        return expr

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
        """解析比较表达式，支持 in / not in"""
        expr = self.parse_addition()

        while ((self.match(TokenType.OPERATOR) and self.current_token.value in ('==', '!=', '<', '>', '<=', '>='))
               or (self.match(TokenType.KEYWORD, 'in'))):
            op_token = self.current_token
            self.advance()
            right = self.parse_addition()
            expr = BinaryOp(left=expr, op=op_token.value, right=right, line=op_token.line, column=op_token.column)
        
        # not in 需要特殊处理（是两个字的关键词）
        if self.match(TokenType.KEYWORD, 'not'):
            # 检查是否紧跟着 in
            saved = self.current_token
            self.advance()  # 消费 not
            if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'in':
                self.advance()  # 消费 in
                right = self.parse_addition()
                expr = BinaryOp(left=expr, op='not in', right=right, line=saved.line, column=saved.column)
            else:
                self.error(saved, "'not' 后面期望 'in'（not in 操作）")

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

    def _starts_expression(self, tok) -> bool:
        """A3a: 判断 token 能否作为表达式起点(await 软关键字的消歧依据)

        保守集: 排除语句终止符与不能起始表达式的算符 —
        `-`/`+`/`!` 可起始一元表达式故保留(await -1 虽怪但合法)。
        """
        if tok is None:
            return False
        if tok.type == TokenType.NEWLINE:
            return False
        if tok.type == TokenType.SYMBOL and tok.value in (
                ';', ',', ')', ']', '}', '=', '==', '!=', '<=', '>=',
                '<', '>', '&&', '||', '?', ':', '.', '->', '=>', '<-'):
            return False
        if tok.type == TokenType.OPERATOR and tok.value in (
                '&&', '||', '==', '!=', '<=', '>=', '<', '>', '=', '+=',
                '-=', '*=', '/=', '%=', '**=', '//=', '?', ':'):
            return False
        return True

    def parse_unary(self) -> Expression:
        """解析一元运算"""
        # 'not' 关键字作为逻辑非
        if self.match(TokenType.KEYWORD, 'not'):
            op_token = self.current_token
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(op='!', operand=operand, line=op_token.line, column=op_token.column)
        # A3a: await 协程(前缀软关键字 — 仅当后随表达式起点时才吞,
        # `await` 单独作变量名/语句结尾不受影响)
        if (self.match(TokenType.IDENTIFIER, 'await')
                and self._starts_expression(self.peek())):
            op_token = self.current_token
            self.advance()
            operand = self.parse_unary()
            return AwaitExpr(operand=operand, line=op_token.line,
                             column=op_token.column)
        # CC2: <- ch 通道接收(前缀, 与 ch <- v 共用 <- 词法)
        if self.match(TokenType.OPERATOR) and self.current_token.value == '<-':
            op_token = self.current_token
            self.advance()
            operand = self.parse_unary()
            return RecvExpr(chan=operand, line=op_token.line, column=op_token.column)
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
                    self._skip_newlines()
                    call.args.append(self.parse_expression())
                    while self.match(TokenType.SYMBOL, ','):
                        self.advance()
                        self._skip_newlines()
                        call.args.append(self.parse_expression())
                self._skip_newlines()
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
            
            # 下标访问 / 切片
            elif self.match(TokenType.SYMBOL, '['):
                start_token = self.current_token
                self.advance()
                # 检查是否为切片 [start:end] 或 [:end] 或 [start:] 或 [start::step] 或 [::step]
                start_expr = None
                if not self.match(TokenType.SYMBOL, ':') and not self.match(TokenType.SYMBOL, ']'):
                    start_expr = self.parse_expression()
                
                if self.match_double_colon():
                    # 步长切片 [start::step] 或 [::step]
                    self.consume_double_colon()
                    step_expr = None
                    if not self.match(TokenType.SYMBOL, ']'):
                        step_expr = self.parse_expression()
                    self.expect(TokenType.SYMBOL, ']')
                    expr = SliceExpr(obj=expr, start=start_expr, end=None, step=step_expr,
                                    line=start_token.line, column=start_token.column)
                elif self.match(TokenType.SYMBOL, ':'):
                    # 切片 [start:end] 或 [start:end:step]
                    self.advance()  # 跳过 :
                    end_expr = None
                    if not self.match(TokenType.SYMBOL, ']') and not self.match(TokenType.SYMBOL, ':'):
                        end_expr = self.parse_expression()
                    
                    step_expr = None
                    if self.match(TokenType.SYMBOL, ':'):
                        self.advance()
                        if not self.match(TokenType.SYMBOL, ']'):
                            step_expr = self.parse_expression()
                    
                    self.expect(TokenType.SYMBOL, ']')
                    expr = SliceExpr(obj=expr, start=start_expr, end=end_expr, step=step_expr,
                                    line=start_token.line, column=start_token.column)
                else:
                    # 普通下标
                    self.expect(TokenType.SYMBOL, ']')
                    expr = SubscriptExpr(obj=expr, index=start_expr,
                                        line=start_token.line, column=start_token.column)
            
            # ? 操作符 — Err 提前返回(后缀 TryExpr) vs 三元表达式 cond ? a : b
            elif self.match(TokenType.SYMBOL, '?'):
                next_tok = self.peek()
                # ? 后是「表达式起始」才是三元(让 ternary 处理);
                # 否则(== != < > ; ) , ] 行尾…)是后缀 TryExpr, 在此直接消费 —
                # 早先的 break 设计会让 ? 遗留在 token 流中被 panic mode 吞掉
                is_expr_start = (
                    next_tok is None or
                    next_tok.type in (TokenType.IDENTIFIER, TokenType.STRING,
                                      TokenType.NUMBER, TokenType.KEYWORD) or
                    (next_tok.type == TokenType.SYMBOL
                     and next_tok.value in ('(', '[', '{', '-', '!'))
                )
                if is_expr_start:
                    break  # 让 ternary 处理
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
            return self._parse_string_literal(token)

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

        # S3: yield 表达式 — let x = yield v; (send 的递送点)
        elif self.match(TokenType.KEYWORD, 'yield'):
            return self.parse_yield_expr()

        # 变量
        elif self.match(TokenType.IDENTIFIER):
            self.advance()
            # 检查是否是枚举路径 Direction::North
            if self.match_double_colon():
                self.consume_double_colon()
                variant_name = self.expect(TokenType.IDENTIFIER).value
                return Variable(name=variant_name, line=token.line, column=token.column)
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

    @staticmethod
    def _skip_string_in(text: str, i: int) -> int:
        """text[i] 是引号 — 返回收尾引号之后的位置(引号内括号/冒号不计数)"""
        q = text[i]
        i += 1
        while i < len(text):
            if text[i] == '\\':
                i += 2
                continue
            if text[i] == q:
                return i + 1
            i += 1
        return i

    def _scan_interpolations(self, raw: str, token):
        """S2b: 扫描 ${...} 插值段(括号感知 + 字符串感知)

        返回 [(kind, text, spec, debug), ...]:
          kind='str'  — text 字面量, spec/debug 无意义
          kind='expr' — text 表达式源码, spec 格式规格(None 或 str),
                        debug 是否 f"{x=}" 调试格式
        旧正则 [^}]+ 不敢放嵌套括号(切片 l[1:2]/字典/调用);
        本扫描器括号深度感知, "${d["k"]}" 类嵌套引号由 lexer 侧放行。
        """
        parts = []
        i, n, last = 0, len(raw), 0
        while i < n:
            if raw[i] == '$' and i + 1 < n and raw[i + 1] == '{':
                depth = 0
                j = i + 1  # 指向 {
                while j < n:
                    c = raw[j]
                    if c in '([{':
                        depth += 1
                    elif c in ')]}':
                        depth -= 1
                        if depth == 0:
                            break
                    elif c in '"\'':
                        j = self._skip_string_in(raw, j)
                        continue
                    j += 1
                if depth != 0:
                    raise SyntaxError(f"未闭合的插值表达式,行 {token.line}")
                content = raw[i + 2:j]
                if i > last:
                    parts.append(('str', raw[last:i], None, False))
                expr_text, spec, debug = self._split_interp_content(content, token)
                parts.append(('expr', expr_text, spec, debug))
                i = j + 1
                last = i
            else:
                i += 1
        if last < n:
            parts.append(('str', raw[last:], None, False))
        return parts

    def _split_interp_content(self, content: str, token):
        """拆分插值内容: expr [=] [: spec] — 对齐 Python f-string 三形态"""
        # 深度1 的 ':' 才是规格分隔符(切片 l[1:2]/字典内的不算)
        depth = 0
        colon = -1
        k = 0
        while k < len(content):
            c = content[k]
            if c in '([{':
                depth += 1
            elif c in ')]}':
                depth -= 1
            elif c in '"\'':
                k = self._skip_string_in(content, k)
                continue
            elif c == ':' and depth == 0:
                colon = k
                break
            k += 1
        if colon >= 0:
            expr_text = content[:colon]
            spec = content[colon + 1:].strip()
        else:
            expr_text = content
            spec = None
        # 调试格式 f"{x=}": 表达式末尾独立 '='(= 前面不是 =!<> 比较符)
        stripped = expr_text.rstrip()
        if (stripped.endswith('=')
                and not stripped.endswith('==')
                and not (len(stripped) >= 2 and stripped[-2] in '=!<>')):
            expr_text = stripped[:-1].rstrip()
            debug = True
        else:
            debug = False
        if not expr_text.strip():
            raise SyntaxError(f"空的插值表达式,行 {token.line}")
        return expr_text, spec, debug

    def _parse_string_literal(self, token) -> 'Expression':
        """解析字符串字面量,支持 ${expr} / ${expr=} / ${expr:spec} 插值(S2b)"""
        raw = token.value
        # 检查是否有 ${...} 插值
        if '${' not in raw:
            return Literal(value=raw, literal_type='string', line=token.line, column=token.column)

        parts = self._scan_interpolations(raw, token)

        def make_str(s):
            return Literal(value=s, literal_type='string', line=token.line, column=token.column)

        def make_expr(text):
            """将插值表达式文本解析为AST"""
            inner_lexer = Lexer(text)
            inner_tokens = inner_lexer.tokenize()
            inner_parser = Parser(inner_tokens, text)
            return inner_parser.parse_expression()

        def make_value_node(expr_text, spec):
            """插值求值节点: 有规格走 format(v, spec), 否则 str(v)"""
            inner = make_expr(expr_text)
            if spec:
                return CallExpr(
                    func=Variable(name='format', line=token.line, column=token.column),
                    args=[inner, make_str(spec)],
                    line=token.line, column=token.column
                )
            return CallExpr(
                func=Variable(name='str', line=token.line, column=token.column),
                args=[inner],
                line=token.line, column=token.column
            )

        result = None
        for kind, text, spec, debug in parts:
            if kind == 'str':
                node = make_str(text)
            else:
                value_node = make_value_node(text, spec)
                if debug:
                    # f"{x=}" → "x=" + str(x) — 调试格式自带表达式原文
                    node = BinaryOp(
                        op='+',
                        left=make_str(text + '='),
                        right=value_node,
                        line=token.line, column=token.column
                    )
                else:
                    node = value_node
            if result is None:
                result = node
            else:
                result = BinaryOp(
                    op='+', left=result, right=node,
                    line=token.line, column=token.column
                )

        return result

    def parse_call_expr(self, func_name: str) -> CallExpr:
        """解析函数调用"""
        start_token = self.current_token
        self.expect(TokenType.SYMBOL, '(')

        call = CallExpr(func=func_name, line=start_token.line, column=start_token.column)

        # 解析参数（括号内允许换行）
        if not self.match(TokenType.SYMBOL, ')'):
            self._skip_newlines()
            call.args.append(self.parse_expression())
            while self.match(TokenType.SYMBOL, ','):
                self.advance()
                self._skip_newlines()
                call.args.append(self.parse_expression())

        self._skip_newlines()
        self.expect(TokenType.SYMBOL, ')')
        return call


    def _skip_newlines(self):
        """跳过换行符（用于括号内多行参数/元素）"""
        while self.match(TokenType.NEWLINE):
            self.advance()

    def parse_list_expr(self) -> 'Expression':
        """解析列表表达式（含推导式）"""
        start_token = self.expect(TokenType.SYMBOL, '[')
        
        if self.match(TokenType.SYMBOL, ']'):
            self.advance()
            return ListExpr(line=start_token.line, column=start_token.column)
        
        first = self.parse_expression()
        
        # 检查是否是推导式: [expr for x in items if cond]
        if self.match(TokenType.KEYWORD, 'for'):
            self.advance()  # 跳过 for
            # 循环变量
            var_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.KEYWORD, 'in')
            iterable = self.parse_expression()
            
            # 可选 if 条件
            condition = None
            if self.match(TokenType.KEYWORD, 'if'):
                self.advance()
                condition = self.parse_expression()
            
            self.expect(TokenType.SYMBOL, ']')
            
            return ListCompExpr(
                element=first,
                var_name=var_name,
                iterable=iterable,
                condition=condition,
                line=start_token.line,
                column=start_token.column
            )
        
        # 普通列表
        expr = ListExpr(line=start_token.line, column=start_token.column)
        expr.elements.append(first)
        while self.match(TokenType.SYMBOL, ','):
            self.advance()
            self._skip_newlines()
            if self.match(TokenType.SYMBOL, ']'):
                break  # 尾逗号
            expr.elements.append(self.parse_expression())
        
        self.expect(TokenType.SYMBOL, ']')
        return expr

    def parse_dict_expr(self) -> 'Expression':
        """解析字典表达式 {key: value, ...} 或 字典推导式 {k: v for x in items}"""
        start_token = self.expect(TokenType.SYMBOL, '{')

        self._skip_newlines()
        
        # 空字典
        if self.match(TokenType.SYMBOL, '}'):
            self.advance()
            return DictExpr(entries=[], line=start_token.line, column=start_token.column)
        
        # 解析第一个 key: value
        key = self.parse_expression()
        self.expect(TokenType.SYMBOL, ':')
        self._skip_newlines()
        value = self.parse_expression()
        
        # 推导式检测: 如果下一个 token 是 for，则是字典推导式
        if self.match(TokenType.KEYWORD, 'for'):
            self.advance()
            var_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.KEYWORD, 'in')
            iterable = self.parse_expression()
            condition = None
            if self.match(TokenType.KEYWORD, 'if'):
                self.advance()
                condition = self.parse_expression()
            self._skip_newlines()
            self.expect(TokenType.SYMBOL, '}')
            return DictCompExpr(
                key_expr=key, value_expr=value,
                var_name=var_name, iterable=iterable, condition=condition,
                line=start_token.line, column=start_token.column
            )
        
        # 普通字典
        expr = DictExpr(entries=[(key, value)], line=start_token.line, column=start_token.column)
        while self.match(TokenType.SYMBOL, ','):
            self.advance()
            self._skip_newlines()
            if self.match(TokenType.SYMBOL, '}'):
                break  # trailing comma
            key = self.parse_expression()
            self.expect(TokenType.SYMBOL, ':')
            self._skip_newlines()
            value = self.parse_expression()
            expr.entries.append((key, value))

        self._skip_newlines()
        self.expect(TokenType.SYMBOL, '}')
        return expr

@dataclass
class ListExpr(Expression):
    """列表表达式"""
    elements: List[Expression] = field(default_factory=list)

@dataclass
class ListCompExpr(Expression):
    """列表推导式 [expr for x in items if cond]"""
    element: Expression = None  # 循环体表达式
    var_name: str = ""  # 循环变量名
    iterable: Expression = None  # 可迭代对象
    condition: Expression = None  # 可选 if 条件

@dataclass
class DictCompExpr(Expression):
    """字典推导式 {k: v for x in items if cond}"""
    key_expr: Expression = None
    value_expr: Expression = None
    var_name: str = ""
    iterable: Expression = None
    condition: Expression = None  # 可选 if 条件

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

@dataclass
class SliceExpr(Expression):
    """切片表达式 obj[start:end] 或 obj[start:end:step]"""
    obj: Expression = None
    start: Expression = None  # None 表示省略
    end: Expression = None
    step: Expression = None
    line: int = 0
    column: int = 0

@dataclass
class TernaryExpr(Expression):
    """三元表达式 cond ? then : else"""
    condition: Expression = None
    then_expr: Expression = None
    else_expr: Expression = None
    line: int = 0
    column: int = 0

@dataclass
class WalrusExpr(Expression):
    """S2a: 海象赋值表达式 name := value

    表达式级赋值: 求值 value → 绑定 name(已存在则赋值, 否则当前作用域声明)
    → 返回 value 本身。优先级最低(低于三元/管道/逻辑或) —
    `x := a or b` 解析为 `x := (a or b)`。
    """
    name: str = ""
    value: Expression = None
    line: int = 0
    column: int = 0

@dataclass
class AssertStmt(ASTNode):
    """断言语句 assert condition, message"""
    condition: Expression = None
    message: Expression = None
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
class EnumPattern(MatchPattern):
    """枚举路径模式: Direction::North"""
    enum_name: str = ""
    variant: str = ""

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

class YieldSignal(BaseException):
    """yield 信号 — 用于中断函数执行并产出值"""
    def __init__(self, value: RuntimeValue):
        self.value = value

# ── Intent 错误体系（P0.1：调用栈与错误诊断） ──────────

class IntentError(Exception):
    """Intent 错误基类 — 携带源码位置与调用栈快照

    所有穿过解释器边界的错误最终包装为 IntentError,
    使 CLI 能渲染: 错误消息 + 源码行高亮 + Intent 调用链。
    """
    def __init__(self, message: str, line: Optional[int] = None,
                 column: Optional[int] = None, stack: Optional[list] = None,
                 filename: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.stack = stack if stack is not None else []
        self.filename = filename

class ContractViolation(IntentError):
    """契约违反 — Intent 的身份证错误

    requires 未满足(进门被拒)或 ensures 未兑现(出门验货失败)。
    区别于普通运行时错误: 它携带违约条款、期望与实际值,
    因为契约是代码间的社会关系,违约必须指名道姓。
    """
    def __init__(self, message: str, clause: str = "",
                 expected: str = "", actual: str = "", **kwargs):
        super().__init__(message, **kwargs)
        self.clause = clause        # "requires" | "ensures"
        self.expected = expected
        self.actual = actual

class CallFrame:
    """调用栈帧 — 记录一次函数调用的发生处"""
    __slots__ = ('name', 'line', 'column', 'filename', 'scope')

    def __init__(self, name: str, line: int = 0, column: int = 0, filename: str = ""):
        self.name = name
        self.line = line
        self.column = column
        self.filename = filename
        self.scope = None  # EX2: 本帧作用域(异常穿帧时帧快照取本地人用)

    def __repr__(self):
        loc = f"{self.filename}:{self.line}" if self.filename else f"line {self.line}"
        return f"{self.name} ({loc})"


class DebuggerQuit(Exception):
    """调试器主动退出 — 穿透解释器异常包装, 顶层优雅收尾"""


POSTMORTEM_SNAPSHOT = '.intent_postmortem.json'


class Postmortem:
    """EX2: 事后调试器 — 崩溃后的帧检视会话

    与 C7 调试器的分工: Debugger 是事前(打断点逐步走),
    Postmortem 是事后(错误已发生, 栈已冻结, 只检视不执行)。
    帧快照来自异常穿帧时挂在 _intent_frames 上的局部变量链。
    命令: frames 帧列表 | frame N 切帧 | vars 当前帧变量 |
          where 出错位置 | quit 收尾。stdin EOF(非交互)自动收尾。
    """

    def __init__(self, interpreter):
        self.interp = interpreter
        self.current = 0

    def save_snapshot(self, err, frames) -> None:
        """帧快照写盘 — 进程退出后仍可捡回(崩溃不留白)"""
        snapshot = {
            'error': {'type': getattr(err, 'py_type', None) or type(err).__name__,
                      'message': str(err),
                      'line': err.line, 'column': err.column,
                      'filename': err.filename},
            'frames': frames,
            'saved_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
        }
        try:
            with open(POSTMORTEM_SNAPSHOT, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
            print(f"\n💾 帧快照已存档: {POSTMORTEM_SNAPSHOT}"
                  f"(停机后可用任何文本编辑器捡回)")
        except OSError as e:
            print(f"\n⚠️  帧快照存档失败: {e}")

    def show_frames(self, frames) -> None:
        print(f"\n🔎 帧检视(共 {len(frames)} 帧, 从外到内;"
              f" frame N 切帧, vars 看当前帧变量):")
        for i, fr in enumerate(frames):
            marker = "👉" if i == self.current else "  "
            loc = f"{fr.get('filename') or '<?>'}:{fr.get('line')}"
            print(f"  {marker} 帧 #{i} {fr.get('name')} ({loc})")
            if i == self.current:
                for k, v in (fr.get('locals') or {}).items():
                    print(f"        {k} = {v}")

    def command_loop(self, frames) -> None:
        while True:
            try:
                raw = input("(intent-pm) ")
            except EOFError:
                print("[事后调试] 输入结束, 收尾")
                return
            except KeyboardInterrupt:
                print("\n[事后调试] 中断, 收尾")
                return
            cmd = raw.strip()
            if not cmd:
                continue
            parts = cmd.split(None, 1)
            head = parts[0].lower()
            rest = parts[1].strip() if len(parts) > 1 else ""
            if head in ('frames', 'f'):
                self.show_frames(frames)
            elif head in ('frame', 'fr'):
                if not frames:
                    print("[事后调试] 没有帧可切")
                    continue
                try:
                    self.current = max(0, min(len(frames) - 1, int(rest)))
                except ValueError:
                    print("[事后调试] frame 需要帧号: frame 1")
                    continue
                self.show_frames(frames)
            elif head in ('vars', 'v'):
                fr = frames[self.current] if frames else {}
                locs = fr.get('locals') or {}
                print(f"  帧 #{self.current} {fr.get('name', '')} "
                      f"局部变量({len(locs)}):")
                for k, v in locs.items():
                    print(f"    {k} = {v}")
            elif head in ('where', 'w'):
                fr = frames[-1] if frames else {}
                print(f"  出错位置: {fr.get('name', '?')} "
                      f"{fr.get('filename') or '<?>'}:{fr.get('line')}")
            elif head in ('quit', 'q'):
                raise DebuggerQuit()
            elif head in ('help', 'h', '?'):
                print("  命令: frames | frame N | vars | where | quit")
            else:
                print(f"[事后调试] 未知命令: {head} (help 查看命令)")


class Debugger:
    """C7 行级调试器 — 断点/单步/变量检视/调用栈

    挂在 Interpreter.execute_statement 入口: 每条语句执行前检查
    当前行是否命中断点或处于单步模式, 命中即打印位置并进入命令循环。
    stdin EOF(非交互/管道场景)时自动放行至程序终止 — 保证 exit 0。
    普通执行路径 self.debugger 为 None, 零开销。
    """

    def __init__(self, interpreter):
        self.interp = interpreter
        self.breakpoints: set = set()
        self.stepping = False
        self._banner_shown = False

    # ── hook: 每条语句执行前由 execute_statement 调用 ──
    def check(self, stmt) -> None:
        """行命中(断点/单步) → 展示位置 + 命令循环"""
        line = getattr(stmt, 'line', None)
        if not line:
            return
        if line in self.breakpoints or self.stepping:
            self._show_location(line)
            self.command_loop()

    def _show_location(self, line: int) -> None:
        src = ""
        if self.interp.source_lines and 0 < line <= len(self.interp.source_lines):
            src = self.interp.source_lines[line - 1].strip()
        name = self.interp.current_filename or "<stdin>"
        print(f"🛑 断点 {name}:{line}  {src}")

    def show_banner(self) -> None:
        if self._banner_shown:
            return
        self._banner_shown = True
        print("╔══ Intent 调试器 (C7) ═════════════════════════════╗")
        print("║ 命令: break N 设断点   | step 单步   | continue 放行 ║")
        print("║       print EXPR 变量检视 | vars 当前变量           ║")
        print("║       backtrace 调用栈 | breakpoints 断点列表       ║")
        print("║       quit 退出调试                                  ║")
        print("╚═══════════════════════════════════════════════════╝")

    def command_loop(self) -> None:
        """断点命令循环 — 返回即放行(step/continue/EOF); quit 抛 DebuggerQuit"""
        while True:
            try:
                raw = input("(intent-dbg) ")
            except EOFError:
                print("[调试器] 命令输入结束, 放行执行至程序终止")
                self.stepping = False
                return
            except KeyboardInterrupt:
                print("\n[调试器] 中断, 放行执行")
                self.stepping = False
                return
            cmd = raw.strip()
            if not cmd:
                continue
            parts = cmd.split(None, 1)
            head = parts[0].lower()
            rest = parts[1].strip() if len(parts) > 1 else ""
            if head in ('step', 's'):
                self.stepping = True
                return
            elif head in ('continue', 'c'):
                self.stepping = False
                return
            elif head in ('break', 'b'):
                self._cmd_break(rest)
            elif head in ('delete', 'd'):
                self._cmd_delete(rest)
            elif head in ('print', 'p'):
                self._cmd_print(rest)
            elif head in ('backtrace', 'bt'):
                self._cmd_backtrace()
            elif head in ('vars', 'v'):
                self._cmd_vars()
            elif head in ('breakpoints', 'bl'):
                self._cmd_list()
            elif head in ('quit', 'q'):
                raise DebuggerQuit()
            elif head in ('help', 'h', '?'):
                self.show_banner()
            else:
                print(f"[调试器] 未知命令: {head} (help 查看命令)")

    def _cmd_break(self, rest: str) -> None:
        try:
            line_no = int(rest)
        except ValueError:
            print("[调试器] break 需要行号: break 12")
            return
        self.breakpoints.add(line_no)
        print(f"[调试器] 断点已设: 第 {line_no} 行")

    def _cmd_delete(self, rest: str) -> None:
        if not rest:
            self.breakpoints.clear()
            print("[调试器] 已清空全部断点")
            return
        try:
            line_no = int(rest)
        except ValueError:
            print("[调试器] delete 需要行号: delete 12")
            return
        self.breakpoints.discard(line_no)
        print(f"[调试器] 断点已删: 第 {line_no} 行")

    def _cmd_list(self) -> None:
        if not self.breakpoints:
            print("[调试器] 当前无断点")
            return
        print("[调试器] 断点: " + ", ".join(str(n) for n in sorted(self.breakpoints)))

    def _cmd_print(self, expr_src: str) -> None:
        """变量检视 — 在当前作用域求值任意 Intent 表达式"""
        if not expr_src:
            print("[调试器] print 需要表达式: print x + 1")
            return
        try:
            # 表达式语句要求分号结尾 — 调试输入补一个, 含分号则不重复加
            src = expr_src if expr_src.rstrip().endswith(';') else expr_src + ';'
            tokens = Lexer(src).tokenize()
            program = Parser(tokens, src).parse()
            stmts = program.statements
            if not stmts or not isinstance(stmts[0], Expression):
                print(f"[调试器] 无法解析为表达式: {expr_src}")
                return
            val = self.interp.evaluate_expression(stmts[0])
            print(f"  {expr_src} = {self.interp._value_to_str(val)}")
        except Exception as e:
            print(f"[调试器] 求值失败: {e}")

    def _cmd_backtrace(self) -> None:
        frames = self.interp.call_stack
        if not frames:
            print("[调试器] 调用栈为空")
            return
        for i, fr in enumerate(reversed(frames)):
            print(f"  #{i} {fr.name}  at {fr.filename}:{fr.line}")

    def _cmd_vars(self) -> None:
        symbols = getattr(self.interp.current_scope, 'symbols', {})
        if not symbols:
            print("[调试器] 当前作用域无变量")
            return
        for name, val in symbols.items():
            print(f"  {name} = {self.interp._value_to_str(val)}")


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
class EnumDef(ASTNode):
    """枚举声明 enum Direction { North, East, South, West }"""
    name: str = ""
    variants: List[str] = field(default_factory=list)  # ["North", "East", ...]

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

class AnyType(Type):
    """任意类型(放宽类型检查)"""

    def __init__(self):
        super().__init__("Any")

    def can_assign_from(self, other: Type) -> bool:
        return True

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

class EnumType(Type):
    """枚举类型"""

    def __init__(self, name: str, variants: List[str]):
        super().__init__(name)
        self.variants = variants

    def can_assign_from(self, other: Type) -> bool:
        return isinstance(other, EnumType) and other.name == self.name


class ChannelType(Type):
    """CC2: 通道类型 — 并发通信的原语类型"""

    def __init__(self):
        super().__init__("Channel")


class MockType(Type):
    """TQ1: 测试替身类型"""

    def __init__(self):
        super().__init__("Mock")

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
        """创建副本 — 保持子类形态

        P3.1 修复: 原实现只覆盖标量与 List, DictValue 等落入 else
        退化为 RuntimeValue 基类 — 参数绑定(arg_value.copy())后
        isinstance(x, DictValue) 全判 False, dict 传参即崩。
        标量/List/Dict 深拷贝; 实例/函数/类保持引用语义;
        Result/Error 委托各自 copy。
        """
        if isinstance(self, (IntValue, FloatValue, StringValue, BoolValue)):
            return type(self)(self.value)
        if isinstance(self, NoneValue):
            return NoneValue()
        if isinstance(self, ListValue):
            return ListValue([v.copy() for v in self.value], self.type)
        if isinstance(self, DictValue):
            new_entries = {k: (v.copy() if isinstance(v, RuntimeValue) else v)
                           for k, v in self.value.items()}
            key_t = self.type.key_type if isinstance(self.type, DictType) else None
            val_t = self.type.value_type if isinstance(self.type, DictType) else None
            return DictValue(new_entries, key_t, val_t)
        if isinstance(self, (InstanceValue, FunctionValue, ClassValue)):
            return self  # 对象/函数/类是引用语义
        if isinstance(self, (ChannelValue, MockValue)):
            return self  # CC2 通道/TQ1 mock: 共享句柄, 引用语义
        if isinstance(self, (LibValue, ForeignFuncValue, StructValue)):
            return self  # I1 FFI: 库/函数句柄/结构体(指针语义)均引用共享
        if isinstance(self, (PyFuncValue, PyObjectValue)):
            return self  # I2a Python 桥: 函数句柄/不透明对象均引用共享
        if isinstance(self, (ResultValue, ErrorValue)):
            return self.copy()  # 委托各自实现
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

# ── MM1: 容器对象注册表(引用计数观测 + 循环回收触发)─────────
# 设计文档: docs/memory_design.md
# 策略(寄生期 v3.0): 容器值(List/Dict/Instance)创建即登记弱引用;
# 循环垃圾委托宿主 CPython 分代 GC — 注册表提供观测与触发入口。
# 不变量: 注册表持有弱引用, 自身不拉长任何对象寿命。
# v3.5(M2 属性优化) / v4.0(M3 JIT) 自持 GC 时必须与此表同构。

import weakref as _weakref
import gc as _gc


class _ObjectRegistry:
    """意图运行时容器对象注册表(MM1 首期)"""

    __slots__ = ("_refs", "alloc_total", "reclaim_total", "alloc_by_type")

    def __init__(self):
        self._refs = []            # weakref.ref — 目标死亡即失效
        self.alloc_total = 0       # 累计创建容器数
        self.reclaim_total = 0     # 累计回收容器数(观测值)
        self.alloc_by_type = {}    # M4: 按类型的累计分配数(分配热点)

    def register(self, obj) -> None:
        self.alloc_total += 1
        # M4: 分配热点按容器类型聚合(实例取类名, 其余取类型名)
        if isinstance(obj, InstanceValue):
            t = obj.klass.name if obj.klass is not None else 'Instance'
        else:
            t = obj.get_type().name if hasattr(obj, 'get_type') else type(obj).__name__
        self.alloc_by_type[t] = self.alloc_by_type.get(t, 0) + 1
        self._refs.append(_weakref.ref(obj))
        if len(self._refs) > 4096:  # 防膨胀: 定期修剪死亡弱引用
            self._prune()

    def _prune(self) -> None:
        self._refs = [r for r in self._refs if r() is not None]

    def live(self) -> int:
        self._prune()
        return len(self._refs)

    def stats(self) -> dict:
        self._prune()
        by_type = {}
        for r in self._refs:
            o = r()
            if o is not None:
                t = o.get_type().name if hasattr(o, 'get_type') else type(o).__name__
                by_type[t] = by_type.get(t, 0) + 1
        return {"live": len(self._refs), "alloc_total": self.alloc_total,
                "reclaim_total": self.reclaim_total, "by_type": by_type}

    def collect(self) -> int:
        before = self.live()
        _gc.collect()
        after = self.live()
        gained = max(0, before - after)
        self.reclaim_total += gained
        return gained


OBJECT_REGISTRY = _ObjectRegistry()

# ── M2: 实例属性访问缓存统计(模块级 — 跨实例/跨类聚合) ──
# 树遍历执行器的内联缓存等价物: 实例形状(字段+方法集)创建后即稳定,
# get() 命中走 _cache 免去 fields/methods 两次查找; set() 写透同步。
# 统计供 cache_stats()/cache_reset() 内置观测(测试与微基准用)。
# 近似计数: 并发 spawn 下非原子, 仅作诊断不作正确性依据。
_ATTR_CACHE_STATS = {"hits": 0, "misses": 0}


class FunctionProfiler:
    """M4: 函数级剖析器 — 调用次数/累计时间/自身时间(cProfile 等价切片)

    挂接点: Interpreter.execute_function 与 _execute_method 的帧入出
    (profiler 为 None 时热路径仅多一次属性判断, 零 instrumentation 开销)。
    自身时间 = 累计 − 直接子调用耗时(子调用经 _stack 逐层上报)。
    时间基准 time.perf_counter — 单调时钟, 不受系统时钟调整影响。
    """
    __slots__ = ("stats", "_stack")

    def __init__(self):
        self.stats = {}    # 函数名 → [调用次数, 累计秒, 自身秒]
        self._stack = []   # [函数名, t0, 子调用累计秒]

    def enter(self, name: str):
        self._stack.append([name, time.perf_counter(), 0.0])

    def exit(self, name: str):
        t1 = time.perf_counter()
        if not self._stack:
            return  # 防御: 出口多于入口(异常路径理论不可达, finally 保证配对)
        frame = self._stack.pop()
        dt = t1 - frame[1]
        st = self.stats.get(name)
        if st is None:
            st = self.stats[name] = [0, 0.0, 0.0]
        st[0] += 1
        st[1] += dt
        st[2] += dt - frame[2]
        if self._stack:
            self._stack[-1][2] += dt

    def report(self, wall: float = None) -> str:
        """渲染函数级报告 — 按累计时间降序"""
        lines = []
        lines.append("🔬 函数级剖析报告（M4 — cProfile 等价切片）")
        lines.append(f"  {'函数':<28}{'调用':>6}{'累计(s)':>12}{'自身(s)':>12}")
        lines.append("  " + "-" * 58)
        rows = sorted(self.stats.items(), key=lambda kv: (-kv[1][1], kv[0]))
        for name, (calls, cum, self_t) in rows:
            lines.append(f"  {name:<28}{calls:>6}{cum:>12.6f}{self_t:>12.6f}")
        lines.append("  " + "-" * 58)
        lines.append(f"  函数总数: {len(rows)}")
        if wall is not None:
            lines.append(f"  墙钟总耗时: {wall:.6f}s（含未 instrumentation 的顶层语句）")
        return "\n".join(lines)


def render_mem_profile() -> str:
    """M4: 内存分配热点报告 — 基于 MM1 对象注册表(OBJECT_REGISTRY)

    分配计数按容器类型聚合(实例/列表/字典); 存活数经弱引用修剪,
    累计分配反映整个运行期的构造压力 — 分配热点一眼可见。
    """
    s = OBJECT_REGISTRY.stats()
    lines = []
    lines.append("🧬 内存分配剖析（M4 — MM1 注册表切片）")
    lines.append(f"  累计分配容器: {s['alloc_total']} | 当前存活: {s['live']} | 已回收: {s['reclaim_total']}")
    lines.append(f"  {'类型':<20}{'存活':>8}{'累计分配':>10}")
    lines.append("  " + "-" * 40)
    live_by_type = s.get("by_type", {})
    alloc_by_type = OBJECT_REGISTRY.alloc_by_type
    for t in sorted(alloc_by_type, key=lambda k: -alloc_by_type[k]):
        lines.append(f"  {t:<20}{live_by_type.get(t, 0):>8}{alloc_by_type[t]:>10}")
    if not alloc_by_type:
        lines.append("  （无容器分配记录）")
    return "\n".join(lines)


class CoverageTracker:
    """E3/Q2: 覆盖率打点器 — 语句覆盖率(E3) + 契约覆盖率(Q2)

    语句口径(与 Python coverage 的语句语义对齐的最小切片):
    分子 = 执行过的非表达式语句节点行(execute_statement 入口打点);
    分母 = AST 全量遍历的非表达式语句节点行。裸表达式语句
    (如 f();)不计分母 — 边界如实记录, 不假装精确。
    契约口径(Q2, Python 没有的维度): requires/ensures 逐子句计数 —
    定义即入分母, 求值即入分子(违约子句也算执行过)。
    """
    __slots__ = ("stmt_hits", "stmt_total", "req_hit", "req_total",
                 "ens_hit", "ens_total", "with_contracts")

    def __init__(self, with_contracts: bool = False):
        self.stmt_hits: set = set()     # (filename, line)
        self.stmt_total: set = set()
        self.req_hit: set = set()       # 执行过的 requires 子句(AST 节点 id)
        self.req_total = 0
        self.ens_hit: set = set()       # 执行过的 ensures 子句
        self.ens_total = 0
        self.with_contracts = with_contracts

    def mark_stmt(self, filename: str, line: int):
        if line:
            self.stmt_hits.add((filename, line))

    def mark_contract(self, kind: str, clause) -> None:
        """Q2: 契约子句按身份计一次(多次调用不重复计 — 覆盖率不是执行次数)"""
        if kind == 'requires':
            self.req_hit.add(id(clause))
        elif kind == 'ensures':
            self.ens_hit.add(id(clause))

    def count_program(self, program, filename: str):
        """执行前遍历 AST: 累计语句分母与契约分母"""
        for node in _walk_ast(program):
            if isinstance(node, FunctionDef):
                self.req_total += len(getattr(node, 'requires', None) or [])
                self.ens_total += len(getattr(node, 'ensures', None) or [])
            if (isinstance(node, ASTNode) and not isinstance(node, Expression)
                    and getattr(node, 'line', 0)):
                self.stmt_total.add((filename, node.line))

    def report(self) -> str:
        hit_n = len(self.stmt_hits & self.stmt_total)
        total_n = len(self.stmt_total)
        pct = (hit_n * 100 // total_n) if total_n else 100
        missed = sorted(line for (fn, line) in (self.stmt_total - self.stmt_hits))
        lines = []
        lines.append("📊 覆盖率报告（E3 语句级切片）")
        lines.append(f"  语句覆盖率: {hit_n}/{total_n} ({pct}%)")
        if missed:
            show = ", ".join(str(m) for m in missed[:20])
            more = f" ...等{len(missed)}行" if len(missed) > 20 else ""
            lines.append(f"  未覆盖行: {show}{more}")
        if self.with_contracts:
            req_n, ens_n = len(self.req_hit), len(self.ens_hit)
            total_c = self.req_total + self.ens_total
            cp = (req_n + ens_n) * 100 // total_c if total_c else 100
            rp = req_n * 100 // self.req_total if self.req_total else 100
            ep = ens_n * 100 // self.ens_total if self.ens_total else 100
            lines.append(f"  契约覆盖率: {req_n + ens_n}/{total_c} ({cp}%)")
            lines.append(f"    requires 子句: {req_n}/{self.req_total} ({rp}%)")
            lines.append(f"    ensures  子句: {ens_n}/{self.ens_total} ({ep}%)")
        return "\n".join(lines)


class ListValue(RuntimeValue):
    """列表值"""

    def __init__(self, values: List[RuntimeValue], element_type: Type = None):
        if element_type is None:
            element_type = IntType() if not values else values[0].get_type()
        super().__init__(ListType(element_type), values)
        OBJECT_REGISTRY.register(self)  # MM1: 创建即登记

    def __str__(self):
        items = ", ".join(str(v) for v in self.value)
        return f"[{items}]"

    def get(self, index: int) -> RuntimeValue:
        # 支持负数索引
        if index < 0:
            index = len(self.value) + index
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

# ── P1.4: Intent 异常层级(错误作为一等值被捕获) ──────────

# Python 异常名 → Intent 异常类型名
PY_TO_INTENT_EXC = {
    'ContractViolation': 'ContractError',
    'AssertionError': 'AssertError',
    'ValueError': 'ValueError',
    'TypeError': 'TypeError',
    'IndexError': 'IndexError',
    'KeyError': 'KeyError',
    'ZeroDivisionError': 'ZeroDivisionError',
    'NameError': 'NameError',
    'RuntimeError': 'RuntimeError',
    'SyntaxError': 'SyntaxError',
    'ImportError': 'ImportError',
}

@dataclass
class ErrorValue(RuntimeValue):
    """Intent 异常值 — 烦恼即菩提: 错误被捕获为一等值

    成员: .type(异常类型名) .message(消息) .stack(Intent 调用链) .__cause__(起因)
    catch 可按类型分流: catch e: ContractError { ... }
    """
    err_type: str = "RuntimeError"
    message: str = ""
    stack: List['RuntimeValue'] = field(default_factory=list)
    cause: Optional['ErrorValue'] = None   # EX1: raise X from Y 的因果链

    def __init__(self, err_type: str = "RuntimeError", message: str = "",
                 stack=None, cause: 'Optional[ErrorValue]' = None):
        super().__init__(StringType(), message)
        self.err_type = err_type
        self.message = message
        self.stack = stack if stack is not None else []
        self.cause = cause

    def __str__(self):
        return f"{self.err_type}: {self.message}"

    def __repr__(self):
        return str(self)

    def copy(self) -> 'ErrorValue':
        return ErrorValue(self.err_type, self.message, list(self.stack),
                          self.cause)


class IntentRaise(Exception):
    """raise 语句的抛出载体(EX1) — 携带 Intent 错误值

    穿帧时由 _execute_function 快照调用栈; 到 catch 时经 _make_error_value
    原样还原为 ErrorValue(类型/消息/因果链不丢); 到顶层由 wrap_intent_error
    接住渲染异常链。
    """
    def __init__(self, error_value: 'ErrorValue'):
        super().__init__(f"{error_value.err_type}: {error_value.message}")
        self.error_value = error_value


class _SpawnTask:
    """CC1: 一个派生的并发任务(线程 + 错误捕获)

    演示级实现(Python threading): 每个任务跑在独立 Interpreter 上,
    闭包作用域经 FunctionValue 共享 — GIL 下对不相交数据的并发访问安全,
    共享可变状态的竞争由使用者自己同步(channel 是 CC2 的课题)。
    异常不沉没: 捕获后挂在 task.error, scope join 时重抛。
    """
    def __init__(self, callee, args: list):
        self.callee = callee
        self.args = args
        self.error = None
        self._thread = None

    def _run(self):
        try:
            if isinstance(self.callee, FunctionValue):
                worker = Interpreter()
                worker.execute_function(self.callee, list(self.args))
            elif callable(self.callee):
                self.callee(list(self.args))
        except Exception as e:  # 任务异常: 捕获, 留到 join 处裁决
            self.error = e

    def start(self):
        self._thread = threading.Thread(target=self._run,
                                        name=f"intent-spawn", daemon=False)
        self._thread.start()

    def join(self):
        if self._thread is not None:
            self._thread.join()


class ChannelClosedError(Exception):
    """CC2: 通道已关闭 — 发送到关闭通道, 或从关闭且排空的通道接收"""


class ChannelValue(RuntimeValue):
    """CC2: 线程安全通道(Go channel 语义的演示级子集)

    - chan() 无界缓冲; chan(n) 容量 n(满则发送阻塞)
    - ch <- v 发送(阻塞直至入队); <- ch 接收(空则阻塞等待)
    - close(ch) 关闭: 此后发送报错; 接收排空剩余数据后抛
      ChannelClosedError — 显式失败, 不返回哑值(契约哲学)
    底层 queue.Queue: 阻塞与线程安全由标准库保证, 不自己造锁。
    引用语义: 传参/赋值共享同一通道(copy() 返回自身)。
    """

    def __init__(self, capacity: int = 0):
        super().__init__(ChannelType(), None)
        self.capacity = capacity
        self._queue: 'queue.Queue' = queue.Queue(maxsize=capacity)
        self._closed = False
        self._close_lock = threading.Lock()

    def send(self, value: 'RuntimeValue') -> None:
        with self._close_lock:
            if self._closed:
                raise ChannelClosedError("向已关闭的 channel 发送")
        self._queue.put(value)  # 缓冲满则阻塞 — 与 Go 一致

    def recv(self) -> 'RuntimeValue':
        # 轮询等待: 关闭信号到时要能立即观察到(纯 get() 阻塞无法感知 close)
        while True:
            try:
                return self._queue.get(timeout=0.02)
            except queue.Empty:
                with self._close_lock:
                    if self._closed and self._queue.empty():
                        raise ChannelClosedError(
                            "channel 已关闭且无剩余数据(关闭语义: 排空即止)")

    def close(self) -> None:
        with self._close_lock:
            self._closed = True

    def __str__(self):
        state = "closed" if self._closed else "open"
        cap = "unbounded" if self.capacity == 0 else f"cap={self.capacity}"
        return f"<channel {state} {cap}>"


class MockValue(RuntimeValue):
    """TQ1: 测试替身 — 记录调用, 返回预设值

    用法: m = mock("名"); m(1, 2); mock_calls(m) → [[1, 2]];
    mock_return(m, v) 预设返回值。不验证参数(那是 Q3 属性测试的活)。
    引用语义: copy() 返回自身。
    """

    def __init__(self, name: str = "mock"):
        super().__init__(MockType(), None)
        self.name = name
        self.calls: list = []          # List[List[RuntimeValue]]
        self.return_value = NoneValue()

    def __call__(self, args: list) -> 'RuntimeValue':
        self.calls.append([a.copy() if isinstance(a, RuntimeValue) else a
                           for a in args])
        return self.return_value

    def __str__(self):
        return f"<mock {self.name} calls={len(self.calls)}>"


# ── I1: C ABI FFI（ctypes 背载的最小切片）────────────────
# 设计: 声明外部函数 + 加载 .dll/.so + 结构体映射。
# ctypes 是 CPython 自己的答案 — 寄生期复用宿主 ABI, 不自己造桥。
# 类型映射: Int→c_int, Float→c_double, Str→c_char_p(utf-8),
#           Bool→c_int, Ptr→c_void_p, Struct→按引用传(ctypes 实例语义)。
# 完整 I1 剩余(见 ROADMAP_LONGTERM 维度 8): 回调(CFUNCTYPE)/数组/
#   联合/varargs/头文件解析/foreign 语法糖 — 最小切片已 note 断点。

_FFI_SCALARS = {
    'Int': ctypes.c_int,
    'Float': ctypes.c_double,
    'Str': ctypes.c_char_p,
    'Bool': ctypes.c_int,
    'Ptr': ctypes.c_void_p,
}

# restype 映射(与 _FFI_SCALARS 的差集: Void→None 即 C void)
_FFI_RESTYPES = dict(_FFI_SCALARS)
_FFI_RESTYPES['Void'] = None


def _ffi_check_type_name(tname: str) -> None:
    """FFI 类型名白名单: 标量或 Struct — 声明期即失败, 不拖到调用期"""
    if tname not in _FFI_SCALARS and tname != 'Struct':
        raise ValueError(
            f"未知 FFI 类型: {tname}(可用: Int/Float/Str/Bool/Ptr/Struct)")


def _ffi_to_c(val: 'RuntimeValue', tname: str):
    """Intent 值 → C 实参

    'Struct' 语义 = 指向结构体的指针(Win32 出参/入参指针模式):
    未声明 argtypes 的 ctypes 函数会把 Structure 实例按值传递,
    必须显式 byref(实测 GetCursorPos: 传实例 ret=0, byref ret=1)。
    """
    if tname == 'Struct':
        if not isinstance(val, StructValue):
            raise TypeError(f"FFI Struct 参数期望结构体, 得到 {val.type}")
        return ctypes.byref(val.instance)  # 指针语义: 外部函数可写回
    if tname == 'Int':
        if not isinstance(val, IntValue):
            raise TypeError(f"FFI Int 参数期望整数, 得到 {val.type}")
        return ctypes.c_int(int(val.value))
    if tname == 'Float':
        if isinstance(val, IntValue):
            return ctypes.c_double(float(val.value))
        if not isinstance(val, FloatValue):
            raise TypeError(f"FFI Float 参数期望浮点, 得到 {val.type}")
        return ctypes.c_double(val.value)
    if tname == 'Str':
        if not isinstance(val, StringValue):
            raise TypeError(f"FFI Str 参数期望字符串, 得到 {val.type}")
        return val.value.encode('utf-8')
    if tname == 'Bool':
        if not isinstance(val, BoolValue):
            raise TypeError(f"FFI Bool 参数期望布尔, 得到 {val.type}")
        return ctypes.c_int(1 if val.value else 0)
    if tname == 'Ptr':
        if isinstance(val, StructValue):
            return ctypes.byref(val.instance)
        if isinstance(val, IntValue):
            return ctypes.c_void_p(int(val.value))
        raise TypeError(f"FFI Ptr 参数期望结构体或整数地址, 得到 {val.type}")
    raise ValueError(f"未知 FFI 类型: {tname}")


def _ffi_from_c(ret, tname: str) -> 'RuntimeValue':
    """C 返回值 → Intent 值"""
    if tname == 'Void':
        return NoneValue()
    if tname == 'Int' or tname == 'Bool':
        return IntValue(int(ret))
    if tname == 'Float':
        return FloatValue(float(ret))
    if tname == 'Str':
        if ret is None:
            return StringValue("")
        if isinstance(ret, bytes):
            return StringValue(ret.decode('utf-8', 'replace'))
        return StringValue(str(ret))
    if tname == 'Ptr':
        return IntValue(int(ctypes.cast(ret, ctypes.c_void_p).value or 0))
    raise ValueError(f"未知 FFI 返回类型: {tname}")


class LibValue(RuntimeValue):
    """I1: 外部动态库句柄(ffi_load 返回)

    持有 ctypes.CDLL; 路径原样保留供报错定位。
    引用语义: copy() 返回自身(句柄共享)。
    """

    def __init__(self, path: str, handle):
        super().__init__(AnyType(), path)
        self.path = path
        self.handle = handle

    def __str__(self):
        return f"<ffi-lib {self.path}>"


class ForeignFuncValue(RuntimeValue):
    """I1: 外部函数(ffi_func 声明) — 可调用值

    走 CallExpr 的 callable 分发(与 mock 同路); 参数个数/类型在
    调用期校验, 声明期校验符号存在性与类型名白名单。
    引用语义: copy() 返回自身。
    """

    def __init__(self, lib: 'LibValue', name: str, restype: str, argtypes: list):
        super().__init__(AnyType(), f"{lib.path}!{name}")
        self.lib = lib
        self.name = name
        self.restype = restype
        self.argtypes = list(argtypes)
        try:
            self._fn = getattr(lib.handle, name)
        except AttributeError:
            raise RuntimeError(
                f"FFI 声明失败: 库 {lib.path} 中不存在符号 {name}")
        # restype 必须在声明期钉死: 默认 c_int 会把指针/字符串返回截断成 int
        self._fn.restype = _FFI_RESTYPES.get(restype, ctypes.c_int)

    def __call__(self, args: list) -> 'RuntimeValue':
        if len(args) != len(self.argtypes):
            raise TypeError(
                f"FFI 函数 {self.name} 期望 {len(self.argtypes)} 个参数, "
                f"得到 {len(args)} 个")
        marshaled = [_ffi_to_c(a, t) for a, t in zip(args, self.argtypes)]
        ret = self._fn(*marshaled)
        return _ffi_from_c(ret, self.restype)

    def __str__(self):
        sig = f"{self.name}({', '.join(self.argtypes)}) -> {self.restype}"
        return f"<ffi-func {sig} @ {self.lib.path}>"


class StructValue(RuntimeValue):
    """I1: C 结构体(ffi_struct 创建)

    fields: name → 类型名(str); instance: ctypes.Structure 实例。
    作实参传外部函数时按引用传递(指针语义 — GetCursorPos 式出参)。
    引用语义: copy() 返回自身(结构体是共享内存, 不是值对象)。
    """

    def __init__(self, fields: dict, instance):
        super().__init__(AnyType(), None)
        self.fields = dict(fields)
        self.instance = instance

    def __str__(self):
        parts = []
        for fname, ft in self.fields.items():
            v = getattr(self.instance, fname)
            parts.append(f"{fname}={v}")
        return f"<ffi-struct {{{', '.join(parts)}}}>"


# ── I2a: Python 互操作桥（寄生期标志, ROADMAP 皇冠）─────────
# import python.X → importlib 加载真 Python 模块, 符号包成桥值。
# 设计: 命名空间挂载(namespace_only) — math.sqrt 可用, 但符号不
# 平扁注入(防遮蔽核心内置, 与 std import 的边界偏差是刻意选择)。
# 编排规则: 标量/列表/字典/None 双向自动; 富对象包 PyObjectValue
# 不透明句柄(可传回 Python, 不可在 Intent 侧探内部)。
# 完整 I2a 剩余(15 人日中的未做部分): 类实例化/关键字参数/
#   Python 回调 Intent/子模块链/pip 三方包 round-trip(requests/numpy)。

def _py_from_intent(v: 'RuntimeValue'):
    """Intent 值 → Python 原生(桥入参)"""
    if isinstance(v, (IntValue, FloatValue, StringValue, BoolValue)):
        return v.value
    if isinstance(v, NoneValue):
        return None
    if isinstance(v, ListValue):
        return [_py_from_intent(x) for x in v.value]
    if isinstance(v, DictValue):
        return {k: _py_from_intent(x) for k, x in v.value.items()}
    if isinstance(v, PyObjectValue):
        return v.obj
    raise TypeError(
        f"python 桥暂不支持把 {v.type} 传进 Python"
        "(标量/列表/字典/None/桥对象可传)")


def _py_to_intent(x) -> 'RuntimeValue':
    """Python 原生 → Intent 值(桥返回)"""
    if x is None:
        return NoneValue()
    if isinstance(x, bool):  # bool 须先于 int(Python bool 是 int 子类)
        return BoolValue(x)
    if isinstance(x, int):
        return IntValue(x)
    if isinstance(x, float):
        return FloatValue(x)
    if isinstance(x, str):
        return StringValue(x)
    if isinstance(x, (list, tuple)):
        return ListValue([_py_to_intent(i) for i in x], AnyType())
    if isinstance(x, dict):
        entries = {}
        for k, v in x.items():
            if isinstance(k, bool):
                entries[k] = _py_to_intent(v)
            elif isinstance(k, (int, float, str)):
                entries[k] = _py_to_intent(v)
            else:
                entries[str(k)] = _py_to_intent(v)  # 非标量键字符串化
        return DictValue(entries)
    return PyObjectValue(x)


class PyFuncValue(RuntimeValue):
    """I2a: Python 函数桥值 — 可调用值, 走 CallExpr callable 分发

    异常策略: Python 侧任何异常 → RuntimeError(带原名),
     Intent 侧 catch 到的是显式失败, 不是静默 None。
    引用语义: copy() 返回自身。
    """

    def __init__(self, py_func, qualname: str):
        super().__init__(AnyType(), qualname)
        self.py_func = py_func
        self.qualname = qualname

    def __call__(self, args: list) -> 'RuntimeValue':
        py_args = [_py_from_intent(a) for a in args]
        try:
            ret = self.py_func(*py_args)
        except Exception as e:
            raise RuntimeError(
                f"Python 桥调用 {self.qualname} 失败: "
                f"{type(e).__name__}: {e}")
        return _py_to_intent(ret)

    def __str__(self):
        return f"<py-func {self.qualname}>"


class PyObjectValue(RuntimeValue):
    """I2a: 不透明 Python 对象句柄(类实例/模块/富返回)

    可传回 Python(桥对象原样交接), 不可在 Intent 侧探内部 —
    寄生期边界: 需要深层互操作时走 I2b(Python 调 Intent)或完整 I2a。
    引用语义: copy() 返回自身。
    """

    def __init__(self, obj):
        super().__init__(AnyType(), None)
        self.obj = obj

    def __str__(self):
        text = str(self.obj)
        if len(text) > 80:
            text = text[:77] + "..."
        return f"<py {type(self.obj).__name__}: {text}>"


class SkipTest(Exception):
    """TQ1: skip(reason) — 测试主动跳过(不是失败, 不是通过)"""


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
        OBJECT_REGISTRY.register(self)  # MM1: 创建即登记

    def __str__(self):
        items = ", ".join(f"{k}: {v}" for k, v in self.value.items())
        return f"{{{items}}}"

    def __repr__(self):
        return str(self)

    @staticmethod
    def _norm_key(key):
        """键规范化(P3.1): RuntimeValue → Python 标量

        dict 的 key 统一为 Python 标量形态; 所有入口(get/set/has_key)
        先过这一层, 消除「读用 str 写用 RuntimeValue」的形态分裂。
        """
        if isinstance(key, (StringValue, IntValue, FloatValue, BoolValue)):
            return key.value
        if isinstance(key, RuntimeValue):
            return getattr(key, 'value', None)
        return key

    def get(self, key) -> RuntimeValue:
        return self.value.get(self._norm_key(key))

    def set(self, key, value: RuntimeValue):
        self.value[self._norm_key(key)] = value

    def has_key(self, key) -> bool:
        """检查 key 是否在字典中"""
        return self._norm_key(key) in self.value

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
class EnumValue(RuntimeValue):
    """枚举值"""

    def __init__(self, enum_name: str, variant: str):
        super().__init__(EnumType(enum_name, [variant]), variant)
        self.enum_name = enum_name
        self.variant = variant

    def copy(self):
        return EnumValue(self.enum_name, self.variant)

    def __str__(self):
        return f"{self.enum_name}::{self.variant}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, EnumValue):
            return self.enum_name == other.enum_name and self.variant == other.variant
        return False

    def __hash__(self):
        return hash((self.enum_name, self.variant))

# ── S3: 生成器完整化 — 线程协作式协程(threadlet) ──
# 生成器函数体跑在独立 Python 线程, 经双队列握手实现真惰性:
#   驱动线程(主线程/外层生成器线程): save-ctx → 发信号 → 阻塞等 out_q
#   生成器线程:                       唤醒 → 装 ctx → 跑体 → yield 时
#                                     save-ctx → 出值 → 阻塞等 in_q
# 任意时刻只有一个线程在跑(阻塞握手), 共享解释器状态靠上下文切换时的
# 保存/恢复保证(_GEN_CTX_ATTRS 只换执行态, 不换全局表 — global_scope/
# functions/builtins/modules 本就共享, 正是生成器闭包所见的世界)。

_GEN_DONE = object()  # 驱动侧哨兵: 生成器耗尽(不是语言值, 不跨边界)


class _GenExitSignal(BaseException):
    """S3: 关闭信号 — BaseException 子类, 用户 catch(Exception) 捕不到
    (对齐 Python GeneratorExit: close 不可被业务代码吞掉)"""


# 上下文切换白名单 — 解释器实例上的执行态属性
_GEN_CTX_ATTRS = ('current_scope', 'call_stack', 'return_flag', 'return_value',
                  'break_flag', 'continue_flag', 'current_line', 'current_col',
                  'current_filename', '_spawn_stack', '_import_stack',
                  '_active_gen', 'profiler')


def _save_gen_ctx(interp: 'Interpreter') -> dict:
    return {a: getattr(interp, a, None) for a in _GEN_CTX_ATTRS}


def _restore_gen_ctx(interp: 'Interpreter', ctx: dict) -> None:
    for a, v in ctx.items():
        setattr(interp, a, v)


class GeneratorController:
    """S3: 生成器控制器 — 一个生成器实例 = 一个协程线程 + 一对队列

    驱动侧 API: next() / send(v) / throw(e) / close()
    生成器线程侧: do_yield(v) — 交出值并返回 send 进来的值
    (yield 表达式化: `let x = yield v` 的 x 即 do_yield 的返回值)。
    A3a: async 协程复用本控制器 — 函数返回值存 final_result,
    驱动侧(run)在 _GEN_DONE 时取它。
    """

    def __init__(self, interp: 'Interpreter', func, args,
                 closure_scope=None, instance=None):
        self.interp = interp
        self.func = func
        self.args = args
        self.closure_scope = closure_scope
        self.instance = instance  # 生成器方法: this 的注入目标
        self.final_result = None  # A3a: 协程跑完后的返回值(done 消息同载)
        # 创建瞬间定格驱动侧状态(主线程此刻的执行态)
        self._call_scope = interp.current_scope
        self._stack_snapshot = list(interp.call_stack)
        self._filename = interp.current_filename
        self._line = interp.current_line
        self._col = interp.current_col
        self.out_q = queue.Queue()   # 生成器线程 → 驱动线程
        self.in_q = queue.Queue()    # 驱动线程 → 生成器线程
        self.closing = False
        self.finished = False
        self.started = False
        self._thread = threading.Thread(target=self._run,
                                        name="intent-generator", daemon=True)
        self._thread.start()

    # ── 驱动侧 ──

    def next(self):
        self.started = True
        return self._resume('send', None)

    def send(self, value):
        if not self.started and not isinstance(value, NoneValue):
            raise TypeError(
                "无法向刚创建的生成器发送非 None 值"
                "(首个 next() 或 send(None) 才能启动)")
        self.started = True
        return self._resume('send', value)

    def throw(self, exc):
        if self.finished:
            raise exc  # 对齐 CPython: 耗尽后 throw 直接把异常给调用方
        self.started = True
        return self._resume('throw', exc)

    def close(self):
        if self.finished:
            return
        self.closing = True
        self._resume('close', None)

    def _resume(self, action, value, owner=None):
        """驱动侧握手 — 保存驱动线程上下文 → 发信号 → 等结果 → 恢复"""
        if self.finished:
            if action == 'throw':
                raise value
            return _GEN_DONE
        interp = self.interp
        saved = _save_gen_ctx(interp)
        try:
            self.in_q.put((action, value))
            while True:
                try:
                    kind, val = self.out_q.get(timeout=0.1)
                    break
                except queue.Empty:
                    # 上层(owner)被关闭 → 本层强制收摊, 关闭信号上抛驱动线程
                    if owner is not None and owner.closing:
                        self._shutdown()
                        raise _GenExitSignal()
                    if self.closing:
                        self._shutdown()
                        kind, val = self.out_q.get()
                        break
                    continue
            if kind == 'yield':
                return val
            if kind == 'error':
                raise val
            self.finished = True
            return _GEN_DONE
        finally:
            _restore_gen_ctx(interp, saved)

    def _shutdown(self):
        """强制收摊 — 通知线程结束并有界等待(卡死则留 daemon 线程, 不无限等)"""
        self.closing = True
        try:
            self.in_q.put(('close', None))
        except Exception:
            pass
        deadline = time.time() + 2.0
        while time.time() < deadline:
            try:
                kind, _ = self.out_q.get(timeout=0.1)
                if kind in ('done', 'error'):
                    self.finished = True
                    return
            except queue.Empty:
                continue

    # ── 生成器线程侧 ──

    def _run(self):
        interp = self.interp
        # 首信号前绝不碰共享解释器状态(主线程还在跑)
        kind, val = self.in_q.get()
        if kind == 'throw':
            # 未启动就 throw: 异常在启动点抛出(对齐 Python)
            self.finished = True
            self.out_q.put(('error', val))
            return
        # 安装生成器上下文(从创建瞬间定格的驱动侧状态重建)
        _restore_gen_ctx(interp, {
            'current_scope': self._call_scope,
            'call_stack': list(self._stack_snapshot),
            'return_flag': False, 'return_value': None,
            'break_flag': False, 'continue_flag': False,
            'current_line': self._line, 'current_col': self._col,
            'current_filename': self._filename,
            '_spawn_stack': [], '_import_stack': [],
            '_active_gen': self, 'profiler': None,
        })
        try:
            if self.instance is not None:
                result = interp._execute_method(self.func, self.instance,
                                                self.args, gen_mode=True)
            else:
                result = interp.execute_function(self.func, self.args,
                                                 gen_mode=True)
            self.final_result = result
            self.out_q.put(('done', result))
        except _GenExitSignal:
            self.out_q.put(('done', None))
        except BaseException as e:
            self.out_q.put(('error', e))

    def do_yield(self, value):
        """生成器线程侧: 交出值, 阻塞等驱动线程的下一个动作, 返回 send 值"""
        interp = self.interp
        ctx = _save_gen_ctx(interp)
        self.out_q.put(('yield', value))
        while True:
            try:
                kind, val = self.in_q.get(timeout=0.1)
                break
            except queue.Empty:
                if self.closing:
                    raise _GenExitSignal()
                continue
        _restore_gen_ctx(interp, ctx)
        if kind == 'send':
            return val if val is not None else NoneValue()
        if kind == 'throw':
            raise val
        raise _GenExitSignal()


class _GenIterator:
    """S3: 生成器的 Python 迭代器适配(for/std 消费)"""

    def __init__(self, ctrl: 'GeneratorController'):
        self._ctrl = ctrl

    def __iter__(self):
        return self

    def __next__(self):
        v = self._ctrl.next()
        if v is _GEN_DONE:
            raise StopIteration()
        return v


def _gen_lazy_items(gen: 'GeneratorValue'):
    """S3: for 循环的懒求值源 — 逐项 pull 生成器, 不预取

    提前退出(break/return/异常)时 finally 收摊协程线程 —
    对齐 Python 生成器被 GC 时自动关闭; 线程卡死(如阻塞在 channel)
    时 close 有界返回(2s), 留 daemon 线程, 不无限等。
    """
    ctrl = gen._ctrl
    try:
        while True:
            item = ctrl.next()
            if item is _GEN_DONE:
                return
            yield item
    finally:
        ctrl.close()


class _GenMethod:
    """S3: 生成器方法绑定(g.send / g.throw / g.close) — 可调用值"""

    def __init__(self, gen: 'GeneratorValue', name: str):
        self.gen = gen
        self.name = name

    def __call__(self, args: list):
        ctrl = self.gen._ctrl
        if self.name == 'send':
            if len(args) != 1:
                raise TypeError("send() 期望1个参数")
            v = ctrl.send(args[0])
            if v is _GEN_DONE:
                raise RuntimeError("生成器已耗尽, send 没有递送点")
            return v
        if self.name == 'throw':
            if len(args) != 1:
                raise TypeError("throw() 期望1个参数")
            err = ctrl.interp._coerce_error_value(args[0])
            v = ctrl.throw(IntentRaise(err))
            if v is _GEN_DONE:
                raise RuntimeError("生成器已退出(throw 后无后续产出)")
            return v
        # close
        if args:
            raise TypeError("close() 不接受参数")
        ctrl.close()
        return NoneValue()


class GeneratorValue(RuntimeValue):
    """S3: 生成器值 — 真惰性序列(线程协作式协程背载)"""
    _ctrl: object = None  # GeneratorController

    def __init__(self, ctrl):
        super().__init__(AnyType(), None)
        self._ctrl = ctrl

    def __iter__(self):
        return _GenIterator(self._ctrl)

    def __str__(self):
        return "<generator>"

    def copy(self):
        # 生成器不能复制,返回自身
        return self


class AsyncValue(RuntimeValue):
    """A3a: 协程值 — async 函数调用的惰性结果(线程协作式协程背载)

    与生成器的分别: 生成器交出数据(next 拉值), 协程交出内层协程
    (await 挂起) — 驱动侧 run() 按此协议蹦床, 取 final_result 收摊。
    """
    _ctrl: object = None  # GeneratorController

    def __init__(self, ctrl):
        super().__init__(AnyType(), None)
        self._ctrl = ctrl

    def __str__(self):
        return "<coroutine>"

    def copy(self):
        # 协程不能复制, 返回自身(引用语义, 与生成器一致)
        return self


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

    def all_method_names(self) -> List[str]:
        """X2: 全部方法名(含继承链, 子类覆盖不重复列出)"""
        names = list(self.methods.keys())
        if self.superclass:
            for n in self.superclass.all_method_names():
                if n not in names:
                    names.append(n)
        return names

    def call(self, interpreter, args: List[RuntimeValue]) -> RuntimeValue:
        """实例化类:创建 InstanceValue,调用 init"""
        instance = InstanceValue(self)
        init_method = self.find_method('__init__') or self.find_method('init')
        if init_method:
            # 用 interpreter 执行构造方法
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
        # M2: 属性访问缓存 — 实例形状稳定后重复读取走此表
        self._cache: Dict[str, RuntimeValue] = {}
        OBJECT_REGISTRY.register(self)  # MM1: 创建即登记

    def get(self, name: str) -> Optional[RuntimeValue]:
        """读取字段(M2: 缓存优先 — 命中免 fields/methods 两级查找)"""
        cache = self._cache
        if name in cache:
            _ATTR_CACHE_STATS["hits"] += 1
            return cache[name]
        _ATTR_CACHE_STATS["misses"] += 1
        if name in self.fields:
            v = self.fields[name]
            cache[name] = v
            return v
        # 回退到方法(类创建后方法表即稳定, 可缓存)
        method = self.klass.find_method(name)
        if method:
            cache[name] = method
            return method
        return None

    def set(self, name: str, value: RuntimeValue):
        """设置字段(M2: 写透 — 缓存与 fields 同步, 无失效窗口)"""
        self.fields[name] = value
        self._cache[name] = value

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
        self.defer_stack: List[List['ASTNode']] = []  # defer 语句栈

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

    def get_opt(self, name: str):
        """获取变量值,不存在返回 None (不抛异常)"""
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.get_opt(name)
        return None

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
            # Q2: 契约覆盖率 — 子句进入验证即计执行(违约/异常也算执行过)
            tracker = getattr(self.interpreter, 'coverage', None)
            if tracker is not None:
                tracker.mark_contract('requires', condition)
            try:
                result = self.interpreter.evaluate_expression(condition, context)
                if not (isinstance(result, BoolValue) and result.value):
                    self.error_messages.append(f"前置条件{i+1}失败: {self.expr_to_str(condition)}")
                    all_passed = False
            except Exception as e:
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
            # Q2: 契约覆盖率 — 子句进入验证即计执行
            tracker = getattr(self.interpreter, 'coverage', None)
            if tracker is not None:
                tracker.mark_contract('ensures', condition)
            try:
                eval_result = self.interpreter.evaluate_expression(condition, context)
                if not (isinstance(eval_result, BoolValue) and eval_result.value):
                    self.error_messages.append(f"后置条件{i+1}失败: {self.expr_to_str(condition)}")
                    all_passed = False
            except Exception as e:
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
            return f"{self.expr_to_str(expr.callee)}({args})" if hasattr(expr, 'callee') and expr.callee else f"{expr.func}({args})"
        elif isinstance(expr, MemberAccess):
            return f"{self.expr_to_str(expr.obj)}.{expr.member}"
        elif isinstance(expr, SubscriptExpr):
            return f"{self.expr_to_str(expr.obj)}[{self.expr_to_str(expr.index)}]"
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
        self.symbols = {}      # 模块内所有符号
        self.exports = {}      # 导出给外部的符号
        self.explicit_exports = set()  # P2.1: export 语句显式声明的名字
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

                # 收集模块中的所有符号
                for name, value in module_scope.symbols.items():
                    module.add_symbol(name, value)
                    # 显式 export 声明存在时, 只导出声明过的名字(P2.1);
                    # 无声明则维持全量导出(兼容旧模块)
                    if not module.explicit_exports or name in module.explicit_exports:
                        module.add_export(name, value)

                # 也收集函数定义
                for name, func_def in self.interpreter.functions.items():
                    if name not in ['main']:
                        if not module.explicit_exports or name in module.explicit_exports:
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
        # ── P0.1: Intent 级调用栈 ──
        # 每个 CallFrame 记录一次函数调用的发生处(函数名/行/列/文件)
        self.call_stack: list = []
        self.current_filename: str = ""
        # ── P0.4: 命令行参数(args() 内置读取) ──
        self.cli_args: list = []
        # ── CC1: 结构化并发 — 嵌套 scope 的任务表栈 ──
        self._spawn_stack: list = []
        # ── P1.3a: 类型别名表(透明同义词) ──
        self.type_aliases: Dict[str, str] = {}
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
        # ── 枚举注册表 ──
        self.enum_registry: Dict[str, List[str]] = {}  # enum_name → [variants]
        # ── 导入栈 (循环依赖检测) ──
        self._import_stack: List[str] = []
        # ── C7: 调试器挂载点(仅 --debug 模式启用; 普通执行为 None 零开销) ──
        self.debugger = None
        # ── M4: 函数级剖析器(仅 --profile 模式启用; None 时零开销) ──
        self.profiler = None
        # ── E3/Q2: 覆盖率打点器(仅 --coverage 模式启用; None 时零开销) ──
        self.coverage = None
        # ── S3: 当前协程线程的生成器控制器(主线程为 None) ──
        # yield 经它握手; 上下文切换时随 _GEN_CTX_ATTRS 保存/恢复
        self._active_gen = None

    def _exit_scope(self, old_scope: 'Scope'):
        """退出当前作用域，执行 defer 栈"""
        # 逆序执行 defer
        while self.current_scope.defer_stack:
            defer_body = self.current_scope.defer_stack.pop()
            for s in defer_body:
                self.execute_statement(s)
        self.current_scope = old_scope

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
            # Resolver 错误静默记录,不打印 — 运行时错误已足够定位问题
        except ImportError:
            # Resolver 模块不存在时静默跳过
            pass
        except Exception:
            # Resolver 异常静默,不打断程序执行
            pass

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
            # X3: dunder 协议入口
            'next': self._builtin_next,
            'repr': self._builtin_repr,
            # M2: 属性访问缓存诊断
            'cache_stats': self._builtin_cache_stats,
            'cache_reset': self._builtin_cache_reset,
            # X2: 反射内置
            'getattr': self._builtin_getattr,
            'setattr': self._builtin_setattr,
            'hasattr': self._builtin_hasattr,
            'dir': self._builtin_dir,
            'callable': self._builtin_callable,
            'assert': self._builtin_assert,
            'args': self._builtin_args,
            'keys': self._builtin_keys,
            'values': self._builtin_values,
            'push': self._builtin_push,
            'pop': self._builtin_pop,
            'insert': self._builtin_insert,
            'remove_at': self._builtin_remove_at,
            'enumerate': self._builtin_enumerate,
            'zip': self._builtin_zip,
            'range': self._builtin_range,
            'run': self._builtin_run,
            'abs': self._builtin_abs,
            'min': self._builtin_min,
            'max': self._builtin_max,
            'sum': self._builtin_sum,
            'reversed': self._builtin_reversed,
            'sorted': self._builtin_sorted,
            'any': self._builtin_any,
            'all': self._builtin_all,
            'contains': self._builtin_contains,
            'type_of': self._builtin_type_of,
            'int': self._builtin_int,
            'float': self._builtin_float,
            'str': self._builtin_str,
            'format': self._builtin_format,
            'bool': self._builtin_bool,
            'type': self._builtin_type,
            'Ok': self._builtin_ok,
            'Err': self._builtin_err,
            'error': self._builtin_error,
            # CC2: 通道通信
            'chan': self._builtin_chan,
            'close': self._builtin_close,
            # I1: C ABI FFI（ctypes 背载最小切片）
            'ffi_load': self._builtin_ffi_load,
            'ffi_func': self._builtin_ffi_func,
            'ffi_struct': self._builtin_ffi_struct,
            'ffi_field_get': self._builtin_ffi_field_get,
            'ffi_field_set': self._builtin_ffi_field_set,
            'ffi_sizeof': self._builtin_ffi_sizeof,
            # TQ1: 测试框架深化
            'skip': self._builtin_skip,
            'expect_error': self._builtin_expect_error,
            'param_cases': self._builtin_param_cases,
            'mock': self._builtin_mock,
            'mock_return': self._builtin_mock_return,
            'mock_calls': self._builtin_mock_calls,
            'mock_call_count': self._builtin_mock_call_count,
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
            'round': self._builtin_round,
            'log': self._builtin_log,
            'exp': self._builtin_exp,
            # 三角函数
            'cos': self._builtin_cos,
            'sin': self._builtin_sin,
            'tan': self._builtin_tan,
            'acos': self._builtin_acos,
            'asin': self._builtin_asin,
            'atan': self._builtin_atan,
            'atan2': self._builtin_atan2,
            'pi': self._builtin_pi,
            # std/random
            'random': self._builtin_random,
            'randint': self._builtin_randint,
            # input
            'input': self._builtin_input,
            # string
            'split': self._builtin_split,
            'join': self._builtin_join,
            'trim': self._builtin_trim,
            'starts_with': self._builtin_starts_with,
            'ends_with': self._builtin_ends_with,
            'replace': self._builtin_replace,
            'to_upper': self._builtin_to_upper,
            'to_lower': self._builtin_to_lower,
            'substr': self._builtin_substr,
            'ord': self._builtin_ord,
            'chr': self._builtin_chr,
            # sys
            'version': self._builtin_version,
            # std/fs
            'list_dir': self._builtin_list_dir,
            'file_exists': self._builtin_file_exists,
            'is_dir': self._builtin_is_dir,
            'is_file': self._builtin_is_file,
            'make_dir': self._builtin_make_dir,
            'delete_file': self._builtin_delete_file,
            'file_size': self._builtin_file_size,
            'file_modified': self._builtin_file_modified,
            # std/os
            'env': self._builtin_env,
            'cwd': self._builtin_cwd,
            'ch_dir': self._builtin_ch_dir,
            'shell': self._builtin_shell,
            'platform': self._builtin_platform,
            'path_join': self._builtin_path_join,
            'path_basename': self._builtin_path_basename,
            'path_dirname': self._builtin_path_dirname,
            'path_ext': self._builtin_path_ext,
            # std/http
            'http_get': self._builtin_http_get,
            'http_post': self._builtin_http_post,
            'http_get_json': self._builtin_http_get_json,
            'http_post_json': self._builtin_http_post_json,
            'http_serve_start': self._builtin_http_serve_start,
            'http_serve_stop': self._builtin_http_serve_stop,
            # std/sqlite
            'sqlite_open': self._builtin_sqlite_open,
            'sqlite_exec': self._builtin_sqlite_exec,
            'sqlite_query': self._builtin_sqlite_query,
            'sqlite_close': self._builtin_sqlite_close,
            # std/re
            're_test': self._builtin_re_test,
            're_full_match': self._builtin_re_full_match,
            're_find_all': self._builtin_re_find_all,
            're_groups': self._builtin_re_groups,
            're_replace': self._builtin_re_replace,
            're_split': self._builtin_re_split,
            # std/datetime
            'datetime_now': self._builtin_datetime_now,
            'datetime_today': self._builtin_datetime_today,
            'datetime_parse': self._builtin_datetime_parse,
            'datetime_format': self._builtin_datetime_format,
            'datetime_add_days': self._builtin_datetime_add_days,
            'datetime_add_hours': self._builtin_datetime_add_hours,
            'datetime_diff_days': self._builtin_datetime_diff_days,
            'datetime_diff_seconds': self._builtin_datetime_diff_seconds,
            'datetime_weekday': self._builtin_datetime_weekday,
            'datetime_parts': self._builtin_datetime_parts,
            'datetime_timestamp': self._builtin_datetime_timestamp,
            'datetime_from_timestamp': self._builtin_datetime_from_timestamp,
            'datetime_to_timezone': self._builtin_datetime_to_timezone,
            # std/encoding
            'enc_base64_encode': self._builtin_enc_base64_encode,
            'enc_base64_decode': self._builtin_enc_base64_decode,
            'enc_gzip_compress': self._builtin_enc_gzip_compress,
            'enc_gzip_decompress': self._builtin_enc_gzip_decompress,
            'enc_urlencode': self._builtin_enc_urlencode,
            'enc_urldecode': self._builtin_enc_urldecode,
            # std/glob (SL1)
            'glob_match': self._builtin_glob_match,
            # std/shutil (SL1)
            'shutil_copy_file': self._builtin_shutil_copy_file,
            'shutil_move': self._builtin_shutil_move,
            'shutil_rmtree': self._builtin_shutil_rmtree,
            # std/tempfile (SL1)
            'tempfile_mkdtemp': self._builtin_tempfile_mkdtemp,
            'tempfile_mkstemp': self._builtin_tempfile_mkstemp,
            'tempfile_tempdir': self._builtin_tempfile_tempdir,
            # std/uuid (SL1)
            'uuid_uuid4': self._builtin_uuid_uuid4,
            'uuid_uuid4_hex': self._builtin_uuid_uuid4_hex,
            # std/hashlib (SL1)
            'hash_md5': self._builtin_hash_md5,
            'hash_sha1': self._builtin_hash_sha1,
            'hash_sha256': self._builtin_hash_sha256,
            'hash_sha512': self._builtin_hash_sha512,
            # std/hmac (SL1)
            'hmac_sha256': self._builtin_hmac_sha256,
            'hmac_sha256_verify': self._builtin_hmac_sha256_verify,
            # std/secrets (SL1)
            'secrets_token_hex': self._builtin_secrets_token_hex,
            'secrets_rand_below': self._builtin_secrets_rand_below,
            'secrets_choice': self._builtin_secrets_choice,
            # std/decimal (SL1)
            'decimal_add': self._builtin_decimal_add,
            'decimal_sub': self._builtin_decimal_sub,
            'decimal_mul': self._builtin_decimal_mul,
            'decimal_div': self._builtin_decimal_div,
            'decimal_compare': self._builtin_decimal_compare,
            # std/memory (MM1)
            'mem_live_count': self._builtin_mem_live_count,
            'mem_alloc_total': self._builtin_mem_alloc_total,
            'mem_stats_info': self._builtin_mem_stats_info,
            'gc_collect_now': self._builtin_gc_collect_now,
            'ref_count_of': self._builtin_ref_count_of,
        }

    def _builtin_print(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置print函数"""
        output = " ".join(self._value_to_str(arg) for arg in args)
        print(output)
        return IntValue(0)

    def _builtin_args(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置args函数 — 命令行参数列表(程序与世界的接口)"""
        return ListValue([StringValue(a) for a in self.cli_args], StringType())

    def _builtin_assert(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置assert函数 — 测试框架的基石

        断言失败时抛出 AssertionError(带消息),
        经 execute_statement 包装层附加源码位置,顶层渲染显示调用链。
        """
        if len(args) != 2:
            raise TypeError("assert() 期望2个参数(condition, message)")
        cond, msg = args[0], args[1]
        msg_str = self._value_to_str(msg)
        if isinstance(cond, BoolValue) and cond.value:
            return cond
        raise AssertionError(msg_str)

    def _builtin_len(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置len函数"""
        if len(args) != 1:
            raise TypeError(f"len() 期望1个参数,得到 {len(args)}个")

        value = args[0]
        if isinstance(value, (ListValue, StringValue, DictValue)):
            return IntValue(len(value.value))
        # S3: 生成器没有长度 — 惰性序列, 拒绝而不是返回 None
        if isinstance(value, GeneratorValue):
            raise TypeError("生成器没有长度(惰性序列 — 用 for 消费或 next() 逐个取)")
        # 运算符重载: __len__()
        if isinstance(value, InstanceValue):
            method = value.get('__len__')
            if method and isinstance(method, FunctionValue):
                return self._execute_method(method, value, [])

    def _builtin_next(self, args: List[RuntimeValue]) -> RuntimeValue:
        """X3: 内置 next() — 迭代器协议 __next__

        取迭代器下一元素; __next__() 返回 None 即序列耗尽
        (语言约定: 无 StopIteration 通道, None 为终点信号)。
        生成器同样支持 — 惰性序列的下一个。
        """
        if len(args) != 1:
            raise TypeError(f"next() 期望1个参数,得到 {len(args)}个")
        it = args[0]
        if isinstance(it, InstanceValue):
            return self._dunder_next(it)
        if isinstance(it, GeneratorValue):
            # S3: 真惰性生成器 — 拉一个值; 耗尽按语言约定返回 None
            v = it._ctrl.next()
            return NoneValue() if v is _GEN_DONE else v
        raise TypeError(f"next() 期望迭代器(有__next__的对象或生成器),得到 {it.get_type()}")

    def _builtin_repr(self, args: List[RuntimeValue]) -> RuntimeValue:
        """X3: 内置 repr() — 调试表示; 实例优先走 __repr__()"""
        if len(args) != 1:
            raise TypeError(f"repr() 期望1个参数,得到 {len(args)}个")
        val = args[0]
        if isinstance(val, InstanceValue):
            method = val.get('__repr__')
            if method is not None and isinstance(method, FunctionValue):
                result = self._execute_method(method, val, [])
                return StringValue(self._value_to_str(result))
        return StringValue(self._value_to_str(val))

    def _builtin_cache_stats(self, args: List[RuntimeValue]) -> RuntimeValue:
        """M2: 属性缓存统计 — 返回 [命中数, 未命中数](模块级聚合)"""
        if args:
            raise TypeError("cache_stats() 不接受参数")
        return ListValue([IntValue(_ATTR_CACHE_STATS["hits"]),
                          IntValue(_ATTR_CACHE_STATS["misses"])], IntType())

    def _builtin_cache_reset(self, args: List[RuntimeValue]) -> RuntimeValue:
        """M2: 清零属性缓存统计 — 微基准/测试的确定性起点"""
        if args:
            raise TypeError("cache_reset() 不接受参数")
        _ATTR_CACHE_STATS["hits"] = 0
        _ATTR_CACHE_STATS["misses"] = 0
        return NoneValue()

    def _builtin_getattr(self, args: List[RuntimeValue]) -> RuntimeValue:
        """X2: getattr(obj, name) — 按名读属性(字段或方法), 不存在抛 AttributeError"""
        if len(args) != 2:
            raise TypeError(f"getattr() 期望2个参数(obj, name),得到 {len(args)}个")
        obj, name = args
        if not isinstance(name, StringValue):
            raise TypeError(f"getattr() 属性名期望 String,得到 {name.get_type()}")
        if isinstance(obj, InstanceValue):
            v = obj.get(name.value)
            if v is not None:
                return v
            raise AttributeError(f"实例没有属性 '{name.value}'")
        raise TypeError(f"getattr() 期望实例,得到 {obj.get_type()}")

    def _builtin_setattr(self, args: List[RuntimeValue]) -> RuntimeValue:
        """X2: setattr(obj, name, value) — 按名写字段(M2: 经 set() 写透缓存)"""
        if len(args) != 3:
            raise TypeError(f"setattr() 期望3个参数(obj, name, value),得到 {len(args)}个")
        obj, name, value = args
        if not isinstance(name, StringValue):
            raise TypeError(f"setattr() 属性名期望 String,得到 {name.get_type()}")
        if not isinstance(obj, InstanceValue):
            raise TypeError(f"setattr() 期望实例,得到 {obj.get_type()}")
        obj.set(name.value, value)
        return NoneValue()

    def _builtin_hasattr(self, args: List[RuntimeValue]) -> RuntimeValue:
        """X2: hasattr(obj, name) — 属性存在性(字段或方法)"""
        if len(args) != 2:
            raise TypeError(f"hasattr() 期望2个参数(obj, name),得到 {len(args)}个")
        obj, name = args
        if not isinstance(name, StringValue):
            raise TypeError(f"hasattr() 属性名期望 String,得到 {name.get_type()}")
        if not isinstance(obj, InstanceValue):
            raise TypeError(f"hasattr() 期望实例,得到 {obj.get_type()}")
        return BoolValue(obj.get(name.value) is not None)

    def _builtin_dir(self, args: List[RuntimeValue]) -> RuntimeValue:
        """X2: dir(obj) — 属性名清单(字段 + 方法含继承链, 排序)"""
        if len(args) != 1:
            raise TypeError(f"dir() 期望1个参数,得到 {len(args)}个")
        obj = args[0]
        if not isinstance(obj, InstanceValue):
            raise TypeError(f"dir() 期望实例,得到 {obj.get_type()}")
        names = set(obj.fields.keys()) | set(obj.klass.all_method_names())
        return ListValue([StringValue(n) for n in sorted(names)], StringType())

    def _builtin_callable(self, args: List[RuntimeValue]) -> RuntimeValue:
        """X2: callable(x) — 是否可调用

        函数/类/FFI 外部函数/Python 桥函数/mock 均可调用;
        实例定义了 __call__ 亦可调用(X3 协议)。
        """
        if len(args) != 1:
            raise TypeError(f"callable() 期望1个参数,得到 {len(args)}个")
        x = args[0]
        if isinstance(x, (FunctionValue, ClassValue, ForeignFuncValue,
                          PyFuncValue, MockValue)):
            return BoolValue(True)
        if isinstance(x, InstanceValue):
            m = x.get('__call__')
            return BoolValue(m is not None and isinstance(m, FunctionValue))
        return BoolValue(False)

    def _builtin_keys(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置keys函数:返回字典所有键"""
        if len(args) != 1 or not isinstance(args[0], DictValue):
            raise TypeError("keys() 期望1个Dict参数")
        keys_list = []
        for k in args[0].value.keys():
            # 键已规范化为 Python 标量(P3.1) — 包回 RuntimeValue
            if isinstance(k, bool):
                keys_list.append(BoolValue(k))
            elif isinstance(k, str):
                keys_list.append(StringValue(k))
            elif isinstance(k, int):
                keys_list.append(IntValue(k))
            elif isinstance(k, float):
                keys_list.append(FloatValue(k))
            else:
                keys_list.append(RuntimeValue(AnyType(), k))
        return ListValue(keys_list, element_type=StringType())

    def _builtin_values(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置values函数:返回字典所有值"""
        if len(args) != 1 or not isinstance(args[0], DictValue):
            raise TypeError("values() 期望1个Dict参数")
        return ListValue(list(args[0].value.values()), element_type=StringType())

    def _builtin_push(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置push函数:向列表末尾添加元素"""
        if len(args) < 2 or not isinstance(args[0], ListValue):
            raise TypeError("push() 期望(列表, 值)")
        args[0].value.append(args[1])
        return IntValue(len(args[0].value))

    def _builtin_pop(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置pop函数:移除并返回列表末尾元素"""
        if len(args) != 1 or not isinstance(args[0], ListValue):
            raise TypeError("pop() 期望1个List参数")
        if not args[0].value:
            raise IndexError("pop() 从空列表弹出")
        return args[0].value.pop()

    def _builtin_insert(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置insert函数:在指定位置插入元素"""
        if len(args) != 3 or not isinstance(args[0], ListValue):
            raise TypeError("insert() 期望(列表, 索引, 值)")
        idx = args[1].value
        if idx < 0:
            idx = len(args[0].value) + idx
        args[0].value.insert(idx, args[2])
        return IntValue(len(args[0].value))

    def _builtin_remove_at(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置remove_at函数:移除指定位置的元素"""
        if len(args) != 2 or not isinstance(args[0], ListValue):
            raise TypeError("remove_at() 期望(列表, 索引)")
        idx = args[1].value
        if idx < 0:
            idx = len(args[0].value) + idx
        if 0 <= idx < len(args[0].value):
            removed = args[0].value.pop(idx)
            return removed
        raise IndexError(f"remove_at() 索引 {idx} 越界")

    def _builtin_enumerate(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置enumerate函数:返回[(index, value), ...]"""
        if len(args) != 1 or not isinstance(args[0], ListValue):
            raise TypeError("enumerate() 期望1个List参数")
        pairs = []
        for i, v in enumerate(args[0].value):
            pairs.append(ListValue([IntValue(i), v], AnyType()))
        return ListValue(pairs, AnyType())

    def _builtin_zip(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置zip函数:合并多个列表"""
        if len(args) < 2:
            raise TypeError("zip() 期望至少2个List参数")
        for a in args:
            if not isinstance(a, ListValue):
                raise TypeError("zip() 参数必须是List")
        min_len = min(len(a.value) for a in args)
        result = []
        for i in range(min_len):
            row = [a.value[i] for a in args]
            result.append(ListValue(row, AnyType()))
        return ListValue(result, AnyType())

    def _builtin_run(self, args: List[RuntimeValue]) -> RuntimeValue:
        """A3a: run(coro) — 驱动协程至完成, 返回 async 函数的返回值

        协议: 协程线程 await 时交出的必是内层协程(AsyncValue);
        驱动侧递归驱动内层, 把结果 send 回挂起点。本质是蹦床——
        没有事件循环(A3b 才做 IO 多路复用), 调度按 await 顺序串行。
        """
        if len(args) != 1:
            raise TypeError("run() 期望1个协程参数(async 函数调用的结果)")
        coro = args[0]
        if not isinstance(coro, AsyncValue):
            raise TypeError(
                f"run() 期望协程(async 函数调用的结果), 得到 {coro.get_type()}")
        return self._drive_coroutine(coro._ctrl, NoneValue())

    def _drive_coroutine(self, ctrl, send_value) -> RuntimeValue:
        """A3a: 蹦床 — 把协程推到完成, 返回其 final_result

        异常沿驱动链自然传播(协程线程的 error 消息在 _resume 处重抛);
        协程交出非协程值即协议违约(TypeError, 显式失败不静默)。
        """
        while True:
            v = ctrl.send(send_value) if ctrl.started else ctrl.next()
            if v is _GEN_DONE:
                result = ctrl.final_result
                return result if result is not None else NoneValue()
            if isinstance(v, AsyncValue):
                send_value = self._drive_coroutine(v._ctrl, NoneValue())
                continue
            raise TypeError(
                f"async 函数只能 await 协程, 交出了 {getattr(v, 'get_type', lambda: type(v))()}")

    def _builtin_range(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置range函数:生成整数序列"""
        if len(args) == 1:
            start, end, step = 0, args[0].value, 1
        elif len(args) == 2:
            start, end, step = args[0].value, args[1].value, 1
        elif len(args) == 3:
            start, end, step = args[0].value, args[1].value, args[2].value
        else:
            raise TypeError("range() 期望1-3个Int参数")
        result = [IntValue(i) for i in range(start, end, step)]
        return ListValue(result, IntType())

    def _builtin_abs(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置abs函数:绝对值"""
        if len(args) != 1:
            raise TypeError("abs() 期望1个参数")
        v = args[0]
        if isinstance(v, IntValue):
            return IntValue(abs(v.value))
        elif isinstance(v, FloatValue):
            return FloatValue(abs(v.value))
        raise TypeError(f"abs() 不支持类型 {v.type}")

    def _builtin_min(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置min函数"""
        if len(args) != 1 or not isinstance(args[0], ListValue):
            raise TypeError("min() 期望1个List参数")
        if not args[0].value:
            raise ValueError("min() 空列表")
        return min(args[0].value, key=lambda x: x.value)

    def _builtin_max(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置max函数"""
        if len(args) != 1 or not isinstance(args[0], ListValue):
            raise TypeError("max() 期望1个List参数")
        if not args[0].value:
            raise ValueError("max() 空列表")
        return max(args[0].value, key=lambda x: x.value)

    def _builtin_sum(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置sum函数"""
        if len(args) != 1 or not isinstance(args[0], ListValue):
            raise TypeError("sum() 期望1个List参数")
        total = 0
        result_type = IntType()
        for v in args[0].value:
            if isinstance(v, FloatValue):
                result_type = FloatType()
            total += v.value
        if result_type == FloatType():
            return FloatValue(float(total))
        return IntValue(int(total))

    def _builtin_reversed(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置reversed函数:反转列表"""
        if len(args) != 1 or not isinstance(args[0], ListValue):
            raise TypeError("reversed() 期望1个List参数")
        return ListValue(list(reversed(args[0].value)), args[0].type.element_type)

    def _builtin_sorted(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置sorted函数:排序列表"""
        if len(args) < 1 or not isinstance(args[0], ListValue):
            raise TypeError("sorted() 期望1个List参数")
        return ListValue(sorted(args[0].value, key=lambda x: x.value), args[0].type.element_type)

    def _builtin_any(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置any函数: 列表中任一为真"""
        if len(args) != 1 or not isinstance(args[0], ListValue):
            raise TypeError("any() 期望1个List参数")
        for v in args[0].value:
            if v.to_bool():
                return BoolValue(True)
        return BoolValue(False)

    def _builtin_all(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置all函数: 列表全部为真"""
        if len(args) != 1 or not isinstance(args[0], ListValue):
            raise TypeError("all() 期望1个List参数")
        for v in args[0].value:
            if not v.to_bool():
                return BoolValue(False)
        return BoolValue(True)

    def _builtin_contains(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置contains函数: contains(list, item) → Bool"""
        if len(args) != 2 or not isinstance(args[0], ListValue):
            raise TypeError("contains() 期望(List, item)")
        target = args[1]
        for v in args[0].value:
            if v.value == target.value:
                return BoolValue(True)
        return BoolValue(False)

    def _builtin_type_of(self, args: List[RuntimeValue]) -> RuntimeValue:
        """内置type_of函数:返回值的类型名"""
        if len(args) != 1:
            raise TypeError("type_of() 期望1个参数")
        return StringValue(str(args[0].type))

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
        return StringValue(self._value_to_str(args[0]))

    def _builtin_format(self, args: List[RuntimeValue]) -> RuntimeValue:
        """S2b: format(value, spec) — f-string 格式规格, 语义对齐 Python

        规格白名单: fill/align(<>^=) sign(+-#) 0 width grouping(,_)
        precision(.N) type(deenfgxoxXeEs%) — 原样交给 Python format();
        花括号拒收(规格不是模板)。数字/布尔/字符串直接格式化,
        容器与 None 先 str 化再套字符串规格(对齐/宽度)。
        """
        if len(args) != 2:
            raise TypeError(f"format() 期望2个参数(值, 规格),得到 {len(args)}个")
        val, spec = args[0], args[1]
        if not isinstance(spec, StringValue):
            raise TypeError("format() 第2个参数必须是格式规格字符串")
        spec_text = spec.value
        if '{' in spec_text or '}' in spec_text:
            raise ValueError(f"非法格式规格(不允许花括号): {spec_text!r}")
        if isinstance(val, (IntValue, FloatValue, BoolValue, StringValue)):
            py_val = val.value
        else:
            py_val = self._value_to_str(val)
        try:
            return StringValue(format(py_val, spec_text))
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"格式规格 {spec_text!r} 不适用于 {val.get_type()}: {e}")

    def _value_to_str(self, val: RuntimeValue) -> str:
        """将 RuntimeValue 转为可读字符串"""
        if isinstance(val, StringValue):
            return val.value
        elif isinstance(val, IntValue):
            return str(val.value)
        elif isinstance(val, FloatValue):
            if val.value == int(val.value):
                return str(int(val.value)) + ".0"
            return str(val.value)
        elif isinstance(val, BoolValue):
            return "true" if val.value else "false"
        elif isinstance(val, NoneValue):
            return "None"
        elif isinstance(val, ListValue):
            items = [self._value_to_str(v) for v in val.value]
            return "[" + ", ".join(items) + "]"
        elif isinstance(val, DictValue):
            items = []
            for k, v in val.value.items():
                # 键已规范化为 Python 标量(P3.1); 字符串键带引号, 数值键原样
                if isinstance(k, str):
                    k_repr = f'"{k}"'
                else:
                    k_repr = str(k)
                items.append(f"{k_repr}: {self._value_to_str(v)}")
            return "{" + ", ".join(items) + "}"
        elif isinstance(val, InstanceValue):
            # 运算符重载: 调用 __str__() 方法; 无则 __repr__(); 再无走结构渲染
            method = val.get('__str__')
            if method and isinstance(method, FunctionValue):
                result = self._execute_method(method, val, [])
                return self._value_to_str(result)
            method = val.get('__repr__')
            if method and isinstance(method, FunctionValue):
                result = self._execute_method(method, val, [])
                return self._value_to_str(result)
            elif hasattr(val, 'type'):
                return f"<{val.type}>"
            else:
                return str(val.value)
        elif isinstance(val, GeneratorValue):
            return "<generator>"
        else:
            return str(val.value)

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

    def _builtin_error(self, args: List[RuntimeValue]) -> RuntimeValue:
        """error(type, message) - 构造 Intent 错误值(EX1: raise 的原料)

        错误是一等值 — 先构造, 再 raise; from 子句挂因果链。
        """
        if len(args) != 2:
            raise TypeError(
                f"error() 期望2个参数(type, message), 得到 {len(args)}个")
        if not isinstance(args[0], StringValue) or not isinstance(args[1], StringValue):
            raise TypeError(
                'error() 参数必须是字符串: error("ValueError", "消息")')
        return ErrorValue(args[0].value, args[1].value)

    # ── CC2: 通道通信内置 ────────────────────────────────

    def _builtin_chan(self, args: List[RuntimeValue]) -> RuntimeValue:
        """chan() / chan(n) — 创建通道: 无界缓冲 / 容量 n(满则发送阻塞)"""
        if len(args) > 1:
            raise TypeError(f"chan() 期望 0-1 个参数(可选容量), 得到 {len(args)} 个")
        capacity = 0
        if args:
            if not isinstance(args[0], IntValue):
                raise TypeError("chan() 的容量必须是整数")
            capacity = args[0].value
            if capacity < 0:
                raise ValueError("chan() 的容量不能为负")
        return ChannelValue(capacity)

    def _builtin_close(self, args: List[RuntimeValue]) -> RuntimeValue:
        """close(ch) — 关闭通道: 发送此后再报错, 接收排空剩余即止"""
        if len(args) != 1:
            raise TypeError(f"close() 期望1个参数(channel), 得到 {len(args)} 个")
        if not isinstance(args[0], ChannelValue):
            raise TypeError(f"close() 期望通道(chan() 创建), 得到 {args[0].type}")
        args[0].close()
        return NoneValue()

    # ── I1: C ABI FFI 内置（ctypes 背载最小切片）──────────

    def _builtin_ffi_load(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ffi_load(path) — 加载外部动态库(.dll/.so), 返回库句柄

        路径直接交给 ctypes.CDLL: Windows 按 LoadLibrary 语义搜路径,
        POSIX 按 dlopen 语义。加载失败(找不到/不是库)报 RuntimeError,
        错误信息带原始 OSError 文本 — 显式失败, 不返回哑值。
        """
        if len(args) != 1:
            raise TypeError(f"ffi_load() 期望1个参数(库路径), 得到 {len(args)} 个")
        if not isinstance(args[0], StringValue):
            raise TypeError(f"ffi_load() 期望字符串路径, 得到 {args[0].type}")
        path = args[0].value
        try:
            handle = ctypes.CDLL(path)
        except OSError as e:
            raise RuntimeError(f"FFI 加载库失败 {path!r}: {e}")
        return LibValue(path, handle)

    def _builtin_ffi_func(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ffi_func(lib, name, restype, argtypes) — 声明外部函数

        argtypes 是类型名列表(Int/Float/Str/Bool/Ptr/Struct);
        restype 同表 + Void。声明期校验: 符号存在 + 类型名白名单。
        """
        if len(args) != 4:
            raise TypeError("ffi_func() 期望4个参数(lib, name, restype, argtypes), "
                            f"得到 {len(args)} 个")
        lib, name, restype, argtypes = args
        if not isinstance(lib, LibValue):
            raise TypeError(f"ffi_func() 第1个参数期望库句柄(ffi_load 创建), 得到 {lib.type}")
        if not isinstance(name, StringValue):
            raise TypeError(f"ffi_func() 第2个参数期望函数名字符串, 得到 {name.type}")
        if not isinstance(restype, StringValue):
            raise TypeError(f"ffi_func() 第3个参数期望返回类型字符串, 得到 {restype.type}")
        if not isinstance(argtypes, ListValue):
            raise TypeError(f"ffi_func() 第4个参数期望参数类型列表, 得到 {argtypes.type}")
        type_names = []
        for t in argtypes.value:
            if not isinstance(t, StringValue):
                raise TypeError(f"ffi_func() 参数类型必须是字符串, 得到 {t.type}")
            _ffi_check_type_name(t.value)
            type_names.append(t.value)
        _ffi_check_type_name(restype.value)
        return ForeignFuncValue(lib, name.value, restype.value, type_names)

    def _builtin_ffi_struct(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ffi_struct(names, types) — 定义并创建 C 结构体实例

        字段类型限 Int/Float/Str/Bool/Ptr(最小切片: 平铺标量,
        嵌套结构体/数组属完整 I1)。names 与 types 等长, 字段名唯一。
        """
        if len(args) != 2:
            raise TypeError("ffi_struct() 期望2个参数(names, types), "
                            f"得到 {len(args)} 个")
        names_v, types_v = args
        if not isinstance(names_v, ListValue) or not isinstance(types_v, ListValue):
            raise TypeError("ffi_struct() 期望两个列表(字段名, 字段类型)")
        if len(names_v.value) != len(types_v.value):
            raise ValueError(
                f"ffi_struct() 字段名与类型数量不符: "
                f"{len(names_v.value)} vs {len(types_v.value)}")
        fields = {}
        cfields = []
        for n, t in zip(names_v.value, types_v.value):
            if not isinstance(n, StringValue) or not isinstance(t, StringValue):
                raise TypeError("ffi_struct() 字段名与类型必须是字符串")
            if n.value in fields:
                raise ValueError(f"ffi_struct() 字段名重复: {n.value}")
            _ffi_check_type_name(t.value)
            fields[n.value] = t.value
            cfields.append((n.value, _FFI_SCALARS[t.value]))
        if not cfields:
            raise ValueError("ffi_struct() 至少需要一个字段")
        cls = type('IntentFFIStruct', (ctypes.Structure,), {'_fields_': cfields})
        return StructValue(fields, cls())

    def _builtin_ffi_field_get(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ffi_field_get(s, name) — 读结构体字段"""
        if len(args) != 2:
            raise TypeError(f"ffi_field_get() 期望2个参数, 得到 {len(args)} 个")
        s, name = args
        if not isinstance(s, StructValue):
            raise TypeError(f"ffi_field_get() 第1个参数期望结构体, 得到 {s.type}")
        if not isinstance(name, StringValue):
            raise TypeError(f"ffi_field_get() 第2个参数期望字段名字符串, 得到 {name.type}")
        if name.value not in s.fields:
            raise KeyError(f"结构体无字段 {name.value}(现有: {sorted(s.fields)})")
        return _ffi_from_c(getattr(s.instance, name.value), s.fields[name.value])

    def _builtin_ffi_field_set(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ffi_field_set(s, name, v) — 写结构体字段(指针语义: 外部函数可见)"""
        if len(args) != 3:
            raise TypeError(f"ffi_field_set() 期望3个参数, 得到 {len(args)} 个")
        s, name, v = args
        if not isinstance(s, StructValue):
            raise TypeError(f"ffi_field_set() 第1个参数期望结构体, 得到 {s.type}")
        if not isinstance(name, StringValue):
            raise TypeError(f"ffi_field_set() 第2个参数期望字段名字符串, 得到 {name.type}")
        if name.value not in s.fields:
            raise KeyError(f"结构体无字段 {name.value}(现有: {sorted(s.fields)})")
        setattr(s.instance, name.value, _ffi_to_c(v, s.fields[name.value]))
        return NoneValue()

    def _builtin_ffi_sizeof(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ffi_sizeof(s) — 结构体内存字节数(与 C sizeof 一致)"""
        if len(args) != 1:
            raise TypeError(f"ffi_sizeof() 期望1个参数, 得到 {len(args)} 个")
        if not isinstance(args[0], StructValue):
            raise TypeError(f"ffi_sizeof() 期望结构体, 得到 {args[0].type}")
        return IntValue(ctypes.sizeof(args[0].instance))

    # ── TQ1: 测试框架深化内置 ────────────────────────────

    def _builtin_skip(self, args: List[RuntimeValue]) -> RuntimeValue:
        """skip(reason) — 标记当前测试跳过

        跳过是诚实的中间态: 既不是通过也不是失败, 运行器单独计数。
        """
        reason = args[0].value if args and isinstance(args[0], StringValue) else ""
        raise SkipTest(reason)

    def _builtin_expect_error(self, args: List[RuntimeValue]) -> RuntimeValue:
        """expect_error(fn, type) — 断言 fn() 抛出指定类型的错误

        返回捕获到的 ErrorValue; 未抛错或类型不符 → AssertionError。
        预期异常的正面表达: 坏路径也是契约的一部分。
        """
        if len(args) != 2:
            raise TypeError("expect_error() 期望2个参数(fn, 期望类型), "
                            f"得到 {len(args)} 个")
        fn, expected = args[0], args[1]
        if not isinstance(expected, StringValue):
            raise TypeError("expect_error() 第2个参数必须是错误类型字符串")
        if not isinstance(fn, FunctionValue) and not callable(fn):
            raise TypeError("expect_error() 第1个参数必须是可调用对象")
        try:
            if isinstance(fn, FunctionValue):
                self.execute_function(fn, [])
            else:
                fn([])
        except SkipTest:
            raise
        except Exception as e:
            ie = wrap_intent_error(e, self)
            actual = getattr(ie, 'py_type', None) or type(e).__name__
            if actual != expected.value:
                raise AssertionError(
                    f"expect_error 类型不符: 期望 {expected.value}, 实际 {actual}")
            ev = getattr(ie, 'error_value', None)
            if ev is None:
                ev = ErrorValue(actual, ie.message)
            return ev
        raise AssertionError(
            f"expect_error: 期望抛出 {expected.value}, 但函数正常返回了")

    def _builtin_param_cases(self, args: List[RuntimeValue]) -> RuntimeValue:
        """param_cases(cases, fn) — 参数化: 每个用例调用一次 fn

        cases 是列表的列表(每项一组实参, 展开传给 fn — pytest
        parametrize 语义); 任一用例失败 → AssertionError 带上用例
        序号与内容(定位到个案)。无装饰器语法前的数据驱动等价物
        (X1 装饰器落地后可升华)。
        """
        if len(args) != 2:
            raise TypeError("param_cases() 期望2个参数(cases, fn), "
                            f"得到 {len(args)} 个")
        cases, fn = args[0], args[1]
        if not isinstance(cases, ListValue):
            raise TypeError("param_cases() 第1个参数必须是用例列表")
        if not isinstance(fn, FunctionValue) and not callable(fn):
            raise TypeError("param_cases() 第2个参数必须是可调用对象")
        for idx, case in enumerate(cases.value):
            case_args = case.value if isinstance(case, ListValue) else [case]
            try:
                if isinstance(fn, FunctionValue):
                    self.execute_function(fn, list(case_args))
                else:
                    fn(list(case_args))
            except SkipTest:
                raise
            except Exception as e:
                ie = wrap_intent_error(e, self)
                raise AssertionError(
                    f"参数化用例 #{idx} 失败: {ie.message} (用例: {case})")
        return NoneValue()

    def _builtin_mock(self, args: List[RuntimeValue]) -> RuntimeValue:
        """mock(name) — 创建测试替身(记录调用序列, 返回预设值)"""
        if len(args) > 1:
            raise TypeError(f"mock() 期望0-1个参数(名称), 得到 {len(args)} 个")
        name = args[0].value if args and isinstance(args[0], StringValue) else "mock"
        return MockValue(name)

    def _builtin_mock_return(self, args: List[RuntimeValue]) -> RuntimeValue:
        """mock_return(m, v) — 预设 mock 的返回值"""
        if len(args) != 2:
            raise TypeError("mock_return() 期望2个参数(mock, 返回值), "
                            f"得到 {len(args)} 个")
        if not isinstance(args[0], MockValue):
            raise TypeError(f"mock_return() 第1个参数必须是 mock, 得到 {args[0].type}")
        args[0].return_value = args[1].copy() if isinstance(args[1], RuntimeValue) \
            else args[1]
        return NoneValue()

    def _builtin_mock_calls(self, args: List[RuntimeValue]) -> RuntimeValue:
        """mock_calls(m) — 取调用记录: [[arg, ...], ...]"""
        if len(args) != 1 or not isinstance(args[0], MockValue):
            raise TypeError("mock_calls() 期望1个参数(mock)")
        return ListValue([ListValue(list(c), AnyType()) for c in args[0].calls],
                         AnyType())

    def _builtin_mock_call_count(self, args: List[RuntimeValue]) -> RuntimeValue:
        """mock_call_count(m) — 调用次数"""
        if len(args) != 1 or not isinstance(args[0], MockValue):
            raise TypeError("mock_call_count() 期望1个参数(mock)")
        return IntValue(len(args[0].calls))

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
                # 键保持 Python 标量形态 — DictValue._norm_key 的全库约定
                d.value[k] = self._py_to_runtime(v)
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

    # ══ std/http（B6）──
    def _http_request(self, method: str, url: str, body: str = None):
        """HTTP 请求 — urllib 实现, 返回 (status, body)"""
        import urllib.request
        import urllib.error
        data = body.encode('utf-8') if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        if data is not None:
            req.add_header('Content-Type', 'application/json')
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, resp.read().decode('utf-8')
        except urllib.error.HTTPError as he:
            return he.code, he.read().decode('utf-8', errors='replace')
        except urllib.error.URLError as ue:
            raise RuntimeError(f"HTTP 请求失败: {url} — {ue.reason}")

    def _builtin_http_get(self, args: List[RuntimeValue]) -> RuntimeValue:
        """http_get(url: String) — GET 请求, 返回响应体字符串"""
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("http_get() 期望1个字符串参数(url)")
        _status, body = self._http_request('GET', args[0].value)
        return StringValue(body)

    def _builtin_http_post(self, args: List[RuntimeValue]) -> RuntimeValue:
        """http_post(url: String, body: String) — POST 请求, 返回响应体字符串"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], StringValue):
            raise TypeError("http_post() 期望2个字符串参数(url, body)")
        _status, body = self._http_request('POST', args[0].value, args[1].value)
        return StringValue(body)

    def _builtin_http_get_json(self, args: List[RuntimeValue]) -> RuntimeValue:
        """http_get_json(url: String) — GET 并解析 JSON 响应"""
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("http_get_json() 期望1个字符串参数(url)")
        import json as _json
        _status, body = self._http_request('GET', args[0].value)
        try:
            return self._py_to_runtime(_json.loads(body))
        except _json.JSONDecodeError as je:
            raise ValueError(f"HTTP 响应不是合法 JSON: {je.msg}")

    def _builtin_http_post_json(self, args: List[RuntimeValue]) -> RuntimeValue:
        """http_post_json(url: String, value) — POST JSON 体, 返回响应体字符串"""
        if len(args) != 2 or not isinstance(args[0], StringValue):
            raise TypeError("http_post_json() 期望 (字符串 url, 任意值)")
        import json as _json
        body = _json.dumps(self._runtime_to_py(args[1]), ensure_ascii=False)
        _status, resp = self._http_request('POST', args[0].value, body)
        return StringValue(resp)

    def _builtin_http_serve_start(self, args: List[RuntimeValue]) -> RuntimeValue:
        """http_serve_start(port: Int) — 本地测试服务器, 返回实际端口

        路由: GET /hello → 文本; GET /json → JSON; POST /echo → 回声。
        port=0 由操作系统分配。测试与演示的闭环球桌——不依赖外网。
        """
        import threading
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        if len(args) != 1:
            raise TypeError("http_serve_start() 期望1个参数(port)")
        interp = self

        class _Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):  # 静默 — 不污染测试输出
                pass

            def _send(self, code: int, payload: str, ctype: str):
                raw = payload.encode('utf-8')
                self.send_response(code)
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Length', str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_GET(self):
                if self.path == '/hello':
                    self._send(200, 'hello from intent test server', 'text/plain')
                elif self.path == '/json':
                    self._send(200, '{"lang": "intent", "version": 2, "ok": true}',
                               'application/json')
                else:
                    self._send(404, 'not found', 'text/plain')

            def do_POST(self):
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length).decode('utf-8') if length else ''
                if self.path == '/echo':
                    self._send(200, body, 'text/plain')
                else:
                    self._send(404, 'not found', 'text/plain')

        try:
            server = ThreadingHTTPServer(('127.0.0.1', int(args[0].value)), _Handler)
        except OSError as oe:
            raise RuntimeError(f"测试服务器启动失败: {oe}")
        server.port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        if not hasattr(interp, '_http_servers'):
            interp._http_servers = {}
        interp._http_servers[server.port] = server
        return IntValue(server.port)

    def _builtin_http_serve_stop(self, args: List[RuntimeValue]) -> RuntimeValue:
        """http_serve_stop(port: Int) — 关闭测试服务器"""
        if len(args) != 1:
            raise TypeError("http_serve_stop() 期望1个参数(port)")
        servers = getattr(self, '_http_servers', {})
        server = servers.pop(int(args[0].value), None)
        if server is not None:
            server.shutdown()
            server.server_close()
        return IntValue(0)

    # ══ std/sqlite（B7）──
    def _sqlite_handle(self, args, idx: int = 0):
        """取 sqlite 连接句柄 — 参数校验 + 连接存在性"""
        import sqlite3
        if len(args) < idx + 1 or not isinstance(args[idx], IntValue):
            raise TypeError("期望整数句柄(sqlite_open 的返回值)")
        conn = getattr(self, '_sqlite_conns', {}).get(args[idx].value)
        if conn is None:
            raise RuntimeError(f"sqlite 句柄 {args[idx].value} 无效或已关闭")
        return conn

    def _builtin_sqlite_open(self, args: List[RuntimeValue]) -> RuntimeValue:
        """sqlite_open(path: String) — 打开数据库, 返回句柄(":memory:" 内存库)"""
        import sqlite3
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("sqlite_open() 期望1个字符串参数(path)")
        try:
            conn = sqlite3.connect(args[0].value)
        except sqlite3.Error as se:
            raise RuntimeError(f"sqlite 打开失败: {se}")
        if not hasattr(self, '_sqlite_conns'):
            self._sqlite_conns = {}
            self._sqlite_next = 1
        handle = self._sqlite_next
        self._sqlite_next += 1
        self._sqlite_conns[handle] = conn
        return IntValue(handle)

    def _builtin_sqlite_exec(self, args: List[RuntimeValue]) -> RuntimeValue:
        """sqlite_exec(handle: Int, sql: String) — 执行写操作, 返回影响行数"""
        if len(args) != 2 or not isinstance(args[1], StringValue):
            raise TypeError("sqlite_exec() 期望 (整数句柄, 字符串 sql)")
        conn = self._sqlite_handle(args)
        try:
            cur = conn.execute(args[1].value)
            conn.commit()
            return IntValue(cur.rowcount if cur.rowcount != -1 else 0)
        except Exception as se:
            raise RuntimeError(f"sqlite 执行失败: {se}")

    def _builtin_sqlite_query(self, args: List[RuntimeValue]) -> RuntimeValue:
        """sqlite_query(handle: Int, sql: String) — 查询, 返回行字典列表"""
        if len(args) != 2 or not isinstance(args[1], StringValue):
            raise TypeError("sqlite_query() 期望 (整数句柄, 字符串 sql)")
        conn = self._sqlite_handle(args)
        try:
            cur = conn.execute(args[1].value)
            names = [d[0] for d in cur.description] if cur.description else []
            rows = ListValue([], AnyType())
            for row in cur.fetchall():
                d = DictValue()
                for name, val in zip(names, row):
                    # 键为 Python 标量 — DictValue._norm_key 约定
                    d.value[name] = self._py_to_runtime(val)
                rows.value.append(d)
            return rows
        except Exception as se:
            raise RuntimeError(f"sqlite 查询失败: {se}")

    def _builtin_sqlite_close(self, args: List[RuntimeValue]) -> RuntimeValue:
        """sqlite_close(handle: Int) — 关闭连接"""
        conn = self._sqlite_handle(args)
        conn.close()
        getattr(self, '_sqlite_conns', {}).pop(args[0].value, None)
        return IntValue(0)

    # ══ std/re（B8）──
    def _re_compile(self, pattern: str):
        """编译正则 — 非法模式转 ValueError（保留 re 模块原始消息）"""
        import re as _re
        try:
            return _re.compile(pattern)
        except _re.error as ee:
            raise ValueError(f"正则表达式错误: {ee}")

    def _builtin_re_test(self, args: List[RuntimeValue]) -> RuntimeValue:
        """re_test(pattern: String, text: String) — 是否存在匹配(re.search)"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], StringValue):
            raise TypeError("re_test() 期望2个字符串参数(pattern, text)")
        return BoolValue(self._re_compile(args[0].value).search(args[1].value)
                         is not None)

    def _builtin_re_full_match(self, args: List[RuntimeValue]) -> RuntimeValue:
        """re_full_match(pattern, text) — 整串匹配(re.fullmatch)"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], StringValue):
            raise TypeError("re_full_match() 期望2个字符串参数(pattern, text)")
        return BoolValue(self._re_compile(args[0].value).fullmatch(args[1].value)
                         is not None)

    def _builtin_re_find_all(self, args: List[RuntimeValue]) -> RuntimeValue:
        """re_find_all(pattern, text) — 所有匹配子串(完整匹配, 不含分组)"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], StringValue):
            raise TypeError("re_find_all() 期望2个字符串参数(pattern, text)")
        rx = self._re_compile(args[0].value)
        return ListValue([StringValue(m.group(0)) for m in rx.finditer(args[1].value)],
                         StringType())

    def _builtin_re_groups(self, args: List[RuntimeValue]) -> RuntimeValue:
        """re_groups(pattern, text) — 首个匹配的捕获组列表(无匹配返回空列表)"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], StringValue):
            raise TypeError("re_groups() 期望2个字符串参数(pattern, text)")
        m = self._re_compile(args[0].value).search(args[1].value)
        if m is None:
            return ListValue([], StringType())
        # 未参与匹配的组 → None(与 Python re 语义一致)
        return ListValue([NoneValue() if g is None else StringValue(g)
                          for g in m.groups()], StringType())

    def _builtin_re_replace(self, args: List[RuntimeValue]) -> RuntimeValue:
        """re_replace(pattern, repl, text) — 全局替换(repl 支持 \\1 反向引用)"""
        if len(args) != 3 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], StringValue) or not isinstance(args[2], StringValue):
            raise TypeError("re_replace() 期望3个字符串参数(pattern, repl, text)")
        return StringValue(self._re_compile(args[0].value).sub(args[1].value,
                                                              args[2].value))

    def _builtin_re_split(self, args: List[RuntimeValue]) -> RuntimeValue:
        """re_split(pattern, text) — 按模式切分(捕获组产生的分段也返回)"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], StringValue):
            raise TypeError("re_split() 期望2个字符串参数(pattern, text)")
        return ListValue([StringValue(p)
                          for p in self._re_compile(args[0].value).split(args[1].value)],
                         StringType())

    # ══ std/datetime（B4）──
    # 表示法：ISO 字符串（"YYYY-MM-DD" 或 "YYYY-MM-DD HH:MM:SS"），
    # 朴素时间（naive）；timestamp/from_timestamp 按本地时区解释，
    # to_timezone 显式按 UTC 解释输入。非法输入抛 ValueError。
    def _dt_parse(self, s: str):
        """解析 ISO 字符串 → datetime（保留输入是否含时间成分的信息在外层判断）"""
        from datetime import datetime as _dt
        text = s.strip()
        try:
            return _dt.fromisoformat(text)
        except ValueError:
            raise ValueError(
                f"无效的日期时间: '{s}'（期望 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）")

    @staticmethod
    def _dt_iso(dt) -> str:
        """datetime → ISO 字符串（空格分隔，与解析输入同构）"""
        return dt.isoformat(sep=' ')

    def _builtin_datetime_now(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_now() — 当前本地日期时间（ISO 字符串）"""
        from datetime import datetime as _dt
        return StringValue(self._dt_iso(_dt.now()))

    def _builtin_datetime_today(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_today() — 今天日期（ISO 字符串）"""
        from datetime import date as _date
        return StringValue(_date.today().isoformat())

    def _builtin_datetime_parse(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_parse(iso) — 校验并规范化（非法抛 ValueError）"""
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("datetime_parse() 期望1个字符串参数(iso)")
        return StringValue(self._dt_iso(self._dt_parse(args[0].value)))

    def _builtin_datetime_format(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_format(iso, fmt) — 按 strftime 格式串格式化"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], StringValue):
            raise TypeError("datetime_format() 期望2个字符串参数(iso, fmt)")
        return StringValue(self._dt_parse(args[0].value).strftime(args[1].value))

    def _builtin_datetime_add_days(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_add_days(iso, days) — 加天数（可为负）"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], IntValue):
            raise TypeError("datetime_add_days() 期望 (字符串 iso, 整数 days)")
        from datetime import timedelta as _td
        dt = self._dt_parse(args[0].value) + _td(days=args[1].value)
        return StringValue(self._dt_iso(dt))

    def _builtin_datetime_add_hours(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_add_hours(iso, hours) — 加小时（可为负）"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], (IntValue, FloatValue)):
            raise TypeError("datetime_add_hours() 期望 (字符串 iso, 数值 hours)")
        from datetime import timedelta as _td
        dt = self._dt_parse(args[0].value) + _td(hours=args[1].value)
        return StringValue(self._dt_iso(dt))

    def _builtin_datetime_diff_days(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_diff_days(a, b) — a - b 的整天数（向下取整）"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], StringValue):
            raise TypeError("datetime_diff_days() 期望2个字符串参数(a, b)")
        delta = self._dt_parse(args[0].value) - self._dt_parse(args[1].value)
        return IntValue(delta.days)

    def _builtin_datetime_diff_seconds(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_diff_seconds(a, b) — a - b 的秒数"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], StringValue):
            raise TypeError("datetime_diff_seconds() 期望2个字符串参数(a, b)")
        delta = self._dt_parse(args[0].value) - self._dt_parse(args[1].value)
        return IntValue(int(delta.total_seconds()))

    def _builtin_datetime_weekday(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_weekday(iso) — 星期几（0=周一 … 6=周日）"""
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("datetime_weekday() 期望1个字符串参数(iso)")
        return IntValue(self._dt_parse(args[0].value).weekday())

    def _builtin_datetime_parts(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_parts(iso) — {year, month, day, hour, minute, second} 字典"""
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("datetime_parts() 期望1个字符串参数(iso)")
        dt = self._dt_parse(args[0].value)
        d = DictValue()
        for key, val in (('year', dt.year), ('month', dt.month), ('day', dt.day),
                         ('hour', dt.hour), ('minute', dt.minute),
                         ('second', dt.second)):
            d.value[key] = IntValue(val)
        return d

    def _builtin_datetime_timestamp(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_timestamp(iso) — Unix 时间戳（按本地时区解释）"""
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("datetime_timestamp() 期望1个字符串参数(iso)")
        return FloatValue(self._dt_parse(args[0].value).timestamp())

    def _builtin_datetime_from_timestamp(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_from_timestamp(ts) — Unix 时间戳 → 本地 ISO 字符串"""
        if len(args) != 1 or not isinstance(args[0], (IntValue, FloatValue)):
            raise TypeError("datetime_from_timestamp() 期望1个数值参数(ts)")
        from datetime import datetime as _dt
        return StringValue(self._dt_iso(_dt.fromtimestamp(args[0].value)))

    def _builtin_datetime_to_timezone(self, args: List[RuntimeValue]) -> RuntimeValue:
        """datetime_to_timezone(iso, offset_hours) — 输入按 UTC 解释，
        返回 offset_hours 时区的墙上时间（如 (14:00, +8) → 22:00）"""
        if len(args) != 2 or not isinstance(args[0], StringValue) \
                or not isinstance(args[1], (IntValue, FloatValue)):
            raise TypeError("datetime_to_timezone() 期望 (字符串 iso, 数值 offset_hours)")
        from datetime import timezone as _tz, timedelta as _td
        dt = self._dt_parse(args[0].value).replace(tzinfo=_tz.utc)
        shifted = (dt + _td(hours=args[1].value)).replace(tzinfo=None)
        return StringValue(self._dt_iso(shifted))

    # ══ std/encoding（B9）──
    # 表示法：Intent 字符串是文本，二进制字节序列以 base64 文本承载。
    # gzip_compress 返回「压缩字节的 base64」；非法输入一律转 ValueError。
    def _builtin_enc_base64_encode(self, args: List[RuntimeValue]) -> RuntimeValue:
        """enc_base64_encode(text) — UTF-8 字节 → 标准 base64"""
        import base64 as _b64
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("enc_base64_encode() 期望1个字符串参数(text)")
        raw = args[0].value.encode('utf-8')
        return StringValue(_b64.b64encode(raw).decode('ascii'))

    def _builtin_enc_base64_decode(self, args: List[RuntimeValue]) -> RuntimeValue:
        """enc_base64_decode(data) — base64 → UTF-8 文本（非法抛 ValueError）"""
        import base64 as _b64
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("enc_base64_decode() 期望1个字符串参数(data)")
        try:
            raw = _b64.b64decode(args[0].value, validate=True)
            return StringValue(raw.decode('utf-8'))
        except Exception as ee:
            raise ValueError(f"无效的 base64 数据: {ee}")

    def _builtin_enc_gzip_compress(self, args: List[RuntimeValue]) -> RuntimeValue:
        """enc_gzip_compress(text) — gzip 压缩后以 base64 文本返回"""
        import base64 as _b64, gzip as _gzip
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("enc_gzip_compress() 期望1个字符串参数(text)")
        raw = _gzip.compress(args[0].value.encode('utf-8'))
        return StringValue(_b64.b64encode(raw).decode('ascii'))

    def _builtin_enc_gzip_decompress(self, args: List[RuntimeValue]) -> RuntimeValue:
        """enc_gzip_decompress(data) — base64 → gzip 解压 → 文本（非法抛 ValueError）"""
        import base64 as _b64, gzip as _gzip
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("enc_gzip_decompress() 期望1个字符串参数(data)")
        try:
            raw = _b64.b64decode(args[0].value, validate=True)
            return StringValue(_gzip.decompress(raw).decode('utf-8'))
        except Exception as ee:
            raise ValueError(f"无效的 gzip 数据: {ee}")

    def _builtin_enc_urlencode(self, args: List[RuntimeValue]) -> RuntimeValue:
        """enc_urlencode(text) — UTF-8 百分号编码（默认无保留字符，空格 → %20）"""
        from urllib.parse import quote as _quote
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("enc_urlencode() 期望1个字符串参数(text)")
        return StringValue(_quote(args[0].value, safe=''))

    def _builtin_enc_urldecode(self, args: List[RuntimeValue]) -> RuntimeValue:
        """enc_urldecode(data) — 百分号解码（UTF-8，非法输入抛 ValueError）"""
        from urllib.parse import unquote as _unquote
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("enc_urldecode() 期望1个字符串参数(data)")
        try:
            return StringValue(_unquote(args[0].value, errors='strict'))
        except Exception as ee:
            raise ValueError(f"无效的百分号编码: {ee}")

    # ══ std/glob（SL1）══
    def _builtin_glob_match(self, args: List[RuntimeValue]) -> RuntimeValue:
        """glob_match(pattern) — 通配符匹配路径列表(空表=无匹配)"""
        import glob as _glob
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("glob_match() 期望1个字符串参数(pattern)")
        return ListValue([StringValue(p) for p in _glob.glob(args[0].value)],
                         element_type=StringType())

    # ══ std/shutil（SL1）══
    def _builtin_shutil_copy_file(self, args: List[RuntimeValue]) -> RuntimeValue:
        """shutil_copy_file(src, dst) — 复制文件(覆盖式)"""
        import shutil as _shutil
        if len(args) != 2 or not all(isinstance(a, StringValue) for a in args):
            raise TypeError("shutil_copy_file() 期望2个字符串参数(src, dst)")
        try:
            _shutil.copyfile(args[0].value, args[1].value)
        except Exception as ee:
            raise RuntimeError(f"复制失败: {ee}")
        return BoolValue(True)

    def _builtin_shutil_move(self, args: List[RuntimeValue]) -> RuntimeValue:
        """shutil_move(src, dst) — 移动文件或目录"""
        import shutil as _shutil
        if len(args) != 2 or not all(isinstance(a, StringValue) for a in args):
            raise TypeError("shutil_move() 期望2个字符串参数(src, dst)")
        try:
            _shutil.move(args[0].value, args[1].value)
        except Exception as ee:
            raise RuntimeError(f"移动失败: {ee}")
        return BoolValue(True)

    def _builtin_shutil_rmtree(self, args: List[RuntimeValue]) -> RuntimeValue:
        """shutil_rmtree(path) — 递归删除目录(不存在抛 RuntimeError)"""
        import shutil as _shutil
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("shutil_rmtree() 期望1个字符串参数(path)")
        try:
            _shutil.rmtree(args[0].value)
        except Exception as ee:
            raise RuntimeError(f"删除目录失败: {ee}")
        return BoolValue(True)

    # ══ std/tempfile（SL1）══
    def _builtin_tempfile_mkdtemp(self, args: List[RuntimeValue]) -> RuntimeValue:
        """tempfile_mkdtemp() — 创建唯一临时目录, 返回路径"""
        import tempfile as _tf
        if args:
            raise TypeError("tempfile_mkdtemp() 无参数")
        return StringValue(_tf.mkdtemp())

    def _builtin_tempfile_mkstemp(self, args: List[RuntimeValue]) -> RuntimeValue:
        """tempfile_mkstemp(prefix) — 创建唯一临时文件, 返回路径"""
        import tempfile as _tf
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("tempfile_mkstemp() 期望1个字符串参数(prefix)")
        fd, path = _tf.mkstemp(prefix=args[0].value)
        import os as _os
        _os.close(fd)
        return StringValue(path)

    def _builtin_tempfile_tempdir(self, args: List[RuntimeValue]) -> RuntimeValue:
        """tempfile_tempdir() — 系统临时目录路径"""
        import tempfile as _tf
        if args:
            raise TypeError("tempfile_tempdir() 无参数")
        return StringValue(_tf.gettempdir())

    # ══ std/uuid（SL1）══
    def _builtin_uuid_uuid4(self, args: List[RuntimeValue]) -> RuntimeValue:
        """uuid_uuid4() — 随机 UUID(带连字符)"""
        import uuid as _uuid
        if args:
            raise TypeError("uuid_uuid4() 无参数")
        return StringValue(str(_uuid.uuid4()))

    def _builtin_uuid_uuid4_hex(self, args: List[RuntimeValue]) -> RuntimeValue:
        """uuid_uuid4_hex() — 随机 UUID(32 位无连字符)"""
        import uuid as _uuid
        if args:
            raise TypeError("uuid_uuid4_hex() 无参数")
        return StringValue(_uuid.uuid4().hex)

    # ══ std/hashlib（SL1）══
    def _hash_text(self, algo: str, args: List[RuntimeValue]) -> RuntimeValue:
        import hashlib as _hl
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError(f"{algo}() 期望1个字符串参数(text)")
        h = _hl.new(algo)
        h.update(args[0].value.encode('utf-8'))
        return StringValue(h.hexdigest())

    def _builtin_hash_md5(self, args: List[RuntimeValue]) -> RuntimeValue:
        """hash_md5(text) — MD5 十六进制摘要"""
        return self._hash_text('md5', args)

    def _builtin_hash_sha1(self, args: List[RuntimeValue]) -> RuntimeValue:
        """hash_sha1(text) — SHA-1 十六进制摘要"""
        return self._hash_text('sha1', args)

    def _builtin_hash_sha256(self, args: List[RuntimeValue]) -> RuntimeValue:
        """hash_sha256(text) — SHA-256 十六进制摘要"""
        return self._hash_text('sha256', args)

    def _builtin_hash_sha512(self, args: List[RuntimeValue]) -> RuntimeValue:
        """hash_sha512(text) — SHA-512 十六进制摘要"""
        return self._hash_text('sha512', args)

    # ══ std/hmac（SL1）══
    def _builtin_hmac_sha256(self, args: List[RuntimeValue]) -> RuntimeValue:
        """hmac_sha256(key, msg) — HMAC-SHA256 十六进制摘要"""
        import hmac as _hmac, hashlib as _hl
        if len(args) != 2 or not all(isinstance(a, StringValue) for a in args):
            raise TypeError("hmac_sha256() 期望2个字符串参数(key, msg)")
        mac = _hmac.new(args[0].value.encode('utf-8'),
                        args[1].value.encode('utf-8'), _hl.sha256)
        return StringValue(mac.hexdigest())

    def _builtin_hmac_sha256_verify(self, args: List[RuntimeValue]) -> RuntimeValue:
        """hmac_sha256_verify(key, msg, sig) — 常量时间比对签名"""
        import hmac as _hmac, hashlib as _hl
        if len(args) != 3 or not all(isinstance(a, StringValue) for a in args):
            raise TypeError("hmac_sha256_verify() 期望3个字符串参数(key, msg, sig)")
        mac = _hmac.new(args[0].value.encode('utf-8'),
                        args[1].value.encode('utf-8'), _hl.sha256)
        return BoolValue(_hmac.compare_digest(mac.hexdigest(), args[2].value))

    # ══ std/secrets（SL1）══
    def _builtin_secrets_token_hex(self, args: List[RuntimeValue]) -> RuntimeValue:
        """secrets_token_hex(n) — n 字节安全随机数的十六进制(2n 字符)"""
        import secrets as _secrets
        if len(args) != 1 or not isinstance(args[0], IntValue) or args[0].value < 0:
            raise TypeError("secrets_token_hex() 期望1个非负整数参数(n)")
        return StringValue(_secrets.token_hex(args[0].value))

    def _builtin_secrets_rand_below(self, args: List[RuntimeValue]) -> RuntimeValue:
        """secrets_rand_below(n) — [0, n) 安全随机整数"""
        import secrets as _secrets
        if len(args) != 1 or not isinstance(args[0], IntValue) or args[0].value <= 0:
            raise TypeError("secrets_rand_below() 期望1个正整数参数(n)")
        return IntValue(_secrets.randbelow(args[0].value))

    def _builtin_secrets_choice(self, args: List[RuntimeValue]) -> RuntimeValue:
        """secrets_choice(lst) — 列表安全随机取一(空表抛 ValueError)"""
        import secrets as _secrets
        if len(args) != 1 or not isinstance(args[0], ListValue):
            raise TypeError("secrets_choice() 期望1个列表参数(lst)")
        if not args[0].value:
            raise ValueError("secrets_choice() 不能从空列表选择")
        return _secrets.choice(args[0].value)

    # ══ std/decimal（SL1）══
    # 表示法约定: Decimal 以字符串承载("12.34"), 运算走 Python decimal
    # (任意精度, 二进制浮点误差自此绝缘), 结果一律返回规范化字符串。
    def _decimal_parse(self, s: str):
        from decimal import Decimal, InvalidOperation
        try:
            return Decimal(s)
        except InvalidOperation:
            raise ValueError(f"无效的十进制数字: {s}")

    def _builtin_decimal_add(self, args: List[RuntimeValue]) -> RuntimeValue:
        """decimal_add(a, b) — 精确加法(字符串进, 字符串出)"""
        if len(args) != 2 or not all(isinstance(a, StringValue) for a in args):
            raise TypeError("decimal_add() 期望2个字符串参数(a, b)")
        return StringValue(str(self._decimal_parse(args[0].value)
                               + self._decimal_parse(args[1].value)))

    def _builtin_decimal_sub(self, args: List[RuntimeValue]) -> RuntimeValue:
        """decimal_sub(a, b) — 精确减法"""
        if len(args) != 2 or not all(isinstance(a, StringValue) for a in args):
            raise TypeError("decimal_sub() 期望2个字符串参数(a, b)")
        return StringValue(str(self._decimal_parse(args[0].value)
                               - self._decimal_parse(args[1].value)))

    def _builtin_decimal_mul(self, args: List[RuntimeValue]) -> RuntimeValue:
        """decimal_mul(a, b) — 精确乘法"""
        if len(args) != 2 or not all(isinstance(a, StringValue) for a in args):
            raise TypeError("decimal_mul() 期望2个字符串参数(a, b)")
        return StringValue(str(self._decimal_parse(args[0].value)
                               * self._decimal_parse(args[1].value)))

    def _builtin_decimal_div(self, args: List[RuntimeValue]) -> RuntimeValue:
        """decimal_div(a, b) — 精确除法(28 位精度, 除零抛 ZeroDivisionError)"""
        if len(args) != 2 or not all(isinstance(a, StringValue) for a in args):
            raise TypeError("decimal_div() 期望2个字符串参数(a, b)")
        b = self._decimal_parse(args[1].value)
        if b == 0:
            raise ZeroDivisionError("decimal_div() 除数不能为零")
        return StringValue(str(self._decimal_parse(args[0].value) / b))

    def _builtin_decimal_compare(self, args: List[RuntimeValue]) -> RuntimeValue:
        """decimal_compare(a, b) — 精确比较: a>b→1, a<b→-1, 相等→0"""
        if len(args) != 2 or not all(isinstance(a, StringValue) for a in args):
            raise TypeError("decimal_compare() 期望2个字符串参数(a, b)")
        a = self._decimal_parse(args[0].value)
        b = self._decimal_parse(args[1].value)
        return IntValue(1 if a > b else (-1 if a < b else 0))

    # ══ std/memory（MM1: 引用计数观测 + 循环回收）══
    def _builtin_mem_live_count(self, args: List[RuntimeValue]) -> RuntimeValue:
        """mem_live_count() — 当前存活的容器对象数(注册表观测)"""
        if args:
            raise TypeError("mem_live_count() 无参数")
        return IntValue(OBJECT_REGISTRY.live())

    def _builtin_mem_alloc_total(self, args: List[RuntimeValue]) -> RuntimeValue:
        """mem_alloc_total() — 累计创建的容器对象数"""
        if args:
            raise TypeError("mem_alloc_total() 无参数")
        return IntValue(OBJECT_REGISTRY.alloc_total)

    def _builtin_mem_stats_info(self, args: List[RuntimeValue]) -> RuntimeValue:
        """mem_stats_info() — 内存统计字典(live/alloc_total/reclaim_total/by_type)"""
        if args:
            raise TypeError("mem_stats_info() 无参数")
        st = OBJECT_REGISTRY.stats()
        d = DictValue()
        d.value["live"] = IntValue(st["live"])
        d.value["alloc_total"] = IntValue(st["alloc_total"])
        d.value["reclaim_total"] = IntValue(st["reclaim_total"])
        by_type = DictValue()
        for k, v in st["by_type"].items():
            by_type.value[k] = IntValue(v)
        d.value["by_type"] = by_type
        return d

    def _builtin_gc_collect_now(self, args: List[RuntimeValue]) -> RuntimeValue:
        """gc_collect_now() — 触发循环垃圾回收, 返回本次回收的容器数"""
        if args:
            raise TypeError("gc_collect_now() 无参数")
        return IntValue(OBJECT_REGISTRY.collect())

    def _builtin_ref_count_of(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ref_count_of(obj) — 对象的宿主引用计数(观测值, 含解释器内部引用)"""
        import sys as _sys
        if len(args) != 1:
            raise TypeError("ref_count_of() 期望1个参数(obj)")
        return IntValue(_sys.getrefcount(args[0]) - 1)

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

    def _builtin_round(self, args: List[RuntimeValue]) -> RuntimeValue:
        """round(x: Float) — 四舍五入"""
        if len(args) != 1:
            raise TypeError(f"round() 期望1个参数,得到 {len(args)}个")
        return IntValue(int(round(float(args[0].value))))

    def _builtin_log(self, args: List[RuntimeValue]) -> RuntimeValue:
        """log(x: Float, base: Float = e) — 对数"""
        import math
        if len(args) < 1 or len(args) > 2:
            raise TypeError(f"log() 期望1-2个参数,得到 {len(args)}个")
        x = float(args[0].value)
        if len(args) == 2:
            return FloatValue(math.log(x, float(args[1].value)))
        return FloatValue(math.log(x))

    def _builtin_exp(self, args: List[RuntimeValue]) -> RuntimeValue:
        """exp(x: Float) — e^x"""
        import math
        if len(args) != 1:
            raise TypeError(f"exp() 期望1个参数,得到 {len(args)}个")
        return FloatValue(math.exp(float(args[0].value)))


    # ══ 三角函数 (math) ──
    def _builtin_cos(self, args: List[RuntimeValue]) -> RuntimeValue:
        """cos(angle_rad: Float) — 余弦"""
        import math
        if len(args) != 1:
            raise TypeError(f"cos() 期望1个参数,得到 {len(args)}个")
        return FloatValue(math.cos(float(args[0].value)))

    def _builtin_sin(self, args: List[RuntimeValue]) -> RuntimeValue:
        """sin(angle_rad: Float) — 正弦"""
        import math
        if len(args) != 1:
            raise TypeError(f"sin() 期望1个参数,得到 {len(args)}个")
        return FloatValue(math.sin(float(args[0].value)))

    def _builtin_tan(self, args: List[RuntimeValue]) -> RuntimeValue:
        """tan(angle_rad: Float) — 正切"""
        import math
        if len(args) != 1:
            raise TypeError(f"tan() 期望1个参数,得到 {len(args)}个")
        return FloatValue(math.tan(float(args[0].value)))

    def _builtin_acos(self, args: List[RuntimeValue]) -> RuntimeValue:
        """acos(x: Float) — 反余弦"""
        import math
        if len(args) != 1:
            raise TypeError(f"acos() 期望1个参数,得到 {len(args)}个")
        return FloatValue(math.acos(float(args[0].value)))

    def _builtin_asin(self, args: List[RuntimeValue]) -> RuntimeValue:
        """asin(x: Float) — 反正弦"""
        import math
        if len(args) != 1:
            raise TypeError(f"asin() 期望1个参数,得到 {len(args)}个")
        return FloatValue(math.asin(float(args[0].value)))

    def _builtin_atan(self, args: List[RuntimeValue]) -> RuntimeValue:
        """atan(x: Float) — 反正切"""
        import math
        if len(args) != 1:
            raise TypeError(f"atan() 期望1个参数,得到 {len(args)}个")
        return FloatValue(math.atan(float(args[0].value)))

    def _builtin_atan2(self, args: List[RuntimeValue]) -> RuntimeValue:
        """atan2(y: Float, x: Float) — 四象限反正切"""
        import math
        if len(args) != 2:
            raise TypeError(f"atan2() 期望2个参数,得到 {len(args)}个")
        return FloatValue(math.atan2(float(args[0].value), float(args[1].value)))

    def _builtin_pi(self, args: List[RuntimeValue]) -> RuntimeValue:
        """pi() — 圆周率 π"""
        import math
        return FloatValue(math.pi)
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

    def _builtin_starts_with(self, args: List[RuntimeValue]) -> RuntimeValue:
        """starts_with(s: String, prefix: String) → Bool"""
        if len(args) != 2 or not isinstance(args[0], StringValue) or not isinstance(args[1], StringValue):
            raise TypeError("starts_with() 期望2个String参数")
        return BoolValue(args[0].value.startswith(args[1].value))

    def _builtin_ends_with(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ends_with(s: String, suffix: String) → Bool"""
        if len(args) != 2 or not isinstance(args[0], StringValue) or not isinstance(args[1], StringValue):
            raise TypeError("ends_with() 期望2个String参数")
        return BoolValue(args[0].value.endswith(args[1].value))

    def _builtin_replace(self, args: List[RuntimeValue]) -> RuntimeValue:
        """replace(s: String, old: String, new: String) → String"""
        if len(args) != 3 or not all(isinstance(a, StringValue) for a in args):
            raise TypeError("replace() 期望3个String参数")
        return StringValue(args[0].value.replace(args[1].value, args[2].value))

    def _builtin_to_upper(self, args: List[RuntimeValue]) -> RuntimeValue:
        """to_upper(s: String) → String"""
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("to_upper() 期望1个String参数")
        return StringValue(args[0].value.upper())

    def _builtin_to_lower(self, args: List[RuntimeValue]) -> RuntimeValue:
        """to_lower(s: String) → String"""
        if len(args) != 1 or not isinstance(args[0], StringValue):
            raise TypeError("to_lower() 期望1个String参数")
        return StringValue(args[0].value.lower())

    def _builtin_substr(self, args: List[RuntimeValue]) -> RuntimeValue:
        """substr(s: String, start: Int, end: Int) → String — 取子串 s[start..end)"""
        if len(args) != 3:
            raise TypeError(f"substr() 期望3个参数(字符串, 起始, 结束),得到 {len(args)}个")
        if not isinstance(args[0], StringValue):
            raise TypeError("substr() 第1个参数必须是String")
        start = int(args[1].value)
        end = int(args[2].value)
        s = args[0].value
        n = len(s)
        if start < 0:
            start = n + start
        if end < 0:
            end = n + end
        return StringValue(s[max(0, start):min(n, end)])

    # ══ sys ──
    def _builtin_version(self, args: List[RuntimeValue]) -> RuntimeValue:
        """version() — 返回 Intent 解释器版本"""
        return StringValue("Intent 1.0.0-alpha | 心学为体 禅道为翼 马哲为用")

    # ══ fs (文件系统) ──
    def _builtin_list_dir(self, args: List[RuntimeValue]) -> RuntimeValue:
        """list_dir(path: String) → List[String] — 列出目录内容"""
        if len(args) != 1:
            raise TypeError(f"list_dir() 期望1个参数,得到 {len(args)}个")
        entries = os.listdir(args[0].value)
        return ListValue([StringValue(e) for e in entries])

    def _builtin_file_exists(self, args: List[RuntimeValue]) -> RuntimeValue:
        """file_exists(path: String) → Bool — 检查文件/目录是否存在"""
        if len(args) != 1:
            raise TypeError(f"file_exists() 期望1个参数,得到 {len(args)}个")
        return BoolValue(os.path.exists(args[0].value))

    def _builtin_is_dir(self, args: List[RuntimeValue]) -> RuntimeValue:
        """is_dir(path: String) → Bool"""
        if len(args) != 1:
            raise TypeError(f"is_dir() 期望1个参数,得到 {len(args)}个")
        return BoolValue(os.path.isdir(args[0].value))

    def _builtin_is_file(self, args: List[RuntimeValue]) -> RuntimeValue:
        """is_file(path: String) → Bool"""
        if len(args) != 1:
            raise TypeError(f"is_file() 期望1个参数,得到 {len(args)}个")
        return BoolValue(os.path.isfile(args[0].value))

    def _builtin_make_dir(self, args: List[RuntimeValue]) -> RuntimeValue:
        """make_dir(path: String) — 创建目录"""
        if len(args) != 1:
            raise TypeError(f"make_dir() 期望1个参数,得到 {len(args)}个")
        os.makedirs(args[0].value, exist_ok=True)
        return NoneValue()

    def _builtin_delete_file(self, args: List[RuntimeValue]) -> RuntimeValue:
        """delete_file(path: String) — 删除文件"""
        if len(args) != 1:
            raise TypeError(f"delete_file() 期望1个参数,得到 {len(args)}个")
        os.remove(args[0].value)
        return NoneValue()

    def _builtin_file_size(self, args: List[RuntimeValue]) -> RuntimeValue:
        """file_size(path: String) → Int — 文件大小(字节)"""
        if len(args) != 1:
            raise TypeError(f"file_size() 期望1个参数,得到 {len(args)}个")
        return IntValue(os.path.getsize(args[0].value))

    def _builtin_file_modified(self, args: List[RuntimeValue]) -> RuntimeValue:
        """file_modified(path: String) → Float — 最后修改时间(Unix时间戳)"""
        if len(args) != 1:
            raise TypeError(f"file_modified() 期望1个参数,得到 {len(args)}个")
        return FloatValue(os.path.getmtime(args[0].value))

    # ══ os (操作系统) ──
    def _builtin_env(self, args: List[RuntimeValue]) -> RuntimeValue:
        """env(key: String) → String — 读取环境变量"""
        if len(args) != 1:
            raise TypeError(f"env() 期望1个参数,得到 {len(args)}个")
        val = os.environ.get(args[0].value, "")
        return StringValue(val)

    def _builtin_cwd(self, args: List[RuntimeValue]) -> RuntimeValue:
        """cwd() → String — 获取当前工作目录"""
        return StringValue(os.getcwd())

    def _builtin_ch_dir(self, args: List[RuntimeValue]) -> RuntimeValue:
        """ch_dir(path: String) — 切换工作目录"""
        if len(args) != 1:
            raise TypeError(f"ch_dir() 期望1个参数,得到 {len(args)}个")
        os.chdir(args[0].value)
        return NoneValue()

    def _builtin_shell(self, args: List[RuntimeValue]) -> RuntimeValue:
        """shell(cmd: String) → String — 执行 shell 命令并返回 stdout"""
        if len(args) != 1:
            raise TypeError(f"shell() 期望1个参数,得到 {len(args)}个")
        result = os.popen(args[0].value).read()
        return StringValue(result)

    def _builtin_platform(self, args: List[RuntimeValue]) -> RuntimeValue:
        """platform() → String — 返回操作系统平台"""
        return StringValue(sys.platform)

    def _builtin_path_join(self, args: List[RuntimeValue]) -> RuntimeValue:
        """path_join(a: String, b: String) → String — 拼接两个路径"""
        if len(args) != 2:
            raise TypeError(f"path_join() 期望2个参数,得到 {len(args)}个")
        return StringValue(os.path.join(args[0].value, args[1].value))

    def _builtin_path_basename(self, args: List[RuntimeValue]) -> RuntimeValue:
        """path_basename(path: String) → String — 提取文件名"""
        if len(args) != 1:
            raise TypeError(f"path_basename() 期望1个参数,得到 {len(args)}个")
        return StringValue(os.path.basename(args[0].value))

    def _builtin_path_dirname(self, args: List[RuntimeValue]) -> RuntimeValue:
        """path_dirname(path: String) → String — 提取目录名"""
        if len(args) != 1:
            raise TypeError(f"path_dirname() 期望1个参数,得到 {len(args)}个")
        return StringValue(os.path.dirname(args[0].value))

    def _builtin_path_ext(self, args: List[RuntimeValue]) -> RuntimeValue:
        """path_ext(path: String) → String — 提取扩展名"""
        if len(args) != 1:
            raise TypeError(f"path_ext() 期望1个参数,得到 {len(args)}个")
        _, ext = os.path.splitext(args[0].value)
        return StringValue(ext)

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

    def _apply_decorators(self, func: 'FunctionDef',
                          fv: 'FunctionValue') -> 'FunctionValue':
        """X1: 应用装饰器栈; 返回包装后的函数值

        每条装饰器两形态:
          @deco       — 裸形态: deco(fv)
          @deco(args) — 带参工厂: deco(args...)(fv), 先求值出真装饰器
        应用顺序 = 声明顺序(自上而下), 先应用者居内 — 末位装饰器最外
        (与 Python 的首位最外相反; 既有行为, 测试锁定)。
        提升期(execute_program)与语句期(execute_statement FunctionDef,
        VM 委托通道经此)共用 — 两引擎行为一致的唯一挂点。
        已知边界: 提升期早于顶层 import/let — 装饰器名或参数引用模块
        符号/顶层变量时找不到(spec §6 限制 21); 语句级 def(函数体内)
        执行时机在 import/let 之后, 不受此限。
        """
        for dec in func.decorators:
            dec_func = self.current_scope.get_opt(dec.name)
            # 作用域中没有则查解释器内部函数表
            if dec_func is None and dec.name in self.functions:
                dec_func = self.functions[dec.name]
            # 可能是原始 FunctionDef（scope 中存储的原始声明）
            if isinstance(dec_func, FunctionDef):
                dec_func = FunctionValue(dec_func, self.current_scope)
            if not isinstance(dec_func, FunctionValue):
                print(f"[警告] 装饰器 '{dec.name}' 未找到或不是函数")
                continue
            if dec.is_call:
                # 带参装饰器: deco(args...) → 真装饰器 → (fn)
                # 参数在当前作用域求值(提升期即全局作用域)
                arg_values = [self.evaluate_expression(a) for a in dec.args]
                dec_func = self._execute_method(dec_func, None, arg_values)
                if not isinstance(dec_func, FunctionValue):
                    print(f"[警告] 装饰器 '{dec.name}(...)' 未返回函数")
                    continue
            if isinstance(dec_func, FunctionValue):
                # decorator(fn) → 返回包装后的 FunctionValue
                dec_result = self._execute_method(dec_func, None, [fv])
                if isinstance(dec_result, FunctionValue):
                    fv = dec_result
            else:
                print(f"[警告] 装饰器 '{dec.name}' 未找到或不是函数")
        return fv

    def execute_program(self, program: Program, module_mode: bool = False) -> RuntimeValue:
        """执行整个程序
        module_mode=True 时只注册函数/变量,不执行main(用于模块加载)
        """
        # ── 语义分析遍(Resolver)──
        self._run_resolver(program)

        # 顶层入口: 重置调用栈(模块加载不清栈,保留外层调用链)
        if not module_mode:
            self.call_stack = []

        # 注册所有函数
        for func in program.functions.values():
            self.functions[func.name] = func
            # E3: def 行即执行(定义时刻) — 注册处打点, 与语句覆盖口径一致
            if self.coverage is not None and getattr(func, 'line', 0):
                self.coverage.mark_stmt(self.current_filename, func.line)
            # 顶层函数同时入全局作用域 — 函数是一等值(可作实参传递),
            # 不能只进 functions 表(那只支持按名调用)。
            # 闭包作用域 = 当前作用域(顶层即全局), 与旧行为一致。
            if not module_mode:
                self.current_scope.declare(
                    func.name, FunctionValue(func, self.current_scope),
                    False, allow_redefine=True)
            # 模块模式下同时写入当前作用域,供导入方使用
            if module_mode:
                self.current_scope.declare(func.name, func, False, allow_redefine=True)

            # ── 应用装饰器 ──
            if func.decorators:
                fv = self._apply_decorators(func, FunctionValue(func, self.current_scope))
                # 更新函数注册
                self.functions[func.name] = fv.func_def
                if not module_mode:
                    self.current_scope.declare(func.name, fv, False, allow_redefine=True)

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
            result = self.execute_function(self.functions['main'], [])

        return result

    def execute_statement(self, stmt: ASTNode) -> RuntimeValue:
        """执行语句"""
        self._track_node(stmt)
        # E3: 覆盖率打点 — 语句入口即视为执行(异常路径上的语句也已开始执行)
        if self.coverage is not None:
            line = getattr(stmt, 'line', 0)
            if line:
                self.coverage.mark_stmt(self.current_filename, line)
        # C7: 调试器 hook — 断点/单步命中即暂停进命令循环
        if self.debugger is not None:
            self.debugger.check(stmt)
        try:
            return self._execute_statement_safe(stmt)
        except (NameError, ValueError, TypeError, RuntimeError, IndexError, KeyError, ZeroDivisionError, AssertionError) as e:
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
        elif isinstance(stmt, MemberAssignment):
            return self.execute_member_assignment(stmt)
        elif isinstance(stmt, SubscriptAssignment):
            return self.execute_subscript_assignment(stmt)
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
        elif isinstance(stmt, EnumDef):
            return self.execute_enum_def(stmt)
        elif isinstance(stmt, AssertStmt):
            return self.execute_assert(stmt)
        elif isinstance(stmt, FunctionDef):
            # 嵌套函数定义：注册到当前作用域（闭包捕获）
            # X1: 装饰器在此应用 — VM 对带装饰器的 def 整条委托解释器,
            # 两引擎装饰语义一致的挂点(与 execute_program 提升期共用)
            func_val = FunctionValue(stmt, self.current_scope)
            if stmt.decorators:
                func_val = self._apply_decorators(stmt, func_val)
                self.functions[stmt.name] = func_val.func_def
            self.current_scope.declare(stmt.name, func_val)
            return func_val

        elif isinstance(stmt, TryStmt):
            return self.execute_try_stmt(stmt)
        elif isinstance(stmt, RaiseStmt):
            return self.execute_raise(stmt)
        elif isinstance(stmt, SpawnStmt):
            return self.execute_spawn(stmt)
        elif isinstance(stmt, ScopeStmt):
            return self.execute_scope(stmt)
        elif isinstance(stmt, WithStmt):
            return self.execute_with_stmt(stmt)
        elif isinstance(stmt, TypeAliasStmt):
            return self.execute_type_alias(stmt)
        elif isinstance(stmt, ExportStmt):
            # 显式导出声明(P2.1): 记录到当前模块的导出名单
            current_module = getattr(self, 'current_module', None)
            if current_module is not None:
                for name in stmt.exports:
                    current_module.explicit_exports.add(name)
            return IntValue(0)
        elif isinstance(stmt, DeferStmt):
            # 注册 defer 到当前作用域的 defer 栈
            self.current_scope.defer_stack.append(stmt.body)
            return IntValue(0)
        elif isinstance(stmt, YieldStmt):
            return self.execute_yield(stmt)
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
        # 别名解析(P1.3a): 别名是透明的同义词, 递归解析到底层类型
        seen = set()
        while type_name in self.type_aliases and type_name not in seen:
            seen.add(type_name)
            type_name = self.type_aliases[type_name]
        # Union 校验: 任一成员合法即通过(不二法门的推广)
        if ' | ' in type_name:
            members = [m.strip() for m in type_name.split('|')]
            for m in members:
                try:
                    self._check_type(value, m, context)
                    return
                except TypeError:
                    continue
            actual = value.get_type().name
            raise TypeError(f"类型不匹配{context}: 期望 {type_name},但得到 {actual}")
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

    def execute_member_assignment(self, stmt: MemberAssignment) -> RuntimeValue:
        """执行成员赋值: this.x = value 或 obj.field = value"""
        value = self.evaluate_expression(stmt.value)
        
        # 求值对象
        obj_val = self.evaluate_expression(stmt.obj)
        
        if not isinstance(obj_val, InstanceValue):
            raise TypeError(f"无法对非实例类型 {obj_val.get_type()} 进行成员赋值")
        
        if stmt.op == "=":
            obj_val.set(stmt.member, value)  # M2: 经 set() 写透缓存
        else:
            # 复合赋值
            old_val = obj_val.fields.get(stmt.member)
            if old_val is None:
                raise NameError(f"实例没有属性 '{stmt.member}'")
            if stmt.op == "+=":
                new_val = self._binary_op(old_val, "+", value)
            elif stmt.op == "-=":
                new_val = self._binary_op(old_val, "-", value)
            elif stmt.op == "*=":
                new_val = self._binary_op(old_val, "*", value)
            elif stmt.op == "/=":
                new_val = self._binary_op(old_val, "/", value)
            else:
                raise RuntimeError(f"不支持的成员赋值操作符: {stmt.op}")
            obj_val.set(stmt.member, new_val)  # M2: 经 set() 写透缓存
        
        return value

    def _exec_slice_assignment(self, obj, slice_expr: 'SliceExpr',
                               value: RuntimeValue, op: str) -> RuntimeValue:
        """S2a: 切片赋值 — l[a:b] = v

        语义对齐 Python: 步长限 1(扩展切片赋值未实现, 显式拒绝);
        右侧限列表, 允许增删长度(l[1:3] = [x] 把 2 元素换 1 元素);
        复合操作符(+= 等)不适用切片 — 显式拒绝不静默。
        """
        if op != '=':
            raise RuntimeError(f"切片赋值不支持复合操作符 '{op}'")
        if not isinstance(obj, ListValue):
            raise TypeError(f"不支持对 {obj.get_type()} 类型使用切片赋值")
        start = self.evaluate_expression(slice_expr.start).value if slice_expr.start else None
        end = self.evaluate_expression(slice_expr.end).value if slice_expr.end else None
        step = self.evaluate_expression(slice_expr.step).value if slice_expr.step else None
        if step is not None and step != 1:
            raise TypeError("扩展切片(带步长)赋值未实现 — 步长限 1")
        if not isinstance(value, ListValue):
            raise TypeError("切片赋值右侧必须是列表(替换语义, 允许增删长度)")
        obj.value[slice(start, end)] = list(value.value)
        return value

    def execute_subscript_assignment(self, stmt: SubscriptAssignment) -> RuntimeValue:
        """执行下标赋值: obj[key] = value"""
        obj_val = self.evaluate_expression(stmt.obj)
        # S2a: 切片赋值 l[a:b] = v — 索引是 SliceExpr 时不按值求值
        # (求值会变成切片读取, 语义相反)
        if isinstance(stmt.index, SliceExpr):
            value = self.evaluate_expression(stmt.value)
            return self._exec_slice_assignment(obj_val, stmt.index, value, stmt.op)
        index = self.evaluate_expression(stmt.index)
        value = self.evaluate_expression(stmt.value)

        # 原生类型: List 和 Dict
        if isinstance(obj_val, ListValue):
            idx = index.value
            if idx < 0:
                idx = len(obj_val.value) + idx
            if idx < 0 or idx >= len(obj_val.value):
                raise IndexError(f"列表索引 {idx} 越界")
            if stmt.op == "=":
                obj_val.value[idx] = value
            else:
                old_val = obj_val.value[idx]
                if stmt.op == "+=":
                    new_val = self._binary_op(old_val, "+", value)
                elif stmt.op == "-=":
                    new_val = self._binary_op(old_val, "-", value)
                elif stmt.op == "*=":
                    new_val = self._binary_op(old_val, "*", value)
                elif stmt.op == "/=":
                    new_val = self._binary_op(old_val, "/", value)
                else:
                    raise RuntimeError(f"不支持的下标赋值操作符: {stmt.op}")
                obj_val.value[idx] = new_val
            return value

        if isinstance(obj_val, DictValue):
            if stmt.op == "=":
                obj_val.value[self._dict_key(index)] = value
            else:
                old_val = obj_val.value.get(self._dict_key(index))
                if old_val is None:
                    raise KeyError(f"字典中没有键 '{index.value}'")
                if stmt.op == "+=":
                    new_val = self._binary_op(old_val, "+", value)
                elif stmt.op == "-=":
                    new_val = self._binary_op(old_val, "-", value)
                elif stmt.op == "*=":
                    new_val = self._binary_op(old_val, "*", value)
                elif stmt.op == "/=":
                    new_val = self._binary_op(old_val, "/", value)
                else:
                    raise RuntimeError(f"不支持的下标赋值操作符: {stmt.op}")
                obj_val.value[self._dict_key(index)] = new_val
            return value

        # 运算符重载: __setitem__(key, value)
        if isinstance(obj_val, InstanceValue):
            method = obj_val.get('__setitem__')
            if method and isinstance(method, FunctionValue):
                return self._execute_method(method, obj_val, [index, value])

        raise TypeError(f"不支持对 {obj_val.get_type()} 类型使用下标赋值 []")

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

    def _dunder_next(self, iterator: 'InstanceValue') -> RuntimeValue:
        """X3: 调用迭代器的 __next__(); 返回 None 表示耗尽(语言约定:
        迭代器没有 StopIteration 异常通道, __next__() 返回 None 即序列终点)"""
        method = iterator.get('__next__')
        if method is None or not isinstance(method, FunctionValue):
            raise TypeError(f"对象没有 __next__() 方法, 不是迭代器")
        return self._execute_method(method, iterator, [])

    def _drain_iterator(self, iterator: 'InstanceValue') -> 'ListValue':
        """X3: 预取迭代器全部元素为列表(树遍历执行器的惰性边界)

        解释器无挂起协程式迭代通道, 自定义迭代器在此边界预取;
        生成器(GeneratorValue)仍是真惰性, 不受此影响。
        安全上限 100 万项 — 防忘写终止条件时无限循环拖死进程。
        """
        items = []
        while True:
            nxt = self._dunder_next(iterator)
            if isinstance(nxt, NoneValue):
                break
            items.append(nxt)
            if len(items) >= 1_000_000:
                raise TypeError("迭代超过 100 万项仍未结束, 疑似 __next__() 缺少终止条件")
        return ListValue(items, AnyType())

    def execute_for(self, stmt: ForStmt) -> RuntimeValue:
        """执行for循环"""
        result = IntValue(0)

        # 获取可迭代对象
        iterable = self.evaluate_expression(stmt.iterable)

        if isinstance(iterable, DictValue):
            # 字典遍历: for (k, v) in dict 或 for k in dict(遍历keys)
            for key, val in iterable.value.items():
                old_scope = self.current_scope
                self.current_scope = self.current_scope.enter()

                if stmt.vars and len(stmt.vars) >= 2:
                    self.current_scope.declare(stmt.vars[0], StringValue(key), False)
                    self.current_scope.declare(stmt.vars[1], val.copy(), False)
                elif stmt.vars and len(stmt.vars) == 1:
                    self.current_scope.declare(stmt.vars[0], StringValue(key), False)
                else:
                    self.current_scope.declare(stmt.var, StringValue(key), False)

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

        if not isinstance(iterable, ListValue):
            # S3: 生成器 — 真惰性遍历(逐项 pull, 不预取; 无限生成器可用)
            if isinstance(iterable, GeneratorValue):
                pass  # 下方统一循环换懒求值源
            # 运算符重载: __iter__() 返回 ListValue 或迭代器对象
            elif isinstance(iterable, InstanceValue):
                method = iterable.get('__iter__')
                if method and isinstance(method, FunctionValue):
                    result = self._execute_method(method, iterable, [])
                    if isinstance(result, ListValue):
                        iterable = result
                    elif isinstance(result, InstanceValue) and result.get('__next__') is not None:
                        # X3: __iter__ 返回迭代器(有 __next__) — 预取为列表后统一遍历
                        iterable = self._drain_iterator(result)
                    else:
                        raise TypeError(f"__iter__() 必须返回列表或迭代器,得到 {result.get_type()}")
                elif iterable.get('__next__') is not None:
                    # X3: 无 __iter__ 但有 __next__ — 自身即迭代器
                    iterable = self._drain_iterator(iterable)
                else:
                    raise TypeError(f"for 循环期望 List/Dict/有__iter__的对象,得到 {iterable.type}")
            else:
                raise TypeError(f"for 循环期望 List/Dict,得到 {iterable.type}")

        # S3: 生成器走懒源(break/return/异常 提前退出 → 收摊协程线程,
        # 对齐 Python 生成器被 GC 时关闭); List 原样枚举
        items_source = (iterable.value if isinstance(iterable, ListValue)
                        else _gen_lazy_items(iterable))

        for item_idx, item in enumerate(items_source):
            # 进入循环体作用域
            old_scope = self.current_scope
            self.current_scope = self.current_scope.enter()

            # 设置循环变量
            if stmt.vars:
                # 解包模式: for (i, x) in items
                # i = 索引, x = 值
                idx_val = IntValue(item_idx)
                self.current_scope.declare(stmt.vars[0], idx_val, False)
                if len(stmt.vars) > 1:
                    self.current_scope.declare(stmt.vars[1], item.copy(), False)
            else:
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

    def _check_constraint(self, type_name: str, constraint: str) -> bool:
        """泛型约束检查(P1.3b) — 内置能力约束

        Comparable: 支持排序比较的类型(心即理: 能比较才配进入比较的函数)
        Numeric:    数值类型
        未知约束宽容放行(与 _check_type 对未知类型的策略一致)
        """
        if constraint == 'Any':
            return True
        if constraint == 'Comparable':
            return type_name in ('Int', 'Float', 'String', 'Bool')
        if constraint == 'Numeric':
            return type_name in ('Int', 'Float')
        return True

    def _make_error_value(self, e: Exception) -> 'ErrorValue':
        """把 Python/Intent 异常包装为 Intent 异常值(P1.4)

        类型名经 PY_TO_INTENT_EXC 映射(ContractViolation→ContractError),
        消息取首行(去除 _error_context 的多行位置信息),
        栈取异常穿帧快照(顶层则为当前调用栈)。
        """
        # EX1: raise 抛出的错误值原样进 catch(类型/消息/因果链不丢)
        if isinstance(e, IntentRaise):
            ev = e.error_value
            if not ev.stack:
                ev.stack = [StringValue(repr(fr)) for fr in
                            (getattr(e, '_intent_stack', None) or self.call_stack)]
            return ev
        py_type = type(e).__name__
        intent_type = PY_TO_INTENT_EXC.get(py_type, py_type)
        msg = str(e)
        if '\n' in msg:
            msg = msg.split('\n')[0]
        stack = getattr(e, '_intent_stack', None) or self.call_stack
        stack_vals = [StringValue(repr(fr)) for fr in stack]
        return ErrorValue(intent_type, msg, stack_vals)

    def execute_type_alias(self, stmt: 'TypeAliasStmt') -> RuntimeValue:
        """执行类型别名定义(P1.3a) — 注册透明同义词"""
        self.type_aliases[stmt.name] = stmt.aliased_type
        return IntValue(0)

    def execute_with_stmt(self, stmt: 'WithStmt') -> RuntimeValue:
        """执行 with 语句(P1.1) — 块级资源管理

        获取资源 → 绑定 as 名 → 执行块 → finally 释放。
        X3 协议化: 实例提供 __enter__/__exit__ 时走上下文管理器协议
        (__enter__ 的返回值绑定 as 名, __exit__ 收退出时的错误值);
        否则维持原约定 — as 名绑定资源本身, 块退出调 close()。
        获取与释放在同一对花括号内对称出现 — defer 的块级特化。
        """
        resource = self.evaluate_expression(stmt.resource)
        old_scope = self.current_scope
        self.current_scope = self.current_scope.enter()
        # X3: __enter__ 优先 — 其返回值才是 as 名绑定的值(Python 语义)
        entered = resource
        if isinstance(resource, InstanceValue):
            enter_method = resource.get('__enter__')
            if enter_method is not None and isinstance(enter_method, FunctionValue):
                entered = self._execute_method(enter_method, resource, [])
        if stmt.var_name:
            self.current_scope.declare(stmt.var_name, entered, False)
        result = IntValue(0)
        exc_val = None
        try:
            for body_stmt in stmt.body:
                result = self.execute_statement(body_stmt)
                if self.return_flag or self.break_flag or self.continue_flag:
                    break
        except Exception as e:
            # X3: 块内异常打包为错误值交给 __exit__(exc_type, exc_val, tb 的
            # 最小切片 — 单参传错误值; 返回值暂不承担抑制语义, 异常照常传播)
            try:
                exc_val = self._make_error_value(e)
            except Exception:
                exc_val = NoneValue()
            raise
        finally:
            # 释放: 实例提供 __exit__ 则调用; 否则 close 方法则调用 — 清理在等待中
            if isinstance(resource, InstanceValue):
                exit_method = resource.get('__exit__')
                if exit_method is not None and isinstance(exit_method, FunctionValue):
                    self._execute_method(exit_method, resource,
                                         [exc_val if exc_val is not None else NoneValue()])
                else:
                    close_method = resource.klass.find_method('close')
                    if close_method is not None:
                        self._execute_method(close_method, resource, [])
            self.current_scope = old_scope
        return result

    def execute_try_stmt(self, stmt: 'TryStmt') -> RuntimeValue:
        """执行 try-catch 语句"""
        result = IntValue(0)
        try:
            # 执行 try 块
            old_scope = self.current_scope
            self.current_scope = self.current_scope.enter()
            for body_stmt in stmt.try_body:
                result = self.execute_statement(body_stmt)
                if self.return_flag or self.break_flag or self.continue_flag:
                    break
            self.current_scope = old_scope
        except Exception as e:
            # 恢复作用域
            self.current_scope = old_scope
            # P1.4: 包装为 Intent 异常值(错误作为一等值)
            err_val = self._make_error_value(e)
            # 类型过滤: catch_types 非空且不匹配 → 继续传播
            if stmt.catch_types and err_val.err_type not in stmt.catch_types:
                raise
            # 进入 catch 块
            self.current_scope = self.current_scope.enter()
            # 绑定错误变量(ErrorValue: .type/.message/.stack)
            self.current_scope.declare(stmt.catch_var, err_val, False)
            for body_stmt in stmt.catch_body:
                result = self.execute_statement(body_stmt)
                if self.return_flag or self.break_flag or self.continue_flag:
                    break
            self.current_scope = old_scope
        finally:
            # 执行 finally 块（如果有）
            if stmt.finally_body:
                old_scope = self.current_scope
                self.current_scope = self.current_scope.enter()
                for body_stmt in stmt.finally_body:
                    self.execute_statement(body_stmt)
                self.current_scope = old_scope
        return result

    def execute_raise(self, stmt: 'RaiseStmt') -> RuntimeValue:
        """执行 raise(EX1): 把错误值抛回控制流; from Y 显式挂因果链"""
        err = self._coerce_error_value(self.evaluate_expression(stmt.value))
        if stmt.cause is not None:
            err.cause = self._coerce_error_value(
                self.evaluate_expression(stmt.cause))
        raise IntentRaise(err)

    def _coerce_error_value(self, val) -> 'ErrorValue':
        """raise 目标归一为 ErrorValue: ErrorValue 原样; Err(e) 取内层;
        字符串 → RuntimeError 简写; 其余明确拒绝(不静然猜测)。"""
        if isinstance(val, ErrorValue):
            return val
        if isinstance(val, ResultValue) and not val.is_ok:
            inner = val.err_value
            if isinstance(inner, ErrorValue):
                return inner
            return ErrorValue("ResultError", str(inner))
        if isinstance(val, StringValue):
            return ErrorValue("RuntimeError", val.value)
        raise TypeError(
            f"raise 期望错误值(error() 构造 / Err() / 字符串简写), "
            f"得到 {type(val).__name__}")

    def execute_spawn(self, stmt: 'SpawnStmt') -> RuntimeValue:
        """spawn(CC1): 派生线程任务, 登记进当前 scope 的任务表

        调用点求值(参数在 spawn 处定格), 线程里只负责执行 —
        structured concurrency: 没有孤儿线程, scope 退出统一 join。
        """
        if not self._spawn_stack:
            raise RuntimeError(
                "spawn 必须在 scope 块内(结构化并发: 不允许孤儿线程)")
        expr = stmt.expr
        if isinstance(expr, CallExpr):
            callee_expr = expr.func
            if isinstance(callee_expr, (Variable, MemberAccess)):
                callee = self.evaluate_expression(callee_expr)
            elif isinstance(callee_expr, str):
                callee = self.current_scope.get(callee_expr)
            else:
                raise RuntimeError("spawn 的调用目标无法解析")
            args = [self.evaluate_expression(a) for a in expr.args]
        else:
            callee = self.evaluate_expression(expr)
            args = []
        if not isinstance(callee, FunctionValue) and not callable(callee):
            raise TypeError("spawn 期望可调用对象(函数/闭包/lambda)")
        task = _SpawnTask(callee, args)
        self._spawn_stack[-1].append(task)
        task.start()
        return NoneValue()

    def execute_scope(self, stmt: 'ScopeStmt') -> RuntimeValue:
        """scope 块(CC1): 执行块, 退出时自动 join 全部派生任务

        任务异常在 join 处重抛(第一个) — 并发的错误不沉没。
        return/break/continue 穿透语义与其他块语句一致。
        """
        tasks = []
        self._spawn_stack.append(tasks)
        old_scope = self.current_scope
        self.current_scope = self.current_scope.enter()
        result = IntValue(0)
        try:
            for body_stmt in stmt.body:
                result = self.execute_statement(body_stmt)
                if self.return_flag or self.break_flag or self.continue_flag:
                    break
        finally:
            self.current_scope = old_scope
            self._spawn_stack.pop()
            # 结构化并发的核心: 作用域退出 = 全部任务汇合点
            first_error = None
            for task in tasks:
                task.join()
                if task.error is not None and first_error is None:
                    first_error = task.error
            if first_error is not None:
                raise first_error
        return result

    def execute_assert(self, stmt: 'AssertStmt'):
        """执行断言"""
        cond = self.evaluate_expression(stmt.condition)
        if not cond.value:
            if stmt.message:
                msg = self.evaluate_expression(stmt.message)
                raise AssertionError(f"断言失败: {msg.value}")
            else:
                raise AssertionError(f"断言失败: {stmt.condition}")
        return NoneValue()

    def execute_match(self, expr: 'MatchExpr', context: dict = None) -> RuntimeValue:
        """执行 match 表达式"""
        match_value = self.evaluate_expression(expr.value, context)

        # ── 枚举穷举性检查 ──
        if isinstance(match_value, EnumValue):
            covered = set()
            has_wildcard = False
            for case in expr.cases:
                patterns = self._flatten_or_pattern(case.pattern)
                for p in patterns:
                    if isinstance(p, (WildcardPattern, VariablePattern)):
                        has_wildcard = True
                    elif isinstance(p, EnumPattern):
                        if p.enum_name == match_value.enum_name:
                            covered.add(p.variant)
            if not has_wildcard:
                all_variants = set(self._get_enum_variants(match_value.enum_name))
                missing = all_variants - covered
                if missing:
                    raise MatchError(
                        f"match 未穷举枚举 '{match_value.enum_name}' 的变体: {', '.join(sorted(missing))}",
                        expr.line)

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

        if isinstance(pattern, EnumPattern):
            if not isinstance(value, EnumValue):
                return False
            return value.enum_name == pattern.enum_name and value.variant == pattern.variant

        raise MatchError(f"不支持的匹配模式: {type(pattern).__name__}")

    def _flatten_or_pattern(self, pattern) -> list:
        """展平或模式为叶子模式列表"""
        if isinstance(pattern, OrPattern):
            result = []
            for p in pattern.patterns:
                result.extend(self._flatten_or_pattern(p))
            return result
        return [pattern]

    def _get_enum_variants(self, enum_name: str) -> List[str]:
        """获取枚举的所有变体名"""
        return self.enum_registry.get(enum_name, [])


    def execute_break(self) -> RuntimeValue:
        """执行break语句"""
        self.break_flag = True
        return IntValue(0)

    def execute_yield(self, stmt) -> RuntimeValue:
        """S3: 执行 yield — 真惰性握手(线程协作式协程)

        生成器线程内: 值经控制器 out_q 交出, 阻塞等驱动线程的下一个
        动作; send 进来的值作为 yield 表达式的值返回(`let x = yield v`)。
        yield from expr(P1.5): 委派转发 — 生成器源逐项 pull 且 send
        值透传(对齐 Python yield from); 列表/字典源逐项交出。
        """
        ctrl = getattr(self, '_active_gen', None)
        if ctrl is None:
            raise RuntimeError("yield 只能在生成器函数中使用")

        if getattr(stmt, 'from_expr', None) is not None:
            src = self.evaluate_expression(stmt.from_expr)
            if isinstance(src, GeneratorValue):
                # 生成器委派: 逐项 pull 内层, send 值透传
                sent = None
                while True:
                    item = src._ctrl._resume('send', sent, owner=ctrl)
                    if item is _GEN_DONE:
                        break
                    sent = ctrl.do_yield(item)
                return NoneValue()
            if isinstance(src, ListValue):
                items = list(src.value)
            elif isinstance(src, DictValue):
                # 键归一为 Python 标量 — 转回 Intent 值再交出
                # (旧版直接把 str 键塞缓冲区, len 断言掩盖了类型洞)
                items = [_py_to_intent(k) for k in src.value.keys()]
            else:
                raise TypeError(f"yield from 期望列表/字典/生成器,得到 {src.type}")
            for item in items:
                ctrl.do_yield(item)
            return NoneValue()

        # 裸 yield 产出 None(对齐 Python; 旧版为 IntValue(0), S3 起迁移)
        value = self.evaluate_expression(stmt.value) if stmt.value else NoneValue()
        return ctrl.do_yield(value)

    def execute_continue(self) -> RuntimeValue:
        """执行continue语句"""
        self.continue_flag = True
        return IntValue(0)

    def _load_python_bridge_module(self, module_name: str):
        """I2a: import python.X — importlib 加载真 Python 模块, 包成桥作用域

        返回 Scope(namespace_only=True); 加载失败打印警告返回 None
        (与 std 模块找不到时的宽模式一致 — 运行期显式失败兜底)。
        """
        import importlib
        py_name = module_name[len('python.'):]
        try:
            mod = importlib.import_module(py_name)
        except ImportError as e:
            print(f"[警告] python 桥加载失败: {py_name}: {e}")
            return None
        scope = Scope(parent=self.global_scope)
        scope.namespace_only = True  # 符号只挂命名空间, 不平扁注入
        for name in dir(mod):
            if name.startswith('_'):
                continue  # 私有属性不过桥
            try:
                attr = getattr(mod, name)
            except Exception:
                continue  # 探测性属性抛错的不拦(某些模块 __getattr__ 挑剔)
            if callable(attr):
                scope.declare(name, PyFuncValue(attr, f"{py_name}.{name}"),
                              False, allow_redefine=True)
            else:
                scope.declare(name, _py_to_intent(attr), False,
                              allow_redefine=True)
        return scope

    def execute_import(self, stmt: ImportStmt) -> RuntimeValue:
        """执行import语句"""
        module_name = stmt.module_name
        alias = stmt.alias if stmt.alias else module_name

        # 检查模块是否已加载(缓存)
        if module_name in self.modules:
            module_scope = self.modules[module_name]
        elif module_name.startswith('python.'):
            # ── I2a: Python 互操作桥 — import python.X 加载真 Python 模块 ──
            module_scope = self._load_python_bridge_module(module_name)
            if module_scope is None:
                return IntValue(0)
            self.modules[module_name] = module_scope
        else:
            # ── 循环依赖检测 ──
            if module_name in self._import_stack:
                cycle = ' → '.join(self._import_stack[self._import_stack.index(module_name):] + [module_name])
                print(f"[警告] 检测到模块循环依赖: {cycle}")
                return IntValue(0)
            self._import_stack.append(module_name)
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
                # 弹出导入栈
                self._import_stack.pop()

            except Exception as e:
                self._import_stack.pop() if self._import_stack and self._import_stack[-1] == module_name else None
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
        # I2a: python.* 桥模块 namespace_only=True — 符号只挂命名空间链,
        # 不平扁注入(防遮蔽核心内置), 但末段名独立可用(math.sqrt 而非
        # 只有 python.math.sqrt — 与 std 扁平注入的边界偏差是刻意设计)
        _namespace_only = getattr(module_scope_obj, 'namespace_only', False)
        for name, value in module_scope_obj.symbols.items():
            if hasattr(value, 'body'):
                # 函数: 包成 FunctionValue（闭包=模块作用域）
                fv = FunctionValue(value, module_scope_obj)
                cursor_scope.declare(name, fv, False, allow_redefine=True)
                if not _namespace_only:
                    # 同时注入当前作用域（供模块内裸名调用）
                    self.current_scope.declare(name, fv, False, allow_redefine=True)
                full_name = f"{alias}.{name}"
                self.functions[full_name] = fv
            else:
                cursor_scope.declare(name, value, False, allow_redefine=True)
                if not _namespace_only:
                    # 同时注入当前作用域（供模块内裸名调用，如 ClassValue/Module 等非函数值）
                    self.current_scope.declare(name, value, False, allow_redefine=True)
        if _namespace_only and len(alias_parts) > 1:
            # python.X → X 独立可用(命名空间成员, 非扁平符号洪峰)
            self.current_scope.declare(alias_parts[-1], cursor_val, False,
                                       allow_redefine=True)

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
            # 尝试 base/std/math.intent(扁平模块)
            candidate = os.path.join(base, path_parts + '.intent')
            if os.path.exists(candidate):
                return candidate
            # 尝试 base/std/math/__init__.intent(目录包)
            candidate_init = os.path.join(base, path_parts, '__init__.intent')
            if os.path.exists(candidate_init):
                return candidate_init
            # 尝试 base/std/math/math.intent(P2.1 npm 风格: 包目录内含同名主文件)
            candidate_named = os.path.join(base, path_parts,
                                           path_parts.split(os.sep)[-1] + '.intent')
            if os.path.exists(candidate_named):
                return candidate_named

        return None

    def execute_function(self, func, args: List[RuntimeValue],
                         closure_scope: Optional[Scope] = None,
                         gen_mode: bool = False) -> RuntimeValue:
        """执行函数(带调用栈跟踪) — 委托 _execute_function_inner

        gen_mode=True: 由生成器协程线程驱动 — 不建控制器, 直接跑体
        (yield 在执行内握手挂起; 帧入栈/快照/弹栈仍走本通道)。
        """
        fd = func.func_def if isinstance(func, FunctionValue) else func
        frame_name = getattr(fd, 'name', '<lambda>')
        # 调用发生处的行号;顶层调用(如 main)无发生行,用函数定义行兜底
        frame_line = self.current_line or getattr(fd, 'line', 0) or 0
        frame = CallFrame(frame_name, frame_line, self.current_col,
                          self.current_filename)
        self.call_stack.append(frame)
        prof = self.profiler
        if prof is not None:
            prof.enter(frame_name)
        try:
            return self._execute_function_inner(func, args, closure_scope, gen_mode)
        except Exception as e:
            # 异常首次穿过本帧时,把完整调用链快照挂到异常上 —
            # 传到顶层时 finally 已弹栈,只有此刻看得见全链
            if not getattr(e, '_intent_stack', None):
                try:
                    e._intent_stack = list(self.call_stack)
                except Exception:
                    pass
            # EX2: 帧快照链 — 本帧局部变量在此刻仍可见(作用域还没弹)
            # 最深层先补, 外层穿帧时前插 → 最终从外到内排列
            try:
                snap = {'name': frame.name, 'line': frame.line,
                        'column': frame.column, 'filename': frame.filename,
                        'locals': {k: _brief_value(v) for k, v
                                   in _frame_symbols(frame).items()}}
                chain = getattr(e, '_intent_frames', None)
                if chain is None:
                    chain = []
                    e._intent_frames = chain
                chain.insert(0, snap)
            except Exception:
                pass
            raise
        finally:
            if self.profiler is not None:
                self.profiler.exit(frame_name)
            self.call_stack.pop()

    def _execute_function_inner(self, func, args: List[RuntimeValue],
                          closure_scope: Optional[Scope] = None,
                          gen_mode: bool = False) -> RuntimeValue:
        """执行函数 - 支持闭包和泛型类型推断

        如果 func 是 FunctionValue,自动提取其闭包作用域。
        闭包作用域作为新作用域的 parent,而非当前的 current_scope。
        泛型参数从实参类型推断,代入形参注解和返回类型注解。

        S3: 生成器函数调用(gen_mode=False 且 is_generator)— 惰性创建
        控制器立刻返回 GeneratorValue, 函数体一行不跑(首个 pull 才启动,
        与 Python 一致: 调用即惰性)。gen_mode=True 时由协程线程驱动,
        跳过建控制器, 直接跑体。
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

        # ── S3: 生成器函数 — 调用即惰性, 建控制器交 GeneratorValue ──
        if getattr(func_def, 'is_generator', False) and not gen_mode:
            return GeneratorValue(
                GeneratorController(self, func, args, closure_scope))

        # ── A3a: async 函数 — 调用即惰性, 建协程交 AsyncValue ──
        # 体在协程线程里以 gen_mode 执行(await 经 _active_gen 挂起);
        # async 生成器(yield + await 混用)留后续切片, 显式拒绝不静默。
        if getattr(func_def, 'is_async', False) and not gen_mode:
            if getattr(func_def, 'is_generator', False):
                raise RuntimeError(
                    f"async 函数暂不支持 yield(async 生成器留后续): {func_name}")
            return AsyncValue(
                GeneratorController(self, func, args, closure_scope))

        # ── 泛型类型推断 ──
        type_bindings: Dict[str, str] = {}
        type_params = getattr(func_def, 'type_params', [])
        if type_params:
            # 对每个参数：统一声明的类型标注与实际类型，解出类型参数的绑定
            for param_tuple, arg_value in zip(func_def.params, args):
                param_name, decl_type = param_tuple[0], param_tuple[1]
                if decl_type:
                    self._unify_types(decl_type, arg_value.get_type(), type_bindings)
            # 未绑定类型参数的 fallback
            for tp in type_params:
                if tp not in type_bindings:
                    type_bindings[tp] = "Any"
            # 泛型约束检查(P1.3b): 约束违反走契约错误通道 —
            # 「类型参数的要求」与 requires 同性质: 不满足即拒之门外
            constraints = getattr(func_def, 'type_param_constraints', {})
            for tp, constraint in constraints.items():
                bound_type = type_bindings.get(tp, "Any")
                if not self._check_constraint(bound_type, constraint):
                    raise ContractViolation(
                        f"泛型约束违约: 类型参数 {tp} 要求 {constraint},但得到 {bound_type}",
                        clause=f"constraint {constraint}",
                        expected=constraint, actual=bound_type,
                        line=self.current_line, column=self.current_col,
                        stack=list(self.call_stack), filename=self.current_filename)
            # 代入形参标注和返回类型
            subst_params = [(name, self._subst_type(pt, type_bindings), default)
                            for name, pt, default in func_def.params]
            subst_return = self._subst_type(func_def.return_type, type_bindings)
        else:
            subst_params = func_def.params
            subst_return = func_def.return_type

        # 保存旧的变量状态,用闭包作用域作为父作用域
        old_scope = self.current_scope
        parent = closure_scope if closure_scope is not None else old_scope
        self.current_scope = Scope(parent=parent)
        # EX2: 本帧作用域挂到调用栈帧 — 异常穿帧时(外层 except 看到的
        # 已是最内层 scope), 帧快照必须从帧上取, 才能各帧各的本地人
        if self.call_stack:
            self.call_stack[-1].scope = self.current_scope

        # 设置参数(在验证契约之前,使参数名可用于 requires/ensures)
        # 同时进行运行时类型校验(使用泛型代入后的类型)
        num_params = len(subst_params)
        num_args = len(args)
        for i, (param_name, param_type, *rest) in enumerate(subst_params):
            default_expr = rest[0] if rest else None
            if i < num_args:
                # 有实参：类型校验后声明
                arg_value = args[i]
                if param_type and param_type != "Any":
                    self._check_type(arg_value, param_type, f"@ 参数 '{param_name}' (函数 {func_name})")
                self.current_scope.declare(param_name, arg_value.copy(), False)
            elif default_expr is not None:
                # 无实参但有默认值：求值默认值表达式
                default_val = self.evaluate_expression(default_expr)
                self.current_scope.declare(param_name, default_val.copy(), False)
            else:
                # 既无实参也无默认值：报错
                raise TypeError(f"@ 参数 '{param_name}' 缺少实参(函数 {func_name})")

        # 准备验证上下文(包含参数绑定)
        context = {
            'args': args,
            'variables': {name: val for name, val in self.current_scope.symbols.items()},
            'params': {p[0]: v.copy() for p, v in zip(func_def.params, args) if isinstance(p, tuple)}
        }

        # 验证前置条件
        func_requires = getattr(func_def, 'requires', [])
        if func_requires:
            if not self.contract_verifier.verify_requires(func_requires, context):
                self.current_scope = old_scope
                errs = self.contract_verifier.get_errors()
                first = errs[0] if errs else "前置条件未满足"
                raise ContractViolation(
                    f"契约违约(requires): {first} — 函数 {func_name} 拒绝执行",
                    clause="requires",
                    expected=first,
                    line=self.current_line, column=self.current_col,
                    stack=list(self.call_stack), filename=self.current_filename)

        # 执行函数体
        is_gen = getattr(func_def, 'is_generator', False)
        is_async_fn = getattr(func_def, 'is_async', False)
        result = IntValue(0)
        explicit_return = False

        if is_gen:
            # S3: gen_mode — 体由协程线程顺序驱动, yield 在执行内握手挂起;
            # 执行流即生成器的生命周期(首个 pull 启动, return/耗尽收摊)。
            # 注: 生成器函数不验 ensures — 无返回值可验(Python 同语义),
            # requires 已在首个 pull 前的本线程 setup 里验过。
            for stmt in func_def.body:
                result = self.execute_statement(stmt)
                if self.return_flag:
                    self.return_flag = False
                    explicit_return = True
                    break
        else:
            for stmt in func_def.body:
                result = self.execute_statement(stmt)
                if self.return_flag:
                    self.return_flag = False
                    explicit_return = True
                    break

        # A3a: async 函数的返回值对齐 Python — 无显式 return 即 None
        # (普通函数保持既有隐式返回约定, 不改; 协程结果会被 run 当返回值用)
        if is_async_fn and not explicit_return:
            result = NoneValue()

        # 验证后置条件
        func_ensures = getattr(func_def, 'ensures', [])
        if func_ensures and not (is_gen and gen_mode):
            # 将 result 放入全局作用域,使 ensures 表达式的 result 可解析
            self.global_scope.symbols['result'] = result
            if not self.contract_verifier.verify_ensures(func_ensures, result, context):
                errs = self.contract_verifier.get_errors()
                first = errs[0] if errs else "后置条件未满足"
                del self.global_scope.symbols['result']
                self._exit_scope(old_scope)
                raise ContractViolation(
                    f"契约违约(ensures): {first} — 函数 {func_name} 未兑现承诺",
                    clause="ensures",
                    expected=first,
                    line=self.current_line, column=self.current_col,
                    stack=list(self.call_stack), filename=self.current_filename)
            del self.global_scope.symbols['result']

        # 恢复作用域（执行 defer）
        self._exit_scope(old_scope)

        # 校验返回类型(使用泛型代入后的返回类型)
        if subst_return and subst_return != "Any":
            self._check_type(result, subst_return, f"@ 返回值 (函数 {func_name})")

        return result

    def execute_enum_def(self, stmt: 'EnumDef') -> RuntimeValue:
        """执行枚举定义 — 将每个变体注册为全局常量"""
        enum_type = EnumType(stmt.name, stmt.variants)
        # 注册到枚举注册表（用于穷举检查）
        self.enum_registry[stmt.name] = stmt.variants
        for variant in stmt.variants:
            enum_value = EnumValue(stmt.name, variant)
            self.current_scope.declare(variant, enum_value, True)  # 常量，不可修改
        # 返回类型对象本身（可选，可忽略）
        return EnumValue(stmt.name, "__type__")

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
            # E3: 方法 def 行即执行 — 与顶层函数同口径打点
            if self.coverage is not None and getattr(method_def, 'line', 0):
                self.coverage.mark_stmt(self.current_filename, method_def.line)
        
        # 创建 ClassValue
        class_value = ClassValue(stmt.name, methods, superclass)
        
        # 注册到当前作用域
        self.current_scope.declare(stmt.name, class_value, False)
        
        return class_value
    
    def _execute_method(self, method: FunctionValue, instance: 'InstanceValue', args: List[RuntimeValue],
                        gen_mode: bool = False):
        """在实例上下文中执行方法(带调用栈跟踪) — 委托 _execute_method_inner

        gen_mode=True: 生成器方法的协程线程驱动 — 不建控制器, 直接跑体。
        """
        fd = method.func_def
        klass = getattr(instance, 'klass', None)
        class_name = getattr(klass, 'name', '') or ''
        frame_name = f"{class_name}.{getattr(fd, 'name', '<method>')}" if class_name \
            else getattr(fd, 'name', '<method>')
        frame = CallFrame(frame_name, self.current_line, self.current_col,
                          self.current_filename)
        self.call_stack.append(frame)
        prof = self.profiler
        if prof is not None:
            prof.enter(frame_name)
        try:
            return self._execute_method_inner(method, instance, args, gen_mode)
        except Exception as e:
            if not getattr(e, '_intent_stack', None):
                try:
                    e._intent_stack = list(self.call_stack)
                except Exception:
                    pass
            # EX2: 方法帧同样补局部变量快照(与 execute_function 同构)
            try:
                snap = {'name': frame.name, 'line': frame.line,
                        'column': frame.column, 'filename': frame.filename,
                        'locals': {k: _brief_value(v) for k, v
                                   in _frame_symbols(frame).items()}}
                chain = getattr(e, '_intent_frames', None)
                if chain is None:
                    chain = []
                    e._intent_frames = chain
                chain.insert(0, snap)
            except Exception:
                pass
            raise
        finally:
            if self.profiler is not None:
                self.profiler.exit(frame_name)
            self.call_stack.pop()

    def _execute_method_inner(self, method: FunctionValue, instance: 'InstanceValue',
                              args: List[RuntimeValue], gen_mode: bool = False):
        """在实例上下文中执行方法

        S3: 生成器方法(gen_mode=False 且 is_generator)— 调用即惰性,
        建控制器交 GeneratorValue(this 由协程线程重建后注入)。
        """
        func_def = method.func_def
        closure = method.closure

        # ── S3: 生成器方法 — 惰性创建控制器 ──
        if getattr(func_def, 'is_generator', False) and not gen_mode:
            return GeneratorValue(
                GeneratorController(self, method, args, closure,
                                    instance=instance))

        # ── A3a: async 方法 — 惰性创建协程 ──
        if getattr(func_def, 'is_async', False) and not gen_mode:
            return AsyncValue(
                GeneratorController(self, method, args, closure,
                                    instance=instance))

        # 创建方法作用域
        method_scope = Scope(parent=closure)
        
        # 绑定参数 (跳过 this 参数, 它由执行器注入)
        non_this_params = [(i, p) for i, p in enumerate(func_def.params) if (p[0] if isinstance(p, tuple) else p) != 'this']
        for arg_idx, (param_i, param) in enumerate(non_this_params):
            param_name = param[0] if isinstance(param, tuple) else param
            default_expr = param[2] if (isinstance(param, tuple) and len(param) > 2) else None
            if arg_idx < len(args):
                method_scope.declare(param_name, args[arg_idx], False)
            elif default_expr is not None:
                default_val = self.evaluate_expression(default_expr)
                method_scope.declare(param_name, default_val, False)
            else:
                method_scope.declare(param_name, self.get_default_value(None), False)
        
        # 注入 this
        method_scope.declare('this', instance, True)
        
        # 保存并切换作用域 + return 状态
        old_scope = self.current_scope
        old_return_flag = self.return_flag
        old_return_value = self.return_value
        self.current_scope = method_scope
        # EX2: 方法帧作用域挂帧(与 _execute_function_inner 同构)
        if self.call_stack:
            self.call_stack[-1].scope = self.current_scope
        
        # 执行函数体
        self.return_flag = False
        result = IntValue(0)
        try:
            for stmt in func_def.body:
                result = self.execute_statement(stmt)
                if self.return_flag:
                    break
        finally:
            self._exit_scope(old_scope)
            self.return_flag = old_return_flag
            self.return_value = old_return_value
        
        return result

    def _get_member_access_instance(self, member_access):
        """从 MemberAccess 链中获取方法接收者实例
        如 this.start.distance_to(...) → this.start = Point3D InstanceValue
           line.midpoint() → line = Line3D InstanceValue
        关键：取倒数第二层对象（方法前的那个），而非链的根部
        """
        if isinstance(member_access, MemberAccess):
            return self.evaluate_expression(member_access.obj)
        return None

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
                # 字段未找到，尝试查找方法（如 this.to(other)）
                method = obj_value.klass.find_method(expr.member)
                if method is not None:
                    return method
                raise NameError(f"实例没有属性 '{expr.member}'")

            # S3: 生成器方法 g.send(v) / g.throw(e) / g.close()
            if isinstance(obj_value, GeneratorValue):
                if expr.member in ('send', 'throw', 'close'):
                    return _GenMethod(obj_value, expr.member)
                raise NameError(
                    f"生成器没有成员 '{expr.member}'(可用: send/throw/close)")

            # ErrorValue 成员访问(P1.4): e.type / e.message / e.stack / e.__cause__
            if isinstance(obj_value, ErrorValue):
                if expr.member == 'type':
                    return StringValue(obj_value.err_type)
                if expr.member == 'message':
                    return StringValue(obj_value.message)
                if expr.member == 'stack':
                    return ListValue(list(obj_value.stack), StringType())
                if expr.member in ('__cause__', 'cause'):
                    if obj_value.cause is not None:
                        return obj_value.cause
                    return NoneValue()
                raise NameError(f"异常值没有成员 '{expr.member}'")

            # ResultValue 成员访问 — Ok/Err 是平等的两种值,Result 有自己的结构
            if isinstance(obj_value, ResultValue):
                if expr.member == 'is_ok':
                    return BoolValue(obj_value.is_ok)
                if expr.member == 'ok_value':
                    if obj_value.ok_value is not None:
                        return obj_value.ok_value
                    raise NameError("对 Err 访问 ok_value")
                if expr.member == 'err_value':
                    if obj_value.err_value is not None:
                        return obj_value.err_value
                    raise NameError("对 Ok 访问 err_value")
                raise NameError(f"Result 没有成员 '{expr.member}'")

            # DictValue 成员(P3.1): 字典没有属性成员, 方法走 CallExpr 路由 —
            # 提前拒绝, 防止落入模块 fallback 把 dict 当模块名
            if isinstance(obj_value, DictValue):
                raise NameError(f"字典没有成员 '{expr.member}'(方法调用: d.has_key(k)/d.keys()/d.values())")

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

            # 尝试在模块中查找(仅当值是字符串 — 防止 dict/list 等被误当模块名)
            if hasattr(obj_value, 'value') and isinstance(obj_value.value, str):
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
                val = obj.get(self._dict_key(index))
                if val is None:
                    raise KeyError(f"字典中没有键 '{index.value}'")
                return val
            elif isinstance(obj, StringValue):
                idx = index.value
                if idx < 0:
                    idx = len(obj.value) + idx
                if idx < 0 or idx >= len(obj.value):
                    raise IndexError(f"字符串索引 {idx} 越界")
                return StringValue(obj.value[idx])
            else:
                # 运算符重载: __getitem__(index)
                if isinstance(obj, InstanceValue):
                    method = obj.get('__getitem__')
                    if method and isinstance(method, FunctionValue):
                        return self._execute_method(method, obj, [index])
                raise TypeError(f"不支持对 {obj.get_type()} 类型使用下标访问 []")

        elif isinstance(expr, PipeExpr):
            # 管道: left |> right → right(left)
            left_val = self.evaluate_expression(expr.left, context)

            # 右侧如果是函数名,先查作用域变量(lambda),再查 builtins 和全局函数
            if isinstance(expr.right, Variable):
                fname = expr.right.name
                # 先查作用域: 可能是变量绑定的 lambda
                try:
                    scope_val = self.current_scope.get(fname)
                    if isinstance(scope_val, FunctionValue):
                        return self.execute_function(scope_val, [left_val])
                except (NameError, KeyError):
                    pass
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

        elif isinstance(expr, SendExpr):
            # CC2: ch <- v — 发送(阻塞直到入队; 关闭通道上报错)
            chan_val = self.evaluate_expression(expr.chan, context)
            if not isinstance(chan_val, ChannelValue):
                raise TypeError(f"<- 左侧必须是通道(chan() 创建), 得到 {chan_val.type}")
            value = self.evaluate_expression(expr.value, context)
            chan_val.send(value)
            return NoneValue()

        elif isinstance(expr, RecvExpr):
            # CC2: <- ch — 接收(空则阻塞; 关闭且空则 ChannelClosedError)
            chan_val = self.evaluate_expression(expr.chan, context)
            if not isinstance(chan_val, ChannelValue):
                raise TypeError(f"<- 右侧必须是通道(chan() 创建), 得到 {chan_val.type}")
            return chan_val.recv()

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

        elif isinstance(expr, SliceExpr):
            obj = self.evaluate_expression(expr.obj, context)
            start = None
            end = None
            step = None
            if expr.start:
                start = self.evaluate_expression(expr.start, context).value
            if expr.end:
                end = self.evaluate_expression(expr.end, context).value
            if expr.step:
                step = self.evaluate_expression(expr.step, context).value
            if isinstance(obj, ListValue):
                lst = obj.value
                # 处理步长切片
                step_val = step if step is not None else 1
                if step_val != 1:
                    # 自己实现步长切片
                    start_val = start if start is not None else (0 if step_val > 0 else len(lst)-1)
                    end_val = end if end is not None else (len(lst) if step_val > 0 else -1)
                    indices = range(start_val, end_val, step_val)
                    sliced = [lst[i] for i in indices if 0 <= i < len(lst)]
                else:
                    sliced = lst[slice(start, end)]
                return ListValue(sliced, obj.type.element_type)
            elif isinstance(obj, StringValue):
                s = obj.value[start:end:step] if step is not None else obj.value[start:end]
                return StringValue(s)
            else:
                raise TypeError(f"不支持对 {obj.get_type()} 类型使用切片")

        elif isinstance(expr, TernaryExpr):
            cond = self.evaluate_expression(expr.condition, context)
            if cond.value:
                return self.evaluate_expression(expr.then_expr, context)
            else:
                return self.evaluate_expression(expr.else_expr, context)

        elif isinstance(expr, WalrusExpr):
            # S2a: 海象 := — 求值→绑定(存在则赋值, 否则声明)→原值返回
            val = self.evaluate_expression(expr.value, context)
            if self.current_scope.has(expr.name):
                self.current_scope.assign(expr.name, val)
            else:
                self.current_scope.declare(expr.name, val, False)
            return val

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
            # 逻辑运算短路求值(Python 语义): and 左假即假 / or 左真即真,
            # 右侧不需求值。修根因: 原实现两侧 eager 求值后交 _binary_op,
            # 边界条件如 `i < len(lst) and lst[i] < x` 在 i==len(lst) 时
            # 右侧仍被求值 → IndexError(空列表/heapq/bisect 全族中招)。
            # 返回类型保持 BoolValue 不变(与原 _binary_op 语义兼容)。
            if expr.op == 'and':
                left = self.evaluate_expression(expr.left, context)
                if not left.to_bool():
                    return BoolValue(False)
                return BoolValue(self.evaluate_expression(expr.right, context).to_bool())
            if expr.op == 'or':
                left = self.evaluate_expression(expr.left, context)
                if left.to_bool():
                    return BoolValue(True)
                return BoolValue(self.evaluate_expression(expr.right, context).to_bool())
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
                    # X3: __call__ — 实例可调用: obj(args) → obj.__call__(args)
                    if isinstance(var_val, InstanceValue):
                        call_method = var_val.get('__call__')
                        if call_method is not None and isinstance(call_method, FunctionValue):
                            return self._execute_method(call_method, var_val, args)
                    # FunctionValue → 调用 lambda 或闭包
                    if isinstance(var_val, FunctionValue):
                        return self.execute_function(var_val, args)

            # 2️⃣ 处理MemberAccess作为函数的情况 (如 std.math.add(x, y) 或 p.method())
            if isinstance(expr.func, MemberAccess):
                # ResultValue 方法调用: r.unwrap() — Err 上 unwrap 即违约,抛错
                recv = self.evaluate_expression(expr.func.obj, context)
                if isinstance(recv, ResultValue) and expr.func.member == 'unwrap':
                    return recv.unwrap()
                # DictValue 方法调用(P3.1): d.has_key(k) / d.keys() / d.values()
                if isinstance(recv, DictValue):
                    m = expr.func.member
                    args = [self.evaluate_expression(arg, context) for arg in expr.args]
                    if m == 'has_key' and len(args) == 1:
                        return BoolValue(recv.has_key(self._dict_key(args[0])))
                    if m == 'keys' and not args:
                        return self._builtin_keys([recv])
                    if m == 'values' and not args:
                        return self._builtin_values([recv])
                    raise NameError(f"字典没有方法 '{m}'(可用: has_key/keys/values)")
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
                # X3: __call__ — 实例可调用: holder(args) → holder.__call__(args)
                if isinstance(func_val, InstanceValue):
                    call_method = func_val.get('__call__')
                    if call_method is not None and isinstance(call_method, FunctionValue):
                        return self._execute_method(call_method, func_val, args)
                # ClassValue → 类构造函数 (如 std.bim.geometry.Vector3D())
                if isinstance(func_val, ClassValue):
                    return func_val.call(self, args)
                # I1/I2a 可调用桥值(FFI 外部函数/Python 桥函数/mock 同路)
                if callable(func_val):
                    return func_val(args)

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

            # 回退：从当前作用域查找（模块导入注入的符号）
            if func_name and self.current_scope.has(func_name):
                scope_val = self.current_scope.get(func_name)
                if isinstance(scope_val, FunctionValue):
                    args = [self.evaluate_expression(arg, context) for arg in expr.args]
                    return self.execute_function(scope_val, args)
                if isinstance(scope_val, ClassValue):
                    args = [self.evaluate_expression(arg, context) for arg in expr.args]
                    instance = scope_val.call(self, args)
                    return instance
                # TQ1: mock 等可调用值(测试替身直接调用 m(args))
                if callable(scope_val):
                    args = [self.evaluate_expression(arg, context) for arg in expr.args]
                    return scope_val(args)

            raise NameError(f"未定义的函数: {func_name or expr.func}")

        elif isinstance(expr, ListCompExpr):
            # 列表推导式 [expr for x in items if cond]
            iterable = self.evaluate_expression(expr.iterable, context)
            if not isinstance(iterable, ListValue):
                raise TypeError(f"推导式期望列表,得到 {iterable.type}")
            
            result_elements = []
            for item in iterable.value:
                old_scope = self.current_scope
                self.current_scope = self.current_scope.enter()
                self.current_scope.declare(expr.var_name, item.copy(), False)
                
                # 检查 if 条件
                if expr.condition is not None:
                    cond_val = self.evaluate_expression(expr.condition, context)
                    if isinstance(cond_val, BoolValue) and not cond_val.value:
                        self.current_scope = old_scope
                        continue
                
                # 求值元素表达式
                elem_val = self.evaluate_expression(expr.element, context)
                result_elements.append(elem_val)
                self.current_scope = old_scope
            
            # 确定元素类型
            if result_elements:
                element_type = result_elements[0].type
                for elem in result_elements[1:]:
                    if not element_type.can_assign_from(elem.type) and not elem.type.can_assign_from(element_type):
                        element_type = AnyType()
                        break
            else:
                element_type = IntType()
            
            return ListValue(result_elements, element_type)

        elif isinstance(expr, DictCompExpr):
            # 字典推导式 {k: v for x in items if cond}
            iterable = self.evaluate_expression(expr.iterable, context)
            if not isinstance(iterable, ListValue):
                raise TypeError(f"推导式期望列表,得到 {iterable.type}")
            
            entries = {}
            for item in iterable.value:
                old_scope = self.current_scope
                self.current_scope = self.current_scope.enter()
                self.current_scope.declare(expr.var_name, item.copy(), False)
                
                if expr.condition is not None:
                    cond_val = self.evaluate_expression(expr.condition, context)
                    if isinstance(cond_val, BoolValue) and not cond_val.value:
                        self.current_scope = old_scope
                        continue
                
                key_val = self.evaluate_expression(expr.key_expr, context)
                value_val = self.evaluate_expression(expr.value_expr, context)
                entries[self._dict_key(key_val)] = value_val
                self.current_scope = old_scope
            
            return DictValue(entries, StringType(), AnyType())

        elif isinstance(expr, ListExpr):
            elements = [self.evaluate_expression(elem, context) for elem in expr.elements]
            if not elements:
                return ListValue([], IntType())

            # 确定元素类型（允许混合类型，回退到 Any）
            element_type = elements[0].type
            for elem in elements[1:]:
                if not element_type.can_assign_from(elem.type) and not elem.type.can_assign_from(element_type):
                    element_type = AnyType()
                    break

            return ListValue(elements, element_type)

        elif isinstance(expr, DictExpr):
            entries = {}
            for key_expr, value_expr in expr.entries:
                key_val = self.evaluate_expression(key_expr, context)
                val_val = self.evaluate_expression(value_expr, context)
                # 用字符串/数值作为键(实例键走 __hash__ 归一)
                key = self._dict_key(key_val)
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

        elif isinstance(expr, YieldExpr):
            # S3: yield 表达式 — 产出值并返回 send 进来的值
            return self.execute_yield(expr)

        elif isinstance(expr, AwaitExpr):
            # A3a: await — 求值出内层协程, 经协程线程交出(挂起),
            # 驱动线程驱完内层后把结果 send 回来, 即本表达式的值。
            inner = self.evaluate_expression(expr.operand)
            if not isinstance(inner, AsyncValue):
                raise TypeError(
                    f"await 期望协程(async 函数调用的结果), 得到 {inner.get_type()}")
            ctrl = getattr(self, '_active_gen', None)
            if ctrl is None:
                raise RuntimeError("await 只能在 async 函数中使用")
            return ctrl.do_yield(inner)

        else:
            raise RuntimeError(f"不支持的表达式类型: {type(expr).__name__}")

    def _dict_key(self, key: RuntimeValue):
        """X3: dict 键归一 — 实例作键时走 __hash__()

        约定: 实例定义 __hash__() 返回 Int/String, 以该值为 dict 键;
        未定义则回落 DictValue._norm_key 的标量归一(实例取 value 字段)。
        """
        if isinstance(key, InstanceValue):
            method = key.get('__hash__')
            if method is not None and isinstance(method, FunctionValue):
                hv = self._execute_method(method, key, [])
                if isinstance(hv, (IntValue, StringValue)):
                    return hv.value
                raise TypeError(f"__hash__() 必须返回 Int 或 String,得到 {hv.get_type()}")
        return DictValue._norm_key(key)

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
        elif op == 'in':
            # x in list / key in dict / sub in string / obj.__contains__(x)
            if isinstance(right, ListValue):
                for elem in right.value:
                    eq_result = self._binary_op(left, '==', elem)
                    if eq_result.value:
                        return BoolValue(True)
                return BoolValue(False)
            elif isinstance(right, DictValue):
                return BoolValue(right.has_key(self._dict_key(left)))
            elif isinstance(right, StringValue):
                # 子串归属 — 一物是否在他物之中(格物的基本操作)
                if not isinstance(left, StringValue):
                    raise TypeError(f"'in' 对字符串期望 String 左侧,得到 {left.type}")
                return BoolValue(left.value in right.value)
            elif isinstance(right, InstanceValue):
                # X3: __contains__ — 归属判断交给对象自己
                method = right.get('__contains__')
                if method is not None and isinstance(method, FunctionValue):
                    return self._execute_method(method, right, [left])
            raise TypeError(f"'in' 操作符右侧期望列表、字典、字符串或有__contains__的对象,得到 {right.type}")

        elif op == 'not in':
            # x not in list / key not in dict
            result = self._binary_op(left, 'in', right)
            return BoolValue(not result.value)

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

            # Bool 比较
            if isinstance(left, BoolValue) and isinstance(right, BoolValue):
                if op == '==':
                    return BoolValue(left.value == right.value)
                elif op == '!=':
                    return BoolValue(left.value != right.value)

            # Enum 比较
            if isinstance(left, EnumValue) and isinstance(right, EnumValue):
                if op == '==':
                    return BoolValue(left == right)
                elif op == '!=':
                    return BoolValue(left != right)

            # List 比较
            if isinstance(left, ListValue) and isinstance(right, ListValue):
                if op == '==':
                    if len(left.value) != len(right.value):
                        return BoolValue(False)
                    for lv, rv in zip(left.value, right.value):
                        eq_result = self._binary_op(lv, '==', rv)
                        if not eq_result.value:
                            return BoolValue(False)
                    return BoolValue(True)
                elif op == '!=':
                    eq_result = self._binary_op(left, '==', right)
                    return BoolValue(not eq_result.value)

            # Dict 比较
            if isinstance(left, DictValue) and isinstance(right, DictValue):
                if op == '==':
                    if len(left.value) != len(right.value):
                        return BoolValue(False)
                    for k, lv in left.value.items():
                        # 键集合一致 + 值逐项递归比较(与 List 比较同策略,
                        # 避免 RuntimeValue dataclass 空字段 eq 的身份比较陷阱)
                        if k not in right.value:
                            return BoolValue(False)
                        eq_result = self._binary_op(lv, '==', right.value[k])
                        if not eq_result.value:
                            return BoolValue(False)
                    return BoolValue(True)
                elif op == '!=':
                    eq_result = self._binary_op(left, '==', right)
                    return BoolValue(not eq_result.value)

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

        # ── 运算符重载 (obj.__add__(other) 等) ──
        op_to_method = {
            '+': '__add__', '-': '__sub__', '*': '__mul__', '/': '__div__',
            '%': '__mod__', '**': '__pow__', '//': '__floordiv__',
            '==': '__eq__', '!=': '__ne__', '<': '__lt__',
            '>': '__gt__', '<=': '__le__', '>=': '__ge__',
        }
        if op in op_to_method and isinstance(left, InstanceValue):
            method_name = op_to_method[op]
            method = left.get(method_name)
            # != 未定义 __ne__ 时回退 __eq__ 取反(与 Python 的默认推导一致)
            if method is None and op == '!=':
                method_name, method = '__eq__', left.get('__eq__')
                if method is not None and isinstance(method, FunctionValue):
                    eq_result = self._execute_method(method, left, [right])
                    if isinstance(eq_result, BoolValue):
                        return BoolValue(not eq_result.value)
                    raise TypeError(f"__eq__() 必须返回 Bool,得到 {eq_result.get_type()}")
            if method and isinstance(method, FunctionValue):
                return self._execute_method(method, left, [right])
            # 反射方法: 如果右操作数是实例且有 __radd__ 等
            rmethod_name = '__r' + method_name[2:]
            if isinstance(right, InstanceValue):
                rmethod = right.get(rmethod_name)
                if rmethod and isinstance(rmethod, FunctionValue):
                    return self._execute_method(rmethod, right, [left])

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

# ==================== 嵌入 API（BD1: Dynamo/pyRevit 宿主调用） ====================

def run_source(code: str, filename: str = "<embedded>"):
    """在宿主进程内运行 Intent 源码, 返回最后一条表达式的原生 Python 值。

    BD1 Dynamo 落地入口: Dynamo 的 PythonNet3 节点(CPython 3.11)里
    `import mini_intent; mini_intent.run_source(intent_code)` 即可跑 Intent —
    解释器是纯 Python, 零 C 依赖, 无需重写。

    返回: 最后一条顶层语句的值(RuntimeValue → Python 原生: int/float/str/
    bool/None/list/dict); 无顶层语句或最后是语句则返回 None。
    异常: 语法错误/契约违约/运行时错误原样抛出(宿主可捕获)。
    """
    lexer = Lexer(code, filename)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    program = parser.parse()
    if parser.errors:
        raise SyntaxError(f"Intent 语法错误: {parser.errors[0]}")

    interp = Interpreter()
    interp.cli_args = []
    # 顶层函数注册(与 execute_program 的函数提升一致, 否则调用即 NameError)
    for func in program.functions.values():
        interp.functions[func.name] = func
    result = None
    for stmt in program.statements:
        if isinstance(stmt, Expression):
            rv = interp.evaluate_expression(stmt)
            result = rv.value if isinstance(rv, RuntimeValue) else rv
        else:
            interp.execute_statement(stmt)
    # 顶层无语句但有 main 函数时, 自动调用(与 CLI 行为一致)
    if result is None and 'main' in program.functions:
        rv = interp.execute_function(program.functions['main'], [])
        result = rv.value if isinstance(rv, RuntimeValue) else rv
    return result


# ==================== 主程序 ====================
def main():
    """主函数"""
    import argparse
    # Windows 编码修复
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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
    parser.add_argument('-c', '--code', default=None,
                        help='直接执行代码串(对齐 python -c)')
    parser.add_argument('--version', action='store_true', help='显示版本号')
    parser.add_argument('--check', action='store_true',
                        help='只解析不执行: 语法干净退出0, 有错误退出2(CI/lint 前置)')
    parser.add_argument('--types', action='store_true',
                        help='L1: 渐进类型静态检查(mypy-lite: 标注处检查+推断处放过)')
    parser.add_argument('--emit', nargs=2, metavar=('KIND', 'FILE'),
                        help='将词法/语法结果写入文件: --emit tokens out.txt | --emit ast out.txt')
    parser.add_argument('--install', nargs='?', const='__BATCH__', default=None,
                        metavar='URL',
                        help='安装依赖: 带 URL 装单个; 不带按 intent.toml 的 [deps] 批量装')
    parser.add_argument('--dry-run', action='store_true',
                        help='PK1: 安装预演 — 只做依赖解析(约束合并/冲突检测)不安装')
    parser.add_argument('--fmt', default=None, metavar='FILE',
                        help='格式化 Intent 文件, 结果输出到 stdout')
    parser.add_argument('--lint', default=None, metavar='FILE',
                        help='静态检查: let 重赋值/空 catch/无契约导出/未用 import')
    parser.add_argument('--compile', default=None, metavar='FILE',
                        help='M10: 编译 Intent 文件为字节码(可加 --run-vm 直接执行)')
    parser.add_argument('--run-vm', action='store_true',
                        help='M10: 编译后用栈式 VM 执行(与 --compile 搭配)')
    parser.add_argument('--doc', default=None, metavar='FILE',
                        help='从源码生成 markdown 模块文档(签名/契约/注释)')
    parser.add_argument('--test', nargs='?', const='tests', default=None,
                        help='运行测试: 不带参数默认 tests/ 目录, 也可指定文件或目录')
    parser.add_argument('-p', '--philosophy', action='store_true', help='显示哲学视角')
    parser.add_argument('-m', '--mapping', default='philosophy/mapping.json', help='哲学映射文件路径')
    parser.add_argument('-d', '--demo', action='store_true', help='运行演示程序')
    parser.add_argument('-r', '--repl', action='store_true', help='启动REPL交互环境')
    parser.add_argument('-t', '--tokens', action='store_true', help='显示词法分析结果')
    parser.add_argument('-a', '--ast', action='store_true', help='显示语法分析结果')
    parser.add_argument('--debug', action='store_true',
                        help='C7: 调试模式执行(断点/单步/变量检视/调用栈)')
    parser.add_argument('--postmortem', action='store_true',
                        help='EX2: 事后调试(异常帧快照存档 + 崩溃后进场检视)')
    parser.add_argument('--profile', action='store_true',
                        help='M4: 函数级剖析(cProfile 等价: 调用次数/累计/自身时间)')
    parser.add_argument('--mem-profile', action='store_true',
                        help='M4: 内存分配热点(基于 MM1 对象注册表的按类型分配计数)')
    parser.add_argument('--coverage', action='store_true',
                        help='E3: 语句覆盖率(执行打点 + AST 分母, Python coverage 语句语义)')
    parser.add_argument('--contracts', action='store_true',
                        help='Q2: 与 --coverage 同用 — 叠加契约覆盖率(requires/ensures 子句级)')

    # parse_known_args: 源文件之后的额外参数透传给 Intent 程序(args() 读取)
    args, extra = parser.parse_known_args()

    # 创建翻译器
    translator = PhilosophyTranslator(args.mapping)

    # 创建解释器
    interpreter = Interpreter()

    # --version: 只报版本
    if args.version:
        print(f"Intent v{VERSION} ({PHILOSOPHY_SLOGAN})")
        return

    # --install: 依赖安装(PK1: 版本解析 + lock)
    if args.install is not None:
        proj_dir = None
        # 批量模式的位置参数是项目目录(判定命令: --install --dry-run tests/pkg_fixture)
        if args.install == '__BATCH__' and args.filename \
                and os.path.isdir(args.filename):
            proj_dir = args.filename
        sys.exit(run_install(None if args.install == '__BATCH__' else args.install,
                             dry_run=args.dry_run, project_dir=proj_dir))

    # --fmt: 格式化(P2.2)
    if args.fmt:
        sys.exit(run_format(args.fmt))

    # --lint: 静态检查(P2.3)
    if args.lint:
        sys.exit(run_lint(args.lint))

    # --doc: 生成模块文档(P2.4)
    if args.doc:
        sys.exit(run_doc(args.doc))

    # --compile: 字节码编译(M10)
    if args.compile:
        try:
            with open(args.compile, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            print(f"❌ 找不到文件: {args.compile}")
            sys.exit(2)
        lexer = Lexer(code, args.compile)
        tokens = lexer.tokenize()
        parser = Parser(tokens, code)
        program = parser.parse()
        if parser.errors:
            print(f"❌ 语法错误, 无法编译: {parser.errors[0]}")
            sys.exit(2)
        from intent_bytecode import compile_program, VM
        try:
            emitter = compile_program(program, interpreter.builtins.keys())
        except NotImplementedError as e:
            print(f"❌ 编译失败(特性未覆盖, 属 M11 范围): {e}", file=sys.stderr)
            sys.exit(2)
        # 编译元信息走 stderr — stdout 只留程序输出, 与解释器 stdout 可直接对照
        print(f"⚙️  字节码编译完成: {args.compile} → {len(emitter.code)} 条指令, "
              f"{len(emitter.functions)} 个函数", file=sys.stderr)
        if args.run_vm:
            vm = VM(emitter, interpreter)
            vm.run()
        sys.exit(0)

    # P2.1: intent.toml 存在时, 项目 lib 与全局库加入搜索路径
    manifest = load_project_manifest()
    if manifest is not None:
        lib_dir = os.path.abspath('lib')
        if lib_dir not in interpreter.module_search_paths:
            interpreter.module_search_paths.append(lib_dir)
    # PK2: .venv/lib 优先于全局库 — 项目有自己的院子就不去公共池塘打水
    # (INTENT_HOME 可覆盖默认 ~/.intent, 与 tools/venv.py 同一约定)
    intent_home = os.environ.get('INTENT_HOME') or os.path.join(
        os.path.expanduser('~'), '.intent')
    venv_lib = os.path.abspath(os.path.join('.venv', 'lib'))
    if os.path.isdir(venv_lib) and venv_lib not in interpreter.module_search_paths:
        interpreter.module_search_paths.append(venv_lib)
    global_lib = os.path.join(intent_home, 'lib')
    if os.path.isdir(global_lib) and global_lib not in interpreter.module_search_paths:
        interpreter.module_search_paths.append(global_lib)

    # 代码来源: -c 优先, 其次 filename; 都没有则后续走 demo/help 分支
    code = None
    code_name = "<-c>"
    if args.code is not None:
        code = args.code
    elif args.filename and args.filename != '-':
        try:
            with open(args.filename, 'r', encoding='utf-8') as f:
                code = f.read()
            code_name = args.filename
            interpreter.current_filename = args.filename
            file_dir = os.path.dirname(os.path.abspath(args.filename))
            interpreter.add_module_search_path(file_dir)
            # P0.4: 源文件名之后的命令行参数交给 args() — 程序与世界的接口
            if extra:
                interpreter.cli_args = extra
        except FileNotFoundError:
            print(f"错误: 找不到文件 {args.filename}")
            sys.exit(2)

    # --check: 只解析不执行(治宽松模式假通过, CI 用)
    if args.check:
        check_code(code or "", code_name)
        return

    # --types: L1 渐进类型静态检查(标注处检查+推断处放过)
    if args.types:
        type_check_code(code or "", code_name)
        return

    # --emit: tokens/ast 写入文件
    if args.emit:
        emit_kind, emit_path = args.emit
        emit_analysis(code or "", emit_kind, emit_path, code_name)
        return

    # --debug: 调试模式执行(C7) — 断点/单步/变量检视/调用栈
    if args.debug:
        if code is None:
            print("❌ --debug 需要代码来源: --debug file.intent 或 --debug -c '...'")
            sys.exit(2)
        run_debug(code, code_name)
        return

    # --postmortem: 事后调试(EX2) — 异常帧快照存档, 崩溃后进场检视
    if args.postmortem:
        if code is None:
            print("❌ --postmortem 需要代码来源: --postmortem file.intent")
            sys.exit(2)
        run_postmortem(code, code_name)
        return

    # M4: 剖析模式 — --profile 函数级计时 + --mem-profile 分配热点
    if args.profile or args.mem_profile:
        if code is None:
            print("❌ --profile/--mem-profile 需要代码来源: --profile file.intent 或 -c '...'")
            sys.exit(2)
        if args.profile:
            interpreter.profiler = FunctionProfiler()
        wall0 = time.perf_counter()
        run_code(code, interpreter, args)
        wall = time.perf_counter() - wall0
        if args.profile:
            print()
            print(interpreter.profiler.report(wall))
        if args.mem_profile:
            print()
            print(render_mem_profile())
        return

    # E3/Q2: 覆盖率模式 — 语句打点 + (可选)契约子句打点
    if args.coverage:
        if code is None:
            print("❌ --coverage 需要代码来源: --coverage file.intent")
            sys.exit(2)
        sys.exit(run_coverage(code, code_name, with_contracts=args.contracts))

    # -c 直接执行(无需文件)
    if args.code is not None:
        run_code(code, interpreter, args)
        return

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

    # 循环
    let mut i = 1;
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

    # P0.2: 测试模式
    if args.test:
        run_tests(args.test)
        return

    # 无代码来源且无 demo: 打印帮助
    if code is None and not args.demo:
        parser.print_help()
        return

    # 显示哲学视角
    if args.philosophy and code:
        print("🧘 哲学视角代码:")
        print("=" * 60)
        print(translator.translate_code(code, "display"))
        print("=" * 60)
        print("\n⚙️  执行结果:")
        print("-" * 40)

    # 运行代码
    if code is not None:
        run_code(code, interpreter, args)

def _brief_value(v) -> str:
    """EX2: 帧快照的变量渲染 — 安全截断, 不因 repr 失败丢整份快照"""
    try:
        s = str(v)
    except Exception:
        s = f"<{type(v).__name__}>"
    return s if len(s) <= 60 else s[:57] + "..."

def _frame_symbols(frame) -> dict:
    """EX2: 取某帧自己的局部变量表

    异常路径上内层作用域不会恢复, 外层 except 看到的 current_scope
    已是最内层 — 所以每帧的作用域在建帧时就挂到 CallFrame.scope 上,
    快照从帧取, 各帧各的本地人, 张冠李戴即是假检视。
    """
    scope = getattr(frame, 'scope', None)
    return scope.symbols if scope is not None else {}

def wrap_intent_error(e: Exception, interpreter: 'Interpreter') -> IntentError:
    """把任意异常包装为带源码位置与调用栈的 IntentError

    解释器内部各处 raise 的是 Python 原生异常(TypeError/IndexError...),
    在顶层统一包装,补上出错位置与 Intent 调用链 — 不逐处修改 raise 点。
    """
    if isinstance(e, IntentError):
        if not e.stack:
            # 异常穿帧时已快照的栈,优先于顶层已弹空的 call_stack
            e.stack = getattr(e, '_intent_stack', None) or list(interpreter.call_stack)
        if e.line is None:
            e.line = interpreter.current_line
            e.column = interpreter.current_col
            e.filename = interpreter.current_filename
        return e
    # EX1: raise 抛出的错误值 → IntentError(携带 error_value 供链渲染)
    if isinstance(e, IntentRaise):
        ev = e.error_value
        ie = IntentError(
            f"{ev.err_type}: {ev.message}",
            line=getattr(e, '_intent_line', None) or interpreter.current_line or None,
            column=interpreter.current_col or None,
            stack=getattr(e, '_intent_stack', None) or list(interpreter.call_stack),
            filename=interpreter.current_filename)
        ie.py_type = ev.err_type
        ie.error_value = ev
        return ie
    is_syntax = isinstance(e, SyntaxError)
    ie = IntentError(
        str(e),
        line=getattr(e, 'lineno', None) or interpreter.current_line or None,
        column=getattr(e, 'offset', None) or interpreter.current_col or None,
        stack=getattr(e, '_intent_stack', None) or list(interpreter.call_stack),
        filename=interpreter.current_filename)
    ie.py_type = type(e).__name__
    ie.is_syntax = is_syntax
    return ie

def render_intent_error(e: IntentError, interpreter: 'Interpreter') -> str:
    """渲染 Intent 错误: 消息 + 源码行高亮 + 调用链(从外到内)"""
    out = []
    # 1. 错误头 — 契约违反是身份证错误,必须第一个被看见
    if isinstance(e, ContractViolation):
        head = "❌ 契约违反"
    elif getattr(e, 'is_syntax', False):
        head = "❌ 语法错误"
    else:
        head = "❌ 运行时错误"
    py_type = getattr(e, 'py_type', None)
    type_note = f" [{py_type}]" if py_type else ""
    out.append(f"{head}: {e.message}{type_note}")

    # 2. 源码位置 + 出错行片段 + 光标
    # 注: execute_statement 的旧包装层可能已在消息里附加过位置,检测到则不重复
    has_inline_pos = '   at line' in (e.message or '')
    if e.line and not has_inline_pos:
        fname = e.filename or "<stdin>"
        out.append(f"   at {fname}:{e.line}:{e.column or 1}")
        src_lines = interpreter.source_lines
        if src_lines and 0 < e.line <= len(src_lines):
            src = src_lines[e.line - 1].rstrip('\n')
            gutter = " " * (len(str(e.line)) + 3)
            out.append(f"   {e.line} | {src}")
            col = e.column or 1
            out.append(f"{gutter}{' ' * (col - 1)}^")

    # 3. Intent 调用链 — 从外到内,看清错误穿过哪些函数
    if e.stack:
        out.append("   调用链(从外到内):")
        for fr in e.stack:
            out.append(f"     {fr}")

    # 4. 契约违反的专属提示
    if isinstance(e, ContractViolation):
        out.append("   提示: 契约是函数与调用者之间的合同 — 检查实参是否满足")
        out.append("         requires,或函数实现是否兑现了 ensures 的承诺")

    # 5. 异常链(EX1): raise X from Y 的 __cause__ — 从起因到外层
    causes = []
    cur = getattr(getattr(e, 'error_value', None), 'cause', None)
    while cur is not None and isinstance(cur, ErrorValue):
        causes.append(cur)
        cur = getattr(cur, 'cause', None)
    if causes:
        out.append("   异常链(__cause__, 从起因到外层):")
        for c in reversed(causes):
            out.append(f"     {c.err_type}: {c.message}")
    return "\n".join(out)

def run_coverage(code: str, code_name: str, with_contracts: bool = False) -> int:
    """E3/Q2: 覆盖率运行 — 解析后先计 AST 分母, 再打点执行, 出报告

    程序异常也出报告(崩了更要看见覆盖到哪) — 渲染错误到 stderr,
    报告走 stdout, 退出码 1; 干净执行退出 0。
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, code)
    program = parser.parse()
    if parser.errors:
        print(f"❌ 语法错误, 无法覆盖率分析: {parser.errors[0]}")
        return 2
    tracker = CoverageTracker(with_contracts=with_contracts)
    tracker.count_program(program, code_name)
    interp = Interpreter()
    interp._set_source(code)
    interp.current_filename = code_name
    interp.coverage = tracker
    exit_code = 0
    try:
        interp.execute_program(program)
        # 测试文件约定(无 main, 全是 test_* 函数): 与 --test 同口径执行用例,
        # 否则覆盖率报告是 0% 的空壳 — 覆盖要对准真实执行面
        if 'main' not in interp.functions:
            for tname in sorted(n for n in interp.functions if n.startswith('test_')):
                interp.execute_function(interp.functions[tname], [])
    except Exception as e:
        err = wrap_intent_error(e, interp)
        print(render_intent_error(err, interp), file=sys.stderr)
        exit_code = 1
    print()
    print(tracker.report())
    return exit_code


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

        # P0.1: 提供源码行,供错误渲染显示出错行片段
        interpreter._set_source(code)
        result = interpreter.execute_program(ast)

        if parser.errors:
            print(f"\n⚠️  程序部分执行成功({len(parser.errors)} 个错误已跳过)")
        else:
            print(f"\n✅ 程序执行成功")
        if result is not None and not (isinstance(result.value, int) and result.value == 0):
            print(f"返回值: {result}")

    except Exception as e:
        err = wrap_intent_error(e, interpreter)
        print()
        print(render_intent_error(err, interpreter))
        sys.exit(1)

# ==================== P0.4 CLI 辅助 ====================

# ==================== P0.4 CLI 辅助 ====================

# ── P2.1 包管理 V0.1(本地优先, 无版本求解器) ──────────

def load_project_manifest(path: str = "intent.toml") -> Optional[dict]:
    """读取项目清单 intent.toml(P2.1 / PK1)

    格式:
      [project]
      name = "myproj"
      version = "0.1.0"
      [deps]
      mylib = { git = "https://github.com/x/mylib.git", version = "^1.2" }
      utils = "../utils"        # 本地路径依赖
      mathkit = "^1.2"          # 裸版本约束 → 本地注册表同名包(PK1)

    返回 None 表示无清单文件。tomllib 不可用时抛清晰错误。
    deps 每项规范化为 {'source': 路径或URL, 'version': 约束串或 ''}。
    """
    if not os.path.isfile(path):
        return None
    try:
        import tomllib
    except ImportError:
        raise RuntimeError("解析 intent.toml 需要 Python 3.11+ 的 tomllib 模块")
    with open(path, 'rb') as f:
        data = tomllib.load(f)
    manifest = {
        'name': data.get('project', {}).get('name', ''),
        'version': data.get('project', {}).get('version', '0.0.0'),
        'deps': {},
        'raw': data,
    }
    for dep_name, spec in data.get('deps', {}).items():
        if isinstance(spec, dict):
            manifest['deps'][dep_name] = {
                'source': spec.get('git') or spec.get('path') or '',
                'version': str(spec.get('version', '') or ''),
            }
        else:
            manifest['deps'][dep_name] = {'source': str(spec), 'version': ''}
    return manifest

def _dep_dir_name(dep_name: str, source: str) -> str:
    """从依赖名/源推导本地目录名"""
    if source.startswith(('http://', 'https://', 'git@')):
        base = source.rstrip('/').split('/')[-1]
        if base.endswith('.git'):
            base = base[:-4]
        return base or dep_name
    return dep_name

def install_dependency(dep_name: str, source: str, lib_dir: str = "lib") -> bool:
    """安装单个依赖(P2.1) — git clone 或本地路径复制

    刻意不做版本求解: 冲突了直接报错让人工裁决 —
    连接贵在简单可信, 版本求解器是复杂性瘟疫。
    """
    import subprocess
    target = os.path.join(lib_dir, _dep_dir_name(dep_name, source))
    if source.startswith(('http://', 'https://', 'git@')):
        if os.path.isdir(os.path.join(target, '.git')):
            print(f"  ⬇️  更新 {dep_name} ({source})")
            r = subprocess.run(['git', '-C', target, 'pull', '--ff-only'],
                               capture_output=True, text=True)
            return r.returncode == 0
        print(f"  📦 克隆 {dep_name} ({source})")
        os.makedirs(lib_dir, exist_ok=True)
        r = subprocess.run(['git', 'clone', '--depth', '1', source, target],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ❌ 克隆失败: {r.stderr.strip()}")
        return r.returncode == 0
    # 本地路径依赖: 符号链接或目录复制
    src_path = os.path.abspath(source)
    if not os.path.isdir(src_path):
        print(f"  ❌ 本地依赖不存在: {src_path}")
        return False
    os.makedirs(lib_dir, exist_ok=True)
    import shutil
    if os.path.isdir(target):
        shutil.rmtree(target)
    shutil.copytree(src_path, target, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    print(f"  📦 复制 {dep_name} ({source})")
    return True

# ==================== PK1 依赖解析器 ====================
# 语义化版本约束 + 冲突解决 + intent.lock 锁定。
# 设计: 约束累积 → 候选枚举 → 公共兼容集取最高(回退) → 无解报冲突。
# 刻意不做: 全局 SAT 求解(复杂性瘟疫); git 依赖的 tag 枚举(未克隆无版本可读)。

class DependencyConflict(Exception):
    """依赖冲突: 同一包的多个约束不存在公共兼容版本"""


def _parse_semver(vstr: str) -> tuple:
    """语义化版本 → (major, minor, patch, prerelease_ids|None)

    '1.2.3' → (1,2,3,None); '1.2' → (1,2,0,None); '1.0.0-beta.1' → (1,0,0,('beta','1'))
    正式版高于同号预发布版(semver 共识)。
    """
    s = (vstr or '').strip()
    if s.startswith('v'):
        s = s[1:]
    if not s:
        raise ValueError("空版本号")
    core, sep, pre = s.partition('-')
    parts = core.split('.')
    if len(parts) > 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"非法语义化版本: '{vstr}'")
    while len(parts) < 3:
        parts.append('0')
    pre_ids = tuple(pre.split('.')) if sep and pre else None
    return (int(parts[0]), int(parts[1]), int(parts[2]), pre_ids)


def _cmp_semver(a: tuple, b: tuple) -> int:
    """semver 比较: -1 / 0 / 1"""
    for i in range(3):
        if a[i] != b[i]:
            return -1 if a[i] < b[i] else 1
    pa, pb = a[3], b[3]
    if pa is None and pb is None:
        return 0
    if pa is None:
        return 1
    if pb is None:
        return -1
    for x, y in zip(pa, pb):
        xd, yd = x.isdigit(), y.isdigit()
        if xd and yd:
            if int(x) != int(y):
                return -1 if int(x) < int(y) else 1
        elif xd != yd:
            return -1 if xd else 1   # 数字标识符 < 字母标识符
        elif x != y:
            return -1 if x < y else 1
    if len(pa) != len(pb):
        return -1 if len(pa) < len(pb) else 1
    return 0


def _semver_str(v: tuple) -> str:
    base = f"{v[0]}.{v[1]}.{v[2]}"
    return base + (f"-{'.'.join(v[3])}" if v[3] else "")


def _caret_bound(vstr: str) -> tuple:
    """^ 的上界(不含): ^1.2.3→2.0.0; ^0.2.3→0.3.0; ^0.0.3→0.0.4; ^1→2.0.0"""
    s = vstr.strip().lstrip('v').split('-')[0]
    parts = [p for p in s.split('.') if p != '']
    nums = [int(p) for p in parts] + [0, 0, 0]
    major, minor, patch = nums[0], nums[1], nums[2]
    if major > 0:
        return (major + 1, 0, 0, None)
    if len(parts) >= 2:
        if minor > 0:
            return (0, minor + 1,0, None)
        return (0, 0, patch + 1, None)
    return (1, 0, 0, None)


def _tilde_bound(vstr: str) -> tuple:
    """~ 的上界(不含): ~1.2.3→1.3.0; ~1.2→1.3.0; ~1→2.0.0"""
    s = vstr.strip().lstrip('v').split('-')[0]
    parts = [p for p in s.split('.') if p != '']
    nums = [int(p) for p in parts] + [0, 0, 0]
    if len(parts) >= 2:
        return (nums[0], nums[1] + 1, 0, None)
    return (nums[0] + 1, 0, 0, None)


def _parse_constraint(cstr: str) -> list:
    """约束串 → [(op, bound), ...] AND 语义

    '*'/'' 任意; '^1.2' 兼容; '~1.2' 补丁级; '>=1.0, <2.0' 多段;
    '=1.2.3' 或裸 '1.2.3' 精确匹配。
    """
    cstr = (cstr or '').strip()
    if cstr in ('', '*', 'any'):
        return []
    clauses = []
    for part in cstr.split(','):
        part = part.strip()
        if not part:
            continue
        if part.startswith('^'):
            clauses.append(('>=', _parse_semver(part[1:])))
            clauses.append(('<', _caret_bound(part[1:])))
        elif part.startswith('~'):
            clauses.append(('>=', _parse_semver(part[1:])))
            clauses.append(('<', _tilde_bound(part[1:])))
        elif part.startswith('>='):
            clauses.append(('>=', _parse_semver(part[2:])))
        elif part.startswith('<='):
            clauses.append(('<=', _parse_semver(part[2:])))
        elif part.startswith('=='):
            clauses.append(('=', _parse_semver(part[2:])))
        elif part.startswith('>'):
            clauses.append(('>', _parse_semver(part[1:])))
        elif part.startswith('<'):
            clauses.append(('<', _parse_semver(part[1:])))
        elif part.startswith('='):
            clauses.append(('=', _parse_semver(part[1:])))
        else:
            clauses.append(('=', _parse_semver(part)))
    return clauses


def _constraint_allows(clauses: list, version: tuple) -> bool:
    for op, bound in clauses:
        c = _cmp_semver(version, bound)
        if op == '>=' and c < 0:
            return False
        if op == '>' and c <= 0:
            return False
        if op == '<=' and c > 0:
            return False
        if op == '<' and c >= 0:
            return False
        if op == '=' and c != 0:
            return False
    return True


def _pkg_manifest_at(pkg_dir: str) -> Optional[dict]:
    """读取依赖包目录下的 intent.toml; 无则 None(裸模块目录)"""
    path = os.path.join(pkg_dir, 'intent.toml')
    if not os.path.isfile(path):
        return None
    return load_project_manifest(path)


def _registry_candidates(name: str, registry_dir: str) -> list:
    """本地注册表中同名包的全部候选 → [(version_tuple, snapshot_dir)] 按版本降序"""
    idx_path = os.path.join(registry_dir, 'registry.json')
    if not os.path.isfile(idx_path):
        return []
    try:
        with open(idx_path, 'r', encoding='utf-8') as f:
            index = json.load(f)
    except (OSError, ValueError):
        return []
    entry = index.get(name)
    if not entry:
        return []
    import functools
    cands = []
    for ver, meta in (entry.get('versions') or {}).items():
        try:
            vt = _parse_semver(ver)
        except ValueError:
            continue
        cands.append((vt, os.path.join(registry_dir, meta.get('path', ''))))
    cands.sort(key=functools.cmp_to_key(lambda a, b: _cmp_semver(a[0], b[0])),
               reverse=True)
    return cands


def _is_path_like(source: str, parent_dir: str) -> bool:
    """依赖源是路径还是注册表包名: 含分隔符/相对点/目录存在 → 路径"""
    return ('/' in source or os.sep in source or source.startswith('.')
            or os.path.isdir(os.path.join(parent_dir, source)))


def resolve_dependencies(project_dir: str, root_manifest: dict,
                         registry_dir: Optional[str] = None) -> dict:
    """BFS 解析依赖图 → lock 结构 {name: {version, source, deps, required_by}}

    - 约束累积: 同一包被多处要求时合并全部约束(钻石依赖)
    - 候选枚举: path/git 依赖单候选; 注册表依赖多版本候选
    - 择高回退: 满足全部约束的候选取最高版本(最新不满足自动退到次高)
    - 冲突: 无公共兼容版本, 或同目录版本漂移 → DependencyConflict
    """
    if registry_dir is None:
        registry_dir = os.path.join(os.path.abspath(project_dir), 'registry')
    constraints = {}   # name → [(constraint_str, required_by)]
    candidates = {}    # name → {source_key: (version_tuple|None, dep_dir|None, deps)}
    order = []         # 首次出现序(报告稳定)
    queue = deque([(n, s, 'root(项目清单)', os.path.abspath(project_dir))
                   for n, s in root_manifest['deps'].items()])

    def register(name, spec, parent_dir):
        """登记一个候选; 返回本次新增的候选 key(其子树待遍历)"""
        source = (spec.get('source') or '').strip()
        if not source:
            raise DependencyConflict(f"依赖 '{name}' 没有源地址")
        new_keys = []
        if source.startswith(('http://', 'https://', 'git@')):
            key = f"git:{source}"
            if key not in candidates[name]:
                # git 依赖未克隆读不到版本 — 占位候选, install 后校验
                candidates[name][key] = (None, None, {})
                new_keys.append(key)
        elif not _is_path_like(source, parent_dir):
            for vt, snap in _registry_candidates(name, registry_dir):
                key = f"registry:{name}@{_semver_str(vt)}"
                if key in candidates[name]:
                    continue
                pkg = _pkg_manifest_at(snap)
                candidates[name][key] = (vt, snap, pkg['deps'] if pkg else {})
                new_keys.append(key)
            if not candidates[name]:
                raise DependencyConflict(
                    f"注册表中没有包 '{name}'(registry_dir={registry_dir})")
        else:
            dep_dir = source if os.path.isabs(source) \
                else os.path.abspath(os.path.join(parent_dir, source))
            if not os.path.isdir(dep_dir):
                raise DependencyConflict(f"依赖目录不存在: {dep_dir}")
            pkg = _pkg_manifest_at(dep_dir)
            if pkg and (pkg.get('version') or '').strip():
                try:
                    vt = _parse_semver(pkg['version'])
                except ValueError as e:
                    raise DependencyConflict(f"依赖 '{name}' 版本非法: {e}")
                deps = pkg['deps']
            else:
                vt, deps = None, {}
            key = f"path:{dep_dir}"
            prev = candidates[name].get(key)
            if prev is None:
                candidates[name][key] = (vt, dep_dir, deps)
                new_keys.append(key)
            elif vt is not None and prev[0] is not None \
                    and _cmp_semver(vt, prev[0]) != 0:
                raise DependencyConflict(
                    f"包 '{name}' 同目录版本漂移: {_semver_str(prev[0])} → "
                    f"{_semver_str(vt)}(以先见者为准, 请人工裁决)")
        return new_keys

    while queue:
        name, spec, required_by, parent_dir = queue.popleft()
        ver_c = (spec.get('version') or '').strip() or '*'
        if name not in constraints:
            order.append(name)
            candidates[name] = {}
        constraints.setdefault(name, []).append((ver_c, required_by))
        for key in register(name, spec, parent_dir):
            _vt, dep_dir, deps = candidates[name][key]
            if dep_dir is None:
                continue
            for dn, ds in deps.items():
                queue.append((dn, ds, name, dep_dir))

    # ── 仲裁: 每个包在满足全部约束的候选中取最高版本 ──
    resolved = {}
    for name in order:
        cons = constraints[name]
        best = None
        for key, (vt, dep_dir, deps) in candidates[name].items():
            if vt is None:
                continue
            if not all(_constraint_allows(_parse_constraint(c), vt)
                       for c, _by in cons):
                continue
            if best is None or _cmp_semver(vt, best[0]) > 0:
                best = (vt, key, dep_dir, deps)
        if best is None:
            versioned = [(k, v) for k, v in candidates[name].items()
                         if v[0] is not None]
            if not versioned:
                # 只有 git 候选: 版本留空, install 后校验
                key, (_vt, dep_dir, deps) = next(iter(candidates[name].items()))
                resolved[name] = {'version': None, 'source': key[4:],
                                  'deps': {}, 'required_by': [b for _c, b in cons]}
                continue
            detail = " ∧ ".join(f"{c}(by {b})" for c, b in cons)
            avail = ", ".join(_semver_str(v[0]) for _k, v in versioned)
            raise DependencyConflict(
                f"包 '{name}' 无公共兼容版本: 约束 [{detail}] vs 可用 [{avail}]")
        vt, key, dep_dir, deps = best
        resolved[name] = {
            'version': _semver_str(vt),
            'source': dep_dir if key.startswith('path:') else key.split(':', 1)[1],
            'deps': {dn: dict(ds) for dn, ds in deps.items()},
            'required_by': [b for _c, b in cons],
            '_constraints': [c for c, _by in cons],
        }
    return resolved


def write_lockfile(project_dir: str, resolved: dict, root_manifest: dict) -> str:
    """写 intent.lock(JSON): 锁定版本/来源/直接依赖/要求方"""
    lock = {
        'version': 1,
        'project': root_manifest.get('name') or '',
        'packages': {
            name: {
                'version': info['version'],
                'source': info['source'],
                'deps': {dn: (ds.get('version') or '*')
                         for dn, ds in info['deps'].items()},
                'required_by': info['required_by'],
            }
            for name, info in resolved.items()
        },
    }
    path = os.path.join(project_dir, 'intent.lock')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(lock, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return path


def render_resolution_plan(root_manifest: dict, resolved: dict,
                           project_dir: str) -> str:
    """依赖解析计划(判定命令要求输出含「依赖解析」)"""
    lines = [f"🔍 依赖解析: {root_manifest.get('name') or '项目'} "
             f"v{root_manifest.get('version', '0.0.0')} ({project_dir})"]
    for name, info in resolved.items():
        ver = info['version'] or '未锁定(git)'
        src = info['source'] or '?'
        if not src.startswith(('http://', 'https://', 'git@')):
            try:
                src = os.path.relpath(src, project_dir)
            except ValueError:
                pass
        # 约束合并展示: 该包被全部要求方施加的约束(去重保序)
        seen, merged = set(), []
        for cstr in info.get('_constraints', []):
            if cstr not in seen:
                seen.add(cstr)
                merged.append(cstr)
        cons_txt = " ∧ ".join(merged) if merged else "(无约束)"
        lines.append(f"  {name} {ver} ← {src}   约束: {cons_txt}")
    lines.append(f"  ✅ 解析完成: {len(resolved)} 个包, 0 冲突")
    return "\n".join(lines)


def run_install(source: Optional[str] = None, manifest_path: str = "intent.toml",
                dry_run: bool = False, project_dir: Optional[str] = None) -> int:
    """--install: 安装依赖(PK1 起带版本解析)

    带 URL: 安装单个; 不带: 按 intent.toml 的 [deps] 批量安装。
    --dry-run: 只跑依赖解析(约束合并/冲突检测/计划), 不安装不写锁。
    project_dir: 批量模式项目目录(判定命令 --install --dry-run <dir> 传入)。
    """
    if source:
        # 本地目录且带 intent.toml → 按项目批量解析(而非当成单个依赖源)
        if os.path.isdir(source) and os.path.isfile(os.path.join(source, 'intent.toml')):
            return _run_batch_install(source, dry_run=dry_run)
        ok = install_dependency(_dep_dir_name('dep', source), source)
        print("✅ 安装完成" if ok else "❌ 安装失败")
        return 0 if ok else 1
    return _run_batch_install(project_dir=project_dir,
                              manifest_path=manifest_path, dry_run=dry_run)


def _run_batch_install(project_dir: Optional[str] = None,
                       manifest_path: str = "intent.toml",
                       dry_run: bool = False) -> int:
    """批量安装: 按项目 intent.toml 的 [deps] 解析(PK1)并安装"""
    base_dir = os.path.abspath(project_dir) if project_dir else os.getcwd()
    mpath = os.path.join(base_dir, os.path.basename(manifest_path))
    manifest = load_project_manifest(mpath)
    if manifest is None:
        print(f"❌ 找不到 {mpath}(可用 --install <git-url> 安装单个依赖)")
        return 2
    if not manifest['deps']:
        print(f"✅ {manifest['name'] or '项目'} 无依赖")
        return 0
    try:
        resolved = resolve_dependencies(base_dir, manifest)
    except DependencyConflict as e:
        print(f"❌ 依赖冲突: {e}")
        return 1
    print(render_resolution_plan(manifest, resolved, base_dir))
    if dry_run:
        print("   (--dry-run: 未写入 intent.lock, 未执行安装)")
        return 0
    lock_path = write_lockfile(base_dir, resolved, manifest)
    try:
        lock_rel = os.path.relpath(lock_path, os.getcwd())
    except ValueError:
        lock_rel = lock_path
    print(f"   🔒 已写入 {lock_rel}")
    lib_dir = os.path.join(base_dir, 'lib')
    failed = []
    for name, info in resolved.items():
        if not info['source'] or info['source'].startswith(
                ('http://', 'https://', 'git@')):
            continue
        if not install_dependency(name, info['source'], lib_dir=lib_dir):
            failed.append(name)
    if failed:
        print(f"❌ {len(failed)} 个依赖安装失败: {', '.join(failed)}")
        return 1
    print("✅ 全部依赖安装完成(版本已锁定 intent.lock)")
    return 0

# ==================== P2.2 Formatter ====================

def format_code(code: str) -> str:
    """Intent 代码格式化(P2.2) — token 流重排, 不动语义

    大道不称: 格式不该是个人品味, 是语言的默认秩序。
    规则刻意少(对齐 gofmt 哲学):
      - 4 空格缩进, { 后加深, } 前恢复
      - K&R 花括号: def f() { — { 不换行
      - ; 结尾换行(类内方法 } 也换行)
      - 二元运算符/=>/管道两侧空格; , 后空格; ( [ . : 紧贴
      - 保留注释(行注释跟随所在行)
    不做: 80 列软限制不断行(太长是内容问题不是格式问题)、无可配置项。
    """
    tokens = Lexer(code, keep_comments=True).tokenize()
    out_lines = []
    depth = 0
    line_parts = []          # 当前行的 token 片段
    pending_comments = []    # 独立成行的注释(上一行遗留)

    def flush_line():
        nonlocal line_parts
        text = "".join(line_parts).rstrip()
        if text:
            out_lines.append("    " * depth + text)
        line_parts = []

    def spacing(prev_tok, tok) -> str:
        """两个 token 之间是否需要空格"""
        if prev_tok is None:
            return ""
        pv, tv = prev_tok.value, tok.value
        pt, tt = prev_tok.type, tok.type
        # 注释前保留两空格
        if tt == TokenType.COMMENT:
            return "  " if line_parts else ""
        # 冒号: 类型标注 x: Int / 字典 "k": v — 前紧贴, 后空格
        if tv == ':' and pt != TokenType.COMMENT:
            return ""
        if pv == ':':
            # match 分支标签 score: 后不空格; 其余冒号后空格
            if tv == '{':
                return " "
            return " "
        # 开括号/点/分号类紧贴
        if tv in (')', ']', ',', ';', '.'):
            return ""
        if tv == '(':
            # 调用/定义紧贴; 关键字(if/while/for/match)后留空格
            if pt == TokenType.KEYWORD and pv in ('if', 'while', 'for', 'match', 'return', 'catch', 'with'):
                return " "
            return ""
        if pv in ('(', '[', '.', '!'):
            return ""
        if pv == ',':
            return " "
        if pv == ';':
            return ""  # ; 后通常换行, 兜底
        # => 与管道两侧空格
        if pv in ('=>', '|>') or tv in ('=>', '|>'):
            return " "
        # 运算符两侧空格
        if pt == TokenType.OPERATOR or tt == TokenType.OPERATOR:
            return " "
        if pt == TokenType.SYMBOL and pv in ('+', '-', '*', '/', '%', '**', '//', '==', '!=', '<', '>', '<=', '>=', '='):
            return " "
        if tt == TokenType.SYMBOL and tv in ('+', '-', '*', '/', '%', '**', '//', '==', '!=', '<', '>', '<=', '>=', '='):
            return " "
        # 默认: 关键字/标识符/字面量之间留空格
        return " "

    prev = None
    for tok in tokens:
        if tok.type == TokenType.EOF:
            break
        if tok.type == TokenType.NEWLINE:
            flush_line()
            prev = None
            continue
        if tok.type == TokenType.COMMENT:
            if line_parts:
                # 行尾注释: 拼到当前行
                line_parts.append("  " + tok.value)
                flush_line()
                prev = None
            else:
                # 独立注释行
                out_lines.append("    " * depth + tok.value)
            continue
        # 花括号深度管理
        if tok.value == '{':
            line_parts.append(" {")
            flush_line()
            depth += 1
            prev = None
            continue
        if tok.value == '}':
            if line_parts:
                flush_line()
            depth = max(0, depth - 1)
            line_parts.append("}")
            prev = tok
            continue
        # 普通 token
        if tok.type == TokenType.STRING:
            # Lexer 剥掉了引号 — formatter 还原(f 前缀一并恢复)
            prefix = 'f' if getattr(tok, 'is_fstring', False) else ''
            text = prefix + '"' + tok.value + '"'
            line_parts.append(spacing(prev, tok) + text)
        else:
            line_parts.append(spacing(prev, tok) + tok.value)
        prev = tok
        # ; 结尾换行
        if tok.value == ';':
            flush_line()
            prev = None
        # match 分支: 行内出现过 => 时, 分支逗号后换行
        elif tok.value == ',' and any('=>' in p for p in line_parts):
            flush_line()
            prev = None
    flush_line()
    # 收尾: 去掉多余空行(最多保留一个连续空行由源码空行决定 — V0.1 统一单空行分隔块)
    result = "\n".join(out_lines)
    return result + "\n" if result else ""

def run_format(path: str) -> int:
    """--fmt: 格式化文件, 结果打印到 stdout(重定向即写回)"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"❌ 找不到文件: {path}")
        return 2
    try:
        formatted = format_code(code)
    except SyntaxError as e:
        print(f"❌ 语法错误, 无法格式化: {e}")
        return 2
    print(formatted, end='')
    return 0

# ==================== P2.3 Linter ====================

def _walk_ast(node):
    """遍历 AST 所有节点(dataclass 通用递归, 含 dict/list/tuple 容器)"""
    from dataclasses import fields, is_dataclass
    if node is None:
        return
    yield node
    if is_dataclass(node):
        for f in fields(node):
            v = getattr(node, f.name, None)
            if isinstance(v, ASTNode):
                yield from _walk_ast(v)
            elif isinstance(v, dict):
                for item in v.values():
                    if isinstance(item, ASTNode):
                        yield from _walk_ast(item)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, ASTNode):
                        yield from _walk_ast(item)
                    elif isinstance(item, tuple):
                        for sub in item:
                            if isinstance(sub, ASTNode):
                                yield from _walk_ast(sub)

def lint_code(code: str) -> List[Tuple[str, int, int, str]]:
    """Intent 静态检查(P2.3) — 基于 AST, 不执行

    省察克治的自动化。规则刻意少, 每条对应 Intent 的一条哲学:
      E1 let 常量被重新赋值        — 不可变是默认, 改了就是违约
      W1 catch 吞掉错误却什么都不做 — 沉默的 catch 比没有 catch 更糟
      I1 顶层函数无契约            — 契约是身份证, 建议随身携带
      W2 import 了却没用到          — 不带多余的东西上路
    返回 [(级别, 行, 列, 消息), ...]
    """
    issues = []
    tokens = Lexer(code).tokenize()
    parser = Parser(tokens, code)
    program = parser.parse()

    # E1: 不可变变量被重新赋值 — 作用域敏感(块内 let 不出块, 方法间同名互不相干)
    from dataclasses import fields as _dc_fields, is_dataclass as _is_dc

    def _scope_aware_check(root):
        scope_stack = [{}]   # name -> (is_const, decl_line)
        local_issues = []

        def declare(name, is_const, line):
            scope_stack[-1][name] = (is_const, line)

        def find(name):
            for scope in reversed(scope_stack):
                if name in scope:
                    return scope[name]
            return None

        def visit(node):
            if node is None:
                return
            if isinstance(node, VariableDecl):
                declare(node.name, node.is_const, node.line)
                return
            if isinstance(node, Assignment):
                found = find(node.target)
                if found is not None and found[0]:
                    local_issues.append(('E', node.line, node.column,
                                         f"let 声明的常量 '{node.target}' (第 {found[1]} 行) 被重新赋值"
                                         f"(需要 mut 就诚实声明 let mut)"))
                return
            if isinstance(node, (IfStmt, WhileStmt, ForStmt, TryStmt, WithStmt)):
                # 条件/可迭代表达式属于外层作用域
                for fname in ('condition', 'iterable', 'resource'):
                    v = getattr(node, fname, None)
                    if v is not None:
                        visit(v)
                if isinstance(node, IfStmt):
                    bodies = [node.then_branch] + [b for _, b in node.elif_branches] + [node.else_branch]
                elif isinstance(node, TryStmt):
                    bodies = [node.try_body, node.catch_body, node.finally_body]
                else:
                    bodies = [node.body]
                for body in bodies:
                    scope_stack.append({})
                    for stmt in body:
                        visit(stmt)
                    scope_stack.pop()
                return
            # 其余节点: 递归子节点
            if _is_dc(node):
                for f in _dc_fields(node):
                    v = getattr(node, f.name, None)
                    if isinstance(v, ASTNode):
                        visit(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, ASTNode):
                                visit(item)
                    elif isinstance(v, dict):
                        for item in v.values():
                            if isinstance(item, ASTNode):
                                visit(item)

        nodes = root if isinstance(root, list) else [root]
        for n in nodes:
            visit(n)
        return local_issues

    issues.extend(_scope_aware_check(program.statements))
    for func in program.functions.values():
        issues.extend(_scope_aware_check(func))
    for node in _walk_ast(program):
        if isinstance(node, ClassStmt):
            for method in node.methods:
                issues.extend(_scope_aware_check(method))

    # W1: 空 catch 块
    for node in _walk_ast(program):
        if isinstance(node, TryStmt) and node.catch_var and not node.catch_body:
            issues.append(('W', node.line, node.column,
                           "catch 绑定了错误变量却什么都不做 — 沉默的 catch 比没有 catch 更糟"))

    # I1: 顶层函数无契约
    for func in program.functions.values():
        if not func.requires and not func.ensures:
            issues.append(('I', func.line, func.column,
                           f"函数 '{func.name}' 无 requires/ensures — 契约是身份证, 建议携带"))

    # W2: 未使用的 import(import std.math 后用 math.x 或 std.math.x 都算用过)
    imports = []   # (module_name, alias, line, col)
    used_names = set()
    for node in _walk_ast(program):
        if isinstance(node, ImportStmt):
            imports.append((node.module_name, node.alias, node.line, node.column))
        if isinstance(node, MemberAccess):
            root = node.obj
            while isinstance(root, MemberAccess):
                root = root.obj
            if isinstance(root, Variable):
                used_names.add(root.name)
    for module_name, alias, line, col in imports:
        candidates = set()
        if alias:
            candidates.add(alias)
        else:
            candidates.add(module_name.split('.')[0])   # std.math → std
            candidates.add(module_name.split('.')[-1])  # std.math → math
        if not (candidates & used_names):
            issues.append(('W', line, col,
                           f"import 的 '{module_name}' 未被使用 — 不带多余的东西上路"))
    return issues

def run_lint(path: str) -> int:
    """--lint: 静态检查, 打印报告。有 E 级问题退出 1, 否则 0(警告不阻断)"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"❌ 找不到文件: {path}")
        return 2
    try:
        issues = lint_code(code)
    except SyntaxError as e:
        print(f"❌ 语法错误, 无法检查: {e}")
        return 2
    if not issues:
        print(f"✅ {path}: 无问题")
        return 0
    level_name = {'E': '错误', 'W': '警告', 'I': '提示'}
    level_icon = {'E': '❌', 'W': '⚠️ ', 'I': '💡'}
    errors = 0
    for level, line, col, msg in sorted(issues, key=lambda x: (x[1], x[2])):
        print(f"{level_icon[level]} {level_name[level]} {path}:{line}:{col}")
        print(f"   {msg}")
        if level == 'E':
            errors += 1
    print(f"\n共 {len(issues)} 条({errors} 错误 / "
          f"{sum(1 for i in issues if i[0]=='W')} 警告 / "
          f"{sum(1 for i in issues if i[0]=='I')} 提示)")
    return 1 if errors else 0

# ==================== P2.4 Doc 生成 ====================

def _unparse(node) -> str:
    """把表达式 AST 反打印为源码字符串(doc 生成用)"""
    if node is None:
        return ""
    if isinstance(node, Literal):
        if node.literal_type == 'string':
            return f'"{node.value}"'
        return str(node.value)
    if isinstance(node, Variable):
        return node.name
    if isinstance(node, BinaryOp):
        return f"{_unparse(node.left)} {node.op} {_unparse(node.right)}"
    if isinstance(node, UnaryOp):
        return f"{node.op}{_unparse(node.operand)}"
    if isinstance(node, CallExpr):
        inner = _unparse(node.func)
        args = ", ".join(_unparse(a) for a in node.args)
        return f"{inner}({args})"
    if isinstance(node, MemberAccess):
        return f"{_unparse(node.obj)}.{node.member}"
    if isinstance(node, TernaryExpr):
        return f"if {_unparse(node.condition)} {{ ... }} else {{ ... }}"
    return f"<{type(node).__name__}>"

def generate_docs(code: str, title: str = "模块文档") -> str:
    """从 Intent 源码生成 markdown 文档(P2.4)

    函数签名 + 上方注释块(文档注释) + 契约 + 参数表。
    哲学注释是文档的一部分 — 代码解释自己为什么存在。
    """
    tokens = Lexer(code).tokenize()
    parser = Parser(tokens, code)
    program = parser.parse()

    # 按行取源码, 用于提取函数上方的注释块
    lines = code.split('\n')

    def comment_block_before(line_no: int) -> List[str]:
        """提取 line_no 行(1-based)之前的连续注释行"""
        block = []
        i = line_no - 2  # 0-based 的前一行
        while i >= 0:
            stripped = lines[i].strip()
            if stripped.startswith('//'):
                block.append(stripped[2:].strip())
                i -= 1
            elif stripped == '':
                break
            else:
                break
        return list(reversed(block))

    def param_type_str(t: Optional[str]) -> str:
        return t if t else 'Any'

    out = [f"# {title}", ""]
    funcs = sorted(program.functions.values(), key=lambda f: (f.line, f.column))
    for func in funcs:
        doc_lines = comment_block_before(func.line)
        out.append(f"## `{func.name}`")
        out.append("")
        if doc_lines:
            for dl in doc_lines:
                out.append(f"> {dl}")
            out.append("")
        # 签名
        params = ", ".join(f"{p[0]}: {param_type_str(p[1])}" for p in func.params)
        sig = f"def {func.name}({params})"
        if func.return_type:
            sig += f" -> {func.return_type}"
        out.append("```intent")
        out.append(sig)
        if func.requires:
            for r in func.requires:
                out.append(f"    requires {_unparse(r)}")
        if func.ensures:
            for e in func.ensures:
                out.append(f"    ensures {_unparse(e)}")
        out.append("```")
        out.append("")
        if func.params:
            out.append("| 参数 | 类型 |")
            out.append("|---|---|")
            for p in func.params:
                out.append(f"| `{p[0]}` | {param_type_str(p[1])} |")
            out.append("")
        if func.requires:
            out.append("**前置条件**:")
            for r in func.requires:
                out.append(f"- {_unparse(r)}")
            out.append("")
        if func.ensures:
            out.append("**后置条件**:")
            for e in func.ensures:
                out.append(f"- {_unparse(e)}")
            out.append("")
    # 类
    for node in _walk_ast(program):
        if isinstance(node, ClassStmt):
            out.append(f"## class `{node.name}`")
            out.append("")
            doc_lines = comment_block_before(node.line)
            if doc_lines:
                for dl in doc_lines:
                    out.append(f"> {dl}")
                out.append("")
            for method in node.methods:
                params = ", ".join(f"{p[0]}: {param_type_str(p[1])}" for p in method.params)
                out.append(f"- `{method.name}({params})`"
                           + (f" -> `{method.return_type}`" if method.return_type else ""))
            out.append("")
    return "\n".join(out) + "\n"

def run_doc(path: str) -> int:
    """--doc: 生成模块文档到 stdout"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"❌ 找不到文件: {path}")
        return 2
    try:
        title = os.path.splitext(os.path.basename(path))[0]
        print(generate_docs(code, title))
    except SyntaxError as e:
        print(f"❌ 语法错误, 无法生成文档: {e}")
        return 2
    return 0

# ==================== L1 渐进类型: 静态类型检查器 ====================
# mypy-lite 切片: 标注处检查 + 推断处放过。
# 哲学同构: 契约(运行时可验证)是主防线, 类型(静态提示)是副防线 —
# 已知的检查, 未知的放过; 显式的信任, 不猜。

# 内置函数返回类型白名单(标注处检查的最小知识集; None = 放过不猜)
_BUILTIN_RETURN_TYPES = {
    'len': 'Int', 'int': 'Int', 'ord': 'Int', 'hex': 'Int', 'bin': 'Int',
    'float': 'Float',
    'str': 'String', 'type_of': 'String', 'upper': 'String', 'lower': 'String',
    'strip': 'String', 'join': 'String', 'replace': 'String', 'format': 'String',
    'keys': 'List', 'values': 'List', 'sorted': 'List', 'reversed': 'List',
    'range': 'List', 'enumerate': 'List', 'zip': 'List', 'list': 'List',
    'set': 'Set',
    'dict': 'Dict', 'any': 'Bool', 'all': 'Bool',
}

# 数值互通(spec §2.1 刻意宽松): Int 标注接受 Float 值, 反之亦然
_NUMERIC_TYPES = {'Int', 'Float'}


def _base_type(type_str: str) -> str:
    """取类型基类名: 'List[Int]' -> 'List', 'A | B' -> 'A | B'(Union 不拆)"""
    if type_str is None:
        return 'Any'
    for i, ch in enumerate(type_str):
        if ch in '<[':
            return type_str[:i]
    return type_str


def _split_union(type_str: str) -> List[str]:
    """拆 Union: 'A | B' -> ['A', 'B']; 非 Union 返回 [type_str]"""
    if '|' in type_str:
        return [p.strip() for p in type_str.split('|')]
    return [type_str]


class TypeChecker:
    """L1 渐进类型静态检查器(mypy-lite)。

    策略(反膨胀的最小切片):
      - 只查「标注处」: 变量声明/参数传递/return 的标注 vs 可推断出的实际类型;
      - 「推断处放过」: 推断不出类型的一律不报(显式信任, 不猜);
      - 容器只查基类: List[Int] 的元素类型不查(留待完整版);
      - 数值互通: Int/Float 互相接受(spec §2.1);
      - 泛型参数视为 Any: identity<T>(x: T) 的调用不误报;
      - 类型别名透明解析: type Meters = Float; let m: Meters = 1.5; 通过。
    """

    def __init__(self, ast: 'Program', code_name: str = "<input>"):
        self.ast = ast
        self.code_name = code_name
        self.errors: List[str] = []
        self.aliases: Dict[str, str] = {}
        self.checked_count = 0    # 标注处检查次数
        self.inferred_count = 0   # 推断放过次数(无标注/未知)
        # 预收集类型别名
        for stmt in ast.statements:
            if isinstance(stmt, TypeAliasStmt):
                self.aliases[stmt.name] = stmt.aliased_type

    # ---------- 类型解析与兼容 ----------

    def _resolve_alias(self, type_str: str, depth: int = 0) -> str:
        """别名透明解析(防环, 深度上限 5)"""
        if depth > 5 or type_str not in self.aliases:
            return type_str
        return self._resolve_alias(self.aliases[type_str], depth + 1)

    def _compatible(self, declared: Optional[str], actual: Optional[str],
                    type_params: Optional[set] = None) -> bool:
        """实际类型能否赋给声明标注。actual=None(推断不出) → 放过"""
        if declared is None or declared == 'Any':
            return True
        if actual is None:
            self.inferred_count += 1
            return True
        if type_params and (actual in type_params):
            self.inferred_count += 1
            return True
        declared_r = self._resolve_alias(declared)
        actual_r = self._resolve_alias(actual)
        # Union 标注: 任一成员兼容即通过(不二法门)
        for d in _split_union(declared_r):
            if self._compatible_one(d, actual_r, type_params):
                return True
        return False

    def _compatible_one(self, declared: str, actual: str,
                        type_params: Optional[set]) -> bool:
        """单类型兼容判定(基类级)"""
        if declared == 'Any' or actual == 'Any':
            return True
        if type_params and declared in type_params:
            return True
        # 数值互通(spec §2.1): Int <-> Float 双向宽松
        if declared in _NUMERIC_TYPES and actual in _NUMERIC_TYPES:
            return True
        # 容器/泛型: 只查基类(最小切片不查元素类型)
        return _base_type(declared) == _base_type(actual)

    # ---------- 表达式类型推断(轻量) ----------

    def _infer(self, expr: Optional['Expression'],
               env: Dict[str, str], func: Optional['FunctionDef']) -> Optional[str]:
        """推断表达式类型; None = 未知(推断处放过)"""
        if expr is None:
            return None
        if isinstance(expr, Literal):
            mapping = {'int': 'Int', 'float': 'Float', 'string': 'String',
                       'bool': 'Bool', 'none': 'None'}
            return mapping.get(expr.literal_type)
        if isinstance(expr, ListExpr):
            return 'List'
        if isinstance(expr, (DictExpr, DictCompExpr)):
            return 'Dict'
        if isinstance(expr, ListCompExpr):
            return 'List'
        if isinstance(expr, Variable):
            if expr.name in env:
                return env[expr.name]
            return None
        if isinstance(expr, UnaryOp):
            if expr.op == 'not':
                return 'Bool'
            return self._infer(expr.operand, env, func)  # -x 保留数值类型
        if isinstance(expr, BinaryOp):
            return self._infer_binary(expr, env, func)
        if isinstance(expr, CallExpr):
            return self._infer_call(expr, env, func)
        # MemberAccess/SendExpr/RecvExpr/LambdaExpr/SubscriptExpr 等: 不猜
        return None

    def _infer_binary(self, expr: 'BinaryOp',
                      env: Dict[str, str], func: Optional['FunctionDef']) -> Optional[str]:
        lt = self._infer(expr.left, env, func)
        rt = self._infer(expr.right, env, func)
        if expr.op in ('==', '!=', '<', '>', '<=', '>=', 'and', 'or'):
            return 'Bool'
        if expr.op in ('+', '-', '*', '/', '%'):
            if lt is None or rt is None:
                return None
            if lt == rt and lt in ('Int', 'Float', 'String', 'List'):
                return lt
            if lt in _NUMERIC_TYPES and rt in _NUMERIC_TYPES:
                return 'Float'  # 混合运算提升为 Float
            return None
        return None

    def _call_target_name(self, expr: 'CallExpr') -> Optional[str]:
        """取调用目标名: 裸函数名(str 或 Variable 节点)才返回; 成员访问/表达式返回 None"""
        f = expr.func
        if isinstance(f, str):
            return f
        if isinstance(f, Variable):
            return f.name
        return None

    def _infer_call(self, expr: 'CallExpr',
                    env: Dict[str, str], func: Optional['FunctionDef']) -> Optional[str]:
        name = self._call_target_name(expr)
        if name is None:
            return None  # 函数位是表达式(如高阶函数传参调用), 不猜
        # 内置白名单
        if name in _BUILTIN_RETURN_TYPES:
            return _BUILTIN_RETURN_TYPES[name]
        # 本模块函数: 用其返回标注(无标注 = 放过)
        if '.' not in name and name in self.ast.functions:
            target = self.ast.functions[name]
            return target.return_type if target.return_type else None
        return None

    # ---------- 表达式检查(实参 vs 形参标注) ----------

    def _check_expr(self, expr: Optional['Expression'],
                    env: Dict[str, str], func: Optional['FunctionDef']) -> None:
        if expr is None:
            return
        if isinstance(expr, CallExpr):
            self._check_call_args(expr, env, func)
        # 通用递归: dataclass 字段里的子表达式/子语句自动覆盖
        for value in vars(expr).values():
            self._recurse_value(value, env, func)

    def _check_call_args(self, expr: 'CallExpr',
                         env: Dict[str, str], func: Optional['FunctionDef']) -> None:
        name = self._call_target_name(expr)
        if name is None or '.' in name or name not in self.ast.functions:
            return  # 只查本模块函数调用(裸名)
        target = self.ast.functions[name]
        tp_set = set(target.type_params)
        for i, arg in enumerate(expr.args):
            if i >= len(target.params):
                break  # 参数个数错误归语法/运行层, 不属类型检查
            param_name, param_type, _default = target.params[i]
            if param_type == 'Any' or param_type is None:
                self.inferred_count += 1
                continue
            actual = self._infer(arg, env, func)
            if actual is None:
                self.inferred_count += 1
                continue
            self.checked_count += 1
            if not self._compatible(param_type, actual, tp_set):
                self.errors.append(
                    f"{self.code_name}: 调用 {name}() 第 {i + 1} 个参数"
                    f"({param_name}) 标注为 {param_type}, 实际推断为 {actual}")

    # ---------- 语句检查 ----------

    def _check_stmt(self, stmt, env: Dict[str, str],
                    func: Optional['FunctionDef']) -> None:
        if isinstance(stmt, VariableDecl):
            if stmt.var_type is not None and stmt.value is not None:
                actual = self._infer(stmt.value, env, func)
                self.checked_count += 1
                if not self._compatible(stmt.var_type, actual):
                    shown = actual if actual is not None else "未知"
                    self.errors.append(
                        f"{self.code_name}:{stmt.line}: 变量 {stmt.name} 声明标注"
                        f"{stmt.var_type}, 实际推断为 {shown}")
                env[stmt.name] = stmt.var_type  # 标注入环境, 供后续引用
            else:
                self.inferred_count += 1
                if stmt.value is not None:
                    inferred = self._infer(stmt.value, env, func)
                    if inferred is not None and stmt.name not in env:
                        env[stmt.name] = inferred  # 无标注声明也进环境(推断值)
            self._check_expr(stmt.value, env, func)
            return
        if isinstance(stmt, ReturnStmt):
            if func is not None and func.return_type is not None:
                actual = self._infer(stmt.value, env, func)
                self.checked_count += 1
                if not self._compatible(func.return_type, actual, set(func.type_params)):
                    shown = actual if actual is not None else "未知"
                    self.errors.append(
                        f"{self.code_name}:{stmt.line}: 函数 {func.name} 返回标注"
                        f"{func.return_type}, 实际推断为 {shown}")
            elif stmt.value is not None:
                self.inferred_count += 1
            self._check_expr(stmt.value, env, func)
            return
        # 通用递归: 语句体内的子语句/子表达式自动覆盖
        # (If/While/For/Try/With/Defer/Scope 等, 新语句类型零成本受益)
        for value in vars(stmt).values():
            self._recurse_value(value, env, func)

    # ---------- 通用递归 ----------

    def _recurse_value(self, value, env: Dict[str, str],
                       func: Optional['FunctionDef']) -> None:
        if isinstance(value, ASTNode):
            if isinstance(value, Expression):
                self._check_expr(value, env, func)
            else:
                # 语句: 分支体复制环境(分支内声明不污染外层)
                self._check_stmt(value, dict(env), func)
        elif isinstance(value, (list, tuple)):
            for item in value:
                self._recurse_value(item, env, func)

    # ---------- 主入口 ----------

    def check(self) -> List[str]:
        """执行检查, 返回错误列表(空 = 通过)"""
        # 全局语句
        for stmt in self.ast.statements:
            self._check_stmt(stmt, {}, None)
        # 函数体(参数标注入环境)
        for func in self.ast.functions.values():
            env: Dict[str, str] = {}
            tp_set = set(func.type_params)
            for name, ptype, _default in func.params:
                if ptype != 'Any' and ptype is not None and name not in tp_set:
                    env[name] = ptype
            for stmt in func.body:
                self._check_stmt(stmt, dict(env), func)
        return self.errors


def type_check_code(code: str, code_name: str) -> None:
    """--types: L1 渐进类型静态检查(mypy-lite)。

    标注处检查 + 推断处放过。通过 → 退出0; 有类型错误 → 逐条报告退出1;
    语法错误 → 退出2(类型检查以语法干净为前提)。
    """
    try:
        tokens = Lexer(code).tokenize()
        parser = Parser(tokens, code)
        ast = parser.parse()
    except SyntaxError as e:
        print(f"❌ 类型检查中止: {code_name} 存在语法错误")
        print(f"   {e}")
        sys.exit(2)
    if parser.errors:
        print(f"❌ 类型检查中止: {code_name} ({len(parser.errors)} 个语法错误)")
        for err in parser.errors:
            print(f"   • {err}")
        sys.exit(2)
    checker = TypeChecker(ast, code_name)
    errors = checker.check()
    if errors:
        print(f"❌ 类型错误: {code_name} ({len(errors)} 处)")
        for err in errors:
            print(f"   • {err}")
        sys.exit(1)
    print(f"✅ 类型检查通过: {code_name} "
          f"(标注处检查 {checker.checked_count} 处, 推断处放过 {checker.inferred_count} 处)")
    sys.exit(0)


def check_code(code: str, code_name: str) -> None:
    """--check: 只解析不执行。

    语法干净 → 退出0; 有错误 → 逐条报告并退出2。
    治文件模式的宽松执行假通过(语法错误只警告仍退出0)。
    """
    try:
        tokens = Lexer(code).tokenize()
        parser = Parser(tokens, code)
        parser.parse()
    except SyntaxError as e:
        print(f"❌ 语法错误: {code_name}")
        print(f"   {e}")
        sys.exit(2)
    if parser.errors:
        print(f"❌ 语法错误: {code_name} ({len(parser.errors)} 个)")
        for err in parser.errors:
            print(f"   • {err}")
        sys.exit(2)
    print(f"✅ 语法检查通过: {code_name}")
    sys.exit(0)

def emit_analysis(code: str, kind: str, out_path: str, code_name: str) -> None:
    """--emit: 将词法/语法分析结果写入文件"""
    try:
        tokens = Lexer(code).tokenize()
        parser = Parser(tokens, code)
        ast = parser.parse()
    except SyntaxError as e:
        print(f"❌ 无法分析 {code_name}: {e}")
        sys.exit(2)
    lines = []
    if kind == 'tokens':
        for i, tok in enumerate(tokens):
            lines.append(f"{i:4d}: {tok}")
    elif kind == 'ast':
        for func in ast.functions.values():
            lines.append(f"函数: {func.name}")
            if func.params:
                params = ", ".join(f"{p[0]}: {p[1]}" for p in func.params)
                lines.append(f"  参数: {params}")
            if func.return_type:
                lines.append(f"  返回类型: {func.return_type}")
            if func.requires:
                lines.append(f"  前置条件: {len(func.requires)} 条")
            if func.ensures:
                lines.append(f"  后置条件: {len(func.ensures)} 条")
            lines.append(f"  语句数: {len(func.body)}")
        lines.append(f"全局语句数: {len(ast.statements)}")
        if parser.errors:
            lines.append(f"解析错误: {len(parser.errors)} 个")
            for err in parser.errors:
                lines.append(f"  • {err}")
    else:
        print(f"❌ 未知的 --emit 类型: {kind}(支持 tokens/ast)")
        sys.exit(2)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    print(f"✅ 已写入 {out_path} ({len(lines)} 行)")

# ==================== P0.2 测试框架 ====================

def collect_test_files(path: str) -> List[str]:
    """收集测试文件: 目录下所有不以 _ 开头的 .intent 文件

    _ 开头的文件是演示/草稿,不参与测试运行。
    """
    if os.path.isfile(path):
        return [path]
    if not os.path.isdir(path):
        print(f"❌ 测试路径不存在: {path}")
        sys.exit(2)
    files = []
    for root, _dirs, names in os.walk(path):
        for name in names:
            if name.endswith('.intent') and not name.startswith('_'):
                files.append(os.path.join(root, name))
    return sorted(files)

def run_postmortem(code: str, code_name: str):
    """EX2: 事后调试 — 崩溃即存档, 停机后进场检视

    执行程序; 一旦抛出错误:
      1. 渲染完整诊断(D3: 消息 + 源码行 + Intent 调用链)
      2. 帧快照链写盘 .intent_postmortem.json(跨进程可捡回)
      3. 打印帧检视(每帧: 函数/位置/局部变量)
      4. 进入 (intent-pm) 命令循环; stdin EOF(非交互)自动收尾
    正常结束则报告无事可检。退出码 0 — postmortem 的职责是
    接住崩溃, 不是复制失败(崩溃的退出码在存档里, 不在进程上)。
    """
    interpreter = Interpreter()
    interpreter._set_source(code)
    interpreter.current_filename = code_name
    file_dir = os.path.dirname(os.path.abspath(code_name)) if code_name != "<-c>" else "."
    interpreter.add_module_search_path(file_dir)
    pm = Postmortem(interpreter)
    try:
        lexer = Lexer(code, code_name)
        tokens = lexer.tokenize()
        parser = Parser(tokens, code)
        program = parser.parse()
        if parser.errors:
            print(f"❌ 语法错误, 无法进入事后调试: {parser.errors[0]}")
            sys.exit(2)
        interpreter.execute_program(program)
        print("✅ 程序正常结束, 无事可检(没有崩溃)")
        sys.exit(0)
    except DebuggerQuit:
        print("[事后调试] 会话结束 (quit)")
    except Exception as e:
        err = wrap_intent_error(e, interpreter)
        print()
        print(render_intent_error(err, interpreter))
        frames = getattr(e, '_intent_frames', None) or []
        pm.save_snapshot(err, frames)
        # 默认停在出错帧(最内层) — 事后调试第一眼要看见的是崩溃现场
        pm.current = max(0, len(frames) - 1)
        pm.show_frames(frames)
        try:
            pm.command_loop(frames)
        except DebuggerQuit:
            print("[事后调试] 会话结束 (quit)")
    sys.exit(0)


def run_debug(code: str, code_name: str):
    """C7: 调试模式执行 — 断点/单步/变量检视/调用栈

    非交互(stdin EOF/管道)时命令循环自动放行, 程序跑完 exit 0 —
    与普通执行的唯一差别是 banner 与断点位置信息。
    quit 命令抛 DebuggerQuit 至此收尾, 同样 exit 0。
    """
    interpreter = Interpreter()
    interpreter._set_source(code)
    interpreter.current_filename = code_name
    file_dir = os.path.dirname(os.path.abspath(code_name)) if code_name != "<-c>" else "."
    interpreter.add_module_search_path(file_dir)
    dbg = Debugger(interpreter)
    interpreter.debugger = dbg
    dbg.show_banner()
    try:
        lexer = Lexer(code, code_name)
        tokens = lexer.tokenize()
        parser = Parser(tokens, code)
        program = parser.parse()
        if parser.errors:
            print(f"❌ 语法错误, 无法调试: {parser.errors[0]}")
            sys.exit(2)
        # 启动即暂停在起点(pdb 风格) — 否则断点未设, 程序一泻千里
        print(f"🛑 起点 {code_name}  (输入 break N 设断点, help 查看命令)")
        dbg.command_loop()
        interpreter.execute_program(program)
    except DebuggerQuit:
        print("[调试器] 会话结束 (quit)")
    sys.exit(0)


def run_tests(path: str):
    """P0.2 测试框架: 发现并执行 test_* 函数

    约定: 测试文件中 def test_xxx() 函数即测试用例;
    每个测试文件用独立 Interpreter 执行,测试间状态隔离。
    断言用内置 assert(condition, message)。
    """
    files = collect_test_files(path)
    if not files:
        print(f"❌ 在 {path} 下没有找到测试文件(*.intent, _ 开头的文件被跳过)")
        sys.exit(2)

    total = passed = skipped = 0
    failures = []  # (rel_path, test_name, IntentError, interpreter)
    t0 = time.time()

    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            code = f.read()
        # 每个文件独立解释器 — 测试间状态隔离
        interp = Interpreter()
        interp._set_source(code)
        interp.current_filename = fpath
        # P2.1: 测试文件所在目录加入模块搜索路径(lib/ 相对测试文件解析)
        interp.add_module_search_path(os.path.dirname(os.path.abspath(fpath)))
        rel = os.path.relpath(fpath, path)
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens, code)
            ast = parser.parse()
            if parser.errors:
                raise SyntaxError(f"{len(parser.errors)} 个语法错误,首个: {parser.errors[0]}")
            interp.execute_program(ast)
        except Exception as e:
            err = wrap_intent_error(e, interp)
            total += 1
            failures.append((rel, '<模块加载>', err, interp))
            print(f"  ❌ {rel} :: <模块加载>")
            continue
        # 执行所有 test_* 函数; 无测试函数的文件是库文件, 静默跳过
        test_names = sorted(n for n in interp.functions if n.startswith('test_'))
        # TQ1: fixture 约定 — setup 每个用例前跑, teardown 每个用例后跑
        # (用例失败/skip 也要清理; teardown 自身失败即用例失败)
        setup_fn = interp.functions.get('setup')
        teardown_fn = interp.functions.get('teardown')
        for tname in test_names:
            total += 1
            teardown_done = False
            try:
                if setup_fn is not None:
                    interp.execute_function(setup_fn, [])
                interp.execute_function(interp.functions[tname], [])
                if teardown_fn is not None:
                    interp.execute_function(teardown_fn, [])
                    teardown_done = True
                passed += 1
                print(f"  ✅ {rel} :: {tname}")
            except SkipTest as sk:
                # TQ1: skip(reason) — 既非通过也非失败, 单独计数
                skipped += 1
                if teardown_fn is not None and not teardown_done:
                    try:
                        interp.execute_function(teardown_fn, [])
                    except Exception:
                        pass
                reason = f" ({sk})" if str(sk) else ""
                print(f"  ⏭️  {rel} :: {tname}{reason}")
            except Exception as e:
                if teardown_fn is not None and not teardown_done:
                    try:
                        interp.execute_function(teardown_fn, [])
                    except Exception:
                        pass
                err = wrap_intent_error(e, interp)
                failures.append((rel, tname, err, interp))
                print(f"  ❌ {rel} :: {tname}")

    elapsed = time.time() - t0
    print()
    print("=" * 56)
    summary = f"  测试结果: {passed}/{total} 通过, {total - passed - skipped} 失败"
    if skipped:
        summary += f", {skipped} 跳过"
    print(summary + f" ({elapsed:.2f}s)")
    print("=" * 56)
    # 失败详情统一渲染 — 复用 P0.1 的错误诊断
    for rel, tname, err, interp in failures:
        print()
        print(f"── {rel} :: {tname} ──")
        print(render_intent_error(err, interp))
    sys.exit(1 if failures else 0)

# ==================== 程序入口 ====================
if __name__ == '__main__':
    # 单文件入口 + 辅助模块(intent_bytecode 等)的经典坑:
    # 本文件以 __main__ 运行时, 辅助模块的 from mini_intent import ...
    # 会重新加载一份 mini_intent → 两套类定义 → isinstance 全部失效。
    # 把 __main__ 注册为 sys.modules['mini_intent'], 保证类身份唯一。
    import sys as _sys
    _sys.modules['mini_intent'] = _sys.modules['__main__']
    # banner 只在交互终端显示 — 重定向到文件时保持输出纯净
    if sys.stdout.isatty():
        print(f"""
╔═══════════════════════════════════════════════════════╗
║              Intent 语言解释器 v{VERSION}              ║
║         {PHILOSOPHY_SLOGAN}                ║
╚═══════════════════════════════════════════════════════╝
    """)
    main()