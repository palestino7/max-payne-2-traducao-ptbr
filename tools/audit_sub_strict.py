import os, re

sub_dir = 'extracted_english/data/database/subtitles'
files = [
    '03_First_Hospital.h', '04_Warehouse.h', '05_First_Vodka.h', '06_First_Dream.h',
    '07_Maxs_Apartment.h', '08_First_Address_Unknown.h', '09_Upper_East_Side.h',
    '10_Police_Station.h', '11_Second_Address_Unknown.h', '12_Condemned_Building.h',
    '13_Construction_Site.h', '14_Second_Dream.h', '15_Second_Hospital.h',
    '16_Second_Vodka.h', '17_Crackhouse.h', '18_Gognittis_Lot.h',
    '19_Third_Address_Unknown.h', '20_Third_Dream.h', '21_Manor.h', '22_End.h',
    'Cinematics.h', 'TV_Series.h'
]

total_subs = 0
errors = []

for fname in files:
    fpath = os.path.join(sub_dir, fname)
    with open(fpath, 'r', encoding='latin1') as f:
        lines = f.readlines()
    for lnum, line in enumerate(lines, 1):
        raw = line.strip()
        # strip comments
        c_idx = raw.find('//')
        if c_idx != -1:
            raw = raw[:c_idx].strip()
        if not raw:
            continue
        # Expected pattern: [Identifier] String = "...";
        m = re.match(r'^\[([a-zA-Z0-9_]+)\]\s+String\s*=\s*"(.*)"\s*;\s*$', raw)
        if not m:
            errors.append(f'{fname}:{lnum}: INVALID SYNTAX -> {raw}')
        else:
            ident, val = m.group(1), m.group(2)
            # check unescaped quotes inside val
            temp = val.replace('\\"', '')
            if '"' in temp:
                errors.append(f'{fname}:{lnum}: UNESCAPED QUOTE -> {raw}')
            total_subs += 1

print(f'Total subtitles parsed: {total_subs}')
print(f'Total syntax errors: {len(errors)}')
for e in errors[:20]:
    print(' ', e)

print('--- Checking stringdefines.h ---')
with open('extracted_english/data/database/stringdefines.h', 'r', encoding='latin1') as f:
    for lnum, l in enumerate(f, 1):
        s = l.strip()
        if not s or s.startswith('//') or s.startswith('/*') or s.startswith('*'): continue
        if not re.match(r'^#define\s+[a-zA-Z0-9_]+\s+"(.*)"$', s):
            print(f'stringdefines.h:{lnum} -> {s}')

print('--- Checking stringtable.txt ---')
with open('extracted_english/data/database/stringtable.txt', 'r', encoding='latin1') as f:
    for lnum, l in enumerate(f, 1):
        s = l.strip()
        if not s or s.startswith('//'): continue
        if not re.match(r'^\[[a-zA-Z0-9_]+\]\s+String\s*=\s*"(.*)"\s*;\s*$', s):
            print(f'stringtable.txt:{lnum} -> {s}')

print('Finished.')

