# str

## `length`

```intent
def length(s: String) -> Int
    ensures result >= 0
```

| 参数 | 类型 |
|---|---|
| `s` | String |

**后置条件**:
- result >= 0

## `is_empty`

```intent
def is_empty(s: String) -> Bool
```

| 参数 | 类型 |
|---|---|
| `s` | String |

## `concat`

```intent
def concat(a: String, b: String) -> String
    ensures len(result) == len(a) + len(b)
```

| 参数 | 类型 |
|---|---|
| `a` | String |
| `b` | String |

**后置条件**:
- len(result) == len(a) + len(b)

## `repeat`

```intent
def repeat(s: String, n: Int) -> String
    requires n >= 0
    ensures len(result) == len(s) * n
```

| 参数 | 类型 |
|---|---|
| `s` | String |
| `n` | Int |

**前置条件**:
- n >= 0

**后置条件**:
- len(result) == len(s) * n

## `contains`

```intent
def contains(s: String, sub: String) -> Bool
```

| 参数 | 类型 |
|---|---|
| `s` | String |
| `sub` | String |

## `starts_with`

```intent
def starts_with(s: String, prefix: String) -> Bool
```

| 参数 | 类型 |
|---|---|
| `s` | String |
| `prefix` | String |

## `ends_with`

```intent
def ends_with(s: String, suffix: String) -> Bool
```

| 参数 | 类型 |
|---|---|
| `s` | String |
| `suffix` | String |

## `index_of`

```intent
def index_of(s: String, sub: String) -> Int
    ensures result >= -1
```

| 参数 | 类型 |
|---|---|
| `s` | String |
| `sub` | String |

**后置条件**:
- result >= -1

## `last_index_of`

```intent
def last_index_of(s: String, sub: String) -> Int
    ensures result >= -1
```

| 参数 | 类型 |
|---|---|
| `s` | String |
| `sub` | String |

**后置条件**:
- result >= -1

## `substring`

```intent
def substring(s: String, start: Int, end: Int) -> String
    requires start >= 0
    requires end <= len(s)
    requires start <= end
    ensures len(result) == end - start
```

| 参数 | 类型 |
|---|---|
| `s` | String |
| `start` | Int |
| `end` | Int |

**前置条件**:
- start >= 0
- end <= len(s)
- start <= end

**后置条件**:
- len(result) == end - start

## `to_upper`

```intent
def to_upper(s: String) -> String
    ensures len(result) == len(s)
```

| 参数 | 类型 |
|---|---|
| `s` | String |

**后置条件**:
- len(result) == len(s)

## `to_lower`

```intent
def to_lower(s: String) -> String
    ensures len(result) == len(s)
```

| 参数 | 类型 |
|---|---|
| `s` | String |

**后置条件**:
- len(result) == len(s)

## `replace`

```intent
def replace(s: String, old_val: String, new_val: String) -> String
```

| 参数 | 类型 |
|---|---|
| `s` | String |
| `old_val` | String |
| `new_val` | String |

## `cut`

```intent
def cut(s: String, sep: String)
```

| 参数 | 类型 |
|---|---|
| `s` | String |
| `sep` | String |

## `glue`

```intent
def glue(sep: String, parts: Any) -> String
```

| 参数 | 类型 |
|---|---|
| `sep` | String |
| `parts` | Any |

## `strip`

```intent
def strip(s: String) -> String
```

| 参数 | 类型 |
|---|---|
| `s` | String |

## `match_at`

```intent
def match_at(s: String, sub: String, pos: Int) -> Bool
```

| 参数 | 类型 |
|---|---|
| `s` | String |
| `sub` | String |
| `pos` | Int |

