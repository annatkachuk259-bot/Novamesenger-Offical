
#define MyAppName "NovaMessenger"
#define MyAppVersion "1.3"
#define MyAppPublisher "Nova Corp"
#define MyAppExeName "NovaMessenger.exe"

[Setup]
AppId={{D82B14C0-85A3-41E2-9F1C-123456789ABC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=C:\Users\Юрий\Desktop\NovaMessenger\InstallerOutput
OutputBaseFilename=NovaMessenger_Setup_v1.3
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Исправлено имя исполняемого файла (убедитесь, что после pyinstaller он называется NovaMessenger.exe или переименуйте его в папке dist)
Source: "C:\Users\Юрий\Desktop\NovaMessenger\dist\novamesenger.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Юрий\Desktop\NovaMessenger\dist\serviceAccountKey.json"; DestDir: "{app}"; Flags: ignoreversion
; Добавлено копирование иконки в папку программы, чтобы ярлыки могли её отображать
Source: "C:\Users\Юрий\Desktop\NovaMessenger\photo_2026-08-25_13-51-31.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\photo_2026-08-25_13-51-31.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\photo_2026-08-25_13-51-31.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
