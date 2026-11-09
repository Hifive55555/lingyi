#!/usr/bin/env python
"""
ASR 转写 → 带章节的 Markdown
============================
把 faster-whisper 的逐段转写按人工标定的章节边界重排成可引用文稿。
章节边界来自通读全文后的判断（见 SECTIONS），可随时调整后重跑。

用法：
  python scripts/build_transcript_md.py --segments work/jj/audio/segments.json \
      --out docs/讲解/00-讲解转写.md
"""
import argparse
import json

# (起始秒, 标题)
SECTIONS = [
    (0, "开场：五个智能体的总体清单"),
    (30, "一、监控智能体（飞机 / 船只 / 地空导弹营共用）"),
    (77, "二、地空导弹营智能体"),
    (153, "三、空战躲避智能体"),
    (287, "　三·附：空战躲避要求的二维表 / 三维曲面验证"),
    (353, "四、船只自卫智能体"),
    (410, "　四·1 卢卡斯无人机（Lucas）"),
    (488, "　四·2 海马斯 / 反舰导弹排"),
    (581, "　四·3 158C / 154C 与双船切向背身"),
    (675, "　四·4 调用飞机（苏 57）驱赶照射机"),
    (715, "五、打空战（空空）智能体"),
    (790, "　五·1 开火距离与追击模型"),
    (930, "　五·2 d 与 d0 的判定、0.8 d0 与 ¾ d0"),
    (1010, "　五·3 迎头 / 逃逸 / 切向三种态势"),
    (1039, "　五·4 双方同高与高度差 80%–120%"),
    (1149, "收尾：求解与验证的分工、1v1 大量重复实验"),
    (1181, "交付要求（格式、时间节点、需要的图）"),
]


def fmt(t):
    t = int(t)
    h, m, s = t // 3600, t % 3600 // 60, t % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--segments", default="work/jj/audio/segments.json")
    ap.add_argument("--out", default="docs/讲解/00-讲解转写.md")
    ap.add_argument("--video", default="讲解/智能体讲解.mp4")
    ap.add_argument("--every", type=float, default=20.0,
                    help="无分段处每隔多少秒起一行，便于检索")
    args = ap.parse_args()

    data = json.load(open(args.segments, encoding="utf-8"))
    segs = data["segments"]

    lines = [
        "# 讲解视频·逐段转写",
        "",
        f"> 源视频：`{args.video}`　时长 {fmt(data['duration'])}　"
        f"模型 faster-whisper {data['model']}（VAD 开启，language=zh）",
        "> 转写为机器识别结果，**未经人工逐句校对**；术语错字见 "
        "`01-手写笔记转写.md` 末尾的对照表。",
        "> 每行 `[时:分:秒]` 为该句起始时间码，可直接回原片定位。",
        "",
        "---",
        "",
    ]

    cur = -1
    last_emit = -1e9
    for s in segs:
        t = s["start"]
        while cur + 1 < len(SECTIONS) and t >= SECTIONS[cur + 1][0]:
            cur += 1
            lines += ["", f"## {SECTIONS[cur][1]}", ""]
            last_emit = t
        if cur < 0:
            cur = 0
            lines += ["", f"## {SECTIONS[0][1]}", ""]
            last_emit = t
        if t - last_emit >= args.every:
            lines.append("")
            last_emit = t
        lines.append(f"`[{fmt(t)}]` {s['text']}")

    open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"{len(segs)} 段 / {len(SECTIONS)} 章 → {args.out}")


if __name__ == "__main__":
    main()
