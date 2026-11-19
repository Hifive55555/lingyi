# -*- coding:utf-8 -*-
# Description: 潜艇

from .global_util import *
from .unit import Unit


class Submarine(Unit):
    def __init__(self, guid, name, side_name):
        """
        潜艇类  
        1、设置潜艇的期望深度  
        2、设置潜艇的期望深度层  
        3、获取单元挂架武器信息, 以列表形式返回  
        4、获取精简信息, 提炼信息进行决策  

        示例：  
        submarine_id = "sflsf0-gjlsf-sf"  # 潜艇guid  
        submarine = self.get_unit(submarine_id)  # 获取潜艇对象  
        if submarine is not None:  
            submarine.set_depth(200)  # 潜艇下潜200米  
        """
        Unit.__init__(self, guid, name, side_name, ElementType.Submarine)
        self.DepthPreset = 0  # 潜艇深度预设，含义如下
        """
        0:  None,  无
        1:  Periscope, 潜望镜深度 
        2:  Shallow,  浅层
        3:  OverLayer,  温跃层之上
        4:  UnderLayer, 温跃层之下
        5:  MaxDepth,   最大深度
        6:  Surface   水面
        """
        self.DockingOps = {}  # 停靠码头--结构：THDockingOps 定义请查看entitys/struct.proto文件

    def set_depth(self, depth):
        """
        1、设置潜艇的期望深度
        :param depth: int, 期望深度值, 单位：米，例：200，则期望水下200米深
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_depth(self, depth)

    def set_depth_level(self, depth_level):
        """
        2、设置潜艇的期望深度层
        :param depth_level: str, "CURRENT":当前设置的当前的深度；"OFF":不勾选手动控制，
                            "DESIRED":当前设置的期望深度,即勾选手动控制高度
                            期望深度层：'SURFACE'：水面;'PERISCOPE':潜望深度;'SHALLOW':浅的;
                            'OVERLAYER':温跃层上;'UNDERLAYER':温跃层下;'MAXDEPTH':尽可能深
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_depth_level(self, depth_level)

    def get_weapon_infos(self):
        """
        3、获取单元挂架武器信息, 以列表形式返回
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
        4、获取精简信息, 提炼信息进行决策
        :return: dict
        """
        info_dict = {
            "category": "Submarine",
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

