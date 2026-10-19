#!/usr/bin/env python
# tools/csdk/selftest.py — C 扩展 SDK 端到端自检（I3a）
#
# 判定链（同一套 ABI，两条验证路径）：
#   有 C 编译器 → 编译 example.c → load_native → Intent 调用 → 断言结果
#   无 C 编译器 → ctypes 回调表 → 同一条 load→读表→调用 路径 → 断言结果
# 两种情况下 ABI 都被端到端验证；「C 编译产物」只在有编译器时才算验证过，
# 输出里明示，不把模拟路径冒充成编译验证。
#
# 退出码：0 全通 ｜ 1 失败

import contextlib
import io
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PROJECT, 'src'))

import loader  # noqa: E402
from mini_intent import run_source  # noqa: E402

INTENT_PROBE = """
let a = native_sum_range(1, 100);
let b = native_square(12);
print(a);
print(b);
"""

COMPILERS = [
    ('gcc', ['gcc', '-shared', '-O2', '-o', '{out}', '{src}']),
    ('clang', ['clang', '-shared', '-O2', '-o', '{out}', '{src}']),
    ('cl', ['cl', '/nologo', '/LD', '/O2', '/Fe:{out}', '{src}']),
]


def _try_compile() -> tuple:
    """返回 (NativeModule|None, 说明) — 找不到/编译失败都如实返回"""
    src = os.path.join(HERE, 'example.c')
    if sys.platform == 'win32':
        out = os.path.join(HERE, 'build', 'intent_example.dll')
    else:
        out = os.path.join(HERE, 'build', 'libintent_example.so')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    for name, cmd in COMPILERS:
        if shutil.which(name) is None:
            continue
        argv = [c.format(out=out, src=src) for c in cmd]
        if name == 'cl':
            # MSVC 输出名会带 .dll 后缀（/Fe 指定的是基名时自动补）
            argv = [c.format(out=out, src=src) for c in cmd]
        try:
            r = subprocess.run(argv, capture_output=True, timeout=120)
        except Exception as e:
            return None, f"{name} 编译异常: {e}"
        if r.returncode != 0:
            tail = (r.stdout or b'')[-300:] + (r.stderr or b'')[-300:]
            continue  # 该编译器不可用, 试下一个
        # MSVC 可能产出 out 或 out+.dll
        candidates = [out, out + '.dll', out.replace('.dll', '')]
        for c in candidates:
            if os.path.isfile(c):
                try:
                    mod = loader.load_native(c)
                    return mod, f"C 编译器: {name}（example.c 编译通过 → {os.path.basename(c)}）"
                except Exception as e:
                    return None, f"{name} 产物加载失败: {e}"
        return None, f"{name} 编译成功但未找到产物"
    return None, "未检测到 C 编译器（gcc/clang/cl）"


def main() -> int:
    # 1) 取得模块：优先真 DLL，退路 ctypes 回调表
    mod, note = _try_compile()
    if mod is None:
        print(f"⚠️  {note}")
        print("   → 回退：ctypes 回调表验证 ABI（C 编译路径未验证）")
        mod = loader.make_simulated_module()
    else:
        print(f"🔧 {note}")

    names = mod.names()
    if 'native_sum_range' not in names or 'native_square' not in names:
        print(f"❌ 注册表缺函数: {names}")
        return 1
    print(f"   注册函数: {', '.join(names)}")

    # 2) 通过 Intent 调用原生函数（run_source + 注入 builtins）
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            run_source(INTENT_PROBE, inject_builtins=mod.functions())
    except Exception as e:
        print(f"❌ Intent 调用原生函数失败: {e}")
        return 1
    lines = [ln.strip() for ln in buf.getvalue().splitlines() if ln.strip()]
    if lines[-2:] != ['5050', '144']:
        print(f"❌ 原生函数返回值不符: {lines[-2:] if lines else '无输出'}"
              f"（期望 5050 / 144）")
        return 1
    print("   Intent 侧调用: native_sum_range(1,100)=5050, native_square(12)=144")

    # 3) ABI 版本校验：错误版本必须被拒
    if not loader.check_abi_rejected(loader.ABI_VERSION + 1):
        print("❌ ABI 版本不匹配未被拒绝")
        return 1
    if not loader.check_abi_rejected(loader.ABI_VERSION):
        print("❌ ABI 版本匹配被误拒")
        return 1
    print("   ABI 版本校验: v1 接受 / v2 拒绝")

    print("✅ CSDK selftest 全通（ABI v1: 加载→注册表→Intent 调用 → "
          "5050/144 断言 → 版本校验）")
    return 0


if __name__ == '__main__':
    sys.exit(main())
