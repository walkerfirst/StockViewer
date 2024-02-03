# Author: Nike Liu
#­*­coding: utf­8 ­*­

from PyQt5 import QtCore, QtGui

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
                return QtCore.QVariant(unicode(
                    self._data.values[index.row()][index.column()]))
        return QtCore.QVariant()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            try:
                return '%s' % unicode(self._data.columns.tolist()[section], encoding="utf-8")
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                return '%s' % self._data.index.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():

            print("data set with keyboard : " + value.toByteArray().data().decode("latin1"))
            self._data.values[index.row()][index.column()] = "anything"
            print("data committed : " +self._data.values[index.row()][index.column()])

            self.dataChanged.emit(index, index)
            return True
        return QtCore.QVariant()