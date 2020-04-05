import copy
import time
import json
import SimulationInterface

id_str = 'id'
total_count_str = 'total_count'
car_type_dict_str = 'car_type_dict'

def taskFunction(self, id, adjDirection, datalist):
    adjid = copy.deepcopy(datalist[0])  #邻居节点ID
    information = copy.deepcopy(datalist[1]) #4个车信息
    # information = SimulationInterface.getCarStatus(1, id) # 获取节点下的车辆信息
    car_type = copy.deepcopy(datalist[2])  # 节点区域类型
    # car_type = SimulationInterface.getAreaType(id)  # 从数据库获取节点区域类型：A, B, C, D
    seek_id = copy.deepcopy(datalist[-1])  # 节点类型
    # seek_id = SimulationInterface.getNodeType(id)  # 从数据库获取节点类型： 出入口，其他
    exchangedata_origin = copy.deepcopy(self.adjData) 
    flag = [1] * len(self.adjData)  
    calcu_flag = 0 
    return_id = -1  
    self.syncNode()
    self.sendUDP(str(id) + "号节点就绪")
    data = None
    data_dict = None
    
    if self.parentID == id:  
        parent_flag = 1   
    else:
        parent_flag = 0  
        for i in range(len(adjDirection)):  
            if self.parentID == adjid[i]:  
                parent_i = i               
    if self.sonID: 
        son_flag = 0 
        son_i = [0] * len(self.sonID)             
        for i in range(len(self.sonID)):          
            for j in range(len(adjDirection)):  
                if self.sonID[i] == adjid[j]:   
                    son_i[i] = j  
    else:
        son_flag = 1

    if parent_flag == 1:  # 根节点
        time_out = 0
        while (sum(flag)) and (time_out < 50):
            time.sleep(0.1)      
            time_out += 1        
            for i in range(len(self.adjData)):       
                if exchangedata_origin[i] != self.adjData[i]:    
                    flag[i] = 0

        if time_out < 50 :
            adj_result_sum = 0
            car_type_count = dict()
            car_type_count[car_type] = len(information) - sum(information)
            for i in range(len(self.adjData)):
                if self.adjData[i][0] in self.sonID:
                    adj_result_sum += self.adjData[i][1]

                    if not self.adjData[i][2]:
                        continue
                    
                    for key, value in self.adjData[i][2].items():
                        if key in car_type_count:
                            car_type_count[key] += value
                        else:
                            car_type_count[key] = value
            data_dict=[id, len(information) - sum(information)+adj_result_sum, car_type_count]
            self.sendUDP("************************通过")
        else:
            self.sendUDP("************************超时")
    elif son_flag == 1: # 末尾节点
        car_type_count = dict()
        car_type_count[car_type] = len(information) - sum(information)
        data_dict = [id, len(information) - sum(information), car_type_count]
        self.sendUDP(str(id) + "testeteest" + json.dumps(data_dict))
        self.sendDataToDirection(adjDirection[parent_i], (data_dict))
    else:
        time_out = 0
        flag = [1] * len(self.sonID)
        while (sum(flag)) and (time_out < 50):  
            time.sleep(0.1)
            time_out += 1
            for i in range(len(self.adjData)):
                if not self.adjData[i] or exchangedata_origin[i] == self.adjData[i] or self.adjData[i][0] not in self.sonID:
                    continue

                for j in range(len(self.sonID)):
                    if self.adjData[i][0] == self.sonID[j]:
                        flag[j] = 0  

        if time_out < 50:
            adj_result_sum = 0
            car_type_count = dict()
            car_type_count[car_type] = len(information) - sum(information)

            for i in range(len(self.adjData)):
            
                if self.adjData[i] and self.adjData[i][0] in self.sonID:
                    adj_result_sum += self.adjData[i][1]

                    if not self.adjData[i][2]:
                        continue
                    
                    for key, value in self.adjData[i][2].items():
                        if key in car_type_count:
                            car_type_count[key] += value
                        else:
                            car_type_count[key] = value
            data_dict=[id, len(information) - sum(information)+adj_result_sum, car_type_count]
        self.sendDataToDirection(adjDirection[parent_i], (data_dict))
        # if son_flag==1: # 末尾节点
        # else: # 其他节点
        #     time_out = 0
        #     flag = [1] * len(self.sonID)
        #     while (sum(flag)) and (time_out < 50):  
        #         time.sleep(0.1)
        #         time_out += 1
        #         for i in range(len(self.adjData)):
        #             if not self.adjData[i] or exchangedata_origin[i] == self.adjData[i]:
        #                 continue

        #             adj_result = json.loads(self.adjData[i])
        #             for j in range(len(self.sonID)):
        #                 if adj_result[id_str] == self.sonID[j]:
        #                     flag[j] = 0  

        #     if time_out < 50:
        #         adj_result_sum = 0
        #         car_type_count = dict()
        #         car_type_count[car_type] = len(information) - sum(information)

        #         for i in range(len(self.adjData)):
                
        #             if self.adjData[i] and self.adjData[i][0] in self.sonID:
        #                 ajd_dict = json.loads(self.adjData[i])
        #                 adj_result_sum += ajd_dict[i][total_count_str]

        #                 if not self.ajd_dict[2]:
        #                     continue
                        
        #                 for key, value in ajd_dict[car_type_dict_str].items():
        #                     if key in car_type_count:
        #                         car_type_count[key] += value
        #                     else:
        #                         car_type_count[key] = value
                
        #         data_dict = dict()
        #         data_dict[id_str] = id
        #         data_dict[total_count_str] = len(information) - sum(information)+adj_result_sum
        #         data_dict[car_type_dict_str] = car_type_count
        #         self.sendDataToDirection(adjDirection[parent_i], json.dumps(data_dict))
    self.sendUDP(str(id) + "号节点完成")
    value=[json.dumps(data_dict), self.parentID, self.sonID]
    
    return value
