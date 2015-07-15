'''
calculate profit

Created on 2015/07/15

@author: Daytona
'''

import numpy as np
class profitLjCao():
    def __init__(self, y_real, y_pred):
        """
        input_data
        example
        {[date,real,pred], [2011-1-1,80,81], [2011-1-2,81,83]}
        """
        self.real = y_real
        self.pred = y_pred
        
    def Profit(self):
            '''
            calculate profit
            '''
            n = len(self.real)
            value = 100
            for i in range(n):
                if self.real[i] * self.pred[i] > 0 :
                    value =  value * (1+np.abs(self.real[i])/100)
                else:
                    value = value * (1-np.abs(self.real[i])/100)
            return (value-100) / 100
        
    def ProfitTimeSeries(self):
        '''
        calculate profit change with time
        '''
        n = len(self.real)
        value = 100
        profit_time = []
        profit_time.append(0)
        for i in range(n):
            if self.real[i] * self.pred[i] > 0 :
                value =  value * (1+np.abs(self.real[i])/100)
            else:
                value = value * (1-np.abs(self.real[i])/100)
            profit_time.append((value-100) / 100)
        return profit_time
