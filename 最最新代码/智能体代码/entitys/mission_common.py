# -*- coding:utf-8 -*-
# Description: 任务加油设置

from .mission import Mission


class MissionCommon(Mission):
    """
    任务(打击、巡逻、支援、布雷、清雷和转场任务)中包含空中加油相关设置的任务基类
    1、设置任务加油规划-选择加油机设置
    2、设置已分配特定任务的加油机加油
    3、设置所需加油机最小数量
    4、设置留空加油机最小数量
    5、设置阵位上加油机最小数量
    6、设置加油机没有到位的情况下启动任务
    7、每架加油机允许加油队列最大长度
    8、受油机开始寻找加油机占任务燃料百分比
    9、加油机遵循受油机的飞行计划
    10、空中受油机多远距离选择加油机

    示例：  
    patrol_mission = self.get_mission_by_name('patrol_mission_1')  #通过任务名 获取巡航任务对象  
    patrol_mission.set_mission_fuelQtyToStartLookingForTanker_airborne(30) #设置巡航任务中单元接受者开始寻找油轮燃料百分比  
    """
    def __init__(self, guid, name, side_name, element_type):
        Mission.__init__(self, guid, name, side_name, element_type)

    def use_tanker(self, tanker_usage):
        """
        1、设置任务加油规划-选择加油机设置
        :param tanker_usage: str, 'Automatic': 自动选择加油机; ‘Mission’：选择任务的加油机
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "tankerUsage='%s'" % tanker_usage
        return self._set(str_set)

    def set_mission_tankerMissionList(self, tankerMissionList):
        """
        2、设置已分配特定任务的加油机加油
        :param tankerMissionList: list, 作为加油源的要使用的任务id列表（注意，需闯入任务ID列表，而非任务名）
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        mission_list = str(tankerMissionList).replace('[', '{').replace(']', '}')
        str_set = "tankerMissionList=%s" % mission_list
        return self._set(str_set)

    def set_mission_tankerMinNumber_total(self, tankerMinNumber_total):
        """
        3、设置所需加油机最小数量
        :param tankerMinNumber_total: int, 所需油轮最低数量
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "tankerMinNumber_total=%d" % tankerMinNumber_total
        return self._set(str_set)

    def set_mission_tankerMinNumber_airborne(self, tankerMinNumber_airborne):
        """
        4、设置留空加油机最小数量
        :param tankerMinNumber_airborne: int, 数量
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "tankerMinNumber_airborne=%d" % tankerMinNumber_airborne
        return self._set(str_set)

    def set_mission_tankerMinNumber_station(self, tankerMinNumber_station):
        """
        5、设置阵位上加油机最小数量
        :param tankerMinNumber_station: int, 数量
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "tankerMinNumber_station=%d" % tankerMinNumber_station
        return self._set(str_set)

    def set_mission_launchMissionWithoutTankersInPlace(self, launchMissionWithoutTankersInPlace):
        """
        6、设置加油机没有到位的情况下启动任务
        :param launchMissionWithoutTankersInPlace: bool, 是否
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "launchMissionWithoutTankersInPlace=%s" % str(launchMissionWithoutTankersInPlace).lower()
        return self._set(str_set)

    def set_mission_maxReceiversInQueuePerTanker_airborne(self, maxReceiversInQueuePerTanker_airborne):
        """
        7、每架加油机允许加油队列最大长度
        :param maxReceiversInQueuePerTanker_airborne: int, 数量
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "maxReceiversInQueuePerTanker_airborne=%d" % maxReceiversInQueuePerTanker_airborne
        return self._set(str_set)

    def set_mission_fuelQtyToStartLookingForTanker_airborne(self, fuelQtyToStartLookingForTanker_airborne):
        """
        8、受油机开始寻找加油机占任务燃料百分比
        :param fuelQtyToStartLookingForTanker_airborne: int, 百分比分子整数 例如：70，90
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "fuelQtyToStartLookingForTanker_airborne=%d" % fuelQtyToStartLookingForTanker_airborne
        return self._set(str_set)

    def set_mission_TankerFollowsReceiverse(self, TankerFollowsReceivers):
        """
        9、加油机遵循受油机的飞行计划
        :param TankerFollowsReceivers: bool, 是否
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "TankerFollowsReceivers=%s" % str(TankerFollowsReceivers).lower()
        return self._set(str_set)

    def set_mission_tankerMaxDistance_airborne(self, tankerMaxDistance_airborne):
        """
        10、空中受油机多远距离选择加油机
        :param tankerMaxDistance_airborne: str, 'internal'或设置以下的一个里程（海里）: ‘50’, '100', '250', '500'
                                    'internal': 当前燃料负荷和飞行剖面下受油机的战术距离
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "tankerMaxDistance_airborne='%s'" % tankerMaxDistance_airborne
        return self._set(str_set)






