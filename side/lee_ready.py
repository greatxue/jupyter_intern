#####################################################################################
# 参考文献：https://doi.org/10.5445/KSP/1000085951/20

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 指定数据存储目录
directory = '/Users/kevinshuey/massive_dataset/quant_intern'

# 处理每个文件并生成图表
for filename in os.listdir(directory):
    if filename.endswith('.txt'):  # 只要数据文件
        file_path = os.path.join(directory, filename)
        
        df = pd.read_csv(file_path, sep='\t', header=0)
        
        df_u = df[['TDATE', 'TTIME', 'UPDATEMILLISEC', 'LASTPX', 'B1', 'S1', 'AVGPX', 'TQ', 'OPENINTS']]
        
        df_u = df_u.dropna(subset=['LASTPX', 'S1', 'B1', 'AVGPX'])

        # 作差求出最后报价的变化、现手的变化
        df_u['dP'] = df_u["LASTPX"].diff()
        df_u['dVOL'] = df_u["TQ"].diff()

        # 计算当前最优买卖报价均值
        avg_best_bid_ask = (df_u['B1'] + df_u['S1']) / 2

        # Stage I 判断主动买卖方向
        buy_condition_stage1 = df_u['LASTPX'] > avg_best_bid_ask
        sell_condition_stage1 = df_u['LASTPX'] < avg_best_bid_ask
        equal_condition_stage1 = df_u['LASTPX'] == avg_best_bid_ask

        direction_stage1 = np.where(buy_condition_stage1, 'BUY', np.where(sell_condition_stage1, 'SELL', 'EQUAL'))

        # Stage II 判断在 Stage I 中为 EQUAL 的交易
        df_u['direction_stage1'] = direction_stage1
        df_u['direction_stage2'] = 'Unclassified'  # 初始化

        # 对于 direction_stage1 为 EQUAL 的交易，进一步判断
        df_equal = df_u[df_u['direction_stage1'] == 'EQUAL']
        if not df_equal.empty:
            buy_condition_stage2 = (avg_best_bid_ask.loc[df_equal.index] > df_u['LASTPX'].shift(1).loc[df_equal.index])
            sell_condition_stage2 = (avg_best_bid_ask.loc[df_equal.index] < df_u['LASTPX'].shift(1).loc[df_equal.index])

            direction_stage2 = np.where(buy_condition_stage2, 'BUY', np.where(sell_condition_stage2, 'SELL', 'Unclassified'))
            df_u.loc[df_equal.index, 'direction_stage2'] = direction_stage2

            df_unclassified = df_equal[df_equal['direction_stage2'] == 'Unclassified']

            # 找到最后一次非零价格变化的符号
            last_non_zero_index = (df_u['dP'] != 0).idxmax()

            for index, row in df_unclassified.iterrows():
                if row['LASTPX'] > df_u.loc[last_non_zero_index, 'LASTPX']:
                    df_u.loc[index, 'direction'] = 'BUY'
                elif row['LASTPX'] < df_u.loc[last_non_zero_index, 'LASTPX']:
                    df_u.loc[index, 'direction'] = 'SELL'
                else:
                    df_u.loc[index, 'direction'] = 'Unclassified'
        else:
            df_u['direction_stage2'] = 'Unclassified'

        # 对于 Stage I 和 Stage II 的结果进行合并
        df_u['direction'] = np.where(df_u['direction_stage1'] != 'EQUAL', df_u['direction_stage1'], df_u['direction_stage2'])

        # 计算每个条目的累积买入和卖出单数量
        df_u['buy_count'] = (df_u['direction'] == 'BUY').cumsum()
        df_u['sell_count'] = (df_u['direction'] == 'SELL').cumsum()

        # 绘制折线图
        plt.figure(figsize=(12, 6))
        plt.plot(df_u.index, df_u['buy_count'], label='Buy Count', marker='o')
        plt.plot(df_u.index, df_u['sell_count'], label='Sell Count', marker='x')
        plt.xlabel('Entry Number')
        plt.ylabel('Cumulative Count')
        plt.title(f'Cumulative Buy and Sell Counts for {filename}')
        plt.legend()
        plt.tight_layout()
        plt.show()