# Author: Nike Liu


def DefaultLayout(self):
    """  默认显示窗口"""
    self.splitter = QSplitter(Qt.Vertical)

    # self.top_left = QGroupBox(self.hbox)

    # 设置QFrame显示样式
    # self.top_left.setFrameShape(QFrame.StyledPanel)
    # tab = TabDemo(self.top_left)

    # 将 tab 页面加入到top_left

    self.top_right = QFrame()
    self.top_right.setFrameShape(QFrame.StyledPanel)

    self.bottom_left = QFrame()
    self.bottom_left.setFrameShape(QFrame.StyledPanel)

    self.bottom_right = QFrame()
    self.hbox = QHBoxLayout(self.bottom_right)
    self.bottom_right.setFrameShape(QFrame.StyledPanel)

    self.splitter1 = QSplitter(Qt.Horizontal)
    self.splitter1.addWidget(self.tab)
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
    # self.hbox.addWidget(self.splitter)

    # 建立主layout为水平布局
    self.Mainlayout = QHBoxLayout()

    # 将tab组件添加到主layout中
    self.Mainlayout.addWidget(self.splitter)

    # 添加状态栏
    self.statusBar().showMessage('默认窗口')

    # 设置窗口中心显示区域
    self.default_frame = QWidget()
    self.setCentralWidget(self.default_frame)
    # 显示窗口
    self.default_frame.setLayout(self.Mainlayout)


def TabWigde(self):
    # 添加状态栏
    self.statusBar().showMessage('历史记录窗口')
    # 新建一个水平布局
    TabLayout = QVBoxLayout()
    # 新建一个选项卡控件，用来装载选项卡页面
    # self.QTabWidget = QTabWidget()

    TabLayout.addWidget(self.tab)

    # 设置窗口中心显示区域
    self.history_frame = QWidget()
    self.setCentralWidget(self.history_frame)
    # 显示窗口
    self.history_frame.setLayout(TabLayout)
