'''
Created on 2015/10/06
Using 44 words google trend result as input, to predict the Nasdaq 500 variation
@author: Daytona
'''

import numpy as np
import pandas as pd
import RFclass as rf
import multipleWordsCommonApp as mwca
from pandas.tslib import Timestamp
from pandas.tseries.offsets import DateOffset

def main():
    
    RDP_period = 2
    
    # collect google trends data as input
    google_trends_result_list = importGoogleTrendsResult()
    
    # collect Nasdaq data as target
    nasdaq_quotes = pd.read_csv('../Data/nasdaq_historical_quotes.csv',header = 0, index_col = 'Date')[['Open','Close']]
    #print nasdaq_quotes
    
    # preprocess google trends data, into RDP 
    google_trends_result_list = preprocessGoogleTrendsData(google_trends_result_list, RDP_period = RDP_period)
    #print google_trends_result_list
    
    # preprocess NASDAQ data as target
    nasdaq_quotes_weekly = preprocessNasdaqData(nasdaq_quotes, RDP_period = RDP_period)
    #print nasdaq_quotes_weekly
    
    # merging google trends datas and Nasdaq quotes
    merged_data = merge(google_trends_result_list, nasdaq_quotes_weekly)
    
    # split train and test data
    train_x, train_y, test_x, test_y = prepareTrainTestData(merged_data, RDP_period = RDP_period, train_percent = 0.7)
    
    # training
    forest = train(train_x, train_y )
    
    # test
    test(test_x, test_y, forest)
    
    # result analysis
    
    print "finished"

def importGoogleTrendsResult():
    return mwca.importAllGoogleTrendsResults()

def preprocessGoogleTrendsData(google_trends_result_list, RDP_period = 1):
    new_list = []
    for single_result in google_trends_result_list:
        # Use the first day of the week as index
        DateTime = {'DateTime' : single_result.index.map(lambda x: Timestamp(x.split(' ')[0]) + DateOffset(days=-6))}
        single_result = single_result.set_index(DateTime['DateTime'])
        
        # Calculating RDP
        key_word = single_result.columns.values[0]
        col_name = str('%s_RDP_%s' % (key_word, str(RDP_period)))
        single_result = RDPProcess(single_result, key_word, col_name, RDP_period)
        
        new_list.append(single_result)
        
    return new_list

def preprocessNasdaqData(nasdaq_quotes, RDP_period = 1):
    # change to week scale quotes
    nasdaq_quotes_weekly = change_to_week_quotes(nasdaq_quotes)
    # calculation of RDP
    #col_name = str('Nasdaq_Close_RDP_%s' % (str(RDP_period)))
    #nasdaq_quotes_weekly = RDPProcess(nasdaq_quotes_weekly, "Close", col_name, RDP_period)
    
    # calculation if the nasdaq increase(1) or decrease(0) in week pace
    nasdaq_quotes_weekly = ifIncreaseOrDecrease(nasdaq_quotes_weekly)
    
    return nasdaq_quotes_weekly

def change_to_week_quotes(daily_quotes):
    '''
    change to weekly quotes from day frame
    '''
    daily_quotes['DateTime'] = pd.to_datetime(daily_quotes.index)
    daily_quotes = daily_quotes.set_index(['DateTime'])
    
    # Mark each row with day, week of year and year 
    daily_quotes['WeekDay'] = daily_quotes.index.map(lambda row: row.weekday)
    daily_quotes['WeekOfYear'] = daily_quotes.index.map(lambda row: row.weekofyear)
    daily_quotes['Year'] = daily_quotes.index.map(lambda row: row.year)
    
    DateTime = []
    Open = []
    Close = []
    
    # loop in unique combination of week of year and year to ensure there are in same week and same year
    for col in daily_quotes[['WeekOfYear','Year']].drop_duplicates().values :
        one_week_quotes = daily_quotes[daily_quotes['WeekOfYear'] == col[0]][daily_quotes['Year'] == col[1]]
        
        # Choose Open price of the first day of the week, and Close price of the last day of the week
        DateTime.append(one_week_quotes['WeekDay'].idxmin())
        Open.append(one_week_quotes[one_week_quotes['WeekDay'] == one_week_quotes['WeekDay'].min()]['Open'].values[0])
        Close.append(one_week_quotes[one_week_quotes['WeekDay'] == one_week_quotes['WeekDay'].max()]['Close'].values[0])
    
    return pd.DataFrame(data = {'Open' : Open, 'Close' : Close}, index = DateTime)

def ifIncreaseOrDecrease(input):
    
    input['Close_Pct'] = input['Close'].pct_change(periods = 1)
    # if Close_Pct >= 0 -> Close_Change -> 1, else -> 1
    input['Close_Change'] = input['Close_Pct'].map(lambda x : 1 if x >= 0 else 0)
    return input

def RDPProcess(data, key_word, col_name, period = 1):
    '''
        n day relative difference in percentage of price
        
        Args:
            n: number of day for calculation
            inputData : dataType pandasFrame
            example:
            {[date, AdjClose], [2011-1-1, 80.6], [2011-1-2, 82.2]}
        
        Return:
            dataType pandasFrame
            example:
            {[date,RDP5], [2011-1-6, 0.23333],[2011-1-7,0.34556]}
            the date here refers to the last date of the n day duration (e.x. 2011-1-6 is duration from 2011-1-1)
            Since it is a n day differential average, so first n day has no result
        '''
    data[col_name] = (data[key_word].pct_change(period) * data[key_word] / period)
    return data

def merge(google_trends_result_list, nasdaq_quotes):
    merged_google_result = google_trends_result_list[0]
    for index in range(1, google_trends_result_list.__len__()) :
        merged_google_result = merged_google_result.join(google_trends_result_list[index],how = 'inner')
    merged_result = merged_google_result.join(nasdaq_quotes,how='outer').replace([np.inf, -np.inf], np.nan)
    return merged_result.dropna()

def prepareTrainTestData(input_data, RDP_period = 1, train_percent = 0.7):
    feature_set = getTrainColumnName(RDP_period)
    train_size = int(train_percent * len(input_data))
    
    train_x = input_data[feature_set][ : train_size]
    train_y = input_data['Close_Change'][ : train_size]
    test_x = input_data[feature_set][ train_size : ]
    test_y = input_data['Close_Change'][ train_size : ]
    
    return train_x, train_y, test_x, test_y

def train(train_x, train_y):
    forest = rf.training().trainforest('gbt', train_x, train_y, 1000, accuracy_train_calculation = True)
    
    #===========================================================================
    # rf.training().importance(forest)
    # rf.training().dependence(forest, train_x, feature_set)
    # rf.training().dependence3d(forest, train_x, feature_set)
    #===========================================================================
    return forest

def test(test_x, test_y, train_model):
    rf.test().testforest(test_x, test_y, train_model)

def getTrainColumnName(RDP_period):
    file_name_list = mwca.getGoogleTrendsResultFileName()
    word_list = []
    for word in file_name_list :
        word_list.append(str('%s_RDP_%s' % (word.split("/")[2].split("_")[0], str(RDP_period))))
    return word_list
    

if __name__ == '__main__':
    main()