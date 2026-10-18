# itertools

## `chain`

> chain — 多条序列首尾相续

```intent
def chain(a: Any, b: Any)
```

| 参数 | 类型 |
|---|---|
| `a` | Any |
| `b` | Any |

## `zip_longest`

> zip_longest — 配对, 短的一方补足(不丢弃)

```intent
def zip_longest(a: Any, b: Any, fill: Any)
```

| 参数 | 类型 |
|---|---|
| `a` | Any |
| `b` | Any |
| `fill` | Any |

## `cycle`

> cycle — 循环往复, 重复 n 次

```intent
def cycle(lst: Any, n: Int)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `n` | Int |

## `enumerate`

> enumerate — 物各有其位, 返回 [序号, 值] 对

```intent
def enumerate(lst: Any)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |

## `flatten`

> flatten — 化繁为简, 展平一层

```intent
def flatten(lst: Any)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |

## `unique`

> unique — 去重保序(存在的才留, 不重复)

```intent
def unique(lst: Any)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |

## `chunk`

> chunk — 分而治之, 按大小切块

```intent
def chunk(lst: Any, size: Int)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `size` | Int |

## `groupby`

> groupby — 物以类聚, 按键分组(键限标量)

```intent
def groupby(lst: Any, key_fn: Any)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `key_fn` | Any |

## `count_where`

> count_where — 数一数符合条件的

```intent
def count_where(lst: Any, pred: Any) -> Int
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `pred` | Any |

