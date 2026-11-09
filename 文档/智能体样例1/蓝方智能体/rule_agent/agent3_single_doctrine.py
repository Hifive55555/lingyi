# -*- coding:utf-8 -*-
# Author: 退退退不掉队-王睿、王鹏扉

"""
单独对飞机进行条令设置
"""

import logging
import time

# 1. 【关键修改】从 global_util 中导入所需的枚举类型
from engine.LingYi.entitys.global_util import *
from engine.LingYi.entitys.agent_base import RuleAgentBase
from engine.LingYi.entitys.player import Player # 虽然继承自RuleAgentBase，但为了获取self.aircrafts等属性，Player类更方便


class Agent(Player): # 建议继承自 Player 以方便地访问 self.aircrafts
    def __init__(self, side_name, params):
        super(Agent, self).__init__(side_name) # 使用 super() 是更现代和推荐的写法
        logging.info('%s:%s play game' % (side_name, self.__class__.__name__))
    
    def set_custom_aircraft_doctrines(self):
        """
        遍历所有我方飞机，并为它们单独设置条令。
        """
        print("正在为所有飞机单位配置自定义条令...")

        my_aircrafts = self.aircrafts

        for unit_id, aircraft_obj in my_aircrafts.items():
            
            print(f"  -> 正在为飞机: {aircraft_obj.Name} (ID: {unit_id}) 设置条令...")

            aircraft_obj.doctrine_refuel_select(ERefuelSelect.Include_NoBack)
            aircraft_obj.doctrine_fuel_state_planned(FuelState.Bingo)
            aircraft_obj.doctrine_fuel_state_rtb(FuelStateRTB.No)
            aircraft_obj.doctrine_weapon_state_planned(WeaponStatePlanned.WinchesterUseAirGuns)
            aircraft_obj.doctrine_weapon_state_rtb(WeaponStateRTB.No)
            aircraft_obj.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.No)

            time.sleep(0.5)
            # --- 其他可用选项 ---
            # aircraft_obj.doctrine_fuel_state_rtb(FuelStateRTB.Bingo) # 燃油严重不足时返航
            # aircraft_obj.doctrine_fuel_state_rtb(FuelStateRTB.No)    # 从不因燃油状态自动返航

        print("所有飞机的自定义条令配置完成。")

    def initial(self, situation):
        # 将此逻辑放在 initial 中，确保在推演开始时所有飞机都已配置好
        self.set_custom_aircraft_doctrines()

    def step(self, time_elapse, situation):
        pass