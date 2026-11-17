# -*- coding: utf-8 -*-
"""想定构建流水线：规格 -> Lua -> 引擎 -> .scen -> 回读 -> 验收 -> 归档。

    spec  ──lua_gen──►  LuaProgram ──顺序执行──►  引擎（无头）
                                                  │
                        .scen 文件 ◄──Command_SaveScen
                            │
                            └──GetScenarioContent──► digest ──verify──► 验收报告

三个工程要点：
1. **分块执行 + 占位符回填**：GUID 只有引擎知道，所以每块执行完把真实返回值写进
   上下文，再渲染下一块。哪一块失败就停在哪一块，日志里能直接看到失败的 Lua 原文。
2. **DBID 先复核后下发**：下单前用 ``queryDatabase`` 确认 dbid 在**当前 DB 版本**
   里确实是你想要的那个平台（DBID 会随版本漂移，硬编码必然出事故）。
3. **验收即产物**：每次构建都留下 spec.json / scenario.lua / build.json / verify.md，
   任何一份都能被别人复现。
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .catalog import Catalog
from .digest import parse_scenario_xml, digest_summary
from .lua_gen import LuaProgram, generate
from .lyclient import LuaClient, LuaError
from .spec import ScenarioSpec
from .verify import Report, verify

ILLEGAL = re.compile(r'[\\/:*?"<>|\s]+')


def slugify(title: str, maxlen: int = 60) -> str:
    s = ILLEGAL.sub("-", title.strip())
    return (s[:maxlen] or "scenario").strip("-")


@dataclass
class BuildResult:
    ok: bool = False
    title: str = ""
    name: str = ""
    scen_path: str = ""          # 靶机上的完整路径
    size: int = 0
    lua: str = ""
    digest: Optional[Dict[str, Any]] = None
    report: Optional[Report] = None
    steps: List[Dict[str, Any]] = field(default_factory=list)
    elapsed: float = 0.0
    error: str = ""
    out_dir: str = ""

    def to_dict(self):
        return {"ok": self.ok, "title": self.title, "name": self.name,
                "scen_path": self.scen_path, "size": self.size,
                "elapsed": round(self.elapsed, 2), "error": self.error,
                "steps": self.steps,
                "digest_summary": digest_summary(self.digest) if self.digest else "",
                "verify": self.report.to_dict() if self.report else None}


class Builder(object):
    def __init__(self, client: LuaClient, scen_dir: str = "D:/LingYi/Data/Scenarios",
                 out_dir: str = "out", target=None, catalog: Optional[Catalog] = None,
                 trace: bool = False):
        self.c = client
        self.scen_dir = scen_dir.rstrip("/")
        self.out_dir = out_dir
        self.target = target
        self.cat = catalog or Catalog()
        self.trace = trace

    # ------------------------------------------------------------ DBID 复核
    def check_dbids(self, spec: ScenarioSpec) -> List[str]:
        """下单前自检：① dbid 在当前引擎 DB 里确实存在；② 设施必须落在陆地。

        DBID 会随 DB 版本漂移（同一个 173 在不同版本里可能是驱逐舰也可能是巡逻艇），
        所以必须问引擎，而不是信文档。设施落水会被引擎直接拒绝
        （"此点在水下!"），这里顺手把它"吸附"到最近的陆地并留痕。
        """
        notes = []
        for u in spec.units:
            ok, klass = self.c.query_db(u.kind, u.dbid)
            if not ok:
                raise LuaError("DBID 不存在：%s %s #%d -> %s" % (u.side, u.kind, u.dbid, klass))
            if u.alias and klass and u.alias.lower() not in klass.lower():
                notes.append("提示：单元 %s 的别名 %r 与引擎类名 %r 不完全一致"
                             % (u.name, u.alias, klass))
            if u.kind == "Facility":
                if self._snap_to_land(u):
                    notes.append("设施 %s 的原坐标在水面，已吸附到最近的陆地 (%.4f, %.4f)"
                                 % (u.name, u.lat, u.lon))
            elif u.kind in ("Ship", "Submarine"):
                # 引擎会拒绝"把船放在陆地上"；把落陆的舰艇挪到最近的海面
                elev, _ = self.c.get_elevation(u.lat, u.lon)
                if elev is not None and elev > 0:
                    if self._snap_to_water(u):
                        notes.append("舰艇 %s 的原坐标在陆地，已吸附到最近的海面 (%.4f, %.4f)"
                                     % (u.name, u.lat, u.lon))
                    else:
                        raise LuaError("舰艇 %s 的坐标 (%.4f, %.4f) 在陆地，附近找不到海面"
                                       % (u.name, u.lat, u.lon))
        return notes

    def _snap_to_water(self, u, max_ring: int = 16, step_deg: float = 0.05) -> bool:
        """把落在陆地上的舰艇挪到最近的海面（同心环搜索）。"""
        import math
        for ring in range(1, max_ring + 1):
            r = step_deg * ring
            for k in range(16):
                brg = math.radians(k * 22.5)
                lat = round(u.lat + r * math.cos(brg), 6)
                lon = round(u.lon + r * math.sin(brg) / (math.cos(math.radians(u.lat)) or 1.0), 6)
                ev, _ = self.c.get_elevation(lat, lon)
                if ev is not None and ev <= 0:
                    u.lat, u.lon = lat, lon
                    return True
        return False

    def _snap_to_land(self, u, max_ring: int = 12, step_deg: float = 0.03) -> bool:
        """把落水设施吸附到最近陆地（同心环搜索），返回是否移动过。"""
        elev, _ = self.c.get_elevation(u.lat, u.lon)
        if elev is None or elev > 0:
            return False
        import math
        for ring in range(1, max_ring + 1):
            r = step_deg * ring
            for k in range(16):
                brg = math.radians(k * 22.5)
                lat = round(u.lat + r * math.cos(brg), 6)
                lon = round(u.lon + r * math.sin(brg) / (math.cos(math.radians(u.lat)) or 1.0), 6)
                ev, _ = self.c.get_elevation(lat, lon)
                if ev is not None and ev > 0:
                    u.lat, u.lon = lat, lon
                    return True
        raise LuaError("设施 %s 在 (%.4f, %.4f) 附近 %.2f° 内找不到陆地，请直接给陆地坐标"
                       % (u.name, u.lat, u.lon, max_ring * step_deg))

    # ------------------------------------------------------------ 主流程
    def build(self, spec: ScenarioSpec, name: Optional[str] = None, *,
              verify_after: bool = True, write_artifacts: bool = True,
              wait_file: float = 6.0) -> BuildResult:
        t0 = time.time()
        res = BuildResult(title=spec.title)
        spec.raise_if_invalid()

        notes = self.check_dbids(spec)
        name = name or slugify(spec.title)
        res.name = name
        remote_path = "%s/%s.scen" % (self.scen_dir, name)
        res.scen_path = remote_path

        prog = generate(spec, remote_path)
        res.lua = prog.to_text()

        ctx: Dict[str, str] = {}
        for blk in prog.blocks:
            outs = self._exec_block(blk, ctx, res)
            if outs is None:
                res.elapsed = time.time() - t0
                if write_artifacts:
                    res.out_dir = self.save_artifacts(spec, prog, res)
                return res
            try:
                self._harvest(blk.key, outs, ctx, spec)
            except LuaError as e:
                res.error = "第 %s 块结果解析失败：%s" % (blk.key, e)
                res.elapsed = time.time() - t0
                if write_artifacts:
                    res.out_dir = self.save_artifacts(spec, prog, res)
                return res

        # ---- 等文件落盘
        if self.target:
            deadline = time.time() + wait_file
            while time.time() < deadline:
                res.size = self.target.file_size(remote_path)
                if res.size > 0:
                    break
                time.sleep(0.5)
        # ---- 回读 + 验收
        if verify_after:
            rb_ok, rb_detail, digest = self.readback(name)
            res.digest = digest
            res.report = verify(spec, digest, file_size=res.size if self.target else None,
                                readback_ok=rb_ok, readback_detail=rb_detail)
            if notes:
                for n in notes:
                    res.report.add("自动修正 / 提示", True, n, warn=True)
            res.ok = res.report.ok
        else:
            res.ok = True
        res.elapsed = time.time() - t0
        if write_artifacts:
            res.out_dir = self.save_artifacts(spec, prog, res)
        return res

    # ------------------------------------------------------------ 内部
    def _exec_block(self, blk, ctx: Dict[str, str], res: BuildResult):
        """逐条执行一个块里的可执行语句（块内没有 local 变量，条条自包含）。

        这样做的好处：错误定位到**单条 Lua**，且每条 AddXxx 的返回值都能直接拿到
        （GUID 不需要事后靠 GetUnit/GetMissions 去猜——实测 GetMissions('红方')
        会直接把 RPC 拖到超时）。
        """
        outs = []
        for line in blk.code.split("\n"):
            if not line.strip() or line.strip().startswith("--"):
                continue
            try:
                code = render(line, ctx)
            except KeyError as e:
                res.error = "第 %s 块占位符渲染失败：%s" % (blk.key, e)
                res.steps.append({"block": blk.key, "code": line, "ok": False, "ret": -1,
                                  "out": str(e)})
                return None
            st = {"block": blk.key, "code": code}
            try:
                ret, out = self.c.lua(code, raise_on_error=False)
            except Exception as e:
                st.update(ok=False, ret=-99, out=str(e)[:400])
                res.steps.append(st)
                res.error = "第 %s 块连接失败：%s\n  %s" % (blk.key, e, code)
                return None
            st.update(ok=(ret == 0), ret=ret, out=out.strip()[:400])
            res.steps.append(st)
            outs.append((code, ret, out.strip()))
            if ret != 0:
                res.error = "Lua 执行失败（第 %s 块）\n  %s\n  -> %s" % (blk.key, code, out.strip()[:300])
                return None
        return outs

    def _harvest(self, key: str, outs, ctx: Dict[str, str], spec: ScenarioSpec) -> None:
        """把块内每条语句的真实返回值写进上下文（供后续块渲染）。"""
        if key == "sides":
            guids = [o[2].strip().strip('"') for o in outs]
            if len(guids) != len(spec.sides):
                raise LuaError("AddSide 返回条数 %d 与推演方数 %d 不符" % (len(guids), len(spec.sides)))
            for s, g in zip(spec.sides, guids):
                if not g:
                    from .lyclient import parse_sides
                    name2guid = parse_sides(self.c.lua("GetSides()")[1])
                    g = name2guid.get(s.name, "")
                if not g:
                    raise LuaError("推演方 %s 没有拿到 GUID" % s.name)
                ctx["S:%s" % s.name] = "'%s'" % g
        elif key == "units":
            guids = [o[2].strip().strip('"') for o in outs]
            if len(guids) != len(spec.units):
                raise LuaError("AddUnit 返回条数 %d 与单元数 %d 不符" % (len(guids), len(spec.units)))
            for u, g in zip(spec.units, guids):
                if not g:
                    raise LuaError("单元 %s 没有拿到 GUID" % u.name)
                ctx["U:%s" % u.name] = g
        elif key == "missions":
            from .lyclient import parse_mission_guid
            for m, o in zip(spec.missions, outs):
                g = parse_mission_guid(o[2])
                if not g:
                    raise LuaError("任务 %s 的返回里没有 GUID：%s" % (m.name, o[2][:200]))
                ctx["M:%s" % m.name] = "'%s'" % g

    def readback(self, name: str):
        """用引擎回读 .scen 并解析 digest。"""
        try:
            code, xml = self.c.scenario_content("%s.scen" % name)
        except Exception as e:
            return False, "gRPC 失败：%s" % e, None
        if code != 0 or len(xml) < 200:
            return False, "引擎返回 code=%s（%s）" % (code, xml[:120]), None
        try:
            digest = parse_scenario_xml(xml)
        except Exception as e:
            return False, "XML 解析失败：%s" % e, None
        return True, "回读 %d 字节" % len(xml), digest

    def save_artifacts(self, spec: ScenarioSpec, prog: LuaProgram, res: BuildResult) -> str:
        d = os.path.join(self.out_dir, res.name)
        os.makedirs(d, exist_ok=True)
        spec.to_json(os.path.join(d, "spec.json"))
        with open(os.path.join(d, "scenario.lua"), "w", encoding="utf-8") as f:
            f.write(prog.to_text())
        with open(os.path.join(d, "build.json"), "w", encoding="utf-8") as f:
            json.dump(res.to_dict(), f, ensure_ascii=False, indent=1)
        if res.digest:
            with open(os.path.join(d, "digest.json"), "w", encoding="utf-8") as f:
                json.dump(res.digest, f, ensure_ascii=False, indent=1)
        if res.report:
            with open(os.path.join(d, "verify.md"), "w", encoding="utf-8") as f:
                f.write(res.report.to_markdown("想定验收报告：%s" % spec.title))
        return d


def _q(s: str) -> str:
    return "'%s'" % str(s).replace("\\", "\\\\").replace("'", "\\'")


PLACEHOLDER = re.compile(r"%\{([SUM]):([^}]+)\}")


def render(code: str, ctx: Dict[str, str]) -> str:
    """把 ``%{S:红方}`` / ``%{U:舰名}`` / ``%{M:任务名}`` 换成真实值。"""
    def sub(m):
        key = "%s:%s" % (m.group(1), m.group(2))
        if key not in ctx:
            raise KeyError("渲染失败：上下文缺少 %s（已解析：%s）"
                           % (key, ", ".join(sorted(ctx))[:300]))
        return ctx[key]
    return PLACEHOLDER.sub(sub, code)
