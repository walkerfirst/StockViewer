import sys,re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime,Qt
from PyQt5.QtGui import QStandardItem
from BaseQWidgets import BaseDFTable,BaseStandardTable2
from model.DataFrameTableModel import pandasModel
# from DataEngine import DataEngineSina,DataEngineTS

from event.eventType import *
from datetime import datetime

class Myhold2(BaseStandardTable2):
    # 设置表头
    tableheader = ['代码', '名称','数量', '仓位(%)', '成本', '当前价', '市值(W)', '当日亏损(K)', '涨跌幅(%)', '盈亏(K)', '盈亏(%)']
    def __init__(self,mainEngine,event,account):
        super(Myhold2, self).__init__()

        # 初始化引擎
        self.mainEngine = mainEngine
        self.account = account
        self.initData()

        # 添加监听函数，注意类后面不需要带形参
        self.mainEngine.registerHandler(type_=EVENT_TIMER, handler=self.run_update)

    def initData(self):
        """从db中获取需要展示的数据"""
        # 获取持仓信息

        self.dbdata = self.mainEngine.positionDict[self.account]
        # print(self.dbdata)

        # 获取数据中的账户信息
        df_acc = self.mainEngine.accDict[self.account]
        self.cash = df_acc['cash']
        self.cost = df_acc['cost']
        # print(self.cash)

    def run_update(self,event):
        """将需要显示的数据更新到model中"""
        # 这里要再次获取df，不然不会实时更新
        try:
            self.tickdata = event.dict["tick"]
            self.df = self.mainEngine.processData(self.dbdata,self.tickdata)
            self.df = self.df.drop(['time'],axis=1)
            if self.df.index.size > 0:
                self.update_data_to_model(self.df,self.account)
            # print(self.df.columns)
            # print(u'MyTable2触发的计时器事件：%s' % str(datetime.now()))
        except Exception as e:
            print('myhold2 set model发生错误%s'%str(e))
        # self.initData()
        # 把数据更新到model中去

        # 设置汇总行的行标
        # print('mark1')
        try:
            x = max(self.df.index) + 1
            self.total_profit = round(self.df['profit'].sum(),1)  # 账户利润总计
            self.total_day = round(self.df['profit_day'].sum(),1)   # 当日利润总计
            self.total_value = round(self.df['value'].sum(),1)
            self.total_day_rate = round(self.total_day/self.total_value*10, 1)    # 当日利润率
            self.total_rate = round(self.total_profit/(self.total_value*10-self.total_profit)*100, 1)  # 账户利润率
            # print('mark2')

            # print('mark3')
            # 设置汇总行要显示的内容
            time_update = str(datetime.now())[11:19]
            self.model.setItem(x, 0, QStandardItem(time_update))
            self.model.setItem(x, 1, QStandardItem('汇总'))  # 这一行为了点击该行时，不会发生错误
            self.model.setItem(x, 2, QStandardItem('计数:(%s)'%x))  # 这一行为了点击该行时，不会发生错误
            self.model.setItem(x, 3, QStandardItem(
                str(round(self.total_value / (self.cash / 10000 + self.total_value) * 100, 1)) + "%"))
            self.model.setItem(x, 4, QStandardItem(str(round(self.cost / 10000, 1))))
            self.model.setItem(x, 5, QStandardItem('C:' + str(round(self.cash / 1000, 1))))
            self.model.setItem(x, 6, QStandardItem(str(self.total_value)))
            self.model.setItem(x, 7, QStandardItem(str(self.total_day)))
            self.model.setItem(x, 8, QStandardItem(str(self.total_day_rate)))
            self.model.setItem(x, 9, QStandardItem(str(self.total_profit)))
            self.model.setItem(x, 10, QStandardItem(str(self.total_rate)))

            # 设置第几列的字体颜色
            self.setForeground(byname='change_rate', column=7)
            self.setForeground(byname='change_rate',column=8)
            self.setForeground(byname='profit_rate',column=9)
            self.setForeground(byname='profit_rate',column=10)

            # 设置最后一行的字体颜色
            self.setForeground_LastLine(self.total_day,x,7)
            self.setForeground_LastLine(self.total_profit,x,9)

            # 给最后一行设置对齐方式
            index_max = self.df.shape[0]
            column_max = self.df.shape[1]
            for i in range(0, column_max):
                self.model.item(index_max, i).setTextAlignment(Qt.AlignCenter)

        except Exception as e:

            print('myhold2 最后一行设置发生错误%s'%str(e))

class IndexTable2(BaseStandardTable2):
    # 设置表头
    tableheader = ['代码', '名称', '当前价', '涨跌幅(%)','时间']
    def __init__(self,mainEngine,event,symbols):
        super(IndexTable2, self).__init__()

        # 初始化引擎
        self.mainEngine = mainEngine
        self.symbols = symbols
        # 去除原始输入的symbols带有的字母，后改为ETF代替指数，暂时不要这个功能
        # self.newsymbols = []
        # for symbol in self.symbols:
        #     x = re.sub('[^0-9]','', symbol)
        #     self.newsymbols.append(x)
        # 添加监听函数，注意类后面不需要带形参
        self.mainEngine.registerHandler(type_=EVENT_TIMER, handler=self.run_update)

    def run_update(self,event):
        """将需要显示的数据更新到model中"""
        # 这里要再次获取df，不然不会实时更新
        try:
            self.tickdata = event.dict["tick"]
            self.df = self.tickdata[self.tickdata['code'].isin(self.symbols)]
            self.df = self.df[['code', 'name', 'price', 'change_rate', 'time']].sort_values(by='change_rate', ascending=False)

            # 重置索引，不然会出错
            self.df = self.df.reset_index(drop=True)
            if len(self.df) >0:
                self.update_data_to_model(self.df,account=None)
                # print(u'INDEX计时器事件：%s' % str(datetime.now()))

            # 设置第几列的字体颜色
            self.setForeground(byname='change_rate', column=3)
        except Exception as e:
            print('Index set model发生错误%s'%str(e))
        # self.initData()

class IndexTable(BaseDFTable):
    """将给定的代码直接转换成表格控件，并定时刷新"""
    columnName = ['代码', '名称', '报价', '涨跌幅(%)']
    def __init__(self,symbols):
        super(IndexTable, self).__init__()
        self.symbolArray = symbols
        self.initData()
        # self.run_update()
        self.createQtimer()

    def initData(self):
        # 需要展示的数据
        self.df = DataEngineSina(self.symbolArray).data
        self.df = self.df.sort_values(by='change_rate',ascending=False)
        self.df = self.df[['code', 'name', 'price','change_rate']]
        # columnName = ['代码', '名称', '报价', '涨跌幅(%)']

        return self.df

    def run_update(self):
        self.update_model(self.df)


class StatusForm(QWidget):
    def __init__(self,mainEngine,event):
        super(StatusForm, self).__init__()
        self.mainEngine = mainEngine
        self.initData()
        self.initUI()
        self.mainEngine.registerHandler(type_=EVENT_TIMER, handler=self.updateData)

    def initData(self):
        """从db中获取需要展示的数据"""
        # 获取持仓信息
        self.dbdata = self.mainEngine.positionDict['all']
        # print('1', self.dbdata)
        # 获取数据中的账户信息
        df_acc = self.mainEngine.accDict['all']
        self.cash = df_acc['cash']
        self.cost = df_acc['cost']

    def initUI(self):

        self.label_time = QLabel('显示当前时间')
        self.label_today = QLabel()
        self.label_float = QLabel()
        self.label_total = QLabel()
        self.label_cash = QLabel()
        # 建立一个网格布局
        layout = QGridLayout(self)
        # 把label控件添加到网格布局中

        layout.addWidget(self.label_today, 0, 1)
        layout.addWidget(self.label_float, 0, 2)
        layout.addWidget(self.label_total, 0, 3)
        layout.addWidget(self.label_cash, 0, 4)
        # 设置网格内容右对齐
        layout.addWidget(self.label_time, 0, 5,1,2,alignment=Qt.AlignRight)
        # self.MainLayout.addLayout(layout)

        self.setLayout(layout)

    def updateData(self,event):
        # 获取系统现在的时间
        time = QDateTime.currentDateTime()
        # 设置系统时间显示格式
        timeDisplay = time.toString("yyyy-MM-dd hh:mm:ss dddd")
        # 在标签上显示时间
        self.label_time.setText(timeDisplay)
        try:
            self.tickdata = event.dict["tick"]
            if self.tickdata.index.size > 0:
                self.df = self.mainEngine.processData(self.dbdata,self.tickdata)
                self.df = self.df[['value','profit','profit_day']]
                self.series = round(self.df.sum(),1)

            # print(self.df.columns)
            # print(u'MyTable2触发的计时器事件：%s' % str(datetime.now()))
        except Exception as e:
            print('statusForm set model发生错误%s'%str(e))
        total_day = self.series['profit_day']
        total_value = self.series['value']
        total_day_rate = round(total_day/total_value*10,1)
        total_profit = self.series['profit']
        total_rate = round(total_profit/total_value*10,1)

        today_str = "TODAY: " + str(total_day) + " (" + str(total_day_rate) + "%)"
        float_str = "FLOAT: " + str(total_profit) + " (" + str(total_rate) + "%)"
        total_str = "TOTAL: " + str(round(total_value-total_profit/10,1)) + " / "+ str(total_value) + " / " + str(round(total_value + self.cash / 10000, 1))
        cash_str = "CASH: " + str(round(self.cash / 10000, 1)) + " / " + str(round(self.cost / 10000, 1))

        # 设置label的数据
        self.label_today.setText(today_str)
        self.label_float.setText(float_str)
        self.label_total.setText(total_str)
        self.label_cash.setText(cash_str)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = StatusForm()
    win.show()
    sys.exit(app.exec_())
