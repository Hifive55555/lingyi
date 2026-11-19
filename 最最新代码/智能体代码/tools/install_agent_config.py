# -*- coding: utf-8 -*-
"""
往灵弈的「智能体编辑」配置里预置两套配置，省得在客户端里一个个点「＋」。

配置文件：<灵弈>\\intelligent\\config\\agentConfig.json
它的结构是三层：

    {
      "<想定id>": {                      # 想定（.scen）自己的 id，一个想定一份
        "<阵营id>": {                    # 想定里的一方（红/蓝），**id 每份想定都不一样**
          "overlay_ai#1": {              # 智能体显示名 = 文件名 + #序号
            "filePath": "overlay_ai.py", # 可以相对（相对 agent_path）也可以绝对
            "id": "<guid>", "Contact": {}, "RefPoint": {}, "unit": {}
          },
          ...
        }
      }
    }

所以**不能**把阵营 id 写死：官方想定里蓝方是 `k55efi-...gip`，换个想定就变成
`K8-00001K7KMJ3EQ` 这种。本脚本的判定办法是：

  1. 已经有 `Mission_all_blue_hh.py` 的那一方 = 蓝方；
  2. 同一想定的另一方，从 `Data\\Recordings\\<想定id>\\*\\simulation.ini` 里的
     `SITUATION_DYNAMIC_*` 键取（排除 GLOBAL），那就是红方；
  3. 文件里一个想定都没有时，用最近一次推演记录的那个想定。

写入内容（两套配置）：
  蓝方：overlay_ai + Mission_all_blue_hh
  红方：overlay_ai + Mission_all_red

用法：
    python install_agent_config.py                 # 写入（先自动备份）
    python install_agent_config.py --dry-run       # 只看会做什么
    python install_agent_config.py --check         # 只打印发现到的想定/阵营
    python install_agent_config.py --root D:\\LingYi --relative
"""

from __future__ import print_function

import argparse
import json
import os
import shutil
import sys
import time
import uuid

BLUE_MODULE = "Mission_all_blue_hh.py"
RED_MODULE = "Mission_all_red.py"
OVERLAY_MODULE = "overlay_ai.py"


# ---------------------------------------------------------------- 找目录
def find_intelligent(start):
    """从脚本位置往上找 intelligent（其下有 config/ 与 ai/），找不到就返回 None"""
    p = os.path.abspath(start)
    for _ in range(8):
        if os.path.isdir(os.path.join(p, "config")) and os.path.isdir(os.path.join(p, "ai")):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent
    return None


def recordings_sides(intelligent, scenario):
    """从推演记录里读该想定的阵营 id 列表（排除 GLOBAL）。

    记录目录长这样（注意 NORMAL 下面还有一层日期）：
        Data\\Recordings\\NORMAL\\20260930\\LOCAL\\<想定id>\\<时间戳>\\simulation.ini
    """
    base = os.path.abspath(os.path.join(intelligent, "..", "Data", "Recordings"))
    if not os.path.isdir(base):
        return []
    sides = []
    for root, dirs, files in os.walk(base):
        # root 是 <想定id>\<时间戳>，所以要比对上一级目录名
        if os.path.basename(os.path.dirname(root)) != scenario or "simulation.ini" not in files:
            continue
        try:
            with open(os.path.join(root, "simulation.ini"), "rb") as f:
                text = f.read().decode("utf-8", "ignore")
        except Exception:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("SITUATION_DYNAMIC_"):
                continue
            sid = line.split("=")[0][len("SITUATION_DYNAMIC_"):].strip()
            if sid and sid.upper() != "GLOBAL" and sid not in sides:
                sides.append(sid)
        if len(sides) >= 2:
            break
    return sides


def newest_scenario(intelligent):
    """最近一次推演用的想定 id（agentConfig 是空的时候拿它起步）"""
    base = os.path.abspath(os.path.join(intelligent, "..", "Data", "Recordings"))
    if not os.path.isdir(base):
        return None
    best, best_t = None, 0.0
    for root, dirs, files in os.walk(base):
        if "simulation.ini" in files:          # root 就是 <想定id> 下的时间戳目录
            scen_dir = os.path.dirname(root)
            t = os.path.getmtime(root)
            if t > best_t:
                best, best_t = os.path.basename(scen_dir), t
    return best


# ---------------------------------------------------------------- 配置读写
def agent_entry(intelligent, module, relative):
    path = module if relative else os.path.join(intelligent, module).replace("\\", "/")
    return {"Contact": {}, "RefPoint": {}, "filePath": path,
            "id": str(uuid.uuid4()), "unit": {}}


def side_has(side_cfg, module):
    for name, cfg in (side_cfg or {}).items():
        fp = str((cfg or {}).get("filePath") or "")
        if os.path.basename(fp.replace("\\", "/")) == module:
            return name
    return None


def ensure_agents(side_cfg, intelligent, modules, relative):
    """把 modules 里缺的智能体补进这一方；返回补了哪些（已存在的不动）"""
    added = []
    for module in modules:
        if side_has(side_cfg, module):
            continue
        base = os.path.splitext(module)[0]
        name, n = base + "#1", 1
        while name in side_cfg:                 # 撞名就往后排 #
            n += 1
            name = "%s#%d" % (base, n)
        side_cfg[name] = agent_entry(intelligent, module, relative)
        added.append(name)
    return added


def main():
    ap = argparse.ArgumentParser(description="预置两套智能体配置（overlay+蓝 / overlay+红）")
    ap.add_argument("--root", default="", help="灵弈根目录（含 intelligent\\），默认自动找")
    ap.add_argument("--scenario", default="", help="只处理这一个想定 id（默认全部）")
    ap.add_argument("--relative", action="store_true", help="filePath 写相对路径（默认绝对）")
    ap.add_argument("--dry-run", action="store_true", help="只打印，不落盘")
    ap.add_argument("--check", action="store_true", help="只打印发现到的想定/阵营")
    args = ap.parse_args()

    if args.root:
        intelligent = os.path.abspath(os.path.join(args.root, "intelligent"))
        if not os.path.isdir(intelligent):
            intelligent = os.path.abspath(args.root)
    else:
        intelligent = find_intelligent(os.path.dirname(os.path.abspath(__file__)))
        if not intelligent:
            print("[STOP] 找不到 intelligent 目录，用 --root <灵弈根目录> 指定")
            return 2

    cfg_path = os.path.join(intelligent, "config", "agentConfig.json")
    print("灵弈 intelligent = %s" % intelligent)
    print("配置文件         = %s" % cfg_path)

    data = {}
    if os.path.isfile(cfg_path):
        try:
            with open(cfg_path, "rb") as f:
                data = json.loads(f.read().decode("utf-8-sig") or "{}")
        except Exception as e:
            print("[STOP] agentConfig.json 解析失败：%s" % e)
            return 2
    if not isinstance(data, dict):
        data = {}

    # 一个想定都没有 -> 用最近一次推演的想定起步
    if not data:
        scen = newest_scenario(intelligent)
        if not scen:
            print("[WARN] 配置是空的，也没有推演记录：先在客户端里打开一次想定，再跑本脚本")
            return 2
        print("[INFO] 配置为空，按最近一次推演的想定起步：%s" % scen)
        data[scen] = {}

    changed = 0
    for scenario in list(data.keys()):
        if args.scenario and scenario != args.scenario:
            continue
        sides = data[scenario]
        if not isinstance(sides, dict):
            continue

        # 1) 蓝方：已经装了 blue_hh 的那一方
        blue = None
        red = None
        for sid, scfg in sides.items():
            if side_has(scfg, BLUE_MODULE):
                blue = sid
            if side_has(scfg, RED_MODULE):
                red = sid

        # 2) 从推演记录补全另一方
        recorded = recordings_sides(intelligent, scenario)
        if blue is None and recorded:
            # 没有线索时：记录里第一个当蓝方（人人版通常蓝先）
            blue = recorded[0]
        if red is None:
            for sid in recorded:
                if sid != blue:
                    red = sid
                    break
        if red is None:
            others = [s for s in sides.keys() if s != blue]
            red = others[0] if others else None

        print("\n想定 %s" % scenario)
        print("  推演记录里的阵营: %s" % (", ".join(recorded) if recorded else "(没找到)"))
        print("  蓝方阵营 id     : %s" % (blue or "(未识别)"))
        print("  红方阵营 id     : %s" % (red or "(未识别)"))
        if args.check:
            continue

        if not blue or not red:
            print("  [WARN] 红/蓝阵营没认全，先跳过这个想定。"
                  "可在客户端里给缺的那一方随便加一个智能体（会生成阵营键），再跑一次本脚本。")
            continue

        for sid, modules, label in ((blue, [OVERLAY_MODULE, BLUE_MODULE], "蓝方"),
                                    (red, [OVERLAY_MODULE, RED_MODULE], "红方")):
            scfg = sides.setdefault(sid, {})
            if not isinstance(scfg, dict):
                scfg = {}
                sides[sid] = scfg
            added = ensure_agents(scfg, intelligent, modules, args.relative)
            if added:
                changed += len(added)
                print("  %s：新增 %s" % (label, ", ".join(added)))
            else:
                print("  %s：已存在，跳过" % label)

    if args.check:
        return 0
    if not changed:
        print("\n没有要改的（两套配置都已在）。")
        return 0
    if args.dry_run:
        print("\n[dry-run] 会写入 %d 个智能体配置，未落盘。" % changed)
        return 0

    stamp = time.strftime("%Y%m%d_%H%M%S")
    if os.path.isfile(cfg_path):
        bak = cfg_path + ".bak_" + stamp
        shutil.copy2(cfg_path, bak)
        print("\n已备份：%s" % bak)

    tmp = cfg_path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4).encode("utf-8"))
    os.replace(tmp, cfg_path)
    print("已写入 %d 个智能体配置：%s" % (changed, cfg_path))
    print("打开客户端「智能体调度 → 智能体编辑」应能看到：overlay_ai + 蓝方/红方 两套。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
