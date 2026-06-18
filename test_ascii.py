# -*- coding: utf-8 -*-
# 测试最简单的 Intent 程序

# 1. 先测试纯ASCII版本
test_ascii = '''def main() {
 print("Hello");
 return 0;
}'''

with open('C:/Users/阿J/intent/examples/test_ascii.intent', 'w', encoding='utf-8') as f:
    f.write(test_ascii)

print("✅ 已创建纯ASCII测试文件")
print("\n运行测试:")
