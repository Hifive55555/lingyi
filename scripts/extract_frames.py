#!/usr/bin/env python
"""从比赛录屏按时间点抽帧（顺序解码，避免大跨度 seek 失败）。

用法: python scripts/extract_frames.py --video <mp4> --out <dir> --every 60
"""
import argparse, os
import cv2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--every", type=int, default=60)
    ap.add_argument("--prefix", default="f")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 16.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = int(round(fps * a.every))
    n = 0
    idx = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if idx % step == 0:
            t = idx / fps
            name = os.path.join(a.out, f"{a.prefix}_{int(t):04d}s.jpg")
            cv2.imwrite(name, fr, [cv2.IMWRITE_JPEG_QUALITY, 92])
            n += 1
        idx += 1
    cap.release()
    print(f"{a.video}: {total} frames, saved {n} → {a.out}")


if __name__ == "__main__":
    main()
