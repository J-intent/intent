# figlet

Intent 官方包中的 ASCII 大字横幅工具，使用 5x5 点阵字模（`#` 与空格）。

- 内置字模：`A`、`B`、`C`、`D`、`E` 与空格，满足最小演示集。
- `glyph(ch)` 返回单个字符的 5 行点阵；未收录字符返回空心方框占位。
- `is_supported(ch)` 判断字符是否有专用字模。
- `render(text)` 把整段文本横向拼接成 5 行，每行宽度为 `5 * 字符数`。
- `banner(text)` 在 `render` 基础上用换行拼接，可直接 `print` 输出。
- `width(text)` 返回横幅列数，便于对齐排版。

## 用法

```intent
import figlet;

print(figlet.banner("ABE"));
assert figlet.width("AB") == 10, "宽度按 5 列/字符计算";
```

## 测试

```bash
python src/mini_intent.py --test packages/figlet/test_figlet.intent
```
