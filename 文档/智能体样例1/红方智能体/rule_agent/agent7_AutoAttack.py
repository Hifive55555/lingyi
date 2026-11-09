# -*- coding:utf-8 -*-
# Author: TTTBDD

from engine.LingYi.entitys.player import Player
import logging
import math

class Agent(Player): 
    def __init__(self, side_name, params):
        super(Agent, self).__init__(side_name)
        self.Missile = []
        self.MOSAirport = None
        self.MAirport = None
        self.ShiZong = None
        self.DuDao = None
        self.ZhaoRi = None
        self.target_id = None

    def initial(self, situation):
        pass
    def step(self, time_elapse, situation):
        contact_select_list = list(self.client_info.get('contact', {}).keys())
        #确定K-9炮兵中队位置后，手动前端添加以防止误伤医疗车
        if contact_select_list:
            self.target_id = contact_select_list[0]
        #根据经纬度确定打击目标
        for contact_guid,contact in situation[1].items():
            if not self.MOSAirport:
            #M国海外机场
                if contact['Lat'] > 24 and contact['Lat'] < 25 and contact['Lon'] < -81 and contact['Lon'] > -82:
                    self.MOSAirport = contact_guid
                    self.agent_message_text(text=f"[情报] {contact.get('Name', '目标')} 已加入目标")
            if not self.MAirport:
            #M国实体机场
                if contact['Lat'] > 30 and contact['Lat'] < 31 and contact['Lon'] < -94 and contact['Lon'] > -95:
                    self.MAirport = contact_guid
                    self.agent_message_text(text=f"[情报] {contact.get('Name', '目标')} 已加入目标")
            if not self.ShiZong:
            #世宗大王
                if contact['Lat'] > 20 and contact['Lat'] < 21.8 and contact['Lon'] < - 89 and contact['Lon'] > - 92 and contact['Type'] == 2:
                    self.ShiZong = contact_guid
                    self.agent_message_text(text=f"[情报] {contact.get('Name', '目标')} 已加入目标")
            if not self.DuDao:
            #独岛攻击舰
                if contact['Lat'] > 21.8 and contact['Lat'] < 23 and contact['Lon'] < - 89 and contact['Lon'] > - 92 and contact['Type'] == 2:
                    self.DuDao = contact_guid
                    self.agent_message_text(text=f"[情报] {contact.get('Name', '目标')} 已加入目标")
                    
                    
        for guid,unit in situation[0].items():
            dbid = unit.get("dbid")
            if dbid == 1845: 
                #舞水端打击H国实体机场及天马地导
                unitObj = self.get_unit(guid)
                unitObj.attack_BOL(18.38,-95.23,0,2439,4)
                unitObj.attack_BOL(18.26,-95.25,0,2439,2)
            if dbid == 3367: 
                #北朝鲜打击H国实体机场及天马地导
                unitObj = self.get_unit(guid)
                unitObj.attack_BOL(18.38,-95.23,0,3817,5)
                unitObj.attack_BOL(18.26,-95.25,0,3817,1)
            if dbid == 2816: 
                #戈尔打击朝日
                unitObj = self.get_unit(guid)
                unitObj.attack_BOL(23.148,-84.709,0,1173,16)
                unitObj.attack_BOL(23.148,-84.709,0,3218,8)
            if dbid == 2974: 
                #间谍船打击朝日
                unitObj = self.get_unit(guid)
                unitObj.attack_BOL(23.148,-84.709,0,1365,3)
                unitObj.attack_BOL(23.148,-84.709,0,1480,6)
            if dbid == 677: 
                #亚森打击提康德罗加
                unitObj = self.get_unit(guid)
                unitObj.attack_BOL(19.44,-106.7,0,1173,24)
            if dbid == 656: 
                #库兹涅佐夫打击M国海外机场
                unitObj = self.get_unit(guid)
                unitObj.attack_weapon_allocate_to_target(self.MOSAirport,2713,12,[(22.74,-81.52)]) 
                #此坐标为SAM-4地导上空，经过此处意为消耗其地空导弹以便于后续打击地导
            if dbid == 627: 
                #新浦级潜艇打击M国海外机场
                unitObj = self.get_unit(guid)
                unitObj.attack_weapon_allocate_to_target(self.MOSAirport,3348,16,[(22.74,-81.52)])
            if dbid == 5554:
                #Blackjack轰炸机打击M国实体机场
                unitObj = self.get_unit(guid)
                if unit['lat'] > 16.7:
                    #测试得飞机飞行速度快于导弹速度，限制其较晚发射以更快打击机场
                    unitObj.attack_weapon_allocate_to_target(self.MAirport,935,12,)
            if dbid == 2776:
            #KN-01打击世宗大王
                unitObj = self.get_unit(guid)
                if self.ShiZong:
                    unitObj.attack_weapon_allocate_to_target(self.ShiZong,3351,6,)
            if dbid == 2851:
            #南高打击世宗大王
                unitObj = self.get_unit(guid)
                if self.ShiZong:
                    unitObj.attack_weapon_allocate_to_target(self.ShiZong,18,4,)
                    unitObj.attack_weapon_allocate_to_target(self.ShiZong,969,4,)
            if dbid ==417:
            #彼得大帝打击世宗大王
                unitObj = self.get_unit(guid)
                if self.ShiZong:
                    unitObj.attack_weapon_allocate_to_target(self.ShiZong,3361,2,)
            if dbid == 2837:
            #对图22轰炸机，优先打击世宗，其次选择打击独岛
                unitObj = self.get_unit(guid)
                if unit['lon'] < - 89:
                    if self.ShiZong:
                        unitObj.attack_weapon_allocate_to_target(self.ShiZong,3122,2,)
                    if self.DuDao:
                        unitObj.attack_weapon_allocate_to_target(self.DuDao,3122,2,)
            if dbid == 2269:
            #谷山手动打击K-9
                unitObj = self.get_unit(guid)
                if self.target_id:
                    unitObj.attack_weapon_allocate_to_target(self.target_id,2955,6,)


        for guid,unit in situation[0].items():  
            if unit['category'] == 'Weapon' and unit['dbid'] in {1173,1480,18}:
            #对于带有雷达的导弹，开启其雷达
                missileObj = self.get_unit(guid)
                missileObj.EMCON_Obey_doctrine(False)
                missileObj.switch_radar(True,) 
                if unit['lat'] > 23.3:
                #对于已经离开可打击朝日范围的导弹，引导其前去打击日向机
                    self.Missile.append(guid)
                    missileObj.plotted_course([(23.5558,-84.9885)])
            if unit['category'] == 'Weapon' and unit['dbid'] == 3218 and guid not in self.Missile:
                #测试得“炙热”巡航导弹在航线不直的情况下会在抵达目标位置前耗尽燃油，故限制其航线为直线
                missileObj = self.get_unit(guid)
                self.Missile.append(guid)
                missileObj.plotted_course([(20.57,-83.86),(23.148,-84.709)])