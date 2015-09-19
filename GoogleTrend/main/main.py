'''
Created on 2015/08/12

@author: Daytona
'''

import numpy as np
import pandas as pd
import random
import pylab as p
from math import log10
from matplotlib.finance import quotes_historical_yahoo_ochl
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from hmmlearn.hmm import GaussianHMM

def main():    
    # Acquiring data
    debt_data = pd.read_csv('../Data/debt_google_trend.csv',header = 1)
    nasdaq = pd.read_csv('../Data/nasdaq_historical_quotes.csv',header = 0)[['Date','Open','Close']]
    
    # Processing data
    preprocess_raw_data = preprocessData(debt_data, 'debt',nasdaq)
    
    # add indicator into data for trading strategy
    trade_data, random_data = excuteStrategy(preprocess_raw_data, excute_random_strategy = True)
    
    # Strategy backtest
    
    # Result Output
    writeToCSV(trade_data, random_data)

def preprocessData(trend_data, key_word, nasdaq):
    # Insert week start date and end date
    debt_data = processGoogleTrendData(trend_data, key_word)
    # merge google trend data and nasdaq quotes
    merged_raw_data = mergeTrendNasdaq(debt_data,nasdaq)
    
    return merged_raw_data
    

def processGoogleTrendData(input_data, key_word):
    # create list to store start date and end date of ecah google trend record
    start_date_list = []
    end_date_list = []
    # loop to split and start and end date from column 'Week'
    for i in input_data['Week']:
        split_word = i.split('-')
        #print split_word
        start_date, end_date = '',''
        for j in [0,1,2]:
            if j != 2 :
                start_date = start_date + split_word[j].strip() + '-'
            else:
                start_date = start_date + split_word[j].strip()
        start_date_list.append(start_date)
        for j in [3,4,5]:
            if j != 5 :
                end_date = end_date + split_word[j].strip() + '-'
            else:
                end_date = end_date + split_word[j].strip()
        end_date_list.append(end_date)
    input_data['Start_Date'] = start_date_list
    input_data['End_Date'] = end_date_list
    return input_data[['Start_Date','End_Date',key_word]]

def mergeTrendNasdaq(trend_data, nasdaq_data):
    # because nasdaq is daily quote,  so change the record into weekly record, and merge with google trend record
    nasdaq_open = []
    nasdaq_close = []
    for i in range(0,len(trend_data.index)):
        start_date =  trend_data['Start_Date'][i]
        end_date =  trend_data['End_Date'][i]
        week_nasdaq = nasdaq_data[(nasdaq_data['Date'] >= start_date) & (nasdaq_data['Date'] <= end_date)]
        week_nasdaq = week_nasdaq.set_index([range(0,len(week_nasdaq.index))])
        if len(week_nasdaq.index) > 0:
            nasdaq_open.append(week_nasdaq['Open'][0])
            nasdaq_close.append(week_nasdaq['Close'][len(week_nasdaq.index)-1])
        else:
            nasdaq_open.append(None)
            nasdaq_close.append(None)
    trend_data['Nasdaq_Open'] = nasdaq_open
    trend_data['Nasdaq_Close'] = nasdaq_close
    return trend_data

def excuteStrategy(raw_data,key_word, excute_random_strategy = False):
    trade_data = insertIndicator(raw_data, key_word).dropna()
    trade_data = trade_data.set_index([range(0,len(trade_data.index))])
    #print trade_data
    
    strategy_value = []
    strategy_gross_return = []
    buy_hold_value = []
    buy_hold_gross_return = []
    strategy_return_R = []
    buy_hold_return_R = []
    win = []
    win_rate = []
    initial_invest_value = float(100)
     
    for i in range(len(trade_data.index)):
        if i == 0 :
            strategy_invest_value = initial_invest_value
            buy_hold_invest_value = initial_invest_value
        else:
            strategy_invest_value = strategy_value[i-1]
            buy_hold_invest_value = buy_hold_value[i-1]
        if trade_data['Strategy_Buy_Or_Sell'][i] == 0:
            # no trade happened
            strategy_value.append(strategy_invest_value)       
            win.append(0)
            if i == 0 :
                strategy_return_R.append(0)
            else :
                strategy_return_R.append(strategy_return_R[i-1])
        elif (trade_data['Nasdaq_Change'][i] >= 0 and trade_data['Strategy_Buy_Or_Sell'][i] == 1) | (trade_data['Nasdaq_Change'][i] <= 0 and trade_data['Strategy_Buy_Or_Sell'][i] == -1) :
            # win 
            strategy_value.append(strategy_invest_value*(1+abs(trade_data['Nasdaq_Change'][i])))
            win.append(1)
            if i == 0:
                strategy_return_R.append(abs(log10(trade_data['Nasdaq_Close'][i] / trade_data['Nasdaq_Open'][i])))
            else :
                strategy_return_R.append(strategy_return_R[i-1] + abs(log10(trade_data['Nasdaq_Close'][i] / trade_data['Nasdaq_Open'][i])))
        else:
            # loss
            strategy_value.append(strategy_invest_value*(1-abs(trade_data['Nasdaq_Change'][i])))
            win.append(0)
            if i == 0:
                strategy_return_R.append(-abs(log10(trade_data['Nasdaq_Close'][i] / trade_data['Nasdaq_Open'][i])))
            else :
                strategy_return_R.append(strategy_return_R[i-1] - abs(log10(trade_data['Nasdaq_Close'][i] / trade_data['Nasdaq_Open'][i])))
        
              
        if i == 0 :
            buy_hold_return_R.append(0)
        else :
            buy_hold_return_R.append(buy_hold_return_R[i-1] + log10(trade_data['Nasdaq_Close'][i] / trade_data['Nasdaq_Open'][i]))
        
        buy_hold_value.append(buy_hold_invest_value * (1+trade_data['Nasdaq_Change'][i]))
        buy_hold_gross_return.append((buy_hold_value[i] - initial_invest_value) / initial_invest_value)
        strategy_gross_return.append((strategy_value[i] - initial_invest_value) / initial_invest_value)
        win_rate.append(float(sum(win)) / float(len(win)))
    
    trade_data['Strategy_Position'], trade_data['Strategy_Gross_Return'], trade_data['Strategy_Cumulative_Return_R'], trade_data['Buy_Hold_Position'], \
    trade_data['Buy_Hold_Gross_Return'], trade_data['Buy_Hold_Cumulative_Return_R'], trade_data['Strategy_Win'], trade_data['Strategy_Win_Rate'],\
    = strategy_value, strategy_gross_return, strategy_return_R, buy_hold_value, buy_hold_gross_return, buy_hold_return_R, win, win_rate
    #print trade_data.describe()
    
    if excute_random_strategy == True :
        random_data = excuteRandomStrategy(raw_data.dropna())
        return trade_data, random_data
    else:
        return  trade_data

def insertIndicator(raw_data, key_word,delta_t = 3):
    # calcualte the N(t-1,delta_t) = (n(t-1) + n(t-2) + n(t-3) + ...+ n(t-delta_t)) / delta_t
    # if n > N , sell, Strategy_Buy_Or_Sell = -1, 
    N = []
    buy_sell = []
    for i in range(0, len(raw_data.index)):
        if i < delta_t:
            N.append(None)
            buy_sell.append(None)
        else:
            n_sum = 0
            for j in range(1,delta_t+1):
                n_sum += raw_data[key_word][i-j]
            N.append(float(n_sum) / float(delta_t))
            if raw_data[key_word][i] < float(n_sum) / float(delta_t):
                buy_sell.append(1)
            elif raw_data[key_word][i] > float(n_sum) / float(delta_t):
                buy_sell.append(-1)
            else:
                buy_sell.append(0)
    raw_data['N'] = N
    raw_data['Strategy_Buy_Or_Sell'] = buy_sell
    raw_data['Nasdaq_Change'] = (raw_data['Nasdaq_Close'] - raw_data['Nasdaq_Open']) / raw_data['Nasdaq_Open']
    return raw_data

def excuteRandomStrategy(raw_data):
    raw_data = raw_data.set_index([range(0,len(raw_data.index))])
    loop = 1000
    #random_strategy_return_R = zeroList(len(raw_data.index))
    random_strategy_cumulative_return_R = []
    for i in range(loop) :
        # create n but or sell decision random
        buy_or_sell = randomList(len(raw_data.index))
        cumulative_return_R = 0
        for j in range(len(buy_or_sell)):
            if buy_or_sell[j] == 1:
                cumulative_return_R += log10(raw_data['Nasdaq_Close'][j] / raw_data['Nasdaq_Open'][j])                
            else:
                cumulative_return_R += log10(raw_data['Nasdaq_Open'][j] / raw_data['Nasdaq_Close'][j])
        random_strategy_cumulative_return_R.append(cumulative_return_R)
    
    result = pd.DataFrame(data = {'Random_Strategy_Cumulative_Return_R' : random_strategy_cumulative_return_R})
    result.hist(bins = 100)
    p.show()
    print result.describe()
    return result

def zeroList(number):
    result = []
    for i in range(number):
        result.append(0)
    return result

def randomList(number):
    result = []
    for i in range(number):
        result.append(random.randint(0,1))
    return result



def writeToCSV(trade_data, random_data):
    trade_data.to_csv("debt_strategy_result.csv")
    random_data.to_csv("random_strategy_result.csv")

if __name__ == '__main__':
    main()