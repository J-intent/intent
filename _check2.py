import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open("src/mini_intent.py", encoding="utf-8").read()
idx = src.find("elif isinstance(expr, ListExpr)")
# find the end of this elif block
end = src.find("\n        elif", idx)
print(src[idx:end])
