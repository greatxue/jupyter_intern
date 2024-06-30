#####################################################################################
# Reference：https://doi.org/10.5445/KSP/1000085951/20

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


dir = '/Users/kevinshuey/massive_dataset/quant_intern'

for filename in os.listdir(dir):
    if filename.endswith('.txt'):  
        path = os.path.join(dir, filename)
        
        df = pd.read_csv(path, sep='\t', header=0)
        df_u = df[['TDATE', 'TTIME', 'UPDATEMILLISEC', 'LASTPX', 'B1', 'S1', 'AVGPX', 'TQ', 'OPENINTS']]
        df_u = df_u.dropna(subset=['LASTPX', 'S1', 'B1', 'AVGPX'])
        
        df_u['CRTPX'] = df['LASTPX'].shift(-1)
        df_u['MID'] = (df_u['B1'] + df_u['S1']) / 2

        # Stage I: Comparison between P_t and P_t^{mid}
        buy_stage1 = df_u['CRTPX'] > df_u['MID']
        sell_stage1 = df_u['CRTPX'] < df_u['MID']
        equal_stage1 = df_u['CRTPX'] == df_u['MID']
        dir1 = np.where(buy_stage1, 'BUY', np.where(sell_stage1, 'SELL', 'EQUAL'))
        df_u['dir1'] = dir1

        # Stage II: Comparison between P_{t-1} and P_t^{mid}
        df_u['dir2'] = np.where(df_u['dir1'] != 'EQUAL', df_u['dir1'], 'NA1')
        df_equal = df_u[df_u['dir1'] == 'EQUAL']

        buy_stage2 = (df_u['MID'].loc[df_equal.index] > df_u['LASTPX'].loc[df_equal.index])
        sell_stage2 = (df_u['MID'].loc[df_equal.index] < df_u['LASTPX'].loc[df_equal.index])
        dir2 = np.where(buy_stage2, 'BUY', np.where(sell_stage2, 'SELL', 'NA2'))
        df_u.loc[df_equal.index, 'dir2'] = dir2
        
        # Stage III: Comparison between P_{t} and P_{t-k}
        df_u['dP'] = df_u['CRTPX'].diff()

        nonzero_indices = df_u.index[df_u['dP'] != 0]
        df_u['LASTID'] = np.nan
        df_u.loc[nonzero_indices, 'LASTID'] = nonzero_indices
        df_u['LASTID'] = df_u['LASTID'].ffill().astype(int)

        df_u['LASTVAL'] = df_u['LASTID'].apply(lambda x: df_u.at[x, 'CRTPX'])

        def Dir3(row):
            if row['dir2'] == 'SELL':
                return 'SELL'
            elif row['dir2'] == 'BUY':
                return 'BUY'
            elif row['dir2'] == 'NA2':
                if row['CRTPX'] > row['LASTVAL']:
                    return 'BUY'
                elif row['CRTPX'] < row['LASTVAL']:
                    return 'SELL'
                else:
                    return 'NA3'
            else:
                return 'NA3'
        # 'apply' methods will consume a little more time
        df_u['dir3'] = df_u.apply(Dir3, axis=1)
        
        count_na3 = (df_u['dir3'] == 'NA3').sum()
        count_buy = (df_u['dir3'] == 'BUY').sum()
        count_sell = (df_u['dir3'] == 'SELL').sum()
        counts = {
            'Category': ['BUY', 'SELL', 'N/A'],
            'Count': [count_buy, count_sell, count_na3]
        }

        df_counts = pd.DataFrame(counts)

        print(df_counts)

        df_u['buy_count'] = (df_u['dir3'] == 'BUY').cumsum()
        df_u['sell_count'] = (df_u['dir3'] == 'SELL').cumsum()
        
        plt.figure(figsize=(12, 6))
        plt.plot(df_u.index, df_u['buy_count'], label='Buy Count', marker='o')
        plt.plot(df_u.index, df_u['sell_count'], label='Sell Count', marker='x')
        plt.xlabel('Entry Number')
        plt.ylabel('Cumulative Count')
        plt.title(f'{filename}: Cumulative Buy/Sell Counts')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{filename[:-4]}.png")
        plt.show()
        
        
