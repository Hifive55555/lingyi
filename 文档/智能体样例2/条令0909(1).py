
import logging

from engine.LingYi.entitys.global_util import *
from engine.LingYi.entitys.player import Player
# from agent.agent_base_2025 import *

class Agent(Player):
    def __init__(self, side_name, params):
        Player.__init__(self, side_name)
        logging.info('%s:%s play game' % (side_name, self.__class__.__name__))
        # self.save_jason_flag=0


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
        self.doctrine_weapon_control_status_air(WeaponControlStatus.Free)  # 自由开火
        self.doctrine_weapon_control_status_surface(WeaponControlStatus.Free)  # 自由开火
        self.doctrine_weapon_control_status_subsurface(WeaponControlStatus.Free)  # 自由开火
        self.doctrine_weapon_control_status_land(WeaponControlStatus.Free)  # 自由开火
        # 攻击时忽略计划航线设置
        self.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.Yes)
        # 接战临机出现目标
        self.doctrine_engage_opportunity_targets(EngageWithContactTarget.No_Only)
        # 接战模糊位置目标
        self.doctrine_engaging_ambiguous_targets(BehaviorTowardsAmbigousTarget.Optimistic)

        '''
        电磁管控
        
        self.doctrine_electromagnetism(IgnoreEMCONUnderAttack.Ignore_EMCON_While_Under_Attack)
        '''


        '''
        杂项
        '''
        # 鱼雷射程
        self.torpedoes_kinematic_range(UseTorpedoesKinematicRange.PracticalRange)
        # 自动规避
        self.doctrine_automatic_evasion(AutomaticEvasion.Yes)
        # 加油 / 途中补给
        self.doctrine_refuel(ERefuel.Yes_NoTanker)
        # 所选单元加油/途中补给
        self.doctrine_refuel_select(ERefuelSelect.Include_NoBack)
        # 给盟军加油 / 途中补给
        self.doctrine_refuel_allied(ERefuelAllied.No)

        '''
        空中作战行动
        '''
        # 空战节奏
        self.doctrine_air_operations_tempo(AirOpsTempo.Sustained)
        # 快速周转
        self.doctrine_quick_turnaround(QuickTurnAround.No)
        # 燃油状态,预先规划
        self.doctrine_fuel_state_planned(FuelState.Bingo)
        # 燃油状态，返航
        self.doctrine_fuel_state_rtb(FuelStateRTB.No)
        # 武器状态，预先规划 任务武器已耗光.允许使用航炮对临机目标进行打击（推荐）：
        self.doctrine_weapon_state_planned(WeaponStatePlanned.WinchesterUseAirGuns)
        # 武器状态-返航
        self.doctrine_weapon_state_rtb(WeaponStateRTB.No)
        # 空对地扫射
        self.doctrine_gun_strafing(GunStrafeGroundTargets.Yes)
        # 丢弃武器
        self.doctrine_jettison_ordnance(JettisonOrdnance.No)
        # 超视距交战  相机而动
        self.doctrine_bvr_logic(BvrLogic.Operation)

        '''
        反舰作战行动
        '''
        # 反水面战模式下使用防空导弹
        self.use_sams_in_anti_surface_mode(UseSAMsInASuWMode.No)
        # 反水面作战行动,与目标保持距离
        self.doctrine_maintain_standoff(MaintainStandoff.Yes)

        '''
        反潜作战行动
        '''
        # 反潜作战行动，规避搜索
        self.avoid_contact(AvoidContact.No)
        # 反潜作战行动，探测到威胁进行下潜
        self.dive_on_threat(DiveOnThreat.YesESMOnly)
        # 反潜作战行动，充电电池 运输/站点
        self.recharge_on_patrol(RechargePercent.Recharge60Percent)
        # 反潜作战行动，充电电池 进攻/防守
        self.recharge_on_attack(RechargePercent.Recharge10Percent)
        # 反潜作战行动，使用AIP技术
        self.use_aip(UseAIP.YesAttackOnly)
        # 反潜作战行动， 吊放声呐
        self.dipping_sonar(DippingSonar.Automatically)

        '''
        #电磁管控
        
        # 雷达切换
        self.doctrine_switch_radar(True)
        # 干扰机切换
        self.doctrine_switch_oecm(True)
        # 声纳切换
        self.doctrine_switch_sonar(True)

        
        #消息输出
        
        self.agent_message_text('条令设置完成')
        #self.agent_message_intelligence
        #self.agent_message_unit_range
        #self.agent_message_arrow
        #self.agent_message_are
        '''

    def step(self, time_elapse, situation):
        # if self.save_jason_flag==0:
        #     with open('2025red.json', 'w', encoding='utf-8') as f:
        #         json.dump(situation[0], f, ensure_ascii=False, indent=4)
        #     self.save_jason_flag=1
        pass

    def deduction_end(self):
        # agent结束后自动被调用函数， 可保存模型，比如记录本局策略后的得分等
        pass

    def is_done(self):
        pass
        # return True
        # agent主动结束本局推演，比如一定胜利或失败后
        # 只能训练时调用此函数，比赛对战时此函数不可用
        # if self.TotalScore >= 1500 or self.TotalScore <= -1500:
        #     return True
        # return False
