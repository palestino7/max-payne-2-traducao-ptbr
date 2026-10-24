import glob, re, os

total_ui = 0
for f in ['extracted_english/data/database/stringdefines.h',
         'extracted_english/data/database/stringtable.txt',
         'extracted_english/data/dialogtexts.txt',
         'extracted_english/data/input.txt']:
    with open(f, 'r', encoding='latin-1') as fp:
        content = fp.read()
        # Find defines
        defines = re.findall(r'#define\s+\w+\s+"([^"]*)"', content)
        # Find string table entries
        entries = re.findall(r'\[[^\]]+\]\s*String\s*=\s*"([^"]*)";', content)
        # Find dialog entries
        dialog = re.findall(r'\[\w+\]\s*String\s*=\s*"([^"]*)";', content)
        # Combine
        matches = defines + entries + dialog
        non_empty = [m for m in matches if m.strip()]
        print(f'{f:50} strings: {len(non_empty)}')
        total_ui += len(non_empty)

print(f'\nTOTAL UI STRINGS: {total_ui}')
