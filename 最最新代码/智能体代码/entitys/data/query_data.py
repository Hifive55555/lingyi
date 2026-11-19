# -*- coding: utf-8 -*-
# Author:
# Date

import os

from .DB_manager import DbManage

dbmanager = None
db_path = os.path.join(os.path.dirname(__file__), "model.db")
weapon_cache = {}
weapon_name_cache = {}
weapon_type_cache = {}
weapon_target_cache = {}
weapon_codes_cache = {}
weapon_subpok_cache = {}
unit_codes_cache = {}
weapon_is_ballistic_missile_cache = {}
weapon_ballistic_or_reentry_cache = {}
unit_sensors_cache = {}
sensor_cache = {}
sensor_type_cache = {}
sensor_role_cache = {}
sensor_ECMPoKReduction_cache = {}
sensor_generation_cache = {}
sensor_code_cache = {}
unit_cost_cache = {}
unit_type_cost_cache = {}
type_description_cache = {}
unit_type_description_cache = {}
unit_category_description_cache = {}
unit_type_cache = {}
unit_category_cache = {}
facility_threat_cache = {}
contact_threat_cache = {}
contact_type_threat_cache = {}
aircraft_cache = {}
aircraft_RCS_cache = {}
ship_info_cache = {}
facility_info_cache = {}
ship_type_size_cache = {}
facility_type_size_cache = {}
facility_point_rate = {}
weapon_valid_id_cache = {}
weapon_propulsion_type_cache = {}
weapon_max_speed_cache = {}  # 武器最大速度
weapon_sensor_range_count = {}  # 武器传感器搜索范围数量 0-16，代表0-360
aircraft_ceiling_cache = {}
aircraft_max_speed_cache = {}  # 飞机最大速度
aircraft_min_speed_cache = {}
aircraft_weight_with = {}  # 飞机平均携带重量：武器重量+燃油重量
aircraft_fuel_capacity_cache = {}  # 飞机满油量
unit_signatures_cache = {}  # 单元信号特征缓存
unit_name_cache = {}
submarine_max_speed_cache = {}
facility_mount_exist_cache = {}
satellite_mission_name_cache = {}  # 卫星sid到卫星名缓存
torpedo_fuel = {}  # 鱼雷燃油量
torpedo_spoof_possibility = {}  # 鱼雷被诱饵诱骗概率
attack_mobile = {}  # 武器是否可打击地面移动目标
weapon_warhead_dp = {}  # 武器战斗部毁伤当量


attack_weapon_set = {
    2001: "制导武器",
    2002: "火箭弹",
    2003: "炸弹",
    2004: "火炮",
    2009: "集束炸弹",
    2010: "接触炸弹（自杀式）",
    2011: "接触炸弹（破坏）",
    2012: "制导炮弹",
    4001: "鱼雷",
    4002: "深弹",
    4004: "沉底水雷",
    4005: "锚雷",
    4006: "浮雷",
    4007: "自航水雷",
    4008: "上浮雷",
    4009: "漂雷",
    4011: "教练雷",
    5001: "战略战术导弹",
    8001: "超音速飞行工具",
}


def get_attack_weapon_type(weapon_id):
    # 通过武器DBID获取武器类型
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)
    sql_str = "SELECT TYPE FROM DataWeapon WHERE ID = %d" % weapon_id
    result = []
    bResult = dbmanager.execute(sql_str, result)
    if bResult:
        for infor_row in result:
            type_n = int(infor_row[0])
            if type_n in attack_weapon_set:
                return attack_weapon_set[type_n]
    return ""


def get_weapon_type(weapon_id):
    # 通过武器DBID获取武器类型
    global dbmanager, weapon_type_cache
    if weapon_id in weapon_type_cache:
        return weapon_type_cache[weapon_id]
    if dbmanager is None:
        dbmanager = DbManage(db_path)
    sql_str = "SELECT TYPE FROM DataWeapon WHERE ID = %d" % weapon_id
    result = []
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        weapon_type_cache[weapon_id] = result[0][0]
        return result[0][0]
    return 1001


def get_weapon_name(weapon_id):
    # 通过武器DBID获取武器型号名称
    global weapon_name_cache
    if weapon_id in weapon_name_cache:
        return weapon_name_cache[weapon_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    sql_str = "SELECT name FROM DataWeapon WHERE ID = %d" % weapon_id
    result = []
    w_name = ""
    bResult = dbmanager.execute(sql_str, result)
    if bResult:
        for infor_row in result:
            w_name = infor_row[0]
            weapon_name_cache[weapon_id] = w_name
            return w_name
    return w_name


def get_weapon_info(weapon_id):
    # 通过武器DBID获取武器射程，目标最大速度，CEP等值
    global weapon_cache
    if weapon_id in weapon_cache:
        return weapon_cache[weapon_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)
    sql_str = "SELECT AirRangeMax,AirPoK,LandRangeMax,LandPoK,SurfaceRangeMax," \
              "SurfacePoK,SubsurfaceRangeMax,SubsurfacePoK,TargetSpeedMax,TargetAltitudeMax,TargetAltitudeMin," \
              "CEP,CEPSurface,Name FROM DataWeapon WHERE ID = %d" % weapon_id
    result = []
    if dbmanager.execute(sql_str, result):
        if len(result) == 1:
            weapon_cache[weapon_id] = result[0]
            return result[0]
    return []


def get_weapon_submarine_pok(weapon_id):
    """
    获取武器对水下攻击置性度
    :param weapon_id:
    :return:
    """
    global weapon_subpok_cache
    if weapon_id in weapon_subpok_cache:
        return weapon_subpok_cache[weapon_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)
    sql_str = "SELECT SubsurfacePoK FROM DataWeapon WHERE ID = %d" % weapon_id
    result = []
    if dbmanager.execute(sql_str, result):
        if len(result) == 1 and result[0] is not None:
            weapon_subpok_cache[weapon_id] = result[0][0]
            return result[0][0]
    return 70


def get_unit_name(category, unit_dbid):
    # 通过单元类型和DBID获取单元型号名称
    global unit_name_cache
    if category in unit_name_cache and unit_dbid in unit_name_cache[category]:
        return unit_name_cache[category][unit_dbid]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    table_name = "Data%s" % category
    result = []
    uname = ""
    sql_str = "SELECT Name from %s WHERE ID = %d" % (table_name, int(unit_dbid))
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for code in result:
            if code[0] is not None:
                uname = code[0]
                if category in unit_name_cache:
                    unit_name_cache[category][unit_dbid] = uname
                else:
                    unit_name_cache[category] = {
                        unit_dbid: uname
                    }
    return uname


def get_satellite_mission_name(sid):
    # 通过卫星sid获取卫星发射任务名
    global satellite_mission_name_cache
    if sid in satellite_mission_name_cache:
        return satellite_mission_name_cache[sid]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    if "_" not in sid:
        return ""
    parts = sid.split("_")
    dbid = parts[0]
    dbmid = parts[1]
    result = []
    uname = ""
    sql_str = "SELECT MissonName FROM DataSatelliteOrbits WHERE ID = %s AND ComponentNumber = %s" % (dbid, dbmid)
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for code in result:
            if code[0] is not None:
                uname = code[0]
                satellite_mission_name_cache[sid] = uname
    return uname


def get_weapon_range_pok(weapon_id, target_type):
    """
    返回武器对相应目标射程和基准命中率
    """
    weapon_info = get_weapon_info(weapon_id)
    if not weapon_info:
        return 0, 0
    if target_type in {0, 1, 6, 13}:
        # 空中
        return weapon_info[0], weapon_info[1]
    elif target_type in {2, 4, 14, 17}:
        # 水面
        return weapon_info[4], weapon_info[5]
    elif target_type in {7, 8, 15, 18, 19, 20, 21, 22}:
        # 地面
        return weapon_info[2], weapon_info[3]
    elif target_type in {3, 9, 10, 13, 16}:
        # 水下
        return weapon_info[6], weapon_info[7]
    return 0, 0


def get_weapon_airpok(weapon_id):
    # 通过武器DBID获取对空基础命中率
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)
    sql_str = "SELECT AirPoK FROM DataWeapon WHERE ID = %d" % weapon_id
    result = []
    bResult = dbmanager.execute(sql_str, result)
    if bResult:
        if len(result) == 1:
            return result[0][0]
    return None


def get_weapon_sensor_detect_range(weapon_id):
    """
    获取武器传感器最大探测范围数量
    :param weapon_id:
    :return:
    """
    global weapon_sensor_range_count
    if weapon_id in weapon_sensor_range_count:
        return weapon_sensor_range_count[weapon_id]

    range_count = 0
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)
    sql_str = "SELECT max(SB1+SB2+SMF1+SMF2+SMA1+SMA2+SS1+SS2+PB1+PB2+PMF1+PMF2+PMA1+PMA2+PS1+PS2) RANGE FROM " \
              "DataWeaponSensors WHERE ID = %d" % weapon_id
    result = []
    if dbmanager.execute(sql_str, result):
        if len(result) == 1:
            if result[0][0] is not None:
                range_count = result[0][0]
                weapon_propulsion_type_cache[weapon_id] = range_count
    return range_count


def get_weapon_propulsion_type(weapon_id):
    # 通过武器DBID获取发动机类型
    global weapon_propulsion_type_cache
    if weapon_id in weapon_propulsion_type_cache:
        return weapon_propulsion_type_cache[weapon_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)
    sql_str = "SELECT DataPropulsion.Type FROM DataWeaponPropulsion LEFT JOIN DataPropulsion ON " \
              "DataWeaponPropulsion.ComponentID=DataPropulsion.ID WHERE DataWeaponPropulsion.ID = %d" % weapon_id
    result = []
    if dbmanager.execute(sql_str, result):
        if len(result) == 1:
            weapon_propulsion_type_cache[weapon_id] = result[0][0]
            return result[0][0]
    return 1001


def get_facility_category(facility_id):
    # 通过地面装备DBID获取类别
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)
    sql_str = "SELECT category FROM DataFacility WHERE ID = %d" % facility_id
    result = []
    bResult = dbmanager.execute(sql_str, result)
    if bResult:
        if len(result) == 1:
            return result[0][0]
    return None


def get_sensor_info(sensor_id):
    # 通过传感器DBID获取传感器名，类型描述等
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    sensor_info = []
    capacity = ""
    sql_str = "SELECT EnumSensorCapability.Description FROM DataSensorCapabilities LEFT JOIN EnumSensorCapability " \
              "on DataSensorCapabilities.CodeID = EnumSensorCapability.ID WHERE DataSensorCapabilities.ID = %d" % sensor_id
    result = []
    bResult = dbmanager.execute(sql_str, result)
    if bResult:
        for capa in result:
            if capacity != "":
                capacity += "," + capa[0]
            else:
                capacity = capa[0]

    result = []
    sql_str = "SELECT DataSensor.ID, NAME, DataSensor.Comments, EnumSensorType.Description TYPE," \
              "EnumSensorRole.Description role, RangeMax FROM DataSensor LEFT JOIN EnumSensorType " \
              "ON DataSensor.Type = EnumSensorType.ID LEFT JOIN EnumSensorRole ON DataSensor.Role = EnumSensorRole.ID " \
              "WHERE DataSensor.ID = %d" % sensor_id
    bResult = dbmanager.execute(sql_str, result)
    if bResult:
        if len(result) == 1:
            sensor_info.append(result[0][0])
            sensor_info.append(result[0][1])
            sensor_info.append(result[0][2])
            sensor_info.append(result[0][3])
            sensor_info.append(result[0][4])
            sensor_info.append(capacity)
            sensor_info.append(result[0][5])
    return sensor_info


def get_detect_info(category, unit_dbid):
    # 查询单元探测能力
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    sensor_table = "Data" + category + "Sensors"
    result = []
    sql_str = "SELECT DataSensor.id,DataSensor.name,DataSensor.Type,DataSensor.Role,DataSensor.RangeMax from " \
              "%s LEFT JOIN DataSensor on %s.ComponentID = DataSensor.id " \
              "WHERE %s.id = %d" % (sensor_table, sensor_table, sensor_table, unit_dbid)
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        return result
    return []


def weapon_ballistic_or_reentry(missile_dbid):
    # 通过武器DBID获取是否弹道导弹或者大气层再入武器
    global weapon_ballistic_or_reentry_cache
    if missile_dbid in weapon_ballistic_or_reentry_cache:
        return weapon_ballistic_or_reentry_cache[missile_dbid]

    if is_ballistic_missile(missile_dbid):
        weapon_ballistic_or_reentry_cache[missile_dbid] = True
        return True

    codes = get_weapon_codes(missile_dbid)
    if 7001 in codes or 7002 in codes or 7003 in codes:
        weapon_ballistic_or_reentry_cache[missile_dbid] = True
        return True
    else:
        weapon_ballistic_or_reentry_cache[missile_dbid] = False
        return False


def get_weapon_max_speed(weapon_id):
    """
    获取武器最大速度
    :param weapon_id:
    :return: 海里/小时
    """
    global weapon_max_speed_cache
    if weapon_id in weapon_max_speed_cache:
        return weapon_max_speed_cache[weapon_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    max_speed = 50
    result = []
    sql_str = "SELECT max(DataPropulsionPerformance.Speed) from DataWeaponPropulsion " \
              "LEFT JOIN DataPropulsionPerformance ON DataWeaponPropulsion.ComponentID=DataPropulsionPerformance.ID " \
              "WHERE DataWeaponPropulsion.ID = %d" % weapon_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            if row_result[0] is not None:
                max_speed = row_result[0]
                weapon_max_speed_cache[weapon_id] = result[0][0]
            break
    return max_speed


def get_weapon_launch_speed(weapon_id):
    """
    获取武器发射速度
    :param weapon_id:
    :return:
    """

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    max_speed = 50
    result = []
    sql_str = "SELECT max(DataPropulsionPerformance.Speed) from DataWeaponPropulsion " \
              "LEFT JOIN DataPropulsionPerformance ON DataWeaponPropulsion.ComponentID=DataPropulsionPerformance.ID " \
              "WHERE DataWeaponPropulsion.ID = %d AND DataPropulsionPerformance.AltitudeBand=1" % weapon_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            if row_result[0] is not None:
                max_speed = row_result[0]
                weapon_max_speed_cache[weapon_id] = result[0][0]
            break
    return max_speed


def is_ballistic_missile(missile_dbid):
    # 通过武器DBID获取是否弹道导弹
    global weapon_is_ballistic_missile_cache
    if missile_dbid in weapon_is_ballistic_missile_cache:
        return weapon_is_ballistic_missile_cache[missile_dbid]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    w_type = get_weapon_type(missile_dbid)
    if w_type == 5000:
        return True

    codes = get_weapon_codes(missile_dbid)
    result = 4010 in codes
    weapon_is_ballistic_missile_cache[missile_dbid] = result
    return result


def get_weapon_codes(missile_dbid):
    # 通过武器DBID获取武器功能
    global weapon_codes_cache
    if missile_dbid in weapon_codes_cache:
        return weapon_codes_cache[missile_dbid]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    codes = []
    sql_str = "SELECT CodeID from DataWeaponCodes WHERE ID = %d" % missile_dbid
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for code in result:
            codes.append(code[0])
        weapon_codes_cache[missile_dbid] = codes
    return codes


def get_unit_codes(category, unit_dbid):
    """
    获取实体功能
    """
    global unit_codes_cache
    if category in unit_codes_cache and unit_dbid in unit_codes_cache[category]:
        return unit_codes_cache[category][unit_dbid]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    codes = []
    sql_str = "SELECT CodeID from Data%sCodes WHERE ID = %d" % (category, unit_dbid)
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for code in result:
            codes.append(code[0])
        if category in unit_codes_cache:
            unit_codes_cache[category][unit_dbid] = codes
        else:
            unit_codes_cache[category] = {
                unit_dbid: codes
            }
    return codes


def is_RV_or_HGV(weapon_dbid, weapon_type=None):
    # 通过武器DBID获取武器是否超音速导弹或托盘弹药
    if weapon_type is None:
        weapon_type = get_weapon_type(weapon_dbid)
    if weapon_type == 5002 or weapon_type == 8001:
        return True
    return False


def is_missile(weapon_dbid):
    # 通过武器DBID获取武器是否导弹，或超音速导弹或托盘弹药
    weapon_type = get_weapon_type(weapon_dbid)
    if weapon_type == 2001 or is_ballistic_missile(weapon_dbid) or is_RV_or_HGV(weapon_dbid, weapon_type):
        return True
    return False


def get_weapon_targets(weapon_dbid):
    # 通过武器DBID获取武器目标类型
    global weapon_target_cache
    if weapon_dbid in weapon_target_cache:
        return weapon_target_cache[weapon_dbid]
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT CodeID FROM DataWeaponTargets WHERE ID = %d" % weapon_dbid
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        code_set = set()
        for code in result:
            code_set.add(code[0])
        weapon_target_cache[weapon_dbid] = code_set
        return code_set
    return set()


def weapon_target_ship_or_radar(weapon_dbid):
    # 服务器函数method_196() 文件weapon.cs
    # 攻击舰艇或者雷达
    targets = get_weapon_targets(weapon_dbid)
    if 2001 in targets:
        return True
    if 3004 in targets:
        return True
    return False


def weapon_target_air(weapon_dbid):
    # 通过武器DBID获取武器目标是否空中类型
    weapon_type = get_weapon_type(weapon_dbid)
    if weapon_type in (2005, 2006, 2007):
        return False
    targets = get_weapon_targets(weapon_dbid)
    if 1001 in targets:
        return True
    if 1003 in targets:
        return True
    return False


def weapon_target_facility_or_radar(weapon_dbid):
    # 服务器函数method_195() 文件weapon.cs
    # 攻击地面设施或者雷达
    targets = get_weapon_targets(weapon_dbid)
    return 3004 in targets or 3001 in targets or 3002 in targets or 3003 in targets or \
           4001 in targets or 4002 in targets


def is_weapon_capableVSSeaskimmer(weapon_id):
    """
    武器是否有掠海攻击能力
    """
    return 2006 in get_weapon_codes(weapon_id)


def get_aircraft_info(unit_dbid):
    """
    查询飞机单元的信息
    """
    global aircraft_cache
    if unit_dbid in aircraft_cache:
        return aircraft_cache[unit_dbid]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT Category,type,name,Agility,WeightMax,YearCommissioned,YearDecommissioned,fillCost,Crew," \
              "WeightEmpty from DataAircraft WHERE ID = %d" % unit_dbid
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        aircraft_cache[unit_dbid] = result[0]
        return result[0]
    return []


def get_aircraft_front_rcs(unit_dbid):
    """
    查询飞机前向雷达RCS的信息
    """
    global aircraft_RCS_cache
    if unit_dbid in aircraft_RCS_cache:
        return aircraft_RCS_cache[unit_dbid]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT front from DataAircraftSignatures WHERE ID = %d AND Type = 5001" % unit_dbid
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for s_result in result:
            rcs_data = s_result[0]
            aircraft_RCS_cache[unit_dbid] = rcs_data
            return rcs_data
    return 999


def get_ship_info(unit_dbid):
    """
    查询舰艇的信息
    """
    global ship_info_cache
    if unit_dbid in ship_info_cache:
        return ship_info_cache[unit_dbid]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT Category,type,name,DisplacementStandard,YearCommissioned,YearDecommissioned," \
              "fillCost,Length,Beam from DataShip WHERE ID = %d" % unit_dbid
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        ship_info_cache[unit_dbid] = result[0]
        return result[0]
    return []


def get_unit_mount_weapon(category, unit_dbid):
    # 查询单元挂架的武器
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    ship_mount = "Data%sMounts" % category
    sql_str = "SELECT DataWeaponRecord.ComponentID,DataWeaponRecord.DefaultLoad,DataWeapon.Name from %s " \
              "LEFT JOIN DataMountWeapons ON %s.ComponentID=DataMountWeapons.ID " \
              "LEFT JOIN DataWeaponRecord ON DataMountWeapons.ComponentID=DataWeaponRecord.ID " \
              "LEFT JOIN DataWeapon ON DataWeaponRecord.ComponentID=DataWeapon.ID WHERE %s.ID = %d" % \
              (ship_mount, ship_mount, ship_mount, unit_dbid)
    result = []
    exe_result = dbmanager.execute(sql_str, result)
    weapon_result = {}
    if exe_result:
        for weapon in result:
            wid = weapon[0]
            count = weapon[1]
            name = weapon[2]
            if wid in weapon_result:
                weapon_result[wid]["count"] += count
            else:
                weapon_result[wid] = {
                    "name": name,
                    "count": count
                }
    return weapon_result


def get_facility_info(facility_id):
    # 通过地面装备DBID获取名称，类别，类型，长度等
    global facility_info_cache
    if facility_id in facility_info_cache:
        return facility_info_cache[facility_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)
    sql_str = "SELECT Name,Category,Type,Armorgeneral,YearCommissioned,YearDecommissioned,fillCost,Length,Width," \
              "DamagePoints,MountsAreAimpoints FROM DataFacility WHERE ID = %d" % facility_id
    result = []
    bResult = dbmanager.execute(sql_str, result)
    if bResult:
        if len(result) == 1:
            facility_info_cache[facility_id] = result[0]
            return result[0]
    return []


def get_unit_sensors(category, unit_dbid):
    """
    获取实体所有传感器集合
    """
    global unit_sensors_cache
    if category in unit_sensors_cache and unit_dbid in unit_sensors_cache[category]:
        return unit_sensors_cache[category][unit_dbid]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    sensor_table = "Data%sSensors" % category
    sensors = set()
    result = []
    sql_str = "SELECT ComponentID from %s WHERE id = %d " % (sensor_table, unit_dbid)
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for s_result in result:
            if s_result[0] not in sensors:
                sensors.add(s_result[0])

        if category == "Weapon":
            if category not in unit_sensors_cache:
                unit_sensors_cache[category] = {
                    unit_dbid: sensors
                }
            else:
                unit_sensors_cache[category][unit_dbid] = sensors
            return sensors

        mount_table = "Data%sMounts" % category
        sql_str = "SELECT DataMountSensors.ComponentID from DataMountSensors LEFT JOIN %s ON %s.ComponentID = " \
                  "DataMountSensors.ID WHERE %s.ID = %d" % (mount_table, mount_table, mount_table, unit_dbid)
        result = []
        exe_result = dbmanager.execute(sql_str, result)
        if exe_result:
            for s_result in result:
                if s_result[0] not in sensors:
                    sensors.add(s_result[0])

        # 如果是传感器组，再获取传感器
        alreay_sensors = list(sensors)
        for sensorid in alreay_sensors:
            sensor_type = get_sensor_type(sensorid)
            if sensor_type == 9001:
                sql_str = "Select ComponentID from DataSensorSensorGroups where ID = %d" % sensorid
                result = []
                exe_result = dbmanager.execute(sql_str, result)
                if exe_result:
                    for s_result in result:
                        if s_result[0] not in sensors:
                            sensors.add(s_result[0])

        if category not in unit_sensors_cache:
            unit_sensors_cache[category] = {
                unit_dbid: sensors
            }
        else:
            unit_sensors_cache[category][unit_dbid] = sensors

        return sensors
    return set()


def get_sensor_type(sensor_id):
    """
    获取传感器类型
    """
    global sensor_type_cache
    if sensor_id in sensor_type_cache:
        return sensor_type_cache[sensor_id]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT type from DataSensor WHERE id = %d " % sensor_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for s_result in result:
            sensor_type = s_result[0]
            sensor_type_cache[sensor_id] = sensor_type
            return sensor_type
    return 1001


def get_sensor_role(sensor_id):
    """
    获取传感器角色
    """
    global sensor_role_cache
    if sensor_id in sensor_role_cache:
        return sensor_role_cache[sensor_id]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT Role from DataSensor WHERE id = %d " % sensor_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for s_result in result:
            sensor_role = s_result[0]
            sensor_role_cache[sensor_id] = sensor_role
            return sensor_role
    return 1001


def get_sensor_ECMPoKReduction(sensor_id):
    """
    获取传感器ECMPoKReduction 干扰能力
    """
    global sensor_ECMPoKReduction_cache
    if sensor_id in sensor_ECMPoKReduction_cache:
        return sensor_ECMPoKReduction_cache[sensor_id]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT ECMPoKReduction from DataSensor WHERE id = %d " % sensor_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for s_result in result:
            sensor_ECM_POK = s_result[0]
            sensor_ECMPoKReduction_cache[sensor_id] = sensor_ECM_POK
            return sensor_ECM_POK
    return 0


def get_sensor_generation(sensor_id):
    """
    获取传感器代级
    """
    global sensor_generation_cache
    if sensor_id in sensor_generation_cache:
        return sensor_generation_cache[sensor_id]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT Generation from DataSensor WHERE id = %d " % sensor_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for s_result in result:
            nresult = s_result[0]
            sensor_generation_cache[sensor_id] = nresult
            return nresult
    return 0


def get_sensor_code(sensor_id):
    """
    获取传感器功能代码
    """
    global sensor_code_cache
    if sensor_id in sensor_code_cache:
        return sensor_code_cache[sensor_id]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT CodeID from DataSensorCodes WHERE ID = %d" % sensor_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        codes = set()
        for s_result in result:
            codes.add(s_result[0])
        sensor_code_cache[sensor_id] = codes
        return codes
    return set()


def is_sensor_interfere(sensor_id):
    """
    传感器可否干扰别的传感器
    """
    role = get_sensor_role(sensor_id)
    if role == 4011 or role == 4041 or role == 4021:
        return True
    return False


def sensor_is_ECM(sensor_id):
    """
    传感器有ECM角色
    """
    role = get_sensor_role(sensor_id)
    if role == 4001 or role == 4021 or role == 4091:
        return True
    return False


def is_sensor_interfere_other(sensor_id, sensor_id2):
    """
    传感器可否干扰别的传感器
    """
    role = get_sensor_role(sensor_id)
    type = get_sensor_type(sensor_id2)
    if type == 2004:
        # 红外
        return role == 4041
    elif type == 2001 or type == 2002:
        return is_sensor_interfere(sensor_id) or sensor_is_ECM(sensor_id)
    elif type == 5002 or type == 5003 or type == 5013 or type == 5023 or type == 5032 or type == 5033:
        return role == 4901
    return False


def get_sensor_interfere_possibility(weapon_dbid, unit_category, unit_dbid):
    """
    获取武器打击目标致盲概率,对舰导弹打船、鱼雷打船（典型适用）
    # 东风21D 打阿里伯克驱逐舰
    pos1 = qd.get_sensor_interfere_possibility(2106, "Ship", 2716)
    print(pos1)  # 35
    # 鹰击18打 打阿里伯克驱逐舰
    pos2 = qd.get_sensor_interfere_possibility(2867, "Ship", 2716)
    print(pos2)  # 35
    # 鹰击18打 打雾岛级驱逐舰
    pos22 = qd.get_sensor_interfere_possibility(2867, "Ship", 1003405)
    print(pos22)  # 10
    pos3 = qd.get_sensor_interfere_possibility(2106, "Ship", 442)
    print(pos3)  # 20
    pos4 = qd.get_sensor_interfere_possibility(2106, "Ship", 2718)
    print(pos4)  # 35
    """
    weapon_sensors = get_unit_sensors("Weapon", weapon_dbid)
    if not weapon_sensors:
        return 0

    unit_sensors = get_unit_sensors(unit_category, unit_dbid)
    if not unit_sensors:
        return 0

    no_interfere_possibility = 1  # 不致盲概率
    for wsensor in weapon_sensors:
        wsensor_type = get_sensor_type(wsensor)
        if wsensor_type == 3001:
            if 3004 not in get_weapon_targets(weapon_dbid):
                continue
        elif wsensor_type == 3002:
            continue

        safe_possibility = 1
        for usensor in unit_sensors:
            if is_sensor_interfere(usensor) and is_sensor_interfere_other(usensor, wsensor):
                interfere_possibility = 0  # 此传感器对武器传感器致盲概率
                urole = get_sensor_role(usensor)
                ECMPokReduction = get_sensor_ECMPoKReduction(usensor)
                generation = get_sensor_generation(usensor)
                if generation == 1002:
                    # 没有待级
                    interfere_possibility = ECMPokReduction
                elif urole == 4041:
                    interfere_possibility = ECMPokReduction
                else:
                    generation_sub = generation - get_sensor_generation(wsensor)
                    if generation_sub < -3:
                        interfere_possibility = ECMPokReduction - 15
                    elif generation_sub == -3:
                        interfere_possibility = ECMPokReduction - 10
                    elif generation_sub == -2:
                        interfere_possibility = ECMPokReduction - 5
                    elif generation_sub == -1 or generation_sub == 0 or generation_sub == 1:
                        interfere_possibility = ECMPokReduction
                    elif generation_sub == 2:
                        interfere_possibility = ECMPokReduction + 5
                    elif generation_sub == 3:
                        interfere_possibility = ECMPokReduction + 10
                    elif generation_sub > 3:
                        interfere_possibility = ECMPokReduction + 15
                if wsensor_type == 2001 and 3012 in get_sensor_code(wsensor):
                    interfere_possibility -= 30
                interfere_possibility = max(interfere_possibility, 5)
                safe_possibility *= (1 - interfere_possibility)
                no_interfere_possibility *= (1 - interfere_possibility)
        if safe_possibility == 1:
            no_interfere_possibility = 1
            break
    return 1 - no_interfere_possibility


def get_unit_cost(category, unit_dbid):
    """
    获取单元价值
    """
    global unit_cost_cache
    if category in unit_cost_cache and unit_dbid in unit_cost_cache[category]:
        return unit_cost_cache[category][unit_dbid]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    data_table = "Data%s" % category
    result = []
    sql_str = "SELECT fillCost FROM %s WHERE ID = %d" % (data_table, unit_dbid)
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for s_result in result:
            cost = s_result[0]
            if category not in unit_cost_cache:
                unit_cost_cache[category] = {
                    unit_dbid: cost
                }
            else:
                unit_cost_cache[category][unit_dbid] = cost
            return cost
    return 0


def get_unit_type_id(category, type_description):
    """
    通过单元类型描述获取单元类型id
    """
    global type_description_cache
    description = type_description.strip()
    if category in type_description_cache and description in type_description_cache[category]:
        return type_description_cache[category][description]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    data_table = "Enum%sType" % category
    result = []
    sql_str = "SELECT ID,Description from %s" % data_table
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for s_result in result:
            type_id = s_result[0]
            type_despt = s_result[1].strip()
            if category not in type_description_cache:
                type_description_cache[category] = {
                    type_despt: type_id
                }
            else:
                type_description_cache[category][type_despt] = type_id
        if category in type_description_cache and description in type_description_cache[category]:
            return type_description_cache[category][description]
    return 1001


def get_unit_type_description(category, unit_type_id):
    """
    实体类型ID得到实体类型描述
    """
    global unit_type_description_cache
    if category in unit_type_description_cache and unit_type_id in unit_type_description_cache[category]:
        return unit_type_description_cache[category][unit_type_id]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    data_table = "Enum%sType" % category
    result = []
    sql_str = "SELECT ID,Description from %s" % data_table
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for s_result in result:
            type_id = s_result[0]
            type_despt = s_result[1].strip()
            if category not in unit_type_description_cache:
                unit_type_description_cache[category] = {
                    type_id: type_despt
                }
            else:
                unit_type_description_cache[category][type_id] = type_despt
        if category in unit_type_description_cache and unit_type_id in unit_type_description_cache[category]:
            return unit_type_description_cache[category][unit_type_id]
    return ""


def get_unit_category_description(category, unit_category_id):
    """
    实体类型ID得到实体类型描述
    """
    global unit_category_description_cache
    if category in unit_category_description_cache and unit_category_id in unit_category_description_cache[category]:
        return unit_category_description_cache[category][unit_category_id]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    data_table = "Enum%sCategory" % category
    result = []
    sql_str = "SELECT ID,Description from %s" % data_table
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for s_result in result:
            type_id = s_result[0]
            type_despt = s_result[1].strip()
            if category not in unit_category_description_cache:
                unit_category_description_cache[category] = {
                    type_id: type_despt
                }
            else:
                unit_category_description_cache[category][type_id] = type_despt
        if category in unit_category_description_cache and unit_category_id in unit_category_description_cache[
            category]:
            return unit_category_description_cache[category][unit_category_id]
    return ""


def init_cost(log=None):
    """
    初始化价值缓存
    """
    global unit_cost_cache
    category_list = ["Aircraft", "Ship", "Facility", "Submarine"]
    for category in category_list:
        unit_cost_cache[category] = {}

        # 查询飞机单元的信息
        global dbmanager
        if dbmanager is None:
            dbmanager = DbManage(db_path)

        data_table = "Data%s" % category
        result = []
        sql_str = "SELECT ID,fillCost FROM %s" % data_table
        exe_result = dbmanager.execute(sql_str, result)
        if exe_result:
            for row_result in result:
                id = row_result[0]
                cost = row_result[1]
                unit_cost_cache[category][id] = cost


def get_avg_cost_from_type(category, type_id):
    global unit_type_cost_cache
    if category in unit_type_cost_cache and type_id in unit_type_cost_cache[category]:
        return unit_type_cost_cache[category][type_id]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT Type,avg(fillCost) from Data%s GROUP BY type" % category
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            type_id = row_result[0]
            type_cost = row_result[1]
            if category not in unit_type_cost_cache:
                unit_type_cost_cache[category] = {
                    type_id: type_cost
                }
            else:
                unit_type_cost_cache[category][type_id] = type_cost
        if category in unit_type_cost_cache and type_id in unit_type_cost_cache[category]:
            return unit_type_cost_cache[category][type_id]
    return 10


def init_query(log=None):
    """
    """
    init_cost(log)


def get_unit_type(category, unit_dbid):
    """
    获取单元类型id
    """
    global unit_type_cache
    if category in unit_type_cache and unit_dbid in unit_type_cache[category]:
        return unit_type_cache[category][unit_dbid]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    data_table = "Data%s" % category
    result = []
    sql_str = "SELECT Type from %s WHERE ID=%d" % (data_table, unit_dbid)
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            type_id = row_result[0]
            if category in unit_type_cache:
                unit_type_cache[category][unit_dbid] = type_id
            else:
                unit_type_cache[category] = {
                    unit_dbid: type_id
                }
            return type_id
    return 1001


def get_unit_category(category, unit_dbid):
    """
    获取单元类别
    """
    global unit_category_cache
    if category in unit_category_cache and unit_dbid in unit_category_cache[category]:
        return unit_category_cache[category][unit_dbid]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    data_table = "Data%s" % category
    result = []
    sql_str = "SELECT Category from %s WHERE ID=%d" % (data_table, unit_dbid)
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            category_id = row_result[0]
            if category in unit_category_cache:
                unit_category_cache[category][unit_dbid] = category_id
            else:
                unit_category_cache[category] = {
                    unit_dbid: category_id
                }
            return category_id
    return 1001


def get_facility_weapon_threat(unit_dbid):
    """
    获取是否有对空、对舰、对地、对潜艇威胁能力
    """
    global facility_threat_cache
    if unit_dbid in facility_threat_cache:
        return facility_threat_cache[unit_dbid]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    threat_result = [False, False, False, False]  # 对空、对舰、对地、对潜艇威胁能力
    result = []
    sql_str = "SELECT DataWeapon.ID,DataWeapon.NAME,DataWeapon.AirRangeMax,DataWeapon.SurfaceRangeMax," \
              "DataWeapon.LandRangeMax,DataWeapon.SubsurfaceRangeMax from DataFacilityMounts LEFT JOIN " \
              "DataMountWeapons ON DataFacilityMounts.ComponentID=DataMountWeapons.ID LEFT JOIN DataWeaponRecord " \
              "ON DataMountWeapons.ComponentID=DataWeaponRecord.ID LEFT JOIN DataWeapon " \
              "ON DataWeaponRecord.ComponentID=DataWeapon.ID WHERE DataFacilityMounts.ID = %d " \
              "and DataWeapon.ID > 0" % unit_dbid
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        weapon_id_set = set()
        for row_result in result:
            w_id = row_result[0]
            if w_id not in weapon_id_set:
                weapon_id_set.add(w_id)
                if row_result[2] > 0:
                    threat_result[0] = True
                if row_result[3] > 0:
                    threat_result[1] = True
                if row_result[4] > 0:
                    threat_result[2] = True
                if row_result[5] > 0:
                    threat_result[3] = True
        facility_threat_cache[unit_dbid] = threat_result
    return threat_result


def get_ship_category_from_type(ship_type):
    # 通过舰船类型获取类别
    if 2001 <= ship_type <= 2011:
        return 2001
    elif 3001 <= ship_type <= 3420:
        return 2002
    elif 4000 <= ship_type <= 4028:
        return 2003
    elif 5001 <= ship_type <= 7003:
        return 2004
    elif ship_type == 9001:
        return 2005
    elif ship_type == 9002:
        return 2006
    elif 9003 <= ship_type <= 9008:
        return 2004
    elif ship_type == 9011:
        return 2001


def get_facility_category_from_type(facility_type):
    # 通过地面装备类型获取类别
    if 1001 <= facility_type <= 3007:
        return 2001
    elif 4001 <= facility_type <= 5002:
        return facility_type
    elif facility_type == 5003:
        return 5002
    elif facility_type == 5004:
        return 3001
    elif 5005 <= facility_type == 5103:
        return 5001
    elif facility_type == 6001 or facility_type == 9001:
        return facility_type


def get_threat_capacity(category, unit_dbid, conatct_type=0, type_description=""):
    """
    获取实体能力类型
    战斗机--对空、舰、地
    攻击机--对舰、地
    轰炸机--对舰、地
    预警机--对空、舰、地
    电子战机--对空、舰、地
    反潜机--对潜
    无人机--对空、舰、地
    其他辅助机（运输、加油等空、舰、地系数为0.8）---
    return: {}, Aircraft, Ship, Submarine, Land, Satellite
    """
    global contact_threat_cache, contact_type_threat_cache
    if unit_dbid != 0:
        if category in contact_threat_cache and unit_dbid in contact_threat_cache[category]:
            return contact_threat_cache[category][unit_dbid]
    else:
        if category in contact_type_threat_cache and conatct_type in contact_type_threat_cache[category]:
            return contact_type_threat_cache[category][conatct_type]

    target_discription = "战斗机"
    threat_values = {
        "Aircraft": 0,
        "Ship": 0,
        "Submarine": 0,
        "Facility": 0,
        "Satellite": 0,
        "Despt": target_discription
    }
    if category == "Aircraft":
        if unit_dbid != 0:
            air_type = get_unit_type(category, unit_dbid)
            target_discription = "飞机-%s" % get_unit_type_description(category, air_type)
        else:
            air_type = conatct_type
            target_discription = "飞机-%s" % type_description
        if air_type == 2001:
            threat_values["Aircraft"] = 1
            threat_values["Ship"] = 0.5
            threat_values["Facility"] = 0.5
        elif air_type == 2002:
            threat_values["Aircraft"] = 1
            threat_values["Ship"] = 1
            threat_values["Facility"] = 1
        elif air_type == 2101:
            threat_values["Satellite"] = 1
        elif air_type == 2002:
            threat_values["Aircraft"] = 1
            threat_values["Ship"] = 1
            threat_values["Facility"] = 1
        elif air_type == 3001:
            threat_values["Aircraft"] = 0.3
            threat_values["Ship"] = 1
            threat_values["Facility"] = 1
        elif air_type == 3002:
            threat_values["Aircraft"] = 0.3
            threat_values["Ship"] = 0.6
            threat_values["Facility"] = 1
        elif air_type == 3101:
            threat_values["Ship"] = 1
            threat_values["Facility"] = 1
        elif air_type == 4001 or air_type == 4002 or air_type == 4003:
            threat_values["Aircraft"] = 1
            threat_values["Ship"] = 1
            threat_values["Facility"] = 1
        elif air_type == 4101:
            threat_values["Aircraft"] = 0.2
            threat_values["Ship"] = 0.5
            threat_values["Facility"] = 0.5
        elif air_type == 4201:
            threat_values["Aircraft"] = 0.1
            threat_values["Ship"] = 0.3
            threat_values["Facility"] = 0.3
        elif air_type == 6001:
            threat_values["Submarine"] = 1
        elif air_type == 6002:
            threat_values["Aircraft"] = 0.1
            threat_values["Ship"] = 0.1
            threat_values["Submarine"] = 1
        elif 7001 <= air_type <= 7005:
            threat_values["Aircraft"] = 0.6
            threat_values["Ship"] = 0.6
            threat_values["Facility"] = 0.6
        elif 7101 <= air_type:
            threat_values["Aircraft"] = 0.5
            threat_values["Ship"] = 0.5
            threat_values["Facility"] = 0.5
    elif category == "Ship":
        if unit_dbid != 0:
            ship_cat = get_unit_category("Ship", unit_dbid)
        else:
            ship_cat = get_ship_category_from_type(conatct_type)
        target_discription = get_unit_category_description(category, ship_cat)
        if ship_cat == 2001 or ship_cat == 2007 or ship_cat == 2008:
            threat_values["Aircraft"] = 1
            threat_values["Ship"] = 1
            threat_values["Facility"] = 1
            threat_values["Submarine"] = 0.5
        elif ship_cat == 2002:
            threat_values["Aircraft"] = 1
            threat_values["Ship"] = 1
            threat_values["Facility"] = 1
            threat_values["Submarine"] = 0.5
        elif ship_cat == 2003:
            threat_values["Aircraft"] = 0.5
            threat_values["Ship"] = 0.5
            threat_values["Facility"] = 1
        elif ship_cat == 2004:
            threat_values["Aircraft"] = 0.6
            threat_values["Ship"] = 0.6
            threat_values["Facility"] = 0.6
        elif ship_cat == 2005:
            threat_values["Aircraft"] = 0.4
            threat_values["Ship"] = 0.4
            threat_values["Facility"] = 0.4
        elif ship_cat == 2006:
            threat_values["Aircraft"] = 0.3
            threat_values["Ship"] = 0.3
            threat_values["Facility"] = 0.3
    elif category == "Submarine":
        if unit_dbid == 0:
            sub_type = get_unit_type(category, unit_dbid)
            target_discription = get_unit_type_description(category, sub_type)
        else:
            sub_type = conatct_type
            target_discription = type_description
        if sub_type == 2004 or sub_type == 2005:
            threat_values["Facility"] = 1
            threat_values["Submarine"] = 1
        elif sub_type == 2001 or sub_type == 2002:
            threat_values["Ship"] = 0.5
            threat_values["Facility"] = 0.5
            threat_values["Submarine"] = 0.5
        elif sub_type == 2003 or 2006 <= sub_type <= 2010:
            threat_values["Ship"] = 1
            threat_values["Facility"] = 1
            threat_values["Submarine"] = 1
        elif 2011 <= sub_type <= 4003:
            threat_values["Ship"] = 0.5
            threat_values["Facility"] = 0.5
            threat_values["Submarine"] = 0.5
        elif 9001 <= sub_type <= 9002:
            threat_values["Ship"] = 0.2
            threat_values["Submarine"] = 0.2
    elif category == "Facility":
        if unit_dbid != 0:
            fat_cat = get_unit_category(category, unit_dbid)
        else:
            fat_cat = get_facility_category_from_type(conatct_type)
        target_discription = get_unit_category_description(category, fat_cat)
        if fat_cat <= 3006:
            threat_values["Aircraft"] = 0.6
            threat_values["Ship"] = 0.6
            threat_values["Facility"] = 0.6
        elif fat_cat == 4001:
            threat_values["Submarine"] = 1
        elif fat_cat == 5001 or fat_cat == 5002:
            threat_type = get_facility_weapon_threat(unit_dbid)
            if threat_type[0]:
                threat_values["Facility"] = 1
            if threat_type[1]:
                threat_values["Ship"] = 1
            if threat_type[2]:
                threat_values["Facility"] = 1
            if threat_type[3]:
                threat_values["Submarine"] = 1
        elif fat_cat == 6001 or fat_cat == 9001:
            threat_values["Aircraft"] = 0.6
            threat_values["Ship"] = 0.6
            threat_values["Facility"] = 0.6
            threat_values["Submarine"] = 0.6

    threat_values["Despt"] = target_discription
    if category in contact_threat_cache:
        contact_threat_cache[category][unit_dbid] = threat_values
    else:
        contact_threat_cache[category] = {
            unit_dbid: threat_values
        }

    return threat_values


def get_ship_size_from_type(ship_type):
    """
    获取船类型的平均大小
    """
    global ship_type_size_cache
    if ship_type in ship_type_size_cache:
        return ship_type_size_cache[ship_type]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    sql_str = "SELECT avg(Length),avg(Beam) from DataShip WHERE Type = %d" % ship_type
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            avg_len = row_result[0]
            if avg_len is not None:
                avg_beam = row_result[1]
                ship_type_size_cache[ship_type] = avg_len, avg_beam
                return avg_len, avg_beam
    return 20, 5


def get_facility_size_from_type(facility_type):
    """
    获取设施类型的平均大小
    :param: facility_type, 0:代表所有设施
    """
    global facility_type_size_cache
    if facility_type in facility_type_size_cache:
        return facility_type_size_cache[facility_type]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    if facility_type != 0:
        sql_str = "SELECT avg(Length),avg(Width) from DataFacility WHERE MountsAreAimpoints = 0 and Type = %d" % facility_type
    else:
        sql_str = "SELECT avg(Length),avg(Width) from DataFacility WHERE MountsAreAimpoints = 0"
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            avg_len = row_result[0]
            if avg_len is not None:
                avg_width = row_result[1]
                ship_type_size_cache[facility_type] = avg_len, avg_width
                return avg_len, avg_width
    return 10, 10


def get_facility_point_rate_from_type(facility_type):
    """
    获取设施类型的平均大小
    """
    global facility_point_rate
    if facility_type in facility_point_rate:
        return facility_point_rate[facility_type]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    result = []
    if facility_type != 0:
        sql_str = "SELECT MountsAreAimpoints,count(*) from DataFacility WHERE Type = %d " \
                  "GROUP BY MountsAreAimpoints" % facility_type
    else:
        sql_str = "SELECT MountsAreAimpoints,count(*) from DataFacility GROUP BY MountsAreAimpoints"
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        sum_count = 0
        point_c = 0
        for row_result in result:
            point = row_result[0]
            if point is not None:
                count = row_result[1]
                if point == 1:
                    point_c = count
                sum_count += count
        if sum_count:
            rate = point_c / sum_count
            facility_point_rate[facility_type] = rate
            return rate
    return 0.5


def get_real_attack_weapon(weapon_id):
    """
    获取实体攻击的武器id, 东风21D，武器id:2105，实际攻击弹头是2106
    """
    global weapon_valid_id_cache
    if weapon_id in weapon_valid_id_cache:
        return weapon_valid_id_cache[weapon_id]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    valid_ids = []
    result = []
    sql_str = "SELECT DataWarhead.Type,DataWarhead.DamagePoints from DataWeaponWarheads LEFT JOIN DataWarhead ON " \
              "DataWeaponWarheads.ComponentID=DataWarhead.ID WHERE DataWeaponWarheads.ID = %d" % weapon_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            warhead_type = row_result[0]
            if warhead_type is not None:
                if warhead_type == 5002:
                    valid_id = int(row_result[1])
                    valid_ids.append(valid_id)
                else:
                    valid_ids.append(weapon_id)
        weapon_valid_id_cache[weapon_id] = valid_ids
    return valid_ids


def get_aircraft_ceiling(unit_dbid):
    """
    获取飞机升限高度
    :return: float, 米
    """
    global aircraft_ceiling_cache
    if unit_dbid in aircraft_ceiling_cache:
        return aircraft_ceiling_cache[unit_dbid]

    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    ceiling = 0
    result = []
    sql_str = "SELECT max(DataPropulsionPerformance.AltitudeMax) FROM DataAircraftPropulsion LEFT JOIN " \
              "DataPropulsionPerformance ON DataAircraftPropulsion.ComponentID=DataPropulsionPerformance.ID " \
              "WHERE DataAircraftPropulsion.ID=%d" % unit_dbid
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            ceiling = row_result[0]
            aircraft_ceiling_cache[unit_dbid] = ceiling
    return ceiling


def get_aircraft_max_speed(aircraft_id):
    """
    获取飞机最大速度
    :param aircraft_id:  int, 飞机DBID
    :return: float, 海里/小时
    """
    global aircraft_max_speed_cache
    if aircraft_id in aircraft_max_speed_cache:
        return aircraft_max_speed_cache[aircraft_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    max_speed = 600
    result = []
    sql_str = "SELECT max(DataPropulsionPerformance.Speed) from DataAircraftPropulsion " \
              "LEFT JOIN DataPropulsionPerformance ON DataAircraftPropulsion.ComponentID=DataPropulsionPerformance.ID " \
              "WHERE DataAircraftPropulsion.ID = %d" % aircraft_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            if row_result[0] is not None:
                max_speed = row_result[0]
                weapon_max_speed_cache[aircraft_id] = result[0][0]
            break
    return max_speed


def get_aircraft_min_speed(aircraft_id):
    """
    获取飞机最小速度
    :param aircraft_id:  int, 飞机DBID
    :return: float, 海里/小时
    """
    global aircraft_min_speed_cache
    if aircraft_id in aircraft_min_speed_cache:
        return aircraft_min_speed_cache[aircraft_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    max_speed = 600
    result = []
    sql_str = "SELECT min(DataPropulsionPerformance.Speed) from DataAircraftPropulsion " \
              "LEFT JOIN DataPropulsionPerformance ON DataAircraftPropulsion.ComponentID=DataPropulsionPerformance.ID " \
              "WHERE DataAircraftPropulsion.ID = %d" % aircraft_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            if row_result[0] is not None:
                max_speed = row_result[0]
                aircraft_min_speed_cache[aircraft_id] = result[0][0]
            break
    return max_speed


def get_aircraft_avg_weapon_weight(air_dbid):
    """
    获取飞机平均携带武器重量
    """
    # 查询飞机单元的信息
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    weapon_weight = 0
    result = []
    sql_str = "SELECT avg(Weight) weight FROM (SELECT SUM(DataWeapon.Weight*DataWeaponRecord.DefaultLoad) AS WEIGHT " \
              "FROM DataAircraftLoadouts LEFT JOIN DataLoadoutWeapons ON DataAircraftLoadouts.ComponentID=" \
              "DataLoadoutWeapons.ID LEFT JOIN DataWeaponRecord ON DataLoadoutWeapons.ComponentID=DataWeaponRecord.ID " \
              "LEFT JOIN DataWeapon ON DataWeaponRecord.ComponentID=DataWeapon.ID WHERE DataAircraftLoadouts.ID = %d " \
              "AND DataWeapon.Weight > 0 GROUP BY DataAircraftLoadouts.ComponentID)" % air_dbid
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            if row_result[0] is not None:
                weapon_weight = row_result[0]
    return weapon_weight


def get_aircraft_loadouts(air_dbid):
    """
    获取飞机可用挂载方案
    """
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    loadouts = []
    result = []
    sql_str = "SELECT ComponentID FROM DataAircraftLoadouts WHERE ID=%d" % air_dbid
    try:
        exe_result = dbmanager.execute(sql_str, result)
        if exe_result:
            for row_result in result:
                if row_result[0] is not None:
                    loadouts.append(int(row_result[0]))
    except Exception as e:
        print("查询飞机%d挂载出错:%s！" % (air_dbid, str(e)))
    return loadouts


def get_aircraft_fuel_capacity(air_dbid):
    # 通过飞机DBID通过飞机燃油满载燃油量
    global aircraft_fuel_capacity_cache
    if air_dbid in aircraft_fuel_capacity_cache:
        return aircraft_fuel_capacity_cache[air_dbid]

    fuel_capacity = 0
    result = []
    sql_str = "SELECT DataFuel.Capacity FROM DataAircraftFuel LEFT JOIN DataFuel ON DataAircraftFuel.ComponentID=" \
              "DataFuel.ID WHERE DataAircraftFuel.ID = %d" % air_dbid
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            fuel_capacity += row_result[0]
    aircraft_fuel_capacity_cache[air_dbid] = fuel_capacity
    return fuel_capacity


def query_max_contacts_illuminate(facility_dbid):
    """
    查询防空营火控通道数
    :param facility_dbid: list 传感器bdid的列表 例如[2788, 3204]
    """
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)
    num_max_contacts_illuminate = 0
    result = []
    exe_result = False
    for dbid in facility_dbid:
        sql_str = """
            SELECT DataSensor.MaxContactsIlluminate 
            FROM DataSensor 
            WHERE DataSensor.Type=2001 
            AND DataSensor.RadarPeakPowerIlluminate>0
            AND DataSensor.ID = %d 
             """\
              % dbid
        #
        exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        num_max_contacts_illuminate = sum(tpl[0] or 0 for tpl in result)
    return num_max_contacts_illuminate


def query_aircraft_avg_weight_with(air_dbid):
    """
    预估飞机载重:武器加燃油
    """
    global aircraft_weight_with
    if air_dbid in aircraft_weight_with:
        return aircraft_weight_with[air_dbid]

    weight = get_aircraft_avg_weapon_weight(air_dbid) + get_aircraft_fuel_capacity(air_dbid) / 2
    aircraft_weight_with[air_dbid] = weight
    return weight


def get_aircraft_weight_with_fuel(air_dbid, weight_empty=0):
    """
    预估飞机带油后载重
    """
    if weight_empty == 0:
        air_info = get_aircraft_info(air_dbid)
        weight_empty = air_info[9]
    return weight_empty + get_aircraft_fuel_capacity(air_dbid) / 2


def get_load_weight_rate(air_dbid):
    """
    预估飞机挂载重量率
    """
    air_info = get_aircraft_info(air_dbid)
    weight_empty = air_info[9]
    weight_max = air_info[4]
    actual_weight = weight_empty + query_aircraft_avg_weight_with(air_dbid)
    other_weight = weight_max - get_aircraft_weight_with_fuel(air_dbid, weight_empty)
    weight_rate = min(0.99, (actual_weight - get_aircraft_weight_with_fuel(air_dbid, weight_empty)) / other_weight)
    if weight_rate < 0:
        weight_rate = 0
    return weight_rate


def get_unit_signatures(category, unit_dbid):
    """
    获取单元信号特征
    """
    global unit_signatures_cache
    if category in unit_signatures_cache and unit_dbid in unit_signatures_cache[category]:
        return unit_signatures_cache[category][unit_dbid]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    signatures = {}
    table_name = "Data%sSignatures" % category
    result = []
    sql_str = "SELECT Type,Front,Side,Rear FROM %s WHERE ID = %d" % (table_name, unit_dbid)
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            type = row_result[0]
            signatures[type] = {
                "Front": row_result[1],
                "Side": row_result[2],
                "Rear": row_result[3],
            }
        if signatures:
            if category in unit_signatures_cache:
                unit_signatures_cache[category][unit_dbid] = signatures
            else:
                unit_signatures_cache[category] = {
                    unit_dbid: signatures
                }
    return signatures


def get_submarine_max_speed(submarine_id):
    """
    获取潜艇最大速度  海里每小时
    :param submarine_id:
    :return:
    """
    global submarine_max_speed_cache
    if submarine_id in submarine_max_speed_cache:
        return submarine_max_speed_cache[submarine_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    max_speed = 30
    result = []
    sql_str = "SELECT max(DataPropulsionPerformance.Speed) from DataSubmarinePropulsion LEFT JOIN " \
              "DataPropulsionPerformance ON DataSubmarinePropulsion.ComponentID=DataPropulsionPerformance.ID WHERE " \
              "DataSubmarinePropulsion.ID = %d" % submarine_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            if row_result[0] is not None:
                max_speed = row_result[0]
                submarine_max_speed_cache[submarine_id] = max_speed
    return max_speed


def check_facility_mount_exist(facility_id):
    # 通过地面装备DBID获取是否有挂架
    global facility_mount_exist_cache
    if facility_id in facility_mount_exist_cache:
        return facility_mount_exist_cache[facility_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    exist = False
    result = []
    sql_str = "SELECT ID FROM DataFacilityMounts WHERE ID = %d" % facility_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            if row_result[0] is not None:
                exist = True
                break
        facility_mount_exist_cache[facility_id] = exist
    return exist


def get_torpedo_spoof_possibility(weapon_dbid):
    """
    获取鱼雷打击潜艇被诱骗概率
    :param weapon_dbid:
    :param submarine_dbid:
    :param submarine_type:
    :return:
    """
    global torpedo_spoof_possibility
    if weapon_dbid in torpedo_spoof_possibility:
        return torpedo_spoof_possibility[weapon_dbid]

    weapon_sensors = get_unit_sensors("Weapon", weapon_dbid)
    if not weapon_sensors:
        return 0

    decoy_count = 2  # 默认两发诱饵

    no_interfere_possibility = 1  # 不致盲概率
    generation = 2011  # 默认诱饵武器代级是 2000年代早期
    pok_sub = 25  # 默认诱饵对水下武器成功率25%
    for wsensor in weapon_sensors:
        safe_possibility = 1
        generation_sub = generation - get_sensor_generation(wsensor)
        interfere_possibility = pok_sub
        if generation_sub < -3:
            interfere_possibility = pok_sub - 15
        elif generation_sub == -3:
            interfere_possibility = pok_sub - 10
        elif generation_sub == -2:
            interfere_possibility = pok_sub - 5
        elif generation_sub == -1 or generation_sub == 0 or generation_sub == 1:
            interfere_possibility = pok_sub
        elif generation_sub == 2:
            interfere_possibility = pok_sub + 5
        elif generation_sub == 3:
            interfere_possibility = pok_sub + 10
        elif generation_sub > 3:
            interfere_possibility = pok_sub + 15
        interfere_possibility /= 100.0

        for i in range(decoy_count):
            safe_possibility *= (1 - interfere_possibility)
            no_interfere_possibility *= (1 - interfere_possibility)
            if safe_possibility == 1:
                no_interfere_possibility = 1
                break
    possibility = 1 - no_interfere_possibility
    torpedo_spoof_possibility[weapon_dbid] = possibility
    return possibility


def get_weapon_fuel_capacity(weapon_id):
    """
    获取武器燃油量，特别是鱼雷
    :param weapon_id:
    :return:
    """
    global torpedo_fuel
    if weapon_id in torpedo_fuel:
        return torpedo_fuel[weapon_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    capacity = 200
    result = []
    sql_str = "SELECT Capacity FROM DataWeaponFuel LEFT JOIN DataFuel ON DataWeaponFuel.ComponentID=DataFuel.ID " \
              "WHERE DataWeaponFuel.ID = %d" % weapon_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            if row_result[0] is not None:
                capacity = row_result[0]
                break
        torpedo_fuel[weapon_id] = capacity
    return capacity


def get_weapon_attack_mobile_unit(weapon_id: int) -> bool:
    """
    获取武器是否可以打击地面移动目标
    :param weapon_id: 武器dbid
    :return:
    """
    global attack_mobile
    if weapon_id in attack_mobile:
        return attack_mobile[weapon_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    can_attack = False
    result = []
    sql_str = "SELECT CodeID FROM DataWeaponTargets WHERE ID = %d" % weapon_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            if row_result[0] is not None:
                target_id = row_result[0]
                if target_id in (4001, 4002, 3004):
                    can_attack = True
                    break
    attack_mobile[weapon_id] = can_attack
    return can_attack


def get_weapon_warhead_dp(weapon_id: int) -> float:
    """
    获取武器战斗部当量
    :param weapon_id: 武器dbid
    :return:
    """
    global weapon_warhead_dp
    if weapon_id in weapon_warhead_dp:
        return weapon_warhead_dp[weapon_id]

    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage(db_path)

    damage_point = 1
    result = []
    sql_str = "SELECT DataWarhead.ID,DataWarhead.TYPE,DataWarhead.DamagePoints FROM DataWeaponWarheads LEFT JOIN " \
              "DataWarhead ON DataWeaponWarheads.ComponentID = DataWarhead.ID WHERE " \
              "DataWeaponWarheads.ID = %d" % weapon_id
    exe_result = dbmanager.execute(sql_str, result)
    if exe_result:
        for row_result in result:
            if row_result[0] is not None:
                warhead_type = row_result[1]
                if warhead_type == 5002:
                    rv_weapon_id = int(row_result[2])
                    damage_point = get_weapon_warhead_dp(rv_weapon_id)
                else:
                    damage_point = float(row_result[2])
                break
    weapon_warhead_dp[weapon_id] = damage_point
    return damage_point
