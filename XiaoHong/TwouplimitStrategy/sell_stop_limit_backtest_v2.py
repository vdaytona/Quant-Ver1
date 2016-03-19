'''
Created on 2016/02/25

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

raw_year_data = pd.read_csv("./Data/2005-2016.csv")
print len(raw_year_data)
#===============================================================================
# start_date = datetime.strptime("01 01 2005" , "%d %m %Y")
# end_date = datetime.strptime("01 01 2005" , "%d %m %Y")
# raw_year_data = raw_year_data[raw_year_data["Buy_date"] >= start_date]
# raw_year_data = raw_year_data[raw_year_data["Buy_date"] <= end_date]
#===============================================================================
# Highest return and lowest return appearing in trading

high = []
low = []
for i in range(len(raw_year_data)) :
    high.append(raw_year_data.loc[i][3:].max())
    low.append(raw_year_data.loc[i][3:].min())

#===============================================================================
# plt.hist(high, bins=50, normed=True)
# plt.title("Highest return appearing in trading")
# plt.show()
# plt.hist(low, bins=50, normed=True)
# plt.title("Lowest return appearing in trading")
# plt.show()
# plt.scatter(high, low)
# plt.xlabel("Highest return appearing in trading")
# plt.ylabel("Lowest return appearing in trading")
# plt.title("Highest vs lowest return appearing in trading")
# plt.show()
#===============================================================================




##############################################
sl_list = []
st_list = []
for selllimit in range(0, int(max(high)*1000) + 20 , 10) :
    sl = selllimit / 1000.0
    sl_list.append(sl)

for sellstop in range(0, int(abs(min(low))*1000) + 20 , 10) :
    st = (sellstop / 1000.0) * -1
    st_list.append(st)

print sl_list

win_ratio_matrix = []

average_return_matrix = []
average_sell_at_close_return = 0.0
average_sell_at_close_return_win_ratio = 0.0

# calculate average return and win ratio if close position at 2nd close price
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
print "sl_list " + str(len(sl_list))
print "st_list " + str(len(st_list))
for sl in sl_list :
    #l = sl_list[i]
    average_return_list = []
    win_ratio_list = []
    for st in st_list :
        print str(sl) +  "  " + str(st)
        #t = st_list[i]
        success_count = 0.0
        loss_count = 0.0
        trade_return = 0.0
        failed_count = 0.0
        for i in range(len(raw_year_data)) :
            difference = len(raw_year_data.loc[i]) - len(raw_year_data.loc[i].dropna())
            # if no enough data , it may paused in the 2nd day, so delete at present
            if difference >= 240 :
                failed_count += 1
                continue
            # choose the data for the 2nd day
            time_series = raw_year_data.loc[i].dropna()[-240:]
            
            if time_series[0] < sl or time_series[0] > st :
                # if 2nd day open do not hit sl or st
                if time_series.max() >= sl and time_series.min() > st :
                    # if max value > stop limit and min value > sell stop, close position at sell limit
                    success_count += 1
                    trade_return += sl
                    continue
                elif time_series.max() < sl and time_series.min() <= st :
                    # if max value < stop limit and min value < sell stop, close position at sell stop
                    loss_count += 1
                    trade_return += st
                    continue
                else :
                    # iterate each value to find if hit sl or st first
                    for j in range(len(time_series)) :
                        if time_series[j] >= sl and j != len(time_series) -1:
                            success_count += 1
                            trade_return += sl
                            break
                        elif time_series[j] <= st and j != len(time_series) -1:
                            loss_count += 1
                            trade_return += st
                            break
                        elif time_series[-1] >= 0 and j == len(time_series) -1 :
                            success_count += 1
                            trade_return += time_series[-1]
                        elif time_series[-1] <= 0  and j == len(time_series) -1 :
                            loss_count += 1
                            trade_return += time_series[-1]                            
                    continue
            elif time_series[0] >= 0 :
                # if 2nd open is already hit sl or st
                success_count += 1
                trade_return += time_series[0]
            else :
                loss_count += 1
                trade_return += time_series[0]
        trade_count = len(raw_year_data) - failed_count
        win_ratio_list.append(success_count / trade_count)
        average_return_list.append(trade_return / trade_count)
    win_ratio_matrix.append(win_ratio_list)
    average_return_matrix.append(average_return_list)


sl_list, st_list = np.meshgrid(sl_list, st_list)
#print sl_list.shape
#print st_list.shape
average_return_matrix = np.asarray(average_return_matrix)
average_return_matrix = np.transpose(average_return_matrix)
win_ratio_matrix = np.asarray(win_ratio_matrix)
win_ratio_matrix = np.transpose(win_ratio_matrix)
#print average_return_matrix.shape
np.savetxt("./Data/sl.csv", sl_list, delimiter=",")
np.savetxt("./Data/st.csv", st_list, delimiter=",")
np.savetxt("./Data/return_v2.csv", average_return_matrix, delimiter=",")
np.savetxt("./Data/win_ratio_v2.csv", win_ratio_matrix, delimiter=",")
print "finished"
    

#from mpl_toolkits.mplot3d import Axes3D
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
# surf = ax.plot_surface(sl_list, st_list, average_return_matrix, rstride=1, cstride=1, cmap=cm.coolwarm,
#                        linewidth=0, antialiased=False)
# 
# ax.zaxis.set_major_locator(LinearLocator(10))
# ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
# 
# fig.colorbar(surf, shrink=0.5, aspect=5)
# 
# plt.show()
#===============================================================================