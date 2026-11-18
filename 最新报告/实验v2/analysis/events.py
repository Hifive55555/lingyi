#!/usr/bin/env python3
"""规则级事件抽取：灵弈平台 stderr 日志 -> data/events.csv（流式，只读）。

输入：远端 `D:/LingYi/exp/v2/logs/<arm>.err` 的本地只读快照（每臂一个文件）。
输出：`data/events.csv`，一行一个规则事件（威胁 / 规避 / 开火 / 地导 / 舰船自卫）。

口径、正则、切分假设与近似项写在 `analysis/README.md` 的「规则级事件抽取」一节；
本文件的 `PATTERNS` / `SAM_ENTRY_PATTERNS` / `KNOWN_NON_EVENT` 与那一节的表格一一对应，
改任一处必须同步另一处。

用法：
    python analysis/events.py                          # 读 raw/logs/*.err -> data/events.csv
    python analysis/events.py --logs /tmp/lingyi_logs   # 指定日志快照目录
    python analysis/events.py --logs A0_new.err B1.err --out /tmp/e.csv

只读：本脚本只打开日志文件读取，不写日志目录、不接触远端。
"""

from __future__ import annotations

import argparse
import ast
import csv
import glob
import os
import re
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# 一、行头与结构性消息
# ---------------------------------------------------------------------------

# 形如 `2026-11-17 23:41:52 - Platform - INFO - <消息>`；其它平台名也接受。
HEAD_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (?P<logger>[^-]+?) - "
    r"(?P<level>[A-Z]+) - (?P<msg>.*)$"
)

# 局（episode）起点：一次进程装载想定 = 一局。日志里 `round` 恒为 1、没有 reset 行，
# 因此用这一行切局；该行里的「第N局」恒为 1，不能当局号。
RE_EPISODE_START = re.compile(r"进程:(\d+),第\d+局,想定'.*?'加载成功")

# 每步一行的心跳：给出仿真时刻与步序，用于把事件对齐到 sim_t。
RE_STEP = re.compile(
    r"process:\d+-(?P<pid>\d+), round:(?P<round>\d+), time:(?P<t>[\d.]+)s, "
    r"step index:(?P<idx>\d+)"
)

# 单元清单：`红方单元清单(Aircraft 12/80)：名字[dbid] | 名字[dbid] | ...`
RE_ROSTER = re.compile(
    r"(?P<side>[红蓝])方单元清单\((?P<cat>\w+) (?P<i>\d+)/(?P<n>\d+)\)：(?P<body>.*)$"
)
RE_ROSTER_ITEM = re.compile(r"([^|]+?)\[(\d+)\]")

# 地导营初始化：给出每座防空营的 Dmax（km），用于 dist/Dmax。
RE_SAM_INIT = re.compile(r"^\[地空导弹营\] 初始化完成：(\{.*\})$")

# 红方 TAC 周期汇总：只用作「解析完整性」的对照计数，不产生事件行。
RE_TAC_SUMMARY = re.compile(
    r"^TAC 汇总：周期\d+ 威胁(\d+) 自卫(\d+) 开火(\d+) 出界纠正(\d+) 指令(\d+)"
)
TAC_KEYS = ("威胁", "自卫", "开火", "出界", "指令")

# ---------------------------------------------------------------------------
# 二、规则级事件的正则（与 README 表格一一对应）
# ---------------------------------------------------------------------------

PATTERNS = [
    # 1) 威胁告警（红方 Mission_tactics_red.monitor()；tgo<=120s 或每 20 周期才打印）
    (
        "threat",
        re.compile(
            r"^威胁\[(?P<unit>.+)\] ← (?P<missile>.+)#(?P<mun>\d+)\s+"
            r"弹速(?P<speed>[\d.]+)km/h 距离(?P<dist>[\d.]+)km "
            r"CPA(?P<cpa>[\d.]+)km 预计(?P<tgo>[\d.]+)s命中"
        ),
    ),
    # 2) 规避动作之一：正横机动（EVADE_MODE='beam'；'away' 时写作「掉头」）
    (
        "evade_beam",
        re.compile(
            r"^规避\[(?P<unit>.+)\] (?:正横机动|掉头)"
            r"（弹速(?P<speed>[\d.]+) 距离(?P<dist>[\d.]+) 门限(?P<gate>[\d.]+)）"
            r"→ 航向(?P<hdg>[\d.]+)° (?P<lat>-?[\d.]+),(?P<lon>-?[\d.]+)"
        ),
    ),
    # 3) 规避动作之二：垂直扭动（VERTICAL_JINK=True 才会出现）
    (
        "evade_jink",
        re.compile(
            r"^规避\[(?P<unit>.+)\] 垂直扭动 → 航向(?P<hdg>[\d.]+)° "
            r"降高(?P<alt>[\d.]+)m"
        ),
    ),
    # 4) 规避开始时接管控制权（退任务）
    (
        "evade_takeover",
        re.compile(r"^规避\[(?P<unit>.+)\] 接管控制（退任务 (?P<mission>.+?)）(?P<ok>.*)$"),
    ),
    # 5) 规避结束
    (
        "evade_end",
        re.compile(r"^规避结束\[(?P<unit>.+)\]（(?P<why>[^）]*)）(?:→ (?P<tail>.*))?$"),
    ),
    # 6) 空战开火（红方 Mission_tactics_red.fire）。本快照红方带对空弹 0 架，实际 0 行。
    (
        "fire_aam",
        re.compile(
            r"^开火\[(?P<unit>.+)\] → (?P<target>.+?)\s+武器(?P<wid>\S+)×(?P<qty>\d+)\s+"
            r"距离(?P<dist>[\d.]+)km ≤ 门限(?P<gate>[\d.]+)km "
            r"\(0\.8d0=(?P<d08>[\d.]+) 射程(?P<rng>[\d.]+) V0=(?P<v0>[\d.]+) "
            r"Va=(?P<va>[\d.]+) 高度比(?P<hr>[\d.]+)\)"
        ),
    ),
    ("fire_aam_rejected", re.compile(r"^开火\[(?P<unit>.+)\] 被拒：(?P<why>.*)$")),
    # 7) 地空导弹营的周期报告（一条日志含多座营，下面再拆条目）
    ("sam_cycle", re.compile(r"^\[地空导弹营\] 周期(?P<cyc>\d+)：(?P<body>.*)$")),
    # 7b) 地导营的平台确认事件（单条一行）
    (
        "sam_intercept",
        re.compile(
            r"^\[地空导弹营\] (?P<unit>.+?) 拦截\[(?P<target>.+)\] "
            r"距离(?P<dist>[\d.]+)km 弹数(?P<qty>\d+) 弹种(?P<wid>\d+)$"
        ),
    ),
    (
        "sam_radar_on",
        re.compile(
            r"^\[地空导弹营\] (?P<unit>.+?) 威胁解除→停车\+开雷达"
            r"(?:，恢复防空值班)?$"
        ),
    ),
    (
        "sam_disengage",
        re.compile(
            r"^\[地空导弹营\] (?P<unit>.+?) 脱离中（原阵位 "
            r"\((?P<lat>-?[\d.]+), (?P<lon>-?[\d.]+)\)，雷达已关）$"
        ),
    ),
    (
        "sam_evade_persist",
        re.compile(
            r"^\[地空导弹营\] (?P<unit>.+?) 已连续规避 (?P<n>\d+) 周期"
            r"[（,，].*$"
        ),
    ),
    (
        "sam_fire_rejected",
        re.compile(r"^\[地空导弹营\] (?P<unit>.+?) 发弹被拒（(?P<why>[^）]*)）$"),
    ),
    # 8) 舰船自卫的周期报告
    (
        "ship_cycle",
        re.compile(
            r"^\[舰船自卫\] 周期(?P<cyc>\d+)：威胁(?P<nthr>\d+)（(?P<who>[^）]*)）[,，]"
            r"\s*动作\[(?P<acts>.*)\]$"
        ),
    ),
]

# 地导营周期报告里每个条目的形态。
SAM_ENTRY_PATTERNS = [
    (
        "sam_fire",
        re.compile(
            r"^(?P<unit>.+?) 发弹→(?P<target>.+)"
            r"\((?P<dist>[\d.]+)km/发弹线(?P<gate>[\d.]+)km\)$"
        ),
    ),
    ("sam_fire_rejected", re.compile(r"^(?P<unit>.+?) 发弹被拒（(?P<why>[^）]*)）$")),
    ("sam_standby", re.compile(r"^(?P<unit>.+?) 目标(?P<dist>[\d.]+)km>(?P<gate>[\d.]+)km 待机$")),
    ("sam_radar_off", re.compile(r"^(?P<unit>.+?) 被瞄准→关雷达\+加速脱离$")),
    ("sam_radar_on", re.compile(r"^(?P<unit>.+?) 威胁解除→停车\+开雷达$")),
    ("sam_evade_timeout", re.compile(r"^(?P<unit>.+?) 规避超时→(?P<why>.*)$")),
]

# 已知的非事件消息（不计入「未匹配」）。按顺序匹配，命中即止。
KNOWN_NON_EVENT = [
    ("monitor", r"^\[三维监控\]"),
    ("sam_radar_resend", r"^\[地空导弹营\] .+雷达[开关]（重发）$"),
    ("sam_doctrine", r"^\[地空导弹营\] .+(对空改为|雷达[开关]$)"),
    ("sam_init", r"^\[地空导弹营\] 初始化完成："),
    ("ship_init", r"^\[舰船自卫\] 初始化完成："),
    ("aircombat_diag", r"^空战诊断："),
    ("boundary", r"^出界\["),
    ("unit_new_position", r"^unit_new_position:"),
    ("capability_check", r"^能力自检"),
    ("capability_detail", r"^\s+· "),
    ("agent_build", r"^AGENT_BUILD="),
    ("roster", r"^[红蓝]方单元(总数|清单)"),
    ("doctrine", r"^(总条令|条令|对空|舰船\[|飞机\[|潜艇\[|挂载\[)"),
    ("mission_setup", r"^(巡逻任务\[|支援任务\[|任务\[|战前移动\[)"),
    ("bol", r"^BOL"),
    ("dead_unit", r"^单元 \S+ 已失效"),
    ("lua_error", r"^执行Lua指令失败"),
    (
        "sim_setup",
        r"^(每步决策推演服务|game_process_id|server_ip:|房间-|话题订阅|设置订阅|"
        r"收到有效全量态势|推演第\d+局处理初始化|已安装指令预算)",
    ),
    ("episode_end", r"^(推演结束|已等待\d+秒取不到更新态势数据|receive end situation)"),
    ("spec_estimate", r"^标定弹速："),
    ("no_fly_zone", r"^禁航区\["),
    ("weapon_doctrine", r"^(单元\[|地面单元\[|单元级武器使用规则|武器\S+：|.+对空条令设置完成|"+ 
                        r"飞机挂载设置完成|挂载设置完成)"),
    ("prebattle_sync", r"^(战前|舰船航线规划完成|支援任务创建完成|巡逻任务创建完成|"
                       r"任务创建完成|起飞|侦察机)"),
    ("bootstrap", r"^(A~|任务级武器使用规则|单元开雷达设置完成|initial 完成|本次实验设置|"
                  r"记录初始位置|Fighter agents|全速机动完成|地面部队机动完成|"
                  r"第\d+局, 当前推演时间|本周期 BOL)"),
]
KNOWN_NON_EVENT_RES = [(name, re.compile(p)) for name, p in KNOWN_NON_EVENT]

# 单元类别 -> unit_kind（与 metrics.py 的 air/sea/land 三分类一致）
CAT_TO_KIND = {"Aircraft": "air", "Ship": "sea", "Submarine": "sea", "Facility": "land"}

CSV_COLUMNS = [
    "arm", "episode_idx", "sim_t", "step_index", "event", "unit", "unit_kind",
    "opponent", "missile", "dist_km", "speed_kmh", "gate_km", "d0_km", "cpa_km",
    "tgo_s", "ratio_gate", "dmax_km", "ratio_dmax", "evade_phase", "detail", "raw",
]

# 同一单元的两次「规避[...]」相隔超过这个秒数就视为新的规避（EVADE_MAX_SEC=120 的 2 倍）
EVADE_SPLIT_SEC = 240.0


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return ""


def _ratio(a, b):
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return ""
    if b <= 0:
        return ""
    return round(a / b, 4)


class EpisodeState:
    """一局（一次进程装载想定）内的解析状态。"""

    __slots__ = ("idx", "kind_of", "side_of", "dmax", "sim_t", "step_index",
                 "evade_open", "tac", "rows")

    def __init__(self, idx):
        self.idx = idx
        self.kind_of = {}
        self.side_of = {}
        self.dmax = {}
        self.sim_t = 0.0
        self.step_index = 0
        self.evade_open = {}
        self.tac = Counter()
        self.rows = 0


class Parser:
    """单个 .err 的流式解析器：喂一行，吐若干事件行。"""

    def __init__(self, arm, writer, stats, prefixes):
        self.arm = arm
        self.writer = writer
        self.stats = stats
        self.prefixes = prefixes      # 未匹配消息前缀计数（独立 Counter，便于跨文件合并）
        self.st = None
        # 每局的「起始行」延迟到该局结束（或文件读尽）时写，这样才能填上步数；
        # 它给 rule_metrics 提供分母（含 0 事件的局），不参与事件计数。
        self.pending = None

    # -- 局边界 -------------------------------------------------------------
    def _new_episode(self):
        self.flush_episode_row()
        self.st = EpisodeState(self.stats["episodes"] + 1)
        self.stats["episodes"] += 1
        self.pending = self.st

    def flush_episode_row(self):
        """写上一局的 episode_start 行（step_index=该局观测到的最后步序）。"""
        st = self.pending
        if st is None:
            return
        self.pending = None
        for k, v in st.tac.items():          # 红方 TAC 汇总的累计值（用于完整性核对）
            self.stats["tac:" + k] += v
        row = self._row("episode_start", "steps=%d" % st.step_index, st=st, count=False)
        row["step_index"] = st.step_index
        row["detail"] = "steps=%d" % st.step_index
        self.writer.writerow(row)

    # -- 行 ----------------------------------------------------------------
    def feed(self, raw_line):
        line = raw_line.rstrip("\n")
        m = HEAD_RE.match(line)
        if not m:
            self.stats["continuation"] += 1
            return
        msg = m.group("msg")
        self.stats["msg_lines"] += 1

        if RE_EPISODE_START.search(msg):
            self._new_episode()
            return
        st = self.st
        if st is None:
            self.stats["pre_episode"] += 1
            return

        mh = RE_STEP.search(msg)
        if mh:
            t = float(mh.group("t"))
            if st.step_index and int(mh.group("idx")) <= st.step_index and t < st.sim_t - 60:
                self.stats["resegmented"] += 1
                self._new_episode()
                st = self.st
            st.sim_t = t
            st.step_index = int(mh.group("idx"))
            self.stats["step_lines"] += 1
            return

        mr = RE_ROSTER.search(msg)
        if mr:
            side = mr.group("side") + "方"
            kind = CAT_TO_KIND.get(mr.group("cat"), "")
            items = RE_ROSTER_ITEM.findall(mr.group("body"))
            for name, _dbid in items:
                name = name.strip()
                st.kind_of[name] = kind
                st.side_of[name] = side
            self.stats["roster_lines"] += 1
            self.stats["roster_units"] += len(items)
            return

        ms = RE_SAM_INIT.match(msg)
        if ms:
            try:
                d = ast.literal_eval(ms.group(1))
                st.dmax.update({k: float(v) for k, v in (d.get("Dmax") or {}).items()})
            except (ValueError, SyntaxError):
                self.stats["bad_sam_init"] += 1
            self.stats["sam_init_lines"] += 1
            return

        for name, rx in PATTERNS:
            mm = rx.match(msg)
            if not mm:
                continue
            if name == "sam_cycle":
                self._emit_sam_cycle(msg, mm)
            elif name == "ship_cycle":
                self._emit_ship_cycle(msg, mm)
            else:
                self._emit_event(name, msg, mm)
            return

        if RE_TAC_SUMMARY.match(msg):
            self.stats["non_event:tac_summary"] += 1
            for key, g in zip(TAC_KEYS, RE_TAC_SUMMARY.match(msg).groups()):
                st.tac[key] += int(g)
            return

        for name, rx in KNOWN_NON_EVENT_RES:
            if rx.match(msg):
                self.stats["non_event:" + name] += 1
                return

        self.stats["unmatched"] += 1
        self.prefixes[re.sub(r"[\[（(].*", "", msg)[:24]] += 1

    # -- 输出 --------------------------------------------------------------
    def _row(self, event, msg, st=None, count=True):
        st = st or self.st
        self.stats["rows_by_event:" + event] += 1
        if count:
            st.rows += 1
            self.stats["rows"] += 1
        row = {c: "" for c in CSV_COLUMNS}
        row.update({"arm": self.arm, "episode_idx": st.idx,
                    "sim_t": round(st.sim_t, 1), "step_index": st.step_index,
                    "event": event, "raw": msg[:400]})
        return row

    def _write(self, row):
        self.writer.writerow(row)

    def _kind(self, name):
        return self.st.kind_of.get(name, "")

    def _evade_phase(self, unit):
        """「规避[...]」行是本次规避的触发点（start）还是重画航线（replot）。

        规避航路每 REPLOT_SEC(30s) 至少重画一次，一次规避因此会有多行「正横机动」，
        其 dist 已比触发时更小；只有第一行反映规则真正触发的距离。
        """
        st = self.st
        cur = st.evade_open.get(unit)
        if cur is None or st.sim_t - cur > EVADE_SPLIT_SEC:
            st.evade_open[unit] = st.sim_t
            return "start"
        st.evade_open[unit] = st.sim_t
        return "replot"

    def _emit_event(self, name, msg, mm):
        g = mm.groupdict()
        row = self._row(name, msg)
        unit = (g.get("unit") or "").strip()
        row["unit"] = unit
        row["unit_kind"] = self._kind(unit)

        if name == "threat":
            row["missile"] = g["missile"].strip()
            row["opponent"] = row["missile"]
            row["dist_km"] = _num(g["dist"])
            row["speed_kmh"] = _num(g["speed"])
            row["cpa_km"] = _num(g["cpa"])
            row["tgo_s"] = _num(g["tgo"])
            row["detail"] = "mun#%s" % g["mun"]
        elif name == "evade_beam":
            row["evade_phase"] = self._evade_phase(unit)
            row["dist_km"] = _num(g["dist"])
            row["speed_kmh"] = _num(g["speed"])
            row["gate_km"] = _num(g["gate"])
            row["ratio_gate"] = _ratio(g["dist"], g["gate"])
            row["detail"] = "hdg%s lat,lon=%s,%s" % (g["hdg"], g["lat"], g["lon"])
        elif name == "evade_jink":
            row["evade_phase"] = self._evade_phase(unit)
            row["detail"] = "hdg%s alt_m=%s" % (g["hdg"], g["alt"])
        elif name == "evade_takeover":
            row["evade_phase"] = "start"
            row["detail"] = g["mission"].strip()
        elif name == "evade_end":
            self.st.evade_open.pop(unit, None)
            row["detail"] = "reason=%s tail=%s" % (g["why"], (g.get("tail") or "").strip())
        elif name == "fire_aam":
            row["opponent"] = g["target"].strip()
            row["missile"] = g["wid"]
            row["dist_km"] = _num(g["dist"])
            row["gate_km"] = _num(g["gate"])
            row["d0_km"] = round(float(g["d08"]) / 0.8, 3)   # 日志固定打印 0.8*d0
            row["ratio_gate"] = _ratio(g["dist"], g["gate"])
            row["detail"] = "qty=%s rng_km=%s V0=%s Va=%s height_ratio=%s" % (
                g["qty"], g["rng"], g["v0"], g["va"], g["hr"])
        elif name == "fire_aam_rejected":
            row["detail"] = g["why"].strip()
        elif name == "sam_intercept":
            row["opponent"] = g["target"].strip()
            row["missile"] = g["wid"]
            row["dist_km"] = _num(g["dist"])
            row["detail"] = "qty=%s weapon=%s" % (g["qty"], g["wid"])
        elif name == "sam_disengage":
            row["detail"] = "origin=%s,%s" % (g["lat"], g["lon"])
        elif name == "sam_evade_persist":
            row["detail"] = "consecutive_cycles=%s %s" % (
                g["n"], msg.split("周期", 1)[-1].lstrip("，,"))
        elif name == "sam_fire_rejected":
            row["detail"] = "why=%s" % g["why"]
        self._write(row)

    def _emit_sam_cycle(self, msg, mm):
        cyc = mm.group("cyc")
        for entry in _sam_split(mm.group("body")):
            if entry == "无动作":
                self.stats["non_event:sam_noop"] += 1
                continue
            hit = None
            for name, rx in SAM_ENTRY_PATTERNS:
                g = rx.match(entry)
                if g:
                    hit = (name, g)
                    break
            if hit is None:
                row = self._row("sam_unparsed", "周期%s：%s" % (cyc, entry))
                self.stats["unmatched_sam_entry"] += 1
                self._write(row)
                continue
            name, g = hit
            gd = g.groupdict()
            unit = (gd.get("unit") or "").strip()
            row = self._row(name, "周期%s：%s" % (cyc, entry))
            row["unit"] = unit
            row["unit_kind"] = self._kind(unit)
            dmax = self.st.dmax.get(unit, "")
            row["dmax_km"] = dmax
            if name in ("sam_fire", "sam_standby"):
                row["dist_km"] = _num(gd["dist"])
                row["gate_km"] = _num(gd["gate"])
                row["ratio_gate"] = _ratio(gd["dist"], gd["gate"])
                row["ratio_dmax"] = _ratio(gd["dist"], dmax)
                if name == "sam_fire":
                    row["opponent"] = gd["target"].strip()
            elif name == "sam_fire_rejected":
                row["detail"] = "why=%s" % gd["why"]
            elif name == "sam_evade_timeout":
                row["detail"] = "why=%s" % gd["why"]
            self._write(row)

    def _emit_ship_cycle(self, msg, mm):
        n_thr = int(mm.group("nthr"))
        acts = mm.group("acts").strip()
        if n_thr == 0 and not acts:
            self.stats["non_event:ship_idle"] += 1
            return
        row = self._row("ship_defense", msg)
        row["detail"] = "cycle=%s threats=%d who=%s actions=[%s]" % (
            mm.group("cyc"), n_thr, mm.group("who").strip(), acts)
        for name, kind in self.st.kind_of.items():
            if kind == "sea" and name in acts:
                row["unit"] = name
                row["unit_kind"] = "sea"
                break
        self._write(row)


def _sam_split(body):
    """把 `['a 发弹→X(1km/发弹线2km)', 'b 待机']` 拆成条目。

    条目之间用 `', '`（带引号）分隔，单个条目内可能用「；」拼了两段动作。
    """
    s = body.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    out = []
    for chunk in re.split(r"'\s*,\s*'", s):
        for item in chunk.split("；"):
            item = item.strip().strip("'").strip()
            if item:
                out.append(item)
    return out


def _episode_arm_name(path):
    base = os.path.basename(path)
    return base[:-4] if base.endswith(".err") else os.path.splitext(base)[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description="灵弈日志 -> 规则级事件 CSV（流式，只读）")
    ap.add_argument("--logs", nargs="+", default=[os.path.join("raw", "logs")],
                    help="日志快照目录或 .err 文件列表（默认 raw/logs）")
    ap.add_argument("--out", default=os.path.join("data", "events.csv"))
    ap.add_argument("--top-unmatched", type=int, default=12,
                    help="打印最常见的未匹配消息前缀条数")
    args = ap.parse_args(argv)

    paths = []
    for p in args.logs:
        if os.path.isdir(p):
            paths.extend(sorted(glob.glob(os.path.join(p, "*.err"))))
        elif os.path.exists(p):
            paths.append(p)
        else:
            print("跳过不存在的路径：%s" % p, file=sys.stderr)
    if not paths:
        print("没有找到 .err 日志：%s" % args.logs, file=sys.stderr)
        return 2

    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    grand = Counter()
    grand_prefixes = Counter()
    with open(args.out, "w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for path in paths:
            arm = _episode_arm_name(path)
            stats = Counter()
            prefixes = Counter()
            p = Parser(arm, writer, stats, prefixes)
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    p.feed(line)
                p.flush_episode_row()
            grand.update(stats)
            grand_prefixes.update(prefixes)
            denom = stats["msg_lines"] or 1
            print("[%s] 事件行=%d 局数=%d 消息行=%d 未匹配=%d（%.3f%%）" % (
                arm, stats["rows"], stats["episodes"], stats["msg_lines"],
                stats["unmatched"], 100.0 * stats["unmatched"] / denom))
            for pref, cnt in prefixes.most_common(args.top_unmatched):
                print("    未匹配前缀 %-24r %d" % (pref, cnt))

    print("\n== 汇总 ==")
    print("臂数=%d 装载局数=%d 事件行=%d" % (
        len(paths), grand["episodes"], grand["rows"]))
    print("消息行=%d（续行/traceback=%d，局前=%d）" % (
        grand["msg_lines"], grand["continuation"], grand["pre_episode"]))
    denom = grand["msg_lines"] or 1
    print("未匹配行=%d（%.3f%% of 消息行）" % (grand["unmatched"],
                                              100.0 * grand["unmatched"] / denom))
    print("完整性核对（红方 TAC 汇总累计 vs 解析出的行数）：")
    for tac_key, ev in (("威胁", "threat"), ("自卫", "evade_beam"), ("开火", "fire_aam")):
        print("  %s：TAC=%d  解析=%d" % (ev, grand["tac:" + tac_key],
                                       grand["rows_by_event:" + ev]))
    print("  注：threat 行受 monitor() 节流（tgo<=120s 或每 20 周期），故解析数 < TAC 数；"
          "evade_beam 与 TAC 自卫应逐条相等。")
    print("事件分布：")
    for k, v in sorted(((k.split(":", 1)[1], v) for k, v in grand.items()
                        if k.startswith("rows_by_event:")), key=lambda kv: -kv[1]):
        print("  %-22s %d" % (k, v))
    if grand_prefixes:
        print("未匹配前缀 Top%d：" % args.top_unmatched)
        for pref, cnt in grand_prefixes.most_common(args.top_unmatched):
            print("  %-30r %d" % (pref, cnt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
