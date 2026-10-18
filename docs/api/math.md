# math

## `add`

```intent
def add(a: Int, b: Int) -> Int
    ensures result == a + b
```

| 参数 | 类型 |
|---|---|
| `a` | Int |
| `b` | Int |

**后置条件**:
- result == a + b

## `multiply`

```intent
def multiply(a: Int, b: Int) -> Int
    ensures result == a * b
```

| 参数 | 类型 |
|---|---|
| `a` | Int |
| `b` | Int |

**后置条件**:
- result == a * b

## `square`

```intent
def square(x: Int) -> Int
    ensures result >= 0
```

| 参数 | 类型 |
|---|---|
| `x` | Int |

**后置条件**:
- result >= 0

## `abs`

```intent
def abs(x: Int) -> Int
    ensures result >= 0
```

| 参数 | 类型 |
|---|---|
| `x` | Int |

**后置条件**:
- result >= 0

## `max`

```intent
def max(a: Int, b: Int) -> Int
    ensures result >= a and result >= b
```

| 参数 | 类型 |
|---|---|
| `a` | Int |
| `b` | Int |

**后置条件**:
- result >= a and result >= b

## `min`

```intent
def min(a: Int, b: Int) -> Int
    ensures result <= a and result <= b
```

| 参数 | 类型 |
|---|---|
| `a` | Int |
| `b` | Int |

**后置条件**:
- result <= a and result <= b

