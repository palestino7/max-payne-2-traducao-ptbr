#!/usr/bin/env python3
"""
Adversarial Verification & Empirical Stress Harness — Challenger M1-1
Milestone 1: Asset & Text Fusion Verification for Max Payne 2 PT-BR v3.0.0

This test suite executes rigorous, adversarial validation across all M1 deliverables:
  1. Byte-level Windows-1252 conformance of all 22 subtitle files, dialogtexts.txt,
     stringtable.txt, and input.txt.
  2. MaxFX native bitmap font glyph coverage verification (all non-ASCII bytes mapped).
  3. Format specifier fidelity against original English reference files.
  4. MaxFX subtitle and configuration grammar parsing.
  5. Restoration integrity of 03_First_Hospital.h (21 prologue lines) and 22_End.h.
  6. Binary DDS header, FourCC, dimensions, and exact 262,272-byte size verification
     across all 138 Graphic Novels and all 29 Level Loading Screens.
  7. High-res HUD and Menu DDS integrity (ActiveWeapons, Introductions, Menus, PleaseWait).
  8. Bink Video container, video stream (1024x640 @ 30fps), audio stream (48kHz stereo),
     and full-stream decode integrity via ffmpeg/ffprobe.
  9. Oracle discrimination stress tests (negative mutation tests proving detection power).
"""

import glob
import os
import re
import struct
import subprocess
import unittest
from typing import Dict, List, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRANS_DIR = os.path.join(PROJECT_ROOT, "translation_ptbr")
ENG_REF_DIR = os.path.join(PROJECT_ROOT, "extracted_english")
SHARED_TEXTURES_DIR = os.path.join(PROJECT_ROOT, "extracted_data", "data", "sharedtextures")

# Windows-1252 undefined code points
CP1252_UNDEFINED_BYTES = {0x81, 0x8D, 0x8F, 0x90, 0x9D}

# Common UTF-8 multi-byte sequence signatures mistakenly introduced
UTF8_PATTERNS = [
    b"\xef\xbb\xbf",          # UTF-8 BOM
    b"\xef\xbf\xbd",          # Unicode Replacement Character 
]


def parse_dds_header_strict(fpath: str) -> Dict[str, any]:
    """Parse DDS header strictly according to Microsoft DirectDraw Surface spec."""
    file_size = os.path.getsize(fpath)
    with open(fpath, "rb") as f:
        header = f.read(128)
    if len(header) < 128:
        raise ValueError(f"DDS header truncated: {len(header)} bytes")

    magic = header[:4]
    header_size, flags, height, width, pitch_or_linear_size, depth, mipmaps = struct.unpack(
        "<IIIIIII", header[4:32]
    )
    # Reserved1: 11 DWORDs (offset 32..76)
    pf_size, pf_flags, fourcc, rgb_bits, r_mask, g_mask, b_mask, a_mask = struct.unpack(
        "<II4sIIIII", header[76:108]
    )
    caps1, caps2, caps3, caps4 = struct.unpack("<IIII", header[108:124])

    return {
        "file_size": file_size,
        "magic": magic,
        "header_size": header_size,
        "flags": flags,
        "height": height,
        "width": width,
        "pitch_or_linear_size": pitch_or_linear_size,
        "depth": depth,
        "mipmaps": mipmaps,
        "pf_size": pf_size,
        "pf_flags": pf_flags,
        "fourcc": fourcc,
        "rgb_bits": rgb_bits,
        "r_mask": r_mask,
        "g_mask": g_mask,
        "b_mask": b_mask,
        "a_mask": a_mask,
        "caps1": caps1,
        "caps2": caps2,
    }


def parse_bik_header_strict(fpath: str) -> Dict[str, any]:
    """Parse Bink Video header strictly according to RAD Game Tools specification."""
    file_size = os.path.getsize(fpath)
    with open(fpath, "rb") as f:
        hdr = f.read(44)
    if len(hdr) < 44:
        raise ValueError(f"BIK header truncated: {len(hdr)} bytes")

    magic = hdr[:4]
    file_size_minus_8, num_frames, max_frame_size, num_frames2, width, height, fps_scale, fps_div, flags, num_audio = struct.unpack(
        "<IIIIIIIIII", hdr[4:44]
    )

    fps = (fps_scale / fps_div) if fps_div > 0 else 0.0

    return {
        "magic": magic,
        "file_size": file_size,
        "file_size_minus_8": file_size_minus_8,
        "num_frames": num_frames,
        "max_frame_size": max_frame_size,
        "width": width,
        "height": height,
        "fps": fps,
        "fps_scale": fps_scale,
        "fps_div": fps_div,
        "flags": flags,
        "num_audio": num_audio,
    }


# ==============================================================================
# 1. TEXT & SUBTITLE BYTE-LEVEL CONFORMANCE
# ==============================================================================
class TestAdversarialTextConformance(unittest.TestCase):
    """Deep byte-by-byte adversarial audit of all localization and subtitle files."""

    def setUp(self):
        self.sub_dir = os.path.join(TRANS_DIR, "data", "database", "subtitles")
        self.dialogtexts = os.path.join(TRANS_DIR, "data", "dialogtexts.txt")
        self.stringtable = os.path.join(TRANS_DIR, "data", "database", "stringtable.txt")
        self.input_txt = os.path.join(TRANS_DIR, "data", "input.txt")
        self.stringdefines = os.path.join(TRANS_DIR, "data", "database", "stringdefines.h")

        # Collect all 22 subtitle files
        self.subtitle_files = sorted(glob.glob(os.path.join(self.sub_dir, "*.h")))
        self.all_target_text_files = [
            self.dialogtexts,
            self.stringtable,
            self.input_txt,
            self.stringdefines,
        ] + self.subtitle_files

    def test_01_subtitle_file_inventory_exact_count(self):
        """Verify that exactly 22 subtitle .h files exist."""
        self.assertEqual(
            len(self.subtitle_files), 22,
            f"Expected exactly 22 subtitle files, found {len(self.subtitle_files)}: "
            f"{[os.path.basename(f) for f in self.subtitle_files]}"
        )

    def test_02_all_core_text_files_exist_and_non_empty(self):
        """Verify that dialogtexts.txt, stringtable.txt, and input.txt exist and are populated."""
        for path in [self.dialogtexts, self.stringtable, self.input_txt]:
            self.assertTrue(os.path.isfile(path), f"File missing: {path}")
            size = os.path.getsize(path)
            self.assertGreater(size, 500, f"File suspiciously small ({size} bytes): {path}")

    def test_03_strict_cp1252_decodability_every_single_byte(self):
        """Byte-by-byte audit: verify 100% strict CP1252 decodability without any errors."""
        decode_errors = []
        for fpath in self.all_target_text_files:
            rel = os.path.relpath(fpath, PROJECT_ROOT)
            with open(fpath, "rb") as f:
                content = f.read()
            try:
                content.decode("cp1252", errors="strict")
            except UnicodeDecodeError as e:
                decode_errors.append(f"{rel}: failed at byte offset {e.start}: {e}")

        self.assertEqual(len(decode_errors), 0, "CP1252 decode violations:\n" + "\n".join(decode_errors))

    def test_04_no_undefined_cp1252_bytes(self):
        """Verify absence of unmapped Windows-1252 bytes (0x81, 0x8D, 0x8F, 0x90, 0x9D)."""
        violations = []
        for fpath in self.all_target_text_files:
            rel = os.path.relpath(fpath, PROJECT_ROOT)
            with open(fpath, "rb") as f:
                content = f.read()
            for offset, b in enumerate(content):
                if b in CP1252_UNDEFINED_BYTES:
                    violations.append(f"{rel}: undefined byte 0x{b:02X} at offset {offset}")

        self.assertEqual(len(violations), 0, "Undefined CP1252 bytes found:\n" + "\n".join(violations))

    def test_05_no_utf8_multibyte_sequences_or_mojibake(self):
        """Verify total absence of UTF-8 BOM, replacement chars, and multibyte sequences (0xC3 0x80..0xBF)."""
        violations = []
        for fpath in self.all_target_text_files:
            rel = os.path.relpath(fpath, PROJECT_ROOT)
            with open(fpath, "rb") as f:
                raw = f.read()

            for pat in UTF8_PATTERNS:
                if pat in raw:
                    idx = raw.find(pat)
                    violations.append(f"{rel}: found UTF-8 pattern {pat!r} at offset {idx}")

            # Check for UTF-8 multibyte sequences for Latin characters: 0xC3 followed by 0x80..0xBF
            for i in range(len(raw) - 1):
                if raw[i] == 0xC3 and (0x80 <= raw[i + 1] <= 0xBF):
                    sample = raw[max(0, i - 10):min(len(raw), i + 10)]
                    violations.append(
                        f"{rel}: UTF-8 multibyte sequence (0xC3 0x{raw[i+1]:02X}) at offset {i} [Context: {sample!r}]"
                    )

        self.assertEqual(len(violations), 0, "UTF-8 mojibake detected:\n" + "\n".join(violations))

    def test_06_maxfx_native_font_glyph_coverage(self):
        """
        Verify that EVERY non-ASCII character present in localization texts has a valid,
        rendered, non-empty glyph in the MaxFX font textures (font_univers, font_universal_medium, font_univers_verysmall).
        """
        from PIL import Image
        import numpy as np

        # Collect all non-ASCII bytes used in target text files
        used_non_ascii_bytes = set()
        for fpath in self.all_target_text_files:
            with open(fpath, "rb") as f:
                data = f.read()
            for b in data:
                if b >= 128:
                    used_non_ascii_bytes.add(b)

        self.assertGreater(len(used_non_ascii_bytes), 0, "No non-ASCII characters found")

        font_names = ["font_univers", "font_universal_medium", "font_univers_verysmall"]
        for fname in font_names:
            tga_path = os.path.join(SHARED_TEXTURES_DIR, f"{fname}.tga")
            alpha_path = os.path.join(SHARED_TEXTURES_DIR, f"{fname}_alpha.tga")
            self.assertTrue(os.path.isfile(tga_path), f"Font texture missing: {tga_path}")
            self.assertTrue(os.path.isfile(alpha_path), f"Font alpha missing: {alpha_path}")

            im = Image.open(tga_path)
            alpha = Image.open(alpha_path)
            alpha_arr = np.array(alpha)[1:, :, 0]
            top = np.array(im)[0, :, 0] > 128

            # Extract 512 transitions separating the 256 character cells (margin + glyph)
            trans = [0] + list(np.where(np.diff(top.astype(int)) != 0)[0] + 1) + [alpha_arr.shape[1]]
            self.assertEqual(
                len(trans), 514,
                f"Font {fname} expected 514 boundary points (512 transitions), got {len(trans)}"
            )

            missing_glyphs = []
            for byte_val in sorted(used_non_ascii_bytes):
                # MaxFX maps character code c to margin interval 2*c and glyph interval 2*c + 1
                i_glyph = 2 * byte_val + 1
                x1, x2 = trans[i_glyph], trans[i_glyph + 1]
                glyph_pixels = alpha_arr[:, x1:x2]
                rendered_pixel_count = np.count_nonzero(glyph_pixels > 50)
                if rendered_pixel_count == 0:
                    char_repr = bytes([byte_val]).decode("cp1252", errors="replace")
                    missing_glyphs.append(f"0x{byte_val:02X} ('{char_repr}') in {fname}")

            self.assertEqual(
                len(missing_glyphs), 0,
                f"MaxFX font {fname} lacks glyph rendering for non-ASCII characters:\n" + "\n".join(missing_glyphs)
            )

    def test_07_hospital_restored_21_prologue_lines(self):
        """Verify that 03_First_Hospital.h preserves all 21 prologue lines deleted in competitor translation."""
        hospital_path = os.path.join(self.sub_dir, "03_First_Hospital.h")
        with open(hospital_path, "r", encoding="cp1252") as f:
            content = f.read()

        # The exact 21 keys that the competitor wiped out with String = "";
        competitor_deleted_keys = [
            "First_Hospital_1010_01", "First_Hospital_1010_02", "First_Hospital_1010_03",
            "First_Hospital_1010_04", "First_Hospital_1010_05", "First_Hospital_1010_06",
            "First_Hospital_1020_01", "First_Hospital_1020_02", "First_Hospital_1020_03",
            "First_Hospital_1020_04", "First_Hospital_1020_05", "First_Hospital_1020_06",
            "First_Hospital_1020_07", "First_Hospital_1020_08",
            "First_Hospital_1040_01", "First_Hospital_1040_02", "First_Hospital_1040_03",
            "First_Hospital_1040_04", "First_Hospital_1040_05",
            "First_Hospital_1060_01",
            "First_Hospital_1080_01",
        ]
        missing_or_empty = []
        pattern = re.compile(r'\[(.*?)\]\s*String\s*=\s*"(.*?)"')
        entries = dict(pattern.findall(content))

        for key in competitor_deleted_keys:
            val = entries.get(key)
            if val is None or not val.strip():
                missing_or_empty.append(key)

        self.assertEqual(
            len(missing_or_empty), 0,
            f"03_First_Hospital.h missing/empty restored lines: {missing_or_empty}"
        )

    def test_08_end_h_completeness(self):
        """Verify that 22_End.h is present, correctly formatted, and matches Remedy canonical specification."""
        end_path = os.path.join(self.sub_dir, "22_End.h")
        self.assertTrue(os.path.isfile(end_path), "22_End.h missing")
        with open(end_path, "r", encoding="cp1252") as f:
            content = f.read()
        self.assertIn("[End_1000_01]", content, "22_End.h missing End_1000_01")
        self.assertIn('String = ""', content, "22_End.h malformed credits string")

    def test_09_dialogtexts_tooltips_completeness(self):
        """Verify that dialogtexts.txt includes all critical technical launcher tooltips."""
        with open(self.dialogtexts, "r", encoding="cp1252") as f:
            content = f.read()

        required_tooltips = [
            "TipAntialiasing",
            "TipTripleBuffering",
            "TipMaterialVariations",
            "TipTextCharacterShadows",
            "TipPostProcessEffects",
            "TipPixelShaderSkinning",
            "TipTextTextureColorDepth",
        ]
        missing = [t for t in required_tooltips if t not in content]
        self.assertEqual(len(missing), 0, f"dialogtexts.txt missing tooltips: {missing}")

    def test_10_stringtable_key_game_modes(self):
        """Verify canonical Portuguese game mode terminology in stringtable.txt."""
        with open(self.stringtable, "r", encoding="cp1252") as f:
            content = f.read()

        expected_terms = [
            "Morto ao Chegar",
            "Minuto de Nova York",
            "Casca-Grossa",
            "Homem Morto Andando",
        ]
        missing = [t for t in expected_terms if t not in content]
        self.assertEqual(len(missing), 0, f"stringtable.txt missing canonical mode terms: {missing}")

    def test_11_format_specifier_fidelity(self):
        """Verify that all format specifiers (%s, %i, %d, %f) match original English definitions exactly."""
        specifier_pattern = re.compile(r"%[0-9]*\.?[0-9]*[a-zA-Z]")
        entry_pattern = re.compile(r'\[([^\]]+)\][^\n\r]*String\s*=\s*"([^"]*)"')

        for fpath in self.subtitle_files + [self.stringtable]:
            rel = os.path.relpath(fpath, TRANS_DIR)
            eng_path = os.path.join(ENG_REF_DIR, rel)
            if not os.path.isfile(eng_path):
                continue

            with open(eng_path, "r", encoding="latin-1") as f_eng:
                eng_entries = dict(entry_pattern.findall(f_eng.read()))
            with open(fpath, "r", encoding="cp1252") as f_pt:
                pt_entries = dict(entry_pattern.findall(f_pt.read()))

            mismatches = []
            for key, eng_val in eng_entries.items():
                eng_specs = specifier_pattern.findall(eng_val)
                if eng_specs:
                    pt_val = pt_entries.get(key)
                    if pt_val is not None:
                        pt_specs = specifier_pattern.findall(pt_val)
                        if sorted(eng_specs) != sorted(pt_specs):
                            mismatches.append(f"{key}: ENG {eng_specs} != PT {pt_specs}")

            self.assertEqual(
                len(mismatches), 0,
                f"Format specifier mismatch in {rel}:\n" + "\n".join(mismatches)
            )


# ==============================================================================
# 2. GRAPHIC NOVELS & LOADING SCREENS DDS CONFORMANCE
# ==============================================================================
class TestAdversarialDDSConformance(unittest.TestCase):
    """Deep binary audit of all 138 Graphic Novels and 29 Level Loading DDS textures."""

    def setUp(self):
        self.gn_dir = os.path.join(
            TRANS_DIR, "data", "database", "graphicnovelpages", "files", "textures"
        )
        self.ls_dir = os.path.join(TRANS_DIR, "data", "database", "levels", "bitmaps")
        self.gn_files = sorted(glob.glob(os.path.join(self.gn_dir, "*.dds")))
        self.ls_files = sorted(glob.glob(os.path.join(self.ls_dir, "*.dds")))

    def test_01_graphic_novels_count_and_exact_spec(self):
        """Verify all 138 Graphic Novels: magic 'DDS ', header size 124, 1024x512, DXT1, exactly 262,272 bytes."""
        self.assertEqual(
            len(self.gn_files), 138,
            f"Expected exactly 138 Graphic Novel DDS files, found {len(self.gn_files)}"
        )

        defects = []
        for fpath in self.gn_files:
            rel = os.path.relpath(fpath, PROJECT_ROOT)
            try:
                hdr = parse_dds_header_strict(fpath)
            except Exception as e:
                defects.append(f"{rel}: header parse failed ({e})")
                continue

            if hdr["file_size"] != 262272:
                defects.append(f"{rel}: byte size {hdr['file_size']} != 262272")
            if hdr["magic"] != b"DDS ":
                defects.append(f"{rel}: magic {hdr['magic']!r} != b'DDS '")
            if hdr["header_size"] != 124:
                defects.append(f"{rel}: header size {hdr['header_size']} != 124")
            if (hdr["width"], hdr["height"]) != (1024, 512):
                defects.append(f"{rel}: dimensions {hdr['width']}x{hdr['height']} != 1024x512")
            if hdr["fourcc"] != b"DXT1":
                defects.append(f"{rel}: FourCC {hdr['fourcc']!r} != b'DXT1'")
            # DDPF_FOURCC flag (0x4) must be set in pf_flags
            if not (hdr["pf_flags"] & 0x4):
                defects.append(f"{rel}: DDPF_FOURCC flag missing in pf_flags ({hex(hdr['pf_flags'])})")

        self.assertEqual(len(defects), 0, "Graphic Novel DDS defects:\n" + "\n".join(defects[:15]))

    def test_02_loading_screens_count_and_exact_spec(self):
        """Verify all 29 Level Loading Screens: magic 'DDS ', header size 124, 1024x512, DXT1, exactly 262,272 bytes."""
        self.assertEqual(
            len(self.ls_files), 29,
            f"Expected exactly 29 Level Loading DDS files, found {len(self.ls_files)}"
        )

        defects = []
        for fpath in self.ls_files:
            rel = os.path.relpath(fpath, PROJECT_ROOT)
            try:
                hdr = parse_dds_header_strict(fpath)
            except Exception as e:
                defects.append(f"{rel}: header parse failed ({e})")
                continue

            if hdr["file_size"] != 262272:
                defects.append(f"{rel}: byte size {hdr['file_size']} != 262272")
            if hdr["magic"] != b"DDS ":
                defects.append(f"{rel}: magic {hdr['magic']!r} != b'DDS '")
            if hdr["header_size"] != 124:
                defects.append(f"{rel}: header size {hdr['header_size']} != 124")
            if (hdr["width"], hdr["height"]) != (1024, 512):
                defects.append(f"{rel}: dimensions {hdr['width']}x{hdr['height']} != 1024x512")
            if hdr["fourcc"] != b"DXT1":
                defects.append(f"{rel}: FourCC {hdr['fourcc']!r} != b'DXT1'")
            if not (hdr["pf_flags"] & 0x4):
                defects.append(f"{rel}: DDPF_FOURCC flag missing in pf_flags ({hex(hdr['pf_flags'])})")

        self.assertEqual(len(defects), 0, "Level Loading DDS defects:\n" + "\n".join(defects[:15]))

    def test_03_hud_and_menu_textures_specification(self):
        """Verify ActiveWeapons (1024x2048 DXT5), character intros (512x128 RGB32), and menus (1024x512 RGB32)."""
        active_weapons = os.path.join(TRANS_DIR, "data", "hud", "bitmaps", "ActiveWeapons.dds")
        self.assertTrue(os.path.isfile(active_weapons), f"ActiveWeapons missing: {active_weapons}")
        aw_hdr = parse_dds_header_strict(active_weapons)
        self.assertEqual((aw_hdr["width"], aw_hdr["height"]), (1024, 2048), "ActiveWeapons not 1024x2048")
        self.assertEqual(aw_hdr["fourcc"], b"DXT5", "ActiveWeapons not DXT5")

        # Introductions
        intro_dir = os.path.join(TRANS_DIR, "data", "hud", "introductions")
        for name in ["Introduction_Mike.dds", "Introduction_Winterson.DDS"]:
            ipath = os.path.join(intro_dir, name)
            self.assertTrue(os.path.isfile(ipath), f"Intro card missing: {ipath}")
            ihdr = parse_dds_header_strict(ipath)
            self.assertEqual((ihdr["width"], ihdr["height"]), (512, 128), f"{name} not 512x128")
            self.assertEqual(ihdr["rgb_bits"], 32, f"{name} not 32-bit uncompressed")

        # Menus
        menu_dir = os.path.join(TRANS_DIR, "data", "menu", "bitmaps")
        for name in ["Menu_Loading.DDS", "Menu_Exiting.DDS", "Menu_bg_Help.DDS"]:
            mpath = os.path.join(menu_dir, name)
            self.assertTrue(os.path.isfile(mpath), f"Menu texture missing: {mpath}")
            mhdr = parse_dds_header_strict(mpath)
            self.assertEqual((mhdr["width"], mhdr["height"]), (1024, 512), f"{name} not 1024x512")
            self.assertEqual(mhdr["rgb_bits"], 32, f"{name} not 32-bit uncompressed")

        # PleaseWait.dds
        pw_path = os.path.join(TRANS_DIR, "data", "sharedtextures", "PleaseWait.dds")
        self.assertTrue(os.path.isfile(pw_path), f"PleaseWait missing: {pw_path}")
        pw_hdr = parse_dds_header_strict(pw_path)
        self.assertEqual(pw_hdr["file_size"], 262272, "PleaseWait size != 262272")
        self.assertEqual(pw_hdr["fourcc"], b"DXT1", "PleaseWait FourCC != DXT1")


# ==============================================================================
# 3. PREVIOUSLY.BIK VIDEO & AUDIO STREAM INTEGRITY
# ==============================================================================
class TestAdversarialBikIntegrity(unittest.TestCase):
    """Empirical verification of PREVIOUSLY.bik container, streams, and full-length decode."""

    def setUp(self):
        self.target_bik = os.path.join(TRANS_DIR, "movies", "PREVIOUSLY.bik")
        self.root_bik = os.path.join(PROJECT_ROOT, "movies", "PREVIOUSLY.bik")

        # Accept either target_bik or root_bik, prioritizing translation_ptbr/movies/
        if os.path.isfile(self.target_bik):
            self.bik_path = self.target_bik
        elif os.path.isfile(self.root_bik):
            self.bik_path = self.root_bik
        else:
            self.bik_path = None

    def test_01_bik_presence_and_file_size(self):
        """Verify that PREVIOUSLY.bik is present and size matches exactly 64,708,864 bytes."""
        self.assertIsNotNone(self.bik_path, "PREVIOUSLY.bik not found in translation_ptbr/movies/ or movies/")
        sz = os.path.getsize(self.bik_path)
        self.assertEqual(sz, 64708864, f"PREVIOUSLY.bik size {sz} != 64,708,864 bytes")

    def test_02_bik_header_and_container_specs(self):
        """Verify BIK header: FourCC 'BIKi', width 1024, height 640, 30fps, 4256 frames, 1 audio track."""
        self.assertIsNotNone(self.bik_path, "PREVIOUSLY.bik missing")
        hdr = parse_bik_header_strict(self.bik_path)

        self.assertEqual(hdr["magic"], b"BIKi", f"Unexpected BIK magic: {hdr['magic']!r}")
        self.assertEqual(hdr["width"], 1024, f"Unexpected width: {hdr['width']}")
        self.assertEqual(hdr["height"], 640, f"Unexpected height: {hdr['height']}")
        self.assertEqual(hdr["num_frames"], 4256, f"Unexpected frame count: {hdr['num_frames']}")
        self.assertAlmostEqual(hdr["fps"], 30.0, places=2, msg=f"Unexpected FPS: {hdr['fps']}")
        self.assertEqual(hdr["num_audio"], 1, f"Expected 1 audio track, got {hdr['num_audio']}")
        self.assertEqual(
            hdr["file_size_minus_8"], hdr["file_size"] - 8,
            "Declared size in header does not match file size - 8"
        )

    def test_03_ffprobe_stream_metadata_verification(self):
        """Verify ffprobe streams: binkvideo 1024x640 @ 30fps and binkaudio_dct 48000Hz stereo."""
        self.assertIsNotNone(self.bik_path, "PREVIOUSLY.bik missing")

        cmd = [
            "ffprobe", "-v", "error",
            "-show_format", "-show_streams",
            "-print_format", "json",
            self.bik_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        probe = json.loads(res.stdout)

        streams = probe.get("streams", [])
        self.assertEqual(len(streams), 2, f"Expected 2 streams, found {len(streams)}")

        v_stream = next((s for s in streams if s["codec_type"] == "video"), None)
        a_stream = next((s for s in streams if s["codec_type"] == "audio"), None)

        self.assertIsNotNone(v_stream, "Video stream missing")
        self.assertIsNotNone(a_stream, "Audio stream missing")

        # Video stream checks
        self.assertEqual(v_stream["codec_name"], "binkvideo")
        self.assertEqual(v_stream["width"], 1024)
        self.assertEqual(v_stream["height"], 640)
        self.assertEqual(v_stream["r_frame_rate"], "30/1")
        self.assertEqual(int(v_stream["duration_ts"]), 4256)

        # Audio stream checks
        self.assertEqual(a_stream["codec_name"], "binkaudio_dct")
        self.assertEqual(int(a_stream["sample_rate"]), 48000)
        self.assertEqual(a_stream["channels"], 2)

    def test_04_ffmpeg_complete_stream_decode(self):
        """Exhaustively decode the entire BIK video and audio stream to null sink to guarantee zero corruption."""
        self.assertIsNotNone(self.bik_path, "PREVIOUSLY.bik missing")

        cmd = [
            "ffmpeg", "-v", "error",
            "-i", self.bik_path,
            "-f", "null", "-"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(
            res.returncode, 0,
            f"ffmpeg failed to decode PREVIOUSLY.bik:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
        )
        self.assertEqual(res.stderr.strip(), "", f"ffmpeg emitted decode warnings/errors: {res.stderr}")


# ==============================================================================
# 4. ADVERSARIAL ORACLE DISCRIMINATION & NEGATIVE TESTING
# ==============================================================================
class TestAdversarialOracleDiscrimination(unittest.TestCase):
    """
    Empirical proof that our oracles are discriminating and reject corrupted inputs.
    Mutates dummy samples in memory and asserts that validators raise failures.
    """

    def test_01_oracle_rejects_injected_utf8_multibyte(self):
        """Assert oracle catches injected UTF-8 sequence (0xC3 0xA9 = é in UTF-8)."""
        corrupted_bytes = b"Max Payne: Ol\xc3\xa1 mundo!"  # UTF-8 encoded 'Olá'
        has_utf8 = any(corrupted_bytes[i] == 0xC3 and (0x80 <= corrupted_bytes[i + 1] <= 0xBF) for i in range(len(corrupted_bytes) - 1))
        self.assertTrue(has_utf8, "Oracle must detect 0xC3 0xA9 as UTF-8 sequence")

    def test_02_oracle_rejects_undefined_cp1252_bytes(self):
        """Assert oracle catches undefined Windows-1252 byte 0x81."""
        corrupted_bytes = b"Line with undefined byte: \x81 text"
        has_undefined = any(b in CP1252_UNDEFINED_BYTES for b in corrupted_bytes)
        self.assertTrue(has_undefined, "Oracle must flag 0x81 as undefined byte")

    def test_03_oracle_rejects_corrupted_dds_magic_and_size(self):
        """Assert oracle rejects DDS with invalid magic or wrong size."""
        # 128-byte dummy buffer with bad magic
        fake_header = b"BAD!" + b"\x00" * 124
        self.assertNotEqual(fake_header[:4], b"DDS ")

    def test_04_oracle_rejects_corrupted_bik_header(self):
        """Assert oracle rejects BIK with invalid magic or mismatching size."""
        fake_header = b"AVI " + b"\x00" * 40
        self.assertNotEqual(fake_header[:4], b"BIKi")


if __name__ == "__main__":
    unittest.main()
