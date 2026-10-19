# inspect

## `getmembers`

> getmembers(obj) → Dict[name, value] — 枚举全部可见成员(字段+方法)

```intent
def getmembers(obj: Any)
```

| 参数 | 类型 |
|---|---|
| `obj` | Any |

## `get`

> get(obj, name, default) — 安全读: 不存在返默认值, 不抛

```intent
def get(obj: Any, name: Any, default: Any)
```

| 参数 | 类型 |
|---|---|
| `obj` | Any |
| `name` | Any |
| `default` | Any |

## `attr_names`

> attr_names(obj) → List — dir 的直传(枚举字段+方法名, 排序)

```intent
def attr_names(obj: Any)
```

| 参数 | 类型 |
|---|---|
| `obj` | Any |

## `is_field`

> is_field(obj, name) — 名是否为数据字段(存在且不可调用)

```intent
def is_field(obj: Any, name: Any)
```

| 参数 | 类型 |
|---|---|
| `obj` | Any |
| `name` | Any |

## `is_method`

> is_method(obj, name) — 名是否为方法(存在且可调用)

```intent
def is_method(obj: Any, name: Any)
```

| 参数 | 类型 |
|---|---|
| `obj` | Any |
| `name` | Any |

