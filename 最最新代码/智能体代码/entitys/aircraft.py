# -*- coding:utf-8 -*-
# Description: 飞机

from .unit import Unit
from .global_util import *


class Aircraft(Unit):
    """
    飞机类  
    1、获取飞机挂架和挂载上的武器信息  
    2、获取精简信息, 提炼信息进行决策  
    3、获取飞机当前油量  
    4、获取飞机当前飞行状态  
    5、获取飞机状态  
    6、设置飞机的武器挂载
    7、飞机中止出动
    8、飞机燃油计算
    9、设置当前单元（飞机）的飞行高度跟随地形
    10、卸货，飞机等卸掉物资
    11、卸载选定物资
    12、设置飞机的飞行高度层

    示例：  
    air1_id = "sflsf0-gjlsf-sf"  # 飞机guid  
    air1 = self.get_unit(air1_id)  # 获取飞机对象  
    if air1 is not None:  
        reply = air1.set_loadout(22682)  # 设置此飞机武器挂载方案，挂载方案id：22682  
        rate = air1.FuelRate  # 此飞机当前耗油率  
    """
    def __init__(self, guid, name, side_name):
        Unit.__init__(self, guid, name, side_name, ElementType.Aircraft)
        # THAirOps等结构定义请查看entitys/struct.proto文件
        # 结构THUnitAircraft中属性： 飞机
        self.FlightRole = 0  # EFlightElement 航班角色
        self.AirborneTime = 0.0  # 飞行时间
        self.AltitudePreset = 0  # 预设高度  高度预设枚举值定义参见：飞机EAircraftAltitudePreset
        self.AirOps = {}  # 飞机停靠机场--结构：THAirOps
        self.FuelRate = 0.0  # 耗油率 千克/秒

    def get_weapon_info(self):
        """
        1、获取飞机挂架和挂载上的武器信息
        :return: 武器ID和数量的字典
        """
        weapon_info = {}
        for k, v in self.Mounts.items():
            if "WeaponRecs" in v:
                for rid, w in v["WeaponRecs"].items():
                    count = w["CurrentLoad"]
                    if count > 0:
                        weaponid = w["WeaponDBID"]
                        if weaponid in weapon_info:
                            weapon_info[weaponid] += count
                        else:
                            weapon_info[weaponid] = count

        for k, v in self.Loadouts.items():
            if "WeaponRecs" in v:
                for rid, w in v["WeaponRecs"].items():
                    if 'CurrentLoad' not in w:
                        continue
                    count = w["CurrentLoad"]
                    if count > 0:
                        weaponid = w["WeaponDBID"]
                        if weaponid in weapon_info:
                            weapon_info[weaponid] += count
                        else:
                            weapon_info[weaponid] = count
        return weapon_info

    def get_summary_info(self):
        """
        2、获取精简信息, 提炼信息进行决策
        :return: dict, 飞机提炼信息
        """
        info_dict = {
            "category": "Aircraft",
            "guid": self.ID,
            "dbid": self.DBID,
            "type": self.Type,
            "name": self.Name,
            "mission": self.AssignedMission,
            "lat": self.Lat,
            "lon": self.Lon,
            "alt": self.CurrentAltitude,
            "course": self.get_way_points_info(),
            "head": self.CurrentHeading,
            "pitch": self.Pitch,
            "roll": self.Roll,
            "speed": self.CurrentSpeed,
            "fuel": self.FuelRecs,
            "damage": self.DamagePercent,
            "status": self.Status,
            "airops": self.AirOps,
            "sensors": self.Sensors,
            "sensory": self.Sensory,
            "mounts": self.Mounts,
            "loadout": self.Loadouts,
            "targetedBy": self.get_targets(),
            "fuelstate": self.FuelState,
            "fuelrate": self.FuelRate
        }
        return info_dict

    def get_fuel_capacity(self):
        """
        3、获取飞机当前油量
        :return: float, 千克
        """
        fuel_capacity = 0
        for v in self.FuelRecs.values():
            if "CQ" in v:
                fuel_capacity += v['CQ']
        return fuel_capacity

    def get_status(self):
        """
        4、获取飞机当前飞行状态
        :return: 枚举AirOpsCondition的值, global_util.py中定义
        """
        ops_code = 999
        if 'Con' in self.AirOps:
            ops_code = self.AirOps['Con']
        elif 'Condition' in self.AirOps:
            ops_code = self.AirOps['Condition']
        return ops_code

    def get_status_type(self):
        """
        5、获取飞机状态
        :return: AirValidStatus, global_util.py中定义
        """
        ops_code = 999
        if 'Condition' in self.AirOps:
            ops_code = self.AirOps['Condition']
        elif 'Con' in self.AirOps:
            ops_code = self.AirOps['Con']

        if ops_code in (1, 2, 4, 8, 9, 18, 23, 24, 26):
            # 在基地可马上部署飞行任务
            return AirValidStatus.validToFly
        elif ops_code in (0, 13, 14, 15, 16, 19, 20, 21, 22):
            # 在空中可部署巡逻，进攻，航路规划
            return AirValidStatus.InAir
        elif ops_code in (5, 10, 11, 17, 25):
            # 在空中返航或降落
            return AirValidStatus.InAirRTB
        else:
            # 在基地等待准备好
            return AirValidStatus.WaitReady

    def set_loadout(self, loadoutID):
        """
        6 、设置飞机的武器挂载
        推演模式，需考虑机场或航母上弹药库有所需挂载的武器
        如机场或航母上弹药库无所需挂载的武器，则飞机挂载失败，挂载方案调整为预备飞行
        :param loadoutID: int  武器挂载方案ID
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_loadout_need_magazine_weapon(self, loadoutID)

    def abort_launch(self):
        """
        7、飞机中止出动
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_abort_launch(self)

    def calc_fuel_by_abntime(self, abntime):
        """
        8、飞机燃油计算，通过飞行时间（秒）计算剩余燃油（千克）
        :param abntime: int, 飞行时间，单位：秒
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_calc_fuel_by_abntime(self, abntime)

    def unit_follow_terrain(self, is_fellow):
        """
        9、设置当前单元（飞机）的飞行高度跟随地形
        :param is_fellow:bool, True:跟随地形
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        self._game_server.api_unit_follow_terrain(self, is_fellow)

    def unload_cargo(self):
        """
        10、卸货，飞机等卸掉物资
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_unload_cargo(self)

    def UnloadSelCargos(self, cargo):
        """
        11、卸载选定物资
        :param cargo: list, 需卸货的物资ID列表
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_UnloadSelCargos(self, cargo)

    def set_alt_level(self, enum_alt):
        """
        12、设置飞机的期望飞行高度层,枚举AltitudeLevel的字符串值, global_util.py中定义
        :param enum_alt: str, 期望高度层：'MIN'：尽可能低;'LOW1000':低空305米，'LOW2000':低空610米;'MEDIUM12000':中高3658米;
                            'HIGH25000':高空7620米;'HIGH36000':高空10973米高;'MAX':尽可能高
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_alt_level(self, enum_alt)

