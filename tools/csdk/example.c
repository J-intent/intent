/* Intent C 扩展示例（I3a）— 高速数值核
 *
 * 两个函数：
 *   native_sum_range(lo, hi)  → Σlo..hi（闭区间）
 *   native_square(x)          → x²
 *
 * 构建：见 README.md / intent_api.h 头部注释。
 * 加载：python tools/csdk/selftest.py（自动检测编译器）
 */
#include "intent_api.h"

/* 显式置零的 unused 参数 — ABI 固定二元，一元函数吃 b 不用 */
#define UNUSED(x) (void)(x)

static long long native_sum_range(long long lo, long long hi) {
    long long s = 0;
    long long i;
    for (i = lo; i <= hi; i++) {
        s += i;
    }
    return s;
}

static long long native_square(long long x, long long unused) {
    UNUSED(unused);
    return x * x;
}

static IntentFuncEntry ENTRIES[] = {
    {"native_sum_range", 2, native_sum_range},
    {"native_square",    1, native_square},
};

static IntentModule MODULE = { INTENT_ABI_VERSION, 2, ENTRIES };

#if defined(_WIN32)
__declspec(dllexport)
#else
__attribute__((visibility("default")))
#endif
void intent_module_register(IntentModule *out) {
    *out = MODULE;
}
