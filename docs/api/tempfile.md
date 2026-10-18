# tempfile

## `mkdtemp`

> mkdtemp() → String  创建唯一临时目录(调用方负责清理)

```intent
def mkdtemp() -> String
```

## `mkstemp`

> mkstemp(prefix: String) → String  创建唯一临时文件, 返回路径

```intent
def mkstemp(prefix: String) -> String
```

| 参数 | 类型 |
|---|---|
| `prefix` | String |

## `tempdir`

> tempdir() → String  系统临时目录路径

```intent
def tempdir() -> String
```

