# -*- coding: utf-8 -*-
import os, sys, shutil, subprocess

repo_root = r'c:\Users\omate\OneDrive\Desktop\tradução max payne 2\max-payne-2-traducao-ptbr-main'
rasmaker_exe = os.path.join(repo_root, 'tools', 'rasmaker.exe')
original_ras = r'C:\Program Files (x86)\Steam\steamapps\common\Max Payne 2 The Fall of Max Payne\MP2_English.ras.bak'
target_ras = os.path.join(repo_root, 'MP2_English_PTBR.ras')
trans_data = os.path.join(repo_root, 'translation_ptbr', 'data')
temp_staging = r'c:\Users\omate\AppData\Local\Temp\mp2_staging_build'

print("=== BUILDING MP2_English_PTBR.ras ===")

if os.path.exists(temp_staging):
    shutil.rmtree(temp_staging, ignore_errors=True)
os.makedirs(temp_staging, exist_ok=True)

print(f"1. Extracting original RAS from: {original_ras}")
# Run rasmaker -x in temp_staging
subprocess.run([rasmaker_exe, "-x", original_ras], cwd=temp_staging, check=False)

print(f"2. Overlaying translation from: {trans_data}")
staging_data = os.path.join(temp_staging, 'data')
for root, dirs, files in os.walk(trans_data):
    rel_path = os.path.relpath(root, trans_data)
    dest_dir = os.path.join(staging_data, rel_path)
    os.makedirs(dest_dir, exist_ok=True)
    for f in files:
        src_file = os.path.join(root, f)
        dst_file = os.path.join(dest_dir, f)
        shutil.copy2(src_file, dst_file)

print(f"3. Repacking archive into: {target_ras}")
if os.path.exists(target_ras):
    os.remove(target_ras)

p = subprocess.run([rasmaker_exe, "-a", "data", target_ras], cwd=temp_staging, check=False)

if os.path.exists(target_ras):
    size = os.path.getsize(target_ras)
    print(f"SUCCESS: MP2_English_PTBR.ras built successfully! Size: {size:,} bytes")
else:
    print("ERROR: Target RAS was not created!")
    sys.exit(1)

print("4. Cleaning up temp staging...")
shutil.rmtree(temp_staging, ignore_errors=True)
print("Done.")
