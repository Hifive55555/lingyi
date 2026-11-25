; ============================================================================
;  灵弈小窗 + 红方智能体 —— Inno Setup 安装脚本（Inno Setup 6）
;
;  不要直接双击本文件，用同目录的 build_installer.bat（先打包再编译）。
;  产物：<包目录>\dist\灵弈小窗+红方智能体_setup_<版本>.exe
;
;  三个设计要点（都是踩过的坑）：
;   1) PrivilegesRequired=lowest —— 必须普通权限。这台比赛机的 %LOCALAPPDATA%
;      (C:\Users\A\AppData\Local) 不可写；用管理员（高完整性级别）跑，WebView2
;      拿不到 profile 目录 → 小窗灰屏 + 0x80070005。
;   2) 文件不按死路径铺：整包进 {app}\_pkg，再调 deploy.ps1 部署。拷贝映射
;      (intelligent\ / ai\engine\LingYi\ / ai\agent\overlay\) 只有一处定义，
;      安装与手工部署同一套逻辑，都会 .bak_时间戳 备份并跑 check_env.py 自检。
;   3) 校验 {app} 是灵弈根目录（其下有 intelligent\new_env\ray210\python.exe）。
; ============================================================================

#define MyAppName "灵弈小窗 + 红方智能体"
#define MyAppVer "20261119"
#define MyAppId "{{A7F3C1E2-5B4D-4E8A-9C31-7D2F6B8E4A10}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVer}
AppVerName={#MyAppName} {#MyAppVer}
AppPublisher=兵棋比赛队
DefaultDirName={code:LingyiDir}
DefaultGroupName=灵弈小窗
DisableProgramGroupPage=yes
DisableDirPage=no
PrivilegesRequired=lowest
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=灵弈小窗+红方智能体_setup_{#MyAppVer}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ShowLanguageDialog=no
UninstallDisplayName={#MyAppName}
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel1=欢迎安装 [name]
WelcomeLabel2=这个安装包会把「红方智能体 + 两个小窗」装进灵弈。%n%n  · 主智能体 Mission_all_red.py（红方）%n  · 战术模块 BattlefieldMonitor / SamBattalionDefense / ShipClusterDefense%n  · 灵弈小窗（自带 WebView2 宿主）+ 监控小窗%n%n下一步请选择灵弈根目录：其下应有 intelligent\new_env\ray210\python.exe，一般就是 D:\LingYi。%n%n不需要联网，也不会安装任何 Python 包。
SelectDirDesc=灵弈装在哪？
SelectDirLabel3=安装程序会把文件部署到所选目录的 intelligent\ 下（覆盖前自动备份 .bak_时间戳）。
SelectDirBrowseLabel=如果自动探测不对，点"浏览"选到灵弈根目录（能看到 APlatformLobby.exe 的那一层）。
DiskSpaceMBLabel=至少需要 [mb] MB 磁盘空间。
ReadyLabel1=准备安装 [name]
ReadyLabel2a=点"安装"开始部署；勾选下面的选项可以创建桌面快捷方式。
InstallingLabel=正在部署到灵弈（先备份被覆盖的文件，请稍等）...
FinishedHeadingLabel=[name] 安装完成
FinishedLabel=部署已完成。接下来：%n%n  1) 打开 APlatformLobby.exe → 单机版启动，加载想定%n  2) 智能体调度 → 智能体编辑 → 左下角 + → 选 overlay_ai.py，点启动%n  3) 双击桌面「灵弈小窗」→ 出现两个窗口（主小窗 + 监控小窗）%n%n如果窗口不出来，看 intelligent\ai\agent\overlay\logs\launcher.log。
ConfirmUninstall=确定卸载 [name] 吗？%n%n只删安装程序放进去的文件，灵弈本体、比赛数据和日志都不动。

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式（灵弈小窗 / 小窗截图）"; GroupDescription: "附加任务："

[Files]
Source: "..\build\_pkg\*"; DestDir: "{app}\_pkg"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autodesktop}\灵弈小窗"; Filename: "{app}\intelligent\ai\agent\overlay\灵弈小窗.bat"; WorkingDir: "{app}\intelligent\ai\agent\overlay"; Tasks: desktopicon
Name: "{autodesktop}\小窗截图"; Filename: "{app}\intelligent\ai\agent\overlay\截图.bat"; WorkingDir: "{app}\intelligent\ai\agent\overlay"; Tasks: desktopicon
Name: "{group}\灵弈小窗"; Filename: "{app}\intelligent\ai\agent\overlay\灵弈小窗.bat"; WorkingDir: "{app}\intelligent\ai\agent\overlay"
Name: "{group}\小窗截图"; Filename: "{app}\intelligent\ai\agent\overlay\截图.bat"; WorkingDir: "{app}\intelligent\ai\agent\overlay"
Name: "{group}\打开小窗日志目录"; Filename: "{app}\intelligent\ai\agent\overlay\logs"

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\_pkg\deploy.ps1"" -Lingyi ""{app}"""; WorkingDir: "{app}\_pkg"; StatusMsg: "正在部署到灵弈（备份 + 拷贝 + 环境自检）..."; Flags: waituntilterminated
Filename: "{app}\intelligent\ai\agent\overlay\灵弈小窗.bat"; Description: "立刻打开小窗（两个窗口）"; WorkingDir: "{app}\intelligent\ai\agent\overlay"; Flags: postinstall nowait skipifsilent unchecked
Filename: "{app}\intelligent\ai\agent\overlay\logs"; Description: "打开小窗日志目录"; Flags: postinstall nowait skipifsilent unchecked shellexec

[UninstallDelete]
; 只清我们放进去的部署包副本；灵弈本体和日志一律不动
Type: filesandordirs; Name: "{app}\_pkg"

[Code]
function LingyiDir(Param: String): String;
var
  cands: array[0..6] of String;
  i: Integer;
begin
  Result := 'D:\LingYi';
  cands[0] := ExpandConstant('{sd}\LingYi');
  cands[1] := 'D:\LingYi';
  cands[2] := 'C:\LingYi';
  cands[3] := 'E:\LingYi';
  cands[4] := 'F:\LingYi';
  cands[5] := 'D:\lingyi';
  cands[6] := 'C:\lingyi';
  for i := 0 to 6 do
    if FileExists(cands[i] + '\intelligent\new_env\ray210\python.exe') then
    begin
      Result := cands[i];
      Exit;
    end;
  for i := 0 to 6 do
    if DirExists(cands[i] + '\intelligent') then
    begin
      Result := cands[i];
      Exit;
    end;
end;

function IsLingyiRoot(Dir: String): Boolean;
begin
  Result := FileExists(Dir + '\intelligent\new_env\ray210\python.exe');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpSelectDir then
    if not IsLingyiRoot(WizardDirValue) then
      if MsgBox('这个目录里没找到 intelligent\new_env\ray210\python.exe：' + #13#10 + WizardDirValue + #13#10#13#10 + '请选到灵弈根目录（能看到 APlatformLobby.exe 的那一层）。仍然继续吗？', mbConfirmation, MB_YESNO) = IDNO then
        Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    // 统一布局后智能体入口都在 intelligent\ai\agent\（老包在 intelligent\ 根目录，两个位置都认）
    if not (FileExists(ExpandConstant('{app}\intelligent\ai\agent\overlay\launcher.py')) and
            FileExists(ExpandConstant('{app}\intelligent\ai\agent\overlay\wv2\overlay_wv2.exe')) and
            (FileExists(ExpandConstant('{app}\intelligent\ai\agent\Mission_all_red.py')) or
             FileExists(ExpandConstant('{app}\intelligent\Mission_all_red.py')))) then
      MsgBox('部署好像没成功：overlay\launcher.py / overlay\wv2\overlay_wv2.exe / Mission_all_red.py 至少缺一个。' + #13#10#13#10 + '请手工在 ' + ExpandConstant('{app}\_pkg') + ' 里双击 deploy.bat 再试一次，并把窗口里的 [FAIL] 行发回来。', mbError, MB_OK);
end;
