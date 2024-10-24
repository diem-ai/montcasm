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

from app import montecarlo as mc
from app import backtestsim as bts
from app import strategy as stra
from app.strategy import  SmaCross
from app import tsdata 
from app.tsdata import get_csv_files, read_csv

from tests.testparam import t_datapath, t_outputpath, t_simulation
import random as rd
from app.backtestsim import run_backtest, run_monte_carlo_simulation, run_sim
from tests.testparam import t_outputpath

def test_run_sim():
    # Calculate the start time of simulation
    start = time.time()
    filenames = get_csv_files(datapath=t_datapath)

    for fname in filenames:
        ticker = fname.replace('.csv','')
        #executor.map(run_sim, ticker)
        data = read_csv(ticker, t_datapath)
        bts.run_sim(ticker, t_datapath, t_outputpath, t_simulation)

    # check files exisiting in output folder
    # we expect 3 files * number of ticker in data folder: html, txt and png
    files = [x for x in glob.glob(t_outputpath + "*") if (x.endswith(".txt") or x.endswith(".png") or x.endswith(".html"))]
    status = 0
    if (len(files) == len(filenames)*3):
        status = 0
    else:
        status = 1
    # Calculate the time at the end of simulation
    end = time.time()
    usedtime = int(np.round( (end - start)/60))
    # clean this folder after the completion
    for f in files:
        os.remove(f)

    # print out the run time
    print(f"{usedtime} (minutes), status={status}" )
    #print(status)
    assert (status==0)
    # the execution time shouldn't be more than 5 mins
    assert (usedtime <= 5)


def test_run_monte_carlo_simulation_without_plot():
    # create a dataframe
    data = pd.DataFrame(data={'Close': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Open': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Low': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15] 
                             , 'High': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Date': pd.date_range("2020-01-01", periods=10, freq="D")} )
    run_monte_carlo_simulation(data, "TEST_TICKER", 3, t_outputpath, plot=False)


def test_run_monte_carlo_simulation_with_plot():
   
    data = pd.DataFrame(data={'Close': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Open': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Low': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15] 
                             , 'High': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Date': pd.date_range("2020-01-01", periods=10, freq="D")})       
        
    run_monte_carlo_simulation(data, "TEST_TICKER", 3, t_outputpath, plot=True)
    
    plotfiles = [x for x in glob.glob(t_outputpath + "*") if (x.endswith(".png") )]
    assert(len(plotfiles) == 1)
    for file in plotfiles:
        os.remove(file)


def test_run_backtest_with_plot():
    # create a dataframe
    data = pd.DataFrame(data={'Close': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Open': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Low': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15] 
                             , 'High': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Date': pd.date_range("2020-01-01", periods=10, freq="D")} )
    run_backtest(data, 'TEST_TICKET', t_outputpath, plot=True)

    statsfiles = [x for x in glob.glob(t_outputpath + "*") if (x.endswith(".txt") )]
    assert(len(statsfiles) == 1)
    htmlfiles = [x for x in glob.glob(t_outputpath + "*") if (x.endswith(".html") )]
    assert(len(htmlfiles) == 1) 

    for file1, file2 in zip(statsfiles, htmlfiles):
        os.remove(file1)
        os.remove(file2)


def test_run_backtest_without_plot():
    # create a dataframe
    data = pd.DataFrame(data={'Close': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Open': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Low': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15] 
                             , 'High': [10, 12, 14,  9,  8, 11, 16, 13, 10, 15]
                             , 'Date': pd.date_range("2020-01-01", periods=10, freq="D")} )
    run_backtest(data, 'TEST_TICKET', t_outputpath, plot=False)
    
    statsfiles = [x for x in glob.glob(t_outputpath + "*") if (x.endswith(".txt") )]
    assert(len(statsfiles) == 1) 
    for file in statsfiles:
        os.remove(file)


if __name__=="__main__":
    test_run_sim()
    test_run_backtest_without_plot()
    test_run_backtest_with_plot()
    test_run_monte_carlo_simulation_with_plot()
    test_run_monte_carlo_simulation_without_plot()