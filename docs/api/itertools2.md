# itertools2

## `permutations`

> permutations — 全排列：每个元素都曾领头，物各有其位

```intent
def permutations(lst: Any)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |

## `combinations`

> combinations — k 组合：选与不选之间，穷尽所有 subsets

```intent
def combinations(lst: Any, k: Int)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `k` | Int |

## `product`

> product — 笛卡尔积：两集合的所有姻缘

```intent
def product(a: Any, b: Any)
```

| 参数 | 类型 |
|---|---|
| `a` | Any |
| `b` | Any |

## `heappush`

> heappush — 入堆：小者浮前

```intent
def heappush(heap: Any, x: Any)
```

| 参数 | 类型 |
|---|---|
| `heap` | Any |
| `x` | Any |

## `heappop`

> heappop — 出堆：返回 [最小值, 剩余堆]；空堆返回 Err

```intent
def heappop(heap: Any)
```

| 参数 | 类型 |
|---|---|
| `heap` | Any |

## `bisect_left`

> bisect_left — x 的左插入点（相等元素之前）

```intent
def bisect_left(lst: Any, x: Any) -> Int
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `x` | Any |

## `bisect_right`

> bisect_right — x 的右插入点（相等元素之后）

```intent
def bisect_right(lst: Any, x: Any) -> Int
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `x` | Any |

## `insort`

> insort — 有序插入：位定而后安

```intent
def insort(lst: Any, x: Any)
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `x` | Any |

## class `MinHeap`

- `init()`
- `push(x: Any)`
- `pop()`
- `peek()`
- `size()` -> `Int`
- `is_empty()` -> `Bool`

## class `Deque`

- `init()`
- `append(x: Any)`
- `appendleft(x: Any)`
- `pop()`
- `popleft()`
- `size()` -> `Int`
- `is_empty()` -> `Bool`

## class `DefaultDict`

- `init(factory: Any)`
- `get(key: Any)`
- `set(key: Any, value: Any)`
- `has(key: Any)` -> `Bool`
- `keys()`
- `size()` -> `Int`

## class `ChainMap`

- `init()`
- `push(d: Any)`
- `get(key: Any)`
- `has(key: Any)` -> `Bool`
- `size()` -> `Int`

