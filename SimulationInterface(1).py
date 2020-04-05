#coding=utf-8
import pymysql

floorID = 1
room_Num = 16
def controlModel(data):
    db = pymysql.connect(host="39.100.78.210", user="root", passwd="893893", db="syslynkros_v30_qh", charset='utf8')
    cursor = db.cursor()
    for ele in data:
        nID, dllid, nIndex, paracode, t, memindex, memlength, paravalue = ele   #元素定义
        sql = "INSERT INTO modeinfosetvalue(nID, dllid, nIndex, paracode, __t, memindex, memlength, paravalue) VALUES (%s, %s, %s, '%s', %s, %s, %s, %s);" #(nID, dllid, nIndex, paracode, t, memindex, memlength, paravalue)变量元素放入数据库
        cursor.execute(sql) #执行单条sql语句,接收的参数为sql语句本身和使用的参数列表,返回值为受影响的行数
        db.commit()  %调用db.commit( )  #成功插入数据

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