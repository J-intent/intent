# hmac

## `sha256`

> sha256(key: String, msg: String) → String  HMAC-SHA256 十六进制摘要

```intent
def sha256(key: String, msg: String) -> String
    requires len(key) > 0
```

| 参数 | 类型 |
|---|---|
| `key` | String |
| `msg` | String |

**前置条件**:
- len(key) > 0

## `sha256_verify`

> sha256_verify(key: String, msg: String, sig: String) → Bool
> 常量时间比对签名——防时序侧信道，不等即假

```intent
def sha256_verify(key: String, msg: String, sig: String) -> Bool
    requires len(key) > 0 and len(sig) > 0
```

| 参数 | 类型 |
|---|---|
| `key` | String |
| `msg` | String |
| `sig` | String |

**前置条件**:
- len(key) > 0 and len(sig) > 0

