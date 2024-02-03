# Author: Nike Liu

"""
对access 数据库的操作
"""
import pyodbc

path = r'D:\project\StockViewer\db\stock_records.accdb'# 数据库文件
# print(path)

conn = pyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + path + ";Uid=;Pwd=;")

cursor = conn.cursor()
# 按照顺序插入数据
# cursor.execute("INSERT INTO buy VALUES(502,'2020-02-22','军工etf', 66, 20,1000,0.5,'N','突破法','')")

# 指定某列的数据
# cursor.execute("INSERT INTO buy (买入日期, 名称, 结单) VALUES ('20200212', 'Wilson3', 'N')")
# 更新某个字段的数据
# cursor.execute("UPDATE buy SET 结单='N' WHERE id=502")
SQL = "SELECT * FROM buy WHERE ID >= 300;"
for row in cursor.execute(SQL):
    print(row.名称)
    print(row)

cursor.commit() # 提交数据（只有提交之后，所有的操作才会生效）
cursor.close()
conn.close()