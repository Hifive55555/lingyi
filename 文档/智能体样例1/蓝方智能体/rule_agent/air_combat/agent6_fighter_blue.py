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

from calculate_threat_level_of_the_target import ThreatEvaluator  # 目标威胁等级评估工具
from calculate_weapon_attack_air_rate import calculate_possibility  # 武器攻击概率计算工具


class Agent(Player):
    """战斗机智能体核心类，继承自Player基类，实现自主决策逻辑"""
    
    def __init__(self, side_name, params):
        """初始化智能体属性
        
        Args:
            side_name: 阵营名称
            params: 初始化参数
        """
        super(Agent, self).__init__(side_name)
        
        self.decision_cooldown = 0  # 决策冷却时间（避免频繁决策）
        # 战斗机数据库ID集合（用于识别己方战斗机单位）：蓝方
        self.FIGHTER_DBIDs = {4455, 5460, 346, 1795, 2164, 2936, 3383, 4517, 1392, 1748, 2582, 3599, 4513, 4955, 4980, 5184, 290, 318, 320, 541, 808, 2918, 3687, 3821, 3835, 4325, 4860, 5449}
        # 红方 {2346,1342,2734,4958,4959,3963,2232,3913,5214,1336,2293,2382,2636,3461,4289,4440,4607,4728,5554}

        
        # 空空导弹数据库ID集合（用于识别可用武器）：蓝方
        self.AIR_TO_AIR_MISSILE_DBIDs = {718, 1384, 718, 945, 1691, 1400, 1756, 1199, 897, 945, 183, 1052, 446, 1129, 961, 3828, 3567, 2780, 3567}
        # 红方 {152,1897,1896,2002,1800,1796,2053,2056,2556,352,1896,3128,915,3126,1129,961}


        self.evasion_speed = 9999  # 紧急规避时的速度
        self.drag_speed = 9999     # 拖拽导弹时的速度
        self.cruise_speed = 'OFF'  # 巡航速度模式
        
        self.terminal_evasion_altitude = 'MIN'  # 紧急规避时的高度（最低）
        self.drag_evasion_altitude = 'OFF'      # 拖拽导弹时的高度模式
        self.cruise_altitude = 'OFF'            # 巡航高度模式

        self.last_decision_time = -self.decision_cooldown  # 上次决策时间（初始化为负冷却值，确保首次可决策）
        
        self.fighter_tasks = {}  # 战斗机-目标分配字典 {战斗机GUID: 目标GUID}
        self.target_assignment_counts = {}  # 目标被分配的攻击者数量 {目标GUID: 数量}
        self.max_attackers_per_target = 2  # 每个目标的最大攻击者数量（避免过度分配）

        self.threat_evaluator = ThreatEvaluator()  # 威胁评估器实例
        self.wta_threshold = 0.2  # 武器目标分配（WTA）的最低分数阈值
        
        self.engagement_range_km = 200.0  # 交战范围（200公里内的目标才考虑攻击）

    def initial(self, situation):
        """初始化场景时的设置
        
        Args:
            situation: 初始场景信息，包含单位和接触目标数据
        """
        self.agent_message_text(text='[DEBUG] 战斗机WTA智能体(V11.3)已启动。')
        
        # 遍历所有单位，对己方战斗机设置初始准则
        for guid, unit in situation[0].items():
            if unit.get('dbid') in self.FIGHTER_DBIDs:
                plane_obj = self.get_unit(guid)  # 获取战斗机实体对象
                if plane_obj:
                    # 设置战斗准则：攻击时不忽略规划航线
                    plane_obj.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.No)
                    # 设置武器控制状态：空中目标自由开火
                    plane_obj.doctrine_weapon_control_status_air(WeaponControlStatus.Free)
                    # 关闭自动规避（使用自定义规避逻辑）
                    plane_obj.doctrine_automatic_evasion(AutomaticEvasion.No)

    def step(self, time_elapse, situation):
        """每帧更新时的决策逻辑
        
        Args:
            time_elapse: 当前时间
            situation: 当前场景信息 (units, contacts)，分别为己方单位和接触到的目标
        """
        # 检查决策冷却，未到时间则跳过
        if (time_elapse - self.last_decision_time) < self.decision_cooldown:
            return
        self.last_decision_time = time_elapse  # 更新决策时间
        
        units, contacts = situation[0], situation[1]  # 解析单位和接触目标

        self._cleanup_assignments(units, contacts)  # 清理无效的任务分配（如目标或战斗机已消失）

        # 遍历所有单位，处理己方战斗机
        for guid, unit_info in units.items():
            # 过滤非战斗机单位或高度过低（<=100）的单位
            if unit_info.get('dbid') not in self.FIGHTER_DBIDs or unit_info.get('alt', 0) <= 100:
                continue
            
            fighter_obj = self.get_unit(guid)  # 获取战斗机实体
            if not fighter_obj:
                continue  # 实体不存在则跳过

            # --- 优先级 1: 生存 (规避导弹) ---
            # 查找紧迫的导弹威胁及规避方向
            imminent_threat, notch_ward = self._find_imminent_threat(unit_info, contacts)
            
            if imminent_threat:  # 存在紧迫威胁时，执行规避逻辑
                # 规避时武器保持（停止攻击）
                fighter_obj.doctrine_weapon_control_status_air(WeaponControlStatus.Hold)
                # 不忽略规划航线（优先执行规避航线）
                fighter_obj.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.No)
                # 不遵循EMCON（电子对抗）准则
                fighter_obj.EMCON_Obey_doctrine(False)
                # 关闭雷达（减少被探测概率）
                fighter_obj.switch_radar(False,) 
                
                # 计算战斗机与导弹的水平距离
                dist_km = geo.get_horizontal_distance(
                    (unit_info['lat'], unit_info['lon']), 
                    (imminent_threat['Lat'], imminent_threat['Lon'])
                )
                
                if dist_km <= 60.0:  # 导弹距离<=60km，执行紧急规避
                    evasion_course = self._calculate_notch_course(unit_info, imminent_threat, notch_ward)
                    try:
                        fighter_obj.set_desired_speed(self.evasion_speed)  # 设置紧急规避速度
                        fighter_obj.set_alt_level(self.terminal_evasion_altitude)  # 设置紧急规避高度
                    except Exception as e:
                        print(f"设置紧急规避状态时出错: {e}")
                    self.agent_message_text(text=f"{unit_info['name']} 正在【紧急规避】！")
                
                else:  # 导弹距离>60km，执行拖拽规避（引导导弹远离）
                    evasion_course = self._calculate_drag_course(unit_info, imminent_threat)
                    try:
                        fighter_obj.set_desired_speed(self.drag_speed)  # 设置拖拽速度
                        fighter_obj.set_alt_level(self.drag_evasion_altitude)  # 设置拖拽高度
                    except Exception as e:
                        print(f"设置拖拽状态时出错: {e}")
                    self.agent_message_text(text=f"{unit_info['name']} 正在【拖拽】导弹！")

                fighter_obj.plotted_course(evasion_course)  # 执行规避航线
                
                # 清除当前战斗机的攻击任务（规避优先）
                if guid in self.fighter_tasks:
                    target_to_free = self.fighter_tasks.pop(guid)
                    if target_to_free in self.target_assignment_counts:
                        self.target_assignment_counts[target_to_free] -= 1
                continue  # 完成规避逻辑，跳过后续攻击逻辑

            # --- 优先级 2: 进攻/巡航 (非规避状态) ---
            else:
                # 恢复武器自由开火状态
                fighter_obj.doctrine_weapon_control_status_air(WeaponControlStatus.Free)
                # 攻击时忽略规划航线（优先追击目标）
                fighter_obj.doctrine_ignore_plotted_course(IgnorePlottedCourseWhenAttacking.Yes)
                # 开启雷达（探测目标）
                fighter_obj.switch_radar(True,) 
                # 清除所有已锁定目标（重新规划攻击）
                fighter_obj.attack_drop_target_all()

                # 设置巡航状态的速度和高度
                try:
                    fighter_obj.set_desired_speed(self.cruise_speed)
                    fighter_obj.set_alt_level(self.cruise_altitude)
                except Exception as e:
                    pass  # 忽略设置失败的情况

                current_target_guid = self.fighter_tasks.get(guid)  # 获取当前战斗机的目标
                
                if not current_target_guid:  # 没有当前目标时，寻找最佳目标
                    best_target = self._find_best_target_by_value(fighter_obj, unit_info, contacts) 
                    if best_target:
                        target_guid = best_target['guid']
                        
                        # 记录任务分配
                        self.fighter_tasks[guid] = target_guid
                        self.target_assignment_counts[target_guid] = self.target_assignment_counts.get(target_guid, 0) + 1
                        
                        fighter_obj.attack_auto(target_guid)  # 自动攻击目标
                        fighter_obj.doctrine_switch_radar(True)  # 确保雷达开启
                        
                        # 输出锁定信息
                        self.agent_message_text(text=f"[WTA] {unit_info['name']} 正在锁定 {best_target['Name']}！")
                else:
                    pass  # 已有目标时不做处理（保持攻击）

    # --- 辅助函数 ---
    
    def _cleanup_assignments(self, units, contacts):
        """清理无效的任务分配（战斗机或目标已消失）
        
        Args:
            units: 当前己方单位字典
            contacts: 当前接触目标字典
        """
        tasks_to_remove = []
        # 遍历所有任务，检查战斗机和目标是否仍存在
        for fighter_guid, target_guid in self.fighter_tasks.items():
            if fighter_guid not in units or target_guid not in contacts:
                tasks_to_remove.append(fighter_guid)
        
        # 移除无效任务，并更新目标的攻击者计数
        for fighter_guid in tasks_to_remove:
            target_guid = self.fighter_tasks.pop(fighter_guid, None)
            if target_guid:
                if target_guid in self.target_assignment_counts:
                    self.target_assignment_counts[target_guid] -= 1
                    # 计数为0时移除该目标的记录
                    if self.target_assignment_counts[target_guid] <= 0:
                        self.target_assignment_counts.pop(target_guid)

    def _find_imminent_threat(self, unit_info, contacts):
        """查找对当前战斗机最紧迫的导弹威胁
        
        判定逻辑：100km内、航向角与目标方位角差<=20度（处于导弹攻击锥内）的导弹，取最近的一个
        
        Args:
            unit_info: 战斗机信息
            contacts: 接触到的目标字典（含导弹）
        
        Returns:
            closest_threat: 最紧迫的导弹威胁（字典），无则为None
            notch_ward: 规避方向（1或-1，用于计算规避航线）
        """
        aircraft_pos = (unit_info['lat'], unit_info['lon'])  # 战斗机位置（纬度，经度）
        closest_threat = None
        notch_ward = 1  # 默认规避方向
        min_dist = float('inf')  # 初始最小距离设为无穷大

        # 遍历所有接触目标，筛选导弹威胁
        for guid, contact in contacts.items():
            # 筛选类型为导弹（Type=1）的目标
            if not isinstance(contact, dict) or contact.get('Type') != 1: 
                continue
            
            missile_pos = (contact['Lat'], contact['Lon'])  # 导弹位置
            dist_km = geo.get_horizontal_distance(aircraft_pos, missile_pos)  # 计算距离
            
            if dist_km <= 100:  # 仅考虑100km内的导弹
                missile_heading = contact.get('CurrentHeading')  # 导弹当前航向
                if missile_heading is None: 
                    continue  # 无航向信息则跳过
                
                # 计算导弹到战斗机的方位角（导弹指向战斗机的方向）
                bearing_to_aircraft = geo.get_azimuth(missile_pos, aircraft_pos)
                # 计算导弹航向与目标方位角的差值
                angle_diff = abs(bearing_to_aircraft - missile_heading)
                # 确定规避方向（左或右）
                notch_ward = 1 if bearing_to_aircraft - missile_heading > 0 else -1
                # 处理角度环绕（取最小角度差，如350度与10度的差为20度）
                angle_diff = min(angle_diff, 360 - angle_diff)
                
                # 角度差<=20度（处于导弹攻击锥内），且距离更近则更新最近威胁
                if angle_diff <= 20:
                    if dist_km < min_dist:
                        min_dist = dist_km
                        closest_threat = contact
        
        return closest_threat, notch_ward  # 返回最近的真实威胁及规避方向

    def _calculate_drag_course(self, unit_info, threat_info):
        """计算拖拽规避航线（引导导弹远离，适用于中距离导弹）
        
        逻辑：沿导弹指向战斗机的方向飞行（保持在导弹导引头范围内，引导其远离关键区域）
        
        Args:
            unit_info: 战斗机信息
            threat_info: 导弹威胁信息
        
        Returns:
            规避航线点列表（单个点）
        """
        aircraft_pos = (unit_info['lat'], unit_info['lon'])
        missile_pos = (threat_info['Lat'], threat_info['Lon'])
        # 导弹指向战斗机的方位角
        bearing_missile_to_aircraft = geo.get_azimuth(missile_pos, aircraft_pos)
        evasion_heading = bearing_missile_to_aircraft  # 沿该方位角飞行
        # 计算30km外的规避点
        evasion_point = geo.get_geopoint_from_distance(aircraft_pos, evasion_heading, 30)
        return [evasion_point]

    def _calculate_notch_course(self, unit_info, threat_info, notch_ward):
        """计算紧急规避航线（快速脱离导弹攻击锥，适用于近距离导弹）
        
        逻辑：垂直于导弹指向方向飞行（90度转向），脱离导弹导引头锁定范围
        
        Args:
            unit_info: 战斗机信息
            threat_info: 导弹威胁信息
            notch_ward: 规避方向（1为右，-1为左）
        
        Returns:
            规避航线点列表（单个点）
        """
        aircraft_pos = (unit_info['lat'], unit_info['lon'])
        missile_pos = (threat_info['Lat'], threat_info['Lon'])
        # 导弹指向战斗机的方位角
        bearing_missile_to_aircraft = geo.get_azimuth(missile_pos, aircraft_pos)
        # 计算垂直于导弹指向的规避航向（左或右90度）
        evasion_heading = (bearing_missile_to_aircraft + notch_ward * 90) % 360
        # 计算30km外的规避点
        evasion_point = geo.get_geopoint_from_distance(aircraft_pos, evasion_heading, 30)
        return [evasion_point]

    def _find_best_target_by_value(self, fighter_obj, fighter_info, contacts):
        """查找最佳攻击目标（200km内，战术价值最高且攻击者未满）
        
        Args:
            fighter_obj: 战斗机实体
            fighter_info: 战斗机信息
            contacts: 接触到的目标字典
        
        Returns:
            best_target: 最佳目标信息（字典），无则为None
        """
        # 获取当前战斗机可用的最佳武器ID
        weapon_id, _ = self._get_best_weapon_id(fighter_obj)
        if not weapon_id:
            return None  # 无可用武器则返回空
            
        available_targets = []  # 可用目标列表
        fighter_pos = (fighter_info['lat'], fighter_info['lon'])  # 战斗机位置

        # 筛选200km内、攻击者未满的敌方飞机（Type=0）
        for guid, contact in contacts.items():
            if isinstance(contact, dict) and contact.get('Type') == 0:  # Type=0为飞机
                contact_pos = (contact['Lat'], contact['Lon'])
                dist_km = geo.get_horizontal_distance(fighter_pos, contact_pos)  # 计算距离
                
                if dist_km > self.engagement_range_km:
                    continue  # 超出交战范围则跳过

                # 检查目标当前的攻击者数量
                current_attackers = self.target_assignment_counts.get(guid, 0)
                if current_attackers < self.max_attackers_per_target:
                    contact['guid'] = guid  # 记录目标GUID
                    available_targets.append(contact)
        
        if not available_targets:
            return None  # 无可用目标则返回空

        # 格式化目标和自身信息，用于威胁评估
        targets_formatted = [self._format_target_for_threat(t) for t in available_targets]
        self_unit_formatted = self._format_unit_for_threat(fighter_info)
        
        # 计算目标威胁等级向量（战术价值）
        threat_vector = self.threat_evaluator.threat_matrix(targets_formatted, [self_unit_formatted]).flatten()
        # 计算攻击概率向量（武器对目标的杀伤概率）
        pk_vector = self._calculate_pk_for_plane(fighter_obj, weapon_id, available_targets)
        
        # 综合评分：威胁等级 + 攻击概率
        result_vector = threat_vector + pk_vector
        
        best_target = None
        best_score = self.wta_threshold  # 初始最佳评分为阈值

        # 筛选评分最高的目标
        for i in range(len(result_vector)):
            if result_vector[i] > best_score:
                best_score = result_vector[i]
                best_target = available_targets[i]
        
        return best_target

    def _get_best_weapon_id(self, fighter_obj):
        """获取战斗机当前可用的最佳空空导弹ID
        
        Args:
            fighter_obj: 战斗机实体
        
        Returns:
            weapon_id: 最佳武器ID，无则为None
            count: 武器数量
        """
        weapon_info = fighter_obj.get_weapon_info()  # 获取武器信息
        # 遍历预设的空空导弹ID，返回第一个有库存的武器
        for dbid in self.AIR_TO_AIR_MISSILE_DBIDs:
            if dbid in weapon_info and weapon_info[dbid] > 0:
                return dbid, weapon_info[dbid]
        return None, 0

    def _format_unit_for_threat(self, unit_info):
        """格式化己方单位信息，用于威胁评估器
        
        Args:
            unit_info: 单位信息字典
        
        Returns:
            格式化后的单位信息
        """
        return {
            'lon': unit_info['lon'], 'lat': unit_info['lat'], 'alt': unit_info['alt'],
            'speed': unit_info['speed'], 'head': unit_info['head'],
            'aircraft_type': unit_info.get('type')  # 机型
        }

    def _format_target_for_threat(self, contact_info):
        """格式化目标信息，用于威胁评估器
        
        Args:
            contact_info: 目标接触信息字典
        
        Returns:
            格式化后的目标信息
        """
        return {
            'lon': contact_info['Lon'], 'lat': contact_info['Lat'],
            'alt': contact_info.get('CurrentAltitude', 0.0),  # 高度
            'speed': contact_info.get('CurrentSpeed', 0.0),   # 速度
            'head': contact_info.get('CurrentHeading', 0.0),  # 航向
            'aircraft_type': contact_info.get('ActType')      # 目标机型
        }

    def _calculate_pk_for_plane(self, fighter_obj, weapon_id, targets_list):
        """计算当前战斗机对各目标的攻击概率（P(k)）
        
        Args:
            fighter_obj: 战斗机实体
            weapon_id: 武器ID
            targets_list: 目标列表
        
        Returns:
            pk_vector: 各目标的攻击概率向量（numpy数组）
        """
        pk_vector = np.zeros(len(targets_list))  # 初始化概率向量
        
        self_unit_info = fighter_obj.get_summary_info()  # 获取己方单位摘要信息
        
        # 遍历目标列表，计算每个目标的攻击概率
        for i, target_contact in enumerate(targets_list):
            try:
                # 计算距离（海里）
                dist_nm = self.threat_evaluator.get_horizontal_distance(
                    self_unit_info['lon'], self_unit_info['lat'], 
                    target_contact['Lon'], target_contact['Lat']
                )
                # 计算攻击概率（参数2表示空中目标）
                pk = calculate_possibility(weapon_id, target_contact, 2, dist_nm)
                pk_vector[i] = pk
            except Exception as e:
                print(f"[警告] P(k) 计算失败 (WeaponID: {weapon_id}, Target: {target_contact.get('Name')}): {e}")
                pk_vector[i] = 0.0  # 计算失败时概率设为0
            
        return pk_vector