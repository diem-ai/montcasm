"""
@author: Diem BUI (diem.bui@lxp.lu)
"""

import pandas as pd
import ssl
import os
from os.path import exists
import time
import glob


from app_gpu.parameters import g_stdate, g_endate, g_datapath

#from strategy import SmaCross

ssl._create_default_https_context = ssl._create_unverified_context
#apikey = "6a870124581757224dcaa94c6a54571e"
apikey = "5f416ec1d55c1e141c18428aceeabde2"
historical_url = "https://fmpcloud.io/api/v3/historical-price-full"
etf_url = "https://fmpcloud.io/api/v3/etf-holder/SPY?apikey=" + apikey



def get_etfs():
    """
    Retrieve all the ETFs holder currently available
    """
    data = pd.read_json(etf_url)
    return data
    #return data.asset[:g_num_ticker]

def get_historical_data(ticker, 
                        stdate = g_stdate, 
                        endate = g_endate):
    """
    - Send request to fmpcloud and receive historical transactions of assets (ticker)
    """
#    print(ticker)
    request = historical_url + "/" + ticker + "?from=" + stdate + "&to=" + endate + "&apikey=" + apikey
#    print(request)
    try:
        data = pd.read_json(request)
        date = []
        open = []
        low = []
        high = []
        close = []
        volume = []
        for row in data.historical:
            #print(row)
            date.append(row['date'])
            open.append(row['open'])
            low.append(row['low'])
            high.append(row['high'])
            close.append(row['close'])
            volume.append(row['volume'])
        data = dict({'Open': open,
                    "Low": low,
                    "High": high,
                    'Close': close,
                    "Volume": volume})
        data  = pd.DataFrame(data, index=date)
        data.index = pd.to_datetime(data.index) 
        return data.sort_index (ascending = True )
    except Exception as exc:
        print(f'Error in retrieving data: {exc}')
    return None

def save_data2csv(ticker):
    """
    Check the file exists, do nothing.
    Otherwise, retrieve historical data and save it to csv files.
    """
    filename = g_datapath + ticker + '.csv'
    print(f"file name: {filename}")
    if (not exists(filename)):
        print(f"{filename} is not existed. Start retreiving historical data..")
        data = get_historical_data(ticker)
        data.to_csv(filename, index=True, index_label=False)
    else:
        print(f"{filename} is already existed.")

def read_csv(ticker, datapath = g_datapath):
    data = pd.read_csv(datapath + ticker + '.csv')
    data.index = pd.to_datetime(data.index)
    ##data = dd.from_pandas(data, npartitions=2)
    return data

def get_csv_files(datapath = g_datapath):
    filenames  = os.listdir(datapath)
    return [fname for fname in filenames if fname.endswith('.csv')]

def read_all_files():
    files = get_csv_files()
    # Loop to print each filename separately
    for filename in files:
        # print the ticker
        ticker, data =  read_csv(filename, g_datapath)
#        print(f"ticker: {ticker}")
#        print(f"first five lines : {data.head()}")



if __name__=="__main__":
    print(__file__)