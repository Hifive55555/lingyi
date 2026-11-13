#import "@preview/easy-paper:0.2.2": *

#show strong: it => {
  show regex("\p{Han}"): set text(weight: "light")
  it
}
#show: project.with(
  title: "联合作战人机协同智能体 · 效果验证文档",
  author: "春夏秋冬队\u{3000}国防科技大学",
  date: auto,
  abstract: text(font: ("New Computer Modern", "Noto Serif CJK SC"))[
    在这次专业比赛中，该团队主要部署了五名基于规则制定的战术执行者（即负责执行具体战术策略的成员）。具体内容包括：  
1. 对物理战斗区域的三维监控；  
2. 空战单位的自我防御能力；  
3. 空对空战斗机制；  
4. 登陆舰队的自我防御机制；  
5. 地对空导弹部队的攻击与自我防御能力。在本报告中，我们将详细说明这些代理程序的设计内容、在实际系统中的使用方法，以及客户方能够进行哪些程度的验证（即客户方可以通过哪些方式来确认这些代理程序的正确性或功能）。这五个代理都使用了一个共同的观测系统，即“物理战斗区域的三维监控”系统。该系统能够检测朝自己队伍飞来的子弹，并输出这些子弹的类型和速度信息。位于“下层”（即系统较低层级）的这四个决策区域彼此相互独立，每个区域都独立地运行（即各自按照自己的规则或逻辑进行决策）。这种结构的优点在于每个处理步骤都可以单独进行验证；然而缺点在于，所有的决策都会受到物理战斗区域三维监控系统输出范围的限制。报告的主要内容是关于这类独立性验证流程的详细说明。例如，在“空战单位的自我防御”机制中，系统会根据子弹的速度来计算所需的躲避距离；在近距离遭遇攻击时，空战单位会向与子弹运动方向垂直的方向扭转身体，待子弹速度降低后再进行反击。此外，在空对空战斗中，会使用追踪模型来计算“临界距离”（即双方战斗机之间必须保持的安全距离）。在发射时，我们会再次考虑为 $d_0$ 留出一定的安全裕度（即额外的空间或时间）。用于登陆的舰船群将自行采取防御措施。根据弹种和射程范围，这些舰艇被分为三类：第一类舰艇负责从远距离进行拦截；第二类舰艇负责从中距离进行拦截；通过这种分工，可以避免拦截行动的重复发生。同时，还会出动苏-57战机来干扰对方的雷达信号（即阻止对方使用雷达进行探测）。地对空导弹大队负责执行进攻任务以及进行自我防御。如果遭到攻击，应立即关闭雷达以躲避敌人；如果没有遭到攻击，则可以打开雷达并自由地进行射击。在每一节中，内容的描述将按照以下顺序进行：规则的起源、在推理过程中的应用方法、在界面上的具体实现方式，以及支持这些规则的相关定量分析结果。所有定量结果均基于我们自行开发的运动学仿真模型；相关的重要数据及算法说明也均记录在同一章节中。例如，用于判断是否需要改变方向的“阈值”（即判断是否需要改变方向的临界距离）的余量范围仅为 0.47 至 1.67。在 $1.2d_0$ 之后的整个弹速范围内，生存率均达到了 1.000。“$0.8d_0$”型武器的发射时间比对方设定的60海里范围内任何目标的响应时间都要早46至83秒。一方面，对方的命中率在追击过程中会降为0（即完全无法命中目标）。在实际设备上进行测试时，存在两个限制因素。第一点是：客户端界面中不会显示指令的来源（即指令是由哪个系统或组件发出的）。第二个问题是：无法判断同一飞行轨迹的变更究竟是由代理机构所为，还是由操作人员所为。第三个问题是：由于这四场比赛的录像数据中并未包含战况和得分的相关信息，因此我们无法获取命中次数、造成的伤害以及得分等数据。唯一可以确定的是：正如预期的那样，确实存在一支独立的地对空导弹部队（该部队使用的是“霍克导弹”）。 [P3, TAS] #31」）、确实存在巡逻区与责任区两套区域图层、交战确实在图上留下了瞄准十字与航迹折转。这三条以外的归因与定量，本报告一律标为不可判定，并给出把“不可判定”转成结论所需的取证条件。
  ],
  keywords: ("人机协同", "兵棋推演", "规则型智能体", "实机验证", "临界距离"),
  config: (
    title-font: ("New Computer Modern", "Noto Sans CJK SC"),
    author-font: ("New Computer Modern", "Zhuque Fangsong (technical preview)"),
    body-font: ("New Computer Modern", "Noto Serif CJK SC"),
    heading-font: ("New Computer Modern", "Noto Sans CJK SC"),
    caption-font: ("New Computer Modern", "Zhuque Fangsong (technical preview)"),
    header-font: ("New Computer Modern", "Noto Serif CJK SC"),
    strong-font: ("New Computer Modern", "Noto Sans CJK SC"),
    emph-font: ("New Computer Modern", "Zhuque Fangsong (technical preview)"),
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

#bibliography("../../shared/ref.bib", style: "gb-7714-2015-numeric")

#pagebreak()
= 附录A：界面操作步骤  

本报告中提到的所有界面相关内容均可在客户端环境中进行重现。具体操作步骤如下：

#figure(
  kind: table,
  text(size: 8.5pt, table(
    columns: (auto, 1.2fr, 2.2fr),
    table.header([目的（Purpose）], [位置], [说明：  
这段文字是根据某种特定目的或情境撰写的说明性文本。其内容可能包含事实、数据以及逻辑性的论述。撰写说明文的目的在于向读者传递信息、帮助他们加深理解，或促使他们采取某种行动。]),
    [让我们先查看一下战斗记录吧。], [工具栏 → 战况], [这是该报告中缺失的三种数据之一。在重新输入这些数据时，必须确保它们被正确地设置（即被激活或启用）才能被使用。],
    [查看指示处理的流程。], [工具栏 → 指令列表], [是否能够显示来源信息，决定了归属关系（即某项内容或数据的来源）是否可以被验证。],
    [请看一下对抗赛中的得分情况。], [工具栏 → 得分], [关于得分情况的唯一信息来源],
    [“Export Type”（导出类型）], [工具栏 → 导出状态信息], [用于比较的截图更便于分析，因此其优先级应该高于普通的截图。],
    [请确认一下单位的详细信息。], [工具栏 → 数据显示], [以易于阅读的形式显示单位的状态、弹药数量以及相关规则等信息。],
    [让我们换个角度来思考这个问题吧。], [工具栏 → 红方视角], [为了对比“红色”与“蓝色”这两种视角（或观点），所需的基础知识/工具。],
    [评论], [工具栏 → 战役回顾], [对于持续时间较长的事件，其回放功能非常适用于确定规则被触发的具体时间点。],
    [智能体配置], [顶部菜单 → 代理人排班系统], [请确认哪一组规则已被加载（即被程序读取）。],
  )),
  caption: [在客户端界面中，所有与身份验证相关的信息都以用户易于理解的方式呈现出来。],
) <tab:app-1>

= 附录B　术语表

#figure(
  kind: table,
  text(size: 8.5pt, table(
    columns: (auto, 2.4fr),
    table.header([该文本中并未包含“术语”（term）这个词。如果该文本中确实包含与“术语”相关的信息，请具体指明；否则，这个问题的提法就不合适了。], [这意味着……]),
    [$d_0$], [“尾追临界距离”（Tail-Chasing Critical Distance）指的是：在导弹耗尽所有能量之前，它仍能够刚好追上目标所需的初始距离。],
    [责任区域（Responsibility Area）], [这个多边形由界面上的红色折线组成，其各个顶点都标有“BP-T71xx”的编号。],
    [巡逻区域], [在用户界面上显示的蓝色多边形共有 7 种类型（分别是 Storm 1/2、TB1/TB2/TB3、S70-1/2，以及左侧控制/北部控制）。],
    [把目标对准那个十字形标志吧。], [系统会在与战斗相关的地点显示一个白色的十字标记。],
    [对象层（Object Layer）/ 行为层（Behavior Layer）/ 属性层（Attribute Layer）], [本报告中的三个验证步骤如下：  
1. 目标对象是否确实存在；  
2. 相关行为是否留下了任何痕迹；  
3. 这些痕迹是由谁留下的。],
    [$D_max$], [在“地对空导弹大队”的背景下，通过使用模型进行二分搜索算法，计算得出防空导弹的最大射程为 100.8 公里。],
  )),
  caption: [（由于“用語集”并非标准术语，此处保留原文，但建议提供更明确的术语或解释。）],
) <tab:app-2>
