# -*- coding: utf-8 -*-
"""灵弈客户端「智能体编辑」导入用的入口（灵弈小窗）。

用法：客户端里“添加智能体”选这个文件，类名 Agent。
它自己不打仗、不改任何东西，只给叠在客户端上的小窗供态势、执行
武器分配 / 油门 / 高度 / 防空值班。

⚠️ 这里必须在**任何重依赖之前**先落一行日志：
   平台用 importlib.import_module('overlay_ai') 加载本文件且不捕获异常
   （start_ai_apply.py），一旦 aiohttp / engine.LingYi / zmqlock 里任何一步
   抛错，进程直接退出、stdout 被隐藏，现场什么都看不到 —— 之前“小窗进程
   静默消失、查不到日志”就是这么来的。
   所以：boot.log 记每一步；crash.log 用 faulthandler 抓 C 层崩溃（.pyd 段错误）。
"""
import os
import sys
import time
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
_LOG_DIR = os.path.join(_HERE, 'overlay', 'logs')
BOOT_LOG = os.path.join(_LOG_DIR, 'boot.log')
CRASH_LOG = os.path.join(_LOG_DIR, 'crash.log')


def boot(tag, extra=''):
    """不依赖 logging 的裸写日志：哪怕 logging 还没配好也能留下痕迹。"""
    try:
        if not os.path.isdir(_LOG_DIR):
            os.makedirs(_LOG_DIR)
        with open(BOOT_LOG, 'a', encoding='utf-8') as f:
            f.write('%s [%-26s] pid=%s %s\n'
                    % (time.strftime('%Y-%m-%d %H:%M:%S'), tag, os.getpid(), extra))
    except Exception:
        pass


boot('overlay_ai: import start', 'python=%s' % sys.version.split()[0])

try:
    import faulthandler
    _crash = open(CRASH_LOG, 'a', encoding='utf-8')
    faulthandler.enable(file=_crash, all_threads=True)
    boot('faulthandler 已开')
except Exception as e:                                   # noqa: BLE001
    boot('faulthandler 开不起来', repr(e))

if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
boot('sys.path 就绪', 'path[0]=%s' % sys.path[0])

try:
    from overlay.agent import OverlayAgent          # noqa: E402
    boot('import overlay.agent 成功')
except BaseException:                               # noqa: BLE001
    boot('import overlay.agent 失败', '\n' + traceback.format_exc())
    raise


class Agent(OverlayAgent):
    """平台按 agent_class_name=Agent 构造本类。"""

    def __init__(self, side_name="蓝方", *args, **kwargs):
        boot('Agent.__init__ 开始', 'side=%s' % side_name)
        try:
            OverlayAgent.__init__(self, side_name)
        except BaseException:                       # noqa: BLE001
            boot('Agent.__init__ 失败', '\n' + traceback.format_exc())
            raise
        boot('Agent.__init__ 完成')
