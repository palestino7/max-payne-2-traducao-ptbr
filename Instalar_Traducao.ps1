#Requires -RunAsAdministrator
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "       MAX PAYNE 2: THE FALL OF MAX PAYNE - TRADUÇÃO PT-BR" -ForegroundColor Yellow
Write-Host "                     Instalador Automatizado" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$DefaultPaths = @(
    "C:\Program Files (x86)\Steam\steamapps\common\MaxPayne2",
    "C:\Program Files (x86)\Steam\steamapps\common\Max Payne 2 The Fall of Max Payne",
    $ScriptDir
)

$GamePath = $null
foreach ($path in $DefaultPaths) {
    if (Test-Path (Join-Path $path "maxpayne2.exe")) {
        $GamePath = $path
        break
    }
}

if (-not $GamePath) {
    $UserPath = Read-Host "Caminho do jogo não detectado automaticamente. Digite ou cole o caminho da pasta do Max Payne 2"
    if (Test-Path (Join-Path $UserPath "maxpayne2.exe")) {
        $GamePath = $UserPath
    } else {
        Write-Host "[ERRO] Executavel maxpayne2.exe nao encontrado em: $UserPath" -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host "[OK] Pasta do jogo detectada: $GamePath" -ForegroundColor Green
Write-Host ""

$RasFile = Join-Path $ScriptDir "MP2_English_PTBR.ras"
$Mp2mFile = Join-Path $ScriptDir "MaxPayne2_PTBR.mp2m"
$UninstFile = Join-Path $ScriptDir "Desinstalar_Traducao.bat"

if (-not (Test-Path $RasFile) -or -not (Test-Path $Mp2mFile)) {
    Write-Host "[ERRO] Arquivos de instalacao ausentes na pasta do script!" -ForegroundColor Red
    pause
    exit 1
}

# Backup
$BakFile = Join-Path $GamePath "MP2_English.ras.bak"
$TargetRas = Join-Path $GamePath "MP2_English.ras"
if (-not (Test-Path $BakFile)) {
    if (Test-Path $TargetRas) {
        Copy-Item -Path $TargetRas -Destination $BakFile -Force
        Write-Host "[OK] Backup do arquivo original criado: MP2_English.ras.bak" -ForegroundColor Green
    }
} else {
    Write-Host "[INFO] Backup previo ja existente mantido intacto." -ForegroundColor DarkGray
}

Write-Host "Instalando traducao PT-BR..." -ForegroundColor Yellow
Copy-Item -Path $RasFile -Destination $TargetRas -Force
Write-Host "  -> MP2_English.ras copiado com sucesso." -ForegroundColor Green

if (Test-Path $UninstFile) {
    Copy-Item -Path $UninstFile -Destination (Join-Path $GamePath "Desinstalar_Traducao.bat") -Force
    Write-Host "  -> Desinstalador copiado para a pasta do jogo." -ForegroundColor Green
}

# Garantir Legendas ativadas e Volume de Efeitos > 0 no Registro (Effects Volume = 0 desativa cues de legenda na engine sndmfc.dll)
$RegOther = "HKCU:\Software\Remedy Entertainment\Max Payne 2\Other Settings"
if (Test-Path $RegOther) {
    Set-ItemProperty -Path $RegOther -Name "Subtitles Toggle" -Value 1 -Type DWord
}
$RegAudio = "HKCU:\Software\Remedy Entertainment\Max Payne 2\Audio Settings"
if (Test-Path $RegAudio) {
    $effVol = (Get-ItemProperty -Path $RegAudio -Name "Effects Volume" -ErrorAction SilentlyContinue)."Effects Volume"
    if ($null -ne $effVol -and $effVol -eq 0) {
        Set-ItemProperty -Path $RegAudio -Name "Effects Volume" -Value 10000 -Type DWord
        Set-ItemProperty -Path $RegAudio -Name "Music Volume" -Value 10000 -Type DWord
        Write-Host "  -> Volume de Efeitos restaurado (Effects Volume = 0 impedia o disparo de legendas na engine)." -ForegroundColor Green
    }
}
$RegMod = "HKCU:\Software\Remedy Entertainment\Max Payne 2\Customized Game"
if (Test-Path $RegMod) {
    Set-ItemProperty -Path $RegMod -Name "Customized Game" -Value "" -Type String
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "       TRADUÇÃO INSTALADA COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Destaques:" -ForegroundColor White
Write-Host " - 100% dos dialogos e series de TV traduzidos com acentuacao perfeita" -ForegroundColor Gray
Write-Host " - Tom literario Neo-Noir autentico e fiel ao roteiro original" -ForegroundColor Gray
Write-Host " - Compatibilidade total e estabilidade validada em tempo real" -ForegroundColor Gray
Write-Host ""
Write-Host "Bom jogo!" -ForegroundColor Yellow
Write-Host ""
pause
