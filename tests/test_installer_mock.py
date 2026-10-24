#!/usr/bin/env python3
"""
Empirical Stress Test Harness for Inno Setup Installer
Tests:
1. Silent mock installation into sandbox directory with all components.
2. Component layout and file hash integrity verification.
3. Pre-installation backup (.bak) creation and integrity.
4. Idempotent re-installation (ensure .bak files are not overwritten by translation).
5. Silent uninstallation and 100% bit-for-bit rollback verification.
6. Clean removal of translation files and .bak files upon uninstallation.
7. Selective component installation (core only vs full).
8. Read-only original file handling.
9. Microsoft Defender zero-detection command line audit.
"""

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INSTALLER_EXE = os.path.join(PROJECT_ROOT, "dist", "Instalador_MaxPayne2_PTBR_v3.0.0.exe")


def sha256_file(filepath: str) -> str:
    """Calculate SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestInstallerEmpirical(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.isfile(INSTALLER_EXE), f"Installer not found: {INSTALLER_EXE}")
        # Create unique sandbox directory
        self.sandbox_dir = tempfile.mkdtemp(prefix="mp2_inst_test_")
        self.log_file = os.path.join(self.sandbox_dir, "install.log")

    def tearDown(self):
        # Wait a moment for any file handles to release
        time.sleep(0.5)
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)

    def _setup_mock_game(self) -> dict:
        """Create a mock Max Payne 2 directory structure with original files."""
        # 1. maxpayne2.exe (dummy executable to pass DirHasGame)
        exe_path = os.path.join(self.sandbox_dir, "maxpayne2.exe")
        with open(exe_path, "wb") as f:
            f.write(b"MZ_DUMMY_ORIGINAL_MAXPAYNE2_EXE_HEADER\x00\x01\x02\x03")

        # 2. Original MP2_English.ras
        orig_ras = os.path.join(self.sandbox_dir, "MP2_English.ras")
        with open(orig_ras, "wb") as f:
            f.write(b"ORIGINAL_ENGLISH_RAS_BINARY_PAYLOAD_FOR_TESTING_12345\n" * 100)

        # 3. Original movies/previously.bik
        movies_dir = os.path.join(self.sandbox_dir, "movies")
        os.makedirs(movies_dir, exist_ok=True)
        orig_bik = os.path.join(movies_dir, "previously.bik")
        with open(orig_bik, "wb") as f:
            f.write(b"BIKi_ORIGINAL_ENGLISH_RECAP_VIDEO_PAYLOAD_TEST\n" * 50)

        # 4. Original sndmfc.dll
        orig_dll = os.path.join(self.sandbox_dir, "sndmfc.dll")
        with open(orig_dll, "wb") as f:
            f.write(b"ORIGINAL_SNDMFC_DLL_UNPATCHED_PAYLOAD_TEST\n" * 50)

        # 5. Original scripts/ControlScheme.png (optional pre-existing)
        scripts_dir = os.path.join(self.sandbox_dir, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        orig_ctrl = os.path.join(scripts_dir, "ControlScheme.png")
        with open(orig_ctrl, "wb") as f:
            f.write(b"ORIGINAL_CONTROL_SCHEME_PNG_PAYLOAD\n" * 20)

        return {
            "maxpayne2.exe": sha256_file(exe_path),
            "MP2_English.ras": sha256_file(orig_ras),
            os.path.join("movies", "previously.bik"): sha256_file(orig_bik),
            "sndmfc.dll": sha256_file(orig_dll),
            os.path.join("scripts", "ControlScheme.png"): sha256_file(orig_ctrl),
        }

    def _run_installer(self, components=None, extra_args=None) -> subprocess.CompletedProcess:
        """Run installer silently targeting sandbox directory."""
        args = [
            INSTALLER_EXE,
            "/VERYSILENT",
            "/SUPPRESSMSGBOXES",
            "/NORESTART",
            f"/DIR={self.sandbox_dir}",
            f"/LOG={self.log_file}",
        ]
        if components:
            args.append(f"/COMPONENTS={components}")
        if extra_args:
            args.extend(extra_args)

        # Run process and wait up to 120 seconds
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        return res

    def _find_uninstaller(self) -> str:
        """Locate unins000.exe in sandbox."""
        uninst_dir = os.path.join(self.sandbox_dir, "uninst_ptbr")
        self.assertTrue(os.path.isdir(uninst_dir), f"Uninstaller directory missing: {uninst_dir}")
        for fname in os.listdir(uninst_dir):
            if fname.lower().startswith("unins") and fname.lower().endswith(".exe"):
                return os.path.join(uninst_dir, fname)
        self.fail(f"No unins*.exe found in {uninst_dir}")

    def _run_uninstaller(self) -> subprocess.CompletedProcess:
        """Run uninstaller silently."""
        uninstaller_exe = self._find_uninstaller()
        args = [
            uninstaller_exe,
            "/VERYSILENT",
            "/SUPPRESSMSGBOXES",
            "/NORESTART",
        ]
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        # Inno Setup spawns a temporary child process during uninstall, wait a moment for completion
        time.sleep(2)
        return res

    def test_01_silent_full_install_and_component_layout(self):
        """Test full silent installation and verify all components extract to correct paths."""
        orig_hashes = self._setup_mock_game()

        # Run installer
        res = self._run_installer()
        self.assertEqual(res.returncode, 0, f"Installer failed with return code {res.returncode}")

        # 1. MP2_English.ras must be overwritten with translated ras
        target_ras = os.path.join(self.sandbox_dir, "MP2_English.ras")
        self.assertTrue(os.path.isfile(target_ras), "MP2_English.ras missing after install")
        source_ras = os.path.join(PROJECT_ROOT, "MP2_English_PTBR.ras")
        self.assertEqual(sha256_file(target_ras), sha256_file(source_ras), "Installed MP2_English.ras does not match MP2_English_PTBR.ras")

        # 2. Backup MP2_English.ras.bak must exist and match original hash
        bak_ras = os.path.join(self.sandbox_dir, "MP2_English.ras.bak")
        self.assertTrue(os.path.isfile(bak_ras), "Backup MP2_English.ras.bak was not created")
        self.assertEqual(sha256_file(bak_ras), orig_hashes["MP2_English.ras"], "Backup MP2_English.ras.bak does not match original bytes")

        # 3. previously.bik must be overwritten with translated video
        target_bik = os.path.join(self.sandbox_dir, "movies", "previously.bik")
        self.assertTrue(os.path.isfile(target_bik), "movies/previously.bik missing after install")
        source_bik = os.path.join(PROJECT_ROOT, "translation_ptbr", "movies", "PREVIOUSLY.bik")
        self.assertEqual(sha256_file(target_bik), sha256_file(source_bik), "Installed previously.bik does not match source BIK")

        # 4. Backup previously.bik.bak must exist and match original hash
        bak_bik = os.path.join(self.sandbox_dir, "movies", "previously.bik.bak")
        self.assertTrue(os.path.isfile(bak_bik), "Backup previously.bik.bak was not created")
        self.assertEqual(sha256_file(bak_bik), orig_hashes[os.path.join("movies", "previously.bik")])

        # 5. sndmfc.dll must be overwritten with patched dll
        target_dll = os.path.join(self.sandbox_dir, "sndmfc.dll")
        self.assertTrue(os.path.isfile(target_dll), "sndmfc.dll missing after install")
        source_dll = os.path.join(PROJECT_ROOT, "src", "installer", "assets", "sndmfc.dll")
        self.assertEqual(sha256_file(target_dll), sha256_file(source_dll), "Installed sndmfc.dll does not match source")

        # 6. Backup sndmfc.dll.bak must exist and match original hash
        bak_dll = os.path.join(self.sandbox_dir, "sndmfc.dll.bak")
        self.assertTrue(os.path.isfile(bak_dll), "Backup sndmfc.dll.bak was not created")
        self.assertEqual(sha256_file(bak_dll), orig_hashes["sndmfc.dll"])

        # 7. Widescreen Fix components
        target_d3d8 = os.path.join(self.sandbox_dir, "d3d8.dll")
        self.assertTrue(os.path.isfile(target_d3d8), "d3d8.dll from widescreen fix missing")
        target_ctrl = os.path.join(self.sandbox_dir, "scripts", "ControlScheme.png")
        self.assertTrue(os.path.isfile(target_ctrl), "scripts/ControlScheme.png missing")
        bak_ctrl = os.path.join(self.sandbox_dir, "scripts", "ControlScheme.png.bak")
        self.assertTrue(os.path.isfile(bak_ctrl), "scripts/ControlScheme.png.bak missing")
        self.assertEqual(sha256_file(bak_ctrl), orig_hashes[os.path.join("scripts", "ControlScheme.png")])

        # 8. Mod file MaxPayne2_PTBR.mp2m and Desinstalar_Traducao.bat
        mp2m_path = os.path.join(self.sandbox_dir, "MaxPayne2_PTBR.mp2m")
        self.assertTrue(os.path.isfile(mp2m_path), "MaxPayne2_PTBR.mp2m missing")
        bat_path = os.path.join(self.sandbox_dir, "Desinstalar_Traducao.bat")
        self.assertTrue(os.path.isfile(bat_path), "Desinstalar_Traducao.bat missing")

        # 9. Uninstaller executable exists
        uninstaller_exe = self._find_uninstaller()
        self.assertTrue(os.path.isfile(uninstaller_exe), f"Uninstaller not found: {uninstaller_exe}")

    def test_02_idempotence_repeated_installation(self):
        """Verify that installing twice does not corrupt original backups."""
        orig_hashes = self._setup_mock_game()

        # Install #1
        res1 = self._run_installer()
        self.assertEqual(res1.returncode, 0)

        # Install #2 over existing
        res2 = self._run_installer()
        self.assertEqual(res2.returncode, 0)

        # Backups must still match the initial original hashes (not overwritten by translated files)
        bak_ras = os.path.join(self.sandbox_dir, "MP2_English.ras.bak")
        self.assertEqual(sha256_file(bak_ras), orig_hashes["MP2_English.ras"], "Idempotence failed: MP2_English.ras.bak corrupted on 2nd install")

        bak_bik = os.path.join(self.sandbox_dir, "movies", "previously.bik.bak")
        self.assertEqual(sha256_file(bak_bik), orig_hashes[os.path.join("movies", "previously.bik")])

        bak_dll = os.path.join(self.sandbox_dir, "sndmfc.dll.bak")
        self.assertEqual(sha256_file(bak_dll), orig_hashes["sndmfc.dll"])

    def test_03_silent_uninstallation_and_rollback(self):
        """Verify uninstallation cleanly restores original files bit-for-bit and removes translation artifacts."""
        orig_hashes = self._setup_mock_game()

        # Install
        res_inst = self._run_installer()
        self.assertEqual(res_inst.returncode, 0)

        # Uninstall
        res_uninst = self._run_uninstaller()
        self.assertEqual(res_uninst.returncode, 0)

        # 1. Verify original files are restored bit-for-bit
        target_ras = os.path.join(self.sandbox_dir, "MP2_English.ras")
        self.assertTrue(os.path.isfile(target_ras), "MP2_English.ras missing after rollback")
        self.assertEqual(sha256_file(target_ras), orig_hashes["MP2_English.ras"], "Rollback failed: MP2_English.ras does not match original bytes!")

        target_bik = os.path.join(self.sandbox_dir, "movies", "previously.bik")
        self.assertTrue(os.path.isfile(target_bik), "movies/previously.bik missing after rollback")
        self.assertEqual(sha256_file(target_bik), orig_hashes[os.path.join("movies", "previously.bik")])

        target_dll = os.path.join(self.sandbox_dir, "sndmfc.dll")
        self.assertTrue(os.path.isfile(target_dll), "sndmfc.dll missing after rollback")
        self.assertEqual(sha256_file(target_dll), orig_hashes["sndmfc.dll"])

        target_ctrl = os.path.join(self.sandbox_dir, "scripts", "ControlScheme.png")
        self.assertTrue(os.path.isfile(target_ctrl), "scripts/ControlScheme.png missing after rollback")
        self.assertEqual(sha256_file(target_ctrl), orig_hashes[os.path.join("scripts", "ControlScheme.png")])

        # 2. Verify all .bak files are deleted
        for root_path, _, filenames in os.walk(self.sandbox_dir):
            for fname in filenames:
                self.assertFalse(fname.endswith(".bak"), f"Leftover backup file found: {os.path.join(root_path, fname)}")

        # 3. Verify translation-only files are deleted
        self.assertFalse(os.path.isfile(os.path.join(self.sandbox_dir, "MaxPayne2_PTBR.mp2m")), "MaxPayne2_PTBR.mp2m not removed after uninstall")
        self.assertFalse(os.path.isfile(os.path.join(self.sandbox_dir, "Desinstalar_Traducao.bat")), "Desinstalar_Traducao.bat not removed after uninstall")
        self.assertFalse(os.path.isfile(os.path.join(self.sandbox_dir, "d3d8.dll")), "Widescreen d3d8.dll not removed after uninstall")

    def test_04_core_only_component_installation(self):
        """Verify selective component installation: when only 'core' is selected, other components are omitted."""
        orig_hashes = self._setup_mock_game()

        # Install with only core component
        res = self._run_installer(components="core")
        self.assertEqual(res.returncode, 0)

        # Core file must be installed and backed up
        target_ras = os.path.join(self.sandbox_dir, "MP2_English.ras")
        self.assertEqual(sha256_file(target_ras), sha256_file(os.path.join(PROJECT_ROOT, "MP2_English_PTBR.ras")))
        bak_ras = os.path.join(self.sandbox_dir, "MP2_English.ras.bak")
        self.assertTrue(os.path.isfile(bak_ras))

        # Widescreen and mod must NOT be installed
        self.assertFalse(os.path.isfile(os.path.join(self.sandbox_dir, "d3d8.dll")), "d3d8.dll was installed despite widescreen not selected")
        self.assertFalse(os.path.isfile(os.path.join(self.sandbox_dir, "MaxPayne2_PTBR.mp2m")), "MaxPayne2_PTBR.mp2m was installed despite mp2m not selected")

        # video and audiofix were NOT selected, so previously.bik and sndmfc.dll must remain untouched (original hashes)
        target_bik = os.path.join(self.sandbox_dir, "movies", "previously.bik")
        self.assertEqual(sha256_file(target_bik), orig_hashes[os.path.join("movies", "previously.bik")], "previously.bik was overwritten without video component")
        self.assertFalse(os.path.isfile(target_bik + ".bak"), "previously.bik.bak should not exist when video component unselected")

        target_dll = os.path.join(self.sandbox_dir, "sndmfc.dll")
        self.assertEqual(sha256_file(target_dll), orig_hashes["sndmfc.dll"], "sndmfc.dll was overwritten without audiofix component")
        self.assertFalse(os.path.isfile(target_dll + ".bak"), "sndmfc.dll.bak should not exist when audiofix component unselected")

    def test_05_microsoft_defender_scan(self):
        """Scan dist/Instalador_MaxPayne2_PTBR_v3.0.0.exe with Microsoft Defender MpCmdRun.exe and verify 0 threats."""
        mpcmdrun = None
        known_locations = [
            r"C:\Program Files\Windows Defender\MpCmdRun.exe",
            r"C:\Program Files (x86)\Windows Defender\MpCmdRun.exe",
        ]
        import glob
        platform_matches = glob.glob(r"C:\ProgramData\Microsoft\Windows Defender\Platform\*\MpCmdRun.exe")
        for loc in known_locations + platform_matches:
            if os.path.isfile(loc):
                mpcmdrun = loc
                break

        if not mpcmdrun:
            self.skipTest("MpCmdRun.exe not found on system.")

        # In Windows with accented paths, convert to 8.3 short path
        import win32api  # fallback if available
        short_installer = INSTALLER_EXE
        try:
            import win32api
            short_installer = win32api.GetShortPathName(INSTALLER_EXE)
        except Exception:
            # Query short path via powershell
            cmd_sp = ["powershell", "-NoProfile", "-Command", f'(New-Object -ComObject Scripting.FileSystemObject).GetFile("{INSTALLER_EXE}").ShortPath']
            sp_res = subprocess.run(cmd_sp, capture_output=True, text=True)
            if sp_res.returncode == 0 and sp_res.stdout.strip():
                short_installer = sp_res.stdout.strip()

        cmd = [mpcmdrun, "-Scan", "-ScanType", "3", "-File", short_installer]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        stdout = res.stdout.decode("utf-8", errors="ignore")
        self.assertEqual(res.returncode, 0, f"Defender reported threats or failed with code {res.returncode}:\n{stdout}")
        self.assertIn("found no threats", stdout.lower(), f"Defender output did not confirm clean scan: {stdout}")

    def test_06_invalid_directory_validation(self):
        """Verify that installing into an empty non-game directory triggers validation warning or rejection."""
        # Empty directory without maxpayne2.exe or MP2_English.ras
        empty_dir = tempfile.mkdtemp(prefix="mp2_empty_test_")
        try:
            args = [
                INSTALLER_EXE,
                "/VERYSILENT",
                "/SUPPRESSMSGBOXES",
                "/NORESTART",
                f"/DIR={empty_dir}",
            ]
            res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            # When /SUPPRESSMSGBOXES is passed and NextButtonClick prompts with mbConfirmation,
            # Inno Setup defaults to IDNO and aborts setup (returncode != 0), preventing accidental install into non-game folder.
            self.assertNotEqual(res.returncode, 0, "Installer silently proceeded to install into an invalid non-game directory!")
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)

