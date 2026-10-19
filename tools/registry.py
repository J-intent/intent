#!/usr/bin/env python
# tools/registry.py — Intent 包注册表（E4）
#
# 心学为体：包的流转如意的流通——发布即立言，安装即借势
# 禅道为翼：注册表是一面镜子，照出社区的积累，不造中心的霸权
# 马哲为用：本地目录注册表 + HTTP 注册表服务（P3a），
#           与 C2 的 intent.toml / lib/ 搜索路径无缝衔接
#
# 包格式：一个含 intent.toml 的目录——
#   [project]
#   name = "mypkg"        # 必填, 小写字母/数字/连字符
#   version = "0.1.0"     # 必填, semver 三段
# 包内容是 .intent 源码（模块由 lib/<pkg>/ 下的文件提供）。
#
# 注册表布局（默认 ./registry，可 --registry 指定）：
#   registry/
#     registry.json           # 索引: {packages: {name: {versions: {ver: {path, published, files}}}}}
#     <name>/<version>/       # 包快照（publish 时整目录拷贝）
#
# 用法：
#   python tools/registry.py publish <pkg-dir> [--registry DIR] [--registry-url URL]
#   python tools/registry.py list [--registry DIR]
#   python tools/registry.py install <name> [--version V] [--dest DIR] [--registry DIR] [--registry-url URL]
#   python tools/registry.py serve [--registry DIR] [--host H] [--port P]
#   python tools/registry.py --selftest          # 临时目录 round-trip 自检（含 HTTP）
#
# HTTP 注册表（P3a）：serve 把本地 registry 变成 HTTP 服务——
#   GET  /index.json            查询索引（包/版本/文件清单）
#   GET  /pkg/<name>/<ver>/<f>  下载包文件
#   POST /publish               {name, version, files:{relpath: content}} 发布
# publish/install 带 --registry-url 即走 HTTP 通道（否则本地目录）。
#
# 与解释器的衔接：install 的目标目录（默认 ./lib）正是
# mini_intent.py 的模块搜索路径之一——装完即可 import。

import json
import os
import re
import shutil
import sys
import tempfile

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REGISTRY = os.path.join(PROJECT, 'registry')
DEFAULT_DEST = os.path.join(PROJECT, 'lib')

NAME_PAT = re.compile(r'^[a-z0-9][a-z0-9-]*$')
VER_PAT = re.compile(r'^\d+\.\d+\.\d+$')


def _load_toml(path: str) -> dict:
    """读 intent.toml — 复用解释器的清单解析（单一事实源）"""
    sys.path.insert(0, os.path.join(PROJECT, 'src'))
    try:
        import tomllib
    except ImportError:
        raise RuntimeError("解析 intent.toml 需要 Python 3.11+ 的 tomllib")
    with open(path, 'rb') as f:
        return tomllib.load(f)


def _registry_index(registry_dir: str) -> dict:
    idx_path = os.path.join(registry_dir, 'registry.json')
    if not os.path.isfile(idx_path):
        return {'packages': {}}
    with open(idx_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_registry_index(registry_dir: str, index: dict) -> None:
    os.makedirs(registry_dir, exist_ok=True)
    with open(os.path.join(registry_dir, 'registry.json'), 'w',
              encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def cmd_publish(pkg_dir: str, registry_dir: str) -> int:
    """发布：校验包 → 快照进注册表 → 更新索引"""
    pkg_dir = os.path.abspath(pkg_dir)
    manifest_path = os.path.join(pkg_dir, 'intent.toml')
    if not os.path.isfile(manifest_path):
        print(f"❌ 包目录缺少 intent.toml: {pkg_dir}")
        return 2
    try:
        data = _load_toml(manifest_path)
    except Exception as e:
        print(f"❌ intent.toml 解析失败: {e}")
        return 2
    project = data.get('project', {})
    name = project.get('name', '')
    version = project.get('version', '')
    if not NAME_PAT.match(name):
        print(f"❌ 非法包名 '{name}'（小写字母/数字/连字符，字母数字开头）")
        return 2
    if not VER_PAT.match(version):
        print(f"❌ 非法版本号 '{version}'（semver 三段: x.y.z）")
        return 2
    if not any(f.endswith('.intent') for f in os.listdir(pkg_dir)
               if os.path.isfile(os.path.join(pkg_dir, f))):
        print(f"❌ 包目录没有 .intent 源码文件: {pkg_dir}")
        return 2

    snapshot = os.path.join(registry_dir, name, version)
    if os.path.isdir(snapshot):
        print(f"❌ 版本已存在: {name} v{version}（版本不可覆盖，请升版本）")
        return 1
    os.makedirs(os.path.dirname(snapshot), exist_ok=True)
    shutil.copytree(pkg_dir, snapshot,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

    index = _registry_index(registry_dir)
    entry = index['packages'].setdefault(name, {'versions': {}})
    # files 清单：HTTP install 按清单逐文件下载（本地 install 仍 copytree 整目录）
    entry['versions'][version] = {
        'path': os.path.relpath(snapshot, registry_dir).replace(os.sep, '/'),
        'files': _snapshot_files(snapshot),
        'published': _now_iso(),
    }
    _save_registry_index(registry_dir, index)
    print(f"✅ 已发布 {name} v{version} → {os.path.relpath(snapshot, PROJECT)}")
    return 0


def _snapshot_files(snapshot: str) -> list:
    """快照内文件相对路径清单（排序稳定，HTTP install 按它下载）"""
    out = []
    for root, _, fnames in os.walk(snapshot):
        for fn in fnames:
            rel = os.path.relpath(os.path.join(root, fn), snapshot)
            out.append(rel.replace(os.sep, '/'))
    return sorted(out)


def cmd_list(registry_dir: str) -> int:
    """列出注册表全部包与版本"""
    index = _registry_index(registry_dir)
    packages = index.get('packages', {})
    if not packages:
        print(f"（注册表为空: {os.path.relpath(registry_dir, PROJECT)}）")
        return 0
    for name in sorted(packages):
        versions = sorted(packages[name]['versions'])
        print(f"  {name}  " + "  ".join(versions))
    print(f"共 {len(packages)} 个包 / "
          f"{sum(len(p['versions']) for p in packages.values())} 个版本")
    return 0


def cmd_install(name: str, version: str, dest_dir: str,
                registry_dir: str) -> int:
    """安装：注册表快照 → dest（默认 lib/，即解释器模块搜索路径）"""
    index = _registry_index(registry_dir)
    pkg = index.get('packages', {}).get(name)
    if pkg is None:
        print(f"❌ 注册表没有包 '{name}'（list 查看可用包）")
        return 1
    if version is None:
        version = _latest_version(pkg['versions'])
        if version is None:
            print(f"❌ 包 '{name}' 没有任何版本")
            return 1
    elif version not in pkg['versions']:
        avail = ", ".join(sorted(pkg['versions']))
        print(f"❌ {name} 没有 v{version}（可用: {avail}）")
        return 1
    src = os.path.join(registry_dir, pkg['versions'][version]['path'])
    if not os.path.isdir(src):
        print(f"❌ 快照缺失: {src}")
        return 1
    target = os.path.join(dest_dir, name)
    if os.path.isdir(target):
        print(f"❌ 目标已存在: {os.path.relpath(target, PROJECT)}"
              f"（先删除再装，或换 dest）")
        return 1
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copytree(src, target,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    print(f"✅ 已安装 {name} v{version} → {os.path.relpath(target, PROJECT)}")
    print(f"   解释器模块搜索路径已含 {os.path.relpath(dest_dir, PROJECT)}/"
          f"，可直接 import {name}")
    return 0


def _latest_version(versions: dict) -> str:
    """semver 数值序取最大（非字符串序）"""
    if not versions:
        return None
    return max(versions,
               key=lambda v: tuple(int(p) for p in v.split('.')))


def _now_iso() -> str:
    from datetime import datetime
    return datetime.now().isoformat(timespec='seconds')


# ── HTTP 注册表（P3a）────────────────────────────────

def _validate_package(name: str, version: str, filenames) -> bool:
    """包校验（本地 publish 与 HTTP 发布共用同一套规则）"""
    if not NAME_PAT.match(name):
        print(f"❌ 非法包名 '{name}'（小写字母/数字/连字符，字母数字开头）")
        return False
    if not VER_PAT.match(version):
        print(f"❌ 非法版本号 '{version}'（semver 三段: x.y.z）")
        return False
    if not any(f.endswith('.intent') for f in filenames):
        print("❌ 包没有 .intent 源码文件")
        return False
    return True


def _store_files(registry_dir: str, name: str, version: str,
                 files: dict) -> str:
    """把 {relpath: 文本内容} 落成快照并更新索引；版本已存在抛 RuntimeError"""
    snapshot = os.path.join(registry_dir, name, version)
    if os.path.isdir(snapshot):
        raise RuntimeError(
            f"版本已存在: {name} v{version}（版本不可覆盖，请升版本）")
    os.makedirs(snapshot, exist_ok=True)
    for rel, content in files.items():
        dst = os.path.join(snapshot, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(content)
    index = _registry_index(registry_dir)
    entry = index['packages'].setdefault(name, {'versions': {}})
    entry['versions'][version] = {
        'path': f"{name}/{version}",
        'files': sorted(files.keys()),
        'published': _now_iso(),
    }
    _save_registry_index(registry_dir, index)
    return f"{name}/{version}"


def _read_pkg_files(pkg_dir: str) -> dict:
    """读包目录的文本文件（.intent/.toml/.md）为 {relpath: content}"""
    files = {}
    for root, _, fnames in os.walk(pkg_dir):
        for fn in fnames:
            if fn.endswith(('.intent', '.toml', '.md')):
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, pkg_dir).replace(os.sep, '/')
                with open(full, 'r', encoding='utf-8') as f:
                    files[rel] = f.read()
    return files


def _make_handler(registry_dir: str):
    """HTTP 注册表处理器（闭包捕获 registry_dir）"""
    from http.server import BaseHTTPRequestHandler

    class RegistryHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # 静音默认访问日志
            pass

        def _send_json(self, obj, status: int = 200):
            body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split('?', 1)[0]
            if path in ('/index.json', '/packages'):
                self._send_json(_registry_index(registry_dir))
                return
            m = re.match(r'^/pkg/([a-z0-9-]+)/(\d+\.\d+\.\d+)/(.+)$', path)
            if m:
                name, version, rel = m.group(1), m.group(2), m.group(3)
                target = os.path.normpath(
                    os.path.join(registry_dir, name, version, rel))
                base = os.path.normpath(registry_dir)
                # 路径穿越防护：解析后必须仍在 registry 内
                if not (target == base or target.startswith(base + os.sep)):
                    self._send_json({'error': '非法路径'}, 403)
                    return
                if os.path.isfile(target):
                    with open(target, 'rb') as f:
                        body = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type',
                                     'text/plain; charset=utf-8')
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
            self._send_json({'error': f'未找到: {path}'}, 404)

        def do_POST(self):
            if self.path.split('?', 1)[0] != '/publish':
                self._send_json({'error': '未找到'}, 404)
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                payload = json.loads(
                    self.rfile.read(length).decode('utf-8'))
            except Exception as e:
                self._send_json({'error': f'请求体解析失败: {e}'}, 400)
                return
            name = payload.get('name', '')
            version = payload.get('version', '')
            files = payload.get('files', {})
            if not isinstance(files, dict) or not files:
                self._send_json({'error': 'files 必须是非空字典'}, 400)
                return
            if not _validate_package(name, version, files.keys()):
                self._send_json({'error': '包校验失败'}, 400)
                return
            try:
                rel_path = _store_files(registry_dir, name, version, files)
            except RuntimeError as e:
                self._send_json({'error': str(e)}, 409)
                return
            self._send_json({'ok': True, 'package': name,
                             'version': version, 'path': rel_path})

    return RegistryHandler


def cmd_serve(registry_dir: str, host: str, port: int) -> int:
    """启动 HTTP 注册表服务（Ctrl-C 停止）"""
    from http.server import ThreadingHTTPServer
    server = ThreadingHTTPServer((host, port), _make_handler(registry_dir))
    print(f"🌐 HTTP 注册表服务: http://{host}:{port}"
          f"（registry: {os.path.relpath(registry_dir, PROJECT)}）")
    print("   GET  /index.json            查询索引")
    print("   GET  /pkg/<name>/<ver>/<f>  下载包文件")
    print("   POST /publish               {name, version, files} 发布")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
    finally:
        server.server_close()
    return 0


def _http_post_json(url: str, obj: dict) -> dict:
    from urllib.request import Request, urlopen
    req = Request(url, data=json.dumps(obj, ensure_ascii=False)
                  .encode('utf-8'),
                  headers={'Content-Type': 'application/json'},
                  method='POST')
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _http_get(url: str) -> bytes:
    from urllib.request import urlopen
    with urlopen(url, timeout=30) as resp:
        return resp.read()


def cmd_publish_url(pkg_dir: str, registry_url: str) -> int:
    """发布到 HTTP 注册表：读目录文本文件 → POST /publish"""
    pkg_dir = os.path.abspath(pkg_dir)
    manifest_path = os.path.join(pkg_dir, 'intent.toml')
    if not os.path.isfile(manifest_path):
        print(f"❌ 包目录缺少 intent.toml: {pkg_dir}")
        return 2
    try:
        data = _load_toml(manifest_path)
    except Exception as e:
        print(f"❌ intent.toml 解析失败: {e}")
        return 2
    project = data.get('project', {})
    name = project.get('name', '')
    version = project.get('version', '')
    files = _read_pkg_files(pkg_dir)
    if not _validate_package(name, version, files.keys()):
        return 2
    try:
        resp = _http_post_json(registry_url.rstrip('/') + '/publish',
                               {'name': name, 'version': version,
                                'files': files})
    except Exception as e:
        print(f"❌ 发布失败(HTTP): {e}")
        return 1
    if not resp.get('ok'):
        print(f"❌ 服务端拒绝: {resp.get('error')}")
        return 1
    print(f"✅ 已发布(HTTP) {name} v{version} → {registry_url}")
    return 0


def cmd_install_url(name: str, version, dest_dir: str,
                    registry_url: str) -> int:
    """从 HTTP 注册表安装：拉索引 → 按 files 清单逐文件下载 → 落 dest"""
    try:
        index = json.loads(
            _http_get(registry_url.rstrip('/') + '/index.json')
            .decode('utf-8'))
    except Exception as e:
        print(f"❌ 拉取索引失败: {e}")
        return 1
    pkg = index.get('packages', {}).get(name)
    if pkg is None:
        print(f"❌ 注册表没有包 '{name}'（HTTP index 查看可用包）")
        return 1
    if version is None:
        version = _latest_version(pkg['versions'])
        if version is None:
            print(f"❌ 包 '{name}' 没有任何版本")
            return 1
    elif version not in pkg['versions']:
        avail = ", ".join(sorted(pkg['versions']))
        print(f"❌ {name} 没有 v{version}（可用: {avail}）")
        return 1
    entry = pkg['versions'][version]
    target = os.path.join(dest_dir, name)
    if os.path.isdir(target):
        print(f"❌ 目标已存在: {os.path.relpath(target, PROJECT)}"
              f"（先删除再装，或换 dest）")
        return 1
    os.makedirs(target, exist_ok=True)
    base = registry_url.rstrip('/')
    try:
        for rel in entry.get('files', []):
            content = _http_get(f"{base}/pkg/{name}/{version}/{rel}")
            dst = os.path.join(target, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'wb') as f:
                f.write(content)
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return 1
    print(f"✅ 已安装(HTTP) {name} v{version} → "
          f"{os.path.relpath(target, PROJECT)}"
          f"（{len(entry.get('files', []))} 个文件）")
    print(f"   解释器模块搜索路径已含 {os.path.relpath(dest_dir, PROJECT)}/"
          f"，可直接 import {name}")
    return 0


def selftest() -> int:
    """临时目录 round-trip：构造包 → publish → list → install → 校验落盘"""
    with tempfile.TemporaryDirectory() as tmp:
        reg = os.path.join(tmp, 'registry')
        dest = os.path.join(tmp, 'lib')
        # 1) 构造两个版本的包
        pkg_src = os.path.join(tmp, 'src')
        os.makedirs(pkg_src)
        for ver in ('0.1.0', '0.2.0'):
            pkg_dir = os.path.join(pkg_src, f'greet-{ver}')
            os.makedirs(pkg_dir)
            with open(os.path.join(pkg_dir, 'intent.toml'), 'w',
                      encoding='utf-8') as f:
                f.write(f'[project]\nname = "greet"\nversion = "{ver}"\n')
            with open(os.path.join(pkg_dir, 'greet.intent'), 'w',
                      encoding='utf-8') as f:
                f.write(f'// greet v{ver}\n'
                        'def hello() -> String { return "hi"; }\n')
            rc = cmd_publish(pkg_dir, reg)
            if rc != 0:
                print(f"❌ selftest: publish {ver} 失败")
                return 1
        # 2) 重复发布同版本必须被拒
        dup = os.path.join(pkg_src, 'greet-0.1.0')
        if cmd_publish(dup, reg) == 0:
            print("❌ selftest: 重复版本未被拒绝")
            return 1
        # 3) list 可见
        if cmd_list(reg) != 0:
            print("❌ selftest: list 失败")
            return 1
        # 4) install 默认取最新版(0.2.0)
        if cmd_install('greet', None, dest, reg) != 0:
            print("❌ selftest: install 失败")
            return 1
        installed_ver = None
        with open(os.path.join(dest, 'greet', 'intent.toml'), 'r',
                  encoding='utf-8') as f:
            for line in f:
                m = re.search(r'version\s*=\s*"([^"]+)"', line)
                if m:
                    installed_ver = m.group(1)
        if installed_ver != '0.2.0':
            print(f"❌ selftest: 默认安装的不是最新版: {installed_ver}")
            return 1
        # 5) 指定旧版本安装到另一 dest
        dest2 = os.path.join(tmp, 'lib2')
        if cmd_install('greet', '0.1.0', dest2, reg) != 0:
            print("❌ selftest: 指定版本 install 失败")
            return 1
        # 6) 不存在包必须失败
        if cmd_install('no-such-pkg', None, dest2, reg) == 0:
            print("❌ selftest: 不存在的包未被拒绝")
            return 1
    # 7) HTTP round-trip：serve → publish(HTTP) → index(HTTP) → install(HTTP)
    if not _selftest_http(tmp):
        return 1
    print("✅ 注册表 selftest 全通（publish/拒绝重复/list/默认最新/指定旧版/"
          "拒绝不存在 + http round-trip: serve/publish/index/install）")
    return 0


def _selftest_http(tmp: str) -> bool:
    """HTTP 通道 round-trip：真起服务(临时端口) → HTTP 发布 → 索引查询
    → HTTP 安装 → 内容校验 → 重复发布被拒。任一环节失败返回 False。"""
    from http.server import ThreadingHTTPServer
    from threading import Thread
    reg = os.path.join(tmp, 'http-registry')
    os.makedirs(reg)
    server = ThreadingHTTPServer(('127.0.0.1', 0), _make_handler(reg))
    port = server.server_address[1]
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    url = f"http://127.0.0.1:{port}"
    try:
        # 1) 构造包并通过 HTTP 发布
        pkg_dir = os.path.join(tmp, 'http-src', 'greet-http')
        os.makedirs(pkg_dir)
        with open(os.path.join(pkg_dir, 'intent.toml'), 'w',
                  encoding='utf-8') as f:
            f.write('[project]\nname = "greet-http"\nversion = "1.0.0"\n')
        with open(os.path.join(pkg_dir, 'greet.intent'), 'w',
                  encoding='utf-8') as f:
            f.write('def hello() -> String { return "hi-http"; }\n')
        if cmd_publish_url(pkg_dir, url) != 0:
            print("❌ selftest: HTTP publish 失败")
            return False
        # 2) 索引经 HTTP 可见
        index = json.loads(_http_get(url + '/index.json').decode('utf-8'))
        if 'greet-http' not in index.get('packages', {}):
            print("❌ selftest: HTTP index 没有已发布的包")
            return False
        entry = index['packages']['greet-http']['versions'].get('1.0.0', {})
        if 'greet.intent' not in entry.get('files', []):
            print("❌ selftest: HTTP index 缺少 files 清单")
            return False
        # 3) HTTP 安装并校验内容
        dest = os.path.join(tmp, 'http-lib')
        if cmd_install_url('greet-http', None, dest, url) != 0:
            print("❌ selftest: HTTP install 失败")
            return False
        with open(os.path.join(dest, 'greet-http', 'greet.intent'),
                  'r', encoding='utf-8') as f:
            if 'hi-http' not in f.read():
                print("❌ selftest: HTTP 安装的文件内容不符")
                return False
        # 4) 重复发布必须被服务端拒绝
        if cmd_publish_url(pkg_dir, url) == 0:
            print("❌ selftest: HTTP 重复发布未被拒绝")
            return False
        return True
    finally:
        server.shutdown()
        server.server_close()


USAGE = """用法:
  python tools/registry.py publish <pkg-dir> [--registry DIR] [--registry-url URL]
                                                                 发布包(URL 则走 HTTP)
  python tools/registry.py list [--registry DIR]                列出注册表
  python tools/registry.py install <name> [--version V] [--dest DIR] [--registry DIR] [--registry-url URL]
                                                                 安装到 dest(默认 lib/; URL 则走 HTTP)
  python tools/registry.py serve [--registry DIR] [--host H] [--port P]
                                                                 启动 HTTP 注册表服务
  python tools/registry.py --selftest                           临时目录 round-trip 自检(含 HTTP)
"""


def main(argv: list) -> int:
    if not argv or argv[0] in ('-h', '--help', 'help'):
        print(USAGE)
        return 0 if argv else 2
    if argv[0] == '--selftest':
        return selftest()
    cmd = argv[0]
    rest = argv[1:]
    registry_dir = DEFAULT_REGISTRY
    registry_url = None
    host, port = '127.0.0.1', 8471
    # 通用选项提取
    if '--registry-url' in rest:
        i = rest.index('--registry-url')
        registry_url = rest[i + 1]
        del rest[i:i + 2]
    if '--registry' in rest:
        i = rest.index('--registry')
        registry_dir = os.path.abspath(rest[i + 1])
        del rest[i:i + 2]
    if '--host' in rest:
        i = rest.index('--host')
        host = rest[i + 1]
        del rest[i:i + 2]
    if '--port' in rest:
        i = rest.index('--port')
        port = int(rest[i + 1])
        del rest[i:i + 2]
    if cmd == 'serve':
        return cmd_serve(registry_dir, host, port)
    if cmd == 'publish':
        if len(rest) != 1:
            print(USAGE)
            return 2
        if registry_url:
            return cmd_publish_url(rest[0], registry_url)
        return cmd_publish(rest[0], registry_dir)
    if cmd == 'list':
        return cmd_list(registry_dir)
    if cmd == 'install':
        version = None
        dest_dir = DEFAULT_DEST
        if '--version' in rest:
            i = rest.index('--version')
            version = rest[i + 1]
            del rest[i:i + 2]
        if '--dest' in rest:
            i = rest.index('--dest')
            dest_dir = os.path.abspath(rest[i + 1])
            del rest[i:i + 2]
        if len(rest) != 1:
            print(USAGE)
            return 2
        if registry_url:
            return cmd_install_url(rest[0], version, dest_dir, registry_url)
        return cmd_install(rest[0], version, dest_dir, registry_dir)
    print(f"❌ 未知命令: {cmd}")
    print(USAGE)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
