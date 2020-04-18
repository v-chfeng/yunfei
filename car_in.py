import copy
import time
import datetime
import random
import math
import SimulationInterface
from enum import Enum, unique

@unique
class CarType(Enum):
    little = 1  # 小型车
    big = 2     # 大客车


@unique
class UserType(Enum):
    vip = 1     # vip用户
    normal = 2  # 普通用户


@unique 
class DayOrNight(Enum):
    day = 1     # 白天
    night = 2   # 夜晚


def get_price(start_time, end_time, car_lic):
    """  
        计算停车费
        可以根据车牌，停车时间，找到存储的用户信息，车辆信息，及白天黑夜
    """
    # unit_price, unit = get_unit_price(UserType.vip, CarType.little, DayOrNight.day)#调用子函数计算停车计费的单价
    unit_price, unit = SimulationInterface.get_unit_price(UserType.vip.value -1, CarType.little.value-1, DayOrNight.day.value-1)#调用子函数计算停车计费的单价
    time_delta = end_time - start_time
    return math.ceil(time_delta.total_seconds() / 3600 / unit) * unit_price

def get_unit_price(user_type, car_type, day_or_night):
    """
        计算单价
        返回价钱，及单位--30mins, 60mins
    """
    price_table = generate_price_table()
    
    user_i = user_type.value - 1
    car_i = car_type.value - 1
    day_i = day_or_night.value - 1
    unit_price = price_table[user_i][car_i][day_i]

    if day_or_night == DayOrNight.day:
        unit = 3   # 30分钟
    else:
        unit = 6   # 60 分钟
    return unit_price, unit


def generate_price_table():
    # vip
    vip_price_table = list()
    vip_little_car = [1, 0.5]  # 白天， 夜晚
    vip_big_car = [2, 1]  # 白天，夜晚
    vip_price_table.append(vip_little_car)
    vip_price_table.append(vip_big_car)

    normal_price_table = list()
    normal_little_car = [2, 1]  # 白天，夜晚
    normal_big_car = [3, 1.5]  # 白天，夜晚

    normal_price_table.append(normal_little_car)
    normal_price_table.append(normal_big_car)

    price_table = list()
    price_table.append(vip_price_table)
    price_table.append(normal_price_table)
    return price_table


def taskFunction(self, id, adjDirection, datalist):
    adjid = copy.deepcopy(datalist[0])  #邻居节点ID
    floor_id = 1
    carport_status = copy.deepcopy(datalist[1])  #4个车位状态
    car_information = [[]] * len(carport_status) #4个车信息
    # seek_id = copy.deepcopy(datalist[-1]) ## 获取节点类型，出口，入口，中间节点
    seek_id = SimulationInterface.getNodeType(id)  # 从数据库获取节点的类型
    exchangedata_origin = copy.deepcopy(self.adjData) #存储邻居传来的数据信息
    #flag = [1] * len(self.adjData)  # 设定flag为全是0的数组
    #calcu_flag = 0 #计算标识位
    #return_id = -1  #标识为设定为-1
    self.syncNode()
    self.sendUDP(str(id) + "号节点就绪")

    # writeData = []
    # 数据库读操作
    car_fee, car_lic= SimulationInterface.dataForCar(floor_id)

    if not car_lic: # 如果没有获取到车牌信息，就直接结束
        return 

	# 子节点，父节点对应方向   #计算拓扑结构CPN的子节点和父节点
    if self.parentID == id:  #如果父节点等于id  即没有父节点为根节点
        parent_flag = 1   #令 parent_flag = 1
    else:
        parent_flag = 0  #有父节点  令 parent_flag = 0
        for i in range(len(adjDirection)):  #i从0到端口数循环
            if self.parentID == adjid[i]:  #找到父节点id所对应的端口
                parent_i = i               #并赋值（记录父节点所对应的端口在adjDirection里的位置）
    if self.sonID: #%如果该节点有子节点  self.sonID存储本节点的子节点ID
        son_flag = 0 #令son_flag = 0
        son_i = [0] * len(self.sonID)             #son_i存储的是子节点所对应的方向在adjDirection 将son_i置为全是0的数组
        for i in range(len(self.sonID)):          #遍历所有子节点
            for j in range(len(adjDirection)):  #子节点j从0遍历所有节点端口i
                if self.sonID[i] == adjid[j]:   #adjid存储的是本节点的邻居节点，其位置和adjDirection一一对应。
                    son_i[i] = j  #这两个嵌套for循环是为了找到本节点的子节点所对应的端口在adjDirection数组里的位置，即j。adjDirection[j]即为第i个子节点所对应的端口
    else:
        son_i = []
        son_flag = 1  #没有子节点

    #初始化要输出的信息
    car_info = None
    parking_fee = None
    car_dict = None

    # 这是入口的节点
    if seek_id == 1:
        i = 0
        current_car_count = 2  # 应该是通过另一个task获取
        total_car_count = 5    # 应该是通过另一个task获取
        car_info=[0,0,0] #[车牌信息，进入时间，离开时间]
        # car_lic= f"#{i}#" + str(int(random.random() * pow(10, 8)))  # 获取车牌信息

        car_start = datetime.datetime.strftime(datetime.datetime.now(),r"%y-%m-%d %H:%M:%S")
        car_info[0]=car_lic
        car_info[1]=car_start
        car_dict = {}
    
        if current_car_count < total_car_count:
            # current_car_count:现在车库中车的数量
            # total_car_count： 车库中车的总数量
            # 保存车辆信息
            car_dict[car_lic] = car_info

            SimulationInterface.save_input_car_license_number(car_lic, car_start)
        else:
            self.sendUDP(str(id)+ f"号：车库已满，车辆-{car_lic}不能进库!")
            return car_info
    else:
        self.sendUDP(str(id) + "无需操作")

    self.sendUDP(str(id) + "号节点完成")
    value = car_dict
    return value
