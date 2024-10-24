"""
- @author: Diem BUI (diem.bui@lxp.lu)
- This file delicates to HPC benchmark test
"""
import app.tsdata
from app.tsdata import get_historical_data
from app.tsdata import get_etfs
from app.tsdata import read_csv
from app.parameters import g_datapath, g_outputpath, g_simulation
from app.strategy import SmaCross
from app.montecarlo import monte_carlo
from app.montecarlo import plot as mcplot

import time
from datetime import datetime
import matplotlib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA


def run_backtest(data
                , ticker
                , outputpath):
    # data = get_historical_data(ticker, g_stdate, g_endate )
    bt = Backtest(data, SmaCross)
    stats = bt.run()
    with open(outputpath + ticker + '_stats_' + str(time.time()) + '.txt', 'w') as file:
        file.write(stats.to_string())
    bt.plot(filename = outputpath + ticker + '_' + str(time.time()), open_browser=False)

def run_monte_carlo_simulation(data
                            , ticker
                            , simulation
                            , outputpath):
    predictions, pickers = monte_carlo(data, simulation)    
    mcplot(data,  predictions, pickers, ticker, outputpath)


def run_sim(ticker
            , datapath = g_datapath
            , outputpath =g_outputpath
            , simulation = g_simulation):

    data = read_csv(ticker, datapath)
    run_backtest(data, ticker, outputpath)
    run_monte_carlo_simulation(data, ticker, simulation, outputpath)

"""
def run_sim(ticker, simulation = g_simulation):
    data = read_csv(ticker)
    run_backtest(data, ticker)
    run_monte_carlo_simulation(data, ticker, simulation)
"""

