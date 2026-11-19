#import "../_lib.typ": pseudocode
#heading(level: 1, numbering: none, outlined: true)[附录 A　推导、协议与产物]

本附录收三块：判定距离的解析推导、平台在环实验的协议与字段要点、代码与产物清单。三块都是“可复核的部分”，不是结论本身；结论在正文各节，且每一个平台数字都应能回指到本附录列出的某一份 CSV。

#heading(level: 2, numbering: none, outlined: true)[A.1　$d_0$ 的解析推导]

$d_0$ 是全文判定距离的共同来源，它是一维尾追问题的一个闭式解，不含任何拟合参数。设目标以速度 $V_a$ 匀速远离，导弹在 $t = 0$ 从距离 $d$ 处以初速度 $V_0$ 发射，速度按

$ V(t) = V_0 - (V_0 - V_"term") t / T , quad 0 <= t <= T $

线性衰减，其中 $V_"term"$ 是能量耗尽的终端速度，$T$ 是从 $V_0$ 衰减到 $V_"term"$ 所需的时间。导弹要追上目标，必须在某个时刻之前把初始距离补回来：

$ integral_0^t (V(s) - V_a) dif s >= d $

记左端为 $F(t)$。被积函数 $V(t) - V_a$ 随 $t$ 单调递减，因此 $F$ 在 $V(t) - V_a = 0$ 处取极大值，此时

$ t^* = (T (V_0 - V_a)) / (V_0 - V_"term") $

临界距离就是可补回的最大距离：

$ d_0 = F(t^*) = integral_0^(t^*) (V(s) - V_a) dif s = (T (V_0 - V_a)^2) / (2 (V_0 - V_"term")) $

当 $V_a <= V_"term"$ 时，$F$ 在整个 $[0, T]$ 上单调增，$t^* = T$，上式退化为

$ d_0 = (T (V_0 + V_"term")) / 2 - T V_a $

三条性质直接读自上面两式，正文反复用到。第一，$d_0$ 对 $V_0$ 超线性：速度越快的来袭弹，威胁范围比它的速度本身扩张得更快，因此“按弹速分档、每档取一个常数”必然在中间档落到导弹可达范围内侧（@sec:evade 节）。第二，$d_0$ 对 $V_a$ 是二次的：目标速度每降一档，临界距离塌得比线性更快，所以 $V_0$ 必须取本段交会里*观测到的最高速*，用当前弹速会把判定距离算到“已经来不及”。第三，衰减律的形式进入答案：把线性换成 MOD（$V(t) = V_0 r^(t slash T)$）后 $d_0$ 整体变小，两式的逐档对照与幅度见 @sec:limits。

代入全文统一取值 $T = 240$ s、$V_"term" = 500$ km/h，并把 $V_a$ 取作脱离方（或目标）的速度，就得到正文三个判定距离的出生地：空战单元自卫取 $1.2 d_0$（@sec:evade），空空作战取 $0.8 d_0$（@sec:aircombat）。地空导弹营与船只自卫按 $D_max$ 的比例给线（@sec:sam、@sec:ship），那是能量裕度的另一种写法，不直接出自上式：$D_max$ 是弹型的最大可拦截距离，由平台挂载反查得到，不是弹道解。

#heading(level: 2, numbering: none, outlined: true)[A.2　平台在环实验协议与字段]

正文的结局级结论全部来自灵弈平台的受控对局。协议与字段的唯一权威文档是 `最新报告/实验v2/数据字典.md`，指标定义在 `最新报告/实验v2/实验设计.md`，两者的分工是：前者定义字段，后者定义由字段算出的指标。读表时最容易读错的有四条约定。

协议可以归纳为四条。第一，载体唯一，即《诺曼底 2027 人机协同（人人版，有红有蓝）》想定，决策间隔 30 s 仿真时间，`continuous=0` 让引擎等智能体算完再推进，因此单局内部的时序是确定的。第二，配置间只有 θ 不同：θ 经环境变量 `PI_THETA` 在实例化之前打到类属性上（映射表在 `harness/pi_v2_run.py` 的 `THETA_MAP`），不存在运行中切参，也就没有配置内漂移。第三，一局一进程，上一局的状态（拉黑列表、已毁单元、任务缓存）不跨局残留。第四，平台不暴露随机种子，`Deduction` 没有可设种子的参数，“重放同一局”这条路不存在；重复局是唯一的重采样手段，全部区间按局做 bootstrap（`n_boot=1000`，种子 `20261118`），且因为无种子，“同局号”不是同一随机实现，所以只报区间与效应量，不报 p 值、不做配对检验。

两类原始文件各记一类事实。`raw/runs.jsonl` 一行一局：`arm`、`theta`（JSON 文本）、`tap`（唯一键）、`steps`、`red_score`/`blue_score`、`winner`、`sim_end`、`ok`、`wall_s`、`step_avg_s`。`raw/tap/<arm>_<ts>_<side>.jsonl` 一行一个决策周期：`t`、`score`、`own`（本方存活单元，8 元位置数组）、`cts`（本方情报可见的接触，7 元位置数组）。派生表在 `data/`：`runs.csv`、`episode_metrics.csv`、`arm_summary.csv` 来自 `metrics.py`，`events.csv` 来自 `events.py`，`rule_metrics.csv` 来自 `rule_metrics.py`。

读表时必须守住六条。第一，唯一键是 `runs.tap`（`arm__ts`）：`episode` 实测恒为 1，不能当键。第二，`own` 只含存活单元，被击毁的单元直接从列表消失，存活率只能按计数差算，不能按 `damage` 阈值筛。第三，`cts` 隔步采集，`null` 表示本步未采集而不是“没有敌人”；敌方的损失只能取对侧 `own` 的确数，本方 `cts` 的消失计数系统性偏高。第四，红方 `own` 的 `damage` 恒为 0，红方毁伤类指标不可引用，要算“敌方毁伤”必须取对侧 `own`。第五，两个文件都是追加写，重试会让 `i` 归零，必须按 `i == 1` 切段、只取最后一段。第六，`sim_end` 有两种分布（满时长 10 800 s 与早停），得分速率必须与“满时长子集”一起报，否则早赢的局被系统性奖励。

每条结论都要能落到列。正文里任何平台数字都必须指到 `data/*.csv` 的某一列，指不到列的只能写成“设计判断”。数据字典明确列为不可派生的有四类：单发命中率、交战持续时间、单条指令的因果归因、用本方 `cts` 当敌方损失；这也是 @sec:aircombat 与 @sec:sam 只报开火点与弹药消耗、不报命中率的原因。

#heading(level: 2, numbering: none, outlined: true)[A.3　代码与产物清单]

靶机与采样（`实验v2/harness/`）。`pi_v2_run.py` 在一局一进程里跑对局：注入 θ、调 `reset`/`step`/取结果，把结局写成 `runs.jsonl` 的一行；`pi_tap.py` 是只读采样器，每决策周期抓一份态势写 `tap/*.jsonl`，不下发任何指令；`pi_v2_drive.py` 按 `plan_*.json` 批量驱动，带断点续跑与时间预算，一局崩溃只损失一局。

数据管道（`实验v2/analysis/`）。`metrics.py` 把 `runs.jsonl` 与 `tap` 对齐成 `runs.csv`、`episode_metrics.csv`、`arm_summary.csv`（含按局 bootstrap 区间）；`events.py` 把智能体 stderr 日志抽成 `events.csv`，一行一个规则事件（威胁、规避、开火、地导、舰船自卫）；`rule_metrics.py` 把 `events.csv` 聚成 `rule_metrics.csv`，一行一个（配置, 指标），附均值、标准差与 P10/P50/P90；`figs.py` 与 `figs_v2.py` 把 `data/*.csv` 画成 `fig/*.png|svg`；`gen_arms_table.py` 生成正文实验配置表的行。

产物与正文之间是一一对应的。`实验v2/data/` 是唯一数据源，`实验v2/fig/` 是图源；正文引用的副本放在 `最新报告/paper/shared/figures/`，与 `fig/` 下的同名 SVG 一一对应，正文的每一张数据图都能按文件名回到生成它的 CSV。

#pseudocode(caption: [从原始日志到 PDF 的复现命令])[
```
# 1 批量对局（靶机侧，一局一进程；plan.json 定义配置与局数）
python harness/pi_v2_drive.py plan.json

# 2 数据管道（本地，只读原始日志）
python analysis/metrics.py --runs raw/runs.jsonl --tap raw/tap --out data
python analysis/events.py
python analysis/rule_metrics.py

# 3 图（正文副本由 fig/ 同步到 paper/shared/figures/）
python analysis/figs.py
python analysis/figs_v2.py

# 4 文稿
cd ../paper && ./build.sh
```
]

运行依赖：Python 3.12（numpy、matplotlib）、Typst 0.15 与模板 `@preview/easy-paper:0.2.2`。中文字体用系统自带的 `Noto Serif CJK SC` 与 `Noto Sans CJK SC`，两者均为可变字体，正文字重显式设为 400，以免 Typst 选到最细实例。

#heading(level: 1, numbering: none, outlined: true)[附录 B　术语与型号对照表]

下表列出文中专名，第三列给出来处。

#figure(
  kind: table,
  text(size: 8pt, table(
    columns: (auto, 1.5fr, 1.7fr),
    table.header([专名], [文中含义], [出处与备注]),
    [诺曼底 2027], [本次推演的想定名], [想定说明 p1],
    [红方 / 蓝方], [红方为登陆进攻方（我方），蓝方为海岸防御方], [想定说明 p11–p14],
    [登陆准备区], [5 处海滩要点；两栖舰船进入并停留，每超过 20 分钟计 150 分（可多次累计）], [想定 5.1、占领分 1],
    [A / B / C 防御区], [蓝方装甲车加固区，加固满 30 分钟得分], [想定 5.3],
    [ABDE 区], [我方分区；与想定 A/B/C 编号的对应关系未定], [—],
    [雷鸣号], [护卫舰，想定给 7 个单元（分值 50）；本报告中承担舰空拦截], [兵力表],
    [23900], [船坞登陆舰，1 艘（另载 726 气垫艇），本报告中提供激光拦截], [想定 3.4.2],
    [海马斯 / HIMARS], [火箭炮，想定给 4 个，可对海射击], [兵力表],
    [卢卡斯 / Lucas], [低成本自杀无人机，第一类威胁], [—],
    [158C / 154C], [第三类威胁；158C 需对方飞机持续照射才能命中], [—],
    [苏-57], [用于驱离对方照射机的战斗机；与苏-75 同为红方机型], [兵力表],
    [TB1 / TB2 / TB3], [巡逻区编号；注意“TB2”同时也是无人机型号], [兵力表],
    [RP-T71xx], [平台自动生成的任务参考点编号，由“任务”菜单添加], [平台界面],
  )),
  caption: [想定专名与出处。],
) <tab:scenario>
