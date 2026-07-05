; Exam Email Automation — Inno Setup Installer Script
; Run on Windows with Inno Setup 6+ (https://jrsoftware.org/isinfo.php)
;
; Usage:
;   1. Build the PyInstaller executable:  scripts\build_exe.bat
;   2. Compile this script in Inno Setup or run:  scripts\build_installer.bat
;   3. Output: dist\installer\ExamEmailAutomation-Setup-v1.0.0.exe

#define MyAppName "Exam Email Automation"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Exam Email Automation"
#define MyAppExeName "ExamEmailAutomation.exe"

[Setup]
AppId={{2D7F8F70-87C7-493D-A742-51F1208A64F4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist\installer
OutputBaseFilename=ExamEmailAutomation-Setup-v{#MyAppVersion}
SetupIconFile=..\resources\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "..\dist\ExamEmailAutomation\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
