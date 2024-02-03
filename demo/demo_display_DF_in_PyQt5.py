#!/usr/bin/env python

import sys
import pandas as pd
from demo.demo_1 import TableModel
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor,QFont
import qdarkstyle

class StockViewer(QWidget):

    def __init__(self):
        super(StockViewer, self).__init__()

        self.Ui()

    def Ui(self):
        # 设置窗口的名称和大小
        self.setWindowTitle("Stock Viewer")
        self.resize(650, 650)

        data1 = {
            "id": [1, 2, 3],
            "name": [4, 5, 6],
            "age": [7, 8, 9]}
        # self.df = pd.DataFrame(data1,index=[4,2,3])
        self.df = pd.read_excel(r'./data/fund_data.xlsx', encoding='gbk')


        # print(self.df)

        # 建立表格控件，用于显示表格数据
        self.dataView = QTableView()
        self.dataView.setObjectName("dataView")

        # 建立model,通过自定义类PandasModel把DF转换成 table model
        self.model = TableModel(self.df)

        # self.model.setHeaderData(1,Qt.Horizontal,'nii')

        # self.model.select()

        # 让TableView显示 model表格
        self.dataView.setModel(self.model)
        # 选择内容的行为：行高亮
        self.dataView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 允许右键产生菜单，如果不设为CustomContextMenu,无法使用customContextMenuRequested
        self.dataView.setContextMenuPolicy(Qt.CustomContextMenu)

        # 将右键菜单绑定到槽函数showContextMenu
        self.dataView.customContextMenuRequested.connect(self.showContextMenu)

        # 将右键菜单绑定到槽函数generateMenu
        # self.dataView.customContextMenuRequested.connect(self.generateMenu)
        # 设置表格列与行尺寸适用内容
        self.dataView.resizeColumnsToContents()
        self.dataView.resizeRowsToContents()
        # 开启按列排序功能
        self.dataView.setSortingEnabled(True)
        # 设置行名隐藏
        self.dataView.verticalHeader().setVisible(False)
        # 设置列名隐藏
        # self.dataView.horizontalHeader().setVisible(False)

        # 隐藏不需要的列，必须放在在setModel之后才能生效，从第0列开始
        self.dataView.hideColumn(1)
        self.dataView.setFont(QFont("Arial", 12))

        # 新建一个layout
        layout = QHBoxLayout()
        # 将表格控件添加到layout中去
        layout.addWidget(self.dataView)
        # 设置layout
        self.setLayout(layout)

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

        print('动作a',row_num)

        print('你选了选项一，当前行文字内容是：', self.dataView.item(row_num, 1).text())


    def generateMenu(self, pos):
        """右键菜单"""

        # 计算有多少条数据，默认-1,
        row_num = -1
        for i in self.dataView.selectionModel().selection().indexes():
            row_num = i.row()

        print(row_num)

        # 表格中只有两条有效数据，所以只在前两行支持右键弹出菜单

        menu = QMenu()
        item1 = menu.addAction(u'选项一')
        item2 = menu.addAction(u'选项二')
        item3 = menu.addAction(u'选项三')
        action = menu.exec_(self.dataView.mapToGlobal(pos))
        # 显示选中行的数据文本
        if action == item1:
            print('你选了选项一，当前行文字内容是：', self.dataView.item(row_num, 0).text())
        if action == item2:
            print('你选了选项二，当前行文字内容是：', self.dataView.item(row_num, 0).text(),
                  self.dataView.item(row_num, 1).text(),
                  self.dataView.item(row_num, 2).text())
        if action == item3:
            print('你选了选项三，当前行文字内容是：', self.dataView.item(row_num, 0).text(),
                  self.dataView.item(row_num, 1).text(),
                  self.dataView.item(row_num, 2).text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    dialog = StockViewer()
    dialog.show()
    sys.exit(app.exec_())
