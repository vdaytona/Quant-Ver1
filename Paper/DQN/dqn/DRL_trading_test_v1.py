'''
 Deep learning reinfocement based trading
Test for the trained model

 @author: Daytona
 '''


import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd
#from keras.utils.visualize_util import  plot
import matplotlib.pyplot as plt
import copy
import datetime
import logging
from time import gmtime, strftime
import json
from keras.models import model_from_json
from gevent.monkey import WIN

ACTION_LIST = [1,0,-1]

class FX_Market():
    def __init__(self,ret_train, look_back_term, transaction_cost, close_test):
        self.__ret_train = ret_train
        self.__close_test = close_test
        self.__look_back_term = look_back_term
        self.__previous_action = 1
        self.__transaction_cost = transaction_cost
        self.__initial_wealth = 10000.0
        self.__wealth = copy.deepcopy(self.__initial_wealth)
        self.__investment_rate = 0.1
        self.__leverage = 20
        self.__share = 0.0
        self.__cash = 10000.0
        self.__enter_price = 0.0
        self.__accumulate_pips = 0.0
        self.__accumulate_return = 0.0

    def reset(self):
        self.__previous_action = 1

    def get_state(self,t):
        state = np.zeros((1,self.__look_back_term))
        state[0] = self.__ret_train[t - self.__look_back_term +  1 : t + 1]
        return state

    def get_instant_reward(self, t , action):
        # print (self.__close_test[t+1] - self.__close_test[t]) / self.__close_test[t]
        if self.__previous_action == action : # no change
            pass
        elif self.__previous_action == 1 : # open position
            investment = self.__cash * self.__investment_rate
            self.__enter_price = self.__close_test[t]
            self.__cash = self.__cash - investment
            self.__share = investment / self.__close_test[t] * (1 - self.__transaction_cost * self.__leverage)
        elif action == 1: # close position
            self.__cash += self.__share * (self.__enter_price + (self.__close_test[t] - self.__enter_price) * self.__leverage * ACTION_LIST[self.__previous_action] - self.__transaction_cost * self.__leverage)
            self.__share = 0.0
        else : # change position
            self.__cash += self.__share * (self.__enter_price + (self.__close_test[t] - self.__enter_price) * self.__leverage * ACTION_LIST[self.__previous_action] - self.__transaction_cost * self.__leverage)
            investment = self.__cash * self.__investment_rate
            self.__enter_price = self.__close_test[t]
            self.__cash = self.__cash - investment
            self.__share = investment / self.__close_test[t]* (1 - self.__transaction_cost * self.__leverage)
        self.__wealth = self.__cash + self.__share * self.__close_test[t]
        self.__accumulate_return = (self.__wealth - self.__initial_wealth) / self.__initial_wealth * 100
    
    def get_instant_pips(self, t, action):
        self.__accumulate_pips +=  ACTION_LIST[action] * (self.__ret_train[t+1]) - \
        self.__transaction_cost * abs(ACTION_LIST[self.__previous_action] - ACTION_LIST[action])

    def act(self, t, action):
        self.get_instant_reward(t, action)
        self.get_instant_pips(t, action)
        #reward = self.get_instant_pips(t,action)
        self.__previous_action = action
        return self.__accumulate_return, self.__accumulate_pips

def run():
    
    version = "6"
    serial_No = "5"
    look_back_term = 300
    train_start_period = 700
    train_stop_period = 1100
    transaction_cost = 0.00025 # for side trade
    
    
    time_start = "2016-05-30-08-34-44"
    with open("../Temp/DRL_model_v" + version + "_" + time_start + ".json", "r") as jfile:
        model = model_from_json(json.load(jfile))
    model.load_weights("../Temp/DRL_model_v" + version + "_" + time_start + ".h5")
    
    #===========================================================================
    # with open("../Archive_Result/v" + version + "/DRL_model_v" + version + "_" + serial_No + ".json", "r") as jfile:
    #     model = model_from_json(json.load(jfile))
    # model.load_weights("../Archive_Result/v" + version + "/DRL_model_v" + version + "_" + serial_No + ".h5")
    #===========================================================================
    
    
    model.compile("sgd", "mse")
    
    # import return data
    data = pd.read_csv("../Data/GBPUSD240.csv",header=None)
    close = data[5].values

    
    ret_test = (close[1:] - close[:-1])[train_start_period:train_stop_period]
    close_test = close[train_start_period+1:train_stop_period]

    env = FX_Market(ret_train = ret_test, look_back_term = look_back_term, transaction_cost = transaction_cost,close_test = close_test)

    accumulate_ret = [0.0]
    accumulate_pips = [0.0]
    action_list = []
    q_value_list = []
    win = 0.0
    loss = 0.0
    for t in range(look_back_term - 1 , len(ret_test) - 2) :
        state = env.get_state(t)
        # decide action
        q = model.predict(state)

        print q[0]
        action = np.argmax(q[0])  # if max(q[0]) > 0 else 1
        action_list.append(ACTION_LIST[action])
        q_value_list.append(q[0])

        if ret_test[t+1] * np.argmax(q[0]) > 0 :
            win += 1
        elif ret_test[t+1] * np.argmax(q[0]) < 0 :
            loss += 1

        wealth, pips = env.act(t, action)
        accumulate_ret.append(wealth)
        accumulate_pips.append(pips)
        print "accumulate return : " + str(accumulate_ret[-1])
    q_value_list = np.transpose(np.asarray(q_value_list))
    # print q_value_list[0]
    print win
    print loss
    print win / (win + loss)
    print accumulate_pips[-1]
    
    # plot result
    fig = plt.figure(1)
    ax1 = fig.add_subplot(411)
    ax1.plot(range(len(accumulate_ret)),accumulate_ret,"r-",label = "Return")
    plt.ylabel("Return (%)")
    ax1.legend()
    plt2 = ax1.twinx()
    #plt2.plot(range(len(action_list)),action_list,"b")

    if train_stop_period < 0 :
        plt2.plot(range(len(accumulate_ret)), close[train_start_period+look_back_term+1:train_stop_period],"b-", label = "GBPUSD exchange rate")
    else :
        plt2.plot(range(len(accumulate_ret)), close[train_start_period+look_back_term+1:train_stop_period+1],"b-", label = "GBPUSD exchange rate")
    plt.ylabel("GBPUSD exchange rate")
    #plt2.legend()
    
    ax2 = fig.add_subplot(412)
    ax2.plot(range(len(accumulate_ret)),accumulate_pips,"r-",label = "Pips")
    plt.ylabel("Pips")
    ax2.legend()
    plt2 = ax2.twinx()
    if train_stop_period < 0 :
        plt2.plot(range(len(accumulate_ret)), close[train_start_period+look_back_term+1:train_stop_period],"b-", label = "GBPUSD exchange rate")
    else :
        plt2.plot(range(len(accumulate_ret)), close[train_start_period+look_back_term+1:train_stop_period+1],"b-", label = "GBPUSD exchange rate")
    plt.ylabel("GBPUSD exchange rate")
    #plt2.legend()
    
    ax3 = fig.add_subplot(413)
    ax3.plot(range(len(action_list)),action_list,"r.",label = "Action")
    plt.ylabel("Action 0 = no entry, 1 = buy, -1 = sell")
    plt.ylim(-1.2,1.2)
    ax3.legend()
    plt2 = ax3.twinx()
    if train_stop_period < 0 :
        plt2.plot(range(len(accumulate_ret)), close[train_start_period+look_back_term+1:train_stop_period],"b-", label = "GBPUSD exchange rate")
    else :
        plt2.plot(range(len(accumulate_ret)), close[train_start_period+look_back_term+1:train_stop_period+1],"b-", label = "GBPUSD exchange rate")
    
    ax3 = fig.add_subplot(414)
    ax3.plot(range(len(q_value_list[0])), q_value_list[0],"r",label = "Q value of buy")
    ax3.plot(range(len(q_value_list[0])), q_value_list[1],"g",label = "Q value of hold")
    ax3.plot(range(len(q_value_list[0])), q_value_list[2],"b",label = "Q value of sell")
    ax3.legend()
    plt.show()


if __name__ == '__main__': run()
