# 文稿工程（Typst + easy-paper）

正式排版稿。内容取自上级目录的资料整理与实验，按技术报告体例重写：
每条结论标注证据级别（A 讲解 / B 笔记 / C 代码 / D 仿真 / E 存疑），
自建仿真数据与平台实测严格区分。

**当前版本：19 页，6 张多面板图，13 张表，11 条参考文献**

## 文件

- `main.typ` — 文稿源文件（正文、图、表、引用）
- `ref.bib` — 参考文献（GB/T 7714—2015 数字顺序制）
- `figures/fig1-architecture.svg` — 图 1 架构与状态机
- `figures/fig2-evasion.svg` — 图 2 空战躲避四面板（几何 / 相图 / Pareto / 策略对比）
- `figures/fig3-aircombat.svg` — 图 3 临界距离闭式解 / 等值线 / 开火策略
- `figures/fig4-altitude-sam.svg` — 图 4 高低差与地导开火时机
- `figures/fig5-ship.svg` — 图 5 船只自卫三面板
- `figures/fig6-sensitivity.svg` — 图 6 敏感性龙卷风图与过载悬崖
- `scripts/comparative.py` — 受控对比 / 消融 / 敏感性 / 端到端（实验 A–F）
- `scripts/figures.py` — 插图生成（matplotlib，黑白灰论文风，文字转路径）
- `data/*.csv` — 受控对比原始数据
- `main.pdf` — 构建产物

## 构建

```bash
./build.sh          # 生成 main.pdf
./build.sh watch    # 监听改动
```

依赖：`typst` ≥ 0.15（本机 0.15.1），模板 `@preview/easy-paper:0.2.2`。
字体：`Noto Serif CJK SC` / `Noto Sans CJK SC`（均为可变字体，正文显式指定字重 400，
否则 Typst 会取到 Thin 实例）。

## 数据与图的复现

```bash
python paper/scripts/comparative.py all --n 800 --seed 2026   # 约 6 分钟
python paper/scripts/figures.py                               # 约 20 秒
```

## 与上级目录的关系

`../docs/粗版报告.md` 是资料整理粗版（含全部时间码索引与存疑清单）；
`../docs/讲解/`、`../docs/资料/`、`../docs/实验/` 是原始转写、文档抽取与单规则实验；
本目录只保留正式文稿所需的结论、图表与可复现脚本。

## 定稿前需处理

1. **作者与单位**：`author: "参赛队\u{3000}国防科技大学"` 需按赛会要求替换。
2. **日期**：默认取编译当天；如需固定，改为 `datetime(year: 2026, month: 11, day: 9)`。
3. **参考文献补全**：当前 11 条中 5 条为赛会文档，6 条为经典教材/论文；
   若需扩充，优先补反舰导弹防御与武器-目标分配的近年文献。
4. **图内字号**：整页宽图内标注约 6–7 pt，若要求更大字号需按比例调整。
