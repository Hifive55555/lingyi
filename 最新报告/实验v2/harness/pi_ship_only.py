# -*- coding: utf-8 -*-
"""舰队自卫专项对局用的最小智能体（只装 Monitor + ShipClusterDefense）

用途：把红方的战前配置、空战、地导全部摘掉，只留“登陆船只集群自卫”这一条规则，
让蓝方的全谱反舰火力去打船团，从而**单独观测量**：
  `ship_defense_count`（拦截次数）、`red_loss_sea`（舰船损失）、拦截距离。

为什么需要它：整场对局里蓝方反舰弹从未进到舰空导弹包线（23 个臂的
`ship_defense_count` 全为 0），舰船自卫这条规则没有被执行到。把红方其它
兵力摘掉之后，蓝方的反舰火力才会全部倾泻到船团上。

注意：这不是一个新的战场，而是**同一份想定 + 只挂一个决策域**的专项对局，
因此它仍然满足“同一想定、同一蓝方、只改一个因素”的受控要求。

环境变量：
  PI_SHIP_LAYERED   0/1  覆盖 ShipClusterDefense.LAYERED（默认用类属性）
"""
import logging
import os

try:                                                     # 平台运行环境
    from engine.LingYi.entitys.agent_base import RuleAgentBase
    from engine.LingYi.BattlefieldMonitor import BattlefieldMonitor
    from engine.LingYi.ShipClusterDefense import ShipClusterDefense
except ImportError:                                      # 本地工作区
    from entitys.agent_base import RuleAgentBase
    from BattlefieldMonitor import BattlefieldMonitor
    from ShipClusterDefense import ShipClusterDefense


class Agent(RuleAgentBase):
    """只做一件事：监控 + 舰队自卫。"""

    def __init__(self, side_name, params=None):
        RuleAgentBase.__init__(self, side_name)
        lay = os.environ.get('PI_SHIP_LAYERED')
        if lay is not None and str(lay).strip() != '':
            ShipClusterDefense.LAYERED = bool(int(lay))
        self.monitor = BattlefieldMonitor(self)
        self.ship_defense = ShipClusterDefense(self, self.monitor)
        logging.info('%s:ShipOnly 启动（LAYERED=%s）' % (side_name, ShipClusterDefense.LAYERED))

    def _log(self, level, msg):
        """把模块日志直接写到 stdout（runner 的 .out），避免 root logger 级别把 INFO 丢掉。"""
        print('[%s] %s' % (level, msg), flush=True)

    def initial(self, situation):
        try:
            self.monitor.setup(situation)
            self.ship_defense.setup(situation)
        except Exception as e:
            logging.warning('ShipOnly initial 异常: %s' % e)

    def step(self, time_elapse, situation):
        try:
            self.monitor.ensure(situation)
            self.ship_defense.step(situation)
        except Exception as e:
            logging.warning('ShipOnly step 异常: %s' % e)

    def is_done(self, *a, **k):
        return False
