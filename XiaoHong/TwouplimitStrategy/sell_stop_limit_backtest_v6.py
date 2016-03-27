'''
Created on 2016/02/25

processing v2 data
5.2 advanced sell strategy
    if D+1 open / D close > 1.04
        sell at open price D+1
    if D+1 open / D close < 1.04
        sell at close price D+1 or using sell limit and stop
    if D+1 open / D close >= 1.099
        uplimit condition:
        sell when uplimit is broken or keep onto D+2 and repeat (!!!since no additional date data, sell at close price,
        not relized in this code)

@author: Daytona
'''
# calculate the minute highest and lowest return distribution
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from datetime import timedelta, date, datetime
import pandas as pd
from pandas.core.series import TimeSeries
import copy

raw_data = pd.read_csv("./Data/2005-2016_v2.csv").dropna()
print len(raw_data)
#date_list = ["2005/01/01","2006/01/01","2007/01/01","2008/01/01","2009/01/01","2010/01/01","2011/01/01","2012/01/01","2013/01/01","2014/01/01","2015/01/01","2016/02/28"]
date_list = ["2005/01/01","2016/02/14"]
for i in range(0, len(date_list) - 1) :
# filter data using date
    start_date = date_list[i]
    end_date = date_list[i+1]
    year = start_date.split("/")[0]
    print year
    raw_year_data = copy.deepcopy(raw_data[raw_data["Buy_Date"] >= start_date])
    raw_year_data = raw_year_data[raw_year_data["Buy_Date"] <= end_date]
    raw_year_data = raw_year_data.reset_index(drop = True)
    print len(raw_year_data)
    
    #Highest return and lowest return appearing in trading
    
    
    high = []
    low = []
    for i in range(len(raw_year_data)) :
        high.append(raw_year_data.loc[i][-480:].max())
        low.append(raw_year_data.loc[i][-480:].min())
    
    print max(high)
    print min(low)
     
    sl_list = []
    trace_st_list = []
    for selllimit in range(0, int(max(high)*1000) + 20 , 10) :
        sl = selllimit / 1000.0
        sl_list.append(sl)
     
    for sellstop in range(0, int(abs(min(low))*1000) + 20 , 10) :
        st = (sellstop / 1000.0) * -1
        trace_st_list.append(st)
    sl_list = [0.0]
    trace_st_list = [0.0]
    
     
    win_ratio_matrix = []
     
    average_return_matrix = []
    average_sell_at_close_return = 0.0
    average_sell_at_close_return_win_ratio = 0.0
     
    # calculate average return and win ratio if close position at 2nd close price
    win_ratio_close = 0.0
    average_return_close = 0.0
    for i in range(len(raw_year_data)) :
        time_series = raw_year_data.loc[i][-240:].dropna()
        close_return = time_series[-1]
        if close_return > 0 :
            win_ratio_close += 1
        average_return_close += close_return
    print ("Win ratio sell at close : %s" %(win_ratio_close / len(raw_year_data)))
    print ("average return sell at close : %s" %(average_return_close / len(raw_year_data)))
    
    # calculate the win ratio and return for set sell stop and sell limit
    print "sl_list " + str(len(sl_list))
    print "trace_st_list " + str(len(trace_st_list))
    for sl in sl_list :
        #l = sl_list[i]
        average_return_list = []
        win_ratio_list = []
        for st in trace_st_list :
            print str(sl) +  "  " + str(st)
            #t = trace_st_list[i]
            success_count = 0.0
            loss_count = 0.0
            trade_return = 0.0
            for i in range(len(raw_year_data)) :
                buy_price =  raw_year_data.loc[i][2]
                open_price_ratio = raw_year_data.loc[i][-721] / raw_year_data.loc[i][-720]
                # sell the stock if second day open / close is higher than 1.04, but no high limit
                time_series = raw_year_data.loc[i].dropna()[-240:]
                if open_price_ratio > 1.04 and open_price_ratio < 1.099 :
                    if time_series[0] >= 0 :
                        success_count += 1
                        trade_return += time_series[0]
                        continue
                    else :
                        loss_count += 1
                        trade_return += time_series[0]
                        continue
                elif open_price_ratio >= 1.099 :
                    
                # sell the stock when the high limit is broken
                    for j in range(len(time_series)) :
                        if raw_year_data.loc[i][-721+j] / raw_year_data.loc[i][-720] < 1.099 or j == len(time_series) -1:
                            print j
                            print raw_year_data.loc[i][-721+j] / raw_year_data.loc[i][-720]
                            if time_series[j] >= 0 :
                                success_count += 1
                                trade_return += time_series[j]
                                break
                            else :
                                loss_count += 1
                                trade_return += time_series[j]
                                break
                    continue
                else :
                    if time_series[-1] >= 0 :
                        success_count += 1
                        trade_return += time_series[-1]
                        continue
                    else :
                        loss_count += 1
                        trade_return += time_series[-1]
                        continue
            trade_count = len(raw_year_data)
            win_ratio_list.append(success_count / trade_count)
            average_return_list.append(trade_return / trade_count)
        win_ratio_matrix.append(win_ratio_list)
        average_return_matrix.append(average_return_list)
     
     
    sl_list, trace_st_list = np.meshgrid(sl_list, trace_st_list)
    #print sl_list.shape
    #print trace_st_list.shape
    average_return_matrix = np.asarray(average_return_matrix)
    average_return_matrix = np.transpose(average_return_matrix)
    win_ratio_matrix = np.asarray(win_ratio_matrix)
    win_ratio_matrix = np.transpose(win_ratio_matrix)
    #print average_return_matrix.shape
    #year = start_date.split["/"][0]
    np.savetxt("./Data/return_sell_v6_2015_2016.csv" , average_return_matrix, delimiter=",")
    np.savetxt("./Data/win_ratio_v6_2015_2016.csv" , win_ratio_matrix, delimiter=",")
print "finished"
        
        
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