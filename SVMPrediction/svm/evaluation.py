'''

This module is for prediction result evaluation

Created on 2015/07/13

@author: Daytona
'''

class evaluation():
    def __init__(self, input_data):
        """
        input_data
        example
        {[date,real,pred], [2011-1-1,80,81], [2011-1-2,81,83]}
        """
        self.date = input_data['date']
        self.real = input_data['real']
        self.pred = input_data['pred']
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
        pass
    
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
        """
        pass
    
    # TODO @JP
    def WDS(self):
        """
        weighted directional symmetry
        """
        pass
    