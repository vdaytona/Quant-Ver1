'''
Deep learning reinfocement based trading
Test for the trained model

v2 : batch predict
@author: Daytona
'''


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import json
from keras.models import model_from_json

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
    serial_No = "6"
    look_back_term = 300
    train_start_period = 0
    train_stop_period = -1
    transaction_cost = 0.0005 # for side trade
    
    
    time_start = "2016-05-30-15-15-12"
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
    win = 0.0
    loss = 0.0
    state_batch = np.zeros((len(ret_test) - 2 -look_back_term +1 , look_back_term))
    
    for t in range(look_back_term - 1 , len(ret_test) - 2) :
        state_batch[t-(look_back_term-1) : t-look_back_term+2] = env.get_state(t)
    Q_predict = model.predict(state_batch,batch_size = len(state_batch))
    action_batch = Q_predict.argmax(axis = 1)
        
    for t in range(look_back_term - 1 , len(ret_test) - 2) :
        i = t-(look_back_term-1)
        if ret_test[t+1] * ACTION_LIST[action_batch[i]] > 0 :
            win += 1
        elif ret_test[t+1] *ACTION_LIST[action_batch[i]] < 0 :
            loss += 1
        wealth, pips = env.act(t, action_batch[i])
        accumulate_ret.append(wealth)
        accumulate_pips.append(pips)
        #print "accumulate return : " + str(accumulate_ret[-1])
        action_list.append(ACTION_LIST[action_batch[i]])
    q_value_list = np.transpose(np.asarray(Q_predict))
    
    print "win trade count :" + str(int(win))
    print "loss trade count :" + str(int(loss))
    print "win ratio :" + str(win / (win + loss))
    print "accumulate pips :" + str(accumulate_pips[-1])
    print "accumulate return :" + str(accumulate_ret[-1])
    
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
