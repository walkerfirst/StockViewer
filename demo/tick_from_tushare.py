#!/usr/bin/env python

import sys
import tushare as ts
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor, QFont, QDesktopServices
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import qdarkstyle
from setting.symbols import index_symbols
from DataEngine import DataEngineSina

class StockViewerDialog(QDialog):
    """a demo of  get tick data from tushare,
    注：tushare 必须升级到 1.4.2版本以上
    Python3.3 + PyQt5 IDE: PyCharm 3.0"""

    def __init__(self, parent=None):
        super(StockViewerDialog, self).__init__(parent)

        self.resize(600, 950)
        self.openFilesPath = ''

        self.errorMessageDialog = QErrorMessage(self)

        self.codeLineEdit = QLineEdit()
        self.codeLineEdit.setText('002463,399001,399006')

        subLayout = QHBoxLayout()

        self.integerButton = QPushButton("显示")
        self.stopRefreshButton = QPushButton("停止")
        subLayout.addWidget(self.codeLineEdit)
        subLayout.addWidget(self.integerButton)
        subLayout.addWidget(self.stopRefreshButton)
        # 建立表格控件，用于显示表格数据
        self.dataView = QTableView()
        # 建立model
        self.model = QStandardItemModel(self)
        # 设置model 的行名称
        self.model.setHorizontalHeaderItem(0, QStandardItem("股票名称"))
        self.model.setHorizontalHeaderItem(1, QStandardItem("股票代号"))
        self.model.setHorizontalHeaderItem(2, QStandardItem("日期"))
        self.model.setHorizontalHeaderItem(3, QStandardItem("时间"))
        # self.model.setHorizontalHeaderItem(4, QStandardItem("今日开盘价"))
        self.model.setHorizontalHeaderItem(4, QStandardItem("昨日收盘价"))
        self.model.setHorizontalHeaderItem(5, QStandardItem("当前价格"))
        self.model.setHorizontalHeaderItem(6, QStandardItem("涨跌幅"))
        # self.model.setHorizontalHeaderItem(8, QStandardItem("今日最高价"))
        # self.model.setHorizontalHeaderItem(9, QStandardItem("今日最低价"))
        # self.model.setHorizontalHeaderItem(10, QStandardItem("成交量(万手)"))
        # self.model.setHorizontalHeaderItem(11, QStandardItem("成交金额(元)"))
        self.model.setHorizontalHeaderItem(7, QStandardItem("详情"))
        # 隐藏表格的列名称
        self.dataView.verticalHeader().hide()
        # 设置表格字号大小
        self.dataView.setFont(QFont("Arial", 11))
        # 设置表格交叉颜色
        self.dataView.setAlternatingRowColors(True)

        self.dataView.setModel(self.model)
        # self.dataView.setColumnWidth(0,60)
        # self.dataView.setColumnWidth(1, 60)
        # self.dataView.setColumnWidth(2, 60)
        # self.dataView.setColumnWidth(3, 60)
        # self.dataView.setColumnWidth(4, 60)
        # self.dataView.setColumnWidth(5, 60)
        # self.dataView.setColumnWidth(6, 80)
        # self.dataView.setColumnWidth(7, 80)
        # self.dataView.setColumnWidth(8, 80)
        # self.dataView.setColumnWidth(9, 80)
        # self.dataView.setColumnWidth(10, 80)
        # self.dataView.setColumnWidth(11, 80)
        self.dataView.resizeColumnsToContents()
        self.dataView.resizeRowsToContents()
        # 设置表格横向/纵向填满整个layout
        self.dataView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dataView.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
        # print('2',symbol)
        # df = ts.get_realtime_quotes(symbol)  # Single stock symbol
        # # print(df)
        # df = df[['code','name','date','time','pre_close','price']]
        # df[['pre_close', 'price']] = df[['pre_close', 'price']].astype(float)
        # df['rate'] = df['price']/df['pre_close']-1
        # df = df.sort_values(by='rate', ascending=False)
        # df[['pre_close', 'price']] = df[['pre_close', 'price']].astype(str)
        # # print(df)

        df = DataEngineSina(symbol).data
        return df


    def onShowButtonClick(self):
        '''开始刷新行情'''
        self.refreshNum = 0
        # 获取数据
        self.getStockData()
        # 建立一个计时器
        self.timer = QTimer()
        # 如果超时，则再次获取数据
        self.timer.timeout.connect(self.getStockData)
        self.timer.start(20000)

        self.stopRefreshButton.setEnabled(True)
        self.integerButton.setEnabled(False)
        self.integerButton.setText("刷新中")

    def getStockData(self):
        """ 获取爬虫交易数据"""


        # 更新前，先清空之前的数据
        self.model.removeColumns(self.model.columnCount(),0)

        index = 0
        # 获取N条交易数据，返回列表
        self.symbolString = index_symbols
        # dataArray = pd.DataFrame()

        dataArray = self.__request(self.symbolString)

        for index in dataArray.index:
            # print(index)
            data = dataArray.iloc[index]
            # print(data)
            self.upDataModel(data, index)

        # self.refreshNum += 1

    def upDataModel(self, data, colNum):

        name = data['name']
        code = data['code']

        # 给表格模型赋值
        self.model.setItem(colNum, 0,QStandardItem(name))
        self.model.setItem(colNum, 1,QStandardItem(code))
        self.model.setItem(colNum, 2,QStandardItem(data['date']))
        self.model.setItem(colNum, 3, QStandardItem(data['time']))
        # self.model.setItem(colNum, 4, QStandardItem(data['open']))
        self.model.setItem(colNum, 4,QStandardItem(data['pre_close']))

        curPriceItem = QStandardItem(data['price'])
        self.model.setItem(colNum, 5,curPriceItem)

        changeNum = ((float(data['price'])/float(data['pre_close']) - 1.0) * 100)
        changeStr = "%.2f%%" % changeNum
        curChangeItem = QStandardItem(str(changeStr))

        if changeNum > 0.0:
            curChangeItem.setForeground(QBrush(QColor("red")))
            self.model.item(colNum, 5).setForeground(QBrush(QColor("red")))
        else:
            curChangeItem.setForeground(QBrush(QColor("green")))
            self.model.item(colNum, 5).setForeground(QBrush(QColor("green")))
        self.model.setItem(colNum, 6,curChangeItem)

        # self.model.setItem(colNum, 8,QStandardItem(data['high']))
        # self.model.setItem(colNum, 9,QStandardItem(data['low']))

        # volume = float(data['volume'])
        # volumeStr = "%.2f" % (volume / 1000000)
        # self.model.setItem(colNum, 10,QStandardItem(volumeStr))
        #
        # turnover = float(data['amount'])
        # if turnover > 1e8:
        #     turnoverStr = "%.2f亿" % (turnover / 100000000)
        # else:
        #     turnoverStr = "%.2f万" % (turnover / 10000)
        # self.model.setItem(colNum, 11,QStandardItem(turnoverStr))

        myBtn = QPushButton(changeStr)
        myBtn.setAccessibleDescription(code)
        myBtn.clicked.connect(self.showStockPages)

        self.model.setItem(colNum, 7,QStandardItem())
        parent = self.model.item(colNum, 7)

        # 获取当前model行与列
        index = self.model.indexFromItem(parent)

        # 设置按钮在表格控件中的位置
        self.dataView.setIndexWidget(index, myBtn)

    def showStockPages(self):

        sender = self.sender()
        url = "http://finance.sina.com.cn/realstock/company/sz" + sender.accessibleDescription() + "/nc.shtml"
        QDesktopServices.openUrl(QUrl(url))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    dialog = StockViewerDialog()
    dialog.show()
    sys.exit(app.exec_())
