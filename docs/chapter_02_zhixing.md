# 第2章：知行合一 — 管道即认知流

> **运行代码**：`python3 src/mini_intent.py examples/lesson_02_zhixing.intent`
> **哲学**：王阳明"知行合一"、庄子"庖丁解牛"
> **语法**：`|>` 管道、`def` 函数、Lambda

---

## 2.1 函数 = 功夫

```intent
def double(x: Int): Int { return x * 2; };
def add_one(x: Int): Int { return x + 1; };
```

你刚定义了两个**函数**。函数是什么？

传统教学中，函数是"一段可重用的代码"。这没错，但太浅了。

王阳明有一个概念——**功夫**。功夫不是在书斋里读到的理论，是在事上磨炼出来的。你能背下 `double(x) = x * 2` 是理论，你写 `def double(x: Int): Int { return x * 2; };` 是功夫。

**函数是你内化了的技艺。** 你不需要每次从头想"两倍是什么意思"，你直接调用 `double(5)`。

---

## 2.2 管道的直觉

```intent
let result = 5 |> double |> add_one;
print(result);  // 11
```

读法：`5` 先经过 `double`（变成 10），再经过 `add_one`（变成 11）。

这是 Intent 管道 `|>` 的核心直觉：**数据从左到右穿过每个函数。**

大多数语言中，你要嵌套写：
```intent
let result = add_one(double(5));
```

从里到外读。`double(5)` → 然后 `add_one(...)`。

管道改变了你的认知结构。你不是嵌套，你是流动。顺着数据的方向想：

```
5 → double → 10 → add_one → 11
```

王阳明说"知行合一"——知和行本质上是一个东西。你知道 `double` 的存在（知），你使用它（行），这两步应该是连续的箭头，不是脱节的嵌套。管道把"知"和"行"连成一条线。

---

## 2.3 庖丁解牛的刀

庄子讲了一个庖丁解牛的故事。庖丁的刀顺着牛的纹理走，游刃有余，十九年刀刃如新。

管道就是那把刀。

```intent
let evens = [];
for x in data {
    if is_even(x) { push(evens, x); };
};
```

每一步都是数据形态的一次转变：

```
原始数据 → 筛选(filter) → 偶数列表
```

大数据的流向同理：

```
.dyn文件列表 → 过滤(file exists) → 解析(get content) → 统计(count lines) → 汇总
```

庖丁没有"切到一半停下来思考下一步"，刀顺着纹理，一气呵成。管道的意义就是让认知顺着数据流，不停顿、不回跳。

---

## 2.4 高阶函数：功夫可以传递

```intent
def triple(x: Int): Int { return x * 3; };
def apply_triple(num: Int): Int {
    return triple(num);
};
print(apply_triple(7));  // 21
```

`apply_triple` 不自己实现三倍逻辑——它调用 `triple`。这是**组合**的思想。

王阳明说功夫是事上磨炼的，但功夫可以传递。你练成了 `triple`，你可以把它交给 `apply_triple`。徒弟不需要自己练功，师傅把功夫传给他。

在编程中，这就是高阶函数：函数可以作为参数传递、作为返回值返回。

---

## 2.5 Lambda：无名之功夫

Intent 中 `fn` 创建匿名函数（Lambda）：

```intent
let doubler = fn(x: Int): Int { return x * 2; };
```

这不只是语法便利。**不是所有功夫都需要一个名字。** 有时候你只是需要"现在给我加倍"，不需要注册一个 `DoublerService`。

禅宗说"吃饭时吃饭，睡觉时睡觉"。不是每一个动作都需要名字和标签。Lambda 就是"当下的功夫"——用在这里，用这一次，用过就放。

---

## 2.6 练习：感受流动

1. 把 `5 |> double |> add_one` 改成 `5 |> add_one |> double`。结果从 11 变成 12。管道顺序 = 认知顺序。
2. 写三个函数：`inc`（+1）、`dec`（-1）、`square`（平方）。用管道组合：`10 |> inc |> square |> dec`。结果是多少？
3. 如果不用管道，嵌套写出来。感受从里到外读的"阻力"。

---

## 2.7 小结

| 语法 | 哲学 |
|------|------|
| `def f(x) { ... }` | 功夫 = 在事上磨炼的技艺 |
| `\|>` 管道 | 知行合一（知→行是连续的箭头） |
| 管道链 | 庖丁解牛（顺着纹理流动） |
| 高阶函数 | 功夫可以传递 |
| Lambda | 当下的功夫（不需命名） |

> **上一章**：[第1章：无为之始](chapter_01_wuwei.md)
> **下一章**：[第3章：格物致知 → 穷举](chapter_03_gewu.md)
