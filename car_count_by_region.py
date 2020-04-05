import copy
import time
import json

id_str = 'id'
total_count_str = 'total_count'
car_type_dict_str = 'car_type_dict'

# 以指定节点为根节点形成生成树
# root_node:根节点，cpn_num：拓扑节点总数
def spanningTree(self, id, adjDirection, root_node, cpn_num):
    # init
    # 生成树节点标识
    Flag = False
    # 用于判断计算是否结束的END计数器
    End_Counter = 0
    # 父节点方向
    parentdirection = []
    # 子节点方向
    childdirection = []
    # END计数器初始化为邻居数量
    End_Counter = [1] * len(adjDirection)
    # 与邻居通信的数据格式，分别为邻居的方向、BFS信号、END信号
    data_base = [0, False, 0]
    # 本地给不同邻居的数据数组
    data = []

    # 初始化data，每一个邻居方向都进行初始化
    for i in range(len(adjDirection)):
        data_base_temp = [0, False, 0]
        data_base_temp[0] = adjDirection[i]
        data.append(data_base_temp)

    # id为1的为发起节点
    if id == root_node:
        Flag = True
        parentdirection.append(0)  # 假定一个0方向，父节点方向为0的即为根节点/发起节点
        for i in range(len(data)):
            data[i][1] = True  # 给每个邻居发送BFS信号

    # 循环次数为网络规模的2倍，5  *2 = 10
    for m in range(2 * cpn_num):
        self.syncNode()  # 同步异步通信函数
        time.sleep(0.1)  # 异步通信函数前sleep一段时间防止通信数据覆盖写入
        for i in range(len(data)):
            self.sendDataToDirection(data[i][0], data[i][1:])  # 只传给邻居BFS和END信号
        self.syncNode()  # 同步异步通信函数
        adjData_fb = copy.deepcopy(self.adjData)  # 获取邻居传输的数据
        adjDirection_fb = adjDirection  # 获取邻居的方向数组

        # 清空BFS、END信号
        for i in range(len(data)):
            data[i][1] = False
            data[i][2] = 0

        # 如果END计数器不为0
        if sum(End_Counter) != 0:
            for i in range(len(adjData_fb)):
                # 如果邻居传来BFS信号
                if adjData_fb[i][0] == True:
                    # 如果本节点没有加入宽度优先生成树中
                    if Flag == False:
                        Flag = True
                        parentdirection.append(adjDirection_fb[i])  # 将邻居方向加入父节点方向
                        # 向其他邻居广播BFS信号
                        for j in range(len(data)):
                            if data[j][0] != adjDirection_fb[i]:
                                data[j][1] = True
                    End_Counter[i] = 0

                # 如果邻居传来END信号
                if adjData_fb[i][1] > 0:
                    End_Counter[i] = 0
                    # END = 2 说明是该节点的子节点，将邻居方向加入父节点方向数组
                    if adjData_fb[i][1] == 2:
                        childdirection.append(adjDirection_fb[i])

            # 如果本轮END计数器减为0
            if sum(End_Counter) == 0:
                for i in range(len(data)):
                    data[i][1] = False
                    # 给父节点方向的邻居发送END = 2
                    if data[i][0] == parentdirection[0]:
                        data[i][2] = 2
                    # 给其他邻居发送END = 1
                    else:
                        data[i][2] = 1
    # 返回父节点方向、子节点方向
    value = [parentdirection, childdirection]
    return value

def count_region(self, id, adjDirection, datalist, parentdirection, childdirection):
    adjid = copy.deepcopy(datalist[0])  #邻居节点ID
    information = copy.deepcopy(datalist[1]) #4个车位状态
    # information = SimulationInterface.getCarStatus(1, id) # 获取节点下的车辆信息
    car_type = copy.deepcopy(datalist[2])
    # car_type = SimulationInterface.getAreaType(id)  # 从数据库获取节点区域类型：A, B, C, D
    seek_id = copy.deepcopy(datalist[-1])
    # seek_id = SimulationInterface.getNodeType(id)  # 从数据库获取节点类型： 出入口，其他
    exchangedata_origin = copy.deepcopy(self.adjData) 
    calcu_flag = 0 
    return_id = -1  
    self.syncNode()
    self.sendUDP(str(id) + "号节点就绪")
    data = None
    data_dict = None
    
    if parentdirection and parentdirection[0] == 0:  
        parent_flag = 1
        parent_i = []
    else:
        parent_flag = 0  
        parent_i = parentdirection[0]

    if childdirection: 
        son_flag = 0 
        son_i = childdirection 
    else:
        son_flag = 1
        son_i = []

    if parent_flag == 1:  # 根节点
        time_out = 0
        flag = [1] * len(son_i)  
        while (sum(flag)) and (time_out < 50):
            time.sleep(0.1)      
            time_out += 1        
            for j in range(len(son_i)):
                i = son_i[j] - 1       
                if exchangedata_origin[i] != self.adjData[i]:    
                    flag[i] = 0

        if time_out < 50 :
            adj_result_sum = 0
            car_type_count = dict()
            car_type_count[car_type] = len(information)
            for i in range(len(son_i)):
                son_adj = son_i[i] - 1
                adj_result_sum += self.adjData[son_adj][1]

                if not self.adjData[son_adj][2]:
                    continue
                    
                for key, value in self.adjData[son_adj][2].items():
                    if key in car_type_count:
                        car_type_count[key] += value
                    else:
                        car_type_count[key] = value
            # data_dict=[id, len(information)+adj_result_sum, car_type_count]
            data_dict=[id, "total car count: " + str(len(information)+adj_result_sum), car_type+" region car count:" + str(car_type_count[car_type])]
            self.sendUDP("************************通过")
        else:
            self.sendUDP(str(id) + "************************超时")
    elif son_flag == 1: # 末尾节点
        car_type_count = dict()
        car_type_count[car_type] = len(information)
        data_dict = [id, len(information), car_type_count]
        self.sendUDP(str(id) + "parent" + str(parent_i) + "testeteest" + json.dumps(data_dict))
        self.sendDataToDirection(adjDirection[parent_i-1], (data_dict))
    else:
        time_out = 0
        flag = [1] * len(son_i)
        while (sum(flag)) and (time_out < 50):  
            time.sleep(0.1)
            time_out += 1
            for i in range(len(son_i)):
                if exchangedata_origin[son_i[i] - 1] != self.adjData[son_i[i] - 1]:    
                    flag[i] = 0  

        if time_out < 50:
            adj_result_sum = 0
            car_type_count = dict()
            car_type_count[car_type] = len(information)

            for j in range(len(son_i)):
                i = son_i[j] - 1
                if self.adjData[i]:
                    adj_result_sum += self.adjData[i][1]

                    if not self.adjData[i][2]:
                        continue
                    
                    for key, value in self.adjData[i][2].items():
                        if key in car_type_count:
                            car_type_count[key] += value
                        else:
                            car_type_count[key] = value
            data_dict=[id, len(information)+adj_result_sum, car_type_count]
            self.sendDataToDirection(adjDirection[parent_i -1], (data_dict))
        else:
            self.sendUDP(str(id) + "************************超时")
        
    self.sendUDP(str(id) + "号节点完成")
    value=[json.dumps(data_dict), parent_i, son_i]
    return value

def taskFunction(self, id, adjDirection, datalist):
    root_node = 3
    cpn_num = 10 # 我们的拓扑是10个节点
    tree_value = spanningTree(self, id, adjDirection, root_node, cpn_num)

    value = count_region(self, id, adjDirection, datalist, tree_value[0], tree_value[1])
    return value
