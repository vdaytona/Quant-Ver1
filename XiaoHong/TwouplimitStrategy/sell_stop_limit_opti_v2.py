'''
Created on 2016/03/07
 1.2.2
 input : {open(D1), close (D1), high(D1), low(D1) } 
 target : {high(D2) / low(D2) / close(D2)}
 
 using clustering algorithm to group the event, and fitting them separately
 
@author: Daytona
'''
print(__doc__)

import pandas as pd
from svmCal import svr
import numpy
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# read raw file and clean data
raw_data = pd.read_csv("./Data/2005-2016_v2.csv").dropna().reset_index(drop = True)

# extract input {open(D1), close (D1), high(D1), low(D1) }  and target {high(D2)}
high_series = []
low_series = []
open_series = []
open2_series = []
close_series = []
target_series = []
#TODO
#volume_series = []
for i in range(len(raw_data)) :
    time_series = raw_data.loc[i][-480 :]
    high_series.append(time_series[:240].max())
    low_series.append(time_series[:240].min())
    close_series.append(time_series[240])
    open_series.append(time_series[0])
    open2_series.append(time_series[240])
    target_series.append(time_series[-240:].max())
input = pd.DataFrame()
target = pd.DataFrame()
input["Open_1"] = open_series
input["Close_1"] = close_series
input["High_1"] = high_series
input["Low_1"] = low_series
input["Open_2"] = open2_series
target["High_2"] = target_series

# Use PCA to decrease the features dimension
# without PCA best NMSE ~= 0.161(low), 0.15(high) , with PCA best NMSE ~= 0.161(low), 
#input = PCA().fit_transform(input.values)

#print input
#print target

train_ratio = 0.9
target_name = "High_2"

input_array = input.values
target_array = target["High_2"].values

#random_state = 170
n_clusters = 2
y_pred = KMeans(n_clusters=n_clusters).fit_predict(input_array)
print y_pred

input_group = []
target_group = []

for i in range(0,n_clusters) :
    input_list = []
    target_list = []
    for j in range(len(y_pred)) :
        if y_pred[j] == i :
            input_list.append(input_array[j])
            target_list.append(target_array[j])
    input_group.append(input_list)
    target_group.append(target_list)

input_index = 1
index_train = int (len(input_group[input_index]) * train_ratio)
input_train = input_group[input_index][:index_train]
target_train = target_group[input_index][:index_train]
input_test = input_group[input_index][index_train :]
target_test = target_group[input_index][index_train: ]

svr().svr_timeseries(input_train, target_train, input_test, target_test, 'rbf')
