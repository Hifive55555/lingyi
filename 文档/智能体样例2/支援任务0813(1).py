import logging

#from PyQt5.QtGui.QRawFont import supportsCharacter#
from engine.LingYi.entitys.player import Player
# from agent.rule_agent.air_combat.calculate_threat_level_of_the_target import ThreatEvaluator
# from agent.rule_agent.air_combat.calculate_weapon_attack_air_rate import calculate_possibility
import numpy as np
from engine.LingYi.entitys.global_util import *


# from ...entitys.agent_base import *

class Agent(Player):
    def __init__(self, side_name, params):
        Player.__init__(self, side_name)
        logging.info('%s:%s play game' % (side_name, self.__class__.__name__))

    def initial(self, situation):
        situation_data = situation[0] if isinstance(situation[0], list) else []
        support_1_name='支援1南高'
        support_2_name='支援2航母撤退'
        support_3_name='支援3坦克任务'
        support_4_name='支援4S-400'
        support_5_name='支援5陆地目标'
        support_6_name='支援6KN-01'
        support_7_name='支援7新浦级'
        support_8_name='支援8S-300'
        support_1_points=[(19.241480,-91.457580,'南高1'),(19.015490,-92.375720,'南高2')]
        support_2_points=[(16.720680,-81.489180,'航母撤退1'),(19.015490,-80.015450,'航母撤退2')]
        support_3_points=[(22.441750,-84.925290,'坦克任务1'),(21.214380,-86.013670,'坦克任务2')]
        support_4_points=[(11.472310,-84.576900,'S-400 1'),(12.005040,-84.576530,'S-400 2'),(11.668030,-84.056030,'S-400 3')]
        support_5_points=[(14.239490,-87.193890,'陆地目标1'),(13.560970,-86.412500,'陆地目标2')]
        support_6_points=[(20.739740,-86.880250,'KN-01 1'),(20.900250,-90.315780,'KN-01 2')]
        support_7_points=[(18.169070,-91.457580,'新浦级1'),(18.165850,-87.214300,'新浦级2')]
        support_8_points=[(18.445390,-77.577620,'S-300 1'),(18.438680,-77.366250,'S-300 2'),(11.668030,-77.458500,'S-300 3')]
        self.create_support_mission(name=support_1_name, point_list=support_1_points)
        self.create_support_mission(name=support_2_name, point_list=support_2_points)
        self.create_support_mission(name=support_3_name, point_list=support_3_points)
        self.create_support_mission(name=support_4_name, point_list=support_4_points)
        self.create_support_mission(name=support_5_name, point_list=support_5_points)
        self.create_support_mission(name=support_6_name, point_list=support_6_points)
        self.create_support_mission(name=support_7_name, point_list=support_7_points)
        self.create_support_mission(name=support_8_name, point_list=support_8_points)

        pass

    def step(self, time_elapse, situation):
        pass

    def deduction_end(self):
        # agent结束后自动被调用函数， 可保存模型，比如记录本局策略后的得分等
        pass

    def is_done(self):
        # agent主动结束本局推演，比如一定胜利或失败后
        # 只能训练时调用此函数，比赛对战时此函数不可用
        pass


