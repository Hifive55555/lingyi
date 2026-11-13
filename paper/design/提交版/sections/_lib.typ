// 共用小工具：伪代码块（与图、表并列编号，kind = 代码）
#let pseudocode(body, caption: none) = figure(
  body,
  kind: "代码",
  supplement: [代码],
  numbering: "1",
  gap: 0.6em,
  caption: caption,
)
