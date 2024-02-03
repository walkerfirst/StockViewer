#  -*- coding: utf-8 -*-

from pymongo import ASCENDING
from util.database import DB_CONN
from datetime import datetime, timedelta
import pandas as pd
import json
import time
import tushare as ts


def get_trading_dates(begin_date=None, end_date=None):
    """
    获取指定日期范围的按照正序排列的交易日列表
    如果没有指定日期范围，则获取从当期日期向前365个自然日内的所有交易日

    :param begin_date: 开始日期
    :param end_date: 结束日期
    :return: 日期列表
    """
    # 开始日期，默认今天向前的365个自然日
    now = datetime.now()
    if begin_date is None:
        one_year_ago = now - timedelta(days=365)
        begin_date = one_year_ago.strftime('%Y-%m-%d')

    # 结束日期默认为今天
    if end_date is None:
        end_date = now.strftime('%Y-%m-%d')

    daily_cursor = DB_CONN.daily_index.find(
        {'code': '399001', 'date': {'$gte': begin_date, '$lte': end_date}},
        sort=[('date', ASCENDING)],
        projection={'date': True, '_id': False})

    dates = [x['date'] for x in daily_cursor]

    return dates


def get_all_codes(date=None):
    """
    获取某个交易日的所有股票代码列表，如果没有指定日期，则从当前日期一直向前找，直到找到有
    数据的一天，返回的即是那个交易日的股票代码列表

    :param date: 日期
    :return: 股票代码列表
    """

    datetime_obj = datetime.now()
    if date is None:
        date = datetime_obj.strftime('%Y-%m-%d')

    codes = []
    while len(codes) == 0:
        code_cursor = DB_CONN.daily_hfq.find(
            {'date': date},
            projection={'code': True, '_id': False})

        codes = [x['code'] for x in code_cursor]

        datetime_obj = datetime_obj - timedelta(days=1)
        date = datetime_obj.strftime('%Y-%m-%d')

    return codes

def get_all_data(db_name):
    """
    获取某个因子在某个交易日的所有股票的数据
    :param factor: 因子名称
    :param date: 日期
    :return: DataFrame(columns=['code',factor, 'date'])
    """

    collection = DB_CONN[db_name]
    cursor = collection.find({},projection={'_id': False})
    df = pd.DataFrame(list(cursor))
    return df

def save_data_to_db(df,db_name):
    db = DB_CONN[db_name]
    db.insert_many(json.loads(df.T.to_json()).values())
    print('data saving is done')

# def check_data_is_holiday(date):
#     return tushare.is_holiday(datetime.strftime(date,"%Y-%m-%d"))

def check_today_is_holiday():
    date_ = datetime.now().strftime('%Y-%m-%d')
    symbols = ['399006']
    try:
        data = ts.get_realtime_quotes(symbols)
        if not data.empty:
            date_tick = data.iloc[0]['date']
            # print(date_tick,date_tick)
            if date_ != date_tick:
                return True
            else:
                return False
        else:
            return False
    except:
        return False

if __name__ == '__main__':
    x = check_today_is_holiday()
    print(x)