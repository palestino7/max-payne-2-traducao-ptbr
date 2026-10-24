# -*- coding: utf-8 -*-
import re

def get_defines(path, enc):
    defines = {}
    with open(path, 'r', encoding=enc) as f:
        for i, line in enumerate(f, 1):
            line_str = line.strip()
            if not line_str.startswith('#define'):
                continue
            parts = line_str.split(None, 2)
            if len(parts) >= 3:
                key = parts[1]
                val = parts[2]
                defines[key] = (i, val)
            elif len(parts) == 2:
                defines[parts[1]] = (i, "")
    return defines

eng_def = get_defines('extracted_english/data/database/stringdefines.h', 'latin-1')
pt_def = get_defines('translation_ptbr/data/database/stringdefines.h', 'cp1252')

print('ENG defines count:', len(eng_def))
print('PT defines count:', len(pt_def))
missing = set(eng_def.keys()) - set(pt_def.keys())
extra = set(pt_def.keys()) - set(eng_def.keys())
print('Missing defines in PT:', len(missing))
print('Extra defines in PT:', len(extra))

# Check that every define in PT has properly balanced quotes if string
quote_issues = []
for k, (line_no, val) in pt_def.items():
    if val.startswith('"'):
        if not val.endswith('"') or len(val) < 2:
            quote_issues.append((line_no, k, val))

print('Quote formatting issues in PT stringdefines.h:', len(quote_issues))
for item in quote_issues:
    print(' ', item)
