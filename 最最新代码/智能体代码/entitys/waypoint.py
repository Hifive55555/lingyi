# -*- coding:utf-8 -*-

from .global_util import *
from .operatorbase import DoctrineOperator


class Waypoint(DoctrineOperator):
    """
    航路点类  
    设置飞机等单元某航路点的条令、高度等  
    示例：  
    if air.Navigator["PC"]:  
        # 飞机已设置航路点  
        for point in air.Navigator["PC"]:  
            if "GeoPoint" in point:  
                point_id = point["GeoPoint"]["ID"]  
                point_name = point["GeoPoint"]["Name"]  
                point_lat = point["GeoPoint"]["Lat"]  
                if point_lat < 12.6:  
                    air.set_weapoint(point_id, 500, 8000)  # 设置单元航路点速度和高度  
                    if point_name:  
                        air.set_waypoint_sensor(point_name, sensor_id=radar_id, radar=False)  # 设置单元航路点雷达关闭  
                    waypoint = air.get_way_point(point_id, point_name)  # 获取航路点对象    
                    waypoint.doctrine_weapon_control_status_surface(WeaponControlStatus.Free)  # 设置航路点条令  
                elif point_lat < 12.95:  
                    air.set_weapoint(point_id, 600, 3000)  # 设置单元航路点速度和高度  
                    if point_name:  
                        air.set_waypoint_sensor(point_name, sensor_id=radar_id, radar=True)  # 设置单元航路点雷达关闭  
                    waypoint = air.get_way_point(point_id, point_name)  # 获取航路点对象    
                    waypoint.doctrine_weapon_control_status_subsurface(WeaponControlStatus.Hold)  # 设置航路点条令  
                self.air_alt_set = True  
    else:  
        # 还没有设置航路点  
        air.plotted_course([(12.4, -88.5, 'A1'), (12.9, -89.6, 'A2'), (14.5, -90.6, 'A3')])  # 设置飞机航路    
    """
    def __init__(self, guid, name, side_name, unit_id, game_server):
        sel_category = SelectorCategory.WayPoint
        DoctrineOperator.__init__(self, guid, name, side_name, sel_category, ElementType.WayPoint, unit_id)
        self.Lon = 0.0  # 航路点纬度
        self.Lat = 0.0  # 航路点经度
        self._game_server = game_server

    def get_summary_info(self):
        """
        获取精简信息, 提炼信息进行决策
        :return: dict
        """
        info_dict = {
            "category": "WayPoint",
            "guid": self.ID,
            "name": self.Name,
            "latitude": self.Lat,
            "longitude": self.Lon,
        }
        return info_dict
