from PyQt5.QtWidgets import *
import sys


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主窗口")
        button = QPushButton("弹出子窗", self)
        button.clicked.connect(self.show_child)

        # 设置菜单项
        bar = self.menuBar()
        self.Menu = bar.addMenu("文件")
        self.signUpAction = QAction("注册", self)
        self.close = QAction("退出", self)

        self.Menu.addAction(self.signUpAction)


        self.query = bar.addMenu("查询")
        self.history_by_month = QAction("按月查询", self)
        self.query.addAction(self.history_by_month)

        self.history_by_month.triggered.connect(self.show_child)

    def show_child(self):
        self.child_window = Child()
        self.child_window.show()


class Child(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("我是子窗口啊")


# 运行主窗口
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Main()
    window.show()

    sys.exit(app.exec_())
