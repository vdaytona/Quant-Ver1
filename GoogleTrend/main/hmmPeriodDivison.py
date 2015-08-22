'''
Created on 2015/08/19
Using Hmm model to specified the 'google trend debt strategy' 
1. positive effective period, 2. negative effective period, 3. non effective period 
@author: Daytona
'''

import main as m
import pandas as pd
import numpy as np
import pylab as p
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from hmmlearn.hmm import GaussianHMM, GMMHMM, MultinomialHMM

def main():
    # read data
    
    debt_data = pd.read_csv('../Data/debt_google_trend.csv',header = 1)
    nasdaq = pd.read_csv('../Data/nasdaq_historical_quotes.csv',header = 0)[['Date','Open','Close']]
    
    # preprocess data
    preprocess_raw_data = m.preprocessData(debt_data, nasdaq)
    
    # strategy excution
    trade_data = m.excuteStrategy(preprocess_raw_data, excute_random_strategy = False)
    
    # process trade result data
    trade_data = processTradingData(trade_data)

    # hmm model analyze
    hmmtest(trade_data, trade_data[['Nasdaq_Close_RDP_5','Strategy_Gross_Return_RDP_5']])
    columnName = []
    period = [1,2,5,15,30]
    column = ['Nasdaq_Close','Strategy_Gross_Return','Strategy_Cumulative_Return_R']
    for col in column:
        for i in period:
            col_name = str('%s_RDP_%s' % (col, str(i))) 
            columnName.append(col_name)
    #===========================================================================
    # for i in range(len(column.index)-1):
    #     for j in range(i+1 , len(column.index)):
    #         print ()
    #         hmmtest(trade_data[[column[i],column[j]]])
    #===========================================================================

def processTradingData(trade_data):
    # add RDP on Nasdaq_Close, Strategy_Gross_Return, Strategy_Cumulative_Return_R
    period = [1,2,5,15,30]
    column = ['Nasdaq_Close','Strategy_Gross_Return','Strategy_Cumulative_Return_R']
    for col in column:
        for i in period:
            trade_data = RDPProcess(trade_data, col, i)
    print trade_data.describe()
    
    return trade_data.dropna()


def RDPProcess(trade_data, column = None, period = 1):
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
    col_name = str('%s_RDP_%s' % (column, str(period))) 
    # print trade_data[column].pct_change(period)
    #trade_data[col_name] = scalerData(substractOutliers(trade_data[column].pct_change(period), period),1,-1)
    trade_data[col_name] = substractOutliers(trade_data[column].pct_change(period) * trade_data[column] / period, period)
    return trade_data

def scalerData(input_data, max_value, min_value):
    max = float(input_data.dropna().max())
    min = float(input_data.dropna().min())
    input_data = input_data.dropna().apply(lambda x: min_value + (max_value-min_value) * (x.astype(float) - min) / (max - min))
    return input_data

# replace the outliers by the closest marginal values
def substractOutliers(input_data,n):
    double_standard_deviation = input_data.std() * 2
    mean = input_data.mean()
    up_limit = mean + double_standard_deviation
    down_limit = mean - double_standard_deviation
    for i in range(n, len(input_data)) :
        if input_data[i] > up_limit or input_data[i] < down_limit:
            if i != n:
                input_data[i] = input_data[i-1]
            elif input_data[i] > up_limit:
                input_data[i] = up_limit
            elif input_data[i] < down_limit:
                input_data[i] = down_limit
    return input_data

def hmmtest(trade_data, test_data):
    # pack diff and volume for training
    X = test_data
    
    ###############################################################################
    # Run Gaussian HMM
    #print("fitting to HMM and decoding ...", end='')
    
    # make an HMM instance and execute fit
    model = GaussianHMM(n_components=4, covariance_type="full", n_iter=1000).fit(X)
    #model= GMMHMM(n_components=4,n_mix=3,covariance_type="diag", n_iter=100).fit(X)
    # model = MultinomialHMM(n_components=4, n_iter=100).fit(X)
    # predict the optimal sequence of internal hidden state
    hidden_states = model.predict(X)
    
    print("done\n")
    
    ###############################################################################
    # print trained parameters and plot
    print("Transition matrix")
    print(model.transmat_)
    print()
    
    print("means and vars of each hidden state")
    for i in range(model.n_components):
        print("%dth hidden state" % i)
        print("mean = ", model.means_[i])
        print("var = ", np.diag(model.covars_[i]))
        print()
    
    years = YearLocator()   # every year
    months = MonthLocator()  # every month
    yearsFmt = DateFormatter('%Y')
    fig = p.figure()
    ax = fig.add_subplot(111)
    
    for i in range(model.n_components):
        # use fancy indexing to plot data in each state
        idx = (hidden_states == i)
        ax.plot_date(trade_data.index[idx], trade_data[['Nasdaq_Close']][idx], 'o', label="%dth hidden state" % i)
        print "%dth hidden state has %d element" % (i,len(trade_data.index[idx]))
    ax.legend()
    
    ax.plot(trade_data.index, trade_data[['Strategy_Gross_Return']]*500)
    ax.plot(trade_data.index,trade_data[['Strategy_Gross_Return_RDP_2']]*1000)
    # format the ticks
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)
    ax.autoscale_view()
    
    # format the coords message box
    ax.fmt_xdata = DateFormatter('%Y-%m-%d')
    ax.fmt_ydata = lambda x: '$%1.2f' % x
    ax.grid(True)
    
    #fig.autofmt_xdate()
    p.show()

if __name__ == '__main__':
    main()