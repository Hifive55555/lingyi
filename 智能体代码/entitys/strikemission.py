# -*- coding:utf-8 -*-
# Description: 打击任务

from .global_util import *
from .mission_common import MissionCommon
from .commonfunction import guid_list_parser


class StrikeMission(MissionCommon):
    def __init__(self, guid, name, side_name, is_escort=False):
        """
        打击任务类  
        1、设置打击目标  
        2、设置任务：删除打击任务目标  
        3、设置任务细节：是否仅考虑计划目标（在目标清单中）  
        4、设置打击任务触发条件  
        5、设置任务细节：任务允许出动的最大飞行批次  
        6、设置打击任务飞机编队规模  
        7、设置打击任务所需最少飞机数  
        8、设置打击任务雷达运用规则  
        9、设置打击任务燃油弹药规则  
        10、设置打击任务最小打击半径  
        11、设置打击任务最大打击半径设置打击任务最小打击半径  
        12、设置打击任务是否飞机数低于编组规模数要求就不能起飞  
        13、设置打击任务是否多扇面攻击（任务AI自动生成）  
        14、设置打击任务是否仅限一次  
        15、设置打击任务舰艇/潜艇编队规模  
        16、设置打击任务是否强制舰艇/潜艇编队规模  
        17、设置打击任务护航飞机编队规模  
        18、设置打击护航任务所需最少飞机数  
        19、设置打击护航任务所需最大飞机数  
        20、设置打击护航任务最大威胁响应半径  
        21、设置打击任务舰船/潜艇最小打击半径  
        22、设置打击任务舰船/潜艇最大打击半径 海里  
        23、包含在空中任务指令中  
        24、护航飞机数低于编队规模要求，不能起飞(根据基地、类型或挂载进行编组)  
        25、非火力打击编队大小设置，电子战、侦察或预警  
        26、非火力打击, 执行任务所需的最低就绪护航数  
        27、非火力打击,飞行任务允许的最大护航数  
        28、护航舰船/潜艇 护航任务的舰船/潜艇编队大小  
        29、护航舰船/潜艇 使用护航水面舰艇/潜艇小于编队规模不能出动
        30、护航飞机设置 侦查不明目标飞机数量
        31、护航舰/船 与敌方对抗的飞机数量
        32、飞机设置 僚机可以在xx范围内与敌交战
        33、护航舰船/潜艇 侦查不明目标单元数量
        34、护航舰船/潜艇 与敌方对抗的单元数量
        35、护航舰船/潜艇 舰船可以在--范围内与敌交战 海里

        示例：  
        self.ShiZong_attack = self.create_strike_mission('ShiZong_attack', MissionStrikeType.SHIP) #创建ShiZong_attack打击任务  
        target_list = []  
        for contact_id,contact_info in situation[1].items():   # 遍历敌方情报信息  
            if contact_info['Name'] == '水面#7':  # 获取'水面#7'的敌方目标id  
                target_list.append(contact_id)  # 目标id加入target_list  
            elif contact_info['Name'] == '水面#5':  
                target_list.append(contact_id)  
        self.ShiZong_attack.strike_add_target(target_list) #多个目标加入ShiZong_attack打击任务  
        """
        if is_escort:
            MissionCommon.__init__(self, guid, name, side_name, ElementType.StrikeEscortMission)
        else:
            MissionCommon.__init__(self, guid, name, side_name, ElementType.StrikeMission)
            self.escort = StrikeMission(guid, name, side_name, is_escort=True)
        self.Type = 0  # 打击任务子类型，含义如下：
        """
        0: 对空打击
        1: 对陆打击
        2: 对海攻击
        3: 对潜攻击
        """
        self.DoctrineEscorts = {}  # 护航条令--结构：THDoctrine
        self.SpecificTargets = []  # 打击目标GUID列表
        self.STargName = []  # 打击目标名称列表(与SpecificTargets一一对应)
        self.MCSTT = 0  # MinimumContactStanceToTrigger 触发的最小接触立场
        self.UP = False  # UsePlanner 使用计划
        self.FormationCruise = 0  # 队形_巡航
        self.FormationAttack = 0  # 队形_攻击
        self.Bingo = 0  # Bingo 燃油设置
        self.TargeteeringMethod = 0  # 目标定位方法
        self.EscortFlightSizeShooter = 0  # 护送_航班大小_射击
        self.EscortFlightSizeNonShooter = 0  # 护送_航班大小_无射击
        self.EscortFormationCruise = 0  # 护送_队形_巡航
        self.EscortFormationAttack = 0  # 护送_队形_攻击
        self.EscortTransitThrottle = 0  # 护送_运输油门
        self.EscortStationThrottle = 0  # 护送_攻击油门
        self.EscortTransitAltitude = 0.0  # 护送_运输高度
        self.EscortStationAltitude = 0.0  # 护送_攻击高度
        self.EscortTransitTerrainFollowing = False  # 护送_运输地形跟随
        self.EscortAttackTerrainFollowing = False  # 护送_攻击地形跟随
        self.EscortResponseRadius = 0.0  # 护送_响应半径(海里)
        self.EscortGroupSize = 0  # 护送_编队大小
        self.MinAircraftReqStrikers = 0  # 最小飞机数量 MinimumNumberOfAircraft
        self.MaxAircraftToFlyStrikers = 0  # 最大飞行次数_打击 MaxFlightNumber_Strike
        self.MinAircraftReqEscortsShooter = 0  # 最小飞机数量_护送_射击
        self.MaxAircraftToFlyEscortShooter = 0  # 最大飞机数量_护送_射击
        self.MinAircraftReqEscortsNonShooter = 0  # 最小飞机数量_护送_无射击
        self.MaxAircraftToFlyEscortNonShooter = 0  # 最大飞机数量_护送_无射击
        self.MinResponseRadiusAircraft = 0.0  # 最小响应半径_飞机
        self.MaxResponseRadiusAircraft = 0.0  # 最大响应半径_飞机
        self.MinResponseRadiusShip = 0.0  # 最小响应半径_舰艇
        self.MaxResponseRadiusShip = 0.0  # 最大响应半径_舰艇
        self.PrePlannedOnly = False  # 仅预先计划
        self.OneTimeOnly = False  # 仅限一次性
        self.OneTimeOnlyFlown = False  # 仅限一次性飞行
        self.RadarBehaviour = 0  # 雷达行为
        self.AttackMethod = 0  # 攻击方法
        self.SplitDistance = 0  # 分割距离
        self.UseFlightSizeHardLimitEscort = False  # 使用航班大小强制限制_护送
        self.UseGroupSizeHardLimitEscort = False  # 使用编队大小强制限制_护送
        self.EscortNumberOfFlightsInvestigate = 0  # 护送_航班数量_侦查
        self.EscortNumberOfFlightsEngage = 0  # 护送_航班数量_交战
        self.EscortWingmanEngageDistance = 0.0  # 护送_僚机交战距离
        self.EscortNumberOfBoatsInvestigate = 0  # 护送_船只数量_侦查
        self.EscortNumberOfBoatsEngage = 0  # 护送_船只数量_交战
        self.EscortGroupMemberEngageDistance = 0.0  # 护送_编队成员交战距离

    def strike_add_target(self, target_list):
        """
        1、设置打击目标
        :param target_list: list, 目标列表, Contact id
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_strike_add_target(self, target_list)

    def strike_removeTarget(self, target_list):
        """
        2、设置任务：删除打击任务目标
        :param target_list: list, 目标列表, Contact id
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_strike_removeTarget(self, target_list)

    def strike_setPreplan(self, bPreplan):
        """
        3、设置任务细节：是否仅考虑计划目标（在目标清单中）
        :param bPreplan: bool, True:是仅考虑计划目标
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "strikePreplan=%s" % str(bPreplan).lower()
        return self._set(str_set)

    def strike_setAttackCondition(self, enum_strikeMinimumTrigger):
        """
        4、设置打击任务触发条件
        :param enum_strikeMinimumTrigger:StrikeMinimumTrigger枚举值,
                                        global_util.py中定义，例：StrikeMinimumTrigger.Hostile
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "StrikeMinimumTrigger=%d" % enum_strikeMinimumTrigger.value
        return self._set(str_set)

    def strike_setStrikeMax(self, strikeMax):
        """
        5、设置任务细节：任务允许出动的最大飞行批次
        :param strikeMax:StrikeFlyTimeMax枚举值，global_util.py中定义，例：StrikeFlyTimeMax.TWO
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "strikeMax=%d" % strikeMax.value
        return self._set(str_set)

    def strike_setStrikeFlightSize(self, flightSize):
        """
        6、设置打击任务飞机编队规模
        :param flightSize:FlightSize枚举值, 编队规模，global_util.py中定义，例：FlightSize.Two：双机编队
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "strikeFlightSize=%d" % flightSize.value
        return self._set(str_set)

    def strike_setStrikeMinAircraftReq(self, minAircraft):
        """
        7、设置打击任务所需最少飞机数
        :param minAircraft:MinAircraftReq枚举值, global_util.py中定义，例：MinAircraftReq.TWO：双机
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "strikeMinAircraftReq=%d" % minAircraft.value
        return self._set(str_set)

    def strike_setStrikeRadarUsage(self, radarUsage):
        """
        8、设置打击任务雷达运用规则
        :param radarUsage:StrikeRadarUsage枚举值, global_util.py中定义，例：StrikeRadarUsage.ALL_PLAN：整个任务使用
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "StrikeRadarUsage=%d" % radarUsage.value
        return self._set(str_set)

    def strike_setStrikeFuelAmmo(self, fuelAmmo):
        """
        9、设置打击任务燃油弹药规则
        :param fuelAmmo: StrikeFuelAmmo枚举值, global_util.py中定义，例：StrikeFuelAmmo.MOUNT_SET：根据装载位置...
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "StrikeFuelAmmo=%d" % fuelAmmo.value
        return self._set(str_set)

    def strike_setStrikeMinDist(self, minDist):
        """
        10、设置打击任务最小打击半径
        :param minDist:int, 海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "StrikeMinDist=%d" % minDist
        return self._set(str_set)

    def strike_setMissionStrikeMaxDist(self, maxDist):
        """
        11、设置打击任务最大打击半径
        :param maxDist: int, 海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "StrikeMaxDist=%d" % maxDist
        return self._set(str_set)

    def strike_setStrikeUseFlightSize(self, bUseFlightSize):
        """
        12、设置打击任务是否飞机数低于编组规模数要求就不能起飞
        :param bUseFlightSize: bool, 是否飞机数低于编组规模数要求就不能起飞
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "strikeUseFlightSize=%s" % str(bUseFlightSize).lower()
        return self._set(str_set)

    def strike_setStrikeUseAutoPlanner(self, bUseAutoPlanner):
        """
        13、设置打击任务是否多扇面攻击（任务AI自动生成）
        :param bUseAutoPlanner: bool, 是否多多扇面攻击
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "strikeAutoPlanner=%s" % str(bUseAutoPlanner).lower()
        return self._set(str_set)

    def strike_setStrikeOneTimeOnly(self, bOneTimeOnly):
        """
        14、设置打击任务是否仅限一次
        :param bOneTimeOnly: bool, 是否仅一次
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "strikeOneTimeOnly=%s" % str(bOneTimeOnly).lower()
        return self._set(str_set)

    def strike_ship_size(self, ship_size):
        """
        15、设置打击任务舰艇/潜艇编队规模
        :param ship_size:GroupSize枚举值, 编队规模, global_util.py中定义, 例：GroupSize.Double,双船编队
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "strikeGroupSize=%d" % ship_size.value
        return self._set(str_set)

    def strike_use_ship_size(self, use_size):
        """
        16、设置打击任务是否强制舰艇/潜艇编队规模
        :param use_size: bool, 使用编队规模
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "strikeUseGroupSize=%s" % str(use_size).lower()
        return self._set(str_set)

    def escort_flight_size(self, flight_size):
        """
        17、设置打击任务护航飞机编队规模
        :param flight_size: FlightSizeNum枚举值, 编队规模, global_util.py中定义, 例：FlightSizeNum.SingleAircraft,单机编队
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "escortFlightSizeShooter=%d" % flight_size.value
        return self._set(str_set)

    def escort_min_shooter(self, flight_size):
        """
        18、设置打击护航任务所需最少飞机数
        :param flight_size: MinAircraftReq枚举值, 编队规模, global_util.py中定义, 例：MinAircraftReq.TWO, 2机
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "escortMinShooter=%d" % flight_size.value
        return self._set(str_set)

    def escort_max_shooter(self, flight_size):
        """
        19、设置打击护航任务所需最大飞机数
        :param flight_size: MinAircraftReq枚举值, 编队规模, global_util.py中定义, 例：MinAircraftReq.TWO, 2机
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "escortMaxShooter=%d" % flight_size.value
        return self._set(str_set)

    def escort_response_radius(self, radius):
        """
        20、设置打击护航任务最大威胁响应半径
        :param radius: int,  最大威胁响应半径  海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "escortResponseRadius=%d" % radius
        return self._set(str_set)

    def set_strike_minDistShip(self, min_range):
        """
        21、设置打击任务舰船 / 潜艇最小打击半径
        :param min_range: int, 距离，海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "StrikeMinDistShip=%d" % min_range
        return self._set(str_set)

    def set_strike_maxDistShip(self, max_range):
        """
        22、设置打击任务舰船 / 潜艇最大打击半径  海里
        :param max_range: int, 距离，海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "StrikeMaxDistShip=%d" % max_range
        return self._set(str_set)

    def set_includeInATO(self, is_in):
        """
        23、包含在空中任务指令中
        :param is_in：bool, True: 包含在空中任务指令中
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "IncludeInATO=%s" % str(is_in).lower()
        return self._set(str_set)

    def set_escortUseFlightSize(self, escort_use_size):
        """
        24、护航飞机数低于编队规模要求，不能起飞(根据基地、类型或挂载进行编组)
        :param escort_use_size: bool，执行护航编队规模
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "escortUseFlightSize=%s" % str(escort_use_size).lower()
        return self._set(str_set)

    def set_escortFlightSizeNonshooter(self, escort_size):
        """
        25、非火力打击编队大小设置，电子战、侦察或预警
        :param escort_size: int, 1:单机; 2:使用与战斗机和压制敌防空相同设置
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "escortFlightSizeNonshooter=%d" % escort_size
        return self._set(str_set)

    def set_strike_escortMinNonshooter(self, escort_min):
        """
        26、非火力打击, 执行任务所需的最低就绪护航数
        :param escort_min: int, 13:所有，0:无偏好
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "escortMinNonshooter=%d" % escort_min
        return self._set(str_set)

    def set_strike_escortMaxNonshooter(self, escort_max):
        """
        27、非火力打击,飞行任务允许的最大护航数
        :param escort_max: int, 13:所有，0:无偏好
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "escortMaxNonshooter=%d" % escort_max
        return self._set(str_set)

    def set_escortGroupSize(self, escort_ship_size):
        """
        28、护航舰船/潜艇   护航任务的舰船 / 潜艇编队大小
        :param escort_ship_size:GroupSize枚举值, 编队规模, global_util.py中定义, GroupSize.Double,双船编队
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "escortGroupSize=%d" % escort_ship_size.value
        return self._set(str_set)

    def set_escortUseGroupSize(self, escort_use_group):
        """
        29、护航舰船/潜艇      使用护航水面舰艇 / 潜艇小于编队规模不能出动
        :param escort_use_group: bool, True:勾选
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "escortUseGroupSize=%s" % str(escort_use_group).lower()
        return self._set(str_set)

    def set_flightStoinvestigate(self, flight_count):
        """
        30、护航飞机设置  侦查不明目标飞机数量
        :param flight_count: EUnitCount枚举值，global_util.py中定义, 例: EUnitCount.ONE, 单机
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "FlightStoinvestigate=%d" % flight_count.value
        return self._set(str_set)

    def set_strike_flightStoengage(self, flight_count):
        """
        31、护航舰/船  与敌方对抗的飞机数量      所有/1/2/3/4/6/8/12/无偏好
        :param flight_count: EUnitCount枚举值，global_util.py中定义, 例: EUnitCount.ONE, 单机
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "FlightStoengage=%d" % flight_count.value
        return self._set(str_set)

    def set_wingmanEngageDistance(self, engage_range):
        """
        32、飞机设置  僚机可以在xx范围内与敌交战
        :param engage_range: int, 需整数，海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "WingmanEngageDistance=%d" % engage_range
        return self._set(str_set)

    def set_boatStoinvestigate(self, flight_count):
        """
        33、护航舰船/潜艇  侦查不明目标单元数量
        :param flight_count: EUnitCount枚举值，global_util.py中定义, 例: EUnitCount.ONE, 单机
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "BoatStoinvestigate=%d" % flight_count.value
        return self._set(str_set)

    def set_boatStoengage(self, flight_count):
        """
        34、护航舰船/潜艇 与敌方对抗的单元数量
        :param flight_count: EUnitCount枚举值，global_util.py中定义, 例: EUnitCount.ONE, 单机
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "BoatStoengage=%d" % flight_count.value
        return self._set(str_set)

    def set_shipEngageDistance(self, engage_range):
        """
        35、护航舰船/潜艇  舰船可以在 - -范围内与敌交战   海里
        :param engage_range: int, 需整数，海里
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "GroupmemberEngageDistance=%d" % engage_range
        return self._set(str_set)
