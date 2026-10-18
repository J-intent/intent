# solid

## `bbox_intersects`

> BBox vs BBox 碰撞

```intent
def bbox_intersects(a: BBox3D, b: BBox3D) -> Bool
```

| 参数 | 类型 |
|---|---|
| `a` | BBox3D |
| `b` | BBox3D |

## `pipe_collides`

> 管道碰撞（批量检测入口）

```intent
def pipe_collides(a_start: Point3D, a_end: Point3D, a_r: Float, b_start: Point3D, b_end: Point3D, b_r: Float) -> Bool
```

| 参数 | 类型 |
|---|---|
| `a_start` | Point3D |
| `a_end` | Point3D |
| `a_r` | Float |
| `b_start` | Point3D |
| `b_end` | Point3D |
| `b_r` | Float |

## class `Plane`

- `init()`
- `create_from_normal(n: Vector3D, point: Point3D)`
- `create_from_points(a: Point3D, b: Point3D, c: Point3D)`
- `distance_to(point: Point3D)` -> `Float`
- `project(point: Point3D)` -> `Point3D`
- `intersect_line(line: Line3D)` -> `Point3D`

## class `Sphere`

- `init()`
- `create(center: Point3D, radius: Float)`
- `contains(point: Point3D)` -> `Bool`
- `intersects_bbox(bbox: BBox3D)` -> `Bool`
- `volume()` -> `Float`

## class `Cylinder`

- `init()`
- `create(start: Point3D, end: Point3D, radius: Float)`
- `axis()` -> `Vector3D`
- `length()` -> `Float`
- `distance_to_point(point: Point3D)` -> `Float`
- `intersects_bbox(bbox: BBox3D)` -> `Bool`
- `intersects_cylinder(other: Cylinder)` -> `Bool`
- `bbox()` -> `BBox3D`

