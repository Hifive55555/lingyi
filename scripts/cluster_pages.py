#!/usr/bin/env python
"""
页帧聚类（ORB 特征匹配）
========================
讲解视频里同一页会被反复展示、推近、拉远。用 ORB + 单应估计做"同一内容"判定，
把 page_index.py 产出的稠密帧聚成若干"内容单元"（同一页/同一局部放大图），
每个单元给出：时间范围、质量最优代表帧、成员帧列表。

为什么不用感知哈希：矫正后的图仍有抖动/缩放，dHash 帧间汉明距离中位数 69/256，
完全无法区分。ORB 对缩放/旋转不敏感，配 RANSAC 单应后内点数很干净。

用法：
  python scripts/cluster_pages.py --idx work/jj/idx --out work/jj/clusters --resize 640
"""
import argparse
import json
import os

import cv2
import numpy as np


def load_frames(idx_dir, rows, resize):
    imgs, meta = [], []
    for r in rows:
        p = os.path.join(idx_dir, r["file"])
        if not os.path.exists(p):
            continue
        g = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
        if g is None:
            continue
        s = resize / g.shape[1]
        g = cv2.resize(g, (resize, max(1, int(g.shape[0] * s))),
                       interpolation=cv2.INTER_AREA)
        imgs.append(g)
        meta.append(r)
    return imgs, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--idx", default="work/jj/idx")
    ap.add_argument("--out", default="work/jj/clusters")
    ap.add_argument("--resize", type=int, default=640)
    ap.add_argument("--min-inliers", type=int, default=30)
    ap.add_argument("--ratio", type=float, default=0.78)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    idx = json.load(open(os.path.join(args.idx, "index.json"), encoding="utf-8"))
    rows = [r for r in idx["frames"] if r.get("ok")]
    imgs, meta = load_frames(args.idx, rows, args.resize)
    print(f"载入 {len(imgs)} 帧")

    orb = cv2.ORB_create(nfeatures=2000, fastThreshold=12)
    kps, des = [], []
    for g in imgs:
        k, d = orb.detectAndCompute(g, None)
        kps.append(k)
        des.append(d)
    print(f"特征提取完成，平均 {np.mean([0 if d is None else len(d) for d in des]):.0f} 点")

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matcher = cv2.FlannBasedMatcher(dict(algorithm=6, table_number=12,
                                         key_size=20, multi_probe_level=2),
                                    dict(checks=50))

    def match_count(i, j, tool="bf"):
        d1, d2 = des[i], des[j]
        if d1 is None or d2 is None or len(d1) < 20 or len(d2) < 20:
            return 0
        try:
            if tool == "bf":
                pairs = bf.knnMatch(d1, d2, k=2)
            else:
                pairs = matcher.knnMatch(d1, d2, k=2)
        except cv2.error:
            return 0
        good = []
        for p in pairs:
            if len(p) == 2 and p[0].distance < args.ratio * p[1].distance:
                good.append(p[0])
        if len(good) < args.min_inliers:
            return 0
        src = np.float32([kps[i][m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst = np.float32([kps[j][m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 4.0)
        if H is None or mask is None:
            return 0
        return int(mask.sum())

    # ---- 贪心聚类：与已有代表帧匹配成功即归入
    clusters = []
    for i in range(len(imgs)):
        best_cl, best_inl = None, 0
        for cl in clusters:
            n = match_count(i, cl["rep"], "flann" if i > 40 else "bf")
            if n > best_inl:
                best_inl, best_cl = n, cl
        if best_cl is not None and best_inl >= args.min_inliers:
            best_cl["members"].append(i)
            # 质量更高则替换代表帧
            if meta[i].get("score", 0) > meta[best_cl["rep"]].get("score", 0):
                best_cl["rep"] = i
        else:
            clusters.append({"rep": i, "members": [i]})
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(imgs)}  聚类数 {len(clusters)}", flush=True)

    out = []
    for n, cl in enumerate(clusters, 1):
        mem = sorted(cl["members"], key=lambda k: meta[k]["t"])
        rep = cl["rep"]
        out.append({
            "id": f"c{n:02d}",
            "rep_frame": meta[rep]["frame"],
            "rep_t": meta[rep]["t"],
            "rep_file": meta[rep]["file"],
            "rep_score": meta[rep].get("score", 0),
            "n_members": len(mem),
            "t_span": [meta[mem[0]]["t"], meta[mem[-1]]["t"]],
            "times": [meta[k]["t"] for k in mem],
            "members": [meta[k]["file"] for k in mem],
        })
    out.sort(key=lambda c: c["t_span"][0])
    json.dump(out, open(os.path.join(args.out, "clusters.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"\n{len(out)} 个内容单元：")
    for c in out:
        print(f"  {c['id']}  {c['t_span'][0]/60:5.1f}–{c['t_span'][1]/60:5.1f} min  "
              f"帧数={c['n_members']:3d}  score={c['rep_score']:7.0f}  {c['rep_file']}")

    # 联络表
    tw, cols = 300, 6
    reps = [cv2.imread(os.path.join(args.idx, c["rep_file"])) for c in out]
    reps = [r for r in reps if r is not None]
    if reps:
        th = int(tw * reps[0].shape[0] / reps[0].shape[1])
        R = (len(reps) + cols - 1) // cols
        sheet = np.full((R * (th + 20), cols * tw, 3), 25, np.uint8)
        for i, (im, c) in enumerate(zip(reps, out)):
            r, q = divmod(i, cols)
            y, x = r * (th + 20), q * tw
            sheet[y:y + th, x:x + tw] = cv2.resize(im, (tw, th))
            cv2.putText(sheet, f"{c['id']} {c['t_span'][0]/60:.0f}m",
                        (x + 3, y + th + 15), cv2.FONT_HERSHEY_SIMPLEX,
                        0.42, (0, 255, 0), 1)
        cv2.imwrite(os.path.join(args.out, "contact-sheet.jpg"), sheet,
                    [cv2.IMWRITE_JPEG_QUALITY, 85])


if __name__ == "__main__":
    main()
