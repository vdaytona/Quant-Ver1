#coding = utf-8
#encoding: utf-8
'''
Created on 2016/03/07
 1.2.1
 input : {open(D1), close (D1), high(D1), low(D1), volume D1, volume D2} 
 target : {high(D2) / low(D2) / close(D2)}
 using data v4

2015-2016
volume1 change (D1 / D-1) :
MAX DS = 136.000000
Hit rate = 0.814371
NMSE = 0.265982
DOC = 0.732416
MAE = 0.036194
C = 35.397289, gamma = 1.774067, epsilon = 0.019905

volume1 D1
MAX DS = 144.000000
Hit rate = 0.862275
NMSE = 0.207025
DOC = 0.791728
MAE = 0.030146
C = 7.924466, gamma = 1.774067, epsilon = 0.004456

volume1 D1 and volume2 D-1
MAX DS = 71.000000
Hit rate = 0.845238
NMSE = 0.182068
DOC = 0.815738
MAE = 0.026944
C = 35.397289, gamma = 7.924466, epsilon = 0.004456

2005-2016 :
Low
MAX DS = 228.000000
Hit rate = 0.912000
NMSE = 0.133745
DOC = 0.865718
MAE = 0.019032
C = 0.088914, gamma = 7.924466, epsilon = 0.019905

close
MAX DS = 577.000000
Hit rate = 0.771390
NMSE = 0.456214
DOC = 0.543175
MAE = 0.040270
C = 3.154787, gamma = 3.154787, epsilon = 0.079245
 
@author: Daytona
'''
print(__doc__)

import pandas as pd
from svmCal import svr

# read raw file and clean data
raw_data = pd.read_csv("./Data/2005-2016_v4.csv").dropna().reset_index(drop = True)

# extract input {open(D1), close (D1), high(D1), low(D1) }  and target {high(D2)}
high_series = []
low_series = []
open_series = []
open2_series = []
close_series = []
target_series = []
volume1 = []
volume2 = []
for i in range(len(raw_data)) :
    time_series = raw_data.loc[i][-480 :]
    high_series.append(time_series[:240].max())
    low_series.append(time_series[:240].min())
    close_series.append(time_series[240])
    open_series.append(time_series[0])
    open2_series.append(time_series[240])
    #target_series.append(time_series[-240:].max()) # highest return
    #target_series.append(time_series[-240:].min()) # lowest return
    target_series.append(time_series[-1]) # close return
    volume1.append(time_series[3])
    volume2.append(time_series[4])
input = pd.DataFrame()
target = pd.DataFrame()
input["Open_1"] = open_series
input["Close_1"] = close_series
input["High_1"] = high_series
input["Low_1"] = low_series
input["Open_2"] = open2_series
input["Volume_1"] = volume1
input["Volume_2"] = volume2
target["High_2"] = target_series



# Use PCA to decrease the features dimension
# without PCA best NMSE ~= 0.161(low), 0.15(high) , with PCA best NMSE ~= 0.161(low), 
#input = PCA().fit_transform(input.values)

#print input
#print target

train_ratio = 0.7

index_train = int (len(input) * train_ratio)
input_train = input[:index_train].values
target_train = target[:index_train]["High_2"].values
input_test = input[index_train :].values
target_test = target[index_train: ]["High_2"].values

print target_train

svr().svr_timeseries(input_train, target_train, input_test, target_test, 'rbf')


#print input_test

#===============================================================================
# svr().svr_timeseries(input_train, target_train["High_2"].values, input_test, target_test["High_2"].values, 'rbf')
# 
# # predict after classify the input using k-means
# random_state = 170
# n_clusters = 2
# y_pred = KMeans(n_clusters=n_clusters, random_state=random_state).fit_predict(input_train)
# print y_pred
# 
# input_train_group = []
# target_train_group = []
# input_test_group = []
# target_test_group = []
# for i in range(0, n_clusters) :
#     input_train_list = []
#     target_train_list = []
#     input_test_list = []
#     target_test_list = []
#     for j in range(len(y_pred)) :
#         if y_pred[j] == i :
#             input_train_list.append(input_train[j])
#             target_train_list.append(target_train[j])
#             input_test_list.append(input_test[j])
#             input_test_list.append(target_test[j])
#     input_train_group.append(input_train_list)
#     target_train_group.append(target_train_list)
#     input_test_group.append(input_test_list)
#     target_test_group.append(target_test_list)
# 
# svr().svr_timeseries(input_train_group[0], target_train_group[0], input_test_group[0], target_test_group[0], 'rbf')
#===============================================================================


#===============================================================================
# from sknn.mlp import Classifier, Layer
# 
# nn = Classifier(
#     layers=[
#         Layer("Rectifier", units=100),
#         Layer("Linear")],
#     learning_rate=0.02,
#     n_iter=10)
# 
# print input_train.values
# 
# nn.fit(input_train.values, target_train["High_2"].values)
# 
# y_valid = nn.predict(input_test.values)
# 
# score = nn.score(y_valid, target_test["High_2"].values)
# 
# print score
#===============================================================================



