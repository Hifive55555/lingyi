# -*- coding:utf-8 -*-
# Author: 退退退不掉队-王鹏扉、王睿

from engine.LingYi.entitys.player import Player
import logging
import math

class Agent(Player):
    def __init__(self, side_name, params):
        super(Agent, self).__init__(side_name)
        self.Flag_WSD = False
        self.Missile = []

    def initial(self, situation):
        pass
    def step(self, time_elapse, situation):
        for guid,unit in situation[0].items():
            dbid = unit.get("dbid")
            # if dbid == 3128:
            #     unitObj = self.get_unit(guid)
            #     unitObj.attack_BOL(22.879093, -84.821166, 0, 1575, 2)
            #     unitObj.attack_BOL(22.744197, -84.503723, 0, 1575, 3)
            #     unitObj.attack_BOL(22.891325, -84.394428, 0, 1575, 2)
            if dbid == 509:
                unitObj = self.get_unit(guid)
                unitObj.attack_BOL(17.842501,-82.158427,0,1189,6)
            # if dbid == 346:
            #     unit_obj = self.get_unit(guid)
            #     unit_obj.attack_BOL(17.318506, -82.608131, 0, 722, 4)





        for guid,unit in situation[0].items():
            if unit['category'] == 'Weapon' and unit['dbid'] in {1189} and guid not in self.Missile:
                missileObj = self.get_unit(guid)
                missileObj.EMCON_Obey_doctrine(False)
                missileObj.switch_radar(True,)
                self.Missile.append(guid)