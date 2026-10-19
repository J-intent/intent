# Intent C 扩展 SDK（I3a）

用 C 写 Intent 原生模块的最小 ABI。

## 文件

| 文件 | 作用 |
|---|---|
| `intent_api.h` | ABI v1 契约：`IntentModule` / `IntentFuncEntry` / 注册入口签名 |
| `example.c` | 示例扩展（`native_sum_range` / `native_square`） |
| `loader.py` | 加载器：`load_native(path)` → 读注册表 → 注入 `run_source` |
| `selftest.py` | 端到端自检（有编译器编译真 DLL；无编译器用 ctypes 回调表验证 ABI） |

## 构建

```bash
# MinGW / Git Bash
gcc -shared -O2 -o intent_example.dll example.c

# Linux / macOS
gcc -shared -fPIC -O2 -o libintent_example.so example.c

# MSVC（在 Developer Command Prompt 里）
cl /LD /O2 example.c
```

## 使用

```python
import sys
sys.path.insert(0, 'tools/csdk')
from loader import load_native
from mini_intent import run_source   # src/ 在搜索路径下

mod = load_native('intent_example.dll')
run_source('print(native_sum_range(1, 100));',
           inject_builtins=mod.functions())
```

## ABI v1 边界

- 值类型：`long long` 整数；元数 1 或 2（`arity=1` 时第二参未使用）
- 版本不匹配 → 加载器显式拒绝
- 浮点/字符串/结构体/回调映射留后续切片（spec §6 限制 30）
