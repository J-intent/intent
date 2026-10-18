# json

## `parse`

> parse(json_str: String) — 解析 JSON 字符串

```intent
def parse(json_str: String)
```

| 参数 | 类型 |
|---|---|
| `json_str` | String |

## `stringify`

> stringify(value: Any) — 将值序列化为 JSON 字符串

```intent
def stringify(value: Any) -> String
```

| 参数 | 类型 |
|---|---|
| `value` | Any |

## `read_json`

> read_json(path: String) — 从文件读取并解析 JSON

```intent
def read_json(path: String)
```

| 参数 | 类型 |
|---|---|
| `path` | String |

## `write_json`

> write_json(path: String, value) — 将值序列化后写入文件

```intent
def write_json(path: String, value: Any) -> Int
```

| 参数 | 类型 |
|---|---|
| `path` | String |
| `value` | Any |

