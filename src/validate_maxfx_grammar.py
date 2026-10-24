# -*- coding: utf-8 -*-
import os, re

def validate_maxfx_file(filepath):
    errors = []
    with open(filepath, 'r', encoding='cp1252') as f:
        content = f.read()

    lines = content.splitlines()
    brace_depth = 0
    in_block_comment = False

    for line_idx, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            continue

        # Handle block comment
        if in_block_comment:
            if '*/' in s:
                s = s[s.find('*/') + 2:].strip()
                in_block_comment = False
            else:
                continue

        if '/*' in s:
            if '*/' in s:
                # inline block comment
                s = re.sub(r'/\*.*?\*/', '', s).strip()
            else:
                s = s[:s.find('/*')].strip()
                in_block_comment = True

        # Strip line comment //
        if '//' in s:
            # Check if // is inside quotes
            # Find all quotes
            quote_ranges = [m.span() for m in re.finditer(r'"(?:\\.|[^"\\])*"', s)]
            comment_idx = s.find('//')
            inside_quote = any(start <= comment_idx <= end for start, end in quote_ranges)
            if not inside_quote:
                s = s[:comment_idx].strip()

        if not s:
            continue

        # Check brace balance
        for char in s:
            if char == '{':
                brace_depth += 1
            elif char == '}':
                brace_depth -= 1
                if brace_depth < 0:
                    errors.append((line_idx, "Unmatched closing brace '}'"))

        # If it's a preprocessor define
        if s.startswith('#define'):
            parts = s.split(None, 2)
            if len(parts) < 2:
                errors.append((line_idx, f"Invalid #define: {s}"))
            continue

        # If line contains an assignment '=', verify it ends with a semicolon or is followed by opening brace
        if '=' in s and not s.endswith('{') and not s.endswith('}'):
            # Must end with a semicolon
            if not s.endswith(';'):
                errors.append((line_idx, f"Missing semicolon at end of assignment: {s}"))
            # Check quotes balance
            # Count quotes that are not escaped
            unescaped_quotes = len(re.findall(r'(?<!\\)"', s))
            if unescaped_quotes % 2 != 0:
                errors.append((line_idx, f"Unbalanced quotes: {s}"))

    if brace_depth != 0:
        errors.append((len(lines), f"Unbalanced braces in file! Final brace depth: {brace_depth}"))

    return errors

print("=== DEEP MAX-FX ENGINE GRAMMAR AUDIT ===")
total_files = 0
total_errors = 0

for root, dirs, files in os.walk('translation_ptbr/data'):
    for f in files:
        if f.endswith('.h') or f.endswith('.txt'):
            total_files += 1
            fpath = os.path.join(root, f)
            errs = validate_maxfx_file(fpath)
            if errs:
                total_errors += len(errs)
                print(f"[FAIL] {fpath}:")
                for lno, msg in errs:
                    print(f"   Line {lno}: {msg}")

if total_errors == 0:
    print(f"SUCCESS: All {total_files} files passed strict MAX-FX engine grammar validation!")
else:
    print(f"FAILED: {total_errors} grammar errors found.")
