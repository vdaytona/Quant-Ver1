'''
Deep learning reinfocement based trading
State: return_t, return_t-1. return_t-2....,return_t-m
instant reward : Ft * return_t 1
Q-value : instant reward   max(Q(a|s 1))
Created on 14 May 2016
Using two layers CNN

v4 : use random memory to train to avoid correlation of the data
v5 : discount rate - > 0.000009 (four rate, compound annual interest rate is 2%)
* discount rate need to be discussed
v6 : 1. two model : online network and target network, online use to calculate action, 
and target network used to calculate the value of greedy policy, detailed in "Double DQN"
change memory.get_batch
     2. set skip frame, to increase training speed - > only used in DRL_model_v6_3 
v7: 1. Modify the Traning_memory.get_batch(), extremely reduced processing time
    2. Data has fixed. (4 hour data only begin from 1999)
@author: Daytona
import os
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
'''


#import os
#os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

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
from keras.models import model_from_json
import json
import copy
import theano
#from numba.types import float32
from theano import config
import pickle
import time

ACTION_LIST = [1,0,-1]
#floatX = float32
time_get_batch = list(np.zeros(7))

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
        state[0] = self.__ret_train[t - self.__look_back_term +  1 : t + 1]
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
        
    def get_memory(self):
        return self.__memory
    
    def memory(self,state, state_new, action, reward):
        self.__memory.append([state, state_new, action, reward])
        if len(self.__memory) > self.__max_memory:
            del self.__memory[0]
            

    def get_batch(self, target_model,online_model, batch_size=30):
        # use target_model to decide greedy policy (action), 
        # and target_model to calculate the value
        
        len_memory = len(self.__memory)
        env_dim = self.__memory[0][0].shape[1]
        state_batch = np.zeros((min(len_memory, batch_size), env_dim))
        
        new_state_batch = np.zeros((min(len_memory, batch_size), env_dim))
        reward_batch = np.zeros(state_batch.shape[0])
        action_batch = np.zeros(state_batch.shape[0])        
        
        for i, idx in enumerate(np.random.randint(0, len_memory,size=state_batch.shape[0])):
            state, state_new, action, reward = self.__memory[idx]
            state_batch[i:i+1] = state
            new_state_batch[i:i+1] = state_new
            reward_batch[i:i+1] = reward
            action_batch[i:i+1] = action
        
        joined_batch = np.concatenate((state_batch, new_state_batch))        
        joined_predict_batch = target_model.predict(joined_batch,batch_size = len(state_batch) * 2)
        targets_predict_batch = joined_predict_batch[: len(joined_predict_batch) / 2]
               
        Q_predict = online_model.predict(new_state_batch,batch_size = len(new_state_batch))
        action_next_bath = Q_predict.argmax(axis = 1)
        Q_max = joined_predict_batch[len(joined_predict_batch) / 2 : ][np.array(range(len(new_state_batch))), action_next_bath]
        
        for i in range(len(targets_predict_batch)) :
            targets_predict_batch[i, action_batch[i]] = reward_batch[i] + self.discount * Q_max[i]
            
        return state_batch, targets_predict_batch

def write_model(online_model, version, time_start):
    #output model
    online_model.save_weights("../Temp/DRL_model_v" + version + "_" + time_start + ".h5", overwrite=True)
    with open("../Temp/DRL_model_v" + version + "_" + time_start + ".json", "w") as outfile:
        json.dump(online_model.to_json(), outfile)
    outfile.close()

def read_model(version, time_start):
    with open("../Temp/DRL_model_v" + version + "_" + time_start + ".json", "r") as jfile:
        target_model = model_from_json(json.load(jfile))
    target_model.load_weights("../Temp/DRL_model_v" + version + "_" + time_start + ".h5")
    target_model.compile("sgd", "mse")
    jfile.close()
    return target_model

def save_variable(fileName, variable):
    f = file("../Temp/" + fileName, 'wb')
    pickle.dump(variable, f)
    f.close

def load_variable(fileName, variable):
    f = file("../Temp/" + fileName, 'rb')
    return pickle.load(f)
    

def run():
    global ACTION_LIST
    global floatX
    global time_get_batch
    # parameters
    version = str(7)
    epsilon = 0.1  # exploration
    num_actions = len(ACTION_LIST)  # [buy, hold, sell]
    transcation_cost = 0.0005
    epoch = 1000
    max_memory = 1000000
    hidden_size = 600
    batch_size = 200
    look_back_term = 300
    training_period_start = 50
    training_period_stop = 10050
    learning_rate = 0.1
    discount_rate = 0.000009
    step_size = 10 # iterate step to update target_model
    act_function = "relu"
    #frame_skip = 4 # train the model with some frames intervals
    input_data = "GBPUSD240.csv"

    # log
    time_start_epoch = datetime.datetime.now()
    time_start = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    log_name = '../log/DRL_Learning_v' + version + '_' + time_start + '.log'
    logging.basicConfig(filename=log_name,level=logging.DEBUG)
    logging.info("Version : " + version)
    logging.info("Time start : " + str(time_start))
    logging.info("Input data :" + input_data)
    logging.info("Parameter setting :")
    logging.info("epsilon = " + str(epsilon))
    logging.info("transaction_cost = " + str(transcation_cost))
    logging.info("epoch ="  + str(epoch))
    logging.info("max_memory = " + str(max_memory))
    logging.info("batch_size = " + str(batch_size))
    logging.info("look back term = " + str(look_back_term))
    logging.info("hidden_size = " + str(hidden_size))
    logging.info("training period = " + str(training_period_start) + " ~ " + str(training_period_stop))
    logging.info("learning rate = " + str(learning_rate))
    logging.info("discount rate = " + str(discount_rate))
    logging.info("step_size = " + str(step_size))
    logging.info("activation function = " + act_function)
    #logging.info("frame_skip" + str(frame_skip))
    print "log start"

    # import return data
    data = pd.read_csv("../Data/" + input_data,header=None)
    close = data[5].values
    ret_train = (close[1:] - close[:-1])[training_period_start : training_period_stop]
    
    #build model : online mode and target model
    model = Sequential()
    model.add(Dense(hidden_size, input_shape=(look_back_term,), activation=act_function))
    model.add(Dense(hidden_size, activation=act_function))
    model.add(Dense(hidden_size, activation=act_function))
    model.add(Dense(num_actions))
    model.compile(sgd(lr=learning_rate), "mse")
    
    write_model(model, version, time_start)
    target_model = read_model(version, time_start)
    
    # create market
    env = FX_Market(ret_train = ret_train, look_back_term = look_back_term, transaction_cost = transcation_cost)
    # create memory
    trading_his = Trading_Memory(max_memory = max_memory, discount=discount_rate)
    
    # Train
    return_list = []
    
    for e in range(epoch):
        print "epoch : " + str(e)
        env.reset()
        accumulate_ret = [0.0] # pips earn from fx market
        if e % step_size == 0:
            write_model(model, version, time_start)
            target_model = read_model(version, time_start)
            
        #time_cal = list(np.zeros(6))
        time_get_batch = list(np.zeros(7))
        
        for t in range(look_back_term - 1 , len(ret_train) - 2) :
            #if np.random.random_integers(1,frame_skip) == 4 :
            state = env.get_state(t)
            # decide action
            if np.random.rand() < epsilon:
                action = np.random.randint(0, num_actions, size=1)
            else:
                q = target_model.predict(state)
                action = np.argmax(q[0])
            
            new_state, reward = env.act(t, action)

            accumulate_ret.append(accumulate_ret[-1]  + reward)

            trading_his.memory(state, new_state, action, reward)
            
            #save_variable("memory_" + time_start, trading_his.get_memory())
            
            inputs, targets = trading_his.get_batch(target_model, model,batch_size=batch_size)

            model.train_on_batch(inputs, targets)
        
        #for i in range(len(time_cal)) :
        #    print "process " + str(i) + " : " + str(time_cal[i]/60) + " minutes"
        
        print "accumulate return : " + str(accumulate_ret[-1])
        
        return_list.append(accumulate_ret[-1])
        logging.info("accumulate return : " + str(accumulate_ret[-1]))
        loop_time = datetime.datetime.now() - time_start_epoch
        time_left = float(loop_time.seconds) / 3600.0 / float(e+1) * float(epoch - e + 1)
        print "left time : " + str(time_left) + " hours"
    
    time_used = datetime.datetime.now() - time_start_epoch
    time_used = float(time_used.seconds) / 3600.0
    logging.info("Processing time : " + str(time_used) + " hours")
    
    save_variable("../Temp/memory_" + time_start + ".mem", trading_his.get_memory())
    
    #output accumulate data
    result = pd.DataFrame()
    result["accumulate return"] = return_list
    result.to_csv("../Result_Data/DRL_v" + version + "_result_" + time_start + ".csv")
    
    #output model
    model.save_weights("../Model/DRL_model_v" + version + "_" + time_start + ".h5", overwrite=True)
    with open("../Model/DRL_model_v" + version + "_" + time_start + ".json", "w") as outfile:
        json.dump(model.to_json(), outfile)
    outfile.close()

    #plt.plot(range(len(return_list)),return_list,"r.")
    #plt.show()
    #test(model, ret_test)

    
    print "finished"

if __name__ == '__main__': run()

