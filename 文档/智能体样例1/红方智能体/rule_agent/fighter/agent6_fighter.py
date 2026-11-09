# -*- coding:utf-8 -*-
# Author: 退退退不掉队-王睿、王鹏扉

"""
红方 - 通用战斗机规则智能体 (V11.3 - 最终修正版)
战术目标：
1. (生存) 自动规避【真正有威胁】的来袭导弹。
2. (进攻) 自动索敌并锁定200km范围内【战术价值最高】且【攻击者未满】的敌机。
"""

from engine.LingYi.entitys.player import Player
from engine.LingYi.entitys.global_util import *
from engine.LingYi.entitys import geo 
import numpy as np

from calculate_threat_level_of_the_target import ThreatEvaluator
from calculate_weapon_attack_air_rate import calculate_possibility


class Agent(Player):
    def __init__(self, side_name, params):
        super(Agent, self).__init__(side_name)
        
        self.decision_cooldown = 0
        self.FIGHTER_DBIDs = {2346,1342,2734,4958,4959,3963,2232,3913,5214,1336,2293,2382,2636,3461,4289,4440,4607,4728,5554}
        self.AIR_TO_AIR_MISSILE_DBIDs = {152,1897,1896,2002,1800,1796,2053,2056,2556,352,1896,3128,915,3126,1129,961}
        
        self.evasion_speed = 9999
        self.drag_speed = 9999 
        self.cruise_speed = 'OFF'
        
        self.terminal_evasion_altitude = 'MIN' 
        self.drag_evasion_altitude = 'OFF'
        self.cruise_altitude = 'OFF'

        self.last_decision_time = -self.decision_cooldown
        
        self.fighter_tasks = {} 
        self.target_assignment_counts = {} 
        self.max_attackers_per_target = 2 

        self.threat_evaluator = ThreatEvaluator()
        self.wta_threshold = 0.2
        
        self.engagement_range_km = 200.0

    def initial(self, situation):
        self.agent_message_text(text='[DEBUG] 战斗机WTA智能体(V11.3)已启动。')
        
        for guid, unit in situation[0].items():
            if unit.get('dbid') in self.FIGHTER_DBIDs:
                plane_obj = self.get_unit(guid)
                if plane_obj:
                    plane_obj.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.No)
                    plane_obj.doctrine_weapon_control_status_air(WeaponControlStatus.Free)
                    plane_obj.doctrine_automatic_evasion(AutomaticEvasion.No)

    def step(self, time_elapse, situation):
        if (time_elapse - self.last_decision_time) < self.decision_cooldown:
            return
        self.last_decision_time = time_elapse
        
        units, contacts = situation[0], situation[1]

        self._cleanup_assignments(units, contacts)

        for guid, unit_info in units.items():
            
            if unit_info.get('dbid') not in self.FIGHTER_DBIDs or unit_info.get('alt', 0) <= 100:
                continue
            
            fighter_obj = self.get_unit(guid)
            if not fighter_obj: continue

            # --- 优先级 1: 生存 (规避导弹) ---
            
            imminent_threat,notch_ward = self._find_imminent_threat(unit_info, contacts)
            
            if imminent_threat:
                fighter_obj.doctrine_weapon_control_status_air(WeaponControlStatus.Hold)
                fighter_obj.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.No)
                fighter_obj.EMCON_Obey_doctrine(False)
                fighter_obj.switch_radar(False,) 
                
                dist_km = geo.get_horizontal_distance(
                    (unit_info['lat'], unit_info['lon']), 
                    (imminent_threat['Lat'], imminent_threat['Lon'])
                )
                
                if dist_km <= 60.0:
                    evasion_course = self._calculate_notch_course(unit_info, imminent_threat,notch_ward)
                    try:
                        fighter_obj.set_desired_speed(self.evasion_speed)
                        fighter_obj.set_alt_level(self.terminal_evasion_altitude)
                    except Exception as e:
                        print(f"设置紧急规避状态时出错: {e}")
                    self.agent_message_text(text=f"{unit_info['name']} 正在【紧急规避】！")
                
                else:
                    evasion_course = self._calculate_drag_course(unit_info, imminent_threat)
                    try:
                        fighter_obj.set_desired_speed(self.drag_speed)
                        fighter_obj.set_alt_level(self.drag_evasion_altitude)
                    except Exception as e:
                        print(f"设置拖拽状态时出错: {e}")
                    self.agent_message_text(text=f"{unit_info['name']} 正在【拖拽】导弹！")

                fighter_obj.plotted_course(evasion_course)
                
                if guid in self.fighter_tasks:
                    target_to_free = self.fighter_tasks.pop(guid)
                    if target_to_free in self.target_assignment_counts:
                        self.target_assignment_counts[target_to_free] -= 1
                continue

            # --- 优先级 2: 进攻/巡航 (非规避状态) ---
            else:
                fighter_obj.doctrine_weapon_control_status_air(WeaponControlStatus.Free)
                fighter_obj.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.Yes)
                fighter_obj.switch_radar(True,) 
                fighter_obj.attack_drop_target_all()

                try:
                    fighter_obj.set_desired_speed(self.cruise_speed)
                    fighter_obj.set_alt_level(self.cruise_altitude)
                except Exception as e:
                    pass 

                current_target_guid = self.fighter_tasks.get(guid)
                
                if not current_target_guid:
                    best_target = self._find_best_target_by_value(fighter_obj, unit_info, contacts) 
                    if best_target:
                        target_guid = best_target['guid']
                        
                        self.fighter_tasks[guid] = target_guid
                        self.target_assignment_counts[target_guid] = self.target_assignment_counts.get(target_guid, 0) + 1
                        
                        fighter_obj.attack_auto(target_guid) 
                        fighter_obj.doctrine_switch_radar(True)
                        
                        # --- 输出锁定的目标信息 ---
                        self.agent_message_text(text=f"[WTA] {unit_info['name']} 正在锁定 {best_target['Name']}！")
                        
                else:
                    pass 

    # --- 辅助函数 ---
    
    def _cleanup_assignments(self, units, contacts):
        tasks_to_remove = []
        for fighter_guid, target_guid in self.fighter_tasks.items():
            if fighter_guid not in units or target_guid not in contacts:
                tasks_to_remove.append(fighter_guid)
        
        for fighter_guid in tasks_to_remove:
            target_guid = self.fighter_tasks.pop(fighter_guid, None)
            if target_guid:
                if target_guid in self.target_assignment_counts:
                    self.target_assignment_counts[target_guid] -= 1
                    if self.target_assignment_counts[target_guid] <= 0:
                        self.target_assignment_counts.pop(target_guid)

    def _find_imminent_threat(self, unit_info, contacts):
        """
        使用距离和航向角判断威胁
        """
        aircraft_pos = (unit_info['lat'], unit_info['lon'])
        closest_threat = None
        notch_ward = 1
        min_dist = float('inf')

        for guid, contact in contacts.items():
            if not isinstance(contact, dict) or contact.get('Type') != 1: 
                continue
            
            missile_pos = (contact['Lat'], contact['Lon'])
            dist_km = geo.get_horizontal_distance(aircraft_pos, missile_pos)
            
            if dist_km <= 100: # 100km内的导弹
                missile_heading = contact.get('CurrentHeading')
                if missile_heading is None: 
                    continue 
                
                bearing_to_aircraft = geo.get_azimuth(missile_pos, aircraft_pos)
                angle_diff = abs(bearing_to_aircraft - missile_heading)
                notch_ward = 1 if bearing_to_aircraft - missile_heading > 0 else -1
                angle_diff = min(angle_diff, 360 - angle_diff) # 处理环绕
                
                if angle_diff <= 20: # 40度威胁锥角
                    if dist_km < min_dist:
                        min_dist = dist_km
                        closest_threat = contact
        
        return closest_threat , notch_ward # 返回最近的那个真实威胁

    def _calculate_drag_course(self, unit_info, threat_info):
        aircraft_pos = (unit_info['lat'], unit_info['lon'])
        missile_pos = (threat_info['Lat'], threat_info['Lon'])
        bearing_missile_to_aircraft = geo.get_azimuth(missile_pos, aircraft_pos)
        evasion_heading = bearing_missile_to_aircraft
        evasion_point = geo.get_geopoint_from_distance(aircraft_pos, evasion_heading, 30)
        return [evasion_point]

    def _calculate_notch_course(self, unit_info, threat_info, notch_ward):
        aircraft_pos = (unit_info['lat'], unit_info['lon'])
        missile_pos = (threat_info['Lat'], threat_info['Lon'])
        bearing_missile_to_aircraft = geo.get_azimuth(missile_pos, aircraft_pos)
        evasion_heading = (bearing_missile_to_aircraft + notch_ward * 90) % 360
        evasion_point = geo.get_geopoint_from_distance(aircraft_pos, evasion_heading, 30)
        return [evasion_point]

    def _find_best_target_by_value(self, fighter_obj, fighter_info, contacts):
        """
        查找200km内，“战术价值最高”且“攻击者未满”的敌方飞机。
        """
        weapon_id, _ = self._get_best_weapon_id(fighter_obj)
        if not weapon_id:
            return None 
            
        available_targets = []
        fighter_pos = (fighter_info['lat'], fighter_info['lon']) 

        for guid, contact in contacts.items():
            if isinstance(contact, dict) and contact.get('Type') == 0:
                contact_pos = (contact['Lat'], contact['Lon'])
                dist_km = geo.get_horizontal_distance(fighter_pos, contact_pos)
                
                if dist_km > self.engagement_range_km:
                    continue

                current_attackers = self.target_assignment_counts.get(guid, 0)
                if current_attackers < self.max_attackers_per_target:
                    contact['guid'] = guid
                    available_targets.append(contact)
        
        if not available_targets:
            return None 

        targets_formatted = [self._format_target_for_threat(t) for t in available_targets]
        self_unit_formatted = self._format_unit_for_threat(fighter_info)
        
        threat_vector = self.threat_evaluator.threat_matrix(targets_formatted, [self_unit_formatted]).flatten()
        pk_vector = self._calculate_pk_for_plane(fighter_obj, weapon_id, available_targets)
        
        result_vector = threat_vector + pk_vector
        
        best_target = None
        best_score = self.wta_threshold

        for i in range(len(result_vector)):
            if result_vector[i] > best_score:
                best_score = result_vector[i]
                best_target = available_targets[i]
        
        return best_target

    def _get_best_weapon_id(self, fighter_obj):
        weapon_info = fighter_obj.get_weapon_info()
        for dbid in self.AIR_TO_AIR_MISSILE_DBIDs:
            if dbid in weapon_info and weapon_info[dbid] > 0:
                return dbid, weapon_info[dbid]
        return None, 0

    def _format_unit_for_threat(self, unit_info):
        return {
            'lon': unit_info['lon'], 'lat': unit_info['lat'], 'alt': unit_info['alt'],
            'speed': unit_info['speed'], 'head': unit_info['head'],
            'aircraft_type': unit_info.get('type') 
        }

    def _format_target_for_threat(self, contact_info):
        return {
            'lon': contact_info['Lon'], 'lat': contact_info['Lat'],
            'alt': contact_info.get('CurrentAltitude', 0.0),
            'speed': contact_info.get('CurrentSpeed', 0.0),
            'head': contact_info.get('CurrentHeading', 0.0),
            'aircraft_type': contact_info.get('ActType')
        }

    def _calculate_pk_for_plane(self, fighter_obj, weapon_id, targets_list):
        """
        
        """
        pk_vector = np.zeros(len(targets_list))
        
        self_unit_info = fighter_obj.get_summary_info()
        
        for i, target_contact in enumerate(targets_list):
            try:
                dist_nm = self.threat_evaluator.get_horizontal_distance(
                    self_unit_info['lon'], self_unit_info['lat'], 
                    target_contact['Lon'], target_contact['Lat']
                )
                pk = calculate_possibility(weapon_id, target_contact, 2, dist_nm)
                pk_vector[i] = pk
            except Exception as e:
                print(f"[警告] P(k) 计算失败 (WeaponID: {weapon_id}, Target: {target_contact.get('Name')}): {e}")
                pk_vector[i] = 0.0 
            
        return pk_vector