# -*- coding: utf-8 -*-
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('extracted_strings/08_First_Address_Unknown.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for k, v in d.items():
    print(f'"{k}": "{v}",')
