"""
示例：用 Intent 契约标注的 Python 函数

每个函数有 @requires（进门条件）和 @ensures（出门保证）。
运行验证：
    python3 intent_contract.py contract_demo.py -v
生成模板：
    python3 intent_contract.py --generate contract_demo.py
"""

import math


# @requires: b != 0
# @ensures: abs(result * b - a) < 1e-9
def divide(a: float, b: float) -> float:
    """安全的除法——除数为零时契约拒绝调用"""
    return a / b


# @requires: x >= 0
# @ensures: abs(result * result - x) < 1e-9
def safe_sqrt(x: float) -> float:
    """安全的开根号——负数输入被契约拦截"""
    return math.sqrt(x)


# @requires: balance >= 0
# @requires: amount > 0
# @requires: amount <= balance
# @ensures: result >= 0
def withdraw(balance: float, amount: float) -> float:
    """取款——不能透支、不能取负数、不能取0"""
    return balance - amount


# @requires: 0 <= index < len(data)
# @ensures: result == data[index]
def safe_index(data: list, index: int):
    """安全的索引访问——越界被契约拒绝"""
    return data[index]


# @requires: len(values) > 0
# @requires: all(isinstance(v, (int, float)) for v in values)
# @ensures: result >= min(values) and result <= max(values)
def average(values: list) -> float:
    """计算平均值——空列表被契约拒绝"""
    return sum(values) / len(values)


# 故意违反契约的示例（验证时会报错）
# @requires: x > 0
# @ensures: result == x * 2
def bad_double(x: int) -> int:
    """Bug: 应该返回 x*2，实际返回 x+2"""
    return x + 2  # ← 契约 violation! asyncensures 说 result == x*2


if __name__ == '__main__':
    print("运行: python3 intent_contract.py contract_demo.py -v")
    print("来验证这些函数的契约")
