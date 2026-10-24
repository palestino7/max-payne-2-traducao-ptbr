# -*- coding: utf-8 -*-
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('extracted_strings/15_Second_Hospital.json', 'r', encoding='utf-8') as f:
    d15 = json.load(f)

print(f"15_Second_Hospital: {len(d15)} strings")
for k, v in d15.items():
    print(f'"{k}": "{v}",')
