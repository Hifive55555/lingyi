#import "@preview/easy-paper:0.2.2": *

#show strong: it => {
  show regex("\p{Han}"): set text(weight: "light")
  it
}
#show: project.with(
  title: "联合作战人机协同智能体设计报告",
  author: "春夏秋冬队\u{3000}国防科技大学",
  date: auto,
  abstract: text(font: ("New Computer Modern", "Noto Serif CJK SC"))[
    我们基于“灵弈”联合作战智能推演平台的《诺曼底 2027-人机协同版》想定，构建了一系列基于规则的战术智能体。这些智能体被划分为三个主要部分：_（1）战前规划智能体_：负责任务分配、规则设置以及武器装备的配置。它们能够同时执行 22 项支援任务、16 项巡逻任务、24 组挂载方案，以及与 WRA 相关的所有流程。_（2）战术智能体_：负责物理作战域三维监控（三维视角）、空战单元自卫、空空作战的指挥，以及登陆船只集群自卫。这些智能体需要处理频繁发生的操作，例如飞行、射击、雷达的开启与关闭等。_（3）辅助模块_：负责开局的自动打击（纯方位打击）。

    虽然这些规则仍然遵循“仅在满足特定条件时才执行相应操作”的原则，但它们之间的关键区别在于阈值（决策临界点）的确定方式。我们并非基于经验来设定阈值，而是首先为每个阈值制定物理标尺，然后通过实验来验证在这些标准范围内系统行为的有效性。例如，如果我们假设导弹的速度会呈线性下降，当速度降至每小时 500 公里时导弹会失去动能，那么导弹能够追上目标的最大距离可以通过以下公式计算：$d_0 = (T (V_0 - V_a)^2) / (2 (V_0 - 500))$。如果射击距离超过这个值，导弹就无法击中目标。攻击时机的选择取决于阈值被设定为该距离的多少倍。

    主要改进结果如下：_（1）空战单元自卫_：之前系统在面对时速 2000 至 3500 公里的导弹时，会在 50 至 20 公里的距离内进行掉头；然而这一距离实际上只是临界距离的 0.47 至 1.67 倍，导致在某些情况下掉头动作过于迟缓。改进后，系统能够根据双方的速度实时计算最佳掉头距离，从而在所有速度范围内实现 100% 的生存率，平均生存率也从 88.4% 提升到了 100.0%。_（2）空空作战_：之前系统在固定距离（60/90 海里）内进行射击，但由于导弹能量不足而无法有效命中目标，命中率极低（0% 至 12%）。调整后，射击距离改为 $0.8 d_0$，命中率提升至 100%，同时射击时间也比对手快了 46.7 至 83.3 秒。_（3）登陆船只集群自卫_：当两艘舰船分层补射进行导弹拦截时，拦截成功率仅为 75.1%，低于两艘舰船在半射程距离内拦截时的 84.9%；不过拦截距离从 30.0 公里延长到了 43.3 公里。这一方案使拦截率降低了约 10 个百分点，效率增益则主要来自两艘舰船分担弹舱。_（4）地空导弹营_：传统模型中最佳作战策略并不明确，但实际上最佳策略会随着导弹速度的不同而变化。最佳开火比例范围为 $D_max$ 的 0.2 至 0.7 倍，具体数值需根据导弹速度从相应表格中确定。

    这些结果表明：不存在适用于所有情况的“通用最优阈值”。距离和速度相关的参数应通过实时计算得出，并通过实验进行验证。此外，在同时处理多个目标时，必须明确各因素的优先级后再设定相应的阈值。需要进一步完善的地方是：该模型尚未包含导引头、雷达对抗机制或激光毁伤效果等要素，也没有确定能量衰减的具体规律。所有数值均基于我们的模拟结果。因此，虽然可以得出某些规则的有效性，但关于“哪个方案更优”之类的结论可以直接参考；而对于“提前多少秒”“在多远的距离上采取行动”之类的具体数值，仍应将其视为参考数据。
  ],
  keywords: ("人机协同", "兵棋推演", "规则型智能体", "临界距离", "追逃问题", "受控对比实验"),
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

// Noto CJK 为可变字体（VF），Typst 可能选到最细实例；显式指定字重
#set text(font: ((name: "New Computer Modern", covers: "latin-in-cjk"), "Noto Serif CJK SC"), lang: "zh", region: "cn", weight: 400)
#set heading(supplement: none)
#show heading: set text(weight: 600)
#show heading: it => {
  show regex("\p{Han}"): set text(weight: 600)
  it
}
#show strong: set text(weight: 700)

// ---------- 标题编号 / 图表编号：蓝色强调（与赛会样板 #3370ff 一致） ----------
#show heading: it => {
  // 二、三级编号形如 2.1.2（至少含一个点号）；要求含点号，
  // 这样标题正文里的 $d_0$ 下标、"0.8" 之类的数字不会被误染成蓝色。
  show regex("^\d+(\.\d+)+$"): set text(fill: rgb("#3370ff"))
  show regex("\p{Han}"): set text(weight: 600)
  it
}
// 一级标题编号（1 / 2 / 3 …）：一级标题正文不含数字，可安全匹配纯数字
#show heading.where(level: 1): it => {
  show regex("^\d+$"): set text(fill: rgb("#3370ff"))
  show regex("\p{Han}"): set text(weight: 600)
  it
}
// 题注：整块居中；若折行，折行部分两端对齐（避免末行只有几个字被居中而显得零散）
#show figure.caption: it => layout(size => {
  let head = text(fill: rgb("#3370ff"), weight: 600)[#it.supplement #context it.counter.display(it.numbering)]
  let body = head + h(0.6em) + it.body
  let natural = measure(body, width: size.width).width
  let w = calc.min(natural, size.width)
  align(center, block(width: w, {
    set par(justify: natural >= size.width, leading: 0.62em)
    body
  }))
})

// ---------- 伪代码：与图、表并列编号（kind = 代码） ----------

#title-state.update("人机协同规则型智能体")
#show ref: set text(fill: rgb("#1f2937"))
// ---------- 各类序号统一用文中的强调蓝 ----------
// （1）式手写段首序号：（1）（2）……
#show regex("^（\d+）"): it => text(fill: rgb("#3370ff"), it)
// 有序列表编号：1. / (1) / ① / a.
#set enum(numbering: (..n) => {
  let n = n.pos()
  let pat = ("1.", "(1)", "①", "a.").at(n.len() - 1, default: "1.")
  text(fill: rgb("#3370ff"), numbering(pat, ..n))
})
// 无序列表圆点 • ◦ ▶
#set list(marker: (
  text(fill: rgb("#3370ff"), "•"),
  text(fill: rgb("#3370ff"), "◦"),
  text(fill: rgb("#3370ff"), "▶"),
))
// 避免 "km/h" 在行尾被拆成 "km/" + "h"
#show "km/h": it => box(it)
#show table.cell: set par(justify: false)
// 表内文字左对齐（figure 默认居中会把折行单元格排成居中，长说明列尤显零散）
#show table.cell: set align(left)
#show table.cell.where(x: 0): set align(left)


// ---------- 代码块样式：浅底 + 左侧色条 + 等宽小字号 + 注释淡灰 ----------
#show raw.where(block: true): it => block(
  width: 100%,
  inset: (left: 1.1em, right: 1.0em, top: 0.65em, bottom: 0.65em),
  stroke: (left: 2.5pt + rgb("#3370ff99")),
  fill: rgb("#f7f8fa"),
  radius: (right: 2pt),
  above: 0.7em,
  below: 0.7em,
  {
    set par(leading: 0.62em)
    text(
      font: ("DejaVu Sans Mono", "Noto Sans Mono CJK SC"),
      size: 8.4pt,
      fill: rgb("#1f2937"),
      it,
    )
  },
)

// 整行注释淡灰；行内 "  # …" 之后的部分也淡灰
#show raw.line: it => {
  let t = it.text
  if t.trim().starts-with("#") {
    text(fill: rgb("#8a93a0"), t)
  } else {
    let parts = t.split(regex("[ ]{2,}#"))
    if parts.len() > 1 {
      let code = parts.first()
      let rest = parts.slice(1).join("  #")
      text(code) + text(fill: rgb("#8a93a0"), "  #" + rest)
    } else {
      it
    }
  }
}
// ---------- 目录（三级，与赛会样板报告一致） ----------
#show outline.entry.where(level: 1): set text(weight: 700, size: 11pt)
#show outline.entry.where(level: 2): set text(size: 10.5pt)
#show outline.entry.where(level: 3): set text(size: 10pt)
#show outline.entry: set par(leading: 0.9em)
#set outline.entry(fill: repeat("·", gap: 0.2em))
#pagebreak(weak: true)
#align(center)[#text(size: 18pt, weight: 700)[目　录]]
#v(1.2em)
#outline(title: none, depth: 3, indent: 1.6em)
#pagebreak(weak: true)

#include "sections/01-design.typ"
#include "sections/02-overview.typ"
#include "sections/03-basic.typ"
#include "sections/04-core.typ"
#include "sections/05-perf.typ"
#include "sections/06-effect.typ"
#include "sections/07-concl.typ"
#include "sections/08-appendix.typ"

#pagebreak()


// 参考文献条目编号 [1] [2] … 用蓝色（与标题编号同一强调色）
#show bibliography: it => {
  show regex("^\[\d+\]"): set text(fill: rgb("#3370ff"))
  it
}

#bibliography("shared/ref.bib", style: "gb-7714-2015-numeric")
