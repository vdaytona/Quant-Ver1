'''
Deep learning reinfocement based trading
State: return_t, return_t-1. return_t-2....,return_t-m
instant reward : Ft * return_t+1
Q-value : instant reward + max(Q(a|s+1))

Using two layers CNN

training first 160 days, and test with 40 days
Created on 14 May 2016

@author: Daytona
'''

import json
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers.core import Dense
from keras.layers.convolutional import Convolution1D 
from keras.layers import Embedding
from keras.optimizers import sgd
import matplotlib.pyplot as plt
import logging
import datetime
from time import gmtime, strftime

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
        state = np.zeros((1,self.__look_back_term))
        state[0] = self.__ret_train[t - self.__look_back_term + 1 : t+1]
        return state

    def get_instant_reward(self, t , action):
        return (ACTION_LIST[action] * self.__ret_train[t+1] - \
            self.__transaction_cost * abs(ACTION_LIST[self.__previous_action] - ACTION_LIST[action]) )

    def act(self, t, action):
        state_new = self.get_state(t + 1)
        reward = self.get_instant_reward(t, action)
        self.__previous_action = action
        return state_new, reward


class Trading_Memory():
    def __init__(self,max_memory, discount = 0.9):
        self.__max_memory = max_memory
        self.__memory = list()
        self.discount = discount

    def memory(self,state, state_new, action, reward):
        self.__memory.append([state, state_new, action, reward])
        if len(self.__memory) > self.__max_memory:
            del self.__memory[0]

    def get_batch(self, model, batch_size=30):
        len_memory = len(self.__memory)

        num_actions = model.output_shape[-1]

        env_dim = self.__memory[0][0].shape[1]

        inputs = np.zeros((min(len_memory, batch_size), env_dim))
        targets = np.zeros((inputs.shape[0], num_actions))

        for i, idx in enumerate(np.random.randint(0, len_memory,size=inputs.shape[0])):
            state, state_new, action, reward = self.__memory[idx]
            inputs[i:i+1] = state
            targets[i] = model.predict(state)[0]
            Q_sa = np.max(model.predict(state_new)[0])
            targets[i, action] = reward + self.discount * Q_sa
        return inputs, targets

def run():
    global ACTION_LIST
    
    # parameters
    epsilon = .1  # exploration
    num_actions = len(ACTION_LIST)  # [buy, hold, sell]
    transcation_cost = 0.0005
    epoch = 200
    max_memory = 1000
    batch_size = max_memory
    look_back_term = 100
    hidden_size = look_back_term
    act_function = "relu"
    learning_rate = .2
    
    # import return data
    data = pd.read_csv("../Data/GBPUSD30.csv",header=None)
    close = data[5].values
    ret = (close[1:] - close[:-1])[:1000]
    train_percent = 1
    ret_train = ret[:len(ret) * train_percent]

    
    #model.add(Dense(hidden_size, input_shape=(look_back_term,), activation=act_function))
    #model.add(Dense(hidden_size, activation=act_function))
    #model.add(Dense(hidden_size, activation=act_function))
    #model.add(Dense(num_actions))
    #model.compile(sgd(lr=learning_rate), "mse")
    
    model = Sequential()
    #model.add(Embedding(look_back_term, embedding_dims, input_length=maxlen, dropout=0.2))
    model.add(Convolution1D(hidden_size, 2, input_shape=(look_back_term,),activation=act_function))
    model.add(Dense(num_actions))
    model.compile(sgd(lr=learning_rate), "mse")
    

    env = FX_Market(ret_train = ret_train, look_back_term = look_back_term, transaction_cost = transcation_cost)

    trading_his = Trading_Memory(max_memory = max_memory)
    
    logging.basicConfig(filename='DRL_Trading_Learning_v2.log',level=logging.INFO)
    logging.info("Start time : " + strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    logging.info("Parameter setting :")
    logging.info("epsilon = " + str(epsilon))
    logging.info("transaction_cost = " + str(transcation_cost))
    logging.info("epoch ="  + str(epoch))
    logging.info("max_memory = " + str(max_memory))
    logging.info("batch_size = " + str(batch_size))
    logging.info("look back term = " + str(look_back_term))
    logging.info("hidden_size = " + str(hidden_size))
    logging.info("activation function = " + act_function)
    logging.info("learning rate" + str(learning_rate))

    # Train
    return_list = []
    for e in range(epoch):
        print "epoch : " + str(e)
        env.reset()
        accumulate_ret = [0.0]
        for t in range(look_back_term - 1 , len(ret_train) - 2) :
            state = env.get_state(t)
            # decide action
            if np.random.rand() < epsilon:
                action = np.random.randint(0, num_actions, size=1)
            else:
                q = model.predict(state)
                action = np.argmax(q[0])

            new_state, reward = env.act(t, action)

            accumulate_ret.append(accumulate_ret[-1] + reward)

            trading_his.memory(state, new_state, action, reward)

            inputs, targets = trading_his.get_batch(model, batch_size=batch_size)

            model.train_on_batch(inputs, targets)

        print "accumulate return : " + str(accumulate_ret[-1])
        logging.info("accumulate return : " + str(accumulate_ret[-1]))
        return_list.append(accumulate_ret[-1])
        
#===============================================================================
#     result = pd.DataFrame()
#     result["accumulate return"] = return_list
#     result.to_csv("./DRL_result_1_14052016.csv")
# 
#     model.save_weights("./model2.h5", overwrite=True)
#     with open("model2.json", "w") as outfile:
#         json.dump(model.to_json(), outfile)
#===============================================================================

    plt.plot(range(len(return_list)),return_list,"r.")
    plt.show()
    #test(model, ret_test)


if __name__ == '__main__': run()
