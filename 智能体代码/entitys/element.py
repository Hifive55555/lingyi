# -*- coding:utf-8 -*-

from abc import ABCMeta, abstractmethod


class Element(object):
    __metaclass__ = ABCMeta

    """
    元素类 飞机，舰船等作战单元，武器、传感器、天气实体，触发器对象等的基类
    """
    def __init__(self, guid, name, side_name, element_type):
        self.ID = guid
        self.Name = name
        self.Side = side_name
        self.ElementType = element_type
        self._game_server = None

    def delete_sub_object(self):
        """
        当删除本元素时，删除子对象
        返回需要先删除的子对象guid列表
        :return:
        """
        return []


