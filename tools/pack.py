#!/usr/bin/env python
# tools/pack.py — Intent 包构建与分发（P4）
#
# 心学为体：打包是「立言成书」——把一目录的意图收拢成一个可流转的文件。
# 禅道为翼：格式用 zip + JSON 元数据（标准库即可读写，任何人能拆开看），
#           不造私有二进制格式。
# 马哲为用：安装即落地——解包到 dest/<name>/，按 [scripts] 生成可执行入口。
#
# .intentp 结构（format_version 1）：
#   metadata.json           {format_version, name, version, files, entry_points, built_at}
#   files/<原目录结构>       包内所有文件
#
# 用法：
#   python tools/pack.py build <pkg-dir> [--out FILE]     构建 .intentp
#   python tools/pack.py inspect <file.intentp>           查看元数据
#   python tools/pack.py install <file.intentp> [--dest DIR]  解包 + 生成入口
#   python tools/pack.py --selftest                       build→inspect→install→跑入口
#
# 入口点约定（intent.toml）：
#   [scripts]
#   demo = "demo.intent"        # 安装后生成 dest/bin/demo(.bat / 无后缀 sh)
# 生成 .bat(Windows) 与 sh(Unix) 两份启动器，解释器路径嵌入为安装时的
# sys.executable（不依赖 PATH）。`:func` 函数级入口留后续切片（spec §6 限制 29）。

import json
import os
import subprocess
import sys
import tempfile
import zipfile

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DEST = os.path.join(PROJECT, 'lib')
FORMAT_VERSION = 1


def _load_toml(path: str) -> dict:
    import tomllib
    with open(path, 'rb') as f:
        return tomllib.load(f)


def _pkg_files(pkg_dir: str):
    """包内文件相对路径清单（排除缓存/产物）"""
    out = []
    for root, dirs, fnames in os.walk(pkg_dir):
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git')]
        for fn in fnames:
            if fn.endswith(('.pyc', '.intentp')):
                continue
            rel = os.path.relpath(os.path.join(root, fn), pkg_dir)
            out.append(rel.replace(os.sep, '/'))
    return sorted(out)


def build(pkg_dir: str, out_path: str = None) -> int:
    """构建 .intentp：校验清单 → 写 metadata + files → 落盘"""
    pkg_dir = os.path.abspath(pkg_dir)
    manifest = os.path.join(pkg_dir, 'intent.toml')
    if not os.path.isfile(manifest):
        print(f"❌ 包目录缺少 intent.toml: {pkg_dir}")
        return 2
    try:
        data = _load_toml(manifest)
    except Exception as e:
        print(f"❌ intent.toml 解析失败: {e}")
        return 2
    project = data.get('project', {})
    name = project.get('name', '')
    version = project.get('version', '')
    if not name or not version:
        print("❌ intent.toml 缺少 [project] name/version")
        return 2
    files = _pkg_files(pkg_dir)
    if not any(f.endswith('.intent') for f in files):
        print("❌ 包里没有 .intent 源码文件")
        return 2
    scripts = data.get('scripts', {}) or {}
    # 入口脚本必须指向包内文件
    for cmd, target in scripts.items():
        if target not in files:
            print(f"❌ [scripts] {cmd} 指向不存在的文件: {target}")
            return 2
    meta = {
        'format_version': FORMAT_VERSION,
        'name': name,
        'version': version,
        'files': files,
        'entry_points': scripts,
        'built_at': _now_iso(),
    }
    if out_path is None:
        out_path = os.path.join(os.getcwd(), f"{name}-{version}.intentp")
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('metadata.json',
                   json.dumps(meta, ensure_ascii=False, indent=2))
        for rel in files:
            z.write(os.path.join(pkg_dir, rel), f"files/{rel}")
    size = os.path.getsize(out_path)
    print(f"✅ 已构建 {name} v{version} → {os.path.relpath(out_path, PROJECT)}"
          f"（{len(files)} 个文件, {size} 字节）")
    return 0


def _read_meta(path: str) -> dict:
    with zipfile.ZipFile(path, 'r') as z:
        return json.loads(z.read('metadata.json').decode('utf-8'))


def inspect(pkg_path: str) -> int:
    try:
        meta = _read_meta(pkg_path)
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return 1
    print(f"  包名    : {meta.get('name')}")
    print(f"  版本    : {meta.get('version')}")
    print(f"  格式版本: {meta.get('format_version')}")
    print(f"  构建时间: {meta.get('built_at')}")
    print(f"  文件({len(meta.get('files', []))}): "
          + ", ".join(meta.get('files', [])))
    eps = meta.get('entry_points', {})
    if eps:
        print("  入口点  : " + ", ".join(f"{k} → {v}" for k, v in eps.items()))
    return 0


def install(pkg_path: str, dest_dir: str) -> int:
    """解包到 dest/<name>/，按 [scripts] 生成启动器（bin/）"""
    try:
        meta = _read_meta(pkg_path)
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return 1
    name = meta.get('name', '')
    version = meta.get('version', '')
    target = os.path.join(dest_dir, name)
    if os.path.isdir(target):
        print(f"❌ 目标已存在: {os.path.relpath(target, PROJECT)}"
              f"（先删除再装，或换 dest）")
        return 1
    os.makedirs(target, exist_ok=True)
    with zipfile.ZipFile(pkg_path, 'r') as z:
        for rel in meta.get('files', []):
            data = z.read(f"files/{rel}")
            dst = os.path.join(target, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'wb') as f:
                f.write(data)
    # 入口点：.bat(Windows) + sh(Unix)，解释器路径嵌入 sys.executable
    bin_dir = os.path.join(dest_dir, 'bin')
    actions = []
    for cmd, rel in (meta.get('entry_points') or {}).items():
        os.makedirs(bin_dir, exist_ok=True)
        entry_file = os.path.join(target, rel)
        interpreter = os.path.join(PROJECT, 'src', 'mini_intent.py')
        bat = os.path.join(bin_dir, f"{cmd}.bat")
        # .bat 必须用系统 ANSI 编码写：cmd.exe 按代码页读脚本，
        # UTF-8 写的中文路径(如用户名)会被读成乱码 → “找不到路径”
        try:
            bat_enc = 'mbcs' if sys.platform == 'win32' else 'utf-8'
            with open(bat, 'w', encoding=bat_enc, errors='replace',
                      newline='') as f:
                f.write(f'@echo off\r\n'
                        f'"{sys.executable}" "{interpreter}" "{entry_file}" %*\r\n')
        except LookupError:
            with open(bat, 'w', encoding='utf-8', errors='replace',
                      newline='') as f:
                f.write(f'@echo off\r\n'
                        f'"{sys.executable}" "{interpreter}" "{entry_file}" %*\r\n')
        sh = os.path.join(bin_dir, cmd)
        with open(sh, 'w', encoding='utf-8', newline='\n') as f:
            f.write(f'#!/bin/sh\n'
                    f'"{sys.executable}" "{interpreter}" "{entry_file}" "$@"\n')
        os.chmod(sh, 0o755)
        actions.append(f"{cmd} → bin/{cmd}(.bat)")
    print(f"✅ 已安装 {name} v{version} → {os.path.relpath(target, PROJECT)}"
          f"（{len(meta.get('files', []))} 个文件）")
    if actions:
        print("   入口点: " + ", ".join(actions))
    return 0


def _now_iso() -> str:
    from datetime import datetime
    return datetime.now().isoformat(timespec='seconds')


def selftest() -> int:
    """build → inspect → install → 真跑入口点（round-trip）"""
    with tempfile.TemporaryDirectory() as tmp:
        pkg_dir = os.path.join(tmp, 'demo-pkg')
        os.makedirs(pkg_dir)
        with open(os.path.join(pkg_dir, 'intent.toml'), 'w',
                  encoding='utf-8') as f:
            f.write('[project]\nname = "demo"\nversion = "1.0.0"\n\n'
                    '[scripts]\ndemo = "demo.intent"\n')
        with open(os.path.join(pkg_dir, 'demo.intent'), 'w',
                  encoding='utf-8') as f:
            f.write('print("hello from demo");\n')
        out = os.path.join(tmp, 'demo-1.0.0.intentp')
        if build(pkg_dir, out) != 0:
            print("❌ selftest: build 失败")
            return 1
        if not os.path.isfile(out):
            print("❌ selftest: 产物不存在")
            return 1
        # inspect 元数据完整性
        try:
            meta = _read_meta(out)
        except Exception as e:
            print(f"❌ selftest: 元数据不可读: {e}")
            return 1
        if meta.get('name') != 'demo' or meta.get('version') != '1.0.0':
            print("❌ selftest: 元数据 name/version 不符")
            return 1
        if 'demo.intent' not in meta.get('files', []):
            print("❌ selftest: files 清单缺 demo.intent")
            return 1
        if meta.get('entry_points', {}).get('demo') != 'demo.intent':
            print("❌ selftest: entry_points 不符")
            return 1
        # install + 启动器
        dest = os.path.join(tmp, 'lib')
        if install(out, dest) != 0:
            print("❌ selftest: install 失败")
            return 1
        installed = os.path.join(dest, 'demo', 'demo.intent')
        if not os.path.isfile(installed):
            print("❌ selftest: 文件未落盘")
            return 1
        if sys.platform == 'win32':
            launcher = os.path.join(dest, 'bin', 'demo.bat')
        else:
            launcher = os.path.join(dest, 'bin', 'demo')
        if not os.path.isfile(launcher):
            print("❌ selftest: 启动器未生成")
            return 1
        # 真跑启动器（这才是 round-trip 的终点：装完能执行）
        # 字节捕获 + UTF-8 容错解码：中文 Windows 的默认代码页(GBK)
        # 与解释器的 UTF-8 输出不一致，text=True 会炸在解码上
        r = subprocess.run([launcher], capture_output=True,
                           timeout=60, shell=(sys.platform == 'win32'))
        out_text = ((r.stdout or b'').decode('utf-8', 'replace')
                    + (r.stderr or b'').decode('utf-8', 'replace'))
        if 'hello from demo' not in out_text:
            print(f"❌ selftest: 启动器执行失败: {out_text.strip()[:200]}")
            return 1
        # 重复安装必须被拒
        if install(out, dest) == 0:
            print("❌ selftest: 重复安装未被拒绝")
            return 1
    print("✅ pack selftest 全通（build → metadata → install → 启动器执行 → "
          "拒绝重复: round-trip 完成）")
    return 0


USAGE = """用法:
  python tools/pack.py build <pkg-dir> [--out FILE]        构建 .intentp
  python tools/pack.py inspect <file.intentp>              查看元数据
  python tools/pack.py install <file.intentp> [--dest DIR] 解包 + 生成入口(bin/)
  python tools/pack.py --selftest                          build→install→跑入口 round-trip
"""


def main(argv) -> int:
    if not argv or argv[0] in ('-h', '--help', 'help'):
        print(USAGE)
        return 0 if argv else 2
    if argv[0] == '--selftest':
        return selftest()
    cmd = argv[0]
    rest = argv[1:]
    out_path = None
    dest_dir = DEFAULT_DEST
    if '--out' in rest:
        i = rest.index('--out')
        out_path = rest[i + 1]
        del rest[i:i + 2]
    if '--dest' in rest:
        i = rest.index('--dest')
        dest_dir = os.path.abspath(rest[i + 1])
        del rest[i:i + 2]
    if cmd == 'build' and len(rest) == 1:
        return build(rest[0], out_path)
    if cmd == 'inspect' and len(rest) == 1:
        return inspect(rest[0])
    if cmd == 'install' and len(rest) == 1:
        return install(rest[0], dest_dir)
    print(f"❌ 用法错误: {cmd}")
    print(USAGE)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
