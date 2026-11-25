# -*- coding:utf-8 -*-
# Author: Liao
# Description: 单元（飞机、舰船等单元通用）

from .global_util import *
from .waypoint import Waypoint
from .gameunit import GameUnit


class Unit(GameUnit):
    """
    作战单元（飞机、防空导弹和雷达站等，不包含武器和传感器）的其他操作：  
        获取详细信息  
        攻击作战行动：自动攻击，手动分配武器攻击，纯方位攻击  
        反潜作战行动：投放声呐  
        航线规划  
        设置油门，期望速度和期望高度  
        航线规划  
        空中作战行动（对飞机下达起飞指令）  
        分配任务和退出已加入任务  

    单元类  
    1、获取挂架上的武器信息  
    2、获取挂架统计的武器信息  
    3、获取单元航路点列表  
    4、获取挂架上武器的挂架ID和武器数量  
    5、获取当前单元目标列表  
    6、实体传感器面板， 实体是否遵循电磁管控条令  
    7、实体传感器面板， 实体雷达开关机  
    8、实体传感器面板， 实体声呐开关机  
    9、实体传感器面板， 实体电子干扰开关机  
    10、实体传感器面板， 实体激光传感器开关机  
    11、自动攻击目标  
    12、查询手动攻击信息  
    13、手动攻击，指定武器挂架、武器ID和武器数量打击某目标  
    14、手动攻击，指定武器ID和武器数量打击某目标  
    15、纯方位攻击  
    16、取消武器攻击，需运行推演后调用  
    17、单元释放一个箔条弹  
    18、箔条连续爆破  
    19、实体放弃某个之前设定的目标  
    20、实体放弃所有目标，脱离接战  
    21、反潜作战行动  
    22、设置单元的期望速度  
    23、设置实体油门  
    24、设置飞机或者潜艇手动控制高度  
    25、设置飞机单元的期望高度  
    26、设置当前单元（飞机）的飞行高度跟随地形  
    27、实体航线规划  
    28、单元清除航路点  
    29、给单元航路点设置速度和高度  
    30、单元的航路点设置传感器  
    31、设定参考点相对于本单元固定方位距离或者相对本单元航向固定旋转，或取消关联  
    32、实体返航  
    33、实体选择新基地/新港口  
    34、加油/补给  
    35、保持阵位-所选单元  
    36、分配加入到任务中  
    37、将单元分配为某打击任务的护航任务  
    38、将单元取消分配任务  
    39、设置单元优先挂载武器  
    40、空中行动、船舶出动业务装卸物资  
    41、获取某单元的航路点对象, 航路点对象可调用条令接口设置航路点条令  
    42、手动攻击里设置、取消武器攻击弹道

    示例：  
    air1_id = "sflsf0-gjlsf-sf"  # 飞机guid  
    air1 = self.get_unit(air1_id)  # 获取飞机对象  
    if air1 is not None:  
        reply = air1.get_weapon_info()  # 获取此飞机挂架上的武器信息  
        air1.switch_radar(True)  # 单元打开雷达  
        air1.set_throttle(Throttle.Cruise)  # 设置单元巡航油门  
    """
    def __init__(self, guid, name, side_name, element_type):
        sel_category = SelectorCategory.Unit
        if element_type == ElementType.Group:
            sel_category = SelectorCategory.Group
        GameUnit.__init__(self, guid, name, side_name, sel_category, element_type)
        # THSidePosition结构中属性：
        self.Lon = 0.0  # 经度
        self.Lat = 0.0  # 纬度
        self.CurrentAltitude = 0.0  # 当前高度
        self.CurrentHeading = 0.0  # 朝向
        self.Pitch = 0.0  # 纵摇，俯仰角
        self.Roll = 0.0  # 横摇，滚转角

        # THActiveUnit结构中属性：
        self.CurrentSpeed = 0.0  # 当前速度  海里/小时
        self.Acc = 0.0  # 加速度/过载
        self.CargoToMission = ""  # 物资所属任务
        self.DockingCondition = False  # 值为false时不在界面显示  false为停靠状态
        self.Throttle = 0  # 油门状态  0:悬停 1:慢速  2：巡航  3：全速  4：加力
        self.Status = 0  # 活动单元状态
        self.FuelState = 0  # 油量状态
        self.WeaponState = 0  # 武器状态
        self.DesiredSpeed = 0.0  # 期望速度
        self.DesiredAltitude = 0.0  # 期望高度
        self.DamagePts = 0.0  # 损毁Pts值
        self.DamagePercent = 0.0  # 生命值、损毁百分比
        self.AssignedMission = ""  # 分配任务GUID
        self.GroupID = ""  # 编组ID
        self.IsAD = False  # 是否被自动检测
        # THAI,THWeaponry,THComponentCommDevice等结构定义请查看entitys/struct.proto文件
        self.AI = {}  # AI决策---结构：THAI
        self.Weaponry = {}  # 武器分配信息---结构：THWeaponry
        self.Kinematics = {}  # 机动模块---结构：THKinematics
        self.Navigator = {}  # 导航---结构：THNavigator
        self.Damage = {}  # 单元毁伤：失火和进水---结构：THDamage
        self.Sensory = {}  # 单元是否遵守电磁管控---结构：THSensory
        self.CommDevices = {}  # 通信设备字典---结构：dict:<string, THComponentCommDevice>，key:通信设备guid
        self.Sensors = {}  # 传感器字典---结构：dict<string, THComponentSensor>，key:传感器guid
        self.Mounts = {}  # 挂架字典,包含打击范围---结构：dict<string, THComponentMount>，key:挂架guid
        self.Magazines = {}  # 弹药库字典---结构：dict<string, THComponentMagazine>，key:弹药库guid
        self.Cargos = {}  # 装载物资字典---结构：dict<string, THComponentCargo>，key:货物guid
        self.AirFacilitys = {}  # 航空设施字典---结构：dict<string, THComponentAirFacility>，key:航空设施guid
        self.DockFacilitys = {}  # 舰艇停靠设施字典---结构：dict<string, THComponentDockFacility>，key:舰艇停靠设施guid
        self.Propulsions = {}  # 发动机字典---结构：dict<string, THComponentPropulsion>，key:发动机guid
        self.FuelRecs = {}  # 燃料字典---结构：dict<string, THFuelRec>，key:燃料guid
        self.Loadouts = {}  # 挂载方案---结构：dict<string, THLoadout>，key:挂载方案guid
        self.RangeSymbols = {}  # 新探测范围---结构：dict<string, THRangeSymbol>，key:范围guid
        self.Source = 0  # 数据来源 0：虚拟添加，1：实时数据
        self.CommStuff = {}  # 通信模块---结构：THCommStuff

        # THActiveUnitInfo结构中属性：
        self.Category = 0  # 大类-例如2002：水面战斗舰艇
        self.Type = 0  # 实体类型  (暂不使用，各类型的实体类型在各自结构体中体现）
        self.DBID = 0  # 数据库实体ID
        """
        0:  Novice,//新手
        1:	Cadet,//学员
        2:	Regular,//一般
        3:	Veteran,//老手
        4:	Ace//高手
        """
        self.ProficiencyLevel = 2  # 熟练程度, 参考以上定义
        self.XSections = {}  # 信号特征参数---结构：THVectorXSection二进制序列化
        self.UnitType = 0  # 实体类型（飞机或船）（0:编组, 1:飞机 2:水面舰艇 3:潜艇 4:设施 6:武器 7:卫星）

    def get_weapon_info(self):
        """
        1、获取挂架上的武器信息
        :return: dict, 挂架上的武器id和数量
        """
        weapon_info = {}
        for k, v in self.Mounts.items():
            if "WeaponRecs" in v:
                for rid, w in v["WeaponRecs"].items():
                    count = w["CurrentLoad"]
                    if count > 0:
                        weaponid = w["WeaponDBID"]
                        count = w["CurrentLoad"]
                        if weaponid in weapon_info:
                            weapon_info[weaponid] += count
                        else:
                            weapon_info[weaponid] = count
        return weapon_info

    def get_mounts_weapon_info(self):
        """
        2、获取挂架统计的武器信息
        :return: list, 挂架上的武器统计信息
        """
        info = []
        for id, mount_info in self.Mounts.items():
            if "Component" in mount_info and "WeaponRecs" in mount_info:
                m_info = {}  # 武器id和数量
                for rid, w in mount_info["WeaponRecs"].items():
                    weaponid = w["WeaponDBID"]
                    count = w["CurrentLoad"]
                    if weaponid in m_info:
                        m_info[weaponid] += count
                    else:
                        m_info[weaponid] = count
                info.append({
                    "mount_guid": id,
                    "mount_dbid": mount_info["Component"]["DBID"],
                    "mount_name": mount_info["Component"]['Name'],
                    "mount_weapons": m_info
                })
        return info

    def get_way_points_info(self):
        """
        3、获取单元航路点列表
        :return: list, 单元航路点列表
        """
        points = []
        if self.Navigator:
            if "PC" in self.Navigator:
                for point in self.Navigator["PC"]:
                    if "GeoPoint" in point and "Lon" in point["GeoPoint"]:
                        points.append({
                            "longitude": point["GeoPoint"]["Lon"],
                            "latitude": point["GeoPoint"]["Lat"],
                            "name": point["GeoPoint"]["Name"],
                            "ID": point["GeoPoint"]["ID"]})
        return points

    def weapon2mount(self):
        """
        4、获取挂架上武器的挂架ID和武器数量
        :return: dict, 武器信息
        """
        weapon_mount_info = {}
        for k, v in self.Mounts.items():
            if "Component" in v and "DBID" in v["Component"]:
                mount_dbid = v["Component"]["DBID"]
            else:
                continue
            if "WeaponRecs" in v:
                for rid, w in v["WeaponRecs"].items():
                    weaponid = w["WeaponDBID"]
                    count = w["CurrentLoad"]
                    mount_weapon_infor = {"mount": mount_dbid, "count": count}
                    if weaponid not in weapon_mount_info:
                        weapon_mount_info[weaponid] = [mount_weapon_infor]
                    else:
                        weapon_mount_info[weaponid].append(mount_weapon_infor)
        return weapon_mount_info

    def get_targets(self):
        """
        5、获取当前单元目标列表
        :return: list, 目标列表
        """
        if isinstance(self.AI, dict):
            if "TargetList" in self.AI and isinstance(self.AI["TargetList"], dict):
                return list(self.AI["TargetList"].keys())
        else:
            return []

    # ---------------------传感器部面板设置------------------------
    def EMCON_Obey_doctrine(self, is_obey):
        """
        6、实体传感器面板， 实体是否遵循电磁管控条令
        :param is_obey: bool(True 或 False) False表示”不需要管控电磁条令，用户可随意开启、关闭雷达、声纳、电子干扰“
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_EMCON_Obey_doctrine(self, is_obey)

    def switch_radar(self, switch_on, radar_id=""):
        """
        7、实体传感器面板， 实体雷达开关机
        雷达开启前，必须确保”实体是否遵循电磁管控条令“为False，即False表示”不需要管控电磁条令，用户可随意开启、关闭雷达、声纳、电子干扰“
        :param switch_on: bool(True 或 False)
        :param radar_id: str 雷达传感器ID
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_switch_radar(self, switch_on, radar_id)

    def switch_sonar(self, switch_on, sonar_id=""):
        """
        8、实体传感器面板， 实体声呐开关机
        声纳开启前，必须确保”实体是否遵循电磁管控条令“为False，即False表示”不需要管控电磁条令，用户可随意开启、关闭雷达、声纳、电子干扰“
        :param switch_on: bool(True 或 False)
        :param sonar_id: str 声呐传感器ID
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_switch_sonar(self, switch_on, sonar_id)

    def switch_OECM(self, switch_on, sensor_id=""):
        """
        9、实体传感器面板， 实体电子干扰开关机
        电子干扰开启前，必须确保”实体是否遵循电磁管控条令“为False，即False表示”不需要管控电磁条令，用户可随意开启、关闭雷达、声纳、电子干扰“
        :param switch_on: bool(True 或 False)
        :param sensor_id: str 电子干扰传感器ID
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_switch_OECM(self, switch_on, sensor_id)

    def switch_laser(self, laser_sensor_id, switch_on):
        """
        10、实体传感器面板， 选择某激光传感器进行开关
        设置某激光传感器开关前，必须确保”实体是否遵循电磁管控条令“为False，即False表示”不需要管控电磁条令，用户可随意开关传感器“
        :param laser_sensor_id: str 需设置的激光传感器ID
        :param switch_on: bool(True 或 False)
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_switch_laser(self, switch_on, laser_sensor_id)

    # ---------------------选择实体，鼠标右键操作------------------------
    def attack_auto(self, contact_guid):
        """
        11、自动攻击目标
        :param contact_guid: str, 目标guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_attack_auto(self, contact_guid)

    def attack_target_info(self, contact_guid):
        """
        12、查询手动攻击信息
        :param contact_guid: str, 目标guid
        :return: str, 本单元打击目标信息
        """
        return self._game_server.api_attack_target_info(self, contact_guid)

    def attack_manual(self, contact_guid, mount_num, weapon_id, qty_num):
        """
        13、手动攻击，指定武器挂架、武器ID和武器数量打击某目标
        注意：查看单元挂架mounts下 武器的WeaponRecs下CurrentLoad为0时，表示武器当前数量为0，为0时武器不可用于执行攻击
        :param contact_guid: str, 目标guid
        :param mount_num: int, 攻击者的装具 DBID，如果不指定挂架，则可传0
        :param weapon_id: int, 攻击者的武器 DBID
        :param qty_num: int, 分配武器数量
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_attack_manual(self, contact_guid, mount_num, weapon_id, qty_num)

    def attack_weapon_allocate_to_target(self, contact_guid, weapon_id, qty_num, weapon_course=[]):
        """
        14、手动攻击，指定武器ID和武器数量打击某目标
        注意：查看单元挂架mounts下 武器的WeaponRecs下CurrentLoad为0时，表示武器当前数量为0，为0时武器不可用于执行攻击
        :param contact_guid: str, 目标guid  example: "jfsl-24jl-fjsl242"
        :param weapon_id: int, 武器id  example: 596
        :param qty_num: int 攻击武器数量 example:2
        :param weapon_course: [] 攻击武器航线，example:[(12.4,-91.2),(12.9,-92.2)], 纬度、经度的元组列表；
                            需确认可设置武器航路，例如巡航导弹；注意航路点不可太多，一般不超过5个
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_attack_weapon_allocate_to_target(self, contact_guid, weapon_id, qty_num, 
                                                                      course=weapon_course)

    def attack_BOL(self, lat, lon, mount_num, weapon_id, qty_num):
        """
        15、纯方位攻击
        注意：查看单元挂架mounts下 武器的WeaponRecs下CurrentLoad为0时，表示武器当前数量为0，为0时武器不可用于执行攻击
        飞机纯方位打击时，挂架ID可以置0
        :param lat: float, 目标位置纬度,  example: 24.5
        :param lon: float, 目标位置经度   example: 144.2
        :param mount_num: int, 攻击者的挂架 DBID
        :param weapon_id: int, 攻击者的武器 DBID
        :param qty_num: int, 攻击武器数量
        :example:
            海洋空战.scen 想定，阿利伯克驱逐舰发射战俘导弹纯方位攻击:
            for unit in situation[0]:
                if 'DDG' in unit["name"]:
                    u = self.get_unit(unit["guid"])
                    u.attack_BOL(24.5, 157, 2804, 586, 2)
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_attack_BOL(self, lat, lon, mount_num, weapon_id, qty_num)

    def cancel_attack_contact(self, target_guid, mount_id, weapon_dbid, count):
        """
        16、取消武器攻击，需运行推演后调用
        :param target_guid: str,  敌方目标GUID
        :param mount_id: int, 挂架ID, 为0则表示不指定挂架
        :param weapon_dbid: int, 武器DBID
        :param count: int, 取消武器发射数量
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_cancel_attack_contact(self, target_guid, mount_id, weapon_dbid, count)

    def chaff_burst(self):
        """
        17、单元释放一个箔条弹
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_chaff_burst(self)

    def chaff_continous_burst(self, is_enabled):
        """
        18、箔条连续爆破
        :param is_enabled: bool, 是否开启或关闭连续爆破
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_chaff_continous_burst(self, is_enabled)

    def attack_drop_target(self, contact_guid):
        """
        19、实体放弃某个之前设定的目标
        :param contact_guid: str, 情报目标guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_attack_drop_target(self, contact_guid)

    def attack_drop_target_all(self):
        """
        20、实体放弃所有目标，脱离接战
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_attack_drop_target_all(self)

    def deploy_sonar(self, sonar_type, is_shallow):
        """
        21、反潜作战行动
        :param sonar_type: str, 声呐类型 被动"PASSIVE"、主动"ACTIVE"、吊放"DIPPING"
        :param is_shallow: bool, 是否浅层
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_deploy_sonar(self, sonar_type, is_shallow)

    def set_desired_speed(self, desired_speed):
        """
        22、设置单元的期望速度
        注意：1,飞机等单元必须有航线规划
            2、速度设置超过最大值时，速度被设置为最大速度；速度设置超过最小值时，速度被设置为最小速度
        :param desired_speed: float, 千米/小时
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_desired_speed(self, desired_speed)

    def set_throttle(self, enum_throttle):
        """
        23、设置实体油门
        :param enum_throttle: 枚举Throttle的值, 油门, global_util.py中定义, 例：Throttle.Cruise 巡航
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_throttle(self, enum_throttle)

    def set_alt_manual(self, is_manual):
        """
        24、设置飞机或者潜艇手动控制高度
        :param is_manual: bool, 是手动控制: True； 必须设置是手动控制，才能设置飞行高度层/潜艇深度
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_alt_manual(self, is_manual)

    def set_desired_height(self, desired_height):
        """
        25、设置飞机单元的期望高度
        :param desired_height: int或float, 期望高度值, 海拔高度：米
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_desired_height(self, desired_height)

    def follow_terrain(self, is_fellow):
        """
        26、设置当前单元（飞机）的飞行高度跟随地形
        设置地形跟随，需首先设置飞机手动控制高度，即接口：set_alt_manual设置为True
        :param is_fellow:bool, True:跟随地形
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_follow_terrain(self, is_fellow)

    def plotted_course(self, course_list):
        """
        27、实体航线规划
        :param course_list: list, [(lat, lon)], 例子：[(40, 39.0), (41, 39.0)]或带航路点名称
                                    [(40, 39.0, 'WY1'), (41, 39.0, 'WY2')]
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_plotted_course(self, course_list)

    def clear_plotted_course(self):
        """
        28、单元清除航路点
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_clear_unit_course(self, self.ID)

    def set_weapoint(self, point_id, speed, altitude):
        """
        29、给单元航路点设置速度和高度; 可以通过self.Navigator['PC']获取当前单元航路点
        :param point_id: str, 航路点id
        :param speed: float, 速度, 千米/小时
        :param altitude: float, 高度, 米
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_weapoint(self, point_id, speed/1.852, altitude)

    def set_waypoint_sensor(self, point_name, sensor_id, radar=None, sonar=None, OECM=None):
        """
        30、单元的航路点设置传感器
        :param point_name: str, 航路点名，需设置单元航路时，也传入航路点名称
        :param sensor_id: str, 传感器guid
        :param radar: bool, 开关雷达则赋值, True: 开
        :param sonar: bool, 开关声纳则赋值, True: 开
        :param OECM: bool, 开关电子干扰则赋值, True: 开
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_waypoint_sensor(self, point_name, sensor_id, radar, sonar, OECM)

    def set_waypoint_bearings(self, orient_type, points):
        """
        31、设定参考点相对于本单元固定方位距离或者相对本单元航向固定旋转，或取消关联
        :param orient_type: int, 0.取消 1.旋转 2.固定
        :param points: list, 多个参考点id列表
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_waypoint_bearings(self, orient_type, points)

    def return_to_base(self, is_return=True):
        """
        32、实体返航
        :param is_return: bool, 是否返航； False: 取消返航
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_return_to_base(self, is_unit_return=is_return)

    def select_new_base(self, base_guid):
        """
        33、实体选择新基地/新港口
        :param base_guid: str, 新基地的guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_select_new_base(self, base_guid)

    def refuel(self, refuel_unit_guid="", refuel_missions=[]):
        """
        34、加油/补给
        :param refuel_unit_guid: str, 加油机或补给船的guid, 如果为空，则自动选择加油机/补给船
        :param refuel_missions: [], 加油机或补给船的支援任务名或id列表, 如果为空，则自动选择加油机/补给船或指定加油机
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_refuel(self, refuel_unit_guid, refuel_missions=refuel_missions)

    def hold_positon(self, is_hold):
        """
        35、保持阵位-所选单元
        :param is_hold: bool, True:保持阵位，False:不保持
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        self._game_server.api_hold_positon(self, is_hold)

    def assign_to_mission(self, mission_name):
        """
        36、此单元分配加入到任务中
        :param mission_name: str, 任务名称
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_assign_to_mission(self, mission_name)

    def assign_to_mission_escort(self, mission_name):
        """
        37、将单元分配为某打击任务的护航任务
        :param mission_name: 任务名称
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_assign_to_mission_escort(self, mission_name)

    def withdraw_from_mission(self):
        """
        38、将单元取消分配任务
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_withdraw_from_mission(self)

    def weapon_reload_priority(self, mountid, weaponDBID, enabled):
        """
        39、设置单元优先挂载武器
        :param mountid: 挂架id type: str
        :param weaponDBID: 武器数据库ID  type: int
        :param enabled:是否优先  type：bool
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_weapon_reload_priority(self, mountid, weaponDBID, enabled)

    def cargo_load_ops(self, host_guid, cargo_to_unit, cargo_to_host):
        """
        40、空中行动、船舶出动业务装卸物资
        :param host_guid: str, 实体guid  机场等可容纳飞机、船舶的基地单元GUID
        :param cargo_to_unit: list, 从机场向飞机装载的物资列表
        :param cargo_to_host: list, 从飞机向机场卸载的物资列表
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_cargo_load_ops(self, host_guid, cargo_to_unit, cargo_to_host)

    def get_way_point(self, point_id, name):
        """
        41、获取某单元的航路点对象, 航路点对象可调用条令接口设置航路点条令
        :param point_id: str, 航路点Id
        :param name: str, 航路点名
        :return: 航路点对象, Waypoint实例子，条令设置类DoctrineOperator子类
        """
        waypoint = Waypoint(guid=point_id, name=name, side_name=self.Side, unit_id=self.ID, 
                            game_server=self._game_server)
        return waypoint

    def set_attack_course(self, target, weaponDBID, points=[]):
        """
        42、手动攻击里设置、取消武器攻击弹道,弹道规划,导弹航路
        :param target: str, 被攻击单元guid
        :param weaponDBID: int, 武器DBID
        :param points: list, [(纬度，经度),(纬度，经度)], 导弹航路（如果不赋值，则是取消武器航路） 例:[(24.2,147.2),(24.9,147.8)]
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_attack_course(self, target, weaponDBID, points)


