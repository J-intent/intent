# pipe_routing

## `dist_3d`

> 三维距离

```intent
def dist_3d(x1: Float, y1: Float, z1: Float, x2: Float, y2: Float, z2: Float) -> Float
```

| 参数 | 类型 |
|---|---|
| `x1` | Float |
| `y1` | Float |
| `z1` | Float |
| `x2` | Float |
| `y2` | Float |
| `z2` | Float |

## `manhattan_3d`

> 曼哈顿距离

```intent
def manhattan_3d(x1: Float, y1: Float, z1: Float, x2: Float, y2: Float, z2: Float) -> Float
```

| 参数 | 类型 |
|---|---|
| `x1` | Float |
| `y1` | Float |
| `z1` | Float |
| `x2` | Float |
| `y2` | Float |
| `z2` | Float |

## `point_collides`

> 点是否在任一障碍物内 (带管道半径的安全余量)

```intent
def point_collides(x: Float, y: Float, z: Float, obstacles: Any, margin: Float) -> Int
```

| 参数 | 类型 |
|---|---|
| `x` | Float |
| `y` | Float |
| `z` | Float |
| `obstacles` | Any |
| `margin` | Float |

## `segment_collides`

> 线段-障碍物碰撞检测

```intent
def segment_collides(a: Point3D, b: Point3D, obstacles: Any, margin: Float) -> Int
```

| 参数 | 类型 |
|---|---|
| `a` | Point3D |
| `b` | Point3D |
| `obstacles` | Any |
| `margin` | Float |

## `directions`

> 六个方向 (正交)

```intent
def directions()
```

## `find_best`

> 在开放列表中找 f 值最小的节点 index

```intent
def find_best(open_list: Any) -> Int
```

| 参数 | 类型 |
|---|---|
| `open_list` | Any |

## `rebuild_path`

> 重建路径: 从终点回溯到起点

```intent
def rebuild_path(nodes: Any, end_x: Float, end_y: Float, end_z: Float, start_x: Float, start_y: Float, start_z: Float)
```

| 参数 | 类型 |
|---|---|
| `nodes` | Any |
| `end_x` | Float |
| `end_y` | Float |
| `end_z` | Float |
| `start_x` | Float |
| `start_y` | Float |
| `start_z` | Float |

## `route_pipe`

```intent
def route_pipe(start: Point3D, end: Point3D, obstacles: Any, diameter: Float, grid_spacing: Float)
```

| 参数 | 类型 |
|---|---|
| `start` | Point3D |
| `end` | Point3D |
| `obstacles` | Any |
| `diameter` | Float |
| `grid_spacing` | Float |

## `simplify_path`

```intent
def simplify_path(path: Any, obstacles: Any, margin: Float)
```

| 参数 | 类型 |
|---|---|
| `path` | Any |
| `obstacles` | Any |
| `margin` | Float |

## `path_to_pipes`

```intent
def path_to_pipes(path: Any, diameter: Float, thickness: Float)
```

| 参数 | 类型 |
|---|---|
| `path` | Any |
| `diameter` | Float |
| `thickness` | Float |

## `routing_total_length`

```intent
def routing_total_length(segments: Any, elbows: Any) -> Float
```

| 参数 | 类型 |
|---|---|
| `segments` | Any |
| `elbows` | Any |

## `routing_material_list`

```intent
def routing_material_list(segments: Any, elbows: Any)
```

| 参数 | 类型 |
|---|---|
| `segments` | Any |
| `elbows` | Any |

## class `RoutingNode`

- `init()`
- `f()` -> `Float`
- `key(snap: Float)` -> `String`
- `copy()` -> `RoutingNode`
- `set(x: Float, y: Float, z: Float, g: Float, h: Float, px: Float, py: Float, pz: Float)`
- `point()` -> `Point3D`

