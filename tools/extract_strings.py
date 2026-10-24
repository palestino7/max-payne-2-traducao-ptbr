# -*- coding: utf-8 -*-
import sys, re, json, glob, os

def get_file_strings(path):
    with open(path, 'r', encoding='latin-1') as f:
        content = f.read()
    # Match [KEY] \t String = "VAL";
    pattern = r'(\[([^\]]+)\]\s*String\s*=\s*"([^"]*)";)'
    matches = re.findall(pattern, content)
    result = {}
    for full, key, val in matches:
        if val.strip():
            result[key] = val
    return result

if __name__ == '__main__':
    for path in sorted(glob.glob('extracted_english/data/database/subtitles/*.h')):
        data = get_file_strings(path)
        base = os.path.basename(path)
        print(f'{base:35}: {len(data)} non-empty strings')
