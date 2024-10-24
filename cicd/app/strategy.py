"""
@author: Diem BUI (diem.bui@lxp.lu)
"""

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

from app.tsdata import get_historical_data

class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


def analyse(ticker
        , strategy
        , stdate
        , endate
        , commission = .001
        , exclusive_orders = True):

    """"
    @Param:
        - ticker: (string): equity or forex which are available on market
        - strategy: (string):  instance of Strategy class
        - stdate: (string): start date of analysis
        - endate: (string): end date of analysis
    @Return:
        Return the statistical summary
    """
    data = get_historical_data(ticker, stdate, endate)
    if (strategy == "SMA"):
        bt = Backtest(data
                        , SmaCross
                        , commission=.001
                        , exclusive_orders=True)
        return bt.run()
    return "Unknown"





# test strategy
if __name__ == "__main__":
    '''
    tickers = ['NVDA']
    for tic in tickers:
 
        #from_date = "2000-03-28"
        from_date = "2000-03-28"
        to_date = "2021-09-28"
#       apikey = "6a870124581757224dcaa94c6a54571e"
        data = get_historical_data(tic, from_date, to_date)
        print(data.head())
        print(data.tail())
        print(data.index)
    
        bt = Backtest(data, SmaCross, commission=.001, exclusive_orders=True)
        stats = bt.run()
        print(stats)
    '''
    '''
    # test analyse() function
    from_date = "2000-03-28"
    to_date = "2021-09-28"
    ticker = "GE"
    print(analyse(ticker
                , "SMA"
                , stdate = from_date
                , endate = to_date))
    '''
    data = get_historical_data('GE', '2000-03-28', '2021-09-28')
    #print(data[['Close']].describe())
    bt = Backtest(data
                , SmaCross
                , commission=.001
                , exclusive_orders=True)
    stats = bt.run()
    import pandas as pd
    pd_stats = pd.DataFrame(stats.to_frame())
    print(pd_stats.head())
    





