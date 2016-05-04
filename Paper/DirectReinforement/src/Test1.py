'''
#Test of Direct Reinforcement Trading based on paper
"Learning to Trade via Direct Reinforcement"

# Utility function use as wealth directly
# return = prize(t) - prize(t-1)
# input only return of commodity of each time

Main flow:
1. Prepare time series data as input and initialize parameter
position size , transaction cost, initial wealth
2. Iteration:
    2.1 compute F(t) using F(t-1) and theta(t-1)
    2.2 compute U(t) using F(t)
    2.3 optimizing theta(t) to maximum U(t) through f(t) and got optimized theta(t)
    2.4 training is a rolling window training of 60 days
3. get optimized theta(tk)
4. test theat(tk) to trade test data

Calculation d_U(t) / d_theta(t) flow: (pd : partial difference)
d_U(t) / d_theta(t) ~= dU(t) / dR(t) * (dR(t) / dF(t) * dF(t) / dtheta(t) + dR(t) / dF(t-1) * dF(t-1) / dtheta(t-1))
where
dF(t) / dtheta(t) ~= pd_F(t) / pd_theta(t) + pd_F(t) / pd_F(t-1) * dF(t-1) / dtheta(t-1)
and
theta(t) = {u(t) , v(t) , w(t)}

Optimize flow of U(t) :
1. calculate d_U(t) / d_theta(t)
2. update theta with p * d_U(t) / d_theta(t), p is learning parameter until d_U(t) / d_theta(t) -> 0

Created on 19 Apr 2016

@author: purewin7
'''

import pandas as pd
import math
import numpy as np
from __builtin__ import str

class parameters_container():

    def __init__(self, training_interval):
        # parameter need to be optimized
        self.training_interval = training_interval
        self.__u = []
        self.__w = []
        self.__v = []
        self.__ret_series = []
        self.__df_du = []
        self.__df_dw = []
        self.__df_dv = []

        # constant
        self.__position_size = 5.0
        self.__transaction_cost = 0.005
        self.__initial_wealth = 10000.0
        self.__learning_rate = 1.0

        # sequential data
        self.__decision_function = []
        self.__return = []
        self.__wealth = []
        self.__utility = []

    def get_transcation_cost(self):
        return self.__transaction_cost

    def get_decision_function(self):
        return self.__decision_function

    def get_return(self):
        return self.__return

    def get_position_size(self):
        return self.__position_size

    def get_u(self):
        return self.__u

    def get_v(self):
        return self.__v

    def get_w(self):
        return self.__w

    def get_new_v(self):
        new_v = []
        for i in range(self.training_interval) :
            new_v.append(1.0)
        return new_v

    def add__ret_series(self,ret_series):
        self.__ret_series.append(ret_series)

    def calculate_new_decision_function(self, ret_series):
        # calculate initial F(t) when a new loop start
        new_u = 1.0
        new_w = 1.0
        new_v = self.get_new_v()
        if len(self.__u) == 0 :
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

    def calculate_new_return(self, ret):
        if len(self.__decision_function) == 1 :
            self.__return.append(0.0)
        else :
            new_ret = self.__decision_function[-1] * ret - self.__transaction_cost * abs(self.__decision_function[-1]-self.__decision_function[-2])
            new_ret = new_ret * self.__position_size
            self.__return.append(new_ret)

    def calculate_new_wealth(self):
        self.__wealth.append(sum(self.__return))

    def calculate_new_utility(self):
        # we set utility at t = return at time
        self.__utility.append(self.__return[-1])

    def calculate_new_para(self,ret_series,ret) :
        self.calculate_new_decision_function(ret_series)
        self.calculate_new_return(ret)
        self.calculate_new_wealth()
        self.calculate_new_utility()

    def update_decision_function(self,ret_series):
        if len(self.__decision_function) == 1 :
            new_f = 0.0
            for i in range(self.training_interval) :
                new_f += self.__v[-1][i] * ret_series[i]
            new_f += self.__w[-1]
        else :
            new_f = 0.0
            for i in range(self.training_interval) :
                new_f += self.__v[-1][i] * ret_series[i]
            new_f += self.__w[-1] + self.__decision_function[-1] * self.__u[-1]
        self.__decision_function[-1] = math.tanh(new_f)

    def update_return(self,ret):
        if len(self.__decision_function) == 1 :
            new_ret = self.__decision_function[-1]
        else :
            new_ret = self.__decision_function[-1] * ret - self.__transaction_cost * abs(self.__decision_function[-1]-self.__decision_function[-2])
        new_ret = new_ret * self.__position_size
        self.__return[-1] = new_ret
        print new_ret

    def update_wealth(self):
        self.__wealth[-1] = sum(self.__return)

    def update_utility(self):
        self.__utility[-1] = self.__return[-1]

    def update_para(self,ret_series, ret):
        self.update_decision_function(ret_series)
        self.update_return(ret)
        self.update_utility()
        self.update_wealth()

    def calculate_d_Rt_d_Ft(self) :
        if len(self.__decision_function) == 1 :
            return -1.0 * self.__position_size * self.__transaction_cost
        else :
            if self.__decision_function[-1] > self.__decision_function[-2] :
                return -1.0 * self.__position_size * self.__transaction_cost
            else :
                return self.__position_size * self.__transaction_cost

    def calculate_d_Rt_d_Ftminus(self, ret) :
        if len(self.__decision_function) == 1 :
            return 0.0
        else :
            if self.__decision_function[-1] > self.__decision_function[-2] :
                return self.__position_size * (ret + self.__transaction_cost)
            else :
                return self.__position_size * (ret - self.__transaction_cost)

    def calculate_pd_Ft_pd_theata(self) :
        k = np.power(1-self.__decision_function[-1],2)
        if len(self.__decision_function) == 1:
            u = 0.0
        else :
            u = k * self.__decision_function[-2]
        v = self.list_multiple(self.__v[-1],k)
        w = k
        return u, v, w

    def calculate_d_Ftminus_d_thetatminus(self, *kwagrs) :
        if len(self.__decision_function) >= 2 :
            k = np.power(1-self.__decision_function[-2],2)
            v = self.list_multiple(self.__v[-2],k)
            w = k
            if len(self.__decision_function) == 2 :
                u = 1.0
            else :
                u = k * self.__decision_function[-3]
        else :
            u = 1.0
            v = self.get_new_v()
            w = 1.0
        return u, v, w

    def calculate_pd_Ft_pd_Ftminus(self) :
        k = np.power(1-self.__decision_function[-1],2)
        return k * self.__u[-1]

    def calculate_d_Ft_d_theata(self) :
        pd_Ft_pd_theata = self.calculate_pd_Ft_pd_theata()
        pd_Ft_pd_Ftminus = self.calculate_pd_Ft_pd_Ftminus()
        d_Ftminus_d_thetaminus = self.calculate_d_Ftminus_d_thetatminus()
        dFt_dut = pd_Ft_pd_theata[0] + pd_Ft_pd_Ftminus * d_Ftminus_d_thetaminus[0]
        dFt_dvt = self.list_add(pd_Ft_pd_theata[1], self.list_multiple(d_Ftminus_d_thetaminus[1],pd_Ft_pd_Ftminus))
        dFt_dwt = pd_Ft_pd_theata[2] + pd_Ft_pd_Ftminus * d_Ftminus_d_thetaminus[2]
        return dFt_dut, dFt_dvt, dFt_dwt

    def calculate_dUt_dtheata(self, ret_series, ret):
        # here, Ut == Rt
        d_Rt_d_Ft = self.calculate_d_Rt_d_Ft()
        d_Ft_d_theata = self.calculate_d_Ft_d_theata()
        d_Rt_d_Ftminus = self.calculate_d_Rt_d_Ftminus(ret)
        d_Ftminus_d_thetaminus = self.calculate_d_Ftminus_d_thetatminus()
        d_Ut_dRt = 1.0
        d_Ut_d_u = d_Ut_dRt * d_Rt_d_Ft * d_Ft_d_theata[0] + d_Rt_d_Ftminus * d_Ftminus_d_thetaminus[0]
        d_Ut_d_v = self.list_add(self.list_multiple(self.list_multiple(d_Ft_d_theata[1], d_Rt_d_Ft),d_Ut_dRt), \
                                 self.list_multiple(d_Ftminus_d_thetaminus[1], d_Rt_d_Ftminus))
        d_Ut_d_w = d_Ut_dRt * d_Rt_d_Ft * d_Ft_d_theata[2] + d_Rt_d_Ftminus * d_Ftminus_d_thetaminus[2]
        print "Calculated dUt_du : " + str(d_Ut_d_u)
        # to calcualte the dUt_du using plus a minor change to the variable
        estimated_dUt_du = self.derivitive_evaluation("u",ret_series, ret,0.000001)
        print "Ref dUt_du : " + str(estimated_dUt_du)
        print d_Ut_d_v
        print d_Ut_d_w
        self.__u[-1] = self.__learning_rate * d_Ut_d_u + self.__u[-1]
        self.__v[-1] = self.list_add(self.list_multiple(d_Ut_d_v,self.__learning_rate), self.__v[-1])
        self.__w[-1] = self.__learning_rate * d_Ut_d_w + self.__w[-1]

        self.update_para(ret_series, ret)
        #print "sum return : " + str(self.__wealth[-1])
        return d_Ut_d_u, d_Ut_d_v, d_Ut_d_w

    def list_multiple(self,list,multiplier) :
        return [x * multiplier for x in list]

    def list_add(self,list1,list2):
        for i in range(len(list1)) :
            list1[i] = list1[i] + list2[i]
        return list1

    def derivitive_evaluation(self, item, ret_series, ret, step) :
        return_now = self.__return[-1]
        if item == "u" :
            # calculate initial F(t) when a new loop start
            if len(self.__u) == 1 :
                new_f = 0.0
                for i in range(self.training_interval) :
                    new_f += self.__v[-1][i] * ret_series[i]
                    new_f += self.__w[-1]
            else :
                new_f = 0.0
                for i in range(self.training_interval) :
                    new_f += self.__v[-1][i] * ret_series[i]
                    new_f += self.__w[-1] + self.__decision_function[-2] * self.__u[-1] * (1 + step)
            new_ret = self.calculate_new_Rt_for_evaluation(math.tanh(new_f),ret)
            print "new_ret : " + str(new_ret)
            print "return_now : " + str(return_now)
            return (new_ret - return_now) / return_now
        elif item == "v":
            return None
        elif item == "w":
            return None
        else :
            return None

    def calculate_new_Rt_for_evaluation(self,new_ft,ret):
        if len(self.__decision_function) == 1 :
            return 0.0
        else :
            new_ret = new_ft  * ret - self.__transaction_cost * abs(new_ft - self.__decision_function[-2])
            new_ret = new_ret * self.__position_size
            return new_ret

def trainingDL(parameters, ret_series, training_interval):
    threshold = 0.01
    for i in range(len(ret_series)-training_interval-1) :
        print i
        # calculate new decision function
        parameters.calculate_new_para(ret_series[i:i + training_interval],ret_series[i + training_interval])
        if i > 0 :
            Flag = True
            loop = 0
            while loop < 10 :
                update_result = parameters.calculate_dUt_dtheata(ret_series[i:i + training_interval],ret_series[i + training_interval])
                #print update_result[0]
                #print update_result[1]
                #print update_result[2]
                if abs(update_result[0]) < threshold and abs(update_result[2]) < threshold and check_list_threshold(update_result[1],threshold):
                    Flag = False
                loop += 1
                #print loop
        print "decision F: " + str(parameters.get_decision_function()[-1])
        print "U : " + str(parameters.get_u()[-1])
        print "V : " + str(parameters.get_v()[-1])
        print "W : " + str(parameters.get_w()[-1])
        print "return : " + str(parameters.get_return()[-1])

def check_list_threshold(input,threshold) :
    Flag = True
    for i in input :
        if abs(i) > threshold :
            Flag = False
            break
    return Flag


def run():
    # 1. get time data series
    data = pd.read_csv("../Data/GBPUSD30.csv",header=None)
    close = data[5].values
    print close
    ret = close[1:] - close[:-1]
    training_series = ret[:-200]
    training_interval = 60
    parameters = parameters_container(training_interval)

    # training
    print len(training_series)
    trainingDL(parameters,training_series,training_interval)

    '''
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
    '''

if __name__ == "__main__": run()
