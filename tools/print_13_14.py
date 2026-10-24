# -*- coding: utf-8 -*-
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('extracted_strings/13_Construction_Site.json', 'r', encoding='utf-8') as f:
    d13 = json.load(f)

with open('extracted_strings/14_Second_Dream.json', 'r', encoding='utf-8') as f:
    d14 = json.load(f)

print(f"13_Construction_Site: {len(d13)} strings")
for k, v in list(d13.items())[:25]:
    print(f'"{k}": "{v}",')

print(f"\n14_Second_Dream: {len(d14)} strings")
for k, v in list(d14.items())[:25]:
    print(f'"{k}": "{v}",')
