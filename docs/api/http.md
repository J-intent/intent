# http

## `get`

> get(url: String) → String  GET 请求，返回响应体

```intent
def get(url: String) -> String
```

| 参数 | 类型 |
|---|---|
| `url` | String |

## `post`

> post(url: String, body: String) → String  POST 文本，返回响应体

```intent
def post(url: String, body: String) -> String
```

| 参数 | 类型 |
|---|---|
| `url` | String |
| `body` | String |

## `get_json`

> get_json(url: String)  GET 并解析 JSON 响应为 Dict/List

```intent
def get_json(url: String)
```

| 参数 | 类型 |
|---|---|
| `url` | String |

## `post_json`

> post_json(url: String, value) → String  POST JSON 体，返回响应体

```intent
def post_json(url: String, value: Any) -> String
```

| 参数 | 类型 |
|---|---|
| `url` | String |
| `value` | Any |

## `serve_start`

> serve_start(port: Int) → Int  启动本地测试服务器，返回实际端口（0=系统分配）

```intent
def serve_start(port: Int) -> Int
```

| 参数 | 类型 |
|---|---|
| `port` | Int |

## `serve_stop`

> serve_stop(port: Int)  关闭测试服务器

```intent
def serve_stop(port: Int)
```

| 参数 | 类型 |
|---|---|
| `port` | Int |

