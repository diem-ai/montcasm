"""
@author: Diem BUI (diem.bui@lxp.lu)

Run Monte Carlo Simulation on 1 GPU node

"""
from app.tsdata import get_historical_data
from app.tsdata import read_csv
from app.tsdata import save_data2csv
from app.tsdata import get_etfs
from app.tsdata import get_csv_files
from app.parameters import g_datapath, g_outputpath, g_simulation
from app.backtestsim import run_backtest
from app.backtestsim import run_monte_carlo_simulation

import concurrent.futures
import os
import multiprocessing
from multiprocessing import Process, Queue, current_process, freeze_support
import time

# start counting when the process is started
start_time = time.time()
filenames =  get_csv_files()
futures_to_backtest = []
futures_to_sim = []


with concurrent.futures.ProcessPoolExecutor(multiprocessing.cpu_count()) as executor:
    for fname in filenames:
        ticker = fname.replace('.csv','')
        #executor.map(run_sim, ticker)
        data = read_csv(ticker, g_datapath)
        #print(g_datapath)
        executor.submit(run_backtest, data, ticker, g_outputpath)
        #executor.submit(run_monte_carlo_simulation, data, ticker)
        #futures_to_backtest.append(executor.submit(run_backtest, data, ticker))
        futures_to_sim.append(executor.submit(run_monte_carlo_simulation, data, ticker, g_simulation, g_outputpath))
        #freeze_support()
    for future in concurrent.futures.as_completed(futures_to_sim):
        # do nothing
        continue
        #print(future.result())

# start counting when process is finished
end_time = time.time()
#print(f"{(end_time - start_time)}")
print(f"{(end_time - start_time)/3600}")

# clean the output folder
import glob, os
files = [x for x in glob.glob(g_outputpath + "*") if (x.endswith(".txt") or x.endswith(".png") or x.endswith(".html"))]
for f in files:
    os.remove(f)