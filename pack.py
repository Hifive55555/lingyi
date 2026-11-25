#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包「最新智能体 + 小窗」成一个 zip，拷到目标机解压后双击 deploy.bat 即可。

用法（在本目录下）：
    python3 pack.py                 # 生成 dist/灵弈小窗+红方智能体_<时间戳>.zip
    python3 pack.py --with-entitys  # 连平台库 entitys 一起打（约 +60MB，一般不需要）
    python3 pack.py --no-zip        # 只生成 dist/<名字>/ 目录，不压缩（便于用 robocopy 拷）
    python3 pack.py --out /tmp/x    # 换个输出目录
    python3 pack.py --name test     # 自定包名（默认带时间戳）

设计原则（和 deploy.ps1 对齐）：
  * 只打「要装到目标机的东西」：deploy 脚本 + 主智能体 + 战术模块 + 任务表 +
    tools 自检脚本 + 小窗（含 WebView2 宿主 wv2）。
  * 运行时垃圾一律不打：logs/、__pycache__/、*.log、*.bak_*、
    overlay_wv2.exe.WebView2/（WebView2 的 profile 缓存）。
  * entitys（平台库）默认不打，目标机用灵弈自带的。
  * 打完做一次**清单校验**：缺关键文件就报错退出，不会给你一个装不上的包。
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ---- 必打（缺一个就失败）----
REQUIRED = [
    "pack.py",          # installer\build_installer.bat 要用它做暂存
    "deploy.ps1",
    "deploy.bat",
    "README.md",
    "AGENTS.md",        # 给 AI/接手者的硬约束，随包发一份方便现场查
    "智能体代码/Mission_all_red.py",
    "小窗/overlay_ai.py",
    "小窗/overlay/agent.py",
    "小窗/overlay/launcher.py",
    "小窗/overlay/灵弈小窗.bat",
    "小窗/overlay/截图.bat",
    "小窗/overlay/截图.ps1",
    "小窗/overlay/创建快捷方式.bat",
    "小窗/overlay/创建快捷方式.ps1",
    "小窗/overlay/wv2/overlay_wv2.exe",
]

# ---- 有就带上（缺了只警告）----
OPTIONAL = [
    "verify.sh",        # 一键回归（Linux/macOS）
    "verify.py",        # 一键回归（Windows）
    "verify.bat",
    "CLAUDE.md",        # 指向 AGENTS.md
    "智能体代码/Mission_all_blue_hh.py",
    "智能体代码/BattlefieldMonitor.py",
    "智能体代码/SamBattalionDefense.py",
    "智能体代码/ShipClusterDefense.py",
    "智能体代码/战术智能体说明.md",
    "智能体代码/红方人人任务列表.xlsx",
    "智能体代码/蓝方人人任务列表.xlsx",
    "智能体代码/红方人人总任务.txt",
    "智能体代码/蓝方人人总任务.txt",
    "小窗/overlay/web/overlay.html",
    "小窗/overlay/web/overlay.js",
    "小窗/overlay/web/monitor.html",
    "小窗/overlay/web/monitor.js",
    "小窗/overlay/settings.json",
    "小窗/overlay/weapons.json",
    "小窗/overlay/zmqlock.py",
    "小窗/overlay/monitor.py",
    "小窗/overlay/monitor_core.py",
    "小窗/overlay/__init__.py",
    "小窗/overlay/wv2/host.cs",
    "小窗/overlay/wv2/Microsoft.Web.WebView2.Core.dll",
    "小窗/overlay/wv2/Microsoft.Web.WebView2.WinForms.dll",
    "小窗/overlay/wv2/WebView2Loader.dll",
    "小窗/overlay/wv2/构建说明.md",
]

# ---- 整目录带上（按扩展名筛）----
DIRS = [
    ("智能体代码/tools", {".py", ".md"}),
    ("小窗/overlay/web", None),          # None = 不过滤，但照样过 BAD_* 黑名单
    ("installer", {".iss", ".bat", ".md"}),   # Inno Setup 安装包脚本
    ("docs", {".md"}),                        # 架构与数据流 / 协作与合并
]

# ---- 运行时垃圾，永远不打 ----
BAD_DIR_NAMES = {
    "__pycache__", "logs", ".git", ".venv", "venv", "entitys",
    "overlay_wv2.exe.WebView2", ".pytest_cache", ".mypy_cache",
    "build", "dist",                     # pack.py 自己的暂存/产物目录
}
BAD_SUFFIXES = {".pyc", ".pyo", ".log", ".pid", ".tmp", ".zip"}
BAD_PREFIXES = ("~$", ".~lock.")
BAD_SUBSTR = (".bak_", ".bak.", "browser")   # logs/browser 这类旧 Edge profile


def is_bad(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    for part in rel.parts:
        if part in BAD_DIR_NAMES:
            return True
    name = path.name
    if name.startswith(BAD_PREFIXES):
        return True
    if path.suffix.lower() in BAD_SUFFIXES:
        return True
    if any(s in name for s in BAD_SUBSTR):
        return True
    return False


def collect(include_entitys: bool) -> tuple[list[Path], list[str], list[str]]:
    """返回 (要打的文件, 缺失的必打项, 缺失的可选项)"""
    missing_req = [r for r in REQUIRED if not (ROOT / r).is_file()]
    missing_opt = [o for o in OPTIONAL if not (ROOT / o).is_file()]

    files: list[Path] = []
    seen: set[Path] = set()

    def add(p: Path):
        if p.is_file() and p not in seen and not is_bad(p, ROOT):
            seen.add(p)
            files.append(p)

    for rel in REQUIRED + OPTIONAL:
        add(ROOT / rel)

    for rel, exts in DIRS:
        d = ROOT / rel
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if exts is not None and p.suffix.lower() not in exts:
                continue
            add(p)

    if include_entitys:
        ent = ROOT / "智能体代码" / "entitys"
        if ent.is_dir():
            for p in sorted(ent.rglob("*")):
                if p.is_file() and p.suffix.lower() not in {".bak", ".log", ".pyc"}:
                    seen.add(p)
                    files.append(p)
        else:
            missing_opt.append("智能体代码/entitys（--with-entitys 但目录不存在）")

    files.sort(key=lambda p: p.relative_to(ROOT).as_posix())
    return files, missing_req, missing_opt


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="打包最新智能体 + 小窗")
    ap.add_argument("--out", default=str(ROOT / "dist"), help="输出目录（默认 ./dist）")
    ap.add_argument("--name", default="", help="包名（默认 灵弈小窗+红方智能体_<时间戳>）")
    ap.add_argument("--with-entitys", action="store_true", help="连平台库 entitys 一起打")
    ap.add_argument("--no-zip", action="store_true", help="只生成目录，不压缩")
    args = ap.parse_args()

    name = args.name or ("灵弈小窗+红方智能体_" + time.strftime("%Y%m%d_%H%M%S"))
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    files, missing_req, missing_opt = collect(args.with_entitys)

    print("=" * 68)
    print("打包源 :", ROOT)
    print("包  名 :", name)
    print("输出到 :", out_dir)
    print("=" * 68)

    if missing_req:
        print("\n[STOP] 缺关键文件，包会装不上：")
        for m in missing_req:
            print("   -", m)
        print("\n请先补齐再打包（例如 wv2/overlay_wv2.exe 缺失时小窗会退回 msedge，这台机会灰屏）。")
        return 2

    if missing_opt:
        print("\n[WARN] 以下可选文件不存在，将不带：")
        for m in missing_opt:
            print("   -", m)

    # 1) 先铺到暂存目录（保持相对路径），再打成 zip
    #
    # 暂存目录放在 --out 下面，而不是系统临时目录：这台比赛机的
    # %LOCALAPPDATA%\Temp（C:\Users\A\AppData\Local\Temp）不可写，
    # tempfile.mkdtemp() 会直接 FileNotFoundError/no usable temporary directory。
    stage_root = out_dir / (".stage_%d" % os.getpid())
    shutil.rmtree(str(stage_root), ignore_errors=True)
    stage_root.mkdir(parents=True, exist_ok=True)
    stage = stage_root / name
    total = 0
    for p in files:
        rel = p.relative_to(ROOT)
        dst = stage / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        total += p.stat().st_size

    # 2) 包内清单：方便在目标机上核对
    mf = stage / "打包清单.txt"
    lines = [
        "包名 : %s" % name,
        "时间 : %s" % time.strftime("%Y-%m-%d %H:%M:%S"),
        "文件 : %d 个，%.1f MB（未压缩）" % (len(files), total / 1048576),
        "entitys: %s" % ("已包含" if args.with_entitys else "未包含（用灵弈自带的）"),
        "",
        "在目标机上：解压 → 双击 deploy.bat → 按 README.md 走。",
        "",
        "相对路径 / 字节 / sha256",
        "-" * 68,
    ]
    for p in files:
        lines.append("%s\t%d\t%s" % (p.relative_to(ROOT).as_posix(), p.stat().st_size, sha256(p)[:16]))
    mf.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n--- 包内容 ---")
    for p in files:
        print("  %-58s %8.1f KB" % (p.relative_to(ROOT).as_posix(), p.stat().st_size / 1024))
    print("  %-58s %8.1f KB" % ("打包清单.txt", mf.stat().st_size / 1024))

    if args.no_zip:
        final_dir = out_dir / name
        if final_dir.exists():
            shutil.rmtree(final_dir)
        shutil.move(str(stage), str(final_dir))
        print("\n[OK] 目录已生成：%s" % final_dir)
        print("     拷这个目录到目标机后，进目录双击 deploy.bat")
        shutil.rmtree(str(stage_root), ignore_errors=True)
        return 0

    zip_path = out_dir / (name + ".zip")
    tmp_zip = out_dir / (name + ".zip.part")
    if tmp_zip.exists():
        tmp_zip.unlink()
    # UTF-8 文件名（中文目录/文件名），Windows 资源管理器能正确显示
    with zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(stage).as_posix())
    shutil.rmtree(str(stage_root), ignore_errors=True)
    if zip_path.exists():
        zip_path.unlink()
    tmp_zip.rename(zip_path)

    zsize = zip_path.stat().st_size
    print("\n" + "=" * 68)
    print("[OK] 打好：%s" % zip_path)
    print("     文件 %d 个，原始 %.1f MB → 压缩后 %.1f MB"
          % (len(files) + 1, total / 1048576, zsize / 1048576))
    print("     sha256(包) = %s" % sha256(zip_path))
    print("=" * 68)
    print("目标机上：解压到 <灵弈>\\intelligent\\ 下（目录名随意）→ 双击 deploy.bat")
    print("注意：wv2\\overlay_wv2.exe 必须存在，否则小窗会退回 msedge --app（这台机会灰屏）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
