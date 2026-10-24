using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Win32;

[assembly: AssemblyTitle("Instalador da Tradução Completa Max Payne 2 PT-BR")]
[assembly: AssemblyDescription("Tradução 100% Completa para Max Payne 2: The Fall of Max Payne (Legendas, Menus, Graphic Novels, Telas de Carregamento, HUD e Widescreen Fix)")]
[assembly: AssemblyConfiguration("Release")]
[assembly: AssemblyCompany("palestino7")]
[assembly: AssemblyProduct("Max Payne 2 Tradução Completa PT-BR - por palestino7")]
[assembly: AssemblyCopyright("Copyright © 2026 palestino7")]
[assembly: AssemblyTrademark("palestino7")]
[assembly: AssemblyVersion("2.0.0.0")]
[assembly: AssemblyFileVersion("2.0.0.0")]

namespace MaxPayne2TraducaoPTBR
{
    public class InstallerForm : Form
    {
        private TextBox txtGamePath;
        private Button btnBrowse;
        private Label lblDetectionStatus;
        private CheckBox chkCoreTranslation;
        private CheckBox chkSndMfcPatch;
        private CheckBox chkWidescreenFix;
        private CheckBox chkInstallMp2m;
        private ProgressBar progressBar;
        private TextBox txtLog;
        private Button btnInstall;
        private Button btnUninstall;

        public InstallerForm()
        {
            InitializeComponent();
            AutoDetectGameFolder();
        }

        private void InitializeComponent()
        {
            this.Text = "Max Payne 2 — Tradução Completa PT-BR (por palestino7)";
            this.ClientSize = new Size(680, 575);
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(18, 18, 22);
            this.ForeColor = Color.FromArgb(230, 230, 230);
            this.Font = new Font("Segoe UI", 9.25f, FontStyle.Regular);

            try
            {
                this.Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            }
            catch { }

            // 1. Header Banner
            PictureBox picBanner = new PictureBox
            {
                Location = new Point(0, 0),
                Size = new Size(680, 115),
                SizeMode = PictureBoxSizeMode.StretchImage
            };
            using (Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream("Banner.png"))
            {
                if (s != null)
                    picBanner.Image = Image.FromStream(s);
            }
            this.Controls.Add(picBanner);

            // 2. Game Directory Selection
            GroupBox grpPath = new GroupBox
            {
                Text = " Pasta de Instalação do Max Payne 2 ",
                Location = new Point(16, 125),
                Size = new Size(648, 82),
                ForeColor = Color.FromArgb(220, 75, 65),
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold)
            };

            txtGamePath = new TextBox
            {
                Location = new Point(14, 26),
                Size = new Size(510, 25),
                BackColor = Color.FromArgb(30, 30, 36),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Font = new Font("Segoe UI", 9.5f, FontStyle.Regular)
            };
            txtGamePath.TextChanged += (s, e) => ValidateSelectedPath();

            btnBrowse = new Button
            {
                Text = "Procurar...",
                Location = new Point(532, 24),
                Size = new Size(102, 28),
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(45, 45, 52),
                ForeColor = Color.White,
                Font = new Font("Segoe UI", 9f, FontStyle.Bold),
                Cursor = Cursors.Hand
            };
            btnBrowse.FlatAppearance.BorderColor = Color.FromArgb(90, 90, 100);
            btnBrowse.Click += BtnBrowse_Click;

            lblDetectionStatus = new Label
            {
                Location = new Point(14, 56),
                Size = new Size(620, 20),
                ForeColor = Color.FromArgb(170, 170, 180),
                Font = new Font("Segoe UI", 8.5f, FontStyle.Regular),
                Text = "Verificando instalação..."
            };

            grpPath.Controls.Add(txtGamePath);
            grpPath.Controls.Add(btnBrowse);
            grpPath.Controls.Add(lblDetectionStatus);
            this.Controls.Add(grpPath);

            // 3. Components GroupBox
            GroupBox grpOptions = new GroupBox
            {
                Text = " Componentes da Tradução e Melhorias ",
                Location = new Point(16, 215),
                Size = new Size(648, 128),
                ForeColor = Color.FromArgb(220, 75, 65),
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold)
            };

            chkCoreTranslation = new CheckBox
            {
                Text = "Tradução 100% Completa PT-BR (Legendas, Menus, 138 Páginas de Graphic Novel, Loading Screens e HUD)",
                Location = new Point(14, 24),
                Size = new Size(625, 22),
                Checked = true,
                AutoCheck = false,
                ForeColor = Color.White,
                Font = new Font("Segoe UI", 9f, FontStyle.Bold)
            };

            chkSndMfcPatch = new CheckBox
            {
                Text = "Correção de Engine de Áudio/Legendas (sndmfc.dll — exibe legendas mesmo com o volume em 0)",
                Location = new Point(14, 49),
                Size = new Size(625, 22),
                Checked = true,
                ForeColor = Color.FromArgb(230, 230, 235),
                Font = new Font("Segoe UI", 9f, FontStyle.Regular)
            };

            chkWidescreenFix = new CheckBox
            {
                Text = "Widescreen Fix + Compatibilidade Windows 10/11 + Esquema de Controle Xbox em PT-BR (Recomendado)",
                Location = new Point(14, 74),
                Size = new Size(625, 22),
                Checked = true,
                ForeColor = Color.FromArgb(230, 230, 235),
                Font = new Font("Segoe UI", 9f, FontStyle.Regular)
            };

            chkInstallMp2m = new CheckBox
            {
                Text = "Instalar também pacote Mod opcional (MaxPayne2_PTBR.mp2m) para o seletor de mods",
                Location = new Point(14, 99),
                Size = new Size(625, 22),
                Checked = true,
                ForeColor = Color.FromArgb(230, 230, 235),
                Font = new Font("Segoe UI", 9f, FontStyle.Regular)
            };

            grpOptions.Controls.Add(chkCoreTranslation);
            grpOptions.Controls.Add(chkSndMfcPatch);
            grpOptions.Controls.Add(chkWidescreenFix);
            grpOptions.Controls.Add(chkInstallMp2m);
            this.Controls.Add(grpOptions);

            // 4. Progress & Log
            progressBar = new ProgressBar
            {
                Location = new Point(16, 352),
                Size = new Size(648, 20),
                Minimum = 0,
                Maximum = 100,
                Value = 0,
                Style = ProgressBarStyle.Continuous
            };
            this.Controls.Add(progressBar);

            txtLog = new TextBox
            {
                Location = new Point(16, 380),
                Size = new Size(648, 118),
                BackColor = Color.FromArgb(12, 12, 15),
                ForeColor = Color.FromArgb(180, 230, 185),
                BorderStyle = BorderStyle.FixedSingle,
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                ReadOnly = true,
                Font = new Font("Consolas", 8.75f, FontStyle.Regular)
            };
            this.Controls.Add(txtLog);

            // 5. Action Buttons
            btnInstall = new Button
            {
                Text = "INSTALAR TRADUÇÃO COMPLETA",
                Location = new Point(16, 508),
                Size = new Size(415, 40),
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(185, 35, 30),
                ForeColor = Color.White,
                Font = new Font("Segoe UI", 10.5f, FontStyle.Bold),
                Cursor = Cursors.Hand
            };
            btnInstall.FlatAppearance.BorderColor = Color.FromArgb(225, 65, 55);
            btnInstall.Click += BtnInstall_Click;
            this.Controls.Add(btnInstall);

            btnUninstall = new Button
            {
                Text = "RESTAURAR ORIGINAL",
                Location = new Point(442, 508),
                Size = new Size(222, 40),
                FlatStyle = FlatStyle.Flat,
                BackColor = Color.FromArgb(42, 42, 48),
                ForeColor = Color.FromArgb(220, 220, 225),
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold),
                Cursor = Cursors.Hand
            };
            btnUninstall.FlatAppearance.BorderColor = Color.FromArgb(85, 85, 95);
            btnUninstall.Click += BtnUninstall_Click;
            this.Controls.Add(btnUninstall);

            Label lblFooter = new Label
            {
                Text = "Desenvolvido e assinado por palestino7  •  Compatível com Steam, GOG, Rockstar Launcher e Retail CD/DVD",
                Location = new Point(16, 553),
                Size = new Size(648, 18),
                TextAlign = ContentAlignment.MiddleCenter,
                ForeColor = Color.FromArgb(130, 130, 140),
                Font = new Font("Segoe UI", 8f, FontStyle.Regular)
            };
            this.Controls.Add(lblFooter);

            Log("Bem-vindo ao Instalador da Tradução Completa PT-BR de Max Payne 2 (por palestino7).");
            Log("Esta tradução traduz 100% dos diálogos, programas de TV, menus, 138 páginas de Graphic Novel, telas de carregamento e HUD.");
        }

        private void Log(string msg)
        {
            if (txtLog.InvokeRequired)
            {
                txtLog.Invoke(new Action<string>(Log), msg);
                return;
            }
            string ts = DateTime.Now.ToString("HH:mm:ss");
            txtLog.AppendText("[" + ts + "] " + msg + Environment.NewLine);
            txtLog.ScrollToCaret();
        }

        private void SetProgress(int val)
        {
            if (progressBar.InvokeRequired)
            {
                progressBar.Invoke(new Action<int>(SetProgress), val);
                return;
            }
            progressBar.Value = Math.Max(0, Math.Min(100, val));
        }

        private bool IsValidGameDir(string dir)
        {
            if (string.IsNullOrWhiteSpace(dir) || !Directory.Exists(dir))
                return false;
            return File.Exists(Path.Combine(dir, "MP2_English.ras")) ||
                   File.Exists(Path.Combine(dir, "MaxPayne2.exe"));
        }

        private void AutoDetectGameFolder()
        {
            List<string> candidates = new List<string>();

            // 1. Current directory
            candidates.Add(AppDomain.CurrentDomain.BaseDirectory);

            // 2. Steam Registry & libraryfolders.vdf
            try
            {
                using (RegistryKey key = Registry.LocalMachine.OpenSubKey(@"SOFTWARE\WOW6432Node\Valve\Steam") ??
                                         Registry.CurrentUser.OpenSubKey(@"Software\Valve\Steam"))
                {
                    if (key != null)
                    {
                        string steamPath = (key.GetValue("InstallPath") ?? key.GetValue("SteamPath")) as string;
                        if (!string.IsNullOrEmpty(steamPath))
                        {
                            steamPath = steamPath.Replace("/", "\\");
                            candidates.Add(Path.Combine(steamPath, @"steamapps\common\MaxPayne2"));
                            string vdf = Path.Combine(steamPath, @"steamapps\libraryfolders.vdf");
                            if (File.Exists(vdf))
                            {
                                string vdfText = File.ReadAllText(vdf);
                                foreach (Match m in Regex.Matches(vdfText, "\"path\"\\s+\"([^\"]+)\""))
                                {
                                    string libPath = m.Groups[1].Value.Replace("\\\\", "\\");
                                    candidates.Add(Path.Combine(libPath, @"steamapps\common\MaxPayne2"));
                                }
                            }
                        }
                    }
                }
            }
            catch { }

            // 3. Remedy / GOG Registry
            string[] regPaths = new string[]
            {
                @"SOFTWARE\WOW6432Node\Remedy Entertainment\Max Payne 2",
                @"SOFTWARE\Remedy Entertainment\Max Payne 2",
                @"SOFTWARE\WOW6432Node\GOG.com\Games\1207666223"
            };
            foreach (string rp in regPaths)
            {
                try
                {
                    using (RegistryKey rk = Registry.LocalMachine.OpenSubKey(rp) ?? Registry.CurrentUser.OpenSubKey(rp))
                    {
                        if (rk != null)
                        {
                            string p = (rk.GetValue("InstallPath") ?? rk.GetValue("path") ?? rk.GetValue("EXE")) as string;
                            if (!string.IsNullOrEmpty(p))
                            {
                                if (File.Exists(p)) p = Path.GetDirectoryName(p);
                                candidates.Add(p);
                            }
                        }
                    }
                }
                catch { }
            }

            // 4. Standard paths across all fixed drives
            foreach (DriveInfo d in DriveInfo.GetDrives())
            {
                if (d.DriveType != DriveType.Fixed) continue;
                string root = d.RootDirectory.FullName;
                candidates.Add(Path.Combine(root, @"Program Files (x86)\Steam\steamapps\common\MaxPayne2"));
                candidates.Add(Path.Combine(root, @"Program Files\Steam\steamapps\common\MaxPayne2"));
                candidates.Add(Path.Combine(root, @"SteamLibrary\steamapps\common\MaxPayne2"));
                candidates.Add(Path.Combine(root, @"Games\MaxPayne2"));
                candidates.Add(Path.Combine(root, @"GOG Games\Max Payne 2"));
                candidates.Add(Path.Combine(root, @"Program Files (x86)\Rockstar Games\Max Payne 2"));
            }

            foreach (string c in candidates)
            {
                if (IsValidGameDir(c))
                {
                    txtGamePath.Text = Path.GetFullPath(c);
                    Log("Pasta do jogo detectada automaticamente: " + txtGamePath.Text);
                    return;
                }
            }

            ValidateSelectedPath();
        }

        private void ValidateSelectedPath()
        {
            string dir = txtGamePath.Text.Trim();
            if (IsValidGameDir(dir))
            {
                bool hasBackup = File.Exists(Path.Combine(dir, "MP2_English.ras.bak"));
                lblDetectionStatus.ForeColor = Color.FromArgb(100, 220, 120);
                lblDetectionStatus.Text = hasBackup
                    ? "✔ Max Payne 2 encontrado! (Backup original MP2_English.ras.bak já presente)"
                    : "✔ Max Payne 2 encontrado e pronto para instalação!";
                btnInstall.Enabled = true;
                btnUninstall.Enabled = true;
            }
            else
            {
                lblDetectionStatus.ForeColor = Color.FromArgb(235, 165, 60);
                lblDetectionStatus.Text = "⚠ Selecione a pasta onde estão localizados MaxPayne2.exe e MP2_English.ras.";
                btnInstall.Enabled = false;
                btnUninstall.Enabled = false;
            }
        }

        private void BtnBrowse_Click(object sender, EventArgs e)
        {
            using (FolderBrowserDialog fbd = new FolderBrowserDialog())
            {
                fbd.Description = "Selecione a pasta de instalação do Max Payne 2 (onde está o arquivo MaxPayne2.exe):";
                if (Directory.Exists(txtGamePath.Text))
                    fbd.SelectedPath = txtGamePath.Text;
                if (fbd.ShowDialog(this) == DialogResult.OK)
                {
                    txtGamePath.Text = fbd.SelectedPath;
                }
            }
        }

        private bool CheckGameNotRunning()
        {
            Process[] procs = Process.GetProcessesByName("MaxPayne2");
            if (procs.Length > 0)
            {
                MessageBox.Show(this,
                    "O jogo Max Payne 2 está aberto no momento.\nPor favor, feche o jogo antes de instalar ou desinstalar a tradução.",
                    "Max Payne 2 em execução", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return false;
            }
            return true;
        }

        private async void BtnInstall_Click(object sender, EventArgs e)
        {
            if (!CheckGameNotRunning()) return;

            string gameDir = txtGamePath.Text.Trim();
            string rasPath = Path.Combine(gameDir, "MP2_English.ras");
            if (!File.Exists(rasPath))
            {
                MessageBox.Show(this, "O arquivo MP2_English.ras não foi encontrado na pasta selecionada!", "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            bool doSndMfc = chkSndMfcPatch.Checked;
            bool doWidescreen = chkWidescreenFix.Checked;
            bool doMp2m = chkInstallMp2m.Checked;

            SetUiBusy(true);
            SetProgress(2);

            try
            {
                await Task.Run(() => RunInstallation(gameDir, doSndMfc, doWidescreen, doMp2m));
                SetProgress(100);
                Log("==================================================================");
                Log("✔ INSTALAÇÃO CONCLUÍDA COM SUCESSO! Bom jogo! — palestino7");
                Log("==================================================================");
                ValidateSelectedPath();
                MessageBox.Show(this,
                    "A Tradução Completa PT-BR do Max Payne 2 (por palestino7) foi instalada com sucesso!\n\n" +
                    "• 100% das legendas, menus, TVs e diários traduzidos\n" +
                    "• Todas as 138 páginas de Graphic Novel traduzidas em português\n" +
                    "• Todas as 32 telas de carregamento e HUD de armas traduzidos\n" +
                    "• Basta abrir o jogo normalmente pela Steam, GOG ou atalho!",
                    "Instalação Concluída — palestino7", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                Log("❌ ERRO durante a instalação: " + ex.Message);
                MessageBox.Show(this, "Ocorreu um erro durante a instalação:\n\n" + ex.Message, "Erro na Instalação", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                SetUiBusy(false);
            }
        }

        private void RunInstallation(string gameDir, bool doSndMfc, bool doWidescreen, bool doMp2m)
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), "MP2_PTBR_Palestino7_" + Guid.NewGuid().ToString("N").Substring(0, 8));
            Directory.CreateDirectory(tempRoot);

            try
            {
                // Step 1: Extract embedded payload.zip
                Log("Extraindo pacote de tradução embutido...");
                SetProgress(8);
                string payloadZipPath = Path.Combine(tempRoot, "payload.zip");
                using (Stream resStream = Assembly.GetExecutingAssembly().GetManifestResourceStream("Payload.zip"))
                {
                    if (resStream == null)
                        throw new Exception("Recurso interno Payload.zip não encontrado no executável.");
                    using (FileStream fs = new FileStream(payloadZipPath, FileMode.Create, FileAccess.Write))
                    {
                        resStream.CopyTo(fs);
                    }
                }

                string payloadExtractDir = Path.Combine(tempRoot, "payload");
                ZipFile.ExtractToDirectory(payloadZipPath, payloadExtractDir);
                File.Delete(payloadZipPath);

                string rasmakerExe = Path.Combine(payloadExtractDir, "tools", "rasmaker.exe");
                string transDir = Path.Combine(payloadExtractDir, "translation");
                string wsDir = Path.Combine(payloadExtractDir, "widescreen");

                // Step 2: Backup original MP2_English.ras -> MP2_English.ras.bak
                string rasPath = Path.Combine(gameDir, "MP2_English.ras");
                string rasBakPath = Path.Combine(gameDir, "MP2_English.ras.bak");
                if (!File.Exists(rasBakPath))
                {
                    Log("Criando backup seguro do arquivo original (MP2_English.ras.bak)...");
                    SetProgress(15);
                    File.Copy(rasPath, rasBakPath, false);
                }
                else
                {
                    Log("Backup original MP2_English.ras.bak já existe (usando-o como base limpa).");
                    SetProgress(15);
                }

                // Step 3: Unpack MP2_English.ras.bak into tempRasDir
                string tempRasDir = Path.Combine(tempRoot, "ras_work");
                Directory.CreateDirectory(tempRasDir);
                Log("Descompactando MP2_English.ras para aplicar os 198 arquivos traduzidos...");
                SetProgress(25);
                RunProcessHidden(rasmakerExe, "-x \"" + rasBakPath + "\" \"" + tempRasDir + "\"", tempRasDir, allowExitCode1: true);
                if (!Directory.Exists(Path.Combine(tempRasDir, "data", "database")))
                    throw new Exception("Falha ao descompactar MP2_English.ras.");

                // Step 4: Fix Remedy's WAV cue typo in Upper_East_Side_dlg_1180_cleaner3.wav & cleaner4.wav
                SetProgress(50);
                PatchUpperEastSideWavCues(tempRasDir);

                // Step 5: Copy all 198 translated files into tempRasDir
                Log("Aplicando textos, legendas, Graphic Novels, telas de carregamento e HUD PT-BR...");
                SetProgress(60);
                CopyDirectoryRecursive(Path.Combine(transDir, "data"), Path.Combine(tempRasDir, "data"));

                // Step 6: Repack MP2_English.ras
                Log("Reconstruindo MP2_English.ras nativo em Português (Brasil)...");
                SetProgress(72);
                string newRasTemp = Path.Combine(tempRoot, "MP2_English_new.ras");
                RunProcessHidden(rasmakerExe, "-a data \"" + newRasTemp + "\"", tempRasDir);
                if (!File.Exists(newRasTemp) || new FileInfo(newRasTemp).Length < 100 * 1024 * 1024)
                    throw new Exception("Falha ao reconstruir MP2_English.ras.");

                File.Copy(newRasTemp, rasPath, true);
                File.Delete(newRasTemp);

                // Step 7: Optional MaxPayne2_PTBR.mp2m
                if (doMp2m)
                {
                    Log("Gerando pacote Mod opcional (MaxPayne2_PTBR.mp2m)...");
                    SetProgress(84);
                    string mp2mPath = Path.Combine(gameDir, "MaxPayne2_PTBR.mp2m");
                    if (File.Exists(mp2mPath)) File.Delete(mp2mPath);
                    RunProcessHidden(rasmakerExe, "-a data \"" + mp2mPath + "\"", transDir);
                }

                // Step 8: Patch sndmfc.dll (subtitles at volume 0 fix)
                if (doSndMfc)
                {
                    SetProgress(90);
                    PatchSndMfcDll(gameDir);
                }

                // Step 9: Install Widescreen Fix + PT-BR ControlScheme.png
                if (doWidescreen && Directory.Exists(wsDir))
                {
                    Log("Instalando Widescreen Fix e esquema de controle Xbox em PT-BR...");
                    SetProgress(95);
                    string origCtrl = Path.Combine(gameDir, "scripts", "ControlScheme.png");
                    string bakCtrl = Path.Combine(gameDir, "scripts", "ControlScheme.png.bak");
                    if (File.Exists(origCtrl) && !File.Exists(bakCtrl))
                    {
                        File.Copy(origCtrl, bakCtrl, false);
                    }
                    CopyDirectoryRecursive(wsDir, gameDir);
                }
            }
            finally
            {
                try
                {
                    if (Directory.Exists(tempRoot))
                        Directory.Delete(tempRoot, true);
                }
                catch { }
            }
        }

        private void PatchUpperEastSideWavCues(string rasRoot)
        {
            string[] relCandidates = new string[]
            {
                @"data\database\sounds\Upper_East_Side",
                @"data\database\sounds\wavs\dialogue\09_upper_east_side"
            };
            byte[] pat = Encoding.ASCII.GetBytes("[UES_1180_07\0");
            byte[] rep = Encoding.ASCII.GetBytes("UES_1180_07\0\0");

            foreach (string rel in relCandidates)
            {
                string folder = Path.Combine(rasRoot, rel);
                if (!Directory.Exists(folder)) continue;
                foreach (string fn in new[] { "Upper_East_Side_dlg_1180_cleaner3.wav", "Upper_East_Side_dlg_1180_cleaner4.wav" })
                {
                    string p = Path.Combine(folder, fn);
                    if (!File.Exists(p)) continue;
                    byte[] data = File.ReadAllBytes(p);
                    int idx = IndexOfBytes(data, pat);
                    if (idx >= 0)
                    {
                        Buffer.BlockCopy(rep, 0, data, idx, rep.Length);
                        File.WriteAllBytes(p, data);
                        Log("Corrigido marcador de legenda WAV original da Remedy em " + fn + ".");
                    }
                }
            }
        }

        private void PatchSndMfcDll(string gameDir)
        {
            string dllPath = Path.Combine(gameDir, "sndmfc.dll");
            if (!File.Exists(dllPath))
            {
                Log("Aviso: sndmfc.dll não encontrado (pulando patch de áudio mudo).");
                return;
            }

            string bakPath = Path.Combine(gameDir, "sndmfc.dll.bak");
            if (!File.Exists(bakPath))
            {
                File.Copy(dllPath, bakPath, false);
            }

            byte[] data = File.ReadAllBytes(dllPath);
            // Check exact offsets 0x9DC5 and 0x9DD2
            if (data.Length > 0x9DD5)
            {
                bool isUnpatched = (data[0x9DC5] == 0x75 && data[0x9DC6] == 0x09 && data[0x9DD2] == 0x75 && data[0x9DD3] == 0x2B);
                bool isAlreadyPatched = (data[0x9DC5] == 0x90 && data[0x9DC6] == 0x90 && data[0x9DD2] == 0x90 && data[0x9DD3] == 0x90);
                if (isUnpatched)
                {
                    data[0x9DC5] = 0x90;
                    data[0x9DC6] = 0x90;
                    data[0x9DD2] = 0x90;
                    data[0x9DD3] = 0x90;
                    File.WriteAllBytes(dllPath, data);
                    Log("Aplicado patch em sndmfc.dll (legendas ativas mesmo com volume em 0).");
                }
                else if (isAlreadyPatched)
                {
                    Log("sndmfc.dll já está com a correção de legendas aplicada.");
                }
            }
        }

        private async void BtnUninstall_Click(object sender, EventArgs e)
        {
            if (!CheckGameNotRunning()) return;

            string gameDir = txtGamePath.Text.Trim();
            string rasBak = Path.Combine(gameDir, "MP2_English.ras.bak");
            if (!File.Exists(rasBak))
            {
                MessageBox.Show(this,
                    "Não foi encontrado um backup (MP2_English.ras.bak) nesta pasta.\nA tradução não parece estar instalada ou o backup foi removido.",
                    "Backup não encontrado", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            if (MessageBox.Show(this,
                "Deseja restaurar os arquivos originais em Inglês do Max Payne 2?",
                "Confirmar Restauração", MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes)
                return;

            SetUiBusy(true);
            SetProgress(20);

            try
            {
                await Task.Run(() =>
                {
                    string rasPath = Path.Combine(gameDir, "MP2_English.ras");
                    Log("Restaurando MP2_English.ras original a partir do backup...");
                    File.Copy(rasBak, rasPath, true);
                    File.Delete(rasBak);

                    string sndBak = Path.Combine(gameDir, "sndmfc.dll.bak");
                    string sndPath = Path.Combine(gameDir, "sndmfc.dll");
                    if (File.Exists(sndBak))
                    {
                        Log("Restaurando sndmfc.dll original...");
                        File.Copy(sndBak, sndPath, true);
                        File.Delete(sndBak);
                    }

                    string ctrlBak = Path.Combine(gameDir, "scripts", "ControlScheme.png.bak");
                    string ctrlPath = Path.Combine(gameDir, "scripts", "ControlScheme.png");
                    if (File.Exists(ctrlBak))
                    {
                        Log("Restaurando ControlScheme.png original...");
                        File.Copy(ctrlBak, ctrlPath, true);
                        File.Delete(ctrlBak);
                    }

                    string mp2m = Path.Combine(gameDir, "MaxPayne2_PTBR.mp2m");
                    if (File.Exists(mp2m))
                        File.Delete(mp2m);
                });

                SetProgress(100);
                Log("✔ Arquivos originais restaurados com sucesso!");
                ValidateSelectedPath();
                MessageBox.Show(this, "Os arquivos originais do Max Payne 2 foram restaurados com sucesso!", "Restauração Concluída", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                Log("❌ ERRO ao restaurar: " + ex.Message);
                MessageBox.Show(this, "Erro ao restaurar arquivos:\n" + ex.Message, "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                SetUiBusy(false);
            }
        }

        private void SetUiBusy(bool busy)
        {
            btnInstall.Enabled = !busy;
            btnUninstall.Enabled = !busy;
            btnBrowse.Enabled = !busy;
            txtGamePath.Enabled = !busy;
            chkSndMfcPatch.Enabled = !busy;
            chkWidescreenFix.Enabled = !busy;
            chkInstallMp2m.Enabled = !busy;
            this.Cursor = busy ? Cursors.WaitCursor : Cursors.Default;
        }

        private static void RunProcessHidden(string exePath, string args, string workingDir, bool allowExitCode1 = true)
        {
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = exePath,
                Arguments = args,
                WorkingDirectory = workingDir,
                CreateNoWindow = true,
                UseShellExecute = false
            };
            using (Process p = Process.Start(psi))
            {
                p.WaitForExit();
                if (p.ExitCode != 0 && !(allowExitCode1 && p.ExitCode == 1))
                {
                    throw new Exception("rasmaker retornou código " + p.ExitCode + " para argumentos: " + args);
                }
            }
        }

        private static void CopyDirectoryRecursive(string sourceDir, string targetDir)
        {
            Directory.CreateDirectory(targetDir);
            foreach (string file in Directory.GetFiles(sourceDir))
            {
                string dest = Path.Combine(targetDir, Path.GetFileName(file));
                File.Copy(file, dest, true);
            }
            foreach (string subDir in Directory.GetDirectories(sourceDir))
            {
                string destSub = Path.Combine(targetDir, Path.GetFileName(subDir));
                CopyDirectoryRecursive(subDir, destSub);
            }
        }

        private static int IndexOfBytes(byte[] haystack, byte[] needle)
        {
            for (int i = 0; i <= haystack.Length - needle.Length; i++)
            {
                bool match = true;
                for (int j = 0; j < needle.Length; j++)
                {
                    if (haystack[i + j] != needle[j])
                    {
                        match = false;
                        break;
                    }
                }
                if (match) return i;
            }
            return -1;
        }

        [STAThread]
        public static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            InstallerForm form = new InstallerForm();
            if (args != null && args.Length >= 2 && args[0] == "--screenshot")
            {
                string outPath = args[1];
                form.Shown += async (s, e) =>
                {
                    form.txtGamePath.SelectionStart = 0;
                    form.txtGamePath.SelectionLength = 0;
                    form.btnInstall.Focus();
                    form.Refresh();
                    await Task.Delay(300);
                    using (Bitmap bmp = new Bitmap(form.Width, form.Height))
                    {
                        form.DrawToBitmap(bmp, new Rectangle(0, 0, form.Width, form.Height));
                        bmp.Save(outPath, System.Drawing.Imaging.ImageFormat.Png);
                    }
                    form.Close();
                };
            }
            Application.Run(form);
        }
    }
}
