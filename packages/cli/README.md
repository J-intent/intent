# cli

Intent 官方包中的极简命令行参数解析工具，纯 Intent 实现、零外部依赖。

- `parse_args(argv)` 把参数拆成子命令、flag、位置参数三部分。
- `is_flag` / `flag_name` 负责识别与去前缀（`--verbose` → `verbose`）。
- `has_flag` / `command_of` / `args_of` 提供只读访问。
- `validate(parsed, allowed)` 用 `Result` 返回校验结果：`Ok(parsed)` 或 `Err(原因)`。
- 所有导出函数都带有 `requires` 或 `ensures` 契约，越界输入会显式失败。

## 用法

```intent
import cli;

let parsed = cli.parse_args(["build", "main.intent", "--verbose"]);
assert cli.command_of(parsed) == "build", "子命令";
assert cli.has_flag(parsed, "verbose"), "flag";
```

## 测试

```bash
python src/mini_intent.py --test packages/cli/test_cli.intent
```
