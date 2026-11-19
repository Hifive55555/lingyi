# -*- coding: utf-8 -*-
"""把「放智能体 .py 的目录」挂进 sys.path —— 让 tools 里的脚本在两种布局下都能跑。

- 开发布局：智能体代码/ 与 tools/ 同级          -> 上一层就是
- 部署布局（统一后）：智能体入口 .py 都装在 <灵弈>/intelligent/ai/agent/
            而 tools 在 <灵弈>/intelligent/ai/engine/LingYi/tools/  -> 要靠下面的附加候选找到

用法：
    from _agentpath import ensure
    ensure('Mission_all_red.py')
"""
import os
import sys


def find(fname, start, levels=6):
    """先按“逐级往上”找；再补几个已知落点。

    统一布局后智能体入口在 ai\agent\，它不在 tools 的祖先链上，所以要额外看：
        <某级>/agent/            （ai\agent）
        <某级>/ai/agent/         （intelligent\ai\agent）
    """
    d = os.path.abspath(start)
    chain = []
    for _ in range(levels):
        chain.append(d)
        up = os.path.dirname(d)
        if up == d:
            break
        d = up
    cands = []
    for base in chain:
        cands.append(base)
        cands.append(os.path.join(base, 'agent'))
        cands.append(os.path.join(base, 'ai', 'agent'))
    for c in cands:
        if os.path.exists(os.path.join(c, fname)):
            return c
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
