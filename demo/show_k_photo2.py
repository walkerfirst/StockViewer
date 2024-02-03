import sys
import importlib

importlib.reload(sys)
# sys.setdefaultencoding('utf-8')
from PyQt5 import QtCore, QtGui
import datetime
import pyqtgraph as pg
import tushare as ts

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):
    def setData(self, original_data):
        self.original_data = original_data

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 31))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)

        self.drawChart = DrawChart(ktype='D', original_data=self.original_data)
        self.verticalLayout_2.addWidget(self.drawChart.pyqtgraphDrawChart())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))


class DrawChart():
    def __init__(self, code='sz50', start=str(datetime.date.today() - datetime.timedelta(days=200)),
                 end=str(datetime.date.today() + datetime.timedelta(days=1)), ktype='D', original_data=[]):
        self.code = code
        self.start = start
        self.end = end
        self.ktype = ktype
        self.original_data = original_data
        self.data_list, self.t = self.getData()

    def pyqtgraphDrawChart(self):
        # try:
        self.item = CandlestickItem(self.data_list)
        print("weiyuanzu", self.data_list)
        self.xdict = {0: str(self.hist_data.index[0]).replace('-', '/'),
                      int((self.t + 1) / 2) - 1: str(self.hist_data.index[int((self.t + 1) / 2)]).replace('-', '/'),
                      self.t - 1: str(self.hist_data.index[-1]).replace('-', '/')}
        self.stringaxis = pg.AxisItem(orientation='bottom')
        self.stringaxis.setTicks([self.xdict.items()])
        self.plt = pg.PlotWidget(axisItems={'bottom': self.stringaxis}, enableMenu=False)

        self.plt.addItem(self.item)
        self.plt.showGrid(x=True, y=True)
        return self.plt

    # except:
    #     print("pyqtgraphDrawChart 异常")
    #     return pg.PlotWidget()

    def getData(self):
        self.start = str(datetime.date.today() - datetime.timedelta(days=150))
        self.end = str(datetime.date.today() + datetime.timedelta(days=1))
        self.hist_data = ts.get_hist_data(self.code, self.start, self.end, self.ktype).sort_index()[-300:-1]
        self.hist_data = self.original_data
        data_list = []
        t = 0
        for dates, row in self.hist_data.iterrows():
            open, low, high, close = row[:4]
            datas = (t, open, close, low, high)
            data_list.append(datas)
            t += 1
        return data_list, t


class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, open, close, min, max) in self.data:
            print(open, close, type(open))
            if open > close:
                p.setPen(pg.mkPen('g'))
                p.setBrush(pg.mkBrush('g'))
            else:
                p.setPen(pg.mkPen('r'))
                p.setBrush(pg.mkBrush('r'))
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


def myData():
    import pandas as pd
    data = pd.read_csv("K线导出_RB2005_5分钟数据.csv", encoding="gbk")
    data.index = data["交易时间"]
    data.drop(["结算价", "证券代码", "证券名称", "交易时间", "涨跌幅%", "涨跌", "成交量", "成交额"], axis=1, inplace=True)
    data.rename(columns={"开盘价": "open", "收盘价": "close", "最高价": "high", "最低价": "low"}, inplace=True)
    data.sort_index(ascending=False, inplace=True, axis=1)
    len = data.shape[0]
    data = data.iloc[len - 200:]
    return data


def mouseMoved(evt):
    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    if plot.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        index = int(mousePoint.x())
        pos_y = int(mousePoint.y())
        print(index)
        if 0 < index < len(data.index):
            print(xdict[index], data['open'][index], data['close'][index])
            label.setHtml(
                "<p style='color:white'>日期：{0}</p><p style='color:white'>开盘：{1}</p><p style='color:white'>收盘：{2}</p>".format(
                    xdict[index], data['open'][index], data['close'][index]))
            label.setPos(mousePoint.x(), mousePoint.y())
        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())


if __name__ == "__main__":
    import sys

    data = myData()
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setData(data)
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
