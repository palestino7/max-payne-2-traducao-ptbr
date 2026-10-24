import os, re

for root, dirs, files in os.walk('extracted_data/data'):
    for f in files:
        if f.endswith('.txt') and f.lower() not in ['stringtable.txt', 'dialogtexts.txt', 'input.txt', 'hud.txt', 'levels.txt']:
            p = os.path.join(root, f)
            with open(p, 'r', encoding='latin1') as file:
                content = file.read()
            matches = re.findall(r'(?:String|ToolTip|Text|Description|Title)\s*=\s*"([^"]+)"', content)
            if matches:
                user_strings = [m for m in matches if not any(ext in m.lower() for ext in ['.kf2', '.dds', '.tga', '.wav', '.pcx', '->', '::', '(', ')'])]
                if user_strings:
                    print(p, '->', user_strings[:5])
