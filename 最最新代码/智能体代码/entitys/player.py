# -*- coding:utf-8 -*-
# Description: 推演方

from abc import ABCMeta
import re
from random import randint

from .global_util import *
from . import commonfunction as cf
from .patrolmission import PatrolMission
from .strikemission import StrikeMission
from .supportmission import SupportMission
from .cargomission import CargoMission
from .minemission import MineMission
from .mineclearmission import MineClearMission
from .ferrymission import FerryMission
from .gameunit import GameUnit

guid_pattern = re.compile("{ guid = '([a-z0-9A-Z-]+)', name = '([^{]+)' }")
name_pattern = re.compile("{ name = '([^=]+)', guid = '([a-z0-9-]+)' }")
guid_ptn = re.compile(r"guid = '([a-z0-9A-Z-]+)',")


class Player(GameUnit):
    """
    推演方类  
    1、通过任务名获取任务对象  
    2、获取实体单元对象  
    3、获取情报信息  
    4、获取当前天气  
    5、获取某点（纬经度）高程  
    6、添加一个或多个参考点  
    7、移动参考点的位置  
    8、删除参考点  
    9、批量增加多个参考点  
    10、分配多个单元到任务  
    11、清除单元所有航路点  
    12、创建巡逻任务  
    13、增加巡逻任务的警戒区  
    14、创建打击任务  
    15、创建支援任务  
    16、创建转场任务  
    17、创建布雷任务  
    18、创建扫雷任务  
    19、创建货运任务  
    20、删除任务  
    21、给任务分配单元  
    22、将若干单元取消分配任务  
    23、将某单元取消分配任务  
    24、删除禁航区或封锁区域  
    25、添加禁航区  
    26、添加封锁区  
    27、添加禁航区或封锁区  
    28、修改禁航区和封锁区  
    29、将多个单元作为一个编队  
    30、分离编组单元  
    31、将单元移除出编队  
    32、编队添加一个单元  
    33、飞机单机出动  
    34、飞机编组出动  
    35、飞机准备/备战，飞机挂载武器  
    36、船舶/潜艇单独出航  
    37、船舶/潜艇编队出航  
    38、船舶/潜艇中止出航  
    39、保持所有单元阵位  
    40、单元选择新基地/新港口  
    41、实体返航  
    42、批量自动攻击某目标  
    43、开火条件检查  
    44、情报标识重命名  
    45、情报标识标记位置  
    46、标识情报阵营  
    47、断开若干情报标识  
    48、修改单元名称  
    49、战前规划时间，可设置飞机挂载  
    50、战前规划时间，对战开始之前，设置本单元经纬度位置或高度或深度或航向  
    51、智能体消息输出接口——纯文本  
    52、智能体消息输出接口——重要情报（202507版本未实现）  
    53、智能体消息输出接口——圆形区域显示（跟随单元）（202507版本未实现）  
    54、智能体消息输出接口——箭头（202507版本未实现）  
    55、智能体消息输出接口——多边形区域（202507版本未实现）  

    示例：  
    air1_id = "sflsf0-gjlsf-sf"  # 飞机guid  
    air1 = self.get_unit(air1_id)  # 获取飞机对象--进而调用飞机、单元接口，设置飞机条令等  
    self.doctrine_fuel_state_rtb(FuelStateRTB.No)  # 设置推演方条令，燃油状态返航，operatorbase.py中接口  
    mission_name = "first_patrol"  
    patrol_area = [(16.1, -92.3), (16.1, -91.2), (14.9, -91.2), (14.9, -92.3)]  # 纬度、经度  
    first_patrol = self.create_patrol_mission(mission_name, MissionPatrolType.AIR, patrol_area)  # 创建巡逻任务  
    select_units_guid = ["air1-fsjlf2sfs", "air2-fsjlf27dg"]  # 飞机列表  
    self.air_single_out(select_units_guid)  # 飞机起飞  
    self.zone_add_no_navigate("no-navi1", patrol_area, [1,2])  # 设置飞机、舰船的禁航区  
    score = self.TotalScore  # 获取此推演方得分  
    """
    __metaclass__ = ABCMeta

    def __init__(self, side_name):
        GameUnit.__init__(self, "", side_name, side_name, SelectorCategory.Side, ElementType.Side)
        self.deduce_remove_mission = None  # 用于删除任务后同步更新到deduce。elements中
        self.deduce_add_unit = None  # 全局新增单元或任务
        self.get_command_check = None  # 获取指令检查对象
        self.log = None  # 平台Log
        self.flag = 0
        # 智能体动态参数，训练时由配置config.py配置，客户端上推演使用调度功能动态配置
        self.client_info = {
            'unit': {},
            'point': {},
            'contact': {}
        }  # 智能体通过此属性获取配置的单元、情报或参考点
        # 智能体调度决策间隔
        self.agent_decision_time = 30  # 推演30秒决策一次（调用一次step）--可自行在智能体类初始化函数里赋值
        self.client_info_simple = {}  # 从前端获取的原始单元、情报或参考点
        self.agent_type = ""  # 强化学习或规则智能体描述
        self.is_rule_agent = True  # 是规则智能体，否则就是强化学习智能体
        self.situation_cache = {}, {}  # get_situation缓存
        self.last_situation_time = 0  # situation_cache缓存的推演时间
        self.simulate_timestamp = 0  # 推演时间戳
        self.client_i = 0
        self.random_point_name = "%s%d%s" % (chr(65 + randint(0, 25)), randint(0, 9), chr(65 + randint(0, 25)))
        self._init()

    def _init(self):
        """
        初始化智能体对象本局推演相关属性（内部接口，智能算法勿动）
        """
        # 每局会被调用，注意不要存储需要不变的属性
        self.reference_point_index_increment = 1  # 创建参考点的自增命名序号

        self.units_of_name = {}
        self.situation_cache = {}, {}  # 缓存重置
        self.missions_obj = {}  # key:mission name, value: Mission任务对象
        self.groups = {}  # key:group guid, value: Group编队对象
        self.aircrafts = {}  # key:aircraft guid, value: Aircraft飞机对象
        self.ships = {}  # key:ship guid, value: Ship舰船对象
        self.submarines = {}  # key:submarine guid, value: Submarine潜艇对象
        self.satellites = {}  # key:satellite guid, value: Satellite卫星对象
        self.facilitys = {}  # key:facility guid, value: Facility地面装备对象
        self.weapons = {}  # key:weapon guid, value: Weapon武器（导弹）对象

        self.simulate_time = ""  # 当前推演时间
        self.time_elapse = 0  # 当前推演已过时间
        self.scenario_duration = 0  # 想定时长（单位：秒）
        self.scenario = None  # 当前想定对象，scenario.py的Scenario对象，可获取想定开始时间，推演速度，天气或全局参考点等信息

        # THSideInfo、THGeoPoint等结构定义请查看entitys/struct.proto文件
        # 结构THSideInfo中属性：（运行过程中变化的数据发送）
        self.Postures = {}  # 立场---结构：dict:<string, int32>，key:推演方guid, value: 含义如下：
        """
        立场值类型含义：
        0：中立
        1: 友方
        2: 非友方
        3: 敌方
        4: 未知
        """
        self.CollectiveResponsibility = False  # 分配集体责任
        self.MapCenter = {}  # 推演方地图中心点--结构：THGeoPoint
        self.CameraAlt = 0.0  # 相机高度
        self.AwarenessLevel = 0  # 意识水平
        """
        0:  Novice,//新手
        1:	Cadet,//学员
        2:	Regular,//一般
        3:	Veteran,//老手
        4:	Ace//高手
        """
        self.ProficiencyLevel = 0  # 熟练程度。参考上面值定义
        self.ScoringDisaster = 0  # 评分设置(完败)
        self.ScoringTriumph = 0  # 评分设置(完胜)
        self.IsAIOnly = False  # 是否电脑控制
        self.CATC = False  # 可以自动跟踪平民
        self.Briefing = ""  # 简报

        # THSide,THDoctrine,THRefPoint等结构定义请查看entitys/struct.proto文件
        # 结构THSide中属性： 席位基础数据（触发式变化）
        self.Doctrine = {}  # 条例---结构：THDoctrine
        self.ReferencePoints = {}  # 参考点---结构：dict:<string, THRefPoint>，key:参考点guid
        self.SpecialActions = {}  # 特殊动作---结构：dict:<string, THSpecialAction>，key:特殊动作guid
        self.ExclusionZones = {}  # 封锁区---结构：dict:<string, THExclusionZone>，key:封锁区guid
        self.NoNavZones = {}  # 禁航区---结构：dict:<string, THNoNavZone>，key:禁航区guid
        self.AirCorridorZones = {}  # 空中走廊---结构：dict:<string, THAirCorridorZone>，key:空中走廊guid

        # 结构THSideReal中属性： 席位实时变化数据（低频变化[暂定每秒一帧]-----实时变化）
        self.ContactAutoIncrement = 0
        self.WeaponSalvos = {}  # 齐射信息---结构：dict:<string, THWeaponSalvo>，key:齐射guid
        self.TotalScore = 0  # 比分
        self.Contacts = {}  # 情报---结构：dict:<string, THContact>，key:情报guid，另外添加Lon, Lat等THPosition中位置属性

        # 20250703版态势协议以下三项已删除, 为兼容之前服务端，这里暂留
        # 结构THSideVitalChange中属性：  席位下数据关键变化（触发式变化-----不需对比差异，此处有值一定是更新数据，按需累加记录）
        self.LoggedMessage = []  # 事件日志信息--THLoggedMessage列表
        self.LastDetections = []  # 被探测到的最近信息记录--THLastDetection列表
        self.AAR = {}  # 损耗信息---结构：THAAR

        # 推演方收到的事件，类型定义请查看envs/utils.py中10行左右，事件类型
        self.KeyMsg = {}  # 收到的关键事件--积累存储，含义如下：
        """
        key: 事件类型，查看envs/utils.py中WEAPON_FIRED_TYPE等事件类型定义
        value：WeaponFiredInfo等结构转json字典的列表, WeaponFiredInfo等请查看entitys/struct.proto文件
        """
        # start.py中配置need_all_side为True，则下面其他推演方信息被赋值
        # 智能体强化学习训练计算奖励或评估智能体效能等情况，本推演方可以获取其他推演方事件或实体单元信息，比赛时不可用
        self.current_players = {}  # key: 推演方名， value: Player对象，从Player对象中可获取所有实体、事件信息
        # 其他推演方，包含敌对、中立、友方，用于获取数据评估或强化学习计算奖励，不可操作其他方单元等
        self.friend_side_units = {}  # key: side name, value: unit dict
        self.simulate_timestamp = 0  # 推演时间戳

    def step(self, time_elapse, situation):
        """
        智能算法子类实现，进行对抗推演，每隔一段时间自动调用
        :param time_elapse:int, 推演仿真时间，单位：秒，取值0-推演总时间秒数
        :param situation: tuple,  units dict, contacts dict
        :return:
        """
        pass

    def initial(self, situation):
        """
        智能算法子类实现，初始化，推演开始前调用，对应战前规划
        可每局推演初始化变量，可赛前规划，可以用于创建任务，修改任务，设置条令，设置作战单元雷达开关机等
        :param situation: tuple, units dict, contacts dict
        :return:
        """
        pass

    def is_done(self):
        """
        智能体主动判断结束本局（智能体应用时无效）
        """
        return False

    def deduction_end(self):
        """
        智能算法子类实现，一局推演结束后，调用的函数，可用于保存模型等
        """
        pass

    # ---------智能体框架调用接口：勿动------------------------------

    def reset(self):
        """
        重置智能体对象的本局相关属性（内部接口，智能算法勿动）
        """
        self._init()

    def update_units_of_names(self):
        """
        更新单元名称影射字典（内部接口，智能算法勿动）
        """
        self.units_of_name = {}
        for id, obj in self.groups.items():
            self.units_of_name[obj.Name] = obj

        for id, obj in self.aircrafts.items():
            self.units_of_name[obj.Name] = obj

        for id, obj in self.ships.items():
            self.units_of_name[obj.Name] = obj

        for id, obj in self.submarines.items():
            self.units_of_name[obj.Name] = obj

        for id, obj in self.satellites.items():
            self.units_of_name[obj.Name] = obj

        for id, obj in self.facilitys.items():
            self.units_of_name[obj.Name] = obj

        for id, obj in self.weapons.items():
            self.units_of_name[obj.Name] = obj

    def update_constant_attribute(self, base_data_player):
        """
        本对象的整数、布尔、字符串、浮点数从数据智能体对象赋值，每步态势更新都赋值（内部接口，智能算法勿动）

        """
        self.simulate_time = base_data_player.simulate_time  # 当前推演时间
        # self.scenario_duration = base_data_player.scenario_duration  # 想定时长（单位：秒）
        # self.CollectiveResponsibility = base_data_player.CollectiveResponsibility  # 分配集体责任
        # self.CameraAlt = base_data_player.CameraAlt  # 相机高度
        # self.AwarenessLevel = base_data_player.AwarenessLevel  # 意识水平
        # self.ProficiencyLevel = base_data_player.ProficiencyLevel  # 熟练程度。参考上面值定义
        # self.ScoringDisaster = base_data_player.ScoringDisaster  # 评分设置(完败)
        # self.ScoringTriumph = base_data_player.ScoringTriumph  # 评分设置(完胜)
        # self.IsAIOnly = base_data_player.IsAIOnly  # 是否电脑控制
        # self.CATC = base_data_player.CATC  # 可以自动跟踪平民
        # self.Briefing = base_data_player.Briefing  # 简报
        self.TotalScore = base_data_player.TotalScore
        self.time_elapse = base_data_player.time_elapse  # 当前推演已过时间
        self.simulate_timestamp = base_data_player.simulate_timestamp

    def update_obj_situation_attribute(self, base_data_player):
        """
        本对象的态势属性的如是空字典，从数据智能体对象赋值，需更新态势才调用；（内部接口，智能算法勿动）
        初始态势赋值后，每步更新态势后，base_data_player的字典、列表赋值后，本对象的属性自动赋值
        """
        if not self.Postures:
            self.Postures = base_data_player.Postures  # 立场---结构：dict:<string, int32>，key:推演方guid
        if not self.MapCenter:
            self.MapCenter = base_data_player.MapCenter  # 推演方地图中心点--结构：THGeoPoint
        if not self.Doctrine:
            self.Doctrine = base_data_player.Doctrine  # 条例---结构：THDoctrine
        if not self.ReferencePoints:
            self.ReferencePoints = base_data_player.ReferencePoints  # 参考点---结构：dict:<string, THRefPoint>，key:参考点guid
        if not self.SpecialActions:
            self.SpecialActions = base_data_player.SpecialActions  # 特殊动作---结构：dict:<string, THSpecialAction>，key:特殊动作guid
        if not self.ExclusionZones:
            self.ExclusionZones = base_data_player.ExclusionZones  # 封锁区---结构：dict:<string, THExclusionZone>，key:封锁区guid
        if not self.NoNavZones:
            self.NoNavZones = base_data_player.NoNavZones  # 禁航区---结构：dict:<string, THNoNavZone>，key:禁航区guid
        if not self.AirCorridorZones:
            self.AirCorridorZones = base_data_player.AirCorridorZones  # 空中走廊---结构：dict:<string, THAirCorridorZone>，key:空中走廊guid
        if not self.WeaponSalvos:
            self.WeaponSalvos = base_data_player.WeaponSalvos  # 齐射信息---结构：dict:<string, THWeaponSalvo>，key:齐射guid
        if not self.Contacts:
            self.Contacts = base_data_player.Contacts  # 情报---结构：dict:<string, THContact>，key:情报guid，另外添加Lon, Lat等THPosition中位置属性

    def update_object_attribute(self, base_data_player):
        """
        本对象的自定义字典、列表从数据智能体对象赋值（内部接口，智能算法勿动）
        初始态势赋值后，每步更新态势后，base_data_player的字典、列表赋值后，本对象的属性自动赋值
        """
        self.ID = base_data_player.ID  # SIDE ID
        self.scenario = base_data_player.scenario
        self.units_of_name = base_data_player.units_of_name
        self.missions_obj = base_data_player.missions_obj  # key:mission name, value: Mission任务对象
        self.groups = base_data_player.groups  # key:group guid, value: Group编队对象
        self.aircrafts = base_data_player.aircrafts  # key:aircraft guid, value: Aircraft飞机对象
        self.ships = base_data_player.ships  # key:ship guid, value: Ship舰船对象
        self.submarines = base_data_player.submarines  # key:submarine guid, value: Submarine潜艇对象
        self.satellites = base_data_player.satellites  # key:satellite guid, value: Satellite卫星对象
        self.facilitys = base_data_player.facilitys  # key:facility guid, value: Facility地面装备对象
        self.weapons = base_data_player.weapons  # key:weapon guid, value: Weapon武器（导弹）对象

        # 结构THSideVitalChange中属性：  席位下数据关键变化（触发式变化-----不需对比差异，此处有值一定是更新数据，按需累加记录）--已删除
        # self.LoggedMessage = base_data_player.LoggedMessage  # 事件日志信息--THLoggedMessage列表
        # self.LastDetections = base_data_player.LastDetections  # 被探测到的最近信息记录--THLastDetection列表
        # self.AAR = base_data_player.AAR  # 损耗信息---结构：THAAR

        # 推演方收到的事件，类型定义请查看envs/utils.py中10行左右，事件类型
        self.KeyMsg = base_data_player.KeyMsg  # 收到的关键事件--积累存储
        self.current_players = base_data_player.current_players  # 其他推演方，包含敌对、中立、友方
        self.friend_side_units = base_data_player.friend_side_units

        self.Postures = base_data_player.Postures  # 立场---结构：dict:<string, int32>，key:推演方guid
        self.MapCenter = base_data_player.MapCenter  # 推演方地图中心点--结构：THGeoPoint

        self.Doctrine = base_data_player.Doctrine  # 条例---结构：THDoctrine
        self.ReferencePoints = base_data_player.ReferencePoints  # 参考点---结构：dict:<string, THRefPoint>，key:参考点guid
        self.SpecialActions = base_data_player.SpecialActions  # 特殊动作---结构：dict:<string, THSpecialAction>，key:特殊动作guid
        self.ExclusionZones = base_data_player.ExclusionZones  # 封锁区---结构：dict:<string, THExclusionZone>，key:封锁区guid
        self.NoNavZones = base_data_player.NoNavZones  # 禁航区---结构：dict:<string, THNoNavZone>，key:禁航区guid
        self.AirCorridorZones = base_data_player.AirCorridorZones  # 空中走廊---结构：dict:<string, THAirCorridorZone>，key:空中走廊guid

        self.WeaponSalvos = base_data_player.WeaponSalvos  # 齐射信息---结构：dict:<string, THWeaponSalvo>，key:齐射guid
        self.Contacts = base_data_player.Contacts  # 情报---结构：dict:<string, THContact>，key:情报guid，另外添加Lon, Lat等THPosition中位置属性

    def info_extract(self):
        """
        解析智能体单元、目标或参考点等参数（内部接口，智能算法勿动）
        """
        if not isinstance(self.client_info, dict):
            self.client_info = {}
        if 'unit' not in self.client_info or not self.client_info["unit"]:
            self.client_info["unit"] = {}
        if "point" not in self.client_info or not self.client_info["point"]:
            self.client_info["point"] = {}
        if "contact" not in self.client_info or not self.client_info["contact"]:
            self.client_info["contact"] = {}
        if not (self.client_info["unit"] or self.client_info["point"] or self.client_info["contact"]):
            return
        if not (isinstance(self.client_info['unit'], list) or
                isinstance(self.client_info['point'], list) or
                isinstance(self.client_info['contact'], list)):
            return
        temp_unit_dict = {}
        for name in self.client_info['unit']:
            if name in self.units_of_name:
                unit_id = self.units_of_name[name].ID
                temp_unit_dict[unit_id] = {
                    'id': unit_id,
                    'name': name,
                    'situation_keys': []
                }
        temp_point_dict = {}
        for point in self.client_info['point']:
            for reference_points, point_info in self.ReferencePoints.items():
                if point_info['Name'] == point:
                    temp_point_dict[reference_points]: dict = {}
                    temp_point_dict[reference_points]['id'] = reference_points
                    temp_point_dict[reference_points]['name'] = point
                    temp_point_dict[reference_points]['situation_keys'] = []
        temp_contact_dict = {}
        for contact in self.client_info['contact']:
            for c_id, Cont in self.Contacts.items():
                if Cont['Name'] == contact:
                    temp_contact_dict[c_id]: dict = {}
                    temp_contact_dict[c_id]['id'] = c_id
                    temp_contact_dict[c_id]['name'] = contact
                    temp_contact_dict[c_id]['situation_keys'] = []
        self.client_info['unit'] = temp_unit_dict
        self.client_info['point'] = temp_point_dict
        self.client_info['contact'] = temp_contact_dict

    def delete_element(self, del_guid, element_type, unit_name=""):
        """
        删除对象（内部接口，智能算法勿动）
        :param del_guid: str, 删除单元guid
        :param element_type: ElementType枚举值, 单元类型
        :param unit_name: str, 删除单元名
        :return:
        """
        del_list = []
        try:
            if element_type == ElementType.Aircraft:
                del self.aircrafts[del_guid]
            elif element_type == ElementType.Ship:
                del self.ships[del_guid]
            elif element_type == ElementType.Submarine:
                del self.submarines[del_guid]
            elif element_type == ElementType.Satellite:
                del self.satellites[del_guid]
            elif element_type == ElementType.Facility:
                del self.facilitys[del_guid]
            elif (element_type == ElementType.SupportMission
                  or element_type == ElementType.StrikeMission
                  or element_type == ElementType.PatrolMission
                  or element_type == ElementType.FerryMission
                  or element_type == ElementType.MineMission
                  or element_type == ElementType.MineClearMission
                  or element_type == ElementType.CargoMission):
                if unit_name in self.missions_obj:
                    del self.missions_obj[unit_name]
            elif element_type == ElementType.Weapon:
                del self.weapons[del_guid]
            elif element_type == ElementType.Group:
                del self.groups[del_guid]
        except Exception as e:
            if self.log is not None:
                self.log.error("错误！删除推演方-%s-中元素，但不存在：%s" % (self.Name, str(e)))
            else:
                print("错误！删除推演方-%s-中元素，但不存在：%s" % (self.Name, str(e)))
        del_list.append(del_guid)
        return del_list

    def set_agent_decision_time(self, time: int):
        """
        设置智能体调度时调用的决策间隔，决策间隔为仿真时间s（内部接口，智能算法勿动）
        :param time: int, 秒，智能体客户端应用时设置决策间隔
        """
        self.agent_decision_time = time

    def set_simulate_time(self, str_simulate_time):
        """
        设置推演时间（内部接口，智能算法勿动）
        :param str_simulate_time: str, 当前推演时间
        """
        self.simulate_time = str_simulate_time

    def set_scenario_duration(self, scenario_duration):
        """
        设置推演想定时长（内部接口，智能算法勿动）
        :param scenario_duration: int, 秒，想定时长
        """
        self.scenario_duration = scenario_duration

    def set_time_elapse(self, time_elapse):
        """
        设置推演已过时间（内部接口，智能算法勿动）
        :param time_elapse: int, 秒，推演已过时间
        """
        self.time_elapse = time_elapse

    def get_situation(self):
        """
        获取当前态势（内部接口，智能算法勿动）
        :return: tuple, 例: {unit_id1:unit1_info, unit_id2:unit2_info}, {contact_id1:contact1_info, contact_id2:contact2_info}
        """
        if self.situation_cache[0] and self.time_elapse < self.last_situation_time + 0.05:
            # 最小区分态势推进50毫秒
            return self.situation_cache
        else:
            unit_info = {}
            for guid, unit in self.aircrafts.items():
                unit_info[guid] = unit.get_summary_info()
            for guid, unit in self.facilitys.items():
                unit_info[guid] = unit.get_summary_info()
            for guid, unit in self.ships.items():
                unit_info[guid] = unit.get_summary_info()
            for guid, unit in self.submarines.items():
                unit_info[guid] = unit.get_summary_info()
            for guid, unit in self.satellites.items():
                unit_info[guid] = unit.get_summary_info()
            for guid, unit in self.weapons.items():
                unit_info[guid] = unit.get_summary_info()
            for guid, unit in self.groups.items():
                unit_info[guid] = unit.get_summary_info()
            self.situation_cache = unit_info, self.Contacts
            self.last_situation_time = self.time_elapse
            return self.situation_cache

    def get_zone_str(self, point_list):
        """
        获取任务点形成的lua脚步参数（内部接口，智能算法勿动）
        :param point_list: list, 参考点列表
        :return: str, lua脚本参数
        """
        if not point_list:
            return ""

        point_names = []
        if isinstance(point_list[0], str):
            for name in point_list:
                point_names.append('"' + name + '"')
        else:
            # 创建参考点
            names = self.reference_point_add(point_list)
            for name in names:
                point_names.append('"' + name + '"')
        return 'Zone={' + ','.join(point_names) + '}'

    def get_prosecution_zone(self, point_list):
        """
        获取任务点(警戒区)形成的lua脚步参数（内部接口，智能算法勿动）
        :param point_list: list, 参考点列表
        :return: str, lua脚步参数
        """
        if not point_list:
            return ""

        point_names = []
        if isinstance(point_list[0], str):
            for name in point_list:
                point_names.append('"' + name + '"')
        else:
            # 创建参考点
            names = self.reference_point_add(point_list)
            for name in names:
                point_names.append('"' + name + '"')
        return 'prosecutionZone={' + ','.join(point_names) + '}'

    def save_mission(self, mission_name, mission_return_str, mission_category):
        """
        保存任务到本方，方便以后调用（内部接口，智能算法勿动）
        :param mission_name: 任务名
        :param mission_return_str: 任务调用返回值
        :param mission_category: ElementType, 任务类型
        :return: Mission, Mission实例
        """
        new_mission = None
        mission_guid = cf.mission_guid_parser(mission_return_str)
        if mission_category == ElementType.PatrolMission:
            new_mission = PatrolMission(mission_guid, mission_name, self.Name)
        elif mission_category == ElementType.StrikeMission:
            new_mission = StrikeMission(mission_guid, mission_name, self.Name)
        elif mission_category == ElementType.SupportMission:
            new_mission = SupportMission(mission_guid, mission_name, self.Name)
        elif mission_category == ElementType.FerryMission:
            new_mission = FerryMission(mission_guid, mission_name, self.Name)
        elif mission_category == ElementType.CargoMission:
            new_mission = CargoMission(mission_guid, mission_name, self.Name)
        elif mission_category == ElementType.MineMission:
            new_mission = MineMission(mission_guid, mission_name, self.Name)
        elif mission_category == ElementType.MineClearMission:
            new_mission = MineClearMission(mission_guid, mission_name, self.Name)
        if new_mission is not None:
            self.missions_obj[mission_name] = new_mission
            self.deduce_add_unit(mission_guid, new_mission)
            new_mission._game_server = self._game_server
            if mission_category == ElementType.StrikeMission:
                new_mission.escort._game_server = self._game_server
        return new_mission

    # ---------智能体可调用接口：------------------------------

    def get_mission_by_name(self, mission_name):
        """
        1、通过任务名获取任务对象
        :param mission_name: str，任务名
        :return: 任务对象
        """
        if mission_name in self.missions_obj:
            return self.missions_obj[mission_name]
        else:
            return None

    def get_unit(self, guid):
        """
        2、获取实体单元对象
        :param guid: str, 实体guid
        :return: Unit, 作战单元对象
        """
        if guid in self.aircrafts:
            return self.aircrafts[guid]
        if guid in self.ships:
            return self.ships[guid]
        if guid in self.submarines:
            return self.submarines[guid]
        if guid in self.satellites:
            return self.satellites[guid]
        if guid in self.facilitys:
            return self.facilitys[guid]
        if guid in self.weapons:
            return self.weapons[guid]
        if guid in self.groups:
            return self.groups[guid]
        return None

    def get_contact(self, contact_guid):
        """
        3、获取情报信息
        :param contact_guid:  情报对象guid, 非实际单元guid
        :return: dict 如果存在此情报id, 否则返回None
        """
        if contact_guid in self.Contacts:
            return self.Contacts[contact_guid]
        else:
            return None

    def get_weather(self):
        """
        4、获取当前天气
        :return: str, 当前前天数据
        """
        return self._game_server.api_get_weather(self)

    def get_elevation(self, coord_point):
        """
        5、获取某点（纬经度）高程----勿智能体训练或调度时大规模调用，以防服务器过载！
        :param coord_point: tuple, (float, float) (lat, lon)
        :return: int, 地形高程数据
        """
        return self._game_server.api_get_elevation(self, coord_point)

    def reference_point_add(self, points):
        """
        6、添加一个或多个参考点
        :param points: tuple, 或list,  参考点列表,例:(40.2, 49.6) 或 [(40, 39.0), (41, 39.0)]，其中纬度值在前，经度值在后
                                                或者 (40.2, 49.6, 'RP002') 或 [(40, 39.0, 'RP1'), (41, 39.0, 'RP2')]，已传入参考点命名
        :return: list, 按顺序添加成功的参考点名列表
        """
        return self._game_server.api_reference_point_add(self, points)

    def reference_point_move(self, rp_name, new_coord):
        """
        7、移动参考点的位置
        :param rp_name: str, 参考点名称
        :param new_coord: tuple, 新的纬度、经度位置 (lat, lon)
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_reference_point_move(self, rp_name, new_coord)

    def reference_point_delete(self, rp_name):
        """
        8、删除参考点
        :param rp_name:  str, 参考点名称
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        self._game_server.api_reference_point_delete(self, rp_name)

    def add_reference_point_list(self, points):
        """
        9、批量增加多个参考点
        :param points: list, 参考点列表，格式：[(50.2,149,'RP-1'),(51,149.6,'RP-2')] 纬度，经度和名称
                                    或不指定参考点名：[(50.2,149),(51,149.6)] 纬度，经度
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_add_reference_point_list(self, points)

    def assign_units_to_mission(self, unit_list, mission_name, is_escort=False):
        """
        10、分配多个单元到任务
        :param unit_list: list, 实体guid列表
        :param mission_name: str, 分配的任务名
        :param is_escort: bool, 是否打击任务的护航任务
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_assign_units_to_mission(self, unit_list, mission_name, is_escort)

    def clear_unit_course(self, guid):
        """
        11、清除单元所有航路点
        :param guid: str, 单元guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        self._game_server.api_clear_unit_course(self, guid)

    def create_patrol_mission(self, name, mission_type, point_list):
        """
        12、创建巡逻任务, 例子：
            create_patrol_mission('空战巡逻中央区', MissionPatrolType.AIR, [(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)])
        :param name: str, 任务名
        :param mission_type: MissionPatrolType, 任务类型
        :param point_list: list, 参考点列表,例:[(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)]，其中纬度值在前，经度值在后，(40, 39.0)中,latitude = 40, longitude = 39.0
                            或者[(40, 39.0, 'RP1'), (41, 39.0, 'RP2'), (41, 40.0, 'RP3'), (40, 40.0, 'RP4')]
                            或者['RP1', 'RP2'，'RP3'，'RP4']，传入参考点名称要求提前创建好参考点
        :return: PatrolMission, 任务实体
        """
        return self._game_server.api_create_patrol_mission(self, name, mission_type, point_list)

    def add_prosecution_zone(self, mission_name, point_list):
        """
        13、增加巡逻任务的警戒区
        :param mission_name: str, 任务名
        :param point_list: list, list, 参考点列表,例:[(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)]，其中纬度值在前，经度值在后，(40, 39.0)中,latitude = 40, longitude = 39.0
                            或者[(40, 39.0, 'RP1'), (41, 39.0, 'RP2'), (41, 40.0, 'RP3'), (40, 40.0, 'RP4')]
                            或者['RP1', 'RP2'，'RP3'，'RP4']，传入参考点名称要求提前创建好参考点
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_add_prosecution_zone(self, mission_name, point_list)

    def create_strike_mission(self, name, mission_type):
        """
        14、创建打击任务
        :param name: str, 任务名
        :param mission_type: MissionStrikeType, 打击任务类型，对空打击，对地打击等
        :return: StrikeMission, 任务实体
        """
        return self._game_server.api_create_strike_mission(self, name, mission_type)

    def create_support_mission(self, name, point_list):
        """
        15、创建支援任务, 例子：
            create_support_mission('空中支援', [(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)])
        :param name: str, 任务名
        :param point_list: list, 参考点列表,例:[(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)]，其中纬度值在前，经度值在后，(40, 39.0)中,latitude = 40, longitude = 39.0
                            或者[(40, 39.0, 'RP1'), (41, 39.0, 'RP2'), (41, 40.0, 'RP3'), (40, 40.0, 'RP4')]
                            或者['RP1', 'RP2'，'RP3'，'RP        4']，传入参考点名称要求提前创建好参考点
        :return: SupportMission, 任务实体
        """
        return self._game_server.api_create_support_mission(self, name, point_list)

    def create_ferry_mission(self, name, destination):
        """
        16、创建转场任务
        :param name: str, 任务名
        :param destination: str, 目的地guid
        :return: FerryMission, 任务实体
        """
        return self._game_server.api_create_ferry_mission(self, name, destination)

    def create_mine_mission(self, name, point_list):
        """
        17、创建布雷任务, 例子：
            create_mine_mission('布雷2', [(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)])
        :param name: str, 任务名
        :param point_list: list, 参考点列表,例:[(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)]，其中纬度值在前，经度值在后，(40, 39.0)中,latitude = 40, longitude = 39.0
                            或者[(40, 39.0, 'RP1'), (41, 39.0, 'RP2'), (41, 40.0, 'RP3'), (40, 40.0, 'RP4')]
                            或者['RP1', 'RP2'，'RP3'，'RP        4']，传入参考点名称要求提前创建好参考点
        :return: MineMission, 任务实体
        """
        return self._game_server.api_create_mine_mission(self, name, point_list)

    def create_mineclear_mission(self, name, point_list):
        """
        18、创建扫雷任务, 例子：
            create_mineclear_mission('绝对扫雷', [(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)])
        :param name: str, 任务名
        :param point_list: list, 参考点列表,例:[(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)]，其中纬度值在前，经度值在后，(40, 39.0)中,latitude = 40, longitude = 39.0
                            或者[(40, 39.0, 'RP1'), (41, 39.0, 'RP2'), (41, 40.0, 'RP3'), (40, 40.0, 'RP4')]
                            或者['RP1', 'RP2'，'RP3'，'RP        4']，传入参考点名称要求提前创建好参考点
        :return: MineClearMission, 任务实体
        """
        return self._game_server.api_create_mineclear_mission(self, name, point_list)

    def create_cargo_mission(self, name, point_list):
        """
        19、创建货运任务
        :param name: str, 任务名
        :param point_list: list, 参考点列表,例:[(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)]，其中纬度值在前，经度值在后，(40, 39.0)中,latitude = 40, longitude = 39.0
                            或者[(40, 39.0, 'RP1'), (41, 39.0, 'RP2'), (41, 40.0, 'RP3'), (40, 40.0, 'RP4')]
                            或者['RP1', 'RP2'，'RP3'，'RP        4']，传入参考点名称要求提前创建好参考点
        :return: CargoMission, 任务实体
        """
        return self._game_server.api_create_cargo_mission(self, name, point_list)

    def delete_mission(self, mission_name):
        """
        20、删除任务
        :param mission_name: str, 任务名称
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_delete_mission(self, mission_name)

    def assign_unit_mission(self, unit_id, mission_name):
        """
        21、给任务分配单元
        :param unit_id: str, 单元guid
        :param mission_name: str, 拟分配的任务名
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_assign_unit_mission(self, unit_id, mission_name)

    def units_withdraw_from_mission(self, units):
        """
        22、将若干单元取消分配任务
        :param units: list, 取消任务的单元guid列表
        :return: None
        """
        self._game_server.api_units_withdraw_from_mission(self, units)

    def del_unit_from_mission(self, unit_guid):
        """
        23、将某单元取消分配任务
        :param unit_guid: str, 单元guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_del_unit_from_mission(self, unit_guid)

    def zone_remove(self, zone_type, zone_guid):
        """
        24、删除禁航区或封锁区域
        :param zone_type: int, 1:封锁区，0：禁航区
        :param zone_guid: str, 区域的guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_zone_remove(self, zone_type, zone_guid)

    def zone_add_no_navigate(self, name, reference_points, affects=None):
        """
        25、添加禁航区
        :param name: str, 禁航区名
        :param reference_points:list, 参考点列表, 例:[(40, 139.0), (41, 139.0), (41, 140.0)], 先纬度，再经度；
                                        或指定参考点名：[(40, 139.0,'RP1'), (41, 139.0,'RP2'), (41, 140.0,'RP3')],先纬度，再经度
        :param affects: list, 应用的装备类型，例:[1]:仅飞机适用; [1,2]:仅飞机、水面舰艇适用; [1,2,3,4]:飞机、水面舰艇,潜艇,地面单元适用
                            1:飞机；2:水面舰艇; 3:潜艇；4:地面单元
        :return:str, zone guid
        """
        if affects is None:
            affects = [1, 2, 3, 4]
        return self.zone_add(reference_points, 0, name, affects)

    def zone_add_exclusion(self, name, reference_points, affects=None):
        """
        26、添加封锁区
        :param name: str, 封锁区名
        :param reference_points:list, 参考点列表， 例:[(40, 139.0), (41, 139.0), (41, 140.0)], 先纬度，再经度
                                    或指定参考点名：[(40, 139.0,'RP2'), (41, 139.0,'RP3'), (41, 140.0,'RP4')],先纬度，再经度,再参考点名
        :param affects: list, 应用的装备类型，例:[1]:仅飞机适用; [1,2]:仅飞机、水面舰艇适用; [1,2,3,4]:飞机、水面舰艇,潜艇,地面单元适用
                            1:飞机；2:水面舰艇; 3:潜艇；4:地面单元
        :return:str, zone guid
        """
        if affects is None:
            affects = [1, 2, 3, 4]
        return self.zone_add(reference_points, 1, name, affects)

    def zone_add(self, reference_points, zone_type, zone_name, affects=None):
        """
        27、添加禁航区或封锁区
        :param reference_points:  list, 区域点列表
        :param zone_type: int, 1: 封锁区   0:禁航区
        :param zone_name:  区域名
        :param affects: list, 应用的装备类型，例:[1]:仅飞机适用; [1,2]:仅飞机、水面舰艇适用; [1,2,3,4]:飞机、水面舰艇,潜艇,地面单元适用
                            1:飞机；2:水面舰艇; 3:潜艇；4:地面单元
        :return: str, zone guid
        """
        zone_guid = self._game_server.api_zone_add(self, reference_points, zone_type, zone_name, affects)
        return cf.zone_guid_parser(zone_guid)

    def zone_set(self, zone_type, zone_name, **kwargs):
        """
        28、修改禁航区和封锁区
        :param zone_type: int, 1: 封锁区   0:禁航区
        :param zone_name: 禁航区和封锁区的名
        :param kwargs:  关键字参数  Area：list, 参考点列表， 例:[(40, 139.0), (41, 139.0), (41, 140.0)], 先纬度，再经度
                                    或指定参考点名：[(40, 139.0,'RP2'), (41, 139.0,'RP3'), (41, 140.0,'RP4')],先纬度，再经度,再参考点名
                                    或使用已建立参考点，则用参考点名列表，例: ['RP1', 'RP2', 'RP3']
                        Rename: str  新名字
                        Isactive： bool 是否启用
                        Affects： list, 应用的装备类型，例:[1]:仅飞机适用; [1,2]:仅飞机、水面舰艇适用;
                                    [1,2,3,4]:飞机、水面舰艇,潜艇,地面单元适用
                                    1:飞机；2:水面舰艇; 3:潜艇；4:地面单元
                        Locked：bool 是否区域已锁定(只有禁航区才需要设置)
                        MarkAs： int 2=非友方，3=敌方（封锁区才有的设置）
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_zone_set(self, zone_type, zone_name, **kwargs)

    def group_add(self, list_unit_guid, group_name=""):
        """
        29、将多个单元作为一个编队
        :param list_unit_guid: list, 例：['2abc947e-8352-4639-9184-641706730018',
                                            '640a7c08-a17a-4fba-b055-07b568f22df5']
        :param group_name: str, 编队名
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_group_add(self, list_unit_guid, group_name)

    def group_detach(self, list_unit_guid):
        """
        30、分离编组单元
        :param list_unit_guid: list, 例：['2abc947e-8352-4639-9184-641706730018','640a7c08-a17a-4fba-b055-07b568f22df5']
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_group_detach(self, list_unit_guid)

    def group_remove_unit(self, unit_guid):
        """
        31、将单元移除出编队
        :param unit_guid: 作战单元guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_group_remove_unit(self, unit_guid)

    def group_add_unit(self, group_guid, unit_guid):
        """
        32、编队添加一个单元
        :param group_guid: 编队guid
        :param unit_guid: 作战单元guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_group_add_unit(self, group_guid, unit_guid)

    def air_single_out(self, air_guid_list):
        """
        33、飞机单机出动
        :param air_guid_list: list, 飞机的guid列表，  例子：['58ba-4013-92f5-2ewds','58ba-4013-92f5-2efa0']
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_air_single_out(self, air_guid_list)

    def air_group_out(self, air_guid_list):
        """
        34、飞机编组出动
        :param air_guid_list:  list, 飞机的guid列表，  例子：['4013-92f5-2effc','4013-92f5-d2fa0']
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_air_group_out(self, air_guid_list)

    def aircraft_action_ready(self, mode, guid_list, loadout_id, qt_enabled):
        """
        35、飞机准备/备战，飞机挂载武器;
        :param mode: 1: 准备就绪; 2: 准备就绪（不包括可选武器）
        :param guid_list: list, 飞机guid列表
        :param loadout_id: int, 挂载方案ID
        :param qt_enabled: bool, 是否快速出动, 如快速出动需提前确认此挂载是否快速出动
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_aircraft_action_ready(self, mode, guid_list, loadout_id, qt_enabled)

    def ship_action_alone(self, guid_list):
        """
        36、船舶/潜艇单独出航
        :param guid_list: list, 舰船guid列表
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_ship_action_alone(self, guid_list)

    def ship_action_group(self, guid_list):
        """
        37、船舶/潜艇编队出航
        :param guid_list: list, 舰船guid列表
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_ship_action_group(self, guid_list)

    def ship_action_stop(self, guid_list):
        """
        38、船舶/潜艇中止出航
        :param guid_list: list, 舰船guid列表
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_ship_action_stop(self, guid_list)

    def hold_position_all_unit(self, is_hold):
        """
        39、保持所有单元阵位，所有单元停止机动，留在原地
        :param is_hold: bool
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_hold_position_all_unit(self, is_hold)

    def unit_select_new_base(self, unit_guid, base_guid):
        """
        40、单元选择新基地/新港口
        :param unit_guid: 单元的guid
        :param base_guid: 新基地的guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_unit_select_new_base(self, unit_guid, base_guid)

    def unit_return_to_base(self, unit_guid):
        """
        41、实体返航
        :param unit_guid: 单元的guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_unit_return_to_base(self, unit_guid)

    def attack_contact_by_list(self, attack_list):
        """
        42、批量自动攻击某目标
        :param attack_list, 攻击信息列表，每条信息包含一个元组, [(attack_id, target_id, weapon_id, weapon_count)]
                                                            攻击单元guid, 目标guid, 武器型号id, 武器数量
                例：[('guid1-2fljs', 'target1-fjslfjl2', 0, 0),     weapon_id=0代表自动打击，系统自动选择武器打击目标
                    ('guid1-3fljs', 'target3f-fjslfjd', 2880, 2)]  weapon_id=2880，手动攻击，指定打击的武器和数量
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_attack_contact_by_list(self, attack_list)

    def check_weapon_fire_condition(self, units_contacts):
        """
        43、开火条件检查, 返回检查开火条件结果； 耗时, 谨慎调用, 请勿每天文时间10秒调用超过3次！！！
        :param units_contacts:list, or tuple, example:  [(unit1, target1),(unit2, target2)] or (unit1, target1)
        :return: dict, 例子：
            {"1796":{"AmmoTotal":5,"AmmoDist":0,"AutoFire":"不能自动开火，目标超出武器射程",
            "Status":"自由开火","Authorize":"每次齐射发射所有武器. 最大射程武器发射. 飞机-第四代战斗机/攻击[敏捷性/通用：4.0～4.9]（F-14、F-15、F-16、MiG-29、Su-27）",
            "ManualFire":{"目标超出武器射程":5}},
            "1896":{"AmmoTotal":2,"AmmoDist":0,"AutoFire":"不能自动开火，目标超出武器射程","Status":"自由开火",
            "Authorize":"1x rnd 每次齐射. 最大射程武器发射. 飞机-第四代战斗机/攻击[敏捷性/通用：4.0～4.9]（F-14、F-15、F-16、MiG-29、Su-27）",
            "ManualFire":{"目标超出武器射程":2}},
            "2056":{"AmmoTotal":6,"AmmoDist":0,"AutoFire":"OK","Status":"自由开火",
            "Authorize":"1x rnd 每次齐射. 15海里 最大射程. 飞机-第四代战斗机/攻击[敏捷性/通用：4.0～4.9]（F-14、F-15、F-16、MiG-29、Su-27）",
            "ManualFire":{"OK":6}}}
        """
        return self._game_server.api_check_weapon_fire_condition(self, units_contacts)

    def contact_rename(self, contact_id, new_name):
        """
        44、情报标识重命名
        :param contact_id: str, contact id
        :param new_name: str, new name
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_contact_rename(self, contact_id, new_name)

    def contact_mark_position(self, contact_id):
        """
        45、情报标识标记位置
        :param contact_id:str, contact id
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_contact_mark_position(self, contact_id)

    def contact_mark_posture(self, contact_id, posture):
        """
        46、标识情报阵营
        :param contact_id: str, 情报id
        :param posture: 枚举ContactStance, global_util.py中定义
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_contact_mark_posture(self, contact_id, posture)

    def contact_drop_target(self, contact_id):
        """
        47、断开若干情报标识
        :param contact_id: str, 情报id; 或list, 情报id列表
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_contact_drop_target(self, contact_id)

    def unit_newname(self, guid, newname):
        """
        48、修改单元名称
        :param guid:str, 单元guid
        :param newname:str, 单元名
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_unit_newname(self, guid, newname)

    def set_aircraft_loadout_plan_time(self, unit_id, loadoutID):
        """
        49、战前规划时间，可设置飞机挂载，不限制机场或航母弹药，准备时间为0，即可马上准备好
        :param unit_id: str, 单元id或单元名称
        :param loadoutID: int  武器挂载方案ID
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_loadout_plan_time(self.get_command_check(unit_id), loadoutID)

    def unit_new_position(self, unit_guid, lon_lat=None, alt=None, depth=None, heading=None):
        """
        50、战前规划时间，对战开始之前，设置本单元经纬度位置或高度或深度或航向
        飞机、舰船、潜艇、地面移动装备可以移动到距初始位置最大距离（20千米）内任意位置（符合地形-例：船在海中，飞机不可在山内）
        正式推演对战之后，本接口会调用失效并给出提示！
        :param unit_guid: str, 本推演方单元guid
        :param lon_lat: tuple, 经度、纬度的元组，(float,float) 需要移动单元到的目的地经度纬度
                                东经0到180，西经-180到0；北纬0到90，南纬-90到0
        :param alt: float, 单元的目标高度（仅用于飞机），米
        :param depth: float, 单元的目标深度（仅用于潜艇），米，正数即可
        :param heading: float, 单元的目标航向，0到360度，正北为0，顺时针增大到360
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.unit_new_position(self.get_command_check(unit_guid), long_lat=lon_lat,
                                                   altitude=alt, new_depth=depth, new_heading=heading)

    def agent_message_text(self, text):
        """
        51、客户端应用智能体中，智能体消息输出接口——纯文本
        :param text: str, 纯文本消息
        :return: str, 返回信息
        """
        message = {
            'text': text
        }
        return self._game_server.agent_message_output(0, message, self.simulate_timestamp)

    def agent_message_intelligence(self, level, contact_id, text):
        """
        52、客户端应用智能体中，智能体消息输出接口——重要情报（202607版本未实现）
        :param level: int
            level重要情报层级：
                1：一级情报，核心情报信息，显示为红色
                2：二级情报，重要情报信息，显示为橙色
                3：三级情报，一般情报信息，显示为白色
        :param contact_id: str, 情报ID
        :param text: str, 纯文本消息
        :return: str, 返回信息
        """
        message = {
            'text': text,
            'level': level,
            'contact_id': contact_id
        }
        return self._game_server.agent_message_output(data_type=1, message=message, timestamp=self.simulate_timestamp)

    def agent_message_unit_range(self, unit_id, dbrange, color_type, line_type, text):
        """
        53、客户端应用智能体中，智能体消息输出接口——圆形区域显示（跟随单元）（202607版本未实现）
        :param unit_id: str, 圆形区域跟随的单元id，可以跟随己方单元或者是敌方单元
        :param dbrange: float, 显示区域半径，千米
        :param color_type: int: 1：白色 2：橙色 3：红色 4：蓝色 5：紫色 6：黄色 7：绿色
        :param line_type: int, 0：实线 1：虚线
        :param text: str, 纯文本消息
        :return: str, 返回信息
        """
        message = {
            'text': text,
            'unit_id': unit_id,
            'dbrange': dbrange,
            'color_type': color_type,
            'line_type': line_type
        }
        return self._game_server.agent_message_output(data_type=2, message=message, timestamp=self.simulate_timestamp)

    def agent_message_arrow(self, arrow_name, color_type, line_type, points_list, text):
        """
        54、客户端应用智能体中，智能体消息输出接口——箭头（202607版本未实现）
        :param arrow_name: str, 箭头名称
        :param color_type: int, 1：白色 2：橙色 3：红色 4：蓝色 5：紫色 6：黄色 7：绿色
        :param line_type: int: 0：实线 1：虚线
        :param points_list: list, 形成箭头的点，[(lon1,lat1),(lon2,lat2)...] ,列表最后一行经纬度为箭头指向
        :param text: str, 纯文本消息
        :return: str, 返回信息
        """
        message = {
            'text': text,
            'arrow_name': arrow_name,
            'color_type': color_type,
            'line_type': line_type,
            'points_list': points_list
        }
        return self._game_server.agent_message_output(data_type=3, message=message, timestamp=self.simulate_timestamp)

    def agent_message_area(self, area_name, points_list, text):
        """
        55、客户端应用智能体中，智能体消息输出接口——多边形区域（202607版本未实现）
        :param area_name: str, 箭头名称
        :param points_list: list, 区域点[(lon1,lat1),(lon2,lat2)...]
        :param text: str, 纯文本消息
        :return: str, 返回信息
        """
        message = {
            'text': text,
            'area_name': area_name,
            'points_list': points_list
        }
        return self._game_server.agent_message_output(data_type=4, message=message, timestamp=self.simulate_timestamp)

