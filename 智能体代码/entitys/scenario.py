# -*- coding:utf-8 -*-

from .global_util import *
from .element import Element


class Scenario(Element):
    """
    想定操作类
    """

    def __init__(self, guid, name, side_name):
        Element.__init__(self, guid, name, side_name, ElementType.Scenario)
        # THFeatureOption,THEventTriggerColl等结构定义请查看entitys/struct.proto文件
        # THScenarioInfo结构中属性：
        self.ScenarioID = ""  # 想定ID
        self.Title = ""  # 想定名称
        self.Description = ""  # 想定描述
        self.FileName = ""  # 文件名称
        self.MetaComplexity = 0  # 复杂度
        self.MetaDifficulty = 0  # 难度
        self.MetaScenSetting = ""  # 位置
        self.PostureColor = ""  # 推演方颜色配置
        self.StartTime = ""  # 开始仿真时间(单位：毫秒)
        self.Duration = 0  # 仿真时长（单位：秒）   1
        self.FeatureOption = {}  # 场景功能设置--结构：THFeatureOption

        # THEventColl结构中属性：
        self.EventTriggers = {}  # 事件触发器--结构：THEventTriggerColl
        self.EventConditions = {}  # 事件条件--结构：THEventConditionColl
        self.EventActions = {}  # 事件行动--结构：THEventActionColl
        self.SimEvents = {}  # 推演事件---结构：dict:<string, THSimEvent>，key:想定设置的事件guid

        # THSituationInfo结构中属性：
        self.Time = ""  # 当前仿真时间(单位：毫秒)
        self.Status = ""  # 仿真状态 "RUN", "DURPAUSE"  "PAUSE"  "END"
        self.LoadTime = ""  # 加载想定时的电脑时间(单位：毫秒)，用于区分仿真的标识（服务器重启自动加载的此值一样）
        self.RecordTime = ""  # 仿真录制时间
        self.Speed = 0  # 推演速度
        self.Seed = 0  # 随机种子(引擎中没找到该值)
        self.FirstRunTime = ""  # 首次点击运行按钮时间(单位：毫秒)
        self.NonActiveUnits = {}  # 爆炸、箔条云、武器撞击或炮弹等非活动实体单--结构：THNonActiveUnitColl
        self.WeatherModel = 0  # 天气模式
        self.WeatherProfile = {}  # 天气配置--结构：THWeatherProfile
        self.Resolution = 0  # 仿真步长(单位:毫秒)
        # self.VitalChange = {}  # 全局关键变化数据--结构：THVitalChange  20250703版态势协议已取消
        self.ReferencePoints = {}  # 全局参考点集

