import logging
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
        #巡逻任务参数
        patrol_1_name='巡逻1阻止蓝方任务'
        patrol_2_name='巡逻2四代机'
        patrol_3_name='巡逻3O国飞机'
        patrol_4_name='巡逻4轰炸机准备'
        patrol_5_name='巡逻5三代机'
        patrol_6_name='巡逻6苍龙级'
        patrol_7_name='巡逻7岛山级'
        patrol_8_name='巡逻8保护航母'
        patrol_9_name='巡逻9左侧轰炸机准备'
        patrol_1_points = [(20.824400,-90.177800,'阻止蓝方任务1'), (20.824400,-89.210800,'阻止蓝方任务2'),
                           (20.380600,-89.210800,'阻止蓝方任务3'),(20.380600,-90.177800,'阻止蓝方任务4')]
        patrol_2_points =[(16.831803,-91.651552,'四代机1'),(18.403182,-90.551782,'四代机2'),
                          (18.164080,-90.171732,'四代机3'),(16.565356,-91.305737,'四代机4')]
        patrol_3_points = [(20.200500,-84.430600,'O国飞机1'),(20.200500,-83.201100,'O国飞机2'),
                           (19.551900,-83.201100,'O国飞机3'),(19.511900,-84.430600,'O国飞机4')]
        patrol_4_points = [(21.428800,-80.151200,'轰炸机准备1'),(21.428800,-79.393800,'轰炸机准备2'),
                           (20.701700,-79.393800,'轰炸机准备3'),(20.701700,-80.151200,'轰炸机准备4')]
        patrol_5_points = [(16.831803,-91.651552, '三代机1'), (18.403182,-90.551782, '三代机2'),
                           (18.164080,-90.171732, '三代机3'), (16.565356,-91.305737, '三代机4')]
        patrol_6_points = [(18.936800,-82.127300,'苍龙级1'),(18.936800,-81.774700,'苍龙级2'),
                           (18.609500,-81.774700,'苍龙级3'),(18.609500,-82.127300,'苍龙级4')]
        patrol_7_points = [(24.593700,-85.942200,'岛山级1'),(24.593700,-85.779600,'岛山级2'),
                           (24.424700,-85.779600,'岛山级3'),(24.424700,-85.942200,'岛山级4')]
        patrol_8_points = [(18.136800,-82.978100,'保护航母1'),(18.136800,-81.937800,'保护航母2'),
                           (17.522600,-81.937800,'保护航母3'),(17.522600,-82.978100,'保护航母4')]
        patrol_9_points = [(18.860700,-87.529500,'左侧轰炸机准备1'),(18.860700,-86.823300,'左侧轰炸机准备2'),
                           (18.313300,-86.823300,'左侧轰炸机准备3'),(18.313300,-87.529500,'左侧轰炸机准备4')]
        #生成巡逻任务
        self.create_patrol_mission(name=patrol_1_name, mission_type=MissionPatrolType.AIR,
                                   point_list=patrol_1_points)
        self.create_patrol_mission(name=patrol_2_name,  mission_type=MissionPatrolType.AIR,
                                   point_list=patrol_2_points)
        self.create_patrol_mission(name=patrol_3_name,  mission_type=MissionPatrolType.AIR,
                                   point_list=patrol_3_points)
        self.create_patrol_mission(name=patrol_4_name,  mission_type=MissionPatrolType.AIR,
                                   point_list=patrol_4_points)
        self.create_patrol_mission(name=patrol_5_name,  mission_type=MissionPatrolType.AIR,
                                   point_list=patrol_5_points)
        self.create_patrol_mission(name=patrol_6_name,  mission_type=MissionPatrolType.ANTI_SHIP,
                                   point_list=patrol_6_points)
        self.create_patrol_mission(name=patrol_7_name,  mission_type=MissionPatrolType.ANTI_SHIP,
                                   point_list=patrol_7_points)
        self.create_patrol_mission(name=patrol_8_name,  mission_type=MissionPatrolType.AIR,
                                   point_list=patrol_8_points)
        self.create_patrol_mission(name=patrol_9_name,  mission_type=MissionPatrolType.AIR,
                                   point_list=patrol_9_points)



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




