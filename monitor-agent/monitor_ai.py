# -*- coding: utf-8 -*-
"""
监控智能体 —— 灵弈客户端「智能体调度 → 智能体编辑 → ＋」导入用的入口文件，类名 `Agent`。

它只做监控、不下发任何指令：每步枚举敌方弹药，判定我方哪些单元被指着，
报出弹型与弹速，并推给叠在客户端上的小窗（双击 monitor\\监控小窗.bat）。

可以和 Mission_all_red.py / Mission_tactics_red.py 同时导入、同时启动。
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from lymonitor.agent import MonitorAgent  # noqa: E402


class Agent(MonitorAgent):
    def __init__(self, side_name="红方", *args, **kwargs):
        super(Agent, self).__init__(side_name)
