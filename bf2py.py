#!/usr/bin/env python3
"""
Brainfuck → Python Transpiler
把 Brainfuck 转成 Python，扔进 Dynamo 没人看得懂
"""

import sys
import os

def transpile(code: str, obfuscate: bool = True) -> str:
    """
    Brainfuck → Python 转译
    obfuscate=True 时输出混淆过的代码
    """
    # 清洗：只保留 BF 指令
    clean = ''.join(c for c in code if c in '><+-.,[]')

    if obfuscate:
        return _transpile_obfuscated(clean)
    else:
        return _transpile_readable(clean)

def _transpile_obfuscated(code: str) -> str:
    """输出混淆过的 Python — 一行，变量名甲乙丙丁，适合塞进 Dynamo"""
    if not code:
        return ''

    # 生成最小化 Python：所有逻辑塞进一个函数，一行一条命令
    lines = []
    # a=tape, b=ptr, c=output, d=jump table, e=stack
    # f=loop idx, g=cmd, h=start/char
    lines.append('def j(i):')
    lines.append(' a=[0]*30000;b=0;c=[];d={};e=[]')
    lines.append(' for f,g in enumerate(i):')
    lines.append('  if g=="[":e.append(f)')
    lines.append('  if g=="]":h=e.pop();d[f]=h;d[h]=f')
    lines.append(' f=0')
    lines.append(' while f<len(i):')
    lines.append('  h=i[f]')
    lines.append('  if h==">":b+=1')
    lines.append('  if h=="<":b-=1')
    lines.append('  if h=="+":a[b]=(a[b]+1)%256')
    lines.append('  if h=="-":a[b]=(a[b]-1)%256')
    lines.append('  if h==".":c.append(chr(a[b]))')
    lines.append('  if h==",":pass')
    lines.append('  if h=="["and a[b]==0:f=d[f]')
    lines.append('  if h=="]"and a[b]!=0:f=d[f]')
    lines.append('  f+=1')
    lines.append(' return"".join(c)')

    return '\n'.join(lines)

def _transpile_readable(code: str) -> str:
    """输出可读的 Python"""
    if not code:
        return ''

    lines = []
    lines.append('# Brainfuck → Python (transpiled)')
    lines.append('def brainfuck(program: str) -> str:')
    lines.append('    tape = [0] * 30000')
    lines.append('    ptr = 0')
    lines.append('    output = []')
    lines.append('    jump = {}')
    lines.append('    stack = []')
    lines.append('')
    lines.append('    # 构建跳转表')
    lines.append('    for idx, cmd in enumerate(program):')
    lines.append('        if cmd == "[":')
    lines.append('            stack.append(idx)')
    lines.append('        elif cmd == "]":')
    lines.append('            start = stack.pop()')
    lines.append('            jump[start] = idx')
    lines.append('            jump[idx] = start')
    lines.append('')
    lines.append('    # 执行')
    lines.append('    ip = 0')
    lines.append('    while ip < len(program):')
    lines.append('        cmd = program[ip]')
    lines.append('        if cmd == ">":   ptr += 1')
    lines.append('        elif cmd == "<": ptr -= 1')
    lines.append('        elif cmd == "+": tape[ptr] = (tape[ptr] + 1) % 256')
    lines.append('        elif cmd == "-": tape[ptr] = (tape[ptr] - 1) % 256')
    lines.append('        elif cmd == ".": output.append(chr(tape[ptr]))')
    lines.append('        elif cmd == ",": pass  # input not supported')
    lines.append('        elif cmd == "[" and tape[ptr] == 0: ip = jump[ip]')
    lines.append('        elif cmd == "]" and tape[ptr] != 0: ip = jump[ip]')
    lines.append('        ip += 1')
    lines.append('')
    lines.append('    return "".join(output)')

    return '\n'.join(lines)

def run_brainfuck(program: str, stdin: str = "") -> str:
    """直接执行 Brainfuck 代码（解释器模式）"""
    tape = [0] * 30000
    ptr = 0
    output = []
    input_idx = 0
    jump = {}
    stack = []

    for idx, cmd in enumerate(program):
        if cmd == '[':
            stack.append(idx)
        elif cmd == ']':
            if not stack:
                raise SyntaxError(f"unmatched ] at {idx}")
            start = stack.pop()
            jump[start] = idx
            jump[idx] = start
    if stack:
        raise SyntaxError(f"unmatched [ at {stack[-1]}")

    ip = 0
    while ip < len(program):
        cmd = program[ip]
        if cmd == '>':
            ptr += 1
            if ptr >= len(tape):
                tape.append(0)
        elif cmd == '<':
            ptr -= 1
            if ptr < 0:
                raise RuntimeError("pointer out of bounds")
        elif cmd == '+':
            tape[ptr] = (tape[ptr] + 1) % 256
        elif cmd == '-':
            tape[ptr] = (tape[ptr] - 1) % 256
        elif cmd == '.':
            output.append(chr(tape[ptr]))
        elif cmd == ',':
            if input_idx < len(stdin):
                tape[ptr] = ord(stdin[input_idx])
                input_idx += 1
            else:
                tape[ptr] = 0
        elif cmd == '[' and tape[ptr] == 0:
            ip = jump[ip]
        elif cmd == ']' and tape[ptr] != 0:
            ip = jump[ip]
        ip += 1

    return ''.join(output)


def transpile_file(input_file: str, output_file: str = None, obfuscate: bool = True) -> str:
    """转译文件"""
    with open(input_file, 'r', encoding='utf-8') as f:
        bf_code = f.read()

    py_code = transpile(bf_code, obfuscate=obfuscate)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(py_code)
        print(f"→ 已写入 {output_file}")

    return py_code


# ── 示例 ──
EXAMPLES = {
    "Hello World": (
        "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>."
        ">---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
    ),
    "Multiply: output 3*5 as ASCII": (
        "+++>+++++[<+>-]++++++++[<++++++>-]<."
    ),
}

def demo():
    """演示"""
    print("=" * 50)
    print("Brainfuck -> Python Transpiler")
    print("=" * 50)

    for name, bf in EXAMPLES.items():
        print(f"\n== {name} ==")
        print(f"  BF ({len(bf)} chars): {bf[:60]}...")
        print(f"  run: {repr(run_brainfuck(bf))}")

        py = transpile(bf, obfuscate=True)
        print(f"  transpiled (obfuscated): {py[:100]}...")
        print(f"  size: {len(bf)} BF -> {len(py)} Python")
        print()


def repl():
    """交互式 Brainfuck REPL"""
    print("Brainfuck REPL (输入空行退出)")
    while True:
        try:
            line = input("bf> ").strip()
            if not line:
                break
            if line == '--py':
                continue
            if line.startswith('--py '):
                print(transpile(line[5:], obfuscate=True))
                continue

            result = run_brainfuck(line)
            print(f"  => {repr(result)}")
        except KeyboardInterrupt:
            print()
            break
        except Exception as e:
            print(f"  ! {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            demo()
        elif sys.argv[1] == '--repl':
            repl()
        elif sys.argv[1] == '--readable':
            # 读取 BF 文件，输出可读 Python
            if len(sys.argv) > 2:
                py = transpile_file(sys.argv[2], obfuscate=False)
                print(py)
            else:
                print("用法: bf2py.py --readable <file.bf>")
        elif sys.argv[1] == '--run':
            # 直接运行 BF 文件
            if len(sys.argv) > 2:
                with open(sys.argv[2]) as f:
                    result = run_brainfuck(f.read())
                    print(result, end='')
            else:
                print("用法: bf2py.py --run <file.bf>")
        else:
            # 默认转译文件
            py = transpile_file(sys.argv[1],
                                sys.argv[2] if len(sys.argv) > 2 else None,
                                obfuscate='--readable' not in sys.argv)
            if len(sys.argv) <= 2:
                print(py)
    else:
        demo()
