@echo off
chcp 65001 >nul
title Desinstalador - Tradução Max Payne 2 PT-BR

:: Elevacao de privilegios UAC
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando privilegios de Administrador...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
cls
echo ========================================================================
echo        DESINSTALADOR DA TRADUÇÃO PT-BR - MAX PAYNE 2
echo ========================================================================
echo.

set "GAME_PATH=%~dp0"
if not exist "%GAME_PATH%\maxpayne2.exe" (
    if exist "C:\Program Files (x86)\Steam\steamapps\common\MaxPayne2\maxpayne2.exe" (
        set "GAME_PATH=C:\Program Files (x86)\Steam\steamapps\common\MaxPayne2"
    )
)

if not exist "%GAME_PATH%\maxpayne2.exe" (
    echo [ERRO] Pasta do jogo não encontrada.
    pause
    exit /b 1
)

echo Pasta do jogo: "%GAME_PATH%"
echo.

if exist "%GAME_PATH%\MP2_English.ras.bak" (
    echo Restaurando arquivo original MP2_English.ras a partir do backup...
    copy /y "%GAME_PATH%\MP2_English.ras.bak" "%GAME_PATH%\MP2_English.ras" >nul
    del "%GAME_PATH%\MP2_English.ras.bak" >nul 2>&1
    echo [OK] Arquivo original restaurado com sucesso!
) else (
    echo [AVISO] Backup MP2_English.ras.bak não encontrado.
)

if exist "%GAME_PATH%\MaxPayne2_PTBR.mp2m" (
    del "%GAME_PATH%\MaxPayne2_PTBR.mp2m" >nul 2>&1
    echo [OK] Mod MaxPayne2_PTBR.mp2m removido.
)

echo.
echo ========================================================================
echo     TRADUÇÃO DESINSTALADA - JOGO RESTAURADO AO ORIGINAL
echo ========================================================================
echo.
pause
exit /b 0
