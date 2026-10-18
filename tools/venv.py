#!/usr/bin/env python
# tools/venv.py — Intent 虚拟环境（PK2）
#
# 心学为体：环境即心意所住之处——项目各住各的院子，互不串门
# 禅道为翼：缓存是中转的驿站，不是囤积的仓库；用过即留，不留不用
# 马哲为用：.venv 目录隔离 + 全局包缓存 + PATH 管理三件套，
#           与 PK1 的 intent.toml/lib/ 安装链路无缝衔接
#
# 用法：
#   python tools/venv.py create [目录]     创建 .venv（默认当前目录）
#   python tools/venv.py install <源>      装入活动 venv（经全局缓存中转）
#   python tools/venv.py list              列出 venv 内包 + 全局缓存统计
#   python tools/venv.py activate          打印激活片段（PATH + INTENT_VENV）
#   python tools/venv.py --selftest        隔离性自测（临时目录，零污染）
#
# 环境变量：
#   INTENT_HOME   覆盖默认 ~/.intent（缓存与全局库的根；selftest 用它隔离）
#
# 与解释器的衔接：.venv/lib 由 mini_intent.py 加入模块搜索路径，
# 且优先于全局库——项目有自己的院子，就不去公共池塘打水。

import json
import os
import re
import shutil
import sys
import tempfile
import time

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT, 'src'))

VENV_DIR = '.venv'
VENV_META = 'venv.json'


def intent_home() -> str:
    """INTENT_HOME 或默认 ~/.intent — 全局缓存与全局库的根"""
    return os.environ.get('INTENT_HOME') or os.path.join(
        os.path.expanduser('~'), '.intent')


def cache_root() -> str:
    return os.path.join(intent_home(), 'cache', 'packages')


def global_lib() -> str:
    return os.path.join(intent_home(), 'lib')


def venv_lib(venv_dir: str) -> str:
    return os.path.join(venv_dir, 'lib')


def venv_bin(venv_dir: str) -> str:
    return os.path.join(venv_dir, 'bin')


def find_venv(start: str = '.') -> str:
    """从 start 向上找最近的 .venv（活动 venv 判定）"""
    cur = os.path.abspath(start)
    while True:
        cand = os.path.join(cur, VENV_DIR)
        if os.path.isdir(cand):
            return cand
        parent = os.path.dirname(cur)
        if parent == cur:
            return ''
        cur = parent


def _read_pkg_meta(pkg_dir: str):
    """读包的 intent.toml → (name, version)；读不到返回 (None, None)"""
    from mini_intent import load_project_manifest
    manifest = load_project_manifest(os.path.join(pkg_dir, 'intent.toml'))
    if manifest is None:
        return None, None
    return manifest.get('name'), manifest.get('version') or '0.0.0'


def create_venv(base_dir: str = '.') -> str:
    """创建 .venv：lib/（隔离安装目标）+ bin/（PATH 入口）+ venv.json"""
    venv_dir = os.path.join(os.path.abspath(base_dir), VENV_DIR)
    if os.path.isdir(venv_dir):
        print(f"⬜ {VENV_DIR} 已存在: {venv_dir}")
        return venv_dir
    os.makedirs(venv_lib(venv_dir), exist_ok=True)
    os.makedirs(venv_bin(venv_dir), exist_ok=True)
    meta = {'created_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'project': os.path.basename(os.path.abspath(base_dir))}
    with open(os.path.join(venv_dir, VENV_META), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"✅ 虚拟环境已创建: {venv_dir}")
    print(f"   lib/  隔离包目录（解释器优先搜索）")
    print(f"   bin/  PATH 入口（activate 后生效）")
    return venv_dir


def _copy_source_to_cache(source: str, name: str, version: str) -> str:
    """源 → 全局缓存 ~/.intent/cache/packages/<name>@<version>/"""
    cache_dir = os.path.join(cache_root(), f"{name}@{version}")
    if os.path.isdir(cache_dir):
        return cache_dir
    os.makedirs(cache_root(), exist_ok=True)
    tmp = cache_dir + '.tmp'
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(os.path.abspath(source), tmp,
                    ignore=shutil.ignore_patterns('.git', '__pycache__'))
    os.replace(tmp, cache_dir)  # 原子落位, 半成品不进缓存
    return cache_dir


def venv_install(source: str, venv_dir: str = '') -> bool:
    """安装包进 venv：源 → 全局缓存（命中跳过）→ .venv/lib/<name>"""
    if not venv_dir:
        venv_dir = find_venv()
    if not venv_dir:
        print(f"❌ 找不到 {VENV_DIR}（先 create，或用 --install 走全局库）")
        return False
    src_path = os.path.abspath(source)
    if not os.path.isdir(src_path):
        print(f"❌ 包源不存在: {src_path}")
        return False
    name, version = _read_pkg_meta(src_path)
    if not name:
        print(f"❌ {src_path} 缺少 intent.toml 或 name 字段")
        return False
    cache_dir = os.path.join(cache_root(), f"{name}@{version}")
    hit = os.path.isdir(cache_dir)
    if hit:
        print(f"  ♻️  缓存命中 {name}@{version}")
    else:
        cache_dir = _copy_source_to_cache(src_path, name, version)
        print(f"  📥 入缓存 {name}@{version}")
    from mini_intent import install_dependency
    ok = install_dependency(name, cache_dir, lib_dir=venv_lib(venv_dir))
    if ok:
        print(f"✅ 已装入 {venv_lib(venv_dir)}/{name}（来自缓存，与全局库隔离）")
    return ok


def list_venv(venv_dir: str = '') -> None:
    """列出 venv 内包（名+版本）+ 全局缓存占用"""
    if not venv_dir:
        venv_dir = find_venv()
    if not venv_dir:
        print(f"❌ 找不到 {VENV_DIR}")
        return
    lib = venv_lib(venv_dir)
    pkgs = []
    if os.path.isdir(lib):
        for entry in sorted(os.listdir(lib)):
            if os.path.isdir(os.path.join(lib, entry)):
                _n, v = _read_pkg_meta(os.path.join(lib, entry))
                pkgs.append((entry, v or '?'))
    print(f"📦 {venv_dir} 内 {len(pkgs)} 个包:")
    for name, ver in pkgs:
        print(f"   {name}  {ver}")
    cache = cache_root()
    if os.path.isdir(cache):
        entries = os.listdir(cache)
        size = sum(
            os.path.getsize(os.path.join(root, f))
            for root, _d, files in os.walk(cache) for f in files)
        print(f"🗄️  全局缓存 {len(entries)} 项, {size / 1024:.1f} KB "
              f"({intent_home()})")
    else:
        print(f"🗄️  全局缓存为空 ({intent_home()})")


def activate_snippet(venv_dir: str = '') -> str:
    """打印激活片段 — PATH 前置 venv/bin, INTENT_VENV 标记活动环境"""
    if not venv_dir:
        venv_dir = find_venv()
    if not venv_dir:
        return f"echo '找不到 {VENV_DIR}; 先 create'"
    abs_dir = os.path.abspath(venv_dir)
    return (f"export INTENT_VENV={abs_dir}\n"
            f"export PATH=\"{venv_bin(abs_dir)}:$PATH\"")


# ── 自测：隔离性是 PK2 的判定标准（两项目互不污染） ──

def _make_fixture_pkg(root: str, name: str, version: str) -> str:
    """临时目录里造一个带 intent.toml 的包（selftest 专用）"""
    pkg = os.path.join(root, f'{name}-{version}')
    os.makedirs(pkg, exist_ok=True)
    with open(os.path.join(pkg, 'intent.toml'), 'w', encoding='utf-8') as f:
        f.write(f'[project]\nname = "{name}"\nversion = "{version}"\n')
    mod = os.path.join(pkg, f'{name}.intent')
    with open(mod, 'w', encoding='utf-8') as f:
        f.write(f'// {name} v{version}\nlet pkg_version = "{version}";\n')
    return pkg


def selftest() -> int:
    tmp = tempfile.mkdtemp(prefix='intent-venv-test-')
    old_home = os.environ.get('INTENT_HOME')
    passed = failed = 0

    def check(cond, msg):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  ✅ {msg}")
        else:
            failed += 1
            print(f"  ❌ {msg}")

    try:
        # 全程隔离在临时 INTENT_HOME — 不碰真实 ~/.intent
        os.environ['INTENT_HOME'] = os.path.join(tmp, 'home')
        proj_a = os.path.join(tmp, 'projA')
        proj_b = os.path.join(tmp, 'projB')
        os.makedirs(proj_a)
        os.makedirs(proj_b)
        pkg_v1 = _make_fixture_pkg(tmp, 'pkga', '1.0.0')
        pkg_v2 = _make_fixture_pkg(tmp, 'pkga', '2.0.0')

        # 1. create: 结构完整
        create_venv(proj_a)
        va = os.path.join(proj_a, VENV_DIR)
        check(os.path.isdir(venv_lib(va)) and os.path.isdir(venv_bin(va))
              and os.path.isfile(os.path.join(va, VENV_META)),
              "create: .venv/{lib,bin,venv.json} 结构完整")

        # 2. install v1 进 A: 缓存 + venv lib 双落
        check(venv_install(pkg_v1, va), "install: v1 装入 projA")
        installed = os.path.join(venv_lib(va), 'pkga')
        check(os.path.isfile(os.path.join(installed, 'pkga.intent')),
              "install: .venv/lib/pkga 就位")
        check(os.path.isdir(os.path.join(cache_root(), 'pkga@1.0.0')),
              "install: 全局缓存 pkga@1.0.0 已中转")

        # 3. 隔离性: B 装 v2, A 的 v1 不受污染, 全局库不被动
        create_venv(proj_b)
        vb = os.path.join(proj_b, VENV_DIR)
        venv_install(pkg_v2, vb)
        _n, ver_a = _read_pkg_meta(installed)
        _n2, ver_b = _read_pkg_meta(os.path.join(venv_lib(vb), 'pkga'))
        check(ver_a == '1.0.0' and ver_b == '2.0.0',
              "隔离: 两项目各装各版本（A=1.0.0, B=2.0.0）")
        check(not os.path.isdir(global_lib()),
              "隔离: 全局库目录未被创建（venv 安装不落全局）")

        # 4. 缓存复用: 同版本再装命中缓存（不重新拷贝源）
        before = os.path.getmtime(os.path.join(cache_root(), 'pkga@1.0.0'))
        time.sleep(0.05)
        venv_install(pkg_v1, va)
        after = os.path.getmtime(os.path.join(cache_root(), 'pkga@1.0.0'))
        check(before == after, "缓存: 同版本重装命中（缓存不重写）")

        # 5. activate: PATH + INTENT_VENV
        snip = activate_snippet(va)
        check('PATH=' in snip and f'INTENT_VENV={os.path.abspath(va)}' in snip,
              "activate: 片段含 PATH 前置与 INTENT_VENV 标记")

        # 6. list: 能看到包与版本
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            list_venv(va)
        out = buf.getvalue()
        check('pkga' in out and '1.0.0' in out, "list: 列出包名与版本")
    finally:
        if old_home is None:
            os.environ.pop('INTENT_HOME', None)
        else:
            os.environ['INTENT_HOME'] = old_home
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n  venv selftest: {passed}/{passed + failed} 通过"
          f"{'' if not failed else f', {failed} 失败'}")
    return 0 if not failed else 1


def main(argv):
    if argv and argv[0] == '--selftest':
        return selftest()
    if not argv or argv[0] in ('-h', '--help', 'help'):
        print(__doc__)
        return 0 if argv else 2
    cmd, rest = argv[0], argv[1:]
    if cmd == 'create':
        create_venv(rest[0] if rest else '.')
        return 0
    if cmd == 'install':
        if not rest:
            print("❌ install 需要包源目录: python tools/venv.py install <pkg-dir>")
            return 2
        return 0 if venv_install(rest[0]) else 1
    if cmd == 'list':
        list_venv()
        return 0
    if cmd == 'activate':
        print(activate_snippet())
        return 0
    print(f"❌ 未知子命令: {cmd}（create/install/list/activate/--selftest）")
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
