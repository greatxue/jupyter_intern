import pandas as pd

RISK_FREE = 1.0015

def cal_sell_turnover(tmp):
    '''return the daily sell turnover rate for a given period'''
    stock = pd.DataFrame(
        tmp.groupby('trade_date').apply(lambda x: set(x.ts_code))).rename(columns={0:'stock_list'})
    stock['stock_list_shift1'] = stock.stock_list.shift(1)
    stock = stock.dropna()
    
    freq = []
    for i in range(len(stock)):
        freq.append(1 - len(stock.iloc[i]['stock_list'] & \
                stock.iloc[i]['stock_list_shift1']) / len(stock.iloc[i]['stock_list']))
    stock['freq'] = freq
    return stock['freq'].mean()


def max_dd(returns):
    '''return the maximum drawdown of the portfolio, with its start date and end date'''
    r = returns.cumsum()+1
    dd = r.div(r.cummax()).sub(1)
    mdd = dd.min()
    end = returns.index[dd.argmin()]
    start = returns.index[r.loc[:end].argmax()]
    
    return mdd, start, end    # return a pandas Series


def max_dd_month(ret_PD):
    '''return key values about monthly returns'''
    ret2_month = ret_PD.reset_index()
    ret2_month['month'] = [str(xx)[:6] for xx in ret2_month['trade_date']]    
    ret2_month = ret2_month.groupby('month')['ret'].sum()
    ret2_month = ret2_month.sort_values()
    
    return [ret2_month.head(1).values[0], ret2_month.head(1).index[0],\
            (ret2_month > 0).sum() / len(ret2_month), ret2_month[ret2_month >= 0].mean(),\
            ret2_month[ret2_month < 0].mean()]

 

def calc_pfmc(ret_PD):
    '''return the evaluation for the performance of different investment strategies'''
    performance = []
    for i in [1, 2, 3, 4, 5, 'diff']:
        returnlist = ret_PD[i]
        ret_year = (returnlist.mean() - 0) * 252    # 252 trade days one year, by default
        ret_sharpe = (returnlist.mean() - 0) / returnlist.std() * (252**0.5)
        max_draw, start, end = max_dd(returnlist)
        winratio = (returnlist > 0).sum() / len(returnlist)
        std = returnlist.std()
        performance.append([i, ret_year, ret_sharpe, std, winratio, max_draw])
    performance = pd.DataFrame(performance, 
                    columns = ['group_name','return','sharpe','std','winratio','mdd'])
    return performance


def evaluate_alpha(alpha_PD):
    ret_PD = (
        alpha_PD.groupby(['factor_rank_bin', 'trade_date']).ret1.mean() - RISK_FREE).unstack().T

    if ret_PD[1.0].mean() > ret_PD[5.0].mean():
        ret_PD['diff'] = ret_PD[1.0] - ret_PD[5.0]
    else:
        ret_PD['diff'] = ret_PD[5.0] - ret_PD[1.0]

    return calc_pfmc(ret_PD)