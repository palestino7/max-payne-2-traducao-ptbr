import re

input_path = 'temp_sounds/data/database/sounds/cinematics.txt'
output_path = 'translation_ptbr/data/database/sounds/cinematics.txt'

with open(input_path, 'r', encoding='latin1') as f:
    content = f.read()

# Replace Dialogue = FALSE; with Dialogue = TRUE; for all sound definitions
# But wait, let's verify if any should remain FALSE or if all dialogue sounds should be TRUE
# In cinematics.txt, every sound definition block is for a cinematic cutscene sound.
# By setting Dialogue = TRUE;, any sound with cue regions will trigger subtitles!
new_content, count = re.subn(r'Dialogue\s*=\s*FALSE\s*;', 'Dialogue = TRUE;', content)
print(f'Replaced {count} occurrences of Dialogue = FALSE; with Dialogue = TRUE;')

import os
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='latin1') as f:
    f.write(new_content)

print(f'Successfully wrote updated cinematics.txt to {output_path}')
