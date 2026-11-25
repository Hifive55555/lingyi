# -*- coding:utf-8 -*-
# Description: 排雷任务

from .global_util import *
from .mission_common import MissionCommon


class MineClearMission(MissionCommon):
    """
    排雷任务类  
    1、三分之一规则  
    2、设置任务编队规模  
    3、是否飞机数低于编队规模不允许起飞  
    4、设置任务舰船/潜艇编队规模  
    5、是否舰船/潜艇数低于编队规模不允许出发  
    6、设置清雷任务所需最少飞机数  
    7、设置任务的出航油门  
    8、设置任务的阵位油门  
    9、设置任务的出航高度  
    10、设置任务的阵位高度  
    11、设置出航地形跟随  
    12、阵地地形跟随  
    13、设置排雷任务的区域，按顺序排列的参考点名  

    示例：  
    mission = self.get_mission_by_name('mineclear_mission')   # 通过排雷任务的名字  获取排雷任务对象  
    mission.set_one_third_rule(True)  # 三分之一规则 开启  
    mission.set_start('05/24/2014 16:05:00')  # 设置任务开始时间 mission.py中接口  
    """
    def __init__(self, guid, name, side_name):
        MissionCommon.__init__(self, guid, name, side_name, ElementType.MineClearMission)
        self.Type = 0  # 任务子类型(无）
        self.Area = []  # 排雷区域--参考点guid列表
        self.OTR = False  # OneThirdRule
        self.TransitThrottleAircraft = 0  # 运输油门_飞机
        self.StationThrottleAircraft = 0  # 阵位油门_飞机
        self.TransitAltitudeAircraft = 0.0  # 运输高度_飞机
        self.StationAltitudeAircraft = 0.0  # 阵位高度_飞机
        self.TransitTerrainFollowingAircraft = False  # 运输地形跟随_飞机
        self.StationTerrainFollowingAircraft = False  # 阵位地形跟随_飞机
        self.TransitThrottleSubmarine = 0  # 运输油门_潜艇
        self.StationThrottleSubmarine = 0  # 阵位油门_潜艇
        self.TransitDepthSubmarine = 0.0  # 9999表示无设置  // 运输深度_潜艇
        self.StationDepthSubmarine = 0.0  # 阵位深度_潜艇
        self.TransitThrottleShip = 0  # 运输油门_舰船
        self.StationThrottleShip = 0  # 阵位油门_舰船
        self.TransitThrottleFacility = 0  # 运输油门_设施
        self.StationThrottleFacility = 0  # 阵位油门_设施
        self.FormationCruise = 0  # 巡航队形
        self.FormationAttack = 0  # 攻击队形
        self.MinAircraftReq = 0  # 最小飞机数量

    def set_one_third_rule(self, one_third):
        """
        1、三分之一规则
        :param one_third: bool, True,设置三分之一规则  False:不遵守三分之一规则
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "oneThirdRule=%s" % (str(one_third).lower())
        return self._set(str_set)

    def set_flight_size(self, enum_flight_size):
        """
        2、设置任务编队规模
        :param enum_flight_size:FlightSize, 编队规模, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "flightSize=%d" % enum_flight_size.value
        return self._set(str_set)

    def use_flight_size(self, use_flight_size):
        """
        3、是否飞机数低于编队规模不允许起飞
        :param use_flight_size: bool, True:是
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "useFlightSize=%s" % str(use_flight_size).lower()
        return self._set(str_set)

    def set_group_size(self, enum_group_size):
        """
        4、设置任务舰船/潜艇编队规模
        :param enum_group_size:GroupSize枚举值, 舰船/潜艇编队规模, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "groupSize=%d" % enum_group_size.value
        return self._set(str_set)

    def use_group_size(self, use_group_size):
        """
        5、是否舰船/潜艇数低于编队规模不允许出发
        :param use_group_size: bool, True:是
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "useGroupSize=%s" % str(use_group_size).lower()
        return self._set(str_set)

    def set_minaircraft(self, min_aircraft):
        """
        6、设置清雷任务所需最少飞机数
        :param min_aircraft:枚举MinAircraftReq的值, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "minaircraftreq=%d" % min_aircraft.value
        return self._set(str_set)

    def set_transit_throttle(self, enum_throttle, unit_category=ElementType.Aircraft):
        """
        7、设置任务的出航油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义
        :param unit_category:ElementType.Aircraft, or ElementType.Ship, or ElementType.Submarine
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if unit_category == ElementType.Aircraft:
            if enum_throttle.value == 0:
                str_set = "transitThrottleAircraft='Unspecified'"
            else:
                str_set = "transitThrottleAircraft=%d" % (enum_throttle.value-1)
        elif unit_category == ElementType.Ship:
            if enum_throttle.value == 0:
                str_set = "transitThrottleShip='Unspecified'"
            else:
                str_set = "transitThrottleShip=%d" % (enum_throttle.value-1)
        elif unit_category == ElementType.Submarine:
            if enum_throttle.value == 0:
                str_set = "transitThrottleSubmarine='Unspecified'"
            else:
                str_set = "transitThrottleSubmarine=%d" % (enum_throttle.value-1)
        else:
            raise ValueError("parameter unit_category value error")
        return self._set(str_set)

    def set_station_throttle(self, enum_throttle, unit_category=ElementType.Aircraft):
        """
        8、设置任务的阵位油门
        :param enum_throttle: 枚举Throttle的值, 油门, global_util.py中定义
        :param unit_category:ElementType.Aircraft, or ElementType.Ship, or ElementType.Submarine
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if unit_category == ElementType.Aircraft:
            if enum_throttle.value == 0:
                str_set = "stationThrottleAircraft='Unspecified'"
            else:
                str_set = "stationThrottleAircraft=%d" % (enum_throttle.value-1)
        elif unit_category == ElementType.Ship:
            if enum_throttle.value == 0:
                str_set = "stationThrottleShip='Unspecified'"
            else:
                str_set = "stationThrottleShip=%d" % (enum_throttle.value-1)
        elif unit_category == ElementType.Submarine:
            if enum_throttle.value == 0:
                str_set = "stationThrottleSubmarine='Unspecified'"
            else:
                str_set = "stationThrottleSubmarine=%d" % (enum_throttle.value-1)
        else:
            raise ValueError("parameter unit_category value error")
        return self._set(str_set)

    def set_transit_alt(self, altitude_value, is_submarine=False):
        """
        9、设置任务的出航高度
        :param altitude_value: float, 出航高度， 单位：米，海拔高度，飞机需正值，例:500; 潜艇需传递负值，例：-150
        :param is_submarine: bool, 是否出潜深度
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if is_submarine:
            str_set = "transitDepthSubmarine=%.1lf" % altitude_value
        else:
            str_set = "transitAltitudeAircraft=%.1lf" % altitude_value
        return self._set(str_set)

    def set_station_altitude(self, altitude_value, is_submarine=False):
        """
        10、设置任务的阵位高度
        :param altitude_value: float, 阵位高度， 单位：米，海拔高度，飞机需正值，例:500; 潜艇需传递负值，例：-150
        :param is_submarine: bool, 是否出潜深度
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if is_submarine:
            str_set = "stationDepthSubmarine=%.1lf" % altitude_value
        else:
            str_set = "stationAltitudeAircraft=%.1lf" % altitude_value
        return self._set(str_set)

    def set_transit_terrain_following(self, transit_terrain):
        """
        11、设置出航地形跟随
        :param transit_terrain: bool
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "TransitTerrainFollowingAircraft=%s" % str(transit_terrain).lower()
        return self._set(str_set)

    def set_station_terrain_following(self, station_terrain):
        """
        12、阵地地形跟随
        :param station_terrain: bool
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "stationTerrainFollowingAircraft=%s" % str(station_terrain).lower()
        return self._set(str_set)

    def mine_clear_set_zone(self, Zone):
        """
        13、设置排雷任务的区域，按顺序排列的参考点名
        :param Zone: 参考点列表, list,
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "Zone=%s" % (str(Zone).replace("[", "{").replace("]", "}"))
        return self._set(str_set)
