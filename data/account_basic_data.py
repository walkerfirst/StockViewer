# Author: Nike Liu
from util.access_db import read_access_db

sql = "select * from 账户;"
df = read_access_db(sql,column_list=['id','name','code','cash','profit','cost'])
ht_cash = df.iloc[0,3]
hx_cash = df.iloc[1,3]
gf_cash = df.iloc[2,3]
gl_cash = df.iloc[3,3]

ht_profit = df.iloc[0,4]
hx_profit = df.iloc[1,4]
gf_profit = df.iloc[2,4]
gl_profit= df.iloc[3,4]

ht_cost = df.iloc[0,5]
hx_cost = df.iloc[1,5]
gf_cost = df.iloc[2,5]
gl_cost = df.iloc[3,5]

total_cash = df['cash'].sum()
total_profit = df['profit'].sum()
total_cost = df['cost'].sum()

# print(df)

