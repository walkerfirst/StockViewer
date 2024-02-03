# Author: Nike Liu
from util.access_db import read_access_db
from datetime import datetime

def GetHoldingDF(Name:str = None):

    columns = ['code', 'qty', 'cost']
    # print(columns)
    # 得到持仓dataframe
    if Name == None:

        sql = "SELECT code,数量合计,平均成本 FROM 持仓概览"
        # print(sql)
    else:
        sql = "SELECT code,数量合计,平均成本 FROM 持仓概览 where account='" + Name +"'"
        # print(sql)

    df = read_access_db(sql, columns)
    print(u'GetHoldingDF触发的计时器事件：%s' % str(datetime.now()))
    return df

if __name__ == '__main__':
    sql = "HX_L"
    run = GetHoldingDF(Name=sql)
    # print(run)