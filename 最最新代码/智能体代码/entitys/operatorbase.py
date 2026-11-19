# -*- coding:utf-8 -*-
# Description: 条令（推演方、任务、编队或单元条令设置）

from .global_util import *
from .element import Element


class DoctrineOperator(Element):
    """
    条令类  
    1、条令中，电磁管控设置，设置雷达开关机  
    2、条令中，电磁管控设置，设置电子干扰传感器开关机  
    3、条令中，电磁管控设置，设置声呐开关机  
    4、设置条令中电磁管控与上级一致  
    5、条令设置，是否使用核武器  
    6、武器控制状态，对空  
    7、武器控制状态，对水面  
    8、武器控制状态，对潜  
    9、武器控制状态，对地  
    10、攻击时忽略计划航线设置  
    11、接战模糊位置目标  
    12、接战临机出现目标  
    13、受到攻击忽略电磁管控  
    14、鱼雷射程  
    15、自动规避  
    16、加油/途中补给  
    17、加油/途中补给加油机选择设置  
    18、给盟军加油/途中补给  
    19、空战节奏  
    20、快速周转  
    21、燃油状态，预先规划  
    22、燃油状态，返航  
    23、武器状态，预先规划  
    24、武器状态-返航  
    25、空对地扫射  
    26、丢弃武器  
    27、超视距交战  
    28、反水面战模式下使用防空导弹   
    29、反水面作战行动 与目标保持距离  
    30、反水面作战行动 导航  
    31、反潜作战行动，规避搜索  
    32、反潜作战行动，探测到威胁进行下潜  
    33、反潜作战行动，充电电池 运输/站点  
    34、反潜作战行动，充电电池 进攻/防守  
    35、反潜作战行动，使用AIP技术  
    36、反潜作战行动，吊放声呐  
    37、反潜作战行动，导航  
    38、陆战导航  
    39、设置条令的武器使用规则  
    40、武器使用规则--齐射武器数  
    41、武器使用规则--齐射发射架数  
    42、武器使用规则--自动开火距离  
    43、武器使用规则--自动防御距离  
    44、满足如下条件时撤退--毁伤程度大于  
    45、满足如下条件时撤退--燃油少于  
    46、满足如下条件时撤退--主要攻击攻击武器至少处于  
    47、满足如下条件时撤退--主要防御武器至少  
    48、满足如下条件时重新部署--毁伤程度小于  
    49、满足如下条件时重新部署--燃油至少处于  
    50、满足如下条件时重新部署--主要攻击武器处于  
    51、满足如下条件时重新部署--主要防御武器处于  
    52、获取武器使用规则  

    设置条令示例：  
    self.doctrine_weapon_control_status_air(WeaponControlStatus.Free)  # 设置推演方条令，自由开火  
    air1_id = "sflsf0-gjlsf-sf"  # 飞机guid  
    air1 = self.get_unit(air1_id)  # 获取飞机对象  
    if air1 is not None:  
        air1.doctrine_weapon_control_status_air(WeaponControlStatus.Hold)  # 设置此飞机条令，限制开火  
        air1.wra_qty_salvo('51', WRA_WeaponTargetType.Aircraft_4th_Generation, '2')  # 设置此飞机武器51对4代机齐射武器数为2  
    patrol_mission = self.get_mission_by_name('patrol_mission1')   # 通过巡航任务的名字，获取巡航任务对象  
    patrol_mission.doctrine_fuel_state_rtb(FuelStateRTB.YesLeaveGroup)  # 设置任务条令，燃油状态：单元离开编队返航  
    attack_mission = self.create_strike_mission('打A机场', MissionStrikeType.LAND)  # 创建对陆打击任务  
    attack_mission.doctrine_weapon_control_status_land(WeaponControlStatus.Free)  # 对陆打击任务设置条令  
    attack_mission.escort.doctrine_weapon_control_status_air(WeaponControlStatus.Free)  # 对陆打击任务的护航任务设置条令  
    """
    def __init__(self, guid, name, side_name, category, element_type, unit_id=''):
        Element.__init__(self, guid, name, side_name, element_type)
        self.Doctrine = {}
        self.category = category
        self.category_str = selector2str[self.category]

        if self.category == SelectorCategory.Side:
            self.selector = '{side="%s"}' % self.Side
        elif self.category == SelectorCategory.Mission:
            self.selector = '{side="%s",mission="%s"}' % (self.Side, self.Name)
        elif self.category == SelectorCategory.WayPoint:
            self.selector = '{guid="%s",pointid="%s"}' % (unit_id, self.ID)
        elif self.category == SelectorCategory.EscortMission:
            self.selector = '{side="%s",mission="%s",escort=true}' % (self.Side, self.Name)
        else:
            self.selector = '{guid="%s"}' % self.ID

    def _set_doctrine(self, doctrine):
        """
        设置条令各项目
        :param doctrine: str, 设置参数，例: '{ignore_plotted_course=true}'
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_doctrine(self, doctrine)

    def doctrine_switch_radar(self, switch_on):
        """
        1、条令中，电磁管控设置，设置雷达开关机
        :param switch_on: bool, 传感器打开或者静默，True:打开
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_doctrine_switch_radar(self, switch_on)

    def doctrine_switch_oecm(self, switch_on):
        """
        2、条令中，电磁管控设置，设置电子干扰传感器开关机
        :param switch_on: bool, 传感器打开或者静默，True:打开
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_doctrine_switch_oecm(self, switch_on)

    def doctrine_switch_sonar(self, switch_on):
        """
        3、条令中，电磁管控设置，设置声呐开关机
        :param switch_on: bool, 传感器打开或者静默，True:打开
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_doctrine_switch_sonar(self, switch_on)

    def doctrine_SetEMCON_Inherit(self):
        """
        4、设置条令中电磁管控与上级一致，推演方条令无法设置为Inherit
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_doctrine_SetEMCON_Inherit(self)

    def use_nuclear_weapons(self, use_nuclear):
        """
        5、条令设置，是否使用核武器； 推演方条令无法设置为Inherit
        本次比赛（2025年兵棋比赛）不允许使用核武器
        :param use_nuclear: EUseNuclear, 是否使用核武器
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if use_nuclear.value == 999:
            if self.category == SelectorCategory.Side:
                return
            doctrine = '{use_nuclear_weapons=\"inherit\"}'
        else:
            if use_nuclear.value == 1:
                return
            doctrine = f"{{use_nuclear_weapons='{use_nuclear.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_weapon_control_status_air(self, weapon_control_status_airEnum):
        """
        6、武器控制状态，对空；推演方条令无法设置为Inherit
        :param weapon_control_status_airEnum: WeaponControlStatus, 状态枚举类型
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if weapon_control_status_airEnum.value == 999:
            if self.category == SelectorCategory.Side:
                return
            doctrine = '{weapon_control_status_air=\"inherit\"}'
        else:
            doctrine = f"{{weapon_control_status_air='{weapon_control_status_airEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_weapon_control_status_surface(self, control_status):
        """
        7、武器控制状态，对水面；推演方条令无法设置为Inherit
        :param control_status: WeaponControlStatus, 状态枚举类型
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if control_status.value == 999:
            if self.category == SelectorCategory.Side:
                return
            doctrine = '{weapon_control_status_surface=\"inherit\"}'
        else:
            doctrine = f"{{weapon_control_status_surface='{control_status.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_weapon_control_status_subsurface(self, control_status):
        """
        8、武器控制状态，对潜；推演方条令无法设置为Inherit
        :param control_status: WeaponControlStatus, 状态枚举类型
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if control_status.value == 999:
            if self.category == SelectorCategory.Side:
                return
            doctrine = '{weapon_control_status_subsurface=\"inherit\"}'
        else:
            doctrine = f"{{weapon_control_status_subsurface='{control_status.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_weapon_control_status_land(self, weapon_control_status_landEnum):
        """
        9、武器控制状态，对地；推演方条令无法设置为Inherit
        :param weapon_control_status_landEnum:  WeaponControlStatus, 状态枚举类型
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if weapon_control_status_landEnum.value == 999:
            if self.category == SelectorCategory.Side:
                return
            doctrine = '{weapon_control_status_land=\"inherit\"}'
        else:
            doctrine = f"{{weapon_control_status_land='{weapon_control_status_landEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_ignore_plotted_course(self, ignore_plotted_courseEnum):
        """
        10、攻击时忽略计划航线设置；推演方条令无法设置为Inherit
        :param ignore_plotted_courseEnum:IgnorePlottedCourseWhenAttacking，选择枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if ignore_plotted_courseEnum == IgnorePlottedCourseWhenAttacking.No:
            doctrine = '{ignore_plotted_course="0"}'
        elif ignore_plotted_courseEnum == IgnorePlottedCourseWhenAttacking.Yes:
            doctrine = '{ignore_plotted_course="1"}'
        elif ignore_plotted_courseEnum == IgnorePlottedCourseWhenAttacking.Inherit:
            if self.category == SelectorCategory.Side:
                return
            doctrine = '{ignore_plotted_course=\"inherit\"}'
        else:
            raise ValueError("parameter error")
        return self._set_doctrine(doctrine)

    def doctrine_engaging_ambiguous_targets(self, towards_ambigous_target):
        """
        11、接战模糊位置目标；推演方条令无法设置为Inherit
        :param towards_ambigous_target: BehaviorTowardsAmbigousTarget
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if towards_ambigous_target.value == 999:
            if self.category == SelectorCategory.Side:
                return
            doctrine = '{engaging_ambiguous_targets=\"inherit\"}'
        else:
            doctrine = f"{{engaging_ambiguous_targets='{towards_ambigous_target.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_engage_opportunity_targets(self, engage_opportunity_targetsEnum):
        """
        12、接战临机出现目标；推演方条令无法设置为Inherit
        :param engage_opportunity_targetsEnum: EngageWithContactTarget, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if engage_opportunity_targetsEnum == EngageWithContactTarget.No_Only:
            doctrine = '{engage_opportunity_targets="0"}'
        elif engage_opportunity_targetsEnum == EngageWithContactTarget.Yes_AnyTarget:
            doctrine = '{engage_opportunity_targets="1"}'
        elif engage_opportunity_targetsEnum.value == 999:
            doctrine = '{engage_opportunity_targets=\"inherit\"}'
        else:
            raise ValueError("parameter error")
        return self._set_doctrine(doctrine)

    def doctrine_ignore_emcon_under_attack(self, ignore_emcon_while_under_attackEnum):
        """
        13、受到攻击忽略电磁管控；推演方条令无法设置为Inherit
        :param ignore_emcon_while_under_attackEnum: IgnoreEMCONUnderAttack, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if ignore_emcon_while_under_attackEnum == IgnoreEMCONUnderAttack.No:
            doctrine = '{ignore_emcon_while_under_attack="0"}'
        elif ignore_emcon_while_under_attackEnum == IgnoreEMCONUnderAttack.Ignore_EMCON_While_Under_Attack:
            doctrine = '{ignore_emcon_while_under_attack="1"}'
        elif ignore_emcon_while_under_attackEnum.value == 999:
            doctrine = '{ignore_emcon_while_under_attack=\"inherit\"}'
        else:
            raise ValueError("parameter error")
        return self._set_doctrine(doctrine)

    def torpedoes_kinematic_range(self, kinematic_range):
        """
        14、鱼雷射程；推演方条令无法设置为Inherit
        :param kinematic_range:  UseTorpedoesKinematicRange, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if kinematic_range.value == 999:
            doctrine = '{kinematic_range_for_torpedoes=\"inherit\"}'
        else:
            doctrine = f"{{kinematic_range_for_torpedoes='{kinematic_range.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_automatic_evasion(self, automatic_evasionEnum):
        """
        15、自动规避；推演方条令无法设置为Inherit
        :param automatic_evasionEnum: AutomaticEvasion, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if automatic_evasionEnum == AutomaticEvasion.No:
            doctrine = '{automatic_evasion="0"}'
        elif automatic_evasionEnum == AutomaticEvasion.Yes:
            doctrine = '{automatic_evasion="1"}'
        elif automatic_evasionEnum.value == 999:
            doctrine = '{automatic_evasion=\"inherit\"}'
        else:
            raise ValueError("parameter error")
        return self._set_doctrine(doctrine)

    def doctrine_refuel(self, refuel):
        """
        16、加油/途中补给；推演方条令无法设置为Inherit
        :param refuel: ERefuel, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if refuel.value == 999:
            doctrine = '{use_refuel_unrep=\"inherit\"}'
        else:
            doctrine = f"{{use_refuel_unrep='{refuel.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_refuel_select(self, refuel_select):
        """
        17、加油/途中补给加油机选择设置；推演方条令无法设置为Inherit
        :param refuel_select: ERefuelSelect, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if refuel_select.value == 999:
            doctrine = '{refuel_unrep_selection=\"inherit\"}'
        else:
            doctrine = f"{{refuel_unrep_selection='{refuel_select.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_refuel_allied(self, refuel):
        """
        18、给盟军加油/途中补给；推演方条令无法设置为Inherit
        :param refuel: ERefuelAllied, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if refuel.value == 999:
            doctrine = '{refuel_unrep_allied=\"inherit\"}'
        else:
            doctrine = f"{{refuel_unrep_allied='{refuel.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_air_operations_tempo(self, air_operations_tempoEnum):
        """
        19、空战节奏；推演方条令无法设置为Inherit
        :param air_operations_tempoEnum: AirOpsTempo, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if air_operations_tempoEnum.value == 999:
            doctrine = '{air_operations_tempo=\"inherit\"}'
        else:
            doctrine = f"{{air_operations_tempo='{air_operations_tempoEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_quick_turnaround(self, quick_turnaroundEnum):
        """
        20、快速周转；推演方条令无法设置为Inherit
        :param quick_turnaroundEnum: QuickTurnAround, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if quick_turnaroundEnum.value == 999:
            doctrine = '{quick_turnaround_for_aircraft=\"inherit\"}'
        else:
            doctrine = f"{{quick_turnaround_for_aircraft='{quick_turnaroundEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_fuel_state_planned(self, fuel_state_plannedEnum):
        """
        21、燃油状态，预先规划；推演方条令无法设置为Inherit
        :param fuel_state_plannedEnum: FuelState, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if fuel_state_plannedEnum.value == 999:
            doctrine = '{fuel_state_planned=\"inherit\"}'
        else:
            doctrine = f"{{fuel_state_planned='{fuel_state_plannedEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_fuel_state_rtb(self, fuel_state_rtbEnum):
        """
        22、燃油状态，返航；推演方条令无法设置为Inherit
        :param fuel_state_rtbEnum: FuelStateRTB, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if fuel_state_rtbEnum.value == 999:
            doctrine = '{fuel_state_rtb=\"inherit\"}'
        else:
            doctrine = f"{{fuel_state_rtb='{fuel_state_rtbEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_weapon_state_planned(self, weapon_state_plannedEnum):
        """
        23、武器状态，预先规划；推演方条令无法设置为Inherit
        :param weapon_state_plannedEnum:WeaponStatePlanned, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if weapon_state_plannedEnum.value == 999:
            doctrine = '{weapon_state_planned=\"inherit\"}'
        else:
            doctrine = f"{{weapon_state_planned='{weapon_state_plannedEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_weapon_state_rtb(self, weapon_state_rtbEnum):
        """
        24、武器状态-返航；推演方条令无法设置为Inherit
        :param weapon_state_rtbEnum: WeaponStateRTB, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if weapon_state_rtbEnum.value == 999:
            doctrine = '{weapon_state_rtb=\"inherit\"}'
        else:
            doctrine = f"{{weapon_state_rtb='{weapon_state_rtbEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_gun_strafing(self, gun_strafingEnum):
        """
        25、空对地扫射；推演方条令无法设置为Inherit
        :param gun_strafingEnum: GunStrafeGroundTargets, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if gun_strafingEnum.value == 999:
            doctrine = '{gun_strafing=\"inherit\"}'
        else:
            doctrine = f"{{gun_strafing='{gun_strafingEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_jettison_ordnance(self, jettison_ordnanceEnum):
        """
        26、丢弃武器；推演方条令无法设置为Inherit
        :param jettison_ordnanceEnum: JettisonOrdnance, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if jettison_ordnanceEnum.value == 999:
            doctrine = '{jettison_ordnance=\"inherit\"}'
        else:
            doctrine = f"{{jettison_ordnance='{jettison_ordnanceEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_bvr_logic(self, bvr_logicEnum):
        """
        27、超视距交战；推演方条令无法设置为Inherit
        :param bvr_logicEnum: BvrLogic, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if bvr_logicEnum.value == 999:
            doctrine = '{bvr_logic=\"inherit\"}'
        else:
            doctrine = f"{{bvr_logic='{bvr_logicEnum.value}'}}"
        return self._set_doctrine(doctrine)

    def use_sams_in_anti_surface_mode(self, use_sams):
        """
        28、反水面战模式下使用防空导弹；推演方条令无法设置为Inherit
        :param use_sams: UseSAMsInASuWMode, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if use_sams.value == 999:
            doctrine = '{use_sams_in_anti_surface_mode=\"inherit\"}'
        else:
            doctrine = f"{{use_sams_in_anti_surface_mode='{use_sams.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_maintain_standoff(self, maintain_standoff):
        """
        29、反水面作战行动 与目标保持距离；推演方条令无法设置为Inherit
        :param maintain_standoff: MaintainStandoff, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if maintain_standoff.value == 999:
            doctrine = '{maintain_standoff=\"inherit\"}'
        else:
            doctrine = f"{{maintain_standoff='{maintain_standoff.value}'}}"
        return self._set_doctrine(doctrine)

    def doctrine_navigation_surface_mode(self, navigation_surface_mode):
        """
        30、反水面作战行动 导航；推演方条令无法设置为Inherit
        :param navigation_surface_mode: NavigationAS, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if navigation_surface_mode.value == 999:
            doctrine = '{navigation_surface_mode=\"inherit\"}'
        else:
            doctrine = f"{{navigation_surface_mode='{navigation_surface_mode.value}'}}"
        return self._set_doctrine(doctrine)

    def avoid_contact(self, avoid_item):
        """
        31、反潜作战行动，规避搜索；推演方条令无法设置为Inherit
        :param avoid_item: AvoidContact, 枚举
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if avoid_item.value == 999:
            doctrine = '{avoid_contact=\"inherit\"}'
        else:
            doctrine = f"{{avoid_contact='{avoid_item.value}'}}"
        return self._set_doctrine(doctrine)

    def dive_on_threat(self, select_item):
        """
        32、反潜作战行动，探测到威胁进行下潜；推演方条令无法设置为Inherit
        :param select_item: DiveOnThreat
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if select_item.value == 999:
            doctrine = '{dive_on_threat=\"inherit\"}'
        else:
            doctrine = f"{{dive_on_threat='{select_item.value}'}}"
        return self._set_doctrine(doctrine)

    def recharge_on_patrol(self, select_item):
        """
        33、反潜作战行动，充电电池 运输/站点；推演方条令无法设置为Inherit
        :param select_item: RechargePercent
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if select_item.value == 999:
            doctrine = '{recharge_on_patrol=\"inherit\"}'
        else:
            doctrine = f"{{recharge_on_patrol='{select_item.value}'}}"
        return self._set_doctrine(doctrine)

    def recharge_on_attack(self, select_item):
        """
        34、反潜作战行动，充电电池 进攻/防守；推演方条令无法设置为Inherit
        :param select_item: RechargePercent
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if select_item.value == 999:
            doctrine = '{recharge_on_attack=\"inherit\"}'
        else:
            doctrine = f"{{recharge_on_attack='{select_item.value}'}}"
        return self._set_doctrine(doctrine)

    def use_aip(self, select_item):
        """
        35、反潜作战行动，使用AIP技术；推演方条令无法设置为Inherit
        :param select_item: UseAIP
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if select_item.value == 999:
            doctrine = '{use_aip=\"inherit\"}'
        else:
            doctrine = f"{{use_aip='{select_item.value}'}}"
        return self._set_doctrine(doctrine)

    def dipping_sonar(self, select_item):
        """
        36、反潜作战行动， 吊放声呐；推演方条令无法设置为Inherit
        :param select_item: DippingSonar
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if select_item.value == 999:
            doctrine = '{dipping_sonar=\"inherit\"}'
        else:
            doctrine = f"{{dipping_sonar='{select_item.value}'}}"
        return self._set_doctrine(doctrine)

    def navigation_sub(self, select_item):
        """
        37、反潜作战行动， 导航；推演方条令无法设置为Inherit
        :param select_item: NavigationSub
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if select_item.value == 999:
            doctrine = '{navigation_subsurface_mode=\"inherit\"}'
        else:
            doctrine = f"{{navigation_subsurface_mode='{select_item.value}'}}"
        return self._set_doctrine(doctrine)

    def navigation_land(self, select_item):
        """
        38、陆战导航；推演方条令无法设置为Inherit
        :param select_item: NavigationLand
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if select_item.value == 999:
            doctrine = '{navigation_land_mode=\"inherit\"}'
        else:
            doctrine = f"{{navigation_land_mode='{select_item.value}'}}"
        return self._set_doctrine(doctrine)

    def set_weapon_release_authority(self, weapon_dbid, target_type, quantity_salvo=2, shooter_salvo=1,
                                     firing_range='none', self_defense='max'):
        """
        39、设置条令的武器使用规则
        :param weapon_dbid: {str: 武器的数据库ID}
        :param target_type: 枚举WRA_WeaponTargetType的值, global_util.py中定义，例如 WRA_WeaponTargetType.Aircraft_Unspecified 飞机未指明
        :param quantity_salvo: {str: 'n'-齐射武器数, 'inherit'-继承设置, 'max'-全量齐射, 'none'-禁用}
        :param shooter_salvo: {str: 'n'-齐射发射架数，'inherit'-继承设置, 'max'-全量齐射}
        :param firing_range: {str: 'n'-自动开火距离，'inherit'-继承设置, 'none'-禁用自动开火}
        :param self_defense: {str: 'n'-自动防御距离, 'inherit'-继承设置, 'max'-最大射程射击, 'none'-禁用自卫}
        注：其中n为数字。
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_set_weapon_release_authority(self, weapon_dbid, target_type, quantity_salvo,
                                                                  shooter_salvo, firing_range, self_defense)

    def wra_qty_salvo(self, weaponID, target_type, select_item):
        """
        40、武器使用规则--齐射武器数
        :param weaponID: str, 武器DBID
        :param target_type: WRA_WeaponTargetType
        :param select_item: 'inherit'、'system'、'Max'或数字字符串, 
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_wra_qty_salvo(self, weaponID, target_type, select_item)

    def wra_shooter_salvo(self, weaponID, target_type, select_item):
        """
        41、武器使用规则--齐射发射架数
        :param weaponID: str,武器DBID
        :param target_type: WRA_WeaponTargetType
        :param select_item: 'inherit'、'system'、'Max'或数字字符串
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_wra_shooter_salvo(self, weaponID, target_type, select_item)

    def wra_firing_range(self, weaponID, target_type, select_item):
        """
        42、武器使用规则 - -自动开火距离
        :param weaponID: str, 武器DBID
        :param target_type:WRA_WeaponTargetType
        :param select_item: 'inherit'、'system'、'Max'或数字字符串
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_wra_firing_range(self, weaponID, target_type, select_item)

    def wra_self_defence_distance(self, weaponID, target_type, select_item):
        """
        43、武器使用规则--自动防御距离
        :param weaponID: str, 武器DBID
        :param target_type: WRA_WeaponTargetType
        :param select_item: 'inherit'、'system'、'Max'或数字字符串
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        return self._game_server.api_wra_self_defence_distance(self, weaponID, target_type, select_item)

    def withdraw_on_damage(self, damage_status):
        """
        44、满足如下条件时撤退 - -毁伤程度大于；推演方条令无法设置为Inherit
        :param damage_status: DamageThreshold
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if damage_status.value == 999:
            doctrine = '{withdraw_on_damage=\"inherit\"}'
        else:
            doctrine = f"{{withdraw_on_damage='{damage_status.value}'}}"
        return self._set_doctrine(doctrine)

    def withdraw_on_fuel(self, fuel_status):
        """
        45、满足如下条件时撤退--燃油少于；推演方条令无法设置为Inherit
        :param fuel_status: FuelQuantityThreshold
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if fuel_status.value == 999:
            doctrine = '{withdraw_on_fuel=\"inherit\"}'
        else:
            doctrine = f"{{withdraw_on_fuel='{fuel_status.value}'}}"
        return self._set_doctrine(doctrine)

    def withdraw_on_attack(self, weapon_status):
        """
        46、满足如下条件时撤退--主要攻击攻击武器至少处于；推演方条令无法设置为Inherit
        :param weapon_status: WeaponQuantityThreshold
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if weapon_status.value == 999:
            doctrine = '{withdraw_on_attack=\"inherit\"}'
        else:
            doctrine = f"{{withdraw_on_attack='{weapon_status.value}'}}"
        return self._set_doctrine(doctrine)

    def withdraw_on_defence(self, weapon_status):
        """
        47、满足如下条件时撤退--主要防御武器至少；推演方条令无法设置为Inherit
        :param weapon_status: WeaponQuantityThreshold
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if weapon_status.value == 999:
            doctrine = '{withdraw_on_defence=\"inherit\"}'
        else:
            doctrine = f"{{withdraw_on_defence='{weapon_status.value}'}}"
        return self._set_doctrine(doctrine)

    def deploy_on_damage(self, damage_status):
        """
        48、满足如下条件时重新部署--毁伤程度小于；推演方条令无法设置为Inherit
        :param damage_status: DamageThreshold
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if damage_status.value == 999:
            doctrine = '{deploy_on_damage=\"inherit\"}'
        else:
            doctrine = f"{{deploy_on_damage='{damage_status.value}'}}"
        return self._set_doctrine(doctrine)

    def deploy_on_fuel(self, fuel_status):
        """
        49、满足如下条件时重新部署--燃油至少处于；推演方条令无法设置为Inherit
        :param fuel_status: FuelQuantityThreshold
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if fuel_status.value == 999:
            doctrine = '{deploy_on_fuel=\"inherit\"}'
        else:
            doctrine = '{deploy_on_fuel=%d}' % fuel_status.value
            doctrine = f"{{deploy_on_fuel='{fuel_status.value}'}}"
        return self._set_doctrine(doctrine)

    def deploy_on_attack(self, weapon_status):
        """
        50、满足如下条件时重新部署--主要攻击武器处于；推演方条令无法设置为Inherit
        :param weapon_status: WeaponQuantityThreshold
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if weapon_status.value == 999:
            doctrine = '{deploy_on_attack=\"inherit\"}'
        else:
            doctrine = '{deploy_on_attack=%d}' % weapon_status.value
            doctrine = f"{{deploy_on_attack='{weapon_status.value}'}}"
        return self._set_doctrine(doctrine)

    def deploy_on_defence(self, weapon_status):
        """
        51、满足如下条件时重新部署--主要防御武器处于；推演方条令无法设置为Inherit
        :param weapon_status: WeaponQuantityThreshold
        :return: 指令执行结果, Reply对象, 和global_util.py中Reply类定义类似
        """
        if weapon_status.value == 999:
            doctrine = '{deploy_on_defence=\"inherit\"}'
        else:
            doctrine = f"{{deploy_on_defence='{weapon_status.value}'}}"
        return self._set_doctrine(doctrine)

    def get_doctrineWRA(self):
        """
        52、获取武器使用规则
        :return: 条令结果
        """
        return self._game_server.api_get_doctrineWRA(self)



