#!/usr/bin/env python
"""
讲解视频 → 稠密页帧索引
========================
单次顺序解码，每 interval 秒对采样帧做纸面检测+矫正，落盘 1200px 宽正视图，
并记录质量分。目的：把耗时的解码一次性做完，后续聚类/去重/挑选全部离线进行。

用法：
  python scripts/page_index.py --video 讲解/智能体讲解.mp4 --out work/jj/idx --interval 4
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deskew_pages import find_page_quad, warp, quality  # noqa: E402

IDX_W = 1200


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--interval", type=float, default=4.0, help="秒")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        sys.exit("无法打开视频")
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, int(round(fps * args.interval)))
    rows, idx, saved = [], 0, 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if idx % step == 0:
            t = round(idx / fps, 2)
            quad, area = find_page_quad(fr)
            rec = {"frame": idx, "t": t, "area": round(area, 3), "ok": False}
            if quad is not None and area > 0.15:
                w = warp(fr, quad)
                if w is not None:
                    scale = IDX_W / w.shape[1]
                    w = cv2.resize(w, (IDX_W, int(w.shape[0] * scale)),
                                   interpolation=cv2.INTER_AREA)
                    sharp, paper, border, ar, ar_ok = quality(w)
                    rec.update({
                        "sharp": round(sharp, 1), "paper": round(paper, 3),
                        "border": round(border, 3), "ar": round(ar, 3),
                        "score": round(sharp * (0.3 + paper) * (0.3 + border) * ar_ok, 1),
                        "ok": True,
                        "file": f"f{idx:06d}.jpg",
                    })
                    cv2.imwrite(os.path.join(args.out, rec["file"]), w,
                                [cv2.IMWRITE_JPEG_QUALITY, 90])
                    saved += 1
            rows.append(rec)
        idx += 1
        if idx % 6000 == 0:
            print(f"  {idx}/{total} ({idx/total*100:.0f}%)  存 {saved}", flush=True)
    cap.release()
    json.dump({"video": args.video, "fps": fps, "interval": args.interval,
               "frames": rows},
              open(os.path.join(args.out, "index.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    print(f"采样 {len(rows)}，矫正成功 {saved} → {args.out}/")


if __name__ == "__main__":
    main()
