'''
#Test of Direct Reinforcement Trading based on paper
"Learning to Trade via Direct Reinforcement"

Utility function use as wealth directly
return = prize(t) - prize(t-1)
input only return of commodity of each time
target value : the return of perfect execution decision

Main flow :
1. Add target value to the training set, leave the decision F blank, which will be filled when doing online learning
2. Learning process
    2.1 Bulid one layer RNN and a output layer calculate by the Rt(Ft, Ft-1), reference "Deep direct reinforcement learning for financial signal representatoin and trading"
    2.2 Learning the parameter
        2.2.1 feed the first time series data
        2.2.2 fill the Ft in the training data set
        2.2.3 feed the next time series data
        2.2.4 terminate until no data
3. Training data is used as first 2000 days, then update the parameters using step 3 after each 100 days.
4. Used the parameters in trained model to make decision 

Created on 19 Apr 2016

@author: purewin7
'''

import pandas as pd
import math
import numpy as np
from __builtin__ import str

class agent():
    def __init__(self, initial_wealth):
        pass
        
        

if __name__ == "__main__": run()
