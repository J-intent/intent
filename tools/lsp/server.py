#!/usr/bin/env python
# tools/lsp/server.py — Intent LSP 服务器（C8）
#
# 心学为体：编辑器里的知行合一——写的当下即见对错
# 禅道为翼：补全如念起，跳转如缘至，诊断如镜现
# 马哲为用：补全/跳转/诊断三件套，stdio JSON-RPC（LSP 2.0 基线子集）
#
# 复用 src/mini_intent.py 的 Lexer/Parser — 诊断与 CLI --check 同源，
# 不搞第二套语法规则（单一事实源纪律）。
#
# 用法：
#   python tools/lsp/server.py            # stdio 模式（编辑器接入）
#   python tools/lsp/smoke_test.py        # 冒烟：三件套端到端自检
#
# 客户端配置示例（VS Code settings.json）：
#   "languageServerExample.trace.server": "off"
#   （launch.json / package.json 贡献点见 README.md）

import json
import os
import re
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT, "src"))

# 语言关键字 — 与 Lexer.KEYWORDS 同源（v2.x 快照，新增关键字时同步此处与 mini_intent）
KEYWORDS = [
    'def', 'func', 'fn', 'let', 'var', 'const', 'mut', 'return', 'if', 'else',
    'elif', 'for', 'while', 'break', 'continue', 'match', 'class', 'this',
    'enum', 'import', 'from', 'as', 'try', 'catch', 'finally', 'defer', 'with',
    'yield', 'requires', 'ensures', 'invariant', 'pure', 'effect', 'export',
    'assert', 'and', 'or', 'not', 'in', 'is',
    'spawn', 'scope', 'raise',  # CC1 结构化并发 / EX1 异常链
    'None', 'True', 'False', 'true', 'false', 'null',
]

# Parser 错误串中的位置标记 — "   at line 3, column 5"
LINE_COL_PAT = re.compile(r"at line (\d+), column (\d+)")
# 文档函数定义 / 变量声明（补全与跳转的静态扫描源）
DEF_PAT = re.compile(r'^\s*def\s+([A-Za-z_]\w*)\s*\(', re.M)
VAR_PAT = re.compile(r'^\s*(?:let|var|const)\s+([A-Za-z_]\w*)', re.M)


class IntentLSPServer:
    """Intent 语言服务器 — 诊断/补全/跳转三件套（LSP 2.0 基线子集）"""

    def __init__(self):
        self.documents = {}          # uri -> 全文
        self.shutdown_received = False
        self._builtin_cache = None
        self._stdmod_cache = None

    # ═══ 传输层：Content-Length 帧 + JSON-RPC ═══

    def read_message(self):
        """读一条 LSP 消息；EOF 返回 None"""
        headers = {}
        while True:
            raw = sys.stdin.buffer.readline()
            if not raw:
                return None
            line = raw.decode('utf-8').strip()
            if line == '':
                break
            if ':' in line:
                key, _, val = line.partition(':')
                headers[key.strip().lower()] = val.strip()
        length = int(headers.get('content-length', 0))
        if length <= 0:
            return None
        body = sys.stdin.buffer.read(length)
        return json.loads(body.decode('utf-8'))

    def write_message(self, obj) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        head = f"Content-Length: {len(data)}\r\n\r\n".encode('ascii')
        sys.stdout.buffer.write(head + data)
        sys.stdout.buffer.flush()

    def respond(self, msg_id, result) -> None:
        self.write_message({"jsonrpc": "2.0", "id": msg_id, "result": result})

    def respond_error(self, msg_id, message: str) -> None:
        self.write_message({"jsonrpc": "2.0", "id": msg_id,
                            "error": {"code": -32603, "message": message}})

    def notify(self, method: str, params) -> None:
        self.write_message({"jsonrpc": "2.0", "method": method, "params": params})

    # ═══ 消息分发 ═══

    def serve_forever(self) -> None:
        while True:
            msg = self.read_message()
            if msg is None:
                break
            try:
                self.handle(msg)
            except Exception as e:
                # 单条消息异常不杀死服务器 — 请求回 error, 通知静默记 stderr
                if msg.get('id') is not None:
                    self.respond_error(msg['id'], f"服务器内部错误: {e}")
                else:
                    print(f"[intent-lsp] notify {msg.get('method')} 失败: {e}",
                          file=sys.stderr)

    def handle(self, msg: dict) -> None:
        method = msg.get('method', '')
        msg_id = msg.get('id')
        params = msg.get('params') or {}

        if method == 'initialize':
            self.respond(msg_id, {
                "capabilities": {
                    "textDocumentSync": 1,            # Full 同步
                    "completionProvider": {"triggerCharacters": ['.']},
                    "definitionProvider": True,
                },
                "serverInfo": {"name": "intent-lsp", "version": "0.1"},
            })
        elif method == 'initialized':
            pass  # 无注册能力需求
        elif method == 'shutdown':
            self.shutdown_received = True
            self.respond(msg_id, None)
        elif method == 'exit':
            sys.exit(0 if self.shutdown_received else 1)
        elif method == 'textDocument/didOpen':
            uri = params['textDocument']['uri']
            self.documents[uri] = params['textDocument'].get('text', '')
            self.publish_diagnostics(uri)
        elif method == 'textDocument/didChange':
            uri = params['textDocument']['uri']
            changes = params.get('contentChanges') or []
            if changes:
                self.documents[uri] = changes[-1].get('text', '')
            self.publish_diagnostics(uri)
        elif method == 'textDocument/completion':
            self.respond(msg_id, self.completion(params))
        elif method == 'textDocument/definition':
            self.respond(msg_id, self.definition(params))
        elif msg_id is not None:
            # 未知请求 — 空结果响应, 不让客户端干等
            self.respond(msg_id, None)

    # ═══ 三件套之一：诊断 ═══

    def publish_diagnostics(self, uri: str) -> None:
        self.notify('textDocument/publishDiagnostics',
                    {"uri": uri, "diagnostics": self.compute_diagnostics(uri)})

    def compute_diagnostics(self, uri: str) -> list:
        text = self.documents.get(uri, '')
        from mini_intent import Lexer, Parser
        try:
            tokens = Lexer(text).tokenize()
            parser = Parser(tokens, text)
            parser.parse()
        except Exception as e:  # 词法/解析器自身异常 — 降级为单条诊断
            return [self._diag(0, 0, 0, 1, f"解析异常: {e}")]
        diags = []
        for err in parser.errors:
            first_line = err.split('\n', 1)[0].strip()
            m = LINE_COL_PAT.search(err)
            if m:
                line, col = int(m.group(1)) - 1, int(m.group(2)) - 1
            else:
                line, col = 0, 0
            diags.append(self._diag(line, col, line, col + 1, first_line))
        return diags

    @staticmethod
    def _diag(sl: int, sc: int, el: int, ec: int, message: str) -> dict:
        return {
            "range": {"start": {"line": max(0, sl), "character": max(0, sc)},
                      "end": {"line": max(0, el), "character": max(0, ec)}},
            "severity": 1,  # Error
            "source": "intent",
            "message": message,
        }

    # ═══ 三件套之二：补全 ═══

    def completion(self, params: dict) -> dict:
        uri = params['textDocument']['uri']
        pos = params.get('position', {})
        text = self.documents.get(uri, '')
        lines = text.split('\n')
        line_no = pos.get('line', 0)
        prefix = ''
        if 0 <= line_no < len(lines):
            cur = lines[line_no][:pos.get('character', 0)]
            m = re.search(r'[A-Za-z_][A-Za-z0-9_]*$', cur)
            prefix = m.group(0) if m else ''
        items = []
        for kw in KEYWORDS:
            items.append(self._item(kw, 14))            # Keyword
        for fn in DEF_PAT.findall(text):
            items.append(self._item(fn, 3))             # Function
        for fn in self._builtin_names():
            items.append(self._item(fn, 3))             # Function
        for mod in self._std_modules():
            items.append(self._item(mod, 9))            # Module
        if prefix:
            items = [it for it in items if it['label'].startswith(prefix)]
        # 客户端一般只展示前几十条; 服务端返回全量, 排序由客户端决定
        return {"isIncomplete": False, "items": items}

    @staticmethod
    def _item(label: str, kind: int) -> dict:
        return {"label": label, "kind": kind}

    def _builtin_names(self) -> list:
        """解释器内置函数名 — 与运行时同源"""
        if self._builtin_cache is None:
            try:
                from mini_intent import Interpreter
                self._builtin_cache = sorted(Interpreter().builtins.keys())
            except Exception:
                self._builtin_cache = []
        return self._builtin_cache

    def _std_modules(self) -> list:
        """std/ 目录下的模块名"""
        if self._stdmod_cache is None:
            std_dir = os.path.join(PROJECT, 'std')
            try:
                self._stdmod_cache = sorted(
                    f[:-len('.intent')] for f in os.listdir(std_dir)
                    if f.endswith('.intent') and not f.startswith('_'))
            except OSError:
                self._stdmod_cache = []
        return self._stdmod_cache

    # ═══ 三件套之三：跳转 ═══

    def definition(self, params: dict):
        uri = params['textDocument']['uri']
        pos = params.get('position', {})
        text = self.documents.get(uri, '')
        lines = text.split('\n')
        line_no, char = pos.get('line', 0), pos.get('character', 0)
        if not (0 <= line_no < len(lines)):
            return []
        word = self._word_at(lines[line_no], char)
        if not word:
            return []
        # 1) 函数定义行
        m = re.search(rf'^\s*def\s+{re.escape(word)}\s*\(', text, re.M)
        # 2) 变量声明行（let/var/const）
        if m is None:
            m = re.search(rf'^\s*(?:let|var|const)\s+{re.escape(word)}\b', text, re.M)
        if m is None:
            return []
        line = text[:m.start()].count('\n')
        col = m.group(0).index(word)
        return [{"uri": uri,
                 "range": {"start": {"line": line, "character": col},
                           "end": {"line": line, "character": col + len(word)}}}]

    @staticmethod
    def _word_at(line: str, char: int) -> str:
        """光标处（或光标左沿）的标识符"""
        left = re.search(r'[A-Za-z_][A-Za-z0-9_]*$', line[:char])
        right = re.match(r'[A-Za-z0-9_]*', line[char:])
        return (left.group(0) if left else '') + (right.group(0) if right else '')


def main():
    IntentLSPServer().serve_forever()


if __name__ == '__main__':
    main()
