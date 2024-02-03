# Author: Nike Liu
from util.database import conn
import pandas as pd

def read_access_db2(sql,column_list=None):
    """将读取来的access 转成df, column_list 为 df 的列名"""
    cursor = conn.cursor()
    # 将读取来的access cursor对象 pyodbc.Cursor object 转成list
    list = []
    # columnsList = []
    cursor_list = cursor.execute(sql)
    if cursor_list is not None:
        for row in cursor_list:
            # 将pyodbc.row转换为list
            new_list = [x for x in row]
            # columnsList.append(row.column_name)
            # print(new_list)
            list.append(new_list)
        cursor.close()
        # 得到持仓dataframe

        if column_list == None:
            df = pd.DataFrame(list)
            # print(columns)
        else:
            df = pd.DataFrame(list,columns=column_list)
        return df
    else:
        return None

def read_access_db(sql,column_list=None):
    """将读取来的access 转成df, column_list 为 df 的列名"""
    # 将读取来的access cursor对象 pyodbc.Cursor object 转成list
    df = pd.read_sql(sql,conn)
    if column_list is not None:
        df.columns = column_list
    return df

# def read_chemical_db(sql,column_list=None):
#     """将读取来的access 转成df, column_list 为 df 的列名"""
#     df = pd.read_sql(sql, chemical_db)
#     if column_list is not None:
#         df.columns = column_list
#     return df

def process_access_db(sql):
    """将数据写入到access"""
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.commit()  # 提交数据（只有提交之后，所有的操作才会生效）
    # cursor.close()
    # conn.close()

def get_columns_name(tablename):
    """获取access某个表的字段名称list"""
    cursor = conn.cursor()
    column_name_list = []
    for row in cursor.columns(table=tablename):
        column = row.column_name
        column_name_list.append(column)
    return column_name_list

if __name__ == '__main__':
    sql = "SELECT code,数量合计,平均成本 FROM 持仓概览;"
    columns = ['code', 'qty', 'cost2']
    data = read_access_db(sql)
    print(data)

    # 获取表的字段名
    # columns_names = get_columns_name('buy')
    # print(columns_names)
