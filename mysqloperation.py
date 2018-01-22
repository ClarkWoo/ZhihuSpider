import mysql.connector as mycon

config={
    'host':'127.0.0.1',
    'user':'root',
    'password':'',
    'port':'3306',
    'database':'zhihu',
    'charset':'utf8'
}

def getMysqlConnect():
    try:
        conn=mycon.connect(**config)
        print("成功连接数据库："+config['database'])
        return conn
    except mycon.Error as e:
        print(e)

def getInsertSql(table,args):
    sql_1='insert into '+table+'('
    sql_2=''
    for arg,value in args.items():
        #sql调试语句
        # print(type(value))
        sql_1+=arg+','
        if type(value)==str:
            sql_2+='\''+value+'\''+','
        elif type(value)==int:
            sql_2+=str(value)+','
    sql_1=sql_1[:-1]+') values('
    sql_2=sql_2[:-1]+');'
    return sql_1+sql_2

def insertZhihu(connect,table,args):
    #假设answer_id为唯一
    sql=getInsertSql(table,args)
    cursor=connect.cursor()
    try:
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        print("成功往"+table+"表写入数据1条")
    except mycon.Error as e:
        print("\n执行失败的sql语句：\n"+sql)
        print(e)
        connect.rollback()

def getSelectData(connect,sql):
    cursor=connect.cursor()
    data_list=[]
    try:
        cursor.execute(sql)
        result_list=cursor.fetchall()
        for data in result_list:
            data_list.append(str(list(data)[0]))
        return data_list
        cursor.close()
    except mycon.Error as e:
        print(e)
        connect.rollback()
