# time

## `current_timestamp`

> current_timestamp() — 返回当前 Unix 时间戳（浮点秒数）

```intent
def current_timestamp() -> Float
```

## `delay`

> delay(seconds) — 暂停指定秒数

```intent
def delay(seconds: Float) -> Int
```

| 参数 | 类型 |
|---|---|
| `seconds` | Float |

## `timestamp_ns`

> timestamp_ns() — 高精度纳秒时刻

```intent
def timestamp_ns() -> Float
```

## `elapsed_ms`

> elapsed_ms(start: Float) — 从 start 到现在的毫秒数

```intent
def elapsed_ms(start: Float) -> Float
```

| 参数 | 类型 |
|---|---|
| `start` | Float |

## `elapsed_ns`

> elapsed_ns(start: Float) — 纳秒级耗时

```intent
def elapsed_ns(start: Float) -> Float
```

| 参数 | 类型 |
|---|---|
| `start` | Float |

