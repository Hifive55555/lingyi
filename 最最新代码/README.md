# 最最新代码 —— 灵弈部署说明

红方规则智能体（`Mission_all_red.py`）+ 三个战术模块 + 灵弈小窗（`overlay`）的最终版。
本目录自带一键部署脚本，部署完在客户端里按第 3 节操作即可。

- **目标机**：Windows + 已装灵弈（含 `intelligent\new_env\ray210\python.exe`）
- **不建虚拟环境、不联网装包**：Python 只用灵弈自带的 ray210（3.9.19，自带 aiohttp 3.9.5）
- **不需要编译**：全是 .py，拷进去就生效（下一局开始时加载）

---

## 1. 打包与放置

1. 把整个 `最最新代码\` 目录打成 zip。
2. 在目标机上解压到 **`<灵弈>\intelligent\`** 下，例如：

   ```
   D:\LingYi\intelligent\最最新代码\
   ├─ deploy.bat            ← 双击这个
   ├─ deploy.ps1
   ├─ 智能体代码\  (Mission_all_red.py, 三个战术模块, tools\, entitys\, 任务表 xlsx)
   └─ 小窗\        (overlay_ai.py, overlay\)
   ```

3. 目录名随意，`deploy.ps1` 是**按文件名**找源文件的，不依赖「智能体代码 / 小窗」
   这两个名字；多套一层目录也能用。

> ⚠️ 中文目录名不要用 `tar` 传输：Windows 的 `tar.exe` 按 GBK 解码 UTF-8 文件名，
> `小窗` 会变成 `灏忕獥`，之后 `ImportError` 且看着像好的。用 zip / robocopy / 资源管理器。

---

## 2. 一键部署

```
双击 deploy.bat
```

- 想先看计划、不动任何文件：`deploy.bat -DryRun`
- 灵弈不在 `D:\LingYi`：`deploy.bat -Lingyi "E:\LingYi"`
- 其余参数见 `deploy.bat -?`（PowerShell 帮助）或下方表格

脚本做的事：

| 步骤 | 内容 |
|---|---|
| ① 定位 | 自动找灵弈根目录（逐级上溯 + 常见安装路径），确认 `intelligent\new_env\ray210\python.exe` 存在 |
| ② 拷主智能体 | `Mission_all_*.py` → `<灵弈>\intelligent\`（灵弈的 `agent_path` 就指这一层） |
| ③ 拷战术模块 | `BattlefieldMonitor.py` / `SamBattalionDefense.py` / `ShipClusterDefense.py` + 任务表 xlsx/md → `<灵弈>\intelligent\ai\engine\LingYi\` |
| ④ 拷自检脚本 | `tools\*` → `<灵弈>\intelligent\ai\engine\LingYi\tools\` |
| ⑤ 拷小窗 | `overlay_ai.py` + `overlay\`（含 `web\`）→ `<灵弈>\intelligent\ai\agent\` |
| ⑥ 自检 | 用 ray210 跑 `check_env.py`；**不过就退出码 1，部署中止** |
| ⑦ 备份 | 覆盖已有文件前存成 `原文件.bak_时间戳`，回滚直接改回来 |

`entitys\` 默认**不覆盖**（沿用灵弈自带的；实测两边 `model.db` 的 SHA256 完全一致）。
真要覆盖加 `-WithEntitys`。

---

## 3. 客户端里要做的（部署脚本不会替你点）

1. **`<灵弈>\APlatformLobby.exe`**（建议管理员）→ 底部 **【单机版启动】**。
2. **想定 → 加载想定**：`.scen` 要先放进 `<灵弈>\Data\Scenarios\`
   （比赛想定：`诺曼底2027(人机协同-人人版)`）→ 弹出「选择推演方」即加载成功。
3. **推演 → 推演速度 → 5 倍速**（与 `decision_time=5` 配套；平台参数
   `agentordercountlimit=500`、`agentorderlengthlimit=300` 不要改小，智能体的
   指令节流与 BOL 指令裁剪是按这两个值设计的）。
4. **智能体调度 → 智能体编辑 → 左下角「＋」**，导入 **`Mission_all_red.py`**：
   - 推演方选 **红方**
   - 勾 **「规则智能体」**
5. 再点一次「＋」，导入 **`<灵弈>\intelligent\ai\agent\overlay_ai.py`**（类名 `Agent`）：
   - 推演方同样选 **红方**
   - 它是小窗的数据与指令通道，和上一个是**两个独立智能体**，可以挂在同一方
6. 右上方「＋」（决策脚本输入框）里的**实体单元 / 目标 / 参考点可以留空** ——
   两个智能体都会自己遍历本方全部单元。
7. 两个智能体分别点 **启动**，然后 **开始推演**。
8. 双击 **`<灵弈>\intelligent\ai\agent\overlay\灵弈小窗.bat`** 打开置顶小窗
   （页面服务 `127.0.0.1:8761`，智能体侧 WebSocket `127.0.0.1:8760`）。
   热键：**Alt+Q 武器分配 / Alt+W 油门高度 / Alt+E 防空值班**
   （改键改 `overlay\settings.json`）。
9. 可选：在客户端「智能体调度 → 智能体消息输出」里看日志。

---

## 4. 确认装的是这一版

开局后在 `<灵弈>\intelligent\ai\config\Mission_all_red#1\log\command_delay.log` 里搜：

```
AGENT_BUILD=2026-11-09-RED-21
```

还能看到：

- `红方单元清单(…)` —— 单元名称匹配是否对得上（对不上就改 `_sel(...)` 的关键字）
- `initial 完成：本周期下发 N 条` —— 条令/挂载/任务实际下发量
- `本周期 BOL 打击成功 N 次` —— 开局锆石 / SS-26 是否打出去了

也可以直接跑：

```
<灵弈>\intelligent\new_env\ray210\python.exe  <灵弈>\intelligent\ai\engine\LingYi\tools\read_agent_log.py
```

**改代码必须先关掉再重开一局**（平台在开局那一刻加载脚本）。

---

## 5. 出问题怎么办

部署脚本输出 `[STOP]` 并退出码 1，就是**终止、现场不修**——
比赛机没有外网，装不了包、补不了依赖。把这两样报上来：

1. 上面全部 `[FAIL]` / `[STOP]` 行
2. `<灵弈>\intelligent\new_env` 下的目录列表（应有 `ray210`）

常见原因与定位：

| 现象 | 原因 | 处理 |
|---|---|---|
| `找不到灵弈安装目录` | 灵弈装在非标准路径 | `deploy.bat -Lingyi "X:\灵弈目录"` |
| `aiohttp 缺失` | ray210 不是这一版 | 换回标准安装，或从别的机器整包拷 `ray210` |
| `entitys 导入失败` | `engine\LingYi\entitys` 不完整 | 用 `-WithEntitys` 覆盖，或检查该目录 |
| 小窗打不开 / `[STOP] no bundled LingYi Python` | `灵弈小窗.bat` 找不到 ray210 | 设 `LY_PYTHON=<python.exe 全路径>` 再双击 |
| 小窗开了但没数据 | `overlay_ai.py` 没导入 / 没启动 | 看 `overlay\logs\agent.log`；回到第 3 节第 5、7 步 |
小窗窗口一闪就没了 / 页面拒绝连接 | launcher 挂了或 8761 没起来 | 看 `overlay\logs\launcher.log` |
小窗连不上智能体（页面显示未连接） | 8760 没监听或被占用 | `overlay\logs\agent.log` 里搜“WS 已监听”/“放弃监听”；`netstat -ano \| findstr :8760` |
| 防空值班按钮没反应 | 状态目录不可写 | `check_env.py` 第 ⑥ 项会报；用 `LY_SAM_STATE_DIR` 指到可写目录（两侧一致） |
| 设了条令却没生效 | 10 秒窗口内指令超 500 条被丢 | 查日志里“指令条数超出数量限制” |

回滚：覆盖过的文件旁边都有 `*.bak_<时间戳>`，改名回去即可。

**小窗日志在哪**（上一版查不到问题就是因为没有日志，现已补上）：

| 文件 | 谁写 | 看什么 |
|---|---|---|
| `<灵弈>\intelligent\ai\agent\overlay\logs\agent.log` | `overlay/agent.py`（跑在引擎进程里） | 启动横幅（python/路径/端口/side）、`initial`/`step`/`execute` 的异常 traceback、“WS 已监听”/“放弃监听” |
| `...\overlay\logs\launcher.log` | `overlay/launcher.py` | 页面服务是否起来、找没找到 Edge、热键注册、崩溃 traceback |
| `<灵弈>\intelligent\ai\config\overlay_ai#1\log\command_delay.log` | 平台 | 只有平台自己的行，**不含**小窗日志 |

两个日志都超过 2 MB 会自动轮转成 `*.1.log`，不会把 D: 占满。

---

## 6. 目录内容对照

| 包内路径 | 部署到 | 说明 |
|---|---|---|
| `智能体代码\Mission_all_red.py` | `<灵弈>\intelligent\` | 红方主智能体（战前配置：条令/WRA/挂载/任务/BOL/航线） |
| `智能体代码\Mission_all_blue_hh.py` | 同上 | 蓝方人人版（备用/陪练） |
| `智能体代码\BattlefieldMonitor.py`<br>`SamBattalionDefense.py`<br>`ShipClusterDefense.py` | `<灵弈>\intelligent\ai\engine\LingYi\` | 三个战术模块（被 `Mission_all_blue_hh.py` 按 `engine.LingYi.X` 导入） |
| `智能体代码\tools\` | `<灵弈>\intelligent\ai\engine\LingYi\tools\` | `check_env.py`（环境门禁）、两个 `selftest_*`、三个 `check_*`、`read_agent_log.py`，说明见其中 README |
| `小窗\overlay_ai.py` | `<灵弈>\intelligent\ai\agent\` | 客户端「添加智能体」选它，类名 `Agent` |
| `小窗\overlay\` | `<灵弈>\intelligent\ai\agent\overlay\` | `agent.py`、`launcher.py`、`web\`、`灵弈小窗.bat`、`weapons.json` |
| `智能体代码\entitys\` | 默认不部署 | 平台接口库（cp39 .pyd + `model.db`）；需要时 `-WithEntitys` |

`tools` 里每个脚本什么时候跑，见 `智能体代码\tools\README.md`。
