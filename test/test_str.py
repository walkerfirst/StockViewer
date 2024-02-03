# Author: Nike Liu
name = '雨桐发债'
if name.find('发债')>=0:
    print('yes')
    name = name.replace("发债", "转债")

print(name)
# 测试字符串左补齐
str = '789'
str = str.rjust(6,'0')

print(str)

from setting.account import account_position
for item in account_position:
    print(item,type(item),account_position[item])