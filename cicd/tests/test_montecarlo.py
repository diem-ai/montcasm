"""
@author: Diem BUI (diem.bui@lxp.lu)
"""

import glob
import os
import time
import numpy as np
import random as rd

from app import montecarlo as mc
from app import backtestsim as bts
from app import strategy as stra
from app.strategy import SmaCross
from app import tsdata
from app.tsdata import get_csv_files, read_csv

from tests.testparam import t_datapath, t_outputpath, t_simulation


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
