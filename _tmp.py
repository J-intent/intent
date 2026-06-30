import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open("std/bim/pipe.intent", encoding="utf-8").read()
for pattern in ["add_vec", r"\.sub\(", r"\.sub_vector\(", r"\.add_vector\("]:
    for m in re.finditer(pattern, src):
        line = src[:m.start()].count("\n") + 1
        print(f"  Line {line}: {m.group()}")
