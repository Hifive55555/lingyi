#!/usr/bin/env bash
# 预览 insert/ 下的片段（不改 main.typ）
# 用法：./scripts/preview_inserts.sh   → 生成 .render/inserts.pdf
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .render insert
# 片段中的路径是相对 main.typ 的；预览时把 include 放在 paper/ 下，故改写为 ../ 前缀
sed 's|"schematics/|"../schematics/|g; s|"figures/|"../figures/|g' \
  insert/SCHEMATICS.typ > insert/_preview_sch.typ
sed 's|"figures/|"../figures/|g' insert/EVIDENCE-SECTION.typ > insert/_preview_ev.typ
cat > _preview.typ <<'TYP'
#import "@preview/easy-paper:0.2.2": *
#show: project.with(title: "插入片段预览", author: "x", date: auto,
  abstract: [预览用，不进入正式文稿], keywords: ("preview",))
#set text(font: ((name: "New Computer Modern", covers: "latin-in-cjk"), "Noto Serif CJK SC"), lang: "zh", region: "cn", weight: 400)
= 五张规则示意图
#include "insert/_preview_sch.typ"
= 实战素材
#include "insert/_preview_ev.typ"
TYP
typst compile _preview.typ .render/inserts.pdf 2>&1 | grep -vE "unknown font family|^ *[│╭╰]" || true
rm -f insert/_preview_sch.typ insert/_preview_ev.typ _preview.typ
echo "preview: $(pwd)/.render/inserts.pdf"
