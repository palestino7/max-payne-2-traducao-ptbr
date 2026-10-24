import glob, re, os

total_strings = 0
for f in sorted(glob.glob('extracted_english/data/database/subtitles/*.h')):
    with open(f, 'r', encoding='latin-1') as fp:
        content = fp.read()
        strings = re.findall(r'(\[[^\]]+\]\s*String\s*=\s*"([^"]*)";)', content)
        non_empty = [s for s in strings if s[1].strip() != '']
        print(f'{os.path.basename(f):35} total: {len(strings):4} non-empty: {len(non_empty):4}')
        total_strings += len(non_empty)

print(f'\nTOTAL NON-EMPTY SUBTITLE STRINGS: {total_strings}')
