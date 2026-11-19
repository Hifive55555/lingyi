# 插图统一风格（v2 · 主体色方案）

**主体色：靛蓝 `#2b5d8f`**。整套图 80% 的信息用靛蓝 +中性灰承载，
**朱砂 `#b23a2b` 只标"论点"**（我方规则、阈值线、被强调的状态），
青 `#33907f` / 砂金 `#b0883a` 只作第三、第四类对象。示意图里原来的
绿/紫/黄三色已并入灰/青/砂，不再出现"彩虹流程图"。

- 色板样张：`palette.png`
- 色盲/灰度效果：`preview-cvd-cvd.png`（正常 / deutan / protan / 灰度 四联）
- 方法与工具调研：`绘图方法调研.md`
- 示意图改色前后：`preview-schematics.png`
- 数据图一览：`preview-plots.png`
- 色源与工具：`../scripts/figstyle.py`

## 一、主体色分工

| 角色 | 颜色 | 用在哪 |
|---|---|---|
| 结构 / 平台 / 默认系列 | 靛蓝 `#2b5d8f`（浅底 `#e7eef7`） | 流程框、坐标系、平台层、大多数数据系列 |
| 论点 / 我方 / 阈值 | 朱砂 `#b23a2b`（浅底 `#f8e9e5`） | 核心智能体、本次规则、门限线、被强调的状态 |
| 第三类 | 青 `#33907f`（浅底 `#e4f0ed`） | 平台内核、第二个对照配置 |
| 第四类 | 砂金 `#b0883a`（浅底 `#f7efde`） | 输出、结论、警示类标注 |
| 支撑 / 输入 / 背景 | 灰 `#6b737d`（浅底 `#f3f5f7`） | 基础智能体、采集、工具框、弱化数据 |

中性阶：`ink #171b20` · `mid #6b737d` · `soft #a4acb5` · `light #d8dde3` ·
`grid #e9edf1` · `panel #f3f5f7`

- 分类色序（并列类别 5–6 个时）：靛蓝 → 朱砂 → 青 → 砂金 → 钢蓝 `#6c8fb8` → 藕 `#6f4a6b`
- 顺序梯度（同一参数的几个取值）：`#d3dfee → #a4bcd9 → #6d92be → #2b5d8f → #1b3f63`

## 二、排版规范（`figstyle.apply()` 已固化）

正文 7 pt / 标题 8 pt / 刻度 6.4 pt；轴线 0.6 pt，只留左下 spine；
网格 `#e9edf1` 0.5 pt 且置于数据之下；线宽 1.0 pt、标记 3 pt、描边 0.6 pt；
白底；`svg.fonttype = path`（CJK 转路径，Typst 端不依赖字体）。
draw.io 示意图：`stroke-width` 2 → 1.2、3 → 1.6，文字 `#171b20`。

## 三、怎么改图

**A. 数据图（matplotlib）**

```bash
cd 最新报告
~/.venvs/ai-dev/bin/python paper/shared/scripts/fig_d0.py        # 单张
# 全部：paper/shared/scripts/{fig_tasks,fig_align,fig_evidence,fig_d0,
#       fig_evade_cdf,fig_evade_channels,fig_evade_timeline,fig_schema_cpa}.py
#      实验v2/analysis/{figs_v2,figs_process,figs_rule,evolve}.py
cd paper && typst compile main.typ main.pdf
```

新写图：`import figstyle` → `figstyle.apply()` → 用 `figstyle.INDIGO` /
`figstyle.BRICK` / `figstyle.CATEGORICAL` / `figstyle.SEQ`，不要写死 hex。

**B. draw.io 示意图（结构不动，只换色）**

```bash
cd 最新报告/paper/shared
~/.venvs/ai-dev/bin/python scripts/figstyle.py --svg 图/图1.svg 图/图2.svg \
    图/图21.drawio.svg 图/图22.svg 图/图23.svg 图/空空作战.drawio.svg
```

只替换颜色字面量（`#rrggbb` 与 `rgb(r,g,b)` 两种写法都认），
几何/文字/内嵌 mxfile 原样保留；新色是恒等映射，重复执行不再漂移。

## 四、这一版改了什么

| 类别 | 处理 |
|---|---|
| 配色体系 | 从"同色相降饱和"改为**主体色方案**：靛蓝打底、朱砂强调、青/砂金辅助、灰承担支撑 |
| 6 张 draw.io 示意图 | 绿、紫、黄三类底全部并入灰/青/砂；蓝→靛蓝、红→朱砂；描边细化。结构零改动 |
| `fig3-d0` | (a) 三条等值线 `V_a` 改单色梯度；(b) 固定档位=灰/靛，本规则=朱砂虚线 |
| `figs_rule`（F4/F5） | `A0_new`=朱砂（我方），`A1`=靛蓝，`B1`=灰；F5 五臂：朱砂/靛/青/砂/藕 |
| `fig_evade_cdf` | 本次规则=朱砂，旧分档=靛蓝 |
| `fig_tasks-overview` | 四组任务：靛蓝 / 青 / 藕 / 朱砂 |
| `fig_gate_hist`、`fig_fire_dist` 等 | 数据=靛蓝，门限/中位=朱砂，弱化数据=灰 |
| 截图类 | 不动（图9/10/13/25、图14/16/20、deploy-\*、fig_frame-\*、ui-overlay-panel）：内容本身是平台深色界面 |

## 五、配色体检（交稿前必跑）

```bash
cd 最新报告/paper/shared/scripts
~/.venvs/ai-dev/bin/python figstyle_audit.py          # 色板 + 全部图
~/.venvs/ai-dev/bin/python figstyle_audit.py --cvd ../figures/fig_evade_cdf.png /tmp/cvd
```

判据：分类色 ΔE ≥ 20；deutan/protan 模拟后 ΔE ≥ 12；顺序梯度 L\* 单调；
正文对比度 ≥ 4.5:1、描边 ≥ 3:1；语义色灰度 ΔL\* ≥ 10；单图非中性色族 ≤ 4。
本轮据此把青提亮（原 `#2e7d74` 与灰在 deutan 下 ΔE 仅 2.9）、藕/钢蓝分开，
并给 `fig_evade_cdf` 的基线加虚线做双重编码。详见 `绘图方法调研.md`。

## 六、注意

- 重新从 draw.io 导出示意图后要再跑一次 `figstyle.py --svg`；导出前把 draw.io
  主题设为 Light（深色模式的坑见 `../../图/` 修复脚本 `scripts/fix_svg_darkmode.py`）。
- 正文标题/编号蓝是 Typst 侧 `#3370ff`（`main.typ`），比图示靛蓝更亮，属有意区分：
  正文用亮蓝提亮屏幕阅读，图内用可印刷的深靛蓝。
- 换色后分页会整体位移 1 页左右（图高变化导致），图表编号不受影响。
