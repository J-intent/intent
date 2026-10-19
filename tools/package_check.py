#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""官方包校验工具（E6）—— 扫描 packages/ 下的每个包并逐项验收。

检查项（全部通过才算合格）：
  1. intent.toml 可解析，且 [project] 的 name / version 合法；
  2. 至少一个实现文件（非 test_*.intent）含 requires / ensures 契约；
  3. 存在 test_*.intent，且用 `python src/mini_intent.py --test <文件>` 全部通过；
  4. README.md 非空，且有效内容不少于 5 行。

退出码：全部合格 → 0；任意包不合格 → 1；用法错误 → 2。
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

# 仓库根目录：tools/package_check.py 的上一级
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "mini_intent.py"
PACKAGES_DIR = ROOT / "packages"

# npm 风格：小写字母 / 数字 / 连字符，且不以连字符开头或结尾
NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
# semver 三段：主版本.次版本.补丁版本
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
# 契约关键字（词边界，避免匹配到注释里的普通单词）
CONTRACT_RE = re.compile(r"\b(requires|ensures)\b")


class CheckResult:
    """单个包的检查结果集合。"""

    def __init__(self, name: str, path: Path) -> None:
        self.name = name
        self.path = path
        self.items: list[tuple[bool, str]] = []

    def add(self, ok: bool, message: str) -> None:
        self.items.append((ok, message))

    @property
    def passed(self) -> bool:
        # 所有分项都通过（且至少执行了检查项）才算合格
        return bool(self.items) and all(ok for ok, _ in self.items)


def check_manifest(path: Path) -> tuple[bool, str]:
    """校验 intent.toml 可解析且 name / version 合法。"""
    manifest = path / "intent.toml"
    if not manifest.is_file():
        return False, "intent.toml: 文件不存在"

    try:
        with manifest.open("rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        return False, f"intent.toml: 解析失败 ({exc})"
    except OSError as exc:
        return False, f"intent.toml: 读取失败 ({exc})"

    project = data.get("project")
    if not isinstance(project, dict):
        return False, "intent.toml: 缺少 [project] 表"

    name = project.get("name")
    version = project.get("version")
    if not isinstance(name, str) or not NAME_RE.match(name):
        return False, f"intent.toml: name 非法 ({name!r})，应匹配 {NAME_RE.pattern}"
    if not isinstance(version, str) or not VERSION_RE.match(version):
        return False, f"intent.toml: version 非法 ({version!r})，应为三段 semver"

    return True, f"intent.toml: name={name} version={version}"


def implementation_files(path: Path) -> list[Path]:
    """实现文件 = 目录下的 *.intent，但排除 test_*.intent。"""
    return sorted(p for p in path.glob("*.intent") if not p.name.startswith("test_"))


def check_contracts(path: Path) -> bool:
    """至少一个实现文件里出现 requires / ensures。"""
    files = implementation_files(path)
    if not files:
        return False
    for file_path in files:
        try:
            text = file_path.read_text(encoding="utf-8")
        except OSError:
            continue
        if CONTRACT_RE.search(text):
            return True
    return False


def run_test_file(test_file: Path) -> tuple[bool, str]:
    """调用官方测试框架执行单个测试文件，返回 (是否通过, 摘要/错误)。"""
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    command = [sys.executable, str(SRC), "--test", str(test_file)]
    try:
        proc = subprocess.run(
            command,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return False, "测试超时（180s）"
    except OSError as exc:
        return False, f"无法启动解释器: {exc}"

    output = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode == 0:
        # 从测试框架输出里摘出「测试结果: x/y 通过」一行
        summary = ""
        for line in output.splitlines():
            if "测试结果" in line:
                summary = line.strip()
                break
        return True, summary or "测试通过"

    # 失败时把关键输出带出来，便于定位，绝不静默
    lines = [line for line in output.splitlines() if line.strip()]
    tail = "\n".join(lines[-12:]) if lines else "(无输出)"
    return False, f"退出码 {proc.returncode}\n{tail}"


def check_tests(path: Path) -> list[tuple[bool, str]]:
    """存在 test_*.intent，且每个测试文件都通过。返回逐文件结果。"""
    test_files = sorted(path.glob("test_*.intent"))
    if not test_files:
        return [(False, "测试: 缺少 test_*.intent")]

    details: list[tuple[bool, str]] = []
    for test_file in test_files:
        passed, message = run_test_file(test_file)
        if passed:
            details.append((True, f"测试: {test_file.name} 通过 ({message})"))
        else:
            details.append((False, f"测试: {test_file.name} 失败 ({message})"))
    return details


def check_readme(path: Path) -> tuple[bool, str]:
    """README.md 存在且有效内容 ≥ 5 行。"""
    readme = path / "README.md"
    if not readme.is_file():
        return False, "README.md: 文件不存在"
    try:
        text = readme.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"README.md: 读取失败 ({exc})"

    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 5:
        return False, f"README.md: 有效内容仅 {len(lines)} 行（要求 ≥ 5）"
    return True, f"README.md: {len(lines)} 行"


def check_package(path: Path) -> CheckResult:
    """对单个包目录执行全部检查项。"""
    result = CheckResult(path.name, path)

    ok, message = check_manifest(path)
    result.add(ok, message)

    impls = implementation_files(path)
    if check_contracts(path):
        names = ", ".join(p.name for p in impls)
        result.add(True, f"契约: 实现文件含 requires/ensures ({names})")
    elif not impls:
        result.add(False, "契约: 没有实现文件（非 test_*.intent）")
    else:
        result.add(False, "契约: 实现文件中未找到 requires/ensures")

    for detail_ok, detail in check_tests(path):
        result.add(detail_ok, detail)

    ok, message = check_readme(path)
    result.add(ok, message)

    return result


def print_result(result: CheckResult, index: int, total: int) -> None:
    """打印单个包的分项结果。"""
    print(f"[{index}/{total}] {result.name}  ({result.path})")
    for ok, message in result.items:
        mark = "✅" if ok else "❌"
        # 多行错误逐行缩进，保持可读
        first, *rest = message.splitlines()
        print(f"  {mark} {first}")
        for line in rest:
            print(f"     {line}")
    print()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="官方包校验工具：检查 packages/ 下每个包的 manifest、契约、测试与 README。",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="扫描 packages/ 下的全部包（必选）",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if not args.all:
        print("❌ 请使用 --all 扫描 packages/ 下的全部官方包")
        return 2

    if not PACKAGES_DIR.is_dir():
        print(f"❌ 包目录不存在: {PACKAGES_DIR}")
        return 1
    if not SRC.is_file():
        print(f"❌ 解释器不存在: {SRC}")
        return 1

    package_dirs = sorted(p for p in PACKAGES_DIR.iterdir() if p.is_dir())
    if not package_dirs:
        print(f"❌ {PACKAGES_DIR} 下没有任何包")
        return 1

    print("=" * 60)
    print(f"官方包检查 — {len(package_dirs)} 个包，目录: {PACKAGES_DIR}")
    print("=" * 60)

    results: list[CheckResult] = []
    for index, path in enumerate(package_dirs, start=1):
        result = check_package(path)
        results.append(result)
        print_result(result, index, len(package_dirs))

    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]

    print("=" * 60)
    if failed:
        names = ", ".join(r.name for r in failed)
        print(f"❌ 检查未通过: {len(passed)}/{len(results)} 个包合格；不合格: {names}")
        print("=" * 60)
        return 1

    print(f"✅ 全部合格: {len(passed)}/{len(results)} 个包通过（manifest/契约/测试/README）")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
