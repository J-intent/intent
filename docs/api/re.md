# re

## `test`

> test(pattern: String, text: String) → Bool  是否存在匹配（search，不锚定）

```intent
def test(pattern: String, text: String) -> Bool
```

| 参数 | 类型 |
|---|---|
| `pattern` | String |
| `text` | String |

## `full_match`

> full_match(pattern: String, text: String) → Bool  整串匹配（两端锚定）

```intent
def full_match(pattern: String, text: String) -> Bool
```

| 参数 | 类型 |
|---|---|
| `pattern` | String |
| `text` | String |

## `find_all`

> find_all(pattern: String, text: String) → List  所有匹配子串（完整匹配）

```intent
def find_all(pattern: String, text: String) -> List
```

| 参数 | 类型 |
|---|---|
| `pattern` | String |
| `text` | String |

## `groups`

> groups(pattern: String, text: String) → List  首个匹配的捕获组（无匹配为空列表）

```intent
def groups(pattern: String, text: String) -> List
```

| 参数 | 类型 |
|---|---|
| `pattern` | String |
| `text` | String |

## `replace`

> replace(pattern: String, repl: String, text: String) → String  全局替换（\1 反向引用）

```intent
def replace(pattern: String, repl: String, text: String) -> String
```

| 参数 | 类型 |
|---|---|
| `pattern` | String |
| `repl` | String |
| `text` | String |

## `split`

> split(pattern: String, text: String) → List  按模式切分

```intent
def split(pattern: String, text: String) -> List
```

| 参数 | 类型 |
|---|---|
| `pattern` | String |
| `text` | String |

