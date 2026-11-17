#!/usr/bin/env bash
# 预览 insert/ 下的片段（不改 design/main.typ）
# 用法：./shared/scripts/preview_inserts.sh  → paper/.render/inserts.pdf
set -euo pipefail
cd "$(dirname "$0")/../.."          # → paper/
mkdir -p .render
# insert/ 里的片段用 ../shared/ 相对路径，与 design/main.typ 一致，可直接 include
cat > _preview.typ <<'TYP'
#import "@preview/easy-paper:0.2.2": *
#show: project.with(title: "插入片段预览", author: "x", date: auto,
  abstract: [预览用，不进入正式文稿], keywords: ("preview",))
#set text(font: ((name: "New Computer Modern", covers: "latin-in-cjk"), "Noto Serif CJK SC"), lang: "zh", region: "cn", weight: 400)
#show heading: set text(weight: 600)
= 五张规则示意图
#include "insert/SCHEMATICS.typ"
= 实战素材
#include "insert/EVIDENCE-SECTION.typ"
TYP
typst compile --root . _preview.typ .render/inserts.pdf 2>&1 \
  | grep -vE "unknown font family|^ *[│╭╰]" || true
rm -f _preview.typ
echo "preview: $(pwd)/.render/inserts.pdf"
