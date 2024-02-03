#  -*- coding: utf-8 -*-

from pymongo import UpdateOne
from util.database import DB_CONN
import tushare as ts
from datetime import datetime,timedelta
import json
import pandas as pd

"""
从tushare获取日K数据，保存到本地的MongoDB数据库中
"""


class DailyCrawler:
    def __init__(self):
        self.buy_db = DB_CONN['buy_record']
        self.sell_db = DB_CONN['sell_record']
    def crawl_index(self,df=None):
        """
        抓取指数的日线数据，并保存到本地数据数据库中
        抓取的日期范围从2008-01-01至今
        """

        # 设置默认的日期范围buy.xlsx

        df = pd.read_excel(r'../db/buy.xlsx',encoding='gbk')
        # df = pd.read_excel(r'./data/组合.xlsx', encoding='gbk')
        print(df.head(5))
        x = df['日期'].iloc[1]
        print(type(x))

        # self.buy_db.insert_many(json.loads(df.T.to_json()).values())
        print('daily_index is done')


    def crawl(self, begin_date=None, end_date=None):
        """
        获取所有股票从2008-01-01至今的K线数据（包括前复权、后复权和不复权三种），保存到数据库中
        """
        print('start crawl daily')
        # 获取所有股票代码
        stock_df = ts.get_stock_basics()
        codes = list(stock_df.index)

        # 设置默认的日期范围
        if begin_date is None:
            begin_date = '2008-01-01'

        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        for code in codes:
            # 抓取后复权的价格
            df_daily_hfq = ts.get_k_data(code, autype='hfq', start=begin_date, end=end_date)
            if df_daily_hfq.index.size > 0:
                self.daily_hfq.insert_many(json.loads(df_daily_hfq.T.to_json()).values())
        print('daily_hfq is done')

    def crawl_hs300(self, begin_date=None, end_date=None):
        """
        获取所有股票从2004-01-01至今的hs300日K线数据（后复权），保存到数据库中
        """

        # 获取所有股票代码
        codes = ts.get_hs300s()['code'].tolist()

        # 设置默认的日期范围
        if begin_date is None:
            begin_date = '2008-01-01'

        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        for code in codes:
            # 抓取后复权的价格
            df_daily = ts.get_k_data(code, autype='hfq', start=begin_date, end=end_date)
            if df_daily.index.size > 0:
                self.daily_hs300.insert_many(json.loads(df_daily.T.to_json()).values())
                # print(df_daily)
        print('it is finished')

if __name__ == '__main__':

    dc = DailyCrawler()

    # 抓取指数
    dc.crawl_index()

