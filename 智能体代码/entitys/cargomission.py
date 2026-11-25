# -*- coding:utf-8 -*-
# Description: 货运任务

from .global_util import *
from .mission import Mission


class CargoMission(Mission):
    """
    货运任务类  
    1、设置任务的出航油门  
    2、设置任务的阵位油门  
    3、设置任务的出航高度  
    4、设置任务的阵位高度  
    5、设置运送货物DBIB和数量  
    6、货运任务区域按顺序排列的参考点名  

    示例:  
    mission = self.get_mission_by_name('cargeo')   # 通过货运任务的名字  获取货运任务对象  
    mission.set_transit_throttle(Throttle.Cruise)  # 设置出航油门为巡航  
    mission.set_unload_mount(65, 5)  # 设置货运任务运输DBID为65的货物（萨姆10B车），数量为5
    """
    def __init__(self, guid, name, side_name):
        Mission.__init__(self, guid, name, side_name, ElementType.CargoMission)
        # 结构THMissionCargo中属性： 货运任务
        self.Type = 0  # 货运任务类型 参考ECargoMissionType定义
        self.TransitThrottleAircraft = 0  # 运输油门_飞机
        self.StationThrottleAircraft = 0  # 阵位油门_飞机
        self.TransitAltitudeAircraft = 0.0  # 运输高度_飞机
        self.StationAltitudeAircraft = 0.0  # 阵位高度_飞机
        self.TransitThrottleShip = 0  # 运输油门_舰艇
        self.StationThrottleShip = 0  # 阵位油门_舰艇
        self.Area = []  # 投送区域--参考点guid列表
        self.MountsToUnload = {}  # 卸载的货物---结构：dict<int32, int32>，key:货物类型，value：数量

    def set_transit_throttle(self, enum_throttle, unit_category=ElementType.Aircraft):
        """
        1、设置任务的出航油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义
        :param unit_category:ElementType.Aircraft, or ElementType.Ship, or ElementType.Submarine
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if unit_category == ElementType.Aircraft:
            str_set = "transitThrottleAircraft=%d" % (enum_throttle.value-1)
        elif unit_category == ElementType.Ship:
            str_set = "transitThrottleShip=%d" % (enum_throttle.value-1)
        elif unit_category == ElementType.Submarine:
            str_set = "transitThrottleSubmarine=%d" % (enum_throttle.value-1)
        else:
            raise ValueError("parameter unit_category value error")
        return self._set(str_set)

    def set_station_throttle(self, enum_throttle, unit_category=ElementType.Aircraft):
        """
        2、设置任务的阵位油门
        :param enum_throttle: 枚举Throttle的值, 油门, global_util.py中定义
        :param unit_category:ElementType.Aircraft, or ElementType.Ship, or ElementType.Submarine
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if unit_category == ElementType.Aircraft:
            str_set = "stationThrottleAircraft=%d" % (enum_throttle.value-1)
        elif unit_category == ElementType.Ship:
            str_set = "stationThrottleShip=%d" % (enum_throttle.value-1)
        elif unit_category == ElementType.Submarine:
            str_set = "stationThrottleSubmarine=%d" % (enum_throttle.value-1)
        else:
            raise ValueError("parameter unit_category value error")
        return self._set(str_set)

    def set_transit_alt(self, altitude_value):
        """
        3、设置任务的出航高度
        :param altitude_value: float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "transitAltitudeAircraft=%.1lf" % altitude_value
        return self._set(str_set)

    def set_station_altitude(self, altitude_value):
        """
        4、设置任务的阵位高度
        :param altitude_value: float, 阵位高度， 单位：米，最多6位字符
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "stationAltitudeAircraft=%.1lf" % altitude_value
        return self._set(str_set)

    def set_unload_mount(self, unload_mount_dbid, unload_mount_count):
        """
        5、设置货运任务中基地中转移货物DBIB与数量
        :param unload_mount_dbid: int, 货运任务中转移货物DBIB
        :param unload_mount_count: int, 货运任务中转移货物的数量
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "unloadMountDBID=%d,unloadMountCount=%d" % (unload_mount_dbid, unload_mount_count)
        return self._set(str_set)

    def cargo_set_zone(self, Zone):
        """
        6、货运任务区域按顺序排列的参考点名
        :param Zone: list， 参考点名列表
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "Zone=%s" % (str(Zone).replace("[", "{").replace("]", "}"))
        return self._set(str_set)
