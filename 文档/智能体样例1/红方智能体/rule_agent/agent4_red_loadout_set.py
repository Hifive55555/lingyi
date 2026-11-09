# -*- coding:utf-8 -*-
# Author: Liaojiang

import logging


from engine.LingYi.entitys.global_util import AirValidStatus 
from engine.LingYi.entitys.agent_base import RuleAgentBase
from engine.LingYi.entitys.player import Player 

class Agent(Player): 
    def __init__(self, side_name, params):
        super(Agent, self).__init__(side_name) 
        logging.info('%s:%s play game' % (side_name, self.__class__.__name__))
    
    def set_aircraft_loadout_initial(self, situation):
        units = situation[0]
        for guid, unit in units.items():
            if unit.get("category") != "Aircraft":
                continue
                
            dbid = unit.get("dbid")
            unit_name = unit.get("name", "")
            
            #C国单实体
            if dbid == 2346: self.set_aircraft_loadout_plan_time(guid, 5298)  #米格-29
            if dbid == 1342: self.set_aircraft_loadout_plan_time(guid, 5186)  #米格-23ML
            if dbid == 2734: self.set_aircraft_loadout_plan_time(guid, 12816) #米格-21bis
            #E国野战
            if dbid == 4958: self.set_aircraft_loadout_plan_time(guid, 11076) #苏-35S
            if dbid == 4959: self.set_aircraft_loadout_plan_time(guid, 19292) #苏-30SM
            #E国单实体
            if dbid == 770 : self.set_aircraft_loadout_plan_time(guid, 6061)  #图-142MZ
            if dbid == 1336: self.set_aircraft_loadout_plan_time(guid, 8166)  #图-22MR
            if dbid == 2232: self.set_aircraft_loadout_plan_time(guid, 1770)  #T-50
            if dbid == 2293: self.set_aircraft_loadout_plan_time(guid, 8425)  #安-12BK
            if dbid == 2382: self.set_aircraft_loadout_plan_time(guid, 9410)  #3MS-2
            if dbid == 2686: self.set_aircraft_loadout_plan_time(guid, 9007)  #伊尔-78
            if dbid == 3461: self.set_aircraft_loadout_plan_time(guid, 8060)  #A-50U
            if dbid == 3913: self.set_aircraft_loadout_plan_time(guid, 19620) #米格-35
            if dbid == 4289: self.set_aircraft_loadout_plan_time(guid, 21929) #图-214R
            if dbid == 4440: self.set_aircraft_loadout_plan_time(guid, 22482) #伊尔-96
            if dbid == 4607: self.set_aircraft_loadout_plan_time(guid, 25089) #伊尔-22PP
            if dbid == 4728: self.set_aircraft_loadout_plan_time(guid, 25726) #A-100
            if dbid == 5327: self.set_aircraft_loadout_plan_time(guid, 29569) #Su-75
            if dbid == 5554: self.set_aircraft_loadout_plan_time(guid, 30163) #Tu-160M
            #O国单实体
            if dbid == 220 : self.set_aircraft_loadout_plan_time(guid, 15167) #空客A310
            if dbid == 563 : self.set_aircraft_loadout_plan_time(guid, 8874)  #S-100B
            if dbid == 2837: self.set_aircraft_loadout_plan_time(guid, 13758) #图-22M
            if dbid == 3698: self.set_aircraft_loadout_plan_time(guid, 17279)  #JAS 39D
            if dbid == 4960: self.set_aircraft_loadout_plan_time(guid, 27822) #苏-34
            if dbid == 5214: self.set_aircraft_loadout_plan_time(guid, 17284) #EF-2000
            #舰载
            if dbid == 1470: self.set_aircraft_loadout_plan_time(guid, 5944)  #米-14PL
            if dbid == 371 : self.set_aircraft_loadout_plan_time(guid, 821)  #卡-27PL
            if dbid == 608 : self.set_aircraft_loadout_plan_time(guid, 8033)  #卡-31
            if dbid == 3320: self.set_aircraft_loadout_plan_time(guid, 17526) #米格-29K
            if dbid == 4622: self.set_aircraft_loadout_plan_time(guid, 26857) #苏-33

    def initial(self, situation):
        self.set_aircraft_loadout_initial(situation) 

    def step(self, time_elapse, situation):
        pass