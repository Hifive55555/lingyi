# AGENTS.md —— 改这个仓库前必须知道的硬约束

> 给 AI 编码助手（Claude Code / Codex / Cursor / pi…）和接手的人看。
> **违反下面任何一条，代码能跑但部署会坏，而且坏在比赛机上、没时间内查。**
> 本文件是可执行的契约，不是介绍；读完后按第 5 节跑验证命令，全绿才算改完。

---

## 0. 三十秒认识这个仓库

灵弈兵棋推演的**规则智能体 + 小窗**。三个进程/组件：

| 组件 | 位置 | 作用 |
| --- | --- | --- |
| 两个规则智能体 | `智能体代码/Mission_all_red.py`（红）、`Mission_all_blue_hh.py`（蓝） | 战前规划 + 每决策周期下指令，跑在**灵弈引擎进程内** |
| 三个战术模块 | `智能体代码/BattlefieldMonitor.py` / `SamBattalionDefense.py` / `ShipClusterDefense.py` | 被上面两个 import（`from engine.LingYi.X import …`） |
| 灵弈小窗 | `小窗/overlay_ai.py` + `小窗/overlay/` | 独立 Python 进程：ws 收态势 → 网页小窗；自带 WebView2 宿主开两个窗口 |

部署形态（`deploy.ps1` 负责落地）：

```
<灵弈>\intelligent\ai\agent\            ← 智能体入口（三个 .py）+ overlay/ 小窗
<灵弈>\intelligent\ai\engine\LingYi\    ← 战术模块、任务表 xlsx/txt、tools/
<灵弈>\intelligent\config\agentConfig.json ← 客户端「智能体编辑」配置
```

架构与数据流细节、ws 快照字段、端口、日志路径 → `docs/架构与数据流.md`
与对面（决赛代码）协作、分支与合并规则 → `docs/协作与合并.md`

---

## 1. 七条不可违反的契约

### 1.1 `agentConfig.json` 里的 `filePath` 必须是**绝对路径**

平台 `start_ai_apply.py` 是这么干的：

```python
sys.path.append(agent_path)                    # agent_path = dirname(filePath)
importlib.import_module(agent_import_path)     # agent_import_path = 文件名去 .py
```

所以 `filePath` 写成相对路径 → `dirname` 为空 → `agent_path` 退回默认的
`intelligent\ai\agent` → `ModuleNotFoundError`。
**改配置只能用 `tools/install_agent_config.py`（默认绝对路径）；不要加 `--relative`。**

### 1.2 智能体入口必须在 `intelligent\ai\agent\`

平台跑智能体时把 `intelligent\ai` 和 `intelligent\ai\agent` 都加进 `sys.path`：

- 入口放 `intelligent\` 根目录 → 老布局能跑，但会与「入口统一」冲突，别退回去
- 入口放到别的子目录 → `from engine.LingYi.* import` 找不到 `engine` 包

因此 `deploy.ps1` ① 段把 `Mission_all_*.py` 拷到 `ai\agent\`，**不要**改成别的目录。

### 1.3 战术模块必须放 `ai\engine\LingYi\`，导入必须带同级兜底

```python
try:                                   # 平台运行环境
    from engine.LingYi.BattlefieldMonitor import BattlefieldMonitor
except ImportError:                    # 本地/离线自测：同目录 import
    from BattlefieldMonitor import BattlefieldMonitor
```

两段都要留：`tools/selftest_*.py` 与 `check_table*.py` 靠兜底在纯 Python 下跑。

### 1.4 编码与换行（Windows 老工具会按 ANSI 解码）

| 文件类型 | 编码 | 换行 |
| --- | --- | --- |
| `.ps1` / `.iss` | **UTF-8 with BOM** | **CRLF** |
| `.bat` | 任意 ASCII 安全编码 | **CRLF** |
| `.py` / `.md` / `.js` / `.html` / `.json` | UTF-8 无 BOM | LF 即可 |

`.ps1` 少了 BOM，PowerShell 5.1 会把中文按 GBK 解，脚本直接乱码报错；
`.iss` 少了 BOM，Inno Setup 编译报 `Text is not inside a section`。

### 1.5 不建虚拟环境、不联网装包

比赛机无外网。Python 只能用灵弈自带的：

```
<灵弈>\intelligent\new_env\ray210\python.exe      # 3.9.19 + aiohttp 3.9.5 + psutil 6.0.0
```

**禁止**新增第三方依赖（`pip install`、`requirements.txt`、`.venv/`）。
本机/CI 想跑脚本，用你自己的环境，但**落到部署包里的代码**必须只用标准库 + aiohttp + psutil。

### 1.6 小窗必须用自带 WebView2 宿主，不要退回 `msedge --app`

比赛机 `%LOCALAPPDATA%` 不可写，Edge 的默认 profile 建不出来 → `--app` 窗口纯灰、
标题停在 `127.0.0.1_/`（`0x80070005`）。所以：

- 渲染器 = `小窗/overlay/wv2/overlay_wv2.exe`（WinForms + WebView2，UDF 放 **exe 同级**）
- `launcher.py` 只在宿主缺失时才回退 `msedge --app`，那是兜底不是方案
- `check_env.py` 把小窗宿主 exe 缺失记为**硬失败**

改 `host.cs` 后必须重新编译（命令见 `小窗/overlay/wv2/构建说明.md`），
并把新的 `overlay_wv2.exe` **一起提交**（目标机没有编译器）。

### 1.7 安装包必须低权限运行

`installer/setup.iss` 是 `PrivilegesRequired=lowest`。
**不要**为了省事改成 `admin`：管理员/高完整性下 WebView2 的 UDF 会 `0x80070005`，小窗灰屏。

---

## 2. 目录 = 打包清单 = 部署映射，三处必须同时改

新增/移动一个文件，**三处都要动**，否则「本机能跑、装出来缺文件」：

| 要改的地方 | 作用 |
| --- | --- |
| `pack.py` 的 `REQUIRED` / `OPTIONAL` / `DIRS` | 进不进 `dist/*.zip` |
| `deploy.ps1` 对应段（①~⑥） | 解到目标机哪个目录 |
| `tools/check_env.py` ⑤ 段 | 部署后自检能不能发现缺失 |

`pack.py` 的 `BAD_DIR_NAMES` 会剔除 `__pycache__ / logs / .venv / entitys /
overlay_wv2.exe.WebView2 / build / dist`，别把运行时产物塞进清单。

---

## 3. 改战法（任务表 / 坐标 / BOL）的正确姿势

1. 改 `Mission_all_*.py` 里的常量（`SUPPORT_TASKS` / `PATROL_TASKS` /
   `PREWAR_MOVES` / `BOL_STRIKES` / `SIDE_GROUND_WRA` …），**同时**更新模块
   docstring 里的条目数（人靠它对账）。
2. 若与 `*任务列表.xlsx` 不一致：**不要改 xlsx**（那是给人看的原始表格），
   在 `tools/check_table.py` / `check_table_blue.py` 的 `COORD_OVERRIDES`
   里登记「以代码为准」并写一行原因。
3. 改完必须跑 `tools/check_table*.py`，要求输出 `结论: 全部一致`。
4. 更新 `AGENT_BUILD=...` 字符串（`initial()` 第一行），并在括号里写清这版改了什么。
   日志里搜 `AGENT_BUILD` 是确认「跑的是哪一版」的唯一手段。
5. **同步离线自测里的断言**：`tools/selftest_offline.py` / `selftest_blue_hh.py`
   把任务条数、BOL 项数、战前移动次数等写成了硬断言。战法一改，它们必然红——
   这不是「测试坏了」，是契约变了：按新战法改数字，并在注释里写清
   「为什么从 X 变成 Y（对应哪条任务/哪项 BOL）」。**不要为了让测试绿而删断言。**

---

## 4. 已知陷阱（都是踩过的）

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 小窗纯灰、标题 `127.0.0.1_/` | `%LOCALAPPDATA%` 不可写 / 用了 `msedge --app` | 用 `wv2/overlay_wv2.exe`；UDF 留 exe 同级 |
| `0x80070005 E_ACCESSDENIED` | UDF 指到 `%LOCALAPPDATA%`，或进程被提权 | UDF 换 D 盘、普通权限启动 |
| `0x800700AA 请求的资源在使用中` | 两个宿主共用一个 UDF | 一个 UDF 只给一个实例 |
| 智能体 `ModuleNotFoundError: No module named 'X'` | `agentConfig.json` 的 `filePath` 是相对路径 | 见 §1.1，用绝对路径重写 |
| `launcher` 起窗口又自己关掉/置顶失效 | 监控窗标题不是以「监控小窗」开头 | 标题模板不许改（`launcher.py` 靠它按 PID 认窗口） |
| 页面底部缺一条 / 顶部被标题栏压住 | 窗口高没算标题栏 | 窗口高 = **页面设计高 + 26**（`host.cs` 里 `BAR_H`） |
| 拖边框拖不动 | 无边框窗口没有 `WS_THICKFRAME` | 已改自绘缩放（`OverlayForm` 的 `WM_NCHITTEST` + `SetBounds`），别回退 |
| Win11 窗口四周一圈白框 | DWM 给「无标题栏可缩放」窗口画的边框 | 所以**没有**用 `WS_THICKFRAME`，别再加回来 |
| 部署后 `check_env.py` 报 ⑤ 缺文件 | `pack.py` 清单没登记 | 见 §2 |
| 中文乱码 | `.ps1/.iss` 没存 BOM | 见 §1.4 |

---

## 5. 改完必须跑的验证（按可利用环境选）

**任意机器（纯 Python 3 + openpyxl，无需灵弈）——一条命令**

```bash
./verify.sh              # Linux/macOS/Git-Bash
python verify.py         # Windows（或用 verify.bat）
```

它会跑：11 个文件的 `py_compile` → 3 个任务表核对 → 2 个离线自测 → `pack.py` 清单校验，
逐项 `PASS/FAIL`，最后一行是 `结果：通过 N 项，失败 0 项`。
`--quick` 跳过离线自测（改文档/小窗时用）。

单独跑某一项：

```bash
python 智能体代码/tools/check_table.py          # 期望：结论: 全部一致
python 智能体代码/tools/check_table_blue.py     # 期望：结论: 全部一致
python 智能体代码/tools/selftest_offline.py     # 期望：全部断言通过
python 智能体代码/tools/selftest_blue_hh.py     # 期望：全部断言通过
./pack.sh --no-zip                              # 期望：[OK] 目录已生成
```

**目标机（Windows + 灵弈，部署后）**

```bat
D:\LingYi\intelligent\new_env\ray210\python.exe -X utf8 ^
  D:\LingYi\intelligent\ai\engine\LingYi\tools\check_env.py
:: 期望：六项全 [OK]，退出码 0
```

**安装包（需要 Inno Setup 6）**

```bat
installer\build_installer.bat
:: 产物 dist\灵弈小窗+红方智能体_setup_<日期>.exe，静默安装退出码 0
```

全绿才允许提交；有红项就在提交信息里写清楚哪项没过、为什么、谁来补。

**强烈建议装提交钩子**（每个克隆做一次，之后 `git commit` 自动跑 `verify.sh --quick`）：

```bash
git config core.hooksPath .githooks
```

钩子红灯会直接拦下提交（`--no-verify` 可绕过，不推荐）。

---

## 6. 提交信息的要求

- 标题 ≤ 72 字符，中文可以，格式 `类型(范围): 一句话`
- 正文写**为什么**（现象 → 根因 → 改法），涉及目标机实测的把命令/日志关键行贴上来
- 改战法的提交，必须写清「改了哪几条任务/坐标、AGENT_BUILD 从哪版到哪版」
- 一次提交只做一件事；`pack.py` / `deploy.ps1` / `check_env.py` 三件套的改动放在同一条

---

## 7. 与「对面」（决赛代码）协作

**分工**：对面写战法（`Mission_all_*.py` + xlsx 任务表），我们维护运行环境
（小窗、部署、打包、校验工具）。合并时**按目录定归属**，见 `docs/协作与合并.md`。

一句话版：`Mission_all_*.py` 以对面为准；`小窗/**`、`tools/**`、`pack.py`、
`deploy.ps1`、`installer/**` 以我们为准；对面新增的文件必须补进
`pack.py` + `deploy.ps1` + `check_env.py` 三处。

### 分支策略（硬要求）

| 分支 | 用途 | 谁能动 |
| --- | --- | --- |
| `main` | **只放发布版本**（能直接打包/上机的那一版） | 发布时由维护者合并后推送，**平时不许直接提交** |
| `feat/<一句话>`、`fix/<一句话>`、`docs/<一句话>` | 日常开发 | 任何人 |
| `duimian` | 对面「决赛代码」原样快照 | 留档，不删不改 |

流程：`git switch -c feat/xxx main` → 改 → `./verify.sh` 全绿 → 提交 →
合并回 `main`（本地 `--no-ff` 合并或发 PR）→ 在 `main` 上打标签发布
（例如 `v2026.11.25`）。**需要发包/上机验证时才让 main 前进，别把半成品推进去。**
