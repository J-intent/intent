# tools/dynamo_node.py — Intent × Dynamo 节点模板（BD1）
#
# 用法（Dynamo Python 节点，引擎选 CPython3 / PythonNet3，Revit 2025+）：
#   1. 把本文件内容粘进 Python 节点（或存为 .py 由节点加载）
#   2. 修改 INTENT_CODE 为你的 Intent 源码
#   3. IN[0]/IN[1]... 是节点输入，OUT 是输出
#
# 机制：Dynamo 的 PythonNet3 引擎跑在真 CPython 3.11 上，能 import 任意
# PyPI 包；Intent 解释器是纯 Python（src/mini_intent.py，零 C 依赖），
# 所以 import 即用——不需要 C ABI / WASM / 重写。
#
# 契约价值：Intent 的 requires 失败会抛 ContractViolation（带明确原因），
# Dynamo 节点红灯显示的是「前置条件1失败: x > 0」而不是 cryptic null。
#
# 2026-10-19 BD2 期修复（原模板从未实跑过的三处断点）：
#   ① `geometry.point(...)` 不可用 — import std.bim.geometry 扁平注入
#      Point3D 等符号，中间名 geometry 并不存在（spec §3.8 已知边界）；
#      且 bim/geometry 无 point() 函数。改为 Point3D() + create()。
#   ② 返回值是 RuntimeValue 树（ListValue.value 内为 InstanceValue），
#      Dynamo 吃不下 — 模板改返回扁平 [x, y, z] 浮点（Dynamo 友好）。
#      富几何转换（InstanceValue → DesignScript Point）属 BD4 范围。
#   ③ 工作目录依赖：std/ 模块按 cwd 相对查找，节点里用绝对路径注入。

import sys

# ── 配置：Intent 源码位置（按你的实际路径改） ──────────
INTENT_SRC_PATH = r"D:\Desktop\intent\src"
INTENT_ROOT = r"D:\Desktop\intent"   # std/ 搜索根（ModuleSystem 按 cwd 找）
if INTENT_SRC_PATH not in sys.path:
    sys.path.append(INTENT_SRC_PATH)

import os
import mini_intent  # Intent 解释器本体

# ── 你的 Intent 代码（带契约的 BIM 规则示例） ──────────
INTENT_CODE = """
import std.bim.geometry;

// 柱网生成: 契约保证数量与间距合法
// 返回扁平坐标 [x, y, z] — Dynamo 侧再组装(见文件头注②)
def column_grid(spacing: Float, count: Int): List
    requires spacing > 0.0
    requires count > 0
    ensures len(result) == count
{
    let mut pts = [];
    let mut i = 0;
    while i < count {
        let p = Point3D();
        p.create(i * spacing, 0.0, 0.0);
        pts = pts + [[p.x, p.y, p.z]];
        i = i + 1;
    };
    return pts;
};
"""

# ── 执行 ──────────────────────────────────────────────
# IN[0] = 间距, IN[1] = 数量（Dynamo 输入经 IN 列表传入）
spacing = IN[0] if IN[0] is not None else 6000.0   # mm
count = int(IN[1]) if IN[1] is not None else 5

# 把 Dynamo 输入注入 Intent 全局（run_source 前声明）
full_code = f"let spacing = {spacing};\nlet count = {count};\n" + INTENT_CODE + """
column_grid(spacing, count);
"""

# std/ 模块按 cwd 相对查找 — 切到 intent 根再跑, 完事还原(见文件头注③)
_old_cwd = os.getcwd()
try:
    os.chdir(INTENT_ROOT)
    result = mini_intent.run_source(full_code, filename="dynamo_node")
except mini_intent.ContractViolation as e:
    # 契约违约: Dynamo 节点红灯 + 明确原因（不是 null）
    OUT = f"契约违约: {e}"
except Exception as e:
    OUT = f"Intent 错误: {e}"
else:
    # RuntimeValue 树 → 原生(list/dict 递归脱壳), Dynamo 只认原生类型
    def _native(v):
        if isinstance(v, mini_intent.RuntimeValue):
            return _native(v.value)
        if isinstance(v, list):
            return [_native(x) for x in v]
        if isinstance(v, dict):
            return {k: _native(x) for k, x in v.items()}
        return v
    OUT = _native(result)
finally:
    os.chdir(_old_cwd)
