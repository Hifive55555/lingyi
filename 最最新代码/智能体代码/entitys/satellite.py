# -*- coding:utf-8 -*-
# Author: Liaojiang
# Description: 卫星

from .global_util import *
from .unit import Unit


class Satellite(Unit):
    """
    卫星类  
    1、获取精简信息, 提炼信息进行决策  

    示例：  
    satellite_id = "sflsf0-gjlsf-sf"  # 卫星guid  
    satellite = self.get_unit(satellite_id)  # 获取卫星对象  
    if satellite is not None:  
        reply = satellite.EMCON_Obey_doctrine(False)  # 设置卫星不遵循电磁管控条令  
        reply = satellite.switch_radar(True)  # 设置卫星开启雷达  
    """
    def __init__(self, guid, name, side_name):
        Unit.__init__(self, guid, name, side_name, ElementType.Satellite)

    def get_summary_info(self):
        """
        获取精简信息, 提炼信息进行决策
        :return: dict
        """
        info_dict = {
            "category": "Satellite",
            "guid": self.ID,
            "dbid": self.DBID,
            "name": self.Name,
            "lat": self.Lat,
            "lon": self.Lon,
            "alt": self.CurrentAltitude,
            "sensors": self.Sensors
        }
        return info_dict
