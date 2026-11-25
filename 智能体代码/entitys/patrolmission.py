# -*- coding:utf-8 -*-
# Description: 巡逻任务

from .global_util import *
from .mission_common import MissionCommon


class PatrolMission(MissionCommon):
    def __init__(self, guid, name, side_name):
        """
        巡逻任务类  
        1、三分之一规则  
        2、巡逻任务阵位上每类平台保存作战单元数量  
        3、设置任务是否对巡逻区外的探测目标进行分析  
        4、设置任务是否仅在巡逻任务警戒区内打开电磁辐射  
        5、设置任务是否对武器射程内探测目标进行分析  
        6、设置任务编队规模  
        7、是否飞机数低于编队规模不允许起飞  
        8、设置任务的飞机出航油门  
        9、设置任务的飞机阵位油门  
        10、设置任务的飞机攻击油门  
        11、设置任务的飞机出航高度  
        12、设置任务的飞机阵位高度  
        13、设置任务的飞机攻击高度  
        14、设置任务的飞机攻击距离, 需整数  
        15、设置巡逻区  
        16、设置巡逻任务警戒区
        17、设置任务所需最少飞机数
        18、设置任务舰船/潜艇编队大小
        19、强制舰船/潜艇编队大小
        20、飞机出航地形跟随
        21、飞机阵位地形跟随
        22、潜艇出航油门
        23、潜艇阵位油门
        24、潜艇出航潜深
        25、潜艇阵位潜深
        26、水面舰艇出航油门
        27、水面舰艇阵位油门
        28、攻击飞机地形跟随
        29、潜艇攻击油门
        30、潜艇攻击潜深
        31、潜艇攻击距离
        32、水面舰艇攻击油门
        33、水面舰艇攻击距离
        34、动作风格设置
        35、侦查不明目标飞机数量
        36、敌方对抗的飞机数量
        37、飞机设置  僚机可以在xx范围内侦察/交战   海里
        38、舰船/潜艇设置   侦查不明目标舰船数量
        39、舰船/潜艇设置  与敌方交火的舰船数量
        40、舰船/潜艇设置 编组成员可以在--范围内侦察/交战   海里

        示例：  
        patrol_mission = self.get_mission_by_name('patrol_mission1')   # 通过巡航任务的名字  获取巡航任务对象  
        patrol_mission.set_one_third_rule(True)  # 三分之一规则 开启  
        mission.set_start('05/24/2014 16:05:00')  # 设置任务开始时间 mission.py中接口  
        mission.set_mission_tankerMinNumber_airborne(2)  # 设置空中油轮最低数量 mission_common.py中接口  
        """
        MissionCommon.__init__(self, guid, name, side_name, ElementType.PatrolMission)
        self.Type = 0  # 任务子类型  值含义如下：
        """
        0: ASW,//反潜作战巡逻
        1: ASuW_Naval,//反水面战巡逻（海军）
        2: AAW,//防空作战巡逻
        3: ASuW_Land,//反水面战巡逻（陆地）
        4: ASuW_Mixed,//反水面战巡逻（混合）
        5: SEAD,//防空压制巡逻
        6: SeaControl//海上控制巡逻
        """
        self.PatrolArea = []  # 巡逻区域--参考点guid列表
        self.ProsecutionArea = []  # 警戒区域--参考点guid列表
        self.OTR = False  # 三分之一规则
        self.MNOS = 0  # 阵位上的最小数量
        self.IOPA = False  # 侦查巡逻区外
        self.IWWR = False  # 侦查武器范围内
        self.AEOIPA = False  # 仅在巡逻区或警戒区域内激活电磁辐射控制
        self.SAD = False  # 冲刺和漂移
        self.TransitThrottleAircraft = 0  # 运输油门_飞机
        self.StationThrottleAircraft = 0  # 阵位油门_飞机
        self.AttackThrottleAircraft = 0  # 攻击油门_飞机
        self.TransitAltitudeAircraft = 0.0  # 运输高度_飞机
        self.StationAltitudeAircraft = 0.0  # 阵位高度_飞机
        self.AttackAltitudeAircraft = 0.0  # 攻击高度_飞机
        self.AttackDistanceAircraft = 0.0  # 攻击距离_飞机
        self.TransitTerrainFollowingAircraft = False  # 运输地形跟随_飞机
        self.StationTerrainFollowingAircraft = False  # 阵位地形跟随_飞机
        self.AttackTerrainFollowingAircraft = False  # 攻击地形跟随_飞机
        self.TransitThrottleSubmarine = 0  # 运输油门_潜艇
        self.StationThrottleSubmarine = 0  # 阵位油门_潜艇
        self.AttackThrottleSubmarine = 0  # 攻击油门_潜艇
        self.TransitDepthSubmarine = 0.0  # 9999表示无设置  // 运输深度_潜艇
        self.StationDepthSubmarine = 0.0  # 9999表示无设置 // 阵位深度_潜艇
        self.AttackDepthSubmarine = 0.0  # 攻击深度_潜艇
        self.AttackDistanceSubmarine = 0.0  # 攻击距离_潜艇
        self.TransitThrottleShip = 0  # 运输油门_舰船
        self.StationThrottleShip = 0  # 阵位油门_舰船
        self.AttackThrottleShip = 0  # 攻击油门_舰船
        self.AttackDistanceShip = 0.0  # 攻击距离_舰船
        self.TransitThrottleFacility = 0  # 运输油门_设施
        self.StationThrottleFacility = 0  # 阵位油门_设施
        self.AttackThrottleFacility = 0  # 攻击油门_设施
        self.FormationCruise = 0  # 巡航队形
        self.FormationAttack = 0  # 攻击队形
        self.MinAircraftReq = 0  # 最小飞机数量
        self.NumberOfFlightsInvestigate = 0  # 航班数量_侦查
        self.NumberOfFlightsEngage = 0  # 航班数量_交战
        self.WingmanEngageDistance = 0  # 僚机交战距离
        self.NumberOfBoatsInvestigate = 0  # 船只数量_侦查
        self.NumberOfBoatsEngage = 0  # 船只数量_交战
        self.GroupMemberEngageDistance = 0  # 组成员交战距离
        self.ContinousCoverageEnable = False  # 连续覆盖启用
        self.ContinousCoverageAllowQRA = False  # 连续覆盖_QRA启用
        self.ContinousCoverageFlightGenerationMethod = 0  # 连续覆盖_航班方法
        self.ContinousCoverageStationTime = 0  # 连续覆盖_阵位时间
        self.ContinousCoverageOverlap = 0  # 连续覆盖_重叠
        self.ContinousCoverageDuration = 0  # 连续覆盖_持续时间
        self.CCSList = []  # 连续覆盖阵位列表--THCCS列表
        self.QRAs = []  # 连续覆盖_QRA--THCCS列表
        self.ContinousCoverageQRANumberOfFlights = 0  # 连续覆盖_QRA航班数量
        self.ContinousCoverageQRAFlightGenerationMethod = 0  # 连续覆盖_QRA航班方法
        self.ContinousCoverageNumberOfFlightsNeededToAllowQRA = 0  # 连续覆盖_允许QRA所需的航班数量
        self.MovementStyle = 0  # 巡逻运动风格

    def set_one_third_rule(self, one_third):
        """
        1、三分之一规则
        :param one_third: bool, True,设置三分之一规则  False:不遵守三分之一规则
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "oneThirdRule=%s" % (str(one_third).lower())
        return self._set(str_set)

    def station_count(self, unit_number):
        """
        2、巡逻任务阵位上每类平台保存作战单元数量
        :param unit_number: int, 阵位上每类平台保存单元数量
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "onStation='%d'" % unit_number
        return self._set(str_set)

    def patrol_checkOPA(self, ischeckOPA):
        """
        3、设置任务是否对巡逻区外的探测目标进行分析
        :param ischeckOPA: bool, True:分析，False:不分
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "checkOPA=%s" % str(ischeckOPA).lower()
        return self._set(str_set)

    def patrol_activeEMCON(self, isactiveEMCON):
        """
        4、设置任务是否仅在巡逻任务警戒区内打开电磁辐射
        :param isactiveEMCON: bool, True:打开 False:不打开
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "activeEMCON=%s" % str(isactiveEMCON).lower()
        return self._set(str_set)

    def patrol_checkWWR(self, ischeckWWR):
        """
        5、设置任务是否对武器射程内探测目标进行分析
        :param ischeckWWR: bool, True遵守  False不遵守
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "checkWWR=%s" % str(ischeckWWR).lower()
        return self._set(str_set)

    def patrol_flight_size(self, enum_flight_size):
        """
        6、设置任务编队规模
        :param enum_flight_size:FlightSize枚举值, 查看global_util.py中定义 编队规模
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "flightSize=%d" % enum_flight_size.value
        return self._set(str_set)

    def patrol_useFlightSize(self, useFlightSize):
        """
        7、是否飞机数低于编队规模不允许起飞
        :param useFlightSize: bool,  True:是
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "useFlightSize=%s" % str(useFlightSize).lower()
        return self._set(str_set)

    def patrol_set_throttle_transit(self, enum_throttle):
        """
        8、设置任务的飞机出航油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "transitThrottleAircraft='Unspecified'"
        else:
            str_set = "transitThrottleAircraft=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def patrol_set_throttle_station(self, enum_throttle):
        """
        9、设置任务的飞机阵位油门
        :param enum_throttle: 枚举Throttle的值, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "stationThrottleAircraft='Unspecified'"
        else:
            str_set = "stationThrottleAircraft=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def patrol_set_throttle_attack(self, enum_throttle):
        """
        10、设置任务的飞机攻击油门
        :param enum_throttle: 枚举Throttle的值, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "attackThrottleAircraft='Unspecified'"
        else:
            str_set = "attackThrottleAircraft=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def patrol_set_transitAltitude(self, transitAltitude):
        """
        11、设置任务的飞机出航高度
        :param transitAltitude: int, 出航高度， 单位：米，最多6位数字，例：9999， 888888
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "transitAltitudeAircraft=%.1lf" % transitAltitude
        return self._set(str_set)

    def patrol_set_stationAltitude(self, altitude_value):
        """
        12、设置任务的飞机阵位高度
        :param altitude_value: int, 阵位高度， 单位：米，最多6位数字，例：9999， 888888
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "StationAltitudeAircraft=%.1lf" % altitude_value
        return self._set(str_set)

    def patrol_set_attackAltitude(self, altitude_value):
        """
        13、设置任务的飞机攻击高度
        :param altitude_value: int, 攻击高度， 单位：米，最多6位数字，例：9999， 888888
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "attackAltitudeAircraft=%.1lf" % altitude_value
        return self._set(str_set)

    def patrol_set_attack_distance(self, distance):
        """
        14、设置任务的飞机攻击距离, 需整数
        :param distance: int, 攻击距离，单位：海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "attackDistanceAircraft=%d" % int(distance)
        return self._set(str_set)

    def set_patrolZone(self, points_list):
        """
        15、设置巡逻区
        :param points_list:  区域按顺序排列的参考点名列表 type:list
        案例：points_list=['RP-101','RP-102','RP-103'] 3个点组成的巡逻区域
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        point_list_str = str(points_list).replace('[', '{').replace(']', '}')
        str_set = "patrolZone=%s" % point_list_str
        return self._set(str_set)

    def set_prosecutionZone(self, points_list):
        """
        16、设置巡逻任务警戒区
        points_list: 区域按顺序排列的警戒参考点名列表  type:list
        points_list=['RP-101','RP-102','RP-103'] 3个点组成的巡逻警戒区域
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        point_list_str = str(points_list).replace('[', '{').replace(']', '}')
        str_set = "prosecutionZone=%s" % point_list_str
        return self._set(str_set)

    def set_minAircraftReq(self, minAircraftReq):
        """
        17、设置任务所需最少飞机数
        :param minAircraftReq: 枚举MinAircraftReq的值, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "minAircraftReq=%d" % minAircraftReq.value
        return self._set(str_set)

    def set_groupSize(self, groupSize):
        """
        18、设置任务舰船/潜艇编队大小
        :param groupSize: 枚举GroupSize的值 global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "groupSize=%d" % groupSize.value
        return self._set(str_set)

    def set_useGroupSize(self, useGroupSize):
        """
        19、强制舰船/潜艇编队大小
        :param useGroupSize: bool, 是否
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "useGroupSize=%s" % str(useGroupSize).lower()
        return self._set(str_set)

    def set_transitTerrainFollowingAircraft(self, transitTerrainFollowingAircraft):
        """
        20、飞机出航地形跟随
        :param transitTerrainFollowingAircraft: bool, 是否
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "transitTerrainFollowingAircraft=%s" % str(transitTerrainFollowingAircraft).lower()
        return self._set(str_set)

    def set_stationTerrainFollowingAircraft(self, stationTerrainFollowingAircraft):
        """
        21、飞机阵位地形跟随
        :param stationTerrainFollowingAircraft: bool, 是否
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "stationTerrainFollowingAircraft=%s" % str(stationTerrainFollowingAircraft).lower()
        return self._set(str_set)

    def set_transitThrottleSubmarine(self, enum_throttle):
        """
        22、潜艇出航油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "transitThrottleSubmarine='Unspecified'"
        else:
            str_set = "transitThrottleSubmarine=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def set_stationThrottleSubmarine(self, enum_throttle):
        """
        23、潜艇阵位油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "stationThrottleSubmarine='Unspecified'"
        else:
            str_set = "stationThrottleSubmarine=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def set_transitDepthSubmarine(self, transitDepthSubmarine):
        """
        24、潜艇出航潜深
        :param transitDepthSubmarine: float, 米, 海拔高度，需传递负值,例：-100
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "transitDepthSubmarine=%.2lf" % transitDepthSubmarine
        return self._set(str_set)

    def set_stationDepthSubmarine(self, stationDepthSubmarine):
        """
        25、潜艇阵位潜深
        :param stationDepthSubmarine: float  米, 海拔高度，需传递负值,例：-150
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "stationDepthSubmarine=%.2lf" % stationDepthSubmarine
        return self._set(str_set)

    def set_transitThrottleShip(self, enum_throttle):
        """
        26、水面舰艇出航油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "transitThrottleShip='Unspecified'"
        else:
            str_set = "transitThrottleShip=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def set_stationThrottleShip(self, enum_throttle):
        """
        27、水面舰艇阵位油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "stationThrottleShip='Unspecified'"
        else:
            str_set = "stationThrottleShip=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def set_attackTerrainFollowingAircraft(self, attackTerrain):
        """
        28、攻击飞机地形跟随
        :param attackTerrain: type:bool 是否攻击飞机地形跟随
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "attackTerrainFollowingAircraft=%s" % str(attackTerrain).lower()
        return self._set(str_set)

    def set_attackThrottleSubmarine(self, enum_throttle):
        """
        29、潜艇攻击油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "attackThrottleSubmarine='Unspecified'"
        else:
            str_set = "attackThrottleSubmarine=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def set_attackDepthSubmarine(self, attackDepthSubmarine):
        """
        30、潜艇攻击潜深
        :param attackDepthSubmarine: float   米, 海拔高度，需传递负值,例：-150.5
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "attackDepthSubmarine=%.2lf" % attackDepthSubmarine
        return self._set(str_set)

    def set_attackDistanceSubmarine(self, attackDistanceSubmarine):
        """
        31、潜艇攻击距离
        :param attackDistanceSubmarine: int, 需整数，海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "attackDistanceSubmarine=%d" % attackDistanceSubmarine
        return self._set(str_set)

    def set_attackThrottleShip(self, enum_throttle):
        """
        32、水面舰艇攻击油门
        :param enum_throttle:枚举Throttle的值, 油门, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if enum_throttle.value == 0:
            str_set = "attackThrottleShip='Unspecified'"
        else:
            str_set = "attackThrottleShip=%d" % (enum_throttle.value - 1)
        return self._set(str_set)

    def set_attackDistanceShip(self, attackDistanceShip):
        """
        33、水面舰艇攻击距离
        :param attackDistanceShip: int, 需整数，海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "attackDistanceShip=%d" % attackDistanceShip
        return self._set(str_set)

    def set_PatrolMovementStyle(self, PatrolMovementStyle):
        """
        34、动作风格设置:  0:区域内随机; 1:可重复循环；
        :param PatrolMovementStyle: int
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "PatrolMovementStyle=%d" % PatrolMovementStyle
        return self._set(str_set)

    def set_flightStoinvestigate(self, FlightStoinvestigate):
        """
        35、侦查不明目标飞机数量      所有/1/2/3/4/6/8/12/无偏好
        :param FlightStoinvestigate: str, "all","1","2"..."12","0"
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "FlightStoinvestigate='%s'" % FlightStoinvestigate
        return self._set(str_set)

    def set_flightStoengage(self, FlightStoengage):
        """
        36、敌方对抗的飞机数量      所有/1/2/3/4/6/8/12/无偏好
        :param FlightStoengage: str, "all","1","2"..."12","0"
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "FlightStoengage='%s'" % FlightStoengage
        return self._set(str_set)

    def set_wingmanEngageDistance(self, WingmanEngageDistance):
        """
        37、飞机设置  僚机可以在xx范围内侦察/交战   海里
        :param WingmanEngageDistance: int, 需整数，海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "WingmanEngageDistance=%d" % WingmanEngageDistance
        return self._set(str_set)

    def set_boatStoinvestigate(self, BoatStoinvestigate):
        """
        38、舰船/潜艇设置   侦查不明目标舰船数量  所有/1/2/3/4/6/8/12/无偏好
        :param BoatStoinvestigate: str, "all","1","2"..."12","0"
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "BoatStoinvestigate='%s'" % BoatStoinvestigate
        return self._set(str_set)

    def set_boatStoengage(self, BoatStoengage):
        """
        39、舰船/潜艇设置  与敌方交火的舰船数量   所有/1/2/3/4/6/8/12/无偏好
        :param BoatStoengage: str, "all","1","2"..."12","0"
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "BoatStoengage='%s'" % BoatStoengage
        return self._set(str_set)

    def set_GroupmemberEngageDistance(self, GroupmemberEngageDistance):
        """
        40、舰船/潜艇设置 编组成员可以在--范围内侦察/交战   海里
        :param GroupmemberEngageDistance: int, 需整数，海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "GroupmemberEngageDistance=%d" % GroupmemberEngageDistance
        return self._set(str_set)

