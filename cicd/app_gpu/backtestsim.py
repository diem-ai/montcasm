"""
- @author: Diem BUI (diem.bui@lxp.lu)
- This file delicates to HPC benchmark test
"""
import app_gpu.tsdata
from app_gpu.tsdata import get_historical_data
from app_gpu.tsdata import get_etfs
from app_gpu.tsdata import read_csv
from app_gpu.parameters import g_datapath, g_outputpath, g_simulation
from app_gpu.strategy import SmaCross
from app_gpu.montecarlo import monte_carlo
from app_gpu.montecarlo import plot as mcplot

#from numba import jit, prange, cuda

import time
from datetime import datetime
import matplotlib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

#@cuda.jit
def run_backtest(data, ticker, output_path, plot=True):
    # data = get_historical_data(ticker, g_stdate, g_endate )
    bt = Backtest(data, SmaCross)
    stats = bt.run()
    with open(output_path + ticker + '_stats_' + str(time.time()) + '.txt', 'w') as file:
        file.write(stats.to_csv())
    if plot:
        bt.plot(filename=output_path + ticker + '_' +
                str(time.time()), open_browser=False)

#@cuda.jit
def run_monte_carlo_simulation(data, ticker, simulation, output_path, plot=True):
    predictions, pickers = monte_carlo(data, simulation)    
    if plot:
        mcplot(data,  predictions, pickers, ticker, output_path)

#@cuda.jit
def run_sim(ticker, datapath=g_datapath, output_path=g_outputpath, simulation=g_simulation, plot=True):
    data = read_csv(ticker, datapath)
    run_backtest(data, ticker, output_path, plot)
    run_monte_carlo_simulation(data, ticker, simulation, output_path, plot)


"""
def run_sim(ticker, simulation = g_simulation):
    data = read_csv(ticker)
    run_backtest(data, ticker)
    run_monte_carlo_simulation(data, ticker, simulation)
"""
