# -*- coding: utf-8 -*-
import sys, re, json, glob, os

os.makedirs('extracted_strings', exist_ok=True)

for path in sorted(glob.glob('extracted_english/data/database/subtitles/*.h')):
    with open(path, 'r', encoding='latin-1') as f:
        content = f.read()
    pattern = r'\[([^\]]+)\]\s*String\s*=\s*"([^"]*)";'
    matches = re.findall(pattern, content)
    data = {}
    for key, val in matches:
        if val.strip():
            data[key] = val
    base = os.path.basename(path).replace('.h', '.json')
    out_path = os.path.join('extracted_strings', base)
    with open(out_path, 'w', encoding='utf-8') as out_f:
        json.dump(data, out_f, indent=2, ensure_ascii=False)
    print(f'Wrote {out_path} ({len(data)} strings)')
