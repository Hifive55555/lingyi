#Requires -Version 5.0
<#
    一键部署：把本目录（最最新代码）里的代码装进灵弈。

    用法（目标机上）：
      1) 把「最最新代码」整个目录放到 <灵弈>\intelligent\ 下（目录名随意）
      2) 双击 deploy.bat；或
         powershell -NoProfile -ExecutionPolicy Bypass -File deploy.ps1
      3) 先看计划不落盘：deploy.bat -DryRun

    源文件按**文件名**找，不依赖「智能体代码 / 小窗」这两个目录名；
    改名、解压多套一层都能用。

    装到哪里（与灵弈的 agent_path 一致，实测 D:\LingYi）：
      <灵弈>\intelligent\Mission_all_red.py       主智能体（agent_path 指这一层）
      <灵弈>\intelligent\ai\engine\LingYi\        三个战术模块 + tools + 任务表
      <灵弈>\intelligent\ai\agent\                overlay_ai.py + overlay\

    不建虚拟环境、不联网装包：Python 只用灵弈自带的 ray210。
    部署完自动跑 check_env.py，不过就退出码 1（现场不修）。
#>
[CmdletBinding()]
param(
    [string]$Lingyi = '',
    [switch]$DryRun,
    [switch]$WithEntitys,
    [switch]$NoBackup,
    [switch]$SkipCheck,
    [switch]$SkipAgentConfig,
    [switch]$SkipShortcut
)

$ErrorActionPreference = 'Stop'
$Src   = $PSScriptRoot
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$script:n = 0

function Say($tag, $msg) { Write-Host ("[{0}] {1}" -f $tag, $msg) }

function Test-LingyiRoot($p) {
    if (-not $p) { return $false }
    return (Test-Path (Join-Path $p 'intelligent\new_env\ray210\python.exe'))
}

# ---------------- 1. 找灵弈根 ----------------
$cands = New-Object System.Collections.ArrayList
if ($Lingyi) { [void]$cands.Add($Lingyi) }
$d = $Src
for ($i = 0; $i -lt 5; $i++) {
    [void]$cands.Add($d)
    [void]$cands.Add((Split-Path $d -Parent))
    $d = Split-Path $d -Parent
    if (-not $d) { break }
}
foreach ($r in @('D:\LingYi', 'C:\LingYi', 'E:\LingYi', 'F:\LingYi')) { [void]$cands.Add($r) }

$LY = $null
foreach ($c in $cands) {
    if (Test-LingyiRoot $c) { $LY = (Resolve-Path $c).Path; break }
}
if (-not $LY) {
    Say 'STOP' '找不到灵弈安装目录（其下应有 intelligent\new_env\ray210\python.exe）'
    Say 'INFO' ('已尝试：' + (($cands | Where-Object { $_ } | Select-Object -Unique) -join '  '))
    Say 'INFO' '用 -Lingyi "X:\灵弈目录" 指定，例如：'
    Say 'INFO' 'powershell -ExecutionPolicy Bypass -File deploy.ps1 -Lingyi "E:\LingYi"'
    exit 1
}

$LYInt  = Join-Path $LY 'intelligent'
$AI     = Join-Path $LYInt 'ai'
$EngDir = Join-Path $AI 'engine\LingYi'
$Agent  = Join-Path $AI 'agent'
$Tools  = Join-Path $EngDir 'tools'

Say 'OK' ('灵弈目录 : ' + $LY)
Say 'OK' ('包目录   : ' + $Src)
if ($DryRun) { Say 'DRY' '试运行：只打印计划，不改任何文件' }

# ---------------- 2. 按文件名定位源 ----------------
function Find-One($filter) {
    $hits = @(Get-ChildItem -Path $Src -Filter $filter -File -Recurse -ErrorAction SilentlyContinue |
              Where-Object { $_.FullName -notmatch '[\\\/](entitys|\.venv|logs|__pycache__)[\\\/]' } |
              Sort-Object FullName)
    if ($hits.Count -eq 0) { return $null }
    if ($hits.Count -gt 1) { Say 'WARN' ("$filter 有 $($hits.Count) 份，用 " + $hits[0].FullName) }
    return $hits[0]
}

$redFile = Find-One 'Mission_all_red.py'
if (-not $redFile) { Say 'STOP' '包里找不到 Mission_all_red.py'; exit 1 }
$AgentsDir = $redFile.DirectoryName

$ovFile = Find-One 'overlay_ai.py'
if (-not $ovFile) { Say 'STOP' '包里找不到 overlay_ai.py（小窗入口）'; exit 1 }
$OvDir  = $ovFile.DirectoryName
$OvPkg  = Join-Path $OvDir 'overlay'
if (-not (Test-Path (Join-Path $OvPkg 'agent.py'))) {
    Say 'STOP' ('overlay_ai.py 同层缺少 overlay\agent.py：' + $OvPkg); exit 1
}
$ToolsDir = Join-Path $AgentsDir 'tools'

Say 'INFO' ('源-智能体 : ' + $AgentsDir)
Say 'INFO' ('源-小窗   : ' + $OvDir)

# ---------------- 3. 拷贝 ----------------
function Copy-One($from, $toDir, $label) {
    if ($from -is [System.IO.FileInfo]) { $from = $from.FullName }
    $name = [System.IO.Path]::GetFileName($from)
    $to   = Join-Path $toDir $name
    $script:n++
    if ($DryRun) {
        $flag = if (Test-Path $to) { '覆盖' } else { '新建' }
        Say 'DRY' ('{0,-10} {1,-26} {2}' -f $label, $name, $flag)
        return
    }
    if (-not (Test-Path $toDir)) { New-Item -ItemType Directory -Force $toDir | Out-Null }
    if ((Test-Path $to) -and (-not $NoBackup)) { Copy-Item $to ($to + '.bak_' + $stamp) -Force }
    Copy-Item $from $to -Force
    Say 'CP' ('{0,-10} {1}' -f $label, $to)
}

Say 'INFO' '--- ① 主智能体 -> <灵弈>\intelligent\ai\agent\ ---'
# 统一布局：所有智能体入口（Mission_all_red.py / Mission_all_blue_hh.py / overlay_ai.py）
# 都放 ai\agent\。平台跑智能体时本来就会把 intelligent\ai 和 intelligent\ai\agent
# 都加进 sys.path（见 ai\config\<agent>\log 旁边的 boot 记录），所以
# `from engine.LingYi.xxx import ...` 这条引用照旧成立，不需要改智能体代码。
Get-ChildItem $AgentsDir -Filter 'Mission_all_*.py' -File | Sort-Object Name | ForEach-Object {
    Copy-One $_.FullName $Agent 'agent'
}

Say 'INFO' '--- ② 战术模块 / 任务表 -> ai\engine\LingYi\ ---'
foreach ($f in @('BattlefieldMonitor.py', 'SamBattalionDefense.py', 'ShipClusterDefense.py',
                 '红方人人任务列表.xlsx', '蓝方人人任务列表.xlsx',
                 '红方人人总任务.txt', '蓝方人人总任务.txt', '战术智能体说明.md')) {
    $p = Join-Path $AgentsDir $f
    if (Test-Path $p) { Copy-One $p $EngDir 'module' }
}

Say 'INFO' '--- ③ 自检脚本 -> ai\engine\LingYi\tools\ ---'
if (Test-Path $ToolsDir) {
    # 只拷脚本与说明（tools 里还放着一份报告素材 txt，不是工具）
    Get-ChildItem $ToolsDir -File | Where-Object { $_.Extension -in @('.py', '.md') } |
        Sort-Object Name | ForEach-Object {
        Copy-One $_.FullName $Tools 'tool'
    }
} else {
    Say 'WARN' ('包里没有 tools 目录：' + $ToolsDir)
}

Say 'INFO' '--- ④ 小窗 -> ai\agent\ ---'
Copy-One $ovFile $Agent 'overlay'
Get-ChildItem $OvPkg -File | Sort-Object Name | ForEach-Object {
    Copy-One $_.FullName (Join-Path $Agent 'overlay') 'overlay'
}
$web = Join-Path $OvPkg 'web'
if (Test-Path $web) {
    Get-ChildItem $web -File | Sort-Object Name | ForEach-Object {
        Copy-One $_.FullName (Join-Path $Agent 'overlay\web') 'web'
    }
}

Say 'INFO' '--- ⑤ 小窗宿主 WebView2 -> ai\agent\overlay\wv2\ ---'
$wv2src = Join-Path $OvPkg 'wv2'
if (Test-Path $wv2src) {
    foreach ($f in @('overlay_wv2.exe', 'host.cs', 'Microsoft.Web.WebView2.Core.dll',
                     'Microsoft.Web.WebView2.WinForms.dll', 'WebView2Loader.dll', '构建说明.md')) {
        $p = Join-Path $wv2src $f
        if (Test-Path $p) { Copy-One $p (Join-Path $Agent 'overlay\wv2') 'wv2' }
    }
    if (-not (Test-Path (Join-Path $wv2src 'overlay_wv2.exe'))) {
        Say 'WARN' 'wv2 里缺少 overlay_wv2.exe，小窗会退回 msedge --app（在这台机上会灰屏）'
    }
} else {
    Say 'WARN' ('包里没有 wv2 目录：' + $wv2src + '（小窗将退回 msedge --app）')
}

if ($WithEntitys) {
    Say 'INFO' '--- ⑥ 平台库 entitys ---'
    $srcEnt = Join-Path $AgentsDir 'entitys'
    $dstEnt = Join-Path $EngDir 'entitys'
    if (-not (Test-Path $srcEnt)) {
        Say 'WARN' ('包里没有 entitys：' + $srcEnt)
    } elseif ($DryRun) {
        Say 'DRY' 'entitys 整目录 -> ' + $dstEnt
    } else {
        if (Test-Path $dstEnt) { Copy-Item $dstEnt ($dstEnt + '.bak_' + $stamp) -Recurse -Force }
        Copy-Item $srcEnt $dstEnt -Recurse -Force
        Say 'CP' 'entitys -> ' + $dstEnt
    }
} else {
    Say 'SKIP' 'entitys 不覆盖（默认用灵弈自带的；实测 model.db 版本一致，需要时加 -WithEntitys）'
}

Say 'OK' ('计划/完成 {0} 个文件（覆盖时备份后缀 .bak_{1}）' -f $script:n, $stamp)

if ($DryRun) {
    Say 'DRY' '试运行结束，未改动任何文件。去掉 -DryRun 即真正部署。'
    exit 0
}

# ---------------- 4. 环境自检 ----------------
$py    = Join-Path $LY 'intelligent\new_env\ray210\python.exe'
$check = Join-Path $Tools 'check_env.py'
Say 'INFO' '--- ⑦ 环境自检 check_env.py ---'
if ($SkipCheck) {
    Say 'SKIP' '按 -SkipCheck 跳过自检（正式部署不要跳过）'
} elseif (Test-Path $check) {
    & $py '-X' 'utf8' $check
    if ($LASTEXITCODE -ne 0) {
        Say 'STOP' '环境自检没过，部署中止（现场不修：比赛机无外网，装不了包）'
        Say 'INFO' '把上面 [FAIL] 行连同 <灵弈>\intelligent\new_env 的目录列表报上来'
        exit 1
    }
} else {
    Say 'WARN' ('没找到 ' + $check + '，跳过自检')
}

# ---------------- 4b. 预置两套智能体配置（overlay+蓝 / overlay+红） ----------------
# agentConfig.json 是「想定 id -> 阵营 id -> 智能体」三层，阵营 id 每份想定都不一样，
# 所以不写死，由 install_agent_config.py 现场判：已装 blue_hh 的那方=蓝方，另一方从
# 推演记录的 simulation.ini 里取。写之前自动备份。
if ($SkipAgentConfig) {
    Say 'SKIP' '按 -SkipAgentConfig 跳过智能体配置预置'
} else {
    $cfgpy = Join-Path $Tools 'install_agent_config.py'
    Say 'INFO' '--- ⑧ 预置智能体配置（overlay+蓝 / overlay+红）---'
    if (Test-Path $cfgpy) {
        # ① 直接合并进 agentConfig.json（装完不用选就能用）
        # ② 另存两份 json 到 config\，客户端里可用「导入智能体配置文件」手动导入
        $cfgOut = Join-Path $LYInt 'config'
        # 注意：绝对不要加 --relative —— 客户端用 dirname(filePath) 当 agent_path 写 sys.path，
        # 相对路径会让它退回 ai\agent，import 时 ModuleNotFoundError。
        & $py '-X' 'utf8' $cfgpy '--root' $LY '--export' $cfgOut
        if ($LASTEXITCODE -ne 0) {
            Say 'WARN' '配置预置没成功（不影响智能体本身）；按上面提示在客户端里手动加一次即可'
        }
    } else {
        Say 'WARN' ('没找到 ' + $cfgpy)
    }
}

# ---------------- 4.5 桌面快捷方式（按本机真实路径生成）----------------
# 不随包发 .lnk：.lnk 里是绝对路径，换台机器/换个安装盘就废了。
# 这里用 overlay 里的 创建快捷方式.ps1 就地生成 —— 它按自己所在目录推路径。
if ($SkipShortcut) {
    Say 'SKIP' '按 -SkipShortcut 跳过创建快捷方式'
} else {
    Say 'INFO' '--- ⑨ 创建桌面快捷方式（灵弈小窗 / 小窗截图）---'
    $mk = Join-Path $Agent 'overlay\创建快捷方式.ps1'
    if (Test-Path $mk) {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $mk -Quiet
        if ($LASTEXITCODE -eq 0) { Say 'OK' '快捷方式已按本机路径写好（可直接双击桌面「灵弈小窗」）' }
        else { Say 'WARN' '快捷方式没建成；进 overlay 目录双击 创建快捷方式.bat 手动补一次' }
    } else {
        Say 'WARN' ('没找到 ' + $mk)
    }
}

# ---------------- 5. 收尾 ----------------
Say 'OK' '部署完成。客户端里还要做（详见包内 README.md）：'
Say 'INFO' '  1) APlatformLobby.exe -> 单机版启动'
Say 'INFO' '  2) 想定 -> 加载想定（*.scen 先放进 <灵弈>\Data\Scenarios\）'
Say 'INFO' '  3) 推演 -> 推演速度 -> 5 倍速'
Say 'INFO' '  4) 智能体调度 -> 智能体编辑 -> "+" 导入 Mission_all_red.py（红方、勾规则智能体）'
Say 'INFO' '  5) 同一个 "+" 再导入 agent\overlay_ai.py（类名 Agent），两者都点启动'
Say 'INFO' '  6) 双击 agent\overlay\灵弈小窗.bat，热键 Alt+Q / Alt+W / Alt+E'
Say 'INFO' '  7) 开局后日志搜 AGENT_BUILD=2026-11-09-RED-21 确认版本'
exit 0
