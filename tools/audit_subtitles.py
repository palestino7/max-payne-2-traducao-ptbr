# -*- coding: utf-8 -*-
import os, re

eng_dir = 'extracted_english/data/database/subtitles'
pt_dir = 'translation_ptbr/data/database/subtitles'

all_eng_files = sorted(os.listdir(eng_dir))
all_pt_files = sorted(os.listdir(pt_dir))

print(f'English files count: {len(all_eng_files)}')
print(f'PT-BR files count: {len(all_pt_files)}')

pattern = r'\[([^\]]+)\]\s*String\s*=\s*"([^"]*)";'

total_strings = 0
total_untranslated = 0

for fname in all_eng_files:
    if not fname.endswith('.h'):
        continue
    eng_path = os.path.join(eng_dir, fname)
    pt_path = os.path.join(pt_dir, fname)
    
    if not os.path.exists(pt_path):
        print(f'ERROR: {fname} MISSING in PT-BR directory!')
        continue
        
    with open(eng_path, 'r', encoding='latin-1') as f:
        eng_content = f.read()
    with open(pt_path, 'r', encoding='cp1252', errors='replace') as f:
        pt_content = f.read()
        
    eng_matches = dict(re.findall(pattern, eng_content))
    pt_matches = dict(re.findall(pattern, pt_content))
    
    file_strings = len(eng_matches)
    total_strings += file_strings
    
    file_untranslated = 0
    identical_keys = []
    for k, v in eng_matches.items():
        if not v.strip():
            continue
        pt_v = pt_matches.get(k, '')
        if pt_v == v:
            file_untranslated += 1
            identical_keys.append((k, v))
            
    total_untranslated += file_untranslated
    print(f'{fname}: {file_strings} strings (identical to ENG: {file_untranslated})')
    if identical_keys:
        # Show which ones are identical (e.g. "Max", "Jesus!", names)
        sample = ', '.join([f'{k}: {repr(v)}' for k, v in identical_keys[:3]])
        print(f'   Sample identical: {sample}')

print('--- SUMMARY ---')
print(f'Total subtitles strings: {total_strings}')
print(f'Total identical to ENG: {total_untranslated} (mostly proper names, exclamations like Max, Vlad, etc.)')
