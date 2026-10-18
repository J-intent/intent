# pathlib

## `_norm`

> _norm(path) → String  分隔符规范化(内部函数, 不导出)

```intent
def _norm(path: String) -> String
```

| 参数 | 类型 |
|---|---|
| `path` | String |

## `name`

> name(path: String) → String  末段文件名("a/b/c.intent" → "c.intent")

```intent
def name(path: String) -> String
    requires len(path) > 0
```

| 参数 | 类型 |
|---|---|
| `path` | String |

**前置条件**:
- len(path) > 0

## `stem`

> stem(path: String) → String  去扩展名的文件名(隐藏文件保全)

```intent
def stem(path: String) -> String
    requires len(path) > 0
```

| 参数 | 类型 |
|---|---|
| `path` | String |

**前置条件**:
- len(path) > 0

## `suffix`

> suffix(path: String) → String  末段扩展名(含点, 无则空串)

```intent
def suffix(path: String) -> String
    requires len(path) > 0
```

| 参数 | 类型 |
|---|---|
| `path` | String |

**前置条件**:
- len(path) > 0

## `parent`

> parent(path: String) → String  父目录(顶层返回 "")

```intent
def parent(path: String) -> String
    requires len(path) > 0
```

| 参数 | 类型 |
|---|---|
| `path` | String |

**前置条件**:
- len(path) > 0

## `join_path`

> join_path(a: String, b: String) → String  拼接两段(不重复尾分隔符)
> 命名避坑: 不叫 join — import 符号注入会遮蔽核心内置 join(sep, parts)

```intent
def join_path(a: String, b: String) -> String
    requires len(a) > 0 and len(b) > 0
```

| 参数 | 类型 |
|---|---|
| `a` | String |
| `b` | String |

**前置条件**:
- len(a) > 0 and len(b) > 0

## `with_suffix`

> with_suffix(path: String, ext: String) → String  替换扩展名(ext 含点)

```intent
def with_suffix(path: String, ext: String) -> String
    requires len(path) > 0 and len(ext) > 0
```

| 参数 | 类型 |
|---|---|
| `path` | String |
| `ext` | String |

**前置条件**:
- len(path) > 0 and len(ext) > 0

