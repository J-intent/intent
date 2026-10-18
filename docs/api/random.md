# random

## `random_val`

> random_val() → Float  返回 0~1 之间的随机浮点数

```intent
def random_val() -> Float
```

## `rand_int`

> rand_int(lo: Int, hi: Int) → Int  返回 [lo, hi] 范围内的随机整数

```intent
def rand_int(lo: Int, hi: Int) -> Int
```

| 参数 | 类型 |
|---|---|
| `lo` | Int |
| `hi` | Int |

## `uniform`

> uniform(lo: Float, hi: Float) → Float  返回 [lo, hi] 范围内的随机浮点数

```intent
def uniform(lo: Float, hi: Float) -> Float
    ensures result >= lo and result <= hi
```

| 参数 | 类型 |
|---|---|
| `lo` | Float |
| `hi` | Float |

**后置条件**:
- result >= lo and result <= hi

## `choice`

> choice(items: List) → Any  从列表中随机选一个元素

```intent
def choice(items: List) -> Any
    requires len(items) > 0
```

| 参数 | 类型 |
|---|---|
| `items` | List |

**前置条件**:
- len(items) > 0

## `dice`

> dice(sides: Int) → Int  掷骰子 [1, sides]

```intent
def dice(sides: Int) -> Int
    requires sides >= 1
    ensures result >= 1 and result <= sides
```

| 参数 | 类型 |
|---|---|
| `sides` | Int |

**前置条件**:
- sides >= 1

**后置条件**:
- result >= 1 and result <= sides

