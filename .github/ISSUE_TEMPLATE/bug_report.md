name: Bug report
description: 报告一个缺陷 — 契约被违反、解释器崩溃、或行为与 spec 不符
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        提交前请确认：已搜索现有 issue；已用 `python src/mini_intent.py --check <file>` 确认是运行时问题而非语法笔误。
  - type: textarea
    id: repro
    attributes:
      label: 最小复现
      description: 一段能稳定触发问题的最小 Intent 代码
      render: python
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: 期望行为
      description: 依据 docs/spec.md，这段代码应该怎样
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: 实际行为
      description: 完整输出（含错误渲染、调用链）— 不要截断
    validations:
      required: true
  - type: input
    id: version
    attributes:
      label: Intent 版本
      placeholder: "python src/mini_intent.py --version"
    validations:
      required: true
  - type: dropdown
    id: executor
    attributes:
      label: 执行通道
      options:
        - 树遍历解释器（默认）
        - 字节码 VM（--compile --run-vm）
        - REPL
    validations:
      required: true
  - type: textarea
    id: contract
    attributes:
      label: 契约上下文（如涉及）
      description: 相关函数的 requires/ensures — Intent 的契约违反有专属诊断，请贴出
