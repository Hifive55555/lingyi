# 文稿工程（Typst + easy-paper）

**两篇文稿，共用一套资产，侧重点不同，都是全集。**

| 文稿 | 定位 | 源文件 | 产物 | 规模 |
|---|---|---|---|---|
| **智能体设计报告** | 理论：规则怎么来的、为什么这样写、在仿真里站不站得住；末章简述实机 | `design/main.typ` | `design/main.pdf` | 24 页 / 11 图 / 13 表 |
| **效果验证文档** | 实机：智能体怎么被用上、验证到什么程度；以验证矩阵为主干 | `verify/main.typ` | `verify/main.pdf` | 10 页 / 4 图 / 9 表 |

两篇不重复摆结论：设计报告给"规则是否成立"，效果验证给"规则是否被用上、能否取证"。

## 目录

```
paper/
├── design/main.typ        智能体设计报告（理论侧）
├── verify/main.typ        效果验证文档（实机侧）
├── shared/                两篇共用
│   ├── figures/           图（SVG/PDF/PNG）
│   ├── schematics/        五张规则示意图 + SPEC.md
│   ├── data/              受控对比原始 CSV
│   ├── ref.bib            参考文献
│   └── scripts/           仿真、绘图、合入、预览
├── insert/                待合入片段（示意图 / 实战章节 / 实机部署章）
└── build.sh               一键构建
```

## 构建

```bash
./build.sh            # 两篇都构建
./build.sh design     # 只构建设计报告
./build.sh verify     # 只构建效果验证文档
./build.sh watch      # 监听设计报告
```

依赖：`typst ≥ 0.15`（本机 0.15.1）、模板 `@preview/easy-paper:0.2.2`。
字体：`Noto Serif CJK SC` / `Noto Sans CJK SC`（可变字体，正文显式指定字重 400，
否则 Typst 会取到 Thin 实例）。

## 数据与图复现

```bash
python paper/shared/scripts/comparative.py all --n 800 --seed 2026   # 受控对比（约 6 分钟）
python paper/shared/scripts/figures.py                               # 图 2–6
python paper/shared/scripts/fig_arch.py                              # 图 1 架构
python paper/shared/scripts/fig_schema_a.py                          # 示意图 3、4
python paper/shared/scripts/fig_schema_b.py                          # 示意图 1、2、5
python paper/shared/scripts/fig_evidence.py                          # 实战素材 2 张
python paper/shared/scripts/fig_verify.py                            # 验证文档专用 2 张
```

## 片段合入

`insert/` 里是需要贴进 `design/main.typ` 的片段。合入脚本以**小节标题**为锚点，
只插入不删除，不碰已写好的句子：

```bash
python paper/shared/scripts/merge_inserts.py --dry-run
python paper/shared/scripts/merge_inserts.py      # 自动备份 main.typ.bak
paper/shared/scripts/preview_inserts.sh                  # 预览片段（路径已随目录调整，见下）
```

## 定稿前需处理

1. **作者与单位**：两篇均为 `参赛队\u{3000}国防科技大学`，按赛会要求替换。
2. **日期**：默认取编译当天。
3. **两篇的图号**：由模板自动编号，正文若写死"图 3"需改成 `@fig:` 引用。
4. **效果验证文档的第 8 章**（未验证项与反例）建议保留——它是这份文档最实的部分。
