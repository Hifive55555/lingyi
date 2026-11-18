# -*- coding: utf-8 -*-
"""态势真源採样器（实验用只读智能体）

每个决策步把「本方全部单元 + 全部情报 + 本方总分」写成一行 JSONL，
供离线计算命中/毁伤/存活/开火等指标。**不下发任何指令**，不占指令配额。

环境变量：
  PI_TAP_DIR   输出目录（默认 D:/LingYi/exp/v2/tap）
  PI_TAP_SIDE  标记用推演方名（缺省取 side_name）
  PI_TAP_TAG   批次标记（写进每行，便于分文件/分批）
  PI_TAP_EVERY 情报落盘间隔（默认 2：每 2 个决策步记一次情报；本方单元每步都记）

与 RuleAgentBase 同一套取值口径（见 monitor-agent/lymonitor/core.py）：
  CurrentSpeed 单位是节，统一 ×1.852 转 km/h。
"""
import json
import os
import time

from engine.LingYi.entitys.agent_base import RuleAgentBase

KNOT = 1.852
_KIND = (('air', 'aircrafts'), ('sea', 'ships'), ('sea', 'submarines'), ('land', 'facilitys'))


def _g(o, key, default=None):
    if o is None:
        return default
    if isinstance(o, dict):
        for k in (key, key.capitalize(), key.lower(), key.upper()):
            if k in o:
                return o[k]
        return default
    return getattr(o, key, default)


def _num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


class Agent(RuleAgentBase):
    """只读採样器。"""

    def __init__(self, side_name, params=None):
        RuleAgentBase.__init__(self, side_name)
        self.side = os.environ.get('PI_TAP_SIDE') or str(side_name)
        self.tag = os.environ.get('PI_TAP_TAG', 'run')
        d = os.environ.get('PI_TAP_DIR', r'D:/LingYi/exp/v2/tap')
        try:
            os.makedirs(d)
        except OSError:
            pass
        self.fp = os.path.join(d, '%s__%s.jsonl' % (self.tag, self.side))
        self.fh = open(self.fp, 'a', encoding='utf-8')
        self.every = max(1, int(float(os.environ.get('PI_TAP_EVERY', '2'))))
        self.last_t = 1e9
        self.ep = 0
        self.n = 0

    # ------------------------------------------------------------------
    def _own(self):
        out = []
        for kind, attr in _KIND:
            for guid, u in list((getattr(self, attr, None) or {}).items()):
                lat, lon = _num(_g(u, 'Lat', 0)), _num(_g(u, 'Lon', 0))
                if abs(lat) < 1e-9 and abs(lon) < 1e-9:
                    continue
                out.append([str(_g(u, 'Name', guid) or guid), kind,
                            round(lat, 5), round(lon, 5),
                            round(_num(_g(u, 'CurrentAltitude', 0)), 0),
                            round(_num(_g(u, 'CurrentSpeed', 0)) * KNOT, 0),
                            round(_num(_g(u, 'CurrentHeading', 0)), 1),
                            round(_num(_g(u, 'DamagePercent', 0)), 3)])
        return out

    def _contacts(self, situation):
        cts = situation[1] if isinstance(situation, (tuple, list)) and len(situation) > 1 else None
        if not isinstance(cts, dict):
            cts = getattr(self, 'Contacts', None) or {}
        out = []
        for cid, c in cts.items():
            lat, lon = _num(_g(c, 'Lat', 0)), _num(_g(c, 'Lon', 0))
            if abs(lat) < 1e-9 and abs(lon) < 1e-9:
                continue
            out.append([str(_g(c, 'Name', cid) or cid),
                        int(_num(_g(c, 'Type', -1), -1)),
                        round(lat, 5), round(lon, 5),
                        round(_num(_g(c, 'CurrentAltitude', 0)), 0),
                        round(_num(_g(c, 'CurrentSpeed', 0)) * KNOT, 0),
                        round(_num(_g(c, 'CurrentHeading', 0)), 1)])
        return out

    # ------------------------------------------------------------------
    def initial(self, situation):
        self.step(0, situation)

    def step(self, time_elapse, situation):
        try:
            t = _num(time_elapse, 0.0)
            if t < self.last_t:
                self.ep += 1
                self.n = 0
            self.last_t = t
            self.n += 1
            rec = {
                'tag': self.tag, 'side': self.side, 'ep': self.ep, 'i': self.n, 't': t,
                'score': _num(getattr(self, 'TotalScore', 0)),
                'own': self._own(),
                'cts': (self._contacts(situation) if self.n % self.every == 1 else None),
                'wall': round(time.time(), 2),
            }
            self.fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
            if self.n % 20 == 0:
                self.fh.flush()
        except Exception as e:                                   # 只读，绝不影响推演
            try:
                self.fh.write(json.dumps({'tag': self.tag, 'side': self.side,
                                          'err': str(e)[:300]}, ensure_ascii=False) + '\n')
                self.fh.flush()
            except Exception:
                pass

    def is_done(self, *a, **k):
        return False
