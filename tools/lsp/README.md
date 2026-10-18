# Intent LSP（C8）

补全 / 跳转 / 诊断三件套。stdio JSON-RPC，LSP 2.0 基线子集，
复用 `src/mini_intent.py` 的 Lexer/Parser——诊断与 CLI `--check` 同源。

## 启动

```bash
python tools/lsp/server.py        # stdio 模式，由编辑器客户端拉起
```

## 自检

```bash
python tools/lsp/smoke_test.py    # 起真实子进程走完整会话：initialize →
                                  # didOpen(错误文件) → 诊断非空 → 补全/跳转
                                  # → didChange 修复 → 诊断清零 → shutdown/exit
```

退出码 0 = 三件套全通。

## 能力矩阵

| 能力 | 方法 | 说明 |
|---|---|---|
| 诊断 | `textDocument/didOpen` `didChange` → `publishDiagnostics` | 语法错误行列 + 首行消息；与 `--check` 同一解析器 |
| 补全 | `textDocument/completion` | 语言关键字 + 当前文档 `def` 函数 + 解释器内置函数 + `std/` 模块名 |
| 跳转 | `textDocument/definition` | 光标词 → 本文件 `def`/`let`/`var`/`const` 声明行 |

同步模式：Full（整文档推送）。位置语义：LSP 0-based 行列。

## VS Code 接入（最小客户端扩展）

`package.json` 贡献点：

```json
{
  "contributes": {
    "languages": [{"id": "intent", "extensions": [".intent"]}],
    "configuration": {
      "title": "Intent",
      "properties": {
        "intent.server.path": {"type": "string", "default": "python"}
      }
    }
  }
}
```

客户端扩展 `extension.ts` 骨架：

```ts
import * as vscode from 'vscode';
import { LanguageClient, TransportKind } from 'vscode-languageclient/node';

export function activate(ctx: vscode.ExtensionContext) {
  const server = vscode.workspace.getConfiguration('intent').get('server.path')!;
  const client = new LanguageClient('intent', 'Intent LSP', {
    command: server,
    args: [ctx.asAbsolutePath('tools/lsp/server.py')],
    transport: TransportKind.stdio,
  }, { documentSelector: [{ scheme: 'file', language: 'intent' }] });
  ctx.subscriptions.push(client.start());
}
```

## 边界（有意不为，反膨胀）

- 无模块成员补全（`std.re.` 之后的函数列表）——静态扫描跨文件开销大于收益
- 无跨文件跳转——当前仅本文件声明
- 无语义级诊断（resolver 未接入）——先语法层，与 C4 linter 职责分工
- 无 hover / rename / signature help——三件套之外按需增量
