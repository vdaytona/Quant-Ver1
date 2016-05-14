'''
Deep learning reinfocement based trading
State: return_t, return_t-1. return_t-2....,return_t-m
instant reward : Ft * return_t+1
Q-value : instant reward + max(Q(a|s+1))
Created on 14 May 2016

@author: Daytona
'''


import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd
import matplotlib.pyplot as plt

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
        state[0] = self.__ret_train[t - self.__look_back_term + 1 : t+1]
        return state
    
    def get_instant_reward(self, t , action):
        return ACTION_LIST[action] * self.__ret_train[t+1] - \
            self.__transaction_cost * abs(ACTION_LIST[self.__previous_action] - ACTION_LIST[action])
    
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
    epoch = 500
    max_memory = 5000
    hidden_size = 300
    batch_size = 50
    look_back_term = 100
    
    
    # import return data
    data = pd.read_csv("../Data/GBPUSD30.csv",header=None)
    close = data[5].values
    ret = (close[1:] - close[:-1])[:1000]
    train_percent = 0.8
    ret_train = ret[:len(ret) * train_percent]
    ret_test = ret[len(ret) :]
    
    model = Sequential()
    model.add(Dense(hidden_size, input_shape=(look_back_term,), activation='relu'))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(num_actions))
    
    model.compile(sgd(lr=.2), "mse")
    
    env = FX_Market(ret_train = ret_train, look_back_term = look_back_term, transaction_cost = transcation_cost)
    
    trading_his = Trading_Memory(max_memory = max_memory)
    
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
        return_list.append(accumulate_ret[-1])
    
    plt.plot(range(len(return_list)),return_list)
    plt.show()
    
    
if __name__ == '__main__': run()