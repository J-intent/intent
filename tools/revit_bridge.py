#!/usr/bin/env python3
"""tools/revit_bridge.py — Revit × Intent 元素桥（BD2）

UnwrapElement 模式 + bim 元素收发: Intent 脚本跨 .NET 边界操控 Revit 元素。

═══ 核心不变式 ═══

1. **Intent 侧永远只见 handle（Int），不见 .NET 对象。**
   句柄是唯一的跨边界引用: Python 侧把元素包成 handle 送进 Intent,
   Intent 只回传 handle 集(选择/筛选结果), Python 侧再解回元素。
   解释器不需要任何 .NET 知识 — 这是寄生期架构(见 ROADMAP §0.1)。

2. **unwrap 只发生在边界。** Dynamo 的包装对象(DynamoWrapper 等)与
   pyRevit 的包装对象在进入注册表前一律解包, 注册表里只有裸元素。

3. **句柄失效是显式错误。** 元素被删/句柄从未发送 → RuntimeError,
   不返回哑值 null(契约哲学: 显式失败)。

═══ 用法一: Dynamo Python 节点（CPython3 引擎）═══

    import sys
    sys.path.append(r"D:\\Desktop\\intent\\tools")
    import revit_bridge

    session = revit_bridge.RevitSession()
    handles = session.send(IN[0])          # Revit 元素(可带 Dynamo 包装) → handles
    props = session.read_props(handles, ["管径", "长度"])  # 边界读属性
    picked = session.run(RULE_CODE, handles=handles, props=props)
    OUT = session.recv(picked)             # handles → Revit 元素

═══ 用法二: pyRevit 按钮（CPython3 模式）═══

    import sys
    sys.path.append(r"D:\\Desktop\\intent\\tools")
    import revit_bridge
    # 见 tools/pyrevit_hook.py — 选择集收发同经本桥

═══ 自检 ═══

    python tools/revit_bridge.py --selftest

    mock Revit 世界(FakeElement + Dynamo/pyRevit 两种包装)上跑真实
    Intent 规则脚本(std/bim/unit 参与), 验证 wrap→Intent→recv 全闭环。

═══ 完整 BD2 剩余（最小切片已交付, 见 ROADMAP_LONGTERM 维度 8）═══

- 属性双向通道: Intent 侧直接 get/set 元素参数（现经 props 字典旁路）
- 事务与撤销: 批量写操作的 Transaction 包裹
- 事件订阅: 元素变更回调进 Intent
"""

import os
import sys

# ── 桥本体（无 Revit 依赖, 纯 Python 可测）────────────────

def unwrap_element(obj):
    """UnwrapElement 模式: 拆掉 Dynamo/pyRevit 的 .NET 包装, 拿裸元素

    识别链(按优先级):
      1. __unwrap__()          — pyRevit/RevitPythonShell 约定
      2. InternalElement 属性  — Dynamo Revit.Elements 包装
      3. unwrap() 方法         — 其他封装库约定
    都不命中 → 原样返回(标量/列表等非元素值透传)。
    """
    if hasattr(obj, '__unwrap__'):
        return obj.__unwrap__()
    internal = getattr(obj, 'InternalElement', None)
    if internal is not None:
        return internal
    if hasattr(obj, 'unwrap') and callable(obj.unwrap):
        return obj.unwrap()
    return obj


class ElementRegistry:
    """handle ↔ element 双向注册表

    - wrap 幂等: 同一元素恒得同一 handle(按元素 Id 去重)
    - handle 从 1 起顺序分配, 与 Revit ElementId 解耦(证明映射层在工作)
    - resolve 失效句柄 → RuntimeError(显式失败)
    """

    def __init__(self):
        self._handle_of = {}   # element_key → handle
        self._element_of = {}  # handle → element
        self._next = 1

    @staticmethod
    def _key(element):
        """元素标识: 优先 Revit ElementId.IntegerValue, 退化为 id()"""
        eid = getattr(element, 'Id', None)
        ival = getattr(eid, 'IntegerValue', None)
        return ival if isinstance(ival, int) else id(element)

    def wrap(self, element) -> int:
        element = unwrap_element(element)
        key = self._key(element)
        if key not in self._handle_of:
            handle = self._next
            self._next += 1
            self._handle_of[key] = handle
            self._element_of[handle] = element
        return self._handle_of[key]

    def resolve(self, handle: int):
        if handle not in self._element_of:
            raise RuntimeError(
                f"桥句柄 {handle} 不存在(元素已删除, 或从未经本会话发送)")
        return self._element_of[handle]

    def wrap_all(self, elements):
        return [self.wrap(e) for e in elements]

    def resolve_all(self, values):
        """Intent 返回值 → Python 值: handle 解回元素, 非 handle 原样透传"""
        out = []
        for v in values:
            if isinstance(v, bool):
                out.append(v)
            elif isinstance(v, int):
                out.append(self.resolve(v))
            else:
                out.append(v)
        return out

    def __len__(self):
        return len(self._element_of)


class RevitSession:
    """一次 Dynamo 求值 / 一次 pyRevit 点击的桥会话

    send 进, recv 出; read_props 在边界把元素属性读成 Intent 字典
    (Intent 侧不直接碰 .NET — 属性读取是边界的活)。
    """

    def __init__(self, registry: ElementRegistry = None):
        self.registry = registry or ElementRegistry()

    def send(self, elements):
        """Revit 元素列表(可带包装) → Intent 侧 handle 列表"""
        return self.registry.wrap_all(elements)

    def recv(self, values):
        """Intent 侧返回值 → Python 值(handle 解回元素, 其余透传)"""
        return self.registry.resolve_all(values)

    def read_props(self, handles, prop_map):
        """边界读属性: prop_map = {Intent字段名: 元素属性名}

        返回 {handle: {字段名: 值}} — 属性读取失败的元素字段置 None
        (显式缺失, 不静默丢字段)。
        """
        props = {}
        for h in handles:
            element = self.registry.resolve(h)
            entry = {}
            for field, attr in prop_map.items():
                entry[field] = getattr(element, attr, None)
            props[h] = entry
        return props

    def run(self, intent_code: str, **injected):
        """在宿主进程内跑 Intent 代码, 返回最后一条表达式的原生 Python 值

        injected: 变量名 → Python 值(int/float/str/list/dict/bool),
        经 prelude 注入 Intent 全局(与 tools/dynamo_node.py 同模式)。
        """
        import mini_intent
        prelude = "".join(
            f"let {name} = {_intent_literal(value)};\n"
            for name, value in injected.items())
        raw = mini_intent.run_source(
            prelude + intent_code, filename="revit_bridge_session")
        return _to_native(raw)


def _to_native(value):
    """Intent 运行时值树 → Python 原生值

    run_source 的返回值对容器是 RuntimeValue 树(ListValue.value 里仍是
    IntValue 等); 桥的边界只认原生类型, 故在此统一脱壳。
    """
    mini_intent = sys.modules.get('mini_intent')
    rv_cls = getattr(mini_intent, 'RuntimeValue', None)
    if rv_cls is not None and isinstance(value, rv_cls):
        return _to_native(value.value)
    if isinstance(value, list):
        return [_to_native(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_native(v) for k, v in value.items()}
    return value


def _intent_literal(value) -> str:
    """Python 值 → Intent 字面量(注入 prelude 用)"""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_intent_literal(v) for v in value) + "]"
    if isinstance(value, dict):
        items = ", ".join(
            f"{_intent_literal(k)}: {_intent_literal(v)}"
            for k, v in value.items())
        return "{" + items + "}"
    raise TypeError(f"桥注入不支持的类型: {type(value).__name__}")


# ── 选管规则（BD2 闭环演示: Intent 侧只见 handle）──────────

RULE_SELECT_PIPES = """
import std.bim.unit;

// 选管规则: 管径 ≥ 100mm 且 长度 ≥ 3m
// props[handle] = [管径mm, 长度mm]; mm_to_m 来自 std/bim/unit —
// import 扁平注入符号(中间名 unit 不存在, 见 docs/spec.md §3.8 已知边界),
// 规则是纯 Intent, 不含任何 Revit/.NET 痕迹。
def select_pipes(handles, props) {
    let mut out = [];
    for h in handles {
        let p = props[h];
        if p[0] >= 100.0 and mm_to_m(p[1]) >= 3.0 {
            push(out, h);
        };
    };
    return out;
};

select_pipes(handles, props);
"""


# ── 自检: mock Revit 世界 + 真实 Intent 规则 ──────────────

class _MockElementId:
    def __init__(self, value: int):
        self.IntegerValue = value


class _MockElement:
    """mock Revit 元素(管段): Id + 两个属性, __eq__ 按 Id"""

    def __init__(self, eid: int, diameter_mm: float, length_mm: float):
        self.Id = _MockElementId(eid)
        self.DiameterMm = diameter_mm
        self.LengthMm = length_mm

    def __eq__(self, other):
        return (isinstance(other, _MockElement)
                and other.Id.IntegerValue == self.Id.IntegerValue)

    def __hash__(self):
        return hash(self.Id.IntegerValue)

    def __repr__(self):
        return f"Pipe({self.Id.IntegerValue})"


class _DynamoWrapper:
    """mock Dynamo 包装: InternalElement 形态"""

    def __init__(self, element):
        self.InternalElement = element


class _PyRevitWrapper:
    """mock pyRevit 包装: __unwrap__ 形态"""

    def __init__(self, element):
        self._element = element

    def __unwrap__(self):
        return self._element


def _selftest() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(repo_root, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    old_cwd = os.getcwd()
    os.chdir(repo_root)  # std/ 模块搜索路径相对 cwd
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
        import mini_intent  # noqa: F401  (RevitSession.run 内部用)

        # ── 1. unwrap_element 三种形态 ──
        e = _MockElement(101, 50.0, 2000.0)
        check("unwrap: Dynamo 包装拆出裸元素",
              unwrap_element(_DynamoWrapper(e)) is e)
        check("unwrap: pyRevit 包装拆出裸元素",
              unwrap_element(_PyRevitWrapper(e)) is e)
        check("unwrap: 非元素值原样透传", unwrap_element(42) == 42)

        # ── 2. mock Revit 世界: 4 根管, 2 根过规则 ──
        elems = [
            _MockElement(101, 50.0, 2000.0),    # 径不足
            _MockElement(102, 150.0, 3500.0),   # ✓
            _MockElement(103, 100.0, 3000.0),   # ✓ 边界(≥)
            _MockElement(104, 200.0, 1500.0),   # 长不足
        ]
        inbound = [
            _DynamoWrapper(elems[0]),   # 混入两种包装 + 裸传
            elems[1],
            _PyRevitWrapper(elems[2]),
            elems[3],
        ]
        session = RevitSession()
        handles = session.send(inbound)
        check("send: 4 元素 → 4 handle(顺序分配)",
              handles == [1, 2, 3, 4] and len(handles) == 4)
        check("wrap 幂等: 同元素同 handle",
              session.registry.wrap(elems[0]) == 1)

        # ── 3. 边界读属性 → Intent 字典 ──
        props = session.read_props(
            handles, {"d": "DiameterMm", "l": "LengthMm"})
        # props: {handle: {d, l}} → RULE 期望 [d, l] 列表
        rule_props = {h: [entry["d"], entry["l"]]
                      for h, entry in props.items()}
        check("read_props: 边界读出全部属性",
              rule_props[1] == [50.0, 2000.0] and rule_props[3] == [100.0, 3000.0])

        # ── 4. Intent 规则脚本跑选管(真实解释器 + std/bim/unit) ──
        picked_handles = session.run(
            RULE_SELECT_PIPES, handles=handles, props=rule_props)
        check("run: Intent 规则选中 102/103(边界值 ≥ 含)",
              picked_handles == [2, 3])

        # ── 5. recv: handle 解回元素(身份保持) ──
        picked = session.recv(picked_handles)
        check("recv: handle → 同一元素对象",
              picked == [elems[1], elems[2]])

        # ── 6. 混合值透传 ──
        mixed = session.recv([1, "备注", 3.5, True])
        check("recv: 非 handle 值原样透传",
              mixed[0] == elems[0] and mixed[1] == "备注"
              and mixed[2] == 3.5 and mixed[3] is True)

        # ── 7. 失效句柄显式报错 ──
        try:
            session.recv([999])
            check("recv: 失效句柄 → RuntimeError", False)
        except RuntimeError as ex:
            check("recv: 失效句柄 → RuntimeError(显式失败)",
                  "999" in str(ex))

        print(f"\n  revit_bridge selftest: {passed} 通过, {failed} 失败")
        return 0 if failed == 0 else 1
    finally:
        os.chdir(old_cwd)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
    print("用法: python tools/revit_bridge.py --selftest")
