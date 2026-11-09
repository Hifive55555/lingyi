#!/usr/bin/env python
"""
讲解视频 → 扫描件化页面
========================
手持拍摄的手写笔记视频，三段式处理：

  Stage 1  scan      单次顺序解码，逐采样帧检测纸面四边形 + 矫正 + 打分 + dHash
                     → work/<name>/candidates.json （小文件，可反复聚类重跑）
  Stage 2  cluster   按 dHash 时序贪心聚类去重，同一页多次展示只留最优帧
                     → work/<name>/clusters.json
  Stage 3  extract   取最优帧，落盘整页 + 水平分带（供细节转写）
                     → <out>/pageNNN.jpg / pageNNN_a|b|c.jpg / pages.json

说明：
  * 顺序解码，不用随机 seek（部分 mp4 大跨度 seek 会失败）
  * 质量分 = 锐度 × 纸面占比 × 贴边度，被手/笔遮挡或运动模糊会掉分
  * 分带是为了喂多模态模型时提高小字/手写辨识率

用法：
  python scripts/deskew_pages.py scan    --video 讲解/智能体讲解.mp4 --work work/jj
  python scripts/deskew_pages.py cluster --work work/jj
  python scripts/deskew_pages.py extract --video 讲解/智能体讲解.mp4 --work work/jj --out work/jj/scan
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np

CANON_W = 1600
HASH_SIZE = 16


# ---------------------------------------------------------------- 几何
def order_corners(pts):
    pts = np.array(pts, dtype=np.float32).reshape(4, 2)
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)],
                     pts[np.argmax(s)], pts[np.argmax(d)]], dtype=np.float32)


def find_page_quad(bgr):
    """白纸 vs 深色背景 → 纸面四边形"""
    h, w = bgr.shape[:2]
    gray = cv2.GaussianBlur(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None, 0.0
    best, best_area = None, 0.0
    for c in sorted(cnts, key=cv2.contourArea, reverse=True)[:5]:
        a = cv2.contourArea(c)
        if a < 0.12 * w * h or a <= best_area:
            continue
        peri = cv2.arcLength(c, True)
        for eps in (0.02, 0.03, 0.05, 0.08):
            ap = cv2.approxPolyDP(c, eps * peri, True)
            if len(ap) == 4 and cv2.isContourConvex(ap):
                best, best_area = ap.reshape(4, 2), a
                break
        else:
            box = cv2.boxPoints(cv2.minAreaRect(c))
            if cv2.contourArea(box) > best_area:
                best, best_area = box, cv2.contourArea(box)
    return best, best_area / (w * h)


def warp(bgr, quad):
    tl, tr, br, bl = order_corners(quad)
    W = max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl))
    H = max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr))
    if W < 50 or H < 50:
        return None
    dst = np.array([[0, 0], [W, 0], [W, H], [0, H]], np.float32)
    M = cv2.getPerspectiveTransform(np.array([tl, tr, br, bl]), dst)
    out = cv2.warpPerspective(bgr, M, (int(W), int(H)), flags=cv2.INTER_CUBIC)
    return cv2.resize(out, (CANON_W, int(out.shape[0] * CANON_W / out.shape[1])),
                      interpolation=cv2.INTER_AREA)


# ---------------------------------------------------------------- 特征
def dhash(gray, size=HASH_SIZE):
    r = cv2.resize(gray, (size + 1, size), interpolation=cv2.INTER_AREA)
    bits = (r[:, 1:] > r[:, :-1]).flatten()
    val = 0
    for b in bits:
        val = (val << 1) | int(b)
    return val


def hamming(a, b):
    return bin(a ^ b).count("1")


def quality(w):
    g = cv2.cvtColor(w, cv2.COLOR_BGR2GRAY)
    sharp = float(cv2.Laplacian(g, cv2.CV_64F).var())
    paper = float((g > max(120, np.percentile(g, 50))).mean())
    border = np.mean([float((s > 150).mean()) for s in
                      (g[:8, :], g[-8:, :], g[:, :8], g[:, -8:])])
    # 长宽比合理性：笔记页矫正后应为 0.45~0.85
    ar = w.shape[0] / w.shape[1]
    ar_ok = 1.0 if 0.45 <= ar <= 0.85 else 0.3
    return sharp, float(paper), float(border), float(ar), ar_ok


# ---------------------------------------------------------------- Stage 1
def stage_scan(args):
    os.makedirs(args.work, exist_ok=True)
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        sys.exit(f"无法打开视频: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, int(round(fps / args.sample_fps)))
    cand, idx = [], 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if idx % step == 0:
            quad, ar = find_page_quad(fr)
            if quad is not None and ar > 0.15:
                w = warp(fr, quad)
                if w is not None:
                    sharp, paper, border, par, ar_ok = quality(w)
                    small = cv2.cvtColor(
                        cv2.resize(w, (320, max(1, 320 * w.shape[0] // w.shape[1]))),
                        cv2.COLOR_BGR2GRAY)
                    score = sharp * (0.3 + paper) * (0.3 + border) * ar_ok
                    cand.append({
                        "frame": idx, "t": round(idx / fps, 2),
                        "sharp": round(sharp, 1), "paper": round(paper, 3),
                        "border": round(border, 3), "ar": round(par, 3),
                        "area": round(ar, 3), "score": round(score, 1),
                        "hash": str(dhash(small)),
                    })
        idx += 1
        if idx % 3000 == 0:
            print(f"  {idx}/{total} ({idx/total*100:.0f}%)  候选 {len(cand)}", flush=True)
    cap.release()
    out = os.path.join(args.work, "candidates.json")
    json.dump({"video": args.video, "fps": fps, "size": [640, 360],
               "sample_fps": args.sample_fps, "candidates": cand},
              open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"候选 {len(cand)} 帧 → {out}")


# ---------------------------------------------------------------- Stage 2
def stage_cluster(args):
    data = json.load(open(os.path.join(args.work, "candidates.json"), encoding="utf-8"))
    cand = sorted(data["candidates"], key=lambda c: c["frame"])
    cand = [c for c in cand if c["score"] >= args.min_score]
    print(f"质量门限 {args.min_score} → 剩 {len(cand)} 候选")

    clusters = []
    for c in cand:
        h = int(c["hash"])
        for cl in clusters:
            if (c["t"] - cl["last_t"] >= args.min_gap
                    and hamming(h, int(cl["best"]["hash"])) <= args.hash_dist):
                cl["members"].append(c)
                cl["last_t"] = c["t"]
                if c["score"] > cl["best"]["score"]:
                    cl["best"] = c
                break
        else:
            clusters.append({"best": c, "last_t": c["t"], "members": [c]})

    clusters.sort(key=lambda cl: cl["best"]["frame"])
    pages = []
    for n, cl in enumerate(clusters, 1):
        b = cl["best"]
        pages.append({
            "id": f"page{n:03d}", "frame": b["frame"], "t": b["t"],
            "timecode": f"{int(b['t']//3600):02d}-{int(b['t']%3600//60):02d}-{int(b['t']%60):02d}",
            "score": b["score"], "sharp": b["sharp"], "ar": b["ar"],
            "seen": len(cl["members"]),
            "t_all": [m["t"] for m in cl["members"]],
        })
    out = os.path.join(args.work, "clusters.json")
    json.dump({"video": data["video"], "pages": pages},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"聚类 → {len(pages)} 页 → {out}")
    for p in pages:
        print(f"  {p['id']}  {p['timecode']}  score={p['score']:>9}  "
              f"sharp={p['sharp']:>7}  ar={p['ar']:.2f}  seen={p['seen']}")


# ---------------------------------------------------------------- Stage 3
def stage_extract(args):
    meta = json.load(open(os.path.join(args.work, "clusters.json"), encoding="utf-8"))
    pages = meta["pages"]
    os.makedirs(args.out, exist_ok=True)
    cap = cv2.VideoCapture(args.video)
    cur, done = 0, []
    for p in pages:
        target = p["frame"]
        while cur < target:
            if not cap.grab():
                break
            cur += 1
        ok, fr = cap.read()
        cur += 1
        if not ok:
            print(f"  ! {p['id']} frame {target} 读取失败")
            continue
        quad, _ = find_page_quad(fr)
        w = warp(fr, quad) if quad is not None else None
        if w is None:
            print(f"  ! {p['id']} 矫正失败")
            continue
        cv2.imwrite(os.path.join(args.out, f"{p['id']}.jpg"), w,
                    [cv2.IMWRITE_JPEG_QUALITY, 94])
        h = w.shape[0]
        for k in range(args.bands):
            cv2.imwrite(os.path.join(args.out, f"{p['id']}_{'abcde'[k]}.jpg"),
                        w[int(k * h / args.bands):int((k + 1) * h / args.bands)],
                        [cv2.IMWRITE_JPEG_QUALITY, 94])
        p["file"] = f"{p['id']}.jpg"
        p["bands"] = [f"{p['id']}_{'abcde'[k]}.jpg" for k in range(args.bands)]
        done.append(p)
    cap.release()

    json.dump({"video": args.video, "canon_w": CANON_W, "pages": done},
              open(os.path.join(args.out, "pages.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    thumbs = [cv2.imread(os.path.join(args.out, p["file"])) for p in done]
    if thumbs:
        tw, cols = 300, 7
        th = int(tw * thumbs[0].shape[0] / thumbs[0].shape[1])
        rows = (len(thumbs) + cols - 1) // cols
        sheet = np.full((rows * (th + 20), cols * tw, 3), 30, np.uint8)
        for i, im in enumerate(thumbs):
            r, c = divmod(i, cols)
            y, x = r * (th + 20), c * tw
            sheet[y:y + th, x:x + tw] = cv2.resize(im, (tw, th))
            cv2.putText(sheet, f"{i+1}", (x + 3, y + th + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
        cv2.imwrite(os.path.join(args.out, "contact-sheet.jpg"), sheet,
                    [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"\n落盘 {len(done)} 页 → {args.out}/")


# ---------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["scan", "cluster", "extract"])
    ap.add_argument("--video")
    ap.add_argument("--work", default="work/jj")
    ap.add_argument("--out", default=None)
    ap.add_argument("--sample-fps", type=float, default=2.0)
    ap.add_argument("--min-gap", type=float, default=1.5)
    ap.add_argument("--hash-dist", type=int, default=14)
    ap.add_argument("--min-score", type=float, default=60.0)
    ap.add_argument("--bands", type=int, default=3)
    args = ap.parse_args()
    if args.out is None:
        args.out = os.path.join(args.work, "scan")
    {"scan": stage_scan, "cluster": stage_cluster,
     "extract": stage_extract}[args.stage](args)


if __name__ == "__main__":
    main()
