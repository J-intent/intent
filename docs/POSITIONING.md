# Intent 定位书：阿J 风格的语言

> 版本：v2.5.0 ｜ 2026-10-18 ｜ 配套：`ROADMAP_LONGTERM.md`（演进路线）、`PROGRESS_PLAN.md`（LangForge 管理方案）
>
> 本文回答三个问题：**这门语言为什么长这样（哲学映射）｜它该用在哪（画像战场）｜怎么变成生产力（Dynamo 落地）**

---

## 0. 一句话定位

> **Intent 是一门「契约优先」的语言：把「你想干什么」钉在签名上，让机器（和 AI）无法假装不知道。**

它不是 Python 的竞品，是 Python 的**意图层**——在需要「说清楚再动手」的地方（BIM 自动化、AI 协作、个人系统），它比 Python 更诚实。

---

## 1. 哲学 → 语言：每个特性都有出处

阿J 的框架是「心学为体，禅道为翼，马哲为用」+ 个人志的「安顿」。映射不是装饰，是设计约束：

| 哲学源 | 语言特性 | 现状 | 设计含义 |
|---|---|---|---|
| **心学·知行合一** | 契约系统 `requires/ensures` | ✅ 运行时可验证 | 「知」是签名上的条件，「行」是函数体——两者不匹配即违约。这是语言的灵魂，不是功能 |
| **心学·事上练** | `requires` 进门检查 | ✅ | 条件不具备就拒之门外——「在事上磨炼」不是硬闯 |
| **禅道·无住生心** | `pure` 纯函数 + `let` 不可变默认 | ✅ | 不执外相：默认不改变世界，改变需显式声明（`let mut`） |
| **禅道·格物** | `let` 关键字即「格物」 | ✅ | 变量声明 = 探究事物之理，不是随手占位 |
| **马哲·量变到质变** | 渐进类型（L1 已落地） | ✅ | 标注从「量」（可选）累积到「质」（编译期防错）——不要求一步到位 |
| **马哲·结构化** | 结构化并发 `scope{}`（CC1） | ✅ | 任务的生与死都在声明处可见——「向死而生」的作用域版 |
| **安顿·边界管理**（衣） | 模块边界 + 契约边界 | ✅ | 个人志底层是「安顿」，衣=边界管理——语言的边界感即存在感 |
| **安顿·三层**（物质/关系/意义） | 语言三层：语法（物质）/ 组合（关系）/ 契约（意义） | ✅ | 只有第一层叫活着（能跑），只有第三层叫飘着（光说不练）——三层齐备才是语言 |
| **地球OL 三柱**（世界/自我/创造） | 语言三境：标准库（世界）/ REPL+调试器（自我）/ 脚本（创造） | ✅ | 用 Intent 编程人生 = 创造层；地球OL 的维护脚本是第一批真实用户 |

**关键推论**：Intent 的差异化不在语法糖，在**「意图显式化」**——Python 把意图藏在注释和测试里，Intent 把意图钉在签名上。这对 AI 协作是决定性的（见 §3.3）。

---

## 2. 画像 → 四大战场

阿J 画像：BIM 工程师（Revit/Dynamo/pyRevit，翻模+CBWD 工具链）｜哲学实践者（地球OL）｜AI 协作者（出思路、指挥 AI、验收）｜「BIM 是生存桥，圈外是归宿」。

| 战场 | 为什么是 Intent | 现状 | 优先级 |
|---|---|---|---|
| **① Dynamo/Revit 生产力** | 他的主业战场；Python 在 Dynamo 里是「脚本胶水」，Intent 是「带契约的构件逻辑」——翻模规则、开洞合并、管道路由这类**规则明确、边界清晰**的活，契约优先的语言天生适合 | bim 模块 7 个（geometry/pipe/solid…）已有雏形 | **P0** |
| **② 地球OL 自我维护** | 因果链结算、checkin 分析、哲学 KG 查询——「用 Intent 编程人生」的创造层落地 | 未开始（地球OL 是 Flask+SQLite） | P1 |
| **③ AI 协作的意图语言** | 他的工作模式是「出思路 → AI 落地 → 验收」——**契约就是给 AI 的需求规格书**：`requires` 说清前提，`ensures` 说清验收，AI 无法交差时糊弄。这是「指挥 AI」的语言级工具 | 契约系统已就绪，未产品化 | P1 |
| **④ BIM 领域包生态** | CBWD 工具链（翻弯/打断/连接/开洞/标签排列）全部可移植成 Intent bim 包——「圈内能力变现」的生存桥 | 7 模块雏形 | P2 |

**战略判断**：战场①是「变成生产力」的答案，战场③是「为什么不是 Python」的答案。两者合起来：**在 BIM 自动化里，用一门 AI 无法糊弄的语言**。

---

## 3. Dynamo 落地路径（技术核心）

### 3.1 关键事实（2026-10 调研）

- Dynamo 的 Python 节点有四种引擎：IronPython2（遗产）/ IronPython3 / CPython3（Python.NET 2.5）/ **PythonNet3（CPython 3.11 + Python.NET 3，Revit 2025+ 可用，.NET 8）**
- **PythonNet3 跑在真正的 CPython 上——能 import 任意 PyPI 包**
- Dynamo Python 节点接口：`IN[0]` 输入列表 / `OUT` 输出 / `UnwrapElement()` 解包 Revit 元素
- **Intent 解释器是纯 Python 写的**（`src/mini_intent.py` + `src/intent_bytecode.py`，零 C 依赖）

### 3.2 路径：不需要重写，import 就行

Dynamo PythonNet3 节点里直接跑 Intent：

```python
# Dynamo Python 节点（引擎选 CPython3 / PythonNet3）
import sys
sys.path.append(r"D:\Desktop\intent\src")
import mini_intent  # Intent 解释器本体就是 Python 模块

# Intent 源码：带契约的翻模规则
intent_code = '''
import std.bim.geometry;

def column_grid(spacing: Float, count: Int): List
    requires spacing > 0.0
    requires count > 0
    ensures len(result) == count
{
    let mut pts = [];
    let mut i = 0;
    while i < count {
        pts = pts + [geometry.point(i * spacing, 0.0, 0.0)];
        i = i + 1;
    };
    return pts;
};
'''

result = mini_intent.run_source(intent_code)   # 跑 Intent, 拿结果
OUT = result  # 回传 Dynamo
```

**这是最巧的路径**：不碰 C ABI、不写 WASM、不重写解释器——Intent 是 Python 生态的「超集模块」，Dynamo 节点 import 即用。契约在 Dynamo 里变成**节点级的输入校验**（`requires` 不过 = 节点红灯 + 明确原因，而不是 Dynamo 默认的 cryptic null）。

### 3.3 进阶形态（按路线）

| 形态 | 做法 | 期 |
|---|---|---|
| **A. 节点内嵌**（上面） | Python 节点里 import + run_source | 现在就能做（BD1） |
| **B. Dynamo 包** | 打成 `.dyn` 包 + 自定义节点模板（ZeroTouch 视图） | v3.5（BD2） |
| **C. Revit API 桥** | `UnwrapElement` 模式封装：Intent 的 bim 模块直接收/发 Revit 元素 | v3.5（BD2） |
| **D. pyRevit 按钮** | pyRevit 4+ 的 CPython 模式（IronPython2.7 跑不了纯 Python3 的 Intent——**硬限制，诚实标注**） | v4.0（BD3） |

### 3.4 为什么这对阿J 是「生存桥」

他的真实工作：CAD 出图 → 翻模 → 模型出施工图。翻模是「规则明确、重复、边界清晰」的活——**契约优先的语言在翻模场景比裸 Python 强**：每条翻模规则是一条带 `requires/ensures` 的 Intent 函数，规则错了违约报出来，而不是像 Dynamo 脚本那样静默产出错模型。CBWD 工具链（弯头翻弯/开洞合并/标签排列）移植成 Intent bim 包 = **圈内能力的产品化**——这正是「BIM 作保命桥直到副业盖过主业」的桥面。

---

## 4. GitHub 借鉴清单（已调研）

| 项目 | 借鉴什么 | 用在哪 |
|---|---|---|
| **pythonnet** | .NET ↔ CPython 双向桥的对象映射、异常传播、循环引用处理 | I2a Python 桥的参照实现；Dynamo 落地的底层机制 |
| **CUE**（Configure-Unify-Execute） | 「数据=约束」统一模型：`port: int & >0` 类型即校验 | **T5 契约即类型的最近亲**——CUE 证明了「约束写进类型」可行，Intent 的 `requires` 是它的运行时版 |
| **Dhall** | total 语言（保证终止）+ 内容寻址导入（供应链安全） | 契约优先的纯粹形态；包签名（P3）的设计参考 |
| **Starlark**（Bazel） | 嵌入式语言的纪律：确定性、无 IO、受限子集 | Intent 作为「嵌入 Dynamo/pyRevit 的脚本层」的纪律参照 |
| **pyRevit / RevitPythonShell** | BIM 脚本生态的现状与痛点（IronPython 遗产、无契约、难维护） | 对标与互补：Intent 不替代 pyRevit，是它的「规则层」 |
| **ifcopenshell** | BIM 数据层既有生态 | Intent bim 包对接 IFC 的桥（不重造轮子） |

**借鉴纪律**：抄设计不抄实现——CUE 的约束统一思想进 T5，pythonnet 的桥接模式进 I2a，但 Intent 的语法与契约哲学保持自己的（心学为体）。

---

## 5. 接进路线图：新增 BD 任务组（BIM/Dynamo 集成）

以下任务加入 `ROADMAP_LONGTERM.md` 与 LangForge TASKS（Phase 6 批次）：

| ID | 任务 | 依赖 | 判定标准 | 人日 |
|---|---|---|---|---|
| BD1 | Dynamo 节点适配器：`run_source` API + 节点模板 + 示例图 | 无 | `tools/dynamo_node.py` 可在 CPython3 下 import 并跑通示例 | 5 |
| BD2 | Revit API 桥：UnwrapElement 模式 + bim 模块收发 Revit 元素 | BD1 | 测试：Intent 函数收 Revit 元素返回新元素 | 10 |
| BD3 | pyRevit CPython 模式适配 | BD1 | pyRevit 4+ CPython 按钮跑通 Intent 脚本 | 5 |
| BD4 | CBWD 移植：翻弯/开洞合并/标签排列 → Intent bim 包 | BD2 | 三个工具在 Dynamo 里跑出与 CBWD 一致结果 | 15 |
| BD5 | 契约即 Dynamo 校验：requires 失败 → 节点级红灯+原因 | BD1 | 演示：违约输入在 Dynamo 里显式报错 | 3 |

**BD 组的战略位置**：BD1 现在就能做（不依赖任何 Phase 6 任务），是「Intent 第一次变成生产力」的时刻——建议作为 Phase 6 的第一优先，甚至先于 X1 装饰器。

---

## 6. 一页纸总结

```
Intent 是什么：契约优先的语言——意图钉在签名上, AI 无法糊弄
为什么是它：  心学(知行合一→契约) + 安顿(边界管理→模块/契约边界) + 马哲(渐进→类型)
用在哪：      ① Dynamo/Revit 生产力(主战场) ② 地球OL 自我维护 ③ AI 协作意图层 ④ BIM 包生态
怎么落地：    Dynamo PythonNet3 节点 import mini_intent —— 纯 Python 解释器, 零重写
差异化：      Python 把意图藏注释里, Intent 钉签名上 —— BIM 自动化 + AI 协作双场景
下一步：      BD1 Dynamo 适配器(5 人日, 现在就能做) → BD2 Revit 桥 → BD4 CBWD 移植
```
