# -*- coding: utf-8 -*-
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('extracted_strings/11_Second_Address_Unknown.json', 'r', encoding='utf-8') as f:
    d11 = json.load(f)

with open('extracted_strings/12_Condemned_Building.json', 'r', encoding='utf-8') as f:
    d12 = json.load(f)

print("=== 11_Second_Address_Unknown ===")
for k, v in d11.items():
    print(f'"{k}": "{v}",')

print("\n=== 12_Condemned_Building ===")
for k, v in d12.items():
    print(f'"{k}": "{v}",')
