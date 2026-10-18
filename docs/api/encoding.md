# encoding

## `base64_encode`

> base64_encode(text: String) → String  标准 base64（含 = 补齐）

```intent
def base64_encode(text: String) -> String
```

| 参数 | 类型 |
|---|---|
| `text` | String |

## `base64_decode`

> base64_decode(data: String) → String  base64 解码（非法输入抛 ValueError）

```intent
def base64_decode(data: String) -> String
```

| 参数 | 类型 |
|---|---|
| `data` | String |

## `gzip_compress`

> gzip_compress(text: String) → String  gzip 压缩 → base64 文本

```intent
def gzip_compress(text: String) -> String
```

| 参数 | 类型 |
|---|---|
| `text` | String |

## `gzip_decompress`

> gzip_decompress(data: String) → String  base64 → gzip 解压（非法输入抛 ValueError）

```intent
def gzip_decompress(data: String) -> String
```

| 参数 | 类型 |
|---|---|
| `data` | String |

## `urlencode`

> urlencode(text: String) → String  百分号编码（UTF-8，空格 → %20）

```intent
def urlencode(text: String) -> String
```

| 参数 | 类型 |
|---|---|
| `text` | String |

## `urldecode`

> urldecode(data: String) → String  百分号解码（非法输入抛 ValueError）

```intent
def urldecode(data: String) -> String
```

| 参数 | 类型 |
|---|---|
| `data` | String |

