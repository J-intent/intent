# -*- coding: utf-8 -*-
with open(r'C:\Users\阿J\intent\src\mini_intent.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'def parse_function_def' in line:
        print(f"行 {i}: {line.rstrip()}")
