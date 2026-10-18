# geometry

## `min_float`

```intent
def min_float(a: Float, b: Float) -> Float
```

| 参数 | 类型 |
|---|---|
| `a` | Float |
| `b` | Float |

## `max_float`

```intent
def max_float(a: Float, b: Float) -> Float
```

| 参数 | 类型 |
|---|---|
| `a` | Float |
| `b` | Float |

## class `Vector3D`

- `init()`
- `create(x: Float, y: Float, z: Float)`
- `add(other: Vector3D)` -> `Vector3D`
- `sub(other: Vector3D)` -> `Vector3D`
- `scale(s: Float)` -> `Vector3D`
- `dot(other: Vector3D)` -> `Float`
- `cross(other: Vector3D)` -> `Vector3D`
- `length()` -> `Float`
- `normalize()` -> `Vector3D`
- `negate()` -> `Vector3D`
- `from_points(a: Point3D, b: Point3D)`
- `distance_to(other: Vector3D)` -> `Float`

## class `Point3D`

- `init()`
- `create(x: Float, y: Float, z: Float)`
- `add_vector(v: Vector3D)` -> `Point3D`
- `sub_vector(v: Vector3D)` -> `Point3D`
- `to(other: Point3D)` -> `Vector3D`
- `distance_to(other: Point3D)` -> `Float`
- `midpoint(other: Point3D)` -> `Point3D`

## class `Line3D`

- `init()`
- `create(start: Point3D, end: Point3D)`
- `direction()` -> `Vector3D`
- `length()` -> `Float`
- `point_at(t: Float)` -> `Point3D`
- `midpoint()` -> `Point3D`

## class `BBox3D`

- `init()`
- `create(min: Point3D, max: Point3D)`
- `from_points(a: Point3D, b: Point3D)`
- `size()` -> `Vector3D`
- `center()` -> `Point3D`
- `volume()` -> `Float`
- `contains(p: Point3D)` -> `Int`
- `intersects(other: BBox3D)` -> `Int`
- `expand(p: Point3D)`
- `expand_padded(p: Point3D, pad: Float)`
- `merge(other: BBox3D)`
- `set_empty()`

