# -*- coding: utf-8 -*-
"""把「放智能体 .py 的目录」挂进 sys.path —— 让 tools 里的脚本在两种布局下都能跑。

- 开发布局：智能体代码/ 与 tools/ 同级          -> 上一层就是
- 部署布局：<灵弈>/intelligent/ai/engine/LingYi/tools/
            而主智能体在 <灵弈>/intelligent/      -> 要逐级往上找

用法：
    from _agentpath import ensure
    ensure('Mission_all_red.py')
"""
import os
import sys


def find(fname, start, levels=6):
    d = os.path.abspath(start)
    for _ in range(levels):
        if os.path.exists(os.path.join(d, fname)):
            return d
        up = os.path.dirname(d)
        if up == d:
            break
        d = up
    return None


def ensure(fname, start=None):
    """找到含 fname 的目录并插到 sys.path 前面；返回该目录（找不到返回 None）。"""
    here = os.path.dirname(os.path.abspath(__file__))
    start = start or here
    found = find(fname, start)
    for d in (found, here):
        if d and d not in sys.path:
            sys.path.insert(0, d)
    return found
