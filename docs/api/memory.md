# memory

## `mem_live`

> mem_live() → Int  当前存活容器对象数

```intent
def mem_live() -> Int
    ensures result >= 0
```

**后置条件**:
- result >= 0

## `alloc_total`

> alloc_total() → Int  累计创建容器对象数

```intent
def alloc_total() -> Int
    ensures result >= 0
```

**后置条件**:
- result >= 0

## `mem_stats`

> mem_stats() → Dict  统计字典(live/alloc_total/reclaim_total/by_type)

```intent
def mem_stats()
```

## `gc_collect`

> gc_collect() → Int  触发循环垃圾回收, 返回本次回收容器数

```intent
def gc_collect() -> Int
    ensures result >= 0
```

**后置条件**:
- result >= 0

## `ref_count`

> ref_count(obj) → Int  对象的宿主引用计数(诊断观测值)

```intent
def ref_count(obj: Any) -> Int
    ensures result >= 1
```

| 参数 | 类型 |
|---|---|
| `obj` | Any |

**后置条件**:
- result >= 1

