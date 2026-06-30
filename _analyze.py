src = open("src/mini_intent.py", encoding="utf-8").read()
idx = src.find("def parse_primary")
end = src.find("\n    def ", idx + 10)
# find the IDENTIFIER branch inside parse_primary
ident_idx = src.find("if self.match(TokenType.IDENTIFIER)", idx)
# find the end of that branch
branch_end = src.find("\n            elif", ident_idx)
print(src[ident_idx:branch_end])
