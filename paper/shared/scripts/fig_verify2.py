"""补齐效果验证文档的三类实机证据图。

fig_verify-menus   顶栏菜单与任务工具条（手动指令入口 vs 智能体调度）
fig_verify-rings   选中舰艇后的多层包线环
fig_verify-latency 界面右上角耗时读数（绿→橙）对比

所有裁切坐标基于 2560x1600 原始录屏；只做裁切、放大与标注，不改动像素内容。
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
VIDEO = ROOT / "兵棋录屏/春夏秋冬选手1-对战深蓝智汇/春夏秋冬红方.mp4"
OUT = ROOT / "paper/shared/figures"
FONT = "/nix/store/9swv95wd3z6358f5rcf6fpmal1nx06q5-noto-fonts-cjk-sans-2.004/share/fonts/opentype/noto-cjk/NotoSansCJK-VF.otf.ttc"

INK = (255, 255, 255)
ACC = (255, 96, 64)
WARN = (255, 176, 32)


def frame(cap, t):
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * cap.get(cv2.CAP_PROP_FPS)))
    ok, fr = cap.read()
    if not ok:
        raise RuntimeError(f"取帧失败 t={t}")
    return fr


def font(size):
    return ImageFont.truetype(FONT, size, index=0)


def tag(draw, xy, text, size=26, fg=INK, bg=(0, 0, 0, 190), pad=7):
    f = font(size)
    l, t, r, b = draw.textbbox((0, 0), text, font=f)
    w, h = r - l, b - t
    x, y = xy
    draw.rectangle([x, y, x + w + 2 * pad, y + h + 2 * pad], fill=bg)
    draw.text((x + pad - l, y + pad - t), text, font=f, fill=fg)
    return w + 2 * pad, h + 2 * pad


def arrow(draw, p0, p1, color=ACC, width=4, head=13):
    draw.line([p0, p1], fill=color, width=width)
    v = np.array(p1, dtype=float) - np.array(p0, dtype=float)
    n = np.linalg.norm(v)
    if n < 1:
        return
    u = v / n
    nrm = np.array([-u[1], u[0]])
    base = np.array(p1, dtype=float) - u * head
    pts = [tuple(np.array(p1, dtype=float)), tuple(base + nrm * head * 0.55), tuple(base - nrm * head * 0.55)]
    draw.polygon(pts, fill=color)


def menus(cap):
    """顶栏菜单与任务工具条：手动指令入口可见，接管者归属不可见"""
    fr = frame(cap, 545)[20:136, 0:1200]
    img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
    img = img.resize((int(img.width * 2.3), int(img.height * 2.3)), Image.LANCZOS)
    S = 2.3
    pad_top, pad_bottom = 200, 160
    canvas = Image.new("RGBA", (img.width, img.height + pad_top + pad_bottom), (16, 16, 16, 255))
    canvas.paste(img, (0, pad_top))
    d = ImageDraw.Draw(canvas, "RGBA")

    y_menu = pad_top + int(30 * S)
    y_bar = pad_top + int(100 * S)

    # ① 「任务」菜单
    x_task = int(516 * S)
    arrow(d, (x_task, pad_top - 78), (x_task, y_menu - 16), color=ACC)
    tag(d, (x_task - 180, pad_top - 132), "① 「任务」菜单", size=30)
    # ③ 「智能体调度」菜单
    x_disp = int(627 * S)
    arrow(d, (x_disp + 40, pad_top - 78), (x_disp + 30, y_menu - 16), color=(120, 210, 255))
    tag(d, (x_disp - 30, pad_top - 132), "③ 「智能体调度」菜单", size=30, fg=(150, 220, 255))
    # ② 任务工具条 = 手动指令入口
    x_tools = int(150 * S)
    arrow(d, (x_tools, pad_top + img.height + 62), (x_tools, y_bar + 18), color=WARN)
    tag(d, (x_tools - 150, pad_top + img.height + 72), "② 手动指令入口", size=30, fg=WARN)

    d.rectangle([8, canvas.height - 52, canvas.width - 8, canvas.height - 8], fill=(0, 0, 0, 175))
    d.text((22, canvas.height - 46),
           "界面上没有任何一处显示“当前由操作手还是智能体在指挥”",
           font=font(29), fill=INK)

    canvas.convert("RGB").save(OUT / "fig_verify-menus.png")
    print("→ figures/fig_verify-menus.png")


def rings(cap):
    """选中舰艇后的多层包线环；绿色放射线通向带编号的任务参考点"""
    fr = frame(cap, 26)[480:1440, 154:1280]
    img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    tag(d, (12, 12), "推演 00:26", size=30)
    # 选中单位
    arrow(d, (300, 690), (632, 566), color=ACC)
    tag(d, (150, 696), "① 选中单位（护卫舰）", size=27)
    # 包线环族
    arrow(d, (980, 400), (905, 545), color=WARN)
    tag(d, (640, 372), "② 多层包线环", size=27, fg=WARN)
    # 任务参考点连线
    arrow(d, (430, 176), (452, 214), color=(120, 210, 255))
    tag(d, (110, 150), "③ 任务参考点及连线", size=27, fg=(150, 220, 255))

    img.convert("RGB").save(OUT / "fig_verify-rings.png")
    print("→ figures/fig_verify-rings.png")


def latency(cap):
    """界面右上角两项耗时读数：常规为绿色，超阈值转橙色"""
    times = [60, 300, 590, 610, 700]
    x0, x1, y0, y1 = 2130, 2408, 8, 48
    tiles = []
    for t in times:
        fr = frame(cap, t)[y0:y1, x0:x1]
        img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGB")
        img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
        canvas = Image.new("RGBA", (img.width + 24, img.height + 64), (26, 26, 26, 255))
        canvas.paste(img, (12, 48))
        d = ImageDraw.Draw(canvas, "RGBA")
        tag(d, (10, 8), f"推演 {int(t // 60):02d}:{t % 60:02d}", size=26)
        tiles.append(canvas)

    h = tiles[0].height
    w = sum(t.width for t in tiles) + 12 * (len(tiles) - 1)
    sheet = Image.new("RGBA", (w, h + 52), (18, 18, 18, 255))
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 0))
        x += t.width + 12
    d = ImageDraw.Draw(sheet, "RGBA")
    d.text((14, h + 12), "橙色为超出阈值的高值；界面只给出这两项耗时，不给出任何单位状态数值",
           font=font(26), fill=WARN)
    sheet.convert("RGB").save(OUT / "fig_verify-latency.png")
    print("→ figures/fig_verify-latency.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(VIDEO))
    try:
        menus(cap)
        rings(cap)
        latency(cap)
    finally:
        cap.release()


if __name__ == "__main__":
    main()
