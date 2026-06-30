import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open("src/mini_intent.py", encoding="utf-8").read()
# find the exact IDENTIFIER branch in parse_primary
idx = src.find("def parse_primary")
ident_idx = src.find("if self.match(TokenType.IDENTIFIER):", idx)
# get more context
line_start = src.rfind("\n", 0, ident_idx)
next_elif = src.find("\n        elif", ident_idx)
print(repr(src[line_start:next_elif]))
