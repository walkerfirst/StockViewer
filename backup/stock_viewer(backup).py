#!/usr/bin/env python

import sys
import urllib.request
from PandasModel import PandasModel


from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor, QFont, QDesktopServices
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import qdarkstyle


class StockViewerDialog(QDialog):

    def __init__(self, parent=None):
        super(StockViewerDialog, self).__init__(parent)

        self.resize(600, 950)
        self.openFilesPath = ''

        self.errorMessageDialog = QErrorMessage(self)

        self.codeLineEdit = QLineEdit()
        self.codeLineEdit.setText('002463')

        subLayout = QHBoxLayout()

        self.integerButton = QPushButton("Show")
        self.stopRefreshButton = QPushButton("Stop Refresh")

        subLayout.addWidget(self.integerButton)
        subLayout.addWidget(self.stopRefreshButton)
        # 建立表格控件，用于显示表格数据
        self.dataView = QTableView()
        # 建立model
        self.model = QStandardItemModel(12, 0, self)
        # 设置model 的行名称
        self.model.setVerticalHeaderItem(0, QStandardItem("股票名称"))
        self.model.setVerticalHeaderItem(1, QStandardItem("股票代号"))
        self.model.setVerticalHeaderItem(2, QStandardItem("日期"))
        self.model.setVerticalHeaderItem(3, QStandardItem("时间"))
        self.model.setVerticalHeaderItem(4, QStandardItem("今日开盘价"))
        self.model.setVerticalHeaderItem(5, QStandardItem("昨日收盘价"))
        self.model.setVerticalHeaderItem(6, QStandardItem("当前价格"))
        self.model.setVerticalHeaderItem(7, QStandardItem("涨跌幅"))
        self.model.setVerticalHeaderItem(8, QStandardItem("今日最高价"))
        self.model.setVerticalHeaderItem(9, QStandardItem("今日最低价"))
        self.model.setVerticalHeaderItem(10, QStandardItem("成交量(万手)"))
        self.model.setVerticalHeaderItem(11, QStandardItem("成交金额(元)"))
        self.model.setVerticalHeaderItem(12, QStandardItem("详情"))
        # 隐藏表格的列名称
        self.dataView.horizontalHeader().hide()
        # 设置表格字号大小
        self.dataView.setFont(QFont("SimSun", 10))

        self.dataView.setModel(self.model)
        self.dataView.setRowHeight(0, 25)
        self.dataView.setRowHeight(1, 25)
        self.dataView.setRowHeight(2, 25)
        self.dataView.setRowHeight(3, 25)
        self.dataView.setRowHeight(4, 25)
        self.dataView.setRowHeight(5, 25)
        self.dataView.setRowHeight(6, 25)
        self.dataView.setRowHeight(7, 25)
        self.dataView.setRowHeight(8, 25)
        self.dataView.setRowHeight(9, 25)
        self.dataView.setRowHeight(10, 25)
        self.dataView.setRowHeight(11, 25)

        layout = QVBoxLayout()
        layout.addWidget(self.codeLineEdit)
        layout.addLayout(subLayout)
        layout.addWidget(self.dataView)
        self.setLayout(layout)

        self.setWindowTitle("Stock Viewer")

        self.integerButton.clicked.connect(self.onShowButtonClick)
        self.stopRefreshButton.clicked.connect(self.stopRefresh)

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
        self.integerButton.setText("Refreshing")

    def getStockData(self):
        """ 获取爬虫交易数据"""

        print("refresh")
        # 处理输入的代码
        self.processInputString()

        # 更新前，先清空之前的数据
        self.model.removeColumns(0, self.model.columnCount())

        index = 0
        # 获取交易数据，返回列表
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
        self.model.setItem(0, colNum, QStandardItem(name))
        self.model.setItem(1, colNum, QStandardItem(code))
        self.model.setItem(2, colNum, QStandardItem(data[30]))
        self.model.setItem(3, colNum, QStandardItem(data[31]))
        self.model.setItem(4, colNum, QStandardItem(data[1]))
        self.model.setItem(5, colNum, QStandardItem(data[2]))

        curPriceItem = QStandardItem(data[3])
        self.model.setItem(6,colNum, curPriceItem)

        changeNum = ((float(data[3])/float(data[2]) - 1.0) * 100)
        changeStr = "%.2f%%" % changeNum
        curChangeItem = QStandardItem(str(changeStr))

        if changeNum > 0.0:
            curChangeItem.setForeground(QBrush(QColor("red")))
            self.model.item(6, colNum).setForeground(QBrush(QColor("red")))
        else:
            curChangeItem.setForeground(QBrush(QColor("green")))
            self.model.item(6, colNum).setForeground(QBrush(QColor("green")))
        self.model.setItem(7, colNum, curChangeItem)

        self.model.setItem(8, colNum, QStandardItem(data[4]))
        self.model.setItem(9, colNum, QStandardItem(data[5]))

        volume = float(data[8])
        volumeStr = "%.2f" % (volume / 1000000)
        self.model.setItem(10, colNum, QStandardItem(volumeStr))

        turnover = float(data[9])
        if turnover > 1e8:
            turnoverStr = "%.2f亿" % (turnover / 100000000)
        else:
            turnoverStr = "%.2f万" % (turnover / 10000)
        self.model.setItem(11, colNum, QStandardItem(turnoverStr))

        myBtn = QPushButton("点击")
        myBtn.setAccessibleDescription(code)
        myBtn.clicked.connect(self.showStockPages)

        self.model.setItem(12, colNum, QStandardItem())
        parent = self.model.item(12, colNum)

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
