# -*- coding:utf-8 -*-

"""
动态空中加油智能体
战术目标：
1. 解析飞机数据(油量/分值)，为加油机开启加油权限并关闭所有飞机的加油权限。
2. 监控所有飞机，油量 < 20% 则强制返航并设为中速。
3. 监控飞机，油量 < 35% 时，根据燃油和分值计算优先级，为其动态匹配加油机。
4. 设置飞机与加油机中点为目标加油点，检测到飞机靠近后开启加油权限。
5. 飞机燃油 > 80% 后结束加油任务，飞机与加油机返回原任务。
"""

from engine.LingYi.entitys.player import Player
from engine.LingYi.entitys.global_util import *
from engine.LingYi.entitys import geo 

class Agent(Player):
    def __init__(self, side_name, params):
        super(Agent, self).__init__(side_name)
        
        # --- 智能体参数配置 ---
        self.decision_cooldown = 10 
        self.permission_proximity_km = 10.0 
        self.refuel_speed = 450 

        # ---解析飞机数据，同时保存 MaxFuel 和 Score ---
        self.aircraft_max_fuel = {}
        self.aircraft_score = {} 
        data_string = "2232 10200 40,3913 5000 30,4958 11500 30,4959 9420 30,3698 2405 30,5214 4990 30"
        #Blue:1392 2000 80,1748 5960 30,4980 3160 30,5184 9375 40,2918 8935 75,3821 9375 40,3835 8375 40,4455 5960 30,5460 3160 30,346 3840 30,3383 6105 30,4971 6530 30,5258 6530 30,4874 8900 40,4592 3595 40,4518 6145 75
        #此处数据对应位 dbid max_fuel score;
        try:
            groups = data_string.split(',')
            for group in groups:
                parts = group.split()
                if len(parts) >= 3: 
                    dbid = int(parts[0])
                    max_fuel = float(parts[1])
                    score = float(parts[2])
                    self.aircraft_max_fuel[dbid] = max_fuel
                    self.aircraft_score[dbid] = score if score > 0 else 1.0 
        except Exception as e:
            print(f"[错误] 解析飞机数据时出错: {e}")

        self.FIGHTER_DBIDs = set(self.aircraft_max_fuel.keys()) 
        self.TANKER_DBIDs = {2686,4440,2382,220}
        #Blue:4554,4513,808,3687,1795,4517
        self.AMMO_DBIDs = {5299, 19951}

        # --- 状态追踪 ---
        self.busy_tankers = {} 
        self.refueling_jobs = {}
        self.planes_forced_to_rtb = set()
        self.last_decision_time = -self.decision_cooldown

    def initial(self, situation):

        print("--- 动态空中加油智能体已启动，正在设置默认权限... ---")
        for guid, unit in situation[0].items():
            if unit.get('category') != 'Aircraft':
                continue
            try:
                plane_obj = self.get_unit(guid)
                if not plane_obj:
                    continue
                if unit.get('dbid') in self.TANKER_DBIDs:
                    plane_obj.doctrine_refuel(ERefuel.Yes)
                elif unit.get('dbid') in self.FIGHTER_DBIDs:
                    plane_obj.doctrine_refuel(ERefuel.No)
            except (AttributeError, NameError):
                pass 

    def step(self, time_elapse, situation):

        if (time_elapse - self.last_decision_time) < self.decision_cooldown:
            return
        self.last_decision_time = time_elapse
        
        units, contacts = situation[0], situation[1]

        self._handle_fuel_emergencies(units)
        self._monitor_and_manage_jobs(units)
        available_tankers = self._find_available_tankers(units)
        needy_fighters = self._find_needy_fighters(units)

        if not needy_fighters or not available_tankers:
            return 

        needy_fighters.sort(key=lambda f: f['priority_score'])

        for fighter in needy_fighters:
            if not available_tankers:
                break 
            
            best_tanker = self._find_best_tanker_for_fighter(fighter, available_tankers)
            
            if best_tanker:
                self._create_and_assign_refuel_mission(fighter, best_tanker)
                available_tankers.remove(best_tanker)



    def _handle_fuel_emergencies(self, units):
        """
        强制燃油低于20%的飞机返航并设置为中速
        """
        active_guids = set(units.keys())
        self.planes_forced_to_rtb.intersection_update(active_guids)
        for guid, unit_info in units.items():
            dbid = unit_info.get('dbid')
            max_fuel = self.aircraft_max_fuel.get(dbid)
            if not max_fuel: continue 
            if unit_info.get('alt', 0) <= 100: continue
            if guid in self.refueling_jobs or guid in self.planes_forced_to_rtb:
                continue 
            rtb_threshold = max_fuel * 0.20
            fighter_obj = self.get_unit(guid)
            if not fighter_obj: continue
            current_fuel = fighter_obj.get_fuel_capacity()
            if current_fuel < rtb_threshold:
                try:
                    fighter_obj.set_throttle(Throttle.Loiter)
                    fighter_obj.set_alt_level(AltitudeLevel.MAX)
                except AttributeError: pass
                self.unit_return_to_base(guid)
                self.agent_message_text(text=f"[紧急返航] {unit_info['name']} 油量低于20%，已命令其返航！")
                self.planes_forced_to_rtb.add(guid)

    def _monitor_and_manage_jobs(self, units):
        """
        监控加油中的飞机，油满(80%)后关闭权限并恢复双方的原任务。
        """
        jobs_to_remove = []
        tankers_to_free = []
        for fighter_guid, job_details in self.refueling_jobs.items():
            fighter_obj = self.get_unit(fighter_guid)
            tanker_guid = job_details.get("tanker_guid")
            tanker_info = units.get(tanker_guid)
            if not fighter_obj or not tanker_info:
                jobs_to_remove.append(fighter_guid)
                if tanker_guid: tankers_to_free.append(tanker_guid)
                self.delete_mission(job_details["refuel_mission"])
                continue
            dbid = units.get(fighter_guid, {}).get('dbid')
            max_fuel = self.aircraft_max_fuel.get(dbid)
            if not max_fuel: continue 
            high_threshold = max_fuel * 0.80
            current_fuel = fighter_obj.get_fuel_capacity()
            if current_fuel >= high_threshold:
                try:
                    fighter_obj.doctrine_refuel(ERefuel.No)
                except (AttributeError, NameError): pass
                if job_details["original_mission"]:
                    self.assign_units_to_mission([fighter_guid], job_details["original_mission"])
                if job_details.get("tanker_original_mission"):
                    self.assign_units_to_mission([tanker_guid], job_details["tanker_original_mission"])
                self.delete_mission(job_details["refuel_mission"])
                jobs_to_remove.append(fighter_guid)
                tankers_to_free.append(tanker_guid)
            elif not job_details.get("permission_granted", False):
                fighter_info = units.get(fighter_guid)
                if not fighter_info: continue
                dist = geo.get_horizontal_distance((fighter_info['lat'], fighter_info['lon']), (tanker_info['lat'], tanker_info['lon']))
                if dist <= self.permission_proximity_km:
                    try:
                        fighter_obj.doctrine_refuel(ERefuel.Yes) 
                        self.refueling_jobs[fighter_guid]["permission_granted"] = True
                        self.agent_message_text(text=f"[加油权限] {fighter_obj.Name} 已抵达加油点，【开启】权限。")
                    except (AttributeError, NameError): pass
        for guid in jobs_to_remove:
            self.refueling_jobs.pop(guid, None)
        for guid in tankers_to_free:
            self.busy_tankers.pop(guid, None)

    def _find_available_tankers(self, units):
    
        active_guids = set(units.keys())
        self.busy_tankers = {guid: mission for guid, mission in self.busy_tankers.items() if guid in active_guids}
        available_tankers = []
        for guid, unit_info in units.items():
            is_tanker = unit_info.get('dbid') in self.TANKER_DBIDs
            is_in_air = unit_info.get('alt', 0) > 100
            is_available = guid not in self.busy_tankers
            if is_tanker and is_in_air and is_available:
                available_tankers.append({
                    'guid': guid,
                    'name': unit_info.get('name'),
                    'lat': unit_info.get('lat'),
                    'lon': unit_info.get('lon'),
                    'original_mission': unit_info.get('mission')
                })
        return available_tankers

    def _find_needy_fighters(self, units):
        """
        查找油量在 20% 到 35% 之间、且【附近有加油机】的飞机。
        """
        needy_fighters = []
        active_guids = set(units.keys())
        self.refueling_jobs = {guid: job for guid, job in self.refueling_jobs.items() if guid in active_guids}

        for guid, unit_info in units.items():
            dbid = unit_info.get('dbid')
            is_fighter = dbid in self.FIGHTER_DBIDs
            is_in_air = unit_info.get('alt', 0) > 100
            
            if is_fighter and is_in_air and guid not in self.refueling_jobs and guid not in self.planes_forced_to_rtb:
                fighter_obj = self.get_unit(guid)
                if not fighter_obj:
                    continue
                
                max_fuel = self.aircraft_max_fuel[dbid]
                low_threshold = max_fuel * 0.35
                rtb_threshold = max_fuel * 0.20
                
                fuel_capacity = fighter_obj.get_fuel_capacity()
                
                if rtb_threshold <= fuel_capacity < low_threshold:
                    weapon_info = fighter_obj.get_weapon_info()
                    has_ammo = any(dbid in self.AMMO_DBIDs for dbid in weapon_info.keys() if weapon_info[dbid] > 0)
                    
                    priority_score = self._calculate_refuel_priority(fuel_capacity, has_ammo, dbid)
                    
                    needy_fighters.append({
                        'guid': guid,
                        'name': unit_info.get('name'),
                        'lat': unit_info.get('lat'),
                        'lon': unit_info.get('lon'),
                        'priority_score': priority_score,
                        'original_mission': unit_info.get('mission') 
                    })
        return needy_fighters

    def _calculate_refuel_priority(self, fuel_amount, has_ammo, dbid):
        """
        计算加油优先级分数，分数越低越优先。
        优先服务有弹药的飞机，在有弹药的飞机中，优先服务分值高的。
        """
        if has_ammo:
            score = self.aircraft_score.get(dbid, 1.0)            
            return fuel_amount / score
        else:
            return 100000 + fuel_amount 

    def _find_best_tanker_for_fighter(self, fighter, available_tankers):
        
        best_tanker = None
        min_dist = float('inf')
        for tanker in available_tankers:
            dist = geo.get_horizontal_distance((fighter['lat'], fighter['lon']), (tanker['lat'], tanker['lon']))
            if dist < min_dist:
                min_dist = dist
                best_tanker = tanker
        return best_tanker

    def _create_and_assign_refuel_mission(self, fighter, tanker):

        fighter_obj = self.get_unit(fighter['guid'])
        tanker_obj = self.get_unit(tanker['guid'])
        if not fighter_obj or not tanker_obj:
            return
        try:
            fighter_obj.doctrine_refuel(ERefuel.Yes) 
        except (AttributeError, NameError): pass
        try:
            fighter_obj.set_throttle(Throttle.Loiter)
            fighter_obj.set_alt_level(AltitudeLevel.MAX) 
        except AttributeError: pass
        refuel_point = ((tanker['lat'] + fighter['lat'])/2, (tanker['lon'] + fighter['lon'])/2)
        mission_name = f"refuel_task_{tanker['guid'][-6:]}_{int(self.last_decision_time)}"
        support_mission = self.create_support_mission(mission_name, [refuel_point])
        if support_mission:
            support_mission.support_flightSize(FlightSize.One)
            support_mission.set_one_third_rule(False)
            support_mission.support_tanker_one_time(False) 
            support_mission.support_loopType(False)
            self.assign_units_to_mission([tanker['guid']], mission_name)
            self.assign_units_to_mission([fighter['guid']], mission_name)
            self.busy_tankers[tanker['guid']] = mission_name
            self.refueling_jobs[fighter['guid']] = {
                "original_mission": fighter['original_mission'], 
                "refuel_mission": support_mission.ID,
                "tanker_guid": tanker['guid'],
                "tanker_original_mission": tanker['original_mission'],
                "permission_granted": False 
            }
            self.agent_message_text(text=f"[加油任务] 已指派 {tanker['name']} 为 {fighter['name']} 加油。")