// 共用小工具：伪代码块（与图、表并列编号，kind = 代码）
// 外观、关键字高亮都收在 pseudocode() 自己的作用域里，不在 main.typ 写全局
// show raw —— 全局规则会把正文行内的 `V2_A0_new` 这类代码也一起重建，
// 表格里以代码写成的字段名会因此错位。

// ---------- 关键字高亮 ----------
// 这里的伪代码不是任何一种现成语言（中文标识符与 if/for/return 混排），所以不套
// Typst 内置的语法树，而是自己按关键字表染色：控制词用强调蓝加粗，其余保持正文色。
// 用 \b 界定词边界，`set_mission_wra` 这类标识符里的 in/as 不会被误染。
#let code-keyword = regex(
  "\\b(if|elif|else|for|while|in|and|or|not|is|return|break|continue|pass|True|False|None)\\b",
)
#let highlight-keyword(line) = {
  let out = ""
  let i = 0
  for m in line.matches(code-keyword) {
    if m.start > i { out += line.slice(i, m.start) }
    out += text(fill: rgb("#3370ff"), weight: 700, m.text)
    i = m.end
  }
  out += line.slice(i)
  out
}

// 整行注释淡灰；行内 "  # …" 之后的部分也淡灰；剩下的代码段做关键字染色。
// 这条规则写在代码块自己的作用域里（而不是顶层），因为行内 raw 也带一个 raw.line，
// 放在顶层会把正文里的 `USE_DROPTARGET=False` 这种行内代码也染成两色。
#let code-line-style(it) = {
  let t = it.text
  if t.trim().starts-with("#") {
    text(fill: rgb("#8a93a0"), t)
  } else {
    let parts = t.split(regex("[ ]{2,}#"))
    if parts.len() > 1 {
      let code = parts.first()
      let rest = parts.slice(1).join("  #")
      highlight-keyword(code) + text(fill: rgb("#8a93a0"), "  #" + rest)
    } else {
      highlight-keyword(t)
    }
  }
}

// 独立成段的一段代码（不编号），例如命令行清单
#let codeblock(body) = {
  show raw.where(block: true): it => block(
    width: 100%,
    inset: (left: 1.1em, right: 1.0em, top: 0.65em, bottom: 0.65em),
    stroke: (left: 2.5pt + rgb("#3370ff99")),
    fill: rgb("#f7f8fa"),
    radius: (right: 2pt),
    above: 0.7em,
    below: 0.7em,
    {
      // 高亮后的关键字与代码段是重建出来的普通文本（不再是 raw 元素），
      // 若不关掉两端对齐，行内空格会被拉开，换行位置与原文不一致。
      set par(leading: 0.62em, justify: false)
      show raw.line: code-line-style
      text(
        font: ("DejaVu Sans Mono", "Noto Sans Mono CJK SC"),
        size: 8.4pt,
        fill: rgb("#1f2937"),
        it,
      )
    },
  )
  body
}

#let pseudocode(body, caption: none) = figure(
  codeblock(body),
  kind: "代码",
  supplement: [代码],
  numbering: "1",
  gap: 0.6em,
  caption: caption,
)
