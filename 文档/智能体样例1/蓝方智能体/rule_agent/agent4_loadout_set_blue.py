# -*- coding:utf-8 -*-
# Author: 退退退不掉队-王睿、王鹏扉、史展旭

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
            unit_name = unit.get("name", "")  # 获取飞机的完整名称

            #H国单实体
            if dbid == 1392: self.set_aircraft_loadout_plan_time(guid, 1438)  #S-2E
            if dbid == 1748:                                                  #F-15K
                if unit_name == "F-15K型 #2":
                    self.set_aircraft_loadout_plan_time(guid, 6366)
                if unit_name == "F-15K型 #1":
                    self.set_aircraft_loadout_plan_time(guid, 6367)
            if dbid == 2582: self.set_aircraft_loadout_plan_time(guid, 14993) #E-737
            if dbid == 3599: self.set_aircraft_loadout_plan_time(guid, 4710)  #F-5F
            if dbid == 4513: self.set_aircraft_loadout_plan_time(guid, 22847) #A330-220 货物投送？
            if dbid == 4955: self.set_aircraft_loadout_plan_time(guid, 17051) #FA-50
            if dbid == 4980: self.set_aircraft_loadout_plan_time(guid, 2618)  #F-16DJ
            if dbid == 5184: self.set_aircraft_loadout_plan_time(guid, 28614) #KF-21
            #M国单实体
            if dbid == 290 : self.set_aircraft_loadout_plan_time(guid, 8091)  #E-8C
            if dbid == 318 : self.set_aircraft_loadout_plan_time(guid, 8103)  #EP-3E
            if dbid == 320 : self.set_aircraft_loadout_plan_time(guid, 14471) #EC-130H
            if dbid == 541 : self.set_aircraft_loadout_plan_time(guid, 8823)  #RC-135X
            if dbid == 808 : self.set_aircraft_loadout_plan_time(guid, 8841)  #KC-135T
            if dbid == 2918: self.set_aircraft_loadout_plan_time(guid, 8583)  #U-2S
            if dbid == 3687: self.set_aircraft_loadout_plan_time(guid, 18313) #KC-46A 货物运输?
            if dbid == 3821: self.set_aircraft_loadout_plan_time(guid, 26462) #F-22A
            if dbid == 3835: self.set_aircraft_loadout_plan_time(guid, 26470) #F-35FA
            if dbid == 4325: self.set_aircraft_loadout_plan_time(guid, 22743) #B-1B
            if dbid == 4326: self.set_aircraft_loadout_plan_time(guid, 27353) #B-2A
            if dbid == 4860: self.set_aircraft_loadout_plan_time(guid, 8969)  #SR-71(Bx)
            if dbid == 5449: self.set_aircraft_loadout_plan_time(guid, 16974) #AC-130J
            #M国海外
            if dbid == 4455: self.set_aircraft_loadout_plan_time(guid, 16941) #F-15E
            if dbid == 5460: self.set_aircraft_loadout_plan_time(guid, 25316) #F-16C
            #R国单实体
            if dbid == 346 :                                                  #F-2A
                if unit_name == "F-2A型 #1":
                    self.set_aircraft_loadout_plan_time(guid, 26667)
                if unit_name == "F-2A型 #2":
                    self.set_aircraft_loadout_plan_time(guid, 26667)
                if unit_name == "F-2A型 #3":
                    self.set_aircraft_loadout_plan_time(guid, 26667)
                if unit_name == "F-2A型 #4":
                    self.set_aircraft_loadout_plan_time(guid, 1751)
                if unit_name == "F-2A型 #5":
                    self.set_aircraft_loadout_plan_time(guid, 1751)
                if unit_name == "F-2A型 #6":
                    self.set_aircraft_loadout_plan_time(guid, 1751)
            if dbid == 1795: self.set_aircraft_loadout_plan_time(guid, 8845)  #KC-767
            if dbid == 2164: self.set_aircraft_loadout_plan_time(guid, 8088)  #E-767
            if dbid == 2936: self.set_aircraft_loadout_plan_time(guid, 15708) #P-1
            if dbid == 3383: self.set_aircraft_loadout_plan_time(guid, 9609)  #F-15DJ
            if dbid == 4517: self.set_aircraft_loadout_plan_time(guid, 18313) #KC-46A
            
            #舰载
            if dbid == 2058: self.set_aircraft_loadout_plan_time(guid, 2891)  #SH-60K
            if dbid == 4031: self.set_aircraft_loadout_plan_time(guid, 17804) #MQ-8C 飞机投送？
            if dbid == 4293: self.set_aircraft_loadout_plan_time(guid, 14629) #E-2D
            if dbid == 4518: self.set_aircraft_loadout_plan_time(guid, 22925) #EA-18G
            if dbid == 4592: self.set_aircraft_loadout_plan_time(guid, 27583)  #AV-8B
            if dbid == 4874: self.set_aircraft_loadout_plan_time(guid, 10098) #F-35C
            if dbid == 4971: self.set_aircraft_loadout_plan_time(guid, 25787) #F/A-18F
            if dbid == 5258: self.set_aircraft_loadout_plan_time(guid, 28849) #F/A-18E
            if dbid == 5037: self.set_aircraft_loadout_plan_time(guid, 1100)  #MH-60R
            if dbid == 3374: self.set_aircraft_loadout_plan_time(guid, 25182) #AW-159反潜



    def initial(self, situation):
        self.set_aircraft_loadout_initial(situation) 

    def step(self, time_elapse, situation):
        pass