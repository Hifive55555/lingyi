# -*- coding: utf-8 -*-
"""派生「反舰饱和攻击」微想定 ``PI-SHIP-SAT.scen``。

目的：让蓝方的反舰火力真的打到红方登陆编队，使「登陆船只集群自卫」
（``engine/LingYi/ShipClusterDefense.py``）这条规则被触发 —— 整场想定里它的
``ship_defense_count`` 恒为 0，取不到样本。

链路（照 ``docs/无头Lua建想定方法手册.md`` §6）：

    LoadScenario({PATH=底本})            -- 拿真实想定当底，不从空白手搓
    GetCurrentScenario()                 -- 存底（含 GUID/名称/坐标/任务/条令）
    DeleteUnit({GUID=…})                 -- 先删 1 个验签名，再批量清场
    SetUnit({GUID=…, LATITUDE=, LONGITUDE=})   -- 把蓝方反舰发射车平移到登陆编队 50–70 km
    SetDoctrine({side=…}, {WCS_Surface=…})     -- 蓝方对海自由开火 / 红方保持限制
    SetScenarioInfo({DURATION=2400})            -- 时长缩到 40 分钟
    Command_SaveScen('…/PI-SHIP-SAT.scen')
    GetScenarioContent('PI-SHIP-SAT.scen')      -- 回读验收

每一条 Lua 的 (code, result) 都落盘到 ``out/PI-SHIP-SAT/build.json``（与
``out/EXP1-*/build.json`` 同样的做法），验收摘要写 ``out/PI-SHIP-SAT/verify.md``。

用法::

    python build_pi_ship_sat.py --inventory-only   # 只加载 + 存底 + 打清单（不动想定）
    python build_pi_ship_sat.py                    # 完整派生 + 保存 + 回读验收
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from sce_agent.digest import digest_summary, parse_scenario_xml   # noqa: E402
from sce_agent.engine import EngineManager, Target                 # noqa: E402
from sce_agent.lyclient import LuaClient, LuaError                  # noqa: E402
import ServerInterface_pb2 as pb2                                   # noqa: E402  lyclient 已把 gen 加入 sys.path

BASE_SCEN = '诺曼底2027(人机协同-人人版)_有红有蓝.scen'
OUT_SCEN = 'PI-SHIP-SAT.scen'
SCEN_DIR = 'D:/LingYi/Data/Scenarios'
OUT_PATH = '%s/%s' % (SCEN_DIR.rstrip('/'), OUT_SCEN)
WIP_SCEN = 'PI-SHIP-SAT-wip.scen'          # 仅为「把底本解压成 XML 读回来」的临时文件
WIP_PATH = '%s/%s' % (SCEN_DIR.rstrip('/'), WIP_SCEN)
OUT_DIR = os.path.join(HERE, 'out', 'PI-SHIP-SAT')
DURATION_S = 2400          # 40 分钟

#: 红方保留：**全部舰船**（雷鸣 #1–#5,#8,#10、PR.2235.0 #1#2、蟾蜍 I #1–#7、23900 #1、R91）
KEEP_RED_KINDS = ('Ship',)
#: 蓝方保留：**岸基反舰火力**。
#: 注意（实测）：底本里的 F/A-18F（母舰 CVN 80）与 B-2A（西班牙机场）是**驻留状态**
#: （Lon/Lat=0、DA=6.1），删了母舰/机场引擎会级联删掉载机，而保留母舰就多出一整艘
#: 航母（自带雷达/舰空弹），会把“红方只剩船团”的对照冲淡。经主智能体裁决（选项 A）：
#: 本微想定只留岸基发射车，蓝方反舰火力 = 9 台发射车 + 2 台无人机发射车。
KEEP_BLUE_KEYS = ('反舰导弹排', '海马斯', '无人机发射车')
#: 登陆船只集群（用来算「距登陆编队多远」）
LANDING_KEYS = ('蟾蜍', '23900')
#: 蓝方要平移到 50–70 km 的火力
MOVE_KEYS = ('反舰导弹排', '海马斯')
NEAR_KM = (50.0, 70.0)

_QUOTES = {'\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'"}


def norm(s: str) -> str:
    """名称规范化：去空白、统一引号、小写。"""
    s = (s or '')
    for a, b in _QUOTES.items():
        s = s.replace(a, b)
    return ''.join(s.split()).lower()


def hits(name: str, keys) -> bool:
    n = norm(name)
    return any(k in n for k in keys)


# ------------------------------------------------------------------ 地理
def dest_km(lat: float, lon: float, az_deg: float, dist_km: float):
    """从 (lat, lon) 沿方位 az 走 dist_km 的落点。"""
    r = 6371.0088
    br, d = math.radians(az_deg), dist_km / r
    la, lo = math.radians(lat), math.radians(lon)
    la2 = math.asin(math.sin(la) * math.cos(d) + math.cos(la) * math.sin(d) * math.cos(br))
    lo2 = lo + math.atan2(math.sin(br) * math.sin(d) * math.cos(la),
                          math.cos(d) - math.sin(la) * math.sin(la2))
    return math.degrees(la2), (math.degrees(lo2) + 540.0) % 360.0 - 180.0


def km_between(a, b) -> float:
    """两点球面距离（km）。a/b 是 (lat, lon)。"""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2 +
         math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * 6371.0088 * math.asin(min(1.0, math.sqrt(h)))


# ------------------------------------------------------------------ 记录
class Builder(object):
    """一条 Lua 一次 executeLua，逐条记录 code / 原文。"""

    def __init__(self, client: LuaClient):
        self.c = client
        self.records = []
        self.t0 = time.time()

    def lua(self, phase: str, script: str, expect_ok=True):
        code, res = self.c.lua(script, raise_on_error=False)
        self.records.append({'step': len(self.records) + 1, 'phase': phase,
                             'script': script, 'code': code,
                             'result': res[:4000], 't': round(time.time(), 3)})
        print('%-10s code=%d  %s' % (phase, code, res.strip()[:160].replace('\n', ' ')),
              flush=True)
        if expect_ok and code != 0:
            raise LuaError('%s 失败：%s\n%s' % (phase, script, res[:800]))
        return code, res

    def dump(self, path: str):
        d = dict(scenario=OUT_SCEN, base=BASE_SCEN, started=time.strftime('%Y-%m-%d %H:%M:%S'),
                 elapsed_s=round(time.time() - self.t0, 1), calls=self.records)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)


# ------------------------------------------------------------------ 主流程
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=21005)
    ap.add_argument('--inventory-only', action='store_true',
                    help='只加载底本、存 XML、打印单元清单（不删不改不存）')
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    t = Target()
    print('· 清场：taskkill /f /im Plat.exe', flush=True)
    EngineManager.stop_all(t)
    time.sleep(3)
    mgr = EngineManager(t, port=args.port, dds_port=args.port + 1000, room='pi-ship-sat')
    c = LuaClient(t.host, args.port, timeout=180)
    ok, ver = c.ping(timeout=8)
    if not ok:
        # 端口在监听但不应答（上一次引擎被打僵）也一律重起
        print('· 拉起无头引擎 :%d ……' % args.port, flush=True)
        mgr.start(wait=150, force=True)
        c = LuaClient(t.host, args.port, timeout=180)
        ok, ver = c.ping(timeout=20)
    if not ok:
        raise SystemExit('引擎不可用：%s' % ver)
    print('· 已连接 %s:%d build %s' % (t.host, args.port, ver), flush=True)

    b = Builder(c)

    # 1) 加载底本 + 存底
    #    注意：GetCurrentScenario() 回的是**仍压缩**的 <ScenContainer>（实测），
    #    要拿可解析的 <Scenario> 必须让引擎先落一个盘再 GetScenarioContent 解压回读。
    b.lua('load', "LoadScenario({PATH='%s'})" % BASE_SCEN)
    b.lua('dump.save', "Command_SaveScen('%s')" % WIP_PATH)
    xml_before = b.lua('dump', "GetScenarioContent('%s')" % WIP_SCEN)[1]
    p_before = os.path.join(OUT_DIR, 'scenario_before.xml')
    open(p_before, 'w', encoding='utf-8').write(xml_before)
    d0 = parse_scenario_xml(xml_before)
    print('· 底本：%s' % digest_summary(d0), flush=True)

    red = [u for u in d0['units'] if u['side'] == '红方']
    blue = [u for u in d0['units'] if u['side'] == '蓝方']

    keep_red = [u for u in red if u['kind'] in KEEP_RED_KINDS]
    keep_blue = [u for u in blue if hits(u['name'], KEEP_BLUE_KEYS)]
    keep = keep_red + keep_blue
    keep_ids = {u['id'] for u in keep}
    drop = [u for u in d0['units'] if u['id'] not in keep_ids]

    print('· 红方 %d 单元 → 保留舰船 %d' % (len(red), len(keep_red)), flush=True)
    for u in keep_red:
        print('    keep  %-28s %s' % (u['name'], u['kind']), flush=True)
    print('· 蓝方 %d 单元 → 保留反舰火力 %d' % (len(blue), len(keep_blue)), flush=True)
    for u in keep_blue:
        print('    keep  %-28s %s' % (u['name'], u['kind']), flush=True)
    print('· 待删除 %d 单元' % len(drop), flush=True)

    if args.inventory_only:
        b.lua('side.doctrine', 'GetSides()')
        t.run('del /q "%s"' % WIP_PATH.replace('/', '\\'), check=False)
        b.dump(os.path.join(OUT_DIR, 'inventory.json'))
        print('· --inventory-only：只存底，不改想定', flush=True)
        return

    # 2) 先删 1 个验小样本（手册：DeleteUnit({guid=…})，返回布尔 M4 取不回来；
    #    坑：删完再用 GetUnit 查这个 GUID 会把引擎打僵（实测 UNKNOWN: Unexpected
    #    error in RPC handling → 后续 RPC 全部 Deadline Exceeded），所以改用
    #    「落盘 + GetScenarioContent 回读点数」来验。
    order = {'Aircraft': 0, 'Submarine': 1, 'Ship': 2, 'Facility': 3}
    drop.sort(key=lambda u: order.get(u['kind'], 9))
    victim = drop[0]
    b.lua('del.probe', "DeleteUnit({guid='%s'})" % victim['id'], expect_ok=False)
    b.lua('del.probe.save', "Command_SaveScen('%s')" % WIP_PATH)
    xml_probe = b.lua('del.probe.readback', "GetScenarioContent('%s')" % WIP_SCEN)[1]
    d_probe = parse_scenario_xml(xml_probe)
    gone = victim['name'] not in {u['name'] for u in d_probe['units']}
    b.records.append({'step': len(b.records) + 1, 'phase': 'del.probe.verify',
                      'script': '(count after 1 delete)',
                      'code': 0 if gone else 1,
                      'result': '单元数 %d（删除前 %d），%s %s' %
                                (len(d_probe['units']), len(d0['units']), victim['name'],
                                 '已消失' if gone else '仍在')})
    print('· DeleteUnit 小样本校验：%s → %s（单元 %d → %d）'
          % (victim['name'], '已删除' if gone else '未删除',
             len(d0['units']), len(d_probe['units'])), flush=True)
    if not gone:
        raise SystemExit('DeleteUnit 未生效，停止（避免半成品想定）')

    # 3) 批量删除其余单元（一条语句一次调用，便于定位）
    failed = []
    died = ''
    for u in drop[1:]:
        try:
            code, res = c.lua("DeleteUnit({guid='%s'})" % u['id'], timeout=60,
                              raise_on_error=False)
        except LuaError as e:                      # RPC 层失败：记下已删到哪，中止批量
            died = '%s（%s）' % (u['name'], str(e)[:200])
            b.records.append({'step': len(b.records) + 1, 'phase': 'del.rpc_error',
                              'script': "DeleteUnit({guid='%s'})" % u['id'],
                              'code': -1, 'result': str(e)[:400], 'unit': u['name']})
            break
        b.records.append({'step': len(b.records) + 1, 'phase': 'del',
                          'script': "DeleteUnit({guid='%s'})" % u['id'],
                          'code': code, 'result': res[:400], 'unit': u['name']})
        if code != 0:
            failed.append(u['name'])
    done = len(drop) - 1 - len(failed) - (1 if died else 0)
    print('· 删除完成：成功 %d，失败 %d%s%s'
          % (done, len(failed), ('：' + '、'.join(failed[:5])) if failed else '',
             ('；RPC 中断于 ' + died) if died else ''), flush=True)
    b.records.append({'step': len(b.records) + 1, 'phase': 'del.summary',
                      'script': '(summary)',
                      'code': 0 if (not failed and not died) else 1,
                      'result': 'deleted=%d failed=%d died=%s' % (done, len(failed), died)})
    if died:
        raise SystemExit('批量删除时引擎 RPC 中断：%s' % died)

    # 4) 选一个登陆编队 + 在 50–70 km 的陆地上放蓝方发射车
    landing = [u for u in keep_red if hits(u['name'], LANDING_KEYS)]
    if not landing:
        raise SystemExit('红方没有登陆舰船（蟾蜍/23900），无法定义登陆编队')
    # 按任务名把红方舰船分组（舰 + 护卫都算一个编队）；没挂任务的舰按位置归到最近的编队。
    # 取「登陆舰最多」的那一群；并列时再比总舰数，再并列取任务名字典序最小。
    groups = {}
    loose = []
    for u in keep_red:
        mn = u.get('mission_name') or ''
        if mn:
            groups.setdefault(mn, []).append(u)
        else:
            loose.append(u)
    if groups:
        cents = {k: (sum(x['lat'] for x in v) / len(v), sum(x['lon'] for x in v) / len(v))
                 for k, v in groups.items()}
        for u in loose:
            k = min(cents, key=lambda g: km_between((u['lat'], u['lon']), cents[g]))
            groups[k].append(u)
    else:
        groups['(无任务)'] = loose

    def _gscore(us):
        return (sum(1 for u in us if hits(u['name'], LANDING_KEYS)), len(us))

    best = max(_gscore(us) for us in groups.values())
    gname, gship = sorted((kv for kv in groups.items() if _gscore(kv[1]) == best),
                          key=lambda kv: kv[0])[0]
    clat = sum(u['lat'] for u in gship) / len(gship)
    clon = sum(u['lon'] for u in gship) / len(gship)
    center = (clat, clon)
    print('· 登陆编队「%s」%d 艘（登陆舰 %d），质心 (%.4f, %.4f)'
          % (gname, len(gship), _gscore(gship)[0], clat, clon), flush=True)

    movers = [u for u in keep_blue if hits(u['name'], MOVE_KEYS)]
    if not movers:
        raise SystemExit('蓝方没有可平移的反舰发射车（反舰导弹排/海马斯）')

    # 4.1 找陆地上的基准点（设施不能落水）——瞄准 50–58 km：
    #     既在 65 km 舰空拦截包线内，又不会因为射程边缘而打不出去。
    anchor = None
    for r in (54.0, 56.0, 52.0, 58.0, 60.0, 50.0):
        for az in range(0, 360, 6):
            p = dest_km(clat, clon, az, r)
            e, _ = c.get_elevation(p[0], p[1])
            if e is not None and e > 5.0:
                anchor = (p, az, r)
                break
        if anchor:
            break
    if not anchor:
        raise SystemExit('登陆编队 50–70 km 内找不到陆地，无法安置反舰发射车')
    print('· 基准炮位 (%.4f, %.4f) 方位%d° 距离%.0fkm' %
          (anchor[0][0], anchor[0][1], anchor[1], anchor[2]), flush=True)

    # 4.2 炮位：以基准炮位为中心的小范围内找互不重叠的陆地点（岛上/海岸地窄，
    #     大角度撒点会落水 → 逐个用 getElevation 验，全失败的才回落到基准点）
    placements = []
    used = set()
    for i, u in enumerate(movers):
        picked = None
        for rad in (0.0, 1.2, 2.4, 3.6, 5.0):
            for d in range(0, 360, 45):
                p = dest_km(anchor[0][0], anchor[0][1], (d + i * 40) % 360, rad)
                key = (round(p[0], 4), round(p[1], 4))
                if key in used:
                    continue
                if not (NEAR_KM[0] <= km_between(p, center) <= NEAR_KM[1]):
                    continue
                e, _ = c.get_elevation(p[0], p[1])
                if e is not None and e > 5.0:
                    picked = p
                    used.add(key)
                    break
            if picked:
                break
        if picked is None:
            picked = anchor[0]
        placements.append((u, picked))

    # 4.2 平移（SetUnit 的 LATITUDE/LONGITUDE 就是手册里的“移动单元位置”）
    moved = []
    for u, p in placements:
        b.lua('move', "SetUnit({GUID='%s', LATITUDE=%.6f, LONGITUDE=%.6f})"
              % (u['id'], p[0], p[1]), expect_ok=False)
        res = b.records[-1].get('result', '')
        ok = b.records[-1]['code'] == 0 and '失败' not in res
        moved.append({'name': u['name'], 'lat': p[0], 'lon': p[1],
                      'km_to_fleet': round(km_between(p, center), 1), 'ok': ok})
        print('    move  %-24s -> (%.4f, %.4f) 距编队 %.1f km %s'
              % (u['name'], p[0], p[1], km_between(p, center), '' if ok else '（失败）'), flush=True)

    # 5) 条令：蓝方对海自由开火；红方对海保持限制
    #    坑 17 复现：Lua ``SetDoctrine`` 返回 code=0 但**不落盘**（下面先用“存盘+回读”证实）；
    #    生效的是命名 RPC ``setDoctrine(targetType='side')`` —— 带类型的通道才写得进去。
    wcs_before = {s['name']: (s.get('doctrine') or {}).get('WCS_Surface') for s in d0['sides']}
    print('· 条令前值 WCS_Surface: %s' % wcs_before, flush=True)
    b.lua('doctrine.lua', "SetDoctrine({side='蓝方'}, {WCS_Surface='0'})", expect_ok=False)
    b.lua('doctrine.lua.save', "Command_SaveScen('%s')" % WIP_PATH, expect_ok=False)
    _xml = b.lua('doctrine.lua.readback', "GetScenarioContent('%s')" % WIP_SCEN)[1]
    _d = parse_scenario_xml(_xml.lstrip())
    _wcs = next(((s.get('doctrine') or {}).get('WCS_Surface')
                 for s in _d['sides'] if s['name'] == '蓝方'), None)
    b.records.append({'step': len(b.records) + 1, 'phase': 'doctrine.lua.verify',
                      'script': '(save+readback after Lua SetDoctrine)',
                      'code': 0,
                      'result': '存盘后回读蓝方 WCS_Surface=%s（期望 0，仍为 %s ⇒ Lua 不落盘）'
                                % (_wcs, wcs_before.get('蓝方'))})
    print('· Lua SetDoctrine 后回读：蓝方 WCS_Surface=%s（坑 17 确认）' % _wcs, flush=True)

    blue_id = next(s['id'] for s in d0['sides'] if s['name'] == '蓝方')
    rpc_res = 'ok'
    try:
        req = pb2.RequestSetDoctrine(
            targetType='side', targetId=blue_id,
            doctrine=pb2.MIDoctrineSettings(
                rulesOfEngagementConfig=pb2.RulesOfEngagementConfig(weaponControlSurface='0')))
        r = c.stub.setDoctrine(req, timeout=60)
        rpc_res = r.result.decode('utf-8', 'replace')
        rpc_code = int(r.code)
    except Exception as e:                       # grpc 层失败：记原文，不掩盖
        rpc_code, rpc_res = -1, '%s: %s' % (type(e).__name__, e)
    b.records.append({'step': len(b.records) + 1, 'phase': 'doctrine.blue.rpc',
                      'script': "setDoctrine{targetType='side', targetId=%s, "
                                "rulesOfEngagementConfig.weaponControlSurface='0'}" % blue_id,
                      'code': rpc_code, 'result': rpc_res[:2000]})
    print('· setDoctrine RPC（蓝方对海自由开火）code=%d %s' % (rpc_code, rpc_res[:80]), flush=True)
    try:
        g = c.stub.getDoctrine(
            pb2.RequestGetDoctrine(targetType='side', targetId=blue_id), timeout=60)
        b.records.append({'step': len(b.records) + 1, 'phase': 'doctrine.blue.rpc.verify',
                          'script': "getDoctrine{targetType='side', targetId=%s}" % blue_id,
                          'code': int(g.code),
                          'result': g.result.decode('utf-8', 'replace')[:4000]})
    except Exception as e:
        b.records.append({'step': len(b.records) + 1, 'phase': 'doctrine.blue.rpc.verify',
                          'script': 'getDoctrine', 'code': -1, 'result': str(e)[:400]})

    red_wcs = str(wcs_before.get('红方') or '')
    if red_wcs not in ('1', '2'):
        b.lua('doctrine.red', "SetDoctrine({side='红方'}, {WCS_Surface='1'})", expect_ok=False)
        red_wcs = '1'
    else:
        b.records.append({'step': len(b.records) + 1, 'phase': 'doctrine.red',
                          'script': '(skip) 红方 WCS_Surface 已是 %s，保持限制不动' % red_wcs,
                          'code': 0, 'result': 'unchanged'})

    # 6) 时长 40 分钟
    b.lua('duration', 'SetScenarioInfo({DURATION=%d})' % DURATION_S, expect_ok=False)

    # 7) 保存到新文件名（绝不覆盖底本）
    assert OUT_SCEN != BASE_SCEN and WIP_SCEN != BASE_SCEN
    code, res = b.lua('save', "Command_SaveScen('%s')" % OUT_PATH, expect_ok=False)
    if code != 0:
        b.lua('save.alt', "SaveScenario('%s')" % OUT_PATH, expect_ok=False)
    # 存底用的中间文件不留（想定目录里只留 PI-SHIP-SAT.scen）
    t.run('del /q "%s"' % WIP_PATH.replace('/', '\\'), check=False)

    # 8) 回读验收
    code, xml_after = b.lua('readback', "GetScenarioContent('%s')" % OUT_SCEN, expect_ok=False)
    p_after = os.path.join(OUT_DIR, 'PI-SHIP-SAT.xml')
    if code == 0 and xml_after.lstrip().startswith('<'):
        xml_after = xml_after.lstrip()
        open(p_after, 'w', encoding='utf-8').write(xml_after)
    else:
        raise SystemExit('回读失败，无法验收：%s' % xml_after[:400])
    d1 = parse_scenario_xml(xml_after)

    # 9) 验收摘要
    lines = []
    add = lines.append
    add('# PI-SHIP-SAT 微想定验收')
    add('')
    add('底本 `%s` → 派生 `%s`（40 分钟）。生成于 %s。'
        % (BASE_SCEN, OUT_SCEN, time.strftime('%Y-%m-%d %H:%M:%S')))
    add('')
    add('| 项 | 底本 | 派生 |')
    add('| --- | --- | --- |')
    add('| 单元总数 | %d | %d |' % (len(d0['units']), len(d1['units'])))
    for side in ('红方', '蓝方'):
        c0 = d0['counts'].get(side, {})
        c1 = d1['counts'].get(side, {})
        add('| %s 单元（分类型） | %s | %s |' % (side, c0 or '—', c1 or '—'))
        m0 = [m['name'] for m in d0['missions'] if m['side'] == side]
        m1 = [m['name'] for m in d1['missions'] if m['side'] == side]
        add('| %s 任务数 | %d | %d |' % (side, len(m0), len(m1)))
        w0 = (next((s for s in d0['sides'] if s['name'] == side), {}) or {}).get('doctrine', {})
        w1 = (next((s for s in d1['sides'] if s['name'] == side), {}) or {}).get('doctrine', {})
        add('| %s WCS_Surface | %s | %s |' % (side, w0.get('WCS_Surface'), w1.get('WCS_Surface')))
    add('| 时长（秒） | %d | %d |' % (d0['duration_s'], d1['duration_s']))
    add('| 参考点 | %d | %d |' % (len(d0['reference_points']), len(d1['reference_points'])))
    add('')
    add('> **已知偏差（主智能体裁定 A）**：底本的蓝方载机 `F/A-18F型战斗机 #1–#5` 与'
        ' `B-2A 轰炸机 #1#2` 是**驻留状态**（Lon/Lat=0、DA=6.1m），分别挂靠在蓝方航母'
        ' `CVN 80福特级航空母舰` 与西班牙一侧机场上；删除宿主时引擎会**级联删除**这些载机。'
        '保留它们就得连带保留航母/机场（会把航母编队的雷达与舰空弹带进战场，冲淡“红方只剩船团”的对照），'
        '故本微想定不保留航空反舰兵力，蓝方反舰火力 = 9 台岸基发射车（雄风II ×5、HIMARS ×4）'
        ' + 2 台 LUCAS 无人机发射车。')
    add('')
    add('## 保留清单（派生后）')
    add('')
    for u in d1['units']:
        add('- %s `%s` %s @ (%.4f, %.4f) 任务=%s'
            % (u['side'], u['name'], u['kind'], u['lat'], u['lon'], u.get('mission_name', '')))
    add('')
    add('## 蓝方发射车新炮位（距登陆编队「%s」质心 %.4f,%.4f）'
        % (gname, clat, clon))
    add('')
    add('| 单元 | 纬度 | 经度 | 距编队 km | 生效 |')
    add('| --- | --- | --- | --- | --- |')
    for m in moved:
        add('| %s | %.4f | %.4f | %.1f | %s |'
            % (m['name'], m['lat'], m['lon'], m['km_to_fleet'], '是' if m['ok'] else '否'))
    add('')
    add('## 结论')
    add('')
    checks = [
        ('单元清场', len(d1['units']) == len(keep), '%d 个（期望 %d）' % (len(d1['units']), len(keep))),
        ('红方只剩舰船', all(u['kind'] == 'Ship' for u in d1['units'] if u['side'] == '红方'),
         '%d 艘' % sum(1 for u in d1['units'] if u['side'] == '红方')),
        ('蓝方只剩岸基发射车',
         all(u['kind'] == 'Facility' for u in d1['units'] if u['side'] == '蓝方'),
         '%d 台' % sum(1 for u in d1['units'] if u['side'] == '蓝方')),
        ('蓝方 WCS_Surface 自由开火',
         str((next((s for s in d1['sides'] if s['name'] == '蓝方'), {}) or {}).get('doctrine', {}).get('WCS_Surface')) == '0',
         'RPC setDoctrine 写入后回读=%s'
         % str((next((s for s in d1['sides'] if s['name'] == '蓝方'), {}) or {}).get('doctrine', {}).get('WCS_Surface'))),
        ('Lua SetDoctrine 不落盘（坑 17 复现）', str(_wcs) == str(wcs_before.get('蓝方')),
         'Lua 下发后回读=%s，下发前=%s' % (_wcs, wcs_before.get('蓝方'))),
        ('红方 WCS_Surface 非自由', str(red_wcs) != '0', str(red_wcs)),
        ('时长 2400s', abs(d1['duration_s'] - DURATION_S) < 2, '%d' % d1['duration_s']),
        ('发射车全部进入 50–70 km',
         all(NEAR_KM[0] <= m['km_to_fleet'] <= NEAR_KM[1] for m in moved),
         '%s' % [m['km_to_fleet'] for m in moved]),
        ('发射车平移全部生效', all(m['ok'] for m in moved), ''),
        ('任务数不变（未动任务）',
         len(d1['missions']) == len(d0['missions']),
         '%d → %d' % (len(d0['missions']), len(d1['missions']))),
    ]
    for name, ok, detail in checks:
        add('- %s %s %s' % ('✅' if ok else '❌', name, ('（%s）' % detail) if detail else ''))
    add('')
    add('回读 XML：`%s`（%d 字节）' % (p_after, len(xml_after)))
    open(os.path.join(OUT_DIR, 'verify.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('\n'.join(lines), flush=True)

    b.dump(os.path.join(OUT_DIR, 'build.json'))
    print('· build.json / verify.md 已写入 %s' % OUT_DIR, flush=True)


if __name__ == '__main__':
    main()
