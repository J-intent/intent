# schedule

Intent 官方包中的 BIM 领域工具：构件清单的排序、过滤与分组统计。

构件统一用字典表示：`{"id": ..., "type": ..., "floor": ..., "volume": ...}`。

- `count_by(elements, field)`：按 `type` 或 `floor` 聚合计数，返回字典。
- `sort_by_volume(elements)`：按体积降序做稳定的冒泡排序，不改动入参列表。
- `filter_by_floor(elements, floor)`：筛选指定楼层，保持原始顺序。
- `total_volume(elements)`：求全部构件体积之和，空清单返回 0。
- `summary(elements)`：按楼层输出 `["L1: 2", "L2: 2"]` 形式的汇总行。

所有函数都带 `requires` / `ensures` 契约，空清单与非法字段会显式失败或返回空结果。

## 用法

```intent
import schedule;

let items = [{"id": "W1", "type": "Wall", "floor": "L1", "volume": 3}];
assert schedule.total_volume(items) == 3, "体积合计";
assert contains(schedule.summary(items), "L1: 1"), "楼层汇总";
```

## 测试

```bash
python src/mini_intent.py --test packages/schedule/test_schedule.intent
```
