import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open("src/mini_intent.py", encoding="utf-8").read()

# 1. ReturnStmt 相关
idx = src.find("class ReturnStmt")
end = src.find("\n\n", idx)
print("=== ReturnStmt ===")
print(src[idx:end])

# 2. execute_return
idx = src.find("def execute_return")
end = src.find("\n    def ", idx+5)
print("\n=== execute_return ===")
print(src[idx:end])

# 3. execute_function 中 return_flag 处理
idx = src.find("self.return_flag = False")
ctx = src[idx-100:idx+100]
print("\n=== return_flag usage ===")
print(ctx)

# 4. ForStmt AST
idx = src.find("class ForStmt")
end = src.find("\n\n", idx)
print("\n=== ForStmt ===")
print(src[idx:end])
