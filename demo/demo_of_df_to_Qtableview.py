# Author: Nike Liu
from PyQt5 import QtCore, QtGui

import os,sys
from parametrage import Ui_WinParam
from pandas_to_pyqt import PandasModel
import pandas as pd
import sqlite3

class window_parametreur(QtGui.QDialog, Ui_WinParam):
    def __init__(self, dataframemodel, parent=None):
        QtGui.QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        self.ui = Ui_WinParam()
        self.ui.setupUi(self)
        self.setModal(True)
        self.ui.tableView.setModel(dataframemodel)
        self.ui.tableView.resizeColumnsToContents()

def OpenParametreur(self, db_path):

    #connecting to database and getting datas as pandas.dataframe
    con = sqlite3.connect(db_path)
    strSQL = u'SELECT LIBELLE AS "Paramètre", VALEUR AS "Valeur" FROM parametres'.encode("utf-8")
    #strSQL = u'SELECT * FROM parametres'.encode("utf-8")
    data = pd.read_sql_query(strSQL, con)
    con.close()

    #converting to QtCore.QAbstractTableModel
    model = PandasModel(data)

    #loading dialog
    self.f=window_parametreur(model)
    self.f.exec_()

if __name__=="__main__":
    a=QtGui.QApplication(sys.argv)
    f=QtGui.QMainWindow()
    print(OpenParametreur(f, ".\SQLiteDataBase.db"))