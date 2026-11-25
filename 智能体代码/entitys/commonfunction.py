# -*- coding:utf-8 -*-

import re
from datetime import datetime, timedelta
import pickle
import json
import traceback
import sys

from .global_util import *

"""
通用工具函数集合，包含数据处理、文件操作、时间转换等功能
示例: 任务GUID解析、JSON文件操作、想定时间处理等
"""

ZERO_TIME = datetime(1970, 1, 1, 0, 0, 0)
ALT_BANDS = [0, 6, 450, 1000, 3000, 7000, 10000]

mission_pattern_str = "guid = '([a-z0-9A-Z-]+)',"
# mission_guid_pattern = re.compile(r"guid = '([a-z0-9A-Z-]+)'", re.M | re.S)
zone_guid_pattern = re.compile(r"zone {\r\n guid = '([a-z0-9A-Z-]+)'", re.M | re.S)
lua_common_function_str = ""


def mission_guid_parser(mission_return_str):
    """
    通过创建任务或获取任务返回的字符串，获取任务guid
    :param mission_return_str: 创建任务或获取任务详情返回的字符串,  mission {\r\n guid = 'fdbd661d-2c96-46fb-8e2d-ea0738764604', \r\n name =...
    :return: str, 任务guid
    """
    # m_ret = mission_guid_pattern.match(mission_return_str)  # 适配C++引擎
    m_ret = re.search(mission_pattern_str, mission_return_str)
    if m_ret is not None:
        guid = m_ret.group(1)
        return guid
    return None


def zone_guid_parser(zone_return_str):
    """
    通过创建任务或获取任务返回的字符串，获取任务guid
    :param zone_return_str: 创建区域（禁航或封锁）返回的字符串
    :return: str, 任务guid
    """
    m_ret = zone_guid_pattern.match(zone_return_str)
    if m_ret is not None:
        guid = m_ret.group(1)
        return guid
    return None


def guid_list_parser(guid_list_str):
    """
    返回的guid列表字符串解析器
    :param guid_list_str: str, 获取的guid列表，例：'{"1":"kcfzsj-0hlvnpqoem4v8","2":"kcfzsj-0hlvnpqoem51s"}'
    :return:
    """
    guid_list = []
    if guid_list_str:
        try:
            list_json = json.loads(guid_list_str)
            for index, guid in list_json.items():
                guid_list.append(guid)
        except Exception as e:
            traceback.print_exc()
            # logging.error("解析任务分配单元或者目标列表出错--信息:%s" % str(e))
    return guid_list


def save_json_file(filename, json_object):
    """
    保存json对象为文件
    :param filename: str, 文件路径
    :param json_object: json对象
    """
    with open(filename, mode='w', encoding='utf-8') as fp:
        json.dump(json_object, fp, ensure_ascii=False, indent=4)


def read_json_file(filename):
    """
    读取json对象文件到返回json对象
    :param filename: str, 文件路径
    :return json_object: json对象
    """
    json_object = None
    try:
        with open(filename, mode='r', encoding='utf-8') as fp:
             json_object = json.load(fp)
    except Exception as e:
        pass
    return json_object


def save_python_file(filename, filedata):
    """
    pickle保存文件
    :param filename: str 文件名
    :param filedata: 文件数据
    :return: 成功与否
    """    
    dictfile = open(filename, 'wb')
    if dictfile:
        pickle.dump(filedata, dictfile)
        dictfile.close()
        return True
    else:
        return False


def load_python_file(filename):
    """
    pickle加载文件
    :param filename: str 文件名
    :return:文件数据, Python类型
    """
    filedata = None
    dictfile = open(filename, 'rb')
    if dictfile:
        filedata = pickle.load(dictfile)
        dictfile.close()
    return filedata


def get_scenario_time(time_stamp, beijing_time=False):
    """
    获取当前想定时间，字符串格式
    :param time_stamp:
    :return:
    """
    if beijing_time:
        current = ZERO_TIME + timedelta(seconds=(time_stamp/1000 + 8*60*60))
    else:
        current = ZERO_TIME + timedelta(seconds=(time_stamp / 1000))
    return current.strftime("%Y/%m/%d %H:%M:%S")


def parse_weapons_record(weapon_ratio):
    """
    返回武器的精简信息，适用于挂架，挂载，弹药库的武器解析
    :return:
    """
    info = []
    weapon_name_type = {}
    w_set = set()
    if '@' in weapon_ratio:
        load_ratios = weapon_ratio.split('@')
        for record in load_ratios:
            record_v = record.split('$')
            w_id = int(record_v[1])
            info.append({
                "wpn_guid": record_v[0],
                "wpn_dbid": w_id,
                "wpn_current": int(record_v[2]),
                "wpn_maxcap": int(record_v[3])
            })
            w_set.add(w_id)
    else:
        if '$' in weapon_ratio:
            record_v = weapon_ratio.split('$')
            w_id = int(record_v[1])
            info.append({
                "wpn_guid": record_v[0],
                "wpn_dbid": w_id,
                "wpn_current": int(record_v[2]),
                "wpn_maxcap": int(record_v[3])
            })
            w_set.add(w_id)
    return info


mission_class_values = {
    "Strike": 1,
    "Patrol": 2,
    "Support": 3,
    "Ferry": 4,
    "Mining": 5,
    "MineClearing": 6,
    "Cargo": 8
}


mission_patrol_n = {
    "AAW": MissionPatrolType.AIR,
    "SUR_SEA": MissionPatrolType.ANTI_SHIP,
    "SUR_LAND": MissionPatrolType.ANTI_LAND,
    "SUR_MIXED": MissionPatrolType.ANTI_MLP,
    "SUB": MissionPatrolType.ANTI_SUBMARINE,
    "SEAD": MissionPatrolType.SEAD,
    "SEA": MissionPatrolType.SEA_CONTROL
}


mission_strike_n = {
    "AIR": MissionStrikeType.AIR,
    "LAND": MissionStrikeType.LAND,
    "SEA": MissionStrikeType.SHIP,
    "SUB": MissionStrikeType.SUBMARINE,
}


def get_situation_time(time_stamp):
    """
    获取当前想定时间，字符串格式
    :param time_stamp:
    :return:
    """
    current = ZERO_TIME + timedelta(seconds=(time_stamp))
    return current.strftime("%Y-%m-%d %H:%M:%S")


def get_config_result(config_file, coding='utf-8'):
    """
    获取配置文件中的配置
    :param config_file:  str, 配置文件名
    :param coding:  str, 配置文件编码
    :return:
    """
    config_result = {}
    with open(config_file, mode='r', encoding=coding) as fp:
        lines = fp.readlines()
        for line in lines:
            new_str = line.strip().strip("\ufeff")
            if not new_str.startswith("#") and "=" in new_str:
                e_index = new_str.index("=")
                if e_index > 0:
                    key_data = new_str[0:e_index].strip()
                    value_data = new_str[e_index + 1:]
                    if "#" in value_data:
                        value_data = value_data.split("#")[0].strip()
                    config_result[key_data] = value_data
    return config_result


def read_config(config_ini):
    """
    读取本地文件 config.ini的配置
    :param config_ini:
    :return:
    """
    server_config = get_config_result("config.ini")
    config_ini["server"] = server_config


def str2bin(str):
    """
    字符串转换为二进制
    :return:
    """
    return ' '.join([bin(ord(c)).replace('0b', '') for c in str])


def bin2str(bin):
    """
    二进制转换为字符串
    :return:
    """
    return ''.join([chr(i) for i in [int(b, 2) for b in bin.split(" ")]])


def parse_attack_info(check_result):
    """
    解析开火条件返回内容
    :param check_result: str, 后台返回的开火条件检测
    :return: dict, 有效可打击武器
    """
    try:
        valid_weapons = {}
        if sys.version_info >= (3, 9):
            attacks = json.loads(check_result)
        else:
            attacks = json.loads(check_result, encoding='utf8')
        for weapon_id, info in attacks.items():
            if "ManualFire" in info and 'OK' in info["ManualFire"]:
                weapon_id_int = int(weapon_id)
                if weapon_id_int not in valid_weapons:
                    valid_weapons[weapon_id_int] = info["ManualFire"]["OK"]
                else:
                    valid_weapons[weapon_id_int] += info["ManualFire"]["OK"]
        return valid_weapons
    except Exception:
        print("error result:{}".format(check_result))
        traceback.print_exc()
    return valid_weapons


def get_status_type(ops_code):
    """
    获取飞机状态
    :return: AirValidStatus
    """
    if ops_code in (1, 2, 4, 8, 9, 18, 23, 24, 26):
        # 在基地可马上部署飞行任务
        return AirValidStatus.validToFly
    elif ops_code in (0, 13, 14, 15, 16, 19, 20, 21, 22):
        # 在空中可部署巡逻，进攻，航路规划
        return AirValidStatus.InAir
    elif ops_code in (5, 10, 11, 17, 25):
        # 在空中返航或降落
        return AirValidStatus.InAirRTB
    else:
        # 在基地等待准备好
        return AirValidStatus.WaitReady


def air_in_base(ops_code):
    """
    飞机在基地或空中
    :return: bool, 基地：True, 空中: False
    """
    if ops_code in (0, 13, 14, 15, 16, 19, 20, 21, 22, 5, 10, 11, 17, 25):
        return False
    else:
        return True


def is_contains_chinese(strs):
    """
    查询判断字符串是否包含中文
    :param strs:
    :return:
    """
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def update_dict(dict_origin, dict_new):
    """
    递归更新原始的字典对象
    :param dict_origin: dict, the content need update
    :param dict_new: dict, the new value to update origin content
    :return: dict
    """
    if dict_origin:
        for k, v in dict_new.items():
            if k not in dict_origin:
                dict_origin[k] = v
            else:
                if not isinstance(v, type(dict_origin[k])):
                    # if type(v) != type(dict_origin[k]):
                    # 值类型不一致，有一值为DELETE
                    # logger.info('key:{}, v0:{}, v1:{}'.format(k, dict_origin[k], v))
                    dict_origin[k] = v
                else:
                    if type(v) != dict:
                        dict_origin[k] = v
                    else:
                        dict_origin[k] = update_dict(dict_origin[k], dict_new[k])
        return dict_origin
    else:
        return dict_new


def find_and_delete_cp39_files():
    # 脚本文件所在目录（关键修复）
    import os
    crt_path = os.path.dirname(__file__)

    deleted_files = []
    invalid_deduce_file = os.path.join(crt_path, "deduce_RL.cp39-win_amd64.pyd")
    if os.path.exists(invalid_deduce_file):
        invalid_files = [invalid_deduce_file, os.path.join(crt_path, "gameunit.cp39-win_amd64.pyd")]
        for file_path in invalid_files:
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
                print(f"已删除失效文件: {file_path}")
            except Exception as e:
                print(f"删除失效文件失败: {file_path}, 错误: {e}")

    gameenvs_dir = os.path.join(crt_path, "gameenvs")
    invalid_client_file = os.path.join(gameenvs_dir, "gameconnect_client.cp39-win_amd64.pyd")
    invalid_zmq_client = os.path.join(gameenvs_dir, "zmq_client.cp39-win_amd64.pyd")
    invalid_sdk = os.path.join(gameenvs_dir, "ZLNetSDKPY.cp39-win_amd64.pyd")
    invalid_local = os.path.join(gameenvs_dir, "gameconnectlocal.cp39-win_amd64.pyd")
    invalid_local2 = os.path.join(gameenvs_dir, "gameconnect_local.cp39-win_amd64.pyd")
    invalid_server = os.path.join(gameenvs_dir, "gameserver.cp39-win_amd64.pyd")
    if os.path.exists(invalid_client_file) or os.path.exists(invalid_zmq_client) or os.path.exists(invalid_sdk) or \
        os.path.exists(invalid_local) or os.path.exists(invalid_local2) or os.path.exists(invalid_server):
        envs_invalid = [
            "gameconnect.cp39-win_amd64.pyd",
            "gameconnect_client.cp39-win_amd64.pyd",
            "gameconnect_k8s.cp39-win_amd64.pyd",
            "gameconnectk8s.cp39-win_amd64.pyd",
            "gameconnect_local.cp39-win_amd64.pyd",
            "gameconnectlocal.cp39-win_amd64.pyd",
            "gameconnect_normal.cp39-win_amd64.pyd",
            "gameserver.cp39-win_amd64.pyd",
            "wargame_server.cp39-win_amd64.pyd",
            "ZLNetSDKPY.cp39-win_amd64.pyd",
            "zmq_client.cp39-win_amd64.pyd",
            "situation.cp39-win_amd64.pyd"
        ]
        for e_file_path in envs_invalid:
            file_path = os.path.join(gameenvs_dir, e_file_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    print(f"已删除失效文件: {file_path}")
                except Exception as e:
                    print(f"删除失效文件失败: {file_path}, 错误: {e}")

    if not deleted_files:
        print("所有文件正常，未找到失效 cp39-win_amd64.pyd文件。")
    else:
        print(f"共删除 {len(deleted_files)} 个失效文件。")



