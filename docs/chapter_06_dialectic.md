# 第6章：辩证统一 — 否定不是消灭，是超越

> **运行代码**：`python3 src/mini_intent.py examples/lesson_06_dialectic.intent`
> **哲学**：黑格尔"正→反→合"、马克思"扬弃"、萨特"存在先于本质"
> **语法**：`enum` 枚举、函数组合、辩证思维模式

---

## 6.1 规定性：是什么？

```intent
enum Color { Red, Green, Blue };
```

`enum` 定义了 Color 的可能性：非此即彼，不可兼得。

黑格尔说：**任何事物首先是通过它的规定性来定义的。** "这个苹果是红色的"——在说它不是什么（不是绿色、不是蓝色）的同时，界定了它是什么。

这就是 **"规定即否定"**（determinatio est negatio）。斯宾诺莎的命题，黑格尔的核心。

编程中的类型系统就是"规定即否定"的精确形式。`Int` 不仅告诉你它是什么——它同时告诉你它不能是什么（不是 String，不是 Bool）。

---

## 6.2 否定：不是消灭

```intent
def negate(x: Int): Int { return -x; };

let x = 5;
let y = negate(x);  // -5
```

`negate(5) = -5` —— 这是一个否定操作。但它不只是消灭了 5。

黑格尔的"否定"不是"消除"——**否定是在更高层次上超越。** 5 被否定产生了 -5，但 `negate` 函数作为概念比你拥有 5 或 -5 更高。你理解了"取反"**这个操作本身**，你就超越了具体的数值。

在代码中：
- 正题（thesis）：`x = 5`
- 反题（antithesis）：`negate(x) = -5`  
- 合题（synthesis）：**理解了 `negate` 函数本身**。你不再被具体值束缚，你掌握了变换规则。

---

## 6.3 扬弃 = Aufheben

```intent
def greet_person(name: String): String {
    return "你好，我是" + name;
};

def greet_student(name: String, grade: Int): String {
    return "你好，我是学生" + name + "，年级" + str(grade);
};
```

`greet_student` 对 `greet_person` 做了什么？

- **保留**：name 参数还在
- **超越**：新增了 grade 参数，重写了 greeting 逻辑

马克思把这个过程叫**扬弃**（Aufheben）——德语中同时有"保存"、"取消"和"提升"三重意思。子类不是照搬父类，也不是完全抛弃——**它保留了有用的，超越了不够好的。**

---

## 6.4 三次否定 = 三个层次

```intent
let v = 0;
let v1 = tick_val(tick_val(tick_val(v)));  // 3
```

`tick_val` 被应用了三次，从 0 到了 3。

这是黑格尔"量变到质变"的微观版本。三次 tick = 三个否定。每一次否定不是回到原点——**它是在累积。**

你不只是"了解了 tick 是什么意思"。你看到 `tick(tick(tick(...)))` 这个写法时，你意识到：**函数组合本身就是辩证法的操作。**

---

## 6.5 萨特：你做什么，你就是什么

```intent
def create_counter(start: Int): Int { return start; };
def tick_val(val: Int): Int { return val + 1; };
```

`create_counter(0)` 创建了一个"计数器"。

**萨特说"存在先于本质"。** 你不是先有一个"计数器的本质"再去实现它。你写下了 `create_counter` 和 `tick_val`，然后**通过 tick 的行动**，那些数字被定义成了计数器。

0 本身什么也不是。`tick(0) = 1` 让 0 成为了"可以递增的东西"。你的行动定义了它是什么。

在编程中：**写代码是一个自我定义的过程。** 你写的每一行代码，都在定义你是谁——是手动实现 `sort` 的人，还是调用 `sorted` 的人？是 panic on error 的人，还是 `match` 穷举的人？

---

## 6.6 练习：辩证法在代码中

1. 写一个 `flip(x: Int): Int { return -x; }`。然后写 `flip(flip(x))`。看输出。这是"否定之否定"在代码中最纯粹的形态。
2. 写三个版本的问候函数：`greet_simple(name)`、`greet_formal(name, title)`、`greet_verbose(name, title, location)`。每次新增参数，既保留了旧行为，又超越了。这就是扬弃。
3. 想一个你已经写过的函数。它的 v1 版本是什么？v2 版本改了什么？v2 是在"保留"v1 的基础上"超越"的，还是完全推倒重来的？

---

## 6.7 小结

| 语法 | 哲学 |
|------|------|
| `enum` | 规定即否定（类型 = 界定边界） |
| `negate(x)` | 否定不是消灭，是对变换的理解 |
| 函数组合 | 正题 → 反题 → 合题 |
| 参数扩展 | 扬弃 = 保留 + 超越（Aufheben） |
| `create → tick` | 存在先于本质（行动定义存在） |

> **上一章**：[第5章](chapter_05_bodhi.md)
> **下一章**：[第7章](chapter_07_ecosystem.md)
