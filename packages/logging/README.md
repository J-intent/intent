# logging

Intent 官方包中的极简日志工具：只做级别过滤与行格式化，日志收集在内存列表中。

- 四个级别：`DEBUG`(10)、`INFO`(20)、`WARN`(30)、`ERROR`(40)。
- `level_value(name)` 把级别名转成可比较的整数，非法级别触发契约失败。
- `should_log(threshold, level)` 判断当前阈值下是否输出。
- `format_line(level, message)` 产出 `[LEVEL] message` 形式的单行文本。
- `Logger(threshold)` 提供 `log` / `count` / `text` 三个方法，内部维护行列表。
- 不写文件、不依赖外部库，便于在测试或嵌入式场景中使用。

## 用法

```intent
import logging;

let logger = logging.Logger(20);
logger.log("DEBUG", "不会出现");
logger.log("INFO", "服务启动");
assert logger.count() == 1, "DEBUG 被过滤";
```

## 测试

```bash
python src/mini_intent.py --test packages/logging/test_logging.intent
```
