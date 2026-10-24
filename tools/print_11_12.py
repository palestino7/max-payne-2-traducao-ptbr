# -*- coding: utf-8 -*-
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('extracted_strings/11_Second_Address_Unknown.json', 'r', encoding='utf-8') as f:
    d11 = json.load(f)

with open('extracted_strings/12_Condemned_Building.json', 'r', encoding='utf-8') as f:
    d12 = json.load(f)

print(f"11_Second_Address_Unknown: {len(d11)} strings")
for k, v in list(d11.items())[:20]:
    print(f'"{k}": "{v}",')

print(f"\n12_Condemned_Building: {len(d12)} strings")
for k, v in list(d12.items())[:20]:
    print(f'"{k}": "{v}",')
