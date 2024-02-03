import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QDockWidget, QListWidget
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.items = ['呵呵', 'aa', 'bb', 'cc', 'dd', 'ee', 'ff','g', 'h', 'i', 'j', 'k', 'l', 'm'
                 ,'m','n','o','p','q','r','s','t']
        self.items2 = ['你好','委托','下单']
        self.init()
        self.addDock()
        self.addDock2()


    def init(self):
        self.text = QTextEdit('主窗口')
        self.text.setAlignment(Qt.AlignCenter)
        # self.setCentralWidget(self.text)

        # self.setGeometry(200, 200, 800, 400)
        self.setWindowTitle('QDockWidget示例')
        self.show()
        pass

    def onDockListIndexChanged(self, index):
        item = self.items[index]
        self.text.setText(item)
        pass

    def addDock(self):
        dock1 = QDockWidget('DockWidget')
        dock1.setFeatures(QDockWidget.DockWidgetFloatable)
        dock1.setAllowedAreas(Qt.LeftDockWidgetArea)
        listwidget = QListWidget()

        listwidget.addItems(self.items)
        listwidget.currentRowChanged.connect(self.onDockListIndexChanged)
        dock1.setWidget(listwidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock1)

    def addDock2(self):
        dock2 = QDockWidget('行情')
        dock2.setFeatures(QDockWidget.DockWidgetFloatable)
        dock2.setAllowedAreas(Qt.RightDockWidgetArea)
        listwidget = QListWidget()

        listwidget.addItems(self.items2)
        listwidget.currentRowChanged.connect(self.onDockListIndexChanged)
        dock2.setWidget(listwidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock2)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())


# 入口
if __name__ == '__main__':
    main()
