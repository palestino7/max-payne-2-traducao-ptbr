# -*- coding: utf-8 -*-
import os

def write_cp1252(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='cp1252', errors='replace') as f:
        f.write(content)

# 1. input.txt
input_txt = """[key] ScanCode = 69;\tKeyName = "NUM LOCK";\t\t// for some reason win32 GetKeyNameText calls NumLock PAUSE
[key] ScanCode = 156;\tKeyName = "NUM ENTER";
[key] ScanCode = 157;\tKeyName = "CTRL DIR";
[key] ScanCode = 181;\tKeyName = "NUM /";
[key] ScanCode = 183;\tKeyName = "PRINT SCREEN";
[key] ScanCode = 184;\tKeyName = "ALT DIR";
[key] ScanCode = 197;\tKeyName = "PAUSE";
[key] ScanCode = 199;\tKeyName = "HOME";
[key] ScanCode = 200;\tKeyName = "CIMA";
[key] ScanCode = 201;\tKeyName = "PG UP";
[key] ScanCode = 203;\tKeyName = "ESQUERDA";
[key] ScanCode = 205;\tKeyName = "DIREITA";
[key] ScanCode = 207;\tKeyName = "END";
[key] ScanCode = 208;\tKeyName = "BAIXO";
[key] ScanCode = 209;\tKeyName = "PG DOWN";
[key] ScanCode = 210;\tKeyName = "INSERT";
[key] ScanCode = 211;\tKeyName = "DELETE";
[key] ScanCode = 219;\tKeyName = "WIN ESQ";
[key] ScanCode = 220;\tKeyName = "WIN DIR";
[key] ScanCode = 221;\tKeyName = "MENU WIN";

[names]
MouseButtonName\t= "BM ";\t\t// leave space after, NUMBER of the mouse button IS ADDED after this string BY CODE
MouseWheelUp \t= "Roda do Mouse P/ Cima";\t
MouseWheelDown\t= "Roda do Mouse P/ Baixo";\t
MouseLRName\t\t= "Mouse Esq/Dir";\t// mouse left/right axis, not printed anywhere at the moment
MouseUDName \t= "Mouse Cima/Baixo"; \t// mouse up/down axis, not printed anywhere at the moment
DoubleClick \t= " DUPLO CLIQUE";\t// leave space before the word DCLICK, because this may be added for example to string "MB 1" 
                                // and you want it to look like "MB 1 DCLICK" in the menu, 
"""

write_cp1252('translation_ptbr/data/input.txt', input_txt)
print("input.txt written.")
