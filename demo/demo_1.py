from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableView,QAbstractItemView,QHBoxLayout,QWidget
import pandas as pd

class Table(QWidget):
    def __init__(self,dataframe):
        super(Table).__init__()
        self.dataframe = dataframe
        self.initUI()

    def initUI(self):
        #设置标题与初始大小

        Layout = QHBoxLayout()
        print('-1')
        data_table = QTableView()
        print('0')

        tm = TableModel(self.dataframe)
        print('1')
        table.setModel(tm)
        print('2')
        Layout.addWidget(data_table)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.setSortingEnabled(True)

        self.setLayout(Layout)



class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row()][index.column()])
        return None

    def headerData(self, rowcol, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[rowcol]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[rowcol]
        return None

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= QtCore.Qt.ItemIsEditable
        flags |= QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEnabled
        flags |= QtCore.Qt.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemIsDropEnabled
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
if __name__ == "__main__":
    df = pd.read_excel(r'./data/fund_data.xlsx', encoding='gbk')
    # print(df)
    table = Table(df)
    print(table)