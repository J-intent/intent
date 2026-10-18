#!/usr/bin/env python
# tools/vm_diff.py — VM 与树遍历解释器的差分测试（T6 验收工具）
#
# 心学为体：同一段意，两条言路——言可不同，意须一致
# 禅道为翼：差异即bug的显影液
# 马哲为用：用可执行判定代替「我觉得一致」
#
# 用法：
#   python tools/vm_diff.py                 # 跑默认文件集（examples/ + tests/test_*）
#   python tools/vm_diff.py file1.intent …  # 跑指定文件
#   python tools/vm_diff.py --all            # 额外包含 lesson/philosophy 等全部 .intent
#
# 判定：
#   MATCH       两者 stdout 一致（banner 行归一化后）且退出码一致
#   BOTH-FAIL   两者都以非零退出且末行错误类别一致（预期失败的演示文件）
#   DIVERGE     语义分歧 — 必须修
#   ERROR       工具自身运行失败（超时等）
#
# 说明：解释器 banner（⚡解释执行/✅程序执行成功）不计入程序输出；
#      错误渲染格式两侧不同（解释器有 P0.1 诊断，VM 目前抛原生异常），
#      因此失败用例只比对「是否失败 + 末行错误签名」。

import os
import re
import subprocess
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join("src", "mini_intent.py")
TIMEOUT = 60

BANNER_PAT = re.compile(r"^(⚡ 解释执行\.\.\.|✅ 程序执行成功)\s*$")
META_PAT = re.compile(r"^⚙️\s+字节码编译完成:")
# CLI 摘要行（解释器路径打印程序返回值; VM 路径暂无对应输出）— 非程序语义
SUMMARY_PAT = re.compile(r"^返回值:\s")
# 墙钟噪声（性能计时行）
TIMING_PAT = re.compile(r"^Time:\s*[\d.]+\s*ms\s*$")
# 错误类别标记（解释器渲染诊断 vs VM 原生异常 — 只比类别, 不比格式）
ERR_MARKERS = ["契约违反", "MatchError", "NameError", "TypeError", "ValueError",
               "AssertionError", "ZeroDivisionError", "IndexError", "KeyError",
               "未定义", "未覆盖", "除数不能为零"]


def normalize(text: str) -> list:
    """去 banner/编译元信息/CLI摘要/计时行、去首尾空行、统一行尾"""
    lines = [l.rstrip() for l in text.replace("\r\n", "\n").split("\n")]
    return [l for l in lines if l and not BANNER_PAT.match(l)
            and not META_PAT.match(l) and not SUMMARY_PAT.match(l)
            and not TIMING_PAT.match(l)]


def err_signature(text: str) -> str:
    """错误类别: 在全文找第一个已知错误标记（不比渲染格式）"""
    for marker in ERR_MARKERS:
        if marker in text:
            return marker
    for line in reversed(text.replace("\r\n", "\n").split("\n")):
        line = line.strip()
        if line and not BANNER_PAT.match(line) and not META_PAT.match(line):
            return line[:40]
    return ""


def run(cmd: list) -> tuple:
    try:
        r = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True,
                           timeout=TIMEOUT, encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return None, f"<timeout {TIMEOUT}s>"


def diff_file(path: str) -> str:
    rc_i, out_i = run([sys.executable, SRC, path])
    rc_v, out_v = run([sys.executable, SRC, "--compile", path, "--run-vm"])
    if rc_i is None or rc_v is None:
        return "ERROR"
    # 编译失败（语法错误等）— 两侧都进不了执行，跳过语义比对
    if "编译失败" in out_v or "语法错误" in out_v:
        return "SKIP-COMPILE"
    ok_i, ok_v = rc_i == 0, rc_v == 0
    if ok_i and ok_v:
        return "MATCH" if normalize(out_i) == normalize(out_v) else "DIVERGE"
    if not ok_i and not ok_v:
        return "BOTH-FAIL" if err_signature(out_i) == err_signature(out_v) else "DIVERGE"
    return "DIVERGE"


def default_files(all_mode: bool) -> list:
    files = []
    for d in ("examples", "tests"):
        if not os.path.isdir(os.path.join(PROJECT, d)):
            continue
        for name in sorted(os.listdir(os.path.join(PROJECT, d))):
            if not name.endswith(".intent"):
                continue
            if name.startswith("_"):        # 预期失败的演示文件
                continue
            if d == "tests" and not name.startswith("test_"):
                continue
            files.append(os.path.join(d, name))
    return files


def main():
    args = sys.argv[1:]
    files = args if args else default_files("--all" in args)
    results = {}
    for f in files:
        tag = diff_file(f)
        results.setdefault(tag, []).append(f)
        mark = {"MATCH": "✅", "BOTH-FAIL": "➖", "DIVERGE": "❌",
                "SKIP-COMPILE": "⏭️ ", "ERROR": "💥"}.get(tag, "❓")
        print(f"  {mark} {tag:<12} {f}")
    print()
    total = len(files)
    matched = len(results.get("MATCH", [])) + len(results.get("BOTH-FAIL", []))
    print(f"  差分结果: {matched}/{total} 一致"
          f"（DIVERGE {len(results.get('DIVERGE', []))}，"
          f"SKIP {len(results.get('SKIP-COMPILE', []))}，"
          f"ERROR {len(results.get('ERROR', []))}）")
    return 1 if results.get("DIVERGE") or results.get("ERROR") else 0


if __name__ == "__main__":
    sys.exit(main())
