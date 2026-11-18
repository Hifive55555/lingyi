= 智能体算法实现

== 总体概述

1.3 节讲的是人与机之间的界面分工：谁在什么时候看到什么，谁在什么时候能下什么令。本节讲的是机器这一侧的内部组织：每个智能体由哪些子模块组成，子模块按什么顺序调用，它从哪读、往哪写。十个对象分两组排开。基础组三个——任务部署、条令设置、武器挂载，只在开局 `initial()` 里跑一遍；核心组五个——物理作战域三维监控（Monitor）、空战单元自卫（Evade）、空空作战（AirCombat）、登陆船只集群自卫（Ship）、地空导弹营（SAM），在 `step()` 里按 30 秒仿真时间重算。人类意图层 `pi_listener` 与实验采样器 `pi_tap` 挂在两组之外：前者是人的指令入口，后者只读、不下令。这些智能体共用同一套自上而下的骨架，@fig:agent-internal 把它画成七段。

#figure(
  image("../shared/figures/fig2-agent-internal.svg", width: 15.6cm),
  caption: [典型战术智能体的内部流水线：七段按调用顺序横向排开。① 读态势、② 选择器、⑤ 回读与记账、⑥ 日志、⑦ 快照这五段的写法在各智能体之间基本一致，④ 动作按各自的动作集填写，③ 判据是唯一需要整段重写的一段（图中以底色与粗边标出）。上方三个标记是本节与后文反复引用的平台约束，下方虚线回环表示每个 30 秒决策点都从第一段重走一遍。这是单个智能体的内部结构；1.3 的五环图回答的是人与机之间的分工，两者不在同一层次。],
) <fig:agent-internal>

两组智能体的差别可以一句话概括：基础组是一次性的，核心组是有状态的。基础组开一次机只执行一遍，因此写成幂等的下发——同一条条令、同一组挂载重复设一次，结果不变；它们的产物是任务、条令、挂载三类配置，配错了影响整局，所以看的是“配得全不全”。核心组每个 30 秒重算一次，因此必须有跨周期状态：`_st` 记谁在规避、`_engage_at` 记哪枚弹已被哪艘舰拦过、`_seen` 记哪些 `seq` 已经执行过；它们的产物是一串指令，错了只影响一次交战，所以看的是“阈值对不对”。两张表因此分开列（表 @tab:agents-basic、表 @tab:agents-core），列相同：智能体、内部模块（按调用顺序）、职责（做什么、读什么）、产物（下发什么、落什么盘、给谁）。

#figure(
  kind: table,
  {
    set text(size: 7pt)
    show raw: set text(size: 6.7pt)
    set par(leading: 0.62em)
    table(
      inset: (x: 2.4pt, y: 2pt),
      columns: (3.05cm, 4.3cm, 4.15cm, 4.3cm),
      fill: (x, y) => if y > 0 and calc.odd(y) { rgb("#edf1f7") },
      table.header([智能体], [内部模块（自上而下为调用顺序）], [职责（做什么 · 读什么）], [产物（指令 / 落盘 · 给谁）]),
      [任务部署\ （`Mission_all_red`）],
      [`_sel` / `_norm` / `_unit_num` 选择器 \
       `SUPPORT_TASKS` / `PATROL_TASKS` 任务表 \
       `prewar_move_units`、`refresh_ship_assignments` 移动去重 \
       `_OrderBudget` 指令预算器 \
       `do_bol_strikes`、`_dump_bol_inventory` 弹药诊断],
      [读：本方单元表（名、DBID、位置）与任务模板常量，不读敌方情报。\
       做：归一化后按关键字与舷号选单元；按表建任务并下发任务条令；推舰船到起航线；分配后重排一次；开局前导出可用 BOL 弹数。],
      [建任务、分配、航路类指令（给平台），经 `_OrderBudget` 的 400 条/周期与 10 s / 460 条窗口节流；日志记建成条数],

      [条令设置\ （`Mission_all_red`）],
      [`set_side_rules` 总条令 12 项 \
       `set_side_air_wra` 空空 3 型 \
       `set_side_ground_wra` 对地 3 型 + 反辐射 1 型 \
       `set_unit_wra` 与 `set_mission_wra` 例外 \
       `set_ship_doctrines` 舰船例外表],
      [读：武器 DBID、目标类型枚举、本方单元清单。\
       做：推演方级一次下发、下级继承；WRA 按目标类型给开火距离与齐射数；任务与单元再覆盖；雷鸣号对空改限制开火。],
      [`doctrine_*` / `wra_firing_range` / `wra_qty_salvo` 指令（给平台）；日志记每层条数],

      [武器挂载\ （`Mission_all_red`）],
      [`_loadout_rows` 运行期查 `model.db` \
       `_norm` 挂载名归一化 \
       `_pick_loadout` 关键字匹配器 \
       未命中告警（打印候选）\
       `set_aircraft_loadouts` 逐机下发],
      [读：飞机 DBID 与该机型在 `model.db` 的挂载表。\
       做：挑“名字同时含全部关键字”的一条，排除转场与维修；查不到就打出本机全部候选名。],
      [每机一条挂载指令（给平台）；warning 日志列候选挂载名],
    )
  },
  caption: [基础智能体：模块与职责。三行都只在 `initial()` 里执行一遍，产物是配置而不是交战术。],
) <tab:agents-basic>

#figure(
  kind: table,
  {
    set text(size: 7pt)
    show raw: set text(size: 6.7pt)
    set par(leading: 0.62em)
    table(
      inset: (x: 2.4pt, y: 2pt),
      columns: (3.05cm, 4.3cm, 4.15cm, 4.3cm),
      fill: (x, y) => if y > 0 and calc.odd(y) { rgb("#edf1f7") },
      table.header([智能体], [内部模块（自上而下为调用顺序）], [职责（做什么 · 读什么）], [产物（指令 / 落盘 · 给谁）]),
      [物理作战域三维监控\ （`BattlefieldMonitor`）],
      [`_collect_*` 弹目配对枚举 \
       `closest_approach` / `cpa_core` CPA 判据 \
       `route()` 三类路由（空 / 海 / 陆）\
       `_notify_changes` 播报、`status()` 快照导出],
      [读：`situation` 全量——本方单元位置、航向、速度，敌方弹药位置、速度、弹型。\
       做：唯一直接读内核；逐（单位, 弹）对算 CPA，弃掉远离、超门限、到点太远的配对；按空 / 海 / 陆分三路；全量态势写进真源。],
      [真源快照（给小窗、决策域与 `pi_tap`）；`incoming()` 只回弹型与弹速；消息栏播报【袭击】【逼近】【解除】],

      [空战单元自卫\ （`Mission_tactics_red`）],
      [`monitor()` 写威胁缓存 `_threats` \
       `d0_km` 门限 + `EVADE_ALWAYS_*` 两条硬兜底 \
       `_turn_point` 正横解算 \
       `_st` 状态机（`mission` / `evade`）\
       `_end_evade` 恢复判据],
      [读：接触表中的来袭弹（速度、位置、航向）与本机状态。\
       做：用最高弹速算 $d_0$；粒度不足时按绝对距离与剩余时间兜底；退任务接管控制权后画机动航路；威胁消失或超时回原任务。],
      [`withdraw_from_mission` / `plotted_course` / `assign_to_mission`（给平台）；日志记门限、弹速、距离],

      [空空作战\ （`Mission_tactics_red`）],
      [`_collect` 敌机情报 → `_best_aam` 选弹 \
       `_db_air_range_km` / `_v0_of` 查表 \
       `d0_km` + 双重门限（`FIRE_COEF`·$d_0$ 与 `FIRE_RANGE_COEF`·射程）\
       高度比筛 → 齐射数 → `FIRE_RETRY_SEC` 冷却],
      [读：敌方航空接触（位置、速度、高度）与本机挂载、高度。\
       做：选最近且在范围内的敌机；门限取 $c dot d_0$ 与射程七成的较小值；远距 1 发、门限六成内 2 发；同目标 30 秒内不重复。],
      [`attack_weapon_allocate_*`（指定弹种与齐射数，给平台）；日志记门限、射程、$V_0$、高度比],

      [登陆船只集群自卫\ （`ShipClusterDefense`）],
      [`_scan_threats` 威胁扫描\
       `_classify` 弹型到威胁类映射 \
       `_zone_of_unit` 区域判定（C / ABDE）\
       `_sorted_sams` 舰位排序\
       `_dispatch` 处置（`LAYERED` 开关）\
       `_fire` 拦截记账 `_engage_at`],
      [读：Monitor 的威胁清单（未接则读接触表）、舰位与任务名、弹舱余量。\
       做：按任务名判 C 区与 ABDE 区；三类威胁分别处置；一号舰远界先拦、二号舰半射程补；同（舰, 弹）节流。],
      [`attack_weapon_allocate_*` → `attack_manual` → `attack_auto`（给平台）；`switch_radar` / `plotted_course`；日志记距离与弹数],

      [地空导弹营\ （`SamBattalionDefense`）],
      [`_probe_dmax` Dmax 反查（含兜底）\
       `_threatened` 是否被单打 \
       `_maintain_combat` 开雷达⇔停车 \
       `_start_evade` / `_recover` 脱离⇔关雷达 \
       `_pick_target` + 发弹线 `FIRE_RATIO` × $D_max$ \
       `status()` 状态回读],
      [读：`monitor.has_incoming()`（未接监控时退化为 1.5 × $D_max$ 的几何自判）、接触表、弹型射程。\
       做：由弹型查 $D_max$；值班三件事成对下发、成对回读；被瞄准则清航路、停车、关雷达；进发弹线才发弹。],
      [`doctrine_switch_radar` / `hold_positon` / `attack_*`（给平台）；`status()` 供小窗回读],

      [人类意图层\ （`pi_listener`）],
      [`_poll_commands` 增量读命令文件 \
       `_seen` 按 `seq` 幂等 \
       二态展开（打击 / 前进）\
       `_refresh` 生效回读、ack 落盘],
      [读：`cmd.jsonl` 的新增行（`seq`、动作、单元名）与单元当前状态。\
       做：只读新行；同一 `seq` 只执行一次；把“暴露还是隐蔽”展开成清航路、停车、开雷达；执行后回读状态。],
      [与决策域同一通道、同一配额的平台指令；`ack.jsonl` 每次点击一行],

      [实验采样器\ （`pi_tap`）],
      [逐周期快照 \
       `cts` 隔步采样 \
       JSONL 追加写],
      [读：态势真源快照。\
       做：只读、不下令；每周期落一行；接触列表隔步采集。],
      [`tap/<臂>__<时间戳>__<方>.jsonl`（给离线统计，字段见 2.5 节）],
    )
  },
  caption: [核心智能体：模块与职责。前五行是四个决策域加只读的 Monitor，末两行是附属；这一组的模块都带跨周期状态（`_st`、`_engage_at`、`_seen`），产物一律是指令或落盘。],
) <tab:agents-core>

两张表合起来，这套系统的协同只有两条线。第一条是态势线：Monitor 是唯一直接读内核的单位，它把全量态势写进真源，四个决策域、人类视图与 `pi_tap` 都从真源取数，谁都不再各自回头调内核接口——这样“威胁是怎么判出来的”可以单独测，四个域也不可能各看各的。第二条是指令线：人类意图层与四个决策域共用同一条控制流和同一份配额（任意 10 秒 500 条），所以按钮指令必须去重排队，而二态按钮恰好让“同一按钮连按两次”变成状态未变、可直接丢弃。后四节把这两张表填满：2.2 节讲基础组三件套配了什么（二十余条支援任务、十余条巡逻任务、二十余组挂载），2.3 节讲核心组五个域各自的判据（$d_0$ 的推导在 @sec:d0 节），2.4 节给这些判据的计算代价，2.5 节交代平台在环实验的口径与取证链路；调用周期、可读字段、500 条配额与 300 字符上限这类通用约束，也在 @sec:d0 节一次交代完。
