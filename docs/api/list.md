# list

## `sum`

```intent
def sum(lst: Any) -> Int
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |

## `contains`

```intent
def contains(lst: Any, item: Any) -> Bool
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `item` | Any |

## `any`

```intent
def any(lst: Any, pred: Any) -> Bool
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `pred` | Any |

## `all`

```intent
def all(lst: Any, pred: Any) -> Bool
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `pred` | Any |

## `take`

```intent
def take(lst: Any, n: Int)
    requires n >= 0
    ensures len(result) <= len(lst)
    ensures len(result) <= n
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `n` | Int |

**前置条件**:
- n >= 0

**后置条件**:
- len(result) <= len(lst)
- len(result) <= n

## `drop`

```intent
def drop(lst: Any, n: Int)
    requires n >= 0
    ensures len(result) <= len(lst)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `n` | Int |

**前置条件**:
- n >= 0

**后置条件**:
- len(result) <= len(lst)

## `zip`

```intent
def zip(a: Any, b: Any)
    ensures len(result) <= len(a) and len(result) <= len(b)
```

| 参数 | 类型 |
|---|---|
| `a` | Any |
| `b` | Any |

**后置条件**:
- len(result) <= len(a) and len(result) <= len(b)

## `map`

```intent
def map(lst: Any, f: Any)
    ensures len(result) == len(lst)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `f` | Any |

**后置条件**:
- len(result) == len(lst)

## `filter`

```intent
def filter(lst: Any, pred: Any)
    ensures len(result) <= len(lst)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `pred` | Any |

**后置条件**:
- len(result) <= len(lst)

## `reduce`

```intent
def reduce(lst: Any, f: Any, initial: Any)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `f` | Any |
| `initial` | Any |

