# Intent 基准基线

机器: Ryzen 7 9700X / RTX 5060 Ti / 128GB DDR5, Windows 11, Python 3.13.14
口径: 每个基准跑 3 次取最小值(抗抖动); 单位 ms; 由 run_benchmarks.py --update 生成。

| 基准 | 计时点 | 基线 ms |
|---|---|---|
| attrs.intent | read_sum x100000 = 300000 | 1627 |
| attrs.intent | bump x100000, x = 100001 | 1425 |
| contracts.intent | plain_add x100000 = 100000 | 1623 |
| contracts.intent | guarded_add x100000 = 100000 | 2602 |
| fib.intent | fib(25) = 75025 | 3005 |
| fib.intent | fib_iter(10000) digits = 2090 | 108 |
