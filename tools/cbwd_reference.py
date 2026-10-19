#!/usr/bin/env python3
"""tools/cbwd_reference.py — CBWD 洞口合并算法参考 + 对齐校验（BD4）

参考内核提取自 D:\\Desktop\\CBWD\\COM.py（洞口合并工具）的纯算法部分:
  bbox_3d_gap_mm / can_merge_openings / _cells_covered /
  _find_merge_groups_slow / find_merge_groups(连通分量 + 空间哈希预筛)
剥掉 Revit API / WinForms / 几何分析(analyze_opening_geometry)依赖 —
本工具只承载「哪些洞口该合并」的分组逻辑。

单位口径: COM.py 原几何为 ft(Revit 内部), 距离乘 304.8 得 mm。
本提取统一 mm 原生(网格边长阈值 0.5ft ≡ 152.4mm 等价换算) —
与 Intent 移植(std/bim/cbwd.intent)同输入同口径, 逐例对照。

用法:
  python tools/cbwd_reference.py --selftest   固定用例自检
  python tools/cbwd_reference.py --parity     合成数据: Python 参考 vs Intent 移植
"""

import math
import os
import random
import sys

# ── 参考内核（COM.py 算法部分的 mm 原生提取）──────────────

def bbox_3d_gap_mm(b1, b2):
    """COM.py bbox_3d_gap_mm 的 mm 原生版(原: ft 几何 * 304.8)"""
    dx = max(0, b1['min'][0] - b2['max'][0], b2['min'][0] - b1['max'][0])
    dy = max(0, b1['min'][1] - b2['max'][1], b2['min'][1] - b1['max'][1])
    dz = max(0, b1['min'][2] - b2['max'][2], b2['min'][2] - b1['max'][2])
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def can_merge_openings(f1, f2, max_distance=150):
    """COM.py can_merge_openings 的 mm 原生版

    洞口 dict: {'bounding_box': {'min': (x,y,z), 'max': (...)},
                'is_cylindrical': bool, 'radius': float, 'center_point': (x,y,z)}
    (COM.py 里这些由 cached_analyze 从 Revit 几何得出 — 参考版由输入直给)
    """
    gap = bbox_3d_gap_mm(f1['bounding_box'], f2['bounding_box'])
    if gap > max_distance:
        return False
    if f1['is_cylindrical'] and f2['is_cylindrical']:
        r1, r2 = f1['radius'], f2['radius']
        if r1 > 0 and r2 > 0:
            c1, c2 = f1['center_point'], f2['center_point']
            center_dist = math.dist(c1, c2)
            surface_gap = center_dist - (r1 + r2)
            if surface_gap > max_distance:
                return False
    return True


def _cells_covered(min_pt, max_pt, cell):
    ix0 = int(math.floor(min_pt[0] / cell)); ix1 = int(math.floor(max_pt[0] / cell))
    iy0 = int(math.floor(min_pt[1] / cell)); iy1 = int(math.floor(max_pt[1] / cell))
    iz0 = int(math.floor(min_pt[2] / cell)); iz1 = int(math.floor(max_pt[2] / cell))
    for ix in range(ix0, ix1 + 1):
        for iy in range(iy0, iy1 + 1):
            for iz in range(iz0, iz1 + 1):
                yield (ix, iy, iz)


def _find_merge_groups_slow(families, max_distance=150):
    """COM.py _find_merge_groups_slow — O(n²) BFS 兜底

    与 COM.py 的刻意差异: 返回组成员**下标**而非元素对象 —
    签名比较需要稳定身份; 快路径同样返回下标, 两路径同构。
    """
    groups = []
    visited = set()
    for i, family in enumerate(families):
        if i in visited:
            continue
        current_group = [i]
        visited.add(i)
        queue = [i]
        while queue:
            cur_idx = queue.pop(0)
            cur_fam = families[cur_idx]
            for j, other in enumerate(families):
                if j not in visited and can_merge_openings(cur_fam, other, max_distance):
                    current_group.append(j)
                    visited.add(j)
                    queue.append(j)
        groups.append(current_group)
    return groups


def find_merge_groups(families, max_distance=150, prefilter=True):
    """COM.py find_merge_groups — 连通分量 + 空间哈希预筛(默认路径)"""
    n = len(families)
    if n < 2:
        return [families]
    if not prefilter:
        return _find_merge_groups_slow(families, max_distance)
    cell = max_distance if max_distance > 152.4 else 152.4  # 0.5ft ≡ 152.4mm
    grid = {}
    for i, f in enumerate(families):
        b = f['bounding_box']
        for k in _cells_covered(b['min'], b['max'], cell):
            grid.setdefault(k, []).append(i)
    cands = []
    for i in range(n):
        b = families[i]['bounding_box']
        lo = (b['min'][0] - max_distance, b['min'][1] - max_distance, b['min'][2] - max_distance)
        hi = (b['max'][0] + max_distance, b['max'][1] + max_distance, b['max'][2] + max_distance)
        seen = set()
        for k in _cells_covered(lo, hi, cell):
            for j in grid.get(k, ()):
                if j != i:
                    seen.add(j)
        cands.append(sorted(seen))
    groups = []
    visited = set()
    for i in range(n):
        if i in visited:
            continue
        current_group = [i]
        visited.add(i)
        queue = [i]
        while queue:
            cur_idx = queue.pop()
            for j in cands[cur_idx]:
                if j in visited:
                    continue
                if can_merge_openings(families[cur_idx], families[j], max_distance):
                    current_group.append(j)
                    visited.add(j)
                    queue.append(j)
        groups.append(current_group)
    return groups


def groups_signature(groups):
    """组签名: 组内下标升序连字符 + 全体排序(与 Intent 移植同形态)"""
    sigs = []
    for g in groups:
        s = sorted(g)
        sigs.append('-'.join(str(x) for x in s))
    return sorted(sigs)


# ── 合成数据（确定性, 无外部种子依赖）────────────────────

def make_opening(rng, x, y, z, size=100.0, cylindrical=False, radius=50.0):
    if cylindrical:
        bb = {'min': (x - radius, y - radius, z - radius),
              'max': (x + radius, y + radius, z + radius)}
        return {'bounding_box': bb, 'is_cylindrical': True,
                'radius': radius, 'center_point': (x, y, z)}
    h = size / 2.0
    bb = {'min': (x - h, y - h, z - h), 'max': (x + h, y + h, z + h)}
    return {'bounding_box': bb, 'is_cylindrical': False,
            'radius': 0.0, 'center_point': (x, y, z)}


def synthetic_openings(n=24, seed=42):
    """确定性合成洞口: 3 个密集簇 + 散布点, 混方圆 — 分组结构丰富"""
    rng = random.Random(seed)
    openings = []
    centers = [(0.0, 0.0, 0.0), (2000.0, 0.0, 0.0), (1000.0, 1500.0, 0.0)]
    for c in centers:
        for _ in range(5):
            jx = c[0] + rng.uniform(-120, 120)
            jy = c[1] + rng.uniform(-120, 120)
            jz = c[2] + rng.uniform(-60, 60)
            openings.append(make_opening(rng, jx, jy, jz))
    for _ in range(n - 15):
        openings.append(make_opening(rng, rng.uniform(-500, 2500),
                                     rng.uniform(-500, 2000),
                                     rng.uniform(-100, 100)))
    # 第 24 个: 圆柱(表面间隙精修路径)
    openings.append(make_opening(rng, 1500.0, 1500.0, 0.0, cylindrical=True, radius=30.0))
    return openings


# ── Intent 移植调用（parity 用）──────────────────────────

_INTENT_HARNESS = """
import std.bim.cbwd;

groups_signature(find_merge_groups(openings, DIST));
"""

_INTENT_HARNESS_SLOW = """
import std.bim.cbwd;

groups_signature(find_merge_groups_slow(openings, DIST));
"""


def _intent_literal(value) -> str:
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
    if isinstance(value, (list, tuple)):
        return '[' + ', '.join(_intent_literal(v) for v in value) + ']'
    if isinstance(value, dict):
        items = ', '.join(f'{_intent_literal(k)}: {_intent_literal(v)}'
                          for k, v in value.items())
        return '{' + items + '}'
    raise TypeError(f'不支持的注入类型: {type(value).__name__}')


def _openings_to_intent_schema(openings):
    """参考 dict → Intent 移植的洞口 schema"""
    out = []
    for o in openings:
        bb = o['bounding_box']
        out.append({
            'min': list(bb['min']), 'max': list(bb['max']),
            'cylindrical': o['is_cylindrical'],
            'radius': o['radius'], 'center': list(o['center_point']),
        })
    return out


def run_intent_groups(openings, distance, slow=False):
    """跑 Intent 移植, 返回组签名(list[str])"""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(repo_root, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    old_cwd = os.getcwd()
    os.chdir(repo_root)  # std/ 按 cwd 相对查找
    try:
        import mini_intent
        code = _INTENT_HARNESS_SLOW if slow else _INTENT_HARNESS
        code = code.replace('DIST', repr(float(distance)))
        prelude = 'let openings = ' + _intent_literal(_openings_to_intent_schema(openings)) + ';\n'
        raw = mini_intent.run_source(prelude + code, filename='cbwd_parity')
        # RuntimeValue 树 → 原生
        def native(v):
            rv = getattr(mini_intent, 'RuntimeValue', None)
            if rv is not None and isinstance(v, rv):
                return native(v.value)
            if isinstance(v, list):
                return [native(x) for x in v]
            if isinstance(v, dict):
                return {k: native(x) for k, x in v.items()}
            return v
        return native(raw)
    finally:
        os.chdir(old_cwd)


# ── 自检与对齐 ───────────────────────────────────────────

def _selftest() -> int:
    passed = failed = 0

    def check(label, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f'  ✅ {label}')
        else:
            failed += 1
            print(f'  ❌ {label}')

    def rect(x, y, z, size=100.0):
        return make_opening(None, x, y, z, size=size)

    def cyl(x, y, z, r):
        return make_opening(None, x, y, z, cylindrical=True, radius=r)

    # 1. 间隙度量
    a = rect(0, 0, 0)
    b = rect(200, 0, 0)
    check('bbox_gap: x 向 200-100=100mm', abs(bbox_3d_gap_mm(a['bounding_box'], b['bounding_box']) - 100.0) < 1e-9)
    c = rect(0, 0, 0)
    d = rect(0, 0, 0)
    check('bbox_gap: 完全重合 → 0', bbox_3d_gap_mm(c['bounding_box'], d['bounding_box']) == 0.0)

    # 2. 传递链: A-B-C 间隔 100, D=150 → 一组; D=99 → 三组
    chain = [rect(0, 0, 0), rect(200, 0, 0), rect(400, 0, 0)]
    check('传递链 D=150: 3 个洞口一份',
          groups_signature(find_merge_groups(chain, 150)) == ['0-1-2'])
    check('传递链 D=99: 各自为组',
          groups_signature(find_merge_groups(chain, 99)) == ['0', '1', '2'])

    # 3. 边界相等: gap == D 合并(参考语义 gap > D 才拒)
    check('边界 D=100: gap==D 仍合并',
          groups_signature(find_merge_groups(chain, 100)) == ['0-1-2'])

    # 4. 圆柱表面间隙精修: bbox gap 197 ≤ D=200 但 surface 203.6 > 200 → 不合并
    c1 = cyl(0, 0, 0, 10)
    c2 = cyl(200, 100, 0, 10)
    check('圆柱 D=200: bbox 可合但表面间隙超限 → 不合并',
          groups_signature(find_merge_groups([c1, c2], 200)) == ['0', '1'])
    check('圆柱 D=210: 表面间隙也过 → 合并',
          groups_signature(find_merge_groups([c1, c2], 210)) == ['0-1'])

    # 5. 预筛路径 vs 慢路径一致(合成数据)
    openings = synthetic_openings()
    for dist in (80.0, 150.0, 300.0):
        fast = groups_signature(find_merge_groups(openings, dist, prefilter=True))
        slow = groups_signature(find_merge_groups(openings, dist, prefilter=False))
        check(f'参考内部 parity D={dist}: 预筛==慢路径', fast == slow)

    # 6. 边缘: 空表/单元素
    check('空表 → 1 个空组', len(find_merge_groups([], 150)) == 1)
    check('单元素 → 整体一组', len(find_merge_groups([rect(0, 0, 0)], 150)) == 1)

    print(f'\n  cbwd_reference selftest: {passed} 通过, {failed} 失败')
    return 0 if failed == 0 else 1


def _parity() -> int:
    """Python 参考 vs Intent 移植: 同输入同签名"""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(repo_root, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    openings = synthetic_openings()
    passed = failed = 0
    for dist in (80.0, 150.0, 300.0):
        for slow in (False, True):
            ref = groups_signature(
                find_merge_groups(openings, dist, prefilter=not slow))
            got = run_intent_groups(openings, dist, slow=slow)
            label = f'D={dist} {"slow" if slow else "fast"}: Intent 移植 == CBWD 参考'
            if ref == got:
                passed += 1
                print(f'  ✅ {label} ({len(ref)} 组)')
            else:
                failed += 1
                print(f'  ❌ {label}')
                print(f'     参考: {ref}')
                print(f'     移植: {got}')
    print(f'\n  cbwd parity: {passed} 通过, {failed} 失败')
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    if '--parity' in sys.argv:
        sys.exit(_parity())
    if '--selftest' in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
    print('用法: python tools/cbwd_reference.py --selftest | --parity')
