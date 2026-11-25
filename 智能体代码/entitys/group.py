# -*- coding:utf-8 -*-
# Author:Liao
# Description: 编队

from .global_util import *
from .unit import Unit


class Group(Unit):
    """
    编组类  
    1、获取精简信息, 提炼信息进行决策  
    2、设置编组单元方位  
    3、设置编队领队  

    示例：  
    group_id = "sflsf0-gjlsf-sf"  # 编队guid  
    group1 = self.get_unit(group_id) # 获取编队对象  
    if group1 is not None:  
        reply = group1.set_group_leader("fjlsf-vn2-sdfdgssf") # 设置编队领队  
        group1.set_desired_speed(820) # 设置编队期望速度 820千米/小时  
    """
    def __init__(self, guid, name, side_name):
        Unit.__init__(self, guid, name, side_name, ElementType.Group)
        self.GroupLead = ""  # 领队guid
        self.Members = []  # 编组成员guid列表

    def get_summary_info(self):
        """
        1、获取精简信息, 提炼信息进行决策
        :return: dict 编队提炼信息
        """
        info_dict = {
            "category": "Group",
            "guid": self.ID,
            "name": self.Name,
            "lat": self.Lat,
            "lon": self.Lon,
            "alt": self.CurrentAltitude,
            "GroupLead": self.GroupLead,
        }
        return info_dict

    def set_group_bearing(self, guid, nMode, lon, lat):
        """
        2、设置编组单元方位
        :param guid: str, 单元guid
        :param nMode: int [0 - 绝对(固定) 1 - 相对(旋转)]
        :param lon:	float,	 方位参考点经度
        :param lat:	float,	方位参考点纬度
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_group_bearing(self, guid, nMode, lon, lat)

    def set_group_leader(self, guid):
        """
        3、设置编队领队
        :param guid: str, 编组内领队实体guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_group_leader(self, guid)
