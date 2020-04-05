#coding=utf-8
import pymysql

floorID = 1
room_Num = 16

host="39.100.78.210"
user="root"
passwd="893893"
dbname="syslynkros_v30_qh"
charset="utf8"


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

    table="Parking_lot"  #  停车场数据表
    parking_fee='0020090'  +  "%02d" % node_id #  节点车位状态字段


    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()  #建立数据库连接
    sql = "select k" + parking_fee + " from " + table + " where nIndex=%s"  % (floorID - 1)
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
    table="Parking_lot"  #  区域类型表
    parking_fee='002010022'  #  区域类型字段

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()  #建立数据库连接
    sql = "select k" + parking_fee + " from " + table + " where nIndex=%s"  % (node_id - 1)
    affect_line_num = cursor.execute(sql)
    data = cursor.fetchall()
    node_type = None
    if affect_line_num: # 如果能够查到
        node_type = data[0][0]  # 获取节点的区域类型： A, B，C, D, data[0][0]： 筛选后的结果的第一行第一列的数据

    return node_type


def getNodeType(node_id):
    table="Parking_lot"  #  节点类型表
    parking_fee='002010022'  #  节点类型字段

    db = pymysql.connect(
        host=host, 
        user=user,
        passwd=passwd, 
        db=dbname, 
        charset=charset)

    cursor = db.cursor()  #建立数据库连接
    sql = "select k" + parking_fee + " from " + table + " where nIndex=%s"  % (node_id - 1)
    affect_line_num = cursor.execute(sql)
    data = cursor.fetchall()
    node_type = None
    if affect_line_num: # 如果能够查到
        node_type = data[0][0]  # 获取节点的类型： 出口，入口、其他, data[0][0]： 筛选后的结果的第一行第一列的数据

    return node_type


def saveCarFee(floorID ,carFee):  #保存车费到db ----  db相当于连一个车费显示器，显示车牌号及车费
    '''
        停车场
    '''
    table="Parking_lot"  #  停车场数据表
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


def dataForCar(floorID):
    '''
        @param floorID: 楼层
        @return: 返回 parking_feeValue(车费), carlicenseValue(车牌号)
    '''
    carlicense='002010023' # 车牌号----
    parking_fee='002010022' # 停车费

    db = pymysql.connect(host="39.100.78.210", user="root", passwd="893893", db="syslynkros_v30_qh", charset='utf8')
    cursor = db.cursor()

    sql = "SELECT %s FROM Parking_lot WHERE nIndex=%s" % ('k' +carlicense ,floorID-1)
    line_num = cursor.execute(sql)  #返回参数列表
    data = cursor.fetchall()  #接受参数行
    if line_num:
        carlicenseValue = int(data[0][0])

    sql = "SELECT %s FROM Parking_lot WHERE nIndex=%s" % ('k' +parking_fee,floorID-1 )
    cursor.execute(sql)  #返回参数列表
    data = cursor.fetchall()  #接受参数行
    parking_feeValue = float(data[0][0])
    return parking_feeValue, carlicenseValue


if __name__ == "__main__":
    # 测试获取车费及车牌号
    print(dataForCar(1))

    # 测试更新停车费信息
    saveCarFee(1, 1000)