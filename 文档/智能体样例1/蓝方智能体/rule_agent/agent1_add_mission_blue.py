# -*- coding:utf-8 -*-
# Author: 退退退不掉队-王鹏扉

"""
任务设置智能体
包括
巡逻任务
支援任务
打击任务
以及其他特殊的条令设置
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


        # ------------------------A.巡逻任务--------------------------

        # ------------------------A.巡逻任务   1.东边海面--------------------------

        self.create_patrol_mission(name='保护海面', mission_type=MissionPatrolType.AIR,
                                   point_list=[(23.99, -85.11), (23.99, -84.00), (23.13, -84.00), (23.13, -85.11)])
        self.add_prosecution_zone(mission_name='保护海面',
                                  point_list=[(25.11, -85.86), (25.11, -82.30), (22.41, -82.30), (22.41, -85.86)])
        Mission_1 = self.get_mission_by_name('保护海面')
        unit_name_list = ['F-16C Blk 32 “战隼”战斗机  #1', 'F-16C Blk 32 “战隼”战斗机  #2', 'F-16C Blk 32 “战隼”战斗机  #3']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='保护海面', unit_list=unit_guid_list)
        Mission_1.patrol_flight_size(FlightSize.One)  # 设置任务编队规模 机编队，常用于战斗机
        Mission_1.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_1.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_1.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_1.station_count(0)  # 为保持阵位的数量 0
        Mission_1.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_1.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_1.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_1.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_1.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_1.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_1.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_1.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_1.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_1.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_1.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='保护R国', mission_type=MissionPatrolType.AIR,
                                   point_list=[(22.84, -81.93), (22.84, -81.37), (22.27, -81.37), (22.27, -81.93)])
        self.add_prosecution_zone(mission_name='保护R国',
                                  point_list=[(23.18, -83.61), (23.18, -80.67), (21.72, -79.55), (20.94, -81.86),
                                              (22.05, -83.64)])
        Mission_8 = self.get_mission_by_name('保护R国')
        unit_name_list = ['F-2A型 #4', 'F-2A型 #5', 'F-2A型 #6', 'F-15DJ型 #1', 'F-15DJ型 #2']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='保护R国', unit_list=unit_guid_list)
        Mission_8.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_8.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_8.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_8.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_8.station_count(0)  # 为保持阵位的数量 0
        Mission_8.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_8.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_8.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_8.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_8.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_8.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_8.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_8.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_8.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_8.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_8.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='保卫海峡', mission_type=MissionPatrolType.AIR,
                                   point_list=[(22.52, -86.78), (22.52, -85.80), (21.91, -85.80), (21.91, -86.78)])
        self.add_prosecution_zone(mission_name='保卫海峡',
                                  point_list=[(23.61, -86.88), (23.61, -84.73), (21.20, -84.73), (21.20, -86.88)])
        Mission_41 = self.get_mission_by_name('保卫海峡')
        unit_name_list = ['F-15E型 #1', 'F-15E型 #2', 'F-15E型 #3']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='保卫海峡', unit_list=unit_guid_list)
        Mission_41.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_41.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_41.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_41.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_41.station_count(0)  # 为保持阵位的数量 0
        Mission_41.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_41.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_41.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_41.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_41.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_41.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_41.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_41.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_41.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_41.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_41.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        # ------------------------A.巡逻任务   2.中部陆地与海面--------------------------

        time.sleep(0.5)
        self.create_patrol_mission(name='陆地北巡逻', mission_type=MissionPatrolType.AIR,
                                   point_list=[(21.73, -89.47), (21.73, -87.50), (21.02, -87.50), (21.02, -89.47)])
        self.add_prosecution_zone(mission_name='陆地北巡逻',
                                  point_list=[(22.09, -90.29), (22.09, -86.83), (20.45, -86.83), (20.45, -90.29)])
        Mission_16 = self.get_mission_by_name('陆地北巡逻')
        unit_name_list = ['F-35FA 型 #1', 'F-35FA 型 #2', 'F-22A型 #1', 'F-22A型 #2']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='陆地北巡逻', unit_list=unit_guid_list)
        Mission_16.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_16.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_16.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_16.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_16.station_count(0)  # 为保持阵位的数量 0
        Mission_16.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_16.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_16.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_16.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_16.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_16.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_16.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_16.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_16.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_16.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_16.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='C国北巡逻', mission_type=MissionPatrolType.AIR,
                                   point_list=[(20.72, -94.22), (20.72, -92.58), (20.36, -92.58), (20.36, -94.22)])
        self.add_prosecution_zone(mission_name='C国北巡逻',
                                  point_list=[(21.10, -94.97), (21.10, -90.64), (19.29, -90.64), (19.29, -94.97)])
        Mission_19 = self.get_mission_by_name('C国北巡逻')
        unit_name_list = ['EA-18G型 #2', 'EA-18G型 #3', 'EC-130H型 #1', 'F/A-18F型 #1', 'F/A-18F型 #2', 'F/A-18F型 #3']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='C国北巡逻', unit_list=unit_guid_list)
        Mission_19.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_19.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_19.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_19.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_19.station_count(0)  # 为保持阵位的数量 0
        Mission_19.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_19.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_19.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_19.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_19.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_19.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_19.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_19.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_19.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_19.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_19.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='保护世宗', mission_type=MissionPatrolType.AIR,
                                   point_list=[(22.7, -91.0), (22.7, -90.3), (20.9, -90.3), (20.9, -91.0)])
        Mission_9 = self.get_mission_by_name('保护世宗')
        unit_name_list = []
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='保护世宗', unit_list=unit_guid_list)
        Mission_9.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_9.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_9.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_9.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_9.station_count(0)  # 为保持阵位的数量 0
        Mission_9.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_9.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_9.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_9.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_9.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_9.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_9.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_9.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_9.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_9.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_9.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        # ------------------------A.巡逻任务   3.西边陆地--------------------------

        time.sleep(0.5)
        self.create_patrol_mission(name='保护H国机场', mission_type=MissionPatrolType.AIR,
                                   point_list=[(19.78, -94.81), (19.78, -94.00), (17.66, -94.65), (17.64, -95.5)])
        self.add_prosecution_zone(mission_name='保护H国机场',
                                  point_list=[(18.5, -95.5), (18.53, -91.67), (16.20, -93.81), (16.9, -95.5)])
        Mission_6 = self.get_mission_by_name('保护H国机场')
        unit_name_list = ['F-15K型 #2', 'F-5F型 #3', 'F-5F型 #4', 'F-5F型 #5', 'FA-50型 #1', 'F-16DJ Blk 52型 #1',
                          'EA-18G型 #1', 'F-5F型 #1', 'F-5F型 #2', 'F-35C 型 #1', 'F-35C 型 #2']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='保护H国机场', unit_list=unit_guid_list[0:10])
        self.assign_units_to_mission(mission_name='保护H国机场', unit_list=unit_guid_list[10:])
        Mission_6.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_6.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_6.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_6.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_6.station_count(0)  # 为保持阵位的数量 0
        Mission_6.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_6.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_6.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_6.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_6.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_6.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_6.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_6.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_6.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_6.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_6.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        # ------------------------A.巡逻任务   4.西边海域保卫-----------------------

        time.sleep(0.5)
        self.create_patrol_mission(name='防偷家', mission_type=MissionPatrolType.AIR,
                                   point_list=[(19.71, -107.35), (19.70, -104.54), (16.30, -104.12), (15.53, -107.19)])
        Mission_51 = self.get_mission_by_name('防偷家')
        start_time_str = '05/23/2090 12:40:00'
        Mission_51.set_start(start_time_str)
        unit_name_list = ['F/A-18E型 #1', 'F/A-18E型 #2', 'F/A-18E型 #3']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='防偷家', unit_list=unit_guid_list)
        Mission_51.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  2机编队，常用于战斗机
        Mission_51.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_51.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_51.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_51.station_count(0)  # 为保持阵位的数量 0
        Mission_51.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_51.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_51.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_51.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_51.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_51.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_51.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_51.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_51.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_51.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_51.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        # ------------------------A.巡逻任务   5.反潜任务--------------------------

        time.sleep(0.5)
        self.create_patrol_mission(name='R国反潜北', mission_type=MissionPatrolType.ANTI_SUBMARINE,
                                   point_list=[(24.8, -86.7), (24.8, -86.0), (24.2, -86.0), (24.2, -86.7)])
        Mission_2 = self.get_mission_by_name('R国反潜北')
        unit_name_list = ['P-1型 #1', 'SH-60K型 #1', 'SH-60K型 #2', 'SH-60K型 #3', 'SH-60K型 #4', 'SH-60K型 #5', 'SH-60K型 #6', 'AW-159型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='R国反潜北', unit_list=unit_guid_list)
        Mission_2.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_2.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_2.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_2.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_2.station_count(0)  # 为保持阵位的数量 0
        Mission_2.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_2.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_2.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_2.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_2.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_2.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_2.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_2.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_2.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_2.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_2.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里
        Mission_2.set_PatrolMovementStyle(1) # 巡逻任务 动作风格设置: 0:区域内随机; 1:可重复循环；2：单次巡逻

        time.sleep(0.5)
        self.create_patrol_mission(name='R国反潜', mission_type=MissionPatrolType.ANTI_SUBMARINE,
                                   point_list=[(18.5, -87.0), (18.5, -86.1), (17.8, -86.1), (17.8, -87.0)])
        Mission_4 = self.get_mission_by_name('R国反潜')
        unit_name_list = []
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='R国反潜', unit_list=unit_guid_list)
        Mission_4.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_4.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_4.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_4.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_4.station_count(0)  # 为保持阵位的数量 0
        Mission_4.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_4.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_4.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_4.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_4.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_4.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_4.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_4.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_4.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_4.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_4.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里
        Mission_4.set_PatrolMovementStyle(1) # 巡逻任务 动作风格设置: 0:区域内随机; 1:可重复循环；2：单次巡逻

        time.sleep(0.5)
        self.create_patrol_mission(name='最左下反潜', mission_type=MissionPatrolType.ANTI_SUBMARINE,
                                   point_list=[(16.1, -105.5), (16.1, -104.5), (15.5, -104.5), (15.5, -105.5)])
        Mission_5 = self.get_mission_by_name('最左下反潜')
        unit_name_list = ['MH-60R   “海鹰”反潜直升机 #1', 'S-2E型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='最左下反潜', unit_list=unit_guid_list)
        Mission_5.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_5.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_5.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_5.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_5.station_count(0)  # 为保持阵位的数量 0
        Mission_5.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_5.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_5.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_5.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_5.patrol_set_throttle_transit(Throttle.Flank)  # 设置任务的出航油门 巡航
        Mission_5.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_5.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_5.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_5.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_5.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_5.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里
        Mission_5.set_PatrolMovementStyle(1) # 巡逻任务 动作风格设置: 0:区域内随机; 1:可重复循环；2：单次巡逻

        # ------------------------A.巡逻任务   6.预警任务--------------------------

        time.sleep(0.5)
        self.create_patrol_mission(name='左边预警', mission_type=MissionPatrolType.AIR,
                                   point_list=[(20.63, -92.76), (20.63, -92.86), (20.73, -92.86), (20.73, -92.76)])
        Mission_11 = self.get_mission_by_name('左边预警')
        unit_name_list = ['E-737型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='左边预警', unit_list=unit_guid_list)
        Mission_11.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_11.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_11.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_11.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_11.station_count(0)  # 为保持阵位的数量 0
        Mission_11.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_11.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_11.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_11.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_11.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_11.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_11.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_11.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_11.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_11.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_11.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='中间预警', mission_type=MissionPatrolType.AIR,
                                   point_list=[(22.5, -87.5), (22.5, -87.4), (22.4, -87.4), (22.4, -87.5)])
        Mission_14 = self.get_mission_by_name('中间预警')
        unit_name_list = ['E-8C型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='中间预警', unit_list=unit_guid_list)
        Mission_14.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_14.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_14.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_14.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_14.station_count(0)  # 为保持阵位的数量 0
        Mission_14.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_14.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_14.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_14.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_14.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_14.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_14.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_14.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_14.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_14.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_14.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='右边预警', mission_type=MissionPatrolType.AIR,
                                   point_list=[(23.78, -84.40), (23.78, -84.50), (23.68, -84.50), (23.68, -84.40)])
        Mission_20 = self.get_mission_by_name('右边预警')
        unit_name_list = ['E-767型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='右边预警', unit_list=unit_guid_list)
        Mission_20.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  2机编队，常用于战斗机
        Mission_20.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_20.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_20.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_20.station_count(0)  # 为保持阵位的数量 0
        Mission_20.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_20.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_20.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_20.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_20.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_20.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_20.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_20.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_20.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_20.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_20.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='陆地预警', mission_type=MissionPatrolType.AIR,
                                   point_list=[(17.8, -96.2), (17.8, -96.1), (17.7, -96.1), (17.7, -96.2)])
        Mission_21 = self.get_mission_by_name('陆地预警')
        unit_name_list = ['E-2D型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='陆地预警', unit_list=unit_guid_list)
        Mission_21.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  2机编队，常用于战斗机
        Mission_21.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_21.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_21.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_21.station_count(0)  # 为保持阵位的数量 0
        Mission_21.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_21.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_21.patrol_checkWWR(False)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_21.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_21.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_21.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_21.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_21.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_21.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_21.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_21.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        # ------------------------A.巡逻任务   7.特殊任务--------------------------

        time.sleep(0.5)
        self.create_patrol_mission(name='保护投送', mission_type=MissionPatrolType.AIR,
                                   point_list=[(20.8, -90.3), (20.8, -89.7), (20.1, -89.7), (20.1, -90.3)])
        Mission_15 = self.get_mission_by_name('保护投送')
        unit_name_list = []
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='保护投送', unit_list=unit_guid_list)
        Mission_15.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_15.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_15.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_15.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_15.station_count(0)  # 为保持阵位的数量 0
        Mission_15.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_15.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_15.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_15.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_15.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_15.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_15.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_15.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_15.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_15.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_15.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='阻止坦克占领', mission_type=MissionPatrolType.ANTI_LAND,
                                   point_list=[(16.82, -93.89), (16.77, -93.82), (16.50, -93.82), (16.34, -94.08), (16.38, -94.17), (16.64, -94.12)])
        Mission_22 = self.get_mission_by_name('阻止坦克占领')
        unit_name_list = ['F-15K型 #1', 'KF-21 Boramae 战斗机 Blk 2 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='阻止坦克占领', unit_list=unit_guid_list)
        Mission_22.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  2机编队，常用于战斗机
        Mission_22.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_22.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_22.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_22.station_count(0)  # 为保持阵位的数量 0
        Mission_22.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_22.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_22.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_22.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_22.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_22.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_22.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_22.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_22.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_22.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_22.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        # ------------------------A.巡逻任务   8.舔地任务--------------------------

        time.sleep(0.5)
        self.create_patrol_mission(name='右边舔地', mission_type=MissionPatrolType.ANTI_LAND,
                                   point_list=[(20.65, -90.27), (20.78, -89.92), (19.11, -89.12), (18.74, -89.72)])
        Mission_24 = self.get_mission_by_name('右边舔地')
        unit_name_list = ['AC-130J “幽灵骑士”攻击机 #1', 'AC-130J “幽灵骑士”攻击机 #2']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='右边舔地', unit_list=unit_guid_list)
        Mission_24.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  2机编队，常用于战斗机
        Mission_24.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_24.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_24.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_24.station_count(0)  # 为保持阵位的数量 0
        Mission_24.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_24.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_24.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_24.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_24.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_24.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_24.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_24.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_24.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_24.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_24.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='甘蒙1', mission_type=MissionPatrolType.ANTI_LAND,
                                   point_list=[(17.84, -91.93), (17.84, -91.64), (17.57, -91.64), (17.57, -91.93)])
        Mission_10 = self.get_mission_by_name('甘蒙1')
        unit_name_list = ['AV-8B型 #1', 'AV-8B型 #2', 'AV-8B型 #3']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='甘蒙1', unit_list=unit_guid_list)
        Mission_10.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  2机编队，常用于战斗机
        Mission_10.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_10.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_10.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_10.station_count(0)  # 为保持阵位的数量 0
        Mission_10.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_10.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_10.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_10.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_10.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_10.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_10.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_10.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_10.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_10.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_10.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='甘蒙2', mission_type=MissionPatrolType.ANTI_LAND,
                                   point_list=[(16.15, -89.91), (16.15, -89.59), (15.84, -89.59), (15.84, -89.91)])
        Mission_50 = self.get_mission_by_name('甘蒙2')
        unit_name_list = ['B-1B型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='甘蒙2', unit_list=unit_guid_list)
        Mission_50.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  2机编队，常用于战斗机
        Mission_50.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_50.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_50.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_50.station_count(0)  # 为保持阵位的数量 0
        Mission_50.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_50.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_50.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_50.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_50.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_50.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_50.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_50.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_50.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_50.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_50.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里
        unit_guid = None
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == 'B-1B型 #1':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Surface_Contact_Unknown_Type, 8)
                set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Land_Contact_Unknown_Type, 8)

        time.sleep(0.5)
        self.create_patrol_mission(name='北朝鲜', mission_type=MissionPatrolType.ANTI_LAND,
                                   point_list=[(17.21, -91.13), (17.21, -90.33), (16.41, -90.33), (16.41, -91.13)])
        Mission_49 = self.get_mission_by_name('北朝鲜')
        unit_name_list = []
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='北朝鲜', unit_list=unit_guid_list)
        Mission_49.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  2机编队，常用于战斗机
        Mission_49.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_49.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_49.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_49.station_count(0)  # 为保持阵位的数量 0
        Mission_49.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_49.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_49.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_49.patrol_activeEMCON(False)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_49.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_49.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_49.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        Mission_49.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_49.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_49.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_49.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里

        time.sleep(0.5)
        self.create_patrol_mission(name='舞水端', mission_type=MissionPatrolType.ANTI_LAND,
                                   point_list=[(15.47, -88.62), (15.54, -86.85), (14.10, -86.80), (13.20, -93.94)])
        Mission_48 = self.get_mission_by_name('舞水端')
        unit_name_list = ['B-2A型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='舞水端', unit_list=unit_guid_list)
        Mission_48.patrol_flight_size(FlightSize.One)  # 设置任务编队规模  机编队，常用于战斗机
        Mission_48.set_flightStoengage('all')  # 敌方对抗的飞机数量
        Mission_48.patrol_useFlightSize(False)  # 是否飞机数低于编队规模不允许起飞 否
        Mission_48.set_wingmanEngageDistance(30)  # 飞机设置  僚机可以在xx范围内侦察/交战   海里
        Mission_48.station_count(0)  # 为保持阵位的数量 0
        Mission_48.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_48.patrol_checkOPA(False)  # 设置任务是否对巡逻区外的探测目标进行分析 开启
        Mission_48.patrol_checkWWR(True)  # 设置任务是否对武器射程内探测目标进行分析 开启
        Mission_48.patrol_activeEMCON(True)  # 设置任务是否仅在巡逻/警戒区内打开电磁辐射 不开启
        Mission_48.patrol_set_throttle_transit(Throttle.Cruise)  # 设置任务的出航油门 巡航
        Mission_48.patrol_set_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门 低速
        Mission_48.patrol_set_throttle_attack(Throttle.Unspecified)  # 设置任务的攻击油门 不定
        # Mission_48.patrol_set_transitAltitude(99999.9)  # float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_48.patrol_set_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符
        # Mission_48.patrol_set_attackAltitude(attack_altitude)  # float, 攻击高度， 单位：米，最多6位字符
        # Mission_48.patrol_set_attack_distance(attack_distance)  # int, 攻击距离，单位：公里
        unit_guid = None
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == 'B-2A型 #1':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.wra_qty_salvo(11, WRA_WeaponTargetType.Land_Contact_Unknown_Type, 16)

        # ---------------------------B.支援任务----------------------------

        # ---------------------------B.支援任务   1.特殊任务----------------------------

        time.sleep(0.5)
        self.create_support_mission(name='飞机投送', point_list=[(20.4, -90.1), (22.5, -90.55)])
        Mission_7 = self.get_mission_by_name('飞机投送')
        unit_name_list = ['MQ-8C型 #1', 'MQ-8C型 #2', 'MQ-8C型 #3'] # 'MQ-8C型 #4', 'MQ-8C型 #5', 'MQ-8C型 #6'
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='飞机投送', unit_list=unit_guid_list)
        Mission_7.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_7.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_7.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_7.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_7.station_count(0)  # 为保持阵位的数量 0
        Mission_7.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_7.support_oneTimeOnly(True)  # 是否仅一次 不开启
        Mission_7.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_7.support_loopType(True)  # 导航类型 True-仅一次；False-连续循环
        Mission_7.support_throttle_transit(Throttle.Flank)  # 设置任务的飞机出航油门
        Mission_7.support_throttle_station(Throttle.Flank)  # 设置任务的阵位油门
        Mission_7.support_transitAltitude(99999.9)  #设置任务的飞机出航高度 float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_7.support_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符

        # ---------------------------B.支援任务   2.侦察任务----------------------------

        time.sleep(0.5)
        self.create_support_mission(name='黑鸟',
                                    point_list=[(19.10, -91.72), (17.83, -90.20), (15.91, -88.00),
                                                 (22.50, -88.12), (29.38, -93.46)])
        Mission_46 = self.get_mission_by_name('黑鸟')
        unit_name_list = ['SR-71(Bx) “黑鸟”侦察机 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='黑鸟', unit_list=unit_guid_list)
        Mission_46.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_46.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_46.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_46.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_46.station_count(0)  # 为保持阵位的数量 0
        Mission_46.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_46.support_oneTimeOnly(True)  # 是否仅一次 不开启
        Mission_46.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_46.support_loopType(True)  # 导航类型 True-仅一次；False-连续循环
        Mission_46.support_throttle_transit(Throttle.Flank)  # 设置任务的飞机出航油门
        Mission_46.support_throttle_station(Throttle.Flank)  # 设置任务的阵位油门
        Mission_46.support_transitAltitude(99999.9)  # 设置任务的飞机出航高度 float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_46.support_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符

        time.sleep(0.5)
        self.create_support_mission(name='左边侦察', point_list=[(20.38, -92.51), (20.37, -91.89)])
        Mission_12 = self.get_mission_by_name('左边侦察')
        unit_name_list = ['EP-3E型 #1', ]
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='左边侦察', unit_list=unit_guid_list)
        Mission_12.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_12.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_12.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_12.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_12.station_count(0)  # 为保持阵位的数量 0
        Mission_12.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_12.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_12.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_12.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_12.support_throttle_transit(Throttle.Flank)  # 设置任务的飞机出航油门
        Mission_12.support_throttle_station(Throttle.Flank)  # 设置任务的阵位油门
        Mission_12.support_transitAltitude(99999.9)  # 设置任务的飞机出航高度 float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_12.support_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符

        time.sleep(0.5)
        self.create_support_mission(name='右边侦察', point_list=[(21.96, -89.07), (21.79, -89.47)])
        Mission_13 = self.get_mission_by_name('右边侦察')
        unit_name_list = ['U-2S侦察机 #1', 'U-2S侦察机 #2', 'RC-135X型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='右边侦察', unit_list=unit_guid_list)
        Mission_13.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_13.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_13.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_13.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_13.station_count(0)  # 为保持阵位的数量 0
        Mission_13.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_13.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_13.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_13.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_13.support_throttle_transit(Throttle.Flank)  # 设置任务的飞机出航油门
        Mission_13.support_throttle_station(Throttle.Flank)  # 设置任务的阵位油门
        Mission_13.support_transitAltitude(99999.9)  # 设置任务的飞机出航高度 float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_13.support_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符

        # ---------------------------B.支援任务   3.加油任务----------------------------

        time.sleep(0.5)
        self.create_support_mission(name='加油专线1', point_list=[(18.53, -95.50), (18.54, -95.31)])
        Mission_23 = self.get_mission_by_name('加油专线1')
        unit_name_list = ['A330-200 MRTT型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='加油专线1', unit_list=unit_guid_list)
        Mission_23.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_23.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_23.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_23.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_23.station_count(0)  # 为保持阵位的数量 0
        Mission_23.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_23.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_23.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_23.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_23.support_throttle_transit(Throttle.Cruise)  # 设置任务的飞机出航油门
        Mission_23.support_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门
        Mission_23.support_transitAltitude(99999.9)  # 设置任务的飞机出航高度 float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_23.support_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符

        time.sleep(0.5)
        self.create_support_mission(name='加油专线2', point_list=[(20.73, -93.53), (20.73, -93.26)])
        Mission_42 = self.get_mission_by_name('加油专线2')
        unit_name_list = ['KC-135T型 #1', 'MQ-25A型“黄貂鱼”舰载无人加油机#1', 'MQ-25A型“黄貂鱼”舰载无人加油机#2']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='加油专线2', unit_list=unit_guid_list)
        Mission_42.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_42.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_42.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_42.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_42.station_count(0)  # 为保持阵位的数量 0
        Mission_42.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_42.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_42.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_42.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_42.support_throttle_transit(Throttle.Cruise)  # 设置任务的飞机出航油门
        Mission_42.support_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门
        Mission_42.support_transitAltitude(99999.9)  # 设置任务的飞机出航高度 float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_42.support_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符

        time.sleep(0.5)
        self.create_support_mission(name='加油专线3', point_list=[(21.6, -88.4), (21.6, -88.2)])
        Mission_43 = self.get_mission_by_name('加油专线3')
        unit_name_list = ['KC-46A型（M国） #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='加油专线3', unit_list=unit_guid_list)
        Mission_43.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_43.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_43.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_43.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_43.station_count(0)  # 为保持阵位的数量 0
        Mission_43.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_43.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_43.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_43.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_43.support_throttle_transit(Throttle.Cruise)  # 设置任务的飞机出航油门
        Mission_43.support_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门
        Mission_43.support_transitAltitude(99999.9)  # 设置任务的飞机出航高度 float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_43.support_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符

        time.sleep(0.5)
        self.create_support_mission(name='加油专线4', point_list=[(23.47, -84.56), (23.39, -84.50)])
        Mission_44 = self.get_mission_by_name('加油专线4')
        unit_name_list = ['KC-46A型（R国） #1', 'KC-767型 #1']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='加油专线4', unit_list=unit_guid_list)
        Mission_44.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_44.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_44.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_44.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_44.station_count(0)  # 为保持阵位的数量 0
        Mission_44.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_44.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_44.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_44.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_44.support_throttle_transit(Throttle.Cruise)  # 设置任务的飞机出航油门
        Mission_44.support_throttle_station(Throttle.Loiter)  # 设置任务的阵位油门
        Mission_44.support_transitAltitude(99999.9)  # 设置任务的飞机出航高度 float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        # Mission_44.support_stationAltitude(station_altitude)  # float, 阵位高度， 单位：米，最多6位字符

        # ---------------------------B.支援任务   4.舰船潜艇逃跑或进击任务----------------------------

        time.sleep(0.5)
        self.create_support_mission(name='右上海面后撤', point_list=[(25.4, -84.4), (26.0, -84.1)])
        Mission_28 = self.get_mission_by_name('右上海面后撤')
        unit_name_list = ['DDG 179“摩耶”号“摩耶”级驱逐舰', 'DD 119 “朝日”导弹驱逐舰', 'DDH 181型“日向机”直升机航空母舰 [16DDH 级]']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='右上海面后撤', unit_list=unit_guid_list)
        Mission_28.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_28.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_28.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_28.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_28.station_count(0)  # 为保持阵位的数量 0
        Mission_28.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_28.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_28.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_28.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_28.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_28.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_28.support_set_throttle_transit_submarine(Throttle.Flank)   # 设置潜艇出航油门
        Mission_28.support_set_throttle_station_submarine(Throttle.Flank)   #设置潜艇阵位油门

        time.sleep(0.5)
        self.create_support_mission(name='岛山潜艇', point_list=[(23.32, -85.58), (22.83, -85.57)])
        Mission_29 = self.get_mission_by_name('岛山潜艇')
        unit_name_list = ['SS 083 岛山安昌浩级常规动力潜艇']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='岛山潜艇', unit_list=unit_guid_list)
        unit_guid = None
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == 'SS 083 岛山安昌浩级常规动力潜艇':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.set_alt_manual(True)
                set_unit.switch_radar(False)
                set_unit.wra_firing_range(3677, WRA_WeaponTargetType.Subsurface_Contact_Unknown_Type, 0)
                set_unit.wra_firing_range(3677, WRA_WeaponTargetType.Submarine_Unspecified, 0)
        Mission_29.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_29.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_29.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_29.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_29.station_count(0)  # 为保持阵位的数量 0
        Mission_29.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_29.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_29.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_29.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_29.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_29.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_29.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_29.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        Mission_29.support_set_depth_transit_submarine(-250) # 设置潜艇出航潜深
        Mission_29.support_set_depth_station_submarine(-250) # 设置潜艇阵位潜深


        time.sleep(0.5)
        self.create_support_mission(name='苍龙潜艇', point_list=[(19.3, -80.8), (19.6, -80.0)])
        Mission_30 = self.get_mission_by_name('苍龙潜艇')
        unit_name_list = ['“苍龙”级潜艇']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='苍龙潜艇', unit_list=unit_guid_list)
        unit_guid = None
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == '“苍龙”级潜艇':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.set_alt_manual(True)
                set_unit.switch_radar(False)
        Mission_30.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_30.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_30.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_30.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_30.station_count(0)  # 为保持阵位的数量 0
        Mission_30.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_30.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_30.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_30.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_30.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_30.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_30.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_30.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门
        Mission_30.support_set_depth_transit_submarine(-280)  # 设置潜艇出航潜深
        Mission_30.support_set_depth_station_submarine(-280)  # 设置潜艇阵位潜深

        time.sleep(0.5)
        self.create_support_mission(name='世宗大王', point_list=[(20.7, -91.1), (21.2, -90.49)])
        Mission_31 = self.get_mission_by_name('世宗大王')
        unit_name_list = ['“世宗大王”号导弹驱逐舰[KDX-3]']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='世宗大王', unit_list=unit_guid_list)
        Mission_31.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_31.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_31.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_31.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_31.station_count(0)  # 为保持阵位的数量 0
        Mission_31.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_31.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_31.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_31.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_31.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_31.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_31.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_31.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        time.sleep(0.5)
        self.create_support_mission(name='独岛后撤', point_list=[(23.9, -90.4), (24.9, -90.4)])
        Mission_32 = self.get_mission_by_name('独岛后撤')
        start_time_str = '05/23/2090 13:10:00'  # 延迟后撤，否则无人机无法返航
        Mission_32.set_start(start_time_str)
        unit_name_list = ['“独岛”级两栖攻击舰']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='独岛后撤', unit_list=unit_guid_list)
        Mission_32.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_32.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_32.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_32.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_32.station_count(0)  # 为保持阵位的数量 0
        Mission_32.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_32.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_32.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_32.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_32.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_32.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_32.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_32.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        time.sleep(0.5)
        self.create_support_mission(name='玄武后撤', point_list=[(19.0, -99.3), (20.3, -100.5)])
        Mission_33 = self.get_mission_by_name('玄武后撤')
        unit_name_list = ['地地导弹营(“玄武-3B”型巡航导弹  运输-起竖-发射一体车)']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='玄武后撤', unit_list=unit_guid_list)
        Mission_33.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_33.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_33.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_33.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_33.station_count(0)  # 为保持阵位的数量 0
        Mission_33.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_33.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_33.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_33.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_33.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_33.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_33.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_33.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        time.sleep(0.5)
        self.create_support_mission(name='左海域撤退1', point_list=[(22.3, -107.5), (23.1, -107.8)])
        Mission_3 = self.get_mission_by_name('左海域撤退1')
        unit_name_list = ['CG 47 “提康德罗加号”提康德罗加级巡航舰 ', 'CVN 71“西奥多.罗斯福号”尼米兹级航空母舰']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='左海域撤退1', unit_list=unit_guid_list)
        Mission_3.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_3.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_3.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_3.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_3.station_count(0)  # 为保持阵位的数量 0
        Mission_3.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_3.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_3.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_3.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_3.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_3.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_3.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_3.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        time.sleep(0.5)
        self.create_support_mission(name='左海域撤退2', point_list=[(13.9, -113.15), (13.7, -114.5)])
        Mission_47 = self.get_mission_by_name('左海域撤退2')
        unit_name_list = ['DDG 1000 “朱姆沃尔特号”朱姆沃尔特级驱逐舰']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='左海域撤退2', unit_list=unit_guid_list)
        Mission_47.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_47.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_47.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_47.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_47.station_count(0)  # 为保持阵位的数量 0
        Mission_47.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_47.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_47.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_47.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_47.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_47.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_47.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_47.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        # ---------------------------B.支援任务   5.地面单位任务----------------------------

        time.sleep(0.5)
        self.create_support_mission(name='萨德', point_list=[(18.4, -96.4), (19.3, -96.4)])
        Mission_34 = self.get_mission_by_name('萨德')
        unit_name_list = ['SAM Bty (萨德 CEC)']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='萨德', unit_list=unit_guid_list)
        Mission_34.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_34.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_34.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_34.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_34.station_count(0)  # 为保持阵位的数量 0
        Mission_34.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_34.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_34.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_34.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_34.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_34.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_34.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_34.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        time.sleep(0.5)
        self.create_support_mission(name='天马绕机场', point_list=[(18.4, -95.4), (18.3, -95.15), (18.4, -95.13)])
        Mission_35 = self.get_mission_by_name('天马绕机场')
        unit_name_list = ['地空导弹中队(KM-SAM型中程地对空导弹系统 [“天马-2”中程地空导弹])']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='天马绕机场', unit_list=unit_guid_list)
        Mission_35.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_35.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_35.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_35.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_35.station_count(0)  # 为保持阵位的数量 0
        Mission_35.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_35.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_35.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_35.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_35.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_35.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_35.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_35.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        time.sleep(0.5)
        self.create_support_mission(name='反舰导弹车后撤', point_list=[(21.5, -82.9), (21.8, -82.9)])
        Mission_36 = self.get_mission_by_name('反舰导弹车后撤')
        unit_name_list = [' 地地导弹中队(SSM-1型岸对舰导弹 [88式]) ']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='反舰导弹车后撤', unit_list=unit_guid_list)
        Mission_36.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_36.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_36.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_36.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_36.station_count(0)  # 为保持阵位的数量 0
        Mission_36.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_36.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_36.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_36.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_36.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_36.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_36.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_36.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        time.sleep(0.5)
        self.create_support_mission(name='SAM绕机场', point_list=[(22.6, -81.5), (22.5, -81.5), (22.4, -81.7)])
        Mission_37 = self.get_mission_by_name('SAM绕机场')
        unit_name_list = ['地空导弹中队(SAM-4 Chu-SAM中程地空导弹[03型])']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='SAM绕机场', unit_list=unit_guid_list)
        Mission_37.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_37.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_37.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_37.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_37.station_count(0)  # 为保持阵位的数量 0
        Mission_37.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_37.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_37.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_37.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_37.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_37.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_37.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_37.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        time.sleep(0.5)
        self.create_support_mission(name='K9打坦克', point_list=[(16.7, -94.1), (16.4, -94.0)])
        Mission_38 = self.get_mission_by_name('K9打坦克')
        unit_name_list = ['炮兵中队(K-9型“雷电”155毫米自行榴弹炮 x 6) ']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='K9打坦克', unit_list=unit_guid_list)
        Mission_38.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_38.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_38.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_38.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_38.station_count(0)  # 为保持阵位的数量 0
        Mission_38.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_38.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_38.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_38.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_38.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_38.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_38.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_38.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        time.sleep(0.5)
        self.create_support_mission(name='爱国者绕机场', point_list=[(30.1, -94.1), (29.9, -94.3), (30.1, -94.4)])
        Mission_39 = self.get_mission_by_name('爱国者绕机场')
        unit_name_list = ['地空导弹中队(爱国者 [PAC-2 GEM+, PAC-3 ERINT/MSE型增程拦截导弹])']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict)
               and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='爱国者绕机场', unit_list=unit_guid_list)
        Mission_39.support_flightSize(FlightSize.One)  # 设置任务编队规模
        Mission_39.support_useFlightSize(True)  # 是否飞机数低于编队规模不允许起飞
        Mission_39.support_tanker_one_time(False)  # 支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        Mission_39.support_tanker_max_recv(0)  # 支援任务设置加油机可给飞机加油数
        Mission_39.station_count(0)  # 为保持阵位的数量 0
        Mission_39.set_one_third_rule(False)  # 三分之一规则 不开启
        Mission_39.support_oneTimeOnly(False)  # 是否仅一次 不开启
        Mission_39.support_activeEMCON(False)  # 仅在阵位上打开电磁辐射 True:打开, False:不打开  不开启
        Mission_39.support_loopType(False)  # 导航类型 True-仅一次；False-连续循环
        Mission_39.support_set_throttle_transit_ship(Throttle.Flank)  # 设置水面舰艇出航油门
        Mission_39.support_set_throttle_station_ship(Throttle.Flank)  # 设置任务的阵位油门
        Mission_39.support_set_throttle_transit_submarine(Throttle.Flank)  # 设置潜艇出航油门
        Mission_39.support_set_throttle_station_submarine(Throttle.Flank)  # 设置潜艇阵位油门

        # ---------------------------C.打击任务----------------------------

        # time.sleep(0.5)
        # self.Mission_25 = self.create_strike_mission('BIB反舰', MissionStrikeType.SHIP)
        # Mission_25 = self.get_mission_by_name('BIB反舰')
        # unit_name_list = []
        # unit_guid_list = [
        #     unit.get('guid', '') for unit in situation_data.values()
        #     if isinstance(unit, dict) and (unit.get('name', '') in unit_name_list)
        # ]
        # self.assign_units_to_mission(mission_name='BIB反舰', unit_list=unit_guid_list)
        # Mission_25.strike_setStrikeFlightSize(FlightSize.One) # 设置打击任务飞机编队规模
        # Mission_25.strike_setPreplan(True)  # 仅考虑任务目标
        # Mission_25.strike_setStrikeFuleAmmo(StrikeFuleAmmo.FAR_DIST)  # 在最远距离上投掷/抛弃还是带回空对地弹药
        # unit_guid = None
        # for unit in situation_data.values():
        #     if isinstance(unit, dict) and unit.get('name') == 'B-1B型 #1':
        #         unit_guid = unit.get('guid')
        #         break
        # if unit_guid:
        #     set_unit = self.get_unit(unit_guid)
        #     if set_unit:
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Surface_Contact_Unknown_Type, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Surface_Combatant_0_500_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Surface_Combatant_501_1500_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Surface_Combatant_5001_10000_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Surface_Combatant_10001_25000_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Surface_Combatant_25001_45000_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Surface_Combatant_45001_95000_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Surface_Combatant_95000_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Carrier_0_25000_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Carrier_25001_45000_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Carrier_45001_95000_tons, 8)
        #         set_unit.wra_qty_salvo(2378, WRA_WeaponTargetType.Ship_Carrier_95000_tons, 8)


        self.Mission_27 = self.create_strike_mission('机场防空', MissionStrikeType.AIR)
        Mission_27 = self.get_mission_by_name('机场防空')
        unit_name_list = ['H国单实体机场 (3x 4000m+ 跑道)', 'R国单实体机场 (4x 4000m+ 跑道)',
                          'M国单实体机场 (4x 4000m+ 跑道)', 'M国海外机场 (2x 1401-2000m 跑道)']
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict) and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='机场防空', unit_list=unit_guid_list)
        Mission_27.strike_setStrikeFlightSize(FlightSize.One)  # 设置打击任务飞机编队规模
        Mission_27.strike_setPreplan(False)  # 仅考虑任务目标
        Mission_27.strike_setStrikeFuleAmmo(StrikeFuleAmmo.FAR_DIST)  # 在最远距离上投掷/抛弃还是带回空对地弹药

        self.Mission_40 = self.create_strike_mission('戈尔必沉', MissionStrikeType.SHIP)
        Mission_40 = self.get_mission_by_name('戈尔必沉')
        unit_name_list = ['F-2A型 #1'] #, 'F-2A型 #2', 'F-2A型 #3'
        unit_guid_list = [
            unit.get('guid', '') for unit in situation_data.values()
            if isinstance(unit, dict) and (unit.get('name', '') in unit_name_list)
        ]
        self.assign_units_to_mission(mission_name='戈尔必沉', unit_list=unit_guid_list)
        Mission_40.strike_setStrikeFlightSize(FlightSize.One)  # 设置打击任务飞机编队规模
        Mission_40.strike_setPreplan(True)  # 仅考虑任务目标
        Mission_40.strike_setStrikeFuleAmmo(StrikeFuleAmmo.FAR_DIST)  # 在最远距离上投掷/抛弃还是带回空对地弹药
        unit_guid = None
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == 'F-2A型 #1':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Surface_Contact_Unknown_Type, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_0_500_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_501_1500_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_5001_10000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_10001_25000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_25001_45000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_45001_95000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_95000_tons, 4)
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == 'F-2A型 #2':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Surface_Contact_Unknown_Type, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_0_500_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_501_1500_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_5001_10000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_10001_25000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_25001_45000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_45001_95000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_95000_tons, 4)
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == 'F-2A型 #3':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Surface_Contact_Unknown_Type, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_0_500_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_501_1500_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_5001_10000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_10001_25000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_25001_45000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_45001_95000_tons, 4)
                set_unit.wra_qty_salvo(722, WRA_WeaponTargetType.Ship_Surface_Combatant_95000_tons, 4)

        # ----------------------------D.其余条令------------------------------

        time.sleep(0.5)
        unit_guid = None
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == 'DD 119 “朝日”导弹驱逐舰':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.wra_qty_salvo(1575, WRA_WeaponTargetType.Ship_Merchant_Civilian_0_500_tons, 1)
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == '地地导弹营(“玄武-3B”型巡航导弹  运输-起竖-发射一体车)':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.doctrine_engage_opportunity_targets(EngageWithContactTarget.Yes_AnyTarget) # 攻击任何目标
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == ' 地地导弹中队(SSM-1型岸对舰导弹 [88式]) ':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.doctrine_engage_opportunity_targets(EngageWithContactTarget.Yes_AnyTarget)
                set_unit.wra_qty_salvo(1576, WRA_WeaponTargetType.Surface_Contact_Unknown_Type, 18)
                set_unit.wra_qty_salvo(1576, WRA_WeaponTargetType.Ship_Surface_Combatant_0_500_tons, 18)
                set_unit.wra_qty_salvo(1576, WRA_WeaponTargetType.Ship_Surface_Combatant_501_1500_tons, 18)
                set_unit.wra_qty_salvo(1576, WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons, 18)
                set_unit.wra_qty_salvo(1576, WRA_WeaponTargetType.Ship_Surface_Combatant_5001_10000_tons, 18)
                set_unit.wra_qty_salvo(1576, WRA_WeaponTargetType.Ship_Surface_Combatant_10001_25000_tons, 18)
                set_unit.wra_qty_salvo(1576, WRA_WeaponTargetType.Ship_Surface_Combatant_25001_45000_tons, 18)
                set_unit.wra_qty_salvo(1576, WRA_WeaponTargetType.Ship_Surface_Combatant_45001_95000_tons, 18)
                set_unit.wra_qty_salvo(1576, WRA_WeaponTargetType.Ship_Surface_Combatant_95000_tons, 18)
        for unit in situation_data.values():
            if isinstance(unit, dict) and unit.get('name') == '地空导弹中队(SAM-4 Chu-SAM中程地空导弹[03型])':
                unit_guid = unit.get('guid')
                break
        if unit_guid:
            set_unit = self.get_unit(unit_guid)
            if set_unit:
                set_unit.doctrine_engage_opportunity_targets(EngageWithContactTarget.Yes_AnyTarget) # 攻击任何目标





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






