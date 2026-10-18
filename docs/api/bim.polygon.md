# polygon

## `make_rect_xy`

> 矩形多边形（XY 平面，从两点）

```intent
def make_rect_xy(min_pt: Point3D, max_pt: Point3D) -> Polygon
```

| 参数 | 类型 |
|---|---|
| `min_pt` | Point3D |
| `max_pt` | Point3D |

## `make_regular_xy`

> 正多边形（XY 平面，中心+半径+边数）

```intent
def make_regular_xy(center: Point3D, radius: Float, sides: Int) -> Polygon
```

| 参数 | 类型 |
|---|---|
| `center` | Point3D |
| `radius` | Float |
| `sides` | Int |

## class `Polyline`

- `init()`
- `from_list(pts: List)`
- `add(p: Point3D)`
- `count()` -> `Int`
- `is_closed()` -> `Bool`
- `length()` -> `Float`
- `segment(i: Int)` -> `Line3D`
- `bbox()` -> `BBox3D`
- `centroid()` -> `Point3D`

## class `Polygon`

- `init()`
- `from_list(pts: List)`
- `add(p: Point3D)`
- `count()` -> `Int`
- `area_xy()` -> `Float`
- `perimeter()` -> `Float`
- `centroid_xy()` -> `Point3D`
- `contains_xy(point: Point3D)` -> `Bool`
- `bbox()` -> `BBox3D`
- `is_convex_xy()` -> `Bool`

