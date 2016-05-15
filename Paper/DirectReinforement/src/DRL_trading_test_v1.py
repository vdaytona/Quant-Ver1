'''
Created on 15 May 2016

@author: Daytona
'''

import numpy as np

class test():
    def __init__(self,mode, ret_test, look_back_term):
        self.__ret_test = ret_test
        self.__mode = mode
        self.__look_back_term = look_back_term
        
    def test(self):
        pass
    
    def get_batch(self):
        accumulate_return = []
        previous_action = 1
        batch_size = len(self.__ret_test) - self.__look_back_term
        inputs = np.zeros(batch_size, self.__look_back_term)
        for t in range(self.__look_back_term - 1 , batch_size - 2) :
            pass

if __name__ == '__main__':
    pass