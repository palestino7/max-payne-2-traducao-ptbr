# -*- coding: utf-8 -*-
import os, re, sys, glob

def apply_translation_to_file(src_path, dst_path, trans_dict):
    with open(src_path, 'r', encoding='latin-1') as f:
        content = f.read()

    missing = []
    
    def replacer(match):
        prefix = match.group(1) # e.g. "[First_Hospital_1000_01]\t\tString = "
        key = match.group(2)    # e.g. "First_Hospital_1000_01"
        orig_val = match.group(3)
        suffix = match.group(4) # e.g. ";"
        
        if not orig_val.strip():
            return match.group(0)
            
        if key in trans_dict:
            new_val = trans_dict[key]
            # escape double quotes if needed
            new_val = new_val.replace('"', '\\"')
            return f'{prefix}"{new_val}"{suffix}'
        else:
            missing.append((key, orig_val))
            return match.group(0)

    pattern = r'(\[([^\]]+)\]\s*String\s*=\s*)"([^"]*)"(;)'
    new_content = re.sub(pattern, replacer, content)

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, 'w', encoding='cp1252', errors='replace') as out_f:
        out_f.write(new_content)

    return missing

if __name__ == '__main__':
    # Test on 03_First_Hospital
    from translations.trans_03_hospital import TRANSLATIONS as t03
    m = apply_translation_to_file(
        'extracted_english/data/database/subtitles/03_First_Hospital.h',
        'translation_ptbr/data/database/subtitles/03_First_Hospital.h',
        t03
    )
    print("03_First_Hospital missing:", len(m))

    # Test on 04_Warehouse
    from translations.trans_04_warehouse import TRANSLATIONS as t04
    m = apply_translation_to_file(
        'extracted_english/data/database/subtitles/04_Warehouse.h',
        'translation_ptbr/data/database/subtitles/04_Warehouse.h',
        t04
    )
    print("04_Warehouse missing:", len(m))

    # Test on 05_First_Vodka
    from translations.trans_05_vodka import TRANSLATIONS as t05
    m = apply_translation_to_file(
        'extracted_english/data/database/subtitles/05_First_Vodka.h',
        'translation_ptbr/data/database/subtitles/05_First_Vodka.h',
        t05
    )
    print("05_First_Vodka missing:", len(m))

    # Test on 06_First_Dream
    from translations.trans_06_dream import TRANSLATIONS as t06
    m = apply_translation_to_file(
        'extracted_english/data/database/subtitles/06_First_Dream.h',
        'translation_ptbr/data/database/subtitles/06_First_Dream.h',
        t06
    )
    print("06_First_Dream missing:", len(m))
