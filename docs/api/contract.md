# contract

## `require_positive`

> ══ 前置条件辅助 ══
> 正数检查

```intent
def require_positive(n: Int) -> Bool
```

| 参数 | 类型 |
|---|---|
| `n` | Int |

## `require_non_negative`

```intent
def require_non_negative(n: Int) -> Bool
```

| 参数 | 类型 |
|---|---|
| `n` | Int |

## `require_in_range`

```intent
def require_in_range(n: Int, lo: Int, hi: Int) -> Bool
```

| 参数 | 类型 |
|---|---|
| `n` | Int |
| `lo` | Int |
| `hi` | Int |

## `require_divisor_non_zero`

> 除数非零

```intent
def require_divisor_non_zero(d: Int) -> Bool
```

| 参数 | 类型 |
|---|---|
| `d` | Int |

## `require_non_empty`

> 列表/字符串非空

```intent
def require_non_empty(xs: Any) -> Bool
```

| 参数 | 类型 |
|---|---|
| `xs` | Any |

## `ensure_result_not_null`

> ══ 后置条件辅助 ══
> 结果非空（用于返回列表的函数）

```intent
def ensure_result_not_null(result: Any) -> Bool
```

| 参数 | 类型 |
|---|---|
| `result` | Any |

## `ensure_result_in_range`

> 结果在合法范围内

```intent
def ensure_result_in_range(result: Int, lo: Int, hi: Int) -> Bool
```

| 参数 | 类型 |
|---|---|
| `result` | Int |
| `lo` | Int |
| `hi` | Int |

## `ensure_length_le_original`

> 列表长度不变（适用于 filter/take 类操作）

```intent
def ensure_length_le_original(result_len: Int, original_len: Int) -> Bool
```

| 参数 | 类型 |
|---|---|
| `result_len` | Int |
| `original_len` | Int |

## `ensure_result_positive`

> 计算结果与输入关系

```intent
def ensure_result_positive(result: Int) -> Bool
```

| 参数 | 类型 |
|---|---|
| `result` | Int |

