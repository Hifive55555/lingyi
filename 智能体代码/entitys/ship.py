# -*- coding:utf-8 -*-
# Description: 舰船

from .global_util import *
from .unit import Unit


class Ship(Unit):
    """
    舰船类  
    1、获取单元武器信息, 以列表形式返回  
    2、获取精简信息, 提炼信息进行决策  

    示例：  
    ship_id = "sflsf0-gjlsf-sf"  # 舰船guid  
    ship = self.get_unit(ship_id)  # 获取舰船对象  
    if ship is not None:  
        weapon_info = ship.get_weapon_infos()  # 获取舰船挂机上武器  
    """
    def __init__(self, guid, name, side_name):
        Unit.__init__(self, guid, name, side_name, ElementType.Ship)
        self.DockingOps = {}  # 船只停靠码头--结构：THDockingOps 定义请查看entitys/struct.proto文件

    def get_weapon_infos(self):
        """
        1、获取单元武器信息, 以列表形式返回
        :return: list, 武器列表，[(武器名，武器ID，数量)]
        """
        weapon_info = {}
        for k, v in self.Mounts.items():
            if "WeaponRecs" in v:
                for rid, w in v["WeaponRecs"].items():
                    weaponid = w["WeaponDBID"]
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
        2、获取精简信息, 提炼信息进行决策
        :return: dict
        """
        info_dict = {
            "category": "Ship",
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
            "sensory": self.Sensory,
            "mounts": self.Mounts,
            "magazine": self.Magazines,
        }
        return info_dict

