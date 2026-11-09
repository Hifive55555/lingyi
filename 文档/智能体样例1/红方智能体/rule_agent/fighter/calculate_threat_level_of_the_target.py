# Author: MouQingPing

import math
import numpy as np
EARTH_RADIUS = 6371137  # 地球平均半径
degree2radian = math.pi / 180.0

class ThreatEvaluator():
    def __init__(self):
        """
        5个权重因子，各因素权重 可自定义
        权重：
            self.w_type = 0.3           类别威胁权重
            self.w_distance = 0.25      距离威胁权重
            self.w_heading = 0.2        航向意图威胁权重
            self.w_speed = 0.1          速度威胁权重
            self.w_alt = 0.1            高度威胁权重
        """
        self.w_type = 0.3
        self.w_distance = 0.25
        self.w_heading = 0.2
        self.w_speed = 0.1
        self.w_alt = 0.1

    def get_horizontal_distance(self,lon1,lat1,lon2,lat2):
        """
         求地面两点的水平距离   Haversine公式
         参数：
                lon1,lat1：单元1的经纬度
                lon2,lat2：单元2的经纬度
         返回：
                单元1与单元2之间的距离，float，单位：海里
        """
        geopoint1 = [lat1, lon1]
        geopoint2 = [lat2, lon2]
        try:
            lat1 = geopoint1[0] * degree2radian
            lon1 = geopoint1[1] * degree2radian
            lat2 = geopoint2[0] * degree2radian
            lon2 = geopoint2[1] * degree2radian
        except Exception as e:
            print("distance error:{},{},{}".format(geopoint1, geopoint2, e))
            return 0.0

        difference = lat1 - lat2
        mdifference = lon1 - lon2
        distance = 2 * math.asin(math.sqrt(math.pow(math.sin(difference / 2), 2)
                                           + math.cos(lat1) * math.cos(lat2)
                                           * math.pow(math.sin(mdifference / 2), 2)))
        distance = distance * EARTH_RADIUS / 1000
        distance /= 1.825   #千米转海里
        return distance


    def get_dmax_by_type(self,aircraft_type):
        """
            获得最大威胁距离
            参数：
                aircraft_type：飞机的类别
            返回：
                飞机类别对应的最大威胁距离
        """

        dmax_dict = {
            'fighter':202,  #战斗机，最大威胁距离,自定义，假设现在打击目标与我方目标之间的最大距离为202海里
            'bomber':32.4,    #轰炸机，32.4海里(一般是投弹或者远程滑翔炸弹）
            'uav':21.6,       #无人机，21.6海里(携带小型武器或者侦察作用)
            'awacs':54,         #预警机，54海里(不具备攻击能力)
            'uknown':27,    #未知类型保守估计，27海里
        }
        return dmax_dict.get(aircraft_type.lower(),50000)

    def distance_threat(self,d,dmax):
        """
            计算距离威胁度D
            参数：
                d：我方单元与敌方单元距离
                dmax：敌方单元构成的最大威胁距离，超出这个距离就不被是为威胁，或者威胁为0
            返回：
                距离威胁度
        """
        return max(0.0,1-d/dmax)

    def alt_threat(self,target_alt,self_alt):
        """
            计算高度威胁度A  高打低有优势
            参数：
                self_alt：我方单元高度
                target_alt：敌方单元高度
            返回：
                高度威胁度
        """
        ah = target_alt - self_alt #高度差（单位：米）

        if ah < -3000:
            return 0.2 #敌机低很多，威胁较低
        elif -3000<= ah < 3000 :
            return 1.0 #高度接近，威胁较大
        elif ah > 3000:
            return 0.6 #敌机高出较多，威胁较低

    def heading_threat(self,target_pos_lon,target_pos_lat,target_heading,self_pos_lon,self_pos_lat):
        """
            判断目标的航向是否朝我方
            参数：
                target_pos_lon:目标经度
                target_pos_lat:目标纬度
                target_heading:航向角，0-360，正北为0
                self_pos_lon:我方单元经度
                self_pos_lat:我方单元纬度
            返回：
                1：朝向我方（45°)
                0:不是朝向我方
        """
        lon1, lat1 = math.radians(target_pos_lon), math.radians(target_pos_lat)
        lon2, lat2 = math.radians(self_pos_lon), math.radians(self_pos_lat)

        dlon = lon2 - lon1

        # 计算从目标指向我方的方位角(hearing)
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - \
            math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        angle_to_self = (math.degrees(math.atan2(y, x)) + 360) % 360

        # 计算角度差
        angle_diff = abs(angle_to_self - target_heading) % 360
        if angle_diff > 180:
            angle_diff = 360 - angle_diff  # 取较小角

        return 1 if angle_diff <= 45 else 0

    def speed_threat(self,target_speed,self_speed):
        """
            计算敌方单元速度威胁 速度越快威胁越大
            参数：
                target_speed:目标速度
                self_speed:我方单元速度
            返回：
                速度威胁度
        """
        if target_speed > self_speed:
            return 0.5
        elif target_speed > self_speed * 0.8:
            return 0.25
        elif target_speed > self_speed * 0.7:
            return 0.15
        elif target_speed > self_speed * 0.6:
            return 0.10
        elif target_speed > self_speed * 0.5:
            return 0.05
        else:
            return 0.0

    def get_air_type(self,air_type):
        """
            获得飞机类别分类
            参数：
                air_type:态势中的飞机单元分类
            返回：
                态势飞机的分类
        """
        if air_type == 3101:
            # 轰炸机
            aircraft_type = 'bomber'
        elif air_type == 4002 or air_type == 4003:
            # 预警机、指挥机 （ACP）
            aircraft_type = 'awacs'
        elif air_type == 4001 or 7003 <= air_type <= 7005:
            # 电子情报（Electronic Intelligence)、电子战、侦察、区域监视、海上巡逻
            aircraft_type = 'elint'
        elif air_type == 8001:
            # 加油机
            aircraft_type = 'tanker'
        elif air_type == 3001 or air_type == 3002:
            # 攻击机、防空压制
            aircraft_type = 'attack'
        elif air_type == 2001 or air_type == 2002 or air_type == 3401:
            # 战斗机、多用途飞机、战场空中拦截（BAI/ CAS）  2001 2002 3401
            aircraft_type = 'fighter'
        elif air_type == 6001:
            # 反潜作战
            aircraft_type = 'asw'
        elif air_type == 8201 or air_type == 8202:
            # 无人机、无人作战飞行器
            aircraft_type = 'uav'
        else:
            aircraft_type = "unknown"
        return aircraft_type

    def type_threat(self,aircraft_type):
        """
            根据目标的价值得分表计算出的目标类型威胁度字典type_threat_dict
            威胁度字典可自定义

            参数：
                aircraft_type:飞机类别
            返回：
                飞机类别对应的类别威胁度
        """
        type_threat_dict = {
            'bomber': 1,        # 轰炸机
            'awacs':0.42,       # 预警机
            'elint': 0.51,      # 电子情报（Electronic Intelligence)、电子战、侦察、区域监视、海上巡逻
            'tanker': 0.41,     # 加油机
            'attack': 0.125,    # 攻击机
            'fighter':0.15,     # 战斗机、多用途飞机
            'asw':0.0625,       # 反潜作战
            'uav':0.05          # 无人机
        }
        return type_threat_dict.get(aircraft_type.lower(),0.5)  #默认威胁值设置为0.5

    def compute_threat(self,target_unit,self_unit):
        """
            单个目标对应单个单元的威胁度计算
            参数：
               target_unit:目标单元字典
               self_unit:我方单元字典
            返回：
                目标对于我方单元的威胁度
        """

        #距离威胁
        distance = self.get_horizontal_distance(target_unit['lon'],target_unit['lat'],
                                              self_unit['lon'],self_unit['lat'])
        aircraft_type = self.get_air_type(target_unit['aircraft_type'])
        dmax = self.get_dmax_by_type(aircraft_type)
        distance_rate = self.distance_threat(distance,dmax)

        #高度威胁
        alt_rate = self.alt_threat(target_unit['alt'],self_unit['alt'])

        #朝向威胁
        head_rate = self.heading_threat(target_unit['lon'],target_unit['lat'],target_unit['head'],self_unit['lon'],self_unit['lat'])

        #速度威胁
        speed_rate = self.speed_threat(target_unit['speed'], self_unit['speed'])

        #类型价值威胁
        type_rate = self.type_threat(aircraft_type)

        total_threat_rate = self.w_distance * distance_rate + self.w_alt * alt_rate + \
            self.w_heading * head_rate + self.w_speed * speed_rate + self.w_type * type_rate
        return round(min(max(total_threat_rate,0.0),1.0),3)

    def threat_matrix(self,targets,self_units):
        """
            计算目标-威胁矩阵
            参数：
               targets:目标单元字典集合
               self_units:我方单元字典集合
            返回：
                例如:
                0.2 0.4 0.4
                0.1 0.5 0.6
                2*3矩阵表示，目标1和目标2对于我方单元1、单元2、单元3的威胁度
                行对应目标，列对应我方单元，可对应查出目标与单元的威胁度
        """
        matrix = np.zeros((len(targets),len(self_units)))
        for i,target in enumerate(targets):
            for j,self_unit in enumerate(self_units):
                matrix[i][j] = self.compute_threat(target,self_unit)
        return matrix

    def get_target_unit_relationship(self,matrix,w_threat_threshold,show_flag=False):
        """
        根据目标-威胁矩阵显示目标、我方单元的关系
            参数：
               matrix：威胁度矩阵
               w_threat_threshold:威胁阈值
               show_flag:是否显示威胁矩阵、敌我双方基于威胁阈值的威胁关系
            返回：
                目标对于我方单元基于威胁阈值的索引字典
            例如:
            {0: [0, 1, 2, 3, 4], 1: [0, 1, 2, 3, 4], 2: [], 3: [], 4: [], 5: [2]}
            key值是我方单元索引id，value值是敌方目标的索引id
            0: [0, 1, 2, 3, 4]表示我方单元0和敌方目标0、1、2、3、4的威胁度阈值超过w_threat_threshold，建议开火
        """
        thread_per_self_unit = {
            i:np.where(matrix[:,i]>w_threat_threshold)[0].tolist()
            for i in range(matrix.shape[1])
        }
        if show_flag:
            print("威胁矩阵（targets x self_units):\n", matrix)
            for unit_id,targets in thread_per_self_unit.items():
                if len(targets)>0:
                    print("\n每个我方单元对应的威胁目标ID:")
                    print(f"我方单元{unit_id}：目标id {targets}")
        return thread_per_self_unit

