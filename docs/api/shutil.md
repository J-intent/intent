# shutil

## `copy_file`

> copy_file(src: String, dst: String) → Bool  复制文件(覆盖式, 保留权限)

```intent
def copy_file(src: String, dst: String) -> Bool
    requires len(src) > 0 and len(dst) > 0
```

| 参数 | 类型 |
|---|---|
| `src` | String |
| `dst` | String |

**前置条件**:
- len(src) > 0 and len(dst) > 0

## `move`

> move(src: String, dst: String) → Bool  移动文件或目录(跨盘则复制后删)

```intent
def move(src: String, dst: String) -> Bool
    requires len(src) > 0 and len(dst) > 0
```

| 参数 | 类型 |
|---|---|
| `src` | String |
| `dst` | String |

**前置条件**:
- len(src) > 0 and len(dst) > 0

## `rmtree`

> rmtree(path: String) → Bool  递归删除目录(不存在抛 RuntimeError)

```intent
def rmtree(path: String) -> Bool
    requires len(path) > 0
```

| 参数 | 类型 |
|---|---|
| `path` | String |

**前置条件**:
- len(path) > 0

