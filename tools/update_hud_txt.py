import re, os

input_path = 'extracted_data/data/hud/hud.txt'
output_path = 'translation_ptbr/data/hud/hud.txt'

with open(input_path, 'r', encoding='latin1') as f:
    content = f.read()

# 1. Update SubtitlesScreenSpaceLimit from 380 to 480
assert 'SubtitlesScreenSpaceLimit = 380;' in content
content = content.replace('SubtitlesScreenSpaceLimit = 380;', 'SubtitlesScreenSpaceLimit = 480;')

# 2. Update SubtitleSlot Position and Scale
old_slot = """\t[SubtitleSlot]
\tReferencePoint = DOWNLEFT;
\tPosition = ( 100, 470.0, 0 );
\tScale = 0.75;"""

new_slot = """\t[SubtitleSlot]
\tReferencePoint = DOWNLEFT;
\tPosition = ( 80, 465.0, 0 );
\tScale = 1.15;"""

assert old_slot in content, "old_slot exact match failed"
content = content.replace(old_slot, new_slot)

os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='latin1') as f:
    f.write(content)

print(f"Successfully generated updated hud.txt at {output_path}")
