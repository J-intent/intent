name: Feature request
description: 提议新特性 — 先读 ROADMAP_LONGTERM.md，你的提议可能已在路线图上
labels: ["enhancement"]
body:
  - type: markdown
    attributes:
      value: |
        提议前请读 `docs/ROADMAP_LONGTERM.md` — 四期路线（v3.0 生产基座 → v4.0 LTS）已列全部候选任务。
        若提议在图上，请说明你为什么认为它应该提前；若不在图上，请说明它为什么值得进图。
  - type: textarea
    id: problem
    attributes:
      label: 要解决的真实问题
      description: 不是"某个语言有这个所以 Intent 也要有" — 是你踩到的具体场景
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: 提议的形态
      description: 语法草案 + 一段示例代码（Intent 风格：契约先行）
    validations:
      required: true
  - type: dropdown
    id: phase
    attributes:
      label: 你认为属于哪一期
      options:
        - v3.0 生产基座（类型/包/并发/内存/调试/测试/标准库/社区）
        - v3.5 元编程与互操作
        - v4.0-beta 生态冷启动
        - v4.0 LTS 生产就绪
        - "都不适合 — 路线图要改"
    validations:
      required: true
