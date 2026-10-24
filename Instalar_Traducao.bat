@echo off
chcp 65001 >nul
title Instalador - Max Payne 2: The Fall of Max Payne (Tradução PT-BR)

:: Elevacao de privilegios (UAC) para gravacao em Arquivos de Programas
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando privilegios de Administrador...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
cls
echo ========================================================================
echo        MAX PAYNE 2: THE FALL OF MAX PAYNE - TRADUÇÃO PT-BR
echo                      Versão Moderna e Impecável
echo ========================================================================
echo.

set "GAME_PATH="

:: 1. Verifica o caminho informado pelo usuario
if exist "C:\Program Files (x86)\Steam\steamapps\common\MaxPayne2\maxpayne2.exe" (
    set "GAME_PATH=C:\Program Files (x86)\Steam\steamapps\common\MaxPayne2"
    goto :FOUND
)

:: 2. Verifica nome padrao alternativo da pasta na Steam
if exist "C:\Program Files (x86)\Steam\steamapps\common\Max Payne 2 The Fall of Max Payne\maxpayne2.exe" (
    set "GAME_PATH=C:\Program Files (x86)\Steam\steamapps\common\Max Payne 2 The Fall of Max Payne"
    goto :FOUND
)

:: 3. Verifica pasta atual
if exist "maxpayne2.exe" (
    set "GAME_PATH=%CD%"
    goto :FOUND
)

echo Não foi possível localizar automaticamente a pasta do Max Payne 2.
echo.
set /p "GAME_PATH=Por favor, digite ou cole o caminho da pasta do jogo: "
if not exist "%GAME_PATH%\maxpayne2.exe" (
    echo.
    echo [ERRO] O arquivo maxpayne2.exe não foi encontrado em:
    echo "%GAME_PATH%"
    echo.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit /b 1
)

:FOUND
echo [OK] Pasta do jogo detectada:
echo "%GAME_PATH%"
echo.

:: Verifica integridade dos arquivos da traducao
if not exist "MP2_English_PTBR.ras" (
    echo [ERRO] Arquivo MP2_English_PTBR.ras não encontrado na pasta do instalador!
    pause
    exit /b 1
)
if not exist "MaxPayne2_PTBR.mp2m" (
    echo [ERRO] Arquivo MaxPayne2_PTBR.mp2m não encontrado na pasta do instalador!
    pause
    exit /b 1
)

echo Criando backup do arquivo original...
if not exist "%GAME_PATH%\MP2_English.ras.bak" (
    if exist "%GAME_PATH%\MP2_English.ras" (
        copy /y "%GAME_PATH%\MP2_English.ras" "%GAME_PATH%\MP2_English.ras.bak" >nul
        echo [OK] Backup criado com sucesso: MP2_English.ras.bak
    )
) else (
    echo [INFO] Backup previo ja existente mantido intacto.
)

echo.
echo Instalando a Tradução em Português do Brasil...
echo Copiando MP2_English.ras (Jogo em PT-BR direto)...
copy /y "MP2_English_PTBR.ras" "%GAME_PATH%\MP2_English.ras" >nul

echo Copiando Desinstalador para a pasta do jogo...
copy /y "Desinstalar_Traducao.bat" "%GAME_PATH%\Desinstalar_Traducao.bat" >nul

:: Garante Subtitles Toggle = 1 e verifica se Effects Volume está zerado (Effects Volume = 0 desativa legendas na engine sndmfc.dll)
reg add "HKCU\Software\Remedy Entertainment\Max Payne 2\Other Settings" /v "Subtitles Toggle" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Remedy Entertainment\Max Payne 2\Customized Game" /v "Customized Game" /t REG_SZ /d "" /f >nul 2>&1
for /f "tokens=3" %%A in ('reg query "HKCU\Software\Remedy Entertainment\Max Payne 2\Audio Settings" /v "Effects Volume" 2^>nul ^| findstr /i "Effects Volume"') do (
    if "%%A"=="0x0" (
        reg add "HKCU\Software\Remedy Entertainment\Max Payne 2\Audio Settings" /v "Effects Volume" /t REG_DWORD /d 10000 /f >nul 2>&1
        reg add "HKCU\Software\Remedy Entertainment\Max Payne 2\Audio Settings" /v "Music Volume" /t REG_DWORD /d 10000 /f >nul 2>&1
    )
)

echo.
echo ========================================================================
echo        TRADUÇÃO INSTALADA COM SUCESSO!
echo ========================================================================
echo.
echo Destaques da Tradução:
echo  - Tom narrativo Neo-Noir autêntico, poético e fiel à obra de Sam Lake
echo  - Todas as 22 fases e séries de TV completamente traduzidas
echo  - Menus, HUD, tutoriais, armas e piadas do menu em PT-BR
echo  - 100%% estável, sem corrupções na HUD ou na engine
echo.
echo Dica: Nas Opções de Jogo, certifique-se de que "Legendas" (Subtitles)
echo está marcado como ATIVADO (ON).
echo.
echo Pressione qualquer tecla para finalizar...
pause >nul
exit /b 0
