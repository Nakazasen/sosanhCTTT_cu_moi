; Inno Setup 6 script.  AppId must remain unchanged between releases.
#define AppName "So sanh CTTT"
#define AppVersion "7.4.1"
#define AppPublisher "PE Dept"
#define AppId "{{B655CBC7-65DB-4DFD-BEDB-8B8E14822DD8}}"
#define BundleDir "..\release_artifacts\install_bundle"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\SosanhCTTT
DefaultGroupName={#AppName}
OutputDir=..\release_artifacts
OutputBaseFilename=SosanhCTTT_Setup_{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#AppName}
CloseApplications=yes
RestartApplications=no

[Files]
Source: "{#BundleDir}\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\SosanhCTTT.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\SosanhCTTT.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\SosanhCTTT.exe"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; User settings and downloaded update installers are stored in LocalAppData\SosanhCTTTData and deliberately retained.
Type: filesandordirs; Name: "{app}\_old"
