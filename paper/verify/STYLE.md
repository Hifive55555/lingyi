# 效果验证文档 · 分节写作规范

## 全文逻辑（已定，勿改）

```
1 总览：任务、平台、五个智能体一览、两条操控通道
2 物理作战域三维监控智能体   ┐
3 空战单元自卫智能体         │
4 空空作战智能体             ├ 每个智能体一节，四段式：
5 登陆船只集群自卫智能体     │   ① 设计（规则与由来）
6 地空导弹营攻击与自卫智能体 ┘   ② 应用（在实机里怎么用）
                                 ③ 实机核对（截屏证据）
                                 ④ 关键数据（仿真支撑 + 数据怎么来的）
7 综合运用：一次对抗里的三条协同链
8 验证结论、局限与复核条件
```

## 每节的四段式（必须按此顺序）

1. **设计：规则、触发量与阈值**：这个智能体的规则是什么、触发量是什么、阈值多少。讲清楚"为什么是这个规则"，不要只列条目。
2. **应用：调用时机与分工**：它在一次推演里什么时候被调用、对哪些单位生效、与操作手怎么分工、和其他智能体怎么配合。
3. **实机核对：截屏能证明到哪一步**：给截屏，指出画面上哪些元素与该智能体相关；然后诚实地说清"能核对到哪一步、不能核对什么"。
4. **关键数据：数值与算法**：引仿真结果（数值 + 图），并说明**这些数字是怎么得到的**（模型假设、扫描变量、重复次数、种子）。

## 硬性禁止

- ❌ 不要写"本文采用抽帧/抽样/统计方法"之类的**方法学交代**。截图直接用，不解释怎么来的。
- ❌ 不要在章首写"本章将介绍……"这类导语。直接进内容。
- ❌ 不要写"效果良好""显著提升"这类没有证据的评语。
- ❌ 不要重复其他章节已给的定义（$d_0$、证据分级等），用一句话引用即可。
- ❌ 图内不要写"图 N"；正文用 `@fig:xxx` 引用。

## Typst 语法红线（违反会直接编译失败）

- 粗体用**单星号** `*文字*`，不要 Markdown 的 `**`。
- 行首的 `/` 会被当成术语表语法：写成 `[- 文字]` 或改用中文顿号。
- 数学模式里不能放中文：`$d_0$` 可以，`$V_弹$` 不行，写成 `V弹`（普通文本）。
- `pm` 要写成 `plus.minus`。
- 表格最后一行不要写成 `]),`；统一写成 `],` 后接 `)),` 再 `caption:`。
- 图标签唯一：`<fig:mon-1>` 这种带节前缀的写法，避免与其他节冲突。
- 表标签唯一：`<tab:mon-1>`。

## 可用素材（路径相对 `verify/sections/`（即 `../../shared/`））

图（`../shared/figures/`）：
- `fig1-architecture.svg` 五个智能体架构（总览节用）
- `fig_verify-collab.svg` 两条操控通道（总览节用）
- `fig2-evasion.svg` 存活率相图 / 存活率-掉头距离 / 策略对比（3 面板）
- `fig3-aircombat.svg` d0 闭式解 / d0 等值线 / 开火策略（3 面板）
- `fig4-altitude-sam.svg` 高低差 / 地导开火时机（2 面板）
- `fig5-ship.svg` 拦截率-距离权衡 / 弹药消耗 / 规模效应（3 面板）
- `fig6-sensitivity.svg` OAT 龙卷风 / 过载悬崖（2 面板）
- `fig_apply-ship.svg`、`fig_apply-aircombat.svg`、`fig_apply-sam.svg`、`fig_apply-airspace.svg` 逐智能体的实机截屏
- `fig_verify-menus.png` 顶栏菜单与任务工具条：手动指令入口 vs「智能体调度」（总览节用）
- `fig_verify-rings.png` 选中舰艇后的多层包线环（船只节用）
- `fig_verify-latency.png` 界面右上角耗时读数（综合节用）
- `fig_verify-timeline.svg` 六时刻时间线（综合节用）
- `fig_evidence-1.png`、`fig_evidence-2.png` 态势总览与细节

示意图（`../shared/schematics/`）：
- `schema-1-monitor.svg`、`schema-2-sam.svg`、`schema-3-evasion.svg`、`schema-4-aircombat.svg`、`schema-5-ship.svg`

数据（`../shared/data/`，CSV，UTF-8 BOM）：
`a_evade_policy.csv` `a_evade_pareto.csv` `b_aircombat_policy.csv` `c_ship_scheme.csv`
`c_ship_curve.csv` `d_sam_opening.csv` `e_sensitivity.csv` `f_duel.csv`

## 事实来源（写作前必读）

- `docs/讲解/02-讲解语义解析.md`：每个智能体的规则与时间码（V 级证据）
- `paper/design/main.typ`：已写好的设计侧论述（可引用结论，但**不要整段照抄**）
- `docs/资料/04-代码结构映射.md`：代码里到底实现了什么（C 级证据，含行号）
- `docs/粗版报告.md`：材料清单与存疑项

## 关键数字（必须与之一致，不得改）

| 项 | 值 |
|---|---|
| 临界距离 $d_0$ 公式 | $T(V_0-V_a)^2 / (2(V_0-500))$，$T=240$ s |
| 规则裕度 | 1500:1.67 / 2000:0.74 / 2500:0.47 / 3000:0.85 / 3500:0.67 |
| 策略存活率均值 | B0 0.000 / A3 0.638 / R 0.884 / B2 0.891 / A1 0.884 / B1 0.924 / A2 0.958 / P 1.000 |
| 按 $1.2d_0$ 插值 | 全弹速段 1.000（每格 800 次） |
| 空空策略 | 0.8d0 命中 1.000、先射 +46.7~83.3 s；固定 60nm 命中 0~0.12 |
| 高低差 | 高 20% → $d_0$ 44.4 km；同高 37.6；低 20% → 33.3 |
| 船只方案（8 枚） | R 0.751/2.22/43.3；B1 0.446；B2 0.588/2.76；B3 0.849/1.65/30.0 |
| 地导开火 | 0.3Dmax 0.981；0.6Dmax 0.915；1.0Dmax 0.000 |
| 敏感性 | ω 25→30 °/s 被击落概率 0.49→0.98 |
| 端到端 1v1 | 我方胜 100%（对手 60 海里开火超出 $d_0$，确定性落空） |

## 长度

每节 1.5–2.5 页（含图）。总览与结论各 1 页。

## 图的三段式（每节必备，缺一不可）

每节至少出现三类图，顺序为 *示意图 → 数据图 → 实机截屏*：

| 类 | 作用 | 素材 |
|---|---|---|
| 示意图 | 把规则画成几何/状态机，与设计报告同源 | `schema-N-*.svg` |
| 数据图 | 规则在仿真里的效果（你要解释这些数怎么来的） | `fig2`–`fig6` 中的相关面板 |
| 实机截屏 | 规则作用对象在客户端里的样子 | `fig_apply-*.svg` |

分配表（不得挪用别人的图，标签前缀见括号）：

| 节 | 示意图 | 数据图 | 实机截屏 | 标签前缀 |
|---|---|---|---|---|
| 1 总览 | `fig1-architecture.svg` | — | `fig_verify-collab.svg`、`fig_verify-menus.png` | `ov` |
| 2 物理作战域三维监控 | `schema-1-monitor.svg` | — | 无（不可见，如实说明） | `mon` |
| 3 空战单元自卫 | `schema-3-evasion.svg` | `fig2-evasion.svg`、`fig6-sensitivity.svg` | `fig_apply-airspace.svg` | `eva` |
| 4 空空作战 | `schema-4-aircombat.svg` | `fig3-aircombat.svg` | `fig_apply-aircombat.svg` | `acm` |
| 5 登陆船只集群自卫 | `schema-5-ship.svg` | `fig5-ship.svg` | `fig_apply-ship.svg`、`fig_verify-rings.png` | `shp` |
| 6 地空导弹营攻击与自卫 | `schema-2-sam.svg` | `fig4-altitude-sam.svg` | `fig_apply-sam.svg` | `sam` |
| 7 综合运用 | — | `fig6-sensitivity.svg` 的过载悬崖 | `fig_verify-timeline.svg`、`fig_evidence-1.png`、`fig_verify-latency.png` | `syn` |
| 8 结论 | — | — | `fig_evidence-2.png` | `ccl` |

> 图注要写"看什么"，不要写"如图所示"。每条图注至少给一个具体读数或一个判定结论。
