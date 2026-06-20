#!/usr/bin/env python3
"""
Intent Resolver — 语义分析遍 (基于 Crafting Interpreters Ch 11)
心学为体：变量如念头，需知其所从来

在解释执行之前，静态遍历 AST，为每个变量引用标注它所属的作用域深度。
这是修复闭包 Bug 的关键组件。
"""

from enum import Enum, auto
from typing import List, Dict, Optional, Any


class FunctionType(Enum):
    """函数类型"""
    NONE = auto()
    FUNCTION = auto()
    METHOD = auto()
    INITIALIZER = auto()


class ClassType(Enum):
    """类类型"""
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver:
    """语义分析器 — 解析变量绑定，标注作用域深度
    
    在解释执行之前静态遍历 AST，维护一个作用域栈。
    每个作用域是一个 Dict[str, bool]：
      - key: 变量名
      - value: False="已声明但未完成初始化", True="已定义可用"
    
    当遇到变量引用时，从作用域栈中查找该变量属于第几层，
    然后将 (表达式, 深度) 存入 interpreter.locals。
    """
    
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes: List[Dict[str, bool]] = []       # 作用域栈
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE
        self.errors: List[str] = []
    
    # ── 入口 ─────────────────────────────────────────────
    
    def resolve_program(self, program) -> None:
        """解析整个程序"""
        # 解析所有函数定义（函数体内部的变量引用）
        for func in program.functions.values():
            self._resolve_function(func)
        # 解析顶层语句
        for stmt in program.statements:
            self._resolve_stmt(stmt)
    
    def resolve_statements(self, statements: List) -> None:
        for stmt in statements:
            self._resolve_stmt(stmt)
    
    # ── 作用域管理 ──────────────────────────────────────
    
    def _begin_scope(self) -> None:
        self.scopes.append({})
    
    def _end_scope(self) -> None:
        self.scopes.pop()
    
    def _declare(self, name: str) -> None:
        """在当前作用域声明变量（标记为未完成初始化）"""
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name in scope:
            self._error(f"变量 '{name}' 已在此作用域中声明")
        scope[name] = False  # False = 已声明但尚未完成初始化
    
    def _define(self, name: str) -> None:
        """标记变量已完成初始化，可以使用"""
        if not self.scopes:
            return
        self.scopes[-1][name] = True
    
    def _resolve_local(self, expr, name: str) -> None:
        """在作用域栈中查找变量，将深度存入 interpreter"""
        for i in range(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[i]:
                depth = len(self.scopes) - 1 - i
                self.interpreter.resolve(expr, depth)
                return
        # 未找到 → 全局变量，不需要存 depth
    
    # ── 错误报告 ───────────────────────────────────────
    
    def _error(self, message: str) -> None:
        self.errors.append(message)
        print(f"⚠️  [Resolver] {message}")
    
    # ── 语句解析 ───────────────────────────────────────
    
    def _resolve_stmt(self, stmt) -> None:
        """分发语句"""
        from mini_intent import (
            VariableDecl, Assignment, ReturnStmt, PrintStmt,
            IfStmt, WhileStmt, ForStmt, BreakStmt, ContinueStmt,
            ImportStmt, ExportStmt, Expression, FunctionDef, Program
        )
        
        if isinstance(stmt, Program):
            self.resolve_program(stmt)
        
        elif isinstance(stmt, FunctionDef):
            self._resolve_function(stmt)
        
        elif isinstance(stmt, VariableDecl):
            self._resolve_variable_decl(stmt)
        
        elif isinstance(stmt, Assignment):
            self._resolve_assignment(stmt)
        
        elif isinstance(stmt, ReturnStmt):
            self._resolve_return(stmt)
        
        elif isinstance(stmt, PrintStmt):
            self._resolve_print(stmt)
        
        elif isinstance(stmt, IfStmt):
            self._resolve_if(stmt)
        
        elif isinstance(stmt, WhileStmt):
            self._resolve_while(stmt)
        
        elif isinstance(stmt, ForStmt):
            self._resolve_for(stmt)
        
        elif isinstance(stmt, BreakStmt):
            pass  # 无变量
        
        elif isinstance(stmt, ContinueStmt):
            pass  # 无变量
        
        elif isinstance(stmt, ImportStmt):
            # import 语句不引入新变量绑定（模块引用在运行时处理）
            pass
        
        elif isinstance(stmt, ExportStmt):
            pass
        
        elif isinstance(stmt, Expression):
            self._resolve_expr(stmt)
        
        else:
            # 未知语句类型，跳过（可能来自模块或其他扩展）
            pass
    
    # ── 语句处理 ───────────────────────────────────────
    
    def _resolve_function(self, func) -> None:
        """解析函数定义 — 核心方法"""
        # 声明并定义函数名（在当前作用域）
        self._declare(func.name)
        self._define(func.name)
        
        # 进入函数作用域
        enclosing_function = self.current_function
        self.current_function = FunctionType.FUNCTION
        
        self._begin_scope()
        
        # 声明参数
        for param_name, _ in func.params:
            self._declare(param_name)
            self._define(param_name)
        
        # 解析函数体
        for stmt in func.body:
            self._resolve_stmt(stmt)
        
        # 解析契约表达式中的变量引用
        for cond in func.requires:
            self._resolve_expr(cond)
        for cond in func.ensures:
            self._resolve_expr(cond)
        
        self._end_scope()
        self.current_function = enclosing_function
    
    def _resolve_variable_decl(self, stmt) -> None:
        """解析变量声明"""
        self._declare(stmt.name)
        if stmt.value:
            self._resolve_expr(stmt.value)
        self._define(stmt.name)
    
    def _resolve_assignment(self, stmt) -> None:
        """解析赋值"""
        self._resolve_expr(stmt.value)
        self._resolve_local(stmt, stmt.target)
    
    def _resolve_return(self, stmt) -> None:
        """解析返回语句"""
        if self.current_function == FunctionType.NONE:
            self._error("不能在顶层代码中使用 '归元'")
        
        if stmt.value:
            self._resolve_expr(stmt.value)
    
    def _resolve_print(self, stmt) -> None:
        for arg in stmt.args:
            self._resolve_expr(arg)
    
    def _resolve_if(self, stmt) -> None:
        self._resolve_expr(stmt.condition)
        self._resolve_block(stmt.then_branch)
        for _, elif_body in stmt.elif_branches:
            self._resolve_block(elif_body)
        if stmt.else_branch:
            self._resolve_block(stmt.else_branch)
    
    def _resolve_while(self, stmt) -> None:
        self._resolve_expr(stmt.condition)
        self._resolve_block(stmt.body)
    
    def _resolve_for(self, stmt) -> None:
        self._begin_scope()
        if stmt.var:
            self._declare(stmt.var)
            self._define(stmt.var)
        self._resolve_expr(stmt.iterable)
        # 循环体不额外开作用域 — item 和循环体在同一作用域
        for s in stmt.body:
            self._resolve_stmt(s)
        self._end_scope()
    
    def _resolve_block(self, statements: List) -> None:
        """解析一个语句块（进入新作用域）"""
        self._begin_scope()
        for stmt in statements:
            self._resolve_stmt(stmt)
        self._end_scope()
    
    # ── 表达式解析 ─────────────────────────────────────
    
    def _resolve_expr(self, expr) -> None:
        """分发表达式"""
        from mini_intent import (
            Literal, Variable, BinaryOp, UnaryOp, CallExpr,
            MemberAccess, ListExpr, DictExpr, SubscriptExpr, PipeExpr, IfExpr,
            MatchExpr, LiteralPattern, VariablePattern, WildcardPattern, OrPattern
        )
        
        if isinstance(expr, Literal):
            pass  # 无变量
        
        elif isinstance(expr, Variable):
            self._resolve_variable_expr(expr)
        
        elif isinstance(expr, BinaryOp):
            self._resolve_expr(expr.left)
            self._resolve_expr(expr.right)
        
        elif isinstance(expr, UnaryOp):
            self._resolve_expr(expr.operand)
        
        elif isinstance(expr, CallExpr):
            # 解析被调用的函数部分
            if isinstance(expr.func, MemberAccess):
                # 模块函数调用如 std.math.add(x, y)
                self._resolve_expr(expr.func.obj)
            else:
                # 普通函数调用 — 函数名本身不需要 resolve_local
                # （它通过 self.functions 在运行时查找）
                pass
            # 解析参数
            for arg in expr.args:
                self._resolve_expr(arg)
        
        elif isinstance(expr, MemberAccess):
            self._resolve_expr(expr.obj)
        
        elif isinstance(expr, ListExpr):
            for elem in expr.elements:
                self._resolve_expr(elem)
        
        elif isinstance(expr, DictExpr):
            for key_expr, val_expr in expr.entries:
                self._resolve_expr(key_expr)
                self._resolve_expr(val_expr)
        
        elif isinstance(expr, PipeExpr):
            self._resolve_expr(expr.left)
            self._resolve_expr(expr.right)
        
        elif isinstance(expr, IfExpr):
            self._resolve_expr(expr.condition)
            self._resolve_block(expr.then_body)
            self._resolve_block(expr.else_body)
        
        elif isinstance(expr, MatchExpr):
            self._resolve_expr(expr.value)
            for case in expr.cases:
                self._resolve_pattern(case.pattern)
                if case.guard:
                    self._resolve_expr(case.guard)
                if case.body:
                    self._resolve_expr(case.body)
                else:
                    self._resolve_block(case.body_block)
    
    def _resolve_pattern(self, pattern) -> None:
        """解析匹配模式"""
        from mini_intent import LiteralPattern, VariablePattern, WildcardPattern, OrPattern
        
        if isinstance(pattern, LiteralPattern) or isinstance(pattern, WildcardPattern):
            pass
        elif isinstance(pattern, VariablePattern):
            pass  # 运行时绑定
        elif isinstance(pattern, OrPattern):
            for sub in pattern.patterns:
                self._resolve_pattern(sub)
    
    def _resolve_variable_expr(self, expr) -> None:
        """解析变量引用"""
        # 检查：变量是否被用在自身的初始化器中
        if self.scopes and self.scopes[-1].get(expr.name) is False:
            self._error(f"不能在变量 '{expr.name}' 自身的初始化器中读取它")
        
        self._resolve_local(expr, expr.name)
