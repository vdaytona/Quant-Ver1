'''
Created on 2016/02/25

@author: Daytona
'''
# calculate the minute highest and lowest return distribution
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from datetime import timedelta
import pandas as pd
import sys
import time
from copy import deepcopy

raw_year_data = pd.read_csv("2005-2016.csv")
print len(raw_year_data)
# Highest return and lowest return appearing in trading

high = []
low = []
for i in range(len(raw_year_data)) :
    high.append(raw_year_data.loc[i][3:].max())
    low.append(raw_year_data.loc[i][3:].min())
    

sl_list = []
trace_st_list = []
for selllimit in range(0, int(max(high)*1000) , 20) :
    sl = selllimit / 1000.0
    sl_list.append(sl)

for sellstop in range(0, int(abs(min(low))*1000) , 20) :
    st = (sellstop / 1000.0) * -1
    trace_st_list.append(st)

start_moving_sell_stop = 0.05
tracking_sell_stop = 0.05
moving_step = 0.02
moving_threhold = 0.04
win_ratio_matrix = []

average_return_matrix = []
average_sell_at_close_return = 0.0
average_sell_at_close_return_win_ratio = 0.0

# calculate averaae return and win ratio if close position at 2nd close price
win_ratio_close = 0.0
average_return_close = 0.0
for i in range(len(raw_year_data)) :
    time_series = raw_year_data.loc[i][3:].dropna()
    close_return = time_series[-1]
    if close_return > 0 :
        win_ratio_close += 1
    average_return_close += close_return
print ("Win ratio close : %s" %(win_ratio_close / len(raw_year_data)))
print ("average return close : %s" %(average_return_close / len(raw_year_data)))
        

# calculate the win ratio and return for set sell stop and sell limit
win_count_list = []
average_return_list = []
for tracking_sell_stop in range(2, 8 , 1):
    tracking_sell_stop = tracking_sell_stop / 100.0
    win_count = 0.0
    no_count = 0.0
    average_return = 0.0
    print tracking_sell_stop
    for i in range(len(raw_year_data)) :
        # find the start of second day
        difference = len(raw_year_data.loc[i]) - len(raw_year_data.loc[i].dropna())
        #print difference
        if difference >= 240 :
            no_count += 1
            continue
        #print i 
        sell_stop = raw_year_data.loc[i][3 + 240 -difference] - tracking_sell_stop
        for j in range( 3 + 240 - difference , len(raw_year_data.loc[i].dropna())) :
            if sell_stop  < raw_year_data.loc[i][j] - tracking_sell_stop :
                sell_stop = raw_year_data.loc[i][j] - tracking_sell_stop
                
            #print str(sell_stop) + "  " + str(raw_year_data.loc[i][j])
            # first check if hit sell stop or if close time
            if raw_year_data.loc[i][j] <= sell_stop or j == len(raw_year_data.loc[i][3:].dropna()) - 1:
                if sell_stop >= 0 or raw_year_data.loc[i][3:].dropna()[-1] >= 0:
                    win_count += 1
                average_return += sell_stop
                break
    win_count_list.append(win_count / (len(raw_year_data) - no_count))
    average_return_list.append(average_return / (len(raw_year_data) - no_count))
print win_count_list
print average_return_list
    
#===============================================================================
# 
# for sl in sl_list :
#     #l = sl_list[i]
#     average_return_list = []
#     win_ratio_list = []
#     for st in trace_st_list :
#         print str(sl) +  "  " + str(st)
#         #t = trace_st_list[i]
#         success_count = 0.0
#         fail_count = 0.0
#         trade_return = 0.0
#         for i in range(len(raw_year_data)) :
#             # lower than sell stop, fail
#             time_series = raw_year_data.loc[i][3:].dropna()
#             if time_series.max() >= sl and time_series.min() > st :
#                 # if max value > stop limit and min value > sell stop, close positio at sell limit
#                 success_count += 1
#                 trade_return += sl
#             elif time_series.max() < sl and time_series.min() <= st :
#                 # if max value < stop limit and min value < sell stop, close position at sell stop
#                 fail_count += 1
#                 trade_return += st
#             elif time_series.max() < sl and time_series.min() > st :
#                 # if no hit on sell limit or sell stop, close position at 2and day close price
#                 if  time_series[-1] < 0 :
#                     fail_count += 1
#                 else :
#                     success_count += 1
#                 trade_return += time_series[-1]
#             else :
#                 # iterate each value to find if hit sl or st first
#                 for j in range(3 , len(raw_year_data.loc[i].dropna())) :
#                     if raw_year_data.loc[i][j] >= sl :
#                             success_count += 1
#                             trade_return += sl
#                             break
#                     elif raw_year_data.loc[i][j] <= st:
#                             fail_count += 1
#                             trade_return += st
#                             break
#         win_ratio_list.append(success_count / (success_count + fail_count))
#         average_return_list.append(trade_return / len(raw_year_data))
#     win_ratio_matrix.append(win_ratio_list)
#     average_return_matrix.append(average_return_list)
# 
# 
# sl_list, trace_st_list = np.meshgrid(sl_list, trace_st_list)
# #print sl_list.shape
# #print trace_st_list.shape
# average_return_matrix = np.asarray(average_return_matrix)
# average_return_matrix = np.transpose(average_return_matrix)
# win_ratio_matrix = np.asarray(win_ratio_matrix)
# win_ratio_matrix = np.transpose(win_ratio_matrix)
# #print average_return_matrix.shape
# np.savetxt("sl.csv", sl_list, delimiter=",")
# np.savetxt("st.csv", trace_st_list, delimiter=",")
# np.savetxt("return.csv", average_return_matrix, delimiter=",")
# np.savetxt("win_ratio.csv", win_ratio_matrix, delimiter=",")
# print "finished"
#===============================================================================
    
#===============================================================================
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib import cm
# from matplotlib.ticker import LinearLocator, FormatStrFormatter
# import matplotlib.pyplot as plt
# import numpy as np
# 
# fig = plt.figure()
# ax = fig.gca(projection='3d')
# #X = np.arange(-5, 5, 0.25)
# #Y = np.arange(-5, 5, 0.25)
# #X, Y = np.meshgrid(X, Y)
# #R = np.sqrt(X**2 + Y**2)
# #Z = np.sin(R)
# surf = ax.plot_surface(sl_list, trace_st_list, average_return_matrix, rstride=1, cstride=1, cmap=cm.coolwarm,
#                        linewidth=0, antialiased=False)
# 
# ax.zaxis.set_major_locator(LinearLocator(10))
# ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
# 
# fig.colorbar(surf, shrink=0.5, aspect=5)
# 
# plt.show()
#===============================================================================