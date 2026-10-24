; ==============================================================================
; Max Payne 2: The Fall of Max Payne — Tradução PT-BR (Definitiva v3.0.0)
; Autor / Publisher: Palestino7
;
; Inno Setup 6.7+ Unicode Installation Script
; Arquitetura Segura, Zero Falso-Positivo, Instalação Modular e Rollback 100%
; ==============================================================================

#define MyAppName "Max Payne 2: The Fall of Max Payne — Tradução PT-BR"
#define MyAppVerName "Max Payne 2: The Fall of Max Payne — Tradução PT-BR (Definitiva v3.0.0) por Palestino7"
#define MyAppShortName "Max Payne 2 PT-BR"
#define MyAppVersion "3.0.0"
#define MyAppPublisher "Palestino7"
#define MyAppURL "https://github.com/palestino7/max-payne-2-traducao-ptbr"
#define MyAppExeName "maxpayne2.exe"

[Setup]
; AppId único para identificar a instalação da tradução
AppId={{C69A5D6B-4D1E-4B9F-840D-1B2F7E5E3A91}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppVerName}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={code:GetDefaultGameDir}
DirExistsWarning=no
EnableDirDoesntExistWarning=no
DisableDirPage=no
AppendDefaultDirName=no
DefaultGroupName={#MyAppShortName}
DisableProgramGroupPage=yes
OutputDir=..\..\dist
OutputBaseFilename=Instalador_MaxPayne2_PTBR_v3.0.0
Compression=lzma2/max
SolidCompression=yes
LZMANumBlockThreads=4
WizardStyle=modern
UninstallDisplayName={#MyAppName} (v{#MyAppVersion}) por {#MyAppPublisher}
UninstallFilesDir={app}\uninst_ptbr
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog commandline
UsedUserAreasWarning=no
UsePreviousSetupType=no
UsePreviousAppDir=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Messages]
brazilianportuguese.BeveledLabel=Tradução Definitiva v3.0.0 por Palestino7

[Types]
Name: "full"; Description: "Instalação Completa Recomendada (Tradução + Vídeo Recap + Correção de Áudio + Widescreen)"
Name: "compact"; Description: "Instalação Básica (Apenas Tradução dos Textos, Menus, Legendas e Graphic Novels)"
Name: "custom"; Description: "Instalação Personalizada"; Flags: iscustom

[Components]
Name: "core"; Description: "Tradução dos Textos, Menus, Legendas e Graphic Novels (Obrigatório)"; Types: full compact custom; Flags: fixed
Name: "video"; Description: "Cutscene de Introdução ""Anteriormente..."" Legendada (PREVIOUSLY.bik)"; Types: full custom
Name: "audiofix"; Description: "Correção de Áudio e Falhas Modernas (Patch sndmfc.dll + Registro do Windows)"; Types: full custom
Name: "widescreen"; Description: "Widescreen Fix (ThirteenAG) + Suporte a Controles Modernos com Esquema em PT-BR"; Types: full custom
Name: "mp2m"; Description: "Pacote Mod Adicional (MaxPayne2_PTBR.mp2m para o Seletor de Mods)"; Types: full custom

[Files]
; Componente 1: Tradução Principal (substitui MP2_English.ras com backup prévio)
Source: "..\..\MP2_English_PTBR.ras"; DestDir: "{app}"; DestName: "MP2_English.ras"; Flags: ignoreversion uninsneveruninstall; Components: core
Source: "..\..\Desinstalar_Traducao.bat"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; Componente 2: Cutscene Recap Legendada
Source: "..\..\translation_ptbr\movies\PREVIOUSLY.bik"; DestDir: "{app}\movies"; DestName: "previously.bik"; Flags: ignoreversion uninsneveruninstall; Components: video

; Componente 3: Correção de Áudio (sndmfc.dll pré-patcheada)
Source: "assets\sndmfc.dll"; DestDir: "{app}"; Flags: ignoreversion uninsneveruninstall; Components: audiofix

; Componente 4: Widescreen Fix ThirteenAG + Xidi + Esquema PT-BR
Source: "assets\widescreen\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: widescreen

; Componente 5: Pacote Mod Opcional
Source: "..\..\MaxPayne2_PTBR.mp2m"; DestDir: "{app}"; Flags: ignoreversion; Components: mp2m

[Registry]
; Ativa exibição de legendas nas opções do Max Payne 2
Root: HKCU; Subkey: "Software\Remedy Entertainment\Max Payne 2\Other Settings"; ValueType: dword; ValueName: "Subtitles Toggle"; ValueData: "1"; Components: core
; Reseta seleção de mod no jogo original
Root: HKCU; Subkey: "Software\Remedy Entertainment\Max Payne 2\Customized Game"; ValueType: string; ValueName: "Customized Game"; ValueData: ""; Components: core
; Correção de áudio mudo quando volume de efeitos estiver zerado no registro
Root: HKCU; Subkey: "Software\Remedy Entertainment\Max Payne 2\Audio Settings"; ValueType: dword; ValueName: "Effects Volume"; ValueData: "10000"; Check: IsEffectsVolumeZero; Components: audiofix
Root: HKCU; Subkey: "Software\Remedy Entertainment\Max Payne 2\Audio Settings"; ValueType: dword; ValueName: "Music Volume"; ValueData: "10000"; Check: IsEffectsVolumeZero; Components: audiofix

[Code]
// =============================================================================
// Rotinas Pascal Script para Detecção, Validação, Backup e Restauração 100%
// =============================================================================

function DirHasGame(Path: String): Boolean;
begin
  Result := (Path <> '') and DirExists(Path) and
            (FileExists(Path + '\maxpayne2.exe') or
             FileExists(Path + '\MP2_English.ras') or
             FileExists(Path + '\MP2_Data.ras'));
end;

function ParseSteamLibraryFolders(VdfPath: String): String;
var
  Lines: TArrayOfString;
  I, P1, P2: Integer;
  Line, LibPath: String;
begin
  Result := '';
  if not FileExists(VdfPath) then Exit;
  if LoadStringsFromFile(VdfPath, Lines) then
  begin
    for I := 0 to GetArrayLength(Lines) - 1 do
    begin
      Line := Lines[I];
      P1 := Pos('"path"', Line);
      if P1 > 0 then
      begin
        Delete(Line, 1, P1 + 5);
        P1 := Pos('"', Line);
        if P1 > 0 then
        begin
          Delete(Line, 1, P1);
          P2 := Pos('"', Line);
          if P2 > 0 then
          begin
            LibPath := Copy(Line, 1, P2 - 1);
            StringChangeEx(LibPath, '\\', '\', True);
            if DirHasGame(LibPath + '\steamapps\common\MaxPayne2') then
            begin
              Result := LibPath + '\steamapps\common\MaxPayne2';
              Exit;
            end;
            if DirHasGame(LibPath + '\steamapps\common\Max Payne 2 The Fall of Max Payne') then
            begin
              Result := LibPath + '\steamapps\common\Max Payne 2 The Fall of Max Payne';
              Exit;
            end;
          end;
        end;
      end;
    end;
  end;
end;

function GetDefaultGameDir(Param: String): String;
var
  Path, LibResult: String;
begin
  Result := '';

  // 1. Steam AppID 12150 (Chave de Desinstalação Oficial da Steam)
  if RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 12150', 'InstallLocation', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;
  if RegQueryStringValue(HKLM32, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 12150', 'InstallLocation', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;
  if RegQueryStringValue(HKLM64, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 12150', 'InstallLocation', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;

  // 2. Steam InstallPath e Bibliotecas Secundárias (libraryfolders.vdf)
  if RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Valve\Steam', 'InstallPath', Path) or
     RegQueryStringValue(HKLM, 'SOFTWARE\Valve\Steam', 'InstallPath', Path) or
     RegQueryStringValue(HKCU, 'Software\Valve\Steam', 'SteamPath', Path) then
  begin
    StringChangeEx(Path, '/', '\', True);
    if DirHasGame(Path + '\steamapps\common\MaxPayne2') then
    begin
      Result := Path + '\steamapps\common\MaxPayne2';
      Exit;
    end;
    if DirHasGame(Path + '\steamapps\common\Max Payne 2 The Fall of Max Payne') then
    begin
      Result := Path + '\steamapps\common\Max Payne 2 The Fall of Max Payne';
      Exit;
    end;

    // Busca nas bibliotecas adicionais configuradas na Steam
    LibResult := ParseSteamLibraryFolders(Path + '\steamapps\libraryfolders.vdf');
    if LibResult <> '' then
    begin
      Result := LibResult;
      Exit;
    end;
  end;

  // 3. GOG Galaxy / GOG Games
  if RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\GOG.com\Games\1207658930', 'path', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;
  if RegQueryStringValue(HKLM, 'SOFTWARE\GOG.com\Games\1207658930', 'path', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;
  if RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\GOG.com\Games\1207666223', 'path', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;
  if RegQueryStringValue(HKLM, 'SOFTWARE\GOG.com\Games\1207666223', 'path', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;

  // 4. Retail CD / Remedy Entertainment / Rockstar Games
  if RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Remedy Entertainment\Max Payne 2', 'InstallPath', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;
  if RegQueryStringValue(HKLM, 'SOFTWARE\Remedy Entertainment\Max Payne 2', 'InstallPath', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;
  if RegQueryStringValue(HKCU, 'Software\Remedy Entertainment\Max Payne 2', 'InstallPath', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;
  if RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Rockstar Games\Max Payne 2', 'InstallPath', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;
  if RegQueryStringValue(HKLM, 'SOFTWARE\Rockstar Games\Max Payne 2', 'InstallPath', Path) and DirHasGame(Path) then
  begin
    Result := Path;
    Exit;
  end;

  // 5. Verificação de Diretórios Típicos Conhecidos
  if DirHasGame(ExpandConstant('{autopf32}\Steam\steamapps\common\MaxPayne2')) then
    Result := ExpandConstant('{autopf32}\Steam\steamapps\common\MaxPayne2')
  else if DirHasGame(ExpandConstant('{autopf}\Steam\steamapps\common\MaxPayne2')) then
    Result := ExpandConstant('{autopf}\Steam\steamapps\common\MaxPayne2')
  else if DirHasGame('C:\Games\MaxPayne2') then
    Result := 'C:\Games\MaxPayne2'
  else if DirHasGame('C:\GOG Games\Max Payne 2') then
    Result := 'C:\GOG Games\Max Payne 2'
  else if DirHasGame(ExpandConstant('{autopf32}\Rockstar Games\Max Payne 2')) then
    Result := ExpandConstant('{autopf32}\Rockstar Games\Max Payne 2')
  else
    Result := ExpandConstant('{autopf32}\Steam\steamapps\common\MaxPayne2');
end;

function IsEffectsVolumeZero(): Boolean;
var
  Val: Cardinal;
begin
  Result := False;
  if RegQueryDWordValue(HKCU, 'Software\Remedy Entertainment\Max Payne 2\Audio Settings', 'Effects Volume', Val) then
    Result := (Val = 0);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Msg: String;
begin
  Result := True;
  if (not WizardSilent) and (CurPageID = wpSelectDir) then
  begin
    if not DirHasGame(WizardDirValue) then
    begin
      Msg := 'Atenção: Não foi encontrado o arquivo "maxpayne2.exe" nem "MP2_English.ras" na pasta selecionada:' + #13#10#13#10 +
             WizardDirValue + #13#10#13#10 +
             'Deseja continuar mesmo assim e instalar a tradução nesta pasta?';
      if MsgBox(Msg, mbConfirmation, MB_YESNO) = IDNO then
        Result := False;
    end;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  AppDir: String;
begin
  Result := '';
  if WizardSilent then
  begin
    AppDir := ExpandConstant('{app}');
    if not DirHasGame(AppDir) then
    begin
      Result := 'A pasta de destino não contém uma instalação válida do Max Payne 2 ("maxpayne2.exe" ou "MP2_English.ras" ausente): ' + AppDir;
    end;
  end;
end;

procedure SafeBackupFile(const SrcFile, BakFile: String);
begin
  if FileExists(SrcFile) and not FileExists(BakFile) then
  begin
    CopyFile(SrcFile, BakFile, False);
  end;
end;

procedure SafeRestoreFile(const BakFile, SrcFile: String);
begin
  if FileExists(BakFile) then
  begin
    CopyFile(BakFile, SrcFile, False);
    DeleteFile(BakFile);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDir: String;
begin
  if CurStep = ssInstall then
  begin
    AppDir := ExpandConstant('{app}');

    // Backup 1: MP2_English.ras original
    SafeBackupFile(AppDir + '\MP2_English.ras', AppDir + '\MP2_English.ras.bak');

    // Backup 2: PREVIOUSLY.bik original se existir e componente de vídeo selecionado
    if WizardIsComponentSelected('video') then
      SafeBackupFile(AppDir + '\movies\previously.bik', AppDir + '\movies\previously.bik.bak');

    // Backup 3: sndmfc.dll original se componente de correção de áudio selecionado
    if WizardIsComponentSelected('audiofix') then
      SafeBackupFile(AppDir + '\sndmfc.dll', AppDir + '\sndmfc.dll.bak');

    // Backup 4: ControlScheme.png original se componente widescreen selecionado
    if WizardIsComponentSelected('widescreen') then
      SafeBackupFile(AppDir + '\scripts\ControlScheme.png', AppDir + '\scripts\ControlScheme.png.bak');
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    AppDir := ExpandConstant('{app}');

    // Restauração 1: MP2_English.ras.bak -> MP2_English.ras
    SafeRestoreFile(AppDir + '\MP2_English.ras.bak', AppDir + '\MP2_English.ras');

    // Restauração 2: previously.bik.bak -> previously.bik
    SafeRestoreFile(AppDir + '\movies\previously.bik.bak', AppDir + '\movies\previously.bik');

    // Restauração 3: sndmfc.dll.bak -> sndmfc.dll
    SafeRestoreFile(AppDir + '\sndmfc.dll.bak', AppDir + '\sndmfc.dll');

    // Restauração 4: ControlScheme.png.bak -> ControlScheme.png
    SafeRestoreFile(AppDir + '\scripts\ControlScheme.png.bak', AppDir + '\scripts\ControlScheme.png');

    // Remoção de arquivos específicos da tradução
    if FileExists(AppDir + '\MaxPayne2_PTBR.mp2m') then
      DeleteFile(AppDir + '\MaxPayne2_PTBR.mp2m');
    if FileExists(AppDir + '\Desinstalar_Traducao.bat') then
      DeleteFile(AppDir + '\Desinstalar_Traducao.bat');

    // Limpeza de pastas vazias residuais da desinstalação
    if DirExists(AppDir + '\uninst_ptbr') then
      RemoveDir(AppDir + '\uninst_ptbr');
  end;
end;
