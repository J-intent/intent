#!/usr/bin/env python
# tools/csdk/loader.py — C 扩展 SDK 加载器（I3a）
#
# 心学为体：扩展是「别人的手」——ABI 是握手礼，握手成不成在版本与签名上见真章。
# 禅道为翼：用 ctypes 读 C 的结构体与函数表，不写胶水代码生成器。
# 马哲为用：加载即注册——表里的每个函数指针直接变成 Intent 可调用的内置。
#
# 用法：
#   from loader import load_native
#   mod = load_native('intent_example.dll')
#   builtins = mod.functions()          # {name: 可注入 run_source 的 builtin}
#   run_source(code, inject_builtins=builtins)
#
# 无编译器场景（selftest 用）：make_simulated_module() 用 ctypes 回调
# 构成与 C 同构的内存函数表——走同一条 load→读表→调用 路径，
# 证明 ABI 本身可用；C 编译产物需在有编译器的机器上验证。

import ctypes
import os
import sys
import weakref

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT, 'src'))

from mini_intent import IntValue  # noqa: E402

ABI_VERSION = 1

# I3b: GC 钩子 — 原生模块生命周期登记（弱引用，模块被 GC 即自动出表）
_LIVE = weakref.WeakSet()


def live_native_modules() -> int:
    """当前存活的原生模块数（GC 钩子的可观测出口）"""
    return len(_LIVE)


def unload_native(mod: 'NativeModule') -> None:
    """注销原生模块：出登记表并断开库引用（显式卸载，不等 GC）"""
    _LIVE.discard(mod)
    mod.lib = None
    mod.module = IntentModule(0, 0, None)

IntentFnPtr = ctypes.CFUNCTYPE(ctypes.c_longlong,
                               ctypes.c_longlong, ctypes.c_longlong)


class IntentFuncEntry(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('arity', ctypes.c_int),
        ('fn', IntentFnPtr),
    ]


class IntentModule(ctypes.Structure):
    _fields_ = [
        ('abi_version', ctypes.c_int),
        ('count', ctypes.c_int),
        ('funcs', ctypes.POINTER(IntentFuncEntry)),
    ]


class NativeModule:
    """已加载的原生模块：持有库引用 + 函数表，暴露 Intent builtin 包装"""

    def __init__(self, lib, module, keepalive=None):
        self.lib = lib
        self.module = module
        self._keepalive = keepalive or []

    def functions(self) -> dict:
        out = {}
        for i in range(self.module.count):
            entry = self.module.funcs[i]
            name = entry.name.decode('utf-8')
            arity = entry.arity
            raw = entry.fn

            def wrapper(args, _fn=raw, _arity=arity, _name=name):
                if len(args) != _arity:
                    raise TypeError(
                        f"{_name}() 期望 {_arity} 个整数参数, 得到 {len(args)}")
                a = int(args[0].value)
                b = int(args[1].value) if _arity == 2 else 0
                return IntValue(int(_fn(a, b)))

            out[name] = wrapper
        return out

    def names(self) -> list:
        return [self.module.funcs[i].name.decode('utf-8')
                for i in range(self.module.count)]


def _check_abi(module) -> None:
    if module.abi_version != ABI_VERSION:
        raise RuntimeError(
            f"ABI 版本不匹配: 扩展 {module.abi_version}, 加载器 {ABI_VERSION}")


def load_native(path: str) -> NativeModule:
    """加载 .dll/.so 并读注册表；符号缺失/版本不符 → 显式失败"""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"动态库不存在: {path}")
    lib = ctypes.CDLL(path)
    if not hasattr(lib, 'intent_module_register'):
        raise RuntimeError(
            f"动态库未导出 intent_module_register: {path}"
            "(扩展须按 intent_api.h 实现注册入口)")
    register = lib.intent_module_register
    register.argtypes = [ctypes.POINTER(IntentModule)]
    register.restype = None
    module = IntentModule()
    register(ctypes.byref(module))
    _check_abi(module)
    mod = NativeModule(lib, module)
    _LIVE.add(mod)  # I3b: GC 钩子登记
    return mod


def make_simulated_module() -> NativeModule:
    """ABI 等价的 ctypes 回调表（无 C 编译器时的验证路径）

    与真 DLL 走同一条「读结构体 → 取函数指针 → 调用」路径。
    返回的 NativeModule 持有表与回调引用（防 GC 回收函数指针）。
    """
    entries = (IntentFuncEntry * 2)()
    entries[0].name = b'native_sum_range'
    entries[0].arity = 2
    entries[0].fn = IntentFnPtr(lambda lo, hi: sum(range(lo, hi + 1)))
    entries[1].name = b'native_square'
    entries[1].arity = 1
    entries[1].fn = IntentFnPtr(lambda x, _unused: x * x)
    module = IntentModule(ABI_VERSION, 2, entries)
    mod = NativeModule(None, module, keepalive=[entries])
    _LIVE.add(mod)  # I3b: GC 钩子登记
    return mod


def check_abi_rejected(abi_version: int) -> bool:
    """自检钩子：构造指定 ABI 版本的模块，验证加载器拒绝逻辑"""
    try:
        _check_abi(IntentModule(abi_version, 0, None))
        return abi_version == ABI_VERSION
    except RuntimeError:
        return abi_version != ABI_VERSION
