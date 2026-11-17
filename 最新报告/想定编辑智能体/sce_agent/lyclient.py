# -*- coding: utf-8 -*-
"""灵弈引擎 gRPC 客户端（executeLua 通道）。

两种引擎形态（详见 docs/想定编辑智能体设计文档.md §2）：
  * 明文 h2c  —— 由 python 框架 (GameConnectLocal) 或本工具的 engine_host 拉起
  * TLS       —— 由客户端 APlatform.exe 拉起，自签证书 CN=MyCA

用法：
    with LuaClient('10.42.97.205', 21001) as c:
        print(c.lua('GetBuildNumber()'))
"""
from __future__ import annotations

import os
import re
import sys
import threading
import time

import grpc

_HERE = os.path.dirname(os.path.abspath(__file__))
_GEN = os.path.join(_HERE, 'gen')
if _GEN not in sys.path:
    sys.path.insert(0, _GEN)

import ServerInterface_pb2 as pb2              # noqa: E402
import ServerInterface_pb2_grpc as pb2_grpc   # noqa: E402


class LuaError(RuntimeError):
    """引擎返回 code != 0（LuaError / RPC 异常）。"""


class LuaClient(object):
    def __init__(self, host='127.0.0.1', port=21001, timeout=60.0,
                 tls=False, root_cert=None, target_name='MyCA', trace=False):
        self.addr = '%s:%d' % (host, port)
        self.timeout = timeout
        self.trace = trace
        opts = [('grpc.max_receive_message_length', 256 * 1024 * 1024),
                ('grpc.max_send_message_length', 256 * 1024 * 1024),
                # 本机若配了 http_proxy，grpc 会当成 CONNECT 代理 -> 必须显式关掉
                ('grpc.enable_http_proxy', 0)]
        if tls:
            cred = grpc.ssl_channel_credentials(root_certificates=root_cert)
            opts.append(('grpc.ssl_target_name_override', target_name))
            self.ch = grpc.secure_channel(self.addr, cred, options=opts)
        else:
            self.ch = grpc.insecure_channel(self.addr, options=opts)
        self.stub = pb2_grpc.SimRpcStub(self.ch)
        self.history = []

    # ---------------------------------------------------------------- 通道
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.ch.close()

    def ping(self, timeout=5.0):
        try:
            r = self.stub.executeLua(pb2.RequestExecuteLua(script='GetBuildNumber()'),
                                     timeout=timeout)
            return r.code == 0, r.result.decode('utf-8', 'replace')
        except grpc.RpcError as e:
            return False, '%s: %s' % (type(e).__name__, e.details() if hasattr(e, 'details') else e)

    # ---------------------------------------------------------------- Lua
    def lua(self, script, timeout=None, raise_on_error=True):
        """执行一段 Lua，返回 (code, result_str)。"""
        t0 = time.time()
        try:
            r = self.stub.executeLua(pb2.RequestExecuteLua(script=script),
                                     timeout=timeout or self.timeout)
            code = int(r.code)
            res = r.result.decode('utf-8', 'replace')
        except grpc.RpcError as e:
            raise LuaError('gRPC 失败 @%s : %s' % (self.addr, e))
        dt = time.time() - t0
        self.history.append(dict(t=time.time(), dt=dt, script=script, code=code, result=res))
        if self.trace:
            sys.stderr.write('[lua %.2fs code=%d] %s\n  -> %s\n'
                             % (dt, code, script.strip()[:200], res.strip()[:400]))
        if code != 0 and raise_on_error:
            raise LuaError('Lua 执行失败 (code=%d) @%s\n  script: %s\n  result: %s'
                           % (code, self.addr, script.strip()[:800], res.strip()[:800]))
        return code, res

    def lua_ok(self, script, timeout=None):
        """执行并返回 result 字符串（失败抛异常）。"""
        return self.lua(script, timeout=timeout)[1]

    def multi(self, scripts, timeout=None):
        """顺序执行多条 Lua，返回各自 result 列表。"""
        return [self.lua_ok(s, timeout=timeout) for s in scripts]

    # ------------------------------------------------------- 命名 RPC（带类型）
    # 说明（实测）：executeLua 只会把 Lua 侧 SET_RUNRESULT 的**字符串**带回来，
    # 原生返回值（int/bool）和 Lua 表都会丢；因此凡是要拿结构化数据的地方
    # 一律走下面这些命名 RPC。
    def query_db(self, kind: str, dbid: int):
        """queryDatabase：查 DB 里 (类型, dbid) 的真实类名。返回 (ok, class_or_err)。"""
        try:
            r = self.stub.queryDatabase(
                pb2.RequestQueryDatabase(objectType=kind, dbid=int(dbid)),
                timeout=self.timeout)
        except grpc.RpcError as e:
            return False, 'gRPC %s' % e
        txt = r.result.decode('utf-8', 'replace')
        if int(r.code) != 0:
            return False, txt
        m = re.search(r"class\s*=\s*'([^']*)'", txt)
        return True, (m.group(1) if m else '')

    def scenario_list(self):
        """getScenarioList：想定目录里的文件列表（JSON）。"""
        r = self.stub.getScenarioList(pb2.RequestGetScenarioList(), timeout=self.timeout)
        return int(r.code), r.result.decode('utf-8', 'replace')

    def scenario_content(self, name: str):
        """getScenarioContent：返回 .scen 解压后的 <Scenario> XML。"""
        r = self.stub.getScenarioContent(pb2.RequestGetScenarioContent(scenName=name),
                                         timeout=self.timeout)
        return int(r.code), r.result.decode('utf-8', 'replace')

    def scenario_basic_info(self, name: str):
        """getScenarioBasicInfo：外层未压缩信息（JSON）。"""
        r = self.stub.getScenarioBasicInfo(pb2.RequestGetScenarioBasicInfo(scenName=name),
                                           timeout=self.timeout)
        return int(r.code), r.result.decode('utf-8', 'replace')

    def load_scenario(self, name: str, scheme: int = 0):
        """loadScenario：按名加载想定（比 Lua 的 LoadScenario 安全，不炸引擎）。"""
        r = self.stub.loadScenario(pb2.RequestLoadScenario(scenName=name, loadScheme=scheme),
                                   timeout=self.timeout)
        return int(r.code), r.result.decode('utf-8', 'replace')

    def get_elevation(self, lat: float, lon: float):
        """getElevation：地形高程（米，>0 为陆地，<=0 为水面）。"""
        try:
            r = self.stub.getElevation(
                pb2.RequestGetElevation(latitude="%.6f" % lat, longitude="%.6f" % lon),
                timeout=self.timeout)
        except grpc.RpcError as e:
            return None, str(e)
        txt = r.result.decode('utf-8', 'replace').strip()
        try:
            return float(txt), txt
        except ValueError:
            return None, txt

    def init_situation(self):
        """getInitSituation：初始帧态势（streaming Reply，JSON）。"""
        chunks = []
        for rep in self.stub.getInitSituation(pb2.RequestEmpty(), timeout=self.timeout):
            if int(rep.code) != 0:
                raise LuaError('getInitSituation 失败：%s' % rep.result.decode('utf-8', 'replace'))
            chunks.append(rep.result)
        return b''.join(chunks).decode('utf-8', 'replace')


# ------------------------------------------------------------------ 解析辅助
def parse_mission_guid(res: str) -> str | None:
    """AddMission 返回 `mission {guid = 'X', name = 'Y'}`。"""
    m = re.search(r"guid\s*=\s*'([^']+)'", res or '')
    return m.group(1) if m else None


def parse_sides(res: str) -> dict:
    """GetSides() 返回 `"guid","名称";"guid2","名称2"` -> {名称: guid}。"""
    out = {}
    for part in (res or '').split(';'):
        m = re.match(r'\s*"([^"]*)"\s*,\s*"([^"]*)"\s*$', part.strip())
        if m:
            out[m.group(2)] = m.group(1)
    return out


def parse_rp(res: str) -> dict:
    """AddReferencePoint 返回 `{ name = 'RP-1', ..., guid = 'X', ... }`。"""
    d = dict(re.findall(r"(\w+)\s*=\s*'([^']*)'", res or ''))
    return d


def parse_unit_guid(res: str) -> str:
    """AddUnit 返回纯 GUID（count>1 时是逗号分隔的多个）。"""
    s = (res or '').strip().strip('"')
    return s
