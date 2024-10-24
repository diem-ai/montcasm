"""
@author: Diem BUI (diem.bui@lxp.lu)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import ssl
import time
from datetime import datetime
import os
#import numba
#from numba import jit, prange, cuda
import matplotlib
from backtesting import Backtest

from app_gpu.strategy import SmaCross
import app_gpu.parameters
from app_gpu.parameters import g_datapath, g_outputpath
from app_gpu.tsdata import get_historical_data

#numba.cuda.select_device(0)

ssl._create_default_https_context = ssl._create_unverified_context

#@cuda.jit
def zscore_return_values(price):
    """Calulate the return value of assets on stock market.
    returns = (price(t) - price(t-1))/price(t-1)
    """
    returns = price.pct_change()
    # Normalise Return value with z-score
    scaled_returns = (returns - returns.mean())/returns.std()
    return scaled_returns.to_frame().rename(columns={'Close': 'Scaled_Return'})

'''
def f_log_return_value(np_price):
    """Calulate the return value of assets on stock market.
    returns = (price(t) - price(t-1))/price(t-1)
    """
    next_price = np_price[1:]
    # this step is like series.shift(1).iloc[1:]
    next_shift_price = np.append(np.NAN, np_price[:-1])[1:]
    return np.log(next_price/next_shift_price)
'''
    
@guvectorize([(float64[:], float64[:])], '(n)->(n)')
def f_log_return_value(np_price, lg_price):
    """Calulate the return value of assets on stock market.
    returns = (price(t) - price(t-1))/price(t-1)
    """
    next_price = np_price[1:]
    # this step is like series.shift(1).iloc[1:]
    next_shift_price = np.append(np.NaN, np_price[:-1])[1:]
    lg_price[:-1] = np.log(next_price/next_shift_price)
    
@guvectorize([(float64[:], float64[:])], '(n) -> ()')
def f_get_drift_rate(np_returns, drift_rate):
    """
    Drift rate is the risk-free interest rate.
    It is calculated using the standard deviation to measure stock's volatility.
    """
    drift_rate[0] = (np.mean(np_returns) - np.var(np_returns)/2)

'''
def f_get_drift_rate(np_returns):
    """
    Drift rate is the risk-free interest rate.
    It is calculated using the standard deviation to measure stock's volatility.
    """
    return np.mean(np_returns) - np.var(np_returns)/2
'''

#@cuda.jit
def f_get_best_fit(simulation, prediction, np_price):
    """
    # we use simple criterias, the smallest standard deviation
    # we iterate through every simulation and compare it with actual data
    # The winners are the ones with minimum standard deviation.
    """
    std = np.finfo(np.float64).max
    pickers = {}
    for c_sim in range(simulation):
        temp = np.std(np.subtract(prediction[c_sim], np_price))
        if (std > temp):
            std = temp
            pickers = {c_sim: std}
    return pickers

@guvectorize([(float64[:], float64, float64, float64[:])], '(n),(),() -> ()')
def f_forecast_price(np_returns, np_drift_rate, current_price, simulated_price):
    """
    Forecast the future prices with Geometric_Brownian_motion.
    The mathematical expression is taken from this article: https://corpgov.law.harvard.edu/2019/08/18/making-sense-of-monte-carlo
    """
    # Calculate normally distributed random variable
    zscore =  rd.gauss(0,1)
    # Calculate stochastic differential equation (SDE)
    np_sde = np_drift_rate + ( np.std(np_returns) * zscore )
    # Calculate simulated future stock price in the the future.
    simulated_price = current_price * np.exp(np_sde)

'''
def f_forecast_price(np_returns, np_drift_rate, current_price):
    """
    Forecast the future prices with Geometric_Brownian_motion.
    The mathematical expression is taken from this article: https://corpgov.law.harvard.edu/2019/08/18/making-sense-of-monte-carlo/
    """
    # Calculate normally distributed random variable
    zscore =  rd.gauss(0,1)
    # Calculate stochastic differential equation (SDE)
    #print(f"zscore {zscore}")
    np_sde = np_drift_rate + ( np.std(np_returns) * zscore )
    #print(f"np_sde {np_sde}")
    # Calculate simulated future stock price in the the future.
    simulated_price = current_price * np.exp(np_sde)
    return simulated_price
'''

#@cuda.jit
def f_gbm_simulation(np_price):
    """
    Simulate the future prices with Geometric_Brownian_motion (https://en.wikipedia.org/wiki/Geometric_Brownian_motion)
    """
    np_returns = f_log_return_value(np_price)
    #print(f"np_returns {np_returns}")
    np_drift_rate = f_get_drift_rate(np_returns)
    #print(f"np_drift_rate {np_drift_rate}")

    prediction = []
    prediction.append(np_price[0])
    for idx in prange(len(np_price) - 1):
        simulated_price = f_forecast_price(np_returns, np_drift_rate, prediction[-1])
        #print(f"simulated_price {simulated_price}")
        prediction.append(simulated_price)

    return prediction

#@cuda.jit
def f_monte_carlo(np_price, simulation):
    """
    We construct a model to get mean and variance of its residual (return).
    We forcast the future price using Geometric_Brownian_motion (GBM) with drift rate.
    We calculate the output of MC Simulation using Geometric_Brownian_motion (GBM) with drift rate and determine the best fit along with its standard deviation error.
    The pseudo random number is generated via empirical distribution.
    We run this simulations as n times. The more , the better according to the Law of Large Number (https://en.wikipedia.org/wiki/Law_of_large_numbers)
    We pick the forecast that has the least standard deviation against the original Close prices
    we would check if the best forecast can predict the future direction (instead of actual price) and how well monte carlo catches black swans
    What is GBM? checkout the link: https://en.wikipedia.org/wiki/Geometric_Brownian_motion
    What are the dirft rate with GMB and its formula? checkout this link: https://corpgov.law.harvard.edu/2019/08/18/making-sense-of-monte-carlo/
    """
    
    prediction = {}
    for c_sim in prange(simulation):
        #we only care about close price, if there has been dividend issued, we use adjusted close price instead
        prediction[c_sim] = f_gbm_simulation(np_price)
    # Determine the best fitted simulation wit minimum standard deviation
    pickers = f_get_best_fit(simulation, prediction, np_price)
    return prediction, pickers

#@cuda.jit
def monte_carlo(data, simulation):
    """
    - Convert dataframe into numpy before vectorization.
    - Return the list of forcasting prices and the best fitted simulation.
    """
    np_price = data.Close.to_numpy()
    return f_monte_carlo(np_price, simulation)

# In[4]:
#@cuda.jit
def plot(data, prediction, pickers , ticker, outputpath):
    ax = plt.figure(figsize=(15,5)).add_subplot(111)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis="x", which="both", length=4)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("\n%Y"))
    ax.xaxis.set_minor_locator(matplotlib.dates.MonthLocator((1)))
    ax.xaxis.set_major_locator(matplotlib.dates.YearLocator())
    for i in range(len(prediction)):
        if i not in pickers:
            ax.plot(data.index
                    , prediction[i]
                    , linestyle='-'
                    , alpha=0.05
                    , color='cyan'
                    , linewidth=1)
        else:
            label = "sim="+str(i) + ", std=" + str(np.round(pickers[i], 2)) + "%"
            ax.plot(data.index
                    , prediction[i]
                    , label='Best Fitted (' + label + ')'
                    , linestyle='-'
                    #, color='blue'
                    , linewidth=3)

    data.Close.plot(label = 'Close Price'
                        , linewidth = 2
                        , linestyle='--'
                        , color='red')

    # Add one plot for return value
    #
    #

    plt.title(f'Monte Carlo Simulation\nAsset: {ticker}')
    plt.legend(loc=0)
    plt.ylabel('Close Price')
    plt.xlabel('Pricing Date')
    plt.savefig(outputpath + ticker + '_' +  str(time.time()) + '.png')
