'''

This module is for prediction result evaluation

Created on 2015/07/13

@author: Daytona
'''

import numpy as np
import scipy as sp

class evaluation():
    def __init__(self, y_real, y_pred):
        """
        input_data
        example
        {[date,real,pred], [2011-1-1,80,81], [2011-1-2,81,83]}
        """
        self.real = y_real
        self.pred = y_pred
        pass
    
    # TODO @JP
    def NMSE(self):
        """
        normalized mean square error
        Args:
            self.date
            self.real
            self.pred
        
        Return:
            NMSE type: double
        """
        n = len(self.real)
        sigma_square = 0.0
        nmse = 0.0
        real_mean = np.mean(self.real)
        for i in range(n):
            sigma_square += (self.real[i] - real_mean)**2
            nmse += (self.real[i] - self.pred[i])**2
        sigma_square = sigma_square / (n-1) 
        nmse = nmse / (n * sigma_square)
        return nmse
    
    # TODO @JP
    def MAE(self):
        """
        mean average error
        """
        pass
    
    # TODO @JP
    def DS(self):
        """
        directional symmetry
        to check whether the direction is right
        """
        n = len(self.real)
        ds = 0
        for i in range(n):
            if self.real[i] * self.pred[i] > 0 : ds += 1
        return ds
    
    # TODO @JP
    def WDS(self):
        """
        weighted directional symmetry
        """
        pass
    