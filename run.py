# Author: Nike Liu
import sys
# sys.path.append('..')
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow
from MainEngine import MainEngine
from event.eventEngine import EventManager

class Run(object):
    def __init__(self):
        # self.init_data()
        self.start()

    # def init_data(self):
    #     import tushare as ts
        # code = ['000001','600618']
        # df = ts.get_realtime_quotes(code)  # Single stock symbol
        # print(df)

        # df = ts.get_tick_data('002463', date='2019-09-11', src='tt')
        # print(df.tail(20))

    def start(self):

        # 在Application设置窗口样式，则对所有窗口有效
        # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        ee = EventManager()
        me = MainEngine(ee)
        win = MainWindow(me)
        # win.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyleSheet("#MainWindow{background-color: yellow}")
    win = Run()
    sys.exit(app.exec_())
