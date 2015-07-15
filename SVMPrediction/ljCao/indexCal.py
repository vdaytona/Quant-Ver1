'''
Calculation indicator

Created on 2015/07/13

@author: Daytona
'''

import copy
import pandas

class index_cal():
    def __init__(self):
        pass
    
    # TODO @JP
    def RDP_n(self, input_data, n):
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
        result = copy.deepcopy(input_data)
        col_name = str('RDP-%s' %str(n))
        RDP_series = result['AdjClose'].pct_change(n)
        result[col_name] = RDP_series * 100
        return result[['Date',col_name]].dropna()
    
    # this is wrong because calculated as (p(i+5) - pi)/p(i+5)
    def RDP_plus_n(self, input_data, n):
        '''
        future n day relative difference in percentage of price 
        
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
        result = copy.deepcopy(input_data)
        result = result.sort_index(by = ['Date'], ascending = [False])
        col_name = str('RDP+%s' %str(n))
        RDP_series = result['AdjClose'].pct_change(n)
        result[col_name] = RDP_series * 100
        result = result.sort_index(by = ['Date'], ascending = [True])
        return result[['Date',col_name]].dropna()
    
    # TODO @JP
    def EMA_n(self, inputData, n):
        '''
        n-day exponential moving average from the closing price
        
        Args:
            n: number of day for calculation
            inputData : dataType pandasFrame
            example:
            {[date, value], [2011-1-1, 80.6], [2011-1-2, 82.2]}
        
        Return:
            dataType pandasFrame
            example:
            {[date, EMA15], [2011-1-15, 81], [2011-1-16, 82]}
            Since it is a n day average, so first n day has no result
        '''
        
        pass
