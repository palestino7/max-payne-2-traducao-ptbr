# -*- coding: utf-8 -*-
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('extracted_strings/10_Police_Station.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print(f'Total strings: {len(d)}')
for k, v in list(d.items())[:40]:
    v_clean = v.replace('\x92', "'").replace('\x91', "'").replace('\x93', '"').replace('\x94', '"')
    print(f'"{k}": "{v_clean}",')
