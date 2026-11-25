# -*- coding: utf-8 -*-
# Author:
# Date

import datetime

from .DB_manager import DbManage

dbmanager = None


class BatResult(object):
    # 记录一局比赛结果
    def __init__(self, bat_round, time_elapse):
        self.bat_round = bat_round
        self.time = time_elapse
        self.blue_score = 0.0
        self.red_score = 0.0
        self.blue_name = ""
        self.red_name = ""
        self.error_side = ""
        self.bat_result = 0  # 1:红方胜  -1:蓝方胜  0:平局
        self.process_id = None

    def set_score(self, red_score, blue_score):
        self.red_score = red_score
        self.blue_score = blue_score
        if red_score > blue_score:
            self.bat_result = 1
        elif red_score < blue_score:
            self.bat_result = -1
        else:
            self.bat_result = 0


def save_result(bat_result):
    global dbmanager
    if dbmanager is None:
        import os
        db_path = os.path.join(os.path.dirname(__file__), "gamedata.db")
        dbmanager = DbManage(db_path)

    win_side = '平局'
    if bat_result.bat_result == 1:
        win_side = "红方"
    elif bat_result.bat_result == -1:
        win_side = "蓝方"
    elif bat_result.bat_result == 0:
        win_side = "平局"

    crt_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sqlstr = "INSERT INTO batrecord (round, red, blue, redresult, blueresult, gameresult, win_side, error_side, process, endtime) VALUES " \
             "(%d, '%s', '%s', %d, %d, %d, '%s', '%s', %d, '%s')" % (
             bat_result.bat_round, bat_result.red_name, bat_result.blue_name,
             bat_result.red_score, bat_result.blue_score, bat_result.bat_result,
             win_side, bat_result.error_side, bat_result.process_id, crt_time)

    result = dbmanager.execute(sqlstr)
    dbmanager.commit()


def get_record_count(red, blue):
    sqlstr = "SELECT count(*) as count from batrecord WHERE red='%s' and blue='%s'" % (red, blue)
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")
    results = []
    brun = dbmanager.execute(sqlstr, results)
    for record in results:
        count = int(record[0])
        return count
    return 0


def get_result():
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")
    tie_mask = 1
    win_mask = 3

    sqlstr = "SELECT red,blue,redresult,blueresult,gameresult from batrecord"
    team_result = {}
    results = []
    brun = dbmanager.execute(sqlstr, results)
    for record in results:
        red = record[0]
        blue = record[1]
        if red not in team_result:
            team_result[red] = {"red": {"mask": 0, "score": 0, "win": 0, "lost": 0, "tie": 0}, "mask":0,'win': 0, 'lost': 0,
                                'tie': 0, "batcount": 0, 'avg_score': 0.0}
        elif "red" not in team_result[red]:
            team_result[red]['red'] = {"mask": 0, "score": 0, "win": 0, "lost": 0, "tie": 0}
        if blue not in team_result:
            team_result[blue] = {"blue": {"mask": 0, "score": 0, "win": 0, "lost": 0, "tie": 0}, "mask":0, 'win': 0, 'lost': 0,
                                 'tie': 0, "batcount": 0, 'avg_score': 0.0}
        elif "blue" not in team_result[blue]:
            team_result[blue]['blue'] = {"mask": 0, "score": 0, "win": 0, "lost": 0, "tie": 0}
        bat_result = int(record[4])
        if bat_result == 0:
            team_result[red]["red"]["mask"] += tie_mask
            team_result[blue]["blue"]["mask"] += tie_mask
            team_result[red]["red"]["tie"] += 1
            team_result[blue]["blue"]["tie"] += 1
            team_result[red]["tie"] += 1
            team_result[blue]["tie"] += 1
            team_result[red]["mask"] += tie_mask
            team_result[blue]["mask"] += tie_mask
        elif bat_result == 1:
            team_result[red]["red"]["mask"] += win_mask
            team_result[red]["red"]["win"] += 1
            team_result[blue]["blue"]["lost"] += 1
            team_result[red]["win"] += 1
            team_result[blue]["lost"] += 1
            team_result[red]["mask"] += win_mask
        elif bat_result == -1:
            team_result[blue]["blue"]["mask"] += win_mask
            team_result[blue]["mask"] += win_mask
            team_result[blue]["blue"]["win"] += 1
            team_result[red]["red"]["lost"] += 1
            team_result[red]["lost"] += 1
            team_result[blue]["win"] += 1
        team_result[red]["red"]["score"] += int(record[2])
        team_result[blue]["blue"]["score"] += int(record[3])
        team_result[red]["batcount"] += 1
        team_result[blue]["batcount"] += 1
        team_result[red]["avg_score"] += int(record[2])
        team_result[blue]["avg_score"] += int(record[2])
    for team, info in team_result.items():
        if team_result[team]['batcount'] > 0:
            team_result[team]['avg_score'] = team_result[team]['avg_score'] / team_result[team]['batcount']
    team_sort = []  # 组，大得分，平均每局得分
    for team, info in team_result.items():
        i = 0
        have_insert = False
        for result in team_sort:
            if info['mask'] > result[1]:
                team_sort.insert(i, (team, info['mask'], info['avg_score'], info['win'], info['lost'], info['tie']))
                have_insert = True
                break
            elif info['mask'] == result[1]:
                if info['avg_score'] > result[2]:
                    team_sort.insert(i, (team, info['mask'], info['avg_score'], info['win'], info['lost'], info['tie']))
                    have_insert = True
                    break
            i += 1
        if not have_insert:
            team_sort.append((team, info['mask'], info['avg_score'], info['win'], info['lost'], info['tie']))
    return team_result, team_sort


def save_sort_bat_result_to_db(bat_name, result):
    """
    保持排好序的对战结果到数据库gamedata.db的表batgrade
    :param bat_name: 对战名
    :param result: list, get_result函数返回的tuple第二个数据，即拍好序的对战结果
    """
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")
    for sort_result in result:
        team = sort_result[0]
        sqlstr = "INSERT into batgrade (bat_name, team, grade, avg_score, win_count, lost_count, tie_count) " \
                 "values ('%s', '%s','%d', %.2lf, %d, %d, %d)" % \
                 (bat_name, team, sort_result[1], sort_result[2], sort_result[3], sort_result[4],
                  sort_result[5])
        result = dbmanager.execute(sqlstr)
    dbmanager.commit()


def cal_result(result):
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")
    sides = {}
    for team, info in result.items():
        sides[team] = 0
        for side, record in info.items():
            sides[team] += record['mask']
            sqlstr = "INSERT into bat (team, side, mask,score,win_count,lost_count,tie_count) values ('%s', '%s', %d, %d, %d, %d, %d)" % \
                     (team, side, record['mask'], record['score'], record['win'], record['lost'], record['tie'])
            result = dbmanager.execute(sqlstr)
            dbmanager.commit()
    for team, info in sides.items():
        sqlstr = "INSERT into bat (team, mask) values ('%s', %d)" % \
                 (team, info)
        result = dbmanager.execute(sqlstr)
        dbmanager.commit()


def cal_elo_result():
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")
    sqlstr = "SELECT red,blue,gameresult from batrecord"
    results = []
    brun = dbmanager.execute(sqlstr, results)
    return results


def save_attack_submarine_fire(*args, **kwargs):
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")

    if "attacker_type" in kwargs:
        attacker_type = kwargs["attacker_type"]
    if "attacker_dbid" in kwargs:
        attacker_dbid = kwargs["attacker_dbid"]
    if "attacker_name" in kwargs:
        attacker_name = kwargs["attacker_name"]
    if "attacker_lon" in kwargs:
        attacker_lon = kwargs["attacker_lon"]
    if "attacker_lat" in kwargs:
        attacker_lat = kwargs["attacker_lat"]
    if "weapon_id" in kwargs:
        weapon_id = kwargs["weapon_id"]
    if "weapon_range" in kwargs:
        weapon_range = kwargs["weapon_range"]
    if "attacker_head" in kwargs:
        attacker_head = kwargs["attacker_head"]
    if "attacker_speed" in kwargs:
        attacker_speed = kwargs["attacker_speed"]
    if "sub_dbid" in kwargs:
        sub_dbid = kwargs["sub_dbid"]
    if "sub_lon" in kwargs:
        sub_lon = kwargs["sub_lon"]
    if "sub_lat" in kwargs:
        sub_lat = kwargs["sub_lat"]
    if "sub_depth" in kwargs:
        sub_depth = kwargs["sub_depth"]
    if "sub_speed" in kwargs:
        sub_speed = kwargs["sub_speed"]
    if "sub_head" in kwargs:
        sub_head = kwargs["sub_head"]
    if "distance" in kwargs:
        distance = kwargs["distance"]
    if "fire_time" in kwargs:
        fire_time = kwargs["fire_time"]
    if "fire_record_time" in kwargs:
        fire_record_time = kwargs["fire_record_time"]
    else:
        fire_record_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    result = 0
    result_time = 0
    result_record_time = ""
    sqlstr = "INSERT INTO attack_submarine (attacker_type, attacker_dbid, attacker_name, attacker_lon, attacker_lat, " \
             "weapon_id, weapon_range, attacker_head, attacker_speed, sub_dbid, sub_lon, sub_lat, sub_depth,sub_head," \
             "sub_speed, distance, result, fire_time, result_time, fire_record_time, result_record_time) VALUES " \
             "('%s', %d, '%s', %.5lf, %.5lf, %d, %.3lf, %.1lf, %.2lf, %d, %.5lf, %.5lf, %.2lf, %.1lf, %.3lf,%.3lf,%d," \
             "%d, %d, '%s', '%s')" % (
                 attacker_type, attacker_dbid, attacker_name, attacker_lon, attacker_lat, weapon_id, weapon_range, \
                 attacker_head, attacker_speed, sub_dbid, sub_lon, sub_lat, sub_depth, sub_head, sub_speed, distance, \
                 result, fire_time, result_time, fire_record_time, result_record_time)

    result = dbmanager.execute(sqlstr)
    dbmanager.commit()

    if result:
        sql_str = "SELECT max(ID) FROM attack_submarine"
        result_id = []
        result = dbmanager.execute(sql_str, result_id)
        if result:
            for row in result_id:
                if row[0] is not None:
                    return row[0]
    return None


def save_attack_submarine_result(*args, **kwargs):
    """
    保存打击潜艇结果
    :param args:
    :param kwargs:
    :return:
    """
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")

    if "ID" in kwargs:
        ID = kwargs["ID"]
    else:
        return 0

    if "result_time" in kwargs:
        result_time = kwargs["result_time"]
    else:
        return 0

    if "result" in kwargs:
        result = kwargs["result"]
    else:
        return 0

    if "fire_record_time" in kwargs:
        result_record_time = kwargs["fire_record_time"]
    else:
        result_record_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    sqlstr = "UPDATE attack_submarine SET result=%d, result_time=%d, result_record_time='%s' WHERE ID = %d" % (
        result, result_time, result_record_time, ID
    )
    result = dbmanager.execute(sqlstr)
    dbmanager.commit()


def get_max_round():
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")

    sql_str = "SELECT max(MaxRound) FROM detectmissileround"
    result_id = []
    result = dbmanager.execute(sql_str, result_id)
    if result:
        for row in result_id:
            if row[0] is not None:
                return int(row[0])
    return 0


def set_max_round(round):
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")

    sql_str = "UPDATE detectmissileround SET MaxRound = %d where ID = 1" % round
    result_id = []
    result = dbmanager.execute(sql_str)
    dbmanager.commit()


def save_fire(*args, **kwargs):
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")

    round = 1
    if "Round" in kwargs:
        round = kwargs["Round"]
    missileIndex = 1
    if "MissileIndex" in kwargs:
        missileIndex = kwargs["MissileIndex"]
    if "DetectTargetTime" in kwargs:
        DetectTargetTime = kwargs["DetectTargetTime"]
    if "FiredTime" in kwargs:
        FiredTime = kwargs["FiredTime"]
    if "FiredUnitName" in kwargs:
        FiredUnitName = kwargs["FiredUnitName"]
    if "FiredUnitGuid" in kwargs:
        FiredUnitGuid = kwargs["FiredUnitGuid"]
    if "TargetUnitID" in kwargs:
        TargetUnitID = kwargs["TargetUnitID"]
    if "TargetUnitName" in kwargs:
        TargetUnitName = kwargs["TargetUnitName"]
    if "FireLon" in kwargs:
        FireLon = kwargs["FireLon"]
    if "FireLat" in kwargs:
        FireLat = kwargs["FireLat"]
    if "TargetLon" in kwargs:
        TargetLon = kwargs["TargetLon"]
    if "TargetLat" in kwargs:
        TargetLat = kwargs["TargetLat"]

    fire_record_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sqlstr = "INSERT INTO detectmissile (Round, MissileIndex, DetectTargetTime, FiredTime, FiredUnitName, " \
             "FiredUnitGuid, TargetUnitID, TargetUnitName, FireLon, FireLat, TargetLon, TargetLat, FireMyTime) VALUES " \
             "(%d, %d, %.11f, %.1lf, '%s', '%s', '%s', '%s', %.5lf, %.5lf, %.5lf, %.5lf, '%s')" % (
                 round, missileIndex, DetectTargetTime, FiredTime, FiredUnitName, FiredUnitGuid, TargetUnitID, \
                 TargetUnitName, FireLon, FireLat, TargetLon, TargetLat, fire_record_time)

    result = dbmanager.execute(sqlstr)
    dbmanager.commit()


def save_detect(*args, **kwargs):
    de_record_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    global dbmanager
    if dbmanager is None:
        dbmanager = DbManage("data/gamedata.db")

    round = 1
    if "Round" in kwargs:
        round = kwargs["Round"]
    missileIndex = 1
    if "MissileIndex" in kwargs:
        missileIndex = kwargs["MissileIndex"]
    if "DetectMissileTime" in kwargs:
        DetectMissileTime = kwargs["DetectMissileTime"]
    if "DetectMissileUnit" in kwargs:
        DetectMissileUnit = kwargs["DetectMissileUnit"]
    if "DetectMissileSensor" in kwargs:
        DetectMissileSensor = kwargs["DetectMissileSensor"]

    if "DetectMissileUnitLon" in kwargs:
        DetectMissileUnitLon = kwargs["DetectMissileUnitLon"]
    if "DetectMissileUnitLat" in kwargs:
        DetectMissileUnitLat = kwargs["DetectMissileUnitLat"]
    if "DetectMissileUnitAlt" in kwargs:
        DetectMissileUnitAlt = kwargs["DetectMissileUnitAlt"]

    if "DetectLon" in kwargs:
        DetectLon = kwargs["DetectLon"]
    if "DetectLat" in kwargs:
        DetectLat = kwargs["DetectLat"]
    if "DetectAlt" in kwargs:
        DetectAlt = kwargs["DetectAlt"]

    d_record_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sqlstr = 'UPDATE detectmissile SET DetectMissileTime=%.1lf, DetectMissileUnit="%s", DetectMissileSensor="%s",' \
             'DetectMissileUnitLon=%.5lf, DetectMissileUnitLat=%.5lf,DetectMissileUnitAlt=%.1lf,DetectLon=%.5lf, ' \
             'DetectLat=%.5lf,DetectAlt=%.1lf,DetectMyTime="%s" ' \
             'WHERE Round=%d and MissileIndex=%d' % (
                 DetectMissileTime, DetectMissileUnit, DetectMissileSensor, DetectMissileUnitLon, DetectMissileUnitLat,
                 DetectMissileUnitAlt, DetectLon, DetectLat, DetectAlt, d_record_time,
                 round, missileIndex)

    result = dbmanager.execute(sqlstr)
    dbmanager.commit()
