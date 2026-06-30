import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open("src/mini_intent.py", encoding="utf-8").read()
# Find builtin registrations
methods = re.findall(r"'(\w+)': self\._builtin_", src)
print(f"Builtins: {len(methods)}")
for m in methods: print(f"  {m}")
# also find functions defined with def _builtin_
funcs = re.findall(r"def _builtin_(\w+)", src)
print(f"\nBuiltin functions: {len(funcs)}")
