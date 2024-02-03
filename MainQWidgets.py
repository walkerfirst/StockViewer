import sys,re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime,Qt,pyqtSignal
from PyQt5.QtGui import QStandardItem,QIcon,QFont
from BaseQWidgets import BaseStandardTable2,BaseDFTable
from util.access_db import process_access_db,read_access_db
from trading.trading import Trading
from trading.填权处理 import stcokprocess
from trading.资金进出处理 import ZJProcess
from datetime import datetime,timedelta
# from event.eventEngine import Event
from event.eventType import *
from DataEngine import DataEngine
from model.DataFrameTableModel import pandasModel
import pandas as pd



class Myhold2(BaseStandardTable2):
    # 设置表头
    tableheader = ['代码', '名称','数量', '仓位(%)', '成本', '当前价', '市值(W)', '当日亏损(K)', '涨跌幅(%)', '盈亏(K)', '盈亏(%)']

    # 定义一个pyqt 信号类型，必须在类的全局变量定义，不然会出错。
    tickSignal = pyqtSignal(dict)

    def __init__(self,mainEngine,account):
        super(Myhold2, self).__init__()
        # 初始化引擎
        self.mainEngine = mainEngine
        self.dataEngine = DataEngine()
        self.account = account
        self.today = datetime.now().strftime('%Y/%m/%d')

        # 获取db数据
        self.initData()
        self.tickSignal.connect(self.setModels)

        # 添加监听函数，注意类后面不需要带形参
        self.mainEngine.registerHandler(type_=EVENT_ACCOUNT, handler=self.reflash_db_data)
        self.mainEngine.registerHandler(type_=EVENT_TIMER, handler=self.run_update)
        # 账户变动后，立即刷新一次表格
        self.mainEngine.registerHandler(type_=EVENT_ACCOUNT, handler=self.run_update)


    def initData(self):
        """从db中获取需要展示的数据"""
        # 获取持仓信息
        self.dbdata = self.mainEngine.qryPosition(self.account)
        # 获取数据中的账户信息
        df_acc = self.dataEngine.getAccDict()[self.account]
        self.cash = df_acc['cash']
        self.cost = df_acc['cost']
        # sql_history = "select code,盈利,account from 历史单 where 卖出日期 = #"+self.today+"# and account = '" + self.account + "'"
        # sql_buy = "select code,数量,买入价,account from 历史单 where 买入日期 = #"+self.today+"# and account = '" + self.account + "'"
        # self.df_history = read_access_db(sql_history).groupby('code').sum()
        # _columns = ['code', 'qty', 'cost', 'account']
        # self.df_buy = read_access_db(sql_buy,column_list=_columns)
        # print(self.df_history)

    def reflash_db_data(self,event):
        """在有交易事件的情况下，重新刷新账户信息"""
        # print('update account')
        self.initData()

    def run_update(self,event):
        """获取将需要显示的数据"""
        # 这里要再次获取df，不然不会实时更新
        try:
            # print(self.account, self.cash)
            self.tickdata = event.dict["tick"]
            self.df = self.mainEngine.processData(self.dbdata,self.tickdata)
            self.df = self.df.drop(['time'],axis=1)
            if self.df.index.size > 0:
                self.df['profit'] = round(self.df['profit']/1000,1)
                self.df['value'] = round(self.df['value']/10000,1)

                # if not self.df_history.empty:
                #     # print(self.df_history,type(self.df_history))
                #     code = self.df_history.index[0]
                #     profit = self.df_history.loc[code]['盈利']
                #     self.df = self.df.set_index('code')
                #     new_profit = profit + self.df.loc[code]['profit_day']
                #     print(new_profit)
                #     self.df.loc[code,'profit_day'] = new_profit
                #
                #     self.df = self.df.reset_index(drop=False)
                #     print(self.df)

                self.df['profit_day'] = round(self.df['profit_day'] / 1000, 1)

                data_dict = {}    #定义发送数据的字典
                data_dict['data'] = self.df
                data_dict['account'] = self.account
                data_dict['event_type'] = event.type_

                # 将数据作为信号发送出去，不能直接在这里调用setModel类，否则会有报警提示。
                self.tickSignal.emit(data_dict)

            # print(u'MyTable2触发的计时器事件：%s' % str(datetime.now()))
        except Exception as e:
            print('myhold2 set model发生错误%s'%str(e))

    def setModels(self,data_dict):
        "更新数据到model"
        data = data_dict['data']
        account = data_dict['account']
        event_type = data_dict['event_type']

        # 把数据更新到model中去
        try:
            # 更新个股数据
            self.update_data_to_model(data)

            # 更新汇总行
            x = data.index.size  # 获取汇总行的行标
            # 若为交易事件，先要删除之前的汇总行
            if event_type == EVENT_ACCOUNT:
                self.model.removeRow(x)

            total_profit = round(data['profit'].sum(),1)  # 账户利润总计
            total_day = round(data['profit_day'].sum(),1)   # 当日利润总计
            total_value = round(data['value'].sum(),1)
            total_day_rate = round(total_day/total_value*10, 1)    # 当日利润率
            total_rate = round(total_profit/(total_value*10-total_profit)*100, 1)  # 账户利润率
            # 设置汇总行要显示的内容
            time_update = str(datetime.now())[11:19]
            self.model.removeColumns(self.model.columnCount(), 0)
            self.model.setItem(x, 0, QStandardItem(time_update))
            self.model.setItem(x, 1, QStandardItem('汇总'))  # 这一行为了点击该行时，不会发生错误
            self.model.setItem(x, 2, QStandardItem('计数:(%s)'%x))  # 这一行为了点击该行时，不会发生错误
            self.model.setItem(x, 3, QStandardItem(
                str(round(total_value / (self.cash / 10000 + total_value) * 100, 1)) + "%"))
            self.model.setItem(x, 4, QStandardItem(str(round(self.cost / 10000, 1))))
            self.model.setItem(x, 5, QStandardItem('C:' + str(round(self.cash / 1000, 1))))
            self.model.setItem(x, 6, QStandardItem(str(total_value) + "/" + str(round((total_value + self.cash / 10000), 1))))
            self.model.setItem(x, 7, QStandardItem(str(total_day)))
            self.model.setItem(x, 8, QStandardItem(str(total_day_rate)))
            self.model.setItem(x, 9, QStandardItem(str(total_profit)))
            self.model.setItem(x, 10, QStandardItem(str(total_rate)))

            # 设置第几列的字体颜色
            self.setForeground(byname='change_rate', column=7)
            self.setForeground(byname='change_rate',column=8)
            self.setForeground(byname='profit_rate',column=9)
            self.setForeground(byname='profit_rate',column=10)
            self.setForeground(byname='price', column=5)

            # 设置最后一行的字体颜色
            self.setForeground_LastLine(total_day,x,7)
            self.setForeground_LastLine(total_profit,x,9)

            # 给最后一行设置对齐方式
            index_max = data.shape[0]
            column_max = data.shape[1]
            for i in range(0, column_max):
                self.model.item(index_max, i).setTextAlignment(Qt.AlignCenter)

        except Exception as e:
            print('myhold2 最后一行设置发生错误%s'%str(e))

    def saveData(self):
        """保存当日的收盘信息"""
        today = datetime.now().strftime('%Y-%m-%d')
        # 先获取db数据
        qry_sql = "select * from 每日净值 where 日期 = '" + today + "' and 账户 = '" + self.account + "'"
        qry_re = read_access_db(qry_sql)
        # 判断是否已经存在当日数据
        if qry_re.empty:
            symbolList = self.dbdata['code'].tolist()
            tickData = self.mainEngine.getTick(symbolList)
            dataframe = self.mainEngine.processData(self.dbdata, tickData)
            stock_value = round(dataframe['value'].sum(),2)
            total_value = stock_value + round(self.cash/10000,2)
            save_sql = "INSERT INTO 每日净值(日期,账户,市值,总资产) VALUES ('" + today + "','" + self.account + "'," \
                                     " '" + str(stock_value) + "', '" + str(total_value)+ "')"
            process_access_db(save_sql)

    def showContextMenu(self,pos):
        """创建右键菜单"""
        self.tableView.contextMenu = QMenu(self)
        # self.tableView.contextMenu.popup(QCursor.pos())  # 菜单显示的位置,汇报警告信息
        self.tableView.contextMenu.move(self.mapToGlobal(pos))  # 菜单显示的位置

        row_num = -1
        for i in self.tableView.selectionModel().selection().indexes():
            row_num = i.row()

        try:
            if row_num is not None:
                code = self.model.item(row_num, 0).text()
                name = self.model.item(row_num, 1).text()
                # print(code,name)
                data_buy = [code, name, '买入',self.account]
                data_sell = [code, name, '卖出',self.account]
                # 中签的成本价格的计算

                cost = self.model.item(row_num, 4).text()

                data_ZQ = [code, name, '中签卖出',self.account,cost]
                data_HL = [code, name, '现金红利',self.account,cost]

                actionBuy = self.tableView.contextMenu.addAction('买入')
                actionBuy.triggered.connect(lambda: self.actionHandler(data_buy))

                actionSell = self.tableView.contextMenu.addAction('卖出')
                actionSell.triggered.connect(lambda: self.actionHandler(data_sell))

                actionZQ = self.tableView.contextMenu.addAction('中签卖出')
                actionZQ.triggered.connect(lambda: self.actionHandler(data_ZQ))

                actionHL = self.tableView.contextMenu.addAction('现金红利')
                actionHL.triggered.connect(lambda: self.actionHandler(data_HL))

                actionTQ = self.tableView.contextMenu.addAction('填权处理')
                actionTQ.triggered.connect(lambda: self.stockprocessprice(data_buy))

                actionDetail = self.tableView.contextMenu.addAction('买入明细')
                actionDetail.triggered.connect(lambda: self.showDetails(data_buy))

                actionHistory = self.tableView.contextMenu.addAction('历史明细')
                actionHistory.triggered.connect(lambda: self.showHistory(data_buy))

                actionZJ = self.tableView.contextMenu.addAction('资金进出操作')
                actionZJ.triggered.connect(lambda: self.ZJProcess(data_buy))
                self.tableView.contextMenu.show()
                # self.reflash_db_data()
        except Exception as e:
            print("打开右键菜单错误 %s" %(str(e)))

    def actionHandler(self,option):
        """交易处理对话框"""
        self.dialog_trading = Trading(option,self.mainEngine)
        self.dialog_trading.show()

    def stockprocessprice(self,option):
        """填权处理对话框"""
        self.dialog_stock = stcokprocess(option,self.mainEngine)
        self.dialog_stock.show()

    def ZJProcess(self, option):
        """资金进出处理对话框"""
        self.dialog_ZJ = ZJProcess(option,self.mainEngine)
        self.dialog_ZJ.show()

    def showDetails(self,option):
        """展示买入明细对话框"""
        if option[1] != "汇总":
            code = option[0]
            read_sql = "select ID,买入日期,名称,买入价,数量 from buy where 结单 = 'N' AND code = '" + code + "'"
            column_list = ['序号', '日期', '名称', '买入价', '数量']
            buy_history = read_access_db(read_sql, column_list=column_list)
            self.dialog_details = showDFTable(buy_history)
            self.dialog_details.setWindowTitle("买入明细")
            self.dialog_details.setGeometry(600, 600, 1080, 800)
            self.dialog_details.show()
        else:
            QMessageBox.about(self, "对话框", "汇总没有明细")

    def showHistory(self,option):
        """展示交易明细对话框"""
        name = option[1]
        if name != "汇总":
            code = option[0]
            read_sql = "select 卖出日期,数量,买入价,卖出价,盈利,利润率 from 历史单 where code = '" + code + "'"
            column_list = ['日期', '数量', '买入价', '卖出价','盈利','利润率(%)']
            trade_history = read_access_db(read_sql, column_list=column_list)
            # 添加汇总行
            trade_history = addSummary(trade_history)
            trade_history = trade_history[['日期', '数量', '买入价', '卖出价', '盈利', '利润率(%)']]  # 重新列排序
            self.dialog_history = showDFTable(trade_history)
            self.dialog_history.setWindowTitle(" %s  历史明细" % name)
            self.dialog_history.setGeometry(600, 600, 1080, 800)
            self.dialog_history.show()
        else:
            QMessageBox.about(self, "对话框", "汇总没有明细")

def addSummary(df):
    """根据历史交易明细生成汇总行"""
    df_sum = pd.Series()  # 新建一个series，其实这里也可新建一个字典。
    df_sum['买入价'] = (df['数量'] * df['买入价']).sum()
    df_sum['卖出价'] = (df['数量'] * df['卖出价']).sum()
    df_sum['盈利'] = df['盈利'].sum()
    df_sum['数量'] = df['数量'].sum()
    df_sum['利润率(%)'] = df_sum['盈利'] / df_sum['买入价']
    # 将series添加到df的最后一行。
    df = df.append(df_sum, ignore_index=True)

    return df

class IndexTable2(BaseStandardTable2):
    # 设置表头
    tableheader = ['代码', '名称', '当前价', '涨跌幅(%)','时间']

    # 定义一个pyqt 信号类型，必须在类的全局变量定义，不然会出错。
    tickSignal = pyqtSignal(dict)
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

        # 连接信号与槽函数
        self.tickSignal.connect(self.setModels)
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
                data_dict = {}  # 定义发送数据的字典
                data_dict['data'] = self.df
                # print(u'INDEX计时器事件：%s' % str(datetime.now()))
                self.tickSignal.emit(data_dict)

        except Exception as e:
            print('Index set model发生错误%s'%str(e))

    def setModels(self,data_dict):

        data = data_dict['data']
        self.update_data_to_model(data)

        # 设置第几列的字体颜色
        self.setForeground(byname='change_rate', column=3)

    def showContextMenu(self, pos):
        pass

class StatusForm(QWidget):
    def __init__(self,mainEngine,event):
        super(StatusForm, self).__init__(flags=Qt.WindowFlags())
        self.mainEngine = mainEngine
        self.initData()
        self.initUI()
        self.mainEngine.registerHandler(type_=EVENT_ACCOUNT, handler=self.reflash_db_data)
        self.mainEngine.registerHandler(type_=EVENT_TIMER, handler=self.updateData)
        # 账户变动后，立即刷新一次表格
        self.mainEngine.registerHandler(type_=EVENT_ACCOUNT, handler=self.updateData)


    def initData(self):
        """从db中获取需要展示的数据"""
        # 获取持仓信息
        self.dbdata = self.mainEngine.qryPosition(accountName='all')
        # print('1', self.dbdata)
        # 获取数据中的账户信息
        df_acc = DataEngine().getAccDict()['all']
        self.cash = df_acc['cash']
        self.cost = df_acc['cost']

    def reflash_db_data(self,event):
        """在有交易事件的情况下，重新刷新账户信息"""
        # 获取持仓信息
        self.initData()

    def initUI(self):

        self.label_time = QLabel('显示当前时间')
        self.label_today = QLabel()
        self.label_float = QLabel()
        self.label_position = QLabel()
        self.label_cash = QLabel()
        self.label_total = QLabel()

        # 建立一个网格布局
        layout = QGridLayout(self)
        # 把label控件添加到网格布局中

        layout.addWidget(self.label_today,0, 1)
        layout.addWidget(self.label_float, 0, 2)
        layout.addWidget(self.label_position, 0, 3)
        layout.addWidget(self.label_cash, 0, 4)
        layout.addWidget(self.label_total, 0, 5)

        # 设置网格内容右对齐
        layout.addWidget(self.label_time, 0, 6,1,2,alignment=Qt.AlignCenter)
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
                self.df = round(self.df/10000,1)
                self.series = round(self.df.sum(),1)

            # print(self.df.columns)
            # print(u'MyTable2触发的计时器事件：%s' % str(datetime.now()))
        except Exception as e:
            print('statusForm set model发生错误%s'%str(e))
        total_day = self.series['profit_day']*10
        total_value = self.series['value']
        total_day_rate = round(total_day/total_value*10,1)
        float_profit = self.series['profit']*10
        total_rate = round(float_profit/total_value*10,1)
        total_ = round(total_value + self.cash / 10000, 1)
        total_profit = total_ - round(self.cost/10000,1)

        today_str = "TODAY: " + str(total_day) + " k (" + str(total_day_rate) + "%)"
        float_str = "FLOAT: " + str(float_profit) + " k (" + str(total_rate) + "%)"
        position_str = "POS: " + str(total_value) + " k / (" + str(round(total_value/(total_value + self.cash / 10000)*100,1)) + "%)"
        cash_str = "CASH: " + str(round(self.cash / 10000, 1)) + " w"
        total_str = "TOTAL: " + str(total_) + " - " + str(round(self.cost/10000,1)) + " = " + str(round(total_profit,1)) +\
                    " w (" + str(round(total_profit/total_*100,1)) + "%)"

        # 设置label的数据
        self.label_today.setText(today_str)
        self.label_float.setText(float_str)
        self.label_position.setText(position_str)
        self.label_cash.setText(cash_str)
        self.label_total.setText(total_str)


class showDFTable(BaseDFTable):
    """展示简单表格数据的Qtableview的显示控件"""
    def __init__(self,df):
        self.df = df
        super(showDFTable, self).__init__(self.df)
        if not self.df.empty:
            if '日期' in self.df.columns:
                self.df = self.df.sort_values(by='日期', ascending=False)
                self.df['日期'] = self.df['日期'].dt.strftime('%Y-%m-%d')
            if 'index' in self.df.columns:
                self.df = self.df.drop(['index'], axis=1)
            if '盈利' in self.df.columns:
                self.df['盈利'] = self.df['盈利'].astype('int')
            if '利润率(%)' in self.df.columns:
                self.df['利润率(%)'] = round(self.df['利润率(%)'] *100,1)
            self.df = self.df.replace("NaT","总计：")
            if '数量' in self.df.columns:
                self.df['数量'] = self.df['数量'].astype('int')
            # 把新数据更新到model中
            self.update_model()

class SearchDB(QWidget):
    def __init__(self,dbname):
        super(SearchDB,self).__init__()
        self.dbname = dbname
        self.initUi()

    def initUi(self):
        self.setWindowTitle("搜索%s窗口" % self.dbname)
        self.setWindowIcon(QIcon('./res/draw.png'))
        layout = QVBoxLayout()
        uplayout = QHBoxLayout()
        self.setGeometry(500, 500, 1580, 1080)  # 窗口坐标和窗口大小
        self.nameLineEdit = QLineEdit("")
        # 下来列表格式
        self.optionBox = QComboBox()
        self.optionBox.addItem('代码',"code")
        self.optionBox.addItem('名称',"名称")
        self.optionBox.addItem('日期YYYY/M/D',"日期")
        self.optionBox.addItem('账户', "account")
        confirm_Btn = QPushButton('搜索')
        # layout.setSpacing(10)
        uplayout.addWidget(self.nameLineEdit)
        uplayout.addWidget(self.optionBox)
        uplayout.addWidget(confirm_Btn)

        confirm_Btn.clicked.connect(self.Addsearch)
        layout.addLayout(uplayout,1)
        self.dataView = QTableView()
        self.dataView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表头背景色
        self.dataView.horizontalHeader().setStyleSheet("QHeaderView::section{background:#B0C4DE;}")
        self.dataView.verticalHeader().setVisible(False)
        # 设置表格交叉颜色
        self.dataView.setAlternatingRowColors(True)
        self.dataView.setFont(QFont("Arial", 10))
        layout.addWidget(self.dataView, 2)
        self.setLayout(layout)

    def Addsearch(self):
        selected = self.optionBox.itemData(self.optionBox.currentIndex())  # 获取下来框的值
        searchName = self.nameLineEdit.text()
        # 首先处理列名
        if self.dbname == '历史单' and selected == '日期':
            selected = '卖出日期'
        if self.dbname == '研报':
            columns = ['code', '名称', '日期', '期数', '标记', 'account']
        else:
            columns = ['code', '名称', '数量', '买入价', '卖出价', '卖出日期', '盈利', '利润率', 'account']

        read_sql = "select * from " + self.dbname + " where " + selected + " like '%" + searchName + "%'"
        # 需要展示的数据
        sell_history = read_access_db(read_sql)
        data = sell_history.reset_index()

        for index in columns:
            if index not in data.columns:
                columns.remove(index)
        data = data[columns]

        if '卖出日期' in data.columns:
            data.rename(columns={'卖出日期': '日期'}, inplace=True)

        # 调整日期显示格式
        data['日期'] = data['日期'].apply(lambda x : x.strftime('%Y-%m-%d'))

        if '利润率' in data.columns:
            data.rename(columns={'利润率': '利润率(%)'}, inplace=True)
            data['盈利'] = data['盈利'].astype(int)
            # 添加汇总行
            data = addSummary(data)[['code', '名称', '数量', '买入价', '卖出价', '日期', '盈利', '利润率(%)', 'account']]
            data['利润率(%)'] = round(data['利润率(%)'] * 100, 1)
            # data.fillna(value='总计：', limit=1)

        model = pandasModel(data)
        self.dataView.setModel(model)


class SellHistory(QWidget):
    def __init__(self):
        super(SellHistory, self).__init__()
        # 需要展示的数据
        recently_sell_sql = "select top 10 卖出日期,code,名称,数量,买入价,卖出价,盈利,利润率 from 历史单 ORDER BY 卖出日期 DESC"
        column_list = ['日期','代码','名称','数量','买入价','卖出价','盈利','利润率(%)']
        sell_history = read_access_db(recently_sell_sql,column_list=column_list)
        sell_history = sell_history.reset_index()
        # 添加汇总行
        sell_history = addSummary(sell_history)
        sell_history = sell_history[['日期','代码','名称','数量', '买入价', '卖出价', '盈利', '利润率(%)']]  # 重新列排序
        self.dialog_sell = showDFTable(sell_history)
        self.dialog_sell.setWindowTitle(" 最近卖出历史")
        self.dialog_sell.setGeometry(600, 600, 1280, 1000)
        # 窗口不设置样式，则为系统默认
        # self.dialog_sell.setStyleSheet(QStyleFactory.create("WindowsXP"))
        self.dialog_sell.show()


class AccountDetails(QWidget):
    def __init__(self):
        super(AccountDetails, self).__init__()
        # 需要展示的数据
        account_sql = "select top 10 code,name,投入本金,cash,实现盈利 from 账户 ORDER BY 投入本金 DESC"
        column_list = ['代码','名称','本金','现金','实现盈利']
        df_account = read_access_db(account_sql,column_list=column_list)
        df_account = df_account.reset_index()
        # 添加汇总行
        # df_account = addSummary(df_account)
        # df_account = sell_history[['日期', '数量', '买入价', '卖出价', '盈利', '利润率(%)']]  # 重新列排序
        self.dialog_account = showDFTable(df_account)
        self.dialog_account.setWindowTitle("账户信息概览")
        self.dialog_account.setGeometry(600, 600, 1280, 1000)
        # 窗口不设置样式，则为系统默认
        # self.dialog_sell.setStyleSheet(QStyleFactory.create("WindowsXP"))
        self.dialog_account.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyle(QStyleFactory.create("WindowsXP"))
    win = SearchDB('历史单')
    win.show()
    sys.exit(app.exec_())
