# Backtrader Docs

## 1. 总览

### 1.1 Backtrader 主要模块

Backtrader 以“大脑”cerebro 为统一的调度中心，数据、策略、回测条件等信息都会导入 cerebro 中，并由 cerebro 启动和完成回测，最后返回回测结果。Cerebro由下列模块组成：

+ **Cerebro 回测执行模块**

  - `adddata()` 输入数据

  - `addsizer()` 添加仓位

  - `addstrategy()` 添加策略

  - `addanalyzer()` 添加分析器

  - `addobserver()` 添加观察器

  - `run()`启动回测

  - `plot()` 可视化

除了cerebro之后，还有以下模块，模拟或者实现交易的各个组成部份：

- **DataFeeds 数据模块**
  - CSVDataBase 导入CSV
  - PandasData 导入
  - YahooFinanceData 导入网站数据
- **Broker 经纪商模块**
  - cash 初始资金
  - commission 手续费
  - slippage 滑点
- **Orders 订单模块**
  - `buy()` 买入
  - `sell()` 卖出
  - `close()` 平仓
  - `cancel()` 取消订单
- **Sizers 仓位模块**
- **Strategy 策略模块**
  - `next()` 主策略函数
  - notify_order, notify_trade 打印订单、交易信息
- **Indicators 指标模块**
  - SMA, EMA 移动均线
  - Ta-lib 技术指标库
- **Analyzers 策略分析模块**
  - AnnualReturn 年化收益
  - SharpeRatio 夏普比率
  - DrawDown 回撤
  - PyFolio 分析工具
- **Observers 观察器模块**
  - Broker 资金市值曲线
  - Trades 盈亏走势
  - BuySell 买卖信号

### 1.2 基本模版

要使用Backtrader进行回测，首先要准备回测数据并编写策略；在实例化`cerebro = Cerebro()`的基础上，设置回测参数和绩效分析指标；最终运行回测`cerebro.run()`，获取回测数据。

下面是一个最基本的使用模版，从中可以反映出Backtrader的使用流程。

```python
import backtrader as bt # 导入 Backtrader
import backtrader.indicators as btind # 导入策略分析模块
import backtrader.feeds as btfeeds # 导入数据模块

# 创建策略
class TestStrategy(bt.Strategy):
    # 可选，设置回测的可变参数：如移动均线的周期
    params = (
        (...,...), # 最后一个“,”最好别删！
    )
    def log(self, txt, dt=None):
        '''可选，构建策略打印日志的函数：可用于打印订单记录或交易记录等'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        '''必选，初始化属性、计算指标等'''
        pass

    def notify_order(self, order):
        '''可选，打印订单信息'''
        pass

    def notify_trade(self, trade):
        '''可选，打印交易信息'''
        pass

    def next(self):
        '''必选，编写交易策略逻辑'''
        sma = btind.SimpleMovingAverage(...) # 计算均线
        pass

# 实例化 cerebro
cerebro = bt.Cerebro()
# 通过 feeds 读取数据
data = btfeeds.backtraderCSVData(...)
# 将数据传递给 “大脑”
cerebro.adddata(data)
# 通过经纪商设置初始资金
cerebro.broker.setcash(...)
# 设置单笔交易的数量
cerebro.addsizer(...)
# 设置交易佣金
cerebro.broker.setcommission(...)
# 添加策略
cerebro.addstrategy(TestStrategy)
# 添加策略分析指标
cerebro.addanalyzer(...)
# 添加观测器
cerebro.addobserver(...)
# 启动回测
cerebro.run()
# 可视化回测结果
cerebro.plot()
```

## 2. 数据处理和调用

### 2.1 数据馈送对象

数据馈送对象（Data Feed）指的是数据表格或数据表格集合，给策略有序提供数据以及数据的索引位置。

Backtrader提供了各种有效的数据索引方法：

+ 带中括号的常规方式： `self.datas[X]`；
+ 不带中括号的缩写方式：`self.dataX`；
+ 使用负向索引位置编号，仅有`self.datas[-1]`；
+ 默认指向第一个导入的数据集，即`self.data` 等价于 `self.datas[0]`或者`self.data0`；
+ 通过表格名称调用数据：`self.getdatabyname('stockN')`，名称在导入数据时通过name参数设置。

下面是一个示例：

```python
class TestStrategy(bt.Strategy):
    def __init__(self):
        # 打印数据集和数据集对应的名称
        print("-------------self.datas-------------")
        print(self.datas)
        print("-------------self.data-------------")
        print(self.data._name, self.data) # 返回第一个导入的数据表格，缩写形式
        print("-------------self.data0-------------")
        print(self.data0._name, self.data0) # 返回第一个导入的数据表格，缩写形式
        print("-------------self.datas[0]-------------")
        print(self.datas[0]._name, self.datas[0]) # 返回第一个导入的数据表格，常规形式
        print("-------------self.datas[1]-------------")
        print(self.datas[1]._name, self.datas[1]) # 返回第二个导入的数据表格，常规形式
        print("-------------self.datas[-1]-------------")
        print(self.datas[-1]._name, self.datas[-1]) # 返回最后一个导入的数据表格
        print("-------------self.datas[-2]-------------")
        print(self.datas[-2]._name, self.datas[-2]) # 返回倒数第二个导入的数据表格
        
cerebro = bt.Cerebro()
st_date = datetime.datetime(2019,1,2)
ed_date = datetime.datetime(2021,1,28)
# 添加 600466.SH 的行情数据
datafeed1 = bt.feeds.PandasData(dataname=data1,
                                fromdate=st_date,
                                todate=ed_date)
cerebro.adddata(datafeed1, name='600466.SH')
# 添加 603228.SH 的行情数据
datafeed2 = bt.feeds.PandasData(dataname=data2,
                                fromdate=st_date,
                                todate=ed_date)
cerebro.adddata(datafeed2, name='603228.SH')
cerebro.addstrategy(TestStrategy)
rasult = cerebro.run()
```

运行后，输出一下内容：

```txt
-------------self.datas-------------
[<backtrader.feeds.pandafeed.PandasData object at 0x7f65f2a9c2b0>, <backtrader.feeds.pandafeed.PandasData object at 0x7f65f2a9c8b0>]
-------------self.data-------------
600466.SH <backtrader.feeds.pandafeed.PandasData object at 0x7f65f2a9c2b0>
-------------self.data0-------------
600466.SH <backtrader.feeds.pandafeed.PandasData object at 0x7f65f2a9c2b0>
-------------self.datas[0]-------------
600466.SH <backtrader.feeds.pandafeed.PandasData object at 0x7f65f2a9c2b0>
-------------self.datas[1]-------------
603228.SH <backtrader.feeds.pandafeed.PandasData object at 0x7f65f2a9c8b0>
-------------self.datas[-1]-------------
603228.SH <backtrader.feeds.pandafeed.PandasData object at 0x7f65f2a9c8b0>
-------------self.datas[-2]-------------
600466.SH <backtrader.feeds.pandafeed.PandasData object at 0x7f65f2a9c2b0>
```

### 2.2 数据的导入

Backtrader 支持导入各式各样的数据：第三方网站加载数据（Yahoo、VisualChart、Sierra Chart、Interactive Brokers 盈透、OANDA、Quandl）、CSV 文件、Pandas DataFrame、InfluxDB、MT4CSV 等，其中最基础或最常见的就是导入 CSV 和导入 DataFrame了。

导入数据大致分 2 步：首先调用 DataFeeds 模块中的方法读取数据，其次将读取的数据传给大脑。以下是一个示例：

```python
# 读取和导入 CSV 文件
data = bt.feeds.GenericCSVData(dataname='filename.csv', ...)
cerebro.adddata(data, name='XXX')
# 读取和导入 dataframe 数据框 - 方式1
data = bt.feeds.PandasData(dataname=df, ...)
cerebro.adddata(data, name='XXX')
# 读取和导入 dataframe 数据框 - 方式2
data = bt.feeds.PandasDirectData(dataname=df, ...)
cerebro.adddata(data, name='XXX')

# 以 GenericCSVData 为例进行参数说明（其他导入函数参数类似）
bt.feeds.GenericCSVData(
    dataname='daily_price.csv', # 数据源，CSV文件名 或 Dataframe对象
    fromdate=st_date, # 读取的起始时间
    todate=ed_date, # 读取的结束时间
    nullvalue=0.0, # 缺失值填充
    dtformat=('%Y-%m-%d'), # 日期解析的格式
    # 下面是数据表格默认包含的 7 个指标，取值对应指标在 daily_price.csv 中的列索引位置
    datetime=0, # 告诉 GenericCSVData， datetime 在 daily_price.csv 文件的第1列
    high=3,
    low=4,
    open=2,
    close=5,
    volume=6,
    openinterest=-1) # 如果取值为 -1 , 告诉 GenericCSVData 该指标不存在
```

如果你觉得每次都要设置这么多参数来告知指标位置很麻烦，那你也可以重新自定义数据读取函数，自定义的方式就是继承数据加载类 GenericCSVData、PandasData 再构建一个新的类，然后在新的类里统一设置参数。

---

**自定义数据读取规则**

自定义的函数，不会修改 Backtrader 底层的数据表格内 lines 的排列规则，只是规定了一个新的数据读取规则。调用这个函数，就按函数里设置的规则来读数据，而不用每次都设置一堆参数：

```python
class My_CSVData(bt.feeds.GenericCSVData):
    params = (
    ('fromdate', datetime.datetime(2019,1,2)),
    ('todate', datetime.datetime(2021,1,28)),
    ('nullvalue', 0.0),
    ('dtformat', ('%Y-%m-%d')),
    ('datetime', 0),
    ('time', -1),
    ('high', 3),
    ('low', 4),
    ('open', 2),
    ('close', 5),
    ('volume', 6),
    ('openinterest', -1)
)

cerebro = bt.Cerebro()
data = My_CSVData(dataname='daily_price.csv')
cerebro.adddata(data, name='600466.SH')
rasult = cerebro.run()
```

在回测时，除了常规的高开低收成交量这些行情数据外，还会用到别的指标，比如选股回测时会用到很多选股因子（PE、PB 、PCF、......），可以给数据表格新增列，也就是给数据表格新增 line。以导入 DataFrame 为例，在继承原始的数据读取类 bt.feeds.PandasData 的基础上，设置 lines 属性和 params 属性，新的 line 会按其在 lines 属性中的顺序依次添加进数据表格中，具体对照下面例子的输出部分：

```python
class PandasData_more(bt.feeds.PandasData):
    lines = ('pe', 'pb', ) # 要添加的线
    # 设置 line 在数据源上的列位置
    params=(
        ('pe', -1),
        ('pb', -1),
           )
    # -1表示自动按列明匹配数据，也可以设置为线在数据源中列的位置索引 (('pe',6),('pb',7),)
class TestStrategy(bt.Strategy):
    def __init__(self):
        print("--------- 打印 self.datas 第一个数据表格的 lines ----------")
        print(self.data0.lines.getlinealiases())
        print("pe line:", self.data0.lines.pe)
        print("pb line:", self.data0.lines.pb)

data1['pe'] = 2 # 给原先的data1新增pe指标（简单的取值为2）
data1['pb'] = 3 # 给原先的data1新增pb指标（简单的取值为3）
# 导入的数据 data1 中
cerebro = bt.Cerebro()
st_date = datetime.datetime(2019,1,2)
ed_date = datetime.datetime(2021,1,28)
datafeed1 = PandasData_more(dataname=data1,
                            fromdate=st_date,
                            todate=ed_date)
cerebro.adddata(datafeed1, name='600466.SH')
cerebro.addstrategy(TestStrategy)
result = cerebro.run()
```

### 2.3 数据中的行和列

**行数据对象**

Backtrader 数据表格的行，可以看做是蜡烛图中的一个个 bar ，只不过这个 bar 包含的信息并不局限于“高开低收” 4 个指标，可以指向在这个时间点上的所有信息。

回测其实就是按时间先后顺序依次循环遍历各个带有历史行情信息的 bar，检验策略在历史行情上的表现。

---

**列数据对象**

Backtrader 将数据表格的列拆成了一个个 line 线对象，一列就是一个指标，就是该指标的时间序列，就是一条线 line。默认情况下，数据表格要包含 7 个字段：datetime、 open、 high、 low、 close、 volume、openinterest ，回测过程中用到的时间序列行情数据可视化后就是一条条曲线，一个字段就对应了一条条线。

因为可以将 Data Feed 对象看做是数据表格，而表格中又包含列，所以每一个 Data Feed 对象都有一个 lines 属性。可以将 lines 属性看作是 line 的集合，所以想要调用具体的某一条线，就通过 lines 属性来调用： 

+ 访问 lines 属性`xxx.lines`，可简写成 `xxx.l`； 
+ 访问 lines 属性中具体某条线：`xxx.lines.name`，可简写成 `xxx.lines_name`；
+ 套用“先调用某张数据表格，再调用这张表格中具体的某根 line”的逻辑依次编写代码； 
+ 可以通过 `getlinealiases()` 方法查看 Data Feed 对象包含哪些线。

```python
# 访问第一个数据集的 close 线
self.data.lines.close # 可省略 lines 简写成：self.data.close
self.data.lines_close # 可省略 lines 简写成：self.data_close
# 访问第二个数据集的 open 线
self.data1.lines.close # 可省略 lines 简写成：self.data1.close
self.data1.lines_close # 可省略 lines 简写成：self.data1_close
# 注：只有从 self.datas 调用 line 时可以省略 lines，调用 indicators 中的 line 时不能省略
```

也可以通过索引位置的办法，X 对应数据表格在数据表格集合中的索引位置，Y 对应线在数据表格中的索引位置：

+ 完整形式：`self.datas[X].lines[Y]`
+ 简写形式：`self.dataX.lines[Y]`, `self.dataX_Y`

---

**列数据上的数据点索引**

指明了一个line对象后，进一步还可以提取line上面数据点，并根据索引位置访问需要的数据：

+ 索引规则：索引位置编号结合了时间信息，0 号位置永远指向当前时间点的数据，-1 号位置指向前一个时间点的数据，然后依次回退 （backwards）-2、-3、-4、-5、......；1 号位置指向下一天的数据，然后依次向前（forwards）2、3、4、......； 

+ 切片方法：`get(ago=0, size=1)` 函数，其中 ago 对应数据点的索引位置，即从 ago 时间点开始往前取 size 个数据点。默认情况下是取当前最新时点（ago=0）的那一个数据（size=1）。

值得注意的是，对数据点的索引切片操作一般在 `next()` 函数中涉及较多，而` __init__()` 中涉及较少，因为`__init__()` 中一般是对一整条 line 进行操作。这是一个示例：

```python
class TestStrategy(bt.Strategy):
    def __init__(self):
        self.count = 0 # 用于计算 next 的循环次数
        # 打印数据集和数据集对应的名称
        print("------------- init 中的索引位置-------------")
        print("0 索引：",'datetime',self.data1.lines.datetime.date(0), 'close',self.data1.lines.close[0])
        print("-1 索引：",'datetime',self.data1.lines.datetime.date(-1),'close', self.data1.lines.close[-1])
        print("-2 索引",'datetime', self.data1.lines.datetime.date(-2),'close', self.data1.lines.close[-2])
        print("1 索引：",'datetime',self.data1.lines.datetime.date(1),'close', self.data1.lines.close[1])
        print("2 索引",'datetime', self.data1.lines.datetime.date(2),'close', self.data1.lines.close[2])
        print("从 0 开始往前取3天的收盘价：", self.data1.lines.close.get(ago=0, size=3))
        print("从-1开始往前取3天的收盘价：", self.data1.lines.close.get(ago=-1, size=3))
        print("从-2开始往前取3天的收盘价：", self.data1.lines.close.get(ago=-2, size=3))
        print("line的总长度：", self.data1.buflen())
        
    def next(self):
        print(f"------------- next 的第{self.count+1}次循环 --------------")
        print("当前时点（今日）：",'datetime',self.data1.lines.datetime.date(0),'close', self.data1.lines.close[0])
        print("往前推1天（昨日）：",'datetime',self.data1.lines.datetime.date(-1),'close', self.data1.lines.close[-1])
        print("往前推2天（前日）", 'datetime',self.data1.lines.datetime.date(-2),'close', self.data1.lines.close[-2])
        print("前日、昨日、今日的收盘价：", self.data1.lines.close.get(ago=0, size=3))
        print("往后推1天（明日）：",'datetime',self.data1.lines.datetime.date(1),'close', self.data1.lines.close[1])
        print("往后推2天（明后日）", 'datetime',self.data1.lines.datetime.date(2),'close', self.data1.lines.close[2])
        print("已处理的数据点：", len(self.data1))
        print("line的总长度：", self.data0.buflen())
        self.count += 1
        
cerebro = bt.Cerebro()
st_date = datetime.datetime(2019,1,2) # 起始时间
ed_date = datetime.datetime(2021,1,28) # 结束时间
datafeed1 = bt.feeds.PandasData(dataname=data1,
                                fromdate=st_date,
                                todate=ed_date)
cerebro.adddata(datafeed1, name='600466.SH')
datafeed2 = bt.feeds.PandasData(dataname=data2,
                                fromdate=st_date,
                                todate=ed_date)
cerebro.adddata(datafeed2, name='603228.SH')
cerebro.addstrategy(TestStrategy)
result = cerebro.run()
```

以下是输出结果：

```txt
------------- init 中的索引位置-------------
0 索引：datetime 2021-01-28 close 54.91980265
-1 索引：datetime 2021-01-27 close 55.5952978
-2 索引 datetime 2021-01-26 close 55.12449815
1 索引：datetime 2019-01-02 close 51.12077805
2 索引 datetime 2019-01-03 close 50.63976172
从 0 开始往前取3天的收盘价：array('d')
从-1开始往前取3天的收盘价：array('d', [57.49896595, 55.12449815, 55.5952978])
从-2开始往前取3天的收盘价：array('d', [58.1744611, 57.49896595, 55.12449815])
line的总长度：506
------------- next 的第1次循环 --------------
当前时点（今日）：datetime 2019-01-02 close 51.12077805
往前推1天（昨日）：datetime 2021-01-28 close 54.91980265
往前推2天（前日） datetime 2021-01-27 close 55.5952978
前日、昨日、今日的收盘价：array('d')
往后推1天（明日）：datetime 2019-01-03 close 50.63976172
往后推2天（明后日） datetime 2019-01-04 close 50.4555427
已处理的数据点：1
line的总长度：506
------------- next 的第2次循环 --------------
当前时点（今日）：datetime 2019-01-03 close 50.63976172
往前推1天（昨日）：datetime 2019-01-02 close 51.12077805
往前推2天（前日） datetime 2021-01-28 close 54.91980265
前日、昨日、今日的收盘价：array('d')
往后推1天（明日）：datetime 2019-01-04 close 50.4555427
往后推2天（明后日） datetime 2019-01-07 close 50.9672622
已处理的数据点：2
line的总长度：506
------------- next 的第3次循环 --------------
当前时点（今日）：datetime 2019-01-04 close 50.4555427
往前推1天（昨日）：datetime 2019-01-03 close 50.63976172
往前推2天（前日） datetime 2019-01-02 close 51.12077805
前日、昨日、今日的收盘价：array('d', [51.12077805, 50.63976172, 50.4555427])
往后推1天（明日）：datetime 2019-01-07 close 50.9672622
往后推2天（明后日） datetime 2019-01-08 close 50.52718343
已处理的数据点：3
line的总长度：506
------------- next 的第4次循环 --------------
```

在涉及到`datetime` 线的操作中，默认存的是数字形式的时间，可以通过一定的方式转换：

+ 可以通过 `bt.num2date()` 方法将其转为“xxxx-xx-xx xx:xx:xx”这种形式；
+ 对 datetime 线进行索引时，`xxx.date(X)` 可以直接以“xxxx-xx-xx xx:xx:xx”的形式返回，X 就是索引位置

除此以外，如果需要获取总的或者已经回测的line长度，可以选择：

+ `self.data0.buflen()` 返回整条线的总长度，固定不变； 
+ 在 `next()` 中调用 `len(self.data0)`，返回的是当前已处理（已回测）的数据长度。

## 3. 指标计算

### 3.1 指标的基本计算和调用

在编写策略时，除了常规的高开低收成交量等行情数据外，还会用到各式各样的指标（变量），比如宏观经济指标、基本面分析指标、技术分析指标、另类数据等等。除了前面描述的直接通过 DataFeeds 模块导入已经计算好的指标，在编写策略时还可以调用 Indicators 指标模块临时计算指标，比如 5 日均线、布林带等 。

回顾基本流程，发现只有在编写策略Strategy 时才会涉及到指标的计算和使用，而且是 Strategy 中的 `__init__() `和 `next()` 方法涉及的最多。因此建议在 `__init__() `中一次性提前计算指标，并在`next()` 会每个交易日依次循环调用已经算好的指标，避免指标的重复计算，提高回测运行速度。下面是最基本的例子：

```python
import backtrader.indicators as btind # 导入策略分析模块

class MyStrategy(bt.Strategy):
  # 先在 __init__ 中提前算好指标
    def __init__(self):
        sma1 = btind.SimpleMovingAverage(self.data)
        ema1 = btind.ExponentialMovingAverage()
        close_over_sma = self.data.close > sma1
        close_over_ema = self.data.close > ema1
        sma_ema_diff = sma1 - ema1
        # 生成交易信号
        buy_sig = bt.And(close_over_sma, close_over_ema, sma_ema_diff > 0)
    # 在 next 中直接调用计算好的指标
    def next(self):
        if buy_sig:
            self.buy()
```

计算指标时，有不同的简写形式，默认是对`self.datas`数据对象中的第一张表格中的第一条`line`（默认第一条line是 close）计算相关指标。调用指标时，也有不同的简写方式， 在`next()` 中调用当前时刻指标值时，可以省略索引`[0] `：`self.sma5[0] `就是`self.sma5`，就是`self.data.close[0]`，也就是`self.data.close`。

下面是一个例子：

```python
class TestStrategy(bt.Strategy):
    
    def __init__(self):
        self.sma5 = btind.SimpleMovingAverage(period=5) # 5日均线
        self.sma10 = btind.SimpleMovingAverage(period=10) # 10日均线
        self.buy_sig = self.sma5 > self.sma10 # 5日均线上穿10日均线
      
    def next(self):
        # 提取当前时间点
        print('datetime', self.datas[0].datetime.date(0))
        # 打印当前值
        print('close', self.data.close[0], self.data.close)
        print('sma5', self.sma5[0], self.sma5)
        print('sma10', self.sma10[0], self.sma10)
        print('buy_sig', self.buy_sig[0], self.buy_sig)
        # 比较收盘价与均线的大小
        if self.data.close > self.sma5:
            print('------收盘价上穿5日均线------')
        if self.data.close[0] > self.sma10:
            print('------收盘价上穿10日均线------')
        if self.buy_sig:
            print('------ buy ------')
        
cerebro = bt.Cerebro()
st_date = datetime.datetime(2019,1,2)
end_date = datetime.datetime(2021,1,28)
datafeed1 = bt.feeds.PandasData(dataname=data1, fromdate=st_date, todate=end_date)
cerebro.adddata(datafeed1, name='600466.SH')
cerebro.addstrategy(TestStrategy)
result = cerebro.run()
```

以下是运行结果：

```txt
datetime 2019-01-24
close 32.38632075 <backtrader.linebuffer.LineBuffer object at 0x7fa1676d0e10>
sma5 32.50969721 <backtrader.indicators.sma.SimpleMovingAverage object at 0x7fa1676c2c18>
sma10 32.596060732 <backtrader.indicators.sma.SimpleMovingAverage object at 0x7fa1676b3048>
buy_sig 0.0 <backtrader.linebuffer.LinesOperation object at 0x7fa1676b3400>
sma10-sma5 0.0863635219999992
datetime 2019-01-25
close 33.06489128 <backtrader.linebuffer.LineBuffer object at 0x7fa1676d0e10>
sma5 32.57138544 <backtrader.indicators.sma.SimpleMovingAverage object at 0x7fa1676c2c18>
sma10 32.589891909 <backtrader.indicators.sma.SimpleMovingAverage object at 0x7fa1676b3048>
buy_sig 0.0 <backtrader.linebuffer.LinesOperation object at 0x7fa1676b3400>
sma10-sma5 0.018506469000001857
------收盘价上穿5日均线------
------收盘价上穿10日均线------
datetime 2019-01-28
close 33.86683827 <backtrader.linebuffer.LineBuffer object at 0x7fa1676d0e10>
sma5 32.855151297999996 <backtrader.indicators.sma.SimpleMovingAverage object at 0x7fa1676c2c18>
sma10 32.725606015 <backtrader.indicators.sma.SimpleMovingAverage object at 0x7fa1676b3048>
buy_sig 1.0 <backtrader.linebuffer.LinesOperation object at 0x7fa1676b3400>
sma10-sma5 -0.1295452829999988
------收盘价上穿5日均线------
------收盘价上穿10日均线------
------ buy ------
```

### 3.2 指标的运算关系和符号

在计算指标或编写策略逻辑时，离不开算术运算、关系运算、逻辑运算、条件运算......，为了更好的适用于Backtrader 框架的语法规则，Backtrader对一些常用的运算符做了优化和改进。在 `__init__` 中事先通过 `bt.And`、`bt.Or`、`bt.If`、`bt.All`、`bt.Any`、`bt.Max`、`bt.Min`、`bt.Sum` 计算返回的结果与在 `next()` 中对当前时点通过常规 python 运算语法返回的结果是一致的。 

经过优化之后，在`__init__` 中调用这些函数是基于整条 line 进行运算，返回的结果也是 lines ，能在 `next ()`中循环调用。以 `bt.Max(self.data, self.sma10, self.sma5)`为例，`bt.Max` 函数会站在3 条 line 的相同时间节点上求出最大值（各个横截面上求最大值），返回的结果就是由各个时间节点上最大值组成的 line ：

```python
class TestStrategy(bt.Strategy):
    
    def __init__(self):
        self.sma5 = btind.SimpleMovingAverage(period=5) # 5日均线
        self.sma10 = btind.SimpleMovingAverage(period=10) # 10日均线
        # bt.And 中所有条件都满足时返回 1；有一个条件不满足就返回 0
        self.And = bt.And(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.Or 中有一个条件满足时就返回 1；所有条件都不满足时返回 0
        self.Or = bt.Or(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.If(a, b, c) 如果满足条件 a，就返回 b，否则返回 c
        self.If = bt.If(self.data>self.sma5,1000, 5000)
        # bt.All,同 bt.And
        self.All = bt.All(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.Any，同 bt.Or
        self.Any = bt.Any(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.Max，返回同一时刻所有指标中的最大值
        self.Max = bt.Max(self.data, self.sma10, self.sma5)
        # bt.Min，返回同一时刻所有指标中的最小值
        self.Min = bt.Min(self.data, self.sma10, self.sma5)
        # bt.Sum，对同一时刻所有指标进行求和
        self.Sum = bt.Sum(self.data, self.sma10, self.sma5)
        # bt.Cmp(a,b), 如果 a>b ，返回 1；否则返回 -1
        self.Cmp = bt.Cmp(self.data, self.sma5)
        
    def next(self):
        print('---------- datetime',self.data.datetime.date(0), '------------------')
        print('close:', self.data[0], 'ma5:', self.sma5[0], 'ma10:', self.sma10[0])
        print('close>ma5',self.data>self.sma5, 'close>ma10',self.data>self.sma10, 'ma5>ma10', self.sma5>self.sma10)
        print('self.And', self.And[0], self.data>self.sma5 and self.data>self.sma10 and self.sma5>self.sma10)
        print('self.Or', self.Or[0], self.data>self.sma5 or self.data>self.sma10 or self.sma5>self.sma10)
        print('self.If', self.If[0], 1000 if self.data>self.sma5 else 5000)
        print('self.All',self.All[0], self.data>self.sma5 and self.data>self.sma10 and self.sma5>self.sma10)
        print('self.Any', self.Any[0], self.data>self.sma5 or self.data>self.sma10 or self.sma5>self.sma10)
        print('self.Max',self.Max[0], max([self.data[0], self.sma10[0], self.sma5[0]]))
        print('self.Min', self.Min[0], min([self.data[0], self.sma10[0], self.sma5[0]]))
        print('self.Sum', self.Sum[0], sum([self.data[0], self.sma10[0], self.sma5[0]]))
        print('self.Cmp', self.Cmp[0], 1 if self.data>self.sma5 else -1)
        
cerebro = bt.Cerebro()
st_date = datetime.datetime(2019,1,2)
ed_date = datetime.datetime(2021,1,28)
datafeed1 = bt.feeds.PandasData(dataname=data1, fromdate=st_date, todate=ed_date)
cerebro.adddata(datafeed1, name='600466.SH')
cerebro.addstrategy(TestStrategy)
result = cerebro.run()
```

以下是输出：

```txt
---------- datetime 2019-01-15 ------------------
close: 33.06489128 ma5: 33.18826774 ma10: 33.101904218
close>ma5 False close>ma10 False ma5>ma10 True
self.And 0.0 False
self.Or 1.0 True
self.If 5000.0 5000
self.All 0.0 False
self.Any 1.0 True
self.Max 33.18826774 33.18826774
self.Min 33.06489128 33.06489128
self.Sum 99.355063238 99.355063238
self.Cmp -1.0 -1
---------- datetime 2019-01-16 ------------------
close: 32.63307367 ma5: 32.966190112 ma10: 33.12657951
close>ma5 False close>ma10 False ma5>ma10 False
self.And 0.0 False
self.Or 0.0 False
self.If 5000.0 5000
self.All 0.0 False
self.Any 0.0 False
self.Max 33.12657951 33.12657951
self.Min 32.63307367 32.63307367
self.Sum 98.72584329200001 98.72584329200001
self.Cmp -1.0 -1
---------- datetime 2019-01-17 ------------------
```

通常情况下，操作的都是相同周期的数据，比如日度行情数据计算返回各类日度指标、周度行情数据计算返回各类周度指标、......，行情数据和指标的周期是一致的，时间也是对齐的。但有时候也会遇到操作不同周期数据的情况，比如拿日度行情与月度指标作比较，日度行情每天都有数据，而月度指标每个月只有一个，2 条数据在时间上是没有对齐的。

这时，可以使用`( ) `语法操作来对齐不同周期的数据，对齐的方向是“大周期向小周期对齐”，可以选择指标对象中的某条 line 进行对齐，也可以对整个指标对象进行对齐。在使用该语法时，要将 `cerebro.run()` 中的 `runonce` 设置为 False，才能实现对齐操作。

这样的操作符本质是线的切片操作`get (ago=-1, size=1)`，然后在更细的时间点上始终取当前最新的指标值。比如对于月度指标，向日度对齐时，月中的那些时间点的数据取得是当前最新的数据（即：月初的指标值），直到下个月月初新的指标值计算出来为止。

下面是一个例子：

```python
# self.data0 是日度行情、self.data1 是月度行情
self.month = btind.xxx(self.data1) # 计算返回的 self.month 指标也是月度的
# 选择指标对象中的第一条 line 进行对齐
self.sellsignal = self.data0.close < self.month.lines[0]()
# 对齐整个指标对象
self.month_ = self.month()
self.signal = self.data0.close < self.month_.lines[0]

cerebro.run(runonce=False)
```

### 3.3 内置、外部或自定义指标

**Indicators 内置指标模块**

Indicators 指标模块提供了 140 多个技术分析指标计算函数，大部分指标与 TA-Lib 库里的指标是一致的，各函数的用途、算法、参数、返回的结果等信息可以查阅[官方文档对于内置技术指标的说明](https://www.backtrader.com/docu/indautoref/)。在文档中，可以根据这样的结构了解每一个函数：

- Alias：函数别名，如果一个指标函数包含多个别名，那这些名称都可以作为这个函数的函数名。

  如简单移动均线函数 MovingAverageSimple，别名有 SMA,SimpleMovingAverage，那调用该函数时可以有 3 种写法`btind.MovingAverageSimple()`、 `btind.SimpleMovingAverage()`或者`btind.SMA()`。

- Formula：技术指标算法说明，如 MACD 函数的算法为

  ```python
  macd = ema(data, me1_period) - ema(data, me2_period)
  signal = ema(macd, signal_period)
  ```

- Lines: 说明函数返回的指标对象中包含哪些 lines，如 MACD 函数返回的指标对象就包含 2 条线：macd 线和 signal 线，可通过 `xxxx.lines.macd`或者`xxxx.macd`调用具体的线，`.lines`有时可以省略。

- Params：指标函数可以设置的参数，如移动均线 `MovingAverageSimple` 包含一个参数：`period (30)`，括号里是该参数的默认值，默认情况下是计算 30 日均值。

- PlotInfo：绘制指标时，支持设置的图形参数，常用绘图参数有以下所示。

  - `plot = True`，是否显示这个指标值，True的显示，False不显示 ；    
  - `subplot = True`，是否把指标显示到另一个窗口，True显示到另一个窗口，False显示在主图； 
  - `plotname = ""`， 显示 line 的名称，默认是 class.__name__； 
  - `plotabove = False`， 指标绘制的位置，False 指标画在主图下方，True 指标画在主图上方； 
  - `plotlinelabels = False`，False 显示的是指标函数的名称，True 显示指标线的名称； 
  - `plotymargin=0.0`，画图的时候距离顶部和底部的距离； 
  - `plotyticks=[ ]`， y 轴刻度范围，取值为空列表时会自动计算；
  - `plothlines=[ ]`，用于绘制水平线；
  - `plotyhlines=[ ]`，用同一个参数，控制 plotyticks 和 plothlines 的取值；
  - `plotforce=False`，如果该绘制的指标没有被绘制，就将 plotforce 设置为 True 进行 强制绘图。
  - `PlotLines`，绘制的曲线样式 。

---

**TA-Lib 技术指标库**

为了更好满足使用习惯，Backtrader 还接入了 TA-Lib 技术指标库，具体信息可以查阅[官方文档对于TA-Lib支持的描述](https://www.backtrader.com/docu/talibindautoref/)，文档中同样对各个函数的输入、输出，以及在 Backtrader 中特有的绘图参数、返回的 lines 属性等信息都做了介绍和说明。

TA-Lib 指标函数的调用形式为 `bt.talib.xxx`：

```python
class TALibStrategy(bt.Strategy):
    def __init__(self):
        # 计算 5 日均线
        bt.talib.SMA(self.data.close, timeperiod=5)
        bt.indicators.SMA(self.data, period=5)
        # 计算布林带
        bt.talib.BBANDS(self.data, timeperiod=25)
        bt.indicators.BollingerBands(self.data, period=25)
```

---

**自定义技术指标**

在 Backtrader 中，如果涉及到自定义操作，一般都是通过继承原始的父类，然后在新的子类里自定义属性，比如之前介绍的自定义数据读取函数 `class My_CSVData (bt.feeds.GenericCSVData)`，就是继承了原始`GenericCSVData`类，自定义新指标也类似，需要继承原始的 bt.Indicator 类，然后在新的子类里构建指标。新的子类里通常可以设置如下属性：

- `lines = ('xxx', 'xxx', 'xxx',)`：定义指标函数返回的 lines 名称，方便后面通过名称调用具体的指标，如 `self.lines.xxx`、`self.l.xxx`、`self.xxx`；
- `params = (('xxx', n),)`：定义参数，方便在子类里全局调用，也方便在使用指标函数时修改参数取值；
- `__init__()` 方法：同策略 Strategy 里的` __init__()`类似，对整条 line 进行运算，运算结果也以整条 line 的形式返回；
- `next()` 方法：同策略 Strategy 里的 `next()`类似，每个 bar 都会运行一次，在 `next()` 中是对数据点进行运算；
- `once()` 方法：这个方法只运行一次，但是需要从头到尾循环计算指标；
- 指标绘图相关属性的设置，例如`plotinfo = dict()` 通过字典形式修改绘图参数；`plotlines = dict()` 设置曲线样式 等等

```python
class DummyInd(bt.Indicator):
    # 将计算的指标命名为 'dummyline'，后面调用这根 line 的方式有：
    # self.lines.dummyline ↔ self.l.dummyline ↔ self.dummyline
    lines = ('dummyline',)
    # 定义参数，后面调用这个参数的方式有：
    # self.params.xxx ↔ self.p.xxx
    params = (('value', 5),)
    
    def __init__(self):
        self.l.dummyline = bt.Max(0.0, self.p.value)
    
    def next(self):
        self.l.dummyline[0] = max(0.0, self.p.value)
   
    def once(self, start, end):
        dummy_array = self.l.dummyline.array
        for i in xrange(start, end):
            dummy_array[i] = max(0.0, self.p.value)
    plotinfo = dict(...)
    plotlines = dict(...)
```

通过这个例子，可以比较在 `__init__()`、`next()`、`once()` 中计算指标的区别：

- `__init__()`中是对 line 进行运算，最终也以 line 的形式返回，所以运算结果直接赋值给了 `self.l.dummyline`；
- `next()` 中是对当前时刻的数据点进行运算（用了常规的 `max()` 函数），返回的运算结果也只是当前时刻的值，所以是将结果赋值给 dummyline 的当前时刻`self.l.dummyline[0]`， 然后依次在每个 bar 都运算一次；
- `once()` 也只运行一次，适合于不直接对指标 line 进行操作，而单纯的 python 运算和赋值的习惯场景；
- 自定义指标时，建议首选 `__init__()`，因为其能自动实现 `next()` 和 `once()` 的功能。


## 4. 交易条件

### 4.1 Broker 中的交易条件

回测过程中涉及的交易条件设置，最常见的有初始资金、交易税费、滑点、期货保证金比率等，有时还会对成交量做限制、对涨跌幅做限制、对订单生成和执行时机做限制，上述大部分交易条件都可以通过 Broker 来管理：

+ 可以通过设置 `backtrader.brokers.BackBroker() `类中的参数，生成新的 broker 实例，并将新的实例赋值给 `cerebro.broker`进行使用；
+ 通过调用 broker 中的 `set_xxx`方法来修改条件，还可通过 `get_xxx`方法查看当前设置的条件取值。

**资金管理**方面，Broker 默认的初始资金 cash 是 10000，可通过 `cash` 参数、`set_cash() `方法修改初始资金，此外还提供了`add_cash() `方法增加或减少资金。Broker 会检查提交的订单现金需求与当前现金是否匹配，cash 也会随着每次交易进行迭代更新用以匹配当前头寸。

```python
# 初始化时
cerebro.broker.set_cash(100000000.0) # 设置初始资金
cerebro.broker.get_cash() # 获取当前可用资金

# 简写形式
cerebro.broker.setcash(100000000.0) # 设置初始资金
cerebro.broker.getcash() # 获取当前可用资金

# 在 Strategy 中添加资金或获取当前资金
self.broker.add_cash(10000) # 正数表示增加资金
self.broker.add_cash(-10000) # 负数表示减少资金
self.broker.getcash() # 获取当前可用资金
```

**持仓查询**方面，Broker 在每次交易后更新 cash 外，还会同时更新当前总资产 value 和当前持仓 position，通常在 Strategy 中进行持仓查询操作。

当前总资产 = 当前可用资金 + 当前持仓总市值，而当前持仓总市值为当前持仓中所有标的各自持仓市值之和。在计算当前可用资金时，除了考虑扣除购买标的时的费用外，还需要考虑扣除交易费用 。

```python
class TestStrategy(bt.Strategy):
    def next(self):
        print('当前可用资金', self.broker.getcash())
        print('当前总资产', self.broker.getvalue())
        print('当前持仓量', self.broker.getposition(self.data).size)
        print('当前持仓成本', self.broker.getposition(self.data).price)
        # 也可以直接获取持仓
        print('当前持仓量', self.getposition(self.data).size)
        print('当前持仓成本', self.getposition(self.data).price)
        # 注：getposition() 需要指定具体的标的数据集
```

输出结果如下：

```txt
2019-01-16, Close, 32.6331
2019-01-16, 当前可用资金, 1000000.00
2019-01-16, 当前总资产, 1000000.00
2019-01-16, 当前持仓数量, 0.00
2019-01-16, 当前持仓成本, 0.00
2019-01-17, BUY EXECUTED, ref:63，Price: 32.64, Cost: 3263.63, Comm 0.98, Size: 100.00, Stock: 600466.SH
2019-01-17, Close, 32.0779
2019-01-17, 当前可用资金, 996735.39
2019-01-17, 当前总资产, 999943.18
2019-01-17, 当前持仓数量, 100.00
2019-01-17, 当前持仓成本, 32.64
```

### 4.2 滑点管理

在实际交易中，由于市场波动、网络延迟等原因，交易指令中指定的交易价格与实际成交价格会存在较大差别，出现滑点。回测估算时，可以在买入时，在指定价格的基础上提高实际买入价格；卖出时，在指定价格的基础上，降低实际卖出价格。

为了让回测结果更真实，可以通过 brokers 设置滑点，滑点的类型有 2 种：

+ 百分比滑点：假设设置了 n% 的滑点，如果指定的买入价为 x，那实际成交时的买入价会提高至 x * (1+ n%) ；同理，若指定的卖出价为 x，那实际成交时的卖出价会降低至 x * (1- n%)。如果和后者同时设置，百分比滑点优先级高于后者。

  ```python
  # 方式1：通过 BackBroker 类中的 slip_perc 参数设置百分比滑点
  cerebro.broker = bt.brokers.BackBroker(slip_perc=0.0001)
  # 方式2：通过调用 brokers 的 set_slippage_perc 方法设置百分比滑点
  cerebro.broker.set_slippage_perc(perc=0.0001)
  ```

+ 固定滑点：假设设置了大小为 n 的固定滑点，如果指定的买入价为 x，那实际成交时的买入价会提高至 x + n ；同理，若指定的卖出价为 x，那实际成交时的卖出价会降低至 x - n。

  ```python
  # 方式1：通过 BackBroker 类中的 slip_fixed 参数设置固定滑点
  cerebro.broker = bt.brokers.BackBroker(slip_fixed=0.001)
  # 方式2：通过调用 brokers 的 set_slippage_fixed 方法设置固定滑点
  cerebro.broker.set_slippage_fixed(fixed=0.001)
  ```

除了用于设置滑点的 `slip_perc` 和 `slip_fixed` 参数外，broker 还提供了其他参数用于处理价格出现滑点后的极端情况：

- `slip_open`：是否对开盘价做滑点处理，该参数在 `BackBroker()`类中默认为 False，在 `set_slippage_perc` 和`set_slippage_fixed `方法中默认为 True；

- `slip_match`：是否将滑点处理后的新成交价与成交当天的价格区间 low ~ high 做匹配，如果为 True，则根据新成交价重新匹配调整价格区间，确保订单能被执行；如果为 False，则不会与价格区间做匹配，订单不会执行，但会在下一日执行一个空订单；默认取值为 True；

- `slip_out`：如果新成交价高于最高价或低于最高价，是否以超出的价格成交，如果为 True，则允许以超出的价格成交；如果为 Fasle，实际成交价将被限制在价格区间内 low ~ high；默认取值为 False；

- `slip_limit`：是否对限价单执行滑点，如果为 True，即使 `slip_match` 为Fasle，也会对价格做匹配，确保订单被执行；如果为 Fasle，则不做价格匹配；默认取值为 True。

以下通过一些例子把滑点固定在0.35，对上述参数取不同的值，研究标的 600466.SH 在 2019-01-17 的成交情况：

+ 情况一：由于 `slip_open=False`，不会对开盘价做滑点处理，所以仍然以原始开盘价 32.63307367 成交。

  ```python
  set_slippage_fixed(fixed=0.35,
                     slip_open=False,
                     slip_match=True,
                     slip_out=False)
  ```

+ 情况2：滑点调整的新成交价为 32.63307367+0.35 = 32.98307367，超出了当天最高价 32.94151482。由于允许做价格匹配 ～`slip_match=True`, 但不以超出价格区间的价格执行 `slip_out=False`，最终以最高价 32.9415 成交。

  ```python
  set_slippage_fixed(fixed=0.35,
                     slip_open=True,
                     slip_match=True,
                     slip_out=False)
  ```

+ 情况3：滑点调整的新成交价为 32.63307367+0.35 = 32.98307367，超出了当天最高价 32.94151482。由于不进行价格匹配 `slip_match=False`，新成交价超出价格区间无法成交，2019-01-17 这一天订单不会执行，但会在下一日 2019-01-18 执行一个空订单，就是条件满足也不会补充成交。

  ```python
  set_slippage_fixed(fixed=0.35,
                   slip_open=True,
                   slip_match=False,
                   slip_out=True)
  ```

### 4.2 交易税费管理

交易时是否考虑交易费用对回测的结果影响很大，所以在回测是通常会设置交易税费，不同标的的费用收取规则也各不相同。

- 股票：目前 A 股的交易费用分为 2 部分：佣金和印花税，其中佣金双边征收，不同证券公司收取的佣金各不相同，一般在 0.02%-0.03% 左右，单笔佣金不少于 5 元；印花税只在卖出时收取，税率为 0.1%。

- 期货：期货交易费用包括交易所收取手续费和期货公司收取佣金 2 部分，交易所手续费较为固定，不同期货公司佣金不一致，而且不同期货品种的收取方式不相同，有的按照固定费用收取，有的按成交金额的固定百分比收取：合约现价x合约乘数x手续费费率。除了交易费用外，期货交易时还需上交一定比例的保证金 。

Backtrader 也提供了多种交易费设置方式，既可以简单的通过参数进行设置，也可以结合交易条件自定义费用函数：

- 根据交易品种的不同，Backtrader 将交易费用分为 股票 Stock-like 模式和期货 Futures-like 种模式；

- 根据计算方式的不同，Backtrader 将交易费用分为 PERC 百分比费用模式 和 FIXED 固定费用模式 ；

 Stock-like 模式与 PERC 百分比费用模式对应，期货 Futures-like 与 FIXED 固定费用模式对应。

- 在设置交易费用时，最常涉及如下 3 个参数：

- - commission：手续费 / 佣金；
  - mult：乘数；
  - margin：保证金 / 保证金比率 。
  - 双边征收：买入和卖出操作都要收取相同的交易费用 。

---

**如果通过 BackBroker() 设置**，BackBroker 中有一个 commission 参数，用来全局设置交易手续费。如果是股票交易，可以简单的通过该方式设置交易佣金，但该方式无法满足期货交易费用的各项设置。

```python
# 设置 0.0002 = 0.02% 的手续费
cerebro.broker = bt.brokers.BackBroker(commission= 0.0002)
```

**如果通过 setcommission() 设置**，可以完整又方便的设置交易费用。

```python
cerebro.broker.setcommission(
    # 交易手续费，根据margin取值情况区分是百分比手续费还是固定手续费
    commission=0.0,
    # 期货保证金，决定着交易费用的类型,只有在stocklike=False时起作用
    margin=None,
    # 乘数，盈亏会按该乘数进行放大
    mult=1.0, 
    # 交易费用计算方式，取值有：
    # 1.CommInfoBase.COMM_PERC 百分比费用
    # 2.CommInfoBase.COMM_FIXED 固定费用
    # 3.None 根据 margin 取值来确定类型
    commtype=None,
    # 当交易费用处于百分比模式下时，commission 是否为 % 形式
    # True，表示不以 % 为单位，0.XX 形式；False，表示以 % 为单位，XX% 形式 
    percabs=True, 
    # 是否为股票模式，该模式通常由margin和commtype参数决定
    # margin=None或COMM_PERC模式时，就会stocklike=True，对应股票手续费；
    # margin设置了取值或COMM_FIXED模式时,就会stocklike=False，对应期货手续费
    stocklike=False, 
    # 计算持有的空头头寸的年化利息
    # days * price * abs(size) * (interest / 365)
    interest=0.0, 
    # 计算持有的多头头寸的年化利息
    interest_long=False, 
    # 杠杆比率，交易时按该杠杆调整所需现金
    leverage=1.0, 
    # 自动计算保证金
    # 如果False,则通过margin参数确定保证金
    # 如果automargin<0,通过mult*price确定保证金
    # 如果automargin>0,如果automargin*price确定保证金
    automargin=False, 
    # 交易费用设置作用的数据集(也就是作用的标的)
    # 如果取值为None，则默认作用于所有数据集(也就是作用于所有assets)
    name=None)
```

不难发现，margin 、commtype、stocklike 存在 2 种默认的配置规则：股票百分比费用、期货固定费用。

- 第 1 条规则：未设置 margin（即 margin 为 0 / None / False）→ commtype 会指向 COMM_PERC 百分比费用 → 底层的 _stocklike 属性会设置为 True → 对应的是“股票百分比费用”。所以如果想为股票设置交易费用，就令 `margin = 0 / None / False`，或者令 `stocklike=True`；

- 第 2 条规则：为 margin 设置了取值 →  commtype 会指向 COMM_FIXED 固定费用 → 底层的 _stocklike 属性会设置为 False → 对应的是“期货固定费用”，因为只有期货才会涉及保证金。所以如果想为期货设置交易费用，就需要设置 margin，此外还需令 `stocklike=True`，margin 参数才会起作用 。

**如果通过 addcommissioninfo() 设置**，可以更加灵活的设置交易费用。可以在继承 CommInfoBase 基础类的基础上自定义交易费用子类 ，然后通过 `addcommissioninfo()` 方法将实例添加进 broker。

```python
# 在继承 CommInfoBase 基础类的基础上自定义交易费用
class MyCommission(bt.CommInfoBase):
    # 对应 setcommission 中介绍的那些参数，也可以增添新的全局参数
    params = ((xxx, xxx),)
    # 自定义交易费用计算方式
    def _getcommission(self, size, price, pseudoexec):
        pass
    # 自定义佣金计算方式
    def get_margin(self，price):
        pass
    ...
    
# 实例化
mycomm = MyCommission(...)
cerebro = bt.Cerebro()
# 添加进 broker 
cerebro.broker.addcommissioninfo(mycomm, name='xxx') # name 用于指定该交易费用函数适用的标的
```

总而言之，Backtrader 中与交易费用相关的设置都是由 CommInfoBase 类管理的，除了上面介绍的 `setcommission()` 方法中的参数就是 CommInfoBase 类中 params 属性里包含的参数，此外还内置许多 getxxx 方法返回交易产生的指标：

+ 计算成交量 `getsize(price, cash)` ；
+ 计算持仓市值 `getvalue(position, price)`；
+ 计算佣金`getcommission(size, price)` 或 `_getcommission(self, size, price, pseudoexec)`；
+ 计算保证金 `get_margin(price)` 。

其中自定义时最常涉及的就是上面案例中显示的 _getcommission 和 get_margin。

**如果想自定义交易费用**，除了股票百分比费用、期货固定费用，Backtrader还提供了“期货百分比费用”的自定义子类：

```python
# 自定义期货百分比费用
class CommInfo_Fut_Perc_Mult(bt.CommInfoBase):
    params = (
      ('stocklike', False), # 指定为期货模式
      ('commtype', bt.CommInfoBase.COMM_PERC), # 使用百分比费用
      ('percabs', False), # commission 以 % 为单位
    )

    def _getcommission(self, size, price, pseudoexec):
        # 计算交易费用
        return (abs(size) * price) * (self.p.commission/100) * self.p.mult
    # pseudoexec 用于提示当前是否在真实统计交易费用
    # 如果只是试算费用，pseudoexec=False
    # 如果是真实的统计费用，pseudoexec=True

comminfo = CommInfo_Fut_Perc_Mult(
    commission=0.1, # 0.1%
    mult=10,
    margin=2000) # 实例化 
cerebro.broker.addcommissioninfo(comminfo)

# 上述自定义函数，也可以通过 setcommission 来实现
cerebro.broker.setcommission(commission=0.1, #0.1%
                             mult=10,
                             margin=2000,
                             percabs=False,
                             commtype=bt.CommInfoBase.COMM_PERC,
                             stocklike=False)
```

下面是考虑佣金和印花税的股票百分比费用：

```python
class StockCommission(bt.CommInfoBase):
    params = (
      ('stocklike', True), # 指定为期货模式
      ('commtype', bt.CommInfoBase.COMM_PERC), # 使用百分比费用模式
      ('percabs', True), # commission 不以 % 为单位
      ('stamp_duty', 0.001),) # 印花税默认为 0.1%
    
    # 自定义费用计算公式
  def _getcommission(self, size, price, pseudoexec):
        if size > 0: # 买入时，只考虑佣金
            return abs(size) * price * self.p.commission 
        elif size < 0: # 卖出时，同时考虑佣金和印花税
    return abs(size) * price * (self.p.commission + self.p.stamp_duty) 
        else:
            return 0
```

### 4.3 成交量限制管理

默认情况下，Broker 在撮合成交订单时，不会将订单上的购买数量与成交当天 bar 的总成交量 volume 进行对比，即使购买数量超出了当天该标的的总成交量，也会按购买数量全部撮合成交，显然这种“无限的流动性”是不现实的，这种 “不考虑成交量，默认全部成交” 的交易模式，也会使得回测结果与真实结果产生较大偏差。如果想要修改这种默认模式，可以通过 Backtrader 中的 fillers 模块来限制实际成交量，fillers 会告诉 Broker 在各个成交时间点应该成交多少量，一共有 3 种形式：

+ **bt.broker.fillers.FixedSize(size)：** 通过 `FixedSize()` 方法设置最大的固定成交量：size，规则如下：

  - 订单实际成交量的确定规则：取（size、订单执行那天的 volume 、订单中要求的成交数量）中的最小者；

  - 订单执行那天，如果订单中要求的成交数量无法全部满足，则只成交部分数量。

  ```python
  # 通过 BackBroker() 类直接设置
  cerebro = Cerebro()
  filler = bt.broker.fillers.FixedSize(size=xxx)
  newbroker = bt.broker.BrokerBack(filler=filler)
  cerebro.broker = newbroker
  
  # 通过 set_filler 方法设置
  cerebro = Cerebro()
  cerebro.broker.set_filler(bt.broker.fillers.FixedSize(size=xxx))
  ```

+ **bt.broker.fillers.FixedBarPerc(perc)：**通过 `FixedBarPerc(perc)` ，将订单执行当天 bar 的总成交量 volume 的 `perc` % 设置为最大的固定成交量，该模式的成交量限制规则如下：

  + 订单实际成交量的确定规则：取（volume * perc /100、订单中要求的成交数量）的最小者；
  + 订单执行那天，如果订单中要求的成交数量无法全部满足，则只成交部分数量。

  ```python
  # 通过 BackBroker() 类直接设置
  cerebro = Cerebro()
  filler = bt.broker.fillers.FixedBarPerc(perc=xxx)
  newbroker = bt.broker.BrokerBack(filler=filler)
  cerebro.broker = newbroker
  
  # 通过 set_filler 方法设置
  cerebro = Cerebro()
  cerebro.broker.set_filler(bt.broker.fillers.FixedBarPerc(perc=xxx))
  # perc 以 % 为单位，取值范围为[0.0,100.0]
  ```

+ **bt.broker.fillers.BarPointPerc(minmov=0.01，perc=100.0)：**通过`BarPointPerc()`，在考虑价格区间的基础上确定成交量，在订单执行当天，成交量确定规则为：

  - 将当天bar 的价格区间 low ~ high 进行均匀划分，得到划分的份数`part = (high -low +minmov) // minmov` （向下取整）；
  - 再对当天 bar 的总成交量 volume 也划分成相同的份数 part ，得到每份的平均成交量`volume_per = volume // part `；

  - 最终，`volume_per * (perc / 100)`就是允许的最大成交量，实际成交时，对比订单中要求的成交量得到最终实际成交量`min ( volume_per * （perc / 100）, 订单中要求的成交数量 )`。

  ```python
  # 通过 BackBroker() 类直接设置
  cerebro = Cerebro()
  filler = bt.broker.fillers.BarPointPerc(minmov=0.01，perc=100.0)
  newbroker = bt.broker.BrokerBack(filler=filler)
  cerebro.broker = newbroker
  
  # 通过 set_filler 方法设置
  cerebro = Cerebro()
  cerebro.broker.set_filler(bt.broker.fillers.BarPointPerc(minmov=0.01，perc=100.0))
  # perc 以 % 为单位，取值范围为[0.0,100.0]
  ```

### 4.4 交易时机管理

对于交易订单生成和执行时间，Backtrader 默认是 “当日收盘后下单，次日以开盘价成交”，这种模式在回测过程中能有效避免使用未来数据。但对于一些特殊的交易场景，比如 “all_in” 情况下，当日所下订单中的数量是用当日收盘价计算的（总资金 / 当日收盘价），次日以开盘价执行订单时，如果开盘价比昨天的收盘价提高了，就会出现可用资金不足的情况。为了应对一些特殊交易场景，Backtrader 还提供了一些 cheating 式的交易时机模式：Cheat-On-Open 和 Cheat-On-Close。

**Cheat-On-Open：**“当日下单，当日以开盘价成交”模式，在该模式下，Strategy 中的交易逻辑不再写在 `next()` 方法里，而是写在特定的 `next_open()`、`nextstart_open()` 、`prenext_open()` 函数中，具体设置可参考如下案例：

- 方式1：`bt.Cerebro(cheat_on_open=True)`；
- 方式2：`cerebro.broker.set_coo(True)`；
- 方式3：`BackBroker(coo=True)`。

```python
class TestStrategy(bt.Strategy):
    ......
    def next_open(self):
        # 取消之前未执行的订单
        if self.order: 
            self.cancel(self.order) 
        # 检查是否有持仓
        if not self.position: 
            # 10日均线上穿5日均线，买入
            if self.crossover > 0: 
                print('{} Send Buy, open {}'.format(self.data.datetime.date(),self.data.open[0]))
                self.order = self.buy(size=100) # 以下一日开盘价买入100股
        # # 10日均线下穿5日均线，卖出
        elif self.crossover < 0: 
            self.order = self.close() # 平仓，以下一日开盘价卖出
    ...... 

# 实例化大脑
cerebro= bt.Cerebro(cheat_on_open=True)
.......
# 当日下单，当日开盘价成交
# cerebro.broker.set_coo(True)
```

部分运行结果如下：

```txt
# 部分运行结果
2019-01-17 Send Buy, open 32.63307367
2019-01-17 Buy Executed at price 32.63307367
2019-01-29 Send Sell, open 33.928526500000004
2019-01-29 Sell Executed at price 33.928526500000004
2019-02-22 Send Buy, open 34.91553818
2019-02-22 Buy Executed at price 34.91553818
2019-02-27 Send Sell, open 37.50644384
2019-02-27 Sell Executed at price 37.50644384
2019-03-15 Send Buy, open 41.20773764
2019-03-15 Buy Executed at price 41.20773764
2019-03-18 Send Sell, open 44.10708445
2019-03-18 Sell Executed at price 44.10708445
```

与常规模式返回的结果进行对可知：

- 原本 2019-01-16 生成的下单指令，被延迟到了 2019-01-17 日才发出；

- 2019-01-17 发出的订单，在 2019-01-17 当日就以 开盘价 执行成交了。

**Cheat-On-Close：**“当日下单，当日以收盘价成交”模式，在该模式下，Strategy 中的交易逻辑仍写在 `next()` 中，具体设置如下：

- 方式1：`cerebro.broker.set_coc(True)`；

- 方式2：`BackBroker(coc=True)`。

```python
class TestStrategy(bt.Strategy):
    ......
    def next(self):
        # 取消之前未执行的订单
        if self.order: 
            self.cancel(self.order) 
        # 检查是否有持仓
        if not self.position: 
            # 10日均线上穿5日均线，买入
            if self.crossover > 0: 
                print('{} Send Buy, open {}'.format(self.data.datetime.date(),self.data.open[0]))
                self.order = self.buy(size=100) # 以下一日开盘价买入100股
        # # 10日均线下穿5日均线，卖出
        elif self.crossover < 0: 
            self.order = self.close() # 平仓，以下一日开盘价卖出
    ...... 

# 实例化大脑
cerebro= bt.Cerebro()
.......
# 当日下单，当日收盘价成交
cerebro.broker.set_coc(True)
```

部分结果如下：

```txt
# 部分运行结果
2019-01-16 Send Buy, close 32.63307367
2019-01-16 Buy Executed at price 32.63307367
2019-01-28 Send Sell, close 33.86683827
2019-01-28 Sell Executed at price 33.86683827
2019-02-21 Send Buy, close 34.85384995
2019-02-21 Buy Executed at price 34.85384995
2019-02-26 Send Sell, close 37.75319676
2019-02-26 Sell Executed at price 37.75319676
2019-03-14 Send Buy, close 41.20773764
2019-03-14 Buy Executed at price 41.20773764
2019-03-15 Send Sell, close 42.62656693
2019-03-15 Sell Executed at price 42.626566929999996
```

与常规模式返回的结果进行对可知：

- 2019-01-16 生成的下单指令，当天就被发送，而且当天就以 收盘价 执行了；并未在指令发出的下一日执行。

## 5. 交易执行

### 5.1 Order 中的交易订单类型

不同的订单类型，下单时需要配置的参数会存在区别，Broker 能够识别和处理种订单类型，满足不同的交易需求：

+ **Order.Market**

  + 市价单，以当时市场价格成交的订单，不需要自己设定价格。市价单能被快速达成交易，防止踏空，尽快止损/止盈；

  - 按下一个 Bar （即生成订单的那个交易日的下一个交易日）的开盘价来执行成交；
  - 例如：`self.buy(exectype=bt.Order.Market) `。

+ **Order.Close**

  - 和 Order.Market 类似，也是市价单，只是成交价格不一样；

  - 按下一个 Bar 的收盘价来执行成交；

  - 例如：`self.buy(exectype=bt.Order.Close) `。

+ **Order.Limit**

  - 限价单，需要指定成交价格，只有达到指定价格（limit Price）或有更好价格时才会执行，即以指定价或低于指点价买入，以指点价或更高指定价卖出；

  - 在订单生成后，会通过比较 limit Price 与之后 Bar 的 open\high\low\close 行情数据来判断订单是否成交。如果下一个 Bar 的 open 触及到指定价格 limit Price，就以 open 价成交，订单在这个 Bar 的开始阶段就被执行完成；如果下一个 Bar 的 open 未触及到指定价格 limit Price，但是 limit Price 位于这个 bar 的价格区间内 （即 low ~ high），就以 limit Price 成交；
  - 例如：`self.buy(exectype=bt.Order.Limit, price=price, valid=valid) `。

+ **Order.Stop**

  - 止损单，需要指定止损价格（Stop Price），一旦股价突破止损价格，将会以市价单的方式成交；

  - 在订单生成后，也是通过比较 Stop Price 与之后 Bar 的 open\high\low\close 行情数据来判断订单是否成交。如果下一个 Bar 的 open 触及到指定价格 limit Price，就以 open 价成交；如果下一个 Bar 的 open 未触及到指定价格 Stop Price，但是 Stop Price 位于这个 bar 的价格区间内 （即 low ~ high），就以 Stop Price 成交；
  - 例如：`self.buy(exectype=bt.Order.Stop, price=price, valid=valid) `。

+ **Order.StopLimit**
  - 止损限价单，需要指定止损价格（Stop price）和限价（Limit Price），一旦股价达到止损价格，将以限价单的方式下单；
  - 在下一个 Bar，按 Order.Stop 的逻辑触发订单，然后以 Order.Limit 的逻辑执行订单；
  - 例如：`self.buy(exectype=bt.Order.StopLimit, price=price, valid=valid, plimit=plimit)`。

+ **Order.StopTrail**

  - 跟踪止损订单，是一种止损价格会自动调整的止损单，调整范围通过设置止损价格和市场价格之间的差价来确定。差价即可以用金额 trailamount 表示，也可以用市价的百分比 trailpercent  表示；

  - 如果是通过 buy 下达了买入指令，就会“卖出”一个跟踪止损单，在市场价格上升时，止损价格会随之上升；若股价触及止损价格时，会以市价单的形式执行订单；若市场价格下降或保持不变，止损价格会保持不变；

  - 如果是通过 sell 下达卖出指令，就会“买入”一个跟踪止损单，在市场价格下降时，止损价格会随之下降；若股价触及止损价格时，会以市价单的形式执行订单；但是当市场价格上升时，止损价格会保持不变；

  - 例如：`self.buy(exectype=bt.Order.StopTrail, price=xxx, trailamount=xxx)`。

+ **Order.StopTrailLimit**

  - 跟踪止损限价单，是一种止损价格会自动调整的止损限价单，订单中的限价 Limit Price 不会发生变动，止损价会发生变动，变动逻辑与上面介绍的跟踪止损订单一致；

  - 例：`self.buy(exectype=bt.Order.StopTrailLimit, plimit=xxx, trailamount=xxx) `。

虽然订单的类型多种多样，但考虑到国内交易所的现状，回测中使用比较多的还是市价单和限价单。

### 5.2 Strategy 中的交易函数

在 Strategy 的策略逻辑中，一旦满足交易条件，就会通过交易函数下达交易指令，Strategy 提供的交易函数主要分为 2 类：常规下单函数、目标下单函数，常规下单函数需要自行确定买卖方向，而目标下单函数会根据交易目标自动确定买卖方向。除此之外，如果多个订单之间有关联，还支持生成一篮子关联订单和取消关联订单。

**常规下单函数**

Strategy 中的常规下单函数主要有 3 个：买入 `buy()` 、卖出 `sell()`、平仓 `close()` ，它们的调用方式非常简单，大家也经常在案例中看到，交易函数会返回订单 Order 实例，通常会赋值给对象self.order ：

```python
class TestStrategy(bt.Strategy):
    def next(self):
        self.order = self.buy( ...) # 买入、做多 long
        self.order = self.sell(...) # 卖出、做空 short
        self.order = self.close(...) # 平仓 cover
```

调用的 buy、sell、close 方法中支持设置的参数有：

- **data（默认: None）：**用于指定给哪个数据集（即哪个证券）创建订单，默认为 None，表示给第 1 个数据集（self.datas[0] 、self.data0 对应的证券）创建订单。

- **size（默认: None）：**订单委托数量（正数），默认为 None，表示会自动通过 getsizer 获取 sizer 。

- **price（默认: None）：**订单委托价， None 表示不指定具体的委托价，而是由市场决定最终的成交价，适用于市价单；对于限价单、止损单和止损限价单，price 就是触发订单执行的那个价格 。

- **plimit（默认: None）：**仅适用于 StopLimit 订单，用于指定 StopLimit 订单的限价 Limit Price 为多少。

- **exectype （默认: None）：**执行的订单类型，None 表示按市价单执行，可选的类型有：

- - Order.Market  市价单，回测时将以下一个 bar 的开盘价执行的市价单 ；
  - Order.Close  市价单，回测时将以下一个 bar 的收盘价执行的市价单；
  - Order.Limit  限价单；
  -  Order.Stop  止损单；
  - Order.StopLimit  止损现价单；
  - Order.StopTrail  跟踪止损订单；
  - Order.StopTrailLimit  跟踪止损限价单。

- **valid（默认: None）：**订单有效期，可选取值有：

- - None 表示订单在完成成交或被撤销之前一直都有效（aka Good till cancel or match）; 
  - datetime实例、date 实例、数值形式的日期，表示订单在设置的 date 之前有效，date 之后会被撤销（aka good till date）；
  - Order.DAY 、0 、imedelta()，表示订单当日有效，未成交的订单将在当日收盘后被自动撤销（aka day order）。

- **tradeid（默认: None）：**当同一资产出现重复交易的时候，通知订单状态更改时，tradeid 会被传递给 Strategy。

- **\*\*kwargs：**通过传入其他参数，生成特定类型的订单 。

**目标下单函数**

目标下单函数包括按目标数量下单、按目标金额下单、按目标百分比下单，这些下单函数会根据设置的目标来选择买卖方向：

```python
class TestStrategy(bt.Strategy):
   def next(self):
      # 按目标数量下单
      self.order = self.order_target_size(target=size)
      # 按目标金额下单
      self.order = self.order_target_value(target=value)
      # 按目标百分比下单
      self.order = self.order_target_percent(target=percent)
```

- **order_target_size：**按目标数量下单，按“多退少补”的原则，让证券的持仓数量等于设定的目标数量 target ：如果目标数量 target 大于当前持仓数量，则会发出买入订单，补足持仓量；如果目标数量 target 小于当前持仓数量，则会发出卖出订单，减少持仓量。
- **order_target_value：**按目标金额下单，通过比较目标金额与当前持仓额和持仓方向，确定最终买卖买卖方向：（持仓量默认使用当前 Bar 的 close 进行计算，然后以下一根 bar 的开盘价进行交易）

  - 如果当前持有的是空单（size<0）：若目标金额 target > 当前持仓额 -> 卖出；若目标金额 target < 当前持仓额 -> 买入。
  - 如果当前无持仓或持有多单（size>=0）：若目标金额 target > 当前持仓额 -> 买入；若目标金额 target < 当前持仓额 -> 卖出。
- 如果当前无持仓或持有多单（size>=0）：若目标金额 target > 当前持仓额 -> 买入；若目标金额 target < 当前持仓额 -> 卖出。
- **order_target_percent：**按目标百分比下单，订单生成逻辑同 order_target_value，目标金额 = 目标百分比 * 当前账户的总资产。

**取消订单**

交易函数用于生成订单，返回 Order 对象，如果想要取消生成的订单，就可以通过 cancel() 方法来取消：

- 通过 cancel() 来取消订单 ：`self.cancel(order)`；

- 通过 Broker 来取消订单 ：`self.broker.cancel(order) `。

**订单组合**

注：这里的订单组合并不是同时对多个标的进行交易，而是对某一笔交易同时发出多个指令，以满足在不同市场情况时触发对应的指令。

前面介绍的交易函数生成的都是单个订单，而且订单之间并没有什么联系，而此处介绍的交易函数 `buy_bracket()` 和 `sell_bracket()` 会一次性生成 3 个自定义类型的订单：主订单 main order、针对主订单的止损单 stop order、针对主订单的止盈单 limit order 。

+ **buy_bracket()：**用于long side 的交易场景，买入证券后，在价格下跌时，希望通过止损单卖出证券，限制损失；在价格上升时，希望通过限价单卖出证券，及时获利，通过 `buy_bracket()` 可以同时提交上述 3 个订单，而无需繁琐的调用 3 次常规交易函数。以下为参数：

  - data=None，默认是对 data0 数据集对应的证券标的进行交易；


  - 主订单：为买入单，默认为 Order.Limit  限价单，可通过参数 price 设定成交价，也可通过参数 plimit 设置指定价 limit；主订单通常设置为 Order.Limit  限价单 或 Order.StopLimit 止损限价单；


  - 止损单：为卖出单，用于及时止损，默认为 Order.Stop 止损单，可通过参数 stopprice 设置止损价，参数 stopargs 中还可设置止损单相关的其他参数；


  - 止盈单：为卖出单，用于及时止盈，默认为 Order.Limit 限价单，可通过参数 limitprice 设置指定价格，参数 limitargs 中还可设置限价单相关的其他参数。

```python
# 函数可用参数
buy_bracket(# 主订单的参数
            data=None, size=None, price=None,
            plimit=None,exectype=bt.Order.Limit, 
            valid=None, tradeid=0,
            trailamount=None, trailpercent=None, 
            oargs={},
            # 止损单的参数
            stopprice=None, stopexec=bt.Order.Stop, stopargs={},
            # 止盈单的参数
            limitprice=None, limitexec=bt.Order.Limit, limitargs={},
            **kwargs):......

# 调用示例
brackets = self.buy_bracket(price=13.50,
                            limitprice=14.00，
                            stopprice=13.00)
# 主订单以 13.5 的价格买入 self.data0 数据集对应的标的
# 当价格超过 14.00 时，会触发止盈单，卖出标的
# 当价格跌破 13.00 时，会触发止损单，卖出标的
```

+ **sell_bracket()：**用于short side 的交易场景，卖出证券做空后，在价格上升时，希望通过止损单买入证券，限制损失；在价格下降时，希望通过限价单买入证券，及时获利，`sell_bracket()` 也是一次同时提交上述 3 个订单 。
  + sell_bracket 的可用参数与 buy_bracket 的类似，只是 sell_bracket 中的主订单为 卖出单、止损单和止盈单为 买入单。

```python
# 函数可用参数
sell_bracket(# 主订单设置
             data=None,size=None, price=None, plimit=None, 
             exectype=bt.Order.Limit, valid=None, tradeid=0,
             trailamount=None, trailpercent=None, oargs={},
             # 止损单设置
             stopprice=None, stopexec=bt.Order.Stop, stopargs={},
             # 止盈单设置
             limitprice=None, limitexec=bt.Order.Limit, limitargs={}, 
             **kwargs):

# 调用示例
brackets = self.sell_bracket(price=13.50,
                             limitprice=13.00，
                             stopprice=14.00)
# 主订单以 13.5 的价格卖出 self.data0 数据集对应的标的
# 当价格跌破 13.00 时，会触发止盈单，买入标的，获得套利收益
# 当价格超过 14.00 时，会触发止损单，买入标的，及时止损
```


### 5.3 执行逻辑

一篮子订单中的三个订单是一块提交的，但执行顺序有主有次、有先有后：

- 只当在主订单执行后，止损单和止盈单才会被激活，而且是同时激活；
- 如果主订单被取消，止盈单和止损单也会被取消；
- 在止盈单和止损单激活之后，如果取消两者中的任意一个，那另外一个也会被取消。

**OCO订单**

OCO 是“aka One Cancel Others”的缩写，OCO 针对的是多个相互关联的订单，一个订单的执行、取消或到期（对应的订单状态有：Completed、Cancelled、Margin、Expired），就会自动取消其他与其相关联的订单。可以将 OCO 看做是订单的属性或特征，通过下单函数中的“oco”参数来设置，例如：

```python
# 案例1
def next(self):
   ...
   o1 = self.buy(...)
   ...
   o2 = self.buy(..., oco=o1)
   ...
   o3 = self.buy(..., oco=o1)

# 案例 2
def next(self):
   ...
   o1 = self.buy(...)
   ...
   o2 = self.buy(..., oco=o1)
   ...
   o3 = self.buy(..., oco=o2)
```

- 案例 1 中，生成的 o1 与 o2 是一组关联订单，其中 o1 是主订单，它的执行情况将会决定 o2 的生死存亡，如果 o1 被执行、取消或到期，就会自动取消订单 o2； o1 与 o3 也是一组关联订单，情况与o1 - o2 组类似；

- 案例 2 中，订单 o1 关联着订单 o2，订单 o2 关联着订单 o3，虽然是 2 组关联订单，实质上o1、o2、o3 是一组订单，因为 o1 以 o2 为媒介，影响 o2 的同时，也影响了 o3 。

**Broker 中的交易执行**

Broker 在执行交易时，会根据执行流程给订单赋予不同的状态，不同阶段的订单状态可以通过Strategy 中定义 `notify_order()` 方法来捕获，从而进行自定义的处理，从下达交易指令到订单执行结束，订单可能会依次呈现如下状态（按排列顺序）。

- Order.Created：订单已被创建；
- Order.Submitted：订单已被传递给经纪商 Broker；
- Order.Accepted：订单已被经纪商接收；
- Order.Partial：订单已被部分成交；
- Order.Complete：订单已成交；
- Order.Cancelled (or Order.Canceled)：确认订单已经被撤销；
- Order.Expired：订单已到期，其已经从系统中删除；
- Order.Margin：执行该订单需要追加保证金，并且先前接受的订单已从系统中删除；
- Order.Rejected：订单已被经纪商拒绝。
- Order.Margin：执行该订单需要追加保证金，并且先前接受的订单已从系统中删除；

`order.status` 的取值对应上述的位置索引，如`order.status==4`，对应 'Completed' 状态 。

## 6. 策略操作

### 6.1 通过 Strategy 类开发策略

Backtrader中，策略逻辑都在 Strategy 类里，有各式各样的交易函数，有各式各样的查询函数，下面是汇总：

```python
import backtrader as bt # 导入 Backtrader

# 创建策略
class MyStrategy(bt.Strategy):
    # 初始化策略参数
    params = (
        (...,...), # 最后一个“,”最好别删！
    )
    # 日志打印：参考的官方文档
    def log(self, txt, dt=None):
        '''构建策略打印日志的函数：可用于打印订单记录或交易记录等'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
  
    # 初始化函数
    def __init__(self):
        '''初始化属性、计算指标等'''
        # 指标计算可参考《backtrader指标篇》
        self.add_timer() # 添加定时器
        pass
    
    # 整个回测周期上，不同时间段对应的函数
    def start(self):
        '''在回测开始之前调用,对应第0根bar'''
        # 回测开始之前的有关处理逻辑可以写在这里
        # 默认调用空的 start() 函数，用于启动回测
        pass
    
    def prenext(self):
        '''策略准备阶段,对应第1根bar-第 min_period-1 根bar'''
        # 该函数主要用于等待指标计算，指标计算完成前都会默认调用prenext()空函数
        # min_period 就是 __init__ 中计算完成所有指标的第1个值所需的最小时间段
        pass
    
  def nextstart(self):
        '''策略正常运行的第一个时点，对应第 min_period 根bar'''
        # 只有在 __init__ 中所有指标都有值可用的情况下，才会开始运行策略
        # nextstart()只运行一次，主要用于告知后面可以开始启动 next() 了
        # nextstart()的默认实现是简单地调用next(),所以next中的策略逻辑从第 min_period根bar就已经开始执行
        pass
    
     def next(self):
        '''策略正常运行阶段，对应第min_period+1根bar-最后一根bar'''
        # 主要的策略逻辑都是写在该函数下
        # 进入该阶段后，会依次在每个bar上循环运行next函数
        # 查询函数
        print('当前持仓量', self.getposition(self.data).size)
        print('当前持仓成本', self.getposition(self.data).price)
        # self.getpositionbyname(name=None, broker=None)
        print('数据集名称列表',getdatanames())
        data = getdatabyname(name) # 根据名称返回数据集
        # 常规下单函数
        self.order = self.buy( ...) # 买入、做多 long
        self.order = self.sell(...) # 卖出、做空 short
        self.order = self.close(...) # 平仓 cover
        self.cancel(order) # 取消订单
        # 目标下单函数
        # 按目标数量下单
        self.order = self.order_target_size(target=size)
        # 按目标金额下单
        self.order = self.order_target_value(target=value)
        # 按目标百分比下单
        self.order = self.order_target_percent(target=percent)
        # 订单组合
        brackets = self.buy_bracket()
        brackets = self.sell_bracket()
        pass
    
    def stop(self):
        '''策略结束，对应最后一根bar'''
        # 告知系统回测已完成，可以进行策略重置和回测结果整理了
        pass
    
  # 打印回测日志
    def notify_order(self, order):
        '''通知订单信息'''
        pass

    def notify_trade(self, trade):
        '''通知交易信息'''
        pass
    
    def notify_cashvalue(self, cash, value):
        '''通知当前资金和总资产'''
        pass
    
    def notify_fund(self, cash, value, fundvalue, shares):
        '''返回当前资金、总资产、基金价值、基金份额'''
        pass
    
    def notify_store(self, msg, *args, **kwargs):
        '''返回供应商发出的信息通知'''
        pass
    
    def notify_data(self, data, status, *args, **kwargs):
        '''返回数据相关的通知'''
        pass
    
    def notify_timer(self, timer, when, *args, **kwargs)：
      '''返回定时器的通知'''
      # 定时器可以通过函数add_time()添加
        pass
    
  # 各式各样的交易函数和查询函数：请查看《交易篇（上）》和《交易篇（下）》

......
# 将策略添加给大脑
cerebro.addstrategy(MyStrategy)
......
```

### 6.2 基于交易信号直接生成策略

除了在 Strategy 类中编写策略外，追求 “极简” 的 Backtrader 还给大家提供了一种更为简单的策略生成方式，这种方式不需要定义 Strategy 类，更不需要调用交易函数，只需计算信号 signal 指标，然后将其 `add_signal` 给大脑 Cerebro 即可，Cerebro 会自动将信号 signal 指标转换为交易指令，通常可以将这类策略称为信号策略 SignalStrategy 。下面以官方文档中的例子介绍信号策略生成方式：

- 第一步：自定义交易信号，交易信号和一般的指标相比的区别只在于：交易信号指标在通过 add_signal 传递给大脑后，大脑会将其转换为策略，所以在自定义交易信号时直接按照 Indicator 指标定义方式来定义即可。定义时需要声明信号 'signal' 线，信号指标也是赋值给 'signal' 线；

- 第二步：按常规方式，实例化大脑 cerebro、加载数据、通过 add_signal 添加交易信号线 ；

- 备注：信号策略每次下单的成交量取的是 Sizer 模块中的 FixedSize，默认成交 1 单位的标的，比如 1 股、1 张合约等；生成的是市价单 Market，订单在被取消前一直都有效。

```python
import backtrader as bt

# 自定义信号指标
class MySignal(bt.Indicator):
    lines = ('signal',) # 声明 signal 线，交易信号放在 signal line 上
    params = (('period', 30),)

    def __init__(self):
        self.lines.signal = self.data - bt.indicators.SMA(period=self.p.period)

# 实例化大脑
cerebro = bt.Cerebro() 
# 加载数据
data = bt.feeds.OneOfTheFeeds(dataname='mydataname')
cerebro.adddata(data)
# 添加交易信号
cerebro.add_signal(bt.SIGNAL_LONGSHORT, MySignal, period=xxx)
cerebro.run()
```

支持添加多条交易信号：

```python
import backtrader as bt

# 定义交易信号1
class SMACloseSignal(bt.Indicator):
    lines = ('signal',)
    params = (('period', 30),)

    def __init__(self):
        self.lines.signal = self.data - bt.indicators.SMA(period=self.p.period)

# 定义交易信号2
class SMAExitSignal(bt.Indicator):
    lines = ('signal',)
    params = (('p1', 5), ('p2', 30),)

    def __init__(self):
        sma1 = bt.indicators.SMA(period=self.p.p1)
        sma2 = bt.indicators.SMA(period=self.p.p2)
        self.lines.signal = sma1 - sma2
        
# 实例化大脑
cerebro = bt.Cerebro() 
# 加载数据
data = bt.feeds.OneOfTheFeeds(dataname='mydataname')
cerebro.adddata(data)
# 添加交易信号1
cerebro.add_signal(bt.SIGNAL_LONG, MySignal, period=xxx)
# 添加交易信号2
cerebro.add_signal(bt.SIGNAL_LONGEXIT, SMAExitSignal, p1=xxx, p2=xxx) 
cerebro.run()
```

**信号指标取值与多空信号对应关系**

- signal 指标取值大于0 → 对应多头 long 信号；
- signal 指标取值小于0 → 对应空头 short 信号；
- signal 指标取值等于0 → 不发指令.

---

**add_signal(signal type, signal class, arg) 中的参数**

第 1 个参数：信号类型，分为 2 大类，共计 5 种信号类型，用于确定平仓信号，在下达平仓指令时，优先级高于开仓类中的信号。

+ **开仓类：**

  - `bt.SIGNAL_LONGSHORT`：多头信号和空头信号都会作为开仓信号；对于多头信号，如果之前有空头仓位，会先对空仓进行平仓 close，再开多仓；空头信号也类似，会在开空仓前对多仓进行平仓 close。

  - `bt.SIGNAL_LONG`：多头信号用于做多，空头信号用于平仓 close；如果系统中同时存在 LONGEXIT 信号类型，SIGNAL_LONG 中的空头信号将不起作用，将会使用 LONGEXIT 中的空头信号来平仓多头，如上面的多条交易信号的例子。

  - `bt.SIGNAL_SHORT`：空头信号用于做空，多头信号用于平仓；如果系统中同时存在 SHORTEXIT 信号类型，SIGNAL_SHORT 中的多头信号将不起作用，将会使用 SHORTEXIT 中的多头信号来平仓空头。

+ **平仓类：**

  - `bt.SIGNAL_LONGEXIT`：接收空头信号平仓多头；

  - `bt.SIGNAL_SHORTEXIT`：接收多头信号平仓空头；

    上述 2 种信号类型主要用于确定平仓信号，在下达平仓指令时，优先级高于上面开仓类中的信号。

第 2 个参数：定义的信号指标类的名称，比如案例中的 SMACloseSignal 类 和 SMAExitSignal 类，直接传入类即可，不需要将类进行实例化；

第 3 个参数：对应信号指标类中的参数 params，直接通过 `period=xxx` 、`p1=xxx`, `p2=xxx` 形式修改参数取值。

**关于订单累计和订单并发**

由于交易信号指标通常只是技术指标之间进行加减得到，在技术指标完全已知的情况下，很容易连续不断的生成交易信号，进而连续不断的生成订单，这样就容易出现如下 2 种情况：

- 积累 Accumulation：即使已经在市场上，信号也会产生新的订单，进而增加市场的头寸；

- 并发 Concurrency：新订单会并行着生成，而不是等待其他订单的执行完再后依次执行。

可通过如下 2 个函数来控制上述 2 种情况的发生：

```python
cerebro.signal_accumulate(True)
cerebro.signal_concurrency(True)
# True 表示允许其发生， False 表示不允许其发生
```

### 6.3 返回策略收益评价指标

回测完成后，通常需要计算此次回测的各项收益评价指标，据此判断策略的好坏表现，在 Backtrader 中，有专门负责回测收益评价指标计算的模块 analyzers，可称为“策略分析器”。关于 analyzers 支持内置的指标分析器的具体信息可以参考官方文档 Backtrader ~ Analyzers Reference 。分析器的使用主要分为 2 步：

- 第一步：通过 `addanalyzer(ancls, _name, *args, **kwargs) `方法将分析器添加给大脑，ancls 对应内置的分析器类，后面是分析器各自支持的参数，添加的分析器类 ancls 在 cerebro running 区间会被实例化，并分配给 cerebro 中的每个策略，然后分析每个策略的表现，而不是所有策略整体的表现 ；

- 第二步：分别基于`results = cerebro.run()`返回的各个对象 `results[x] `，提取该对象 analyzers 属性下的各个分析器的计算结果，并通过 `get_analysis()` 来获取具体值。

- 说明：`addanalyzer()` 时，通常会通过_name 参数对分析器进行命名。

```python
......
# 添加分析指标
# 返回年初至年末的年度收益率
cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='_AnnualReturn')
# 计算最大回撤相关指标
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='_DrawDown')
# 计算年化收益：日度收益
cerebro.addanalyzer(bt.analyzers.Returns, _name='_Returns', tann=252)
# 计算年化夏普比率：日度收益
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio', timeframe=bt.TimeFrame.Days, annualize=True, riskfreerate=0) # 计算夏普比率
cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name='_SharpeRatio_A')
# 返回收益率时序
cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='_TimeReturn')
# 启动回测
result = cerebro.run() 

# 提取结果
print("--------------- AnnualReturn -----------------")
print(result[0].analyzers._AnnualReturn.get_analysis())
print("--------------- DrawDown -----------------")
print(result[0].analyzers._DrawDown.get_analysis())
print("--------------- Returns -----------------")
print(result[0].analyzers._Returns.get_analysis())
print("--------------- SharpeRatio -----------------")
print(result[0].analyzers._SharpeRatio.get_analysis())
print("--------------- SharpeRatio_A -----------------")
print(result[0].analyzers._SharpeRatio_A.get_analysis())
......
```

各个分析器的结果通常以 OrderedDict 字典的形式返回，如下所示，可通过 keys 取需要的 values：

```python
AutoOrderedDict([('len', 56),
                 ('drawdown', 8.085458202746946e-05),
                 ('moneydown', 8.08547225035727),
                 ('max',
                  AutoOrderedDict([('len', 208),
                                   ('drawdown', 0.00015969111320873712),
                                   ('moneydown', 15.969112889841199)]))])

# 常用指标提取
analyzer = {}
# 提取年化收益
analyzer['年化收益率'] = result[0].analyzers._Returns.get_analysis()['rnorm']
analyzer['年化收益率（%）'] = result[0].analyzers._Returns.get_analysis()['rnorm100']
# 提取最大回撤
analyzer['最大回撤（%）'] = result[0].analyzers._DrawDown.get_analysis()['max']['drawdown'] * (-1)
# 提取夏普比率
analyzer['年化夏普比率'] = result[0].analyzers._SharpeRatio_A.get_analysis()['sharperatio']

# 日度收益率序列
ret = pd.Series(result[0].analyzers._TimeReturn.get_analysis())
```

除了上面提到的这些内置分析器外，Backtrader 当然还支持自定义分析器（不然就不符合 Backtrader style 了）。凡涉及到自定义，遵循的都是“在继承了 xxx 原始父类的基础上，在新的子类里自定义相关属性和方法”。

自定义分析器的过程与定义策略函数是最相似的，分析器毕竟是用来分析整个回测的，既涉及过程，又涉及结果，所以继承的` bt.Analyzer` 父类中的方法和相应的运行逻辑和策略中的基本一致：

```python
import backtrader as bt # 导入 Backtrader 

# 创建分析器
class MyAnalyzer(bt.Analyzer):
    # 初始化参数：比如内置分析器支持设置的那些参数
    params = (
        (...,...), # 最后一个“,”最好别删！
    )
    # 初始化函数
    def __init__(self):
        '''初始化属性、计算指标等'''
        pass
    
    # analyzer与策略一样，都是从第0根bar开始运行
    # 都会面临 min_period 问题
    # 所以都会通过 prenext、nextstart 来等待 min_period 被满足
    def start(self):
        pass
    
    def prenext(self):
        pass
    
  def nextstart(self):
        pass
    
    def next(self):
        pass
    
    def stop(self):
        # 一般对策略整体的评价指标是在策略结束后开始计算的
        pass
    
  # 支持与策略一样的信息打印函数
    def notify_order(self, order):
        '''通知订单信息'''
        pass

    def notify_trade(self, trade):
        '''通知交易信息'''
        pass
    
    def notify_cashvalue(self, cash, value):
        '''通知当前资金和总资产'''
        pass
    
    def notify_fund(self, cash, value, fundvalue, shares):
        '''返回当前资金、总资产、基金价值、基金份额'''
        pass
    
    def get_analysis(self):
        pass

    
# 官方提供的 SharpeRatio 例子
class SharpeRatio(Analyzer):
    params = (('timeframe', TimeFrame.Years), ('riskfreerate', 0.01),)

    def __init__(self):
        super(SharpeRatio, self).__init__()
        self.anret = AnnualReturn()

    def start(self):
        # Not needed ... but could be used
        pass

    def next(self):
        # Not needed ... but could be used
        pass

    def stop(self):
        retfree = [self.p.riskfreerate] * len(self.anret.rets)
        retavg = average(list(map(operator.sub, self.anret.rets, retfree)))
        retdev = standarddev(self.anret.rets)
        self.ratio = retavg / retdev
        
    def get_analysis(self):
        return dict(sharperatio=self.ratio)
```

下面是在 Backtrader 社区中找到的自定义分析器，用于查看每笔交易盈亏情况：

- 地址：https://community.backtrader.com/topic/1274/closed-trade-list-including-mfe-mae-analyzer；

- 该案例涉及到 trade 对象的相关属性，具体可以参考官方文档：https://www.backtrader.com/docu/trade/ 。

```python
class trade_list(bt.Analyzer):
    def __init__(self):

        self.trades = []
        self.cumprofit = 0.0

    def notify_trade(self, trade):

        if trade.isclosed:
            brokervalue = self.strategy.broker.getvalue()

            dir = 'short'
            if trade.history[0].event.size > 0: dir = 'long'

            pricein = trade.history[len(trade.history)-1].status.price
            priceout = trade.history[len(trade.history)-1].event.price
            datein = bt.num2date(trade.history[0].status.dt)
            dateout = bt.num2date(trade.history[len(trade.history)-1].status.dt)
            if trade.data._timeframe >= bt.TimeFrame.Days:
                datein = datein.date()
                dateout = dateout.date()

            pcntchange = 100 * priceout / pricein - 100
            pnl = trade.history[len(trade.history)-1].status.pnlcomm
            pnlpcnt = 100 * pnl / brokervalue
            barlen = trade.history[len(trade.history)-1].status.barlen
            pbar = pnl / barlen
            self.cumprofit += pnl

            size = value = 0.0
            for record in trade.history:
                if abs(size) < abs(record.status.size):
                    size = record.status.size
                    value = record.status.value

            highest_in_trade = max(trade.data.high.get(ago=0, size=barlen+1))
            lowest_in_trade = min(trade.data.low.get(ago=0, size=barlen+1))
            hp = 100 * (highest_in_trade - pricein) / pricein
            lp = 100 * (lowest_in_trade - pricein) / pricein
            if dir == 'long':
                mfe = hp
                mae = lp
            if dir == 'short':
                mfe = -lp
                mae = -hp

            self.trades.append({'ref': trade.ref, 
             'ticker': trade.data._name, 
             'dir': dir，
             'datein': datein, 
             'pricein': pricein, 
             'dateout': dateout, 
             'priceout': priceout,
             'chng%': round(pcntchange, 2), 
             'pnl': pnl, 'pnl%': round(pnlpcnt, 2),
             'size': size, 
             'value': value, 
             'cumpnl': self.cumprofit,
             'nbars': barlen, 'pnl/bar': round(pbar, 2),
             'mfe%': round(mfe, 2), 'mae%': round(mae, 2)})
            
    def get_analysis(self):
        return self.trades
```

调用时，需要设置 `cerebro.run(tradehistory=True)`：

```python
# 添加自定义的分析指标
cerebro.addanalyzer(trade_list, _name='tradelist')

# 启动回测
result = cerebro.run(tradehistory=True)

# 返回结果
ret = pd.DataFrame(result[0].analyzers.tradelist.get_analysis())
```

---

### 6.4 对策略进行参数优化
如果策略的收益表现可能受相关参数的影响，需要验证比较参数不同取值对策略表现的影响，就可以使用 Backtrader 的参数优化功能，使用该功能只需通过 `cerebro.optstrategy()` 方法往大脑添加策略即可：

```python
class TestStrategy(bt.Strategy):
  
    params=(('period1',5),
            ('period2',10),) #全局设定均线周期
    ......

    
# 实例化大脑
cerebro1= bt.Cerebro(optdatas=True, optreturn=True)
# 设置初始资金
cerebro1.broker.set_cash(10000000)
# 加载数据
datafeed1 = bt.feeds.PandasData(dataname=data1, fromdate=datetime.datetime(2019,1,2), todate=datetime.datetime(2021,1,28))
cerebro1.adddata(datafeed1, name='600466.SH')

# 添加优化器
cerebro1.optstrategy(TestStrategy, period1=range(5, 25, 5), period2=range(10, 41, 10))

# 添加分析指标
# 返回年初至年末的年度收益率
cerebro1.addanalyzer(bt.analyzers.AnnualReturn, _name='_AnnualReturn')
# 计算最大回撤相关指标
cerebro1.addanalyzer(bt.analyzers.DrawDown, _name='_DrawDown')
# 计算年化收益
cerebro1.addanalyzer(bt.analyzers.Returns, _name='_Returns', tann=252)
# 计算年化夏普比率
cerebro1.addanalyzer(bt.analyzers.SharpeRatio_A, _name='_SharpeRatio_A')
# 返回收益率时序
cerebro1.addanalyzer(bt.analyzers.TimeReturn, _name='_TimeReturn')

# 启动回测
result = cerebro1.run()

# 打印结果
def get_my_analyzer(result):
    analyzer = {}
    # 返回参数
    analyzer['period1'] = result.params.period1
    analyzer['period2'] = result.params.period2
    # 提取年化收益
    analyzer['年化收益率'] = result.analyzers._Returns.get_analysis()['rnorm']
    analyzer['年化收益率（%）'] = result.analyzers._Returns.get_analysis()['rnorm100']
    # 提取最大回撤(习惯用负的做大回撤，所以加了负号)
    analyzer['最大回撤（%）'] = result.analyzers._DrawDown.get_analysis()['max']['drawdown'] * (-1)
    # 提取夏普比率
    analyzer['年化夏普比率'] = result.analyzers._SharpeRatio_A.get_analysis()['sharperatio']
    
    return analyzer

ret = []
for i in result:
    ret.append(get_my_analyzer(i[0]))
    
pd.DataFrame(ret)
```

- `cerebro.optstrategy(strategy, *args, **kwargs)`：strategy 就是自定义的策略类（比如上例的TestStrategy）、后面*args, **kwargs 对应自定义策略类中 params 中的需要优化的参数的取值（比如上例的period1=range(5, 25, 5), period2=range(10, 41, 10)）；当有多个参数时，会将各个参数的各个取值进行一一匹配（见上面的输出结果）；
- 参数优化是基于 multiprocessing 进行多进程处理数据和分析结果的。在实例化大脑的时候，有 2 个与参数优化相关的参数：

  - `optdatas=True`：在处理数据时会采用相对节省时间的方式，进而提高优化速度；

  - `optreturn=True`：在返回回测结果时，为了节省时间，只返回与参数优化最相关的内容（params 和 analyzers），而不会返回参数优化不关心的数据（比如 datas, indicators, observers …等）.


注意：在对于多个标的进行参数优化过程中（比如连续对1000个股票的均线策略寻优），如果对于多进程的cpu使用数量不加限制，会有一定几率出现异常错误的情况，这类错误目前还没找到解决方法。建议是限制cpu的数量，如设置为2或3：

```python
cerebro.run(maxcpus=2)
```

## 7. 回测可视化

### 7.1 observers 观测器

**最常用的观测器**

下面是对最常用的观测器的介绍，其他观测器可以参考Backtrader 官方文档 ~ Observers - Reference：

- `backtrader.observers.Broker`：记录了经纪商 broker 中各时间点的可用资金和总资产；可视化时，会同时展示 cash 和 values 曲线；如果想各自单独展示 cash 和 values，可以分别调用 backtrader.observers.Cash 和 backtrader.observers.Value；
- `backtrader.observers.BuySell`：记录了回测过程中的买入和卖出信号；可视化时，会在价格曲线上标注买卖点；
- `backtrader.observers.Trades`：记录了回测过程中每次交易的盈亏（从买入建仓到卖出清仓算一次交易）；可视化时，会绘制盈亏点；
- `backtrader.observers.TimeReturn`：记录了回测过程中的收益序列；可视化时，会绘制 TimeReturn 收益曲线；
- `backtrader.observers.DrawDown`：记录了回测过程的回撤序列；可视化时，绘制回撤曲线；
- `backtrader.observers.Benchmark`：记录了业绩基准的收益序列，业绩基准的数据必须事先通过 adddata、resampledata、replaydata 等数据添加函数添加进大脑中 cerebro；可视化时，会同时绘制策略本身的收益序列（即：backtrader.observers.TimeReturn 绘制的收益曲线）和业绩基准的收益曲线。

**如何添加 observers**

observers 观测器是通过 `addobserver()` 添加给大脑 cerebro 的：`addobserver(obscls, *args, **kwargs)`。其中，参数 obscls 对应 observers 类下的观测器、*args, **kwargs 对应观测器支持设置的参数，具体如下所示。

```python
import backtrader as bt
...
cerebro = bt.Cerebro(stdstats=False) 
cerebro.addobserver(bt.observers.Broker)
cerebro.addobserver(bt.observers.Trades)
cerebro.addobserver(bt.observers.BuySell)
cerebro.addobserver(bt.observers.DrawDown)
cerebro.addobserver(bt.observers.TimeReturn)
# 添加业绩基准时，需要事先将业绩基准的数据添加给 cerebro
banchdata = bt.feeds.PandasData(dataname=data, fromdate=st_date, todate=ed_date)
cerebro.adddata(banchdata, name='xxxx')
cerebro.addobserver(bt.observers.Benchmark, data=banchdata)
```

对于 Broker、Trades、BuySell 3个观测器，默认是自动添加给 cerebro 的，可以在实例化大脑时，通过 stdstats 来控制：bt.Cerebro(stdstats=False) 表示可视化时，不展示 Broker、Trades、BuySell 观测器；反之，自动展示；默认情况下是自动展示。

**如何读取 observers 中的数据**

observers  中记录了各种回测数据，可以将其看作是一个支持可视化展示的数据存储器，所以 observers 属于 lines 对象。如果想在 Strategy 中读取 observers 中的数据，就会用到 line 的相关操作，具体可以参考《Backtrader 数据篇》的内容，observers 的数据通过 self.stats 对象 来连接：

```python
class MyStrategy(bt.Strategy):
    def next(self):
        # 当前时点的前一天的可用现金
        self.stats.broker.cash[0]
        # 当前时点的前一天的总资产
        self.stats.broker.value[0]
        # 获取当前时刻前一天的收益
        self.stats.timereturn.line[0]
        # observers 取得[0]值，对应的 next 中 self.data.datetime[-1] 这一天的值
```

observers 是在所有指标被计算完之后、在执行 Strategy 的 next 方法之后才运行并统计数据的，所以读取的最新数据 [0] 相对与 next 的当前时刻是晚一天的。

如果想要将 observers  中的数据保存到本地，可以通过 writer  写入本地文件，如下面的读写到本地 CSV 文件：

```python
import csv

class TestStrategy(bt.Strategy):
    ... 
    def start(self):
        self.mystats = csv.writer(open("mystats.csv", "w"))
        self.mystats.writerow(['datetime',
                               'drawdown', 'maxdrawdown', 
                               'timereturn',
                               'value', 'cash'])
    def next(self): 
        self.mystats.writerow([self.data.datetime.date(-1).strftime('%Y-%m-%d'),
                               '%.4f' % self.stats.drawdown.drawdown[0],
                               '%.4f' % self.stats.drawdown.maxdrawdown[0],
                               '%.4f' % self.stats.timereturn.line[0],
                               '%.4f' % self.stats.broker.value[0],
                               '%.4f' % self.stats.broker.cash[0]]) 
    def stop(self):  
        self.mystats.writerow([self.data.datetime.date(0).strftime('%Y-%m-%d'),
                               '%.4f' % self.stats.drawdown.drawdown[0],
                               '%.4f' % self.stats.drawdown.maxdrawdown[0],
                               '%.4f' % self.stats.broker.value[0],
                               '%.4f' % self.stats.broker.cash[0]])
        
    # 当运行到最后一根 bar 后， next 中记录的是上一根 bar 的收益
    # stop 是在 next 运行完后才运行的，此时 observers 已经计算完 最后一根 bar 的收益了
    # 所以可以在 stop 中获取最后一根 bar 的收益
```

**自定义 observers**

和之前各种自定义一致，自定义 observers 同样是在继承父类 bt.observer.Observer 的基础上，自定义新的的observers。下面是 Backtrader 官网提供的例子，用于统计已成功创建的订单的价格和到期订单的价格。

```python
class OrderObserver(bt.observer.Observer):
    lines = ('created', 'expired',)

    plotinfo = dict(plot=True, subplot=True, plotlinelabels=True)

    plotlines = dict(
        created=dict(marker='*', markersize=8.0, color='lime', fillstyle='full'),
        expired=dict(marker='s', markersize=8.0, color='red', fillstyle='full')
    )

    def next(self):
        for order in self._owner._orderspending:
            if order.data is not self.data:
                continue

            if not order.isbuy():
                continue

            # Only interested in "buy" orders, because the sell orders
            # in the strategy are Market orders and will be immediately
            # executed

            if order.status in [bt.Order.Accepted, bt.Order.Submitted]:
                self.lines.created[0] = order.created.price

            elif order.status in [bt.Order.Expired]:
                self.lines.expired[0] = order.created.price
```

- observers 本身是 Lines 对象，所以构建逻辑与自定义 Indicator 类似，将要统计的数据指定为相应的 line，然后随着回测的进行依次存入数据；
- 作为 Lines 对象的 Observers 和 Indicator ，类内部都有 `plotinfo = dict(...)`、`plotlines = dict(...) `属性，用于回测结束后通过 cerebro.plot() 方法进行可视化展示；
- 有时候如果想修改 Backtrader 已有观测器的相关属性，可以直接继承该观测器，然后设置属性取值进行修改。如下面在原始 bt.observers.BuySell 的基础上，修改买卖点的样式。

```python
class my_BuySell(bt.observers.BuySell):
    params = (('barplot', True), ('bardist', 0.02))
    plotlines = dict(
    buy=dict(marker=r'$\Uparrow$', markersize=10.0, color='#d62728' ),
    sell=dict(marker=r'$\Downarrow$', markersize=10.0, color='#2ca02c'))
    # 将 三角形改为箭头
    
# 突然感受到了继承的强大！
```

### 7.2 plot() 图形绘制

`cerebro.plot()` 写在 `cerebro.run()` 后面，用于回测的可视化。总的来说，`cerebro.plot()` 支持回测如下 3 大内容：

- Data Feeds：即在回测开始前，通过 adddata、replaydata、resampledata 等方法导入大脑的原始数据；
- Indicators ：即回测时构建的各类指标，比如在 strategy 中构建的指标、通过 addindicator 添加的；
- Observers ：即上文介绍的观测器对象；
- 在绘制图形时，默认是将 Data Feeds 绘制在主图上；Indicators 有的与 Data Feeds 一起绘制在主图上，比如均线，有的以子图形式绘制；Observers 通常绘制在子图上。

**plot() 中的参数**

`plot()` 中的参数主要用于系统性的配置图形，具体参数如下所示：

```python
plot(plotter=None, # 包含各种绘图属性的对象或类，如果为None，默认取 PlotScheme 类，如下所示
     numfigs=1, # 是否将图形拆分成多幅图展示，如果时间区间比较长，建议分多幅展示
     iplot=True, # 在 Jupyter Notebook 上绘图时是否自动 plot inline
     **kwargs) # 对应 PlotScheme 中的各个参数

# PlotScheme 中的参数如下所示
class PlotScheme(object):
    def __init__(self):
        # to have a tight packing on the chart wether only the x axis or also
        # the y axis have (see matplotlib)
        self.ytight = False

        # y-margin (top/bottom) for the subcharts. This will not overrule the
        # option plotinfo.plotymargin
        self.yadjust = 0.0
        # Each new line is in z-order below the previous one. change it False
        # to have lines paint above the previous line
        self.zdown = True
        # Rotation of the date labes on the x axis
        self.tickrotation = 15

        # How many "subparts" takes a major chart (datas) in the overall chart
        # This is proportional to the total number of subcharts
        self.rowsmajor = 5

        # How many "subparts" takes a minor chart (indicators/observers) in the
        # overall chart. This is proportional to the total number of subcharts
        # Together with rowsmajor, this defines a proportion ratio betwen data
        # charts and indicators/observers charts
        self.rowsminor = 1

        # Distance in between subcharts
        self.plotdist = 0.0

        # Have a grid in the background of all charts
        self.grid = True

        # Default plotstyle for the OHLC bars which (line -> line on close)
        # Other options: 'bar' and 'candle'
        self.style = 'line'

        # Default color for the 'line on close' plot
        self.loc = 'black'
        # Default color for a bullish bar/candle (0.75 -> intensity of gray)
        self.barup = '0.75'
        # Default color for a bearish bar/candle
        self.bardown = 'red'
        # Level of transparency to apply to bars/cancles (NOT USED)
        self.bartrans = 1.0

        # Wether the candlesticks have to be filled or be transparent
        self.barupfill = True
        self.bardownfill = True

        # Wether the candlesticks have to be filled or be transparent
        self.fillalpha = 0.20

        # Wether to plot volume or not. Note: if the data in question has no
        # volume values, volume plotting will be skipped even if this is True
        self.volume = True

        # Wether to overlay the volume on the data or use a separate subchart
        self.voloverlay = True
        # Scaling of the volume to the data when plotting as overlay
        self.volscaling = 0.33
        # Pushing overlay volume up for better visibiliy. Experimentation
        # needed if the volume and data overlap too much
        self.volpushup = 0.00

        # Default colour for the volume of a bullish day
        self.volup = '#aaaaaa'  # 0.66 of gray
        # Default colour for the volume of a bearish day
        self.voldown = '#cc6073'  # (204, 96, 115)
        # Transparency to apply to the volume when overlaying
        self.voltrans = 0.50

        # Transparency for text labels (NOT USED CURRENTLY)
        self.subtxttrans = 0.66
        # Default font text size for labels on the chart
        self.subtxtsize = 9

        # Transparency for the legend (NOT USED CURRENTLY)
        self.legendtrans = 0.25
        # Wether indicators have a leged displaey in their charts
        self.legendind = True
        # Location of the legend for indicators (see matplotlib)
        self.legendindloc = 'upper left'

        # Plot the last value of a line after the Object name
        self.linevalues = True

        # Plot a tag at the end of each line with the last value
        self.valuetags = True

        # Default color for horizontal lines (see plotinfo.plothlines)
        self.hlinescolor = '0.66'  # shade of gray
        # Default style for horizontal lines
        self.hlinesstyle = '--'
        # Default width for horizontal lines
        self.hlineswidth = 1.0

        # Default color scheme: Tableau 10
        self.lcolors = tableau10

        # strftime Format string for the display of ticks on the x axis
        self.fmt_x_ticks = None

        # strftime Format string for the display of data points values
        self.fmt_x_data = None
```

如果想要系统性修改图形样式，可以重新定义 PlotScheme 类，然后修改里面用到的参数；也可以直接在`plot()` 中修改：

```python
# 通过参数形式来设置
cerebro.plot(iplot=False, 
             style='candel', # 设置主图行情数据的样式为蜡烛图
             lcolors=colors , # 重新设置主题颜色
             plotdist=0.1, # 设置图形之间的间距
             barup = '#ff9896', bardown='#98df8a', # 设置蜡烛图上涨和下跌的颜色
             volup='#ff9896', voldown='#98df8a', # 设置成交量在行情上涨和下跌情况下的颜色
             ....)
```

关于主题颜色，Backtrader 提供了Tableau 10 、Tableau 10 Light、Tableau 20 3种主题色，默认是以 Tableau 10 为主题色。但是看源代码，不知道如何修改 lcolors，源码 scheme.py 文件中的 tableau10 只一个变量，直接赋值给 `self.lcolors = tableau10`，如果在我们在自己的的 notebook上运行 `lcolors=tableau10` 会报错，提示 tableau10 变量不存在。所以，如果想修改主题色，需要重新定义 tableau10 变量：

```python
# 定义主题色变量：直接从源码 scheme.py 中复制的
tableau20 = [
    'steelblue', # 0
    'lightsteelblue', # 1
    'darkorange', # 2
    'peachpuff', # 3
    'green', # 4
    'lightgreen', # 5
    'crimson', # 6
    'lightcoral', # 7
    'mediumpurple', # 8
    'thistle', # 9
    'saddlebrown', # 10
    'rosybrown', # 11
    'orchid', # 12
    'lightpink', # 13
    'gray', # 14
    'lightgray', # 15
    'olive', # 16
    'palegoldenrod', # 17
    'mediumturquoise', # 18
    'paleturquoise', # 19
]

tableau10 = [
    'blue', # 'steelblue', # 0
    'darkorange', # 1
    'green', # 2
    'crimson', # 3
    'mediumpurple', # 4
    'saddlebrown', # 5
    'orchid', # 6
    'gray', # 7
    'olive', # 8
    'mediumturquoise', # 9
]

tableau10_light = [
    'lightsteelblue', # 0
    'peachpuff', # 1
    'lightgreen', # 2
    'lightcoral', # 3
    'thistle', # 4
    'rosybrown', # 5
    'lightpink', # 6
    'lightgray', # 7
    'palegoldenrod', # 8
    'paleturquoise', # 9
]

# 选一个主题色做修改
cerebro.plot(lcolors=tableau10)


# 当然也可以选自己喜欢的主题色
mycolors = ['#729ece', '#ff9e4a', '#67bf5c', 
          '#ed665d', '#ad8bc9', '#a8786e', 
          '#ed97ca', '#a2a2a2', '#cdcc5d', '#6dccda']

cerebro.plot(lcolors=mycolors)
```

从源码中复制的主题色，后面都注释了索引号，而 Backtrader 在绘制图形时，选择颜色的顺序依次是这样的：

- tab10_index = [3, 0, 2, 1, 2, 4, 5, 6, 7, 8, 9]；
- tab10_index 中的序号对应的是 主题色 的索引号；
- 每一幅图，依次取 tab10_index 中的序号对应的颜色来绘制，比如 MACD 有 3 条 line，line0 的颜色为 tab10_index[0] = 3，也就是 lcolors=tableau10 中的索引号为 3 对应的颜色 'crimson'；line1 的颜色为 tab10_index[1] = 0，也就是 lcolors=tableau10 中的索引号为 0 对应的颜色 'blue'；
- 所以在设置颜色时，需要与 tab10_index  中的序号结合起来看。

**局部绘图参数设置**

对于 Indicators  和 Observers 的可视化设置，通过类内部的 `plotinfo = dict(...)`、`plotlines = dict(...)` 属性来控制，其中 plotinfo 主要对图形整体布局进行设置，plotlines 主要对具体 line 的样式进行设置：

```python
plotinfo = dict(plot=True, # 是否绘制
                subplot=True, # 是否绘制成子图
                plotname='', # 图形名称
                plotabove=False, # 子图是否绘制在主图的上方
                plotlinelabels=False, # 主图上曲线的名称
                plotlinevalues=True, # 是否展示曲线最后一个时间点上的取值
                plotvaluetags=True, # 是否以卡片的形式在曲线末尾展示最后一个时间点上的取值
                plotymargin=0.0, # 用于设置子图 y 轴的边界
                plothlines=[a,b,...], # 用于绘制取值为 a,b,... 的水平线
                plotyticks=[], # 用于绘制取值为 a,b,... y轴刻度
                plotyhlines=[a,b,...], # 优先级高于plothlines、plotyticks，是这两者的结合
                plotforce=False, # 是否强制绘图
                plotmaster=None, # 用于指定主图绘制的主数据
                plotylimited=True, 
                # 用于设置主图的 y 轴边界，
                # 如果True，边界只由主数据 data feeds决定，无法完整显示超出界限的辅助指标；
                # 如果False, 边界由主数据 data feeds和指标共同决定，能确保所有数据都能完整展示
           )

# 修改交易观测器的样式
class my_Trades(bt.observers.Trades):
    plotlines = dict(
    pnlplus=dict(_name='Positive',
                 marker='^', color='#ed665d',
                 markersize=8.0, fillstyle='full'),
    pnlminus=dict(_name='Negative',
                  marker='v', color='#729ece',
                  markersize=8.0, fillstyle='full'))
    
# 修改买卖点样式
class my_BuySell(bt.observers.BuySell):
    params = (('barplot', True), ('bardist', 0.02)) # bardist 控制买卖点与行情线之间的距离
    plotlines = dict(
    buy=dict(marker=r'$\Uparrow$', markersize=10.0, color='#d62728' ),
    sell=dict(marker=r'$\Downarrow$', markersize=10.0, color='#2ca02c'))
```

### 7.3 基于收益序列进行可视化

Backtrader 自带的绘图工具方便好用，不过平时在汇报策略回测结果时，可能更关注的是策略的累计收益曲线和业绩评价指标等结果，而这些回测统计信息只需基于回测返回的 TimeReturn 收益序列做简单计算即可得到。下面是基于 Backtrader 回测返回的分析器 TimeReturn、pyfolio、matplotlib 得到的可视化图形：

```python
.....
# 回测时需要添加 TimeReturn 分析器
cerebro1.addanalyzer(bt.analyzers.TimeReturn, _name='_TimeReturn')
result = cerebro1.run()

# 提取收益序列
pnl = pd.Series(result[0].analyzers._TimeReturn.get_analysis())
# 计算累计收益
cumulative = (pnl + 1).cumprod()
# 计算回撤序列
max_return = cumulative.cummax()
drawdown = (cumulative - max_return) / max_return
# 计算收益评价指标
import pyfolio as pf
# 按年统计收益指标
perf_stats_year = (pnl).groupby(pnl.index.to_period('y')).apply(lambda data: pf.timeseries.perf_stats(data)).unstack()
# 统计所有时间段的收益指标
perf_stats_all = pf.timeseries.perf_stats((pnl)).to_frame(name='all')
perf_stats = pd.concat([perf_stats_year, perf_stats_all.T], axis=0)
perf_stats_ = round(perf_stats,4).reset_index()


# 绘制图形
import matplotlib.pyplot as plt
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
import matplotlib.ticker as ticker # 导入设置坐标轴的模块
plt.style.use('seaborn') # plt.style.use('dark_background')

fig, (ax0, ax1) = plt.subplots(2,1, gridspec_kw = {'height_ratios':[1.5, 4]}, figsize=(20,8))
cols_names = ['date', 'Annual\nreturn', 'Cumulative\nreturns', 'Annual\nvolatility',
       'Sharpe\nratio', 'Calmar\nratio', 'Stability', 'Max\ndrawdown',
       'Omega\nratio', 'Sortino\nratio', 'Skew', 'Kurtosis', 'Tail\nratio',
       'Daily value\nat risk']

# 绘制表格
ax0.set_axis_off() # 除去坐标轴
table = ax0.table(cellText = perf_stats_.values, 
                bbox=(0,0,1,1), # 设置表格位置， (x0, y0, width, height)
                rowLoc = 'right', # 行标题居中
                cellLoc='right' ,
                colLabels = cols_names, # 设置列标题
                colLoc = 'right', # 列标题居中
                edges = 'open' # 不显示表格边框
                )
table.set_fontsize(13)

# 绘制累计收益曲线
ax2 = ax1.twinx()
ax1.yaxis.set_ticks_position('right') # 将回撤曲线的 y 轴移至右侧
ax2.yaxis.set_ticks_position('left') # 将累计收益曲线的 y 轴移至左侧
# 绘制回撤曲线
drawdown.plot.area(ax=ax1, label='drawdown (right)', rot=0, alpha=0.3, fontsize=13, grid=False)
# 绘制累计收益曲线
(cumulative).plot(ax=ax2, color='#F1C40F' , lw=3.0, label='cumret (left)', rot=0, fontsize=13, grid=False)
# 不然 x 轴留有空白
ax2.set_xbound(lower=cumulative.index.min(), upper=cumulative.index.max())
# 主轴定位器：每 5 个月显示一个日期：根据具体天数来做排版
ax2.xaxis.set_major_locator(ticker.MultipleLocator(100)) 
# 同时绘制双轴的图例
h1,l1 = ax1.get_legend_handles_labels()
h2,l2 = ax2.get_legend_handles_labels()
plt.legend(h1+h2,l1+l2, fontsize=12, loc='upper left', ncol=1)

fig.tight_layout() # 规整排版
plt.show()
```

