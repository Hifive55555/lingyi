# -*- coding:utf-8 -*-
# Description: 武器

from .global_util import *
from .unit import Unit


class Weapon(Unit):
    """
    武器类  
    1、获取武器打击目标  
    2、获取精简信息, 提炼信息进行决策  

    示例：  
    weapon_id = "sflsf0-gjlsf-sf"  # 武器guid  
    weapon = self.get_unit(weapon_id)  # 获取武器对象  
    if satellite is not None:  
        weapon_target = weapon.get_primary_target()  # 获取武器打击目标信息  
        weapon.Lon  # 武器经度  
    """
    def __init__(self, guid, name, side_name):
        Unit.__init__(self, guid, name, side_name, ElementType.Weapon)
        self.ImpactAltitude = 0.0  # 撞击高度
        self.CEPSurface = 0.0  # 圆概率误差(表示导弹命中精度)_水面
        self.CEPLand = 0.0  # 圆概率误差(表示导弹命中精度)_陆地
        self.FiringParent = ""  # 发射父单元ID
        self.Warheads = {}  # 弹头，即战斗部--结构dict<string, THWarhead>，key:弹头guid
        self.Guidance = 0  # 制导方式，含义如下：
        """
        SemiActive = 0,//半主动
        Inertial_Plus_SemiActive = 1,//惯性与半主动
        Datalink_Plus_SemiActive = 2,//数据链与半主动
        Passive = 4,//被动
        Inertial_Plus_Passive = 5,//惯性与被动
        DataLink_Plus_Passive = 6,//数据链与被动
        Active = 7,//主动
        Datalink_Plus_Active = 8,//数据链与主动
        Inertial_Plus_Active = 9,//惯性与主动
        CommandGuided_Datalinked = 10,//数据链指挥引导
        TVM = 11,//Track Via Missile导弹跟踪
        BeamRiding = 12,//光束扫描
        Inertial = 13,//惯性
        SemiActive_Plus_Active = 14,//半主动与主动
        TimesharedSemiActive_Plus_Active = 0xF//分时半主动与主动
        """

    def get_primary_target(self):
        """
        1、获取武器打击目标
        :return: str, 打击目标id
        """
        if 'PrimaryTarget' in self.AI:
            return self.AI['PrimaryTarget']
        else:
            return ""

    def get_summary_info(self):
        """
        2、获取精简信息, 提炼信息进行决策
        :return: dict
        """
        info_dict = {
            "category": "Weapon",
            "guid": self.ID,
            "dbid": self.DBID,
            "name": self.Name,
            "lat": self.Lat,
            "lon": self.Lon,
            "alt": self.CurrentAltitude,
            "course": self.get_way_points_info(),
            "head": self.CurrentHeading,
            "speed": self.CurrentSpeed,
            "fuel": self.FuelRecs,
            "status": self.Status,
            "sensors": self.Sensors,
            "mounts": None,
            "shooter": self.FiringParent,
            'target': self.AI['PrimaryTarget'] if 'PrimaryTarget' in self.AI else ""
        }
        return info_dict

