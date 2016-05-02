'''
#Test of Direct Reinforcement Trading based on paper
Learning to Trade via Direct Reinforcement

# Utility function use as wealth directly
# return = prize(t) - prize(t-1)
# input only return of commodity of each time

flow:
1. Initialize parameter
2. Iteration:
    2.1 compute F(t) using F(t-1) and theta(t-1)
    2.2 compute U(t) using F(t)
    2.3 optimizing theta(t) to maximum U(t) and got optimized F(t)
3. get optimized theta(tk)
4. test theat(tk) to trade test data

Created on 19 Apr 2016

@author: purewin7
'''

import pandas as pd
import math
import numpy as np

class parameters_container():
    
    def __init__(self, training_interval):
        # parameter need to be optimized
        self.training_interval = training_interval
        self.__u = []
        self.__w = []
        self.__v = [[]]
        self.__ret_series = [[]]
        self.__df_du = []
        self.__df_dw = []
        self.__df_dv = []
        
        # constant
        self.__position_size = 5
        self.__transcation_cost = 0.005    
        self.__initial_wealth = 10000.0    
        
        # sequential data
        self.__decision_function = []
        self.__return = []
        self.__wealth = []
        self.__utility = []
    
    def update_value(self, new_value, item):
        if item == "decision":
            self.__decision_function.append(new_value)
        elif item == "return" :
            self.__return.append(new_value)
        elif item == "wealth" :
            self.__wealth.append(new_value)
        elif item == "utility" :
            self.__utility.append(new_value)
    
    def get_transcation_cost(self):
        return self.__transcation_cost
    
    def get_decision_function(self):
        return self.__decision_function
    
    def get_return(self):
        return self.__return
    
    def get_position_size(self):
        return self.__position_size
    
    def get_u(self):
        return self.__u
    
    def get_new_v(self):
        new_v = []
        for i in range(self.training_interval) :
            new_v.append(1)
        return new_v
    
    def add__ret_series(self,ret_series):
        self.__ret_series.append(ret_series)
        
    def calculate_decision_function(self, ret_series):
        new_u = 1.0
        new_w = 1.0
        new_v = self.get_new_v()
        
        if len(self.__v) == 0 :
            new_f = 0.0
            for i in range(self.training_interval) :
                new_f += new_v[i] * ret_series[i]
            new_f += new_w
        else :
            new_f = 0.0
            for i in range(self.training_interval) :
                new_f += new_v[i] * ret_series[i]
            new_f += new_w + self.__decision_function[-1] * new_u
        self.__u.append(new_u)
        self.__w.append(new_w)
        self.__v.append(new_v)
        self.__decision_function.append(math.tanh(new_f))
    
    def calculate_return(self, ret_series):
        new_ret = self.__decision_function[-2] * ret_series[-1] - self.__transcation_cost * abs(self.__decision_function[-1]-self.__decision_function[-2])
        new_ret = new_ret * self.__position_size
        self.__return.append(new_ret)
    
    def calculate_wealth(self):
        self.__wealth.append(sum(self.__return))
    
    def calculate_utility(self):
        self.__utility = self.__wealth

def optimization_theta(parameters, new_f, new_return, ret_series):
    # initial delta_parameters:
    delta_v = []
    delta_w = 0.0
    delta_u = 0.0
    # set utility = R(t)
    utility = parameters.get_return()[-1]
    
    dU_dR = \
    1
    dRt_dFt = \
    parameters.get_transaction_cost() * parameters.get_position_size() \
    if parameters.get_decision_function()[-1] > parameters.get_decision_function()[-2] else \
    - parameters.get_transaction_cost() * parameters.get_position_size()
    # (1-tanh)^2 = tanh
    tanh_square = np.power(1-parameters.get_decision_function()[-1],2)
    pdFt_pdut = tanh_square * parameters.get_decision_function()[-2]
    pdFt_pdvt = tanh_square * ret_series
    pdFt_pdwt = tanh_square
    # Ft1 -> F(t-1)
    pdFt_pdFt1 = tanh_square * parameters.get_u()[-1]
    
    dRt_dFt1_mulitple_dFt1_dut1 = 2
    pass


def calculatedf_dtheta(parameters, ):
    du = 0.0
    dv = 0.0
    dw = 0.0
    
    for i in range(1, len(parameters.get_decision_function())) :
        
        pass
    pass

def trainingDL(parameters, ret_series, training_interval):
    for i in range(len(ret_series)-training_interval) :
        # calculate new decision function
        new_f = parameters.calculate_decision_function(ret_series[i:i+training_interval])
        parameters.
        if i == 0 :
            parameters.calculate_decision_function.append(new_f)
            parameters.update_value(new_f,"decision")
            parameters.update_value(0.0,"return")
            parameters.update_value(parameters.__wealth,"wealth")
            parameters.update_value(0.0,"utility")
        else :
            # calculate U
            new_return = parameters.calculate_return(ret_series[i:i+training_interval])
            theta = optimization_theta(parameters, new_f,new_return, ret_series)
    pass

def run():
    # 1. get time data series 
    data = pd.read_csv("./Data/GBPUSD30.csv",header=None)
    close = data[5].values
    print close
    print close[1:]
    print close[:-1]
    ret = close[1:] - close[:-1]
    training_series = ret[:-200]
    training_interval = 60
    parameters = parameters_container(training_interval)
    
    # training 
    trainingDL(parameters,training_series,training_interval)
    
    
    
    
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
            # get decision_function
            
            
            # get return
            
            # get multiplicative profit as utility
                        
        if len(data) - i < 2480 :
            break

if __name__ == "__main__": run()
