# statistics

## `mean`

> mean(lst: List) → Float  算术平均(空表违约)

```intent
def mean(lst: Any) -> Float
    requires len(lst) > 0
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |

**前置条件**:
- len(lst) > 0

## `median`

> median(lst: List) → Float  中位数(偶数取中间两值的平均)

```intent
def median(lst: Any) -> Float
    requires len(lst) > 0
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |

**前置条件**:
- len(lst) > 0

## `variance`

> variance(lst: List) → Float  总体方差(均方偏离)

```intent
def variance(lst: Any) -> Float
    requires len(lst) > 0
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |

**前置条件**:
- len(lst) > 0

## `stdev`

> stdev(lst: List) → Float  总体标准差(方差的平方根)

```intent
def stdev(lst: Any) -> Float
    requires len(lst) > 0
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |

**前置条件**:
- len(lst) > 0

