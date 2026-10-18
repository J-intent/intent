# 为 Intent 贡献

> 心学为体，禅道为翼，马哲为用
> 欢迎事上磨炼。本文是贡献者的起点：环境、纪律、流程、架构。

## 1. 开发环境

- Python 3.11+（`tomllib` 依赖，包管理与注册表需要；3.12 为 CI 基线）
- 无第三方运行时依赖——解释器本体纯标准库
- 克隆后直接可用：

```bash
python src/mini_intent.py examples/hello.intent     # 跑示例
python src/mini_intent.py -r                        # REPL
python src/mini_intent.py --test                    # 全量回归(126 用例)
```

## 2. 项目纪律（不可协商）

1. **函数带契约**：`requires`（进门条件）/ `ensures`（出门承诺）。
   契约是一等公民——`ContractError` 可被定向 catch。
2. **改动同步 `docs/spec.md`**：spec 是权威规范，从实现反向提取。
   改了语言行为就改 spec，版本号随 feature 升（语义化版本）。
3. **测试随功能增长**：每个新功能/新 std 模块配 `tests/test_*.intent`。
   测试文件内 `def test_xxx()` 即用例，`assert(cond, msg)` 断言。
4. **反膨胀**：方案变大时砍回核心。先分析根因再动手，不堆补丁。
5. **零漂移**：`CHANGELOG.md` / `docs/spec.md` / 工具链判定同步更新。

## 3. 提交流程

```bash
# 1. 本地全绿再提交
python src/mini_intent.py --test
python tools/vm_diff.py                 # VM 与解释器 56 文件差分
python tools/lsp/smoke_test.py          # LSP 三件套
python tools/gen_docs_site.py --check   # 文档站转换

# 2. 提交信息: <类型>: <一句话>（类型 = feat/fix/refactor/docs/test/chore）
git commit -m "feat: std.encoding base64/gzip/urlencode"
```

CI（`.github/workflows/ci.yml`）自动执行：全库语法检查 → 回归测试 →
linter → doc 生成 → formatter 幂等抽查 → VM 行为对照 → 性能回归门禁
（VM 不得慢于解释器）。

## 4. 架构导览

```
src/
  mini_intent.py        解释器主体(~8600 行): 词法→解析→语义→树遍历执行
                        + std builtin 注册表(Interpreter._setup_builtins)
  intent_bytecode.py    字节码编译器 + 栈式 VM(M10)
  intent_resolver.py    语义分析遍(作用域深度)
  mini_intent_debug.py  v1.2 历史存档解释器(勿改, 仅参考)
std/                   标准库 .intent 模块(bim/ 为 BIM 领域子库)
tests/                 回归测试(test_*.intent)
examples/              示例与 8 章教程
docs/                  spec(权威规范) / chapter_*(教程) / api/(标准库参考) / site/(文档站)
tools/
  vm_diff.py           VM vs 解释器差分
  gen_docs_site.py     文档站生成( --api 生成标准库参考 )
  lsp/                 LSP 服务器 + 冒烟
  registry.py          包注册表(publish/list/install)
```

### 加一个 std 模块的完整清单

1. `std/<mod>.intent`：`def` 函数 + 注释签名（类型即契约文档）
2. `src/mini_intent.py`：`_setup_builtins` 注册 `<前缀>_*` builtin +
   实现方法（参数校验 → TypeError，非法值 → ValueError）
3. `tests/test_stdlib_<mod>.intent`：round-trip + 已知向量 + 非法输入
4. `docs/spec.md` §标准库章节登记；`CHANGELOG.md` 记版本
5. `python tools/gen_docs_site.py --api` 重新生成参考页

## 5. 工具链速查

| 命令 | 用途 |
|---|---|
| `--check <file>` | 只解析不执行（CI 前置，语法错 exit 2） |
| `--lint <file>` | 静态检查：let 重赋值 / 空 catch / 无契约导出 / 未用 import |
| `--fmt <file>` | 格式化（幂等） |
| `--doc <file>` | 生成模块 markdown 文档 |
| `--test [dir]` | 运行测试（默认 tests/） |
| `--debug <file>` | 调试器：断点/单步/变量检视/调用栈 |
| `--compile <file> --run-vm` | 字节码编译 + VM 执行 |
| `tools/registry.py` | 包发布/安装（本地注册表） |
| `tools/gen_docs_site.py` | 文档站 + 标准库参考 |

## 6. 治理

- **维护者**：阿J（吴建基）——方向与最终决策
- **自动化**：LangForge v2 DAG 引擎按五轨道（核心/标准库/工具链/稳定性/生态）
  调度任务，每任务命令级判定；无人值守轮连续推进
- **决策记录**：重大设计决策（表示法、语义边界）进 `docs/spec.md`
  的「状态标注」与 CHANGELOG，不靠口口相传
- **已知边界**（有意不为）：整除运算符 `//` 被行注释抢占（源码不可达，
  用 `/` 真除法）；`str(inf)` 抛 OverflowError（可捕获）；深递归上限约
  千层（RecursionError 可捕获）——修这些前先读 spec 的状态标注

## 7. 行为准则

对事不对人；先复现再发言；反对过度工程；漂亮话不如可执行判定。
