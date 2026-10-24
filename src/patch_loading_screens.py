import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import median_filter, uniform_filter

sys.path.insert(0, os.path.abspath("."))
from dxt_codec import patch_dds_dxt1

BACKUP_ROOT = os.path.abspath(".")
EXTRACTED_ROOT = os.path.abspath(".")
PTBR_ROOT = os.path.abspath(".")

FONT_PATH = r"C:\Windows\Fonts\bahnschrift.ttf"
def get_font(size, variation="Condensed"):
    f = ImageFont.truetype(FONT_PATH, size)
    f.set_variation_by_name(variation)
    return f

def erase_band_100pct(arr, x0, y0, x1, y1, top_y0, top_y1, bot_y0, bot_y1, donor_y0=265):
    """
    100% replaces all pixels inside [x0:x1, y0:y1] so ZERO ghost letters or shadows
    can ever survive, while preserving seamless background gradients and vertical rain/grain texture!
    """
    h, w = y1 - y0, x1 - x0
    top_strip = arr[top_y0:top_y1, x0:x1].astype(np.float32)
    bot_strip = arr[bot_y0:bot_y1, x0:x1].astype(np.float32)
    
    top_med = np.median(top_strip, axis=0)
    bot_med = np.median(bot_strip, axis=0)
    top_smooth = uniform_filter(median_filter(top_med, size=(25, 1)), size=(13, 1))
    bot_smooth = uniform_filter(median_filter(bot_med, size=(25, 1)), size=(13, 1))
    
    t = np.linspace(0, 1, h)[:, None, None]
    bg_smooth = (1.0 - t) * top_smooth[None, :, :] + t * bot_smooth[None, :, :]
    
    # Extract clean micro-texture from donor region [donor_y0 : donor_y0 + h, x0:x1]
    donor = arr[donor_y0:donor_y0+h, x0:x1].astype(np.float32)
    donor_low = uniform_filter(median_filter(donor, size=(5, 9, 1)), size=(5, 9, 1))
    # Clamp any bright raindrop or dark bar outlier in donor residual to [-12, +12]
    residual = np.clip(donor - donor_low, -12.0, 12.0)
    
    synthesized = np.clip(bg_smooth + residual * 0.85, 0, 255)
    
    # Smooth 3px feather at left/right/top/bottom boundaries so there is zero seam
    wy = np.ones(h, dtype=np.float32)
    wy[:2] = [0.35, 0.75]
    wy[-2:] = [0.75, 0.35]
    wx = np.ones(w, dtype=np.float32)
    wx[:3] = [0.25, 0.55, 0.85]
    wx[-4:] = [0.85, 0.60, 0.35, 0.15]
    alpha = (wy[:, None] * wx[None, :])[:, :, None]
    
    orig_sub = arr[y0:y1, x0:x1].astype(np.float32)
    blended = alpha * synthesized + (1.0 - alpha) * orig_sub
    arr[y0:y1, x0:x1] = np.clip(np.round(blended), 0, 255).astype(np.uint8)

def draw_mp2_text(draw, x, y, text, font, fill=(215, 215, 215)):
    draw.text((x+2, y+2), text, font=font, fill=(10, 10, 10))
    draw.text((x+1, y+1), text, font=font, fill=(5, 5, 5))
    draw.text((x, y), text, font=font, fill=fill)

font_part = get_font(29, "SemiBold Condensed")
font_chap = get_font(27, "Condensed")
font_load = get_font(19, "Condensed")

P1 = "PARTE I: A Escuridão Lá Dentro"
P2 = "PARTE II: Uma Escolha Binária"
P3 = "PARTE III: Acordando do Sonho Americano"
DMW = "Homem Morto Caminhando"

level_specs = {
    "03_First_Hospital": (P1, "PRÓLOGO", 352, 155),
    "04_Warehouse": (P1, "CAPÍTULO UM: Portas do Elevador", 336, 310),
    "05_First_Vodka": (P1, "CAPÍTULO DOIS: Um Gênio do Crime", 336, 380),
    "06_First_Dream": (P1, "CAPÍTULO TRÊS: As Profundezas do Meu Cérebro", 336, 400),
    "07_Maxs_Apartment_A": (P1, "CAPÍTULO QUATRO: Não Há 'Nós' Nisso", 336, 320),
    "07_Maxs_Apartment_B": (P1, "CAPÍTULO CINCO: Um Sinal da Passagem Dela", 336, 370),
    "08_First_Address_Unknown": (P1, "CAPÍTULO SEIS: Uma Sequência Linear de Medos", 336, 420),
    "09_Upper_East_Side": (P1, "CAPÍTULO SETE: A Pergunta de Um Milhão de Dólares", 336, 440),
    "10_Police_Station": (P2, "PRÓLOGO", 302, 155),
    "11_Second_Address_Unknown": (P2, "CAPÍTULO UM: As Coisas que Eu Quero", 302, 370),
    "12_Condemned_Building_A": (P2, "CAPÍTULO DOIS: No Meio de Algo", 302, 410),
    "12_Condemned_Building_B": (P2, "CAPÍTULO TRÊS: Explodindo Tudo", 302, 330),
    "13_Construction_Site_A": (P2, "CAPÍTULO QUATRO: Roteando as Sinapses Dela", 302, 385),
    "13_Construction_Site_B": (P2, "CAPÍTULO CINCO: Pela Janela", 302, 340),
    "13_Construction_Site_C": (P2, "CAPÍTULO SEIS: O Gênio do Buraco", 302, 365),
    "14_Second_Dream": (P3, "PRÓLOGO", 515, 155),
    "15_Second_Hospital": (P3, "CAPÍTULO UM: Teimoso Demais para Morrer", 515, 350),
    "16_Second_Vodka": (P3, "CAPÍTULO DOIS: Em Rota de Colisão", 515, 360),
    "17_Crackhouse": (P3, "CAPÍTULO TRÊS: Uma Guerra da Máfia", 515, 390),
    "18_Gognittis_Lot": (P3, "CAPÍTULO QUATRO: O Mais Querido de Todos os Amigos", 515, 520),
    "19_Third_Address_Unknown": (P3, "CAPÍTULO CINCO: Um Jogo Perdido", 515, 340),
    "20_Third_Dream": (P3, "CAPÍTULO SEIS: Não Há Finais Felizes", 515, 415),
    "21_Manor_A": (P3, "CAPÍTULO SETE: O Amor Machuca", 515, 330),
    "21_Manor_B": (P3, "CAPÍTULO OITO: Aquela Velha Sensação Familiar", 515, 440),
    "DeadManWalking_01_ManorYard": (DMW, "Pátio da Mansão", 240, 165),
    "DeadManWalking_02_ConstSite": (DMW, "Canteiro de Obras", 240, 200),
    "DeadManWalking_03_ManorGarden": (DMW, "Jardim da Mansão", 240, 185),
    "DeadManWalking_04_UsedCarLot": (DMW, "Loja de Carros Usados", 240, 170),
    "DeadManWalking_05_Scaffoldings": (DMW, "Andaimes", 240, 160),
}

for name, (part_txt, chap_txt, l1_x1, l2_x1) in level_specs.items():
    rel_path = rf"data\database\levels\bitmaps\{name}.dds"
    orig_p = os.path.join(BACKUP_ROOT, rel_path)
    arr = np.array(Image.open(orig_p).convert("RGB"))
    erase_band_100pct(arr, 35, 333, l1_x1, 367, 323, 331, 366, 372, donor_y0=265)
    erase_band_100pct(arr, 35, 370, l2_x1, 402, 366, 371, 402, 410, donor_y0=295)
    erase_band_100pct(arr, 35, 419, 108, 444, 410, 418, 444, 452, donor_y0=240)
    
    im = Image.fromarray(arr)
    draw = ImageDraw.Draw(im)
    draw_mp2_text(draw, 41, 336, part_txt, font_part, (220, 220, 220))
    draw_mp2_text(draw, 41, 371, chap_txt, font_chap, (208, 208, 208))
    draw_mp2_text(draw, 41, 421, "Carregando...", font_load, (205, 205, 205))
    
    new_arr = np.array(im)
    out_paths = [os.path.join(EXTRACTED_ROOT, rel_path), os.path.join(PTBR_ROOT, rel_path)]
    patch_dds_dxt1(orig_p, new_arr, out_paths)

print("Done 100pct band replacement on all 29 level loading screens.")
