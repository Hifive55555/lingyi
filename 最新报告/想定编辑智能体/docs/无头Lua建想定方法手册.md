# 无头模式下用 Lua 编写想定的方法（实测版）

> 环境：靶机 `10.42.97.205`（HIFIVE-ASUS / Win11 22631），灵弈 `D:\LingYi`，引擎 build **1276.1**，DB `DB3K_480`
> 记录时间：2026-11-17 晚 · 本文所有结论都来自**实机运行**，未验证的地方单独标注
> 阅读对象：要让智能体「自己写想定」的人。第 9 节是坑表，急用可以直接跳到那里

---

## 0. 一句话结论

想定可以**完全用 Lua 脚本在无头（无界面）模式下生成**，链路是：

```
Session 1 里起 Plat.exe（12 参数形态）
   ↓  21001 明文 h2c gRPC
executeLua("<Lua 脚本>")        ← 一条条语句下发，用 AddXxx 的返回值抓 GUID
   ↓
Command_SaveScen("D:/LingYi/Data/Scenarios/xxx.scen")
   ↓
GetScenarioContent("xxx.scen")  ← 让引擎把 .scen 解压成 XML，自己回读验收
```

一份 10 单元 / 2 任务的小想定，从建到验收 **3~5 秒**；官方 251 单元的诺曼底复刻也只要 **19~24 秒**。

---

## 1. 前置条件：引擎必须活在 Session 1

`Plat.exe` 是 **Qt 控制台程序**，即使没有可见窗口，也必须能创建窗口站/消息队列。
`sshd` 落在 **Session 0**（无交互桌面），在那里起引擎的表现是：
进程存在、CPU 0、**永远不监听 21001**，日志里是

```
CreateWindow() for QEventDispatcherWin32 internal window failed (拒绝访问。)
Qt: INTERNAL ERROR: failed to install GetMessage hook: 5
```

所以统一用「**计划任务 + `-LogonType Interactive`（用 SID）+ `RunLevel Highest`**」把启动动作投递到 Session 1：

```powershell
$sid  = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value   # 必须用 SID，不能用 域\用户名
$act  = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c D:\LingYi\Data\lyengine\pi_sce_engine_21005.bat'
$prin = New-ScheduledTaskPrincipal -UserId $sid -LogonType Interactive -RunLevel Highest
$set  = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 720)
Register-ScheduledTask -TaskName PiSceEngine21005 -Action $act -Principal $prin -Settings $set -Force
Start-ScheduledTask     -TaskName PiSceEngine21005
```

确认桌面在：`query session` 里 `console ... Active`（本机是 Session 1）。

> 本文所有引擎操作都由仓库里的 `sce_agent/engine.py` 自动完成（含注册任务、探活、清理）。

---

## 2. 引擎启动参数：12 参数形态（关键）

实测**能用**的形态（由 Python 框架 `GameConnectLocal` 拉起的进程命令行反推得到）：

```bat
cd /d D:\LingYi\Data\lyengine
Plat.exe <房间GUID> 127.0.0.1 21001 22001 0 127.0.0.1 0 0 127.0.0.1 0 "" <房间名>
```

实测**不能用**的形态（官方样例 `Data\lyengine\run.bat`，11 参数）：

```bat
plat.exe a1d7edb5-... 127.0.0.1 21001 22001 0 127.0.0.1 20001 0 127.0.0.1 6379 t~Aa~wGYc5gm zjh03
```

| 形态 | 结果 |
| --- | --- |
| 12 参数（`<guid> ... 0 127.0.0.1 0 0 127.0.0.1 0 "" <room>`） | **7~8 秒**开始监听 21001/22001，RPC 正常 |
| 11 参数（`LOCAL/…/20001/6379/密码` 那一版） | 进程常驻、CPU 0、**永不监听**，日志无有效信息 |
| 客户端 `APlatform.exe` 拉起的引擎 | 监听 21001，但走 **TLS + HTTP/2**（自签 `CN=MyCA`），明文连会 `End of TCP stream` |

`lsengine\Config\Server.ini` 里的 Redis 连不上只会刷日志（`获取Redis连接失败`），**不影响 RPC**，建想定不需要 Redis。
监听地址是 `0.0.0.0`，所以**可以从局域网另一台机器直接连**（本文的实验就是 NixOS → 靶机）。

---

## 3. 连接：gRPC `executeLua`

### 3.1 生成桩代码

靶机上已有 `D:\LingYi\intelligent\ai\proto\ServerInterface.proto`（140 KB，244 个 rpc，无外部 import）。
任意机器上：

```bash
python -m grpc_tools.protoc -I proto --python_out=gen --grpc_python_out=gen proto/ServerInterface.proto
```

### 3.2 最小客户端

```python
import grpc
from gen import ServerInterface_pb2 as pb2, ServerInterface_pb2_grpc as pb2g

ch = grpc.insecure_channel("10.42.97.205:21005", options=[
    ("grpc.max_receive_message_length", 256*1024*1024),
    ("grpc.enable_http_proxy", 0),          # 本机有 http_proxy 时必加，否则 grpc 会走代理
])
stub = pb2g.SimRpcStub(ch)
r = stub.executeLua(pb2.RequestExecuteLua(script="GetBuildNumber()"), timeout=30)
print(r.code, r.result.decode())            # 0  1276.1
```

`Reply = {code, result}`：`code==0` 成功；`code!=0` 时 `result` 是错误文本（中文）。

### 3.3 ★ 返回值机制：只有**字符串**能带回来

这是本方法最反直觉的一点，实测结论：

| 接口返回机制 | executeLua 里能不能拿到 | 例子 |
| --- | --- | --- |
| M1 字符串（`SET_RUNRESULT(字符串)`） | **能** | `GetSides()` `GetUnit()` `AddUnit()` `AddMission()` `GetScenarioContent()` |
| M2/M5 Lua 表（JSON 或 table） | **拿不到（返回空串）** | `QueryDB("ship",2296)`、`GetMissions()`、`GetWeather()`、`GetDoctrine()` |
| M4 原生 int/bool | **拿不到（返回空串）** | `GetScenarioRunState()`、`CurrentTime()`、`SetSidePosture()` 的 true |

推论（很重要）：

1. **不要指望 `QueryDB`** —— 要查 DB 用命名 RPC `queryDatabase`（见 §4.1）；
2. `SetSidePosture` / `SetSideOptions` / `SetDoctrine` / `AssignUnitListToMission` 这类"动作"接口
   返回空串是**正常**的，判成功只看 `code==0`，真正的效果要**回读 XML 验收**；
3. 需要"读回结构化数据"时，统一走命名 RPC 或 `GetScenarioContent` 的 XML。

### 3.4 `local` 变量不跨调用

每次 `executeLua` 是一个**独立的 Lua chunk**，`local` 变量不会保留。因此：

* 想要"一条脚本跑完整流程" → 把整段脚本**一次**发过去（自包含，见 §7.2）；
* 想要"逐条下发、逐条抓 GUID"（推荐，错误定位好）→ 由**客户端记住 GUID**，在下一条里以字面量拼进去。
  仓库里 `lua_gen.py` 就是这么做的：分块脚本里写 `%{S:红方}` 占位符，执行完上一块用真实 GUID 回填。

### 3.5 一条脚本里塞多条语句有风险

实测：`SetStartTime(...); SetTime(...)` 这种"两句一起发"会直接
`UNKNOWN: Unexpected error in RPC handling`（引擎里抛了未捕获异常）。
**一条语句一次调用**最稳，也最利于定位。

---

## 4. 命名 RPC：Lua 拿不到的东西从这里拿

`ServerInterface.proto` 里 244 个命名 RPC 是"带类型的通道"，比 Lua 字符串更可靠：

| 用途 | RPC | 实测返回 |
| --- | --- | --- |
| **查 DBID 是什么平台** | `queryDatabase{objectType,dbid}` | `unit { type='2', subtype='3203', class='DDG 113"约翰.芬"阿里伯克级…' }`；不存在时 `code=1, result="No ship with ID: 1 was found…"` |
| **查地形高程（陆地/水面）** | `getElevation{latitude,longitude}` | `"12.5"`（米，>0 陆地，<=0 水面） |
| 回读想定 XML | `getScenarioContent{scenName}` | `<Scenario>…</Scenario>`（引擎自己解压 `.scen`） |
| 想定初始态势 | `getInitSituation`（stream） | `THSituationFull` 的 JSON（含全部单元/传感器/挂载） |
| 想定列表 | `getScenarioList` | JSON |
| 加载想定 | `loadScenario{scenName,loadScheme}` | 比 Lua 的 `LoadScenario` 安全（后者传错参会把引擎搞崩） |

`queryDatabase` 是**DBID 知识库的唯一权威来源**。实测：同一个 `dbid=173` 在本机 DB 里是
「PSKR 司腾卡巡逻艇」，而某些文档写的是 052D —— **DBID 会随 DB 版本漂移，禁止硬编码**。
（本仓库用一次全量扫描把 13 203 个平台类目落到 `sce_agent/data/db_catalog.json`，见 `cli.py catalog scan`。）

---

## 5. 想定文件 `.scen` 的结构（不要自己解压）

`.scen` = **UTF-8 明文外壳 + 压缩体**：

```xml
<ScenContainer>
  <DBVersion>DB3K_480.db3</DBVersion>
  <Scenario_Compressed>EAAAAKu5Vex…</Scenario_Compressed>   <!-- 高熵，解不开 -->
  <ScenTitle>海洋空战</ScenTitle><Complexity>1</Complexity>…
</ScenContainer>
```

压缩体用 zlib / lz4(block,frame) / zstd / lzma / 7z + 偏移暴破**全部失败**（前 4 字节 `10 00 00 00` 后即高熵）。
正确做法：**让引擎解** —— `GetScenarioContent('x.scen')` 返回完整 `<Scenario>` XML（海洋空战解出 234 934 字节）。

### 5.1 `<Scenario>` XML 里要知道的几件事

```xml
<Scenario>
  <Title> <Description> <StartTime> <Duration> …        <!-- Duration 单位是 100ns ticks（3600s = 3.6e10） -->
  <Sides>
    <Side>
      <ID> <Name> <IsAIOnly>
      <Postures><Posture_<对方GUID>>3</Posture_…></Postures>   <!-- N=0 F=1 U=2 H=3 -->
      <Doctrine><WCS_Air>1</WCS_Air>…
      <ReferencePoints><RPoint><ID><Lon><Lat><Name></RPoint>…</ReferencePoints>
      <Missions>                                            <!-- ★ 任务是挂在 Side 下面的 -->
        <Patrol><ID><Name><Type>2</Type><AssignedUnitsList><ID>…
                <PatrolArea><RPoint><ID>…
        <Strike>…
      </Missions>
    </Side>
  </Sides>
  <ActiveUnits><Aircraft><ID><Name><Side><DBID><Lon><Lat><DA 高度><CH 航向><Loadout>…
              <Ship> <Submarine> <Facility> <Satellite>
  <GlobalWeather><WeatherProfile><Temp><RFR 降雨><FUR 云量><SS 海况>
</Scenario>
```

* **任务类型码**（实测，`<Type>`）：

  | 大类 | 码值 |
  | --- | --- |
  | Patrol | 0=SUB 1=NAVAL 2=AAW 3=LAND 5=SEAD 6=SEACONTROL |
  | Strike | 0=AIR_INTERCEPT 1=LAND 2=NAVAL 3=SUB_STRIKE |

* **姿态码**：`<Posture_<对方GUID>>` 的取值 **N=0 F=1 U=2 H=3**（早期误判为 F=2/U=1，实测纠正）。
* **时间**：客户端做的想定 `StartTime` 是 .NET ticks（如 2020-04-16 → `637226712000000000`）；
  脚本新建的想定是负值哨兵（`-8584…`），**两种都能跑**，不要拿它做判断。
* `AssignedMission` 字段是**任务 GUID**，不是任务名。

---

## 6. 建想定的标准调用序列（实测通过）

```
NewScenario('','')                       -- 必须先于一切场景读写；返回想定 GUID
SetScenarioInfo{TITLE,DURATION,COMPLEXITY,DIFFICULTY,SEED,DESCRIPTION(Base64 HTML)}
AddSide{side='红方'} ×N                   -- 返回推演方 GUID
SetSidePosture(A,B,code) 两两双向         -- H/F/N/U，**必须双向显式设置**
SetSideOptions{side,CAMERALON,CAMERALAT,CAMERAALT}   -- 每个推演方都要设，否则推演界面黑屏
SetDoctrine({side=X},{WCS_Air='1',…})     -- 参数 1 是推演方表，参数 2 才是条令表
SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)        -- 位置参数，不是 table
AddUnit{side,type,name,dbid,latitude,longitude,alt,heading,count,base,loadoutid}  -- 返回 GUID
AddMission('方','任务名','Patrol',{isactive=true,type='NAVAL',unloadMountDBID=0.0,unloadMountCount=0.0})
                                         -- 返回 "mission {guid = 'X',name = 'Y'}"
AddReferencePoint{side,guid,lat,lon,highlighted}      -- guid 由客户端生成 UUID，字段是 lat/lon
SetMission('方', 任务GUID, {patrolZone={参考点GUID…},…})  -- 巡逻区只能这样绑
AssignUnitListToMission('GUID1,GUID2', 任务GUID, false)  -- 三参必须是 GUID、GUID、bool
Command_SaveScen('D:/LingYi/Data/Scenarios/xxx.scen')   -- 完整路径；返回 Scenarios/xxx.scen
```

一次真实执行（`out/EXP1-东海反舰遭遇战/build.json` 摘录，31 条语句 / 4.4 秒）：

```
info    NewScenario('','')                                    -> 'PR-00001K7KNG7G9'
info    SetScenarioInfo({TITLE='东海反舰遭遇战', DURATION=10800, …})  -> '设置成功'
sides   AddSide({side='红方'})                                -> 'PR-00001K7KNG7GA'
sides   AddSide({side='蓝方'})                                -> 'PR-00001K7KNG7GB'
setup   SetSidePosture('PR-…GA','PR-…GB','H')                 -> ''
setup   SetSideOptions({side='PR-…GA', CAMERALON=124.2384, CAMERALAT=28.4293, CAMERAALT=1373979.0}) -> ''
units   AddUnit({… type='Ship', name='红方 052D #1', dbid=2296.0, latitude='28.500000', …c
count=2.0})                                                   -> 'PR-…,PR-…'   （count>1 返回逗号分隔多 GUID）
missions AddMission('PR-…','红方-反舰巡逻','Patrol',{isactive=true,type='NAVAL',…})
                                                              -> "mission {guid = 'PR-…',name = '红方-反舰巡逻'}"
zones   AddReferencePoint({side='PR-…', guid='120e4883-…', lat=28.96, lon=122.37, highlighted=true})
zones   SetMission('PR-…','PR-…',{patrolZone={'120e4883-…',…},unloadMountDBID=0.0,unloadMountCount=0.0})
assign  AssignUnitListToMission('PR-…,PR-…','PR-…',false)
save    Command_SaveScen('D:/LingYi/Data/Scenarios/EXP1-东海反舰遭遇战.scen')  -> 'Scenarios/EXP1-东海反舰遭遇战.scen'
```

随后回读 `GetScenarioContent('EXP1-东海反舰遭遇战.scen')` = 39 320 字节 .scen / 242 KB XML，可解析出
2 方 / 10 平台 / 2 任务 / 8 参考点。

### 6.1 单元（`AddUnit`）的硬约束（都实测过）

| 约束 | 现象 |
| --- | --- |
| 舰船/潜艇不能放陆地 | `你不能把船放在陆地上！` |
| 设施不能放水面 | `此点在水下!` |
| 飞机**必须**带 `loadoutid` 键 | 缺键 → `缺少挂载！`；传 `loadoutid=0.0` 合法（无武装） |
| **`loadoutid=0` 的飞机无法编入任务** | `AssignUnitListToMission` 会把这个单元的 GUID 当失败项返回；`loadoutid=3`（内置"预备飞行[可用]"）对所有机型可编入任务 |
| 飞机"基地模式"（`base=机场GUID`） | 飞机加到基地上（`count` 批量），但**同样编不进任务**（不处于出动状态）→ 想定里更实用的是"空中带挂载" |
| `type` 首字母大写 | `Aircraft` / `Ship` / `Submarine` / `Facility` / `Satellite` |
| `dbid` 传浮点、经纬度传字符串 | 与文档一致，照抄即可 |

**挂载方案（`loadoutid`）从哪来**：`<Loadout><Loadout><DBID>` 是从想定 XML 里读出来的；
本仓库把 17 份官方/竞赛想定里的 `(机型 DBID → 挂载方案 DBID + 名称)` 统计成 `sce_agent/data/loadouts.json`（156 个机型），
再按任务角色**语义匹配**（反舰/对地/空空/反潜/预警/电子战），匹配不到才退到 `3`。

### 6.2 任务（`AddMission` + `SetMission`）

* `AddMission` 只认 `isactive` / `type`（子类型）/ `unloadMountDBID` / `unloadMountCount`；
  **`patrolZone`/`waypoints`/`ZONE` 会被静默忽略** —— 巡逻区必须
  `AddReferencePoint`（4~5 个点、顺时针、UUID 自己生成）+ `SetMission{patrolZone={GUID…}}` 绑定。
* `Strike` 任务**没有巡逻区**（`SetMission` 的 `patrolZone` 对它无效）。
* 实测经验（与厂商手册一致）：**AI 版想定尽量用 `Patrol`**——引擎初期没有敌方情报，
  `Strike` 没有目标就不行动。本仓库的解析器默认把"打击"折算成等价 `Patrol`（可在 `RuleParser(strike_as_patrol=False)` 关掉）。
* `AssignUnitListToMission` 第一参是**逗号分隔的单元 GUID**，第二参是**任务 GUID**，第三参必须给（`false`）。

### 6.3 推演方（`AddSide` + 姿态 + 视点）

* 两两姿态**必须双向**都设（A→B、B→A），否则引擎里是默认的"不友好"，AI 不会开火。
* **每个推演方都要 `SetSideOptions` 设相机**，否则该方在推演界面看不到画面。
  高度经验值：`max(纬度跨度, 经度跨度) × 111000 × 2.5`（米）。

---

## 7. 三种下发方式与取舍

### 7.1 逐条下发 + 客户端回填 GUID（推荐）

每条语句一次 `executeLua`，`local` 变量由客户端记忆。优点：错误定位到**单条 Lua**、
每条 `AddXxx` 的 GUID 直接拿到、失败可断点续跑。缺点：语句多时 RTT 累积（本机 ~10 ms/条，200 条 ≈ 2 s）。

### 7.2 自包含单脚本

用 `local` + `string.match` 自己抓 GUID，一次发完（也能直接贴进引擎控制台给人看）：

```lua
local S1 = AddSide({side='红方'})
local S2 = AddSide({side='蓝方'})
SetSidePosture(S1, S2, 'H'); SetSidePosture(S2, S1, 'H')
local U1 = AddUnit({side=S1, type='Ship', name='052D-1', dbid=2296.0,
                    latitude='26.05', longitude='122.10', heading=90})
local M1 = AddMission('红方','反舰巡逻','Patrol',
                      {isactive=true,type='NAVAL',unloadMountDBID=0.0,unloadMountCount=0.0})
local MG = string.match(M1, "guid = '([^']+)'")
AddReferencePoint({side=S1, guid='11111111-1111-4111-8111-111111111111', lat=26.4, lon=121.8, highlighted=true})
AddReferencePoint({side=S1, guid='22222222-2222-4222-8222-222222222222', lat=26.4, lon=122.4, highlighted=true})
AddReferencePoint({side=S1, guid='33333333-3333-4333-8333-333333333333', lat=25.9, lon=122.4, highlighted=true})
AddReferencePoint({side=S1, guid='44444444-4444-4444-8444-444444444444', lat=25.9, lon=121.8, highlighted=true})
SetMission(S1, MG, {patrolZone={'11111111-1111-4111-8111-111111111111','22222222-2222-4222-8222-222222222222',
                                '33333333-3333-4333-8333-333333333333','44444444-4444-4444-8444-444444444444'},
                    unloadMountDBID=0.0, unloadMountCount=0.0})
AssignUnitListToMission(U1, MG, false)
Command_SaveScen('D:/LingYi/Data/Scenarios/demo.scen')
```

> 注意：多语句一次下发在个别 API 上会触发引擎未捕获异常（§3.5），所以这条路径适合"一次成型"，
> 不适合反复调试。

### 7.3 Python 框架（`Deduction` / `GameServer.api_*`）

`D:\LingYi\intelligent\ai\engine\LingYi\entitys\gameenvs\gameconnect_local.pyd` 会自己拉起引擎
（就是它给的 12 参数形态），`Deduction.reset()` 一次 `reset=1` 大约 **7~10 秒**。
优点：和比赛同链路，能直接跑推演拿 `BatResult`；缺点：**它会按进程名清理 `Plat.exe`**，
会把你在别的端口起的建想定引擎一起杀掉（实测两次）。

→ 结论：**建想定用本文的直连方式，跑推演用框架，两者串行**（本仓库 CLI 已自动化这一步）。

---

## 8. 回读验收（必须做）

因为 §3.3 的"只有字符串能回来" + §9 的一堆"静默忽略"，**下发成功 ≠ 想定正确**。
标准做法：`GetScenarioContent(name)` → 解析 XML → 与预期逐项比对（单元/坐标/DBID/任务/巡逻区/姿态/气象）。

本仓库 `sce_agent/verify.py` 的验收项：文件落盘、可回读、标题、时长、推演方集合、两两姿态、
兵力分布、单元名/DBID/坐标（±0.002°）、任务名/类型/子类型、巡逻区顶点数、单元-任务分配数、
条令（已知不持久化 → 只 WARN）、气象。

---

## 9. 坑表（全部实测）

| # | 坑 | 现象 | 解法 |
| --- | --- | --- | --- |
| 1 | Session 0 起引擎 | 进程在、CPU 0、永不监听 21001 | 计划任务 `-LogonType Interactive`（SID）投递到 Session 1 |
| 2 | `run.bat` 的 11 参数形态 | 同上（挂着不动） | 用 12 参数形态 `<guid> …"" <room>` |
| 3 | 客户端拉起的引擎是 TLS | 明文连 `End of TCP stream` | 要么用本文的明文引擎，要么 `ssl_target_name_override='MyCA'` + 关 http_proxy |
| 4 | grpc 走系统代理 | 连到 `127.0.0.1:7891`、`Hostname Verification failed` | `('grpc.enable_http_proxy', 0)` |
| 5 | **`SetScenarioInfo{STARTTIME=…}`** | 想定加载正常，但推演第 1 步就结束（`sim_time≈2.26e7 s`）——引擎的 Time/ZeroHour/StartTime 三者对不上 | **不下发 STARTTIME**（作战时间只写进简报/规格）；不下发时 30 步跑满 150 s |
| 6 | `SetStartTime{…}` | `UNKNOWN: Unexpected error in RPC handling`（引擎抛异常） | 别用 |
| 7 | `loadoutid` 缺键 | `缺少挂载！` | 飞机一律带 `loadoutid`（无武装写 `0.0`） |
| 8 | `loadoutid=0` 的飞机 | 能加入想定但**编不进任务**（返回值是该单元 GUID） | 用真实挂载方案；查不到就用内置 `3`（预备飞行） |
| 9 | 舰船落陆 / 设施落水 | `你不能把船放在陆地上！` / `此点在水下!` | 先用 `getElevation` 探高程，落错侧就按同心环吸附到最近合法点 |
| 10 | `LoadScenario('x.scen')` 传字符串 | 引擎抛异常后 RPC 崩 | `LoadScenario({PATH='x.scen'})`；或用 RPC `loadScenario` |
| 11 | `GetScenarioContent('x')` 不带后缀 | `加载想定失败` | 必须 `'x.scen'` |
| 12 | `SetScenarioInfo.DESCRIPTION` | 传原文变乱码 | **单次 Base64**（HTML 简报内容）；客户端 UI 保存时才出现"两次"编码 |
| 13 | `GetMissions()` / `GetMissions('红方')` | 空参 → `Unexpected error`；带方名 → **DEADLINE_EXCEEDED，引擎被打僵** | **别调**；用 `AddMission` 的返回值抓任务 GUID |
| 14 | `QueryDB(...)`（Lua） | 永远返回空串 | 用 RPC `queryDatabase` |
| 15 | 多语句一次 executeLua | 个别组合 `Unexpected error in RPC handling` | 一条语句一次调用 |
| 16 | `local` 变量跨调用 | 第二条语句里 `S1` 是 nil | 客户端记住 GUID，或整段一次发 |
| 17 | `SetDoctrine` | `code=0` 但**保存后回读仍是默认值**（试过 `'0'`/`0`/`'2'`） | 接受现状：条令在验收里降级为 WARN；换引擎版本再复核 |
| 18 | `Strike` + `patrolZone` | `SetMission` 成功但任务无巡逻区 | Strikes 没有巡逻区概念；AI 版想定统一用 `Patrol` |
| 19 | `.bat` 里传中文参数 | cmd 按 GBK 读，想定名变乱码（`娴锋磱绌烘垬`） | 参数走 UTF-8 的 JSON 文件，`.bat` 只留 ASCII |
| 20 | 单条 ssh 命令行 ~8 KB | 大 base64 上传变空/报"命令行太长" | 分块上传，每块 ≤2000 个 base64 字符 |
| 21 | 框架跑推演 | 按进程名清理 `Plat.exe`，把建想定引擎一起杀掉 | 建想定与冒烟**串行** |
| 22 | 连续两次 `LoadScenario` | 偶发引擎崩 | 一局一引擎；崩溃后重启（`cli.py engine start --force`） |

---

## 10. 复现清单（5 分钟）

```bash
cd 最新报告/想定编辑智能体
uv venv .venv && uv pip install -r requirements.txt        # grpcio / grpcio-tools / protobuf
python cli.py engine status                                # 看靶机 Session1 / Plat / 端口
python cli.py engine start                                 # 无头拉起（~8 s）
python cli.py catalog verify                               # 用引擎复核 85 条平台别名
python cli.py nl examples/nl/01-东海反舰遭遇战.md --build --smoke
python cli.py family out/EXP1-东海反舰遭遇战/spec.json --axis force_scale=0.5,1,2 --axis rotate=0,45
```

`--smoke` 会用官方框架真的把想定推 30 步（约 20~30 s），并给出 `reset/steps/sim_time`。
