# glob

## `glob`

> glob(pattern: String) → List[String]  通配符匹配(空表=无匹配)
> 支持 * ? [seq]; 递归 ** 留待真实需求，反膨胀不做

```intent
def glob(pattern: String) -> List<String>
    requires len(pattern) > 0
```

| 参数 | 类型 |
|---|---|
| `pattern` | String |

**前置条件**:
- len(pattern) > 0

