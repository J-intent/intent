# pipe

## `pipes_collide`

> 两段管道是否碰撞（圆柱体近似）

```intent
def pipes_collide(a: PipeSegment, b: PipeSegment) -> Int
```

| 参数 | 类型 |
|---|---|
| `a` | PipeSegment |
| `b` | PipeSegment |

## `segment_distance`

> 两条线段的最短距离

```intent
def segment_distance(a1: Point3D, a2: Point3D, b1: Point3D, b2: Point3D) -> Float
```

| 参数 | 类型 |
|---|---|
| `a1` | Point3D |
| `a2` | Point3D |
| `b1` | Point3D |
| `b2` | Point3D |

## `clamp`

> 钳制值到 [lo, hi]

```intent
def clamp(val: Float, lo: Float, hi: Float) -> Float
```

| 参数 | 类型 |
|---|---|
| `val` | Float |
| `lo` | Float |
| `hi` | Float |

## `pipe_slope_percent`

> 计算管道的坡度 (百分比，如 0.02 = 2%)

```intent
def pipe_slope_percent(seg: PipeSegment) -> Float
```

| 参数 | 类型 |
|---|---|
| `seg` | PipeSegment |

## `pipe_slope_ratio`

> 计算管道的坡度 (即 1:N，如 1:50)

```intent
def pipe_slope_ratio(seg: PipeSegment) -> Float
```

| 参数 | 类型 |
|---|---|
| `seg` | PipeSegment |

## `create_pipe`

> 创建从起点到终点的直管

```intent
def create_pipe(start: Point3D, end: Point3D, diameter: Float, thickness: Float) -> PipeSegment
```

| 参数 | 类型 |
|---|---|
| `start` | Point3D |
| `end` | Point3D |
| `diameter` | Float |
| `thickness` | Float |

## `offset_up`

> 向上翻弯（常用场景：绕过上方障碍）

```intent
def offset_up(a: Point3D, b: Point3D, pipe_dir: Vector3D, height: Float, diameter: Float, thickness: Float) -> PipeOffset
```

| 参数 | 类型 |
|---|---|
| `a` | Point3D |
| `b` | Point3D |
| `pipe_dir` | Vector3D |
| `height` | Float |
| `diameter` | Float |
| `thickness` | Float |

## `offset_side`

> 侧向翻弯

```intent
def offset_side(a: Point3D, b: Point3D, pipe_dir: Vector3D, side_dir: Vector3D, distance: Float, diameter: Float, thickness: Float) -> PipeOffset
```

| 参数 | 类型 |
|---|---|
| `a` | Point3D |
| `b` | Point3D |
| `pipe_dir` | Vector3D |
| `side_dir` | Vector3D |
| `distance` | Float |
| `diameter` | Float |
| `thickness` | Float |

## `offset_total_length`

> 计算翻弯总长度

```intent
def offset_total_length(offset: PipeOffset) -> Float
```

| 参数 | 类型 |
|---|---|
| `offset` | PipeOffset |

## `offset_material_list`

> 计算翻弯材料清单: 返回 [总长, 上升段长, 平移段长, 下降段长]

```intent
def offset_material_list(offset: PipeOffset)
```

| 参数 | 类型 |
|---|---|
| `offset` | PipeOffset |

## class `PipeSegment`

- `init()`
- `create(start: Point3D, end: Point3D, diameter: Float, thickness: Float)`
- `length()` -> `Float`
- `direction()` -> `Vector3D`
- `mid_point()` -> `Point3D`
- `bbox()` -> `BBox3D`
- `inner_radius()` -> `Float`
- `outer_radius()` -> `Float`

## class `PipeElbow`

- `init()`
- `create(from_dir: Vector3D, to_dir: Vector3D, diameter: Float, radius: Float, center: Point3D)`
- `arc_length()` -> `Float`

## class `PipeOffset`

- `init()`
- `create(a_point: Point3D, b_point: Point3D, pipe_dir: Vector3D, offset_dir: Vector3D, offset_dist: Float, elbow_radius: Float, diameter: Float, thickness: Float)`
- `get_segments()`
- `get_elbows()`

