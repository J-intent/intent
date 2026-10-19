# functools

## `compose`

> 组合: compose(f, g) → fn(x) { f(g(x)) } — 右先生效

```intent
def compose(f: Any, g: Any)
```

| 参数 | 类型 |
|---|---|
| `f` | Any |
| `g` | Any |

## `memoize`

> 记忆化(单参 lru_cache 的无淘汰子集): 同参第二次直接命中缓存
> 闭包捕获 cache 字典 — 键限标量(Intent 字典键规范), 富键调用方自行编码
> 命中证据由调用方侧证(装饰函数的副作用计数), 不搞外部统计出口

```intent
def memoize(f: Any)
```

| 参数 | 类型 |
|---|---|
| `f` | Any |

## `lru_cache`

> 有界记忆化(真 LRU): 容量满时淘汰最久未访问的键
> - 命中即刷新访问序(命中键移到序尾); 插入超容淘汰序头
> - Intent 字典无 delete — 刷新与淘汰都靠重建字典(闭包重绑定已实证)
> - 代价: 命中 O(cap) 重建 — cap 宜取小值(演示/教学级, 非高性能缓存)
> - cap < 1 显式报错(显式失败不静默)
> 键限标量(Intent 字典键规范), 富键调用方自行编码

```intent
def lru_cache(f: Any, cap: Any)
```

| 参数 | 类型 |
|---|---|
| `f` | Any |
| `cap` | Any |

