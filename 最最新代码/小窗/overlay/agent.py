# -*- coding: utf-8 -*-
"""灵弈小窗的客户端智能体（跟网页版指挥台是两个项目，代码、端口都不共用）
  只做两件事：1. 每步把我方单元 / 敌方情报推给小窗（WebSocket 127.0.0.1:8760/ws）
             2. 执行小窗发来的指令：attack（武器分配）/ unchase（停止追打）/ throttle（油门）/ alt（高度）
                / sam_mode（防空值班：地空导弹 打击⇄机动，雷达 骗弹⇄机动）
  飞机够不着 / 还停着时 attack 走“追打”：退出任务、起飞、飞到射程内再分配武器，打完回原任务；除此之外不自己打仗、不换挂载、不躲弹
  sam_mode 只负责把姿态下给单元，并在被弹瞄准时自动切回机动；状态文件跟 SamBattalionDefense.py 共用
  （%LOCALAPPDATA%\\LingYiOverlay，可用 LY_SAM_STATE_DIR 改）
客户端：添加智能体选 agent/overlay_ai.py，类名 Agent"""
import asyncio
import json
import logging
import math
import os
import sys
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

_AI_DIR = str(Path(__file__).resolve().parents[2])
if _AI_DIR not in sys.path:
    sys.path.insert(0, _AI_DIR)

from aiohttp import web, WSMsgType  # noqa: E402
from engine.LingYi.entitys.player import Player  # noqa: E402
from engine.LingYi.entitys.global_util import Throttle, AirValidStatus, ContactType, WeaponControlStatus  # noqa: E402
from . import zmqlock  # noqa: E402

zmqlock.install()           # 小窗指令在工作线程里下，跟平台 step 线程共用一个 zmq 口，排队收发

log = logging.getLogger("灵弈小窗")
log.setLevel(logging.INFO)
HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get("LY_OVERLAY_PORT", "8760"))
DECISION_SEC = 5
NET_RETRY = 3
THROTTLES = {t.name: t for t in Throttle}
SKIP_TYPES = {2005, 2006}           # 箔条 / 干扰弹 / 诱饵；3xxx 是吊舱 / 副油箱
DOM_I = {"air": 2, "sur": 3, "land": 4, "sub": 5}       # _weapons 每行里这类目标的射程（海里）在第几列
CHASE_AIM = 0.8                     # 追打：航线画到射程 80% 处
CHASE_FIRE = 0.95                   # 进射程 95% 就分配武器
CHASE_PLOT_SEC = 30                 # 航线最快 30 秒重画一次（指令有限额），目标挪够 3km 才画，120 秒兜底重画
CHASE_PLOT_KM = 3
CHASE_PLOT_MAX_SEC = 120
CHASE_RETRY_SEC = 15                # 分配武器被拒：隔 15 秒再试，最多 6 次
CHASE_TRIES = 6
CHASE_LAUNCH_SEC = 30               # 起飞：隔 30 秒再试，被拒 8 次或 15 分钟还没升空就放弃
CHASE_LAUNCH_FAILS = 8
CHASE_LAUNCH_MAX_SEC = 900
CHASE_SHOT_SEC = 90                 # 分配后等实射（看余弹）最多 90 秒，再回原任务
CHASE_RTB_GRACE = 30                # 刚取消返航的 30 秒内不算“又返航了”
try:
    _TYPES = {int(k): v.get("type") for k, v in
              json.loads((HERE / "weapons.json").read_text(encoding="utf-8"))["weapons"].items()}
except Exception:
    _TYPES = {}

# ---------------------------------------------------------------------------- 防空值班（地空导弹 / 雷达）
# 与 SamBattalionDefense.py 共用的状态目录；小窗写指令，智能体写状态。
# sam_intent.json 只有这里写，sam_state.json 只有任务智能体写，各写各的就不会打架。
SAM_KEYWORDS = ('爱国者', '地空导弹连', '地空导弹营', '地空导弹排', '地空导弹分队',
                '霍克', 'patriot', 'hawk', 'sam bty', 'sam coy')
HAWK_KEYWORDS = ('霍克', 'hawk', 'mim-23')
RADAR_KEYWORDS = ('雷达', 'tpq', 'tps', 'mpq', 'radar')
RADAR_SKIP = ('固定', 'fixed', '铺路爪', 'fps-115', 'fps115')
DIR_N, DIR_W, DIR_S = 0.0, 270.0, 180.0
_DIR_CN = {0: "正北", 90: "正东", 180: "正南", 270: "正西"}
_DIR_BRG = {"N": DIR_N, "E": 90.0, "S": DIR_S, "W": DIR_W}


def _DIR_LETTER(brg):
    b = float(brg) % 360.0
    if b < 45 or b >= 315:
        return "N"
    if b < 135:
        return "E"
    if b < 225:
        return "S"
    return "W"


SAM_STATE_FRESH_SEC = 30        # 任务智能体状态多久之内算“它在跑”
SAM_MOVE_KM = 100.0


def _sam_dir():
    d = os.environ.get("LY_SAM_STATE_DIR")
    if not d:
        base = (os.environ.get("LOCALAPPDATA") or os.environ.get("TEMP")
                or os.path.expanduser("~"))
        d = os.path.join(base, "LingYiOverlay")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d


def _sam_read(name):
    try:
        with open(os.path.join(_sam_dir(), name), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _sam_write(name, data):
    path = os.path.join(_sam_dir(), name)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, path)
        return True
    except Exception:
        return False


def _norm_name(text):
    t = str(text or "").lower()
    for ch in (' ', '\u3000', '"', '“', '”', "'", '-', '.', '/',
               '(', ')', '（', '）', '[', ']', '【', '】'):
        t = t.replace(ch, '')
    return t


def _sam_role(name):
    """'sam' / 'radar' / None。"""
    bare = _norm_name(name)
    if any(_norm_name(k) in bare for k in SAM_KEYWORDS):
        return "sam"
    if any(_norm_name(k) in bare for k in RADAR_SKIP):
        return None
    if any(_norm_name(k) in bare for k in RADAR_KEYWORDS):
        return "radar"
    return None


def _sam_default_dir(name, role):
    if role == "radar":
        return DIR_S
    if any(_norm_name(k) in _norm_name(name) for k in HAWK_KEYWORDS):
        return DIR_W
    return DIR_N


def _sam_default_mode(role):
    """没接到任务智能体的状态时，界面按这个默认值显示：
    地空导弹 = 机动模式（开局全速跑），雷达 = 骗弹模式（停车开雷达）。"""
    return "bait" if role == "radar" else "maneuver"


def _sam_dest(lat, lon, brg, km):
    """从 (lat, lon) 沿方位 brg 走 km 后的点。"""
    d = km / 6371.0
    br = math.radians(brg)
    p1, l1 = math.radians(lat), math.radians(lon)
    p2 = math.asin(math.sin(p1) * math.cos(d) + math.cos(p1) * math.sin(d) * math.cos(br))
    l2 = l1 + math.atan2(math.sin(br) * math.sin(d) * math.cos(p1),
                         math.cos(d) - math.sin(p1) * math.sin(p2))
    return (math.degrees(p2), (math.degrees(l2) + 540.0) % 360.0 - 180.0)


def _f(x, nd=4):
    try:
        return round(float(x), nd)
    except (TypeError, ValueError):
        return None


def _get(o, k, default=None):
    if isinstance(o, dict):
        for kk in (k, k.lower(), k.upper()):
            if kk in o:
                return o[kk]
        return default
    return getattr(o, k, default)


def _pos(o):
    lat, lon = _get(o, "Lat"), _get(o, "Lon")
    if lat is None or lon is None or (lat == 0.0 and lon == 0.0):
        return None
    return lat, lon


def _km(a, b):
    dn = (a[0] - b[0]) * 111.32
    de = (a[1] - b[1]) * 111.32 * math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot(dn, de)


def _dom(c):
    ty = _get(c, "Type")
    return "air" if ty in (0, 1) else "sur" if ty in (2, 4) else "sub" if ty == 3 else "land"


def _rtb(u):
    try:
        return u.get_status_type() == AirValidStatus.InAirRTB
    except Exception:
        return False


def _airborne(u):
    try:
        return u.get_status_type() in (AirValidStatus.InAir, AirValidStatus.InAirRTB)
    except Exception:
        return (getattr(u, "CurrentAltitude", 0) or 0) > 50 and _pos(u) is not None


def _reply(r):
    """(成功, 文字)；网络吞的返回 None 让上层重发"""
    res = getattr(r, "result", b"")
    t = res.decode("utf-8", "replace") if isinstance(res, (bytes, bytearray)) else str(res or "")
    try:
        bad = int(getattr(r, "code", 0)) != 0
    except (TypeError, ValueError):
        bad = False
    if any(k in t for k in ("网络", "超时", "取消下发")) or (bad and not t.strip()):
        return None, t or "网络失败"
    if bad or "失败" in t or "超出" in t:
        return False, t
    return True, t


class OverlayAgent(Player):
    def __init__(self, side_name="蓝方", *a, **k):
        super().__init__(side_name)
        self.side_cn = side_name
        self.agent_type = "OverlayAgent"
        self.agent_decision_time = DECISION_SEC
        self.now = 0.0
        self.snapshot = {"t": 0, "units": [], "contacts": []}
        self.fuel_peak = {}
        self.lock = threading.RLock()
        self.server = None
        self.cts = {}               # 情报（每步 situation 里给）
        self.host_mem = {}          # 飞机 -> 宿主名（宿主没了也还归原来那一片）
        self.chase = {}             # 飞机 -> 追打状态，只在指令工作线程里改（见 _chase_tick）
        self.tick_busy = False
        self.notes = []             # [序号, 文字, 成功否]：追打过程的提示，随快照推给小窗
        self.note_n = 0
        self.sam_modes = {}         # guid -> 'strike' / 'maneuver' / 'bait'
        self.sam_units = {}         # guid -> {'name','role','dir'}
        self.sam_seq = 0            # sam_intent.json 的序号（点一次 +1）
        self.sam_state_at = 0.0     # 上次读到任务智能体状态文件的时刻
        self.sam_owned = set()      # 这些 guid 由任务智能体在管（它写了状态文件）

    def _take(self, situation):
        try:
            self.cts = situation[1] or {}
        except Exception:
            self.cts = getattr(self, "contacts", None) or self.cts

    def initial(self, situation):
        self._take(situation)
        log.info(f"[灵弈小窗] 战前，指挥{self.side_cn}，小窗连 127.0.0.1:{PORT}")
        if OverlayServer.instance is None:
            self.server = OverlayServer(self, PORT)
            self.server.start()
        else:
            self.server = OverlayServer.instance
            self.server.agent = self
        self._build(0.0)
        return None

    def step(self, time_elapse, situation):
        self.now = float(time_elapse)
        self._take(situation)
        try:
            self._sam_sync()
        except Exception as e:
            log.debug(f"防空值班同步异常 {e}")
        try:
            with self.lock:
                self._build(self.now)
        except Exception as e:
            log.error(f"快照异常 {e}", exc_info=True)
        if self.server is not None:
            self.server.publish()
            if self.chase and not self.tick_busy:       # 放工作线程：指令 30~60ms/条，不能卡 step
                self.tick_busy = True
                self.server.pool.submit(self._chase_tick)
        return None

    def deduction_end(self):
        log.info("[灵弈小窗] 推演结束")

    # ------------------------------------------------------------------ 快照
    def _weapons(self, u):
        agg = {}
        for attr in ("Mounts", "Loadouts"):
            holder = getattr(u, attr, None)
            for item in (holder.values() if isinstance(holder, dict) else ()):
                recs = item.get("WeaponRecs") if isinstance(item, dict) else None
                for w in (recs.values() if isinstance(recs, dict) else ()):
                    try:
                        d, n = int(w.get("WeaponDBID")), int(w.get("CurrentLoad", 0) or 0)
                    except (TypeError, ValueError, AttributeError):
                        continue
                    ty = _TYPES.get(d)
                    if n <= 0 or ty in SKIP_TYPES or (ty or 0) >= 3000 and ty != 4001:
                        continue
                    r = agg.get(d)
                    if r is None:
                        rng = [_f(w.get(k, 0) or 0, 1) or 0 for k in
                               ("AirRangeMax", "SurfaceRangeMax", "LandRangeMax", "SubsurfaceRangeMax")]
                        agg[d] = r = [d, 0, *rng, ty or 0]
                    r[1] += n
        return list(agg.values())

    def _unit(self, g, u, kind):
        p = _pos(u)
        row = {"id": g, "n": getattr(u, "Name", g), "k": kind,
               "lat": _f(p[0]) if p else None, "lon": _f(p[1]) if p else None,
               "alt": _f(getattr(u, "CurrentAltitude", 0), 0), "spd": _f(getattr(u, "CurrentSpeed", 0), 0),
               "thr": getattr(u, "Throttle", None), "dmg": _f(getattr(u, "DamagePercent", 0), 0), "w": self._weapons(u)}
        if kind == "a":
            fuel = fmax = 0
            for v in (getattr(u, "FuelRecs", None) or {}).values():
                if isinstance(v, dict):
                    fuel += v.get("CQ") or 0
                    fmax += v.get("MQ") or 0
            self.fuel_peak[g] = max(self.fuel_peak.get(g, 0), fmax, fuel)
            ops = getattr(u, "AirOps", {}) or {}
            row.update({"fuel": _f(fuel, 0), "fmax": _f(self.fuel_peak[g], 0), "air": _airborne(u),
                        "rdy": str(ops.get("ReadyTime") or ""), "host": self._host(g, ops)})
            st = self.chase.get(g)
            if st is not None:
                row["ch"] = st["show"]
        return row

    def _host(self, g, ops):
        """当前所在（CHU）> 归属（AHU，升空后还在）；宿主被打没了就用记下的名字"""
        h = self.get_unit(ops.get("CHU") or ops.get("AHU") or "")
        if h is not None:
            self.host_mem[g] = getattr(h, "Name", "") or self.host_mem.get(g, "")
        return self.host_mem.get(g, "")

    def _build(self, t):
        units = []
        for kind, d in (("a", self.aircrafts), ("s", self.ships), ("u", self.submarines), ("f", self.facilitys)):
            for g, u in list((d or {}).items()):
                if u is not None:
                    try:
                        units.append(self._unit(g, u, kind))
                    except Exception as e:
                        log.debug(f"快照单位异常 {g} {e}")
        contacts = []
        for cid, c in list(self.cts.items()):
            p = _pos(c)
            if p is None:
                continue
            ty = _get(c, "Type")
            contacts.append({"id": cid, "n": _get(c, "Name", "") or "", "ty": ty, "lat": _f(p[0]), "lon": _f(p[1]),
                             "ms": ty == ContactType.Missile.value})
        self.snapshot = {"t": round(t), "side": self.side_cn, "started": t >= 1, "units": units, "contacts": contacts,
                         "sam": self._sam_rows(units), "notes": self.notes[-6:]}

    # ------------------------------------------------------------------ 防空值班（地空导弹 / 雷达）
    def _sam_ext(self):
        """读任务智能体（SamBattalionDefense）写的状态：它在跑就以它的模式为准。"""
        data = _sam_read("sam_state.json")
        units = data.get("units") if isinstance(data.get("units"), dict) else {}
        try:
            fresh = (time.time() - float(data.get("updated") or 0)) < SAM_STATE_FRESH_SEC
        except (TypeError, ValueError):
            fresh = False
        return (units if fresh else {}), fresh

    def _sam_rows(self, units):
        """快照里的 sam 段：[{id,n,role,dir,mode}]，一个单元一行。"""
        ext, _fresh = self._sam_ext()
        rows, seen = [], set()
        for u in units:
            g, name = u["id"], u["n"]
            info = ext.get(g) or {}
            role = info.get("role") or _sam_role(name)
            if role is None:
                continue
            rows.append({"id": g, "n": info.get("name") or name, "role": role,
                         "dir": info.get("dir") or ("S" if role == "radar" else "N"),
                         "mode": self.sam_modes.get(g) or info.get("mode") or _sam_default_mode(role)})
            seen.add(g)
        for g, info in ext.items():
            if g in seen or not isinstance(info, dict):
                continue
            role = info.get("role") or "sam"
            rows.append({"id": g, "n": info.get("name") or g,
                         "role": role,
                         "dir": info.get("dir") or ("S" if role == "radar" else "N"),
                         "mode": self.sam_modes.get(g) or info.get("mode") or _sam_default_mode(role)})
        return rows

    def _sam_sync(self):
        """① 任务智能体在跑：采用它发布的模式（含它自动切回的机动）；
           ② 它不在：自己判有没有弹打过来，命中就切机动并直接下指令。"""
        ext, fresh = self._sam_ext()
        if fresh:
            self.sam_state_at = time.time()
            for g, info in ext.items():
                if not isinstance(info, dict):
                    continue
                self.sam_units[g] = {"name": info.get("name") or g,
                                     "role": info.get("role") or "sam",
                                     "dir": info.get("dir") or "N"}
                if info.get("mode"):
                    self.sam_modes[g] = info["mode"]
                self.sam_owned.add(g)
            return

        for g in list(self.sam_modes):
            mode = self.sam_modes.get(g)
            if mode not in ("strike", "bait"):
                continue
            u = self.get_unit(g)
            if u is None or not self._sam_threatened(u):
                continue
            name = getattr(u, "Name", g)
            role = (self.sam_units.get(g) or {}).get("role") or _sam_role(name) or "sam"
            brg = _sam_default_dir(name, role)
            self.sam_modes[g] = "maneuver"
            self._sam_apply(g, u, "maneuver", brg)
            self._note("%s 有弹打过来，自动切回机动模式" % name)
            self._sam_push_intent({g: "maneuver"})

    def _sam_threatened(self, u):
        """有没有弹朝这个单元飞来（几何判据，任务智能体不在时用）。"""
        p = _pos(u)
        if p is None:
            return False
        for c in list(self.cts.values()):
            if _get(c, "Type") != ContactType.Missile.value:
                continue
            cp = _pos(c)
            if cp is None:
                continue
            d = _km(p, cp)
            if d > 80:
                continue
            hdg = _f(_get(c, "CurrentHeading"), 1)
            if hdg is None:
                return True
            dn = (p[0] - cp[0]) * 111.32
            de = (p[1] - cp[1]) * 111.32 * math.cos(math.radians((p[0] + cp[0]) / 2))
            brg = (math.degrees(math.atan2(de, dn)) + 360.0) % 360.0
            if abs((hdg - brg + 180.0) % 360.0 - 180.0) <= 60.0:
                return True
        return False

    def _sam_apply(self, g, u, mode, brg):
        """把某个模式直接下给单元（停车/开雷达 或 关雷达/全速机动）。"""
        try:
            if mode == "maneuver":
                self._send(u.switch_radar, False)
                self._send(u.hold_positon, False)
                p = _pos(u)
                if p is not None:
                    self._send(u.plotted_course, [_sam_dest(p[0], p[1], brg, SAM_MOVE_KM)])
                self._send(u.set_throttle, THROTTLES["Flank"])
                return True, "机动：关雷达 + 全速%s" % _DIR_CN.get(int(brg), "机动")
            self._send(u.clear_plotted_course)
            self._send(u.set_desired_speed, 0)
            self._send(u.set_throttle, THROTTLES["FullStop"])
            self._send(u.hold_positon, True)
            self._send(u.EMCON_Obey_doctrine, False)
            self._send(u.switch_radar, True)
            if mode == "strike":
                self._send(u.doctrine_weapon_control_status_air, WeaponControlStatus.Free)
                return True, "打击：停车 + 开雷达 + 自由开火"
            return True, "骗弹：停车 + 开雷达"
        except Exception as e:
            return False, "异常 %s" % e

    def _sam_push_intent(self, modes):
        """把刚点的模式写进 sam_intent.json，任务智能体下个周期照此执行。"""
        if not modes:
            return
        if not self.sam_seq:        # 上一局留下的 seq 不能比新指令还大
            try:
                self.sam_seq = int(_sam_read("sam_intent.json").get("seq") or 0)
            except (TypeError, ValueError):
                self.sam_seq = 0
        self.sam_seq += 1
        _sam_write("sam_intent.json", {
            "seq": self.sam_seq,
            "updated": round(time.time(), 3),
            "cmd": dict((g, {"mode": m, "ts": self.now}) for g, m in modes.items()),
        })

    def op_sam_mode(self, cmd, units):
        """小窗按钮：mode = strike/maneuver（地空导弹）或 bait/maneuver（雷达）。

        🔴 按 ids 逐个处理，**不要求本地能 get_unit**：客户端里每个智能体只拿了
           一部分单元的句柄时，本地照样要能把指令写进 sam_intent.json，
           由任务智能体（它有全部单元）去执行；本地有句柄就顺手直接下给平台。
        """
        mode = str(cmd.get("mode") or "")
        out, touched = {}, {}
        by_guid = dict(units)
        for g in cmd.get("ids") or []:
            u = by_guid.get(g)
            info = self.sam_units.get(g) or {}
            name = getattr(u, "Name", "") if u is not None else (info.get("name") or "")
            role = info.get("role") or _sam_role(name)
            if role is None:
                out[g] = (False, "不是地空导弹/雷达单元")
                continue
            allowed = ("strike", "maneuver") if role == "sam" else ("bait", "maneuver")
            if mode not in allowed:
                out[g] = (False, "模式不合法：%s" % mode)
                continue
            brg = (_DIR_BRG.get(info.get("dir") or "")
                   if info.get("dir") else None)
            if brg is None:
                brg = _sam_default_dir(name or g, role)
            if u is not None:
                out[g] = self._sam_apply(g, u, mode, brg)
            else:
                out[g] = (True, "已转给任务智能体执行（本地没有该单元句柄）")
            if out[g][0]:
                self.sam_modes[g] = mode
                self.sam_units[g] = {"name": name or g, "role": role,
                                     "dir": _DIR_LETTER(brg)}
                touched[g] = mode
        self._sam_push_intent(touched)
        return out

    # ------------------------------------------------------------------ 指令
    def _send(self, fn, *args):
        why = ""
        for i in range(NET_RETRY):
            try:
                ok, why = _reply(fn(*args))
            except Exception as e:
                return False, f"异常 {e}"
            if ok is not None:
                return ok, why
            time.sleep(0.05 * (i + 1))
        return False, why

    def execute(self, cmd):
        op = cmd.get("op")
        fn = getattr(self, f"op_{op}", None)
        if fn is None:
            return {"ok": False, "msg": f"未知指令 {op}"}
        units = [(g, self.get_unit(g)) for g in cmd.get("ids") or []]
        missing = [g for g, u in units if u is None]
        units = [(g, u) for g, u in units if u is not None]
        try:
            with self.lock:
                per = fn(cmd, units)
        except Exception as e:
            log.exception(f"指令 {op} 异常")
            return {"ok": False, "msg": f"异常 {e}"}
        bad = {g: m for g, (ok, m) in per.items() if not ok}
        unhandled = [g for g in missing if g not in per]
        msg = f"{op} {len(per) - len(bad)}/{len(per)} 成功"
        if bad:
            msg += "；失败：" + "；".join(f"{getattr(self.get_unit(g), 'Name', g)} {m}" for g, m in bad.items())
        if unhandled:
            msg += f"；{len(unhandled)} 个单元本地没有句柄、也没有别的智能体接手"
        log.info(f"[小窗指令] {msg}")
        ok = not bad and bool(per) and not unhandled
        return {"ok": ok, "msg": msg if (per or unhandled) else "这些单元已经没了"}

    def op_attack(self, cmd, units):
        """target: 情报 ID；weapons: [[dbid, 每单元发数], ...]。发数超过这架余弹按余弹算；飞机够不着 / 还停着的走追打"""
        tgt = cmd["target"]
        out = {}
        for g, u in units:
            rs, jobs = [], []
            for d, n in cmd.get("weapons") or []:
                d, n = int(d), int(n)
                if n <= 0:
                    continue
                r = self._reach(u, d, tgt)
                n = min(n, r[2]) if r else n
                if g in (self.aircrafts or {}) and r and r[0] > 0 and (r[1] > r[0] or not _airborne(u)):
                    jobs.append((d, n))
                    rs.append((True, "飞过去打", d, n))
                else:
                    rs.append((*self._send(u.attack_weapon_allocate_to_target, tgt, d, n), d, n))
            if jobs:
                self._chase_add(g, u, tgt, jobs)
            out[g] = (bool(rs) and all(r[0] for r in rs),
                      "；".join(f"{d}×{n} {'ok' if ok else m}" for ok, m, d, n in rs) or "没选武器")
        return out

    def op_unchase(self, cmd, units):
        out = {}
        for g, u in units:
            st = self.chase.get(g)
            if st is None:
                out[g] = (True, "没在追打")
                continue
            self._send(u.clear_plotted_course)
            self._chase_end(g, u, st)
            out[g] = (True, "已停止")
        return out

    # ------------------------------------------------------------------ 追打（超射程打击：下了就退任务飞过去打）
    def _note(self, text, ok=True):
        self.note_n += 1
        self.notes = (self.notes + [[self.note_n, text, ok]])[-30:]
        log.info(f"[追打] {text}")

    def _reach(self, u, dbid, tgt):
        """(射程 km, 距离 km, 余弹)；目标 / 自己没位置、这架没这种弹返回 None"""
        c = self.cts.get(tgt)
        p, me = (_pos(c) if c is not None else None), _pos(u)
        row = next((r for r in self._weapons(u) if r[0] == dbid), None)
        if p is None or me is None or row is None:
            return None
        return row[DOM_I[_dom(c)]] * 1.852, _km(me, p), row[1]

    def _mission_name(self, guid):
        for name, m in (getattr(self, "missions_obj", None) or {}).items():
            if guid in (name, getattr(m, "ID", None)):
                return name
        return ""

    def _chase_add(self, g, u, tgt, jobs):
        st = self.chase.get(g)
        if st is None:
            mis = getattr(u, "AssignedMission", "") or ""
            st = self.chase[g] = {"jobs": {}, "shots": [], "mis": self._mission_name(mis) if mis else "", "t0": self.now,
                                  "plot_t": -1e9, "aim_tgt": None, "aim_p": None, "launch_t": -1e9, "launch_bad": 0,
                                  "rtb_t": -1e9, "show": _get(self.cts.get(tgt), "Name", "") or tgt}
            if mis:
                self._send(u.withdraw_from_mission)         # 任务逻辑会把飞机拉回去，不退就飞不过去
            if _rtb(u):
                st["rtb_t"] = self.now
                self._send(u.return_to_base, False)
        for d, n in jobs:
            st["jobs"][(tgt, d)] = {"tgt": tgt, "d": d, "n": n, "t": -1e9, "tries": 0}
        self._chase_one(g, u, st)

    def _chase_end(self, g, u, st):
        self.chase.pop(g, None)
        if st["mis"]:
            ok, m = self._send(u.assign_to_mission, st["mis"])
            if not ok:
                self._note(f"{getattr(u, 'Name', g)} 回任务 {st['mis']} 失败：{m}", False)

    def _chase_tick(self):
        try:
            for g, st in list(self.chase.items()):
                u = self.get_unit(g)
                if u is None:
                    self.chase.pop(g, None)
                    continue
                try:
                    self._chase_one(g, u, st)
                except Exception as e:
                    log.exception(f"追打异常 {g}")
                    self._note(f"{getattr(u, 'Name', g)} 追打异常 {e}，已停止", False)
                    self.chase.pop(g, None)
        finally:
            self.tick_busy = False

    def _chase_one(self, g, u, st):
        name = getattr(u, "Name", g)
        air = _airborne(u)
        for key, j in list(st["jobs"].items()):
            r = self._reach(u, j["d"], j["tgt"])
            if r is None:
                st["jobs"].pop(key)
                self._note(f"{name} 目标没了或弹没了，这条追打取消", False)
            elif air and r[1] <= r[0] * CHASE_FIRE and self.now - j["t"] >= CHASE_RETRY_SEC:
                self._chase_fire(st, u, key, j, r)
        if not st["jobs"]:
            self._chase_wait(g, u, st)
        elif not air:
            self._chase_launch(g, u, st)
        elif _rtb(u) and self.now - st["rtb_t"] > CHASE_RTB_GRACE:     # 引擎因为油料 / 弹药让它回去的
            self._note(f"{name} 引擎让它返航（多半缺油），追打取消", False)
            self.chase.pop(g, None)
        else:
            self._chase_plot(u, st)

    def _chase_fire(self, st, u, key, j, r):
        j["t"], j["tries"] = self.now, j["tries"] + 1
        c = self.cts.get(j["tgt"])
        if _dom(c) == "air":        # 雷达关着时雷达弹下令回 OK 但不发射，停放时开的雷达起飞还会被引擎关掉
            self._send(u.EMCON_Obey_doctrine, False)
            self._send(u.switch_radar, True)
        n = min(j["n"], r[2])
        ok, m = self._send(u.attack_weapon_allocate_to_target, j["tgt"], j["d"], n)
        if ok:
            st["jobs"].pop(key)
            st["shots"].append([j["d"], r[2] - n, self.now])
            self._note(f"{getattr(u, 'Name', '')} 进射程，打 {_get(c, 'Name', '') or j['tgt']}：武器 {j['d']}×{n}")
        elif j["tries"] >= CHASE_TRIES:
            st["jobs"].pop(key)
            self._note(f"{getattr(u, 'Name', '')} 分配武器被拒 {CHASE_TRIES} 次，放弃：{m}", False)

    def _chase_wait(self, g, u, st):
        """都下完了：等实射（看余弹），再回原任务"""
        left = {r[0]: r[1] for r in self._weapons(u)}
        for s in list(st["shots"]):
            if left.get(s[0], 0) <= s[1]:
                st["shots"].remove(s)
            elif self.now - s[2] > CHASE_SHOT_SEC:
                st["shots"].remove(s)
                self._note(f"{getattr(u, 'Name', g)} 武器 {s[0]} 下令 {CHASE_SHOT_SEC} 秒还没实射", False)
        if not st["shots"]:
            self._chase_end(g, u, st)

    def _chase_launch(self, g, u, st):
        if self.now - st["t0"] > CHASE_LAUNCH_MAX_SEC or st["launch_bad"] >= CHASE_LAUNCH_FAILS:
            self._note(f"{getattr(u, 'Name', g)} 起飞不了，追打取消", False)
            self._chase_end(g, u, st)
        elif self.now - st["launch_t"] >= CHASE_LAUNCH_SEC:
            st["launch_t"] = self.now
            if not self._send(self.air_single_out, [g])[0]:
                st["launch_bad"] += 1

    def _chase_plot(self, u, st):
        j = next(iter(st["jobs"].values()))
        c = self.cts.get(j["tgt"])
        r, p, me = self._reach(u, j["d"], j["tgt"]), _pos(c) if c is not None else None, _pos(u)
        if r is None or p is None or r[1] <= 0:
            return
        st["show"] = _get(c, "Name", "") or j["tgt"]
        since = self.now - st["plot_t"]
        if st["aim_tgt"] == j["tgt"] and st["aim_p"] and (since < CHASE_PLOT_SEC or (
                _km(st["aim_p"], p) < CHASE_PLOT_KM and since < CHASE_PLOT_MAX_SEC)):
            return
        k = min(1.0, r[0] * CHASE_AIM / r[1])
        aim = (p[0] + (me[0] - p[0]) * k, p[1] + (me[1] - p[1]) * k)
        st["plot_t"], st["aim_tgt"], st["aim_p"] = self.now, j["tgt"], p
        ok, m = self._send(u.plotted_course, [aim])
        if not ok:
            self._note(f"{getattr(u, 'Name', '')} 航线被拒：{m}", False)

    def op_throttle(self, cmd, units):
        thr = THROTTLES[cmd["throttle"]]
        return {g: self._send(u.set_throttle, thr) for g, u in units}

    def op_alt(self, cmd, units):
        alt = float(cmd["alt"])
        out = {}
        for g, u in units:
            if g in (self.aircrafts or {}):
                self._send(u.set_alt_manual, True)
                out[g] = self._send(u.set_desired_height, alt)
            elif g in (self.submarines or {}):
                out[g] = self._send(u.set_desired_height, -abs(alt))
        return out


class OverlayServer:
    """aiohttp 跑在独立线程：WS /ws 推快照 {"type":"snap"}、收指令 {"type":"cmd","req","cid",...} 回 {"type":"ack"}；
    指令在一个工作线程里按顺序执行，cid 去重（小窗断线重发同一条不会打两次）"""
    instance = None

    def __init__(self, agent, port):
        self.agent, self.port = agent, port
        self.loop = None
        self.clients = {}
        self.done = OrderedDict()
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="overlay-cmd")
        self.last_pub = 0.0
        OverlayServer.instance = self

    def start(self):
        threading.Thread(target=self._run, name="overlay-ws", daemon=True).start()
        threading.Thread(target=self._beat, name="overlay-beat", daemon=True).start()

    def _beat(self):
        """暂停 / 战前 step 不来：3 秒自己重建一次快照推出去，小窗不会当成没对局"""
        while True:
            time.sleep(1)
            a = self.agent
            if a is None or not self.clients or time.monotonic() - self.last_pub < 3:
                continue
            if a.lock.acquire(timeout=0.5):
                try:
                    a._build(a.now)
                except Exception:
                    pass
                finally:
                    a.lock.release()
            self.publish()

    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        app = web.Application()
        app.router.add_get("/ws", self._ws)
        async def h_index(req):
            return web.Response(text="灵弈小窗智能体在跑；小窗请双击 agent/overlay/灵弈小窗.bat")
        app.router.add_get("/", h_index)
        runner = web.AppRunner(app)
        self.loop.run_until_complete(runner.setup())
        try:
            self.loop.run_until_complete(web.TCPSite(runner, "127.0.0.1", self.port).start())
        except OSError as e:
            log.error(f"[灵弈小窗] 端口 {self.port} 打不开：{e}")
            return
        self.loop.run_forever()

    def publish(self):
        if self.loop is None or not self.clients:
            return
        self.last_pub = time.monotonic()
        text = json.dumps({"type": "snap", **self.agent.snapshot}, ensure_ascii=False, separators=(",", ":"))

        def put():
            for st in self.clients.values():
                st["text"] = text
                st["ev"].set()
        self.loop.call_soon_threadsafe(put)

    async def _sender(self, ws, st):
        while not ws.closed:
            try:
                await asyncio.wait_for(st["ev"].wait(), 3)
            except asyncio.TimeoutError:
                pass
            st["ev"].clear()
            text, st["text"] = st["text"], None
            try:
                await asyncio.wait_for(ws.send_str(text or '{"type":"hb"}'), 15)
            except Exception:
                await ws.close()
                return

    async def _ws(self, req):
        ws = web.WebSocketResponse(heartbeat=10, max_msg_size=8 * 1024 * 1024)
        await ws.prepare(req)
        st = {"text": json.dumps({"type": "snap", **self.agent.snapshot}, ensure_ascii=False), "ev": asyncio.Event()}
        st["ev"].set()
        self.clients[ws] = st
        task = asyncio.ensure_future(self._sender(ws, st))
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                    except Exception:
                        continue
                    if data.get("type") == "cmd":
                        asyncio.ensure_future(self._cmd(ws, data))
        finally:
            self.clients.pop(ws, None)
            task.cancel()
        return ws

    async def _cmd(self, ws, data):
        req, cid = data.get("req"), data.get("cid")
        if cid and cid in self.done:
            res = self.done[cid]
            if isinstance(res, asyncio.Future):
                res = await asyncio.shield(res)
        else:
            fut = asyncio.ensure_future(self.loop.run_in_executor(self.pool, self.agent.execute, data))
            if cid:
                self.done[cid] = fut
                while len(self.done) > 500:
                    self.done.popitem(last=False)
            res = await fut
            if cid:
                self.done[cid] = res
        try:
            await ws.send_str(json.dumps({"type": "ack", "req": req, **res}, ensure_ascii=False))
        except Exception:
            pass


def configure(args=None, side=None):
    """本地测试用（python -m agent.overlay.local_test）"""
    side = side or os.environ.get("LY_OVERLAY_SIDE", "蓝方")
    return {side: {"Overlay": {"class": OverlayAgent, "unit": [], "contact": [], "point": []}}}
