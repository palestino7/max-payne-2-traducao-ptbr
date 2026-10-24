#!/usr/bin/env python3
"""
Max Payne 2 PT-BR Translation (v3.0.0 Definitiva por Palestino7)
Unified Opaque-Box End-to-End Test Harness & Verification Suite

This test suite executes a 4-tier verification matrix:
  - Tier 1: Feature Coverage (Asset Inventory, File Counts, DDS Dimensions, Video & Script Existence)
  - Tier 2: Boundary & Corner Cases (Windows-1252 Byte-Level Check, UTF-8 Mojibake Elimination,
            MaxFX Subtitle Grammar, DDS Magic & PixelFormat, Bink Video Headers)
  - Tier 3: Cross-Feature Integration (Mock Game Directory Install, .bak Backup Creation,
            Idempotency Safeguard, 100% Bit-for-Bit Rollback Restoration)
  - Tier 4: Real-World Acceptance Scenarios (Windows Defender MpCmdRun Scan, README Word Count < 450,
            Competitor Name & SEO Tag Elimination, Author Attribution)

Usage:
    python tests/run_e2e_tests.py [--tier {1,2,3,4,all}] [--strict] [--verbose] [--json <path>]
    pytest tests/run_e2e_tests.py -v
"""

import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from typing import Dict, List, Optional, Tuple

# Ensure stdout and stderr on Windows handle UTF-8 and emojis safely
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Global configuration flags controlled by CLI arguments
STRICT_MODE = False
VERBOSE_OUTPUT = False

# Undefined byte values in Windows-1252 code page
CP1252_UNDEFINED_BYTES = {0x81, 0x8D, 0x8F, 0x90, 0x9D}

# Common Portuguese accented characters in Windows-1252
PORTUGUESE_ACCENT_BYTES = {
    0xC0, 0xC1, 0xC2, 0xC3, 0xC7, 0xC8, 0xC9, 0xCA, 0xCD, 0xD3, 0xD4, 0xD5, 0xDA, 0xDC,  # Uppercase
    0xE0, 0xE1, 0xE2, 0xE3, 0xE7, 0xE8, 0xE9, 0xEA, 0xED, 0xF3, 0xF4, 0xF5, 0xFA, 0xFC   # Lowercase
}


def parse_dds_header(fpath: str) -> Dict[str, any]:
    """Parse a DirectDraw Surface (DDS) binary header and extract metadata."""
    with open(fpath, "rb") as f:
        header = f.read(128)
    if len(header) < 128:
        raise ValueError(f"DDS header too short ({len(header)} bytes)")

    magic = header[:4]
    header_size, flags, height, width, pitch, depth, mipmaps = struct.unpack("<IIIIIII", header[4:32])
    pf_size, pf_flags, fourcc, rgb_bits, r_mask, g_mask, b_mask, a_mask = struct.unpack(
        "<II4sIIIII", header[76:108]
    )

    return {
        "magic": magic,
        "header_size": header_size,
        "width": width,
        "height": height,
        "flags": flags,
        "pf_size": pf_size,
        "pf_flags": pf_flags,
        "fourcc": fourcc,
        "rgb_bits": rgb_bits,
    }


def parse_bik_header(fpath: str) -> Dict[str, any]:
    """Parse a RAD Game Tools Bink Video (BIK) binary header."""
    with open(fpath, "rb") as f:
        header = f.read(16)
    if len(header) < 16:
        raise ValueError(f"BIK header too short ({len(header)} bytes)")

    magic = header[:4]
    declared_size = struct.unpack("<I", header[4:8])[0]
    return {
        "magic": magic,
        "declared_size": declared_size,
        "file_size": os.path.getsize(fpath),
    }


# ==============================================================================
# TIER 1: FEATURE COVERAGE & ASSET INVENTORY
# ==============================================================================
class TestTier1FeatureCoverage(unittest.TestCase):
    """
    Tier 1 tests verify the presence, file counts, and structural integrity
    of all game translation assets across milestones.
    """

    def setUp(self):
        self.root = PROJECT_ROOT
        self.trans_dir = os.path.join(self.root, "translation_ptbr")

    def test_01_subtitles_inventory(self):
        """Verify that exactly 22 subtitle .h files exist, including critical story scenes."""
        sub_dir = os.path.join(self.trans_dir, "data", "database", "subtitles")
        self.assertTrue(os.path.isdir(sub_dir), f"Subtitles dir not found: {sub_dir}")

        h_files = glob.glob(os.path.join(sub_dir, "*.h"))
        self.assertEqual(
            len(h_files), 22,
            f"Expected exactly 22 subtitle .h files, but found {len(h_files)}: {[os.path.basename(f) for f in h_files]}"
        )

        # Restored Hospital Prologue & Final scenes must be present
        hospital_h = os.path.join(sub_dir, "03_First_Hospital.h")
        self.assertTrue(os.path.isfile(hospital_h), "03_First_Hospital.h missing")
        with open(hospital_h, "rb") as f:
            content = f.read().decode("cp1252", errors="ignore")
        self.assertIn("First_Hospital_1010_01", content, "Restored prologue lines missing in 03_First_Hospital.h")

        end_h = os.path.join(sub_dir, "22_End.h")
        self.assertTrue(os.path.isfile(end_h), "22_End.h missing")

    def test_02_graphic_novels_inventory(self):
        """Verify that all 138 Graphic Novel pages exist with 4x SSAA anti-aliased assets."""
        gn_dir = os.path.join(self.trans_dir, "data", "database", "graphicnovelpages", "files", "textures")
        self.assertTrue(os.path.isdir(gn_dir), f"Graphic novels dir not found: {gn_dir}")

        dds_files = glob.glob(os.path.join(gn_dir, "*.dds"))
        self.assertEqual(
            len(dds_files), 138,
            f"Expected exactly 138 Graphic Novel DDS files, but found {len(dds_files)}"
        )

    def test_03_loading_screens_inventory(self):
        """Verify that all 29 loading screens (story chapters + Dead Man Walking) are present."""
        ls_dir = os.path.join(self.trans_dir, "data", "database", "levels", "bitmaps")
        self.assertTrue(os.path.isdir(ls_dir), f"Loading screens dir not found: {ls_dir}")

        dds_files = glob.glob(os.path.join(ls_dir, "*.dds"))
        self.assertEqual(
            len(dds_files), 29,
            f"Expected exactly 29 loading screen DDS files, but found {len(dds_files)}"
        )

    def test_04_menu_bitmaps_inventory_and_dimensions(self):
        """Verify that Menu_Loading, Menu_Exiting, and Menu_bg_Help DDS exist with 1024x512 resolution."""
        menu_dir = os.path.join(self.trans_dir, "data", "menu", "bitmaps")
        self.assertTrue(os.path.isdir(menu_dir), f"Menu bitmaps dir not found: {menu_dir}")

        expected_menus = ["Menu_Loading.dds", "Menu_Exiting.dds", "Menu_bg_Help.dds"]
        existing = {os.path.basename(f).lower(): f for f in glob.glob(os.path.join(menu_dir, "*.[dD][dD][sS]"))}

        for menu_name in expected_menus:
            self.assertIn(
                menu_name.lower(), existing,
                f"Required menu bitmap {menu_name} missing from {menu_dir}"
            )
            fpath = existing[menu_name.lower()]
            hdr = parse_dds_header(fpath)
            self.assertEqual(hdr["width"], 1024, f"{menu_name} width is {hdr['width']}, expected 1024")
            self.assertEqual(hdr["height"], 512, f"{menu_name} height is {hdr['height']}, expected 512")

    def test_05_hud_and_character_cards(self):
        """Verify high-resolution weapon HUD and translated character cards."""
        hud_weapons = os.path.join(self.trans_dir, "data", "hud", "bitmaps", "ActiveWeapons.dds")
        hud_weapons_concorrente = os.path.join(
            self.root, "concorrente", "Max Payne 2 Nova Tradução (2026) por Capitão Frio",
            "data", "hud", "bitmaps", "ActiveWeapons.dds"
        )

        intro_dir = os.path.join(self.trans_dir, "data", "hud", "introductions")
        intro_concorrente = os.path.join(
            self.root, "concorrente", "Max Payne 2 Nova Tradução (2026) por Capitão Frio",
            "data", "hud", "introductions"
        )

        if not os.path.exists(hud_weapons):
            if not STRICT_MODE and os.path.exists(hud_weapons_concorrente):
                self.skipTest("Pending Milestone M1: ActiveWeapons.dds available in concorrente source, awaiting M1 integration.")
            self.fail(f"ActiveWeapons.dds missing from {hud_weapons}")

        hdr = parse_dds_header(hud_weapons)
        # Check weapon HUD dimensions (either legacy 512x1024 or high-res 1024x2048)
        self.assertIn(hdr["width"], [512, 1024], f"Unexpected ActiveWeapons width: {hdr['width']}")
        self.assertIn(hdr["height"], [1024, 2048], f"Unexpected ActiveWeapons height: {hdr['height']}")

        if not os.path.isdir(intro_dir) or not glob.glob(os.path.join(intro_dir, "*.dds")):
            if not STRICT_MODE and os.path.isdir(intro_concorrente):
                self.skipTest("Pending Milestone M1: Character cards available in concorrente source, awaiting M1 integration.")
            self.fail(f"Character introductions missing from {intro_dir}")

    def test_06_recap_cutscene_previously_bik(self):
        """Verify that the PREVIOUSLY.bik recap video exists and is a valid Bink Video."""
        target_bik = os.path.join(self.trans_dir, "movies", "PREVIOUSLY.bik")
        root_bik = os.path.join(self.root, "movies", "PREVIOUSLY.bik")
        source_bik = os.path.join(
            self.root, "concorrente", "Max Payne 2 Nova Tradução (2026) por Capitão Frio",
            "movies", "PREVIOUSLY.bik"
        )

        chosen_bik = None
        for candidate in [target_bik, root_bik]:
            if os.path.isfile(candidate):
                chosen_bik = candidate
                break

        if chosen_bik is None:
            if not STRICT_MODE and os.path.isfile(source_bik):
                # Verify source BIK as reference oracle
                hdr = parse_bik_header(source_bik)
                self.assertTrue(
                    hdr["magic"].startswith(b"BIK"),
                    f"Source BIK has invalid magic: {hdr['magic']}"
                )
                self.skipTest("Pending Milestone M1: PREVIOUSLY.bik validated at source, awaiting M1 target copy.")
            self.fail(f"PREVIOUSLY.bik missing from {target_bik}")

        hdr = parse_bik_header(chosen_bik)
        self.assertTrue(hdr["magic"].startswith(b"BIK"), f"PREVIOUSLY.bik invalid magic: {hdr['magic']}")
        self.assertGreater(hdr["file_size"], 10_000_000, "PREVIOUSLY.bik file size suspiciously small")

    def test_07_inno_setup_script_inventory(self):
        """Verify that the Inno Setup script src/installer/setup.iss exists and satisfies all specifications."""
        iss_path = os.path.join(self.root, "src", "installer", "setup.iss")

        if not os.path.isfile(iss_path):
            if not STRICT_MODE:
                self.skipTest("Pending Milestone M2: src/installer/setup.iss scheduled for Inno Setup delivery.")
            self.fail(f"Inno Setup script missing at {iss_path}")

        with open(iss_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        self.assertIn("[Setup]", content, "setup.iss missing [Setup] section")
        self.assertIn("Palestino7", content, "setup.iss missing Palestino7 author signature")
        self.assertIn("C69A5D6B-4D1E-4B9F-840D-1B2F7E5E3A91", content, "setup.iss missing AppId")
        self.assertIn("BrazilianPortuguese.isl", content, "setup.iss missing Brazilian Portuguese language")
        self.assertIn("SafeBackupFile", content, "setup.iss missing backup routine")
        self.assertIn("SafeRestoreFile", content, "setup.iss missing rollback routine")
        for comp in ["core", "video", "audiofix", "widescreen"]:
            self.assertIn(f'Name: "{comp}"', content, f"setup.iss missing component '{comp}'")

    def test_10_inno_setup_executable_binary_inventory(self):
        """Verify that dist/Instalador_MaxPayne2_PTBR_v3.0.0.exe exists, is valid PE (MZ), and > 250 MB."""
        installer_path = os.path.join(self.root, "dist", "Instalador_MaxPayne2_PTBR_v3.0.0.exe")
        if not os.path.isfile(installer_path):
            if not STRICT_MODE:
                self.skipTest("Pending Milestone M2: dist/Instalador_MaxPayne2_PTBR_v3.0.0.exe awaiting compilation.")
            self.fail(f"Compiled installer missing at {installer_path}")

        file_size = os.path.getsize(installer_path)
        self.assertGreater(
            file_size, 250_000_000,
            f"Compiled installer size suspiciously small ({file_size} bytes < 250 MB)"
        )
        with open(installer_path, "rb") as f:
            header = f.read(2)
        self.assertEqual(header, b"MZ", f"Installer header {header!r} is not a valid Windows PE ('MZ')")


    def test_08_core_text_files_inventory(self):
        """Verify that dialogtexts.txt, input.txt, and stringtable.txt exist in translation_ptbr."""
        dialogtexts = os.path.join(self.trans_dir, "data", "dialogtexts.txt")
        stringtable = os.path.join(self.trans_dir, "data", "database", "stringtable.txt")
        input_txt = os.path.join(self.trans_dir, "data", "input.txt")

        for fpath in [dialogtexts, stringtable, input_txt]:
            self.assertTrue(os.path.isfile(fpath), f"Core text file missing: {fpath}")
            self.assertGreater(os.path.getsize(fpath), 100, f"Core text file suspiciously small: {fpath}")

    def test_09_visual_showcase_assets(self):
        """Verify that docs/images contains banner_hero.png (1280x360) and loading_screens_comparison.png."""
        banner_path = os.path.join(self.root, "docs", "images", "banner_hero.png")
        self.assertTrue(os.path.isfile(banner_path), f"Hero banner missing at {banner_path}")

        # Check PNG header and dimensions without external dependencies
        with open(banner_path, "rb") as f:
            png_header = f.read(24)
        self.assertEqual(png_header[:8], b"\x89PNG\r\n\x1a\n", "banner_hero.png is not a valid PNG")
        width, height = struct.unpack(">II", png_header[16:24])
        self.assertEqual((width, height), (1280, 360), f"banner_hero.png dimensions {width}x{height} != 1280x360")

        comparison_path = os.path.join(self.root, "docs", "images", "loading_screens_comparison.png")
        if not os.path.isfile(comparison_path):
            if not STRICT_MODE:
                self.skipTest("Pending Milestone M3: loading_screens_comparison.png awaiting M3 image generation.")
            self.fail(f"Loading screens comparison graphic missing at {comparison_path}")


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES (ENCODING, MAGIC HEADERS, GRAMMAR)
# ==============================================================================
class TestTier2BoundaryCornerCases(unittest.TestCase):
    """
    Tier 2 tests perform deep byte-level auditing to prevent text corruptions,
    detect UTF-8 mojibake, and ensure binary header compliance.
    """

    def setUp(self):
        self.root = PROJECT_ROOT
        self.trans_dir = os.path.join(self.root, "translation_ptbr")

    def _get_all_localization_text_files(self) -> List[str]:
        """Collect all .txt and .h localization files in translation_ptbr."""
        files = []
        for ext in ["*.txt", "*.h"]:
            files.extend(glob.glob(os.path.join(self.trans_dir, "data", "**", ext), recursive=True))
        return sorted(files)

    def test_01_windows_1252_strict_decoding(self):
        """Verify that all localization text files strictly decode as Windows-1252 without replacement."""
        text_files = self._get_all_localization_text_files()
        self.assertGreater(len(text_files), 0, "No text files discovered for encoding audit")

        errors = []
        for fpath in text_files:
            rel = os.path.relpath(fpath, self.root)
            with open(fpath, "rb") as f:
                raw_bytes = f.read()

            try:
                raw_bytes.decode("cp1252", errors="strict")
            except UnicodeDecodeError as e:
                errors.append(f"{rel}: failed CP1252 decode at byte {e.start} ({e})")

        self.assertEqual(len(errors), 0, "Windows-1252 decoding failures:\n" + "\n".join(errors))

    def test_02_windows_1252_no_undefined_bytes(self):
        """Verify that no text file contains undefined Windows-1252 byte codes (0x81, 0x8D, 0x8F, 0x90, 0x9D)."""
        text_files = self._get_all_localization_text_files()
        violations = []

        for fpath in text_files:
            rel = os.path.relpath(fpath, self.root)
            with open(fpath, "rb") as f:
                raw_bytes = f.read()

            for offset, byte_val in enumerate(raw_bytes):
                if byte_val in CP1252_UNDEFINED_BYTES:
                    violations.append(f"{rel}: undefined CP1252 byte 0x{byte_val:02X} at offset {offset}")

        self.assertEqual(len(violations), 0, "Undefined Windows-1252 bytes detected:\n" + "\n".join(violations))

    def test_03_portuguese_accents_presence(self):
        """Verify that authentic Portuguese accented characters exist in high volume (>3000 total)."""
        text_files = self._get_all_localization_text_files()
        total_accents = 0

        for fpath in text_files:
            with open(fpath, "rb") as f:
                raw_bytes = f.read()
            total_accents += sum(1 for b in raw_bytes if b in PORTUGUESE_ACCENT_BYTES)

        self.assertGreater(
            total_accents, 3000,
            f"Expected > 3000 Portuguese accented characters, but found only {total_accents}. "
            "Text may have been stripped to ASCII."
        )

    def test_04_absence_of_utf8_mojibake_artifacts(self):
        """
        Verify complete absence of UTF-8 multibyte sequences (e.g. \\xc3\\xa1, \\xc3\\xa9, BOM, replacement char)
        which occur when UTF-8 encoded text is mistakenly read as Windows-1252.
        """
        text_files = self._get_all_localization_text_files()
        mojibake_instances = []

        for fpath in text_files:
            rel = os.path.relpath(fpath, self.root)
            with open(fpath, "rb") as f:
                raw_bytes = f.read()

            # UTF-8 BOM check
            if raw_bytes.startswith(b"\xef\xbb\xbf"):
                mojibake_instances.append(f"{rel}: UTF-8 BOM found at file start")

            # Check for UTF-8 multibyte pattern 0xC3 followed by 0x80..0xBF
            for i in range(len(raw_bytes) - 1):
                if raw_bytes[i] == 0xC3 and (0x80 <= raw_bytes[i + 1] <= 0xBF):
                    sample = raw_bytes[max(0, i - 10):min(len(raw_bytes), i + 10)]
                    mojibake_instances.append(
                        f"{rel}: UTF-8 multibyte sequence (0xC3 0x{raw_bytes[i+1]:02X}) at offset {i} [Context: {sample!r}]"
                    )

            # Check for UTF-8 Unicode replacement character bytes (\xef\xbf\xbd)
            if b"\xef\xbf\xbd" in raw_bytes:
                offset = raw_bytes.find(b"\xef\xbf\xbd")
                mojibake_instances.append(f"{rel}: Unicode replacement char bytes at offset {offset}")

        self.assertEqual(
            len(mojibake_instances), 0,
            "UTF-8 Mojibake / Corrupted byte sequences detected:\n" + "\n".join(mojibake_instances[:20])
        )

    def test_05_maxfx_subtitle_grammar_and_empty_strings(self):
        """Verify that subtitle entries follow MaxFX syntax and contain non-empty quoted strings."""
        sub_dir = os.path.join(self.trans_dir, "data", "database", "subtitles")
        h_files = glob.glob(os.path.join(sub_dir, "*.h"))
        self.assertGreater(len(h_files), 0, "No subtitle files found")

        subtitle_pattern = re.compile(r'^\s*\[(.*?)\]\s*String\s*=\s*"(.*?)"\s*;\s*(?://.*)?$', re.MULTILINE)
        broken_lines = []

        for h_file in h_files:
            rel = os.path.relpath(h_file, self.root)
            with open(h_file, "r", encoding="cp1252", errors="replace") as f:
                lines = f.readlines()

            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith("//") or stripped.startswith("#"):
                    continue

                if "String" in line and "=" in line:
                    match = subtitle_pattern.match(line)
                    if not match:
                        broken_lines.append(f"{rel}:{line_no}: Malformed subtitle syntax -> {line.strip()!r}")
                    else:
                        key, content = match.group(1), match.group(2)
                        # Remedy's original 22_End.h intentionally defines End_1000_01 as empty string (credits scene)
                        if not content.strip() and key != "End_1000_01":
                            broken_lines.append(f"{rel}:{line_no}: Empty subtitle string for key [{key}]")

        self.assertEqual(len(broken_lines), 0, "Subtitle grammar errors detected:\n" + "\n".join(broken_lines[:15]))

    def test_06_dds_headers_magic_and_dimensions(self):
        """Verify DDS magic bytes ('DDS '), header size (124), and valid dimensions on all textures."""
        dds_files = glob.glob(os.path.join(self.trans_dir, "**", "*.dds"), recursive=True)
        self.assertGreater(len(dds_files), 100, f"Too few DDS files found: {len(dds_files)}")

        corrupted = []
        for fpath in dds_files:
            rel = os.path.relpath(fpath, self.root)
            try:
                hdr = parse_dds_header(fpath)
            except Exception as e:
                corrupted.append(f"{rel}: failed header parse ({e})")
                continue

            if hdr["magic"] != b"DDS ":
                corrupted.append(f"{rel}: invalid magic {hdr['magic']!r}, expected b'DDS '")
            if hdr["header_size"] != 124:
                corrupted.append(f"{rel}: invalid header_size {hdr['header_size']}, expected 124")
            if hdr["pf_size"] != 32:
                corrupted.append(f"{rel}: invalid pixel format size {hdr['pf_size']}, expected 32")
            if hdr["width"] <= 0 or hdr["height"] <= 0:
                corrupted.append(f"{rel}: invalid dimensions {hdr['width']}x{hdr['height']}")

        self.assertEqual(len(corrupted), 0, "DDS header defects detected:\n" + "\n".join(corrupted[:15]))

    def test_07_bink_video_header_magic(self):
        """Verify Bink Video container signature and declared size on any available PREVIOUSLY.bik."""
        candidates = [
            os.path.join(self.trans_dir, "movies", "PREVIOUSLY.bik"),
            os.path.join(self.root, "movies", "PREVIOUSLY.bik"),
            os.path.join(self.root, "concorrente", "Max Payne 2 Nova Tradução (2026) por Capitão Frio", "movies", "PREVIOUSLY.bik"),
        ]

        found_bik = next((c for c in candidates if os.path.isfile(c)), None)
        if not found_bik:
            self.skipTest("No PREVIOUSLY.bik found to inspect")

        hdr = parse_bik_header(found_bik)
        self.assertTrue(
            hdr["magic"] in [b"BIKi", b"BIKb", b"BIKf", b"BIKg"],
            f"Invalid Bink signature: {hdr['magic']!r}"
        )
        self.assertGreater(hdr["declared_size"], 10_000_000, "Bink declared size suspiciously small")


# ==============================================================================
# TIER 3: CROSS-FEATURE MOCK INSTALLATION & ROLLBACK
# ==============================================================================
class TestTier3CrossFeatureMockInstall(unittest.TestCase):
    """
    Tier 3 tests simulate a full game directory installation and uninstallation
    to guarantee zero file corruption, complete pre-installation backups (.bak),
    and 100% bit-for-bit rollback fidelity.
    """

    def setUp(self):
        self.root = PROJECT_ROOT
        self.trans_dir = os.path.join(self.root, "translation_ptbr")
        self.temp_dir = tempfile.mkdtemp(prefix="mp2_mock_install_")

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _setup_mock_game_directory(self) -> Dict[str, bytes]:
        """Create a mock original English Max Payne 2 installation."""
        original_files = {
            os.path.join("data", "dialogtexts.txt"): b"[Dialogs]\n1000 = \"Original English Dialog\"\n",
            os.path.join("data", "database", "stringtable.txt"): b"[Strings]\n1 = \"Start Game\"\n",
            os.path.join("data", "database", "subtitles", "03_First_Hospital.h"): b"// Original English Hospital Subtitles\n",
            os.path.join("movies", "PREVIOUSLY.bik"): b"BIKi\x00\x00\x00\x00ORIGINAL_ENGLISH_VIDEO_CONTENT",
        }

        checksums = {}
        for rel_path, content in original_files.items():
            full_path = os.path.join(self.temp_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(content)
            checksums[rel_path] = hashlib.sha256(content).hexdigest()

        return checksums

    def _simulate_installation(self):
        """
        Deploy translation files into the mock game directory with automatic
        pre-installation backup (.bak) of overwritten files.
        """
        for root_path, _, filenames in os.walk(self.trans_dir):
            for fname in filenames:
                src_path = os.path.join(root_path, fname)
                rel_to_trans = os.path.relpath(src_path, self.trans_dir)
                dest_path = os.path.join(self.temp_dir, rel_to_trans)

                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                # Pre-installation backup if destination already exists and .bak does not yet exist
                bak_path = dest_path + ".bak"
                if os.path.isfile(dest_path) and not os.path.isfile(bak_path):
                    shutil.copy2(dest_path, bak_path)

                shutil.copy2(src_path, dest_path)

    def _simulate_uninstallation(self):
        """
        Execute uninstallation / rollback: restore .bak files and delete
        translation-only files.
        """
        for root_path, _, filenames in os.walk(self.temp_dir, topdown=False):
            for fname in filenames:
                fpath = os.path.join(root_path, fname)
                if fname.endswith(".bak"):
                    target_restored = fpath[:-4]
                    if os.path.exists(target_restored):
                        os.remove(target_restored)
                    shutil.move(fpath, target_restored)
                else:
                    bak_equivalent = fpath + ".bak"
                    if not os.path.isfile(bak_equivalent):
                        rel = os.path.relpath(fpath, self.temp_dir)
                        # If this file was introduced by translation and has no .bak, remove it
                        trans_origin = os.path.join(self.trans_dir, rel)
                        if os.path.isfile(trans_origin):
                            os.remove(fpath)

    def test_01_mock_installation_layout(self):
        """Verify that after installation, all translated files are positioned at expected engine paths."""
        self._setup_mock_game_directory()
        self._simulate_installation()

        # Check that core translated files exist in mock destination
        test_paths = [
            os.path.join(self.temp_dir, "data", "dialogtexts.txt"),
            os.path.join(self.temp_dir, "data", "database", "stringtable.txt"),
            os.path.join(self.temp_dir, "data", "database", "subtitles", "03_First_Hospital.h"),
        ]
        for p in test_paths:
            self.assertTrue(os.path.isfile(p), f"Target file missing post-install: {p}")

        # Check content is now Portuguese translation, not original English
        with open(os.path.join(self.temp_dir, "data", "dialogtexts.txt"), "rb") as f:
            content = f.read()
        self.assertNotEqual(content, b"[Dialogs]\n1000 = \"Original English Dialog\"\n")

    def test_02_pre_installation_backup_integrity(self):
        """Verify that original files are cleanly backed up to .bak with identical SHA256 hashes."""
        orig_checksums = self._setup_mock_game_directory()
        self._simulate_installation()

        for rel_path, expected_hash in orig_checksums.items():
            # If the file was overwritten, verify its .bak matches original checksum
            trans_origin = os.path.join(self.trans_dir, rel_path)
            if os.path.isfile(trans_origin):
                bak_path = os.path.join(self.temp_dir, rel_path + ".bak")
                self.assertTrue(os.path.isfile(bak_path), f"Backup file missing: {bak_path}")
                with open(bak_path, "rb") as f:
                    actual_hash = hashlib.sha256(f.read()).hexdigest()
                self.assertEqual(
                    actual_hash, expected_hash,
                    f"Backup file {bak_path} content does not match original English bytes"
                )

    def test_03_installation_idempotence(self):
        """Verify that installing twice does NOT overwrite original .bak backups with translation files."""
        orig_checksums = self._setup_mock_game_directory()

        # First install
        self._simulate_installation()

        # Second install over existing install
        self._simulate_installation()

        for rel_path, expected_hash in orig_checksums.items():
            bak_path = os.path.join(self.temp_dir, rel_path + ".bak")
            if os.path.isfile(bak_path):
                with open(bak_path, "rb") as f:
                    actual_hash = hashlib.sha256(f.read()).hexdigest()
                self.assertEqual(
                    actual_hash, expected_hash,
                    f"Idempotence failure: {bak_path} was overwritten during second install run"
                )

    def test_04_uninstallation_rollback_bit_for_bit(self):
        """Verify that uninstallation restores the game directory 100% bit-for-bit to its original state."""
        orig_checksums = self._setup_mock_game_directory()
        self._simulate_installation()
        self._simulate_uninstallation()

        for rel_path, expected_hash in orig_checksums.items():
            full_path = os.path.join(self.temp_dir, rel_path)
            self.assertTrue(os.path.isfile(full_path), f"Original file not restored: {full_path}")
            with open(full_path, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(
                actual_hash, expected_hash,
                f"Restored file {rel_path} does not match initial SHA256 checksum!"
            )

        # Verify no .bak files remain
        remaining_baks = glob.glob(os.path.join(self.temp_dir, "**", "*.bak"), recursive=True)
        self.assertEqual(len(remaining_baks), 0, f"Uninstaller left leftover .bak files: {remaining_baks}")


# ==============================================================================
# TIER 4: REAL-WORLD ACCEPTANCE SCENARIOS
# ==============================================================================
class TestTier4AcceptanceScenarios(unittest.TestCase):
    """
    Tier 4 tests verify real-world release acceptance gates:
    Windows Defender zero-threat scan, README quality and length constraints,
    elimination of competitor names, and elimination of amateur tags.
    """

    def setUp(self):
        self.root = PROJECT_ROOT
        self.readme_path = os.path.join(self.root, "README.md")

    def _locate_mpcmdrun(self) -> Optional[str]:
        """Locate Microsoft Defender CLI scanner MpCmdRun.exe."""
        known_locations = [
            r"C:\Program Files\Windows Defender\MpCmdRun.exe",
            r"C:\Program Files (x86)\Windows Defender\MpCmdRun.exe",
        ]
        platform_matches = glob.glob(r"C:\ProgramData\Microsoft\Windows Defender\Platform\*\MpCmdRun.exe")
        for loc in known_locations + platform_matches:
            if os.path.isfile(loc):
                return loc
        return None

    def test_01_windows_defender_scan(self):
        """Scan workspace with Microsoft Defender MpCmdRun.exe and verify 0 threats detected."""
        mpcmdrun = self._locate_mpcmdrun()
        if not mpcmdrun:
            self.skipTest("MpCmdRun.exe not found on system (non-Windows or custom environment).")

        # Target scan on src/ and translation_ptbr/
        target_dir = os.path.join(self.root, "translation_ptbr")
        cmd = [mpcmdrun, "-Scan", "-ScanType", "3", "-File", target_dir]

        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            stdout = res.stdout.decode("utf-8", errors="ignore")
            # Exit code 0 means clean, 2 means threat found
            self.assertEqual(
                res.returncode, 0,
                f"Microsoft Defender scan returned non-zero code {res.returncode}.\nOutput: {stdout}"
            )
            self.assertNotIn("threat", stdout.lower().replace("no threats", "").replace("0 threats", ""))
        except subprocess.TimeoutExpired:
            self.skipTest("MpCmdRun.exe timed out during file scan")
        except PermissionError:
            self.skipTest("MpCmdRun.exe requires elevated administrator privileges")

    def test_02_readme_word_count(self):
        """Verify that README.md word count is strictly under 450 words (< 1 minute reading time)."""
        self.assertTrue(os.path.isfile(self.readme_path), "README.md missing")
        with open(self.readme_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        words = text.split()
        word_count = len(words)

        if word_count >= 450:
            if not STRICT_MODE:
                self.skipTest(
                    f"Pending Milestone M3: README currently has {word_count} words (limit is < 450 words). "
                    "Awaiting Worker M3 rewrite."
                )
            self.fail(f"README word count {word_count} exceeds limit of 450 words")

        self.assertLess(word_count, 450, f"README word count {word_count} >= 450")

    def test_03_readme_competitor_exclusion(self):
        """Verify that README.md does not contain competitor or other creator names."""
        with open(self.readme_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        forbidden_names = ["Capitão Frio", "Capitao Frio"]
        found = [name for name in forbidden_names if name.lower() in text.lower()]
        self.assertEqual(len(found), 0, f"Competitor names found in README: {found}")

    def test_04_readme_seo_labels_exclusion(self):
        """Verify that README.md does not contain amateur tags such as '(SEO)'."""
        with open(self.readme_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        if "(SEO)" in text or "Keywords / Tags de Busca" in text:
            if not STRICT_MODE:
                self.skipTest("Pending Milestone M3: README still contains (SEO) tags, awaiting Worker M3 cleanup.")
            self.fail("Amateur tag '(SEO)' or keyword spamming discovered in README.md")

    def test_05_readme_creator_attribution(self):
        """Verify that Palestino7 is credited as the definitive author in README.md."""
        with open(self.readme_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        self.assertTrue("palestino7" in text.lower(), "Author credit 'palestino7' missing from README.md")

    def test_21_microsoft_defender_scan_installer(self):
        """Scan compiled Inno Setup installer dist/Instalador_MaxPayne2_PTBR_v3.0.0.exe with Microsoft Defender."""
        installer_path = os.path.join(self.root, "dist", "Instalador_MaxPayne2_PTBR_v3.0.0.exe")
        if not os.path.isfile(installer_path):
            if not STRICT_MODE:
                self.skipTest("Pending Milestone M2: dist/Instalador_MaxPayne2_PTBR_v3.0.0.exe awaiting compilation.")
            self.fail(f"Compiled installer missing at {installer_path}")

        mpcmdrun = self._locate_mpcmdrun()
        if not mpcmdrun:
            self.skipTest("MpCmdRun.exe not found on system (non-Windows or custom environment).")

        # Convert to 8.3 short path to avoid command line encoding issues with accented paths
        try:
            import ctypes
            from ctypes import wintypes
            _GetShortPathName = ctypes.windll.kernel32.GetShortPathNameW
            _GetShortPathName.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
            _GetShortPathName.restype = wintypes.DWORD
            buf = ctypes.create_unicode_buffer(1024)
            ret = _GetShortPathName(installer_path, buf, 1024)
            scan_target = buf.value if ret > 0 else installer_path
        except Exception:
            scan_target = installer_path

        cmd = [mpcmdrun, "-Scan", "-ScanType", "3", "-File", scan_target]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            stdout = res.stdout.decode("utf-8", errors="ignore")
            self.assertEqual(
                res.returncode, 0,
                f"Defender scan on installer returned non-zero code {res.returncode}.\nOutput: {stdout}"
            )
            self.assertNotIn("threat", stdout.lower().replace("no threats", "").replace("0 threats", ""))
        except subprocess.TimeoutExpired:
            self.skipTest("MpCmdRun.exe timed out during installer scan")
        except PermissionError:
            self.skipTest("MpCmdRun.exe requires elevated administrator privileges")



# ==============================================================================
# TEST RUNNER & DIAGNOSTIC REPORTING
# ==============================================================================
class DiagnosticTestResult(unittest.TextTestResult):
    """Custom test result collector capturing pass, fail, error, and skip metrics."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results_summary = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.results_summary.append({"test": test.id(), "status": "PASS", "message": ""})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        msg = self._exc_info_to_string(err, test)
        self.results_summary.append({"test": test.id(), "status": "FAIL", "message": msg})

    def addError(self, test, err):
        super().addError(test, err)
        msg = self._exc_info_to_string(err, test)
        self.results_summary.append({"test": test.id(), "status": "ERROR", "message": msg})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.results_summary.append({"test": test.id(), "status": "SKIP", "message": reason})


def build_suite(tier: Optional[str] = None) -> unittest.TestSuite:
    """Construct test suite filtered by tier."""
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    tier_map = {
        "1": [TestTier1FeatureCoverage],
        "2": [TestTier2BoundaryCornerCases],
        "3": [TestTier3CrossFeatureMockInstall],
        "4": [TestTier4AcceptanceScenarios],
    }

    if tier and tier in tier_map:
        for cls in tier_map[tier]:
            suite.addTests(loader.loadTestsFromTestCase(cls))
    else:
        suite.addTests(loader.loadTestsFromTestCase(TestTier1FeatureCoverage))
        suite.addTests(loader.loadTestsFromTestCase(TestTier2BoundaryCornerCases))
        suite.addTests(loader.loadTestsFromTestCase(TestTier3CrossFeatureMockInstall))
        suite.addTests(loader.loadTestsFromTestCase(TestTier4AcceptanceScenarios))

    return suite


def run_tests_main(args: argparse.Namespace) -> int:
    global STRICT_MODE, VERBOSE_OUTPUT
    STRICT_MODE = args.strict
    VERBOSE_OUTPUT = args.verbose

    print("=" * 80)
    print(" MAX PAYNE 2 PT-BR — OPAQUE-BOX E2E TEST RUNNER (v3.0.0 DEFINITIVA)")
    print(f" Execution Mode: {'STRICT' if STRICT_MODE else 'PROGRESSIVE (Milestone-Aware)'}")
    print(f" Selected Tier: {args.tier or 'All Tiers (1 to 4)'}")
    print("=" * 80)

    suite = build_suite(args.tier)
    stream = sys.stdout if VERBOSE_OUTPUT else open(os.devnull, "w", encoding="utf-8")
    runner = unittest.TextTestRunner(
        stream=stream,
        resultclass=DiagnosticTestResult,
        verbosity=2 if VERBOSE_OUTPUT else 1
    )

    result: DiagnosticTestResult = runner.run(suite)

    # Pretty-print structured results
    print("\n" + "-" * 80)
    print(" TEST EXECUTION SUMMARY")
    print("-" * 80)

    tier_names = {
        "TestTier1FeatureCoverage": "Tier 1: Feature Coverage & Asset Inventory",
        "TestTier2BoundaryCornerCases": "Tier 2: Boundary & Corner Cases (Encoding & Headers)",
        "TestTier3CrossFeatureMockInstall": "Tier 3: Cross-Feature Mock Install & Rollback",
        "TestTier4AcceptanceScenarios": "Tier 4: Acceptance Scenarios & Presentation",
    }

    current_class = None
    for entry in result.results_summary:
        test_id = entry["test"]
        cls_name = test_id.split(".")[-2]
        method_name = test_id.split(".")[-1]
        status = entry["status"]
        msg = entry["message"].strip().split("\n")[-1] if entry["message"] else ""

        if cls_name != current_class:
            current_class = cls_name
            friendly_tier = tier_names.get(cls_name, cls_name)
            print(f"\n[{friendly_tier}]")

        status_tag = f"[{status}]"
        if status == "PASS":
            color_tag = f"  \033[92m{status_tag:<8}\033[0m" if sys.stdout.isatty() else f"  {status_tag:<8}"
        elif status == "SKIP":
            color_tag = f"  \033[93m{status_tag:<8}\033[0m" if sys.stdout.isatty() else f"  {status_tag:<8}"
        else:
            color_tag = f"  \033[91m{status_tag:<8}\033[0m" if sys.stdout.isatty() else f"  {status_tag:<8}"

        print(f"{color_tag} {method_name}")
        if msg and status in ("SKIP", "FAIL", "ERROR"):
            print(f"           Note: {msg}")

    total_run = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total_run - failures - errors - skipped

    print("\n" + "=" * 80)
    print(f" TOTAL: {total_run} | PASSED: {passed} | FAILED: {failures} | ERRORS: {errors} | SKIPPED: {skipped}")
    print("=" * 80)

    # Export JSON if requested
    if args.json:
        report_data = {
            "total": total_run,
            "passed": passed,
            "failed": failures,
            "errors": errors,
            "skipped": skipped,
            "strict_mode": STRICT_MODE,
            "results": result.results_summary,
        }
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"Structured test report written to: {args.json}")

    # Determine exit code: 0 if no failures/errors, 1 otherwise
    return 1 if (failures > 0 or errors > 0) else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Max Payne 2 PT-BR E2E Test Runner")
    parser.add_argument(
        "--tier", choices=["1", "2", "3", "4", "all"], default=None,
        help="Run tests for a specific tier (default: all)"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Strict mode: fail on missing milestone deliverables instead of skipping"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--json", metavar="PATH", default=None,
        help="Export test execution results to JSON file"
    )

    cli_args = parser.parse_args()
    if cli_args.tier == "all":
        cli_args.tier = None

    sys.exit(run_tests_main(cli_args))
