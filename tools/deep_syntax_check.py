# -*- coding: utf-8 -*-
import os, re

def check_file(path):
    issues = []
    with open(path, 'rb') as f:
        raw = f.read()

    # Check for BOM
    if raw.startswith(b'\xef\xbb\xbf'):
        issues.append("Has UTF-8 BOM!")
    if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
        issues.append("Has UTF-16 BOM!")

    # Check CP1252 decode
    try:
        text = raw.decode('cp1252')
    except Exception as e:
        issues.append(f"CP1252 decode error: {e}")
        return issues

    # Line endings
    lines = text.split('\n')
    line_num = 0
    
    # Check syntax of subtitle / string lines: [Key] String = "Value";
    for line in lines:
        line_num += 1
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('#'):
            continue
            
        # Strip trailing comments like // ... if they come AFTER a closing semicolon
        clean_line = re.sub(r';\s*//.*$', ';', line)
            
        # Check matching quotes
        # If line has String = "...", verify it ends with ";
        if 'String' in clean_line and '=' in clean_line:
            idx = clean_line.find('String')
            after = clean_line[idx:]
            # Format should be: String = "value";
            if not re.search(r'String\s*=\s*".*";\s*$', after):
                issues.append(f"Line {line_num} malformed: {line.strip()[:80]}")

    return issues

print("--- AUDITING translation_ptbr ---")
total_files = 0
total_issues = 0
for root, dirs, files in os.walk('translation_ptbr'):
    for f in files:
        fpath = os.path.join(root, f)
        total_files += 1
        issues = check_file(fpath)
        if issues:
            total_issues += len(issues)
            print(f"[FAIL] {fpath}:")
            for iss in issues:
                print(f"   - {iss}")

if total_issues == 0:
    print(f"All {total_files} files passed syntax, encoding, and quote integrity checks!")
else:
    print(f"Found {total_issues} issues across {total_files} files.")
