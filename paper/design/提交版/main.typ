#import "@preview/easy-paper:0.2.2": *

#show strong: it => {
  show regex("\p{Han}"): set text(weight: "light")
  it
}
#show: project.with(
  title: "联合作战人机协同智能体说明文档",
  author: "春夏秋冬队\u{3000}国防科技大学",
  date: auto,
  abstract: text(font: ("New Computer Modern", "Noto Serif CJK SC"))[
    我们在联合作战智能推演平台的《诺曼底 2027-人机协同版》想定里构建了一组规则型智能体，分三块：三个战前规划智能体（任务部署、条令设置、武器挂载），把 26 条支援任务、13 条巡逻任务、24 组挂载和全套 WRA 一次性下发；五个战术智能体（物理作战域三维监控、空战单元自卫、空空作战、登陆船只集群自卫、地空导弹营攻击与自卫），接手飞行、开火、雷达开关这类高频动作；四个辅助模块（自动打击、加油、预警机、任务区分段），补齐开局打击、续航处置与任务区切换。

    这些规则仍然是“条件成立就执行动作”的形式，区别在阈值的来路：我们不凭经验拍一个数，而是先给每条阈值找一把物理尺子，再用受控实验看它落在尺子的哪一侧。尺子是临界距离 $d_0$——假设导弹速度线性下降、降到 500 公里/小时就没有能量，它最远能在哪里追上目标，有闭式解 #box[$d_0 = T(V_0 - V_a)^2 / (2(V_0 - 500))$]。距离超过这个数再开火，弹追不上；小于这个数才追得上。阈值取它的几分之一，等于决定了早打还是晚打。

    主要结果：① *空战单元自卫*原先按 50/20 公里分档掉头。对 2000–3500 公里/小时的来袭弹，这段距离只有临界距离的 0.47–1.67 倍，部分档位起步偏晚；改为按双方速度实时计算 $d_"turn" = 1.2 d_0$ 后，五个弹速档的存活率都是 100%，均值由 88.4% 升至 100.0%。② *空空作战*原先按固定 60/90 海里开火，弹的能量撑不到那个距离，追不上目标，命中率只有 0–12%；改为 $0.8 d_0$ 后命中率 100%，且比对手早开火 46.7–83.3 秒。③ *登陆船只集群自卫*的双舰分层补射，拦截率 75.1% 低于双舰均半射程的 84.9%，但平均拦截距离从 30.0 公里推到 43.3 公里，是用约 10 个百分点的拦截率换 13 公里；效率增益来自双舰分担弹舱。④ *地空导弹营*的 $3 slash 5 D_max$ 在纯能量模型里不是最优点（0.915 对 0.981），最优值还随弹速在 0.2–0.7 $D_max$ 之间漂移，可落地的是按弹速查表。

    四组结果指向同一件事：阈值没有“通用最优常数”。能用距离、速度算出来的，就该跟着弹速实时算，并接受实验检验；同时承担多个目标（拦截率与拦截距离、命中率与先射权）的，先说清哪个优先，再定它取多少。

    最后说明范围：模型里没有导引头、雷达对抗与激光毁伤环节，衰减律尚未定稿，所有数值来自我们自己的仿真而不是平台计分。因此“哪条规则更好”这类方向性结论可以直接用，“提前多少秒”“多出多少公里”只能看方向，不能当标准。
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
  // 只给编号上色：纯数字（可带点号分隔）的文本片段才是编号
  show regex("^\d+(\.\d+)*$"): set text(fill: rgb("#3370ff"))
  show regex("\p{Han}"): set text(weight: 600)
  it
}
#show figure.caption: it => {
  set align(center)
  text(fill: rgb("#3370ff"), weight: 600)[#it.supplement #context it.counter.display(it.numbering)]
  h(0.6em)
  it.body
}

// ---------- 伪代码：与图、表并列编号（kind = 代码） ----------

#title-state.update("人机协同规则型智能体")
#show ref: set text(fill: rgb("#1f2937"))
// 避免 "km/h" 在行尾被拆成 "km/" + "h"
#show "km/h": it => box(it)

// ---------- 目录（三级，与赛会样板报告一致） ----------
#show outline.entry.where(level: 1): set text(weight: 700, size: 11pt)
#show outline.entry.where(level: 2): set text(size: 10.5pt)
#show outline.entry.where(level: 3): set text(size: 10pt)
#show outline.entry: set par(leading: 0.9em)
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

#bibliography("../../shared/ref.bib", style: "gb-7714-2015-numeric")
