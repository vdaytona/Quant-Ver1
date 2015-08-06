'''
Created on 6 Aug 2015

@author: purewin7
'''

import pandas as pd

class balance():
    '''
    Container for historical trading data
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        self.baclance_record = pd.DataFrame(columns='Date','Open_Time','Type','Size','Item',
                                            'Open_Price','Stop_Limit','Take_Profit','Close_Time',
                                            'Close_Price','Commission','Taxes','Swap','Pips','Profit')
    
    def buy(self, pair, **argw):
        pass
    
    def sell(self,pair, **argw):
        pass
    
    def stopLimit(self, pair, **argw):
        pass
    
    def takeProfit(self, pair, **argw):
        pass
    
    def close(self, pair, **argw):
        pass
    
    def exportBalance(self):
        pass