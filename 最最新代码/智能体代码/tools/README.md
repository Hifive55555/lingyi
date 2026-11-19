# tools/ 里每个脚本什么时候跑

本目录只放「检查/自测」脚本，**没有任何运行时依赖**：智能体跑推演时不会 import 这里任何东西。
全部脚本只读、不改环境、不联网。

## 一、上机前（部署门禁，必跑）

```bash
python tools/check_env.py
```

检查灵弈自带 Python 环境是否可用：ray210 版本（必须 3.9）、aiohttp、psutil、
`engine.LingYi.entitys` 能否导入、小窗文件是否就位、小窗状态目录是否可写。

- **退出码 0 = 可以上机；1 = 有一项硬失败**。
- 硬失败就**终止、现场不修**：比赛机没有外网，装不了包也补不了依赖，
  把 `[FAIL]` 行和 `<灵弈>\intelligent\new_env` 的目录列表报上来即可。
- 灵弈装在非默认位置：`python tools/check_env.py --lingyi "E:\LingYi"`

## 二、改完代码后（回归自测，必跑）

```bash
python tools/selftest_offline.py      # 红方 Mission_all_red.py
python tools/selftest_blue_hh.py      # 蓝方 Mission_all_blue_hh.py
```

用假的 `entitys.player` / `agent_base` 打桩驱动 Agent，不需要灵弈、不需要 Windows，
任何 Python 3 都能跑。覆盖：支援/巡逻任务条目、飞机挂载、总条令与 WRA、
BOL 纯方位打击（含"平台回成功但不扣弹"的 5 种兜底策略）、舰船航线与到点停车。

看到最后一行是 `全部断言通过` / `全部断言通过`（`selftest_offline.py` 末尾还会打印
`DBManager,析构函数执行`）即为通过。

## 三、改任务表 / 坐标之后（核表）

```bash
python tools/check_table.py           # 红方：任务表常量 vs 红方人人任务列表.xlsx
python tools/check_table_blue.py      # 蓝方：同上，蓝方人人任务列表.xlsx
python tools/check_111.py             # 红方：坐标是否被 红方人人总任务.txt 原样收录
```

防的是「手抄经纬度抄错一位」。需要 `openpyxl`（灵弈自带的 ray210 里有）。
结论应是 `全部一致` / `一致`。

## 四、实机排错

```bash
python tools/read_agent_log.py                # 默认读 D:\LingYi 下的 command_delay.log
python tools/read_agent_log.py <日志路径>
```

抓的是 `<灵弈>\intelligent\ai\config\<智能体名>#<序号>\log\command_delay.log`，
把这一局的关键行（BOL 下发/核对、指令被拒、异常）打出来。

## 五、其它

- `本队智能体报告_文本.txt` 不是脚本，是设计报告的文字素材。
- `selftest_tactics_red.py` 已删除：它测的 `Mission_tactics_red.py`
  （Monitor / Evade / AirCombat / 边界守卫）不在本目录，见 `../战术智能体说明.md` 顶部说明。
