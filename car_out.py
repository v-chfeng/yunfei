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
    return math.ceil(time_delta.total_seconds() / 60 / unit) * unit_price

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

    # 这是入口的节点
    if seek_id == 1:
        time_out = 0
        while time_out < 60:   #当flag和有值 并且time_out<60
            time.sleep(0.1)      #时间间隔为1
            time_out += 1        #time_out =time_out+1
            match = False
            for i in range(len(self.adjData)):       #收到所有邻居节点信息
                if exchangedata_origin[i] != self.adjData[i]: 
                    if not self.adjData[i][1]: # 如果开始时间为空，回传该车辆的开始时间
                        car_license = self.adjData[i][0]
                        if not car_license:  # 如果没有车牌号，则跳过
                            continue

                        start_datetime = SimulationInterface.get_input_datetime(car_license)  # 获取该车牌号的入库时间
                        car_info = [0, 0, 0]
                        car_info[0]= car_license
                        car_info[1] = datetime.datetime.strftime(start_datetime,r"%y-%m-%d %H:%M:%S")
                        for j in range(len(son_i)):
                            self.sendDataToDirection(adjDirection[son_i[j]], car_info)

                        match = True

            if match:
                break
                        
    elif seek_id == -1:  # 出口
        # 随机找一辆入库的车，待该车停车后，10秒后开始出库
        out_car_info = None

        car_license = SimulationInterface.get_random_car_license()
        self.sendUDP('出口的车牌号'+str(car_license))

        if car_license:  # 若车牌号存在，则退出
            # time.sleep(10)   # 车辆停的时间
            time_out = 0
            out_car_info = [0, 0, 0]
            out_car_info[0] = car_license
            out_car_info[2] = "out"
            self.sendDataToDirection(adjDirection[parent_i], out_car_info)
            while time_out < 60:
                time.sleep(0.1)
                time_out += 1
                for i in range(len(self.adjData)):
                    if exchangedata_origin[i] == self.adjData[i] or self.adjData[i][0] != out_car_info[0] \
                        or not self.adjData[i][1]:  # 没有收到入口节点发来的消息
                        continue
                    in_car_info = copy.deepcopy(self.adjData[i])
                    break
            
            if in_car_info: # 收到进车节点发来的消息
                # 计算停车费信息
                self.sendUDP('入口发来信息：1:' + str(in_car_info[0]) + "2:" + str(in_car_info[1]))
                start_datetime = datetime.datetime.strptime(in_car_info[1], r"%y-%m-%d %H:%M:%S")
                end_datetime = datetime.datetime.now()
                end_datetime_str = datetime.datetime.strftime(end_datetime, r"%y-%m-%d %H:%M:%S")
                in_car_info[2] = end_datetime.strftime(r"%y-%m-%d %H:%M:%S")
                delta_time = end_datetime - start_datetime
                parking_fee = get_price(start_datetime, end_datetime, in_car_info[0])  # 计算停车费
                SimulationInterface.saveCarFee(floor_id, parking_fee)  # 保存停车费到数据库
                SimulationInterface.save_out_time_and_parking_fee(car_license, end_datetime_str, parking_fee)
                car_info = in_car_info
    else:
        # 这是车位控制节点，控制4个车位，接收到停车信息，直接传给子节点。
        car_info = None
        time_out = 0    #赋值
        default_carport_status = [0] * len(carport_status) # 假定这是上一个车位状态
        while time_out < 60:
            # 入库
            time.sleep(0.1)      #时间间隔为1
            time_out += 1      #time_out =time_out+1
            for i in range(len(self.adjData)):
                if exchangedata_origin[i] == self.adjData[i]:  # 没有收到消息
                    continue
                if self.adjData[i][2]: # 如果出库节点请求开始时间
                    self.sendUDP(str(id) + "号请求开始时间")
                    self.sendDataToDirection(adjDirection[parent_i], copy.deepcopy(self.adjData[i]))  # 传给上级节点
                    continue
                
                # 将该停车信息也传给子节点，通知所有节点，有车进库
                for j in range(len(son_i)):
                    self.sendDataToDirection(adjDirection[son_i[j]], copy.deepcopy(self.adjData[i]))

    self.sendUDP(str(id) + "号节点完成")

    if parking_fee:
        value={"car_info": car_info, "parking_fee": parking_fee}
    else:
        value={"car_info": car_info}
	#value = [id, return_id, self.parentID, self.sonID]  #返回 [节点ID，货物所在节点ID，节点的父节点，节点的子节点]

    # writeData.append([room_id + (floor_id - 1) * 16, 6, room_id + (floor_id - 1) * 16 - 1, '002010022', 0, 0, 1, parking_fee])
    # 数据库写操作
    # SimulationInterface.controlModel(writeData)
    return value
