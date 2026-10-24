# -*- coding: utf-8 -*-
import json

with open('extracted_strings/10_Police_Station.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print(f"Total keys in 10: {len(d)}")
