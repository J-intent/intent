# csv

## `parse_line`

> parse_line(line: String) → List[String]  解析单行(引号/转义/空字段)

```intent
def parse_line(line: String) -> List<String>
```

| 参数 | 类型 |
|---|---|
| `line` | String |

## `serialize_row`

> serialize_row(fields: List[String]) → String  生成单行(按需加引号)
> 含逗号/引号/换行的字段加引号包裹, 引号翻倍转义

```intent
def serialize_row(fields: List<String>) -> String
```

| 参数 | 类型 |
|---|---|
| `fields` | List<String> |

## `parse`

> parse(text: String) → List[List[String]]  解析多行文本(空文本→空表)

```intent
def parse(text: String) -> List<List<String>>
```

| 参数 | 类型 |
|---|---|
| `text` | String |

