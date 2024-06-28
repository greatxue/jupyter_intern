import pandas as pd
import numpy as np
from AlphaLib.Alpha101 import Alpha101
from AlphaLib.AlphaCal24 import AlphaCal24
from manage_data.merge_data import manage_data 

class_dict = {
    'Alpha101': Alpha101,
    'AlphaCal24': AlphaCal24
    # to continue
}

def classify(x):
    if x < 0.2: 
        return 1
    elif 0.2 <= x < 0.4: 
        return 2
    elif 0.4 <= x < 0.6: 
        return 3
    elif 0.6 <= x < 0.8: 
        return 4
    elif 0.8 <= x <= 1: 
        return 5
    else: 
        return np.nan

def compute_alpha(alpha_class: str, alpha_index:int, 
                data_source='/Users/kevinshuey/massive_dataset/a_stock/price_PD.csv',
                data_source_unadj='/Users/kevinshuey/massive_dataset/a_stock/price_PD_unadj.csv', 
                indus_source='/Users/kevinshuey/massive_dataset/a_stock/a_stock_industry.csv'
                ):
    selected_class = alpha_class
    SelectedClass = class_dict[selected_class]
    daily_info, price_PD = manage_data(data_source, data_source_unadj, indus_source)
    
    tmp_class = SelectedClass(daily_info)
    
    alpha_dict = {}
    alpha_number = f"{alpha_index:03}"  
    alpha_name = f"alpha{alpha_number}"
    alpha_method = getattr(tmp_class, alpha_name)
    alpha_dict[alpha_name] = alpha_method()

    alpha_PD = alpha_dict[alpha_name].unstack().reset_index().rename(columns={0:'factor'})
    #alpha_PD = alpha_PD.dropna()
    alpha_PD = pd.merge(alpha_PD, price_PD[['trade_date', 'ts_code','ret1','indus1']], 
                        how='left', on=['trade_date', 'ts_code'])
    alpha_PD['factor_rank'] = alpha_PD.groupby(['trade_date','indus1']).factor.rank(
                        pct=True, method='dense')
    
    alpha_PD['factor_rank_bin'] = alpha_PD.factor_rank.apply(classify)

    return alpha_PD

