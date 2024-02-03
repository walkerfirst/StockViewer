# Author: Nike Liu
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    label = QLabel("<font color=red size=128><b>Hello PyQT，窗口会在5秒后消失！</b></font>")

    # 无边框窗口
    label.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)

    label.show()

    # 设置5s后自动退出
    QTimer.singleShot(5000, app.quit)

    sys.exit(app.exec_())
