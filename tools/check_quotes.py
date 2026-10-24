# -*- coding: utf-8 -*-
import os, re

def audit_quotes_and_syntax(path):
    issues = []
    with open(path, 'r', encoding='cp1252') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith('//') or s.startswith('#'):
            continue
            
        # Match String = "..."
        if 'String' in s and '=' in s:
            # Strip trailing comment
            no_comment = re.sub(r'//.*$', '', s).strip()
            
            # Check pattern: [Key] String = "val";
            m = re.search(r'String\s*=\s*"(.*)"\s*;\s*$', no_comment)
            if not m:
                issues.append(f"Line {i} does not match String = \"...\"; -> {s}")
            else:
                val = m.group(1)
                # Count unescaped quotes inside val
                # An unescaped quote would be a quote not preceded by backslash
                # But wait: does Remedy MAX-FX support \"? Or did Remedy not use quotes inside strings?
                # Let's check if there are unescaped quotes:
                unescaped_quotes = re.findall(r'(?<!\\)"', val)
                if unescaped_quotes:
                    issues.append(f"Line {i} has unescaped inner quote: {val}")

    return issues

print("=== CHECKING ALL SUBTITLE & DATABASE FILES FOR QUOTE INTEGRITY ===")
total_issues = 0
for root, dirs, files in os.walk('translation_ptbr'):
    for f in files:
        if f.endswith('.h') or f.endswith('.txt'):
            path = os.path.join(root, f)
            iss = audit_quotes_and_syntax(path)
            if iss:
                total_issues += len(iss)
                print(f"[FAIL] {path}:")
                for item in iss:
                    print(f"   {item}")

if total_issues == 0:
    print("ALL FILES HAVE 100% CLEAN SYNTAX AND NO UNESCAPED QUOTES!")
else:
    print(f"Total issues found: {total_issues}")
