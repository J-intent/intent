# datetime

## `now`

> now() → String  当前本地日期时间

```intent
def now() -> String
```

## `today`

> today() → String  今天日期

```intent
def today() -> String
```

## `parse`

> parse(iso: String) → String  校验并规范化（纯日期补 00:00:00）

```intent
def parse(iso: String) -> String
```

| 参数 | 类型 |
|---|---|
| `iso` | String |

## `format`

> format(iso: String, fmt: String) → String  按 strftime 格式串格式化

```intent
def format(iso: String, fmt: String) -> String
```

| 参数 | 类型 |
|---|---|
| `iso` | String |
| `fmt` | String |

## `add_days`

> add_days(iso: String, days: Int) → String  加天数（可为负）

```intent
def add_days(iso: String, days: Int) -> String
```

| 参数 | 类型 |
|---|---|
| `iso` | String |
| `days` | Int |

## `add_hours`

> add_hours(iso: String, hours: Int) → String  加小时（可为负）

```intent
def add_hours(iso: String, hours: Int) -> String
```

| 参数 | 类型 |
|---|---|
| `iso` | String |
| `hours` | Int |

## `diff_days`

> diff_days(a: String, b: String) → Int  a - b 的整天数（向下取整）

```intent
def diff_days(a: String, b: String) -> Int
```

| 参数 | 类型 |
|---|---|
| `a` | String |
| `b` | String |

## `diff_seconds`

> diff_seconds(a: String, b: String) → Int  a - b 的秒数

```intent
def diff_seconds(a: String, b: String) -> Int
```

| 参数 | 类型 |
|---|---|
| `a` | String |
| `b` | String |

## `weekday`

> weekday(iso: String) → Int  星期几（0=周一 … 6=周日）

```intent
def weekday(iso: String) -> Int
```

| 参数 | 类型 |
|---|---|
| `iso` | String |

## `parts`

> parts(iso: String) → Dict  年月日时分秒字典

```intent
def parts(iso: String) -> Dict
```

| 参数 | 类型 |
|---|---|
| `iso` | String |

## `timestamp`

> timestamp(iso: String) → Float  Unix 时间戳（按本地时区解释）

```intent
def timestamp(iso: String) -> Float
```

| 参数 | 类型 |
|---|---|
| `iso` | String |

## `from_timestamp`

> from_timestamp(ts: Float) → String  Unix 时间戳 → 本地 ISO 字符串

```intent
def from_timestamp(ts: Float) -> String
```

| 参数 | 类型 |
|---|---|
| `ts` | Float |

## `to_timezone`

> to_timezone(iso: String, offset_hours: Int) → String
> 输入按 UTC 解释，返回 offset_hours 时区的墙上时间（(14:00, +8) → 22:00）

```intent
def to_timezone(iso: String, offset_hours: Int) -> String
```

| 参数 | 类型 |
|---|---|
| `iso` | String |
| `offset_hours` | Int |

