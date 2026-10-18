# fs

## `ls`

> ls(path: String) → List[String]  列出目录内容

```intent
def ls(path: String) -> List
```

| 参数 | 类型 |
|---|---|
| `path` | String |

## `exists`

> exists(path: String) → Bool  检查路径是否存在

```intent
def exists(path: String) -> Bool
```

| 参数 | 类型 |
|---|---|
| `path` | String |

## `is_directory`

> is_directory(path: String) → Bool

```intent
def is_directory(path: String) -> Bool
```

| 参数 | 类型 |
|---|---|
| `path` | String |

## `is_regular_file`

> is_regular_file(path: String) → Bool

```intent
def is_regular_file(path: String) -> Bool
```

| 参数 | 类型 |
|---|---|
| `path` | String |

## `mkdir`

> mkdir(path: String)  创建目录(含父目录)

```intent
def mkdir(path: String)
```

| 参数 | 类型 |
|---|---|
| `path` | String |

## `remove`

> remove(path: String)  删除文件

```intent
def remove(path: String)
```

| 参数 | 类型 |
|---|---|
| `path` | String |

## `read_all`

> read_all(path: String) → String  读取整个文件为字符串

```intent
def read_all(path: String) -> String
    requires file_exists(path)
```

| 参数 | 类型 |
|---|---|
| `path` | String |

**前置条件**:
- file_exists(path)

## `write_all`

> write_all(path: String, content: String)  写入文件

```intent
def write_all(path: String, content: String)
```

| 参数 | 类型 |
|---|---|
| `path` | String |
| `content` | String |

## `size_bytes`

> size_bytes(path: String) → Int  文件大小(字节)

```intent
def size_bytes(path: String) -> Int
    requires file_exists(path)
```

| 参数 | 类型 |
|---|---|
| `path` | String |

**前置条件**:
- file_exists(path)

## `mtime`

> mtime(path: String) → Float  最后修改时间(Unix时间戳)

```intent
def mtime(path: String) -> Float
    requires file_exists(path)
```

| 参数 | 类型 |
|---|---|
| `path` | String |

**前置条件**:
- file_exists(path)

