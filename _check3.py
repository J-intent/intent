import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open("src/mini_intent.py", encoding="utf-8").read()
# Find execute_function body execution section  
idx = src.index("result = IntValue(0)")
end = src.index("\n        # 验证后置条件", idx + 100)
ctx = src[idx-50:end+50]
print(ctx)
