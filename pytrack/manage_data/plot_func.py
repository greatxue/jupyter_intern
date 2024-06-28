import matplotlib.pyplot as plt

def plot_rank_bin(alpha_PD):
    plt.figure()
    rank_bin_stat = alpha_PD.factor_rank_bin.value_counts()
    print("Data volume for different ranks: ")
    print(rank_bin_stat)
    
    (alpha_PD.groupby(
        ['factor_rank_bin', 'trade_date']).ret1.mean() - 1).unstack().T.cumsum().plot(rot=45)
    plt.show()

def plot_ret(alpha_PD):
    plt.figure()
    long_ret = (alpha_PD[(alpha_PD.factor_rank_bin == 5)].groupby('trade_date').ret1.mean()-1).cumsum()
    short_ret = (alpha_PD[(alpha_PD.factor_rank_bin == 1)].groupby('trade_date').ret1.mean()-1).cumsum()
    
    (long_ret - short_ret).plot(rot=45)
    plt.show()

def IC_plot(alpha_PD):
    plt.figure()
    ICvalue = alpha_PD.groupby(['trade_date'])[['factor','ret1']].corr()['factor'].reset_index()
    ICvalue = ICvalue[ICvalue.level_1=='ret1']
    ICvalue = ICvalue[['trade_date','factor']].set_index('trade_date')
    
    mean_ic = ICvalue.mean().tolist()[0]
    std_ic = ICvalue.std().tolist()[0]    
    print(f"The mean of IC is {mean_ic}; \nThe standardized IC is {mean_ic / std_ic}.")
    
    ICvalue.plot(rot=45)
    plt.show()

def plot_all(alpha_PD):
    plot_rank_bin(alpha_PD)
    print("========================================================================")
    plot_ret(alpha_PD)
    print("========================================================================")
    IC_plot(alpha_PD)