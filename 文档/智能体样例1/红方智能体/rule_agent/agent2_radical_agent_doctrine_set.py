# -*- coding:utf-8 -*-
# Author: WuRuiZhuo/MouQingPing
"""
设置我方条令
激进版
"""

import logging

from engine.LingYi.entitys.global_util import *
from engine.LingYi.entitys.player import Player


class Agent(Player):
    def __init__(self, side_name, params):
        Player.__init__(self, side_name)
        logging.info('%s:%s play game' % (side_name, self.__class__.__name__))

    def initial(self, situation):
        """
        初始化函数，武器条令设置
        :param situation: tuple: units, contacts
        :return:
        """
        '''
        战略武器使用
        '''
        # 是否使用核武器
        self.use_nuclear_weapons(EUseNuclear.No)  # 不使用

        '''
        交战规则
        '''
        # 武器控制状态，对空；对水面；对潜；对地。
        self.doctrine_weapon_control_status_air(WeaponControlStatus.Free)  # 武器控制状态，对空；自由开火
        self.doctrine_weapon_control_status_surface(WeaponControlStatus.Free)  # 武器控制状态，对海，自由开火
        self.doctrine_weapon_control_status_subsurface(WeaponControlStatus.Free)  #  武器控制状态，对潜；自由开火
        self.doctrine_weapon_control_status_land(WeaponControlStatus.Free)  # 武器控制状态，对地：自由开火
        # 攻击时忽略计划航线设置 是
        self.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.No)
        # 接战模糊位置目标  乐观决策
        self.doctrine_engaging_ambiguous_targets(BehaviorTowardsAmbigousTarget.Optimistic)
        # 接战临机出现目标  否（只与任务目标交战）
        self.doctrine_engage_opportunity_targets(EngageWithContactTarget.No_Only)
        '''
        电磁管控
        '''
        # 电磁管控与上级一致
        self.doctrine_SetEMCON_Inherit()
        # 攻击时忽略电磁管控
        self.doctrine_ignore_emcon_under_attack(IgnoreEMCONUnderAttack.No)

        '''
        杂项
        '''
        # 鱼雷射程 严格射程
        self.torpedoes_kinematic_range(UseTorpedoesKinematicRange.Yes)
        # 自动规避 是
        self.doctrine_automatic_evasion(AutomaticEvasion.Yes)
        # 加油 / 途中补给 是
        self.doctrine_refuel(ERefuel.No)
        # 所选单元加油/途中补给 选择我们和目标之间的加油机，但不允许往回飞
        self.doctrine_refuel_select(ERefuelSelect.Nearest)
        # 给盟军加油 / 途中补给 否
        self.doctrine_refuel_allied(ERefuelAllied.Yes)

        '''
        空中作战行动
        '''
        # 空战节奏 一般强度出动
        self.doctrine_air_operations_tempo(AirOpsTempo.Surge)
        # 快速周转 是
        self.doctrine_quick_turnaround(QuickTurnAround.FightersAndASW)
        # 燃油状态,预先规划 达到计划储备燃油状态时，立即终止任务返回基地
        self.doctrine_fuel_state_planned(FuelState.Bingo)
        # 燃油状态，返航 否，当达到燃油状态时作战单元并不返回
        self.doctrine_fuel_state_rtb(FuelStateRTB.No)
        # 武器状态，预先规划 任务武器已耗光.允许使用航炮对临机目标进行打击（推荐）：
        self.doctrine_weapon_state_planned(WeaponStatePlanned.WinchesterUseAirGuns)
        # 武器状态-返航 否，飞机达到武器状态时并不返回基地
        self.doctrine_weapon_state_rtb(WeaponStateRTB.No)
        # 空对地扫射（航炮） 是
        self.doctrine_gun_strafing(GunStrafeGroundTargets.Yes)
        # 丢弃武器 否
        self.doctrine_jettison_ordnance(JettisonOrdnance.No)
        # 超视距交战  相机而动
        self.doctrine_bvr_logic(BvrLogic.Operation)

        '''
        反舰作战行动
        '''
        # 反水面战模式下使用防空导弹 否
        self.use_sams_in_anti_surface_mode(UseSAMsInASuWMode.No)
        # 反水面作战行动,与目标保持距离 是
        self.doctrine_maintain_standoff(MaintainStandoff.Yes)

        '''
        反潜作战行动
        '''
        # 反潜作战行动，规避搜索 是，除非自防御
        self.avoid_contact(AvoidContact.No)
        # 反潜作战行动，探测到威胁进行下潜 是，当电子侦察措施探测和目标接近时
        self.dive_on_threat(DiveOnThreat.No)
        # 反潜作战行动，充电电池 运输/站点 当电池剩余60%电量
        self.recharge_on_patrol(RechargePercent.RechargeEmpty)
        # 反潜作战行动，充电电池 进攻/防守 当电池剩余10%电量
        self.recharge_on_attack(RechargePercent.RechargeEmpty)
        # 反潜作战行动，使用AIP技术 是，当参与进攻与防御时
        self.use_aip(UseAIP.YesAlways)
        # 反潜作战行动， 吊放声呐 在盘旋于46米高度时自动部署
        self.dipping_sonar(DippingSonar.Manual)

        '''
        电磁管控
        '''
        # 雷达切换
        self.doctrine_switch_radar(True)
        # 干扰机切换
        self.doctrine_switch_oecm(True)
        # 声纳切换
        self.doctrine_switch_sonar(True)

        '''
        撤退与重新部署
        '''
        # 毁伤程度大于
        self.withdraw_on_damage(DamageThreshold.Ignore)
        # 燃油少于
        self.withdraw_on_fuel(FuelQuantityThreshold.Ignore)

        text = "=================条令设置完毕================="  # 智能体调度消息输出
        test = self.agent_message_text(text=text)
        print(f'纯文本显示输出返回：{test}')

    def step(self, time_elapse, situation):
        pass

    def deduction_end(self):
        # agent结束后自动被调用函数， 可保存模型，比如记录本局策略后的得分等
        pass

    def is_done(self):
        pass

