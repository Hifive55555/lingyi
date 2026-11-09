#import "@preview/easy-paper:0.2.2": *

#show strong: it => {
  show regex("\p{Han}"): set text(weight: "light")
  it
}
#show: project.with(
  title: "联合作战人机协同智能体 · 效果验证文档",
  author: "参赛队\u{3000}国防科技大学",
  date: auto,
  abstract: text(font: ("New Computer Modern", "Noto Serif CJK SC"))[
    我队在「灵弈」联合作战智能推演平台上投入了五个规则型战术智能体：监控、空战躲避、空空交战、船只自卫与地空导弹营。本报告逐个说明它们的设计、在实机里的用法、以及能在客户端上核对到什么程度。
    五个智能体共享同一个观测底座——监控筛出指向本方的来袭弹，输出弹型与弹速——下游四个决策域互不相交。这个结构的好处是每一路都能独立检验，代价是所有判断都被监控的输出上限锁死。四节的主体就是这种独立检验：空战躲避按弹速分档决定掉头距离，近距改为垂直于弹方向扭动，弹速衰减后掉头反打；空空交战由追击模型解出临界距离 $d_0$ 再留裕度开火；船只自卫按“弹型 × 区域”分三类处置，并用一号舰远界先拦、二号舰半射程补拦来避免重复拦截，同时召唤苏-57 打断对方的照射链；地空导弹营在被打时关雷达脱离、否则开雷达自由开火。
    每一节都按同一顺序写：规则怎么来的、在推演里怎么用、画面上能对应到什么、以及支撑这些规则的定量结果。定量结果全部来自自建运动学仿真，关键数字与算法说明都放在同一节里——例如分档掉头规则相对临界距离的裕度只有 0.47–1.67，改用 $1.2d_0$ 后全弹速段存活率达到 1.000；按 $0.8d_0$ 开火比对手的固定 60 海里包线早开火 46–83 秒，而后者在尾追态势下命中率为 0。
    实机核对受两道限制：客户端界面不标注指令来源，同一个航迹折转既可能来自智能体也可能来自操作手；四段比赛录屏又都没有打开战况与得分面板，因此拿不到任何命中、损失与得分数字。能立住的只有三条：想定里确实存在独立的地空导弹营实体（标签「霍克导弹 [P3, TAS] #31」）、确实存在巡逻区与责任区两套区域图层、交战确实在图上留下了瞄准十字与航迹折转。这三条以外的归因与定量，本报告一律标为不可判定，并给出把“不可判定”转成结论所需的取证条件。
  ],
  keywords: ("人机协同", "兵棋推演", "规则型智能体", "实机验证", "临界距离"),
  config: (
    title-font: ("New Computer Modern", "Noto Sans CJK SC"),
    author-font: ("New Computer Modern", "Noto Serif CJK SC"),
    body-font: ("New Computer Modern", "Noto Serif CJK SC"),
    heading-font: ("New Computer Modern", "Noto Sans CJK SC"),
    caption-font: ("New Computer Modern", "Noto Serif CJK SC"),
    header-font: ("New Computer Modern", "Noto Serif CJK SC"),
    strong-font: ("New Computer Modern", "Noto Sans CJK SC"),
    emph-font: ("New Computer Modern", "Noto Serif CJK SC"),
    raw-font: ("DejaVu Sans Mono", "Noto Sans Mono CJK SC"),
  ),
)

#set text(font: ((name: "New Computer Modern", covers: "latin-in-cjk"), "Noto Serif CJK SC"), lang: "zh", region: "cn", weight: 400)
#set heading(supplement: none)
#show heading: it => {
  show regex("\p{Han}"): set text(weight: 600)
  it
}
#show strong: set text(weight: 700)
#title-state.update("效果验证文档")
#show ref: set text(fill: rgb("#1f2937"))

#include "sections/01-overview.typ"
#include "sections/02-monitor.typ"
#include "sections/03-evasion.typ"
#include "sections/04-aircombat.typ"
#include "sections/05-ship.typ"
#include "sections/06-sam.typ"
#include "sections/07-scenario.typ"
#include "sections/08-conclusion.typ"

#bibliography("../shared/ref.bib", style: "gb-7714-2015-numeric")

#pagebreak()
= 附录 A　界面操作路径

本报告所有与界面有关的描述都可以在客户端里复现。路径如下。

#figure(
  kind: table,
  text(size: 8.5pt, table(
    columns: (auto, 1.2fr, 2.2fr),
    table.header([目的], [位置], [说明]),
    [看交战日志], [工具条 → 战况], [本报告缺失的三类数据之一，重录时必须打开],
    [看指令流水], [工具条 → 指令列表], [能否显示来源决定归属层能否验证],
    [看对抗得分], [工具条 → 得分], [比分的唯一来源],
    [导出态势], [工具条 → 导出态势], [比录屏更可解析，优先级高于录屏],
    [看单位明细], [工具条 → 数据查看], [单位状态、弹药、条令的可读形式],
    [换视角], [工具条 → 红方视角], [红蓝双视角对照的基础],
    [复盘], [工具条 → 战役复盘], [长时段事件回放，适合定位规则触发时刻],
    [智能体配置], [顶部菜单 → 智能体调度], [确认加载了哪一套规则],
  )),
  caption: [客户端界面中与验证相关的入口，全部为界面可读信息。],
) <tab:app-1>

= 附录 B　术语

#figure(
  kind: table,
  text(size: 8.5pt, table(
    columns: (auto, 2.4fr),
    table.header([术语], [含义]),
    [$d_0$], [尾追临界距离：导弹在能量耗尽前刚好追上目标的初始距离],
    [责任区], [界面上的红色折线多边形，端点带 BP-T71xx 编号],
    [巡逻区], [界面上的蓝色多边形，共七类（阵风 1/2、TB1/TB2/TB3、S70-1/2、左制空/北制空）],
    [瞄准十字], [系统绘制的白色十字，出现在交战相关位置],
    [对象层 / 行为层 / 归属层], [本报告的三层核对口径：对象是否存在、行为是否留痕、痕迹由谁产生],
    [$D_max$], [防空导弹最远射程；地空导弹营语境下由模型二分求得 100.8 km],
  )),
  caption: [术语表。],
) <tab:app-2>
