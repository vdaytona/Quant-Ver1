'''
Calculation indicator

Created on 2015/07/13

@author: Daytona
'''

import copy

class index_cal():
    def __init__(self):
        pass
    
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
        col_name = str('RDP-%s' % str(n))
        RDP_series = result['AdjClose'].pct_change(n)
        
        # replace the outliers by the closest marginal values
        RDP_series = self.substractOutliers(RDP_series, n)
        
        # scalar data to [0 , 1] instead of [-0.9, 0.9] described in paper for better performance        
        RDP_series = self.scalerData(RDP_series, 1, 0)
        
        result[col_name] = RDP_series
        return result[['Date', col_name]].dropna()
    
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
        EMA_3 = self.EMA_n(result, 3)
        col_name = str('RDP+%s' % str(n))
        RDP_series = []
        length = len(result.index)
        for i in range(length) :
            if i < 2 or i > (length - n - 1):
                RDP_series.append(None)
            else:
                value = (result['AdjClose'][i + 5] - EMA_3['EMA'][i]) / (EMA_3['EMA'][i]) * 100
                RDP_series.append(value)
        result[col_name] = RDP_series
        return result[['Date', col_name]].dropna()
    
    def EMA_n(self, input_data, n):
        '''
        in order to calculate EMAn
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
        
        EMA:
            EMA_today = EMA_yesterday + alpha(multiplier) x (pirce_today - EMA_yesterday)
            Or (use here)
            EMA_today = alpha(multiplier) x (p1 + (1 - alpha) x p2 + (1 - alpha)^2 x p3 + ....) until pn,
            where p1 is the price today, p2 is price_yesterday
        '''
        result = copy.deepcopy(input_data)
        col_name = str('EMA')
        EMA_series = []
        multiplier = float(2) / float(n + 1)
        EMA_previous = 0.0
        for i in range(len(result.index)) :
            if i < n - 1:
                EMA_series.append(None)
            elif i == n - 1:
                EMA = result['AdjClose'][i]
                EMA_series.append(EMA)
                EMA_previous = EMA
            else:
                EMA = multiplier * result['AdjClose'][i] + (1 - multiplier) * EMA_previous
                EMA_series.append(EMA)
                EMA_previous = EMA
        result[col_name] = EMA_series
        return result[['Date', col_name]]
    
    def EMAn(self, input_data, n):
        '''
        EMAn = price_today-EMA_n
        '''
        result = self.EMA_n(copy.deepcopy(input_data), n)
        col_name = str('EMA%s' % str(n))
        EMAn_series = []
        for i in range(len(result.index)) :
            if i < n - 1:
                EMAn_series.append(None)
            else:
                EMAn_series.append(input_data['AdjClose'][i] - result['EMA'][i])
        result[col_name] = EMAn_series
        return result[['Date', col_name]].dropna()
    
    def VOL_n(self, input_data, n):
        """
        Sum of past n day volume
        """
        col_name = str('VOL-%s' % str(n))
        length = len(input_data.index)
        sum_volumn = []
        for i in range(0, n - 1):
            sum_volumn.append(None)
        for i in range(n - 1, length):
            sum_volumn.append(input_data['AdjVolume'][i + 1 - n:i + 1].sum())
        input_data[col_name] = sum_volumn
        return input_data[['Date', col_name]]
    
    def RDV_n(self, input_data, n):
        '''
        n day relative difference in percentage of volume
        
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
        col_name = str('RDV-%s' % str(n))
        RDV_series = result['AdjVolume'].pct_change(n)
        
        # replace the outliers by the closest marginal values
        RDV_series = self.substractOutliers(RDV_series, n)
        
        # scalar data to [0 , 1] instead of [-0.9, 0.9] described in paper for better performance
        RDV_series = self.scalerData(RDV_series, 1, 0)
        
        result[col_name] = RDV_series
        return result[['Date', col_name]].dropna()
    
    # replace the outliers by the closest marginal values
    def substractOutliers(self,input_data, n):
        double_standard_deviation = input_data.std() * 2
        if abs(input_data[n]) > double_standard_deviation : input_data[n] = input_data[n] / (abs(input_data[n])) * double_standard_deviation
        for i in range(n + 1 , len(input_data)) :
            if abs(input_data[i]) > double_standard_deviation :
                input_data[i] = input_data[i-1]
        return input_data
    
    # scalar data to [min_value , max_value]
    def scalerData(self, input_data, max_value, min_value):
        max = input_data.max()
        min = input_data.min()
        input_data = input_data.apply(lambda x: min_value + (max_value-min_value) * (x.astype(float) - min) / (max - min))
        return input_data