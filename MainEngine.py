# Author: Nike Liu
from datetime import datetime
from DataEngine import DataEngine
from event.eventEngine import Event
from event.eventType import *


class MainEngine(object):
    """主引擎"""

    def __init__(self, eventEngine):
        """Constructor"""
        # 记录今日日期
        self.todayDate = datetime.now().strftime('%Y-%m-%d')

        # 创建事件引擎
        self.eventEngine = eventEngine
        self.eventEngine.Start()

        # 创建数据引擎
        self.dataEngine = DataEngine()
        # 持仓dataframe 字典
        self.positionDict = self.dataEngine.positionDict
        # 持仓symbol
        self.mySymbols = self.dataEngine.mySymbols

        # 账户信息
        self.accDict = self.dataEngine.accDict
    def qryDB(self,sql,columns = None):
        # 数据库查询
        return self.dataEngine.dbQurey(sql,columns)

    def excuteSQL(self,sql):
        """执行SQL到access"""
        self.dataEngine.excuteSQL(sql)

    def qryPosition(self,accountName):
        """获取持仓dataframe"""
        return self.dataEngine.qryPosition(accountName)

    def qryAccount(self,accountName):
        """获取账户信息的dataframe"""
        return self.dataEngine.qryAccount(accountName)

    def qryMysymbols(self,account='all'):
        """ 获取全部持仓的code list"""
        return self.dataEngine.qryMysymbols(account)

    def getAccDict(self):
        """获取账户信息Dict"""
        return self.dataEngine.getAccDict()

    def getPostionDict(self):
        """将持仓信息df添加到字典中"""
        return self.dataEngine.getPostionDict()

    # 订阅需要推送的tick 列表
    def subcribeTick(self,symbols):
        self.dataEngine.subcribeTick(symbols)

    def getTick(self, symbols):
        return self.dataEngine.getTick(symbols)

    # 合并两个dataframe，获取需要的样式
    def processData(self, left, right):
        return self.dataEngine.processData(left,right)

    # 注册事件源，put tick data 到 event
    def sendEvent(self,event):
        self.eventEngine.SendEvent(event)

    # 注册监听函数（数据使用者）
    def registerHandler(self,type_,handler):
        self.eventEngine.AddEventListener(type_, handler)

    def exit(self):
        """退出程序前调用，保证正常退出"""

        # 停止事件引擎
        self.eventEngine.Stop()

        # 保存数据引擎里的合约数据到硬盘
        # self.dataEngine.saveContracts()

if __name__ == '__main__':
    from event.eventEngine import EventManager

    run = MainEngine(EventManager)
    print(run.positionDict)