# -*- coding:utf-8 -*-
# Author: MouQingPing/WuRuiZhuo

"""
任务设置智能体
包括
巡逻任务
支援任务
打击任务

"""

from engine.LingYi.entitys.global_util import *
from engine.LingYi.entitys.player import Player
import time


class Agent(Player):
    def __init__(self, side_name, params):
        Player.__init__(self, side_name)
        super(Agent, self).__init__(side_name)

    def initial(self, situation):
        """
        初始化函数，每局推演开始前被调用. 可用于任务创建、设置，条令设置，变量初始化等
        :param situation: tuple: units, contacts
        :return:
        """
        situation_data = situation[0] if isinstance(situation[0], dict) else []

        self.flag1 = 0
        self.flag2 = 0
        self.flag3 = 0

        # ------------------------巡逻任务--------------------------

        # 海上中部
        time.sleep(1.0)
        self.create_patrol_mission(name='海上中部', mission_type=MissionPatrolType.AIR,
                                   point_list=[(22.0, -86.4), (22.5, -83.2), (20.0, -83.2), (19.5, -86.4)])
        Sea_patrol = self.get_mission_by_name('海上中部')
        unit_name_list = ['EF2000 型 #2', 'EF2000 型 #3', 'EF2000 型 #4', 'EF2000 型 #5','JAS 39D型 #1', 'JAS 39D型 #2'] 
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='海上中部', unit_list=unit_guid_list[0:10])
        self.assign_units_to_mission(mission_name='海上中部', unit_list=unit_guid_list[10:])
        self.add_prosecution_zone(mission_name='海上中部', point_list=[(21.6, -94.13), (21.6, -90.5), (19.0, -90.5), (19.0, -94.13)])
        Sea_patrol.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  2机编队，常用于战斗机
        Sea_patrol.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Sea_patrol.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Sea_patrol.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Sea_patrol.station_count(0)  # 为保持阵位的数量 0
        Sea_patrol.set_one_third_rule(True)  # 三分之一规则 不开启
        Sea_patrol.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Sea_patrol.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Sea_patrol.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Sea_patrol.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Sea_patrol.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Sea_patrol.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Sea_patrol.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Sea_patrol.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Sea_patrol.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Sea_patrol.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里


        # 最右边机场附近巡逻
        time.sleep(1.0)
        self.create_patrol_mission(name='海上东部', mission_type=MissionPatrolType.AIR,
                                   point_list=[(22.0, -82.5), (22.0, -80.8), (20.5, -80.8), (20.5, -82.5)])
        EF2000_patrol = self.get_mission_by_name('海上东部')
        unit_name_list = ['EF2000 型 #1','米格-29K型 #1', '米格-29K型 #2', '米格-29K型 #3', '米格-29K型 #4']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='海上东部', unit_list=unit_guid_list)
        EF2000_patrol.patrol_flight_size(FlightSize.One)  # 设置任务编队规模单机编队
        EF2000_patrol.set_flightStoengage('all')  # 敌方对抗的飞机数量 所有飞机编队出动
        EF2000_patrol.set_wingmanEngageDistance(15)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        EF2000_patrol.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        EF2000_patrol.station_count(0)  # 为保持阵位的数量 0
        EF2000_patrol.set_one_third_rule(True)  # 三分之一规则 不开启
        EF2000_patrol.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        EF2000_patrol.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        EF2000_patrol.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射  不开启
        EF2000_patrol.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 军用
        EF2000_patrol.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 军用
        EF2000_patrol.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        EF2000_patrol.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # EF2000_patrol.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # EF2000_patrol.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # EF2000_patrol.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        # 海上右下苍龙反潜
        time.sleep(1.0)        
        self.create_patrol_mission(name='海上苍龙反潜', mission_type=MissionPatrolType.ANTI_SUBMARINE,
                                   point_list=[(19.5, -82.4), (19.5, -81.5), (18.4, -81.5), (18.4, -82.4)])
        ASW_Ka27_patrol = self.get_mission_by_name('海上苍龙反潜')
        unit_name_list = ['卡-27PL型 #1','卡-27PL型 #2', '卡-27PL型 #3', '图-142MZ型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='海上苍龙反潜', unit_list=unit_guid_list)
        ASW_Ka27_patrol.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队
        ASW_Ka27_patrol.set_flightStoengage('all')  # 敌方对抗的飞机数量  所有飞机编队出动
        ASW_Ka27_patrol.set_wingmanEngageDistance(30) #飞机设置  僚机可以在xx范围内侦察/交战   海里
        ASW_Ka27_patrol.patrol_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞 否
        ASW_Ka27_patrol.station_count(0)  # 为保持阵位的数量 0
        ASW_Ka27_patrol.set_one_third_rule(False)  # 三分之一规则 不开启
        ASW_Ka27_patrol.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        ASW_Ka27_patrol.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        ASW_Ka27_patrol.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        ASW_Ka27_patrol.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        ASW_Ka27_patrol.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        ASW_Ka27_patrol.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        ASW_Ka27_patrol.set_PatrolMovementStyle(1)  #巡逻任务 动作风格设置 可重复循环

        
        time.sleep(1.0)        
        self.create_patrol_mission(name='坦克掩护', mission_type=MissionPatrolType.ANTI_SUBMARINE,
        point_list=[(17.4,-94.6),(17.4,-94.2),(17.1,-94.2),(17.1,-94.6)])
        tank_protect = self.get_mission_by_name('坦克掩护')
        unit_name_list = ['米格-23ML“鞭挞者”战斗机  #1', '米格-23ML“鞭挞者”战斗机  #2', '米格-23ML“鞭挞者”战斗机  #3', 
        '米格-29型 #1', '米格-29型 #2', '米格-29型 #3','米格-29型 #4', '米格-29型 #5','米格-29型 #6',]
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='坦克掩护', unit_list=unit_guid_list)
        self.add_prosecution_zone(mission_name='坦克掩护', point_list=[(17.80, -94.90), (17.80, -93.80), (16.40, -93.80), (16.40, -94.90)])
        tank_protect.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队
        tank_protect.set_flightStoengage('all')  # 敌方对抗的飞机数量  所有飞机编队出动
        tank_protect.set_wingmanEngageDistance(30) #飞机设置  僚机可以在xx范围内侦察/交战   海里
        tank_protect.patrol_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞 否
        tank_protect.station_count(0)  # 为保持阵位的数量 0
        tank_protect.set_one_third_rule(True)  # 三分之一规则 不开启
        tank_protect.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        tank_protect.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        tank_protect.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        tank_protect.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 军用
        tank_protect.patrol_set_throttle_station(Throttle.Cruise)  # 设置任务的阵位油门 军用
        tank_protect.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        tank_protect.patrol_set_transitAltitude(13000.0)
        tank_protect.patrol_set_stationAltitude(8000.0)
        tank_protect.set_PatrolMovementStyle(1) #巡逻任务 动作风格设置 可重复循环

        time.sleep(1.0)        
        self.create_patrol_mission(name='坦克打击', mission_type=MissionPatrolType.ANTI_SUBMARINE,
        point_list=[(16.8,-94.55),(16.8,-94.25),(16.5,-94.25),(16.5,-94.55)])
        tank_attack = self.get_mission_by_name('坦克打击')
        unit_name_list = ['米格-21bis型 #1', '米格-21bis型 #2']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='坦克打击', unit_list=unit_guid_list)
        self.add_prosecution_zone(mission_name='坦克打击', point_list=[(17.80, -94.90), (17.80, -93.80), (16.40, -93.80), (16.40, -94.90)])
        tank_attack.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队
        tank_attack.set_flightStoengage('all')  # 敌方对抗的飞机数量  所有飞机编队出动
        tank_attack.set_wingmanEngageDistance(30) #飞机设置  僚机可以在xx范围内侦察/交战   海里
        tank_attack.patrol_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞 否
        tank_attack.station_count(0)  # 为保持阵位的数量 0
        tank_attack.set_one_third_rule(False)  # 三分之一规则 不开启
        tank_attack.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        tank_attack.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        tank_attack.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        tank_attack.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 军用
        tank_attack.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 军用
        tank_attack.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        tank_attack.set_stationTerrainFollowingAircraft(True)
        tank_attack.patrol_set_transitAltitude(13000.0)
        tank_attack.set_PatrolMovementStyle(1) #巡逻任务 动作风格设置 可重复循环


        # C国西
        time.sleep(1.0)      
        self.create_patrol_mission(name='C国西', mission_type=MissionPatrolType.AIR,
        point_list=[(17.20, -93.00), (17.20, -92.70), (16.90, -92.70), (16.90, -93.00)])
        C_west = self.get_mission_by_name('C国西')
        unit_name_list = [
        '米格-31BM型“猎狐”战斗机#1', '米格-31BM型“猎狐”战斗机#2','苏-33型 #1', '苏-33型 #2', '苏-33型 #3']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='C国西', unit_list=unit_guid_list)
        self.add_prosecution_zone(mission_name='C国西', point_list=[(18.20, -93.80), (18.20, -92.70), (16.10, -92.70), (16.10, -93.80)])
        C_west.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队，常用于战斗机
        C_west.set_flightStoengage('all')  # 敌方对抗的飞机数量 所有飞机编队出动
        C_west.set_wingmanEngageDistance(5)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        C_west.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        C_west.station_count(0)  # 为保持阵位的数量 0
        C_west.set_one_third_rule(False)  # 三分之一规则 不开启
        C_west.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        C_west.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        C_west.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射  不开启
        C_west.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 军用
        C_west.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 军用
        C_west.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        C_west.patrol_set_transitAltitude(13000.0)
        C_west.patrol_set_stationAltitude(8000.0)
             
        # T50隐蔽巡逻
        time.sleep(1.0)        
        self.create_patrol_mission(name='T50', mission_type=MissionPatrolType.AIR,
                                   point_list=[(21.3, -90.34), (21.3, -89.84), (20.3, -89.84), (20.3, -90.34)])
        T50_hide = self.get_mission_by_name('T50')
        unit_name_list = ['T-50型 #1', 'T-50型 #2','T-50型 #3', 'T-50型 #4',
        '苏-30SM“侧卫G”战斗机 #1', '苏-30SM“侧卫G”战斗机 #2', '苏-30SM“侧卫G”战斗机 #3', '苏-30SM“侧卫G”战斗机 #4',]
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='T50', unit_list=unit_guid_list)
        self.add_prosecution_zone(mission_name='T50', point_list=[(23.10,-93.20), (23.10,-89.70), (20.25,-89.70), (20.25,-93.20)])
        T50_hide.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队，常用于战斗机
        T50_hide.set_flightStoengage('all')  # 敌方对抗的飞机数量 所有飞机编队出动
        T50_hide.set_wingmanEngageDistance(10)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        T50_hide.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        T50_hide.station_count(0)  # 为保持阵位的数量 0
        T50_hide.set_one_third_rule(False)  # 三分之一规则 不开启
        T50_hide.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        T50_hide.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        T50_hide.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 开启
        T50_hide.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        T50_hide.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        T50_hide.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        T50_hide.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        ''''''
        time.sleep(1.0)        
        self.create_patrol_mission(name='世宗探测', mission_type=MissionPatrolType.AIR,
                                   point_list=[(18.4,-90.7), (18.4, -90.3), (18.0, -90.3), (18.0, -90.7)])
        ShiZong_detect = self.get_mission_by_name('世宗探测')
        unit_name_list = ['图-22MR 型 #2']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='世宗探测', unit_list=unit_guid_list)
        ShiZong_detect.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队，常用于战斗机
        ShiZong_detect.set_flightStoengage('all')  # 敌方对抗的飞机数量 所有飞机编队出动
        ShiZong_detect.set_wingmanEngageDistance(25)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        ShiZong_detect.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        ShiZong_detect.station_count(0)  # 为保持阵位的数量 0
        ShiZong_detect.set_one_third_rule(False)  # 三分之一规则 不开启
        ShiZong_detect.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        ShiZong_detect.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        ShiZong_detect.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 开启
        ShiZong_detect.patrol_set_throttle_transit(Throttle.Flank)  # 设置任务的出航油门 全速
        ShiZong_detect.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        ShiZong_detect.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        ShiZong_detect.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888

        time.sleep(1.0)
        self.create_patrol_mission(name='C国北海', mission_type=MissionPatrolType.AIR,
                                   point_list=[(21.6, -94.13), (21.6, -87), (19.0, -87), (19.0, -94.13)])
        C_north_sea = self.get_mission_by_name('C国北海')
        unit_name_list = [ '苏-35S型 #1', '苏-35S型 #2', '苏-35S型 #3',
        '地空导弹营(KN-06型地空导弹 [Pongae-5型防空导弹])','地地导弹营(KN-01型地对舰导弹)',
        'Su-75 Checkmate 战斗机 #1', 'Su-75 Checkmate 战斗机 #2', 'Su-75 Checkmate 战斗机 #3',
        '米格-35型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='C国北海', unit_list=unit_guid_list[0:10])
        self.assign_units_to_mission(mission_name='C国北海', unit_list=unit_guid_list[10:])
        C_north_sea.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队，常用于战斗机
        C_north_sea.set_flightStoengage('all')  # 敌方对抗的飞机数量 所有飞机编队出动
        C_north_sea.set_wingmanEngageDistance(10)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        C_north_sea.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        C_north_sea.station_count(0)  # 为保持阵位的数量 0
        C_north_sea.set_one_third_rule(False)  # 三分之一规则 不开启
        C_north_sea.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        C_north_sea.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        C_north_sea.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 开启
        C_north_sea.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        C_north_sea.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        C_north_sea.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        C_north_sea.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == '地空导弹营(KN-06型地空导弹 [Pongae-5型防空导弹])':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.Yes)
                set_unit.doctrine_engage_opportunity_targets(EngageWithContactTarget.Yes_AnyTarget)
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == '地地导弹营(KN-01型地对舰导弹)':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.Yes)
                set_unit.doctrine_engage_opportunity_targets(EngageWithContactTarget.Yes_AnyTarget)

        # 海上预警机
        time.sleep(1.0)   
        self.create_patrol_mission(name='海上预警', mission_type=MissionPatrolType.AIR,
                                   point_list=[(19.4, -83.0), (19.4, -82.7), (19.1, -82.7), (19.1, -83.0)])
        S_100B_patrol = self.get_mission_by_name('海上预警')
        unit_name_list = ['S 100B 型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='海上预警', unit_list=unit_guid_list)
        end_time_str = '05/23/2090 12:30:00'
        S_100B_patrol.set_end(end_time_str)     
        S_100B_patrol.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队，常用于战斗机
        S_100B_patrol.set_flightStoengage('all')  # 敌方对抗的飞机数量 所有飞机编队出动
        S_100B_patrol.set_wingmanEngageDistance(5)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        S_100B_patrol.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        S_100B_patrol.station_count(0)  # 为保持阵位的数量 0
        S_100B_patrol.set_one_third_rule(False)  # 三分之一规则 不开启
        S_100B_patrol.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        S_100B_patrol.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        S_100B_patrol.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射  不开启
        S_100B_patrol.patrol_set_throttle_transit(Throttle.Loiter)  # 设置任务的出航油门 全速
        S_100B_patrol.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 巡航
        S_100B_patrol.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定

        # 海上预警机B
        time.sleep(1.0)     
        self.create_patrol_mission(name='海上预警B', mission_type=MissionPatrolType.AIR,
                                   point_list=[(18.4, -82.0), (18.4, -81.7), (18.1, -81.7), (18.1, -82.0)])
        S_100B_patrol_B = self.get_mission_by_name('海上预警B')
        # unit_name_list = ['S 100B 型 #1']
        # unit_guid_list = [
        #     unit.get('guid', '') for unit in situation_data.values()
        #     if isinstance(unit, dict)
        #        and (unit.get('name', '') in unit_name_list)
        # ]
        # self.assign_units_to_mission(mission_name='海上预警B', unit_list=unit_guid_list)
        S_100B_patrol_B.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队，常用于战斗机
        S_100B_patrol_B.set_flightStoengage('all')  # 敌方对抗的飞机数量 所有飞机编队出动
        S_100B_patrol_B.set_wingmanEngageDistance(5)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        S_100B_patrol_B.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        S_100B_patrol_B.station_count(0)  # 为保持阵位的数量 0
        S_100B_patrol_B.set_one_third_rule(False)  # 三分之一规则 不开启
        S_100B_patrol_B.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        S_100B_patrol_B.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        S_100B_patrol_B.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射  不开启
        S_100B_patrol_B.patrol_set_throttle_transit(Throttle.Loiter)  # 设置任务的出航油门 全速
        S_100B_patrol_B.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 巡航
        S_100B_patrol_B.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定

        # 中间预警机
        time.sleep(1.0)        
        self.create_patrol_mission(name='中部预警', mission_type=MissionPatrolType.AIR,
                                   point_list=[(17.9, -86.4), (17.9, -86.3), (17.8, -86.3), (17.8, -86.4)])
        A_100_patrol = self.get_mission_by_name('中部预警')
        unit_name_list = ['A-100 Premier 预警机 [伊尔-476] #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='中部预警', unit_list=unit_guid_list)
        A_100_patrol.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队，常用于战斗机
        A_100_patrol.set_flightStoengage('all')  # 敌方对抗的飞机数量 所有飞机编队出动
        A_100_patrol.set_wingmanEngageDistance(5)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        A_100_patrol.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        A_100_patrol.station_count(0)  # 为保持阵位的数量 0
        A_100_patrol.set_one_third_rule(False)  # 三分之一规则 不开启
        A_100_patrol.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        A_100_patrol.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        A_100_patrol.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射  不开启
        A_100_patrol.patrol_set_throttle_transit(Throttle.Flank)  # 设置任务的出航油门 全速
        A_100_patrol.patrol_set_throttle_station(Throttle.Cruise)  # 设置任务的阵位油门 巡航
        A_100_patrol.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定

        # 陆地预警机
        time.sleep(1.0)        
        self.create_patrol_mission(name='陆地预警', mission_type=MissionPatrolType.AIR,
                                   point_list=[(17.6,-91.7), (17.6,-91.5), (17.4,-91.5), (17.4,-91.7)])
        A50_patrol = self.get_mission_by_name('陆地预警')
        unit_name_list = ['A-50U型 #1','图-160M Blackjack 轰炸机 #1', '图-160M Blackjack 轰炸机 #2']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='陆地预警', unit_list=unit_guid_list)
        A50_patrol.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队，常用于战斗机
        A50_patrol.set_flightStoengage('all')  # 敌方对抗的飞机数量 所有飞机编队出动
        A50_patrol.set_wingmanEngageDistance(5)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        A50_patrol.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        A50_patrol.station_count(0)  # 为保持阵位的数量 0
        A50_patrol.set_one_third_rule(False)  # 三分之一规则 不开启
        A50_patrol.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        A50_patrol.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        A50_patrol.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射  不开启
        A50_patrol.patrol_set_throttle_transit(Throttle.Flank)  # 设置任务的出航油门 全速
        A50_patrol.patrol_set_throttle_station(Throttle.Cruise)  # 设置任务的阵位油门 巡航
        A50_patrol.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定

        # 陆地预警机B
        time.sleep(1.0)        
        self.create_patrol_mission(name='陆地预警B', mission_type=MissionPatrolType.AIR,
                                   point_list=[(17.08, -91.22), (17.07, -90.95), (16.83, -90.96), (16.82, -91.21)])
        A50_patrol_B = self.get_mission_by_name('陆地预警B')
        # unit_name_list = ['A-50U型 #1','图-160M Blackjack 轰炸机 #1', '图-160M Blackjack 轰炸机 #2']
        # unit_guid_list = [
        #     unit.get('guid', '') for unit in situation_data.values()
        #     if isinstance(unit, dict)
        #        and (unit.get('name', '') in unit_name_list)
        # ]
        # self.assign_units_to_mission(mission_name='陆地预警B', unit_list=unit_guid_list)   
        A50_patrol_B.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 1机编队，常用于战斗机
        A50_patrol_B.set_flightStoengage('all')  # 敌方对抗的飞机数量 所有飞机编队出动
        A50_patrol_B.set_wingmanEngageDistance(5)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        A50_patrol_B.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        A50_patrol_B.station_count(0)  # 为保持阵位的数量 0
        A50_patrol_B.set_one_third_rule(False)  # 三分之一规则 不开启
        A50_patrol_B.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 不开启
        A50_patrol_B.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        A50_patrol_B.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射  不开启
        A50_patrol_B.patrol_set_throttle_transit(Throttle.Flank)  # 设置任务的出航油门 全速
        A50_patrol_B.patrol_set_throttle_station(Throttle.Cruise)  # 设置任务的阵位油门 巡航
        A50_patrol_B.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定

        # ---------------------------支援任务----------------------------
        # 陆地加油
        time.sleep(1.0)        
        self.create_support_mission(name='陆地加油', point_list=[(17.0, -92.5), (18.1, -91.7),(18.7, -88.3)])
        Land_addoil = self.get_mission_by_name('陆地加油')
        unit_name_list = ['伊尔-78型 #3', '3MS-2 “北美野牛” Bison B 空中加油机 [Tanker] #1','伊尔-78型 #1', '伊尔-78型 #2', '伊尔-96-400TZ型加油机']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='陆地加油', unit_list=unit_guid_list)
        Land_addoil.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Land_addoil.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Land_addoil.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Land_addoil.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Land_addoil.station_count(0)  # 为保持阵位的数量 0
        Land_addoil.set_one_third_rule(False)  # 三分之一规则 不开启
        Land_addoil.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Land_addoil.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Land_addoil.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Land_addoil.support_throttle_transit(Throttle.Flank)  # 设置任务的飞机出航油门
        Land_addoil.support_throttle_station(Throttle.Flank)  # 设置任务的阵位油门
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == '伊尔-22PP型 #2':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.EMCON_Obey_doctrine(True)
                set_unit.switch_radar(True,)

        time.sleep(1.0)        
        self.create_support_mission(name='KN06就位', point_list=[(19.5,-89.5)])
        KN06 = self.get_mission_by_name('KN06就位')
        unit_name_list = ['地空导弹营(KN-06型地空导弹 [Pongae-5型防空导弹])']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='KN06就位', unit_list=unit_guid_list)
        KN06.support_flightSize(FlightSize.One)  # 设置任务编队规模
        KN06.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        KN06.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        KN06.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        KN06.station_count(0)  # 为保持阵位的数量 0
        KN06.set_one_third_rule(False)  # 三分之一规则 不开启
        KN06.support_oneTimeOnly(False)  # 是否仅一次 不开启
        KN06.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        KN06.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        KN06.support_throttle_transit(Throttle.Flank)  # 设置任务的飞机出航油门
        KN06.support_throttle_station(Throttle.Flank)  # 设置任务的阵位油门
        for unit in situation_data.values():
            if isinstance(unit, dict):
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.Yes)
                set_unit.doctrine_engage_opportunity_targets(EngageWithContactTarget.Yes_AnyTarget)
                set_unit.EMCON_Obey_doctrine(True)
                set_unit.switch_radar(True,)

        time.sleep(1.0)        
        self.create_support_mission(name='南高后撤', point_list=[(19.1,-91.8)])
        NanGao = self.get_mission_by_name('南高后撤')
        unit_name_list = ['“南高”级护卫舰']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='南高后撤', unit_list=unit_guid_list)
        NanGao.support_flightSize(FlightSize.One)  # 设置任务编队规模
        NanGao.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        NanGao.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        NanGao.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        NanGao.station_count(0)  # 为保持阵位的数量 0
        NanGao.set_one_third_rule(False)  # 三分之一规则 不开启
        NanGao.support_oneTimeOnly(False)  # 是否仅一次 不开启
        NanGao.support_activeEMCON(True)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        NanGao.support_loopType(True)  # 导航类型 True-仅一次；False-连续循环
        NanGao.support_set_throttle_transit_ship(Throttle.Flank)  # 设置任务的飞机出航油门
        NanGao.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == '“南高”级护卫舰':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.No)
                set_unit.doctrine_engage_opportunity_targets(EngageWithContactTarget.Yes_AnyTarget)
                set_unit.EMCON_Obey_doctrine(False)
                set_unit.switch_radar(False,)

        time.sleep(1.0)        
        self.create_support_mission(name='戈尔后撤', point_list=[(19.15,-84.3)])
        GeEr = self.get_mission_by_name('戈尔后撤')
        unit_name_list = ['Pr.2235.0 “戈尔什科夫海军元帅”级护卫舰']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='戈尔后撤', unit_list=unit_guid_list)
        GeEr.support_flightSize(FlightSize.One)  # 设置任务编队规模
        GeEr.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        GeEr.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        GeEr.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        GeEr.station_count(0)  # 为保持阵位的数量 0
        GeEr.set_one_third_rule(False)  # 三分之一规则 不开启
        GeEr.support_oneTimeOnly(False)  # 是否仅一次 不开启
        GeEr.support_activeEMCON(True)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        GeEr.support_loopType(True)  # 导航类型 True-仅一次；False-连续循环
        GeEr.support_set_throttle_transit_ship(Throttle.Flank)  # 设置任务的飞机出航油门
        GeEr.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == 'Pr.2235.0 “戈尔什科夫海军元帅”级护卫舰':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.No)
                set_unit.EMCON_Obey_doctrine(True)
                set_unit.switch_radar(True,)

        time.sleep(1.0)
        self.create_support_mission(name='C国地面单位侦察', point_list=[(16.05,-93.52),(16.63,-94.22),(18.17,-94.15),(18.6,-94.05)])
        C_land_detect = self.get_mission_by_name('C国地面单位侦察')
        unit_name_list = ['图-214R型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='C国地面单位侦察', unit_list=unit_guid_list)
        C_land_detect.support_flightSize(FlightSize.One)  # 设置任务编队规模
        C_land_detect.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        C_land_detect.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        C_land_detect.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        C_land_detect.station_count(0)  # 为保持阵位的数量 0
        C_land_detect.set_one_third_rule(False)  # 三分之一规则 不开启
        C_land_detect.support_oneTimeOnly(False)  # 是否仅一次 不开启
        C_land_detect.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        C_land_detect.support_loopType(True)  # 导航类型 True-仅一次；False-连续循环
        C_land_detect.support_throttle_transit(Throttle.Flank)  # 设置任务的飞机出航油门
        C_land_detect.support_throttle_station(Throttle.Cruise)  # 设置任务的阵位油门

        # 海上加油
        time.sleep(1.0)        
        self.create_support_mission(name='海上加油', point_list=[(18.7, -85.5),(19.0, -83.4),(19.0, -81.8)])
        Sea_addoil = self.get_mission_by_name('海上加油')
        unit_name_list = ['伊尔-96-400TZ型 #1', '伊尔-96-400TZ型 #2', '空客A310-304 MRTT型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='海上加油', unit_list=unit_guid_list)
        Sea_addoil.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Sea_addoil.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Sea_addoil.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Sea_addoil.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Sea_addoil.station_count(0)  # 为保持阵位的数量 0
        Sea_addoil.set_one_third_rule(False)  # 三分之一规则 不开启
        Sea_addoil.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Sea_addoil.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Sea_addoil.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Sea_addoil.support_throttle_transit(Throttle.Flank)  # 设置任务的飞机出航油门
        Sea_addoil.support_throttle_station(Throttle.Flank)  # 设置任务的阵位油门

        # 西部海域侦察
        # time.sleep(1.0)        
        # self.create_support_mission(name='西部海域侦察', point_list=[(14.1,-103.25),(15.3,-107.0),(18.0,-106.5)])
        # Sea_detect = self.get_mission_by_name('西部海域侦察')
        # unit_name_list = ['图-22MR 型 #1']
        # unit_guid_list = [
        #     unit.get('guid', '') for unit in situation_data.values()
        #     if isinstance(unit, dict)
        #        and (unit.get('name', '') in unit_name_list)
        # ]
        # self.assign_units_to_mission(mission_name='西部海域侦察', unit_list=unit_guid_list)
        # Sea_detect.support_flightSize(FlightSize.One)  # 设置任务编队规模
        # Sea_detect.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        # Sea_detect.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        # Sea_detect.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        # Sea_detect.station_count(0)  # 为保持阵位的数量 0
        # Sea_detect.set_one_third_rule(False)  # 三分之一规则 不开启
        # Sea_detect.support_oneTimeOnly(True)  # 是否仅一次 开启
        # Sea_detect.support_activeEMCON(True)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        # Sea_detect.support_loopType(True)  # 导航类型 True-仅一次；False-连续循环
        # Sea_detect.support_throttle_transit(Throttle.Full)  # 设置任务的飞机出航油门
        # Sea_detect.support_throttle_station(Throttle.Flank)  # 设置任务的阵位油门
        # Sea_detect.support_stationAltitude(99999)
        # Sea_detect.support_transitAltitude(100)

        # time.sleep(1.0)        
        # self.create_support_mission(name='海上侦察B', point_list=[(14.1,-103.25),(15.3,-107.0),(18.0,-106.5)])
        # Sea_detectB = self.get_mission_by_name('海上侦察B')
        # unit_name_list = []
        # unit_guid_list = [
        #     unit.get('guid', '') for unit in situation_data.values()
        #     if isinstance(unit, dict)
        #        and (unit.get('name', '') in unit_name_list)
        # ]
        # self.assign_units_to_mission(mission_name='海上侦察B', unit_list=unit_guid_list)
        # Sea_detectB.support_flightSize(FlightSize.One)  # 设置任务编队规模
        # Sea_detectB.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        # Sea_detectB.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        # Sea_detectB.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        # Sea_detectB.station_count(0)  # 为保持阵位的数量 0
        # Sea_detectB.set_one_third_rule(False)  # 三分之一规则 不开启
        # Sea_detectB.support_oneTimeOnly(True)  # 是否仅一次 开启
        # Sea_detectB.support_activeEMCON(True)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        # Sea_detectB.support_loopType(True)  # 导航类型 True-仅一次；False-连续循环
        # Sea_detectB.support_throttle_transit(Throttle.Cruise)  # 设置任务的飞机出航油门
        # Sea_detectB.support_throttle_station(Throttle.Flank)  # 设置任务的阵位油门
        # Sea_detectB.support_stationAltitude(99999)
        # Sea_detectB.support_transitAltitude(99999)

        # 巡洋舰
        time.sleep(1.0)        
        self.create_support_mission(name='巡洋舰后撤', point_list=[(15.6,-82.3)])
        ASW_support = self.get_mission_by_name('巡洋舰后撤')
        unit_name_list = ['RKR“彼得大帝”号核动力导弹战列巡洋舰 [Pr.1144.2 Orlan, Ex-Yuri Androvo]', '库兹涅佐夫号航空母舰[Pr.1143.5]']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='巡洋舰后撤', unit_list=unit_guid_list)
        ASW_support.support_ship_size(GroupSize.Single)  # 设置任务编队规模
        ASW_support.support_use_group_size(False) # 是否舰船/潜艇数低于编队规模不允许出发
        ASW_support.support_activeEMCON(True)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        ASW_support.support_loopType(True)  # 导航类型 True-仅一次；False-连续循环
        unit_guid = None
        for unit in situation_data.values():
            unit_guid = unit.get('guid')
            set_unit.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.No) # 攻击时不忽略航线
            set_unit.doctrine_weapon_control_status_air(WeaponControlStatus.Free)  # 武器控制状态，对空；自由开火
            set_unit.doctrine_engage_opportunity_targets(EngageWithContactTarget.Yes_AnyTarget)

        time.sleep(1.0)        
        self.create_support_mission(name='北朝鲜打击', point_list=[(18.22,-90.66)])
        BCX = self.get_mission_by_name('北朝鲜打击')
        unit_name_list = ['SSM Bn (KN-23)北朝鲜移动车辆']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='北朝鲜打击', unit_list=unit_guid_list)
        BCX.support_ship_size(GroupSize.Single)  # 设置任务编队规模
        BCX.support_use_group_size(False) # 是否舰船/潜艇数低于编队规模不允许出发
        BCX.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        unit_guid = None
        for unit in situation_data.values():
            unit_guid = unit.get('guid')
            set_unit.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.Yes) # 攻击时不忽略航线
            set_unit.doctrine_engage_opportunity_targets(EngageWithContactTarget.No_Only)

        # 坦克占领支援
        time.sleep(1.0)        
        self.create_support_mission(name='坦克占领', point_list=[(16.38, -94.1)])
        Tank_support = self.get_mission_by_name('坦克占领')
        unit_name_list = ['坦克排(“暴风虎”主战坦克 x 3)']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='坦克占领', unit_list=unit_guid_list)
        Tank_support.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Tank_support.support_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞
        Tank_support.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Tank_support.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Tank_support.station_count(0)  # 为保持阵位的数量
        Tank_support.set_one_third_rule(False)  # 三分之一规则
        Tank_support.support_oneTimeOnly(True)  # 是否仅一次
        Tank_support.support_activeEMCON(True)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开
        Tank_support.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Tank_support.support_throttle_transit(Throttle.Flank)  # 设置任务的飞机出航油门
        Tank_support.support_throttle_station(Throttle.Flank)  # 设置任务的阵位油门

        time.sleep(1.0)        
        self.create_support_mission(name='飞机后撤', point_list=[(15.5, -89.3)])
        Air_retreat = self.get_mission_by_name('飞机后撤')
        unit_name_list = []
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='飞机后撤', unit_list=unit_guid_list)
        Air_retreat.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Air_retreat.support_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞
        Air_retreat.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Air_retreat.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Air_retreat.station_count(0)  # 为保持阵位的数量
        Air_retreat.set_one_third_rule(False)  # 三分之一规则
        Air_retreat.support_oneTimeOnly(True)  # 是否仅一次
        Air_retreat.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开
        Air_retreat.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Air_retreat.support_throttle_transit(Throttle.Cruise)  # 设置任务的飞机出航油门
        Air_retreat.support_throttle_station(Throttle.Cruise)  # 设置任务的阵位油门
        Air_retreat.support_transitAltitude(99999)
        Air_retreat.support_stationAltitude(99999)

        # 中右上方潜艇下潜
        time.sleep(1.0)
        self.create_support_mission(name='中右上方潜艇下潜', point_list=[(24.5, -88.3)])
        SM1_escape = self.get_mission_by_name('中右上方潜艇下潜')
        unit_name_list = ['945型塞拉S级核动力潜艇']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='中右上方潜艇下潜', unit_list=unit_guid_list)
        SM1_escape.station_count(1)  # 为保持阵位的数量 1
        SM1_escape.set_one_third_rule(False)  # 三分之一规则 不开启
        SM1_escape.support_oneTimeOnly(False)  # 是否仅一次 不开启
        SM1_escape.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        SM1_escape.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        SM1_escape.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        SM1_escape.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        SM1_escape.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        SM1_escape.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        SM1_escape.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        SM1_escape.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        SM1_escape.support_set_depth_transit_submarine(-9999)#设置潜艇出航高度
        SM1_escape.support_set_depth_station_submarine(-9999)#设置潜艇阵位高度

        # 中右下方潜艇下潜
        time.sleep(1.0)
        self.create_support_mission(name='中右下方潜艇下潜', point_list=[(17.51, -86.71), (16.73, -86.80)])
        SM2_escape = self.get_mission_by_name('中右下方潜艇下潜')
        unit_name_list = ['“新浦”级弹道导弹潜艇']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='中右下方潜艇下潜', unit_list=unit_guid_list)
        SM2_escape.station_count(1)  # 为保持阵位的数量 1
        SM2_escape.set_one_third_rule(False)  # 三分之一规则 不开启
        SM2_escape.support_oneTimeOnly(False)  # 是否仅一次 不开启
        SM2_escape.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        SM2_escape.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        SM2_escape.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        SM2_escape.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        SM2_escape.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        SM2_escape.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        SM2_escape.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        SM2_escape.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        SM2_escape.support_set_depth_transit_submarine(-9999)#设置潜艇出航高度
        SM2_escape.support_set_depth_station_submarine(-9999)#设置潜艇阵位高度

        #西部海域潜艇上移  (打击蓝方舰船)
        time.sleep(1.0)
        self.create_support_mission(name='西部海域潜艇上移', point_list=[(17.21,-106.00), (17.65, -106.65)])
        YaSen_support = self.get_mission_by_name('西部海域潜艇上移')
        unit_name_list = ['PLA-885M “亚森”级多用途核潜艇']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='西部海域潜艇上移', unit_list=unit_guid_list)
        YaSen_support.station_count(1)  # 为保持阵位的数量 1
        YaSen_support.set_one_third_rule(False)  # 三分之一规则 不开启
        YaSen_support.support_oneTimeOnly(False)  # 是否仅一次 不开启
        YaSen_support.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        YaSen_support.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        YaSen_support.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        YaSen_support.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        YaSen_support.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        YaSen_support.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        YaSen_support.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        YaSen_support.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        YaSen_support.support_set_depth_transit_submarine(-380)#设置潜艇出航高度
        YaSen_support.support_set_depth_station_submarine(-380)#设置潜艇阵位高度

        time.sleep(1.0)
        self.create_support_mission(name='A12电抗', point_list=[(16.5,-92.3),(17.5,-92.3)])
        A12 = self.get_mission_by_name('A12电抗')
        unit_name_list = ['安-12BK-PPS型 #1','伊尔-22PP型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='A12电抗', unit_list=unit_guid_list)
        A12.station_count(0)  # 为保持阵位的数量 1
        A12.set_one_third_rule(False)  # 三分之一规则 不开启
        A12.support_oneTimeOnly(False)  # 是否仅一次 不开启
        A12.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        A12.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        A12.support_throttle_station(Throttle.Cruise) 
        A12.support_throttle_transit(Throttle.Loiter) 

        time.sleep(1.0)
        self.create_support_mission(name='22PP电抗', point_list=[(18.35,-89.2),(19.0,-83.4)])
        E22PP = self.get_mission_by_name('22PP电抗')
        unit_name_list = ['伊尔-22PP型 #2']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='22PP电抗', unit_list=unit_guid_list)
        E22PP.station_count(0)  # 为保持阵位的数量 1
        E22PP.set_one_third_rule(False)  # 三分之一规则 不开启
        E22PP.support_oneTimeOnly(False)  # 是否仅一次 不开启
        E22PP.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        E22PP.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        E22PP.support_throttle_station(Throttle.Cruise) 
        E22PP.support_throttle_transit(Throttle.Loiter) 

        time.sleep(1.0)
        self.create_support_mission(name='间谍船探测', point_list=[(20.5,-84.5)])
        JianDie = self.get_mission_by_name('间谍船探测')
        unit_name_list = ['商用捕鱼船[35米, 间谍船]#1','商用捕鱼船[35米, 间谍船]#2','商用捕鱼船[35米, 间谍船]#3']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='间谍船探测', unit_list=unit_guid_list)
        JianDie.station_count(0)  # 为保持阵位的数量 1
        JianDie.set_one_third_rule(False)  # 三分之一规则 不开启
        JianDie.support_oneTimeOnly(False)  # 是否仅一次 不开启
        JianDie.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        JianDie.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        JianDie.support_throttle_station(Throttle.Flank) 
        JianDie.support_throttle_transit(Throttle.Flank)

        time.sleep(1.0)
        self.create_support_mission(name='图22', point_list=[(19.0,-89.5)])
        Tu22 = self.get_mission_by_name('图22')
        unit_name_list = ['图-22M-3M型 #1','图-22M-3M型 #2','图-22M-3M型 #3','图-22M-3M型 #4','图-22M-3M型 #5','图-22M-3M型 #6']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='图22', unit_list=unit_guid_list)
        Tu22.station_count(0)  # 为保持阵位的数量 1
        Tu22.set_one_third_rule(False)  # 三分之一规则 不开启
        Tu22.support_oneTimeOnly(True)  # 是否仅一次 不开启
        Tu22.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Tu22.support_loopType(True)  # 导航类型 True-仅一次；False-连续循环
        Tu22.support_throttle_station(Throttle.Full) 
        Tu22.support_throttle_transit(Throttle.Cruise)  
        
        # ---------------------------打击任务----------------------------

        # 苏-34“鸭嘴兽”轰炸机 对地打击任务
        time.sleep(1.0)        
        self.Su34_attack = self.create_strike_mission('鸭嘴兽对地打击', MissionStrikeType.LAND)
        Su34_attack = self.get_mission_by_name('鸭嘴兽对地打击')
        unit_name_list = ['苏-34“鸭嘴兽”轰炸机 #1', '苏-34“鸭嘴兽”轰炸机 #2', '苏-34“鸭嘴兽”轰炸机 #3', '苏-34“鸭嘴兽”轰炸机 #4']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict) and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='鸭嘴兽对地打击', unit_list=unit_guid_list)
        Su34_attack.strike_setPreplan(True)  # 仅考虑任务目标
        Su34_attack.strike_setStrikeFlightSize(FlightSize.One)  # 2机编队
        Su34_attack.strike_setStrikeFuleAmmo(StrikeFuleAmmo.FAR_DIST)  # 在最远距离上投掷/抛弃还是带回空对地弹药
        Su34_attack.doctrine_engage_opportunity_targets(EngageWithContactTarget.Yes_AnyTarget) # 接战临机目标
        
        # ---------------------------其他条令-----------------------------
        
        unit_guid = None
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == '地地导弹营(“舞水端-1”型中程弹道导弹)':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.doctrine_weapon_control_status_air(WeaponControlStatus.Hold)  # 武器控制状态，对空；限制开火
                set_unit.doctrine_weapon_control_status_surface(WeaponControlStatus.Hold)  # 武器控制状态，对海，限制开火
                set_unit.doctrine_weapon_control_status_subsurface(WeaponControlStatus.Hold)  # 武器控制状态，对潜；限制开火
                set_unit.doctrine_weapon_control_status_land(WeaponControlStatus.Hold)  # 武器控制状态，对地：限制开火

        unit_guid = None
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == '地地导弹营 (KN-01型地对舰导弹)':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.wra_qty_salvo(3351, WRA_WeaponTargetType.Surface_Contact_Unknown_Type, 6)
                set_unit.wra_qty_salvo(3351, WRA_WeaponTargetType.Ship_Surface_Combatant_0_500_tons, 6)
                set_unit.wra_qty_salvo(3351, WRA_WeaponTargetType.Ship_Surface_Combatant_501_1500_tons, 6)
                set_unit.wra_qty_salvo(3351, WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons, 6)
                set_unit.wra_qty_salvo(3351, WRA_WeaponTargetType.Ship_Surface_Combatant_5001_10000_tons, 6)
                set_unit.wra_qty_salvo(3351, WRA_WeaponTargetType.Ship_Surface_Combatant_10001_25000_tons, 6)
                set_unit.wra_qty_salvo(3351, WRA_WeaponTargetType.Ship_Surface_Combatant_25001_45000_tons, 6)
                set_unit.wra_qty_salvo(3351, WRA_WeaponTargetType.Ship_Surface_Combatant_45001_95000_tons, 6)
                set_unit.wra_qty_salvo(3351, WRA_WeaponTargetType.Ship_Surface_Combatant_95000_tons, 6)
                set_unit.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.Yes)
                set_unit.doctrine_engage_opportunity_targets(EngageWithContactTarget.Yes_AnyTarget)

        self.wra_firing_range(352,WRA_WeaponTargetType.Aircraft_Low_Perf_Recon_EW,20)
        self.wra_firing_range(352,WRA_WeaponTargetType.Aircraft_5th_Generation,0)
        self.wra_firing_range(352,WRA_WeaponTargetType.Aircraft_Unspecified,80)
                


        # 设置任务的加油计划
        missions = self.missions_obj
        for mission_k, mission_v in missions.items():
            mission_v.use_tanker('Automatic')  # 自动选择加油机
            mission_v.set_mission_fuelQtyToStartLookingForTanker_airborne(20)  # 受油机低于30%油量前往加油机
            mission_v.set_mission_tankerMaxDistance_airborne(1000)  # 空中受油机多远距离上寻找加油机
        # self.doctrine_weapon_control_status_air(WeaponControlStatus.Tight)  # 设置开火条件为：谨慎开火
        print("=================任务设置完毕=================")
        text = "=================任务设置完毕================="  # 智能体调度消息输出
        test = self.agent_message_text(text=text)
        print(f'纯文本显示输出返回：{test}')

        self.log.info('%s:%s initial game' % (self.Name, self.__class__.__name__))

    def step(self, time_elapse, situation):
        """
        # 每步决策函数
        :param time_elapse:  int, time elapse
        :param situation: tuple: units-list, contacts-list
        :return:
        """
        print('执行step')
        self.log.info('%s:%s step game time:%d, units:%d contact:%d' %
                      (self.Name, self.__class__.__name__, time_elapse, len(situation[0]), len(situation[1])))

        situation_data = situation[0] if isinstance(situation[0], dict) else []

        if self.flag1==0 and time_elapse >= 4920:
            unit_name_list = ['S 100B 型 #1']
            unit_guid_list = [
                unit.get('guid', '') for unit in situation_data.values()
                if isinstance(unit, dict)
                   and (unit.get('name', '') in unit_name_list)
            ]
            self.assign_units_to_mission(mission_name='海上预警B', unit_list=unit_guid_list)
            self.flag1 = True

        if self.flag2==0 and time_elapse >= 4920:
            unit_name_list = ['A-50U型 #1','图-160M Blackjack 轰炸机 #1', '图-160M Blackjack 轰炸机 #2']
            unit_guid_list = [
                unit.get('guid', '') for unit in situation_data.values()
                if isinstance(unit, dict)
                and (unit.get('name', '') in unit_name_list)
            ]
            self.assign_units_to_mission(mission_name='陆地预警B', unit_list=unit_guid_list)  
            self.flag2 = True






