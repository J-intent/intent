#!/usr/bin/env python3
"""tools/pyrevit_hook.py — pyRevit 适配（BD3）

让 pyRevit 4+ 的 CPython3 模式按钮跑通 Intent 脚本。

═══ 背景 ═══

pyRevit 4.x 按钮脚本默认 CPython3 引擎(非 IronPython2): 跑在真
CPython 3.11 上, 能 import 任意纯 Python 包 — Intent 解释器
(src/mini_intent.py)正是纯 Python 零 C 依赖, import 即用。
本钩子把「选元素 → 跑 Intent 规则 → 结果回写」缩成一个调用。

═══ 按钮模板（复制进 bundle 的 script.py）═══

    import sys
    sys.path.append(r"D:\\Desktop\\intent\\tools")
    import pyrevit_hook

    INTENT_RULE = r\"""
    import std.bim.unit;
    def total_length_m(handles, props) {
        let mut total_mm = 0.0;
        for h in handles {
            total_mm = total_mm + props[h][1];
        };
        return mm_to_m(total_mm);
    };
    total_length_m(handles, props);
    \"""

    # __revit__ 是 pyRevit 注入的宿主(UIApplication); 省略 host 时
    # 钩子自动沿调用栈向上找(按钮 script.py 的全局里就有)
    pyrevit_hook.button_main(INTENT_RULE)

═══ API ═══

- get_revit_host(host=None)   → pyRevit 宿主对象(显式传入或沿栈自动找)
- get_selected_elements(host) → 选中元素列表(已经 unwrap)
- set_selection(values, host) → 把 handle/元素写回选择集
- button_main(code, host)     → 完整按钮流程: 选元素 → Intent 规则 → 原样返回
- check_intent()              → mini_intent 可导入性自检(失败给明确指引)

═══ 自检 ═══

    python tools/pyrevit_hook.py --selftest

    mock pyRevit 宿主(Selection/Document)上跑真实 Intent 规则
    (std/bim/unit 参与), 验证选择集收发 + 总长计算 + 宿主缺失报错。

═══ 边界（诚实声明）═══

- 只做 CPython3 模式; IronPython2 模式按钮请用 tools/dynamo_node.py 同款
  run_source 直跑(本钩子的 frame 自动找宿主依赖 CPython 帧对象)
- 事务(Transaction)/撤销属 BD4 CBWD 移植范围, 本钩子只读选择集
"""

import os
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))


# ── 宿主定位 ─────────────────────────────────────────────

def get_revit_host(host=None):
    """取 pyRevit 宿主(__revit__): 显式参数优先, 否则沿调用栈向上找

    pyRevit 把 __revit__ 注入按钮 script.py 的模块全局; 钩子被 import
    后自身全局没有它 — 所以向上走 3 帧找调用方的全局。找不到返回 None
    (由调用方决定是否报错)。
    """
    if host is not None:
        return host
    for depth in range(1, 4):
        try:
            frame_globals = sys._getframe(depth).f_globals
        except ValueError:
            break
        if '__revit__' in frame_globals:
            return frame_globals['__revit__']
    return None


def _host_selection(host):
    """宿主 → Selection 对象(兼容 ActiveUIDocument/uidoc/直挂三种形态)"""
    if host is None:
        raise RuntimeError(
            "pyRevit 宿主不可用(__revit__ 未定义): 本工具设计为 pyRevit "
            "CPython3 模式按钮内运行; 显式传 host=get_revit_host() 亦可")
    uidoc = getattr(host, 'ActiveUIDocument', None)
    if uidoc is None:
        uidoc = getattr(host, 'uidoc', None)
    selection = getattr(uidoc, 'Selection', None) if uidoc is not None else None
    if selection is None:
        selection = getattr(host, 'Selection', None)
    if selection is None:
        raise RuntimeError(
            f"宿主 {type(host).__name__} 上找不到 Selection "
            "(试过 ActiveUIDocument/uidoc/直挂)")
    return selection


def _host_document(host):
    """宿主 → Document 对象"""
    if host is None:
        raise RuntimeError("pyRevit 宿主不可用(__revit__ 未定义)")
    uidoc = getattr(host, 'ActiveUIDocument', None) or getattr(host, 'uidoc', None)
    doc = getattr(uidoc, 'Document', None) if uidoc is not None else None
    if doc is None:
        doc = getattr(host, 'Document', None)
    if doc is None:
        raise RuntimeError(f"宿主 {type(host).__name__} 上找不到 Document")
    return doc


# ── 选择集收发 ───────────────────────────────────────────

def get_selected_elements(host=None):
    """当前选择集 → 元素列表(经 revit_bridge.unwrap_element 解包)"""
    import revit_bridge
    selection = _host_selection(get_revit_host(host))
    doc = _host_document(get_revit_host(host))
    ids = selection.GetElementIds()
    return [revit_bridge.unwrap_element(doc.GetElement(eid)) for eid in ids]


def set_selection(values, host=None):
    """handle/元素列表 → 写回选择集(元素按原 Id, handle 经桥解出)"""
    import revit_bridge
    selection = _host_selection(get_revit_host(host))
    elements = []
    for v in values:
        if isinstance(v, revit_bridge._MockElement) or hasattr(v, 'Id'):
            elements.append(v)
        else:
            raise RuntimeError(
                f"set_selection 只接受元素或元素 Id 载体, 得到 {type(v).__name__}")
    ids = [getattr(e, 'Id', e) for e in elements]
    selection.SetElementIds(ids)
    return len(ids)


# ── Intent 执行 ──────────────────────────────────────────

def check_intent():
    """mini_intent 可导入性自检 — 返回 src 路径; 失败抛带指引的 RuntimeError"""
    repo_root = os.path.dirname(TOOLS_DIR)
    src_dir = os.path.join(repo_root, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    try:
        import mini_intent  # noqa: F401
        return src_dir
    except ImportError as e:
        raise RuntimeError(
            f"找不到 Intent 解释器({src_dir}): {e} — 请确认 D:\\\\Desktop\\\\intent "
            "仓库完整, 或修改 pyrevit_hook.py 顶部 TOOLS_DIR 推导逻辑")


def run_intent(intent_code: str, host=None, **injected):
    """跑 Intent 代码, 返回原生 Python 值(注入变量经 prelude)"""
    check_intent()
    import revit_bridge
    session = revit_bridge.RevitSession()
    return session.run(intent_code, **injected)


def button_main(intent_code: str, host=None):
    """完整按钮流程: 选元素 → send/read_props → Intent 规则 → 返回值

    返回 Intent 规则的原生结果(标量/列表/字典); 不回写选择集 —
    写回是按钮脚本自己的决定(它知道自己选了谁)。
    """
    import revit_bridge
    host = get_revit_host(host)
    session = revit_bridge.RevitSession()
    elements = get_selected_elements(host)
    handles = session.send(elements)
    props = session.read_props(handles, {"d": "DiameterMm", "l": "LengthMm"})
    rule_props = {h: [entry["d"], entry["l"]] for h, entry in props.items()}
    return session.run(intent_code, handles=handles, props=rule_props)


# ── 选管总长规则（按钮演示 + 自检共用）────────────────────

RULE_TOTAL_LENGTH_M = """
import std.bim.unit;

// 统计规则: 选中管段总长度(m) — props[handle] = [管径mm, 长度mm]
def total_length_m(handles, props) {
    let mut total_mm = 0.0;
    for h in handles {
        total_mm = total_mm + props[h][1];
    };
    return mm_to_m(total_mm);
};

total_length_m(handles, props);
"""


# ── 自检: mock pyRevit 宿主 + 真实 Intent 规则 ────────────

class _MockElementId:
    def __init__(self, value: int):
        self.IntegerValue = value

    def __eq__(self, other):
        return (isinstance(other, _MockElementId)
                and other.IntegerValue == self.IntegerValue)

    def __hash__(self):
        return hash(self.IntegerValue)


class _MockElement:
    def __init__(self, eid: int, diameter_mm: float, length_mm: float):
        self.Id = _MockElementId(eid)
        self.DiameterMm = diameter_mm
        self.LengthMm = length_mm


class _MockSelection:
    def __init__(self, elements):
        self._ids = [e.Id for e in elements]
        self.set_ids = None

    def GetElementIds(self):
        return list(self._ids)

    def SetElementIds(self, ids):
        self.set_ids = list(ids)


class _MockUIDocument:
    def __init__(self, elements):
        self.Selection = _MockSelection(elements)
        self._elements = {e.Id: e for e in elements}
        self.Document = self

    def GetElement(self, eid):
        return self._elements[eid]


class _MockRevit:
    """mock pyRevit 宿主: ActiveUIDocument 形态"""

    def __init__(self, elements):
        self.ActiveUIDocument = _MockUIDocument(elements)


def _selftest() -> int:
    old_cwd = os.getcwd()
    os.chdir(os.path.dirname(TOOLS_DIR))  # std/ 模块搜索路径相对 cwd
    passed = failed = 0

    def check(label: str, cond: bool):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  ✅ {label}")
        else:
            failed += 1
            print(f"  ❌ {label}")

    try:
        # ── 0. 解释器可用性 ──
        src_dir = check_intent()
        check("check_intent: mini_intent 可导入", os.path.isdir(src_dir))

        # ── 1. mock pyRevit 世界: 3 根管 ──
        elems = [
            _MockElement(201, 50.0, 2000.0),
            _MockElement(202, 150.0, 3500.0),
            _MockElement(203, 100.0, 3000.0),
        ]
        host = _MockRevit(elems)

        # ── 2. 选择集读取 ──
        selected = get_selected_elements(host)
        check("get_selected_elements: 读出 3 个选中元素",
              len(selected) == 3 and [e.Id.IntegerValue for e in selected] == [201, 202, 203])

        # ── 3. 宿主自动定位(沿栈向上找 __revit__) ──
        # 真实场景: __revit__ 在按钮 script.py 的模块全局(非函数局部) —
        # 用 exec 造一个带 __revit__ 的模块级命名空间来模拟
        ns = {'__revit__': host, 'get_revit_host': get_revit_host}
        exec("found = get_revit_host() is __revit__", ns)
        check("get_revit_host: 沿调用栈自动找到 __revit__", ns['found'] is True)

        # ── 4. 完整按钮流程: 选元素 → Intent 规则(总长 m) ──
        total = button_main(RULE_TOTAL_LENGTH_M, host=host)
        check("button_main: 总长 8500mm → 8.5m(std/bim/unit 换算)",
              abs(total - 8.5) < 1e-9)

        # ── 5. set_selection 写回 ──
        n = set_selection(selected, host=host)
        check("set_selection: 3 个元素 Id 写回选择集",
              n == 3 and host.ActiveUIDocument.Selection.set_ids == [e.Id for e in elems])

        # ── 6. 宿主缺失显式报错 ──
        try:
            get_selected_elements(None)
            check("宿主缺失 → RuntimeError", False)
        except RuntimeError as ex:
            check("宿主缺失 → RuntimeError(显式失败, 带指引)", "__revit__" in str(ex))

        print(f"\n  pyrevit_hook selftest: {passed} 通过, {failed} 失败")
        return 0 if failed == 0 else 1
    finally:
        os.chdir(old_cwd)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
    print("用法: python tools/pyrevit_hook.py --selftest")
