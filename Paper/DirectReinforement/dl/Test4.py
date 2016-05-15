'''
Based on Test3, add data preprocessing
Test of Direct Reinforcement Trading based on paper
"Learning to Trade via Direct Reinforcement"

Loop the parameter : learning rate , and high/low trading threshold to find best parameter combination

Utility function use as wealth directly
return = prize(t) - prize(t-1)
input only return of commodity of each time
target value : the return of perfect execution decision

Main flow :
1. Learning process
    1.1 Manually build one layer RNN and a output layer calculate by the Rt(Ft, Ft-1), reference "Deep direct reinforcement learning for financial signal representatoin and trading"
    1.2 Learning the parameter
        1.2.1 feed the first time series data
        1.2.2 calculate the derivative of each parameter using the method of "adding a small number to the para, and calculate the difference" to maximum the Rt
        1.2.2 update all the parameters
        1.2.3 feed the next time series data
        1.2.4 terminate until no data
2. Used the parameters in trained DLmodel to make decision 


Created on 19 Apr 2016

@author: purewin7
'''

import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import random as rd


RETURN_SERIES_MULTIPLIER = 1.0
DELTA_DEV = 0.0001
UPDATE_STEP = 1.0
LEARNING_RATE = 0.05
TRAINING_LOOP = 60000
TRAINING_UNITS = 20
HIGH_Threshold = 0.3
LOW_Threshold = -0.3

class agent():
    # to store the wealth, and decision function to make trading dicision
    def __init__(self, initial_wealth):
        self.__return = []
        self.__wealth = []
        self.__utility = []
        pass

class DLmodel() :
    # parameter, calculate and the derivative
    def __init__(self, TRAINING_UNITS, real_ret_series, ret_series):
        # parameter need to be optimized
        self.__training_interval = TRAINING_UNITS
        self.__ret_series = ret_series
        self.__real_ret_series = real_ret_series
        self.__u = []
        self.__w = []
        self.__v = []
        self.__df_du = []
        self.__df_dw = []
        self.__df_dv = []

        # constant
        self.__position_size = 1
        self.__transaction_cost = 0.0002
        self.__initial_wealth = 50000.0
        
        # sequential data
        self.__decision_function = []
        self.__return = []
        self.__real_decision_function = []
        self.__real_return = []
        
    def get_u(self):
        return self.__u

    def get_v(self):
        return self.__v

    def get_w(self):
        return self.__w
    
    def get_decision_function(self):
        return self.__decision_function
    
    def get_real_decision_function(self):
        return self.__real_decision_function
    
    def get_return(self):
        return self.__return
    
    def get_real_return(self):
        return self.__real_return
    
    def initial_para(self):
        self.__u.append(1.0  / float(2 + TRAINING_UNITS))
        self.__w.append(1.0  / float(2 + TRAINING_UNITS))
        #self.__u.append(rd.gauss(0,1))
        #self.__w.append(rd.gauss(0,1))
        new_v = []
        for i in range(self.__training_interval) :
            new_v.append(1.0  / float(2 + TRAINING_UNITS))
            #new_v.append(rd.gauss(0,1))
        self.__v.append(new_v)
    
    def calculate_decision_F(self):
        # calculate initial F(t) when a new TRAINING_LOOP start
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
        self.calculate_real_decision_F()
    
    def calculate_real_decision_F(self):
        #calculate initial F(t) when a new TRAINING_LOOP start
        #new_f = self.__decision_function[-1]
        
        j = len(self.__real_decision_function)
        new_f = self.__w[-1]
        for i in range(self.__training_interval) :
                new_f += self.__v[-1][i] * self.__ret_series[j + i]
        if len(self.__real_decision_function) != 0 :
            new_f += self.__real_decision_function[-1] * self.__u[-1]
        new_f = math.tanh(new_f)
        
        if new_f > HIGH_Threshold :
            self.__real_decision_function.append(1)
        elif new_f < LOW_Threshold :
            self.__real_decision_function.append(-1)
        else :
            self.__real_decision_function.append(0)
        
    def calculate_return(self):
        j = len(self.__decision_function) - 1
        ret_t = self.__ret_series[j + self.__training_interval-1]
        if len(self.__decision_function) == 1 :
            real_ret = 0.0
        else :
            real_ret = self.__decision_function[-2] * ret_t - self.__transaction_cost * abs(self.__decision_function[-1]-self.__decision_function[-2])
        real_ret = real_ret * self.__position_size
        #print "return : " + str(ret_t)
        self.__return.append(real_ret)
        self.calcualte_real_return()
        
    def calcualte_real_return(self):
        j = len(self.__real_decision_function) - 1
        ret_t = self.__real_ret_series[j + self.__training_interval - 1]
        if len(self.__real_decision_function) == 1 :
            new_ret = 0.0
        else :
            new_ret = self.__real_decision_function[-2] * ret_t - self.__transaction_cost * abs(self.__real_decision_function[-1]-self.__real_decision_function[-2])
            new_ret = new_ret * self.__position_size
        #print "return : " + str(ret_t)
        self.__real_return.append(new_ret)
        
    
    def update_para(self):
        # calculate the derivative
        
        if len(self.__u) > 1 :
            new_u = self.update_u(DELTA_DEV, UPDATE_STEP)
            new_w = self.update_w(DELTA_DEV, UPDATE_STEP)
            new_v = self.update_v(DELTA_DEV, UPDATE_STEP)
            self.__u.append(new_u)
            self.__w.append(new_w)
            self.__v.append(new_v)
        else :
            self.__u.append(1.0 / float(2 + TRAINING_UNITS))
            self.__w.append(1.0  / float(2 + TRAINING_UNITS))
            self.__v.append(self.__v[-1])
            #self.__u.append(rd.gauss(0,1))
            #self.__w.append(rd.gauss(0,1))
            #self.__v.append(self.__v[-1])
        
    
    def update_u(self, DELTA_DEV, UPDATE_STEP):
        # calculate the pdR_pdu
        delta_u = self.__u[-1] + DELTA_DEV
        j = len(self.__decision_function) - 1
        ret_t = self.__ret_series[j + self.__training_interval-1]     
        delta_f = 0.0
        for i in range(self.__training_interval) :
            delta_f += self.__v[-1][i] * self.__ret_series[j + i]
        if len(self.__decision_function) == 1 :
            delta_f += self.__w[-1]
        else :
            delta_f += self.__w[-1] + self.__decision_function[-2] * delta_u
        delta_f = math.tanh(delta_f)
        delta_ret = self.calculate_delta_Rt(delta_f,ret_t)
        pd_u = (delta_ret - self.__return[-1]) / DELTA_DEV
        
        #=======================================================================
        # print "f " + str(self.__decision_function[-1])
        # print "delta_f "+ str(delta_f)
        # print "ret " + str(self.__return[-1])
        # print "delta_ret " + str(delta_ret)
        # print "real ret : " + str(ret_t)
        # print "pd_U " + str(pd_u)
        #=======================================================================
        
        new_u = self.__u[-1] + pd_u * LEARNING_RATE * UPDATE_STEP
        return new_u
    
    def update_w(self, DELTA_DEV, UPDATE_STEP):
        # calculate the pdR_pdw
        delta_w = self.__w[-1] + DELTA_DEV
        j = len(self.__decision_function)-1
        ret_t = self.__ret_series[j + self.__training_interval-1]
        delta_f = 0.0
        for i in range(self.__training_interval) :
            delta_f += self.__v[-1][i] * self.__ret_series[j + i]
        if len(self.__decision_function) == 1 :
            delta_f += delta_w
        else :
            delta_f += delta_w + self.__decision_function[-2] * self.__u[-1]        
        delta_f = math.tanh(delta_f)
        delta_ret = self.calculate_delta_Rt(delta_f,ret_t)
        pd_w = (delta_ret - self.__return[-1]) / DELTA_DEV
        new_w = self.__w[-1] + pd_w * LEARNING_RATE * UPDATE_STEP
        
        #print "pd_w " + str(pd_w)
        return new_w
    
    def update_v(self, DELTA_DEV, UPDATE_STEP):
        new_v = []
        for k in range(self.__training_interval) :
            # calculate the pdR_pdv for each v
            delta_v = self.__v[-1][k] + DELTA_DEV
            j = len(self.__decision_function) - 1
            ret_t = self.__ret_series[j + self.__training_interval-1]
            delta_f = 0.0
            #print self.__ret_series[j + k]
            for i in range(self.__training_interval) :
                if i == k :
                    delta_f += delta_v * self.__ret_series[j + i]
                else:
                    delta_f += self.__v[-1][i] * self.__ret_series[j + i]
            if len(self.__decision_function) == 1 :
                delta_f += self.__w[-1]
            else :
                delta_f += self.__w[-1] + self.__decision_function[-2] * self.__u[-1]            
            delta_f = math.tanh(delta_f)
            #print delta_f
            delta_ret = self.calculate_delta_Rt(delta_f,ret_t)
            #print delta_ret
            pd_v = (delta_ret - self.__return[-1]) / DELTA_DEV
            v = self.__v[-1][k] + pd_v * LEARNING_RATE * UPDATE_STEP
            new_v.append(v)
            #print "pd_v" + str(k) + " " + str(pd_v)
        return new_v
        
    
    def calculate_delta_Rt(self,new_ft,ret):
        if len(self.__decision_function) == 1 :
            return 0.0
        else :
            new_ret = self.__decision_function[-2]  * ret - self.__transaction_cost * abs(new_ft - self.__decision_function[-2])
            new_ret = new_ret * self.__position_size
            return new_ret

def return_preprocess(return_series):
    #===========================================================================
    # # standardized to [-1 : 1]
    # max_ret = max(return_series)
    # min_ret = min(return_series)
    # print max_ret
    # print min_ret
    # positive_scale = 1 / max_ret
    # negative_scale = 1 / abs(min_ret)
    # new_ret = []
    # for i in return_series :
    #     if i > 0:
    #         new_ret.append(i * positive_scale * 10)
    #     elif i < 0 :
    #         new_ret.append(i * negative_scale * 10)
    #     else :
    #         new_ret.append(0.0)
    #===========================================================================
            
    # divide by std
    return_series = np.array(return_series)
    std = np.std(return_series)
    return_series = return_series / (std * RETURN_SERIES_MULTIPLIER)
    new_ret = return_series.tolist()
    #print new_ret
    return new_ret

def run():
    # 1. get time data series
    data = pd.read_csv("../Data/GBPUSD30.csv",header=None)
    close = data[5].values
    ret = close[1:] - close[:-1]
    calibrated_ret = return_preprocess(ret)
    
    training_series = calibrated_ret[:-200]
    real_return_series = ret[:-200]
    #print len(training_series)
    
    
    LEARNING_RATE_LIST = []
    for i in range(50) :
        LEARNING_RATE_LIST.append(0.01 + 0.02 * i)
    LEARNING_RATE_LIST.append(1.0)
    for i in range(2,32,2) :
        LEARNING_RATE_LIST.append(float(i))
    HIGH_THRESHOLD_LIST = []
    LOW_THRESHOLD_LIST = []
    for i in range(1, 10) :
        HIGH_THRESHOLD_LIST.append( i / 10.0)
        LOW_THRESHOLD_LIST.append( i / -10.0)
    
    #print LEARNING_RATE_LIST
    #print HIGH_THRESHOLD_LIST
    #print LOW_THRESHOLD_LIST
    loop = len(LEARNING_RATE_LIST) * len(HIGH_THRESHOLD_LIST)
    loop_count = 1
    
    result = pd.DataFrame()
    learning_list = []
    threshold_list = []
    return_list = []
    trade_count_list = []
    
    print LEARNING_RATE_LIST
    print HIGH_THRESHOLD_LIST
    
    for learning_rate in LEARNING_RATE_LIST :
        global LEARNING_RATE, HIGH_Threshold, LOW_Threshold 
        LEARNING_RATE= learning_rate
        for threshold in range(len(HIGH_THRESHOLD_LIST)) :
            print str(loop_count) + " of " + str(loop)
            HIGH_Threshold = HIGH_THRESHOLD_LIST[threshold]
            LOW_Threshold = LOW_THRESHOLD_LIST[threshold]
            DL_model = DLmodel(TRAINING_UNITS = TRAINING_UNITS, real_ret_series = real_return_series , ret_series = training_series,)
            #for i in range(len(training_series) - 20) :
            for i in range(TRAINING_LOOP) :
                #print i
                DL_model.calculate_decision_F()
                DL_model.calculate_return()
                DL_model.update_para()
                
            accumulate_return = [1]
            for ret in DL_model.get_real_return() :
                accumulate_return.append(accumulate_return[-1] + ret)
            trading_count = 0
            for i in range(1 , len(DL_model.get_real_decision_function())-1) :
                if DL_model.get_real_decision_function()[i] != DL_model.get_real_decision_function()[i-1] :
                    trading_count += 1
            learning_list.append(LEARNING_RATE)
            threshold_list.append(HIGH_Threshold)
            return_list.append(accumulate_return[-1])
            trade_count_list.append(trading_count)          
            loop_count += 1
            del DL_model
            print accumulate_return[-1]
    
    result["LEARNING_RATE"] = learning_list
    result["THRESHOLD"] = threshold_list
    result["RETURN"] = return_list
    result["TRADE_COUNT"] = trade_count_list
    result.to_csv("./result.csv")

if __name__ == "__main__": run()