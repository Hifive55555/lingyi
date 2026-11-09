# Author: MouQingPing


from engine.LingYi.entitys.data import query_data as qd
def calculate_possibility(weapon_id, contact, contact_proficiency_level, unit_target_distance):
    """
        返回武器对飞机的命中率
        参数：
            weapon_id：武器的DBID
            contact：目标单元dict
            contact_proficiency_level：目标的操作员熟练度  默认，2
            unit_target_distance：目标与单元之间的距离，  单位：海里
        返回：
            武器对飞机的命中率
    """

    if "IDStatus" not in contact or "Type" not in contact:
        return 0
    IDStatus = contact["IDStatus"]
    contact_dbid = 0
    if IDStatus >= 3:
        contact_dbid = contact["DBID"]
    contact_type = contact["Type"]
    weapon_info = qd.get_weapon_info(weapon_id)
    attack_rate = 0  # 攻击成功概率
    if contact_type == 0 :
        # 目标是飞机
        air_range = weapon_info[0]   #武器对空最大射程
        if not air_range > 0:        # 武器基础命中率（初始值）
            return 0
        base_pok = weapon_info[1]    # 武器基础命中率（初始值）
        attack_rate = base_pok       # 目标最大速度阈值
        target_speed_max = weapon_info[8]
        if contact_type == 0:
            # 目标是飞机
            if qd.is_missile(weapon_id):
                # 是导弹，发射导弹单元到目标距离对命中率修正
                launch_distance = unit_target_distance
                dis_change = launch_distance / air_range
                weapon_propulsion_type = qd.get_weapon_propulsion_type(weapon_id)
                if weapon_propulsion_type == 5001 or weapon_propulsion_type == 5003:
                    propulsion_rate = 0.5
                else:
                    propulsion_rate = 0.75
                if dis_change > propulsion_rate:
                    attack_rate = base_pok * propulsion_rate + base_pok * (1-propulsion_rate) * \
                                  (1-(dis_change-propulsion_rate)/(1-propulsion_rate))
            if target_speed_max > 0:
                # 命中概率(经目标速度修正)
                speed_rate = 0
                target_speed = contact["CurrentSpeed"]
                if target_speed > target_speed_max:
                    speed_rate = 50
                elif target_speed > target_speed_max*0.8:
                    speed_rate = 25
                elif target_speed > target_speed_max*0.7:
                    speed_rate = 15
                elif target_speed > target_speed_max*0.6:
                    speed_rate = 10
                elif target_speed > target_speed_max*0.5:
                    speed_rate = 5
                if speed_rate:
                    attack_rate = round(attack_rate-speed_rate)
                    if attack_rate < 0:
                        attack_rate = 0
            if IDStatus >= 3:
                air_info = qd.get_aircraft_info(contact_dbid)
                agility, crew = air_info[3], air_info[8]
                weapon_detect_by_aircraft = True  # 默认飞机能够探测到攻击的导弹, 实际应根据是否已探测到进行判断
                if crew > 0 and agility > 0 and weapon_detect_by_aircraft:
                    actual_agility = get_aircraft_kinematics_agility(agility, contact, contact_proficiency_level)
                    # 假定飞机会90度左右躲避导弹，机动系数(强转向攻击无影响)
                    actual_agility = round(actual_agility, 1)
                    attack_rate = attack_rate - actual_agility * 10
            elif IDStatus >= 2:
                if contact['ActType'] is not None:
                    type_id = contact['ActType']
                    agility = estimate_agility(type_id)
                    attack_rate = attack_rate - agility * 10
        if contact['CurrentAltitude'] > 0 and not qd.is_weapon_capableVSSeaskimmer(weapon_id):
            # 命中概率(掠海攻击修正量)     “掠海攻击”可能是指武器设计为贴近海面飞行，比如反舰导弹，而如果武器不支持这种攻击方式，那么当目标（比如舰船）在低空时，攻击效果会受到影响。
            target_alt = contact['CurrentAltitude']
            sea_rate = 30
            if target_alt >= 91.44:
                sea_rate = 0
            elif target_alt >= 60.96:
                sea_rate = 5
            elif target_alt >= 30.48:
                sea_rate = 15
            attack_rate -= sea_rate

        attack_rate /= 100
        if attack_rate < 0:
            attack_rate = 0

    return attack_rate


def estimate_agility(air_type):
    """
        根据飞机类型返回飞机的机敏度
        参数：
            air_type：飞机类型
            contact：目标单元dict
        返回：
            飞机的机敏度
    """
    agility = 2
    if air_type == 2001 or air_type == 2002 or air_type == 3001 or air_type == 3002 or air_type == 3401:
        # 战斗机、攻击机
        agility = 4.5
    elif air_type == 3101:
        # 轰炸机
        agility = 2.0
    elif air_type == 4002 or air_type == 4003:
        # 预警机
        agility = 0.5
    elif air_type == 8201 or air_type == 8202:
        # 无人机
        agility = 0.5
    elif air_type == 4001 or 7003 <= air_type <= 7005:
        # 电子战或侦察机
        agility = 2.5
    return agility

def get_agility_with_alt(agility, contact):
    """
        高度对敏捷度的纠偏
        参数：
            agility：目标基础机敏性，读数据库得到
            contact：目标单元dict
        返回：
            高度对机敏性的纠偏结果
    """
    alt = contact['CurrentAltitude']
    if alt <= 3000:
        return agility
    weak_rate = 0.5
    air_dbid = contact["DBID"]
    if 4001 in qd.get_unit_codes("Aircraft", air_dbid):
        weak_rate = 0.25
    alt_to_max = qd.get_aircraft_ceiling(air_dbid) - contact['CurrentAltitude']
    alt_to_3000 = contact['CurrentAltitude'] - 3000
    agility_down = agility * weak_rate * (alt_to_3000 / alt_to_max)
    return max(agility*(1-weak_rate), agility-agility_down)

def get_aircraft_kinematics_agility(agility, contact, proficiency_level):
    """
        高度、熟练度、飞机载重对基础机敏度agility的纠偏
        参数：
            agility：目标基础机敏性，读数据库得到
            contact：目标单元dict
            proficiency_level：操作员熟练度
        返回：
            最终机敏度，即高度、熟练度、飞机载重对基础机敏度agility的纠偏结果
    """
    kinematics_agility = round(get_agility_with_alt(agility, contact), 1)
    if proficiency_level == 0:
        kinematics_agility *= 0.3
    elif proficiency_level == 1:
        kinematics_agility *= 0.5
    elif proficiency_level == 2:
        kinematics_agility *= 0.8
    elif proficiency_level == 3:
        pass
    elif proficiency_level == 4:
        kinematics_agility *= 1.2
    weight_rate = qd.get_load_weight_rate(contact["DBID"])
    kinematics_agility = 0.4 * kinematics_agility + 0.6 * kinematics_agility * (1-weight_rate)
    return kinematics_agility