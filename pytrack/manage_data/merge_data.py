import numpy as np
import pandas as pd
from numpy import abs
from numpy import log
from numpy import sign
from scipy.stats import rankdata
import tushare as ts

# Data port (data_source, data_source_unadj, indus_source) transferred to compute_alpha.py

def manage_data(data_source, data_source_unadj, indus_source) -> dict:
    pro = ts.pro_api('20240522230128-d50d7a15-d7c5-47d4-bccc-25f6c754496a')
    pro._DataApi__http_url = 'http://tsapi.majors.ltd:7000'
 
    # read in the stock index list
    price_PD = pd.read_csv(data_source, dtype = {'trade_date': 'str'})
    price_PD = price_PD.drop_duplicates(['ts_code', 'trade_date']).sort_values(
                                ['ts_code', 'trade_date']).reset_index(drop=True)
    price_PD = price_PD[price_PD.trade_date>='20150101'] # set datetime 
    all_stock = pro.stock_basic()
    all_stock = all_stock[['ts_code', 'name', 'market']]
    
    # merge stock indices with trading stat
    price_PD = pd.merge(price_PD, all_stock, how='left', on='ts_code')
    price_PD = price_PD[['ts_code', 'name', 'market', 'trade_date', 'open', 'high', 'low','close', 
                            'pre_close','change', 'pct_chg', 'vol', 'amount']]
    
    # merge stock indices with industrial info
    indus = pd.read_csv(indus_source, encoding='gbk')
    indus = indus[['windcode','申万行业L1','申万行业L2','申万行业L3']]
    indus.columns = ['ts_code','indus1','indus2','indus3']
    indus = indus[(indus['indus1'] != 0) | (indus['indus2'] != 0) | (indus['indus3'] != 0)].dropna()

    price_PD = pd.merge(price_PD, indus, how='left', on='ts_code')

    # choose stocks with high quality and kick out STs
    price_PD = price_PD[price_PD.market.isin(['主板','中小板','创业板'])]
    price_PD = price_PD[~price_PD.name.str.contains('ST')].reset_index(drop=True)

    price_PD['ret1'] = price_PD.groupby('ts_code').close.shift(-1) \
                        / price_PD.groupby('ts_code').close.shift(0) 
    
    price_PD_unadj = pd.read_csv(data_source_unadj)
    price_PD_unadj.trade_date = price_PD_unadj.trade_date.astype('str')
    price_PD_unadj = price_PD_unadj.drop_duplicates(['ts_code', 'trade_date']).sort_values(
                                            ['ts_code', 'trade_date']).reset_index(drop=True)
    price_PD_unadj['vwap'] = price_PD_unadj.amount / price_PD_unadj.vol
    # comfirm index accordance after merge
    price_PD_unadj = price_PD_unadj[price_PD_unadj.ts_code.isin(price_PD.ts_code.unique())]  

    # output a dict containing daily trading stat
    # vwap = volume weighted average price
    daily_info = {}
    daily_info['open'] = price_PD_unadj.pivot(index='trade_date', columns='ts_code', values='open')
    daily_info['close'] = price_PD_unadj.pivot(index='trade_date', columns='ts_code', values='close')
    daily_info['high'] = price_PD_unadj.pivot(index='trade_date', columns='ts_code', values='high')
    daily_info['low'] = price_PD_unadj.pivot(index='trade_date', columns='ts_code', values='low')
    daily_info['volume'] = price_PD_unadj.pivot(index='trade_date', columns='ts_code', values='vol')
    daily_info['amount'] = price_PD_unadj.pivot(index='trade_date', columns='ts_code', values='amount')
    daily_info['vwap'] = (daily_info['amount'] * 1000) / (daily_info['volume'] * 100 + 1)
    daily_info['returns'] = price_PD.pivot(index='trade_date', columns='ts_code', values='pct_chg') 

    return daily_info, price_PD




