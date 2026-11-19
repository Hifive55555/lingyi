# -*- coding:utf-8 -*-
# Author: Liaojiang
# Description: 通用任务

import json
import traceback

from .global_util import *
from .operatorbase import DoctrineOperator
from .commonfunction import guid_list_parser


class Mission(DoctrineOperator):
    """
    基础任务类  
    1、是否启用任务  
    2、设置、删除任务开始时间  
    3、设置任务：删除任务结束时间
    4、设置任务将实体分配到任务中来
    5、返回任务已分配的单元
    6、任务取消某单元的任务分配
    7、任务设置出航航线或者阵位航线，或者设置返航航线
    8、修改任务名

    示例：  
    mine_mission = self.get_mission_by_name('mine_mission_1')   # 通过排雷任务的名字，获取排雷任务对象  
    mission_info = mine_mission.get_information()  # 获取排雷任务的信息  
    mine_mission.assign_unit("fsf0fjsl-sfjlg-d")  # 分配单元到任务  
    """
    def __init__(self, guid, name, side_name, element_type):
        if element_type == ElementType.StrikeEscortMission:
            DoctrineOperator.__init__(self, guid, name, side_name, SelectorCategory.EscortMission, element_type)
        else:
            DoctrineOperator.__init__(self, guid, name, side_name, SelectorCategory.Mission, element_type)
        self.Category = 0  # 任务类别：0-任务 1-任务池 2-任务包（EMissionCategory）
        self.Status = 0  # 任务状态：1-未启用 0-启用 （EMissionStatus）
        self.START = ""  # 任务启用时间UTC(毫秒)
        self.END = ""  # 任务失效时间UTC(毫秒)
        self.TakeOffTime = ""  # 起飞时间
        self.TimeOnTarget = ""  # 目标时间
        self.SISIH = False  # ScrubIfSideIsHuman 如果推演方是人，则取消
        self.UseFlightplan = False  # 使用飞行计划
        self.UseFlightplansOnly = False  # UsePreGeneratedFlightplansOnly仅使用预生成的飞行计划
        self.IncludeInATO = False  # 包含在ATO中
        self.TankerUsage = 0  # 加油机使用, 0: 自动选择加油机   1:使用任务的加油机
        self.TankerMissionList = []  # 加油机任务ID列表
        self.FlightSize = 0  # 航班大小
        self.GroupSize = 0  # 编队大小
        self.GroupName = ""  # 编组名称
        self.DeactivationUnassignUnits = False  # 停用_取消分配单元
        self.CheckBoxOrderRTB = False  # 停用_命令返回基地
        self.CheckBoxDeleteMission = False  # 停用_删除任务
        self.LaunchMissionWithoutTankersInPlace = False  # 无油轮就位的启动任务
        self.TankerMinNumberTotal = 0  # 油轮最小数量_总共
        self.TankerMinNumberAirborne = 0  # 油轮最小数量_在空
        self.TankerMinNumberStation = 0  # 油轮最小数量_阵位
        self.MaxReceiversInQueuePerTankerAirborne = 0  # 每个油轮队列中的最大接收器数_在空
        self.FuelQtyToStartLookingForTankerAirborne = 0  # 开始寻找油轮的燃油量_在空
        self.TankerMaxDistanceAirborne = 0  # 油轮最大距离_在空
        self.TankerFollowsReceivers = False  # 油轮跟随接收者
        self.UseFlightSizeHardLimit = False  # 使用航班大小限制
        self.UseGroupSizeHardLimit = False  # 使用组大小限制
        # THFlight,THVectorEmptySlot等结构定义请查看entitys/struct.proto文件
        self.Flight = {}  # 航班---结构：dict<string, THFlight>，key:航班ID
        self.EmptySlotsList = []  # 空飞机插槽--结构：THVectorEmptySlot列表
        self.ListNavigation1 = []  # 出航航线--结构：航路点THWaypoint列表
        self.ListNavigation2 = []  # 阵位航线--结构：航路点THWaypoint列表
        self.ListNavigation3 = []  # 返航航线--结构：航路点THWaypoint列表
        self.CreateTime = 0

    def _set(self, item):
        """
        设置任务各项目（为其他接口所用内部函数，智能体无需直接调用此接口）
        :param item: str, exp: isactive='true'
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_mission(self, item)

    def mission_active(self, is_active):
        """
        1、设置是否启用任务
        :param is_active: bool, 是否启用
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "isactive=%s" % (str(is_active).lower())
        return self._set(str_set)

    def set_start(self, start_time):
        """
        2、设置、删除任务开始时间
        :param start_time: str, 开始时间, 例: '05/24/2014 16:05:00'
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "starttime='%s'" % start_time
        return self._set(str_set)

    def set_end(self, end_time):
        """
        3、设置任务：删除任务结束时间
        :param end_time:str, 结束时间, 例: '05/24/2014 16:05:00'
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "endtime='%s'" % end_time
        return self._set(str_set)

    def assign_unit(self, unit_ID, is_escort=False):
        """
        4、设置任务：将实体分配到任务中来
        :param unit_ID: str, 实体单元的guid
        :param is_escort: bool,  是否护航任务
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_assign_unit(self, unit_ID, is_escort)

    def get_units_assigned(self):
        """
        5、返回任务已分配的单元
        :return: list, 单元guid list
        """
        reply = self._game_server.api_get_units_assigned(self)
        if reply.code == 0:
            try:
                mission_json = json.loads(reply.result.decode('utf-8'))
                if "mission" in mission_json and "unitlist" in mission_json["mission"]:
                    return mission_json["mission"]["unitlist"]
            except Exception as e:
                traceback.print_exc()
        return []

    def unassign_unit(self, unit_id):
        """
        6、任务取消某单元的任务分配
        :param unit_id: str, 实体单元的guid
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_unassign_unit(self, unit_id)

    def set_mission_course(self, take_course, station_course, return_course):
        """
        7、任务设置出航航线或者阵位航线，或者设置返航航线
        :param take_course: list, 出航航线   exp: [["rp1", 23.2, 112.2], ["rp2", 24.2, 113.45]]
        :param station_course: list, 阵位航线     exp: [["rp1", 23.2, 112.2], ["rp2", 24.2, 113.45]]
        :param return_course: list, 返航航线      exp: [["rp1", 23.2, 112.2], ["rp2", 24.2, 113.45]]
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        all_course_str = ""
        if take_course:
            course_str = ""
            for course in take_course:
                course_point = "{name='%s', latitude=%.5lf, longitude=%.5lf}," % (course[0], course[1], course[2])
                course_str += course_point
            course_str = course_str[:-1]
            all_course_str = "courseTake={%s}" % course_str

        if station_course:
            course_str = ""
            for course in station_course:
                course_point = "{name='%s', latitude=%.5lf, longitude=%.5lf}," % (course[0], course[1], course[2])
                course_str += course_point
            course_str = course_str[:-1]
            if all_course_str:
                all_course_str += ",courseCircle={%s}" % course_str
            else:
                all_course_str = "courseCircle={%s}" % course_str

        if return_course:
            course_str = ""
            for course in return_course:
                course_point = "{name='%s', latitude=%.5lf, longitude=%.5lf}," % (course[0], course[1], course[2])
                course_str += course_point
            course_str = course_str[:-1]
            if all_course_str:
                all_course_str += ",courseCourse={%s}" % course_str
            else:
                all_course_str = "courseCourse={%s}" % course_str
        all_course_str = "{%s}" % all_course_str
        return self._set(all_course_str)

    def set_mission_newname(self, new_name):
        """
        8、修改任务名
        :param new_name: str, 新任务名
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        str_set = "newname='%s'" % new_name
        return self._set(str_set)



