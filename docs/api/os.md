# os

## `getenv`

> getenv(key: String) → String  读取环境变量

```intent
def getenv(key: String) -> String
```

| 参数 | 类型 |
|---|---|
| `key` | String |

## `curdir`

> curdir() → String  当前工作目录

```intent
def curdir() -> String
```

## `chdir`

> chdir(path: String)  切换目录

```intent
def chdir(path: String)
```

| 参数 | 类型 |
|---|---|
| `path` | String |

## `run`

> run(cmd: String) → String  执行 shell 命令

```intent
def run(cmd: String) -> String
```

| 参数 | 类型 |
|---|---|
| `cmd` | String |

## `sys_platform`

> sys_platform() → String  操作系统平台

```intent
def sys_platform() -> String
```

## `home_dir`

> home_dir() → String  用户主目录

```intent
def home_dir() -> String
```

