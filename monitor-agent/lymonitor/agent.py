# -*- coding: utf-8 -*-
"""
监控智能体（客户端「智能体编辑」导入用的那个）—— 只算、不动手。

组成：
    Player         平台给的基础类（提供 self.aircrafts / self.ships / … / self.Contacts）
    Monitor        判定组件（lymonitor/monitor.py，也可以是别的智能体直接嵌进去用的那个）
    SnapServer     小窗的 WebSocket 服务（127.0.0.1:8762/ws）

每个决策周期：Monitor.step() 算一次 → 打包成快照 → 推给小窗 + 往客户端消息栏推一行汇总。
**不下发任何指令**（不调 attack_* / set_* / plotted_course / withdraw_from_mission），
所以不需要 zmq 收发锁，不会和 step 线程抢口，可以和 Mission_all_red.py /
Mission_tactics_red.py 同时导入、同时启动。
"""

import json
import logging
import os
import sys
import threading
import time
from collections import OrderedDict
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _find_ai_dir(start):
    """往上找 ``intelligent\\ai``（里面有 engine/LingYi/entitys/player.py）。

    不写死层级：整包放在 ``ai\\agent\\monitor-agent`` 还是 ``ai\\monitor-agent``
    都能自己找对。
    """
    p = Path(start).resolve()
    for cand in [p] + list(p.parents):
        if (cand / 'engine' / 'LingYi' / 'entitys' / 'player.py').exists():
            return str(cand)
    return str(p.parents[2]) if len(p.parents) > 2 else str(p)


_AI_DIR = _find_ai_dir(_HERE)
if _AI_DIR not in sys.path:
    sys.path.insert(0, _AI_DIR)

from engine.LingYi.entitys.agent_base import RuleAgentBase   # noqa: E402
from . import core                                        # noqa: E402
from .monitor import Monitor                              # noqa: E402

log = logging.getLogger("监控小窗")
log.setLevel(logging.INFO)

WEB = _HERE / "web"
PORT = int(os.environ.get("LY_MONITOR_PORT", "8762"))


class MonitorAgent(RuleAgentBase):
    """平台规则智能体基类 RuleAgentBase(=Player + initial/step/deduction_end/is_done)。

    注意：必须是 RuleAgentBase。只继承 Player 时平台拿不到 is_done / deduction_end，
    智能体会被当成“已结束”，一局跑几十步就停。
    """
    # ---------------------------------------------------------------- 可调参数
    DECISION_SEC = 5           # 决策间隔（推演秒）。5 s 是平台允许的最小值
    MAX_PER_UNIT = 8           # 小窗里单个单元最多列几枚弹（只影响展示）
    MSG_ENABLE = True          # 往客户端“智能体输出”推汇总
    MSG_DEDUP_SEC = 30.0       # 同形态的汇总 30 秒内不重复
    GATE = None                # None = 不设门限，朝我就算

    def __init__(self, side_name="红方", *args, **kwargs):
        RuleAgentBase.__init__(self, side_name)
        self.side_cn = side_name
        self.agent_type = "MonitorAgent"
        self.agent_decision_time = self.DECISION_SEC
        self.now = 0.0
        self.cycle = 0
        self.lock = threading.RLock()
        self.server = None
        self.monitor = Monitor(self, gate=self.GATE)
        self._last_msg = {}
        self.snapshot = {"t": 0, "side": side_name, "started": False,
                         "groups": {}, "rows": [], "ms": 0, "own": 0}

    # ---------------------------------------------------------------- 生命周期
    def initial(self, situation):
        log.info("[监控] 战前，监控%s，小窗 127.0.0.1:%d", self.side_cn, PORT)
        with self.lock:
            self.monitor.setup(situation)
            self._build(0.0)
        if SnapServer.instance is None:
            self.server = SnapServer(self, PORT)
            self.server.start()
        else:
            self.server = SnapServer.instance
            self.server.agent = self
        return None

    def step(self, time_elapse, situation):
        """注意：平台把 step 里抛出的异常当**致命错误**（直接结束本局），
        所以整个函数体必须兜住——监控出问题不能连累对局。"""
        try:
            self.now = float(time_elapse or 0.0)
            self.cycle += 1
            with self.lock:
                self.monitor.step(situation, self.now)
                self._build(self.now)
        except Exception as e:
            log.error("[监控] 快照异常 %s", e, exc_info=True)
        try:
            self._notify()
        except Exception as e:
            log.warning("[监控] 消息栏异常 %s", e)
        try:
            if self.server is not None:
                self.server.publish()
        except Exception as e:
            log.warning("[监控] 推送异常 %s", e)
        return None

    def deduction_end(self):
        s = self.snapshot.get('groups', {}).get('all', [0, 0])
        log.info("[监控] 推演结束：周期 %d，最后一步被攻击 %d / %d 个单元",
                 self.cycle, s[0], s[1])

    # ---------------------------------------------------------------- 快照
    def _build(self, t):
        rows = self.monitor.rows()
        if self.MAX_PER_UNIT > 0:
            for r in rows:
                if len(r['ms']) > self.MAX_PER_UNIT:
                    r['ms'] = r['ms'][:self.MAX_PER_UNIT]
        groups = core.summarise(rows)
        self.snapshot = {
            "t": round(t), "side": self.side_cn, "started": t >= 1,
            "cycle": self.cycle,
            "ms": len(self.monitor.missiles()),      # 视野内敌方弹药总数
            "own": len(rows),
            "groups": {g: list(v) for g, v in groups.items()},
            "rows": rows,
            "cfg": {"gate": self.monitor.gate or None, "sec": self.DECISION_SEC},
        }

    # ---------------------------------------------------------------- 消息栏
    def _notify(self):
        if not self.MSG_ENABLE:
            return
        fn = getattr(self, 'agent_message_text', None)
        if not callable(fn):
            return
        g = self.snapshot.get('groups', {})
        air, sea, land = g.get('air', (0, 0)), g.get('sea', (0, 0)), g.get('land', (0, 0))
        if not (air[0] + sea[0] + land[0]):
            return
        hottest = None
        for r in self.snapshot.get('rows', []):
            for h in r['ms']:
                if h['tgo'] is None:
                    continue
                if hottest is None or h['tgo'] < hottest[1]:
                    hottest = (r['n'], h['tgo'], h['spd'], h['n'] or ('弹%s' % h['db']))
        text = "【被攻击】空%d/海%d/陆%d" % (air[0], sea[0], land[0])
        if hottest:
            text += "；最危险 %s ← %s %.0fkm/h 约%.0f秒" % (
                hottest[0], hottest[3], hottest[2], hottest[1])
        key = _template(text)
        last = self._last_msg.get(key)
        if last is not None and self.now - last < self.MSG_DEDUP_SEC:
            return
        self._last_msg[key] = self.now
        try:
            fn(text)
        except Exception as e:
            log.warning("[监控] 消息推送失败 %s", e)


def _template(text):
    """把数字换成 #，用于“同形态告警”去重。"""
    return ''.join('#' if ch.isdigit() else ch for ch in text)


class SnapServer:
    """aiohttp 跑在独立线程：/ws 推 {"type":"snap",…}；/ 给一行说明；/web/* 静态资源。
    另有一个 1 秒心跳线程：推演暂停 / 战前 step 不来时自己重建一次快照，
    小窗不会误判“没对局”。"""

    instance = None

    def __init__(self, agent, port):
        self.agent, self.port = agent, port
        self.loop = None
        self.clients = OrderedDict()
        self.last_pub = 0.0
        SnapServer.instance = self

    def start(self):
        threading.Thread(target=self._run, name="monitor-ws", daemon=True).start()
        threading.Thread(target=self._beat, name="monitor-beat", daemon=True).start()

    def _beat(self):
        while True:
            time.sleep(1.0)
            a = self.agent
            if a is None or not self.clients:
                continue
            if time.monotonic() - self.last_pub < 3:
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
        import asyncio
        from aiohttp import web

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        app = web.Application()
        app.router.add_get("/ws", self._ws)

        async def h_index(req):
            return web.Response(
                text="监控智能体在跑；小窗请双击 monitor-agent\\监控小窗.bat",
                content_type="text/plain", charset="utf-8")

        app.router.add_get("/", h_index)
        if WEB.exists():
            app.router.add_static("/web/", WEB, show_index=False)
        runner = web.AppRunner(app)
        self.loop.run_until_complete(runner.setup())
        try:
            self.loop.run_until_complete(
                web.TCPSite(runner, "127.0.0.1", self.port).start())
        except OSError as e:
            log.error("[监控] 端口 %d 打不开：%s", self.port, e)
            return
        log.info("[监控] WebSocket 已监听 127.0.0.1:%d", self.port)
        self.loop.run_forever()

    def publish(self):
        if self.loop is None or not self.clients:
            return
        self.last_pub = time.monotonic()
        text = json.dumps({"type": "snap", **self.agent.snapshot},
                          ensure_ascii=False, separators=(",", ":"))

        def put():
            for st in self.clients.values():
                st["text"] = text
                st["ev"].set()
        self.loop.call_soon_threadsafe(put)

    async def _sender(self, ws, st):
        import asyncio
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
        import asyncio
        from aiohttp import web, WSMsgType
        ws = web.WebSocketResponse(heartbeat=10, max_msg_size=8 * 1024 * 1024)
        await ws.prepare(req)
        st = {"text": json.dumps({"type": "snap", **self.agent.snapshot},
                                 ensure_ascii=False), "ev": asyncio.Event()}
        st["ev"].set()
        self.clients[ws] = st
        task = asyncio.ensure_future(self._sender(ws, st))
        try:
            async for msg in ws:      # 本智能体不执行指令，只吞消息/心跳
                if msg.type == WSMsgType.ERROR:
                    break
        finally:
            self.clients.pop(ws, None)
            task.cancel()
        return ws


def configure(args=None, side=None):
    """训练框架/本地直接选智能体时用。"""
    side = side or os.environ.get("LY_MONITOR_SIDE", "红方")
    return {side: {"Monitor": {"class": MonitorAgent, "unit": [],
                               "contact": [], "point": []}}}
