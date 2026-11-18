# 平台在环实验：数据管道与口径说明

本目录把灵弈推演平台（远端 Windows `10.42.97.205`，`D:\LingYi\exp\v2`）的原始日志
转成可复现的 CSV 与图。**只读远端**：管道从不写远端、不 kill 进程、不改平台状态。

```
analysis/
├── metrics.py   runs.jsonl + tap/*.jsonl -> data/runs.csv, episode_metrics.csv, arm_summary.csv
├── figs.py      data/*.csv（+ raw/tap 用于得分曲线）-> fig/fig_*.png|svg
└── README.md    本文件：口径、近似项、重跑命令、证据链表
```

## 1. 输入与对齐

| 输入 | 说明 |
| --- | --- |
| `raw/runs.jsonl` | 每局一行：`arm, theta, tap, episode, steps, wall_s, step_avg_s, ok, red_score, blue_score, winner, sim_end, error_side` |
| `raw/tap/<arm>__<ts>__红方.jsonl` | 红方态势采样，每步一行；`own` = 红方全部单元，`cts` = 对蓝方情报（每 2 步一次，其余为 `null`） |
| `raw/tap/<arm>__<ts>__蓝方.jsonl` | 蓝方视角的同一份采样，`own` = 蓝方全部单元（本管道用它取蓝方损失的**确数**） |

对局规则（`metrics.py`）：

1. **只拉完备局**：`runs.jsonl` 中 `ok=true` 且能对到 tap 文件；不完整的行/文件一律跳过（打印 `skip` 原因）。
2. **对齐**：`runs.jsonl` 的 `tap` 字段 = 文件名去掉 `__红方/__蓝方.jsonl` 的部分（`<arm>__<ts>`）。无 `tap` 字段时按 `arm` 匹配（本地样本 `tap_sample/` 即此情况）。
3. **同文件多段记录**：同一 tag 文件里可能出现步序 `i` 回绕的多段（进程重启后追加写）。管道按 `i` 回绕切段，取与 `runs.jsonl` 的 `steps`/`sim_end` 最吻合的一段（`tap_passes` 列记录该文件共几段）。本地样本 `T1__红方.jsonl` 即 2 段，选中 137 行、末态 4050.3 s 的那段。
4. **重复运行记录**：同一 `tap` 在 `runs.jsonl` 出现多次时保留首条。

## 2. 指标口径（`data/episode_metrics.csv`）

| 列 | 口径 |
| --- | --- |
| `n_steps_tap` | 选中段的行数 − 1（= 仿真步数），应与 `runs.csv:steps` 一致 |
| `sim_end_tap` | 选中段末行 `t`（观测值） |
| `full_length` | `runs.jsonl:sim_end ≥ 10800 − 1 s` 记 1。以平台登记值为准，因为 tap 末行有时比登记值早一个采样点（如 `1794931446`：tap 10796.3 / 登记 10800.3） |
| `score_final` / `score_peak` | 红方 `score` 末值 / 段内最大值。**得分不单调**（命中/损失会扣分），峰值 ≠ 终值 |
| `score_auc` | `score` 对 `t` 的梯形积分，单位「分·秒」。只用于同口径横向比较，绝对值无物理意义 |
| `red_units_initial` / `red_units_final` | `own` 中出现过的单元名的并集大小 / 末步 `own` 长度 |
| `red_loss_total` / `_air` / `_sea` / `_land` | `own` 中「出现过、但末步消失」的单元数，按 `own[][1]` 分组（本场景红方仅 air/sea/land 三类：80/19/27）。`_total` 是「出现后消失」总数，若将来出现其他类别会计入 `_total` 但不进三组 |
| `red_damaged_units_final` | 末步 `own` 中 `damage_pct > 0` 的单元数 |
| `red_mean_damage_final` | 末步 `own` 的 `damage_pct` 均值（% ） |
| `blue_contacts_distinct` | `cts` 中出现过的蓝方实体名去重计数（含设施、弹药、浮标） |
| `blue_loss_cts_approx` / `_air_approx` / `_sea_approx` | **近似**：`cts` 中「出现过、最后一次可见早于末个 `cts` 采样点」的实体数，按 `cts.type` 分组（0=空中；2=水面与 3=潜艇均计入 `_sea`）。已排除 7/8（机场、雷达等设施，整局常驻）与 17（声呐浮标） |
| `blue_units_initial` / `blue_units_final` | 蓝方 tap 的 `own` 并集 / 末步长度 |
| `blue_loss_own_exact` / `_air` / `_sea` / `_land` | 蓝方 tap 的 `own` 中「出现后消失」的单元数——**确数**，应优先引用；缺失蓝方 tap 时为 `NaN` |
| `engage_peak_type1` / `engage_mean_type1` | 每个 `cts` 采样点中 `type==1`（在飞弹药）计数：峰值 / 均值（只对非 `null` 的 `cts` 行求均值） |
| `munition_models` | `type==1` 的实体名去掉 `#<序号>` 后的型号种类数 |
| `step_wall_mean` / `step_wall_p95` | 相邻两行 `wall` 之差（秒）的均值 / 95 分位，**含平台写盘与采样开销**，不是纯决策耗时；首步含初始化 |

`data/runs.csv`：`ok=true` 且对齐成功的对局，字段原样取自 `runs.jsonl`，另加 `tap_file_red`/`tap_file_blue`/`tap_steps` 便于溯源。

`data/arm_summary.csv`：长表，`(arm, metric)` 一行；`n`、`mean`、`std`（`ddof=1`，n=1 时为空）、
`ci_low`/`ci_high` 为 **bootstrap 95% 百分位区间**（`n_boot=1000`，种子 `20261118`，`n=1` 时退化到点值）。
聚合指标清单见 `metrics.py: SUMMARY_METRICS`。其中 `red_score`/`blue_score`/`steps`/`sim_end` 取自
`runs.jsonl`（平台登记值，论文引用用这四个），其余取自 `episode_metrics.csv`（tap 派生）。
`score_final` 与 `red_score`、`n_steps_tap` 与 `steps` 应当相等；不等说明 tap 末段被截断，
`metrics.py` 会在 stdout 打印一致性检查结果（本快照 4/4 一致）。

## 3. 近似项与不可引用项

| 项 | 结论 |
| --- | --- |
| `blue_loss_cts_*` | **仅近似，且系统性偏高**：情报可见 ≠ 存活。本快照 n=4 中 `blue_loss_cts_approx` 均值 47.0，而蓝方 `own` 确数 `blue_loss_own_exact` 均值 21.75（差 2.2×）。论文若写「蓝方损失」请用 `blue_loss_own_*`，把 `cts` 版本标为「情报可见性衰减」 |
| `red_damaged_units_final`、`red_mean_damage_final` | **不可引用**：本快照全部 4 局、全部步的 `own[][7]`（红方 `damage_pct`）恒为 0（蓝方有 0–87.5 的值）。红方单元只表现为「存活/消失」，没有中间伤态。只能引用「消失数」 |
| `blue_score`、`winner` | **不是独立指标**：`blue_score == -red_score`（零和计分），本快照 `winner` 恒为 1。只能当同一条信息的两种表述（`arm_summary.csv` 里 `blue_score` 与 `red_score` 的 `mean` 互为相反数） |
| `munition_models` | 弱指标：仅由 `cts` 可见弹药名推得，本快照恒为 2（`导弹` / `防空导弹`）；情报漏检会低估，不能当「实际发射型号数」 |
| `engage_*_type1` | 语义是「情报中可见的在飞弹药数」，是威胁强度代理量，**不是发射量**；且 `cts` 每 2 步一次，均值只对采样点成立 |
| `step_wall_mean` / `p95` | 含平台写盘/采样开销，与 `runs.jsonl:step_avg_s`（= `wall_s/steps`，含开局初始化）口径不同，两者只能各自纵向比较 |
| `score_auc` | 受早停影响（`sim_end` 短的局天然 AUC 低）；跨 arm 比较需同时看 `full_length` |
| `sim_end < 10800` 的局 | **不是数据缺失**：平台在胜负已定时提前结束（本快照 2/4 局），已 `ok=true`、`winner=1`。统计满时长率时用 `full_length` 区分 |

## 4. 重跑命令

远端只读拉取（快照；批量实验进行中时随时可重拉，不会影响正在跑的进程）：

```bash
cd 最新报告/实验v2
mkdir -p raw/tap
~/.cache/pi-ssh/scp-hifive 'Hifive@10.42.97.205:D:/LingYi/exp/v2/runs.jsonl' raw/
# 只拉已完备的局（runs.jsonl 里 ok=true 且两份 tap 都非空）：
~/.venvs/ai-dev/bin/python - <<'EOF' > /tmp/todo.txt
import json
for line in open('raw/runs.jsonl', encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    if r.get('ok') is True and r.get('tap'):
        for side in ('红方', '蓝方'):
            print(f"{r['tap']}__{side}.jsonl")
EOF
cd raw/tap && while read -r f; do
  ~/.cache/pi-ssh/scp-hifive "Hifive@10.42.97.205:D:/LingYi/exp/v2/tap/$f" . || echo "缺失: $f"
done < /tmp/todo.txt
```

生成 CSV 与图：

```bash
cd 最新报告/实验v2
~/.venvs/ai-dev/bin/python analysis/metrics.py            # 读 raw/ -> data/
~/.venvs/ai-dev/bin/python analysis/figs.py               # 读 data/ + raw/tap -> fig/
# 本地样本自测（不碰远端数据）：
~/.venvs/ai-dev/bin/python analysis/metrics.py --runs tap_sample/runs_sample.jsonl --tap tap_sample --out /tmp/selftest
```

`metrics.py` 支持 `--runs --tap --out --boot --seed`；`figs.py` 支持 `--data --fig --tap`。
依赖：`numpy pandas matplotlib`（`~/.venvs/ai-dev/bin/python` 已装；也可 `uv run --python 3.13`）。

## 5. 图

| 图 | 内容 | 数据来源 |
| --- | --- | --- |
| `fig/fig_arms_score.png|svg` | 每 arm 红方最终得分：箱线（分布）+ 散点（单局）+ 红菱形（均值 ± bootstrap 95% CI） | `runs.csv:red_score` |
| `fig/fig_losses.png|svg` | 每 arm 红方 air/sea/land 损失堆叠（均值，标注合计），红线为蓝方 `own` 损失对照 | `episode_metrics.csv:red_loss_*`、`blue_loss_own_exact` |
| `fig/fig_score_curve.png|svg` | 代表局得分-仿真时间曲线（每 arm 取最接近中位数得分的一局） | `raw/tap/*__红方.jsonl` 的 `t`/`score` |
| `fig/fig_metadata.png|svg` | (a) 单局步数分布；(b) 单局每步写盘耗时均值 + 95 分位 | `episode_metrics.csv:n_steps_tap`、`step_wall_*` |

字体：本机检出 `Source Han Sans SC`（`figs.py` 优先中文标签）；若部署机无中文字体，脚本自动退回英文标签并在 stdout 打印警告，图仍可用。

## 6. 证据链（论文数字 → CSV 列）

| 报告里要写的数字 | 取数方式 |
| --- | --- |
| 已完备对局数 N | `len(data/runs.csv)`；分 arm 看 `runs.csv.groupby("arm").size()` |
| 单局步数 / 仿真时长 | `runs.csv:steps`、`runs.csv:sim_end`（聚合见 `arm_summary.csv: metric=steps/sim_end`）；tap 观测见 `episode_metrics.csv:n_steps_tap`、`sim_end_tap` |
| 满时长局数 / 满时长率 | `episode_metrics.csv:full_length`（1/0），`arm_summary.csv` 中 `metric=full_length` 的 `mean` |
| 红方最终得分（均值 ± 95% CI） | `arm_summary.csv`：`metric=red_score`（平台登记值）的 `n/mean/std/ci_low/ci_high`；tap 派生版本见 `metric=score_final`（两者应相等） |
| 红方得分峰值 | `arm_summary.csv`：`metric=score_peak`；单局见 `episode_metrics.csv:score_peak` |
| 得分曲线下面积（分·秒） | `arm_summary.csv`：`metric=score_auc` |
| 红方损失（总数 / air / sea / land） | `episode_metrics.csv:red_loss_total/red_loss_air/red_loss_sea/red_loss_land`；聚合见 `arm_summary.csv` 同名 metric |
| 红方剩余兵力 | `episode_metrics.csv:red_units_final`（初始恒为 126：air 80 / sea 19 / land 27） |
| 蓝方损失（推荐引用） | `episode_metrics.csv:blue_loss_own_exact`，分组 `blue_loss_own_air/sea/land` |
| 蓝方损失（情报近似，需标注） | `episode_metrics.csv:blue_loss_cts_approx`（说明为 `cts` 可见性，非确数） |
| 交战强度（在飞弹药峰值 / 均值） | `episode_metrics.csv:engage_peak_type1`、`engage_mean_type1` |
| 弹药型号种类数 | `episode_metrics.csv:munition_models`（弱指标，见 §3） |
| 单步开销（均值 / 95 分位） | `episode_metrics.csv:step_wall_mean`、`step_wall_p95`；对照 `runs.csv:step_avg_s` |
| 单局墙钟总耗时 | `runs.csv:wall_s`、`step_avg_s` |
| 图 1–4 | `fig/fig_arms_score.*`、`fig/fig_losses.*`、`fig/fig_score_curve.*`、`fig/fig_metadata.*`（300 dpi PNG + 矢量 SVG） |
| 可复现性 | `data/README.md` 的输入清单（文件 + 大小 + sha256 + 快照时间） |

## 7. 当前快照的局限

- 快照 `2026-11-18 00:10 (+08:00)` 时批量实验仍在进行，`runs.jsonl` 只有 4 条、**仅 1 个 arm（`A0_new`）**。
  因此「各 arm 对比」暂时没有内容：`fig_arms_score.png` / `fig_losses.png` 只有一列。
  等批量实验结束后重跑 §4 即可，脚本无需修改。
- 单 arm n=4，bootstrap CI 只反映局间波动，不足以支撑「优于基线」这类结论。

## 8. 规则级事件抽取（`events.py` / `rule_metrics.py`）

§1–§7 的指标都以「整局」为粒度（得分、损失、满时长），信号被局级噪声淹没。
本节把日志里的**规则级事件**抽出来，得到「规则在什么距离/速度上真正触发」的连续量，
用来检验 §3 的五条战术规则（掉头、开火、地导发弹线、分层、垂直扭动）在平台判定链下的实际形态。

### 8.1 输入与重跑命令

日志是 Python `logging` 写到 stderr 的文本（UTF-8），每臂一个文件，单文件可达数十 MB，
**必须流式处理**。远端只读，本地快照不落在仓库里（避免把几十 MB 日志提交进 git）：

```bash
mkdir -p /tmp/lingyi_logs
~/.cache/pi-ssh/scp-hifive 'Hifive@10.42.97.205:D:/LingYi/exp/v2/logs/A0_new.err' /tmp/lingyi_logs/

cd 最新报告/实验v2
~/.venvs/ai-dev/bin/python analysis/events.py --logs /tmp/lingyi_logs   # -> data/events.csv
~/.venvs/ai-dev/bin/python analysis/rule_metrics.py                      # -> data/rule_metrics.csv/.md
```

`events.py --logs <dir|file...>` 支持一次传入多个 `.err`（`arm` = 文件名去扩展名），
因此批量实验补齐后直接 `--logs` 指向整个目录即可；`rule_metrics.py` 自动按臂并排。
本节的数字对应快照 `A0_new.err`（13 092 281 B，`sha256=4a8f17a46cf9f2d4c5bef482a8fdbb65cd6b0605b061e1d4fdb27621822cbf1c`，
拉取时间 `2026-11-18 00:33 (+08:00)`）——**日志仍在增长，重跑会得到不同的数字**。

### 8.2 局的切分与时间对齐（两个假设，都要知道）

**局（`episode_idx`）**：日志里 `round` 恒为 `1`、没有 `reset` 行（`reset=1` 只出现在
`runs.jsonl`，不在 stderr 里），`进程:1,第N局` 的 N 也恒为 1。因此切局只能靠
**想定装载行**：每个 `.err` 里每出现一次 `进程:1,第1局,想定'…'加载成功,加载想定耗时:…` 就是新的一局，
`episode_idx` 从 1 顺序编号。另有一条兜底：若 `process:` 心跳的 `time:` 比本局上一个值回退 >60 s
且 `step index` 不增，也切新局（实测未触发）。

> **因此 `events.csv:episode_idx` ≠ `runs.csv:episode`**（后者恒为 1）。它表示「该臂第几次装载想定」，
> **崩溃/重试的尝试也占一个编号**。本快照 17 次装载只有 14 局真正跑出了决策步
> （`episode_start` 行的 `step_index>0`），这 14 局才进指标分母。要跟 `runs.jsonl` 对齐只能用
> 「同臂 + 末步 sim_t ≈ sim_end」或按时间顺序，二者都只在整批跑完后才稳定。

**仿真时刻（`sim_t`）**：事件行本身不带时间，用 `process:1-<pid>, round:R, time:<t>s, step index:<k>`
心跳对齐——事件取**它之前最近一条心跳的 `time:`**，即「智能体做这次决策时看到的态势时刻」。
分辨率 = 一个决策步（实测 20–40 s），且 `time:` 步进不严格等于 30 s（实测 20/25/35 s 混现），
所以 `sim_t` 只用于排序与分段，**不要**用它做速率计算。

### 8.3 事件表与正则

`events.csv` 的 `event` 列共 14 种。正则原文如下（`events.py` 里的 `PATTERNS` / `SAM_ENTRY_PATTERNS`，
改一处必须同步另一处）：

```text
# 行头 / 结构行
头部       ^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (?P<logger>[^-]+?) - (?P<level>[A-Z]+) - (?P<msg>.*)$
局起点     进程:(\d+),第\d+局,想定'.*?'加载成功
心跳       process:\d+-(?P<pid>\d+), round:(?P<round>\d+), time:(?P<t>[\d.]+)s, step index:(?P<idx>\d+)
单元清单   (?P<side>[红蓝])方单元清单\((?P<cat>\w+) (?P<i>\d+)/(?P<n>\d+)\)：(?P<body>.*)$   （条目 ([^|]+?)\[(\d+)\]）
地导 Dmax  ^\[地空导弹营\] 初始化完成：(\{.*\})$                                        （ast.literal_eval 取 Dmax）

# 规则级事件
threat            ^威胁\[(?P<unit>.+)\] ← (?P<missile>.+)#(?P<mun>\d+)\s+弹速(?P<speed>[\d.]+)km/h 距离(?P<dist>[\d.]+)km CPA(?P<cpa>[\d.]+)km 预计(?P<tgo>[\d.]+)s命中
evade_beam        ^规避\[(?P<unit>.+)\] (?:正横机动|掉头)（弹速(?P<speed>[\d.]+) 距离(?P<dist>[\d.]+) 门限(?P<gate>[\d.]+)）→ 航向(?P<hdg>[\d.]+)° (?P<lat>-?[\d.]+),(?P<lon>-?[\d.]+)
evade_jink        ^规避\[(?P<unit>.+)\] 垂直扭动 → 航向(?P<hdg>[\d.]+)° 降高(?P<alt>[\d.]+)m
evade_takeover    ^规避\[(?P<unit>.+)\] 接管控制（退任务 (?P<mission>.+?)）(?P<ok>.*)$
evade_end         ^规避结束\[(?P<unit>.+)\]（(?P<why>[^）]*)）(?:→ (?P<tail>.*))?$
fire_aam          ^开火\[(?P<unit>.+)\] → (?P<target>.+?)\s+武器(?P<wid>\S+)×(?P<qty>\d+)\s+距离(?P<dist>[\d.]+)km ≤ 门限(?P<gate>[\d.]+)km \(0\.8d0=(?P<d08>[\d.]+) 射程(?P<rng>[\d.]+) V0=(?P<v0>[\d.]+) Va=(?P<va>[\d.]+) 高度比(?P<hr>[\d.]+)\)
fire_aam_rejected ^开火\[(?P<unit>.+)\] 被拒：(?P<why>.*)$
sam_cycle         ^\[地空导弹营\] 周期(?P<cyc>\d+)：(?P<body>.*)$          （body 再按 "' , '" 与「；」拆条目）
sam_intercept     ^\[地空导弹营\] (?P<unit>.+?) 拦截\[(?P<target>.+)\] 距离(?P<dist>[\d.]+)km 弹数(?P<qty>\d+) 弹种(?P<wid>\d+)$
sam_radar_on      ^\[地空导弹营\] (?P<unit>.+?) 威胁解除→停车\+开雷达(?:，恢复防空值班)?$
sam_disengage     ^\[地空导弹营\] (?P<unit>.+?) 脱离中（原阵位 \((?P<lat>-?[\d.]+), (?P<lon>-?[\d.]+)\)，雷达已关）$
sam_evade_persist ^\[地空导弹营\] (?P<unit>.+?) 已连续规避 (?P<n>\d+) 周期[（,，].*$
sam_fire_rejected ^\[地空导弹营\] (?P<unit>.+?) 发弹被拒（(?P<why>[^）]*)）$
ship_cycle        ^\[舰船自卫\] 周期(?P<cyc>\d+)：威胁(?P<nthr>\d+)（(?P<who>[^）]*)）[,，]\s*动作\[(?P<acts>.*)\]$

# sam_cycle 的条目（一条日志含多座营，逐条目出行）
sam_fire          ^(?P<unit>.+?) 发弹→(?P<target>.+)\((?P<dist>[\d.]+)km/发弹线(?P<gate>[\d.]+)km\)$
sam_fire_rejected ^(?P<unit>.+?) 发弹被拒（(?P<why>[^）]*)）$
sam_standby       ^(?P<unit>.+?) 目标(?P<dist>[\d.]+)km>(?P<gate>[\d.]+)km 待机$
sam_radar_off     ^(?P<unit>.+?) 被瞄准→关雷达\+加速脱离$
sam_radar_on      ^(?P<unit>.+?) 威胁解除→停车\+开雷达$
sam_evade_timeout ^(?P<unit>.+?) 规避超时→(?P<why>.*)$
```

三处**必须说明的实现细节**：

1. `unit` 组写成贪婪 `.+` 而非 `[^\]]+`：单元名里可能含 `]`（如
   `SS-26型“石头”地地战术导弹[9M723 “伊斯坎德尔-M”, 钻地弹] #2085`），用 `[^\]]+` 会漏 97 行。
2. 一次规避会产生**多行** `evade_beam`：规避航路每 `REPLOT_SEC=30 s` 至少重画一次。
   解析器按单元维护规避状态（`evade_end` 关闭；或相邻两行间隔 > 240 s = 2×`EVADE_MAX_SEC` 时重开），
   把第一行标 `evade_phase=start`、其余标 `replot`。**只有 `start` 反映规则的触发距离**，
   `replot` 的 `dist` 已经更小，混进去会把「触发过晚」算得更严重。
3. `evade_jink` / `fire_aam` / `ship_defense` 在本快照下**各有 0 行**（见 §8.4），
   正则只用构造行做过单元验证，**未经真实日志检验**。

已知的非事件消息（初始化、条令下发、单元清单、`[三维监控]`、`TAC 汇总`、`出界`、`BOL`、
grpc traceback 续行等）在 `events.py:KNOWN_NON_EVENT` 里逐条列出，只计数、不出行。

### 8.4 不可得与近似项

| 项 | 本快照结论 |
| --- | --- |
| 空战开火 `dist/d0` | **不可得（不是缺失，是规则没触发）**：`能力自检…带对空弹 0 架`，`TAC 汇总` 累计开火 = 0（14 局全 0），`开火[` 事件 0 行。红方航空兵在本次部署里**没有任何空空导弹**，所以 A1(`fire_fixed_km`)、B2/D1/D2 的开火轴在平台上没有可观测行为，Q2 的径向指标无法取证，只剩终局得分。 |
| 舰船拦截 | **不可得**：`[舰船自卫]` 全部周期都是 `威胁0（无），动作[]`（红方舰船整局没被瞄准）。`ship_defense` 事件 0 行。 |
| 地导 `d0` | 日志不给，**不可得**；只有 `发弹线`（= `sam_ratio·Dmax`）与 `Dmax`（初始化字典），故就地给出 `ratio_gate=dist/发弹线`、`ratio_dmax=dist/Dmax`。 |
| 规避的 `d0` | 日志不给（只给 `门限`）。`门限 = k_turn·d0(弹速, 我速)`，反推 d0 需要该臂的 `k_turn`，故 `d0_km` 对规避事件留空；`ratio_gate` 无此依赖，是本节的主指标。 |
| `fire_aam:d0_km` | **近似**：日志格式串里 `0.8d0=` 是硬编码的 `0.8*d0`（与 `FIRE_COEF` 无关），故 `d0_km = 日志值/0.8`。本快照 0 行，未验证。 |
| `ratio_gate` 的舍入 | 日志本身把 `门限`、`距离` 打印成 1 位小数（`%.0f`/`%.1f`），`ratio_gate` 因此有 ~±0.01 的量化误差，`gate=0` 时有 1 行无法求比值（留空）。 |
| 事件条目的归属方 | `[地空导弹营]` 是**蓝方** `SamBattalionDefense`（`Dmax` 键全是蓝方营：地空导弹连 110 km / 爱国者 55 km / 霍克 22 km / 捷羚 10 km；发弹目标全是红方单元；每局 1 次 init）。`[舰船自卫]` 是**红方**（`Dmax` 键是 `PR.2235.0`/“雷鸣”号）。`unit_kind` 由单元清单反查（`Aircraft→air`、`Ship|Submarine→sea`、`Facility→land`，与 `metrics.py` 的三分类一致），**不靠模块名猜**。 |
| `threat` 的条数 | **被节流**：`monitor()` 只在 `tgo ≤ 120 s` 或 `cycle % 20 == 0` 时打印，所以「威胁行数」不是「被锁定的架次数」。只能用来看单次威胁的距离/速度分布。 |
| `sam_intercept` 与 `sam_fire` | 本快照 2246 : 2246 **逐条 1:1**，是同一次发弹的两种表述（前者带 `弹数/弹种`）。做频次统计时二者**只能用一个**，本节统一用 `sam_fire`。 |
| `sim_t` 精度 | 1 个决策步（20–40 s），见 §8.2。 |

### 8.5 完整性核对与未匹配行

`events.py` 跑完会打印一张对账表，用红方自己的 `TAC 汇总：周期N 威胁X 自卫Y 开火Z`
的累计值和解析出的行数比对：

| 事件 | TAC 汇总累计 | 解析出行数 | 结论 |
| --- | --- | --- | --- |
| `evade_beam` ↔ 自卫 | 1813 | **1813** | 逐条相等，规避事件**无漏无重** |
| `fire_aam` ↔ 开火 | 0 | **0** | 一致（规则未触发） |
| `threat` ↔ 威胁 | 2759 | 2069 | 差 25%，**源于 `monitor()` 自身节流**（见 §8.4），不是解析漏行 |

**未匹配行占比**：快照 `74 679` 条消息行（另有 `3 906` 条无时间戳的 traceback 续行、
`4` 条装载前日志，均单列不计），**未匹配 0 条 = 0.000%**。
自测中曾漏掉四类行，现已补入正则：单元名内含 `]` 的 `威胁[...]`（`SS-26…[9M723…]`）、
`拦截[...]`、`已连续规避 N 周期`、顶层的 `发弹被拒(...)`。
批量实验新增臂后若出现未匹配，`--top-unmatched` 会打印最常见的前缀，按前缀补正则即可。

### 8.6 指标口径（`data/rule_metrics.csv`）

长表，`(arm, metric)` 一行；列 `unit, n_episodes, n_events, sum, mean, std, p10, p50, p90, ci_low, ci_high`。

| 项 | 口径 |
| --- | --- |
| 抽样单位 | **局**。`mean`/`std`/`p10/p50/p90` 是**池化**到事件（次数类则是每局计数）的点估计；`ci_low/ci_high` 是**按局重采样**（cluster bootstrap，`n_boot=1000`、种子 `20261118`，与 `metrics.py` 同口径）的 95% 百分位区间——区间宽度反映的是**局间波动**，不是事件数 |
| `episodes_loaded` / `episodes_stepped` | 装载想定次数 / 其中真正跑出决策步的次数。**所有「每局频次」的分母是后者** |
| 次数类（`*_count`） | 每局出现次数；`p10/p50/p90` 是**每局计数**的分位数 |
| 分布类（`evade_start_ratio_gate` 等） | `p10/p50/p90` 是**池化到事件**的分位数（即「所有触发点的分布」）；`mean` = 池化均值；`ci` 仍是按局重采样的 |
| 比例类（`*_frac_*`） | `mean` = 池化比例（`sum / n_events`），`ci` 按局重采样；`n_events` = 分母（可用于判定的触发数）。比例类不给 `p10/p50/p90`（池化后只有 0/1，无意义） |
| `evade_start_frac_inside_gate` | **任务口径的「触发过晚」**：触发时 `dist/gate < 1.0`（已进入包线内侧）的比例 |
| `evade_start_frac_deep_half` | 补充口径：`dist/gate < 0.5`（进到包线一半以内才动手）的比例 |
| `evade_start_frac_override` | `dist/gate > 1.0`：由 `EVADE_ALWAYS_KM=25 km` 或 `EVADE_ALWAYS_TGO=60 s` 兜底触发（此时 `dist > 门限`，因为 d0 已塌） |
| `evade_start_gap_km` | `门限 − 距离`（km）。「规则想做 门限 km 外的转向，实际在还剩多少裕度时就转了」 |
| `sam_fire_ratio_dmax` | `dist / Dmax`，`Dmax` 取该营的初始化字典值（不走近似） |

`data/rule_metrics.md` 是同一批数字的并排视图（A0_new 在最左，其余臂按文件名排序），
并给「与 A0_new 的差 + 噪声判定（`|Δ| ≤ A0 自身 std` 记为噪声）」。当前只有 1 个臂，差异表为空。

### 8.7 快照关键数字（`A0_new`，17 次装载 / 14 局有步 / 15 172 事件行）

| 量 | 值 | 列 |
| --- | --- | --- |
| 规避触发次数 | 90.0 次/局（`p10–p90` 74.7–109.1） | `evade_start_count` |
| 规避触发时的 `dist/gate` | 均值 **0.607**，P10 **0.185**，P50 **0.570**，P90 **0.965** | `evade_start_ratio_gate` |
| 「触发过晚」（`dist/gate<1`） | **0.933**（分母 1259） | `evade_start_frac_inside_gate` |
| 进到包线一半以内才动 | **0.435** | `evade_start_frac_deep_half` |
| 兜底常数触发（`dist/gate>1`） | 0.064 | `evade_start_frac_override` |
| 触发时距门限的裕度 | 均值 23.0 km，P10 1.6 km | `evade_start_gap_km` |
| 触发时距本机 | 均值 29.9 km，P10 8.3 km，P90 59.8 km | `evade_start_dist_km` |
| 触发时来袭弹速 | 均值 1604 km/h，P10 675，P90 2209 | `evade_start_speed_kmh` |
| 地导发弹次数（蓝方） | 160.4 次/局 | `sam_fire_count` |
| 地导发弹时 `dist/Dmax` | 均值 **0.368**，P10 0.182，P50 0.364，P90 0.545 | `sam_fire_ratio_dmax` |
| 地导发弹时 `dist/发弹线` | 均值 0.617，P10 0.303，P50 0.615，P90 0.923 | `sam_fire_ratio_gate` |
| 空战开火 / 舰船拦截 | 0 / 0 | `fire_aam_count` / `ship_defense_count` |

**两条读数注意**：

1. `evade_start_frac_inside_gate` 按构造必然接近 1——规则判据就是 `dist ≤ 门限`
   （`Mission_tactics_red.evade()`），所以「`<1` 的比例」只能用来量「兜底条占了多大份额」，
   **真正的「有多晚」看 `evade_start_ratio_gate` 的低分位与 `evade_start_gap_km`**。
   论文若要写「触发过晚」，请用 P10/P50 + `frac_deep_half`，不要用这个近似恒为 1 的比例。
2. `evade_start_gate_km` 依赖各臂的 `k_turn`（`C1=0.8`/`C2=1.6`/`C3=2.0`/`B1=固定 50·20`），
   **跨臂比 `gate_km` 或 `dist_km` 会把 θ 的差异算成行为差异**；跨臂只能比 `ratio_gate` 与
   `ratio_dmax` 这类**无量纲比值**（它们把 θ 约掉了：`k_turn` 变大 → `gate` 变大 → 比值变小）。

### 8.8 已知问题（待主智能体裁决，本次未改任何口径）

1. **红方开火轴无数据**：`能力自检…带对空弹 0 架` ⇒ `TAC 汇总` 累计开火恒 0。
   A1/B2/D1/D2 在平台上测的是「不开火」的后果，不是「开火门限」的后果。
2. **`[地空导弹营]` 属蓝方**：若 `PI_THETA.sam_ratio → SamBattalionDefense.FIRE_RATIO`
   确实打在这个类的唯一实例上（两方智能体跑在同一进程：同一 `process:` 心跳里同时有
   `redMain/redTac/blueMain`），则 E1/E2 改的是**对手**的发弹线。本次只按日志事实记录
   （`sam_fire_*` 全部是蓝方行为），未据此改任何臂的解释。
