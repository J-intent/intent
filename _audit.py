import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")

# 1. 主文件规模
src = open("src/mini_intent.py", encoding="utf-8").read()
lines = src.count("\n")
print(f"=== mini_intent.py: {lines} 行 ===")

# 2. AST 节点
classes = re.findall(r"class (\w+)\(.*?\):", src)
print(f"\n=== AST/类型节点: {len(classes)} ===")
for c in classes[:30]: print(f"  {c}")
if len(classes) > 30: print(f"  ... +{len(classes)-30} more")

# 3. Builtins
builtin_section = src.find("self.builtins =")
end = src.find("}", builtin_section)
b_text = src[builtin_section:end]
builtins = re.findall(r"'(\w+)':", b_text)
print(f"\n=== Builtins: {len(builtins)} ===")
print(f"  {', '.join(builtins)}")

# 4. 标准库模块
std_dir = "std"
if os.path.exists(std_dir):
    for root, dirs, files in os.walk(std_dir):
        for f in files:
            if f.endswith(".intent"):
                fp = os.path.join(root, f)
                lc = len(open(fp, encoding="utf-8").read().split("\n"))
                print(f"  {fp}: {lc} lines")

# 5. 示例/测试文件
ex_dir = "examples"
if os.path.exists(ex_dir):
    tests = [f for f in os.listdir(ex_dir) if f.endswith(".intent") and not f.startswith("_")]
    print(f"\n=== 测试/示例: {len(tests)} ===")
    for t in tests:
        print(f"  {t}")
    # also show temp files
    temps = [f for f in os.listdir(ex_dir) if f.endswith(".intent") and f.startswith("_")]
    print(f"\n临时测试: {len(temps)}")

# 6. Resolver
res = open("src/intent_resolver.py", encoding="utf-8").read()
print(f"\n=== Resolver: {res.count(chr(10))} 行 ===")

# 7. Git log
import subprocess
result = subprocess.run(["git", "log", "--oneline", "-10"], capture_output=True, text=True, cwd="D:/Desktop/worksheet/intent")
print(f"\n=== Git 最近 10 提交 ===")
print(result.stdout)
