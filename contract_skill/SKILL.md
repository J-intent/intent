# Intent Contract Skill

当用户要求你"用契约验证这段代码"、"加契约注释"、"intent contract check" 或类似的契约相关工作，按以下流程操作。

## 核心概念

Intent 契约系统是独立的代码验证层——**进门前签合同（requires），出门前验货（ensures）**。

### 三层验证模型

```
Layer 1: @requires     ← 调用方的责任（调用前检查）
Layer 2: 函数体        ← 作为核心的实现
Layer 3: @ensures      ← 被调用方的承诺（返回后验证）
```

## 工作流

### 当用户要求"给这段代码加契约"

1. **分析函数的意图**：它应该做什么？有什么隐含假设？
2. **写 @requires**：参数的合法范围、前置状态条件
3. **写 @ensures**：返回值的性质、后置状态条件
4. **用 contrarian 视角审查契约**：有没有遗漏的边界？有没有过度宽松的保证？
5. **输出带契约注释的完整代码**

### 契约注释格式

```python
# @requires: b != 0                    # 除法的前置条件
# @ensures: result * b == a            # 除法的数学保证
def divide(a: int, b: int) -> float:
    return a / b
```

```python
# @requires: index >= 0 and index < len(data)
# @ensures: result == data[index]
def safe_get(data: list, index: int):
    return data[index]
```

```python
# @requires: all(isinstance(x, (int, float)) for x in values)
# @ensures: result >= min(values) and result <= max(values)
def average(values: list) -> float:
    return sum(values) / len(values)
```

### 当用户要求"验证契约"

```bash
python3 contract_skill/intent_contract.py <target_file>
```

### 写契约的原则

1. **requires = 调用方的责任**：如果调用者没满足 requires，函数有权拒绝/崩溃
2. **ensures = 函数方的承诺**：只要 requires 满足，ensures 必须成立
3. **契约要可验证**：requires/ensures 中的表达式必须能被 eval 求值
4. **一次只加一个契约**：不要一次写 10 个 requires
5. **先写核心契约**：只写"如果违反，行为一定错"的条件
6. **不写冗余契约**：`isinstance(result, MyClass)` 这类静态类型已知的

### 常见契约模式

| 场景 | requires | ensures |
|------|----------|---------|
| 除法 | `b != 0` | `abs(result * b - a) < 1e-9` |
| 排序 | `all(isinstance(x, (int,float)) for x in data)` | `result == sorted(data)` |
| 开根号 | `x >= 0` | `abs(result*result - x) < 1e-9` |
| 索引访问 | `0 <= i < len(data)` | `result == data[i]` |
| 二分查找 | `sorted(data) == data` | `result == data.index(target)` |
| 文件读取 | `os.path.exists(path)` | `isinstance(result, str)` |
| 网络请求 | `url.startswith('http')` | `isinstance(result, dict) or 'error' in result` |

### 契约验证脚本位置

```
contract_skill/intent_contract.py
```

功能：
- 解析 Python 文件中的 `@requires` / `@ensures` 注释
- 自动生成测试输入验证契约
- 支持生成契约模板：`python3 intent_contract.py --generate file.py`

### 当用户问"这段代码有什么隐藏假设"

用 contrarian 视角分析：
1. 参数可能为 None 吗？
2. 参数可能为负数吗？
3. 参数可能为空列表/空字符串吗？
4. 参数可能包含意外类型吗？
5. 返回值可能为 None 吗？
6. 副作用的范围是什么？

然后生成对应的 @requires/@ensures 注释。

### Philosophy

"心学为体" — 函数不是孤立的代码块，是它和调用者的关系的总和。
"进门前签合同，出门前验货" — requires 是进门的约定，ensures 是出门的承诺。
"烦恼即菩提" — 错误不是要消灭的，是要显式表达的。有了契约，错误就变成了可预期的行为。
