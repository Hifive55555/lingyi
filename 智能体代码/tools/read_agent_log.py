# -*- coding: utf-8 -*-
"""
把这一局智能体的关键日志打出来（BOL / 报错 / 指令被拒）。

平台把智能体的日志写在：
    <安装目录>\\intelligent\\ai\\config\\<智能体名>#<序号>\\log\\command_delay.log

用法：
    python tools/read_agent_log.py                # 读默认路径
    python tools/read_agent_log.py <日志路径>      # 或指定文件
"""
import glob
import io
import os
import sys

CONFIG_GLOB = r'D:\LingYi\intelligent\ai\config\*\log\command_delay.log'
KEYS = ('BOL', 'AGENT_BUILD', '指令执行失败', 'ERROR', '未匹配',
        '未找到', '超出长度', '放弃', '起终点相同')


def latest():
    """优先取最近 12 小时内改过的日志，否则取最新的那个。"""
    hits = glob.glob(CONFIG_GLOB)
    if not hits:
        return None
    import time as _t
    now = _t.time()
    recent = [p for p in hits if now - os.path.getmtime(p) < 12 * 3600]
    pool = recent or hits
    return max(pool, key=lambda p: (os.path.getmtime(p), os.path.getsize(p)))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path or not os.path.exists(path):
        alt = latest()
        if alt:
            path = alt
    if not path or not os.path.exists(path):
        print('找不到日志文件，可用参数指定：python tools/read_agent_log.py <command_delay.log>')
        return 1

    print('日志：%s' % path)
    others = [p for p in glob.glob(CONFIG_GLOB) if p != path]
    if others:
        print('（其它智能体日志：%s；要指定请把路径作为第一个参数）'
              % '、'.join(os.path.basename(os.path.dirname(os.path.dirname(p)))
                         for p in others))
    n = 0
    for line in io.open(path, encoding='utf-8', errors='replace'):
        if any(k in line for k in KEYS):
            n += 1
            print(line.rstrip()[:400])
    print('—— 命中 %d 行' % n)
    return 0


if __name__ == '__main__':
    sys.exit(main())
