#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""benchmarks/run_benchmarks.py — Intent 基准套件运行器(Q4)

用法(在 D:\\Desktop\\intent 下):
    python benchmarks/run_benchmarks.py            # 跑全部基准, 与基线对比
    python benchmarks/run_benchmarks.py --update   # 重写基线(基线变动须人工确认)
    python benchmarks/run_benchmarks.py fib        # 只跑文件名含 fib 的基准

纪律:
    - 每个基准跑 REPEAT 次取最小值(最小值抗抖动, 反映机器能力上限)
    - 与 BASELINE.md 对比, 超过 REGRESSION_THRESHOLD 判定回退并非零退出
    - 基线只来自真实运行, 不手写编造
"""
import argparse
import os
import re
import statistics
import subprocess
import sys
import time

REPEAT = 3
REGRESSION_THRESHOLD = 0.20  # 超过基线 20% 判定回退
BASELINE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BASELINE.md')
INTENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERP = os.path.join(INTENT_ROOT, 'src', 'mini_intent.py')
PYTHON = sys.executable

TIME_RE = re.compile(r'^Time:\s*(\d+(?:\.\d+)?)\s*ms\s*$', re.M)


def run_once(path: str, jit: bool = False):
    """跑一次基准, 返回 [(label, ms), ...]; label 取 Time 行前最近的非 Time 输出"""
    cmd = [PYTHON, INTERP]
    if jit:
        cmd.append('--jit')   # M3c: 热点 JIT 模式对照
    cmd.append(path)
    proc = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=300, cwd=INTENT_ROOT)
    if proc.returncode != 0:
        raise RuntimeError(f"{os.path.basename(path)} 运行失败:\n{proc.stderr}")
    lines = [ln.rstrip() for ln in proc.stdout.splitlines() if ln.strip()]
    results = []
    label = None
    for ln in lines:
        m = re.match(r'^Time:\s*(\d+(?:\.\d+)?)\s*ms$', ln.strip())
        if m:
            results.append((label or '?', float(m.group(1))))
        else:
            label = ln.strip()
    if not results:
        raise RuntimeError(f"{os.path.basename(path)} 没有输出 Time 行")
    return results


def run_benchmark(path: str, jit: bool = False):
    """跑 REPEAT 次, 每个计时点取最小值"""
    runs = [run_once(path, jit) for _ in range(REPEAT)]
    # 同一基准每次运行的计时点集合一致(确定性输出)
    labels = [lab for lab, _ in runs[0]]
    best = {}
    for lab in labels:
        vals = [ms for r in runs for l, ms in r if l == lab]
        best[lab] = min(vals)
    return best


CPY_FIB = '''
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
'''


def cpython_fib_ms(n: int = 25) -> float:
    """CPython 参考实现 fib(n) 的最优耗时(ms) — JIT 倍率的基准面"""
    ns = {}
    exec(CPY_FIB, ns)
    fib = ns['fib']
    best = None
    for _ in range(REPEAT):
        t0 = time.perf_counter()
        fib(n)
        ms = (time.perf_counter() - t0) * 1000.0
        best = ms if best is None else min(best, ms)
    return best


def load_baseline():
    """解析 BASELINE.md 的表格: | 基准 | 计时点 | 基线 ms |"""
    baseline = {}
    if not os.path.exists(BASELINE_FILE):
        return baseline
    with open(BASELINE_FILE, 'r', encoding='utf-8') as f:
        for ln in f:
            m = re.match(r'^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(\d+(?:\.\d+)?)\s*\|', ln)
            if m and m.group(1) not in ('基准', '---'):
                key = (m.group(1).strip(), m.group(2).strip())
                baseline[key] = float(m.group(3))
    return baseline


def write_baseline(all_results):
    lines = [
        '# Intent 基准基线',
        '',
        f'机器: Ryzen 7 9700X / RTX 5060 Ti / 128GB DDR5, Windows 11, Python {sys.version.split()[0]}',
        '口径: 每个基准跑 3 次取最小值(抗抖动); 单位 ms; 由 run_benchmarks.py --update 生成。',
        '',
        '| 基准 | 计时点 | 基线 ms |',
        '|---|---|---|',
    ]
    for bench, points in all_results.items():
        for label, ms in points.items():
            lines.append(f'| {bench} | {label} | {ms:.0f} |')
    lines.append('')
    with open(BASELINE_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"基线已写入 {BASELINE_FILE}")


def main():
    ap = argparse.ArgumentParser(description='Intent 基准套件运行器')
    ap.add_argument('filter', nargs='?', default='', help='只跑文件名含此字符串的基准')
    ap.add_argument('--update', action='store_true', help='重写基线(须人工确认后提交)')
    ap.add_argument('--jit', action='store_true',
                    help='M3c: 用 --jit 跑基准, 并与 CPython 参考实现比倍率(门禁 ≥0.5x)')
    args = ap.parse_args()

    bench_dir = os.path.dirname(os.path.abspath(__file__))
    files = sorted(f for f in os.listdir(bench_dir)
                   if f.endswith('.intent') and args.filter in f)
    if not files:
        print(f"benchmarks/ 下没有匹配的基准文件(filter={args.filter!r})")
        return 2

    all_results = {}
    for f in files:
        path = os.path.join(bench_dir, f)
        print(f"▶ {f} (x{REPEAT}, 取最小)")
        all_results[f] = run_benchmark(path, jit=args.jit)
        for label, ms in all_results[f].items():
            print(f"    {label:<44} {ms:>9.0f} ms")

    if args.update:
        write_baseline(all_results)
        return 0

    if args.jit:
        # M3c: JIT 相对 CPython 倍率门禁(0.5x = Intent JIT 慢不过 CPython 两倍)
        fib_ms = all_results.get('fib.intent', {}).get('fib(25) = 75025')
        if fib_ms is None:
            print("\n❌ --jit 门禁需要 fib.intent 的 fib(25) 计时点")
            return 1
        cpy_ms = cpython_fib_ms(25)
        ratio = cpy_ms / fib_ms if fib_ms > 0 else float('inf')
        print(f"\nJIT vs CPython: CPython {cpy_ms:.0f} ms / "
              f"Intent-JIT {fib_ms:.0f} ms = {ratio:.2f}x"
              f"（目标 ≥ 0.5x）")
        if ratio < 0.5:
            print("❌ JIT 未达 0.5x 目标")
            return 1
        print("✅ JIT 达到 0.5x 门槛")

    baseline = load_baseline()
    if not baseline:
        print("\n(无基线 — 先跑 --update 建立)")
        return 0

    print(f"\n与基线对比(回退阈值 +{int(REGRESSION_THRESHOLD * 100)}%):")
    regressions = 0
    for bench, points in all_results.items():
        for label, ms in points.items():
            base = baseline.get((bench, label))
            if base is None:
                print(f"    {bench} :: {label:<40} 新增计时点(无基线) {ms:.0f} ms")
                continue
            delta = (ms - base) / base
            mark = '✅' if delta <= REGRESSION_THRESHOLD else '🔴 回退'
            if delta > REGRESSION_THRESHOLD:
                regressions += 1
            print(f"    {mark} {bench} :: {label:<36} {ms:>8.0f} ms (基线 {base:.0f}, {delta:+.0%})")
    return 1 if regressions else 0


if __name__ == '__main__':
    sys.exit(main())
