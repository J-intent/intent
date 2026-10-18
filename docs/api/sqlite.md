# sqlite

## `open`

> open(path: String) → Int  打开数据库，返回句柄（":memory:" 为内存库）

```intent
def open(path: String) -> Int
```

| 参数 | 类型 |
|---|---|
| `path` | String |

## `exec`

> exec(handle: Int, sql: String) → Int  执行写操作（建表/插入/更新/删除），返回影响行数

```intent
def exec(handle: Int, sql: String) -> Int
```

| 参数 | 类型 |
|---|---|
| `handle` | Int |
| `sql` | String |

## `query`

> query(handle: Int, sql: String) → List  执行查询，返回行字典列表

```intent
def query(handle: Int, sql: String) -> List
```

| 参数 | 类型 |
|---|---|
| `handle` | Int |
| `sql` | String |

## `close`

> close(handle: Int)  关闭连接

```intent
def close(handle: Int)
```

| 参数 | 类型 |
|---|---|
| `handle` | Int |

