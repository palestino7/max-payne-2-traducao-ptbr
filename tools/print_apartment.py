# -*- coding: utf-8 -*-
import json, sys

with open('extracted_strings/07_Maxs_Apartment.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for k, v in d.items():
    # clean smart quotes for display
    v_clean = v.replace('\x92', "'").replace('\x91', "'").replace('\x93', '"').replace('\x94', '"')
    print(f'"{k}": "{v_clean}",')
