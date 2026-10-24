import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import median_filter, uniform_filter

ORIG_P = os.path.abspath(".")
OUT_STEAM = r"C:\Program Files (x86)\Steam\steamapps\common\MaxPayne2\scripts\ControlScheme.png"
OUT_PREVIEW = os.path.abspath(".")

im = Image.open(ORIG_P).convert("RGB")
arr = np.array(im)

def erase_box(arr, x0, y0, x1, y1, donor_dx=0, donor_dy=-45):
    h, w = y1 - y0, x1 - x0
    top_strip = arr[max(0, y0-6):y0, x0:x1].astype(np.float32)
    bot_strip = arr[y1:min(512, y1+6), x0:x1].astype(np.float32)
    top_med = uniform_filter(median_filter(np.median(top_strip, axis=0), size=(15, 1)), size=(9, 1))
    bot_med = uniform_filter(median_filter(np.median(bot_strip, axis=0), size=(15, 1)), size=(9, 1))
    t = np.linspace(0, 1, h)[:, None, None]
    bg = (1.0 - t) * top_med[None, :, :] + t * bot_med[None, :, :]
    
    dy0 = max(10, min(512 - h - 10, y0 + donor_dy))
    dx0 = max(5, min(1024 - w - 5, x0 + donor_dx))
    donor = arr[dy0:dy0+h, dx0:dx0+w].astype(np.float32)
    donor_low = uniform_filter(median_filter(donor, size=(7, 7, 1)), size=(7, 7, 1))
    res = np.clip(donor - donor_low, -14.0, 14.0)
    synth = np.clip(bg + res * 0.9, 0, 255)
    
    wy = np.ones(h, dtype=np.float32)
    wy[:2] = [0.4, 0.8]
    wy[-2:] = [0.8, 0.4]
    wx = np.ones(w, dtype=np.float32)
    wx[:2] = [0.4, 0.8]
    wx[-2:] = [0.8, 0.4]
    alpha = (wy[:, None] * wx[None, :])[:, :, None]
    orig_sub = arr[y0:y1, x0:x1].astype(np.float32)
    arr[y0:y1, x0:x1] = np.clip(np.round(alpha * synth + (1.0 - alpha) * orig_sub), 0, 255).astype(np.uint8)

left_boxes = [
    (90, 114), (127, 151), (198, 222), (231, 257), (268, 292),
    (305, 329), (340, 364), (375, 399), (411, 435), (447, 473)
]
for y0, y1 in left_boxes:
    erase_box(arr, 3, y0, 165, y1, donor_dx=0, donor_dy=-55 if y0 > 80 else 50)

right_boxes = [
    (89, 113), (128, 194), (198, 224), (232, 256), (271, 295),
    (305, 329), (340, 364), (376, 400), (411, 435)
]
for y0, y1 in right_boxes:
    erase_box(arr, 853, y0, 1005, y1, donor_dx=0, donor_dy=-65 if y0 > 100 else -50)

im_out = Image.fromarray(arr)
draw = ImageDraw.Draw(im_out)

font_main = ImageFont.truetype(r"C:\Windows\Fonts\calibrib.ttf", 19)
font_sub = ImageFont.truetype(r"C:\Windows\Fonts\calibrib.ttf", 12)

def draw_label(x, y, text, font, right_align=False):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = (x - tw) if right_align else x
    # Subtle dark drop shadow matching original ControlScheme.png
    draw.text((tx+1, y+1), text, font=font, fill=(20, 20, 20))
    draw.text((tx, y), text, font=font, fill=(232, 232, 232))

left_labels = [
    (91, "SALTO COM TIRO"),
    (128, "BULLET TIME"),
    (199, "MENU DE PAUSA"),
    (234, "MOVER / ESQUIVAR"),
    (269, "CLIQUE: AGACHAR"),
    (306, "MELHOR ARMA"),
    (341, "ARMA ANTERIOR"),
    (376, "LER HISTÓRIA"),
    (412, "PRÓXIMA ARMA"),
    (449, "N/D"),
]
for y, txt in left_labels:
    draw_label(160, y, txt, font_main, right_align=True)

right_labels = [
    (90, "ATIRAR"),
    (129, "SALVAR RÁPIDO"),
    (158, "CARREGAR RÁPIDO"),
    (200, "USAR / ZOOM"),
    (233, "ANALGÉSICOS"),
    (272, "PULAR"),
    (306, "RECARREGAR"),
    (341, "MIRAR"),
    (377, "CLIQUE: GOLPEAR"),
    (412, "MENU PRINCIPAL"),
]
for y, txt in right_labels:
    draw_label(857, y, txt, font_main, right_align=False)

draw_label(875, 178, "(QUANDO PAUSADO)", font_sub, right_align=False)

im_out.save(OUT_PREVIEW)
im_out.save(OUT_STEAM)
print("Saved translated ControlScheme.png!")
