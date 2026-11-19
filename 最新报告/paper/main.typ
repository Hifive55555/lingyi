#import "@preview/easy-paper:0.2.2": *

#show strong: it => {
  show regex("\p{Han}"): set text(weight: "light")
  show regex("[*]"): it => strong(body: text("*"))
  it
}
#show: project.with(
  title: "联合作战人机协同智能体设计报告",
  author: "春夏秋冬队\u{3000}国防科技大学",
  date: auto,
  abstract: text(font: ("New Computer Modern", "Noto Serif CJK SC"))[
    我们基于“灵弈”联合作战智能推演平台的《诺曼底 2027-人机协同版》想定，构建了一系列基于规则的战术智能体。这些智能体被划分为三个主要部分：（1）战前规划智能体：负责任务分配、规则设置以及武器装备的配置。它们能够同时执行 22 项支援任务、16 项巡逻任务、24 组挂载方案，以及与 WRA 相关的所有流程。（2）战术智能体：负责物理作战域三维监控（三维视角）、空战单元自卫、空空作战的指挥，以及登陆船只集群自卫。这些智能体需要处理频繁发生的操作，例如飞行、射击、雷达的开启与关闭等。（3）辅助模块：负责开局的自动打击（纯方位打击）。

    虽然这些规则仍然遵循“仅在满足特定条件时才执行相应操作”的原则，但它们之间的关键区别在于阈值（决策临界点）的确定方式。我们并非基于经验来设定阈值，而是先为每个阈值找到它的物理依据（比如弹在这段距离上还有没有能量），再用实验验证这些取值是否合理。例如，如果我们假设导弹的速度会呈线性下降，当速度降至每小时 500 公里时导弹会失去动能，那么导弹能够追上目标的最大距离可以通过以下公式计算：$d_0 = (T (V_0 - V_a)^2) / (2 (V_0 - 500))$。如果射击距离超过这个值，导弹就无法击中目标。攻击时机的选择取决于阈值被设定为该距离的多少倍。

    主要结果如下。（1）空战单元自卫：把掉头距离从固定 50/20 公里分档改为按 $1.2 d_0$ 实时计算之后，平台上的平均触发距离由 17.9 公里抬到 29.8 公里，完全依赖 25 公里 / 60 秒硬兜底的比例由 36.0% 降到 7.3%（事件级统计）。但同一批数据也显示，92.5% 的触发仍落在设定的阈值以内——原因是 30 秒的决策粒度，所以阈值要按弹速算，兜底条也不能省。（2）空空作战：开火距离取 $min(0.8 d_0,\u{2060} 0.7 R_"max")$ 之后，同一套平台条令下的开火次数由固定 111 公里的 85.5 次/局降到 49.4 次/局，开火点相对当时 $d_0$ 的比值由 0.724 降到 0.581——固定常数把相当一部分弹药打在了导弹可达范围之外。（3）登陆船只集群自卫：本场想定里蓝方反舰火力从未进入舰空导弹的瞄准几何（`ship_defense_count` 在全部实验配置上恒为 0），因此这一条只报“未被触发”，不报拦截率；分层的设计依据（弹舱分担）保留在正文。（4）地空导弹营：把“没被打就打、被打就跑”的二分支改为人工三态（打击 / 机动 / 骗弹）之后，平台上的读数显示：全员暴露的配置 8 局共触发 103 次“被瞄准→切回机动”，而默认配置只让 5 部诱饵雷达被瞄准、共 31 次；红方得分 575 对 553 分/小时、航空器损失 31.9 对 35.8 架——方向一致，幅度落在噪声内。

    这些结果指向同一条结论：*不存在适用于所有情况的“通用最优阈值”*。距离与速度相关的判据应当实时算，并且必须同时交代它在什么条件下失效。同时要说清本报告的证据边界：规则级结论（何时触发、触发多远）由平台事件统计支撑，样本足够；结局级结论（哪套规则赢面更大）在每组 6–20 局下*分辨不出*，因此只报方向与区间，不报“提升百分之多少”。凡涉及弹目命中、导引头状态、激光毁伤与真假弹识别的规则，平台不提供对应字段，本报告只写成“在当前证据下无法评估”。
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
    emph-font: ("New Computer Modern", "AR PL UKai"),
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

// ---------- 强调文字（楷体）里的全角标点：改用正文宋体的简体形 ----------
// AR PL UKai 是台湾字形：它把 ，。、；：？！（）等全角标点排在字身中央，
// 而简体正文的标点应贴左下角。不换字体会出现“楷体句子里的句号浮到中间、
// 两侧还各空半个字”的现象，读者会以为标点后面多了一个空格。
// 汉字仍用楷体，只把这类标点交给正文字体（Noto Serif CJK SC 有 zh-Hans 字形）。
#show emph: it => {
  show regex("[，。、；：？！（）【】〔〕《》〈〉]"): set text(
    font: ("New Computer Modern", "Noto Serif CJK SC"),
  )
  it
}

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
// ---------- 四级标题：源文件保留层级，正文里显示为「（1）加粗小标题」 ----------
// 目的：既有三级编号已经到 2.3.4，再往下编号会变成 2.3.4.1 这种四段数字，读起来费劲；
// 按评委习惯改成“（1）xxx。正文接排”的样式。源文件仍用 ==== 分层，便于维护。
#set heading(numbering: (..n) => {
  let p = n.pos()
  if p.len() == 1 { numbering("1", p.at(0)) }
  else if p.len() == 2 { numbering("1.1", ..p) }
  else if p.len() == 3 { numbering("1.1.1", ..p) }
  else { numbering("（1）", p.at(3)) }
})
// above/below 控制与上下文的间距：below 太小会让“（1）xxx”贴住下面的
// 伪代码块或正文（之前的 0.28em 肉眼几乎看不出间隙），这里放大到 1em，
// 与上面 1.05em 大致对称。
#show heading.where(level: 4): it => block(
  above: 1.05em, below: 1.0em, sticky: true,
)[
  #context {
    let n = counter(heading).get().last()
    text(weight: 700, size: 10.5pt)[（#numbering("1", n)）#it.body]
  }
]

// 题注：只有一行时整条居中；一旦折行就改为左对齐并占满版心。
// 原因：figure 内部默认是居中的，题注折行后若继续居中，每一行都会被逐行
// 居中（末行只有几个字时尤其零散），与正文左边界对不齐。
// 判定用 measure 不带宽度约束时的自然宽度（= 不折行时的宽度）。
#show figure.caption: it => layout(size => {
  let head = text(fill: rgb("#3370ff"), weight: 600)[#it.supplement #context it.counter.display(it.numbering)]
  let body = head + h(0.6em) + it.body
  if measure(body).width <= size.width {
    align(center, body)
  } else {
    block(width: 100%, {
      set par(justify: true, leading: 0.62em)
      align(left, body)
    })
  }
})

// ---------- 伪代码：与图、表并列编号（kind = 代码） ----------

#title-state.update("人机协同规则型智能体")
#show ref: set text(fill: rgb("#1f2937"))
// ---------- 各类序号统一用文中的强调蓝 ----------
// 公式编号：块级公式自动编号为（1）（2）……，编号用强调蓝（与图表编号一致），行内 $...$ 不受影响。
// 注：easy-paper 模板带着一条“无标签不编号”的 show 规则，会先把无标签块级公式改写成
// numbering: none；set 规则改不动显式参数，只能重建元素，并且必须把标签挂回去，否则两边互相覆盖、深度超限。
#show math.equation: it => if it.block and it.numbering == none {
  [ #math.equation(it.body, block: true, numbering: n => text(fill: rgb("#3370ff"), numbering("（1）", n))) #if it.has("label") { it.label } ]
} else { it }
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
// ---------- 行内代码 ----------
// easy-paper 用 `show raw: set text(font: 等宽, size: 正文五号)` 给 raw 定死了字号，
// show 优先于外层 set，所以 `V2_A0_new` 这类字段名在 7.4pt 的表里仍按 10.5pt 渲染，
// 比同行文字大一圈。这里用一个 state 记住“当前所在单元格的字号”，在 raw 重新绑回去，
// 同时把字体换成真正存在的等宽（easy-paper 指定的 Consolas / SimHei 本机没有）。
#let raw-size = state("raw-size", 10.5pt)
#show raw: it => context {
  set text(size: raw-size.get(), font: ("DejaVu Sans Mono", "Noto Sans Mono CJK SC"))
  it
}
// 成对 update：进单元格时换上表内字号，出单元格时恢复，避免污染后面的正文。
#show table.cell: it => context {
  let prev = raw-size.get()
  raw-size.update(text.size)
  {
    it
    raw-size.update(prev)
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
#include "sections/09-method.typ"
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
