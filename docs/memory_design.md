# Intent 内存管理设计文档（MM1）

> 版本：v1.0 ｜ 2026-10-18 ｜ 状态：首期已实现（寄生策略），M2/M3 演进路线见 §6
> 配套：`src/mini_intent.py`（_ObjectRegistry + OBJECT_REGISTRY）、`std/memory.intent`、`tests/test_memory.intent`

---

## 1. 问题定义

Intent 解释器宿主于 CPython：Intent 的运行时值（List/Dict/Instance 等）都是 Python 对象，
其生死由 CPython 引用计数 + 分代 GC 管辖。Intent 语言层面临三个内存问题：

1. **不可观测**：Intent 程序无法知道自己制造了多少对象、多少还活着；
2. **循环引用**：`a.push(a)` 这类自引用/环结构，引用计数永不归零，宿主不触发 GC 就泄漏；
3. **无回收入口**：长跑服务（v3.0 出口要求 24h 内存曲线平坦）需要一个确定性的回收时机。

## 2. 候选策略与决策

| 策略 | 做法 | 评估 |
|---|---|---|
| A. 自持引用计数 | 解释器给每个值维护 RC，环检测另建图扫描 | 与宿主 RC 双重计数，开销翻倍；环检测要遍历全堆——20 人日打底 |
| B. 自持分代 GC | 解释器自建年轻代/老代，mark-sweep | 同上，且要与宿主 GC 争权；v4.0 JIT 前不值得 |
| C. **寄生 + 观测**（选定） | 容器创建即登记弱引用；循环垃圾委托宿主分代 GC；暴露观测/触发 API | 零额外内存管辖成本；观测真实（弱引用不延命）；回收确定（显式 collect） |

**决策理由（心学为体：知止而后有）**：意图运行时的"存在"由宿主保管，
Intent 第一件该做的事不是夺权，是**看见**。策略 C 用最小代价拿到三样东西：
真实的存活计数、真实的累计分配、确定的循环回收时机。
自持 GC（A/B）留到 M3 JIT 期——那时内存模型必须与执行引擎同构设计，提前做就是重复造轮子。

## 3. 架构（首期已落地）

```
┌────────────────────────────────────────────┐
│ Intent 程序                                  │
│   std.memory.mem_live() / gc_collect() ...  │  ← std/memory.intent（契约封装）
├────────────────────────────────────────────┤
│ 内置层（mini_intent.py）                     │
│   mem_live_count / mem_alloc_total /        │
│   mem_stats_info / gc_collect_now /         │
│   ref_count_of                              │
├────────────────────────────────────────────┤
│ _ObjectRegistry（模块级单例）                │
│   register(obj)  ← ListValue/DictValue/     │
│                     InstanceValue.__init__  │  ← 三个容器类构造即挂接
│   _refs: [weakref.ref]  弱引用不拉长寿命     │
│   live() / stats() / collect()              │
├────────────────────────────────────────────┤
│ 宿主 CPython：gc.collect() 分代回收循环垃圾   │
└────────────────────────────────────────────┘
```

**不变量**：
- 注册表只持弱引用——它自身不是任何 Intent 对象的存活理由；
- `collect()` = 先登记表快照 → `gc.collect()` → 再快照，差值即回收容器数（观测值）；
- `_refs` 超 4096 自动修剪死亡弱引用，注册表自身不泄漏。

**双路径覆盖**：VM（intent_bytecode.py）复用同一套值类（import 自 mini_intent），
树遍历与字节码执行共享同一注册表，vm_diff 两侧观测一致。

## 4. API 语义（std/memory.intent）

| 函数 | 语义 | 契约 |
|---|---|---|
| `mem_live() -> Int` | 当前存活容器数 | `ensures result >= 0` |
| `alloc_total() -> Int` | 累计创建容器数（单调增） | `ensures result >= 0` |
| `mem_stats() -> Dict` | live/alloc_total/reclaim_total/by_type | — |
| `gc_collect() -> Int` | 触发循环回收，返回本次回收数 | `ensures result >= 0` |
| `ref_count(obj) -> Int` | 宿主引用计数（诊断观测值，含解释器内部引用） | `ensures result >= 1` |

## 5. 测试判定（tests/test_memory.intent，5/5）

- 分配可观测：20 个被持有列表 → live ≥ baseline + 20；
- 累计单调：alloc_total 只增不减；
- 自引用可诊断：`push(a, a)` 后 ref_count > 2；
- **循环可回收**：函数作用域内制造 10 个自环并丢弃 → live 暂存（RC 不归零）→
  `gc_collect()` 后 live 回落 ≥10——「长跑无泄漏 + 循环引用回收」的命令级判定；
- 统计字典形态完整。

## 6. 已知限制与演进

| # | 限制 | 影响 | 计划 |
|---|---|---|---|
| L1 | `ListValue.copy()` 等不处理环——自引用列表作 Intent 函数实参时无限递归（形参复制传值语义） | 诊断路径受限（ref_count 须直调内置） | M2 期修：copy 带 memo 表 |
| L2 | 注册表只覆盖容器（List/Dict/Instance）；字符串/整数等标量不登记 | 标量无环，不影响回收正确性 | 不修（反膨胀） |
| L3 | ref_count 是宿主观测值，非语言级 RC | 只做诊断，不做精确契约 | 语言级 RC 随 M3 JIT 同构设计 |
| L4 | 无自动回收策略（无阈值触发/无分代调优） | 长跑需程序自行择机 collect | M4 剖析工具期补 `--mem-profile` |

**M2 衔接**：属性访问优化（内联缓存/隐藏类）要求对象形状稳定——
注册表的 by_type 统计是其现成度量。**M3 衔接**：JIT 编译的代码若自持 GC，
必须与 _ObjectRegistry 同构（同一 Hook 点、同一不变量），否则双重管辖。

## 7. 风险登记（对应 ROADMAP_LONGTERM R7）

内存模型选错（RC vs GC）的最大返工风险，已被「寄生先行」对冲：
首期交付的是观测与回收入口，不绑定任何管辖策略；
M2/M3 的选型可以拿首期的真实分配数据说话，而不是拍脑袋。
