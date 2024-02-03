import sys
from queue import Queue, Empty
from datetime import datetime
from threading import *
from PyQt5.QtCore import QTimer
from event.eventType import *


"""
事件管理类代码
事件驱动的简明讲解: https://www.jianshu.com/p/2290bfbd75dd
事件驱动的Python实现 : https://www.jianshu.com/p/a605fab0ab11
"""

class EventManager(object):

    def __init__(self):
        """ 初始化事件管理类"""
        # 事件对象列表
        self.__eventQueue = Queue()
        # 事件管理器开关
        self.__active = False
        # 事件处理线程
        self.__thread = Thread(target=self.__Run)
        self.count = 0

        # 这里的__handlers 是一个字典，用于保存对应的事件的相应函数
        # 每个键对应的值是一个列表， 列表中保存了对该事件的相应函数
        self.__handlers = {}

    def __Run(self):
        """ 引擎运行 """
        print("{}_run".format(self.count))

        while self.__active == True:
            try:
                # 获取事件的阻塞事件设置为1s
                event = self.__eventQueue.get(block=True, timeout=1)
                self.__EventProcess(event)
            except Empty:
                pass
            self.count += 1

    def __EventProcess(self, event):
        """ 处理事件 """
        print("{}_EventProcess".format(self.count))
        # 检查是否存在对该事件进行监听的处理函数
        if event.type_ in self.__handlers:
            # 如果存在， 则按照顺序将事件传递给处理函数进行执行
            for handler in self.__handlers[event.type_]:
                handler(event)
        self.count += 1

    def Start(self):
        """启动"""
        print("{}_Start".format(self.count))
        # 将事件管理器设置为启动
        self.__active = True
        # 启动事件处理线程
        self.__thread.start()
        self.count += 1

    def Stop(self):
        """停止"""
        print("{}_Stop".format(self.count))
        # 将事件管理器设置为停止
        self.__active = False
        # 等待事件处理线程退出
        self.__thread.join()
        self.count += 1

    def AddEventListener(self, type_, handler):
        """ 绑定事件和监听器处理函数"""
        print("{}_AddEventListener".format(self.count))
        # 尝试获取该事件类型队形的处理函数列表， 若无则创建
        try:
            handlerList = self.__handlers[type_]
        except KeyError:
            handlerList = []

        self.__handlers[type_] = handlerList
        # 若要注册的处理器不在该事件处理器的处理器列表中， 则注册该事件
        if handler not in handlerList:
            handlerList.append(handler)

        print(self.__handlers)
        self.count += 1

    def RemoveEventListener(self, type_, handler):
        """ 移除监听器的处理函数 """
        print('{}_RemoveEventListener'.format(self.count))
        try:
            handlerList = self.handlers[type_]
            # 如果函数存在于列表中，则移除
            if handler in handlerList:
                handlerList.remove(handler)
            # 如果函数列表为空，则从引擎中移除该事件类型
            if not handlerList:
                del self.__handlers[type_]
        except KeyError:
            pass
        self.count += 1

    def SendEvent(self, event):
        """ 发送事件，向事件队列中存入事件"""
        print('{}_SendEvent'.format(self.count))
        self.__eventQueue.put(event)
        self.count+=1

class Event:
    """ 事件类型 """
    def __init__(self,type_=None):
        self.type_ = type_  # 事件类型
        self.dict = {}      # 字典用于保存具体事件数据


# 事件源， 公众号

from data.HoldingTable import GetHoldingDF

class PublicAccounts:

    def __init__(self, eventManager):
        self.__eventManager = eventManager
        self.createQtimer()

    def WriteNewArtical(self):
        # 事件对象，写了信文章
        event = Event(type_=EVENT_TIMER)
        self._data = GetHoldingDF('HX_L')
        event.dict["artical_"] = self._data

        # 发送事件
        self.__eventManager.SendEvent(event)
        print(u'公众号发送新文章\n')

    def createQtimer(self):
        """利用计时器，定时刷新行情"""

        self.refreshNum = 0
        # 获取数据
        self.WriteNewArtical()
        # 建立一个计时器
        self.timer = QTimer()
        # 间隔一段时间，再次获取数据
        self.timer.timeout.connect(self.WriteNewArtical)
        # 设置间隔时间大小ms
        self.timer.start(2550)

# 监听器， 订阅者
class Listener:

    def __init__(self, username):
        self.__username = username

    # 监听器的处理函数， 读文章
    def ReadArtical(self, event):
        print(u'%s 收到新文章' % self.__username)
        print(u'正在阅读新文章内容: %s' % event.dict["artical_"])

def test():
    from qtpy import QtWidgets, QtCore
    # 实例化监听器
    app = QtWidgets.QApplication([])
    # 实例化监听器
    listner1 = Listener("thinkroom")  # 订阅者1
    listner2 = Listener("steve")      # 订阅者2

    # 实例化事件操作函数
    eventManager = EventManager()

    # 绑定事件和监听器相应函数(新文章)
    eventManager.AddEventListener(EVENT_TIMER, listner1.ReadArtical)
    eventManager.AddEventListener(EVENT_TIMER, listner2.ReadArtical)

    # 启动事件管理器 启动事件处理线程
    eventManager.Start()

    publicAcc = PublicAccounts(eventManager)
    publicAcc.WriteNewArtical()


    app.exec_()
if __name__ == '__main__':
    test()