# textwrap

## `wrap`

> wrap(text: String, width: Int) → List[String]  按词贪心换行

```intent
def wrap(text: String, width: Int) -> List<String>
    requires len(text) > 0 and width > 0
```

| 参数 | 类型 |
|---|---|
| `text` | String |
| `width` | Int |

**前置条件**:
- len(text) > 0 and width > 0

## `fill`

> fill(text: String, width: Int) → String  换行后用 chr(10) 重接

```intent
def fill(text: String, width: Int) -> String
    requires len(text) > 0 and width > 0
```

| 参数 | 类型 |
|---|---|
| `text` | String |
| `width` | Int |

**前置条件**:
- len(text) > 0 and width > 0

## `indent`

> indent(text: String, prefix: String) → String  每行加前缀

```intent
def indent(text: String, prefix: String) -> String
    requires len(text) > 0
```

| 参数 | 类型 |
|---|---|
| `text` | String |
| `prefix` | String |

**前置条件**:
- len(text) > 0

## `shorten`

> shorten(text: String, width: Int) → String  超长截断加省略号

```intent
def shorten(text: String, width: Int) -> String
    requires len(text) > 0 and width > 0
```

| 参数 | 类型 |
|---|---|
| `text` | String |
| `width` | Int |

**前置条件**:
- len(text) > 0 and width > 0

