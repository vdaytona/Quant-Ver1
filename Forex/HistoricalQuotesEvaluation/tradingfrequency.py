'''
Created on 2015/08/04
Used to analyze the peak trading session for pair
EUR/USD , GBP/USD, EUR/JPY, USD/CAD, AUD/JPY, AUD/USD, EUR/GBP, USD/JPY
Evaluation :
1. Volume distribution to time
2. One bar change percent: (Close - Open) / Open
3. N bar trend durative : What the possibility of the bar will keep trend for next n bar.

@author: Daytona
'''

import pandas as df
import pylab as P
import copy
import numpy as np
import matplotlib.pyplot as plt

def main():
    
    # import data from csv    
    raw_data = dataCollection()
    
    # evaluation
    evaluation(raw_data)
    # print result[(result['Time_Frame'] == 240) & (result['Pair'] == 'GBP_USD')].describe()
    
    pass

def dataCollection():
    # import data from csv
    # Open, High, Low, CLose, Vol
    # EUR_USD_60
    
    
    AUD_USD_240 = preprocessData(df.read_csv('../Data/AUDUSD240.csv', header=None))
    AUD_USD_240['Pair'] = ('AUD_USD')
    AUD_USD_240['Time_Frame'] = 240
    AUD_USD_60 = preprocessData(df.read_csv('../Data/AUDUSD60.csv', header=None))
    AUD_USD_60['Pair'] = ('AUD_USD')
    AUD_USD_60['Time_Frame'] = 60
    
    AUD_JPY_240 = preprocessData(df.read_csv('../Data/AUDJPY240.csv', header=None))
    AUD_JPY_240['Pair'] = ('AUD_JPY')
    AUD_JPY_240['Time_Frame'] = 240
    AUD_JPY_60 = preprocessData(df.read_csv('../Data/AUDJPY60.csv', header=None))
    AUD_JPY_60['Pair'] = ('AUD_JPY')
    AUD_JPY_60['Time_Frame'] = 60
    
    GBP_USD_240 = preprocessData(df.read_csv('../Data/GBPUSD240.csv', header=None))
    GBP_USD_240['Pair'] = ('GBP_USD')
    GBP_USD_240['Time_Frame'] = 240
    GBP_USD_60 = preprocessData(df.read_csv('../Data/GBPUSD60.csv', header=None))
    GBP_USD_60['Pair'] = ('GBP_USD')
    GBP_USD_60['Time_Frame'] = 60
    
    EUR_USD_240 = preprocessData(df.read_csv('../Data/EURUSD240.csv', header=None))
    EUR_USD_240['Pair'] = ('EUR_USD')
    EUR_USD_240['Time_Frame'] = 240
    EUR_USD_60 = preprocessData(df.read_csv('../Data/EURUSD60.csv', header=None))
    EUR_USD_60['Pair'] = ('EUR_USD')
    EUR_USD_60['Time_Frame'] = 60
    
    USD_JPY_240 = preprocessData(df.read_csv('../Data/USDJPY240.csv', header=None))
    USD_JPY_240['Pair'] = ('USD_JPY')
    USD_JPY_240['Time_Frame'] = 240
    USD_JPY_60 = preprocessData(df.read_csv('../Data/USDJPY60.csv', header=None))
    USD_JPY_60['Pair'] = ('USD_JPY')
    USD_JPY_60['Time_Frame'] = 60
    
    USD_CAD_240 = preprocessData(df.read_csv('../Data/USDCAD240.csv', header=None))
    USD_CAD_240['Pair'] = ('USD_CAD')
    USD_CAD_240['Time_Frame'] = 240
    USD_CAD_60 = preprocessData(df.read_csv('../Data/USDCAD60.csv', header=None))
    USD_CAD_60['Pair'] = ('USD_CAD')
    USD_CAD_60['Time_Frame'] = 60
    
    EUR_JPY_240 = preprocessData(df.read_csv('../Data/EURJPY240.csv', header=None))
    EUR_JPY_240['Pair'] = ('EUR_JPY')
    EUR_JPY_240['Time_Frame'] = 240
    EUR_JPY_60 = preprocessData(df.read_csv('../Data/EURJPY60.csv', header=None))
    EUR_JPY_60['Pair'] = ('EUR_JPY')
    EUR_JPY_60['Time_Frame'] = 60
    
    EUR_GBP_240 = preprocessData(df.read_csv('../Data/EURGBP240.csv', header=None))
    EUR_GBP_240['Pair'] = ('EUR_GBP')
    EUR_GBP_240['Time_Frame'] = 240
    EUR_GBP_60 = preprocessData(df.read_csv('../Data/EURGBP60.csv', header=None))
    EUR_GBP_60['Pair'] = ('EUR_GBP')
    EUR_GBP_60['Time_Frame'] = 60
    
    #===========================================================================
    # EUR_GBP_60
    #===========================================================================
    
    # add all the pair record into one DataFrame variable
    result = df.concat([EUR_USD_240, EUR_USD_60,
                        EUR_GBP_240, EUR_GBP_60,
                        EUR_JPY_240, EUR_JPY_60,
                        GBP_USD_240, GBP_USD_60,
                        AUD_USD_240, AUD_USD_60, 
                        USD_CAD_240, USD_CAD_60,
                        USD_JPY_240, USD_JPY_60,
                        AUD_JPY_240, AUD_JPY_60],
                        ignore_index=True)
    #result = df.concat([AUD_USD_240,AUD_USD_60,GBP_USD_240,GBP_USD_60],ignore_index=True)
    return result


def preprocessData(input_data):
    # add precentage change, and trend counting
    input_data.columns = ['Date','Time','Open','High','Low','Close','Volume']
    input_data['Bar_Change'] = input_data[['Open']].pct_change(1)
    
    up_trend = []
    down_trend = []
    up_trend.append(None)
    down_trend.append(None)
    #print input_data['Bar_Change'][1]
    if input_data['Bar_Change'][1] > 0:
        up_trend.append(1)
        down_trend.append(0)
    elif input_data['Bar_Change'][1] < 0:
        up_trend.append(0)
        down_trend.append(1)
    else:
        up_trend.append(0)
        down_trend.append(0)

    for i in range(2, len(input_data['Bar_Change'])):
        if input_data['Bar_Change'][i] > 0:
            up_trend.append(up_trend[i - 1] + 1)
            down_trend.append(0)
        elif input_data['Bar_Change'][i] < 0:
            up_trend.append(0)
            down_trend.append(down_trend[i - 1] + 1)
        else:
            up_trend.append(0)
            down_trend.append(0)
    
    input_data['Up_Trend'] = up_trend
    input_data['Down_Trend'] = down_trend
    input_data['Trend'] = input_data['Up_Trend'] + input_data['Down_Trend']
    
    if_trend_keep = []
    if_trend_keep.append(None)
    for i in range(1, len(input_data['Bar_Change'])-1):
        if (input_data['Trend'][i+1] > input_data['Trend'][i]):
            if_trend_keep.append(1)
        else:
            if_trend_keep.append(0)
    if_trend_keep.append(None)
    input_data['If_Trend_Keep'] = if_trend_keep
    #print input_data.groupby(by = 'Time').describe()
    #input_data['Down_Trend'].hist(bins=input_data['Down_Trend'].max())
    #P.show()
    return input_data

def evaluation(input_data):
    # volue distribution
    volumeDistribution(input_data)
    
    # Bar change percent
    barChange(input_data)
    
    # If trend keep
    trendKeep(input_data)

def volumeDistribution(input_data):
    input_data = input_data[['Time','Pair','Time_Frame','Volume']]
    
    # 4hour calculation
    # get 4 hour record
    volume_240 = input_data[input_data['Time_Frame'] == 240]
    # get unique Time / pair interval to group record
    time_frame = volume_240['Time'].unique()
    pair = volume_240['Pair'].unique()
    # create new DataFrame index with time interval and column with pair
    df_volume_240 = df.DataFrame(index = time_frame, columns = pair)
    # insert the sum of Volume of the specific time and pair into the created DataFrame
    for pair_name in pair:
        for time_name in time_frame:
            df_volume_240.loc[[time_name],pair_name] = \
            volume_240[(volume_240['Pair'] == str(pair_name)) & (volume_240['Time'] == str(time_name))][['Volume']].mean()[0]
    #===========================================================================
    # # normalize data group by pair
    # df_volume_240 = df_volume_240/df_volume_240.max().astype(np.float64)
    #===========================================================================
    # sort index
    df_volume_240.sort_index(inplace=True)
    # plot bar graph legend by pair
    df_volume_240.plot(kind = 'bar')
    plt.show()
    
    # 1 hour calculation
    # same as 4 hour calculation
    volume_60 = input_data[input_data['Time_Frame'] == 60]
    time_frame = volume_60['Time'].unique()
    pair = volume_60['Pair'].unique()
    df_volume_60 = df.DataFrame(index = time_frame, columns = pair)
    for pair_name in pair:
        for time_name in time_frame:
            df_volume_60.loc[[time_name],pair_name] = \
            volume_60[(volume_60['Pair'] == str(pair_name)) & (volume_60['Time'] == str(time_name))][['Volume']].mean()[0]
    #df_volume_60 = df_volume_60/df_volume_60.max().astype(np.float64)
    df_volume_60.sort_index(inplace=True)
    df_volume_60.plot(kind = 'bar')
    plt.show()
    
def trendKeep(input_data):
    input_data = input_data[['Time','Pair','Time_Frame','If_Trend_Keep']]
    
    # 4hour calculation
    volume_240 = input_data[input_data['Time_Frame'] == 240]
    time_frame = volume_240['Time'].unique()
    pair = volume_240['Pair'].unique()
    df_volume_240 = df.DataFrame(index = time_frame, columns = pair)
    for pair_name in pair:
        for time_name in time_frame:
            df_volume_240.loc[[time_name],pair_name] = \
            volume_240[(volume_240['Pair'] == str(pair_name)) & (volume_240['Time'] == str(time_name))][['If_Trend_Keep']].sum()[0] / \
            len(volume_240[(volume_240['Pair'] == str(pair_name)) & (volume_240['Time'] == str(time_name))][['If_Trend_Keep']])
    #df_volume_240 = df_volume_240/df_volume_240.max().astype(np.float64)
    df_volume_240.sort_index(inplace=True)
    df_volume_240.plot()
    plt.show()
    
    # 1 hour calculation
    volume_60 = input_data[input_data['Time_Frame'] == 60]
    time_frame = volume_60['Time'].unique()
    pair = volume_60['Pair'].unique()
    df_volume_60 = df.DataFrame(index = time_frame, columns = pair)
    for pair_name in pair:
        for time_name in time_frame:
            df_volume_60.loc[[time_name],pair_name] = \
            volume_60[(volume_60['Pair'] == str(pair_name)) & (volume_60['Time'] == str(time_name))][['If_Trend_Keep']].sum()[0] / \
            len(volume_60[(volume_60['Pair'] == str(pair_name)) & (volume_60['Time'] == str(time_name))][['If_Trend_Keep']])
    
    #df_volume_60 = df_volume_60/df_volume_60.max().astype(np.float64)
    df_volume_60.sort_index(inplace=True)
    df_volume_60.plot()
    plt.show()

def barChange(input_data):
    input_data = input_data[['Time','Pair','Time_Frame','Bar_Change']]
    
    # 4hour calculation
    volume_240 = input_data[input_data['Time_Frame'] == 240]
    time_frame = volume_240['Time'].unique()
    pair = volume_240['Pair'].unique()
    df_volume_240 = df.DataFrame(index = time_frame, columns = pair)
    for pair_name in pair:
        for time_name in time_frame:
            df_volume_240.loc[[time_name],pair_name] = volume_240[(volume_240['Pair'] == str(pair_name)) & (volume_240['Time'] == str(time_name))][['Bar_Change']].abs().mean()[0]
    #df_volume_240 = df_volume_240/df_volume_240.max().astype(np.float64)
    df_volume_240.sort_index(inplace=True)
    df_volume_240.plot()
    plt.show()
    
    # 1 hour calculation
    volume_60 = input_data[input_data['Time_Frame'] == 60]
    time_frame = volume_60['Time'].unique()
    pair = volume_60['Pair'].unique()
    df_volume_60 = df.DataFrame(index = time_frame, columns = pair)
    for pair_name in pair:
        for time_name in time_frame:
            df_volume_60.loc[[time_name],pair_name] = volume_60[(volume_60['Pair'] == str(pair_name)) & (volume_60['Time'] == str(time_name))][['Bar_Change']].abs().mean()[0]
    
    #df_volume_60 = df_volume_60/df_volume_60.max().astype(np.float64)
    df_volume_60.sort_index(inplace=True)
    df_volume_60.plot()
    plt.show()


if __name__ == '__main__':
    main()
