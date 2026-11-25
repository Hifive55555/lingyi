# -*- coding:utf-8 -*-

import os
import sqlite3


class DbManage(object):
    def __init__(self, db_path, logger=None):
        self.log = logger
        ret = os.path.exists(db_path)
        self._dbPath = db_path
        self._conn = None    #连接对像
        self._cur = None     #游标
        if not ret:
            if self.log is not None:
                self.log.info('数据库文件不存在 路径为:%s' % db_path)
            else:
                print('数据库文件不存在 路径为:%s' % db_path)
            return
        self.get_connect()

    def close_connect(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            self._cur = None

    def __del__(self):
        """
        析构函数
        :return:
        """
        self.close_connect()
        if self.log is not None:
            self.log.info("DBManager,析构函数执行,数据库连接已断开。")
        else:
            print("DBManager,析构函数执行,数据库连接已断开。")

    def get_connect(self):
        """取得数据库连接"""
        ret = True
        try:
            if self._conn is None:
                self._conn = sqlite3.connect(self._dbPath, check_same_thread=False)
                self._cur = self._conn.cursor()
        except Exception as e:
            if self.log is not None:
                self.log.error(str(e))
            else:
                print(e)
            ret = False
            self._conn.rollback()
        finally:
            return ret        

    def execute(self, sql_str, list_data=None):
        """
        去掉SQL语句前后的空白字符串 否则如果SQL语句前含有空格在区分是否为查询语句时失败
        :param sql_str:
        :param list_data:
        :return:
        """
        if list_data is None:
            list_data = []
        list_word = sql_str.strip().split(" ")
        ret = True     
        """取得数据库连接"""
        try:
            if self._conn is None:
                self.get_connect()
            self._cur.execute(sql_str)
            if list_word[0].lower() in ['select', 'pragma']:
                for item in self._cur.fetchall():
                    list_data.append(item)
        except Exception as e:
            if self.log is not None:
                self.log.error("执行Sql语句失败：{0} 异常信息为 {1}".format(sql_str, e))
            else:
                print("执行Sql语句失败：{0} 异常信息为 {1}".format(sql_str, e))
            ret = False
            self._conn.rollback()
        finally:
            return ret

    def commit(self):
        self._conn.commit()
        
    
if __name__ == '__main__':
    pass
