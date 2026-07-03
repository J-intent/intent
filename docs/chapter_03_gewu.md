# 第3章：格物致知 — 穷举是一种诚实

> **运行代码**：`python3 src/mini_intent.py examples/lesson_03_gewu.intent`
> **哲学**：朱熹"格物致知"、马克思"具体问题具体分析"
> **语法**：`match` 表达式、`enum` 枚举、`if` 守卫

---

## 3.1 枚举：世界的可能性是有限的

```intent
enum Color { Red, Green, Blue };
```

大多数语言让你用字符串或整数表示可能性：
```
color = "red"    // 拼错了？"reed" 也能通过
color = 1        // 1 是什么颜色？
```

Intent 的`enum`说：**非此即彼，没有灰色地带。**

Color 就是 Red、Green、Blue——多一个都不行，少一个也不对。

朱熹说"格物致知"——研究事物时，要把它的每一种可能性都摆出来。枚举就是"格"这件事物的第一步：**它的可能世界有多大？**

---

## 3.2 Match：穷举是一种道德责任

```intent
match color {
    Color::Red => "热烈",
    Color::Green => "生机",
    Color::Blue => "深邃",
};
```

`match` 强制你覆盖所有可能性。

删掉 `Color::Blue => "深邃"`，编译器会报错：**"match 未穷举枚举 Color 的变体: Blue"**。

这是 Intent 最核心的哲学设计之一：**穷举性检查**。

大多数语言中，`switch` 有 `default`，你可以偷懒地说"其他情况都这样处理"。Intent 说：不行。你声明了一个枚举有三项，你就必须逐一处理三项。

**这不是语法约束——这是道德约束。**

你说"我已经全考虑了"——编译器帮你验证。就像一个诤友，在你自我感觉良好时泼冷水：你确定？那 Blue 呢？

---

## 3.3 分支 = 具体问题具体分析

```intent
def score_to_grade(score: Int): String {
    if score >= 90 { return "A"; };
    if score >= 80 { return "B"; };
    if score >= 70 { return "C"; };
    if score >= 60 { return "D"; };
    return "F";
};
```

马克思说"具体问题具体分析"——不搞一刀切。每个分数段有自己独立的处理逻辑。

`match` 让这种哲学变成强制性的：每个分支是平等的、独立的、需要单独考虑的。不存在一个"默认处理"的垃圾箱。

---

## 3.4 模式匹配：不只是值比较

```intent
match result {
    Ok(value) if value > 0 => "正值：" + str(value),
    Ok(value) => "零或负值：" + str(value),
    Err(reason) => "出错了：" + reason,
};
```

`match` 不仅能匹配值，还能解构结构、绑定变量、加条件守卫。

这就是"格物"的精密阶段：不仅把事物分类——还要深入它的内部结构。Result 有两种形态（Ok/Err），每种形态内部有数据（value/reason），你还可以加条件（if value > 0）。

---

## 3.5 练习：穷举你的世界

1. 写一个 `enum Season { Spring, Summer, Autumn, Winter }`，用 match 为每个季节返回一句话。
2. 然后删掉 `Winter` 的分支。跑代码——看编译器的反应。
3. 加 `_ => "其他季节"`（通配符）。为什么编译器不再报错了？通配符是对穷举性承诺的放弃吗？
4. 想一个你日常工作中做决策的场景。如果每次决策都要"穷举所有选项"，会有什么变化？

---

## 3.6 小结

| 语法 | 哲学 |
|------|------|
| `enum` | 事物的可能性是有限的（格物第一步） |
| `match` 穷举 | 覆盖所有情况是道德责任 |
| 模式解构 | 深入事物的内部结构 |
| `if` 守卫 | 具体条件具体分析 |
| `_` 通配符 | 有意识地选择放弃穷举 |

> **上一章**：[第2章](chapter_02_zhixing.md)
> **下一章**：[第4章](chapter_04_contract.md)
