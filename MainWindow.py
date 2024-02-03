from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow,QAction,QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt,QTimer,pyqtSignal
from MainQWidgets import Myhold2,StatusForm,IndexTable2,SearchDB
from setting.symbols import class_symbols,index_symbols
from event.eventEngine import Event
from event.eventType import *
# from MainQWidgets import ChemicalGendan

from setting.account import Account
from res import resource
import qdarkstyle, time
from login import LoginForm

class MainWindow(QMainWindow):
    """主窗口布局设置"""
    loginSignal = pyqtSignal(str)  # 登录信号

    def __init__(self,mainEngine):
        super(MainWindow, self).__init__()
        # 初始化引擎、数据和UI
        self.mainEngine = mainEngine
        self.initUi()
        # loading登录窗口
        self.login = LoginForm(self.mainEngine)
        # 登录信号绑定动作
        self.loginSignal.connect(self.createQtimer)

        self.initData()

        # 注册'更新持仓信息'的函数
        self.mainEngine.registerHandler(type_=EVENT_ACCOUNT, handler=self.upatePositionData)
        # 注册"登录"的函数
        self.mainEngine.registerHandler(type_=EVENT_LOGIN,handler=self.loginEvent)

        # 设置push tick data 的timer和保持收盘数据的状态
        self.timerStatus = False
        self.saveDataStatus = False

        # 间歇check
        self.checkTimer()

    def initData(self):
        """初始化持仓股和订阅list"""
        # 持仓的code list
        self.positionSymbols = self.mainEngine.mySymbols
        # 订阅的tick list
        self.subcribeSymbols = list(set(self.positionSymbols + index_symbols + class_symbols))

    def upatePositionData(self,event):
        """trade后更新持仓股和订阅list"""
        # 持仓的code list
        self.positionSymbols = event.dict['position']
        # 订阅的tick list
        self.subcribeSymbols = list(set(self.positionSymbols + index_symbols + class_symbols))

    def pushData(self):
        """发送tick event"""
        try:
            tickData = self.mainEngine.getTick(self.subcribeSymbols)
        except Exception as e:
            print('Mainwindow getTick 出现异常: %s' %(str(e)))
            time.sleep(2)
            tickData = self.mainEngine.getTick(self.subcribeSymbols)

        if not tickData.empty:
            event_tick = Event(type_=EVENT_TIMER)
            event_tick.dict['tick'] = tickData
            self.mainEngine.sendEvent(event_tick)
        else:
            return

    def createQtimer(self,con):
        """利用计时器，定时刷新行情"""
        print(con)
        self.refreshNum = 0
        right_now = time.strftime("%H:%M %S")
        print('%s 开始更新' % right_now)
        self.pushData()
        self.timerStatus = True
        # 建立一个计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.pushData)

        # 设置间隔时间大小ms
        self.timer.start(5000)

    def intervalCheck(self):
        right_now = int(time.strftime("%H%M%S"))
        from util.stock_util import check_today_is_holiday

        if right_now < 91500:
        # if int(time.strftime("%H%M%S")) > 113200 and int(time.strftime("%H%M%S")) < 125900:
            self.timer_stop()

        if right_now < 150200 and right_now > 91500:
            # if int(time.strftime("%H%M%S")) > 113200 and int(time.strftime("%H%M%S")) < 125900:
            # 检查当日是否为假日
            if check_today_is_holiday() and self.timerStatus:
                    self.timer_stop()
                    QMessageBox.about(self, "提示", "休息日，数据停止更新！")

        if right_now > 150100:
            self.timer_stop()
            if not check_today_is_holiday() and not self.saveDataStatus:
                self.saveData()
                self.saveDataStatus = True

    def checkTimer(self):
        """另外一个timer检查当前时间是否为交易时间"""
        self.Newtimer = QTimer()
        self.Newtimer.timeout.connect(self.intervalCheck)
        # 每分钟运行一次
        self.Newtimer.start(10000)

    def initUi(self):
        """初始化界面"""
        # path = os.getcwd().rsplit('\\')[-1]
        self.setWindowTitle('股票交易记录管理')
        # self.setWindowOpacity(0.9) # 设置窗口透明度
        self.resize(1500,900)
        # 设置程序的图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/files-and-folders.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        self.font = QtGui.QFont()
        self.font.setFamily("Arial")  # 括号里可以设置成自己想要的其它字体
        self.font.setPointSize(12)  # 括号里的数字可以设置成自己想要的字体大小
        self.setFont(self.font)
        # 在这里设置窗口的样式，只对本窗口有效。在Application设置则对所有窗口有效
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # load 菜单栏
        # self.initMenu()

        # load 工具栏
        self.initBar()

        # load 状态栏
        self.initStatusBar()

        # 最大化窗口
        self.showMaximized()
        self.MainLayout()

    def initMenu(self):
        """初始化菜单"""
        # 设置菜单项
        bar = self.menuBar()
        self.Menu = bar.addMenu("文件")
        self.signUpAction = QAction("注册", self)
        self.close = QAction("退出", self)

        self.Menu.addAction(self.signUpAction)
        self.Menu.addAction(self.close)
        self.close.triggered.connect(self.closeEvent)

        self.query = bar.addMenu("操作")
        self.update_price = QAction("更新数据库最新价格", self)
        self.stockprocess = QAction("填权处理", self)
        self.query.addAction(self.update_price)
        self.query.addAction(self.stockprocess)

        self.update_price.triggered.connect(self.run_update)
        self.stockprocess.triggered.connect(self.stockprocessprice)

        self.connet = bar.addMenu("链接数据")
        self.start_timer = QAction('开始更新',self)
        self.stop_timer = QAction('停止更新',self)
        self.connet.addAction(self.start_timer)
        self.connet.addAction(self.stop_timer)
        self.start_timer.triggered.connect(self.createQtimer)
        self.start_timer.triggered.connect(self.timer_stop)

    def initBar(self):

        """初始化工具栏"""
        tb1 = self.addToolBar("File")
        start = QAction(QIcon(':/start.png'), "开始", self)
        tb1.addAction(start)
        start.triggered.connect(lambda: self.createQtimer("开始更新行情..."))

        stop = QAction(QIcon(':/pause.png'), "暂停", self)
        tb1.addAction(stop)
        stop.triggered.connect(self.timer_stop)

        update = QAction(QIcon(':/update.png'), "更新报价", self)
        tb1.addAction(update)
        update.triggered.connect(self.run_update)

        import_data = QAction(QIcon(':/1-19122Q926010-L.png'), "导入数据", self)
        tb1.addAction(import_data)
        import_data.triggered.connect(self.import_data)

        save_data = QAction(QIcon(':/cloud-download2.png'), "保存收盘数据", self)
        tb1.addAction(save_data)
        save_data.triggered.connect(self.saveData)

        search_report = QAction(QIcon(':/1-1912302044060-L.png'), "搜索研报", self)
        tb1.addAction(search_report)
        search_report.triggered.connect(self.showSearch)

        search_history = QAction(QIcon(':/1-1912302044060-L.png'), "搜索历史交易", self)
        tb1.addAction(search_history)
        search_history.triggered.connect(self.showSearch_history)

        recent_sell_history = QAction(QIcon(':/Background.png'), "最近卖出记录", self)
        tb1.addAction(recent_sell_history)
        recent_sell_history.triggered.connect(self.showRecentHistory)

        accountDetails = QAction(QIcon(':/Background.png'), "查看账户信息", self)
        tb1.addAction(accountDetails)
        accountDetails.triggered.connect(self.showAccount)

        # gendan = QAction(QIcon(':/wuxing.png'), "跟单进程", self)
        # tb1.addAction(gendan)
        # gendan.triggered.connect(self.showGendan)

        quit = QAction(QIcon(':/poweroff2.png'), "退出", self)
        tb1.addAction(quit)
        quit.triggered.connect(self.close)

        tb1.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # 给工具添加显示的layout
        # default.triggered.connect(self.DefaultLayout)
        # history.triggered.connect(self.TabWigde)

    def initTable(self):
        self.table_HX_L = Myhold2(self.mainEngine, account='HX_L')
        self.table_GL_J = Myhold2(self.mainEngine,account='GL_J')
        self.table_HT_L = Myhold2(self.mainEngine, account='HT_L')
        self.table_ZH_F = Myhold2(self.mainEngine, account='ZH_F')

        self.table_index = IndexTable2(self.mainEngine,self.event,symbols=index_symbols)
        self.table_class = IndexTable2(self.mainEngine,self.event,symbols=class_symbols)

    def MainLayout(self):
        """主窗口的显示设置"""
        self.initTable()
        holding_dock = self.create_dock(self.table_HX_L, "华鑫", QtCore.Qt.LeftDockWidgetArea)
        mypool_dock = self.create_dock(self.table_GL_J, "国联", QtCore.Qt.LeftDockWidgetArea)
        history_dock = self.create_dock(self.table_HT_L, "华泰", QtCore.Qt.RightDockWidgetArea)

        detail_dock = self.create_dock(self.table_class, "板块ETF", QtCore.Qt.RightDockWidgetArea)
        index_dock = self.create_dock(self.table_index, "重要指数", QtCore.Qt.RightDockWidgetArea)
        order_dock = self.create_dock(self.table_ZH_F, "中航", QtCore.Qt.LeftDockWidgetArea)

        # 设置dock的最大高度和宽度
        holding_dock.setMaximumHeight(850)
        # mypool_dock.setMaximumHeight(850)

        order_dock.setMaximumHeight(400)
        index_dock.setMaximumHeight(450)

        detail_dock.setMaximumWidth(1600)
        # 设置成选项卡格式
        self.tabifyDockWidget(index_dock,history_dock)
        # self.tabifyDockWidget(holding_dock,history_dock)
        # 发出通知？
        detail_dock.raise_()

    def create_dock(self, widget, name: str, area: int):
        """
        Initialize a dock widget.
        """
        dock = QtWidgets.QDockWidget(name)
        dock.setWidget(widget)
        dock.setObjectName(name)
        dock.setFeatures(dock.DockWidgetFloatable |dock.DockWidgetMovable)
        self.addDockWidget(area, dock)
        return dock

    def reset_dock(self):
        self.initTable()
        self.mypool_dock.setWidget(self.table_GL_J)

    def showSearch(self):
        """搜索研报记录"""
        self.showSearch = SearchDB('研报')
        self.showSearch.show()

    def showSearch_history(self):
        """搜索历史交易"""
        self.search_history = SearchDB('历史单')
        self.search_history.show()

    def closeEvent(self, event):
        """关闭窗口的确认动作"""
        box = QMessageBox(QMessageBox.Warning, "警告框", "确定关闭窗口？")
        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
        qno = box.addButton(self.tr("取消"), QMessageBox.NoRole)
        box.exec_()
        if box.clickedButton() == qyes:
            self.timer_stop()
            # 关闭窗口前需要处理的动作
            self.mainEngine.exit()
            app = QApplication.instance()
            # close window
            event.accept()
            # 退出程序
            app.quit()
        else:
            event.ignore()
            # self.saveData()

    def run_update(self):
        """更新价格信息对话框"""
        from import_data.update_price_to_hold import updatePrice
        self.run_update = updatePrice()
        QMessageBox.about(self, "对话框", "更新已完成！")

    def showdialog(self):
        """状态栏对话框"""
        self.dialog = StatusForm(self.mainEngine,self.event)
        self.dialog.show()

    def timer_stop(self):
        right_now = time.strftime("%H:%M %S")
        if self.timerStatus:
            self.timer.stop()
            print('%s 停止更新'%right_now)
            # QMessageBox.about(self, "对话框", "已停止！")
            self.timerStatus = False
            self.timerEnable = False
        # print(self.timerStatus)

    def import_data(self):
        """把exel交易数据导入到db中"""
        from trading.update_records_from_xls_to_access import update_records_to_access
        box = QMessageBox(QMessageBox.Warning, "警告框", "导入文件是否已更新？")
        qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
        qno = box.addButton(self.tr("取消"), QMessageBox.NoRole)
        box.exec_()
        if box.clickedButton() == qyes:
            self.import_data = update_records_to_access()
        else:
            return

    def saveData(self):
        """把当日收盘数据保存到db中"""
        count = 0
        for account in Account.keys():
            today = self.mainEngine.todayDate
            # 先获取db数据
            qry_sql = "select * from 每日净值 where 日期 = '" + today + "' and 账户 = '" + account + "'"
            qry_re = self.mainEngine.qryDB(qry_sql)
            # 判断是否已经存在当日数据
            if qry_re.empty:
                # 获取该账户下的持仓code
                symbolList = self.mainEngine.qryMysymbols(account=account)
                tickData = self.mainEngine.getTick(symbolList)
                posiontData = self.mainEngine.qryPosition(accountName=account)
                dataframe = self.mainEngine.processData(posiontData, tickData)
                dbData = self.mainEngine.getAccDict()[account]
                cash = dbData['cash']
                stock_value = round(dataframe['value'].sum(), 2)
                total_value = stock_value + round(cash / 10000, 2)
                save_sql = "INSERT INTO 每日净值(日期,账户,市值,总资产) VALUES ('" + today + "','" + account + "'," \
                                                                                                       " '" + str(
                    stock_value) + "', '" + str(total_value) + "')"
                count += 1
                self.mainEngine.excuteSQL(save_sql)
        # 判断是否是第一次保存数据
        if len(Account.keys()) == count:
            QMessageBox.about(self, "对话框", "收盘数据已保存！")

    def initStatusBar(self):
        """ 状态栏"""
        self.status = self.statusBar()
        # self.status.showMessage('实时更新的信息', 0)
        #  状态栏本身显示的信息 第二个参数是信息停留的时间，单位是毫秒，默认是0（0表示在下一个操作来临前一直显示）
        # self.lable = QLabel()

        self.comNum1 = StatusForm(self.mainEngine,self.event)
        self.status.addWidget(self.comNum1, stretch=1)

    # def showGendan(self):
    #     self.show_gendan = ChemicalGendan()
        # self.show_gendan.show()
        # self.show_gendan.showMaximized()

    def showRecentHistory(self):
        from MainQWidgets import SellHistory
        self.show_Recent = SellHistory()

    def showAccount(self):
        from MainQWidgets import AccountDetails
        self.show_Account = AccountDetails()

    def loginEvent(self,event):
        """登录事件"""
        # self.pushData()
        # 这里不能直接创建timer，因为不允许在子线程中创建。需要利用pyqt的signal发射机制处理。
        self.loginSignal.emit("用户登录成功")

if __name__ == "__main__":
    import sys
    import qdarkstyle
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # app.setStyleSheet("#MainWindow{background-color: yellow}")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())