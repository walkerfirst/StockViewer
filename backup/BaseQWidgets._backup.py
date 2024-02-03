from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QTimer,QUrl
from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem, QBrush, QColor, QFont, QDesktopServices
import urllib.request
from PyQt5.QtSql import QSqlDatabase,QSqlTableModel
from DataEngine import DataEngineSina,DataEngineTS
from model.DataFrameTableModel import pandasModel
import tushare as ts
import pandas as pd
from show_k_chart import Kchart_MainWindow
# from diyDelegate import TableDelegate
from datetime import datetime
from trading.trading import Trading
from trading.填权处理 import stcokprocess

from PyQt5 import QtGui

class BaseStandardTable(QWidget):

    """a demo of  get tick data from tushare,
    注：tushare 必须升级到 1.4.2版本以上
    Python3.3 + PyQt5 IDE: PyCharm 3.0"""

    tableheader = []
    def __init__(self):
        super(BaseStandardTable, self).__init__()

        self.initModel()
        self.initUI()
        # 自动更新行情
        # self.createQtimer()

    def initModel(self):
        # 定义数据模型
        self.model = QStandardItemModel(self)

        # 重新设置表格头的显示名称
        ColumnsNum = len(self.tableheader)
        if ColumnsNum > 0:
            for index in range(0, ColumnsNum):
                self.model.setHorizontalHeaderItem(index, QStandardItem(self.tableheader[index]))

    def initUI(self):

        # 设置表格布局
        layout = QHBoxLayout()
        self.tableView = QTableView()
        layout.addWidget(self.tableView)
        # 给表格控件设置数据模型
        self.tableView.setModel(self.model)
        self.tableView.setFont(QFont("Arial", 12))
        # 隐藏表格的列名称
        self.tableView.verticalHeader().hide()
        # 设置表格横向/纵向填满整个layout
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格宽度适合内容
        # self.tableView.resizeColumnsToContents()
        # 开启按列排序功能
        self.tableView.setSortingEnabled(True)
        # 选择内容的行为：行高亮
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置表格交叉颜色
        self.tableView.setAlternatingRowColors(True)

        # self.tableView.setTextElideMode()
        # 单击绑定槽函数
        self.tableView.clicked.connect(self.on_tableView_clicked)
        # self.tableView.clicked.connect(self.on_tableView_clicked)
        # delegate = TableDelegate()
        # self.tableView.setItemDelegate(delegate)
        self.setLayout(layout)

    def gettickdata(self, df):
        """从tushare获取tick数据数据，symbol可以是一个list，则返回多条数据（dataframe）"""
        symbols = df['code'].tolist()
        self.ts_df = ts.get_realtime_quotes(symbols)  # stock symbol list
        self.ts_df = self.ts_df[['code', 'name', 'pre_close', 'price']]

        self.ts_df[['pre_close', 'price']] = self.ts_df[['pre_close', 'price']].astype(float)
        self.ts_df['change_rate'] = round((self.ts_df['price'] / self.ts_df['pre_close'] - 1) * 100, 2) # 当日变化
        self.ts_df = self.ts_df[['code', 'name', 'price','pre_close','change_rate']]
        self.df = pd.merge(df, self.ts_df, on='code')
        self.df['profit_rate'] = round((self.df['price'] / self.df['cost'] - 1) * 100, 2)  # 利润率
        self.df['value'] = round(self.df['price'] * self.df['qty']/10000, 2)  # 市值
        self.total_value = round(self.df['value'].sum(),2)
        self.df['position'] = round(self.df['value'] /self.total_value*100,1)
        self.df['profit'] = round((self.df['price'] - self.df['cost'])*self.df['qty']/1000, 1)
        self.df['profit2'] = round((self.df['price'] - self.df['pre_close']) * self.df['qty']/1000, 1)

        self.df = self.df[['code', 'name', 'position', 'cost', 'price','value', 'profit2','change_rate', 'profit','profit_rate']].sort_values\
            (by='change_rate',ascending=False)
        self.total_profit = self.df['profit'].sum()
        self.total_day = self.df['profit2'].sum()

        # print(self.df)
        return self.df

    def update_data_to_model(self,dataframe):
        """ 把dataframe数据关联到model"""

        # 更新model数据前，先清空之前的数据
        self.model.removeColumns(self.model.columnCount(), 0)

        # 开始关联数据
        for index in dataframe.index:
            data = dataframe.iloc[index]
            self.upDataModel(data, index)
        # 设置汇总行的行标
        x = max(dataframe.index)+1
        # 设置汇总行要显示的内容
        self.model.setItem(x, 1, QStandardItem('汇总')) # 这一行为了点击该行时，不会发生错误

        self.model.setItem(x, 5, QStandardItem(str(self.total_value)))
        self.model.setItem(x, 6, QStandardItem(str(self.total_day)))
        self.model.setItem(x, 8, QStandardItem(str(self.total_profit)))


    def upDataModel(self,data,index):
        """把series（单行） 数据添加到model中去"""

        col = len(data)
        for i in range(0,col):
            self.model.setItem(index, i, QStandardItem(str(data[i])))

    def setForeground(self,name,column):
        """设置某一列的字体颜色"""
        # 首先获取总行数
        row = self.model.rowCount()
        for index in range(0,row-1):
            wave = self.df.iloc[index][name]
            if wave > 0:
                self.model.item(index, column).setForeground(QBrush(QColor("red")))
            elif wave == 0:
                self.model.item(index, column).setForeground(QBrush(QColor("white")))
            else:
                self.model.item(index, column).setForeground(QBrush(QColor("green")))

    def on_tableView_clicked(self, index):
        """
        单击显示图书详细信息
        当我们单击表格的时候，取得行号。
        因为我们的数据来源都是数据模型，我们就根据模型中第几行第几个字段取得相应的值
        """
        row = index.row()
        # print(self.model.record(row).value("code"))
        # 获取鼠标单击的单元格值
        print(self.model.item(row,1).text())
        # DetailTable().setdata(self.df)

    def showContextMenu(self):
        """创建右键菜单"""
        self.tableView.contextMenu = QMenu(self)

        # self.actionA = self.view.contextMenu.exec_(self.mapToGlobal(pos))  # 1
        self.tableView.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        self.actionA = self.tableView.contextMenu.addAction('动作a')
        self.actionA.triggered.connect(self.actionHandler)

        # self.tableView.contextMenu.move(self.pos())  # 3
        self.tableView.contextMenu.show()

    def actionHandler(self):
        # 计算有多少条数据，默认-1,
        row_num = -1
        for i in self.tableView.selectionModel().selection().indexes():
            row_num = i.row()
        print('动作a', row_num)
        print('你选了选项一，当前行文字内容是：',self.model.record(row_num).value("country"))

class BaseDFTable(QWidget):
    """利用DataFrame新建Qtableview的显示控件"""
    columnName = []

    def __init__(self):
        super(BaseDFTable, self).__init__()

        self.initUI()

    def initUI(self):

        # 水平布局，初始表格5*3，添加到布局
        layout = QHBoxLayout()
        self.dataView = QTableView()
        self.dataView.setObjectName("dataView")
        # font = self.dataView.horizontalHeader().font()  # 获取当前表头的字体
        # font.setFamily("微软雅黑")  # 修改字体设置
        # self.dataView.horizontalHeader().setFont(font)  # 重新设置表头的字体

        # 设置表头背景色
        # self.dataView.horizontalHeader().setStyleSheet("QHeaderView::section{background:blue;}")

        # 设置表格横向/纵向填满整个layout
        self.dataView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dataView.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格列与行尺寸适用内容
        self.dataView.resizeColumnsToContents()
        self.dataView.resizeRowsToContents()
        # 选择内容的行为：行高亮
        self.dataView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 连接单击槽函数
        # self.dataView.clicked.connect(self.on_tableView_clicked)
        # 允许右键产生菜单，如果不设为CustomContextMenu,无法使用customContextMenuRequested
        self.dataView.setContextMenuPolicy(Qt.CustomContextMenu)

        # 将右键菜单绑定到槽函数showContextMenu
        # self.dataView.customContextMenuRequested.connect(self.showContextMenu)

        # 将右键菜单绑定到槽函数generateMenu
        # self.dataView.customContextMenuRequested.connect(self.generateMenu)

        # 开启按列排序功能
        self.dataView.setSortingEnabled(True)

        # 设置行名隐藏
        self.dataView.verticalHeader().setVisible(False)
        # 设置行名隐藏
        # self.dataView.horizontalHeader().setVisible(False)

        # 隐藏不需要的列，必须放在在setModel之后才能生效，从第0列开始
        self.dataView.hideColumn(1)
        self.dataView.setFont(QFont("Arial", 13))

        # 设置表格交叉颜色
        self.dataView.setAlternatingRowColors(True)

        # 新建一个layout
        layout = QHBoxLayout()
        # 将表格控件添加到layout中去
        layout.addWidget(self.dataView)

        self.dataView.clicked.connect(self.on_tableView_clicked)
        # 设置layout
        self.setLayout(layout)

    def update_model(self,data):
        # self.model = DataFrameTableModel(data)
        # data = self.resetColumnName(data,NewName=self.columnName)
        print('self.model')
        self.model = pandasModel(data)
        print(data)
        self.dataView.setModel(self.model)
        print('finished set')
        # print(u'处理每秒触发的计时器事件：%s' % str(datetime.now()))

        # if '涨跌幅(%)' in data.columns:
        #     self.setColumnColor(columnName='涨跌幅(%)')
        #
        # if '利润率(%)' in data.columns:
        #     self.setColumnColor(columnName='利润率(%)')

    def setCellColor(self, row, column,color):
        """color:Qt.darkGreen"""
        self.model.change_color(row, column, QBrush(color))

    def setColumnColor(self,columnName):

        row = self.model.rowCount()
        self._df = self.model._data
        column = self._df.columns.get_loc(columnName)
        for index in range(0, row):
            wave = self._df.iloc[index,column]
            if wave > 0:
                self.setCellColor(index,column,Qt.red)
            elif wave < 0:
                self.setCellColor(index, column, Qt.darkGreen)

    def resetColumnName(self,df,NewName:list):
        self._df = df
        index = self._df.columns
        count =  min(len(index),len(NewName))
        for i in range(0,count):
            self._df.rename(columns={index[i]: NewName[i]}, inplace=True)
        return self._df

    def on_tableView_clicked(self, index):
        """
        单击获取行信息
        """
        row = index.row()
        name = self.model._data.iloc[row][1]
        # print(self.df[self.df['代码'] == self.model._data.iloc[row]['代码']])
        # print(self.model.flags(index))

        if name != "汇总":
            code = self.model._data.iloc[row][0]
            # print(code)
            if code is not None:
                self.kWindow = QtGui.QMainWindow()
                self.ui = Kchart_MainWindow(code=code, name=name)
                self.ui.setupUi(self.kWindow)
                self.kWindow.show()



    def showContextMenu(self):  # 创建右键菜单
        self.dataView.contextMenu = QMenu(self)

        # self.actionA = self.view.contextMenu.exec_(self.mapToGlobal(pos))  # 1
        self.dataView.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        self.actionA = self.dataView.contextMenu.addAction('动作a')
        self.actionA.triggered.connect(self.actionHandler)

        self.action2 = self.dataView.contextMenu.addAction('动作2')
        self.action2.triggered.connect(self.actionHandler)

        # self.view.contextMenu.move(self.pos())  # 3
        self.dataView.contextMenu.show()

    def actionHandler(self):
        # 计算有多少条数据，默认-1,
        row_num = -1
        for i in self.dataView.selectionModel().selection().indexes():
            row_num = i.row()

        print('动作a', row_num)

        print('你选了选项一，当前行文字内容是：')

class BaseDBTable(QWidget):
    """从SQLite数据库生成模型，并显示的基类"""
    dbpath = ''
    dbtable = ""
    tableheader = []

    def __init__(self):
        super(BaseDBTable, self).__init__()
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.dbpath)
        self.initModel()
        self.initUI()

    def initModel(self):
        # 定义数据模型
        self.model = QSqlTableModel()
        # 将模型操作的数据库表设置为tableName。 不从表中选择数据，而是获取其字段信息。
        self.model.setTable(self.dbtable)
        # 设置数据库中的值编辑策略。这里有三种，如下表：1. OnFieldChange 立即更改 2. OnManualSubmit 人工确认提交
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        # 要使用表的数据填充模型，请调用select()。可以使用lastError()检索错误信息。
        self.model.select()
        # 重新设置表格头的显示名称
        ColumnsNum = len(self.tableheader)
        if ColumnsNum > 0:
            for index in range(0, ColumnsNum):
                self.model.setHeaderData(index, Qt.Horizontal, self.tableheader[index])

    def initUI(self):

        # 设置表格布局
        layout = QHBoxLayout()
        self.tableView = QTableView()
        layout.addWidget(self.tableView)
        # 给表格控件设置数据模型
        self.tableView.setModel(self.model)
        self.tableView.setFont(QFont("Arial", 10))
        # 隐藏表格的列名称
        self.tableView.verticalHeader().hide()
        # 设置表格横向/纵向填满整个layout
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格宽度适合内容
        # self.tableView.resizeColumnsToContents()

        # 开启按列排序功能
        self.tableView.setSortingEnabled(True)

        # 选择内容的行为：行高亮
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 允许右键产生菜单，如果不设为CustomContextMenu,无法使用customContextMenuRequested
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)

        # 将右键菜单绑定到槽函数showContextMenu
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)

        # 单击绑定槽函数
        self.tableView.clicked.connect(self.on_tableView_clicked)
        # self.tableView.clicked.connect(self.on_tableView_clicked)
        # delegate = TableDelegate()
        # self.tableView.setItemDelegate(delegate)
        self.setLayout(layout)


    def on_tableView_clicked(self, index):
        """
        单击显示图书详细信息
        当我们单击表格的时候，取得行号。
        因为我们的数据来源都是数据模型，我们就根据模型中第几行第几个字段取得相应的值
        """
        row = index.row()
        print(self.model.record(row).value("country"))

    def showContextMenu(self):  # 创建右键菜单
        self.tableView.contextMenu = QMenu(self)

        # self.actionA = self.view.contextMenu.exec_(self.mapToGlobal(pos))  # 1
        self.tableView.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        self.actionA = self.tableView.contextMenu.addAction('动作a')
        self.actionA.triggered.connect(self.actionHandler)

        # self.tableView.contextMenu.move(self.pos())  # 3
        self.tableView.contextMenu.show()

    def actionHandler(self):
        # 计算有多少条数据，默认-1,
        row_num = -1
        for i in self.tableView.selectionModel().selection().indexes():
            row_num = i.row()
        print('动作a', row_num)
        print('你选了选项一，当前行文字内容是：',self.model.record(row_num).value("country"))

class BaseModelFlash(QDialog):
    """a demo of  get data from sina,
    Python3.3 + PyQt5 IDE: PyCharm 3.0"""
    # 初始化Model的列名
    ModelHeader = []
    CodeList = []

    def __init__(self, parent=None):
        super(BaseModelFlash, self).__init__(parent)

        # self.resize(600, 950)
        self.openFilesPath = ''

        self.errorMessageDialog = QErrorMessage(self)

        # subLayout = QHBoxLayout()

        # 建立表格控件，用于显示表格数据
        self.dataView = QTableView()
        # 建立model,横向
        ColumsNum = len(self.ModelHeader)
        self.model = QStandardItemModel(0, ColumsNum, self)
        i = 0
        # 设置model 的行名称
        for i in ColumsNum:
            self.model.setHorizontalHeaderItem(0, QStandardItem(self.ModelHeader[i]))

        # 隐藏表格的列名称
        self.dataView.verticalHeader().hide()
        # 设置表格字号大小
        self.dataView.setFont(QFont("Arial", 12))

        self.dataView.setModel(self.model)

        # 设置表格view的列宽
        # self.dataView.setColumnWidth(0,60)

        self.dataView.resizeColumnsToContents()
        self.dataView.resizeRowsToContents()
        self.dataView.hideColumn(1)
        self.dataView.hideColumn(2)

        layout = QVBoxLayout()
        # layout.addWidget(self.codeLineEdit)
        # layout.addLayout(subLayout)
        layout.addWidget(self.dataView)
        self.setLayout(layout)

        self.setWindowTitle("Stock Viewer")
        # 通过按钮运行更新
        # self.integerButton.clicked.connect(self.onShowButtonClick)
        self.stopRefreshButton.clicked.connect(self.stopRefresh)
        # 自动运行更新
        self.onShowButtonClick()

    def stopRefresh(self):
        """停止刷新行情 """

        print("Stop")
        self.timer.stop()
        self.stopRefreshButton.setEnabled(False)
        self.integerButton.setEnabled(True)
        self.integerButton.setText("Show")


    def __request(self, symbol):
        """从新浪网爬虫数据，list后面可以跟一个列表，则返回多条数据"""

        url = "http://hq.sinajs.cn/?list=%s" % symbol
        return urllib.request.urlopen(url, data=None, timeout=500).read().decode('gbk')

    def processInputString(self):
        """处理输入的代码，得到一个新的字符串"""

        # 获取输入控件中的代码
        self.textSymbol = self.codeLineEdit.text()
        # 把空格去除
        symbolText = self.textSymbol.replace(' ', '')
        # 获得一个代码列表
        symbolArray = symbolText.split(',')

        # print(type(symbolArray))

        self.symbolString = ""
        for symbol in symbolArray:
            # 去除首尾指定的字符
            symbol = symbol.strip()

            # 上证 股票以6开头，基金以5开头，B股以9开头
            if len(symbol) == 0:
                return
            if symbol[0] == '6' or symbol[0] == '5' or symbol[0] == '9':
                symbol = "sh" + symbol
            # 深证 股票以3，0开头，基金以1开头, B股以2开头
            if symbol[0] == '3' or symbol[0] == '0' or symbol[0] == '1' or symbol[0] == '2':
                symbol = "sz" + symbol
            if len(self.symbolString) > 0:
                self.symbolString = self.symbolString + "," + symbol
            else:
                self.symbolString = symbol

    def onShowButtonClick(self):
        '''开始刷新行情'''
        self.refreshNum = 0
        # 获取数据
        self.getStockData()
        # 建立一个计时器
        self.timer = QTimer()
        # 如果超时，则再次获取数据
        self.timer.timeout.connect(self.getStockData)
        self.timer.start(2000)

        # self.stopRefreshButton.setEnabled(True)
        # self.integerButton.setEnabled(False)
        # self.integerButton.setText("刷新中")

    def getStockData(self):
        """ 获取爬虫交易数据"""

        # print("refresh")
        # 处理输入的代码，返回一个代码的string
        self.processInputString()

        # 更新前，先清空之前的数据
        self.model.removeColumns(self.model.columnCount(),0)

        index = 0
        # 获取N条交易数据，返回列表
        dataArray = self.__request(self.symbolString).split(';')
        # print(dataArray)
        for textPiece in dataArray:
            data = textPiece.split(',')
            if len(data) == 1:
                continue
            # 处理数据，并把值对应到表格model中
            self.upDataModel(data, index)
            index += 1
        self.refreshNum += 1

    def upDataModel(self, data, colNum):

        name = data[0].split('\"')[1]
        code = data[0].split('_')[2].split('=')[0]

        # 给表格模型赋值
        self.model.setItem(colNum, 0,QStandardItem(name))
        self.model.setItem(colNum, 1, QStandardItem(code))
        self.model.setItem(colNum, 2, QStandardItem(data[30]))
        self.model.setItem(colNum, 3, QStandardItem(data[31]))
        self.model.setItem(colNum, 4, QStandardItem(data[1]))
        self.model.setItem(colNum, 5, QStandardItem(data[2]))

        curPriceItem = QStandardItem(data[3])
        self.model.setItem(colNum, 6,curPriceItem)

        changeNum = ((float(data[3])/float(data[2]) - 1.0) * 100)
        changeStr = "%.2f%%" % changeNum
        curChangeItem = QStandardItem(str(changeStr))

        if changeNum > 0.0:
            curChangeItem.setForeground(QBrush(QColor("red")))
            self.model.item(colNum, 6).setForeground(QBrush(QColor("red")))
        else:
            curChangeItem.setForeground(QBrush(QColor("green")))
            self.model.item(colNum, 6).setForeground(QBrush(QColor("green")))
        self.model.setItem(colNum, 7,curChangeItem)

        self.model.setItem(colNum, 8,QStandardItem(data[4]))
        self.model.setItem(colNum, 9,QStandardItem(data[5]))

        volume = float(data[8])
        volumeStr = "%.2f" % (volume / 1000000)
        self.model.setItem(colNum, 10,QStandardItem(volumeStr))

        turnover = float(data[9])
        if turnover > 1e8:
            turnoverStr = "%.2f亿" % (turnover / 100000000)
        else:
            turnoverStr = "%.2f万" % (turnover / 10000)
        self.model.setItem(colNum, 11,QStandardItem(turnoverStr))

        myBtn = QPushButton("点击")
        myBtn.setAccessibleDescription(code)
        myBtn.clicked.connect(self.showStockPages)

        self.model.setItem(colNum, 12,QStandardItem())
        parent = self.model.item(colNum, 12)

        # 获取当前model行与列
        index = self.model.indexFromItem(parent)

        # 设置按钮在表格控件中的位置
        self.dataView.setIndexWidget(index, myBtn)

    def showStockPages(self):

        sender = self.sender()
        url = "http://finance.sina.com.cn/realstock/company/" + sender.accessibleDescription() + "/nc.shtml"
        QDesktopServices.openUrl(QUrl(url))

class BaseStandardTable2(QWidget):

    """a demo of  get tick data from tushare,
    注：tushare 必须升级到 1.4.2版本以上
    Python3.3 + PyQt5 IDE: PyCharm 3.0"""

    tableheader = []
    def __init__(self):
        super(BaseStandardTable2, self).__init__()

        self.initModel()
        self.initUI()
        # 自动更新行情
        # self.createQtimer()

    def initModel(self):
        # 定义数据模型
        self.model = QStandardItemModel(self)

        # 重新设置表格头的显示名称
        ColumnsNum = len(self.tableheader)
        if ColumnsNum > 0:
            for index in range(0, ColumnsNum):
                self.model.setHorizontalHeaderItem(index, QStandardItem(self.tableheader[index]))

    def initUI(self):

        # 设置表格布局
        layout = QHBoxLayout()
        self.tableView = QTableView()
        layout.addWidget(self.tableView)
        # 给表格控件设置数据模型
        self.tableView.setModel(self.model)
        self.tableView.setFont(QFont("Arial", 12))
        # 隐藏表格的列名称
        self.tableView.verticalHeader().hide()
        # 设置表格横向/纵向填满整个layout
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格宽度适合内容
        # self.tableView.resizeColumnsToContents()
        # 开启按列排序功能
        self.tableView.setSortingEnabled(True)
        # 选择内容的行为：行高亮
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置表格交叉颜色
        self.tableView.setAlternatingRowColors(True)

        # 单击绑定槽函数
        self.tableView.clicked.connect(self.showKChart)

        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)
        # self.tableView.clicked.connect(self.on_tableView_clicked)
        # delegate = TableDelegate()
        # self.tableView.setItemDelegate(delegate)
        self.setLayout(layout)

    def update_data_to_model(self,dataframe,account):
        """ 把dataframe数据关联到model"""

        # 更新model数据前，先清空之前的数据
        self.model.removeColumns(self.model.columnCount(), 0)
        self.account  = account

        # 开始关联数据
        for index in dataframe.index:
            data = dataframe.iloc[index]
            self.upDataModel(data, index)

    def upDataModel(self,data,index):
        """把series（单行） 数据添加到model中去"""

        col = len(data)
        for i in range(0,col):
            self.model.setItem(index, i, QStandardItem(str(data[i])))
            # 设置对齐方式
            self.model.item(index,i).setTextAlignment(Qt.AlignCenter)


    def setForeground(self,byname,column):
        """设置某一列的字体颜色  byname 为df的列名，根据这一列的值判断 """
        # 首先获取总行数
        row = self.model.rowCount()
        for index in range(0,row-1):
            wave = self.df.iloc[index][byname]
            if wave > 0:
                self.model.item(index, column).setForeground(QBrush(QColor("red")))
            elif wave == 0:
                self.model.item(index, column).setForeground(QBrush(QColor("white")))
            else:
                self.model.item(index, column).setForeground(QBrush(QColor("green")))

    def setForeground_LastLine(self,value,index,column):
        """设置单一行的字体颜色 value为判断阈值，index 和column分别为行与列标"""
        # 首先获取总行数
        if value > 0:
            self.model.item(index, column).setForeground(QBrush(QColor("red")))
            # self.model.item(index,column).setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        elif value == 0:
            self.model.item(index, column).setForeground(QBrush(QColor("white")))
        else:
            self.model.item(index, column).setForeground(QBrush(QColor("green")))

    def on_tableView_clicked(self, index):
        """
        单击显示图书详细信息
        当我们单击表格的时候，取得行号。
        因为我们的数据来源都是数据模型，我们就根据模型中第几行第几个字段取得相应的值
        """
        row = index.row()
        # print(self.model.record(row).value("code"))
        # 获取鼠标单击的单元格值
        print(self.model.item(row,1).text())
        # DetailTable().setdata(self.df)

    def showContextMenu(self,pos):
        """创建右键菜单"""
        self.tableView.contextMenu = QMenu(self)

        row_num = -1
        for i in self.tableView.selectionModel().selection().indexes():
            row_num = i.row()
        self.tableView.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        code = self.model.item(row_num, 0).text()
        name = self.model.item(row_num, 1).text()
        data_buy = [code, name, '买入',self.account]
        data_sell = [code, name, '卖出',self.account]
        cost = self.model.item(row_num, 4).text()
        data_ZQ = [code, name, '中签卖出',self.account,cost]

        self.actionBuy = self.tableView.contextMenu.addAction('买入')
        self.actionBuy.triggered.connect(lambda: self.actionHandler(data_buy))

        self.actionSell = self.tableView.contextMenu.addAction('卖出')
        self.actionSell.triggered.connect(lambda: self.actionHandler(data_sell))

        self.actionZQ = self.tableView.contextMenu.addAction('中签卖出')
        self.actionZQ.triggered.connect(lambda: self.actionHandler(data_ZQ))

        self.actionTQ = self.tableView.contextMenu.addAction('填权处理')
        self.actionTQ.triggered.connect(lambda: self.stockprocessprice(data_buy))

        self.tableView.contextMenu.show()

    def actionHandler(self,option):

        self.dialog_trading = Trading(option)
        self.dialog_trading.show()

    def stockprocessprice(self,option):
        """填权处理对话框"""
        self.dialog_stock = stcokprocess(option)
        self.dialog_stock.show()

    def showKChart(self,index):
        row = index.row()
        # 获取鼠标单击的单元格值
        name = self.model.item(row, 1).text()
        if name != "汇总":
            code = self.model.item(row, 0).text()
            self.kWindow = QtGui.QMainWindow()
            self.ui = Kchart_MainWindow(code=code,name=name)
            self.ui.setupUi(self.kWindow)
            self.kWindow.show()
