# -*- coding:utf-8 -*-
# Author: 退退退不掉队-王睿、王鹏扉

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
from engine.LingYi.entitys import geo  # 地理计算工具，用于距离计算等

class Agent(Player):
    def __init__(self, side_name, params):
        super(Agent, self).__init__(side_name)
        
        # --- 智能体参数配置 ---
        self.decision_cooldown = 10  # 决策冷却时间（秒），避免频繁决策
        self.permission_proximity_km = 10.0  # 加油权限开启的距离阈值（千米），飞机靠近到此范围开启加油
        self.refuel_speed = 450  # 加油速率（未在核心逻辑中直接使用，预留参数）

        # --- 解析飞机数据，同时保存最大燃油量和分值 ---
        self.aircraft_max_fuel = {}  # 存储飞机dbid到最大燃油量的映射
        self.aircraft_score = {}     # 存储飞机dbid到任务分值的映射（分值越高优先级可能越高）
        # 飞机数据字符串（蓝方），格式：dbid max_fuel score,dbid max_fuel score,...
        data_string = "1392 2000 80,1748 5960 30,4980 3160 30,5184 9375 40,2918 8935 75,3821 9375 40,3835 8375 40,4455 5960 30,5460 3160 30,3383 6105 30,4971 6530 30,5258 6530 30,4874 8900 40,4592 3595 40,4518 6145 75" # 346 3840 30,
        # 红方 "2232 10200 40,3913 5000 30,4958 11500 30,4959 9420 30,3698 2405 30,5214 4990 30"
        try:
            groups = data_string.split(',')  # 按逗号分割不同飞机的数据
            for group in groups:
                parts = group.split()        # 按空格分割dbid、max_fuel、score
                if len(parts) >= 3: 
                    dbid = int(parts[0])
                    max_fuel = float(parts[1])
                    score = float(parts[2])
                    self.aircraft_max_fuel[dbid] = max_fuel
                    self.aircraft_score[dbid] = score if score > 0 else 1.0  # 确保分值不为0
        except Exception as e:
            print(f"[错误] 解析飞机数据时出错: {e}")

        # 定义飞机类型的dbid集合
        self.FIGHTER_DBIDs = set(self.aircraft_max_fuel.keys())  # 战斗机dbid集合（从解析数据中获取）
        self.TANKER_DBIDs = {4554, 4513, 808, 3687, 1795, 4517}  # 加油机dbid集合（蓝方）
        # 蓝方 {2686,4440,2382,220}
        self.AMMO_DBIDs = {5299, 19951}  # 弹药dbid集合（用于判断飞机是否有弹药）

        # --- 状态追踪变量 ---
        self.busy_tankers = {}  # 记录忙碌的加油机：{tanker_guid: mission_name}
        self.refueling_jobs = {}  # 记录加油任务详情：{fighter_guid: {任务信息}}
        self.planes_forced_to_rtb = set()  # 记录被强制返航的飞机guid
        self.last_decision_time = -self.decision_cooldown  # 上次决策时间（初始值确保首次可决策）

    def initial(self, situation):
        """初始化方法：启动时设置默认加油权限"""
        print("--- 动态空中加油智能体已启动，正在设置默认权限... ---")
        # 遍历所有单位，为加油机开启加油权限，战斗机关闭
        for guid, unit in situation[0].items():
            if unit.get('category') != 'Aircraft':  # 只处理飞行器
                continue
            try:
                plane_obj = self.get_unit(guid)  # 获取单位对象
                if not plane_obj:
                    continue
                # 判断单位类型，设置加油权限
                if unit.get('dbid') in self.TANKER_DBIDs:
                    plane_obj.doctrine_refuel(ERefuel.Yes)  # 加油机开启加油权限
                elif unit.get('dbid') in self.FIGHTER_DBIDs:
                    plane_obj.doctrine_refuel(ERefuel.No)   # 战斗机默认关闭加油权限
            except (AttributeError, NameError):
                pass  # 忽略属性错误（如对象无doctrine_refuel方法）

    def step(self, time_elapse, situation):
        """主循环方法：按冷却时间间隔执行决策逻辑"""
        # 检查是否到达决策时间（避免高频决策）
        if (time_elapse - self.last_decision_time) < self.decision_cooldown:
            return
        self.last_decision_time = time_elapse  # 更新上次决策时间
        
        units, contacts = situation[0], situation[1]  # 解析当前态势：单位信息、接触信息

        # 处理燃油紧急情况（<20%强制返航）
        self._handle_fuel_emergencies(units)
        # 监控并管理当前加油任务（油满后结束任务）
        self._monitor_and_manage_jobs(units)
        # 查找可用的加油机和需要加油的战斗机
        available_tankers = self._find_available_tankers(units)
        needy_fighters = self._find_needy_fighters(units)

        # 若没有需要加油的战斗机或无可用加油机，则退出
        if not needy_fighters or not available_tankers:
            return 

        # 按优先级排序（分数越低越优先）
        needy_fighters.sort(key=lambda f: f['priority_score'])

        # 为每个战斗机匹配最佳加油机
        for fighter in needy_fighters:
            if not available_tankers:  # 无可用加油机时退出
                break 
            
            # 为当前战斗机找到最近的可用加油机
            best_tanker = self._find_best_tanker_for_fighter(fighter, available_tankers)
            
            if best_tanker:
                # 创建并分配加油任务
                self._create_and_assign_refuel_mission(fighter, best_tanker)
                available_tankers.remove(best_tanker)  # 标记加油机为忙碌


    def _handle_fuel_emergencies(self, units):
        """处理燃油紧急情况：燃油低于20%的飞机强制返航并设为中速"""
        # 过滤出仍活跃的强制返航飞机（移除已消失的单位）
        active_guids = set(units.keys())
        self.planes_forced_to_rtb.intersection_update(active_guids)
        
        for guid, unit_info in units.items():
            dbid = unit_info.get('dbid')
            max_fuel = self.aircraft_max_fuel.get(dbid)
            if not max_fuel:  # 未配置最大燃油的飞机不处理
                continue 
            if unit_info.get('alt', 0) <= 100:  # 高度过低（可能已着陆）不处理
                continue
            # 正在加油或已强制返航的飞机不重复处理
            if guid in self.refueling_jobs or guid in self.planes_forced_to_rtb:
                continue 
            
            # 计算20%最大燃油的紧急返航阈值
            rtb_threshold = max_fuel * 0.20
            fighter_obj = self.get_unit(guid)
            if not fighter_obj:
                continue
            
            current_fuel = fighter_obj.get_fuel_capacity()  # 获取当前燃油量
            if current_fuel < rtb_threshold:  # 燃油低于阈值，执行紧急处理
                try:
                    # 设置为中速巡航（Loiter）和最大高度
                    fighter_obj.set_throttle(Throttle.Loiter)
                    fighter_obj.set_alt_level(AltitudeLevel.MAX)
                except AttributeError:
                    pass
                self.unit_return_to_base(guid)  # 命令返航
                self.agent_message_text(text=f"[紧急返航] {unit_info['name']} 油量低于20%，已命令其返航！")
                self.planes_forced_to_rtb.add(guid)  # 记录为已强制返航

    def _monitor_and_manage_jobs(self, units):
        """监控当前加油任务：油满（>80%）后结束任务，恢复原任务并关闭加油权限"""
        jobs_to_remove = []  # 待移除的加油任务
        tankers_to_free = []  # 待释放的加油机

        # 遍历所有加油任务
        for fighter_guid, job_details in self.refueling_jobs.items():
            fighter_obj = self.get_unit(fighter_guid)
            tanker_guid = job_details.get("tanker_guid")
            tanker_info = units.get(tanker_guid)  # 获取加油机当前信息
            
            # 若战斗机或加油机不存在，终止任务
            if not fighter_obj or not tanker_info:
                jobs_to_remove.append(fighter_guid)
                if tanker_guid:
                    tankers_to_free.append(tanker_guid)
                self.delete_mission(job_details["refuel_mission"])  # 删除加油任务
                continue
            
            # 检查战斗机燃油是否达标（>80%最大燃油）
            dbid = units.get(fighter_guid, {}).get('dbid')
            max_fuel = self.aircraft_max_fuel.get(dbid)
            if not max_fuel:
                continue 
            high_threshold = max_fuel * 0.80  # 80%最大燃油为结束加油阈值
            current_fuel = fighter_obj.get_fuel_capacity()
            
            if current_fuel >= high_threshold:  # 燃油已充足，结束加油
                try:
                    fighter_obj.doctrine_refuel(ERefuel.No)  # 关闭战斗机加油权限
                except (AttributeError, NameError):
                    pass
                # 恢复战斗机原任务
                if job_details["original_mission"]:
                    self.assign_units_to_mission([fighter_guid], job_details["original_mission"])
                # 恢复加油机原任务
                if job_details.get("tanker_original_mission"):
                    self.assign_units_to_mission([tanker_guid], job_details["tanker_original_mission"])
                self.delete_mission(job_details["refuel_mission"])  # 删除加油任务
                jobs_to_remove.append(fighter_guid)
                tankers_to_free.append(tanker_guid)
            
            # 若未开启加油权限，检查是否已靠近加油点
            elif not job_details.get("permission_granted", False):
                fighter_info = units.get(fighter_guid)
                if not fighter_info:
                    continue
                # 计算战斗机与加油机的水平距离
                dist = geo.get_horizontal_distance(
                    (fighter_info['lat'], fighter_info['lon']), 
                    (tanker_info['lat'], tanker_info['lon'])
                )
                # 距离小于阈值，开启加油权限
                if dist <= self.permission_proximity_km:
                    try:
                        fighter_obj.doctrine_refuel(ERefuel.Yes) 
                        self.refueling_jobs[fighter_guid]["permission_granted"] = True
                        self.agent_message_text(text=f"[加油权限] {fighter_obj.Name} 已抵达加油点，【开启】权限。")
                    except (AttributeError, NameError):
                        pass
        
        # 清理已结束的任务和忙碌状态
        for guid in jobs_to_remove:
            self.refueling_jobs.pop(guid, None)
        for guid in tankers_to_free:
            self.busy_tankers.pop(guid, None)

    def _find_available_tankers(self, units):
        """查找可用的加油机：处于空中、未忙碌的加油机"""
        # 过滤出仍活跃的忙碌加油机（移除已消失的单位）
        active_guids = set(units.keys())
        self.busy_tankers = {guid: mission for guid, mission in self.busy_tankers.items() if guid in active_guids}
        
        available_tankers = []
        for guid, unit_info in units.items():
            # 检查是否为加油机、是否在空中（高度>100）、是否未忙碌
            is_tanker = unit_info.get('dbid') in self.TANKER_DBIDs
            is_in_air = unit_info.get('alt', 0) > 100
            is_available = guid not in self.busy_tankers
            
            if is_tanker and is_in_air and is_available:
                available_tankers.append({
                    'guid': guid,
                    'name': unit_info.get('name'),
                    'lat': unit_info.get('lat'),  # 纬度
                    'lon': unit_info.get('lon'),  # 经度
                    'original_mission': unit_info.get('mission')  # 原任务（用于后续恢复）
                })
        return available_tankers

    def _find_needy_fighters(self, units):
        """查找需要加油的战斗机：燃油在20%-35%之间、在空中、未在加油/返航中"""
        needy_fighters = []
        active_guids = set(units.keys())
        # 过滤出仍活跃的加油任务（移除已消失的单位）
        self.refueling_jobs = {guid: job for guid, job in self.refueling_jobs.items() if guid in active_guids}

        for guid, unit_info in units.items():
            dbid = unit_info.get('dbid')
            # 检查是否为战斗机、是否在空中
            is_fighter = dbid in self.FIGHTER_DBIDs
            is_in_air = unit_info.get('alt', 0) > 100
            
            # 排除正在加油或已被强制返航的飞机
            if is_fighter and is_in_air and guid not in self.refueling_jobs and guid not in self.planes_forced_to_rtb:
                fighter_obj = self.get_unit(guid)
                if not fighter_obj:
                    continue
                
                max_fuel = self.aircraft_max_fuel[dbid]
                low_threshold = max_fuel * 0.35  # 35%最大燃油为需要加油的阈值
                rtb_threshold = max_fuel * 0.20   # 20%为紧急返航阈值
                
                fuel_capacity = fighter_obj.get_fuel_capacity()  # 当前燃油量
                
                # 燃油在[20%, 35%)之间，需要加油
                if rtb_threshold <= fuel_capacity < low_threshold:
                    # 检查是否有弹药（影响优先级）
                    weapon_info = fighter_obj.get_weapon_info()
                    has_ammo = any(dbid in self.AMMO_DBIDs for dbid in weapon_info.keys() if weapon_info[dbid] > 0)
                    
                    # 计算加油优先级
                    priority_score = self._calculate_refuel_priority(fuel_capacity, has_ammo, dbid)
                    
                    needy_fighters.append({
                        'guid': guid,
                        'name': unit_info.get('name'),
                        'lat': unit_info.get('lat'),
                        'lon': unit_info.get('lon'),
                        'priority_score': priority_score,  # 优先级分数（低优先）
                        'original_mission': unit_info.get('mission')  # 原任务（用于后续恢复）
                    })
        return needy_fighters

    def _calculate_refuel_priority(self, fuel_amount, has_ammo, dbid):
        """
        计算加油优先级分数（分数越低越优先）
        逻辑：有弹药的飞机优先，同有弹药时，分值高的飞机优先（燃油/分值 越小越优先）
        """
        if has_ammo:
            score = self.aircraft_score.get(dbid, 1.0)  # 获取飞机任务分值
            return fuel_amount / score  # 燃油越少、分值越高，分数越低（优先级越高）
        else:
            # 无弹药的飞机优先级低（加一个大基数）
            return 100000 + fuel_amount 

    def _find_best_tanker_for_fighter(self, fighter, available_tankers):
        """为战斗机找到最近的可用加油机（基于水平距离）"""
        best_tanker = None
        min_dist = float('inf')  # 初始化为无穷大
        for tanker in available_tankers:
            # 计算战斗机与加油机的水平距离
            dist = geo.get_horizontal_distance(
                (fighter['lat'], fighter['lon']), 
                (tanker['lat'], tanker['lon'])
            )
            if dist < min_dist:  # 更新最近的加油机
                min_dist = dist
                best_tanker = tanker
        return best_tanker

    def _create_and_assign_refuel_mission(self, fighter, tanker):
        """创建加油任务并分配给战斗机和加油机"""
        fighter_obj = self.get_unit(fighter['guid'])
        tanker_obj = self.get_unit(tanker['guid'])
        if not fighter_obj or not tanker_obj:  # 单位不存在则退出
            return
        
        try:
            fighter_obj.doctrine_refuel(ERefuel.Yes)  # 预先开启战斗机加油权限
        except (AttributeError, NameError):
            pass
        
        try:
            # 设置战斗机为中速巡航、最大高度（便于加油）
            fighter_obj.set_throttle(Throttle.Loiter)
            fighter_obj.set_alt_level(AltitudeLevel.MAX) 
        except AttributeError:
            pass
        
        # 计算加油点：战斗机与加油机当前位置的中点
        refuel_point = ((tanker['lat'] + fighter['lat'])/2, (tanker['lon'] + fighter['lon'])/2)
        # 生成唯一任务名称（包含加油机guid后6位和时间戳）
        mission_name = f"refuel_task_{tanker['guid'][-6:]}_{int(self.last_decision_time)}"
        # 创建支持任务（加油任务）
        support_mission = self.create_support_mission(mission_name, [refuel_point])
        
        if support_mission:
            # 配置加油任务参数
            support_mission.support_flightSize(FlightSize.One)  # 单机任务
            support_mission.set_one_third_rule(False)  # 关闭1/3规则（无需保留油量）
            support_mission.support_tanker_one_time(False)  # 允许多次加油（单次任务内）
            support_mission.support_loopType(False)  # 非循环任务（完成后结束）
            
            # 分配加油机和战斗机到加油任务
            self.assign_units_to_mission([tanker['guid']], mission_name)
            self.assign_units_to_mission([fighter['guid']], mission_name)
            
            # 更新状态变量：标记加油机忙碌，记录加油任务详情
            self.busy_tankers[tanker['guid']] = mission_name
            self.refueling_jobs[fighter['guid']] = {
                "original_mission": fighter['original_mission'],  # 战斗机原任务
                "refuel_mission": support_mission.ID,  # 加油任务ID
                "tanker_guid": tanker['guid'],  # 对应的加油机guid
                "tanker_original_mission": tanker['original_mission'],  # 加油机原任务
                "permission_granted": False  # 加油权限是否已开启（初始未开启）
            }
            self.agent_message_text(text=f"[加油任务] 已指派 {tanker['name']} 为 {fighter['name']} 加油。")