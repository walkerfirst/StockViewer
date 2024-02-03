# Author: Nike Liu
from util.access_db import read_access_db
"""获取各个账户的持仓基本信息"""

def get_df(term,columns):

    if 'all' in term:
        sql = "SELECT code,数量合计,平均成本 FROM 持仓概览"
    else:
        sql = "SELECT code,数量合计,平均成本 FROM 持仓概览 where account=" + term

    data = read_access_db(sql, columns)
    return data

columns = ['code', 'qty', 'cost']

df_hx = get_df(term="'HX_L'",columns=columns)
df_ht = get_df(term="'HT_L'",columns=columns)
df_gf = get_df(term="'GF_L'",columns=columns)
df_gl = get_df(term="'GL_J'",columns=columns)
df_all = get_df(term="'all",columns=columns)