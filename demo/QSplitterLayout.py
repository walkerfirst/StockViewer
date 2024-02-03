# Author: Nike Liu

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,QFrame, QSplitter,QFormLayout)
from PyQt5.QtCore import Qt

class QSplitterLayout(QWidget):

  def __init__(self,parent=None):
    super(QSplitterLayout,self).__init__(parent)
    self.splitter = QSplitter(Qt.Vertical)

    self.hbox = QHBoxLayout()

    self.top_left = QFrame()
    self.top_left.setFrameShape(QFrame.StyledPanel)

    self.top_right = QFrame()
    self.top_right.setFrameShape(QFrame.StyledPanel)

    self.bottom_left = QFrame()
    self.bottom_left.setFrameShape(QFrame.StyledPanel)

    self.bottom_right = QFrame()
    self.bottom_right.setFrameShape(QFrame.StyledPanel)

    self.splitter1 = QSplitter(Qt.Horizontal)
    self.splitter1.addWidget(self.top_left)
    self.splitter1.addWidget(self.top_right)

    self.splitter2 = QSplitter(Qt.Horizontal)
    self.splitter2.addWidget(self.bottom_left)
    self.splitter2.addWidget(self.bottom_right)

    self.splitter.addWidget(self.splitter1)
    self.splitter.addWidget(self.splitter2)

    # 设置分割器比例 7:3
    # splitter.setStretchFactor(2, 1)
    # splitter.setStretchFactor(1, 3)

    # 设置分割器比例 7:3
    self.splitter1.setStretchFactor(0, 7)
    self.splitter1.setStretchFactor(1, 3)

    # 设置分割器比例 7:3
    self.splitter2.setStretchFactor(0, 7)
    self.splitter2.setStretchFactor(1, 3)
    self.hbox.addWidget(self.splitter)
    self.setLayout(self.hbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QSplitterLayout()
    ex.show()
    sys.exit(app.exec_())