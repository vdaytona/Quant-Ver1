'''
processing v4 data
Created on 2016/02/25
test the time for closing position
@author: Daytona
'''
# calculate the minute highest and lowest return distribution
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from datetime import timedelta, date, datetime
import pandas as pd
import sys
import time
from pandas.core.series import TimeSeries

raw_year_data = pd.read_csv("./Data/2005-2016_v4.csv").dropna().reset_index(drop = True)
print len(raw_year_data)

average_sell_at_close_return = 0.0
average_sell_at_close_return_win_ratio = 0.0

# calculate average return and win ratio if close position at 2nd close price
win_ratio_close = 0.0
average_return_close = 0.0
for i in range(len(raw_year_data)) :
    close_return = raw_year_data.loc[i].values[-1]
    if close_return > 0 :
        win_ratio_close += 1
    average_return_close += close_return
print ("Win ratio close : %s" %(win_ratio_close / len(raw_year_data)))
print ("average return close : %s" %(average_return_close / len(raw_year_data)))

# calculate the win ratio and return for set sell stop and sell limit
close_time = range(0,240)
win_ratio_matrix = []
average_return_matrix = []
for ct in range(close_time[0]+1,close_time[-1]) :
    print str(close_time.index(ct)) + " of "  + str(len(close_time))
    positive_count = 0.0
    negative_count = 0.0
    positive_success_count = 0.0
    negative_success_count = 0.0
    positive_trade_return = 0.0
    negative_trade_return = 0.0
    positive_win_ratio = 0.0
    negative_win_ratio = 0.0
    positive_average_return = 0.0
    negative_average_return = 0.0
    for i in range(0,len(raw_year_data)) :
        close_return = raw_year_data.loc[i].values[-(240 - ct)]
        if raw_year_data.loc[i].values[-240] >= raw_year_data.loc[i].values[-241] :
            if close_return > 0 :
                positive_success_count += 1
            positive_trade_return += close_return
            positive_count += 1.0
        else :
            if close_return > 0 :
                negative_success_count += 1
            negative_trade_return += close_return
            negative_count += 1.0
    positive_win_ratio = (positive_success_count / positive_count)
    positive_average_return = (positive_trade_return / positive_count)
    negative_win_ratio = (negative_success_count / negative_count)
    negative_average_return = (negative_trade_return / negative_count)
    win_ratio_matrix.append([positive_win_ratio,negative_win_ratio])
    average_return_matrix.append([positive_average_return,negative_average_return])

average_return_matrix = np.asarray(average_return_matrix)
win_ratio_matrix = np.asarray(win_ratio_matrix)
#print average_return_matrix.shape
np.savetxt("./Data/return_v8.csv", average_return_matrix, delimiter=",")
np.savetxt("./Data/win_ratio_v8.csv", win_ratio_matrix, delimiter=",")
print "finished"