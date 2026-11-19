# -*- coding:utf-8 -*-
# Description: 支援任务

from .global_util import *
from .mission_common import MissionCommon


class SupportMission(MissionCommon):
    """
    支援任务  
    1、三分之一规则  
    2、阵位上每类平台保持几个  
    3、仅一次  
    4、仅在阵位上打开电磁辐射  
    5、导航类型  
    6、编队规模  
    7、是否飞机数低于编队规模不允许起飞  
    8、设置任务的飞机出航油门  
    9、设置任务的飞机阵位油门  
    10、设置任务的飞机出航高度  
    11、设置任务的阵位高度  
    12、支援任务区域按顺序排列的参考点名  
    13、支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场  
    14、支援任务设置加油机可给飞机加油数  
    15、设置任务所需最少飞机数  
    16、设置任务舰船/潜艇编队规模  
    17、是否舰船/潜艇数低于编队规模不允许出发  
    18、设置飞机出航地形跟随  
    19、设置飞机阵地地形跟随  
    20、设置潜艇出航油门  
    21、设置潜艇出航潜深  
    22、设置潜艇阵位潜深  
    23、设置潜艇阵位油门  
    24、设置水面舰艇出航油门  
    25、设置水面舰艇阵位油门  

    示例：    
     self.YiEr_78_support = self.create_support_mission("YiEr_78_support", [(15.1, -88.6), (14.4, -87.4)])  #创建支援任务  
     YiEr_78_support = self.get_mission_by_name('YiEr_78_support')   # 通过任务名字 获取支援任务对象  
     unit_list = ['fsl-fsjdlf2-dfs', 'pgjdlg-sfl2-sfls']  # 单元id列表  
     self.assign_units_to_mission(mission_name='Y78_patrol', unit_list=unit_guid_list) #将多个单元分配给支援任务  
     YiEr_78_support.support_flightSize(FlightSize.One)  # 设置支援任务的编队规模  
    """
    def __init__(self, guid, name, side_name):
        MissionCommon.__init__(self, guid, name, side_name, ElementType.SupportMission)
        self.Type = 0  # 支援任务无任务子类型
        self.Area = []  # 支援航线--参考点guid列表
        self.NLT = 0  # 支援任务导航循环类型
        self.OTR = False  # 三分之一规则
        self.MNOS = 0  # 阵位上的最小数量
        self.OTO = False  # 仅限一次性 OneTimeOnly
        self.AEOOS = False  # 仅在阵位上激活电磁辐射控制 ActiveEMCONOnlyOnStation
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
        self.A2ARMaxNumberOfReceiversPerTanker = 0  # 空中加油_每艘油轮的最大接收器数量
        self.A2AROneTankingCycleOnly = False  # 空中加油_仅限一个油轮循环
        self.MinAircraftReq = 0  # 最小飞机数量
        self.ContinousCoverageEnable = False  # 连续覆盖启用
        self.ContinousCoverageAllowQRA = False  # 连续覆盖_QRA启用
        self.ContinousCoverageFlightGenerationMethod = 0  # 连续覆盖_航班方法
        self.ContinousCoverageStationTime = 0  # 连续覆盖_阵位时间
        self.ContinousCoverageOverlap = 0  # 连续覆盖_重叠
        self.ContinousCoverageDuration = 0  # 连续覆盖_持续时间
        self.CCSList = []  # 连续覆盖_阵位--THCCS列表
        self.QRAs = []  # 连续覆盖_QRA--THCCS列表
        self.ContinousCoverageQRANumberOfFlights = 0  # 连续覆盖_QRA航班数量
        self.ContinousCoverageQRAFlightGenerationMethod = 0  # 连续覆盖_QRA航班方法
        self.ContinousCoverageNumberOfFlightsNeededToAllowQRA = 0  # 连续覆盖_允许QRA所需的航班数量

    def set_one_third_rule(self, one_third):
        """
        1、三分之一规则
        :param one_third: bool, True,设置三分之一规则  False:不遵守三分之一规则
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "oneThirdRule=%s" % str(one_third).lower()
        return self._set(str_set)

    def station_count(self, station_count):
        """
        2、阵位上每类平台保持几个
        :param station_count: int, 保持阵位的数量
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "onStation=%d" % station_count
        return self._set(str_set)

    def support_oneTimeOnly(self, isoneTimeOnly):
        """
        3、仅一次
        :param isoneTimeOnly: bool, 是否仅一次
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "oneTimeOnly=%s" % str(isoneTimeOnly).lower()
        return self._set(str_set)

    def support_activeEMCON(self, isactiveEMCON):
        """
        4、仅在阵位上打开电磁辐射
        :param isactiveEMCON: bool, True:打开, False:不打开
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "activeEMCON=%s" % str(isactiveEMCON).lower()
        return self._set(str_set)

    def support_loopType(self, single_loop):
        """
        5、导航类型
        :param single_loop: bool, True-仅一次；False-连续循环
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if single_loop:
            str_set = "loopType=1"
        else:
            str_set = "loopType=0"
        return self._set(str_set)

    def support_flightSize(self, enum_flightSize):
        """
        6、编队规模
        :param enum_flightSize: FlightSize枚举值, 编队规模，global_util.py中定义，例：FlightSize.Two：双机编队
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "flightSize=%d" % enum_flightSize.value
        return self._set(str_set)

    def support_useFlightSize(self, useFlightSize):
        """
        7、是否飞机数低于编队规模不允许起飞
        :param useFlightSize: bool, True:是
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "useFlightSize=%s" % str(useFlightSize).lower()
        return self._set(str_set)

    def support_throttle_transit(self, enum_throttle):
        """
        8、设置任务的飞机出航油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义，例：Throttle.Cruise: 巡航油门
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "transitThrottleAircraft='Unspecified'"
        else:
            str_set = "transitThrottleAircraft=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def support_throttle_station(self, enum_throttle):
        """
        9、设置任务的飞机阵位油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义，例：Throttle.Cruise: 巡航油门
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "stationThrottleAircraft='Unspecified'"
        else:
            str_set = "stationThrottleAircraft=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def support_transitAltitude(self, transitAltitude):
        """
        10、设置任务的飞机出航高度
        :param transitAltitude: float, 出航高度， 单位：米，最多6位字符，例：99999.9， 888888
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "transitAltitudeAircraft=%.2lf" % transitAltitude
        return self._set(str_set)

    def support_stationAltitude(self, stationAltitude):
        """
        11、设置任务的阵位高度
        :param stationAltitude: float, 阵位高度， 单位：米，最多6位字符
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "StationAltitudeAircraft=%.2lf" % stationAltitude
        return self._set(str_set)

    def support_set_zone(self, Zone):
        """
        12、支援任务区域按顺序排列的参考点名
        :param Zone: 参考点列表, list,
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "Zone=%s" % (str(Zone).replace("[", "{").replace("]", "}"))
        return self._set(str_set)

    def support_tanker_one_time(self, tanker_one_time):
        """
        13、支援任务设置一个加油周期后，加油队列为空时，加油机返回起降机场
        :param tanker_one_time:  bool
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "tankerOneTime=%s" % str(tanker_one_time).lower()
        return self._set(str_set)

    def support_tanker_max_recv(self, tanker_max_recv):
        """
        14、支援任务设置加油机可给飞机加油数
        :param tanker_max_recv: int，最多受油机数
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "tankerMaxReceivers=%d" % tanker_max_recv
        return self._set(str_set)

    def support_minaircraft(self, min_aircraft):
        """
        15、设置任务所需最少飞机数
        :param min_aircraft:枚举MinAircraftReq的值, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "minAircraftReq=%d" % min_aircraft.value
        return self._set(str_set)

    def support_ship_size(self, ship_size):
        """
        16、设置任务舰船/潜艇编队规模
        :param ship_size:枚举GroupSize的值, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "groupSize=%d" % ship_size.value
        return self._set(str_set)

    def support_use_group_size(self, use_group_size):
        """
        17、是否舰船/潜艇数低于编队规模不允许出发
        :param use_group_size: bool, True:是
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "useGroupSize=%s" % str(use_group_size).lower()
        return self._set(str_set)

    def support_set_transit_terrain_following(self, transit_terrain):
        """
        18、设置飞机出航地形跟随
        :param transit_terrain: bool
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "TransitTerrainFollowingAircraft=%s" % str(transit_terrain).lower()
        return self._set(str_set)

    def support_set_station_terrain_following(self, station_terrain):
        """
        19、设置飞机阵地地形跟随
        :param station_terrain: bool
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "stationTerrainFollowingAircraft=%s" % str(station_terrain).lower()
        return self._set(str_set)

    def support_set_throttle_transit_submarine(self, enum_throttle):
        """
        20、设置潜艇出航油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义，例：Throttle.Cruise: 巡航油门
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "transitThrottleSubmarine='Unspecified'"
        else:
            str_set = "transitThrottleSubmarine=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def support_set_depth_transit_submarine(self, depth_value):
        """
        21、设置潜艇出航潜深
        :param depth_value: float,  出潜深度， 米, 海拔高度，需传递负值,例：-150.5
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "transitDepthSubmarine=%.2lf" % depth_value
        return self._set(str_set)

    def support_set_depth_station_submarine(self, depth_value):
        """
        22、设置潜艇阵位潜深
        :param depth_value: float, 阵位潜深， 米, 海拔高度，需传递负值,例：-150.5
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "stationDepthSubmarine=%.2lf" % depth_value
        return self._set(str_set)

    def support_set_throttle_station_submarine(self, enum_throttle):
        """
        23、设置潜艇阵位油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义，例：Throttle.Cruise: 巡航油门
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "stationThrottleSubmarine='Unspecified'"
        else:
            str_set = "stationThrottleSubmarine=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def support_set_throttle_transit_ship(self, enum_throttle):
        """
        24、设置水面舰艇出航油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义，例：Throttle.Cruise: 巡航油门
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "transitThrottleShip='Unspecified'"
        else:
            str_set = "transitThrottleShip=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def support_set_throttle_station_ship(self, enum_throttle):
        """
        25、设置水面舰艇阵位油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义，例：Throttle.Cruise: 巡航油门
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "stationThrottleShip='Unspecified'"
        else:
            str_set = "stationThrottleShip=%d" % (enum_throttle.value - 1)
        return self._set(str_set)


