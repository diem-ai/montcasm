"""
@author: Diem BUI (diem.bui@lxp.lu)
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime
import glob
import os
import time
import numpy as np
import sys
from  pathlib import Path
from backtesting import Backtest, Strategy

#sys.path.insert(0, os.getcwd() + os.sep + 'app')
#sys.path.insert(1, os.getcwd() + os.sep + 'test')
from app import montecarlo as mc
from app import backtestsim as bts
from app import strategy as stra
from app.strategy import  SmaCross
from app import tsdata 
from app.tsdata import get_csv_files, read_csv

from tests.testparam import t_datapath, t_outputpath, t_simulation
import random as rd
from app.montecarlo import f_get_drift_rate, f_log_return_value, f_get_best_fit, f_forecast_price, f_gbm_simulation, f_monte_carlo

def test_drift_rate():
    returns = [1, 2, 5, 7, 4]
    drift_rate = f_get_drift_rate(returns)
    assert(drift_rate > 0)
    assert(drift_rate < np.mean(returns))
    assert(drift_rate==1.5199999999999996)

def test_log_return_value():
    prices = [10, 12, 14, 13, 9, 8]
    lg_returns = f_log_return_value(prices)
    assert(len(lg_returns) == len(prices)-1)
    assert(np.array_equal(lg_returns, prices[1:]) == False)

def test_get_best_fit():
    # number of simulation
    simulation  = 3
    prices      = [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
    predictions = []
    prediction1 = [13, 10, 11, 13, 10, 15, 15, 10, 13, 13]
    prediction2 = [15, 6, 34, 5, 3, 7, 3, 10, 9, 8]
    prediction3 = [20, 35, 78, 14, 8, 16, 19, 25, 19, 18]
    predictions.append(prediction1)
    predictions.append(prediction2)
    predictions.append(prediction3)
    best_fit = f_get_best_fit(simulation, predictions, prices)

    assert(simulation == len(predictions))
    assert(len(prediction3) == len(prediction2) == len(prediction1) == len(prices))
    assert(len(best_fit) == 1)


def test_forecast_price():
    # First price at selected time.
    price = 15
    returns = [0.18232156
                , 0.15415068
                , -0.44183275
                , -0.11778304
                , 0.31845373
                , 0.37469345
                , -0.20763936 
                , -0.26236426
                , 0.40546511]
    drift_rate = 0.02
    simulated_price = f_forecast_price(returns, drift_rate, price)
    # assert the max and the min possible simulated price
    assert (simulated_price <= price + price*drift_rate + np.std(returns))
    assert (simulated_price >= price - price*drift_rate - np.std(returns))

def test_gbm_simulation():
    prices = [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
    predictions = f_gbm_simulation(prices)
    assert(len(prices) == len(predictions))

def test_monte_carlo():

    prices = [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
    simulation = 3
    predictions, pickers = f_monte_carlo(prices, simulation)
    assert(len(predictions)==simulation)
    assert(len(pickers)==1)
    for i in range(len(predictions)):
        assert(len(prices) == len(predictions[i]))
    
def test_mc_stats():
    start = time.time()

    t_datapath = 'tests/data/'
    filename = 'AAPL_500_initial.csv'

    ticker = filename.replace('.csv', '')
    data = read_csv(ticker, t_datapath)

    simulation = 100
    rd.seed(42)
    predictions, pickers = mc.monte_carlo(data, simulation)
    assert len(predictions) == simulation

    tolerance = 1e-6
    last_points = [predictions[i][:-1] for i in range(simulation)]
    assert np.isclose(0.7028484, np.mean(last_points), tolerance)
    assert np.isclose(0.5070332, np.std(last_points), tolerance)
    assert np.isclose(0.1293435, pickers[62], tolerance)

if __name__=="__main__":
    test_drift_rate()
    test_log_return_value()
    test_mc_stats()
    test_get_best_fit()
    test_forecast_price()
    test_gbm_simulation()
    test_monte_carlo()

    



