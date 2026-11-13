#!/usr/bin/env python3
# 从 润色后/main.typ 抽取既有章节，按新层级降级后写入 sections/_parts/。
import re, pathlib

SRC = pathlib.Path(__file__).parent.parent / "润色后" / "main.typ"
OUT = pathlib.Path(__file__).parent / "sections" / "_parts"
OUT.mkdir(parents=True, exist_ok=True)
lines = SRC.read_text(encoding="utf-8").split("\n")


def block(a, b, demote=0, name=None):
    seg = lines[a - 1 : b]
    out = []
    for ln in seg:
        m = re.match(r"^(=+)\s+(.*)$", ln)
        if m and not ln.startswith("//"):
            out.append("=" * (len(m.group(1)) + demote) + " " + m.group(2))
        else:
            out.append(ln)
    text = "\n".join(out).strip("\n") + "\n"
    # 图片相对路径：_parts 比 main.typ 深两级
    text = text.replace('"../../shared/', '"../../../../shared/')
    if name:
        (OUT / f"{name}.typ").write_text(text, encoding="utf-8")
    return text


# ---- 抽取 ----
block(56, 76, 0, "a_intro_d0")
block(65, 76, 0, "d0_def")              # 只要正文
block(82, 87, 0, "a_arch")
block(90, 104, 0, "a_rules")
block(106, 129, 0, "a_monitor")
block(138, 144, 0, "a_constraints")
block(146, 206, 2, "ch3")
block(148, 206, 0, "ch3_body")
block(207, 314, 2, "ch4")
block(210, 314, 2, "ch4_body")
block(315, 382, 2, "ch5")
block(318, 382, 2, "ch5_body")
block(383, 473, 2, "ch6")
block(386, 473, 2, "ch6_body")
block(474, 513, 2, "ch7")
block(477, 513, 2, "ch7_body")
block(514, 560, 2, "ch8")
block(517, 560, 2, "ch8_body")
block(561, 620, 2, "ch9")
block(564, 620, 2, "ch9_body")
block(621, 661, 1, "ch10")
block(624, 661, 1, "ch10_body")
block(662, 688, 1, "ch11")
block(665, 688, 1, "ch11_body")
block(689, 703, 1, "ch12")
block(692, 703, 1, "ch12_body")
block(704, 788, 0, "appendix")

# ch3 正文内的三个二级标题改为粗体引导句（避免出现 2.1.2.1 这样的四级编号）
p = OUT / "ch3_body.typ"
t = p.read_text(encoding="utf-8")
t = t.replace("== 一维尾随模型的设置\n\n", "")
t = t.replace("== 对初速超线性、对目标速度二次、对衰减律敏感\n\n", "*三点性质。*")
t = t.replace("== 闭式解与数值二分之间的偏差小于 1%\n\n", "*数值校核。*")
p.write_text(t, encoding="utf-8")

# 附录标题改为不编号的一级标题
p = OUT / "appendix.typ"
t = p.read_text(encoding="utf-8")
t = t.replace("= 附录 A　仿真参数总表",
              '#heading(level: 1, numbering: none, outlined: true)[附录 A　仿真参数总表]')
t = t.replace("= 附录B　重现方法",
              '#heading(level: 1, numbering: none, outlined: true)[附录 B　重现方法]')
t = t.replace("= 附录C　术语与型号对照表",
              '#heading(level: 1, numbering: none, outlined: true)[附录 C　术语与型号对照表]')
p.write_text(t, encoding="utf-8")

print("ok")

# 原文一处标点笔误（"。。"）顺手修掉
p = OUT / "ch3_body.typ"
t = p.read_text(encoding="utf-8").replace("最终得到$t^* = T$。。", "最终得到 $t^* = T$。")
p.write_text(t, encoding="utf-8")
