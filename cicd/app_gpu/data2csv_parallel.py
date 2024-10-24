"""
@author: Diem BUI (diem.bui@lxp.lu)
"""
from app_gpu.tsdata import save_data2csv
from app_gpu.tsdata import g_datapath
from app_gpu.tsdata import get_historical_data

import os
import concurrent.futures

# Start with 100 assets because of free access limitation to API
# It means we add 100 assets into the porfolio
g_num_ticker = 100
# The path for listing items, for windows
# path = os.getcwd() + os.sep + 'hpcbenchmark' + os.sep + 'data' + os.sep
# path for 

# start with 100 assets because of free access limitation to API
#c_ticker = 5
# The path for listing items
# path = os.getcwd() + os.sep + 'hpcbenchmark' + os.sep + 'data' + os.sep

'''
tickers = get_etfs()
# save 20 years of historical data into csv files
for ticker in tickers[:c_ticker]:
    data = get_historical_data(ticker)
    data.to_csv(path_or_buf = path + ticker + '.csv', index=True, index_label=False)
'''


'''
# testing the data collection 
print(path)
# The list of items
files = os.listdir(path)
print(files)
# Loop to print each filename separately

for filename in files:
    # print the ticker
    print(filename.replace('.csv',''))
    # print the first five lines
    print(pd.read_csv(path + filename).head())
'''


'''
for i in range(c_ticker):
    data = pd.read_csv('/data')
'''

"""
data = pd.read_csv('data/MSFT.csv')
print(data.head())
print(data.index)
print(len(data))
"""
# We can use a with statement to ensure threads are cleaned up promptly

    # this function is called only once
'''
tickers = get_etfs()
tickers = tickers[:2]
print(f"number of tickers {len(tickers)}")
with concurrent.futures.ThreadPoolExecutor(max_workers=128) as executor:
    # Start the load operations and mark each future with its URL
    # save 20 years of historical data into csv files
    [executor.submit(save_data2csv, ticker) for ticker in tickers]
'''

'''
import pandas as pd
import os

data = pd.read_csv(os.getcwd() + os.sep + 'hpcbenchmark' + os.sep + 'data' + os.sep + 'AAPL.csv')
data.index = pd.to_datetime(data.index)
print(data.columns)
print(type(data.index))
print(data.index)
'''

from app_gpu.tsdata import get_etfs
#tickers = get_etfs()
tickers = get_etfs()

with concurrent.futures.ThreadPoolExecutor(max_workers=128) as executor:

    future_to_data = {executor.submit(save_data2csv, ticker): ticker for ticker in tickers}  
    for future in future_to_data:
        future.result()


