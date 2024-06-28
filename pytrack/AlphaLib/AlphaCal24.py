from AlphaLib.utility_func import *

class AlphaCal24(object):
    def __init__(self, daily_info):
        self.open = daily_info['open']
        self.high = daily_info['high']
        self.low = daily_info['low']
        self.close = daily_info['close']
        self.vwap = daily_info['vwap']   
        self.volume = daily_info['volume'] 
        self.amount = daily_info['amount']
        self.returns = daily_info['returns']
    
    def alpha001(self):
        T = 260
        RP_t = pd.Series(0, index=self.close.index)
        
        for n in range(1, T + 1):
            V_t_n = self.volume.shift(n)
            P_t_n = self.close.shift(n)
            if n > 1:
                prod_term = (1 - self.volume.shift(1)).rolling(window=n-1).apply(np.prod, raw=True)
            else:
                prod_term = 1 - self.volume.shift(1)
            impact = V_t_n * prod_term * P_t_n
            RP_t = RP_t.add(impact, fill_value=0)
        
        k = RP_t.sum()
        RP_t /= k
    
        P_t_1 = self.close.shift(1)
        CGO_t = (P_t_1 - RP_t) / P_t_1
        return CGO_t
    
    def alpha002(self, n=12, m=6):
        roc = (self.close - self.close.shift(n)) / self.close.shift(n)
        rocma = roc.rolling(window=m).mean()
        return -abs(roc - rocma)
    
    def alpha003(self, win=40):
        illiq = (self.returns.abs() / self.amount)
        rolling_std = illiq.rolling(window=win).std()
        rolling_mean = illiq.rolling(window=win).mean()
        cvilliq = -rolling_std / rolling_mean
        return cvilliq
    