#!/usr/bin/env python
# tools/registry.py — Intent 包注册表（E4）
#
# 心学为体：包的流转如意的流通——发布即立言，安装即借势
# 禅道为翼：注册表是一面镜子，照出社区的积累，不造中心的霸权
# 马哲为用：本地目录注册表 + 三个命令（publish/list/install），
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
#     registry.json           # 索引: {packages: {name: {versions: {ver: {path, published}}}}}
#     <name>/<version>/       # 包快照（publish 时整目录拷贝）
#
# 用法：
#   python tools/registry.py publish <pkg-dir> [--registry DIR]
#   python tools/registry.py list [--registry DIR]
#   python tools/registry.py install <name> [--version V] [--dest DIR] [--registry DIR]
#   python tools/registry.py --selftest          # 临时目录 round-trip 自检
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
    entry['versions'][version] = {
        'path': os.path.relpath(snapshot, registry_dir).replace(os.sep, '/'),
        'published': _now_iso(),
    }
    _save_registry_index(registry_dir, index)
    print(f"✅ 已发布 {name} v{version} → {os.path.relpath(snapshot, PROJECT)}")
    return 0


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
    print("✅ 注册表 selftest 全通（publish/拒绝重复/list/默认最新/指定旧版/拒绝不存在）")
    return 0


USAGE = """用法:
  python tools/registry.py publish <pkg-dir> [--registry DIR]   发布包
  python tools/registry.py list [--registry DIR]                列出注册表
  python tools/registry.py install <name> [--version V] [--dest DIR] [--registry DIR]
                                                                 安装到 dest(默认 lib/)
  python tools/registry.py --selftest                           临时目录 round-trip 自检
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
    # 通用选项提取
    if '--registry' in rest:
        i = rest.index('--registry')
        registry_dir = os.path.abspath(rest[i + 1])
        del rest[i:i + 2]
    if cmd == 'publish':
        if len(rest) != 1:
            print(USAGE)
            return 2
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
        return cmd_install(rest[0], version, dest_dir, registry_dir)
    print(f"❌ 未知命令: {cmd}")
    print(USAGE)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
