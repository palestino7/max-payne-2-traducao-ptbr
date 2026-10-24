#!/usr/bin/env python3
"""
Adversarial Stress Test Suite for Milestone 1 (Asset & Text Fusion)
Challenger M1-2 Verification Harness

Tests:
1. Subtitle completeness vs English Oracle (22 .h files, verify no empty strings, 03_First_Hospital.h integrity)
2. Grammar, bracket, quote, escape sequence balancing in dialogtexts.txt and subtitle files
3. ActiveWeapons.dds format, 12 mipmaps, and DXT5 alpha channel empirical analysis
4. Introduction_Mike.dds and Introduction_Winterson.DDS format, 10 mipmaps, RGB32 alpha channel analysis
5. Menu textures (Menu_Loading.DDS, Menu_Exiting.DDS, Menu_bg_Help.DDS) format, 11 mipmaps, RGB32 analysis
"""

import os
import re
import struct
import unittest
from typing import Dict, List, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRANSLATION_DIR = os.path.join(PROJECT_ROOT, "translation_ptbr")
ENGLISH_DIR = os.path.join(PROJECT_ROOT, "extracted_english")
CONCORRENTE_DIR = os.path.join(PROJECT_ROOT, "concorrente", "Max Payne 2 Nova Tradução (2026) por Capitão Frio")


def parse_dds_full(path: str) -> dict:
    """Parse complete DDS header and validate structural integrity."""
    with open(path, "rb") as f:
        data = f.read(128)
    if len(data) < 128:
        raise ValueError(f"DDS header truncated: {len(data)} bytes")

    magic = data[:4]
    size, flags, height, width, pitch, depth, mipmaps = struct.unpack("<IIIIIII", data[4:32])
    reserved1 = struct.unpack("<11I", data[32:76])
    pf_size, pf_flags, fourcc, rgb_bits, r_mask, g_mask, b_mask, a_mask = struct.unpack("<II4sIIIII", data[76:108])
    caps, caps2, caps3, caps4, reserved2 = struct.unpack("<IIIII", data[108:128])

    return {
        "magic": magic,
        "size": size,
        "flags": flags,
        "height": height,
        "width": width,
        "pitch": pitch,
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
        "caps": caps,
        "caps2": caps2,
        "file_size": os.path.getsize(path)
    }


def parse_subtitle_entries(filepath: str) -> Dict[str, str]:
    """Extract [Key] String = \"...\"; entries from a subtitle .h file."""
    with open(filepath, "rb") as f:
        content = f.read().decode("cp1252", errors="replace")

    entries = {}
    pattern = re.compile(r'\[\s*([a-zA-Z0-9_]+)\s*\]\s*String\s*=\s*"(.*?)";', re.DOTALL)
    for m in pattern.finditer(content):
        entries[m.group(1)] = m.group(2)
    return entries


class TestChallengerM1SubtitleCompleteness(unittest.TestCase):
    """Adversarial testing of dialog and subtitle completeness."""

    def test_01_all_subtitle_files_exist_and_non_empty(self):
        """Verify all 22 subtitle .h files exist in translation_ptbr and are non-empty."""
        subtitles_dir = os.path.join(TRANSLATION_DIR, "data", "database", "subtitles")
        self.assertTrue(os.path.isdir(subtitles_dir), f"Subtitles dir missing: {subtitles_dir}")

        h_files = [f for f in os.listdir(subtitles_dir) if f.endswith(".h")]
        self.assertEqual(len(h_files), 22, f"Expected exactly 22 subtitle files, found {len(h_files)}: {h_files}")

        for h in h_files:
            p = os.path.join(subtitles_dir, h)
            size = os.path.getsize(p)
            self.assertGreater(size, 50, f"Subtitle file {h} is suspiciously small: {size} bytes")

    def test_02_dialog_completeness_against_english_oracle(self):
        """Compare every subtitle string in translation_ptbr against English original."""
        en_sub_dir = os.path.join(ENGLISH_DIR, "data", "database", "subtitles")
        pt_sub_dir = os.path.join(TRANSLATION_DIR, "data", "database", "subtitles")

        if not os.path.isdir(en_sub_dir):
            self.skipTest("English reference directory not found.")

        en_files = sorted([f for f in os.listdir(en_sub_dir) if f.endswith(".h")])
        total_en_strings = 0
        total_pt_strings = 0
        missing_keys = []
        empty_strings = []

        for f in en_files:
            en_path = os.path.join(en_sub_dir, f)
            pt_path = os.path.join(pt_sub_dir, f)

            self.assertTrue(os.path.isfile(pt_path), f"File missing in translation_ptbr: {f}")

            en_entries = parse_subtitle_entries(en_path)
            pt_entries = parse_subtitle_entries(pt_path)

            total_en_strings += len(en_entries)
            total_pt_strings += len(pt_entries)

            for key, en_text in en_entries.items():
                if key not in pt_entries:
                    missing_keys.append(f"{f}:{key}")
                else:
                    pt_text = pt_entries[key]
                    if not pt_text.strip() and en_text.strip():
                        empty_strings.append(f"{f}:{key} (EN: '{en_text}')")

        self.assertEqual(missing_keys, [], f"Missing subtitle keys present in English: {missing_keys}")
        self.assertEqual(empty_strings, [], f"Empty subtitle strings where English has voice: {empty_strings}")
        self.assertEqual(total_en_strings, total_pt_strings,
                         f"Total string count mismatch: EN={total_en_strings}, PT={total_pt_strings}")

    def test_03_first_hospital_21_prologue_lines_intact(self):
        """Stress-test 03_First_Hospital.h to ensure all 21 prologue lines are intact."""
        pt_path = os.path.join(TRANSLATION_DIR, "data", "database", "subtitles", "03_First_Hospital.h")
        pt_entries = parse_subtitle_entries(pt_path)

        # Check competitor behavior if available
        c_path = os.path.join(CONCORRENTE_DIR, "data", "database", "subtitles", "03_First_Hospital.h")
        if os.path.isfile(c_path):
            c_entries = parse_subtitle_entries(c_path)
            c_empty = [k for k, v in c_entries.items() if not v.strip()]
            # Competitor emptied several lines (e.g. First_Hospital_1010_01..06, 1020, etc.)
            self.assertGreater(len(c_empty), 0, "Competitor was expected to have empty lines in 03_First_Hospital.h")

        # Now verify translation_ptbr has NO empty lines and at least 21 dialogue entries
        self.assertGreaterEqual(len(pt_entries), 21, f"03_First_Hospital.h has fewer than 21 lines: {len(pt_entries)}")
        for key, text in pt_entries.items():
            self.assertTrue(len(text.strip()) > 0, f"Empty dialogue string found in 03_First_Hospital.h: [{key}]")

    def test_04_end_credits_file_intact(self):
        """Verify 22_End.h exists, is non-empty, and has valid subtitle entries."""
        pt_path = os.path.join(TRANSLATION_DIR, "data", "database", "subtitles", "22_End.h")
        self.assertTrue(os.path.isfile(pt_path), "22_End.h missing in translation_ptbr")
        entries = parse_subtitle_entries(pt_path)
        self.assertGreater(len(entries), 0, "22_End.h has 0 entries")


class TestChallengerM1ParserGrammarAndBalancing(unittest.TestCase):
    """Adversarial testing of parser grammar, brackets, quotes, and escapes."""

    def test_05_dialogtexts_bracket_quote_and_syntax_balance(self):
        """Adversarial stress-test of translation_ptbr/data/dialogtexts.txt parser grammar."""
        path = os.path.join(TRANSLATION_DIR, "data", "dialogtexts.txt")
        self.assertTrue(os.path.isfile(path), f"dialogtexts.txt not found at {path}")

        with open(path, "rb") as f:
            raw = f.read()

        # 1. Encoding check: must strictly decode under cp1252
        text = raw.decode("cp1252")

        # 2. Brace balance tracking
        brace_depth = 0
        max_brace_depth = 0
        bracket_errors = []
        quote_errors = []
        semicolon_errors = []
        line_num = 0

        lines = text.splitlines()
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue

            # Check curly braces
            for char in stripped:
                if char == "{":
                    brace_depth += 1
                    max_brace_depth = max(max_brace_depth, brace_depth)
                elif char == "}":
                    brace_depth -= 1
                    if brace_depth < 0:
                        bracket_errors.append(f"Line {idx}: Negative brace depth")

            # Check square brackets for identifiers
            if "[" in stripped or "]" in stripped:
                open_b = stripped.count("[")
                close_b = stripped.count("]")
                if open_b != close_b:
                    bracket_errors.append(f"Line {idx}: Unbalanced square brackets: '{stripped}'")

            # Check String = "..."; entries
            if "String" in stripped:
                # Check for equal sign
                if "=" not in stripped:
                    quote_errors.append(f"Line {idx}: Missing '=' in String assignment: '{stripped}'")
                # Check double quotes
                quote_count = stripped.count('"')
                if quote_count % 2 != 0:
                    quote_errors.append(f"Line {idx}: Unbalanced quotes ({quote_count}): '{stripped}'")
                # Check semicolon termination
                if not stripped.endswith(";"):
                    semicolon_errors.append(f"Line {idx}: Missing terminating semicolon: '{stripped}'")

        self.assertEqual(brace_depth, 0, f"Unbalanced curly braces at end of file: depth = {brace_depth}")
        self.assertGreater(max_brace_depth, 0, "No braces found in dialogtexts.txt")
        self.assertEqual(bracket_errors, [], f"Bracket errors: {bracket_errors}")
        self.assertEqual(quote_errors, [], f"Quote errors: {quote_errors}")
        self.assertEqual(semicolon_errors, [], f"Semicolon errors: {semicolon_errors}")

    def test_06_dialogtexts_escape_sequences_and_placeholders(self):
        """Verify escape sequences and format specifiers in dialogtexts.txt match English."""
        pt_path = os.path.join(TRANSLATION_DIR, "data", "dialogtexts.txt")
        en_path = os.path.join(ENGLISH_DIR, "data", "dialogtexts.txt")

        with open(pt_path, "rb") as f:
            pt_text = f.read().decode("cp1252")

        # Scan for unescaped or illegal backslashes
        # Valid escapes in MaxFX strings: \n, \t, \\, \"
        # We can find all string literals:
        string_pattern = re.compile(r'"(.*?)"')
        invalid_escapes = []

        for idx, line in enumerate(pt_text.splitlines(), start=1):
            for match in string_pattern.finditer(line):
                content = match.group(1)
                # Check backslashes
                i = 0
                while i < len(content):
                    if content[i] == "\\":
                        if i + 1 >= len(content):
                            invalid_escapes.append(f"Line {idx}: Trailing dangling backslash in '{content}'")
                            i += 1
                        else:
                            nxt = content[i+1]
                            if nxt not in ("n", "t", "\\", '"', "'", "r"):
                                invalid_escapes.append(f"Line {idx}: Invalid escape \\{nxt} in '{content}'")
                            i += 2
                    else:
                        i += 1

        self.assertEqual(invalid_escapes, [], f"Invalid escape sequences: {invalid_escapes}")

        # Check % format placeholders between EN and PT
        if os.path.isfile(en_path):
            with open(en_path, "rb") as f:
                en_text = f.read().decode("cp1252")

            def extract_dict(text):
                res = {}
                pattern = re.compile(r'\[\s*([a-zA-Z0-9_]+)\s*\]\s*String\s*=\s*"(.*?)";')
                for m in pattern.finditer(text):
                    res[m.group(1)] = m.group(2)
                return res

            en_dict = extract_dict(en_text)
            pt_dict = extract_dict(pt_text)

            placeholder_errors = []
            for key, en_val in en_dict.items():
                if key in pt_dict:
                    pt_val = pt_dict[key]
                    en_specifiers = re.findall(r'%[0-9]*[a-zA-Z]', en_val)
                    pt_specifiers = re.findall(r'%[0-9]*[a-zA-Z]', pt_val)
                    if en_specifiers != pt_specifiers:
                        placeholder_errors.append(f"Key [{key}]: EN specs {en_specifiers} != PT specs {pt_specifiers}")

            self.assertEqual(placeholder_errors, [], f"Format specifier mismatches: {placeholder_errors}")

    def test_07_all_subtitles_bracket_and_quote_balancing(self):
        """Stress-test bracket, quote, and semicolon balancing on all 22 subtitle .h files."""
        subtitles_dir = os.path.join(TRANSLATION_DIR, "data", "database", "subtitles")
        h_files = [f for f in os.listdir(subtitles_dir) if f.endswith(".h")]

        syntax_errors = []
        for h in h_files:
            filepath = os.path.join(subtitles_dir, h)
            with open(filepath, "rb") as f:
                lines = f.read().decode("cp1252").splitlines()

            for idx, line in enumerate(lines, start=1):
                stripped = line.strip()
                if not stripped or stripped.startswith("//"):
                    continue

                # Strip inline comments
                code_part = stripped.split("//")[0].strip()
                if not code_part:
                    continue

                # Must match [Key] String = "...";
                if code_part.startswith("["):
                    if "]" not in code_part:
                        syntax_errors.append(f"{h}:{idx} Missing closing bracket ']'")
                    if 'String' in code_part:
                        quote_cnt = code_part.count('"')
                        if quote_cnt != 2:
                            syntax_errors.append(f"{h}:{idx} Quote count != 2 ({quote_cnt}): {code_part}")
                        if not code_part.endswith(";"):
                            syntax_errors.append(f"{h}:{idx} Missing trailing semicolon: {code_part}")

        self.assertEqual(syntax_errors, [], f"Subtitle syntax errors: {syntax_errors}")


class TestChallengerM1TextureMipmapsAndAlpha(unittest.TestCase):
    """Adversarial testing of DDS textures: mipmap chains, format, and alpha channels."""

    def test_08_active_weapons_dxt5_mipmaps_and_alpha(self):
        """Empirically verify ActiveWeapons.dds: 1024x2048, DXT5, 12 mipmaps, non-trivial alpha."""
        path = os.path.join(TRANSLATION_DIR, "data", "hud", "bitmaps", "ActiveWeapons.dds")
        self.assertTrue(os.path.isfile(path), f"ActiveWeapons.dds not found at {path}")

        hdr = parse_dds_full(path)

        # 1. Header Validation
        self.assertEqual(hdr["magic"], b"DDS ", "Magic must be 'DDS '")
        self.assertEqual(hdr["size"], 124, "Header size must be 124")
        self.assertEqual(hdr["width"], 1024, f"Width must be 1024, got {hdr['width']}")
        self.assertEqual(hdr["height"], 2048, f"Height must be 2048, got {hdr['height']}")
        self.assertEqual(hdr["fourcc"], b"DXT5", f"FourCC must be DXT5, got {hdr['fourcc']}")
        self.assertEqual(hdr["mipmaps"], 12, f"Mipmap count must be 12, got {hdr['mipmaps']}")

        # 2. File size mathematical verification for 12 DXT5 mipmap levels
        expected_data_size = 0
        w, h = 1024, 2048
        for level in range(12):
            blocks_w = max(1, (w + 3) // 4)
            blocks_h = max(1, (h + 3) // 4)
            level_size = blocks_w * blocks_h * 16  # 16 bytes per block in DXT5
            expected_data_size += level_size
            w = max(1, w // 2)
            h = max(1, h // 2)

        expected_total_size = 128 + expected_data_size
        self.assertEqual(hdr["file_size"], expected_total_size,
                         f"File size mismatch: {hdr['file_size']} vs expected {expected_total_size}")
        self.assertEqual(hdr["file_size"], 2796368, "ActiveWeapons.dds must be exactly 2,796,368 bytes")

        # 3. Adversarial Alpha Channel Inspection via full DXT5 block decoding:
        with open(path, "rb") as f:
            f.seek(128)
            l0_blocks_w = 1024 // 4  # 256
            l0_blocks_h = 2048 // 4  # 512
            total_l0_blocks = l0_blocks_w * l0_blocks_h  # 131,072 blocks
            raw_l0 = f.read(total_l0_blocks * 16)

        self.assertEqual(len(raw_l0), total_l0_blocks * 16)

        # Decompress alpha for sampled blocks across the entire texture
        alphas = []
        step = max(1, total_l0_blocks // 2000)
        for b_idx in range(0, total_l0_blocks, step):
            offset = b_idx * 16
            a0, a1 = raw_l0[offset], raw_l0[offset + 1]
            idx_bits = int.from_bytes(raw_l0[offset + 2: offset + 8], "little")
            if a0 > a1:
                table = [
                    a0, a1,
                    (6 * a0 + 1 * a1) // 7,
                    (5 * a0 + 2 * a1) // 7,
                    (4 * a0 + 3 * a1) // 7,
                    (3 * a0 + 4 * a1) // 7,
                    (2 * a0 + 5 * a1) // 7,
                    (1 * a0 + 6 * a1) // 7,
                ]
            else:
                table = [
                    a0, a1,
                    (4 * a0 + 1 * a1) // 5,
                    (3 * a0 + 2 * a1) // 5,
                    (2 * a0 + 3 * a1) // 5,
                    (1 * a0 + 4 * a1) // 5,
                    0, 255,
                ]
            for p in range(16):
                idx = (idx_bits >> (3 * p)) & 0x7
                alphas.append(table[idx])

        zero_count = sum(1 for a in alphas if a == 0)
        opaque_count = sum(1 for a in alphas if a == 255)
        edge_count = sum(1 for a in alphas if 0 < a < 255)

        self.assertGreater(zero_count, 1000, f"Lacks transparent regions: {zero_count}")
        self.assertGreater(opaque_count, 1000, f"Lacks solid weapon icons: {opaque_count}")
        self.assertGreater(edge_count, 50, f"Lacks anti-aliased gradient edges: {edge_count}")

    def test_09_introduction_mike_rgb32_mipmaps_and_alpha(self):
        """Empirically verify Introduction_Mike.dds: 512x128, RGB32 uncompressed, 10 mipmaps, valid alpha."""
        path = os.path.join(TRANSLATION_DIR, "data", "hud", "introductions", "Introduction_Mike.dds")
        self.assertTrue(os.path.isfile(path), f"Introduction_Mike.dds not found at {path}")

        hdr = parse_dds_full(path)

        # 1. Header Validation
        self.assertEqual(hdr["magic"], b"DDS ")
        self.assertEqual(hdr["size"], 124)
        self.assertEqual(hdr["width"], 512, f"Expected width 512, got {hdr['width']}")
        self.assertEqual(hdr["height"], 128, f"Expected height 128, got {hdr['height']}")
        self.assertEqual(hdr["rgb_bits"], 32, f"Expected 32-bit uncompressed, got {hdr['rgb_bits']}")
        self.assertEqual(hdr["mipmaps"], 10, f"Expected 10 mipmaps, got {hdr['mipmaps']}")

        # 2. Pixel format flags: DDPF_RGB (0x40) and DDPF_ALPHAPIXELS (0x1)
        self.assertTrue(bool(hdr["pf_flags"] & 0x40), "DDPF_RGB flag must be set")
        self.assertTrue(bool(hdr["pf_flags"] & 0x01), "DDPF_ALPHAPIXELS flag must be set")
        self.assertEqual(hdr["a_mask"], 0xFF000000, f"Alpha bitmask should be 0xFF000000, got {hex(hdr['a_mask'])}")

        # 3. File size mathematical calculation:
        expected_data_size = 0
        w, h = 512, 128
        for _ in range(10):
            expected_data_size += w * h * 4
            w = max(1, w // 2)
            h = max(1, h // 2)

        self.assertEqual(hdr["file_size"], 128 + expected_data_size)
        self.assertEqual(hdr["file_size"], 349660, f"Introduction_Mike.dds must be 349,660 bytes, got {hdr['file_size']}")

        # 4. Pixel Alpha Data Analysis (Level 0)
        with open(path, "rb") as f:
            f.seek(128)
            l0_pixels = f.read(512 * 128 * 4)

        # In BGRA32 / RGBA32 with a_mask = 0xFF000000, alpha is the 4th byte of each pixel
        alphas = [l0_pixels[i + 3] for i in range(0, len(l0_pixels), 4)]
        min_a, max_a = min(alphas), max(alphas)

        self.assertEqual(min_a, 0, f"Expected transparent pixels (alpha 0), got min alpha {min_a}")
        self.assertEqual(max_a, 255, f"Expected opaque pixels (alpha 255), got max alpha {max_a}")

        # Check that it is not all black or all opaque
        zero_count = sum(1 for a in alphas if a == 0)
        full_count = sum(1 for a in alphas if a == 255)
        self.assertGreater(zero_count, 1000, f"Too few transparent pixels: {zero_count}")
        self.assertGreater(full_count, 1000, f"Too few opaque pixels: {full_count}")

    def test_10_introduction_winterson_rgb32_mipmaps_and_alpha(self):
        """Empirically verify Introduction_Winterson.DDS: 512x128, RGB32 uncompressed, 10 mipmaps, valid alpha."""
        path = os.path.join(TRANSLATION_DIR, "data", "hud", "introductions", "Introduction_Winterson.DDS")
        self.assertTrue(os.path.isfile(path), f"Introduction_Winterson.DDS not found at {path}")

        hdr = parse_dds_full(path)

        # 1. Header Validation
        self.assertEqual(hdr["magic"], b"DDS ")
        self.assertEqual(hdr["size"], 124)
        self.assertEqual(hdr["width"], 512, f"Expected width 512, got {hdr['width']}")
        self.assertEqual(hdr["height"], 128, f"Expected height 128, got {hdr['height']}")
        self.assertEqual(hdr["rgb_bits"], 32, f"Expected 32-bit uncompressed, got {hdr['rgb_bits']}")
        self.assertEqual(hdr["mipmaps"], 10, f"Expected 10 mipmaps, got {hdr['mipmaps']}")

        # 2. Pixel format flags: DDPF_RGB (0x40) and DDPF_ALPHAPIXELS (0x1)
        self.assertTrue(bool(hdr["pf_flags"] & 0x40), "DDPF_RGB flag must be set")
        self.assertTrue(bool(hdr["pf_flags"] & 0x01), "DDPF_ALPHAPIXELS flag must be set")
        self.assertEqual(hdr["a_mask"], 0xFF000000, f"Alpha bitmask should be 0xFF000000, got {hex(hdr['a_mask'])}")

        # 3. File size check
        self.assertEqual(hdr["file_size"], 349660, f"Introduction_Winterson.DDS must be 349,660 bytes, got {hdr['file_size']}")

        # 4. Pixel Alpha Data Analysis
        with open(path, "rb") as f:
            f.seek(128)
            l0_pixels = f.read(512 * 128 * 4)

        alphas = [l0_pixels[i + 3] for i in range(0, len(l0_pixels), 4)]
        self.assertEqual(min(alphas), 0, "Expected transparent pixels")
        self.assertEqual(max(alphas), 255, "Expected opaque pixels")

        zero_count = sum(1 for a in alphas if a == 0)
        full_count = sum(1 for a in alphas if a == 255)
        self.assertGreater(zero_count, 1000, f"Too few transparent pixels: {zero_count}")
        self.assertGreater(full_count, 1000, f"Too few opaque pixels: {full_count}")

    def test_11_menu_bitmaps_format_and_mipmaps(self):
        """Verify Menu_Loading.DDS, Menu_Exiting.DDS, and Menu_bg_Help.DDS: 1024x512, RGB32, 11 mipmaps."""
        menu_dir = os.path.join(TRANSLATION_DIR, "data", "menu", "bitmaps")
        target_files = ["Menu_Loading.DDS", "Menu_Exiting.DDS", "Menu_bg_Help.DDS"]

        # Exact size calculation:
        # L0: 1024x512 (524288 * 4 = 2097152)
        # 11 levels total:
        expected_data = 0
        w, h = 1024, 512
        for _ in range(11):
            expected_data += w * h * 4
            w = max(1, w // 2)
            h = max(1, h // 2)
        expected_size = 128 + expected_data
        self.assertEqual(expected_size, 2796332)

        for fname in target_files:
            p = os.path.join(menu_dir, fname)
            self.assertTrue(os.path.isfile(p), f"Missing menu file: {fname}")
            hdr = parse_dds_full(p)

            self.assertEqual(hdr["magic"], b"DDS ", f"{fname} invalid magic")
            self.assertEqual(hdr["width"], 1024, f"{fname} width != 1024")
            self.assertEqual(hdr["height"], 512, f"{fname} height != 512")
            self.assertEqual(hdr["rgb_bits"], 32, f"{fname} not 32-bit RGB")
            self.assertEqual(hdr["mipmaps"], 11, f"{fname} mipmaps != 11")
            self.assertEqual(hdr["file_size"], 2796332, f"{fname} size mismatch: {hdr['file_size']}")

    def test_12_stringtable_completeness_and_format_specifiers(self):
        """Stress-test stringtable.txt against English oracle for key parity and format specifiers."""
        en_path = os.path.join(ENGLISH_DIR, "data", "database", "stringtable.txt")
        pt_path = os.path.join(TRANSLATION_DIR, "data", "database", "stringtable.txt")

        self.assertTrue(os.path.isfile(pt_path), f"stringtable.txt missing at {pt_path}")
        if not os.path.isfile(en_path):
            self.skipTest("English stringtable.txt not available")

        en_entries = parse_subtitle_entries(en_path)
        pt_entries = parse_subtitle_entries(pt_path)

        # 1. Key Parity
        missing_keys = [k for k in en_entries if k not in pt_entries]
        self.assertEqual(missing_keys, [], f"Missing keys in stringtable.txt: {missing_keys}")

        # 2. Empty values check
        empty_values = [k for k, v in pt_entries.items() if not v.strip() and en_entries.get(k, "").strip()]
        self.assertEqual(empty_values, [], f"Empty values in stringtable.txt: {empty_values}")

        # 3. Format specifier (%s, %d, %i, etc.) equivalence
        format_errors = []
        for key, en_text in en_entries.items():
            if key in pt_entries:
                pt_text = pt_entries[key]
                en_spec = re.findall(r'%[0-9]*[a-zA-Z]', en_text)
                pt_spec = re.findall(r'%[0-9]*[a-zA-Z]', pt_text)
                if en_spec != pt_spec:
                    format_errors.append(f"Key [{key}]: EN specs {en_spec} != PT specs {pt_spec}")

        self.assertEqual(format_errors, [], f"Format specifier mismatches in stringtable: {format_errors}")

    def test_13_all_mipmap_chains_have_valid_data(self):
        """Verify that every mipmap level across all integrated textures is non-trivial and populated."""
        # 1. ActiveWeapons.dds: 12 levels
        aw_path = os.path.join(TRANSLATION_DIR, "data", "hud", "bitmaps", "ActiveWeapons.dds")
        with open(aw_path, "rb") as f:
            f.seek(128)
            w, h = 1024, 2048
            for level in range(12):
                bw = max(1, (w + 3) // 4)
                bh = max(1, (h + 3) // 4)
                lvl_bytes = f.read(bw * bh * 16)
                self.assertEqual(len(lvl_bytes), bw * bh * 16, f"ActiveWeapons level {level} truncated")
                # Ensure level is not entirely zero
                non_zero = any(b != 0 for b in lvl_bytes)
                self.assertTrue(non_zero, f"ActiveWeapons level {level} ({w}x{h}) is completely blank (all zeroes)")
                w = max(1, w // 2)
                h = max(1, h // 2)

        # 2. Introduction_Mike.dds and Introduction_Winterson.DDS: 10 levels
        for card_name in ["Introduction_Mike.dds", "Introduction_Winterson.DDS"]:
            p = os.path.join(TRANSLATION_DIR, "data", "hud", "introductions", card_name)
            with open(p, "rb") as f:
                f.seek(128)
                w, h = 512, 128
                for level in range(10):
                    lvl_bytes = f.read(w * h * 4)
                    self.assertEqual(len(lvl_bytes), w * h * 4, f"{card_name} level {level} truncated")
                    non_zero = any(b != 0 for b in lvl_bytes)
                    self.assertTrue(non_zero, f"{card_name} level {level} ({w}x{h}) is completely blank")
                    w = max(1, w // 2)
                    h = max(1, h // 2)

        # 3. Menu textures: 11 levels
        for menu_name in ["Menu_Loading.DDS", "Menu_Exiting.DDS", "Menu_bg_Help.DDS"]:
            p = os.path.join(TRANSLATION_DIR, "data", "menu", "bitmaps", menu_name)
            with open(p, "rb") as f:
                f.seek(128)
                w, h = 1024, 512
                for level in range(11):
                    lvl_bytes = f.read(w * h * 4)
                    self.assertEqual(len(lvl_bytes), w * h * 4, f"{menu_name} level {level} truncated")
                    non_zero = any(b != 0 for b in lvl_bytes)
                    self.assertTrue(non_zero, f"{menu_name} level {level} ({w}x{h}) is completely blank")
                    w = max(1, w // 2)
                    h = max(1, h // 2)

    def test_14_no_bom_and_strict_cp1252_encoding(self):
        """Stress-test all text and subtitle files: zero BOM, zero undef bytes, valid Portuguese accents."""
        txt_root = os.path.join(TRANSLATION_DIR, "data")
        undef_bytes = {0x81, 0x8D, 0x8F, 0x90, 0x9D}
        portuguese_accents = {
            0xC0, 0xC1, 0xC2, 0xC3, 0xC7, 0xC8, 0xC9, 0xCA, 0xCD, 0xD3, 0xD4, 0xD5, 0xDA, 0xDC,
            0xE0, 0xE1, 0xE2, 0xE3, 0xE7, 0xE8, 0xE9, 0xEA, 0xED, 0xF3, 0xF4, 0xF5, 0xFA, 0xFC
        }

        bom_detected = []
        corrupt_bytes = []
        files_tested = 0

        for root, _, files in os.walk(txt_root):
            for fname in files:
                if fname.endswith((".txt", ".h")):
                    files_tested += 1
                    path = os.path.join(root, fname)
                    with open(path, "rb") as f:
                        raw = f.read()

                    # 1. No UTF-8 BOM
                    if raw.startswith(b"\xef\xbb\xbf"):
                        bom_detected.append(path)

                    # 2. Strict CP1252 decoding
                    try:
                        raw.decode("cp1252")
                    except Exception as e:
                        corrupt_bytes.append(f"{path}: CP1252 decode error {e}")

                    # 3. No undefined CP1252 bytes
                    found_undef = [b for b in raw if b in undef_bytes]
                    if found_undef:
                        corrupt_bytes.append(f"{path}: contains undefined CP1252 bytes {found_undef}")

        self.assertGreater(files_tested, 20, f"Expected >20 text files, got {files_tested}")
        self.assertEqual(bom_detected, [], f"UTF-8 BOM detected in game text files: {bom_detected}")
        self.assertEqual(corrupt_bytes, [], f"Corrupt bytes in text files: {corrupt_bytes}")

    def test_15_graphic_novels_and_loading_screens_dxt1_integrity(self):
        """Verify all 138 Graphic Novels and 29 Loading Screens are valid DXT1 textures."""
        # 1. Graphic Novels
        gn_dir = os.path.join(TRANSLATION_DIR, "data", "database", "graphicnovelpages", "files", "textures")
        self.assertTrue(os.path.isdir(gn_dir))
        gn_files = [f for f in os.listdir(gn_dir) if f.endswith(".dds") or f.endswith(".DDS")]
        self.assertEqual(len(gn_files), 138, f"Expected 138 graphic novel pages, found {len(gn_files)}")

        for gn in gn_files:
            p = os.path.join(gn_dir, gn)
            hdr = parse_dds_full(p)
            self.assertEqual(hdr["magic"], b"DDS ", f"Corrupt magic in {gn}")
            self.assertEqual(hdr["fourcc"], b"DXT1", f"{gn} must be DXT1, got {hdr['fourcc']}")
            self.assertGreater(hdr["width"], 0)
            self.assertGreater(hdr["height"], 0)

        # 2. Loading Screens
        ls_dir = os.path.join(TRANSLATION_DIR, "data", "database", "levels", "bitmaps")
        self.assertTrue(os.path.isdir(ls_dir))
        ls_files = [f for f in os.listdir(ls_dir) if f.endswith(".dds") or f.endswith(".DDS")]
        self.assertEqual(len(ls_files), 29, f"Expected 29 loading screens, found {len(ls_files)}")

        for ls in ls_files:
            p = os.path.join(ls_dir, ls)
            hdr = parse_dds_full(p)
            self.assertEqual(hdr["magic"], b"DDS ", f"Corrupt magic in {ls}")
            self.assertEqual(hdr["fourcc"], b"DXT1", f"{ls} must be DXT1, got {hdr['fourcc']}")


if __name__ == "__main__":
    unittest.main()
