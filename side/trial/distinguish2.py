import os
import pandas as pd
import numpy as np

#指定数据存储目录
directory = '/Users/kevinshuey/massive_dataset/quant_intern'

results = []
for filename in os.listdir(directory):
    if filename.endswith('.txt'):  #只要数据文件
        file_path = os.path.join(directory, filename)
        
        df_u = df[['TDATE', 'TTIME', 'UPDATEMILLISEC', 
         'LASTPX', 'B1', 'S1', 'AVGPX', 'TQ', 'OPENINTS']]

        for i in ['LASTPX', 'B1', 'S1', 'AVGPX', 'TQ', 'OPENINTS']:
            missing = df_u[i].isnull().sum()
            print(f"Missing {i}: {missing}")
            
        df_u = df_u.dropna(subset=['LASTPX', 'S1', 'B1', 'AVGPX'])

        #作差求出最后报价的变化、现手的变化。
        df_pre = df_u.copy().shift(1)
        df_pre["dP"] = df_u["LASTPX"] - df_pre["LASTPX"]
        df_pre["dVOL"] = df_u["TQ"] - df_pre["TQ"]
        df_pre.head()

        #根据上一单最后报价和买一和卖一的关系，判断该单为主动买或者主动卖，并打上标签。
        con_buy = (df_u['LASTPX'] >= df_pre['B1']) | (df_u['LASTPX'] >= df_u['B1'])
        con_sell = (df_u['LASTPX'] <= df_pre['S1']) |(df_u['LASTPX'] <= df_u['S1'])
        dir_val = np.where(con_buy, 'BUY', np.where(con_sell, 'SELL', 'Unclassified'))

        df_pre['direction'] = pd.Series(dir_val, index=df_u.index)
        df_pre.dropna()
        
        df_buy = df_pre[df_pre['direction'] == 'BUY']
        df_sell = df_pre[df_pre['direction'] == 'SELL']

        print(f"Buy total {abs(df_buy.dVOL.sum())}, sell total {abs(df_sell.dVOL.sum())}.")

        #使用列表统一打印，应对多文件输入
        results.append({
            'filename': filename,
            'buy_vol': buy_vol,
            'sell_vol': sell_vol,
            'mid_vol': mid_vol
        })

results_df = pd.DataFrame(results)
print(results_df)
