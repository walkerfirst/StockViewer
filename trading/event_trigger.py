# Author: Nike Liu
from event.eventEngine import Event
from event.eventType import *
from DataEngine import DataEngine
from setting.symbols import class_symbols,index_symbols

def accountEvent(engine):
    # 定义交易事件类型
    trade_event = Event(type_=EVENT_ACCOUNT)
    # 重新获取持仓股票code
    trade_event.dict['position'] = DataEngine().qryMysymbols()
    # 获取最新的订阅code list
    subcribeSymbols = list(set(trade_event.dict['position'] + index_symbols + class_symbols))
    # 获取一次新的订阅code list 的tick
    tickData = engine.getTick(subcribeSymbols)
    # 设置tick的event 字典
    trade_event.dict['tick'] = tickData
    # 发送交易事件
    engine.sendEvent(trade_event)

def loginEvent(engine):
    login_event = Event(type_=EVENT_LOGIN)
    login_event.dict['confirm'] = "yes"
    engine.sendEvent(login_event)