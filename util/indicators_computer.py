# Author: Nike Liu
import pandas as pd

class Indicators_compute():
    def __init__(self,df,ndays):
        self.df = df
        self.ndays = ndays

    # Exponentially-weighted Moving Average
    def EWMA(self):
        EMA = pd.Series(pd.ewma(self.df['close'], span=self.ndays, min_periods=self.ndays - 1),
                        name='ewma_' + str(self.ndays))
        data = self.df.join(EMA)
        return data

    # 商品通道指数 Commodity Channel Index
    def CCI(self):
        """当CCI指标＞100时，就表示有超买的情形，当它从上向下穿过100时，就可以做空（卖出）
            当CCI指标＜100时，就表示有超卖的情形，当它从下向上穿过100时，就可以多多（买进）
            如果是已经开仓的情况下，就要用±75值的线来做参考分析是否平仓
            在做空时（卖单），当CCI指标穿过＋75，0，－75，然后再回穿任意一条线时就平仓
            在做多时（买单），当CCI指标穿过－75，0，＋75，然后再回穿任意一条线时就平仓"""

        TP = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        CCI = pd.Series((TP - TP.rolling(self.ndays).mean()) / (0.015 * TP.rolling(self.ndays).std()), name='cci')
        data = self.df.join(CCI)
        return data

    # 简易波动指标 Ease of Movement
    def EVM(self):
        """如果较少的成交量较能推动股价上涨，则EMV数值会升高，相反的股价下跌时也仅伴随较少的成交量，则EMV数值将降低。
        另外，如价格不涨不跌，或者价格的上涨和下跌都伴随着较大的成交量时，则EMV的数值会趋近于零。"""

        dm = ((self.df['high'] + self.df['low']) / 2) - ((self.df['high'].shift(1) + self.df['low'].shift(1)) / 2)
        br = (self.df['volume'] / 100000000) / (self.df['high'] - self.df['low'])
        EVM = dm / br
        EVM_MA = pd.Series(EVM.rolling(self.ndays).mean(), name='evm')
        data = self.df.join(EVM_MA)
        return data

    # Rate of Change (ROC)
    def ROC(self):
        N = self.df['close'].diff(self.ndays)
        D = self.df['close'].shift(self.ndays)
        ROC = pd.Series(N / D, name='roc')
        data = self.df.join(ROC)
        return data