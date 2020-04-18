#coding=utf-8
from enum import Enum, unique
import pymysql

floorID = 1
room_Num = 16

host="39.100.78.210"
user="root"
passwd="893893"
dbname="syslynkros_v30_qh"
charset="utf8"


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


def controlModel(data):
    db = pymysql.connect(host="39.100.78.210", user="root", passwd="893893", db="syslynkros_v30_qh", charset='utf8')
    cursor = db.cursor()
    for ele in data:
        nID, dllid, nIndex, paracode, t, memindex, memlength, paravalue = ele   #元素定义
        sql = "INSERT INTO modeinfosetvalue(nID, dllid, nIndex, paracode, __t, memindex, memlength, paravalue) VALUES (%s, %s, %s, '%s', %s, %s, %s, %s);" #(nID, dllid, nIndex, paracode, t, memindex, memlength, paravalue)变量元素放入数据库
        cursor.execute(sql) #执行单条sql语句,接收的参数为sql语句本身和使用的参数列表,返回值为受影响的行数
        db.commit()  #调用db.commit( )  #成功插入数据


def getCarStatus(floorID, node_id):
    """
        获取车位状态信息
    """
    list1 = list()

    table="parking_lot"  #  停车场数据表
    car_status='0020100'  +  "%02d" % node_id #  节点车位状态字段


    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()  #建立数据库连接
    sql = "select k" + car_status + " from " + table + " where nIndex=%s"  % (floorID - 1)
    affect_line_num = cursor.execute(sql)
    data = cursor.fetchall()
    if affect_line_num: # 如果能够查到
        car_status_str = data[0][0]  # 获取节点的区域类型： A, B，C, D, data[0][0]： 筛选后的结果的第一行第一列的数据
        list1 = car_status_str.split('|')  # 分割字符串为
        list1 = list(map(lambda x: int(x), list1)) # 字符转换成int

    return list1

def getAreaType(node_id):
    """
    输入节点id,返回区域类型： A, B, C, D
    """
    table="parking_delta_list"  #  区域类型表
    area_type='AreaType'  #  区域类型字段

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()  #建立数据库连接
    sql = "select k" + area_type + " from " + table + " where nIndex=%s"  % (node_id - 1)
    affect_line_num = cursor.execute(sql)
    data = cursor.fetchall()
    node_type = None
    if affect_line_num: # 如果能够查到
        node_type = data[0][0]  # 获取节点的区域类型： A, B，C, D, data[0][0]： 筛选后的结果的第一行第一列的数据

    return node_type


def getNodeType(node_id):
    '''
        获取节点类型字段
    '''
    table="parking_delta_list"  #  节点类型表
    node_type='NodeType'  #  节点类型字段

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()  #建立数据库连接
    sql = "select k" + node_type + " from " + table + " where nIndex=%s"  % (node_id - 1)
    affect_line_num = cursor.execute(sql)
    data = cursor.fetchall()
    node_type = None
    if affect_line_num: # 如果能够查到
        node_type = int(data[0][0]) if data[0][0] else 0  # 获取节点的类型： 出口，入口、其他, data[0][0]： 筛选后的结果的第一行第一列的数据

    return node_type


def get_unit_price(user_type:int, car_type:int, day_or_night:int):
    '''
        获取停车费价格
    '''
    table = "parking_price_table" # 停车费用表
    unit_price = "price"  # 具体价格
    time_unit = "unit_time"  # 时间单位

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()  # 建立数据库连接
    get_price_sql = "select %s, %s from %s where kday_or_night=%s and kcar_type=%s and kuser_type=%s" % ('k'+unit_price, 'k'+time_unit, 
        table, day_or_night, car_type, user_type)
    affect_line_num = cursor.execute(get_price_sql)
    data = cursor.fetchall()
    unit_price_value = None
    time_unit_value = None
    if affect_line_num: # 如果能够查到
        unit_price_value = float(data[0][0]) if data[0][0] else 0
        time_unit_value = float(data[0][1]) if data[0][1] else 0

    return unit_price_value, time_unit_value


def saveCarFee(floorID ,carFee):  #保存车费到db ----  db相当于连一个车费显示器，显示车牌号及车费
    '''
        停车场
    '''
    table="parking_lot"  #  停车场数据表
    parking_fee='002010022'  #  车费字段

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()  #建立数据库连接
    # 更新数据库的数据
    save_car_fee_sql = "update " + table + " set k" + parking_fee + "=%s where nIndex=%s" % (carFee ,floorID-1)
    cursor.execute(save_car_fee_sql)
    db.commit()


def saveTotalCount(floorID, carCount):  #保存车费到db ----  db相当于连一个车费显示器，显示车牌号及车费
    '''
        保存总车位数量
    '''
    table="parking_lot"  #  停车场数据表
    total_cat_count='002010017'  #  总车位字段

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()  #建立数据库连接
    # 更新数据库的数据
    save_car_fee_sql = "update " + table + " set k" + total_cat_count + "=%s where nIndex=%s" % (carCount ,floorID-1)
    cursor.execute(save_car_fee_sql)
    db.commit()


def saveRegionCount(floorID, regionType, carCount):  #保存车费到db ----  db相当于连一个车费显示器，显示车牌号及车费
    '''
        保存区域车位数量
    '''
    table="parking_lot"  #  停车场数据表
    regionType = str(regionType).upper()

    if regionType == "A":
        region_cat_count='002010018'  #  总车位字段
    elif regionType == "B":
        region_cat_count='002010019'  #  总车位字段
    elif regionType == "C":
        region_cat_count = '002010020'
    elif regionType == "D":
        region_cat_count = '002010021'
    else:
        return

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()  #建立数据库连接
    # 更新数据库的数据
    save_car_fee_sql = "update " + table + " set k" + region_cat_count + "=%s where nIndex=%s" % (carCount ,floorID-1)
    cursor.execute(save_car_fee_sql)
    db.commit()


def dataForCar(floorID):
    '''
        @param floorID: 楼层
        @return: 返回 parking_feeValue(车费), carlicenseValue(车牌号)
    '''
    table="parking_lot"  #  停车场数据表

    carlicense='002010023' # 车牌号----
    parking_fee='002010022' # 停车费

    db = pymysql.connect(host="39.100.78.210", user="root", passwd="893893", db="syslynkros_v30_qh", charset='utf8')
    cursor = db.cursor()

    sql = "SELECT %s FROM %s WHERE nIndex=%s" % ('k' +carlicense, table, floorID-1)
    line_num = cursor.execute(sql)  #返回参数列表
    data = cursor.fetchall()  #接受参数行
    carlicenseValue = None
    if line_num:
        carlicenseValue = int(data[0][0])

    sql = "SELECT %s FROM %s WHERE nIndex=%s" % ('k' +parking_fee, table, floorID-1 )
    line_num = cursor.execute(sql)  #返回参数列表
    data = cursor.fetchall()  #接受参数行
    parking_feeValue = None
    if line_num:
        parking_feeValue = float(data[0][0]) if data[0][0] else 0.0
    return parking_feeValue, carlicenseValue


def save_input_car_license_number(car_license_number, in_datetime_str:str):
    '''
        保存车辆入库信息
    '''
    table = "parking_car_license_number"
    car_license_col = "CarLicenseNumber"
    in_datetime_col = "InTime"
    in_datetime_str = "'" + in_datetime_str + "'"

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()

    sql = "insert into %s (%s, %s) values(%s, %s) on DUPLICATE key update %s=%s" % (
        table, car_license_col, in_datetime_col, car_license_number, in_datetime_str, in_datetime_col, in_datetime_str)
    # sql = "insert into %s (%s, %s) values(%s, %s)" % (table, car_license_col, in_datetime_col)
    line_num = cursor.execute(sql)  #返回参数列表
    db.commit()

    if line_num:
        return True

    return False


def get_input_datetime(car_license_number):
    '''
        返回车辆的入库时间
        result: datetime
    '''
    table = "parking_car_license_number"
    car_license_col = "CarLicenseNumber"
    in_datetime_col = "InTime"
    in_datetime = None

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()

    sql = "select %s from %s where %s = %s" % (
        in_datetime_col, table, car_license_col, car_license_number)
    # sql = "insert into %s (%s, %s) values(%s, %s)" % (table, car_license_col, in_datetime_col)
    line_num = cursor.execute(sql)  #返回参数列表
    data = cursor.fetchall()
    db.commit()


    if line_num:
        in_datetime = data[0][0] if data[0][0] else None

    return in_datetime


def get_random_car_license():
    """
        随机获取一个车牌号
    """
    table = "parking_car_license_number"
    car_license_col = "CarLicenseNumber"
    out_datetime_col = "OutTime"
    parking_fee_col = "ParkingFee"
    car_license_number = None

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()

    sql = """
        SELECT CarLicenseNumber FROM parking_car_license_number  AS t1  
        JOIN ( 
            SELECT ROUND(
                RAND() * (
                    ( 
                        SELECT MAX(id) FROM parking_car_license_number
                    )
                        - 
                    (
                        SELECT MIN(id) FROM parking_car_license_number
                    )
                )
                    + 
                (
                    SELECT MIN(id) FROM parking_car_license_number
                )
            ) AS id
        ) AS t2 
        WHERE t1.id >= t2.id ORDER BY t1.id LIMIT 1"""
    
    # sql = "insert into %s (%s, %s) values(%s, %s)" % (table, car_license_col, in_datetime_col)
    line_num = cursor.execute(sql)  #返回参数列表
    data = cursor.fetchall()
    db.commit()

    if line_num:
        car_license_number = data[0][0] if data[0][0] else None

    return car_license_number


def save_out_time_and_parking_fee(car_license_number, out_datetime_str:str, parking_fee:float):
    '''
        保存车辆入库信息
    '''
    table = "parking_car_license_number"
    car_license_col = "CarLicenseNumber"
    out_datetime_col = "OutTime"
    parking_fee_col = "ParkingFee"
    out_datetime_str = "'" + out_datetime_str + "'"

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)
    
    cursor = db.cursor()

    sql = "update %s set %s=%s, %s=%s where %s=%s;" % (
        table, out_datetime_col, out_datetime_str, parking_fee_col, parking_fee, car_license_col, car_license_number)
    # sql = "insert into %s (%s, %s) values(%s, %s)" % (table, car_license_col, in_datetime_col)
    line_num = cursor.execute(sql)  #返回参数列表
    db.commit()

    if line_num:
        return True

    return False


if __name__ == "__main__":
    # # 测试获取车费及车牌号
    # print(dataForCar(1))

    # # 测试更新停车费信息
    # saveCarFee(1, 1000)

    # print("这是普通节点:" + str(getNodeType(10))) # 普通节点
    # print("这是入口节点:" + str(getNodeType(1))) # 入口节点
    # print("这是出口节点" + str(getNodeType(16))) # 出口节点

    # print('这个节点是A区域:' + str(getAreaType(1)))  # A区域
    # print('这个节点是B区域:' + str(getAreaType(4)))  # B区域
    # print('这个节点是C区域:' + str(getAreaType(5)))  # C区域
    # print('这个节点是D区域:' + str(getAreaType(3)))  # D区域

    # print('获取节点1的停车状态:')
    # print(getCarStatus(1, 1))
    # print('获取节点10的停车状态:')
    # print(getCarStatus(1, 10))

    # print('保存总车位')
    # saveTotalCount(1, 61)
    # print('保存A区域车位')
    # saveRegionCount(1, "A", 7)
    # print('保存B区域车位')
    # saveRegionCount(1, "B", 8)
    # print('保存C区域车位')
    # saveRegionCount(1, "C", 10)
    # print('保存D区域车位')
    # saveRegionCount(1, "D", 12)


    # print('获取停车费价格')
    # price_result = get_unit_price(user_type=UserType.normal.value -1,
    #                 car_type=CarType.little.value -1 ,
    #                 day_or_night=DayOrNight.day.value -1)
    # print(price_result)


    print('保存车牌号，及入库时间')
    print(save_input_car_license_number(3423492, '2019-02-20 12:20'))

    print("获取车牌的入库时间")
    print(get_input_datetime(1111))

    print('保存出库时间及车费')
    print(save_out_time_and_parking_fee(3423492, '2020-02-02', 400))

    print("获取车库内随机的车牌号")
    print(get_random_car_license())
