#!/usr/bin/env python3
# 把旧稿里"第 N 章"的硬编码交叉引用改为标签引用，并修正层级变化后的措辞。
import pathlib, re

ROOT = pathlib.Path(__file__).parent
files = list((ROOT / "sections").glob("*.typ")) + list((ROOT / "sections" / "_parts").glob("*.typ"))

# 顺序敏感：先处理区间与复合形式
PAIRS = [
    ("第 4–7 章", "@sec:evade 至 @sec:sam 各节"),
    ("第 4.2 节", "2.3.2 节"),
    ("第 2 章", "@sec:constraints 节"),
    ("第 3 章", "@sec:d0 节"),
    ("第 4 章", "@sec:evade 节"),
    ("第 5 章", "@sec:aircombat 节"),
    ("第 6 章", "@sec:ship 节"),
    ("第 7 章", "@sec:sam 节"),
    ("第 8 章", "@sec:robust 节"),
    ("第 9 章", "@sec:e2e 节"),
    ("第 10 章", "@sec:effect 节"),
    ("第 11 章", "@sec:limits 节"),
    ("第 12 章", "@sec:conclusion 节"),
    # 已有标签形式
    ("第 @sec:d0 章", "@sec:d0 节"),
    ("第 @sec:evade 章", "@sec:evade 节"),
    ("第 @sec:aircombat 章", "@sec:aircombat 节"),
    ("第 @sec:ship 章", "@sec:ship 节"),
    ("第 @sec:sam 章", "@sec:sam 节"),
    ("第 @sec:limits 章", "@sec:limits 节"),
    ("第 @sec:robust 章", "@sec:robust 节"),
    ("第 @sec:e2e 章", "@sec:e2e 节"),
    # 章节措辞
    ("本章汇总第", "本节汇总第"),
    ("本章中，我们将", "本节中，我们将"),
    ("在前面的章节中，我们分别", "在前面的小节中，我们分别"),
    ("后续每一章都在追问", "后续每一节都在追问"),
    ("第 2 章的调用周期", "@sec:constraints 节的调用周期"),
    ("（见第 @sec:evade 章）", "（见 @sec:evade 节）"),
]

for f in files:
    t0 = f.read_text(encoding="utf-8")
    t = t0
    for a, b in PAIRS:
        t = t.replace(a, b)
    # 兜底：形如"第 3 章"的残留
    t = re.sub(r"第 (\d+) 章", r"第 \1 节", t)
    if t != t0:
        f.write_text(t, encoding="utf-8")
        print("patched", f.name)

# 追加：几处特殊措辞（幂等）
EXTRA = [
    ("第 3 章 d0", "2.1.2 节 d0"),
    ("本章后面的受控实验", "本节的受控实验"),
    ("本章汇总第", "本节汇总第"),
]
for f in files:
    t0 = f.read_text(encoding="utf-8"); t = t0
    for a, b in EXTRA:
        t = t.replace(a, b)
    if t != t0:
        f.write_text(t, encoding="utf-8"); print("extra", f.name)
