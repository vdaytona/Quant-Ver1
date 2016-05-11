'''
#Test of Direct Reinforcement Trading based on paper
"Learning to Trade via Direct Reinforcement"

Utility function use as wealth directly
return = prize(t) - prize(t-1)
input only return of commodity of each time
target value : the return of perfect execution decision

Main flow :
1. Add target value to the training set, leave the decision F blank, which will be filled when doing online learning
2. Learning process
    2.1 Manually build one layer RNN and a output layer calculate by the Rt(Ft, Ft-1), reference "Deep direct reinforcement learning for financial signal representatoin and trading"
    2.2 Learning the parameter
        2.2.1 feed the first time series data
        2.2.2 calculate the derivative of each parameter using the method of "adding a small number to the para, and calculate the difference" 
        2.2.2 update all the parameters
        2.2.3 feed the next time series data
        2.2.4 terminate until no data
3. Training data is used as first 2000 days, then update the parameters using step 3 after each 100 days.
4. Used the parameters in trained model to make decision 

Created on 19 Apr 2016

@author: purewin7
'''

import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from __builtin__ import str

class agent():
    # to store the wealth, and decision function to make trading dicision
    def __init__(self, initial_wealth):
        self.__return = []
        self.__wealth = []
        self.__utility = []
        pass

class model() :
    # parameter, calculate and the derivative
    def __init__(self, training_interval, ret_series):
        # parameter need to be optimized
        self.__training_interval = training_interval
        self.__ret_series = ret_series
        self.__u = []
        self.__w = []
        self.__v = []
        self.__df_du = []
        self.__df_dw = []
        self.__df_dv = []

        # constant
        self.__position_size = 1.0
        self.__transaction_cost = 0.005
        self.__initial_wealth = 10000.0
        self.__learning_rate = 5000

        # sequential data
        self.__decision_function = []
        self.__return = []
        
    def get_u(self):
        return self.__u

    def get_v(self):
        return self.__v

    def get_w(self):
        return self.__w
    
    def get_decision_function(self):
        return self.__decision_function
    
    def initial_para(self):
        self.__u.append(1.0 / 22.0)
        self.__w.append(1.0  / 220.0)
        new_v = []
        for i in range(self.__training_interval) :
            new_v.append(1.0 / 22.0)
        self.__v.append(new_v)
        
    
    def calculate_decision_F(self):
        # calculate initial F(t) when a new loop start
        if len(self.__decision_function) == 0 :
            self.initial_para()
            new_f = 0.0
            for i in range(self.__training_interval) :
                new_f += self.__v[0][i] * self.__ret_series[0 + i]
            new_f += self.__w[0]
        else :
            j = len(self.__decision_function)
            new_f = 0.0
            for i in range(self.__training_interval):
                new_f += self.__v[-1][i] * self.__ret_series[j + i]
            new_f += self.__w[-1] + self.__decision_function[-1] * self.__u[-1]
        self.__decision_function.append(math.tanh(new_f))
        
    def calculate_return(self):
        j = len(self.__decision_function) - 1
        ret_t = self.__ret_series[j + self.__training_interval-1]
        if len(self.__decision_function) == 1 :
            new_ret = self.__decision_function[-1] * ret_t * self.__position_size
        else :
            new_ret = self.__decision_function[-1] * ret_t - self.__transaction_cost * abs(self.__decision_function[-1]-self.__decision_function[-2])
            new_ret = new_ret * self.__position_size
        #print "return : " + str(ret_t)
        self.__return.append(new_ret)
    
    def update_para(self):
        # calculate the derivative
        step = 0.0001
        if len(self.__u) > 1 :
            self.update_u(step)
            self.update_w(step)
            self.update_v(step)
        else :
            self.__u.append(1.0 / 22.0)
            self.__w.append(1.0  / 220.0)
            self.__v.append(self.__v[-1])
        
    
    def update_u(self, step):
        # calculate the pdR_pdu
        delta_u = self.__u[-1] * (1+step)
        j = len(self.__decision_function) - 1
        ret_t = self.__ret_series[j + self.__training_interval-1]        
        delta_f = 0.0
        for i in range(self.__training_interval) :
            delta_f += self.__v[-1][i] * self.__ret_series[j + i]
        delta_f += self.__w[-1] + self.__decision_function[-2] * delta_u
        delta_f = math.tanh(delta_f)
        delta_ret = self.calculate_delta_Rt(delta_f,ret_t)
        pd_u = (delta_ret - self.__return[-1]) / step
        
        print "f " + str(self.__decision_function[-1])
        print "delta f "+ str(delta_f)
        print "ret " + str(self.__return[-1])
        print "delta_ret " + str(delta_ret)
        print "real ret : " + str(ret_t)
        print "pd_U " + str(pd_u)
        
        new_u = self.__u[-1] * (1 + pd_u * self.__learning_rate)
        self.__u.append(new_u)
    
    def update_w(self, step):
        # calculate the pdR_pdw
        delta_w = self.__w[-1] * (1+step)
        j = len(self.__decision_function)-1
        ret_t = self.__ret_series[j + self.__training_interval-1]
        delta_f = 0.0
        for i in range(self.__training_interval) :
            delta_f += self.__v[-1][i] * self.__ret_series[j + i]
        delta_f += delta_w + self.__decision_function[-2] * self.__u[-2]
        delta_f = math.tanh(delta_f)
        delta_ret = self.calculate_delta_Rt(delta_f,ret_t)
        pd_w = (delta_ret - self.__return[-1]) / step
        new_w = self.__w[-1] * (1 + pd_w * self.__learning_rate)
        self.__w.append(new_w)
        print "pd_w " + str(pd_w)
    
    def update_v(self, step):
        new_v = []
        for k in range(self.__training_interval) :
            # calculate the pdR_pdv for each v
            delta_v = self.__v[-1][k] * (1+step)
            j = len(self.__decision_function) - 1
            ret_t = self.__ret_series[j + self.__training_interval-1]
            delta_f = 0.0
            #print self.__ret_series[j + k]
            for i in range(self.__training_interval) :
                if i == k :
                    delta_f += delta_v * self.__ret_series[j + i]
                else:
                    delta_f += self.__v[-1][i] * self.__ret_series[j + i]
            delta_f += self.__w[-2] + self.__decision_function[-2] * self.__u[-2]
            delta_f = math.tanh(delta_f)
            #print delta_f
            delta_ret = self.calculate_delta_Rt(delta_f,ret_t)
            #print delta_ret
            pd_v = (delta_ret - self.__return[-1]) / step
            v = self.__w[-1] * (1 + pd_v * self.__learning_rate)
            new_v.append(v)
            print "pd_v " + str(pd_v)
        self.__v.append(new_v)
        
    
    def calculate_delta_Rt(self,new_ft,ret):
        if len(self.__decision_function) == 1 :
            new_ret = new_ft  * ret * self.__position_size
            return new_ret
        else :
            new_ret = new_ft  * ret - self.__transaction_cost * abs(new_ft - self.__decision_function[-2])
            new_ret = new_ret * self.__position_size
            return new_ret

def run():
    # 1. get time data series
    data = pd.read_csv("../Data/GBPUSD30.csv",header=None)
    close = data[5].values
    ret = close[1:] - close[:-1]
    training_series = ret[:-200]
    print len(training_series)
    training_interval = 20
    DL_model = model(training_interval = training_interval, ret_series = training_series)
    #for i in range(len(training_series) - 20) :
    for i in range(50000) :
        print i
        DL_model.calculate_decision_F()
        DL_model.calculate_return()
        DL_model.update_para()
    
    #===========================================================================
    # print DL_model.get_u()
    # plt.plot(range(len(DL_model.get_u())),DL_model.get_u())
    # plt.show()
    # plt.plot(range(len(DL_model.get_w())),DL_model.get_w())
    # plt.show()
    # plt.plot(range(len(DL_model.get_v())),map(list, zip(*DL_model.get_v()))[-5])
    # plt.show()
    # plt.plot(range(len(DL_model.get_decision_function())),DL_model.get_decision_function())
    # plt.show()
    #===========================================================================
    
    pass
        

if __name__ == "__main__": run()
