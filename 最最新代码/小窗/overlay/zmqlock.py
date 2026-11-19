# -*- coding: utf-8 -*-
"""灵弈平台跟客户端只有一个 zmq REQ 口：下指令（req_client）、报运行次数（req_agent_times）、
请求配置参数（req_client_agent_config）都走它。REQ 必须一发一收，两个线程同时发就
"Operation cannot be accomplished in current state"，平台重连 2~4 秒，还弹
"智能体step函数执行次数发送错误: exception class must be a subclass of BaseException"（平台自己的 bug）。
灵弈小窗的指令在工作线程里随时下，跟平台 step 线程撞车 -> 给这个口的所有收发加一把全局锁排队。"""
import functools
import logging
import threading

log = logging.getLogger("灵弈小窗")
ZLOCK = threading.RLock()


def install():
    try:
        from engine.LingYi.entitys.gameenvs import zmq_client
    except Exception as e:
        log.warning(f"[zmq 锁] 没装上：{e}")
        return False
    cls = zmq_client.Client_connect
    if getattr(cls, "_zlock", False):
        return True
    n = 0
    for name in list(vars(cls)):
        if not (name.startswith("req_") or name == "send_message_to_client"):
            continue
        fn = vars(cls)[name]
        if not callable(fn):
            continue

        def wrap(fn=fn):
            @functools.wraps(fn)
            def call(self, *a, **k):
                with ZLOCK:
                    return fn(self, *a, **k)
            return call
        setattr(cls, name, wrap())
        n += 1
    cls._zlock = True
    log.info(f"[zmq 锁] 已装上 {n} 个收发口")
    return True
