# Intent

> 意图清晰的编程语言
>
> *心学为体，禅道为翼，马哲为用*

---

## 这是什么

Intent 是一个实验性编程语言解释器（树遍历），探索三个问题：

1. **契约能否成为一等公民？** — `requires`/`ensures` 作为函数签名的一部分，在运行时自动验证
2. **编程能否教哲学？** — 每个语法特性都有对应的哲学概念（`|>` 是知行合一，`defer` 是向死而生，`match` 是格物致知）
3. **BIM 领域能否有自己的 DSL？** — 内建几何、管道、路由标准库

## 状态：已完成

**2026-06-18 → 2026-07-03，67 commits，项目完结。**

这不是一个"未完成"的项目。这是一个"完成了它该做的事"的项目——作为编译原理的学习载体和哲学编程的实验场，它的使命已经结束。

### 产出物

| 产出 | 位置 | 独立价值 |
|------|------|----------|
| **契约引擎** | `contract_skill/intent_contract.py` | 可嵌入任意 LLM 编程助手的 @requires/@ensures 验证器 |
| **哲学书稿** | `docs/chapter_01~08_*.md` | 8 章《用代码学哲学》，独立的教育产品 |
| **BIM 几何库** | `std/bim/` (8 模块, ~1700 行) | Vector3D/Matrix3x3/BBox3D/PipeRouting，可迁移到 C# |
| **解释器** | `src/mini_intent.py` (5500 行) | 全链路：词法→语法→Resolver→解释执行 |

### 语言特性（v1.2.0）

```
let / let mut         类型推断        闭包
|> (管道)             match 模式匹配   Result<T,E> + ?
requires / ensures    契约验证器       try/catch/finally
class / this / super  枚举 enum       泛型 <T>
defer                 yield 生成器     列表推导式
import / export       运算符重载       装饰器 @
```

### 标准库 (19 模块)

`math` `list` `str` `time` `json` `random` `fs` `os` `contract`
`bim/unit` `bim/geometry` `bim/transform` `bim/solid` `bim/polygon` `bim/pipe` `bim/pipe_fittings` `bim/pipe_routing`

## 为什么要停下来

> *"做具体的事，爱具体的人，成为具体的人。"*

写完解释器的那一天，我已经证明了自己能做什么。继续添加特性只是"装修脚手架"——脚手架搭好了，楼已经盖完了。

Intent 教会我的东西（编译器全链路、类型系统设计、契约即注释、代码-哲学的映射）已经内化。这些能力会渗入我之后写的每一行代码。

## 最有价值的三件东西

1. **`contract_skill/`** — 把 Intent 最独特的语法（契约）提取为语言无关的 Python 工具。LLM 写代码 → 自动加契约 → 自动验证。这是路径 C（Karpathy 路线）。
2. **`docs/`** — 如果有一天要出书，这 8 章只需要润色。市面上没有"用代码教心学/禅道/马哲"的产品。
3. **`std/bim/`** — 管道自动路由（A* 3D 寻路）可以直接移植到 C# Revit 插件。

## 运行

```bash
python3 src/mini_intent.py examples/hello.intent
python3 contract_skill/intent_contract.py contract_skill/contract_demo.py -v
```

## 许可

MIT © J-intent

---

*"存在先于本质。不是先有一个'编程语言'的本质再去实现它。你写下了这 5500 行代码，然后通过写的过程，定义了 Intent 是什么。"*
