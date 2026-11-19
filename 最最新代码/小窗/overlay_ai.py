# -*- coding: utf-8 -*-
"""
灵弈客户端「智能体编辑」导入用的入口（灵弈小窗，跟网页版指挥台 console_ai.py 是两个项目）：添加智能体时选这个文件，类名 Agent。
智能体不自己打、不改任何东西，只给叠在客户端上的小窗（双击 agent/overlay/灵弈小窗.bat）供态势、执行 武器分配 / 油门 / 高度。
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from overlay.agent import OverlayAgent  # noqa: E402


class Agent(OverlayAgent):
    def __init__(self, side_name="蓝方", *args, **kwargs):
        super(Agent, self).__init__(side_name)
