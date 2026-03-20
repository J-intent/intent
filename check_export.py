# -*- coding: utf-8 -*-
import re

# 读取文件
with open(r'C:\Users\阿J\intent\src\mini_intent.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 检查是否有ExportStmt
if 'class ExportStmt' in code:
    print("ExportStmt 类已存在")
else:
    print("ExportStmt 类不存在，需要添加")

# 检查是否有parse_export
if 'def parse_export' in code or 'parse_export_stmt' in code:
    print("parse_export 方法已存在")
else:
    print("parse_export 方法不存在，需要添加")

# 检查是否在keywords中
if "'export'" in code.lower():
    print("'export' 关键字已添加")
else:
    print("'export' 关键字需要添加")
