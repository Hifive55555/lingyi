# -*- coding: utf-8 -*-
"""监控智能体包。

- ``lymonitor.core``  : 纯几何判定（不依赖平台，可离线自测）
- ``lymonitor.agent`` : 平台侧智能体 + 小窗 WebSocket 服务

这里**不** import agent，否则在 Linux 上单跑 core 的自测会因为找不到
``engine.LingYi`` 而失败。需要 agent 时显式 ``from lymonitor.agent import MonitorAgent``。
"""
