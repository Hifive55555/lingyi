# -*- coding:utf-8 -*-
import json
import re
from datetime import datetime, timedelta

from .common import ManagerServer_pb2


# 事件类型：推演方收到的事件类型定义
# THWeaponDestroyedInfo等请查看entitys/struct.proto文件定义，进而获取事件中的单元等信息
WEAPON_DESTROYED_TYPE = 0x00063  # 武器销毁事件 THWeaponDestroyedInfo
WEAPON_FIRED_TYPE = 0x00057  # 武器开火事件 THWeaponFiredInfo
JAMING_TYPE = 0x00064  # 电子干扰事件 THJamingInfoList
NEW_UNIT_TYPE = 0x00066  # 新增单元 THUnitNewbornInfo
UNIT_DESTROYED_TYPE = 0x00055  # 单元摧毁事件 THUnitDestroyedInfo
NEW_CONTACT_TYPE = 0x00068  # 新情报 THContactInfo
CONTACT_DETECT_RECORD = 0x00071  # 情报探测记录 THLastDetectionList
key_msg_set = {WEAPON_DESTROYED_TYPE, WEAPON_FIRED_TYPE, JAMING_TYPE,
               NEW_UNIT_TYPE, UNIT_DESTROYED_TYPE, NEW_CONTACT_TYPE, CONTACT_DETECT_RECORD}
side_key_msg = "KeyMsg"
ZERO_TIME = datetime(1970, 1, 1, 0, 0, 0)


def room_info_proto_to_dict(_room_info_proto):
    """
    将RoomInfoProto中的信息转换为字典格式
    # TODO, players中的信息没有转换
    :param _room_info_proto:
    :return:
    """
    _room = dict()
    _room['id'] = _room_info_proto.id.decode('utf-8')
    _room['name'] = _room_info_proto.name.decode('utf-8')
    _room['scenario_name'] = _room_info_proto.scenario_name.decode('utf-8')
    _room['app_ip'] = _room_info_proto.appip.decode('utf-8')
    _room['app_port'] = _room_info_proto.appport
    _room['is_free'] = _room_info_proto.isfree
    _room['sim_status'] = _room_info_proto.simstatus
    _room['usage'] = _room_info_proto.usage
    _room['dds_port'] = _room_info_proto.ddsport
    _room['players'] = _room_info_proto.players
    _room['progress'] = _room_info_proto.progress
    _room['father_id'] = _room_info_proto.fatherid.decode('utf-8')
    _room['start_time'] = _room_info_proto.starttime
    _room['time'] = _room_info_proto.time
    _room['duration'] = _room_info_proto.duration
    _room['room_passwd'] = _room_info_proto.room_passwd.decode('utf-8')
    _room['scen_speed'] = _room_info_proto.scenSpeed
    _room['room_mode'] = _room_info_proto.room_mode
    _room['is_private'] = _room_info_proto.isPrivate
    _room['run_ready_time'] = _room_info_proto.runReadyTime
    _room['scenario_ip'] = _room_info_proto.scenario_ip.decode('utf-8')
    _room['scenario_port'] = _room_info_proto.scenario_port
    _room['node_ip'] = _room_info_proto.node_ip.decode('utf-8')
    _room['node_port'] = _room_info_proto.node_port
    return _room


def room_info_dict_to_proto(_room_info_dict):
    """
    将字典格式的房间信息转换成RoomInfoProto格式
    # TODO, players中的信息没有转换
    :param _room_info_dict:
    :return:
    """
    room_info = ManagerServer_pb2.RoomInfoProto()
    if 'id' in _room_info_dict.keys():
        room_info.id = _room_info_dict['id'].encode('utf-8')
    if 'name' in _room_info_dict.keys():
        room_info.name = _room_info_dict['name'].encode('utf-8')
    if 'scenario_name' in _room_info_dict.keys():
        room_info.scenario_name = _room_info_dict['scenario_name'].encode('utf-8')
    if 'app_ip' in _room_info_dict.keys():
        room_info.appip = _room_info_dict['app_ip'].encode('utf-8')
    if 'app_port' in _room_info_dict.keys():
        room_info.appport = _room_info_dict['app_port']
    if 'is_free' in _room_info_dict.keys():
        room_info.isfree = _room_info_dict['is_free']
    if 'sim_status' in _room_info_dict.keys():
        room_info.simstatus = _room_info_dict['sim_status']
    if 'usage' in _room_info_dict.keys():
        room_info.usage = _room_info_dict['usage']
    if 'dds_port' in _room_info_dict.keys():
        room_info.ddsport = _room_info_dict['dds_port']
    if 'players' in _room_info_dict.keys():
        room_info.players = _room_info_dict['players']
    if 'progress' in _room_info_dict.keys():
        room_info.progress = _room_info_dict['progress'].encode('utf-8')
    if 'father_id' in _room_info_dict.keys():
        room_info.fatherid = _room_info_dict['father_id'].encode('utf-8')
    if 'start_time' in _room_info_dict.keys():
        room_info.starttime = _room_info_dict['start_time']
    if 'time' in _room_info_dict.keys():
        room_info.time = _room_info_dict['time']
    if 'duration' in _room_info_dict.keys():
        room_info.duration = _room_info_dict['duration']
    if 'room_passwd' in _room_info_dict.keys():
        room_info.room_passwd = _room_info_dict['room_passwd'].encode('utf-8')
    if 'scen_speed' in _room_info_dict.keys():
        room_info.scenSpeed = _room_info_dict['scen_speed']
    if 'room_mode' in _room_info_dict.keys():
        room_info.room_mode = _room_info_dict['room_mode']
    if 'is_private' in _room_info_dict.keys():
        room_info.isPrivate = _room_info_dict['is_private']
    if 'run_ready_time' in _room_info_dict.keys():
        room_info.runReadyTime = _room_info_dict['run_ready_time']
    if 'scenario_ip' in _room_info_dict.keys():
        room_info.scenario_ip = _room_info_dict['scenario_ip'].encode('utf-8')
    if 'scenario_port' in _room_info_dict.keys():
        room_info.scenario_port = _room_info_dict['scenario_port']
    if 'node_ip' in _room_info_dict.keys():
        room_info.node_ip = _room_info_dict['node_ip'].encode('utf-8')
    if 'node_port' in _room_info_dict.keys():
        room_info.node_port = _room_info_dict['node_port']

    return room_info


def room_req_dict_to_proto(_room_name, _room_init_param):
    if 'is_private' not in _room_init_param.keys():
        _room_init_param['is_private'] = False
    if 'scen_speed' not in _room_init_param.keys():
        _room_init_param['scen_speed'] = 1
    if 'scen_name' not in _room_init_param.keys():
        _room_init_param['scen_name'] = ""
    if 'room_mode' not in _room_init_param.keys():
        _room_init_param['room_mode'] = 0
    room_request = ManagerServer_pb2.RoomReqProto(
        room_name=_room_name.encode('utf-8'),
        room_mode=_room_init_param['room_mode'],
        scen_name=_room_init_param['scen_name'].encode('utf-8'),
        isPrivate=_room_init_param['is_private'],
        scenSpeed=_room_init_param['scen_speed'],
    )
    return room_request


def logged_message_proto_to_dict(_logged_message):
    """
    将THLoggedMessage中的信息转换为字典格式
    :param _logged_message:
    :return:
    """
    _message = dict()
    _message['id'] = _logged_message.ID.decode('utf-8')
    _message['name'] = _logged_message.Increment
    _message['text'] = _logged_message.Text.decode('utf-8')
    _message['summary'] = _logged_message.Summary.decode('utf-8')
    _message['time_stamp'] = _logged_message.TimeStamp
    _message['level'] = _logged_message.Level
    _message['type'] = _logged_message.Type
    _message['reporter_id'] = _logged_message.ReporterID.decode('utf-8')
    _message['target_id'] = _logged_message.TargetID.decode('utf-8')
    _message['firing_parent'] = _logged_message.FiringParent.decode('utf-8')
    _message['side'] = _logged_message.Side.decode('utf-8')
    _message['location'] = _logged_message.Location.decode('utf-8')
    return _message


def extract_mission_type(task_name):
    """从任务名称中提取尖括号内的任务类型"""
    # 方法1：正则表达式（推荐）
    match = re.search(r'<(.*?)>', task_name)
    return match.group(1) if match else None


def decode_unit_fields(unit):
    """递归解码单元对象中的字节字段"""
    for field, value in unit.ListFields():
        if isinstance(value, bytes):
            setattr(unit, field.name, value.decode('utf-8'))
        elif hasattr(value, 'ListFields'):
            # 处理嵌套的proto message
            decode_unit_fields(value)
        elif isinstance(value, list):
            # 处理列表中的元素，如子单元或属性列表
            for item in value:
                if isinstance(item, bytes):
                    setattr(unit, field.name, item.decode('utf-8'))
                elif hasattr(item, 'ListFields'):
                    decode_unit_fields(item)


def parse_json(data: bytes) -> dict:
    return json.loads(data.decode('utf-8'))


def parse_unit_info(msg):
    pattern = r'(\w+)\s*=\s*[\'"](.*?)[\'"]'
    matches = re.findall(pattern, msg)
    return dict(matches)


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
