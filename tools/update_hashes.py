# -*- coding: utf-8 -*-
import hashlib, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')

repo_root = r'c:\Users\omate\OneDrive\Desktop\tradução max payne 2\max-payne-2-traducao-ptbr-main'

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().lower()

files = {
    'exe': os.path.join(repo_root, 'dist', 'Instalador_MaxPayne2_PTBR_v3.0.0.exe'),
    'zip': os.path.join(repo_root, 'dist', 'Instalador_MaxPayne2_PTBR_v3.0.0.zip'),
    'mp2m': os.path.join(repo_root, 'MaxPayne2_PTBR.mp2m'),
    'ras': os.path.join(repo_root, 'MP2_English_PTBR.ras')
}

hashes = {k: get_sha256(path) for k, path in files.items()}
sizes = {k: os.path.getsize(path) for k, path in files.items()}

# 1. Update SHA256SUMS.txt
sha_content = f"""{hashes['exe']}  dist/Instalador_MaxPayne2_PTBR_v3.0.0.exe
{hashes['zip']}  dist/Instalador_MaxPayne2_PTBR_v3.0.0.zip
{hashes['mp2m']}  MaxPayne2_PTBR.mp2m
{hashes['ras']}  MP2_English_PTBR.ras
"""

with open(os.path.join(repo_root, 'SHA256SUMS.txt'), 'w', encoding='utf-8') as f:
    f.write(sha_content)
with open(os.path.join(repo_root, 'dist', 'SHA256SUMS.txt'), 'w', encoding='utf-8') as f:
    f.write(sha_content)

# 2. Update README.md
readme_path = os.path.join(repo_root, 'README.md')
with open(readme_path, 'r', encoding='utf-8') as f:
    readme = f.read()

for k, path in files.items():
    fname = os.path.basename(path)
    pattern = rf'[a-f0-9]{{64}}\s+{re.escape(fname)}'
    replacement = f"{hashes[k]}  {fname}"
    readme = re.sub(pattern, replacement, readme)

with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(readme)

# 3. Update RELEASE_NOTES_v3.0.0.md
rel_path = os.path.join(repo_root, 'RELEASE_NOTES_v3.0.0.md')
with open(rel_path, 'r', encoding='utf-8') as f:
    rel_notes = f.read()

for k, path in files.items():
    fname = os.path.basename(path)
    pattern = rf'[a-f0-9]{{64}}\s+{re.escape(fname)}'
    replacement = f"{hashes[k]}  {fname}"
    rel_notes = re.sub(pattern, replacement, rel_notes)

with open(rel_path, 'w', encoding='utf-8') as f:
    f.write(rel_notes)

print("Updated SHA256SUMS.txt, README.md, and RELEASE_NOTES_v3.0.0.md successfully!")
for k, path in files.items():
    print(f"  {os.path.basename(path)} -> {hashes[k]} ({sizes[k]:,} bytes)")
