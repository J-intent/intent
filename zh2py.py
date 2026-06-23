#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zh2py - Chinese dialect to Python transpiler
Write code in Chinese keywords, transpile to Python for Dynamo

Usage:
  python zh2py.py source.zh > output.py
  python zh2py.py --demo
"""

import sys
import re

CN_MAP = {
    '否则如果': 'elif', '不是属于': 'not in', '打印格式': 'format',
    '定义': 'def', '函数': 'def', '返回': 'return',
    '如果': 'if', '否则': 'else', '循环': 'for', '当': 'while',
    '打印': 'print', '设': '', '让': '', '声明': '',
    '真': 'True', '假': 'False', '空': 'None',
    '且': 'and', '或': 'or', '非': 'not',
    '属于': 'in', '是': 'is', '不是': 'is not',
    '类': 'class', '自身': 'self',
    '尝试': 'try', '捕获': 'except', '最终': 'finally', '引发': 'raise',
    '导入': 'import', '从': 'from', '作为': 'as',
    '突破': 'break', '继续': 'continue',
    '长度': 'len', '范围': 'range', '输入': 'input',
    '整数': 'int', '浮点': 'float', '字符串': 'str',
    '列表': 'list', '字典': 'dict', '集合': 'set', '元组': 'tuple',
    '打开': 'open',
}

# sort longer first so '否则如果' matches before '否则'
CN_KEYS = sorted(CN_MAP.keys(), key=len, reverse=True)

# ensure ASCII-only output names
_NEXT_VAR = 97

def _reset():
    global _NEXT_VAR
    _NEXT_VAR = 97

def _new_name():
    global _NEXT_VAR
    n = _NEXT_VAR
    _NEXT_VAR += 1
    if n <= 122:
        return chr(n)
    return 'v' + str(n - 122)


def is_cn(c):
    return ord(c) > 127 or c.isalpha()


def transpile(code, obfuscate=True):
    _reset()

    # step 1: replace keywords (tokenize-aware, skip strings/comments)
    out = []
    i = 0
    while i < len(code):
        c = code[i]
        # skip strings
        if c in ("'", '"'):
            j = i + 1
            while j < len(code):
                if code[j] == '\\':
                    j += 2
                    continue
                if code[j] == c:
                    # check triple quote
                    if j+2 < len(code) and code[j:j+3] == c*3:
                        end = code.find(c*3, j+3)
                        j = end + 3 if end != -1 else len(code)
                        break
                    j += 1
                    break
                j += 1
            out.append(code[i:j])
            i = j
            continue
        # skip line comments (# and //)
        if c == '#':
            j = code.find('\n', i)
            out.append('#' + code[i+1:j] if j != -1 else code[i:])
            i = j if j != -1 else len(code)
            continue
        if c == '/' and i + 1 < len(code) and code[i + 1] == '/':
            j = code.find('\n', i)
            out.append('#' + code[i+2:j] if j != -1 else '#' + code[i+2:])
            i = j if j != -1 else len(code)
            continue
        # identifiers / Chinese words
        if is_cn(c):
            j = i
            while j < len(code) and (code[j].isalnum() or is_cn(code[j]) or code[j] == '_'):
                j += 1
            word = code[i:j]
            matched = False
            for kw in CN_KEYS:
                if word == kw:
                    repl = CN_MAP[kw]
                    if repl != '':
                        out.append(repl)
                    matched = True
                    break
            if not matched:
                out.append(word)
            i = j
            continue
        out.append(c)
        i += 1
    code = ''.join(out)

    # step 2: mangle Chinese variable/function names to single letters
    # Find all Chinese names defined in the code (after def/class/assignment)
    defined = set()
    for m in re.finditer(r'\bdef\s+(\S+?)(?:\(|:)', code):
        defined.add(m.group(1))
    for m in re.finditer(r'\bclass\s+(\S+?)(?:\(|:|<)', code):
        defined.add(m.group(1))
    # Also find variable names: anything before = that looks like an identifier
    for m in re.finditer(r'(?:^|\s)(\S+?)\s*=', code, re.MULTILINE):
        name = m.group(1)
        if any(ord(ch) > 127 for ch in name):
            defined.add(name)

    cn_names = [n for n in defined if any(ord(ch) > 127 for ch in n)]
    vmap = {}
    for n in sorted(cn_names):
        vmap[n] = _new_name()

    # Replace names: tokenize and substitute
    result = []
    i = 0
    while i < len(code):
        # skip strings and comments
        if code[i] in ("'", '"'):
            j = i + 1
            while j < len(code):
                if code[j] == '\\':
                    j += 2; continue
                if code[j] == code[i]:
                    if j+2 < len(code) and code[j:j+3] == code[i]*3:
                        end = code.find(code[i]*3, j+3)
                        j = end + 3 if end != -1 else len(code)
                        break
                    j += 1; break
                j += 1
            result.append(code[i:j])
            i = j
            continue
        if code[i] == '#':
            j = code.find('\n', i)
            result.append(code[i:j] if j != -1 else code[i:])
            i = j if j != -1 else len(code)
            continue
        # identifiers
        if is_cn(code[i]):
            j = i
            while j < len(code) and (code[j].isalnum() or is_cn(code[j]) or code[j] == '_'):
                j += 1
            word = code[i:j]
            result.append(vmap.get(word, word))
            i = j
            continue
        result.append(code[i])
        i += 1

    code = ''.join(result)

    # step 3: clean up whitespace artifacts from keyword removal
    cleaned = []
    for line in code.split('\n'):
        # fix leading whitespace: if indent is weird (not multiple of 4),
        # it's likely leftover from keyword removal
        raw = line.lstrip()
        indent = len(line) - len(raw)
        if indent > 0 and indent % 4 != 0 and raw:
            # round down to nearest multiple of 4
            fixed = (indent // 4) * 4
            cleaned.append(' ' * fixed + raw)
        else:
            cleaned.append(line)
    code = '\n'.join(cleaned)

    # step 4: strip pure-comment lines
    if obfuscate:
        lines = [l for l in code.split('\n') if not l.strip().startswith('#')]
        code = '\n'.join(lines)

    return code


DEMO_SRC = """定义 main():
    设 arr = [1, 2, 3, 4, 5]
    设 total = 0
    循环 x 属于 arr:
        如果 x > 2:
            打印("big:", x)
            total = total + x
        否则:
            打印("small:", x)
    返回 total

打印("result:", main())
"""


def demo():
    print("=" * 50)
    print("zh2py - Chinese Dialect -> Python")
    print("=" * 50)

    print("\n[Source (Chinese)]")
    print("-" * 50)
    print(DEMO_SRC.strip())

    readable = transpile(DEMO_SRC, obfuscate=False)
    print("\n[Transpiled (readable Python)]")
    print("-" * 50)
    print(readable.strip())

    obf = transpile(DEMO_SRC, obfuscate=True)
    print("\n[Transpiled (obfuscated, Dynamo-ready)]")
    print("-" * 50)
    print(obf.strip())

    print("\n[Run result]")
    print("-" * 50)
    exec(compile(readable, '<demo>', 'exec'))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        demo()
    elif len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as f:
            print(transpile(f.read(), obfuscate='--readable' not in sys.argv))
    else:
        demo()
