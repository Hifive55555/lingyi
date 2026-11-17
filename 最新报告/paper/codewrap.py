#!/usr/bin/env python3
"""把 ``` 代码块包成 #pseudocode（kind = 代码），使其与图、表并列编号。幂等。"""
import pathlib, re

CAPS = {
    "sections/_parts/a_monitor.typ": ["物理作战域三维监控的逐弹判定"],
    "sections/_parts/ch4_body.typ": ["空战单元自卫：分档掉头、垂直扭动与能量阈值"],
    "sections/_parts/ch5_body.typ": ["空空作战：三种态势共用一个开火圆"],
    "sections/_parts/ch6_body.typ": ["登陆船只集群自卫：三类威胁的分支判定"],
    "sections/_parts/ch7_body.typ": ["地空导弹营：二分支循环与 3/5 Dmax 发弹"],
    "sections/_parts/appendix.typ": ["重现全部实验与插图的命令序列"],
    "sections/03-basic.typ": [
        "任务部署：战前一次性配置与逐周期补发",
        "条令设置：总条令、四层 WRA 与单元级例外",
        "武器挂载：按名匹配，不写死挂载 ID",
    ],
    "sections/04-core.typ": [
        "自动打击：BOL 的闭环自愈",
        "加油规划：条令级替代规则",
        "预警机：阵位带与后撤",
        "任务区动态规划：三段切换",
    ],
}

pat = re.compile(r"```\n(.*?)\n```\n", re.S)

for rel, caps in CAPS.items():
    p = pathlib.Path(rel)
    t = p.read_text(encoding="utf-8")
    if "#pseudocode(" in t:
        continue
    blocks = pat.findall(t)
    if len(blocks) != len(caps):
        print(f"! {rel}: 代码块 {len(blocks)} 个，标题 {len(caps)} 条，跳过")
        continue
    it = iter(caps)

    def repl(m):
        cap = next(it)
        return ("#pseudocode(caption: [" + cap + "])[\n```\n"
                + m.group(1) + "\n```\n]\n")

    t = pat.sub(repl, t)
    if rel.startswith("sections/_parts/"):
        t = '#import "../_lib.typ": pseudocode\n' + t
    elif not t.startswith("#import"):
        pass
    p.write_text(t, encoding="utf-8")
    print("wrapped", rel, len(blocks))
