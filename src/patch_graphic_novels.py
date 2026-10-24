import os, sys, glob, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label, binary_fill_holes, binary_dilation

sys.path.insert(0, os.path.abspath("."))
from dxt_codec import patch_dds_dxt1
from gn_translations_ptbr import TITLE_CARDS_PTBR, BUBBLES_PTBR

BACKUP_DIR = os.path.abspath(".")
EXTRACTED_DIR = os.path.abspath(".")
PTBR_DIR = os.path.abspath(".")
PREVIEW_DIR = os.path.abspath(".")
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(PTBR_DIR, exist_ok=True)

COMIC_FONT_PATH = r"C:\Windows\Fonts\comicz.ttf"
BAHN_FONT_PATH = r"C:\Windows\Fonts\bahnschrift.ttf"

def get_bahn(size, var="SemiBold Condensed"):
    f = ImageFont.truetype(BAHN_FONT_PATH, size)
    f.set_variation_by_name(var)
    return f

COMIC_FONTS = {sz: ImageFont.truetype(COMIC_FONT_PATH, sz) for sz in range(7, 15)}

def detect_speech_bubbles_with_masks(arr):
    r = arr[:,:,0].astype(np.int16)
    g = arr[:,:,1].astype(np.int16)
    b = arr[:,:,2].astype(np.int16)
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    is_bg_color = (
        (r >= 115) & (r <= 198) &
        (g >= 130) & (g <= 208) &
        (b >= 130) & (b <= 212) &
        (g >= r - 2) & (b >= r - 2) &
        ((cmax - cmin) <= 50)
    )
    labeled, num = label(is_bg_color)
    bubbles = []
    for i in range(1, num + 1):
        comp = (labeled == i)
        area = int(np.sum(comp))
        if area < 200:
            continue
        ys, xs = np.where(comp)
        y0, y1 = int(ys.min()), int(ys.max()) + 1
        x0, x1 = int(xs.min()), int(xs.max()) + 1
        w, h = x1 - x0, y1 - y0
        if w < 20 or h < 13:
            continue
            
        sub_comp = comp[y0:y1, x0:x1]
        filled = binary_fill_holes(sub_comp)
        holes = filled & (~sub_comp)
        
        sub_rgb = arr[y0:y1, x0:x1]
        sub_lum = sub_rgb[:,:,0]*0.299 + sub_rgb[:,:,1]*0.587 + sub_rgb[:,:,2]*0.114
        dark_in_holes = int(np.sum(holes & (sub_lum < 110)))
        if dark_in_holes < 10:
            continue
            
        pad_comp = np.pad(filled, 2, mode='constant', constant_values=False)
        outer_ring = binary_dilation(pad_comp, iterations=2) & (~pad_comp)
        ry0, ry1 = max(0, y0-2), min(arr.shape[0], y1+2)
        rx0, rx1 = max(0, x0-2), min(arr.shape[1], x1+2)
        ring_crop = outer_ring[2-(y0-ry0):2+(ry1-y0), 2-(x0-rx0):2+(rx1-x0)]
        ring_lum = (arr[ry0:ry1, rx0:rx1, 0]*0.299 + arr[ry0:ry1, rx0:rx1, 1]*0.587 + arr[ry0:ry1, rx0:rx1, 2]*0.114)[ring_crop]
        dark_border_frac = float(np.mean(ring_lum < 95)) if len(ring_lum) > 0 else 0.0
        if dark_border_frac < 0.42:
            continue
            
        row_widths = filled.sum(axis=1)
        body_rows = np.where(row_widths >= 0.55 * row_widths.max())[0]
        by0 = y0 + int(body_rows.min())
        by1 = y0 + int(body_rows.max()) + 1
        col_heights = filled[body_rows, :].sum(axis=0)
        body_cols = np.where(col_heights >= 0.55 * col_heights.max())[0]
        bx0 = x0 + int(body_cols.min())
        bx1 = x0 + int(body_cols.max()) + 1
        
        bg_med = np.median(sub_rgb[sub_comp], axis=0).astype(np.uint8)
        bubbles.append({
            "x0": x0, "y0": y0, "x1": x1, "y1": y1,
            "bx0": bx0, "by0": by0, "bx1": bx1, "by1": by1,
            "filled": filled,
            "holes": holes,
            "bg_med": bg_med
        })
    bubbles.sort(key=lambda b: (b["by0"] // 40, b["bx0"]))
    return bubbles

def typeset_in_box(draw, bx0, by0, bx1, by1, text):
    avail_w = max(16, (bx1 - bx0) - 6)
    avail_h = max(12, (by1 - by0) - 3)
    best = None
    for sz in (12, 11, 10, 9, 8, 7):
        f = COMIC_FONTS[sz]
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            bbox = draw.textbbox((0, 0), test, font=f)
            if (bbox[2] - bbox[0]) <= avail_w or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        max_lw = max((draw.textbbox((0, 0), l, font=f)[2] - draw.textbbox((0, 0), l, font=f)[0]) for l in lines)
        line_h = max(sz, int(round(sz * 1.15)))
        tot_h = len(lines) * line_h
        if max_lw <= avail_w + 3 and tot_h <= avail_h + 3:
            best = (f, lines, line_h, tot_h)
            break
    if not best:
        f = COMIC_FONTS[7]
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            bbox = draw.textbbox((0, 0), test, font=f)
            if (bbox[2] - bbox[0]) <= avail_w + 4 or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        line_h = 8
        tot_h = len(lines) * line_h
        best = (f, lines, line_h, tot_h)
        
    f, lines, line_h, tot_h = best
    start_y = by0 + (by1 - by0 - tot_h) // 2 - 1
    for li, l in enumerate(lines):
        bbox = draw.textbbox((0, 0), l, font=f)
        lw = bbox[2] - bbox[0]
        lx = bx0 + (bx1 - bx0 - lw) // 2
        ly = start_y + li * line_h
        draw.text((lx, ly), l, font=f, fill=(10, 12, 12))

dds_files = sorted(glob.glob(os.path.join(BACKUP_DIR, "*.dds")))
patched_pages = 0
copied_pages = 0
total_bubbles_rendered = 0

f_title_big = get_bahn(38, "SemiBold Condensed")
f_title_sub = get_bahn(23, "Condensed")

preview_samples = {
    "02_Intro_End_01", "02_Intro_End_02_Text", "03_First_Hospital_Begin_02",
    "04_Warehouse_End_02", "10_Police_Station_Begin_02", "13_Construction_Site_C_End_15",
    "15_Second_Hospital_End_03", "20_Third_Dream_Begin_04", "21_Manor_B_End_03", "22_Game_End_01"
}

for orig_p in dds_files:
    name = os.path.splitext(os.path.basename(orig_p))[0]
    out_paths = [
        os.path.join(EXTRACTED_DIR, name + ".dds"),
        os.path.join(PTBR_DIR, name + ".dds")
    ]
    
    if name in TITLE_CARDS_PTBR:
        t_lines = TITLE_CARDS_PTBR[name]
        if t_lines is None:
            for op in out_paths:
                shutil.copy2(orig_p, op)
            copied_pages += 1
            continue
        arr = np.array(Image.open(orig_p).convert("RGB"))
        arr[140:370, 140:884] = 0
        im = Image.fromarray(arr)
        draw = ImageDraw.Draw(im)
        if name == "22_Game_End_01":
            b1 = draw.textbbox((0, 0), t_lines[0], font=f_title_big)
            draw.text((512 - (b1[2]-b1[0])//2, 205), t_lines[0], font=f_title_big, fill=(230, 230, 230))
            b2 = draw.textbbox((0, 0), t_lines[1], font=f_title_sub)
            draw.text((512 - (b2[2]-b2[0])//2, 260), t_lines[1], font=f_title_sub, fill=(215, 215, 215))
        elif len(t_lines) == 1:
            b1 = draw.textbbox((0, 0), t_lines[0], font=f_title_big)
            draw.text((512 - (b1[2]-b1[0])//2, 236), t_lines[0], font=f_title_big, fill=(230, 230, 230))
        else:
            b1 = draw.textbbox((0, 0), t_lines[0], font=f_title_big)
            draw.text((512 - (b1[2]-b1[0])//2, 216), t_lines[0], font=f_title_big, fill=(230, 230, 230))
            b2 = draw.textbbox((0, 0), t_lines[1], font=f_title_big)
            draw.text((512 - (b2[2]-b2[0])//2, 258), t_lines[1], font=f_title_big, fill=(230, 230, 230))
        patch_dds_dxt1(orig_p, np.array(im), out_paths)
        if name in preview_samples:
            im.save(os.path.join(PREVIEW_DIR, name + ".png"))
        patched_pages += 1
        continue
        
    if name.endswith("_BG"):
        for op in out_paths:
            shutil.copy2(orig_p, op)
        copied_pages += 1
        continue
        
    arr = np.array(Image.open(orig_p).convert("RGB"))
    bubbles = detect_speech_bubbles_with_masks(arr)
    
    # Check if any bubble on this page has a translation in BUBBLES_PTBR
    to_render = []
    for idx, b in enumerate(bubbles):
        bid = f"{name}__{idx:02d}"
        if bid in BUBBLES_PTBR and BUBBLES_PTBR[bid] is not None:
            to_render.append((b, BUBBLES_PTBR[bid]))
            
    if not to_render:
        for op in out_paths:
            shutil.copy2(orig_p, op)
        copied_pages += 1
        continue
        
    # Erase English text inside translated bubbles
    for b, pt_text in to_render:
        erase_mask = binary_dilation(b["holes"], iterations=1) & b["filled"]
        arr[b["y0"]:b["y1"], b["x0"]:b["x1"]][erase_mask] = b["bg_med"]
        
    im = Image.fromarray(arr)
    draw = ImageDraw.Draw(im)
    for b, pt_text in to_render:
        typeset_in_box(draw, b["bx0"], b["by0"], b["bx1"], b["by1"], pt_text)
        total_bubbles_rendered += 1
        
    patch_dds_dxt1(orig_p, np.array(im), out_paths)
    if name in preview_samples:
        im.save(os.path.join(PREVIEW_DIR, name + ".png"))
    patched_pages += 1

print(f"Done! Patched {patched_pages} GN pages ({total_bubbles_rendered} bubbles rendered), copied {copied_pages} untouched pages.")
