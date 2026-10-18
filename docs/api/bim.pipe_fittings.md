# pipe_fittings

## `check_pipe_network`

> 批量检测：返回所有碰撞对

```intent
def check_pipe_network(segments: Any)
```

| 参数 | 类型 |
|---|---|
| `segments` | Any |

## `pipe_network_bbox`

```intent
def pipe_network_bbox(segments: Any) -> BBox3D
```

| 参数 | 类型 |
|---|---|
| `segments` | Any |

## class `PipeTee`

- `init()`
- `create(center: Point3D, run_dir: Vector3D, branch_dir: Vector3D, main_diameter: Float, branch_diameter: Float, thickness: Float)`
- `get_segments()`
- `is_equal_tee()` -> `Int`

## class `PipeReducer`

- `init()`
- `create_concentric(start: Point3D, end: Point3D, big_diameter: Float, small_diameter: Float, thickness: Float)`
- `create_eccentric(start: Point3D, end: Point3D, big_diameter: Float, small_diameter: Float, thickness: Float, offset_dir: Vector3D)`
- `get_segments()`

## class `PipeValve`

- `init()`
- `create(start: Point3D, end: Point3D, diameter: Float, valve_type: String)`
- `get_direction()` -> `Vector3D`
- `bbox()` -> `BBox3D`

