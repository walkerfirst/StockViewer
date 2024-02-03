#!/usr/bin/env python

import sys
import urllib.request

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor, QFont, QDesktopServices
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import qdarkstyle


class StockViewerDialog(QDialog):
    """a demo of  get data from sina,
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
        self.model = QStandardItemModel(0, 12, self)
        # 设置model 的行名称
        self.model.setHorizontalHeaderItem(0, QStandardItem("股票名称"))
        self.model.setHorizontalHeaderItem(1, QStandardItem("股票代号"))
        self.model.setHorizontalHeaderItem(2, QStandardItem("日期"))
        self.model.setHorizontalHeaderItem(3, QStandardItem("时间"))
        self.model.setHorizontalHeaderItem(4, QStandardItem("今日开盘价"))
        self.model.setHorizontalHeaderItem(5, QStandardItem("昨日收盘价"))
        self.model.setHorizontalHeaderItem(6, QStandardItem("当前价格"))
        self.model.setHorizontalHeaderItem(7, QStandardItem("涨跌幅"))
        self.model.setHorizontalHeaderItem(8, QStandardItem("今日最高价"))
        self.model.setHorizontalHeaderItem(9, QStandardItem("今日最低价"))
        self.model.setHorizontalHeaderItem(10, QStandardItem("成交量(万手)"))
        self.model.setHorizontalHeaderItem(11, QStandardItem("成交金额(元)"))
        self.model.setHorizontalHeaderItem(12, QStandardItem("详情"))
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

        self.stopRefreshButton.setEnabled(True)
        self.integerButton.setEnabled(False)
        self.integerButton.setText("刷新中")

    def getStockData(self):
        """ 获取爬虫交易数据"""

        print("refresh")
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
        # self.refreshNum += 1

    def upDataModel(self, data, colNum):

        name = data[0].split('\"')[1]
        code = data[0].split('_')[2].split('=')[0]

        # 给表格模型赋值
        self.model.setItem(colNum, 0,QStandardItem(name))
        self.model.setItem(colNum, 1,QStandardItem(code))
        self.model.setItem(colNum, 2,QStandardItem(data[30]))
        self.model.setItem(colNum, 3, QStandardItem(data[31]))
        self.model.setItem(colNum, 4, QStandardItem(data[1]))
        self.model.setItem(colNum, 5,QStandardItem(data[2]))

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    dialog = StockViewerDialog()
    dialog.show()
    sys.exit(app.exec_())
