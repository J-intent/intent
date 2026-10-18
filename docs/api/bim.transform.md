# transform

## `translate_point`

> 平移点

```intent
def translate_point(p: Point3D, v: Vector3D) -> Point3D
```

| 参数 | 类型 |
|---|---|
| `p` | Point3D |
| `v` | Vector3D |

## `rotate_x_matrix`

> 绕 X 轴旋转

```intent
def rotate_x_matrix(angle_rad: Float) -> Matrix3x3
```

| 参数 | 类型 |
|---|---|
| `angle_rad` | Float |

## `rotate_y_matrix`

> 绕 Y 轴旋转

```intent
def rotate_y_matrix(angle_rad: Float) -> Matrix3x3
```

| 参数 | 类型 |
|---|---|
| `angle_rad` | Float |

## `rotate_z_matrix`

> 绕 Z 轴旋转

```intent
def rotate_z_matrix(angle_rad: Float) -> Matrix3x3
```

| 参数 | 类型 |
|---|---|
| `angle_rad` | Float |

## `rotate_around_axis_matrix`

> 绕任意轴旋转（Rodrigues 公式）

```intent
def rotate_around_axis_matrix(v: Vector3D, angle_rad: Float) -> Matrix3x3
```

| 参数 | 类型 |
|---|---|
| `v` | Vector3D |
| `angle_rad` | Float |

## `scale_matrix`

> 均匀缩放矩阵

```intent
def scale_matrix(sx: Float, sy: Float, sz: Float) -> Matrix3x3
```

| 参数 | 类型 |
|---|---|
| `sx` | Float |
| `sy` | Float |
| `sz` | Float |

## `scale_vector`

> 向量缩放

```intent
def scale_vector(v: Vector3D, s: Float) -> Vector3D
```

| 参数 | 类型 |
|---|---|
| `v` | Vector3D |
| `s` | Float |

## `rotate_vector`

> 旋转向量

```intent
def rotate_vector(v: Vector3D, matrix: Matrix3x3) -> Vector3D
```

| 参数 | 类型 |
|---|---|
| `v` | Vector3D |
| `matrix` | Matrix3x3 |

## `rotate_point_2d`

> 绕 Z 轴旋转点（BIM 最常用：平面旋转）

```intent
def rotate_point_2d(p: Point3D, center: Point3D, angle_rad: Float) -> Point3D
```

| 参数 | 类型 |
|---|---|
| `p` | Point3D |
| `center` | Point3D |
| `angle_rad` | Float |

## `mirror_x`

> 镜像：绕 YZ 平面（X 取反）

```intent
def mirror_x(point: Point3D) -> Point3D
```

| 参数 | 类型 |
|---|---|
| `point` | Point3D |

## `mirror_y`

> 镜像：绕 XZ 平面（Y 取反）

```intent
def mirror_y(point: Point3D) -> Point3D
```

| 参数 | 类型 |
|---|---|
| `point` | Point3D |

## `project_to_xy`

> 投影到 XY 平面（Z=0）

```intent
def project_to_xy(point: Point3D) -> Point3D
```

| 参数 | 类型 |
|---|---|
| `point` | Point3D |

## class `Matrix3x3`

- `init()`
- `set(a00: Float, a01: Float, a02: Float, a10: Float, a11: Float, a12: Float, a20: Float, a21: Float, a22: Float)`
- `transform(v: Vector3D)` -> `Vector3D`
- `multiply(other: Matrix3x3)` -> `Matrix3x3`
- `transpose()` -> `Matrix3x3`
- `determinant()` -> `Float`

## class `CoordinateSystem`

- `init()`
- `create(origin: Point3D, x_axis: Vector3D, y_axis: Vector3D)`
- `to_local(global_point: Point3D)` -> `Point3D`
- `to_global(local_point: Point3D)` -> `Point3D`

