# secrets

## `token_hex`

> token_hex(n: Int) → String  n 字节安全随机数的十六进制(2n 字符)

```intent
def token_hex(n: Int) -> String
    requires n >= 0
```

| 参数 | 类型 |
|---|---|
| `n` | Int |

**前置条件**:
- n >= 0

## `rand_below`

> rand_below(n: Int) → Int  [0, n) 安全随机整数

```intent
def rand_below(n: Int) -> Int
    requires n > 0
```

| 参数 | 类型 |
|---|---|
| `n` | Int |

**前置条件**:
- n > 0

## `choice`

> choice(lst: List) → Any  列表安全随机取一(空表抛 ValueError)

```intent
def choice(lst: Any)
    requires len(lst) > 0
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |

**前置条件**:
- len(lst) > 0

