# -*- coding: utf-8 -*-
"""ScenarioSpec -> Lua 脚本生成器（无头建想定的核心）。

同一份规格编译出**两种等价产物**：

* ``LuaProgram.script``  —— 自包含脚本：用 ``local`` + ``string.match`` 自己抓
  GUID，可直接粘进引擎控制台，或一次 ``executeLua`` 跑完，也适合归档给人看。
* ``LuaProgram.blocks``  —— 分块脚本（元信息/推演方/条令/单元/任务/巡逻区/分配/保存），
  块内对 GUID 的引用写成 ``%{S:红方}`` ``%{U:舰名}`` ``%{M:任务名}`` 占位符，
  由 builder 在**上一块执行后**用真实返回值回填。分块的好处：错误定位到块、
  GUID 有据可查、失败可断点续跑。

生成规则全部来自实测（见 docs/无头Lua建想定方法手册.md）：
    1. NewScenario 必须先于一切场景读写；
    2. SetScenarioInfo 的 DESCRIPTION 是 Base64；
    3. SetSidePosture 必须两两**双向**显式设置；
    4. AddUnit 的 type 首字母大写、dbid 传浮点、经纬度传字符串；
    5. AddMission 的 patrolZone/waypoints 参数会被引擎忽略，巡逻区必须用
       AddReferencePoint（客户端生成 UUID，字段 lat/lon 小写）+ SetMission 绑定；
    6. AssignUnitListToMission 第一参是逗号分隔的**单元 GUID**，第二参是
       **任务 GUID**，第三参必须给（false）；
    7. Command_SaveScen 传完整 Windows 路径。
"""
from __future__ import annotations

import base64
import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .spec import ScenarioSpec, PATROL_SUBTYPES, STRIKE_SUBTYPES, SpecError


# ---------------------------------------------------------------- 字面量工具
def q(s: str) -> str:
    """Lua 单引号字符串字面量（转义 \\ 与 '，去掉换行）。"""
    if s is None:
        return "''"
    s = str(s).replace("\\", "\\\\").replace("'", "\\'").replace("\r", " ").replace("\n", " ")
    return "'%s'" % s


def num(x) -> str:
    """数值字面量：整数无小数点，浮点保留 6 位去尾零。"""
    if x is None:
        return "0"
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    f = float(x)
    if f == int(f) and abs(f) < 1e15:
        return "%.1f" % f
    return ("%.6f" % f).rstrip("0").rstrip(".")


def b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def html_description(spec: ScenarioSpec) -> str:
    """把纯文本描述包成引擎认的 HTML 简报。"""
    d = spec.description or ("%s：由想定编辑智能体从自然语言描述生成。" % spec.title)
    if d.lstrip().startswith("<"):
        return d
    body = "".join(
        '<P style="MARGIN: 12px 0px"><SPAN style="FONT-SIZE: 14pt; FONT-FAMILY: \'宋体\'">%s</SPAN></P>'
        % line.replace("&", "&amp;").replace("<", "&lt;")
        for line in d.split("\n") if line.strip()
    )
    return ('<BODY scroll=auto><P style="MARGIN: 12px 0px" align=center>'
            '<SPAN style="FONT-SIZE: 18pt; FONT-FAMILY: \'黑体\'">%s</SPAN></P>%s</BODY>'
            % (spec.title, body))


def camera_for(spec: ScenarioSpec, side) -> Dict[str, float]:
    """未显式给视点时，按想定范围自动算一个能看全战场的相机。"""
    if side.camera:
        return side.camera
    lats = [u.lat for u in spec.units] or [spec.center.get("lat", 0.0)]
    lons = [u.lon for u in spec.units] or [spec.center.get("lon", 0.0)]
    clat = (max(lats) + min(lats)) / 2.0
    clon = (max(lons) + min(lons)) / 2.0
    span = max(max(lats) - min(lats), max(lons) - min(lons), 0.1)
    return {"lat": round(clat, 4), "lon": round(clon, 4), "alt": round(span * 111000 * 2.5, 0)}


def zone_guids(spec: ScenarioSpec, mission_name: str, n_points: int) -> List[str]:
    """巡逻区参考点的**确定性** GUID（同一 spec 重复生成结果一致）。"""
    return [spec.new_guid("zone|%s|%d" % (mission_name, i)) for i in range(n_points)]


# ---------------------------------------------------------------- 两种渲染模式
class _Renderer(object):
    """mode='script'  → 自包含脚本（local 变量）
       mode='blocks'  → 分块脚本（%{S:..} 占位符，由 builder 回填）"""

    def __init__(self, spec: ScenarioSpec, mode: str):
        self.spec = spec
        self.mode = mode
        self.side_var = {s.name: "S_%d" % (i + 1) for i, s in enumerate(spec.sides)}
        self.unit_var = {u.name: "U_%d" % (i + 1) for i, u in enumerate(spec.units)}
        self.miss_var = {m.name: "M_%d" % (i + 1) for i, m in enumerate(spec.missions)}

    def side(self, name: str) -> str:
        return self.side_var[name] if self.mode == "script" else "%%{S:%s}" % name

    def unit(self, name: str) -> str:
        return self.unit_var[name] if self.mode == "script" else "%%{U:%s}" % name

    def mission(self, name: str) -> str:
        return self.miss_var[name] if self.mode == "script" else "%%{M:%s}" % name

    def assign_arg(self, units: List[str]) -> str:
        """AssignUnitListToMission 的第一参（逗号分隔的单元 GUID 字符串）。"""
        if self.mode == "script":
            return "..','..".join(self.unit_var[n] for n in units)
        return q(",".join("%%{U:%s}" % n for n in units))

    def decl(self) -> str:
        return "local " if self.mode == "script" else ""


@dataclass
class LuaBlock:
    key: str
    title: str
    code: str


@dataclass
class LuaProgram:
    spec: ScenarioSpec
    scen_path: str
    blocks: List[LuaBlock] = field(default_factory=list)
    script: str = ""
    notes: List[str] = field(default_factory=list)

    def to_text(self) -> str:
        head = [
            "-- ============================================================",
            "-- 想定：%s" % self.spec.title,
            "-- 生成：sce_agent（想定编辑智能体）  %s"
            % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "-- 保存路径：%s" % self.scen_path,
            "-- 规模：%s" % "；".join(self.notes),
            "-- ============================================================",
        ]
        return "\n".join(head + [self.script, ""])

    def block_map(self) -> Dict[str, str]:
        return {b.key: b.code for b in self.blocks}


# ---------------------------------------------------------------- 生成主体
def generate(spec: ScenarioSpec, scen_path: str) -> LuaProgram:
    """把 spec 编译成 Lua 程序（blocks + 自包含脚本）。"""
    errs = [e for e in spec.validate() if not e.startswith("警告")]
    if errs:
        raise SpecError("规格校验未通过，拒绝生成 Lua：\n  - " + "\n  - ".join(errs))

    prog = LuaProgram(spec=spec, scen_path=scen_path)
    R = _Renderer(spec, "blocks")     # 分块版
    Rs = _Renderer(spec, "script")    # 自包含版

    script: List[str] = []

    def add_block(key, title, blk_lines, sec_no, comment):
        prog.blocks.append(LuaBlock(key, title, "\n".join(blk_lines)))
        script.extend(["", "-- [%d] %s" % (sec_no, comment)] + [ln for ln in blk_lines])

    # ---------- 1 元信息 ----------
    desc = b64(html_description(spec))
    # ⚠ 实测红线：STARTTIME 一旦写进 SetScenarioInfo，引擎的 ZeroHour/Time 三者就对不上，
    # 框架侧会认为"已经推演了 260 天"，reset 后第一步即判结束（sim_time≈2.26e7 s）。
    # 而不写 STARTTIME 的想定能正常跑满 30 步（sim_time 与决策步数严格一致）。
    # 所以默认**不下发** STARTTIME，作战时间只写进简报与 spec；需要时用
    # spec.provenance['engine_start_time']=True 显式打开（并自行承担风险）。
    with_time = bool(spec.provenance.get("engine_start_time"))
    info = ("SetScenarioInfo({TITLE=%(t)s%(st)s, DURATION=%(d)d, COMPLEXITY=%(c)d, "
            "DIFFICULTY=%(f)d, SEED=%(s)d, DESCRIPTION=%(desc)s})"
            % dict(t=q(spec.title),
                   st=(", STARTTIME=%s" % q(spec.start_time)) if with_time else "",
                   d=int(spec.duration_s),
                   c=int(spec.complexity), f=int(spec.difficulty), s=int(spec.seed), desc=q(desc)))
    add_block("info", "新建想定 + 元信息",
              ["NewScenario('','')", info], 1, "新建空白想定 + 元信息（DESCRIPTION 是 Base64）")

    # ---------- 2 推演方 ----------
    add_block("sides", "添加推演方（%d 个）" % len(spec.sides),
              ["%s%s = AddSide({side=%s})" % (R.decl(), R.side_var[s.name], q(s.name))
               for s in spec.sides], 2, "添加推演方（AddSide 返回推演方 GUID）")

    # ---------- 3 姿态 / 视点 / 条令 ----------
    lines = ["-- 姿态两两双向显式设置（H=敌对 F=友好 N=中立 U=不友好）"]
    for s in spec.sides:
        for opp, code in s.posture.items():
            lines.append("SetSidePosture(%s, %s, %s)" % (R.side(s.name), R.side(opp), q(code)))
    lines.append("-- 相机视点（每个推演方都必须设，否则推演界面看不到画面）")
    for s in spec.sides:
        cam = camera_for(spec, s)
        lines.append("SetSideOptions({side=%s, CAMERALON=%s, CAMERALAT=%s, CAMERAALT=%s})"
                     % (R.side(s.name), num(cam["lon"]), num(cam["lat"]), num(cam["alt"])))
    lines.append("-- 条令（参数 1 是推演方表，参数 2 才是条令表，不能合并）")
    for s in spec.sides:
        kv = ", ".join("%s=%s" % (k, q(v)) for k, v in s.doctrine.items())
        lines.append("SetDoctrine({side=%s}, {%s})" % (R.side(s.name), kv))
    add_block("setup", "对抗关系 / 视点 / 条令", lines, 3, "对抗关系 / 视点 / 条令")

    # ---------- 4 气象 ----------
    if spec.weather:
        w = spec.weather
        add_block("weather", "气象",
                  ["SetWeather(%d, %d, %s, %d)" % (w.temp, w.rainfall, num(w.cloud), w.seastate)],
                  4, "气象：SetWeather(气温, 降雨率0-50, 云量0-1, 海况0-9)")

    # ---------- 5 单元 ----------
    lines = ["-- AddUnit 返回单元 GUID（count>1 时返回逗号分隔的多个）"]
    for u in spec.units:
        parts = ["side=%s" % R.side(u.side), "type=%s" % q(u.kind), "DATASOURCE=0.0",
                 "name=%s" % q(u.name), "dbid=%s" % num(float(u.dbid))]
        if u.base:
            parts.append("base=%s" % q(u.base))
        parts.append("latitude=%s" % q("%.6f" % u.lat))
        parts.append("longitude=%s" % q("%.6f" % u.lon))
        if u.alt is not None:
            parts.append("alt=%s" % num(u.alt))
        if u.heading is not None:
            parts.append("heading=%s" % num(u.heading))
        if u.kind == "Aircraft":
            # 实测：附加在空中的飞机**必须**带 loadoutid（缺键直接报"缺少挂载！"，
            # 传 0.0 表示无武装挂载；有真实方案时按 DB 的 loadout DBID 填）
            parts.append("loadoutid=%s" % num(float(u.loadoutid or 0)))
        elif u.loadoutid:
            parts.append("loadoutid=%s" % num(float(u.loadoutid)))
        if u.count and u.count > 1:
            parts.append("count=%s" % num(float(u.count)))
        lines.append("%s%s = AddUnit({%s})" % (R.decl(), R.unit_var[u.name], ", ".join(parts)))
    add_block("units", "部署单元（%d 型 / %d 个）"
              % (len(spec.units), sum(u.count for u in spec.units)),
              lines, 5, "部署单元")

    # ---------- 6 任务 ----------
    if spec.missions:
        lines = []
        for m in spec.missions:
            table = PATROL_SUBTYPES if m.mtype == "Patrol" else STRIKE_SUBTYPES
            lines.append("-- %s（%s/%s=%s）" % (m.name, m.mtype, m.subtype, table.get(m.subtype, "")))
            lines.append("%s%s = AddMission(%s, %s, %s, {isactive=%s, type=%s, "
                         "unloadMountDBID=0.0, unloadMountCount=0.0})"
                         % (R.decl(), R.miss_var[m.name], R.side(m.side), q(m.name), q(m.mtype),
                            "true" if m.isactive else "false", q(m.subtype)))
            if R.mode == "script":
                lines.append("local %sG = string.match(%s, \"guid = '([^']+)'\")   -- 任务 GUID"
                             % (R.miss_var[m.name], R.miss_var[m.name]))
        add_block("missions", "创建任务（%d 个）" % len(spec.missions), lines, 6, "创建任务")

    # ---------- 7 参考点 + 巡逻区 ----------
    if spec.missions:
        lines = []
        for m in spec.missions:
            gs = zone_guids(spec, m.name, len(m.zone))
            lines.append("-- %s 的巡逻区参考点（GUID 由生成端确定性给出）" % m.name)
            for i, (pt, g) in enumerate(zip(m.zone, gs)):
                lines.append("AddReferencePoint({side=%s, guid=%s, name=%s, lat=%s, lon=%s, highlighted=true})"
                             % (R.side(m.side), q(g), q("%s-WP%d" % (m.name, i + 1)),
                                num(pt["lat"]), num(pt["lon"])))
            if m.mtype == "Patrol":
                lines.append("SetMission(%s, %s, {patrolZone={%s}, unloadMountDBID=0.0, "
                             "unloadMountCount=0.0})"
                             % (R.side(m.side), R.mission(m.name), ", ".join(q(g) for g in gs)))
            else:
                # 实测：SetMission 的 patrolZone 只对 Patrol 生效；Strike 任务没有
                # 巡逻区概念（它的作战范围由目标清单 + 打击半径决定），这里只留参考点
                lines.append("-- （Strike 任务无巡逻区，参考点仅作态势标注）")
        add_block("zones", "参考点 + 绑定巡逻区", lines, 7,
                  "参考点 + 绑定巡逻区（AddMission 的 patrolZone 参数会被引擎忽略）")

    # ---------- 8 分配 ----------
    if spec.missions:
        lines = ["-- 第一参=逗号分隔单元 GUID，第二参=任务 GUID，第三参必须给"]
        for m in spec.missions:
            lines.append("AssignUnitListToMission(%s, %s, false)"
                         % (R.assign_arg(m.units), R.mission(m.name)))
        add_block("assign", "分配单元到任务", lines, 8, "单元-任务分配")

    # ---------- 9 保存 ----------
    add_block("save", "保存 .scen",
              ["Command_SaveScen(%s)" % q(scen_path)], 9,
              "保存（必须给完整路径；返回值形如 Scenarios/xxx.scen）")

    prog.script = "\n".join(script[1:] if script and script[0] == "" else script)
    prog.notes.append("单元 %d 型 / %d 个" % (len(spec.units), sum(u.count for u in spec.units)))
    prog.notes.append("任务 %d 个" % len(spec.missions))
    prog.notes.append("参考点 %d 个" % sum(len(m.zone) for m in spec.missions))
    return prog
