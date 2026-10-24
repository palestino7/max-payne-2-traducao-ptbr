# -*- coding: utf-8 -*-
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('extracted_strings/13_Construction_Site.json', 'r', encoding='utf-8') as f:
    d13 = json.load(f)

for k, v in d13.items():
    print(f'"{k}": "{v}",')
