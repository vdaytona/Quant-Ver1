'''
MLfkhwL8
Created on 2016/03/07
 1.2.1
 input : {open(D1), close (D1), high(D1), low(D1) } 
 target : {high(D2) / low(D2) / close(D2)}
 
@author: Daytona
'''
print(__doc__)

import pandas as pd
from svmCal import svr
import numpy
from sklearn.decomposition import PCA

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

index_train = int (len(input) * train_ratio)
input_train = input[:index_train]
target_train = target[:index_train]
input_test = input[index_train :]
target_test = target[index_train: ]

from sknn.mlp import Classifier, Layer

nn = Classifier(
    layers=[
        Layer("Rectifier", units=100),
        Layer("Linear")],
    learning_rate=0.02,
    n_iter=10)

print input_train.values

nn.fit(input_train.values, target_train["High_2"].values)

y_valid = nn.predict(input_test.values)

score = nn.score(y_valid, target_test["High_2"].values)

print score

#svr().svr_timeseries(input_train, target_train["High_2"].values, input_test, target_test["High_2"].values, 'rbf')


