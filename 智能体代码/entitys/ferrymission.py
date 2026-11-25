# -*- coding:utf-8 -*-
# Description: 转场任务

from .global_util import *
from .mission_common import MissionCommon


class FerryMission(MissionCommon):
    """
    转场任务类  
    1、设置转场规则  
    2、设置任务编队规模  
    3、是否飞机数低于编队规模不允许起飞  
    4、设置任务所需最少飞机数  
    5、飞机转场油门  
    6、飞机转场高度  
    7、潜艇转场深度  
    8、设置转场地形跟随  
    9、舰艇转场油门  
    10、潜艇转场油门  

    示例：  
    mission = self.get_mission_by_name('ferry1')   # 通过转场任务的名字，获取任务对象  
    mission.set_flight_size(FlightSize.One)  # 设置任务编队规模  
    mission.set_start('05/24/2014 16:05:00')  # 设置任务开始时间 mission.py中接口  
    """
    def __init__(self, guid, name, side_name):
        MissionCommon.__init__(self, guid, name, side_name, ElementType.FerryMission)
        self.Type = 0  # 转场任务无任务子类型
        self.NDH = ""  # 转场任务目的地（机场或航母）ID mDestinationHostID
        self.FerryThrottleAircraft = 0  # 转场油门_飞机
        self.FerryAltitudeAircraft = 0.0  # 转场高度_飞机
        self.FerryTerrainFollowingAircraft = False  # 转场地形跟随_飞机
        self.FerryThrottleShip = 0  # 转场油门_舰艇
        self.FerryThrottleSubmarine = 0  # 转场油门_潜艇
        self.FerryAltitudeSubmarine = 0.0  # 转场高度_潜艇
        self.FormationCruise = 0  # 队形_巡航
        self.MinAircraftReq = 0.0  # 最小飞机数量
        self.Behavior = 0  # 转场任务行为

    def set_behavior(self, ferry_behavior):
        """
        1、设置转场规则，传入参数时需要用枚举值。
        :param ferry_behavior: FerryBehavior，转场模式，global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "ferryBehavior='%s'" % str(ferry_behavior.value)
        return self._set(str_set)

    def set_flight_size(self, enum_flight_size):
        """
        2、设置任务编队规模，传入参数时需要用枚举值。
        :param enum_flight_size:FlightSize, 编队规模，global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "flightSize=%s" % str(enum_flight_size.value)
        return self._set(str_set)

    def use_flight_size(self, use_flight_size):
        """
        3、是否飞机数低于编队规模不允许起飞
        :param use_flight_size: bool, True:是
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "useFlightSize=%s" % str(use_flight_size).lower()
        return self._set(str_set)

    def set_minaircraft(self, min_aircraft):
        """
        4、设置任务所需最少飞机数，传入参数时需要用枚举值。
        :param min_aircraft: 枚举MinAircraftReq的值, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "minaircraftreq=%d" % min_aircraft.value
        return self._set(str_set)

    def set_aircraft_throttle(self, enum_throttle):
        """
        5、飞机转场油门，传入参数时需要用枚举值。
        :param enum_throttle: 枚举Throttle的值, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "FerryThrottleAircraft='Unspecified'"
        else:
            str_set = "FerryThrottleAircraft=%d" % (enum_throttle.value-1)
        return self._set(str_set)

    def set_aircraft_alt(self, alt):
        """
        6、飞机转场高度
        :param alt: int 米
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "ferryAltitudeAircraft=%.1lf" % alt
        return self._set(str_set)

    def set_submarine_alt(self, alt):
        """
        7、潜艇转场深度
        :param alt: float, 米, 海拔高度，需传递负值,例：-100
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "FerryAltitudeSubmarine=%.11f" % alt
        return self._set(str_set)

    def set_ferry_terrain_following(self, terrain_follow):
        """
        8、设置转场地形跟随
        :param terrain_follow: bool
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "ferryTerrainFollowingAircraft=%s" % str(terrain_follow).lower()
        return self._set(str_set)

    def set_ship_throttle(self, enum_throttle):
        """
        9、舰艇转场油门
        :param enum_throttle: Throttle, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "FerryThrottleShip='Unspecified'"
        else:
            str_set = "FerryThrottleShip=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def set_submarine_throttle(self, enum_throttle):
        """
        10、潜艇转场油门
        :param enum_throttle: Throttle, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "FerryThrottleSubmarine='Unspecified'"
        else:
            str_set = "FerryThrottleSubmarine=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

