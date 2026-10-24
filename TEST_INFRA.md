# Max Payne 2 PT-BR Translation — Test Infrastructure & Opaque-Box Methodology

## 1. Overview & Testing Philosophy

The test infrastructure for **Max Payne 2 PT-BR Translation (v3.0.0 Definitiva por Palestino7)** establishes an independent, automated, opaque-box verification suite. Because game localization involves heterogeneous asset pipelines—binary DirectX textures (DDS), Bink Video (BIK), Windows-1252 localized script and subtitle tables, Inno Setup deployment routines, and public documentation—our testing methodology validates behavior, integrity, and safety without relying on transient internal state.

### Quality Objectives
1. **Zero Text Corruption (100% Encoding Fidelity)**: Strict validation that all dialogue, strings, and subtitle files adhere to `Windows-1252` (`CP1252`), with zero UTF-8 multibyte artifacts (mojibake) and complete preservation of Portuguese accents (`ç, á, é, í, ó, ú, ã, õ, ê, ô, à`).
2. **Visual & Asset Integrity**: Exact asset accounting and format verification across all 138 Graphic Novel pages (4x SSAA DXT1), 29 loading screens, 32-bit uncompressed menu screens, high-resolution weapon HUD (1024x2048 DXT5), character introductions, and the `PREVIOUSLY.bik` recap cutscene.
3. **Safe Deployment & Rollback Fidelity**: Automated mock installation verifying that file placement, pre-installation backup (`.bak`), idempotence, and uninstallation restore the game directory to its pristine state bit-for-bit without data loss.
4. **Antivirus Cleanliness**: Certified automated scanning against Microsoft Defender (`MpCmdRun.exe`) ensuring zero heuristic false positives (`Trojan:Win32/Wacatac` or droppers).
5. **Release & Storefront Compliance**: Automated auditing of `README.md` and repository artifacts for conciseness (< 450 words), absence of competitor names, absence of amateur SEO tags, and proper author attribution.

---

## 2. The 4-Tier Test Architecture

```
+--------------------------------------------------------------------------+
|                        TIER 4: ACCEPTANCE SCENARIOS                      |
|  - Windows Defender CLI Scan (MpCmdRun.exe: 0 threats, exit code 0)     |
|  - README Word Count (< 450 words) & Professional Presentation           |
|  - Competitor Mention & Amateur Tag Elimination                          |
+--------------------------------------------------------------------------+
                                    ^
                                    |
+--------------------------------------------------------------------------+
|                  TIER 3: CROSS-FEATURE MOCK INSTALLATION                 |
|  - Simulated Game Directory Deployment & Target Path Verification        |
|  - Pre-Installation Backup (.bak) Verification                           |
|  - Idempotent Re-Installation Safeguard                                  |
|  - 100% Bit-for-Bit Rollback & Clean Uninstallation Restoration          |
+--------------------------------------------------------------------------+
                                    ^
                                    |
+--------------------------------------------------------------------------+
|                 TIER 2: BOUNDARY & CORNER CASE VALIDATION                |
|  - Windows-1252 Byte-Level Mapping (0x80-0xFF check, no invalid chars)  |
|  - Detection of UTF-8 Multibyte Sequences (\xc3\xa1, \xc3\xa9, BOM, etc) |
|  - MaxFX Subtitle Grammar, String Delimiters & Empty Line Auditing       |
|  - DDS Magic (0x20534444), Dimensions, MipMaps & Compression Formats     |
|  - Bink Video Container Magic (BIKi) & File Header Size Conformance      |
+--------------------------------------------------------------------------+
                                    ^
                                    |
+--------------------------------------------------------------------------+
|                   TIER 1: FEATURE COVERAGE & INVENTORY                   |
|  - 22 Subtitle Files (Including Restored Hospital Prologue & End)        |
|  - 138 Graphic Novel Textures (DXT1, 1024x512)                           |
|  - 29 Loading Screen Bitmaps (DXT1/RGB, 1024x512)                        |
|  - Menu DDS Files (Menu_Loading, Menu_Exiting, Menu_bg_Help: 1024x512)   |
|  - Weapon HUD (ActiveWeapons: 1024x2048 DXT5)                            |
|  - Character Cards (Mike, Winterson) & Video (PREVIOUSLY.bik)            |
|  - Localization Core (dialogtexts.txt, stringtable.txt, input.txt)       |
|  - Inno Setup Architecture (src/installer/setup.iss)                     |
|  - Showcase Visuals (banner_hero.png, loading_screens_comparison.png)    |
+--------------------------------------------------------------------------+
```

---

## 3. Tier Specifications & Authoritative Criteria

### Tier 1: Feature Coverage & Asset Inventory
*Authoritative Source: `ORIGINAL_REQUEST.md` § R1, § R2, § R3; `PROJECT.md` § Feature Inventory.*

| Asset / Feature | Expected Path | Authoritative Specification |
|-----------------|---------------|-----------------------------|
| Subtitles | `translation_ptbr/data/database/subtitles/*.h` | Exactly 22 files; `03_First_Hospital.h` must contain the 21 prologue lines; `22_End.h` present. |
| Graphic Novels | `translation_ptbr/data/database/graphicnovelpages/files/textures/*.dds` | Exactly 138 `.dds` files; 1024x512 resolution; 4x SSAA anti-aliased. |
| Loading Screens | `translation_ptbr/data/database/levels/bitmaps/*.dds` | Exactly 29 `.dds` files covering story chapters and Dead Man Walking levels. |
| Menu Textures | `translation_ptbr/data/menu/bitmaps/*.dds` | `Menu_Loading.dds`, `Menu_Exiting.dds`, `Menu_bg_Help.dds`; dimensions 1024x512. |
| Weapon HUD | `translation_ptbr/data/hud/bitmaps/ActiveWeapons.dds` | Dimensions 1024x2048; DXT5 compression format. |
| Character Cards | `translation_ptbr/data/hud/introductions/*.dds` | `Introduction_Mike.dds` and `Introduction_Winterson.dds`. |
| Recap Cutscene | `translation_ptbr/movies/PREVIOUSLY.bik` | BIK video file with PT-BR subtitles and English audio. |
| Installer Script | `src/installer/setup.iss` | Inno Setup 6.7.3 Unicode script with `BrazilianPortuguese.isl`. |
| Core Texts | `translation_ptbr/data/` | `dialogtexts.txt`, `input.txt`, `database/stringtable.txt`. |
| Visual Showcase | `docs/images/` | `banner_hero.png` (1280x360), `loading_screens_comparison.png`. |

---

### Tier 2: Boundary & Corner Cases
*Authoritative Source: MaxFX Engine Specifications, Windows-1252 Code Page Standard.*

#### 2.1. Byte-Level Windows-1252 Validation
The MaxFX engine reads strings in the local OEM/ANSI code page (`Windows-1252`). If a file is saved in UTF-8 or contains undefined byte codes, the engine renders corrupt characters (`?`, square glyphs, or crashes).
- **Rule**: Every byte in all `.txt` and `.h` files must strictly decode via `cp1252`.
- **Undefined byte check**: In Windows-1252, byte codes `0x81, 0x8D, 0x8F, 0x90, 0x9D` are undefined. Any occurrence is flagged as an immediate failure.
- **Accentuation density**: Verifies that actual accented characters (`0xC0-0xFF` excluding `0xD7` and `0xF7`) exist in expected high volumes (> 3,000 across core files), proving that text was not silently stripped to 7-bit ASCII.

#### 2.2. UTF-8 Multibyte Mojibake Elimination
A common defect in Brazilian Portuguese translations occurs when a UTF-8 file is read as Windows-1252, producing double-byte sequences:
- `\xc3\xa1` (á) displayed as `Ã¡`
- `\xc3\xa9` (é) displayed as `Ã©`
- `\xc3\xa3` (ã) displayed as `Ã£`
- `\xc3\xa7` (ç) displayed as `Ã§`
- `\xc3\xb5` (õ) displayed as `Ãµ`
- `\xef\xbf\xbd` (Unicode replacement character ``)
- **Rule**: Scan all text bytes for `0xC3` followed by `0x80-0xBF` or UTF-8 byte order marks (`0xEF 0xBB 0xBF`). Count must be exactly 0.

#### 2.3. MaxFX Subtitle Grammar Integrity
- Subtitle entries must follow the syntax: `[Key]\t\tString = "Localized line";`.
- Empty strings `String = "";` or strings consisting solely of whitespace are flagged to prevent silent dead audio cues in-game.
- Unbalanced string delimiters (missing closing `"`) are flagged.

#### 2.4. DDS Binary Header Validation
- Must start with Magic `b'DDS '` (`0x20534444`).
- Header size at offset 4 must be 124 (`0x7C000000`).
- PixelFormat size at offset 76 must be 32 (`0x20000000`).
- Formats:
  - Graphic Novel pages: DXT1 FourCC (`b'DXT1'`).
  - ActiveWeapons: DXT5 FourCC (`b'DXT5'`).
  - Menu screens: 32-bit uncompressed RGBA (`rgb_bits == 32`).

#### 2.5. Bink Video (BIK) Container Validation
- Must start with valid Bink signature (`b'BIKi'`, `b'BIKb'`, `b'BIKf'`, `b'BIKg'`).
- Declared file size in header bytes 4..7 must correspond to actual payload size.

---

### Tier 3: Cross-Feature Mock Installation & Rollback
*Authoritative Source: `ORIGINAL_REQUEST.md` § R2; `PROJECT.md` § Feature 11.*

The installer must be 100% reversible and safe, leaving no orphan files or corrupting existing game files upon uninstallation.

#### Test Execution Protocol:
1. **Initialize Sandbox**: Spin up an isolated temporary directory simulating a fresh English Max Payne 2 retail or Steam installation (containing original `dialogtexts.txt`, `stringtable.txt`, subtitles, and video).
2. **Execute Deployment**: Deploy the translation files into the mock directory.
3. **Assert File Structure**: Verify that all localized files reside at the exact paths expected by `MaxPayne2.exe`.
4. **Assert Pre-Installation Backups**: Verify that for every overwritten file, a corresponding `.bak` copy exists, containing the exact original English bytes.
5. **Assert Idempotence**: Re-run the installation routine over the already-installed directory. Verify that the `.bak` files are NOT overwritten by the translation files.
6. **Execute Rollback / Uninstallation**: Trigger the rollback procedure.
7. **Assert Bit-for-Bit State**:
   - Every original file restored from `.bak` must match its initial SHA256 checksum 100%.
   - All newly introduced translation files (textures, additional subtitles, videos) must be cleanly removed.
   - The directory tree returns to its pristine state.

---

### Tier 4: Real-World Acceptance Scenarios
*Authoritative Source: `ORIGINAL_REQUEST.md` § R2, § R3, § Acceptance Criteria.*

#### 4.1. Antivirus Zero-Detection Scan (Microsoft Defender CLI)
- **Engine**: `C:\Program Files\Windows Defender\MpCmdRun.exe` or dynamic platform path.
- **Scan Command**: `MpCmdRun.exe -Scan -ScanType 3 -File <TargetDirectoryOrBinary>`
- **Pass Criteria**: Exit Code 0 (or clean scan exit code), 0 threats detected, 0 detections of `Trojan:Win32/Wacatac` or dropper heuristics.

#### 4.2. README & Documentation Presentation
- **Word Count**: Must be strictly under 450 words to ensure rapid readability (< 1 minute).
- **Competitor Filter**: Must contain zero occurrences of competitor or other creator names (e.g. `Capitão Frio`, `Capitao Frio`).
- **Amateur Label Filter**: Must contain zero occurrences of `(SEO)` or amateur keyword spam tags.
- **Creator Certification**: Must explicitly credit `Palestino7` as the definitive author.
- **Clarity**: Must include clear installation instructions for Steam, GOG, and Retail editions.

---

## 4. Test Runner Usage & Commands

The unified test harness is located at `tests/run_e2e_tests.py`. It requires only Python 3 standard library and works natively on Windows, Linux, and macOS.

### Standard Test Execution
```bash
# Run all 4 tiers in progressive mode (reports status of all implemented and pending features)
python tests/run_e2e_tests.py

# Run with verbose diagnostic output
python tests/run_e2e_tests.py --verbose

# Run a specific tier
python tests/run_e2e_tests.py --tier 1
python tests/run_e2e_tests.py --tier 2
python tests/run_e2e_tests.py --tier 3
python tests/run_e2e_tests.py --tier 4

# Run in strict mode (fails if any planned deliverable is missing)
python tests/run_e2e_tests.py --strict

# Export test results to structured JSON
python tests/run_e2e_tests.py --json test_results.json
```

### Pytest Compatibility
The test suite is structured to also execute seamlessly under `pytest`:
```bash
pytest tests/ -v
```

---

## 5. Exit Codes & CI/CD Integration

| Exit Code | Meaning | Action Required |
|-----------|---------|-----------------|
| `0` | All operational tests passed successfully (or pending milestone tasks cleanly identified). | Ready for build / release. |
| `1` | One or more tests failed (e.g., corrupted encoding, invalid DDS magic, rollback failure). | Review diagnostic output, escalate defect to responsible milestone agent. |
| `2` | Environment configuration error (e.g. missing python interpreter or unreadable root directory). | Check file permissions and paths. |

---

## 6. Defect Escalation Matrix

If a test in `tests/run_e2e_tests.py` fails, consult this matrix to identify the responsible agent:

| Failing Test | Category | Responsible Agent / Milestone |
|--------------|----------|-------------------------------|
| `test_encoding_cp1252`, `test_no_utf8_mojibake` | Text Corruption | Worker M1 (Asset & Text Fusion) |
| `test_dds_headers`, `test_asset_counts` | Asset Formatting | Worker M1 (Asset & Text Fusion) |
| `test_previously_bik` | Video Container | Worker M1 (Asset & Text Fusion) |
| `test_mock_installation`, `test_rollback_fidelity` | Deployment & Backup | Worker M2 (Inno Setup Architecture) |
| `test_defender_scan` | Antivirus False Positives | Worker M2 (Inno Setup Architecture) |
| `test_readme_word_count`, `test_readme_no_competitor` | Presentation & Documentation | Worker M3 (Visual Redesign & README) |
| `test_banner_hero_dimensions`, `test_comparison_graphic` | Visual Assets | Worker M3 (Visual Redesign & README) |
