#!/usr/bin/env python
# tools/async_http_check.py — A3b 真 HTTP 并发验证
#
# 为什么不是 .intent 测试文件：真并发必须有一个「慢服务器」做对照，
# Intent 测试文件起不了服务器。本工具起一个每请求 sleep 300ms 的本地
# HTTP 服务，然后跑两端 Intent 程序：
#   并发：gather(3 × async_http_get) —— 总耗时应 ≈ 一个请求
#   串行：run 三次（run 无事件循环，挂起退化为阻塞）—— 总耗时 ≈ 3 个请求
# 两者对照即证「并发」不是话术。
#
# 用法：python tools/async_http_check.py
# 退出码：0 并发成立且结果正确 ｜ 1 失败

import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERP = os.path.join(PROJECT, 'src', 'mini_intent.py')
PYTHON = sys.executable
LATENCY = 0.3          # 每请求延迟（秒）
CONCURRENT_MAX = 0.6   # 并发门禁：< 2×LATENCY
SERIAL_MIN = 0.85      # 串行对照下限：>= ~3×LATENCY


class SlowHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(LATENCY)
        body = b'ok'
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # 安静


def _run_intent(src: str) -> str:
    with tempfile.NamedTemporaryFile('w', suffix='.intent', delete=False,
                                     encoding='utf-8') as f:
        f.write(src)
        path = f.name
    try:
        r = subprocess.run([PYTHON, INTERP, path], capture_output=True,
                           timeout=60, cwd=PROJECT)
    finally:
        os.unlink(path)
    out = ((r.stdout or b'').decode('utf-8', 'replace')
           + (r.stderr or b'').decode('utf-8', 'replace'))
    if r.returncode != 0:
        raise RuntimeError(f"Intent 程序失败:\n{out[-800:]}")
    return out


def main() -> int:
    server = ThreadingHTTPServer(('127.0.0.1', 0), SlowHandler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}/x"
    try:
        concurrent_src = f'''
async def get(u: String) -> String {{
    return async_http_get(u, 5000);
}};

let t0 = now();
let rs = gather(get("{base}?1"), get("{base}?2"), get("{base}?3"));
let ms = (now() - t0) * 1000.0;
print(rs[0] + rs[1] + rs[2]);
print("MS " + str(int(ms)));
'''
        out = _run_intent(concurrent_src).replace('\r', '')
        m = re.search(r'^MS (\d+)$', out, re.M)
        if 'okokok' not in out or not m:
            print(f"❌ 并发程序输出不符:\n{out[-500:]}")
            return 1
        conc_ms = int(m.group(1))

        serial_src = f'''
async def get(u: String) -> String {{
    return async_http_get(u, 5000);
}};

let t0 = now();
let a = run(get("{base}?1"));
let b = run(get("{base}?2"));
let c = run(get("{base}?3"));
let ms = (now() - t0) * 1000.0;
print(a + b + c);
print("MS " + str(int(ms)));
'''
        out2 = _run_intent(serial_src).replace('\r', '')
        m2 = re.search(r'^MS (\d+)$', out2, re.M)
        if not m2:
            print(f"❌ 串行程序输出不符:\n{out2[-500:]}")
            return 1
        serial_ms = int(m2.group(1))
    finally:
        server.shutdown()
        server.server_close()

    print(f"本地服务器每请求延迟 {int(LATENCY * 1000)} ms")
    print(f"HTTP 并发: gather 3 请求 = {conc_ms} ms"
          f"（门禁 < {int(CONCURRENT_MAX * 1000)} ms）")
    print(f"串行对照: run 3 次 = {serial_ms} ms"
          f"（门禁 >= {int(SERIAL_MIN * 1000)} ms）")
    if conc_ms >= CONCURRENT_MAX * 1000:
        print("❌ 并发未成立（总耗时接近串行）")
        return 1
    if serial_ms < SERIAL_MIN * 1000:
        print("❌ 串行对照异常（run 本应阻塞 3×延迟）")
        return 1
    if serial_ms <= conc_ms:
        print("❌ 串行不慢于并发 — 对照无效")
        return 1
    print(f"✅ HTTP 并发成立：并发 {conc_ms} ms vs 串行 {serial_ms} ms"
          f"（提速 {serial_ms / max(conc_ms, 1):.1f}x）")
    return 0


if __name__ == '__main__':
    sys.exit(main())
