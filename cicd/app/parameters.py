"""
@author: Diem BUI (diem.bui@lxp.lu)
"""

import os
'''
Default parameters backtest on trading strategy
'''
# start date
g_stdate = "2000-03-28"
# end date
g_endate = "2021-12-28"
'''
Default parameters of backtest for Monte Carlo Simulation
'''
g_test_size = 0.33
# 100.000
g_simulation = 100000
#g_simulation = 1000
g_simulation_start = 100
g_simulation_delta = 100

g_datapath = os.getcwd() + os.sep + 'data' + os.sep
g_outputpath = os.getcwd() + os.sep + 'output' + os.sep
