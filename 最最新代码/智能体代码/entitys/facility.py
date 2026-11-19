# -*- coding:utf-8 -*-
# Description: 地面装备

from .global_util import *
from .unit import Unit


class Facility(Unit):
    """
    地面装备类  
    1、获取地面设施弹药库的所有武器  
    2、获取单元挂架武器信息, 以列表形式返回  
    3、获取精简信息, 提炼信息进行决策  
    4、保持阵位-所选单元  

    示例：  
    facility_id = "sflsf0-gjlsf-sf"  # 地面设施guid  
    facility = self.get_unit(facility_id)  # 获取地面设施对象  
    if facility is not None:  
        reply = facility1.get_magazine_weapon()  # 获取地面设施弹药库的所有武器  
        target_id = "tar-fjslf20-fs"  # 目标,contact的id  
        reply = facility1.attack_auto(target_id)  # 地面单元打击目标  
    """
    def __init__(self, guid, name, side_name):
        Unit.__init__(self, guid, name, side_name, ElementType.Facility)

    def get_magazine_weapon(self):
        """
        1、获取地面设施弹药库的所有武器
        :return: 武器ID和数量的字典
        """
        weapon_info = {}
        for info in self.Magazines.values():
            for weapon in info['Weapons'].values():
                count = weapon["CurrentLoad"]
                if count > 0:
                    weaponid = weapon["WeaponDBID"]
                    if weaponid in weapon_info:
                        weapon_info[weaponid] += count
                    else:
                        weapon_info[weaponid] = count
        return weapon_info

    def get_weapon_infos(self):
        """
        2、获取单元挂架武器信息, 以列表形式返回
        :return: 武器信息列表
        """
        weapon_info = {}
        for k, v in self.Mounts.items():
            if "WeaponRecs" in v:
                for rid, w in v["WeaponRecs"].items():
                    weaponid = w["WeaponDBID"]
                    weapon_name = ""
                    if "Name" in w.keys():
                        weapon_name = w["Name"]
                    count = w["CurrentLoad"]
                    if weaponid in weapon_info:
                        record_info = weapon_info[weaponid]
                        new_count = record_info[1] + count
                        weapon_info[weaponid] = [weapon_name, new_count]
                    else:
                        weapon_info[weaponid] = [weapon_name, count]

        weapon_infos = []
        for k, v in weapon_info.items():
            weapon_infos.append([v[0], k, v[1]])
        return weapon_infos

    def get_summary_info(self):
        """
        3、获取精简信息, 提炼信息进行决策
        :return: dict, 地面装备提炼信息
        """
        info_dict = {
            "category": "Facility",
            "guid": self.ID,
            "dbid": self.DBID,
            "name": self.Name,
            "mission": self.AssignedMission,
            "lat": self.Lat,
            "lon": self.Lon,
            "alt": self.CurrentAltitude,
            "course": self.get_way_points_info(),
            "head": self.CurrentHeading,
            "speed": self.CurrentSpeed,
            "fuel": self.FuelRecs,
            "damage": self.DamagePercent,
            "status": self.Status,
            "sensors": self.Sensors,
            "mounts": self.Mounts,
            "magazine": self.Magazines,
            "targetedBy": self.get_targets(),
        }
        return info_dict

    def hold_positon(self, is_hold):
        """
        4、保持阵位-所选单元, 此指令会使地面单元停下
        :param is_hold: bool, True:保持阵位，False:不保持
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        self._game_server.api_hold_positon(self, is_hold)
