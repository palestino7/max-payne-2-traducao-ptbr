# -*- coding: utf-8 -*-
import os, re

def find_specifiers(s):
    # Match %i, %d, %s, %f, %u, etc. (excluding %% and % alone)
    return re.findall(r'%[0-9]*\.?[0-9]*[a-zA-Z]', s)

def compare_file_specifiers(eng_path, pt_path):
    with open(eng_path, 'r', encoding='latin-1') as f:
        eng_text = f.read()
    with open(pt_path, 'r', encoding='cp1252') as f:
        pt_text = f.read()

    # Match key-value
    eng_matches = re.findall(r'(\[[^\]]+\][^\n\r]*String\s*=\s*"([^"]*)")', eng_text)
    pt_matches = re.findall(r'(\[[^\]]+\][^\n\r]*String\s*=\s*"([^"]*)")', pt_text)
    
    # Or for defines:
    eng_defs = re.findall(r'#define\s+([A-Za-z0-9_]+)\s+"([^"]*)"', eng_text)
    pt_defs = re.findall(r'#define\s+([A-Za-z0-9_]+)\s+"([^"]*)"', pt_text)

    issues = []
    
    # Check String = "..."
    pt_dict = {}
    for full, val in pt_matches:
        k = full.split(']')[0] + ']'
        pt_dict[k] = val
        
    for full, eng_val in eng_matches:
        k = full.split(']')[0] + ']'
        eng_specs = find_specifiers(eng_val)
        if eng_specs:
            pt_val = pt_dict.get(k)
            if pt_val is not None:
                pt_specs = find_specifiers(pt_val)
                if eng_specs != pt_specs:
                    issues.append(f"{k}: specifiers mismatch! ENG: {eng_specs} vs PT: {pt_specs}")
                    
    # Check #defines
    pt_def_dict = dict(pt_defs)
    for k, eng_val in eng_defs:
        eng_specs = find_specifiers(eng_val)
        if eng_specs:
            pt_val = pt_def_dict.get(k)
            if pt_val is not None:
                pt_specs = find_specifiers(pt_val)
                if eng_specs != pt_specs:
                    issues.append(f"Define {k}: specifiers mismatch! ENG: {eng_specs} vs PT: {pt_specs}")

    return issues

print("=== CHECKING FORMAT SPECIFIERS (%s, %i, etc.) ===")
total_issues = 0
for root, dirs, files in os.walk('translation_ptbr'):
    for f in files:
        pt_path = os.path.join(root, f)
        rel = os.path.relpath(pt_path, 'translation_ptbr')
        eng_path = os.path.join('extracted_english', rel)
        if os.path.exists(eng_path):
            issues = compare_file_specifiers(eng_path, pt_path)
            if issues:
                total_issues += len(issues)
                print(f"[FAIL] {rel}:")
                for iss in issues:
                    print(f"   {iss}")

if total_issues == 0:
    print("ALL FORMAT SPECIFIERS MATCH 100% PERFECTLY WITH ORIGINAL ENGLISH!")
else:
    print(f"Total format specifier issues: {total_issues}")
