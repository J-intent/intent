# cbwd

## `list_contains`

```intent
def list_contains(lst: Any, v: Any) -> Bool
```

| 参数 | 类型 |
|---|---|
| `lst` | Any |
| `v` | Any |

## `bbox_gap_mm`

> 3D 包围盒间隙(mm): 两盒在任一维度重叠 → 0; 否则三维分离距离的欧氏长度

```intent
def bbox_gap_mm(b1: Any, b2: Any) -> Float
    requires len(<SubscriptExpr>) == 3
    requires len(<SubscriptExpr>) == 3
    ensures result >= 0.0
```

| 参数 | 类型 |
|---|---|
| `b1` | Any |
| `b2` | Any |

**前置条件**:
- len(<SubscriptExpr>) == 3
- len(<SubscriptExpr>) == 3

**后置条件**:
- result >= 0.0

## `can_merge`

> 合并判定: 包围盒间隙 ≤ max_distance 且(圆柱时)表面间隙 ≤ max_distance
> 洞口 schema: {"min": [x,y,z], "max": [x,y,z], "cylindrical": Bool,
> "radius": Float, "center": [x,y,z]} — 单位 mm

```intent
def can_merge(o1: Any, o2: Any, max_distance_mm: Float) -> Bool
    requires max_distance_mm >= 0.0
```

| 参数 | 类型 |
|---|---|
| `o1` | Any |
| `o2` | Any |
| `max_distance_mm` | Float |

**前置条件**:
- max_distance_mm >= 0.0

## `_components`

> 连通分量核心: cands[i] = i 的候选下标表(已去重), DFS 遍历
> 分量集合与参考的 BFS 完全一致(连通分量唯一, 遍历顺序不影响成员)

```intent
def _components(n: Int, cands: Any, openings: Any, max_distance_mm: Float) -> List
```

| 参数 | 类型 |
|---|---|
| `n` | Int |
| `cands` | Any |
| `openings` | Any |
| `max_distance_mm` | Float |

## `_all_candidates`

> 全候选表: 每个下标的候选 = 其余全部(O(n²) 兜底路径, 参考 _find_merge_groups_slow)

```intent
def _all_candidates(n: Int) -> List
```

| 参数 | 类型 |
|---|---|
| `n` | Int |

## `_grid_candidates`

> 空间哈希候选表: 包围盒膨胀 D 后共格的下标(数学不漏: 3D 距离 ≤ D ⟺ 膨胀相交 ⟹ 共格)
> 网格边长沿用参考口径(D_ft > 0.5 ? D_ft : 0.5, 换算 mm: D > 152.4 ? D : 152.4)

```intent
def _grid_candidates(openings: Any, max_distance_mm: Float, cell: Float) -> List
```

| 参数 | 类型 |
|---|---|
| `openings` | Any |
| `max_distance_mm` | Float |
| `cell` | Float |

## `find_merge_groups`

> 洞口合并分组(参考 find_merge_groups 的默认路径: 空间哈希预筛)

```intent
def find_merge_groups(openings: Any, max_distance_mm: Float) -> List
    requires max_distance_mm >= 0.0
    ensures len(result) >= 1
```

| 参数 | 类型 |
|---|---|
| `openings` | Any |
| `max_distance_mm` | Float |

**前置条件**:
- max_distance_mm >= 0.0

**后置条件**:
- len(result) >= 1

## `find_merge_groups_slow`

> 兜底路径: O(n²) 全两两(参考 PRECISE_MERGE_PREFILTER=False)
> 与默认路径的分量集合必须一致 — 测试里互为对照

```intent
def find_merge_groups_slow(openings: Any, max_distance_mm: Float) -> List
    requires max_distance_mm >= 0.0
```

| 参数 | 类型 |
|---|---|
| `openings` | Any |
| `max_distance_mm` | Float |

**前置条件**:
- max_distance_mm >= 0.0

## `group_signature`

> 组签名: 组内下标升序连字符 + 全体排序(跨实现的稳定比较形态)

```intent
def group_signature(g: Any) -> String
```

| 参数 | 类型 |
|---|---|
| `g` | Any |

## `groups_signature`

```intent
def groups_signature(groups: Any) -> List
```

| 参数 | 类型 |
|---|---|
| `groups` | Any |

