# -*- coding: utf-8 -*-
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.dirname(script_dir)
parent_dir = os.path.dirname(repo_dir)

src_dir = os.path.join(parent_dir, 'data', 'database', 'sounds')
dst_dir = os.path.join(repo_dir, 'translation_ptbr', 'data', 'database', 'sounds')
os.makedirs(dst_dir, exist_ok=True)

target_files = [
    'condemned_bldng_b.txt',
    'condemned_building.txt',
    'construction_site.txt',
    'crackhouse.txt',
    'first_au.txt',
    'first_dream.txt',
    'first_hospital.txt',
    'first_vodka.txt',
    'gognittis_lot.txt',
    'manor.txt',
    'maxs_apartment_a.txt',
    'maxs_apartment_b.txt',
    'police_station.txt',
    'second_au.txt',
    'second_dream.txt',
    'second_hospital.txt',
    'second_vodka.txt',
    'third_au.txt',
    'third_dream.txt',
    'upper_east_side.txt',
    'warehouse.txt',
    'TV_Shows.txt'
]

total_converted = 0

for fname in target_files:
    fpath = os.path.join(src_dir, fname)
    with open(fpath, 'r', encoding='cp1252') as f:
        content = f.read()

    # Split into blocks while preserving line structure
    # A block starts with [Identifier] at the start of a line
    # We can split by (?m)(?=^\[[a-zA-Z0-9_-]+\])
    parts = re.split(r'(?m)(?=^\[[a-zA-Z0-9_-]+\])', content)
    
    new_parts = []
    file_converted = 0
    
    for part in parts:
        m = re.match(r'^\[([a-zA-Z0-9_-]+)\]', part)
        if m:
            bname = m.group(1)
            is_dialogue = bname.lower().startswith('dlg_') or fname == 'TV_Shows.txt'
            if is_dialogue and 'Dialogue' in part:
                # Replace Dialogue = FALSE; with Dialogue = TRUE;
                new_part, count = re.subn(r'(\bDialogue\s*=\s*)FALSE;', r'\g<1>TRUE;', part)
                file_converted += count
                new_parts.append(new_part)
            else:
                new_parts.append(part)
        else:
            new_parts.append(part)
            
    out_content = "".join(new_parts)
    out_path = os.path.join(dst_dir, fname)
    with open(out_path, 'w', encoding='cp1252') as out:
        out.write(out_content)
        
    print(f"Patched {fname:22}: {file_converted:3} dialogue blocks updated to Dialogue=TRUE")
    total_converted += file_converted

print(f"\nTOTAL DIALOGUE SOUND BLOCKS ENABLED: {total_converted}")
