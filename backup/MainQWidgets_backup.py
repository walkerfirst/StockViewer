from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QAbstractTableModel,QTimer,QUrl
from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem, QBrush, QColor, QFont, QDesktopServices
import sys
import pandas as pd
from BaseQWidgets import BaseDBTable,BaseDFTable,BaseStandardTable,BaseStandardTable2
import tushare as ts
from util.access_db import read_access_db
from setting.symbols import class_symbols
# from diyDelegate import TableDelegate

class BookTable(BaseDBTable):
    """演示文档"""
    dbpath = './db/book.db'
    dbtable = 'books'
    tableheader = ["国家","ISBN","书名","作者","出版单位","图书分类","定价"]
    def  __init__(self):
        super(BookTable, self).__init__()
        # 隐藏不需要的显示的列
        self.tableView.hideColumn(6)
        self.tableView.hideColumn(7)
        self.tableView.hideColumn(8)
        self.tableView.hideColumn(9)
        self.tableView.hideColumn(10)

class Myhold(BaseStandardTable):
    tableheader = ['代码', '名称', '仓位', '成本', '当前价', '市值(W)', '当日亏损(K)', '涨跌幅(%)', '盈亏(K)', '盈亏(%)']
    def __init__(self,sql):
        super(Myhold, self).__init__()
        # 获取持仓数据
        columns = ['code', 'qty', 'cost']
        # 得到持仓dataframe
        self.data = read_access_db(sql, columns)
        # data = pd.DataFrame(hold_list,columns=['code','qty','cost'])

        # 设置表头

        self.initData()
        self.createQtimer()
    def initData(self):
        # 需要展示的数据
        self.df = self.gettickdata(self.data)

    def run_update(self):
        """将需要显示的数据更新到model中"""
        # 这里要再次获取df，不然不会实时更新
        self.df = self.gettickdata(self.data)

        # 把数据更新到model中去
        self.update_data_to_model(self.df)

        # 设置第几列的字体颜色
        self.setForeground(name='change_rate', column=6)
        self.setForeground(name='change_rate',column=7)
        self.setForeground(name='profit_rate',column=8)
        self.setForeground(name='profit_rate',column=9)

    def createQtimer(self):
        """利用计时器，定时刷新行情"""

        self.refreshNum = 0
        # 获取数据
        self.run_update()
        # 建立一个计时器
        self.timer = QTimer()
        # 间隔一段时间，再次获取数据
        print('s')
        self.timer.timeout.connect(self.run_update)
        # 设置间隔时间大小ms
        self.timer.start(5000)

class Myhold2(BaseStandardTable2):
    # 设置表头
    tableheader = ['代码', '名称', '仓位', '成本', '当前价', '市值(W)', '当日亏损(K)', '涨跌幅(%)', '盈亏(K)', '盈亏(%)']
    def __init__(self,sql):
        super(Myhold2, self).__init__()
        # 获取持仓数据
        columns = ['code', 'qty', 'cost']
        # 得到持仓dataframe
        self.data = read_access_db(sql, columns)
        # data = pd.DataFrame(hold_list,columns=['code','qty','cost'])

        self.initData()
        self.createQtimer()
    def initData(self):
        # 需要展示的数据
        self.ts_df = self.gettickdata(self.data)
        self.df = pd.merge(self.data, self.ts_df, on='code')
        self.df['profit_rate'] = round((self.df['price'] / self.df['cost'] - 1) * 100, 1)  # 利润率
        self.df['value'] = round(self.df['price'] * self.df['qty'] / 10000, 2)  # 市值
        self.total_value = round(self.df['value'].sum(), 1)
        self.df['position'] = round(self.df['value'] / self.total_value * 100, 1)
        self.df['profit'] = round((self.df['price'] - self.df['cost']) * self.df['qty'] / 1000, 1)
        self.df['profit2'] = round((self.df['price'] - self.df['pre_close']) * self.df['qty'] / 1000, 1)
        self.df = self.df[['code', 'name', 'position', 'cost', 'price', 'value', 'profit2', 'change_rate', 'profit',
                           'profit_rate']].sort_values(by='change_rate', ascending=False)
        return self.df

    def run_update(self):
        """将需要显示的数据更新到model中"""
        # 这里要再次获取df，不然不会实时更新
        self.df = self.initData()
        # self.initData()
        # 把数据更新到model中去
        self.update_data_to_model(self.df)
        # 设置汇总行的行标
        x = max(self.df.index) + 1
        self.total_profit = round(self.df['profit'].sum(),1)  # 账户利润总计
        self.total_day = round(self.df['profit2'].sum(),1)   # 当日利润总计
        self.total_day_rate = round(self.total_day/self.total_value*10, 1)    # 当日利润率
        self.total_rate = round(self.total_profit/(self.total_value*10-self.total_profit)*100, 1)  # 账户利润率

        # 设置汇总行要显示的内容
        self.model.setItem(x, 1, QStandardItem('汇总'))  # 这一行为了点击该行时，不会发生错误
        self.model.setItem(x, 5, QStandardItem(str(self.total_value)))
        self.model.setItem(x, 6, QStandardItem(str(self.total_day)))
        self.model.setItem(x, 7, QStandardItem(str(self.total_day_rate)))
        self.model.setItem(x, 8, QStandardItem(str(self.total_profit)))
        self.model.setItem(x, 9, QStandardItem(str(self.total_rate)))

        # 设置第几列的字体颜色
        self.setForeground(byname='change_rate', column=6)
        self.setForeground(byname='change_rate',column=7)
        self.setForeground(byname='profit_rate',column=8)
        self.setForeground(byname='profit_rate',column=9)

        # 设置最后一行的字体颜色
        self.setForeground_LastLine(self.total_day,x,6)
        self.setForeground_LastLine(self.total_profit,x,8)

    def createQtimer(self):
        """利用计时器，定时刷新行情"""

        self.refreshNum = 0
        # 获取数据
        self.run_update()
        # 建立一个计时器
        self.timer = QTimer()
        # 间隔一段时间，再次获取数据
        print('s')
        self.timer.timeout.connect(self.run_update)
        # 设置间隔时间大小ms
        self.timer.start(8000)

class HoldingTable(QWidget):
    """主窗口用到的显示控件"""
    def __init__(self):
        super(HoldingTable, self).__init__()
        self.initUI()

    def initUI(self):

        # 水平布局，初始表格5*3，添加到布局
        layout = QHBoxLayout()
        self.tableWidget = QTableWidget(5, 3)
        layout.addWidget(self.tableWidget)

        # 设置表格水平方向的头标签
        self.tableWidget.setHorizontalHeaderLabels(['姓名', '性别', '体重'])

        # 设置水平方向自动伸缩填满窗口
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 添加数据到指定行列
        newItem = QTableWidgetItem("张三")
        self.tableWidget.setItem(0, 0, newItem)

        newItem = QTableWidgetItem("男")
        self.tableWidget.setItem(0, 1, newItem)

        newItem = QTableWidgetItem("160")
        self.tableWidget.setItem(0, 2, newItem)

        newItem = QTableWidgetItem("李四")
        self.tableWidget.setItem(1, 0, newItem)

        newItem = QTableWidgetItem("女")
        self.tableWidget.setItem(1, 1, newItem)

        newItem = QTableWidgetItem("120")
        self.tableWidget.setItem(1, 2, newItem)

        # 允许右键产生菜单
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # 将右键菜单绑定到槽函数generateMenu
        self.tableWidget.customContextMenuRequested.connect(self.generateMenu)

        self.setLayout(layout)

    def generateMenu(self, pos):
        """右键菜单"""

        # 计算有多少条数据，默认-1,
        row_num = -1
        for i in self.tableWidget.selectionModel().selection().indexes():
            row_num = i.row()

        # 表格中只有两条有效数据，所以只在前两行支持右键弹出菜单
        if row_num < 2:
            menu = QMenu()
            item1 = menu.addAction(u'选项一')
            item2 = menu.addAction(u'选项二')
            item3 = menu.addAction(u'选项三')
            action = menu.exec_(self.tableWidget.mapToGlobal(pos))
            # 显示选中行的数据文本
            if action == item1:
                print('你选了选项一，当前行文字内容是：', self.tableWidget.item(row_num, 0).text(),
                      self.tableWidget.item(row_num, 1).text(),
                      self.tableWidget.item(row_num, 2).text())
            if action == item2:
                print('你选了选项二，当前行文字内容是：', self.tableWidget.item(row_num, 0).text(),
                      self.tableWidget.item(row_num, 1).text(),
                      self.tableWidget.item(row_num, 2).text())
            if action == item3:
                print('你选了选项三，当前行文字内容是：', self.tableWidget.item(row_num, 0).text(),
                      self.tableWidget.item(row_num, 1).text(),
                      self.tableWidget.item(row_num, 2).text())

class IndexTable(BaseDFTable):
    """将给定的代码直接转换成表格控件，并定时刷新"""
    def __init__(self):
        super(IndexTable, self).__init__()
        self.initData()
        self.createQtimer()

    def initData(self):
        # 需要展示的数据
        self.df = ts.get_realtime_quotes(class_symbols)
        self.df = self.df[['code', 'name', 'name', 'date', 'time', 'pre_close', 'price']]
        self.df[['pre_close', 'price']] = self.df[['pre_close', 'price']].astype(float)
        self.df['change_rate'] = round((self.df['price'] / self.df['pre_close'] - 1) * 100, 2)
        self.df = self.df.sort_values(by='change_rate',ascending=False)
        return self.df
    def update_model(self):
        data = self.initData()
        self.model = DataFrameTableModel(data)
        self.dataView.setModel(self.model)

    def createQtimer(self):
        """利用计时器，定时刷新行情"""

        self.refreshNum = 0
        # 获取数据
        self.update_model()
        # 建立一个计时器
        self.timer = QTimer()
        # 间隔一段时间，再次获取数据
        print('s')
        self.timer.timeout.connect(self.update_model)
        # 设置间隔时间大小ms
        self.timer.start(10000)

class DataFrameTableModel(QAbstractTableModel):

    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def data(self, index, role= Qt.DisplayRole):
        """ return dataframe single data with a location"""
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row()][index.column()])
        return None

    def headerData(self, rowcol, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[rowcol]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[rowcol]
        return None

    def flags(self, index):
        """复选框使用？通过Delegate创建QCheckBox来实现的Check列"""
        flags = super(self.__class__, self).flags(index)
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsDragEnabled
        flags |= Qt.ItemIsDropEnabled
        return flags

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        try:
            self.layoutAboutToBeChanged.emit()
            self._data = self._data.sort_values(self._data.columns[Ncol], ascending=not order)
            self.layoutChanged.emit()
        except Exception as e:
            print(e)

class DetailTable(BaseDFTable):

    df = pd.read_excel(r'./data/组合.xlsx', encoding='gbk')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = BookTable()
    example.show()
    sys.exit(app.exec_())