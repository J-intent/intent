# Intent 收尾说明（2026-10-19）

> 一句话：**v2.31.0 收官，89/89 任务全 done，仓库干净可跑。自此暂停推进。**
> 这份文档是给「未来的自己」看的——想重启时不必重新考古。

## 1. 现在的状态（快照）

| 项 | 值 |
|---|---|
| 版本 | **v2.31.0**（commit `7ef0bac`，`--version` 已同步） |
| 测试 | **364/365 通过，0 失败，1 跳过** |
| 双引擎差分 | **80/80 一致**（解释器 vs 字节码 VM） |
| 代码量 | 14,356 行（解释器 13,409 + VM 947） |
| 标准库 | 45 模块（36 通用 + 9 BIM） |
| 工具链 | 16 个 tools（fmt/lint/doc/test/debug/coverage/bench/registry/签名/打包…） |
| 官方包 | 5 个（cli / logging / figlet / ifc / schedule） |
| 规范 | spec v1.30.0，**已知限制 39 条**（诚实清单） |
| 性能 | fib(25)：解释 3005ms / VM 788ms / **JIT 7ms**（= 1.01x CPython） |

## 2. 能用的 / 不能用的

**能用（今天就能干活）**
- 只读/计算类：BIM 数据整理、参数校验、报表、算法验证（标签排列、洞口合并逻辑）
- 契约校验：`requires` 写成业务规则，数据不满足直接拒
- 嵌入 Dynamo / pyRevit（`run_source` + `tools/revit_bridge.py`）

**不能用（别踩）**
- 写模型类工具（**无 Revit Transaction 回滚**，中途失败模型半改）
- 交付客户（单平台、无支持渠道）
- 日常脚本替代 Python（生态 5 包 vs 50 万）
- 对外卖（没人买编程语言）

## 3. 怎么跑起来（三条命令）

```bash
python src/mini_intent.py --version          # v2.31.0
python src/mini_intent.py --test             # 364/365
python src/mini_intent.py --types --show-inferred examples/contract.intent
```

## 4. 重启时先读什么

1. `docs/spec.md` —— 语言规范 + §6 已知限制（39 条，最省时间的入口）
2. `CHANGELOG.md` 顶部 —— v2.20 → v2.31 这十几轮到底改了什么
3. `D:/Desktop/LangForge/PROGRESS_PLAN.md` —— 89 任务、五轨道、判定口径
4. `docs/jit_design.md` —— JIT 方案选型与退路

## 5. 如果哪天想继续（未做清单）

| 优先级 | 事项 | 估时 |
|---|---|---|
| P0 | Revit 事务包裹（Transaction + RollBack + 嵌套检测）→ 解禁写模型工具 | 1 天 |
| P1 | 原子写（临时文件 + os.replace） | 0.5 天 |
| P1 | 长跑验证（1000 次循环内存曲线、5000 构件规模） | 1 天 |
| P2 | socket / selectors / ssl（真异步网络，替换工作线程方案） | 1 周 |
| P2 | JIT 扩到 list/dict 热路径 | 2–4 周 |
| P3 | 把「契约即类型」抽成 Python 包对外发布（真正可交付的形态） | 1–2 周 |

## 6. 交接提醒

- **无人值守已停**：LangForge 自动任务处于暂停状态；重开前先确认额度与目标
- 仓库：`github.com/J-intent/intent`（私有），工作区干净，无未推送提交
- 纪律沉淀：判定防真空（子串必须是实现独有词）、零漂移（先改文档再改代码）、
  大任务切 5–8 人日、子代理按文件边界并行

## 7. 一句话

它不是第二个 Python，也不需要是。
它证明了一件事：**契约可以成为类型，而且这件事在 14k 行里做得成。**
