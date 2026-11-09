# -*- coding:utf-8 -*-


import logging
from engine.LingYi.entitys.global_util import *
from engine.LingYi.entitys.agent_base import RuleAgentBase
from engine.LingYi.entitys.player import Player
import time

class Agent(Player):
    def __init__(self, side_name, params):
        super(Agent, self).__init__(side_name) 
        logging.info('%s:%s play game' % (side_name, self.__class__.__name__))
    
    def set_custom_aircraft_doctrines(self):
        """
        遍历所有我方飞机，并为它们单独设置条令。
        """
        print("正在为所有飞机单位配置自定义条令...")

        my_aircrafts = self.aircrafts

        for unit_id, aircraft_obj in my_aircrafts.items():
            
            print(f"  -> 正在为飞机: {aircraft_obj.Name} (ID: {unit_id}) 设置条令...")

            aircraft_obj.doctrine_refuel_select(ERefuelSelect.Nearest)
            aircraft_obj.doctrine_fuel_state_planned(FuelState.Bingo)
            aircraft_obj.doctrine_fuel_state_rtb(FuelStateRTB.No)
            aircraft_obj.doctrine_weapon_state_planned(WeaponStatePlanned.ShotgunOneEngageAirguns)
            aircraft_obj.doctrine_weapon_state_rtb(WeaponStateRTB.No)
            aircraft_obj.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.No)
            aircraft_obj.doctrine_automatic_evasion(AutomaticEvasion.Yes)
            weapon_info_dict = aircraft_obj.get_weapon_info()
            for weapon_dbid, count in weapon_info_dict.items():
                if count > 0:
                    aircraft_obj.wra_firing_range(weapon_dbid, WRA_WeaponTargetType.Guided_Weapon_Unspecified,0)
                    aircraft_obj.wra_firing_range(weapon_dbid, WRA_WeaponTargetType.Guided_Weapon_Supersonic_Sea_Skimming,0)
            time.sleep(0.5)

        print("所有飞机的自定义条令配置完成。")

    def initial(self, situation):
        # 将此逻辑放在 initial 中，确保在推演开始时所有飞机都已配置好
        self.set_custom_aircraft_doctrines()

    def step(self, time_elapse, situation):
        pass