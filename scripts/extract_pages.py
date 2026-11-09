#!/usr/bin/env python
"""
讲解视频 → 页面切片
====================
输入：手持拍摄的手写笔记本翻页讲解视频
输出：每个"页面停留段"里最清晰的一帧 + 元数据

原理：
  1. 以 2 fps 降采样解码，算相邻帧灰度平均绝对差 (diff) 与拉普拉斯锐度
  2. diff 尖峰 = 翻页/大幅移动 → 作为页面边界
  3. 段内取锐度最高帧（避开手抖/遮挡）
  4. 段内时长过短的丢弃（翻页过程中的过渡帧）

用法：
  python scripts/extract_pages.py --video 讲解/智能体讲解.mp4 --out work/jj/pages
"""
import argparse
import json
import os
import subprocess
import sys

import cv2
import numpy as np


def scan(video, sample_fps=2.0):
    """逐帧扫描，返回 (样本表, fps, 尺寸)"""
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        sys.exit(f"无法打开视频: {video}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    step = max(1, int(round(fps / sample_fps)))
    prev = None
    rows = []
    idx = 0
    size = (0, 0)
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if idx == 0:
            size = (fr.shape[1], fr.shape[0])
        if idx % step == 0:
            g = cv2.cvtColor(cv2.resize(fr, (320, 180)), cv2.COLOR_BGR2GRAY)
            mid = cv2.cvtColor(cv2.resize(fr, (640, 360)), cv2.COLOR_BGR2GRAY)
            sharp = float(cv2.Laplacian(mid, cv2.CV_64F).var())
            diff = 255.0 if prev is None else float(
                np.mean(np.abs(g.astype(np.int16) - prev.astype(np.int16)))
            )
            rows.append((t_of(idx, fps), diff, sharp, idx))
            prev = g
        idx += 1
    cap.release()
    return np.array(rows), fps, size


def t_of(frame_no, fps):
    return frame_no / fps


def segment(samples, thresh, min_dur):
    """按 diff 尖峰切段，返回 [(start_t, end_t, peak_row)]"""
    d = samples[:, 1]
    t = samples[:, 0]
    boundaries = [0]
    i = 1
    while i < len(d):
        if d[i] > thresh:
            # 合并连续超阈样本为一个边界
            j = i
            while j < len(d) and d[j] > thresh:
                j += 1
            boundaries.append(i)
            i = j
        else:
            i += 1
    segs = []
    for k in range(len(boundaries)):
        s = boundaries[k]
        e = boundaries[k + 1] if k + 1 < len(boundaries) else len(d)
        if e - s < 2:
            continue
        if t[e - 1] - t[s] < min_dur:
            continue
        sub = samples[s:e]
        best = sub[np.argmax(sub[:, 2])]  # 最清晰帧
        segs.append({"t_start": float(t[s]), "t_end": float(t[e - 1]),
                     "t_peak": float(best[0]), "frame": int(best[3])})
    return segs


def grab(video, frame_nos, outdir, prefix="p"):
    """按帧号取原始分辨率帧"""
    cap = cv2.VideoCapture(video)
    outs = []
    for n, fn in enumerate(frame_nos, 1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fn)
        ok, fr = cap.read()
        if not ok:
            outs.append(None)
            continue
        p = os.path.join(outdir, f"{prefix}{n:03d}.jpg")
        cv2.imwrite(p, fr, [cv2.IMWRITE_JPEG_QUALITY, 92])
        outs.append(p)
    cap.release()
    return outs


def contact_sheet(paths, out, cols=6, thumb_w=320):
    imgs = [cv2.imread(p) for p in paths if p and os.path.exists(p)]
    if not imgs:
        return
    th = int(thumb_w * imgs[0].shape[0] / imgs[0].shape[1])
    rows = (len(imgs) + cols - 1) // cols
    sheet = np.full((rows * (th + 22), cols * thumb_w, 3), 30, np.uint8)
    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        y, x = r * (th + 22), c * thumb_w
        sheet[y:y + th, x:x + thumb_w] = cv2.resize(im, (thumb_w, th))
        cv2.putText(sheet, f"{i+1}", (x + 4, y + th + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.imwrite(out, sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])


def mmss(x):
    return f"{int(x//60):02d}:{int(x%60):02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--thresh", type=float, default=42.0)
    ap.add_argument("--min-dur", type=float, default=4.0)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    samples, fps, (w, h) = scan(args.video)
    np.save(os.path.join(args.out, "motion.npy"), samples)
    print(f"采样 {len(samples)} 个点 @2fps | 视频 {w}x{h} {fps:.3f}fps "
          f"| 时长 {mmss(samples[-1][0])}")

    segs = segment(samples, args.thresh, args.min_dur)
    print(f"阈值 {args.thresh} → 切出 {len(segs)} 段")

    paths = grab(args.video, [s["frame"] for s in segs], args.out)
    for i, (s, p) in enumerate(zip(segs, paths), 1):
        s["id"] = f"p{i:03d}"
        s["timecode"] = f"{int(s['t_start']//3600):02d}-{int(s['t_start']%3600//60):02d}-{int(s['t_start']%60):02d}"
        s["file"] = os.path.basename(p) if p else None

    meta = {"video": args.video, "fps": fps, "size": [w, h],
            "thresh": args.thresh, "min_dur": args.min_dur,
            "segments": segs}
    with open(os.path.join(args.out, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    contact_sheet(paths, os.path.join(args.out, "contact-sheet.jpg"))
    for s, p in zip(segs, paths):
        print(f"  {s['id']}  {mmss(s['t_start'])}–{mmss(s['t_end'])}  "
              f"peak={mmss(s['t_peak'])}  {s['file']}")
    print(f"\n首轮产物 → {args.out}/  联络表 contact-sheet.jpg")


if __name__ == "__main__":
    main()
