#!/usr/bin/env python
# tools/lsp/smoke_test.py — LSP 三件套端到端冒烟（C8 自检）
#
# 起真实子进程服务器，走完整 LSP 会话：
#   initialize → didOpen(带语法错误) → diagnostics 非空
#   → completion 有内容 → definition 有位置
#   → didChange(修复错误) → diagnostics 清零
#   → shutdown → exit(0)
#
# 退出码 0 = 三件套全通；任一环节失败打印详情并以 1 退出。

import json
import os
import subprocess
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVER = os.path.join(PROJECT, 'tools', 'lsp', 'server.py')

BAD_CODE = 'def main() {\n    let x = ;\n    print(x);\n}\n'
GOOD_CODE = 'def main() {\n    let x = 1;\n    print(x);\n}\n'
URI = 'file:///smoke.intent'


class LSPClient:
    """最小 stdio 客户端 — 帧编解码 + 请求/通知/等待"""

    def __init__(self):
        self.proc = subprocess.Popen(
            [sys.executable, SERVER],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    def _send(self, obj):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        head = f"Content-Length: {len(data)}\r\n\r\n".encode('ascii')
        self.proc.stdin.write(head + data)
        self.proc.stdin.flush()

    def request(self, method, params, msg_id):
        self._send({"jsonrpc": "2.0", "id": msg_id,
                    "method": method, "params": params})
        return self._read_until_id(msg_id)

    def notify(self, method, params):
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def _read_msg(self):
        headers = {}
        while True:
            line = self.proc.stdout.readline().decode('utf-8').strip()
            if line == '':
                break
            if ':' in line:
                key, _, val = line.partition(':')
                headers[key.strip().lower()] = val.strip()
        length = int(headers.get('content-length', 0))
        if length <= 0:
            stderr_tail = ''
            try:
                stderr_tail = self.proc.stderr.read().decode('utf-8', 'replace')[-500:]
            except Exception:
                pass
            raise RuntimeError(
                f"服务器帧异常(可能已崩溃), stderr 尾部: {stderr_tail}")
        body = self.proc.stdout.read(length)
        return json.loads(body.decode('utf-8'))

    def _read_until_id(self, msg_id):
        """读到响应 id 为止；中途的通知原样返回列表"""
        notes = []
        while True:
            msg = self._read_msg()
            if msg.get('id') == msg_id:
                return msg, notes
            notes.append(msg)

    def close(self):
        self.proc.stdin.close()
        self.proc.wait(timeout=10)


def main():
    client = LSPClient()
    failures = []

    def check(name, cond, detail=''):
        mark = '✅' if cond else '❌'
        print(f"  {mark} {name}" + (f" — {detail}" if detail and not cond else ''))
        if not cond:
            failures.append(name)

    # 1) initialize
    resp, _ = client.request('initialize', {
        "processId": None, "rootUri": None, "capabilities": {}}, 1)
    caps = (resp.get('result') or {}).get('capabilities', {})
    check('initialize 返回能力', bool(caps), json.dumps(resp)[:200])
    check('诊断同步能力', caps.get('textDocumentSync') == 1)
    check('补全能力', 'completionProvider' in caps)
    check('跳转能力', caps.get('definitionProvider') is True)

    client.notify('initialized', {})

    # 2) didOpen 带语法错误 → diagnostics 非空
    client.notify('textDocument/didOpen', {
        "textDocument": {"uri": URI, "languageId": "intent",
                         "version": 1, "text": BAD_CODE}})
    _, notes = client.request('textDocument/completion',
                              {"textDocument": {"uri": URI},
                               "position": {"line": 1, "character": 11}}, 2)
    diag_notes = [n for n in notes
                  if n.get('method') == 'textDocument/publishDiagnostics']
    check('didOpen 触发诊断推送', len(diag_notes) == 1)
    diags = diag_notes[0]['params']['diagnostics'] if diag_notes else []
    check('语法错误被诊断捕获', len(diags) >= 1, f"diagnostics={diags}")

    # 3) completion 有内容（含关键字与文档函数）
    resp, _ = client.request('textDocument/completion',
                             {"textDocument": {"uri": URI},
                              "position": {"line": 1, "character": 8}}, 3)
    items = (resp.get('result') or {}).get('items', [])
    labels = {it['label'] for it in items}
    check('补全返回条目', len(items) > 0, f"items={len(items)}")
    check('补全含关键字 def', 'def' in labels)
    check('补全含文档函数 main', 'main' in labels)
    check('补全含 std 模块', 're' in labels or 'math' in labels, str(labels)[:200])

    # 4) definition 跳到变量声明（光标在 line 2 `    print(x);` 的 x 上）
    resp, _ = client.request('textDocument/definition',
                             {"textDocument": {"uri": URI},
                              "position": {"line": 2, "character": 11}}, 4)
    locs = resp.get('result') or []
    check('跳转返回位置', len(locs) == 1, f"result={locs}")
    if locs:
        check('跳转到 let x 声明行(0-based line 1)',
              locs[0]['range']['start']['line'] == 1, str(locs[0]))

    # 5) didChange 修复 → 诊断清零
    client.notify('textDocument/didChange', {
        "textDocument": {"uri": URI, "version": 2},
        "contentChanges": [{"text": GOOD_CODE}]})
    _, notes = client.request('textDocument/completion',
                              {"textDocument": {"uri": URI},
                               "position": {"line": 1, "character": 5}}, 5)
    diag_notes = [n for n in notes
                  if n.get('method') == 'textDocument/publishDiagnostics']
    diags = diag_notes[0]['params']['diagnostics'] if diag_notes else [{'x': 1}]
    check('修复后诊断清零', diag_notes and len(diags) == 0, f"diags={diags}")

    # 6) shutdown / exit
    resp, _ = client.request('shutdown', None, 6)
    check('shutdown 响应', resp.get('result') is None)
    client.notify('exit', None)
    rc = client.proc.wait(timeout=10)
    check('exit 退出码 0', rc == 0, f"rc={rc}")
    client.close()

    print()
    if failures:
        print(f"❌ 冒烟失败 {len(failures)} 项: {failures}")
        sys.exit(1)
    print("✅ LSP 三件套冒烟全通（initialize/诊断/补全/跳转/修复/关闭）")
    sys.exit(0)


if __name__ == '__main__':
    main()
