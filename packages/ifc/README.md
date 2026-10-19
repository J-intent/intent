# ifc

Intent 官方包中的 BIM 领域工具：解析 IFC 风格构件标识。

标识约定为 `<IFC类名>-<样式/规格>-<数字序号>`，例如 `IFCWALL-standard-123`。

- `is_valid_identifier(s)`：校验三段结构、`IFC` 前缀、非空规格、纯数字序号。
- `parse(s)`：返回 `Result`；成功为 `Ok({class, kind, serial})`，失败为 `Err(原因)`。
- `ok_q(r)`：判断 `Result` 是否为 `Ok`，方便调用侧分支。
- `serial_number(s)`：把序号段转为 `Int`，调用前要求标识合法。
- `ifc_class(s)`：取类名段（如 `IFCWALL`）。
- `normalize(s)`：类名大写、规格小写，序号保持不变。

## 用法

```intent
import ifc;

match ifc.parse("IFCWALL-standard-123") {
    Ok(v) => print(v["class"]),
    Err(e) => print(e),
};
```

## 测试

```bash
python src/mini_intent.py --test packages/ifc/test_ifc.intent
```
