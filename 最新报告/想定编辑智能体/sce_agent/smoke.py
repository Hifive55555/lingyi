# -*- coding: utf-8 -*-
"""推演冒烟：把生成的 .scen 真的跑起来（"确定能跑"的硬证据）。

做法：把一段 runner 脚本投到靶机，用**官方 python 框架**（``Deduction``）按正常
流程加载想定、推进 N 个决策步、取 ``BatResult``，再把结果 JSON 拉回来。

为什么要单独一步、不用 gRPC 直接跑
----------------------------------
* ``Deduction.reset()`` 走的是竞赛同款链路（管理服务 + DDS/ZMQ + 引擎），
  能验证"这份想定真的能被当成比赛想定加载并推进"，而不只是"引擎能读它"；
* ``reset`` 返回值本身就是判据：``1`` 成功 / ``-1`` 推演服务 / ``-2`` 无想定 /
  ``-3`` 无初始态势；
* ``BatResult.time`` 证明推演时钟真的在走（不是加载完就卡住）。

该 runner 必须在 **Session 1** 里跑（Qt 引擎要有窗口站），所以同样用计划任务投递。
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .engine import Target

RUNNER_PY = r'''# -*- coding: utf-8 -*-
"""灵弈想定冒烟 runner（由 sce_agent.smoke 投放到靶机执行）。

用法： python pi_sce_smoke.py <想定名> <推演步数> <结果json> [决策间隔秒]
"""
import sys, os, json, time, traceback

AI = r'D:\LingYi\intelligent\ai'
sys.path.insert(0, AI)
os.chdir(AI)

JOB = sys.argv[1]
with open(JOB, encoding='utf-8') as f:
    job = json.load(f)
SCEN = job['scenario']
STEPS = int(job.get('steps', 30))
OUT = job['out']
DI = int(job.get('decision_interval', 5))

res = {'scenario': SCEN, 'steps': 0, 'reset': None, 'error': '', 'ts': time.strftime('%Y-%m-%d %H:%M:%S')}
t0 = time.time()
try:
    from agent.config import LingYiConfig
    from engine.LingYi.entitys.deduce_RL import Deduction

    cfg = LingYiConfig.get_server_config({})
    gs = cfg['game_server']
    sim = gs['simulate']
    sim.update({
        'scenario': SCEN, 'scen_check': True, 'episodes': 1,
        'compression': 10001, 'need_compression': True,
        'decision_interval': DI, 'step_interval': 1,
        'training': False, 'testing': False, 'save_result': False,
        'load_scenario': True, 'main_client': True, 'clear_room': True,
        'save_situation_type': 0, 'simulate_complex': 4,
    })
    gs['server']['room_name'] = 'sce-smoke'
    gs['RL_agents'] = {'红方': {'agents': {}}, '蓝方': {'agents': {}}}
    cfg['rule_config'] = {}

    env = Deduction(cfg)
    r = env.reset(1)
    res['reset'] = int(r)
    if r == 1:
        n = 0
        while n < STEPS:
            env.step({})
            n += 1
            if env.is_done():
                break
        res['steps'] = n
        try:
            g = env.get_game_result()
            res.update(sim_time=float(g.time), result=int(g.bat_result),
                       error_side=str(g.error_side or ''), red_score=g.red_score,
                       blue_score=g.blue_score, round=g.bat_round)
        except Exception:
            res['result_error'] = traceback.format_exc()[-800:]
except Exception:
    res['error'] = traceback.format_exc()[-2000:]
res['elapsed'] = round(time.time() - t0, 1)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False))
'''

RUNNER_BAT = r'''@echo off
cd /d %(dir)s
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
%(py)s %(dir)s\pi_sce_smoke.py "%(job)s" >> %(dir)s\pi_sce_smoke.out 2>> %(dir)s\pi_sce_smoke.err
'''


@dataclass
class SmokeResult:
    ok: bool = False
    raw: Optional[Dict[str, Any]] = None
    elapsed: float = 0.0
    error: str = ""

    def to_dict(self):
        return {"ok": self.ok, "elapsed": self.elapsed, "error": self.error,
                "raw": self.raw or {}}


class SmokeRunner(object):
    """在靶机上按官方框架跑一局冒烟推演。"""

    def __init__(self, target: Optional[Target] = None, steps: int = 30,
                 decision_interval: int = 5, task: str = "PiSceSmoke"):
        self.t = target or Target()
        self.steps = steps
        self.di = decision_interval
        self.task = task
        self.dir = self.t.lingyi + "/intelligent/ai"
        self.py = self.dir + "/pi_sce_smoke.py"
        self.bat = self.dir + "/pi_sce_smoke.bat"
        self.out = self.dir + "/pi_sce_smoke.json"
        self.job = self.dir + "/pi_sce_smoke_job.json"
        self._deployed = False

    def deploy(self) -> None:
        tmp = "/tmp/_pi_sce_smoke.py"
        open(tmp, "w", encoding="utf-8").write(RUNNER_PY)
        self.t.put(tmp, self.py)
        # .bat 里只留纯 ASCII（路径 + job 文件名）：中文一律走 UTF-8 的 job.json，
        # 否则 cmd.exe 按 GBK 读 .bat 会把想定名弄成乱码（实测踩过）
        bat = RUNNER_BAT % dict(dir=self.dir.replace("/", "\\"),
                                py=(self.dir + "/../new_env/ray210/python.exe").replace("/", "\\"),
                                job=self.job.replace("/", "\\"))
        tmp2 = "/tmp/_pi_sce_smoke.bat"
        with open(tmp2, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(bat)
        self.t.put(tmp2, self.bat)
        self._deployed = True

    def run(self, scenario: str, timeout: float = 300.0) -> SmokeResult:
        if not self._deployed:
            self.deploy()
        job = {"scenario": scenario, "steps": self.steps,
               "decision_interval": self.di, "out": self.out}
        tmpj = "/tmp/_pi_sce_smoke_job.json"
        with open(tmpj, "w", encoding="utf-8") as f:
            json.dump(job, f, ensure_ascii=False)
        self.t.put(tmpj, self.job)
        self.t.ps("if (Test-Path '%s') { Remove-Item '%s' -Force }" % (self.out, self.out))
        self.t.register_task(self.task, self.bat.replace("/", "\\"), minutes=10)
        self.t.start_task(self.task)
        t0 = time.time()
        raw = None
        while time.time() - t0 < timeout:
            if self.t.file_size(self.out) > 0:
                time.sleep(0.5)
                txt = self.t.ps("[IO.File]::ReadAllText('%s', [Text.Encoding]::UTF8)" % self.out)
                try:
                    raw = json.loads(txt[txt.index("{"): txt.rindex("}") + 1])
                except Exception:
                    raw = None
                if raw:
                    break
            time.sleep(2)
        el = time.time() - t0
        if not raw:
            tail = self.t.ps("if (Test-Path '%s') { Get-Content '%s' -Tail 20 }"
                             % (self.dir + "/pi_sce_smoke.err", self.dir + "/pi_sce_smoke.err"))
            return SmokeResult(False, None, el, "冒烟超时/无结果。stderr 尾部：\n" + tail[-800:])
        ok = (raw.get("reset") == 1 and raw.get("steps", 0) > 0 and not raw.get("error_side"))
        return SmokeResult(ok, raw, el, raw.get("error", ""))
