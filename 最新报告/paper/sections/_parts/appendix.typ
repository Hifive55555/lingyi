#import "../_lib.typ": pseudocode
#heading(level: 1, numbering: none, outlined: true)[附录 A　仿真参数总表]

下表列出@sec:evade 至 @sec:sam 各节所有实验使用的参数。除了衰减时间常数 $T$ 之外，所有参数均由我们自行设定，没有使用外部信息。$T$ 对应的有效射程为 67–117 公里，与假设中的 60 海里（111 公里）和 90 海里（167 公里）处于同一数量级。$T$ 使用外部基准点校准，详见@sec:limits 节。

#figure(
  kind: table,
  text(size: 8.5pt, table(
    columns: (auto, auto, 2.2fr),
    table.header([参数], [取值], [说明]),
    [积分步长], [0.5 s], [运动学积分；命中判定用步内最近接近点的解析解，避免步长大于命中半径导致的漏判],
    [衰减时间常数 $T$], [240 s], [线性衰减 $V_0 arrow.r 500$ km/h 的时间；MOD 衰减同用此值],
    [终端速度 $V_"term"$], [500 km/h], [模型设定的能量耗尽判据],
    [追踪方最大角速度], [25 °/s], [等价于可用过载约束；敏感性见 @fig:sens b],
    [命中半径], [0.1 km], [战斗部等效杀伤半径的粗略替代],
    [飞机巡航 / 加力], [900 / 1080 km/h], [加力系数 1.2],
    [舰空导弹 $D_max$], [60 km], [登陆船只集群自卫实验的射程基准],
    [单发拦截概率], [$D_max$ 处 0.35，零距离 0.90], [随距离线性递减，自设],
    [每舰弹舱], [8 发], [影响规模效应（@fig:ship c）],
    [地空导弹 $D_max$], [100.8 km], [由模型二分求得，非外部给定],
    [随机种子], [2026], [全部实验固定，可复现],
  )),
  caption: [仿真参数总表。],
) <tab:params>

#heading(level: 1, numbering: none, outlined: true)[附录 B　重现方法]

所有实验结果和图表均由 `paper/shared/scripts/` 下的脚本生成，脚本需从项目根目录运行。

#pseudocode(caption: [重现全部实验与插图的命令序列])[
```
# 单规则验证（2.1.2 节 d0 的数值对比、高度差、地导开火）
python scripts/sim_experiments.py all --out docs/实验 --seed 2026

# 受控对比 / 消融 / 敏感性（2.3、2.4 节各组对比与 3 章的对抗效果）
python paper/shared/scripts/comparative.py all --n 800 --seed 2026

# 模型形式的稳健性扫描（2.4.6 节）
python paper/shared/scripts/sensitivity.py

# 多目标 / 多波次端到端（2.4.7 节）
python paper/shared/scripts/multitarget.py

# 数据图与示意图（SVG/PDF/PNG 三格式）
python paper/shared/scripts/figures.py
python paper/shared/scripts/fig_robust.py
python paper/shared/scripts/fig_apply.py
python paper/shared/scripts/fig_verify.py
python paper/shared/scripts/fig_verify2.py

# 文稿
cd paper && ./build.sh          # 两篇一起，也可 design / verify
```
]

单规则验证数据保存在 `docs/实验/*.csv`，受控对比数据保存在 `paper/shared/data/*.csv`，插图位于 `paper/shared/figures/` 和 `paper/shared/schematics/`。所有 CSV 文件均带 UTF-8 BOM，可直接用 Excel 打开。

运行依赖包括 Python 3.12、numpy、matplotlib 3.11、typst 0.15.1，以及 Typst 模板 `@preview/easy-paper:0.2.2`。字体使用系统自带的 `Noto Serif CJK SC` 和 `Noto Sans CJK SC`，两者均为可变字体；正文字重显式设为 400。

#heading(level: 1, numbering: none, outlined: true)[附录 C　术语与型号对照表]

下表列出文中专名，第三列给出来处。

#figure(
  kind: table,
  text(size: 8pt, table(
    columns: (auto, 1.5fr, 1.7fr),
    table.header([专名], [文中含义], [出处与备注]),
    [诺曼底 2027], [本次推演的想定名], [想定说明 p1],
    [红方 / 蓝方], [红方为登陆进攻方（我方），蓝方为海岸防御方], [想定说明 p11–p14],
    [登陆准备区], [5 处海滩要点；两栖舰船进入并停留，每 20 分钟计 120 分], [想定 5.2、3.4.2],
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
