'''
Created on 2016/02/25
# find the minute after trading start that appears high or low return
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

raw_data = pd.read_csv("2005-2016.csv")
print len(raw_data)
# Highest return and lowest return appearing in trading

high = []
low = []
high_time = []
low_time = []

for i in range(len(raw_data)) :
    difference = len(raw_data.loc[i]) - len(raw_data.loc[i].dropna())
    start_index = 3 + 240 - difference
    if start_index >= 240 :
        high.append(raw_data.loc[i][start_index:].max())
        high_time.append(list(raw_data.loc[i][start_index:].values).index(raw_data.loc[i][start_index:].max()))
        low.append(raw_data.loc[i][start_index:].min())
        low_time.append(list(raw_data.loc[i][start_index:].values).index(raw_data.loc[i][start_index:].min()))

plt.hist(high_time, bins=100, normed=True, cumulative=True)
plt.title("Highest return appearing in trading")
plt.show()
plt.hist(low_time, bins=100, normed=True, cumulative=True)
plt.title("Lowest return appearing in trading")
plt.show()
plt.scatter(high_time, low_time)
plt.xlabel("Highest return appearing in trading")
plt.ylabel("Lowest return appearing in trading")
plt.title("Highest vs lowest return appearing in trading")
plt.show()



print "finished"
    
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