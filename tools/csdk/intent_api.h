/* Intent C 扩展 SDK — ABI v1（I3a）
 *
 * 契约（host ↔ 扩展）：
 *   1. 扩展编译成动态库（.dll / .so / .dylib），导出唯一符号
 *      `intent_module_register`；
 *   2. 调用方传入 IntentModule*，扩展把静态函数表写进去；
 *   3. 表项 = {名字, 元数(1|2), 原生函数指针}。
 *
 * 最小切片边界（spec §6 限制 30）：
 *   - 值类型只支持 long long（整数）——数值核；
 *   - 浮点/字符串/结构体/回调映射留 I3b+；
 *   - ABI 版本不匹配时加载器拒绝（显式失败，不静默降级）。
 *
 * 编译示例（在有编译器的机器上）：
 *   gcc   -shared -O2 -o intent_example.dll example.c      (Windows/MinGW)
 *   gcc   -shared -fPIC -O2 -o libintent_example.so example.c
 *   cl    /LD /O2 example.c                                (MSVC)
 */
#ifndef INTENT_API_H
#define INTENT_API_H

#define INTENT_ABI_VERSION 1

/* 原生函数签名：固定二元 long long（arity=1 时 b 未使用） */
typedef long long (*IntentFnPtr)(long long a, long long b);

typedef struct {
    const char   *name;   /* Intent 侧裸名调用的函数名 */
    int           arity;  /* 1 或 2 */
    IntentFnPtr   fn;
} IntentFuncEntry;

typedef struct {
    int              abi_version;
    int              count;
    IntentFuncEntry *funcs;
} IntentModule;

/* 扩展必须导出的注册入口 */
typedef void (*IntentRegisterFn)(IntentModule *out);

#endif /* INTENT_API_H */
