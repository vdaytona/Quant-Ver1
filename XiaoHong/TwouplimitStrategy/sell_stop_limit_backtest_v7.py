'''
Created on 2016/02/25

processing v4 data
using SVM to predict 2nd day high, low , close return
set sell limit as predicted high return,
if close return  < 0, set sell stop at -4%
if close return > 0 , set sell stop at 0%
@author: Daytona
'''
# calculate the minute highest and lowest return distribution
import pandas as pd
from sklearn.svm import SVR

def getInputTargetSeries(raw_data, target_name = None):
    # extract input {open(D1), close (D1), high(D1), low(D1) , volume D1, and volume D-1 }  and target {high(D2)}
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
        volume1.append(time_series[3]) # volume D1
        volume2.append(time_series[4]) # volume D2
        if target_name == "High" :
            target_series.append(time_series[-240:].max()) # highest return
        elif target_name == "Low" :
            target_series.append(time_series[-240:].min()) # lowest return
        elif target_name == "Close" :
            target_series.append(time_series[-1]) # close return
    train_parameter = pd.DataFrame()
    target = pd.DataFrame()
    train_parameter["Open_1"] = open_series
    train_parameter["Close_1"] = close_series
    train_parameter["High_1"] = high_series
    train_parameter["Low_1"] = low_series
    train_parameter["Open_2"] = open2_series
    train_parameter["Volume_1"] = volume1
    train_parameter["Volume_2"] = volume2
    target["Target"] = target_series
    return [train_parameter, target["Target"]]


# read raw data
raw_data = pd.read_csv("./Data/2005-2016_v4.csv").dropna().reset_index(drop = True)

# split train data and backtest data
train_ratio = 0.8
index_train = int (len(raw_data) * train_ratio)
train_raw_data = raw_data.loc[:index_train].reset_index(drop = True)
test_raw_data = raw_data.loc[index_train:].reset_index(drop = True)

# using SVM to get fitting model
train_parameter= getInputTargetSeries(train_raw_data, target_name="High")[0].values
target_high = getInputTargetSeries(train_raw_data, target_name="High")[1].values
target_low = getInputTargetSeries(train_raw_data, target_name="Low")[1].values
target_close = getInputTargetSeries(train_raw_data, target_name="Close")[1].values

kernel = "rbf"
print ("Start training")
# get high return fit model
svr_bf = SVR(kernel=kernel, C=35.397289, gamma=7.924466, epsilon = 0.004456)
high_fit_model = svr_bf.fit(train_parameter, target_high)
# get low return fit model
low_fit_model = SVR(kernel=kernel, C=0.088914, gamma=7.924466, epsilon = 0.019905).fit(train_parameter, target_low)
# get close return fit model
close_fit_model = SVR(kernel=kernel, C=3.154787, gamma=3.154787, epsilon = 0.079245).fit(train_parameter, target_close)
print ("Training finished")
# Test parameter
test_parameter = getInputTargetSeries(test_raw_data, target_name="High")[0].values

print "All data amount is %s" %len(raw_data)
print "Train data amount is %s" %len(train_raw_data)
print "Back test data amount is %s" %len(test_raw_data)

average_sell_at_close_return = 0.0
average_sell_at_close_return_win_ratio = 0.0
 
# calculate average return and win ratio if close position at 2nd close price
win_ratio_close = 0.0
average_return_close = 0.0
for i in range(len(test_raw_data)) :
    close_return = test_raw_data.loc[i][-1]
    if close_return > 0 :
        win_ratio_close += 1
    average_return_close += close_return
print ("\nBenchmark (sell at close price) :")
print ("Win ratio sell at close : %s" %(win_ratio_close / len(test_raw_data)))
print ("Average return sell at close : %s" %(average_return_close / len(test_raw_data)))

# calculate the win ratio and return for set sell stop and sell limit
positive_success_count = 0.0
loss_count = 0.0
positive_trade_return = 0.0
for i in range(len(test_raw_data)) :
    time_series = test_raw_data.values[i][-240:]
    sell_limit = high_fit_model.predict(test_parameter[i])[0]
    close_return = close_fit_model.predict(test_parameter[i])[0]
    sell_stop = 0.0 if close_return >= 0.0 else -0.04
    #while sell_limit <= sell_stop :
        #sell_limit += 0.03
    #sell_limit = 0.22 if sell_limit <= sell_stop else sell_limit
    sell_stop = -0.04
    sell_limit = 0.22
    if time_series[0] >= sell_limit or time_series[0] <= sell_stop:
        # if open price is over sell limit or under sell stop, sell at market price
        if time_series[0] >= 0.0:
            positive_success_count += 1
        else :
            loss_count += 1
        positive_trade_return += time_series[0]
        continue
    else:
        print time_series[0]
        # iterate each value to find if hit sl or st first
        for j in range(len(time_series)) :
            if time_series[j] >= sell_limit and j != len(time_series) -1:
                positive_success_count += 1
                positive_trade_return += sell_limit
                break
            elif time_series[j] <= sell_stop and j != len(time_series) -1:
                loss_count += 1
                positive_trade_return += sell_stop
                break
            elif time_series[-1] >= 0.0 and j == len(time_series) -1 :
                positive_success_count += 1
                positive_trade_return += time_series[-1]
            elif time_series[-1] <= 0.0  and j == len(time_series) -1 :
                loss_count += 1
                positive_trade_return += time_series[-1]
        continue
trade_count = len(test_raw_data)
positive_win_ratio = positive_success_count / trade_count
positive_average_return = positive_trade_return / trade_count

print "\nTest result :"
print ("Win ratio test : %s" %(positive_win_ratio))
print ("Average return test : %s" %(positive_average_return))

print "finished"