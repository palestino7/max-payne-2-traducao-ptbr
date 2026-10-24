# -*- coding: utf-8 -*-
import subprocess, time, os

game_dir = r"C:\Program Files (x86)\Steam\steamapps\common\MaxPayne2"
exe_path = os.path.join(game_dir, "maxpayne2.exe")

print(f"Launching {exe_path} with test parameters...")
# Launch process
proc = subprocess.Popen(
    [exe_path, "-developer", "-nodialog"],
    cwd=game_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

pid = proc.pid
print(f"Process started successfully with PID: {pid}")

# Wait 3 seconds while monitoring process state
time.sleep(3)

ret = proc.poll()
if ret is None:
    print(f"Process PID {pid} is RUNNING HEALTHILY! It did NOT crash on boot!")
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
    print("Process closed cleanly after verification.")
else:
    print(f"Process exited early with return code: {ret}")
    out, err = proc.communicate()
    print("STDOUT:", out.decode('latin-1', errors='replace'))
    print("STDERR:", err.decode('latin-1', errors='replace'))
