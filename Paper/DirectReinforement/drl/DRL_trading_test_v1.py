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
    def __init__(self,ret_train, look_back_term, transaction_cost):
        self.__ret_train = ret_train
        self.__look_back_term = look_back_term
        self.__previous_action = 1
        self.__transaction_cost = transaction_cost

    def reset(self):
        self.__previous_action = 1

    def get_state(self,t):
        state = np.zeros((1,100))
        state[0] = self.__ret_train[t - self.__look_back_term +  1 : t + 1]
        return state

    def get_instant_reward(self, t , action):
        return ACTION_LIST[action] * self.__ret_train[t+1] + \
            self.__transaction_cost * abs(ACTION_LIST[self.__previous_action] - ACTION_LIST[action])

    def act(self, t, action):
        state_new = self.get_state(t + 1)
        reward = self.get_instant_reward(t, action)
        self.__previous_action = action
        return state_new, reward

def run():
    
    with open("../Archive_Result/DRL_v5_model_1.json", "r") as jfile:
        model = model_from_json(json.load(jfile))
    model.load_weights("../Archive_Result/DRL_v5_model_1.h5")
    model.compile("sgd", "mse")
    look_back_term = 100
    transaction_cost = 0.00005
    
    # import return data
    data = pd.read_csv("../Data/GBPUSD240.csv",header=None)
    close = data[5].values
    ret_test = (close[1:] - close[:-1])[4900:]
    env = FX_Market(ret_train = ret_test, look_back_term = look_back_term, transaction_cost = transaction_cost)

    accumulate_ret = [0.0]
    action_list = []
    win = 0.0
    loss = 0.0
    for t in range(look_back_term - 1 , len(ret_test) - 2) :
        state = env.get_state(t)
        # decide action
        q = model.predict(state)
        action_list.append(np.argmax(q[0]))
        print q[0]
        action = np.argmax(q[0])
        
        if ret_test[t+1] * np.argmax(q[0]) > 0 :
            win += 1
        elif ret_test[t+1] * np.argmax(q[0]) < 0 :
            loss += 1
        
        new_state, reward = env.act(t, action)
        accumulate_ret.append(accumulate_ret[-1]  + reward)
        print "accumulate return : " + str(accumulate_ret[-1])
    
    print win
    print loss
    print win / (win + loss)
    
    
    plt.plot(range(len(accumulate_ret)),accumulate_ret,"r.")
    plt2 = plt.twinx()
    #plt2.plot(range(len(action_list)),action_list,"b")
    print len(accumulate_ret)
    print len(close[5000:-1])
    plt2.plot(range(len(accumulate_ret)), close[5000:-1], "b")
    plt.show()
    
    

if __name__ == '__main__': run()
