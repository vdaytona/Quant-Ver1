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
        self.__wealth = 10000.0
        self.__investment = 1000.0
        self.__investment_rate = 0.1
        self.__leverage = 25

    def reset(self):
        self.__previous_action = 1

    def get_state(self,t):
        state = np.zeros((1,self.__look_back_term))
        state[0] = self.__ret_train[t - self.__look_back_term +  1 : t + 1]
        return state

    def get_instant_reward(self, t , action):
        print (self.__close_test[t+1] - self.__close_test[t]) / self.__close_test[t]
        self.__investment = self.__wealth * self.__investment_rate
        return self.__investment * ( 1.0 + self.__leverage * (self.__close_test[t+1] - self.__close_test[t]) / self.__close_test[t] * ACTION_LIST[action]) - \
            self.__investment * (self.__transaction_cost) / self.__close_test[t] * abs(ACTION_LIST[self.__previous_action] - ACTION_LIST[action])
        # return ACTION_LIST[action] * self.__ret_train[t+1] + \
        #    self.__transaction_cost * abs(ACTION_LIST[self.__previous_action] - ACTION_LIST[action])

    def act(self, t, action):
        state_new = self.get_state(t + 1)
        self.__wealth = self.__wealth - self.__investment
        reward = self.get_instant_reward(t,action)
        self.__wealth += reward
        self.__previous_action = action
        return state_new, self.__wealth

def run():
    time_start = "2016-05-26-10-02-15"
    version = str(6)

    with open("../Model/DRL_model_v" + version + "_" + time_start + ".json", "r") as jfile:
        model = model_from_json(json.load(jfile))
    model.load_weights("../Model/DRL_model_v" + version + "_" + time_start + ".h5")
    model.compile("sgd", "mse")
    look_back_term =   200
    transaction_cost = 0.0005

    # import return data
    data = pd.read_csv("../Data/GBPUSD240.csv",header=None)
    close = data[5].values

    train_start_period = 0
    train_stop_period = 30000
    ret_test = (close[1:] - close[:-1])[train_start_period:train_stop_period]
    close_test = close[train_start_period+1:train_stop_period]

    env = FX_Market(ret_train = ret_test, look_back_term = look_back_term, transaction_cost = transaction_cost,close_test = close_test)

    accumulate_ret = [10000.0]
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

        new_state, reward = env.act(t, action)
        accumulate_ret.append(reward)
        print "accumulate return : " + str(accumulate_ret[-1])
    q_value_list = np.transpose(np.asarray(q_value_list))
    print win
    print loss
    print win / (win + loss)
    print q_value_list[0]
    plt.plot(range(len(accumulate_ret)),accumulate_ret,"r.")
    plt2 = plt.twinx()
    #plt2.plot(range(len(action_list)),action_list,"b")
    print len(accumulate_ret)
    print len(close[train_start_period+look_back_term+1:train_stop_period])


    if train_stop_period < 0 :
        plt2.plot(range(len(accumulate_ret)), close[train_start_period+look_back_term+1:train_stop_period], "b-")
    else :
        plt2.plot(range(len(accumulate_ret)), close[train_start_period+look_back_term+1:train_stop_period+1], "b-")


    plt.show()

    plt.plot(range(len(q_value_list[0])), q_value_list[0],"r")
    plt.plot(range(len(q_value_list[0])), q_value_list[1],"g")
    plt.plot(range(len(q_value_list[0])), q_value_list[2],"b")
    plt.legend()
    plt.show()


if __name__ == '__main__': run()
