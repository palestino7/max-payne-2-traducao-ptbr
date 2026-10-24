# -*- coding: utf-8 -*-
import subprocess, time, os

game_dir = r"C:\Program Files (x86)\Steam\steamapps\common\MaxPayne2"
exe_path = os.path.join(game_dir, "maxpayne2.exe")

print(f"Launching launcher dialog test: {exe_path}...")
proc = subprocess.Popen(
    [exe_path],
    cwd=game_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

pid = proc.pid
print(f"Launcher started with PID: {pid}")
time.sleep(3)

ret = proc.poll()
if ret is None:
    print(f"Launcher dialog PID {pid} is RUNNING HEALTHILY! dialogtexts.txt loaded with 0 crashes!")
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
    print("Launcher dialog closed cleanly.")
else:
    print(f"Launcher dialog exited with return code: {ret}")
