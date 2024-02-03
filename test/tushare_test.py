# Author: Nike Liu
import tushare as ts
# 获取实时分笔数据
code = '300738'
df = ts.get_realtime_quotes(['sh','sz','hs300','sz50','zxb','cyb'])
print(df)