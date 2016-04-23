'''
#Test of Direct Reinforcement Trading based on paper
Learning to Trade via Direct Reinforcement

# Utility function use as wealth directly
# return = prize(t) - prize(t-1)
# input only return of commodity of each time


Created on 19 Apr 2016

@author: purewin7
'''

import pandas as pd
import math

class parameters_container():
    
    def __init__(self):
        # parameter need to be optimized
        self.__u = 0.1
        self.__w = 1
        self.__v = []
        
        # constant
        self.__position_size = 5
        self.__transcation_cost = 0.005    
        self.__initial_wealth = 10000.0    
        
        # sequential data
        self.__desicision_function = []
        self.__return = []
        self.__wealth = []
        self.__utility = []
        self.__wealth = []
        
    def get_transcation_cost(self):
        return self.__transcation_cost
    
    def get_desicision_function(self):
        return self.__desicision_function
    
    def calculate_desicision_functoin(self, ret_series):
        if len(ret_series) == 1 :
            self.__v.append(0.5)
            new_f = self.__v[0] * ret_series[0] + self.__w
        else :
            new_f = self.u * self.__desicision_function[-1] + self.__w
            self.__v.append(0.5)
            for i in range(len(ret_series)) :
                new_f += self.__v[i] * ret_series[i]
        new_f = math.tanh(new_f)
        self.__desicision_function.append(new_f)
    
    def calculate_return(self, ret_series):
        if len(ret_series) == 1 :
            self.__return.append(0.0)
        else :
            new_ret = self.__desicision_function[-2] * ret_series[-1] -  self.__desicision_function * abs(self.__desicision_function[-1]-self.__desicision_function[-2])
            new_ret = new_ret * self.__position_size
            self.__return.append(new_ret)
    
    def calculate_wealth(self):
        self.__wealth.append(sum(self.__return))
    
    def calculate_utility(self):
        self.__utility = self.__wealth

def run():
    # 1. get time data series 
    data = pd.read_csv("./Data/GBPUSD30.csv",header=None)
    close = data[5].values
    print close
    print close[1:]
    print close[:-1]
    ret = close[1:] - close[:-1]
    print sum(ret)
    
    parameteres = parameters_container()
    print parameteres.get_transcation_cost()
    
    # 2. Iteration
    for i in range(0, len(ret),480) :
        # Generate test-set based on rolling_window
        # 2000 data for train, next 480 for test, and move the window for 480 point, and then train 480-2480 data, and test 2481-2960, and iteration
        if len(ret) - i > 2480 :
            start_point = i
            end_point = i + 2480
        else :
            start_point =len(ret) - 2480
            end_point = len(ret)
            i = len(ret)
        for t in range(start_point, end_point) :
            pass
            # get desicision_function
            
            
            # get return
            
            # get multiplicative profit as utility
                        
        if len(data) - i < 2480 :
            break

if __name__ == "__main__": run()
